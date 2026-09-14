# P0 progress and capability results

## Scope

The first study tests whether exact same-token CoLa states, under a tight current-block decoder KL constraint, have reproducible differences in continuation value. No H1/H2 measurement or selector experiment has run yet.

## Engineering evidence

The pinned official checkpoint is integrated with a resumable state engine. The 32-example `001-p0-engineering-v1` suite passed on nebula GPUs 5-8 at implementation commit `f9ecd7f2becfe104aeb455895461680d89ab848b`. It covers exact official token parity, pause/resume, identity replay, chronological cache reconstruction, candidate AB/BA ordering, invariant past tokens, and paired future noise. Identity replay produced zero KL on these examples.

The native proposal and split-statistic code exists. The end-to-end mechanism measurement runner remains an uncommitted development draft and has not produced scientific results. Engineering success does not establish candidate acceptance, future-value heterogeneity, or selection improvement.

## Route capability calibration

Frozen implementation: `3b1fb15cf78f234660169f5fcb1686d61286217b`. Each difficulty contains 128 distinct graph topologies and four complete samples per graph. The four GPU workers completed 1,024 samples with exit status zero. Observed wall elapsed time was 45 minutes 54 seconds; summed measured sample execution time was 10,521.81 GPU-worker seconds, approximately 2.92 worker-hours, excluding setup/loading and wrapper overhead.

| Metric | Target | Easy | Hard |
| --- | --- | --- | --- |
| Parseable answer | >=90% | 422/512 (82.42%) | 331/512 (64.65%) |
| Eligible intervention root | >=80% | 0/512 | 0/512 |
| Complete route success | 15-75% | 0/512 | 0/512 |
| Graph with at least one success in four samples | >=50% | 0/128 | 0/128 |

The raw metric summaries are [easy](p0_capability_easy_v2.json) and [hard](p0_capability_hard_v2.json). [Matched examples](p0_examples_v2.json) preserve prompts, graph constraints, and raw outputs.

In the easy task's graph 0, the common trunk begins Meadow Brook -> Golden Field -> Birch Point -> Maple Hill -> Oak Harbor. The model instead returned Meadow Brook -> Willow Creek -> Green Wood -> Birch Point -> Green Lake. This fails listed-road, required-waypoint, and final-destination conditions. Other outputs emit short routes followed by new invented task examples. Thus low reward is not explained solely by the route-format parser.

Eligibility exclusions were: easy, 40 samples with no complete generated block in the planned trunk layout and 472 with an incorrect trunk; hard, 28 with no complete block, 482 with an incorrect trunk, and 2 already beyond the branch. No samples were retried to improve coverage.

## Task-design and protocol qualifications

The initial single-letter, 7-10-town trunks were too short under the official tokenizer: only 2/16 checked layouts admitted the required complete generated block after the partial prompt block. Before observing calibration rewards, the task was revised to meaningful two-word town names, a 10-12-town trunk, and 17-22 total towns. The revised structural scorer passed 128 graph checks and 14/16 tokenizer layout checks.

Demonstrations remain short routes while the tested routes are longer and use multiword town names. The observed short-answer pattern is consistent with a demonstration-length or task-complexity mismatch; the present experiment does not isolate these explanations. It does not establish that CoLa is incapable of every simpler route task.

The implementation fixes the intervention position before sampling using the demonstrated trunk's tokenization, then validates the actual prefix. This is conservative for alternate spacing and may not be the retrospective last possible boundary. The primary candidate same-token constraint has not been relaxed. The missing-boundary cases should be addressed in a subsequent explicitly versioned task specification; they do not explain the much larger wrong-trunk population.

The answer terminates at the first newline after nonempty output. Raw fixed-horizon text is retained for audit and uniform execution accounting; text after that terminator is not part of the returned answer.

## Main blocker and next decision

The binding blocker is task identifiability: there are no eligible roots and no successful routes under either calibrated setup. H and G are unmeasured, not zero. Candidate coverage under epsilon=0.01 and the value of latent interventions remain unknown. A direct pilot or critic training on this corpus would not answer the research question.

The supplied plan permits a separate frozen-VAE/DiT-LoRA task-capability branch. It has been identified as a fallback, but no adaptation training has started and no adapted checkpoint exists. Before interpreting adaptation as necessary, a bounded diagnostic should distinguish the short demonstration format from actual road-following difficulty. Any revised task or adapted model must be versioned and labeled separately; preserve these released-checkpoint results.

P1-P5 remain incomplete. The overall goal is active. There is no evidence yet for or against H1, H2, or H3, no trained selector, and no cost-matched method comparison.
