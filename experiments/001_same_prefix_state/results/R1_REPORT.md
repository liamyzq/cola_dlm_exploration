# R1: released-checkpoint capability and inference parity

The fixed release-fixture capability subset completed successfully at commit `699dacde51720e02c34012b3ca0b57500ce94a48`, using the pinned official native inference and scorer. All 256 distinct task/index pairs are present. Eight native records are reused from the exact-condition paired smoke at `a97cf2c45b02adf27a7771d7365125ab4e2bbbe9`; the remaining 248 are new generations. [Metrics and artifact paths](r1_official_capability_v1.json).

| Task | Correct | Accuracy | Descriptive item-level 95% Wilson interval |
| --- | --- | --- | --- |
| LAMBADA | 63/128 | 49.22% | 40.71% to 57.78% |
| SQUAD | 43/128 | 33.59% | 26.00% to 42.15% |

These are fixed, ID-selected release fixtures, not a random full-benchmark reproduction. The intervals describe item-level uncertainty; they do not account for all source-document clustering or establish the published benchmark percentage. Native inference takes 902.46 summed worker seconds over the 256 records, including reused samples from the earlier smoke. This sum is not the parallel wall time or an inference-method cost comparison.

## Effective conditions

The checkpoint remains frozen. Use the released 16-step Euler sampler, CFG 7, greedy decoding, repetition penalty 1.1, nominal 32-token allocation, and official PAD/EOS/im_end IDs. The native loop counts the mixed prompt slice toward that allocation and stops on the official special-token policy. Full original prompts are preserved, including the five SQuAD layouts whose total allocation exceeds 512 positions.

LAMBADA is scored by the pinned script's normalized first generated word. SQuAD uses its first-answer-line processing and normalized full-string similarity threshold 1.0 against the supplied gold string. This is the released scorer, not a rewritten multi-reference SQuAD evaluator.

The paired subset passes 8/8 exact output-token comparisons and penalty-aware pause/resume/cache reconstruction. One additional penalty-1.0 control passes. The state engine now saves the complete generated-block decoder history used by the official repetition processor, including the first mixed block's known prompt slice. Raw logits are preserved separately for later KL measurement. The mechanism default remains penalty 1.0.

## Interpretation

The released checkpoint has substantial nonzero competence on these two familiar task formats in the current environment. Together with the paired checks, this supports using the current checkpoint and native state engine for subsequent work. It does not establish general graph-solving competence, and it does not turn the P0 long-route failure into a negative result about latent-state information.

Proceed with bounded route diagnosis and route-independent F/M candidate feasibility. Do not train LoRA or a selector to repair the route task. H1a/H1b/H2/H3 remain unmeasured. The M engineering suite is a separate prerequisite for M scientific sampling.

## Reproduction and provenance

The immutable run configuration is `configs/001_same_prefix_state/r1_official_capability.json` at the recorded commit. The launcher retained exact commands, worker PIDs, configs, raw generated IDs/text, extracted answers, per-sample times, and exit status under the artifact paths in the JSON summary. Prepared inputs come from the pinned official repository's released evaluation fixtures, selected without consulting their published predictions; see [R0](R0_REPORT.md).
