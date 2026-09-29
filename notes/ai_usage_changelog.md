# AI usage changelog — STS panel review (2026-09-27 onward)

For the STS Appendix-4 AI-usage chart. One line per change: what the AI (Claude Code) DRAFTED and what it
VERIFIED. "Drafted" never includes report prose: report/ is author-only (hooks + GUIDE2027 rule 1).
Prompt: notes/ai-prompt-log.md, entry "2026-09-27 (b)".

| Date | Item | AI drafted | AI verified | Author action needed |
|---|---|---|---|---|
| 2026-09-27 | Prompt log | Appended the session prompt to notes/ai-prompt-log.md | — | none |
| 2026-09-27 | Page count | — | Counted pages = 16 from the Overleaf export "(39).pdf" (body pp. 3-18 numbered 1-16; title p1, abstract p2, refs pp. 19-20) | none |
| 2026-09-27 | P-004 Fig. 5 in Overleaf | — | Pixel diff of the 5 PDF-embedded images vs data/*.png: 4 identical; Fig. 5 differs — Overleaf copy is labeled 0-based (bus 75/52/106/0/20), repo PNG is IEEE (76/53/107/1/21) | Upload the corrected PNG to Overleaf |
| 2026-09-27 | Round-1 panels | Five AI reviewer reports (notes/panels/round1_*.md): feedback only, no replacement text | Numbers in findings marked VERIFIED/Reported per file | Read; decide |
| 2026-09-27 | Panel challenge round | Five challenge files + lead resolution record (notes/panels/round1_challenges_*.md, round1_disagreements.md) | Lead re-checked D1 (Fig. 5 pixel diff), D12 (URTC author block), D14 (static ranking vs gate from data/baselines.json) | Read; decide |
| 2026-09-27 | Ledger + work plan | notes/panel_ledger.md (110 rows; fix actions, owners, page costs; §6 claim-ceiling list — content only, no report text) | Still-present check of 33 prior-review anchors by grep; compliance checker run | Approve work plan; take author decisions in §5 |
| 2026-09-27 | E1a facts JSON | Code: scripts/sts_dataset_facts.py (AI-written) → data/sts_dataset_facts.json + manifest | d-figs: byte-reproducible rerun; values match number_check §2 recomputations | Commit if accepted; cite the AI-written script (App. 4) |
| 2026-09-27 | E1c limit-sweep figure | Code: scripts/sts_limit_sweep.py (AI-written) → data/sts_limit_sweep.png/.json | d-figs: L=0.940 row reproduces tradeoff_curve_v2; byte-reproducible | Decide whether to include; write caption |
| 2026-09-27 | E2a cross-network scatter | Code: scripts/sts_crossnet_scatter.py (AI-written) → data/sts_crossnet_scatter.png/.json | d-figs: 132 points, r values recomputed; byte-reproducible | Decide whether to include; write caption |
| 2026-09-27 | Fig. 5 prose-free | Code: scripts/sts_critical_bus_map.py (AI-written, logic copied from feasibility/domain_figure.py) → data/sts_critical_bus_map.png | d-figs: shares match frozen_v2 critical_bus_top5 | Upload to Overleaf; caption is yours |
| 2026-09-27 | Shared helper | Code: scripts/sts_manifest.py (AI-written; duplicates feasibility/manifest.py, ledger P-030) | — | Accept or ask to consolidate |
| 2026-09-27 | P-005 Fig. 2 with std bands | Code: scripts/sts_tradeoff_bands.py (AI-written) → data/sts_tradeoff_bands.png/.json | d-figs: byte-reproducible; same curves as tradeoff_hero_col_v2 | Decide whether to swap Fig. 2; caption must state the ±0.2 pp stds |
| 2026-09-27 | P-008 facts b | Code: scripts/sts_dataset_facts_b.py (AI-written) → data/sts_dataset_facts_b.json | d-figs: 56.8629 matches frozen; 61.61 / 14.06 match REPRO recomputation | Pick one reading of "within 0.005 pu" |
| 2026-09-27 | C8 matched escalation | Code: scripts/sts_matched_escalation.py (AI-written) → data/sts_matched_escalation.json | d-figs: std-rule verdict per grid point | Rewrite IV-B heading/claim yourself |
| 2026-09-27 | N2 Q-limit label audit | Code: scripts/sts_n2_label_audit.py, sts_n2_summary.py (AI-written; PV/PQ switch-back loop) → data/sts_n2_label_audit.parquet/.json | d-runs: exact RNG replay of all 280,455 rows; lead recomputed the flip counts and worst case from the parquet | Decide N2b (rebuild labels) vs state as limitation |
| 2026-09-27 | N1 class-conditional calibration | Code: scripts/sts_n1_class_conditional.py (AI-written) → data/sts_n1_class_conditional.json | d-runs: M2 refit reproduces tuned_metrics exactly | Decide whether to adopt as headline calibration |
| 2026-09-27 | N4 paired F1 shuffle | Code: scripts/sts_n4_f1_shuffle.py (AI-written) → data/sts_n4_f1_shuffle.json | d-runs: split 0 reproduces f1_leakage_audit check_4 | Use in ablation rewrite (E14) |
| 2026-09-27 | N6 warm-start timing | Code: scripts/sts_n6_warmstart_timing.py (AI-written) → data/sts_n6_warmstart_timing.json | d-runs: two runs agree; flags committed ms_solver mismatch (P-033) | Decide how to report solve time |
| 2026-09-27 | E12/E13 conditional coverage | Code: scripts/sts_e12_e13_conditional.py (AI-written) → data/sts_e12_e13_conditional.json | d-runs: matches STATS panel's 11.1% | Use in E13 sentence |
| 2026-09-27 | Fix specs set B | 17 spec files in notes/patches/ (content requirements, verified numbers, page costs; no replacement wording) | Spec B re-read every cited key; 9 mismatches logged in the ledger | Write the text yourself from each spec |
| 2026-09-27 | URTC/STS overlap check | notes/panels/urtc_overlap.md (lead script, inline) | 0 of 33 camera-ready-only sentences verbatim in STS; 4 near matches ≥0.8 listed | Decide cite / rewrite for the near matches |
| 2026-09-27 | Fix specs set A | 21 spec files in notes/patches/ (content requirements, verified numbers, page costs; no replacement wording) | Spec A re-read every cited key; all 91 quoted old-text passages match the .tex; 4 mismatches logged | Write the text yourself from each spec |
| 2026-09-27 | Fig. 3 without artifact annotation | Code: scripts/sts_miss_depth_noannot.py (AI-written) → data/sts_miss_depth_noannot.png | d-figs: byte-reproducible; same data as miss_depth_v3 | Swap the figure and rewrite its caption yourself |
| 2026-09-27 | Conditional strip-share recount | Code: scripts/sts_dataset_facts_c.py (AI-written) → data/sts_dataset_facts_c.json | d-figs: row counts; matches verifier A's 65.594% / 68.904% | Cite this file (not unconditioned_base.json) for 65.59% |
| 2026-09-27 | Number verification | notes/patches/_verification_A.md, _verification_B.md (AI verifiers) | Recomputed every spec number from row-level data; set A 21/21 signed off after one fix pass | — |
| 2026-09-27 | Verification pass 2 | — | Set A 21/21, set B 17/17 specs signed off; no spec failed twice | — |
| 2026-09-27 | N6 re-run (scratch only) | Scratch copy of scripts/sts_n6_warmstart_timing.py writing to the job tmp dir | Cold min 7.56 ms, warm-start saving ≈1.17×: reproduces the first run at lower load | Decide how to print solve time (AD-13) |
| 2026-09-27 | Report text | **Nothing drafted.** report/paper_current_STS.tex unchanged (sha256 c86e47d6…, mtime 13:49) | — | You write every change; specs are in notes/patches/ |
