# 001_same_prefix_state: Future information beyond emitted tokens

Status: the adopted no-training study is complete. Candidate feasibility is established; the measured F distribution effect has no positive support, while M task value remains weakly constrained by a reward floor. See the [final report](results/FINAL_REPORT.md).

Can naturally generated continuous states preserve exactly the same emitted tokens and closely preserve the decoder readout while changing future text distributions or task value? The released CoLa model remains frozen. The [active English protocol](PROTOCOL.md) separates H1a distribution effects, H1b task-value variation, H2 independent selection gain, and H3 equal-cost utility.

The [supplied P0 audit](reviews/P0_review_no_training_plan_v2.md) and [adoption record](reviews/ADOPTION.md) explain the redesign. The [original protocol](archive/PROTOCOL_P0_v1.md) is historical; its default training progression no longer governs new work. LoRA and selector training are outside the current plan.

## Evidence and reusable implementation

- [R0 saved-route audit](results/R0_REPORT.md) reproduces all 1,024 historical records and separates possible M anchors from causal F eligibility. [P0 outcomes](results/P0_REPORT.md) remain available.
- [R1 capability](results/R1_REPORT.md) records 63/128 LAMBADA and 43/128 SQuAD successes under pinned official conditions, with eight exact paired inference and replay checks.
- [R2 route diagnosis](results/R2_REPORT.md) records 3/64 Copy successes and zero successes in Chain, Branch, and Matched-full. Branch's short common trunk also lacks a canonical predecision F layout.
- [R3 feasibility](results/R3_REPORT.md) establishes 32 strict native pairs in each F/M cohort at eta=0.03 and epsilon=0.01. [Raw same-prefix examples](results/SAME_PREFIX_EXAMPLES.md) retain token IDs, latent displacement, KL, and artifact paths.
- [R4 pilot](results/R4_PILOT_REPORT.md) and [independent confirmation](results/R4_CONFIRMATION_REPORT.md) both have zero-compatible H_token intervals. Confirmation yields 93 accepted pairs from 128 fixed sources. Coupled suffix differences alone do not establish a distribution difference.

The native-parity and cache-replay suite passed all 32 original examples. The M/F suite passed all 16 prompt remainders, and the A/B runner passed pairing, independence, and identity-null checks. These are execution results; scientific claims use the substantive studies above.

## Final stage decisions

The [independent F confirmation](results/R4_CONFIRMATION_REPORT.md) has a zero-compatible H_token interval. The [bounded Branch-M probe](results/R5_PROBE_REPORT.md) completes all eight roots with zero successful reference or alternative futures. Cache localization, large reward confirmation, and the equal-cost study are not activated. LoRA, learned selectors, and the original transfer study remain outside the adopted scope.

Keep the shared state engine and strict candidate machinery. The [closing audit](reviews/FINAL_REVIEW_4922a00.md) records a budget-based stop of the current proposal, observable, and route setting. Retire this route family from the main value measurement; do not expand its reward floor. The [final report](results/FINAL_REPORT.md) separates feasibility, H1a, H1b/H2, and unmeasured H3, including intervals and explicit stopping decisions. Full facts and provenance remain in [the experiment ledger](../results.tsv) and [job history](../../jobs/jobs.jsonl).

## Runtime

Source revision: `7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c`.
Checkpoint revision: `c1eafdd9cfd8064aeb917d569ef70a075b353eed`.

Use nebula GPUs 5-8 only. Primary files are in `/home/mlw0719/cola_dlm_exploration`; large artifacts are under `/home/mlw0719/cola_dlm_exploration_storage/runs/001_same_prefix_state/`. Formal runs use committed detached worktrees. GPT-5.6 Luna at max reasoning monitors long waits; the main agent owns implementation and scientific decisions.
