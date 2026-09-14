"""Fixed-budget exact-target ray and projected-gradient search for idea 002."""
import argparse
import json
from pathlib import Path
import time
import torch
from src.models.cola_basin import ColaBasin
from src.tasks.task_basin_data import named_seed


def rms(x):
    return x.square().mean().sqrt()


def search(model,clean,layout,field,world,sigma,stream,base):
    start=layout['prefix_length']; length=layout['answer_length']; z=clean[start:start+length]
    target_ids=layout['target_ids'][field]; target=torch.tensor(target_ids,device=model.device)
    alt_ids=layout['prefix_ids']+target_ids+layout['full_ids'][start+length:]
    endpoint=model.encode(alt_ids)[start:start+length]-z
    successes=[]; trials=0; backward=0

    def verify(delta,channel,**info):
        nonlocal trials
        with torch.no_grad():
            x=torch.cat([clean[:start],z+delta,clean[start+length:]])
            logits=model.decode(x,start,length); ids=logits.argmax(-1).tolist()
            success=ids==target_ids; radius=float(rms(delta))
            row=dict(**base,field=field,channel=channel,rms=radius,success=success,ids=ids,
                     collateral_edits=sum(a!=b for i,(a,b) in enumerate(zip(ids,layout['answer_ids'])) if i!=layout['field_positions'][field]),**info)
            stream.write(json.dumps(row)+'\n'); trials+=1
            if success:
                successes.append(dict(channel=channel,rms=radius,**info))
        return success,radius

    ray=[]
    for i in range(17):
        success,_=verify(endpoint*(i/16),'ray',alpha=i/16)
        ray.append(success)
    origin_failed=not ray[0]
    first=next((i for i in range(1,17) if ray[i] and not ray[i-1]),None)
    if first is not None:
        low=(first-1)/16; high=first/16
        for refinement in range(8):
            mid=(low+high)/2; success,_=verify(mid*endpoint,'ray_refinement',alpha=mid,refinement=refinement)
            if success: high=mid
            else: low=mid
    random=model.gaussian(z.shape,named_seed(world,40,field)); random=random/rms(random)
    for multiplier in (1,2,4):
        radius=sigma*multiplier
        projected=endpoint*min(1.,radius/max(float(rms(endpoint)),1e-12))
        starts=[projected,random*rms(projected)]
        for init,delta in enumerate(starts):
            delta=delta.detach().clone(); best=None; bestnorm=float('inf')
            ok,norm=verify(delta,'pgd',radius=radius,init=init,step=0)
            if ok: best=delta.clone(); bestnorm=norm
            for step in range(1,25):
                delta.requires_grad_(True)
                x=torch.cat([clean[:start],z+delta,clean[start+length:]])
                logits=model.decode(x,start,length)
                top=logits.topk(2,dim=-1)
                other=torch.where(top.indices[:,0]==target,top.values[:,1],top.values[:,0])
                margin=logits.gather(-1,target[:,None]).squeeze(-1)-other
                loss=torch.relu(.5-margin).mean()
                gradient=torch.autograd.grad(loss,delta)[0]; backward+=1
                with torch.no_grad():
                    delta=delta-(radius/8)*gradient/rms(gradient).clamp_min(1e-12)
                    delta=delta*min(1.,radius/max(float(rms(delta)),1e-12))
                if step%4==0:
                    ok,norm=verify(delta,'pgd',radius=radius,init=init,step=step,loss_before_update=float(loss))
                    if ok and norm<bestnorm: best=delta.clone(); bestnorm=norm
                del logits,loss,gradient
            if best is not None and origin_failed and bestnorm>0:
                low=0.; high=1.
                for refinement in range(8):
                    mid=(low+high)/2
                    ok,_=verify(mid*best,'pgd_refinement',radius=radius,init=init,alpha=mid,refinement=refinement)
                    if ok: high=mid
                    else: low=mid
    stream.flush()
    return dict(**base,field=field,endpoint_rms=float(rms(endpoint)),endpoint_exact=ray[-1],
        success_candidates=successes,minimum_found_rms=min((r['rms'] for r in successes),default=None),
        ray_minimum_found_rms=min((r['rms'] for r in successes if r['channel'].startswith('ray')),default=None),
        native_verifications=trials,backward_steps=backward)


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True)
    p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1)
    args=p.parse_args(); cfg=json.loads(Path(args.config).read_text());out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    worlds=[json.loads(line) for line in Path(cfg['worlds']).read_text().splitlines()]
    worlds=[w for w in worlds if w['split']==cfg['split'] and (not cfg.get('subset') or w[cfg['subset']])]
    if cfg.get('world_ids'): worlds=[w for w in worlds if w['world_id'] in cfg['world_ids']]
    if cfg.get('world_limit'): worlds=worlds[:cfg['world_limit']]
    worlds=worlds[args.shard::args.shards]
    model=ColaBasin(cfg['checkpoint']); started=time.monotonic(); results=[]
    with (out/'search_trials.jsonl').open('w') as trials,(out/'search_summary.jsonl').open('w') as summaries:
        for world in worlds:
            clean=[model.encode(l['full_ids']) for l in world['layouts']]
            with torch.no_grad():
                paired=all(model.read(z,l)[0]==l['answer_ids'] for z,l in zip(clean,world['layouts']))
            for query,layout in enumerate(world['layouts']):
                base=dict(world_id=world['world_id'],domain=world['domain'],template=world['template'],query=query,paired_clean=paired)
                for field in (0,1):
                    result=search(model,clean[query],layout,field,world,cfg['sigma_star'],trials,base)
                    summaries.write(json.dumps(result)+'\n');summaries.flush();results.append(result)
                    print(json.dumps({k:v for k,v in result.items() if k!='success_candidates'}),flush=True)
    summary=dict(worlds=len(worlds),targets=len(results),backward_steps=sum(r['backward_steps'] for r in results),
                 native_verifications=sum(r['native_verifications'] for r in results),counts=model.counts,
                 elapsed_seconds=time.monotonic()-started,peak_memory_gb=torch.cuda.max_memory_allocated()/1e9)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
