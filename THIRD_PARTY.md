# Third-party source

The resumable engine follows the native inference algorithm in ByteDance-Seed/Cola-DLM at revision `7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c`, including its Euler arithmetic, CFG, prompt pinning, precision, and commit ordering. Copyright (c) 2025 ByteDance Ltd. and/or its affiliates. Its Apache 2.0 [license](LICENSES/Cola-DLM-LICENSE) and [notice](LICENSES/Cola-DLM-NOTICE) are retained here.

The official model modules and checkpoint remain outside this repository at the paths and pinned revisions in `COMPUTE.md`. The experiment adds explicit snapshots, replay, proposal filtering, task generation, and measurement around those modules.
