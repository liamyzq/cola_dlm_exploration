# P0 review and a revised no-training experimental plan

Date: 2026-09-14. Reviewed project revision: `943b8f55c6112b654ec5b967bdffe2cea36f70f4`, branch `codex/001-same-prefix-state`.

This is a proposed revision, not an executed P1/P2 experiment. No model or selector training was performed for this review. The released checkpoint remains the model of interest. The original P0 evidence must remain intact.

## Decision

Do not start LoRA or selector training. First remove an unnecessary dependency between the representation question and long synthetic route competence. Keep exact emitted token equality, faithful state restoration, reward-blind proposal construction, and independent confirmation. Relax convenience requirements only through explicitly versioned experimental cohorts.

Run three separate checks: released-model task competence; feasibility and future-distribution effects of same-text native generated states; and conditional task-value/selection effects. None should silently stand in for the others.

## 1. What the evidence establishes

The repository records 32 passing engineering examples, then 128 graphs per difficulty with four generations per graph. Each difficulty has zero successful routes and zero eligible intervention roots. Easy parseability is 422/512; Hard is 331/512. These are capability and eligibility observations, not estimates of H1, H2, or H3. The unvalidated full candidate runner remains a separate engineering dependency.

The saved examples contain incorrect edges, missing waypoints, wrong destinations, invented names, premature short answers, and continuations into new demonstrations. Permissive parsing cannot repair these semantic violations. The repository stores two matched raw examples plus aggregate summaries; this review did not read all 1,024 full worker records from nebula.

Sources: [P0 report](https://github.com/liamyzq/cola_dlm_exploration/blob/943b8f55c6112b654ec5b967bdffe2cea36f70f4/experiments/001_same_prefix_state/results/P0_REPORT.md), [saved examples](https://github.com/liamyzq/cola_dlm_exploration/blob/943b8f55c6112b654ec5b967bdffe2cea36f70f4/experiments/001_same_prefix_state/results/p0_examples_v2.json), [original protocol](https://github.com/liamyzq/cola_dlm_exploration/blob/943b8f55c6112b654ec5b967bdffe2cea36f70f4/experiments/001_same_prefix_state/PROTOCOL.md).

## 2. Concrete design issues

1. **The original full-generated-block condition increased task difficulty.** The initial short routes were lengthened to 10–12-town trunks with two-word names to fit a fully generated 16-position block. This made many-hop edge retrieval and long exact copying prerequisites for any mechanism observation.
2. **Demonstrations and targets differ in length and names.** Demos use four or five single-letter towns; targets use long multiword routes. A bounded matched-format experiment is justified, but matching four long demonstrations could create a new context-length problem.
3. **Easy and Hard change two variables.** Road density and demonstration count change together: Easy uses four demonstrations, Hard two. They do not isolate a graph-difficulty effect. Subsequent comparisons must hold demonstration count fixed.
4. **Boundary choice is conservative.** The code selects the last complete fully generated block fitting a canonical trunk tokenization, then checks the actual output. Earlier legal boundaries and different spacing may be missed. Use a fixed causal rule selecting the first eligible completed boundary, with a later boundary as a separate sensitivity analysis.
5. **The nominal bypass need not be an irreversible bad decision.** Random auxiliary edges can connect it back to the required waypoint. This does not explain the current zero correct trunks, and it does not violate the weaker requirement that some complete paths fail. It weakens a future claim that the first branch is a planning bottleneck. Enforce irreversibility only if that is the intended task property.
6. **Configuration fields do not automatically implement decoding ablations.** The current engine always uses argmax and does not apply repetition penalty; current `greedy=true` and penalty `1.0` agree with this. Editing those JSON fields alone will not implement a new decoder.
7. **Termination needs its own failure label.** The scorer takes the first nonempty line, whereas the runner continues generating a fixed horizon. A future anchor rule must reject boundaries after the answer terminator and distinguish premature termination from wrong-edge failures. Post-terminator text is not an answer, and its cost must still be recorded when generated.

Sources: [route task code](https://github.com/liamyzq/cola_dlm_exploration/blob/943b8f55c6112b654ec5b967bdffe2cea36f70f4/src/tasks/routes.py), [calibration runner](https://github.com/liamyzq/cola_dlm_exploration/blob/943b8f55c6112b654ec5b967bdffe2cea36f70f4/src/tasks/route_calibration.py), [state engine](https://github.com/liamyzq/cola_dlm_exploration/blob/943b8f55c6112b654ec5b967bdffe2cea36f70f4/src/models/cola_state.py).

### Additional static measurements performed during this review

These are new CPU measurements of the existing task construction, not additional model results. Regenerate 128 tasks with seeds 510001 and 510002 using the reviewed code and the official tokenizer from checkpoint revision `c1eafdd9cfd8064aeb917d569ef70a075b353eed`.

| Static property | Easy | Hard |
| --- | --- | --- |
| Prompt token count, min–max | 386–470 | 278–392 |
| Allocated generated token count, min–max | 80–110 | 80–110 |
| Full prompt plus allocated generation, min–max | 480–560 | 368–496 |
| Graphs whose full run extends past 512 positions | 47/128 | 0/128 |
| Prompts or intervention boundaries past 512 positions | 0/128 | 0/128 |
| Graphs without a full generated-block layout | 10/128 | 7/128 |
| Graphs where all three first successors can still reach the waypoint | 81/128 | 104/128 |
| Graphs with an earlier full boundary than the current chosen boundary | 13/128 | 19/128 |

Thus context extrapolation may affect late Easy continuations, but cannot explain initial trunk failures or Hard's zero success. The current runner already allocates more than the official benchmark's 32-token limit; simply increasing `max_new_tokens` is not the demonstrated fix. Earlier full-boundary selection helps only a minority of layouts, strengthening the case for a separately validated mixed-block cohort.

Reconstruction details: the generated horizon is `16 * ceil(((boundary or 32) + 64 + prompt_length % 16) / 16) - prompt_length % 16`, exactly following the runner. The branch count checks reachability from each successor of `len(trunk)-1` to the required waypoint. Each of the current four demonstrations occupies 57, 57, 63, and 57 tokens respectively. Original trunk lengths occupy 29–35 tokens. The 10 and seven impossible layouts reproduce the reported 40 and 28 excluded samples because every graph has four samples.

## 3. Revised hypotheses and claims

Keep the original reward hypothesis; add a weaker distribution diagnostic rather than replacing the original endpoint.

| Name | Question | Sufficient interpretation of a positive confirmation |
| --- | --- | --- |
| H1a, distribution | With the emitted tokens fixed, do native continuous states yield different future text distributions? | Emitted tokens alone are insufficient for the measured future observable under this intervention family |
| H1b, original H1 | Do these states differ in expected future task reward? | State variation matters for the specified task reward |
| H2 | Does selecting on independent rollout set A improve reward on set B? | The selection procedure has reproducible conditional value |
| H3 | Does a fully charged inference procedure beat ordinary sampling at equal cost? | Practical benefit for the evaluated budget, verifier, model, and task |

H1a alone does not establish hidden planning, task usefulness, information beyond the complete soft decoder output, or an inference-scaling method. The architecture already makes continuous history relevant in principle. The more interesting result is a useful effect under tight readout preservation, independent selection, and appropriate cache-path controls.

## 4. Intervention cohorts

### F: Complete generated block

Preserve the original cohort. Intervene on a completed block containing 16 newly generated positions. Keep every earlier latent fixed and rebuild both caches from the common pre-block snapshot.

For H1a, use the model's own naturally generated prefix. It need not match a gold route or reference continuation. Prompts can be drawn from a fixed, public natural-text passage collection. Select 128–256 prompt tokens from each document, without appending a target answer or task instruction. Generate to the first complete generated block, then observe the next 32 tokens. Treat this as natural-text continuation, not as an official benchmark score. Split by source document.

### M: First mixed block, generated positions only

Add this as a distinct, initially exploratory cohort. Let `m = prompt_token_count mod 16`. When `1 <= m <= 15`, the first completed block contains `m` known prompt positions and `k = 16-m` newly generated positions.

For every proposal:

- Preserve earlier caches and latents.
- Clamp all `m` known prompt latents to exactly the original values throughout native denoising.
- Perturb native initial noise only for the `k` generated positions; retain the same known-position inputs.
- Require exact equality of all emitted token IDs; verify equality of the known prompt latent subarray.
- Apply the same raw decoder KL acceptance rule, recording both total KL and KL per generated position when comparing cohorts.
- Commit the complete consistent block and rebuild caches through the normal state path.
- Continue only after the block has completed, with independent future-noise tables.

This preserves native generated-state intervention while allowing a much shorter generated prefix. It is not a mid-denoising intervention, arbitrary block-size change, forced gold prefix, or perturbation of encoded prompt states. The current proposal code explicitly rejects this case, so it requires implementation and validation. Do not simply remove the guard and treat the old engineering evidence as sufficient.

Validate identity replay, known-latent equality, candidate order, generated-token equality, prompt positions, first-block conditioning, cache reconstruction, and subsequent noise pairing. Cover prompt remainders 1–15 with one representative case each, plus an aligned full-block control. Add cases only if failures justify them.

The first-block decomposition and clean conditioning are already part of [CoLa, Sections 5.2 and 17.1](https://arxiv.org/html/2605.06548v1). The proposed restricted intervention is an experimental adaptation of that mechanism, not a claim to have invented mixed-block sampling. Full-block and mixed-block results must be reported separately because they differ in position, number of free coordinates, and conditioning history.

### E: Encoded-prompt states, optional diagnostic only

Perturbing or resampling a VAE-encoded prompt can be useful as an auxiliary state-sensitivity check. It changes a different intervention object. It cannot substitute for either F or M in a claim about naturally generated same-text states. Do not start this extra arm unless F/M leaves a concrete uncertainty that E would resolve.

## 5. Official tasks: use them for the right purpose

The public release reports LAMBADA 50.8% and SQuAD 30.9%. These are reference release scores, not new measurements here. Start with these two tasks as capability positive controls. The official script uses CFG 7, 16 steps, greedy decoding, and a 32-token generation limit; preserve the pinned prompt, answer extraction, and actual repetition handling. Verify all effective settings rather than relying on similarly named JSON fields. [Official release evaluation](https://github.com/ByteDance-Seed/Cola-DLM#evaluation-benchmarks), [benchmark script](https://github.com/ByteDance-Seed/Cola-DLM/blob/main/scripts/run_benchmark.sh).

LAMBADA uses a zero-shot passage continuation scored on the first generated word. SQuAD uses one-shot short-answer generation. The paper's multiple-choice setup generates option text, not just A/B/C/D; preserve that distinction when reproducing results. [CoLa evaluation formats, Appendix 16.3](https://arxiv.org/html/2605.06548v1).

| Dataset/use | Immediate value | Limitation for the main study |
| --- | --- | --- |
| LAMBADA official | Native language-model capability and extraction sanity | The evaluated word is usually finished before a full generated block completes |
| SQuAD official | Nonzero factual-answer capability with exact scoring | Many answers finish within the first block; assess position before using for H2 |
| HellaSwag / StoryCloze | Optional later capability checks with generated option text | Long option text does not guarantee answer identity remains unresolved at the intervention |
| Natural passages as continuation prompts | H1a on naturally generated states without a gold-prefix requirement | No official task-accuracy claim and no automatic H2 reward |

Before selecting an official task for H1b/H2, audit answer token spans relative to native block boundaries. One narrow M-cohort pilot is a multi-token LAMBADA target word whose spelling crosses the first native block boundary. Another is a SQuAD answer crossing that boundary. Preselect using dataset metadata and tokenization, never candidate rewards. Model prefixes must then be generated naturally; incompatible prefixes are reported as ineligible with deployment fallback.

Such subsets may be too small. They test answer-completion state, not long-horizon reasoning. Do not add filler, artificial reasoning text, or arbitrary padding to manufacture a claimed native benchmark condition. A changed prompt is a separate task version.

Gold benchmark answers may define H1b/H2 research rewards. They are unavailable at normal deployment. An H3 comparison using them as a selector is an oracle-assisted diagnostic, not a practical inference algorithm. Route constraints, by contrast, are available in the input and can define a public validator.

## 6. Which gates change

| Original condition | Revised treatment |
| --- | --- |
| At least 90% parseable | Usability target, not a universal scientific gate; malformed answers still fail task scoring |
| At least 80% eligible | Report coverage and cost; do not require it for a conditional mechanism result |
| 15–75% full-route success | Prefer tasks with measurable conditional success and room to improve; 5–95% is a screening guide, not a validity theorem |
| pass@4 at least 50% | Remove as a hard gate; retain as ordinary-sampling headroom evidence |
| All 16 positions generated | Retain in F; add M with known prompt latents exactly fixed |
| Four candidates, three alternatives on at least 70% of roots | Start with two candidates: reference and the first accepted alternative |
| KL epsilon 0.01 nats/block | Keep initially; acceptance has not yet been measured |
| Automatic LoRA fallback or mandatory P3 selector | Remove from the current default sequence |

The 15% and pass@4 requirements were not even interchangeable under a homogeneous independent-sampling approximation: `1-(1-.15)^4` is about 47.8%. Real graph heterogeneity makes pass@4 a separate statistic.

Never relax exact past token equality, reward-blind candidate generation, independent A/B randomness, faithful replay/cache semantics, independent confirmation data, or full cost accounting. Semantic route success still requires legal edges, correct endpoints, waypoint satisfaction, and no repeated node. Report partial achievements as separate diagnostics, not as successful complete routes.

## 7. Bounded no-training execution sequence

### R0: CPU audit and configuration locking

Use the existing task seeds and pinned tokenizer to count prompt lengths, allocated total sequence positions, full/mixed layout eligibility, answer positions, and branch properties. From full existing worker records on nebula, if available, recompute earliest valid causal anchors and classify premature termination separately. Do not generate new model samples merely to repeat already available diagnostics.

For revised route tasks, prefilter impossible layouts from prompt/task structure before model sampling. Record the resulting task distribution. Keep prompt plus allocated continuation within the selected 512-position diagnostic envelope, counting block rounding. This is a conservative control based on the reported training context, not an assertion that 513 positions necessarily fail.

Lock one primary setting and primary endpoint for confirmation after development. Preserve P0-v2 and use new experiment IDs for every changed task family.

### R1: Official capability checks

Use 128 fixed LAMBADA items and 128 fixed SQuAD items, one independent native sample per item. Run a small paired native-versus-wrapper subset to detect prompt, extraction, and effective-setting discrepancies. The already passing 32-example state tests need not be rerun wholesale unless changed code affects them.

A 128-item subset cannot reproduce an exact published percentage. Inspect uncertainty and representative errors. If both official tasks are near zero, investigate checkpoint/tokenizer/prompt/scoring/conditioning before task redesign. If the official pipeline works and only the wrapper fails, fix the wrapper. If both behave reasonably but routes fail, stop treating graph competence as a property guaranteed by the checkpoint.

### R2: At most 256 route diagnostic generations

Use four development cells of 32 tasks × two independent samples. Keep naming convention, demonstration count, decoding, and stopping rules explicit. Use meaningful short examples that fit the context budget; do not automatically substitute four long examples.

| Cell | Task | Question answered |
| --- | --- | --- |
| Copy | Reproduce an explicitly supplied common chain in the same output format | Can the model sustain the required names, separators, and length? |
| Chain | Recover a route from a list of edges with no branching | Can it follow the mapping instead of merely copying? |
| Branch | Short 3–5-town common trunk followed by a small branch, with one public constraint | Can it make a useful decision after a short prefix? |
| Matched full task | A compact, matched-demo version of the original long route task | Does the original family recover sufficiently to justify another attempt? |

These are diagnostic task variants, not four estimates of the same causal effect. To specifically attribute an improvement to demonstration length, follow up only if necessary with one matched pair on the same graphs, fixed demo count, same names, and the same two noise seeds. Do not claim a multi-change intervention isolated one cause.

For every sample log parseability, correct first edge, legal prefix length, natural termination point, available full/mixed anchors, branch outcome, full success, and actual compute. If Copy or Chain fails broadly, the long route family should leave the primary path. Success on a supplied-prefix branch task is diagnostic of the tail only; supplied prefixes do not count as native generated roots.

### R3: Candidate feasibility, independently of route competence

Use 32 development roots from natural continuation cohort F, with M tested after its engineering checks. Keep epsilon 0.01. On a fixed small root subset, inspect eta in `{0.01, 0.03, 0.1, 0.3}` using at most eight proposals per eta. Choose a single eta using token/KL acceptance and nontrivial effective state displacement, not future rewards. Use at most 32 proposals per root in the locked pilot.

Target only one alternative, K=2. Report the sequence of exclusions: boundary available; live generated prefix; same tokens; KL accepted; nonduplicate/effectively distinct state. A raw float32 difference is not informative if downstream lower-precision computation produces the identical effective state. Record that possibility rather than counting numerically duplicate states as useful diversity.

Do not demand 70% coverage. For a bounded pilot, attempt at most 128 roots to obtain up to 32 candidate pairs. This cap is an allocation decision, not a proof that 25% coverage is necessary. Keep reference fallback and actual attempt costs. If the cap is hit, report the achieved sample and do not silently keep resampling.

Only if measured KL acceptance is the limiting factor, add a separately declared sensitivity using epsilon 0.1 and an exact-token-only arm. Preserve the strict arm and its result. If only loose readout control works, narrow the conclusion accordingly.

### R4: Mechanism pilot

Start with 32 roots × two candidates × (four A + four B) futures = at most 512 continuations. Use a fixed 32-token future window for H1a. This is a pipeline/variance pilot, not a guaranteed-powered confirmation. If feasible and informative, lock the setting and use an independent 128-root confirmation with eight A + eight B futures, up to 4,096 continuations. Estimate uncertainty by source prompt/document or graph, not individual suffix.

For a task with meaningful conditional reward, additionally estimate the original reward H and independent selection gain G. Reference rollout success conditional on the anchor is more relevant than full-route success from the beginning. Do not select confirmation roots because B happened to contain both successes and failures. Such filtering would bias the result. Development evidence can determine the task family, but confirmation follows a frozen rule.

All-zero reference rewards do not mathematically preclude a beneficial candidate. They justify caution and a bounded exploratory attempt, not a theorem of impossibility. Do not spend the full original P2 budget repeatedly measuring a floor effect.

### R5: Independent task-value confirmation and optional training-free cost study

If H1b/H2 look promising, choose a fresh fixed test size using development variance and a practical target gain, provisionally delta=0.05 (five percentage points). Keep pilot and confirmation data separate. The original 512/1,024/2,048-root options are budgets, not automatic power guarantees.

If no training remains the constraint, compare candidate allocation plus rollouts against repeated reference continuations under identical measured cost, and optionally compare fixed decoder-margin/entropy rules. No learned selector is required to ask this cost question. Charge candidate proposals, rejections, both CFG passes, decoder checks, state/cache work, rollouts, and selection. Permit returning any valid answer found by probes. A probe answer must not be discarded solely to make a method appear better than Best-of-N.

For a decoder rule, fix its formula on development data and compare reference and random candidate choice. For gold-labelled benchmarks, label any answer-aware selector as oracle-assisted; reserve deployment claims for available verification signals.

## 8. H1a statistic without rewards or training

Let Y be a future token sequence of fixed length L=32; after EOS, use the same PAD token in every remaining position. Define f(Y) as the concatenation of per-position one-hot token vectors, divided by sqrt(L). No full-vocabulary vector needs to be materialized: `f(Y) dot f(Y')` is simply the fraction of equal token IDs at corresponding positions.

For candidate j, let mu_j^A and mu_j^B be average f(Y) over independent future-noise sets A and B. Let bar_mu^A and bar_mu^B be averages across the K candidates. Define

```
H_token = sum_j dot(mu_j^A - bar_mu^A, mu_j^B - bar_mu^B) / (K - 1).
```

Conditional on the candidate set, independence of A and B makes its expectation the between-candidate squared variation in future token-position probabilities. Positive independent confirmation witnesses a distribution difference. Common noise within A, and separately within B, is allowed; A and B must remain independent. Keep finite-sample negative estimates.

This measures marginal distributions at specified positions and horizon. A null result does not prove equality of every future joint distribution. Raw paired token disagreement remains a useful debugging statistic but cannot substitute for this cross-split distribution measurement.

Retain original reward H and G definitions when using task rewards. Selection uses only A; ties favor reference; B supplies the evaluation. Candidates and eta cannot depend on A or B in a confirmation run.

## 9. Decisions after each possible result

| Observed result | Appropriate action and claim |
| --- | --- |
| Official model works; wrapper does not | Fix effective inference/prompt/scoring parity, then repeat the small affected check |
| Official tasks work; matched long routes fail | Move long routes out of the primary path; use F natural continuation and M short-prefix tasks |
| Copy works; edge following fails | Use this as task diagnosis; do not call it a latent-state negative result |
| Full blocks yield too few roots, M works | Continue M as a narrower native generated-state study; retain separate full-block limits |
| Roots exist but no exact-token candidate passes | Examine proposal family and effective displacement; do not infer absent hidden information |
| Exact-token candidates exist but strict KL rejects them | Run declared KL sensitivity; strict and loose results stay separate |
| H1a positive; reward remains flat | Report distribution-state effect only; investigate task suitability without automatic training |
| H1b positive; alternatives are mostly worse | Heterogeneity does not establish optimization headroom; revise proposal direction or stop selection work |
| G uncertain and its interval still includes practical gains | One bounded refinement of A sample count or independent sample size may be justified |
| G upper confidence bound is below practical delta | Stop the present practical selector route at that effect scale; preserve the mechanism result |
| G positive; equal-cost Best-of-N wins | Current method is uneconomical; do not automatically train a selector to rescue it |
| Gains appear only with prompt-latent changes or gold-prefilled prefixes | Limit claims to that different intervention; the native generated-state hypothesis remains unanswered |
| Strict controlled candidates show no detectable difference with a precise interval | Report an upper bound for the tested observable, cohort, eta, KL, and horizon; do not universalize to all continuous DLMs |

Absence of statistical significance is not itself a stopping proof. Decisions should consider the interval relative to the practical effect target and the remaining budget.

## 10. Minimal repository changes to implement next

1. Update `PROTOCOL.md` and `PROGRESS.md`: remove the default training fallback; add H1a and separate F/M cohorts; split competence, candidate feasibility, and deployment gates; revise uncertainty-based stopping rules.
2. Update `src/tasks/routes.py`: shorter task family, matched demos, fixed demo count, optional irreversible bypass property, causal earliest-boundary rule, and explicit terminator handling.
3. Update calibration/reporting: conditional reward, prefix survival, total position length, boundary type/free-position count, and exclusion funnel. Keep original output-success semantics.
4. Extend `src/methods/same_prefix.py` for M with explicit known-position invariants; validate before producing scientific results.
5. Add the H1a vector/kernel statistic and a complete small mechanism runner. Verify its null behavior on identity candidates, A/B isolation, and cluster aggregation; these checks address genuinely new statistical code.
6. Add official LAMBADA/SQuAD capability configurations and faithful data/extraction plumbing using pinned upstream code. Do not claim official reproduction with a rewritten prompt or scoring rule.
7. Commit the implementation/configuration before formal runs; store changed-task evidence under new IDs. Preserve all P0-v2 negative evidence. No LoRA module or selector training data is needed for these steps.

The first desired deliverable is a real same-text candidate pair with validated independent futures and a measured acceptance/cost funnel. A high route pass rate is not the research objective. The next useful decision is whether that state pair exhibits a reproducible distribution effect and, on an appropriate task, a reproducible reward effect.
