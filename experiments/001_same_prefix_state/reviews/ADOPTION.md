# P0 audit adoption

Received and adopted on 2026-09-14 UTC. The user's direct request was to read the audit, transfer it, incorporate it into documentation, change the plan, and restart the goal. The review's imperative wording is advisory source material; adoption follows that user request. It is not evidence that its proposed experiments have run.

## Sources and provenance

- [English review, verbatim](P0_review_no_training_plan_v2.md), supplied as `P0_review_no_training_plan_v2.md`, reviewing project commit `943b8f55c6112b654ec5b967bdffe2cea36f70f4`.
- The accompanying Chinese text explains the same revision and requests bounded root attempts, conditional reward analysis, and removal of automatic training. Its substantive additions are incorporated in the English active protocol.
- [Historical P0 protocol](../archive/PROTOCOL_P0_v1.md), copied from the reviewed commit without edits.
- [Completed P0 report](../results/P0_REPORT.md): project measurements, distinct from the review's new static reconstruction.

The English review is retained as supplied, including external citations. Its static counts have not yet been independently rerun in this execution phase. Its descriptions of published scores and paper sections require pinned-source verification when implementing R1/M. Do not append proposed experiments or unverified review counts to the model-result ledger.

## Adopted changes

The [active protocol](../PROTOCOL.md) supersedes the old P0-P5 progression for new work. It removes LoRA and learned selectors from the current scope; adds H1a while retaining the reward H1 as H1b; separates F and M; starts with K=2; keeps strict epsilon=0.01 and exact token equality; replaces universal capability gates with coverage, conditional reward, and cost reports; and follows R0-R5 with independent confirmation and uncertainty-based stopping.

The next operational objective is to obtain validated same-text native state pairs and measure acceptance, future effects, and cost, then complete the supported bounded confirmation stages. One successful pair is a milestone, not sufficient completion of the overall study. There is no requirement to prove a positive result.

## Execution clarifications

The English audit and accompanying Chinese summary label confirmation stages slightly differently. The active protocol uses R4 for the mechanism pilot and independent 128-root distribution confirmation; R5 denotes conditional task-value confirmation and the optional cost study. This preserves the scientific order and avoids treating the same confirmation as two runs.

The R3 root cap is explicit per named cohort: at most 128 attempts for up to 32 pairs, with at most F and M. R4 runs one primary setting selected on development data. Confirmation starts with 128 fixed source roots; exclusions are reported rather than replaced after observing outcomes. No stage may silently expand to fill favorable results.

The original 32-example engine evidence remains valid for its tested path. M, the H_token statistic, and the complete candidate runner need their own targeted validation. Existing untracked P0 candidate-runner/config drafts remain unvalidated and must not be launched as the revised R-series implementation.

## Subsequent execution evidence

The adoption-time pending checks above are now resolved: [R0](../results/R0_REPORT.md)
reproduced the saved outputs and static layout counts, and [R1](../results/R1_REPORT.md)
validated the pinned official inference paths and recorded the bounded capability
subset. Those reports contain project measurements; the supplied review remains
unchanged as historical source material.

## Closing review of 4922a00

The user's [final review](FINAL_REVIEW_4922a00.md), recorded in English, endorses
closure of the current execution scheme and continued no-training. Its reporting
clarifications are adopted in FINAL_REPORT.md, the R4/R5 reports, and PROGRESS.md:
candidate feasibility is positive; R4 is a completed conditional measurement on
93 pairs/128 attempts with no positive support; R5 weakly constrains H1b/H2 at a
task floor; H3 is unmeasured. F and M evidence are explicitly separated, and
closure is a budget decision rather than proof of universal zero benefit.

No implementation, configuration, numerical result, job event, or experimental
outcome is changed by this audit update. No further GPU or offline analysis is
launched. The optional saved-continuation analysis remains an exploratory future
suggestion requiring a stated hypothesis, not a reopening of this study.
