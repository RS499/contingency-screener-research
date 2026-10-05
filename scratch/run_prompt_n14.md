# N14 run — Mac mini: C24 amendment, ILL without trafo 63, islanding sensitivity

## Owner checklist (not part of the prompt)

1. **Review the rule** in `scratch/n14_decision_rule_DRAFT.md`. Every decision is settled (2026-10-05):
   - the C24 amendment and its two disclosure sentences (§A);
   - the trafo-63 exclusion and its post-hoc wording (§B);
   - D94 and C30 restated from N13, provided the hashes match (§B);
   - the sensitivity scope (§B);
   - the classical screen and the D95c gate dropped, both class (b) (§C);
   - replacement (§E);
   - the cutoff: 2026-10-12 23:59 America/New_York (§0).
2. **Commit and push the rule.** That push is the pre-registration.
3. **Confirm on GitHub** that the commit arrived, before you start.
4. **On the Mac mini:** `git pull`, then `caffeinate -i claude`. Permissions as before
   (`Bash(.venv/bin/python:*)`).
5. **Paste the prompt below.** Expected time:
   - ILL full M2 re-search: about 2-2.5 h;
   - C24 and the two small-network sensitivity gates: about 0.5 h each;
   - D94 and ILL sensitivity gates: about 2.5 h each;
   - roughly one night in total.
   - **Restarts:** paste the same prompt; the run resumes from the finished files.

## Prompt (paste everything below this line)

Read CLAUDE.md, scratch/n14_decision_rule_DRAFT.md, scratch/n14_prefacts.md,
scratch/n13_decision_rule.md, scratch/n13_result.md, the hashed rules N13
cites (scratch/n5, n9, n10, n11, n12 _decision_rule.md) and
notes/overnight_status.md ("N13 run"). Use .venv/bin/python. Write only new
files under scratch/ (n14_*) and data/sts_n14_*, with a manifest beside each
data file (include seeds, invocation, candidate grids, selected
hyperparameters, excluded outages and input file hashes). Follow CLAUDE.md §4
code style. No .tex edits, no git writes, no changes to existing files except
appending to notes/ai-prompt-log.md and notes/overnight_status.md. Log this
prompt in notes/ai-prompt-log.md. Append progress under a new heading "N14
run" in notes/overnight_status.md after every step.

This run may span several sessions. On start, read the "N14 run" log and the
existing data/sts_n14_* files, and resume at the first unfinished step. Never
redo a finished output.

Cutoff (rule §0): 2026-10-12 23:59 America/New_York. Check the time before
every step and log it. After the cutoff, finish the step in progress, write
scratch/n14_result.md, and start nothing new. Report anything unfinished as
"not run", never estimated.

Do not ask me questions during the run. Handle problems by these rules, and
log every use under "Interpretations and deviations" in
scratch/n14_result.md:
1. If a rule is ambiguous, choose the narrowest reading that skips data rather
   than changing a method, log it, and continue.
2. If a check fails, stop only that network, arm or analysis, and continue
   with the next. Never change settings to make something pass.
3. Fix bugs in your own new scripts and log them as "deviation (code fix)",
   unless the fix would change a method in the hashed rule.
4. Reuse existing functions by importing them. Where an existing script
   hardcodes a path, write a thin n14_ wrapper. Do not edit any existing
   script.
5. Stop entirely only if the rule hash fails to verify or .venv/bin/python
   stops working.

Step 0 - Environment. Record versions and git HEAD. Pinned versions must
match N13.

Step 1 - Pre-register (first session only). Copy
scratch/n14_decision_rule_DRAFT.md unchanged to scratch/n14_decision_rule.md,
hash it to scratch/n14_decision_rule.sha256, and record the UTC time and the
commit containing the draft. Do this before any N14 computation. Later
sessions re-verify the hash at start and before each verdict.

Step 2 - D94 and C30 hash check (rule §B).
- For every file the rule lists for D94 and C30, compare its sha256 with the
  value in its N13 manifest ("outputs"). Report every comparison.
- If all match, D94 and C30 primary results are restated from N13.
- If any differs, that network is recomputed under the N14 primary
  definition: the N13 §3 tier-A analyses on its N13 dataset, with the full
  M2 re-search.
- Output data/sts_n14_restate_check.json plus manifest.

Step 3 - C24 under the amendment (rule §A).
- Re-run check 3 for C24 from data/sts_n13_C24.parquet,
  data/sts_n13_audit_C24.parquet and the old N11 labels.
- The pinned clause uses a tolerance of 1e-9 pu; the corrected clause is
  unchanged (1e-9 pu).
- Also re-state, from the N13 build files, that every other dataset's
  pinned maximum difference was 0.
- If C24 passes, run its tier-A analyses as rule §A lists, through the N13
  wrappers (scratch/n13_gate.py procedure, then COND-HIST / GLOBAL-STATIC /
  static, then the cross-network row).
- If C24 fails, C24 stays excluded and its analyses are not run.
- Outputs: data/sts_n14_c24_check3.json and, if C24 passes,
  data/sts_n14_gate_C24.json, each with a manifest.

Step 4 - ILL primary without trafo 63 (rule §B).
- Load the rebuilt ILL (data/sts_n13_ILL.parquet) and remove every row of
  each outage that meets the exclusion criterion. Compute the criterion from
  topology and confirm it selects trafo 63 only.
- Run the N13 §3 tier-A analyses that list ILL, with the full M2 re-search:
  - gate;
  - fixed-budget static, COND-HIST, GLOBAL-STATIC;
  - guarantee;
  - cross-network row.
- Outputs: data/sts_n14_gate_ILL.json, data/sts_n14_condhist.json,
  data/sts_n14_guarantee.json, data/sts_n14_crossnet.json, each with a
  manifest.

Step 5 - Sensitivity (rule §B).
- For D94, ILL, C30 and C24 (C24 only if it passed Step 3), remove every
  islanding outage from train, cal and test.
- Run the full N13 arm-S gate procedure, then BEATS-STATIC and
  GATE-BEATS-CONDHIST.
- Do not run N-2, the budget curve, the guarantee or Mondrian here.
- Output data/sts_n14_sensitivity.json plus manifest, with the gate files
  per network.

Step 6 - Descriptive (rule §B). Per network, in primary: catch for gate,
fixed-budget static and COND-HIST on islanding rows and on non-islanding
rows separately (mean ± std over 5 splits). Output
data/sts_n14_islanding_split.json plus manifest.

Step 7 - Verdicts. Re-verify the hash, then apply each definition word for
word:
- primary: BEATS-STATIC per network, SAFER-IL, GATE-BEATS-CONDHIST per
  network (primary: ILL), and the count of networks where the gate wins;
- sensitivity: BEATS-STATIC and GATE-BEATS-CONDHIST per network;
- then the ILL outcome (a), (b) or (c) with its fixed wording.
Output data/sts_n14_verdicts.json plus manifest.

Step 8 - Comparison against N13. For every N14 number that has an N13
counterpart, report both:
- the unpaired std-rule verdict;
- the paired mean ± std over the 5 outer splits.
Output data/sts_n14_compare.json plus manifest.

Finish by writing scratch/n14_result.md: what ran and what did not, each
check with its numbers, each verdict with the numbers it rests on and the
N13 verdict beside it, the disclosure sentences that apply (rule §A), the
tables, the interpretations and deviations, and the files written. Give me
the exact git commands to commit and push the N14 files. Report only. Make
no decisions and no paper edits.
