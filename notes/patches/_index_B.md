# Fix-spec index B — clarity, minors, reproducibility, disclosure, cuts

Built 2026-09-27 by the fix-specification writer (set B). Every file is a **specification**, not prose:
anchors, old text, required content, verified numbers, must-not-claim, consistency, page cost. No
replacement wording anywhere. Nothing was written to `report/`; no git writes; `.venv/bin/python` only.
Status words: **re-read OK** (key re-read this session), **recomputed** (re-derived from committed/untracked
artifacts this session), **Reported** (read, not recomputed), **MISMATCH**, **NOT FOUND**.

Page costs are counted pages at the plan's unit costs — **not a compile** (no TeX toolchain). Confirm on
the next Overleaf export.

## Index

| ID | File | Sev. | Net pp | Dependencies | Numbers cited (status) |
|---|---|---|---|---|---|
| Top5-5 (+OS-1, OS-2, NS-03/19/20, STS-06/19) | `Top5-5.md` | MAJOR | +0.02 (abstract is on an uncounted page) | §5 headline operating point; title decision; P-001/P-003/N2; E1b, E2a, E4, E5, E8, P-009 in body first; C4; C12; P-018; P-028 | histgb@0.90 30.6±2.5 / 4.72±0.98 / 3.29±0.30 (OK); test-picked histgb@0.97 0.83±0.24, 63.7±5.1, 1.58±0.12, 2/5 >1% (OK); ridge@0.94 0.79±0.21, 64.3±2.8, 1.56±0.07 (OK); held-out histgb 1.15±0.27 (4/5 >1%), 59.3±4.0, 1.69±0.12; ridge 0.77±0.78, 65.4±8.1, 1.55±0.22 (recomputed); certify-only 1.24 / 1.12 (OK); BM 56.86 → 28.83 unconditioned (OK); case30 regen BM 7.09, 5.84±1.25 / 0.76±0.20 / 17.91±3.71 (recomputed); r 0.8105 / 0.9176 (OK, untracked); static ranking 99.41±0.16, 96.64±0.50 (OK) vs gate 97.04±0.44, 95.28±0.98 (lead-VERIFIED); N2 9.47% viol→safe (Reported, untracked) |
| C1 (+OS-7, NS-10b, STS-09) | `C1.md` | MINOR | 0 | Cut-5; P-018; P-015; P-011; E2a/E3 | 54 = 3×2×9 (OK); netstudy2 networks (OK); case57 0/3000 (OK); predictor-B prior sets (OK) |
| C4 (+NS-02, OS-4) | `C4.md` | MAJOR | +0.07 (+0.10 if the bound footnote is not shared with E5b) | Fig. 2 path B → d-figs/P-005; E5b; P-017 | 40 occurrences classified (S1 7, S2 3, S3 25, 2 unparseable, 3 other); histgb cov 89.8±1.0, missed 4.72±0.98; ridge 89.3±1.3, 2.96±0.44; viol 17.48; q̂ 0.0052/0.0023; P(o>q̂|viol) 0.388/0.411; bound ≤57.2% (all OK) |
| C6 (+OS-3, POWER-11, NS-16) | `C6.md` | MAJOR | 0 | P-017 (slack) | 374/1,500 = 24.93%; 69,532 rows; p = 0.30 non-slack; no redispatch (code l.142-144); `genon_*` features; rejection-by-status not computable (all OK) |
| C12 + P-014 | `C12.md` | MAJOR | +0.06 | §5 headline decision (picks floor definition F-a/F-b/F-c); OS-10 checker decision; E1b; E2a; P-017 | BM 56.86 / 28.83 / 7.09 / 20.01 (OK); strip 0.005 (OK); saturation 82.64±0.17 (mean OK, std computed, no key); ceilings 74.89±0.83 / 82.79±0.37 (OK); floor candidates 63.7±5.1 / 64.3±2.8 (OK), 59.3±4.0 / 65.4±8.1 (recomputed), 61.2±3.3 / 61.7±1.7 (OK, untracked); Mondrian 42.9±1.9 esc, 1.45±0.30 missed (recomputed) |
| P-002 + P-012 + §8-1 | `P-002-P-012-disclosure.md` | **FATAL** (AI) / MAJOR (program, URTC) | +0.10 to +0.15 if in report; ≈ +0.05 if STS says form field | 10 questions to STS staff (§E); author file-by-file code provenance (A2); URTC-body check (A6, C3) | prompt log 6,155 lines, first entry 2026-07-26 (OK); 33 model-tagged entries (OK); URTC authors (OK) |
| P-006 | `P-006.md` | MINOR | 0 | author choice A/B/C; Cut-2/P-004; P-005 | — (7 credit lines quoted; checker FAIL reproduced) |
| P-010 (+STS-20, NS-24; overlaps s-specA `E12-E13.md` — count the E12/E13 sentence once) | `P-010.md` | MAJOR | +0.05 | d-runs commits `sts_e12_e13_conditional.*`; C4; E5b; P-028 | 300 test bases/split; 55,787-55,792 test rows (OK); element share <0.85 at 0.90: 18.06±0.65 / 23.55±2.95 vs 0.24 expected (OK, untracked); base share <0.85: 8.67 vs 1.89 (OK); ≥1-miss bases histgb@0.97 11.13±2.57, ridge@0.94 7.67±2.03 (OK); cluster-SE 5.6-7.0× (**Reported, no key — not printable**) |
| P-011 (+P-031) | `P-011.md` | MAJOR | +0.05 (table +0.35, Cut-6 −0.30 inside; +0.15 with optional case30 column) | Cut-6; D15; P-001/P-003/N2; N6; owner commits `sts_dataset_facts.*`; R08 link placement; P-006 | solver NR/dc/numba/q-lims, tol 1e-8 default (OK); Python 3.13.9, pandapower 3.5.4, numpy 2.3.5, pandas 2.3.3, sklearn 1.7.2, pyarrow 21.0.0, numba 0.66.0, Matplotlib 3.11.1, igraph 1.0.0 (OK; manifest census 67 identical / 63 no-version / 1 partial / 4 sts, no differing version); sampler knobs from recorded command line (OK); counts (OK); splits/seeds 0-4 (OK); 15 ridge α; chosen configs (OK); histgb space max_depth none for the random draws, the pinned `committed` candidate has max_depth 8; **histgb candidates 26 (24 random + 2 fixed) — MISMATCH vs ledger "24 draws"**; t_solve 9.14 ms min of 400 (OK); Apple M5 (OK); N-0 pass 53.82% (1500/2787, run log only); 35.17 / 55.51 (OK); dataset build seed **NOT FOUND** |
| P-013 | `P-013.md` | MAJOR | +0.03 | §5 headline decision (+N1?); P-003/N2; C4 | inner ceiling 0.01 (OK); 1% of viol ≈ 0.17% of all (derived); crossings + per-split (OK); held-out 1.15±0.27 (recomputed); N1 δ=1% 0.98±0.26 / 1.07±0.28 (OK); ≥1-miss 11.13±2.57 (OK); N2 corrected 0.46±0.08 (Reported, audit-only, not printable); NERC no numeric limit (OK) |
| P-015 | `P-015.md` | MAJOR | −0.03 (drop promise) / +0.05 (report once) | P-018; C1; E4 | 111.83% (OK, `thermal_check.json`); published case30 BM 20.01, viol 28.81, @0.90 histgb 6.98±0.87 / 1.47±0.20 / 14.52±1.60, ridge 27.87±3.99 / 1.49±0.53 / 3.66±0.48; crossings histgb@0.93 0.98%/8.96%/11.27×, ridge@0.92 (OK; crossings have no stored ±) |
| P-017 | `P-017.md` | MAJOR (STS challenge: MINOR) | +0.13 | run after C4, C12, E14, E15, Cut-3, Cut-5, Cut-6, P-011 | 84 term rows; new collisions: "floor" (limit vs escalation), strip vs band-width window, seeds vs splits, variables vs hyperparameters (all re-read OK) |
| P-018 … P-027 | `minors_P-018_P-027.md` | MINOR | +0.06 (P-021's −0.1 counted inside Cut-5) | C1; N2; Cut-5; E5; C13; P-001; P-004; P-006; Cut-2; E15; E8; C4; P-017; P-010; E14; P-028; Top5-5 | case30 = PYPOWER "Washington 30 Bus Dynamic Test Case" (OK); islanding 9/186 (OK, no key); non-converged 45 = 37/7/1 (OK), **flagged 37–39 — MISMATCH vs ledger 38–39**; certified: histgb@0.90 2/45 every seed, ridge@0.90 seed 1 and histgb@0.97 seed 3 1/45 each, in the test split (corrected after verifier pass 1); case57 0.9012/24, 0.7199/39 (OK); ± = ddof 0 (OK); 74/55/26.7/21.4 pooled, 78.6% (OK); PowerNorm γ 0.5 (OK); baseline rows (OK); **ridge MAE 11.6% below persistence — MISMATCH vs ledger "~10%"**; overvoltage 73.136% (OK, no key); audit 25 / 0.0 / 0 (OK) |
| P-028 | `P-028.md` | MINOR | 0 | author full-text re-read; `prior-art.md` §6.6 update; blocks Top5-5 contribution list and P-010 contrast sentence | none printed; lit-note values Reported, not printable |
| numbers-2b (2b-1..6, 2c-1..4, P-008, E2c, OS-5/8/9, "locked tes") | `numbers-2b.md` | MINOR | 0 (+0.03 optional 2b-6 footnote) | P-005; E5; C12; Cut-2/P-004; owner commits | **MISMATCH** 1.07→1.08 and 1.0→1.00 (l.231); 55.5→55.51 (l.121); 56.9→56.86 (l.323); 27.1→27.10 (l.314, l.339); **std-rule FAIL** 2b-5 ceiling 82.79±0.37 vs saturation 82.64±0.17; **std-rule FAIL** E2c A 0.1163±0.2097 vs B 0.1056±0.1145; 2c-1..4 and P-008 re-read OK but keys untracked (`sts_dataset_facts.json`, `sts_dataset_facts_b.json`); t_surr 0.00116/0.00241 OK, re-measure 0.00346 (OK); "locked tes" confirmed |
| checker-phrases (OS-6, OS-10) | `checker-phrases.md` | MINOR | 0 | C12/P-014 option; Cut-7; 2b-5 | `\bprove[sn]?\b` fires l.361, `escalation floor` fires l.365 (reproduced); neither catches l.314 "proved", l.367 "proof", l.312/l.388 "floor"; no recorded rationale (patterns added 2026-08-03, prompt log l.1333) |
| cuts (Cut-3, -5, -6, -7, -8, Cut-2) | `cuts.md` | — | Cut-3 −0.40; Cut-5 −0.30; Cut-6 −0.30 (**counted in P-011**); Cut-7 −0.35 net; Cut-8 −0.25 (only after the P-001 figure rebuild); Cut-2 −0.50 or 0 | bibitem count if tsybakov2004/mammen1999 (Cut-3) or desalvo2015/angelopoulos2024/cortes2016 (Cut-7) drop; P-021; P-010; P-028; P-001; P-004/P-025 | citation map by line (OK); case57 values (via minors, OK) |

## Net page cost (set B)
| Group | pp |
|---|---|
| Additions and rewrites (Top5-5, C1, C4, C6, C12, disclosure mid +0.12, P-006, P-010, P-011+Cut-6, P-013, P-015 option A, P-017, minors, P-028, numbers-2b, checker) | **≈ +0.56** |
| Cuts excluding Cut-6 (Cut-3, Cut-5, Cut-7, Cut-8) | **−1.30** |
| **Net, Fig. 5 kept** | **≈ −0.74** |
| **Net, Fig. 5 cut (Cut-2)** | **≈ −1.24** |
| Net if Cut-8 is not taken, Fig. 5 kept | ≈ −0.49 |

Ranges: disclosure +0.10…+0.15; P-015 −0.03…+0.05; C4 +0.07…+0.10; P-011 +0.05…+0.15. Worst case
(all high, Fig. 5 kept, no Cut-8) ≈ −0.30 pp. Set B frees pages under every combination.

## Dependencies that gate many items (resolve first)
1. **§5 headline operating point** (test-picked / held-out / N1) → Top5-5, C12 floor value, P-013, C4
   numbers, P-023.
2. **P-001 / P-003 / N2** → Top5-5 label caveat, P-013, Cut-8 (Fig. 3 rebuild), P-024. N2 has finished
   (`data/sts_n2_label_audit.json`: 4,615/48,749 = 9.47% of stored violations flip to safe; 2,162
   safe→violation; worst case 0.8485 → 0.94507; corrected BM 56.22%) — **ledger §4 still says
   "pending"**; lead should update after review (values here are Reported, untracked).
3. **STS staff answers** (disclosure §E Q1-Q10) → P-002 severity and placement.
4. **OS-10 checker decision** → C12 wording of "floor".
5. **Owner commits** of untracked keys cited here: `data/sts_dataset_facts{,_b}.*`,
   `data/sts_e12_e13_conditional.*`, `data/sts_n1_class_conditional.*`, `data/sts_crossnet_scatter.*`,
   `data/sts_n2_label_audit.*` and their `scripts/sts_*.py` (all AI-written — disclosure A2).

## MISMATCH / flags found in this set
- **P-011:** ledger P-011 says "24 histgb draws"; code evaluates 26 candidates per seed (24 random + 2
  fixed).
- **P-011 (wording only, not a data mismatch):** the code's N-0 rule is ≥ 0.94, while l.119 says
  "above 0.94". The data agree with the prose (raw minimum 0.940000036; no base sits at exactly 0.94).
  The reproducibility table should state the rule as coded.
- **P-011:** the dataset-build random seed is NOT FOUND; `measure_solve.py` times solves on default-knob
  bases, not the recorded dataset settings; networkx unpinned in `requirements.txt`.
- **numbers-2b:** 5 printed-vs-source mismatches (1.07, 1.0, 55.5, 56.9, 27.1) and 2 std-rule failures
  (2b-5 "above"; E2c "slightly better"). E2c detail: A has the smaller absolute error in 42 of 54
  comparisons; B's lower mean comes from the 9 case24-ridge cells.
- **minors:** P-020 flagged range 37–39 (ledger 38–39); P-027b ridge-vs-persistence MAE gap 11.6%
  (ledger ~10%).
- **C12:** a second case118 "saturation" value exists (`case30_frozen.json` →
  `case118_comparators.saturation_point_pct` = 82.52, all rows) beside 82.64 (test splits); the JSON key
  for 82.64 is named `perfect_model_floor_saturation` — cite the value, not the key's word.
- **Disclosure — evidence status:** all of `notes/` is git-ignored (`.gitignore:23`, "Private — never
  commit to the public fork"). None of these is in git: the prompt log, `contribution-log.md`, both
  agent-drafted reference drafts (`1_research_draft_ORIGINAL.txt`, `1_research_draft_ORIGINAL_rev2.txt`),
  the retired 2026-08-17 draft, `ai_usage_changelog.md`, and `sts-constraints.yaml`. The logbook has no
  commit history (corrected after verifier pass 1; disclosure §F).
- **Disclosure:** no record of which pre-2026-07-26 code (the core `feasibility/` pipeline) was
  AI-generated; AI applied text edits to the URTC camera-ready (2026-09-13) while the STS body is declared
  verbatim from URTC; an agent-drafted reference paper (2026-07-21) exists; Kalita appeared as co-author on
  a pre-URTC draft and was removed. All four are author facts to establish, not spec-writer conclusions.
- Out of scope, noted: `scripts/check_compliance.py` l.11 font floor 10 pt vs R06 11 pt (P-006 fork);
  Fig. 3 PNG embeds "deepest miss 0.0915 pu" in the image (for the P-001 owner).
