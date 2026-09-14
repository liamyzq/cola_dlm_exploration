# Research Progress

## Current state

Idea `001_same_prefix_state` is in P0 implementation. The [English protocol](experiments/001_same_prefix_state/PROTOCOL.md) preserves the user's staged study of same-prefix latent states. The first model is the released CoLa checkpoint, fully frozen; native noise resampling proposes alternatives to the last complete generated block.

Source revision: `7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c`. Checkpoint revision: `c1eafdd9cfd8064aeb917d569ef70a075b353eed`. Nebula GPUs 5-8 are authorized. Environment and weights are being prepared; no model experiment result exists yet.

## Research question

H1 asks whether exact same-token states under tight decoder KL have reproducible continuation-value variation. H2 asks whether independently evaluated selection improves over the reference. H3 asks whether a low-cost selector beats ordinary sampling under full compute accounting. Advance through the protocol's evidence gates; a failed gate must retain the distinction between task limitations and evidence about the hypotheses.

## Next actions

1. Implement pre-block snapshots, native candidate replay, and explicit paired future noise; establish identity and cache invariants on remote engineering examples.
2. Calibrate the two predefined route difficulties on 128 graphs with four samples each; lock the task, horizon, and proposal settings before formal testing.
3. Run the 128-graph untrained pilot, then independent confirmation and downstream stages when their gates are supported.
