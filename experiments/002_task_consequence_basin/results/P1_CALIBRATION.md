# P1 development calibration and H1 test freeze

The 64-world development cohort has 64/64 paired-clean worlds. The original ten-scale grid completed all 10,240 readouts at `d4a4b0a`, but its lexical disagreement jumps from 2.009% at sigma 0.32 to 43.794% at 0.64. No original point meets the prescribed 3%-25% measurement range. Preserve this calibration failure; it is not evidence for or against task-role protection.

The single allowed global development refinement adds seven scales from 0.36 to 0.60, using the same worlds and paired seeds. All 7,168 additional readouts complete at `7f5315d`. Reusing the original records, the union selects **sigma_star = 0.4**, whose 8.181% token disagreement is nearest 10%. Selection does not use role effects. See the [initial grid](p1_calibration_v1.json) and [refined selection](p1_calibration_v2.json).

Freeze 256 test worlds, 16 paired seeds, and scales 0.2, 0.4, 0.8, 1.6, with the primary H1 endpoint at 0.4. Keep the predetermined search and control subsets. No test model output informed these choices. The initial grid and refinement are development evidence, not confirmation.

At sigma 0.4, 54.30% of development query outputs have at least one damaged field, and 25.49% of fields are unparseable. The main analysis therefore reports valid-wrong and unparseable outcomes separately. It must not call every damaged field an incorrect parsed value.

The original workers use GPUs 5-8 and each complete 2,560 records in 32.5-45.2 seconds. Refinement workers use GPUs 7-8. Raw outputs and exact manifests are under `/home/mlw0719/cola_dlm_exploration_storage/runs/002_task_consequence_basin/002-p1-dev-noise-v1-gpu*/` and `002-p1-dev-noise-refinement-v1-gpu*/`.
