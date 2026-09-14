# Research Progress

## Active idea 002: task consequence and decoder geometry

The supplied second protocol is active under `experiments/002_task_consequence_basin/`. P0 passes at `4393c75`: 16/16 paired-clean worlds, 64/64 exact target endpoints, input-gradient and native-recovery checks. The output pipeline smoke at `d4a4b0a` also passes. These establish measurement feasibility only. Fresh full decoder readout is retained because cached raw logits differ despite identical greedy tokens.

The initial development grid missed the required lexical range. The single allowed refinement selects sigma_star=0.4 at 8.181% token disagreement, with 64/64 paired-clean worlds. H1 is frozen at 256 worlds and 16 paired seeds over [0.2,0.4,0.8,1.6]. Main random perturbation and the full 128-world fixed-budget search are launched from `ab3956f`; no task-role effect has yet been interpreted. The balanced search development probe completes 8 targets and 1,152 backward steps in 51.21 seconds, so the original search budget is retained.

The separately calibrated sentence control selects sigma=0.44 at 12.144% lexical disagreement. All four interpretation controls are launched from `a2f9eba`. H2 development recovery at `d4a4b0a` is still awaiting completion; select lambda_star from its real-residual lexical disagreement before launching the main H2 and fixed CFG7 subset. Long waits belong to the monitor subagent. Exact live/terminal job evidence is in `jobs/jobs.jsonl`.

Next: finish H2 calibration and freeze its test, then aggregate H1/search/H2 and controls with world-clustered intervals, perform the blinded parser-output audit, and render the core figures. Natural SQuAD and LoRA remain unactivated extensions. Raw artifacts and frozen worktrees stay on nebula; [P1 calibration](experiments/002_task_consequence_basin/results/P1_CALIBRATION.md) records the scale decision.

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
