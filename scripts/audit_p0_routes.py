"""Reconstruct P0 layouts and causally inspect saved generations; no model sampling."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import subprocess
import time
import networkx as nx
from tokenizers import Tokenizer
from src.tasks.routes import generate_tasks,intervention_boundary,score
from src.tasks.route_diagnostics import boundary_funnel,answer_diagnostics,trunk_prefix_status


def run(config_path,output):
    cfg=json.loads(Path(config_path).read_text())
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    tok=Tokenizer.from_file(cfg['tokenizer'])
    summary={'experiment_id':cfg['experiment_id'],'kind':'CPU reconstruction of existing P0 generations',
             'implementation_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
             'source_run_commit':cfg['source_run_commit'],'difficulties':{}}
    start=time.perf_counter()
    with (out/'sample_diagnostics.jsonl').open('w') as records:
        for difficulty in ('easy','hard'):
            tasks=generate_tasks(128,cfg['task_seeds'][difficulty],difficulty)
            saved=[]
            for gpu in cfg['source_gpus']:
                path=Path(cfg['runs_base'])/f'001-p0-capability-v2-gpu{gpu}'/difficulty
                assert json.loads((path/'tasks.json').read_text())==tasks, 'Task reconstruction differs from saved task data'
                for line in (path/'samples.jsonl').read_text().splitlines():
                    row=json.loads(line);row['source_path']=str(path/'samples.jsonl');saved.append(row)
            assert len(saved)==512 and len({(x['graph_id'],x['repeat']) for x in saved})==512
            assert all(sum(x['graph_id']==i for x in saved)==4 for i in range(128))
            layouts=[]
            for task in tasks:
                p=len(tok.encode(task['prompt']).ids);m=p%16
                boundary,trunk_ids=intervention_boundary(task,tok,p)
                generated=16*math.ceil(((boundary or 32)+64+m)/16)-m
                first=16-m if m else 16
                earliest=first+16 if m else 16
                g=nx.DiGraph();g.add_nodes_from(range(task['topology_nodes']));g.add_edges_from(task['topology_edges'])
                branch=len(task['trunk'])-1;waypoint=task['topology_nodes']-2
                layouts.append(dict(graph_id=task['id'],prompt_tokens=p,generated_tokens=generated,
                    total_positions=p+generated,original_boundary=boundary,
                    original_boundary_position=None if boundary is None else p+boundary,
                    mixed_free_positions=first if m else 0,
                    earlier_full_boundary=bool(boundary is not None and earliest<boundary),
                    all_first_successors_reach_waypoint=all(nx.has_path(g,s,waypoint) for s in g.successors(branch))))
            counts=Counter();m_status=Counter();f_status=Counter();termination_vs_old=Counter();reasons=Counter()
            elapsed=0.;post_tokens=0;legal=Counter()
            for row in saved:
                task=tasks[row['graph_id']];layout=layouts[row['graph_id']]
                assert row['prompt_tokens']==layout['prompt_tokens']
                assert len(row['generated_ids'])==layout['generated_tokens']
                assert tok.decode(row['generated_ids'],skip_special_tokens=False)==row['text']
                rescored=score(task,row['text'])
                assert all(row[k]==rescored[k] for k in ('parseable','reward','reason'))
                mix,full=boundary_funnel(task,tok,row['prompt_tokens'],row['generated_ids'])
                diag=answer_diagnostics(task,tok,row['generated_ids'])
                m_status[mix['status'] if mix else 'aligned_prompt_no_mixed']+=1
                f_status[full[-1]['status'] if full else 'no_completed_full_block']+=1
                original=row['boundary_tokens']
                old_status='no_layout' if original is None else trunk_prefix_status(task,tok.decode(row['generated_ids'][:original],skip_special_tokens=False))
                termination_vs_old[old_status]+=1
                for k in ('parseable','reward','eligible'):counts[k]+=int(row[k])
                counts['first_edge_correct']+=diag['first_edge_correct']
                counts['terminated_within_horizon']+=diag['termination_token'] is not None
                counts['unsuccessful_answer_termination']+=bool(diag['termination_token'] is not None and not row['reward'])
                counts['terminated_legal_trunk']+=diag['terminated_legal_trunk']
                counts['generated_after_termination']+=diag['generated_tokens_after_termination']>0
                reasons[row['reason']]+=1;legal[diag['legal_prefix_towns']]+=1
                post_tokens+=diag['generated_tokens_after_termination'];elapsed+=row['elapsed_seconds']
                records.write(json.dumps(dict(graph_id=row['graph_id'],repeat=row['repeat'],difficulty=difficulty,
                    source_path=row['source_path'],mixed=mix,first_causal_full=full,
                    original_boundary_status_with_termination=old_status,**diag))+'\n')
            def span(key):return [min(x[key] for x in layouts),max(x[key] for x in layouts)]
            summary['difficulties'][difficulty]=dict(graphs=128,samples=512,
                prompt_token_range=span('prompt_tokens'),generated_token_range=span('generated_tokens'),
                total_position_range=span('total_positions'),
                total_positions_above_512=sum(x['total_positions']>512 for x in layouts),
                original_boundary_positions_above_512=sum(x['original_boundary_position'] is not None and x['original_boundary_position']>512 for x in layouts),
                missing_full_layout=sum(x['original_boundary'] is None for x in layouts),
                earlier_full_boundary=sum(x['earlier_full_boundary'] for x in layouts),
                all_first_successors_reach_waypoint=sum(x['all_first_successors_reach_waypoint'] for x in layouts),
                mixed_layout_graphs=sum(x['mixed_free_positions']>0 for x in layouts),
                counts=dict(counts),mixed_anchor_status=dict(m_status),first_causal_full_status=dict(f_status),
                original_boundary_status_with_termination=dict(termination_vs_old),
                answer_failure_reasons=dict(reasons),legal_prefix_towns_histogram=dict(legal),
                generated_tokens_after_termination=post_tokens,source_generation_worker_seconds=elapsed)
            (out/f'{difficulty}_layouts.json').write_text(json.dumps(layouts,indent=2)+'\n')
    summary['audit_cpu_wall_seconds']=time.perf_counter()-start
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.config,a.output)
