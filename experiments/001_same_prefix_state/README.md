# 001_same_prefix_state: Future value beyond the emitted prefix

Status: P0 implementation and capability calibration.

Does the emitted token prefix adequately describe CoLa's continuation state? With all model weights frozen, use native block resampling to find latent alternatives that preserve the exact emitted tokens and closely preserve the decoder distribution. Test reproducible future-value differences, independent selection gains, and compute value in that order.

The [English protocol](PROTOCOL.md) preserves the supplied experimental plan, including its conditional progression from P0 through P5. The base model is the official ByteDance-Seed/Cola-DLM release. No experimental evidence has been collected yet.

Source revision: `7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c`.
Checkpoint revision: `c1eafdd9cfd8064aeb917d569ef70a075b353eed`.

Use nebula physical GPU indices 5, 6, 7, and 8 only. Long-running monitoring belongs to a GPT-5.6 Luna subagent at max reasoning, with bounded status checks and terminal or actionable reports. The main agent owns implementation acceptance, scientific analysis, and conclusions.

Run records will link the [experiment ledger](../results.tsv), [job history](../../jobs/jobs.jsonl), committed configurations, and artifacts under `/home/mlw0719/cola_dlm_exploration_storage/runs/001_same_prefix_state/`.
