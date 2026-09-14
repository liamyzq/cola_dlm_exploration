# 002_task_consequence_basin: Task consequence and latent decoder geometry

Status: core study complete. P0, H1 random corruption and fixed-budget search, H2 real/rotated residuals, CFG7 and interpretation controls, predictive analyses, and the blinded assistant audit are complete. Both primary effects are near zero with nondegenerate intervals inside the declared +/-2 percentage-point band. No training or natural/native-generation extension was activated.

Read the [final report](results/FINAL_REPORT.md), [completion audit](reviews/CORE_COMPLETION_AUDIT.md), and [execution protocol](PROTOCOL.md). The original H1 report is retained as an interim parser-v1 record. Final evidence and PDF/PNG figures are under `results/final_v2/`.

This idea tests encoded-reference conditional reconstruction: for the same source, complete answer, and fixed one-token replacement, does changing the queried field change decoder protection? Does real denoising residual direction preferentially protect that field relative to matched channel rotations? Idea 001 remains a separate native same-prefix study.

Primary storage is `/home/mlw0719/cola_dlm_exploration_storage/runs/002_task_consequence_basin/`. All 36 formal jobs have observed successful terminal events. Original artifacts remain unchanged; `rescored-v2/` applies the audited parser uniformly and `analysis-v2/` contains the final analysis. The original 100-item audit sample was retained after repair. Manual labels were committed before unblinding.

## Reproduce the final analysis

Use the detached `002-scorer-v2` worktree at commit `52244c9` on nebula. The corrected record view already exists; its generating command and original-source paths are recorded in `results/final_v2/rescore_command.json` and `rescore_manifest.json`.

```bash
source scripts/compute/nebula/env.sh
"$COLA_PYTHON" -m scripts.run_task_basin_final_analysis \
  --run-base /home/mlw0719/cola_dlm_exploration_storage/runs/002_task_consequence_basin/rescored-v2 \
  --worlds /home/mlw0719/cola_dlm_exploration_storage/datasets/002_task_consequence_basin/v1/worlds.jsonl \
  --ledger /home/mlw0719/cola_dlm_exploration/jobs/jobs.jsonl \
  --output /home/mlw0719/cola_dlm_exploration_storage/runs/002_task_consequence_basin/analysis-v2
```

Retain the existing `analysis-v2/blind_audit_v1/` before rerunning: these are the frozen audited items, not a new sample to redraw. Full analysis commands are in `results/final_v2/analysis_commands.json`; three supplementary control commands are in `results/final_v2/control_analysis_commands.json`.

Decision: retain the shared measurement implementation and close this hypothesis test. A new CFG-support or native-task study needs a separately stated question; do not extend the same test until significance.
