# N11 decision rule — DRAFT for owner review (not hashed, not in force)

Status: DRAFT written by Claude Code on 2026-09-30 at the owner's request.
- It becomes the pre-registration only after the owner approves it, commits and pushes it, and the N11 run
  (`scratch/run_prompt_n11.md`, Step 1) copies it unchanged to `scratch/n11_decision_rule.md` and hashes it.
- **The predictions in §3 are Claude's, written before any N11 data exists.** Edit them before committing
  if you would predict differently: the pre-registration should be yours.

## 0. Common definitions (same as N5/N9 unless stated)

- **Limit and labels.** L = 0.94 pu. Labels are the PV/PQ switch-back corrected min_vm (N2 method,
  `scripts/sts_n2_label_audit.py` logic); violation = corrected min_vm < L. Failed corrected solves are
  dropped and counted. If more than 0.5% of a dataset's converged rows fail, that part stops and reports.
- **Std.** Population std (ddof=0) over splits (seeds 0-4) unless stated. **Std rule:** a difference counts
  only if the gap exceeds the larger of the two stds.
- **Models.** Primary model histgb; ridge reported.
  - On case118 0.94-floor data (D94), M2 configs and held-out targets are taken unchanged from
    `data/sts_n5_gate_094.json`. They are refit on the split's train rows, and q̂ is calibrated on its cal rows.
  - **Rule B** (flagged cases also solved), gate catch = 1 − missed, and static catch at matched k_B are as
    in `scratch/n9_decision_rule.md` §1.

## 1. Part 1 — N-1 → N-2 coverage (project research question 1): VERDICT

**N-2 sample.**
- For every accepted base case of D94 (1,500), draw 50 unordered pairs of distinct in-service branches,
  uniformly at random, with numpy seed 20261001. The pairs are drawn once and are the same for every split.
- Each pair is solved with both branches out: pinned solver plus the N2 switch-back loop.
- Rows whose pinned solve does not converge are kept as "N-2 nonconverged" and reported separately; they
  are not in the coverage or missed denominators.

**Features.**
- Each N-2 row's scenario features are copied from that base case's rows in `data/dataset.parquet`.
- The branch one-hot has a 1 in both outaged branches' columns ("two-hot").
- No model is refit on N-2 data; the models are exactly the N-1 models described in §0.

**Evaluation per split.**
- The split's N-1 q̂ is applied to the N-2 rows of that split's test base cases.
- Measured: empirical coverage P(y ≥ pred − q̂), missed rate, escalation, flag share and speedup A/B. This is
  done at target 0.90 and at the held-out target.

**COVERAGE-HOLDS-N2 (primary verdict).** Histgb at target 0.90. It holds if

    mean_split(coverage_N2) ≥ 0.90 − max(std_split(coverage_N2), std_split(coverage_N1))

where coverage_N1 is the same split's N-1 test coverage at 0.90 (from N5). Otherwise it is reported as
"coverage does not hold under N-2", together with the size of the shortfall.

**Reported without a verdict:**
- the same check at the held-out target;
- ridge;
- missed-rate ≤ 1% counts (out of 5 splits);
- the N-2 violation rate and nonconverged share;
- coverage split by whether the pair's two branches are adjacent (share a bus).

## 2. Part 6 — per-element (Mondrian) calibration vs static ranking: VERDICT

**Mondrian gate** on D94.
- For each split and each outaged element, a separate one-sided q̂_e is calibrated on that element's cal rows
  at the same held-out target as §0 (the N5 `m2_inner_cov_at`), with the same finite-sample rank.
- If an element has fewer than 20 cal rows, it uses the global q̂.
- Certify / flag / escalate as before, with q̂_e.

**MONDRIAN-BEATS-STATIC (verdict).** Histgb, held-out target, rule B. It holds if

    mean(Mondrian gate catch) − mean(static catch at the Mondrian gate's k_B) > max(std gate, std static)

Reported alongside: the global-q̂ gate's numbers (from N5), escalation, missed, speedup B, and ridge.

## 3. Part 3 — generator voltage floor dose-response: PREDICTION + VERDICT

**Builds.**
- Two new case118 builds, identical to the N3 driver (`scratch/n3_floor_rebuild.py`: committed invocation,
  seeds 100-103, N-0 gate at 0.94). The only change is GEN_VM_LO = 0.93 and GEN_VM_LO = 0.96.
- Both are relabeled with the switch-back method.
- The existing 0.94 build (D94) and 0.95 build (D95a) complete the four levels.

**Predictions** (stored labels, converged N-1 rows; BM = share in [0.94, 0.945), CBM = BM / share ≥ 0.94,
VR = share < 0.94):

| Floor | BM point [range] | CBM point [range] | VR point [range] | Reasoning |
|---|---|---|---|---|
| 0.93 | 55% [50-62] | 67% [62-73] | 17.5% [15.5-19.5] | The N-0 gate at 0.94 still rejects bases whose low-scheduled units sit below 0.94, so the accepted distribution should look like the 0.94 build (a floor below the limit does little) |
| 0.96 | 20% [8-30] | 24% [10-36] | 15.0% [12-17.5] | Continues the 0.94 → 0.95 drop: low-scheduled units forced further above the limit |

**FLOOR-DOSE-RESPONSE (verdict).** It holds if both of these are true (stored labels):
1. BM(0.96) < BM(0.95 build D95a) − 5 pp.
2. |BM(0.93) − BM(0.94)| ≤ 5 pp.

This tests "a floor above the limit reduces boundary mass; a floor below it does not". The same numbers on
corrected labels are reported alongside.

## 4. Descriptive parts (no verdict)

- **Part 2, corrected labels on the small networks.** case30_thermal (`data/case30_thermal/dataset.parquet`),
  case39 and case24_ieee_rts (`data/netstudy/<net>/dataset.parquet`) are relabeled with switch-back, then the
  N5 protocol is run on each (full tuning search, held-out target). Reported:
  - flips, corrected BM and VR;
  - the gate at 0.90 and at the held-out point, with speedup A/B and gate vs static at k_B;
  - escalation vs ρ·q̂ on corrected labels, as in `data/netstudy2/cross_2a_points.json`.

  For case30, the numbers the abstract quotes (histgb @0.97, the first mean-missed crossing) are recomputed
  on corrected labels.
- **Part 4, classical screen on corrected labels.** The committed linearized screen
  (`data/classical_predictions.parquet` → pred_min_vm) is re-scored against D94 corrected labels: conformal at
  target 0.90, the same splits; MAE, R², escalation, missed, speedup (with the classical timing accounting
  in `data/classical_screen_metrics.json`). No new solves.
- **Part 5, gate on the other 0.95 builds.** The N5 protocol (full search) on D95b (seeds 200-203) and D95c
  (seeds 300-303), using their N9 relabels.
  - Report the held-out histgb numbers per build, and mean ± std across the three 0.95 builds.
  - Report what the N5 SAFER and FASTER rules would give on each build, labeled "replication of N5 rule,
    not a new verdict".
- **Part 7, solver re-timing.** The N6 warm-start timing logic, run with the load average below 2.0 at start
  (wait up to 30 minutes for it, otherwise run anyway and record the load). Report cold and warm min/median
  per solve and per 186-outage sweep, next to `data/solve_time.json` (`ms_solver` 9.14, `median_ms` 9.512).

## 5. Commitments

- **Fixed:** no extra seeds, splits, pairs, floors or std definitions after hashing.
- **Reported either way:** every verdict.
- **Deviations:** logged in `notes/overnight_status.md`, and the affected verdict is marked "with deviation".
- **Unchanged:** the N5, N9 and N10 verdicts stay reported.
