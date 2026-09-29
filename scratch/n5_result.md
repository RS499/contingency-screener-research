# N5 result — back-switch relabel, gate re-evaluation, pre-registered verdict

## Prompt and provenance

- **Prompt:** `scratch/run_prompt_n5b.md`, run by Claude Code, 2026-09-29 UTC. It is the owner's revision of
  `run_prompt_n5.md`.
- **Report only.** No decision taken, no `.tex` edited, no git write, no existing data file changed.
- **Numbers.** Every number below is read from the JSON files named here. Recompute from those files; do not
  quote this file.

## Step 0 — Environment check: PASSED

- The rebuild of shard seed 100 (of 100-103; 375 scenarios, 70,125 rows × 634 columns) is **byte-identical**
  to the seed-100 rows of `data/dataset.parquet`.
  - Check: sha256 of every column array; `DataFrame.equals` True.
  - Rejects: 375 accepted, 370 rejected.
  - Wall time: 928 s.
- Evidence: `scratch/n5_step0_envcheck.json`, produced by `scratch/n5_step0_envcheck.py`.
- Interpreter: Python 3.13.11, while the build manifests record 3.13.9. All pinned packages match
  (pandapower 3.5.4, numpy 2.3.5, pandas 2.3.3, scikit-learn 1.7.2, pyarrow 21.0.0, numba 0.66.0). The
  patch-level difference does not change the build.

## Step 1 — Pre-registration

- **File:** `scratch/n5_decision_rule.md`.
- **sha256:** `84239071721caded377c5a1e714a1f63e6525e0d5307ade9260b1c8b19dd8e67`, recorded 2026-09-29T00:11:30Z
  in `scratch/n5_decision_rule.sha256`.
- **When:** written before any N5 surrogate was trained. `scratch/n5_summarize.py` re-verifies the hash before
  it applies the rule.
- **Owner answers pinned in the file before hashing:**
  - full tuning re-search (the `scripts/tune_surrogates.py` procedure);
  - clause-2 STD = the larger of the gate-catch and static-catch stds;
  - SAFER is judged on the 0.95 data, with 0.94 reported;
  - failed relabel rows are dropped, and the run stops if they exceed 0.5%.

## Step 2 — Labels

- **0.94 data.** Existing N2 switch-back labels (`data/sts_n2_label_audit.parquet`).
  - 1 failed row of 278,955, dropped.
- **0.95 data.** Relabeled with the N2 method: `scripts/sts_n2_label_audit.py` functions, imported unchanged.
  - Driver: `scratch/n5_relabel095.py`, 4 workers, one shard file saved per seed.
  - Output: `data/sts_n5_relabel095.{parquet,json}` plus manifest.
  - Replay reproduces all 1,500 stored N-0 minima exactly.
  - The pinned re-solve reproduces every stored min_vm exactly (max diff 0).
  - Failed rows: 0 of 278,971.
  - Label flips at 0.94: viol→safe 4,379; safe→viol 1,534.
  - Violation rate: stored 16.006%, corrected 14.987%.
  - Boundary mass [0.94, 0.945) on the corrected labels: 28.64%. This is one build, so provisional.

## Step 3 — Gate re-evaluation (switch-back labels)

- **Scripts and outputs:**
  - Evaluator: `scratch/n5_gate_eval.py`, writing `data/sts_n5_gate_094.json` and `data/sts_n5_gate_095.json`.
  - Summary and verdict: `scratch/n5_summarize.py`, writing `data/sts_n5_verdict.json`.
  - Each output has a manifest that lists the selected M2 hyperparameters per split.
- **Setup:** 5 splits (seeds 0-4), ridge and histgb, targets 0.90-0.98 plus the held-out point (the M2
  inner_cov_at). Std is population std (ddof=0).
- **Evaluator check** (stored labels, seed 0, `scratch/n5_gate_094stored_seeds0.json`):
  - M2 tags and held-out targets match `data/tuning_search.json`.
  - Test MAE matches `data/tuned_metrics.json` exactly.
  - Escalation and missed rate over 60 sweep cells: max abs diff 0.
  - static_catch_A/B and solve_share_B match `data/sts_matched_budget.json`: max abs diff 0.

### Histgb at the held-out operating point

| | 0.94 data | 0.95 data |
|---|---|---|
| Held-out target | 0.960 ± 0.011 | 0.974 ± 0.008 |
| Escalation | 50.2 ± 8.4% | 33.2 ± 6.7% |
| Missed per split (seeds 0-4) | 1.11 / 0.98 / 0.34 / 0.95 / 4.16% | 1.10 / 1.21 / 1.41 / 0.71 / 1.15% |
| Missed, mean ± std | 1.51 ± 1.35% | 1.12 ± 0.23% |
| Speedup A | 2.058 ± 0.413 | 3.144 ± 0.706 |
| Speedup B | 1.545 ± 0.225 | 2.163 ± 0.327 |
| Gate catch | 98.49 ± 1.35% | 98.88 ± 0.23% |
| Static catch, matched budget B | 98.82 ± 0.81% | 97.94 ± 0.98% |

Ridge, targets 0.90-0.98, rule A and the per-target std-rule verdicts are in `data/sts_n5_verdict.json`
(`tables`).

### Pre-registered rule, applied as written

- **SAFER: NO.**
  - The rule needs histgb missed ≤ 1% in at least 4 of 5 splits on the 0.95 data; 1 of 5 splits meets it.
  - Three of the four failures lie between 1.10% and 1.21%, the fourth at 1.41%.
  - 0.94 data (reported, not the verdict): 3 of 5 splits meet it.
- **FASTER: NO.**
  - Clause 1 holds: speedup B 2.163 (0.95) vs 1.545 (0.94); diff 0.617 > STD 0.327.
  - Clause 2 fails: gate catch 98.88% vs static 97.94%; diff 0.94 pp is not > STD 0.98 pp, so it is a tie
    under the std rule.

## Step 4 — Second 0.95-floor build (new seeds 200-203)

- **Driver:** `scratch/n5_step4_build.py`, with the same invocation as N3 build B except the seeds.
- **Output:** `data/sts_n5_floor095_seed200.{parquet,json}` plus manifest. Wall time 1,563 s.
- **Labels:** stored pinned-solver labels, like-for-like with N3.

| Quantity | Build 1 (seeds 100-103) | Build 2 (seeds 200-203) | Mean ± std, ddof=0 [ddof=1] |
|---|---|---|---|
| Boundary mass [0.94, 0.945) | 32.954% | 34.817% | 33.89 ± 0.93 [1.32] |
| Conditional boundary mass | 39.234% | 41.444% | 40.34 ± 1.10 [1.56] |
| Violation rate | 16.006% | 15.991% | 15.999 ± 0.008 [0.011] |
| N-0 bases in strip | 36.87% | 39.13% | — |
| N-0 gate pass | 72.43% | 73.64% | — |
| Nonconverged rows | 29 | 43 | — |

- **Limits of these numbers:**
  - n = 2 builds, so these are two-point spreads, not well-estimated error bars.
  - Build 2's deepest min_vm is 0.598, against 0.715 for build 1.
  - Build 2 was not switch-back relabeled and not gate-evaluated; Step 4 did not ask for either.

## Facts that bound this result

- **One network (case118).** The 0.95 gate result rests on one relabeled build.
- **Overlap.** The 0.94 and 0.95 Step 3 runs overlapped for part of their wall time (OMP_NUM_THREADS=4 each).
  That affects only the measured t_surr, which is negligible next to t_solve in both speedup formulas.
- **Hardcoded path.** `scratch/n3_floor_rebuild.py` hardcodes `SHARD_DIR` under `/Users/rajansaha/`. The file
  was left unchanged; Step 4 overrides `SHARD_DIR` at run time.
- **Local-only logs.** The running log (`notes/overnight_status.md`) and the prompt log
  (`notes/ai-prompt-log.md` entry 2026-09-28 (f)) are in git-ignored `notes/`, so they stay on this machine.
