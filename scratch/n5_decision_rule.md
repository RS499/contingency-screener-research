# N5 decision rule — pre-registered before any N5 gate result exists

Source: owner prompt scratch/run_prompt_n5b.md, Step 1 (verbatim block below). Four ambiguities were settled
by the owner in-session (AskUserQuestion, 2026-09-29 UTC) before this file was written; those answers are the
"Operational pinning" section. Nothing below was chosen after seeing a gate result: no N5 surrogate has been
trained, and no N5 escalation, missed rate, speedup or catch rate exists when this file is hashed.

## Rule as given by the owner (verbatim)

```
PRIMARY MODEL: histgb (ridge reported, not used for the verdict).
OPERATING POINT: held-out; each split picks its target on its inner tuning
split, same procedure as data/tuning_search.json.
STD: the larger of the 0.94 and 0.95 seed stds (CLAUDE.md std rule).
SAFER: histgb missed violations <= 1% in at least 4 of 5 splits.
FASTER: histgb speedup B = n*t_solve / (n*t_surr + (n_esc + n_flag)*t_solve)
on 0.95 data exceeds the 0.94 value by more than STD, AND histgb catch rate
beats the static ranking at matched budget (rule B) by more than STD.
```

## Operational pinning (owner answers, then fixed definitions)

1. **Datasets.** "0.94 data" = data/dataset.parquet; "0.95 data" = data/sts_n3_floor095.parquet (generator
   voltage floor GEN_VM_LO). The screening limit is 0.94 pu on both.
2. **Labels.** Both datasets use switch-back labels: min_vm replaced by the PV/PQ switch-back corrected min_vm.
   - 0.94: corrected_min_vm from data/sts_n2_label_audit.parquet.
   - 0.95: relabeled with the same method (scripts/sts_n2_label_audit.py logic).
   - violation = corrected min_vm < 0.94. Surrogates train on, calibrate on, and are scored against the
     corrected min_vm.
3. **Failed rows (owner answer).** Rows whose switch-back solve does not return a converged corrected state
   (nonconverged, iteration cap, or pinned re-solve nonconverged) are dropped from train/cal/test, and the
   count is reported. If more than 0.5% of a dataset's N-1 rows fail, stop and report before Step 3.
4. **Splits.** The 5 outer splits are make_splits(groups, seed), seeds 0-4 (60/20/20 by scenario). Each split
   has an inner split of train, make_splits(train groups, 1000 + seed).
5. **Tuning (owner answer: full re-search).** Per dataset and split, run the scripts/tune_surrogates.py
   procedure unchanged on the relabeled data:
   - the same 15 ridge and 26 histgb candidates;
   - M2 = max inner avoided share subject to inner missed <= 1%, ties broken by MAE;
   - refit on the full train split, calibrate on cal, evaluate on test.
6. **Held-out operating point.** For each dataset, split and family, the target is the inner_cov_at of the M2
   selection, i.e. the coverage level (0.70-0.99 grid) that maximised inner avoided share subject to inner
   missed <= 1%. The test split is never read to choose it. If M2 has no feasible level on the inner split
   (inner_cov_at is None), that split's held-out point is recorded as missing and counts as a SAFER failure.
7. **Speedup B.** n*t_solve / (n*t_surr + (n_esc + n_flag)*t_solve) on the test split.
   - t_solve = ms_solver from data/solve_time.json.
   - t_surr = measured per-row predict time of the refit model (as in tune_surrogates.py).
   - Speedup A (reported, not used for the verdict) = the paper's n*t_solve / (n*t_surr + n_esc*t_solve).
8. **Std convention.** Population std (ddof=0) over the 5 splits.
9. **SAFER (owner answer: 0.95 gives the verdict, 0.94 reported).** On the 0.95 data, at the held-out point,
   histgb missed = certified true violations / true violations <= 0.01 in at least 4 of 5 splits. The same
   count is reported for 0.94.
10. **FASTER, clause 1.** mean_split(speedup_B, 0.95) - mean_split(speedup_B, 0.94) >
    max(std_split(speedup_B, 0.94), std_split(speedup_B, 0.95)), histgb, held-out point.
11. **FASTER, clause 2 (owner answer: larger of the gate and static stds).** On the 0.95 data, at the held-out
    point:
    - Gate catch = 1 - missed. Under rule B every escalated or flagged row is solved.
    - Static catch = true violations among the top-k statically ranked contingencies per test scenario, with
      k = round(solve_share_B * mean rows per test scenario), per split. This is the scratch/matched_budget.py
      / scripts/baselines.py definition, with the static frequency table built from relabeled train violations.
    - Clause 2 holds if mean(gate catch) - mean(static catch) > max(std(gate catch), std(static catch)).
12. **FASTER** = clause 1 AND clause 2. The two verdicts, SAFER and FASTER, are reported separately; this file
    does not combine them into one headline.
13. The targets 0.90-0.98 are reported for both families and datasets, but they are descriptive only and do not
    enter the verdict.
