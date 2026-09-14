# Task consequence and latent decoder geometry: final core report

The two frozen-model core experiments do not support task-selective protection in this setting. Both primary 95% intervals lie well inside the declared +/-2 percentage-point practical-equivalence band, with substantial field damage and nondegenerate world variation. Real residual direction has a general effect that changes with CFG; that effect does not preferentially protect the queried field. Keep the measurement implementation and close this core study without launching training or expanding the same test until significance.

All reported field scores below use parser v2 and analysis commit `52244c9`. The original outputs and original scores remain available. See [execution protocol](../PROTOCOL.md), [completion audit](../reviews/CORE_COMPLETION_AUDIT.md), and [analysis provenance](final_v2/analysis_provenance.json).

## Primary evidence

Positive H1 protection means less damage to the same field when queried. Positive H2 selectivity means the real-versus-rotated advantage is greater for the queried field. A field is damaged when its value is wrong or unparseable. Effects pair worlds, questions, fields, noise, and rotations; uncertainty uses 5,000 world bootstrap samples stratified by domain and template, with equal weight for the two domains.

| Primary endpoint | Estimate (percentage points) | 95% world interval | Holm-adjusted p |
| --- | ---: | --- | ---: |
| H1 protection, sigma=0.4 | -0.049 | [-0.208, 0.122] | 1.000 |
| H2 selective residual advantage, lambda=0.5, CFG=1 | -0.092 | [-0.360, 0.195] | 1.000 |

These are bounded negative results for the stated total-field-damage estimands, rather than a failure to obtain errors. H1 has damaged outputs in all 128 worlds of each domain and 47 worlds with nonzero paired effects. At the H2 primary point, real residuals damage 123 numeric and 128 entity worlds; rotations damage 127 and 128 respectively, and 90 worlds have nonzero selective effects. Both estimates meet the prespecified minimum of ten damaged worlds per domain and have nondegenerate bootstrap intervals. The intervals exclude the five-point investment reference. They do not establish equivalence of every semantic error class, all decoder boundaries, or natural generation.

Both studies retain all 256 fixed test worlds: every world exactly reconstructs its answer under both questions. Development uses 64 separate worlds; test uses four held-out template families. H1 domain estimates are -0.024 points for numbers and -0.073 for entities; H2 estimates are +0.085 and -0.269 points, respectively. All four domain intervals include zero. Leaving out one test family gives H1 means from -0.163 to +0.016 points and H2 means from -0.269 to +0.098 points. Full domain, template, and error-component estimates are in [H1 evidence](final_v2/h1_noise_v1.json) and [H2 evidence](final_v2/h2_effects_v1.json).

## Static geometry and targeted search

At sigma=0.4, queried-field damage is 35.449%, versus 35.400% for nonqueried fields. Across fields, 6.616% are parsed wrong values and 28.809% are unparseable; 56.543% of complete answers have at least one damaged field. Mean answer-token disagreement is 8.986%. The absence of protection therefore coexists with a substantial error rate.

The lowest tested scale, 0.2, has only 0.684% field damage. At 0.8, damage is about 99.7%; at 1.6 it is 100%. Degenerate zero contrasts at a floor or ceiling are not population zero bounds. The development-selected middle point remains the confirmatory comparison. The once-refined development grid and lexical-only selection are preserved in [calibration](P1_CALIBRATION.md).

The fixed-budget search verifies all 512 prescribed targets, including their encoded endpoints, and finds every target within RMS 0.4. Ray search succeeds on 99.219% at that radius and 100% at the two larger radii. Combined ray/PGD success is saturated, with no role difference. The full fixed budget was used: 73,728 backward steps and 51,104 native whole-answer verifications. Across the 256 paired field edits, the median log ratio of found critical/noncritical distances is -0.000051. These distances are algorithm-dependent upper bounds. Saturated success curves do not establish equality of nearest damaging boundaries. See [search evidence](final_v2/h1_search_v1.json).

## Denoising residual direction

At lambda=0.5 and CFG=1, real residuals damage 42.969% of critical fields and 43.091% of noncritical fields. Matched rotations damage 37.000% and 37.213%. Thus G_critical is -5.969 points (95% interval [-6.793,-5.157]) and G_noncritical is -5.878 points ([-6.689,-5.078]). Real residuals are more damaging than rotations at this working point, to a similar degree for both roles.

The critical-field difference comprises -3.125 points of parsed wrong values and -2.844 points of unparseability. Selectivity remains small in both components: -0.079 and -0.012 points. At lambda=0.125 neither condition produces damage; lambda=0.25 has few damaged worlds, while lambda=0.75 is nearly saturated. These endpoints do not replace the frozen primary comparison.

Rotation matching is correct: all 81,920 expected readouts are present, noise and rotation seeds pair across questions, and the maximum real/rotated RMS discrepancy is 2.38e-7. At lambda=0.5, mean residual RMS is 0.31864 in both conditions. Mean maximum absolute channel values are 1.482 and 1.488. Mean decoder entropy nevertheless differs: 0.151 for real residuals and 0.756 for rotations. Orthogonal matching preserves norms and inter-position Gram structure, not decoder support or the residual distribution. Interpret the comparison as a direction intervention, not an on-manifold matched sample. See [support diagnostics](final_v2/h2_support_v1.json).

CFG=7 changes the general direction effect. On the predefined 64-world control subset at lambda=0.5, G_critical is +14.282 points ([11.963,16.553]), while G_selective is only +0.122 points ([-0.977,1.221]). Comparing CFG=7 with CFG=1 on those same worlds and seeds gives a +18.555-point change in G_critical but a +0.024-point change in selectivity ([-1.295,1.343]). This auxiliary result supports a CFG-dependent general alignment effect without task selectivity. It does not establish that increasing CFG improves absolute reconstruction. See [matched CFG comparison](final_v2/cfg_matched_v1.json).

## Interpretation controls and predictive analyses

Removing the question and assigning both role labels to the same decoded input yields exactly zero protection, as required by construction. Removing the source gives +0.439 points ([-0.049,0.977]). The separately calibrated sentence format gives +0.391 points ([0.000,0.781]), with 87.744% whole-answer failure and 63.037% unparseable fields. These distribution-changing controls do not reveal a substantial role effect. Sentence edits can span multiple tokens and are kept separate from the headline single-token experiment.

With source retained, replacing answer latents by zero recovers 0/256 fields, and eight high-noise replacements recover 0/2,048. The [corrected source-recovery summary](final_v2/source_recoverability_v2.json) provides no source-only decoder-repair evidence. It does not rule out repair at other latent support or during native generation.

Adding task role to the frozen confidence baseline does not improve macro held-out probability scores: log-loss improvement is -0.000269 (95% interval [-0.000963,0.000384]) and Brier improvement is -0.000143 ([-0.000419,0.000114]). The standardized role contrast is descriptively -0.040 points; no causal or significance claim is attached to that fitted-model contrast. See [confidence analysis](final_v2/h1_confidence_v2.json).

On 128 boundary worlds, the four-fold world-grouped post-recovery model uses residual RMS and clean confidence before adding target-specific boundary features. For total damage, baseline/geometry log loss is 0.08700/0.08711 and AUROC is 0.99544/0.99543; the log-loss improvement is -0.000111 ([-0.000373,0.000133]). For parsed wrong values, log loss is 0.05987/0.06038 and AUROC is 0.71241/0.70472; improvement is -0.000507 ([-0.001079,0.000055]). Brier increments also include zero. Geometry adds no established predictive gain. The high damage AUROC is post-recovery prediction with residual size across four noise levels, not a prospective predictor from clean geometry. Calibration bins show imperfect calibration, particularly for the rarer parsed-wrong outcome. [Full scores, fold AUROCs, and bins](final_v2/geometry_prediction_v1.json) retain this negative evidence. Intervals for these auxiliary scores condition on the fitted cross-validation models.

## Blinded output audit and evaluator repair

An assistant reviewed 100 stratified outputs before opening condition and parser labels; this is not an independent human study. Manual labels were committed at `2853772` before unblinding. The sample contains 50 H1, 40 H2, and 10 sentence outputs, stratified across domain, noise, and predicted error type. It is diagnostic rather than a population accuracy sample.

The original parser agreed on 96/100 items and 195/200 field labels. Four items exposed five incomplete entity phrases incorrectly marked as parsed wrong values: dangling conjunctions, a dangling possessive, and standalone `of`. Parser v2 rejects those incomplete forms. All 80 original cases, ten regression cases, and 200 frozen audit field labels then agree. Agreement on the repaired audit set is not an independent validation estimate.

Uniform rescoring covers 193,728 retained record rows across the 36 formal runs, plus clean anchors. It moves 659 field labels from parsed-wrong to unparseable, changes no total-damage label, and leaves both primary test files byte-for-byte identical. Exact-token search, eligibility, model outputs, configurations, and selected noise points are unchanged. The raw view remains intact and the new view has its own [rescore manifest](final_v2/rescore_manifest.json). No model output was regenerated.

Whole-fact judgments are separately 40 correct, 13 incorrect, and 47 uncertain. Six readable complete facts fail the strict record grammar. Other alphabetic strings remain literal parsed entity labels; a parsed wrong string need not be a plausible person's name. Total damage is therefore a strict field-record metric, not an unrestricted semantic-factuality score. [Review labels, fixed sample, and before/after comparisons](../reviews/BLIND_REVIEW_METHOD.md) preserve this distinction.

## Execution, costs, and reproducibility

Use the pinned official source `7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c` and checkpoint `c1eafdd9cfd8064aeb917d569ef70a075b353eed`. H1 test implementation is `ab3956f`; H2 is `a23ab19`; the scorer and final analysis are `52244c9`. Formal launches used committed detached worktrees on nebula, physical GPUs 5-8. All 36 recorded formal jobs exited successfully. Their summed overlapping worker wall time is 9.434 hours, not dedicated GPU-hours; maximum recorded peak memory is 9.784 GB. No training ran.

| Main group | Jobs | Output units | Summed worker hours |
| --- | ---: | --- | ---: |
| H1 test noise | 4 | 32,768 readouts | 0.268 |
| H1 fixed search | 4 | 512 targets | 0.921 |
| H2 CFG1 test | 4 | 16,384 recoveries; 81,920 readouts | 4.414 |
| H2 CFG7 control | 4 | 4,096 recoveries; 20,480 readouts | 1.552 |
| P0, calibration, controls, geometry | 20 | Detailed per-job accounting | 2.278 |

H2 CFG1 uses 106,496 conditional, 106,496 unconditional, and 16,384 history DiT calls; CFG7 uses 26,624, 26,624, and 4,096. Conditional/unconditional arithmetic remains executed at CFG1 for native parity. [Cost evidence](final_v2/study_costs_v1.json) contains all job commits, configurations, units, timers, peaks, and instrumented calls, including the separately disclosed single P0 history call outside its original counter.

Raw outputs: `/home/mlw0719/cola_dlm_exploration_storage/runs/002_task_consequence_basin/`. Each formal run retains `launch.json`, resolved `measurements/config.json`, summaries, and exit status. Original analysis is `analysis-v1/`; corrected records are `rescored-v2/`; final analysis is `analysis-v2/`. The [analysis commands](final_v2/analysis_commands.json) [control commands](final_v2/control_analysis_commands.json), and [rescore command](final_v2/rescore_command.json) reproduce the final views without new model execution. Shared [job events](../../../jobs/jobs.jsonl) and [result records](../../results.tsv) link the evidence to commits.

P0 established exact clean/native continuation checks, finite gradients, alignment, pinning, and rotation preservation; its smoke establishes implementation validity rather than a scientific effect. Full fresh decoder calls were retained because cached logits differed despite matching greedy tokens. Other declared departures are deterministic PRNG candidate order, answer-preserving trailer token concatenation, and the separately labeled sentence word-span control. See [P0 report](P0_REPORT.md) and the protocol for details.

## Figures and decision

The five final figures are [H1 damage and protection](final_v2/figures/h1_noise_protection.pdf), [error types](final_v2/figures/h1_error_types.pdf), [fixed-budget search](final_v2/figures/h1_fixed_search.pdf), [H2 residual direction](final_v2/figures/h2_residual_direction.pdf), and [predictive calibration](final_v2/figures/geometry_prediction_calibration.pdf). PNG companions are in the same folder. The H2 right panel is G_selective; zero-error and saturated points are contextual endpoints, not equivalence evidence.

Observation: changing the queried field produces very small paired protection and selective-direction differences in this encoded-reference interface. Inference: the proposed task-selective basin mechanism is unsupported at the frozen working points, while CFG-sensitive general residual direction effects are real within these diagnostics. Decision: close the core hypothesis test, retain the shared implementation, and do not activate LoRA or enlarge this cohort. A future study of CFG-dependent residual support or a native task with verified answer competence should receive a new frozen question and design. Natural SQuAD reconstruction, free/native generation, and training remain unexecuted extensions; no conclusion here is transferred to them.
