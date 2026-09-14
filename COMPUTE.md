# Compute and Storage

## Primary workspace

Use the existing local SSH alias `nebula`. At initialization it resolves to `mlw0719@nebula.osl.northwestern.edu` through `quest`. SSH connectivity and GitHub access over SSH were observed on 2026-09-14 UTC. Keep authentication in the user's existing SSH setup, outside this repository.

| Purpose | Absolute path on nebula |
| --- | --- |
| Primary Git checkout | `/home/mlw0719/cola_dlm_exploration` |
| Storage base outside Git | `/home/mlw0719/cola_dlm_exploration_storage` |
| Datasets | `/home/mlw0719/cola_dlm_exploration_storage/datasets` |
| Checkpoints | `/home/mlw0719/cola_dlm_exploration_storage/checkpoints` |
| Run outputs | `/home/mlw0719/cola_dlm_exploration_storage/runs/<idea_id>/<experiment_id>` |
| Development and frozen run worktrees | `/home/mlw0719/cola_dlm_exploration_storage/worktrees` |

The local mirror is `/Users/liamye/Documents/ChatGPT/dlm_exploration`. Move tracked work between checkouts through Git. Do not synchronize data or run directories into the local checkout.

```bash
ssh nebula
cd /home/mlw0719/cola_dlm_exploration
git status --short --branch
git pull --ff-only
```

Before downloading large assets, check the required space against current availability; a setup-time capacity reading is not a reservation. Backup and retention guarantees for this home filesystem have not been established.

## Execution state

`git` and `python3` are available in the noninteractive SSH shell. `sbatch` was not found on that shell's PATH. GPU availability, allocation policy, model dependencies, and the training environment have not been established. This setup session launches no training or evaluation jobs.

Before the first compute run, establish the project's environment, appropriate GPU or scheduler access, and budget, then document the exact working launch procedure here and in `scripts/`. Do not train on a scheduler login node. Prefer nebula for representative smoke tests when its environment is ready.

Before an expensive run, read the job ledger and resolve any possibly equivalent active job, verify the chosen implementation commit, and allocate a unique output directory. Use the established launcher once one exists. Record actual job IDs or PIDs and observed state changes; never create placeholder job events.

## Run artifacts

Each formal output directory retains the resolved configuration, exact launch command, Git commit, seed, logs, metrics, and checkpoint locations needed to interpret or reproduce that run. Checkpoints may live in the shared checkpoint directory if the run records the exact path. Record any upstream source revision, checkpoint revision, or evaluator identity not determined by this repository's commit. A configured path alone does not identify changing external assets.

Frozen worktree creation and synchronization procedures are in [docs/workflow.md](docs/workflow.md). Keep a run worktree unchanged while the run is active.

## Known access behavior

Local HTTPS GitHub access failed because no HTTPS credentials were available in the shell. The existing SSH authentication successfully accessed this repository from both the local machine and nebula. Use `git@github.com:liamyzq/cola_dlm_exploration.git`; no credential changes are needed.
