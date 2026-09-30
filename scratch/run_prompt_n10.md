# N10 run — Mac mini (items 9 and 10, plus the paper figures on corrected labels)

## Owner checklist before starting (not part of the prompt)

1. **Review the rule.** Read `scratch/n10_decision_rule_DRAFT.md` and edit it if needed. Then commit and push
   it: that commit is the git-timestamped pre-registration.
2. **Install the independent solver (Part A only), once, by hand:**
   - `brew install octave` (a large download, about 20-40 minutes).
   - Download MATPOWER 8.x from matpower.org, unzip it to `~/matpower`, then check that it runs:
     `octave --no-gui --eval "addpath(genpath('~/matpower')); mpver"`
   - If you skip the install, Part A is skipped and B and C still run.
   - Before MATPOWER appears in the paper, its citation must be verified in `notes/prior-art.md`; don't cite
     it from memory.
3. **Pull on the Mac mini.**
4. **Let the session run without prompts:** allow `.venv/bin/python` and `octave` to run without asking.
5. **Keep the Mac mini awake** under `caffeinate -i`.
6. **Leave the laptop idle** until the results are pushed from the Mac mini and pulled on the laptop.

Expected wall time: Part A about 1 h, Part B about 5-6 h (relabel about 2 h, tuning search about 3 h).
Part C is skipped: it was already done on the laptop.

## Prompt (paste everything below this line)

Read CLAUDE.md, scratch/n10_decision_rule_DRAFT.md, scratch/n9_result.md,
scratch/n5_result.md and notes/overnight_status.md. Use .venv/bin/python for
all Python, and octave only for Part A. Write only new files under scratch/ and
data/sts_n10_*, with a manifest beside each data file (include model
hyperparameters and solver settings). Follow CLAUDE.md §4 code style. No .tex
edits, no git writes, no changes to existing files except appending to
notes/ai-prompt-log.md and notes/overnight_status.md. Log this prompt in
notes/ai-prompt-log.md. Append progress under a new heading "N10 run" in
notes/overnight_status.md after each step. If anything is ambiguous, ask me
instead of guessing.

Step 0 - Environment. Record python and package versions, git HEAD, and
"octave --version" plus the MATPOWER version (mpver), if present. The Python
versions must match N9. If .venv/bin/python cannot run, write that to
notes/overnight_status.md and stop.

Step 1 - Pre-register. Copy scratch/n10_decision_rule_DRAFT.md unchanged to
scratch/n10_decision_rule.md, hash it to .sha256, record the UTC time and the
commit that contains the draft. Do this before any N10 computation.

Step 2 - Part A (skip it, and say so, if octave or MATPOWER is missing).
- Write scratch/n10_matpower_check.py and one Octave script,
  scratch/n10_switchback.m.
- For the 200 rows in data/sts_label_crosscheck_rows.parquet and the named
  worst case: rebuild each case as scratch/label_crosscheck.py does, export
  it with pandapower.converter.to_mpc, and run the three MATPOWER solves
  M0 / M1 / M2 defined in the rule.
- Apply the pre-declared checks A0, A1 and A2, with Clopper-Pearson
  intervals.
- Output data/sts_n10_matpower_check.{json,parquet} plus manifest.

Step 3 - Part B relabel.
- Write scratch/n10_relabel_illinois.py. It replays the case_illinois200 build
  of scripts/netstudy.py phase 1a exactly: one RNG stream, seed 100, the
  chosen window from data/netstudy/case_illinois200/build_stats.json, the
  voltage and thermal N-0 gate (case30_thermal.n0_feasible), and the same
  mode alternation.
- Then re-solve every converged N-1 row with the pinned solver and apply the
  N2 switch-back loop. Copy the logic of scripts/sts_n2_label_audit.py, but
  make the network a parameter (the original hardcodes case118). Use 4
  workers and save progress per chunk of scenarios.
- Required checks:
  - the replay reproduces every stored N-0 minimum;
  - the pinned re-solve reproduces every stored min_vm exactly;
  - the failed share is at most 0.5%, else stop.
- Output data/sts_n10_relabel_illinois200.{parquet,json} plus manifest.

Step 4 - Part B evaluation.
- Write scratch/n10_gate_illinois.py, following the N5 protocol as defined in
  the rule: full tuning search, M2, held-out target, targets 0.90-0.98, rules
  A and B, static at matched budget.
- Before any new number, check the script on stored labels: reproduce
  data/netstudy2/case_illinois200/frozen.json escalation and missed rate at
  0.90 for seed 0 (and the M2 tags, if they were recorded). If it does not
  match, stop and report.
- Then compute BEATS-STATIC-IL and SAFER-IL. Re-verify the rule hash before
  applying them.
- Also compute the declared budget curve, violation concentration (Illinois
  and case118 D94 corrected) and the operator any-miss metric (both
  networks).
- Output data/sts_n10_illinois.json plus manifest.

Step 5 - Part C: SKIP. The corrected-label figures and table bodies were already produced
on the laptop (scripts/sts_paper_corrected.py -> data/sts_paper_*). Do not rebuild them.

Finish by writing scratch/n10_result.md: what ran, each check, the Part A
verdicts, the two Part B verdicts, the Part B descriptive tables, the Part C
file list, and the deviations. Report only. Make no decisions and no paper
edits.
