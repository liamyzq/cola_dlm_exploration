"""Check that the task generator and scorer implement the declared decision."""
import networkx as nx
from src.tasks.routes import generate_tasks, score


def main():
    tasks=generate_tasks(128,20260914,'easy')
    for task in tasks:
        g=nx.DiGraph(task['roads'])
        paths=list(nx.all_simple_paths(g,task['start'],task['target']))
        successful=[p for p in paths if task['waypoint'] in p]
        failed=[p for p in paths if task['waypoint'] not in p]
        assert len(successful)>=2 and failed
        for path in paths:
            assert path[:len(task['trunk'])]==task['trunk']
            assert score(task,' -> '.join(path)+'.')['reward']==int(task['waypoint'] in path)
        assert score(task,'Here is a route: '+ ' -> '.join(successful[0]))['reward']==0
        assert score(task,' -> '.join(successful[0]+[task['start']]))['reward']==0
    print('PASS: 128 route graphs have a shared trunk, multiple successes, a legal failure, and correct public scoring.')

if __name__=='__main__':
    main()
