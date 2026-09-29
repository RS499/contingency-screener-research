Read CLAUDE.md, notes/overnight_status.md, scratch/n3_floor_result.md,
data/sts_label_crosscheck.json and data/sts_matched_budget.json. Use
.venv/bin/python for everything. Write only new files under scratch/ and
data/sts_* with a manifest beside each data file. No .tex edits, no git writes,
no changes to existing data files. Log this prompt in notes/ai-prompt-log.md.
Append progress to notes/overnight_status.md after each step. If anything is
ambiguous, ask me instead of stopping.

Step 0 - Environment check. Rebuild the first shard (seed 100 of 100-103) of the
0.94-floor dataset and confirm it is byte-identical to the matching rows of
data/dataset.parquet. If not, stop and report versions and the difference.

Step 1 - Pre-register before any N5 gate result exists. Write
scratch/n5_decision_rule.md, hash it to .sha256, record the UTC time:
  PRIMARY MODEL: histgb (ridge reported, not used for the verdict).
  OPERATING POINT: held-out; each split picks its target on its inner tuning
  split, same procedure as data/tuning_search.json.
  STD: the larger of the 0.94 and 0.95 seed stds (CLAUDE.md std rule).
  SAFER: histgb missed violations <= 1% in at least 4 of 5 splits.
  FASTER: histgb speedup B = n*t_solve / (n*t_surr + (n_esc + n_flag)*t_solve)
  on 0.95 data exceeds the 0.94 value by more than STD, AND histgb catch rate
  beats the static ranking at matched budget (rule B) by more than STD.

Step 2 - Labels. For the 0.94 data, use the existing switch-back labels in
data/sts_n2_label_audit.parquet. For data/sts_n3_floor095.parquet, relabel every
row with the same method as scripts/sts_n2_label_audit.py, using 4 parallel
workers; write a batch driver if needed. Save progress after every shard.

Step 3 - On both relabeled datasets, run the same 5 splits, ridge and histgb,
targets 0.90-0.98 plus the held-out point. Report escalation, missed rate,
speedup under rules A and B, and the static ranking at matched budget, as mean
+/- seed std. Apply the Step 1 rule and state the outcome.

Step 4 - Only if steps 0-3 finished: build a second 0.95-floor dataset with a
new seed for error bars on boundary mass and violation rate.

Report only. Make no decisions and no paper edits.
