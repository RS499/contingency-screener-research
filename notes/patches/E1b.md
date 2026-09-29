# E1b: the N-0 acceptance-rule test (pre-registered), N-0 quintiles, escalation split by base-case margin

Fix specification only; the author writes every word (R04/R22/R27).

## 1. Ledger ID(s) and severity
- **E1b** (review §6a; plan Part C E1b). MAJOR. Umbrella: `Top5-1.md`.
- **Conflict with the ledger (flag to lead):** the ledger (§1e E1b, §6, D6) says "lead with the unconditioned build
  (the manipulation)" and reads 56.86% → 28.83% as "removing the N-0 gate halves ρ". The author's own
  **pre-registration** (`notes/preregistration.md`, 2026-09-10, written before the run) states that the
  unconditional share "must fall for arithmetic reasons alone" (deep violations enter the denominator) and names the
  **conditional** share P(strip | not a violation) as the decisive test, with falsifier "< 50% ⇒ concentration is
  gate-made". The committed result: conditional 68.90% → 65.59% — **the falsifier is not triggered**. The
  pre-registered artifact outcome (b) required the unconditional share to fall below ~20%; it is 28.83%. So the
  unconditioned build does **not** show that the acceptance rule creates the concentration; it shows the headline
  56.86% is population-dependent (it depends on how many violations are in the denominator). The spec below is
  written to that reading. The quintiles (below) are the stronger within-data evidence and should lead.

## 2. Anchors
| # | First words (verbatim) | Line |
|---|---|---|
| a | Insert after: "Certain buses account for extreme events, with bus" (last sentence of the IV-C paragraph before the Fig. 4 float) | 314 |

## 3. Old text (verbatim)
- (a) (unchanged; insertion point) "Certain buses account for extreme events, with bus 76 being the weakest node, showing the minimum voltage in 27.1\% of contingencies, while bus 53 is second at 16.81\% and bus 107 is third at 9.31\%, as shown in Fig.~\ref{fig:busmap}."

## 4. What must change (new content, IV-C)
1. **Quintiles (lead):** split the 1,500 committed bases into five equal groups by N-0 minimum. Content: strip share
   78.4 / 81.3 / 82.4% in the three tightest groups, then 37.3% and 5.0% in the two loosest, while the violation rate
   only drifts 21.5 → 14.2%. Because the violation rate barely moves, this change is not a denominator effect: the
   concentration follows where the base case sits relative to 0.94. Present as a small table (5 rows: N-0 minimum
   range, strip share, violation rate) or one sentence giving the two ends.
   - It is a threshold, not a slope (three tightest groups are flat; rank correlation −0.6): do not call it
     proportional.
2. **Acceptance-rule test (second; pre-registered):** same generator, same arguments and seed, acceptance test
   switched off (`--no-gate`), 1,500 bases (not the same 1,500 draws: the gated build filters a longer stream).
   Content, in this order:
   - what was predicted before running, and the decisive quantity (conditional share among non-violations);
   - unconditional strip share 56.86% → 28.83%, but violation rate 17.48% → 56.04% (47.49% of unfiltered bases are
     already below 0.94 before any outage), so most of the drop is the added violations;
   - conditional share 68.90% → 65.59%: the concentration among safe outcomes survives without the acceptance test;
   - therefore the acceptance test is not what creates the pile-up; it decides how many violations sit beside it.
   - Honest-reporting requirement: the pre-registration expected outcome (c) and stated in advance what would count
     as failure. Report the outcome against those stated criteria (falsifier not triggered; artifact outcome not
     met), not against a criterion chosen afterwards.
3. **Gate consequence (from drift test 2C, `E10.md`):** calibration and test both on the looser half of bases
   (median split on N-0 minimum): histgb escalates 2.8%; on the tighter half, 59.1%. Required caveat in the same
   place: the looser half has a higher missed rate (8.25% vs 1.89%), so low escalation there is not free.
- What remains untested: the generator setpoint floor at 0.94 (`P-007.md`) is active in *both* builds, so it is a
  live candidate cause of the surviving conditional concentration; testing it is N3 (author decision). Say this.
- One definition of "strip share"/"boundary mass" throughout (C12); if the conditional share is printed, name it
  as a different quantity.

## 5. Numbers
| Value as printed | Source → key | Ledger status | Re-read | Std rule |
|---|---|---|---|---|
| quintile N-0 ranges 0.94000–0.94119 / 0.94119–0.94256 / 0.94256–0.94427 / 0.94428–0.94652 / 0.94652–0.95898 | `data/quintile_boundary_mass.json` → `quintiles_low_to_high[].base_vm_min/max` | Reported (plan VERIFIED) | re-read OK (300 bases, ~55.8k rows each) | n/a |
| strip share 78.39 / 81.28 / 82.36 / 37.31 / 4.98% | same → `boundary_mass_pct` | Reported | re-read OK | n/a (dataset shares, one generation) |
| violation 21.54 / 18.55 / 17.19 / 15.88 / 14.21% | same → `violation_pct` | Reported | re-read OK | n/a |
| rank correlation −0.6 (strip), −1.0 (violation) | same → `step2_…spearman_rank_corr`, `step4_…` | Reported | re-read OK | n/a (5 points) |
| unconditional strip 28.83% vs 56.86% | `data/unconditioned_base.json` → `unconditioned.boundary_0p94_to_0p945_pct` / `committed_gated.…` | Reported (plan VERIFIED incl. parquet) | re-read OK | n/a |
| violations 56.04% vs 17.48% | same → `*.violation_rate_pct` | Reported | re-read OK | n/a |
| **conditional strip share 65.59% vs 68.90%** (= strip / rows at or above 0.94) | recomputed from `data/unconditioned_base.parquet` (converged N-1 rows: 80,048 strip / 122,035 at or above 0.94 = 65.594%); the JSON key `unconditioned.conditional_boundary_pct` = 65.5823 was computed from 2-dp-rounded percentages (28.83 / 43.96) — do not print the key value; gated 68.904% from `data/dataset.parquet` (key 68.9045 agrees) | **not in ledger** | re-read OK (recomputed) | n/a |
| pre-registered: P1 22% (12–32), P3 66% (60–72), falsifier P3 < 50%; artifact outcome needs unconditional < ~20% AND conditional < 50% | `notes/preregistration.md` (timestamp 2026-09-10T00:40:53Z; file is **git-ignored** and the timestamp is not attested by a commit — owner must force-add/move it before the report relies on it) | not in ledger | re-read OK | — |
| 47.49% of unfiltered bases below 0.94 at N-0 (denominator: the 1,495 converged N-0 bases; over all 1,500 it is 47.33% — state the denominator); 277,628 converged rows; 5 N-0 non-converged | `unconditioned_base.json` → `unconditioned.n0_share_below_0p94_pct`, `converged_n1_rows`, `n0_nonconverged` | Reported | re-read OK | n/a |
| histgb esc 2.8 ± 0.8% (loose→loose) vs 59.1 ± 2.5% (tight→tight) | `data/drift_n0_stratum_long.parquet` via `scratch/drift_summary.py` | Reported (plan E10 VERIFIED) | re-read OK | gap 56.3 > 2.5 → **passes** |
| histgb missed 8.25 ± 1.33% (loose) vs 1.89 ± 0.61% (tight) | same | not in ledger (new caveat) | re-read OK | gap 6.36 > 1.33 → **passes** |

## 6. Must not claim
- That removing the N-0 acceptance test "halves boundary mass" as evidence that the test creates the concentration:
  the pre-registered decisive quantity says it does not.
- That removing the test changes **escalation** (no gate was run on that build).
- That the unconditioned population is a realistic screening population.
- That the setpoint floor causes the concentration (untested; N3).
- A proportional dose-response from the quintiles; that loose bases are "easy" without the missed-rate caveat.

## 7. Consistency
- `Top5-1.md` (all causal sentences) must use this reading; the ledger §6 framing line "Removing the N-0 gate halves
  ρ" should be corrected by the lead before the author reads it as the claim ceiling.
- `E10.md` reports the same 2C cells for coverage; numbers must match.
- Fig. 4 caption (l.323) prints the strip share; same definition.

## 8. Page cost and dependencies
- +0.55 pp (table 0.35 + ~3 sentences 0.2). Sentence-only version (no table): ≈ +0.2 pp.
- Artifacts tracked (commit 7fc39e4: `scripts/uncond_analysis.py`, `data/unconditioned_base.*`);
  `data/quintile_boundary_mass.json` tracked. Depends on `E1a.md` (forward pointer) and the C12 definition. Violation
  rates are pandapower-label rates (P-003).

## 9. Voice note
- The pre-registration is the student's strongest "own thinking" evidence in this section; report prediction,
  criterion and outcome in that order, plainly, including the part that did not go the way a simple story wants.
