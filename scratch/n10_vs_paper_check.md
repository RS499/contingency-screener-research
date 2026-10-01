# N10 Part C vs `data/sts_paper_*` — numeric check

Read-only comparison (scratch/n10_vs_paper_check.py). No `data/sts_paper_*` file was modified. "abs diff" is the largest absolute difference over the compared values; 0 means equal to the last bit.

## Fig. 2 — escalation / missed vs target (values JSON)

| model | points (mine / theirs) | targets identical | max abs diff: escalation, escalation_std, missed, missed_std |
|---|---|---|---|
| ridge | 30 / 30 | True | 5.55e-17, 5.2e-17, 1.39e-17, 3.47e-18 |
| histgb | 30 / 30 | True | 1.11e-16, 2.78e-17, 2.78e-17, 5.2e-18 |

- Image-level difference, not a number: mine draws the first-sub-1% dash-dot markers with value labels (ridge 0.96, histgb 0.97); yours omits them by design (its note: "no operating-point markers: the old 0.94/0.97 markers were test-picked").

## Fig. 3 — miss depth at 0.90 (values JSON)

| model | n misses (mine / theirs) | q̂@0.90 mean abs diff | max depth abs diff |
|---|---|---|---|
| ridge | 1528 / 1528 | 0 | 0 |
| histgb | 1936 / 1936 | 0 | 0 |

- Fields only in yours (share_within_qhat, share_deeper_than_0p005, p99_depth) and only in mine (per-bin counts) are not compared.

## Fig. 4 — corrected min_vm histogram (values JSON)

| quantity | mine | theirs | abs diff |
|---|---|---|---|
| n rows | 278954 | 278954 | 0 |
| boundary mass (%) | 56.21607863662109 | 56.21607863662109 | 0 |
| violation rate (%) | 16.595926210056138 | 16.595926210056138 | 0 |
| tallest bin share (%) | 12.691698272833515 | 12.691698272833515 | 0 |
| tallest bin left edge (pu) | 0.9400000000000002 | 0.9400000000000002 | 0 |
| share below 0.87 view (%) | 0.43483871892856885 | 0.43483871892856885 | 0 |

## Budget-curve figure

- Both are drawn from the same source: mine `data/sts_n9_budget_curve.json`, yours `data/sts_n9_budget_curve.json`.
- Your values JSON carries no curve values (panels hold only n_splits = 5 and k_max = 186), so curve values cannot be compared file to file.
- k_max: mine 186, yours 186; x view: mine [1, 130], yours "k in [0, 130] of 186".
- Content differences, not numbers: mine draws ridge and histgb rankings and bands the oracle; yours draws histgb only (family = histgb) and draws the oracle without a band.

## Table bodies (printed cells, `data/sts_n10_tables.tex` vs `data/sts_paper_tables.tex`)

Comparison is of the printed (rounded) cells; the largest difference is in the printed units.

### tab:ops (the 12 grid-target rows)

| row | identical text | largest numeric diff |
|---|---|---|
| ridge 0.90 | True | 0 |
| ridge 0.94 | True | 0 |
| ridge 0.95 | True | 0 |
| ridge 0.96 | True | 0 |
| ridge 0.97 | True | 0 |
| ridge 0.98 | True | 0 |
| histgb 0.90 | True | 0 |
| histgb 0.94 | True | 0 |
| histgb 0.95 | True | 0 |
| histgb 0.96 | True | 0 |
| histgb 0.97 | True | 0 |
| histgb 0.98 | True | 0 |

- Rows only in yours: 2 (ridge held-out (0.94$\pm$0.01), histgb held-out (0.96$\pm$0.01)); not in the N10 spec.

### tab:models (4 rows)

| row | identical text | largest numeric diff | note |
|---|---|---|---|
| persistence | True | 0 |  |
| train mean | False | 0 | col 2: mine `$-0.00\pm0.00$` vs yours `0.00$\pm$0.00` |
| ridge | True | 0 |  |
| histgb | True | 0 |  |

### Full-precision check: persistence and train mean (your JSON per-seed rows vs my JSON means)

| model | quantity | mine (mean) | yours (mean of per-seed) | abs diff |
|---|---|---|---|---|
| persistence | MAE (mV) | 4.076802380618996 | 4.0768023806189975 | 1.78e-15 |
| persistence | R2 | -0.04891414665124105 | -0.04891414665124105 | 0 |
| persistence | escalation (%) | 98.20003225478612 | 98.20003225478612 | 0 |
| persistence | missed (%) | 1.3505264590819706 | 1.3505264590819708 | 2.22e-16 |
| persistence | speedup A | 1.018345043314239 | 1.0183463889203868 | 1.35e-06 |
| train_mean | MAE (mV) | 6.188874977883889 | 6.188874977883887 | 1.78e-15 |
| train_mean | R2 | -0.00033435328026114596 | -0.00033435328026114596 | 0 |
| train_mean | escalation (%) | 100.0 | 100.0 | 0 |
| train_mean | missed (%) | 0.0 | 0.0 | 0 |
| train_mean | speedup A | 0.9999998589830904 | 0.9999999529633989 | 9.4e-08 |

- Sections only in yours (not in the N10 spec, so not compared): tab:ops held-out rows, the speedup-B variant, the floor table, and gate vs static.

## Summary

- **Figures 2, 3, 4:** every compared value agrees. Fig. 3 and 4 match to the last bit; Fig. 2 differs by at
  most 1.1e-16, which is floating-point summation order.
- **Budget figure:** both come from the same source file. Curve values cannot be compared because yours stores
  none.
- **tab:ops:** all 12 grid rows are character-identical.
- **tab:models:** all four rows agree numerically. The one text difference is the train-mean R², whose true
  value is −0.000334 (both JSONs). Mine prints `$-0.00\pm0.00$`, yours `0.00$\pm$0.00`; the value is the
  same.
- **Speedup A for the two baselines:** diffs of 1.35e-6 (persistence) and 9.4e-8 (train mean). Both scripts
  measure the surrogate's predict time with a wall clock on their own run, so t_surr differs slightly.
  Printed to 2 decimals, the cells are identical.
- No `data/sts_paper_*` file was modified: sha256 of all 15 was checked before and after.
