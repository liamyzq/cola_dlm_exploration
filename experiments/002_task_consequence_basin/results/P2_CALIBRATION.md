# H2 development calibration and frozen test

The predeclared nearest-10% lexical-disagreement rule selects noise fraction **0.5**, native restart index **8**, at CFG=1. This is a development selection; no task-role contrasts enter the decision.

| Noise fraction | Real token disagreement | Any-field damage | Unparseable fields |
| --- | ---: | ---: | ---: |
| 0.125 | 0.000% | 0.000% | 0.000% |
| 0.25 | 0.000% | 0.000% | 0.000% |
| 0.5 | 15.205% | 60.840% | 43.408% |
| 0.75 | 74.851% | 99.902% | 96.777% |

All 64 fixed development worlds reconstruct under both questions. Four completed workers produce 20,480 real/rotated readouts, including 4,096 real recoveries. The clean low-noise stages and nearly unparseable highest stage are reported as observed; the intermediate stage supplies the identifiable working interval.

Freeze the original 256-world test, all four native restart stages, eight noise seeds and four rotations. The primary point is 0.5 at CFG=1. CFG=7 repeats the same grid on the preselected 64 controls worlds and remains supplementary. Configuration files are `p2_test_recovery.json` and `p2_cfg7_control.json`.

Raw development artifacts: `002-p2-dev-recovery-v1-gpu5` through `gpu8` in the nebula idea-002 run base, implementation `d4a4b0a7e5cf9309397e6e03c99bc74cb8e30421`. Compact calibration: [p2_calibration_v1.json](p2_calibration_v1.json).
