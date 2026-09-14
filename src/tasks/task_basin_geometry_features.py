"""Clean local margin gradients on the predefined boundary cohort."""
import argparse
import json
from pathlib import Path
import time
import torch
from src.models.cola_basin import ColaBasin
from src.tasks.task_basin_run import confidence


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();cfg=json.loads(Path(a.config).read_text());out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    worlds=[json.loads(line) for line in Path(cfg['worlds']).read_text().splitlines()]
    worlds=[w for w in worlds if w['split']==cfg['split'] and (not cfg.get('subset') or w[cfg['subset']])]
    model=ColaBasin(cfg['checkpoint']);started=time.monotonic();count=0
    with (out/'features.jsonl').open('w') as stream:
        for w in worlds:
            for query,l in enumerate(w['layouts']):
                z=model.encode(l['full_ids']);start=l['prefix_length'];length=l['answer_length']
                with torch.no_grad():clean_conf=confidence(model.decode(z,start,length),l)
                for field,pos in enumerate(l['field_positions']):
                    dz=z[start:start+length].clone().requires_grad_(True)
                    full=torch.cat([z[:start],dz,z[start+length:]])
                    logits=model.decode(full,start,length)
                    margin=logits[pos,l['answer_ids'][pos]]-logits[pos,l['target_ids'][field][pos]]
                    grad=torch.autograd.grad(margin,dz)[0]
                    assert torch.isfinite(grad).all()
                    row=dict(world_id=w['world_id'],query=query,field=field,domain=w['domain'],template=w['template'],
                        gradient_frobenius=float(grad.norm()),gradient_coordinate_rms=float(grad.square().mean().sqrt()),
                        **{k:v for k,v in clean_conf[field].items() if k!='field'})
                    stream.write(json.dumps(row)+'\n');count+=1
                    del logits,grad,dz,full
            stream.flush();print(w['world_id'],count,flush=True)
    (out/'summary.json').write_text(json.dumps(dict(worlds=len(worlds),features=count,counts=model.counts,elapsed_seconds=time.monotonic()-started),indent=2)+'\n')

if __name__=='__main__':main()
