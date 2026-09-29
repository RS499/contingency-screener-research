# E1c (+P-016): limit-sweep figure; replace the "0.94 is conservative / 0.95 finds everything hazardous" block

Fix specification only; the author writes every word (R04/R22/R27).

## 1. Ledger ID(s) and severity
- **E1c** (review §6a; plan E1c) MAJOR; **P-016 NEW** (NS-11; d-figs flag 2) MAJOR — folded here.
- D6 resolution applies: the sweep is **near-tautological as a causal test** (its lower panel is the true-outcome
  mass in the same window the gate escalates on). Use it to show *where* the escalation spike sits, not *why*.

## 2. Anchors
| # | First words (verbatim) | Line |
|---|---|---|
| a | Insert figure + sentences after: "The gradient-boosted model's band is only 0.0023" | 347 |
| b | "I use 0.94 pu as a conservative choice." | 365 |
| c | "Only 86 of the 1,500 base cases are" | 365 |
| d | "In other words, it finds everything hazardous." | 365 |

## 3. Old text (verbatim)
- (a) (unchanged; insertion point) "The gradient-boosted model's band is only 0.0023 pu wide, but so much of the distribution sits just above 0.94 that this narrow window still captures 30.6\% of all contingencies."
- (b) "I use 0.94 pu as a conservative choice."
- (c) "Only 86 of the 1,500 base cases are above 0.95 pu, and increasing the threshold to 0.95 pu leads to a ridge escalation of 1.38$\pm$0.33\%."
- (d) "In other words, it finds everything hazardous."

## 4. What must change
- **New figure** (IV-C, after a): `data/sts_limit_sweep.png` (d-figs, prose-free, manifest present). Two panels vs
  screening limit L = 0.900–0.955 at target 0.90, both models, ±1 std shading: escalation rate; and share of test
  outcomes in [L, L + q̂). Caption must carry:
  - the coverage target (0.90) and that L is re-applied to the *same* data and models (only the limit moves);
  - that the lower panel's quantity is the outcome share in [L, L + q̂) — **not** the paper's fixed "boundary mass"
    strip [0.94, 0.945). The image's y-label says "boundary mass in [L, L+q̂)"; either the caption names the
    difference or d-figs relabels (C12: one meaning per term);
  - the shading is ±1 std over 5 splits (P-023).
- **Two sentences** (after the figure reference): escalation peaks at L = 0.94, the value at which base cases were
  accepted and setpoints floored; below ~0.936 histgb escalates under 2%; ridge has no flat region close to the
  limit (≤ 3.2% only up to L = 0.930). Scope: this locates the spike; it does not by itself show what causes it (D6).
- **Replace (b)–(d)** (Discussion): (b) is contradicted by the sweep — 0.94 is where escalation is highest, not a
  conservative setting. (c)/(d) must be rewritten with the reason escalation is low at 0.95 (P-016): at L = 0.950,
  95.71% of test outcomes are violations and are simply flagged; low escalation there is not a usable operating
  point. State the coverage target (0.90) and give both models, not ridge only.
- "Only 86 of the 1,500 base cases are above 0.95 pu" may stay (re-read OK) but must be tied to the violation share
  it implies.
- Optional (plan): separate normal vs emergency post-contingency limits — **no verified citation** in
  `notes/prior-art.md`; do not add without one.

## 5. Numbers
| Value as printed | Source → key | Ledger status | Re-read | Std rule |
|---|---|---|---|---|
| histgb esc 30.63 ± 2.51% at L = 0.940 | `data/sts_limit_sweep.json` → `summary.histgb.escalation_mean/std_at_0p940`; cross-check = `tradeoff_curve_v2` (abs diff 0.0) | VERIFIED (d-figs) | re-read OK | — |
| ridge esc 49.07 ± 2.66% at L = 0.940 | same, ridge | VERIFIED (d-figs) | re-read OK | — |
| histgb 0.26–1.77% for L ≤ 0.936 | same → `escalation_mean_min/max_for_L_le_0p936` | VERIFIED (d-figs; plan "DIFFERENT (minor)" vs review 0.3–1.5) | re-read OK | — |
| histgb 5.46 ± 1.25% at 0.938; 19.44 ± 3.16% at 0.939 | `curves.histgb[L]` | Reported (plan) | re-read OK | — |
| ridge ≤ 3.23% only up to L = 0.930 (3.23 ± 0.24%); 19.60% at 0.936 | `curves.ridge[L]` | VERIFIED (d-figs) | re-read OK | — |
| ridge max 51.43% at L = 0.941 (peak one step above 0.94) | `summary.ridge.L_of_max_escalation_mean` 0.941, `max_escalation_mean` 0.5143 | not in ledger | re-read OK | 51.43 ± 1.98 vs 49.07 ± 2.66 at 0.940: gap 2.36 < 2.66 → peak location 0.940 vs 0.941 **not distinguishable**; say "at 0.94" for both |
| L = 0.950: ridge 1.38 ± 0.33%, histgb 1.58 ± 1.19% | `summary.*.escalation_mean/std_at_0p950` | VERIFIED (d-figs) | re-read OK | ridge vs histgb: 0.20 < 1.19 → **no difference** |
| 95.71% of test outcomes are violations at L = 0.950 | `curves.*[L=0.95].violation_rate_mean` 0.9571 | VERIFIED (d-figs) | re-read OK | n/a |
| 86 of 1,500 bases above 0.95 pu | `data/dataset.parquet` base rows (`outaged_type == 'none'`), `min_vm > 0.95` | Reported (in .tex) | re-read OK (86; no JSON key — d-figs to add) | n/a |
| lower panel peak ~60% (ridge) / ~31% (histgb) at 0.94 | `curves.*[L=0.94].boundary_mass_mean` 0.6000 / 0.3126 | not in ledger | re-read OK | — |

## 6. Must not claim
- That the sweep is a dose-response or causal test of the boundary mass (D6; r ≈ 0.98 mostly checks accuracy).
- That "the N-0 gate makes the concentration": the spike sits at the acceptance value, but the author's
  pre-registered test (`E1b.md`) found the concentration among non-violations survives removing the gate
  (68.90% → 65.59%). Coincidence of location is not cause.
- **Open causal question (state it as open):** the generator-setpoint floor at 0.94 (`P-007.md`) is active in both
  builds and untested; the test is an N3-class rebuild (floor 0.94 vs 0.95), an author decision.
- That 0.94 is "conservative".
- That a higher limit is cheaper to screen (low escalation at 0.95 = almost everything flagged).
- Anything about emergency vs normal limits without a verified citation.

## 7. Consistency
- `Top5-1.md` (causal wording); `E1b.md`; P-014 (the "floor" never has a number) — the figure is where a reader
  looks for it.
- Every other "boundary mass" use must match the strip definition; the figure's panel is a different window.
- Table II / Fig. 2 values at L = 0.94 are the same numbers (cross-check abs diff 0.0).

## 8. Page cost and dependencies
- +0.6 pp (figure 0.45 + two sentences 0.15; the Discussion replacement is roughly neutral).
- Depends on: d-figs (figure exists; relabel optional), owner committing `data/sts_limit_sweep.*` and
  `scripts/sts_limit_sweep.py` (currently untracked). Independent of N2 except that violation shares are label rates.

## 9. Voice note
- Say what L is (the voltage limit, re-applied after the fact to the same predictions) before showing it moving.
