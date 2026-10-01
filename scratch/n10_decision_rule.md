# N10 decision rule — DRAFT for owner review (not hashed, not in force)

Status: DRAFT written by Claude Code on 2026-09-30 at the owner's request.
- It becomes the pre-registration only after the owner approves it, commits and pushes it, and the N10 run
  (`scratch/run_prompt_n10.md`, Step 1) copies it unchanged to `scratch/n10_decision_rule.md` and hashes it.
- No N10 result exists when this draft is written.
- Stored-label numbers already on disk for case_illinois200 (`data/netstudy2/case_illinois200/frozen.json`)
  were seen when drafting: boundary mass 19.33%, violation rate 29.28%, histgb escalation 7.84% at 0.90. They
  are on the old labels and are not N10 results.

## Part A — independent-solver label check (item 10)

**Question.** Do the switch-back labels still hold when the network model and the Newton solver come from a
different package (MATPOWER under Octave) instead of pandapower?

**Rows.** The 200 rows of `data/sts_label_crosscheck_rows.parquet` (stratum `viol_to_safe` or `safe_to_viol`),
plus the named worst case (scenario 101000025, line 78). Each case is rebuilt as in
`scratch/label_crosscheck.py` and exported with `pandapower.converter.to_mpc`.

**Three MATPOWER solves per row:**
- **M0:** `runpf` with no Q limits.
- **M1:** `runpf` with `pf.enforce_q_lims = 1` (MATPOWER's one-way PV→PQ conversion).
- **M2:** MATPOWER NR inside a switch-back outer loop. A PQ-converted generator returns to PV when the voltage
  contradicts its limit: at Qmax with V > Vset, or at Qmin with V < Vset. Cap: 30 outer iterations.

Min voltage = min over buses that are not isolated.

**Pre-declared checks, each with an exact 95% Clopper-Pearson interval:**

| Check | Pass condition |
|---|---|
| A0, export fidelity | M0 min_vm within 1e-6 pu of pandapower's no-limit solve on ≥ 99% of rows |
| A1, one-way reproduces the original labels | M1 label = stored label on ≥ 95% of rows |
| A2, **primary** | M2 label = N2 label on ≥ 95% of rows, and the named worst case has M2 min_vm ≥ 0.94 |

- A2 is reported as CONFIRMED / NOT CONFIRMED.
- If A0 or A1 fails, A2 is reported but marked "export not validated".

## Part B — second network, case_illinois200 (item 9)

**Data.**
- `data/netstudy/case_illinois200/dataset.parquet`, as built by `scripts/netstudy.py` phase 1a: one RNG
  stream, seed 100; load window [0.87, 0.99]; voltage and thermal N-0 gate.
- Relabeled with the N2 switch-back method (a network-parameterized copy of `scripts/sts_n2_label_audit.py`).
- Rows whose corrected solve fails are dropped. If more than 0.5% of converged N-1 rows fail, stop and report.

**Evaluation.**
- **Protocol:** exactly the N5 protocol on the corrected labels: 5 outer splits (seeds 0-4); the full
  `scripts/tune_surrogates.py` search (15 ridge, 26 histgb candidates); M2 selection; held-out target =
  M2 `inner_cov_at`; refit on train; q̂ on cal; evaluate on test.
- **Primary model:** histgb. Ridge is reported only.
- **Static ranking:** violation frequency per outaged element over the train split.
- **Std rule:** a difference counts only if the gap exceeds the larger of the two stds (population std,
  ddof=0, 5 splits).
- **Rule-B budget and catch:** as defined in `scratch/n9_decision_rule.md` §1.

**BEATS-STATIC-IL (primary verdict).** It holds if:

    mean(gate catch) − mean(static catch at k_B) > max(std gate, std static)

at the held-out target, histgb, rule B. If it fails, it is not re-judged a different way.

**SAFER-IL (secondary verdict).** Histgb held-out missed ≤ 1% in ≥ 4 of 5 splits.

**Descriptive only (no verdict):**
- **Budget curve.** Budgets are declared as the same shares of contingencies per base case as N9's case118
  budgets: 10.8%, 21.5%, 30.6%, 47.8%, 64.5%, i.e. k = round(share × 245) = {26, 53, 75, 117, 158}. At each,
  report SURR, STATIC and ORACLE catch, the std-rule verdict, and the crossover.
- **Labels.** Flips (viol→safe, safe→viol); violation rate and boundary mass [0.94, 0.945), stored vs
  corrected.
- **Violation concentration.** Share of all test violations coming from the top-5 and top-10 outaged elements
  (ranked by train frequency), for Illinois and for case118 (D94, corrected labels).
- **Operator metric.** Share of test base cases with at least one missed violation at the held-out point,
  both networks.

## Part C — paper artifacts on corrected labels (no verdict)

Figures and JSON only, each with a manifest. No claims are made in this file about what they show.

## Commitments

- **Fixed:** no extra seeds, splits, budgets, std definitions or families after hashing.
- **Reported either way:** every verdict.
- **Deviations:** logged in `notes/overnight_status.md`, and the affected verdict is marked "with deviation".
- **Unchanged:** the N5 and N9 verdicts stay reported.
