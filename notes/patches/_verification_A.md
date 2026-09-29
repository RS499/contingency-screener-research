# Number verification — spec set A (`_index_A.md`), 2026-09-27

Verifier: independent recompute (second key). Interpreter `.venv/bin/python` only. Nothing in `report/` or `data/`
was written; no git writes. Scratch scripts live in the job tmp dir (not in the repo).

Conventions used here
- Std = population std (ddof = 0) over the 5 splits unless stated. Std rule: a gap counts only if it exceeds the
  larger of the two seed stds (CLAUDE.md §8).
- **Route**: wherever possible I recomputed from row-level data rather than re-reading the spec's key:
  `data/sts_n1_predictions_long.parquet` (per-seed cal/test predictions; I rebuilt q̂ with the `gate_eval.calibrate_qhat`
  rule and re-ran the gate), `data/sts_n2_label_audit.parquet` (row-level N2), `data/dataset.parquet`,
  `data/unconditioned_base.parquet`, `data/tuned_metrics.json` per-seed sweeps, `data/netstudy2/*` raw points/records,
  `data/drift_*_long.parquet` counts, `data/classical_predictions.parquet`, per-seed arrays inside the N1/N4/E12 JSONs.
  My stored-label rebuild from the N1 predictions reproduces `tuned_metrics.json` / `tradeoff_curve_v2.json` exactly
  (e.g. histgb@0.97 missed 0.8322 ± 0.2447, per split 1.162/0.798/1.032/0.699/0.470), so that parquet is a sound
  independent path.
- Cross-occurrence rule: consistency is **complete** if every other `.tex` occurrence of a cited quantity that must
  change in step (value, label convention, or wording the spec changes) is listed in the spec's §7 or anchors, directly
  or via a named spec that lists it. Unchanged verbatim reprints are noted, not counted against the spec.
- Items the spec itself marks **do not print** (P-003 panel sample, P-007 floor-0.95 probe, E12-E13 cluster-SE) are
  reported but excluded from the sign-off test.

UNTRACKED sources used (owner must commit before any of these numbers is printed):
`data/sts_n2_label_audit.{json,parquet,manifest.json,parquet.run.json}`, `data/sts_n1_class_conditional.json`,
`data/sts_n1_predictions_long.parquet`, `data/sts_dataset_facts.json`, `data/sts_dataset_facts_b.json`,
`data/sts_limit_sweep.json`, `data/sts_crossnet_scatter.json`, `data/sts_e12_e13_conditional.json`,
`data/sts_n4_f1_shuffle.json`, `data/sts_n6_warmstart_timing.json`, `data/sts_matched_escalation.json`, and their
`scripts/sts_*.py`. Also: `notes/preregistration.md` and `data/archive_clip/dataset.parquet` are **git-ignored**
(`.gitignore` l.23 `notes/`, l.20 `data/archive_clip/`) — they cannot be committed without an ignore change / `-f`.
Every other source named below is tracked.

## Summary

Counts are per table row (one row = one printed value or one tightly bundled value set from one key; 209 rows).

| Verdict | Rows |
|---|---|
| MATCH | 200 |
| MISMATCH | 3 (P-007 41.2%, E6 k≈119 row, C8 "~10%") |
| ROUNDING | 3 (Top5-1 65.58, E1b 65.58, E8 histgb@0.95 1.47) |
| NOT FOUND | 3 (all "do not print": P-003 panel sample, P-007 floor-0.95 probe, E12-E13 cluster-SE) |
| STD-PASS (claimed comparisons) | 33 |
| STD-FAIL | 23 — none on a claimed comparison; every one is a gap the spec already labels "no difference / tie / do not claim" |

**SIGNED OFF (14):** P-001, P-005, Top5-2d-E5, E1a, E1c, E2, E4, E5b-E15, E9, E10, E11, E12-E13, E14, C13.
(Top5-2d-E5 and E1a are signed off with one non-numeric correction each; see cross-spec notes.)

**REJECTED (7):**
- **P-003** — numbers all MATCH; consistency incomplete: the strip share it changes (56.86 → 56.22) also prints at l.121;
  the violation-rate-derived saturation point 82.64% and ceilings 74.89/82.79% (l.347) are label-dependent and unlisted;
  "all pre-outage voltages above 0.94" at l.107 and l.349 conflicts with its own "9 accepted N-0 bases below 0.94 under
  the corrected solve" and is unlisted.
- **P-007** — printed numbers MATCH (and its 13.09% MISMATCH finding is confirmed), but the supporting figure "41.2% of the
  bus-76 rows" recomputes to **41.4%** (13.094 / 31.616); consistency misses l.107 and l.349, which repeat the "above 0.94"
  imprecision the spec corrects at l.119.
- **Top5-1** — ROUNDING: conditional strip share printed 65.58%; exact value **65.59%** (the key 65.5823 was computed from
  2-dp-rounded percentages 28.83 / 43.96; row counts give 65.594%).
- **E1b** — same ROUNDING (65.58 → 65.59).
- **E6** — MISMATCH: histgb escalation-budget static capture "k≈119: 98.61 ± 0.30". 0.63679 × 186 = 118.44 → nearest
  k = 118 → **98.57 ± 0.31**; k = 119 is a ceiling, while the same table rounds the flags-solved budgets to nearest
  (166.38 → 166, 150.45 → 150). Conclusion unchanged (gate 99.17 still ahead: 0.60 > 0.31).
- **E8** — ROUNDING: histgb certify-only speedup at 0.95 printed 1.47; with the formula the spec states
  (t_solve / (t_surr + (1 − c) t_solve), per-seed `ms_surrogate`) it is **1.46** (1.46496); 1.47 comes from 1/(1 − c)
  (t_surr = 0), which is what `scratch/confirm_missing.py` computes. Spec's stated formula and its source disagree.
  Consistency also misses l.199 and l.292, which print net speedups (2.04×, 3.29×) that its rule "each should name
  which accounting it uses" covers.
- **C8** — MISMATCH: "ridge better [than persistence], by ~10%": MAE 3.754 vs 4.246 (×10⁻³) is **11.6%** lower
  (persistence 13.1% higher). Also: the 74% row's "ridge lower" contradicts `data/sts_matched_escalation.json`, whose
  own rule marks 74% **incomplete** (ridge reaches it on 4 splits); the 20%, 63.7% and 64.3% rows are not in that
  artifact (grid is 25–75% in integer steps) — the committed artifact the spec asks for does not yet carry them.
  All eleven table cells themselves recompute exactly.

Cross-spec notes (not blocking)
- Top5-2d-E5 §7 says the E12-E13 base-case statistic exists "only at histgb 0.97 and ridge 0.97"; the artifact has
  `any_miss` at 0.9 / 0.94 / 0.97 for **both** families (ridge@0.94 = 7.7 ± 2.0% is in E12-E13 §5). Fix the sentence.
- E1a §5 says 55.5 / 55.51% is "not reproducible from git (no tracked source)". It is: tracked
  `data/clip_artifact.json → clip_era.boundary_0p94_to_0p945_pct` = 55.51 (also `cited_in_sts.boundary_before_fix_pct`),
  and I recomputed 55.512% from the ignored `data/archive_clip/dataset.parquet`, whose sha256 equals the tracked
  `clip_era.input_sha256`. Cite that key.
- E1a §7 "persistence has MAE only ~10% worse than ridge" → 13.1% worse (same issue as C8; §7, so not scored).
- Index "N6 warm 16% faster": the median time ratio is 1.16 (throughput +16%); the time saving is 13.7%
  (9.25 → 7.98 ms). Say which. N6 also recorded 5/15-min load averages 48.7 / 86.9 before the run (machine busy) —
  a timing caveat.
- "47.49% of unfiltered bases below 0.94 at N-0" uses the 1,495 converged N-0 bases as denominator (1,500 → 47.33%).
- Top5-1 "61.61% both sides (no key — do not print)": a key now exists, untracked
  `data/sts_dataset_facts_b.json → within_0p005_of_limit.two_sided_open.share_pct` = 61.610; recomputed 61.610%.
- `notes/preregistration.md` P1/P3/falsifier values match the file, but the file is git-ignored; its timestamp
  (2026-09-10T00:40:53Z, equal to the file mtime) is not attested by any commit.

## Full table

Legend: V = verdict (M = MATCH, MM = MISMATCH, R = ROUNDING, NF = NOT FOUND). U = source untracked.

### P-001 — SIGNED OFF (consistency complete: l.292, l.303, l.367, Fig. 3 image)
| Value as printed | Source → key | Recomputed (route) | V | Std |
|---|---|---|---|---|
| depth 0.0915 pu | `missed_depth.json` → `families.histgb.pooled.0.97.max` | 0.0915 (predictions → q̂ → certified violations, max 0.94−y; also pooled 0.90 max for both models) | M | n/a |
| bus 0.8485 pu | `miss_mechanism.json` → `reconstruction.recorded_min_vm` | 0.848543 (`dataset.parquet` row 101000025/line 78) | M | n/a |
| gen 21, IEEE 54, Q −194.71 = Q_min, at_min | `miss_mechanism.json` → `saturated_gens…[gen 21]` | −194.7147 = qmin, at_min True, bus 53 (IEEE 54) | M | n/a |
| N-0 Q −10.00 MVAr | same → `q_n0` | −10.0015 | M | n/a |
| setpoint 0.9549 vs 0.8485 (gap 0.106) | `genvm_21` | `dataset.parquet` genvm_21 = 0.954866; gap 0.1063 | M | n/a |
| back-off 0.94507 = N-0 min, IEEE 27 | N2 → `worst_case_0p8485` | N2 parquet row: corrected 0.9450730, argmin idx 26 (IEEE 27), 2 outer iters; dataset n0_min 0.9450730 | M (U) | n/a |
| Q-lims-off 0.9390 @ IEEE 20; Δ 0.0905 | `qlims_off_check.json` | 0.939009, IEEE 20, Δ 0.09047 | M | n/a |
| certified histgb@0.97 in seeds 2, 3 | `qlimit_class.json` per_seed_depth | predictions route: per-seed max depth 0.0359/0.0460/0.0915/0.0915/0.0670 → seeds 2, 3 | M | n/a |
| featured case → 0.9451, safe | N2 `worst_case_0p8485` | N2 parquet: stored_violation True, corrected False | M (U) | n/a |
| 4,615 / 48,749 (9.47%) v→s; 2,162 / 230,206 (0.94%) s→v | N2 `violation_rate` | N2 parquet recount: 4,615, 0.09467; 2,162 / 230,206 = 0.939% | M (U) | n/a |
| corrected deepest miss histgb@0.97 0.0682 (seed 4, 0.8718); ridge@0.94 0.0516 | N2 `missed_cases` | predictions × N2 corrected labels: min 0.87177 (seed 4) / 0.88844 | M (U) | n/a |
| "maximum of the ridge pooled misses at 0.90" (§4) | `missed_depth` | ridge@0.90 pooled max 0.0915 (seed 2) | M | n/a |

### P-003 — REJECTED (consistency incomplete; numbers all MATCH)
| Value | Source → key | Recomputed (route) | V | Std |
|---|---|---|---|---|
| 93.5% (260,963 / 278,955) wrongly pinned | N2 `all_n1_rows.share_any_inconsistent` | N2 parquet: n_absorbing+n_injecting > 0 → 260,963, 0.93550 | M (U) | n/a |
| 4,615 / 48,749 (9.47%) | N2 | as P-001 | M (U) | n/a |
| 2,162 / 230,206 (0.94%) | N2 | 0.9392% | M (U) | n/a |
| violation rate 17.48 → 16.60% | N2 | stored 0.174756, corrected 0.165962 (non-converged row keeps stored label) | M (U) | n/a |
| strip 56.86 → 56.22% | N2 | 0.568629 → 0.562159 (row recount; key 0.562161) — both 56.22 | M (U) | n/a |
| min 0.7179 → 0.8077 | N2 | 0.717941 → 0.807743 | M (U) | n/a |
| 38 of 6,879 < 0.90 flip | N2 | 6,879 / 38 | M (U) | n/a |
| 280,455 re-solved, max diff 0.0 | N2 `reproduction` | parquet 280,455 rows, `repro_abs_diff` max 0.0; stored = `dataset.parquet` min_vm exactly on all 278,955 | M (U) | n/a |
| 1 non-converged row | N2 | `corrected_status` = nonconverged: 1 | M (U) | n/a |
| histgb@0.97 0.83 ± 0.24 → 0.46 ± 0.08 (0.33, 0.56, 0.53, 0.43, 0.46) | N2 `missed_cases` | predictions × corrected labels: 0.4624 ± 0.0786; 0.333/0.558/0.526/0.433/0.463 | M (U) | gap 0.37 > 0.24 **STD-PASS** (claimed) |
| ridge@0.94 0.79 ± 0.21 → 1.14 ± 0.57 (1.63, 0.43, 1.01, 0.69, 1.94; 3/5 > 1%) | N2 | 1.1384 ± 0.5677; 1.631/0.427/1.007/0.688/1.939; 3 of 5 | M (U) | 0.35 < 0.57 STD-FAIL (spec: not claimed) |
| @0.90 histgb 4.72 ± 0.98 → 3.96 ± 1.34; ridge 2.96 ± 0.44 → 2.91 ± 0.71 | N2 | 3.958 ± 1.344; 2.910 ± 0.710 | M (U) | both STD-FAIL (not claimed) |
| 66.3% (268/404), 31.3% (120/384) of misses flip | N2 | 268/404 = 0.6634; 120/384 = 0.3125 | M (U) | n/a |
| 9 accepted N-0 bases < 0.94 corrected | N2 `n0_rows` | N2 parquet N-0 rows: 9 (stored: 0) | M (U) | n/a |
| 0.7179–0.9603, 17.48% | `frozen_poster_numbers_v2.json → dataset_facts` | `dataset.parquet`: 0.717941–0.960311, 17.4756% | M | n/a |
| 0.54% below 0.87 | `sts_dataset_facts.json` | parquet: 1,510 rows, 0.5413% | M (U) | n/a |
| panel sample 10% / 1% / +0.12 | scratch | not re-derived (superseded, do not print) | NF (excluded) | — |
| **Consistency:** listed l.119, 314, 365, l.81, Tables I/II, Fig. 3/4 captions. **Unlisted:** l.121 (56.86 strip); l.347 (82.64% saturation = 1 − violation rate; ceilings 74.89/82.79%); l.107 and l.349 ("all pre-outage … above 0.94", contradicted by 9 corrected N-0 bases). | | | | |

### P-005 — SIGNED OFF (consistency complete: l.81, 231, 281, 349, 388, Table II caption)
| Value | Source → key | Recomputed | V | Std |
|---|---|---|---|---|
| ridge@0.94 0.79 ± 0.21; upper 1.00 | `tradeoff_curve_v2` | per-seed `tuned_metrics` m2 sweep: 0.7935 ± 0.2090 → 1.0025 | M | mean vs 1%: 0.21 ≈ 1.0 std → not resolved (not claimed) |
| histgb@0.97 0.83 ± 0.24; upper 1.08 | same | 0.8322 ± 0.2447 → 1.0769 | M | not resolved (not claimed) |
| esc 64.3 ± 2.8 / 63.7 ± 5.1; 1.56 ± 0.07 / 1.58 ± 0.12 | same | 64.34 ± 2.78 / 63.68 ± 5.12; 1.557 ± 0.068 / 1.579 ± 0.117 | M | esc 0.66 < 5.12 STD-FAIL (spec: no difference) |
| `*_std` keys on all 60 records | `tradeoff_curve_v2.records` | 60 records, all five `_std` keys present | M | — |
| no `fill_between`/`errorbar` | `grep feasibility/paper_hero.py` | no hits | M | — |
| per-split > 1%: ridge 1 of 5, histgb 2 of 5 (§4) | `tuned_metrics` | 1.146 only; 1.162 and 1.032 | M | — |

### P-007 — REJECTED (41.2 → 41.4; consistency misses l.107, l.349)
| Value | Source → key | Recomputed | V | Std |
|---|---|---|---|---|
| GEN_VM_LO = VMIN_LIMIT = 0.94; reject-and-redraw | `feasibility/generate_dataset.py` l.8, l.10, `draw_gen_vm` | read: both 0.94; `while not (GEN_VM_LO <= v <= VMAX_LIMIT)` redraw | M | n/a |
| jitter ±0.025 | `dataset.manifest.json` | invocation `--dvm 0.025`; `max_abs_gen_vm_deviation` 0.024995 | M | n/a |
| 1,016 / 1,500 (67.73%) N-0 min in strip | parquet (no key) | parquet base rows: 1,016, 67.733% | M (no JSON key) | n/a |
| N-0 min 0.94–0.958976, median 0.943358 | `unconditioned_base.json → committed_gated` | parquet: 0.9400000 / 0.943358 / 0.958976 | M | n/a |
| 31.62% of strip rows at IEEE 76 | `sts_dataset_facts.json` | parquet: 31.616% | M (U) | n/a |
| "holding own setpoint" 13.09% (not 31.6%) | parquet | `argmin_bus==75` & \|min_vm − genvm_33\| < 1e-4: 13.094% of strip rows; median offset −0.00274 | M (spec's MISMATCH confirmed) | n/a |
| "41.2% of the bus-76 rows" | parquet | **41.42%** (13.094 / 31.616) | MM | n/a |
| case30 gens all 1.00 pu | `pandapower.networks.case30()` | gen vm_pu [1.0]×5, ext_grid 1.0 | M | n/a |
| case30 7.09% / 15.40% | `case30_thermal_frozen.json` | 7.0862 / 15.3967 | M | n/a |
| floor-0.95 probe 67.3 → 37.0% | scratch | not re-derived (do not print) | NF (excluded) | — |
| **Consistency:** l.121, l.365, l.81, l.388 listed. **Unlisted:** l.107 "all voltages are above a minimum limit" and l.349 "All the pre-outage scenarios are above 0.94 pu" (same "at or above" fix as anchor a). | | | | |

### Top5-1 — REJECTED (ROUNDING 65.58)
| Value | Source → key | Recomputed | V | Std |
|---|---|---|---|---|
| 56.86% strip | `frozen_v2.dataset_facts`; `sts_dataset_facts.json` | parquet 56.8629% | M | n/a |
| 77.6% (216,605 / 278,955) | `sts_dataset_facts.json → n0_persistence` | parquet \|min_vm − base min_vm\| ≤ 0.001: 216,605, 77.649% | M (U) | n/a |
| 28.83% vs 56.86% | `unconditioned_base.json` | `unconditioned_base.parquet`: 28.833% (277,628 rows) | M | n/a |
| conditional 65.58% vs 68.90% | `*.conditional_boundary_pct` | row counts: **65.594%** vs 68.904% | **R** (print 65.59 / 65.6) | n/a |
| quintiles 78.39/81.28/82.36/37.31/4.98 | `quintile_boundary_mass.json` | parquet, bases sorted by N-0 min, 300 per quintile: identical | M | n/a |
| 67.73% | parquet | 1,016/1,500 | M (no key) | n/a |
| case30 7.09% | `case30_thermal_frozen.json` | 7.0862 | M | n/a |
| 61.61% both sides (do not print) | none per spec | parquet 61.610%; key now exists in untracked `sts_dataset_facts_b.json` | M (U) | n/a |
| **Consistency:** l.63, 81, 101, 121, 312, 314, 347, 353, 361, 365, 388 covered. l.323 caption "holds 56.9%" is an unchanged reprint (not counted). Complete. | | | | |

### Top5-2d-E5 — SIGNED OFF (fix §7 note on E12-E13 key coverage)
| Value | Source → key | Recomputed (route: `tuned_metrics` per-seed m2 sweeps; B via `tuning_search` selections → `inner_cov_at`; C via predictions) | V | Std |
|---|---|---|---|---|
| A ridge@0.94 0.79 ± 0.21, 64.3 ± 2.8, cov 94.0 ± 0.7, 1.56 ± 0.07; 1/5 (1.146) | `tradeoff_curve_v2` / `tuned_metrics` | 0.7935 ± 0.2090, 64.34 ± 2.78, 93.95 ± 0.74, 1.557 ± 0.068; 0.601/0.624/1.146/0.918/0.678 | M | — |
| A histgb@0.97 0.83 ± 0.24, 63.7 ± 5.1, 97.0 ± 0.2, 1.58 ± 0.12; 2/5 (1.162, 1.032) | same | 0.8322 ± 0.2447, 63.68 ± 5.12, 96.96 ± 0.25, 1.579 ± 0.117 | M | — |
| A′ ridge@0.95 0.45 ± 0.12, 67.9 ± 2.8, 1.48 ± 0.06; 0/5 | same | 0.4466 ± 0.1224, 67.85 ± 2.84, 1.476 ± 0.062; 0 | M | resolved < 1% (0.57) STD-PASS |
| A′ histgb@0.98 0.30 ± 0.13, 72.0 ± 3.7, 1.39 ± 0.07; 0/5 | same | 0.3045 ± 0.1329, 72.00 ± 3.67, 1.392 ± 0.067; 0 | M | resolved < 1% STD-PASS |
| B histgb targets [0.96,0.97,0.97,0.96,0.96]; 1.15 ± 0.27 (1.61,0.80,1.03,1.05,1.23; 4/5); 59.3 ± 4.0; 1.69 ± 0.12; cov 96.2 ± 0.6 | `tuning_search` × `tuned_metrics` | identical targets; 1.145 ± 0.270; 59.27 ± 4.01; 1.694 ± 0.116; 96.19 ± 0.60 | M | B vs A missed 0.31 > 0.27 **STD-PASS** (claimed); esc 4.4 < 5.1 STD-FAIL (not claimed) |
| B ridge [0.97,0.94,0.96,0.92,0.94]; 0.77 ± 0.78 (0.02,0.62,0.27,2.24,0.68; 1/5); 65.4 ± 8.1; 1.55 ± 0.22; 94.1 ± 2.5 | same | identical; 0.767 ± 0.776; 65.43 ± 8.12; 1.555 ± 0.216; 94.13 ± 2.54 | M | vs A STD-FAIL (not claimed) |
| C histgb threshold_rows α=0.01: 0.98 ± 0.26 (1.41,0.83,0.69,0.86,1.14; 2/5), 61.2 ± 3.3, 1.63 ± 0.09, cert-only 1.27 ± 0.05 | `sts_n1_class_conditional.json` | predictions, τ = ⌈(n_v+1)(1−α)⌉-th cal-violation prediction: 0.984 ± 0.256, 61.20 ± 3.33, 1.634 ± 0.092, 1.275 ± 0.049 | M (U) | vs A: 0.15 < 0.26, 2.5 < 5.1 STD-FAIL (not claimed) |
| C ridge threshold_rows: 1.07 ± 0.28 (1.46,0.95,1.20,1.12,0.62; 3/5), 61.7 ± 1.7, 1.62 ± 0.04, 1.15 ± 0.03 | same | 1.068 ± 0.279; 61.70 ± 1.72; 1.621 ± 0.044; 1.152 ± 0.031 | M (U) | 0.274 < 0.279; 2.64 < 2.78 STD-FAIL (not claimed) |
| C histgb threshold_groups: 0.84 ± 0.46 (1.50,0.98,0.17,0.50,1.06), gw 0.88 ± 0.45, 64.6 ± 5.1, 1.55 ± 0.12 | same | per-seed arrays (random group draw not re-simulated): 0.842 ± 0.464, 0.881 ± 0.451, 64.59 ± 5.12, 1.554 ± 0.119 | M (U) | — |
| C ridge threshold_groups: 0.75 ± 0.46 (0.37,1.21,1.21,0.92,0.07), gw 0.81 ± 0.50, 65.1 ± 5.2, 1.54 ± 0.12 | same | 0.755 ± 0.459, 0.814 ± 0.497, 65.11 ± 5.22, 1.545 ± 0.121 | M (U) | — |
| histgb threshold_rows α=0.10: 10.18 ± 0.74, 2/5 ≤ α | same | 10.176 ± 0.741; 2 splits ≤ 10% | M (U) | — |
| corrected labels A: 0.46 ± 0.08 (0/5), 1.14 ± 0.57 (3/5) | N2 | as P-003 | M (U) | histgb change PASS; ridge change FAIL (as labelled) |
| **Consistency:** l.81, 124, 231, 241–260, 281, 349, 388 — complete. **Correction:** §7 says E12-E13 any-miss keys exist "only at histgb 0.97 and ridge 0.97"; they exist at 0.9/0.94/0.97 for both. | | | | |

### E1a — SIGNED OFF (update 55.51 source to tracked `clip_artifact.json`)
| Value | Source → key | Recomputed | V | Std |
|---|---|---|---|---|
| 77.6% (216,605 of 278,955) | `sts_dataset_facts.json` | parquet 216,605 / 77.649% | M (U) | n/a |
| median \|Δ\| 3.3e-6 | same | 3.3135e-6 | M (U) | n/a |
| 96.3% strip rows from bases < 0.945 | same | 96.265% | M (U) | n/a |
| 93.4% same weakest bus | same | 93.374% | M (U) | n/a |
| 56.86% | `frozen_v2` | 56.863% | M | n/a |
| 55.5 / 55.51% (spec: "no tracked source") | tracked `clip_artifact.json → clip_era.boundary_0p94_to_0p945_pct` 55.51 | ignored `archive_clip/dataset.parquet` (sha256 = tracked `input_sha256`): 55.512% | M | n/a |
| **Consistency:** l.121 (both anchors), l.349 via §7; other 56.86 reprints owned by Top5-1. Complete. | | | | |

### E1b — REJECTED (ROUNDING 65.58)
| Value | Source → key | Recomputed | V | Std |
|---|---|---|---|---|
| quintile ranges 0.94000–0.94119 / 0.94119–0.94256 / 0.94256–0.94427 / 0.94428–0.94652 / 0.94652–0.95898 | `quintile_boundary_mass.json` | parquet (300 bases each, 55.8k rows each): identical | M | n/a |
| strip 78.39/81.28/82.36/37.31/4.98 | same | identical | M | n/a |
| violation 21.54/18.55/17.19/15.88/14.21 | same | identical | M | n/a |
| ρ_s −0.6 / −1.0 | same | scipy spearman −0.6 / −1.0 | M | n/a |
| 28.83% vs 56.86% | `unconditioned_base.json` | 28.833% / 56.863% | M | n/a |
| violations 56.04% vs 17.48% | same | 56.044% / 17.476% | M | n/a |
| conditional 65.58% vs 68.90% | same | **65.594%** / 68.904% | **R** | n/a |
| P1 22% (12–32), P3 66% (60–72), falsifier < 50%, artifact outcome < ~20% and < 50% | `notes/preregistration.md` (git-ignored) | file l.55, 57, 71–73: identical | M (ignored file) | — |
| 47.49% / 277,628 / 5 non-conv | `unconditioned_base.json` | parquet: 710/1,495 = 47.49% (denominator = converged N-0; /1,500 = 47.33%); 277,628; 5 | M (note denominator) | n/a |
| histgb esc 2.8 ± 0.8 vs 59.1 ± 2.5 | `drift_n0_stratum_long.parquet` | n_escalated / n_test at 0.90: 2.85 ± 0.78 vs 59.14 ± 2.52 | M | 56.3 > 2.5 **STD-PASS** |
| histgb missed 8.25 ± 1.33 vs 1.89 ± 0.61 | same | 8.246 ± 1.335 vs 1.885 ± 0.615 | M | 6.36 > 1.33 **STD-PASS** |
| **Consistency:** Top5-1, E10, Fig. 4 caption l.323. Complete. | | | | |

### E1c — SIGNED OFF (all U: `sts_limit_sweep.json`)
| Value | Source → key | Recomputed (predictions; q̂ at 0.90 per seed; gate re-run at each L) | V | Std |
|---|---|---|---|---|
| histgb 30.63 ± 2.51 @0.940 | `sts_limit_sweep.json` | 30.63 ± 2.51 | M (U) | — |
| ridge 49.07 ± 2.66 @0.940 | same | 49.07 ± 2.66 | M (U) | — |
| histgb 0.26–1.77% for L ≤ 0.936 | same | 0.260–1.771 | M (U) | — |
| histgb 5.46 ± 1.25 @0.938; 19.44 ± 3.16 @0.939 | same | identical | M (U) | — |
| ridge ≤ 3.23% only to L = 0.930 (3.23 ± 0.24); 19.60 @0.936 | same | 3.23 ± 0.24 at 0.930, 3.50 at 0.931; 19.60 | M (U) | — |
| ridge max 51.43 @0.941 | same | 51.43 ± 1.98 | M (U) | vs 49.07 ± 2.66: 2.36 < 2.66 STD-FAIL (spec: "not distinguishable") |
| L = 0.950: ridge 1.38 ± 0.33, histgb 1.58 ± 1.19 | same | identical | M (U) | 0.20 < 1.19 STD-FAIL (spec: no difference) |
| 95.71% violations @0.950 | same | 95.708% | M (U) | n/a |
| 86 of 1,500 bases > 0.95 | parquet (no key) | 86 | M (no key) | n/a |
| lower panel ~60% / ~31% @0.94 | same → `boundary_mass_mean` | 60.00 / 31.26 | M (U) | — |
| **Consistency:** l.347, l.365 (anchors); 30.6/49.1 reprints at l.199, 217–218, 231, 248, 255 are the identical numbers (spec §7). Complete. | | | | |

### E2 — SIGNED OFF (U: `sts_crossnet_scatter.json`; raw points are tracked)
| Value | Source → key | Recomputed (from tracked `netstudy2/cross_2a_points.json`, `summary.json` rows) | V | Std |
|---|---|---|---|---|
| 132 pts; r 0.81; log-log 0.92 | `sts_crossnet_scatter.json` | x = BM/0.005·q̂ (0.0 recompute error): 0.8105 / 0.9176 | M | n/a |
| case24-ridge median 0.34; 9/9 < 0.5; without r 0.90 / 0.96 (123 pts) | same | 0.3408; 9 of 9; 0.8956 / 0.9582 | M | — |
| A rel 0.4726, B 0.4933; A abs 0.1163, B 0.1056 (n = 54) | `summary.json → cross_network` | from 54 rows: mean\|rel\| 0.47255 / 0.49325; abs 0.11631 / 0.10561 | M | 0.0107 < 0.210 STD-FAIL (spec: fails) |
| std of abs errors 0.210 / 0.114 | same rows | 0.2097 / 0.1145 | M | — |
| per-cell 2.111 / 0.194 / 0.322 / 0.101 / 0.047 / 0.061 | `cross_comparisons` | 2.1111 / 0.1941 / 0.3215 / 0.1012 / 0.0465 / 0.0608 (9 each) | M | n/a |
| naive prior mean abs 0.1144 | recompute | 0.11439 (n = 54) | M | A vs naive 0.0019 → no difference |
| case24 ridge @0.90 A 0.451 vs 0.217 | `table_at_090` | 0.4511 / 0.2168 | M | — |
| E3 strip 4.43 / 20.70 / 19.33% | `<net>/frozen.json` | 4.431 / 20.7038 / 19.3287 | M | n/a |
| E3 histgb esc @0.90 3.72 ± 0.68 / 17.19 ± 1.37 / 7.84 ± 0.50 | `records` | n_escalated/n_test: identical | M | — |
| E3 histgb speedup 27.8 ± 5.1 / 5.85 ± 0.42 / 12.8 ± 0.8 | same | 27.81 ± 5.14 / 5.85 ± 0.42 / 12.80 ± 0.82 | M | — |
| E3 ridge esc 11.86 / 21.68 / 13.74% | same | 11.86 ± 0.76 / 21.68 ± 1.05 / 13.74 ± 1.52 | M | — |
| t_solve 9.14 imported from case118 | `ms_solver_provenance` | "imported from data/solve_time.json (case118); NOT re-timed" ×3 | M | — |
| **Consistency:** l.353, 355, 365, l.81/101/388 listed. Complete. | | | | |

### E4 — SIGNED OFF
| Value | Source → key | Recomputed (n_missed/n_true_viol, n_escalated/n_test per seed) | V | Std |
|---|---|---|---|---|
| histgb@0.97 5.84 ± 1.25, 0.76 ± 0.20 (5/5), 17.9 ± 3.7× | `case30_thermal_frozen.json` | 5.84 ± 1.25; 0.759 ± 0.201 (0.851/0.771/0.888/0.369/0.916); 17.91 ± 3.71 | M | — |
| histgb@0.96 4.86 ± 0.98, 0.91 ± 0.22 (2/5), 21.5 ± 4.5× | same | 4.86 ± 0.98; 0.909 ± 0.220; 21.46 ± 4.51; crossing key 0.96 | M | vs 1%: 0.09 < 0.22 not resolved (not claimed) |
| histgb@0.90 38.6 ± 6.2× (esc 2.65 ± 0.41) | same | 38.63 ± 6.21; 2.65 ± 0.41 | M | — |
| ridge@0.98 37.83 ± 1.78, 0.51 ± 0.21 (5/5), 2.65 ± 0.12× | same | identical; crossing key 0.98 | M | — |
| ridge@0.97 29.70 ± 1.70, 1.05 ± 0.22 (3/5), 3.38 ± 0.19× | same | 29.70 ± 1.70; 1.048 ± 0.221; 3.38 ± 0.19 | M | vs histgb@0.97 esc 23.9 > 1.70 **STD-PASS**; missed 0.289 > 0.221 **STD-PASS** |
| case118 all-splits ridge 0.95, histgb 0.98 (+ values) | `tuned_metrics` | ridge 0.95: 0/5 > 1% (0.94: 1/5); histgb 0.98: 0/5 (0.97: 2/5) | M | — |
| t_surr 1e-6, t_solve 9.14 | `scripts/case30_gate.py:124`; frozen `ms_solver` | l.124 `ge.score(gate, yte, 1e-6, ms_solver, LIMIT)`; 9.14 | M | — |
| strip 7.09, violations 15.40 | frozen | 7.0862 / 15.3967 | M | — |
| published case30 20.01% (§7) | `case30_frozen.json` | 20.0146 | M | — |
| **Consistency:** l.81, l.365, l.388 — complete. | | | | |

### E5b-E15 — SIGNED OFF
| Value | Source → key | Recomputed | V | Std |
|---|---|---|---|---|
| bound ≤ 1 − target (0.10 / 0.03) | definition | — (definition) | M | n/a |
| conditional ≤ 57.2 / 34.3 / 17.2% | `frozen_v2.ceilings.true_violation_rate` 0.1748 | 0.5721 / 0.3432 / 0.1716 (with exact 0.174756: 0.5722 / 0.3433 / 0.1717) | M | n/a |
| P(overshoot > q̂ \| viol) 0.388 / 0.411 | `barrier_height.json` | predictions: 0.38837 / 0.41150 | M | n/a |
| missed @0.90 2.96 ± 0.44 / 4.72 ± 0.98 | `tradeoff_curve_v2` | 2.963 ± 0.439 / 4.717 ± 0.977 | M | n/a |
| S_mean 0.6038 ± 0.0757 / 0.7919 ± 0.0743 (cut) | `barrier_height.json` | predictions: 0.60378 ± 0.07569 / 0.79193 ± 0.07433 | M | 0.188 > 0.0757 PASS (irrelevant once cut) |
| **Consistency:** l.128, 132, 181, 183–189, 363 — complete. | | | | |

### E6 — REJECTED (k≈119 row)
| Value | Source → key | Recomputed | V | Std |
|---|---|---|---|---|
| classical MAE 3.77 ± 0.06 e-3, R² 0.12 ± 0.00 | `classical_screen_metrics.json` | `classical_predictions.parquet` on the N1 test splits: 3.7657 ± 0.0583, R² 0.1171 ± 0.0036 | M | — |
| esc 92.0 ± 0.5, missed 1.07 ± 0.22, 1.09 ± 0.01× | `conformalized[0.9]` | 92.03 ± 0.52, 1.074 ± 0.221, 1.085 ± 0.006 | M | — |
| 0.0101 ms | `ms_classical_headline` | 0.010144 | M | — |
| dominance ridge 9/9, histgb 1/9 | `comparison_curve_v2.dominance` | 9 of 9 dominated / 1 of 9 | M | — |
| PV 0.00081 / PQ 0.00482 | `qlimit_analysis` | predictions parquet by `true_weakest_type`: 0.000809 (72,725) / 0.004823 (206,230) | M | — |
| PV voltages fixed | `classical_screen.py:51-70` | `vm_slice=(npv+npq, npv+2*npq)` spans PQ only | M | — |
| ridge MAE 3.75e-3 vs 3.77 | `physics_ablation` baseline | 0.003754 ± 0.000133 | M | 0.012e-3 < 0.13e-3 STD-FAIL (claimed as "same") |
| static k≈91 96.91 ± 0.49 vs gate 97.04 ± 0.44 | `baselines.json` | 96.912 ± 0.487; 97.037 ± 0.439 (= 1 − missed@0.90) | M | 0.13 < 0.49 STD-FAIL (claimed as tie) |
| k≈57 91.01 ± 2.00 / 91.22 ± 0.55 vs 95.28 ± 0.98 | same | 91.014 ± 2.001; curve[56] 91.22 ± 0.55; 95.283 ± 0.977 | M | ≥ 4.06 > 2.0 **STD-PASS** |
| escalate-only 15.96 / 10.44 | same | 15.958 / 10.440 | M | — |
| flag share 25.1 / 17.2 → k 138 / 89 | `flag_confusion_long` | predictions: flag share 25.11 ± 0.83 / 17.21 ± 0.37; (0.4907+0.2511)·186 = 137.98; (0.3063+0.1721)·186 = 88.96 | M | — |
| static k=138 99.41 ± 0.16 vs 97.04 | curve[137] | 99.41 ± 0.16 | M | 2.37 > 0.44 **STD-PASS** |
| static k=89 96.64 ± 0.50 vs 95.28 | curve[88] | 96.64 ± 0.50 | M | 1.36 > 0.98 **STD-PASS** |
| flags-solved ridge k≈166 99.92 ± 0.03 vs 99.21 ± 0.21 | curve[165] | k = 166.38 → 166: 99.916 ± 0.034 | M | 0.71 > 0.21 **STD-PASS** |
| flags-solved histgb k≈150 99.71 ± 0.09 vs 99.17 ± 0.24 | curve[149] | k = 150.45 → 150: 99.708 ± 0.085 | M | 0.54 > 0.24 **STD-PASS** |
| esc-budget ridge k≈120 98.67 ± 0.29 | curve[119] | k = 119.67 → 120: 98.671 ± 0.285 | M | 0.54 > 0.29 **STD-PASS** |
| esc-budget histgb k≈119 98.61 ± 0.30 | curve[118] | k = 118.44 → **118: 98.57 ± 0.31** (119 is a ceiling; other rows use nearest) | **MM** | 0.60 > 0.31 STD-PASS either way |
| train-mean 0.9398 | parquet pooled mean | 0.939826 | M | — |
| **Consistency:** l.109, 124, 208, 349, 388 — complete. | | | | |

### E8 — REJECTED (ROUNDING 1.47; consistency l.199, l.292)
| Value | Source → key | Recomputed (predictions: certified share per seed; speedup with the stated formula, per-seed `ms_surrogate`) | V | Std |
|---|---|---|---|---|
| ridge cert-only 1.35 ± 0.04 / 1.12 ± 0.03 / 1.08 ± 0.03 / 1.04 ± 0.02 / 1.01 ± 0.00 / 1.00 ± 0.00 | `flag_confusion_long` | 1.349 ± 0.044 / 1.119 ± 0.035 / 1.076 ± 0.032 / 1.036 ± 0.015 / 1.010 ± 0.004 / 1.001 ± 0.001 | M | — |
| histgb 2.10 ± 0.12 / 1.57 ± 0.06 / **1.47** ± 0.07 / 1.35 ± 0.07 / 1.24 ± 0.07 / 1.12 ± 0.04 | same | 2.096 ± 0.121 / 1.567 ± 0.062 / **1.46496** ± 0.069 / 1.352 ± 0.070 / 1.240 ± 0.071 / 1.122 ± 0.042 (t_surr = 0 gives 1.4655) | **R** at 0.95; rest M | @0.97 1.24 ± 0.07 vs net 1.58 ± 0.12: 0.34 > 0.12 **STD-PASS** |
| certified ridge@0.94 10.5 ± 2.7, histgb@0.97 19.1 ± 4.9 | `certified_frac` | predictions: 10.55 ± 2.73 / 19.12 ± 4.94 (= parquet) | M | — |
| false flags 11.0 ± 0.9 / 2.5 ± 0.3 | `false_flag_rate_of_all` | predictions: 11.03 ± 0.86 / 2.47 ± 0.26 | M | 8.5 > 0.9 **STD-PASS** |
| precision 56.1 ± 2.0 / 85.6 ± 1.4 | `flag_precision` | 56.13 ± 2.00 / 85.64 ± 1.39 | M | 29.5 > 2.0 **STD-PASS** |
| net 1.56 ± 0.07 / 1.58 ± 0.12 | `tradeoff_curve_v2` | 1.557 ± 0.068 / 1.579 ± 0.117 | M | — |
| **Consistency:** listed l.81, 231, 349, 388. **Unlisted:** l.199 ("2.04 … 3.29 times faster") and l.292 ("3.29 times speedup compared to 2.04") — same accounting rule applies. | | | | |

### E9 — SIGNED OFF
| Value | Source → key | Recomputed (predictions: pooled certified violations) | V | Std |
|---|---|---|---|---|
| ridge@0.94 384, max 0.0324, p99 0.0152, 84.9% within q̂ | `missed_depth.json` | 384; 0.0324 (seed 4); 0.0152; 84.90% | M | n/a |
| histgb@0.97 404, max 0.0915, p99 0.0810, 73.8% | same | 404; 0.0915; 0.0810; 73.76% | M | n/a |
| certified in seeds 2, 3 | `qlimit_class.json` | seeds 2, 3 | M | — |
| per-seed max histgb 0.0359/0.0460/0.0915/0.0915/0.0670 | same | identical | M | — |
| per-seed max ridge 0.0241/0.0159/0.0129/0.0227/0.0324 | same | identical | M | — |
| 0.90: 74% / 55% within q̂; 26.7 / 21.4% deeper than 0.005 | `missed_depth` pooled 0.90 | 73.68% / 54.90%; 26.74% / 21.41% | M | n/a |
| corrected deepest histgb@0.97 0.9239/0.8845/0.8845/0.8845/0.8718 (0.0682) | N2 | predictions × corrected labels: identical | M (U) | n/a |
| corrected deepest ridge@0.94 0.9312/0.9242/0.9271/0.9173/0.8884 (0.0516) | N2 | identical | M (U) | n/a |
| 66.3% (268/404), 31.3% (120/384) flip | N2 | identical | M (U) | n/a |
| **Consistency:** l.292, l.303, l.367 + image via P-001 — complete. | | | | |

### E10 — SIGNED OFF
| Value | Source → key | Recomputed (drift parquets, cells at 0.90 directly) | V | Std |
|---|---|---|---|---|
| 2C ridge 79.5 ± 1.8 vs 88.4 ± 2.7 | `drift_n0_stratum_long` | 79.53 ± 1.80 vs 88.44 ± 2.69 | M | 8.9 > 2.7 **STD-PASS** |
| 2C histgb 89.6 ± 0.5 vs 90.3 ± 1.0 | same | 89.60 ± 0.51 vs 90.34 ± 0.96 | M | 0.74 < 0.96 STD-FAIL (spec: no difference) |
| 2C ridge missed 5.01 ± 0.52 vs 2.02 ± 0.78 | same | 5.011 ± 0.522 vs 2.016 ± 0.782 | M | 3.0 > 0.78 **STD-PASS** |
| 2D histgb 87.6 ± 1.0 vs 89.8 ± 1.0 | `drift_element_type_long` | 87.60 ± 1.01 vs 89.75 ± 1.05 | M | 2.15 > 1.05 **STD-PASS** |
| 2D ridge 89.3 ± 1.4 vs 89.4 ± 1.7 | same | 89.31 ± 1.42 vs 89.43 ± 1.74 | M | STD-FAIL (no gap, as labelled) |
| 2E histgb 89.5 ± 1.0 / 89.9 ± 1.2 vs 89.8 ± 1.0 | `drift_loading_tilt_long` | 89.49 ± 0.98 / 89.86 ± 1.19 vs 89.82 ± 0.98 | M | STD-FAIL (null, as labelled) |
| 2E ridge 89.5 ± 1.2 / 89.5 ± 1.2 vs 89.3 ± 1.3 | same | 89.48 ± 1.19 / 89.52 ± 1.20 vs 89.34 ± 1.33 | M | STD-FAIL (null) |
| **Consistency:** l.132, l.367, l.388, E1b cells identical — complete. | | | | |

### E11 — SIGNED OFF
| Value | Source → key | Recomputed (cases = one_time_cost·1000 / saving; saving = 9.14(1 − esc) − t_surr; ÷186) | V | Std |
|---|---|---|---|---|
| ridge@0.94 786,904 = 4,231 sweeps (2,564 s) | `break_even.json` | 786,903.5 / 4,230.7 / 2,563.77 | M | n/a |
| incl. training + search 1,494,968 = 8,037 (4,871 s) | same | 1,494,967.8 / 8,037.5 / 4,870.68 | M | n/a |
| histgb@0.97 772,851 = 4,155; 1,473,021 = 7,919 (4,886 s) | same | 772,851.4 / 4,155.1; 1,473,020.6 / 7,919.5 / 4,886.43 | M | n/a |
| saving 3.26 / 3.32 ms | same | 3.2580 / 3.3173 | M | n/a |
| 10 workers 5.40×, 1.87 ms, 54% | `parallel_speedup.json` | 5.398, 1.868, 0.540 | M | n/a |
| mean over 930 solves; serial 10.08 ms | same | "mean over 930 solves … JIT warm-up discarded"; 10.082 | M | — |
| N6 cold median 9.25, warm 7.98, ratio 1.16, cold min 7.53, 0 label diffs / 2,232 | `sts_n6_warmstart_timing.json` | 9.2507 / 7.9842 / 1.1586 / 7.5261 / 0 of 2,232 | M (U) | n/a (note busy-machine load average) |
| rejected 1,287; 2,575.5 s | `break_even.generation` | 1,287; 2,575.53 (from a run-log constant, not a committed file — as spec says) | M | — |
| **Consistency:** l.99, 147, 349, 388 — complete. | | | | |

### E12-E13 — SIGNED OFF (U: `sts_e12_e13_conditional.json`)
| Value | Source → key | Recomputed (predictions: group by scenario_id / outaged element) | V | Std |
|---|---|---|---|---|
| histgb@0.97 11.1 ± 2.6% (10.7,12.0,15.0,11.0,7.0) | `summary.histgb.any_miss["0.97"]` | 11.13 ± 2.57; identical per split | M (U) | — |
| ridge@0.94 7.7 ± 2.0% (6.3,5.7,11.3,8.3,6.7) | `any_miss["0.94"]` | 7.67 ± 2.03 | M (U) | vs histgb@0.97: 3.46 > 2.57 **STD-PASS** |
| @0.90 ridge 22.5 ± 3.6, histgb 47.1 ± 4.7 | `any_miss["0.9"]` | 22.53 ± 3.59 / 47.13 ± 4.73 | M (U) | 24.6 > 4.7 **STD-PASS** |
| max misses one base 13.2 ± 6.4 / 11.8 ± 2.1 | same | 13.2 ± 6.43 / 11.8 ± 2.14 | M (U) | — |
| E12 min 57.5 ± 1.6 / 55.7 ± 3.0; p5 66.8 / 66.1; median 93.5 / 94.9 | `E12_element` | 57.47 ± 1.57 / 55.67 ± 3.03; 66.83 / 66.13; 93.50 / 94.87 | M (U) | — |
| below 85%: 18.1 ± 0.6 / 23.5 ± 3.0 vs 0.24% | same | 18.06 ± 0.65 / 23.55 ± 2.95; binomial reference 0.243% | M (U) | n/a |
| E13 8.7 ± 1.5 / 8.7 ± 1.7 vs 1.9%; min ~9% | `E13_base_coverage` | 8.67 ± 1.52 / 8.67 ± 1.73; 1.889%; min 8.6 / 9.4% | M (U) | — |
| cluster-SE ratio 7.0 / 5.6 | scratch `tmp/panel_stats/analyze.py` | not in any artifact (spec: do not print) | NF (excluded) | — |
| **Consistency:** l.132, l.363, Tables I/II captions — complete. | | | | |

### E14 — SIGNED OFF (confirms the spec's reading: +F1+F2 escalation change passes the std rule)
| Value | Source → key | Recomputed (per-seed `physics_ablation.records`, mode m2_searched) | V | Std |
|---|---|---|---|---|
| best ridge 0.00371 ± 0.00010 (+F1+F3); histgb 0.00153 ± 0.00011 (+F1+F2+F3+F4) | `physics_ablation` / `physics_conclusion` | 0.003707 ± 0.000096; 0.001526 ± 0.000111 | M | vs baseline both STD-FAIL (claimed "no gain") |
| ridge +F1+F2 0.004161 ± 0.000247 vs 0.003754 ± 0.000133 (+10.8%) | same | identical; +10.84% | M | 0.000407 > 0.000247 **STD-PASS** |
| @0.94 esc 59.0 ± 2.9 vs 64.3 ± 2.8; missed 1.00 ± 0.37 vs 0.79 ± 0.21 | `by_target["0.94"]` | 59.00 ± 2.85 vs 64.34 ± 2.78; 1.00 ± 0.37 vs 0.79 ± 0.21 | M | esc 5.34 > 2.85 **STD-PASS**; missed 0.21 < 0.37 STD-FAIL (not claimed) |
| histgb best @0.97 esc 59.9 ± 3.2 vs 63.7 ± 5.1; missed 0.66 ± 0.13 vs 0.83 ± 0.24 | same | 59.86 ± 3.15; 0.66 ± 0.13 | M | both STD-FAIL (as labelled) |
| F3/F4 186 rows | `physics/lodf.parquet`, `edistance.parquet` | (186, 189), (186, 120) | M | n/a |
| 118 pload + 118 qload | `dataset.parquet` schema | 118 / 118 | M | n/a |
| audit 25 bases, max err 0.0 | `f1_leakage_audit.json` | n_scenarios_checked 25; all four max errors 0.0 | M | n/a |
| N4 histgb 1.563 ± 0.076 / 1.558 ± 0.092 / 1.576 ± 0.088; paired −1.8 ± 2.5e-5, 4/5 | `sts_n4_f1_shuffle.json` | per_seed arrays: identical | M (U) | STD-FAIL (as labelled) |
| N4 ridge paired +3.1 ± 2.8e-6, 1/5 | same | identical | M (U) | STD-FAIL |
| N4 histgb@0.97 missed 0.75 ± 0.19 vs 0.82 ± 0.07; paired −0.07 ± 0.13 | same | 0.748 ± 0.188 vs 0.819 ± 0.066; −0.071 ± 0.135 | M (U) | STD-FAIL |
| N4 ridge@0.90 2.64 ± 0.43 vs 2.97 ± 0.43; paired −0.33 ± 0.04, 5/5 | same | 2.643 ± 0.434 vs 2.974 ± 0.434; −0.330 ± 0.038; 5/5 | M (U) | 0.33 < 0.43 STD-FAIL (spec: do not report as effect) |
| check_4 0.0015638 / 0.0015539 / 0.0015300 | `f1_leakage_audit.check_4_permutation` | identical; N4 `reproduction_vs_check_4` equal | M | — |
| **Consistency:** l.124, 371–379 — complete (l.377's 2.39e-5 = 0.0015539 − 0.0015300 and 7.58e-5 = baseline std check out). | | | | |

### C8 — REJECTED ("~10%"; 74% verdict vs artifact rule; rows missing from artifact)
| Value | Source → key | Recomputed (per-split linear interpolation of missed vs escalation over `tuned_metrics` m2 sweeps, no extrapolation) | V | Std |
|---|---|---|---|---|
| 20%: 9.89 ± 0.50 vs 7.06 ± 1.25 | scratch; not in `sts_matched_escalation.json` (grid 25–75) | identical | M (no artifact key) | 2.83 > 1.25 **STD-PASS** |
| 30%: 6.99 ± 0.48 vs 4.79 ± 1.09 | `sts_matched_escalation.json` | identical | M (U) | **STD-PASS** |
| 40%: 4.78 ± 0.52 vs 3.34 ± 0.83 | same | identical | M (U) | **STD-PASS** |
| 50%: 2.79 ± 0.40 vs 2.15 ± 0.62 | same | 2.786 ± 0.404 vs 2.148 ± 0.618; gap 0.638 | M (U) | 0.638 > 0.618 **STD-PASS** (barely) |
| 55%: 2.02 ± 0.37 vs 1.63 ± 0.50 | same | identical | M (U) | tie (as labelled) |
| 60%: 1.30 ± 0.23 vs 1.18 ± 0.38 | same | identical | M (U) | tie |
| 63.7%: 0.82 ± 0.15 vs 0.89 ± 0.31 | not on artifact grid | identical | M (no artifact key) | tie |
| 64.3%: 0.75 ± 0.13 vs 0.85 ± 0.30 | not on artifact grid | identical | M (no artifact key) | tie |
| 70%: 0.29 ± 0.10 vs 0.47 ± 0.21 | same | identical | M (U) | tie |
| 72%: 0.14 ± 0.06 vs 0.37 ± 0.17 | same | identical | M (U) | 0.23 > 0.17 **STD-PASS** (ridge lower) |
| 74%: 0.04 ± 0.04 (4 splits) vs 0.27 ± 0.12, "ridge lower" | same | values identical; artifact verdict **"incomplete (ridge 4 / histgb 5)"** | M values / verdict conflicts with artifact rule | not a 5-split comparison |
| @0.96: 0.14 ± 0.07 @71.4 ± 1.4 vs 1.36 ± 0.20 @57.0 ± 4.3 | `tradeoff_curve_v2` | 0.142 ± 0.072 @71.43 ± 1.41; 1.357 ± 0.198 @56.96 ± 4.25 | M | 1.22 > 0.20 STD-PASS |
| ridge ceiling 74.89% | `frozen_v2.ceilings` | 0.748876 | M | — |
| corrected 0.46 ± 0.08 vs 1.14 ± 0.57 | N2 | 0.4624 ± 0.0786 vs 1.1384 ± 0.5677 | M (U) | 0.676 > 0.568 **STD-PASS** |
| MAE ridge 3.8 ± 0.1 vs persistence 4.2 ± 0.1 | Table I | `tuned_metrics` m2 ridge 3.754 ± 0.133; `screener_metrics` persistence 4.246 ± 0.071 | M | 0.49 > 0.13 **STD-PASS** |
| "ridge better, by ~10%" | Table I | **11.6%** lower (persistence 13.1% higher) | **MM** | — |
| **Consistency:** l.81, 199, 290–292, 303, 388 — complete (0.14/1.36 also in Table II rows l.251/258, unchanged reprints). | | | | |

### C13 — SIGNED OFF (confirms STATS-09 mismatch: histgb is 2 of 5)
| Value | Source → key | Recomputed | V | Std |
|---|---|---|---|---|
| ridge@0.94 0.60, 0.62, 1.15, 0.92, 0.68 → 1/5 | `tuned_metrics` | predictions route: 0.601/0.624/1.146/0.918/0.678 | M | mean vs 1% not resolved (not claimed) |
| histgb@0.97 1.16, 0.80, 1.03, 0.70, 0.47 → 2/5 | same | 1.162/0.798/1.032/0.699/0.470 | M | not resolved |
| upper 1.00 / 1.08 | `tradeoff_curve_v2` | 1.0025 / 1.0769 | M | — |
| ddof=1: 1.03 / 1.11 (0.234, 0.274) | — | ddof=1 std 0.2337 / 0.2736 → 1.027 / 1.106 | M | — |
| case30 histgb@0.97 5/5 < 1%; @0.96 2/5 | `case30_thermal_frozen.json` | 5 / 2 | M | — |
| corrected per split histgb 0.33/0.56/0.53/0.43/0.46 (0/5); ridge 1.63/0.43/1.01/0.69/1.94 (3/5) | N2 | predictions × corrected labels: identical | M (U) | — |
| STATS-09 "1 of 5 at each point" is wrong for histgb | files | histgb 2 of 5 | M (spec's finding confirmed) | — |
| **Consistency:** l.81, 231, 281, 349, 365, 388 — complete. | | | | |

## Re-read check after the lead's "specs updated" notice (19:11)
- Every spec file in set A, and `_index_A.md`, still has the size and mtime (latest 18:55:57) it had in my first
  directory listing, taken before I read any of them. The content I verified is therefore the current content,
  including the "Update after the lead's 2nd message" section. The N2b blocks are present in P-003, E6, E8, E9,
  E12-E13, C8, C13 and Top5-2d-E5; the E14 consistent-sign note and the E11 P-033 note are present too. No Numbers
  section changed, so no verdict changes.
- E11 P-033 (§4) numbers, checked in addition: N6 cold minimum 7.53 ms (MATCH, `sts_n6_warmstart_timing.json`
  → 7.526); committed `ms_solver` 9.14 (MATCH); medians 9.25 vs 9.51 ms (MATCH: N6 9.2507; `data/solve_time.json`
  → `median_ms` 9.512). E11 stays SIGNED OFF.

## Pass 2 (2026-09-27, after the specs' "Update after verifier pass 1")
I used the same method as pass 1: recompute from row-level data, population std, and the std rule on claimed
comparisons. Spec files were re-read at their 19:12–19:13 versions. `report/paper_current_STS.tex` is unchanged
(mtime 13:49), so the pass-1 line numbers still hold.

**Correction to my pass-1 table:** E6 histgb k = 118 std is 0.30495, which rounds to **0.30**, not the 0.31 I wrote.
The spec's pass-2 value 98.57 ± 0.30 is correct. The gap 0.60 exceeds 0.30 (and 0.31), so the verdict is unaffected.

| Spec | Pass-1 issue | Pass-2 check (route) | Result |
|---|---|---|---|
| P-003 | consistency: l.121, l.347, l.107/l.349 unlisted | All three are now listed in §7. New number: "saturation ≈ 83.4% on the full dataset" = 1 − 0.165962 = 83.40% (N2 row recount). It is correctly caveated as full-dataset, not the test-split 82.64%. All other §5 values are unchanged and were re-matched in pass 1. | **SIGNED OFF** |
| P-007 | 41.2% → 41.4%; l.107/l.349 unlisted | Now 41.4% (parquet: 13.094 / 31.616 = 41.42%). l.107 and l.349 are listed in §7. | **SIGNED OFF** |
| Top5-1 | ROUNDING 65.58 | Now 65.59%, "80,048 / 122,035". Recount from `unconditioned_base.parquet`: 80,048 / 122,035 = 65.594% MATCH; gated 68.904% MATCH. | **SIGNED OFF** (note 1) |
| E1b | ROUNDING 65.58 | Same recount, MATCH. 47.49% denominator is now stated: 710 / 1,495 = 47.49%, and 47.33% over 1,500, MATCH. The preregistration is now flagged as git-ignored. | **SIGNED OFF** (note 1) |
| E6 | MISMATCH k≈119 row | Now k = 118, "98.57 ± 0.30". `baselines.json` curve[117] = 98.566 ± 0.305 MATCH. The stated nearest-integer rule reproduces every listed k: 91.25→91, 56.95→57, 137.98→138, 88.96→89, 166.38→166, 150.45→150, 119.67→120, 118.44→118. Gate ahead: 99.17 − 98.57 = 0.60 > 0.30, **STD-PASS**. | **SIGNED OFF** |
| E8 | ROUNDING 1.47; l.199/l.292 unlisted | One formula (Eq. 2, per-split t_surr) is now stated for all 12 values. Predictions route: histgb 2.10/1.57/**1.46**/1.35/1.24/1.12 and ridge 1.35/1.12/1.08/1.04/1.01/1.00, with stds as printed, MATCH. l.199 and l.292 are now listed. | **SIGNED OFF** |
| C8 | "~10%"; 74% verdict; rows missing from the artifact | "11.6% lower / 13.1% higher" MATCH (3.754 vs 4.246). The table is re-sourced to `sts_matched_escalation.json`: all 12 rows (25, 30, 40, 50, 51, 55, 60, 64, 70, 71, 73, 74) equal my independent interpolation from `tuned_metrics` m2 sweeps, including n_seeds. Verdicts equal the artifact's; 74% is "incomplete — no verdict". Std checks: 25–50 PASS (50%: 0.638 > 0.618, barely); 51–70 tie (51%: 0.580 < 0.596); 71% PASS **barely** (0.197 > 0.190); 73% PASS (0.249 > 0.142). | **SIGNED OFF** (note 2) |

Spot-checks (changed under the non-blocking notes):
- **E1a:** 55.51% is now sourced to tracked `clip_artifact.json`, MATCH. New in §6: "22.4% of rows move by more than 0.001 pu" = 100 − 77.649 = 22.35%, MATCH; "mean \|Δ\| 0.0043 pu" = 0.004263, MATCH. §7 "13.1% higher / 11.6% lower" MATCH. **Still SIGNED OFF.**
- **E1c:** §6 cites 68.90% → 65.59%, MATCH. Numbers section unchanged. **Still SIGNED OFF.**
- **E11:** N6 note now says "cuts the median per-solve time by 13.7%": 1 − 7.9842 / 9.2507 = 13.69%, MATCH. Also "paired median saving 1.27 ms" (1.2652) MATCH and "load ≈ 49 / 87 over 5 / 15 min" (48.73 / 86.85) MATCH. The index "16% faster" wording is gone. **Still SIGNED OFF.**
- **Top5-2d-E5:** §7 now says any-miss keys exist at 0.90 / 0.94 / 0.97 for both models, which matches the artifact. **Still SIGNED OFF.**

Notes (not blocking):
1. The conditional share 65.59% has no correct artifact key. The only key (`unconditioned.conditional_boundary_pct`)
   holds 65.5823. Before printing, d-figs should write the recounted value into a facts JSON (same status as the
   1,016/1,500 and 86/1,500 counts). Otherwise the paper prints a number that no file carries.
2. At 50% and 71% the std-rule margin is under 0.01 percentage points. Both verdicts are correct, but a one-split
   change would flip them. The prose should not lean on the exact crossover points.
3. Unchanged since pass 1: Top5-1's 61.61% row still says "no tracked key". The key now exists in untracked
   `sts_dataset_facts_b.json`; the row is still do-not-print.

**Pass-2 totals: SIGNED OFF 21 of 21** (the 14 from pass 1 plus P-003, P-007, Top5-1, E1b, E6, E8, C8). No spec failed
again on the same issue, so nothing needs escalating to the owner on repeat-failure grounds. The untracked-artifact
commits listed in the header are still required before printing.
