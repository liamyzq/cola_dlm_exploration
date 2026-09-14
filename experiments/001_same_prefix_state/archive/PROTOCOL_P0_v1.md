# Same-prefix latent states in continuous DLMs

English translation and execution specification of the user-supplied plan, received 2026-09-14 UTC. The referenced sandbox protocol file was not attached; this document preserves the complete substantive plan in the supplied text. The first study uses only the released CoLa checkpoint with all model parameters frozen.

## Research question and evidence chain

Does already emitted text adequately describe the future generation state of a continuous DLM? Can we keep that text fixed and choose a latent state with greater continuation value?

The evidence chain is: same-text states differ in future value; useful differences can be identified; exploiting them outperforms ordinary sampling at equal total cost.

- **H1:** States with exactly the same current tokens and very similar decoder distributions have reproducible differences in expected future task reward. Different suffixes under a single seed do not establish this.
- **H2:** Some candidates improve on the original state, and selection gains survive independent future randomness. Increased variance caused only by harmful perturbations does not establish this.
- **H3:** Gains exceed those from ordinary repeated sampling after counting all proposal, filtering, and selection costs. Better answers with more compute do not establish this.

H1 without H2 remains a representation result. H2 without H3 establishes exploitable state variation but an uneconomical search method. Complex tree search is unnecessary for the first study.

## State boundary and notation

Intervene only on the last complete generated block. Keep all earlier generated latents fixed. Reconstruct each candidate state from the same pre-block snapshot.

| Symbol | Meaning |
| --- | --- |
| c | Fixed input prompt |
| S-minus | Complete state before the studied block: earlier latents, both caches, tokens, and positions |
| z0 | Original generated block latent |
| zj | Candidate latent; j=0 always denotes the reference |
| S(zj) | Complete state obtained by committing zj from S-minus |
| x | Complete emitted token prefix |
| D(z) | Current-block token IDs decoded with fixed decoder history |
| q_l(z) | Raw full-vocabulary decoder probability distribution at position l |
| U | Explicit initial Gaussian noise tensors for all future blocks |
| Y_j(U) | Suffix continued from S(zj) |
| R(Y) | Task reward for the committed prefix plus suffix |

The supplied plan identifies a 16-position block, latent dimension 16, and patch size 1. Verify these against the pinned release. The official inference path commits generated latents to the DiT history and retains decoder state derived from them rather than replacing these states with a re-encoding of emitted text.

Primary settings: native 16-step Euler sampling, CFG 7, greedy token decoding, repetition penalty 1, frozen weights, and a default continuation horizon of 64 tokens. Calibration must establish that this horizon permits task completion before it is locked. Future randomness comes from block-initial Gaussian noise; candidates share identical future-noise tables.

Compute q from logits before temperature, top-k, top-p, or repetition processing. It is a decoder predictive distribution, not the token sampling distribution under greedy decoding.

## Same-text acceptance

Require exact equality of complete token IDs, including punctuation and special tokens:

    D(zj) = D(z0).

No string normalization is allowed for this test. For every current-block position, define

    k_l(zj) = 0.5 * [KL(q_l(z0) || q_l(zj)) + KL(q_l(zj) || q_l(z0))].

Accept only if both constraints hold:

    sum_l k_l(zj) <= epsilon
    max_l k_l(zj) <= epsilon / 4.

The primary epsilon is 0.01 nats/block. Predefine 0.001 and 0.1 as distortion-benefit sensitivity conditions. These are empirical thresholds, not theoretical guarantees. Measure identity-replay numerical noise first, and lock thresholds before formal testing rather than selecting the most favorable threshold afterward.

## Native candidate proposals

Do not begin with a decoder nullspace or task-reward gradients. Save the original initial block noise e0. With independent standard Gaussian xi_j, form

    e_j = sqrt(1 - eta^2) * e0 + eta * xi_j
    z_j = NativeBlockSampler(S-minus, e_j).

Keep K=4 total candidates, including z0. Attempt at most 32 block proposals per root. Accept the earliest passing proposals in fixed order, without reading future reward. Calibrate eta over {0.01, 0.03, 0.1, 0.3}; choose the largest value at which at least 70% of eligible roots obtain three alternatives. Select on coverage, not future gain.

With only one or two alternatives, select within the actual candidate set. With none, retain the reference. Count rejected proposals as cost. Native sampling followed by same-text filtering does not produce unbiased unconditional-prior samples.

Only after native candidates prove useful but expensive should a separate follow-up consider direct latent proposals, such as weak decoder-sensitivity directions. Report these separately with same-norm random directions, matched KL, and matched cost.

## Directed-route task

Use objectively verifiable short routes with a common trunk before a genuine decision. For example, all legal routes begin A -> B -> C -> D -> E -> F -> G -> H. Two tails, H -> I -> L -> N -> Z and H -> J -> L -> N -> Z, satisfy arrival at Z through N; H -> K -> Z is locally legal but misses N.

Provide the full road list, constraints, and 2-4 short demonstrations in ordinary completion format:

    Find a route from A to Z that visits N.
    Use only the listed roads and do not visit a town twice.
    Route:

Require a natural route list, without JSON, explanations, or a reasoning template. Generate approximately 14-22 nodes with randomized names and road statement order. Every task has at least two successful complete routes and at least one locally legal unsuccessful route. Do not request shortest paths or score against a single reference route.

Use the official tokenizer to determine trunk length. The intervention boundary is the last complete generated-block boundary inside the common trunk, before the first branching decision. Do not add meaningless filler or prefill the trunk for the model. Leave enough continuation tokens to finish the route.

Binary reward is 1 only when the answer has the correct start and end, uses only listed directed edges, visits the required node, repeats no node, and contains one parseable answer. The scorer uses only the graph and constraints supplied in the prompt.

Sample each root reference trajectory once. An incorrect trunk, early termination, or already crossed decision boundary makes it ineligible for intervention; record this without resampling. Mechanism statistics use eligible roots and report coverage. Deployment retains the original continuation and its actual reward for ineligible roots; do not automatically score them as zero.

Calibration uses 128 graphs and four complete samples per graph. Targets: at least 90% parseability, at least 80% arrival at an eligible boundary, 15-75% single-sample success, and at least 50% of graphs successful in one or more of four samples. Predefine two task difficulties and choose between them during calibration, then lock the task.

These targets assess task competence and identifiability, not intervention efficacy. If the base model cannot solve even the easy task, do not train a critic. A separate frozen-VAE, DiT-LoRA capability branch is a possible follow-up, but results from it describe an adapted model rather than the released checkpoint.

## Independent continuation measurement

Define V_j = E_U[R(Y_j(U))]. Common random numbers reduce paired variance, but changed suffixes alone might reflect only a changed mapping from noise to text. Measure expected reward.

Freeze candidate sets before future evaluation. Use independent A and B noise splits, paired across candidates: pilot A/B each contain 4 seeds; confirmation A/B each contain 8 seeds. Let v_ij^A and v_ij^B be candidate reward means, and bar_v_i^A and bar_v_i^B be candidate-group means. For actual candidate count K_i >= 2,

    H_i = sum_j [(v_ij^A - bar_v_i^A) * (v_ij^B - bar_v_i^B)] / (K_i - 1).

Its expectation is the sample variance of true candidate values when A/B are independent and candidates are fixed. Preserve negative estimates and confidence intervals. For K_i=1, heterogeneity is not estimable; report coverage and the conditional estimate separately. Selection fallback gain is zero for that root.

Choose j_star using only A rewards, breaking ties in favor of the reference, then in candidate order. Evaluate only on B:

    G = mean_i [v_i,j_star^B - v_i0^B].

Report candidate acceptance, root coverage, H and G with 95% confidence intervals, and final success versus total compute cost. Bootstrap by underlying graph, clustering all roots and suffixes of a graph together.

## Required controls and engineering checks

1. **Reference replay:** Commit z0 through exactly the candidate path and reproduce the original continuation. Failure invalidates intervention interpretation.
2. **Same-text re-encoding:** Compare generated latent with posterior mode and posterior samples of the currently visible prefix. Encode no future text. Replace only the last block; keep earlier generated latents. Recheck token and KL constraints, report failures and unconstrained results separately. Degradation alone may be distribution mismatch and does not prove deletion of hidden planning.
3. **2x2 cache-path localization:** Compare original DiT/original decoder, candidate DiT/original decoder, original DiT/candidate decoder, and candidate DiT/candidate decoder. Mixed states are counterfactual diagnostics; primary conclusions use consistent candidate states. Do not attribute every decoder-history effect to DiT planning.

Always restore the pre-block snapshot and replay commits rather than patching cache tails. Inspect the actual cache-toggle and update_kv semantics; toggles may clear cache, and update_kv=False may still read it.

Before interpreting results, pass pause/resume, identity replay, AB/BA candidate ordering, cache reconstruction, invariant past token IDs, and explicit future-noise pairing checks on 32 engineering examples.

## Lightweight selector, conditional on positive independent gain

Train a selector only after confirmation of G > 0. Its job is candidate discrimination within the same prompt and prefix, not predicting which graph is easy.

Initial data: 1,024 training graph roots, up to four candidates per root, four continuations per candidate (approximately 16,384 suffixes), and 128 independent validation graphs. Reserve final test graphs separately. Split by underlying graph topology; renaming nodes does not create a held-out topology.

Freeze the base model. Start with a linear/logistic baseline, then assess whether a two-layer MLP with widths 256/128 and at most roughly 1M parameters is worthwhile. Targets are training-rollout success proportions.

Compare text-only shared context (must tie within a same-text group), decoder-only context plus per-position probabilities/entropy/margins, latent or clean-DiT-hidden context plus candidate features, random selection, and always-reference selection. Text-only ties are an input-isolation check, not a scientific discovery. Latent gains over a simple text model do not prove information beyond the complete soft decoder distribution q(z).

Deployment generates and filters candidates, scores them with a small head, commits one state, and continues once. No terminal test-time lookahead or MCTS in the first version.

## Cost-matched deployment evaluation

A/B lookahead estimates state value; the small head is the proposed low-cost deployed algorithm. Any successful answer produced by an actual terminal probe may be returned. Do not discard successful probes and force new continuations to disadvantage Best-of-N.

From the same committed prefix, compare reference once, repeated reference continuations with the public validator (Best-of-N), candidate generation plus random choice, margin/entropy choice, decoder head, and latent head.

Count all rejected proposals, extra CFG calls, decoder checks, selector compute, cache cloning/replay, and rollouts. Use total budgets 1x, 2x, 4x, and 8x; 1x is the measured cost of one fixed-horizon reference continuation. Also report full end-to-end cost including prefix generation. Reserve the cost of one final suffix before spending on proposals; no free fallback after proposal budget exhaustion.

## Stages and continuation decisions

| Stage | Scale | Required evidence |
| --- | --- | --- |
| P0 | 32 engineering examples; 128 calibration graphs, four samples each | Correct replay, task competence, locked task and proposal settings |
| P1 | 128 new graphs; up to four candidates; 8 continuation seeds | Coverage, H, G, measured cost; at most about 4,096 suffixes |
| P2 | 512 new graphs; up to four candidates; 16 seeds | Independent confirmation; re-encoding and cache diagnostics on 64 graphs |
| P3 | 1,024 train roots; 128 validation roots | Within-group ranking and held-out selection gain |
| P4 | Separate test set starting at 512 graphs | Success-cost curves against all declared baselines |
| P5 | 200 source passages | Same-text coverage, future-value differences, and transfer limits |

512 graphs is not a power guarantee. Use validation paired variance and a predefined practical effect of 3-5 percentage points to choose 512, 1,024, or 2,048 final test graphs, then freeze test size. Keep P2 confirmation separate from P4 testing.

For P5, use source-constrained short factual continuation or summarization with a 64-96-token output horizon. Preserve the block intervention and exact same-text acceptance rules. Start with phenomenon and coverage; do not expect a route-trained critic to judge news factuality zero-shot. Score source support, fact coverage, entity/numeric conflicts, and repetition, with a blinded human review subset. If strict same-text candidates are rare, report this applicability limit. Human review requires actual human judgments; automated checks cannot be labeled human review.

Decision rules:

- Low same-text coverage: establish proposal feasibility before critic training.
- Positive H without positive G: retain the state-variation result and stop method development.
- Positive G that available features cannot predict: improvement exists, but no effective low-cost selector is established.
- Effective selector beaten by cost-matched Best-of-N: exploitable state structure, uneconomical current algorithm.
- Gains only at loose KL or anomalous latents: not primary evidence under strict readout preservation.

Complete the stages supported by these gates and report the disposition of every remaining stage. A clear negative or bounded inconclusive result is valid; failure of a capability gate is not evidence against H1. Do not silently substitute a different model or task.

## Deliverables

Produce distortion versus future-value variation, independently evaluated selection gain, and success versus total budget plots when the corresponding stages yield evidence. Include the cache-localization table and exact-prefix examples. If a stage is scientifically gated off, explain why its figure or result is unavailable instead of fabricating data.

## Sources

- [Official inference](https://github.com/ByteDance-Seed/Cola-DLM/blob/7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c/cola_dlm/inference.py)
- [Official VAE](https://github.com/ByteDance-Seed/Cola-DLM/blob/7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c/cola_dlm/modeling_cola_vae.py)
- [Official DiT](https://github.com/ByteDance-Seed/Cola-DLM/blob/7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c/cola_dlm/modeling_cola_dit.py)
- [Released VAE configuration](https://huggingface.co/ByteDance-Seed/Cola-DLM/blob/c1eafdd9cfd8064aeb917d569ef70a075b353eed/cola_dlm/cola_vae/config.json)
