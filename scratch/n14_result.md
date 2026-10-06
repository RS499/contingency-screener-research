# N14 result — C24 amendment, Illinois without trafo 63, islanding sensitivity

## Prompt, provenance, cutoff

- **Prompt:** `scratch/run_prompt_n14.md` (prompt section), session 1 on the Mac mini, 2026-10-05 22:31 UTC to
  2026-10-06 ~01:35 UTC. Every step ran.
- **Report only.** No decision taken, no `.tex` edited, no git write, no existing file edited. The only changes to
  existing files are appends to `notes/ai-prompt-log.md` and `notes/overnight_status.md`.
- **Numbers.** Every number below is read from the JSON files named here. Recompute from them; do not quote
  this file.
- **Cutoff** (2026-10-12 23:59 America/New_York): not reached. N14 finished on 2026-10-05 local.
- **Pre-checks:**
  - HEAD `9ca3c06` = origin/main; the tracked working tree was clean;
  - the rule draft was in HEAD with no uncommitted changes.
- **Pre-registration:**
  - `scratch/n14_decision_rule.md` is a copy of the draft committed in `9ca3c06`.
  - **sha256:** `a0985845b76d46911d19e38718f996d3fa5c1f02a0a13b1e3b029310788692d5`, recorded 2026-10-05T22:32:00Z,
    before any N14 computation.
  - The hash was re-verified in every script and before every verdict.
- **Environment:** pinned versions match N13 (Python 3.13.11; pandapower 3.5.4, numpy 2.3.5, pandas 2.3.3,
  scikit-learn 1.7.2, pyarrow 21.0.0, numba 0.66.0).
- **These are re-analyses.** Every verdict below is a re-analysis of the rebuilt N13 datasets, decided once already
  on them. Two parts are post hoc and say so: the §A tolerance and the §B exclusion criterion.

## Checks

| Check | Result | Evidence |
|---|---|---|
| Step 2: D94 / C30 hash check | D94 10/10 and C30 5/5 files match their N13 manifest sha256, so both are **restated from N13** | `data/sts_n14_restate_check.json` |
| Step 3: C24 check 3 under the amendment (pinned tolerance 1e-9 pu) | **PASS**. Pinned max \|diff\| 1.95e-14 pu (2,266 rows, nonzero on 1,062); corrected max \|diff\| 0; 0 status mismatches. Every other dataset's N13 pinned maximum was 0 | `data/sts_n14_c24_check3.json` |
| Exclusion selection (topology) | the primary removes only ILL trafo 63 (1,500 rows). The sensitivity removes D94 9, ILL 72, C30 3 and C24 1 outages (13,500 / 108,000 / 4,500 / 1,462 rows) | gate files → `labels` |
| Refit reproduction (guarantee, islanding split) | every refit reproduced its gate's held-out numbers | analysis files |

**C24 is re-admitted.** The paper uses two disclosure sentences from rule §A:
- the amendment: "case24 is included under a pre-registered amendment (N14) that replaced N13's exact-equality
  check on pinned voltages with a 1e-9 pu tolerance; the original check failed by at most 1.95e-14 pu, a
  floating-point difference."
- arm F: "Arm F had produced C24 safety numbers (missed, escalation, speedup) on the original C24 bases with
  corrected inputs before this amendment; the gate-vs-baseline comparisons had not been computed."

## Verdicts (data/sts_n14_verdicts.json; definitions and outcome wording verbatim from the hashed rules)

### Primary

D94 and C30 are restated from N13; ILL is without trafo 63; C24 is new.

| Verdict | N14 primary | Numbers it rests on | N13 |
|---|---|---|---|
| BEATS-STATIC, D94 | no | gate 98.86 ± 0.96 vs static 99.16 ± 0.58 | no |
| BEATS-STATIC, ILL | **YES** | 99.02 ± 0.31 vs 84.59 ± 2.63; gap 14.43 > 2.63 | YES |
| BEATS-STATIC, C30 | yes | 99.26 ± 0.35 vs 83.16 ± 3.01 | yes |
| BEATS-STATIC, C24 | **YES** | 98.85 ± 0.27 vs 89.65 ± 1.01; gap 9.20 > 1.01 | not run (excluded) |
| SAFER-IL | NO | histgb held-out missed 1.47 / 0.68 / 0.61 / 1.05 / 1.10%, so 2/5 ≤ 1% | NO (3/5) |
| GATE-BEATS-CONDHIST, D94 | no | gate 98.86 vs COND-HIST 99.64; gap −0.78 | no |
| **GATE-BEATS-CONDHIST, ILL (primary)** | **NO** | gate 99.02 ± 0.31 vs COND-HIST 98.21 ± 1.08; gap 0.81 not > STD 1.08 | YES (gap 0.64 > 0.61) |
| GATE-BEATS-CONDHIST, C30 | yes | gap 9.45 > 2.89 | yes |
| GATE-BEATS-CONDHIST, C24 | yes | gate 98.85 vs COND-HIST 97.18; gap 1.67 > 0.41 | not run |

- **Count of networks where the gate beats COND-HIST:** 2 of 4 (C30, C24).

### Sensitivity (every islanding outage removed)

| Network | BEATS-STATIC | GATE-BEATS-CONDHIST |
|---|---|---|
| D94 | no (gap −0.27 vs 1.03) | no (gap −0.78 vs 1.03) |
| ILL | yes (gap 15.12 > 2.19) | **yes** (99.07 vs 97.86; gap 1.22 > 0.86) |
| C30 | yes | yes (gap 10.52 > 2.67) |
| C24 | yes | yes (gap 1.64 > 0.58) |

### ILL outcome: case (c)

> "on Illinois the gate does not beat COND-HIST once trafo 63 is excluded"

- The cross-network count of networks where the gate wins drops by one.
- Per the rule, (c) applies whatever the sensitivity result. The sensitivity result (holds) is reported beside it.
- **What moved:**
  - The gap is slightly larger than in N13 (0.81 vs 0.64).
  - COND-HIST's split-to-split std rose from 0.61 to 1.08, so the gap no longer exceeds the larger std.
  - Paired against N13 on the same splits: gate catch −0.07 ± 0.14 pp; COND-HIST −0.25 ± 0.51 pp.

## Descriptive tables

### Held-out gate (histgb), sensitivity runs (data/sts_n14_sensitivity.json)

| Network | Rows removed | Escalation | Missed | Speedup A | Speedup B |
|---|---|---|---|---|---|
| D94 | 13,500 | 55.3 ± 10.6% | 1.14 ± 1.03% | 1.88 | 1.44 |
| ILL | 108,000 | 8.6 ± 2.3% | 0.93 ± 0.24% | 12.16 | 2.36 |
| C30 | 4,500 | 5.5 ± 1.6% | 0.67 ± 0.34% | 19.44 | 4.62 |
| C24 | 1,462 | 8.4 ± 1.1% | 1.07 ± 0.37% | 12.03 | 1.58 |

### Other primary numbers

- **ILL primary held-out (histgb):** escalation 8.6%; missed 0.98%; speedup A 12.44; speedup B 2.76.
- **ILL guarantee** (`data/sts_n14_guarantee.json`), histgb any-miss share global / row-level / base-level:
  30.1 / 29.7 / 10.1%; speedup B 2.76 / 2.77 / 2.12; base-level any-miss ≤ 0.10 in 1/5 splits.
- **Cross-network** (`data/sts_n14_crossnet.json`, n = 4, no law claimed):
  - D94: BM 54.75, VR 16.26 (restated);
  - ILL: BM 18.83, VR 27.28 (trafo 63 removed);
  - C30: BM 7.10, VR 15.38 (restated);
  - C24: BM 24.09, VR 54.24 (new).

### Catch on islanding vs non-islanding rows, primary, histgb held-out (data/sts_n14_islanding_split.json; %)

| Network | Gate (isl / non) | Static (isl / non) | COND-HIST (isl / non) |
|---|---|---|---|
| D94 | 99.52 / 98.82 | 99.58 / 99.12 | 99.90 / 99.62 |
| ILL | 99.00 / 99.02 | 79.12 / 85.48 | 96.94 / 98.41 |
| C30 | 90.71 / 99.34 | 0.00 / 83.95 | 28.10 / 90.40 |
| C24 | 100.00 / 98.79 | 100.00 / 89.10 | 100.00 / 97.03 |

- Stds per split are in the file.
- C30's islanding rows hold few violations: 2.38% of its islanding rows are violations, vs 16.41% of the rest.
  Its "isl" column rests on 14-21 test violations per split (the file has every count).

## Comparison against N13 (data/sts_n14_compare.json)

- **Totals:** 103 rows; 94 within std, 4 differ under the unpaired std rule. The rest are single numbers or
  "no counterpart" entries.
- **The 4 that differ** are all ILL sensitivity, with paired differences:
  - histgb solve share B 36.4 → 42.5% (+6.1 ± 1.3 pp), speedup B 2.75 → 2.36 (−0.39 ± 0.06);
  - ridge solve share B +7.3 ± 0.9 pp, speedup B −0.35 ± 0.05.
- **ILL primary vs N13:** every row within std. Paired: gate catch −0.07 ± 0.14 pp; static −0.23 ± 1.02 pp;
  COND-HIST −0.25 ± 0.51 pp.
- **ILL cross-network** (unpaired only, because the N13 file keeps no per-split values for these):
  - risk spread within std;
  - top-10 concentration equal to N13 (trafo 63 has no violations, so removing it changes neither).
  - Boundary mass 18.75 → 18.83% and violation rate 27.17 → 27.28%: single numbers, no std rule.
- **C24** has no N13 rebuilt counterpart, so it is listed as such.

## What did not run

- **The classical screen and the D95c gate:** dropped from N14 under rule §C, both classification (b).
  - Classical: "not run" in the rebuilt Table 1.
  - D95c gate: from the old build, labelled "old build, uncorrected solver" (`data/sts_n11_gate_095bc.json`).
- Nothing else was skipped.

## Interpretations and deviations

1. **Deviation (code fix), launch command.** The first launch of the six gates failed at once: zsh did not
   word-split my job string, so each script got one combined argument. No output was written. Relaunched with
   explicit arguments. No method changed and no verdict is touched.

2. **Deviation (code fix), comparison coverage.** My first `scratch/n14_compare.py` left out the ILL
   cross-network risk spread and top-10 concentration, which have N13 counterparts. I added them (unpaired only)
   and re-ran; `data/sts_n14_compare.json` was overwritten by that re-run. No verdict uses these rows.

- No interpretation was needed. No verdict is "with deviation".

## Replacement (rule §E)

- The N14 primary results replace the N13 ILL and C24 numbers, whichever way they moved. The N13 numbers are
  reported as "before N14".
- D94 and C30 keep their N13 numbers (restated; hashes matched).

## Files written

- **scratch:**
  - pre-registration: `n14_decision_rule.{md,sha256}`;
  - scripts: `n14_restate_check.py`, `n14_c24_check3.py`, `n14_common.py`, `n14_gate.py`, `n14_analyses.py`,
    `n14_verdicts.py`, `n14_compare.py`;
  - `n14_result.md`;
  - logs `*.log` (git-ignored).
- **data (each with a manifest):**
  - checks: `sts_n14_restate_check.json`, `sts_n14_c24_check3.json`;
  - gates: `sts_n14_gate_C24.json`, `sts_n14_gate_ILL.json`, `sts_n14_gate_{D94,ILL,C30,C24}_sens.json`;
  - analyses: `sts_n14_condhist.json`, `sts_n14_guarantee.json`, `sts_n14_crossnet.json`,
    `sts_n14_sensitivity.json`, `sts_n14_islanding_split.json`;
  - verdicts and comparison: `sts_n14_verdicts.json`, `sts_n14_compare.json`.
