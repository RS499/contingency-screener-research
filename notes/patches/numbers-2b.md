# numbers-2b — §2b mismatches, §2c sources, P-008, E2c, OS-5/OS-8/OS-9, typo "locked tes"

Fix specification only. No replacement wording. Every value below was re-read by this spec writer
on 2026-09-27 with `.venv/bin/python` from the named key. "Computed (spec)" = recomputed here from a
committed input, no stored key exists; such a value must get a key (d-figs/d-runs, new file) before
it is printed. std rule = a gap is real only if it exceeds the larger of the two stds.

Line numbers refer to `report/paper_current_STS.tex` as of 2026-09-27 (460 lines).

---

## 2b-1 / OS-9 — error-bar upper ends "1.0–1.07%"

1. **Ledger IDs:** 2b-1, OS-9. MINOR.
2. **Anchor:** "although the error bars still reach up to" — l.231.
3. **Old text (verbatim):** `although the error bars still reach up to about 1.0--1.07\%, as Fig.~\ref{fig:tradeoff} shows.`
4. **What must change:**
   - The two upper ends are (ridge @0.94 mean + 1 std) and (histgb @0.97 mean + 1 std). At the
     two-decimal precision the rest of the range uses, they are 1.00 and 1.08, not "1.0" and "1.07".
     The upper value is a rounding error (1.0769 rounds to 1.08); the lower one is a precision
     mismatch only.
   - "as Fig. 2 shows" is false until Fig. 2 draws the spread (P-005; `data/sts_tradeoff_bands.png`
     now exists, owner d-figs). Either swap the figure or stop pointing to it for the spread.
   - The spread is ±1 population std over 5 re-splits (P-023), not a confidence interval; the
     passage must not read as a CI.
5. **Numbers:**

   | Printed | Correct | Source → key | Status |
   |---|---|---|---|
   | 1.0 | 1.00 (0.7935 + 0.2090 = 1.0025) | `data/tradeoff_curve_v2.json` → `records[model=ridge, coverage_target=0.94].missed_viol` + `.missed_viol_std` (0.007935, 0.002090) | re-read OK (precision) |
   | 1.07 | **1.08** (0.8322 + 0.2447 = 1.0769) | same file → `records[model=histgb, coverage_target=0.97].missed_viol` + `.missed_viol_std` (0.008322, 0.002447) | **MISMATCH** (rounding) |

   std convention: `data/tradeoff_curve_v2.json` → `std_convention` = "population std (ddof=0) over
   five held-out splits" — re-read OK.
6. **Must not claim:** that either model is "below 1%" (both means fail the std rule against 1%:
   ridge gap 0.21 vs std 0.21; histgb gap 0.17 vs std 0.24 — `notes/number_check.md` §3, re-derived
   here from the same keys); that the band is a confidence interval.
7. **Consistency (same fact elsewhere):** l.81 abstract ("error bars going slightly above 1\%");
   l.281 Fig. 2 caption ("error bars still reaching slightly above 1\%"); l.349 ("with error bars
   still touching the 1\% threshold"). All three are qualitatively consistent with 1.00/1.08 and need
   no number change, but all three depend on the headline-operating-point author-decision
   (Top-5 #2(d), E5, C13): if the headline moves to the held-out histgb point, every one of these
   and 2b-1 is superseded, not patched.
8. **Page cost:** 0. **Depends on:** P-005 (figure), Top-5 #2(d)/E5 (headline decision), P-023.

---

## 2b-2 — clip-era boundary share "55.5"

1. **Ledger ID:** 2b-2. MINOR.
2. **Anchor:** "but the number of rows in the narrow" — l.121.
3. **Old text (verbatim):** `but the number of rows in the narrow band [0.94, 0.945) stayed about the same, moving from 55.5\% to 56.86\%.`
4. **What must change:** print the before value at the same precision as the after value (two
   decimals), so the comparison is like-for-like. The source is gitignored (P-031): the table in
   P-011 must say the clip-era parquet is not in git, so 55.51 and 35.17 are reproducible only from
   the archived copy.
5. **Numbers:**

   | Printed | Correct | Source → key | Status |
   |---|---|---|---|
   | 55.5 | **55.51** | `data/clip_artifact.json` → `clip_era.boundary_0p94_to_0p945_pct` (also `cited_in_sts.boundary_before_fix_pct`) | MISMATCH (precision) |
   | 56.86 | 56.86 | same file → `fixed_v2.boundary_0p94_to_0p945_pct` | re-read OK |
   | 35.17 (same line) | 35.17 | same file → `clip_era.clip_atom_share_pct` | re-read OK |

   Input of the clip-era values: `data/archive_clip/dataset.parquet` (`clip_era.source`), sha256
   `7efabd3f…` — gitignored.
6. **Must not claim:** "stayed about the same" as evidence that the strip is a network property
   (Top-5 #1 / C7 / P-007 — the same sentence's causal reading is revised there). No std exists for
   either value (single dataset), so no difference claim beyond "about the same".
7. **Consistency:** none elsewhere in the .tex (55.5 appears only at l.121).
8. **Page cost:** 0. **Depends on:** C7/E1a rewrite of the next sentence (same paragraph); P-011/P-031.

---

## 2b-3 / OS-8 — Fig. 4 caption "56.9"

1. **Ledger IDs:** 2b-3, OS-8. MINOR.
2. **Anchor:** "The shaded strip spans [0.94, 0.945) and" — l.323 (Fig. 4 caption).
3. **Old text (verbatim):** `The shaded strip spans [0.94, 0.945) and holds 56.9\% of all cases, yet the tallest 0.001 pu bin within it holds only 14.1\%.`
4. **What must change:** the caption prints the same quantity as l.81, l.314, l.365 at a different
   precision; use one precision everywhere (two decimals is what every other occurrence uses).
5. **Numbers:**

   | Printed | Correct | Source → key | Status |
   |---|---|---|---|
   | 56.9 | **56.86** | `data/frozen_poster_numbers_v2.json` → `dataset_facts.boundary_0p94_to_0p945_pct` (56.86); unrounded `data/sts_dataset_facts.json` → `boundary_strip.share_of_converged_n1_pct` (56.8629) | MISMATCH (precision) |
   | 14.1 | 14.06 or 14.1 (either, but match l.314 — see P-008) | `data/sts_dataset_facts_b.json` → `tallest_0p001_bin.figure_binning.share_pct` (14.0628) | re-read OK |

6. **Must not claim:** nothing new; the "yet … only 14.1%" clause's purpose (rules out a single
   spike, i.e. the old clip atom) is unstated — NS-21; that is a P-027/NS-21 item, not this one.
7. **Consistency:** 56.86 at l.81, l.121, l.314, l.365 — already two decimals; leave them.
8. **Page cost:** 0. **Depends on:** none.

---

## 2b-4 — critical-bus shares "27.1 / 16.81 / 9.31"

1. **Ledger ID:** 2b-4. MINOR.
2. **Anchors:** "Certain buses account for extreme events, with" — l.314; "The three dominant buses are 76, 53," — l.339 (Fig. 5 caption).
3. **Old text (verbatim):**
   - l.314: `with bus 76 being the weakest node, showing the minimum voltage in 27.1\% of contingencies, while bus 53 is second at 16.81\% and bus 107 is third at 9.31\%`
   - l.339: `(see main text for their shares: 27.1\%, 16.81\%, and 9.31\%)`
4. **What must change:** mixed precision in one list (1 dp next to 2 dp). The frozen key stores
   27.1 only because 27.10 loses its trailing zero as a float; the unrounded value is 27.0961, so the
   two-decimal print is 27.10. Bus names are IEEE 1-based (76/53/107 = index 75/52/106) — correct
   in prose; the Overleaf figure copy is stale 0-based (P-004, separate).
5. **Numbers:**

   | Printed | Correct | Source → key | Status |
   |---|---|---|---|
   | 27.1 | **27.10** | `data/frozen_poster_numbers_v2.json` → `dataset_facts.critical_bus_top5[0].share_pct` (27.1, bus 75); unrounded `data/critical_bus_map.manifest.json` → `rendered_numbers.top5_labelled_buses[0].share_pct` (27.0961) and `data/classical_screen_metrics.json` → `qlimit_analysis.per_bus.75.share_of_all` (0.270961) | MISMATCH (precision) |
   | 16.81 | 16.81 | `…_v2.json` → `dataset_facts.critical_bus_top5[1].share_pct` (bus 52) | re-read OK |
   | 9.31 | 9.31 | `…_v2.json` → `dataset_facts.critical_bus_top5[2].share_pct` (bus 106) | re-read OK |
   | (not printed) | 8.45, 4.12 (IEEE 1, IEEE 21) | same key `[3]`, `[4]` | re-read OK — relevant only if the caption mentions the other labelled buses (P-004, d-figs flag 4) |

6. **Must not claim:** that bus 76's share is a network property (31.6% of strip rows sit at IEEE 76
   holding its own sampled setpoint — P-007, `data/sts_dataset_facts.json` →
   `boundary_strip.share_at_bus_index_75_pct` 31.616, re-read OK).
7. **Consistency:** l.314 and l.339 must change together. If Fig. 5 is cut (Cut-2), l.339 goes and
   the "as shown in Fig. 5" clause at l.314 goes with it.
8. **Page cost:** 0. **Depends on:** Cut-2 (Fig. 5 author-decision), P-004.

---

## 2b-5 / OS-5 — "ceiling lands just above the saturation point"

1. **Ledger IDs:** 2b-5, OS-5. MINOR (std-rule violation).
2. **Anchor:** "The gradient-boosted model flags violations about as often" — l.347.
3. **Old text (verbatim):** `The gradient-boosted model flags violations about as often as they occur, so its ceiling lands just above the saturation point.`
4. **What must change:** the direction word "above" states a difference the std rule does not
   support; the supported statement is that the histgb ceiling and the saturation value are
   indistinguishable. The ridge-vs-histgb ceiling comparison earlier in the same paragraph passes
   and stays.
5. **Numbers:**

   | Quantity | Value (mean ± pop. std, 5 splits) | Source → key | Status |
   |---|---|---|---|
   | histgb ceiling | 82.79 ± 0.37 | mean: `data/frozen_poster_numbers_v2.json` → `ceilings.escalation_at_max_band_width_approaches_P_pred_ge_0.94.histgb` (0.827948); std: computed (spec) as pop. std of 1 − `p_pred_below_limit` over `data/tuned_metrics.json` `records[family=histgb, metric=m2]` → 0.369 pp | re-read OK (mean); std computed (spec), matches `notes/number_check.md` §3 |
   | saturation (perfect model) | 82.64 ± 0.17 | mean: `…_v2.json` → `ceilings.perfect_model_floor_saturation` (0.826352); std: computed (spec) from per-seed test share of min_vm ≥ 0.94 via `feasibility/make_splits.py` seeds 0-4 → 82.418/82.485/82.634/82.818/82.822, std 0.166 pp | re-read OK (mean); std computed (spec) |
   | ridge ceiling | 74.89 ± 0.83 | `…_v2.json` → `ceilings…ridge` (0.748876); std computed (spec) 0.831 pp | re-read OK |

   std-rule check: histgb ceiling − saturation = 0.16 pp < larger std 0.37 → **FAILS** ("above" not
   supported). ridge vs histgb ceiling gap 7.9 pp > 0.83 → passes.
   Neither ceiling std is stored in a key; if the author prints a ± here, d-runs must add the key
   first (new file).
6. **Must not claim:** "above", "below", or any ordering of the histgb ceiling vs saturation.
   **Checker trap:** `scripts/check_paper.py` `PHRASE_REGEXES` bans the literal `lands on the
   saturation` (see `checker-phrases.md`); the fix must carry the "no difference" content without
   that phrase or the checker fails. Also do not call 82.64 a "floor" in prose: the key name
   `perfect_model_floor_saturation` is a legacy name for what the text calls the saturation point
   (C12/P-014 define the floor separately).
7. **Consistency:** l.347 only. The "saturation" name collision (`scripts/case30_gate.py`
   `saturation_point` = 82.52 vs the frozen 82.64; `notes/ai-prompt-log.md` l.4609) does not reach
   the STS .tex (82.52 absent — grep), so no change elsewhere.
8. **Page cost:** 0. **Depends on:** C12/P-014 (floor/ceiling/saturation vocabulary); Cut-4
   keeps this sentence (D5).

---

## 2b-6 — surrogate time histgb 0.00241 vs re-measure 0.00346 (optional)

1. **Ledger ID:** 2b-6. MINOR, optional.
2. **Anchor:** "is the surrogate time ($0.00116\pm0.00012$ ms" — l.147.
3. **Old text (verbatim):** `$t_{\text{surr}}$ is the surrogate time ($0.00116\pm0.00012$ ms for ridge and $0.00241\pm0.00062$ ms for histgb per case, timed as one batch prediction divided by the number of cases)`
4. **What must change:** nothing is wrong; the printed values match the committed timing. Optional:
   one footnote that a later re-measurement of histgb inference gave a larger per-case time and that
   the effect on net speedup is negligible (surrogate time is ~4×10⁻⁴ of a solve).
5. **Numbers:**

   | Quantity | Value | Source → key | Status |
   |---|---|---|---|
   | ridge t_surr | 0.00116 ± 0.00012 ms | `data/tuned_metrics.json` → `records[family=ridge, metric=m2].ms_surrogate` mean 0.0011628, pop. std 0.0001216; also `data/break_even.json` → `timing.ms_infer_committed.ridge` | re-read OK |
   | histgb t_surr | 0.00241 ± 0.00062 ms | same → histgb mean 0.0024111, std 0.0006163; `timing.ms_infer_committed.histgb` | re-read OK |
   | histgb re-measure | 0.00346 ms | `data/break_even.json` → `timing.ms_infer_measured_now.histgb` (0.0034565) | re-read OK |
   | ridge re-measure | 0.00115 ms | `…ms_infer_measured_now.ridge` (0.0011463) | re-read OK |
   | t_solve | 9.14 ms | `data/break_even.json` → `timing.ms_solver` (also `data/tradeoff_curve_v2.json` → `ms_solver`) | re-read OK |

   Comparison: histgb re-measure (0.00346) exceeds committed mean + 1 std (0.00303) — a real
   difference in timing, but speedup impact at histgb@0.97 is 1.5697 → 1.5694 (computed (spec) from
   1/(t_surr/t_solve + escalation 0.63679)); below every printed precision.
6. **Must not claim:** that inference time is stable across runs; that the re-measure changes any
   speedup.
7. **Consistency:** none (speedups printed to 2 decimals are unaffected). P-029 (base-solve cost,
   N6 warm-start timing) is a separate clause in the same sentence; coordinate if both are added.
8. **Page cost:** 0 (or +0.03 with footnote). **Depends on:** P-029/N6 if combined.

---

## 2c-1..4 — dataset numbers at l.119 now sourced

1. **Ledger IDs:** 2c-1 … 2c-4. MINOR (sourcing, not value).
2. **Anchor:** "I determined the load levels by scaling the" — l.119; Fig. 4 caption l.323.
3. **Old text (tokens, verbatim):** `(750 bases)` ×2; `from 0.9009 to 1.2310 (43.91\% outside the 1.0 to 1.12 target range)`; `from 0.8156 to 1.4083`; l.323 `below which 0.5\% of cases fall`.
4. **What must change:** no value changes. The values now have a key, but the key file is
   **untracked** (`git ls-files` returns nothing for `data/sts_dataset_facts.json`); the owner must
   commit `data/sts_dataset_facts.{json,manifest.json}` and `scripts/sts_dataset_facts.py` before the
   paper can claim these trace to committed code (CLAUDE.md §9). If Cut-6 moves these into the P-011
   table, carry the same values and precision.
5. **Numbers:**

   | Printed | Source → key (`data/sts_dataset_facts.json`) | Value | Status |
   |---|---|---|---|
   | 750 (Independent) | `base_cases_per_sampling_mode.independent` | 750 | re-read OK |
   | 750 (Regional) | `base_cases_per_sampling_mode.regional` | 750 | re-read OK |
   | 0.9009 | `load_multipliers.regional_p_mult_min` | 0.900858 | re-read OK |
   | 1.2310 | `load_multipliers.regional_p_mult_max` | 1.230963 | re-read OK |
   | 43.91 | `load_multipliers.regional_p_mult_share_outside_pct` | 43.9057 | re-read OK |
   | 1.0 to 1.12 (Independent window) | `independent_p_mult_min/max` | 1.000004 / 1.120000 | re-read OK |
   | 0.8156 | `load_multipliers.q_mult_min_all_bases` | 0.815637 | re-read OK |
   | 1.4083 | `load_multipliers.q_mult_max_all_bases` | 1.408329 | re-read OK |
   | 0.5 (below 0.87 pu) | `below_0p87.share_pct` | 0.5413 (1,510 rows) | re-read OK (0.54 if two decimals wanted) |

6. **Must not claim:** that these are byte-reproducible from git until the owner commits the files.
7. **Consistency:** Cut-6 / P-011 (same values move to the table); the 43.91% share is a share of
   74,250 per-load multipliers (`regional_p_mult_n_values`), not of bases — the unit must be clear
   wherever it lands (NS-13 "target range").
8. **Page cost:** 0. **Depends on:** owner commit; Cut-6/P-011.

---

## P-008 — "most … within 0.005 pu" and "about 14%" bin

1. **Ledger ID:** P-008. MINOR.
2. **Anchors:** "Most of the contingencies lie within 0.005 per" — l.314; "there is not a single 0.001 per-unit bin" — l.314.
3. **Old text (verbatim):** `Most of the contingencies lie within 0.005 per unit of the boundary, resulting in a significant number of escalations.` … `there is not a single 0.001 per-unit bin that accounts for more than about 14\% of the whole dataset.`
4. **What must change:**
   - "Most … within 0.005 pu" is true only as a **two-sided** window (61.61%); the one-sided strip
     the paper uses everywhere else is 56.86% (also a majority). The passage must say which window it
     means, or use the strip already defined (one quantity, one number — ties to C12).
   - "about 14%" (l.314) and "14.1%" (l.323) are the same key at two precisions; pick one.
   - The ledger said "no tracked key"; keys now exist in `data/sts_dataset_facts_b.json` — also
     **untracked**; owner commit needed.
5. **Numbers:**

   | Printed | Value | Source → key (`data/sts_dataset_facts_b.json`) | Status |
   |---|---|---|---|
   | "Most … within 0.005" (two-sided) | 61.61% (171,865 rows) | `within_0p005_of_limit.two_sided_open.share_pct` (61.6103) | re-read OK, untracked |
   | one-sided above | 56.86% | `within_0p005_of_limit.above_only.share_pct` (56.8629) | re-read OK |
   | one-sided below [0.935, 0.94) | 4.75% | `within_0p005_of_limit.below_only.share_pct` (4.7474) | re-read OK |
   | "about 14" / "14.1" | 14.06% (39,229 rows, bin [0.940, 0.941)) | `tallest_0p001_bin.figure_binning.share_pct` (14.0628) | re-read OK, untracked |

6. **Must not claim:** that "most" contingencies are escalated (escalation is 30.6–63.7% depending on
   the operating point; the strip is the population, not the escalated set).
7. **Consistency:** l.323 Fig. 4 caption (14.1 — see 2b-3); if Cut-3 rewrites l.314 the sentences
   survive only if the author keeps them.
8. **Page cost:** 0. **Depends on:** C12 (boundary-mass definition), Cut-3, owner commit.

---

## E2c — predictor B "slightly better on absolute error"

1. **Ledger ID:** E2c. MINOR (std-rule violation).
2. **Anchor:** "Since predictor B was not clearly more accurate" — l.353.
3. **Old text (verbatim):** `Since predictor B was not clearly more accurate than predictor A (worse on relative error yet slightly better on absolute error at 0.1056 versus 0.1163) under this locked tes,`
4. **What must change:**
   - "slightly better" asserts a difference that fails the std rule; the supported content is no
     difference on absolute error.
   - The two means hide the structure: A has the smaller absolute error in 42 of 54 comparisons; B's
     lower mean comes entirely from the case24 ridge cells (9 of 54), where A is worse in all 9.
     Excluding those cells, A's mean absolute error is about half of B's. This belongs with E2b
     (per-cell errors) and the E2a caption's named case24-ridge failure, not in this sentence alone.
5. **Numbers:**

   | Quantity | Value | Source → key | Status |
   |---|---|---|---|
   | A mean abs error | 0.1163 | `data/netstudy2/summary.json` → `cross_network.A_mean_abs_error` (0.116306) | re-read OK |
   | B mean abs error | 0.1056 | same → `cross_network.B_mean_abs_error` (0.105612) | re-read OK |
   | A mean rel error | 0.4726 | same → `cross_network.A_mean_rel_error` (0.472555) | re-read OK |
   | B mean rel error | 0.4933 | same → `cross_network.B_mean_rel_error` (0.493252) | re-read OK |
   | n comparisons | 54 | same → `cross_network.n` | re-read OK |
   | A abs error spread | pop. std 0.2097 over 54 | computed (spec) from `cross_comparisons[*].abs_err_A` | computed (spec), matches `notes/number_check.md` §3 |
   | B abs error spread | pop. std 0.1145 over 54 | computed (spec) from `cross_comparisons[*].abs_err_B` | computed (spec) |
   | A < B count | 42 / 54 | computed (spec) | computed (spec), no key |
   | case24 ridge cells | A 0.5194 vs B 0.2852 mean abs error, A worse 9/9 | computed (spec), grouping `network`,`family` | computed (spec), no key |
   | excl. case24 ridge (45 cells) | A 0.0357 vs B 0.0697 | computed (spec) | computed (spec), no key |

   std-rule check: gap 0.0107 < larger std 0.21 → **FAILS**; paired difference 0.0107 ± 0.113 also
   fails. Relative error gap 0.021 — no per-comparison spread printed; do not state an ordering there
   either without one.
   The computed (spec) values need a stored key (d-figs, new file) before any is printed.
6. **Must not claim:** that B is better on either metric; that A is "a law" (D-e; n = 3 target
   networks); any claim from the 42/54 count without saying the cells are not independent (9 targets
   per network-family share one network).
7. **Consistency:** l.353 only; E2a caption and E2b per-cell sentence (other patch) must carry the
   case24-ridge failure consistently with this.
8. **Page cost:** 0. **Depends on:** E2a/E2b (cross-network rewrite), NS-10 restructuring of IV-D.

---

## typo — "locked tes"

1. **Ledger ID:** typo "locked tes" (review §4c, NS-26, STS-09). MINOR.
2. **Anchor:** "under this locked tes, this indicates that" — l.353.
3. **Old text (verbatim):** `under this locked tes,`
4. **What must change:** truncated word (the intended word is the standard term for a pre-registered
   evaluation; the author supplies it). Grammar-only; the author makes the edit.
5. **Numbers:** none. `grep -n "locked tes"` → l.353 only — re-read OK.
6. **Must not claim:** n/a.
7. **Consistency:** l.355 "I locked and hashed the predictions" uses the same concept; keep one term.
8. **Page cost:** 0. **Depends on:** E2c (same sentence), NS-10 rewrite of the section.

---

## Summary for the index

| Item | Status | Net pp |
|---|---|---|
| 2b-1/OS-9 | MISMATCH 1.07→1.08 (rounding); 1.0→1.00 precision | 0 |
| 2b-2 | MISMATCH precision 55.5→55.51 | 0 |
| 2b-3/OS-8 | MISMATCH precision 56.9→56.86 | 0 |
| 2b-4 | MISMATCH precision 27.1→27.10 | 0 |
| 2b-5/OS-5 | std rule FAILS ("above") | 0 |
| 2b-6 | re-read OK; optional footnote | 0 / +0.03 |
| 2c-1..4 | re-read OK; keys untracked | 0 |
| P-008 | re-read OK; keys untracked; one-/two-sided ambiguity | 0 |
| E2c | std rule FAILS ("slightly better") | 0 |
| typo | present l.353 | 0 |
