# N16 decision rule — gate speed across generator-setpoint floors (follow-up to N11 Part 3)

Methods skeleton drafted by Claude Code; predictions and verdict written by Rajan Saha.

- **Status:** filled by owner on Oct 30. In force once committed and pushed.
  - The N16 run checks that the commit is on origin and records this file's sha256 before any N16
    computation.
- **Registered after N11 and N13.** N16 is a follow-up, not one of the paper's pre-registered results.

## 0. Known before the owner sections were filled in

- **Dataset-level numbers, all four rebuilt floors:** BM, CBM and VR in `data/sts_n13_floor.json` (N13
  FLOOR_DOSE_RESPONSE).
- **Gate results on D94 and D95a:** produced under this exact protocol, at target 0.90 and at the held-out
  target: `data/sts_n13_gate_D94.json`, `data/sts_n13_gate_D95a.json`.
- **Also known to the owner when predicting:** the N5 FASTER result (speedup B higher at 0.95 than at 0.94).
- **Not known:** any gate result on D93 or D96. No gate has been run on either build, old or rebuilt.
- **So** the 0.94 and 0.95 rows of the Predictions table restate known values. Only the 0.93 and 0.96 rows
  are predictions.

## 1. Data

| Floor (generator setpoint lower bound) | Build | Dataset | Build record |
|---|---|---|---|
| 0.93 | D93 | `data/sts_n13_D93.parquet` | `data/sts_n13_build_D93.json` |
| 0.94 | D94 | `data/sts_n13_D94.parquet` | `data/sts_n13_build_D94.json` |
| 0.95 | D95a | `data/sts_n13_D95a.parquet` | `data/sts_n13_build_D95a.json` |
| 0.96 | D96 | `data/sts_n13_D96.parquet` | `data/sts_n13_build_D96.json` |

- **The four builds.** N13 rebuilt them with the corrected (switch-back) solver; all four passed N13
  checks 2-6.
  - N16 uses only these four.
  - D95b and D95c are not part of N16, and the D95b gate is never substituted for D95a.
- **Labels.** Each dataset's own min_vm; violation = min_vm < 0.94.
  - Loaded by `n5_gate_eval.load_relabeled(path, "")` → `make_splits.load_dataset` (drops
    converged = False rows), as in `scratch/n13_gate.py`.
- **Limit.** L = 0.94 pu on every build. The floor changes only the generator setpoints.
- **Splits.** `make_splits(groups, seed)`, seeds 0-4, on each build's own scenario groups.
  - The builds have different base cases, so split k of one build shares no base case with split k of
    another.
  - Every comparison across floors is therefore unpaired.

## 2. Model and protocol (per build, per split)

- **The N5 protocol, unchanged:** `scratch/n5_gate_eval.py` `run_seed`, as used by N11 Part 5
  (`scratch/n11_gate_095bc.py`) and N13 arm S (`scratch/n13_gate.py`). It runs:
  - the full `scripts/tune_surrogates.py` search (15 ridge, 26 histgb candidates), with inner split
    `make_splits(train groups, 1000 + seed)`;
  - M2 selection: maximum inner avoided share subject to inner missed ≤ 1%, ties broken by MAE;
  - a refit on the full train split, a one-sided split-conformal q̂ on cal, and evaluation on test.
- **Families:** histgb primary; ridge reported.
- **Two operating points** per build, split and family:
  1. **Fixed target 0.90**, the same on every build, so floors are compared at one band-setting rule.
  2. **Held-out target:** M2's `inner_cov_at` (0.70-0.99 grid), chosen without reading test. If None, that
     split's held-out point is recorded as missing (`scratch/n5_decision_rule.md` §6).
- **Gate:** certify if pred − q̂ ≥ 0.94; flag if pred < 0.94; otherwise escalate.
- **Rule B speedup** (flagged rows are also solved):
  - speedup B = n·t_solve / (n·t_surr + (n_esc + n_flag)·t_solve);
  - t_solve = `ms_solver` from `data/solve_time.json`. It must equal the `ms_solver` in
    `data/sts_n13_gate_D94.json` and `data/sts_n13_gate_D95a.json`; otherwise stop and report;
  - t_surr = the refit model's measured per-row predict time in this run.
- **Std:** population std (ddof=0) over the 5 splits. A difference counts only if it exceeds the larger of
  the two stds.
- **Speedup B and solve share are one axis** (speedup B ≈ 1 / solve share), so they are not independent
  evidence.
- **Escalation and flag share are reported separately.** Escalation tracks BM; flag share tracks VR.

## 3. Metrics (per floor, per split, per family, at both operating points)

| Metric | Definition |
|---|---|
| BM | share of the split's test rows with true min_vm in [0.94, 0.945) |
| VR | share of the split's test rows with true min_vm < 0.94 |
| target | 0.90, or the held-out target |
| q̂ | the band width, pu |
| escalation | share of test rows escalated |
| flag share | share of test rows flagged |
| solve share | escalation + flag share (`solve_share_B`) |
| missed | certified true violations / true violations, test rows |
| catch | 1 − missed |
| speedup B | §2 |

- **Summaries per floor:** mean ± std over the 5 splits for every metric.
- **Splits with missed ≤ 1%:** counted out of 5 at each operating point. A missing held-out point counts as
  not ≤ 1%.
- **Also written, no verdict:** speedup A, empirical coverage, static catch at k_B, M1/M2 tags and configs,
  MAE, R².
- **Dataset-level check:** BM and VR over all converged rows must equal `data/sts_n13_floor.json`; a
  mismatch stops the run.

## 4. Run

- **Script:** a new `scratch/n16_floorgate.py`, a thin wrapper like `scratch/n11_gate_095bc.py`.
  - It imports `n5_gate_eval.run_seed` and `load_relabeled` unchanged; N_LINE = 173; no existing file is
    edited.
- **Family isolation:**
  - a ridge failure (for example "SVD did not converge") does not void histgb results;
  - histgb is computed and reported for that split, and the ridge failure is logged as a deviation;
  - if `run_seed` cannot produce histgb alone without editing `n5_gate_eval.py`, the run stops before any
    D93/D96 computation and reports this.
- **D94 and D95a are not re-searched.** Their results are taken unchanged from
  `data/sts_n13_gate_D94.json` and `data/sts_n13_gate_D95a.json`. Their per-split BM and VR come from the
  same test rows.
- **Step 1, reproduction check, before anything else.** Rerun D94 split 0 alone with OMP_NUM_THREADS=4.
  It must exactly match `data/sts_n13_gate_D94.json` split 0, for both families, in:
  - the M1/M2 tags and the held-out target;
  - test MAE;
  - q̂, escalation, flag share, missed, k_B and static catch at k_B, at every target.

  Speedups are excluded (t_surr is wall-clock time). If anything differs, stop; D93 and D96 are not run.
- **Step 2.** D93 and D96, 5 splits each, in parallel; OMP_NUM_THREADS per job recorded.
- **If a histgb run crashes:**
  - it is not retried, and settings are not changed;
  - that build's histgb results are "not run";
  - any verdict that needs them is "not computable".
- **Outputs:**
  - `data/sts_n16_floorgate.json` and `data/sts_n16_verdicts.json`, each with this file's sha256, the
    commit timestamp, the run start time and a manifest;
  - `scratch/n16_result.md`: one table (floor × metrics, mean ± std), the verdict and deviations. No
    interpretation beyond this rule.

## Predictions (owner)

Family: histgb. Target 0.90. Speedup B, rule B.

| Floor | Speedup B: point | Speedup B: range | Escalation: point | Escalation: range |
|---|---|---|---|---|
| 0.93 | 2.4 | 2.1-2.7 | 24.9% | 21-29% |
| 0.94 | known: 2.45 ± 0.20 | — | known: 24.23 ± 3.35% | — |
| 0.95 | known: [from D95a file] | — | known: [from D95a file] | — |
| 0.96 | 4.5 | 3.3-5.5 | 8.4% | 5-14% |

Held-out target: not predicted; reported descriptively.

**Rule used.**
- Escalation scales with boundary mass at the D94 ratio: escalation = (24.23 / 54.75) × BM = 0.443 × BM.
- Flag share scales with the violation rate at the D94 ratio (1.01 × VR; D94 flag ≈ 16.5%, derived from
  speedup B 2.45).
- Speedup B ≈ 1 / (escalation + flag + 0.001).

**Main assumption:** the share of near-limit cases the 0.90 band escalates stays at the D94 fraction.

**Sanity check against the known 0.95 build:** the rule predicts escalation ≈ 14.8% and speedup B ≈ 3.3;

## Verdict (owner)

**Primary verdict: - (c) Safety. mean missed(0.96) − mean missed(0.94) ≤ max(the two stds), at target 0.90.**

- **(d)** escalation(0.94) − escalation(0.96) > max(the two stds), at target 0.90, histgb.
  - Holds → N16 supports "lower boundary mass reduces escalations" on the same grid at a fixed
    band-setting rule.
  - Fails → reported as "not supported".
  - This alone decides the N16 result.

**Secondary checks.** Each is computed with the same std rule and reported as holds / does not hold.
None of them changes the primary verdict.

- **(a) Speed, fixed target.** speedup B(0.96) − speedup B(0.94) > max(the two stds), at target 0.90.
  - Reported together with the flag-share change, so the speed gain from fewer flags (lower VR) is shown
    separately from the gain from fewer escalations.
- **(c) Safety.** mean missed(0.96) − mean missed(0.94) ≤ max(the two stds), at target 0.90 
- **(e) Speed, held-out target.** speedup B(0.96) − speedup B(0.94) > max(the two stds), at the held-out
  target.
  - The held-out target is retuned per build, so this comparison is not at a fixed band.


## 5. Commitments

- **Fixed after hashing:** no extra floors, builds, seeds, splits, targets, families or std definitions.
- **Reported either way:** every result and the verdict, including results against the predictions.
- **Deviations:** logged in `notes/overnight_status.md` and `scratch/n16_result.md`. Any verdict touched by
  a deviation is marked "with deviation".
- **Unchanged:** the paper's pre-registered results and the N5-N14 verdicts stay as reported.