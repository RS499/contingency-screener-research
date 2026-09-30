# N9 result — budget curve, shift test, three-build floor replication

## Prompt and provenance

- **Prompt:** `scratch/run_prompt_n9.md` (prompt section), run in-session on the Mac mini, 2026-09-29/30 UTC.
- **Report only.** No decision taken, no `.tex` edited, no git write.
  - The only existing files changed are appends to `notes/ai-prompt-log.md` and `notes/overnight_status.md`.
- **Numbers.** Every number below is read from the JSON files named here. Recompute from them; do not quote
  this file.
- **Deviations from the hashed rule:** none. No code was changed after hashing.

## Step 0 — Environment

- Python 3.13.11; pandapower 3.5.4, numpy 2.3.5, pandas 2.3.3, scikit-learn 1.7.2, pyarrow 21.0.0, numba 0.66.0.
  All match the N5 run.
- git HEAD at start: `8488e8c`.

## Step 1 — Pre-registration

- `scratch/n9_decision_rule.md` is a byte-for-byte copy of `scratch/n9_decision_rule_DRAFT.md`.
- **sha256:** `37a614def80e95df3a00746573933114b93e9402c36f81f7b1dc7c77b3a7fa01`, recorded 2026-09-29T23:17:06Z
  in `scratch/n9_decision_rule.sha256`.
- **Git timestamp:** the draft was committed in `fb64040` (2026-09-29T18:41:47-04:00, pushed). The working copy
  is identical to that commit.
- Hashed before any N9 model fit or N9 number.
- `scratch/n9_shift.py` re-verified the hash before applying the verdict.

## Step 2 — Relabel D95b (`data/sts_n5_floor095_seed200.parquet`)

- **Driver:** `scratch/n9_relabel.py`. Output: `data/sts_n9_relabel095_seed200.{parquet,json}` plus manifest.
- **Checks, all pass:**
  - the replay reproduces all 1,500 stored N-0 minima exactly (rejects 537, matching the build);
  - the pinned re-solve reproduces every stored min_vm exactly;
  - failed rows: 0 of 278,957.
- **Label flips at 0.94:** viol→safe 4,474; safe→viol 784.
  - Violation rate: stored 15.991% → corrected 14.668%.
- **The 0.598 pu row** (scenario 202000172, line 78 out):
  - 5 generators are at their limit with a contradicting voltage;
  - corrected min_vm 0.949 pu, so it is **not a violation** after relabel;
  - line 78 is also the outage in N2's named worst case.

## Step 3 — Part 1, budget curve (descriptive, no verdict)

- **Script and output:** `scratch/n9_budget_curve.py` → `data/sts_n9_budget_curve.json`. The full k = 1..186
  curves are saved there.
- **N5 reproduction:** all 20 (dataset, seed, family) cells are exact (test MAE, held-out escalation, missed),
  not only seed 0.

### Histgb catch at k per base case, mean ± std over 5 splits

| Data | k | SURR | STATIC | ORACLE | Std rule |
|---|---|---|---|---|---|
| D94 | 20 | 65.11 ± 0.91 | 62.20 ± 0.83 | 65.90 | SURR higher |
| D94 | 40 | 93.46 ± 1.26 | 86.76 ± 1.09 | 96.94 | SURR higher |
| D94 | 57 | 95.73 ± 1.14 | 94.16 ± 1.09 | 98.62 | SURR higher |
| D94 | 89 | 96.71 ± 0.91 | 97.83 ± 0.87 | 99.16 | STATIC higher |
| D94 | 120 | 97.97 ± 0.61 | 98.89 ± 0.57 | 99.43 | STATIC higher |
| D95a | 20 | 71.68 ± 1.37 | 67.85 ± 1.28 | 72.68 | SURR higher |
| D95a | 40 | 95.57 ± 1.12 | 92.13 ± 1.23 | 97.32 | SURR higher |
| D95a | 57 | 96.83 ± 0.95 | 96.18 ± 1.02 | 98.28 | tie |
| D95a | 89 | 97.49 ± 0.72 | 98.09 ± 0.72 | 98.86 | tie |
| D95a | 120 | 98.34 ± 0.48 | 98.92 ± 0.49 | 99.23 | STATIC higher |

- **Crossover** (smallest declared k where SURR is no longer higher): D94 k = 89; D95a k = 57.
- **Ridge:** a tie at every declared k on both datasets.
  - Unverified reading: ridge is additive in the branch one-hots, so its within-base-case order is the same
    in every scenario, i.e. a static-type ranking.

## Step 4 — Part 2, shift test (the verdict)

- **Script and output:** `scratch/n9_shift.py` → `data/sts_n9_shift.json`.
- **Feature alignment:** 0 D94 columns are missing in D95a.

### SHIFT-ADVANTAGE: NO

D94 → D95a, histgb, held-out target, rule B:
- gate catch 97.24 ± 1.34% vs static 97.06 ± 1.42%;
- the gap of 0.18 pp is not > STD 1.42 pp.

Per the rule, this is not re-judged a different way.

### Reported alongside (no verdict)

| Direction, family | Gate catch | Static catch (k_B) | Missed ≤ 1% | Coverage vs target |
|---|---|---|---|---|
| D94→D95a histgb | 97.24 ± 1.34 | 97.06 ± 1.42 | 0 / 5 | 0.965 vs 0.960 |
| D94→D95a ridge | 98.13 ± 0.35 | 99.11 ± 0.35 | 0 / 5 | 0.943 vs 0.936 |
| D95a→D94 histgb | 98.56 ± 0.43 | 98.56 ± 0.70 | 1 / 5 | 0.916 vs 0.974 |
| D95a→D94 ridge | 98.10 ± 1.22 | 99.33 ± 0.32 | 1 / 5 | 0.913 vs 0.948 |

- **Histgb D94→D95a detail:** solve share B 39.1 ± 4.4%; missed 2.76 ± 1.34%.
- **Degradation vs D95a→D95a:** gate −1.64 ± 1.47 pp; static −0.21 ± 0.13 pp at the same k_B.
- **Coverage under shift:** coverage holds forward (D94→D95a) but falls well short of target in reverse
  (D95a→D94).

## Step 5 — Third build and Part 3 replication (descriptive)

- **Build D95c:** `scratch/n9_build_seed300.py`, seeds 300-303, same invocation as build 2. Output:
  `data/sts_n9_floor095_seed300.{parquet,json}` plus manifest.
  - Wall 858 s; nonconverged rows 50; N-0 gate pass 73.82%.
- **Relabel D95c:** `scratch/n9_relabel.py` → `data/sts_n9_relabel095_seed300.*`.
  - All checks pass; failed 0.
  - Flips: viol→safe 4,680; safe→viol 699.
  - Deepest stored row (scenario 300000007, trafo 0 out) goes from 0.658 pu to 0.909 pu corrected, so it is
    **still a violation**.
- **Replication:** `scratch/n9_replication.py` → `data/sts_n9_floor_replication.json`. It re-verified the N3
  prediction hash (`9975a07e…`).

| Build | BM stored | CBM stored | VR stored | BM corrected | CBM corrected | VR corrected | In N3 range (BM/CBM/VR) |
|---|---|---|---|---|---|---|---|
| D95a (100-103) | 32.954 | 39.234 | 16.006 | 28.641 | 33.690 | 14.987 | yes / yes / yes |
| D95b (200-203) | 34.817 | 41.444 | 15.991 | 30.676 | 35.949 | 14.668 | yes / yes / yes |
| D95c (300-303) | 34.911 | 41.581 | 16.041 | 29.957 | 35.084 | 14.613 | yes / yes / yes |
| Mean ± std (ddof=0) [ddof=1] | 34.23 ± 0.90 [1.10] | 40.75 ± 1.08 [1.32] | 16.01 ± 0.02 [0.03] | 29.76 ± 0.84 [1.03] | 34.91 ± 0.93 [1.14] | 14.76 ± 0.17 [0.20] | |

- n = 3 builds of one network (case118).

## Files written

- **scratch:** `n9_decision_rule.{md,sha256}`, `n9_relabel.py`, `n9_budget_curve.py`, `n9_shift.py`,
  `n9_build_seed300.py`, `n9_replication.py`, `n9_result.md`, the `*.log` files (git-ignored), and the shard
  dirs `n9_relabel_seed200_shards/`, `n9_relabel_seed300_shards/`, `n9_seed300_shards/` (intermediate; not for
  commit).
- **data**, each with a manifest:
  - `sts_n9_relabel095_seed200.{parquet,json}`
  - `sts_n9_budget_curve.json`
  - `sts_n9_shift.json`
  - `sts_n9_floor095_seed300.{parquet,json}`
  - `sts_n9_relabel095_seed300.{parquet,json}`
  - `sts_n9_floor_replication.json`
