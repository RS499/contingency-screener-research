# Fact-check — report/paper_current_STS.tex

**Date:** 2026-08-27. **Mode:** report only; no `.tex` edit, no git write, no manuscript prose.
**Interpreter:** `.venv/bin/python` (3.13.9, pandapower 3.5.4, numpy 2.3.5) for every derivation.

## 0. Anchor

| field | value |
|---|---|
| path | `report/paper_current_STS.tex` |
| sha256 | `982cc00bacf48fc49ffc1eea514c0b0182e6d7a0394e57000d39e2f1e5ce4bd6` |
| lines | 326 |
| bytes | 35,558 |
| git HEAD at check | `9b5e5a4` (working tree clean) |
| non-ASCII characters | **0** (`LC_ALL=C grep '[^ -~]'` returns nothing) |

Every artifact value below was read from its file **in this session**. `notes/writing-numbers.md`
was used as an index only; where it disagrees with an artifact, the artifact wins and the
disagreement is reported in §1.3.

**Scope honoured.** The mid-revision exclusion list in the prompt was applied. Nothing on it is
reported as a finding. Where a listed item is adjacent to a new finding, the report says so
explicitly.

---

## 1. Every number

Excludes the bibliography (L271-onward), `%` comment lines, and pure LaTeX lengths
(`\vspace{0.15in}`, `width=0.8\textwidth`, `{10^{-3}}`).

Abbreviations: `fpn_v2` = `data/frozen_poster_numbers_v2.json`; `tc_v2` =
`data/tradeoff_curve_v2.json`; `tm` = `data/tuned_metrics.json`; `sm` =
`data/screener_metrics.json`; `c30t` = `data/case30_thermal/case30_thermal_frozen.json`;
`ds` = `data/dataset.parquet`.

### 1.1 Background and Method (§II, §III)

| # | § / line | claim as written | artifact value | source file | jsonpath / column | aggregation | verdict |
|---|---|---|---|---|---|---|---|
| 1 | II / L92 | "0.94 per unit indicates a 6\% under-voltage" | 1 − 0.94 = 0.06 | — | arithmetic on the stated floor | raw | CORRECT |
| 2 | II / L92 | "73.1\% of converged N-1 rows are over 1.05 pu" | 0.731358 | `ds` | `max_vm > 1.05` over converged N-1 | raw share, n=278,955 | CORRECT |
| 3 | II / L92 | "case118 assigns every line the same 9,900 MVA rating" | 9900.0 MVA, **one** unique value | `pandapower.networks.case118()` | √3·`bus.vn_kv`·`line.max_i_ka` | all 173 lines | CORRECT |
| 3b | II / L92 | (implied: the thermal test is inert for all 186 branches) | `trafo.sn_mva` also uniform 9900.0, 13 of 13 | same | `net.trafo.sn_mva` | all 13 trafos | CORRECT — the sentence says "every line"; the transformers carry the same placeholder, so the conclusion holds for the whole N-1 set |
| 4 | II / L96 | "118 buses ... 173 lines, and 13 transformers ... 186 total" | 118 / 173 / 13 / 186 | `case118()` | `len(net.bus/line/trafo)` | raw | CORRECT |
| 5 | III-A / L104 | "Independent mode (750 bases) ... multipliers ranging from 1.0 to 1.12" | n=750; per-load multiplier min 1.0000, max 1.1200 | `ds` | `pload_i / p0_i`, `sampling_mode=='independent'` | min/max over 74,250 (base, bus) pairs | CORRECT |
| 6 | III-A / L104 | "Regional mode (750 bases) ... from 0.9009 to 1.2310 (43.91\% outside the target range)" | n=750; 0.9009 / 1.2310; 43.91\% outside [1.0, 1.12] | `ds` | same, `sampling_mode=='regional'` | min/max/share over 74,250 pairs | CORRECT |
| 7 | III-A / L104 | "reactive power scales across all 1,500 bases range from 0.8156 to 1.4083 (56.83\% outside)" | 0.8156 / 1.4083; 56.83\% | `ds` | `qload_i / q0_i`, all bases | min/max/share over 135,000 pairs | CORRECT |
| 8 | III-A / L104 | "kept if the minimum pre-outage voltage exceeded 0.94 per unit" | min base `n0_min_vm` = 0.940000035663552 | `data/bases_clearing_0p95.json` | `canonical_v2.min_base` | raw | CORRECT |
| 9 | III-A / L104 | "a simulation of 186 contingencies" | 186 | `case118()` | lines + trafos | raw | CORRECT |
| 10 | III-A / L104 | "1,500 base cases and 280,500 rows" | 1500 scenarios; 280,500 rows (= 1500 × 187) | `ds` | parquet `num_rows`; `scenario_id.nunique()` | raw | CORRECT |
| 11 | III-A / L104 | "1,500 were N-0 base rows ... the other 279,000 rows are N-1" | 1500 / 279,000 | `ds` | `outaged_type=='none'` / `!='none'` | count | CORRECT |
| 12 | III-A / L104 | "45 were removed due to failing to converge, resulting in 278,955 converged rows" | 45 / 278,955 | `ds` | `~converged` / `converged & outaged_type!='none'` | count | CORRECT |
| 13 | III-A / L104 | "ranged from 0.7179 to 0.9603 per unit" | 0.7179413407605296 / 0.96031121678118 | `ds` | `min_vm` over converged N-1 | min/max | CORRECT |
| 14 | III-A / L104 | "17.48\% of the observations violated the voltage limit" | 0.174756 | `ds` | `min_vm < 0.94` over converged N-1 | raw share | CORRECT |
| 15 | III-A / L104 | "the published base case is at 111.83\% line loading" | 111.83140586617333 | `notes/writing-numbers.md` §"Unchanged by the fix", from `data/thermal_check.json` | case30 N-0 base max line loading | raw | CORRECT |
| 16 | III-A / L104 | "41 rather than 186 branches, the 1,500 bases produce 61,500 contingency scenarios, all of which were solved successfully" | case30: 41 branches; 1,500 bases; 61,500 N-1 rows; 0 non-converged | `case30()`; `data/case30_dataset.parquet`; `data/case30_thermal/dataset.parquet` | `len(line)+len(trafo)`; `outaged_type!='none'`; `converged` | count | CORRECT — **but see §3.1**: true of *both* case30 sets, and the sentence names only the published one |
| 17 | III-B / L107 | "split into 60\%, 20\%, and 20\% sets using different base scenarios" | 0.6 / 0.2 / 0.2, grouped on `scenario_id` (900/300/300) | `data/splits.json` | `train_frac`, `cal_frac`, `test_frac`, `group_col` | raw | CORRECT |
| 18 | III-B / L107 | "three smaller parts ... never look at the real calibration or test sets" | protocol step (2)-(7): inner fit/inner_cal/inner_score; "cal and test are never read during the search" | `tm` | `.protocol` | raw | CORRECT |
| 19 | III-B / L107 | "skip the most solves while still missing 1\% or fewer of the violations" | "M2 = max avoided subject to inner missed <= 1%" | `tm` | `.protocol` | raw | CORRECT |
| 20 | III-B / L107 | "repeat the whole process with five different random splits" | 5 | `tc_v2`, `tm` | `.seeds` | raw | CORRECT |
| 21 | III-C / L115 | "At a 90\% coverage level ... 0.0052 per unit for the linear model and 0.0023 ... for the gradient-boosted" | 0.005198 / 0.002291 | `tc_v2` | `.records[].q_hat`, `coverage_target=0.90` | seed-mean, ddof=0 | CORRECT |
| 22 | III-D / L119 | "the limit $L=0.94$" | 0.94 | `tc_v2` | `.limit` | raw | CORRECT |
| 23 | III-D / L130 | "$t_{\text{solve}}$ ... set at 9.14 ms, which is the minimum over 400 timed solves" | 9.14; `n_timed` 400; `min_ms` 9.138 | `data/solve_time.json` | `.ms_solver`, `.n_timed`, `.min_ms` | min over 400, 30 warmup dropped | CORRECT |

### 1.2 Results, Discussion, Conclusion, Abstract

| # | § / line | claim as written | artifact value | source file | jsonpath / column | aggregation | verdict |
|---|---|---|---|---|---|---|---|
| 24 | IV / L146 | "$R^2$ of 0.77 ... and 0.92" | 0.7718 / 0.9227 | `tm` | `.records[].r2`, `metric=='m2'` | seed-mean, ddof=0 | CORRECT |
| 25 | IV / L146 | "mean absolute errors of 0.0038 and 0.0016 per unit" | 0.003754 / 0.001563 | `tm` | `.records[].mae`, `metric=='m2'` | seed-mean | CORRECT |
| 26 | IV / L146 | "ridge ... escalates 49.1\%, has 89.3\% coverage, misses 2.96\%, and is 2.04 times faster" | 49.07 / 89.34 / 2.96 / 2.043 | `tc_v2` | `.records[]`, ridge @0.90 | seed-mean | CORRECT |
| 27 | IV / L146 | "histgb escalates 30.6\%, has 89.8\% coverage, and is 3.29 times faster ... misses 4.72\%" | 30.63 / 89.82 / 3.287 / 4.72 | `tc_v2` | `.records[]`, histgb @0.90 | seed-mean | CORRECT |
| 28 | Table I / L162 | persistence: 4.2±0.1 / −0.06±0.00 / 99.5±0.2 / 0.31±0.08 / 1.00±0.00 | 4.246±0.071 e-3 / −0.06114±0.00322 / 99.534±0.164 / 0.311±0.080 / 1.0047±0.0017 | `sm` | `.records[]`, `model=='persistence'` | seed-mean, ddof=0 | CORRECT |
| 29 | Table I / L163 | train mean: 6.7±0.2 / −0.00±0.00 / 0.0±0.0 / 0.00±0.00 / N/A | 6.732±0.173 e-3 / −0.00021±0.00021 / 0.0±0.0 / 0.0±0.0 / 2.13e7 | `sm` | same, `model=='train_mean'` | seed-mean | CORRECT — "N/A$^\dagger$" is the honest rendering of a 2.1e7 speedup |
| 30 | Table I / L164 | ridge: 3.8±0.1 / 0.77±0.01 / 49.1±2.7 / 2.96±0.44 / 2.04±0.11 | 3.754±0.133 / 0.7718±0.0134 / 49.07±2.66 / 2.96±0.44 / 2.043±0.106 | `tm`, `tc_v2` | m2 records; `.records[]` @0.90 | seed-mean, ddof=0 | CORRECT |
| 31 | Table I / L165 | histgb: 1.6±0.1 / 0.92±0.00 / 30.6±2.5 / 4.72±0.98 / 3.29±0.30 | 1.563±0.076 / 0.9227±0.0038 / 30.63±2.51 / 4.72±0.98 / 3.287±0.302 | `tm`, `tc_v2` | same | seed-mean, ddof=0 | CORRECT |
| 32-37 | Table II / L184-189 | ridge @0.90/0.94/0.95/0.96/0.97/0.98, all four columns | 49.07±2.66, 89.34±1.33, 2.96±0.44, 2.043±0.106 · 64.34±2.78, 93.95±0.74, 0.79±0.21, 1.557±0.068 · 67.85±2.84, 95.01±0.63, 0.45±0.12, 1.476±0.062 · 71.43±1.41, 95.90±0.39, 0.14±0.07, 1.400±0.028 · 73.91±1.02, 96.94±0.25, 0.03±0.03, 1.353±0.019 · 74.80±0.82, 98.01±0.18, 0.00±0.00, 1.337±0.015 | `tc_v2` | `.records[]`, `model=='ridge'` | seed-mean, pop std ddof=0 | CORRECT (all 24 cells) |
| 38-43 | Table II / L191-196 | histgb @0.90/0.94/0.95/0.96/0.97/0.98, all four columns | 30.63±2.51, 89.82±0.98, 4.72±0.98, 3.287±0.302 · 46.68±2.75, 93.68±0.43, 2.48±0.38, 2.148±0.127 · 51.18±3.42, 94.66±0.44, 1.94±0.21, 1.961±0.127 · 56.96±4.25, 95.70±0.42, 1.36±0.20, 1.764±0.124 · 63.68±5.12, 96.96±0.25, 0.83±0.24, 1.579±0.117 · 72.00±3.67, 97.97±0.17, 0.30±0.13, 1.392±0.067 | `tc_v2` | `.records[]`, `model=='histgb'` | seed-mean, pop std ddof=0 | CORRECT (all 24 cells) |
| 44 | Fig. 2 cap / L208 | "first falls just under 1\% at 0.94 coverage for ridge and 0.97 for the gradient-boosted model" | ridge 0.94, histgb 0.97 | `fpn_v2` | `.crossings_first_below_1pct_missed` | seed-mean | CORRECT |
| 45 | IV-A / L214 | histgb 0.90→0.94: missed 4.72→2.48, escalation 30.6→46.7, speedup 3.29→2.15 | as row 38-39 | `tc_v2` | — | seed-mean | CORRECT |
| 46 | IV-A / L214 | ridge crossing: 0.94, "0.79\% missed, 64.3\% escalation, 1.56 times faster" | 0.79 / 64.34 / 1.557 | `tc_v2` | ridge @0.94 | seed-mean | CORRECT |
| 47 | IV-A / L214 | histgb crossing: 0.97, "0.83\% missed, 63.7\% escalation, 1.58 times faster" | 0.83 / 63.68 / 1.579 | `tc_v2` | histgb @0.97 | seed-mean | CORRECT |
| 48 | IV-A / L214 | "the error bars still reach up to about 1.0--1.07\%" | 0.79+0.21 = **1.00**; 0.83+0.24 = **1.07** | `tc_v2` | `missed_viol` + `missed_viol_std` | mean + 1σ | CORRECT |
| 49 | Fig. 3 cap / L224 | "a thin tail reaches 0.0915 pu, where one certified bus had fallen to 0.8485" | depth 0.0914569251411822; `y_true` 0.8485430748588177 | `data/missed_depth.json` | `.families.*.deepest_missed` | 5-seed pooled max | CORRECT (0.94 − 0.09146 = 0.84854; internally consistent) |
| 50 | IV-B / L230 | "at a coverage of 0.96, the linear model misses 0.14\% ... the gradient-boosted model 1.36\%" | 0.14 / 1.36 | `tc_v2` | @0.96 | seed-mean | CORRECT |
| 51 | IV-B / L230 | "3.29 times faster versus 2.04" | 3.287 / 2.043 | `tc_v2` | @0.90 | seed-mean | CORRECT |
| 52 | IV-B / L230 | "74\% of misses fall within one band width ... for the linear model and 55\% for the gradient-boosted" | 0.736769 / 0.549037 | `data/missed_depth.json` | `.families.*.pooled['0.90'].share_below_qhat` | **pooled over 5 seeds**, n=1,436 / 2,284 | CORRECT — aggregation differs from Tables I-II (pooled, not seed-mean); see §1.3-c |
| 53 | IV-B / L230 | "the worst being 0.0915 per unit under the limit, which was a bus that fell to 0.8485" | as row 49 | same | `.pooled['0.90'].max` | pooled max | CORRECT |
| 54 | IV-C / L234 | "56.86\% are in a narrow range of [0.94, 0.945)" | 0.568629 | `ds` | `0.94 <= min_vm < 0.945`, converged N-1 | raw share | CORRECT |
| 55 | IV-C / L234 | "17.48\% lie below the threshold as violations" | 0.174756 | `ds` | `min_vm < 0.94` | raw share | CORRECT |
| 56 | IV-C / L234 | "no 0.001-per-unit width bin makes up more than around 14\%" | modal bin `[0.940, 0.941)` = 0.140628 (39,229 of 278,955) | `ds` | `min_vm`, converged N-1 | modal 0.001-pu bin share, **edges anchored at 0.000, half-open** | CORRECT — anchor-dependent; see §1.3-a |
| 57 | IV-C / L234 | "bus 76 ... 27.1\% ... bus 53 ... 16.81\% ... bus 107 with 9.31\%" | 0-based buses 75 / 52 / 106 at 27.1 / 16.81 / 9.31 | `fpn_v2` | `.dataset_facts.critical_bus_top5` | raw share | CORRECT — IEEE 1-based names correctly = index+1, per `CLAUDE.md` §5 |
| 58 | IV-C / L247 | "band is only 0.0023 pu wide ... still captures 30.6\% of all contingencies" | 0.002291 / 30.63 | `tc_v2` | histgb @0.90 | seed-mean | CORRECT |
| 59 | IV-C / L247 | "the remaining **82.52\%** of cases ..., or the saturation point" | 82.52 = 100×(1 − 0.1748); but `perfect_model_floor_saturation` = **82.6352** | `fpn_v2` `.ceilings.true_violation_rate`; `scripts/case30_gate.py:188,197` vs `fpn_v2` `.ceilings.perfect_model_floor_saturation` | two different definitions | 1 − violation rate **vs** `floor` at max q̂ for persistence | **AGGREGATION-MISMATCH** — see §1.3-b |
| 60 | IV-C / L247 | "a lower escalation ceiling of 74.89\% versus 82.79\%" | 0.7488763 / 0.8279477 (= 1 − mean `p_pred_below_limit` 25.112\% / 17.205\%) | `fpn_v2` `.ceilings.escalation_at_max_band_width_...`; re-derived from `tm` m2 records | seed-mean, ddof=0 | CORRECT — stds are ±0.83 and ±0.37 pp, not printed |
| 61 | IV-C / L249 | "the model escalates 99.5\% of cases" (persistence) | 99.534 | `sm` | `model=='persistence'` | seed-mean | CORRECT |
| 62 | IV-C / L249 | "about a 1.6 times speedup instead of the 2 to 3 times available at 0.90" | 1.557 / 1.579; @0.90: 2.043 and **3.287** | `tc_v2` | — | seed-mean | CORRECT on 1.6; **hedge understates the upper end** — see §5 |
| 63 | V / L257 | "Every base case generates 186 related contingencies" | 186 | `case118()` | — | raw | CORRECT |
| 64 | V / L259 | "7.09\% of contingencies reach the threshold level, while another 15.40\% fall below it" (case30-thermal) | boundary mass 7.0862\%; violation rate 15.3967\% | `c30t` | `.boundary_mass_pct`, `.violation_rate_pct` | raw | CORRECT |
| 65 | V / L259 | "For case118, 56.86\% ... and 17.48\% fall below it" | 0.568629 / 0.174756 | `ds` | as rows 54-55 | raw | CORRECT |
| 66 | V / L259 | "111.83\% line loading in its base case" | 111.83140586617333 | `notes/writing-numbers.md`, from `data/thermal_check.json` | case30 N-0 base max loading | raw | CORRECT |
| 67 | V / L259 | "the gradient-boosted model at a 0.97 coverage target yields 5.84$\pm$1.25\% escalations" | 5.8358 ± 1.2505 | `c30t` | `.records[]`, `family=='histgb'`, `coverage_target==0.97` | seed-mean, pop std ddof=0, n=5 | CORRECT |
| 68 | V / L259 | "for 0.96 it is 0.91$\pm$0.22\%, with only two of five being under this limit" | 0.9094 ± 0.2196; 2 of 5 seeds < 1\% | `c30t` | `.records[]`, histgb @0.96, `missed_viol` | seed-mean + per-seed count | CORRECT |
| 69 | V / L259 | "Only 86 of the 1,500 base cases are above 0.95 pu" | 86 (both `>=` and `>`), 5.7333\% of 1500 | `data/bases_clearing_0p95.json` | `.canonical_v2.ge_0p95` / `.gt_0p95` | count | CORRECT |
| 70 | V / L259 | "increasing the threshold to 0.95 pu leads to a ridge escalation of 1.38$\pm$0.33\%" | 0.01384837 ± 0.00326317 | `data/escalation_at_095.json` | `.summary.ridge.escalation_at_0.95` | seed-mean, ddof=0 | CORRECT — **the coverage target (0.90) is not stated in the prose**; see §5 |
| 71 | V / L261 | "roughly one-quarter of converged rows ... include a single-generator outage" | 0.249259 (69,532 of 278,955) | `data/sampling_audit.json` | `.prevalence.share_of_n1_converged_rows` | raw share | CORRECT — but see §3.2 |
| 72 | V / L261 | "the worst case, at 0.0915 per unit" | 0.0914569 | `data/missed_depth.json` | `.families.*.deepest_missed.depth` | pooled max | CORRECT |
| 73 | VI / L267 | "requires escalating around two-thirds of cases" | 64.34 (ridge @0.94) / 63.68 (histgb @0.97) | `tc_v2` | — | seed-mean | CORRECT |
| 74 | Abs / L72 | "3.29 times faster ... misses 4.72\%" @90\% | as row 27 | `tc_v2` | — | seed-mean | CORRECT |
| 75 | Abs / L72 | "0.97 coverage target results in a 63.7\% escalation and speedup dropping to roughly 1.58, with error bars going slightly above 1\%" | 63.68 / 1.579 / 0.83+0.24 = 1.07 | `tc_v2` | histgb @0.97 | seed-mean + 1σ | CORRECT |
| 76 | Abs / L72 | "7.09\% ... compared to 56.86\% for case118 ... 5.84$\pm$1.25\% escalation" | as rows 64, 65, 67 | `c30t`, `ds` | — | — | CORRECT |

### 1.3 Rows of `notes/writing-numbers.md` that no longer reconcile

**(a) The "around 14\%" bin — the file contradicts itself.**
Two sections of `notes/writing-numbers.md` give opposite verdicts on the same manuscript claim:

- `## NO SOURCE` and `## Values in the manuscript with NO artifact behind them` both state:
  *"Line 235, 'no 0.001-per-unit width bin makes up more than around 14%' — **NO SOURCE**."*
- `### F.5 — modal 0.001-pu bin of min_vm` (added 2026-08-21) gives the value: `0.140628`,
  bin `[0.940, 0.941)`, count `39229`, derived two ways from `data/dataset.parquet`.

F.5 supersedes the NO SOURCE rows; the two stale rows were never retracted. I re-derived F.5
independently this session and it reproduces exactly. **Manuscript verdict: CORRECT.**
Caveat that must travel with the number: the bin edges are anchored at 0.000 and half-open, and
F.5 itself says a different anchor moves the modal bin. The manuscript states no anchor.
The stale rows also carry a line number (235) that no longer points at the claim in this file —
the sentence is now at **L234**.

**(b) Two artifact quantities named "saturation".** `data/frozen_poster_numbers_v2.json`
`.ceilings.perfect_model_floor_saturation` = `0.826352382506341` (**82.64\%**), computed by
`feasibility/freeze_poster_numbers.py:80` as the `floor` column at maximum q̂ for persistence.
`scripts/case30_gate.py:188` defines a *different* `saturation_point` = `100·(1 − violation_rate)`,
and `:197` hard-codes **82.52** as the case118 comparator, attributing it to
`frozen_poster_numbers_v2.json` — a file that does not contain 82.52, only
`.ceilings.true_violation_rate` = `0.1748` from which it is one step. The manuscript at L247
prints 82.52 and calls it "the saturation point". The value reconciles under the
`case30_gate.py` definition and does **not** reconcile with the artifact field that carries that
name. `notes/writing-numbers.md` records neither quantity. The gap is 0.12 pp.
(The separate defect in that same clause — attributing a model-independent 82.52\% "for the
gradient-boosted model", whose own ceiling is 82.79\% — is on the prompt's known-unfixed list and
is not counted here.)

**(c) Aggregation label, row 52.** The 74\%/55\% figures are **pooled over 5 seeds**
(`missed_depth.json` `.definitions.pooled`), while every other percentage in the paper is a
seed-mean with ddof=0 population std. `notes/writing-numbers.md` carries no row for these two
values at all. Not an error; an undocumented mixed convention.

**(d) `notes/writing-numbers.md` header staleness.** The file's header pins
`git HEAD 69eeb80a...`; HEAD is now `9b5e5a4`. The ADDED-ROWS blocks pin
`ab970c19...` and `03e1136e...`. Three different anchors in one file.

### 1.4 Verdict counts (§1)

| verdict | count |
|---|---|
| CORRECT | 75 |
| **AGGREGATION-MISMATCH** | **1** (row 59) |
| WRONG | 0 |
| UNSOURCED | 0 |
| SUPERSEDED | 0 |

Table rows 32-43 are counted as 12 rows (48 cells, all correct).

---

## 2. Every citation

### 2.1 Structural

- **18 distinct `\cite` keys; 18 `\bibitem`s; `\begin{thebibliography}{18}`. All three agree.**
- **No `\cite` without a `\bibitem`. No `\bibitem` never cited.** Nothing renders as `[?]`.
- **`\cite{tibshirani2019}` DOES remain in the body, at L261 — and its `\bibitem` is also still
  present.** The prompt states the bibitem was removed; **it was not removed from this file.**
  The document is internally consistent as it stands (18/18), so the predicted `[?]` does not
  occur. If the intended edit is still wanted, removing the bibitem alone would break L261 and
  require `{18}` → `{17}`.
- **`ansi2020` is a dangling key.** The pre-bibliography comment block (L269) says
  `ansi2020` was fetch-verified on 2026-07-29, and `notes/citation_support.json` carries an
  `ansi2020` entry — but there is no `\bibitem{ansi2020}` and no `\cite{ansi2020}` in this file.
  Leftover from the URTC version's ANSI C84.1 Range B sentence (`notes/prior-art.md` §7.3), which
  is not in this document. The comment should not claim verification of a reference the paper
  does not contain.
- **`notes/citation_support.json` is entirely unfilled.** All 19 entries have
  `cited_work: null`, `claim: null`, `verified_how: null`, `venue_status: null`. The file's own
  rules say *"An unfilled entry FAILS."* By the project's own gate, **claim-level support is
  currently documented for zero references.** Everything in §2.2 below rests on
  `notes/prior-art.md` plus the two live fetches I ran this session, not on that file.

### 2.2 Does the source support *that* claim?

| key | line | the claim it is attached to | supports? | evidence |
|---|---|---|---|---|
| `nerc` | 82 | the N-1 criterion requires post-outage voltages of remaining components to stay in range | **YES** | TPL-001-5.1 planning event P1 (single-element). Bibliographic identity confirmed in the file's own comment block (nerc.com, eff. 2023-07-01) |
| `bates2021` | 84 | a point-prediction surrogate "fails undetected ... since it only provides a single-point estimate without an attached confidence or uncertainty interval" | **PARTIAL** | RCPS (J. ACM 68(6):43) constructs distribution-free risk-controlling prediction *sets*. It motivates uncertainty sets; it makes no claim about surrogate failure modes in contingency screening. Generic motivational attachment |
| `manoharan2026` | 86 | "a fast computer model that checks if any single piece of equipment ... is in danger ... also runs randomized full solves on some of the equipment it did skip" | **YES** | `notes/prior-art.md` B5, VERIFIED [FETCHED] full text: LODF-based danger score proposes skips; a random audit runs exact AC on a subset. **Scope caveat:** the source's target is **thermal**; the prose never says so (the bibitem title does) |
| `alcantara2026` | 86 | "use an AI foundation model and conformal prediction to create a binary yes/no switch" | **YES** | `notes/prior-art.md` A1, VERIFIED [FETCHED] full text 2026-07-21: conformal intervals on a foundation model; decision is a BINARY flag; no escalation, no net-cost |
| `christianson2025` | 86 | "an input-convex network that completely removes false negatives, although that claim is only relevant to DC power flow models, not the AC power flow model our study uses" | **YES — verified this session** | Abstract (proceedings.mlr.press/v283/christianson25a.html, fetched 2026-08-27): *"our method can ensure a zero false negative rate."* Full text (arXiv:2410.00796v1, read this session) §2.1 is titled **"DC-OPF and Contingency Screening"**: *"system operators typically solve the DC-optimal power flow (OPF) problem, which considers a linearized model of power flow"*; the feasible region (Eq. 2-3) is the DC line-flow set $\underline{f} \le H_c y \le \bar{f}$. Both halves of the manuscript's sentence hold. *Unstated additional delta:* their screened quantity is line flow (thermal), not voltage |
| `ejebe1979` | 94 | "Classical fast screens rank power system contingencies without running a full solver" | **YES** | `notes/prior-art.md` §3 C7: the foundational performance-index contingency-selection method; VERIFIED [SEARCH] |
| `case118` | 96 | the IEEE 118-bus test case | **YES** | UW PSTCA archive; structure re-derived this session (118/173/13) |
| `pandapower` | 96 | the Python library used for post-outage solves with generator reactive limits enforced | **YES** | Thurner et al., IEEE Trans. Power Syst. 33(6):6510-6521. `notes/prior-art.md` §8.3 record, verified 2026-08-21. Solver config `enforce_q_lims=True` is pinned in `CLAUDE.md` §5 and in `data/miss_depth_v2.manifest.json` `.solver` |
| `sklearn` | 107 | ridge regression and a histogram-based gradient-boosted tree ensemble | **YES** | Both are scikit-learn estimators; env pinned at scikit-learn 1.7.2 |
| `lei2018` (×2) | 111 | (i) split conformal converts calibration residuals into a coverage guarantee; (ii) the finite-sample rank approach for $\hat q$ | **YES** for both | Lei et al., JASA 113(523):1094-1111 — split conformal with the finite-sample rank quantile is that paper's central construction |
| `vovk2005` | 111 | same, as the conformal-prediction foundation | **YES** | *Algorithmic Learning in a Random World* is the canonical monograph |
| `romano2019` | 115 | "locally adaptive alternatives exist" to a single global quantile | **YES** | CQR is exactly a locally adaptive conformal band |
| `desalvo2015` | 255 | "deciding whether or not to hand over the task to a more complex model" | **YES** | *Learning with Deep Cascades*, ALT 2015. `notes/prior-art.md` B6, VERIFIED [FETCHED] via Crossref + dblp |
| `angelopoulos2024` | 255 | "giving the model multiple options" | **YES** | *Conformal Triage* — three-way low-risk / high-risk / uncertain partition (`prior-art.md` A3) |
| `cortes2016` | 255 | same | **YES** | *Learning with Rejection*, ALT 2016. VERIFIED [FETCHED] Crossref + dblp |
| `chow1970` | 255 | same | **YES** | Chow's reject-option error/reject tradeoff is the origin of the primitive |
| `bates2021` | 257 | Manoharan's audited population control "is itself a form of distribution-free risk control" | **YES** | This is the RCPS paper's exact subject; `prior-art.md` B5 names Learn-Then-Test / Clopper-Pearson, the same family |
| `barber2021` | 257 | "If one demands perfect correctness with a limited amount of calibration data, then the prediction intervals become extremely wide, to the point where it becomes useless" | **NO — known** | Confirmed as flagged in the prompt. Barber et al., *Inf. Inference* 10(2):455-482, proves that distribution-free **conditional** coverage forces uninformative (infinite-length) intervals. The manuscript's sentence attributes the blow-up to (i) *perfect* coverage rather than *conditional* coverage, and (ii) *limited calibration data* — the impossibility result is not a small-sample statement. Both substitutions change what the theorem says |
| `tibshirani2019` | 261 | "mathematical proof is unable to determine the safety of N-2 outages since conformal prediction requires the data to be exchangeable with the calibration set" | **PARTIAL** | The premise (standard conformal assumes exchangeability) is background the paper states. But *Conformal Prediction Under Covariate Shift* is the paper that **relaxes** exchangeability via weighted conformal, so citing it for an impossibility reads against its own contribution. The reason it does not rescue N-1→N-2 is recorded in `notes/writing-numbers.md` (`CANNOT BE COMPUTED`: *"whether 2D bounds N-2 expectations — the event space changes; no likelihood ratio exists"*) and is **not stated in the manuscript**. The citation needs that one clause to carry the claim |

**Citation verdict counts:** supports = 15 keys (17 attachments), PARTIAL = 3 attachments
(`bates2021`@84, `tibshirani2019`@261, plus the `manoharan2026` thermal-scope silence),
does-not-support = 1 (`barber2021`, already known).

---

## 3. Internal consistency — statements that cannot both be true

### 3.1 The Method's 30-bus dataset vs the Discussion's — the numbers belong to different datasets

**HIGH.** III-A (L104) introduces exactly one 30-bus dataset: *"the **published** IEEE 30-bus
system, where the published base case is at 111.83\% line loading"*, then gives its size
(41 branches, 61,500 contingencies, all solved). Every 30-bus number the paper actually reports —
abstract L72 and Discussion L259 (7.09\%, 15.40\%, 5.84±1.25\%, 0.91±0.22\%) — comes from
`data/case30_thermal/`, a **different dataset built by `scripts/case30_thermal_build.py` under a
different N-0 criterion** (voltage *and* max loading ≤ 100\%).

`notes/writing-numbers.md` states this in bold: *"A row that says only 'case30' is ambiguous and
must not be used"*, and lists the two sets' violation rates as 28.81\% vs 15.40\% and boundary
masses as 20.01\% vs 7.09\%.

The prompt lists "case30-thermal's missing Method introduction" as known. What is **not** on that
list and is reported here: the size sentence in III-A (row 16) is numerically true of *both*
sets — I verified 1,500 bases / 61,500 N-1 rows / 0 non-convergences in **both**
`data/case30_dataset.parquet` and `data/case30_thermal/dataset.parquet` — so a reader has no
numerical cue that the Discussion has switched datasets. The 111.83\% figure is the only marker,
and it belongs to the set the results do **not** use.

### 3.2 The safety claim is scoped to a population no reported number is computed over

**HIGHEST SEVERITY.** L261 states: *"Our claims of safety are only true for N-1 contingency cases,
as the safety claims apply only to the specific set of N-1 branch-contingency cases, since there
are roughly one-quarter of converged rows that include a single-generator outage occuring
simultaneously with the branch outage, which does not meet the N-1 criterion."*

I verified the 24.93\% (`data/sampling_audit.json` `.prevalence.share_of_n1_converged_rows` =
0.24925884). But **every metric in the paper is computed over the full test split, gen-outage rows
included.** I searched `feasibility/*.py`, `scripts/*.py` and every `data/*.json`: **no artifact in
the repository reports gate metrics restricted to `gen_out < 0`.** The only files that touch
`gen_out` as a filter are `sampling_audit.py` (prevalence only) and `thermal_check.py`
(reconstruction).

So the sentence asserts a restriction that no number in Tables I-II, Fig. 2, or the abstract
honours. Read literally, the paper claims safety for a subset it never measures, using numbers
measured on a superset it says is out of scope. `data/sampling_audit.json` shows the two
populations are not interchangeable: violation rate 18.24\% with a generator outage vs 17.22\%
without (Δ 1.01 pp), boundary-strip share 58.10\% vs 56.45\% (Δ 1.64 pp).

This is a **new** finding. The prompt's known list covers the *wording* of the N-2 scoping
sentence (corrected in `9b5e5a4`); it does not cover the fact that the restriction is unmeasured.
Either the branch-only metrics get computed, or the sentence has to say that the reported numbers
are over the full mixed population.

### 3.3 The Introduction's first differentiator contradicts its own preceding sentence

**HIGH.** L86 says of Alcántara and Chatzivasileiadis: *"use an AI foundation model **and conformal
prediction** to create a binary yes/no switch."* Four sentences later, the same paragraph says:
*"Our work stands out from these papers in three distinct ways. **First, unlike the first two
approaches, we add a band to each contingency.**"*

"The first two approaches" are Manoharan and Alcántara. Manoharan has no per-instance band
(population audit) — true. **Alcántara does.** `notes/prior-art.md` A1, VERIFIED [FETCHED] full
text: *"Conformal intervals (stratified SCP + kernel-weighted KCP) on a foundation model's
predictions."* Their bands are, if anything, more elaborate than this project's single global
quantile.

Two problems compound: the two sentences contradict each other on the page, and the differentiator
as written is a conformal-*method* novelty claim — which `CLAUDE.local.md` explicitly rules out
(*"claim NO conformal-method novelty; their conformal is locally adaptive (SCP/KCP) vs my single
global quantile"*). The supportable delta is the **three-way gate with escalation to an exact AC
solver and net-cost accounting**, which the paper's own second and third differentiators and its
Discussion (L255) already state correctly.

### 3.4 IV-B's model ordering vs the Discussion's case30-thermal figures — NOT a contradiction

Checked as requested. IV-B (L230) is scoped to case118 twice ("On the IEEE 118-bus system…",
"…across all targets in the sweep on the IEEE 118-bus system" — the duplication itself is on the
known list). On case118 ridge does have the lower missed rate at every target
(`tc_v2`: 2.96/0.79/0.45/0.14/0.03/0.00 vs 4.72/2.48/1.94/1.36/0.83/0.30). On case30-thermal the
ordering reverses (histgb 2.226\% vs ridge 6.087\% at 0.90, `c30t`). Because IV-B is scoped and
the Discussion never restates the ordering, **the two are consistent.** The Conclusion's *"the
30-bus result shows that this depends on data distribution relative to the limit"* is the right
bridge. Noting for completeness that `notes/writing-numbers.md` §"BARRIER HEIGHT — RESOLVED"
explains the reversal via `S_mean`, and none of that mechanism is in the paper.

### 3.5 Abstract vs Table II — consistent

Every abstract figure traces to Table II or `c30t` (rows 74-76). The abstract's "first going just
under a 1\% mean missed rate at a 0.97 coverage target" agrees with Table II (1.36\% at 0.96,
0.83\% at 0.97) and with `fpn_v2.crossings_first_below_1pct_missed`. No conflict found.

### 3.6 Claims the experiments do not test

- L261 asserts N-2 safety is undeterminable; **no N-2 experiment is reported anywhere in this
  paper.** VI (L267) correctly books it as future work, so this is consistent, but the reader is
  given an impossibility claim with no accompanying measurement.
- VI says *"testing ... a third network"*, implying two were tested. Two are reported. The
  repository contains five more (`data/netstudy2/`, `data/network_triage.json`) that this paper
  does not use — not a contradiction, but "a third network" will read oddly against the repo.

---

## 4. LaTeX integrity

| check | result |
|---|---|
| `\label` count | 12 (5 section, 4 figure, 2 table, 1 `sec:results`) |
| `\ref` targets | 4 distinct figures + `sec:discussion` (×2) + `tab:models` (×3) + `tab:ops` — **all 10 resolve to an existing `\label`** |
| unused labels | **5**: `sec:intro`, `sec:background`, `sec:method`, `sec:results`, `sec:conclusion` — declared, never `\ref`'d. Harmless |
| `\includegraphics` | 4, all existing **relative to the repository root**: `data/gate_schematic_v3.png`, `data/tradeoff_hero_col_v2.png`, `data/miss_depth_v2.png`, `data/boundary_mass_hist.png` |
| **graphics path risk** | **`report/` contains only the `.tex`; there is no `report/data/`.** Compiling in place (`cd report && pdflatex paper_current_STS.tex`) fails on all four figures. The document only builds from the repo root, or with `\graphicspath{{../}}`. Not currently documented anywhere in the file |
| non-ASCII | **0** |
| environments | balanced: `document` 1/1, `equation` 2/2, `itemize` 1/1, `figure` 4/4, `table` 2/2, `tabular` 2/2, `thebibliography` 1/1 |
| braces | 201 `{` / 201 `}` |
| math `$` | 176, even |
| tabular columns | Table I spec `lccccc` = 6, header 6 fields, 4 body rows × 6 — consistent. Table II spec `llcccc` = 6, header 6, 12 body rows × 6 — consistent |
| section numbering | `\thesection` forced Roman. I Intro, II Background, III Method, IV Results, V Discussion, VI Conclusion. `\ref{sec:discussion}` → "V" as the header comment intends. Abstract and Acknowledgments are `\section*` (unnumbered) — correct |
| **subsection numbering vs comments** | With `article` + `\Roman{section}`, `\thesubsection` renders **III.1, III.2, IV.1** — *not* IEEEtran's III-A, IV-B. The tex comments at L133, L219, L237 say "Cited in III-D", "Cited in IV-B", "Cited in IV-C". Comments only, nothing rendered breaks, but they no longer describe the output |

### 4.1 Figure provenance

| figure | manifest | byte-reproducible | input |
|---|---|---|---|
| Fig. 1 `gate_schematic_v3.png` | `data/gate_schematic_v3.manifest.json` (schema B) | **yes**, md5 `5ceefccf…` verified 2026-08-27 | `tc_v2`, sha `a40a0797…`; strip sized from q̂ = 0.0022907 (M2) — matches the 0.0023 in prose |
| Fig. 2 `tradeoff_hero_col_v2.png` | `data/tradeoff_hero_col_v2.manifest.json` (schema B) | **yes**, md5 `47e37f20…` | `tc_v2`, same sha — Fig. 2 is the M2 curve |
| Fig. 3 `miss_depth_v2.png` | `data/miss_depth_v2.manifest.json` (schema A) | not asserted | `run_settings.source` names `dataset.parquet`, `tuned_metrics.json`, `missed_depth.json`. **`model_hyperparameters: null`** — `CLAUDE.md` §8 requires the hyperparameters that produced the artifact, and this figure depends on the per-seed M2 configs. `git_commit` recorded as `a4df350`, stale vs HEAD `9b5e5a4` |
| Fig. 4 `boundary_mass_hist.png` | **NONE — `data/boundary_mass_hist.manifest.json` does not exist** | unknown | unknown. Violates `CLAUDE.md` §8 ("Manifest beside every new artifact"). The only nearby manifest is `quintile_boundary_mass.manifest.json`, a different artifact |

Not re-reported as new: `notes/erratum.md` **E4** already logs that no graphic carries the
STS Appendix 3 attribution line. The three required elements are sourced in the two schema-B
manifests above; nothing is sourced for Fig. 3 or Fig. 4.

---

## 5. Claims with no number, where the number exists

| line | hedge | underlying figure | assessment |
|---|---|---|---|
| L146 | "Both surrogates **accurately** predict the minimum post-contingency voltage" | ridge MAE 3.8e-3 pu, R² 0.77; the escalation band is 5.2e-3 pu and the boundary strip 5e-3 pu | **Borderline.** Ridge's mean error is comparable to the decision band itself. The numbers follow in the same sentence, so a reader is not misled — but "accurately" is doing unearned work for the linear model |
| L230 | "**Only a few** misses were serious" | at 0.90, **26.7\%** of ridge misses and **21.4\%** of histgb misses fall deeper than the 0.005-pu strip; p99 depth 0.0350 / 0.0460 pu (`missed_depth.json` `.pooled['0.90']`) | **OVERSTATES the rarity.** Roughly one miss in four or five is deeper than the boundary strip. "A few" is not defensible against 26.7\% |
| Fig. 3 cap / L224 | "**Most** misses stay within one band" | ridge 73.7\%, histgb **54.9\%**; pooled across both models 62.2\% | **Holds, barely.** A majority in both cases, but 54.9\% is a coin-flip for the model the paper deploys. The caption is model-agnostic where the two values differ by 19 pp |
| L234 | "The **majority** of contingencies are within 0.005 per unit **of** the boundary" | 56.86\% in **[0.94, 0.945)**, i.e. within 0.005 pu **above**; 74.34\% are below 0.945 either side | **Matches** on the majority claim; "of the boundary" reads two-sided where the artifact is one-sided. The exact interval is given in the next sentence, which repairs it |
| L247 | ceiling "**essentially** lands on the saturation point" | 82.79\% vs 82.52\%, Δ = 0.27 pp; histgb ceiling std ±0.37 pp, ridge ±0.83 pp | **CORRECTLY hedged.** The gap is below one σ, so by `CLAUDE.md` §8's std rule it is not a real difference — "essentially" is exactly right |
| L249 | "**barely** faster than the solver" (persistence) | 1.0047 ± 0.0017 | **Matches** |
| L249 | "instead of the **2 to 3 times** available at 0.90" | ridge 2.043, histgb **3.287** | **UNDERSTATES.** The upper end is 3.29, above the stated range. IV/L146 and Table I both print 3.29 two pages earlier |
| L230 | histgb is "**far more** accurate than the linear one" | MAE 1.563 vs 3.754 e-3 (Δ 2.19, larger σ 0.133); R² 0.9227 vs 0.7718 (Δ 0.151, larger σ 0.0134) | **Supported.** Both gaps exceed the larger std by >10× |
| L259 | "In other words, it finds **everything** hazardous" | at a 0.95 pu limit, **95.61\%** of converged N-1 rows have `min_vm < 0.95`; ridge escalation collapses to 1.38\% | **Supported** |
| L261 | "**roughly one-quarter** of converged rows" | 24.93\% | **Matches** |
| L267 | "escalating **around two-thirds** of cases" | 64.34\% / 63.68\% | **Matches** |
| L267 | "The speedup ... decreases enough to be **comparable to the speed of the solver itself**" | 1.557× and 1.579× net | **Overstates in the conservative direction.** 56-58\% faster is not "comparable to the solver". The honest phrasing is the one already used at L249 ("about a 1.6 times speedup") |
| L94 | "up to **several milliseconds** for one scenario" | 9.14 ms min, 9.561 ms mean | **Matches** |
| L94 | "a **fraction of a millisecond**" for the surrogate | 0.00116 ms (ridge) / 0.00241 ms (histgb), `tm` `.records[].ms_surrogate` | **Matches**, with three orders of magnitude to spare |
| L247 | "so **much** of the distribution sits just above 0.94" | 56.86\% | **Matches** |
| L259 | "leads to a ridge escalation of 1.38±0.33\%" | true at **coverage target 0.90** (`escalation_at_095.json` `.coverage_target`) | **Under-specified**, not wrong. Every other escalation figure in the paper names its coverage target; this one does not, and it is quoted in a paragraph whose other numbers are at 0.96/0.97 |

---

## 6. Incidental (outside the four checks, one line each)

- L261: "occuring" → "occurring". Sole spelling defect found in the body.

---

## 7. Summary

### Verdict counts

| | |
|---|---|
| **Numbers** — CORRECT | **75** |
| **Numbers** — AGGREGATION-MISMATCH | **1** |
| **Numbers** — WRONG / UNSOURCED / SUPERSEDED | **0 / 0 / 0** |
| **Citations** — source supports the claim | 15 keys / 17 attachments |
| **Citations** — PARTIAL | 3 attachments |
| **Citations** — does not support | 1 (`barber2021`, known) |
| **Citations** — `\cite` with no `\bibitem` | 0 |
| **Citations** — `\bibitem` never cited | 0 |
| **Citations** — `{18}` vs bibitem count | 18 = 18, matches |
| **Internal consistency** — contradictions | 2 new (§3.2, §3.3) + 1 dataset-ambiguity (§3.1) |
| **LaTeX** — broken `\ref` / missing graphics file / unbalanced env / non-ASCII | 0 / 0 / 0 / 0 |
| **LaTeX** — build-blocking issue | 1 (graphics path, §4) |
| **Provenance** — figures without a manifest | 1 (Fig. 4) |
| **Hedges** — overstated | 3 (L230 "only a few", L249 "2 to 3 times", L267 "comparable to the solver") |

**Every numeral in the body reconciles with an artifact.** The paper's arithmetic is sound; not one
value is wrong, unsourced, or drawn from a superseded result set. That is the headline of §1.

### Single highest-severity finding

**§3.2 — the safety claim is scoped to a population no reported number is computed over.**

The Discussion restricts the paper's safety claims to "the specific set of N-1 branch-contingency
cases", excluding the 24.93\% of converged rows that also carry a generator outage. No metric in
the paper — not Table I, not Table II, not Fig. 2, not the abstract — is computed on that
restricted set, and no artifact in the repository contains one. The two populations are measurably
different (violation rate 18.24\% vs 17.22\%; boundary-strip share 58.10\% vs 56.45\%,
`data/sampling_audit.json`). Unlike the wording issues on the known-unfixed list, this cannot be
resolved by editing the sentence alone: either the branch-only metrics get produced, or the
sentence must state plainly that the reported numbers are measured over the full mixed population
and the restriction is aspirational.

Runner-up: **§3.3** — the Introduction's first differentiator ("unlike the first two approaches, we
add a band to each contingency") is contradicted four sentences earlier by the paper's own
description of Alcántara as using conformal prediction, and asserts a conformal-method novelty that
`CLAUDE.local.md` rules out.

---

*Method note: no `.tex` file was written, no git command that writes was run, and
`.venv/bin/python` was the only interpreter used. Two live fetches were made, both read-only and
both for citation-claim verification: `proceedings.mlr.press/v283/christianson25a.html` and
`arxiv.org/pdf/2410.00796` (2026-08-27).*
