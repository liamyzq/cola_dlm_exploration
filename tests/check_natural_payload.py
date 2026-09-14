"""Check saved natural F/M candidate replay before distribution experiments."""
import argparse,json,os
from pathlib import Path
import torch
from src.models.cola_state import ColaStateEngine
from src.methods.same_prefix import native_candidates
from src.tasks.natural_candidates import make_root,save_pair,restore_pair

@torch.inference_mode()
def run(out):
    out.mkdir(parents=True,exist_ok=False)
    items=[json.loads(x) for x in Path('/home/mlw0719/cola_dlm_exploration_storage/datasets/001_natural_continuation_v1/development.jsonl').read_text().splitlines()]
    engine=ColaStateEngine(os.environ['COLA_CHECKPOINT'])
    records=[]
    for cohort in ('F','M'):
        item=next(x for x in items[:8] if x['prompt_tokens']%16)
        root,reason=make_root(engine,item,cohort,91000000+item['root_id']*10000)
        assert root is not None,reason
        cs,proposals=native_candidates(engine,root['pre'],root['latent'],root['noise'],.01,.01,191000000,count=2,max_proposals=2)
        file=out/f'{cohort}.pt';save_pair(file,item,root,cs)
        payload=torch.load(file,map_location='cpu',weights_only=True)
        noises=engine.noise(81000000,2)
        for i,candidate in enumerate(cs):
            restored=restore_pair(engine,payload,i)
            for old,new in ((candidate.state.dit_cache,restored.dit_cache),(candidate.state.decoder_cache,restored.decoder_cache)):
                for a,b in zip(old,new):
                    for xs,ys in zip(a,b):
                        assert (xs is None)==(ys is None)
                        if xs is not None:assert all(torch.equal(x,y) for x,y in zip(xs,ys))
            assert engine.continue_from(candidate.state,noises)==engine.continue_from(restored,noises)
        records.append(dict(cohort=cohort,root_id=item['root_id'],candidates=len(cs),status='pass',proposals=proposals))
    (out/'checks.json').write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps(records),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();run(Path(a.output))
