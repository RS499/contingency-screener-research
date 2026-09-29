# Verification B — independent recomputation of the numbers in spec set B

Verifier: v-B (second key), 2026-09-27. Scope: every number/fact in the "Numbers" sections of the specs
named in `_index_B.md`; P-011 row by row; P-002/P-012 rules verbatim against `notes/sts-constraints.yaml`
and dated facts against `notes/ai-prompt-log.md` / `notes/contribution-log.md`. Spec reasoning and
status columns were not trusted. `.venv/bin/python` only; read-only everywhere except this file; no git
writes. Scratch scripts: `$CLAUDE_JOB_DIR/tmp/{tm,heldout,cond,n1,mond,c4,depth,pool,clse,ds,mult,splits}.py`.

**Primary alternative route.** Wherever possible values were recomputed from raw rows rather than read
from the cited key: (a) case118 gate metrics from per-seed `sweep` arrays in `data/tuned_metrics.json`
(not the aggregated `tradeoff_curve_v2.json` / frozen v2 the specs cite); (b) conditional-coverage,
any-miss, N1 threshold form, Mondrian, miss depth, ceilings, saturation, certify-only speedup from the raw
cal/test predictions in `data/sts_n1_predictions_long.parquet` with my own q̂ rule (k = ⌈(n+1)t⌉-th
overshoot) and gate; (c) dataset facts from `data/dataset.parquet`, `data/unconditioned_base.parquet`,
`data/case30_thermal/dataset.parquet`, `data/case30_dataset.parquet`, `data/archive_clip/dataset.parquet`
(gitignored, present locally, sha256 7efabd3f… matches `clip_artifact.json`); (d) N2 from
`data/sts_n2_label_audit.parquet`; (e) ρ·q̂ correlation from the tracked `data/netstudy2/cross_2a_points.json`.
Aggregation: ± = population std (ddof 0) over seeds 0-4. For the four headline missed rates both
seed-mean and count-pooled were computed; they agree at printed precision (histgb@0.90 4.717 / 4.715;
ridge@0.90 2.963 / 2.965; histgb@0.97 0.832 / 0.834; ridge@0.94 0.794 / 0.793).

UNTRACKED sources used (owner must commit before printing): `data/sts_e12_e13_conditional.json`,
`data/sts_n1_class_conditional.json`, `data/sts_crossnet_scatter.json`, `data/sts_n2_label_audit.{json,parquet}`,
`data/sts_dataset_facts.json`, `data/sts_dataset_facts_b.json`, `data/sts_n1_predictions_long.parquet`
(my raw route; it reproduces tracked `tuned_metrics.json` exactly). **Also: the whole `notes/` directory
is gitignored (`.gitignore:23 notes/`)** — prompt log, contribution log, sts-constraints.yaml, the
agent-drafted and retired drafts are not in git.

## Summary

| Verdict | Count |
|---|---|
| MATCH | 242 |
| MISMATCH | 3 (D11 disclosure "tracked"; M9 P-020 "only place certified"; P17-4 row count 84 ≠ 80) |
| ROUNDING | 0 (no spec value is mis-rounded; the tex's own 1.07 → 1.08 error is a numbers-2b finding, confirmed) |
| NOT FOUND | 3 (P10-9 cluster-SE multiplier, no artifact; P11-31 case118 build seed, correctly disclosed as unknown; L2 no printable P-028 number, by design) |
| STD-PASS | 14 |
| STD-FAIL | 8 (every one is a comparison the spec already forbids; no spec permits a claim that fails) |

**SIGNED OFF (15):** Top5-5, C1, C4, C6, C12, P-006, P-010, P-011, P-013, P-015, P-017, numbers-2b,
checker-phrases, cuts, P-028 — with the non-blocking corrections listed below
(checker-phrases, cuts and P-028 carry no printable result number).

**REJECTED (2):**
1. `P-002-P-012-disclosure.md` — A7 states the agent-drafted reference files are "(tracked…)". They are
   not: `git ls-files` returns nothing; `notes/` is gitignored (`.gitignore:23`). The same fact means the
   prompt log that A3 offers as the R22 logbook, `contribution-log.md`, the retired 2026-08-17 draft and
   `sts-constraints.yaml` are not version-controlled — material for a FATAL-severity disclosure checklist.
   Second file name is `notes/1_research_draft_ORIGINAL_rev2.txt`. All 20 quoted-rule rows and all other
   dated facts MATCH.
2. `minors_P-018_P-027.md` — P-020 §4 says histgb@0.90 is "the only place a non-converged case is
   certified". `data/nonconverged_gate.json` shows ridge@0.90 seed 1 (`certified_all45_by_seed`
   [0,1,0,0,0], in that seed's test split) and histgb@0.97 seed 3 ([0,0,0,1,0], in test) each certify one
   of the 45. Every other minors number MATCHES (one-line fix).

**Non-blocking corrections for signed-off specs**
- P-011 line anchors off (values correct): `generate_dataset.py:254` → **l.256** (N-0 reject test);
  `:170` → **l.168** (`genp_*`); `:201-203` → **l.197** (`nanmin`); `:314-316` → **l.316-318** (mode
  alternation). Manifest census today: 67 identical / 63 no-version / 1 partial / 4 sts (135), not
  66/58/1/4 — three manifests postdate the spec (`sts_miss_depth_noannot`, `sts_n4_f1_shuffle`,
  `sts_n6_warmstart_timing`); "no manifest records a different version" still holds. HistGB "max_depth
  none" is true for the 24 random draws, but the pinned `committed` candidate has max_depth 8.
  Selected-feature counts 701/700/700/700/701 hold only with the repo's float32 cast (a float64 std gives
  702/701/701/701/702).
- `_index_B.md` (not a spec): "the data contain a base at exactly 0.94" is wrong — the minimum N-0 minimum
  voltage is 0.940000036 pu (> 0.94); the key `committed_gated.n0_min_vm_min` = 0.94 is rounded. The
  prose "above 0.94" is true of the data; only the rule wording (code accepts ≥) differs.
- P-017: "80 term/symbol rows" — §4a-4d contain **84** data rows.
- P-010: cluster-SE multiplier has no artifact (NOT FOUND, as the spec itself says). Orientation recompute
  (300 base-case bootstrap resamples, seed 0): ridge 7.09 ± 0.95×, histgb 5.77 ± 0.68× — consistent with
  the panel's 7.0 ± 0.8 / 5.6 ± 0.8; still not printable.
- Consistency gaps (quantities printed in the .tex at lines the spec's §7 does not list): see the
  cross-occurrence table.

## Full table

Verdict = agreement at printed precision. "raw" = recomputed from raw rows (route above); "key" = read
from the cited key only (no second route available).

### Top5-5
| # | Value as printed | Source → key | My route | Recomputed | Verdict | Flag |
|---|---|---|---|---|---|---|
| T1 | histgb@0.90 esc 30.6 ± 2.5 | tradeoff_curve_v2 / frozen v2 four_metrics | tuned_metrics m2 sweeps; raw preds | 30.625 ± 2.510 | MATCH | |
| T2 | missed 4.72 ± 0.98 | same | same | 4.717 ± 0.977 (pooled 4.715) | MATCH | |
| T3 | speedup 3.29 ± 0.30 | same | sweeps | 3.287 ± 0.302 | MATCH | |
| T4 | histgb@0.97 missed 0.83 ± 0.24 | frozen v2 safety_operating_points.histgb[4] | sweeps; raw | 0.832 ± 0.245 (pooled 0.834) | MATCH | |
| T5 | esc 63.7 ± 5.1 | same | sweeps; raw | 63.679 ± 5.119 | MATCH | |
| T6 | speedup 1.58 ± 0.12 | same | sweeps | 1.579 ± 0.117 | MATCH | |
| T7 | 2/5 splits > 1% (1.162, 1.032) | sts_e12_e13 any_miss."0.97".missed_viol_rows | raw per seed | [1.162, 0.798, 1.032, 0.699, 0.470] | MATCH | UNTRACKED key |
| T8 | ridge@0.94 0.79 ± 0.21 / 64.3 ± 2.8 / 1.56 ± 0.07 | safety_operating_points.ridge[1] | sweeps; raw | 0.794 ± 0.209 / 64.341 ± 2.783 / 1.557 ± 0.068 | MATCH | |
| T9 | held-out histgb targets [0.96,0.97,0.97,0.96,0.96]; 1.15 ± 0.27 (1.61,0.80,1.03,1.05,1.23; 4/5); 59.3 ± 4.0; 1.69 ± 0.12 | tuning_search selections × inner_cov_at × tuned_metrics sweeps | own join | same targets; 1.145 ± 0.270, [1.611,0.798,1.032,1.054,1.231], 4/5; 59.269 ± 4.013; 1.694 ± 0.116 | MATCH | |
| T10 | held-out ridge [0.97,0.94,0.96,0.92,0.94]; 0.77 ± 0.78 (1/5: 2.24); 65.4 ± 8.1; 1.55 ± 0.22 | same | own join | same; 0.767 ± 0.776, 2.243; 65.431 ± 8.123; 1.555 ± 0.216 | MATCH | |
| T11 | certify-only 1.24× / 1.12× | sts_n1_class_conditional global_reference certify_only_speedup | key; raw 1/(1−certified) | key 1.238 / 1.119; raw 1.241 / 1.119 | MATCH | UNTRACKED |
| T12 | BM 56.86; viol 17.48 | unconditioned_base committed_gated | raw dataset.parquet | 56.8629 / 17.4756 | MATCH | |
| T13 | unconditioned BM 28.83; viol 56.04 | unconditioned_base unconditioned | raw unconditioned_base.parquet | 28.8328 / 56.0437 | MATCH | |
| T14 | case30 regen BM 7.09; viol 15.40 | case30_thermal_frozen | raw case30_thermal/dataset.parquet | 7.0862 / 15.3967 | MATCH | |
| T15 | case30 histgb@0.97 5.84 ± 1.25 / 0.76 ± 0.20 / 17.91 ± 3.71 | case30_thermal_frozen records | per-seed records | 5.836 ± 1.250 / 0.759 ± 0.201 / 17.914 ± 3.709 | MATCH | |
| T16 | r 0.8105 / log-log 0.9176, 132 pts; case24 ridge median 0.3408, 9/9 < 0.5 | sts_crossnet_scatter | recomputed from tracked netstudy2/cross_2a_points.json | 0.81048 / 0.91762, 132; 0.34077, 9 | MATCH | UNTRACKED key (tracked twin agrees) |
| T17 | static 99.41 ± 0.16 (k=138), 96.64 ± 0.50 (k=89) | baselines comparators.static_severity curve[k−1] | key; k from (esc+flag)·186 | 99.411 ± 0.155; 96.644 ± 0.497; k = 137.97 / 88.96 | MATCH | |
| T18 | gate 97.04 ± 0.44 / 95.28 ± 0.98 | baselines gate.*.capture_escalate_or_flag | key (spec had lead-VERIFIED only) | 97.037 ± 0.439 / 95.283 ± 0.977 | MATCH | |
| T19 | N2 4,615 / 48,749 (9.47%) flip; 2,162 reverse; corrected BM 56.22; worst 0.8485 → 0.94507 | sts_n2_label_audit violation_rate | raw audit parquet | 4,615 (flip column; naive stored∧¬corrected gives 4,616 — the 1 non-converged row keeps its stored label); 9.467; 2,162; 56.216; 0.848543 → 0.945073 | MATCH | UNTRACKED; audit-only |
| T20 | abstract 282 words | l.81 | wc -w | 282 | MATCH | |

### C1
| # | Value | Source → key | Route | Recomputed | Verdict | Flag |
|---|---|---|---|---|---|---|
| C1-1 | 54 = 3 × 2 × 9 (0.90-0.98) | netstudy2/summary cross_comparisons | count cells | 54; case24_ieee_rts, case39, case_illinois200; ridge/histgb; 9 targets | MATCH | |
| C1-2 | run_status networks case39, case24_ieee_rts, case89pegase, case_illinois200 | run_status.networks | key | same | MATCH | |
| C1-3 | case57 0 / 3,000 | case57_feasibility step1_n0 | key | accepted 0, attempts 3000 | MATCH | |
| C1-4 | prior sets (3 values) | cross_comparisons[].prior | set of values | "case118,case30_thermal" / "+case39" / "+case24_ieee_rts" | MATCH | |
| C1-5 | rel err A 0.4726 / B 0.4933; abs 0.1163 / 0.1056 | cross_network | mean over 54 cells | 0.47255 / 0.49325; 0.11631 / 0.10561 | MATCH | |

### C4
| # | Value | Source → key | Route | Recomputed | Verdict | Flag |
|---|---|---|---|---|---|---|
| C4-1 | histgb Cov 89.8 ± 1.0 | tradeoff_curve_v2 [histgb,0.90] | sweeps; raw | 89.818 ± 0.984 | MATCH | |
| C4-2 | histgb missed 4.72 ± 0.98 | same | same | 4.717 ± 0.977 | MATCH | |
| C4-3 | ridge Cov 89.3 ± 1.3 | [ridge,0.90] | sweeps; raw | 89.339 ± 1.327 | MATCH | |
| C4-4 | ridge missed 2.96 ± 0.44 | same | same | 2.963 ± 0.439 | MATCH | |
| C4-5 | frozen v2 cross-check 0.89339 / 0.029632 / 0.89818 / 0.047167 | four_metrics_at_90pct_coverage | key | same | MATCH | |
| C4-6 | violation share 17.48 | dataset_facts | raw | 17.4756 | MATCH | |
| C4-7 | bound 0.10 / 0.1748 ≈ 57.2% | derived | arithmetic | 57.208% | MATCH | |
| C4-8 | P(overshoot > q̂ \| viol) 0.388 / 0.411 | barrier_height summary_at_090 | raw preds | 0.38837 / 0.41150 | MATCH | |
| C4-9 | nine targets 0.90-0.98; 18 comparisons | case39/cross_2b_comparison | count | 18; 9 levels | MATCH | |
| C4-10 | 40 occurrences = S1 7 + S2 3 + S3 25 + 2 + 3 other (38 tex + 2 PNG) | grep | per-line hit count | per-line counts consistent with the 38 tex rows (43 word hits; multi-word rows explain the excess) | MATCH | sense labels not re-judged |
| C4-11 | `acceptance`/`risk--coverage` only at l.231 | grep | grep | l.231 only | MATCH | |

### C6
| # | Value | Source → key | Route | Recomputed | Verdict | Flag |
|---|---|---|---|---|---|---|
| C6-1 | 374 / 1,500 (24.93%) | sampling_audit prevalence | raw (gen_out ≥ 0; sentinel −1) | 374, 24.933 | MATCH | |
| C6-2 | 69,532 rows (24.93% of 278,955) | same | raw | 69,532, 24.926 | MATCH | |
| C6-3 | P_GEN_OUT 0.30 l.28; non-slack l.128-130 | generate_dataset.py | read code; case118 gen.slack sum | l.28, l.129; 0 gen with slack=True, 1 ext_grid | MATCH | |
| C6-4 | no redispatch l.142-144 | code | read | l.142-144 in_service only | MATCH | |
| C6-5 | genon_ features l.171 | code | read | l.171 | MATCH | |
| C6-6 | rejection by status not computable | acceptance_effect.interpretation_note | key | text present | MATCH | |
| C6-7 | medians 0.94305 / 0.94349 | acceptance_effect | raw | 0.943045 / 0.943486 | MATCH | |

### C12 (+P-014)
| # | Value | Source → key | Route | Recomputed | Verdict | Flag |
|---|---|---|---|---|---|---|
| C12-1 | BM 56.86 | unconditioned_base committed_gated | raw | 56.8629 | MATCH | |
| C12-2 | strip 0.005; ρ = BM / 0.005 | sts_crossnet_scatter | tracked cross_2a_points has same fields | 0.005; same definition | MATCH | UNTRACKED key |
| C12-3 | unconditioned BM 28.83 | unconditioned | raw | 28.8328 | MATCH | |
| C12-4 | case30 regen 7.09; published 20.01 | case30_thermal_frozen / case30_frozen | raw both parquets | 7.0862 / 20.0146 | MATCH | |
| C12-5 | q̂@0.90 0.0052 / 0.0023 | tradeoff_curve_v2 q_hat | sweeps; raw | 0.005198 / 0.002291 | MATCH | |
| C12-6 | esc@0.90 30.6 ± 2.5 / 49.1 ± 2.7 | four_metrics / sts_n1 global_reference | raw | 30.625 ± 2.510 / 49.070 ± 2.661 | MATCH | |
| C12-7 | saturation 82.64 ± 0.17 | ceilings.perfect_model_floor_saturation (mean) | raw per-seed test share y ≥ 0.94 | 82.635 ± 0.166 | MATCH | std has no key |
| C12-8 | ceilings 74.89 ± 0.83 / 82.79 ± 0.37 | ceilings…; tuned_frontier std | raw share pred ≥ 0.94 | 74.888 ± 0.831 / 82.795 ± 0.369 | MATCH | |
| C12-9 | F-a 63.7 ± 5.1 (0.83 ± 0.24); 64.3 ± 2.8 (0.79 ± 0.21) | sts_n1 global_reference | raw | as T4-T8 | MATCH | |
| C12-10 | F-b 59.3 ± 4.0 (1.15 ± 0.27, 4/5); 65.4 ± 8.1 (0.77 ± 0.78, 1/5) | recomputed join | own join | as T9-T10 | MATCH | |
| C12-11 | F-c 61.2 ± 3.3 @ 0.98 ± 0.26; 61.7 ± 1.7 @ 1.07 ± 0.28 | sts_n1 threshold_rows."0.01" | own threshold form on raw preds (τ = ⌈(n_v+1)0.99⌉-th cal-violation prediction) | 61.202 ± 3.328 @ 0.984 ± 0.256; 61.703 ± 1.723 @ 1.068 ± 0.279 | MATCH | UNTRACKED |
| C12-12 | Mondrian histgb@0.97 42.9 ± 1.9 / 1.45 ± 0.30; global@0.96 57.0 ± 4.3 / 1.36 ± 0.20 | mondrian_element_summary aggregate; safety_operating_points.histgb[3] | own per-element q̂ on raw preds; sweeps | 42.897 ± 1.914 / 1.453 ± 0.297; 56.955 ± 4.252 / 1.357 ± 0.198 | MATCH | |
| C12-13 | case30 5.84 ± 1.25 | records | per-seed | 5.836 ± 1.250 | MATCH | |
| C12-14 | second saturation 82.52 (= 100 − 17.48) | case30_frozen case118_comparators.saturation_point_pct | key + arithmetic | 82.52 | MATCH | |

### P-002 + P-012 disclosure
| # | Fact / quote | Source | Route | Found | Verdict |
|---|---|---|---|---|---|
| D1 | prompt log 6,155 lines | wc | wc -l | 6,155 | MATCH |
| D2 | first entry 2026-07-26 at l.13; entries to 2026-09-27 | `^## ` | grep | l.13 "Classical baseline (2026-07-26)"; last l.5961 2026-09-27 | MATCH |
| D3 | 33 `**Model:**` entries: 21 "(Claude Code)", 12 bare | grep tally | grep -o | 7+5+3+6 = 21; 12 | MATCH |
| D4 | categories research 18, experiment 5, citation-audit 3, manuscript-adjacent 5 | grep tally | grep -o | 18; 5; 2+1 ("+ numbers"); 4+1 (retired) | MATCH |
| D5 | URTC authors Saha + Pinsky, URTC tex l.48-58 | paper_current_URTC_20260808.tex | read | l.48-58 | MATCH |
| D6 | STS tex AI grep → l.101 + bib title only | grep | grep | l.101, l.452 | MATCH |
| D7 | STS tex "urtc" → l.3 comment only | grep | grep | l.3 | MATCH |
| D8 | .tex l.3-4 "Body text is VERBATIM from the URTC conference version" | tex | read | l.3-4 | MATCH |
| D9 | URTC Ack l.242: AI "validate the code and grammar", URL, "the authors" | URTC tex | read | l.242 as described | MATCH |
| D10 | 2026-07-21 agent-drafted 5-page reference; "Claude (Claude Code, Opus 4.8)" | contribution-log.md l.7, l.29 | read | present | MATCH |
| D11 | A7 files `notes/1_research_draft_ORIGINAL.txt`, `_rev2.txt` "(tracked…)" | git ls-files; .gitignore | git ls-files, check-ignore | NOT tracked; `.gitignore:23 notes/`; 2nd file is `…ORIGINAL_rev2.txt` | **MISMATCH** |
| D12 | 2026-08-17 retired AI draft, product/prompt NOT DETERMINED, l.2294-2318; quarantine path | prompt log | read | present; `notes/retired/2026-08-17_ai_draft_sections_RETIRED.md` exists | MATCH |
| D13 | 2026-08-15 citation resolution l.2202-2222 | prompt log | read | present | MATCH |
| D14 | 2026-09-04 paste / math conversion / build fixes l.4860, 4937, 4982, sha before/after | prompt log | read | headers at those lines; Pre/Post sha lines present | MATCH |
| D15 | 2026-09-13 "make the edits to the text", 278 → 276 lines, l.5521-5528 | prompt log | read | present | MATCH |
| D16 | Kalita co-author removal fact pattern l.1165-1171 | prompt log | read | present | MATCH |
| D17 | Pinsky writing STS recommendation l.5336-5341 | prompt log | read | quote at l.5343 (inside the 5336-5345 entry) | MATCH |
| D18 | URTC "accepted … not yet published" l.5543 | prompt log | read | l.5542-5543 | MATCH |
| D19 | 8cefaa7 "submitted 2026-08-08, CMT #74"; 8b88a99 camera-ready 2026-09-22 | git show (read-only) | git show | as stated (8cefaa7 committed 2026-08-18) | MATCH |
| D20 | `ai_usage_changelog.md` marks `scripts/sts_*.py` AI-written | file | grep | present | MATCH |
| D21 | hooks from 2026-08-18 | prompt log l.2294-2318 | read | stated there | MATCH |
| R-a | R22 code row "Use AI to write initial code … log of the prompts." | yaml R22 (and R04) | verbatim compare | identical | MATCH |
| R-b | R04 note "The code-portion condition is NOT MET" | yaml R04 note | compare | identical | MATCH |
| R-c | R22 "…and with a log of the prompts"; "Maintain a logbook … research notebook." | R22 | compare | identical | MATCH |
| R-d | R22 statistical-tests row (prefix quote) | R22 | compare | identical prefix | MATCH |
| R-e | R20 "full disclosure of any research or person … is required." | R20 | compare | identical | MATCH |
| R-f | R22 abstract-sharpen row "…Must be credited." | R22 | compare | identical | MATCH |
| R-g | R04/R22 "initially write … Never acceptable … Guidance or refinement … explicit citation and a log." | R22 | compare (ellipsis) | identical ends | MATCH |
| R-h | R22 "…This must be the independent work of the student." | R22 | compare | identical | MATCH |
| R-i | R22 starter bibliography "No - Never acceptable" | R22 | compare | identical | MATCH |
| R-j | R22 fix-bibliography row "…verify all citations as valid." | R22 | compare | identical | MATCH |
| R-k | R04 note "STILL AN ASK" | R04 | compare | identical | MATCH |
| R-l | R03 "Research conducted alongside adult researchers … is vital." | R03 | compare | identical | MATCH |
| R-m | R27 "Adults reviewing research reports … any portion of the entry." | R27 (and R20) | compare | identical | MATCH |
| R-n | R18 "In the case of published group research, acknowledge …" | R18 | compare | identical | MATCH |
| R-o | R18 "It is not recommended … sole or first author…" | R18 | compare | identical prefix | MATCH |
| R-p | R20 "both the content and writing should be the work of the applicant" | R20 | compare | identical | MATCH |
| R-q | R21 "If you used third-party software … mention the name of the program." | R21 | compare (ellipsis) | identical ends | MATCH |
| R-r | R08/R09 "Students may not provide links … requested in the application." (GUIDE2027 5e) | R08, R09 | compare | identical | MATCH |
| R-s | R05: title page, abstract, bibliography excluded; appendices count | R05 | compare | identical | MATCH |
| R-t | Task 5 Q5 / Q8-Q9 quotes via `scholar-research.md` l.163-169 | scholar-research.md | read | present at l.163-168 (secondary source; form not re-read, as spec says) | MATCH |

### P-006
| # | Value | Source | Route | Recomputed | Verdict |
|---|---|---|---|---|---|
| P6-1 | R10/R21 FAIL 7 of 7 floats; PASS 4 FAIL 2 SKIPPED 3 MANUAL 18 | check_compliance.py | ran (read-only) | identical | MATCH |
| P6-2 | regex l.122 | script | read | identical | MATCH |
| P6-3 | 7 credit lines l.158/223/265/284/306/327/342 | tex | grep | identical text and lines | MATCH |
| P6-4 | Matplotlib 3.11.1 | .venv; requirements l.7 | import | 3.11.1 | MATCH |
| P6-5 | python-igraph 1.0.0 | requirements l.8 | import | 1.0.0 | MATCH |
| P6-6 | R21 example "Graph created by the student researcher using BioRender, 2024." | yaml R21 | compare | identical | MATCH |
| P6-7 | igraph layout domain_figure.py l.30; sts_critical_bus_map.py l.36 | code | grep | l.30; l.36 | MATCH |
| P6-8 | Fig. 5 label l.340 precedes credit l.342 | tex | grep | yes | MATCH |
| P6-9 | FONT_FLOOR_PT = 10 (l.11) | check_compliance.py | read | l.11 = 10 | MATCH |

### P-010
| # | Value | Source → key | Route | Recomputed | Verdict | Flag |
|---|---|---|---|---|---|---|
| P10-1 | splits grouped by scenario_id (GroupShuffleSplit) | make_splits.py | read | yes | MATCH | |
| P10-2 | 300 test bases/split; rows/base min 185, median 186 | sts_e12_e13 | raw | 300 each; 185 min | MATCH | UNTRACKED |
| P10-3 | test rows 55,789 / 55,792 / 55,787 / 55,791 / 55,791 | tuned_metrics n_test | own GroupShuffleSplit | identical | MATCH | |
| P10-4 | marginal cov 89.3 ± 1.3 / 89.8 ± 1.0 | sts_e12_e13 marginal_coverage_090 | raw | 89.339 ± 1.327 / 89.818 ± 0.984 | MATCH | |
| P10-5 | element share < 0.85: 18.06 ± 0.65 / 23.55 ± 2.95; expected 0.24 | E12_element | raw (186 elements) | 18.065 ± 0.645 / 23.548 ± 2.953; 0.243 (key) | MATCH | UNTRACKED |
| P10-6 | min element coverage 0.575 ± 0.016 / 0.557 ± 0.030 | E12_element.min | key | 0.5747 ± 0.0157 / 0.5567 ± 0.0303 | MATCH | UNTRACKED |
| P10-7 | base share < 0.85: 8.67 ± 1.52 / 8.67 ± 1.73; expected 1.89 | E13 | raw; key | 8.667 ± 1.520 / 8.667 ± 1.726; 1.889 | MATCH | UNTRACKED |
| P10-8 | ≥1-miss bases: histgb@0.97 11.13 ± 2.57; ridge@0.94 7.67 ± 2.03; @0.90 47.13 ± 4.73 / 22.53 ± 3.59; ridge@0.97 0.47 ± 0.50 | any_miss | raw | 11.133 ± 2.570; 7.667 ± 2.033; 47.133 ± 4.726; 22.533 ± 3.594; 0.467 ± 0.499 | MATCH | UNTRACKED |
| P10-9 | cluster-bootstrap SE 7.0 ± 0.8× / 5.6 ± 0.8× | panel round1_stats.md l.76 only | searched data/ for a key | no artifact (orientation recompute 7.09 ± 0.95 / 5.77 ± 0.68) | NOT FOUND | not printable |
| P10-10 | exchangeability statement | sts_n1_class_conditional.exchangeability | key | present | MATCH | UNTRACKED |

### P-011 (row by row)
| # | Row | Value | Source | Route | Recomputed | Verdict | Flag |
|---|---|---|---|---|---|---|---|
| P11-1 | algorithm | NR | dataset.manifest solver.algorithm; gd:149 | read | "nr"; runpp at l.149 | MATCH | |
| P11-2 | init | dc | manifest; gd:149,183,214 | read | l.149, 183, 214 | MATCH | |
| P11-3 | Q-limits | enforced | manifest; gd:149 | read | true | MATCH | |
| P11-4 | numba | on, 0.66.0 | manifest | read; import | 0.66.0 | MATCH | |
| P11-5 | tolerance | 1e-8 MVA default | runpp signature | inspect | 1e-08 | MATCH | |
| P11-6 | max iterations | "auto" default | signature | inspect | 'auto' | MATCH | |
| P11-7 | non-converged | 45 of 279,000 | manifest derived_verification | raw | 279,000 / 278,955 / 45 | MATCH | |
| P11-8 | Python | 3.13.9 | tuned_metrics.manifest; .venv | read; --version | 3.13.9 | MATCH | |
| P11-9 | pinned packages | pandapower 3.5.4, numpy 2.3.5, pandas 2.3.3, sklearn 1.7.2, pyarrow 21.0.0, numba 0.66.0, matplotlib 3.11.1, igraph 1.0.0 | requirements.txt; manifests | import each | identical | MATCH | |
| P11-10 | networkx | 3.6.1, unpinned | import; requirements | import; read | 3.6.1; absent from requirements | MATCH | |
| P11-11 | manifest census | 66 identical / 58 none / 1 partial / 4 sts; no differing version | all *.manifest.json | recursive scan | 67 / 63 / 1 / 4 (135); no differing version | MATCH (substance) | counts drifted: 3 manifests newer than spec |
| P11-12 | invocation | --n 1500 --mult 1.0-1.12 --reg 1.0-1.12 --pf 0.9-1.15 --dvm 0.025 | manifest run_settings; README:94-95 | read | identical | MATCH | |
| P11-13 | code defaults differ | REG 1.00-1.50, PF 0.80-1.50, DVM 0.03 (gd:18-27) | code | read | l.19-25 | MATCH | |
| P11-14 | base cases | 1,500 = 750 + 750 alternating | sts_dataset_facts; gd:314-316 | raw | 750/750, alternating | MATCH | UNTRACKED; anchor is **l.316-318** |
| P11-15 | independent multiplier | U(1.00,1.12); realised 1.000004-1.119999 | invocation; gd:114 | raw (pload / case118 base) | 1.0000040 / 1.1199996 | MATCH | |
| P11-16 | regional | 0.9009-1.2310, 43.91% outside of 74,250 | sts_dataset_facts | raw | 0.900858 / 1.230963; 43.9057% of 74,250 | MATCH | UNTRACKED |
| P11-17 | regions | 8 | region_of_load | ran | 8 | MATCH | |
| P11-18 | floor 0.5 / cap 1.60 inactive; agg 1.0142-1.1239 | gd:115-118; manifest | read | as stated | MATCH | |
| P11-19 | reactive scale | U(0.90,1.15); realised 0.8156-1.4083 | gd:119-121; facts | raw (qload / base) | 0.815637 / 1.408329 | MATCH | label flag stands |
| P11-20 | setpoint | ±0.025, redrawn in [0.94,1.06]; max dev 0.024995 | gd:9-10, 80-93; manifest | read | as stated | MATCH | |
| P11-21 | Q-limit scale | U(0.60,1.40) | gd:26 | read | l.26 | MATCH | |
| P11-22 | gen P fixed; genp zero-variance | gd:170 | raw nunique | nunique 1 for all 53 | MATCH | anchor is **l.168** |
| P11-23 | gen removal p 0.30 non-slack | gd:28, 128-130 | read | as C6-3 | MATCH | |
| P11-24 | gen-out bases 374 (24.93%) | manifest | raw | 374 | MATCH | |
| P11-25 | N-0 rule ≥ 0.94 | gd:254 | read | test is at **l.256** | MATCH | anchor off; data min 0.940000036 (> 0.94) |
| P11-26 | N-0 acceptance 53.82% (1500/2787) | frozen v2 n0_gate_pass_rate_pct; case57_gonogo.py:21 | arithmetic; read | 53.821%; l.21 = 53.82 | MATCH | run-log only |
| P11-27 | contingencies 186 = 173 + 13 | branch_list | ran | 186 | MATCH | |
| P11-28 | rows 280,500 = 1,500 + 279,000; 278,955 | manifest | raw | identical | MATCH | |
| P11-29 | target = nanmin | gd:201-203 | read | at **l.197** | MATCH | anchor off |
| P11-30 | range 0.7179-0.9603; 17.48% | clip_artifact fixed_v2 | raw | 0.717941 / 0.960311 / 17.4756 | MATCH | |
| P11-31 | build seed not recorded | manifest provenance_class.unknown | read | stated | NOT FOUND (value) | correctly disclosed as NOT FOUND |
| P11-32 | manifest retroactive | provenance_class.retroactive | read | true | MATCH | |
| P11-33 | sha256 8f0fd108…c1b8e | manifest; clip_artifact | shasum of parquet | 8f0fd108…4e49c1b8e | MATCH | |
| P11-34 | case30 window 0.87-0.99; rule; seed 100 | case30_thermal/dataset.manifest | read | identical | MATCH | |
| P11-35 | case30 acceptance 1,500 / 8,050 (18.63%); rejects 840 V / 5,710 thermal; rows 61,500 / 63,000 | h3_build_stats | read; raw row count | identical | MATCH | |
| P11-36 | case30 other knobs not in manifest | manifest | read | only stress/mult recovered-from-docs + range | MATCH | |
| P11-37 | split unit / 60-20-20 / 900-300-300 bases | make_splits | own GroupShuffleSplit | identical | MATCH | |
| P11-38 | seeds 0-4 | tune_surrogates:17,241 | read | yes | MATCH | |
| P11-39 | rows per split (train/cal/test × 5) | make_splits | own split | identical to all 15 numbers | MATCH | |
| P11-40 | inner 540/180/180 bases, ≈100.4k/33.5k/33.5k rows, rs 1000+seed | tune_surrogates:19,172 | own split | 540/180/180; 100,422-100,425 / 33,470-33,477 / 33,473-33,476 | MATCH | |
| P11-41 | ± ddof 0 | std_convention | read | yes | MATCH | |
| P11-42 | inputs 805 = 118+118+118+53×5+186 | build_design_matrix | ran repo fn | (278,955, 805) | MATCH | |
| P11-43 | agg_loading excluded | make_splits:14-18 | read | yes | MATCH | |
| P11-44 | kept 701/700/700/700/701 | select_features | ran repo fn | identical | MATCH | float32-cast dependent |
| P11-45 | ridge standardised | tune_surrogates:57-60 | read | l.58-59 | MATCH | |
| P11-46 | ridge grid 15 α logspace(−3,4) | :25; tuning_search | read | 15 values | MATCH | |
| P11-47 | histgb space | :26-30, 40-47 | read | identical | MATCH | pinned `committed` has max_depth 8 |
| P11-48 | histgb candidates 24 + 2 = 26 | :21-22, 32-48; tuning_search records | count records per seed | 26 histgb, 15 ridge per seed (205 total) | MATCH | |
| P11-49 | early stopping auto, 0.1, 10; n_iter 81/71/71/73/144 | sklearn signature; tuned_metrics | inspect; read | identical | MATCH | |
| P11-50 | coverage grid 0.70-0.99, 30 | :23 | read | yes | MATCH | |
| P11-51 | M2 rule; tie → lower MAE; refit | :92-122, 247-253 | read | select_best l.110-121 as stated | MATCH | |
| P11-52 | chosen α 1, 0.001, 0.001, 0.001, 0.01 | selections | read | identical | MATCH | |
| P11-53 | chosen histgb configs (5) | selections + config | read | identical | MATCH | |
| P11-54 | histgb random_state = seed | :69 | read | yes | MATCH | |
| P11-55 | score = pred − true; k = ⌈(n+1)t⌉ capped | gate_eval:7-13 | read; reimplemented | identical results | MATCH | |
| P11-56 | limit 0.94 | tune_surrogates:18 | read | yes | MATCH | |
| P11-57 | t_solve 9.14 = min of 400 after 30 warm-up; mean 9.561, median 9.512, std 0.256 | solve_time.json | read | identical (min_ms 9.138) | MATCH | measure_solve override flag confirmed (only mult_hi) |
| P11-58 | t_surr 0.00116 ± 0.00012 / 0.00241 ± 0.00062 | tuned_metrics ms_surrogate | recomputed ddof 0 | 0.0011628 ± 0.0001216 / 0.0024111 ± 0.0006163 | MATCH | |
| P11-59 | hardware Apple M5 arm64 Darwin 25.5.0 | solve_time.manifest; tuned_metrics.manifest | read | identical | MATCH | |
| P11-60 | clip-era 35.17 / 55.51, archive gitignored (.gitignore:20) | clip_artifact cited_in_sts | recomputed from local archive parquet (sha matches) | 35.1703 / 55.5119 | MATCH | archive is gitignored but present locally |
| P11-61 | sts_dataset_facts untracked | git ls-files | git ls-files | untracked | MATCH | |

### P-013
| # | Value | Source → key | Route | Recomputed | Verdict | Flag |
|---|---|---|---|---|---|---|
| P13-1 | inner ceiling 0.01 | tuning_search.inner_missed_ceiling; tune_surrogates:20 | read | 0.01 | MATCH | |
| P13-2 | violation rate 17.48 | unconditioned_base | raw | 17.4756 | MATCH | |
| P13-3 | 1% of violations ≈ 0.17% of all | derived | arithmetic | 0.1748% | MATCH | |
| P13-4 | crossings ridge 0.94, histgb 0.97; per-seed lists; 2/5, 1/5 | frozen v2 crossings; any_miss per_seed | raw | identical | MATCH | |
| P13-5 | held-out histgb 1.15 ± 0.27 (4/5) | recomputed | own join | 1.145 ± 0.270 | MATCH | |
| P13-6 | N1 δ=1% 0.98 ± 0.26 / 1.07 ± 0.28 | threshold_rows."0.01" | raw threshold form | 0.984 ± 0.256 / 1.068 ± 0.279 | MATCH | UNTRACKED |
| P13-7 | ≥1-miss histgb@0.97 11.13 ± 2.57 | any_miss | raw | 11.133 ± 2.570 | MATCH | UNTRACKED |
| P13-8 | N2 corrected 0.46 ± 0.08 vs stored 0.83 ± 0.24 | sts_n2 missed_cases per_seed | recomputed from per-seed fields | 0.462 ± 0.079 / 0.832 ± 0.245 | MATCH | UNTRACKED; audit only, not printable |
| P13-9 | NERC TPL-001-5.1 no numeric limit | prior-art.md §9.10 | read | "no numeric voltage limit" | MATCH | |

### P-015
| # | Value | Source → key | Route | Recomputed | Verdict | Flag |
|---|---|---|---|---|---|---|
| P15-1 | 111.83% | thermal_check networks.case30.rating_audit.base_case_loading_pct.line_max | key | 111.8314 | MATCH | key is under `rating_audit`, not directly under `case30` |
| P15-2 | published BM 20.01; viol 28.81 | case30_frozen | raw case30_dataset.parquet | 20.0146 / 28.8081 | MATCH | |
| P15-3 | histgb@0.90 6.98 ± 0.87 / 1.47 ± 0.20 / 14.52 ± 1.60 | four_metrics | key; missed also from per-seed n_missed / n_true_viol | 6.982 ± 0.874 / 1.466 ± 0.195 / 14.522 ± 1.599 | MATCH | |
| P15-4 | ridge@0.90 27.87 ± 3.99 / 1.49 ± 0.53 / 3.66 ± 0.48 | same | same | 27.875 ± 3.987 / 1.493 ± 0.527 / 3.656 ± 0.482 | MATCH | |
| P15-5 | crossings histgb@0.93 0.98 / 8.96 / 11.27; ridge@0.92 0.85 / 34.48 / 2.98 | crossings_first_below_1pct_missed | key (no per-seed records in file) | 0.981 / 8.959 / 11.265; 0.853 / 34.483 / 2.985 | MATCH | means only |
| P15-6 | regen window 0.87-0.99; BM 7.09 | manifest range; frozen | read; raw | [0.87, 0.99]; 7.0862 | MATCH | |
| P15-7 | regen 21.5% > 100% loading | h3_build_stats.n1_loading.share_above_100 | read | 21.485 | MATCH | |

### P-017
| # | Value | Source | Route | Recomputed | Verdict |
|---|---|---|---|---|---|
| P17-1 | strip 0.005; ρ definition | netstudy2/cross_2a_points | read | identical | MATCH |
| P17-2 | q̂ 0.0051982 / 0.0022907 | tradeoff_curve_v2 | sweeps | 0.0051982 / 0.0022907 | MATCH |
| P17-3 | BM 56.86 | frozen v2 | raw | 56.8629 | MATCH |
| P17-4 | "80 term/symbol rows" | P-017 §4a-4d | count table rows | 84 | **MISMATCH** (not printed) |

### minors P-018 … P-027
| # | Value | Source | Route | Recomputed | Verdict | Flag |
|---|---|---|---|---|---|---|
| M1 | P-018 pandapower 3.5.4; case30 = "Washington 30 Bus Dynamic Test Case" (l.205-217); case_ieee30 separate (l.224-238); code refs | pandapower source; scripts | grep | identical | MATCH | |
| M2 | P-019 9 / 186 islanding outages | topology | own `unsupplied_buses` loop | 9 | MATCH | no key |
| M3 | lines 6, 7 → 100% violations | dataset.parquet | raw | 100.0 / 100.0 | MATCH | |
| M4 | seven load-losing outages, MW 6/21/0/68/20/0/184, rates 3.87/0.13/3.00/0.60/0.40/2.20/4.53 | topology + parquet | raw | identical | MATCH | no key |
| M5 | nanmin gd:197 | code | read | l.197 | MATCH | |
| M6 | P-020 45 = trafo0 37 / trafo7 7 / trafo6 1; IEEE 8-5, 65-68, 65-66; ≤1 per scenario | nonconverged_gate; parquet | raw | identical | MATCH | |
| M7 | flagged ridge 38-39, histgb 37-39; certified 0-2; escalated 4-8 | summary | read all by_seed arrays | identical | MATCH | |
| M8 | histgb@0.90 certifies 2/45 every seed; 0-1 in test | summary | read | [2,2,2,2,2]; test [1,1,0,1,0] | MATCH | |
| M9 | "That is the only place a non-converged case is certified" | summary | read | ridge@0.90 seed 1 certifies 1 (test 1); histgb@0.97 seed 3 certifies 1 (test 1) | **MISMATCH** | |
| M10 | Δmissed −1.0e-5 / −8.4e-6 / +1.3e-5 / +1.2e-5; published means = v2 | summary | read | identical | MATCH | |
| M11 | P-021 0.9012 / 24 (mult 0); 0.7199 / 39 (nominal); 0 / 3,000 | case57 diagnostic; feasibility | read | 0.901210 / 24; 0.719914 / 39; 0 / 3000 | MATCH | |
| M12 | P-023 ± values (7) | tradeoff_curve_v2; case30 records | sweeps; per-seed | all identical at printed precision | MATCH | |
| M13 | ddof=1 upper bars 1.03 / 1.11 | same | ddof 1 | 1.027 / 1.106 | MATCH | |
| M14 | per-seed missed ridge@0.94 / histgb@0.97; 1/5, 2/5 | tuned_metrics | sweeps | identical | MATCH | |
| M15 | code ddof 0 (build_v2_frozen:34-38; emit_v2_tables:22,32-34) | scripts | read | np.std default | MATCH | |
| M16 | P-024 pooled 73.68 / 54.90 / 26.74 / 21.41; 78.59; per-seed 73.73 ± 3.93, 55.21 ± 2.65, 26.82, 21.21; counts 1,436 / 2,284; max 0.091457 both | missed_depth | raw preds, own q̂ | identical | MATCH | |
| M17 | P-025 NORM_GAMMA 0.5; STRIP 0.005; stale manuscript_role; null model_hyperparameters (2 manifests) | code; manifests | read | identical | MATCH | |
| M18 | P-026 persistence 4.2 ± 0.1, −0.06, 99.5 ± 0.2, 0.31 ± 0.08, 1.00; train-mean 6.7 ± 0.2, −0.00, 0.0, 0.00 | screener_metrics | recomputed ddof 0 | 4.2457 ± 0.0706, −0.0611 ± 0.0032, 99.534 ± 0.164, 0.311 ± 0.080, 1.0047 ± 0.0017; 6.7316 ± 0.1726, −0.0002 ± 0.0002, 0, 0 | MATCH | |
| M19 | same test counts; n_true_viol 9,809 / 9,772 | screener_metrics; baselines | read | identical | MATCH | |
| M20 | mean min_vm 0.93983 | dataset.parquet | raw | 0.939826 | MATCH | |
| M21 | R² strings hard-coded | emit_v2_tables l.56, l.60 | grep | yes | MATCH | |
| M22 | P-027b ridge 11.6% below persistence (8.95-17.09 per seed); histgb 63.2% | tuned_metrics; screener_metrics | recomputed | 11.57% (8.95-17.09); 63.19% | MATCH | |
| M23 | P-027e 30 coverage levels; 9 targets; OPS_TARGETS l.8 | files | read | identical | MATCH | |
| M24 | P-027g 73.136% max_vm > 1.05 | dataset.parquet | raw | 73.1358 | MATCH | no key |
| M25 | F1 audit n 25, max errors 0.0, zero-variance elements 0 | f1_leakage_audit | read | identical | MATCH | |

### numbers-2b
| # | Value | Source → key | Route | Recomputed | Verdict | Flag |
|---|---|---|---|---|---|---|
| N1 | 2b-1 upper ends 1.00 (0.7935 + 0.2090) / 1.08 (0.8322 + 0.2447); tex "1.07" is a rounding error | tradeoff_curve_v2 | sweeps | 1.0025 / 1.0769 | MATCH | tex l.231 "1.0--1.07" confirmed wrong |
| N2 | 2b-2 55.51; 56.86; 35.17 | clip_artifact | raw archive parquet (sha matches) + dataset.parquet | 55.5119 / 56.8629 / 35.1703 | MATCH | archive gitignored |
| N3 | 2b-3 56.9 → 56.86; 14.06 | frozen v2; facts_b | raw | 56.8629; 14.0628 (39,229 rows) | MATCH | UNTRACKED (facts_b) |
| N4 | 2b-4 27.10 (27.0961), 16.81, 9.31, 8.45, 4.12 | frozen v2 critical_bus_top5; manifest; classical_screen | raw argmin_bus shares | 27.0961 / 16.8084 / 9.308 / 8.448 / 4.1179 | MATCH | |
| N5 | 31.616% of strip rows at index 75 | sts_dataset_facts | raw | 31.616 | MATCH | UNTRACKED |
| N6 | 2b-5 ceilings / saturation (see C12-7, C12-8) | | raw | as C12 | MATCH | |
| N7 | 2b-6 t_surr (see P11-58); re-measure 0.00346 / 0.00115; t_solve 9.14 | break_even timing | read | 0.0034565 / 0.0011463; 9.14 | MATCH | |
| N8 | speedup 1.5697 → 1.5694 | computed | arithmetic | 1.56974 → 1.56943 | MATCH | |
| N9 | 2c 750/750, 0.9009, 1.2310, 43.91, 1.000004/1.120000, 0.8156, 1.4083, 0.5413 (1,510) | sts_dataset_facts | raw | identical (independent max 1.1199996) | MATCH | UNTRACKED |
| N10 | P-008 two-sided 61.61 (171,865); above 56.86; below 4.75; bin 14.06 | sts_dataset_facts_b | raw | 61.6103 / 56.8629 / 4.7474 / 14.0628 | MATCH | UNTRACKED |
| N11 | E2c A 0.1163 / B 0.1056; rel 0.4726 / 0.4933; n 54 | netstudy2 cross_network | from cells | identical | MATCH | |
| N12 | E2c spreads 0.2097 / 0.1145; paired 0.0107 ± 0.113; A < B 42/54; case24 ridge 0.5194 / 0.2852, 9/9; excl. 0.0357 / 0.0697 | cross_comparisons | from cells | 0.2097 / 0.1145; 0.01069 ± 0.1132; 42; 0.5194 / 0.2852, 9; 0.0357 / 0.0697 | MATCH | no key |
| N13 | "locked tes" only l.353 | tex | grep | l.353 | MATCH | |

### checker-phrases
| # | Value | Source | Route | Recomputed | Verdict |
|---|---|---|---|---|---|
| K1 | check_paper exit 1; phrase hits l.361 `\bprove[sn]?\b`, l.365 `escalation floor` | check_paper.py | ran (plain run, no write) | identical | MATCH |
| K2 | PHRASE_REGEXES at l.48-58 | script | read | identical list | MATCH |
| K3 | l.314 "proved", l.367 "proof" not caught | tex | grep + regex | not caught | MATCH |
| K4 | patterns added 2026-08-03, prompt log l.1330-1334 | prompt log | read | entry header l.1320 dated 2026-08-03 | MATCH |
| K5 | first committed d32f309 (2026-07-28) | git log -S | read-only git | d32f309 2026-07-28 | MATCH |
| K6 | factcheck-2026-08-27.md l.357 "essentially lands on the saturation point" | notes | read | present | MATCH |

### cuts
| # | Value | Source | Route | Recomputed | Verdict |
|---|---|---|---|---|---|
| X1 | citation map: tsybakov2004, mammen1999 only l.314; desalvo2015, angelopoulos2024, cortes2016 only l.361; chow1970 l.314 + l.361; elyaniv2010 l.231 + l.361; bates2021 l.99 + l.363 | tex | grep | identical | MATCH |
| X2 | `\begin{thebibliography}{23}`, 23 bibitems | tex | grep | 23 / 23 | MATCH |
| X3 | case89pegase 392%, 16 of 50, 199.37% (spec: not re-read) | case89pegase_nofeasible_diagnostic | read | 392.21 / 16 of 50 / 199.37 | MATCH |
| X4 | case57 numbers | as M11 | | | MATCH |

### P-028
| # | Value | Source | Route | Recomputed | Verdict |
|---|---|---|---|---|---|
| L1 | AC-solve fraction 0.25-0.71 (§VII-B p.6); IEEE-118 row 0.63 / 0.012 / 0.71 (p.7) | lit note "Audited Selective Verification…md" l.40, l.46 | read | present in lit note | MATCH (to lit note only; source PDF not re-read — not printable) |
| L2 | printable number from the paper | — | — | none exists | NOT FOUND (by design) |

## Std-rule checks (comparisons a spec says may, or may not, be claimed)
| Spec | Comparison | Values (recomputed) | Gap vs larger std | Result | Spec's position |
|---|---|---|---|---|---|
| Top5-5 | histgb vs ridge at ~1% (missed) | 0.832 ± 0.245 vs 0.794 ± 0.209 | 0.04 < 0.245 | STD-FAIL | tie — correct |
| Top5-5 | same (escalation) | 63.68 ± 5.12 vs 64.34 ± 2.78 | 0.66 < 5.12 | STD-FAIL | tie — correct |
| Top5-5 | held-out vs test-picked histgb missed | 1.145 ± 0.270 vs 0.832 ± 0.245 | 0.313 > 0.270 | STD-PASS (narrow) | correct |
| Top5-5 | case118 vs case30 escalation | 63.68 ± 5.12 vs 5.84 ± 1.25 | 57.8 | STD-PASS | correct |
| Top5-5 / P-009 | static vs ridge gate | 99.41 ± 0.16 vs 97.04 ± 0.44 | 2.37 | STD-PASS | correct |
| Top5-5 / P-009 | static vs histgb gate | 96.64 ± 0.50 vs 95.28 ± 0.98 | 1.36 | STD-PASS | correct |
| C4 | histgb vs ridge missed @0.90 | 4.717 ± 0.977 vs 2.963 ± 0.439 | 1.75 | STD-PASS | correct |
| C4 | measured coverage vs knob 0.90 | 89.82 ± 0.98; 89.34 ± 1.33 | 0.18; 0.66 | within 1 std ("calibrated" supported) | correct |
| C12 | F-a vs F-b vs F-c histgb | 63.7 ± 5.1 / 59.3 ± 4.0 / 61.2 ± 3.3 | max 4.4 < 5.1 | STD-FAIL | indistinguishable — correct |
| C12 | ceiling histgb vs saturation | 82.795 ± 0.369 vs 82.635 ± 0.166 | 0.16 < 0.37 | STD-FAIL | "at", not "above" — correct |
| C12 | ridge vs histgb ceiling | 74.89 ± 0.83 vs 82.79 ± 0.37 | 7.9 | STD-PASS | correct |
| C12 | Mondrian vs global escalation | 42.90 ± 1.91 vs 56.96 ± 4.25 | 14.1 | STD-PASS | correct (missed 1.45 vs 1.36: tie, correct) |
| P-010 | element share vs 0.24 expectation | 18.07 ± 0.65; 23.55 ± 2.95 | ≫ | STD-PASS | correct |
| P-010 | ridge vs histgb element share | 18.07 ± 0.65 vs 23.55 ± 2.95 | 5.48 > 2.95 | STD-PASS | correct |
| P-010 | ≥1-miss histgb@0.97 vs ridge@0.94 | 11.13 ± 2.57 vs 7.67 ± 2.03 | 3.47 > 2.57 | STD-PASS | correct (different operating points caveat) |
| P-013 | stored vs N2-corrected missed | 0.832 ± 0.245 vs 0.462 ± 0.079 | 0.37 > 0.245 | STD-PASS | not printable (audit only) — correct |
| P-015 | case30 pub vs case118 escalation @0.90 | 6.98 ± 0.87 vs 30.63 ± 2.51 | 23.6 | STD-PASS | correct |
| P-023 / 2b-1 | histgb@0.97 mean vs 1% | 0.832 ± 0.245 | 0.168 < 0.245 | STD-FAIL | must not claim "below 1%" — correct |
| P-023 / 2b-1 | ridge@0.94 mean vs 1% | 0.7935 ± 0.2090 | 0.2065 < 0.2090 | STD-FAIL | correct |
| P-024 | pooled vs per-seed-mean shares | 73.68 vs 73.73 ± 3.93; 54.90 vs 55.21 ± 2.65 | < std | tie | correct |
| P-027b | ridge MAE vs persistence | 3.754 ± 0.133 vs 4.246 ± 0.071 (×1e-3) | 0.49 > 0.133 | STD-PASS | correct |
| numbers-2b 2b-5 | as C12 ceiling vs saturation | | | STD-FAIL | correct |
| numbers-2b E2c | A vs B mean abs error | 0.1163 ± 0.2097 vs 0.1056 ± 0.1145 | 0.0107 < 0.2097 (paired 0.0107 ± 0.113) | STD-FAIL | "slightly better" unsupported — correct |
| numbers-2b 2b-6 | histgb re-measure vs committed t_surr | 0.00346 vs 0.00241 ± 0.00062 | 0.00105 > 0.00062 | STD-PASS (one re-measure, no std) | correct; no speedup effect |

(Counts: 14 STD-PASS, 8 STD-FAIL. The C4 coverage-vs-knob row and the P-024 pooled-vs-seed-mean row are
ties that the specs use correctly; they are not counted as PASS or FAIL.)

## Cross-occurrence check (grep of `report/paper_current_STS.tex`, 460-line working tree)
| Spec | Quantity | Printed at lines | Listed in the spec's consistency section? |
|---|---|---|---|
| Top5-5 | 3.29 / 4.72 (histgb@0.90) | 81, 199, 218, 231, 255 (+3.29 at 292) | partial — only l.231 (body values unchanged unless §5 headline changes) |
| Top5-5 | 63.7 / 1.58 / 0.83; "1.6" | 81, 231, 259; 1.6 at 349, 388 | yes except Table 2 l.259 (data row) |
| Top5-5 | 56.86 / 56.9 | 81, 121, 314, 365; 56.9 at 323 | partial — l.365 only; 121/314/323 not listed (323 handled in numbers-2b) |
| Top5-5 | 7.09 / 5.84 ± 1.25 | 81, 365 | yes |
| Top5-5 | "IEEE 30-bus" | 81, 119, 365 (+ bare "30-bus" 367, 388) | yes via P-018 |
| C1 | 54; "five networks"; 0.4726/0.4933 | 353; 355; 353 | yes |
| C4 | 89.8 / 89.3 | 199, 255 / 199, 248 | yes |
| C4 | 4.72 | 81, 199, 218, 231, 255 | **no — l.231 missing** |
| C4 | 2.96 | 199, 217, 248 | yes |
| C4 | 17.48 | 119, 314, 365 | **no — l.365 missing** |
| C6 | 374 / 24.93 / 69,532 / 30% | 119, 367 / 367 / 119 | yes |
| C12 | 56.86 / 56.9 | 81, 121, 314, 365 / 323 | **no — l.121 missing** |
| C12 | q̂ 0.0052 / 0.0023 | 132 / 132, 347 | **no — l.132 missing** |
| C12 | 30.6 | 199, 218, 231, 255, 347 | partial — l.347 only (value unchanged) |
| C12 | 82.64 / 74.89 / 82.79 | 347 | yes |
| C12 | 7.09 / 5.84 | 81, 365 | yes |
| P-010 | 186 per base | 111, 119, 363 | partial — l.363 (anchor); 111/119 are structural counts |
| P-010 | 89.3 / 89.8 (if printed) | 199, 248, 255 | partial — captions only |
| P-011 | 9.14 / "9 ms" / M5 | 147 / 109 | yes |
| P-011 | t_surr | 147 | yes |
| P-011 | l.119 sampler numbers, 280,500 / 279,000 / 45 / 278,955 | 119 | yes (via Cut-6) |
| P-011 | 374 / 24.93 | 119, 367 | partial — l.367 not listed (C6 lists it) |
| P-011 | 17.48 (if kept in table) | 119, 314, 365 | partial — 314/365 not listed |
| P-011 | 55.5 / 35.17 | 121 | yes |
| P-013 | 1% as the bar | 81, 124, 231, 281, 349, 365, 388 | **no — l.365 ("All five splits are under 1% at 0.97") missing** |
| P-015 | 111.83 | 119, 365 | yes |
| P-015 | 7.09 | 81, 365 | yes |
| P-017 | q̂ 0.0052 / 0.0023; 56.86 | 132, 347; see above | q̂ yes (l.132, PNG) |
| minors | 45 (P-020) | 119 | yes |
| minors | 0.9012 / 24 (P-021) | 353 | yes |
| minors | 74 / 55 / 26.7 / 21.4 (P-024) | 292, 303 | yes |
| minors | 73.1 (P-027g) | 107 | yes |
| minors | 2.04 / 3.29 "very fast" (P-027b) | 199, 217, 248, 292, 388 | yes (199, 388 anchors) |
| numbers-2b | 1.0--1.07 and its qualitative twins | 231; 81, 281, 349 | yes |
| numbers-2b | 55.5 | 121 | yes |
| numbers-2b | 56.9 vs 56.86 | 323 vs 81, 121, 314, 365 | yes |
| numbers-2b | 27.1 / 16.81 / 9.31 | 314, 339 | yes |
| numbers-2b | 14 / 14.1 | 314 / 323 | yes |
| numbers-2b | 0.1056 / 0.1163; "locked tes" | 353 | yes |
| numbers-2b | 2c values; 0.5% | 119; 323 | yes |
| checker-phrases | "floor" | 101, 107 (×3), 303, 312, 365, 388 | yes |
| cuts | bibitem-only citations | see X1 | yes |

---

## Pass 2 — re-verification of the two rejected specs and spot-check of non-blocking fixes (2026-09-27)

Same rules and method as pass 1: `.venv/bin/python`, read-only git, and a second route where one exists.
Revised files checked: `P-002-P-012-disclosure.md` (mtime 19:14:58), `minors_P-018_P-027.md` (19:14:38),
`P-011.md`, `P-017.md`, `C4.md`, `C12.md`, `P-013.md`, `Top5-5.md` and `_index_B.md` (19:15-19:16).

### Verdicts
| Spec | Pass 1 | Pass 2 | Same issue again? |
|---|---|---|---|
| P-002-P-012-disclosure.md | REJECTED (A7 "tracked") | **SIGNED OFF** | No. A3, A7 and §F are correct. One non-blocking quote caveat (Q2-9). |
| minors_P-018_P-027.md | REJECTED (P-020 "only place certified") | **SIGNED OFF** | No. All 20 seed × target cells match. |
| P-011, P-017, C4, C12, P-013, Top5-5 | SIGNED OFF (non-blocking notes) | SIGNED OFF | The fixes are in place (below). |
| _index_B.md (not a spec) | exactly-0.94 claim wrong | corrected | — |

Pass 2 counts: 27 MATCH, 0 MISMATCH, 0 NOT FOUND, 0 ROUNDING.

### Disclosure: A3, A7, §F
| # | Claim | Route | Found | Verdict |
|---|---|---|---|---|
| Q2-1 | A3: prompt log 6,155 lines, 2026-07-26 → 2026-09-27; not in git (`.gitignore:23`) | wc; `git check-ignore -v` | 6,155; `.gitignore:23:notes/` | MATCH |
| Q2-2 | A7: `1_research_draft_ORIGINAL.txt` and `…_ORIGINAL_rev2.txt` NOT tracked; the comment reads "# Private — never commit to the public fork" | check-ignore; `.gitignore` l.22-23 | both ignored; comment at l.22 | MATCH (pass-1 defect fixed; filename fixed) |
| Q2-3 | §F: check-ignore run for the prompt log, contribution log, sts-constraints.yaml and draft ORIGINAL | check-ignore | all 4 ignored by `.gitignore:23` | MATCH |
| Q2-4 | §F: `git ls-files notes` is empty | git ls-files | 0 | MATCH |
| Q2-5 | §F list of records not in git: prompt log, contribution log, both drafts, retired 2026-08-17 draft, ai_usage_changelog.md, sts-constraints.yaml | check-ignore on each file | all 7 files ignored | MATCH |
| Q2-6 | §F: the only record is local mtimes plus sha256 values quoted in the log | prompt log l.4937, l.4982, l.5521-5528 | sha lines present | MATCH |
| Q2-7 | §F: pipeline code is tracked apart from the untracked `sts_*` files | git ls-files; git status | feasibility 42 and scripts 65 tracked; `scripts/sts_*.py` untracked (including the new `sts_dataset_facts_c.py` and `sts_miss_depth_noannot.py`) | MATCH. "`sts_*` files" must be read as covering the scripts as well as the data. |
| Q2-8 | §E Q3 addition (log outside version control) | read | consistent with §F | MATCH |
| Q2-9 | §F quote: R22 asks for "a log of the prompts … as part of your research notebook" | verbatim compare with the yaml R22 block | Both fragments are verbatim and in order inside the R22 block. The ellipsis, however, joins two chart rows: the code row ends "…with a log of the prompts." and "as part of your research notebook" belongs to the chatbot and statistics rows. | MATCH (elision). **Caveat:** quote a single row, e.g. "requires a log of your prompts as part of your research notebook." |
| Q2-10 | §5 Numbers unchanged (6,155; 33 = 21 + 12; URTC authors) | as pass 1 | unchanged | MATCH |

### minors: P-020, every cell of `data/nonconverged_gate.json`
Route: I used `q1_q2_per_seed.<family>[seed].target_<t>.{all45,test_split_only}`, a different key from the
pass-1 route (`summary.*_by_seed`), and checked every cell. I also asserted certified + flagged + escalated = 45 in each cell.

| # | Claim | Recomputed (20 cells: ridge {0.90, 0.94} and histgb {0.90, 0.97} × seeds 0-4) | Verdict |
|---|---|---|---|
| Q2-11 | histgb@0.90 certifies 2 of 45 in every seed; in the test split 1/1/0/1/0 (of 11/8/13/9/9) | identical | MATCH |
| Q2-12 | ridge@0.90 seed 1 certifies 1 of 45; test split 1 of 8 | identical | MATCH |
| Q2-13 | histgb@0.97 seed 3 certifies 1 of 45; test split 1 of 9 | identical | MATCH |
| Q2-14 | every other cell certifies 0 (all ridge@0.94 cells included) | 0 in the remaining 12 cells | MATCH |
| Q2-15 | across all cells: flagged 37-39, certified 0-2, escalated 4-8 | 37-39 / 0-2 / 4-8; each cell sums to 45 | MATCH |
| Q2-16 | flagged ridge 38-39, histgb 37-39 | identical | MATCH |
| Q2-17 | Δ seed-mean missed −1.0e-5 / −8.4e-6 / +1.3e-5 / +1.2e-5 | from per-seed `missed_rate_if_nc_are_violations − published_missed_rate`: −1.03e-5 / −8.43e-6 / +1.27e-5 / +1.20e-5 | MATCH |
| Q2-18 | `nonconverged_gate.json` and its manifest are tracked | git ls-files | both tracked | MATCH |
| Q2-19 | summary-table row updated | read l.297 | consistent with the above | MATCH |

### Spot-check of non-blocking fixes
| # | Spec | Fix | Found | Verdict |
|---|---|---|---|---|
| Q2-20 | P-011 | anchors 256 / 168 / 197 / 316-318 | all four corrected; the old anchors (254, 170, 201-203, 314-316) are gone | MATCH |
| Q2-21 | P-011 | census 135 = 67 / 63 / 1 / 4; no differing version | Recount now gives 136 = 68 / 63 / 1 / 4. One more manifest, `data/sts_dataset_facts_c.manifest.json`, was created after pass 1. Still no manifest records a different version. | MATCH (substance). The count will keep drifting while d-runs/d-figs write files, so the table should state "no differing version" rather than a count. |
| Q2-22 | P-011 | pinned `committed` candidate max_depth 8 | stated in the HistGB-space row | MATCH |
| Q2-23 | P-011 / _index_B | N-0 rule is ≥ in code; data minimum 0.940000036; 0 bases exactly at 0.94 | raw: minimum 0.940000035663552; 0 rows == 0.94; 0 rows < 0.94 | MATCH |
| Q2-24 | P-011 §7 | l.367 repeat of 374 / 24.93 / 69,532 | listed | MATCH |
| Q2-25 | P-017 | 84 term rows | stated; my recount is 84 | MATCH |
| Q2-26 | C4 / C12 / P-013 / Top5-5 §7 | C4: l.231 (4.72) and l.365 (17.48). C12: l.121 (56.86) and l.132 (q̂). P-013: l.365 (1% bar). Top5-5: l.121, l.314, l.323 and l.365 (56.86) | All listed. The quoted tex fragments match the working tree (l.121 "moving from 55.5\% to 56.86\%"; l.231 "4.72\% to 2.48\%"; l.365 "17.48\% fall below it" and "All five splits are under 1\% at 0.97"). | MATCH |
| Q2-27 | P-011 | float32-dependent 701/700 feature counts | not added; the printed values are still correct under the repo code | MATCH (optional note, not required) |

Aside, outside the scope of any spec: `.gitignore:24` also ignores the root `CLAUDE.md`, which CLAUDE.md §7
calls "SHARED, TRACKED in git". This is for the owner, not for any spec.
