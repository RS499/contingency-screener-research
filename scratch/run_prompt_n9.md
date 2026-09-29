# N9 run — Mac mini

## Owner checklist before starting (not part of the prompt)

1. **Review the rule.** Read `scratch/n9_decision_rule_DRAFT.md` and edit anything you disagree with. Once
   it's final, commit and push it: that commit is your git-timestamped pre-registration.
2. **Pull on the Mac mini,** so it has the draft, the N5 outputs and the current `notes/`.
3. **Allow Python for the run.** Let the session run `.venv/bin/python` without asking; the first N5 night
   died at Step 0 on this. Either add a project permission allow rule for it, or start the session
   interactively and approve the first call with "always allow".
4. **Stop the Mac mini sleeping.** Start the session under `caffeinate -i`, or set it to never sleep on power.
5. **Use one machine.** Don't run a Claude session on the laptop until you've pushed from the Mac mini and
   pulled on the laptop (this keeps `notes/ai-prompt-log.md` from forking).

## Prompt (paste everything below this line)

Read CLAUDE.md, scratch/n9_decision_rule_DRAFT.md, scratch/n5_result.md,
notes/overnight_status.md and data/sts_n5_verdict.json. Use .venv/bin/python
for everything. Write only new files under scratch/ and data/sts_n9_* with a
manifest beside each data file (include the model hyperparameters). Follow the
course-style code rules in CLAUDE.md §4. No .tex edits, no git writes, no
changes to existing files anywhere except appending to notes/ai-prompt-log.md
and notes/overnight_status.md. Log this prompt in notes/ai-prompt-log.md.
Append progress to notes/overnight_status.md under a new heading "N9 run"
after each step, so a crash only loses the unfinished step. If anything is
ambiguous, ask me instead of stopping or guessing.

Step 0 - Environment. Record python and package versions and git HEAD. They
must match the N5 run (Python 3.13.11; pandapower 3.5.4, numpy 2.3.5, pandas
2.3.3, scikit-learn 1.7.2, pyarrow 21.0.0, numba 0.66.0). If .venv/bin/python
cannot run, write that to notes/overnight_status.md and stop.

Step 1 - Pre-register. Copy scratch/n9_decision_rule_DRAFT.md unchanged to
scratch/n9_decision_rule.md, hash it to scratch/n9_decision_rule.sha256 and
record the UTC time. Do this before any N9 model is fit or any N9 number is
computed. If git shows the draft was committed, record that commit hash too.
The rule file is final; do not edit it after hashing.

Step 2 - Relabel D95b (data/sts_n5_floor095_seed200.parquet, shard seeds
200-203, GEN_VM_LO = 0.95) with the N2 switch-back method. Write a new driver,
scratch/n9_relabel.py, that takes the dataset path, shard seeds and output
path as arguments and otherwise does what scratch/n5_relabel095.py does
(replay with the floor set inside each worker, n2.audit_scenario unchanged,
4 workers, one shard file per seed, skip finished shards on restart).
Required checks:
- the replay reproduces every stored N-0 minimum exactly;
- the pinned re-solve reproduces every stored min_vm exactly;
- the failed share is at most 0.5%, else stop and report.
Output data/sts_n9_relabel095_seed200.{parquet,json} plus manifest. Report
the corrected value of the build's deepest row (stored 0.598 pu).

Step 3 - Part 1 of the rule (budget curve), on D94 and D95a, both families,
5 splits. Reuse the N5 M2 selections from data/sts_n5_gate_094.json and
data/sts_n5_gate_095.json; refit and calibrate as the rule says. Before any
new number, reproduce, for seed 0 and each family and dataset, the N5 test
MAE and the held-out escalation and missed rate from those JSONs exactly. If
they do not match, stop and report. Output data/sts_n9_budget_curve.json plus
manifest: SURR, STATIC and ORACLE catch at k in {20, 40, 57, 89, 120}, the
per-k std-rule verdicts, the crossover budget, and the full k = 1..186
curves.

Step 4 - Part 2 of the rule (shift test, D94 -> D95a), exactly as written in
scratch/n9_decision_rule.md. Also run the reverse direction and ridge as
reported-only items. Output data/sts_n9_shift.json plus manifest. Apply the
hashed rule, after re-verifying its sha256, and state the SHIFT-ADVANTAGE
outcome in one line.

Step 5 - Only if Steps 0-4 finished: build D95c, a third 0.95-floor dataset
with shard seeds 300-303 and the same invocation as
scratch/n5_step4_build.py. Use a new script, scratch/n9_build_seed300.py, and
set SHARD_DIR inside scratch/ at run time. Relabel it with
scratch/n9_relabel.py. Then compute Part 3 of the rule over D95a, D95b and
D95c (stored and corrected labels) and compare each build with the hashed N3
prediction. Output data/sts_n9_floor_replication.json plus manifest.

Finish by writing scratch/n9_result.md: what ran, each check, the Part 1
table, the SHIFT-ADVANTAGE outcome, the Part 3 table, and the files written.
Report only. Make no decisions and no paper edits.
