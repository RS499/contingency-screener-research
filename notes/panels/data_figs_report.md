# Data & figures report (E1a, E1c, E2a, Fig. 5)

**Date:** 2026-09-27. **Scope:** four new artifacts for the STS revision. Every number below was
read from the new JSON named beside it, which the script computed from the input named in its
manifest. Nothing here is caption text. The captions are the author's to write; the lists below
are facts only.

**What was written (all new files; no existing file in `data/`, `feasibility/`, `scripts/` or
`report/` was touched):**

| Script | Outputs | One manifest per run |
|---|---|---|
| `scripts/sts_manifest.py` | (helper imported by the four builders: hashes, versions, manifest) | — |
| `scripts/sts_dataset_facts.py` | `data/sts_dataset_facts.json` | `data/sts_dataset_facts.manifest.json` |
| `scripts/sts_limit_sweep.py` | `data/sts_limit_sweep.json`, `data/sts_limit_sweep.png` | `data/sts_limit_sweep.manifest.json` (covers both) |
| `scripts/sts_crossnet_scatter.py` | `data/sts_crossnet_scatter.json`, `data/sts_crossnet_scatter.png` | `data/sts_crossnet_scatter.manifest.json` (covers both) |
| `scripts/sts_critical_bus_map.py` | `data/sts_critical_bus_map.png` | `data/sts_critical_bus_map.manifest.json` |

A figure and its values JSON share a stem, so one manifest covers both. Its `outputs` list gives
the sha256, md5 and size of each file.

**Manifest contents:**
- the generating script and its blob sha;
- `regeneration_argv`, repo HEAD, and every input with its sha256;
- the library versions and `generated_utc`;
- a `parameters` block with every constant that shapes the output, including the upstream M2
  hyperparameters for the sweep.

**Byte reproducibility:** every output was generated twice by an independent run of the same
script. The first run went into the job scratch directory, the second into `data/`. The md5s are
identical for all six files, and each manifest records the check (`outputs[].byte_reproducible:
true`).

**Regenerate any of them:** `.venv/bin/python scripts/<name>.py data`. An optional second
argument names a directory of an earlier run, for the md5 check.

**Graphic attribution elements (STS, all three figures):**
- created by the student researcher;
- program: Python 3.13.9 with matplotlib 3.11.1 (the version is recorded in each manifest under
  `packages.matplotlib`);
- year: 2026.

---

## 1. E1a: dataset facts → `data/sts_dataset_facts.json`

Regenerate: `.venv/bin/python scripts/sts_dataset_facts.py data`

**Population:** 278,955 converged N-1 rows and 1,500 base rows (`n_converged_n1_rows`,
`n_base_cases`). The script cross-checks both counts against `data/frozen_poster_numbers_v2.json`:
row count and 56.86% boundary share agree (`crosscheck_frozen_v2.agree = true`).

| Fact | Value (VERIFIED) | Key |
|---|---|---|
| share of N-1 rows with \|min_vm − n0_min_vm\| ≤ 0.001 pu | 77.6487% (216,605 / 278,955) | `n0_persistence.share_within_pct`, `.n_within` |
| same with strict `<` | identical count 216,605 | `n0_persistence.n_within_strict_lt` |
| median \|min_vm − n0_min_vm\| | 3.3135e-6 pu | `n0_persistence.median_abs_diff_pu` |
| mean \|min_vm − n0_min_vm\| | 4.263e-3 pu | `n0_persistence.mean_abs_diff_pu` |
| rows in [0.94, 0.945) | 158,622 = 56.863% of N-1 | `boundary_strip.n_rows`, `.share_of_converged_n1_pct` |
| strip rows whose base N-0 min < 0.945 | 96.2653% (152,698) | `boundary_strip.share_base_n0_below_strip_hi_pct` |
| strip rows whose weakest bus = the N-0 weakest bus | 93.3736% (148,111) | `boundary_strip.share_same_weakest_bus_as_n0_pct` |
| strip rows at IEEE bus 76 (index 75) | 31.6160% (50,150) | `boundary_strip.share_at_bus_index_75_pct` |
| base cases per sampling mode | independent 750, regional 750 | `base_cases_per_sampling_mode` |
| regional per-load P multiplier min / max | 0.900858 / 1.230963 | `load_multipliers.regional_p_mult_min` / `_max` |
| regional P multipliers outside [1.0, 1.12] | 43.9057% of 74,250 values | `load_multipliers.regional_p_mult_share_outside_pct` |
| independent P multiplier min / max (context) | 1.000004 / 1.120000 | `load_multipliers.independent_p_mult_min` / `_max` |
| Q multiplier min / max, all bases | 0.815637 / 1.408329 | `load_multipliers.q_mult_min_all_bases` / `_max` |
| N-1 rows with min_vm < 0.87 | 0.5413% (1,510) | `below_0p87.share_pct`, `.n_rows` |

**Discrepancies vs the brief's expected values:** none.

| Brief expected | Now |
|---|---|
| 77.6% | 77.65 |
| 3.3e-6 | 3.31e-6 |
| 96.3% / 93.4% | 96.27 / 93.37 |
| 750 / 750 | same |
| 0.9009 / 1.2310 | 0.900858 / 1.230963 |
| 43.91% | 43.906 |
| 0.8156 / 1.4083 | 0.815637 / 1.408329 |
| 0.54% | 0.5413 |

**Notes for the author:**
- The multiplier is computed per bus: the base-case load at a bus divided by the case118 load at
  that bus. case118 has 99 loads on 99 distinct buses, so this per-bus ratio equals the per-load
  multiplier. Of those 99 buses, 90 have nonzero Q.
- Loads are stored as float32, so the independent-mode minimum reads 1.000004 rather than 1.0.
- Bus 76's share of the strip (31.6%) is higher than its share of all N-1 rows (27.10%, Fig. 5).
  These are two different denominators; do not mix them.

---

## 2. E1c: limit-sweep figure → `data/sts_limit_sweep.png` + `data/sts_limit_sweep.json`

Regenerate: `.venv/bin/python scripts/sts_limit_sweep.py data`

**Source:** `data/sweep_results_long.parquet` (5 seeds, M2 ridge and histgb, L = 0.900…0.955 in
steps of 0.001). The figure uses coverage target 0.90 only. The parquet's sha256 matches its own
manifest (`source_sha256_matches_its_manifest: true`).

**Boundary-mass definition:** [L, L + q̂). This is the only boundary-mass column the parquet
holds. It is model- and seed-specific because q̂ is. The fixed-width [L, L + 0.005) mass is **not**
in the parquet, so it is not plotted.

**Layout:**
- Two stacked panels with a shared x axis: top = escalation rate, bottom = boundary mass. This
  avoids a dual y axis.
- Each curve is the seed mean with a ±1 population-std (ddof = 0) band.
- A thin black vertical line marks L = 0.94. Its only label is the legend entry.

**Key numbers (VERIFIED; the `summary` block and `curves[model][i]`; fractions in the JSON, % here):**

| | ridge | histgb |
|---|---|---|
| escalation at L = 0.940 | 49.07 ± 2.66% | 30.63 ± 2.51% |
| escalation at L = 0.950 | 1.38 ± 0.33% | 1.58 ± 1.19% |
| escalation mean range, L ≤ 0.936 | 0.64 – 19.60% | 0.26 – 1.77% |
| L of peak escalation mean | 0.941 (51.43%) | 0.940 (30.63%) |
| boundary mass [L, L+q̂) at L = 0.940 | 60.00 ± 2.51% | 31.26 ± 2.99% |

- **Cross-check:** the sweep row at L = 0.940 reproduces `data/tradeoff_curve_v2.json` at target
  0.90 exactly, for both models (`crosscheck_at_0p94_vs_tradeoff_curve_v2[*].abs_diff = 0.0`).
- **Test violation rate (seed mean, `curves[*][i].violation_rate_mean`):**

  | L | violation rate |
  |---|---|
  | 0.940 | 17.36% |
  | 0.941 | 31.08% |
  | 0.950 | 95.71% |

**Caption content (facts only):**
- escalation and boundary mass vs screening limit L at coverage target 0.90;
- M2 ridge and histgb; seed mean ± 1 std over 5 splits;
- boundary mass is [L, L + q̂);
- the vertical line is the study limit 0.94 pu;
- histgb escalation is 0.26–1.77% for L ≤ 0.936, 30.63% at 0.940 and 1.58% at 0.950;
- the escalation peak sits at L = 0.940–0.941 for both models, and the boundary-mass peak sits at
  the same place;
- above 0.94, escalation falls because most test cases become true violations (95.71% at 0.950)
  and are flagged. The low escalation there is not a usable operating point.

**Discrepancies vs the brief:**
- histgb 30.6% at 0.940: matches (30.63).
- histgb 1.6% at 0.950: matches (1.58). Its std is large (±1.19), so the value is imprecise.
- histgb "0.3–1.8% for L ≤ 0.936": the exact range is 0.26–1.77%. The lower end rounds to 0.3,
  so it is consistent.
- **Ridge does not share the flat low region.** It reaches 5.89% at 0.933 and 19.60% at 0.936.
  Its mean stays ≤ 3.23% only up to L = 0.930. Any claim of low escalation below the limit needs
  "histgb", or a lower L bound for ridge.

**Std-rule notes:**
- ridge vs histgb at L = 0.950: 1.38 ± 0.33 vs 1.58 ± 1.19. The gap is smaller than the larger
  std, so no difference can be claimed.
- histgb at 0.940 vs 0.941: 30.63 vs 30.56, the same within noise.

---

## 3. E2a: cross-network scatter → `data/sts_crossnet_scatter.png` + `data/sts_crossnet_scatter.json`

Regenerate: `.venv/bin/python scripts/sts_crossnet_scatter.py data`

**Source:** `data/netstudy2/cross_2a_points.json`, assembled by `scripts/netstudy2_cross.py`
`phase_2a()` from each network's frozen M2 results. The file's sha256 matches its manifest.

**What is plotted:**
- x = the stored `rho_times_qhat`. The script recomputed it as boundary_mass / 0.005 × q̂; the
  maximum error is 0.0 (`max_abs_rho_qhat_recompute_error`).
- y = the stored seed-mean escalation.
- Log-log axes with equal aspect and the identity line y = x (dashed).
- Color encodes the network; marker encodes the model (circle = ridge, triangle = histgb).

**Palette:** Okabe-Ito blue, vermillion, green and orange, plus Tol wine. The dataviz validator
was run on it: all-pairs CVD ΔE ≥ 8.6 (PASS) and normal-vision floor 15.6 (PASS). There is a
contrast WARN on orange; the values JSON serves as the table view.

**Key numbers (VERIFIED):**

| Quantity | Value | Key |
|---|---|---|
| points | 132 (5 networks × 2 models; case118 has 30 targets, the others 9 each) | `all_points.n_points` |
| Pearson r, linear | 0.8105 | `all_points.pearson_r_linear` |
| Pearson r, log-log | 0.9176 | `all_points.pearson_r_loglog` |
| flagged group (median ratio furthest from 1 in \|log\|) | case24_ieee_rts ridge, median esc/(ρq̂) = 0.3408, 9 of 9 points below 0.5 | `flagged_group` |
| r without the flagged group (n = 123) | linear 0.8956, log-log 0.9582 | `flagged_group.sensitivity_without_this_group` |

**Per-network median of escalation / (ρ·q̂)** (`per_network_family[].median_ratio_esc_over_rho_qhat`):

| network | ridge | histgb |
|---|---|---|
| case118 | 0.762 | 1.139 |
| case24_ieee_rts | **0.341** | 0.895 |
| case30_thermal | 1.361 | 0.848 |
| case39 | 1.428 | 0.989 |
| case_illinois200 | 0.990 | 0.948 |

**Points with ρ·q̂ > 1** (`n_rho_qhat_above_1`): case118 ridge 4, case118 histgb 1,
case24_ieee_rts ridge 2. Escalation cannot exceed 1, so the approximation must under-shoot there.
This saturation is visible in the upper right of the plot.

**Caption content (facts only):**
- measured escalation vs ρ·q̂, with ρ = boundary mass / 0.005 pu;
- 5 networks by color and 2 models by marker; 132 points;
- dashed line y = x;
- r = 0.81 (linear) and 0.92 (log-log);
- the case24_ieee_rts ridge points lie well below the line (median ratio 0.34);
- the case118 ridge points bend over where ρ·q̂ > 1 (saturation);
- the source is the netstudy2 phase-2a record, in which nothing is fitted.

**Discrepancies vs the brief:** none. 132 points, r 0.8105 (≈ 0.81), log-log r 0.9176 (≈ 0.92),
case24 ridge median 0.3408 (≈ 0.34).

**Caveats for the author:**
- The case118 boundary mass inside the points file is read from `data/frozen_poster_numbers.json`
  (v1 file). It is a model-independent dataset fact, 56.86%, the same value as in v2.
- The case118 escalations come from `data/tradeoff_curve_v2.json` (M2).
- The network id `case30_thermal` is the source's own label. What "thermal" means in that
  network's setup is documented in `data/case30_thermal/`, not here. Its limit field reads 0.94.

---

## 4. Fig. 5: prose-free critical-bus map → `data/sts_critical_bus_map.png`

Regenerate: `.venv/bin/python scripts/sts_critical_bus_map.py data`

**Provenance:**
- The logic was copied from `feasibility/domain_figure.py`, which is unchanged.
- The data, the frozen layout (`data/bus_layout.json`) and the color map are the same as in
  `data/critical_bus_map.png`: YlOrRd with PowerNorm γ = 0.5.

**Changes from the original:**
- no title and no footer;
- figsize 5.0 × 4.2 in with 9/8 pt fonts, so it stays readable at 0.55–0.6 textwidth. The original
  was 15 × 12 in with 16/13 pt fonts, which prints at about 4 pt at that width.

**Labels:**
- Only **bus 76, bus 53 and bus 107** are labeled. They are IEEE 1-based (index + 1).
- No percentages are printed inside the image. The original's integer-rounded "17%" disagreed with
  the text's 16.81%; the colour bar and the caption now carry the values.

**Verified against `data/frozen_poster_numbers_v2.json` → `dataset_facts.critical_bus_top5`:**
the script asserts that the index matches and that the share matches when rounded to 2 dp. The
result is recorded in the manifest under `parameters.top5_verified_against_frozen_v2`.

| rank | IEEE bus (index) | share recomputed | frozen v2 | match |
|---|---|---|---|---|
| 1 | 76 (75) | 27.0961% | 27.1 | yes |
| 2 | 53 (52) | 16.8084% | 16.81 | yes |
| 3 | 107 (106) | 9.3080% | 9.31 | yes |
| 4 | 1 (0) | 8.4480% | 8.45 | yes, not labeled |
| 5 | 21 (20) | 4.1179% | 4.12 | yes, not labeled |

**Label choice, recorded in the manifest `label_choice_reason`:**
- Bus 1 (8.45%) is close to bus 107 (9.31%), so it renders in a similar orange-red at the top of
  the map without a label.
- If the caption should not leave a reader wondering about that node, either the caption mentions
  bus 1, or the label count goes up to 4. That is the author's call.

**Caption content (facts only):**
- IEEE 118-bus network with a topological (igraph, seed 0) layout; positions are not geographic;
- node color = share of the 278,955 converged N-1 cases in which that bus holds the lowest voltage;
- the color scale is square-root (PowerNorm γ = 0.5);
- lines are solid and transformers dashed;
- bus 76 has 27.10%, bus 53 has 16.81%, bus 107 has 9.31%;
- labels are IEEE bus numbers.

---

## Open items for the lead / author

1. `report/paper_current_STS.tex` still points at `data/critical_bus_map.png` (line 338). Switching
   it to `data/sts_critical_bus_map.png` is an author edit.
2. The E1c ridge caveat in §2: the low-escalation region below the limit holds for histgb only.
3. Nothing is committed (no git writes).
4. To commit, the owner would run:

   ```
   git add scripts/sts_manifest.py scripts/sts_dataset_facts.py scripts/sts_limit_sweep.py \
       scripts/sts_crossnet_scatter.py scripts/sts_critical_bus_map.py data/sts_*
   ```

   Then commit. `scripts/sts_n2_label_audit.py` is another teammate's file and is not part of this
   set.
5. This task's prompt is not yet in `notes/ai-prompt-log.md`. I left that to the lead.

---

# Phase 3

**Date:** 2026-09-27. Three new scripts, each writing new files only:
- `scripts/sts_tradeoff_bands.py`
- `scripts/sts_dataset_facts_b.py`
- `scripts/sts_matched_escalation.py`

**Manifests.** These scripts reuse the repo helpers rather than `scripts/sts_manifest.py` (ledger
P-030): `classical_manifest.build_manifest` (environment, git commit, content sha256, run_settings,
model_hyperparameters) plus `manifest.manifest_path`. Each manifest's `run_settings` records:
- the regeneration argv;
- the input sha256s;
- the output sha256s;
- the reproducibility check.

The Phase-1 scripts were not rewritten.

**Byte reproducibility.** Each script ran once into the job scratch directory, then into `data/`
with that directory as the reference. sha256 is identical for all 4 outputs:
`run_settings.outputs[].repro.same_sha256 = true`.

**Regenerate:** `.venv/bin/python scripts/<name>.py data`.

## P-005: Fig. 2 with ±1 std bands → `data/sts_tradeoff_bands.png` + `.json`

**Source:** `data/tradeoff_curve_v2.json`. The `*_std` keys hold the population std over 5 seeds.

**What is the same as `data/tradeoff_hero_col_v2.png`.** The look is copied from
`feasibility/paper_hero.py`, which is unchanged:
- figsize 3.5 × 2.7 in and the fonts;
- the colours;
- the twin y axis;
- the dash-dot first-sub-1% markers labelled 0.94 and 0.97;
- the 1%-missed guide line and the legend.

**What is new.** Shaded ±1 std bands are drawn around all four curves:
- escalation bands at alpha 0.20;
- missed bands at alpha 0.12.

The lower edge of the missed band is clipped at 0, because a rate cannot be negative. This affects
ridge at 0.97 and histgb at 0.99 (`models.*.points[].missed_band_lower_clipped_at_0`). Because the
bands extend past the curves, the right axis auto-scales to about 0–14.5, against about 0–13 in the
original.

**Key values at the marked points (VERIFIED, from `models.*.points[]`):**

| Model | Target | Missed | Escalation |
|---|---|---|---|
| ridge | 0.94 | 0.79 ± 0.21% | 64.34 ± 2.78% |
| histgb | 0.97 | 0.83 ± 0.24% | 63.68 ± 5.12% |

**Largest std over the axis:**

| Model | Escalation | Missed |
|---|---|---|
| ridge | 3.61 pp | 1.01 pp |
| histgb | 5.12 pp | 1.34 pp |

**Readability at 0.6\textwidth.** I rendered the figure and inspected it at the size it prints.
- **Still readable:**
  - all four lines;
  - the 0.94 / 0.97 markers and their labels;
  - the 1% guide line.
- **Hard to read:**
  - **The bands that matter most are the thinnest.** Near the 1% line the missed band is only
    about ±0.2 pp on a 15-pp axis, roughly 1.5 mm tall in print, and very faint at alpha 0.12.
    A reader cannot see from the figure that the ridge@0.94 and histgb@0.97 error bars reach
    about 1.0–1.08%. The caption or text must give those stds numerically.
  - **Some bands cannot be told apart.** For coverage 0.83–0.90, the escalation band of one model
    overlaps the missed band of the other. Because a model's escalation and missed bands share
    its colour, the bands there cannot be attributed to a curve. The line styles (solid vs
    dotted) still can.
  - **The legend box hides part of a band.** It covers the top of the histgb missed band at
    coverage 0.70–0.76, as it covered the curve in the original.
- **Verdict:** the bands do not make the lines or markers unreadable. They add visible spread only
  where the spread is large, which is at low coverage for missed and high coverage for escalation.

**Caption content (facts only):**
- the Fig. 2 content;
- shading is ±1 population std over 5 held-out splits;
- the missed-band lower edge is clipped at 0;
- ridge@0.94 missed 0.79 ± 0.21%, histgb@0.97 missed 0.83 ± 0.24%.

## P-008: `data/sts_dataset_facts_b.json`

**Population:** 278,955 converged N-1 rows.

| Fact | Value (VERIFIED) | Key |
|---|---|---|
| (a) min_vm in [0.94, 0.945) | 56.8629% (158,622). Matches frozen v2 56.86. | `strip_0p94_to_0p945.share_pct`; cross-check `strip_crosscheck_frozen_v2_pct` |
| (b) \|min_vm − 0.94\| < 0.005, two-sided | 61.6103% (171,865). The closed form ≤ gives the same count. | `within_0p005_of_limit.two_sided_open` / `.two_sided_closed` |
| (b) one-sided below, [0.935, 0.94) | 4.7474% (13,243) | `within_0p005_of_limit.below_only` |
| (c) tallest 0.001 pu bin | [0.940, 0.941), 39,229 rows = 14.0628% | `tallest_0p001_bin.figure_binning` |

**Check on (c).** An integer-index binning gives the same bin and count
(`tallest_0p001_bin.integer_binning_check`), so the result does not depend on floating-point edges.
The figure's edges sit at 0.94 + 2e-16.

**Which definition l.314 means ("Most of the contingencies lie within 0.005 per unit of the
boundary").**
- Both readings reproduce "most", because both are above 50%: one-sided 56.86%, two-sided 61.61%.
- The same paragraph goes on to quantify the strip as "56.86% fall in the narrow range [0.94,
  0.945)". The escalation region it describes is also one band width *above* the limit. So the
  one-sided reading is the one consistent with the paragraph.
- The two-sided 61.61% (REPRO's value) is the literal reading of "within 0.005 pu of the boundary".
- **Author decision:** either say "above" (and cite 56.86), or cite 61.61 for the two-sided claim.
  The two numbers must not be mixed.
- The tallest-bin claim, "not a single 0.001 per-unit bin … more than about 14%", is consistent
  with 14.06%.

## C8: `data/sts_matched_escalation.json` (JSON only)

**Method:**
- Source: `data/tuned_metrics.json` records with `metric == "m2"`, 5 seeds × 30 sweep points
  (coverage 0.70–0.99).
- Per seed, missed_viol (and the coverage target) are linearly interpolated against escalation
  onto a 25–75% grid in 1-point steps.
- There is no extrapolation. A grid point outside a seed's escalation range is dropped for that
  seed.
- Ties in escalation (ridge seeds 0, 1 and 4 at the ceiling) were merged. The missed rate is
  identical at every tie (`seed_ranges.*.max_missed_gap_at_ties = 0.0`), as it must be when the
  escalated set is the same.
- The std-rule verdict is taken only where all 5 seeds of both models reach the grid point.

**Verdict runs (VERIFIED, `verdict_runs`):**

| Escalation | Verdict |
|---|---|
| 25–50% | **histgb safer**. Example: 40%, ridge 4.78 ± 0.52% vs histgb 3.34 ± 0.83%. |
| 51–70% | **tie**. Example: 64%, ridge 0.78 ± 0.14% vs histgb 0.87 ± 0.31%. |
| 71–73% | **ridge safer**. Example: 72%, ridge 0.14 ± 0.06% vs histgb 0.37 ± 0.17%. |
| 74% and 75% | **incomplete**. Only 4 and then 2 ridge seeds reach them, because the ridge escalation ceilings are 73.6–76.0% (`seed_ranges.ridge[].esc_max`). |

**Comparison with the panelist's claim:**

| Region | Panelist | Here |
|---|---|---|
| histgb safer | 30–50% | 25–50% (the grid starts at 25) |
| tie | 55–70% | 51–70% |
| ridge safer | from ~72% | 71–73%, then incomplete |

So the claim is **confirmed in substance**.

**The region boundaries are knife-edge under the std rule**, so the report should not over-state
where one region ends:

| Escalation | Gap vs larger std | Verdict |
|---|---|---|
| 50% | 0.64 pp vs 0.62 pp | passes (histgb safer) |
| 51% | 0.58 pp vs 0.60 pp | tie |
| 70% | 0.18 pp vs 0.21 pp | tie |
| 71% | 0.20 pp vs 0.19 pp | passes (ridge safer) |

**Context for the author.** Both paper operating points sit in the tie region, and in the paper's
own terms the two models are equally safe at matched escalation there:

| Operating point | Escalation |
|---|---|
| ridge@0.94 | 64.34% |
| histgb@0.97 | 63.68% |

**Caveat.** Linear interpolation between coverage targets 0.01 apart is an approximation within
each seed. It is not a new gate run.

**Files (Phase 3):**
- `scripts/sts_tradeoff_bands.py`, `scripts/sts_dataset_facts_b.py`, `scripts/sts_matched_escalation.py`
- `data/sts_tradeoff_bands.png`, `data/sts_tradeoff_bands.json`, `data/sts_tradeoff_bands.manifest.json`
- `data/sts_dataset_facts_b.json`, `data/sts_dataset_facts_b.manifest.json`
- `data/sts_matched_escalation.json`, `data/sts_matched_escalation.manifest.json`

**Graphic attribution elements (`sts_tradeoff_bands.png`):** student-created; Python 3.13.9 with
matplotlib 3.11.1 (in the manifest `run_settings.plotting_library`); 2026.

## Fig. 3 without the deepest-miss annotation → `data/sts_miss_depth_noannot.png`

**Files:**
- Script: `scripts/sts_miss_depth_noannot.py`
- Manifest: `data/sts_miss_depth_noannot.manifest.json` (repo helpers: classical_manifest + manifest)
- Regenerate: `.venv/bin/python scripts/sts_miss_depth_noannot.py data`

**Byte reproducibility:** the script ran once into the job scratch directory, then into `data/`;
the sha256 is identical (`run_settings.outputs[0].repro.same_sha256 = true`).

**Unchanged from `data/miss_depth_v3.png`.** The data and the look are copied from
`scripts/miss_depth_fig.py`, which is untouched, with prose off:
- data from `data/miss_depth_pool.json`, coverage 0.90;
- figsize 3.5 × 4.3 in and the colours;
- log-y 0.001 pu bins out to 0.095;
- the grey 0.005 pu strip;
- the dashed q̂ lines with their value labels ("q̂@0.90 = 0.0052" / "0.0023").

**Removed:**
- the "deepest miss 0.0915 pu" text and arrow;
- the red triangle markers at d = 0.09146 in both panels.

**Remaining in-image text:** axis labels, tick labels, and the two q̂ value labels.

**Labels are NOT corrected.** The pooled depths are the stored pandapower labels, so the bin that
holds the artifact case is still drawn.

| Model | Misses | Max depth | Misses deeper than 0.09 pu |
|---|---|---|---|
| ridge | 1,436 | 0.091457 pu | 1 |
| histgb | 2,284 | 0.091457 pu | 3 |

Source: `run_settings.per_model` (VERIFIED from the pool).

A corrected-label version waits on the author's N2b decision.

**The N2 record of the case**, read and not recomputed (`data/sts_n2_label_audit.json` →
`worst_case_0p8485`, copied into the manifest):
- scenario 101000025, line 78 out;
- stored min_vm 0.848543;
- corrected min_vm 0.945073;
- `flips_to_safe: true`.

**Author items:**
- The Fig. 3 caption and the text at l.292 and l.303 still name this case (ledger P-001).
- Swapping `\includegraphics` to this file is an author edit.

## Conditional strip-share recount → `data/sts_dataset_facts_c.json`

**Files:**
- Script: `scripts/sts_dataset_facts_c.py`
- Manifest: `data/sts_dataset_facts_c.manifest.json`
- Regenerate: `.venv/bin/python scripts/sts_dataset_facts_c.py data`

**Byte reproducibility:** a second run gave the same sha256.

**Population:** converged N-1 rows. There are no non-finite min_vm values in either build.

**Results (VERIFIED from row counts, `builds.*`):**

| Build | Rows | Violation rate | Strip share (unconditional) | Strip share given min_vm ≥ 0.94 |
|---|---|---|---|---|
| ungated `data/unconditioned_base.parquet` | 277,628 | 155,593 = 56.0437% | 80,048 = 28.8328% | **80,048 / 122,035 = 65.5943%** |
| committed gated `data/dataset.parquet` | 278,955 | 48,749 = 17.4756% | 158,622 = 56.8629% | **158,622 / 230,206 = 68.9044%** |

**Differences from `data/unconditioned_base.json`:**
- That file's `conditional_boundary_pct` values are 65.5823 (ungated) and 68.9045 (committed).
- They were computed from 2-dp-rounded percentages in `scripts/uncond_analysis.py`
  `conditional_boundary()`. The manifest records this under `run_settings.rounding_note`.
- The ungated value moves by 0.012 pp (65.5823 → 65.5943). The committed value moves by 0.0001 pp.
- The verifier's 65.594% is confirmed.
