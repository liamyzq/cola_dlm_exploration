"""Summarize the fixed eight-root development probe from terminal raw outputs."""
import argparse
import json
from pathlib import Path
from src.methods.same_prefix_statistics import aggregate, root_statistics
from src.tasks.routes import score


def summarize(runs, manifest):
    items = {x['root_id']: x for x in json.loads(manifest.read_text())}
    records = []
    for run in runs:
        assert (run / 'exit.txt').read_text().strip() == '0'
        folder = run / 'probe'
        for line in (folder / 'roots.jsonl').read_text().splitlines():
            row = json.loads(line)
            item = items[row['root_id']]
            assert row['source_id'] == item['source_id']
            assert row['prefix_ids'] == item['prefix_ids']
            raw = json.loads((folder / f"future-root-{row['root_id']}.json").read_text())
            rewards = {}
            for split in ('A', 'B'):
                rewards[split] = []
                assert len(raw[split]) == row['candidates']
                for candidate in raw[split]:
                    assert len(candidate) == 4
                    values = []
                    for future in candidate:
                        assert future['generated_ids'][:len(row['prefix_ids'])] == row['prefix_ids']
                        rescored = score(item['task'], future['text'])
                        assert rescored == future['score']
                        values.append(rescored['reward'])
                    rewards[split].append(values)
                assert rewards[split] == row['rewards'][split]
            stats = root_statistics(rewards['A'], rewards['B'])
            assert all(row[k] == v for k, v in stats.items())
            records.append(row)
    assert len(records) == len(items) and {x['root_id'] for x in records} == set(items)
    result = aggregate(records)
    for name in ('h', 'g'):
        endpoint = result[name]
        if endpoint is not None:
            endpoint['bootstrap_degenerate'] = endpoint['ci95'][0] == endpoint['ci95'][1]
            if endpoint['bootstrap_degenerate']:
                endpoint['empirical_bootstrap_ci95'] = endpoint.pop('ci95')
                endpoint['ci95'] = None
                endpoint['interval_note'] = 'Degenerate empirical bootstrap; not a population zero bound.'
    result.update(stage='bounded Branch-M development probe', attempted_roots=len(records),
        paired_roots=sum(x['candidates'] == 2 for x in records),
        reference_only_roots=sum(x['candidates'] == 1 for x in records),
        proposals=sum(len(x['proposals']) for x in records),
        future_trajectories=sum(x['candidates'] * 8 for x in records),
        successful_futures=sum(sum(sum(c) for c in x['rewards'][s]) for x in records for s in ('A', 'B')),
        reference_successes=sum(sum(x['rewards'][s][0]) for x in records for s in ('A', 'B')),
        alternative_successes=sum(sum(sum(c) for c in x['rewards'][s][1:]) for x in records for s in ('A', 'B')),
        construction_worker_seconds=sum(x['construction_seconds'] for x in records),
        total_worker_seconds=sum(x['total_seconds'] for x in records),
        future_worker_seconds=sum(x['split_costs'][s]['seconds'] for x in records for s in ('A', 'B')),
        per_root=[{k: x[k] for k in ('root_id', 'source_id', 'candidates', 'h', 'g', 'reference', 'selected_value', 'selected', 'rewards', 'prefix_text')} for x in sorted(records, key=lambda x: x['root_id'])],
        runs=[str(x) for x in runs])
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('runs', nargs='+')
    p.add_argument('--manifest', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    result = summarize([Path(x) for x in a.runs], Path(a.manifest))
    Path(a.output).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'per_root'}, indent=2))
