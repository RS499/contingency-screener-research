# Number check — `report/paper_current_STS.tex`

**Date:** 2026-09-27.
**File checked:** working tree, 460 lines, sha256 `c86e47d6…`. It changed since the 09-23 review: the
edits at the "I add the solver time…", "To confirm its reliability…", "Apple M5 processor", "contingencies
include…" and "scaling the initial network load…" sentences. No number changed.
**Method:** every item was re-found by its surrounding **text**, not by line number. Line numbers
below are for navigation only.

**Scripts (all read-only, `.venv/bin/python scratch/<name>.py`):**
- `extract_literals.py` finds every numeric literal.
- `number_check.py` maps each literal to its intended data key, recomputes it, and emits the table in §7.
- `std_rule_check.py` covers §3 and §4.
- `provenance_sts.py` is the repo matcher, re-run as a cross-check.

None of them writes a file.

**VERIFIED** in this file means I recomputed the value myself from the named file. Nothing here is
marked VERIFIED on the strength of the review or a reviewer subagent.

---

## 1. Summary

**Scope.** 443 numeric-literal occurrences in the body (title through Acknowledgments, including the
abstract, captions, both tables, and the figure/table attribution lines), across 56 lines.

**Excluded, and counted separately:**
- 75 tokens that are names or layout, not quantities: `case118`-style network ids, N-0/N-1/N-2,
  F1–F4, R², `\cite`/`\label` keys, `\setstretch{1.5}`, figure widths, and the `($10^{-3}$ pu)`
  unit in the Table I header;
- the bibliography: volume, page, year and DOI fields are citation metadata and are covered by
  `notes/prior-art.md`, not by this check.

| Status | Count | What it means here |
|---|---|---|
| **MATCH** | **432** | 316 measured results, 85 design constants, 16 network sizes used as names (for example "118-bus"), 10 figure-attribution fields, 4 hedged threshold claims ("slightly above 1%", "touching the 1%"), and 1 definition (1.0 pu = nominal) |
| **ROUNDING** | **1** | "…reach up to about 1.0–**1.07**%". mean + std = 0.8322 + 0.2447 = **1.0769 → 1.08** (`data/tradeoff_curve_v2.json` → `records[histgb, 0.97].missed_viol + missed_viol_std`). It comes from adding two already-rounded numbers (0.83 + 0.24). |
| **MISMATCH** | **0** | — |
| **NO SOURCE** | **10** | 8 have no `data/*.json` key but agree when recomputed from `data/dataset.parquet` (§2). 2 are table attribution years with no recorded build date. |

Every design constant was verified against the value actually run, not echoed back:
- targets appear in `data/tradeoff_curve_v2.json` → `coverage_levels`;
- 0.95 appears in `data/escalation_at_095.json` → `limits`;
- 0.94 is `data/tradeoff_curve_v2.json` → `limit`.

**Std rule.** Four directional claims fail it (§3). One of them, the operating points "below 1%", is
already hedged in the text.

**Formatting.** One quantity is printed two ways at equal precision (56.86 vs 56.9). The other
repeats are deliberate hedges (§4).

**Fig. 5.** Correct: the IEEE 1-based labels 76 / 53 / 107 (§5).

**Review §2b / §2c.** Every item is still present (§6). Nothing was fixed between 09-23 and today.

---

## 2. NO SOURCE items (no `data/*.json` key)

| Line | Search text | Printed | Recomputed (VERIFIED from the parquet / code named) | Agrees? |
|---|---|---|---|---|
| 119 | "For Independent mode (750" | 750 | 750 (`data/dataset.parquet`, base rows, `sampling_mode == "independent"`) | yes |
| 119 | "For Regional mode (750" | 750 | 750 (same, `"regional"`) | yes |
| 119 | "from 0.9009 to 1.2310" | 0.9009 | 0.900858 (`pload_i` / case118 per-bus base `p_mw`, regional bases, min) | yes (→ 0.9009) |
| 119 | same | 1.2310 | 1.2310 (same, max) | yes |
| 119 | "(43.91\% outside" | 43.91 | 43.9057 (share of regional per-bus multipliers outside [1.0, 1.12]) | yes (→ 43.91) |
| 119 | "range from 0.8156 to 1.4083" | 0.8156 | 0.815637 (`qload_i` / case118 per-bus base `q_mvar`, all bases, min) | yes |
| 119 | same | 1.4083 | 1.4083 (same, max) | yes |
| 323 | "below which 0.5\%" | 0.5 | 0.5413 (converged N-1 rows with `min_vm` < 0.87) | yes (→ 0.5) |
| 223 | Table I attribution "…\LaTeX, 2026" | 2026 | No manifest records a table build date. `data/tradeoff_curve_v2.manifest.json` has no date field. | not checked |
| 265 | Table II attribution | 2026 | same | not checked |

**Fix.** Emit one small artifact with a manifest, for example `data/sampling_ranges.json`, holding the
mode counts, the P/Q multiplier ranges, the out-of-range share and the below-0.87 share. That
satisfies the project's "every number from a JSON key" rule. I did not create it, because it would be
a new `data/` file and this task limited new files to `scratch/` and `notes/`.

---

## 3. Mean ± std claims (project std rule: a difference is real only if the gap exceeds the larger std)

Every row below is VERIFIED from the named file; population std (ddof = 0) over 5 splits.

| Search text | Claim | Values | Gap | Larger std | Verdict |
|---|---|---|---|---|---|
| "falling below 1\% at 0.94" / "first going just under a 1\% mean" | ridge@0.94 missed "below 1%" | 0.7935 ± 0.209 | 0.2065 | 0.209 | **FAILS** (by 0.003). The text hedges it ("error bars still reach…"). |
| same | histgb@0.97 missed "below 1%" | 0.8322 ± 0.245 | 0.168 | 0.245 | **FAILS**. Hedged the same way. |
| "so its ceiling lands just above the saturation point" | histgb ceiling > saturation | 82.79 ± 0.37 vs 82.64 ± 0.17 | 0.16 | 0.37 | **FAILS**. "Above" is not supported; say "at". |
| "slightly better on absolute error at 0.1056 versus 0.1163" | B beats A on absolute error | 0.1056 ± 0.114 vs 0.1163 ± 0.210 (spread over the 54 comparisons) | 0.011 | 0.21 | **FAILS**. "Not clearly more accurate" is right; "slightly better" is not. |
| "not safer at any point in the coverage axis" | ridge misses less than histgb at each of 0.90 / 0.94 / 0.95 / 0.96 / 0.97 / 0.98 | e.g. 0.96: 0.14 ± 0.07 vs 1.36 ± 0.20 | 0.30–1.75 | 0.13–0.98 | passes at all 6 targets (at *matched target*; review C8 is about matched *escalation*) |
| "much more accurate than the linear model" | MAE (×10⁻³) | 1.563 ± 0.076 vs 3.754 ± 0.133 | 2.19 | 0.133 | passes |
| "3.29 times speedup compared to 2.04" | speedup at 0.90 | 3.29 ± 0.30 vs 2.04 ± 0.11 | 1.24 | 0.30 | passes |
| "lower escalation ceiling of 74.89\% versus 82.79" | ridge ceiling < histgb | 74.89 ± 0.83 vs 82.79 ± 0.37 | 7.9 | 0.83 | passes |
| "coverage is close to 90" | no-difference claim | 89.34 ± 1.30; 89.82 ± 0.98 | 0.66; 0.18 | 1.30; 0.98 | passes (gap < std) |
| "run the models at a 0.94 or a 0.97" | the two points treated as equivalent | missed 0.79 ± 0.21 vs 0.83 ± 0.24; escalation 64.3 ± 2.8 vs 63.7 ± 5.1 | 0.04; 0.66 | 0.24; 5.1 | passes as a no-difference claim. Miss *depth* differs: see placement plan E9. |
| "The additional features contribute no meaningful increase" | +F1, +F1+F3 (ridge), all histgb configs vs baseline | e.g. histgb +F1+F2+F3+F4: 1526 ± 111 vs 1563 ± 76 (×10⁻⁶) | ≤ 63 | ≥ 76 | passes (all 12 no-difference cells) |
| "the ridge MAE increases by +10.82\%" / "greater than seed variability regardless…" | ridge +F1+F2 vs baseline, searched and fixed | 4161 ± 247 and 4181 ± 254 vs 3754 ± 133 | 406; 427 | 247; 254 | passes in both modes |
| "falls within normal seed variation" | F1 real vs shuffled | 1553.9 vs 1530.0 (single seed) | 23.9 | 75.8 (between-seed) | passes as stated. Caveat (review ST-M6): a paired difference is being compared with an unpaired std. |

Source keys: `data/tradeoff_curve_v2.json` → `records[*]`; `data/tuned_metrics.json` → `records[metric=m2]`
(`mae`, `p_pred_below_limit` for the ceilings); `data/flag_confusion_long.parquet` (per-seed test
violation rate for saturation); `data/netstudy2/summary.json` → `cross_comparisons[].abs_err_A|B`;
`data/physics_ablation.json` → `records[]`; `data/f1_leakage_audit.json` → `check_4_permutation`.

---

## 4. Same quantity, different printed forms

Grouped by the data key each literal resolves to (`scratch/std_rule_check.py`, second table).

| Quantity | Forms (line) | Verdict |
|---|---|---|
| boundary mass [0.94, 0.945) | `56.86` (81, 121, 314, 365); `56.9` (323, Fig. 4 caption) | **Inconsistent**; pick one precision. The review flagged the same. |
| missed mean + std at histgb@0.97 | `1` (81, 281, 349: "slightly above 1%", "touching the 1%"); `1.07` (231) | 1.07 should be 1.08 (§1). The three hedged forms are consistent with 1.08. |
| tallest 0.001 pu bin | `14` (314, "about 14%"); `14.1` (323) | hedged word, consistent |
| solver time | `9` (109, "around 9 milliseconds"); `9.14` (147) | hedged word, consistent |
| histgb speedup at 0.90 / 0.97 | `3.29` / `1.58` (throughout); `3.3` / `1.6` (349, "about") | hedged words, consistent |
| ridge speedup at 0.90 / 0.94 | `2.04` / `1.56`; `2` (349, "2 to 3.3 times"), `1.6` (388, "a speed-up factor of 1.6") | line 388 gives no hedge word, so 1.6 there stands for 1.56 / 1.58 unqualified. Minor. |
| 90% operating point | `90` with "%" (81, 132, 199, 208, 303, 388); `0.90` (231, 292, 349) | Same quantity written two ways. Pick one notation for "coverage target". |
| critical-bus shares | `27.1`, `16.81`, `9.31` (314, 339) | The source stores 27.1 because 27.10 dropped its trailing zero. Print `27.10` for one precision. |
| clip-era boundary mass | `55.5` next to `56.86` (121) | Source is 55.51; mixed precision in one sentence. |

---

## 5. Fig. 5 bus labels

- The code labels `bus {b + 1}`, where `b` is the 0-based pandapower index (`feasibility/domain_figure.py:97`).
  The summary line (`:110`) also adds 1 and calls it the "IEEE name".
- Rendered PNG (`data/critical_bus_map.png`, hash matches its manifest): the labels read **bus 76
  (27%), bus 53 (17%), bus 107 (9%)**, plus bus 1 (8%) and bus 21 (4%). These are IEEE 1-based.
- Text and caption: "bus 76 … bus 53 … bus 107" and "76, 53, and 107" match
  `data/frozen_poster_numbers_v2.json` → `dataset_facts.critical_bus_top5[0..2].bus` (75 / 52 / 106) + 1.
- **Consistent.**

Two side notes, not errors:
- The PNG still has an in-image title ("IEEE 118-bus: critical-bus frequency across 278,955 converged
  N-1 cases") and a footer line. The other figures were made prose-free for STS; this one was not.
- The image labels two more buses (1 and 21) than the caption mentions.

---

## 6. Review §2b / §2c: still present or fixed?

| Review item | Search text | Status 2026-09-27 |
|---|---|---|
| §2b "1.0–1.07%" (should be 1.08) | "reach up to about 1.0--1.07" | **still present** (ROUNDING) |
| §2b 55.5 vs 56.86 mixed precision | "moving from 55.5\% to 56.86" | **still present** |
| §2b 56.86 (text) vs 56.9 (caption) | "holds 56.9\%" | **still present** |
| §2b 27.1 / 16.81 / 9.31 mixed precision | "showing the minimum voltage in 27.1" | **still present** |
| §2b ceiling "just above" saturation (std rule) | "lands just above the saturation point" | **still present**; fails the std rule (§3) |
| §2b t_surr histgb 0.00241 vs re-measure 0.00346 | "$0.00241\pm0.00062$" | **still present**. It matches its committed source (`data/tuned_metrics.json` m2 `ms_surrogate`); the re-measure is `data/break_even.json` → `timing.ms_infer_measured_now.histgb` = 0.003456. |
| §2c 0.9009–1.2310, 43.91% | "from 0.9009 to 1.2310" | **still NO SOURCE**; recomputed values agree (§2) |
| §2c 0.8156–1.4083 | "range from 0.8156 to 1.4083" | **still NO SOURCE**; agrees |
| §2c 750 / 750 | "Independent mode (750" | **still NO SOURCE**; agrees |
| §2c 0.5% below 0.87 | "below which 0.5\%" | **still NO SOURCE**; agrees (0.54) |
| §2c 0.000247, 0.004161 | "+F1+F2 $0.004161" | Traceable. Recomputed from `data/physics_ablation.json` → `records[+F1+F2, ridge, m2_searched].mae` (mean 0.0041610, pop. std 0.0002473). There is no *summary* key, but the records are a data file, so I count it as sourced. The repo matcher still lists it as an orphan because it matches only leaves. |
| Repo checker banned phrases | "are proven methods" (361); "This escalation floor is set by" (365) | **still present** (`scripts/check_paper.py` `PHRASE_REGEXES`) |

**Cross-check with the repo matcher** (`scratch/provenance_sts.py`, today): 207 matched, 6 orphans
(0.000247, 0.004161, 0.9009, 43.91, 392, 750), 5 ambiguous. This is identical to the review.
- `392` is an orphan only because the source holds 392.2137. It is VERIFIED here as `worst_trafos_at_nominal[0].loading_pct`.
- The wording "the transformers, at nominal load, were at 392%" describes the *worst* transformer
  (review C-note).

---

## 7. Full table

Every occurrence, in reading order.

**Columns:**
- **Kind:** result = measured; config = design constant checked against what was run; name =
  network size used as a name; meta = figure attribution; nokey = no JSON key; claim>1 / claim~1 = a
  hedged threshold claim ("slightly above 1%", "touching 1%").
- **Recomputed:** in the paper's printed units (%, pu, ms, ×10⁻³ for Table I MAE).
- The `90`/`0.90` operating-point rows resolve to `data/tradeoff_curve_v2.json` → `operating_point` (0.9).

| Line | Printed | Kind | Source file → key | Recomputed | Status |
|---|---|---|---|---|---|
| 81 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 81 | 118 | name | data/network_triage.json → networks[case118].n_bus | 118 | MATCH |
| 81 | 90 | config | data/tradeoff_curve_v2.json → operating_point | 90 | MATCH |
| 81 | 3.29 | result | data/tradeoff_curve_v2.json → .net_speedup | 3.2871 | MATCH |
| 81 | 4.72 | result | data/tradeoff_curve_v2.json → .missed_viol | 4.7167 | MATCH |
| 81 | 1 | config | data/tuning_search.json → inner_missed_ceiling | 1 | MATCH |
| 81 | 0.97 | result | data/frozen_poster_numbers_v2.json → crossings_first_below_1pct_missed.histgb | 0.97 | MATCH |
| 81 | 63.7 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 63.6795 | MATCH |
| 81 | 1.58 | result | data/tradeoff_curve_v2.json → .net_speedup | 1.5791 | MATCH |
| 81 | 1 | claim>1 | data/tradeoff_curve_v2.json → missed_viol + missed_viol_std | 1.0769 | MATCH |
| 81 | 30 | name | data/network_triage.json → networks[case30].n_bus | 30 | MATCH |
| 81 | 30 | name | data/network_triage.json → networks[case30].n_bus | 30 | MATCH |
| 81 | 7.09 | result | data/case30_thermal/case30_thermal_frozen.json → boundary_mass_pct | 7.0862 | MATCH |
| 81 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 81 | 0.945 | config | data/unconditioned_base.json → strip_hi | 0.945 | MATCH |
| 81 | 56.86 | result | data/frozen_poster_numbers_v2.json → dataset_facts.boundary_0p94_to_0p945_pct | 56.8600 | MATCH |
| 81 | 0.97 | result | data/case30_thermal/case30_thermal_frozen.json → first target with all 5 histgb splits < 1% | 0.97 | MATCH |
| 81 | 5.84 | result | data/case30_thermal/case30_thermal_frozen.json → records[histgb, target].escalation | 5.8358 | MATCH |
| 81 | 1.25 | result | data/case30_thermal/case30_thermal_frozen.json → records[histgb, target].escalation (pop. std) | 1.2505 | MATCH |
| 107 | 1.0 | definition | definition (1.0 pu = nominal) | — | MATCH |
| 107 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 107 | 6 | result | arithmetic: 1 − 0.94 = 0.06 → 6% | 6 | MATCH |
| 107 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 107 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 107 | 73.1 | result | data/thermal_check.json → networks.case118.overvoltage.n1.share_above_1p05 | 73.1358 | MATCH |
| 107 | 1.05 | config | data/thermal_check.json → over_voltage_threshold | 1.0500 | MATCH |
| 107 | 9,900 | result | data/thermal_check.json → networks.case118.rating_audit.trafo_sn_mva / line implied_mva (both 9900) | 9,900 | MATCH |
| 109 | 9 | result (hedged, tol ±0.5) | data/solve_time.json → ms_solver | 9.1400 | MATCH |
| 111 | 118 | name | data/network_triage.json → networks[case118].n_bus | 118 | MATCH |
| 111 | 118 | name | data/network_triage.json → networks[case118].n_bus | 118 | MATCH |
| 111 | 173 | result | data/thermal_check.json → networks.case118.rating_audit.n_lines | 173 | MATCH |
| 111 | 13 | result | data/thermal_check.json → networks.case118.rating_audit.n_trafos | 13 | MATCH |
| 111 | 186 | result | data/break_even.json → generation.branches | 186 | MATCH |
| 119 | 750 | nokey | NO KEY — data/dataset.parquet → base rows, sampling_mode == independent | 750 | NO SOURCE |
| 119 | 1.0 | config | data/sampling_audit.json → multiplier_audit.multiplier_range_as_invoked ('U(1.0, 1.12)') | 1 | MATCH |
| 119 | 1.12 | config | data/sampling_audit.json → multiplier_audit.multiplier_range_as_invoked ('U(1.0, 1.12)') | 1.1200 | MATCH |
| 119 | 750 | nokey | NO KEY — data/dataset.parquet → base rows, sampling_mode == regional | 750 | NO SOURCE |
| 119 | 0.9009 | nokey | NO KEY — dataset.parquet pload_i / case118 p_mw, regional bases, min | 0.900858 | NO SOURCE |
| 119 | 1.2310 | nokey | NO KEY — dataset.parquet pload_i / case118 p_mw, regional bases, max | 1.2310 | NO SOURCE |
| 119 | 43.91 | nokey | NO KEY — share of regional per-load multipliers outside [1.0, 1.12] | 43.9057 | NO SOURCE |
| 119 | 1.0 | config | data/sampling_audit.json → multiplier_audit.multiplier_range_as_invoked ('U(1.0, 1.12)') | 1 | MATCH |
| 119 | 1.12 | config | data/sampling_audit.json → multiplier_audit.multiplier_range_as_invoked ('U(1.0, 1.12)') | 1.1200 | MATCH |
| 119 | 1,500 | result | data/frozen_poster_numbers_v2.json → dataset_facts.scenarios | 1,500 | MATCH |
| 119 | 0.8156 | nokey | NO KEY — dataset.parquet qload_i / case118 q_mvar, all bases, min | 0.815637 | NO SOURCE |
| 119 | 1.4083 | nokey | NO KEY — dataset.parquet qload_i / case118 q_mvar, all bases, max | 1.4083 | NO SOURCE |
| 119 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 119 | 30 | config | data/sampling_audit.json → outage_probability.as_coded | 30 | MATCH |
| 119 | 374 | result | data/sampling_audit.json → prevalence.n_base_with_generator_outage | 374 | MATCH |
| 119 | 1,500 | result | data/frozen_poster_numbers_v2.json → dataset_facts.scenarios | 1,500 | MATCH |
| 119 | 24.93 | result | data/sampling_audit.json → prevalence.share_of_base_scenarios | 24.9333 | MATCH |
| 119 | 186 | result | data/break_even.json → generation.branches | 186 | MATCH |
| 119 | 1,500 | result | data/frozen_poster_numbers_v2.json → dataset_facts.scenarios | 1,500 | MATCH |
| 119 | 280,500 | result | data/frozen_poster_numbers_v2.json → dataset_facts.rows | 280,500 | MATCH |
| 119 | 1,500 | result | data/break_even.json → generation.base_solves_accepted | 1,500 | MATCH |
| 119 | 279,000 | result | data/break_even.json → generation.n1_solves | 279,000 | MATCH |
| 119 | 279,000 | result | data/break_even.json → generation.n1_solves | 279,000 | MATCH |
| 119 | 45 | result | data/element_conditional_escalation.json → n_nonconverged | 45 | MATCH |
| 119 | 278,955 | result | data/frozen_poster_numbers_v2.json → dataset_facts.converged_n1_rows | 278,955 | MATCH |
| 119 | 0.7179 | result | data/frozen_poster_numbers_v2.json → dataset_facts.min_vm_min | 0.7179 | MATCH |
| 119 | 0.9603 | result | data/frozen_poster_numbers_v2.json → dataset_facts.min_vm_max | 0.9603 | MATCH |
| 119 | 17.48 | result | data/frozen_poster_numbers_v2.json → dataset_facts.violation_rate_pct | 17.4800 | MATCH |
| 119 | 30 | name | data/network_triage.json → networks[case30].n_bus | 30 | MATCH |
| 119 | 111.83 | result | data/network_triage.json → networks[case30].base_max_loading_pct | 111.831 | MATCH |
| 119 | 30 | name | data/network_triage.json → networks[case30].n_bus | 30 | MATCH |
| 119 | 100 | config | data/network_triage.json → criteria.thermal_max_pct | 100 | MATCH |
| 119 | 0.87 | config | data/case30_thermal/h3_build_stats.json → range.lo | 0.87 | MATCH |
| 119 | 0.99 | config | data/case30_thermal/h3_build_stats.json → range.hi | 0.99 | MATCH |
| 119 | 100 | result (hedged, tol ±0.01) | data/case30_thermal/h3_build_stats.json → max_base_loading_pct | 99.9993 | MATCH |
| 119 | 41 | result | data/network_triage.json → networks[case30].n_branch_n1 | 41 | MATCH |
| 119 | 186 | result | data/break_even.json → generation.branches | 186 | MATCH |
| 119 | 1,500 | result | data/case30_thermal/h3_build_stats.json → n_accepted | 1,500 | MATCH |
| 119 | 61,500 | result | data/case30_thermal/h3_build_stats.json → n1_loading.n | 61,500 | MATCH |
| 121 | 0.94 | config | feasibility/generate_dataset.py:10 GEN_VM_LO; data/archive_clip/README.md:4 ('CLIPPED at the 0.94') | 0.94 | MATCH |
| 121 | 0.940000 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 121 | 1×10^{-9} | config | data/clip_artifact.json → atom_definition ('rounded to 9 decimals' = ±0.5e-9, inside the printed ±1e-9) | 1e-09 | MATCH |
| 121 | 35.17 | result | data/clip_artifact.json → clip_era.clip_atom_share_pct | 35.1700 | MATCH |
| 121 | 76 | result | data/clip_artifact.json → clip_era.atom_top_buses[0].ieee_bus | 76 | MATCH |
| 121 | 0.943 | result | pandapower case118() → gen at bus index 75 (IEEE 76) .vm_pu | 0.943 | MATCH |
| 121 | 0.940000 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 121 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 121 | 0.945 | config | data/unconditioned_base.json → strip_hi | 0.945 | MATCH |
| 121 | 55.5 | result | data/clip_artifact.json → clip_era.boundary_0p94_to_0p945_pct | 55.5100 | MATCH |
| 121 | 56.86 | result | data/frozen_poster_numbers_v2.json → dataset_facts.boundary_0p94_to_0p945_pct | 56.8600 | MATCH |
| 124 | 60 | config | data/splits.json → train_frac | 60 | MATCH |
| 124 | 20 | config | data/splits.json → cal_frac / test_frac | 20 | MATCH |
| 124 | 20 | config | data/splits.json → cal_frac / test_frac | 20 | MATCH |
| 124 | 1 | config | data/tuning_search.json → inner_missed_ceiling | 1 | MATCH |
| 132 | 90 | config | data/tradeoff_curve_v2.json → operating_point | 90 | MATCH |
| 132 | 0.0052 | result | data/tradeoff_curve_v2.json → .q_hat | 0.00519823 | MATCH |
| 132 | 0.0023 | result | data/tradeoff_curve_v2.json → .q_hat | 0.0022907 | MATCH |
| 136 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 147 | 9.14 | result | data/solve_time.json → ms_solver | 9.1400 | MATCH |
| 147 | 400 | result | data/solve_time.json → n_timed | 400 | MATCH |
| 147 | 0.00116 | result | data/tuned_metrics.json → records[family, metric=m2].ms_surrogate | 0.00116278 | MATCH |
| 147 | 0.00012 | result | data/tuned_metrics.json → records[family, metric=m2].ms_surrogate (pop. std) | 0.000121601 | MATCH |
| 147 | 0.00241 | result | data/tuned_metrics.json → records[family, metric=m2].ms_surrogate | 0.00241106 | MATCH |
| 147 | 0.00062 | result | data/tuned_metrics.json → records[family, metric=m2].ms_surrogate (pop. std) | 0.000616286 | MATCH |
| 155 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 158 | 3.11.1 | meta | data/gate_schematic_v4.manifest.json → plotting_library | matplotlib 3.11.1 | MATCH |
| 158 | 2026 | meta | data/gate_schematic_v4.manifest.json → generated_utc | 2026 | MATCH |
| 167 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 189 | 118 | name | data/network_triage.json → networks[case118].n_bus | 118 | MATCH |
| 189 | 0.6038 | result | data/barrier_height.json → summary_at_090.case118.ridge.S_mean_over_qhat_at_090_mean | 0.603785 | MATCH |
| 189 | 0.0757 | result | data/barrier_height.json → …S_mean_over_qhat_at_090_std | 0.0756853 | MATCH |
| 189 | 0.7919 | result | data/barrier_height.json → summary_at_090.case118.histgb.S_mean_over_qhat_at_090_mean | 0.79193 | MATCH |
| 189 | 0.0743 | result | data/barrier_height.json → …S_mean_over_qhat_at_090_std | 0.0743288 | MATCH |
| 199 | 0.77 | result | data/tuned_metrics.json → records[family, metric=m2].r2 | 0.771834 | MATCH |
| 199 | 0.92 | result | data/tuned_metrics.json → records[family, metric=m2].r2 | 0.922718 | MATCH |
| 199 | 0.0038 | result | data/tuned_metrics.json → records[family, metric=m2].mae (pu) | 0.00375433 | MATCH |
| 199 | 0.0016 | result | data/tuned_metrics.json → records[family, metric=m2].mae (pu) | 0.00156273 | MATCH |
| 199 | 90 | config | data/tradeoff_curve_v2.json → operating_point | 90 | MATCH |
| 199 | 49.1 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 49.0697 | MATCH |
| 199 | 89.3 | result | data/tradeoff_curve_v2.json → .coverage_emp | 89.3390 | MATCH |
| 199 | 2.96 | result | data/tradeoff_curve_v2.json → .missed_viol | 2.9632 | MATCH |
| 199 | 2.04 | result | data/tradeoff_curve_v2.json → .net_speedup | 2.0431 | MATCH |
| 199 | 30.6 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 30.6251 | MATCH |
| 199 | 89.8 | result | data/tradeoff_curve_v2.json → .coverage_emp | 89.8175 | MATCH |
| 199 | 3.29 | result | data/tradeoff_curve_v2.json → .net_speedup | 3.2871 | MATCH |
| 199 | 4.72 | result | data/tradeoff_curve_v2.json → .missed_viol | 4.7167 | MATCH |
| 199 | 90 | config | data/tradeoff_curve_v2.json → operating_point | 90 | MATCH |
| 208 | 90 | config | data/tradeoff_curve_v2.json → operating_point | 90 | MATCH |
| 215 | 4.2 | result | data/screener_metrics.json → records[model=persistence].mae (×10³) | 4.2457 | MATCH |
| 215 | 0.1 | result | data/screener_metrics.json → records[model=persistence].mae (×10³, pop. std) | 0.0706315 | MATCH |
| 215 | -0.06 | result | data/screener_metrics.json → records[model=persistence].r2 | -0.0611382 | MATCH |
| 215 | 0.00 | result | data/screener_metrics.json → records[model=persistence].r2 (pop. std) | 0.00322352 | MATCH |
| 215 | 99.5 | result | data/screener_metrics.json → records[model=persistence].escalation | 99.5336 | MATCH |
| 215 | 0.2 | result | data/screener_metrics.json → records[model=persistence].escalation (pop. std) | 0.163619 | MATCH |
| 215 | 0.31 | result | data/screener_metrics.json → records[model=persistence].missed_viol | 0.310986 | MATCH |
| 215 | 0.08 | result | data/screener_metrics.json → records[model=persistence].missed_viol (pop. std) | 0.0798257 | MATCH |
| 215 | 1.00 | result | data/screener_metrics.json → records[model=persistence].net_speedup | 1.0047 | MATCH |
| 215 | 0.00 | result | data/screener_metrics.json → records[model=persistence].net_speedup (pop. std) | 0.00165267 | MATCH |
| 216 | 6.7 | result | data/screener_metrics.json → records[model=train_mean].mae (×10³) | 6.7316 | MATCH |
| 216 | 0.2 | result | data/screener_metrics.json → records[model=train_mean].mae (×10³, pop. std) | 0.172632 | MATCH |
| 216 | -0.00 | result | data/screener_metrics.json → records[model=train_mean].r2 | -0.000209725 | MATCH |
| 216 | 0.00 | result | data/screener_metrics.json → records[model=train_mean].r2 (pop. std) | 0.000213228 | MATCH |
| 216 | 0.0 | result | data/screener_metrics.json → records[model=train_mean].escalation | 0 | MATCH |
| 216 | 0.0 | result | data/screener_metrics.json → records[model=train_mean].escalation (pop. std) | 0 | MATCH |
| 216 | 0.00 | result | data/screener_metrics.json → records[model=train_mean].missed_viol | 0 | MATCH |
| 216 | 0.00 | result | data/screener_metrics.json → records[model=train_mean].missed_viol (pop. std) | 0 | MATCH |
| 217 | 3.8 | result | data/tuned_metrics.json → records[family, metric=m2].mae (×10³, seed mean) | 3.7543 | MATCH |
| 217 | 0.1 | result | data/tuned_metrics.json → records[family, metric=m2].mae (×10³, pop. std) | 0.132771 | MATCH |
| 217 | 0.77 | result | data/tuned_metrics.json → records[family, metric=m2].r2 | 0.771834 | MATCH |
| 217 | 0.01 | result | data/tuned_metrics.json → records[family, metric=m2].r2 (pop. std) | 0.0133696 | MATCH |
| 217 | 49.1 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 49.0697 | MATCH |
| 217 | 2.7 | result | data/tradeoff_curve_v2.json → .escalation_std | 2.6608 | MATCH |
| 217 | 2.96 | result | data/tradeoff_curve_v2.json → .missed_viol | 2.9632 | MATCH |
| 217 | 0.44 | result | data/tradeoff_curve_v2.json → .missed_viol_std | 0.439389 | MATCH |
| 217 | 2.04 | result | data/tradeoff_curve_v2.json → .net_speedup | 2.0431 | MATCH |
| 217 | 0.11 | result | data/tradeoff_curve_v2.json → .net_speedup_std | 0.105697 | MATCH |
| 218 | 1.6 | result | data/tuned_metrics.json → records[family, metric=m2].mae (×10³, seed mean) | 1.5627 | MATCH |
| 218 | 0.1 | result | data/tuned_metrics.json → records[family, metric=m2].mae (×10³, pop. std) | 0.0757534 | MATCH |
| 218 | 0.92 | result | data/tuned_metrics.json → records[family, metric=m2].r2 | 0.922718 | MATCH |
| 218 | 0.00 | result | data/tuned_metrics.json → records[family, metric=m2].r2 (pop. std) | 0.00384683 | MATCH |
| 218 | 30.6 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 30.6251 | MATCH |
| 218 | 2.5 | result | data/tradeoff_curve_v2.json → .escalation_std | 2.5100 | MATCH |
| 218 | 4.72 | result | data/tradeoff_curve_v2.json → .missed_viol | 4.7167 | MATCH |
| 218 | 0.98 | result | data/tradeoff_curve_v2.json → .missed_viol_std | 0.977221 | MATCH |
| 218 | 3.29 | result | data/tradeoff_curve_v2.json → .net_speedup | 3.2871 | MATCH |
| 218 | 0.30 | result | data/tradeoff_curve_v2.json → .net_speedup_std | 0.301977 | MATCH |
| 223 | 2026 | meta | table attribution year — no manifest records a table build date | — | NO SOURCE |
| 231 | 0.90 | config | data/tradeoff_curve_v2.json → operating_point | 0.9 | MATCH |
| 231 | 0.98 | config | data/tradeoff_curve_v2.json → coverage_levels (contains 0.98) | 0.98 | MATCH |
| 231 | 0.90 | config | data/tradeoff_curve_v2.json → operating_point | 0.9 | MATCH |
| 231 | 0.94 | config | data/frozen_poster_numbers_v2.json → crossings_first_below_1pct_missed.ridge | 0.94 | MATCH |
| 231 | 4.72 | result | data/tradeoff_curve_v2.json → .missed_viol | 4.7167 | MATCH |
| 231 | 2.48 | result | data/tradeoff_curve_v2.json → .missed_viol | 2.4756 | MATCH |
| 231 | 30.6 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 30.6251 | MATCH |
| 231 | 46.7 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 46.6840 | MATCH |
| 231 | 3.29 | result | data/tradeoff_curve_v2.json → .net_speedup | 3.2871 | MATCH |
| 231 | 2.15 | result | data/tradeoff_curve_v2.json → .net_speedup | 2.1483 | MATCH |
| 231 | 1 | config | data/tuning_search.json → inner_missed_ceiling | 1 | MATCH |
| 231 | 0.94 | result | data/frozen_poster_numbers_v2.json → crossings_first_below_1pct_missed.ridge | 0.94 | MATCH |
| 231 | 0.79 | result | data/tradeoff_curve_v2.json → .missed_viol | 0.793537 | MATCH |
| 231 | 64.3 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 64.3412 | MATCH |
| 231 | 1.56 | result | data/tradeoff_curve_v2.json → .net_speedup | 1.5568 | MATCH |
| 231 | 0.97 | result | data/frozen_poster_numbers_v2.json → crossings_first_below_1pct_missed.histgb | 0.97 | MATCH |
| 231 | 0.83 | result | data/tradeoff_curve_v2.json → .missed_viol | 0.832214 | MATCH |
| 231 | 63.7 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 63.6795 | MATCH |
| 231 | 1.58 | result | data/tradeoff_curve_v2.json → .net_speedup | 1.5791 | MATCH |
| 231 | 1.0 | result | data/tradeoff_curve_v2.json → missed_viol + missed_viol_std | 1.0025 | MATCH |
| 231 | 1.07 | result | data/tradeoff_curve_v2.json → missed_viol + missed_viol_std | 1.0769 | ROUNDING |
| 241 | 118 | name | data/network_triage.json → networks[case118].n_bus | 118 | MATCH |
| 248 | 0.90 | config | data/tradeoff_curve_v2.json → coverage_levels (contains 0.9) | 0.9 | MATCH |
| 248 | 49.1 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 49.0697 | MATCH |
| 248 | 2.7 | result | data/tradeoff_curve_v2.json → .escalation_std | 2.6608 | MATCH |
| 248 | 89.3 | result | data/tradeoff_curve_v2.json → .coverage_emp | 89.3390 | MATCH |
| 248 | 1.3 | result | data/tradeoff_curve_v2.json → .coverage_emp_std | 1.3272 | MATCH |
| 248 | 2.96 | result | data/tradeoff_curve_v2.json → .missed_viol | 2.9632 | MATCH |
| 248 | 0.44 | result | data/tradeoff_curve_v2.json → .missed_viol_std | 0.439389 | MATCH |
| 248 | 2.04 | result | data/tradeoff_curve_v2.json → .net_speedup | 2.0431 | MATCH |
| 248 | 0.11 | result | data/tradeoff_curve_v2.json → .net_speedup_std | 0.105697 | MATCH |
| 249 | 0.94 | config | data/tradeoff_curve_v2.json → coverage_levels (contains 0.94) | 0.94 | MATCH |
| 249 | 64.3 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 64.3412 | MATCH |
| 249 | 2.8 | result | data/tradeoff_curve_v2.json → .escalation_std | 2.7828 | MATCH |
| 249 | 94.0 | result | data/tradeoff_curve_v2.json → .coverage_emp | 93.9516 | MATCH |
| 249 | 0.7 | result | data/tradeoff_curve_v2.json → .coverage_emp_std | 0.740206 | MATCH |
| 249 | 0.79 | result | data/tradeoff_curve_v2.json → .missed_viol | 0.793537 | MATCH |
| 249 | 0.21 | result | data/tradeoff_curve_v2.json → .missed_viol_std | 0.208993 | MATCH |
| 249 | 1.56 | result | data/tradeoff_curve_v2.json → .net_speedup | 1.5568 | MATCH |
| 249 | 0.07 | result | data/tradeoff_curve_v2.json → .net_speedup_std | 0.0680528 | MATCH |
| 250 | 0.95 | config | data/tradeoff_curve_v2.json → coverage_levels (contains 0.95) | 0.95 | MATCH |
| 250 | 67.9 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 67.8533 | MATCH |
| 250 | 2.8 | result | data/tradeoff_curve_v2.json → .escalation_std | 2.8360 | MATCH |
| 250 | 95.0 | result | data/tradeoff_curve_v2.json → .coverage_emp | 95.0073 | MATCH |
| 250 | 0.6 | result | data/tradeoff_curve_v2.json → .coverage_emp_std | 0.626695 | MATCH |
| 250 | 0.45 | result | data/tradeoff_curve_v2.json → .missed_viol | 0.446575 | MATCH |
| 250 | 0.12 | result | data/tradeoff_curve_v2.json → .missed_viol_std | 0.122371 | MATCH |
| 250 | 1.48 | result | data/tradeoff_curve_v2.json → .net_speedup | 1.4761 | MATCH |
| 250 | 0.06 | result | data/tradeoff_curve_v2.json → .net_speedup_std | 0.0619187 | MATCH |
| 251 | 0.96 | config | data/tradeoff_curve_v2.json → coverage_levels (contains 0.96) | 0.96 | MATCH |
| 251 | 71.4 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 71.4346 | MATCH |
| 251 | 1.4 | result | data/tradeoff_curve_v2.json → .escalation_std | 1.4100 | MATCH |
| 251 | 95.9 | result | data/tradeoff_curve_v2.json → .coverage_emp | 95.9014 | MATCH |
| 251 | 0.4 | result | data/tradeoff_curve_v2.json → .coverage_emp_std | 0.388032 | MATCH |
| 251 | 0.14 | result | data/tradeoff_curve_v2.json → .missed_viol | 0.142382 | MATCH |
| 251 | 0.07 | result | data/tradeoff_curve_v2.json → .missed_viol_std | 0.0719923 | MATCH |
| 251 | 1.40 | result | data/tradeoff_curve_v2.json → .net_speedup | 1.4002 | MATCH |
| 251 | 0.03 | result | data/tradeoff_curve_v2.json → .net_speedup_std | 0.0278831 | MATCH |
| 252 | 0.97 | config | data/tradeoff_curve_v2.json → coverage_levels (contains 0.97) | 0.97 | MATCH |
| 252 | 73.9 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 73.9111 | MATCH |
| 252 | 1.0 | result | data/tradeoff_curve_v2.json → .escalation_std | 1.0227 | MATCH |
| 252 | 96.9 | result | data/tradeoff_curve_v2.json → .coverage_emp | 96.9399 | MATCH |
| 252 | 0.2 | result | data/tradeoff_curve_v2.json → .coverage_emp_std | 0.247256 | MATCH |
| 252 | 0.03 | result | data/tradeoff_curve_v2.json → .missed_viol | 0.026876 | MATCH |
| 252 | 0.03 | result | data/tradeoff_curve_v2.json → .missed_viol_std | 0.0274472 | MATCH |
| 252 | 1.35 | result | data/tradeoff_curve_v2.json → .net_speedup | 1.3530 | MATCH |
| 252 | 0.02 | result | data/tradeoff_curve_v2.json → .net_speedup_std | 0.0187584 | MATCH |
| 253 | 0.98 | config | data/tradeoff_curve_v2.json → coverage_levels (contains 0.98) | 0.98 | MATCH |
| 253 | 74.8 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 74.8045 | MATCH |
| 253 | 0.8 | result | data/tradeoff_curve_v2.json → .escalation_std | 0.821886 | MATCH |
| 253 | 98.0 | result | data/tradeoff_curve_v2.json → .coverage_emp | 98.0068 | MATCH |
| 253 | 0.2 | result | data/tradeoff_curve_v2.json → .coverage_emp_std | 0.178471 | MATCH |
| 253 | 0.00 | result | data/tradeoff_curve_v2.json → .missed_viol | 0 | MATCH |
| 253 | 0.00 | result | data/tradeoff_curve_v2.json → .missed_viol_std | 0 | MATCH |
| 253 | 1.34 | result | data/tradeoff_curve_v2.json → .net_speedup | 1.3368 | MATCH |
| 253 | 0.01 | result | data/tradeoff_curve_v2.json → .net_speedup_std | 0.0146835 | MATCH |
| 255 | 0.90 | config | data/tradeoff_curve_v2.json → coverage_levels (contains 0.9) | 0.9 | MATCH |
| 255 | 30.6 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 30.6251 | MATCH |
| 255 | 2.5 | result | data/tradeoff_curve_v2.json → .escalation_std | 2.5100 | MATCH |
| 255 | 89.8 | result | data/tradeoff_curve_v2.json → .coverage_emp | 89.8175 | MATCH |
| 255 | 1.0 | result | data/tradeoff_curve_v2.json → .coverage_emp_std | 0.984178 | MATCH |
| 255 | 4.72 | result | data/tradeoff_curve_v2.json → .missed_viol | 4.7167 | MATCH |
| 255 | 0.98 | result | data/tradeoff_curve_v2.json → .missed_viol_std | 0.977221 | MATCH |
| 255 | 3.29 | result | data/tradeoff_curve_v2.json → .net_speedup | 3.2871 | MATCH |
| 255 | 0.30 | result | data/tradeoff_curve_v2.json → .net_speedup_std | 0.301977 | MATCH |
| 256 | 0.94 | config | data/tradeoff_curve_v2.json → coverage_levels (contains 0.94) | 0.94 | MATCH |
| 256 | 46.7 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 46.6840 | MATCH |
| 256 | 2.8 | result | data/tradeoff_curve_v2.json → .escalation_std | 2.7507 | MATCH |
| 256 | 93.7 | result | data/tradeoff_curve_v2.json → .coverage_emp | 93.6842 | MATCH |
| 256 | 0.4 | result | data/tradeoff_curve_v2.json → .coverage_emp_std | 0.431235 | MATCH |
| 256 | 2.48 | result | data/tradeoff_curve_v2.json → .missed_viol | 2.4756 | MATCH |
| 256 | 0.38 | result | data/tradeoff_curve_v2.json → .missed_viol_std | 0.382562 | MATCH |
| 256 | 2.15 | result | data/tradeoff_curve_v2.json → .net_speedup | 2.1483 | MATCH |
| 256 | 0.13 | result | data/tradeoff_curve_v2.json → .net_speedup_std | 0.12719 | MATCH |
| 257 | 0.95 | config | data/tradeoff_curve_v2.json → coverage_levels (contains 0.95) | 0.95 | MATCH |
| 257 | 51.2 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 51.1830 | MATCH |
| 257 | 3.4 | result | data/tradeoff_curve_v2.json → .escalation_std | 3.4227 | MATCH |
| 257 | 94.7 | result | data/tradeoff_curve_v2.json → .coverage_emp | 94.6567 | MATCH |
| 257 | 0.4 | result | data/tradeoff_curve_v2.json → .coverage_emp_std | 0.440042 | MATCH |
| 257 | 1.94 | result | data/tradeoff_curve_v2.json → .missed_viol | 1.9440 | MATCH |
| 257 | 0.21 | result | data/tradeoff_curve_v2.json → .missed_viol_std | 0.21157 | MATCH |
| 257 | 1.96 | result | data/tradeoff_curve_v2.json → .net_speedup | 1.9612 | MATCH |
| 257 | 0.13 | result | data/tradeoff_curve_v2.json → .net_speedup_std | 0.127153 | MATCH |
| 258 | 0.96 | config | data/tradeoff_curve_v2.json → coverage_levels (contains 0.96) | 0.96 | MATCH |
| 258 | 57.0 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 56.9553 | MATCH |
| 258 | 4.3 | result | data/tradeoff_curve_v2.json → .escalation_std | 4.2519 | MATCH |
| 258 | 95.7 | result | data/tradeoff_curve_v2.json → .coverage_emp | 95.7050 | MATCH |
| 258 | 0.4 | result | data/tradeoff_curve_v2.json → .coverage_emp_std | 0.42172 | MATCH |
| 258 | 1.36 | result | data/tradeoff_curve_v2.json → .missed_viol | 1.3568 | MATCH |
| 258 | 0.20 | result | data/tradeoff_curve_v2.json → .missed_viol_std | 0.197668 | MATCH |
| 258 | 1.76 | result | data/tradeoff_curve_v2.json → .net_speedup | 1.7641 | MATCH |
| 258 | 0.12 | result | data/tradeoff_curve_v2.json → .net_speedup_std | 0.123534 | MATCH |
| 259 | 0.97 | config | data/tradeoff_curve_v2.json → coverage_levels (contains 0.97) | 0.97 | MATCH |
| 259 | 63.7 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 63.6795 | MATCH |
| 259 | 5.1 | result | data/tradeoff_curve_v2.json → .escalation_std | 5.1192 | MATCH |
| 259 | 97.0 | result | data/tradeoff_curve_v2.json → .coverage_emp | 96.9564 | MATCH |
| 259 | 0.2 | result | data/tradeoff_curve_v2.json → .coverage_emp_std | 0.2463 | MATCH |
| 259 | 0.83 | result | data/tradeoff_curve_v2.json → .missed_viol | 0.832214 | MATCH |
| 259 | 0.24 | result | data/tradeoff_curve_v2.json → .missed_viol_std | 0.244681 | MATCH |
| 259 | 1.58 | result | data/tradeoff_curve_v2.json → .net_speedup | 1.5791 | MATCH |
| 259 | 0.12 | result | data/tradeoff_curve_v2.json → .net_speedup_std | 0.116935 | MATCH |
| 260 | 0.98 | config | data/tradeoff_curve_v2.json → coverage_levels (contains 0.98) | 0.98 | MATCH |
| 260 | 72.0 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 71.9953 | MATCH |
| 260 | 3.7 | result | data/tradeoff_curve_v2.json → .escalation_std | 3.6706 | MATCH |
| 260 | 98.0 | result | data/tradeoff_curve_v2.json → .coverage_emp | 97.9717 | MATCH |
| 260 | 0.2 | result | data/tradeoff_curve_v2.json → .coverage_emp_std | 0.165707 | MATCH |
| 260 | 0.30 | result | data/tradeoff_curve_v2.json → .missed_viol | 0.304537 | MATCH |
| 260 | 0.13 | result | data/tradeoff_curve_v2.json → .missed_viol_std | 0.132897 | MATCH |
| 260 | 1.39 | result | data/tradeoff_curve_v2.json → .net_speedup | 1.3919 | MATCH |
| 260 | 0.07 | result | data/tradeoff_curve_v2.json → .net_speedup_std | 0.0673298 | MATCH |
| 265 | 2026 | meta | table attribution year — no manifest records a table build date | — | NO SOURCE |
| 281 | 1 | config | data/tuning_search.json → inner_missed_ceiling | 1 | MATCH |
| 281 | 0.94 | result | data/frozen_poster_numbers_v2.json → crossings_first_below_1pct_missed.ridge | 0.94 | MATCH |
| 281 | 0.97 | result | data/frozen_poster_numbers_v2.json → crossings_first_below_1pct_missed.histgb | 0.97 | MATCH |
| 281 | 1 | claim>1 | data/tradeoff_curve_v2.json → missed_viol + missed_viol_std | 1.0769 | MATCH |
| 284 | 3.11.1 | meta | data/tradeoff_hero_col_v2.manifest.json → plotting_library | matplotlib 3.11.1 | MATCH |
| 284 | 2026 | meta | data/tradeoff_hero_col_v2.manifest.json → generated_utc | 2026 | MATCH |
| 292 | 118 | name | data/network_triage.json → networks[case118].n_bus | 118 | MATCH |
| 292 | 3.29 | result | data/tradeoff_curve_v2.json → .net_speedup | 3.2871 | MATCH |
| 292 | 2.04 | result | data/tradeoff_curve_v2.json → .net_speedup | 2.0431 | MATCH |
| 292 | 0.96 | config | data/tradeoff_curve_v2.json → coverage_levels (contains 0.96) | 0.96 | MATCH |
| 292 | 0.14 | result | data/tradeoff_curve_v2.json → .missed_viol | 0.142382 | MATCH |
| 292 | 1.36 | result | data/tradeoff_curve_v2.json → .missed_viol | 1.3568 | MATCH |
| 292 | 118 | name | data/network_triage.json → networks[case118].n_bus | 118 | MATCH |
| 292 | 0.90 | config | data/tradeoff_curve_v2.json → operating_point | 0.9 | MATCH |
| 292 | 74 | result | data/missed_depth.json → families.ridge.pooled['0.90'].share_below_qhat | 73.6769 | MATCH |
| 292 | 55 | result | data/missed_depth.json → families.histgb.pooled['0.90'].share_below_qhat | 54.9037 | MATCH |
| 292 | 26.7 | result | data/missed_depth.json → 1 − families.ridge.pooled['0.90'].share_below_strip | 26.7409 | MATCH |
| 292 | 21.4 | result | data/missed_depth.json → 1 − families.histgb.pooled['0.90'].share_below_strip | 21.4098 | MATCH |
| 292 | 0.005 | config | data/missed_depth.json → boundary_strip_width | 0.005 | MATCH |
| 292 | 0.0915 | result | data/missed_depth.json → families.*.deepest_missed.depth | 0.0914569 | MATCH |
| 292 | 0.8485 | result | data/missed_depth.json → families.*.deepest_missed.y_true | 0.848543 | MATCH |
| 303 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 303 | 90 | config | data/tradeoff_curve_v2.json → operating_point | 90 | MATCH |
| 303 | 74 | result | data/missed_depth.json → families.ridge.pooled['0.90'].share_below_qhat | 73.6769 | MATCH |
| 303 | 55 | result | data/missed_depth.json → families.histgb.pooled['0.90'].share_below_qhat | 54.9037 | MATCH |
| 303 | 0.0915 | result | data/missed_depth.json → families.*.deepest_missed.depth | 0.0914569 | MATCH |
| 303 | 0.8485 | result | data/missed_depth.json → families.*.deepest_missed.y_true | 0.848543 | MATCH |
| 306 | 3.11.1 | meta | data/miss_depth_v3.manifest.json → plotting_library | matplotlib 3.11.1 | MATCH |
| 306 | 2026 | meta | data/miss_depth_v3.manifest.json → generated_utc | 2026 | MATCH |
| 314 | 0.005 | config | data/missed_depth.json → boundary_strip_width | 0.005 | MATCH |
| 314 | 56.86 | result | data/frozen_poster_numbers_v2.json → dataset_facts.boundary_0p94_to_0p945_pct | 56.8600 | MATCH |
| 314 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 314 | 0.945 | config | data/unconditioned_base.json → strip_hi | 0.945 | MATCH |
| 314 | 17.48 | result | data/frozen_poster_numbers_v2.json → dataset_facts.violation_rate_pct | 17.4800 | MATCH |
| 314 | 0.001 | config | data/unconditioned_base.json → committed_gated.largest_bin_hi − _lo | 0.001 | MATCH |
| 314 | 14 | result (hedged, tol ±0.5) | data/unconditioned_base.json → committed_gated.largest_bin_share_pct | 14.0628 | MATCH |
| 314 | 76 | result | data/frozen_poster_numbers_v2.json → dataset_facts.critical_bus_top5[0].bus (+1, IEEE name) | 76 | MATCH |
| 314 | 27.1 | result | data/frozen_poster_numbers_v2.json → dataset_facts.critical_bus_top5[0].share_pct | 27.1000 | MATCH |
| 314 | 53 | result | data/frozen_poster_numbers_v2.json → dataset_facts.critical_bus_top5[1].bus (+1, IEEE name) | 53 | MATCH |
| 314 | 16.81 | result | data/frozen_poster_numbers_v2.json → dataset_facts.critical_bus_top5[1].share_pct | 16.8100 | MATCH |
| 314 | 107 | result | data/frozen_poster_numbers_v2.json → dataset_facts.critical_bus_top5[2].bus (+1, IEEE name) | 107 | MATCH |
| 314 | 9.31 | result | data/frozen_poster_numbers_v2.json → dataset_facts.critical_bus_top5[2].share_pct | 9.3100 | MATCH |
| 323 | 278,955 | result | data/frozen_poster_numbers_v2.json → dataset_facts.converged_n1_rows | 278,955 | MATCH |
| 323 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 323 | 0.945 | config | data/unconditioned_base.json → strip_hi | 0.945 | MATCH |
| 323 | 56.9 | result | data/frozen_poster_numbers_v2.json → dataset_facts.boundary_0p94_to_0p945_pct | 56.8600 | MATCH |
| 323 | 0.001 | config | data/unconditioned_base.json → committed_gated.largest_bin_hi − _lo | 0.001 | MATCH |
| 323 | 14.1 | result | data/unconditioned_base.json → committed_gated.largest_bin_share_pct | 14.0628 | MATCH |
| 323 | 0.87 | config | feasibility/boundary_mass_hist.py:21 VIEW_LO | 0.87 | MATCH |
| 323 | 0.5 | nokey | NO KEY — dataset.parquet converged N-1 rows, share min_vm < 0.87 | 0.541306 | NO SOURCE |
| 327 | 3.11.1 | meta | data/boundary_mass_hist_v2.manifest.json → plotting_library | matplotlib 3.11.1 | MATCH |
| 327 | 2026 | meta | data/boundary_mass_hist_v2.manifest.json → generated_utc | 2026 | MATCH |
| 339 | 76 | result | data/frozen_poster_numbers_v2.json → dataset_facts.critical_bus_top5[0].bus (+1, IEEE name) | 76 | MATCH |
| 339 | 53 | result | data/frozen_poster_numbers_v2.json → dataset_facts.critical_bus_top5[1].bus (+1, IEEE name) | 53 | MATCH |
| 339 | 107 | result | data/frozen_poster_numbers_v2.json → dataset_facts.critical_bus_top5[2].bus (+1, IEEE name) | 107 | MATCH |
| 339 | 27.1 | result | data/frozen_poster_numbers_v2.json → dataset_facts.critical_bus_top5[0].share_pct | 27.1000 | MATCH |
| 339 | 16.81 | result | data/frozen_poster_numbers_v2.json → dataset_facts.critical_bus_top5[1].share_pct | 16.8100 | MATCH |
| 339 | 9.31 | result | data/frozen_poster_numbers_v2.json → dataset_facts.critical_bus_top5[2].share_pct | 9.3100 | MATCH |
| 342 | 3.11.1 | meta | data/critical_bus_map.manifest.json → plotting_library | matplotlib 3.11.1 | MATCH |
| 342 | 2026 | meta | data/critical_bus_map.manifest.json → generated_utc | 2026 | MATCH |
| 347 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 347 | 0.0023 | result | data/tradeoff_curve_v2.json → .q_hat | 0.0022907 | MATCH |
| 347 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 347 | 30.6 | result | data/tradeoff_curve_v2.json → records[model,target].escalation | 30.6251 | MATCH |
| 347 | 82.64 | result | data/frozen_poster_numbers_v2.json → ceilings.perfect_model_floor_saturation | 82.6352 | MATCH |
| 347 | 74.89 | result | data/frozen_poster_numbers_v2.json → ceilings.escalation_at_max_band_width_…ridge | 74.8876 | MATCH |
| 347 | 82.79 | result | data/frozen_poster_numbers_v2.json → ceilings.escalation_at_max_band_width_…histgb | 82.7948 | MATCH |
| 349 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 349 | 99.5 | result | data/screener_metrics.json → records[model=persistence].escalation | 99.5336 | MATCH |
| 349 | 1 | claim~1 | data/tradeoff_curve_v2.json → missed_viol + missed_viol_std | 1.0769 | MATCH |
| 349 | 1 | claim~1 | data/tradeoff_curve_v2.json → missed_viol + missed_viol_std | 1.0769 | MATCH |
| 349 | 0.94 | result | data/frozen_poster_numbers_v2.json → crossings_first_below_1pct_missed.ridge | 0.94 | MATCH |
| 349 | 0.97 | result | data/frozen_poster_numbers_v2.json → crossings_first_below_1pct_missed.histgb | 0.97 | MATCH |
| 349 | 1.6 | result (hedged, tol ±0.05) | data/tradeoff_curve_v2.json → .net_speedup | 1.5791 | MATCH |
| 349 | 2 | result (hedged, tol ±0.05) | data/tradeoff_curve_v2.json → .net_speedup | 2.0431 | MATCH |
| 349 | 3.3 | result (hedged, tol ±0.05) | data/tradeoff_curve_v2.json → .net_speedup | 3.2871 | MATCH |
| 349 | 0.90 | config | data/tradeoff_curve_v2.json → operating_point | 0.9 | MATCH |
| 353 | 54 | result | data/netstudy2/summary.json → cross_network.n | 54 | MATCH |
| 353 | 3 | result | data/netstudy2/summary.json → distinct cross_comparisons[].network | 3 | MATCH |
| 353 | 2 | result | data/netstudy2/summary.json → distinct cross_comparisons[].family | 2 | MATCH |
| 353 | 9 | result | data/netstudy2/summary.json → distinct cross_comparisons[].coverage_target | 9 | MATCH |
| 353 | 0.4726 | result | data/netstudy2/summary.json → cross_network.A_mean_rel_error | 0.472555 | MATCH |
| 353 | 0.4933 | result | data/netstudy2/summary.json → cross_network.B_mean_rel_error | 0.493252 | MATCH |
| 353 | 0.1056 | result | data/netstudy2/summary.json → cross_network.B_mean_abs_error | 0.105612 | MATCH |
| 353 | 0.1163 | result | data/netstudy2/summary.json → cross_network.A_mean_abs_error | 0.116306 | MATCH |
| 353 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 353 | 0.0 | config | data/netstudy/case57/nofeasible_diagnostic.json → scaling[multiplier=0.0] | 0 | MATCH |
| 353 | 0.9012 | result | data/netstudy/case57/nofeasible_diagnostic.json → scaling[multiplier=0.0].min_vm_pu | 0.90121 | MATCH |
| 353 | 24 | result | data/netstudy/case57/nofeasible_diagnostic.json → scaling[multiplier=0.0].n_bus_below_094 | 24 | MATCH |
| 353 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 353 | 392 | result | data/netstudy2/case89pegase_nofeasible_diagnostic.json → worst_trafos_at_nominal[0].loading_pct (the WORST trafo) | 392.214 | MATCH |
| 353 | 16 | result | data/netstudy2/case89pegase_nofeasible_diagnostic.json → n_trafo_over_100_at_nominal | 16 | MATCH |
| 353 | 50 | result | data/netstudy2/case89pegase_nofeasible_diagnostic.json → n_trafo | 50 | MATCH |
| 353 | 100 | config | data/network_triage.json → criteria.thermal_max_pct | 100 | MATCH |
| 353 | 0.0 | config | data/netstudy/case57/nofeasible_diagnostic.json → scaling[multiplier=0.0] | 0 | MATCH |
| 353 | 199.37 | result | data/netstudy2/case89pegase_nofeasible_diagnostic.json → scaling[multiplier=0.0].max_loading_pct | 199.369 | MATCH |
| 363 | 186 | result | data/break_even.json → generation.branches | 186 | MATCH |
| 365 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 365 | 30 | name | data/network_triage.json → networks[case30].n_bus | 30 | MATCH |
| 365 | 7.09 | result | data/case30_thermal/case30_thermal_frozen.json → boundary_mass_pct | 7.0862 | MATCH |
| 365 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 365 | 15.40 | result | data/case30_thermal/case30_thermal_frozen.json → violation_rate_pct | 15.3967 | MATCH |
| 365 | 56.86 | result | data/frozen_poster_numbers_v2.json → dataset_facts.boundary_0p94_to_0p945_pct | 56.8600 | MATCH |
| 365 | 17.48 | result | data/frozen_poster_numbers_v2.json → dataset_facts.violation_rate_pct | 17.4800 | MATCH |
| 365 | 30 | name | data/network_triage.json → networks[case30].n_bus | 30 | MATCH |
| 365 | 111.83 | result | data/network_triage.json → networks[case30].base_max_loading_pct | 111.831 | MATCH |
| 365 | 0.97 | result | data/case30_thermal/case30_thermal_frozen.json → first target with all 5 histgb splits < 1% | 0.97 | MATCH |
| 365 | 5.84 | result | data/case30_thermal/case30_thermal_frozen.json → records[histgb, target].escalation | 5.8358 | MATCH |
| 365 | 1.25 | result | data/case30_thermal/case30_thermal_frozen.json → records[histgb, target].escalation (pop. std) | 1.2505 | MATCH |
| 365 | 0.76 | result | data/case30_thermal/case30_thermal_frozen.json → records[histgb, target].missed_viol | 0.759014 | MATCH |
| 365 | 0.20 | result | data/case30_thermal/case30_thermal_frozen.json → records[histgb, target].missed_viol (pop. std) | 0.200824 | MATCH |
| 365 | 1 | config | data/tuning_search.json → inner_missed_ceiling | 1 | MATCH |
| 365 | 0.97 | result | data/case30_thermal/case30_thermal_frozen.json → first target with all 5 histgb splits < 1% | 0.97 | MATCH |
| 365 | 0.96 | config | data/tradeoff_curve_v2.json → coverage_levels (contains 0.96) | 0.96 | MATCH |
| 365 | 0.91 | result | data/case30_thermal/case30_thermal_frozen.json → records[histgb, target].missed_viol | 0.909353 | MATCH |
| 365 | 0.22 | result | data/case30_thermal/case30_thermal_frozen.json → records[histgb, target].missed_viol (pop. std) | 0.219629 | MATCH |
| 365 | 0.94 | config | data/tradeoff_curve_v2.json → limit | 0.94 | MATCH |
| 365 | 86 | result | data/bases_clearing_0p95.json → canonical_v2.ge_0p95 | 86 | MATCH |
| 365 | 1,500 | result | data/frozen_poster_numbers_v2.json → dataset_facts.scenarios | 1,500 | MATCH |
| 365 | 0.95 | config | data/escalation_at_095.json → limits [0.94, 0.95] (contains 0.95) | 0.95 | MATCH |
| 365 | 0.95 | config | data/escalation_at_095.json → limits [0.94, 0.95] (contains 0.95) | 0.95 | MATCH |
| 365 | 1.38 | result | data/escalation_at_095.json → summary.ridge.escalation_at_0.95.mean | 1.3848 | MATCH |
| 365 | 0.33 | result | data/escalation_at_095.json → summary.ridge.escalation_at_0.95.std | 0.326317 | MATCH |
| 367 | 374 | result | data/sampling_audit.json → prevalence.n_base_with_generator_outage | 374 | MATCH |
| 367 | 1,500 | result | data/frozen_poster_numbers_v2.json → dataset_facts.scenarios | 1,500 | MATCH |
| 367 | 24.93 | result | data/sampling_audit.json → prevalence.share_of_base_scenarios | 24.9333 | MATCH |
| 367 | 69,532 | result | data/sampling_audit.json → prevalence.n_n1_rows_with_generator_outage | 69,532 | MATCH |
| 367 | 30 | name | data/network_triage.json → networks[case30].n_bus | 30 | MATCH |
| 367 | 21.5 | result | data/case30_thermal/h3_build_stats.json → n1_loading.share_above_100 | 21.4846 | MATCH |
| 367 | 100 | config | data/network_triage.json → criteria.thermal_max_pct | 100 | MATCH |
| 367 | 145.8 | result | data/case30_thermal/h3_build_stats.json → n1_loading.max | 145.797 | MATCH |
| 367 | 0.0915 | result | data/missed_depth.json → families.*.deepest_missed.depth | 0.0914569 | MATCH |
| 373 | 0.00371 | result | data/physics_ablation.json → records[config, family, m2_searched].mae (+F1+F3, ridge, mean) | 0.00370725 | MATCH |
| 373 | 0.00010 | result | data/physics_ablation.json → records[config, family, m2_searched].mae (+F1+F3, ridge, pop. std) | 9.60545e-05 | MATCH |
| 373 | 0.00153 | result | data/physics_ablation.json → records[config, family, m2_searched].mae (+F1+F2+F3+F4, histgb, mean) | 0.00152643 | MATCH |
| 373 | 0.00011 | result | data/physics_ablation.json → records[config, family, m2_searched].mae (+F1+F2+F3+F4, histgb, pop. std) | 0.000110871 | MATCH |
| 375 | 10.82 | result | data/physics_ablation.json → records[config, family, m2_searched].mae (+F1+F2 / baseline − 1, ridge) | 10.8205 | MATCH |
| 375 | 0.003754 | result | data/physics_ablation.json → records[config, family, m2_searched].mae (baseline, ridge, mean) | 0.00375433 | MATCH |
| 375 | 0.000133 | result | data/physics_ablation.json → records[config, family, m2_searched].mae (baseline, ridge, pop. std) | 0.000132771 | MATCH |
| 375 | 0.004161 | result | data/physics_ablation.json → records[config, family, m2_searched].mae (+F1+F2, ridge, mean) | 0.00416057 | MATCH |
| 375 | 0.000247 | result | data/physics_ablation.json → records[config, family, m2_searched].mae (+F1+F2, ridge, pop. std) | 0.000246975 | MATCH |
| 377 | 0.0015638 | result | data/f1_leakage_audit.json → check_4_permutation.baseline.mae | 0.00156376 | MATCH |
| 377 | 0.0015539 | result | data/f1_leakage_audit.json → check_4_permutation.F1_real.mae | 0.0015539 | MATCH |
| 377 | 0.0015300 | result | data/f1_leakage_audit.json → check_4_permutation.F1_shuffled.mae | 0.00153001 | MATCH |
| 377 | 2.39× 10^{-5} | result | data/f1_leakage_audit.json → F1_real.mae − F1_shuffled.mae | 2.38849e-05 | MATCH |
| 377 | 7.58× 10^{-5} | result | data/physics_ablation.json → records[config, family, m2_searched].mae (baseline, histgb, pop. std) | 7.57534e-05 | MATCH |
| 377 | 25 | result | data/f1_leakage_audit.json → check_2_base_solve_integrity.n_scenarios_checked | 25 | MATCH |
| 388 | 118 | name | data/network_triage.json → networks[case118].n_bus | 118 | MATCH |
| 388 | 30 | name | data/network_triage.json → networks[case30].n_bus | 30 | MATCH |
| 388 | 90 | config | data/tradeoff_curve_v2.json → operating_point | 90 | MATCH |
| 388 | 1 | config | data/tuning_search.json → inner_missed_ceiling | 1 | MATCH |
| 388 | 1.6 | result (hedged, tol ±0.05) | data/tradeoff_curve_v2.json → .net_speedup | 1.5568 | MATCH |
