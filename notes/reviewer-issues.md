# Diagnosis of the four reviewer issues

> **SUPERSEDED (updated 2026-07-21) - escalation/speedup numbers below.** The escalation, speedup,
> and missed-violation figures in Issue 1 (82.9% / 1.21x / 0.63%; 62.2% / 1.61x / 1.82%; and the
> "62-83% esc, 1.1-1.6x" summary at lines 33, 101, 175) are **two-sided-band SCRATCH** values.
> They were first replaced by the clip-era one-sided pipeline (ridge 51.3% / 1.96x / 3.84%; histgb
> 39.7% / 2.53x / 3.01%), which is ITSELF now superseded by the resampled v2 build (the clip put a
> spurious point mass of min_vm at exactly 0.94; see notes/artifact-clip-0.94.md). **Canonical now:
> the v2 committed pipeline (`data/screener_metrics.json`, 5 seeds, pinned solver) at 90% coverage -
> ridge 48.2% esc / 89.0% cov / 3.23% missed / 2.08x; histgb 33.0% / 89.9% / 6.91% / 3.04x.** Quote
> THOSE. Rows are retained unedited below for the record. The old "~61% perfect-model floor" is
> two-sided; the one-sided floor is ~40-55% (CLAUDE.md 3, 5.5).

Investigation only, no fixes applied. Every number below comes from a run I did this session
(scripts in the session scratchpad). Ordered by importance.

## Issue 1: the escalation-rate collapse - the reviewer is right about the collapse, partly wrong about the cause

### What I ran

Screening population: the 278,960 converged N-1 cases in `data/dataset.parquet`. Features: the
566 pre-contingency scenario columns (per-bus P/Q, gen setpoints, Q-limits, in-service, N-0
voltages; dropped the constant `genp_*`) plus a 186-way one-hot of which branch is out. Target:
`min_vm` (float64). Split by `scenario_id`, never by row. Split-conformal band at 90%, then the
three-way gate: certify safe if the band is entirely above 0.94, flag violation if entirely
below, escalate if it crosses 0.94. Escalation rate is the fraction that crosses.

### In-distribution result (train/calib/test all from the boundary-enriched set)

| Model | test resid std | 90th-pct \|resid\| | conformal q | escalation | net speedup | missed violations |
|---|---:|---:|---:|---:|---:|---:|
| Ridge (alpha=10) | 0.0059 | 0.0075 | 0.0071 | **82.9%** | **1.21x** | 0.63% |
| HistGradientBoosting | 0.0037 | 0.0044 | 0.0038 | **62.2%** | **1.61x** | 1.82% |

Empirical band coverage was 89.0% (ridge) and 87.9% (HistGB) against the 90% target, so the
conformal machinery itself is working. The reviewer's threshold intuition is confirmed
numerically: the conformal half-width q (0.0038 to 0.0071 pu) is at or above the 0.005 boundary
tolerance, and the boundary is dense:

- within +/-0.003 of 0.94: 59.4% of cases
- within +/-0.005 of 0.94: 71.7%
- within +/-0.010 of 0.94: 87.9%

**So the reviewer is right: escalation is 62 to 83% and net speedup is 1.2 to 1.6x. The "fast
model handles the clear cases" story is badly weakened, because on this dataset there are almost
no clear cases.** A useful way to see why: even a *perfect* model (zero residual) escalates
`P(|true min_vm - 0.94| < q)`, which is 78.3% at q=0.0071 and 61.1% at q=0.0038. Escalation is
floored by the boundary mass, not by model error alone.

> **RECORD (moved from CLAUDE.md 5.5 on 2026-07-21, so it is not silently dropped when 5.5 was
> reconciled to the v2 build).** The "~61% perfect-model floor" that circulated in earlier
> sessions is UNTRACEABLE to any committed config. Under the two-sided form `P(|min_vm-0.94| < q)`
> the committed band widths give 81% at q=0.0071 and 70.8% at q=0.0048, never 61%; the 61.1% above
> appears only at q=0.0038, a tighter width that was never committed. (The project's gate is
> ONE-SIDED anyway, so it does not incur the two-sided floor: sub-0.94 cases are FLAGGED, not
> escalated. One-sided floor is ~40-55%; on the committed v2 build ridge/histgb escalate 48.2%/
> 33.0% at 90% coverage - see CLAUDE.md 5.5.)

### Where the reviewer's causal story is wrong

The reviewer blames `mult_hi=1.12` ("tuned to maximize straddle"). I tested that by generating a
**nominal-distribution** set: per-bus load U(0.95, 1.05), tiny reactive tilt and setpoint jitter,
gen-outage prob 0.10, same `enforce_q_lims=True` oracle, same N-0 feasibility gate. This is not
tuned for straddle at all. Result (200 scenarios, 37,199 N-1 rows):

- N-1 violation rate 16.7% (vs 28.6% in the tuned set), but
- **70.4% of N-1 cases still sit within +/-0.005 pu of 0.94.**

The boundary pile-up is nearly identical (70.4% vs 71.7%) on a distribution that was never tuned
for it. **The concentration is structural to case118, not an artifact of the `mult_hi` choice.**
The mechanism: the N-0 feasibility gate (correctly) forces every base case to sit at or just
above 0.94, because case118 is barely N-1 secure; a single contingency then drops the weakest bus
just below 0.94, so `min_vm` clusters at the threshold by construction. Re-tuning `mult_hi` will
not move this.

### Escalation measured on the nominal (deployment-like) distribution

| Model | escalation | net speedup | missed violations |
|---|---:|---:|---:|
| Ridge | 89.3% | 1.12x | 0 |
| HistGradientBoosting | 65.6% | 1.53x | 10 (~0.3% of ~3,100 true violations) |

Escalation stays high even on the honest deployment distribution. The fix does not rescue the
speedup on case118. Note the safety side is fine throughout: missed violations are 0 to 2%.

### Is the proposed fix (nominal test set) methodologically sound?

**Partly, and with a correction.**

1. **Sound:** escalation rate, net speedup, and missed-violation rate are properties of the
   *deployment* distribution, not the training distribution. Measuring them on the
   straddle-enriched set was never meaningful for the headline. They must be measured on a
   realistic operating distribution. So generating a separate nominal set to measure them is
   correct.

2. **The correction - you must also calibrate on the deployment distribution, not just test on
   it.** Split-conformal coverage holds only when calibration and test data are exchangeable.
   Calibrating on the boundary-enriched set and testing on nominal breaks exchangeability, and
   the 90% guarantee is then void in general. I checked this empirically:

   | | coverage | escalation |
   |---|---:|---:|
   | (a) calib=boundary, test=nominal (naive) | 90.3% / 92.9% | 89% / 70% |
   | (b) calib=nominal, test=nominal (correct) | 90.5% / 92.2% | 89% / 66% |

   (Ridge / HistGB.) Here (a) did not visibly break, but only by luck: the residual scale is
   almost the same on both distributions (q=0.0074 vs 0.0075 ridge; 0.0042 vs 0.0038 HistGB)
   because both distributions are boundary-heavy. You cannot rely on that. Under a genuinely
   different deployment distribution the coverage would drift.

3. **Correct construction:** train on whatever helps the model learn the boundary (the
   boundary-enriched set is fine, even useful, for training only); then draw a **calibration set
   and a test set from the same deployment distribution** you will run on, and compute q on that
   calibration set. If for some reason you must calibrate on a different distribution than you
   deploy on, the right tool is *weighted* conformal prediction (Tibshirani et al. 2019) with the
   deployment/training density ratio, but estimating that ratio is fragile and the clean answer
   is to calibrate on deployment.

### Bottom line on Issue 1

- Escalation collapse: **confirmed** (62 to 89% escalation, 1.1 to 1.6x speedup).
- Cause: **structural to case118**, not the `mult_hi` tuning. The nominal distribution is equally
  boundary-concentrated.
- The nominal-test-set fix makes the metric *honest* but does not make the speedup *good* on this
  network. It also must include calibration on the deployment distribution to keep the coverage
  guarantee.
- Two levers that actually move escalation: (a) a stronger regressor. Ridge escalates 89%,
  HistGB 66%, because a tighter model shrinks q. Both tree models are in the RISE syllabus, so
  this is available. (b) the network itself: case118 is pathologically weak, so almost every
  feasible-base contingency straddles 0.94. A network with more N-1 voltage margin would have
  real clear-cases to certify. This is worth raising before committing the headline metric to
  case118.

## Issue 2: numba - confirmed, and it moves the headline metric

`generate_dataset.py` `solve()` calls `pp.runpp(..., numba=True)`. `gonogo.py` uses
`numba=False`. Timed on the same 145 N-1 cases, `enforce_q_lims=True`, steady state (JIT warmup
dropped):

| numba | mean ms/solve | median | p95 |
|---|---:|---:|---:|
| True | 9.58 | 9.45 | 10.61 |
| False | 15.03 | 14.59 | 16.37 |

numba on is **1.57x faster** per solve. Since the headline speedup is model time vs solver
wall-clock, the solver baseline (the denominator) changes by 1.57x depending purely on this flag.
A speedup quoted against a numba-off solver would be inflated ~1.57x versus numba-on. This has to
be pinned. What to record alongside any speedup number: numba on/off, `enforce_q_lims`, init mode,
pandapower/numpy/numba versions, and the machine, because per-solve times are hardware dependent
(the old gonogo p95 of 19 ms and my 10 ms differ only by machine/run). Also note numba has a
one-time compile cost of seconds on the first solve in a fresh process; that must be excluded from
per-case timing (measure steady state) or amortized honestly.

## Issue 3: reproducibility - confirmed

The committed `data/dataset.parquet` was **not** made with bare defaults. Proven from the parquet
itself:

- Worker-seed prefixes in `scenario_id` are 100 to 104, implying `--seed 100 --nproc 5`.
- `agg_loading` ranges [1.004, 1.104], mean 1.059 - a fixed U(1.0, 1.12) window. The default
  `--stress perscenario` with ceiling 1.5 would spread `agg_loading` up to ~1.5.

So `python generate_dataset.py --n 1500` (defaults) reproduces a different dataset. The exact
command is recorded in `broadened-diversity.md`, which is good, but the code default does not
match the artifact.

Proposed fix (for later): both of these, not one.
1. Make the tuned setting the default (or add a named preset), so bare invocation reproduces the
   artifact.
2. Emit a **manifest** next to the parquet: seed, all sampling flags, `enforce_q_lims`, numba
   state, `nproc`, pandapower/numpy/pandas/numba versions, git commit, row/column count, and a
   content hash. This is the durable fix; defaults drift, manifests do not.

Git and stray files:
- `data/`, `notes/`, `feasibility/` are entirely untracked (`git ls-files` returns nothing for
  them). The whole project output lives outside version control. `.gitignore` currently only
  ignores `/secrets` and itself.
- `secrets/CLAUDE.md` is git-ignored on purpose (that is why the project-context doc sits in
  `secrets/`).
- `test.json` at repo root is an orphan `straddle.py` smoke-test output: 5 scenarios, 930 cases,
  `mult_hi=1.3`, and it carries the old over-voltage `near_hi` band, so it predates the current
  pipeline and the oracle fix. It is not referenced by any script. Safe to delete or ignore; it
  is not part of the dataset.

## Issue 4: stale number - confirmed

`broadened-diversity.md` line 39 says "632 columns"; line 278 correctly says 634. The parquet has
**634 columns** (I loaded it and checked). The 632 predates the two columns added in the revision
(`n0_min_vm`, `deep_collapse`). One-line stale value.

## Issue 5: HistGB early-stops on a ROW-random inner split (found 2026-07-26) - DISCLOSURE, not a bug

`HistGradientBoostingRegressor` resolves `early_stopping='auto'` to **True** whenever
`n_samples > 10_000`. Our train split is 167,375 rows, so early stopping is **active in every
committed histgb fit** and neither the code nor the paper says so. Verified on seed 0 with the
committed config (`lr 0.08, max_iter 300, max_depth 8`): `do_early_stopping_=True`,
**`n_iter_ = 214` of `max_iter=300`**, `validation_fraction=0.1`, `n_iter_no_change=10`.

Two consequences.

1. **`max_iter=300` was never reached.** It is an upper bound the fit stopped short of, so the
   value carries less meaning than it appears to.
2. **The internal 10% validation split is row-random, not grouped by `scenario_id`.** Rows from the
   same base scenario land on both sides of it, so the early-stopping signal is measured partly on
   rows whose scenario the model has already seen, and is optimistic.

**This does not break the conformal guarantee.** The internal split is carved out of the training
data only; the calibration and test splits are never touched, so q-hat is still computed on data
that had no influence on the fit. Exchangeability between calibration and test is unaffected.

**It is a disclosure item for the paper.** The draft states that "all the failures in one base
scenario do not mix across datasets" (`notes/1_research_draft.txt` line 60). That is true of the
train/calibration/test partition, which is what the sentence is about, but it is **not** true of the
row-random split that scikit-learn creates *inside* train. The honest form of the sentence
distinguishes the two. Record it; do not "fix" it by disabling early stopping, which would change
the committed model.

Related: the committed hyperparameters are not scikit-learn defaults either (the paper claims they
are, twice). See the provenance trace filed with the hyperparameter-tuning work item.

## Summary

| Issue | Verdict |
|---|---|
| 1 escalation collapse | Confirmed: escalation 62-89%, speedup 1.1-1.6x. But the cause is structural to case118, not the `mult_hi` tuning (nominal distribution is equally boundary-heavy). The nominal-test fix is right for honest measurement but must calibrate on the deployment distribution, and does not rescue the speedup. Stronger model and/or a less marginal network are the real levers. |
| 2 numba | Confirmed: 1.57x per-solve swing; must be pinned and recorded, headline metric depends on it. |
| 3 reproducibility | Confirmed: defaults do not reproduce the artifact (proven from the parquet: seed 100, nproc 5, fixed 1.12 window). Fix defaults and emit a manifest. Outputs are untracked; `test.json` is an old orphan. |
| 4 stale number | Confirmed: 632 should be 634. |
