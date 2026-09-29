# State of project

> **UNSOURCED FIGURES — DO NOT USE (2026-07-31).** The figures "case57 acceptance rate 87%,
> boundary mass 30.65%, base range [0.94000, 0.99464]" are **unsourced**. A full provenance search
> (repo files, git history across all refs, and every session transcript) found them in only two
> places: (a) the text of two prompts in `notes/ai-prompt-log.md`, and (b) artifacts derived from
> those prompts — `feasibility/quintile_boundary_mass.py` (hardcoded `CASE57_BOUNDARY_PCT = 30.65`,
> lifted from a prompt CONTEXT block, not computed) and its output `data/quintile_boundary_mass.json`.
> **No tool run anywhere in project history ever computed them from data.** The only COMPUTED case57
> result is `data/case57_feasibility.json` (`feasibility/case57_gonogo.py`), which says the opposite:
> under the pinned config, case57's N-0 accept rate is **0.0% (0/3000)**, boundary mass is **null**,
> nominal base is **0.7199 pu (39/57 buses below 0.94)**, and the max achievable `n0_min_vm` over
> converged draws is **0.7747** — the network never clears the 0.94 floor. These unsourced figures
> **must not enter the paper, poster, or any frozen artifact**; the `quintile_boundary_mass` "case57
> sits inside the case118 envelope" comparison rests on the 30.65% number and is therefore
> **not established**. If a case57 result is ever needed, it must be produced by committed repo code
> and the config regime disclosed (case57 is only feasible under a changed regime, not the pinned one).

> **Stale, 2026-07-21.** This whole document predates the screener and carries clip-era dataset
> figures (72 buses, 28.6% violations, min_vm [0.732, 0.963]). The screener, conformal gate,
> baselines, tradeoff curve, and figures now exist, and the dataset is the resampled v2 build; for
> current state see CLAUDE.md section 0 and data/frozen_poster_numbers.json.

> **REVISION 2026-07 — oracle correction + dataset built.** Two things changed since the
> assessment below was written:
>
> 1. **The oracle was wrong.** All feasibility work used `runpp` *without* `enforce_q_lims`,
>    under which generator Q-limits have no effect on the solution (verified empirically). This
>    made the "bus 76 loses reactive support at its Q-limit" narrative impossible and made the
>    two-bus concentration partly an artifact. The project now uses `enforce_q_lims=True`
>    everywhere. Corrected feasibility numbers: the practical loading ceiling is **~140%**, not
>    160% (non-convergence hits 100% at 160% under the correct oracle); see the banner in
>    `gonogo.md`.
>
>    *Addendum (2026-07-29) — the bug would have erased the heavy tail, not just shifted numbers.*
>    Re-solving the deepest missed violation (scenario 101000025, line 78 out) with
>    `enforce_q_lims=False` reads min_vm=**0.93901** — depth 0.00099 pu below the 0.94 floor,
>    *shallower than the median miss* — at IEEE bus 20, versus **0.84854** (depth 0.091 pu) at IEEE
>    bus 54 under the correct `enforce_q_lims=True` oracle. The Q-limit-induced voltage collapse, and
>    the entire heavy tail of deep misses, exist only with enforcement on; the wrong oracle would have
>    removed the tail, not merely relocated the critical bus. See `data/qlims_off_check.json` and
>    `data/miss_mechanism.json`.
> 2. **The diversified dataset is built** (was "next step #1"). `feasibility/generate_dataset.py`
>    produces `data/dataset.parquet` (280,500 rows, 1,500 N-0-feasible scenarios × 187
>    contingencies). With broadened sampling + an N-0 feasibility gate, critical under-voltage
>    now spreads across **72 buses (top-2 43.8%)**, min_vm spans [0.732, 0.963], and the split is
>    28.6% violation / 69.2% straddle. A **2×2 controlled experiment** (sampling × oracle) proves
>    the diversification is a sampling effect (+30/+35 buses), not an oracle artifact (+7/+12 buses).
>    Full writeup: `feasibility/broadened-diversity.md`. Eight degeneracy-guard tests
>    (`feasibility/test_dataset.py`) all pass.
>
> The findings marked "Confirmed" below (esp. #1 ceiling and #4 concentration numbers) are
> **superseded** where they cite old-oracle values; they are retained for the record. Next
> build steps #1 (dataset) is DONE; steps #2–#6 stand.

---

Assessment written after reading the four feasibility files on disk and re-running what was cheap to re-run. Purpose: separate what is verified from what is still assumed, state the honest claim ceiling, and list the next build steps.

## What is on disk

- `feasibility/gonogo.md` — loading-sweep GO/NO-GO writeup (uniform load scaling, 100 to 180%).
- `feasibility/straddle-diversity.md` — straddle-case diversity study (per-bus non-uniform scaling, 100 to 130%).
- `feasibility/straddle.py` — the sweep script behind the diversity study.
- `feasibility/analysis.py` — the metrics script behind the diversity study.
- `README.md` — was a one-line stub, now rewritten.
- `.venv/` — a Python 3.12 virtual environment that is empty (no numpy, no pandapower).

There is no model code, no conformal code, and no dataset export yet. The repository is at the end of feasibility, not the start of modeling.

## Verified

Each of the five findings from the project brief was checked against the files. Where re-running was cheap I re-ran it with pandapower 3.5.4.

1. GO verdict and convergence. Confirmed. Re-derived the gonogo base facts directly: case118 has 118 buses, 173 lines, 13 transformers, 4242.0 MW base load, and line thermal ratings up to 41.4 kA. The 100% uniform full N-1 sweep reproduces min V 0.902, 12 voltage violations out of 187 cases, and 0 non-convergence. The solve times, and the 1.1% / 2.7% / 17.6% non-convergence at 140 / 160 / 180% in gonogo.md, were not re-run (see the caveat below) but the base numbers that anchor them all match.

2. Voltage binds, not thermal. Confirmed. Line ratings of 41.4 kA are far above realistic loading, so branch current never nears its limit and the 0.94 pu voltage floor binds first. This project screens under-voltage violations.

3. Single-sided problem. Confirmed. In the straddle run, max_vm is pinned at exactly 1.0500 in every near-limit case and never comes within 0.005 pu of the 1.06 ceiling. That 1.05 value is the fixed voltage setpoint of the three highest-set generators (buses 10, 25, 66), not an approach to an over-voltage violation. The upper band carries no signal and should be dropped.

4. Straddle data is abundant but concentrated. Confirmed and reproduced exactly. 200 scenarios give 37,200 cases: 8,460 violations (22.7%) and 28,740 near-limit straddle cases, about 14x the 2000 target. Feasible min_vm sits in [0.940, 0.943], a 3 milli-pu window. Critical under-voltage lands at only 11 buses, dominated by bus 53 (72.7%) and bus 76 (25.8%), which is the ~99% concentration the brief describes. Root cause holds up: bus 53 is a pure load bus with no local generator, and bus 76 is a generator held at the fleet's lowest setpoint (0.943) that loses voltage support once it hits its reactive limit.

5. Recommended sampling fix is not yet done. Confirmed. No script on disk widens the multipliers past 1.30, varies reactive load independently, perturbs generator setpoints or Q-limits, or stratifies splits by bus. This is future work.

## Discrepancies and caveats to carry forward

- The generating script for `gonogo.md` is not in the repository. Only `straddle.py` and `analysis.py` are present, and both reproduce their numbers exactly. The gonogo table can be cross-checked by hand (the base facts and the 100% N-1 result match) but it cannot be re-run from disk. If the sweep code still exists elsewhere, add it as `feasibility/gonogo.py` so the whole feasibility set is reproducible.

- The two feasibility documents use different straddle definitions. gonogo.md still includes an over-voltage band [1.05, 1.06] and a thermal band [95, 100]% in its straddle count. straddle-diversity.md concludes both are inert here and keeps only the under-voltage band. This is a refinement over time, not a contradiction, but the two counts are not directly comparable for that reason.

- Environment mismatch. The working pandapower install (3.5.4, numpy 2.3.5, pandas 2.3.3) is under an Anaconda Python 3.13, not the checked-in `.venv` (Python 3.12), which has no packages installed. The scripts run with the Anaconda interpreter, not with the repo venv as it stands. A `requirements.txt` has been added; the venv still needs to be populated from it.

- gonogo.md's own verdict says constrain scenario generation to no more than 160%. The straddle study used 100 to 130%, which sits well inside that ceiling.

## Honest claim ceiling

What the evidence supports today: pandapower N-1 screening on IEEE 118-bus is a fast and reliable oracle across the intended loading range, and it produces a large supply of cases that straddle the 0.94 pu under-voltage limit. That is enough to build and calibrate the gate against this one constraint on this one network.

What the evidence does not yet support: any claim of network-general screening. The straddle set is concentrated at two buses and inside a 3 milli-pu voltage window, so a surrogate trained on it now would demonstrate the gate mechanism but could report generalization that is really memorization of buses 53 and 76. The defensible framing until the sampling is diversified is "calibrated under-voltage screening on case118 under per-bus N-1 load scaling," not "a general contingency screener." The N-1 to N-2 shift test only becomes meaningful once the training distribution is broad enough that holding coverage past it says something.

## Next build steps

1. Diversified scenario generator. Extend per-bus multipliers past 1.30, vary reactive load and power factor independently of real power, perturb generator voltage setpoints and Q-limits, and stratify sampling so buses beyond 53 and 76 appear. Export a labeled dataset: features per (scenario, contingency) plus min_vm and the violation label.

2. Feature and target design. Decide the surrogate target: regress min_vm and then threshold at 0.94, or classify the violation directly. Regressing min_vm is the better fit for a conformal band, since the band lives in voltage units where the limit is defined.

3. Train the fast surrogate on N-1 data.

4. Split-conformal wrapper. Hold out a calibration set, form residual quantiles at the 90% target, and turn each prediction into a band that drives the three-way gate: certify safe, flag violation, or escalate when the band crosses 0.94.

5. Escalation harness. Route only band-crossing cases to pandapower and measure the four headline metrics: net speedup including escalated solver time, escalation rate, missed violations, and empirical coverage against the 90% target.

6. N-1 to N-2 shift test. Calibrate on single-line outages, evaluate on unseen double-line outages, and report whether coverage holds past the training regime. Both outcomes are results.
