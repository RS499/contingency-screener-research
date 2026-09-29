# Top5-2d-E5: the headline operating point — options (author decides; this file does not choose)

Fix specification only; the author writes every word (R04/R22/R27).

> **Depends on the author's N2b decision (P-032; ledger §1g): rebuild labels with PV/PQ switch-back and re-run the M2 pipeline, OR keep pandapower labels and state the N2 audit as a limitation.** It governs all three options' numbers. Branch (i) rebuild: every option (A test-picked, B held-out, C N1) must be re-run on rebuilt labels; the values in §5 are then superseded. Branch (ii) limitation: the options are presented on stored labels, and the chosen option's corrected-label missed rate (A: histgb 0.46%, ridge 1.14%) must be given with it. The option choice and the N2b choice should be made together, since under corrected labels option A's ridge point fails on 3 of 5 splits.

## 1. Ledger ID(s) and severity
- **Top-5 #2(d)** (review ST-F2; STATS-01), **E5** (held-out headline; E5a rows, E5c sentences), N1 (option C).
  **MAJOR** (prior review: FATAL). Author decision (ledger §5). Linked: C13, C2 (`E4.md`), P-005, P-013.

## 2. Anchors
| # | First words (verbatim) | Line |
|---|---|---|
| a | "For the gradient-boosted model, first going just under" (abstract) | 81 |
| b | "The ridge model shows a similar pattern as well," | 231 |
| c | Table II body rows "ridge  & 0.94" / "histgb & 0.97" (and caption "Safety and throughput at each coverage target") | 241–260 |
| d | "The mean missed rate first falls just under" (Fig. 2 caption) | 281 |
| e | "An operator that requires a missed rate around" | 349 |
| f | "To make sure that the missed ratio approaches" (conclusion) | 388 |
| g | "I kept whichever variable values skipped the most" (Method, the inner rule) | 124 |

## 3. Old text (verbatim)
- (a) "For the gradient-boosted model, first going just under a 1\% mean missed rate at a 0.97 coverage target results in a 63.7\% escalation and speedup dropping to roughly 1.58, with error bars going slightly above 1\%."
- (b) "The ridge model shows a similar pattern as well, with the average of missed cases falling below 1\% at 0.94 for the ridge model (0.79\% missed, 64.3\% escalation, 1.56 times faster) and 0.97 for the gradient-boosted model (0.83\% missed, 63.7\% escalation, 1.58 times faster), although the error bars still reach up to about 1.0--1.07\%, as Fig.~\ref{fig:tradeoff} shows."
- (c) "\caption{Safety and throughput at each coverage target on IEEE 118-bus system. Means $\pm$ standard deviation over five random splits. Escalation, empirical coverage, and missed-violation rate (share of true violations) in percent; histgb is the gradient-boosted model.}"
- (d) "The mean missed rate first falls just under 1\% at 0.94 coverage for ridge and 0.97 for the gradient-boosted model, with high escalation at both and the error bars still reaching slightly above 1\%."
- (e) "An operator that requires a missed rate around 1\% (with error bars still touching the 1\% threshold) would run the models at a 0.94 or a 0.97 target coverage and accept about a 1.6 times speedup instead of the 2 to 3.3 times available at 0.90."
- (f) "To make sure that the missed ratio approaches 1\% on average, almost two-thirds of the cases have to be escalated, resulting in a speed-up factor of 1.6."
- (g) "I kept whichever variable values skipped the most solves while still missing 1\% or fewer of the violations, and I repeated the whole process with five different random splits."

## 4. What must change — per option
The defect common to all options: 0.94 (ridge) and 0.97 (histgb) are the first targets whose **test-set** mean
missed rate drops below 1%. The reader is never told that the operating point was read off the test sweep.

**Option A — keep the test-picked points (0.94 / 0.97), disclose.**
- State at (b) that the targets were chosen by reading the test-split sweep (so the missed rate at that point is
  optimistic), and give the per-split exceedance count (`C13.md`).
- Variant A′ (all-splits rule, still test-picked): the first target at which every one of the five test splits is
  below 1% is ridge 0.95 / histgb 0.98. Only use it if the same rule is used for case30 (`E4.md`, C2).
- Minimal text change; weakest statistically.

**Option B — held-out (inner-split) choice.**
- Method (g) already describes an inner split drawn from training data. Option B reuses it: for each split, the target
  is the one the inner split chose (the first target whose inner missed rate is ≤ 1%, with the M2-selected model);
  the test split is only scored.
- Add two Table II rows labelled as held-out choices (ridge, histgb) and one or two sentences: the held-out histgb
  choice misses 1.15 ± 0.27% with 4 of 5 splits above 1%; the held-out ridge choice misses 0.77 ± 0.78% (one split at
  2.24%).
- Consequence: the "just under 1%" headline does not survive for histgb; the escalation/speedup trade-off does.

**Option C — violation-conditional calibration (N1).**
- Replace the per-target scan by a calibration whose nominal guarantee is on the missed rate itself: the certify
  threshold is set from calibration *violations* only, so that at most δ = 1% of them would be certified.
- One paragraph + one table row, no new notation (D15). Cite a verified source for class-conditional / Mondrian
  conformal before using it (`vovk2003mondrian` is "verified, NOT inserted", prior-art §9.6).
- **N1 landed** (`data/sts_n1_class_conditional.json` + manifest; script `scripts/sts_n1_class_conditional.py`,
  untracked until committed). It evaluates four forms; the one matching the STATS check is `threshold_rows`
  (certify iff prediction exceeds the calibrated threshold τ, where τ is set from calibration violation rows). What
  the artifact itself says must shape the text:
  - **it does not move the frontier**: every form lies on the same (missed, escalation) curve as the global gate
    and only selects a threshold (`matched_missed_note`; paired escalation difference vs global at matched missed
    −0.1 ± 0.1 pts ridge, −0.1 ± 0.4 pts histgb) — so C is a *selection rule with a stated target*, not a better
    gate;
  - the row-pooled forms do **not** carry a finite-sample guarantee (rows within a base case are not exchangeable;
    at α = 0.10 histgb threshold_rows misses 10.2% with only 2/5 splits ≤ α). Only the one-row-per-base-case forms
    (`threshold_groups`) carry the marginal guarantee, and only for one randomly chosen violation row of a new base
    case that has a violation; its matching metric is the group-weighted missed rate;
  - the "band" forms (τ applied to the overshoot) certify almost nothing (ridge escalation 74.9% = saturation,
    certify-only speedup 1.00×); do not present them as an operating point.
  If C is chosen, the text must name the form, the guarantee's unit (base case), and that it lands on the same
  frontier.

**All options** must change (a), (b), (d), (e), (f) in step, and P-013 applies to all: the 1% target is the
operator's chosen parameter (no verified source for a 1% criterion in `notes/prior-art.md`).

## 5. Numbers
| Option | Value as it would be printed | Source → key / command | Ledger status | Re-read |
|---|---|---|---|---|
| A ridge@0.94 | missed 0.79 ± 0.21%, esc 64.3 ± 2.8%, cov 94.0 ± 0.7%, 1.56 ± 0.07×; splits > 1%: 1 of 5 (1.146) | `data/tradeoff_curve_v2.json` → `records[ridge, 0.94]`; per-split `data/tuned_metrics.json` → `records[metric=m2, family=ridge].sweep[0.94].missed_viol` | Reported / VERIFIED (teammate) | re-read OK (per split 0.601, 0.624, 1.146, 0.918, 0.678) |
| A histgb@0.97 | missed 0.83 ± 0.24%, esc 63.7 ± 5.1%, cov 97.0 ± 0.2%, 1.58 ± 0.12×; 2 of 5 (1.162, 1.032) | same, histgb 0.97 | Reported / VERIFIED (teammate) | re-read OK (1.162, 0.798, 1.032, 0.699, 0.470) |
| A′ ridge@0.95 | 0.45 ± 0.12%, 67.9 ± 2.8%, 1.48 ± 0.06×; 0 of 5 | same keys | C2 (ledger) | re-read OK |
| A′ histgb@0.98 | 0.30 ± 0.13%, 72.0 ± 3.7%, 1.39 ± 0.07×; 0 of 5 | same keys | C2 (ledger) | re-read OK |
| B histgb | targets [0.96, 0.97, 0.97, 0.96, 0.96]; missed **1.15 ± 0.27%** (1.61, 0.80, 1.03, 1.05, 1.23; 4 of 5 > 1%); esc 59.3 ± 4.0%; 1.69 ± 0.12×; cov 96.2 ± 0.6% | `data/tuning_search.json` → `selections[seed].histgb.m2` → `records[tag].inner_cov_at` × `data/tuned_metrics.json` sweep; `scratch/confirm_missing.py`, `tmp/panel_stats/heldout_op.py` | VERIFIED (teammate STATS; plan E5) | re-read OK (both scripts re-run) |
| B ridge | targets [0.97, 0.94, 0.96, 0.92, 0.94]; missed 0.77 ± 0.78% (0.02, 0.62, 0.27, 2.24, 0.68; 1 of 5); esc 65.4 ± 8.1%; 1.55 ± 0.22×; cov 94.1 ± 2.5% | same | VERIFIED (teammate) | re-read OK |
| C histgb, threshold_rows, α = 0.01 | missed 0.98 ± 0.26% (1.41, 0.83, 0.69, 0.86, 1.14; 2 of 5 > 1%), esc 61.2 ± 3.3%, speedup 1.63 ± 0.09×, certify-only 1.27 ± 0.05× | `data/sts_n1_class_conditional.json` → `summary.histgb.threshold_rows["0.01"]` | new (N1); matches STATS check | re-read OK (also re-ran `tmp/panel_stats/analyze.py`) |
| C ridge, threshold_rows, α = 0.01 | missed 1.07 ± 0.28% (1.46, 0.95, 1.20, 1.12, 0.62; 3 of 5 > 1%), esc 61.7 ± 1.7%, 1.62 ± 0.04×, certify-only 1.15 ± 0.03× | → `summary.ridge.threshold_rows["0.01"]` | new (N1) | re-read OK |
| C histgb, threshold_groups (guarantee-carrying), α = 0.01 | missed 0.84 ± 0.46% (1.50, 0.98, 0.17, 0.50, 1.06), group-weighted 0.88 ± 0.45%, esc 64.6 ± 5.1%, 1.55 ± 0.12× | → `summary.histgb.threshold_groups["0.01"]` | new (N1) | re-read OK |
| C ridge, threshold_groups, α = 0.01 | missed 0.75 ± 0.46% (0.37, 1.21, 1.21, 0.92, 0.07), group-weighted 0.81 ± 0.50%, esc 65.1 ± 5.2%, 1.54 ± 0.12× | → `summary.ridge.threshold_groups["0.01"]` | new (N1) | re-read OK |
| C row-pooled validity check: histgb threshold_rows α = 0.10 → missed 10.18 ± 0.74%, 2/5 splits ≤ α | → `summary.histgb.threshold_rows["0.1"]` | new (N1) | re-read OK | — |
| **All options on corrected labels (N2, no retrain):** A histgb@0.97 0.46 ± 0.08% (0/5 > 1%); A ridge@0.94 1.14 ± 0.57% (3/5 > 1%) | `data/sts_n2_label_audit.json` → `missed_cases` | new (N2) | re-read OK | histgb change passes (0.37 > 0.24); ridge change fails (0.35 < 0.57) |

**Std-rule checks (larger seed std, ddof = 0, 5 splits):**
- B vs A, histgb missed: 1.15 vs 0.83, gap 0.32 > 0.27 → **passes**: held-out choice misses more.
- B vs A, histgb escalation: 59.3 vs 63.7, gap 4.4 < 5.1 → fails (no difference).
- B vs A, ridge missed: 0.77 vs 0.79 → fails (no difference; B's std 0.78 is larger than its mean).
- C vs A, histgb missed 0.98 vs 0.83 (gap 0.15 < 0.26) and escalation 61.2 vs 63.7 (2.5 < 5.1) → no difference.
- C vs A, ridge missed 1.07 vs 0.79: gap 0.28, larger std 0.28 → does not exceed → fails; escalation 61.7 vs 64.3
  (2.6 < 2.8) → fails.
- Mean vs the 1% line: only A′ is resolved below 1% (0.45 ± 0.12, 0.30 ± 0.13). A (0.79 ± 0.21, 0.83 ± 0.24),
  B (0.77 ± 0.78; histgb 1.15 ± 0.27 is not resolved *above* 1% either) and C (0.98 ± 0.26, 1.07 ± 0.28) are all
  within one seed std of 1%.

## 6. Must not claim
- "Below 1%" as a resolved property of any option (see the std checks).
- That the 1% target comes from a standard (P-013).
- For C: a guarantee on the per-base-case missed rate, or a guarantee under N-2 shift; the nominal guarantee is
  marginal over calibration violations (and, for the row-pooled forms, not even that — see above). Print C numbers
  only from the N1 artifact, after the owner commits it.
- That any option's missed rate is label-independent: under N2's corrected labels the A points change (histgb
  better, ridge 3/5 splits above 1%); whichever option is chosen, report its value on both label sets or state that
  only stored labels were used (`P-003.md`).
- That option B "confirms" option A: for histgb it contradicts the sub-1% reading.

## 7. Consistency
- Abstract (a); IV-A (b) and Table II (c); Fig. 2 caption (d); IV-C (e); conclusion (f); Method (g) for option B.
- `E4.md` (C2): whatever rule is chosen here must also pick case30's point (mean rule → histgb 0.96; all-splits →
  0.97).
- `C13.md` per-split counts; `P-005.md` error-bar wording; `E8.md` certify-only speedups at the chosen point;
  `E9.md` miss depth at the chosen point; `E11.md` break-even at the chosen point (break-even keys exist only for
  ridge 0.94 / histgb 0.97); `E12-E13.md` base-case statistic (any-miss keys exist at 0.90, 0.94 and 0.97 for both models; option B's per-split targets would need a recompute).

## 8. Page cost and dependencies
- A: +0.07 pp (one disclosure sentence). A′: +0.07. B: +0.21 (two table rows + two sentences). C: ≈ +0.17–0.2 (one
  paragraph, one row, one citation).
- Depends on: author decision (ledger §5); C additionally on committing the N1 artifact/script and a verified
  bibitem; all options on the P-003 label disclosure (N2).
- Blocks: C13, E4 (C2), E8/E9/E11 wording at "the operating point".

## 9. Voice note
- Whichever option: say in one clause, before the number, *which data* chose the operating point.
