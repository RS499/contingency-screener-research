# E1a: replace the "inherent characteristic" sentence with the inheritance-from-N-0 evidence

Fix specification only; the author writes every word (R04/R22/R27).

## 1. Ledger ID(s) and severity
- **E1a** (review §6a; plan Part C E1a). MAJOR. Also closes **C7**. Umbrella: `Top5-1.md`.

## 2. Anchors
| # | First words (verbatim) | Line |
|---|---|---|
| a | "This implies that clustering is an inherent characteristic" | 121 |
| b | "After modifying the code and resampling the data," (preceding sentence, carries 55.5 → 56.86) | 121 |

## 3. Old text (verbatim)
- (a) "This implies that clustering is an inherent characteristic of the network and the sampling process."
- (b) "After modifying the code and resampling the data, the exact spike at 0.940000 per unit went away, but the number of rows in the narrow band [0.94, 0.945) stayed about the same, moving from 55.5\% to 56.86\%."

## 4. What must change
- Remove (a). In its place (same position, end of the clipping paragraph in III-A), the content must be:
  - the pile-up above 0.94 is inherited from the base cases, not created by the outages;
  - why: base cases are accepted only at or above 0.94 (same value as the limit), and generator setpoints have a
    floor at the same value (`P-007.md` — one sentence can carry both, or P-007's sentence can sit just before);
  - evidence: 77.6% of converged N-1 rows have a post-outage minimum within 0.001 pu of their own base-case minimum
    (median difference 3.3 × 10⁻⁶ pu);
  - a forward pointer to IV-C, where the manipulation (`E1b.md`) is shown.
- Optional second fact (only if space): 96.3% of strip rows come from base cases whose own N-0 minimum is already
  below 0.945, and 93.4% of strip rows have the same weakest bus as their base case. One of the two is enough.
- (b): keep, but the "55.5\%" should cite its tracked source: `data/clip_artifact.json` → `clip_era.boundary_0p94_to_0p945_pct`
  = 55.51 (the clip-era parquet itself is git-ignored; its sha256 matches the tracked `clip_era.input_sha256`). Either print 55.51 with the
  provenance caveat, or describe the before/after qualitatively.

## 5. Numbers
| Value as printed | Source → key | Ledger status | Re-read | Std rule |
|---|---|---|---|---|
| 77.6% (216,605 of 278,955 rows) within 0.001 pu of N-0 min | `data/sts_dataset_facts.json` → `n0_persistence.share_within_pct` = 77.6487; `n_within` 216605 | VERIFIED (d-figs, byte-reproducible) | re-read OK | n/a (dataset count) |
| median |Δ| 3.3 × 10⁻⁶ pu | same → `n0_persistence.median_abs_diff_pu` = 3.3135e-6 | VERIFIED (d-figs) | re-read OK | n/a |
| 96.3% of strip rows from bases with N-0 min < 0.945 | same → `boundary_strip.share_base_n0_below_strip_hi_pct` = 96.265 | VERIFIED (d-figs) | re-read OK | n/a |
| 93.4% same weakest bus as N-0 | same → `boundary_strip.share_same_weakest_bus_as_n0_pct` = 93.374 | VERIFIED (d-figs) | re-read OK | n/a |
| 56.86% (after clip fix) | `data/frozen_poster_numbers_v2.json` → `dataset_facts.boundary_0p94_to_0p945_pct` | Reported | re-read OK | n/a |
| 55.51% (before clip fix) | `data/clip_artifact.json` (tracked) → `clip_era.boundary_0p94_to_0p945_pct` 55.51 | Reported (2b-2) | re-read OK (verifier also recomputed 55.512% from the ignored `data/archive_clip/dataset.parquet`) | n/a |

Note: `data/sts_dataset_facts.json` and its script are **untracked**; the owner must commit them before the number
is printed (ledger 2c, REPRO-10).

## 6. Must not claim
- That the network itself produces the pile-up (C7).
- That outages "do not change" voltages: 22.4% of rows move by more than 0.001 pu, and the mean |Δ| is 0.0043 pu
  (`n0_persistence.mean_abs_diff_pu`); the claim is about the typical row.

## 7. Consistency
- `Top5-1.md` (all causal sentences), `P-007.md` (setpoint floor sentence right next to this one), `E1b.md` (the
  forward-pointer target), l.349 persistence paragraph (persistence predicts the N-0 minimum; the 77.6% is also why
  persistence's MAE is 13.1% higher than ridge's (ridge 11.6% lower) — P-027 "accurately").

## 8. Page cost and dependencies
- +0.03 pp (one sentence replaced by one slightly longer sentence).
- Depends on: owner committing `data/sts_dataset_facts.*`; write with `P-007.md`.

## 9. Voice note
- "Base case" is defined at l.107; use that term, not "N-0 row" or "pre-outage row", in this sentence.
