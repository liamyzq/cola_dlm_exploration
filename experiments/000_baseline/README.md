# 000_baseline: Shared released CoLa model

Status: native inference integrated; route-task capability calibration is running.

Use the official ByteDance-Seed/Cola-DLM source at `7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c` and checkpoint at `c1eafdd9cfd8064aeb917d569ef70a075b353eed`. Paths and dependencies are in [COMPUTE.md](../../COMPUTE.md).

The shared [state engine](../../src/models/cola_state.py) imports the pinned upstream model modules with all weights frozen. It uses fp32 master weights and bf16 autocast, the native 16-step Euler sampler, CFG 7, greedy decoding, repetition penalty 1, 16-position DiT blocks, and latent dimension 16. The released VAE has patch size 1 and its own causal block size 1; this differs from the DiT generation block size.

The 32-example `001-p0-engineering-v1` suite passed exact official token parity, pause/resume, identity replay, chronological cache reconstruction, AB/BA proposal ordering, unchanged historical tokens, and paired future noise. Identity-replay KL was zero. These checks establish engine behavior, not task accuracy or latent-state value.

[Idea 001](../001_same_prefix_state/README.md) runs two predefined directed-route capability calibrations before using this checkpoint as a scientific comparator. Later ideas should reuse compatible baseline experiment IDs from [the result ledger](../results.tsv), matching their data, evaluator, and budget. No adapted checkpoint has been trained.
