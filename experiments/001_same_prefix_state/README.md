# 001_same_prefix_state: Future information beyond emitted tokens

Status: R0-R3 and the F distribution pilot are complete. Independent F confirmation is running. The pilot does not establish H1a; task-value and utility claims remain unresolved.

Can naturally generated continuous states preserve exactly the same emitted tokens and closely preserve the decoder readout while changing future text distributions or task value? The released CoLa model remains frozen. The [active English protocol](PROTOCOL.md) separates H1a distribution effects, H1b task-value variation, H2 independent selection gain, and H3 equal-cost utility.

The [supplied P0 audit](reviews/P0_review_no_training_plan_v2.md) and [adoption record](reviews/ADOPTION.md) explain the redesign. The [original protocol](archive/PROTOCOL_P0_v1.md) is historical; its default training progression no longer governs new work. LoRA and selector training are outside the current plan.

## Evidence and reusable implementation

- [R0 saved-route audit](results/R0_REPORT.md) reproduces all 1,024 historical records and separates possible M anchors from causal F eligibility. [P0 outcomes](results/P0_REPORT.md) remain available.
- [R1 capability](results/R1_REPORT.md) records 63/128 LAMBADA and 43/128 SQuAD successes under pinned official conditions, with eight exact paired inference and replay checks.
- [R2 route diagnosis](results/R2_REPORT.md) records 3/64 Copy successes and zero successes in Chain, Branch, and Matched-full. Branch's short common trunk also lacks a canonical predecision F layout.
- [R3 feasibility](results/R3_REPORT.md) establishes 32 strict native pairs in each F/M cohort at eta=0.03 and epsilon=0.01. [Raw same-prefix examples](results/SAME_PREFIX_EXAMPLES.md) retain token IDs, latent displacement, KL, and artifact paths.
- [R4 pilot](results/R4_PILOT_REPORT.md) reports a zero-centered independent A/B endpoint on 32 F pairs. Coupled suffix differences alone do not establish a distribution difference.

The native-parity and cache-replay suite passed all 32 original examples. The M/F suite passed all 16 prompt remainders, and the A/B runner passed pairing, independence, and identity-null checks. These are execution results; scientific claims use the substantive studies above.

## Remaining decisions

Complete the [locked independent F confirmation](R4_EXECUTION.md) on 128 fixed source documents. Its endpoint and sample inclusion remain unchanged. Run the [bounded Branch-M development value probe](R5_DEVELOPMENT_PROBE.md) on the eight existing eligible roots after GPUs become free. Cache localization uses the same preselected eight development pairs only if positive mechanism evidence activates it.

R5 confirmation and the cost study depend on useful reward evidence. Record unactivated stages explicitly; do not expand floor measurements or introduce training. The study's final report must distinguish candidate feasibility, H1a, H1b/H2, and H3. See [the experiment ledger](../results.tsv), [job history](../../jobs/jobs.jsonl), and [current progress](../../PROGRESS.md).

## Runtime

Source revision: `7d1daeea1455a6cb9e23ddd4f06b8a2e59e63a8c`.
Checkpoint revision: `c1eafdd9cfd8064aeb917d569ef70a075b353eed`.

Use nebula GPUs 5-8 only. Primary files are in `/home/mlw0719/cola_dlm_exploration`; large artifacts are under `/home/mlw0719/cola_dlm_exploration_storage/runs/001_same_prefix_state/`. Formal runs use committed detached worktrees. GPT-5.6 Luna at max reasoning monitors long waits; the main agent owns implementation and scientific decisions.
