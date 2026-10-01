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

# N10 run (prompt: scratch/run_prompt_n10.md, run in-session on the Mac mini)

## 2026-09-30T21:12:28Z — Step 0 done (environment)
- Python 3.13.11; pandapower 3.5.4, numpy 2.3.5, pandas 2.3.3, scikit-learn 1.7.2, pyarrow 21.0.0, numba 0.66.0.
  All match N9.
- git HEAD 7f2c289d94e06283125c9c35cabe110a44569c6a.
  - Working tree: .claude/settings.json modified (owner's /permissions edit); two untracked owner files.
- GNU Octave 11.3.0 (aarch64-apple-darwin25.4.0); MATPOWER 8.1 (12-Jul-2025) at ~/matpower.

## 2026-09-30T21:12:28Z — Step 1 done (pre-registration)
- scratch/n10_decision_rule.md copied byte-for-byte from the draft.
  - sha256 7f94bd0a8958c011832895caded9db3275681ceae402e92913b3a3467e2f8907, recorded 2026-09-30T21:12:28Z.
- The draft was committed in 7f2c289 (2026-09-30T17:00:11-04:00); the working copy matches that commit.
- Hashed before any N10 computation.

## 2026-09-30T21:20:40Z — Step 2 done (Part A, MATPOWER check)
- Scripts: scratch/n10_matpower_check.py and scratch/n10_switchback.m. Output: data/sts_n10_matpower_check.{parquet,json}
  plus manifest. MATPOWER 8.1, Octave 11.3.0. The rule hash was re-verified.
- Rows: 201 (100 viol->safe, 100 safe->viol, plus the named worst case). Every M0/M1/M2 solve converged.
- **A0 PASS:** 201/201 within 1e-6 of pandapower's no-limit min_vm (max diff 2.05e-7); CP95 [0.982, 1].
- **A1 PASS:** M1 (MATPOWER one-way) label = stored label on 201/201 (max |M1 - stored| 1.58e-6 pu);
  CP95 [0.982, 1].
- **A2 CONFIRMED:**
  - M2 (MATPOWER + switch-back) label = N2 label on 201/201 (max |M2 - N2| 5.6e-7 pu); CP95 [0.982, 1].
  - Named worst case: M2 min_vm 0.94507 (N2 0.94507; stored 0.84854) after 3 outer iterations, >= 0.94.
- Implementation notes, fixed before any N10 number:
  - to_mpc needs init='flat' (it accepts only 'flat' or 'results').
  - The slack generator's Q limits are set to +/-Inf for M1/M2, because pandapower never Q-limits the
    ext_grid.
  - MATPOWER NR is set to tol 1e-8 and max_it 30.
  - A non-converged MATPOWER solve would count as a check failure; none occurred.

## 2026-09-30T21:39:17Z — Step 5 done early (Part C, paper artifacts; no verdict)
- Order note: Part C was run while Part B was still computing, because it uses no Part B output. Nothing in Part
  C feeds a verdict.
- Script: scratch/n10_paper_artifacts.py. Every refit reproduces the N5 test MAE exactly (checked in code).
- Outputs (each with a manifest):
  - data/sts_n10_fig_tradeoff.{png,json}: first sub-1% missed coverage is ridge 0.96, histgb 0.97.
  - data/sts_n10_fig_missdepth.{png,json}: at 0.90, pooled over 5 seeds.
    - ridge 1,528 misses, max depth 0.0475 pu; histgb 1,936 misses, max depth 0.0682 pu.
    - No miss lies beyond the 0.095 x-range.
  - data/sts_n10_fig_boundary.{png,json}: 278,954 rows; BM 56.22%; VR 16.60%.
  - data/sts_n10_fig_budget.{png,json}: from data/sts_n9_budget_curve.json. The ridge curve lies under the
    static curve.
  - data/sts_n10_tables.tex (+ .json): tab:ops and tab:models bodies on corrected labels.
- Train-mean baseline: on stored labels it flagged every row (escalation 0, speedup about 2e7). On corrected
  labels it escalates every row (escalation 100%, speedup 1.00).
- Persistence and train-mean were recomputed on corrected labels, not copied from the stored-label rows.

## 2026-09-30T21:56:50Z — Step 4 pre-check PASSED (stored labels)
- scratch/n10_gate_illinois.py check, seed 0, full tune_surrogates search on stored labels.
  - Reproduces data/netstudy2/case_illinois200/frozen.json exactly at 0.90: escalation, missed rate and test
    index hash (2c89a6175379f94a), for ridge and histgb.
  - Evidence: scratch/n10_gate_illinois_check.json.
- M2 tags were not recorded in frozen.json, so they could not be compared. This run picked ridge alpha316.2 and
  histgb rand13.
- The corrected-label run waits for the relabel (Step 3, about 15/30 chunks done).

## 2026-09-30T22:17:48Z — Step 3 done (Part B relabel, case_illinois200)
- Script: scratch/n10_relabel_illinois.py. Output: data/sts_n10_relabel_illinois200.{parquet,json} plus
  manifest. Wall about 3,800 s.
- Replay exact: 7,880 draws; rejects 9 / 6,359 / 12 as stored; all 1,500 N-0 minima diff 0.
- Pinned re-solve reproduces every stored min_vm (max diff 0). All 360,589 converged N-1 rows audited; failed 0.
- Switch-back needed on 275,323 rows. Flips: viol->safe 27,478; safe->viol 0.
  - Violation rate: stored 29.28% -> corrected 21.66%.
  - BM [0.94, 0.945): stored 19.33% -> corrected 14.31%.
- Implementation note, fixed before any N10 number: the N2 logic was copied with the network as a parameter.
  - N2's add_pq_sgens/apply_fixed switch every sgen (case118 has none).
  - Illinois has 11 own sgens, so here only the helper sgens are switched.
- Step 4 (corrected labels, 5 seeds) launched with OMP_NUM_THREADS=8.

## 2026-09-30T22:25:30Z — owner request: N10 Part C vs data/sts_paper_* (numbers only)
- Written to scratch/n10_vs_paper_check.md (script scratch/n10_vs_paper_check.py, read-only).
- All compared values agree:
  - Fig. 2: max diff 1.1e-16. Fig. 3 and 4: exactly equal.
  - tab:ops: 12/12 rows identical text.
  - tab:models: numerically equal. One sign-format difference (train-mean R2 -0.000334 printed -0.00 vs 0.00).
    Baseline speedup_A differs by <= 1.35e-6 from the wall-clock t_surr.
- The budget JSON on your side has no curve values, so those were not comparable.
- data/sts_paper_* sha256 unchanged.

## 2026-09-30T23:53:48Z — Step 4 done (Part B evaluation, case_illinois200, corrected labels)
- Output: data/sts_n10_illinois.json plus manifest. The rule hash (7f94bd0a…) was re-verified before the
  verdicts.
- **BEATS-STATIC-IL: YES.** Histgb, held-out, rule B:
  - gate catch 99.04 ± 0.22% vs static at k_B 88.90 ± 1.20%;
  - gap 10.14 pp > STD 1.20 pp.
- **SAFER-IL: NO.** Histgb held-out missed per split 1.19 / 0.85 / 0.59 / 1.14 / 1.04%, so 2 of 5 splits are
  <= 1% (4 needed).
- Descriptive (no verdict):
  - Budget curve, k = 26/53/75/117/158: SURR vs STATIC is a tie at every k, for both families. Crossover =
    26 (SURR never "higher").
  - Violation concentration (top-5 / top-10 elements by train frequency):
    - Illinois: 9.2% / 18.4%.
    - case118 D94 corrected: 16.5% / 32.9%.
  - Any-miss share of test base cases at the held-out point:
    - Illinois: histgb 23.9 ± 4.9%, ridge 20.4 ± 3.5%.
    - case118: histgb 17.1 ± 7.2%, ridge 11.4 ± 2.2%.
- N10 complete; writing scratch/n10_result.md.

## 2026-09-30T23:54:42Z — N10 complete; scratch/n10_result.md written

# N11 run (prompt: scratch/run_prompt_n11.md, chained after N10 in-session on the Mac mini)

## 2026-09-30T23:54:42Z — Step 0 done (order and environment)
- scratch/n10_result.md exists, so N10 is not re-run.
- Environment: Python/pandapower/numpy/pandas/sklearn/pyarrow/numba = 3.13.11 3.5.4 2.3.5 2.3.3 1.7.2 21.0.0 0.66.0 (matches N9).
- git HEAD af7dcbac0f4c7b89963898f491528334e0f397a1. The working tree carries the uncommitted N10 files and the appended notes.

## 2026-09-30T23:54:42Z — Step 1 done (pre-registration)
- scratch/n11_decision_rule.md copied byte-for-byte from the draft.
  - sha256 4a0e48d47d1c1b8a053dedd6036977c60ede4957dbcb6f542356552a64f0775d, recorded 2026-09-30T23:54:42Z.
- The draft was committed in af7dcbac0f4c7b89963898f491528334e0f397a1 (2026-09-30T18:17:59-04:00); the working copy matches that commit (yes).
- Hashed before any N11 computation.

## 2026-09-30T23:59:43Z — Step 2 done (Part 7, solver re-timing)
- Script: scratch/n11_timing.py (N6 logic, new output path). Output: data/sts_n11_timing.json plus manifest.
  Wall 95 s.
- Load rule: waited 180 s; 1-min load 1.93 at start (quiet reached); 2.29 at the end.
- **Hardware: Apple M4 (Mac mini).** The committed data/solve_time.json and dataset manifests record an Apple M5.
- Per solve, cold (pinned): min 8.96 / median 11.09 ms. Warm: min 7.53 / median 9.53 ms.
  - Committed ms_solver 9.14 (min), median 9.512.
  - N6 (M5): cold min 7.53 / median 9.25; warm 6.38 / 7.98.
- 186-outage sweep median: cold 2,082 ms, warm 1,804 ms.
- Cold vs warm agreement: 2,232 pairs, max |min_vm diff| 4.3e-15, 0 label differences.

## 2026-09-30T23:59:55Z — Step 3 done (Part 4, classical screen on corrected labels)
- Script: scratch/n11_classical.py. Output: data/sts_n11_classical.json plus manifest.
- Stored-label check: reproduces data/classical_screen_metrics.json (fit MAE/R2, conformalized @0.90) exactly
  (max diff 0).
- Corrected labels @0.90: MAE 3.68 ± 0.06 mV; R2 0.135 ± 0.007; escalation 90.7 ± 1.1%; missed 1.83 ± 0.57%;
  speedup A 1.10 ± 0.01; speedup B 1.04 ± 0.01.
- Table-1-style row (in the JSON): classical (linearized) & 3.7±0.1 & 0.14±0.01 & 90.7±1.1 & 1.83±0.57 & 1.10±0.01.
- Launched Step 4 (N-2 build) and the Step 7 floor-0.93 build in parallel (4 workers each; independent jobs).

## 2026-10-01T00:09:33Z — Step 5 done (Part 6, Mondrian vs static; verdict)
- Script: scratch/n11_mondrian.py. Output: data/sts_n11_mondrian.json plus manifest.
  - The rule hash (4a0e48d4…) was re-verified.
  - The global-q refit reproduces the N5 held-out numbers in every split (checked in code).
- Every one of the 186 elements had >= 20 cal rows in every split, so the global fallback was never used.
- **MONDRIAN-BEATS-STATIC: NO.** Histgb, held-out, rule B:
  - gate catch 98.24 ± 1.43% vs static at the Mondrian k_B 98.07 ± 1.12%;
  - gap 0.17 pp is not > STD 1.43 pp.
- Reported alongside (histgb, Mondrian vs global q):
  - escalation 37.0 ± 7.1% vs 50.2%; missed 1.76 ± 1.43% vs 1.51%; <= 1% in 3/5 splits;
  - speedup B 1.93 ± 0.24 vs 1.55.
- Ridge, Mondrian: catch 97.71 ± 0.49% vs static 99.15 ± 0.43%; 0/5 splits <= 1%.

## 2026-10-01T00:15:02Z — Step 4a done (Part 1, N-2 build)
- Script: scratch/n11_n2_build.py. Output: data/sts_n11_n2_rows.{parquet,json} plus manifest. Wall 874 s.
- Replay exact: 1,500 D94 bases, N-0 diff 0. Pairs: 50 per base, numpy seed 20261001, so 75,000 rows.
- Pinned nonconverged: 79 (0.105%), kept and marked.
- Corrected-solve failures among converged: 1 (0.0013%, under the 0.5% ceiling).
- Corrected N-2 violation rate 30.18% (pinned 32.04%). Adjacent pairs (sharing a bus): 3.33%.

## 2026-10-01T00:17:29Z — Step 4b: implementation fix in scratch/n11_n2_eval.py (before any verdict)
- First run stopped at its own pre-verdict check: seed 2 ridge did not reproduce N5 N-1 test numbers at 0.90
  exactly (seeds 0-1 and seed 2 histgb did).
- Cause: the script predicted N-1 and N-2 rows as ONE stacked matrix. For a linear model that changes the BLAS
  blocking of the matmul, so a prediction can move by an ulp and cross the q_hat threshold.
- Fix: same fitted model, N-1 and N-2 rows predicted separately (as N9 did).
- No definition in the hashed rule changed and no verdict had been computed. Logged here as an implementation
  fix; the owner may judge whether to call it a deviation.

## 2026-10-01T00:22:53Z — Step 4 done (Part 1, N-1 -> N-2 coverage; primary verdict)
- Script: scratch/n11_n2_eval.py (with the fix above). Output: data/sts_n11_n2.json plus manifest.
  - The rule hash was re-verified.
  - All 10 (split, family) refits reproduce N5 N-1 test escalation and missed at 0.90 exactly.
  - Two-hot encoding: 0 missing branch columns.
- **COVERAGE-HOLDS-N2: NO** ("coverage does not hold under N-2"). Histgb at 0.90:
  - N-2 coverage 0.8346 ± 0.0181 vs threshold 0.90 - max(0.0181, N-1 std 0.0173) = 0.8819;
  - shortfall 0.047. N-1 coverage on the same splits: 0.8981 ± 0.0173.
- Reported without verdict:
  - histgb held-out (target 0.960): N-2 coverage 0.917 ± 0.025 (N-1 0.959); missed 1.64 ± 0.91%; <= 1% in 1/5.
  - histgb at 0.90: N-2 missed 3.95 ± 1.06% (0/5 <= 1%); escalation 23.0%.
  - ridge at 0.90: N-2 coverage 0.611 ± 0.020 (N-1 0.889); missed 11.67 ± 0.80%.
  - ridge held-out: N-2 coverage 0.719; missed 7.46%.
  - Adjacent pairs vs non-adjacent, histgb 0.90: 0.818 vs 0.835. N-2 violation rate 30.0%.
  - N-2 rows used: 74,920 of 75,000 (79 pinned nonconverged, 1 corrected failure).

## 2026-10-01T00:23:20Z — Step 7a: floor 0.93 build done
- Script: scratch/n11_floor_build.py 0.93. Output: data/sts_n11_floor093.{parquet,json} plus manifest.
- Stored BM 58.07% (summary in the JSON). Relabel running; then the 0.96 build and its relabel.

## 2026-10-01T00:35:57Z — Step 6: case30_thermal relabel PASSED; case39 relabel STOPPED (failed share > 0.5%)
- case30_thermal (data/sts_n11_relabel_case30_thermal.*): replay exact (8,050 draws, rejects as stored); every
  check passes.
- **case39** (data/sts_n11_relabel_case39.*):
  - Replay exact (2,092 draws); pinned re-solve exact (max diff 0); all 67,050 rows audited.
  - Switch-back failures: 728 = 1.09% (421 nonconverged, 307 at the 30-iteration cap). That is above the
    0.5% ceiling, so by rule §0 case39's part STOPS and reports.
  - Of the rows that did settle: flips viol->safe 52, safe->viol 0; VR 20.74% -> 19.99%; BM 4.43% -> 4.44%.
- Ambiguity raised with the owner: does "that part stops" stop all of Part 2, or only case39?
  - case24_ieee_rts relabel is running meanwhile (data only).
  - The Part 2 evaluation is held until the owner answers.

## 2026-10-01T00:51:24Z — Step 6: owner decision on case39; failure characterization
- **Owner decision (interpretation, NOT a rule change):** §0's 0.5% ceiling is applied per dataset, so case39 is
  excluded from the Part 2 evaluation. The iteration cap was not raised and case39 was not rerun.
- **case39 failure facts:** 728 / 67,050 = 1.09%.
  - 307 at the 30-iteration cap: 296 stuck with the same inconsistent-generator count every outer iteration
    (period 1, i.e. not oscillating but not changing state); 8 period-2 oscillations; 3 other.
  - 421 nonconverged: 394 (93.6%) fail at the first switch-back solve, 26 at the second, 1 at the third.
  - 81% of failed rows were stored violations. They span 581 base cases.
  - Concentrated by outage: trafo 10 = 437, trafo 6 = 75, trafo 8 = 70, trafo 7 = 43, trafo 9 = 36.
- case24_ieee_rts relabel: replay exact (8,348 draws); every check passes.
- The Part 2 evaluation now runs on case30_thermal and case24_ieee_rts, plus the cross-network points for the
  networks that pass (and case118, Illinois).

## 2026-10-01T00:51:36Z — owner rules for the rest of N11 (no questions)
- Five rules adopted (verbatim in notes/ai-prompt-log.md entry (l)): interpretation; per-dataset/step stop;
  code-fix deviation; whole-run stop conditions; finish then git commands.
- Earlier events classified under these rules:
  - Step 4b, n11_n2_eval.py separate prediction: **deviation (code fix)**, rule 3. A bug in my new script; no
    hashed method changed. The pre-verdict check stopped it before any verdict.
  - Step 6, case39 excluded: **interpretation** (owner-chosen, consistent with rule 1/2); the ceiling is
    applied per dataset.
- Disk check (rule 4): 85Gi free.

## 2026-10-01T01:10:28Z — Step 6 done (Part 2, small networks on corrected labels; descriptive)
- Script: scratch/n11_smallnets.py. Output: data/sts_n11_smallnets.json plus manifest. case39 is excluded
  (interpretation above).
- **case30_thermal relabel:** failed 0; flips viol->safe 8, safe->viol 0; VR 15.40 -> 15.38%; BM 7.09 -> 7.10%.
- **case30_thermal histgb:**
  - held-out (target 0.972): escalation 6.2 ± 2.8%; missed 0.63 ± 0.31% (4/5 <= 1%); speedup A 19.34, B 4.76;
    gate catch 99.37 vs static 84.09 (gate higher).
  - At 0.97 (abstract number on corrected labels): escalation 4.6 ± 0.4%; missed 0.66 ± 0.17% (5/5); speedup A
    21.60.
  - First target with mean missed < 1%: histgb 0.96, ridge 0.98.
- **case24_ieee_rts relabel:** failed 28 (0.05%); flips viol->safe 6,988, safe->viol 1,422; VR 58.06 -> 47.88%;
  BM 20.70 -> 20.94%.
- **case24_ieee_rts histgb:**
  - held-out (target 0.886): escalation 16.9 ± 1.1%; missed 0.98 ± 0.18% (2/5 <= 1%); speedup A 5.93, B 1.54;
    gate catch 99.02 vs static 92.48 (gate higher).
  - First mean missed < 1%: 0.90 for both families.
- Cross-network rho*q_hat points on corrected labels: 72 points (case118, case_illinois200, case30_thermal,
  case24_ieee_rts).

## 2026-10-01T01:57:09Z — Step 7 done (Part 3, floor dose-response; verdict)
- Builds: scratch/n11_floor_build.py → data/sts_n11_floor093.* (wall 1,393 s) and data/sts_n11_floor096.*.
- Relabels: scratch/n11_relabel_floor.py → data/sts_n11_floor09{3,6}_relabel.*. Every check passes.
  - 0.93: failed 0. 0.96: failed 1 row, which is the build's deepest stored row (0.694 pu; no corrected value).
- Verdict output: scratch/n11_dose_response.py → data/sts_n11_dose_response.json. The rule hash was re-verified.
- **FLOOR-DOSE-RESPONSE: YES.**
  - Clause 1: BM(0.96) 19.91% < BM(0.95) 32.95% - 5 pp.
  - Clause 2: |BM(0.93) 58.07% - BM(0.94) 56.86%| = 1.21 <= 5 pp.
  - On corrected labels (reported only) both clauses also hold: BM 56.42 / 56.22 / 28.64 / 15.75 for
    0.93/0.94/0.95/0.96.
- vs the hashed §3 predictions (stored), all 6 in range:
  - 0.93: BM 58.07 [50-62]; CBM 70.20 [62-73]; VR 17.28 [15.5-19.5].
  - 0.96: BM 19.91 [8-30]; CBM 23.28 [10-36]; VR 14.46 [12-17.5].
- Other facts:
  - N-0 gate pass: 0.93 23.89%; 0.96 82.10%. N-0 bases in the strip: 69.3% vs 20.3%.
  - 0.93 relabel flips viol->safe 4,168 and safe->viol 5,222; 0.96: 3,503 and 621.

## 2026-10-01T03:00:37Z — Step 8 done (Part 5, gate on D95b and D95c; descriptive)
- Script: scratch/n11_gate_095bc.py (N5 protocol, full search). Output: data/sts_n11_gate_095bc.json plus
  manifest. 0 failed relabel rows dropped on either build.
- **D95b histgb held-out:** escalation 35.2 ± 5.0%; missed 0.92 ± 0.30% (per split 0.81/1.14/1.27/0.97/0.40);
  speedup B 2.04 ± 0.19; gate catch 99.08 vs static 98.53.
  - N5 rules (replication of N5 rule, not a new verdict): SAFER no (3/5); FASTER no (clause 1 holds, clause 2
    tie).
- **D95c histgb held-out:** escalation 34.5 ± 14.4%; missed 2.13 ± 1.39% (2.16/3.94/0.61/3.40/0.55); speedup B
  2.21 ± 0.51; gate catch 97.87 vs static 97.70.
  - N5 rules (replication): SAFER no (2/5); FASTER no (clause 1 holds, clause 2 tie).
- **Across D95a/b/c** (build means, ddof=0 [ddof=1]):
  - escalation 34.30 ± 0.83 [1.02]%; missed 1.39 ± 0.53 [0.65]%; speedup B 2.136 ± 0.073 [0.089];
  - gate catch 98.61 ± 0.53%; static catch 98.06 ± 0.35%.
- **N11 complete.** Every step ran; case39 was excluded from Part 2 (interpretation). Disk 84 GB free.
