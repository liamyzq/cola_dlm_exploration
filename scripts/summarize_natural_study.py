"""Aggregate a terminal pilot or fixed-source confirmation with source clustering."""
import argparse,json
from pathlib import Path
import numpy as np
from src.methods.token_distribution import aggregate_distribution,pad_after_eos,token_heterogeneity


def summarize(runs,expected,kind):
    wanted=json.loads(expected.read_text()) if kind=='pilot' else [json.loads(s) for s in expected.read_text().splitlines()]
    source_by_id={x['root_id']:x['source_id'] for x in wanted};records=[];diagnostics=[]
    for run in runs:
        assert (run/'exit.txt').read_text().strip()=='0'
        folder=run/('measurement' if kind=='pilot' else 'confirmation')
        file=folder/('measurements.jsonl' if kind=='pilot' else 'roots.jsonl')
        for line in file.read_text().splitlines():
            row=json.loads(line);index=row['root_id'];assert source_by_id[index]==row['source_id'];records.append(row)
            if row['candidates']<2:continue
            raw=json.loads((folder/f'future-root-{index}.json').read_text())
            # Recomputing the endpoint from retained raw tokens detects an
            # aggregation/transcription mismatch, not a new hypothesis test.
            assert token_heterogeneity(raw['A'],raw['B'])==row['h_token']
            aa=pad_after_eos(raw['A']);bb=pad_after_eos(raw['B'])
            differences=np.concatenate([aa[0]!=aa[1],bb[0]!=bb[1]],axis=0)
            diagnostics.append(dict(root_id=index,source_id=row['source_id'],h_token=row['h_token'],paired_future_count=len(differences),any_token_disagreements=int(differences.any(axis=1).sum()),token_position_disagreement=float(differences.mean())))
    assert len(records)==len(source_by_id) and {x['root_id'] for x in records}==set(source_by_id)
    result=aggregate_distribution(records);result.update(stage=kind,cohort='F',attempted_roots=len(records),paired_roots=len(diagnostics),root_statuses={s:sum(x.get('root_status','live')==s for x in records) for s in sorted({x.get('root_status','live') for x in records})},future_trajectories=sum(x['candidates']*(x.get('samples_a',0)+x.get('samples_b',0)) for x in records),future_worker_seconds=sum(x.get('future_seconds',0) for x in records),per_root=diagnostics,runs=[str(x) for x in runs])
    result['paired_future_count']=sum(x['paired_future_count'] for x in diagnostics)
    result['any_token_disagreements']=sum(x['any_token_disagreements'] for x in diagnostics)
    result['mean_token_position_disagreement']=float(np.mean([x['token_position_disagreement'] for x in diagnostics])) if diagnostics else None
    if kind=='confirmation':result['total_worker_seconds']=sum(x['total_seconds'] for x in records)
    h=result['h_token']
    result['bootstrap_degenerate']=h is not None and h['ci95'][0]==h['ci95'][1]
    if result['bootstrap_degenerate']:
        result['interval_note']='The empirical source bootstrap is degenerate. Do not interpret a zero-width interval as a population equivalence bound.'
    result['disagreement_note']='Paired suffix disagreement is a coupling diagnostic, not evidence by itself of different marginal future distributions.'
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+');p.add_argument('--expected',required=True);p.add_argument('--kind',choices=['pilot','confirmation'],required=True);p.add_argument('--output',required=True);a=p.parse_args()
    result=summarize([Path(x) for x in a.runs],Path(a.expected),a.kind);Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='per_root'},indent=2))
