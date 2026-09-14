# Research Progress

## Current state

R1 capability completed: LAMBADA 63/128 (49.22%), SQuAD 43/128 (33.59%) on fixed released fixtures using pinned official inference/scoring. All eight paired token/replay checks and the default-penalty control passed. See [R1 report](experiments/001_same_prefix_state/results/R1_REPORT.md).

R0 reproduced the static audit and all 1,024 P0 scores. Earlier F route roots remain unavailable; M has 76 Easy and 61 Hard compatible prefixes. Original route success remains zero. See [R0 report](experiments/001_same_prefix_state/results/R0_REPORT.md). H1a/H1b/H2/H3 are still unmeasured in formal experiments. Strict native pairs now exist: eta calibration accepted five F and six M roots at eta0.03.

## Observation and decision

The released checkpoint works on the official task formats; long-route failure is not evidence that the checkpoint is generally unusable. Continue route-independent F and separately validated M. Keep model weights frozen, exact emitted IDs, strict initial KL, independent A/B, and consistent caches. No LoRA or learned selector is in scope.

The H1a kernel passed explicit-feature, signed-split, identity, EOS, and source-cluster checks. Natural continuation inputs now contain 128 development and 128 confirmation articles, disjoint by source document. These are engineering/data preparation outcomes, not measured state effects.

## Active work and next actions

The 16-case M/F engineering suite `001-r3-m-engineering-v1` completed successfully on GPUs 6-8 from commit `7e757d8`. All prompt remainders 0..15 passed. Eight cases yielded accepted alternatives; this engineering sample does not estimate natural-passage coverage. R1 and M workers are terminal. Candidate-artifact replay passed for F and M. Reward-blind eta calibration completed; both cohorts lock eta0.03. Primary distribution measurement is F, following the full-generated-block priority; M remains a separate feasibility cohort. R2 Copy/Chain/Branch are active on GPUs5/6/8; ordered F collection is active on GPU7. The A/B runner smoke passed, including explicit noise pairing/isolation and identity null. M collection and R2 Matched-full await a free permitted GPU. The independent A/B runner and bounded R2 task diagnosis are implemented for targeted validation.

1. Complete M validation, then freeze and run R3 native candidate feasibility on natural passages. Implement the complete R4 continuation runner with explicit independent A/B noise and full cost records.
2. Run the bounded R2 Copy/Chain/Branch/Matched-full diagnosis, keeping route and natural-continuation results separate.
3. Lock the primary setting for R4 pilot and independent confirmation; run R5 only when conditional task-value evidence warrants it.

The goal remains active. One same-text pair is a milestone, not completion. Finish the supported revised experiments and record a clear disposition for every conditional stage; training and the original human-reviewed transfer study remain deferred. The old untracked P0 proposal-runner/config drafts are not the R-series implementation.


## R2 diagnostic update

Copy succeeded 3/64 with 59/64 correct first edges; Chain and Branch both
succeeded 0/64 and yielded no eligible F roots. No Branch sample reached its
first branch after a correct trunk. Matched-full is running; native task-value
claims remain unsupported. See the R2 report for scope and termination costs.
The first 16 F pairs are frozen for pilot part1 on an available GPU; effect
outputs remain unread until ordered F collection is terminal. Both pilot parts
share one setting and a combined 512-future cap.
