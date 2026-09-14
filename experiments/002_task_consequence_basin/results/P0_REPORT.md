# P0: Measurement interface and fixed synthetic cohorts

P0 passes at commit `4393c75c32abe426bd1259312be7c7a59156d051` on nebula GPU 6. The 16 independent smoke worlds yield 32/32 exact clean query anchors, 16/16 paired-clean worlds, and 64/64 exact target-reencoding endpoints. This establishes measurement feasibility on the smoke cohort, not task protection or residual selectivity. See [the measured summary](p0_v1.json).

All 80 explicit parser cases pass. Repeated and AB/BA full readout, causal prefix logits, target-encoding prefix latents, finite input gradients, and full-precision finite-difference directions pass. Cached versus complete readout preserves greedy IDs but differs by up to 1.5 in raw logits. Cache acceleration is not accepted as numerically equivalent; the scientific runner retains fresh complete readout. The full-precision gradient finite-difference check has maximum relative error 0.00195. The native full-noise first-block Euler result exactly matches the established shared state engine. Recovery keeps the known prefix fixed and is identical at zero remaining time. Haar channel rotation preserves the residual Gram matrix to relative error 5.96e-8.

The generator produced 16 smoke, 64 development and 256 held-out test worlds without consulting model outputs. Sixty-two names from the prescribed pool occur in tokenizer-eligible worlds. The fixed boundary and control flags select 128 and 64 test worlds respectively. [Tokenizer audit](tokenizer_audit_v1.json) records six rejected numeric candidates and forty rejected single-token edits. Test model outputs have not been read.

Joint tokenization of the trailer changed the answer's terminal period token. The generator therefore preserves canonical prefix+answer IDs and appends separately tokenized fixed trailer IDs before block truncation. This documented token-boundary decision keeps E1/E2 answer anchors identical. Deterministic PRNG candidate ordering replaces the proposed SHA256 sort under the user's project instructions.

P0 takes 16.94 seconds after worker initialization begins and peaks at 9.59 GB allocated GPU memory; this includes 97 encodes, 288 decoder calls, and the recorded recovery/parity checks. It is not a full-study runtime estimate. Proceed to development-only lexical calibration and freeze the test settings before measuring task-role effects.

Raw artifacts: `/home/mlw0719/cola_dlm_exploration_storage/runs/002_task_consequence_basin/002-p0-v1`. The launch manifest records the command and PID 2223799; exit status is 0.
