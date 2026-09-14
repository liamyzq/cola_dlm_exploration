"""Validate first mixed-block interventions; these inputs are engineering only."""
import argparse
import json
import math
import os
from pathlib import Path
from unittest.mock import patch
import torch
from src.models.cola_state import ColaStateEngine
from src.methods.same_prefix import native_candidates,same_computed_history

TEXT = """The museum opened its doors on a quiet morning. Visitors walked through the
courtyard before entering the main gallery. A guide described the photographs,
letters, maps, and tools that local families had donated over many years. Near
the window, a wooden table held a notebook with careful drawings of birds and
plants. Children stopped to compare the drawings with the trees outside. Later
that afternoon, the curator brought another box from the archive and explained
how the collection had grown. Each object had a short label describing where
it came from, who had used it, and why it mattered to the town. The visitors
asked questions and shared memories before returning to the sunny courtyard."""


def prompts_for_remainders(tokenizer):
    words=TEXT.split();result={}
    for n in range(1,len(words)+1):
        prompt=' '.join(words[:n]);size=len(tokenizer.encode(prompt).ids)
        if size>=32:result.setdefault(size%16,prompt)
    assert set(result)==set(range(16))
    return result


def check(engine,prompt,remainder):
    base=88000000+remainder*1000
    pre=engine.begin(prompt)
    assert pre.trim==remainder
    known=pre.first_mask
    noises=engine.noise(base,3)
    z,ids,logits=engine.advance(noises[0]);original=engine.snapshot()
    assert torch.equal(z[known],pre.first_latent[known])
    expected=engine.continue_from(original,noises[1:])
    # Read-only hooks verify clean conditioning on every DiT evaluation during
    # the actual proposal function, and that it does not perturb known noise.
    forward=engine.dit.forward;sample=engine.sample_block;calls=0
    def checked_forward(*args,**kwargs):
        nonlocal calls
        if engine.step==0 and not kwargs.get('update_kv',False):
            assert torch.equal(kwargs['txt'][known],pre.first_latent[known].bfloat16())
            assert torch.equal(kwargs['timestep'][known],torch.zeros_like(kwargs['timestep'][known]))
            calls+=1
        return forward(*args,**kwargs)
    def checked_sample(noise):
        assert torch.equal(noise[known],noises[0][known])
        return sample(noise)
    with patch.object(engine.dit,'forward',checked_forward),patch.object(engine,'sample_block',checked_sample):
        identity,identity_attempts=native_candidates(engine,pre,z,noises[0],0.,.01,base+100,count=2,max_proposals=1)
        assert len(identity)==1 and identity_attempts[0]['duplicate']
        candidates,attempts=native_candidates(engine,pre,z,noises[0],.03,.01,base+200,count=2,max_proposals=2)
    assert calls>=64
    assert engine.continue_from(identity[0].state,noises[1:])==expected
    engine.restore(original)
    assert same_computed_history(engine,identity[0].state)
    for candidate in candidates:
        assert candidate.ids==ids and candidate.state.generated_ids==original.generated_ids
        assert candidate.state.prompt_ids==pre.prompt_ids
        assert torch.equal(candidate.latent[known],pre.first_latent[known])
        engine.rebuild(candidate.state)
        assert same_computed_history(engine,candidate.state)
        assert engine.decoder_ids==candidate.state.decoder_ids
    outcomes={}
    for label in (0,1,1,0):
        proposed=math.sqrt(1-.03**2)*noises[0]+.03*engine.noise(base+300+label)[0]
        proposed[known]=noises[0][known]
        engine.restore(pre)
        zz,ii,qq=engine.advance(proposed);state=engine.snapshot()
        assert torch.equal(zz[known],pre.first_latent[known])
        assert state.generated_ids==ii[remainder:]
        future=engine.continue_from(state,noises[1:])
        item=(zz,ii,qq,future)
        if label in outcomes:
            old=outcomes[label]
            assert torch.equal(zz,old[0]) and ii==old[1] and torch.equal(qq,old[2]) and future==old[3]
        outcomes[label]=item
    return dict(remainder=remainder,cohort='M' if remainder else 'F',status='pass',
                prompt=prompt,prompt_tokens=len(pre.prompt_ids),free_positions=16-remainder,
                clean_conditioning_forward_checks=calls,candidates=len(candidates),attempts=attempts,
                checks=['identity','known_latents','known_noise','every_step_clean_conditioning',
                        'prompt_positions','accepted_tokens','cache_rebuild','penalty_context',
                        'AB_BA_order','paired_future_noise'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1);p.add_argument('--output',required=True)
    a=p.parse_args();engine=ColaStateEngine(os.environ['COLA_CHECKPOINT'])
    prompts=prompts_for_remainders(engine.tokenizer)
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w') as f:
        for remainder in range(16):
            if remainder%a.shards!=a.shard:continue
            result=check(engine,prompts[remainder],remainder)
            f.write(json.dumps(result)+'\n');f.flush()
            print(json.dumps({k:result[k] for k in ['remainder','cohort','status','candidates']}),flush=True)
