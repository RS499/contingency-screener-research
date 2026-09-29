# Round-1 blind panel: Statistics / ML PhD (conformal prediction, selective prediction, risk control)

Reviewer: panel_stats. Paper: `report/paper_current_STS.tex` (compiled text `notes/panels/round1_paper_text.txt`).
Scratch scripts (all read-only against the repo, outputs only in the scratch dir):
`/Users/rajansaha/.claude/jobs/484f4ac7/tmp/panel_stats/{matched_esc,heldout_op,refit,analyze}.py`.
`refit.py` re-fits the five per-seed M2 models (configs from `data/tuning_search.json`, same splits and
feature selection as `scripts/tune_surrogates.py`) and saves cal/test predictions. **Reproduction check:**
q-hat, escalation and missed rate at 0.90 and 0.97 match `data/tuned_metrics.json` for all 10 model×seed
pairs exactly, except one row of escalation on ridge seed 3 (Δ = 1.8e-5). Every number below labelled
"panel recomputation" comes from those predictions.

---

## 1. Rubric (statistics / ML point of view)

| Criterion | Score | One sentence |
|---|---|---|
| Originality | 5 | A single global split-conformal quantile wrapped around a regressor with a reject band is a known construction (the paper's own ref. [21], conformal triage, is already a three-way gate). What is new is the use: physical units, an exact solver as the fallback, and net-cost accounting. |
| Rigor | 6 | The engineering rigor is well above student level: group-aware splits, tuning nested inside train, manifests, hash-locked predictions, and a bit-exact reproduction. The statistical inference is not at that level: the operating point is picked on test, models are compared at a matched nominal knob rather than matched cost, and the paper never states what is guaranteed. |
| Significance | 4 | One primary network. The headline "floor" is partly produced by the sampling design (see STATS-07). The cross-network test of the mechanism has a mean relative error of 47%. |
| Clarity | 5 | Clear on the gate and the speedup accounting. Muddled on exactly the statistical points a doctoral judge will probe: exchangeability, what "coverage" means, the Barber et al. paraphrase, and the "Theory" section. |
| Student potential | 8 | The instincts are there: the clip-artifact self-correction, negative results reported as negative, locked predictions, no tuning to a nicer number. The gaps are ones of framing and one missing analysis, not of integrity. |

Counts: **FATAL 0 · MAJOR 7 · MINOR 5**

---

## 2. Findings

### STATS-01: MAJOR. The headline operating point is picked on the test sweep. Picked on held-out data, it misses more than 1% in 4 of 5 splits.
- **Anchor:** abstract, l.81, "For the gradient-boosted model, first going just under a 1\% mean missed rate at a 0.97 coverage target…". Also IV.1, l.231, "…the average of missed cases falling below 1\% at 0.94 for the ridge model… and 0.97 for the gradient-boosted model…". Also V, l.365, "All five splits are under 1\% at 0.97, but not at 0.96…".
- **Evidence (VERIFIED):** `build_v2_frozen.py:first_below_1pct` takes the first coverage target whose **test** mean missed rate is below 1%. So 0.94 (ridge) and 0.97 (histgb) are chosen on the same data that reports the result. That is a minimum-selected statistic from a 30-level sweep, and it is biased downward.
  The repo already contains the honest version. The inner M2 search records, per seed, the smallest coverage level whose **inner** missed rate is ≤1% (`data/tuning_search.json` → `records[tag=M2 pick].inner_cov_at`). Applying that held-out choice to the test split (`heldout_op.py`):

  | model | inner-chosen targets (seeds 0-4) | test missed | test escalation | seeds >1% |
  |---|---|---|---|---|
  | histgb | 0.96, 0.97, 0.97, 0.96, 0.96 | **1.15 ± 0.27%** | 59.3 ± 4.0% | **4 / 5** |
  | ridge | 0.97, 0.94, 0.96, 0.92, 0.94 | 0.77 ± 0.78% (max 2.24%) | 65.4 ± 8.1% | 1 / 5 |

  The two networks also use different selection rules, both applied on test. For case118 the rule is "first **mean** below 1%": ridge 0.94 has seed 2 = 1.146% and histgb 0.97 has seed 0 = 1.162%, so 1/5 seeds is above 1% at each. For case30 the rule is "all five splits below 1%" (0.97, 5.84% escalation), although the mean first drops below 1% at 0.96 (0.91 ± 0.22%, 4.86% escalation). Source: `data/case30_thermal/case30_thermal_frozen.json` → `records`.
- **Why it matters:** "just under 1%" in the abstract is not a held-out result. The qualitative finding survives: roughly 60–65% escalation is needed for about 1% misses. The number does not.
- **Suggested fix:** Report the operating point chosen without test data (the inner-split choice already computed, or the STATS-05 calibration) as the headline, with its test missed rate and the count of seeds above 1%. Present the full Table 2 sweep as descriptive. Use one stated selection rule for both networks.

### STATS-02: MAJOR. "The faster model is not the safer one" is an artifact of comparing at a matched nominal coverage target. At matched escalation (matched cost), the more accurate model is safer over most of the range.
- **Anchor:** IV.2 heading, l.290. l.292: "On the IEEE 118-bus system, the more accurate model is not safer at any point in the coverage axis…" and "…at a coverage of 0.96, the linear model misses 0.14\%… while the gradient-boosted model misses 1.36\%".
- **Evidence (VERIFIED, `matched_esc.py`):** The coverage target is not what the operator pays for. Ridge at 0.96 escalates 71.4% and histgb at 0.96 escalates 57.0%, so the 0.96 comparison gives ridge 14 points more solver budget. I interpolated each seed's 30-point sweep (`data/tuned_metrics.json` → `records[metric=m2].sweep`) onto a common escalation grid. Missed rate, mean ± std over 5 seeds:

  | escalation | ridge | histgb | std-rule verdict |
  |---|---|---|---|
  | 30% | 6.99 ± 0.48 | 4.79 ± 1.09 | histgb safer (gap 2.20 > 1.09) |
  | 40% | 4.78 ± 0.52 | 3.34 ± 0.83 | histgb safer (1.44 > 0.83) |
  | 46.7% | 3.41 ± 0.49 | 2.53 ± 0.70 | histgb safer (0.88 > 0.70) |
  | 55% | 2.02 ± 0.37 | 1.63 ± 0.50 | tie |
  | 63.7% | 0.82 ± 0.15 | 0.89 ± 0.31 | tie |
  | 70% | 0.29 ± 0.10 | 0.47 ± 0.21 | tie |
  | 72% | 0.14 ± 0.06 | 0.37 ± 0.17 | ridge safer (0.23 > 0.17) |

  At the operating point the paper recommends (about 64% escalation), the two models are statistically indistinguishable. The paper half-says this at l.349 ("run the models at a 0.94 or a 0.97 target"), which contradicts the IV.2 heading. The risk–coverage framing cited at l.231 ([14, 23]) is exactly the matched-acceptance comparison, but the paper never plots it.
- **Suggested fix:** Compare the models on missed rate versus escalation (or versus net speedup) with seed bands, and restate IV.2 to match what that comparison shows. Keep the matched-target table only as a description of the knob.

### STATS-03: MAJOR. The paper never separates what is guaranteed from what is measured, and it misstates the assumption behind the guarantee.
- **Anchors:**
  - l.128: "…converts the residuals from the calibration dataset into a coverage guarantee…".
  - l.132: "As long as the test cases and calibration cases come from the same type of condition (a single-element outage), the true voltage remains at or above the lower bound with the desired probability."
  - l.363: "This establishes the lower bound because, in split conformal prediction, I can be correct on average but not necessarily inside the band. If one demands perfect correctness…".
- **Evidence (VERIFIED from `feasibility/gate_eval.py`):**
  1. The guarantee is marginal coverage, P(y ≥ p̂ − q̂) ≥ 1 − α. It holds on average over base cases, contingencies and the calibration draw, under **exchangeability of (features, voltage) pairs**. That is not the same thing as "the same type of condition (a single-element outage)". Seasonal drift, a different load window, or a different N-0 filter all break it while every case is still a single-element outage.
  2. **The missed-violation rate, the paper's safety headline, has no guarantee.** The only bound that follows is the one the paper's own inequality (4) nearly states: a miss is a miscoverage event, so P(certify ∧ y < L) ≤ α. The conditional missed rate is therefore bounded only by α / P(y < L) = 0.10 / 0.1748 ≈ 57% at the 0.90 target and 0.03 / 0.1748 ≈ 17% at 0.97. The measured rates are 4.72% and 0.83%. The bound holds but is more than 10× loose. Every missed-rate number in the paper is empirical, and the text never says so.
  3. l.363 paraphrases Barber et al. [18] incorrectly. That paper shows that distribution-free **conditional** (per-x) coverage is impossible without assumptions (`notes/cited papers/The limits of distribution-free conditional predictive inference.pdf`, abstract). It says nothing about "perfect correctness with limited calibration data".
  4. "Finite-sample rank approach" (l.128) is implemented correctly in code (`k = ceil((n+1)(1-α))`, capped at n). But n there is the number of **rows**, and the exchangeable unit is the base case (STATS-04).
- **Suggested fix:** State in Method which quantity carries a guarantee (marginal coverage), under which assumption (exchangeability at the base-case level), and which quantities are only measured (missed rate, escalation, speedup). State the joint bound and how loose it is. Correct the exchangeability sentence and the [18] paraphrase.

### STATS-04: MAJOR. The exchangeable unit is the base case, not the contingency. Uncertainty and the operational meaning of "1%" are both understated.
- **Anchor:** l.363, "Every base case generates 186 related contingencies, and therefore, the coverage rates are measured averages and not an assurance for a single contingency."
- **Evidence (panel recomputation, `analyze.py`, 300 test base cases per seed):**
  - The cluster-bootstrap standard error of test coverage (300 resamples over base cases) is **7.0 ± 0.8×** the i.i.d. binomial SE for ridge and **5.6 ± 0.8×** for histgb. That is a design effect of roughly 30–50. The effective sample size is on the order of the number of base cases, not the 55,789 rows.
  - Per-base-case coverage at the 0.90 target falls as low as 0.048–0.145, depending on seed and model. 2–8% of test base cases have coverage below 0.80.
  - Operator-level statistic: at the recommended histgb 0.97 point, **11.1 ± 2.6% of test base cases contain at least one certified (missed) violation**. At histgb 0.90 the figure is 47 ± 5%. At ridge 0.97 it is 0.47 ± 0.50%. A "0.83% of violations" figure hides that roughly 1 in 9 N-1 studies would contain a silent miss.
- **Suggested fix:** Report per-base-case statistics next to the pooled ones: the share of base cases with any miss, and the spread of per-base-case coverage. State that the conformal guarantee is exchangeable at the base-case level. Optionally, calibrate at the scenario level (for example, one score per base case such as the maximum overshoot) and compare.

### STATS-05: MAJOR. Baselines. The only baselines shown are trivial. A non-ML baseline computed in the repo matches the ridge gate at matched budget. The risk-controlling alternatives the paper cites are never run.
- **Anchors:** III.2, l.124, "I tested my models against two baselines: persistence… and the training mean". Table 1 caption, l.208. V, l.363, contrast with [3]/[2]. l.361 cites [21], conformal triage.
- **Evidence:**
  1. *Reported, `data/baselines.json` → `gate.ridge.comparators_at_gate_k`:* at the ridge gate's matched solve budget (k ≈ 91 of 186 per base case, the 0.90 target), a **static element ranking by training-set violation frequency** captures 96.91 ± 0.49% of violations. The gate captures 97.04 ± 0.44% (escalate or flag). They are identical, and the static ranking never looks at the operating point. At the histgb budget (k ≈ 57), the gate leads the static ranking, 95.28% vs 91.01 ± 2.00, a real gap. None of this appears in the paper.
  2. *Conformal triage [21] (cited) is already a three-way low-risk / high-risk / uncertain gate*, with guarantees on the error rate of **both** skip branches (NPV and PPV; abstract of `notes/cited papers/Conformal Triage for Medical Imaging AI Deployment.pdf`). RCPS [2] is cited as well. Neither is run as a calibration alternative.
  3. *Panel recomputation (`analyze.py`):* the gate is a one-parameter threshold (certify iff p̂ ≥ L + t), so any calibration method just picks t. Picking t by **violation-conditional split conformal** at δ = 1% (the ⌈(n_v+1)(1−δ)⌉-th order statistic of p̂ − L over calibration violations) gives the following on test:

     | model | test missed | test escalation |
     |---|---|---|
     | histgb | 0.98 ± 0.26% | 61.2 ± 3.3% |
     | ridge | 1.07 ± 0.28% | 61.7 ± 1.7% |

     This is the same frontier as the paper's hand-picked points. The difference is that it comes from a method whose nominal guarantee is on the headline metric, and it needs no test scanning. Its per-split variation (0.62–1.46%) again reflects the base-case clustering from STATS-04.
- **Suggested fix:** Add the static-ranking comparator and the matched-budget comparison to Table 1 or a companion table. Add one risk-controlling calibration of the same gate (violation-conditional or RCPS/CRC-style) as the principled alternative. Position the global-quantile band against it, not only against persistence and the training mean.

### STATS-06: MAJOR. The flag branch skips the solver with no calibration, and its error rate is never reported.
- **Anchors:** III.4, l.140, "Flag (skip the solver): $\hat{p}< L$…". Table 1, l.215 ff.: the train-mean row shows 0.00 missed.
- **Evidence (panel recomputation, 5 seeds; M2 models):**

  | model | flag precision | share of all contingencies false-flagged |
  |---|---|---|
  | ridge | **56.1 ± 2.0%** | 11.0 ± 0.9% |
  | histgb | 85.6 ± 1.4% | 2.5 ± 0.3% |

  Flag decisions depend only on p̂, so these are identical at every target. The train-mean row reports 0.00% missed only because it flags every case, and a table without a false-flag column cannot show that. Ridge's lower missed rate at a matched target partly comes from predicting below L more often. l.347 says this ("Linear prediction predicts below the limit more often…"), but the cost is never quantified.
- **Suggested fix:** Add a false-flag (or flag-precision) column to Tables 1 and 2. Say explicitly that only the certify branch is covered by the band. Either calibrate the flag branch (as in [21]) or state that it carries no guarantee.

### STATS-07: MAJOR. The causal claim in the title and conclusion ("limits set by boundary mass") is supported by a definitional identity, a two-network contrast that confounds network with sampling design, and a cross-network test whose error is large and dominated by one case.
- **Anchors:** title, l.63. Conclusion, l.388: "The main reason is that most of the cases fall very close to the limit." IV.4, l.353: "…the mean relative error was $0.4726$ for predictor A and $0.4933$ for predictor B…". l.355: "I only report the average errors…".
- **Evidence (VERIFIED, `data/netstudy2/summary.json` → `cross_comparisons`, `cross_2a_points.json`):**
  - **Effective sample size.** The 54 cross-network predictions are 3 target networks × 2 models × 9 monotone coverage targets. In effect n = 3 networks, and predictor B's slope was fit on 2–4 prior networks.
  - **Where the error comes from.** Predictor A's mean |relative error| by network and model:

    | network | ridge | histgb |
    |---|---|---|
    | case39 | 32% | 3% |
    | case24 | **211%** | 19% |
    | illinois200 | 5% | 6% |

    ρ·q̂ exceeds 1 (an impossible escalation) in 2 of the 54 predictions; outside the cross test it reaches 1.217 for case118 ridge at 0.97. The mechanism predicts histgb escalation well and ridge escalation poorly, and averaging hides this.
  - **Against a no-physics baseline.** Predicting each target network's escalation by the mean escalation of its prior networks, at the same model and target, gives mean absolute error 0.1144 vs predictor A's 0.1163, so A is no better on absolute error. On relative error A does better (0.47 vs 0.89).
  - **Sampling-design confound.** Removing the N-0 ≥ 0.94 acceptance filter halves case118's boundary mass, from 56.86% to 28.83% (`data/unconditioned_base.json` → `unconditioned.boundary_0p94_to_0p945_pct`; not in the paper). The case30 contrast (7.09%) also uses a different acceptance rule (thermal filter) and load window (0.87–0.99). So "118 vs 30" differs in network and sampling design at the same time.
  - **The identity.** Eq. (3) is the gate's definition, so escalation = P(L ≤ p̂ < L + q̂) holds by construction. It shows that the floor is mass-near-L-in-prediction-space. It does not show that boundary mass of the *true* voltages drives it across networks.
- **Suggested fix:** Report the per-network and per-model breakdown and the naive baseline alongside the averages. State n = 3 target networks. Report the unconditioned boundary mass and acknowledge that the floor depends on the base-case acceptance rule. Scope the title and conclusion to "on case118 under this sampling design".

### STATS-08: MINOR. The "Theory" section restates the gate and summarizes the wrong part of the distribution.
- **Anchor:** III.5, l.165–190: "Since this inequality comes from the gate's mechanisms, it is a structural property…" and Eq. (5), S_mean.
- **Evidence:** Eqs. (3)–(4) follow in one line from the certify rule (`data/barrier_height.json` → `identity_checks.max_identity_gap` = 5.6e-17, a check of an identity). S_mean is a *mean* signed overshoot over violations, and a mean does not determine misses. Misses live in the tail: the repo's own S_p99 at 0.90 is **6.55 ± 0.57 (ridge)** and **9.77 ± 0.57 (histgb)**, and P(overshoot > q̂ | violation) is 0.39 / 0.41 (same file, `summary_at_090`). Neither is reported. The section also omits the one real consequence of Eq. (4): P(miss) ≤ α (STATS-03).
- **Suggested fix:** Either rename the section to something descriptive, or add the joint bound and report a tail quantity in place of, or next to, S_mean.

### STATS-09: MINOR. The meaning of the error bars and the reporting of seed dispersion are inconsistent.
- **Anchors:** abstract, l.81 ("3.29 times faster… misses 4.72\%", no ±). Table captions, l.208 and the Table 2 caption. IV.1, l.231 ("error bars still reach up to about 1.0–1.07\%").
- **Evidence (VERIFIED):** The std is population std (ddof = 0) over n = 5 re-splits of one generated dataset. It measures split variability, not data-generation variability, and it is neither a standard error nor a confidence interval. With ddof = 1 the headline upper bars become 0.79 + 0.23 = 1.03% (ridge 0.94) and 0.83 + 0.27 = 1.11% (histgb 0.97). The mean being 0.83% versus a 1% threshold is about 1.4 standard errors of the mean, not a resolved difference. The per-seed count is given for case30 ("all five splits") but not for case118, where 1 of 5 seeds is above 1% at each headline point (STATS-01).
- **Suggested fix:** State the dispersion convention and what it represents in each caption. Give ± on every abstract number. Report per-seed counts above 1% the same way for both networks.

### STATS-10: MINOR. Two comparative words fail the std rule.
- **Anchors:** IV.4, l.353: "(worse on relative error yet slightly better on absolute error at 0.1056 versus 0.1163)". l.347: "…so its ceiling lands just above the saturation point."
- **Evidence (VERIFIED):** 0.1056 vs 0.1163 is a gap of 0.011, while the dispersion across the 54 comparisons is at least 0.11 (`summary.json`). The histgb ceiling is 82.79 ± 0.37% (`tuned_metrics.json` → `1 − p_pred_below_limit`) vs a saturation point of 82.64%, a gap of 0.15 < 0.37.
- **Suggested fix:** Change both to no-difference statements.

### STATS-11: MINOR. The permutation control compares a paired difference with an unpaired between-seed std, on a single seed.
- **Anchor:** V.1, l.377: "The shuffled arm was lower than real F1 by ($2.39\times10^{-5}$), but this difference is small enough that it falls within normal seed variation…"
- **Evidence (Reported):** single-seed values, with a between-seed std of 7.58e-5. The three arms share one split, so the right yardstick is the std of the *paired* difference across seeds, which is usually much smaller. Measured that way, "shuffled beats real" could be a real effect, and a surprising one.
- **Suggested fix:** Run the three arms on all 5 seeds and report the mean ± std of the paired differences.

### STATS-12: MINOR. "Coverage" means two different things within one paragraph.
- **Anchor:** IV.1, l.231: "…provides the risk–coverage curve for selective prediction [14, 23] (where coverage is the acceptance rate)."
- **Evidence:** Everywhere else, "coverage" is the conformal quantity P(y ≥ lower). Fig. 2 plots missed rate and escalation against the conformal target. It is not the risk–coverage (risk versus acceptance) curve the sentence describes.
- **Suggested fix:** Use a different term for the acceptance rate (the paper already has "escalation"), and either plot the actual risk–acceptance curve (see STATS-02) or drop the claim.

---

## 3. Three strongest parts (protect these in revision)

1. **Nested, group-aware tuning with a genuinely untouched cal/test split.** III.2, l.124: "To tune the specific variables for each model, I split the training set again into three smaller parts…". Verified in `scripts/tune_surrogates.py:run_seed`: GroupShuffleSplit on `scenario_id`, the inner split drawn from train only, and feature selection on train only. All 10 model×seed test sweeps reproduce exactly from a fresh refit. That protocol is also what makes the held-out operating-point fix in STATS-01 a small change rather than new work.
2. **The safety-throughput trade-off reported as a negative result, with the full sweep and honest hedging.** Table 2 (l.231 ff.) and "although the error bars still reach up to about 1.0–1.07\%". The finding that ~1% misses costs ~60–65% escalation holds up under held-out selection (STATS-01) and under a risk-controlling calibration (STATS-05). Net speedup that charges the escalated solves, with the minimum solve time as a conservative choice (l.143 ff.), is correct accounting.
3. **Pre-registered, hash-locked cross-network prediction on disjoint cal/test, and the clip-artifact self-correction.** IV.4, l.355: "I locked and hashed the predictions before each target network's gate ran…". III.1, l.121: "The previous implementation of the dataset generator used a lower bound…". Reporting that the fitted predictor B does not beat the parameter-free A is exactly the kind of null a doctoral panel respects. Keep it, but report it with its n and its breakdown (STATS-07).

---

## 4. Open questions (not settled)

- Whether the base-case clustering also affects the case30 figures (300 test base cases, 7–20 misses per seed at 0.97) enough that "all five splits under 1%" is fragile. Not recomputed.
- Whether a scenario-level conformal score (one score per base case) would change the escalation floor materially. Not run.
- The Mondrian-by-element analysis (`data/mondrian_element_summary.json`) shows element-conditional calibration trading escalation for missed rate differently. I did not evaluate whether it belongs in the paper.
