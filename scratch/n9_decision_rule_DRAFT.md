# N9 decision rule — DRAFT for owner review (not hashed, not in force)

Status: DRAFT written by Claude Code on 2026-09-29 at the owner's request.
- It becomes the pre-registration only after the owner has edited it (optional), approved it, and the N9 run
  (`scratch/run_prompt_n9.md`, Step 1) has copied it unchanged to `scratch/n9_decision_rule.md` and hashed it.
- Recommended: the owner also commits and pushes the approved file before the run starts. That gives the
  pre-registration a git timestamp, which N5's lacked.
- No N9 result exists when this draft is written.

## 0. What N9 asks

1. **Budget curve (descriptive, no verdict).** At which solve budgets does ranking contingencies by the
   surrogate's prediction catch more violations than the static training-frequency ranking? The data on disk
   (stored labels, `data/baselines.json`) suggest histgb wins at small budgets and loses at large ones. N9
   measures this on switch-back (corrected) labels.
2. **Shift test (verdict).** When the gate and the static ranking are both built on the 0.94-floor data and
   applied to the 0.95-floor data, does the gate catch more violations than the static ranking at a matched
   solve budget?
3. **Replication of the floor effect (descriptive).** Boundary mass and violation rate over 2-3 independent
   0.95-floor builds, on corrected labels.

## 1. Fixed definitions

- **Limit L** = 0.94 pu everywhere. The std convention is population std (ddof=0) over the 5 outer splits,
  unless stated otherwise.
- **Datasets and labels.** Every label is the PV/PQ switch-back corrected min_vm (the N2 method,
  `scripts/sts_n2_label_audit.py`), and violation = corrected min_vm < L. Rows whose corrected solve failed are
  dropped and counted. If more than 0.5% of a dataset's N-1 rows fail, the run stops and reports.

  | Name | Data | Labels |
  |---|---|---|
  | D94 | `data/dataset.parquet` | `data/sts_n2_label_audit.parquet` |
  | D95a | `data/sts_n3_floor095.parquet` (seeds 100-103) | `data/sts_n5_relabel095.parquet` |
  | D95b | `data/sts_n5_floor095_seed200.parquet` (seeds 200-203) | relabeled in N9 Step 2 |
  | D95c | third 0.95 build, seeds 300-303 | N9 Step 5, only if Steps 0-4 finish |

- **Splits.** Outer splits are `make_splits(groups, seed)` for seeds 0-4 (60/20/20 by scenario). Each
  dataset's groups are its own scenario_ids.
- **Models.** Primary model: histgb. Ridge is reported and not used for the verdict.
  - For D94 and D95a, the M2 configuration and the held-out target of each split are taken unchanged from
    N5 (`data/sts_n5_gate_094.json` and `data/sts_n5_gate_095.json` → `selections`). No re-search.
  - The model is refit on the split's train rows with that configuration (`scripts/tune_surrogates.py`
    `fit_one`), and q̂ is calibrated on the cal rows (`feasibility/gate_eval.py` `calibrate_qhat`).
- **Rankings** (within each test base case, over its converged contingencies; `scripts/baselines.py`
  machinery):
  - **SURR:** ascending predicted min_vm (lowest predicted voltage solved first).
  - **STATIC:** descending violation frequency per outaged element over the train rows of the dataset the
    ranking was built on. Ties go by element index.
  - **ORACLE:** ascending true min_vm (upper bound, reported only).
- **Catch at budget k** = true violations among each test base case's top-k, summed over test base cases,
  divided by all test violations (pooled; the `baselines.py` definition).
- **Gate at an operating point.**
  - Certify = pred − q̂ ≥ L; flag = pred < L; escalate = otherwise.
  - Rule-B solve share = (escalated + flagged) / n. Rule-B catch = 1 − (certified true violations / true
    violations).
  - Matched static budget k_B = round(rule-B solve share × mean converged rows per test base case), computed
    per split. This is the `scratch/matched_budget.py` definition.

## 2. Part 1 — budget curve (descriptive; no verdict)

- **Datasets and models:** D94 and D95a, both models.
- **Budgets declared in advance:** k ∈ {20, 40, 57, 89, 120} contingencies per base case (out of ~186). The
  full k = 1..186 curve is saved but not used for any claim.
- **Reported:** catch ± std for SURR, STATIC and ORACLE at each declared k.
- **Std-rule verdict per k:** "SURR higher", "STATIC higher" or "tie", where a difference counts only if the
  gap exceeds the larger of the two stds.
- **Crossover budget:** the smallest declared k at which SURR is no longer higher. This is descriptive only.

## 3. Part 2 — shift test (the verdict)

- **Train side:** D94, splits 0-4. Refit, calibration and static frequency table all use D94 train and cal
  rows only. The held-out target is the D94 N5 selection (`m2_inner_cov_at`), chosen on D94's inner split.
- **Test side:** the D95a test split for the same seed, `make_splits(D95a groups, seed)["test"]`. No D95a row
  is used for fitting, calibrating, choosing the target or building the static table.
- **Measured per split,** at the held-out target (histgb): rule-B solve share, gate catch, static catch at
  k_B (static table from D94 train), missed rate, and empirical coverage on D95a test.

### SHIFT-ADVANTAGE (primary verdict)

It holds if:

    mean_split(gate catch) − mean_split(static catch) > max(std_split(gate catch), std_split(static catch))

on D94 → D95a, histgb, held-out target, rule B. This is the same std rule as N5's FASTER clause 2. It is
**not** replaced by a paired or per-split comparison if it fails.

### Reported alongside, not part of the verdict

- **In-distribution references,** already on disk from N5: D94 → D94 and D95a → D95a, gate vs static.
- **Degradation.**
  - Gate: shifted catch − D95a → D95a catch.
  - Static: shifted catch − D95a → D95a catch at the same k_B.
  - Both as mean ± std, with no verdict.
- **Missed rate under shift:** histgb splits with missed ≤ 1% (count out of 5), and empirical coverage vs
  the target.
- **Reverse direction** (D95a → D94) and ridge, both directions, with the same definitions and no verdict.

## 4. Part 3 — floor replication (descriptive)

- **Per build:** BM = share of converged N-1 rows in [0.94, 0.945); CBM = BM / share ≥ 0.94; VR = share < 0.94.
  Each is computed on stored labels and on corrected labels.
- **Across builds** (D95a, D95b and, if built, D95c): mean ± std, ddof=0 and ddof=1.
- **Compared with the hashed N3 prediction** (`scratch/n3_floor_prediction.md`, sha256 `9975a07e…`): BM 33%
  [20-45], CBM 40% [28-55], VR 15.5% [12-18] on stored labels. For each build: in or out of range.
- **Build D95b's 0.598 pu minimum:** after relabel, report its corrected value and whether it is still a
  violation.

## 5. Commitments

- **Fixed:** no additional seeds, splits, budgets, std definitions, or model families after hashing.
- **Reported either way:** the SHIFT-ADVANTAGE result and every Part 1 verdict, favourable or not. The N5
  verdict (SAFER no, FASTER no) stays reported regardless of N9.
- **Deviations:** any code change needed after hashing is recorded in `notes/overnight_status.md` with the
  reason, and the verdict is marked "with deviation".
