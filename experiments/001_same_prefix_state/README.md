# 001_same_prefix_state: Future value beyond the emitted prefix

Status: P0 implementation and capability calibration.

Does the emitted token prefix adequately describe CoLa's continuation state? With all model weights frozen, use native block resampling to find latent alternatives that preserve the exact emitted tokens and closely preserve the decoder distribution. Test reproducible future-value differences, independent selection gains, and compute value in that order.

The [English protocol](PROTOCOL.md) preserves the supplied experimental plan, including its conditional progression from P0 through P5. The base model is the official ByteDance-Seed/Cola-DLM release. No experimental evidence has been collected yet.

Source revision: `7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c`.
Checkpoint revision: `c1eafdd9cfd8064aeb917d569ef70a075b353eed`.

Use nebula physical GPU indices 5, 6, 7, and 8 only. Long-running monitoring belongs to a GPT-5.6 Luna subagent at max reasoning, with bounded status checks and terminal or actionable reports. The main agent owns implementation acceptance, scientific analysis, and conclusions.

Run records will link the [experiment ledger](../results.tsv), [job history](../../jobs/jobs.jsonl), committed configurations, and artifacts under `/home/mlw0719/cola_dlm_exploration_storage/runs/001_same_prefix_state/`.

## Initial engineering evidence

One GPU 5 smoke example passed exact token parity with official inference, pause/resume, identity replay (zero numerical KL), chronological cache reconstruction, read-only proposal history, AB/BA order independence, unchanged past tokens, and paired future noise. The route generator/scorer passed a 128-graph check of common trunks, multiple successful routes, and legal unsuccessful routes. Split-statistic checks cover future-split leakage, reference-first ties, signed heterogeneity, and single-candidate fallback. These establish implementation behavior, not H1-H3.

The 32-example engineering suite passed in full at commit f9ecd7f. The two 128-graph/four-sample calibration configurations are the next P0 runs. Calibration uses a one-line answer termination policy: the emitted answer ends at the first newline after nonempty output. Fixed-horizon generation is retained for uniform cost accounting; raw generated text is saved, and text after the answer terminator is not part of the returned answer. The full answer line must parse as a single route. This policy is fixed before observing calibration rewards.

The planned intervention boundary is computed before sampling from the official tokenization of the demonstrated common-trunk format. Eligibility validates the actually emitted prefix against the graph's trunk, allowing the route separators accepted by the public scorer. A root that has already crossed the first branch at that boundary is ineligible. This avoids conditioning boundary selection on future output or reward. Exact candidate token equality is unchanged. For alternate spacing, this is a fixed conservative boundary rather than a retrospectively selected last boundary; report any resulting branch-crossing exclusions.

Before reward calibration, tokenizer checks showed that single-letter names with a 7-10-town trunk often leave no complete generated block after the partial prompt block (2/16 engineering-format examples). The route generator therefore uses meaningful two-word town names and a 10-12-town trunk, keeping 17-22 total towns. This adds actual route content rather than filler. The revised task/scorer passed 128 structural examples and 14/16 tokenizer boundary examples. Calibration configuration IDs advance to v2; no v1 reward calibration was run.

## Prespecified interpretation of the mechanism stages

The primary constraint remains epsilon=0.01. Sensitivity conditions are descriptive and cannot replace the primary result. Provided capability and candidate-coverage gates pass, P2 independently confirms the mechanism even if the small pilot is noisy. Train a value head only when the independently evaluated P2 gain has a 95% graph-bootstrap interval wholly above zero. Use a three-percentage-point practical improvement target when assessing precision; an interval spanning both zero and meaningful gains remains inconclusive. Do not call a failed route capability gate evidence that same-prefix latent states are equivalent.
