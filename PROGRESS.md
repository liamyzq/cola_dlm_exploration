# Research Progress

## Active idea 002: task consequence and decoder geometry

P0 and the frozen H1 core have completed. All 256 H1 worlds reconstruct under both questions. At development-selected sigma=0.4, protection is -0.049 percentage points (95% world interval [-0.208,0.122]); there is no positive role-protection signal. The primary interval is nondegenerate, while the highest-noise endpoint and search success curves saturate. All 512 prescribed search targets are found within RMS0.4 using the fixed 73,728-backward-step budget. These remain initial parser-version results pending the planned 100-output blinded audit. See [H1 readout](experiments/002_task_consequence_basin/results/H1_REPORT.md).

No-question identical-input labels cancel exactly. Source removal and sentence format show only small supplementary role differences. Zero/high-noise answer-latent replacement with source retained recovers 0/2,304 fields; source-only decoder repair is unsupported by this diagnostic. Confidence adjustment adds no macro probability-score improvement from task role. Keep the completed measurement evidence without increasing H1 sample size or changing its working point.

H2 development completes 64 paired-clean worlds. Lexical-only selection fixes lambda_star=0.5 (15.205% token disagreement), with a nondegenerate field-error interval. The full 256-world CFG1 recovery study and 64-world CFG7 control are running from immutable commit `a23ab19`, worktree `002-h2-v1`, on permitted GPUs 5-8. All eight workers have written records. The monitor subagent owns long waits; actual PIDs and terminal events are in `jobs/jobs.jsonl`. H2 outcomes have not been interpreted.

Next: after both H2 groups complete, run `scripts/run_task_basin_final_analysis.py` against the completed run base, inspect the blinded 100-output sample before its key, resolve any parser discrepancy uniformly, render and inspect final figures, and write the bounded core report. Clean geometry features are complete for 128 worlds; the grouped auxiliary model is fixed. A reproducible final-analysis command is recorded in the idea README. Natural SQuAD and LoRA remain unactivated extensions.

## Completed idea 001

## Current state and decision

Idea 001's current execution scheme is formally closed; the no-training decision
remains in force. Candidate feasibility is an established positive result, and
the core F distribution observable has completed independent measurement.
R4 provides no positive support under the declared setting. R5 remains weakly
informative because the route task has an all-zero reward floor; H3 is unmeasured.

Stopping is a research-budget decision: the current proposal, observable, and
route setting lack enough positive evidence to justify further investment.
This supersedes the original P0 limitation of having no qualified starting
points; it does not assert that nothing was measured or every possible gain is
zero. See the [final report](experiments/001_same_prefix_state/results/FINAL_REPORT.md)
and [closing audit](experiments/001_same_prefix_state/reviews/FINAL_REVIEW_4922a00.md).

## Established evidence

R1 records 63/128 LAMBADA and 43/128 SQuAD successes under pinned official
conditions, with eight exact paired inference/replay checks. The original
32-example state suite and all 16 M/F prompt remainders pass. These validate
execution; they do not imply route-task competence.

R2 Copy succeeds 3/64; Chain, Branch, and Matched-full each succeed 0/64.
Branch has both poor first-edge/trunk performance and no canonical predecision
F layout on its short common trunk. Geometry and capability are distinct.

R3 reaches 32 strict pairs in each F/M development cohort. Independent F
confirmation yields 93 pairs from 128 fixed sources, at eta=0.03 and epsilon=0.01.
Fixed-source pair yield is 72.7%; 93 alternatives from 1,520 proposals give
6.1% overall proposal acceptance. It retains 34 reference fallbacks and one
terminated anchor. The conditional mean on the 93 accepted pairs is
-0.00005513 with 95% source interval [-0.00013951, 0.00002952]. The interval
includes zero. F completed natural-text distribution confirmation; M completed
feasibility and a small route-reward probe, without equivalent natural-text
confirmation. The L2 interval does not establish practical equivalence. Coupled
suffix disagreement does not establish a marginal-law effect, and this result does not prove universal text-state sufficiency.

The bounded R5 probe accepts alternatives at all eight M roots on four graphs,
but reference and alternative futures both succeed 0/64. H_reward=0 and G=0.
The all-zero bootstrap is degenerate, not a population zero bound. Task-value
heterogeneity and gain remain unsupported and poorly constrained by this floor.

## Conditional stages and remaining questions

Cache localization is not activated because the positive mechanism trigger is
unmet. Large R5 reward confirmation and equal-cost H3 are not activated because
the bounded probe shows no reward headroom. LoRA, learned selectors, and the
original human-reviewed transfer study remain outside the adopted scope. None
is reported as executed. All actual jobs and outcomes are recorded.

The current route family leaves the main state-value experiment because it is
mismatched to the frozen checkpoint. Lowering thresholds or dropping road
validity does not solve this measurement problem. Official answer-boundary
metadata offer only one LAMBADA and 15 SQuAD crossing answers in the fixed
128-item subsets, before native-root requirements. Future task screening must
first establish conditional reward variation after the intervention boundary.

The strongest reusable result is strict native same-text candidate construction
with independently measured futures. The open research question is whether a
different explicitly stated proposal/observable, or a native task with measurable
conditional reward, reveals useful hidden-state control. Treat that as a new
idea or separately frozen follow-up, not an extension until significance.
A possible bounded offline sequence-dependence analysis is only a recorded suggestion, not an active task; any
post-hoc result would be exploratory and would not alter R4 confirmation.

Primary storage stays on nebula. Formal worktrees and raw artifacts preserve
all tested commits and commands. Two pre-existing untracked P0 drafts remain
untouched and are not validated R-series entry points.
