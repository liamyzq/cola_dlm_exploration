"""Summarize terminal R2 workers without changing run or research ledgers."""
import argparse,json
import networkx as nx
from pathlib import Path
from src.methods.same_prefix_statistics import aggregate


def summarize(path):
    assert (path/'exit.txt').read_text().strip()=='0'
    cfg=json.loads((path/'evaluation/config.json').read_text())
    rows=[json.loads(x) for x in (path/'evaluation/samples.jsonl').read_text().splitlines()]
    expected={(i,j) for i in range(cfg['tasks']) for j in range(cfg['samples_per_task'])}
    assert len(rows)==len(expected) and {(x['task_id'],x['repeat']) for x in rows}==expected
    out=dict(cell=cfg['cell'],tasks=cfg['tasks'],samples=len(rows),source_topologies=len({x['source_id'] for x in rows}),artifact_dir=str(path))
    for field in ['reward','parseable','first_edge_correct']:
        stats=aggregate([dict(graph_id=x['source_id'],h=None,g=float(x[field])) for x in rows])
        out[field]=dict(count=sum(x[field] for x in rows),**stats['g'])
    if out['reward']['count']==0:
        out['reward']['empirical_bootstrap_ci95']=out['reward'].pop('ci95')
        out['reward']['ci95']=None
        out['reward']['interval_note']='The all-zero nonparametric bootstrap is degenerate and does not provide a useful population upper bound.'
    out['best_of_2_success']=sum(any(x['reward'] for x in rows if x['task_id']==i) for i in range(cfg['tasks']))
    out['eligible_mixed']=sum(x['mixed'] is not None and x['mixed']['status']=='eligible' for x in rows)
    out['eligible_full']=sum(any(z['status']=='eligible' for z in x['full']) for x in rows)
    out['termination_within_horizon']=sum(x['termination_token'] is not None for x in rows)
    out['post_termination_tokens']=sum(x['generated_tokens_after_termination'] for x in rows)
    out['legal_prefix_towns_histogram']={str(n):sum(x['legal_prefix_towns']==n for x in rows) for n in sorted({x['legal_prefix_towns'] for x in rows})}
    if cfg['cell'] in ('branch','matched_full'):
        tasks=json.loads((path/'evaluation/tasks.json').read_text())
        crossed=[x for x in rows if x['first_branch_successor'] is not None]
        good=0;bad=0;unlisted=0
        for x in crossed:
            task=tasks[x['task_id']];graph=nx.DiGraph(task['roads']);successor=x['first_branch_successor']
            if not graph.has_edge(task['trunk'][-1],successor):unlisted+=1
            elif nx.has_path(graph,successor,task['waypoint']):good+=1
            else:bad+=1
        out['first_branch']=dict(crossed_after_correct_trunk=len(crossed),can_reach_waypoint=good,irreversible_bypass=bad,unlisted_edge=unlisted)
    out['worker_seconds']=sum(x['elapsed_seconds'] for x in rows)
    out['calls']={k:sum(x['calls'][k] for x in rows) for k in rows[0]['calls']}
    out['eligible_full_with_reference_success']=sum(x['reward'] and any(z['status']=='eligible' for z in x['full']) for x in rows)
    out['eligible_mixed_with_reference_success']=sum(x['reward'] and x['mixed'] is not None and x['mixed']['status']=='eligible' for x in rows)
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+');p.add_argument('--output',required=True);a=p.parse_args()
    result=[summarize(Path(x)) for x in a.runs];Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
