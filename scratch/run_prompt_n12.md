# N12 run — Mac mini: conditional-history baseline, price of a guarantee, cross-network table

## Owner checklist (not part of the prompt)

1. **Review the rule.** Read `scratch/n12_decision_rule_DRAFT.md`, then commit and push it (see the commit
   commands). That commit is the pre-registration.
2. **On the Mac mini:** `git pull` (preserve any Mac-only log entries if git refuses), then start the session
   with `caffeinate -i claude`. Permissions as before.
3. **Paste the prompt below.** Expected time: about 1.5-2 hours. No new power-flow solves.

## Prompt (paste everything below this line)

Read CLAUDE.md, scratch/n12_decision_rule_DRAFT.md, scratch/n10_result.md,
scratch/n11_result.md and notes/overnight_status.md. Use .venv/bin/python.
Write only new files under scratch/ and data/sts_n12_*, with a manifest beside
each data file (include seeds, bins, smoothing and model hyperparameters).
Follow CLAUDE.md §4 code style. No .tex edits, no git writes, no changes to
existing files except appending to notes/ai-prompt-log.md and
notes/overnight_status.md. Log this prompt in notes/ai-prompt-log.md. Append
progress under a new heading "N12 run" in notes/overnight_status.md after
every step.

Do not ask me questions during the run. Handle problems by these rules, and
log every use under "Interpretations and deviations" in
scratch/n12_result.md:
1. If a rule is ambiguous, choose the narrowest reading that skips data rather
   than changing a method, log it, and continue.
2. If a check fails, stop only that network or part, and continue with the
   next. Never change settings to make something pass.
3. Fix bugs in your own new scripts and log them as "deviation (code fix)",
   unless the fix would change a method in the hashed rule.
4. Stop entirely only if the rule hash fails to verify or .venv/bin/python
   stops working.

Step 0 - Environment. Record versions and git HEAD. They must match N11.

Step 1 - Pre-register. Copy scratch/n12_decision_rule_DRAFT.md unchanged to
scratch/n12_decision_rule.md, hash it to .sha256, and record the UTC time and
the commit containing the draft. Do this before any N12 computation.
Re-verify the hash before each verdict.

Step 2 - Loaders and reproduction check. For each of the 4 networks, load the
data and labels exactly as the script that produced its gate results did:
- case118: scratch/n5_gate_eval.py load_relabeled;
- case_illinois200: scratch/n10_gate_illinois.py;
- case30_thermal and case24_ieee_rts: scratch/n11_smallnets.py.
Rebuild the splits and reproduce the existing per-split fixed-budget static
catch at k_B for histgb at the held-out point exactly. Stop any network that
does not reproduce.

Step 3 - Part A (verdict). Write scratch/n12_condhist.py implementing
COND-HIST and GLOBAL-STATIC exactly as in the rule, using each split's gate
s_B from the existing gate outputs. Compute GATE-BEATS-CONDHIST per network
(primary: case_illinois200). Output data/sts_n12_condhist.json plus manifest.

Step 4 - Part B (descriptive). Write scratch/n12_guarantee.py. Refit the
N5/N10 M2 configs per split (no re-search), check that each refit reproduces
the existing held-out escalation and missed exactly, then compute the two
guarantee calibrations from the rule. Output data/sts_n12_guarantee.json plus
manifest.

Step 5 - Part C (descriptive). Write scratch/n12_crossnet.py, building the
4-network table from the rule. Output data/sts_n12_crossnet.json plus
manifest.

Finish by writing scratch/n12_result.md: what ran, each check, the verdicts,
the tables, the interpretations and deviations, and the files written. Give me
the exact git commands to commit and push the N12 files. Report only. Make no
decisions and no paper edits.
