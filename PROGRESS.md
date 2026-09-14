# Research Progress

## Current state

P0 capability calibration completed for idea `001_same_prefix_state`. All 32 engineering examples passed, but both route difficulties produced zero success and zero eligible roots across 512 samples each. See [the P0 report](experiments/001_same_prefix_state/results/P0_REPORT.md) for full counts, matched raw examples, and protocol qualifications.

## Observation and interpretation

The released checkpoint often generates short routes and then invents new task examples. The binding blocker is obtaining a task distribution with meaningful success variation and eligible prefixes. Current evidence does not isolate demonstration-length mismatch from road-following difficulty. It provides no H1/H2/H3 result; those quantities are unmeasured.

The initial single-letter layout was revised before reward calibration because it lacked sufficient token length. The current task uses two-word town names and 10-12-town trunks. Some planned layouts still lack a complete intervention block; most exclusions are incorrect trunks rather than that layout issue.

## Next actions

1. Preserve and explain the completed released-checkpoint calibration; no equivalent jobs remain active.
2. Use a bounded, separately versioned capability diagnostic to distinguish prompt-format mismatch from graph-solving difficulty before committing to model adaptation.
3. If needed, follow the plan's frozen-VAE/DiT-LoRA capability branch, clearly labeling all adapted-checkpoint results. No LoRA training has started.
4. After capability and proposal gates pass, run P1 and independent P2, followed by the conditional selector, cost, and text-transfer stages.

The overall goal remains active; P1-P5 are incomplete. The end-to-end mechanism runner and proposal-calibration configuration are development drafts, not validated results.
