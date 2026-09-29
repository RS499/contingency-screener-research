# Independent review of the broadened-sampling work

> **Historical, 2026-07-21.** This review is of the pre-N-0-gate build (different column count,
> higher violation rate, different bus distribution), and it is the review that motivated adding the
> N-0 feasibility gate. It is kept as the record of that decision; for the current build see
> CLAUDE.md and data/frozen_poster_numbers.json.

Adversarial review of the dataset generation and diversity claims produced by the other agent
(generate_dataset.py, analyze_broadened.py, ablation.py, broadened-diversity.md, dataset.parquet).
Every number below was recomputed directly from `data/dataset.parquet` or from a fresh
power-flow run I wrote, not read back from the agent's own JSON. Recompute scripts live in the
session scratchpad; the controlled experiment is described in full so you can re-run it.

## Verdict (3 sentences)

The dataset is real, the schema is clean with no post-contingency leakage, and every headline
count in broadened-diversity.md reproduces exactly, so the reporting is honest and the agent
flagged its own oracle change rather than hiding it. The central claim (broadening spread the
critical bus from a 2-bus pile-up to 81 buses) holds and is driven mostly by the sampling, not
by the oracle switch, so the headline is only mildly confounded. But the dataset is not usable
as a screener training set as-is: 95% of the pre-contingency base cases are themselves already
in violation, so the scenarios sit past the edge of a valid operating point, and the resulting
96% violation rate leaves the three-way gate almost nothing to screen.

## What checks out (independently recomputed)

Loaded `data/dataset.parquet` fresh and recomputed. All of these match the report to the digit:

| Quantity | Report | My recompute | Match |
|---|---:|---:|:--:|
| Rows | 280,500 | 280,500 | yes |
| Scenarios | 1,500 | 1,500 | yes |
| Columns | 632 | 632 | yes |
| Rows per scenario | 187 | 187.0 | yes |
| Non-converged | 14,297 (5.10%) | 14,297 (5.097%) | yes |
| Converged | 266,203 | 266,203 | yes |
| Violations | 256,247 (96.26%) | 256,247 (96.26%) | yes |
| Straddle | 9,820 (3.69%) | 9,820 (3.689%) | yes |
| Comfortably safe (min_vm > 0.95) | 136 | 136 | yes |
| min_vm range | 0.445 to 0.951 | 0.4448 to 0.9511 | yes |
| Distinct critical (argmin) buses | 81 | 81 | yes |
| Top-1 (bus 76) | 41.1% | 41.13% | yes |
| Top-2 (buses 76, 53) | 58.6% | 58.63% | yes |
| Top-5 | 76.5% | 76.53% | yes |

**Schema and leakage (item 1): clean.** The 632 columns break down as 619 feature columns plus
13 id/target columns:

- 118 `pload_i` + 118 `qload_i` (per-bus real and reactive load) = 236
- 53 gens x 5 (`genvm`, `genp`, `genqmin`, `genqmax`, `genon`) = 265
- 118 `vm0_i` (N-0 solved bus voltages) = 118
- 13 other: `scenario_id`, `sampling_mode`, `outaged_type`, `outaged_idx`, `gen_out`,
  `agg_loading`, `n0_converged`, `converged`, `min_vm`, `max_vm`, `argmin_bus`, `violation`,
  `straddle`

Every feature is knowable before the post-contingency solve: loads and generator settings are
scenario inputs, `vm0` is the pre-contingency (N-0) solved state, and the outaged branch is the
contingency definition. The targets (`min_vm`, `max_vm`, `argmin_bus`, `violation`, `straddle`)
are the only post-contingency quantities and they are not fed back as features. I confirmed
`vm0` is genuinely the N-0 state and constant within a scenario: across sampled scenarios the
maximum within-scenario standard deviation of any `vm0_i` is 2.5e-6, which is float32 noise, not
variation. No leakage found.

**The oracle-inertness claim (part of item 3): confirmed.** The report justifies switching to
`enforce_q_lims=True` by claiming that with enforcement off, generator Q-limits do nothing. I
re-ran the micro-test: sweeping the bus-76 generator's `max_q_mvar` over {5, 23, 100} Mvar with
`enforce_q_lims=False` gives an identical result every time (min_vm 0.943 at bus 76), while with
enforcement on the result starts to move. The physical reasoning behind the oracle change is
sound: with enforcement off, PV generators hold their setpoint with unlimited reactive power, so
the Q-limit sampling axis is a genuine no-op. Confirmed that both old scripts omit the flag:
`straddle.py` calls `pp.runpp(net, init="dc")` and `gonogo.py` calls
`pp.runpp(net, init="flat", numba=False)`, and pandapower defaults `enforce_q_lims=False`.

## What does NOT check out

**1. A float32 boundary defect mislabels ~2,310 violations if you re-derive the label from the
stored feature.** The `min_vm` column is stored as float32, but the `violation` / `straddle`
boolean labels were computed in float64 before the downcast. For 2,310 violation rows, the true
float64 min_vm sat just below 0.94 and float32 rounded it to exactly 0.94000000. The stored
boolean labels are correct. But the project's own chosen method (regress min_vm, then threshold
at 0.94) would re-derive the label from the stored float32 value and silently flip those 2,310
true violations to "safe." They are exactly the boundary cases the conformal band cares about
most. This is small (0.9% of violations) but it is at the worst possible place. Fix: store
min_vm as float64, or mandate that labels always come from the boolean columns, never from the
feature.

**2. 326 converged rows carry all-NaN N-0 features.** 65 scenarios had a non-converging N-0 base
case. Those scenarios still emit 187 rows each, and where a contingency happened to converge
(326 rows total, 0.12%) the row has a real min_vm target but all 118 `vm0_i` features are NaN.
These are malformed training rows that do not raise an error. Small, but a model will choke on
them unless they are dropped.

**3. Silent exception swallowing.** `solve()` catches bare `Exception` and reports it as
non-convergence. Any real bug (a bad index, a shape error) would be counted as a
non-converged case rather than surfacing. The 5.10% non-convergence figure could in principle
include silent errors. I did not find evidence that it does, but the code cannot tell the
difference.

**4. The "506 milli-pu spread" headline is a tail artifact.** min_vm reaches 0.445, but only 11
converged cases sit below 0.50, and the p5 is 0.798. The operationally meaningful spread is
roughly [0.80, 0.95]. Quoting a 506 milli-pu range anchored on 0.445 oversells it, because 0.445
pu is not an operating point, it is a near-collapsed solution the solver happened to converge.
The honest statement is that min_vm now has a continuous spread across roughly [0.80, 0.95] with
mass at the 0.94 boundary, which is the property that actually matters and is genuinely present.

**5. The ablation's fine ranking is not robust (item 5).** The headline ablation conclusion,
that generator setpoint perturbation is the workhorse for bus spread, is solid: disabling it
drops distinct buses 63 to 38 and pushes top-2 from 55.9% back up to 73.2%, far outside any
plausible noise. But the secondary claim that Q-limit scaling "contributes least" is weak:

- It is a statistical tie with generator outage. Disabling Q-limit gives (delta distinct -4,
  delta top-2 -0.2). Disabling gen outage gives (delta distinct -4, delta top-2 -0.5). The
  ranking of qlim below genout rests on 0.2 vs 0.5 percentage points on a single 60-scenario run
  with no repetition.
- The ranking metric adds a percentage-point number to a raw bus count (mixed units, arbitrary
  weighting). A different weighting could swap the bottom two.
- The design is not fully paired. Disabling the load axis switches the sampler from per-scenario
  to fixed stress, which changes the random-number draw sequence, so the load row is not drawn
  on the same random stream as the others.
- Disabling load *lowers* top-2 concentration (delta -2.6), which is the wrong sign for a
  "removing a spreading axis" story and points to interaction noise at this budget.

The report's nuance that Q-limit scaling adds voltage *depth* rather than spatial spread (it is
tied for the largest delta on min_vm width, -0.139) is the most defensible part and is worth
keeping. Net: trust "setpoint is the workhorse," treat "Q-limit contributes least" as
"Q-limit and gen-outage both contribute little to spread, order uncertain."

**6. Minor:** `ablation.json` is written to `data/ablation.json`, not `feasibility/ablation.json`
as the brief states (the report itself says `data/`). The new generator runs with `numba=True`,
while CLAUDE.md 8 records the feasibility numbers as "numba OFF," so solve-time comparisons
across the two are not apples to apples.

## The oracle-change problem, explained plainly

**What changed.** The old feasibility scripts solved the power flow with generator reactive power
*unlimited* (`enforce_q_lims=False`). That is physically wrong: real generators have a reactive
ceiling, and bus 76 losing voltage support at its reactive limit is the whole physical story the
notes tell. The new generator fixes this with `enforce_q_lims=True`. The fix is correct.

**Why it confounds the before/after.** The report's headline compares the OLD study (11 buses,
[0.940, 0.943] window, computed under the old unphysical oracle) against the NEW run (81 buses,
computed under the new oracle). Two things changed at once: the sampling got broader AND the
oracle got stricter. A clean comparison has to hold one fixed.

**I ran the controlled experiment (the one the brief asks for).** Old sampling is straddle.py's
per-bus U(1.0, 1.3) load with no generator perturbation. New sampling is the full broadened
generator. I ran all four combinations, same seed, full N-1, 30 scenarios each (about 22,000
solves total). Distinct critical buses:

|  | OLD oracle (no q-lims) | NEW oracle (enforce) |
|---|---:|---:|
| **OLD sampling** | 15 | 22 |
| **NEW sampling** | 46 | 53 |

Reading the decomposition from the 15-bus baseline to the 53-bus corner:

- Oracle switch alone (hold old sampling): 15 to 22, about +7 buses.
- Sampling switch alone (hold old oracle): 15 to 46, about +31 buses.
- Both together: 15 to 53, about +38 buses. The two effects are close to additive.

So the broadened **sampling does roughly 80% of the bus-spreading work; the oracle switch does
roughly 20%.** The "11 to 81" headline is real and is mostly earned by the sampling. The oracle
change nudges it, it does not manufacture it. (My absolute numbers are lower than 81 only because
this is 30 scenarios, not 1,500; more scenarios discover more rare critical buses. The
decomposition is the point, not the absolute counts.)

**Where the oracle change matters much more: the class balance.** The same 2x2 on violation rate
and voltage depth:

| Arm | Violation % | min_vm floor | Straddle count |
|---|---:|---:|---:|
| OLD sampling / OLD oracle | 20.2% | 0.875 | 4,476 |
| OLD sampling / NEW oracle | 35.4% | 0.813 | 3,625 |
| NEW sampling / OLD oracle | 82.3% | 0.808 | 993 |
| NEW sampling / NEW oracle | 96.7% | 0.676 | 180 |

The oracle switch alone lifts violations from 20% to 35% and deepens the voltage floor, because
generators can no longer prop up voltage with infinite reactive power. Combined with the
aggressive new sampling it drives 96.7% violations and collapses the straddle population from
~4,500 to 180. In short: the oracle change is a minor confound for the *bus-spread* headline but
a major driver of the *class-imbalance* problem. Both the stricter (correct) oracle and the
over-aggressive stress window pushed the dataset into violation saturation.

**Bottom line on confounding:** the headline diversity claim survives. The class-balance problem
is partly an artifact of stacking the corrected oracle on top of a load window that was tuned for
the old, weaker-constraint oracle.

## Is the dataset usable as-is? No.

I agree with your read on the class balance, and I will sharpen the reason. The problem is not
only that a classifier would learn "always violation." The deeper problem is that the
**pre-contingency base case is itself infeasible in 95% of scenarios.** Recomputed from the
parquet: of 1,500 N-0 base rows, 1,435 converged, and 1,360 of those (94.8%) are already in
under-voltage violation before any line is removed. Only 1 base case out of 1,435 is comfortably
safe.

A contingency screener answers "does removing this one branch push a *valid* operating point into
violation." If the operating point is already collapsed, there is nothing to screen: every case
is a violation regardless of the contingency, and min_vm reaching 0.445 and 0.676 pu describes a
grid past the point where an operator would have shed load long ago. So this is not a hard
screening dataset, it is a grid-already-collapsed dataset.

One place I partly push back on the "unusable" framing: for the project's actual chosen method, a
conformal band around a **min_vm regression**, raw class balance matters less than having a
continuous target with mass near 0.94. The dataset does have that: 10.3% of converged cases sit
within +/-0.005 pu of the boundary, and the distribution is smooth from ~0.88 up to 0.94. So the
dataset is not worthless for pure regression calibration. What kills it is (a) the unrealistic
operating regime (infeasible base case), and (b) the deep-collapse tail below ~0.80 that will
distort a regressor's residuals and therefore the conformal quantiles. Both are fixable by
regenerating with a saner stress range.

### Recommended regeneration settings

1. **Gate on N-0 feasibility.** Reject or resample any scenario whose N-0 base case is already in
   violation (min_vm < 0.94 at N-0). Screen contingencies only on valid operating points. This
   single change is the most important one.
2. **Lower the stress window under the new oracle.** The per-scenario ceiling U(1.05, 1.50) was
   effectively tuned against the old, weaker-constraint oracle. Under `enforce_q_lims=True` the
   grid is much weaker, so the same window saturates. My controlled run shows old-style U(1.0,
   1.3) load under the correct oracle gives ~35% violations and a healthy straddle population,
   which is a trainable balance. Re-tune the load range under the new oracle, targeting something
   like 20% to 50% violations rather than 96%.
3. **Keep `enforce_q_lims=True`.** It is physically correct. Do not revert it. Just stop pairing
   it with a load window designed for the old oracle.
4. **Clip or exclude non-physical collapse.** Drop or cap cases below roughly 0.80 pu, or at
   minimum flag them, so the regression target and conformal residuals are not dominated by
   solutions no operator would run.
5. **Store min_vm as float64** (or forbid re-deriving labels from the feature), to remove the
   2,310-row boundary mislabeling.
6. **Drop the 326 NaN-feature rows** (non-converged N-0), and split the bare `except Exception`
   in `solve()` so genuine errors are distinguishable from non-convergence.
7. Keep generator setpoint perturbation (the proven diversity driver). Q-limit scaling and
   generator outage can stay but are minor contributors to spread.

## Which existing docs and facts are now stale

The important structural facts (118 buses, 173 lines, 13 trafos, 4242 MW, voltage binds not
thermal, over-voltage inert) are unchanged. What is stale is everything computed under the old
`enforce_q_lims=False` oracle, plus the status lines that predate the generator:

- **secrets/CLAUDE.md 0 and 7** ("No model code yet. Next build step: the diversified scenario
  generator"): stale. The generator exists and has been run.
- **secrets/CLAUDE.md 5.1** (GO verdict: "<=1.1% non-convergence through 140%, ~9 ms/case"):
  computed under the old oracle. Under `enforce_q_lims=True` non-convergence rises (5.10% at
  <=160% aggregate in this run, 3.6% at 30 scenarios in my controlled run at U(1.0,1.5)). The
  convergence-and-speed GO verdict has NOT been re-established under the corrected oracle.
- **secrets/CLAUDE.md 5.4** ("37,200 cases: 8,460 violations (22.7%), 28,740 straddle,
  [0.940, 0.943] window, buses 53 at 72.7% / 76 at 25.8%"): all old-oracle numbers. Under the new
  oracle even old-style sampling gives ~35% violations, fewer straddle, and a floor near 0.81.
- **secrets/CLAUDE.md 6** ("3 milli-pu window," "memorization of buses 53 and 76"): superseded by
  the broadened result (81 buses, top-2 58.6%). The two-bus concentration is broken.
- **feasibility/straddle-diversity.md**: its entire before-picture (11 buses, 3 milli-pu window,
  ~99% at two buses) is old-oracle. Still valid as a record of that study, but must be annotated
  as `enforce_q_lims=False` so it is not read as the current pipeline's behavior.
- **feasibility/gonogo.md**: the non-convergence column (0 / 0 / 1.1 / 2.7 / 17.6% across 100 to
  180%) and the solve times are old-oracle. Convergence behavior changes under enforcement, so
  the 160% ceiling and the "GO" convergence story need re-validation under the new oracle before
  they justify the pipeline.
- **notes/state-of-project.md**: says the sweep script behind gonogo was missing (it now exists as
  gonogo.py), says diversified sampling is "not yet done" (now done), and repeats the old-oracle
  straddle numbers. Stale on all three.
- **README.md**: "converges with no more than 1.1% non-convergence through 140%... roughly 9 ms
  per case" and "28,740 cases sitting on the 0.94 pu boundary" are old-oracle; "Build a
  diversified scenario generator" as the first next step is now done.
- **notes/repro-fixes.md**: still valid as a record of reproducing gonogo.py, but note that what
  it reproduced was the old-oracle sweep.

The single sentence to carry into every one of these: the feasibility GO verdict (convergence,
speed, straddle abundance) was established under `enforce_q_lims=False`, and has not yet been
re-established under the physically correct `enforce_q_lims=True` oracle the project is now
committed to.
