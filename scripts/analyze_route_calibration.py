"""Summarize all prespecified capability metrics, including unsuccessful roots."""
import argparse
import json
from pathlib import Path
import numpy as np


def summarize(paths):
    rows=[json.loads(line) for path in paths for line in path.read_text().splitlines()]
    by_graph={}
    for r in rows:
        key=(r['graph_id'],r['repeat'])
        if key in by_graph:
            raise ValueError(f'Duplicate sample {key}')
        by_graph[key]=r
    groups={}
    for r in rows:
        groups.setdefault(r['graph_id'],[]).append(r)
    # Missing or duplicate samples would change the calibration denominator.
    assert len(groups)==128 and all(len(v)==4 for v in groups.values()), 'Incomplete calibration'
    metrics=dict(graphs=len(groups),samples=len(rows),
                 parseable=float(np.mean([r['parseable'] for r in rows])),
                 eligible=float(np.mean([r['eligible'] for r in rows])),
                 success=float(np.mean([r['reward'] for r in rows])),
                 best_of_4=float(np.mean([max(r['reward'] for r in group) for group in groups.values()])),
                 total_worker_seconds=float(sum(r['elapsed_seconds'] for r in rows)),
                 median_sample_seconds=float(np.median([r['elapsed_seconds'] for r in rows])))
    metrics['gates']={'parseable':metrics['parseable']>=.9,'eligible':metrics['eligible']>=.8,
                      'success':.15<=metrics['success']<=.75,'best_of_4':metrics['best_of_4']>=.5}
    metrics['capability_gate_passed']=all(metrics['gates'].values())
    metrics['eligibility_reasons']={reason:sum(r['eligibility_reason']==reason for r in rows)
                                   for reason in sorted({r['eligibility_reason'] for r in rows})}
    return metrics


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('samples',nargs='+',type=Path)
    p.add_argument('--output',required=True,type=Path)
    args=p.parse_args()
    result=summarize(args.samples)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
