"""Bounded Copy/Chain/Branch/Matched-full diagnosis with compact demonstrations."""
import argparse,json,math,os,random,time
from pathlib import Path
import networkx as nx
import torch
from src.models.cola_state import ColaStateEngine
from src.tasks.routes import TOWN_NAMES,score
from src.tasks.route_diagnostics import answer_diagnostics,boundary_funnel


def graph_instance(rng,cell):
    trunk_n=rng.randint(10,12) if cell in ('copy','chain','matched_full') else rng.randint(3,5)
    trunk=list(range(trunk_n));g=nx.DiGraph();g.add_edges_from(zip(trunk,trunk[1:]))
    if cell in ('copy','chain'):
        return g,trunk,trunk[-2],trunk[-1],trunk,None
    next_node=trunk_n;arms=[]
    for _ in range(3):
        length=rng.randint(1,3) if cell=='branch' else rng.randint(2,4)
        arm=list(range(next_node,next_node+length));next_node+=length;arms.append(arm)
    waypoint=next_node;target=next_node+1
    for i,arm in enumerate(arms):
        path=[trunk[-1]]+arm+[waypoint if i<2 else target]
        g.add_edges_from(zip(path,path[1:]))
    g.add_edge(waypoint,target)
    assert not nx.has_path(g,arms[2][0],waypoint)
    solution=trunk+arms[0]+[waypoint,target]
    bad=trunk+arms[2]+[target]
    return g,trunk,waypoint,target,solution,bad


def format_question(task,cell):
    if cell=='copy':
        return 'Copy this route exactly: '+' -> '.join(task['solution'])+'.\nRoute:'
    roads='; '.join(f'{a} -> {b}' for a,b in task['roads'])
    return (f'Roads: {roads}.\nFrom {task["start"]} to {task["target"]}, visit {task["waypoint"]}. '
            'Use listed directed roads, no repeated town.\nRoute:')


def named_task(rng,cell):
    graph,trunk,waypoint,target,solution,bad=graph_instance(rng,cell)
    names=rng.sample(TOWN_NAMES,len(graph));roads=[(names[a],names[b]) for a,b in graph.edges];rng.shuffle(roads)
    return dict(roads=roads,start=names[0],target=names[target],waypoint=names[waypoint],
        trunk=[names[n] for n in trunk],solution=[names[n] for n in solution],
        bad_solution=None if bad is None else [names[n] for n in bad],
        topology_edges=list(graph.edges),topology_nodes=len(graph))


def generate(cfg,tokenizer):
    rng=random.Random(cfg['task_seed']);cell=cfg['cell']
    demo_cell='branch' if cell=='matched_full' else cell
    demo=named_task(random.Random(cfg['demonstration_seed']),demo_cell)
    demo_text=format_question(demo,cell)+' '+' -> '.join(demo['solution'])+'.'
    tasks=[];excluded=[];groups=[]
    for draw in range(cfg['max_layout_draws']):
        if len(tasks)==cfg['tasks']:break
        task=named_task(rng,cell);task['prompt']=demo_text+'\n\n'+format_question(task,cell)
        tokens=len(tokenizer.encode(task['prompt']).ids)
        blocks=math.ceil((cfg['generated_tokens']+tokens%16)/16)
        total=tokens-tokens%16+blocks*16
        if total>512:
            excluded.append(dict(draw=draw,prompt_tokens=tokens,allocated_total=total));continue
        graph=nx.DiGraph(task['topology_edges']);group=None
        for i,old in enumerate(groups):
            if nx.is_isomorphic(graph,old):group=i;break
        if group is None:group=len(groups);groups.append(graph)
        task.update(id=len(tasks),cell=cell,source_id=f'{cell}-topology-{group}',
            prompt_tokens=tokens,allocated_total=total,blocks=blocks)
        assert score(task,' -> '.join(task['solution'])+'.')['reward']==1
        if task['bad_solution'] is not None:
            assert score(task,' -> '.join(task['bad_solution'])+'.')['reward']==0
        tasks.append(task)
    assert len(tasks)==cfg['tasks'],(cell,len(tasks),len(excluded))
    return tasks,excluded


@torch.inference_mode()
def run(a):
    cfg=json.loads(Path(a.config).read_text());out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    engine=ColaStateEngine(os.environ['COLA_CHECKPOINT'],steps=cfg['euler_steps'],cfg=cfg['cfg'],repetition_penalty=cfg['repetition_penalty'])
    tasks,excluded=generate(cfg,engine.tokenizer)
    (out/'tasks.json').write_text(json.dumps(tasks,indent=2)+'\n');(out/'layout_exclusions.json').write_text(json.dumps(excluded,indent=2)+'\n')
    with (out/'samples.jsonl').open('w') as f:
        for task in tasks:
            for repeat in range(cfg['samples_per_task']):
                torch.cuda.synchronize();start=time.perf_counter();before=engine.calls.copy()
                engine.begin(task['prompt']);seed=cfg['noise_seed']+task['id']*10000+repeat
                for noise in engine.noise(seed,task['blocks']):engine.advance(noise)
                text=engine.text();record=score(task,text)
                mixed,full=boundary_funnel(task,engine.tokenizer,len(engine.prompt_ids),list(engine.generated_ids))
                record.update(answer_diagnostics(task,engine.tokenizer,list(engine.generated_ids)))
                route=record.get('route',[]);trunk=task['trunk']
                branch=(route[len(trunk)] if len(route)>len(trunk) and route[:len(trunk)]==trunk else None)
                torch.cuda.synchronize()
                record.update(task_id=task['id'],source_id=task['source_id'],repeat=repeat,cell=cfg['cell'],
                    noise_seed=seed,generated_ids=engine.generated_ids,text=text,prompt_tokens=len(engine.prompt_ids),
                    mixed=mixed,full=full,first_branch_successor=branch,
                    elapsed_seconds=time.perf_counter()-start,calls={k:engine.calls[k]-before[k] for k in before})
                f.write(json.dumps(record)+'\n');f.flush();print(json.dumps({k:record[k] for k in ('task_id','repeat','reward','parseable','cell')}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True);run(p.parse_args())
