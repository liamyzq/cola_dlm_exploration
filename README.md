# CoLA and Continuous DLM Exploration

This repository explores CoLA DLM and related continuous diffusion language models. The released CoLa checkpoint is integrated through a resumable state engine using pinned official modules. Shared capability controls and exact state-replay checks support idea-specific experiments. Idea 001 studies native continuous states that preserve emitted text, under the adopted no-training protocol. See [the current research state](PROGRESS.md) for results and active work.

## Workspace

The primary checkout is `nebula:/home/mlw0719/cola_dlm_exploration`. The local Codex checkout is a lightweight mirror for planning and editing. Synchronize tracked work through [GitHub](https://github.com/liamyzq/cola_dlm_exploration); store datasets, checkpoints, and large outputs on nebula outside Git. See [COMPUTE.md](COMPUTE.md) for paths and machine procedures.

```text
src/
  models/                 Shared model implementations and upstream integration
  training/               Shared training and evaluation flows
  methods/                Composable method modules used by individual ideas
configs/                  Baseline, idea, and complete formal-run configurations
experiments/
  000_baseline/           Shared baseline establishment
  <idea_id>/              One persistent research idea per directory
  results.tsv             Repository-wide formal experiment ledger
scripts/                  Reusable commands once their execution path is established
jobs/jobs.jsonl           Observed job events
docs/idea-template.md     Starting point for an idea README
```

Each directory under `experiments/` is an independent research unit; `000_baseline` establishes the common comparator. Infrastructure directories serve all ideas. New ideas reuse the model and training implementation, select methods through configuration, and retain their own hypothesis, commands, evidence links, and conclusions. Do not copy the full model or training tree for each idea.

Use short-lived development branches for code changes. After baseline integration, `main` should retain the runnable baseline and accepted methods. Use separate worktrees for concurrently edited versions and detached worktrees at committed revisions for formal runs. See [the workflow](docs/workflow.md).

## Research records

- [PROGRESS.md](PROGRESS.md): current understanding, unresolved questions, and next actions.
- [experiments/results.tsv](experiments/results.tsv): formal experimental facts and decisions.
- [COMPUTE.md](COMPUTE.md): storage and compute procedures.
- [jobs/jobs.jsonl](jobs/jobs.jsonl): actual submissions and terminal events on nebula.
- [AGENTS.md](AGENTS.md): persistent project instructions, informed by `research-repo` and `ccf-humanization`.

The first idea is [future value beyond the emitted prefix](experiments/001_same_prefix_state/README.md). Its [English protocol](experiments/001_same_prefix_state/PROTOCOL.md) specifies R0-R5: bounded capability diagnosis, native same-token F/M cohorts, independent distribution and value measurement, and a conditional training-free cost study. LoRA and learned selectors are outside the current plan. The [completed study report](experiments/001_same_prefix_state/results/FINAL_REPORT.md) establishes native same-text feasibility, records zero-compatible distribution evidence and a task-reward floor, and explains why larger selection and utility stages were not activated.
