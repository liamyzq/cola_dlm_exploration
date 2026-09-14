# Figure captions

## H1 random corruption

`h1_noise_protection.pdf`: Frozen synthetic test, 256 paired-clean worlds, 16 paired Gaussian seeds per query and scale. Left: critical and noncritical field-damage rates; curves nearly overlap. Right: paired noncritical-minus-critical damage in percentage points, with 95% world-clustered intervals stratified by domain and template and equal-domain averaging. Sigma=0.4 is the development-selected primary point. The zero contrast at sigma=1.6 is saturated damage, not an informative zero-mechanism bound.

`h1_error_types.pdf`: Mean field outcomes over the same fixed worlds and paired queries. Valid-wrong and unparseable rates are separate. The primary-point damage is mostly unparseable under the declared record grammar; the final output audit accompanies semantic interpretation.

## Fixed-budget target search

`h1_fixed_search.pdf`: Success of exact whole-answer prescribed replacements on the 128-world boundary cohort (512 targets). The two role curves coincide. Ray success at RMS0.4 is99.219%; combined ray/PGD success is100%, and all curves reach100% at larger measured radii. Both panels share a zero-based percentage scale to show saturation. The fixed algorithm uses73,728 backward steps and51,104 native verifications. Found distances are upper bounds toward prescribed alternatives, not true distances to every damaging boundary.

All panels are rendered on nebula with the committed `scripts/plot_task_basin.py`. PNG previews and the full source summaries remain under the idea-002 `analysis-v1` run directory.
