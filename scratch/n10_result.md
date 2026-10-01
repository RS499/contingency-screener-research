# N10 result — MATPOWER label check, second network (case_illinois200), paper artifacts on corrected labels

## Prompt and provenance

- **Prompt:** `scratch/run_prompt_n10.md` (prompt section), run in-session on the Mac mini, 2026-09-30 UTC.
- **Report only.** No decision taken, no `.tex` edited, no git write.
  - The only existing files changed are appends to `notes/ai-prompt-log.md` and `notes/overnight_status.md`.
- **Numbers.** Every number below is read from the JSON files named here. Recompute from them; do not quote
  this file.

## Step 0 — Environment

- Python 3.13.11; pandapower 3.5.4, numpy 2.3.5, pandas 2.3.3, scikit-learn 1.7.2, pyarrow 21.0.0, numba 0.66.0.
  All match N9.
- GNU Octave 11.3.0; MATPOWER 8.1 (12-Jul-2025).
- git HEAD at start: `7f2c289`.

## Step 1 — Pre-registration

- `scratch/n10_decision_rule.md` is a byte-for-byte copy of the draft committed in `7f2c289`
  (2026-09-30T17:00:11-04:00).
- **sha256:** `7f94bd0a8958c011832895caded9db3275681ceae402e92913b3a3467e2f8907`, recorded 2026-09-30T21:12:28Z,
  before any N10 computation.
- The hash was re-verified in code before each verdict (Part A, Part B).

## Part A — Independent-solver label check (MATPOWER under Octave)

- **Scripts and output:** `scratch/n10_matpower_check.py` and `scratch/n10_switchback.m` →
  `data/sts_n10_matpower_check.{parquet,json}`.
- **Rows:** 201 (100 viol→safe, 100 safe→viol, plus the named worst case). Every M0/M1/M2 solve converged.

| Check | Result | k / n | CP95 | Max abs diff |
|---|---|---|---|---|
| A0 export fidelity (M0 vs pandapower no-limit, ≤ 1e-6 pu) | **PASS** | 201 / 201 | [0.982, 1] | 2.05e-7 pu |
| A1 one-way M1 label = stored label | **PASS** | 201 / 201 | [0.982, 1] | 1.58e-6 pu (min_vm) |
| A2 switch-back M2 label = N2 label | **CONFIRMED** | 201 / 201 | [0.982, 1] | 5.6e-7 pu (min_vm) |

- **Named worst case** (101000025, line 78):
  - stored 0.84854 pu; M1 0.84854; M2 0.94507 after 3 outer iterations; N2 0.94507.
  - M2 ≥ 0.94, as A2 requires.
- **Implementation notes,** fixed before any number:
  - `to_mpc(init='flat')`; `to_ppc` accepts only 'flat' or 'results'.
  - The slack generator's Q limits are set to ±Inf for M1/M2, because pandapower never Q-limits the ext_grid.
  - MATPOWER NR is set to tol 1e-8 and max_it 30.

## Part B — case_illinois200 (second network)

### Relabel (Step 3)

- **Script and output:** `scratch/n10_relabel_illinois.py` → `data/sts_n10_relabel_illinois200.{parquet,json}`.
- **Checks, all pass:**
  - replay exact: 7,880 draws; rejects 9 / 6,359 / 12 as stored; all 1,500 N-0 minima diff 0;
  - the pinned re-solve reproduces every stored min_vm (max diff 0);
  - 360,589 / 360,589 converged N-1 rows audited; failed 0.

| | Stored | Corrected |
|---|---|---|
| Violation rate | 29.28% | 21.66% |
| Boundary mass [0.94, 0.945) | 19.33% | 14.31% |

- **Flips:** viol→safe 27,478; safe→viol 0. Switch-back was needed on 275,323 rows.
- **Implementation note:** only the helper sgens are switched. N2's `apply_fixed` switches every sgen, and
  Illinois has 11 of its own; case118 has none.

### Evaluation (Step 4)

- **Script and output:** `scratch/n10_gate_illinois.py` → `data/sts_n10_illinois.json`. The pre-check is in
  `scratch/n10_gate_illinois_check.json`.
- **Pre-check on stored labels, seed 0:** reproduces `data/netstudy2/case_illinois200/frozen.json` exactly at
  0.90 (escalation, missed, test index hash) for ridge and histgb.
- **M2 selections:** histgb rand13 in all 5 splits; ridge alpha 31.62 / 0.001 / 10 / 0.001 / 0.1.

#### Verdicts (histgb, held-out target, rule B)

- **BEATS-STATIC-IL: YES.**
  - gate catch 99.04 ± 0.22% vs static at k_B 88.90 ± 1.20%;
  - gap 10.14 pp > STD 1.20 pp.
- **SAFER-IL: NO.**
  - held-out missed per split: 1.19 / 0.85 / 0.59 / 1.14 / 1.04%;
  - 2 of 5 splits are ≤ 1% (4 needed).

#### Held-out point and selected targets, mean ± std over 5 splits

| Family | Point | Target | Escalation | Missed | Speedup A | Speedup B | Gate catch | Static catch (k_B) | Std rule (B) |
|---|---|---|---|---|---|---|---|---|---|
| histgb | held-out | 0.952 ± 0.012 | 10.7 ± 2.2% | 0.96 ± 0.22% | 9.64 ± 1.99 | 3.12 ± 0.25 | 99.04 ± 0.22 | 88.90 ± 1.20 | gate higher |
| histgb | 0.90 | — | 5.8 ± 0.5% | 1.94 ± 0.12% | 17.01 ± 1.54 | 3.67 ± 0.17 | 98.06 ± 0.12 | 83.68 ± 0.85 | gate higher |
| histgb | 0.97 | — | 14.4 ± 1.6% | 0.57 ± 0.05% | 6.97 ± 0.76 | 2.80 ± 0.18 | 99.43 ± 0.05 | 92.02 ± 1.23 | gate higher |
| ridge | held-out | 0.952 ± 0.004 | 19.5 ± 1.6% | 0.83 ± 0.11% | 5.16 ± 0.43 | 2.42 ± 0.13 | 99.17 ± 0.11 | 95.18 ± 1.55 | gate higher |

- **Other held-out histgb numbers:** solve share B 32.1 ± 2.4%; k_B 77.2; flag share 21.4%; coverage 0.949.
- **Full tables:** targets 0.90-0.98, both families and both rules are in `data/sts_n10_illinois.json`
  (`table`).

#### Descriptive (no verdict)

- **Budget curve** (declared k = 26, 53, 75, 117, 158):
  - SURR vs STATIC is a **tie at every k for both families**.
  - Crossover = 26, i.e. SURR is never "higher".
  - Histgb vs static: 47.72 vs 47.17 at k = 26; 77.46 vs 75.98 at 53; 88.92 vs 88.11 at 75; 97.97 vs 97.79 at
    117; 99.60 vs 99.58 at 158.
- **Violation concentration** (share of test violations from the top-5 / top-10 elements by train frequency):
  - Illinois: 9.2 ± 0.4% / 18.4 ± 1.3%.
  - case118 D94 corrected: 16.5 ± 0.2% / 32.9 ± 0.5%.
- **Operator any-miss** (share of test base cases with ≥ 1 missed violation at the held-out point):
  - Illinois: histgb 23.9 ± 4.9%, ridge 20.4 ± 3.5%.
  - case118 D94: histgb 17.1 ± 7.2%, ridge 11.4 ± 2.2%.

## Part C — Paper artifacts on corrected labels (case118 D94; no verdict)

- **Script:** `scratch/n10_paper_artifacts.py`. Every refit reproduces the N5 test MAE exactly.
- **Files** (each with a manifest):
  - `data/sts_n10_fig_tradeoff.{png,json}`: escalation and missed vs target 0.70-0.99, ±1 std. First sub-1%
    mean missed: ridge 0.96, histgb 0.97.
  - `data/sts_n10_fig_missdepth.{png,json}`: at 0.90, no annotation. Ridge 1,528 misses (max 0.0475 pu);
    histgb 1,936 (max 0.0682 pu).
  - `data/sts_n10_fig_boundary.{png,json}`: 278,954 rows; BM 56.22%; VR 16.60%.
  - `data/sts_n10_fig_budget.{png,json}`: SURR / STATIC / ORACLE vs k, D94 and D95a.
  - `data/sts_n10_tables.{tex,json}`: tab:ops and tab:models bodies. Persistence and train-mean are recomputed
    on corrected labels.
- **Train-mean baseline:** on stored labels it flagged everything (escalation 0, speedup about 2×10⁷). On
  corrected labels it escalates everything (100%, speedup 1.00).
- **Comparison with the owner's `data/sts_paper_*`:** `scratch/n10_vs_paper_check.md`. All compared values
  agree:
  - Fig. 2 max diff 1.1e-16; Fig. 3 and 4 exactly equal;
  - tab:ops 12/12 identical;
  - tab:models numerically equal.

## Deviations and notes

- **Deviations from the hashed rule:** none.
- **Order:** Part C ran while Part B was computing, because it uses no Part B output.
- **Code style:**
  - `scratch/n5_summarize.py` (N5, committed) contains one `lambda`. It was not edited, because it is an
    existing file.
  - A few generator expressions remain in N9/N10 scratch scripts that have already produced artifacts. They
    were left as-is so their manifests' script hashes stay valid.

## Files written

- **scratch:** `n10_decision_rule.{md,sha256}`, `n10_matpower_check.py`, `n10_switchback.m`,
  `n10_relabel_illinois.py`, `n10_gate_illinois.py`, `n10_gate_illinois_check.json`, `n10_paper_artifacts.py`,
  `n10_vs_paper_check.{py,md}`, `n10_result.md`; git-ignored logs; `n10_mpc_cases/` (exported .mat cases,
  intermediate); `n10_relabel_illinois_chunks/` (intermediate).
- **data:** `sts_n10_matpower_check.{parquet,json}`, `sts_n10_relabel_illinois200.{parquet,json}`,
  `sts_n10_illinois.json`, `sts_n10_fig_{tradeoff,missdepth,boundary,budget}.{png,json}`,
  `sts_n10_tables.{tex,json}`, each with a manifest.
