Read CLAUDE.md, scratch/n3_floor_result.md, data/sts_label_crosscheck.json and
data/sts_matched_budget.json. Use .venv/bin/python for everything. Write only new
files under scratch/ and data/sts_* with a manifest beside each data file. No
.tex edits, no git writes, no changes to frozen or existing data files. Log this
prompt in notes/ai-prompt-log.md. After each step, append what finished to
notes/overnight_status.md so a crash only loses the unfinished step.

Step 0 - Environment check. Rebuild shard 1 of the 0.94-floor dataset (seed 100,
4 shards) and confirm it is byte-identical to the matching rows of
data/dataset.parquet. If not, stop and report the versions and the difference.

Step 1 - Pre-register the decision rule before any gate result exists. Write this
to scratch/n5_decision_rule.md, hash it to .sha256, and record the UTC time:
  SAFER: at the held-out operating point, missed violations <= 1% in at least
  4 of 5 splits.
  FASTER: speedup with flagged cases also solved (rule B) on the 0.95-floor data
  exceeds the 0.94-floor value by more than the seed std, AND the gate beats the
  static ranking at matched budget under rule B.

Step 2 - Relabel data/sts_n3_floor095.parquet and data/dataset.parquet (0.94
floor) with the back-switching solver in scratch/label_crosscheck.py, using
4 parallel workers. Only re-solve rows where a generator hit its reactive
limit in the original solve; copy the rest unchanged. Verify the shortcut by
re-solving 200 random copied rows and confirming identical labels. Save progress
after every shard.

Step 3 - On both relabeled datasets, run the same 5 splits, ridge and histgb,
targets 0.90-0.98, including the held-out operating point. Report escalation,
missed rate, and speedup under counting rules A and B, plus the static ranking
at matched budget, all as mean +/- seed std. Then apply the Step 1 rule and
state which outcome it gives.

Step 4 - Only if steps 0-3 finished: build a second 0.95-floor dataset with a new
seed for error bars on boundary mass and violation rate.

Report only. Make no decisions and no paper edits.
