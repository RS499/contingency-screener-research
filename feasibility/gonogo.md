# IEEE 118-Bus Loading Sweep — Feasibility GO/NO-GO

> **⚠️ ORACLE CORRECTION (2026-07).** The table below was computed with
> `enforce_q_lims=False` — an **unphysical oracle** under which PV generators hold their
> voltage setpoint regardless of reactive output (generator Q-limits have no effect). Under
> the physically correct oracle (`enforce_q_lims=True`, now the project default), the
> feasibility picture changes materially:
>
> | Loading | Non-conv (old oracle) | Non-conv (correct oracle) | Min V (correct) |
> |--------:|----------------------:|--------------------------:|----------------:|
> | 100% | 0.0% | 0.0% | 0.886 |
> | 120% | 0.0% | 0.0% | 0.827 |
> | 140% | 1.1% | **3.2%** | 0.647 |
> | 160% | 2.7% | **100.0%** | (diverges) |
> | 180% | 17.6% | **100.0%** | (diverges) |
>
> **The practical feasibility ceiling under the correct oracle is ~140%, not 160%** —
> generators saturate their Q-limits and the AC solve diverges at ≥160%. Solve time also
> roughly doubles (Q-limit enforcement is iterative). The GO verdict for the *pipeline* still
> holds (the sweep converges reliably and fast through 140%), but any scenario generation must
> cap at ~140% under the correct oracle. Re-run with `GONOGO_QLIM=1 python gonogo.py`.
> The original (old-oracle) table is retained below for the record.

**Verdict: GO** (pipeline feasibility; see oracle correction above for the corrected ceiling)

Pipeline feasibility gate for the RISE load-sweep analysis. Evaluates whether the pandapower N-1 sweep is a reliable, fast basis for downstream work across the intended operating envelope, and characterises grid security along the way.

## Method

- **Network:** IEEE 118-bus (`pandapower.networks.case118`) — 118 buses, 173 lines, 13 transformers, 4242.0 MW base load.
- **Sweep:** load scaled to 100/120/140/160/180 % of nominal (P and Q).
- **Cases per level:** 187 = 1 base (N-0) + N-1 contingencies (each in-service line and transformer removed one at a time).
- **Solver:** Newton-Raphson (`runpp`, flat start, numba off).
- **Binding constraint:** bus voltage. `case118` ships with very high thermal ratings (max_i_ka ~41 kA) so branch loading never nears its limit; voltage limits 0.94-1.06 pu bind first.
- **Near-limit (straddle):** feasible case hugging a limit — min bus voltage in [0.94, 0.95] pu, max in [1.05, 1.06] pu, or thermal loading in [95, 100] %.
- **Violation:** min V < 0.94 pu, max V > 1.06 pu, or thermal > 100 %.
- **Versions:** pandapower 3.5.4, pandas 2.3.3.

## Results per loading level

| Loading | Cases | Near-limit (straddle) | Violations | Non-conv | Non-conv rate | Solve mean (ms) | median (ms) | p95 (ms) | Min V (pu) |
|--------:|------:|----------------------:|-----------:|---------:|--------------:|----------------:|------------:|---------:|-----------:|
| 100% | 187 | 175 | 12 | 0 | 0.0% | 11.55 | 9.01 | 19.19 | 0.902 |
| 120% | 187 | 155 | 32 | 0 | 0.0% | 9.17 | 8.36 | 15.58 | 0.884 |
| 140% | 187 | 0 | 185 | 2 | 1.1% | 8.66 | 8.09 | 9.80 | 0.750 |
| 160% | 187 | 0 | 182 | 5 | 2.7% | 8.94 | 8.54 | 9.47 | 0.804 |
| 180% | 187 | 0 | 154 | 33 | 17.6% | 9.77 | 9.72 | 10.21 | 0.735 |

## Decision rule

| # | Criterion | Threshold | Result | Pass |
|---|-----------|-----------|--------|:----:|
| 1 | Solver reliability over envelope [100, 120, 140] % | non-conv ≤ 5% | max 1.1% | ✅ |
| 2 | Performance (all levels) | p95 < 100 ms | max 19.2 ms | ✅ |
| 3 | Nominal solution exists at 100% | converged | yes | ✅ |

## Findings

- **Solver is fast and reliable through 120% loading** (0% non-convergence, p95 ≤ 19 ms). Non-convergence appears at 140% (1.1%), rises to 2.7% at 160%, and reaches 17.6% at 180% — the tractable analysis ceiling is ~160%.
- **Grid security caveat:** the network is *not* N-1 secure even at nominal load — 12 of 187 contingencies breach the 0.94 pu voltage floor at 100% (min V 0.902), growing to 32 at 120%. This is a grid-adequacy issue, separate from the pipeline-feasibility verdict above.
- **Straddle behaviour:** at 100-120% most feasible cases hug the voltage floor (175 / 155); by 140%+ the straddle band empties as nearly every case crosses into full violation.

## Verdict

**GO** — the pandapower N-1 sweep converges reliably (≤1.1% non-convergence) and fast (p95 < 100 ms) across the 100-140% envelope, so it is a sound basis for the downstream RISE analysis. Constrain scenario generation to ≤160% loading (solver convergence degrades sharply beyond it) and treat the nominal-load N-1 voltage violations as a grid-reinforcement finding to carry forward, not a blocker for the modelling pipeline.
