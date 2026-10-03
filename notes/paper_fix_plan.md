# Paper fix plan — `report/paper_current_STS.tex`

Written 2026-09-30 by Claude Code at the owner's request. It is a plan only: **you write every word of the
report** (STS GUIDE2027 rule 1; `sts-constraints.yaml` R04, R22, R27). This file says what each part must
contain, which numbers go where, and where each number comes from. It contains no replacement text.

The detailed per-item specs are in `notes/patches/`, all verifier-signed. The master list is
`notes/panel_ledger.md`. When this plan and a patch disagree, the patch has the numbers and this plan has the
order. **Numbers below are read from the named files on 2026-09-30.** Re-read the key before printing any of
them; never copy from this file.

Deadline 2026-11-05, 8 pm ET (support deadline 11-04).

---

## Timeline

| Dates | Work |
|---|---|
| Sep 30 - Oct 3 | Step 1 (disclosure), and send the STS staff questions. Run N10 on the Mac mini. |
| Oct 3 - Oct 10 | Steps 2 and 4 (numbers and figures), using the N10 Part C outputs. Decide the title. |
| Oct 10 - Oct 24 | Step 3 (rewrite around the new story), then steps 6-8. |
| Oct 24 - Oct 31 | Step 5 (compile, count pages, compliance, re-upload figures), and a human read-through (R27: readers may suggest, not rewrite). |
| Nov 1 - Nov 4 | Buffer. Final PDF, filename rule (R14), and download it and check that every symbol survived (R15). |

---

## Step 1 — Disclosure (blocker; do first)

- **Spec:** `notes/patches/P-002-P-012-disclosure.md`, which holds the facts, the rule quotes and 10
  questions for STS staff.
- **The report must state:**
  - BU RISE is a fee-based program.
  - The instructors and TFs by name, and what each contributed.
  - Anyone who read a draft.
  - The URTC paper (camera-ready), including that Eugene Pinsky is its co-author.
  - The AI tools used.
  - **Which portions of the code are AI-written.** At minimum, every `scripts/sts_*.py` and every
    `scratch/*.py` from the review runs. The prompt log also has no record before 2026-07-26, so decide
    how to describe the older code honestly.
  - That AI was used for review and verification (the panels, the verifiers).
  - That a prompt log exists (`notes/ai-prompt-log.md`, now tracked in git).
- **URTC overlap:** decide for each of the 4 close-match sentences (`notes/panels/urtc_overlap.md`) whether
  to rewrite it yourself or cite the AI refinement.
- **Checker:** `scripts/check_compliance.py` R10/R21 fails on a regex false negative (ledger P-006). Fix
  the regex or accept the FAIL knowingly.

## Step 2 — Replace the numbers with corrected-label numbers

**The rule.** Every result number moves from the old pandapower labels to the switch-back labels.

**Where the corrected sources already exist (no rerun needed):**
- **Gate on case118 corrected labels:** `data/sts_n5_gate_094.json` (per split) and
  `data/sts_n5_verdict.json → tables["094"]` (mean ± std).
- **Label facts:** `data/sts_n2_label_audit.json` and `.parquet`.
- **Mechanism (floor):** `data/sts_n9_floor_replication.json`, `scratch/n3_floor_result.md`,
  `data/sts_n3_floor09{4,5}.json`.
- **Budget curve:** `data/sts_n9_budget_curve.json`.
- **Shift test:** `data/sts_n9_shift.json`.

**Old → new mapping, main numbers:**

| Where in the current paper | Current (old labels) | Corrected source → value |
|---|---|---|
| Abstract, Table 1, Table 2: histgb @0.90 | 30.6% esc, 4.72% missed, 3.29× | `tables["094"]` histgb 0.90 → esc 26.3 ± 2.8%, missed 4.24 ± 1.76%, speedup A 3.83 ± 0.40, speedup B 2.39 ± 0.15 |
| Abstract and IV-A headline point | "first under 1%" at 0.97, 63.7% esc, 1.58× (picked on test) | **Use the held-out point** (patch Top5-2d-E5): histgb esc 50.2 ± 8.4%, missed 1.51 ± 1.35% (3 of 5 splits ≤ 1%), speedup A 2.06 ± 0.41, speedup B 1.55 ± 0.23 |
| Ridge @0.90 / held-out | 49.1% esc, 2.96% missed / 0.94 point | ridge 0.90: esc 46.8 ± 3.8%, missed 3.36 ± 0.39%; held-out: esc 59.5 ± 2.2%, missed 1.82 ± 0.59% |
| Table 1 MAE and R² | 0.0038 / 0.77; 0.0016 / 0.92 | `sts_n5_gate_094.json → fits`: ridge 0.00349 ± 0.00015 / 0.804 ± 0.013; histgb 0.00133 ± 0.00003 / 0.956 ± 0.002 |
| Violation rate | 17.48% | `sts_n2_label_audit.json` → 16.60% (46,295 of 278,955) |
| Boundary mass | 56.86% | corrected 56.22% (patch P-003); say which label set you use |
| Min-voltage range | 0.7179-0.9603 | corrected 0.8077-0.9595 (N2 parquet `corrected_min_vm`, 278,954 rows) |
| Worst miss 0.0915 pu / 0.8485 | printed 3 times | **delete** (solver artifact; patch P-001) |
| case30 numbers | 5.84 ± 1.25% etc. | still stored-label; either relabel case30 (not planned) or label it "stored pandapower labels" |

- **Rows not in the mapping above:** every Table 2 row (0.90-0.98) comes from `tables["094"]`. N10 Part C (e)
  emits the table bodies. Each table's attribution line stays.
- **Operator number (step 8):** share of base cases with ≥ 1 missed violation. The stored-label value is in
  `data/sts_e12_e13_conditional.json`; the corrected one comes from N10 Part B.

## Step 3 — Rewrite around the new story (content order, not text)

**Title.** Author decision (ledger AD-3). It should name the question (when a conformal gate pays off), not
a causal network claim.

**Abstract, in this order:**
1. the problem;
2. the gate idea;
3. the question;
4. the mechanism, stated once in plain words;
5. the pre-registered floor experiment and its outcome (3 builds, all in the predicted range);
6. the honest headline (held-out missed rate; speedup; static ranking ties or wins at that budget);
7. where ML does help (small solve budgets);
8. the limitation (one network, or two if N10 runs).

Define "boundary mass" and "coverage" before use (patches C12, C4).

**Introduction:**
- State the research question(s) and what outcome would answer each (patch Top5-5).
- The contribution list must contain only contributions, not the scope restriction.

**Method, which must now include:**
- the sampler, including that the generator voltage floor equals the limit (P-007);
- the switch-back labeling and why it's needed (P-003);
- the held-out operating-point selection;
- the static-ranking baseline;
- the pre-registration practice (hashes, git timestamps);
- a compact reproducibility table (P-011).

**Results, suggested order:**
1. accuracy and gate trade-off on corrected labels (Table 1, the Fig. 2 equivalent);
2. safety at the held-out point: missed rate is measured, not guaranteed (E5b); the N5 SAFER verdict;
3. the static baseline and the budget curve: ML wins at small budgets, history at large ones (N9 Part 1,
   the N5 FASTER verdict);
4. the mechanism: the floor experiment, prediction vs outcome over 3 builds;
5. shift: the N9 shift test (SHIFT-ADVANTAGE no; coverage held forward, failed in reverse);
6. a second network, if N10 runs.

**Discussion:**
- why the static ranking is hard to beat here (violation concentration, step 6);
- the two self-found artifacts: the clip bug and the Q-limit solver bug;
- limitations: one or two networks, a synthetic stress sampler, pandapower-based labels, and n = 3 builds.

**Delete or shrink** (patches `cuts.md`, E14, E5b-E15):
- the deepest-miss collapse story;
- the "must be a floor" and "inherent" claims;
- S_mean;
- the reject-option digression;
- the case57/pegase detail;
- the ablation, shrunk to about 150-200 words: keep the leakage audit, the 5-seed shuffle (N4) and the
  F3/F4-by-construction point.

**Claim ceiling:**
- **Can say:**
  - escalation equals the prediction mass near the limit (accounting);
  - the floor manipulation moved it as predicted, 3 times;
  - ML ranking beats history at small budgets on case118;
  - the gate did not beat history at the held-out budget, and did not beat it under the tested shift.
- **Cannot say:**
  - a network-general law;
  - "first" or "novel method";
  - a physical missed rate without naming the label method;
  - any number from old labels without saying so.

## Step 4 — Figures

| Figure | Action | Source |
|---|---|---|
| Fig. 1 gate schematic | keep | unchanged |
| Fig. 2 trade-off | swap for the banded version on corrected labels | **`data/sts_paper_fig2_tradeoff.png`** (done 2026-09-30) |
| Fig. 3 miss depth | regenerate on corrected labels, no annotation | **`data/sts_paper_fig3_missdepth.png`** (done) |
| Fig. 4 boundary histogram | regenerate on corrected labels | **`data/sts_paper_fig4_boundary.png`** (done) |
| Fig. 5 bus map | author decision (AD-9); if kept, upload `data/sts_critical_bus_map.png` and name igraph in the credit line | — |
| New: budget curve | add; the key new result | **`data/sts_paper_fig_budget.png`** (done) |
| Optional: cross-network scatter / limit sweep | only if pages allow | `data/sts_crossnet_scatter.png`, `data/sts_limit_sweep.png` |

- **Every figure needs a credit line** under it: you as creator, the program, the year (R21).
- **AI-drawn figures (author decision; ask STS staff).** The `data/sts_paper_*` figures and table bodies were
  produced by AI-written code (`scripts/sts_paper_corrected.py`). So were several earlier figures (the
  `sts_*` scripts). RULES2027 App. 4 (R22) says an AI-produced graphic "should be clearly marked as
  AI-generated and with explicit citation as to how the image was created". The current credit line
  "Graph created by Rajan Saha using Matplotlib 3.11.1, 2026" may be incomplete for these. Decide the
  wording, and add this to the STS staff questions.
- **Table bodies:** `data/sts_paper_tables.tex` holds Table 1 (models), Table 2 (operating points,
  plus a variant with speedup B), a floor-experiment table, and a gate-vs-static table, all on corrected
  labels. Values and manifests are in `data/sts_paper_tables.json`. Note two changes: the train-mean
  baseline now escalates every case (the corrected mean is 0.9403 > 0.94), so the old "never calls
  the solver" footnote no longer applies; and at the held-out point, histgb has 3 of 5 splits ≤ 1% and
  ridge 0 of 5.
- **Upload every changed PNG to Overleaf,** then re-run the pixel check. The last export had a stale Fig. 5.

## Step 5 — Compile and compliance (after each big change)

1. **Compile in Overleaf** and count the body pages. The current export is 16 counted pages; about 18 is
   projected after the changes. The cap is 20; title, abstract and bibliography are excluded, appendices
   count (R05).
2. **Run the checker:** `.venv/bin/python scripts/check_compliance.py`.
3. **Check the floats:** every figure and table is cited before it appears, and each has a credit line.
4. **Check the std rule:** no "above", "better" or "gap" unless it exceeds the larger std (patch numbers-2b
   lists the current violations).
5. **Check the bibliography:** every citation is verified in `notes/prior-art.md`. Don't fill any field from
   memory. `manoharan2026` must be re-read first (patch P-028). MATPOWER needs verifying before citing, if
   N10 Part A is used.

## Step 6 — Why the static ranking wins: violation concentration

- **Measure:** the share of test violations from the top-5 and top-10 outaged elements.
- **Source:** N10 Part B descriptive (both networks).
- **Where it goes:** one sentence plus one number in the Discussion.

## Step 7 — Budget curve as a main result

- **Source:** `data/sts_n9_budget_curve.json`, and the N10 figure.
- **Content** (histgb, corrected labels, catch ± std):

  | Data | ML wins | Tie | History wins |
  |---|---|---|---|
  | case118 at the 0.94 floor | k = 20, 40, 57 | — | k = 89, 120 |
  | case118 at the 0.95 floor | k = 20, 40 | k = 57, 89 | k = 120 |

  k is per base case, out of about 186. Ridge ties history at every k.

## Step 8 — Operator metric

- **Measure:** the share of base cases with at least one missed violation at the held-out point.
- **Values:** stored labels 7.7 ± 2.0% (ridge@0.94) and 11.1 ± 2.6% (histgb@0.97) in
  `data/sts_e12_e13_conditional.json`. Use the corrected-label value from N10 when it exists.
- **Where it goes:** one sentence in Results 2.

---

## Author decisions still open (ledger §5)

- **Headline point:** recommended the held-out point.
- **Title** (AD-3).
- **Disclosure wording and STS staff answers** (AD-4).
- **Fig. 5** (AD-9).
- **Whether to include the N10 Illinois results.** If N10 runs, report its verdicts whichever way they go.
- **Whether to relabel case30** or keep it labeled as old-label evidence.
- **Checker regex** (AD-11).

## Done when

- [ ] Disclosure in the report; STS staff questions sent.
- [ ] No old-label number without a label note; no test-picked operating point as the headline.
- [ ] The deepest-miss story is gone; the floor experiment and verdicts are present.
- [ ] Budget curve and static baseline in the Results.
- [ ] All figures regenerated, uploaded and pixel-checked; credit lines present.
- [ ] Overleaf compile ≤ 20 counted pages; `check_compliance.py` run; std rule checked.
- [ ] Every number traced to a JSON key (spot-check with a verifier pass).
- [ ] Final PDF downloaded and inspected; filename per R14; submitted before 11-04.

---

## Location map — where each number and figure lives in the .tex

Mapped 2026-09-30 against `report/paper_current_STS.tex` sha256 `1e2c36d1…`.
- **Line numbers are for navigation only.** Search by the anchor words, because lines move as you edit.
- **"Source → value"** is where the corrected number comes from (Step 2). N10 Part C re-emits Table 1-2
  bodies and Figs. 2-4 on corrected labels; use those when they exist.

### Numbers

| Section | Line | Anchor (first words) | Now | Change to (source → value) |
|---|---|---|---|---|
| Abstract | 73 | "The power system grid should remain resilient…" | histgb 3.29× and 4.72% @90% | `tables["094"]` histgb 0.90 → speedup 3.83 ± 0.40 (rule A), missed 4.24 ± 1.76% |
| Abstract | 73 | same paragraph | "first … under 1% … 0.97", 63.7% esc, 1.58× | held-out point → esc 50.2 ± 8.4%, missed 1.51 ± 1.35% (3 of 5 splits ≤ 1%), speedup 2.06 ± 0.41 (A) / 1.55 ± 0.23 (B) |
| Abstract | 73 | same paragraph | 56.86% vs 7.09% | 56.22% corrected (case118); case30 7.09% is on stored labels, so say so. Add the floor experiment (Step 3) |
| Method, Dataset | 111 | "I determined the load levels by scaling…" | 17.48%; range 0.7179-0.9603 | 16.60%; 0.8077-0.9595 (`sts_n2_label_audit.parquet` corrected_min_vm). Add the switch-back label method here (patch P-003) and the setpoint floor (P-007) |
| Method, Dataset | 113 | "The previous implementation of the dataset generator…" | clip story, 56.86% | keep the clip story (a strength); say which label set 56.86/56.22 refers to |
| Method, Conformal band | 124 | "where $\hat{p}$ is the prediction…" | q̂ 0.0052 / 0.0023; "same type of condition" | q̂ from `sts_n5_gate_094.json` (per-split `q_hat` at 0.90); fix the exchangeability wording (patch P-010) |
| Method, Theory | 181 | "For the IEEE 118-bus system, using the statistic above…" | S_mean 0.6038 / 0.7919 | **delete** S_mean (patch E5b-E15) |
| Results intro | 191 | "Both surrogate models accurately predict…" | MAE 0.0038 / 0.0016, R² 0.77 / 0.92; 49.1/2.96/2.04; 30.6/4.72/3.29 | `sts_n5_gate_094.json → fits`: ridge 0.00349 / 0.804, histgb 0.00133 / 0.956; @0.90 ridge 46.8% esc, 3.36% missed; histgb 26.3%, 4.24% |
| Table 1 | 209-210 (+ persistence and train-mean rows) | "ridge & 3.8…", "histgb & 1.6…" | old-label rows | `data/sts_paper_tables.tex` (tab:models body, corrected; persistence and train-mean recomputed). Add the static-ranking comparison (gate-vs-static body in the same file) |
| IV-A text | 223 | "In Table~\ref{tab:ops}, I adjusted the target…" | 0.94 / 0.97 picked on test; 64.3 / 63.7; 1.56 / 1.58; "1.0-1.07%" | held-out point (as above); the test-picked points only as description; 1.07 → recompute from the corrected table |
| Table 2 | 240-251 | "ridge & 0.90…" to "histgb & 0.98…" | 12 old-label rows | `data/sts_paper_tables.tex` (tab:ops body, corrected; the held-out rows are included) |
| IV-B | 284 | "On the IEEE 118-bus system, the more accurate model is not safer…" | 3.29 vs 2.04; worst miss 0.0915 / 0.8485; 26.7% / 21.4% | **delete** the worst-miss sentence (P-001). Rewrite the comparison at matched escalation (patch C8; values from `sts_matched_escalation.json`, stored labels, or redo on corrected) |
| IV-C | 306 | "Most of the contingencies lie within 0.005 per unit…" | 56.86%, 17.48%, 2.04 | 56.22%, 16.60%; move the reject-option digression out (cuts.md) |
| IV-C ceiling | 339 | "A case is escalated when the prediction lies…" | 30.6%; 74.89 / 82.79 / 82.64 | recompute on corrected labels or keep as stored-label description; "just above" → "at" (std rule) |
| IV-C | 341 | "Persistence is the baseline model…" | "0.94 or a 0.97 target … about a 1.6 times speedup" | held-out point; add the static-ranking result (N5 FASTER clause 2) and the budget curve (N9) |
| IV-D | 345 | "I used non-overlapping calibration and testing data…" | 0.4726 / 0.4933; "locked tes" typo | per-network errors (patch E2); fix the typo |
| Discussion | 357 | "The key findings obtained during the experiments…" | 56.86 / 17.48; "escalation floor"; case30 | 56.22 / 16.60; replace the causal claim with the floor experiment (`sts_n9_floor_replication.json`) |
| Discussion | 359 | "All metrics reported use the sampled N-1 population…" | worst-case collapse story (0.0915) | **delete** the mechanism story (P-001); keep the gen-out counts (374 / 69,532), and fix the N-1 wording (C6) |
| Conclusion | 380 | "My models can predict N-1 under-voltage contingencies…" | "almost two-thirds … 1.6" | held-out-point numbers; static-ranking and budget-curve result; floor experiment |

### Figures (`\includegraphics` lines)

| Fig. | Line | File now | Replace with | Caption line to revise |
|---|---|---|---|---|
| 1, gate | 146 | `data/gate_schematic_v4.png` | keep | 147 |
| 2, trade-off | 272 | `data/tradeoff_hero_col_v2.png` (no error bars) | N10 Part C (a) corrected banded figure; interim `data/sts_tradeoff_bands.png` (old labels) | 273: drop "first falls just under 1%… 0.94 / 0.97"; state the ±std numerically |
| 3, miss depth | 294 | `data/miss_depth_v3.png` (prints "deepest miss 0.0915") | N10 Part C (b); interim `data/sts_miss_depth_noannot.png` | 295: remove the 0.0915 / 0.8485 case and the 74% / 55% old-label shares |
| 4, boundary | 314 | `data/boundary_mass_hist_v2.png` | N10 Part C (c) corrected histogram | 315: 56.9% → corrected value, one precision everywhere |
| 5, bus map | 330 | `data/critical_bus_map.png` (Overleaf copy stale, 0-based) | cut (AD-9), or `data/sts_critical_bus_map.png` | 331: name igraph in the credit line |
| New, budget curve | — | — | N10 Part C (d) | new caption: SURR vs STATIC vs ORACLE catch by budget |

- **Upload to Overleaf:** after changing an `\includegraphics` path, upload the new PNG to Overleaf's
  `data/` folder, then re-export and pixel-check it against the repo file.
- **Credit lines:** every figure and table keeps its "created by Rajan Saha using …, 2026" line (R21).

---

## Update 2026-10-01 — N10 / N11 results and where they go

**Status labels.**
- **VERIFIED:** recomputed by the lead from the raw files on 2026-10-01 (prompt-log entry 2026-09-30 (t)).
- **Reported:** read from `scratch/n10_result.md` / `scratch/n11_result.md`. Re-read the JSON key before
  printing.

**The story now.** It answers both research questions:
- **RQ2, when does the gate pay?** Not on case118 under this sampler, where history ties. It does on 3 other
  networks, and the floor experiment shows why.
- **RQ1, does coverage survive N-1 → N-2?** No.

### New results

| Result | Numbers | Status | Source | Where in the paper |
|---|---|---|---|---|
| Independent solver check (MATPOWER 8.1) | 201/201 labels agree with the corrected labels; worst case 0.94507 pu | VERIFIED | `data/sts_n10_matpower_check.json` | Method, label section (P-003): one sentence |
| Illinois-200 relabel | VR 29.28 → 21.66%; BM 19.33 → 14.31%; 0 failures | VERIFIED | `data/sts_n10_relabel_illinois200.json` | Method, datasets |
| Illinois gate vs history (pre-registered) | gate 99.04 ± 0.22% vs history 88.90 ± 1.20%; the gate is higher in 5/5 splits | VERIFIED | `data/sts_n10_illinois.json` (points, held_out) | Results, gate vs history: the first "yes" |
| Illinois safety (pre-registered) | 2 of 5 splits ≤ 1% missed | VERIFIED | same | Results, safety |
| Illinois held-out point | esc 10.7 ± 2.2%; missed 0.96 ± 0.22%; speedup A 9.64 ± 1.99, B 3.12 ± 0.25 | Reported | `data/sts_n10_illinois.json` → table | Results |
| Why the gate wins on Illinois | within-base ranking ties history at every budget; the gain comes from spending solves on riskier base cases | Reported | `curves_at_declared_k` | Discussion (N12 tests this) |
| case30_thermal, corrected | held-out: esc 6.2%, missed 0.63%, 4/5 ≤ 1%; gate 99.37 vs history 84.09; @0.97: esc 4.6 ± 0.4%, missed 0.66 ± 0.17%, speedup A 21.60 | Reported | `data/sts_n11_smallnets.json` | **Abstract** (replaces the old-label case30 numbers) and Results, network table |
| case24_ieee_rts, corrected | held-out: esc 16.9%, missed 0.98%, 2/5; gate 99.02 vs history 92.48 | Reported | same | Results, network table |
| case39 | excluded: 1.09% of rows failed the switch-back solve (> 0.5% ceiling) | Reported | `data/sts_n11_relabel_case39.json` | Method or limitations: one sentence |
| N-1 → N-2 coverage (pre-registered) | histgb 0.8346 ± 0.0181 vs N-1 0.8981 (threshold 0.8819): **does not hold**; N-2 missed 3.95%; ridge 0.611 | VERIFIED | `data/sts_n11_n2.json` | Results, new subsection answering RQ1 |
| Mondrian vs history (pre-registered) | tie (gap 0.17 vs std 1.43) | VERIFIED | `data/sts_n11_mondrian.json` | Results, one sentence |
| Floor dose-response (pre-registered) | BM 58.07 / 56.86 / 32.95 / 19.91% at floors 0.93 / 0.94 / 0.95 / 0.96; all 6 predictions in range | VERIFIED | `data/sts_n11_dose_response.json` | Results, mechanism. Replaces the 2-level floor table; consider a small figure |
| Classical screen, corrected (Table 1 row) | 3.7 ± 0.1 / 0.14 ± 0.01 / 90.7 ± 1.1% / 1.83 ± 0.57% / 1.10 ± 0.01 | Reported | `data/sts_n11_classical.json` | Table 1 |
| D95b / D95c gate | both builds: N5 rules SAFER no, FASTER no | Reported | `data/sts_n11_gate_095bc.json` | Results or appendix: one sentence |
| Solver time | the M4 Mac mini timing is not comparable to the M5 laptop; the laptop re-time was stopped (not run) | — | — | Method, timing (P-033): say "median" or keep 9.14 ms with its basis |

### Changes to the earlier steps

- **Step 3, Results order (revised):**
  1. corrected-label trade-off (case118);
  2. safety at the held-out point (all networks);
  3. **gate vs history across 4 networks** (case118 tie; Illinois, case30, case24 gate higher), plus the budget
     curve;
  4. mechanism: the 4-level floor dose-response;
  5. N-2 coverage;
  6. Mondrian (one sentence).
- **Claim ceiling, now allowed:**
  - "the gate beat the history ranking on 3 of 4 networks; on case118 they tie";
  - "boundary mass responded to the generator voltage floor as predicted at all 4 levels";
  - "coverage calibrated on N-1 fell to 83% under N-2".
- **Claim ceiling, still not allowed:**
  - a general law from 4 networks;
  - that the ML ordering is better than history (on Illinois the gain comes from allocation across base
    cases);
  - any guarantee on missed rate.
- **Abstract:** case30 numbers must come from the corrected-label run (case30 @0.97 or held-out, as above),
  not the old 5.84% / 17.9×.
- **Figure candidates:**
  - a 4-network gate-vs-history bar or table;
  - the floor dose-response (4 points vs the predicted ranges);
  - the N-2 coverage comparison.

  These can be built from the JSONs above (same script style as `scripts/sts_paper_corrected.py`); ask
  before adding pages.
- **N12** (pending, Mac mini) tests whether a no-ML "conditional history" baseline that may also spend more on
  risky base cases closes the gate's advantage. Its verdict decides how the Illinois/case30/case24 win is
  described.

---

## Update 2026-10-02 — N12 results and final experimental picture

**Experiments are closed.** From here on, everything is writing (Steps 1-8 above, with the additions below).

**Status labels.**
- **VERIFIED:** recomputed by the lead on 2026-10-02 (prompt-log entry 2026-10-02 (c)).
  - The Illinois COND-HIST was re-implemented independently and matches per split to 3 decimals.
  - The commit map ties the N12 draft's old ID `d5744e6` to the current `4eb61ec`; the rule hash `8d11714c…`
    matches.
- **Reported:** read from `scratch/n12_result.md`; re-read the key before printing.

### N12 results and where they go

| Result | Numbers | Status | Source | Where in the paper |
|---|---|---|---|---|
| Gate vs conditional history (no-ML lookup by line × pre-outage voltage margin; same solve budget), **Illinois, primary, pre-registered** | gate 99.04 ± 0.22% vs COND-HIST 97.94 ± 0.97%: **yes, narrowly** (gap 1.10 vs std 0.97); gate higher in 5/5 splits | VERIFIED | `data/sts_n12_condhist.json` → networks.case_illinois200 | Results, gate vs baselines; the key robustness check |
| Same, case30_thermal | 99.37 vs 89.44: yes (gap 9.93 vs 3.90), 5/5 | VERIFIED | same | same table |
| Same, case24_ieee_rts | 99.02 vs 94.62: yes (gap 4.40 vs 0.72), 5/5 | VERIFIED | same | same table |
| Same, case118 | 98.49 vs 99.06: tie (history higher in 3/5) | VERIFIED | same | same table |
| Global budget alone (GLOBAL-STATIC) | within 0.65 pp of fixed-budget static on every network: the gain comes from conditioning on the operating condition, not from moving the budget | Reported | same | Discussion: one sentence |
| Price of a guarantee, base-level (P(any miss in a new base case) ≤ 10%) | case118 histgb: esc 50.2 → 60.0%, speedup B 1.55 → 1.32, any-miss 17.1 → 8.1% (5/5 splits ≤ 10%). Illinois histgb: esc 10.7 → 19.6%, speedup B 3.12 → 2.46, any-miss 23.9 → 10.1% (3/5 ≤ 10%) | Reported | `data/sts_n12_guarantee.json` | Results, safety: the guaranteed alternative, with its cost |
| Price of a guarantee, row-level α = 0.01 | case118 histgb missed 1.22 ± 0.70% (3/5 ≤ 1%); Illinois 1.03 ± 0.14% (3/5); rows are not exchangeable, so this is no per-row guarantee | Reported | same | Footnote or one sentence |
| Cross-network table | BM, VR, risk spread across base cases, top-10 concentration, and gate / static / COND-HIST / GLOBAL-STATIC catch, for 4 networks | Reported | `data/sts_n12_crossnet.json` | **Main results table (new)**: candidate to replace the old case118-vs-case30 contrast |

### Final claim ceiling (supersedes earlier lists)

**Can say:**
- **The bug:** a pandapower Q-limit artifact; independently confirmed by MATPOWER (201/201); labels
  corrected.
- **The mechanism:** escalation is the prediction mass near the limit; the generator voltage floor moved
  boundary mass as predicted at 4 levels (pre-registered).
- **The baselines:** the gate beat a no-ML conditional-history baseline at the same solve budget on 3 of 4
  networks (narrowly on Illinois, clearly on case30 and case24) and tied on case118.
- **Safety:** at the held-out point, missed is about 1-1.5% and is not guaranteed. A base-level calibration
  guarantees P(any miss) ≤ 10% per operating condition, at a stated cost in solves.
- **Shift:** coverage calibrated on N-1 falls to about 83% under N-2.

**Cannot say:**
- that the ML ranking beats history in general;
- that the gate is "safe" without naming the guarantee and its cost;
- any law from 4 networks;
- "first" or "novel method".

### Suggested Results structure (final)

1. Labels and correction: the bug, the MATPOWER confirmation, the corrected numbers.
2. Accuracy and the gate trade-off on case118 (Table 1, Fig. 2).
3. **Gate vs baselines across 4 networks:** the cross-network table, with fixed static, COND-HIST and the gate,
   plus the budget-curve figure.
4. Mechanism: the floor dose-response (4 levels, prediction vs outcome).
5. Safety: the held-out missed rate, and the base-level guarantee with its cost.
6. Shift: the N-2 coverage result.

Mondrian, D95b/c and the row-level guarantee get one sentence each or go in an appendix if the pages allow.

### Data artifacts still to build (on request, no new solves)

- A 4-network results table body (`.tex`) from `data/sts_n12_crossnet.json` + `data/sts_n12_condhist.json`.
- A floor dose-response figure (4 levels vs the hashed predicted ranges) from
  `data/sts_n11_dose_response.json`.
- An optional N-2 coverage bar figure from `data/sts_n11_n2.json`.
