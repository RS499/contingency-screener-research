# writing-numbers.md

Every value the manuscript may use, with its provenance. Read numbers from here; never
retype one from prose.

**Written:** 2026-08-19. **Git HEAD at verification:** `69eeb80a34c9815194d6ead556ab26e86bfc249d`.

## Rules this file follows

- Every row was read from an artifact **in this session**. Nothing is carried from memory,
  from a planning document, or from a chat transcript.
- `notes/writing-background.md` and `notes/section-V-writing-context.md` were **not read**.
  Both are absent from the repository.
- Where an aggregation choice exists, **both** are given and the one the manuscript's existing
  tables use is named.
- Values that cannot be computed from stored data say **CANNOT BE COMPUTED** and why.
- Values with no artifact say **NO SOURCE**.

## THERE ARE NOW THREE RESULT SETS

Every row below names its network. The two case30 sets are **not interchangeable**:

| set | dataset | N-0 criterion | thermally feasible? |
|---|---|---|---|
| **case118** | `data/dataset.parquet` | voltage only (`n0_min_vm >= 0.94`) | UNDEFINED — ratings are 9,900 MVA placeholders |
| **case30-published** | `data/case30_dataset.parquet` | voltage only | **NO** — base case at 111.83% loading; 100% of sampled N-1 above 100% |
| **case30-thermal** | `data/case30_thermal/dataset.parquet` | voltage **and** `max loading_percent <= 100` | **YES** at N-0; 21.48% of N-1 still above 100% |

A row that says only "case30" is ambiguous and must not be used.

---

## Provenance table

| quantity | value | source file | jsonpath/column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| case118 total rows | `280500` | `data/dataset.parquet` | parquet metadata num_rows | raw | `8f0fd1081c8603e8` |
| case118 base scenarios | `1500` | `data/dataset.parquet` | outaged_type=='none' | count | `8f0fd1081c8603e8` |
| case118 N-1 attempted | `279000` | `data/dataset.parquet` | outaged_type!='none' | count | `8f0fd1081c8603e8` |
| case118 N-1 converged | `278955` | `data/dataset.parquet` | outaged_type!='none' & converged | count | `8f0fd1081c8603e8` |
| case118 non-converged | `45` | `data/dataset.parquet` | ~converged | count | `8f0fd1081c8603e8` |
| case118 violation rate | `0.174756` | `data/dataset.parquet` | min_vm<0.94 over N-1 converged | raw | `8f0fd1081c8603e8` |
| case118 boundary mass | `0.568629` | `data/dataset.parquet` | 0.94<=min_vm<0.945 | raw | `8f0fd1081c8603e8` |
| case118 N-1 share max_vm>1.05 | `0.731358` | `data/dataset.parquet` | max_vm>1.05 | raw | `8f0fd1081c8603e8` |
| case118 N-0 share max_vm>1.05 | `0.734` | `data/dataset.parquet` | max_vm>1.05 | raw | `8f0fd1081c8603e8` |
| case118 gen-outage share of N-1 | `0.249259` | `data/dataset.parquet` | gen_out>=0 | raw | `8f0fd1081c8603e8` |
| sweep total evaluations | `16800` | `data/sweep_results_long.parquet` | parquet metadata num_rows | row count NOT a prose product | `3783d41c1b6e14d5` |
| flag precision ridge@0.94 count-pooled | `0.56062` | `data/flag_confusion_long.parquet` | sum(flag_viol)/sum(flag_viol+flag_safe) | count-pooled | `2ef84483e67518da` |
| flag precision ridge@0.94 seed-mean | `0.561265` | `data/flag_confusion_long.parquet` | flag_precision | seed-mean | `2ef84483e67518da` |
| flag ceiling ridge | `0.691482` | `data/flag_confusion_long.parquet` | P(Y<L)/P(pred<L) | count-pooled | `2ef84483e67518da` |
| flag precision histgb@0.97 count-pooled | `0.856295` | `data/flag_confusion_long.parquet` | sum(flag_viol)/sum(flag_viol+flag_safe) | count-pooled | `2ef84483e67518da` |
| flag precision histgb@0.97 seed-mean | `0.856372` | `data/flag_confusion_long.parquet` | flag_precision | seed-mean | `2ef84483e67518da` |
| flag ceiling histgb | `1.009272` | `data/flag_confusion_long.parquet` | P(Y<L)/P(pred<L) | count-pooled | `2ef84483e67518da` |
| case30-published violation rate | `0.288081` | `data/case30_frozen.json` | violation_rate_pct | raw | `d501f99671b40a78` |
| case30-published boundary mass | `0.20014600000000002` | `data/case30_frozen.json` | boundary_mass_pct | raw | `d501f99671b40a78` |
| case30-thermal violation rate | `0.153967` | `data/case30_thermal/case30_thermal_frozen.json` | violation_rate_pct | raw | `b340af22662fdd29` |
| case30-thermal boundary mass | `0.070862` | `data/case30_thermal/case30_thermal_frozen.json` | boundary_mass_pct | raw | `b340af22662fdd29` |
| case30-published ridge crossing target | `0.92` | `data/case30_frozen.json` | crossings.ridge.coverage_target | seed-mean | `d501f99671b40a78` |
| case30-published ridge crossing escalation | `0.344829` | `data/case30_frozen.json` | crossings.ridge.escalation | seed-mean | `d501f99671b40a78` |
| case30-published ridge crossing speedup | `2.985` | `data/case30_frozen.json` | crossings.ridge.net_speedup | seed-mean | `d501f99671b40a78` |
| case30-published ridge esc@0.90 | `0.278748` | `data/case30_frozen.json` | four_metrics.ridge.escalation_mean | seed-mean | `d501f99671b40a78` |
| case30-published ridge speedup@0.90 | `3.6562` | `data/case30_frozen.json` | four_metrics.ridge.net_speedup_mean | seed-mean | `d501f99671b40a78` |
| case30-published ridge missed@0.90 | `0.014931` | `data/case30_frozen.json` | four_metrics.ridge.missed_viol_mean | seed-mean | `d501f99671b40a78` |
| case30-thermal ridge crossing target | `0.98` | `data/case30_thermal/case30_thermal_frozen.json` | crossings.ridge.coverage_target | seed-mean | `b340af22662fdd29` |
| case30-thermal ridge crossing escalation | `0.378341` | `data/case30_thermal/case30_thermal_frozen.json` | crossings.ridge.escalation | seed-mean | `b340af22662fdd29` |
| case30-thermal ridge crossing speedup | `2.6489` | `data/case30_thermal/case30_thermal_frozen.json` | crossings.ridge.net_speedup | seed-mean | `b340af22662fdd29` |
| case30-thermal ridge esc@0.90 | `0.119187` | `data/case30_thermal/case30_thermal_frozen.json` | four_metrics.ridge.escalation_mean | seed-mean | `b340af22662fdd29` |
| case30-thermal ridge speedup@0.90 | `8.4493` | `data/case30_thermal/case30_thermal_frozen.json` | four_metrics.ridge.net_speedup_mean | seed-mean | `b340af22662fdd29` |
| case30-thermal ridge missed@0.90 | `0.060873` | `data/case30_thermal/case30_thermal_frozen.json` | four_metrics.ridge.missed_viol_mean | seed-mean | `b340af22662fdd29` |
| case30-published histgb crossing target | `0.93` | `data/case30_frozen.json` | crossings.histgb.coverage_target | seed-mean | `d501f99671b40a78` |
| case30-published histgb crossing escalation | `0.089593` | `data/case30_frozen.json` | crossings.histgb.escalation | seed-mean | `d501f99671b40a78` |
| case30-published histgb crossing speedup | `11.2653` | `data/case30_frozen.json` | crossings.histgb.net_speedup | seed-mean | `d501f99671b40a78` |
| case30-published histgb esc@0.90 | `0.069821` | `data/case30_frozen.json` | four_metrics.histgb.escalation_mean | seed-mean | `d501f99671b40a78` |
| case30-published histgb speedup@0.90 | `14.5218` | `data/case30_frozen.json` | four_metrics.histgb.net_speedup_mean | seed-mean | `d501f99671b40a78` |
| case30-published histgb missed@0.90 | `0.014664` | `data/case30_frozen.json` | four_metrics.histgb.missed_viol_mean | seed-mean | `d501f99671b40a78` |
| case30-thermal histgb crossing target | `0.96` | `data/case30_thermal/case30_thermal_frozen.json` | crossings.histgb.coverage_target | seed-mean | `b340af22662fdd29` |
| case30-thermal histgb crossing escalation | `0.048618` | `data/case30_thermal/case30_thermal_frozen.json` | crossings.histgb.escalation | seed-mean | `b340af22662fdd29` |
| case30-thermal histgb crossing speedup | `21.4571` | `data/case30_thermal/case30_thermal_frozen.json` | crossings.histgb.net_speedup | seed-mean | `b340af22662fdd29` |
| case30-thermal histgb esc@0.90 | `0.026537` | `data/case30_thermal/case30_thermal_frozen.json` | four_metrics.histgb.escalation_mean | seed-mean | `b340af22662fdd29` |
| case30-thermal histgb speedup@0.90 | `38.6263` | `data/case30_thermal/case30_thermal_frozen.json` | four_metrics.histgb.net_speedup_mean | seed-mean | `b340af22662fdd29` |
| case30-thermal histgb missed@0.90 | `0.022255` | `data/case30_thermal/case30_thermal_frozen.json` | four_metrics.histgb.missed_viol_mean | seed-mean | `b340af22662fdd29` |
| H2 lo values with ZERO acceptance | `0.94..1.0 (7 values)` | `data/case30_thermal/h2_range_sweep.json` | h2.sweep acceptance_rate==0 | raw | `dd98d69da1be1937` |
| H2 chosen range | `[0.87, 0.99]` | `data/case30_thermal/h2_range_sweep.json` | h2.chosen | raw | `dd98d69da1be1937` |
| H2 chosen acceptance | `0.205` | `data/case30_thermal/h2_range_sweep.json` | h2.chosen.acceptance_rate | raw | `dd98d69da1be1937` |
| H3 build acceptance | `0.186335` | `data/case30_thermal/h3_build_stats.json` | acceptance_rate | raw | `f2d3717c163ff964` |
| case30-thermal N-1 loading >100% | `0.214846` | `data/case30_thermal/h3_build_stats.json` | n1_loading.share_above_100 | raw | `f2d3717c163ff964` |
| case30-published N-1 loading >100% | `1.0` | `data/thermal_check.json` | networks.case30.thermal_sweep | SAMPLE 120/1500 bases | `23d42c7146e0f580` |
| 2C shortfall histgb benign->benign | `0.00891` | `data/drift_n0_stratum_long.parquet` | mean(target-coverage_emp) | seed+target mean | `97c8ef7aa40c4e97` |
| 2C shortfall histgb benign->marginal | `0.017613` | `data/drift_n0_stratum_long.parquet` | mean(target-coverage_emp) | seed+target mean | `97c8ef7aa40c4e97` |
| 2C shortfall histgb marginal->benign | `-0.011827` | `data/drift_n0_stratum_long.parquet` | mean(target-coverage_emp) | seed+target mean | `97c8ef7aa40c4e97` |
| 2C shortfall histgb marginal->marginal | `-0.00776` | `data/drift_n0_stratum_long.parquet` | mean(target-coverage_emp) | seed+target mean | `97c8ef7aa40c4e97` |
| 2C shortfall ridge benign->benign | `0.008282` | `data/drift_n0_stratum_long.parquet` | mean(target-coverage_emp) | seed+target mean | `97c8ef7aa40c4e97` |
| 2C shortfall ridge benign->marginal | `0.164335` | `data/drift_n0_stratum_long.parquet` | mean(target-coverage_emp) | seed+target mean | `97c8ef7aa40c4e97` |
| 2C shortfall ridge marginal->benign | `-0.068568` | `data/drift_n0_stratum_long.parquet` | mean(target-coverage_emp) | seed+target mean | `97c8ef7aa40c4e97` |
| 2C shortfall ridge marginal->marginal | `0.010189` | `data/drift_n0_stratum_long.parquet` | mean(target-coverage_emp) | seed+target mean | `97c8ef7aa40c4e97` |
| 2D shortfall histgb line->line | `-0.001425` | `data/drift_element_type_long.parquet` | mean(target-coverage_emp) | seed+target mean | `58bd35de57f96c58` |
| 2D shortfall histgb line->trafo | `0.02281` | `data/drift_element_type_long.parquet` | mean(target-coverage_emp) | seed+target mean | `58bd35de57f96c58` |
| 2D shortfall histgb trafo->line | `-0.022445` | `data/drift_element_type_long.parquet` | mean(target-coverage_emp) | seed+target mean | `58bd35de57f96c58` |
| 2D shortfall histgb trafo->trafo | `0.001512` | `data/drift_element_type_long.parquet` | mean(target-coverage_emp) | seed+target mean | `58bd35de57f96c58` |
| 2D shortfall ridge line->line | `0.005931` | `data/drift_element_type_long.parquet` | mean(target-coverage_emp) | seed+target mean | `58bd35de57f96c58` |
| 2D shortfall ridge line->trafo | `0.003776` | `data/drift_element_type_long.parquet` | mean(target-coverage_emp) | seed+target mean | `58bd35de57f96c58` |
| 2D shortfall ridge trafo->line | `0.00716` | `data/drift_element_type_long.parquet` | mean(target-coverage_emp) | seed+target mean | `58bd35de57f96c58` |
| 2D shortfall ridge trafo->trafo | `0.005035` | `data/drift_element_type_long.parquet` | mean(target-coverage_emp) | seed+target mean | `58bd35de57f96c58` |
| 2E shortfall histgb tilted_test_unweighted_cal | `0.000624` | `data/drift_loading_tilt_long.parquet` | mean(target-coverage_emp) | seed+target mean | `3c744f658e5a3973` |
| 2E shortfall histgb tilted_test_weighted_cal | `-0.002061` | `data/drift_loading_tilt_long.parquet` | mean(target-coverage_emp) | seed+target mean | `3c744f658e5a3973` |
| 2E shortfall histgb untilted_test_unweighted_cal | `-0.00121` | `data/drift_loading_tilt_long.parquet` | mean(target-coverage_emp) | seed+target mean | `3c744f658e5a3973` |
| 2E shortfall ridge tilted_test_unweighted_cal | `0.004624` | `data/drift_loading_tilt_long.parquet` | mean(target-coverage_emp) | seed+target mean | `3c744f658e5a3973` |
| 2E shortfall ridge tilted_test_weighted_cal | `0.003816` | `data/drift_loading_tilt_long.parquet` | mean(target-coverage_emp) | seed+target mean | `3c744f658e5a3973` |
| 2E shortfall ridge untilted_test_unweighted_cal | `0.005857` | `data/drift_loading_tilt_long.parquet` | mean(target-coverage_emp) | seed+target mean | `3c744f658e5a3973` |
| 2F baseline off-setpoint gens mean | `20.7993` | `data/qlimit_class.json` | baseline.offsetpoint_gens_mean | raw | `3c0149754f0eefdb` |
| 2F ridge deep misses | `58` | `data/qlimit_class.json` | per_operating_point.ridge.n_deep_total | 5-seed total | `3c0149754f0eefdb` |
| 2F ridge distinct elements | `32` | `data/qlimit_class.json` | ...n_distinct_elements | 5-seed | `3c0149754f0eefdb` |
| 2F ridge max miss depth | `0.032426` | `data/qlimit_class.json` | ...max_depth | 5-seed max | `3c0149754f0eefdb` |
| 2F histgb deep misses | `106` | `data/qlimit_class.json` | per_operating_point.histgb.n_deep_total | 5-seed total | `3c0149754f0eefdb` |
| 2F histgb distinct elements | `54` | `data/qlimit_class.json` | ...n_distinct_elements | 5-seed | `3c0149754f0eefdb` |
| 2F histgb max miss depth | `0.091457` | `data/qlimit_class.json` | ...max_depth | 5-seed max | `3c0149754f0eefdb` |

rows: 80   git HEAD: 69eeb80a34c9815194d6ead556ab26e86bfc249d   date verified: 2026-08-19

---

## Aggregation notes

- **Manuscript Tables I and II use seed-mean with population std (ddof=0) over five splits**
  (`data/tradeoff_curve_v2.json` `std_convention`). Where this file gives a count-pooled
  figure, it is labelled, and it is **not** what the existing tables use.
- Flag precision: seed-mean and count-pooled agree to ~3 decimals here only because per-seed
  test sizes are near-identical (55,789–55,792). They are different estimators.
- 2C/2D/2E shortfalls are means over 5 seeds **and** 30 coverage targets. A single-target
  figure is a different quantity.
- 2F counts are 5-seed totals, not per-seed.

## CANNOT BE COMPUTED

| quantity | why |
|---|---|
| pooled percentiles of false-flag margins | `flag_confusion_long.parquet` stores per-seed `ff_margin_p50/p90/max` only; raw margins are not retained. A mean of five percentiles is not a pooled percentile. |
| case118 thermal violation rate | ratings are uniform 9,900 MVA placeholders; the quantity is UNDEFINED, not zero |
| thermal/voltage violation-set overlap | UNDEFINED on case118; degenerate on case30 (thermal share = 1.0 as published) |
| rejection rate by generator-outage status | rejected draws are not recorded in the dataset |
| whether 2D bounds N-2 expectations | the event space changes; no likelihood ratio exists |
| a loading shift large enough to stress weighted conformal | the sampler's `agg_loading` window is 7.7 points wide (1.019–1.096) |
| full case30-published thermal sweep | ~87 min projected; only a 120-of-1500 prefix sample exists |

## NO SOURCE

| quantity | note |
|---|---|
| "around 14%" bin share (manuscript line 235) | no artifact located anywhere in `data/` |
| flag precision 1.0000 / 0.99981 / 21 false flags / 111,000 | came from a `new_sections.tex` that existed 2026-08-15 and is now deleted; no artifact ever produced them |
| 2C circulating values 87.7 / 87.1 / 92.4 / 92.1 and 0.0159 pu | measured instead: 79.53 / 88.44 / 90.22 / 89.64 and 0.00486 pu |
| home ZIP code for the PDF filename | not in this repository; must not be guessed |

## Values in the manuscript with NO artifact behind them

- Line 235, "no 0.001-per-unit width bin makes up more than around 14%" — **NO SOURCE**.

## Values appearing in more than one artifact with DIFFERENT values

| quantity | artifact A | artifact B |
|---|---|---|
| first coverage target with missed < 1% | `frozen_poster_numbers.json` (M1): ridge 0.95, histgb 0.96 | `frozen_poster_numbers_v2.json` (M2): ridge 0.94, histgb 0.97 |
| case30 violation rate | `case30_frozen.json`: 28.8081% | `case30_thermal/case30_thermal_frozen.json`: 15.3967% |
| case30 boundary mass | `case30_frozen.json`: 20.0146% | `case30_thermal/...`: 7.0862% |
| case30 N-1 loading > 100% | `thermal_check.json`: 1.000000 (sample) | `h3_build_stats.json`: 0.214846 (full, thermal set) |

The M1/M2 pair is resolved by `data/canonical.json` (`authoritative: M2`) and `CLAUDE.md` §8.
The case30 pairs are **not a contradiction** — they are two different result sets, and every
row must name which.

## Section III-A corrections, as coded

From `data/sampling_audit.json` (three independent routes: AST parse, artifact variance,
committed invocation):

- **TOUCHED by the 1.0–1.12 multiplier:** `net.load.p_mw` (`p_new = _p0 * mp`);
  `net.load.q_mvar` (`q_new = _q0 * mp * pf`, so also an independent power-factor draw
  `U(0.9, 1.15)`).
- **NOT touched:** `net.gen.p_mw` — **never assigned anywhere in `apply_scenario`**
  (AST) and empirically constant (`nunique`=1, `std`=0). The slack bus absorbs the entire
  load increase. Also not touched by the multiplier: `net.gen.vm_pu` (independent ±0.025
  jitter), `net.gen.min_q_mvar`/`max_q_mvar` (independent `U(0.60, 1.40)`),
  `net.gen.in_service` (independent `P_GEN_OUT = 0.30` draw).
- Committed invocation is `README.md:94-95`, **not** `case57_gonogo.py:COMMITTED_CFG`.
  `--dvm 0.025`, not the module default `DVM = 0.03`.

## The flag branch

Flag membership is **invariant to the coverage target**. Deciding line:

```
feasibility/gate_eval.py:19        flag = pred < limit
```

`q_hat` appears only at line 18 (`lower = pred - q_hat`), which feeds `certify` and hence
`escalate`. The flag test never sees it. Verified: `nunique` = 1 for `flag_safe`, `flag_viol`,
`flag_precision`, `flag_recall` in all 10 (model, seed) groups across 30 targets.

## Non-convergence

1,545 = **1,500** N-0 base rows (all converged, excluded because they are base cases) +
**45** genuine solver failures. All 45 are transformer outages on 3 elements (trafo 0/7/6 →
IEEE 1/8/7), 37/7/1. Gate disposition: 0/45 certified for ridge@0.94; 1 of 225 seed-rows for
histgb@0.97. Missed-rate delta from counting all 45 as violations: **0.0000 at four decimals**,
and negative for ridge.

## The `run_scenario` state-carryover bug (found mid-H2)

**`feasibility/generate_dataset.py:210-216`.** `run_scenario` toggles `in_service` and calls
`solve(net)` on the **current** net state; it does **not** re-apply `params`. The committed
`worker()` (`:252-262`) calls it immediately after `solve_n0`, so the net is correct there.
Any caller that defers `run_scenario` until after a draw loop measures contingencies against
the **last drawn** scenario — usually a rejected one.

This is not a defect in the committed pipeline; it is a **latent precondition** on
`run_scenario` that is undocumented. It bit the H2 probe, producing violation rates of exactly
1.0 next to neighbours at 0.12. Fixed by re-applying via `G.solve_n0(net, params)` before each
probe. Acceptance, loading and voltage columns were computed inside the draw loop and were
never affected.

## Does the barrier-height inequality predict the case30-thermal model-ordering reversal?

**Reported, not resolved.**

The barrier-height argument: a violation is missed only when `p_hat >= L + q_hat` while
`Y < L`, so the overshoot must exceed `q_hat + d`. At fixed coverage `q_hat` is set by each
model's error scale, so the *less* accurate model buys a *taller* barrier and should miss
less. On **case118** this holds: ridge (MAE 3.8e-3, `q_hat` 0.0052) has the lower missed rate
at every target than histgb (MAE 1.6e-3, `q_hat` 0.0023).

On **case30-thermal** the ordering **reverses**: histgb has both the lower missed rate at 0.90
(**2.226%** vs ridge **6.087%**) and the earlier sub-1% crossing (**0.96** vs **0.98**).

Two readings, both consistent with the artifacts:

1. **The inequality does not predict it.** The argument fixes coverage and compares `q_hat`
   across models, so a taller barrier should still mean fewer misses. On case30-thermal
   ridge's `q_hat` at 0.90 is ~0.0065–0.0077 against histgb's ~0.0020–0.0027 (from the H3b
   calibration log) — ridge's barrier is still ~3x taller, yet ridge misses **more**. On the
   face of it the inequality is contradicted.
2. **The inequality is not violated, its premise is.** The barrier bounds misses only relative
   to the *overshoot distribution*. Ridge's accuracy collapses more on the thermal-feasible
   set (its 2C behaviour already shows its calibration failing inside the boundary layer), so
   its overshoot tail can grow faster than its barrier. The inequality is about one model's
   own residuals, not a cross-model ordering — reading it as a cross-model law may be the
   error.

**Which reading is correct is not settled by the artifacts in this repository.** Deciding it
requires comparing each model's overshoot tail against its own `q_hat` on case30-thermal,
which is a further experiment and was not run. Recorded for the author's decision.

---

## Verifier findings against this table

An independent `verifier` subagent, which had not seen the work that produced this file,
checked **every one of the 80 rows** on 2026-08-19: value against the named artifact, and
sha256(16) against the named file.

**Result: 80/80 value MATCH, 80/80 sha MATCH. No row was wrong.**

It raised five points that change no value but would mislead a later reader if left
unrecorded. Read the table with these in mind:

1. **Rows 18-21 state a fraction under a `_pct` jsonpath.** The artifacts store
   `violation_rate_pct` = 28.8081 / 20.0146 / 15.3967 / 7.0862; this table states the
   corresponding fractions. The conversion is correct and consistently applied, but the
   jsonpath as written does not literally yield the stated value — divide by 100.

2. **jsonpaths are abbreviated.** `crossings.*` means
   `crossings_first_below_1pct_missed.*`; `four_metrics.*` means
   `four_metrics_at_90pct_coverage.*`; `baseline.offsetpoint_gens_mean` means
   `baseline_all_n1_rows.offsetpoint_gens_mean`.

3. **Rows 22-45 are labelled "seed-mean" but hold stored scalars.** The label records how the
   value was originally produced, not an aggregation a reader can redo from that file. Only
   `case30_thermal_frozen.json` carries a `records` array permitting per-seed re-derivation;
   `case30_frozen.json` does not.

4. **Rows 6-10 carry an implicit `converged` restriction.** The condition column reads bare
   (`max_vm>1.05`, `gen_out>=0`) but the values are over converged N-1 rows. Over all
   attempted N-1 rows including the 45 failures the values would be **0.731240** and
   **0.249333**, not 0.731358 and 0.249259.

5. **Rows 76 and 79 cannot be recomputed from their artifact alone.**
   `data/qlimit_class.json` truncates `deep_elements` to the top 10 entries (31 and 43
   occurrences of the 58 and 106 deep misses), so the stored `n_distinct_elements` scalars
   32 and 54 were verified as stored values, not re-derived from the list.

## Known reporting-column defects in the 2E artifact

Both affect only descriptive columns. Coverage, escalation, missed and speedup are unaffected
in every cell — independently confirmed by reproducing all six 2E shortfalls to 6 dp.

- **`realized_mean_agg_test`** (`scripts/drift_tests.py:237`) applies the tilted bootstrap
  index to all three cells, so the untilted control row reports the tilted test mean. Correct
  untilted per-seed means: 1.059097, 1.058946, 1.058411, 1.059368, 1.059807. Tilted:
  1.063707, 1.064138, 1.063808, 1.064081, 1.064363.
- **`realized_mean_agg_cal`** (same statement) is unweighted for all three cells, so the
  weighted cell reports the unweighted calibration mean and hides the effect of `w_cal`.
  Values: 1.058861, 1.059059, 1.059392, 1.059325, 1.058282.

**Do not quote either column as evidence that the tilt moved the loading distribution.** Use
the per-seed values above.

## CAVEAT on row 51 (case30-published N-1 loading > 100%)

`scripts/thermal_check.py:159-160` reconstructs the operating point by assigning **per-bus**
`pload_i`/`qload_i` features positionally to `net.load` rows, whose `bus` column is not
`0..n_load-1`. On case30 all 20 of 20 loads receive the wrong bus's demand (total 154.48 MW
assigned against 203.95 MW correct). See CORRECTION C-4.

**Row 51's value (`share_above_100` = 1.000000) survives** — a paired as-coded vs bus-mapped
replay gives 1.0000 both ways. But the median (154.72), p90 (192.48) and max (490.45) stored
alongside it in `data/thermal_check.json` are **WRONG and must not be quoted**.

The case30-**thermal** loading figures (row 50 and the median/max in
`data/case30_thermal/h3_build_stats.json`) come from `G.solve_n0` -> `apply_scenario`, a
different and correct path, and are unaffected.

## CAVEAT on rows 40-42 (case30-thermal histgb crossing)

`crossings_first_below_1pct_missed.histgb.missed_viol = 0.009094` sits within a whisker of the
0.01 threshold that defines the crossing, and the artifact stores **no std** beside it.
Whether the crossing is at 0.96 or 0.97 is **not decidable from the stored scalar**. Per-seed
values are recoverable from `records[]` in the same file. Quote 0.96 only with this caveat.
See CORRECTION C-11.

## CAVEAT on rows 74-80 (2F)

The deep-miss pools (n=58 ridge, n=106 histgb) are unions over 5 test splits drawn from the
same 1,500 scenarios and therefore **overlap**; they are not independent observations.
Concentration shares computed off them (e.g. `top_bus_share` = 6 of 58) **overstate**
concentration. None of the 2F conclusion-bearing scalars carries a std or a per-seed
breakdown, so the baseline-vs-deep-miss comparison (20.799 vs 21.328 off-setpoint generators)
is **unevaluable under the project's std rule**. See CORRECTION C-10.

## CAVEAT UPDATE on rows 40-45 (case30-thermal crossings) — S6 adjudication

An independent re-derivation anchored bit-exact against `data/case30_frozen.json` (max abs
diff 0.0 over 16 entries) established that **both stored crossing locations are
INDETERMINATE at 5 seeds**:

- **histgb 0.96**: mean missed_viol 0.00909353, std 0.00219629 — separated from the 0.01
  threshold by only **0.41 std**, with **2 of 5 seeds** individually below 0.01. The first
  decidable target is **0.97** (gap 1.20 std, 5/5 seeds below).
- **ridge 0.98**: decidable as a value (2.35 std), but the exclusion of 0.97 rests on a
  **0.22 std** excess, so the location could equally be 0.97.

Headline consequences for histgb: at 0.96, escalation 4.86% ± 0.98 and speedup 21.46x ± 4.51;
at 0.97, escalation **5.84% ± 1.25** and speedup **17.91x ± 3.71**.

Do not quote a crossing target as resolved. Quote the pair, or quote the metric at a fixed
coverage target instead.

## CORRECTION to the row-51 caveat above (S7 adjudication)

The caveat above states "a paired as-coded vs bus-mapped replay gives 1.0000 both ways."
**That is wrong at four decimals.** An independent bus-mapped replay of the SAME 120-scenario
prefix gives **0.999797** (4919/4920) — one contingency lands at 99.61% loading. The mapping
was validated first by reproducing stored `min_vm` to 6.8e-08 across all 4,920 contingencies.

Consistent values by route, all correct for their population:

| route | share above 100% |
|---|---|
| stored artifact (as-coded, 120 prefix) | 1.000000 |
| bus-mapped, same 120 prefix | **0.999797** |
| bus-mapped, a different random 120 sample | 1.000000 |
| bus-mapped, full 61,500 | **0.9989105691** |

The full population has 67 contingencies at or below 100%. **Do not write "100%" without a
qualifier.** The corrected quantiles are confirmed: 122.66 / 135.70 / 195.61 against the void
154.7238 / 192.4818 / 490.4466.

## THREE FURTHER LABEL DEFECTS (S7)

1. **The `converged` filter is load-bearing and unstated in the condition column.** Recomputing
   the literal condition without it: case30-published violation rate 28.8081% -> **28.1222%**;
   case30-thermal 15.3967% -> **15.0302%**.
2. **Row 7's denominator.** Boundary mass 0.568629 is the share of ALL converged N-1 rows in
   [0.94, 0.945). The share of NON-VIOLATING rows in that strip is **0.689044**.
3. **Flag ceiling aggregation.** count-pooled 0.691482 vs seed-mean **0.692415**. And the 2C
   shortfall is 0.164335 over 30 targets but **0.104702 at the 0.90 target alone**.

---

## ROW 51 SUPERSEDED — corrected full-population values now in the artifact (Task 1)

`scripts/thermal_check.py:159-160` is FIXED (bus-mapped indexing) and
`data/thermal_check.json` re-emitted as a **FULL SWEEP: 1,500 scenarios, 61,500 contingencies,
0 failures**. Acceptance test `scripts/thermal_selftest.py` passes both directions —
bus-mapped reproduces stored `min_vm` to **6.14e-08**, positional to only **2.92e-01**.

Use these; the earlier prefix-sample values are void:

| quantity | value |
|---|---|
| case30-published, share of N-1 above 100% loading | **0.9989105691056911** |
| share above 95% | **0.9999837398373984** |
| median max-line loading | **122.56098152254225** |
| p90 | **136.44159869188255** |
| max | **217.54822673764184** |

Two-key: all four match the S1 adjudication agent's fully independent full-population
derivation to 1e-6. **Do not write "100%"** — 67 of 61,500 contingencies are at or below 100%.

Unchanged by the fix: case30 N-0 base max line loading 111.83140586617333; both case118
PLACEHOLDER verdicts; all over-voltage figures.

## BARRIER HEIGHT — RESOLVED (Task 2)

`data/barrier_height.json`, `data/barrier_height_long.parquet`. Pre-registered before running.

**The inequality holds within every model, everywhere, exactly** — share of misses satisfying
`overshoot >= q_hat + depth` is **1.000000** across all 173 rows containing a miss, and
`|P(o > q_hat) − (1 − coverage)| = 5.551e-17`. Both are algebraic consequences of the gate, so
they confirm the computation, not the theory.

**The reversal is explained by `S_mean = E[overshoot | Y < L] / q_hat`, at coverage 0.90:**

| network | model | q_hat | missed | S_mean |
|---|---|---|---|---|
| case118 | ridge | 0.005198 | 2.963% | **0.6038 ± 0.0757** |
| case118 | histgb | 0.002291 | 4.717% | **0.7919 ± 0.0743** |
| case30-thermal | ridge | 0.006974 | 6.087% | **0.7213 ± 0.0656** |
| case30-thermal | histgb | 0.002355 | 2.226% | **0.3439 ± 0.0618** |

`S_mean` tracks the missed-rate ordering on both networks and reverses with it. Gaps exceed the
std rule: case118 0.1881 vs 0.0757 (2.5x); case30-thermal 0.3774 vs 0.0656 (5.7x).

Mechanism: between the two networks ridge's barrier grows 1.34x but its conditional overshoot
grows **1.60x**, so the barrier loses ground; histgb's barrier grows 1.03x while its
conditional overshoot **shrinks to 0.45x**, so its barrier gains ground.

**The earlier two readings are resolved in favour of the second: the inequality is sound but
was never a cross-model ordering law.** It bounds misses against a model's OWN overshoot
distribution.

**NOT settled:** why ridge's conditional overshoot grows 1.60x while histgb's shrinks. Not
asked, not run.

Two-key: 12 of 12 headline values reproduced by an independent pyarrow/numpy route, MATCH to
1e-12.

---

## ADDED ROWS — 2C stratum violation rates (SINGLE-PATH, cite this source not the drift artifact)

Paired adjudication S9 established these are derivable only from `data/dataset.parquet`;
`data/drift_n0_stratum_long.parquet` contains no violation-rate field. Verified 2026-08-20,
git HEAD `03e1136e27142ad2a746fe31919bdea5b53606ac`.

| quantity | value | source file | jsonpath/column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| 2C benign stratum violation rate | `0.15373696096354447` | `data/dataset.parquet` | `min_vm < 0.94` over converged N-1 rows whose base scenario has `n0_min_vm >= 0.9433575252264039` | raw share over 139,485 rows (21,444 violations) | `8f0fd1081c8603e8` |
| 2C marginal stratum violation rate | `0.19577686957768695` | `data/dataset.parquet` | `min_vm < 0.94` over converged N-1 rows whose base scenario has `n0_min_vm < 0.9433575252264039` | raw share over 139,470 rows (27,305 violations) | `8f0fd1081c8603e8` |

Median split point: `0.9433575252264039`. **These are NOT 24.3% / 4.7%** — that pair appears in
no artifact and is recorded as NO SOURCE.

## ADDED ROWS — barrier-height S ratios, anchored (S8)

Independently re-derived from raw with both anchors exact at 0.0. Per-seed values below are the
ones the summary block does not expose.

| quantity | value | source file | jsonpath/column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| S_mean case118 ridge | `0.603785 ± 0.075685` | `data/barrier_height_long.parquet` | `S_mean_over_qhat`, network=case118, model=ridge, target 0.90 | seed-mean, pop std ddof=0; per seed .619351/.634103/.667862/.641884/.455723 | `see manifest` |
| S_mean case118 histgb | `0.791930 ± 0.074329` | same | model=histgb | per seed .781071/.851347/.868252/.657542/.801439 | |
| S_mean case30-thermal ridge | `0.721343 ± 0.065644` | same | network=case30_thermal | per seed .701759/.615385/.709015/.778465/.802089 | |
| S_mean case30-thermal histgb | `0.343935 ± 0.061752` | same | | per seed .408244/.413042/.291068/.258294/.349025 | |
| S_p99 case118 ridge → case30-thermal | `6.548389 → 4.390677` | same | `S_p99_over_qhat` | seed-mean; diff −2.157712, larger std 0.572435, exceeds | |
| S_p99 case118 histgb → case30-thermal | `9.774697 → 5.213065` | same | | diff −4.561632, larger std 0.649338, exceeds | |

**Direction, per model:** ridge S_mean **RISES** (+0.117558, std 0.075685, exceeds); histgb
S_mean **FALLS** (−0.447995, std 0.074329, exceeds). **S_p99 FALLS for both.** The two
statistics disagree in direction for ridge — always name which one is meant.

## ADDED ROWS — 3.F break-even, ms_solver, and the modal min_vm bin

Added 2026-08-21. Git HEAD at derivation: `ab970c19bd9210a2a2c00b1ff21fe9e8d8488051`.
These close the gap `notes/writing-guide.md` §3.F flags as "NOT YET IN `notes/writing-numbers.md`:
every `data/break_even.json` row AND the `ms_solver` row."

**Every row below was derived by TWO routes.** Route A is the stored field. Route B is an
independent re-derivation. Where route B is only an internal-consistency check inside the same
artifact rather than a second artifact, the row says so — that is a weaker key and is labeled.

Artifact hashes at derivation:
`data/break_even.json` = `0d4266967a611d2adc7547fab1edf0eefceb91ef2633c6336fc12362c9a6ce3f`;
`data/solve_time.json` = `94d8e8059d2b35260da090e33e3ce058c0437ef7b578556a134bbdc258a0d4ec`;
`data/dataset.parquet` = `8f0fd1081c8603e805e07a776e9f8e70392795203751fbd915d46ea4e49c1b8e`.
All three match the hashes already recorded in `notes/writing-guide.md` §0.1.

### F.1 — solver time per case

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| solver time per case (route A) | `9.14` | `data/solve_time.json` | `.ms_solver` | min over 400 timed solves, 30 warmup dropped | `94d8e8059d2b3526` |
| solver time per case (route B) | `9.138` → `9.14` at 2 dp | `data/solve_time.json` | `.min_ms` | raw min; `.n_timed`=400, `.warmup_dropped`=30 | `94d8e8059d2b3526` |
| solver time per case (route C, second artifact) | `9.14` | `data/break_even.json` | `.timing.ms_solver` | basis string identical: `minimum over N timed solves` | `0d4266967a611d2a` |

**AGREE.** Routes B and C are independent of A (B is the unrounded raw, C is a different file).
Distribution for context, same artifact: `.mean_ms`=`9.561`, `.median_ms`=`9.512`, `.std_ms`=`0.256`.
**The committed number is the MINIMUM, not the mean** — the mean is 4.6% higher. Any prose that
calls 9.14 "the solve time" is quoting a best case; `CLAUDE.md` §5 pins this.

### F.2 — generation cost

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| solves recorded in the dataset (route A) | `280500` | `data/break_even.json` | `.generation.solves_recorded_in_dataset` | count | `0d4266967a611d2a` |
| solves recorded in the dataset (route B) | `280500` | `data/dataset.parquet` | parquet metadata `num_rows` | raw | `8f0fd1081c8603e8` |
| solves recorded in the dataset (route C) | `280500` | `data/break_even.json` | `.generation.base_solves_accepted` × `.generation.per_scenario_solves` = 1500 × 187 | product | `0d4266967a611d2a` |
| recorded generation time, s (route A) | `2563.77` | `data/break_even.json` | `.generation.t_generation_s_recorded` | raw | `0d4266967a611d2a` |
| recorded generation time, s (route B — INTERNAL ONLY) | `2563.77` | `data/break_even.json` | `.generation.t_generation_s_including_rejected` × 280500 / 281787 | back-out | `0d4266967a611d2a` |

**AGREE**, exactly. **Route B for the generation time is a WEAK key.** `2563.77` appears in exactly
one artifact in `data/` (searched every `data/*.json`); the back-out only proves the two fields in
that one file are mutually consistent. There is no second measurement of generation time in the
repo. Do not present this number as cross-verified.

### F.3 — ridge break-even at its operating point, generation cost only

`data/break_even.json` `.break_even_at_operating_points.ridge.gen_only`, sha `0d4266967a611d2a`.

| field | value | route B re-derivation | agree? |
|---|---|---|---|
| `target` | `0.94` | `data/frozen_poster_numbers_v2.json` `.safety_operating_points.ridge[1].coverage_target` (sha `ccb8096d9e382d40`) | YES |
| `escalation` | `0.6434123029630445` | `data/tradeoff_curve_v2.json` `.records[24].escalation`, model=`ridge`, coverage_target=`0.94` (sha `a40a079733ecdfcd`); also `data/frozen_poster_numbers_v2.json` `.safety_operating_points.ridge[1].escalation` (sha `ccb8096d9e382d40`) | YES, bit-exact, in two other artifacts |
| `saving_ms_per_case` | `3.2580487700032297` | `9.14 × (1 − 0.6434123029630445) − 0.001162780914543728`, the last term being `.timing.ms_infer_committed.ridge` | YES, delta `0.0` |
| `one_time_cost_s` | `2563.77` | = `.generation.t_generation_s_recorded` (F.2) | YES |
| `break_even_cases` | `786903.5060507883` | `one_time_cost_s × 1000 / saving_ms_per_case` | YES, delta `0.0` |
| `break_even_scenarios` | `4230.664011025744` | `break_even_cases / .generation.branches` (=186) | YES, delta `0.0` |

**THE COST MODEL IS NOW EXPLICIT AND MUST BE STATED WHEREVER THIS ROW IS USED:**
saving per screened contingency = (solver ms) × (1 − escalation) − (inference ms). It charges
escalated solves and surrogate inference; it does NOT charge dataset generation per case — that is
the one-time cost being amortised. This is the model `report/paper_current_STS.tex:84` and Eq. 2
assert.

**`target` = 0.94 IS THE CONFORMAL COVERAGE TARGET, NOT THE 0.94 pu VOLTAGE FLOOR.** The two are
numerically identical on this operating point and mean entirely different things. Never write a
sentence where a reader could take one for the other. The histgb operating point is coverage `0.97`
(`.operating_points.histgb`), which makes the distinction visible.

**Three other cost bases exist in the same artifact and give very different answers.** Reporting
`gen_only` alone understates the amortisation threshold by ~1.9×:

| basis | `one_time_cost_s` | `break_even_cases` | `break_even_scenarios` |
|---|---|---|---|
| `gen_only` | `2563.77` | `786903.5060507883` | `4230.664011025744` |
| `gen_plus_training` | `2570.7280643584254` | `789039.1598882901` | `4242.1460209047855` |
| `gen_plus_training_plus_search` | `4870.678064358425` | `1494967.819144585` | `8037.461393250456` |
| `gen_incl_rejected_plus_training_plus_search` | `4882.441244358426` | `1498578.3175841123` | `8056.872675183399` |

All four re-derive bit-exact by `one_time_cost_s × 1000 / saving_ms_per_case` and `/186`.
The M2 search alone (`.timing.m2_search_total_fit_s` = `2299.95` over `.timing.m2_search_n_configs`
= `205` configs) nearly doubles the one-time cost. **If the manuscript names one number, it must name
which basis, and honesty points at the search-inclusive one** — the search was run and its cost is real.

### F.4 — fields §3.F cannot use without their stated disclosure

| quantity | value | source file | jsonpath | aggregation | sha256(16) |
|---|---|---|---|---|---|
| rejected scenarios | `1287` | `data/break_even.json` | `.generation.rejected_scenarios` | count | `0d4266967a611d2a` |
| total solves incl. rejected | `281787` | `data/break_even.json` | `.generation.total_solves_including_rejected` | count | `0d4266967a611d2a` |
| GNN comparator break-even, 118-bus | `498000` scenarios | `data/break_even.json` | `.comparator.value_118bus_scenarios` | read from a lit note, NOT from an artifact | `0d4266967a611d2a` |

- **Rejected count is UNVERIFIABLE BY CONSTRUCTION.** The artifact says so itself at
  `.generation.rejected_provenance`: it is a hardcoded constant in
  `feasibility/freeze_poster_numbers.py` whose stated source is a `generate_dataset.py` run log that
  is not a committed file. Route B does not exist. Two-key **FAILS** for this field; that is the
  finding, not a gap to paper over.
- **Comparator unit mismatch, stated in the artifact at `.comparator.unit_caveat`:** the GNN figure
  is in SCENARIOS, this project's break-even is in screened CONTINGENCIES, at 186 contingencies per
  scenario. `.comparator.read_from_notes` is `true` — it is a transcription from
  `notes/lit/notes/Graph Neural Networks for Fast Contingency Analysis of Power Systems.md`, not a
  measurement. Do not put it in a table beside measured rows without that label.

### F.5 — modal 0.001-pu bin of min_vm, converged N-1 only

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| largest 0.001-pu bin, share | `0.140628` | `data/dataset.parquet` | `min_vm`, rows where `outaged_type != 'none'` & `converged` | modal bin share, n=278955 | `8f0fd1081c8603e8` |
| largest 0.001-pu bin, location | `[0.940, 0.941)` | same | same | bin edges anchored at 0.000 | `8f0fd1081c8603e8` |
| largest 0.001-pu bin, count | `39229` | same | same | count | `8f0fd1081c8603e8` |

**Two-key:** route A `np.floor(min_vm / 0.001)` then `np.unique(..., return_counts=True)`, argmax;
route B `np.histogram` with explicit edges `np.arange(0.0, 1.501, 0.001)`, argmax. Both return bin
`[0.940, 0.941)`, count `39229`, share `0.140628`. **AGREE** on location, count and share.

Denominator is 278955 converged N-1 rows — matches the `case118 N-1 converged` row already in this
file. Support: `min` = `0.7179413407605296`, `max` = `0.96031121678118`.

Top five bins, same derivation:

| bin | count | share |
|---|---|---|
| `[0.940, 0.941)` | `39229` | `0.140628` |
| `[0.941, 0.942)` | `37343` | `0.133867` |
| `[0.942, 0.943)` | `30094` | `0.107881` |
| `[0.943, 0.944)` | `29375` | `0.105304` |
| `[0.944, 0.945)` | `22581` | `0.080949` |

**This is the boundary-mass mechanism at 1-mpu resolution.** The modal bin is the FIRST bin at or
above the 0.94 pu floor, and the five bins above the floor fall monotonically. Sum of the five =
`0.568629`, which reproduces the `case118 boundary mass` row (`0.94 <= min_vm < 0.945` = `0.568629`)
already in this file, to six decimals — an independent confirmation of that row.

**Bin edges are anchored at 0.000 and the bin is half-open `[lo, hi)`.** A different anchor moves
the modal bin. State the anchor whenever the number is used.
