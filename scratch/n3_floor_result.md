# N3 generator-voltage-floor rebuild — result, scored against the hashed prediction

## Prediction integrity

- **Prediction file:** `scratch/n3_floor_prediction.md`.
- **sha256:** `9975a07ec1c1a3004b524636239194a1584a8eadc5b6e3748766c4714446ba0f`, recorded 2026-09-28T03:15:32Z in
  `scratch/n3_floor_prediction.sha256` and `notes/ai-prompt-log.md` (entry 2026-09-27 (d)).
- **Builds started:** 2026-09-28T03:17:22Z. The first launch at ~03:16Z was stopped after ~10 s with no output
  written, and relaunched detached.
- **Re-hashed after the builds:** identical, `9975a07e…ba0f`. The file mtime is still 2026-09-27 23:15:32 local.
- **Not git-committed:** CLAUDE.md §8 says Claude runs no git writes. The hash is evidenced by the two records
  above and the session transcript, not by a commit.

## Runs

- **Driver:** `scratch/n3_floor_rebuild.py`, which uses the `feasibility/generate_dataset.py` worker.
- **Invocation:** the committed one (1,500 scenarios; 4 RNG shards, seeds 100-103; 375 accepted each; mixed
  modes; stress "fixed"; N-0 gate at 0.94).
- **Only change:** `GEN_VM_LO`.
- **Outputs:** `data/sts_n3_floor094.{parquet,json,manifest.json}` and `data/sts_n3_floor095.{parquet,json,manifest.json}`.
- **Wall time:** 24,846 s and 24,844 s. The power log shows the machine slept on battery during the run, so the
  wall time is not compute time.

## Results vs prediction (converged N-1 rows)

| # | Quantity | Predicted A (0.94) | Observed A | Predicted B (0.95) point [range] | Observed B | In range? |
|---|---|---|---|---|---|---|
| Q1 | BM, share in [0.94, 0.945) | 56.86% | 56.8629% | 33% [20-45] | **32.9543%** (91,933 / 278,971) | yes |
| Q2 | CBM, BM / share ≥ 0.94 | 68.90% | 68.9044% | 40% [28-55] | **39.2343%** (91,933 / 234,318) | yes |
| Q3 | VR, share < 0.94 | 17.48% | 17.4756% | 15.5% [12-18] | **16.0063%** (44,653 / 278,971) | yes |
| Q4 | N0S, bases with N-0 min in strip | 67.7% | 67.733% | 35% [20-50] | **36.867%** | yes |
| Q5 | PASS, N-0 gate pass rate | ≈ 54% | 53.8213% (1,500 / 2,787) | 70% [55-85] | **72.4288%** (1,500 / 2,071) | yes |
| Q6 | Build A reproduces `data/dataset.parquet` | bit-identical | **yes**: file sha256 identical (`8f0fd108…`); `DataFrame.equals` True; max \|Δ min_vm\| 0.0 | — | — | yes |

Other observed values:
- **Build B:** non-converged rows 29 (Build A: 45); median N-0 min 0.94647 (A: 0.94336); min_vm range
  0.71545-0.95859 (A: 0.71794-0.96031).

## The pre-stated reading rule, applied as written

The prediction file stated in advance:
- "BM in 20-45% and CBM < 60%: consistent with the generator voltage floor being a major driver of the
  concentration."

Observed: BM 32.95% and CBM 39.23%, so that condition is met. The two falsifiers were not hit:
- BM ≥ 45%;
- CBM ≥ 60%.

## Facts that bound this result (no decisions taken)

- **One dataset build per floor.** This is one draw of 1,500 scenarios per floor, not five independent builds.
  The builds use common random numbers (the same seeds), but their RNG streams diverge once redraw counts
  differ. There are no error bars from repeated builds.
- **The prediction was not blind.** It was informed by the round-1 40-base, one-seed probe (disclosed in the
  prediction file).
- **Labels are pandapower's pinned-solver labels** (one-way PV→PQ switching) in both builds; see N2.
- **No retraining, gate evaluation, escalation or missed-rate numbers were produced** for Build B.
- **The strip does not disappear.** Under the 0.95 floor it stays at 32.95%, versus 7.09% for case30-thermal.
- **Build A's exact reproduction settles the dataset seed:** it is `--seed 100 --nproc 4` (shards 100-103).
  The committed invocation string omits it (verifier B had recorded the seed as NOT FOUND).
