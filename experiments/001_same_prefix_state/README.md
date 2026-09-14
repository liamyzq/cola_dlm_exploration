# 001_same_prefix_state: Future information beyond emitted tokens

Status: P0 completed; revised no-training R-series plan adopted. No R-series GPU experiment has run yet.

Can naturally generated continuous states preserve exactly the same emitted tokens and closely preserve the decoder readout while changing future text distributions or task value? The released CoLa model remains frozen. The [active English protocol](PROTOCOL.md) separates H1a distribution effects, H1b task-value variation, H2 independent selection gain, and H3 equal-cost utility.

The [supplied P0 audit](reviews/P0_review_no_training_plan_v2.md) and [adoption record](reviews/ADOPTION.md) explain the redesign. The [original protocol](archive/PROTOCOL_P0_v1.md) is historical; its default training progression no longer governs new work. LoRA and selector training are outside the current plan.

## Established evidence

The 32-example native-parity, state-replay, and cache suite passed. Original route calibration produced zero successful answers and zero eligible roots on both difficulties, 512 generations each. These are task-capability/eligibility results; H1a/H1b/H2/H3 remain unmeasured. See [the P0 report](results/P0_REPORT.md), [experiment ledger](../results.tsv), and [job history](../../jobs/jobs.jsonl).

## Next work

R0 reuses full existing records for layout/termination diagnosis. R1 checks official LAMBADA/SQuAD capability; R2 decomposes route difficulty with a 256-generation ceiling. R3 tests same-text candidates independently of route competence. Full generated blocks (F) and first mixed blocks with fixed prompt latents (M) are separate cohorts. R4 measures and independently confirms future-distribution effects; R5 conditionally tests reward gain and training-free compute value.

The first milestone is a validated same-text pair and its acceptance/cost funnel. The study continues to supported independent confirmation and an evidence-based disposition of the remaining stages.

## Runtime

Source revision: `7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c`.
Checkpoint revision: `c1eafdd9cfd8064aeb917d569ef70a075b353eed`.

Use nebula GPUs 5-8 only. Primary files are in `/home/mlw0719/cola_dlm_exploration`; large artifacts are under `/home/mlw0719/cola_dlm_exploration_storage/runs/001_same_prefix_state/`. Formal runs use committed detached worktrees. GPT-5.6 Luna at max reasoning monitors long waits; the main agent owns implementation and scientific decisions.
