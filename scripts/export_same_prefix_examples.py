"""Export fixed earliest development examples without selecting by future effects."""
import json
from pathlib import Path
import torch
from tokenizers import Tokenizer

BASE = Path('/home/mlw0719/cola_dlm_exploration_storage')
RUNS = BASE / 'runs/001_same_prefix_state'
OUT = Path('experiments/001_same_prefix_state/results')
tokenizer = Tokenizer.from_file(str(BASE / 'checkpoints/Cola-DLM-c1eafdd/tokenizer.json'))
examples = []
for cohort, gpus in [('F', (5, 6)), ('M', (7, 8))]:
    roots = []
    for gpu in gpus:
        directory = RUNS / f'001-r3-eta-{cohort.lower()}-v1-gpu{gpu}/candidates'
        for line in (directory / 'roots.jsonl').read_text().splitlines():
            root = json.loads(line)
            for arm in root['arms']:
                if arm['eta'] == .03 and arm['candidates'] == 2:
                    roots.append((root['root_id'], directory, root, arm))
    index, directory, root, arm = sorted(roots, key=lambda x: x[0])[0]
    payload = torch.load(directory / arm['pair_file'], map_location='cpu', weights_only=True)
    ids = list(payload['reference_generated_ids'])
    assert ids == root['prefix_ids']
    accepted = next(x for x in arm['proposals'] if x['accepted'])
    example = dict(cohort=cohort, root_id=index, source_id=root['source_id'],
        selection='Earliest accepted development root at locked eta=0.03; no future-based selection',
        prompt=payload['prompt'], shared_prefix_ids=ids,
        shared_prefix_text=tokenizer.decode(ids),
        candidate_file=str(directory / arm['pair_file']),
        candidate_generation_commit='3209858356d467e620e93e83ff93982e14666d0f',
        acceptance=accepted)
    if cohort == 'F':
        pilot = RUNS / '001-r4-pilot-f-part1-v1/measurement'
        raw = json.loads((pilot / f'future-root-{index}.json').read_text())
        example['illustrative_future'] = dict(split='A', sample_index=0,
            reference_ids=raw['A'][0][0], alternative_ids=raw['A'][1][0],
            reference_text=tokenizer.decode(raw['A'][0][0]),
            alternative_text=tokenizer.decode(raw['A'][1][0]),
            source_file=str(pilot / f'future-root-{index}.json'),
            interpretation='A single common-noise realization; not a marginal distribution comparison')
    examples.append(example)
(OUT / 'same_prefix_examples_v1.json').write_text(json.dumps(examples, indent=2) + '\n')
lines = ['# Raw same-prefix development examples', '',
    'These are the earliest accepted F and M development roots at the locked eta=0.03.',
    'Selection does not use future outcomes. Exact IDs, source paths, and proposal',
    'measurements are retained in [the compact JSON](same_prefix_examples_v1.json).', '']
for example in examples:
    a = example['acceptance']
    lines += [f"## {example['cohort']}: root {example['root_id']} ({example['source_id']})", '',
        'Shared generated prefix for the reference and alternative:', '',
        '```text', example['shared_prefix_text'], '```', '',
        f"All emitted token IDs match. Raw block symmetric KL sum is {a['kl_sum']:.8g}",
        f"(maximum position {a['kl_max']:.8g}); latent displacement is {a['delta_norm']:.6g}",
        f"and displacement after BF16 conversion is {a['dit_input_bf16_delta_norm']:.6g}.",
        f"There are {a['free_positions']} free generated positions; known prompt latents remain equal.", '']
    if 'illustrative_future' in example:
        f = example['illustrative_future']
        lines += ['The first archived A noise gives these 32-token suffixes:', '',
            'Reference:', '', '```text', f['reference_text'], '```', '',
            'Alternative:', '', '```text', f['alternative_text'], '```', '',
            'This illustration shows one coupled realization. Distribution evidence comes',
            'from the independent A/B estimator across the full fixed cohort.', '']
(OUT / 'SAME_PREFIX_EXAMPLES.md').write_text('\n'.join(lines) + '\n')
print(json.dumps([{k: e[k] for k in ('cohort', 'root_id', 'source_id', 'shared_prefix_text')} for e in examples], indent=2))
