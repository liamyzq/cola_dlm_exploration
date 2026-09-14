# Third-party source

The resumable engine follows the native inference algorithm in ByteDance-Seed/Cola-DLM at revision `7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c`, including its Euler arithmetic, CFG, prompt pinning, precision, and commit ordering. Copyright (c) 2025 ByteDance Ltd. and/or its affiliates. Its Apache 2.0 [license](LICENSES/Cola-DLM-LICENSE) and [notice](LICENSES/Cola-DLM-NOTICE) are retained here.

The official model modules and checkpoint remain outside this repository at the paths and pinned revisions in `COMPUTE.md`. The experiment adds explicit snapshots, replay, proposal filtering, task generation, and measurement around those modules.

## Natural passage corpus

The natural-continuation input preparation uses article contexts from SQuAD 1.1, distributed by the [Stanford SQuAD project](https://rajpurkar.github.io/SQuAD-explorer/) under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The pinned dataset source is `rajpurkar/SQuAD-explorer` revision `eee5fdbf62f8613a7812b03419e6b29617b74fd1`, `dataset/train-v1.1.json`. Article titles and paragraph indices are preserved as provenance; prefixes are cropped at word boundaries. The raw dataset and prepared text remain in nebula storage outside Git. Questions and gold answers are not used in this continuation study, and no training or official SQuAD accuracy claim is implied.
