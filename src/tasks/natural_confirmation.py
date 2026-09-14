"""Fixed-source confirmation: candidate construction precedes independent futures."""
import argparse,json,os,time
from pathlib import Path
import torch
from src.models.cola_state import ColaStateEngine
from src.methods.same_prefix import native_candidates
from src.methods.token_distribution import aggregate_distribution
from src.tasks.natural_candidates import make_root,save_pair
from src.tasks.natural_state_study import measure_pair


@torch.inference_mode()
def run(a):
    cfg=json.loads(Path(a.config).read_text());out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    items=[json.loads(x) for x in Path(cfg['data']).read_text().splitlines()]
    assert len(items)==128 and len({x['source_id'] for x in items})==128
    assert cfg['noise_seed_a']+128*10000 < cfg['noise_seed_b']
    engine=ColaStateEngine(os.environ['COLA_CHECKPOINT'],steps=cfg['euler_steps'],cfg=cfg['cfg'],repetition_penalty=cfg['repetition_penalty'])
    measurements=[]
    with (out/'roots.jsonl').open('w') as f:
        for item in items:
            index=item['root_id']
            if index%a.shards!=a.shard:continue
            assert item['split']=='confirmation'
            torch.cuda.synchronize();start=time.perf_counter();before=engine.calls.copy()
            root_seed=cfg['reference_noise_seed']+index*10000
            root,reason=make_root(engine,item,cfg['cohort'],root_seed)
            record=dict(root_id=index,source_id=item['source_id'],cohort=cfg['cohort'],root_status=reason,
                        reference_noise_seed=root_seed,h_token=None,candidates=0)
            if root is not None:
                proposal_seed=cfg['proposal_noise_seed']+index*10000
                candidates,proposals=native_candidates(engine,root['pre'],root['latent'],root['noise'],
                    cfg['eta'],cfg['epsilon'],proposal_seed,count=2,max_proposals=cfg['max_proposals'])
                record.update(proposal_seed=proposal_seed,proposals=proposals,candidates=len(candidates),
                    prefix_ids=root['reference'].generated_ids,prefix_text=engine.text(root['reference'].generated_ids))
                torch.cuda.synchronize()
                record.update(construction_seconds=time.perf_counter()-start,
                    construction_calls={k:engine.calls[k]-before[k] for k in before})
                # Preserve and measure the reference fallback even when no
                # alternative passes. It contributes coverage and cost; H is
                # undefined for a single candidate.
                pair_file=out/f'pair-root-{index}.pt';save_pair(pair_file,item,root,candidates)
                payload=torch.load(pair_file,map_location='cpu',weights_only=True)
                measured=measure_pair(engine,payload,cfg,out)
                record.update(measured,pair_file=str(pair_file))
            torch.cuda.synchronize();record['total_seconds']=time.perf_counter()-start
            record['total_calls']={k:engine.calls[k]-before[k] for k in before}
            measurements.append(record);f.write(json.dumps(record)+'\n');f.flush()
            print(json.dumps({k:record[k] for k in ('root_id','root_status','candidates','h_token','total_seconds')}),flush=True)
    (out/'summary.json').write_text(json.dumps(aggregate_distribution(measurements),indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True)
    p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1);run(p.parse_args())
