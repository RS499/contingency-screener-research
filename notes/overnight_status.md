# Overnight status — N5 run (prompt: scratch/run_prompt_n5.md)

## 2026-09-28T23:59:52Z — STOPPED at Step 0 (nothing computed)

- **Step 0: not run.** Every `.venv/bin/python` call, even `--version`, was denied: it needs
  interactive approval, and the session was non-interactive. The versions and the byte comparison are
  therefore unknown.
- **Steps 1-4: not run.** They run in order, and Step 0 is the stop gate.
  - Nothing was written: no scratch/n5_decision_rule.md, no .sha256, no data/sts_* files.
  - The pre-registration is still clean, because no N5 gate result exists.
- scratch/run_n5.log already existed, is EMPTY, and was not written by this session.

## Spec issues found by reading code (resolve before rerun)

1. **Step 0, which shard is "shard 1 (seed 100, 4 shards)".** The shards are seeds 100-103
   (generate_dataset.py:340, `args.seed + w`). Shard 1 is seed 100 if counted from 1, or seed 101 if
   counted from 0. Pin which one.
2. **Step 2, the shortcut needs a column that does not exist.** Neither dataset.parquet nor
   sts_n3_floor095.parquet has a Q-limit-hit column (generate_dataset.py make_row, lines 191-207).
   - To find the rows where a generator hit its limit, every row must be replayed and re-solved with the
     pinned solver, as scripts/sts_n2_label_audit.py does.
   - So the shortcut saves only the back-switch solve, not the pinned solve.
3. **Step 2 overlaps N2 on the 0.94 data, and there is no batch driver.**
   - data/sts_n2_label_audit.parquet already holds switch-back labels for dataset.parquet. N2 used the
     pandapower outer loop, not the semismooth solver in scratch/label_crosscheck.py. Decide which
     solver defines the relabel.
   - scratch/label_crosscheck.py samples 200 rows. It has no batch, shard or worker mode, so Step 2
     needs a new driver script.
4. **Step 1, the rule is under-specified for a pre-registration.** Pin these before hashing:
   - Which model family: ridge, histgb, either, or both?
   - Which target is "the held-out operating point"?
   - How is "speedup" defined, e.g. 1/solve_share_B?
   - Which seed std: the 0.95 std, the 0.94 std, or the larger of the two (the CLAUDE.md std rule
     uses the larger)?
   - "Beats the static ranking at matched budget": at which target(s), and judged by the std rule?

# N5b run (prompt: scratch/run_prompt_n5b.md)

## 2026-09-29T00:04:50Z — started
- .venv/bin/python now runs: Python 3.13.11; pandapower 3.5.4, numpy 2.3.5,
  pandas 2.3.3, scikit-learn 1.7.2, pyarrow 21.0.0, numba 0.66.0 (all match CLAUDE.md §6).
  - Python patch differs from the build manifests (3.13.9 recorded; 3.13.11 now). Step 0 tests whether that matters.
- Prompt logged in notes/ai-prompt-log.md entry 2026-09-28 (f).

## 2026-09-29T00:11:30Z — Step 1 done (pre-registration)
- scratch/n5_decision_rule.md written and hashed; sha256 84239071721caded377c5a1e714a1f63e6525e0d5307ade9260b1c8b19dd8e67 in scratch/n5_decision_rule.sha256.
- Hashed before any N5 gate result existed. No N5 surrogate has been trained.
- The owner settled four ambiguities in-session before hashing (all recorded in the file): full tuning
  re-search; clause-2 STD = the larger of the gate and static stds; SAFER judged on the 0.95 data (0.94
  reported); failed relabel rows dropped, stopping if they exceed 0.5%.
- Step 0 (shard-100 rebuild) is running in the background; Step 2 is not started.

## 2026-09-29T00:13:26Z — progress (Steps 0/2/3 prep)
- Step 0 running: scratch/n5_step0_envcheck.py, output in scratch/n5_step0_envcheck.json.
- Step 2 (0.95 relabel) running: scratch/n5_relabel095.py, 4 workers, one shard file per seed in
  scratch/n5_relabel095_shards/.
  - Replay reproduced all 1,500 stored N-0 minima exactly (max diff 0); rejects 168/122/142/139 = 571, which
    matches N3's gate count of 1,500 / 2,071.
  - Step 2 runs alongside Step 0. Its output is used only if Step 0 passes.
- 0.94 labels: N2 file data/sts_n2_label_audit.parquet, 1 failed row of 278,955 N-1 rows (well under 0.5%).
- Step 3 evaluator written: scratch/n5_gate_eval.py. It imports the tune_surrogates search unchanged.
  - Reproduction check against data/tuned_metrics.json (stored labels, seed 0) is running.

## 2026-09-29T00:20:45Z — Step 0 PASSED
- The rebuilt seed-100 shard (375 scenarios, 70,125 rows, 634 columns) is byte-identical to the seed-100
  rows of data/dataset.parquet, checked column by column with sha256 of the raw arrays; DataFrame.equals
  is True.
- Rejects: 375 accepted, 370 rejected, which matches N2's replay count for seed 100.
- Wall time 928 s. Python 3.13.11 (the manifests record 3.13.9); the patch-level difference does not change
  the build.
- Evidence: scratch/n5_step0_envcheck.json. The rebuilt shard is in the session scratchpad, not the repo.

## 2026-09-29T00:27:40Z — Step 3 evaluator verified; 0.94 run started
- Reproduction check (stored labels, seed 0, scratch/n5_gate_094stored_seeds0.json) against the committed
  artifacts:
  - M1/M2 tags and held-out targets match data/tuning_search.json (ridge alpha1 @0.97; histgb rand00 @0.96).
  - Test MAE matches data/tuned_metrics.json exactly.
  - Escalation and missed rate over the 30-level sweep (60 cells): max abs diff 0.
  - static_catch_A/B and solve_share_B match data/sts_matched_budget.json: max abs diff 0.
- Step 3 on the 0.94 switch-back labels launched (5 seeds). Step 2 (0.95 relabel): shard 100 done in 567 s.

## 2026-09-29T01:04:15Z — Step 2 done (0.95 relabel)
- Output: data/sts_n5_relabel095.{parquet,json} plus manifest. Shards 567 / 671 / 928 / 922 s, 4 workers.
- N-1 rows 278,971; failed 0 (0.0%, under the 0.5% ceiling); converged 265,373, not_needed 13,598.
- Pinned re-solve reproduces every stored min_vm exactly (max abs diff 0).
- Flips at 0.94: viol->safe 4,379, safe->viol 1,534 (N2 on the 0.94 data: 4,615 / 2,162).
  - Violation rate: stored 16.006% (matches N3) -> corrected 14.987%.
  - Boundary mass [0.94, 0.945) on the corrected labels: 28.64% (N2 0.94 data, corrected: 56.22%).
  - These are one-build numbers, provisional; Step 4 exists for error bars.
- Step 3 on the 0.95 data launched in parallel with the running 0.94 job (OMP_NUM_THREADS=4 each).
  - The contention affects only the measured t_surr, which enters speedup through n*t_surr and is
    negligible next to t_solve.

## 2026-09-29T02:04:48Z — Step 3, 0.94 run done
- data/sts_n5_gate_094.json plus manifest, wall 5,820 s; the 0.95 run is still going. Verdict pending until both
  finish; per-split values are in the JSON.

## 2026-09-29T02:44:06Z — Step 3 done; pre-registered rule applied
- Outputs: data/sts_n5_gate_095.json (wall 5,960 s) and data/sts_n5_verdict.json, each with a manifest.
  scratch/n5_summarize.py re-verified the rule hash (84239071…) before applying it.
- **SAFER: NO.** Histgb at the held-out point, missed rate per split:
  - 0.95 data: 1.10 / 1.21 / 1.41 / 0.71 / 1.15%, so 1 of 5 splits is <= 1% (4 needed).
  - 0.94 data (reported, not the verdict): 1.11 / 0.98 / 0.34 / 0.95 / 4.16%, so 3 of 5.
- **FASTER: NO.**
  - Clause 1 holds: speedup_B 2.163 ± 0.327 (0.95) vs 1.545 ± 0.225 (0.94); diff 0.617 > STD 0.327.
  - Clause 2 fails: gate catch 98.88 ± 0.23% vs static (rule B) 97.94 ± 0.98%; diff 0.94 pp < STD 0.98 pp,
    so it is a tie under the std rule.
- Full tables (targets 0.90-0.98 plus held-out, both families, rules A/B, static at the matched budget) are in
  data/sts_n5_verdict.json. No decisions taken.

## 2026-09-29T03:10:30Z — Step 4 done; run complete
- Output: data/sts_n5_floor095_seed200.{parquet,json} plus manifest. Seeds 200-203 (new), otherwise the N3
  build-B invocation. Wall 1,563 s. Pinned-solver (stored) labels, like-for-like with N3.
- Build 2 vs build 1 (seeds 100-103), stored labels, converged N-1 rows:

  | Quantity | Build 1 | Build 2 | Mean ± std (ddof=0; ddof=1 in brackets) |
  |---|---|---|---|
  | BM [0.94, 0.945) | 32.954% | 34.817% | 33.89 ± 0.93 [1.32] |
  | CBM | 39.234% | 41.444% | 40.34 ± 1.10 [1.56] |
  | Violation rate | 16.006% | 15.991% | 15.999 ± 0.008 [0.011] |
  | N-0 in strip | 36.87% | 39.13% | |
  | Gate pass | 72.43% | 73.64% | |
  | Nonconverged rows | 29 | 43 | |

- Build 2's deepest min_vm is 0.598 (build 1: 0.715).
- n = 2 builds: these are two-point spreads, not a well-estimated std.
- Build 2 was not switch-back relabeled and not gate-evaluated; the step did not ask for either.
- Files written this run:
  - scratch: n5_step0_envcheck.{py,json}, n5_decision_rule.{md,sha256}, n5_relabel095.py (+ shards dir),
    n5_gate_eval.py, n5_gate_094stored_seeds0.{json,manifest.json}, n5_summarize.py, n5_step4_build.py (+ shards
    dir), and the *.log files.
  - data: sts_n5_relabel095.{parquet,json,manifest.json}, sts_n5_gate_094.{json,manifest.json},
    sts_n5_gate_095.{json,manifest.json}, sts_n5_verdict.{json,manifest.json},
    sts_n5_floor095_seed200.{parquet,json,manifest.json}.
  - notes: this file and ai-prompt-log.md were appended.
- No existing data file, no .tex file, and no git state was changed.

# N9 run (prompt: scratch/run_prompt_n9.md, run in-session on the Mac mini)

## 2026-09-29T23:17:06Z — Step 0 done (environment)
- Python 3.13.11; pandapower 3.5.4, numpy 2.3.5, pandas 2.3.3, scikit-learn 1.7.2, pyarrow 21.0.0, numba 0.66.0.
  All match the N5 run.
- git HEAD 8488e8c9ee18cd03344455bf93d73328cf1df8f9. Clean apart from untracked SAHA.RAJAN.BIB.pdf and report/STS Activities Science Fair Projects.md.

## 2026-09-29T23:17:06Z — Step 1 done (pre-registration)
- scratch/n9_decision_rule.md copied byte-for-byte from the draft.
  - sha256 37a614def80e95df3a00746573933114b93e9402c36f81f7b1dc7c77b3a7fa01, recorded 2026-09-29T23:17:06Z, in scratch/n9_decision_rule.sha256.
- The draft was committed in fb64040027f359efb4d53c00ed07d842185394b5 (2026-09-29T18:41:47-04:00). The working copy is identical to that commit
  (yes).
- Hashed before any N9 model fit or N9 number.

## 2026-09-29T23:19:15Z — progress
- Step 2 running: scratch/n9_relabel.py on D95b.
  - Replay exact: max N-0 diff 0 over 1,500 scenarios; rejects 144/144/110/139 = 537, which matches the build.
- Step 3 running: scratch/n9_budget_curve.py.
  - Seed-0 N5 reproduction on D94 is exact for ridge and histgb (MAE, held-out escalation and missed).
  - D95a check pending.
- Step 4 script written (scratch/n9_shift.py); it runs after Step 3.

## 2026-09-29T23:27:53Z — Step 3 done (Part 1, budget curve; descriptive)
- Output: data/sts_n9_budget_curve.json plus manifest. Wall 549 s.
- N5 reproduction: all 20 (dataset, seed, family) cells are exact (test MAE, held-out escalation, missed),
  not only seed 0.
- Histgb, SURR vs STATIC catch, std-rule verdict per declared k:
  - D94: k = 20, 40, 57 SURR higher; k = 89, 120 STATIC higher. Crossover k = 89.
  - D95a: k = 20, 40 SURR higher; k = 57, 89 tie; k = 120 STATIC higher. Crossover k = 57.
- Ridge: a tie at every k on both datasets (SURR within 0.5 pp of STATIC).
  - Structural reading, not tested: ridge is additive in the branch one-hots, so within a base case its
    ranking is the same fixed element order in every scenario, i.e. a static-type ranking.
- Full table in the JSON. Step 4 launched.

## 2026-09-29T23:37:19Z — Step 4 done (Part 2, shift test; the verdict)
- Output: data/sts_n9_shift.json plus manifest. The rule hash (37a614de…) was re-verified before the verdict.
- Feature alignment: 0 of the D94 kept columns are missing in D95a.
- **SHIFT-ADVANTAGE: NO.** D94 -> D95a, histgb, held-out target, rule B:
  - gate catch 97.24 ± 1.34% vs static 97.06 ± 1.42%;
  - gap 0.18 pp is not > STD 1.42 pp.
- Reported only, histgb D94 -> D95a:
  - solve share B 39.1 ± 4.4%; missed 2.76 ± 1.34%; 0 of 5 splits <= 1%.
  - empirical coverage 0.965 vs target 0.960.
  - degradation vs D95a -> D95a: gate -1.64 ± 1.47 pp; static -0.21 ± 0.13 pp (same k_B).
- Reverse direction D95a -> D94 (reported only):
  - histgb: gate 98.56 ± 0.43 vs static 98.56 ± 0.70, a tie; 1 of 5 splits <= 1%; coverage 0.916 vs target
    0.974.
  - ridge, D94 -> D95a: gate 98.13 ± 0.35 vs static 99.11 ± 0.35 (static higher by the std rule).
  - ridge, reverse: gap -1.22 pp, equal to STD 1.22 pp, so not higher.
- Step 2 (D95b relabel) is still running. Step 5 waits until it finishes.

## 2026-09-29T23:50:40Z — Step 2 done (D95b relabel)
- Output: data/sts_n9_relabel095_seed200.{parquet,json} plus manifest. Shards 552 / 556 / 430 / 417 s.
- Checks: replay N-0 exact; pinned re-solve reproduces every stored min_vm (max diff 0); failed 0 of 278,957
  (0.0%).
- Flips at 0.94: viol->safe 4,474; safe->viol 784.
  - Violation rate: stored 15.991% -> corrected 14.668%.
  - Corrected BM: 30.68%.
- **Deepest stored row** (scenario 202000172, line 78 out; stored 0.598 pu):
  - 5 inconsistent absorbing generators; switch-back converged in 2 outer iterations.
  - Corrected min_vm 0.949 pu, so it is NOT a violation after relabel.
  - Line 78 is also the outage in N2's named worst case (scenario 101000025).
- Steps 0-4 all finished, so Step 5 launched: scratch/n9_build_seed300.py (seeds 300-303).

## 2026-09-30T00:33:48Z — Step 5 done; N9 run complete
- D95c built (seeds 300-303) and relabeled.
  - All checks pass; failed 0.
  - Deepest row goes from 0.658 pu to 0.909 pu corrected, still a violation.
- Part 3 (data/sts_n9_floor_replication.json): all 3 builds fall in the N3 predicted ranges for BM, CBM and VR
  (stored labels). Values over the 3 builds, mean ± std (ddof=0):
  - stored: BM 34.23 ± 0.90, CBM 40.75 ± 1.08, VR 16.01 ± 0.02;
  - corrected: BM 29.76 ± 0.84, CBM 34.91 ± 0.93, VR 14.76 ± 0.17.
- Summary: scratch/n9_result.md. No deviations from the hashed rule. No decisions taken.
