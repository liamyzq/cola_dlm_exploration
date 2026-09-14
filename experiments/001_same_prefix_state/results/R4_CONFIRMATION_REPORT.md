# Independent F distribution confirmation

The fixed confirmation completed all **128 source-disjoint articles** at implementation
commit `3f63ae20394b6c612910ab4c04cc2e8c194973b6`. All four workers exited zero,
and the raw-token recomputation matches every paired-root endpoint. No source
was replaced. See [compact results](r4_confirmation_f_v1.json),
[locked execution plan](../R4_EXECUTION.md), and [job history](../../../jobs/jobs.jsonl).

## Primary result

The mean signed cross-split **H_token is -0.0000551285**, with a 95%
source-document bootstrap interval **[-0.0001395089, 0.0000295180]**.
The interval includes zero and is not degenerate. This independent cohort does
not establish a positive difference in the declared future token-position
probability observable. Negative finite-sample estimates are retained; they
do not imply negative population heterogeneity.

The estimator uses eight independent A and eight independent B noises per
candidate, paired across candidates within each split, over 32 future tokens.
For two candidates its population target is half the mean squared L2 distance
between their token-position probability vectors. Inference is conditional on
accepted pairs. It does not test every joint text distribution, longer horizons,
or other proposal settings, and it does not establish that emitted text is a
sufficient description of every future generation state.

## Native-candidate funnel

| Stage | Count |
| --- | ---: |
| Fixed attempted sources | 128 |
| Live anchors | 127 |
| Terminated at anchor | 1 |
| Strict accepted pairs | 93 |
| Reference-only fallbacks | 34 |
| Native proposal attempts | 1,520 |
| Same-token proposals | 349 |
| Same-token proposals rejected by KL | 256 |
| Raw or effective cache duplicates | 0 |
| Future trajectories, including fallbacks | 3,520 |

All 93 alternatives satisfy exact token equality, block symmetric KL <=0.01,
and maximum-position KL <=0.0025 at eta=0.03. Accepted block KL ranges from
3.3056573e-06 to 0.0057926078; the largest
position KL is 0.0023547988. Median latent displacement is
0.348084, and after BF16 conversion it is
0.350572. Feasibility remains strong in fresh sources.

The common-noise suffixes differ in 807/1488
paired realizations, with mean token-position disagreement
0.102025. This describes the coupling; it does
not contradict the zero-compatible independent distribution estimate.

## Cost and decision

Root construction and candidate search cost 2813.21
summed worker-seconds. Future generation plus native-state replay cost
11151.97 seconds. Total recorded per-root work is
13965.73 seconds (3.879 worker-hours).
Launch to the last terminal exit is 59.87 minutes
on four RTX A6000 GPUs. The wall measurement includes startup; per-root timing
starts after model loading. All failed proposals, reference fallbacks, and
post-EOS fixed-horizon model calls are retained. Detailed call counts are in JSON.

The fixed confirmation is complete. Do not extend it or retune eta/KL using its
result. The positive-mechanism trigger is not met, so the eight-root cache-path
diagnostic remains unactivated with zero diagnostic GPU trajectories. Natural
continuation has no task reward here; H1b/H2 and H3 require separate evidence.
The bounded eight-root Branch-M probe addresses the remaining development
headroom question without enlarging this confirmation or initiating training.
