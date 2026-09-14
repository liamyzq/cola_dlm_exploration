"""Freeze 100 stratified output-only audit items and a separately retained key."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import random
from scripts.analyze_task_basin import read_records
from src.tasks.task_basin_data import text_parts


def sample(rows,n,rng):
    strata=defaultdict(list)
    for row in rows:
        error='unparseable' if 'unparseable' in row['status'] else 'valid_wrong' if 'valid_wrong' in row['status'] else 'correct'
        strata[(row['domain'],row.get('sigma',row.get('noise_fraction')),error)].append(row)
    for group in strata.values():rng.shuffle(group)
    keys=list(sorted(strata));rng.shuffle(keys);chosen=[]
    while len(chosen)<n:
        for key in keys:
            if strata[key] and len(chosen)<n:chosen.append(strata[key].pop())
        if not any(strata.values()) and len(chosen)<n:raise ValueError('Insufficient distinct audit records')
    return chosen


def main():
    p=argparse.ArgumentParser();p.add_argument('--noise',nargs='+',required=True);p.add_argument('--recovery',nargs='+',required=True)
    p.add_argument('--sentence',nargs='+',required=True);p.add_argument('--worlds',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    worlds={w['world_id']:w for w in map(json.loads,Path(a.worlds).read_text().splitlines())};rng=random.Random(20260914)
    chosen=[]
    for kind,paths,n in [('noise',a.noise,50),('recovery',a.recovery,40),('sentence',a.sentence,10)]:
        chosen.extend((kind,r) for r in sample(read_records(paths),n,rng))
    rng.shuffle(chosen);blind=[];key=[]
    for i,(kind,r) in enumerate(chosen):
        w=worlds[r['world_id']];variant='sentence' if kind=='sentence' else 'record'
        audit_id=f'A{i+1:03d}'
        blind.append(dict(audit_id=audit_id,domain=w['domain'],keys=w['keys'],gold_values=w['values'],
            gold_answer=text_parts(w,0,variant)[1],output=r['text']))
        key.append(dict(audit_id=audit_id,cohort=kind,world_id=r['world_id'],query=r['query'],
            sigma=r.get('sigma'),noise_fraction=r.get('noise_fraction'),kind=r['kind'],seed_id=r['seed_id'],
            rotation_id=r['rotation_id'],parser_status=r['status'],parser_parsed=r['parsed']))
    for filename,rows in [('blind_items.jsonl',blind),('audit_key.jsonl',key)]:
        (out/filename).write_text(''.join(json.dumps(r)+'\n' for r in rows))
    (out/'sampling.json').write_text(json.dumps(dict(seed=20260914,items=100,allocation=dict(noise=50,recovery=40,sentence=10),
        strata=['cohort','domain','noise scale','predicted error type'],sampling='seeded round-robin across nonempty strata without replacement',
        reviewer_instructions='Judge each field as correct, valid_wrong, or unparseable; separately judge whether the complete output preserves both gold facts. Role, method, distance and parser labels are hidden.'),indent=2)+'\n')
    print(json.dumps(dict(items=len(blind),output=str(out))))

if __name__=='__main__':main()
