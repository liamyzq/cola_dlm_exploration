# Research Progress

## Current state

Idea `001_same_prefix_state` is running P0 capability calibration. The [English protocol](experiments/001_same_prefix_state/PROTOCOL.md) preserves the user's staged study of same-prefix latent states. The first model is the released CoLa checkpoint, fully frozen; native noise resampling proposes alternatives to the last complete generated block.

Source revision: `7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c`. Checkpoint revision: `c1eafdd9cfd8064aeb917d569ef70a075b353eed`. Nebula GPUs 5-8 are authorized. Environment and weights are ready. The 32-example engineering suite passed on GPUs 5-8; no scientific result for H1-H3 exists yet.

## Research question

H1 asks whether exact same-token states under tight decoder KL have reproducible continuation-value variation. H2 asks whether independently evaluated selection improves over the reference. H3 asks whether a low-cost selector beats ordinary sampling under full compute accounting. Advance through the protocol's evidence gates; a failed gate must retain the distinction between task limitations and evidence about the hypotheses.

## Next actions

1. Completed: native-parity state engine, paired noise, and 32/32 remote engineering checks (001-p0-engineering-v1).
2. Running: the two predefined route difficulties, each with 128 graphs and four samples, on GPUs 5-8 from frozen commit 3b1fb15 (001-p0-capability-v2). The full 32-example state-engine suite already passed.
3. Run the 128-graph untrained pilot, then independent confirmation and downstream stages when their gates are supported.

## Active work

The four P0 workers run easy then hard calibration at `/home/mlw0719/cola_dlm_exploration_storage/runs/001_same_prefix_state/001-p0-capability-v2-gpu{5,6,7,8}`. GPT-5.6 Luna (max) monitors their terminal status. The main agent will analyze complete graph-level outcomes and capability gates. No H1/H2 rollout measurement has been launched.
