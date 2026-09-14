# Bounded Branch-M task-value development probe

R2 has no successful non-Copy reference routes. The active protocol explicitly
allows a bounded exploration because an all-zero reference reward does not
exclude a beneficial alternative. This probe tests that remaining possibility;
it does not initiate the large R5 confirmation or use the cache diagnostic's
unused budget. The F distribution study and its endpoint remain unchanged.

## Fixed inputs and budget

Use all eight observed eligible first-mixed-block prefixes from the R2 Branch
cell. They are two noise repetitions on four underlying graphs, with original
task IDs 7, 11, 24, and 28. Selection reads only the public-trunk prefix condition,
not any post-anchor reward. The committed manifest retains the exact prefix IDs,
original reference seed, graph, source experiment, and source commit.

Replay the original first block and require exact agreement with its saved IDs.
Use M with eta=0.03, epsilon=0.01, K at most two, and at most 32 native proposals
per root. Preserve known prompt latents and all emitted IDs. These settings were
already selected in M feasibility without task rewards. No reward-based retry,
new reference search, or additional root is allowed.

For each accepted set, use four A and four B future noises paired across candidates
within a split and independent across splits. Generate 32 tokens per future.
The four selected graphs' canonical valid answers contain 18-27 tokens in total,
so this continuation window covers their remaining route content. It is a new
short diagnostic horizon, not a claim to repeat the R2 128-token budget.

The cap is eight roots, 256 proposals, and 128 future trajectories. Reference-only
fallbacks are retained and charged. Every trajectory, including text after the
first answer terminator, retains its actual compute cost. Run only on a permitted
GPU once its current confirmation worker has completed.

## Endpoint and stopping decision

Use the existing public directed-road, endpoint, waypoint, no-repeat and parse
scorer. Compute H_reward and choose-on-A/evaluate-on-B G with reference-first
ties. Cluster both repetitions and all suffixes by their underlying graph;
there are only four independent graph groups. Preserve all signed estimates.

This is a development headroom probe. If it observes no useful conditional
reward, report that bounded floor and do not expand the probe or train. An
all-zero bootstrap is not a useful population zero bound, and the small study
cannot exclude every practical gain. If credible headroom appears, freeze a
separate R5 confirmation design using the specified practical gain and variance,
with fresh topology-disjoint task data; do not silently repurpose these roots.
No equal-cost H3 claim follows from selecting a latent state on A and evaluating
it on B. A later utility study would also have to retain valid probe answers.
