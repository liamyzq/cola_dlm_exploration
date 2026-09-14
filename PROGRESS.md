# Research Progress

## Current state

The research workspace is initialized for CoLA DLM and related continuous DLM ideas. Nebula is the primary workspace and artifact store; GitHub holds tracked code and research records. There is no integrated model, accepted runnable baseline, or experimental result yet.

## Current understanding

The organizational decision is to share implementation across persistent idea directories and use short-lived branches for changes. This is a workspace decision, not a scientific result. No method hypothesis has been tested.

## Open questions

- Which exact CoLA paper, official implementation revision, and checkpoint define the initial baseline?
- Which related continuous DLM models share a useful comparison protocol?
- Which dataset, evaluator, primary metric, and compute budget should govern the first comparison?

## Next actions

1. Establish the source and protocol in `experiments/000_baseline/README.md`, including upstream provenance and the first meaningful runnable baseline.
2. Define the first idea in its own directory using `docs/idea-template.md`; identify the smallest comparison that distinguishes its hypothesis.
3. Integrate the shared baseline and nebula execution procedure, perform a targeted remote smoke test, then commit the formal-run configuration before execution.

No jobs are active for this project and no formal experiments have been recorded at initialization.
