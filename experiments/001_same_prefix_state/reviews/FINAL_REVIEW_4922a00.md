# Final review of Idea 001 at 4922a00

## Provenance and disposition

This is an English rendering of the user's closing review supplied in this
conversation after examining FINAL_REPORT.md, the R4/R5 reports, statistical
implementation, and result summaries at commit
`4922a00a08b64a1dadfba0407d171b467589865e`. It preserves the review's substantive
findings and recommendations; it is not a verbatim English source or a new
experimental result. The user requested that it be incorporated into the audit
and research record. The current execution scheme remains formally closed,
and the no-training decision remains in force.

The research state has changed materially from the original P0 limitation:
strict candidates now exist, and the core distribution observable has been
independently measured. Stopping is justified by insufficient positive evidence
for further investment in the current setting, not by a claim that nothing
could be measured.

## 1. One positive finding and distinct unresolved claims

| Question | Evidence | Conclusion |
| --- | --- | --- |
| Can strict same-text, effectively distinct native states be constructed? | 93 pairs among 128 fixed sources, passing token, KL, and effective-state checks | Candidate feasibility is established |
| Do candidates change future token-position distributions? | The independent R4 H_token interval includes zero | No positive support under the current observable and setting |
| Do states differ in task value or offer selectable gain? | Both Branch-M state classes have zero reward | Task capability limits measurement; H1b/H2 are weakly constrained |
| Is there equal-cost inference utility? | No cost-matched utility comparison ran | H3 is unmeasured |

The fixed-source pair yield is 93/128=72.7%, so feasibility is not confined to
a few selected illustrations. Construction nevertheless costs 1,520 proposals
for 93 alternatives, an overall proposal acceptance rate of 6.1%. Constructibility
and efficient search remain different questions. See [R4](../results/R4_CONFIRMATION_REPORT.md).

## 2. What the independent distribution test measures

The signed estimate is -0.00005513, with a 95% source interval
[-0.00013951, 0.00002952]. Keeping the negative estimate is correct: a
nonnegative population target can have a negative finite-sample estimator.
For two candidates, the per-source target is

\[
H_{\mathrm{token}} = \frac{1}{2L}\sum_{\ell=1}^{L}
\|p_{1,\ell}-p_{0,\ell}\|_2^2,\qquad L=32.
\]

Here p_{j,l} is the token probability vector at future position l when
continuing from state j, under the recorded EOS-padding convention. The
reported mean is conditional on the 93 accepted source pairs, out of 128
attempted sources. The 34 reference-only fallbacks contribute coverage and
cost, but do not supply two-state heterogeneity observations.

The question is whether the next 32 positions' marginal token probabilities
differ reproducibly. It does not test every sequence-level dependency. As a
scope illustration, state 0 could generate AA or BB equally often, while state
1 generates AB or BA equally often. Each position has the same A/B marginal,
so H_token=0, while the probability of equal adjacent tokens is 1 versus 0.
This hypothetical example is not evidence of such an effect in the CoLa data.

Do not translate the current interval directly into practically negligible
effects: no correspondence between this squared-L2 scale and task success or
semantic importance has been established.

## 3. Paired output disagreement is a different observable

The 93 pairs and 16 shared future noises give 1,488 paired realizations;
807 differ somewhere (54.2%), and mean position disagreement is 10.2%.
These counts are consistent with the independent distribution result. A
shared-noise comparison asks whether the same random input produces a different
output after the state changes. The independent endpoint averages future
randomness to compare probability vectors. Concrete outputs may change often
while the marginal difference is small or undetected.

A few striking paired continuations therefore do not establish usable semantic
control or planning information in the latent state. This distinction is a
reusable methodological result of the study.

## 4. Retire the route family as the main value task

Bounded diagnostic revisions are complete: Copy succeeds 3/64; Chain, Branch,
and Matched-full each succeed 0/64; Branch-M reference and alternative futures
each succeed 0/64. Every parseable Branch-M continuation violates the road
constraint. Official subsets give LAMBADA 63/128 and SQuAD 43/128, so a universal
checkpoint or wrapper failure is not the best explanation.

The current route family is mismatched to this frozen checkpoint's capabilities
and should leave the main state-value and selection experiment. Lowering a
success threshold does not repair that mismatch; removing road validity would
change the measured task. M makes native anchors easier to obtain, but its
one-to-three generated positions are partial starting-town names or the first
arrow, not a completed common trunk just before a planning decision. See
[R5](../results/R5_PROBE_REPORT.md).

## 5. Official answer-completion tasks also have limited coverage

In the fixed 128-item subsets, only one LAMBADA and 15 SQuAD gold answers cross
the first mixed-block boundary. These are metadata opportunities, not usable
native roots. A correct naturally generated prefix, an unfinished answer, and
a passing candidate would further reduce coverage. See the
[answer-position audit](../results/r0_official_answer_positions_v1.json).

This does not justify another large experiment now. Future task screening
should first establish measurable conditional reward variation after the
intervention boundary with the frozen model.

## 6. Reporting changes adopted without new experiments

- Put the effective sample size beside R4's estimate: a conditional mean on 93
  accepted pairs, with 128 total source attempts and fallback accounting.
- Separate cohort evidence: F has the natural-text distribution confirmation;
  M has feasibility and a small route-reward probe. M has no equivalent natural-
  text distribution confirmation.
- Preserve the distinction between a measured but unsupported R4 effect and
  R5's weakly informative all-zero task floor. Do not collapse them into a claim
  that the idea has no effect.
- State closure as a research-budget decision about this proposal, observable,
  and route setting. It does not require proving every possible gain is zero.

The R5 treatment of the degenerate four-graph bootstrap is correct: [0,0] is
not a population confidence interval establishing zero gain.

## 7. Closure and future work

Close the present Idea 001 execution scheme without adding R4 samples,
extending route-reward trials, or starting LoRA or selector training. Preserve
native F/M intervention, strict candidates, effective-state checks, independent
A/B measurement, and cost records for subsequent research.

Any new study needs a different, explicit testable hypothesis and a reason its
task, observable, or proposal is more informative than the current setting.
A parameter change alone does not justify continuing the same search.

The review allows at most a possible bounded offline exploration of saved
continuations using a single stated sequence-dependence observable, such as
local repetition or adjacent-token structure. This is a suggestion, not an
executed or scheduled stage. Any such endpoint is post hoc relative to R4 and
could generate a new hypothesis, but could not revise the original independent
confirmation conclusion. No offline exploration is performed by this record update.

The final research statement is: strict same-text native continuous states are
constructible; the specified future marginal-distribution effect is unsupported;
the route task supplies no usable reward signal. These completed judgments
justify stopping current investment and preserving the tools for better questions.
