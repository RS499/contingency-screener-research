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
| Fig. 2 trade-off | swap for the banded version on corrected labels | N10 Part C (a); interim: `data/sts_tradeoff_bands.png` (old labels) |
| Fig. 3 miss depth | regenerate on corrected labels, no annotation | N10 Part C (b); interim: `data/sts_miss_depth_noannot.png` (old labels) |
| Fig. 4 boundary histogram | regenerate on corrected labels | N10 Part C (c) |
| Fig. 5 bus map | author decision (AD-9); if kept, upload `data/sts_critical_bus_map.png` and name igraph in the credit line | — |
| New: budget curve | add; the key new result | N10 Part C (d), from `data/sts_n9_budget_curve.json` |
| Optional: cross-network scatter / limit sweep | only if pages allow | `data/sts_crossnet_scatter.png`, `data/sts_limit_sweep.png` |

- **Every figure needs a credit line** under it: you as creator, the program, the year (R21).
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
