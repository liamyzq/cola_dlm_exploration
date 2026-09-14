"""Independent A/B continuation measurements for fixed native same-text states."""
import argparse,json,os,time
from pathlib import Path
import numpy as np
import torch
from src.models.cola_state import ColaStateEngine
from src.tasks.natural_candidates import restore_pair
from src.methods.token_distribution import token_heterogeneity,aggregate_distribution


@torch.inference_mode()
def measure_pair(engine,payload,cfg,out):
    """The candidate payload is fixed before either future noise set is drawn."""
    torch.cuda.synchronize();start=time.perf_counter();before=engine.calls.copy()
    states=[restore_pair(engine,payload,j) for j in range(len(payload['candidate_latents']))]
    anchor=len(payload['reference_generated_ids'])
    root_id=payload['root_id'];length=cfg['future_tokens'];assert length==32
    blocks=length//16
    samples={};noise_archive={};costs={}
    for split in ('A','B'):
        torch.cuda.synchronize();split_start=time.perf_counter();split_before=engine.calls.copy()
        count=cfg[f'samples_{split.lower()}'];base=cfg[f'noise_seed_{split.lower()}']+root_id*10000
        noises=[engine.noise(base+i,blocks) for i in range(count)]
        noise_archive[split]=torch.stack(noises).cpu()
        samples[split]=[]
        for state in states:
            suffixes=[]
            for noise in noises:
                ids=engine.continue_from(state,noise)
                assert ids[:anchor]==tuple(payload['reference_generated_ids'])
                suffix=ids[anchor:];assert len(suffix)==length
                suffixes.append(suffix)
            samples[split].append(suffixes)
        torch.cuda.synchronize()
        costs[split]=dict(seconds=time.perf_counter()-split_start,
            calls={k:engine.calls[k]-split_before[k] for k in split_before},
            seeds=list(range(base,base+count)))
    torch.cuda.synchronize()
    record=dict(root_id=root_id,source_id=payload['source_id'],candidates=len(states),
        h_token=token_heterogeneity(samples['A'],samples['B']),
        future_tokens=length,samples_a=cfg['samples_a'],samples_b=cfg['samples_b'],
        future_seconds=time.perf_counter()-start,
        calls={k:engine.calls[k]-before[k] for k in before},split_costs=costs)
    # Both actual noise arrays and raw token IDs are retained for replay and
    # independent inspection. EOS padding belongs to the statistic only;
    # generation of the entire declared horizon remains charged.
    torch.save(noise_archive,out/f'noise-root-{root_id}.pt')
    (out/f'future-root-{root_id}.json').write_text(json.dumps(samples)+'\n')
    return record


@torch.inference_mode()
def run(a):
    cfg=json.loads(Path(a.config).read_text());out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    assert cfg['noise_seed_a']+128*10000 < cfg['noise_seed_b']
    entries=json.loads(Path(cfg['pair_manifest']).read_text())
    engine=ColaStateEngine(os.environ['COLA_CHECKPOINT'],steps=cfg['euler_steps'],cfg=cfg['cfg'],repetition_penalty=cfg['repetition_penalty'])
    results=[]
    with (out/'measurements.jsonl').open('w') as f:
        for entry in entries:
            if entry['root_id']%a.shards!=a.shard:continue
            payload=torch.load(entry['pair_file'],map_location='cpu',weights_only=True)
            assert payload['root_id']==entry['root_id'] and payload['source_id']==entry['source_id']
            record=measure_pair(engine,payload,cfg,out);record.update(pair_file=entry['pair_file'],cohort=cfg['cohort'])
            results.append(record);f.write(json.dumps(record)+'\n');f.flush();print(json.dumps(record),flush=True)
    (out/'summary.json').write_text(json.dumps(aggregate_distribution(results),indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True)
    p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1);run(p.parse_args())
