# 002_task_consequence_basin: Task consequence and latent decoder geometry

Status: P0, H1 random corruption, fixed-budget search, and the four interpretation controls are complete. H1 shows no positive primary protection signal; the output audit is pending. H2 is frozen at lambda_star=0.5 and the full CFG1 test plus CFG7 control are running under monitor-subagent supervision. See [H1 readout](results/H1_REPORT.md) and [H2 calibration](results/P2_CALIBRATION.md).

For the same source, complete answer, and fixed one-token replacement, does changing which field the question asks about change decoder protection? Does real denoising residual direction protect the currently critical field more than matched random channel rotations?

The [execution protocol](PROTOCOL.md) implements the user-supplied proposal. The user subsequently supplied `task_consequence_basin_experiment_protocol_v1.md`; its exact templates, name pool and search settings govern this execution. The English execution protocol records implementation choices and departures.

Use the pinned shared official model and existing nebula launcher. The first idea's native same-prefix intervention remains a separate completed study; these are encoded-reference conditional reconstruction experiments.

Records use the shared experiment and job ledgers. Compact reports belong in `results/`; raw outputs belong under `/home/mlw0719/cola_dlm_exploration_storage/runs/002_task_consequence_basin/`.

## Continue after H2 completion

The two live groups are `002-p2-test-recovery-v1-gpu5` through `gpu8` (64 worlds / 20,480 readouts each) and `002-p2-cfg7-control-v1-gpu5` through `gpu8` (16 worlds / 5,120 readouts each). Their frozen implementation is `a23ab19f66ee33a5b6a93fb68d3fc2bf97ff0e90`; do not edit their worktree.

From a committed analysis checkout on nebula:

```bash
source scripts/compute/nebula/env.sh
"$COLA_PYTHON" -m scripts.run_task_basin_final_analysis \
  --run-base /home/mlw0719/cola_dlm_exploration_storage/runs/002_task_consequence_basin \
  --worlds /home/mlw0719/cola_dlm_exploration_storage/datasets/002_task_consequence_basin/v1/worlds.jsonl \
  --ledger /home/mlw0719/cola_dlm_exploration/jobs/jobs.jsonl \
  --output /home/mlw0719/cola_dlm_exploration_storage/runs/002_task_consequence_basin/analysis-v1
```

The entry point refuses incomplete worker artifacts, records analysis commands, and creates the 100-item blinded output sample. Review `blind_items.jsonl` without reading `audit_key.jsonl`; record field statuses and whole-fact correctness before comparing labels. An assistant audit must be labeled as such, not as a human study. If scoring changes, retain original scores and uniformly rescore all methods and outputs. Final interpretation and visual inspection are still required.
