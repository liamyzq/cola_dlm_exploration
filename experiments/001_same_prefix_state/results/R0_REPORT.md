# R0: saved-trajectory and answer-position audit

The CPU audit `001-r0-saved-routes-v2` completed at implementation commit `827285209957d870812bc4fe9b13f99345e2a2ab`. It reconstructed the original 256 graph tasks and checked all 1,024 saved generations against task data, decoded text, allocated lengths, and the unchanged P0 scorer. No new model sample was generated. [Full summary](r0_saved_routes_v2.json).

## Main observation

| Metric | Easy, 512 saved samples | Hard, 512 saved samples |
| --- | --- | --- |
| Original eligible F roots | 0 | 0 |
| Eligible roots at first causally evaluated F boundary | 0 | 0 |
| Eligible first M roots | 76 (14.84%) | 61 (11.91%) |
| No mixed layout because prompt is aligned | 40 | 64 |
| Terminated by M boundary | 188 | 140 |
| Wrong trunk at M boundary | 208 | 247 |
| Correct first directed edge in returned answer | 22 | 11 |
| Full route success | 0 | 0 |

M eligibility means the naturally emitted prefix remains compatible with the common trunk at the first mixed boundary. It can end inside the first town name. It does not mean a complete first edge, an accepted alternative latent, or a useful continuation. We have not reconstructed or tested M candidate states yet. F/M cannot be combined into one intervention-effect estimate.

The first causally evaluated F boundary is already terminated for 430 Easy and 337 Hard samples; the remaining 82 and 175 are wrong trunks. Classification prioritizes termination, so a terminated answer may also contain semantic errors. These categories do not identify a causal reason for failure.

## Static audit reproduction

All named static measurements in the supplied review reproduced: prompt lengths 386-470 / 278-392, generated allocation 80-110 in both, total positions 480-560 / 368-496, 47 / 0 graphs exceeding 512, no original boundary beyond 512, missing full layouts 10 / 7, earlier full layouts 13 / 19, and all three first successors still able to reach the waypoint on 81 / 104 graphs.

The review's context concern applies to late Easy continuations. It does not explain initial wrong edges, initial trunk failure, or Hard's zero success. The first-edge counts independently show that the released checkpoint does poorly on this long edge-following task.

Within the recorded horizons, 436 Easy and 352 Hard outputs reach an answer terminator; 436 and 350 continue generating additional tokens afterward. There are 35,031 and 27,800 generated tokens strictly after the first token containing the terminator. These are token counts, not saved compute: no early-stopping speedup was run. No terminated returned line forms a legal unfinished common trunk under the diagnostic rule. Do not relabel every terminated wrong answer as premature termination.

## Official capability input preparation

The pinned upstream checkout lacks the `generate_task_data` directory referenced by its benchmark shell script. Recover 128 inputs per task from its versioned `eval_output/tasks_default/{lambada,squad}.jsonl` fixtures, sorted by original ID. Discard published predictions before selection; keep prompt and gold answer. Reconstruct the removed common prefix and require exact equality with the official prompt template for every item.

This is a released-fixture capability subset, not the full original benchmark. [Selected IDs and position summary](r0_official_answer_positions_v1.json). The preparation code is `scripts/prepare_released_benchmarks.py`; raw prepared inputs and per-item spans are outside Git at `/home/mlw0719/cola_dlm_exploration_storage/datasets/001_released_capability_v1`.

Only 1/128 LAMBADA and 15/128 SQuAD gold answers cross the first mixed boundary under the natural space-prefixed answer tokenization. These are gold layout opportunities, not model-generated eligible roots. LAMBADA prompts range from 53 to 148 tokens. SQuAD prompts range from 133 to 522; five official 32-token allocated runs exceed 512 positions. Preserve the official prompts for capability checks and report that coverage; do not silently truncate them to match the separate route diagnostic envelope.

The pinned benchmark uses repetition penalty 1.1, while the current mechanism engine uses 1.0. R1 must implement and verify the actual official path, including its context-token handling. Existing parity evidence at penalty 1.0 remains evidence for that setting only.

## Interpretation and next action

The full-block route bottleneck persists under an earlier causal anchor. M provides a measurable set of potential natural roots without changing the task or training, which supports the planned M engineering extension. Natural-continuation F remains the route-independent primary feasibility input. H1a/H1b/H2/H3 are still unmeasured.

Proceed with official capability inference and paired wrapper parity, the bounded route diagnostic cells, and F/M candidate feasibility. Do not train LoRA or a selector. The small number of cross-boundary official answers prevents treating this fixed capability subset as a ready-made large H2 study.

The first audit attempt (`001-r0-saved-routes-v1`) stopped before statistics because Python tuples were compared directly with loaded JSON lists. The retry compares the ordinary serialized representation. Both the failure and successful retry are preserved in the job and experiment ledgers.

## Reproduction

From frozen worktree `/home/mlw0719/cola_dlm_exploration_storage/worktrees/001-r0-v2`:

```bash
bash scripts/compute/nebula/run.sh 5 scripts/audit_p0_routes.py --config configs/001_same_prefix_state/r0_saved_routes.json --output /path/to/new/audit_directory
```

The shared launcher sets device visibility, but this script performs CPU analysis only. The actual launch command, process ID, exit status, source paths, per-sample diagnostics, and complete configuration are retained under `/home/mlw0719/cola_dlm_exploration_storage/runs/001_same_prefix_state/001-r0-saved-routes-v2`.
