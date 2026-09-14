# Native state implementation for R3/R4

## Mixed-block extension

The proposal implementation identifies M from the first block and a nonzero prompt remainder. It restores the common pre-block state, perturbs only generated-position noise, preserves the known noise entries, and verifies exact known prompt latent equality after native denoising. Accepted candidates preserve all emitted IDs and the original raw decoder KL limits. F remains a separate cohort. Default candidate count is two.

Raw latent displacement and its bf16 DiT input displacement are reported. If both newly computed DiT and decoder cache segments are bitwise identical to an existing candidate, the alternative is not counted as effective diversity. Cache lists contain batch members, each concatenated over time; comparison examines the last 16 positions after an identical common prefix. It does not patch any cache. This checks the actual finite-precision continuation state instead of equating a small fp32 latent difference with useful diversity.

## Validation allocation

`tests/check_mixed_candidates.py` covers prompt remainders 1-15 and one aligned F control, with native 16-step CFG-7 inference and penalty 1.0. Each case checks identity rejection, known noise, known latent and zero-timestep conditioning at every DiT evaluation in the proposal path, exact accepted tokens, prompt positions, cache reconstruction, AB/BA order, and paired future noise. Up to two nonidentity native proposals are used per case; acceptance frequency on these engineering prompts is not scientific coverage. The full suite must pass before M scientific sampling.

`tests/check_token_distribution.py` passed on nebula: the H1a kernel matches explicit one-hot features, identity candidates give zero, swapping independent candidate ordering across A/B preserves negative estimates, EOS padding is consistent, and source-document cluster aggregation retains the correct root-weighted mean. This is statistical implementation evidence, not an H1a result.

## Natural input preparation

[Corpus manifest](data/natural_corpus_v1.json) records the pinned SQuAD article-context source, article IDs, selection rule, and word-boundary cropping. Of 442 articles, 427 qualify. The first 128 selected articles are development sources; the next 128 are confirmation sources. They are disjoint by article title. Prompts contain 128-241 tokens with no appended question, answer, or padding. Raw prepared inputs live at `/home/mlw0719/cola_dlm_exploration_storage/datasets/001_natural_continuation_v1`.

F uses the first fully generated block; M uses the first mixed block when available. Natural continuation treats EOS/im_end as termination; newline alone does not terminate an unrestricted passage. The exact root/proposal budgets, eta selection, and future-noise domains will be committed in the R3/R4 execution configurations before those runs.
