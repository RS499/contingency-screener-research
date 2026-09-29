# Round-1 challenges from REPRO (reproducibility auditor)

Scripts: `/Users/rajansaha/.claude/jobs/484f4ac7/tmp/panel_repro/t9.py` (cross-run of PV/PQ implementations) and the inline
commands quoted below. `.venv/bin/python`, ddof=0.

## (a) Label-flip rate: REPRO-01 vs POWER-01/02, reconciled (sampling, not method)
- **Implementations.** Mine (`t7.py:solve_pvpq`) and power's (`panel_power/pvpq.py`) use the same algorithm:
  - pin every Q violator at its limit (as an sgen), release any pinned unit whose V is on the wrong side of V_set, and repeat;
  - `enforce_q_lims=False`, `init="dc"`.
  Differences:
  - Tolerances: mine 1e-6 on Q and V; power's TOL_Q 1e-3, TOL_V 1e-4.
  - Mine skips `slack` gens; none are slack in case118, so no effect.
- **Cross-run (t9.py).** My loop on power's 500 rows (`relabel.csv` + `relabel2.csv`):
  - max |mine − power| = 2.8e-5 pu, 0 rows > 1e-4;
  - identical flip counts in every stratum: viol 13/150, [0.935, 0.94) 20/100, [0.92, 0.935) 1/60, deepest40 0/40, boundary/safe 0.
- **Deepest case.** 0.94507 (power) and 0.9451 (mine) are the same number: my full value was 0.9450730085, which is the scenario's N-0 minimum. That was rounding only.
- **Why the rates differ.** My 7/50 (14%) comes from a 300-row uniform sample, and power's 13/150 (8.7%) comes from a violation-only stratum. The Wilson 95% CIs (about 7–26% and 5–14%) overlap.
  - Pooled: 20/200 = **10%** of random violations flip to safe.
  - My 3.7% of all rows includes 4/250 safe→violation flips. Power saw 0/150 in boundary+safe strata. Pooled safe→violation is 4/400 = 1%.
  - Both rates should be quoted with their n. Neither panel's number is wrong.
- **Severity change.** Two implementations now agree to 3e-5 pu on 500 rows (same algorithm, so this is not an independent solver). I **upgrade REPRO-01 to FATAL** for the deepest-miss claim (printed 3×: l.292, l.303, l.367), agreeing with POWER-01. The label-noise part stays MAJOR (= POWER-02). I accept power's added deep-tail result (dataset min 0.7179 → 0.9294) as reported but did not re-run it; my t8 sample had no row below 0.80.

## (b) case24 predictor-A error: 115% (REPRO-04) vs 211% (STATS-07). Both correct, but STATS-07 has one wrong cell
- `data/netstudy2/summary.json → cross_comparisons`, mean |rel_err_A| by network × family:
  - case24: ridge 211.1%, histgb 19.4%. My 115% is the two-model mean ((211.1 + 19.4)/2 = 115.3); STATS splits by model. Consistent.
  - illinois200: ridge 4.7, histgb 6.1 (STATS says 5 / 6).
  - case39 ridge: 32.2 (STATS says 32).
  - **case39 histgb: 10.1%** (mean |rel err|). STATS-07 prints **3%**, which is the *signed* mean (+0.030) of values ranging −0.108 to +0.281. Challenge: the case39 histgb cell must use the absolute mean to match the table's stated definition.
  - ρ·q̂ > 1 in 2 of 54 cross predictions: VERIFIED.
- REPRO-04 is refined: the failure is **case24 ridge**, not case24 as a whole. STATS' model split is the better presentation.

## (c) N-0 bases in [0.94, 0.945): judge 67.7% vs power "68%". Same quantity, agree
- DS base rows (`outaged_type=="none"`): 1,016/1,500 = **67.73%**. Power's own text (POWER-03(b)) also says 67.7%; "68%" is rounding.
- Also consistent: STS-03's 77.6% / 93.4% (`data/sts_dataset_facts.json → n0_persistence.share_within_pct` 77.65, `boundary_strip.share_same_weakest_bus_as_n0_pct` 93.37). That file is **untracked** (REPRO-10), so these numbers need a committed source before anyone cites them.
- Different quantities, both fine:
  - POWER's 67.3% "within 1e-4 pu of the N-0 min" uses a tighter threshold than STS-03's 1e-3.
  - POWER's 31.6% (strip rows whose argmin is an in-service generator bus) is a generator-bus count; `sts_dataset_facts` 31.62% is the share at bus index 75 only, the same number by coincidence of definition. I did not verify the generator-bus framing.

## (d) Static ranking vs gate (STATS-05): VERIFIED, with one caveat that strengthens it
- `data/baselines.json → gate.ridge`:
  - k_equivalent 91.3;
  - `comparators_at_gate_k.static_severity` 96.91 ± 0.49%;
  - `capture_escalate_or_flag` 97.04 ± 0.44%.
  - Gap 0.13 < 0.49: a tie under the std rule.
- `gate.histgb`: k 57.0; gate 95.28 ± 0.98 vs static 91.01 ± 2.00. Gap 4.27 > 2.00: real.
- Caveat (the file's own `asymmetry_warning`):
  - The gate's 97.04% credits flagged violations the solver never checks. The like-for-like `capture_escalate_only` is 15.96 ± 0.58% for ridge.
  - Flag precision is 56% for ridge (STATS-06).
  - At an equal solve budget, the static ranker's 96.9% is solver-verified, so for ridge it is at least as good as the gate, not merely tied.

## Other challenges and corrections
1. **STS-12 / NS-09 (Fig. 5 labels): they are right, and my REPRO "checked and consistent" line was wrong for the submitted PDF.**
   - I extracted all images with `pdfimages -png paper_v39.pdf`.
   - Figs. 1–4 are pixel-identical to `data/gate_schematic_v4.png`, `tradeoff_hero_col_v2.png`, `miss_depth_v3.png` and `boundary_mass_hist_v2.png` (mean |Δ| = 0).
   - Fig. 5 differs from `data/critical_bus_map.png` (mean |Δ| 0.039, same 4128×3582 size). The PDF copy carries 0-based labels (bus 75/52/106/0/20). The repo PNG has IEEE labels (76/53/107/1/21), per `domain_figure.py:97` and its manifest.
   - The Overleaf project holds a stale figure that is not the repo artifact. **New MAJOR (REPRO-13):** replace Fig. 5 in Overleaf with the repo PNG, and check every float's bytes against the repo before export.
2. **POWER-14 (case30 speedup uses case118's 9.14 ms) is overstated.**
   - Recomputing from `data/case30_thermal/case30_thermal_frozen.json` records shows the implied t_surr = **1.0e-6 ms**, a placeholder rather than a measurement.
   - So case30 net speedup = 1/escalation exactly, and swapping in 4.848 ms (`case57_feasibility.json`) gives the identical 17.91 ± 3.71.
   - The real issue is that case30's surrogate time was never measured. If NS-12 / STS-05's "17.9×" is printed, it must say it equals 1/escalation.
3. **STATS-01 VERIFIED** from `data/tuning_search.json` (`inner_cov_at` of each seed's M2 tag) applied to the `tuned_metrics.json` sweeps:
   - histgb targets 0.96/0.97/0.97/0.96/0.96 → missed 1.15 ± 0.27%, escalation 59.3 ± 4.0%, **4/5 seeds > 1%**;
   - ridge → 0.77 ± 0.78%, 65.4 ± 8.1%, 1/5.
   This supersedes my REPRO-06 wording: the headline should be a held-out operating point, not a per-seed count at a test-picked point.
4. **STATS-02 and my REPRO-03 agree** at every shared escalation level (~47%: 3.41 vs 2.53 interpolated; my table point 3.50 vs 2.48). Keep one of the two as the canonical finding.
5. **STS-05 case30 values VERIFIED:**
   - case30 records histgb@0.90 2.23 ± 0.35% at 2.65% escalation, ridge 6.09 ± 0.42% at 11.9%;
   - S_mean case30 histgb 0.344 ± 0.062, ridge 0.721 ± 0.066 (`barrier_height.json → summary_at_090`).

## Effect on my severities and scores
- REPRO-01 → FATAL (the deepest-miss claim); REPRO-13 added (MAJOR). New totals: **FATAL 1, MAJOR 5, MINOR 7.**
- Scores: Rigor 7 → **5** (the stale submitted figure, POWER-03's sampler confound with `GEN_VM_LO = VMIN_LIMIT = 0.94` at `generate_dataset.py:7-9`, and STATS-01's test-picked operating point).
- Significance 5 → **4** (STATS-01, POWER-03, the static-ranking tie).
- Originality 6, Clarity 6 and Student potential 8 are unchanged.
