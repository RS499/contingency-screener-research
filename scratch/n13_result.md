# N13 result — every dataset rebuilt with the corrected solver; replications on corrected data

## Prompt, provenance, cutoff

- **Prompt:** `scratch/run_prompt_n13.md` (prompt section), session 1 on the Mac mini, 2026-10-04 18:12 UTC to
  2026-10-05 ~03:00 UTC. All steps ran in one session.
- **Report only.** No decision taken, no `.tex` edited, no git write, no existing file edited. The only changes to
  existing files are appends to `notes/ai-prompt-log.md` and `notes/overnight_status.md`.
- **Numbers.** Every number below is read from the JSON files named here. Recompute from them; do not quote
  this file.
- **Cutoff** (rule §1, 2026-10-14 23:59 local): not reached. N13 finished on 2026-10-04 local.
- **Pre-registration:**
  - `scratch/n13_decision_rule.md` is a byte-for-byte copy of the draft committed in `504d728`
    (2026-10-04T14:11:21-04:00).
  - **sha256:** `ae941f64cf14b66eb5471a63396152365dc37e27c9066af99c1381b7cea5a5ce`, recorded
    2026-10-04T18:12:44Z, before any N13 computation.
  - The hash was re-verified before every verdict and in every analysis; it never failed.
- **Environment:** Python 3.13.11; pandapower 3.5.4, numpy 2.3.5, pandas 2.3.3, scikit-learn 1.7.2,
  pyarrow 21.0.0, numba 0.66.0. All match N12.
- **These are replications.** Every verdict below was decided once already on the old builds; the paper must
  call these replications on corrected data.

## How the rebuild was done (no existing file edited)

- **Solver swap.** `scratch/n13_common.py` replaces `generate_dataset.solve` and `solve_n0` at run time, inside
  the N13 processes only, with the corrected solve:
  - the pinned solve, then the N2 switch-back where a generator's limit state contradicts its voltage;
  - case118: `scripts/sts_n2_label_audit.corrected_solve`;
  - other networks: the N10/N11 helper-only version.
- **Build loop.** `scratch/n13_build.py` runs each build's original accept loop, then `run_scenario` (C30:
  `contingency_rows`) per accepted base, in parallel chunks.
- **Outputs.** Dataset files keep exactly the original schema (verified per dataset); audit columns are in
  `data/sts_n13_audit_<name>.parquet`.
- **Matching.** Old and rebuilt bases are matched by a hash of the scenario parameters, so every old-vs-rebuilt
  comparison is unpaired.

## Checks per dataset (rule §2)

| Dataset | Check 1 (replay) | Draws (old) | Common bases | Check 3 (labels) | Check 5 (failed rows; N-0 corr. fails) | Check 6 (independent solver) | Status |
|---|---|---|---|---|---|---|---|
| D94 | exact | 2,501 (2,787) | 159 | exact, 29,570 rows | 0; 0 | pass; all strata agree; near-limit 15.52% | **complete** |
| ILL | exact | 6,042 (7,880) | 10 | exact, 2,404 rows | 0; 0 | pass *with interpretation 1*; near-limit 6.56% | **complete** |
| C30 | exact | 8,050 (8,050) | 1,500 (identical set) | exact, 61,500 rows | 0; 0 | pass; near-limit 2.06% | **complete** |
| C24 | exact | 5,079 (8,348) | 62 | **FAIL**: pinned minima differ by up to 1.95e-14 on 1,062 / 2,266 rows | 20; 5 | pass | **excluded** |
| D93 | exact | 5,980 (6,278) | 76 | exact, 14,136 rows | 0; 0 | pass; near-limit 14.76% | **complete** |
| D95a | exact | 1,839 (2,071) | 108 | exact, 20,088 rows | 0; 0 | pass; near-limit 6.22% | **complete** |
| D96 | exact | 1,707 (1,827) | 382 | exact, 71,052 rows | 1; 0 | pass; near-limit 3.69% | **complete** |
| N2R | (D94's) | 75,000 rows | 159 | exact, 1,816 rows | 2 | pass; near-limit 14.50% | **complete** |
| D95b | exact | 1,843 (2,037) | 214 | exact, 39,804 rows | 0; 0 | pass; near-limit 6.24% | **complete** |
| D95c | exact | 1,874 (2,032) | 232 | exact, 43,152 rows | 1; 0 | pass; near-limit 6.29% | **complete** (its gate stopped, below) |

- **Check 2 and check 4** passed on every dataset.
- **Base sets.** They diverge almost at once: the shared prefix is 0-64 draws per shard (ILL 10 draws). The one
  exception is C30, where the corrected check changed no acceptance at all.
- **Evidence:** `data/sts_n13_replaycheck.json`, `data/sts_n13_build_<name>.json`, `data/sts_n13_indep_<name>.json`.
- **Rebuilt descriptives (converged outage rows, corrected labels):**

| Dataset | VR | BM | CBM |
|---|---|---|---|
| D94 | 16.26% | 54.75% | 65.37% |
| ILL | 27.17% | 18.75% | 25.75% |
| C30 | 15.38% | 7.10% | 8.39% |
| D93 | 16.35% | 56.32% | 67.33% |
| D95a | 14.81% | 33.36% | 39.16% |
| D96 | 13.59% | 18.97% | 21.95% |
| D95b | 14.92% | 31.60% | 37.14% |
| D95c | 14.72% | 31.90% | 37.41% |

- **Old rejected draws that pass the corrected check** (§5, `data/sts_n13_old_rejects.json`, every replay exact):

| Dataset | Would now pass |
|---|---|
| D94 | 185 / 1,287 |
| ILL | 423 / 6,380 |
| C30 | 0 / 6,550 |
| C24 | 1,084 / 6,848 |
| D93 | 152 / 4,778 |
| D95a | 148 / 571 |
| D96 | 83 / 327 |
| D95b | 144 / 537 |
| D95c | 139 / 532 |

## Tier-A verdicts (data/sts_n13_verdicts.json; definitions verbatim from the hashed rule files)

| Verdict | Rebuilt | Numbers it rests on | Old build |
|---|---|---|---|
| **V1 SAFER-94** (primary) | **YES** | histgb held-out missed 0.52 / 0.72 / 3.03 / 0.91 / 0.51%, so 4/5 splits ≤ 1% | NO (3/5) |
| **V2 SAFETY-CHANGED** (primary) | **NO** | rebuilt 1.136 ± 0.957% vs old 1.509 ± 1.355%; diff −0.37 pp (rebuilt lower), within STD 1.355 | n/a |
| BEATS-STATIC, D94 | no | gate 98.86 ± 0.96 vs static 99.16 ± 0.58 | no |
| **BEATS-STATIC, ILL** (primary) | **YES** | 99.09 ± 0.25 vs 84.82 ± 1.69; gap 14.27 > 1.69 | YES |
| BEATS-STATIC, C30 | yes | 99.26 ± 0.35 vs 83.16 ± 3.01 | yes |
| BEATS-STATIC, C24 | not run (excluded) | — | yes |
| SAFER-IL | NO | 3/5 splits ≤ 1% | NO (2/5) |
| GATE-BEATS-CONDHIST, D94 | no | gate 98.86 vs COND-HIST 99.64; gap −0.78 | no |
| **GATE-BEATS-CONDHIST, ILL** (primary) | **YES (narrow)** | gate 99.09 vs COND-HIST 98.45; gap 0.64 > STD 0.61 | YES |
| GATE-BEATS-CONDHIST, C30 | yes | gap 9.45 > 2.89 | yes |
| **COVERAGE-HOLDS-N2** (primary) | **NO** | N-2 coverage 0.8394 ± 0.0126 < threshold 0.8861 | NO |
| MONDRIAN-BEATS-STATIC | **YES (narrow)** | gap 0.78 > STD 0.76 (gate 98.78 ± 0.76 vs static 98.00 ± 0.68) | NO |
| **FLOOR_DOSE_RESPONSE** (primary) | **YES** | BM 56.32 / 54.75 / 33.36 / 18.97 for floors 0.93 / 0.94 / 0.95 / 0.96 | YES |

- **Verdicts that changed sign vs the old build:**
  - V1 SAFER-94 (NO → YES, 3/5 → 4/5);
  - MONDRIAN-BEATS-STATIC (NO → YES, by 0.02 pp over the std).
- **V2 says the mean missed rate did not change beyond the std.** The V1 flip is one split crossing 1%.

## Tier-B verdicts (data/sts_n13_verdicts_tierB.json)

| Verdict | Rebuilt | Numbers | Old build |
|---|---|---|---|
| SAFER (N5 form, D95a) | NO | 2/5 (0.37 / 1.16 / 0.81 / 1.03 / 1.35%) | NO (1/5) |
| FASTER (N5 form) | NO | clause 1 yes: speedup B 1.971 ± 0.278 vs 1.439 ± 0.228. Clause 2 no: gate 99.06 vs static 98.88, diff 0.18 pp < STD 0.39 | NO (clause 1 yes, clause 2 no) |
| SHIFT-ADVANTAGE | NO | D94 → D95a histgb gate 98.64 ± 0.66 vs static 98.64 ± 0.61; gap −0.00 | NO |

## Arm F diagnostic (data/sts_n13_armF.json; original bases, corrected inputs only; never replaces paper numbers)

- **Reproduction gate.** Refitting on the original inputs reproduces the stored held-out missed rate exactly for
  every network, family and split.
- **V3 MISMATCH-DRIVES-DRIFT-GAP: NO.** Histgb, > 1e-3 drift bin:
  - pinned inputs 1.57 / 1.18 / 0.67 / 1.44 / 19.49% (4.87 ± 7.32);
  - corrected inputs 1.57 / 0.67 / 1.43 / 2.10 / 2.13% (1.58 ± 0.53);
  - gap 3.29 pp, not > 7.32 pp.
  - The pinned rates equal `data/sts_n0drift_check.json` exactly.
  - Split 4's 19.49% falls to 2.13%, but that one split drives the pinned std.
- **Paired differences** (corrected − original inputs), histgb:

| Network | Missed (pp) | Escalation (pp) | Speedup B |
|---|---|---|---|
| D94 | −0.41 ± 0.83 | −4.13 ± 3.84 | +0.072 ± 0.080 |
| ILL | −0.16 ± 0.17 | −1.35 ± 0.37 | +0.085 ± 0.047 |
| C30 | +0.06 ± 0.15 | +0.02 ± 0.18 | −0.012 ± 0.040 |
| C24 | +0.30 ± 0.43 | −6.34 ± 0.81 | +0.161 ± 0.013 |

- Both binnings (minimum and max per-bus |Δ vm0|), for both families, are in the JSON.

## Descriptive tables on rebuilt data

### Gate, histgb held-out (data/sts_n13_gate_<name>.json)

| Dataset | Target | Escalation | Missed | Gate catch | Static (k_B) |
|---|---|---|---|---|---|
| D94 | 0.970 ± 0.011 | 54.2% | 1.14 ± 0.96% | 98.86 | 99.16 |
| ILL | — | — | 1.15 / 0.67 / 0.57 / 0.96 / 1.20% | 99.09 | 84.82 |
| D95a | 0.98 | 37.4% | 0.94% | 99.06 | 98.88 |
| D95b | — | 31.1% | 1.32% | 98.68 | 98.38 |

- C30 is in its gate file. D95c's gate: not run (see stops below).

### Other tables

- **Budget curve (histgb):** D94 and D95a both show SURR higher at k = 20, 40, 57 and STATIC higher at k = 89,
  120. Same as the old build (`data/sts_n13_budget.json`, `data/sts_n13_budget_D95a.json`).
- **N-2** (`data/sts_n13_n2.json`):
  - histgb at 0.90: N-2 coverage 0.839, missed 4.60 ± 0.80%, 0/5 ≤ 1%;
  - histgb held-out: coverage 0.935, missed 1.40%, 3/5 ≤ 1%.
- **Guarantee** (`data/sts_n13_guarantee.json`), histgb, global-q̂ → base-level α = 0.10:

| Network | Any-miss share | Speedup B | Splits with any-miss ≤ α |
|---|---|---|---|
| D94 | 12.4 → 11.2% | 1.44 → 1.40 | 2/5 |
| ILL | 28.4 → 11.2% | 2.75 → 2.15 | 2/5 |

- **Cross-network table** (`data/sts_n13_crossnet.json`, n = 3 after C24's exclusion; no law claimed):

| Network | BM | VR | Risk spread | Top-10 | Gate | Static | COND-HIST | GLOBAL-STATIC |
|---|---|---|---|---|---|---|---|---|
| D94 | 54.75 | 16.26 | 0.047 | 32.8% | 98.86 | 99.16 | 99.64 | 99.16 |
| ILL | 18.75 | 27.17 | 0.170 | 13.7% | 99.09 | 84.82 | 98.45 | 84.49 |
| C30 | 7.10 | 15.38 | 0.082 | 89.5% | 99.26 | 83.16 | 89.81 | 83.56 |

- **Floor replication** (rebuilt D95a/b/c): BM 32.29 ± 0.77, CBM 37.90 ± 0.89, VR 14.82 ± 0.08 (ddof=0).

## Old vs rebuilt (Step 8, data/sts_n13_compare.json; unpaired; std rule)

- **Totals:** 334 rows; 76 differ, 238 within std, 20 not run (all C24).
- **tab:ops** (72 rows): 69 within std. 3 differ:
  - histgb 0.95 escalation 44.4 → 40.3%;
  - histgb 0.95 speedup A 2.27 → 2.49;
  - ridge 0.97 speedup B 1.038 → 1.023.
  - Every held-out row is within std (histgb held-out missed 1.51 ± 1.35 → 1.14 ± 0.96%).
- **tab:models:** 19 within std. 1 differs: persistence MAE 4.08 → 3.90 mV.
- **Gate vs static:**
  - ILL histgb static catch 88.90 → 84.82; solve share B 32.1 → 36.4%; speedup B 3.12 → 2.75;
  - ILL ridge escalation 19.5 → 13.9%, missed 0.83 → 1.08%;
  - the rest within std.
- **Floor and cross-network BM/VR** are single numbers without a std, so "differs" there means "not equal".
  - ILL moved most: BM 14.31 → 18.75%, VR 21.66 → 27.17%.
  - D94: BM 56.22 → 54.75%, VR 16.60 → 16.26%.
- **N-2 and Mondrian:** all rows within std.

## What did not run

- **C24:** excluded at check 3, so it has no rebuilt analyses. Its old results are not substituted back.
- **Classical screen on rebuilt D94** (stopped, rule 2):
  - `scripts/run_classical.py`, run unchanged, stopped on its own guard at the first base: "reconstructed vm0
    differs from stored by 1.58e-03 (tolerance 1e-05)".
  - It re-solves each base with the pinned solver, while the rebuilt `vm0_*` are corrected states. Running it
    would need a method change.
- **D95c gate** (stopped, rule 2):
  - it crashed in split 4's ridge M2 search inside scikit-learn Ridge (`LinAlgError: SVD did not converge`);
  - not retried, settings unchanged;
  - the D95c dataset is still in the floor replication.

## Interpretations and deviations

1. **Interpretation, check 6 validation (ILL; applied to all datasets):**
   - 3 ILL rows (all trafo 63 outages) make the independent model unbuildable (`KeyError 'baseMVA'`): trafo 63's
     outage islands 199 of 200 buses.
   - Validation therefore covers rows whose model exists (it passed on 2,297 rows); model-build failures count
     under the rule's 2% non-convergence stop (0.13%).
   - The alternative would exclude the whole primary network over 3 rows.
2. **Finding (not a deviation):** all 1,500 trafo-63 outage rows of ILL, in the old and the rebuilt build, are
   this islanding case. min_vm = 1.04 is the slack bus only, and the label is "safe".
3. **Interpretation (arm F, C24):** 2 bases whose N-0 switch-back failed keep their stored inputs; no corrected
   input exists.
4. **Deviation (code fix), check 6 script:** the validation flag first counted model-build failures as validation
   failures. Changed as in interpretation 1, before C30's check 6; D94's result is unaffected (0 such rows).
5. **Deviation (code fix), `scratch/n13_old_rejects.py`:**
   - the log accumulated across pool tasks;
   - the corrected solve mutated the replay net (C24 replay inexact).
   - Fixed: log reset per task; corrected solve on a deep copy. The first, wrong counts were never used.
6. **Deviation (code fix), `scratch/n13_armF.py`:** it crashed on N11's smallnets file, which has no "fits"
   list. Configs now come from the M2 tag via the unchanged candidate list, and t_surr from the stored held-out
   speedup B.
7. **Deviation (code fix), queue invocation:** "budget D95a" was passed as one argument; it was rerun correctly.
8. **Correction to my N11 report:**
   - N11's own C24 relabel recorded `resolve_min_vm_exact = False` (max 1.03e-13,
     `data/sts_n11_relabel_case24_ieee_rts.json`).
   - My N11 status entry and `scratch/n11_result.md` wrongly said every C24 check passed (my monitor matched
     only two of the four flags).
   - C24's N13 check-3 failure has the same cause (helper sgens shift the pinned solve at about 1e-14) and was
     already present in N11.
- **No verdict is touched by a deviation.** The code fixes concern counting and diagnostics, and none changes a
  hashed method. Interpretation 1 decides ILL's inclusion, so every verdict on ILL should be read as "with
  interpretation".

## Files written

- **scratch:**
  - pre-registration: `n13_decision_rule.{md,sha256}`;
  - scripts: `n13_common.py`, `n13_replay.py`, `n13_build.py`, `n13_checks.py`, `n13_indep_check.py`,
    `n13_n2r.py`, `n13_old_rejects.py`, `n13_gate.py`, `n13_analyses.py`, `n13_classical.py`,
    `n13_verdicts.py`, `n13_verdicts_B.py`, `n13_armF.py`, `n13_compare.py`;
  - `n13_result.md`;
  - small evidence files: `n13_armF_<net>_build.json`, `n13_indep_rows_<name>.parquet`;
  - logs `*.log` (git-ignored);
  - intermediate dirs: `n13_build/`, `n13_drawlogs/`.
- **data (each with a manifest):**
  - checks and builds: `sts_n13_replaycheck.json`, `sts_n13_old_rejects.json`;
  - per rebuilt dataset: `sts_n13_<name>.parquet`, `sts_n13_audit_<name>.parquet`, `sts_n13_build_<name>.json`,
    `sts_n13_indep_<name>.json` (D94, ILL, C30, C24, D93, D95a, D96, D95b, D95c); N2R: `sts_n13_N2R.parquet`
    plus its build and indep JSONs;
  - gates: `sts_n13_gate_{D94,ILL,C30,D95a,D95b}.json`;
  - analyses: `sts_n13_{condhist,budget,budget_D95a,guarantee,crossnet,n2,mondrian,floor,shift,floorrep,gate095bc,classical}.json`;
  - verdicts: `sts_n13_verdicts.json`, `sts_n13_verdicts_tierB.json`;
  - arm F: `sts_n13_armF.json`, `sts_n13_armF_{D94,ILL,C30,C24}.parquet`;
  - comparison: `sts_n13_compare.json`.
