# Top5-1: the causal claim — boundary mass is set by the sampler and the limit, not by case118 itself

Fix specification only; the author writes every word (R04/R22/R27). This file is the umbrella for the causal
wording. The evidence placements are `E1a.md` (one sentence), `E1b.md` (manipulation + quintiles), `E1c.md`
(limit sweep), `P-007.md` (setpoint floor).

## 1. Ledger ID(s) and severity
- **Top-5 #1** (review; POWER-03, STATS-07, STS-03/04, NS-06). **MAJOR** (prior review said FATAL; panels D-a:
  the measurement is robust, the causal reading fails). Linked: C7, C12, P-007, D8, OS-10.

## 2. Anchors
| # | First words (verbatim) | Line |
|---|---|---|
| a | Title: "Conformal‑Gated Surrogate Screening for N‑1 Under‑Voltage" | 63 |
| b | "Finally, I explain why there must be a" | 101 |
| c | "This implies that clustering is an inherent characteristic" | 121 |
| d | "and second, I also explain why the speedup" (second clause of the sentence beginning "In this study, two things differ") | 361 |
| e | "This escalation floor is set by how the" | 365 |
| f | "On this network, safety and speed are inversely" | 388 |
| g | "The main reason is that most of the" | 388 |
| h | "What this study contributes here is the reasoning" | 388 |
| i | "Most of the contingencies lie within 0.005 per" | 314 |

## 3. Old text (verbatim)
- (a) "\title{\textbf{Conformal‑Gated Surrogate Screening for N‑1 Under‑Voltage Contingencies: Safety and Throughput Limits Set by Boundary Mass}}"
- (b) "Finally, I explain why there must be a certain floor for escalation."
- (c) "This implies that clustering is an inherent characteristic of the network and the sampling process."
- (d) "In this study, two things differ from that literature. First, I fall back to an exact solver instead of a more complex model, so the escalated case can be resolved, and second, I also explain why the speedup is capped, which is because most of the data is very close to the limit."
- (e) "This escalation floor is set by how the distribution of the data occurs in relation to the 0.94 pu limit."
- (f) "On this network, safety and speed are inversely related, though the 30-bus result shows that this depends on data distribution relative to the limit."
- (g) "The main reason is that most of the cases fall very close to the limit."
- (h) "What this study contributes here is the reasoning for the existence of such a floor, and a warning that people should expect less speed-up from a surrogate model that is calibrated to be safe on average over the N-1 distribution."
- (i) "Most of the contingencies lie within 0.005 per unit of the boundary, resulting in a significant number of escalations."

## 4. What must change
Keep (supported): the **measurement** (56.86% of converged N-1 rows in [0.94, 0.945)) and the **accounting**
(a case is escalated exactly when its prediction lies within one band width above the limit, so escalation tracks
the prediction mass in that window).

Change (not supported as written): the **cause**. What the evidence on disk supports:
- the N-1 pile-up is **inherited from the base cases**: most outages barely move the minimum voltage (77.6% of rows
  within 0.001 pu of their base case; `E1a.md`), and within the committed data the strip share falls from ~78–82%
  (three tightest base-case quintiles) to 4.98% (loosest) while the violation rate barely moves (`E1b.md`);
- the base cases sit at the limit under this sampler: 67.73% of accepted bases already have N-0 minimum in the strip;
  the sampler accepts bases at ≥ 0.94 and floors generator setpoints at 0.94 — both equal to the limit (`P-007.md`);
- **but** the pre-registered acceptance-rule test (`notes/preregistration.md`) did not find the acceptance test to be
  the cause: without it the unconditional share falls to 28.83% mostly because violations rise to 56.04%, while the
  pre-registered decisive quantity (share among non-violations) stays 65.59% vs 68.90% (falsifier < 50% not hit).
  The setpoint floor is active in both builds and is untested (N3).
- Supported ceiling, therefore: "on case118 under this sampler, the concentration is inherited from base cases that
  sit just above the limit; the acceptance test is not what creates it; which sampler choice (setpoint floor, load
  window) or network property puts the bases there is not isolated." Neither "network property" nor "made by the
  acceptance test" is supported. (This differs from the ledger §6 line "Removing the N-0 gate halves ρ … Not a
  property of the network alone"; flagged to the lead.)
Per sentence:
- (a) Title: retitling is an author decision (§5 of the ledger). If "Boundary Mass" stays, the term must be defined
  at first use in the abstract/intro (C12), and nothing in the title may imply a network property.
- (b) Remove "must": per-element (Mondrian) calibration lowers escalation at matched missed rate (Top-5 #2(b)); the
  floor is not forced. The contribution item should say what was *shown* (the accounting + the sampler cause), not
  a necessity.
- (c) Replaced by `E1a.md` content.
- (d) Same as (b)/(g): scope to "on this data".
- (e) Contains the checker-banned phrase "escalation floor" (OS-10); restate as the escalation level that the
  boundary density sets for a given band width on this sampled population.
- (f) The 30-bus contrast cannot carry "depends on data distribution relative to the limit" as a clean comparison:
  it differs in network and sampler at once (`P-007.md`). The within-network evidence for "depends on where the base
  cases sit" is the quintile split (`E1b.md`), and it should carry this sentence's load.
- (g)/(h) Conclusion: the reason is the density of outcomes just above the limit in this sampled population,
  inherited from base cases that sit there; the contribution is (i) the accounting, (ii) the inheritance evidence and
  the pre-registered test that ruled out the acceptance rule as its cause, and (iii) the cross-network ρ·q̂ check with
  its named failure (`E2.md`). The "warning" can stand if scoped to populations whose base cases sit near the limit.
- (i) "Most … within 0.005 per unit": the committed key is the 56.86% strip share (0.94–0.945, i.e. *above* the
  limit only); "within 0.005 of the boundary" on both sides is 61.61% (P-008, no tracked key yet). Use one quantity,
  named once.

## 5. Numbers
| Value as printed | Source → key | Ledger status | Re-read | Std rule |
|---|---|---|---|---|
| 56.86% in [0.94, 0.945) | `data/frozen_poster_numbers_v2.json` → `dataset_facts.boundary_0p94_to_0p945_pct`; `data/sts_dataset_facts.json` → `boundary_strip.share_of_converged_n1_pct` 56.863 | Reported / VERIFIED (d-figs) | re-read OK | n/a (dataset count) |
| 77.6% of N-1 rows within 0.001 pu of their N-0 minimum (216,605 / 278,955) | `data/sts_dataset_facts.json` → `n0_persistence.share_within_pct` 77.649 | VERIFIED (d-figs) | re-read OK | n/a |
| 28.83% (unconditioned build) vs 56.86% | `data/unconditioned_base.json` → `unconditioned.boundary_0p94_to_0p945_pct`, `committed_gated.…` | Reported (plan: VERIFIED 09-27 incl. parquet recompute) | re-read OK | n/a (single build, one seed of generation) |
| conditional share 65.59% vs 68.90% (pre-registered decisive quantity) | recomputed from `data/unconditioned_base.parquet` (converged N-1 rows: 80,048 strip / 122,035 at or above 0.94 = 65.594%); the JSON key `unconditioned.conditional_boundary_pct` = 65.5823 was computed from 2-dp-rounded percentages (28.83 / 43.96) — do not print the key value; gated 68.904% from `data/dataset.parquet` (key 68.9045 agrees); `notes/preregistration.md` P3 (git-ignored file — owner must force-add or move it before citing) | not in ledger | re-read OK (recomputed) | n/a |
| quintiles 78.39 / 81.28 / 82.36 / 37.31 / 4.98% | `data/quintile_boundary_mass.json` → `quintiles_low_to_high[].boundary_mass_pct` | Reported (plan VERIFIED) | re-read OK | n/a |
| 67.73% of bases with N-0 min in the strip | parquet (see `P-007.md`) | VERIFIED (teammate) | re-read OK (no JSON key yet) | n/a |
| case30 7.09% vs case118 56.86% | `case30_thermal_frozen.json` → `boundary_mass_pct` 7.0862 | Reported | re-read OK | n/a |
| within 0.005 pu both sides: 61.61% | P-008 (no tracked key) | recomputes (ledger) | not re-read — **do not print until d-figs adds the key** | n/a |

## 6. Must not claim
- "Inherent", "network property", "set by the network", or any network-general claim (CLAUDE.md §8; one network
  plus four small ones, all with their own samplers).
- "Must" / "necessarily" for the floor (Mondrian refutes necessity).
- That the unconditioned build shows lower *escalation*: only the strip share (and violation rate) were measured on
  it; no gate was run on that build.
- That "the N-0 gate makes the concentration" in any form (the pre-registered decisive test says it does not:
  conditional share 68.90% → 65.59%, falsifier < 50% not hit), or that the setpoint floor does (untested).
- **Open causal question (must be named as open in the paper):** whether the generator-setpoint floor at 0.94
  (`P-007.md`) puts the base cases at the limit. Testing it is an N3-class rebuild (floor 0.94 vs 0.95, ≥ 5 seeds);
  author decision, not authorized in this run.
- The phrases "escalation floor" and "proven methods" (checker-banned, OS-6/OS-10).

## 7. Consistency
- Abstract l.81: "where the regenerated 30-bus network has 7.09\% … compared to 56.86\% for case118" and last
  sentence "These results allow operators to make an informed decision…" (OS-1, Top-5 #5 framing).
- IV-C heading l.312 "The boundary layer sets a floor on escalation" (P-014: the floor never has a number).
- l.347 ceiling/saturation paragraph (keep; D5).
- l.365 case30 block (`E4.md`, `E1c.md`).
- Every place "boundary mass" appears (title, l.81, l.353) must use one definition; note `data/sts_limit_sweep.png`
  labels a *different* quantity "boundary mass in [L, L+q̂)" (`E1c.md`).

## 8. Page cost and dependencies
- ≈ 0 pp here (rewrites); evidence costs are counted in E1a (+0.03), E1b (+0.55), E1c (+0.6), P-007 (+0.07).
- Depends on: title decision (author, §5); should be written after E1a/E1b/P-007 content is settled.

## 9. Voice note
- Define "boundary mass" once, in plain words (the share of outcomes that land just above the limit), before its
  first use in the abstract, and never use it for any other window.
