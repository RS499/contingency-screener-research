# N12 decision rule — DRAFT for owner review (not hashed, not in force)

Status: DRAFT written by Claude Code on 2026-10-01 at the owner's request.
- It becomes the pre-registration only after the owner approves it, commits and pushes it, and the N12 run
  (`scratch/run_prompt_n12.md`, Step 1) copies it unchanged to `scratch/n12_decision_rule.md` and hashes it.
- The gate and fixed-budget static numbers it refers to already exist (N5, N10, N11). The conditional-history
  baseline (Part A) and the guarantee runs (Part B) do not exist when this is written.

## 0. Common definitions

- **Labels, splits, std rule.** Exactly as in N5, N10 and N11:
  - switch-back corrected labels, with failed rows dropped;
  - outer splits `make_splits(groups, seed)`, seeds 0-4;
  - population std (ddof=0);
  - a difference counts only if it exceeds the larger of the two stds.
- **Networks and their existing gate results** (histgb, held-out target, rule B):

  | Network | Data | Labels | Gate source |
  |---|---|---|---|
  | case118 (0.94 floor) | `data/dataset.parquet` | `data/sts_n2_label_audit.parquet` | `data/sts_n5_gate_094.json` |
  | case_illinois200 | `data/netstudy/case_illinois200/dataset.parquet` | `data/sts_n10_relabel_illinois200.parquet` | `data/sts_n10_illinois.json` |
  | case30_thermal | `data/case30_thermal/dataset.parquet` | `data/sts_n11_relabel_case30_thermal.parquet` | `data/sts_n11_smallnets.json` |
  | case24_ieee_rts | `data/netstudy/case24_ieee_rts/dataset.parquet` | `data/sts_n11_relabel_case24_ieee_rts.parquet` | `data/sts_n11_smallnets.json` |

- **Gate numbers are reused, not recomputed:** per split, the gate's rule-B solve share s_B and its catch.
  Before any new number, each network's loader must reproduce its existing per-split fixed-budget static catch
  at k_B exactly. That proves the splits and labels are identical.

## 1. Part A — conditional-history baseline (VERDICT)

**Question.** Does the gate still beat a no-ML baseline once that baseline may also spend more solves on
riskier operating conditions?

**COND-HIST ranking.** A lookup table; no model is fit.
1. **Margin bins.** Each base case's pre-outage margin is m_b = n0_min_vm − 0.94. Bins are the quintiles of
   m_b over the split's train base cases (5 bins; the edges come from train only).
2. **Score** for (base b, element e):

       p(e, bin(b)) = (v + a · f_e) / (n + a)

   - v and n are the violations and rows of element e in bin(b) over the train split;
   - f_e is element e's overall train violation frequency;
   - a = 10 (shrinks sparse cells toward f_e).
3. **Budget.** Same total solves as the gate: N = round(s_B × n_test). The N test rows with the highest score
   across all test base cases are solved. Ties are broken by element index, then scenario_id. The budget is
   global, so a riskier base case can receive more solves.
4. **COND-HIST catch** = true violations among the solved rows / all test true violations.

**Also reported** (no verdict): GLOBAL-STATIC, the same global budget ranked by f_e alone. It shows how much
of any gain comes from the global budget itself vs. the margin conditioning.

**GATE-BEATS-CONDHIST, per network.** It holds if

    mean_split(gate catch) − mean_split(COND-HIST catch) > max(std gate, std COND-HIST)

at histgb, held-out target, rule B.
- **Primary verdict:** case_illinois200, the network where the gate beat the fixed-budget static ranking (N10).
- **Reported, not part of the primary verdict:** the other three networks, and a count of how many of the 4
  networks the gate beats COND-HIST on.

## 2. Part B — the price of a guarantee (descriptive, no verdict)

**Networks:** case118 (0.94) and case_illinois200. Histgb and ridge.
- The N5/N10 M2 configs are refit per split on train, with no re-search.

Two calibrations of the certify threshold t (certify iff pred ≥ L + t; flag iff pred < L), both on the cal
split:
1. **Row-level, α = 0.01:**
   - t is the ⌈(n_v + 1)(1 − α)⌉-th smallest value of (pred − L) over the cal violation rows (n_v of them),
     as in N1.
   - Report its caveat: rows within a base case are not exchangeable.
2. **Base-level any-miss, α = 0.10:**
   - For each cal base case with ≥ 1 violation, m_b = max over its violation rows of (pred − L).
   - t is the ⌈(n_b + 1)(1 − α)⌉-th smallest m_b.
   - Under base-case exchangeability, P(a new base case has any certified violation) ≤ α.

Reported on test for each: escalation, flag share, missed rate, any-miss share of base cases, speedup A and B,
and the comparison with the held-out global-q̂ gate.

## 3. Part C — cross-network summary (descriptive, no verdict)

One table over the 4 networks. Columns:
- corrected boundary mass and violation rate;
- the spread of risk across base cases (std over test base cases of the per-base violation share);
- violation concentration (top-10 elements' share);
- gate catch, fixed-budget static catch, COND-HIST catch and GLOBAL-STATIC catch.

n = 4, so no correlation or law is claimed.

## 4. Commitments

- **Fixed:** no extra seeds, bins, smoothing values or networks after hashing.
- **Reported either way:** every verdict.
- **Deviations:** logged in `notes/overnight_status.md`, and the verdict is marked "with deviation".
- **Unchanged:** the N5, N9, N10 and N11 verdicts stay reported.
