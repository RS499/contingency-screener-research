# Claims map

Binds each differentiator to the Discussion sentences that qualify it and the papers
cited alongside, and each derived quantity to the sentence that derives it.

**Why dependency edges.** A derived number can be orphaned by deleting the sentence that
derives it, leaving a figure in the text with nothing behind it. That happened exactly
once in the prior version. The `derived_from` edges below exist so a deletion that
orphans a number fires a gate rather than surviving to submission.

**Why qualifier edges.** A differentiator stated without its qualifier is an overclaim.
When a differentiator changes, its qualifier almost always needs to change with it, and
the two are usually in different sections written weeks apart.

Line numbers are against `report/paper_current_STS.tex` at sha256 `754be12b…`,
344 lines. **Re-anchor after any edit** — these are positions, not identities.

---

## Part 1 — Differentiators and their qualifiers

### D1. Per-case band rather than a per-stratum guarantee

- **Stated:** L86 (Introduction, "unlike the first two approaches, we add a band to each contingency")
- **Cited alongside:** `manoharan2026`, `alcantara2026`, `christianson2025`
- **Qualified by:** L258 (Discussion, "coverage rates are measured averages rather than guarantees on individual contingencies")
- **Standing risk:** `alcantara2026` also uses conformal prediction. The real distinction is per-case action versus per-stratum guarantee, not the presence of a band. If D1's wording changes, L258 and the Related Work framing must change with it.
- **Status:** LIVE — flagged in the URTC camera-ready list.

### D2. Under-voltage only, one-sided band

- **Stated:** L92 (Background), L112 (Method, "the primary source of the danger is the voltage being less than the predicted one")
- **Qualified by:** L262 (Discussion limitations, "we only checked if the final voltage was too low")
- **Depends on:** the claim that over-voltage is not a live constraint here.
- **Standing risk:** **UNRESOLVED.** 73.1% of converged N-1 rows and 73.4% of N-0 base rows have `max_vm` > 1.05 (`data/dataset.parquet`). Over-voltage is a pre-outage property of the sampled setpoints, not a contingency effect — but it is not absent, and no artifact records this. If D2's justification is stated as "over-voltage does not occur", it is false as written. The survivable form states that one-sided treatment suits the load-stress regime and that two-sided screening is out of scope **with the sampling reason given**.
- **Blocks:** Section V.

### D3. The escalation floor and its mechanism

- **Stated:** L86 (Introduction, "we explain why there must be a certain floor for escalation"), L233–248 (Results IV-C)
- **Qualified by:** L260 (Discussion, "The floor exists on any network, but its height depends on the data distribution")
- **Standing risk:** "exists on any network" is a network-general claim from two networks. CLAUDE.md §8 forbids network-general claims from one network; two is not obviously enough either. Contrast with the case30 numbers at L260.
- **Status:** LIVE.

### D4. Net-cost accounting (escalated solver time charged against the speedup)

- **Stated:** L84 (Introduction), L127–131 (Method, Eq. 2)
- **Qualified by:** nothing currently.
- **Missing qualifier:** Eq. 2 charges escalated solves but not the 280,500 solves that built the dataset. `data/break_even.json` now exists and quantifies this; no sentence cites it.
- **Status:** GAP — a differentiator with no qualifier.

### D5. Model selection does not follow accuracy

- **Stated:** L229–231 (Results IV-B)
- **Qualified by:** L231 (miss-depth shares at 0.90 coverage)
- **Strengthening evidence not yet used:** at the recommended operating points, ridge@0.94 has max miss depth 0.0324 pu while histgb@0.97 still contains the 0.0915 pu miss (`data/missed_depth.json`). Table II presents the two as equivalent on frequency alone.
- **Status:** UNDERSTATED.

---

## Part 2 — Derived quantities and their deriving sentences

| Quantity | Value | Derived at | Artifact | Orphan risk |
|---|---|---|---|---|
| escalation ceiling, ridge | 74.9% | L248 | `data/frozen_poster_numbers*.json` | HIGH — derived and used in one sentence |
| escalation ceiling, histgb | 82.8% | L248 | same | HIGH |
| saturation point | 82.52% | L248 | complement of the violation rate | HIGH — L248 asserts histgb's ceiling "essentially lands on" it; 82.8 vs 82.52 is the whole claim |
| boundary strip share | 56.86% | L235 | `data/frozen_poster_numbers.json` | MEDIUM |
| violation rate | 17.48% | L104, L235 | `data/dataset.parquet` | LOW — stated twice |
| band width, ridge | 0.0052 pu | L116 | `data/tradeoff_curve_v2.json` | MEDIUM |
| band width, histgb | 0.0023 pu | L116, L248 | same | MEDIUM |
| deepest miss | 0.0915 pu / 0.8485 | L225, L231, L262 | `data/missed_depth.json` | LOW — stated three times |
| bases clearing 0.95 | 86 of 1,500 | L260 | `data/bases_clearing_0p95.json` | HIGH |
| escalation at L=0.95 | "roughly 1.5%" | L260 | `data/escalation_at_095.json` | HIGH — hedged; the hedge is load-bearing (seed-mean 1.38% ridge / 1.58% histgb) |
| `t_solve` | 9.14 ms | L131 | `data/solve_time.json` | LOW |
| bin share cap | "around 14%" | L235 | NOT LOCATED | **NO SOURCE** — hedged, and the hedge cannot be checked against an artifact |

---

## Part 3 — Open edges

- **`bin share cap ~14%` → NO SOURCE.** L235 states no 0.001-pu bin exceeds about 14% of the dataset. No artifact in `data/` was found carrying this. Either locate it or remove the sentence.
- **D4 has no qualifier sentence.** `data/break_even.json` and `data/parallel_speedup.json` both exist and neither is cited anywhere in the manuscript.
- **D2's justification is unresolved** pending the thermal/over-voltage artifact (Stage 2A).
- **Three drift experiments (2C, 2D, 2E) have no claims and no edges yet.** Add rows when the artifacts exist, not before.
