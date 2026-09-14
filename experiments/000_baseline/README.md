# 000_baseline: Shared released CoLa model

Status: frozen native inference and the revised capability/state checks are complete.

Use the official ByteDance-Seed/Cola-DLM source at `7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c` and checkpoint at `c1eafdd9cfd8064aeb917d569ef70a075b353eed`. Paths and dependencies are in [COMPUTE.md](../../COMPUTE.md).

The shared [state engine](../../src/models/cola_state.py) imports the pinned upstream model modules with all weights frozen. It uses fp32 master weights and bf16 autocast, the native 16-step Euler sampler, CFG 7, greedy decoding, repetition penalty 1, 16-position DiT blocks, and latent dimension 16. The released VAE has patch size 1 and its own causal block size 1; this differs from the DiT generation block size.

The 32-example `001-p0-engineering-v1` suite passed exact official token parity, pause/resume, identity replay, chronological cache reconstruction, AB/BA proposal ordering, unchanged historical tokens, and paired future noise. Identity-replay KL was zero. These checks establish engine behavior, not task accuracy or latent-state value.

[Idea 001](../001_same_prefix_state/README.md) completes the original route calibrations and the revised no-training study. [Official capability controls](../001_same_prefix_state/results/R1_REPORT.md) record 63/128 LAMBADA and 43/128 SQuAD, with repetition penalty 1.1 as required by those pinned official conditions. The mechanism experiments use penalty 1. The added M/F suite passes all 16 prompt remainders. Route capability remains weak; see the [final evidence summary](../001_same_prefix_state/results/FINAL_REPORT.md). Later ideas should reuse compatible baseline experiment IDs from [the result ledger](../results.tsv), matching their data, evaluator, and budget. No adapted checkpoint has been trained.
