# N12 result — conditional-history baseline, price of a guarantee, cross-network table

## Prompt and provenance

- **Prompt:** `scratch/run_prompt_n12.md` (prompt section), run in-session on the Mac mini, 2026-10-02 UTC. The
  run includes the no-question rules 1-4.
- **Report only.** No decision taken, no `.tex` edited, no git write.
  - The only existing files changed are appends to `notes/ai-prompt-log.md` and `notes/overnight_status.md`.
- **Numbers.** Every number below is read from the JSON files named here. Recompute from them; do not quote
  this file.

## Step 0 — Environment

- Python 3.13.11; pandapower 3.5.4, numpy 2.3.5, pandas 2.3.3, scikit-learn 1.7.2, pyarrow 21.0.0, numba 0.66.0.
  All match N11.
- git HEAD `d5744e6` (= origin/main).

## Step 1 — Pre-registration

- `scratch/n12_decision_rule.md` is a byte-for-byte copy of the draft committed in `d5744e6`
  (2026-10-01T23:18:15-04:00).
- **sha256:** `8d11714cba7a5aa1f65e209e37438e4f1b3f99cb49820b2937f421d6a5aead50`, recorded 2026-10-02T03:18:58Z,
  before any N12 computation.
- The hash was re-verified in code before and after the verdict computation, and in Parts B and C. It never
  failed.

## Step 2 — Loaders and reproduction check

- **Script and evidence:** `scratch/n12_loaders.py` → `scratch/n12_repro_check.json`.
- **Loaders:** every network is loaded with `n5_gate_eval.load_relabeled`, the function the N5, N10 and N11 gate
  scripts call.
- **Result:** the per-split fixed-budget static catch at k_B (histgb, held-out) is reproduced **exactly in 5/5
  splits for all 4 networks**. No network was stopped.

## Part A — Conditional-history baseline (verdict)

- **Script and output:** `scratch/n12_condhist.py` → `data/sts_n12_condhist.json`. No model is fit.
- **Settings:**
  - 5 margin bins: quintiles of n0_min_vm − 0.94 over the train base cases.
  - Smoothing a = 10.
  - Global budget N = round(s_B × n_test), where s_B is the stored gate's rule-B solve share.
  - Ties broken by element index, then scenario_id.

### GATE-BEATS-CONDHIST (primary, case_illinois200): YES

- Gate catch 99.04 ± 0.22% vs COND-HIST 97.94 ± 0.97%.
- The gap of 1.10 pp exceeds STD 0.97 pp, a narrow margin.

| Network | Gate catch | COND-HIST | GLOBAL-STATIC | Fixed-budget static | Gap vs STD | Gate beats COND-HIST? |
|---|---|---|---|---|---|---|
| case118 | 98.49 ± 1.35 | 99.06 ± 0.80 | 98.82 ± 0.81 | 98.82 ± 0.81 | −0.57 vs 1.35 | no (tie) |
| **case_illinois200** | 99.04 ± 0.22 | 97.94 ± 0.97 | 88.62 ± 1.20 | 88.90 ± 1.20 | 1.10 vs 0.97 | **yes** |
| case30_thermal | 99.37 ± 0.31 | 89.44 ± 3.90 | 83.44 ± 4.55 | 84.09 ± 4.00 | 9.93 vs 3.90 | yes |
| case24_ieee_rts | 99.02 ± 0.18 | 94.62 ± 0.72 | 92.44 ± 1.22 | 92.48 ± 1.15 | 4.40 vs 0.72 | yes |

- **Count:** the gate beats COND-HIST on 3 of 4 networks. This is reported, not part of the primary verdict.
- **GLOBAL-STATIC vs fixed-budget static:** within 0.65 pp on every network. Moving to a global budget changes
  little; COND-HIST's gain over static comes from the margin conditioning.

## Part B — Price of a guarantee (descriptive)

- **Script and output:** `scratch/n12_guarantee.py` → `data/sts_n12_guarantee.json`.
- **Refits:** all 20 (2 networks × 2 families × 5 splits) reproduce the stored held-out escalation and missed
  exactly.
- **Precedence:** 0 rows were both certified and flagged, so the precedence convention never applied.

Each cell is mean ± std over 5 splits, in the order global-q̂ (held-out) / row-level α = 0.01 / base-level
any-miss α = 0.10.

| Network, family | Escalation (%) | Missed (%) | Any-miss share of base cases (%) | Speedup A | Speedup B |
|---|---|---|---|---|---|
| case118 histgb | 50.2±8.4 / 52.7±3.0 / 60.0±1.8 | 1.51±1.35 / 1.22±0.70 / 0.48±0.13 | 17.1±7.2 / 14.6±2.8 / 8.1±1.0 | 2.06 / 1.90 / 1.66 | 1.55 / 1.46 / 1.32 |
| case118 ridge | 59.5±2.2 / 57.9±3.4 / 59.9±2.5 | 1.82±0.59 / 1.98±0.39 / 1.74±0.50 | 11.4±2.2 / 12.7±3.7 / 11.1±2.8 | 1.68 / 1.73 / 1.67 | 1.22 / 1.24 / 1.21 |
| Illinois histgb | 10.7±2.2 / 9.9±1.7 / 19.6±3.6 | 0.96±0.22 / 1.03±0.14 / 0.37±0.08 | 23.9±4.9 / 24.9±3.8 / 10.1±3.5 | 9.64 / 10.25 / 5.24 | 3.12 / 3.20 / 2.46 |
| Illinois ridge | 19.5±1.6 / 17.6±2.6 / 35.0±2.6 | 0.83±0.11 / 0.96±0.18 / 0.30±0.06 | 20.4±3.5 / 23.5±3.1 / 8.1±1.3 | 5.16 / 5.79 / 2.88 | 2.42 / 2.54 / 1.76 |

- **Splits with test any-miss ≤ 0.10** (base-level): case118 histgb 5/5, ridge 3/5; Illinois histgb 3/5, ridge
  5/5.
- **Splits with test missed ≤ 0.01** (row-level): case118 histgb 3/5, ridge 0/5; Illinois histgb 3/5, ridge 2/5.
- **Caveat (row-level):** rows within a base case are not exchangeable, so α = 0.01 is not a per-row guarantee.
- **Guarantee (base-level):** P(any certified violation in a new base case) ≤ α holds only under base-case
  exchangeability. It is a finite-sample, marginal statement.

## Part C — Cross-network table (descriptive; n = 4, no law claimed)

- **Script and output:** `scratch/n12_crossnet.py` → `data/sts_n12_crossnet.json`.

| Network | Rows | BM [0.94, 0.945) | VR | Risk spread (std of per-base viol. share) | Top-10 share | Gate | Fixed static | COND-HIST | GLOBAL-STATIC |
|---|---|---|---|---|---|---|---|---|---|
| case118 | 278,954 | 56.22% | 16.60% | 0.056 ± 0.015 | 32.9 ± 0.5% | 98.49 | 98.82 | 99.06 | 98.82 |
| case_illinois200 | 360,589 | 14.31% | 21.66% | 0.128 ± 0.007 | 18.4 ± 1.3% | 99.04 | 88.90 | 97.94 | 88.62 |
| case30_thermal | 61,500 | 7.10% | 15.38% | 0.082 ± 0.004 | 89.5 ± 0.7% | 99.37 | 84.09 | 89.44 | 83.44 |
| case24_ieee_rts | 54,648 | 20.94% | 47.88% | 0.209 ± 0.008 | 51.5 ± 0.4% | 99.02 | 92.48 | 94.62 | 92.44 |

- **Cross-check:** the top-10 concentration for case118 and Illinois equals the N10 values (32.9%, 18.4%).

## Interpretations and deviations

- **None.** No check failed, no network or part was stopped, and no code fix was needed after hashing.
- **Implementation conventions,** fixed in code before any N12 computation and recorded in the JSON settings:
  - quintile edges use numpy's default (linear) `np.quantile`; bin = number of edges ≤ m_b;
  - unseen (element, bin) cells fall back to f_e through the smoothing formula (v = n = 0);
  - an element never seen in train gets f_e = 0;
  - "certify iff pred ≥ L + t" is used as written; t = +inf if the conformal rank exceeds n;
  - certify takes precedence where certify and flag overlap, as in `gate_eval`. It never occurred.
- **Code style:** before any run, one generator expression in a print statement of `n12_guarantee.py` was
  replaced with a loop. Not a method change.

## Files written

- **scratch:** `n12_decision_rule.{md,sha256}`, `n12_loaders.py`, `n12_repro_check.json`, `n12_condhist.py`,
  `n12_guarantee.py`, `n12_crossnet.py`, `n12_result.md`.
- **data,** each with a manifest: `sts_n12_condhist.json`, `sts_n12_guarantee.json`, `sts_n12_crossnet.json`.
