# Panel ledger — STS 2027 report (`report/paper_current_STS.tex`)

**Built:** 2026-09-27 by the lead (Claude Code), from round-1 blind panels (`notes/panels/round1_*.md`,
challenges `round1_challenges_*.md`, resolutions `round1_disagreements.md`) reconciled with
`notes/sts_review.md` (09-23), `notes/placement_plan.md` and `notes/number_check.md` (09-27).
`notes/claude_ai_draft_edits.tex` does not exist.

**Paper state checked:** working tree, 460 lines, unchanged since the 09-27 number check. Every
prior-review anchor was re-found by text (`grep -c`, §Commands C3); **all are still present** — nothing
from the 09-23 review has been fixed yet. Compiled state: Overleaf export
`~/Downloads/Conformal Gated Surrogate Screening (39).pdf` (2026-09-27 13:50, 1 min after the .tex save;
text matches), **16 counted pages** (body pp. 3-18, folios 1-16; title p1, abstract p2, refs pp. 19-20).

**Scope boundary (project rules override the prompt).** `report/` is author-only (hooks
`guard_report_prose.sh`, `guard_report_bash.sh`; STS GUIDE2027 rule 1; RULES2027 App. 4 via
`sts-constraints.yaml` R04/R22/R27). The lead therefore makes **no edits to the .tex**, and "patches"
are fix *specifications* (anchor, old text, what must change, verified numbers, page cost) — no
replacement prose. No git writes (CLAUDE.md §8); commit commands for the owner are at the end.

**Evidence convention** (from `notes/sts_review.md`): **VERIFIED** = the lead recomputed it (command in
§Commands); **VERIFIED (teammate)** = a named teammate recomputed it and the lead has not (= "Reported"
from the lead's seat, pending the Phase-3 verifier); **Reported** = read from a file/manifest without
recomputation; **unverified**.

**NEW** in the ID column = found by the round-1 panels (or the lead) and **absent from the prior
review/number check**. These are the reason this run exists.

---

## 0. Summary

| | Count |
|---|---|
| Ledger rows (§1 tables, counted by awk) | 110 |
| FATAL | 2 distinct issues (P-001 = C11; P-002). P-003 downgraded to MAJOR-with-mandatory-disclosure after N2 |
| MAJOR | 47 rows |
| Rows marked NEW vs prior review | 29 |
| Prior-review items still present in .tex | all (0 fixed) |
| Prior-review items the panels disagree with | 9 (§3) |
| Author decisions | 14 (§5, AD-1…AD-14) |
| Fix specs | 38 (set A 21, set B 17), all SIGNED OFF by independent verifiers |
| Edits made to the .tex | **0** (author-only; see Scope boundary) |

**FATAL items (submission blockers): P-001, P-002; P-003 is now MAJOR with mandatory disclosure:**
1. **P-001** — the featured worst miss (0.8485 pu, 0.0915 below the limit; printed at l.292, Fig. 3
   caption l.303, l.367) is a solver artifact: pandapower's one-way PV→PQ switching leaves gen 21 (IEEE 54)
   at its *absorbing* limit 0.106 pu below setpoint; two independently written back-off loops re-solve
   it to 0.94507 (not a violation). The paper's "reaches the limit of reactive power … collapse"
   mechanism is the opposite of what `data/miss_mechanism.json` records.
2. **P-002** — no generative-AI disclosure anywhere in the report (RULES2027 App. 4 requires naming the
   AI-generated code portions + a prompt log). Treat as blocker until STS confirms a form field suffices.
3. **P-003** — label trust, **confirmed at full scale by N2** (§4; counts VERIFIED by the lead): under a
   consistent PV/PQ switch-back re-solve, 4,615 of 48,749 violation labels (9.47%) flip to safe and 2,162
   safe labels flip to violation (violation rate 17.48% → 16.60%). 66% of the misses at histgb@0.97 are
   artifact labels, and the corrected-label missed rates reverse the model ordering at the operating
   points (histgb 0.46%, ridge 1.14%, no retraining) — P-032. The printed range 0.7179-0.9603, the
   miss-depth tail (Fig. 3), S_mean, and every missed-rate comparison rest on the pandapower labels.
   Whether to rebuild (N2b) is an author decision.

---

## 1. Ledger

Columns: ID · Source(s) · Present in .tex? · Severity · Evidence · Action · Page cost (counted pp) · Owner.
Owners: **author** (prose, the only person who may edit the .tex) · **d-figs** / **d-runs** (data
teammates; new files only) · **verifier** · **lead** · **author-decision**.

### 1a. FATAL and correctness

| ID | Source(s) | Present? | Sev. | Evidence | Action | pp | Owner |
|---|---|---|---|---|---|---|---|
| **P-001 NEW (upgrade of PS-M2 / C11)** | POWER-01, REPRO-01, STS; review Top-5 #4, PS-M2, C11; plan E9b | yes (l.292, l.303, l.367) | **FATAL** | VERIFIED (teammate ×2): `tmp/panel_power/a3.py,a4.py,pvpq.py,c1.py`; `tmp/panel_repro/t5-t8.py` → back-off min_vm 0.94507 = N-0 min of scenario 101000025. Reported: `data/miss_mechanism.json` → `part1_mechanism.saturated_gens_near_weak_bus_post_outage` (gen 21 `at_min: true`, q = −194.71 = Q_min, V 0.8485 vs setpoint 0.9549); `data/qlims_off_check.json` (no-limits solve 0.9390). Full-set confirmation: N2 (running). | revise: remove the collapse mechanism (l.367), the "worst miss" sentence (l.292) and the Fig. 3 caption's deepest-miss clause (l.303) or rebuild them on a validated case; disclose the one-way Q-limit convention as a modelling limitation; frame as the second self-found artifact (like the clip bug). Figure: **`miss_depth_v3.png` itself prints "deepest miss 0.0915 pu" (spec A) → Fig. 3 must be regenerated** (d-figs, new file). N2 confirms: 0.848543 → 0.945073. | ≈0 (rewrite) | author (+ d-runs N2) |
| **P-002** | STS-01, NS-01; review §8; `sts-constraints` R04/R20/R22 | yes (l.393, Acknowledgments has no AI line) | **FATAL** | VERIFIED: `grep -n -i -E "generative\|claude\|chatgpt\|\bAI\b\|artificial" report/paper_current_STS.tex` → only l.101 (Alcántara) and a bib title. HEAD version also has none (`git show HEAD:report/paper_current_STS.tex`); R04 note quotes an older "used to validate the code and grammar" line that is gone. | author-decision: add a disclosure naming the AI tools, which code portions were AI-generated/assisted, AI review/verification use (incl. this panel), and the prompt log (`notes/ai-prompt-log.md`); confirm with STS where it goes. | +0.1 | author-decision |
| **P-003 NEW (upgrade of review N2 "unverified")** | POWER-02, REPRO-01; review §4 PS-M2 ("share unverified"), N2 | yes (l.119 range; Fig. 3; l.189 S_mean; l.292) | **MAJOR, disclosure mandatory** (was FATAL until N2; N2 shows the strip is robust 56.86 → 56.22% and the violation rate moves 17.48 → 16.60%, but the missed-rate headline and model ordering are label-dependent — P-032) | VERIFIED (teammate ×2, agree to <1e-4 pu on shared rows): pooled 20/200 = 10% viol→safe; 4/400 = 1% safe→viol; 97% of solves leave ≥1 gen pinned on the wrong side of setpoint; the 40 deepest rows stay violations but rise by median +0.12 pu; dataset min 0.7179 → 0.929; boundary strip 58.7% → 57.0% in sample (robust). Needs: N2 full audit + an independent solver on a sample (not available locally — unverified). | run-new-analysis (N2, authorized, running) → then revise: caveat or relabel the range, the tail, Fig. 3, S_mean; state the headline missed rates are measured against pandapower labels. | +0.1 | d-runs → author |
| **P-004 NEW (number_check §5 said "consistent")** | NS-09, STS-12, REPRO-13 (challenge); lead | yes (Overleaf PDF) | MAJOR | VERIFIED: `pdfimages -png` of the Overleaf export; pixel diff vs `data/*.png`: Figs. 1-4 max diff 0; Fig. 5 differs on 0.022% of pixels = the labels (Overleaf copy reads bus 75/52/106/0/20; repo PNG reads 76/53/107/1/21). | fix in Overleaf: upload `data/sts_critical_bus_map.png` (prose-free, IEEE labels 76/53/107, d-figs) and point `\includegraphics` at it; then re-check every figure in the next export. Caption: mention bus 1 (8.45%) or not — author (d-figs flag 4). Credit line should name every program used (STS-12: igraph layout) — author. | 0 | author |
| **P-005 NEW** | REPRO-02, STS-07, NS-08 | yes (l.231 "as Fig.~\ref{fig:tradeoff} shows", l.281 caption) | MAJOR | VERIFIED (teammate ×3): `data/tradeoff_hero_col_v2.png` draws mean curves only; `grep fill_between\|errorbar feasibility/paper_hero.py` → none; `*_std` keys exist in `data/tradeoff_curve_v2.json`. | run-new-analysis (d-figs: new prose-free Fig. 2 with ±1 std bands, `data/sts_tradeoff_bands.png` + manifest) OR author removes the error-bar clause from caption and text. | 0 | d-figs → author |
| P-006 NEW | lead (check_compliance run) | n/a (checker) | MINOR | VERIFIED: `.venv/bin/python scripts/check_compliance.py` → R10/R21 FAIL "7 of 7 floats carry no APA line"; the regex (`\\apacite\|APA:\|\(\d{4}\)\.`) does not accept the rule book's own example form ("Graph created by the student researcher using BioRender, 2024."). All 7 floats carry "created by Rajan Saha using …, 2026" (l.158, 223, 265, 284, 306, 327, 342). | author-decision: widen the checker regex (lead did NOT edit the gate) or switch lines to APA form. Compliance audit also found three stale checker spots: font floor 10 pt (row says 11), R09 still "ask", R04 PASS only tests that the hooks exist. Coverage counts for C4: 26 uses — conformal sense 7, acceptance-rate sense 2, target knob 17. | 0 | author-decision |

### 1b. Top-5 of the prior review

| ID | Source(s) | Present? | Sev. | Evidence | Action | pp | Owner |
|---|---|---|---|---|---|---|---|
| Top-5 #1 | review; POWER-03, STATS-07, STS-03/04, NS-06 | yes (l.63 title, l.121 "inherent", l.365, l.388) | MAJOR (prior: FATAL — see §3 D-a) | VERIFIED (d-figs, `data/sts_dataset_facts.json`): 77.649% of N-1 rows within 0.001 pu of their N-0 min; median |Δ| 3.31e-6; 96.27% of strip rows from bases with N-0 min < 0.945; 93.37% same weakest bus; 31.62% at IEEE 76. Reported: `data/unconditioned_base.json` → 28.83% (vs 56.86%); `data/quintile_boundary_mass.json` 78.4/81.3/82.4/37.3/4.98%. **NEW sub-finding P-007** below. | revise (causal wording: "set by the sampler × limit on case118", not a network property) + add (E1a/E1b); title = author-decision (§5). | see E1 | author |
| **P-007 NEW** | POWER-03(a,b,d,e) | yes (unstated) | MAJOR | VERIFIED (teammate): `feasibility/generate_dataset.py` `GEN_VM_LO = 0.94 = VMIN_LIMIT`; 67.7% of the 1,500 accepted bases already have N-0 min in [0.94, 0.945) (also STS: 1,016/1,500); ~~31.6% of strip rows are at a PV bus holding its own sampled setpoint~~ **corrected (spec A, re-read of the parquet): 13.09% of strip rows sit at bus 76 within 1e-4 pu of its setpoint; 31.6% is only the share whose minimum is at bus 76.** Provisional (40 bases, 1 seed): floor 0.95 → strip 67.3% → 37.0%. case30 schedules every unit at 1.00 pu, so no PV bus can sit at 0.94. | add one sentence to Method (setpoint floor equals the limit) + revise case118-vs-case30 causal reading; the floor-0.95 rebuild = N3-class, **author approval needed** (§4). | +0.07 | author |
| Top-5 #2 (a) Theory definitional | review ST-F1; STATS-08, STS-10, NS-15 | yes (l.165-190, l.181 "structural property") | MINOR (prior: FATAL — §3 D-b) | Reported: `data/barrier_height.json` → `identity_checks.max_identity_gap` 5.6e-17. | revise: retitle/shorten; keep the ceiling/saturation reasoning (l.347-349); if Eq. 4 stays, carry it to P(certify ∧ violation) ≤ α. | −0.2 | author |
| Top-5 #2 (b) "must" floor refuted | review; STS-06; E7 | yes (l.101, l.388) | MAJOR | Reported (plan E7, VERIFIED 09-27): Mondrian histgb@0.97 42.9±1.9% esc, 1.45±0.30% missed vs global histgb@0.96 57.0%, 1.36%. | revise "must"; E7 rows optional (needs `vovk2003mondrian` bibitem: prior-art §9.6 "verified, NOT inserted"). | 0 / +0.15 | author |
| Top-5 #2 (c) missed rate unguaranteed | review; STATS-03 | yes (l.128, l.132) | MAJOR | VERIFIED (teammate): bound P(certify ∧ viol) ≤ α ⇒ conditional ≤ 0.10/0.1748 ≈ 57% at 0.90, ≤ 17% at 0.97; Reported `data/barrier_height.json` → P(o > q̂ \| viol) 0.388/0.411. | add (E5b, one sentence in words; the numeric bound in a footnote per NS challenge). | +0.07 | author |
| Top-5 #2 (d) operating point picked on test | review ST-F2; STATS-01 | yes (l.81, l.231, l.349, l.388) | MAJOR (prior: FATAL) | VERIFIED (teammate STATS, and plan E5): held-out (inner-chosen) targets histgb [0.96,0.97,0.97,0.96,0.96] → test missed **1.15 ± 0.27%**, 4/5 seeds > 1%, esc 59.3 ± 4.0%, speedup 1.69 ± 0.12×; ridge 0.77 ± 0.78% (seed max 2.24), esc 65.4 ± 8.1%. Test-picked histgb@0.97: 2/5 seeds > 1% (1.162, 1.032). | author-decision (headline operating point, §5); then revise abstract/IV-A/IV-C/conclusion (E5a/E5c). | +0.2 | author-decision |
| Top-5 #3 | review | yes (none of E1-E11 in paper; `grep quintile\|unconditioned\|Mondrian` → 0) | MAJOR | see E-rows | add per §2 order | see E | author |
| Top-5 #4 | review; POWER-05, STATS-06, NS-04 | yes | MAJOR | VERIFIED (teammate POWER, matches plan E8): flagged-also-solved speedup histgb@0.97 1.24 ± 0.07×, ridge@0.94 1.12 ± 0.03×; ridge flag precision 56.1%, false flags 11.0% of all; histgb 85.6%, 2.5%. | add (E8, E11) + revise l.109 | see E8/E11 | author |
| Top-5 #5 | review; NS-03, STS-06, STS-19, NS-02 | yes (l.81 ends "informed decision"; l.101; no "hypothes*" in file) | MAJOR | VERIFIED: `grep -c -i hypothes report/paper_current_STS.tex` → 0; "boundary mass" appears only in title + l.353. | revise abstract/intro: question → mechanism → honest headline → when it pays → why it matters (content only; **§6 framing proposal**). Define "boundary mass" at first use. | ≈0 | author |

### 1c. Review §3 contradictions C1-C13

| ID | Present? | Sev. | Evidence / panel view | Action | pp | Owner |
|---|---|---|---|---|---|---|
| C1 network count | yes (l.355 "five networks in total") | MINOR | NS-10b, STS-09: reader counts 7 | revise (inventory once in Method) | 0 | author |
| C2 different "safe" rules per network | yes (l.365 "All five splits…") | MAJOR | REPRO-07, STATS-01: case30 mean-rule crossing 0.96 (0.91 ± 0.22%, 4.86% esc); case118 ridge 0.95 / histgb 0.98 under all-splits | revise (one rule; tie to §5 headline decision) | 0 | author |
| C3 "must be a floor" | yes (l.101, l.388) | MAJOR | as Top-5 #2(b) | revise | 0 | author |
| C4 coverage two meanings | yes (l.128 vs l.231) | MAJOR (NS: three senses; NS/STATS-12 raised to MAJOR) | NS-02 | revise: one word per concept incl. Fig. 2 axis "target coverage" vs caption "safety target"; one sentence linking target → coverage → missed rate | +0.07 | author |
| C5 classical screens "no numerical minimum voltage" | yes (l.109) | MAJOR | POWER-06, STS-08; Reported `data/classical_screen_metrics.json` (MAE 0.00377, R² 0.117) | revise l.109 + E6 | see E6 | author |
| C6 "two elements out" vs "still N-1" | yes (l.111, l.367) | MAJOR (NS-16) | POWER-11: 374/1,500 bases, 69,532 rows | revise (one definition in Method; no redispatch between outages) | 0 | author |
| C7 "inherent characteristic" | yes (l.121) | MAJOR | as Top-5 #1 / P-007 | revise (E1a) | +0.03 | author |
| C8 "faster is not safer" axis | yes (l.290 heading, l.292) | MAJOR | VERIFIED (teammate STATS, REPRO; D-c): matched escalation — histgb safer 30-50% (e.g. 30%: 4.79 ± 1.09 vs 6.99 ± 0.48), tie 55-70% incl. 64% operating point (0.79 ± 0.21 vs 0.83 ± 0.24), ridge safer ≥ ~72% | revise heading + claim to the matched-escalation result; optional risk-vs-escalation panel (d-figs, from `data/tuned_metrics.json` sweeps) | 0 / +0.45 | author (+ d-figs) |
| C9 "total demand is concealed" | yes (l.371) | MAJOR (false claim) | review; 118 `pload_*` features sum to total demand | remove (E14) | − | author |
| C10 "true end-to-end cost" | yes (l.99) | MINOR | break-even excludes generation/training/search | revise (E11b) | 0 | author |
| C11 worst-miss mechanism | yes (l.367) | **FATAL** | → P-001 | revise | 0 | author |
| C12 "boundary mass" undefined | yes (l.63, l.81) | MAJOR | NS-03, NS-13 | revise (define once at first use) | +0.03 | author |
| C13 abstract error bars vs per-seed exceedances | yes (l.81, l.349) | MAJOR | REPRO-06, STATS-09: 1/5 ridge (1.146), 2/5 histgb (1.162, 1.032) seeds > 1% at the test-picked points | revise ("k of 5 splits" for case118 as for case30) | 0 | author |

### 1d. Review §2b mismatches and §2c no-source numbers

| ID | Present? | Sev. | Evidence | Action | Owner |
|---|---|---|---|---|---|
| 2b-1 "1.0–1.07%" | yes (l.231) | MINOR | VERIFIED (teammate ×3): 0.8322 + 0.2447 = 1.0769 → **1.08** | revise | author |
| 2b-2 55.5 vs 56.86 | yes (l.121) | MINOR | source 55.51 | revise precision | author |
| 2b-3 56.86 vs 56.9 | yes (l.323 caption) | MINOR | same key | revise | author |
| 2b-4 27.1 / 16.81 / 9.31 | yes (l.314, l.339) | MINOR | VERIFIED (d-figs): 27.0961 / 16.8084 / 9.3080 → print 27.10 | revise | author |
| 2b-5 ceiling "just above" saturation | yes (l.347) | MINOR (std rule) | 82.79 ± 0.37 vs 82.64 ± 0.17 | revise to "at" | author |
| 2b-6 t_surr histgb 0.00241 vs re-measure 0.00346 | yes (l.147) | MINOR | matches committed key; re-measure in `data/break_even.json` | optional footnote | author |
| 2c-1..4 (750/750; 0.9009-1.2310; 43.91%; 0.8156-1.4083; 0.5% below 0.87) | yes | MINOR | **now sourced**: VERIFIED (d-figs) `data/sts_dataset_facts.json` (+ manifest, byte-reproducible). Untracked until the owner commits it (REPRO-10). | owner commits `data/sts_dataset_facts.*`, `scripts/sts_dataset_facts.py` | d-figs → owner |
| 2c-5 (0.000247, 0.004161) | yes (l.375) | — | traceable to `data/physics_ablation.json` records (number_check §6) | none | — |
| P-008 NEW | REPRO-10 | yes (l.314 "most … within 0.005 pu"; l.314/323 tallest bin 14.1%) | MINOR | recomputes (61.61%; 14.063%) but no tracked key | d-figs: add both keys to a new facts JSON (Phase 3) | d-figs |

### 1e. E-items (review §6a, plan Part C)

| ID | Present? | Sev. | Evidence (numbers) | Action | pp | Owner |
|---|---|---|---|---|---|---|
| E1a 77.6% sentence | not in paper | MAJOR | VERIFIED (d-figs) `data/sts_dataset_facts.json`: 77.649% (key now exists) | add (replaces "inherent" sentence) | +0.03 | author |
| E1b quintile table + unconditioned + 2C | not in paper | MAJOR | Reported `data/quintile_boundary_mass.json`, `data/unconditioned_base.json` (unconditional 28.83%, 56.04% violations, 47.49% of unfiltered bases < 0.94; **conditional 68.90% gated vs 65.58% ungated**); 2C histgb esc 2.8 ± 0.8% vs 59.1 ± 2.5% | add; **corrected (D16): lead with the quintiles; report the unconditioned build as the pre-registered test with its conditional result (not a halving)** | +0.55 | author |
| E1c limit-sweep figure | not in paper | MAJOR | VERIFIED (d-figs) `data/sts_limit_sweep.{png,json}`: histgb 30.63 ± 2.51% at L=0.940, 1.58 ± 1.19% at 0.950, 0.26-1.77% for L ≤ 0.936; ridge 49.07 ± 2.66% at 0.940 (reproduces tradeoff_curve_v2). **Caveats:** (i) D6 — near-tautological as a causal test; use it to show the spike sits exactly at the N-0 acceptance value; (ii) ridge has no flat region below the limit (≤ 3.23% only up to L = 0.930); (iii) low escalation above 0.94 is not a usable operating point — 95.71% of test rows are violations at L = 0.950 (all flagged); (iv) 0.950 ridge vs histgb fails the std rule. | add figure + 2 sentences (content per caveats); replaces "I use 0.94 pu as a conservative choice" block (NS-11) | +0.6 | author |
| E2a ρ·q̂ scatter | not in paper | MAJOR | VERIFIED (d-figs) `data/sts_crossnet_scatter.{png,json}`: 132 points, r = 0.8105, log-log r = 0.9176; case24 ridge median ratio 0.3408 (9/9 points < 0.5); without it r = 0.896 / 0.958. **Temper per STATS-07:** effectively n = 3 target networks; predictor A's abs error 0.1163 is no better than a naive prior-network mean 0.1144 (VERIFIED teammate STATS). | add figure; caption names the case24-ridge failure; state n | +0.45 | author |
| E2b per-cell errors | not in paper ("I only report the average errors") | MAJOR | case24 ridge 2.111, histgb 0.194; case39 ridge 0.322, histgb 0.101; illinois200 0.047 / 0.061 (plan E2, D4) | revise | +0.1 | author |
| E2c "slightly better on absolute error" | yes (l.353) | MINOR | std rule fails (0.011 vs ≥ 0.11) | revise to no-difference | 0 | author |
| E3 3 extra networks | not in paper | MAJOR | plan E3 (VERIFIED 09-27): BM 4.43 / 20.70 / 19.33%; histgb esc@0.90 3.72 / 17.19 / 7.84%; speedups use case118 t_solve | add (fold into E2a caption or small table; drop table first if short) | +0.42 | author |
| E4 case30 speedup | not in paper | MAJOR | plan E4 / NS-12 / STS-05: histgb@0.97 17.91 ± 3.71×; @0.96 21.46 ± 4.51×; case30 ridge crossing 0.98 (37.8%, 2.65×) → model order reverses on case30 (report as observation, D7). **Caveat (REPRO challenge, D13):** case30 runs use a placeholder t_surr = 1e-6 ms, so every case30 speedup is exactly 1/escalation — a printed 17.9× must say so. | add | +0.05 | author |
| E5 held-out headline | not in paper | MAJOR | see Top-5 #2(d) | author-decision → add | +0.21 | author-decision |
| E5b vs **E15 overlap** | — | — | **Decision (lead): keep E5b** (the guarantee statement belongs where the guarantee is stated, III-C; STATS-03). **E15 becomes a cut**: delete S_mean (D5/D7; S_p99 replacement is oracle-dependent under P-003). | E5b add; E15 cut | +0.07 / −0.25 | author |
| E6 classical screen row | not in paper | MAJOR | plan E6: esc 92.0 ± 0.5%, missed 1.07 ± 0.22%, 1.09 ± 0.01×, MAE 3.77 ± 0.06e-3, R² 0.12; conformal ridge dominates 9/9, histgb 1/9 | add row + revise l.109. **Must be paired with P-009** (static ranking beats the gate) so the baseline story is not one-sided. | +0.13 | author |
| E7 Mondrian | not in paper | MAJOR | plan E7 table; compare at matched missed | add sentences (needs bibitem) or skip | +0.15 | author |
| E8 certify-only speedup + false flags | not in paper | MAJOR | see Top-5 #4 | add column + 2 sentences; NS-04: caption says train-mean flags every case (VERIFIED teammate: mean min_vm 0.93983 < 0.94) | +0.14 | author |
| E9 miss depth at recommended points | not in paper | MAJOR | plan E9: ridge@0.94 max 0.0324 pu; histgb@0.97 max 0.0915 (**= the P-001 artifact case**) | revise **after N2**; E9 values depend on labels | +0.07 | author (after N2) |
| E10 drift 2C/2D/2E | not in paper | MAJOR (project RQ1) | plan E10: 2C ridge 79.5 ± 1.8 vs 88.4 ± 2.7; histgb 89.6 vs 90.3; 2D histgb 87.6 ± 1.0 vs 89.8 ± 1.0; 2E null | add (sentences first; table if room) | +0.2/0.49 | author |
| E11 break-even + parallel | not in paper | MAJOR | plan E11: ridge@0.94 786,904 contingencies = 4,231 sweeps (gen only), 8,037 incl. training; histgb@0.97 4,155 / 7,919; 10 workers 5.40× | add | +0.1 | author |
| E12/E13 conditional coverage | not in paper | MAJOR (STATS-04) | **Decision: run** (refit, no solves; authorized as analysis of existing data) — d-runs task 5 (running). Panel (STATS, VERIFIED teammate): 11.1 ± 2.6% of test base cases contain ≥ 1 missed violation at histgb@0.97; cluster SE 5.6-7.0× i.i.d. | add (one sentence + number) | +0.07 | d-runs → author |
| E14 ablation rewrite | yes (l.369-379) | MAJOR | **Do not cut to nothing** (prompt; STS lists the permutation control + leakage audit as own thinking). Keep: (a) audit shows F1 uses only pre-outage data (`data/f1_leakage_audit.json` check_2: 25 scenarios, max err 0.0); (b) shuffle control — single seed **unless N4** (running) supplies 5-seed paired differences; (c) gate metrics not only MAE (ridge +F1+F2 MAE +10.82% yet esc@0.94 64.3 → 59.0% — **this drop passes the std rule, 5.3 > 2.85 (spec A correction)** — while missed 0.79 → 1.00 ± 0.37 is within std); (d) F3/F4 null by construction (186-row lookups keyed by outaged element). Delete "total demand is concealed" (C9). | revise ~460 → ~150-200 words | −0.9 | author (+ d-runs N4) |
| E15 | — | — | see E5b row | cut S_mean | −0.25 | author |

### 1f. New runs (review §6b)

| ID | Status | Sev. | Notes | Owner |
|---|---|---|---|---|
| N1 class-conditional / risk control | **authorized, running** | MAJOR (ST-F2) | STATS panel check (VERIFIED teammate): violation-conditional δ = 1% → histgb 0.98 ± 0.26% missed at 61.2 ± 3.3% esc; ridge 1.07 ± 0.28% at 61.7 ± 1.7% — same frontier, but a nominal guarantee on the headline metric and no test scanning. d-runs will produce the committed artifact. | d-runs |
| N2 Q-limit label audit | **authorized, running (first)** | FATAL-linked (P-001, P-003) | full ~48.8k violation rows + back-off re-solve | d-runs |
| N3 realistic-margin resample | **propose only** | — | subsumes STS revised "single change": 2×2 rebuild (setpoint floor 0.94/0.95 × N-0 gate on/off), 5 seeds | author-decision |
| N4 paired 5-seed F1 shuffle | **authorized, running** | MINOR | | d-runs |
| N5 stronger learned baselines (violation classifier, CQR) | not in the prompt's authorized or propose lists → **treated as author-decision** | MAJOR-adjacent | P-009 (static ranking) is the more damaging missing baseline and is already on disk | author-decision |
| N6 warm-start timing | **authorized, running** | MINOR | | d-runs |
| N7 N-2 shift test | **propose only** | — | project RQ1; 2D is a partial proxy | author-decision |
| N8 larger network | **propose only** | — | | author-decision |

### 1g. NEW panel findings not covered above

| ID | Source(s) | Present? | Sev. | Evidence | Action | pp | Owner |
|---|---|---|---|---|---|---|---|
| **P-009 NEW** | STS (challenge), STATS-05; D14 | not in paper | MAJOR | **VERIFIED** (§Commands C5), `data/baselines.json`: static training-frequency ranking vs gate at 0.90 — escalate-only budget: 96.91 ± 0.49 vs 97.04 ± 0.44 (tie; gate escalate-only capture 15.96%). Flagged cases also solved (k ≈ 138 ridge / 89 histgb): static **99.41 ± 0.16 vs 97.04 ± 0.44** (ridge), **96.64 ± 0.50 vs 95.28 ± 0.98** (histgb) — static wins beyond the std. Caveat: labels (P-003); element-concentration caveat (STATS challenge). | add (Table I row or one sentence); this is a headline-level negative and must not be buried | +0.1 | author |
| P-010 NEW | STATS-04 | not in paper | MAJOR | cluster-bootstrap SE 5.6-7.0× binomial (**no committed key — cannot be printed until a script + JSON exist**); exchangeable unit is the base case; l.132 misstates the condition as "a single-element outage" | revise l.132 and l.363 (STS-20: separate grouping from marginal-vs-conditional) | +0.05 | author |
| P-011 NEW | REPRO-05 | not in paper | MAJOR | solver settings (NR, init dc, numba, enforce_q_lims), versions (pandapower 3.5.4, sklearn 1.7.2, Python 3.13), sampler knobs (setpoint ±0.025 with floor 0.94, Q-limit scale U(0.6,1.4), pf U(0.9,1.15), regional ±10%), search space (15 ridge α logspace(−3,4); **26 histgb candidates per seed = 24 random + 2 fixed** — spec B correction), chosen configs, repo link; `data/dataset.manifest.json` is retroactive | add one compact reproducibility table (NS challenge: table, not prose). Spec B flagged l.119 "above 0.94" vs code `< 0.94` reject; **verifier B: the raw minimum is 0.940000036, so "above 0.94" is literally true of the data** (only the code wording is ≥) — no change needed. The dataset-build RNG seed is NOT FOUND in any manifest. | +0.35 | author |
| **P-012 NEW** | NS (open Q), STS (challenge); lead D12 | not in paper | MAJOR | VERIFIED: `paper_current_URTC_20260808.tex` authors Rajan Saha (first) + Eugene Pinsky (BU); STS .tex header l.3 "Body text is VERBATIM from the URTC conference version". R18 → acknowledge the published paper; R27 → adults may not supply replacement text. | author-decision (acknowledge URTC + co-author; confirm no co-author-written text remains). **Also (spec B, lead-verified):** `notes/ai-prompt-log.md` 2026-09-13 records an AI session that applied text edits to the URTC camera-ready. Lead overlap check (`notes/panels/urtc_overlap.md`): of 33 sentences new in the camera-ready (upper bound on AI+human edits), **0 appear verbatim in the STS body**; 4 are ≥ 0.8 similar and 12 ≥ 0.6 (listed). App. 4 allows post-draft refinement only with explicit citation + log. Other facts spec B found for the disclosure (P-002 file): prompt log starts 2026-07-26 (no record for earlier core-pipeline code); an agent-drafted reference paper exists (07-21); Kalita was a co-author on a pre-URTC draft. | +0.05 | author-decision |
| P-013 NEW | STS-11, POWER-05 | yes (l.349) | MAJOR | 1% target never justified; N-1 planning checks every contingency | revise (state it as the operator's chosen parameter, or cite a criterion — no verified source in prior-art) | +0.03 | author |
| P-014 NEW | NS-14 | yes (l.312 heading; l.388) | MAJOR | the "floor" never has a number; section gives ceilings + saturation | revise (define the floor once with ±) | +0.03 | author |
| P-015 NEW | NS-12 | yes (l.119 "discussed in Section V") | MAJOR | published-case30 numbers promised, never given (`data/case30_frozen.json`: BM 20.01%) | revise (report or drop the promise) | 0 | author |
| P-016 NEW | NS-11; d-figs flag 2 | yes (l.365) | MAJOR | at L = 0.95 escalation is low because almost everything is a violation and is flagged (95.71% test violations at L = 0.950, `data/sts_limit_sweep.json`); coverage target 0.90 unstated; only ridge quoted | revise (fold into E1c) | 0 | author |
| P-017 NEW | NS-13 (60 terms), review §4c (≈20) | yes | MAJOR | e.g. y never defined; Fig. 3 "Y", "q̂@0.90"; indicator; MVA, slack, reactive power, Independent/Regional; code identifiers in prose | revise (define at first use; drop code names) | +0.2 | author |
| P-018 NEW | POWER-08 | yes (l.81, l.119) | MINOR | pandapower `case30` = PYPOWER "Washington 30 Bus Dynamic Test Case"; IEEE 30-bus PF case is `case_ieee30` | revise name + source | 0 | author |
| P-019 NEW | POWER-09 | yes (unstated) | MINOR | 9/186 outages island buses; `np.nanmin` over energized buses labels them "safe" | revise (one sentence) | +0.03 | author |
| P-020 | POWER-10; review PS minor | yes (l.119) | MINOR | 37/45 non-converged = trafo idx 0 (IEEE 8-5); gate flags 37-39 (spec B correction) (`data/nonconverged_gate.json`) | revise | +0.03 | author |
| P-021 | POWER-07; review PS-M7 | yes (l.353) | MINOR | case57 at load × 0 → 0.9012 pu = broken model data (VERIFIED teammate) | revise reason; keep exclusion | −0.1 | author |
| P-022 NEW | POWER-12 | yes (l.107) | MINOR | a branch outage adds no load; it redistributes flow and raises I²X losses | revise | 0 | author |
| P-023 NEW | STATS-09 | yes | MINOR | ± is population std over 5 re-splits of one dataset (not SE/CI); abstract numbers lack ± | revise captions + abstract | 0 | author |
| P-024 NEW | REPRO-09 | yes (l.292, l.303) | MINOR | 74/55% and 26.7/21.4% are pooled over splits and use different thresholds | revise | 0 | author |
| P-025 NEW | REPRO-11 | yes | MINOR | Fig. 5 PowerNorm colourbar undisclosed; stale manifest `manuscript_role`; stale .tex comments l.297-298, l.317-318; Fig. 3 shaded strip unexplained; `barrier_height.manifest.json` hyperparameters null | revise captions/comments; manifest fixes = new files only | 0 | author / d-figs |
| P-026 NEW | REPRO-12 | yes (Table I) | MINOR | persistence/train-mean rows from `data/screener_metrics.json` (committed v1 pipeline; model-free, same splits) | revise caption | 0 | author |
| P-027 NEW | NS-17, NS-18, NS-20, NS-21, NS-22, NS-23, NS-24, STS-14 | yes | MINOR | direction cues; "accurately" (ridge MAE 11.6% below persistence — spec B); abstract vs intro prior-work categories; Fig. 1/3 glyphs; Table 2 skips 0.91-0.93; forward refs; unparseable sentences l.107, l.167, l.363, l.377 | revise | 0 | author |
| P-028 NEW | STS-16; review §5 | yes (l.101) | MINOR | `notes/prior-art.md` §6.6: manoharan2026 record rests on a 07-19 HTML skim, re-read before citing; intro doesn't say it is thermal-only | author re-reads source; lead does not fill citation fields | 0 | author |
| P-029 NEW | STS-17, POWER-13 | yes (l.147) | MINOR | base solve for `vm0_*` features not charged (~0.5% amortized); t_solve cold-start (N6 running) | revise (one clause) | 0 | author |
| P-030 NEW | lead | n/a | MINOR | `scripts/sts_manifest.py` duplicates `feasibility/manifest.py` | cleanup later (reuse existing helper) | 0 | d-figs |
| P-031 NEW | REPRO (open Q) | n/a | MINOR | N-0 gate pass rate 53.82% only in a run log; clip-era parquet gitignored (35.17%, 55.5% not reproducible from git) | disclose in the reproducibility table (P-011) | 0 | author |
| **P-032 NEW** | d-runs N2 | yes (every missed-rate number) | MAJOR | see §4 N2: under switch-back labels (no retraining) histgb@0.97 missed 0.46% vs ridge@0.94 1.14% — the "which model is safer" conclusions depend on the solver artifact; 66% of histgb misses at 0.97 are artifact labels | **author-decision (N2b):** rebuild labels with PV/PQ switch-back and re-run the M2 pipeline (no new sampling; re-solve cost already paid by N2; changes every headline number and the pinned-solver rule in CLAUDE.md §5) — OR keep pandapower labels and state they are the oracle, with the N2 audit numbers as a limitation. Propose only. | +0.1 (limitation) | author-decision |
| **P-033 NEW** | d-runs N6 | yes (l.147 "9.14 ms, min of 400") | MINOR | VERIFIED (teammate): N6 cold min 7.53 ms over 12 bases × 186 vs committed 9.14 ms (min over ~2-3 bases, different generator config); medians agree (9.25 vs 9.51). Speedup ≈ 1/escalation, so ratios barely move. | investigate before printing any absolute time; say "median" or give both; mention warm start ≈1.16× | 0 | author |
| typo "locked tes" | review §4c, NS-26, STS-09 | yes (l.353) | MINOR | VERIFIED `grep -n "locked tes"` | revise (grammar-only; author) | 0 | author |

### 1h. Review §7 cuts and placement-plan "Other sentences"

| ID | Present? | Panel view | Decision | pp | Owner |
|---|---|---|---|---|---|
| Cut-1 ablation → 2-3 sentences | yes | **overridden** by the prompt and STS/NS (permutation control + audit are "own thinking") | shrink to ~150-200 words (E14), not to nothing | −0.9 | author |
| Cut-2 Fig. 5 | yes | NS: referenced once, not used; nobody protects it | **author-decision** (it is a figure, not a result; if kept, use `data/sts_critical_bus_map.png`) | −0.5 | author-decision |
| Cut-3 reject-option digression (l.314) | yes | NS: interrupts mechanism | cut to one sentence + cites | −0.4 | author |
| Cut-4 ceiling paragraph + S_mean | yes | POWER protects ceiling/saturation reasoning (D5) | **keep the ceiling/saturation sentence(s), cut S_mean** (E15) | −0.25 | author |
| Cut-5 case57/pegase detail | yes | POWER-07 | cut to one sentence with the corrected reason | −0.3 | author |
| Cut-6 dataset wall of numbers (l.119) | yes | NS | move numbers into the P-011 table | −0.3 | author |
| Cut-7 Discussion l.361-363 merge | yes | — | merge with related work | −0.4 | author |
| Cut-8 shrink Fig. 3 | yes | — | only if short | −0.25 | author |
| OS-1 abstract last sentence | yes (l.81) | Top-5 #5 | revise | 0 | author |
| OS-2 "three distinct ways" / scope as contribution | yes (l.101) | NS-19, STS-06 | revise | 0 | author |
| OS-3 two elements vs N-1 | yes | C6 | revise | 0 | author |
| OS-4 "coverage is the acceptance rate" | yes | C4 | revise | 0 | author |
| OS-5 "just above the saturation point" | yes | 2b-5 | revise | 0 | author |
| OS-6 "proven methods" (checker banned phrase) | yes (l.361) | — | revise | 0 | author |
| OS-7 "Future work … more networks" | yes (l.388) | C1 | revise | 0 | author |
| OS-8 56.9 caption | yes | 2b-3 | revise | 0 | author |
| OS-9 1.07 → 1.08 | yes | 2b-1 | revise | 0 | author |
| OS-10 "escalation floor" (checker banned phrase) | yes (l.365) | — | revise | 0 | author |

### 1i. Review §8 compliance

| ID | Present? | Sev. | Action | Owner |
|---|---|---|---|---|
| §8-1 Acknowledgments (paid program, named instructors/TFs, AI) | yes (l.393) | FATAL (AI part = P-002) / MAJOR (program, people: STS-02) | author-decision | author-decision |
| §8-2 links | fixed (only bib URL) | — | none | — |
| §8-3 spacing comment stale (header says `\onehalfspacing`, file uses `\setstretch{1.5}`) | yes | MINOR | revise comment | author |
| §8-4 prompt log | this run's prompt appended (`notes/ai-prompt-log.md` 2026-09-27 (b)) | — | none | — |

---

## 2. Ordered work plan

Budget: 16 counted pages now, 4 free. Running totals use the plan's unit costs (not a compile).

**Step 1 — correctness and FATAL (blocks everything else).**
1. N2 label audit (running) → confirm P-001 / P-003 at full scale.
2. P-001: remove/rebuild the deepest-miss story (3 places). ≈0 pp.
3. P-002 + §8-1 + P-012: disclosures (author-decision). +0.15 pp.
4. P-004: re-upload Fig. 5 (`data/sts_critical_bus_map.png`); re-export; lead re-runs the pixel diff. 0 pp.
5. P-005: Fig. 2 bands (d-figs builds `data/sts_tradeoff_bands.png`) or drop the error-bar clause. 0 pp.
6. Typo "locked tes", 1.08, 56.86, 55.51, 27.10, "at" saturation, "slightly better" (2b rows, E2c, OS rows). 0 pp.
   *Running: +0.15.*

**Step 2 — results already on disk** (E1 → E2/E3 → E5 → E8 → E6/E7 → E9-E11, E14, E15).
- E1a (+0.03), E1b led by unconditioned (+0.55), E1c (+0.6, replaces 0.95 block) → +1.18 → *1.33*
- E2a (+0.45), E2b (+0.1), E3 folded into E2a caption (+0.07) → *1.95*
- E5 per the headline decision (+0.21), E5b (+0.07) → *2.23*
- E8 column + sentences (+0.14), **P-009 static ranking** (+0.1) → *2.47*
- E6 row + l.109 (+0.13), E7 skip unless bibitem inserted (0) → *2.60*
- E9 after N2 (+0.07), E10 sentences (+0.2), E11 (+0.1), E4 (+0.05) → *3.02*
- E14 (−0.9), E15 cut S_mean (−0.25) → *1.87*

**Step 3 — new runs.** N2 (first), then N1 (+0.1 if it becomes the headline calibration, one table row),
N4 (feeds E14, 0), N6 (one clause, 0), E12/E13 (+0.07). → *2.04*

**Step 4 — page cuts to stay ≤ 20.** Cut-3 (−0.4), Cut-5 (−0.3), Cut-6 → P-011 table (−0.3 +0.35),
Cut-7 (−0.4); Fig. 5 author-decision (−0.5 if cut). → *≈0.9-1.4 of 4 free* (projected; **must be
confirmed by an Overleaf compile** — no TeX toolchain here).

**CORRECTION (compliance audit, `notes/panels/compliance_round1.md` §4):** the unit costs above use 345
words/page; the Overleaf PDF measures ≈ 440 words per full text page (p4 452, p14 432, p15 443). So cuts
save less (E14 ≈ −0.63 not −0.9; Cut-3 and Cut-5 ≈ −0.2 each) and the two new figures are portrait and
cost more (E1c ≈ 0.70, E2a ≈ 0.68). p18 has 0.42 pp free. **Corrected projection: ≈ 18 counted pages,
range 17-19.5** (moderate confidence; main risk is float placement — p13 is already float-only and
E1b/E1c/E2a land next to it). The steps' own rows sum to +0.99 (+0.49 with Fig. 5 cut), not the
"0.9-1.4" range quoted above. If a compile lands above 19, drop in this order: E10 table → E3 table
(fold into E2a caption) → Fig. 5 → E1b quintile table (keep the unconditioned sentence).

**Step 5 — prose and clarity.** Top-5 #5 framing (§6), C4 coverage vocabulary, C12/P-014 definitions,
P-017 blocking terms, P-027 minors, P-010/P-023 statistics wording. ≈ +0.3.

---

## 3. Prior-review items the panels disagree with

| # | Prior position | Panel position | Reasoning / resolution |
|---|---|---|---|
| D-a | Top-5 #1 FATAL ("removing the N-0 filter halves boundary mass") | MAJOR (all 4 panels) — but review AND panels misread the unconditioned build (D16) | The *measurement* (56.86% strip, escalation = mass in band) is robust, even under relabelling (57.0% in sample). What fails is the causal reading. MAJOR, and the title is an author decision. The panels add a more direct cause the review missed: the **setpoint floor equals the limit** (P-007). |
| D-b | Top-5 #2 "Theory definitional" FATAL | MINOR (STATS-08, STS-10, NS-15) | Definitional ≠ wrong; it wastes space. The operating-point leak (STATS-01) is the real MAJOR. |
| D-c | C8: ridge vs histgb "indistinguishable at matched escalation" | STATS/REPRO: histgb **safer** at 30-50% escalation | The review only checked ~50% and ~64%; the full matched-escalation curve shows histgb safer at low budgets, tie at the operating point, ridge safer ≥ 72%. |
| D-d | E1: limit sweep as the mechanism figure | Near-tautological (STATS, POWER; D6) | Keep the figure for *location* of the spike. **Corrected (D16):** do NOT lead with "the unconditioned build halves the mass" as causal evidence — the author's pre-registered conditional test shows the N-0 gate does not create the concentration. Lead with inheritance (77.6%) + N-0-margin quintiles; report the pre-registered unconditioned test with its conditional result; the setpoint-floor manipulation (N3-class) is the open causal test. |
| D-e | E2: "turns the identity into a tested law" | n = 3 networks; A no better than a naive prior-network mean on absolute error (STATS-07) | Report it as a partial success with a named failure mode, not a law. |
| D-f | §5 novelty: "the gate is shown to beat a classical conformalized screen" | P-009: a static ranking beats the gate once flags are solved | Keep E6, but the baseline story must include P-009. |
| D-g | §7 cut the ablation to 2-3 sentences | STS/NS protect the permutation control + audit; prompt forbids cutting to nothing | ~150-200 words (E14). |
| D-h | number_check §5 "Fig. 5 consistent" | stale 0-based copy in Overleaf (P-004) | Checked the repo file, not the compiled PDF. |
| D-i | PS-M2 "share of affected labels unverified" | ~10% of violations, ~1% of safe rows flip (provisional) | Upgraded to FATAL-linked P-003 pending N2. |

---

## 4. New-run results (filled as runs finish)

| Run | Artifact | Result | Status |
|---|---|---|---|
| N2 | `data/sts_n2_label_audit.{parquet,json}` | **Confirms P-001/P-003 at full scale.** Cause in pandapower `_run_ac_pf_with_qlims_enforced` (one-way PV→PQ). Replay exact (280,455 rows, diff 0.0). 93.6% of N-1 rows have ≥1 inconsistent gen (median effect ~1e-16; 47,142 rows move > 1e-3 pu; 4,281 > 1e-2). Violations 48,749 (17.476%) → 46,295 (16.596%); 4,615 viol→safe (9.47%); 2,162 safe→viol. Worst case 0.848543 → **0.945073** (IEEE 27, 2 passes). Corrected dataset min 0.8077 (not 0.929 — that was a 40-row sample). Missed cases: histgb@0.97 268/404 (66%) flip to safe; ridge@0.94 120/384 (31%). Corrected-label missed rate without retraining: histgb@0.97 0.83% → 0.46%; ridge@0.94 0.79% → 1.14% (**model ordering at the operating point flips**). Deepest corrected miss 0.8845 pu. 9/1,500 bases would fail the N-0 gate. | counts **VERIFIED (lead, §Commands C8)**; missed-case mapping VERIFIED (teammate d-runs); d-runs reports 46,296 corrected violations vs lead 46,295 (1-row difference, likely the 1 non-converged row) |
| N1 | `data/sts_n1_class_conditional.json` | Literal violation-conditional band is extremely conservative (ridge certifies ≈0%). Usable form (threshold on violation-row predictions): histgb α=0.01 missed 0.98 ± 0.26%, esc 61.2 ± 3.3%, 1.63× (1.27× flags solved); ridge 1.07 ± 0.28%, 61.7 ± 1.7%. **Same frontier** as the global-q̂ gate at matched missed (|Δesc| ≤ 0.0017): it picks a point and attaches a bound, it does not improve the curve. Row-pooled forms lack the textbook guarantee (base case is the exchangeable unit); group-level forms reported. | VERIFIED (teammate d-runs; matches STATS panel check) |
| N4 | `data/sts_n4_f1_shuffle.json` | 5-seed paired, real − shuffled F1 MAE: ridge +3.1e-6 ± 2.8e-6; histgb −1.8e-5 ± 2.5e-5 → no MAE gain. Four gate metrics have a consistent sign in 5/5 splits (e.g. ridge missed@0.90 −0.0033 ± 0.0004) but each is below the between-split std → not real under the std rule (reporting the sign = author call). | VERIFIED (teammate d-runs; split 0 reproduces check_4 exactly) |
| N6 | `data/sts_n6_warmstart_timing.json` | 12 bases × 186 outages: cold min 7.53 / median 9.25 ms; warm min 6.38 / median 7.98 ms; full sweep 1,731 vs 1,492 ms (≈1.16×); identical results. **Flag P-033:** cold min 7.53 ms < committed `ms_solver` 9.14 ms (medians agree: 9.25 vs 9.51). The first run was under heavy load (load avg 48.7/86.9). **Lead re-ran the same script from a scratch copy (output to job tmp only; repo artifact untouched) at load ≈ 4: cold min 7.56 / median 10.34 ms; warm min 6.52 / median 8.91 ms; sweep 1,966 vs 1,682 ms (≈1.17×).** The ≈7.5 ms cold minimum and the ≈1.16-1.17× warm-start saving reproduce; medians are load-sensitive. The committed 9.14 ms min is the outlier (different base set / generator config per d-runs); speedup ratios are insensitive because t_surr ≪ t_solve. | VERIFIED (teammate d-runs); re-run VERIFIED (lead) |
| E12/E13 | `data/sts_e12_e13_conditional.json` | Target 0.90: per-element min coverage 0.575 (ridge) / 0.557 (histgb); 18% / 24% of 186 elements below 0.85 (≈0.24% expected from binomial noise). Per base case min coverage ≈ 0.09. Test bases with ≥1 missed violation: **7.7 ± 2.0% (ridge@0.94), 11.1 ± 2.6% (histgb@0.97)**; every test base has ≥1 violation. | VERIFIED (teammate d-runs; matches STATS panel) |
| E1a facts | `data/sts_dataset_facts.json` | done (above) | VERIFIED (d-figs, byte-reproducible) |
| E1c | `data/sts_limit_sweep.{png,json}` | done | VERIFIED (d-figs) |
| E2a | `data/sts_crossnet_scatter.{png,json}` | done | VERIFIED (d-figs) |
| Fig. 5 | `data/sts_critical_bus_map.png` | done | VERIFIED (d-figs) |
| P-005 Fig. 2 bands | `data/sts_tradeoff_bands.{png,json}` | done; bands readable at 0.6\textwidth but the missed band near 1% is ≈ ±0.2 pp (thin) → state the stds in the caption/text; lower missed band clipped at 0 | VERIFIED (d-figs, byte-reproducible) |
| P-008 facts | `data/sts_dataset_facts_b.json` | [0.94,0.945) 56.8629%; two-sided ±0.005 of 0.94 = 61.6103%; tallest 0.001 bin [0.940,0.941) = 14.0628% (39,229 rows). l.314 "most" holds either way — pick one reading, don't mix | VERIFIED (d-figs) |
| C8 matched escalation | `data/sts_matched_escalation.json` | histgb safer 25-50%, tie 51-70% (both operating points ≈64% fall here), ridge safer 71-73%; boundaries knife-edge under the std rule (50%: 0.64 vs 0.62; 70%: 0.18 vs 0.21) | VERIFIED (d-figs) |
| Fig. 3 no-annotation | `data/sts_miss_depth_noannot.png` | done; same data/bins/q̂ lines as miss_depth_v3; "deepest miss 0.0915 pu" text, arrow and red triangles removed; the bin containing the artifact case is still drawn (labels uncorrected pending N2b) | VERIFIED (d-figs, byte-reproducible) |

---

## 4b. Spec sets (Phase 3)

- Set A (`notes/patches/_index_A.md`): 21 specs; net ≈ +2.06 pp (range +1.57 to +3.67) under option B, E1b with table, E3 folded, E10 sentences only. All 91 quoted old-text passages match the .tex verbatim.
- Set B (`notes/patches/_index_B.md`): 16 specs; net ≈ −0.74 pp (−1.24 with Fig. 5 cut; worst case −0.30).
- **Combined ≈ +1.3 pp by plan units → ≈ 17.3 counted pages; with the compliance audit's density/float correction ≈ 17.5-18.5.** Needs an Overleaf compile to confirm.
- Under corrected labels (N2, no retraining): histgb@0.97 missed 0.83 → 0.46 ± 0.08% (0/5 splits > 1%; change passes the std rule); ridge@0.94 0.79 → 1.14 ± 0.57% (3/5 splits > 1%; change within std).

## 4c. Verification (Phase 3 gate)

- Set A (`notes/patches/_verification_A.md`): 209 rows — 200 MATCH, 3 MISMATCH, 3 ROUNDING, 3 NOT FOUND (all "do not print"); 0 STD-FAIL on a claimed comparison. **Signed off 14**; rejected 7 (P-003, P-007, Top5-1, E1b, E6, E8, C8) → returned to spec A (pass 2 pending).
- Set B (`notes/patches/_verification_B.md`): 242 MATCH, 3 MISMATCH, 3 NOT FOUND; 0 STD-FAIL on a claimed comparison. **Signed off 15**; rejected 2 (P-002-P-012-disclosure, minors_P-018_P-027) → returned to spec B (pass 2 pending).
- **Pass 2 (after one fix round each): set A 21/21 SIGNED OFF, set B 17/17 SIGNED OFF. No spec failed verification twice.** Every number in every spec is recomputed from row-level data by an agent that did not write the spec.
- Remaining non-blocking notes: quote a single R22 chart row in the disclosure spec §F (the current ellipsis joins two rows); P-011 should say "no manifest records a differing version" rather than a census count (the count drifts as files are added); the C8 crossover points (50%, 71%) pass the std rule by < 0.01 pp — do not lean on them; **CLAUDE.md §7 says root CLAUDE.md is tracked, but `.gitignore:24` ignores it** (doc/code conflict for the owner, CLAUDE.md §8 "flag any file that disagrees").
- Verifier notes carried into rows: conditional strip share is 65.59% (key 65.5823 computed from rounded inputs); N6 ran under heavy machine load (load avg 48.7/86.9) → absolute times suspect, re-run on an idle machine; `notes/` (incl. `preregistration.md`, the prompt log) is git-ignored by design, so the pre-registration's only timestamp is its mtime (2026-09-09 20:40).

## 5. Author decisions — options and recommendation

| # | Decision | Options | Recommendation |
|---|---|---|---|
| AD-1 | **Headline operating point** (Top5-2d-E5 spec) | A: keep test-picked 0.94 / 0.97 (0.79 / 0.83% missed, 64 / 64% esc). B: held-out inner-chosen (histgb 1.15 ± 0.27% missed, 4/5 splits > 1%, 59.3 ± 4.0% esc, 1.69 ± 0.12×). C: N1 violation-conditional at α = 1% (histgb 0.98 ± 0.26% at 61.2 ± 3.3%, 1.63×; same frontier, bound attached; only the one-row-per-base form carries the guarantee). | **B as the headline**, with C as one row/sentence showing a principled selector lands on the same curve. Decide together with AD-2: under corrected labels option A's ridge point fails on 3/5 splits. |
| AD-2 | **N2b: labels** (P-003, P-032) | (i) Relabel with N2's switch-back values (already computed for every row), drop/keep the 9 bases that fail N-0, retrain M2, re-run the gate and tables — no new sampling, minutes-to-an-hour compute, but every headline number and the CLAUDE.md §5 pinned-solver convention change. (ii) Keep pandapower labels, state them as the oracle, report the N2 audit numbers as a limitation. | **(i) if it can be done and re-verified by ~Oct 10**; it turns a FATAL-class weakness into a second self-found, fixed artifact (like the clip bug). Otherwise (ii). Either way remove the 0.8485 story (P-001). Optional: spot-check ~50 flipped rows with an independent AC solver (MATPOWER/PowerModels — not installed here; install = your call). |
| AD-3 | **Retitling** | Keep "…Safety and Throughput Limits Set by Boundary Mass", or retitle so the title names the question (when a conformal gate pays) rather than a causal network claim. | **Retitle** (your wording). "Set by boundary mass" is not supported as a network property (D8, D16) and "boundary mass" is never defined (C12). |
| AD-4 | **Acknowledgments + AI disclosure** (P-002, P-012, spec `P-002-P-012-disclosure.md`) | Report only / application only / both. | **Both**, and treat it as a blocker. In the report: RISE is a paid program; name Kalita, Pinsky and the TFs; the URTC paper and its co-author; AI tools, which code portions were AI-generated (all `scripts/sts_*.py` from this run are), AI review/verification use, the prompt log. Rewrite yourself the 4 STS sentences that closely match AI-refined URTC camera-ready wording (`notes/panels/urtc_overlap.md`), or cite the refinement. Send the 10 questions in the disclosure spec to STS staff. |
| AD-5 | **N3 — setpoint-floor rebuild** (P-007, D16; judge's "single change") | Rebuild case118 with GEN_VM_LO 0.94 vs 0.95 (N-0 gate unchanged), 5 seeds, full gate metrics; optionally the 2×2 with the N-0 gate. | **Run the 0.94 vs 0.95 arm, pre-registered first** (write predictions before running, as you did for the unconditioned build). It is the open causal test and the experiment most likely to move Top-40 odds. Cost per the review ≈ 45 min build + ≈ 1 h tuning per arm. Needs your approval. |
| AD-6 | N7 — N-2 test | run / skip | Skip before Nov 5 unless AD-2 and AD-5 are done by ~Oct 10. |
| AD-7 | N8 — larger network | run / skip | Skip (case57/pegase feasibility failures; time). |
| AD-8 | N5 — learned baselines (classifier, CQR) | run / skip | Skip; report the static ranking (P-009), which is the more damaging and already on disk. |
| AD-9 | Fig. 5 | keep (swap to `data/sts_critical_bus_map.png`) / cut | **Cut**, keep one sentence on bus 76's published 0.943 setpoint (saves ≈ 0.5 pp; figure is not used in the argument). If kept, re-upload and name igraph in the credit line. |
| AD-10 | Mondrian (E7) | add one sentence (needs `vovk2003mondrian` bibitem, verified-not-inserted in prior-art §9.6) / skip | One sentence if space after AD-1…AD-5. |
| AD-11 | Checker regex (P-006) | widen to accept the R21 example form / switch lines to APA | Widen (it is the rule book's own example); your edit to the gate. |
| AD-12 | `notes/` is git-ignored (prompt log, pre-registration, contribution log) | keep private / keep a dated export in the STS research notebook / private repo | **Dated export** (e.g. PDF) of the prompt log and `notes/preregistration.md` into your research notebook; R22 asks for the log "as part of your research notebook". |
| AD-13 | Solver-time reporting (P-033) | keep "9.14 ms, min of 400" / report median / re-time | Report the median or both; see the N6 re-run note in §4. |
| AD-14 | `% AUTHOR-REWRITE` passages | — | None placed: the lead did not edit the .tex (authorship boundary). Every "revise"/"add" row is an author rewrite; the specs in `notes/patches/` say what each must contain. |

## 7. What text edits cannot fix

| Weakness | Threat to Top 40 | What would address it |
|---|---|---|
| One real network, and a stress sampler that places base cases at the limit (setpoint floor = limit; 67.7% of bases already in the strip) | **High** — the first question a PhD panel asks, and the paper's causal claim rests on it | AD-5 (setpoint-floor rebuild, pre-registered). Then 1-2 more feasible networks with an operator-like voltage schedule. |
| Oracle labels from one-way PV→PQ switching (9.47% of violations flip; 66% of histgb@0.97 misses are artifacts; model ordering flips) | **High** if left as is; **low** once relabelled and disclosed | AD-2 (i) relabel + retrain; independent-solver spot check |
| Weak absolute payoff: 1.2-1.7× on a ≈ 1.7 s serial sweep; certify-only 1.24×; break-even ≈ 4,200 sweeps; 10 parallel workers 5.4×; a static ranking beats the gate once flagged cases are solved | **Medium-high** for significance; not fixable by wording | Only a setting where the gate pays (low-ρ operating distributions, larger systems) — or an honest reframing of the contribution as *predicting when* it pays (§6), which text can do |
| Missed rate carries no guarantee under the headline selector | Medium | N1 (done): same frontier with a bound; adopt as the selector (AD-1 C) |
| Cross-network evidence is effectively n = 3 target networks; predictor A no better than a naive mean on absolute error | Medium | More networks under one sampler |
| 7.7-11.1% of N-1 studies contain at least one silent miss at the operating points | Medium (operator relevance) | Disclose (E13); a per-base-case calibration (one score per base) is a research extension |

## 8. Owner's git commands (Claude runs no git writes — CLAUDE.md §8)

`notes/` and `CLAUDE.md` are private by design (`.gitignore` l.22-24: "never commit to the public fork"), so
the ledger, panels, patches and changelog stay uncommitted. Only the public artifacts below are committable.
The working tree also carries your own uncommitted `report/paper_current_STS.tex` and
`.claude/settings.json` edits; the commands below leave them alone.

```
git checkout -b sts-panel-revision
git add scripts/sts_manifest.py
git add scripts/sts_dataset_facts.py scripts/sts_dataset_facts_b.py scripts/sts_dataset_facts_c.py data/sts_dataset_facts.json data/sts_dataset_facts.manifest.json data/sts_dataset_facts_b.json data/sts_dataset_facts_b.manifest.json data/sts_dataset_facts_c.json data/sts_dataset_facts_c.manifest.json
git commit -m "E1a/P-008/D16: dataset facts with JSON keys (inheritance share, sampling ranges, conditional strip share)"
git add scripts/sts_limit_sweep.py data/sts_limit_sweep.json data/sts_limit_sweep.png data/sts_limit_sweep.manifest.json
git commit -m "E1c: limit-sweep figure (prose-free) and values"
git add scripts/sts_crossnet_scatter.py data/sts_crossnet_scatter.json data/sts_crossnet_scatter.png data/sts_crossnet_scatter.manifest.json
git commit -m "E2a: cross-network escalation vs rho*qhat scatter"
git add scripts/sts_critical_bus_map.py data/sts_critical_bus_map.png data/sts_critical_bus_map.manifest.json
git commit -m "P-004: prose-free Fig. 5 with IEEE bus labels"
git add scripts/sts_tradeoff_bands.py data/sts_tradeoff_bands.json data/sts_tradeoff_bands.png data/sts_tradeoff_bands.manifest.json
git commit -m "P-005: Fig. 2 with seed std bands"
git add scripts/sts_miss_depth_noannot.py data/sts_miss_depth_noannot.png data/sts_miss_depth_noannot.manifest.json
git commit -m "P-001: Fig. 3 without the artifact deepest-miss annotation"
git add scripts/sts_matched_escalation.py data/sts_matched_escalation.json data/sts_matched_escalation.manifest.json
git commit -m "C8: missed rate at matched escalation"
git add scripts/sts_n2_label_audit.py scripts/sts_n2_summary.py data/sts_n2_label_audit.json data/sts_n2_label_audit.manifest.json data/sts_n2_label_audit.parquet data/sts_n2_label_audit.parquet.run.json
git commit -m "N2 (P-001/P-003): Q-limit PV/PQ switch-back label audit"
git add scripts/sts_n1_class_conditional.py data/sts_n1_class_conditional.json data/sts_n1_class_conditional.manifest.json data/sts_n1_predictions_long.parquet
git commit -m "N1: class-conditional calibration of the certify threshold"
git add scripts/sts_n4_f1_shuffle.py data/sts_n4_f1_shuffle.json data/sts_n4_f1_shuffle.manifest.json
git commit -m "N4: paired 5-seed F1 shuffle control"
git add scripts/sts_n6_warmstart_timing.py data/sts_n6_warmstart_timing.json data/sts_n6_warmstart_timing.manifest.json
git commit -m "N6 (P-033): warm-start solver timing"
git add scripts/sts_e12_e13_conditional.py data/sts_e12_e13_conditional.json data/sts_e12_e13_conditional.manifest.json
git commit -m "E12/E13: per-element and per-base-case conditional coverage"
```
Sizes: `data/sts_n1_predictions_long.parquet` 17 MB, `data/sts_n2_label_audit.parquet` 7.3 MB (25 MB total
for `data/sts_*`). Every script above is AI-written (disclosure, AD-4).

## 6. Headline framing — content proposal (not prose)

What the evidence supports (all numbers above, sources in the rows):
- **Question:** when does a conformal gate on an ML surrogate save AC solves at a ~1% missed-violation
  rate, and what sets that?
- **Mechanism (supported):** escalation = share of predictions within one band width above the limit
  (exact accounting); across 5 networks it tracks ρ·q̂ (r = 0.81; log-log 0.92), with a named failure
  (case24 ridge). ρ is measurable before training.
- **Cause on case118 (CORRECTED 2026-09-27, see D16):** post-outage minima inherit the base case (77.6% of
  outages move the minimum < 0.001 pu), and the base cases sit at the limit. The author's own
  **pre-registered** test (`notes/preregistration.md`, 09-10) shows the **N-0 acceptance gate is NOT what
  creates the concentration**: the pre-registered decisive quantity, the conditional share
  P(strip | not a violation), is 68.90% gated vs 65.58% ungated (falsifier < 50% not hit); the
  unconditional 56.86 → 28.83% drop is the pre-registered denominator effect (P1 range 12-32%, point 22%).
  Within case118 the N-0-margin quintiles move the strip 78 → 5% (violation rate only 21.5 → 14.2%). The
  remaining candidate cause is the **generator-setpoint floor at the limit** (P-007), active in both builds
  and untested at scale; a provisional 40-base, 1-seed probe (POWER a7.py) implies conditional shares of
  ≈ 82% (floor 0.94) vs ≈ 44% (floor 0.95) — lead's arithmetic on teammate numbers, provisional; N3-class
  test needs author approval. So: supported = "inherited from base cases that the sampler places at the
  limit"; not supported = "the N-0 gate makes it" and "a property of the network alone".
- **A strength to surface:** the pre-registered unconditioned test itself (predictions written before the
  run, P1-P5 checked) is exactly the "own scientific thinking" the STS judge found missing from the paper.
- **Honest headline numbers (must not be buried):** held-out histgb 1.15 ± 0.27% missed (4/5 splits
  > 1%) at 59.3% escalation, 1.69×; certify-only 1.24×; break-even ≈ 4,200 base-case sweeps; 10
  parallel workers 5.4×; a static training-frequency ranking catches more violations than the gate at
  the gate's full solve budget (P-009).
- **Therefore the contribution to claim:** a way to predict, before training, whether a gate will pay
  on a given network and operating-point distribution — and a documented case (case118 under this
  stress sampler) where it does not. Not: a faster screener; not a network-general law.
- **Not supported:** "must" floor; network property; "faster model is not safer" at matched cost;
  deepest-miss collapse story; any physical missed rate before N2.

The author writes the introduction and conclusion; this list is the claim ceiling, not text.

---

## §Commands (lead-verified items)

- C1 counted pages: `pdftotext -f $p -l $p "…(39).pdf" -` per page → folios 1-16 on pp. 3-18.
- C2 Fig. 5 staleness: `pdfimages -png paper_v39.pdf all`; pixel diff with PIL vs `data/{gate_schematic_v4,tradeoff_hero_col_v2,miss_depth_v3,boundary_mass_hist_v2,critical_bus_map}.png` → max diff 0,0,0,0,255 (0.022% of pixels).
- C3 still-present check: `grep -c -- "<anchor>" report/paper_current_STS.tex` for 33 anchors (all ≥ 1 except "quintile", "unconditioned", "Mondrian" = 0).
- C4 compliance: `.venv/bin/python scripts/check_compliance.py` → PASS 4, FAIL 2 (R10/R21 regex, P-006), SKIPPED 3 (no TeX), MANUAL 18.
- C5 static ranking: `data/baselines.json` → `comparators.static_severity.curve_mean/curve_std` at k = 57, 89, 91, 138 → 91.22/96.64/96.89/99.41 (± 0.55/0.50/0.47/0.16); budgets k = (escalation + flag share) × 186 with escalation 0.4907/0.3063 (`gate.*.escalation_mean`) and flag share 0.251/0.172 (POWER-05, `data/flag_confusion_long.parquet`).
- C6 URTC authors: `grep -A8 '\\author' paper_current_URTC_20260808.tex`.
- C8 N2 counts: `pd.read_parquet("data/sts_n2_label_audit.parquet")`, N-1 rows (`outaged_type != "none"`, 278,955): stored `min_vm < 0.94` = 48,749; `corrected_violation` = 46,295; `flip_viol_to_safe` = 4,615; `flip_safe_to_viol` = 2,162; `repro_abs_diff.max()` = 0.0; scenario 101000025 line 78 corrected 0.945073 (argmin 26, 2 iters); corrected min 0.8077.
- C7 AI disclosure absence: `grep -n -i -E "generative|claude|chatgpt|\bAI\b|artificial" report/paper_current_STS.tex`.
