"""Run the preregistered route capability calibration on a frozen checkpoint."""
import argparse
import json
import math
import os
from pathlib import Path
import time
import torch
from src.models.cola_state import ColaStateEngine
from src.tasks.routes import generate_tasks, intervention_boundary, eligible, score


def run(args):
    config=json.loads(Path(args.config).read_text())
    out=Path(args.output)
    out.mkdir(parents=True,exist_ok=False)
    (out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    tasks=generate_tasks(config['graphs'],config['graph_seed'],config['difficulty'])
    (out/'tasks.json').write_text(json.dumps(tasks,indent=2)+'\n')
    engine=ColaStateEngine(os.environ['COLA_CHECKPOINT'],steps=config['euler_steps'],cfg=config['cfg'])
    with (out/'samples.jsonl').open('w') as f:
        for task in tasks:
            if task['id'] % args.shards != args.shard:
                continue
            for repeat in range(config['samples_per_graph']):
                torch.cuda.synchronize()
                start=time.perf_counter()
                before=engine.calls.copy()
                engine.begin(task['prompt'])
                boundary,trunk_ids=intervention_boundary(task,engine.tokenizer,len(engine.prompt_ids))
                # Always preserve a full 64-token continuation opportunity after
                # the intervention boundary, including the partial prompt block.
                requested=(boundary or 32)+config['suffix_tokens']
                blocks=math.ceil((requested+engine.trim)/16)
                seed=config['noise_seed']+task['id']*10000+repeat*100
                noises=engine.noise(seed,blocks)
                for noise in noises:
                    engine.advance(noise)
                text=engine.text()
                result=score(task,text)
                ok,reason,_=eligible(task,engine.tokenizer,len(engine.prompt_ids),engine.generated_ids)
                torch.cuda.synchronize()
                result.update(graph_id=task['id'],repeat=repeat,noise_seed=seed,
                              difficulty=config['difficulty'],eligible=ok,eligibility_reason=reason,
                              boundary_tokens=boundary,prompt_tokens=len(engine.prompt_ids),
                              generated_ids=engine.generated_ids,text=text,
                              elapsed_seconds=time.perf_counter()-start,
                              calls={k:engine.calls[k]-before[k] for k in before})
                f.write(json.dumps(result)+'\n');f.flush()
                print(json.dumps({k:result[k] for k in ['graph_id','repeat','reward','parseable','eligible','elapsed_seconds']}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--config',required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--shard',type=int,default=0)
    p.add_argument('--shards',type=int,default=1)
    run(p.parse_args())
