# Round-1 challenges from the statistics / ML panelist (panel_stats)

I read `round1_{power,nonspecialist,sts_judge,repro}.md`. Scratch work is in `/Users/rajansaha/.claude/jobs/484f4ac7/tmp/panel_stats/`.

## 0. Corrections to my own round-1 file (reviewers caught these, or I found them while cross-checking)
- **STATS-01 and STATS-09: histgb at 0.97 has 2 of 5 seeds above 1%, not 1 of 5.** The per-seed values are 1.162, 0.798, **1.032**, 0.699, 0.470 (`data/tuned_metrics.json` → m2 sweep, via `heldout_op.py`). REPRO-06 is right. Ridge at 0.94 is 1 of 5 above 1% (1.146). This strengthens STATS-01.
- **STATS-07 table: case39 histgb |rel err A| is 10.1%, not 3%.** I averaged the *signed* errors. The other cells were already absolute values: case39 ridge 32.2, case24 ridge 211.1, case24 histgb 19.4, illinois ridge 4.7, illinois histgb 6.1. The conclusion does not change.
- **Upper error-bar edge.** Unrounded, 0.8322 + 0.2447 = 1.077, so "1.08", not "1.07" (REPRO-08, accepted).

## 1. The tensions the lead asked about

**(a) Is the "Theory" section definitional (me, STS-10, NS-15) or a strength worth protecting (POWER strength #3)? Both are right, about different parts.**
- *Power is right:* Eqs. (3)–(4) are exact, and they hold whatever the oracle is. They therefore survive POWER-01/02. The ceiling and saturation reasoning at l.347 is correct and useful:
  - as q̂ grows, escalation tends to P(p̂ ≥ L);
  - for a perfect model it saturates at 1 − the violation rate;
  - persistence can never flag.
  The values check out: ceilings 74.89 ± 0.83 and 82.79 ± 0.37, saturation 82.64.
- *We are right:* nothing in III.5 is *derived*. Eq. (3) is the gate rule rewritten, and Eq. (4) is the certify rule combined with y < L.
- **What should be protected:**
  - the ceiling/saturation decomposition at l.347;
  - Eq. (4), but only if it is carried one step further to the result it implies. A miss is a miscoverage event, so P(certify ∧ y < L) ≤ α, and therefore missed rate ≤ α / P(y < L). That is the paper's only *guaranteed* safety statement (STATS-03).
- **What should not be protected:**
  - the section title "Theory";
  - S_mean as it currently stands (see (e) below).

**(b) case24 ridge predictor-A error: 211% (me) versus 115% (REPRO-04). Both numbers are right; they aggregate differently.** From `data/netstudy2/summary.json` → `cross_comparisons[network=case24_ieee_rts]`, |rel_err_A|:
- ridge, mean over the 9 targets: **2.111**. The range runs from 1.081 at 0.90 to 3.772 at the top target.
- histgb, mean over 9 targets: 0.194.
- Both models pooled (18 cells): **1.153**. This is REPRO's figure.
- ridge at 0.90 only: 1.081. This is the STS judge's "0.451 vs 0.217".

The report should give model × network cells. Pooling ridge with histgb hides the finding that ρ·q̂ tracks histgb escalation well but fails for ridge. Predictor A also exceeds 1 in 2 of the 54 cross predictions, and `esc_pred_rho_*` in `data/sweep_results_long.parquet` reaches 2.34. A predicted escalation above 1 is impossible, so any version of the law that gets printed needs capping or a comment.

**(c) Matched escalation: I found histgb safer at 30–47% escalation; REPRO found ~42–51%. These are consistent.**
- The two analyses cover different ranges. I interpolated each seed's 30-point sweep and started at 30%. REPRO paired the nearest sweep points on the mean curves (`data/tradeoff_curve_v2.json`) and started at 42%.
- Where they overlap, they agree: at ~42% escalation the gap is 1.33 (REPRO), against 1.44 at 40% (mine).
- At 50%, my per-seed interpolation gives 2.79 ± 0.40 vs 2.15 ± 0.62. The gap of 0.64 is just above 0.62, so it is marginal. REPRO's unpaired points give 1.02 > 0.44 at slightly different escalations (49.1 vs 51.2), which inflates the gap.
- **The joint statement all of us support:** histgb is safer from about 30% to about 50% escalation; the two models tie from about 55% to 70%, which includes the recommended ~64% point; ridge is safer only from about 72% up. STS-05 and NS-05 reach the same conclusion.

**(d) Does the label artifact (POWER-01/02, REPRO-01) change my statistical conclusions? Partly.** I accept both findings. Two independent back-off re-solves agree: 8.7% of random violations flip in POWER's sample, 7 of 50 (14%) in REPRO's, and 20% of the violations in [0.935, 0.94) flip.
- *Unchanged:* the conformal coverage guarantee and every internal comparison. Test-set selection (STATS-01), matched escalation (STATS-02), clustering (STATS-04) and the flag precision ranking (STATS-06) are all statements about predicting *pandapower's* min_vm, and all methods face the same labels.
- *Changed, the missed-rate definition:* "missed violation" now means a miss against a label that is noisy in one direction, and the noise is concentrated exactly where misses concentrate: 74% of ridge misses and 55% of histgb misses lie within one band width. The physical missed rate could therefore be *lower* than printed; the denominator shrinks as well, so the net effect is unknown. The headline's "0.83 vs 1%" gap is smaller than both the seed std and the plausible label-noise band. The quantity is therefore unresolved on two independent axes, which strengthens STATS-01/09.
- *Changed, S_p99 and miss depth:* the deep tail rises by a median of +0.122 pu under back-off (POWER-02). My suggestion to report S_p99 in place of S_mean (STATS-08) is only meaningful once the labels are validated, so I now mark S_p99 as oracle-dependent.
- *Static-ranking baseline (STATS-05):* the comparison stays internally valid, since both methods are trained and scored on the same labels. It could be biased in either direction if the artifact is concentrated on particular elements, for example trafo 0 in POWER-10, which a by-element static ranking would pick up. That is unverified. The tie at the ridge budget should be reported with that caveat, not dropped.

## 2. Challenges to other panelists' findings

- **STS-04 (substance). The "limit sweep" is not a controlled dose-response test of the mechanism.** In `data/sweep_results_long.parquet`, `boundary_mass` is the *true-voltage* mass in [L, L + q̂). The window width is model-dependent: the mean is 0.0888 for ridge and 0.0386 for histgb. `esc_observed` is the *predicted-voltage* mass in the same window. Their means are almost equal (0.0888 vs 0.0892; 0.0386 vs 0.0387), so a Pearson r of 0.977 to 0.995 is close to guaranteed whenever p̂ tracks y. That makes it an accuracy check, not a manipulation.
  - The "within-network predictor MAE 0.61 pp" is the same plug-in quantity estimated on the calibration split, so it measures sampling error.
  - It does support "an operator can estimate escalation after calibrating". It does not show *why* the mass is there.
  - The real manipulations of the data-generating process are:
    - the N-0 gate on/off: 56.86 → 28.83% (`data/unconditioned_base.json`);
    - POWER-03(d), the `GEN_VM_LO` knob (1 seed, 40 bases, provisional).
  - The N-0 stratum split is informative but selects on a covariate that also changes model error: benign-stratum histgb misses 8.2%.
  - Recommendation: lead with the unconditioned build, not the limit sweep.
- **STS-05 (substance). "S_mean explains the case30 reversal" rests on n = 2 networks.**
  - Agreement in ordering on 2 networks happens by chance 1 time in 4.
  - S_mean is a *mean* signed overshoot. Misses are a tail event, P(o ≥ q̂ + depth | violation). The repo's own tail statistic P(overshoot > q̂ | violation) is 0.39 vs 0.41 on case118 (`data/barrier_height.json` → `summary_at_090`), which barely separates the models.
  - Present the relationship as an observation, not an explanation, unless it is tested on the 3 netstudy2 networks.
- **POWER-05 and NS-04: agree, and adding a number.** Flagged cases carry no calibration and have to be solved in practice. POWER-05's open question can be answered from my refit predictions (`analyze.py`, 300 test base cases per seed):
  - At histgb 0.97, **11.1 ± 2.6% of base cases certify at least one violation**. At histgb 0.90 the figure is 47 ± 5%, and at ridge 0.97 it is 0.47 ± 0.50%.
  - Flag precision is 56.1 ± 2.0% for ridge and 85.6 ± 1.4% for histgb.
  - Both figures use pandapower labels, so the caveat from (d) applies.
- **STS-08 (severity: agree, with one qualifier).** The Mondrian result (43.7% escalation, 1.66% missed vs global 63.8% and 1.16%) is a move *along* the trade-off. It is not evidence either way until it is compared at matched escalation (as in STATS-02) and over 5 seeds.
- **POWER-01 FATAL.** I defer on the physics and do not challenge it. Statistically it is an error in a *featured* number, printed three times, and REPRO reproduces the flip independently. From my discipline I would rate it MAJOR. The trust damage a power judge would register justifies FATAL, as a physics call.
- **STS-01 / NS-01 FATAL (AI disclosure).** Outside my discipline. No challenge.
- **No disagreement** with REPRO-02/03/04/06/07, NS-02 (the "90% coverage makes an outsider expect 10% missed" point is the reader-level form of STATS-03), NS-05, STS-10, STS-11 or STS-20.

## 3. Revised scores and severities
- **Rigor: 6 → 5.** The label layer was never validated against a complementarity-consistent solver (POWER-01/02, REPRO-01). The statistical design itself is unchanged.
- **Significance stays 4.** POWER-05's flag-solved speedup (1.24× at histgb 0.97) confirms the low value I already scored.
- **Originality 5, clarity 5 and student potential 8 are unchanged.**
- **Severity changes:**
  - STATS-06 (flag branch) stays MAJOR, now reinforced by POWER-05.
  - STATS-08 (Theory) stays MINOR. The ceiling/saturation part moves to my protected list, per (a).
- **Counts:** FATAL 0, MAJOR 7, MINOR 5 (unchanged).
