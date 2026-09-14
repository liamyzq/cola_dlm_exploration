# Research Progress

## Current state

The revised no-training protocol governs idea 001. R0 and R1 are complete;
R2 is complete with only Copy succeeding (3/64). R3 reached 32 strict
native pairs in each F/M cohort. The F pilot is complete: H_token mean 0,
95% source interval [-0.000214,0.000244]. Independent confirmation is running on GPUs 5-8.
The pilot does not establish H1a; H1b/H2/H3 remain unmeasured. No model training has run.

## Evidence and interpretation

R1 official capability is 63/128 LAMBADA and 43/128 SQuAD with eight exact
paired inference/replay checks. R0 reproduced all 1,024 historical P0 records;
original routes had no success or eligible full-block roots. See the R0/R1 reports.

R2 Copy succeeds 3/64 with 59/64 correct first edges. Chain and Branch each
succeed 0/64 and provide no eligible F roots. No Branch sample reaches the
first branch after a correct trunk. These are task-capability limitations,
not evidence about H1a or the choice between branch arms. See the R2 report.

R3 locks eta=0.03 with exact tokens and epsilon=0.01. F uses 45 development
sources for 32 pairs; M uses 41 for 32. Calibration and collection have different
proposal caps, so coverage remains descriptive. Collection root/proposal work,
including failures, costs 848.07 s for F and 392.64 s for M; calibration and future
rollouts are additional. See the R3 report and the results ledger.

The M/F engineering suite passed all 16 prompt remainders. Candidate serialization
and reconstruction preserve caches and paired futures. The actual A/B runner
passed independent split noise, within-split pairing, and identity-null checks.
These validate execution without establishing a future-distribution effect.

## Active work and next decisions

All R2, R3 and pilot workers are terminal. The four confirmation workers are active
from frozen commit `3f63ae2`, under experiment `001-r4-confirmation-f-v1`. The pilot completed 512 futures on
32 source-disjoint development pairs. Although 156/256 paired suffixes differ,
the independent cross-split endpoint is centered at zero. See the pilot report.

Complete the active locked 128-source independent F confirmation with eight A/eight B
samples, preserving all failed roots and reference fallbacks. Do not top up by
outcomes or change the primary setting. The positive-effect cache-path diagnostic
is not activated by the pilot. Actual jobs and artifact paths are in jobs/jobs.jsonl;
GPT-5.6 Luna at max reasoning monitors long waits.

R5 remains conditional on suitable task-value evidence. Natural continuation has
no task reward here and cannot support a selection or inference-utility claim.
Keep route limitations and negative outcomes visible. The final report must give
an explicit disposition for every conditional stage. LoRA, learned selectors and
the original human-reviewed transfer study remain deferred outside this revision.
