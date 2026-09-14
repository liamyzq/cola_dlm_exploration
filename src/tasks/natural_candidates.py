"""Reward-blind native candidate feasibility on natural passage prefixes."""
import argparse
import json
import os
from pathlib import Path
import time
import torch
from src.models.cola_state import ColaStateEngine
from src.methods.same_prefix import native_candidates

EOS_IDS={100257,100265}


@torch.inference_mode()
def make_root(engine,item,cohort,seed):
    prompt_tokens=len(engine.tokenizer.encode(item['prompt']).ids)
    if cohort=='M' and prompt_tokens%16==0:
        return None,'aligned_prompt_no_mixed'
    engine.begin(item['prompt'])
    noises=engine.noise(seed,2 if cohort=='F' and engine.trim else 1)
    earlier=[]
    if cohort=='F' and engine.trim:
        z,_,_=engine.advance(noises[0]);earlier.append(z.clone())
        if EOS_IDS.intersection(engine.generated_ids):return None,'terminated_before_full_block'
    pre=engine.snapshot()
    z,ids,logits=engine.advance(noises[-1]);reference=engine.snapshot()
    if EOS_IDS.intersection(reference.generated_ids):return None,'terminated_at_anchor'
    return dict(pre=pre,latent=z,noise=noises[-1],noises=noises,
                earlier=earlier,reference=reference),'live'


def save_pair(path,item,root,candidates):
    # Save the minimum exact states needed to reconstruct the consistent caches.
    # The known prompt representation is re-encoded by the pinned model; no
    # future text enters encoding. Earlier generated blocks are saved directly.
    payload=dict(prompt=item['prompt'],source_id=item['source_id'],root_id=item['root_id'],
                 pre_generated_latents=[x.cpu() for x in root['earlier']],
                 candidate_latents=torch.stack([x.latent.cpu() for x in candidates]),
                 reference_generated_ids=root['reference'].generated_ids,
                 prompt_ids=root['reference'].prompt_ids,
                 original_noises=root['noises'].cpu())
    torch.save(payload,path)


@torch.inference_mode()
def restore_pair(engine,payload,index):
    engine.begin(payload["prompt"])
    assert engine.prompt_ids==tuple(payload["prompt_ids"])
    for latent in payload["pre_generated_latents"]:
        engine.commit(latent.to(engine.device))
    engine.commit(payload["candidate_latents"][index].to(engine.device))
    assert engine.generated_ids==tuple(payload["reference_generated_ids"])
    return engine.snapshot()


def run(a):
    cfg=json.loads(Path(a.config).read_text())
    if 'pair_target' in cfg:assert a.shards==1, 'Use one ordered worker for the global pair cap'
    out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    items=[json.loads(x) for x in Path(cfg['data']).read_text().splitlines()]
    engine=ColaStateEngine(os.environ['COLA_CHECKPOINT'],steps=cfg['euler_steps'],cfg=cfg['cfg'],repetition_penalty=cfg['repetition_penalty'])
    paired_roots=0
    with (out/'roots.jsonl').open('w') as f:
        for index in cfg['root_indices']:
            if 'pair_target' in cfg and paired_roots>=cfg['pair_target']:break
            if index%a.shards!=a.shard:continue
            item=items[index]
            assert item['root_id']==index and item['split']=='development'
            torch.cuda.synchronize();start=time.perf_counter();before=engine.calls.copy()
            seed=cfg['reference_noise_seed']+index*10000
            root,reason=make_root(engine,item,cfg['cohort'],seed)
            torch.cuda.synchronize();root_seconds=time.perf_counter()-start
            record=dict(root_id=index,source_id=item['source_id'],cohort=cfg['cohort'],
                root_status=reason,reference_noise_seed=seed,prompt_tokens=item['prompt_tokens'],
                root_seconds=root_seconds,root_calls={k:engine.calls[k]-before[k] for k in before},arms=[])
            if root is not None:
                record.update(prefix_ids=root['reference'].generated_ids,
                    prefix_text=engine.text(root['reference'].generated_ids),
                    free_positions=16-root['pre'].trim if cfg['cohort']=='M' else 16)
                for eta_index,eta in enumerate(cfg['etas']):
                    torch.cuda.synchronize();start=time.perf_counter();before=engine.calls.copy()
                    proposal_seed=cfg['proposal_noise_seed']+index*10000+eta_index*100
                    candidates,proposals=native_candidates(engine,root['pre'],root['latent'],root['noise'],
                        eta,cfg['epsilon'],proposal_seed,count=cfg['candidate_count'],max_proposals=cfg['max_proposals'])
                    torch.cuda.synchronize();elapsed=time.perf_counter()-start
                    if eta==0:
                        assert len(candidates)==1 and all(x['duplicate'] for x in proposals)
                    arm=dict(eta=eta,proposal_seed=proposal_seed,candidates=len(candidates),
                        proposals=proposals,elapsed_seconds=elapsed,
                        calls={k:engine.calls[k]-before[k] for k in before})
                    if len(candidates)==2:
                        name=f'pair-root-{index}-eta-{eta:g}.pt'
                        save_pair(out/name,item,root,candidates);arm['pair_file']=name
                    record['arms'].append(arm)
            paired_roots+=int(any(x['candidates']==2 for x in record['arms']))
            f.write(json.dumps(record)+'\n');f.flush()
            print(json.dumps(dict(root_id=index,status=reason,
                candidates=[(x['eta'],x['candidates']) for x in record['arms']])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True)
    p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1)
    run(p.parse_args())
