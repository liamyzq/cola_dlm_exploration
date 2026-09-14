# Native same-text candidate feasibility

Both declared cohorts reached the 32-pair development target with the released
checkpoint frozen, exact emitted token IDs, epsilon=0.01, and eta=0.03.
Candidate caches are rebuilt from consistent native latent histories. M keeps
known prompt latents fixed. No KL relaxation, learned selector, or LoRA was used.
See [eta calibration](R3_ETA_REPORT.md) and [collection records](r3_collection_v1.json).

| Cohort | Calibration pairs / roots | Collection pairs / roots | Total pairs / sources | Collection proposals |
| --- | --- | --- | --- | --- |
| F: 16 generated positions | 5/8 | 27/37 | 32/45 | 448 |
| M: first mixed block | 6/8 | 26/33 | 32/41 | 214 |

All 37 additional F roots were live. M had 31 live roots and two aligned prompts
without a mixed boundary; its calibration also had one aligned prompt. All
32 F pairs are in the frozen primary pilot manifest. M remains separate.

Among collection proposals, F produced 190 exact-token matches, of which 163
failed strict KL and 27 passed. M produced 89 exact-token matches, of which 63
failed KL and 26 passed. No proposal was rejected as a raw or computed-cache
duplicate. This measures a real proposal cost even though feasibility succeeds.
The data do not require a relaxation sweep to obtain the planned pairs.

The largest accepted single-position KL was 0.002440 for F and 0.002054 for M,
below the 0.0025 limit. Median accepted latent displacement was 0.3018 and
0.2044; median BF16 DiT-input displacement was 0.3086 and 0.2091. F always
changes 16 generated positions, while M's accepted collection pairs span
1-13 or 15 generated positions. These cohorts have different intervention sizes.

Collection root construction plus proposal work cost 848.07 worker-seconds for
F and 392.64 for M, including failed roots and rejected attempts: 31.41 and
15.10 seconds per newly accepted pair. Complete worker wall times were 861.05
and 405.48 seconds, including startup and output overhead. Calibration costs
are reported separately and are additional to these figures. Future rollout
and selection costs are not included here; no inference-utility claim follows.

Coverage ratios are descriptive under the stop-at-target collection rule.
Calibration uses at most eight proposals per eta; collection uses at most 32.
The fixed independent confirmation will report its own attempted/live/paired
funnel without replacing failures. Candidate existence alone does not establish
H1a, useful task reward variation, or selection gain.

Decision: feasibility is established for both tested native intervention forms.
Keep the strict settings. Complete the one-setting F pilot and independent
confirmation before interpreting future-distribution effects. Preserve the
route capability limitations rather than adding training.

Block KL divided by the number of generated positions ranges from 6.33e-07 to 0.000267 for F and 3.02e-08 to 0.000376 for M in collection. These per-position values supplement the unchanged block acceptance limits.
