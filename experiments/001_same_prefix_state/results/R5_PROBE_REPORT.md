# Bounded Branch-M task-value probe

All eight fixed development roots completed at implementation
`9df1226653d328effaff468d794121ad740dd785`, with two noise repetitions on each of
four underlying graphs. Every root reproduced its saved prefix and accepted
the first proposed alternative under eta=0.03, exact emitted IDs, and strict
KL. The probe used eight proposals and all 128 allocated 32-token futures.
Every saved answer was rescored with the public graph evaluator; the recorded
rewards and split-sample statistics agree. See [compact results](r5_branch_m_probe_v1.json)
and [the fixed plan](../R5_DEVELOPMENT_PROBE.md).

## Outcome and scope

Reference futures succeed **0/64**; alternative futures succeed **0/64**.
Both **H_reward=0** and **independent B selection gain G=0**. All A rewards tie,
so the reference-first rule selects the reference at all eight roots. The
source bootstrap degenerates to [0,0]; the compact result explicitly marks
the population confidence interval unavailable. Four graph groups and an
all-zero floor do not provide a useful bound excluding every practical gain.

The existing M anchors contain one or three free generated
positions. Half the roots have only a partial first town (" Pine" or " Stone");
the other prefixes are " Fair Haven ->" and " River Bend ->". These are native
first-block completion anchors, not successful long-trunk or branch-decision
states. Candidate feasibility at such early anchors does not establish useful
planning-state control.

As a descriptive failure diagnosis, 42/128 futures are
parseable. Failure categories are:

| Failed conditions | Futures |
| --- | ---: |
| unique,roads | 2 |
| end,roads | 12 |
| format | 86 |
| end,unique,roads | 13 |
| end,waypoint,roads | 4 |
| end,waypoint,unique,roads | 6 |
| roads | 5 |

These terminal categories are descriptive, not extra confirmatory endpoints.
The meaningful conclusion is the observed task-reward floor, rather than a
negative population heterogeneity or universal inability to improve the model.

## Cost and stopping decision

Construction used 29.25 summed worker-seconds;
future sampling used 404.31; total measured per-root
work was 433.59 seconds. The retained 32-token horizon
covers the canonical remaining route length on these selected graphs; it is
not a reproduction of R2's longer diagnostic generation budget.

The bounded development probe is complete without observed reward headroom.
Stop this floor probe as specified. Do not expand it, train a selector, or start
LoRA. The variance-based R5 reward confirmation and equal-cost H3 study are not
activated. H1b/H2 remain unsupported and poorly constrained by this task floor;
H3 is unmeasured. No claim that candidate search beats repeated reference
sampling follows from this probe.
