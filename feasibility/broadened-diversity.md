# Broadened-Sampling Diversity — IEEE 118-Bus N-1 Under-Voltage Dataset

> **2026-07 REVISION.** This supersedes the first (pre-review) build. Two fatal defects in
> that build were fixed and the dataset regenerated; every number below is from the
> regenerated dataset. What changed and why is marked **[REVISED]**. See "What changed in
> the revision" at the end.

**Question.** The original per-bus-load-only sampling produced straddle cases concentrated
~99% at buses 52 and 75 inside a 3 milli-pu voltage window. Does broadening the sampling
— wider/regional load, independent reactive tilt, generator setpoint and Q-limit
perturbation, and generator outage — spread the critical bus across the network and widen
the min_vm range enough to train (not just calibrate) an under-voltage surrogate?

**Verdict — CONCENTRATION BROKEN.** After broadening (with an N-0 feasibility gate and the
physically correct Q-limit-enforcing oracle), critical under-voltage lands on **72 distinct
buses** (was 11), and the **top-2 share falls to 43.8%** (was ~98.5%) — well below the 80%
red line. N-1 min_vm spans **0.732–0.963 pu** versus the old 3 milli-pu window. The dataset
is now well-balanced for a conformal regressor: **28.6% of converged N-1 cases violate**
0.94, **69.2% straddle** the [0.94, 0.95] band, and only **23 cases** collapse below 0.80 pu.

**The 2×2 controlled experiment proves the diversification is a real SAMPLING effect, not an
artifact of the oracle change** (see §"2×2 controlled experiment").

**Class balance is now healthy [REVISED].** The previous (ungated) build was 96.3%
violations with only 136 safe cases — because ~95% of its scenarios had a base (N-0) case
that *already violated* 0.94, so there was nothing to screen. The N-0 feasibility gate is the
fix: only scenarios whose pre-contingency base is feasible are accepted, and the contingency
outcome then straddles the limit as a screening problem should.

---

## Method

| Element | Choice |
|---|---|
| Network | `pandapower.networks.case118` (pandapower 3.5.4, numpy 2.3.5); 118 buses, 173 lines, 13 trafos, 99 loads, 53 gens |
| Scenarios | **1,500** (750 independent-load + 750 regional-load, interleaved) |
| Contingencies | Full **N-1**: N-0 base + every in-service line and trafo out one at a time |
| Cases | 1,500 × 187 = **280,500 rows** (`data/dataset.parquet`, 632 columns) |
| Voltage floor | 0.94 pu (under-voltage only; over-voltage inert on this case and not a target) |
| Loading cap | aggregate P ≤ 160% (gonogo ceiling: non-convergence 17.6% at 180%) |
| Solve | AC `runpp`, **`enforce_q_lims=True`** (see deviation below), DC-initialized, numba on |

### Sampling axes (all varied per scenario)

1. **Load magnitude [REVISED window].** Per-bus multipliers on `U(1.0, 1.12)` (independent
   mode) or as regional blocks on `U(1.0, 1.12)` with ±10% within-region jitter (regional
   mode). Regions = 8 graph-community partitions of the electrical network (`case118` has no
   usable `zone`/geodata; `zone` is uniformly 1.0). The `1.12` ceiling was chosen by the tuning
   sweep (below).
2. **Reactive load / power factor**, independent of P: `q_i = q0_i · mp_i · pf_i`,
   `pf_i ~ U(0.90, 1.15)`.
3. **Generator setpoints and Q-limits**: `vm_pu` perturbed `U(−0.025, +0.025)` (clipped to
   [0.94, 1.06]); Q-limits scaled `U(0.6, 1.4)`.
4. **Generator outage**: one non-slack generator dropped with probability 0.30.

Reproducible via `feasibility/generate_dataset.py` (generator), `feasibility/tune_sweep.py`
(load-ceiling sweep), `feasibility/test_dataset.py` (degeneracy guards),
`feasibility/experiment_2x2.py` (controlled sampling×oracle experiment). Exact command:
```
python generate_dataset.py --n 1500 --mode mixed --stress fixed \
  --mult-hi 1.12 --reg-hi 1.12 --pf-lo 0.9 --pf-hi 1.15 --dvm 0.025 \
  --out data/dataset.parquet --nproc 5 --seed 100
```

### N-0 feasibility gate (the core fix) [REVISED]

A scenario is **accepted only if its base (N-0) case converges and is itself feasible**
(min_vm ≥ 0.94). Rejected scenarios are re-drawn. At the tuned window the gate passes
**31.9%** of draws (1,500 accepted, 3,207 rejected). Without this gate, ~95% of scenarios had
a base case that already violated the limit — a system you cannot "screen" because there is
nothing safe to certify. The gate is what turns a violation-dominated dump into a screening
dataset that straddles the boundary.

### Tuning the load ceiling under the correct oracle

The load-multiplier ceiling was swept (N-0 gate on, Q-lims enforced, 60 accepted
scenarios/setting). Higher ceiling → more bus diversity and higher violation rate, but lower
N-0 pass rate. See `feasibility/tune_sweep_hist.png` for the min_vm distribution at each
setting.

| mult_hi | N-0 pass | N-1 viol | straddle | collapse | buses | top-2 | min_vm range |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1.02 | 56.1% | 21.3% | 76.0% | 0.0% | 29 | 50.8% | [0.826, 0.955] |
| 1.05 | 48.4% | 22.8% | 75.9% | 0.0% | 38 | 46.8% | [0.837, 0.954] |
| 1.08 | 47.6% | 25.6% | 72.1% | 0.0% | 40 | 48.3% | [0.814, 0.953] |
| **1.12** | **31.4%** | **27.6%** | **72.4%** | **0.0%** | **48** | **44.7%** | **[0.762, 0.949]** |
| 1.18 | 15.7% | 31.4% | 67.4% | 0.0% | 56 | 35.7% | [0.768, 0.955] |
| 1.25 | 7.7% | 37.3% | 62.6% | 0.0% | 60 | 35.5% | [0.776, 0.951] |

**Selected `mult_hi = 1.12`**: violation rate mid-band (~28%), abundant straddle, top-2 well
under 80%, zero collapse, and a still-cheap 31% gate pass rate. Every setting satisfies the
criteria; 1.12 is the balance point.

---

## *** ORACLE DEVIATION FROM THE FEASIBILITY STUDY — read this ***

`straddle.py` and `gonogo.py` call `runpp` **without** `enforce_q_lims`. With enforcement OFF,
PV generators hold their voltage setpoint regardless of reactive output, so **generator
Q-limits have no effect on the solution at all**. This was verified empirically: varying
bus-75's `max_q_mvar` over {5, 23, 100} Mvar with `enforce_q_lims=False` gives an *identical*
result every time (min_vm = 0.9373 at bus 52); the critical bus never moves. Under the study's
own oracle, sampling axis 3 ("perturb Q-limits to move the weak bus") is **inert**, and the
physical narrative in the notes (bus 75 losing reactive support at its Q-limit) cannot actually
occur.

This generator therefore uses **`enforce_q_lims=True`**. With enforcement ON, the same bus-75
Q-limit sweep moves the critical bus across buses {117, 73, 75} and spreads min_vm from 0.895
to 0.931 — the mechanism the brief intends.

**The correct oracle lowers the feasibility ceiling [REVISED].** Re-running `gonogo.py` with
`enforce_q_lims=True` shows non-convergence hitting **100% at 160%** aggregate load (generators
saturate their Q-limits and the AC solve diverges), versus 2.7% under the old oracle. The
practical ceiling under the physical oracle is **~140%** (3.2% non-conv at 140%), not 160%.
The regeneration window (U(1.0, 1.12) per-bus, ~112% aggregate) sits comfortably inside this.
Full corrected gonogo table is in `gonogo.md`.

**Consequence:** counts here are **NOT directly comparable** to the original
`straddle-diversity.md`, which used the no-enforcement oracle. The "before" numbers quoted
below (11 buses, ~98.5% top-2, [0.940, 0.943] window) are from that prior study; the "after"
numbers are from this Q-limit-enforced, N-0-gated run. **The 2×2 experiment below is the
controlled A/B that isolates the sampling effect from the oracle effect.**

---

## Results (regenerated dataset, seed 100)

### Case census (280,500 rows, 1,500 accepted scenarios)

| Bucket | Count | % |
|---|---:|---:|
| Non-converged | 40 | 0.01% of all rows |
| Converged | 280,460 | — |
| N-1 cases (converged) | 278,960 | 100% of N-1 |
| N-1 violation (min_vm < 0.94) | 79,658 | 28.56% |
| N-1 straddle ([0.94, 0.95]) | 193,031 | 69.20% |
| N-1 deep collapse (min_vm < 0.80) | 23 | 0.008% |

N-0 gate: 1,500 accepted / 3,207 rejected (31.9% pass rate). All 1,500 accepted scenarios have
a feasible N-0 base by construction.

### 1. Critical-bus distribution — the headline

| Metric | Before (per-bus load only, old oracle) | After (broadened + gated, correct oracle) |
|---|---:|---:|
| Distinct critical (argmin) buses | 11 | **72** |
| Top-1 share | 72.7% (bus 52) | 29.4% (bus 75) |
| **Top-2 share** | **~98.5%** (buses 52, 75) | **43.8%** (buses 75, 106) |
| Top-5 share | ~99% | 62.9% |
| Top-10 share | — | 78.1% |

Top-12 buses after (bus: share of N-1 violations): 75: 29.4%, 106: 14.4%, 0: 8.1%, 37: 6.6%,
117: 4.5%, 20: 4.0%, 52: 2.9%, 51: 2.9%, 12: 2.9%, 19: 2.6%, 42: 2.3%, 73: 2.1%.

**The top-2 share (43.8%) is well below the 80% red line.** The concentration is broken. Note
[REVISED] that **bus 52 dropped from #2 (72.7% top-1 in the old study) to #7 (2.9%)** and
**bus 106 rose to #2** — bus 52's former dominance was partly an artifact of the no-gate,
no-enforcement regime. Under the correct oracle the weak-point set is genuinely distributed.

### 2. N-1 min_vm range and boundary population

| Percentile | min_vm (pu) |
|---|---:|
| min / p1 / p5 | 0.732 / 0.882 / 0.915 |
| p25 / p50 / p75 | 0.940 / 0.940 / 0.943 |
| p95 / p99 / max | 0.948 / 0.952 / 0.963 |

- min_vm spans **[0.732, 0.963]**, versus the old [0.940, 0.943] (3 milli-pu). Mass is
  concentrated near the 0.94 boundary (median exactly at the floor) with a left tail of
  violations — exactly the shape a conformal regressor of min_vm wants.
- **71.7%** of converged cases sit within ±0.005 pu of 0.94 — the calibration-critical region
  is densely populated.
- **min_vm is stored float64** [REVISED]. The previous float32 build snapped 6,541 cases onto
  exactly 0.94 and flipped **2,310 true violations to the safe side** of the decision boundary
  — the precise failure this project exists to prevent. Fixed.

### 3. Straddle and violations

- **193,031 straddle cases** (feasible, min_vm ∈ [0.94, 0.95]) and **79,658 violations** — a
  28.6% / 69.2% split. Well-balanced for both regression and threshold calibration.

### 4. Non-convergence

- **0.01%** (40 of 280,500). At the tuned ~112% window under the correct oracle, the AC solve
  is very reliable. (Contrast: the corrected gonogo table shows convergence failing hard at
  ≥160% under this oracle — the tuned window stays far from that regime.)

---

## 2×2 controlled experiment: sampling × oracle

The single most important rigor check: is the diversification a real effect of the broadened
**sampling**, or just an artifact of switching the **oracle** (Q-limit enforcement off→on)?
All four cells use the same network, same N-1 set, 100 scenarios, same seed; only the two
factors move. (`feasibility/experiment_2x2.py` → `data/experiment_2x2.json`,
`experiment_2x2.png`.)

The N-0 feasibility gate belongs to the **sampling** factor (on for new sampling, off for old),
independent of the oracle — so the reject counts differ between the two new-sampling cells
(210 vs 187) because base feasibility is evaluated under each cell's own oracle.

| sampling | oracle | distinct buses | top-2 share | N-1 viol | min_vm range | rejected |
|---|---|---:|---:|---:|---|---:|
| old (load only) | old (enforce=False) | 15 | 67.0% | 22.6% | [0.875, 0.943] | 0 |
| old (load only) | new (enforce=True) | 22 | 62.8% | 40.4% | [0.809, 0.943] | 0 |
| new (broadened+gated) | old (enforce=False) | 45 | 33.8% | 41.7% | [0.856, 0.947] | 210 |
| **new (broadened+gated)** | **new (enforce=True)** | **57** | **43.4%** | 29.1% | [0.754, 0.952] | 187 |

**Main effects on distinct-bus count:**
- Switching **sampling** old→new (oracle held): **+30** buses (old oracle), **+35** (new oracle).
- Switching **oracle** old→new (sampling held): **+7** buses (old sampling), **+12** (new sampling).

**The sampling effect is ~3–4× the oracle effect (ratios 30/7≈4.3, 35/12≈2.9).** Diversification is driven by the broadened
sampling and survives under *both* oracles; the oracle change is a smaller, additive
contribution. The diversification is real, not an oracle artifact. (Both new-sampling cells
drop top-2 below the 80% line.)

---

## Which axis moves the critical bus? (ablation — first build, indicative)

An axis-ablation on the *first* build (before the N-0 gate) found generator **setpoint
perturbation** to be the dominant axis for bus spread and **Q-limit scaling** the least
impactful for spread (though it adds voltage depth). That ranking is directional and was not
re-run under the gated pipeline; treat it as indicative. The 2×2 experiment above is the
controlled result. (`feasibility/ablation.py`, `data/ablation.json`.)

---

## Honest assessment / claim ceiling

**Supported after this run:** broadening the sampling genuinely spreads critical under-voltage
across 72 buses with top-2 at 43.8%, and — with the N-0 gate — produces a well-balanced
screening dataset (28.6% violation / 69.2% straddle) with a continuous min_vm target. The 2×2
experiment shows this is a sampling effect, not an oracle artifact. The defensible framing is
**"calibrated under-voltage screening on case118 under diversified, N-0-feasible N-1 stress"**
— a real step up from the two-bus-calibration ceiling.

**Not supported / limitations to state plainly:**
- Still **one network**. Nothing here supports network-general screening claims. With
  case118's genuine weak points (buses 75, 106, 0, 37…) still leading the distribution, a
  surrogate could report generalization that is really structural memorization of this network.
- The **oracle changed** from the original feasibility study; the old GO verdict's numbers
  (ceiling 160%, ~9 ms/case, [0.940, 0.943] window, 2-bus concentration) were computed under
  the unphysical no-enforcement oracle and are superseded by the corrected baselines.
- The ablation is from the pre-gate build and is indicative only.
- Tuning and 2×2 use 60–100 scenarios/cell; signs and rough magnitudes are robust, exact values
  would shift at full scale.

---

## What changed in the revision (2026-07)

| Fix | Before | After |
|---|---|---|
| **min_vm dtype** | float32 (snapped 2,310 violations to 0.94) | **float64** |
| **N-0 feasibility gate** | none (~95% of scenarios had infeasible base) | **on** (31.9% pass) |
| **All-NaN N-0 rows** | 326 converged rows with NaN N-0 features | **0** (gate rejects non-conv base) |
| **Load window** | per-scenario U(1.05,1.5) | **fixed U(1.0, 1.12)**, tuned |
| **Violation / straddle mix** | 96.3% / 3.7% (degenerate) | **28.6% / 69.2%** (balanced) |
| **Distinct buses / top-2** | 81 / 58.6% (on buggy data) | **72 / 43.8%** |
| **Feasibility ceiling** | 160% (old oracle) | **~140%** (correct oracle) |
| **Tests** | none | **8 degeneracy guards** (`test_dataset.py`) |
| **2×2 experiment** | not done | sampling effect ≫ oracle effect |

All 8 tests in `test_dataset.py` pass on the regenerated dataset.

---

## Files

- `feasibility/generate_dataset.py` — diversified scenario generator (N-0 gate, float64 targets, tunable knobs).
- `feasibility/tune_sweep.py` — load-ceiling sweep → `data/tune_sweep.json`, `tune_sweep_hist.png`.
- `feasibility/test_dataset.py` — 8 degeneracy guards (run: `python test_dataset.py data/dataset.parquet`).
- `feasibility/experiment_2x2.py` — controlled sampling×oracle experiment → `data/experiment_2x2.json`, `experiment_2x2.png`.
- `feasibility/ablation.py` — per-axis attribution (pre-gate, indicative) → `data/ablation.json`.
- `data/dataset.parquet` — 280,500 rows × 634 columns; targets/N-0 voltages float64, features float32.
- `data/broadened_metrics.json` — full metric set for this build.
- `feasibility/broadened_diversity.png` — before/after concentration and min_vm-straddle figure.
