# Same-text native states: revised no-training protocol

Version: R-v1, adopted on 2026-09-14 UTC following the user's request to incorporate the P0 audit and change the plan. This document governs subsequent experiments. The [original P0 protocol](archive/PROTOCOL_P0_v1.md), its configurations, and all P0-v2 outcomes remain historical evidence. The [supplied audit](reviews/P0_review_no_training_plan_v2.md) is preserved verbatim; its reported static measurements are attributed review evidence until R0 reproduces them.

## Objective and scope

Obtain validated native same-text state pairs on the released CoLa checkpoint, measure their acceptance and full cost, and test reproducible future-distribution effects. On a suitable task, separately test reward heterogeneity, independent selection gain, and training-free equal-cost utility. Complete the bounded stages below and record the disposition of every conditional stage.

All model parameters remain frozen. LoRA, model adaptation, learned selectors, and selector-training data collection are outside the current execution plan. Natural text is a mechanism input, not a claim to reproduce an official benchmark. Route competence is no longer a prerequisite for the representation study.

Source: `7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c`. Checkpoint: `c1eafdd9cfd8064aeb917d569ef70a075b353eed`. Use nebula physical GPUs 5-8 only. Formal runs use committed configurations and detached worktrees; long waits belong to GPT-5.6 Luna at max reasoning.

## Questions and claim boundaries

| Hypothesis | Endpoint | Positive evidence supports |
| --- | --- | --- |
| H1a | Cross-split token-distribution heterogeneity over the next 32 tokens | Emitted token IDs do not suffice for this future observable under the studied interventions |
| H1b, formerly H1 | Cross-split expected task-reward heterogeneity | Same-text state differences matter for the specified reward |
| H2 | Choose on A, evaluate reward gain on independent B | Reproducible conditional selection value |
| H3 | Fully charged success versus ordinary sampling at equal cost | Inference utility for the measured task, verifier, and budget |

H1a alone does not establish hidden planning, useful task control, information beyond the complete soft decoder readout, or inference scaling. Different paired suffixes alone need not imply different distributions. H1b need not imply beneficial alternatives. Gold-label selection on an official benchmark is oracle-assisted, not a deployable verifier.

## Native state and fixed settings

Restore the same complete pre-block snapshot for every proposal: earlier generated latents, DiT cache, decoder cache, emitted tokens, and positions. Commit candidate blocks through the normal consistent state path. Do not patch cache tails. Native proposals resample block-initial Gaussian noise and run the released sampler to completion.

Use native 16-step Euler, CFG 7, greedy decoding, and repetition penalty 1 for the initial mechanism setting. The current engine implements argmax and no repetition processing; these settings agree, but changing a configuration field alone does not implement an ablation. R1 must inspect effective official settings and extraction. H1a observes 32 future tokens; official capability checks retain the official 32-token generation limit and block-rounding behavior. Any task-specific horizon is fixed before its run and its actual generated cost is recorded.

## Separate intervention cohorts

**F: complete generated block.** Intervene on the first completed block containing 16 newly generated positions. Preserve all earlier state. For natural continuation, use 128-256 prompt tokens from a fixed public passage collection, without adding a target answer, artificial filler, or reasoning instruction. The model generates its own prefix; no gold-prefix match is required. Split by source document.

**M: first mixed block.** Initially exploratory. With prompt remainder m in 1-15, the first completed block has m known prompt positions and k=16-m generated positions. Preserve the known prompt latent subarray exactly throughout denoising; perturb initial noise only on generated positions. Keep known-position inputs unchanged. Commit only after the full block is complete, then continue using independent future noise. This is neither mid-denoising intervention nor perturbation of encoded prompt states.

F and M remain separate in coverage, displacement, KL, effect, and cost reports. Record m, k, absolute boundary, and history length. No change to native block size is permitted.

For task roots, choose the first eligible completed boundary with a fixed causal rule, using only the emitted prefix at that boundary and public task constraints. A later boundary is a separate sensitivity condition. Reject anchors at or after the answer terminator, and distinguish premature termination, wrong edge, crossed decision, and unavailable layout. Do not inspect future rewards to choose the boundary or retry a reference root.

Encoded-prompt perturbations (E) are optional auxiliary diagnostics only. Do not run E unless a specific unresolved F/M question requires it; E cannot substitute for a native generated-state result.

## Exact-text acceptance and native proposals

Require equality of the complete emitted token IDs, including punctuation and special tokens. Do not normalize strings. On the same decoder history, compute raw full-vocabulary distributions q_l before any output processing:

    k_l = 0.5 * (KL(q_l(reference) || q_l(candidate))
                 + KL(q_l(candidate) || q_l(reference)))

Initially require sum_l k_l <= 0.01 nats/block and max_l k_l <= 0.01/4. Apply the same current-block rule to F and M; additionally report KL per generated position for cohort comparison. M also requires exact known-prompt-latent equality. Preserve all past IDs independently of the decoder KL result.

For free positions use e_j = sqrt(1-eta^2)*e_0 + eta*xi_j. In F all 16 positions are free; in M only the k generated positions are free. Save original noise. Proposals and acceptance may not read A/B rollouts or rewards.

Use K=2: reference plus the first passing alternative in fixed proposal order. On a preselected small development subset, examine eta in {0.01, 0.03, 0.1, 0.3}, at most eight proposals per eta. Choose one eta from acceptance and meaningful effective displacement, never future gain. Lock it before the pilot. Use at most 32 proposals per root thereafter. Reject duplicate states; report when differences disappear at the downstream computation precision instead of treating float32 noise as useful diversity.

Do not require 70% candidate coverage. Keep reference fallback, attempted-root counts, rejected proposals, and actual costs. Only measured KL rejection as the binding acceptance failure warrants epsilon=0.1 and exact-token-only sensitivity arms. Declare their budgets before launch and retain the strict result separately; no automatic KL relaxation.

## Independent distribution and value measurements

For a future token sequence Y of length L=32, pad after EOS with the same fixed PAD token. Let f(Y) concatenate per-position one-hot token vectors divided by sqrt(L). Compute its kernel without materializing vocabulary vectors:

    dot(f(Y), f(Y')) = mean_l [Y_l == Y'_l]

For each fixed candidate set, obtain independent noise sets A and B, paired across candidates within each set. Let mu_j^A and mu_j^B be mean features and bar_mu^A/B their candidate averages:

    H_token = sum_j dot(mu_j^A - bar_mu^A, mu_j^B - bar_mu^B) / (K-1)

Its expectation is between-candidate variation in future token-position probabilities. Preserve finite-sample negative estimates. A precise null constrains this observable, horizon, cohort, and intervention family; it does not prove equality of every future joint distribution.

For task reward means v_j^A/B, retain the original definitions:

    H_reward = sum_j (v_j^A-bar_v^A)*(v_j^B-bar_v^B)/(K-1)
    j_star = argmax_j v_j^A
    G = mean_roots(v_j_star^B-v_reference^B)

Ties favor reference, then candidate order. Candidates, eta, task family, and confirmation inclusion cannot depend on B. H is undefined for K=1; report conditional H and coverage, while fallback selection gain is zero. Record the actual fallback answer and reward. Never retain confirmation roots just because their rollouts contain both successes and failures.

Estimate 95% intervals by source document or underlying graph, clustering all roots and suffixes from that source. Do not bootstrap individual suffixes as independent observations. Graph splits must be topology-disjoint; node renaming alone is insufficient.

## Execution sequence and budgets

Every changed task, cohort, and effective setting gets a new experiment ID and a committed resolved configuration. The sizes below are ceilings or fixed screening samples, not power guarantees. Unused conditional budgets do not transfer automatically to unrelated sweeps.

| Stage | Initial allocation | Decision |
| --- | --- | --- |
| R0 | CPU reconstruction and existing worker records; no new generations | Resolve layout, context, termination, boundary, and branch-property issues |
| R1 | 128 fixed LAMBADA + 128 fixed SQuAD items, one native sample each; small paired official/wrapper subset | Establish capability and prompt/extraction/effective-inference parity |
| R2 | Copy, Chain, Branch, Matched-full: each 32 tasks x 2 samples; at most 256 generations | Separate sustained copying, edge following, short branch decisions, and the combined route task |
| R3 | Natural F first; M after validation. Per declared cohort, at most 128 attempted roots to obtain at most 32 pairs; at most two cohorts | Measure exact-token/KL acceptance, effective displacement, coverage, and proposal cost |
| R4 pilot | One development-selected primary cohort, up to 32 pairs x 2 candidates x (4 A + 4 B); at most 512 futures | Validate the complete runner and estimate distribution/value uncertainty |
| R4 independent distribution confirmation | Fresh fixed 128 source roots, up to 2 candidates x (8 A + 8 B); at most 4,096 futures | Confirm locked H1a; report actual eligible sample rather than topping up after results |
| R5 conditional value confirmation | Fresh task roots; choose fixed size from development variance and delta=0.05; provisional options 512/1,024/2,048 | Confirm H1b/H2 and decide whether a training-free cost study is justified |

R3 caps apply separately to explicitly named F and M cells, for a maximum of 256 attempted roots across both. The R4 pilot and confirmation budgets apply to one primary setting, not repeated searches across settings. Additional sensitivity arms require explicit bounded configurations before execution. Preserve all failed attempts and exclusion counts.

### R0: reuse existing evidence

Reconstruct the two original 128-task sets with their original seeds and pinned tokenizer. Count prompt length, rounded allocated sequence length, full/mixed layouts, earliest legal causal anchors, and first-branch reachability. Read all available P0 worker records to classify semantic failures and premature termination; do not infer population frequencies from the two compact examples.

The audit reports that 47 Easy graphs exceed 512 total allocated positions, while no original intervention boundary does; Hard stays within that envelope. These are review measurements pending local reproduction. Use a 512-position envelope for new route diagnostics, including block rounding. This is a conservative control, not a theorem of failure at position 513. Prefilter impossible layouts from task structure before sampling and record the resulting distribution.

Audit official answer token spans relative to the first mixed boundary before selecting a reward task. Corpus selection and tokenization may use gold metadata, but state prefixes must be generated naturally. Avoid padding or prefilled gold text to manufacture an official condition.

### R1: faithful capability controls

Use pinned official LAMBADA continuation and SQuAD short-answer prompts and extraction. Published scores quoted in the audit are reference claims, not project measurements or targets that a 128-item subset must exactly reproduce. Inspect upstream implementation before configuring the run; archive dataset revision, fixed item IDs, effective decoding, and scorer provenance. A small paired subset compares the same prompts and noise through official and wrapper paths.

If both official paths are near zero, investigate checkpoint/tokenizer/conditioning/scoring before redesign or training. If official inference works but the wrapper fails, repair the discrepancy. If both work but routes fail, remove long-route competence from the primary research path.

### R2: bounded route diagnostics

Fix naming convention and demonstration count across comparisons intended to isolate graph difficulty. Use concise meaningful matched demonstrations within the context envelope.

- Copy: reproduce a supplied chain; diagnose format and length, not native-root task-value gain.
- Chain: recover a route from an unbranched edge list.
- Branch: 3-5-town common trunk, small branch, one public constraint.
- Matched-full: compact matched-demo version of the original longer task.

These four variants change different requirements and do not isolate a single causal factor. Only if necessary, use a separately declared paired comparison on identical graphs, names, demo count, and two noise seeds to attribute a demonstration effect. If claiming an irreversible bad first branch, enforce that property; existence of a failing complete path alone does not imply it.

Log parseability, first-edge correctness, legal-prefix length, termination, F/M anchors, branch outcome, complete success, and actual compute. Complete route success still requires listed directed edges, correct endpoints, waypoint, no repeat, and one parseable answer. Partial progress is a separate metric. Text generated after the first answer terminator is not scored as answer content; its generation cost remains charged.

### R3-R5: independent feasibility and useful effects

Candidate feasibility proceeds without route success as a prerequisite. Record the funnel: raw prompts -> available boundary -> live prefix -> same-token candidate -> KL acceptance -> effectively distinct state -> measured future behavior.

Choose task families using development evidence about conditional reward after the anchor. A 5-95% success range is a screening guide, not a scientific validity gate. All-zero reference reward does not logically exclude a beneficial alternative; permit a bounded exploration, not repeated full-budget floor measurements. No universal parseability, eligibility, or pass@4 threshold gates H1a.

Multi-token LAMBADA words or SQuAD answers crossing M may supply narrow task pilots if metadata coverage permits. Report these as answer-completion studies, not long-horizon planning. Natural passage continuation supplies H1a without automatically supplying H2 reward.

R5 uses development paired variance and a five-percentage-point practical gain to choose and freeze test size before reading confirmation results. One bounded refinement of A sample count or independent sample size is permitted when uncertainty still includes practical gains; define its allocation before launch. Do not repeatedly extend a run until significance appears.

## Controls and meaningful validation

Reuse the 32 passing engineering examples for unchanged paths. M requires one representative prompt remainder case for each m=1..15 and an aligned F control. Validate identity replay, exact known-latent equality, prompt positions, generated-token equality, first-block conditioning, candidate order, cache reconstruction, and subsequent noise pairing. Removing the old mixed-block guard alone is insufficient.

Validate the new H_token kernel against an explicit small-vocabulary calculation, identity-candidate null behavior, A/B isolation, signed estimates, and source-cluster aggregation. Validate the end-to-end candidate runner before interpreting its output. Failed changed-path checks stop only the affected scientific launch until corrected.

For an interpretable positive mechanism, include bounded cache-path localization: consistent reference/reference and candidate/candidate primary states plus DiT-only and decoder-only counterfactual paths. Choose the diagnostic sample and cap from development before confirmation. Re-encoding visible text remains an optional diagnostic for a specific uncertainty; encode no future text, check acceptance, and report altered intervention objects separately. Counterfactual or re-encoded states do not substitute for native consistent F/M states.

## Training-free cost study and stopping decisions

Conditional on useful reward evidence, compare candidate allocation plus rollouts with repeated reference continuations, reference once, random candidate choice, and optionally a decoder-margin/entropy rule fixed on development data. No learned selector is required. For gold-answer selection label the study oracle-assisted; practical claims require a verifier available from the input or deployment environment.

Charge all proposals and rejections, both CFG passes, decoder checks, state/cache work, rollouts, and selection. Report suffix-relative 1x/2x/4x/8x measured budgets and complete prefix-to-answer cost. Reserve a final suffix before spending on proposals. Any valid answer found by a terminal probe may be returned; do not discard it to disadvantage Best-of-N.

- No accepted candidate: report a feasibility limitation and its measured cause, not state sufficiency.
- Positive H1a with flat reward: report a distribution result only; no automatic training.
- Positive H1b with mostly harmful alternatives: report value variation without optimization headroom.
- G interval includes zero and practical gains: inconclusive; consider the single bounded refinement.
- G upper interval bound below delta: stop the present practical-selection route at that effect scale.
- Positive G but equal-cost Best-of-N wins: report an uneconomical method; do not train a selector to rescue it.
- Effects only under loose KL, changed prompt latents, or gold prefixes: retain the actual narrower claim.
- Precise null: report the tested-observable bound, not a universal result about continuous DLMs.

## Completion and deliverables

The first milestone is a real same-text native candidate pair, validated independent futures, and an acceptance/cost funnel. It is not the final completion condition. Complete R0-R4 when feasible, and R5 when supported; otherwise record the bounded failed or inconclusive stage and its scientific consequence. Finish with a report separating capability, feasibility, H1a, H1b/H2, and cost conclusions, including intervals and remaining limitations.

Provide raw same-prefix examples, cohort-specific acceptance/displacement plots, H_token and reward/selection intervals where measured, cache localization where interpretable, and cost curves only when run. Preserve the old P0-v2 evidence. Original P3 selector training and P5 human-reviewed transfer are deferred outside this revised no-training goal, not falsely marked executed. Source-document natural continuation is now an earlier H1a input; it is not the former P5 factuality evaluation.
