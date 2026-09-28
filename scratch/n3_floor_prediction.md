# N3 generator-voltage-floor rebuild — prediction, written BEFORE the 0.95-floor data exist

Written: 2026-09-27, by Claude Code (AI), at the owner's instruction (notes/ai-prompt-log.md entry
2026-09-27 (d)). Its sha256 is recorded in scratch/n3_floor_prediction.sha256 and printed in the session
transcript before either build starts. No git commit was made (CLAUDE.md §8: Claude runs no git writes).

## What will be run

Two builds with `feasibility/generate_dataset.py` logic, via a new driver `scratch/n3_floor_rebuild.py`.
Both use the committed invocation (data/dataset.manifest.json → run_settings.invocation):
`--n 1500 --mult-lo 1.0 --mult-hi 1.12 --reg-lo 1.0 --reg-hi 1.12 --pf-lo 0.9 --pf-hi 1.15 --dvm 0.025`.
They also use the committed shard layout: 4 RNG shards, seeds 100-103, 375 accepted scenarios each,
mixed modes, `stress="fixed"`, and the N-0 gate at 0.94.

- **Build A (floor 0.94):** `GEN_VM_LO = 0.94`, unchanged. This is a regeneration of the committed build.
- **Build B (floor 0.95):** `GEN_VM_LO = 0.95`. Nothing else changes: same seeds, the N-0 gate still at
  0.94, the N-1 limit still 0.94.

## Quantities (converged N-1 rows, i.e. `outaged_type != "none"` and `converged`)

- **BM** = unconditional boundary mass = share with `0.94 <= min_vm < 0.945`.
- **CBM** = conditional boundary mass = BM / share with `min_vm >= 0.94` (the decisive quantity in
  `notes/preregistration.md`).
- **VR** = violation rate = share with `min_vm < 0.94`.
- **N0S** = share of the 1,500 accepted base cases whose `n0_min_vm` lies in [0.94, 0.945).
- **PASS** = N-0 gate pass rate = accepted / (accepted + rejected).

## Predictions

| # | Quantity | Build A (0.94) | Build B (0.95): point | Build B range | Falsifier |
|---|---|---|---|---|---|
| Q1 | BM | 56.86% (identical to committed; `min_vm` equal row for row) | **33%** | 20-45% | B ≥ 45% |
| Q2 | CBM | 68.90% | **40%** | 28-55% | B ≥ 60% |
| Q3 | VR | 17.48% | **15.5%** | 12-18% | B > 19% or < 10% |
| Q4 | N0S | 67.7% | **35%** | 20-50% | B ≥ 55% |
| Q5 | PASS | ≈ 54% (only a run-log value exists) | **70%** | 55-85% | B < 55% |
| Q6 | Build A reproduces `data/dataset.parquet` | yes, `min_vm` bit-identical on all 280,500 rows | — | — | any row differs by > 1e-9 |

## Basis (disclosed; this is not a blind prediction)

- **The 40-base probe:** a provisional, one-seed, 40-base probe by the round-1 power panelist
  (`/Users/rajansaha/.claude/jobs/484f4ac7/tmp/panel_power/a7.py`). Raising GEN_VM_LO from 0.94 to 0.95
  moved BM 67.3% → 37.0%, VR 18.4% → 15.8% and PASS 56% → 71%. The implied CBM is ≈ 82% → ≈ 44%.
  The probe's 0.94 sample (67.3%) sits above the full build (56.86%), so its relative drop (×0.55) is
  applied to 56.86: about 31%, rounded to a 33% point with a wide range.
- **Mechanism assumed:** under the 0.94 floor, the setpoint of the lowest-scheduled unit (IEEE 76,
  published 0.943) is uniform on [0.94, 0.968], so it lands in the strip about 18% of the time. 13.09% of
  strip rows sit at bus 76 holding its setpoint (`data/dataset.parquet`, verified 2026-09-27). A 0.95
  floor removes that directly. It also lifts neighbouring load-bus minima, because several other
  low-scheduled units (0.952-0.955) are also forced up.
- **Why the strip will not vanish:** the N-0 gate still truncates at 0.94, and load-bus minima can still
  sit just above it. Hence a floor well above 0, not a collapse to the case30 level (7.09%).

## How the result will be read (stated in advance)

- **BM in 20-45% and CBM < 60%:** consistent with the generator voltage floor being a major driver of the
  concentration.
- **BM ≥ 45% or CBM ≥ 60%:** the floor is not the main driver.
- **Build A differs from the committed dataset:** a reproducibility finding, reported as such before any
  A-vs-B comparison.
- No retraining, gate evaluation or escalation numbers are part of this prediction.
