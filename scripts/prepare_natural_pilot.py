"""Freeze the F pilot manifest from terminal, reward-blind candidate records."""
import argparse,json
from pathlib import Path


def prepare(repo,collection):
    assert (collection/'exit.txt').read_text().strip()=='0'
    calibration=json.loads((repo/'experiments/001_same_prefix_state/results/r3_eta_v1.json').read_text())['F']
    pairs=calibration['selected_pairs'].copy()
    launch=json.loads((collection/'launch.json').read_text())
    rows=[json.loads(x) for x in (collection/'candidates/roots.jsonl').read_text().splitlines()]
    assert [x['root_id'] for x in rows]==list(range(8,8+len(rows)))
    for row in rows:
        for arm in row['arms']:
            assert arm['eta']==.03
            if arm['candidates']==2:
                pairs.append(dict(root_id=row['root_id'],source_id=row['source_id'],pair_file=str(collection/'candidates'/arm['pair_file']),origin_experiment=launch['experiment'],commit=launch['commit']))
    assert len(pairs)<=32 and (len(pairs)==32 or rows[-1]['root_id']==127)
    assert len({x['source_id'] for x in pairs})==len(pairs)
    pairs.sort(key=lambda x:x['root_id'])
    manifest=Path('experiments/001_same_prefix_state/data/r4_pilot_f_pairs.json')
    (repo/manifest).write_text(json.dumps(pairs,indent=2)+'\n')
    cfg=dict(experiment_id='001-r4-pilot-f-v1',phase='R4 F distribution pilot',cohort='F',pair_manifest=str(manifest),eta=.03,epsilon=.01,euler_steps=16,cfg=7.,repetition_penalty=1.,noise_seed_a=310000000,noise_seed_b=410000000,samples_a=4,samples_b=4,future_tokens=32,primary_metric='conditional_cross_split_H_token',comparator='native reference with exact emitted IDs; independent A/B paired noise',budget=f'{len(pairs)} fixed pairs x2 candidates x8 futures; maximum512 trajectories',stopping_rule='Complete the fixed manifest, without pair replacement or outcome-based extension',invalidation_conditions='Wrong candidate replay, changed emitted IDs, A/B noise overlap, missing manifest roots, or changed source pin invalidates the affected measurement',source_revision='7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c',checkpoint_revision='c1eafdd9cfd8064aeb917d569ef70a075b353eed')
    (repo/'configs/001_same_prefix_state/r4_pilot_f.json').write_text(json.dumps(cfg,indent=2)+'\n')
    print(json.dumps(dict(pairs=len(pairs),root_ids=[x['root_id'] for x in pairs],manifest=str(manifest))))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--collection',required=True);a=p.parse_args();prepare(Path(a.repo),Path(a.collection))
