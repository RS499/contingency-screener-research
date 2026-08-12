# Straddle-Case Diversity — IEEE 118-Bus N-1 Voltage Feasibility

> **⚠️ ORACLE CORRECTION (2026-07).** This study used `enforce_q_lims=False` — an unphysical
> oracle under which generator Q-limits have no effect on the solution. Two consequences:
> (1) the "bus 75 sheds voltage support at its reactive limit" narrative below **cannot
> actually occur** under this oracle (Q-limits are inert — verified: sweeping bus-75 `max_q`
> over {5,23,100} Mvar gives an identical result); (2) the specific concentration numbers
> (bus 52 = 72.7%, bus 75 = 25.8%, 11 weak buses, [0.940,0.943] window) are **oracle-dependent
> artifacts**. Re-running the same OLD sampling under the correct oracle (`STRADDLE_QLIM=1`)
> still concentrates on ~14 buses — so the diversity *caveat* stands — but under the correct
> oracle bus 52's dominance disappears (it falls to ~3% of violations in the broadened build).
> The pivotal fix is the **broadened sampling + N-0 feasibility gate** documented in
> `broadened-diversity.md`, which spreads the critical bus to 72 distinct buses (top-2 43.8%).
> The 2×2 controlled experiment there proves the diversification is a *sampling* effect, not an
> oracle artifact. Numbers below are retained for the record.

**Question.** Under non-uniform 100–130% load growth on the IEEE 118-bus system, does full
N-1 branch screening produce **> 2000 usable "straddle" cases** (voltages sitting on the
feasibility boundary) with enough diversity to *train* a voltage-violation classifier and
*calibrate* its decision threshold?

**Verdict — CONFIRMED, with a diversity caveat.** A 200-scenario sweep yields **28,740
lower-boundary straddle cases** plus **8,460 violation cases** — a ~14× margin over the 2000
target, reachable in practice with ≈15 scenarios. But the straddle set is *single-sided*
(under-voltage only), *spatially concentrated* (~11 weak buses, 99% at buses 52 & 75), and
*razor-thin* (feasible `min_vm ∈ [0.940, 0.943]`). The upper-voltage band is a generator
setpoint artifact and carries no information. The dataset is usable as-is for calibrating the
0.94 lower limit; broadening the sampling is recommended before treating it as a *diverse*
train set.

---

## Method

| Element | Choice |
|---|---|
| Network | `pandapower.networks.case118` (pandapower 3.5.4); 118 buses, 173 lines, 13 trafos, 99 loads |
| Load scenarios | **Per-bus** multiplier `m_i ~ U(1.00, 1.30)` applied independently to each load's P **and** Q — *not* uniform scaling |
| Contingency set | Full **N-1**: every branch out one at a time = 173 lines + 13 trafos = **186 elements** |
| Solve | AC power flow `runpp` (DC-initialized) per (scenario × contingency) |
| Voltage limits | `[0.94, 1.06] pu` (base case already sits at 0.943–1.05) |
| **Violation** label | `min_vm < 0.94` or `max_vm > 1.06` |
| **Near-limit straddle** | feasible **and** (`min_vm ∈ [0.94, 0.95]` **or** `max_vm ∈ [1.05, 1.06]`) |
| Scale | 200 scenarios × 186 = **37,200 cases**; 8 processes; 57 s wall |

Reproducible via `feasibility/straddle.py` (sweep, seeded per worker) and
`feasibility/analysis.py` (metrics below).

---

## Results

### Case census (37,200 cases, 200 scenarios)

| Bucket | Count | % of converged |
|---|---:|---:|
| Non-converged | 0 | 0.0% |
| Converged | 37,200 | 100% |
| **Violation** (positive class) | 8,460 | 22.7% |
| **Near-limit straddle** (usable) | **28,740** | 77.3% |

Every converged, non-violating case is a straddle case — there are **zero "comfortably safe"
cases** (`min_vm > 0.95` never occurs). The system operates hard against its lower voltage limit.

### > 2000 usable straddle cases — CONFIRMED

- **28,740** genuine straddle cases at 200 scenarios → **14.4× the 2000 target**.
- Yield ≈ **144 straddle cases / scenario**; the 2000 threshold is crossed at **≈14 scenarios**.
- 70/30 split → **20,118 train / 8,622 calibrate**, with 8,460 violation cases for the positive class.
- Deduplicated distinctness: **11,735** distinct straddle configurations at milli-pu voltage
  resolution (≈893 at coarse element+weak-bus resolution). Even the conservative count clears 2000.

### Where the straddle lives — a razor-thin, single-sided boundary

| `min_vm` percentile (straddle cases) | value |
|---|---|
| p0 / p50 / p100 | 0.9400 / 0.9420 / 0.9430 |

- Feasible minimum voltage occupies only **[0.940, 0.943] pu — a 3 milli-pu window**. Every
  straddle case is within 0.005 pu of the 0.94 limit; 14,332 are within 0.002 pu.
- The classification boundary is therefore **sharp and well-populated on both sides** (feasible
  pile-up just above 0.94; violations just below) — this is exactly what threshold calibration wants.

### The upper band is an artifact — ignore it

- `max_vm` is **pinned at exactly 1.0500** in every near case (p0=p100=1.0500) and **never comes
  within 0.005 pu of 1.06** (0 cases). It reflects the fixed voltage setpoint of the 3 highest-set
  generators (buses 9, 24, 65 at 1.05 pu), not an approach to an over-voltage violation.
- Load growth lowers voltages, so **over-voltage is not a binding constraint here**. The
  `max_vm ∈ [1.05, 1.06]` band should be dropped from the straddle definition — the real
  straddle count on the lower boundary alone is **28,740** (headline claim holds without it).

### Diversity assessment

| Dimension | Diversity | Detail |
|---|---|---|
| Contingency element | **Strong** | 170 / 186 branches produce ≥1 straddle case; spread across many lines + all trafos |
| Load pattern | **Strong** | 200 independent per-bus multiplier draws; every case has a unique loading vector |
| Spatial (weak bus) | **Weak** | Critical under-voltage at only **11 buses**; **bus 52 (72.7%)** and **bus 75 (25.8%)** dominate |
| Voltage margin | **Weak** | Feasible `min_vm` confined to a 3 milli-pu window |
| Boundary sidedness | **Single-sided** | Under-voltage only; over-voltage never engaged |

Root cause of the spatial concentration (verified against the network): **bus 52 is a pure load
bus with no local generator**, and **bus 75 is a generator held at the fleet's lowest setpoint
(0.943 pu)** that sheds voltage support once it hits its reactive limit under contingency. These
are the structural weak points of case118, so the model will legitimately learn a small recurring
set of critical buses.

---

## Implications for train + calibrate

**Usable now:** The set is well-suited to **calibrating a violation classifier's threshold around
the 0.94 lower limit** — abundant, tightly straddling, with a clean 77/23 feasible/violation split
near the boundary.

**Before treating it as a diverse *training* set**, address the concentration so the model does not
overfit to two buses and a 3 milli-pu band:

1. **Drop the `max_vm` near-band** — it is a constant setpoint feature with no signal.
2. **Widen / stress the sampling** to spread the critical bus and deepen margins:
   - extend per-bus multipliers past 1.30 (e.g. U(1.0, 1.5)) and/or apply correlated regional load blocks;
   - **vary reactive load / power factor** independently of P;
   - **perturb generator voltage setpoints and Q-limits** — this is what moves the weak bus around;
   - consider **N-1-1 / double contingencies** for rarer critical buses.
3. **Stratify the train/calibrate split by weak bus and by `min_vm` bin** so buses 117, 37, 20, 105,
   44, 28 (the long tail) are represented, not swamped by buses 52/75.
4. **Keep the 8,460 violation cases** as the positive class; class balance near the boundary is healthy.

**Bottom line:** > 2000 usable straddle cases — **confirmed with ~14× margin**. They robustly
calibrate the under-voltage limit; add sampling diversity (setpoints, reactive load, wider/correlated
multipliers) before relying on them for generalization across the network.
