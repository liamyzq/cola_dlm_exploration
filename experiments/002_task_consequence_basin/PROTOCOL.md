# Task consequence / decoder basin: core execution protocol v1

## Scope and provenance

Implement the two frozen-model core experiments from the supplied proposal: P1 static decoder geometry (H1) and P2 conditional denoising residuals (H2), following P0 interface validation. Include the bounded controls needed for interpretation. Natural SQuAD reconstruction, free generation, and optional LoRA are later extensions and are not activated by this core run.

Reuse official CoLa source `7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c` and checkpoint `c1eafdd9cfd8064aeb917d569ef70a075b353eed`. Source and checkpoint paths and the Python environment are in `../../COMPUTE.md`. Use physical GPUs 5-8 only, with the existing launcher and dedicated committed worktrees. Delegate long waits to a monitor subagent.

The user supplied the complete `task_consequence_basin_experiment_protocol_v1.md` after the initial proposal. Its eight templates per domain, 64-name pool, four key pairs, search parameters and trailer policy are adopted. Exact strings are in `src/tasks/task_basin_data.py`. Under the user's higher-priority instruction against unnecessary hashes, candidate selection uses deterministic Python PRNG order with seed 20260914 instead of the document's SHA256 sorting. No checksum files are added. Worlds are deduplicated by their actual domain and four-value tuple across splits. This is the sole candidate-order departure.

## Questions and primary estimands

H1: a field is less damaged when queried than when the same field is unqueried. Pair the same world, original values, replacement, and noise across the two questions. Let P = mean_world(mean_field(p_noncritical - p_critical)), calculated within each domain and then averaged equally across domains. The primary point is development-selected sigma_star.

H2: real recovery residuals preferentially avoid critical errors compared with random channel rotations of identical size. G_critical = H_rotated,critical - H_real,critical, similarly G_noncritical; G_selective = G_critical - G_noncritical. The primary point is development-selected lambda_star at CFG 1. General residual direction advantages without positive G_selective do not establish task selectivity.

Neither hypothesis by itself establishes latent collapse, encoder-only causality, independent semantic abstraction, or free-generation performance. Noncritical modifications still change facts.

## Data and inclusion

Use numeric and name worlds equally. Each world has two source values, two distinct alternative values, two questions swapping the queried field, and one complete answer in a fixed order. Independently balance source and answer order in four combinations. Use eight source/question template families per domain: four development and four held-out test. Input is `Context:\n{source}\nQuestion: {question}\nRecord:\n{answer}`. Questions name the field, not its answer value.

Numbers are 3-98. All four values in a world differ. Half use adjacent edits and half same-digit-length edits with absolute difference at least three. Name originals and alternatives come from the same frozen 64-name pool. Select only using the tokenizer and structural rules, never model reconstruction or margin. Require equal query-prefix token length, identical answer IDs between queries, and exactly one changed token in the intended span. Record tokenizer exclusions. Multi-token name spans are a separate, currently inactive stratum.

Freeze 16 smoke worlds, 64 development worlds (32/domain), and 256 test worlds (128/domain). Preselect 128 test worlds for search and 64 for controls, balanced by domain, template and order. World identity, rather than question or noise seed, is the independent unit. Do not replace reconstruction failures. The primary analysis uses worlds with exact answer-token reconstruction under both questions, while reporting coverage and absolute error over all fixed worlds.

## Model interface

Encode the whole input using the VAE posterior mode and native shifting/scaling; prefix latents stay fixed during interventions. The released VAE uses causal blocks of size 1, whereas DiT uses blocks of size 16. Preserve that distinction. Basin readout uses full input decoding with fresh caches, argmax, no sampling and repetition penalty 1. Freeze all parameters; enable gradients only for input-latent search.

P1 perturbs all and only answer positions; padding after the answer is fixed and cannot causally influence earlier positions. P2 appends the fixed task-independent trailer `\nEnd of record.` repeated as necessary and truncated at the final answer-containing block boundary, rounds the token sequence to full DiT blocks, and corrupts/recovers every position from answer start to the block end, including trailer. Score only original answer positions. Use clean earlier blocks for each recovered block, not previously recovered blocks. Pin mixed-block prefix positions at every Euler step and at output.

## P0 validation

Before formal effects, use 16 smoke worlds to check paired token alignment, parser behavior, clean reconstruction coverage, repeated full-readout identity, posterior-mode selection, finite nonzero latent gradients with frozen model weights, prefix pinning, zero-time identity, and real/rotated residual norm and Gram preservation. Compare the native full-noise Euler continuation with the established shared engine on an identical first block. These detect implementation mismatches; fix affected paths before the corresponding scientific launch.

Run 80 explicit parser cases before model outcomes. Later blind-audit 100 stratified model outputs without showing condition labels. Parse output alone: preserve numeric signs and decimals; normalize names only for case, outer punctuation and whitespace. A missing, conflicting or malformed field is damaged and unparseable. If the parser changes, rescore every retained output uniformly.

## P1 random corruption and search

Development: sigma in [0.005,0.01,0.02,0.04,0.08,0.16,0.32,0.64,1.28,2.56], eight paired noise seeds each. Pick the sigma with paired-clean development mean answer-token disagreement closest to 0.10, without reading task-role differences. Resolve exact ties by the smaller sigma.

Test: [0.5,1,2,4] times sigma_star, 16 seeds. Budget: 256 x 2 x 4 x 16 = 32,768 readouts. Save decoded IDs/text, parsed field states, specified-target hits, token disagreement, word edit distance and noise seed. Include all fixed worlds; filter paired-clean only at analysis.

On the preselected 128 worlds, search each of two fields in each of two questions (512 targets). Encode the complete target answer but keep the anchor prefix fixed. Scan 17 equally spaced points on the answer-latent endpoint direction, then refine only the nearest observed failure-to-success interval eight times without assuming global monotonicity. Search at RMS radii [1,2,4] times sigma_star, with endpoint and paired Gaussian initializations, 24 projected gradient steps each. Optimize the mean hinge max(0, 0.5 - target-versus-best-other margin) over every target position. Use normalized RMS gradient steps of radius/8 and projection to the RMS ball. Verify exact whole-answer token equality every four steps. For each start with success, refine its smallest found successful direction for eight radial bracket steps, keeping the zero failure endpoint and all verified successes. Finish the fixed budget after success. The endpoint start is projected inside the ball; its paired random start has the same RMS. These are the supplied settings; any one-time development adjustment must be recorded before test.

Report success curves under the fixed algorithm/budget as primary search evidence. A found RMS distance is an upper bound; search failure is not a lower bound on the true distance and is never imputed as the maximum radius.

## P2 residual direction

Diagnostic corruption Z_lambda=(1-lambda)Z+lambda*epsilon. It is an experimental corruption, not a claim that this matches the model's verified training distribution. Restart on the native 16-step Euler grid at lambda in [0.75,0.5,0.25,0.125], with [12,8,4,2] steps respectively, clean block history and fixed prefix.

Development chooses lambda_star by overall token disagreement closest to 0.10, never selective effect; exact ties favor the smaller lambda. Use eight development seeds. Test all four positions with eight seeds, CFG 1. Save residual e=Z_hat-Z and compare its readout with four eR channel rotations. Draw R by QR of an independent Gaussian 16x16 matrix with diagonal-sign correction (Haar O(16)); use the same R at every answer position. Pair noises and rotation seeds across questions. Preserve per-position norms and inter-position Gram matrix. Rotate answer residuals; retain the recovered trailer, which cannot affect the causal answer readout.

Budget: 16,384 recovered answers and 81,920 real/rotated readouts. Record actual block and conditional/unconditional DiT calls separately. On the preselected 64 controls worlds additionally run CFG 7 with the same lambda/seed settings.

## Interpretation controls

Record clean original-versus-replacement logit margins, probabilities, and entropy. Raw paired effects are primary; confidence adjustment is mechanism analysis because confidence may mediate protection.

On fixed control worlds include identical-input label swaps, removed question, removed source, zero/high-noise answer latents, and full-sentence answers with separately development-calibrated sigma. Label question/source removal as distribution-changing diagnostics. Protection dependent on source plus successful recovery from destroyed answer latents supports condition-assisted repair rather than independent answer-latent abstraction.

## Analysis and stopping

Bootstrap 5,000 times over worlds, preserving their questions, fields and noise/rotation pairing; stratify by domain and template. Report 95% intervals per domain and equal-domain macro. Report leave-one-test-template-family-out results. Apply Holm correction if claiming significance from both primary tests. Five percentage points is a reference for further investment; equivalence requires the full 95% interval within +/-2 points and enough error events for a nondegenerate estimate.

Do not tune templates, edits, primary noise points or endpoints after reading test effects. Keep the initial 256-world test size unless a single development-based size decision is recorded before test access. If development has no field errors or almost all outputs are unparseable, repair the measurement range before freezing test. H1 null does not prevent H2.

Deliver coverage, error/noise curves, fixed-budget search curves, real/rotated residual errors and selective differences, and a report separating observations, inference and next actions. Natural-data and generation figures remain pending extensions rather than fabricated completed panels.

## Execution details from the complete supplied protocol

Use the four key pairs red/blue, east/west, north/south and gold/silver only when complete query lengths match. Full sequences have at most 256 tokens and scored answers at most 32. Inspect at most 10,000 candidates per stratum; retain the actual exclusion reasons. If fewer than 16 names are tokenizer-eligible, resolve a separate word-span entity stratum before test instead of silently mixing edit sizes.

P0 also checks target-encoding prefix invariance, query order AB/BA, decoder prefix-logit invariance and finite-difference input derivatives. Minimum clean feasibility targets are 90% overall and 80% per domain; low coverage is reported and investigated, never repaired by resampling failed worlds. Target endpoint success is a label, not an inclusion filter.

Sigma calibration is on paired-clean development worlds. At least one development sigma must produce 3%-25% lexical disagreement; otherwise report failed calibration and allow one global development-only grid revision. H2 needs a nondegenerate development recovery interval; an all-success or all-unparseable grid is not evidence for a zero mechanism.

The four controls use the preselected 64 test worlds. No-query identity decodes the same input once per noise and scores both role labels. Query-only uses the main sigma and 16 seeds. Source-only recoverability uses zero answer latents once and eight high-noise draws. Sentence answers use the original template source clauses, a corresponding declared parser and their own development sigma calibration.

Auxiliary geometry-to-error analysis uses world-grouped four-fold regularized logistic regression, with hyperparameters fixed on development. Compare probability scores with and without boundary features; include missing-search indicators rather than inventing radii. Explain this as post-recovery prediction when residual norms are included. Natural-data and training protocols remain reserved extensions.

The tokenizer merges the answer's final period with the trailer newline when they are encoded together (token 13 becomes 627 in the supplied example). Preserve the canonical complete prefix+answer IDs and append separately tokenized fixed trailer IDs, then truncate only the trailer at the DiT block boundary. This token-level concatenation preserves the scored answer across E1 and E2; it is recorded rather than silently changing the answer window.

Sentence-format controls preserve all 64 predefined worlds. Their value edits can span multiple tokens after moving a name to sentence-initial position; they are a separately labeled format/word-span noise control, not part of single-token headline effects or targeted boundary search. A tokenizer-only audit found 52 of 256 development/control query layouts fail the record's single-token constraint under sentence formatting. Retain these worlds in the sentence noise diagnostic; its parser scores complete field values. Any saved confidence for this supplementary format is first-changed-token confidence, not a span aggregate.

Source-present destruction uses a zero answer replacement once and eight independent Gaussian answer replacements with coordinate standard deviation 4.0. This is outside ordinary local support and is labeled as a conditional recoverability diagnostic.

## Development amendment: one noise-grid refinement

The initial 64-world calibration (10,240 readouts at `d4a4b0a`) has 2.009% token disagreement at sigma=0.32 and 43.794% at 0.64, with no original point in the required 3%-25% range. Invoke the single allowed global development refinement: add [0.36,0.40,0.44,0.48,0.52,0.56,0.60] using the same eight paired seeds and all 64 worlds. Reuse the original grid's records. Select the nearest lexical 10% point from the union without reading role contrasts. No test model outputs have been accessed.

## H1 test freeze

The union of original and once-refined development scales selects sigma_star=0.4 (8.181% paired-clean answer-token disagreement, nearest 10%). The development cohort has 64/64 paired-clean worlds. Freeze the original 256 test worlds, scales [0.2,0.4,0.8,1.6], 16 seeds, primary point 0.4 and the preselected 128-world search subset. Keep all 128 worlds for PGD as well as ray unless the pre-test development profile demonstrates an impractical resource cost. The optimizer settings remain the supplied defaults. Development search validation uses one prespecified world per domain without selecting on task-role differences.
