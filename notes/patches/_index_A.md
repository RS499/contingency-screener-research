# Fix-spec index A: correctness + results (2026-09-27)

Specifications only. No replacement text; the author writes every word of `report/paper_current_STS.tex`
(R04/R22/R27). Every number below was re-read from the named key during this session; "re-read OK" unless marked.
Status tags: **V** = VERIFIED (lead), **Vt** = VERIFIED (teammate), **R** = Reported, **new** = new-run artifact that
landed 2026-09-27 18:27–18:36 (N1, N2, N4, N6, E12/E13; not yet in the ledger, not yet tracked in git), **calc** =
computed by this spec writer from committed keys (not yet independently verified).

Page costs use the ledger's unit costs (sentence 0.07, row 0.03, small table 0.35, figure 0.45); not a compile.

| File | ID(s) | Severity | Net pp | Depends on | Numbers cited (status) |
|---|---|---|---|---|---|
| `P-001.md` | P-001 (= C11) | FATAL → fixable now | ≈ 0 | N2 (**landed, confirms → Branch 1**); d-figs Fig. 3 regen (the image itself prints "deepest miss 0.0915 pu"); blocks E9 | 0.0915 / 0.8485 pu (R); gen 21 IEEE 54 Q = −194.71 = Q_min, N-0 Q −10.00 (R); setpoint 0.9549 (Vt; re-ran a4.py); back-off 0.945073 (Vt; re-ran) = N2 corrected 0.9450730 at IEEE 27 (new); Q-limits-off 0.9390 at IEEE 20, Δ 0.0905 (R); certified seeds 2, 3 (R); N2 flips 4,615/48,749 = 9.47%, 2,162 safe→viol (new); corrected deepest miss 0.0682 / 0.0516 pu (new) |
| `P-003.md` | P-003 (+P-032) | FATAL → **MAJOR** after N2 | +0.2 | owner commits N2 artifacts; precedes E9, C8, C13 | **N2b (P-032) author decision**; 93.5% rows with a wrongly pinned gen (new); 9.47% viol→safe, 0.94% safe→viol (new); violation rate 17.48 → 16.60% (new); strip 56.86 → 56.22% (new); min 0.7179 → 0.8077 (new); 38 of 6,879 deep (< 0.90) violations flip (new); histgb@0.97 missed 0.83 ± 0.24 → 0.46 ± 0.08% (new; passes std rule); ridge@0.94 0.79 ± 0.21 → 1.14 ± 0.57%, 3/5 > 1% (new; fails std rule); @0.90 4.72 → 3.96, 2.96 → 2.91 (new; both fail); 9 N-0 bases below 0.94 corrected (new); 0.7179–0.9603, 17.48% (R); 0.54% below 0.87 (Vt); 74/55%, 26.7/21.4% (R); panel sample 10%/1% (Vt, superseded — do not print) |
| `P-005.md` | P-005 (+2b-1) | MAJOR | 0 | d-figs (route 1) or text route; headline decision; C13 | 0.79 ± 0.21 → upper 1.00 (R); 0.83 ± 0.24 → upper **1.08** (Vt); esc 64.3 ± 2.8 / 63.7 ± 5.1, 1.56 ± 0.07 / 1.58 ± 0.12 (R); `*_std` keys exist, no `fill_between` (Vt) |
| `P-007.md` | P-007 | MAJOR | +0.07 | d-figs facts key for 1,016/1,500; with E1a/Top5-1 | GEN_VM_LO = VMIN_LIMIT = 0.94 (Vt); ±0.025 jitter (R); 1,016/1,500 = 67.73% (Vt; no JSON key); N-0 min 0.94–0.958976, median 0.943358 (R); 31.62% of strip rows at IEEE 76 (Vt d-figs); **"holding its own setpoint" = 13.09% of strip rows (41.4% of bus-76 rows), not 31.6% — MISMATCH**; case30 gens all 1.00 pu (Vt); case30 7.09% / 15.40% (R); floor-0.95 probe (provisional, do not print) |
| `Top5-1.md` | Top-5 #1 (+C7, OS-10) | MAJOR | 0 | title decision; after E1a/E1b/P-007 | 56.86% (R/Vt); 77.649% (Vt); 28.83% vs 56.86% (R); **conditional 65.59% vs 68.90% (recomputed from parquet; key 65.5823 from rounded inputs) (R; pre-registered decisive test — not in ledger)**; quintiles 78.39/81.28/82.36/37.31/4.98% (R); 67.73% (Vt); case30 7.09% (R); 61.61% both-sides (no key — do not print) |
| `Top5-2d-E5.md` | Top-5 #2(d), E5, N1 | MAJOR (author decision; options A/B/C, not chosen) | A +0.07 / B +0.21 / C ≈ +0.2 | author decision; C: commit N1 + verified bibitem; all: P-003 label disclosure | **N2b (P-032) author decision**; A: ridge@0.94 0.79 ± 0.21, 64.3 ± 2.8, 1.56 ± 0.07, 1/5 > 1% (1.146); histgb@0.97 0.83 ± 0.24, 63.7 ± 5.1, 1.58 ± 0.12, 2/5 (1.162, 1.032) (R/Vt); A′ ridge@0.95 0.45 ± 0.12, histgb@0.98 0.30 ± 0.13 (R); B histgb 1.15 ± 0.27 (4/5), esc 59.3 ± 4.0, 1.69 ± 0.12, cov 96.2 ± 0.6; ridge 0.77 ± 0.78 (1/5, 2.24), 65.4 ± 8.1, 1.55 ± 0.22 (Vt); C threshold_rows α = 0.01 histgb 0.98 ± 0.26 (2/5), 61.2 ± 3.3, 1.63 ± 0.09×; ridge 1.07 ± 0.28 (3/5), 61.7 ± 1.7, 1.62 ± 0.04× (new; = Vt STATS); C threshold_groups histgb 0.84 ± 0.46, ridge 0.75 ± 0.46 (new); corrected-label A values (new). Std: B vs A histgb missed passes; all others fail |
| `E1a.md` | E1a (+C7) | MAJOR | +0.03 | owner commits `sts_dataset_facts.*`; with P-007 | 77.649% = 216,605/278,955 (Vt); median Δ 3.31e-6 (Vt); 96.27%, 93.37% (Vt); 56.86% (R); 55.51% (R; tracked `data/clip_artifact.json` → `clip_era.boundary_0p94_to_0p945_pct`) |
| `E1b.md` | E1b | MAJOR | +0.55 (sentences only +0.2) | E1a; C12 definition | quintile ranges, strip 78.39…4.98%, violation 21.54…14.21%, ρ_s −0.6 / −1.0 (R); 28.83% / 56.04% / 47.49% / 277,628 / 5 non-conv (R); **conditional 65.59 vs 68.90% (recomputed from parquet) and pre-registered P1/P3/falsifier (R; not in ledger — reverses the ledger's "halves ρ" reading)**; 2C histgb esc 2.8 ± 0.8 vs 59.1 ± 2.5 (R; passes); missed 8.25 ± 1.33 vs 1.89 ± 0.61 (R; passes) |
| `E1c.md` | E1c (+P-016) | MAJOR | +0.6 | owner commits `sts_limit_sweep.*`; optional d-figs relabel ("boundary mass in [L, L+q̂)" ≠ strip) | histgb 30.63 ± 2.51 @0.940, ridge 49.07 ± 2.66 (Vt d-figs); histgb 0.26–1.77% for L ≤ 0.936 (Vt); 5.46 @0.938, 19.44 @0.939 (R); ridge ≤ 3.23% only to L = 0.930 (Vt); ridge peak 51.43 @0.941 (calc; not distinguishable from 0.940); @0.950 ridge 1.38 ± 0.33, histgb 1.58 ± 1.19 (Vt; no difference); 95.71% violations @0.950 (Vt); 86/1,500 bases > 0.95 (R; no key) |
| `E2.md` | E2a, E2b, E2c, E3 (+C1) | MAJOR (E2c MINOR) | +0.62 (fold E3) / +0.97 (table) | owner commits `sts_crossnet_scatter.*`; legend code names (P-017) | 132 pts, r 0.8105 / log-log 0.9176 (Vt); case24-ridge median 0.3408, 9/9 < 0.5, r without 0.896 / 0.958 (Vt); A 0.4726 / B 0.4933 rel, A 0.1163 / B 0.1056 abs (R; B-vs-A fails std, std of abs errs 0.210 / 0.114); per-cell 2.111 / 0.194 / 0.322 / 0.101 / 0.047 / 0.061 (Vt); naive prior mean 0.1144 (Vt; re-derived 0.11439); case24 ridge pred 0.451 vs 0.217 (R); E3 BM 4.43/20.70/19.33%, histgb esc 3.72/17.19/7.84%, speedup 27.8 ± 5.1 / 5.85 ± 0.42 / 12.8 ± 0.8× (Vt plan); ridge esc 11.86/21.68/13.74% (R); t_solve imported from case118 (Vt) |
| `E4.md` | E4 (+C2) | MAJOR | +0.05 | headline rule decision | case30 histgb@0.97 5.84 ± 1.25, 0.76 ± 0.20 (5/5), 17.91 ± 3.71×; @0.96 4.86 ± 0.98, 0.91 ± 0.22 (2/5 under), 21.46 ± 4.51×; @0.90 38.63 ± 6.21× (Vt plan); ridge@0.98 37.83 ± 1.78, 0.51 ± 0.21, 2.65 ± 0.12×; ridge@0.97 29.70 ± 1.70, 1.05 ± 0.22, 3.38 ± 0.19× (R); case118 all-splits ridge 0.95 / histgb 0.98 (R); t_surr placeholder 1e-6 ms, t_solve 9.14 (R, D13); published case30 BM 20.01% (R) |
| `E5b-E15.md` | E5b (+E15 cut, +P-010 note) | MAJOR | −0.18 (+0.07 −0.25) | — | bound ≤ 1 − target; conditional ≤ 57.2% / 34.3% / 17.2% at 0.90/0.94/0.97 (Vt; recomputed); P(o > q̂ \| viol) 0.388 / 0.411 (R); missed @0.90 2.96 ± 0.44 / 4.72 ± 0.98 (R); S_mean 0.6038 ± 0.0757 / 0.7919 ± 0.0743 (R; cut) |
| `E6.md` | E6 (+C5), P-009 (+NS-04, P-026) | MAJOR | +0.23 (+0.45 optional figure) | headline decision; P-003 | **N2b (P-032) author decision**; classical MAE 3.77 ± 0.06, R² 0.12, esc 92.0 ± 0.5, missed 1.07 ± 0.22, 1.09 ± 0.01× (Vt plan); 0.0101 ms (R); dominance 9/9, 1/9 (Vt); PV/PQ MAE 0.00081 / 0.00482 (R); static k≈91 96.91 ± 0.49 vs 97.04 ± 0.44 (V; tie); k≈57 91.01 ± 2.00 (R, per-seed k) / 91.22 ± 0.55 (V, fixed k) vs 95.28 ± 0.98 (gate ahead); k = 138: 99.41 ± 0.16 vs 97.04 (V; static ahead); k = 89: 96.64 ± 0.50 vs 95.28 (V; static ahead); flag shares 25.1 / 17.2% (V); headline points flags-solved 99.92 ± 0.03 vs 99.21 (calc) and 99.71 ± 0.09 vs 99.17 (STS judge, re-read); escalation-budget k = 120 / 118 (nearest): 98.67 / 98.57 (calc; verifier-recomputed); train-mean 0.9398 (Vt) |
| `E8.md` | E8 | MAJOR | +0.14 | headline decision | **N2b (P-032) author decision**; cert-only ridge 1.35/1.12/1.08/1.04/1.01/1.00×, histgb 2.10/1.57/1.46/1.35/1.24/1.12× (Vt; Eq. 2 formula with per-split t_surr); certified 10.5 ± 2.7 / 19.1 ± 4.9% (R); false flags 11.0 ± 0.9 / 2.5 ± 0.3% (Vt); precision 56.1 ± 2.0 / 85.6 ± 1.4% (Vt); net 1.56 / 1.58× (R) |
| `E9.md` | E9 | MAJOR | +0.07 | **after N2 (landed)**; headline decision | **N2b (P-032) author decision**; ridge@0.94 384 misses, max 0.0324, p99 0.0152, 84.9% (Vt plan); histgb@0.97 404, max 0.0915, p99 0.0810, 73.8% (Vt); seeds 2, 3 (Vt); per-split maxima (R); corrected-label maxima 0.0682 (histgb) / 0.0516 (ridge) (new); 66.3% / 31.3% of misses flip (new) |
| `E10.md` | E10 | MAJOR | +0.2 (table +0.49) | — | 2C ridge 79.5 ± 1.8 vs 88.4 ± 2.7 (Vt; passes); histgb 89.6 ± 0.5 vs 90.3 ± 1.0 (Vt; fails); ridge missed 5.01 vs 2.02 (R; passes); 2D histgb 87.6 ± 1.0 vs 89.8 ± 1.0 (Vt; passes); ridge 89.3 vs 89.4 (Vt); 2E histgb 89.5/89.9 vs 89.8, ridge 89.5/89.5 vs 89.3 (Vt/R; null) |
| `E11.md` | E11 (+C10, N6 note, P-033) | MAJOR (C10 MINOR) | +0.1 | headline decision; optional N6 clause | 786,904 = 4,231 sweeps; 1,494,968 = 8,037 (Vt); histgb 772,851 = 4,155; 1,473,021 = 7,919 (Vt); saving 3.26 / 3.32 ms (R); 10 workers 5.40× (Vt); parallel basis mean 10.08 ms (R); N6 warm-start median time ratio 1.16 (time saving 13.7%: 9.25 → 7.98 ms), cold min 7.53 ms, 0 label diffs (new) |
| `E12-E13.md` | E12, E13 (+P-010) | MAJOR | +0.07 (+0.14) | owner commits `sts_e12_e13_conditional.*`, `sts_n1_predictions_long.parquet` | **N2b (P-032) author decision**; histgb@0.97 11.1 ± 2.6% of test bases with ≥ 1 miss (new = Vt STATS); ridge@0.94 7.7 ± 2.0% (new; passes vs histgb); @0.90 22.5 / 47.1% (new); max misses per base 13.2 / 11.8 (new); element min 57.5 / 55.7%, below-85% 18.1 / 23.5% vs 0.24% expected (new); base below-85% 8.7% vs 1.9% (new); cluster-SE ratio 7.0 / 5.6× (Vt, scratch only — not in artifact) |
| `E14.md` | E14 (+C9) | MAJOR | −0.9 | owner commits N4 artifacts | best MAE 0.00371 ± 0.00010 / 0.00153 ± 0.00011 (R); ridge +F1+F2 MAE 0.004161 ± 0.000247 vs 0.003754 ± 0.000133 (R; passes); esc 59.0 ± 2.9 vs 64.3 ± 2.8 (R; **passes — ledger says "within std": MISMATCH of reading**); missed 1.00 ± 0.37 vs 0.79 ± 0.21 (R; fails); F3/F4 186-row lookups (R); 118 pload + 118 qload (R); audit 25 bases, err 0.0 (R); N4 histgb paired real−shuffled MAE −1.8 ± 2.5e-5, 4/5 (new; fails); ridge +3.1 ± 2.8e-6 (new); histgb@0.97 missed 0.75 vs 0.82 (new; fails); ridge@0.90 missed paired −0.33 ± 0.04, 5/5, unpaired fails (new) |
| `C8.md` | C8 | MAJOR | 0 (+0.45 optional figure) | committed matched-escalation artifact before printing; P-003 | **N2b (P-032) author decision**; matched-escalation rows 25–74% from `data/sts_matched_escalation.json` (Vt; histgb safer 25–50%, tie 51–70%, ridge safer 71–73%, 74–75% incomplete); ridge MAE 11.6% below persistence (R); @0.96 0.14 ± 0.07 vs 1.36 ± 0.20 at 71.4 vs 57.0% esc (R); ridge ceiling 74.89% (R); corrected-label headline 0.46 ± 0.08 vs 1.14 ± 0.57 (new; passes) |
| `C13.md` | C13 | MAJOR | 0 | headline decision; P-003 | **N2b (P-032) author decision**; ridge@0.94 per split 0.60/0.62/1.15/0.92/0.68 (Vt); histgb@0.97 1.16/0.80/1.03/0.70/0.47 (Vt); upper bars 1.00 / 1.08 (Vt); ddof=1 1.03 / 1.11 (Vt); case30 5/5, 2/5 (R); corrected-label counts 0/5, 3/5 (new); **STATS-09 "1 of 5 at each point" MISMATCH for histgb (2 of 5)** |

## Totals (net counted pages, planning choices: option B, E1b with table, E2 folded, E10 sentences, no optional figures)

| | pp |
|---|---|
| Additions (P-003 0.2, P-007 0.07, E5 option B 0.21, E1a 0.03, E1b 0.55, E1c 0.6, E2 0.62, E4 0.05, E5b 0.07, E6+P-009 0.23, E8 0.14, E9 0.07, E10 0.2, E11 0.1, E12-E13 0.07) | +3.21 |
| Savings (E15 −0.25, E14 −0.9) | −1.15 |
| **Net for this file set** | **≈ +2.06 pp** |
| Range across choices | +1.57 (option A, E1b sentences only) to +3.67 (option B, E1b/E2/E10 tables, C8 + E6 figures, E12-E13 extra sentence) |

## Update after verifier pass 1 (`_verification_A.md`)
- P-003: consistency adds l.121, l.347 (82.64 / 74.89 / 82.79, label-dependent), l.107/l.349 ("above 0.94" vs 9 corrected N-0 bases).
- P-007: 41.2 → 41.4%; consistency adds l.107, l.349.
- Top5-1, E1b (and E1c): conditional share 65.59%, sourced as a recomputation from `data/unconditioned_base.parquet`.
- E6: escalation-budget histgb row k = 118 (nearest), 98.57 ± 0.30; rounding rule stated for every k.
- E8: histgb@0.95 certify-only 1.46 under the single stated formula (Eq. 2 with per-split t_surr); consistency adds l.199, l.292.
- C8: 11.6%; table re-sourced to `data/sts_matched_escalation.json` (20/63.7/64.3 rows dropped; 74% marked incomplete, no verdict).
- Non-blocking: Top5-2d-E5 §7 any-miss keys; E1a 13.1%; E11/index N6 wording; E1b 47.49% denominator; preregistration git-ignored note.

## Update after the lead's 2nd message
- Explicit **N2b (P-032)** dependency block added at the top of P-003, E9, C8, Top5-2d-E5, C13, E6, E8, E12-E13: each spec states what changes under (i) rebuild labels + re-run M2 vs (ii) keep pandapower labels + state N2 as a limitation.
- E1c and Top5-1 "must not claim" now exclude "the N-0 gate makes the concentration" and name the setpoint-floor test (N3-class) as the open causal question.
- E14: consistent-sign N4 gate differences are stated as not real under the std rule. E11 carries P-033.

## Cross-cutting findings for the lead
1. **N2 landed and confirms P-001**; P-003 drops from FATAL to MAJOR-with-mandatory-disclosure. Under corrected
   labels the headline changes asymmetrically (histgb@0.97 0.83 → 0.46%, passes std; ridge@0.94 0.79 → 1.14%,
   3/5 splits > 1%, fails std). This touches Top5-2d-E5, C8 and C13.
2. **Pre-registration conflict (E1b/Top5-1):** the author's own pre-registered decisive quantity (conditional strip
   share among non-violations) survives removing the N-0 gate (68.90 → 65.59%; falsifier < 50% not hit). The ledger's
   §6/D6 reading "removing the N-0 gate halves ρ ⇒ not a network property" is not supported as a causal test; the
   quintiles are the stronger evidence, and the setpoint floor is untested (N3).
3. **MISMATCHES:** P-007 "31.6% of strip rows at a PV bus holding its own setpoint" → 13.1% hold setpoint (31.6% are
   at that bus); E14 "+F1+F2 … within std" → the escalation change passes the std rule; STATS-09 "1 of 5 at each
   headline point" → histgb is 2 of 5 (ledger C13 is right).
4. **N1 artifact caveat:** row-pooled class-conditional forms do not hold their nominal α (histgb α = 0.10 →
   10.2% missed, 2/5 splits ≤ α); only the one-row-per-base-case form carries the guarantee; no form moves the
   frontier.
5. Fig. 3 (`data/miss_depth_v3.png`) prints "deepest miss 0.0915 pu" inside the image — the ledger's "q̂ marker
   only" note is incomplete; a regenerated figure is needed under P-001 Branch 1.
6. Untracked artifacts that the specs rely on (owner must commit before printing): `data/sts_dataset_facts.*`,
   `data/sts_limit_sweep.*`, `data/sts_crossnet_scatter.*`, `data/sts_n1_*`, `data/sts_n2_*`, `data/sts_n4_*`,
   `data/sts_n6_*`, `data/sts_e12_e13_conditional.*` and their `scripts/sts_*.py`. Matched-escalation (C8) and the
   1,016/1,500 and 86/1,500 counts have no committed key yet.
