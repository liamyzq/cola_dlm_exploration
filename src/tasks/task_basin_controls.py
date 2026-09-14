"""Source-present zero/high-noise answer replacement diagnostic."""
import argparse
import json
from pathlib import Path
import time
import torch
from src.models.cola_basin import ColaBasin
from src.tasks.task_basin_data import named_seed, score_output


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True)
    args=p.parse_args();cfg=json.loads(Path(args.config).read_text());out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    worlds=[json.loads(x) for x in Path(cfg['worlds']).read_text().splitlines()]
    worlds=[w for w in worlds if w['split']==cfg['split'] and w['controls']]
    model=ColaBasin(cfg['checkpoint']);started=time.monotonic();count=0
    with (out/'records.jsonl').open('w') as stream,torch.no_grad():
        for w in worlds:
            clean=[model.encode(l['full_ids']) for l in w['layouts']]
            paired=all(model.read(z,l)[0]==l['answer_ids'] for z,l in zip(clean,w['layouts']))
            for query,l in enumerate(w['layouts']):
                z=clean[query];start=l['prefix_length'];length=l['answer_length']
                for i in range(9):
                    x=z.clone();seed=named_seed(w,50,i)
                    replacement=torch.zeros((length,16),device=model.device) if i==0 else cfg['replacement_std']*model.gaussian((length,16),seed)
                    x[start:start+length]=replacement
                    ids,text,_=model.read(x,l)
                    row=dict(world_id=w['world_id'],domain=w['domain'],template=w['template'],query=query,paired_clean=paired,
                        kind='zero' if i==0 else 'high_noise',seed=seed,seed_id=i,ids=ids,text=text,
                        **score_output(w,l,ids,text))
                    stream.write(json.dumps(row)+'\n');count+=1
            stream.flush();print(w['world_id'],count,flush=True)
    (out/'summary.json').write_text(json.dumps(dict(worlds=len(worlds),records=count,counts=model.counts,elapsed_seconds=time.monotonic()-started),indent=2)+'\n')

if __name__=='__main__':main()
