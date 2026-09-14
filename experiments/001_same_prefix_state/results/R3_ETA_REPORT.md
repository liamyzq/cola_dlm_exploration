# Native candidate eta calibration

The fixed eight development roots were evaluated independently in F and M at
commit `3209858`. All four workers completed successfully. The raw root/proposal
records and artifact paths are linked in [the compact result](r3_eta_v1.json).

| Eta | F paired / attempted roots | M paired / attempted roots |
| --- | --- | --- |
| 0.01 | 4 / 8 | 6 / 8 |
| 0.03 | 5 / 8 | 6 / 8 |
| 0.10 | 2 / 8 | 5 / 8 |
| 0.30 | 0 / 8 | 5 / 8 |

All eight F roots were live; M had seven live roots and one aligned prompt with
no mixed block. Acceptance required exact emitted token IDs, block KL sum at
most 0.01, position maximum at most 0.0025, and distinct computed caches. M
preserved known prompt latents. These are native consistent state pairs.

The preregistered maximum-coverage rule, with larger eta breaking ties, selects
**eta 0.03 for both cohorts**. Accepted median latent displacement was 0.3692
for F and 0.2475 for M; median BF16 DiT-input displacement was 0.3777 and 0.2471.
Differences therefore did not disappear at the model's computation precision.
The eight-root calibration is too small to precisely estimate corpus coverage.

At the selected eta, F used 35 proposals and 58.22 worker-seconds for its arms;
M used 15 proposals and 25.35 worker-seconds. Original root construction cost
26.79 and 13.61 worker-seconds, respectively. Total calibration also includes
all rejected proposals and the three unselected eta arms; do not attribute
only successful-proposal time to the method. These are summed worker times,
not elapsed wall time or an equal-cost utility result.

Continue ordered roots 8..127, stopping after 27 additional F pairs and 26
additional M pairs or exhaustion. Reuse the five and six selected calibration
pairs, respectively, for at most 32 paired roots per cohort. Keep strict KL;
current feasibility does not warrant a relaxation sweep.

The primary R4 cohort is **F**, following the protocol's complete-generated-
block priority. M remains a separate feasibility cohort. No future reward or
formal H_token estimate was read to select this setting. R4 will measure
independent A/B suffix distributions; candidate acceptance alone does not
establish a distribution effect or useful selection.

Calibration and collection have different proposal caps (8 versus32). Report
their funnels separately. Ordered collection stops at its accepted-pair target,
so its paired/attempted ratio is descriptive under that stopping rule; do not
attach a fixed-sample binomial interval or treat it as independent confirmation
coverage. The fixed128-source confirmation provides that later measurement.
