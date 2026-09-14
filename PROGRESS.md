# Research Progress

## Current state

The [revised no-training protocol](experiments/001_same_prefix_state/PROTOCOL.md) governs idea 001. R0 has completed the full saved-output audit and prepared fixed official capability inputs; see [R0 report](experiments/001_same_prefix_state/results/R0_REPORT.md). No R-series GPU generation or training has run. H1a/H1b/H2/H3 are unmeasured.

The unchanged engine has 32 passing engineering examples at penalty 1.0. P0-v2 still has zero successful routes and zero eligible original full-block roots in both 512-sample difficulties. All submitted P0 and R0 workers are terminal; no equivalent job remains active.

## Observation, inference, and decision

R0 reproduces the supplied audit's static counts and the original scores on all 1,024 saved generations. Earlier causal full-block selection gives no eligible roots. The first mixed block yields 76/512 Easy and 61/512 Hard compatible live prefixes. These may end inside a town name and are not yet candidate pairs. Correct first edges occur in only 22 and 11 returned answers.

Decision: validate M with fixed known prompt latents and test route-independent F natural continuation. Do not make long-route competence a prerequisite for state feasibility. Keep strict token/KL constraints, independent A/B, and consistent caches. Do not train LoRA or a learned selector.

Official data preparation recovers 128 fixed items per task from pinned released evaluation fixtures, excluding published predictions from selection. All prompts match official templates. Only 1 LAMBADA and 15 SQuAD gold answers cross M, so these subsets are capability controls rather than a large ready-made H2 set. Official repetition penalty is 1.1; current engine default is 1.0, requiring an explicit paired R1 path.

## Next actions

1. Complete official R1 inference and targeted wrapper parity, preserving effective penalty, special-token stopping, prompts, and official extraction.
2. Implement and validate M and H_token, prepare source-document F continuation inputs, and run bounded R2/R3 diagnostics and feasibility.
3. Lock one setting from development evidence for R4 pilot and independent distribution confirmation. Run R5 only when conditional task value warrants it; report skipped or inconclusive stages explicitly.

The first milestone is a validated native same-text pair with independent futures and measured acceptance/cost. Completion still requires the supported revised experiments and an evidence-based final report. Original selector training and human-reviewed transfer are deferred, not completed. Existing untracked P0 proposal-runner/config drafts are unvalidated and must not be launched as the R-series implementation.
