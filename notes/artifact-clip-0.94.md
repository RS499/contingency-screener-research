# Finding: generator-setpoint clip at the 0.94 screening threshold

> **Superseded status, updated 2026-07-21.** The fix described here shipped: clipping was replaced by
> resampling, the dataset was regenerated as the canonical v2 build, and the downstream screener,
> tradeoff curve, and figures are done. Canonical numbers are in data/frozen_poster_numbers.json. A
> few body lines that had become false are corrected in place: the Status block, the 0.95 probe line,
> the domain-figure item, and the population-shift Flag. The diagnostic evidence and the probe-results
> table are unchanged.

## Symptom

10.4% of converged N-1 cases in `data/dataset.parquet` have `min_vm` equal to **exactly**
0.940000 - a literal point mass sitting on the decision threshold. It surfaced while inverting
the escalation-vs-band-width curve (the q_hat sensitivity in `tradeoff.py`): the inversion
returned degenerate factors (thousands-fold accuracy needed for 20% escalation, 10% unreachable),
which is the signature of a spike at the threshold rather than a smooth density.

## Diagnostic evidence

- `min_vm == 0.940000` exactly: 28,908 of 278,960 N-1 cases (10.4%).
- **UPDATE (T9 guard, 2026-07):** the exact-bit-pattern count UNDERSTATES the atom. A clipped PV bus
  held at its 0.94 setpoint is smeared across ~5 adjacent float64 bit-patterns by solver rounding
  noise (0.94, 0.9400000000000001, 0.9399999999999998, ...). Merging values within 1e-9 pu (far
  finer than the ~1e-4 pu spacing of physically distinct min_vm), the true clip atom is **35.17%**
  of converged N-1 rows - 3.4x the exact-match figure. The next value after the atom is at 0.06%,
  so the atom is cleanly separated from the continuum. This is what `test_dataset.py::test_T9`
  keys on.
- The argmin bus for that spike is a generator bus: bus 76 (16,511 cases) and bus 107 (9,800).
  Bus 76 is a generator with base setpoint 0.943; its `vm0` bottoms out at exactly 0.94.
- In the whole boundary band [0.94, 0.945) (55.5% of all N-1 cases), **65.7% have their weakest
  bus at bus 76 or 107**, and 78% at some generator bus. Only ~22% of the band is load-bus
  behavior.
- Generators do not physically pin at exactly 0.94; a solved PV bus holds its setpoint. So a pile
  of solved voltages at exactly 0.94 points to the setpoint itself being pinned there.

## Root cause (one line)

`feasibility/generate_dataset.py:197` -
`gen_vm = np.clip(net["_gen_vm0"] + dvm, VMIN_LIMIT, VMAX_LIMIT)` with `VMIN_LIMIT = 0.94`:
perturbed generator voltage setpoints are clipped at exactly the screening threshold, so every
draw that would fall below 0.94 stacks at 0.94. Generators with base setpoint near the floor
(bus 76 at 0.943, bus 107) clip to 0.94 in ~44% of scenarios (dvm=0.025). When such a generator
is the weakest bus, `min_vm` is exactly 0.94.

The clip does two things, not one: (1) it creates the point mass at 0.94, and (2) it biases the
setpoint distribution downward (mass that belongs below 0.94 is stacked at 0.94 instead of
redrawn higher), which raises system stress.

## What it contaminates

- **Boundary mass (the central headline).** The exact-0.94 spike (~10%) is artifact. The broader
  "~70% within +/-0.005 of 0.94" is partly inflated by it; the probe shows the core [0.94, 0.945)
  concentration is mostly genuine (see below), but the +/-0.005 figure is not clean.
- **Escalation floor.** The ~10% exact-0.94 point mass is a hard, q-independent escalation floor
  (a perfect model still escalates those cases for any positive band). CLAUDE.md 3 / 5.5 state a
  "40-55% perfect-model floor"; ~10 points of that are the clip artifact, and those cases are
  trivially predictable (min_vm equals a clipped setpoint that is a model input), so they inflate
  escalation with easy-but-boundary cases.
- **Critical-bus distribution.** Buses 76 and 107 are over-represented as the weakest bus because
  their setpoints are pinned low. Their share of the boundary band drops from 52.1% to 35.4% once
  the clip is removed. Any "critical bus" ranking (and CLAUDE.md 5.3 "72 critical buses, top-2
  43.8%") partly reflects the clip.
- **Domain figure (built on v2).** The 118-bus map colored by critical-bus frequency was rebuilt on
  the clean build and is committed at data/critical_bus_map.png. On the clip data buses 76 and 107
  were over-weighted; on v2 the top critical bus is 76 at 27.1% (frozen), followed by 53 and 107, and
  the 76/107 pairing no longer dominates.
- **2x2 sampling/oracle decomposition (CLAUDE.md 5.4).** It counts distinct critical buses as the
  diversity signal; if two generator buses are artificially pinned, the diversity counts are
  affected. Re-check after a clean regeneration.

## Probe results (150 accepted scenarios per arm, matched committed config)

Two arms, distribution statistics only, no surrogate or gate. CLIP = current behavior. RESAMPLE =
redraw dvm until the setpoint is in [0.94, 1.06] (no clip, so no point mass, SAME support - chosen
to avoid shifting the population below the threshold). Script: `feasibility/probe_clip_0_94.py`.

| Metric | CLIP (current) | RESAMPLE (fix) | committed dataset |
|---|---:|---:|---:|
| N-0 gate pass rate | 31.2% | 52.4% | ~31.9% |
| min_vm == 0.94 exactly | 9.6% | **0.0%** | 10.4% |
| in [0.94, 0.945) | 54.7% | 52.4% | 55.5% |
| within +/-0.005 of 0.94 | 70.5% | 57.0% | 71.7% |
| N-1 violation rate | 27.8% | **16.8%** | 28.6% |
| argmin at bus 76 or 107 | 52.1% | 35.4% | (dataset) |

CLIP reproduces the committed dataset on every metric, so the probe is trustworthy.

Two conclusions:

1. **The exact-0.94 point mass is a clip artifact** and is fully removed by resampling
   (9.6% -> 0.0%). Confirmed.
2. **Most of the boundary mass is genuine, not artifact.** [0.94, 0.945) barely moves
   (54.7% -> 52.4%). The marginal-network boundary concentration survives the fix; the
   +/-0.005 figure drops more (70.5% -> 57.0%) because it captured a slice of the spike.

## Flag: the fix shifts the population (not like-for-like)

Removing the clip lowers stress: the N-1 violation rate drops from 27.8% to **16.8%**, and the
N-0 gate pass rate rises from 31% to 52%. This is material (the committed dataset is 28.6%
violations). The clip was biasing generator setpoints downward, so removing it raises voltages.

Re-tuning the stress window (raising `mult_hi`) until the resampled violation rate matched ~28.6%
again was considered and deliberately rejected, not left as unfinished work. Matching on the
violation rate would be circular: the violation rate is correlated with the boundary mass being
measured, so tuning one to a target biases the other. CLAUDE.md 5.5 records this as a deliberate
choice. The v2 figures are therefore reported at their natural, lower stress (17.48% violations,
frozen), with that stated, rather than at a back-fitted 28.6%. The probe already establishes the two
things that matter: the exact-0.94 spike is an artifact, and the broader boundary mass is largely
genuine (on the committed v2 build, [0.94, 0.945) holds at 56.86%).

## Finding: the network is marginal at the 0.95 ANSI/NERC threshold (this justifies 0.94)

Why screen at 0.94 rather than the ANSI C84.1 / NERC "Range A" service voltage of 0.95 pu? Because
case118 under this study's N-0 feasibility gate is already marginal at 0.95: almost no
pre-contingency base clears it.

Direct evidence from the committed dataset (`data/dataset.parquet`, 1,500 accepted N-0 bases; every
base clears 0.94 by construction):

| N-0 base threshold | bases clearing | share of bases |
|---|---:|---:|
| min_vm >= 0.940 (the gate) | 1500 / 1500 | 100.00% |
| min_vm >= 0.942 | 610 / 1500 | 40.67% |
| min_vm >= 0.944 | 383 / 1500 | 25.53% |
| min_vm >= 0.946 | 221 / 1500 | 14.73% |
| min_vm >= 0.948 | 105 / 1500 | 7.00% |
| **min_vm >= 0.950** | **44 / 1500** | **2.93%** |
| min_vm >= 0.955 | 6 / 1500 | 0.40% |
| min_vm >= 0.960 | 1 / 1500 | 0.07% |

Base n0_min_vm range: [0.94000, 0.96047]. **Only 44 of 1,500 accepted bases (2.93%) also clear
0.95.** Screening at 0.95 would leave essentially nothing certifiable pre-contingency: the whole
population sits in a ~0.02 pu shell just above the floor. This is a property of the network under
the diversified N-0-feasible stress, not a modeling choice, and it is the concrete justification
for pinning the screening limit at 0.94. (These are CLIP-dataset figures; the resampling fix raises
base voltages, so the true 0.95 gate-pass rate is somewhat higher. The post-Task-6 N-0-only 0.95
gate probe was run: on the resampled build the 0.95 gate-pass rate is still only low single digits,
above the clip's 2.93% but far below the 0.94 gate, which confirms the network is marginal at 0.95.)

## Status

Resolved. The clip was fixed by resampling the generator setpoints (generate_dataset.py no longer
clips at the screening constant), the dataset was regenerated as the canonical v2 build, and a guard
(test T9) fails if any single min_vm value takes more than one percent of the rows. The downstream
work that was held is done: the four metrics, the tradeoff curve, and the figures are committed. On
the clean build the exact-0.94 spike is 0.00% and the boundary mass [0.94, 0.945) holds at 56.86%,
so the mechanism this memo describes survived regeneration.
