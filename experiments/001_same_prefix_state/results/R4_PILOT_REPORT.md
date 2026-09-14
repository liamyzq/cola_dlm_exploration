# F distribution pilot

The frozen pilot contains all 32 accepted F development pairs, measured in two
disjoint scheduled parts under identical settings. Each candidate receives four
A and four B independent future noises, paired across candidates within each
split. All 512 trajectories completed and the raw-token endpoint recomputation
matched every recorded root. See [compact results](r4_pilot_f_v1.json).

The mean cross-split H_token is **0.000000**, with a 95% source-document bootstrap
interval of **[-0.000213623, 0.000244141]**. Negative finite-sample estimates were
retained. The interval is not degenerate. This pilot does not demonstrate a
stable difference in the declared token-position probability observable.

In contrast, 156 of 256 paired candidate/reference suffixes differ somewhere
within the 32-token horizon, with mean token-position disagreement 0.109497.
That is a common-noise coupling result, not a distribution-difference test.
Different realized suffixes can coexist with a near-zero cross-split endpoint.
The data do not establish equality of every marginal or joint future law.

Future inference plus state reconstruction used 1,632.22 summed worker-seconds.
Candidate construction and all R3 calibration/collection costs are additional.
No task reward, selection gain or equal-cost inference utility was measured.

Decision: keep the locked F setting and run the fixed 128-source independent
confirmation with eight A/eight B samples and reference fallbacks. Do not tune
eta, KL, root inclusion, or the endpoint using this pilot. The predeclared
positive-effect cache-path diagnostic is not activated by this result. Its
unused budget is not transferred to another search. H1b/H2/H3 remain unmeasured.
