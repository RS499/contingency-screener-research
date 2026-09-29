# STS 2027 research-report review — `report/paper_current_STS.tex`

**Date:** 2026-09-23. **Deadline:** 2026-11-05 (about 6 weeks; the internal "done" date is late October).
**Reviewed file:** `report/paper_current_STS.tex`, working tree (460 lines; `git status` shows it
modified relative to HEAD `7fc39e4`). All line numbers below refer to this working-tree version and
must be re-anchored after any edit.

**What this review is.** AI-generated feedback (Claude Code, with three reviewer subagents).

**Evidence convention.** `:NNN` means `report/paper_current_STS.tex:NNN`. A data claim is cited as
`file` → `key`. **VERIFIED** means I recomputed it myself from the file, using the scratch scripts
listed in §9. **Reported** means it comes from a reviewer subagent and I did not re-verify it.
**unverified** means nobody could point to evidence.

---

## 0. Top 5

The biggest threats and the biggest upside are the same thing. The central claim, as written,
would not survive a first-round power-systems or statistics PhD. The data needed to rebuild it into
the paper's strongest result are already on disk and unreported.

### 1. FATAL: the "boundary mass" is mostly produced by the sampler, not by the network

A base case is accepted only if its N-0 minimum voltage is ≥ 0.94 (`feasibility/generate_dataset.py:256`,
`GATE_N0 and ... n0_min_vm < VMIN_LIMIT`). N-1 is then screened against the same 0.94. Most branch
outages barely move the minimum voltage, so each base's N-0 minimum is copied across its 186 rows.
All of the following are VERIFIED:

- **Rows barely move from N-0.** Median |min_vm − n0_min_vm| = 3.3×10⁻⁶ pu, and 77.6% of N-1 rows are
  within 0.001 pu of their N-0 minimum (`scratch/verify_reviewer_claims.py`, section e/f).
- **The strip is inherited from the base case.**
  - 96.3% of rows in [0.94, 0.945) come from bases whose N-0 minimum was already < 0.945.
  - 93.4% have the same weakest bus as their N-0 base.
  - 31.6% sit at IEEE bus 76, whose published setpoint is 0.943 pu (pandapower `case118`, gen at bus
    index 75, `vm_pu = 0.943`).
- **Within-network quintiles** (`data/quintile_boundary_mass.json` → `quintiles_low_to_high`).
  Boundary mass is 78.4 / 81.3 / 82.4 / 37.3 / **4.98%** across N-0-margin quintiles. The top
  quintile is at case30's 7.09% and case39's 4.43%.
- **Removing the N-0 filter** (`data/unconditioned_base.json` → `unconditioned.boundary_0p94_to_0p945_pct`)
  roughly halves boundary mass, from 56.86% to **28.83%**.
- **Limit sweep** (`data/sweep_results_long.parquet`, 5 seeds, 0.90 target, histgb):
  - escalation is 0.3–1.5% for every L from 0.900 to 0.936;
  - 30.6% at L = 0.940 (the filter value);
  - 1.6% at 0.950.

  The "floor" is a spike located exactly at the chosen limit.

The paper says the opposite. `:121` calls the clustering "an inherent characteristic of the network
and the sampling process". The title (`:63`) promises "Limits Set by Boundary Mass". `:365` and
`:388` present the case118 vs case30 contrast as a network property. That contrast is also
confounded, because case30 used a different sampler: load window 0.87–0.99 plus a thermal N-0 filter
(`data/case30_thermal/h3_build_stats.json` → `range`, `median_base_loading_pct`). The words
"quintile" and "unconditioned" do not appear in the paper.

**Fix (existing data, about 10–15 h, fits before Nov 5).** Restate the mechanism as: escalation is
set by the share of operating points whose margin to the limit is smaller than q̂. Then show it three
ways:

- within case118, by N-0 margin (the quintile table, plus the 2C drift split in item 3, where histgb
  escalation is 2.8% on benign bases vs 59.1% on marginal ones);
- within case118, by limit (the sweep);
- across five networks (item 3).

The confound then becomes the paper's natural experiment. Also state that a separate, lower
post-contingency emergency limit is common in practice. The sweep already shows what happens then
(histgb at L = 0.92: 0.7% escalation). Whether 0.92 is the right emergency value is unverified; cite
a source before using it.

### 2. FATAL (for a statistics judge): the floor restates the gate definition, the safety metric has no guarantee, and the headline operating point was picked on test data

- **The Theory is definitional.** Eq. `:170` is the escalate rule (`:139-141`) rewritten. Eq. `:178`
  is two lines of algebra from certify plus violation. The repo "confirms" it to 5.6×10⁻¹⁷
  (`data/barrier_height.json` → `identity_checks.max_identity_gap`), which checks algebra rather
  than testing a hypothesis. `:101` ("explain why there must be a certain floor") and `:388` claim
  it as the contribution.
- **"Must" is refuted by the repo's own results.** Mondrian (per-element) calibration cuts escalation
  sharply at a similar missed rate (VERIFIED, `data/mondrian_element_summary.json` → `aggregate`):
  - histgb at 0.94: 32.1±2.3% escalation, 2.67±0.38% missed; global calibration gives 46.7±2.8% and
    2.48±0.38%;
  - ridge at 0.94: 49.6% vs 64.3%.

  The floor therefore belongs to one global q̂, not to the task. `:132` says only that adaptive
  alternatives "exist".
- **Missed rate carries no guarantee.** It is P(certify | violation). The conformal guarantee covers
  only marginal coverage (`feasibility/gate_eval.py`). On violations the band covers only about 60%:
  P(overshoot > q̂ | violation) is 0.388 for ridge and 0.411 for histgb at 0.90 (VERIFIED,
  `data/barrier_height.json` → `summary_at_090.case118.*.p_overshoot_gt_qhat_given_viol_at_090_mean`).
- **The headline operating point was chosen on the test split.** "First target below 1% mean missed"
  (`:81`, `:231`, `:349`) is selected from the test sweep (`scripts/build_v2_frozen.py:49-54`,
  `first_below_1pct`). The pipeline already has a held-out choice (`data/tuning_search.json` →
  `records[].inner_cov_at`). At those inner-chosen targets the test results are (VERIFIED):
  - histgb misses **1.15±0.27%**, above 1% in 4 of 5 seeds (per seed 1.61, 0.80, 1.03, 1.05, 1.23);
  - ridge misses 0.77±0.78%, with seed 3 at 2.24%;
  - even at the test-picked histgb@0.97, 2 of 5 seeds exceed 1% (1.16, 1.03).

**Fix.**
- Text:
  - say plainly that missed rate is uncontrolled;
  - report the inner-selected operating point as the honest headline;
  - present the Theory as an accounting identity whose empirical content is ρ·q̂ (item 3).
- Existing data: the Mondrian rows.
- A new run (no new AC solves, about 8–12 h): calibrate the certify threshold on violations only
  (class-conditional conformal), or use conformal risk control, so the missed rate itself carries a
  finite-sample bound. The paper already cites that family (`bates2021`, `:363`).

### 3. MAJOR (largest cheap upside): decisive results already in `data/` are missing from the paper

| Existing result | What it shows | Source (VERIFIED) |
|---|---|---|
| Classical conformalized screen | At 0.90 it avoids only 8.0% of solves (1.07% missed; 1.09×). Conformal ridge dominates it at 9/9 points. This beats a non-trivial physics baseline, which answers "only trivial baselines". `:109` wrongly says classical screens give no numeric minimum voltage; the repo's screen outputs `pred_min_vm`. | `data/comparison_curve_v2.json` → `curves.classical_conformal`, `dominance`; `data/classical_predictions.parquet` |
| Escalation vs ρ·q̂ on 5 networks (132 points) | Pearson r = 0.81; log-log r = 0.92. For histgb, escalation/(ρq̂) has a median of 0.85–1.14 on every network. Ridge breaks down on case24 (median 0.34). | `data/netstudy2/cross_2a_points.json` → `points` (`scratch/crossnet_points.py`) |
| Per-cell cross-network errors | Predictor A's 0.47 mean relative error is driven by one cell: case24 ridge, predicted 0.451 vs measured 0.217 at 0.90. illinois200 errors are 0.001–0.010 absolute. | `data/netstudy2/summary.json` → `table_at_090`, `cross_comparisons` |
| Drift tests 2C / 2D / 2E, each with a same-stratum control | See the bullets below this table. | `data/drift_*_long.parquet` (`scratch/drift_summary.py`) |
| case30 speedup | Never reported (`:81`, `:365` give only escalation). See the bullets below. | `data/case30_thermal/case30_thermal_frozen.json` → `records` |
| Miss depth at the recommended points | See the bullets below. | `data/missed_depth.json` → `families.*.pooled`; `data/qlimit_class.json` → `per_operating_point` |
| Break-even | ridge@0.94 needs about 787k contingencies (4,231 base-case sweeps) to repay the 2,564 s of dataset generation. `:99` claims "true end-to-end cost". | `data/break_even.json` → `break_even_at_operating_points.ridge.gen_only` |

Details for the rows that need more than one line:

- **Drift test 2C** (median split on N-0 margin). Ridge calibrated on benign bases and tested on
  marginal ones covers **79.5±1.8%** at a 0.90 target, against 88.4±2.7% for the marginal→marginal
  control. Histgb is robust (89.6 vs 90.3). This is a real distribution-shift result, and the
  project's stated research question 1.
- **Drift test 2D** (element type), histgb, line-calibrated: 87.6±1.0 on transformers vs 89.8±1.0 for
  the control. The gap exceeds the larger std, but only by about 2×.
- **Drift test 2E** (loading tilt): null.
- **case30 speedup.**
  - histgb@0.97: **17.9±3.7×**; histgb@0.90: 38.6±6.2×.
  - Under case118's own "first mean < 1%" rule, case30 histgb lands at 0.96: 4.86% escalation, 21.5×.
- **Miss depth at the recommended points.** The paper reports it only at 0.90 (`:292`).
  - ridge@0.94: maximum miss depth 0.032 pu.
  - histgb@0.97: still **0.0915 pu**. The 0.8485 pu case is still certified in seed 2.
  - `:349` treats the two operating points as equivalent.

**Fix.** Add these results (existing data, about 15–20 h in total). They pay for their page cost only
if the ablation and digressions are cut (§7).

### 4. MAJOR: operator relevance and physics correctness

- **Flags skip the solver, but an operator needs the AC solution exactly for flagged cases.** The
  certify-only speedup is **1.24×** for histgb@0.97 and **1.12×** for ridge@0.94, against the
  headline 1.58× / 1.56×. Ridge's flag precision is 0.56, so 11.0% of all contingencies are false
  alarms. That partly explains why ridge "misses less" (`:292`). VERIFIED: `data/flag_confusion_long.parquet`
  → `certified_frac`, `flag_precision`, `false_flag_rate_of_all`.
- **The stakes are never quantified.** A full 118-bus N-1 sweep is 186 × 9.14 ms ≈ 1.7 s. Ten cores
  give 5.4× (`data/parallel_speedup.json` → `best_parallel.speedup`), more than the gate does.
  - The solve is timed from a cold `init="dc"` over about 2–3 bases (`feasibility/measure_solve.py:20-40`;
    430 consecutive solves).
  - `:109` attributes the 9 ms to "complex and non-linear" math. Reported by the power-systems
    reviewer: one amortized sparse LU costs about 0.13 ms, so most of the 9.14 ms is overhead.
  - The paper never says why a 1.6× saving on a 2-second job matters. The honest frame is large
    systems, many-scenario studies, or N-1-1.
- **The worst-miss physics is misexplained, and the label may be a solver artifact.** `:367` says the
  weak-bus generator "reaches the limit of reactive power and can no longer control the voltage".
  The data show gen 21 (IEEE bus 54) pinned at its **absorbing** limit (Q = Qmin = −194.7 Mvar) while
  its voltage is 0.106 pu *below* setpoint. A voltage-regulating generator below its setpoint injects
  reactive power; it does not absorb it. With Q limits off, the same case solves to 0.939. VERIFIED:
  `data/miss_mechanism.json` → `part1_mechanism.saturated_gens_near_weak_bus_post_outage[1]`,
  `key_bus_voltages_n0_vs_n1`; `data/qlims_off_check.json` → `qlims_check`. The likely cause is a
  PV→PQ switch that never switches back. How many of the 17.48% violation labels share this pattern
  is **unverified**.
- **Other physics wording.**
  - `:367`: "whether or not the grid crashed … dynamic stability". Loss of power-flow solvability is
    *static* voltage collapse.
  - `:353`: the case57/case89pegase "load multiplier 0.0" diagnostics scale load but not generation.
    Reported: `scripts/netstudy_case57_diag.py:21-23`. Pegase loading *rises* to 199% at zero load
    (`data/netstudy2/case89pegase_nofeasible_diagnostic.json` → `scaling`), which reads as nonsense.
  - `:111` says generator-out rows have "two elements out"; `:367` says they are "still N-1".
- **Realism facts the Method never states.**
  - Every one of the 1,500 bases is N-1 insecure: at least 14 and a median of 31 violating
    contingencies per base (VERIFIED).
  - 94% of bases fail 0.95 pu before any outage (`data/bases_clearing_0p95.json` → `canonical_v2.ge_0p95` = 86).
  - 73.4% of N-0 bases exceed 1.05 pu (`data/thermal_check.json` → `networks.case118.overvoltage.n0_base.share_above_1p05`).
  - On average 21 of 53 generators sit at a Q limit in the base case (`data/classical_screen_metrics.json`
    → `gens_at_qlim_base.mean`).
  - Generator setpoints are jittered ±0.025, Q limits are scaled by U(0.6, 1.4), and there is no MW
    re-dispatch. Reported: `feasibility/generate_dataset.py:26,124-144`.

**Fix.** Mostly text, plus existing data: certify-only speedup, false-flag column, break-even. The
Q-limit label audit is a new check (item N3 in §6).

### 5. MAJOR for the 15-scientist panel: page 1 does not say the question, the answer, or why it matters, and the page budget has no headroom

- **Page 1.** The abstract (`:81`) lists five numbers and ends without a finding ("allow operators to
  make an informed decision"). The introduction never states a question or result (`:94-101`).
  Nothing on page 1 says the headline is a *limiting* result.
- **Title noun.** "Boundary mass" (`:63`) is never defined anywhere in the body.
- **"Coverage" has two meanings.**
  - `:128`: P(true value ≥ lower edge).
  - `:231`: redefined as the acceptance rate.
  - The same axis is also called "coverage target", "safety target" and "coverage axis" (`:241`,
    `:281`, `:292`).
- **Contribution list.** `:101` lists a scope restriction ("only under-voltage") as a contribution.
  The genuine strengths are buried: the self-caught clipping bug (`:121`), the sealed/hashed
  cross-network predictions (`:355`; "hashed" is never explained), and the net-cost accounting.
- **Page budget.** An estimated **about 19 counted pages** at the current `\setstretch{1.5}` (§7).
  Anything added under items 1–4 must be paid for with cuts.

**Fix.** Text only. Restructure the abstract and introduction as question → mechanism → headline
with the honest operating point → when it pays off (ρ·q̂) → why it matters. Define the 5–6 blocking
terms (§4c).

---

## 1. Map: tables and figures → script → data

Every PNG's sha256 matches the `output_sha256` in its manifest (checked 2026-09-23 with `shasum -a 256`).

| Float | Line | File | Generator | Data inputs | Traceable? |
|---|---|---|---|---|---|
| Fig. 1 `fig:gate` | `:154` | `data/gate_schematic_v4.png` | `feasibility/gate_schematic.py` | `data/tradeoff_curve_v2.json` | Yes (`data/gate_schematic_v4.manifest.json`, byte-reproducible) |
| Table I `tab:models` | `:206-226` | inline | `scripts/emit_v2_tables.py` → `notes/paper_tables_v2.tex` | `data/tradeoff_curve_v2.json`, `data/tuned_metrics.json`, `data/screener_metrics.json` (persistence and train-mean rows) | Yes. 3 of 4 rows are byte-identical to the emitter output. The train-mean speedup cell was hand-changed from the emitted `2.1×10^7` to `N/A†`; this is intentional and the caption explains it (`:208`). |
| Table II `tab:ops` | `:239-268` | inline | `scripts/emit_v2_tables.py` | `data/tradeoff_curve_v2.json` | Yes. All 12 rows are byte-identical to the emitter, and all recomputed values match (`scratch/number_audit.py`). |
| Fig. 2 `fig:tradeoff` | `:280` | `data/tradeoff_hero_col_v2.png` | `feasibility/paper_hero.py` | `data/tradeoff_curve_v2.json` | Yes |
| Fig. 3 `fig:missdepth` | `:302` | `data/miss_depth_v3.png` | `scripts/miss_depth_fig.py` | `data/miss_depth_pool.json` | Yes. **Stale LaTeX comment** at `:296-298` names `miss_depth_v2.png` / `missed_depth.json`. It is not rendered, but fix it. |
| Fig. 4 `fig:boundary` | `:322` | `data/boundary_mass_hist_v2.png` | `feasibility/boundary_mass_hist.py` | `data/dataset.parquet`, `data/frozen_poster_numbers.json` | Yes. **Stale comment** at `:316-318` names `boundary_mass_hist.png`. |
| Fig. 5 `fig:busmap` | `:338` | `data/critical_bus_map.png` | `feasibility/domain_figure.py` | `data/dataset.parquet`, `data/bus_layout.json` | Yes. The manifest's `manuscript_role` field says the figure is "Not referenced by report/paper_current_STS.tex", which is stale: it is now used at `:338`. |

No float lacks a traceable source. All seven floats carry the Appendix-3 attribution line (`:158`,
`:223`, `:265`, `:284`, `:306`, `:327`, `:342`). **Fig. 5's line sits after `\label` (`:340-342`), so
check that it renders under the caption like the others.**

---

## 2. Number audit

**Method.**
- `scratch/provenance_sts.py` runs the repo's own matcher (`scripts/check_paper.py`) over `data/` and
  its subfolders. The stock script finds 0 artifacts for this file, because it looks for `data/` next
  to the tex (`report/data`).
- Of 218 distinct literals, **207 are matched, 6 orphaned and 5 ambiguous**.
- Value matching alone produces coincidences (for example, `3.29` matched a bus-layout coordinate).
  So `scratch/number_audit.py` re-derives every result number from its *intended* key.

### 2a. Verified against the intended source (all match to the printed precision)

| Claim (line) | Source |
|---|---|
| Table I and Table II, all 16 printed rows (`:215-218`, `:248-260`) | `data/tradeoff_curve_v2.json` → `records[model, coverage_target]`. MAE and R² come from `data/tuned_metrics.json` m2 records. |
| 3.29×, 4.72% (`:81`, `:199`); 63.7%, 1.58×, 0.97 (`:81`, `:231`) | same; the 0.94 / 0.97 crossings come from `data/frozen_poster_numbers_v2.json` → `crossings_first_below_1pct_missed` |
| R² 0.77 / 0.92; MAE 0.0038 / 0.0016 (`:199`) | `data/tuned_metrics.json` m2: 0.772 / 0.923; 0.00375 / 0.00156 |
| q̂ 0.0052 / 0.0023 (`:132`) | `data/tradeoff_curve_v2.json` → `records[*,0.90].q_hat` |
| t_solve 9.14 ms, min of 400 (`:147`) | `data/solve_time.json` → `ms_solver`, `n_timed` |
| t_surr 0.00116±0.00012 / 0.00241±0.00062 ms (`:147`) | `data/tuned_metrics.json` → m2 `ms_surrogate` (seed mean ± std). Re-measuring gives histgb **0.00346** ms (`data/break_even.json` → `timing.ms_infer_measured_now`), 43% higher. Immaterial to speedup, but the ± understates it. |
| S_mean 0.6038±0.0757 / 0.7919±0.0743 (`:189`) | `data/barrier_height.json` → `summary_at_090.case118.*.S_mean_over_qhat_at_090_*` |
| 74% / 55% within q̂; 26.7% / 21.4% beyond 0.005 pu (`:292`, `:303`) | `data/missed_depth.json` → `families.*.pooled["0.90"].share_below_qhat` (0.737 / 0.549) and `share_below_strip` (0.733 / 0.786) |
| 0.0915 pu, 0.8485 pu (`:292`, `:303`, `:367`) | `data/missed_depth.json` → `families.*.deepest_missed` |
| 56.86%, 17.48%, 278,955, 280,500, 0.7179–0.9603 (`:119`, `:314`) | `data/frozen_poster_numbers_v2.json` → `dataset_facts` |
| 27.1 / 16.81 / 9.31% at buses 76 / 53 / 107 (`:314`, `:339`) | `dataset_facts.critical_bus_top5`, 0-based index + 1 |
| "about 14%" / 14.1% tallest bin (`:314`, `:323`) | `data/unconditioned_base.json` → `committed_gated.largest_bin_share_pct` = 14.06. This **closes** the NO SOURCE flag in `notes/claims_map.md` Part 2. |
| 35.17%, 55.5% → 56.86% (`:121`) | `data/clip_artifact.json` → `clip_era.clip_atom_share_pct`, `.boundary_0p94_to_0p945_pct` (55.51), `fixed_v2.*` |
| 374 / 1,500 = 24.93%; 69,532 rows; 30% draw (`:119`, `:367`) | `data/sampling_audit.json` → `prevalence.*`, `outage_probability.as_coded` |
| 82.64 / 74.89 / 82.79% (`:347`) | `data/frozen_poster_numbers_v2.json` → `ceilings.*` |
| 99.5% persistence escalation (`:349`) | Table I row |
| 0.4726 / 0.4933; 0.1163 / 0.1056 (`:353`) | `data/netstudy2/summary.json` → `cross_network.*` |
| 0.9012 pu, case57 (`:353`) | `data/netstudy/case57/nofeasible_diagnostic.json` (`min_vm_pu` 0.90121). The claim is correct, but see Top 5 item 4 on the zero-load framing. |
| 392% / 16 of 50; 199.37% (`:353`) | `data/netstudy2/case89pegase_nofeasible_diagnostic.json` → `worst_trafos_at_nominal[0].loading_pct` (392.21), `n_trafo_over_100_at_nominal`, `scaling[7]`. "The transformers … were at 392%" overgeneralizes: that is the *worst* transformer. |
| 111.83% (`:119`, `:365`) | `data/network_triage.json` → `networks[2].base_max_loading_pct` |
| case30 regenerated: 7.09, 15.40, 5.84±1.25, 0.76±0.20, 0.91±0.22 with 2 of 5 splits (`:81`, `:365`) | `data/case30_thermal/case30_thermal_frozen.json` → `boundary_mass_pct`, `violation_rate_pct`, `records` (recomputed per seed) |
| 61,500 contingencies, 0.87–0.99, 21.5%, 145.8% (`:119`, `:367`) | `data/case30_thermal/h3_build_stats.json` → `range`, `n1_loading.*` |
| 86 of 1,500; 1.38±0.33% (`:365`) | `data/bases_clearing_0p95.json` → `canonical_v2.ge_0p95`; `data/escalation_at_095.json` → `summary.ridge.escalation_at_0.95` |
| 73.1% above 1.05 pu (`:107`) | `data/thermal_check.json` → `networks.case118.overvoltage.n1.share_above_1p05` (0.7314) |
| 9,900 MVA (`:107`) | `data/thermal_check.json` → `networks.case118.rating_audit` (lines: implied MVA 9900 at both kA values; transformers: `sn_mva` 9900). Correct. |
| 0.943 setpoint, bus 76 (`:121`) | pandapower `case118()` gen at bus index 75, `vm_pu` = 0.943 (read live) |
| 0.00371±0.00010, 0.00153±0.00011 (`:373`) | `data/physics_ablation.json`, recomputed: `+F1+F3` ridge m2_searched 0.003707±0.000096; `+F1+F2+F3+F4` histgb 0.001526±0.000111 |
| +10.82%, 0.003754±0.000133, 0.004161±0.000247 (`:375`) | same file, recomputed (10.820%) |
| 0.0015638 / 0.0015539 / 0.0015300; 2.39×10⁻⁵; 7.58×10⁻⁵; 25 scenarios (`:377`) | `data/f1_leakage_audit.json` → `check_4_permutation.*.mae`, `check_2_base_solve_integrity.n_scenarios_checked`; the seed std comes from the physics_ablation histgb baseline |

### 2b. Mismatches and rounding inconsistencies

| Line | Printed | Source value | Severity |
|---|---|---|---|
| `:231` | error bars "up to about 1.0–1.07%" | mean + std = **1.00%** (ridge@0.94) and **1.08%** (histgb@0.97: 0.8322 + 0.2447). The 1.07 comes from adding two already-rounded numbers. | minor |
| `:121` | "55.5% to 56.86%" | 55.51 → 56.86. One number is given to 1 decimal and the other to 2. | minor |
| `:314` vs `:323` | 56.86% (text) vs 56.9% (caption) | same source | minor; pick one convention |
| `:314` | 27.1% / 16.81% / 9.31% | the precision is mixed within a single sentence | minor |
| `:347` | 74.89 / 82.79 / 82.64 (2 dp) next to 30.6 (1 dp) | The claim "lands just above the saturation point" rests on a 0.15-point gap with no std reported. The std rule means it cannot be called "above". | minor, and a std-rule issue |
| `:147` | t_surr histgb 0.00241±0.00062 | a re-measure gives 0.00346 | minor |

### 2c. Numbers not traceable to a `data/*.json` key

| Line | Literal | Only source found |
|---|---|---|
| `:119` | Regional 0.9009–1.2310; 43.91% outside | `notes/RUN_REPORT.md:3790`, `notes/audit-new-sections-layout.md:49`. These were recomputed from `data/dataset.parquet` in a notes file; there is no artifact key. |
| `:119` | Q scales 0.8156–1.4083 | `notes/RUN_REPORT.md:3911` only |
| `:119` | 750 / 750 bases per mode | recomputed here from `data/dataset.parquet` → `sampling_mode` (750 / 750); no artifact key |
| `:323` | 0.5% below 0.87 pu | recomputed here: 0.54%; no artifact key |
| `:375` | 0.000247, 0.004161 | recomputed from `data/physics_ablation.json` records; no summary key |

**Fix.** Emit a small `data/*.json` with a manifest for the load-range and mode facts, per the
project's "manifest beside every artifact" rule. Everything else in the paper traces.

The repo's own checker also flags two banned phrases in this file: `:361` "proven methods" (the
regex matches `\bprove[sn]?\b`) and `:365` "escalation floor".

---

## 3. Consistency across abstract, introduction, results, discussion and conclusion

| # | Contradiction | Where |
|---|---|---|
| C1 | **How many networks.** The abstract names 2 (118, 30). `:355` says "I tested five networks in total, with three … completing". A reader counts **7**: case118, case30 published, case30 regenerated, case39, case24_ieee_rts, case_illinois200, case57, case89pegase (network_triage scanned 14). The conclusion (`:388`) lists "more networks … whether speedup depends on the amount of data … near the threshold" as future work, although `:351-355` already did this on 3 networks. The introduction never mentions the cross-network test. | `:81`, `:355`, `:388` |
| C2 | **Different "safe" criteria for the two networks.** case118 uses the first target whose *mean* missed rate is below 1% (`:81`, `:231`). case30 uses *all five splits* below 1% (`:365`). Under one common rule: mean rule → case30 histgb at 0.96 (4.86% escalation, 21.5×); all-splits rule → case118 ridge at 0.95 (67.9%, 1.48×) and histgb at 0.98 (72.0%, 1.39×). VERIFIED with `data/tuned_metrics.json` per-seed sweeps. | `:81`, `:231`, `:365` |
| C3 | "There must be a certain floor" (`:101`, `:388`) vs "depends on data distribution" (`:365`), case30 at 5.84%, and the unreported Mondrian and limit-sweep results. | `:101`, `:365`, `:388` |
| C4 | Coverage defined as P(y ≥ lower edge) (`:128`) vs the acceptance rate (`:231`). | `:128`, `:231` |
| C5 | "Classical screens … fail to provide a numerical minimum voltage" vs the repo's classical screen, which predicts `pred_min_vm` (`data/classical_predictions.parquet`) and is dominated by the gate. | `:109` |
| C6 | Generator-out rows have "two elements out" vs "these are still N-1 contingencies". | `:111`, `:367` |
| C7 | "Clustering is an inherent characteristic of the network" vs the unreported quintile and unconditioned artifacts. | `:121` |
| C8 | "The more accurate model is not safer at any point in the coverage axis" vs matched escalation, where ridge@0.94 (64.3±2.8, 0.79±0.21) and histgb@0.97 (63.7±5.1, 0.83±0.24) are indistinguishable. At ~50% escalation histgb is *safer* (histgb@0.95 1.94±0.21 vs ridge@0.90 2.96±0.44). | `:292`, `:249`, `:257-259` |
| C9 | "Total demand is concealed from the model" vs the 118 per-load `pload_*` features, whose sum *is* total demand (`feasibility/make_splits.py:14-18` drops only `agg_loading`). Reported by the statistics reviewer; the column family was verified via `data/sampling_audit.json` → `multiplier_audit.empirical_family_variance.pload_`. | `:371` |
| C10 | "Reflect the true end-to-end cost" vs dataset generation, tuning and training all excluded (`data/break_even.json`). | `:99` |
| C11 | The worst-miss mechanism text vs `data/miss_mechanism.json` (absorbing limit; see Top 5 item 4). | `:367` |
| C12 | The title's key noun, "boundary mass", is never defined; the body uses "boundary band", "boundary layer" and "within 0.005 pu of the boundary". | `:63`, `:81`, `:312`, `:314` |
| C13 | The abstract says error bars go "slightly above 1%"; `:349` says "still touching". Neither mentions that 2 of 5 histgb splits exceed 1% at 0.97, or 4 of 5 at the held-out point. | `:81`, `:349` |

The headline numbers are *numerically* consistent everywhere they repeat: 3.29, 4.72, 63.7, 1.58,
56.86, 17.48, 0.0915 / 0.8485, and "almost two-thirds … 1.6" (`:388`).

---

## 4. Reviewer panels

Three independent subagents reviewed the paper read-only. Their rankings are condensed below, with my
verification status. Items already covered in the Top 5 are only referenced.

### 4a. Power-systems PhD

**FATAL**
- **PS-F1** Boundary mass is produced by the N-0 filter at the same limit. → Top 5 item 1 (VERIFIED).

**MAJOR**
- **PS-M1** Unrealistic operating points: all bases are N-1 insecure; 94% fail 0.95 pu at N-0; about
  40% of generators sit at Q limits; setpoints are uncoordinated; there is no re-dispatch. → Top 5
  item 4 (VERIFIED except the code-line citations `generate_dataset.py:26,124-144`, which are Reported).
- **PS-M2** The worst "violation" is physically inconsistent (a PV generator at its absorbing limit
  while below setpoint) and the paper explains it with the opposite mechanism (`:367`). VERIFIED.
  The share of affected labels is unverified.
- **PS-M3** Flags skip the solver; the certify-only speedup is 1.12–1.24×; ridge's false flags are 11%.
  VERIFIED.
- **PS-M4** The safety metric pools rows. At ridge@0.94 there are 59–111 misses per seed across
  about 300 test bases (`data/qlimit_class.json` → `per_seed_depth[*].n_missed`, VERIFIED). The
  per-base "any miss" rate needs a refit and is unverified.
- **PS-M5** Solver timing (cold start, about 3 bases, Python overhead) and uncounted one-time cost; 10
  cores give 5.4×. VERIFIED except the 0.13 ms LU figure (Reported).
- **PS-M6** The classical baseline was run and omitted, and it is misdescribed at `:109`. VERIFIED.
  Caveat: the linear screen holds PV buses fixed, so it cannot see Q-limit switching. Say that it is a
  weak baseline.
- **PS-M7** The case30 contrast is confounded by a different sampler; the zero-load diagnostics for
  case57/pegase are physically misleading. VERIFIED (h3 stats, pegase scaling).

**MINOR**
- `:81` "safe" should be "no under-voltage" (over-voltage and thermal are unchecked).
- 0.94 as both the N-0 and N-1 limit is non-standard, and "conservative" (`:365`) is undefined
  relative to what.
- G-1+N-1 framing: `:111` vs `:367`.
- The 45 non-converged rows are dropped silently. They are harmless: histgb certifies 0–1 of them
  (`data/nonconverged_gate.json`).
- "Dynamic stability" is misused (`:367`).
- TPL-001 is a planning standard, sets no 0.94 limit, and its P1 events include generator outages
  (`:97`); the citation is imprecise.
- In 26% of rows the minimum sits at a PV bus holding its setpoint, which is an input feature.
  VERIFIED: `data/classical_screen_metrics.json` → `qlimit_analysis.by_weakest_bus_type.PV.n` = 72,725.
- Surrogate timing excludes feature assembly.
- "111.83% unrealistic" is one line over one rating; say that.

**Already acknowledged in the paper:** over-voltage and thermal unchecked (`:107`, `:367`);
speedup ≈ 1/escalation (`:147`); "synthetic loads and generation" (`:365`). None of PS-F1 or
PS-M2–M6 is acknowledged.

### 4b. Statistics / ML PhD

**FATAL**
- **ST-F1** The escalation floor restates the gate definition; "must" is refuted by Mondrian. →
  Top 5 item 2 (VERIFIED).
- **ST-F2** Missed rate has no guarantee; the operating point was selected on test; the held-out
  headline misses the 1% target for histgb. → Top 5 item 2 (VERIFIED).

**MAJOR**
- **ST-M1** Sampler-driven boundary mass. → Top 5 item 1.
- **ST-M2** The exchangeable unit is the base case, but q̂ uses 55,791 correlated rows from about 300
  bases. The splits *are* grouped (`feasibility/make_splits.py`, GroupShuffleSplit on `scenario_id`),
  and the ⌈(n+1)(1−α)⌉ rank is correct. But the coverage SD across splits is 1.0–1.3 points, against
  about 0.18 expected for i.i.d. rows, so the effective n is about 10³ (Reported; the per-seed
  coverages are consistent with `data/tuned_metrics.json`). 89.3±1.3 is still consistent with a
  marginal guarantee. `:132` misstates the condition as "same type of condition (a single-element
  outage)"; it should be "base cases exchangeable under the same sampler". The hierarchical-conformal
  citation (Dunn–Wasserman–Ramdas) suggested by the reviewer is **unverified**; verify it before
  citing.
- **ST-M3** Flags are uncosted, so the metric pair can be gamed. Train-mean gets 0% escalation and 0%
  missed by flagging everything (`:216`). → Top 5 item 4.
- **ST-M4** "Faster is not safer" is compared on the wrong axis. → C8.
- **ST-M5** Baselines are weak while stronger ones sit on disk (classical, Mondrian). Sweeping the
  target is the same as sweeping a non-conformal margin, so conformal adds a coverage label, not a
  better curve. CQR (cited at `:132`) and a direct violation classifier are untested.
- **ST-M6** The physics ablation is misread:
  - F1 is a deterministic (nonlinear) function of inputs already in the model.
  - MAE is the wrong endpoint by the paper's own thesis. Ridge +F1+F2 MAE is +10.8%, yet escalation
    at 0.94 *falls* from 64.3±2.8 to 59.0±2.8 while missed goes 0.79 → 1.00±0.37, within std
    (VERIFIED from `data/physics_ablation.json` → `records[].by_target`).
  - Ridge picks α = 0.001 in 3 of 5 seeds, so the F2 block of about 186 collinear columns is fit
    nearly unregularized.
  - The single-seed shuffle compares a paired difference against an unpaired between-seed std.
  - **Additional finding (mine, VERIFIED).** F3 (LODF rows) and F4 (electrical distance) have exactly
    186 rows each, keyed only by outaged element (`data/physics/lodf.parquet`,
    `data/physics/edistance.parquet`, shape 186×189 and 186×120). They are therefore a fixed
    function of the branch one-hot already in the model, so their null result is guaranteed by
    construction. For ridge, the per-split MAE with F3 added (fixed α) is identical to 7 digits with
    and without F3. `:373-379` should not present F3/F4 as a physics test.
- **ST-M7** Cross-network: ρ·q̂ is a first-order expansion, and the 0.47 average hides the failure
  mode (case24 ridge). VERIFIED.

**MINOR**
- ± is a population std over 5 overlapping resplits, not a CI.
- S_mean (`:183-189`) is never used, and normalizing by q̂ reverses the ordering. The informative
  quantities, P(o > q̂ | violation) = 0.39 / 0.41 and S_p99 = 6.5 / 9.8, are already in
  `data/barrier_height.json` (VERIFIED).
- Non-converged cases are dropped silently.
- HistGB early stopping uses a row-random internal split (`notes/reviewer-issues.md` Issue 5);
  disclose it in one line.
- Garbled sentences at `:132` and `:363`.
- **No hyperparameter leakage found.** Tuning stays in a grouped inner split
  (`scripts/tune_surrogates.py`); the only selection leak is the operating point.
- **Std-rule check: no violations.**

**Carried over from `notes/prior-art.md` §8.7, still open:** `:363` cites `barber2021` for "perfect
correctness … intervals become extremely wide". That paper's result concerns **conditional**
coverage, not perfect correctness.

### 4c. Non-specialist panel scientist

**Grades from the title, abstract and page 1:**

| Question | Grade | Why |
|---|---|---|
| Question asked | C | Never stated as a question. |
| Main result | C− | The numbers are there, but the causal link from 56.86% vs 7.09% to 63.7% vs 5.84% is never stated. |
| Why it matters | D | Only "computationally expensive" (`:81`, `:97`). |
| What is new | C | `:101` lists a scope restriction; the self-caught bug and the sealed predictions are buried. |

**Blocking undefined terms, in reading order:**
- "boundary mass" (`:63`, never defined);
- per-unit, split-conformal and coverage, all used in the abstract before `:107` / `:128`;
- "thermally feasible" (`:81`, never defined as a concept);
- the two meanings of "coverage" (`:128` vs `:231`);
- LODF (`:373`, never expanded).

**Confusing ones:**
- N-1 ("N" is never explained); AC (expanded only at `:119`; DC is expanded at `:81`);
- "escalation floor" (`:101`, never defined); case118 vs IEEE 118-bus; case39 / case24 / illinois200
  (never described);
- MVA, slack, reactive power limits, Independent vs Regional mode (`:119`, never explained);
- exchangeability (`:367`); one-hot (`:379`); predictor A/B (`:353`); "locked and hashed" (`:355`);
- code identifiers in prose (`agg_loading`, `vm0_*`, `pre_p_mw`, `:371`, `:377`).

**Readability:**
- The reject-option digression (`:314`) interrupts the key mechanism section.
- The escalation-ceiling paragraph (`:347`) is very hard to follow.
- The dataset paragraph (`:119`) is a wall of numbers.
- The ablation (`:369-379`) sits inside Limitations, disconnected from the story.
- Sentences that do not parse: `:107` ("although 73.1% of converged N-1 rows the highest bus voltage…"),
  `:143`, `:167`, `:361`, `:363`, `:377`.
- Typo: "locked tes" (`:353`).

**Signals of promise are present but buried:**
- the clipping-bug discovery (`:121`);
- the sealed/hashed predictions, which amount to pre-registration (`:355`);
- the permutation control and leakage audit (`:377`);
- honest net-cost accounting (`:99`, `:145`).

Its suggested story is: the 118-vs-30 contrast as a natural experiment, plus "I pre-registered a
prediction on three unseen grids", plus "I caught a bug in my own data". This is consistent with
Top 5 items 1 and 3, *after* the confound is handled. The confound must be handled first, or the
natural-experiment story is exactly what a PhD judge will attack.

---

## 5. Novelty: does it survive "this is just split conformal plus a threshold"?

This section uses only `notes/prior-art.md` and the paper's own descriptions, as the task required.

**The pieces, and where each already exists:**
- Split conformal: `lei2018`, `vovk2005`.
- Three-way certify / flag / defer: conformal triage (prior-art A3). Its deferral target is a human.
- Routing uncertain cases to a costlier model with cost-based thresholds: DeSalvo cascades and the
  LLM cascade papers UCCI / C3PO / RouteNLP (prior-art A2: "well populated in the 2024–2026 LLM
  literature").
- Conformal plus contingency screening on **IEEE-118**, including the locally adaptive KCP that this
  paper does not use: `alcantara2026` (prior-art A1, §6.3). Its scope is a binary flag, with voltage
  claimed but thermal demonstrated.
- Surrogate, exact-AC fallback, net solve count, and concern about shift: `manoharan2026` (prior-art
  B5). Per the prior-art record it shares "surrogate + exact-AC fallback + net cost + shift concern";
  its delta is thermal-only, population-level LTT / Clopper–Pearson rather than a per-instance band.

**The paper's three stated deltas (`:101`), tested:**

1. **"A three-way gate on each contingency."** Correct only relative to the two power papers.
   Conformal triage is three-way. The paper concedes this at `:361` ("proven methods"), which
   contradicts presenting it as a contribution at `:101`.
2. **"Only under-voltage."** A scope restriction, not a contribution. The accurate delta is
   *demonstrated* on voltage, where `alcantara2026` only claims voltage (prior-art §6.1). That is
   worth stating precisely.
3. **"Explain why there must be a floor."** As written this is the gate's definition (Top 5 item 2),
   and "must" is refuted by Mondrian.

Net-cost accounting (`:99`) is **not** a delta against `manoharan2026`, which reports net AC solves
(prior-art B5).

**What would survive the challenge.** Not the method; the paper should claim no method novelty,
consistent with the project's own ceiling. What survives is an **empirical, pre-registered
characterization of when a conformal gate pays**:

- escalation ≈ ρ(L)·q̂, where ρ(L) is the density of operating points at the limit, a quantity
  measurable before any model is trained;
- that density is shown to be driven by the N-0 margin distribution relative to the limit, within
  one network (quintiles, limit sweep, 2C drift);
- the law is tested out of sample on three networks with sealed predictions, including its failure
  mode (wide ridge q̂ on case24);
- the gate is shown to beat a classical conformalized screen.

"Split conformal plus a threshold" does not predict any of that. This is also consistent with the
fact that the closest prior work already applies locally adaptive conformal on IEEE-118 (prior-art
§6.3–6.4). The paper should say so and position Mondrian as a known remedy that lowers, but does not
remove, the escalation driven by boundary density.

**Pre-submission risks:**
- **Manoharan not re-read.** Prior-art §6.6 says the `manoharan2026` record rests on a 2026-07-19
  HTML skim and must be re-read in full before citing. It is the closest prior work, so do this
  first. A lit note exists (`notes/lit/notes/Audited Selective Verification…md`); it was not used
  here, per the task scope.
- **Open bibliography items:** `romano2019` page numbers are unconfirmed (prior-art §8.8), and the
  `barber2021` claim precision is still open (§4b).

---

## 6. Improvement opportunities

**Timeline.** From 2026-09-23 to the late-October internal "done" date is about 4.5 working weeks.
The hours below are the author's estimates of their own time, including code, checking and prose.
Compute is minutes unless stated.

### 6a. From existing results only (no new solves, no refits unless noted)

| # | Analysis | Objection it answers | Hours | Risk | Before Nov 5? |
|---|---|---|---|---|---|
| E1 | **Limit sweep figure** (escalation and boundary mass vs L, 0.900–0.955) **plus the N-0 quintile table plus the unconditioned numbers**; reframe the mechanism | PS-F1 / ST-M1 (sampler confound), C3, C7 | 8–12 | Low (data exist: `data/sweep_results_long.parquet`, `data/quintile_boundary_mass.json`, `data/unconditioned_base.json`). The narrative risk is that the headline changes from "case118 floor" to "margin-driven floor". That is an honest improvement. | Yes, and first |
| E2 | **Escalation vs ρ·q̂ across all 5 networks** (132 points; log-log r = 0.92), with per-network ratios and the case24-ridge failure explained | ST-F1 (turns the identity into a tested law), ST-M7, C1 | 5–7 | Low. Must show the ridge failure, not hide it. | Yes |
| E3 | **Add case39 / case24_ieee_rts / case_illinois200** as boundary-mass vs escalation data points (BM 4.43 / 20.70 / 19.33%; histgb esc@0.90 3.7 / 17.2 / 7.8%) in the case30 comparison | C1; strengthens beyond one network | 2–3 (with E2) | Low | Yes |
| E4 | **Report the case30 speedup** (histgb@0.97 17.9±3.7×; @0.90 38.6±6.2×) and **one "safe" criterion for both networks** | C2; the missing half of the abstract contrast | 1–2 | None | Yes |
| E5 | **Held-out operating point** from `inner_cov_at` as the headline (histgb 1.15±0.27% missed, 59.3±4.0% escalation; ridge 0.77±0.78%, 65.4±8.1%) plus per-seed exceedances | ST-F2 | 2–3 | The headline gets slightly worse. That is honest, and a judge will respect it. | Yes |
| E6 | **Classical baseline row / curve** (`comparison_curve_v2.json`, dominance table) | ST-M5, PS-M6, C5 | 2–3 | Low; the result is favorable | Yes |
| E7 | **Mondrian-by-element rows** (0.90 / 0.94 / 0.97) | ST-F1 ("must" floor), prior-art §6.3 | 2–3 | Low. Shows the global q̂ is not best, which is consistent with the reframe. | Yes |
| E8 | **Certify-only speedup plus a false-flag column** (Table II) | PS-M3, ST-M3 | 2 | Low; the headline shrinks (1.58 → 1.24×) | Yes |
| E9 | **Miss depth at the recommended points** (ridge@0.94 max 0.032 pu; histgb@0.97 max 0.0915 pu, still certified) | PS-M4, C8, `claims_map` D5 | 1 | None | Yes |
| E10 | **Drift tests 2C / 2D / 2E table** (ridge 79.5% coverage under the benign→marginal shift; histgb robust) | Project research question 1 (shift); ST-M2 | 3–4 | Low. 2D's gap is only about 2× the std, so state it cautiously. | Yes |
| E11 | **Break-even** (about 787k contingencies ≈ 4,231 sweeps for ridge@0.94) plus the parallel 5.4× context | PS-M5, C10, "why it matters" | 1–2 | Low; unflattering but honest | Yes |
| E12 | **Per-element conditional coverage** under global q̂. Only Mondrian-calibrated per-element coverage is stored (`data/mondrian_element_long.parquet`: min 0.872 / 0.881 at 0.90). The global-q̂ per-element view needs a **refit** (no solves, about 3 min). | ST-M2 | 3–4 | Low | Yes |
| E13 | **Per-base-case (conditional) coverage and "any miss per base case"**. Per-row predictions are not stored, so this needs a **refit** (no solves, a few minutes). The per-N-0-stratum view already exists (E10). | ST-M2, PS-M4 (operator metric) | 4–6 | Medium: may show misses cluster in a minority of bases (informative either way) | Yes |
| E14 | **Ablation on gate metrics, not MAE**; drop the F3/F4 physics claim (null by construction); say what the leakage audit actually shows | ST-M6 | 2 | None; shortens the section | Yes |
| E15 | **Replace S_mean** with P(o > q̂ \| violation) and S_p99 from `data/barrier_height.json` | ST minor m2 | 1 | None | Yes |

### 6b. Experiments that need new runs

| # | Experiment | Objection it answers | Hours (compute) | Risk | Before Nov 5? |
|---|---|---|---|---|---|
| N1 | **Class-conditional conformal / conformal risk control on the missed rate** (calibrate the certify threshold on calibration violations) | ST-F2; gives the safety metric an actual finite-sample bound | 8–12 (minutes) | Medium: escalation rises at a guaranteed 1%, which reinforces the floor story | Yes, top priority among new runs |
| N2 | **Q-limit label audit.** For every violation row, check for a generator at Qmin with V < setpoint. Re-solving about 48.8k violation rows at 9 ms is about 8 min. Cross-check a sample with Q-limit switch-back or a second solver. | PS-M2; oracle label correctness | 6–10 (≈ 10–30 min) | **High impact if positive**: some violation labels, including the headline worst miss, may be artifacts. Run early. | Yes, and early |
| N3 | **Realistic-margin sampler for case118**: N-0 at a normal band (for example ≥ 0.95, ≤ 1.05) and N-1 at a separate emergency limit; rebuild, retune, gate | PS-F1 decisively, PS-M1 | 15–20 (≈ 45 min build + ≈ 1 h tuning) | Medium; E1 already answers most of this with the existing sweep | Yes, if started by about Oct 5 |
| N4 | **Paired 5-seed F1 shuffle control** | ST-M6 | 2–3 (≈ 5 min) | Low value; optional | Yes |
| N5 | **Stronger learned baselines**: a direct violation classifier with two thresholds, and CQR (cited at `:132`) | ST-M5 | 8–12 (minutes) | Medium | Yes |
| N6 | **Warm-start / factorization-reuse solver timing** | PS-M5 fairness | 4–6 | Low; changes only the absolute framing, not the ratio | Yes |
| N7 | **N-2 shift test** (sample N-2 pairs for a subset of bases; evaluate coverage and missed) | Project research question 1; `:132`, `:367` | 15–25 (≈ 10–20 min per 50k solves) | Medium–high; 2D is a partial proxy | Tight; only if E1–E8 are done by about Oct 10 |
| N8 | **Larger network** (for example case300 or a PEGASE case), where the speedup would matter in absolute terms | "Why it matters" | 20+ | High (feasibility filters failed on case57 and case89pegase) | Probably not |

**Suggested order:**
1. E1 → E2 / E3 → E5 → E8 → E6 / E7 (the reframe, plus honest headline numbers).
2. N2 (label audit) in parallel.
3. N1.
4. Then page cuts (§7).
5. Then prose.

Every new artifact needs a manifest (project rule), and the frozen JSONs stay untouched.

---

## 7. Page budget

**No compiled PDF and no TeX toolchain exist in this environment** (`pdflatex` / `latexmk` absent;
`scripts/check_compliance.py:130` also skips `page_count`). The count below is an estimate.

**Rule (confirmed, `notes/sts-constraints.yaml` R05).** Title, abstract and bibliography are
excluded. Appendices count. Anything past page 20 is not read.

**Estimate.**
- Prose from Introduction to Acknowledgments, excluding floats, headings and the abstract:
  **4,780 words** (`scratch/page_estimate.py`, same definition as `notes/writing-guide.md` §6.2).
- Measured density: **345 words/page** (`notes/writing-guide.md` §6.2). That density was measured
  under `\onehalfspacing` (stretch ≈ 1.24). `\setstretch{1.5}` was introduced in commit `48d5675`
  (2026-09-22) and is at `:75`, which lowers the density to about **285 words/page**.
- Graphics: 1.64 pp. Measured from PNG aspect × width / 9 in:
  - Fig. 1: 1.66 in
  - Fig. 2: 3.23 in
  - Fig. 3: 4.09 in
  - Fig. 4: 2.70 in
  - Fig. 5: 3.10 in
- Tabular bodies: about 0.55 pp.
- **Total: about 16.0 pp** at Word-style 1.5, and **about 18.9 pp** at the literal 1.5 now in the
  file. Likely range 18–20. At literal 1.5 there is effectively **no headroom** for E1–E11.
- **First action:** compile once on any machine with TeX and count.

**Words per section:**

| Section | Words | Pages at 285 wpp |
|---|---|---|
| Introduction | 377 | 1.3 |
| Background | 456 | 1.6 |
| Method (incl. Theory) | 1,499 | 5.3 |
| Results (incl. cross-network) | 1,832 | 6.4 |
| Discussion | 722 | 2.5 |
| Ablation subsection | 460 | 1.6 |
| Conclusion and Acknowledgments | 214 | 0.75 |

These counts include captions, so they sum above the prose-only figure.

**What could be cut (≈ 3–4 pp available):**

| Cut | Saves | Why it is safe |
|---|---|---|
| Physics ablation (`:369-379`) → 2–3 sentences (the null, plus the F3/F4-by-construction note) | ≈ 1.3 pp | Its current reading is contested (ST-M6); it is disconnected from the story |
| Critical-bus map, Fig. 5 (`:336-343`); keep one sentence (bus 76's setpoint is the story) | ≈ 0.5 pp | It is decorative once E1 exists |
| Reject-option digression (`:314`, Chow / Tsybakov) → one sentence plus citations, or move it to Discussion | ≈ 0.4 pp | It interrupts the mechanism |
| Escalation-ceiling paragraph (`:347`) and S_mean (`:183-189`) → one sentence each | ≈ 0.6 pp | Hard to follow; S_mean is unused |
| case57 / case89pegase exclusion details (`:353`) → one sentence ("no feasible bases under this sampler") | ≈ 0.3 pp | The zero-load physics is misleading (PS-M7) |
| Dataset paragraph (`:119`): move the load-range numbers into one small table or cut them | ≈ 0.3 pp | Wall of numbers |
| Discussion `:361-363`: merge with the introduction's related work | ≈ 0.4 pp | Duplicated positioning |
| Shrink Fig. 3 to 0.45 `\textwidth` (it is 4.09 in tall) | ≈ 0.25 pp | Legibility permitting |

**What must be added.** E1 (one figure plus a 5-row table ≈ 0.8 pp), E2/E3 (one scatter ≈ 0.5 pp),
extra columns in Table I/II for E5–E8 (≈ 0.2 pp), and E10 (a small table ≈ 0.3 pp). That totals
≈ 1.8–2 pp, which fits after the cuts above.

---

## 8. Compliance and disclosure checks noticed in passing

- **Acknowledgments (`:391-393`).** They thank "the program and the teaching fellows and staff". They
  do not state that RISE is fee-based, do not name the instructors or TFs, and do not disclose the
  AI toolchain. Project rule `CLAUDE.md` §8 says to disclose all support; STS Appendix 4 has an AI
  usage chart (`notes/sts-constraints.yaml` R04). How to present this is the author's decision.
- **Links.** No `\url` remains in the body. The one in `\bibitem{case118}` is permitted (R08
  exception). The R08 note about `:287` is stale.
- **Spacing.** `:75` uses literal `\setstretch{1.5}`. The header comment (`:8-12`) still describes
  `\onehalfspacing` as the active setting; update the comment to avoid confusion.
- **Prompt log.** `CLAUDE.md` §8 requires appending every prompt to `notes/ai-prompt-log.md`. This
  task's hard rule forbade modifying existing files, so **the prompt for this review was not
  logged**. The author should append it.

---

## 9. Scripts written for this review (all read-only, in `scratch/`)

| Script | What it does |
|---|---|
| `scratch/provenance_sts.py` | Runs `scripts/check_paper.py` matching against `data/` plus subfolders for the STS tex |
| `scratch/number_audit.py` | Semantic audit: re-derives each claim from its intended key; recomputes the parquet-only facts |
| `scratch/crossnet_points.py` | Escalation vs ρ·q̂ across the 5 networks; per-network ratios; `table_at_090` |
| `scratch/conditional_coverage.py` | Per-element (Mondrian) and per-N-0-stratum coverage from the existing parquet files |
| `scratch/drift_summary.py` | Seed-mean ± std for the 2C / 2D / 2E drift tests |
| `scratch/page_estimate.py` | Prose word count, figure heights, and counted-page estimate at both spacings |
| `scratch/verify_reviewer_claims.py` | Recomputes the reviewer-subagent claims used above (held-out operating point, Mondrian, flags, persistence of the N-0 minimum, worst-miss record, Q-limit depth) |

Run each with `.venv/bin/python scratch/<name>.py` from the repo root. None writes a file. Each runs
in under about 1 minute.

**Not done, and why:**
- **No refits.** E12 / E13 need per-row predictions.
- **No new solves.**
- **No page compile** (no TeX).
- **`manoharan2026` not re-read,** per the task scope.
- **The code-line citations marked Reported** were not all opened. The ones spot-checked all held:
  `generate_dataset.py:256`, `measure_solve.py:20-40`, `parallel_speedup.json`, `pi_ranking k=150`,
  `qlimit_analysis`.
