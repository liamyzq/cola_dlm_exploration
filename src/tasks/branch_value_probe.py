"""Bounded public-reward probe on the eight existing eligible Branch M roots."""
import argparse,json,os,time
from pathlib import Path
import torch
from src.models.cola_state import ColaStateEngine
from src.methods.same_prefix import native_candidates
from src.methods.same_prefix_statistics import root_statistics,aggregate
from src.tasks.natural_candidates import save_pair
from src.tasks.route_diagnostics import trunk_prefix_status
from src.tasks.routes import score


@torch.inference_mode()
def run(a):
    cfg=json.loads(Path(a.config).read_text());out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    items=json.loads(Path(cfg['root_manifest']).read_text());assert len(items)==8
    assert cfg['future_tokens']==32 and cfg['noise_seed_a']+80000<cfg['noise_seed_b']
    engine=ColaStateEngine(os.environ['COLA_CHECKPOINT'],steps=cfg['euler_steps'],cfg=cfg['cfg'],repetition_penalty=cfg['repetition_penalty'])
    records=[]
    with (out/'roots.jsonl').open('w') as f:
        for item in items:
            index=item['root_id']
            if index%a.shards!=a.shard:continue
            task=item['task'];torch.cuda.synchronize();start=time.perf_counter();before=engine.calls.copy()
            pre=engine.begin(task['prompt']);assert pre.trim>0
            noise=engine.noise(item['reference_noise_seed'])[0];latent,_,_=engine.advance(noise);reference=engine.snapshot()
            assert reference.generated_ids==tuple(item['prefix_ids'])
            assert trunk_prefix_status(task,engine.text(reference.generated_ids))=='eligible'
            proposal_seed=cfg['proposal_noise_seed']+index*10000
            candidates,proposals=native_candidates(engine,pre,latent,noise,cfg['eta'],cfg['epsilon'],proposal_seed,count=2,max_proposals=cfg['max_proposals'])
            torch.cuda.synchronize();construction=time.perf_counter()-start
            root=dict(earlier=[],reference=reference,noises=noise.unsqueeze(0))
            save_pair(out/f'pair-root-{index}.pt',dict(prompt=task['prompt'],root_id=index,source_id=item['source_id']),root,candidates)
            rewards={};raw={};archives={};split_costs={}
            for split in ('A','B'):
                torch.cuda.synchronize();split_start=time.perf_counter();split_before=engine.calls.copy()
                n=cfg[f'samples_{split.lower()}'];seed=cfg[f'noise_seed_{split.lower()}']+index*10000
                noises=[engine.noise(seed+j,cfg['future_tokens']//16) for j in range(n)]
                archives[split]=torch.stack(noises).cpu();raw[split]=[];rewards[split]=[]
                for candidate in candidates:
                    rr=[];yy=[]
                    for future in noises:
                        ids=engine.continue_from(candidate.state,future)
                        assert ids[:len(reference.generated_ids)]==reference.generated_ids
                        text=engine.text(ids);result=score(task,text);rr.append(result['reward'])
                        yy.append(dict(generated_ids=ids,text=text,score=result))
                    rewards[split].append(rr);raw[split].append(yy)
                torch.cuda.synchronize();split_costs[split]=dict(seconds=time.perf_counter()-split_start,seeds=list(range(seed,seed+n)),calls={k:engine.calls[k]-split_before[k] for k in split_before})
            stats=root_statistics(rewards['A'],rewards['B'])
            torch.save(archives,out/f'noise-root-{index}.pt');(out/f'future-root-{index}.json').write_text(json.dumps(raw)+'\n')
            torch.cuda.synchronize();record=dict(root_id=index,graph_id=item['source_id'],source_id=item['source_id'],original_task_id=item['original_task_id'],repeat=item['repeat'],prefix_ids=reference.generated_ids,prefix_text=engine.text(reference.generated_ids),proposal_seed=proposal_seed,proposals=proposals,rewards=rewards,construction_seconds=construction,split_costs=split_costs,total_seconds=time.perf_counter()-start,total_calls={k:engine.calls[k]-before[k] for k in before},future_tokens=32,samples_a=cfg['samples_a'],samples_b=cfg['samples_b'],**stats)
            records.append(record);f.write(json.dumps(record)+'\n');f.flush();print(json.dumps({k:record[k] for k in ['root_id','candidates','h','g','reference','selected_value']}),flush=True)
    (out/'summary.json').write_text(json.dumps(aggregate(records),indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True)
    p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1);run(p.parse_args())
