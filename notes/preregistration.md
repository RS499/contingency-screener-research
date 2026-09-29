# Pre-registration: N-0 acceptance-rule confound test

- **Timestamp (UTC):** 2026-09-10T00:40:53Z
- **git HEAD:** 14bf5ecf7e5680bf174a1523269b46bd1ab4134c
- **Written BEFORE any experiment code was run.** Only source files and committed JSON
  were read to fix definitions and the committed build command.

## The objection under test

case118 base cases are accepted only if `n0_min_vm >= VMIN_LIMIT` (0.94) at
`feasibility/generate_dataset.py:256`. Load multipliers are drawn in [1.00, 1.12].
The paper reports 56.86% of converged N-1 rows in [0.94, 0.945). Acceptance rule and
measured quantity share the 0.94 threshold. The 56.86% may be manufactured.

## Committed reference values (read from repo, not predicted)

| Quantity | Value | Source |
|---|---|---|
| boundary mass [0.94,0.945) | 56.86% | data/frozen_poster_numbers.json ceilings |
| violation rate | 17.48% | same |
| escalation @0.90, ridge | 0.48246 | frozen four_metrics_at_90pct_coverage |
| escalation @0.90, histgb | 0.32987 | same |
| case30-thermal boundary mass | 7.0862% | data/case30_thermal/case30_thermal_frozen.json |
| case30-voltage boundary mass | 20.0146% | data/case30_frozen.json |

Definition two-keyed from `feasibility/freeze_poster_numbers.py:103`:
`n1 = df[(outaged_type != "none") & converged]; y = n1.min_vm`
`boundary = 100*mean((y >= 0.94) & (y < 0.945))`; `violation = 100*mean(y < 0.94)`.
Denominator is ALL converged N-1 rows.

## Mechanism I expect, stated before measuring

Outages only lower voltage. A base case already below 0.94 will produce N-1 rows that
are almost all violations. Removing the gate therefore injects a large block of
deep-violation rows into the DENOMINATOR. The unconditional boundary share must fall
for arithmetic reasons alone, even if the shape of the distribution near the limit is
completely unchanged.

That makes the unconditional number a weak test. The sharp test is the CONDITIONAL
quantity, which I pre-register as the decisive one:

```
conditional_boundary = P(0.94 <= min_vm < 0.945  |  min_vm >= 0.94)
                     = boundary_mass / (1 - violation_rate)
committed: 56.86 / 82.52 = 68.90%
```

If the conditional survives ungated, the near-limit concentration is a property of the
network. If it collapses too, it was manufactured by the acceptance rule.

## Predictions

| # | Quantity | Point | Range | Confidence | Falsifier |
|---|---|---|---|---|---|
| P1 | Unconditional boundary mass, ungated | **22%** | 12-32% | MODERATE magnitude / HIGH that it falls below 40% | >= 45% falsifies |
| P2 | Violation rate, ungated | **55%** | 40-70% | HIGH direction / MODERATE magnitude | <= 25% falsifies |
| P3 | **Conditional boundary mass, ungated** | **66%** | 60-72% | MODERATE | < 50% falsifies (concentration itself is gate-made) |
| P4 | Acceptance rate, ungated | **100.0%** | exactly | HIGH (code has no other reject branch) | any rejection > 0 falsifies |
| P5 | n0_min_vm share below 0.94, ungated | **45%** | 30-65% | MODERATE | outside 20-75% falsifies |
| P6 | Escalation @0.90 ridge, if rerun | **0.32** | 0.22-0.45 | LOW | >= committed 0.482 falsifies |
| P7 | Escalation @0.90 histgb, if rerun | **0.22** | 0.14-0.32 | LOW | >= committed 0.330 falsifies |
| P8 | Largest 0.001-pu bin, ungated | still the [0.940,0.941) bin; share falls roughly in proportion to P1 | - | MODERATE | a different bin becoming tallest falsifies |

P6/P7 are only to be evaluated if PART C returns (a).

## Which outcome means the escalation-floor thesis is an artifact

Stated plainly, in advance:

**ARTIFACT (outcome b)** requires BOTH:
1. Unconditional boundary mass falls below ~20%, i.e. into the neighbourhood of the
   case30-voltage 20.01% and case30-thermal 7.09% figures; AND
2. Conditional boundary mass falls below 50%.

If both hold, the 56.86% is a product of the sampler, the escalation floor is not a
property of case118, and the paper's central claim needs rescoping.

**NETWORK PROPERTY (outcome a)** requires the unconditional boundary mass to stay at or
above ~45% with the gate removed.

**IN BETWEEN (outcome c)** is what I actually expect: condition 1 holds and condition 2
fails. That would mean the unconditional 56.86% headline is population-dependent and
must be restated as conditional on N-0 feasibility, while the near-limit concentration
among N-0-feasible cases remains a real property of case118. I record now that I regard
(c) as the most likely outcome, so that claiming it afterwards is not a free move.

## What would make me report failure

If P3 lands below 50% I will report outcome (b) plainly and state that the boundary-mass
floor is an artifact of the acceptance rule, regardless of how the unconditional number
compares to case30.
