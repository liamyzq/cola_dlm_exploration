# Bounded route diagnosis: first three cells

Generation commit `8e2ab3f`; all three workers completed with all 64 required
(task, repeat) observations. Matched-full is still running and will be added
before the R2 stage is closed. See [compact results](r2_first_three_v1.json).

| Cell | Complete success | Parseable | First edge correct | Eligible M | Eligible F |
| --- | --- | --- | --- | --- | --- |
| Copy | 3/64 | 44/64 | 59/64 | 52/64 | 3/64 |
| Chain | 0/64 | 40/64 | 2/64 | 7/64 | 0/64 |
| Branch | 0/64 | 34/64 | 6/64 | 8/64 | 0/64 |

Copy usually starts along the supplied chain but rarely sustains all 10-12
towns. Chain and Branch struggle before the first completed generated block.
No Branch sample reaches its first branch after a correct common trunk, so
these outputs do not diagnose the choice between the valid and bypass arms.
They provide no successful native F reward roots for either cell.

These cells use the same two-word naming convention and one concise format-
matched demonstration, but change multiple task requirements. Do not attribute
the differences to one causal factor or claim that a particular demonstration
change caused improvement over P0. Copy is a format/length control and is not
a task-value candidate cohort under the active protocol.

Intervals in the compact results cluster renamed isomorphic graph instances.
Copy and Chain have only three underlying chain lengths, limiting inference
beyond the tested layouts. All-zero reward bootstraps for Chain/Branch are
marked degenerate; a [0, 0] resampling interval is not a population zero bound.
No inference about H1a follows from this reward floor.

Summed generation worker times were 932.85 s, 929.31 s and 931.37 s. All requested
128-token horizons were block-rounded and charged, including generation after
the first answer terminator. The largest allocated context across the complete
static R2 data was 464 positions; no task was excluded for length.

Decision: continue the independent natural F distribution study. Preserve M
prefix opportunities without treating them as accepted candidate pairs or
useful reward control. Finish Matched-full before choosing any bounded task-
value follow-up; do not train to rescue the route task.
