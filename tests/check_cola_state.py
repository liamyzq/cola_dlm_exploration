"""Remote model checks for the state intervention path, not scientific evidence."""
import argparse
import json
import os
from pathlib import Path
from unittest.mock import patch
import torch
import cola_dlm.inference as native
from src.models.cola_state import ColaStateEngine, symmetric_kl
from src.tasks.routes import generate_tasks


def cache_equal(a,b):
    for ca,cb in zip(a,b):
        for xa,xb in zip(ca,cb):
            if xa is None or xb is None:
                assert xa is None and xb is None
            else:
                assert len(xa)==len(xb)
                assert all(torch.equal(x,y) for x,y in zip(xa,xb))


def run(engine, prompt, idx):
    base = 84001+idx*1000
    os.environ['COLA_INFER_PER_SAMPLE_NOISE_SEED']=str(base)
    captured=[]
    original = native.sample_with_strategies
    def capture(*a,**kw):
        result=original(*a,**kw)
        captured.extend(result[0].tolist())
        return result
    with patch.object(native,'sample_with_strategies',capture):
        expected=native.generate_task_repaint_inference(engine.dit,engine.vae,engine.tokenizer,
            [{'id':0,'question':prompt}],max_new_tokens=48,repetition_penalty=1.0)[0]['generate']
    del os.environ['COLA_INFER_PER_SAMPLE_NOISE_SEED']
    engine.begin(prompt)
    noises=[engine.noise(base+s*10000000)[0] for s in range(3)]
    engine.advance(noises[0])
    pre=engine.snapshot()
    z,ids,logits=engine.advance(noises[1])
    committed=engine.snapshot()
    engine.advance(noises[2])
    final_ids=engine.generated_ids
    assert list(final_ids)==captured[len(pre.prompt_ids)%16:], 'native token mismatch'
    assert engine.text()==expected, 'native text mismatch'
    resumed=engine.continue_from(committed,torch.stack(noises[2:]))
    assert resumed==final_ids, 'pause/resume mismatch'
    engine.restore(pre)
    replay_ids,replay_logits=engine.commit(z)
    replay=engine.snapshot()
    assert replay_ids==ids and torch.equal(logits,replay_logits), 'identity mismatch'
    assert symmetric_kl(logits,replay_logits).abs().max().item()==0
    cache_equal(committed.dit_cache,replay.dit_cache)
    cache_equal(committed.decoder_cache,replay.decoder_cache)
    assert engine.continue_from(replay,torch.stack(noises[2:]))==final_ids
    engine.rebuild(committed)
    rebuilt=engine.snapshot()
    cache_equal(committed.dit_cache,rebuilt.dit_cache)
    cache_equal(committed.decoder_cache,rebuilt.decoder_cache)
    assert engine.continue_from(rebuilt,torch.stack(noises[2:]))==final_ids
    proposal_noises=[0.99995*noises[1]+0.01*engine.noise(base+99+k)[0] for k in range(2)]
    outputs={}
    for label in (0,1,1,0):
        engine.restore(pre)
        candidate=engine.sample_block(proposal_noises[label])
        # Sampler reads, but must not mutate, the restored history.
        sampled=engine.snapshot()
        cache_equal(pre.dit_cache,sampled.dit_cache)
        cache_equal(pre.decoder_cache,sampled.decoder_cache)
        cand_ids,cand_logits=engine.commit(candidate)
        assert engine.generated_ids[:len(pre.generated_ids)]==pre.generated_ids
        cand_state=engine.snapshot()
        future=engine.continue_from(cand_state,torch.stack(noises[2:]))
        record=(candidate.clone(),cand_ids,cand_logits.clone(),future)
        if label in outputs:
            old=outputs[label]
            assert torch.equal(old[0],record[0]) and old[1]==record[1]
            assert torch.equal(old[2],record[2]) and old[3]==record[3], 'AB/BA contamination'
        outputs[label]=record
    return dict(example=idx,status='pass',native_tokens=len(final_ids),identity_kl=0,
                checks=['official_parity','pause_resume','identity_replay','cache_rebuild',
                        'proposal_cache_read_only','AB_BA','past_tokens','paired_future_noise'])


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--count',type=int,default=1)
    p.add_argument('--offset',type=int,default=0)
    p.add_argument('--output',required=True)
    args=p.parse_args()
    engine=ColaStateEngine(os.environ['COLA_CHECKPOINT'])
    tasks=generate_tasks(args.count+args.offset,401,'easy')
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w') as f:
        for i in range(args.offset,args.offset+args.count):
            result=run(engine,tasks[i]['prompt'],i)
            print(json.dumps(result),flush=True)
            f.write(json.dumps(result)+'\n');f.flush()
