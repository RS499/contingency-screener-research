# N11 result — N-2 coverage, Mondrian calibration, floor dose-response, and four descriptive parts

## Prompt and provenance

- **Prompt:** `scratch/run_prompt_n11.md` (prompt section), chained after N10 in-session on the Mac mini,
  2026-09-30/10-01 UTC. Owner rules for problems were added mid-run (`notes/ai-prompt-log.md` entry (l)).
- **Report only.** No decision taken, no `.tex` edited, no git write.
  - The only existing files changed are appends to `notes/ai-prompt-log.md` and `notes/overnight_status.md`.
- **Numbers.** Every number below is read from the JSON files named here. Recompute from them; do not quote
  this file.

## Step 0 — Order and environment

- `scratch/n10_result.md` existed, so N10 was not re-run.
- Python 3.13.11; pandapower 3.5.4, numpy 2.3.5, pandas 2.3.3, scikit-learn 1.7.2, pyarrow 21.0.0, numba 0.66.0.
  All match N9.
- git HEAD `af7dcba`.

## Step 1 — Pre-registration

- `scratch/n11_decision_rule.md` is a byte-for-byte copy of the draft committed in `af7dcba`
  (2026-09-30T18:17:59-04:00).
- **sha256:** `4a0e48d47d1c1b8a053dedd6036977c60ede4957dbcb6f542356552a64f0775d`, recorded
  2026-09-30T23:54:42Z, before any N11 computation.
- The hash was re-verified in code before each of the three verdicts. It never failed.

## Verdicts

| Verdict | Result | Numbers |
|---|---|---|
| **COVERAGE-HOLDS-N2** (Part 1, primary) | **NO**, coverage does not hold under N-2 | Histgb at 0.90: N-2 coverage 0.8346 ± 0.0181 vs threshold 0.90 − max(0.0181, 0.0173) = 0.8819; shortfall 0.047. N-1 coverage on the same splits 0.8981 ± 0.0173 |
| **MONDRIAN-BEATS-STATIC** (Part 6) | **NO** | Histgb, held-out, rule B: gate catch 98.24 ± 1.43% vs static at the Mondrian k_B 98.07 ± 1.12%; gap 0.17 pp is not > STD 1.43 pp |
| **FLOOR-DOSE-RESPONSE** (Part 3) | **YES** | BM(0.96) 19.91% < BM(0.95) 32.95% − 5 pp; and \|BM(0.93) 58.07% − BM(0.94) 56.86%\| = 1.21 ≤ 5 pp (stored labels) |

## Part 7 — Solver re-timing (Step 2; descriptive)

- **Script and output:** `scratch/n11_timing.py` (N6 logic, new output path) → `data/sts_n11_timing.json`.
- **Load rule:** waited 180 s; 1-min load 1.93 at start.
- **Hardware:** this run is an **Apple M4** (Mac mini). The committed `data/solve_time.json` and the dataset
  manifests record an Apple M5.

| | min (ms) | median (ms) |
|---|---|---|
| cold per solve (pinned) | 8.96 | 11.09 |
| warm per solve | 7.53 | 9.53 |
| committed `solve_time.json` (M5) | 9.14 | 9.512 |
| N6 cold / warm (M5) | 7.53 / 6.38 | 9.25 / 7.98 |

- **186-outage sweep median:** cold 2,082 ms, warm 1,804 ms.
- **Cold vs warm:** 2,232 pairs; max |Δ min_vm| 4.3e-15; 0 label differences.

## Part 4 — Classical screen on corrected labels (Step 3; descriptive)

- **Script and output:** `scratch/n11_classical.py` → `data/sts_n11_classical.json`.
- **Check:** on stored labels it reproduces `data/classical_screen_metrics.json` exactly (max diff 0).
- **D94 corrected, target 0.90:**
  - MAE 3.68 ± 0.06 mV; R² 0.135 ± 0.007;
  - escalation 90.7 ± 1.1%; missed 1.83 ± 0.57%;
  - speedup A 1.10 ± 0.01; speedup B 1.04 ± 0.01.
- **Stored labels, for reference:** MAE 3.77 mV; R² 0.117; escalation 92.0%; missed 1.07%; speedup A 1.09.
- **Table-1-style row:** `classical (linearized) & 3.7±0.1 & 0.14±0.01 & 90.7±1.1 & 1.83±0.57 & 1.10±0.01`.

## Part 1 — N-1 → N-2 coverage (Step 4; primary verdict above)

- **Build:** `scratch/n11_n2_build.py` → `data/sts_n11_n2_rows.{parquet,json}`.
  - Replay exact: 1,500 D94 bases.
  - Pairs: 50 per base, seed 20261001, so 75,000 rows.
  - Pinned nonconverged: 79 (0.105%), kept and marked. Corrected failures among converged: 1. Rows used: 74,920.
  - N-2 corrected violation rate 30.0%. Adjacent pairs: 3.33%.
- **Evaluation:** `scratch/n11_n2_eval.py` → `data/sts_n11_n2.json`.
  - All 10 (split, family) refits reproduce N5 N-1 test escalation and missed at 0.90 exactly.
  - Two-hot encoding: 0 missing columns.

| Family | Point | N-2 coverage | N-1 coverage | N-2 missed | Missed ≤ 1% (of 5) | N-2 escalation | Speedup A / B |
|---|---|---|---|---|---|---|---|
| histgb | 0.90 | 0.8346 ± 0.0181 | 0.8981 ± 0.0173 | 3.95 ± 1.06% | 0 | 23.0 ± 2.5% | 4.38 / 1.94 |
| histgb | held-out (0.960 ± 0.011) | 0.9169 ± 0.0247 | 0.9591 ± 0.0192 | 1.64 ± 0.91% | 1 | 43.3 ± 6.9% | 2.38 / 1.40 |
| ridge | 0.90 | 0.6113 ± 0.0204 | 0.8889 ± 0.0160 | 11.67 ± 0.80% | 0 | 17.5 ± 2.0% | 5.77 / 2.34 |
| ridge | held-out (0.936 ± 0.010) | 0.7192 ± 0.0211 | 0.9315 ± 0.0090 | 7.46 ± 0.86% | 0 | 28.9 ± 3.0% | 3.50 / 1.85 |

- **Coverage by adjacency** (histgb, 0.90): adjacent pairs 0.818 ± 0.025; non-adjacent 0.835 ± 0.018.

## Part 6 — Mondrian calibration vs static (Step 5; verdict above)

- **Script and output:** `scratch/n11_mondrian.py` → `data/sts_n11_mondrian.json`.
- **Global-q check:** the global-q refit reproduces the N5 held-out numbers in every split.
- **Fallback:** all 186 elements had ≥ 20 cal rows in every split, so the global fallback was never used.

| Family | Gate | Escalation | Missed | ≤ 1% (of 5) | Speedup B | Gate catch | Static catch (k_B) |
|---|---|---|---|---|---|---|---|
| histgb | Mondrian | 37.0 ± 7.1% | 1.76 ± 1.43% | 3 | 1.93 ± 0.24 | 98.24 ± 1.43 | 98.07 ± 1.12 |
| histgb | global (N5) | 50.2% | 1.51% | — | 1.55 | 98.49 | 98.82 |
| ridge | Mondrian | 47.3 ± 2.6% | 2.29 ± 0.49% | 0 | 1.43 ± 0.04 | 97.71 ± 0.49 | 99.15 ± 0.43 |

## Part 2 — Small networks on corrected labels (Step 6; descriptive)

- **Relabel:** `scratch/n11_relabel_net.py` (the N10 driver with the network as an argument) →
  `data/sts_n11_relabel_<net>.*`.
- **Evaluation:** `scratch/n11_smallnets.py` → `data/sts_n11_smallnets.json`.
- **case39 is excluded from the evaluation** (see the interpretations below). Its relabel facts are still
  reported.

| Network | Replay | Failed rows | Flips v→s / s→v | VR stored → corrected | BM stored → corrected |
|---|---|---|---|---|---|
| case30_thermal | exact (8,050 draws) | 0 | 8 / 0 | 15.40 → 15.38% | 7.09 → 7.10% |
| case39 | exact (2,092 draws) | **728 (1.09%) > 0.5%: stopped** | 52 / 0 (settled rows) | 20.74 → 19.99% | 4.43 → 4.44% |
| case24_ieee_rts | exact (8,348 draws) | 28 (0.05%) | 6,988 / 1,422 | 58.06 → 47.88% | 20.70 → 20.94% |

### case39 failure facts

- **307 at the 30-iteration cap.**
  - 296 are stuck with the same inconsistent-generator count every outer iteration (period 1: not oscillating,
    not changing state).
  - 8 are period-2 oscillations; 3 are neither.
- **421 nonconverged:** 394 (93.6%) fail at the first switch-back solve.
- **Concentration:** trafo 10 alone accounts for 437 failures. 81% of failed rows were stored violations.

### Gate, histgb

| Network | Point | Escalation | Missed | ≤ 1% | Speedup A / B | Gate catch vs static (k_B) |
|---|---|---|---|---|---|---|
| case30_thermal | held-out (0.972) | 6.2 ± 2.8% | 0.63 ± 0.31% | 4/5 | 19.34 / 4.76 | 99.37 vs 84.09 (gate higher) |
| case30_thermal | 0.97 | 4.6 ± 0.4% | 0.66 ± 0.17% | 5/5 | 21.60 / 5.06 | 99.34 vs 80.53 (gate higher) |
| case30_thermal | 0.90 | 2.0 ± 0.3% | 2.48 ± 0.32% | 0/5 | 48.51 / 5.82 | 97.52 vs 75.07 (gate higher) |
| case24_ieee_rts | held-out (0.886) | 16.9 ± 1.1% | 0.98 ± 0.18% | 2/5 | 5.93 / 1.54 | 99.02 vs 92.48 (gate higher) |
| case24_ieee_rts | 0.90 | 18.5 ± 1.9% | 0.84 ± 0.32% | 4/5 | 5.44 / 1.50 | 99.16 vs 93.16 (gate higher) |

- **First target with mean missed < 1%:** case30_thermal histgb 0.96, ridge 0.98; case24_ieee_rts 0.90 for both.
- **case30 abstract numbers on corrected labels:** histgb at 0.97 = escalation 4.6%, missed 0.66%, speedup A
  21.60. The first crossing is 0.96.
- **Cross-network ρ·q̂ points** on corrected labels: 72 points (case118, case_illinois200, case30_thermal,
  case24_ieee_rts), in `data/sts_n11_smallnets.json` → `cross_points`.

## Part 3 — Floor dose-response (Step 7; verdict above)

- **Builds:** `scratch/n11_floor_build.py` → `data/sts_n11_floor093.*`, `data/sts_n11_floor096.*`.
- **Relabels:** `scratch/n11_relabel_floor.py` → `data/sts_n11_floor09{3,6}_relabel.*`. Every check passes.
  - 0.93: 0 failed rows.
  - 0.96: 1 failed row, which is that build's deepest stored row (0.694 pu).
- **Verdict:** `scratch/n11_dose_response.py` → `data/sts_n11_dose_response.json`.

| Floor | BM stored | CBM stored | VR stored | BM corrected | VR corrected | vs hashed prediction (stored) |
|---|---|---|---|---|---|---|
| 0.93 | 58.07 | 70.20 | 17.28 | 56.42 | 17.66 | BM 55 [50-62] in; CBM 67 [62-73] in; VR 17.5 [15.5-19.5] in |
| 0.94 (D94) | 56.86 | 68.90 | 17.48 | 56.22 | 16.60 | — |
| 0.95 (D95a) | 32.95 | 39.23 | 16.01 | 28.64 | 14.99 | — |
| 0.96 | 19.91 | 23.28 | 14.46 | 15.75 | 13.43 | BM 20 [8-30] in; CBM 24 [10-36] in; VR 15.0 [12-17.5] in |

- **Corrected labels** (reported only): both verdict clauses also hold.
- **N-0 gate pass:** 0.93 23.9%; 0.96 82.1%.
- **One build per floor:** seeds 100-103 for each, with no error bars across builds.

## Part 5 — The gate on D95b and D95c (Step 8; descriptive)

- **Script and output:** `scratch/n11_gate_095bc.py` (N5 protocol, full search) → `data/sts_n11_gate_095bc.json`.

| Build | Escalation | Missed (per split) | Speedup B | Gate catch vs static | N5 SAFER / FASTER (replication of N5 rule, not a new verdict) |
|---|---|---|---|---|---|
| D95a (N5) | 33.2% | 1.12% | 2.16 | 98.88 vs 97.94 | no / no |
| D95b | 35.2 ± 5.0% | 0.92 ± 0.30% (0.81/1.14/1.27/0.97/0.40) | 2.04 ± 0.19 | 99.08 vs 98.53 | no (3/5) / no (clause 1 yes, clause 2 tie) |
| D95c | 34.5 ± 14.4% | 2.13 ± 1.39% (2.16/3.94/0.61/3.40/0.55) | 2.21 ± 0.51 | 97.87 vs 97.70 | no (2/5) / no (clause 1 yes, clause 2 tie) |
| Across 3 builds, ddof=0 [ddof=1] | 34.30 ± 0.83 [1.02]% | 1.39 ± 0.53 [0.65]% | 2.136 ± 0.073 [0.089] | 98.61 ± 0.53 vs 98.06 ± 0.35 | — |

## Interpretations and deviations

1. **Interpretation** (owner-chosen, consistent with owner rule 1/2):
   - §0's 0.5% failure ceiling is applied **per dataset**. case39 is excluded from the Part 2 evaluation.
   - The iteration cap was not raised and case39 was not rerun.
2. **Deviation (code fix)** (owner rule 3), `scratch/n11_n2_eval.py`:
   - The first run stopped at its own pre-verdict check: seed 2 ridge did not reproduce N5 exactly.
   - Cause: N-1 and N-2 rows were predicted as one stacked matrix, which changes a linear model's BLAS
     blocking.
   - Fix: the same fitted model predicts them separately.
   - No method in the hashed rule changed. No verdict had been computed before the fix.
3. **Implementation notes,** fixed before the affected computations:
   - The small-network relabel switches only helper sgens (case24_ieee_rts has 22 own sgens), as in N10.
   - The floor-build relabel takes the floor as an argument; N9's driver hardcoded 0.95.
4. **Timing hardware:** this run is M4, while the committed timings are M5. Recorded, not corrected.
5. **Code style:**
   - `scratch/n11_timing.py` keeps three generator expressions, copied verbatim from the committed N6 script.
   - The other N11 scripts use list comprehensions.
6. **Pre-hash work:** no step was skipped. N11 scripts were written while N10 was computing, before the N11
   hash; no N11 computation ran before the hash.

## Files written

- **scratch:**
  - `n11_decision_rule.{md,sha256}`
  - `n11_timing.py`, `n11_classical.py`, `n11_n2_build.py`, `n11_n2_eval.py`, `n11_mondrian.py`
  - `n11_relabel_net.py`, `n11_smallnets.py`
  - `n11_floor_build.py`, `n11_relabel_floor.py`, `n11_dose_response.py`
  - `n11_gate_095bc.py`, `n11_result.md`
  - git-ignored logs
  - intermediate shard/chunk dirs, not for commit: `n11_n2_shards/`, `n11_relabel_*_chunks/`,
    `n11_floor_shards_*/`, `n11_relabel_floor09*_shards/`
- **data,** each with a manifest:
  - `sts_n11_timing.json`, `sts_n11_classical.json`
  - `sts_n11_n2_rows.{parquet,json}`, `sts_n11_n2.json`, `sts_n11_mondrian.json`
  - `sts_n11_relabel_{case30_thermal,case39,case24_ieee_rts}.{parquet,json}`, `sts_n11_smallnets.json`
  - `sts_n11_floor093.{parquet,json}`, `sts_n11_floor093_relabel.{parquet,json}`
  - `sts_n11_floor096.{parquet,json}`, `sts_n11_floor096_relabel.{parquet,json}`
  - `sts_n11_dose_response.json`, `sts_n11_gate_095bc.json`
