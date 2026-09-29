# New runs report — N2, N1, N4, N6, E12/E13 (2026-09-27)

Facts and numbers only. Every number below is read from the named JSON; key paths are given as
`file → key.path`. Std = population std (ddof=0) over the five committed splits unless stated.
Bus numbering: pandapower 0-based index in code/artifacts; IEEE name = index + 1 (given where used).
No existing file in `data/`, `feasibility/`, `scripts/` was modified. No git writes.

Shared refit (used by N1, N2 missed-case mapping, E12/E13, N4 baseline arm):
`scripts/sts_n1_class_conditional.py` refits the committed M2 configs (`data/tuned_metrics.json`)
on the committed splits and saves cal/test predictions to `data/sts_n1_predictions_long.parquet`.
**Reproduction check: exact.** Worst absolute difference vs `tuned_metrics.json` over q̂, escalation,
missed (at 0.90/0.94/0.97) and MAE, all 10 family×seed fits = 0.0
(`sts_n1_class_conditional.json → reproduction_check.worst_abs_diff`); histgb `n_iter` matches the
committed value for every seed (`fit_info[*].n_iter` vs `n_iter_committed`).

---

## N2 — Q-limit label audit

**Commands**
```
.venv/bin/python scripts/sts_n2_label_audit.py      # replay + re-solve + switch-back, 10 procs
.venv/bin/python scripts/sts_n1_class_conditional.py # (refit predictions for the missed-case mapping)
.venv/bin/python scripts/sts_n2_summary.py          # counts/shares + mapping -> JSON + manifest
```
**Wall time:** audit 1359 s (+12 s RNG replay), summary ~10 s. Machine was shared with other jobs.

**Artifacts:** `data/sts_n2_label_audit.parquet` (one row per audited row: ids, stored / re-solved /
corrected min_vm, gens at limits, inconsistent gen lists, switch-back status and pass history, flip
flags), `data/sts_n2_label_audit.json`, `data/sts_n2_label_audit.manifest.json`,
`data/sts_n2_label_audit.parquet.run.json` (run-side record read by the summary).

**Method (short).** The committed generator RNG was replayed exactly (seeds 100–103 × 375 accepted
scenarios, mixed modes, committed flags, stress fixed, rejected draws included; rejects per shard
370/313/287/317). Every converged row (278,955 N-1 + 1,500 N-0) was re-solved with the pinned
solver. "Inconsistent" = in-service gen with Q ≤ Qmin + 1e-3 Mvar and V < Vset − 1e-3 pu
(absorbing), or Q ≥ Qmax − 1e-3 Mvar and V > Vset + 1e-3 pu (injecting). Correction = outer loop
that holds consistent limited gens as fixed-Q injections and returns inconsistent gens to PV, each
pass solved by the pinned `runpp` (so free gens still switch PV→PQ), until no gen is inconsistent
(cap 30 passes). Cause confirmed in the library source:
`pandapower/pf/run_newton_raphson_pf.py::_run_ac_pf_with_qlims_enforced` converts violators to PQ
and has no PQ→PV step.

**Reproduction check.** 280,455 / 280,455 rows reproduce the stored min_vm **exactly** (max abs diff
0.0; `reproduction.n_reproduced_exact`, `reproduction.max_abs_diff`); replayed N-0 min_vm of all 1,500
scenarios also exact (`reproduction.replay_n0_max_abs_diff` = 0.0).

**Key numbers** (`data/sts_n2_label_audit.json`)
| quantity | value | key |
|---|---|---|
| N-1 rows with ≥1 inconsistent gen | 260,963 / 278,955 (93.6%) | `all_n1_rows.share_any_inconsistent` |
| … absorbing / injecting | 73.9% / 66.3% | `all_n1_rows.share_inconsistent_absorbing` / `_injecting` |
| stored-violation rows with ≥1 inconsistent gen | 46,001 / 48,749 (94.4%) | `stored_violation_rows.share_any_inconsistent` |
| switch-back status (N-1) | 260,962 converged, 17,992 not needed, 1 non-converged, 0 hit cap | `all_n1_rows.corrected_status_counts` |
| rows whose min_vm moves > 1e-3 / > 1e-2 pu | 47,142 / 4,281 | `all_n1_rows.corrected_minus_pinned_min_vm_among_inconsistent.n_abs_gt_1e3` / `_1e2` |
| median change among inconsistent rows | ≈ 0 (3.3e-16 pu) | `...median` |
| flips violation → safe | 4,615 (9.47% of stored violations) | `violation_rate.n_flip_violation_to_safe`, `.share_of_stored_violations_flipping_to_safe` |
| flips safe → violation | 2,162 | `violation_rate.n_flip_safe_to_violation` |
| violation rate stored → corrected | 17.48% (48,749) → 16.60% (46,296) | `violation_rate.stored_rate` / `.corrected_rate` |
| boundary mass [0.94, 0.945) stored → corrected | 56.86% → 56.22% | `violation_rate.stored_boundary_mass_0p94_0p945` / `corrected_...` |
| minimum min_vm stored → corrected | 0.7179 → 0.8077 pu | `violation_rate.stored_min` / `.corrected_min` |
| stored violations below 0.90 pu | 6,879, of which 38 flip to safe | `violation_rate.stored_violations_below_0p90` |
| stored min_vm of the viol→safe flips | median 0.9376; 72% stored above 0.935 | `violation_rate.flip_violation_to_safe_stored_min_vm` |

**Worst case (0.8485 pu; scenario 101000025, line 78 out)** — `worst_case_0p8485`:
re-solve reproduces 0.848543 exactly; inconsistent gens: absorbing 21, 22, 32 (gen 21 at bus index 53
/ IEEE 54), injecting 16. Switch-back converges in 2 passes to **min_vm 0.94507 pu at bus index 26
(IEEE 27)**, i.e. the case **flips to safe** (`flips_to_safe: true`). The corrected value equals the
scenario's own N-0 minimum (0.9450730, `data/miss_mechanism.json → reconstruction.dataset_n0_min_vm`),
so under the corrected solve line 78's outage leaves the minimum voltage unchanged.

**Currently-missed cases mapped onto the audit** (`missed_cases.<fam>@<cov>`; refit predictions,
committed global q̂, summed over 5 seeds):
| operating point | missed (5 seeds) | of which flip to safe | missed rate stored labels | missed rate if labels corrected (no retrain) |
|---|---|---|---|---|
| histgb@0.97 | 404 | 268 (66%) | 0.0083 ± 0.0024 | 0.0046 ± 0.0008 |
| ridge@0.94 | 384 | 120 (31%) | 0.0079 ± 0.0021 | 0.0114 ± 0.0057 |
| histgb@0.90 | 2,284 | 1,212 (53%) | 0.0472 ± 0.0098 | 0.0396 ± 0.0134 |
| ridge@0.90 | 1,436 | 553 (39%) | 0.0296 ± 0.0044 | 0.0291 ± 0.0071 |

Deepest miss under corrected labels at histgb@0.97: 0.8845 pu in seeds 1–3 (seeds 2 and 3 are the
ones whose stored deepest miss was the 0.8485 case), 0.8718 pu in seed 4, 0.9239 pu in seed 0
(`missed_cases.histgb@0.97.per_seed[*].deepest_missed_under_corrected_labels`). Deep misses remain;
the 0.8485 one does not.

**N-0 rows:** 1,400 / 1,500 accepted bases have an inconsistent gen at N-0; 9 would have N-0 min
< 0.94 after correction and so would fail the N-0 gate (`n0_rows.n_corrected_n0_min_below_0p94`).

**What it means.** The pinned solver's one-way PV→PQ switching leaves a generator at a Q limit that
contradicts its voltage in most rows; on most rows this moves min_vm by nothing measurable, but it
flips 4,615 violation labels to safe and 2,162 safe labels to violation, and the paper's worst missed
violation (0.8485 pu) is one of the flips. About two thirds of the histgb@0.97 misses are rows whose
label flips to safe.

**Caveats.** Audit only: dataset not rebuilt, models not retrained. "Missed rate if labels corrected"
applies models trained on stored labels to corrected labels; it is not a corrected-pipeline result.
The switch-back loop is one standard PV/PQ logic; where several consistent solutions exist, a
different switching order could reach another. Rejected N-0 draws were not re-solved, and N-0
features (`vm0_*`) come from the uncorrected solver. The ridge@0.94 corrected-label missed rate rises
because safe→violation flips are certified. 1 row did not converge under switch-back (keeps its stored
label in the corrected rate).

---

## N1 — class-conditional (violation-only) calibration

**Command:** `.venv/bin/python scripts/sts_n1_class_conditional.py` (full refit, 1000 s under shared
load); the summary was then recomputed with the added matched comparison via
`.venv/bin/python scripts/sts_n1_class_conditional.py --from-predictions` (13 s, same predictions).

**Artifacts:** `data/sts_n1_class_conditional.json` (+ `.manifest.json`),
`data/sts_n1_predictions_long.parquet`.

**Reproduction check:** exact (see top).

**Forms computed** (`forms` in the JSON). Flag rule unchanged (pred < 0.94) and takes priority.
- `band_rows`: q_v = ⌈(n_v+1)(1−α)⌉-th smallest of pred − y over the n_v calibration violation rows;
  certify iff pred − q_v ≥ 0.94. (Task's literal construction.)
- `threshold_rows`: τ = same rank over the *predictions* of calibration violation rows; certify iff
  pred > τ. Bounds P(pred > τ | violation) directly.
- `band_groups` / `threshold_groups`: the same on one randomly drawn violation row per calibration
  base case (draw seed 7000 + split seed); n_v ≈ 9.5–9.9k rows, 300 base cases per split, every
  calibration base case has ≥1 violation (`per_seed[*].n_cal_violation_rows/groups`).

**Key numbers** (`summary.<fam>.<form>.<alpha>.<metric>`; mean ± std over 5 splits)
| family, form, α | missed | escalation | certified | full speedup | certify-only speedup | equiv. global cov. |
|---|---|---|---|---|---|---|
| ridge band_rows 0.10 | 0.0000 | 0.749 ± 0.008 | 0.0001 | 1.34 | 1.00 | 0.982 |
| histgb band_rows 0.10 | 0.0024 ± 0.0013 | 0.737 ± 0.038 | 0.091 | 1.36 | 1.10 | 0.982 |
| histgb band_rows ≤0.02 | 0.0000 | 0.828 ± 0.004 | 0.000 | 1.21 | 1.00 | ≥0.9965 |
| ridge threshold_rows 0.10 | 0.102 ± 0.014 | 0.190 ± 0.040 | 0.559 | 5.50 ± 1.20 | 2.28 | 0.738 |
| ridge threshold_rows 0.05 | 0.056 ± 0.009 | 0.366 ± 0.039 | 0.383 | 2.76 ± 0.28 | 1.62 | 0.844 |
| ridge threshold_rows 0.01 | 0.0107 ± 0.0028 | 0.617 ± 0.017 | 0.132 | 1.62 ± 0.04 | 1.15 | 0.934 |
| histgb threshold_rows 0.10 | 0.102 ± 0.007 | 0.100 ± 0.052 | 0.728 | 12.2 ± 4.8 | 3.77 | 0.774 |
| histgb threshold_rows 0.05 | 0.050 ± 0.004 | 0.294 ± 0.044 | 0.534 | 3.45 ± 0.50 | 2.15 | 0.894 |
| histgb threshold_rows 0.01 | 0.0098 ± 0.0026 | 0.612 ± 0.033 | 0.216 | 1.63 ± 0.09 | 1.27 | 0.967 |
| global reference ridge@0.94 | 0.0079 ± 0.0021 | 0.643 ± 0.028 | 0.106 | 1.56 | 1.12 | — |
| global reference histgb@0.97 | 0.0083 ± 0.0024 | 0.637 ± 0.051 | 0.191 | 1.58 | 1.24 | — |

`threshold_rows` realizes missed ≈ α on average; per seed, missed ≤ α in 2–3 of 5 splits
(`n_seeds_missed_le_alpha`), as expected for a marginal (on-average) guarantee. `band_rows`
over-covers heavily: for ridge it certifies essentially nothing at every α.

**Matched missed rate** (`summary.<fam>.matched_missed_vs_global.threshold_rows.<alpha>`): escalation
of the class-conditional gate minus the global gate at the smallest global coverage (0.001 grid) with
test missed ≤ the class-conditional missed rate: ridge −0.0004 to −0.0013, histgb 0.0000 to −0.0017
(magnitudes ≤ 0.0017; a small negative sign is expected because the matched global point is picked
with missed ≤ the class-conditional rate on a 0.001 coverage grid). Every gate here is "certify iff pred ≥ 0.94 + q", so both
calibrations sit on the same (missed, escalation) curve; class-conditional calibration picks a
different point and attaches a missed-rate bound, it does not move the frontier (`matched_missed_note`).

**Exchangeability** (`exchangeability`). Splits are grouped by scenario (base case). The exchangeable
unit is the base case, not the row. The pooled-row forms therefore do not carry the textbook
finite-sample row-level guarantee (rows within a base case are dependent; violation counts per base
vary). The group forms carry the finite-sample marginal guarantee for one randomly chosen violation
row of a new base case with ≥1 violation; the matching test metric is `missed_viol_group_weighted`
(e.g. histgb threshold_groups α=0.01: 0.0088 ± 0.0045; ridge 0.0081 ± 0.0050).

**What it means.** Calibrating on violation rows only gives a missed-rate bound of α on average;
the usable version (threshold on predictions) lands on the same speed/safety curve as the committed
global band, at an operating point chosen by α instead of by coverage.

**Caveats.** Guarantee is marginal over calibration draws, not per split. Speedups use
t_surr measured in this refit under heavy shared CPU load (histgb 0.011–0.018 ms vs committed
~0.002 ms; `fit_info[*].ms_surrogate`); the effect on speedup is below 0.2% because t_solve = 9.14 ms.
Certify-only speedup = flagged cases are also solved (definition in `speedup_definitions`).

---

## N4 — paired 5-seed F1 shuffle control

**Command:** `.venv/bin/python scripts/sts_n4_f1_shuffle.py` — wall 526 s.

**Artifacts:** `data/sts_n4_f1_shuffle.json` (+ `.manifest.json`).

**Design.** Committed M2 config per split (held fixed across arms, as in `check_4_permutation`);
arms: baseline (no F1, from the N1 refit), real F1, F1 permuted across scenarios within each outaged
element (check_4 scheme), permutation seed 12345 + split seed. Paired difference = real − shuffled.

**Reproduction check:** split 0 histgb arms reproduce `data/f1_leakage_audit.json → check_4_permutation`
exactly: baseline 0.0015637634, real 0.0015538985, shuffled 0.0015300137
(`reproduction_vs_check_4`).

**Key numbers** (`summary.<fam>.<metric>`; paired real − shuffled, mean ± std, # splits real lower)
| family | metric | real | shuffled | real − shuffled | real lower |
|---|---|---|---|---|---|
| ridge | MAE | 0.0037576 ± 0.00013 | 0.0037545 ± 0.00013 | +3.1e-6 ± 2.8e-6 | 1/5 |
| histgb | MAE | 0.0015580 ± 0.000092 | 0.0015763 ± 0.000088 | −1.8e-5 ± 2.5e-5 | 4/5 |
| ridge | missed@0.90 | 0.0264 ± 0.0043 | 0.0297 ± 0.0043 | −0.0033 ± 0.0004 | 5/5 |
| ridge | escalation@0.94 | 0.636 ± 0.027 | 0.643 ± 0.028 | −0.0077 ± 0.0055 | 5/5 |
| ridge | escalation@0.97 | 0.735 ± 0.009 | 0.739 ± 0.010 | −0.0036 ± 0.0010 | 5/5 |
| histgb | escalation@0.94 | 0.458 ± 0.035 | 0.468 ± 0.031 | −0.0095 ± 0.0063 | 5/5 |
| histgb | missed@0.97 | 0.0075 ± 0.0019 | 0.0082 ± 0.0007 | −0.0007 ± 0.0013 | 4/5 |
(Other gate metrics in the JSON. Paired means larger than one paired std: ridge MAE (+), ridge
missed@0.90, ridge escalation@0.94 and @0.97, histgb escalation@0.94; all other paired differences are
within one paired std.)

**What it means.** MAE: real vs shuffled F1 differ by less than the paired std for histgb and by a
few 1e-6 (real slightly worse) for ridge — no MAE gain from the scenario-specific F1 values. Four
gate metrics (ridge missed@0.90, ridge escalation@0.94 and @0.97, histgb escalation@0.94) show a small
same-sign paired effect in all five splits (e.g. ridge missed@0.90 lower by 0.33 points with real F1),
but each difference is smaller than the between-split std of the arms (0.0043 for ridge missed@0.90,
0.031–0.035 for histgb escalation@0.94), so under the project's std rule it is not stated as a real
difference. Whether a consistent paired sign should be reported is a call for the owner.

**Caveats.** Hyperparameters held at the committed baseline M2 tags (the ablation's `m2_fixed`
mode), not re-searched with F1. The shuffle keeps each element's F1 marginal, so it tests
scenario-specific information only.

---

## N6 — warm-start solver timing (sensitivity only; pinned config unchanged)

**Command:** `.venv/bin/python scripts/sts_n6_warmstart_timing.py` — wall 78 s. Run twice; the
second run (1-min load average 4.0 at start) is the stored artifact; the first run (load 10.3)
gave cold min 7.50 / median 9.27 ms and warm min 6.40 / median 8.01 ms, i.e. the same to ≤0.03 ms.

**Artifacts:** `data/sts_n6_warmstart_timing.json` (+ `.manifest.json`: CPU Apple M5, numba 0.66.0 on).

**Design.** Committed generator flags, seed 2026, 12 accepted base cases × 186 outages = 2,232
paired solves per config (+1 discarded warm-up base). Cold = pinned (init "dc"); warm = identical
except init "results" with `res_bus` reset to the N-0 solution before each solve (reset not timed in
per-solve numbers; included in sweep times). Order alternates per outage.

**Key numbers** (`per_solve`, `full_sweep_one_base`, `agreement`)
| | cold (pinned) | warm |
|---|---|---|
| per-solve min | 7.53 ms | 6.38 ms |
| per-solve median | 9.25 ms | 7.98 ms |
| full 186-outage sweep, median over 12 bases | 1731 ms | 1492 ms |
| first base sweep | see `full_sweep_one_base.first_base` | |
Median ratio cold/warm ≈ 1.16 per solve and per sweep. All 2,232 pairs converge both ways; min_vm
agrees to ≤ 4e-15 pu; 0 label differences (`agreement`).

**Reproduction / mismatch flag.** This run's cold **min** (7.53 ms) is below the committed
`ms_solver` = 9.14 ms (`data/solve_time.json`), while its cold median (9.25 ms) is close to the
committed median (9.512 ms). The committed number is a min over 400 solves from about 2–3 base cases
drawn by `feasibility/measure_solve.py` with only `--mult-hi 1.12` set (other flags at script
defaults), so the min depends on which contingencies are sampled. This is flagged, not corrected.

**What it means.** Starting each outage from the pre-outage solution cuts solve time by about 14%
(median) without changing any result on this sample.

**Caveats.** Shared machine (other processes present; load averages recorded in the JSON). Warm
start was not audited against the N2 PV/PQ issue (same one-way switching applies).

---

## E12/E13 — conditional coverage under the committed global q̂ (no solves, no new fits)

**Command:** `.venv/bin/python scripts/sts_e12_e13_conditional.py` — wall ~1 s (reads the N1 refit).

**Artifacts:** `data/sts_e12_e13_conditional.json` (+ `.manifest.json`).

**Key numbers** (`summary.<fam>...`; target 0.90; mean ± std over splits)
| | ridge | histgb | key |
|---|---|---|---|
| marginal test coverage | 0.893 ± 0.013 | 0.898 ± 0.010 | `marginal_coverage_090` |
| per-element coverage: min | 0.575 ± 0.016 | 0.557 ± 0.030 | `E12_element.min` |
| per-element coverage: 5th pct | 0.668 ± 0.010 | 0.661 ± 0.023 | `E12_element.p5` |
| share of 186 elements below 0.85 | 0.181 ± 0.006 | 0.235 ± 0.030 | `E12_element.share_below_085` |
| … expected from binomial noise alone if every element were at 0.90 | 0.0024 | 0.0024 | `E12_element.share_below_085_expected_if_exact_target` |
| per-base coverage: min | 0.086 ± 0.025 | 0.094 ± 0.031 | `E13_base_coverage.min` |
| per-base coverage: 5th pct | 0.446 ± 0.197 | 0.829 ± 0.016 | `E13_base_coverage.p5` |
| share of test bases below 0.85 | 0.087 ± 0.015 | 0.087 ± 0.017 | `E13_base_coverage.share_below_085` |
| … binomial-noise expectation | 0.019 | 0.019 | `..._expected_if_exact_target` |
| **share of test bases with ≥1 missed violation at operating point** | **0.077 ± 0.020 (ridge@0.94)** | **0.111 ± 0.026 (histgb@0.97)** | `any_miss_at_operating_point.share_of_test_bases_with_ge1_miss` |
| same at 0.90 | 0.225 ± 0.036 | 0.471 ± 0.047 | `any_miss.0.9...` |
| max misses in one base at operating point | 11.8 ± 2.1 | 13.2 ± 6.4 | `any_miss_at_operating_point.max_misses_in_one_base` |

Each test split has 300 base cases (186 rows each) and every one of them contains ≥1 violation
(`per_seed[*].n_test_bases_with_violation` = 300), so the "among violating bases" share equals the
plain share. Elements have 291–300 test rows each. Lowest-coverage elements per split are listed in
`five_lowest_elements_per_split` (e.g. split 0 ridge: line 67, line 171, line 69, line 66, line 14).

**What it means.** The 90% band holds on average but not per element or per base case: about a fifth
of outaged elements sit below 0.85 coverage, roughly 75–100× the share binomial noise would give, and
some base cases have under 10% coverage. At the operating points, about 1 in 13 (ridge@0.94) and
1 in 9 (histgb@0.97) test base cases contain at least one certified violation.

**Caveats.** Labels are the stored (uncorrected) labels; see N2. Per-base coverage over 186 rows is
noisy and rows within a base are dependent, so the binomial reference is a floor, not an exact null.

---

## Files written
- Scripts: `scripts/sts_n2_label_audit.py`, `scripts/sts_n2_summary.py`,
  `scripts/sts_n1_class_conditional.py`, `scripts/sts_n4_f1_shuffle.py`,
  `scripts/sts_n6_warmstart_timing.py`, `scripts/sts_e12_e13_conditional.py`.
- Data (each with `.manifest.json`): `data/sts_n2_label_audit.{parquet,json}` (+ `.parquet.run.json`),
  `data/sts_n1_class_conditional.json`, `data/sts_n1_predictions_long.parquet`,
  `data/sts_n4_f1_shuffle.json`, `data/sts_n6_warmstart_timing.json`,
  `data/sts_e12_e13_conditional.json`.
