# Round-1 panel: Reproducibility auditor (REPRO)

Reviewed: `report/paper_current_STS.tex` (460 lines, working tree 2026-09-27) plus the compiled text
`notes/panels/round1_paper_text.txt`. Every number was traced to an artifact and recomputed with my own scripts
(`/Users/rajansaha/.claude/jobs/484f4ac7/tmp/panel_repro/t1.py` to `t8.py`), not with the scratch helpers.
Std = population (ddof=0) over the 5 outer splits unless stated otherwise. `.venv/bin/python` throughout.

## 1. Rubric

| Dimension | Score | One sentence |
|---|---|---|
| Originality | 6 | The three-way conformal gate with exact-solver fallback and net-cost accounting is a sensible instantiation of known ideas; the boundary-mass explanation is the part that belongs to the student. |
| Rigor | 7 | Almost every printed number reproduces exactly from a manifest-backed artifact, but the solver's one-way Q-limit switching contaminates labels (REPRO-01), and one figure caption describes error bars the figure does not draw. |
| Significance | 5 | This is a single-network negative result. Its best generalization evidence (the cross-network predictor) has 47% mean relative error, and the paper reports that only as a pooled mean. |
| Clarity | 6 | The tables are clean and consistent. Mixed rounding, pooled-vs-mean statistics that are not labeled, and a switch between the coverage axis and the escalation axis make the model comparison hard to follow. |
| Student potential | 8 | The provenance discipline is unusually high for any level: sealed predictions, byte-reproducible figures, and manifests beside nearly every file. |

## 2. Findings (ordered by severity)

**REPRO-01. MAJOR (could become FATAL once confirmed). The pinned solver's Q-limit handling produces physically inconsistent generator states. The deepest miss is one of them.**
Anchor: L367 "In addition, the worst case, at 0.0915 per unit, represents a case of sudden collapse where the generator at that particular worst-case scenario's weakest bus reaches the limit of reactive power..." Also L292 and the Fig. 3 caption (L303).
Evidence:
- `data/miss_mechanism.json` → `part1_mechanism.saturated_gens_near_weak_bus_post_outage`: gen 21 (at the weak bus, IEEE 54, index 53) has `at_min: true`, q_n1 = -194.71 = Q_min. So the generator is at its absorbing (lower) limit, not its upper one.
- I re-solved scenario 101000025 with line 78 out (t5.py), rebuilt from the parquet row and reproducing min_vm 0.848543. Gen 21 has setpoint 0.9549 and terminal V 0.8485 while at Q_min. That breaks the PV/PQ complementarity rule: a generator at Q_min must have V ≥ V_set. pandapower's `enforce_q_lims=True` converts PV to PQ one way and never releases the generator.
- Without Q limits the same case solves to min V 0.9390. With a PV/PQ loop that does release generators (t7.py: fix violators at their limit, release a fixed generator when V is on the wrong side of V_set, iterate until nothing changes), it settles in 3 iterations at min V 0.94507. That is the case's own N-0 minimum, so the case is **not a violation**.
- 90 stratified rows (t6.py): 76 of 90 have at least one generator at Q_min with V < V_set − 0.001, with gaps up to 0.090 pu.
- 300 random converged rows (t8.py): 33% have min_vm changed by more than 1e-4 pu. 11 of 300 labels flip (7 violation→safe, 4 safe→violation). Of the 50 recorded violations, 7 (14%) are not violations under the consistent loop. Sample violation rate is 16.7% → 15.7% and the boundary strip is 58.7% → 57.0%.

Consequences:
- The aggregate boundary-mass finding looks robust in this sample.
- The "sudden collapse" story for the worst miss is contradicted by the project's own artifact.
- Missed-violation rates near 1% are measured against violation labels with about 14% label noise in the violation class (n=50, so this estimate is rough).

Caveat: this uses my own back-switching loop on 390 rows. It must be confirmed independently, for example with MATPOWER/PowerModels or a second PV/PQ implementation, before anything in the paper changes.
Fix (content-level):
- Verify the finding.
- If it holds, state the one-way Q-limit convention as a modeling limitation in Background/Method.
- Rewrite the deepest-miss mechanism so it matches `miss_mechanism.json`, or drop the claim.
- Quantify the label-flip rate on a seeded sample of at least 5 splits' worth and report it next to the missed-rate headline.

**REPRO-02. MAJOR. The Fig. 2 caption and text rely on error bars that the figure does not draw.**
Anchor: L281 "The mean missed rate first falls just under..." ("...with the error bars still reaching slightly above 1%"). Also L231 "...error bars still reach up to about 1.0--1.07\%, as Fig.~\ref{fig:tradeoff} shows."
Evidence:
- `data/tradeoff_hero_col_v2.png` shows mean lines only.
- `grep -n "fill_between\|errorbar\|_std" feasibility/paper_hero.py` returns no plotting of std.
- The std exists in `data/tradeoff_curve_v2.json` (`missed_viol_std`, `escalation_std`).

Fix: draw ±1 std bands (both models, both axes) from the existing `*_std` keys and regenerate with a new manifest, or remove "as Fig. 2 shows" and the caption's error-bar clause.

**REPRO-03. MAJOR. The "faster model is not the safer one" claim holds only on the nominal-coverage axis. At matched escalation, which is the risk–coverage axis the paper itself invokes at L231, histgb is safer below about 60% escalation.**
Anchor: L292 "On the IEEE 118-bus system, the more accurate model is not safer at any point in the coverage axis..."
Evidence, from `data/tradeoff_curve_v2.json` records (esc%, missed%):

| Escalation | ridge | histgb | Gap vs larger std |
|---|---|---|---|
| ~42% | 0.87: (42.0, 4.42±0.62) | 0.93: (42.0, 3.09±0.64) | 1.33 > 0.64 |
| ~47% | 0.89: (46.6, 3.50±0.62) | 0.94: (46.7, 2.48±0.38) | 1.02 > 0.62 |
| ~50% | 0.90: (49.1, 2.96±0.44) | 0.95: (51.2, 1.94±0.21) | 1.02 > 0.44 |
| ~64% | 0.94: (64.3, 0.79) | 0.97: (63.7, 0.83) | tie |
| ~72% | 0.96: (71.4, 0.14±0.07) | 0.98: (72.0, 0.30±0.13) | ridge safer |

The literal sentence is VERIFIED: at every one of the 30 targets ridge's missed rate is at or below histgb's, and the gap exceeds the std at 0.73–0.98.

Fix: state which axis the comparison uses. Add the matched-escalation comparison, which is the one an operator paying for solves would use, and adjust the Section IV-B heading and claims to match.

**REPRO-04. MAJOR. The cross-network result is reported only as a pooled mean that hides one failing network.**
Anchor: L353 "Across the resulting 54 predictions of the escalation rate..."
Evidence, recomputed from `data/netstudy2/summary.json` → `cross_comparisons`:
- Pooled |rel err|: A 0.4726, B 0.4933 (VERIFIED).
- Per network (A / B mean |rel err|): case39 0.211 / 0.440; case24_ieee_rts 1.153 / 0.679; case_illinois200 0.054 / 0.361.
- So predictor A beats B on 2 of 3 networks and is off by 115% on case24.
- Spread over the 54: |abs err| A 0.116 ± 0.210, B 0.106 ± 0.114. "Slightly better on absolute error" (0.1056 vs 0.1163) is a gap of 0.011 against a std of 0.21, which fails the std rule.

Fix: report the per-network errors with dispersion and drop "slightly better". Say explicitly that the boundary-mass predictor fails on case24_ieee_rts, and that this bears on how far the "floor" explanation generalizes.

**REPRO-05. MAJOR. The report does not carry enough method detail for anyone to reproduce it, and there is no code or data availability statement.**
Anchor: L119 (Dataset), L124 (Surrogates), L147 (timing).
Evidence. The paper never states:
- Solver settings: Newton–Raphson, `init="dc"`, numba on. Only "reactive power limits enforced" appears, at L111. Source: `data/*.manifest.json` → `solver`.
- Software versions (pandapower 3.5.4, scikit-learn 1.7.2, Python 3.13). Only Matplotlib appears, and only in the graphic lines.
- Generator setpoint jitter ±0.025 pu, Q-limit scaling U(0.6, 1.4), power-factor draw U(0.9, 1.15), and the regional block × ±10% jitter. Sources: `data/dataset.manifest.json` → `run_settings.invocation`; `feasibility/generate_dataset.py:18-27`.
- The hyperparameter search space: 15 ridge alphas logspace(−3, 4) and 24 random histgb draws, from `scripts/tune_surrogates.py:21-25`.
- The selected per-seed configurations: ridge alpha ∈ {1, 0.001, 0.001, 0.001, 0.01}; histgb rand00/13/20/01/16. Source: `data/tuned_metrics.json` → `selections`.
- A repository URL.

Also, `data/dataset.manifest.json` is **retroactive**: `provenance_class.retroactive: true`, and the build-time environment is listed as "unknown". The clip-era parquet behind 35.17% and 55.5% is gitignored (`data/archive_clip/`), so those two numbers cannot be reproduced from the repository.

Fix: add a short reproducibility paragraph or appendix table: solver settings, versions, sampling distributions, search space and chosen configurations, and a repository link. State that the clip-era file is archived outside git.

**REPRO-06. MINOR. The std rule fails in two places.**
- L347 "so its ceiling lands just above the saturation point": histgb ceiling 82.79 ± 0.37 vs saturation 82.64 ± 0.17. I recomputed the saturation over the 5 test splits in t4.py. The gap of 0.15 is less than 0.37.
- L231 and L81 "just under a 1% mean": ridge@0.94 0.79 ± 0.21 and histgb@0.97 0.83 ± 0.24. The paper hedges this correctly, but per seed 1 of 5 ridge splits (1.146%) and 2 of 5 histgb splits (1.162%, 1.032%) are above 1% (`data/tuned_metrics.json`).

Fix: say "at" the saturation point. Report "k of 5 splits under 1%" for case118 too, as the paper already does for case30 at L365.

**REPRO-07. MINOR. The operating-point criterion changes between networks.**
Anchor: L365 "All five splits are under 1\% at 0.97, but not at 0.96..."
Evidence:
- `data/case30_thermal/case30_thermal_frozen.json` → `crossings_first_below_1pct_missed.histgb.coverage_target = 0.96` (mean 0.91%).
- For case118 the paper uses the mean criterion, and 0.97 is 2 of 5 splits above 1%. For case30 it uses the all-splits criterion.
- Case30 ridge is not reported at all. Its crossing is 0.98, with escalation 37.8% and missed 0.51%, so the model ordering reverses on case30.

Fix: use one criterion for both networks and report both models on case30.

**REPRO-08. MINOR. Rounding and precision are inconsistent.**
- 56.86% (L121, L314, L365) vs 56.9% in the Fig. 4 caption (L323).
- 55.5% vs 56.86% in the same sentence (L121). The file gives 55.51.
- 27.1% vs 16.81% / 9.31% (L314). The file gives 27.096.
- 74% / 55% vs 26.7% / 21.4% (L292).
- "1.0--1.07%" (L231): from unrounded values the error-bar tops are 1.00 and **1.08** (0.8322 + 0.2447 = 1.0769). 1.07 only comes from adding rounded numbers.
- "−0.00±0.00" (Table I, train-mean R²).

Fix: fix the precision per quantity type and recompute from unrounded values.

**REPRO-09. MINOR. Pooled statistics are not labeled as pooled.**
L292 and the Fig. 3 caption give 74% / 55% / 26.7% / 21.4%. These are pooled misses across the 5 splits (n = 1,436 ridge, 2,284 histgb; `data/missed_depth.json` → `families.*.pooled["0.90"]`), not per-split means. Per-split, ridge share-within-band ranges 0.67 to 0.79. The two pairs also use different thresholds (one band width vs 0.005 pu), so the numbers are not complements; for histgb 55% + 21.4% ≠ 100%.

Fix: say "pooled over five splits", give the per-split range, and name both thresholds.

**REPRO-10. MINOR. Some numbers have no tracked artifact key (all recomputed and correct).**
- Regional multiplier 0.9009 to 1.2310 and 43.91% outside, Q-scale 0.8156 to 1.4083, and 0.5% below 0.87 pu: these appear only in `data/sts_dataset_facts.json`, which is **untracked** (created 2026-09-27 18:03, during this panel).
- "Most... within 0.005 pu" (L314): 61.6%, no key.
- The tallest 0.001 pu bin, 14.1% (L314, L323): exists only as a removed in-image string in `boundary_mass_hist_v2.manifest.json`.

Fix: commit `sts_dataset_facts.json` and its script, and add keys for the tallest bin and the ±0.005 share.

**REPRO-11. MINOR. Figure and manifest details.**
- `critical_bus_map.png` uses `PowerNorm(gamma=0.5)` (manifest → `rendered_numbers.colour_norm`). The colorbar is nonlinear and neither the caption nor the image says so. Dashed edges, probably transformers, have no legend. Its manifest also says `manuscript_role: "Not referenced by report/paper_current_STS.tex"`, which is stale.
- `barrier_height.manifest.json` → `model_hyperparameters: null`. The values match the M2 configurations: I compared per-seed q̂ and missed rates to `tuned_metrics.json` and they agree exactly. The manifest should record them.
- Stale `.tex` comments: L297-298 names `miss_depth_v2.png` / `missed_depth.json` but the file includes `miss_depth_v3.png` from `miss_depth_pool.json`; L317-318 names `boundary_mass_hist.png`.
- The Fig. 3 shaded strip (0 to 0.005 pu) is not explained in the caption.
- "1.38±0.33%" at the 0.95 pu limit (L365) does not say it is measured at 0.90 coverage (`data/escalation_at_095.json` → `coverage_target`).
- Typo "locked tes" at L353.

**REPRO-12. MINOR. Table I mixes artifacts without saying so.**
The persistence and train-mean rows come from `data/screener_metrics.json` (the committed v1 pipeline). That is legitimate because both are model-independent and use the same test splits (seed 0 n_test 55,789 in both), but the caption should say so. The histgb "t_surr 0.00241 ± 0.00062 ms" has a std of about 26% of the mean. That is fine but worth a word, given that t_solve is a minimum (9.14 ms, mean 9.561).

**Checked and consistent (no finding):**
- Solver config across manifests: `enforce_q_lims=True`, nr, dc, numba.
- Apple M5; n_timed 400 with min 9.138.
- Splits 900/300/300 scenarios, 60/20/20.
- 5 seeds.
- Conformal rank `ceil((n+1)·cov)` (`feasibility/gate_eval.py:11`) matches L128.
- Gate logic and the net-speedup formula match L139-145.
- Inner-selection ceiling of 1% missed (`scripts/tune_surrogates.py:20`).
- No M1 or v1 model number is printed: v2 q̂ 0.0052/0.0023, not v1 0.0050/0.0026.
- All seven floats carry an STS citation line: 5 "Graph created by Rajan Saha using Matplotlib 3.11.1, 2026" and 2 "Table created...". Matplotlib 3.11.1 matches `.venv` and `requirements.txt`.
- Bus labels in `critical_bus_map.png` (76, 53, 107, 1, 21) are IEEE names = index + 1 (indices 75, 52, 106, 0, 20). They match the text.
- The generating-script blobs of all 5 figures match their manifests' `script_git_blob_sha`.
- The three netstudy2 seals read "SEAL INTACT".

## 3. Three strongest parts (protect during revision)
1. **Table II and its provenance** (L239-268). All 60 cells reproduce exactly from per-seed `tuned_metrics.json` records, with ddof=0 matching the stated convention. It is the paper's most defensible artifact.
2. **The boundary-mass explanation of the escalation floor** (L314, L347; Fig. 4). The numbers (56.86% strip, 14.1% max bin, 82.64% ± 0.17 saturation, ceilings 74.89/82.79) all recompute. The strip share stayed near 57% even under the re-solve test in REPRO-01.
3. **The honest pre-registration machinery and the clip-artifact disclosure** (L121, L355). The sealed cross-network predictions with intact hashes, and the self-reported 35.17% clip atom that was found and fixed, are exactly the integrity signals an STS panel rewards. Keep both, and add the per-network breakdown (REPRO-04) rather than cutting the section.

## 4. Open questions
- REPRO-01 needs independent confirmation, and a full-dataset estimate if it holds. How are base cases (N-0) affected? The N-0 feasibility gate uses the same one-way switching.
- Ridge +F1+F2 and +F1+F2+F3+F4 have identical MAE (0.004161 ± 0.000247, `physics_ablation.json`), and with fixed hyperparameters +F1+F3 equals +F1. Presumably this is because F3 (LODF rows) and F4 are per-element constants collinear with the branch one-hot. If so, the paper should say F3 and F4 cannot add information by construction.
- The N-0 acceptance rate (53.82%) lives only in a run log (`frozen_poster_numbers_v2.json` → `n0_gate_pass_rate_pct.source`: "NOT a committed file"). It is not printed now, but it would be needed to reproduce the sampling.

## 5. Per-number table
V = VERIFIED (recomputed); MM = MISMATCH; NS = NO SOURCE in a tracked artifact (recomputed value given). Line = `.tex` line.
Abbreviations: TM = `data/tuned_metrics.json` records[metric=m2]; SM = `data/screener_metrics.json`; DS = `data/dataset.parquet` (converged N-1 rows); C30 = `data/case30_thermal/`.

| # | Line | Printed | Source → key | Recomputed | Status |
|---|---|---|---|---|---|
| 1 | 81 | 3.29× histgb @0.90 | TM sweep net_speedup | 3.2871 ± 0.3020 | V |
| 2 | 81 | misses 4.72% | TM missed_viol | 4.7167 ± 0.9772 | V |
| 3 | 81 | <1% at 0.97, 63.7%, 1.58 | TM @0.97 | 0.8322 / 63.68 / 1.5791 | V |
| 4 | 81 | error bars slightly above 1% | TM @0.97 mean+std | 1.077 | V |
| 5 | 81, 365 | 7.09% case30 strip | C30 frozen boundary_mass_pct; parquet | 7.0862 | V |
| 6 | 81, 121, 314, 365 | 56.86% | frozen_v2 dataset_facts; DS | 56.8629 | V |
| 7 | 81, 365 | 5.84±1.25% | C30 frozen records histgb@0.97 | 5.836 ± 1.250 | V |
| 8 | 107 | 73.1% max_vm > 1.05 | thermal_check n1.share_above_1p05; DS | 73.136 | V |
| 9 | 107 | 9,900 MVA | thermal_check rating_audit | 9900 (lines, trafos) | V |
| 10 | 109 | ~9 ms, Apple M5 | solve_time.json; manifest hardware | 9.14 min | V |
| 11 | 111 | 118 buses, 173 lines, 13 trafos, 186 | pandapower case118 | same | V |
| 12 | 119 | 750 / 750 bases | DS sampling_mode | 750 / 750 | V |
| 13 | 119 | 1.0 to 1.12 independent | dataset.manifest invocation; DS | 1.000004 to 1.119999 | V |
| 14 | 119 | 0.9009 to 1.2310 | sts_dataset_facts.json (untracked) | 0.90086 to 1.23096 | NS |
| 15 | 119 | 43.91% outside | same | 43.906 | NS |
| 16 | 119 | Q 0.8156 to 1.4083 | same | 0.81564 to 1.40833 | NS |
| 17 | 119 | N-0 min > 0.94 | generate_dataset GATE_N0; DS n0_min_vm min | 0.94000004 | V |
| 18 | 119 | 30% gen removal | generate_dataset.py:28 P_GEN_OUT | 0.30 | V |
| 19 | 119, 367 | 374 of 1,500 (24.93%) | sampling_audit prevalence; DS | 374; 24.933 | V |
| 20 | 119 | 1,500 / 280,500 / 1,500 / 279,000 | DS | same | V |
| 21 | 119 | 45 nonconverged, 278,955 | DS | 45; 278,955 | V |
| 22 | 119 | 0.7179 to 0.9603 | frozen_v2 min_vm_min/max; DS | 0.71794 to 0.96031 | V |
| 23 | 119, 314, 365 | 17.48% | frozen_v2 violation_rate_pct; DS | 17.4756 | V |
| 24 | 119, 365 | 111.83% | C30 h2_range_sweep h1.ratings_check | 111.831 | V |
| 25 | 119 | 0.87 to 0.99, ≤100%, "just under 100%" | C30 h3_build_stats range, max_base_loading_pct | 0.87 to 0.99; 99.9993 | V |
| 26 | 119 | 41 branches, 61,500, all solved | C30 dataset.parquet | 41 lines, 61,500, 0 nonconverged | V |
| 27 | 121 | 0.940000 ± 1e-9 cluster, 35.17% | clip_artifact clip_era.clip_atom_share_pct; archive parquet | 35.170 (both definitions) | V (gitignored input) |
| 28 | 121 | bus 76 setpoint 0.943 | case118 gen at index 75 | 0.943 | V |
| 29 | 121 | 55.5% → 56.86% | clip_artifact cited_in_sts | 55.512 → 56.863 | V (precision mixed) |
| 30 | 124 | 60/20/20 | make_splits; splits.json | 900/300/300 scenarios | V |
| 31 | 124 | ≤1% missed selection | tune_surrogates INNER_MISSED_CEIL | 0.01 | V |
| 32 | 124 | five splits | TM seeds | 5 | V |
| 33 | 132 | q̂ 0.0052 ridge / 0.0023 histgb | TM q_hat_90 | 0.005198 / 0.002291 | V |
| 34 | 147 | 9.14 ms, min of 400 | solve_time.json | 9.138, n_timed 400 | V |
| 35 | 147 | 0.00116 ± 0.00012 ms | TM ms_surrogate ridge | 0.0011628 ± 0.0001216 | V |
| 36 | 147 | 0.00241 ± 0.00062 ms | TM ms_surrogate histgb | 0.0024111 ± 0.0006163 | V |
| 37 | 189 | S_mean 0.6038 ± 0.0757 | barrier_height summary_at_090; long parquet | 0.60378 ± 0.07569 | V |
| 38 | 189 | S_mean 0.7919 ± 0.0743 | same | 0.79193 ± 0.07433 | V |
| 39 | 199 | R² 0.77 / 0.92 | TM r2 | 0.7718 / 0.9227 | V |
| 40 | 199 | MAE 0.0038 / 0.0016 | TM mae | 0.003754 / 0.001563 | V |
| 41 | 199 | ridge 49.1 / 89.3 / 2.96 / 2.04 | TM @0.90 | 49.07 / 89.34 / 2.963 / 2.043 | V |
| 42 | 199 | histgb 30.6 / 89.8 / 3.29 / 4.72 | TM @0.90 | 30.63 / 89.82 / 3.287 / 4.717 | V |
| 43 | T1 | persistence 4.2±0.1, −0.06±0.00, 99.5±0.2, 0.31±0.08, 1.00±0.00 | SM model=persistence | 4.246±0.071, −0.061±0.003, 99.53±0.16, 0.311±0.080, 1.005±0.002 | V |
| 44 | T1 | train mean 6.7±0.2, −0.00±0.00, 0.0, 0.00 | SM model=train_mean | 6.732±0.173, −0.0002, 0, 0 | V |
| 45 | T1 | ridge 3.8±0.1, 0.77±0.01, 49.1±2.7, 2.96±0.44, 2.04±0.11 | TM | 3.754±0.133, 0.772±0.013, 49.07±2.66, 2.963±0.439, 2.043±0.106 | V |
| 46 | T1 | histgb 1.6±0.1, 0.92±0.00, 30.6±2.5, 4.72±0.98, 3.29±0.30 | TM | 1.563±0.076, 0.923±0.004, 30.63±2.51, 4.717±0.977, 3.287±0.302 | V |
| 47 | T2 | ridge 0.90 row | TM | matches | V |
| 48 | T2 | ridge 0.94: 64.3±2.8, 94.0±0.7, 0.79±0.21, 1.56±0.07 | TM | 64.34±2.78, 93.95±0.74, 0.794±0.209, 1.557±0.068 | V |
| 49 | T2 | ridge 0.95: 67.9±2.8, 95.0±0.6, 0.45±0.12, 1.48±0.06 | TM | 67.85±2.84, 95.01±0.63, 0.447±0.122, 1.476±0.062 | V |
| 50 | T2 | ridge 0.96: 71.4±1.4, 95.9±0.4, 0.14±0.07, 1.40±0.03 | TM | 71.43±1.41, 95.90±0.39, 0.142±0.072, 1.400±0.028 | V |
| 51 | T2 | ridge 0.97: 73.9±1.0, 96.9±0.2, 0.03±0.03, 1.35±0.02 | TM | 73.91±1.02, 96.94±0.25, 0.027±0.027, 1.353±0.019 | V |
| 52 | T2 | ridge 0.98: 74.8±0.8, 98.0±0.2, 0.00±0.00, 1.34±0.01 | TM | 74.80±0.82, 98.01±0.18, 0, 1.337±0.015 | V |
| 53 | T2 | histgb 0.90 row | TM | matches | V |
| 54 | T2 | histgb 0.94: 46.7±2.8, 93.7±0.4, 2.48±0.38, 2.15±0.13 | TM | 46.68±2.75, 93.68±0.43, 2.476±0.383, 2.148±0.127 | V |
| 55 | T2 | histgb 0.95: 51.2±3.4, 94.7±0.4, 1.94±0.21, 1.96±0.13 | TM | 51.18±3.42, 94.66±0.44, 1.944±0.212, 1.961±0.127 | V |
| 56 | T2 | histgb 0.96: 57.0±4.3, 95.7±0.4, 1.36±0.20, 1.76±0.12 | TM | 56.96±4.25, 95.71±0.42, 1.357±0.198, 1.764±0.124 | V |
| 57 | T2 | histgb 0.97: 63.7±5.1, 97.0±0.2, 0.83±0.24, 1.58±0.12 | TM | 63.68±5.12, 96.96±0.25, 0.832±0.245, 1.579±0.117 | V |
| 58 | T2 | histgb 0.98: 72.0±3.7, 98.0±0.2, 0.30±0.13, 1.39±0.07 | TM | 72.00±3.67, 97.97±0.17, 0.305±0.133, 1.392±0.067 | V |
| 59 | 231 | histgb 0.90→0.94: 4.72→2.48, 30.6→46.7, 3.29→2.15 | TM | as rows 42, 54 | V |
| 60 | 231 | ridge 0.94 (0.79, 64.3, 1.56); histgb 0.97 (0.83, 63.7, 1.58) | TM | as rows 48, 57 | V |
| 61 | 231 | error bars to "1.0--1.07%" | TM mean+std | 1.00 / **1.08** | MM (rounding) |
| 62 | 281 | Fig. 2 "error bars" | tradeoff_hero_col_v2.png; paper_hero.py | no error bars drawn | MM |
| 63 | 281 | crossings 0.94 / 0.97 | frozen_v2 crossings_first_below_1pct_missed | 0.94 / 0.97 | V |
| 64 | 292 | 0.96: 0.14% vs 1.36% | TM @0.96 | 0.142 / 1.357 | V |
| 65 | 292, 303 | 74% / 55% within band | missed_depth pooled["0.90"].share_below_qhat | 73.68 / 54.90 (pooled) | V |
| 66 | 292 | 26.7% / 21.4% deeper than 0.005 | 1 − pooled share_below_strip | 26.74 / 21.41 | V |
| 67 | 292, 303, 367 | deepest 0.0915, bus at 0.8485 | missed_depth deepest_missed | 0.091457 / 0.848543 | V (value); see REPRO-01 |
| 68 | 303 | in-image q̂ 0.0052 / 0.0023 | miss_depth_v3.png vs TM | match | V |
| 69 | 314 | "most" within 0.005 pu | DS | 61.61% | NS |
| 70 | 314, 323 | tallest bin ~14% / 14.1% | DS 0.001 bins | 14.063 at [0.940, 0.941) | NS |
| 71 | 314, 339 | bus 76 27.1%, 53 16.81%, 107 9.31% | frozen_v2 critical_bus_top5 (idx 75/52/106) | 27.096 / 16.808 / 9.308 | V |
| 72 | 323 | 278,955; 56.9% | as rows 21, 6 | 56.86 | V (rounding differs from text) |
| 73 | 323 | truncated at 0.87, 0.5% below | sts_dataset_facts below_0p87 (untracked); DS | 0.541 | NS |
| 74 | 347 | 0.0023 band captures 30.6% | TM | 30.63 | V |
| 75 | 347 | saturation 82.64% | frozen_v2 ceilings (copied from v1, model-free); t4.py | 82.635 ± 0.166 | V |
| 76 | 347 | ceilings 74.89 / 82.79 | frozen_v2 ceilings; 1 − TM p_pred_below_limit | 74.89 ± 0.83 / 82.79 ± 0.37 | V ("just above" fails std, REPRO-06) |
| 77 | 349 | persistence 99.5% | SM | 99.53 | V |
| 78 | 349 | ~1.6× vs 2 to 3.3× | TM | 1.56 / 1.58; 2.04 / 3.29 | V |
| 79 | 353 | 54 = 3×2×9 | netstudy2/summary cross_network.n | 54 | V |
| 80 | 353 | MRE 0.4726 / 0.4933 | same → A/B_mean_rel_error | 0.47255 / 0.49325 | V |
| 81 | 353 | MAE 0.1056 / 0.1163 | same → B/A_mean_abs_error | 0.10561 / 0.11631 | V (std rule fails) |
| 82 | 353 | case57: 0.9012, 24 buses at mult 0.0 | netstudy/case57/nofeasible_diagnostic scaling[0.0] | 0.90121, 24 | V |
| 83 | 353 | pegase 392%, 16 of 50, 199.37% at 0.0 | netstudy2/case89pegase_nofeasible_diagnostic | 392.21, 16/50, 199.369 | V |
| 84 | 355 | 5 networks, 3 complete, hashes intact | netstudy2/run_status seal_verdict | 3 × SEAL INTACT | V |
| 85 | 365 | 15.40% below (case30) | C30 frozen violation_rate_pct; parquet | 15.397 | V |
| 86 | 365 | 0.76±0.20 missed @0.97, 5/5 < 1% | C30 frozen records | 0.759 ± 0.201; 5/5 | V |
| 87 | 365 | 0.96: 0.91±0.22, 2 of 5 | same | 0.909 ± 0.220; 2/5 | V |
| 88 | 365 | 86 of 1,500 above 0.95 | bases_clearing_0p95 canonical_v2.gt_0p95 | 86 | V |
| 89 | 365 | ridge esc 1.38±0.33% at 0.95 limit | escalation_at_095 summary.ridge | 1.385 ± 0.326 (at 0.90 coverage, unstated) | V |
| 90 | 367 | 69,532 rows | sampling_audit n_n1_rows_with_generator_outage; DS | 69,532 | V |
| 91 | 367 | 21.5% > 100%, up to 145.8% | C30 h3_build_stats n1_loading | 21.485 / 145.797 | V |
| 92 | 367 | worst case = generator hit Q limit | miss_mechanism saturated_gens; re-solve | gen at Q_**min** with V < V_set; consistent solve 0.9451 | MM (REPRO-01) |
| 93 | 373 | best ridge 0.00371±0.00010 | physics_ablation m2_searched +F1+F3 | 0.003707 ± 0.000096 | V |
| 94 | 373 | best histgb 0.00153±0.00011 | same +F1+F2+F3+F4 | 0.001526 ± 0.000111 | V |
| 95 | 375 | +10.82%, 0.003754±0.000133 → 0.004161±0.000247 | same | 10.820% | V |
| 96 | 375 | exceeds std either way | searched 406 > 247; fixed 427 > 254 (×1e-6) | holds | V |
| 97 | 377 | 0.0015638 / 0.0015539 / 0.0015300 | f1_leakage_audit check_4_permutation | same | V |
| 98 | 377 | Δ 2.39e-5; seed std ≈7.58e-5 | arithmetic; TM histgb mae std | 2.388e-5; 7.575e-5 | V |
| 99 | 377 | 4 F1 columns, 25 scenarios, all match | f1_leakage_audit check_2 | 25, max err 0.0 | V |
| 100 | 388 | ~two-thirds escalated, ~1.6× | TM | 64.3 / 63.7; 1.56 / 1.58 | V |

Counts (100 rows): **V 91**, **MM 3** (rows 61, 62, 92), **NS 6** (rows 14, 15, 16, 69, 70, 73; each recomputes correctly but has no tracked artifact key).
Findings: FATAL 0 (REPRO-01 could become one), MAJOR 5, MINOR 7.
