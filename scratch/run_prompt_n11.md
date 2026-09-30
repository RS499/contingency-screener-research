# N11 run — Mac mini: the seven extra analyses (chains after N10)

## Owner checklist (not part of the prompt)

1. **Review the rule.** Read `scratch/n11_decision_rule_DRAFT.md`, especially the §3 predictions, which are
   Claude's. Change any you'd predict differently. Then commit and push it (together with the N10 draft,
   if N10 hasn't run yet).
2. **On the Mac mini:** `git pull`, then start the session with `caffeinate -i claude`.
3. **Allow unattended runs:** in `/permissions`, allow `Bash(.venv/bin/python:*)` and `Bash(octave:*)`.
4. **Paste the prompt below.** It runs N10 first if N10 hasn't finished, then N11. Expect about 16-18 hours
   in total (N10 about 7, N11 about 10). Don't use the laptop for Claude sessions until it's done.

## Prompt (paste everything below this line)

Read CLAUDE.md, notes/overnight_status.md, scratch/n11_decision_rule_DRAFT.md,
scratch/n9_result.md and scratch/n5_result.md. Use .venv/bin/python for all
Python. Write only new files under scratch/ and data/sts_n11_*, with a manifest
beside each data file (include model hyperparameters, seeds and solver
settings). Follow CLAUDE.md §4 code style. No .tex edits, no git writes, no
changes to existing files except appending to notes/ai-prompt-log.md and
notes/overnight_status.md. Log this prompt in notes/ai-prompt-log.md. Append
progress under a new heading "N11 run" in notes/overnight_status.md after
every step, so a crash only loses the unfinished step. If a script needs
logic from an existing file whose output path is hardcoded, copy the logic
into a new scratch/n11_*.py; never overwrite an existing output. If anything
is ambiguous, ask me instead of guessing.

Step 0 - Order and environment.
- If scratch/n10_result.md does not exist, first carry out
  scratch/run_prompt_n10.md (its prompt section) completely, then continue
  here.
- Record python and package versions and git HEAD. They must match N9.

Step 1 - Pre-register. Copy scratch/n11_decision_rule_DRAFT.md unchanged to
scratch/n11_decision_rule.md, hash it to .sha256, and record the UTC time and
the commit that contains the draft. Do this before any N11 computation.
Re-verify the hash before applying each verdict.

Step 2 - Part 7, solver re-timing (first, while the machine is quiet).
- Write scratch/n11_timing.py: the logic of scripts/sts_n6_warmstart_timing.py
  with a new output path. Follow the load-average rule in the draft.
- Output data/sts_n11_timing.json plus manifest.

Step 3 - Part 4, classical screen on corrected labels.
- Write scratch/n11_classical.py and follow the rule's §4.
- Output data/sts_n11_classical.json plus manifest, including a Table-1-style
  row.

Step 4 - Part 1, the N-2 coverage test (primary verdict).
- Write scratch/n11_n2_build.py: replay the D94 base cases with
  scripts/sts_n2_label_audit.py's replay_shard, and draw the pairs exactly as
  the rule says. Solve each pair with pinned_solve, gen_check and
  corrected_solve from that module (both branches out; restore the state
  after each row). Use 4 workers and save one file per shard.
- Output data/sts_n11_n2_rows.parquet plus manifest.
- Then write scratch/n11_n2_eval.py:
  - build two-hot feature rows from the base case's features in
    data/dataset.parquet;
  - refit the N5 D94 models per split and apply each split's N-1 q̂;
  - compute COVERAGE-HOLDS-N2 and everything reported with it.
- Before the verdict, check that the refit reproduces the N5 N-1 test
  escalation and missed at 0.90 for every split exactly; stop if not.
- Output data/sts_n11_n2.json plus manifest.

Step 5 - Part 6, Mondrian calibration vs static (verdict).
- Write scratch/n11_mondrian.py, per the rule's §2.
- Output data/sts_n11_mondrian.json plus manifest.

Step 6 - Part 2, small networks on corrected labels.
- Relabel case30_thermal, case39 and case24_ieee_rts. Generalize N10's
  Illinois relabel driver if it takes the network as a parameter; otherwise
  write scratch/n11_relabel_net.py. Replay each network's own build exactly:
  - case30_thermal: scripts/case30_thermal_build.py and
    data/case30_thermal/h3_build_stats.json;
  - the others: scripts/netstudy.py phase 1a and their build_stats.json.
- Run the same checks as N10 (replay exact, pinned re-solve exact, failed
  share ≤ 0.5%).
- Then run the N5 protocol on each and recompute the cross-network ρ·q̂
  points.
- Outputs: data/sts_n11_relabel_<net>.{parquet,json} and
  data/sts_n11_smallnets.json, each with a manifest.

Step 7 - Part 3, floor dose-response (verdict).
- Write scratch/n11_floor_build.py, the scratch/n3_floor_rebuild.py logic
  with GEN_VM_LO as an argument and a SHARD_DIR inside scratch/. Build floors
  0.93 and 0.96 (seeds 100-103), then relabel each with the switch-back
  method.
- Compute FLOOR-DOSE-RESPONSE and compare every quantity with the hashed §3
  predictions.
- Outputs: data/sts_n11_floor093.* and data/sts_n11_floor096.* (dataset,
  relabel, summary) and data/sts_n11_dose_response.json, each with a manifest.

Step 8 - Part 5, the gate on D95b and D95c.
- Run the N5 protocol (full tuning search) on each, using the N9 relabels.
- Output data/sts_n11_gate_095bc.json plus manifest.

Finish by writing scratch/n11_result.md: what ran, every check, the three
verdicts (COVERAGE-HOLDS-N2, MONDRIAN-BEATS-STATIC, FLOOR-DOSE-RESPONSE), each
descriptive table, the deviations, and the files written. Report only. Make
no decisions and no paper edits.
