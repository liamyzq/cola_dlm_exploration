"""Committed P1 perturbation and P2 conditional-recovery workers for idea 002."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time
import torch
from src.models.cola_basin import ColaBasin
from src.tasks.task_basin_data import named_seed, score_output, token_layout


def now():
    return datetime.now(timezone.utc).isoformat()


def confidence(logits,layout):
    rows=[]
    for field,pos in enumerate(layout['field_positions']):
        x=logits[pos]; original=layout['answer_ids'][pos]; alternative=layout['target_ids'][field][pos]
        lp=x.log_softmax(-1); prob=lp.exp()
        rows.append(dict(field=field,position=pos,original_id=original,alternative_id=alternative,
            gap=float(x[original]-x[alternative]),original_probability=float(prob[original]),
            alternative_probability=float(prob[alternative]),entropy=float(-(prob*lp).sum())))
    return rows


def run(config,out,shard,shards):
    started=time.monotonic(); out.mkdir(parents=True,exist_ok=True)
    (out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    worlds=[json.loads(line) for line in Path(config['worlds']).read_text().splitlines()]
    worlds=[w for w in worlds if w['split']==config['split'] and (not config.get('subset') or w[config['subset']])]
    worlds=worlds[shard::shards]
    model=ColaBasin(config['checkpoint'],load_dit=config['stage']=='recovery')
    (out/'latents').mkdir(exist_ok=True)
    count=0; eligible=0; anchors=[]
    with (out/'records.jsonl').open('w') as stream, torch.no_grad():
        for world in worlds:
            if config.get('variant'):
                world=dict(world,variant=config['variant'])
                world['layouts']=[token_layout(model.tokenizer,world,q,config['variant']) for q in (0,1)]
            clean=[]; metadata=[]
            for query,layout in enumerate(world['layouts']):
                z=model.encode(layout['full_ids']); clean.append(z)
                ids,text,logits=model.read(z,layout)
                metadata.append(dict(world_id=world['world_id'],query=query,domain=world['domain'],template=world['template'],
                    ids=ids,text=text,clean_exact=ids==layout['answer_ids'],confidence=confidence(logits,layout),
                    **score_output(world,layout,ids,text)))
            paired=all(m['clean_exact'] for m in metadata); eligible+=int(paired)
            for m in metadata:
                m['paired_clean']=paired; anchors.append(m)
            torch.save({'clean':[z.cpu() for z in clean]},out/'latents'/f"{world['world_id']}-clean.pt")
            for query,layout in enumerate(world['layouts']):
                if config.get('variant')=='no_query' and query==1:
                    continue
                z=clean[query]; start=layout['prefix_length']; length=layout['answer_length']
                base=dict(world_id=world['world_id'],world_index=world['index'],query=query,domain=world['domain'],
                    template=world['template'],paired_clean=paired,stage=config['stage'])
                residuals=[]
                points=config['sigmas'] if config['stage']=='noise' else config['restart_indices']
                for point in points:
                    for seed_id in range(config['seeds']):
                        if config['stage']=='noise':
                            seed=named_seed(world,10,seed_id)
                            eps=model.gaussian((length,16),seed)
                            delta=float(point)*eps
                            changed=z.clone(); changed[start:start+length]+=delta
                            variants=[('noise',-1,changed,delta,None)]
                            extra=dict(sigma=point,noise_seed=seed,seed_id=seed_id)
                        else:
                            seed=named_seed(world,20,seed_id)
                            eps=model.gaussian(z[start:].shape,seed)
                            changed=model.recover(z,start,eps,point,config['cfg'])
                            e=changed[start:start+length]-z[start:start+length]
                            residuals.append(dict(restart_index=point,seed_id=seed_id,residual=e.cpu()))
                            variants=[('real',-1,changed,e,None)]
                            for rot_id in range(config['rotations']):
                                rs=named_seed(world,30,seed_id,rot_id+1)
                                er=e@model.rotation(rs)
                                rotated=changed.clone(); rotated[start:start+length]=z[start:start+length]+er
                                variants.append(('rotated',rot_id,rotated,er,rs))
                            extra=dict(restart_index=point,noise_fraction=float(model.timesteps[point])/1000,
                                cfg=config['cfg'],noise_seed=seed,seed_id=seed_id,
                                blocks=(len(z)-start//16*16)//16,steps_per_block=16-point)
                        for kind,rotation_id,changed,delta,rotation_seed in variants:
                            ids,text,logits=model.read(changed,layout)
                            row=dict(**base,**extra,kind=kind,rotation_id=rotation_id,rotation_seed=rotation_seed,
                                rms=float(delta.square().mean().sqrt()),max_channel_abs=float(delta.abs().max()),
                                ids=ids,text=text,**score_output(world,layout,ids,text))
                            if config['stage']=='recovery':
                                lp=logits.log_softmax(-1); row['mean_decoder_entropy']=float(-(lp.exp()*lp).sum(-1).mean())
                            stream.write(json.dumps(row)+'\n'); count+=1
                        if config.get('variant')=='no_query':
                            # One actual decode, two analysis-only role labels.
                            twin=dict(row,query=1)
                            stream.write(json.dumps(twin)+'\n');count+=1
                        stream.flush()
                if residuals:
                    torch.save(residuals,out/'latents'/f"{world['world_id']}-q{query}-residuals.pt")
            print(json.dumps(dict(world_id=world['world_id'],paired_clean=paired,rows=count,seconds=time.monotonic()-started)),flush=True)
            (out/'anchors.jsonl').write_text(''.join(json.dumps(m)+'\n' for m in anchors))
    expected=len(worlds)*2*len(points)*config['seeds']*(1 if config['stage']=='noise' else 1+config['rotations'])
    assert count==expected,(count,expected)
    summary=dict(finished_at=now(),worlds=len(worlds),paired_clean_worlds=eligible,records=count,counts=model.counts,
        elapsed_seconds=time.monotonic()-started,peak_memory_gb=torch.cuda.max_memory_allocated()/1e9,
        actual_timesteps=model.timesteps.tolist(),shard=shard,shards=shards)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary),flush=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument('--config',required=True); p.add_argument('--output',required=True)
    p.add_argument('--shard',type=int,default=0); p.add_argument('--shards',type=int,default=1)
    args=p.parse_args(); run(json.loads(Path(args.config).read_text()),Path(args.output),args.shard,args.shards)

if __name__=='__main__':
    main()
