# N13 run — Mac mini: rebuild every dataset with the corrected solver, rerun every analysis

## Owner checklist (not part of the prompt)

1. **Review the rule** in `scratch/n13_decision_rule_DRAFT.md`. The three owner decisions are settled (2026-10-04):
   - the cutoff is 2026-10-14 (§1);
   - a failed non-D94 dataset is excluded (§2; D94 has its own fallback);
   - the rebuilt numbers lead whichever way they move (§6).
2. **Commit and push the rule.** That push is the pre-registration. Check on GitHub that it arrived before
   you start.
3. **On the Mac mini:** `git pull`, then `caffeinate -i claude`. Permissions as before.
4. **Paste the prompt below.** This is a multi-night run.
   - **Night 1:** the tier-A rebuilds. Earlier Mac mini runs took about 1-1.3 h per case118 dataset (build
     plus switch-back), about 2 h for Illinois and about 0.5 h for the two small networks.
   - **Nights 2-3:** the tier-A analyses, then the arm-F diagnostic. The full M2 re-search alone took about
     1.6 h per case118 dataset and 1.6 h for Illinois in N5/N10.
   - **Restarts:** if a session stops, start a new one and paste the same prompt. It resumes from the
     finished files.
5. **Stopping early:** to skip tier B, tell it "stop after the diagnostic". Tier B is then reported as
   "not run".

## Prompt (paste everything below this line)

Read CLAUDE.md, scratch/n13_decision_rule_DRAFT.md, the hashed rules it
cites (scratch/n5, n9, n10, n11, n12 _decision_rule.md), scratch/n5_result.md,
scratch/n9_result.md, scratch/n10_result.md, scratch/n11_result.md,
scratch/n12_result.md, scratch/label_crosscheck.py, scratch/n0drift_check.py
and notes/overnight_status.md. Use .venv/bin/python. Write only new files
under scratch/ (n13_*) and data/sts_n13_*, with a manifest beside each data
file (include seeds, invocation, candidate grids, selected hyperparameters
and input file hashes). Follow CLAUDE.md §4 code style. No .tex edits, no git
writes, no changes to existing files except appending to
notes/ai-prompt-log.md and notes/overnight_status.md. Log this prompt in
notes/ai-prompt-log.md. Append progress under a new heading "N13 run" in
notes/overnight_status.md after every step.

This run spans several sessions. On start, read the "N13 run" log and the
existing data/sts_n13_* files, and resume at the first unfinished step.
Never redo a finished output. Build scripts save one file per shard (or
chunk) and skip finished ones on restart.

Do not ask me questions during the run. Handle problems by these rules, and
log every use under "Interpretations and deviations" in
scratch/n13_result.md:
1. If a rule is ambiguous, choose the narrowest reading that skips data rather
   than changing a method, log it, and continue.
2. If a check fails, stop only that dataset, arm or analysis, and continue
   with the next. Never change settings to make something pass.
3. Fix bugs in your own new scripts and log them as "deviation (code fix)",
   unless the fix would change a method in the hashed rule.
4. Reuse existing functions by importing them. Where an existing script
   hardcodes a path, write a thin n13_ wrapper that calls the same functions
   with the new path. Do not edit any existing script.
5. Dataset files must have exactly the original schema. Audit columns go
   only in data/sts_n13_audit_<name>.parquet (rule §1).
6. Stop entirely only if the rule hash fails to verify or .venv/bin/python
   stops working.

Step 0 - Environment. Record versions and git HEAD. Pinned versions must
match N12.

Step 1 - Pre-register (first session only). Copy
scratch/n13_decision_rule_DRAFT.md unchanged to scratch/n13_decision_rule.md,
hash it to .sha256, and record the UTC time and the commit containing the
draft. Do this before any N13 computation. Later sessions re-verify the hash
at start and before each verdict. Record the rule's cutoff date and check it
at the start of each session and before each step. After the cutoff, finish
the step in progress, write scratch/n13_result.md, and start nothing new
(rule §1).

Step 2 - Check 1 (rule §2). For every dataset in the rule §1 table, replay
the original build N-0 only with the original pinned acceptance and confirm
every stored n0_min_vm reproduces exactly. Output
data/sts_n13_replaycheck.json plus manifest.

Step 3 - Tier-A rebuilds (rule §1), in this order: D94, ILL, C30, C24, D93,
D95a, D96, then N2R on the rebuilt D94 bases.
- Write scratch/n13_build.py (argv: dataset name), which calls each
  dataset's original build functions with the corrected solver for
  acceptance, inputs and labels.
- If D94 fails a check, follow the rule's D94-failure clause (§2): do not
  build N2R, keep checking the other datasets, and report N13 as failed.
- After each dataset, run checks 2-6. For check 6, write
  scratch/n13_indep_check.py, which outputs data/sts_n13_indep_<name>.json
  plus manifest.
- Output per dataset: data/sts_n13_<name>.parquet,
  data/sts_n13_audit_<name>.parquet, and data/sts_n13_build_<name>.json
  (draws, rejections by reason, base-set changes, checks, VR, BM, CBM,
  failed rows, outer iterations), each with a manifest.
- Also count, for each original build, the old rejected draws that pass the
  corrected check (rule §5). Output data/sts_n13_old_rejects.json plus
  manifest.

Step 4 - Tier-A analyses, arm S (rule §3, tier-A rows), each through an
n13_ wrapper. Output data/sts_n13_<analysis>.json plus manifest per
analysis.

Step 5 - Tier-A verdicts (rule §4, the rows on tier-A data). Re-verify the
hash, then apply each definition word for word. Output
data/sts_n13_verdicts.json plus manifest.

Step 6 - Diagnostic, arm F (rule §3). Write scratch/n13_armF.py.
- For D94, ILL, C30 and C24, solve the corrected N-0 state of every
  original base case and write data/sts_n13_armF_<name>.parquet.
- Reproduce the existing held-out missed rates on the original inputs
  exactly, then refit with the corrected inputs.
- Compute V3, the drift tables (both binnings) and the paired differences.
  Output data/sts_n13_armF.json plus manifest.

Step 7 - Tier B (unless I said "stop after the diagnostic"): rebuild D95b
and D95c with checks 2-6, then run the tier-B analyses and verdicts, as in
Steps 3-5.

Step 8 - Comparison (rule §5). Write scratch/n13_compare.py: old vs
rebuilt, side by side, for every number in the paper's tables, unpaired,
with the std rule applied. Output data/sts_n13_compare.json plus manifest.

Finish by writing scratch/n13_result.md: what ran and what did not, each
check with its numbers, each verdict with the numbers it rests on and the
old-build verdict beside it, the tables, the interpretations and
deviations, and the files written. Give me the exact git commands to commit
and push the N13 files. Report only. Make no decisions and no paper edits.
