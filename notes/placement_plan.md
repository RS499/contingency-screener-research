# Placement plan for the missing results — `report/paper_current_STS.tex`

**Date:** 2026-09-27. Companion to `notes/number_check.md` (Part A). It follows the ordering of
`notes/sts_review.md` §6.

**Scope.** Location and content only; the author writes every sentence. Anchors quote the first
words of the sentence to search for; line numbers (sha256 `c86e47d6…`) are for navigation only.

**Scripts:** `scratch/confirm_missing.py` (E1, E4–E9, E11), `scratch/crossnet_points.py` (E2/E3),
`scratch/drift_summary.py` (E10). All are read-only.

---

## Part B — Is each missing result confirmed?

VERIFIED means I recomputed it myself from the named file today.

| Item | Source opened | Recomputed | Status |
|---|---|---|---|
| **E1** limit sweep | `data/sweep_results_long.parquet` (5 seeds, L = 0.900–0.955, 56 values), target 0.90, seed mean | See E1 notes below this table. | **DIFFERENT (minor).** The range is 0.26–1.77%; the review said 0.3–1.5%. The 0.940 and 0.950 values are VERIFIED. |
| **E1** N-0 quintiles | `data/quintile_boundary_mass.json` → `quintiles_low_to_high` | Boundary mass 78.39 / 81.28 / 82.36 / 37.31 / **4.98%**; violations 21.54 → 14.21% | **VERIFIED** |
| **E1** unconditioned | `data/unconditioned_base.json` → `unconditioned.*`, **and recomputed from** `data/unconditioned_base.parquet` | See E1 notes below this table. | **VERIFIED** |
| **E2** ρ·q̂ on 5 networks | `data/netstudy2/cross_2a_points.json` → `points` (132) | Pearson r = **0.810**; log-log r = **0.918**. Histgb median esc/(ρq̂) is 0.85–1.14 on all 5 networks. Ridge on case24 has median 0.34 (range 0.21–0.48). | **VERIFIED** |
| **E2** case24 ridge failure | `data/netstudy2/summary.json` → `cross_comparisons` | At 0.90, predicted A 0.451 vs measured 0.217. Mean \|rel. err. A\| per cell: case24 ridge **2.111**, case24 histgb 0.194, case39 ridge 0.322, case39 histgb 0.101, illinois200 ridge 0.047, illinois200 histgb 0.061. The overall 0.4726 reproduces. | **VERIFIED** |
| **E3** 3 networks as data points | `data/netstudy2/{case39,case24_ieee_rts,case_illinois200}/frozen.json` → `boundary_mass_pct`, `records` | See E3 notes below this table. | **VERIFIED** (speedup caveat) |
| **E4** case30 speedup | `data/case30_thermal/case30_thermal_frozen.json` → `records` | See E4 notes below this table. | **VERIFIED** (same t_solve caveat) |
| **E5** held-out operating point | `data/tuning_search.json` → `selections`, `records[].inner_cov_at` × `data/tuned_metrics.json` → `records[m2].sweep` | See E5 notes below this table. | **VERIFIED** |
| **E6** classical conformal screen | `data/comparison_curve_v2.json` → `curves.classical_conformal`, `dominance`; `data/classical_screen_metrics.json` → `fit_quality`, `conformalized[0]` | See E6 notes below this table. | **VERIFIED**, with a nuance the review omitted |
| **E7** Mondrian rows | `data/mondrian_element_summary.json` → `aggregate` | See E7 notes below this table. | **VERIFIED** (the review's "32.1" should read 32.0; seed mean 32.05) |
| **E8** certify-only speedup, false flags | `data/flag_confusion_long.parquet` → `certified_frac`, `flag_precision`, `false_flag_rate_of_all` | See E8 notes below this table. | **VERIFIED** |
| **E9** miss depth at operating points | `data/missed_depth.json` → `families.*.pooled`; `data/qlimit_class.json` → `per_operating_point.*.per_seed_depth` | See E9 notes below this table. | **DIFFERENT (minor).** The review said "seed 2"; it is seeds 2 **and 3**. |
| **E10** drift tests | `data/drift_n0_stratum_long.parquet`, `data/drift_element_type_long.parquet`, `data/drift_loading_tilt_long.parquet` | See E10 notes below this table. | **VERIFIED** |
| **E11** break-even | `data/break_even.json` → `break_even_at_operating_points`; `data/parallel_speedup.json` → `best_parallel` | See E11 notes below this table. | **VERIFIED** |

No source file is missing.

**E1: limit sweep.**
- histgb: escalation is **0.26–1.77%** for L = 0.900–0.936; 5.46% at 0.938; 19.44% at 0.939;
  **30.63% at 0.940**; 15.94% at 0.945; **1.58% at 0.950**; 0.68% at 0.920.
- ridge: 1.41% at 0.920; 49.07% at 0.940; 1.38% at 0.950.

**E1: unconditioned build.** Boundary mass **28.83%** and violations 56.04% over 277,628 converged
N-1 rows. 47.49% of unfiltered bases fall below 0.94 at N-0. The committed build is 56.86% / 17.48%.

**E3: three extra networks.** Boundary mass, then histgb escalation and speedup at 0.90:

| Network | Boundary mass | histgb escalation @0.90 | histgb speedup @0.90 |
|---|---|---|---|
| case39 | 4.43% | 3.72% | 27.8 ± 5.1× |
| case24_ieee_rts | 20.70% | 17.19% | 5.85 ± 0.42× |
| case_illinois200 | 19.33% | 7.84% | 12.8 ± 0.8× |

Ridge escalation at 0.90 is 11.86 / 21.68 / 13.74%. **Caveat:** these speedups use case118's
`ms_solver` = 9.14 ms (`frozen.json` → `ms_solver_provenance`: "imported from data/solve_time.json
(case118); NOT re-timed"). Speedup ≈ 1/escalation, so the effect is small, but say so.

**E4: case30 speedup.**
- histgb@0.97: **17.91 ± 3.71×** (escalation 5.84 ± 1.25%, missed 0.76 ± 0.20%).
- histgb@0.96: 21.46 ± 4.51×. histgb@0.90: 38.63 ± 6.21×.
- ridge@0.97: 3.38 ± 0.19×.

**E5: held-out operating point.**
- histgb: inner targets [0.96, 0.97, 0.97, 0.96, 0.96]; missed **1.15 ± 0.27%**, with 4 of 5 splits
  above 1% (1.61, 0.80, 1.03, 1.05, 1.23); escalation 59.3 ± 4.0%; speedup 1.69 ± 0.12×;
  coverage 96.2 ± 0.6%.
- ridge: inner targets [0.97, 0.94, 0.96, 0.92, 0.94]; missed 0.77 ± 0.78% (1 of 5 above 1%:
  2.24); escalation 65.4 ± 8.1%; speedup 1.55 ± 0.22×; coverage 94.1 ± 2.5%.

**E6: classical conformal screen.** At 0.90 it avoids 8.0% of solves (escalation 92.0 ± 0.5%),
missed 1.07 ± 0.22%, speedup 1.09 ± 0.01×. Its MAE is 3.77 ± 0.06 ×10⁻³ and R² is 0.12. Two things
to note:
- **Conformal ridge dominates it at 9 of 9 points; conformal histgb at only 1 of 9.** The classical
  screen's missed rate is near 0 at targets ≥ 0.91 because it escalates about 94%.
- Its MAE matches ridge (3.77 vs 3.75), yet it avoids only 8% of solves. That is a striking point
  for "accuracy does not settle safety".

**E7: Mondrian vs global calibration.**

| Model | Target | Mondrian escalation | Mondrian missed | Global escalation | Global missed |
|---|---|---|---|---|---|
| histgb | 0.94 | 32.0 ± 2.3% | 2.67 ± 0.38% | 46.7 ± 2.8% | 2.48 ± 0.38% |
| histgb | 0.97 | 42.9 ± 1.9% | 1.45 ± 0.30% | 63.7 ± 5.1% | 0.83 ± 0.24% |
| ridge | 0.94 | 49.6 ± 2.9% | 2.02 ± 0.28% | 64.3 ± 2.8% | 0.79 ± 0.21% |
| ridge | 0.97 | 58.9 ± 4.3% | 0.83 ± 0.25% | 73.9 ± 1.0% | 0.03 ± 0.03% |

**At the same target, Mondrian misses more.** Compare at matched *missed* instead:
- Mondrian histgb@0.97 (42.9%, 1.45%) vs global histgb@0.96 (57.0%, 1.36%): 14 points less escalation.
- Mondrian ridge@0.97 (58.9%, 0.83%) vs global ridge@0.94 (64.3%, 0.79%): 5.4 points less, which
  only just passes the std rule (5.4 > 4.3).

**E8: certify-only speedup and false flags.**
- Certify-only speedup, ridge: 1.35 / 1.12 / 1.08 / 1.04 / 1.01 / 1.00× at 0.90 / 0.94 / 0.95 /
  0.96 / 0.97 / 0.98.
- Certify-only speedup, histgb: 2.10 / 1.57 / 1.47 / 1.35 / **1.24** / 1.12×.
- False flags as a share of all contingencies: ridge 11.0 ± 0.9%, histgb 2.5 ± 0.3%. These are
  independent of the target, because the flag rule is p̂ < L.
- Flag precision: ridge 0.561, histgb 0.856.

**E9: miss depth at the operating points.**
- ridge@0.94: 384 pooled misses; maximum depth **0.0324 pu**; p99 0.0152; 84.9% within q̂.
- histgb@0.97: 404 pooled misses; maximum depth **0.0915 pu**; p99 0.0810; 73.8% within q̂. The
  0.8485 pu case is certified in **seeds 2 and 3**.

**E10: drift tests.**
- 2C (N-0 margin): ridge benign→marginal coverage **79.5 ± 1.8%** vs control 88.4 ± 2.7%; histgb
  89.6 ± 0.5% vs 90.3 ± 1.0%. Histgb escalation is 2.8 ± 0.8% on benign→benign and 59.1 ± 2.5% on
  marginal→marginal.
- 2D (element type): histgb line→trafo coverage 87.6 ± 1.0% vs control 89.8 ± 1.0%. The gap of 2.2
  exceeds the std of 1.0. Ridge shows no gap.
- 2E (loading tilt): null (histgb 89.5–89.9% vs 89.8%).

**E11: break-even.**
- ridge@0.94: 786,904 contingencies = **4,231 base-case sweeps**, dataset generation only (2,564 s);
  1,494,968 = 8,037 including training and search (4,871 s).
- histgb@0.97: 772,851 = 4,155 sweeps; 1,473,021 = 7,919 including training and search.
- Context: 10 parallel workers give 5.40×.

---

## Page budget used below

**Your count** is 16 counted pages, leaving 4 free.

**Disagreement to resolve first.** My estimate for the current file, which uses `\setstretch{1.5}`,
was about 18.9 pp (`scratch/page_estimate.py`); about 16.0 pp was the *Word-style* 1.5 estimate. If
your 16 is a real compile of this file, use it. If it came from the 16.0 estimate, there is only
about 1 page free. In that case the net total below only fits together with the review §7 cuts,
listed at the end.

**Unit costs** (at 345 words per page, consistent with 16 pp):
- one sentence (~25 words) ≈ 0.07 pp;
- one table row ≈ 0.03 pp; a new column ≈ 0 pp (if the table stays within the width);
- a new small table (header, 5–6 rows, caption, attribution line) ≈ 0.35 pp;
- a new figure at 0.6 `\textwidth` with caption ≈ 0.45 pp.

---

## Part C — Placements

### E1 — the boundary mass is produced by the N-0 margin (Top-5 #1; C3, C7)

**E1a. Replace one sentence.**
- **Section:** III-A Dataset, end of the clipping paragraph.
- **Replaces:** "This implies that clustering is an inherent characteristic of the network and the
  sampling process."
- **Content:** the pile-up above 0.94 is inherited from the base cases. N-0 cases are accepted only
  at ≥ 0.94, the same value as the N-1 limit, and most outages barely move the minimum voltage:
  77.6% of N-1 rows are within 0.001 pu of their N-0 minimum. Point forward to IV-C.
- **Source note:** the 77.6% has **no JSON key**. It was recomputed from `data/dataset.parquet`
  (`scratch/verify_reviewer_claims.py`), so it needs a small `data/*.json` plus manifest before it
  can be printed. That would be new work in `data/`, not done here.
- **Space:** +0.03 pp. **Running total: 0.03 / 4.**

**E1b. New sentences plus a new table (Table III).**
- **Section:** IV-C "The boundary layer sets a floor on escalation".
- **Goes after:** "Certain buses account for extreme events, with bus 76 being the weakest node…"
  (the last sentence before the Fig. 4 float).
- **Table:** 5 quintile rows with columns N-0 minimum range, boundary mass, violation rate.
- **Sentences:**
  - the unconditioned build (28.83% boundary mass; 56.04% violations; 47.5% of unfiltered bases
    already below 0.94 at N-0);
  - the 2C escalation split (histgb 2.8% on benign bases vs 59.1% on marginal ones; data from E10).
- **Space:** 0.35 + 0.2 = 0.55 pp. **Running total: 0.58.**

**E1c. New figure (limit sweep) plus two sentences.**
- **Section:** IV-C.
- **Goes after:** "The gradient-boosted model's band is only 0.0023 pu wide, but so much of the
  distribution sits just above 0.94…"
- **Figure content:** escalation vs screening limit L (0.900–0.955) for both models at target 0.90,
  with the boundary mass in [L, L+q̂) overlaid and L = 0.940 marked. Values as in Part B.
- **Script:** no existing script draws this. `scripts/sweep_figures.py` makes `data/fig_floor.png`
  (escalation vs boundary mass, coloured by L) from the same parquet. Either add a prose-free
  "escalation vs L" panel there, or write a new course-style script. The existing PNG carries an
  in-image title and annotations, so it is not usable as-is. **Data:** `data/sweep_results_long.parquet`.
  A manifest is required.
- **Also replaces:** "I use 0.94 pu as a conservative choice." (Discussion). The sweep shows 0.94 is
  the escalation *peak*. The follow-on 0.95 sentences ("Only 86 of the 1,500…", "increasing the
  threshold to 0.95 pu leads to…", "In other words, it finds everything hazardous.") can be folded
  into this paragraph.
- **Optional:** one sentence on separate normal vs emergency post-contingency limits. It needs a
  verified citation first; none is in `notes/prior-art.md`, so it is **not checked**.
- **Space:** 0.45 + 0.15 = 0.6 pp (the Discussion replacement is roughly neutral). **Running total: 1.18.**

### E2 — escalation vs ρ·q̂ across networks (Top-5 #2 and #3; C1)

**E2a. New figure.**
- **Section:** IV-D "Cross-network prediction".
- **Goes after:** "Predictor A used the parameter-free form $\rho\cdot\hat{q}$, where $\rho$
  measures how crowded the voltages are just above the limit…"
- **Content:** log-log scatter of measured escalation vs ρ·q̂; 132 points; 5 networks by colour; the
  two models by marker; identity line. r = 0.81 and log-log r = 0.92 go in the caption, with the
  case24-ridge cluster named in the caption rather than the image.
- **Script:** none exists. `data/fig_identity.png` is a within-case118 sweep across L, not this.
  Write a new one. **Data:** `data/netstudy2/cross_2a_points.json`, plus
  `data/netstudy2/summary.json` → `cross_comparisons` for the sealed predictions. Manifest required.
- **Space:** 0.45 pp. **Running total: 1.63.**

**E2b. Replace two sentences.**
- **Replaces:** "I only report the average errors, and these averages are only the final results
  from this cross-network comparison test. This is shown only to suggest that fitting a slope on
  prior networks does not reliably improve predictions on new networks."
- **Content:** the per-cell mean |rel. error| from Part B (the 0.4726 average is carried by case24
  ridge at 2.11), and why: ridge's wide q̂ runs past the 0.005 strip.
- **Space:** +0.1 pp. **Running total: 1.73.**

**E2c. Two sentences that must change with it.**
- "(worse on relative error yet slightly better on absolute error at 0.1056 versus 0.1163)". Fails
  the std rule (number_check §3); keep only "not clearly more accurate".
- "I tested five networks in total, with three of them completing…". Must agree with the network
  count used everywhere else (C1).
- **Space:** 0.

### E3 — the three extra networks as boundary-mass data points (C1)

**E3. New table** (network comparison) **plus one sentence.**
- **Section:** V Discussion.
- **Goes after:** "For case118, 56.86\% fall just above the limit, and 17.48\% fall below it."
- **Rows:** case118, case30 (regenerated), case39, case24_ieee_rts, case_illinois200.
- **Columns:** boundary mass, histgb escalation @0.90, histgb speedup @0.90. Values as in Part B.
- **Footnote:** every speedup uses case118's t_solve.
- **Note:** this table also carries E4 if you choose that option.
- **Space:** 0.35 + 0.07 = 0.42 pp. **Running total: 2.15.**

### E5 — held-out operating point (Top-5 #2; C13)

**E5a. Two new rows in Table II plus two sentences.**
- **Section:** IV-A "Safety comes at high escalation".
- **Goes after:** "The ridge model shows a similar pattern as well, with the average of missed cases
  falling below 1\% at 0.94…"
- **Rows:** labelled "held-out" for ridge and histgb, with escalation / coverage / missed / speedup
  from Part B.
- **Sentences:**
  - state that 0.94 and 0.97 were read from the test sweep, while the held-out choice uses only the
    inner split;
  - give histgb's 1.15 ± 0.27% with 4 of 5 splits above 1%.
- **Space:** 0.06 + 0.15 = 0.21 pp. **Running total: 2.36.**

**E5b. New sentence.**
- **Section:** III-C "One-sided conformal band".
- **Goes after:** "As long as the test cases and calibration cases come from the same type of
  condition…"
- **Content:** the guarantee covers marginal coverage only. The missed rate has no guarantee; on
  violations the band covers only about 60%. P(overshoot > q̂ | violation) = 0.388 / 0.411 at 0.90
  (`data/barrier_height.json` → `summary_at_090.case118.*.p_overshoot_gt_qhat_given_viol_at_090_mean`,
  VERIFIED on 09-23).
- **Space:** 0.07 pp. **Running total: 2.43.**

**E5c. Sentences that must change.**
- **Abstract:** "For the gradient-boosted model, first going just under a 1\% mean missed rate at a
  0.97 coverage target results in…"
- **IV-C:** "An operator that requires a missed rate around 1\% (with error bars still touching the
  1\% threshold) would run the models at a 0.94 or a 0.97 target…"
- **Conclusion:** "To make sure that the missed ratio approaches 1\% on average, almost two-thirds
  of the cases…"
- **Space:** 0.

### E8 — certify-only speedup and false flags (Top-5 #4)

**E8a. New column in Table II** ("Cert.-only speedup", 12 values from Part B).
- **Space:** about 0 pp if Table II stays within the width at `\small`; otherwise drop the Cov.
  column's ± to make room.
- **Running total: 2.43.**

**E8b. Two new sentences.**
- **Section:** III-D "Three-way gate".
- **Goes after:** "The net speedup is close to the inverse of the escalation rate since the surrogate
  is much cheaper than the solve."
- **Content:**
  - define the certify-only speedup (flagged cases still need a solve for severity and remedial
    action);
  - give the false-flag rates (ridge 11.0%, histgb 2.5% of all contingencies, the same at every
    target).
- **Space:** 0.14 pp. **Running total: 2.57.**

### E6 — classical conformal screen (Top-5 #3; C5)

**E6a. New row in Table I** ("classical (conformal)": MAE 3.77 ± 0.06; R² 0.12 ± 0.00; escalation
92.0 ± 0.5; missed 1.07 ± 0.22; speedup 1.09 ± 0.01).
- **Caption change:** "Four-model comparison" becomes five.
- **Space:** 0.03 pp. **Running total: 2.60.**

**E6b. Replace one sentence.**
- **Section:** II Background.
- **Replaces:** "While this indicates which equipment is subject to the most danger when there's an
  equipment failure, it fails to provide a numerical minimum voltage."
- **Content:** the repo's classical linear-sensitivity screen *does* give a minimum voltage (it is
  the new Table I row). State its limitation: PV buses are held fixed, so it cannot see Q-limit
  switching.
- **Space:** +0.03 pp. **Running total: 2.63.**

**E6c. New sentences.**
- **Section:** IV-C, persistence paragraph.
- **Goes after:** "In Table~\ref{tab:models}, the model escalates 99.5\% of cases and is barely
  faster than the solver…"
- **Content:**
  - the classical screen avoids 8% of solves;
  - conformal ridge dominates it at all 9 targets;
  - histgb dominates it at only 1 of 9, because it trades missed rate for throughput. Do **not**
    write "the gate beats the classical screen" for both models.
  - Same MAE as ridge but 8% avoided makes the "accuracy does not settle safety" point.
- **Optional figure** (not counted): `scripts/plot_comparison.py --curve data/comparison_curve_v2.json`.
  The default `data/classical_vs_conformal.png` reads `data/comparison_curve.json` (**v1**); do not
  use it under the M1/M2 rule. The poster version is v2 but in poster format. +0.45 pp if added.
- **Space:** 0.1 pp. **Running total: 2.73.**

### E7 — Mondrian calibration (Top-5 #2)

**E7. New sentences, or 2 rows in Table II.**
- **Section:** IV-C.
- **Goes after:** the new E1c limit-sweep sentences.
- **Content:** per-element (Mondrian) calibration reaches the same missed rate with less escalation.
  Compare at matched *missed*, not matched target (Part B). The floor therefore belongs to a single
  global q̂ at a given boundary density.
- **Citation:** Mondrian conformal needs a bibitem. `vovk2003mondrian` is "verified, NOT inserted"
  (`notes/prior-art.md` §9.6).
- **Space:** 0.15 pp. **Running total: 2.88.**

**E7-linked sentences that must change** (the "must be a floor" claim; Top-5 #2):
- **Intro:** "Finally, I explain why there must be a certain floor for escalation."
- **Theory:** "Since this inequality comes from the gate's mechanisms, it is a structural property
  of this gate." Reframe as an accounting identity whose empirical content is ρ·q̂ (E2).
- **Discussion:** "and second, I also explain why the speedup is capped, which is because most of
  the data is very close to the limit."
- **Discussion:** "This escalation floor is set by how the distribution of the data occurs in
  relation to the 0.94 pu limit." This also contains a banned checker phrase (`escalation floor`).
- **Conclusion:** "The main reason is that most of the cases fall very close to the limit." and
  "What this study contributes here is the reasoning for the existence of such a floor…"
- **Title:** "…Safety and Throughput Limits Set by Boundary Mass". The term is never defined (C12);
  at minimum define it, and retitling is optional.
- **Space:** 0 (rewrites).

### E4 — case30 speedup (C2)

**E4. New clauses in existing sentences.**
- **Abstract:** add the speedup (17.9 ± 3.7×) after "…the gradient-boosted model at 0.97 coverage
  results in a 5.84$\pm$1.25\% escalation."
- **Discussion:** add the same after "The gradient-boosted model with a coverage target of 0.97 gives
  5.84$\pm$1.25\% escalations…".
- **Must change** (C2): "All five splits are under 1\% at 0.97, but not at 0.96…". Use the *same*
  operating-point rule for both networks. Under the mean rule case30 lands at 0.96 (4.86%
  escalation, 21.5×). Under the all-splits rule case118 lands at ridge 0.95 / histgb 0.98. The
  held-out rule (E5) is the most defensible.
- **Space:** 0.05 pp. **Running total: 2.93.**

### E9 — miss depth at the recommended points (C8; Top-5 #4)

**E9a. New sentence.**
- **Section:** IV-B "The faster model is not the safer one".
- **Goes after:** "The worst miss was a case at 0.0915 per unit under the limit, which was a bus that
  fell to 0.8485."
- **Content:** at ridge@0.94 the maximum miss depth is 0.032 pu; at histgb@0.97 the 0.0915 pu case is
  still certified (in 2 of 5 splits).
- **Space:** 0.07 pp. **Running total: 3.00.**

**E9b. Sentences that must change.**
- **IV-B:** "On the IEEE 118-bus system, the more accurate model is not safer at any point in the
  coverage axis…". This passes at matched *target* (number_check §3). At matched *escalation*, the two
  are equal in frequency but differ in depth (C8).
- **Discussion:** "In addition, the worst case, at 0.0915 per unit, represents a case of sudden
  collapse where the generator at that particular worst-case scenario's weakest bus reaches the limit
  of reactive power…" (C11). The data show gen 21 (IEEE bus 54) pinned at its **absorbing** limit,
  Q = Qmin = −194.7 Mvar, while its voltage is 0.106 pu below setpoint; with Q limits off the case
  solves to 0.939 (`data/miss_mechanism.json`, `data/qlims_off_check.json`, VERIFIED on 09-23).
  Describe the label as unresolved until the Q-limit audit (review N2) runs.
- **Discussion:** "…whether or not the grid crashed in the first place, which is called dynamic
  stability." This is static voltage collapse (review PS minor).
- **Space:** +0.05 pp. **Running total: 3.05.**

### E10 — drift tests (Top-5 #3; project research question 1)

**E10. New small table (4 rows) plus two sentences.**
- **Section:** V Discussion.
- **Goes after:** "However, this ratio only exists when the shifted distribution is absolutely
  continuous relative to the calibration distribution, which is not the case for N-2 outages."
- **Rows:** 2C ridge, 2C histgb, 2D histgb, 2E histgb. Each shows shifted vs same-stratum control
  coverage (Part B).
- **Sentences:**
  - 2D (line→transformer) is the closest existing analogue of an event-space change such as N-1→N-2;
  - state that the 2D gap is small.
- **Space:** 0.35 + 0.14 = 0.49 pp. The sentence-only version is 0.2 pp. **Running total: 3.54.**

### E11 — break-even and parallel context (C10; Top-5 #4)

**E11a. New sentence(s).**
- **Section:** IV-C.
- **Goes after:** "…and accept about a 1.6 times speedup instead of the 2 to 3.3 times available at
  0.90."
- **Content:**
  - break-even is about 4,200 base-case sweeps (dataset cost only), or about 8,000 including training
    and search;
  - 10 parallel workers already give 5.4×.
- **Space:** 0.1 pp. **Running total: 3.64.**

**E11b. Sentence that must change.**
- **Intro:** "I add the solver time for escalated cases to the screening gate's total time to reflect
  the true end-to-end cost." It is not end-to-end while data generation, training and search are
  excluded. Qualify it, or point to E11a.
- **Space:** 0.

### The rest — replacements that *save* space

**E14. Rewrite of the physics ablation subsection** (Discussion, `\subsection{Physics-feature
ablation}`; ST-M6, C9).
- **Replaces:** the four paragraphs starting "In the specific ablations, I intentionally left out
  the aggregate loading…" (about 460 words).
- **New content (about 120 words):**
  - F1/F2 give no gain beyond the std, reported on gate metrics as well as MAE. Ridge +F1+F2 has
    MAE +10.82%, yet escalation at 0.94 moves 64.3 → 59.0% with missed 0.79 → 1.00% (within std;
    `data/physics_ablation.json` → `records[].by_target`, VERIFIED on 09-23).
  - F3/F4 are fixed per outaged element (186-row lookups in `data/physics/lodf.parquet` and
    `data/physics/edistance.parquet`), so their null result is guaranteed by the one-hot encoding.
- **Removes:** "Although the total demand is concealed from the model" (false; C9).
- **Space:** about −1.0 pp. **Running total: 2.64.**

**E15. Replace the S_mean definition and result** (III-E Theory).
- **Replaces:** "To summarize the behavior of the gate's mechanism on violations, I define a
  statistic…" through "…(normalized by the calibrated band width)."
- **New content:** P(overshoot > q̂ | violation) = 0.388 / 0.411 and S_p99 = 6.55 / 9.78
  (`data/barrier_height.json` → `summary_at_090.case118.*`).
- **Note:** this overlaps E5b; keep only one of the two.
- **Space:** about −0.05 pp. **Running total: 2.59.**

**E12 / E13** (per-element and per-base-case conditional coverage under global q̂) are **not
placeable**. They need a refit; the values do not exist on disk.

---

## Other sentences the new results force to change

These are not tied to a single E item.

| Search text | Why | Review ref |
|---|---|---|
| "These results allow operators to make an informed decision…" (abstract, last sentence) | Replace with the finding: when the gate pays off (ρ·q̂ / N-0 margin) | Top-5 #5 |
| "My work stands out from these papers in three distinct ways." and "Second, I specifically check for only under-voltage issues." | The contribution list changes after E1/E2; a scope restriction is not a contribution | Top-5 #5, novelty §5 |
| "Some base cases are also missing a generator before the contingency, so those rows have two elements out…" vs "These are still N-1 contingencies…" | Make the two consistent | C6 |
| "(where coverage is the acceptance rate)" | Second meaning of "coverage"; rename one of them | C4 |
| "so its ceiling lands just above the saturation point" | Fails the std rule (0.16 gap vs 0.37 std); say "at" | number_check §3 |
| "Calibrated uncertainty, as well as making the decision… are proven methods." | Checker's banned phrase "prove" | number_check §6 |
| "Future work involves examining multi-element outages and more networks…" | More networks were already run (E2/E3) | C1 |
| "…holds 56.9\% of all cases…" (Fig. 4 caption) | Use 56.86 as in the text | number_check §4 |
| "…reach up to about 1.0--1.07\%…" | The value is 1.08 | number_check §1 |

---

## Totals

| | pp |
|---|---|
| Additions E1–E11 (core, no optional figure) | **+3.64** |
| Optional classical figure (E6c) | +0.45 |
| Savings E14 + E15 | −1.05 |
| **Net, core** | **+2.59 of 4 free** (≈ 1.4 pp to spare) |
| Net with the optional figure | +3.04 |

**If only about 1 page is actually free** (see the page-budget note), add these review §7 cuts:

| Cut | Saves |
|---|---|
| Reject-option digression, "While the methodology of this research is similar to classical reject-option results…" through "…not the underlying theorem." | 0.4 pp |
| Fig. 5 critical-bus map; keep one sentence | 0.5 pp |
| Ceiling paragraph from "As the band becomes larger…" | 0.3 pp |
| case57 / case89pegase detail, "I also dropped two networks…" through "…so the case was left out." | 0.3 pp |
| Shrink Fig. 3 to 0.45 `\textwidth` | 0.25 pp |

Those cuts total about 1.75 pp, which brings the net to about +0.85 pp.

**If space is short, drop in this order:** the E10 table (keep sentences, −0.29), the E3 table
(fold into the E2 caption, −0.35), then the optional E6 figure.

**Every new figure needs a manifest** (project rule), including the hyperparameters behind it.
