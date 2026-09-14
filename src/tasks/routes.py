"""Directed-route tasks and a public-constraint evaluator."""
import random
import re
import networkx as nx


DEMONSTRATIONS = [
    ('Roads: A -> B; B -> C; C -> D; B -> E; E -> D.\n'
     'Find a route from A to D that visits C.\n'
     'Use only the listed roads and do not visit a town twice.\nRoute: A -> B -> C -> D.'),
    ('Roads: P -> Q; Q -> R; R -> S; Q -> T; T -> S.\n'
     'Find a route from P to S that visits R.\n'
     'Use only the listed roads and do not visit a town twice.\nRoute: P -> Q -> R -> S.'),
    ('Roads: J -> K; K -> L; K -> M; L -> N; M -> N; N -> O.\n'
     'Find a route from J to O that visits N.\n'
     'Use only the listed roads and do not visit a town twice.\nRoute: J -> K -> M -> N -> O.'),
    ('Roads: U -> V; V -> W; W -> X; V -> Y; Y -> X.\n'
     'Find a route from U to X that visits W.\n'
     'Use only the listed roads and do not visit a town twice.\nRoute: U -> V -> W -> X.'),
]


def topology(rng, difficulty):
    # A common trunk, two routes through the waypoint, and one bypass route.
    trunk_n = rng.randint(7, 10)
    tail_n = rng.randint(7, 12)
    n = min(22, trunk_n + tail_n)
    g = nx.DiGraph()
    g.add_nodes_from(range(n))
    g.add_edges_from((i, i+1) for i in range(trunk_n-1))
    branch = trunk_n-1
    a, b, bypass = trunk_n, trunk_n+1, trunk_n+2
    waypoint, target = n-2, n-1
    g.add_edges_from([(branch,a),(branch,b),(branch,bypass), (a,waypoint),
                      (b,waypoint),(waypoint,target),(bypass,target)])
    # Vary branch topology without changing the common trunk. Every auxiliary
    # town has an incoming and outgoing road; all edges respect the DAG order.
    for node in range(trunk_n+3, waypoint):
        source = rng.choice(list(range(trunk_n, node)))
        dest = rng.choice(list(range(node+1, n)))
        g.add_edge(source,node)
        g.add_edge(node,dest)
    probability = 0.12 if difficulty == 'easy' else 0.30
    for source in range(trunk_n, waypoint):
        for dest in range(source+1, n):
            if rng.random() < probability:
                g.add_edge(source,dest)
    return g, list(range(trunk_n)), waypoint, target


def make_task(graph, trunk, waypoint, target, rng, task_id, difficulty):
    names = rng.sample(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), len(graph))
    roads = [(names[a], names[b]) for a,b in graph.edges]
    rng.shuffle(roads)
    demos = DEMONSTRATIONS[:4 if difficulty == 'easy' else 2]
    prompt = '\n\n'.join(demos) + '\n\nRoads: ' + '; '.join(f'{a} -> {b}' for a,b in roads) + '.\n'
    prompt += f'Find a route from {names[0]} to {names[target]} that visits {names[waypoint]}.\n'
    prompt += 'Use only the listed roads and do not visit a town twice.\nRoute:'
    return dict(id=task_id, difficulty=difficulty, prompt=prompt, roads=roads,
                start=names[0], target=names[target], waypoint=names[waypoint],
                trunk=[names[i] for i in trunk], topology_edges=list(graph.edges),
                topology_nodes=len(graph))


def generate_tasks(count, seed, difficulty, exclude=()):
    rng = random.Random(seed)
    known = []
    for task in exclude:
        g = nx.DiGraph()
        g.add_nodes_from(range(task['topology_nodes']))
        g.add_edges_from(task['topology_edges'])
        known.append(g)
    tasks = []
    while len(tasks) < count:
        g,trunk,waypoint,target = topology(rng,difficulty)
        # Exact graph isomorphism, not renamed-node identities or fingerprints.
        if any(len(g)==len(h) and g.number_of_edges()==h.number_of_edges()
               and nx.is_isomorphic(g,h) for h in known):
            continue
        known.append(g)
        tasks.append(make_task(g,trunk,waypoint,target,rng,len(tasks),difficulty))
    return tasks


def parse_route(text):
    # A route occupies one answer line. A following blank-line-delimited prompt
    # demonstration is outside this completion answer, as in few-shot benchmarks.
    line = text.strip().split('\n')[0].strip()
    line = re.split(r'<\|(?:endoftext|im_end)\|>', line, maxsplit=1)[0].strip()
    if not re.fullmatch(r'[A-Z](?:\s*(?:->|→|,)\s*[A-Z])+\.?', line):
        return None
    return re.findall(r'[A-Z]', line)


def score(task, text):
    route = parse_route(text)
    if route is None:
        return dict(parseable=False, reward=0, reason='format')
    roads = {tuple(edge) for edge in task['roads']}
    conditions = {'start': route[0]==task['start'], 'end': route[-1]==task['target'],
                  'waypoint': task['waypoint'] in route, 'unique':len(set(route))==len(route),
                  'roads':all((a,b) in roads for a,b in zip(route,route[1:]))}
    failed = [k for k,v in conditions.items() if not v]
    return dict(parseable=True, reward=int(not failed), reason=','.join(failed), route=route)


def intervention_boundary(task, tokenizer, prompt_token_count):
    # End strictly before the first branch's successor begins. A partial first
    # generated block containing prompt tokens is not eligible for replacement.
    trunk_text = ' ' + ' -> '.join(task['trunk'])
    trunk_ids = tokenizer.encode(trunk_text).ids
    trim = prompt_token_count % 16
    first_size = 16-trim if trim else 16
    candidates = [first_size+16*i for i in range(8) if first_size+16*i <= len(trunk_ids)]
    candidates = [n for n in candidates if n >= (first_size+16 if trim else 16)]
    return (max(candidates) if candidates else None), trunk_ids


def eligible(task, tokenizer, prompt_token_count, emitted_ids):
    boundary, trunk_ids = intervention_boundary(task,tokenizer,prompt_token_count)
    if boundary is None:
        return False, 'no_full_block', boundary
    ids = list(emitted_ids)
    if len(ids)<boundary:
        return False, 'early_end', boundary
    if ids[:boundary] != trunk_ids[:boundary]:
        return False, 'wrong_trunk', boundary
    return True, 'eligible', boundary
