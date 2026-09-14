# 000_baseline: Shared CoLA / Continuous DLM Baseline

Status: awaiting source and protocol selection.

This directory establishes the shared comparator used by future idea directories. No baseline implementation, executable configuration, or result exists yet.

Identify the exact paper and official source, upstream revision, checkpoint, tokenizer, data split, evaluator, primary metric, and compute budget before choosing the first formal run. Record the protocol here and implement common code under `src/`. Place executable configurations under `configs/000_baseline/` once the upstream configuration format is known.

The first remote smoke run should establish whether the selected model loads and the relevant evaluation path produces a metric. Its success alone is not a baseline result. Formal baseline runs must use committed code and configurations, a frozen worktree, and outputs under `/home/mlw0719/cola_dlm_exploration_storage/runs/000_baseline/`.

Subsequent ideas should link to compatible baseline experiment IDs in [the result ledger](../results.tsv). Reuse a baseline only when its data, evaluator, and budget remain suitable for the comparison.
