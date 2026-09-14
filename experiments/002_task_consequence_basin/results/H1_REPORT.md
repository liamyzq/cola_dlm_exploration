# H1 and interpretation controls: completed-run readout

Historical parser-v1 interim readout. Superseded by the [final parser-v2 core report](FINAL_REPORT.md); original evidence is retained.

The frozen random-corruption test does not show task-role protection at sigma=0.4. The paired equal-domain estimate is -0.049 percentage points (95% world interval [-0.208, 0.122]). All 256 fixed worlds reconstruct exactly under both questions. This is the initial parser-version readout; the predefined 100-output blinded audit will accompany the final core report.

## Random corruption

The committed implementation is `ab3956f6d2bf21493f268c8e9251c09341c85a7d`. Four workers completed 32,768 answer readouts over four scales and 16 paired seeds. Independent record aggregation finds complete unique world/query/scale/seed keys and identical seeds and RMS across the paired questions.

| Sigma | Critical damage (%) | Noncritical damage (%) | Protection (percentage points) | 95% world interval |
| --- | ---: | ---: | ---: | --- |
| 0.2 | 0.684 | 0.684 | 0.000 | [-0.073, 0.061] |
| 0.4 (primary) | 35.449 | 35.400 | -0.049 | [-0.208, 0.122] |
| 0.8 | 99.744 | 99.707 | -0.037 | [-0.085, 0.000] |
| 1.6 | 100.000 | 100.000 | 0.000 | [0.000, 0.000] |

At the primary point, answer-token disagreement is 8.986%, valid-wrong fields are 6.952%, unparseable fields are 28.473%, and at least one field fails in 56.543% of answers. The primary interval is informative with observed errors and nondegenerate paired-world resampling. The degenerate high-noise endpoint is a saturation result, not independent evidence of equivalence.

Per-domain protection is -0.024 percentage points for numbers (95% interval [-0.293, 0.244]) and -0.073 for entities ([-0.244, 0.098]). Leaving out each test template family gives macro effects from -0.163 to 0.016 percentage points. The two-sided centered-bootstrap primary p-value is 0.6161; there is no positive H1 significance claim. Final joint reporting will account for both predefined primary tests.

## Fixed-budget target search

All 512 target endpoints decode exactly, and every target is found within RMS 0.4 by the combined ray/PGD algorithm. Ray-only success at 0.4 is 99.219% for both critical and noncritical targets; at 0.8 and 1.6 it is 100% for both. Both-success coverage is 256/256 paired edits. The median log critical/noncritical found-distance ratio is -0.0000506. Searches use 73,728 backward steps and 51,104 native target verifications in total.

The declared success curves are saturated at their measured radii. Their zero role contrast does not establish equality of the unknown nearest boundaries. Found distances remain algorithm-dependent upper bounds toward prescribed replacements; no failed distance was imputed.

## Interpretation controls

Each control retains the 64 predefined worlds, with 64/64 paired-clean coverage where anchors apply.

| Control | Protection (percentage points) | 95% world interval | Interpretation |
| --- | ---: | --- | --- |
| No question, identical-input role relabeling | 0.000 | [0.000, 0.000] | Exact paired-null behavior by construction |
| Question only, source removed | 0.439 | [-0.049, 0.977] | Distribution-changing diagnostic; main sigma retained |
| Sentence answer, separately calibrated sigma=0.44 | 0.391 | [0.000, 0.781] | Format/word-span control; no separate significance claim |

Sentence-format full-fact failure is 87.744%; 63.037% of fields are unparseable under the declared sentence grammar. Its labels and whole-sentence factual reading require the planned output audit.

With source retained but answer latents replaced by zero, 0/256 fields are correct across 128 readouts. With eight independent standard-deviation-4 Gaussian replacements, 0/2,048 fields are correct across 1,024 readouts. All these fields are unparseable. This destruction diagnostic provides no evidence that the decoder reconstructs the answer solely from source context.

The world-held-out confidence model gains no macro probability-score improvement from adding task role: log-loss improvement -0.000269 (95% interval [-0.000963, 0.000384]); Brier improvement -0.000143 ([-0.000419, 0.000114]). This is predictive adjustment, not causal mediation.

## Artifacts and next action

Compact evidence: `h1_noise_v1.json`, `h1_integrity_v1.json`, `h1_search_v1.json`, `h1_confidence_v1.json`, and `interpretation_controls_v1.json`. Raw records are under the corresponding `002-p1-test-*` and `002-control-*` directories in the nebula run base. The exact launch command, implementation and config are retained with every run. Figures are rendered from those summaries in `analysis-v1/figures/`; the first two H1 panels have been visually inspected.

Keep this bounded H1 result. Complete independently calibrated H2 and the blinded output audit before making the final core-study decision. Do not alter the fixed H1 scale, templates or sample size after these results.
