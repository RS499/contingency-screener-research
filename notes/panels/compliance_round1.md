# Compliance & page budget — round 1 (STS 2027 report)

**Teammate:** compliance (Claude Code), 2026-09-27. **Read-only on `report/`.** No wording proposed.
**Inputs:** `report/paper_current_STS.tex` (460 lines, working tree), Overleaf export
`~/.claude/jobs/484f4ac7/tmp/paper_v39.pdf` (20 pp, 1,236,133 bytes, pdfTeX 1.40.27, 2026-09-27 13:50),
`notes/sts-constraints.yaml`, `notes/panel_ledger.md`, `notes/placement_plan.md`.
**Tools:** `pdftotext -layout` and `-bbox-layout` per page, `pdfimages -list`, `.venv/bin/python` (PIL, re).
Line numbers `l.N` are .tex lines; `pN` is the physical PDF page; folio = printed page number (p3 = folio 1).
Scratch extraction lives in `~/.claude/jobs/484f4ac7/tmp/cmp/` (not durable).

---

## 1. `scripts/check_compliance.py` output

`.venv/bin/python scripts/check_compliance.py` → exit 1. **PASS=4 FAIL=2 SKIPPED=3 MANUAL=18** (matches ledger C4).

| Row | Verdict | Interpretation |
|---|---|---|
| R04 | PASS | Tests only that the two authorship hooks exist and are registered. It does **not** test report content; the report has no AI disclosure (P-002). Do not read this PASS as R22 compliance. |
| R05 | SKIPPED | No TeX toolchain. **Settled by the PDF instead:** 16 counted pages (§4) → PASS. |
| R06 | PASS | Correct outcome, stale floor: `FONT_FLOOR_PT = 10` (`check_compliance.py:11`) while R06 is `corrected` to an 11 pt-equivalent floor. 12 pt passes both. |
| R07 | PASS | Declarations only; the regex accepts any `\setstretch`. The PDF confirms the layout (§5). |
| R08 | MANUAL | Should be PASS. The detail text says "R09 is status: ask" (`check_compliance.py:87`), but R09 is `confirmed` (bibliography URLs are allowed by GUIDE2027 5e). One URL, in `\bibitem{case118}` (l.424). |
| R10 | **FAIL** | **False negative (P-006).** The regex `\\apacite\|APA:\|\(\d{4}\)\.` (`check_compliance.py:122`) rejects the rule book's own example form. All 7 floats have an attribution line (§2). |
| R12 | SKIPPED | Settled by the PDF: folios sit bottom right (x 528–540 pt, y 742 pt) and start at 1 on p3. Title and abstract pages are unnumbered. → PASS. |
| R13 | PASS | Correct: no email or phone before `\maketitle`. The title page carries the name and title. |
| R14 | SKIPPED | Size is now measurable: 1.24 MB, under 4 MB → PASS. The filename still needs the home ZIP, which is not in the repo (author). |
| R21 | **FAIL** | Same false negative as R10 (P-006). See §2 for a per-element check. |

The MANUAL rows are advisory rows with `check: null` and are not scored here, except the ones covered in §5.

**Confirming P-006 against the R21 verbatim example.** The example is "Graph created by the student researcher using
BioRender, 2024." It has three elements: student attribution, program, and year. The 7 lines in the .tex are:

| .tex line | Float | Text |
|---|---|---|
| l.158 | Fig. 1 | Graph created by Rajan Saha using Matplotlib 3.11.1, 2026 |
| l.223 | Table 1 | Table created by Rajan Saha using Python and \LaTeX, 2026 |
| l.265 | Table 2 | Table created by Rajan Saha using Python and \LaTeX, 2026 |
| l.284 | Fig. 2 | Graph created by Rajan Saha using Matplotlib 3.11.1, 2026 |
| l.306 | Fig. 3 | Graph created by Rajan Saha using Matplotlib 3.11.1, 2026 |
| l.327 | Fig. 4 | Graph created by Rajan Saha using Matplotlib 3.11.1, 2026 |
| l.342 | Fig. 5 | Graph created by Rajan Saha using Matplotlib 3.11.1, 2026 |

All seven have the same structure as the example. The only difference is that they give the student's name instead
of the phrase "the student researcher". Every line renders in the PDF directly under its float, at \scriptsize
(≈ 8 pt, text height 7.2 pt in the bbox). R06 allows smaller captions if legible. `matplotlib.__version__` in
`.venv` = 3.11.1 (VERIFIED). **P-006 confirmed: the FAIL is a checker defect, not a report defect.** The substantive
exception is Fig. 5's program element (§2).

---

## 2. Float audit (PDF-rendered)

LaTeX `article` numbers these **Figure 1–5, Table 1–2** (Arabic). The .tex header comment (l.22–23) says
"Table I-II", which is stale; the prose uses `\ref`, so nothing hard-codes a numeral. The first `\ref` of each float
is the first mention, since there are no hard-coded "Fig. N" strings.

| Float (label) | Rendered no. | First `\ref` (line → page) | Float position | Cited before shown? | `\ref` count | Credit line: student / program / year | Used in argument? |
|---|---|---|---|---|---|---|---|
| `fig:gate` | Figure 1 | l.143 → p7 | top of p8 | yes | 1 | Rajan Saha / Matplotlib 3.11.1 / 2026 ✓ (`feasibility/gate_schematic.py` imports matplotlib) | Explanatory schematic, cited once as a parenthetical. Acceptable. |
| `tab:models` | Table 1 | l.199 → p9 | mid p9, after the citing paragraph | yes | 3 (l.199, 292, 349) | Rajan Saha / Python and LaTeX / 2026 ✓ | yes |
| `tab:ops` | Table 2 | l.231 → p9 | top of p10 | yes | 1 | ✓ | yes: its values are quoted without `\ref` at l.231, 292, 349 |
| `fig:tradeoff` | Figure 2 | l.231 → p10 | top of p11 | yes | 1 | ✓ | **The single citation claims error bars that the rendered figure does not draw (P-005).** Its one use is for a property it lacks. The replacement `data/sts_tradeoff_bands.png` now exists with the same pixel size, so swapping costs 0 pp. |
| `fig:missdepth` | Figure 3 | l.292 → p10 | top of p12 (two pages after citation, behind Fig. 2) | yes | 1 | ✓ | yes (74/55% shares). Content is FATAL-linked (P-001). |
| `fig:boundary` | Figure 4 | l.314 → p11 | top of p13 (float-only page) | yes | 1 | ✓ | yes (the 56.86% strip) |
| `fig:busmap` | Figure 5 | l.314 → p12 | bottom of p13 (float-only page) | yes | 1 | **Program incomplete:** node layout is `pandapower.plotting.create_generic_coordinates(..., library="igraph")` (`feasibility/domain_figure.py:30`), and the credit names only Matplotlib. The d-figs replacement is `scripts/sts_critical_bus_map.py`, same issue: its layout source should be checked before the credit is written. | **Cited once and not used in the argument.** "as shown in Fig. 5" repeats shares already in the text, and no inference is drawn from the figure. The rendered image is also stale (0-based labels 75/52/106 against caption 76/53/107, P-004). |

**Order:** citation order is Fig 1 (l.143) → Tab 1 (l.199) → Tab 2 (l.231) → Fig 2 (l.231) → Fig 3 (l.292) → Fig 4
(l.314) → Fig 5 (l.314). Figures and tables are each numbered in citation order. **No float is out of order. No float
appears before its first citation.**

**Layout side effect (not a rule issue):** p13 holds only Fig. 4 and Fig. 5 with zero text rows. It splits the
sentence "Persistence is the baseline model where the voltage before the outage of one element is assumed | to be equal
…" across p12 and p14.

Unreferenced labels, all harmless: `sec:intro`, `sec:background`, `sec:results`, `sec:conclusion`,
`subsec:theory`, `subsec:crossnet`, `subsec:ablation`. Two stale comments: l.332 names `fig:critical` while the label
is `fig:busmap`, and l.297 names `miss_depth_v2.png` while the file used is v3 (both are P-025).

---

## 3. Definition-before-use audit

"Abstract" = l.81 (p2). Body first use is listed separately, because the body has to stand without the abstract.
**Verdicts:** OK = defined at or before first body use. LATE = defined later in the body. NEVER = no definition.

| Term | First use (abstract / body) | First definition | Verdict |
|---|---|---|---|
| N-1 | l.81 / l.97 | l.97 ("determines whether … after an element fails") | OK. It later conflicts with "two elements out" (l.111) against "still N-1" (l.367), per C6. |
| N-0 | — / l.107 | l.107 | OK |
| contingency | title l.63, l.81 / l.97 | l.111 ("Each contingency subjects a single line or transformer to failure"). Only implied by context at l.97. | LATE (l.97 → l.111), minor |
| per-unit (pu) | l.81 / l.107 | l.107 | OK in body; undefined in abstract |
| AC | l.81 / l.97 | Never tied to the abbreviation. "alternating-current" appears only at l.119, and what an AC solve is (nonlinear, full voltage) is never contrasted with DC. | NEVER (as a defined term) |
| DC | l.81 (expanded "direct current (DC)") / l.101 | Never explained: it is not stated what a DC model drops (voltage magnitudes). The Christianson contrast at l.101 depends on it. | NEVER (meaning) |
| surrogate | l.63, l.81 / l.101 | l.124 (what it predicts). l.99 describes a "fast approximation" without using the word. | LATE (l.101 → l.124), minor |
| conformal | l.63, l.81 / l.101 | l.128 | LATE (l.101 → l.128), minor |
| split-conformal | l.81 / l.128 | l.128, with the split at l.124 | OK |
| coverage | l.81 / l.128 | l.128 (P(true ≥ lower edge)), then **redefined** at l.231 as the acceptance rate | Defined, then overloaded (see list below): **MAJOR** |
| coverage target | l.81 ("0.97 coverage target") / l.208 ("target coverage"), l.231 ("the target") | **Never.** No α, and nothing says the target is the nominal level used to set q̂. Closest is "desired probability" (l.132). Fig. 2 calls it "safety target" (l.281). | **NEVER: MAJOR** |
| escalation / escalate | l.81 (defined in abstract) / l.99 ("escalated cases"), l.101 ("floor for escalation") | l.141 | LATE (l.99 → l.141). The denominator of "escalation rate" is never stated. **"Escalation floor"** (l.101, 312, 365, 388) is never given a value (P-014). |
| certify | abstract says "classify … as safe" / l.99 (informal) | l.139 | OK-ish (informal use first) |
| flag | l.81 / l.107 (generic "this study flags any part of the grid") | l.140 | OK. l.107 uses the word in a different, generic sense. |
| missed rate | l.81 ("misses 4.72% of violations") / l.199 | l.208, Table 1 caption: "share of true violations" (denominator only) | LATE (l.199 → l.208). The numerator (certified ∧ true violation) is **never stated**. |
| boundary mass | l.63 (title) / l.353 | **Never.** l.353 uses it as a predictor input. The strip share is given at l.121/l.314 but never named. The abstract says "boundary band" (l.81), and the heading at l.312 says "boundary layer". | **NEVER: MAJOR (C12)** |
| band width q̂ | — / l.121 ("band width relation"), l.124 ("band width q̂") | l.128 | LATE (l.121 → l.128), minor |
| ρ | — / l.353 (only use) | l.353, in words only ("how crowded the voltages are just above the limit"). No formula, window width, or units, although ρ·q̂ is predictor A. | Vague; not reproducible |
| speedup | l.81 ("3.29 times faster") / l.143 | l.145 (Eq. 2) | OK |
| base case | l.81 / l.107 | l.107 | OK in body; undefined in abstract. Synonyms "bases" (l.119) and "base scenarios" (l.124). |
| bus | l.81 ("118-bus") / l.107 | l.111 ("the junctions where voltage is measured") | LATE by one paragraph, minor |
| PV / PQ | not used anywhere | — | n/a. The concept (generator voltage control, "generator bus" l.121) is used without definition. |
| reactive power | — / l.111 ("generator reactive power limits are enforced") | **Never.** The only functional gloss is at l.367 ("can no longer control the voltage"), and it is the P-001 claim. Also l.119 "reactive power scales". | **NEVER: MAJOR (load-bearing for l.367)** |
| histgb | — / l.147 | l.208 (Table 1 caption: "histgb is the gradient-boosted model"). The model is described at l.124. | LATE (l.147 → l.208). Three names are used: histgb / gradient-boosted model / histogram-based gradient boosting. |
| ridge | l.81 / l.124 | l.124 names it ("ridge linear regression … standardized inputs"). The penalty is never explained. | OK (named). Synonym "linear model". |
| MAE | — / l.199 (spelled out), l.213 (abbreviation in table header) | l.373 ("mean absolute error (MAE)") | Abbreviation LATE (l.213 → l.373), minor |
| R² | — / l.199 | never | NEVER, minor (standard term) |

Two gaps outside the list: *y* is used at l.175 and never defined as the true minimum voltage (P-017), and "case118"
is a code identifier used in the abstract (l.81) and at l.107 before l.111 names the IEEE 118-bus system.

**Three worst gaps:** (1) **boundary mass**: it is in the title and never defined, it has four names, and ρ has no
formula. (2) **coverage target / coverage**: the target is never defined, the word carries three senses, and l.199
uses two of them in one sentence. (3) **reactive power**: it is undefined, yet the Discussion's worst-case mechanism
(l.367) rests on it. The undefined "escalation floor" (P-014) is a close fourth.

### Every "coverage" in the text (comments excluded): 26 occurrences

Senses: **S1** = conformal coverage, P(y ≥ lower edge), empirical or guaranteed. **S2** = acceptance rate
(selective-prediction coverage: the share decided without the solver). **S3** = the target knob (nominal level).

| # | Line | Context | Sense |
|---|---|---|---|
| 1 | 81 | "at 90% coverage, the gradient-boosted model is 3.29 times faster" | S3 |
| 2 | 81 | "at a 0.97 coverage target" | S3 |
| 3 | 81 | "the gradient-boosted model at 0.97 coverage results in a 5.84±1.25% escalation" | S3 |
| 4 | 128 | "into a coverage guarantee (the probability that the true voltage is at or above …)" | S1 (definition) |
| 5 | 128 | "q̂ as the quantile for the coverage of the model overshoot" | S3 (quantile level; could be read as S1) |
| 6 | 132 | "A single quantile coverage is the easiest way to choose the band" | S1 (method sense) |
| 7 | 132 | "At a 90% coverage level, the calibrated band widths are" | S3 |
| 8 | 199 | "At 90% coverage, the ridge model escalates 49.1%" | S3 |
| 9 | 199 | "has 89.3% coverage" | S1 (empirical) |
| 10 | 199 | "has 89.8% coverage" | S1 |
| 11 | 199 | "as the coverage is close to 90%" | S1 |
| 12 | 208 | Table 1 caption "at 90% target coverage" | S3 |
| 13 | 231 | "risk–coverage curve for selective prediction" | S2 |
| 14 | 231 | "(where coverage is the acceptance rate)" | S2 (definition) |
| 15 | 241 | Table 2 caption "at each coverage target" | S3 |
| 16 | 241 | Table 2 caption "empirical coverage" | S1 |
| 17 | 281 | Fig. 2 caption "at 0.94 coverage for ridge" | S3 |
| 18 | 292 | "not safer at any point in the coverage axis" | S3 (Fig. 2 x-axis) |
| 19 | 292 | "at a coverage of 0.96" | S3 |
| 20 | 292 | "At 0.90 coverage, 74% of misses" | S3 |
| 21 | 303 | Fig. 3 caption "at 90% coverage" | S3 |
| 22 | 349 | "at a 0.94 or a 0.97 target coverage" | S3 |
| 23 | 353 | "9 coverage targets" | S3 |
| 24 | 363 | "the coverage rates are measured averages" | S1 |
| 25 | 365 | "coverage target of 0.97" | S3 |
| 26 | 388 | "At 90% coverage, both methods perform very fast" | S3 |

**Counts: 3 senses. S1 = 7, S2 = 2, S3 = 17.** Adjacent labels: Table 2 has a "Cov." column (S1) and a "Target"
column (S3), and Fig. 2 names S3 "safety target" (l.281), a fourth name. **Collision:** at the "90% coverage"
operating point, S2 (acceptance = 100 − escalation) is 50.9% for ridge and 69.4% for histgb (from Table 2: 100 − 49.1,
100 − 30.6). So the same word points to three different numbers (90, 89.3/89.8, 50.9/69.4) within l.199–231.

---

## 4. Page budget (measured on `paper_v39.pdf`)

**Counted pages = 16** (body p3–p18 = folios 1–16). Title p1 and abstract p2 are unnumbered, references p19–20 are
excluded, and there is no appendix. **4 pages free under the 20-page cap.**

Geometry measured from `-bbox-layout`: text block x 72–540 pt and y 72–720 pt. Body baseline pitch is **21.67 pt**
(literal 1.5 × 14.45 pt), so a page holds **29.9 body rows**.

| Page (folio) | Body text rows | Floats (approx. share of page incl. separation) | Blank at foot |
|---|---|---|---|
| p3 (1) | 25 + section heading | — | **79 pt (0.12 pp)**. Section II moved to p4; consistent with a heading plus two lines not fitting. |
| p4 (2) | 28 + heading | — | 14 pt |
| p5 (3) | 27 + 2 headings | — | 1 pt |
| p6 (4) | 23 + 2 headings + Eq. 1 | — | 16 pt |
| p7 (5) | 24 + 2 headings + list + Eq. 2 | — | 0 |
| p8 (6) | 16 incl. Eqs. 3–5 | Fig. 1 ≈ 0.35 | 15 pt |
| p9 (7) | 19 + 2 headings | Table 1 ≈ 0.26 | 0 |
| p10 (8) | 15 + heading | Table 2 ≈ 0.44 | 0 |
| p11 (9) | 13 + heading | Fig. 2 ≈ 0.52 | 10 pt |
| p12 (10) | 12 | Fig. 3 ≈ 0.62 | 0 |
| p13 (11) | **0** | Fig. 4 ≈ 0.45 + Fig. 5 ≈ 0.51 (float-only page) | 18 pt |
| p14 (12) | 27 + heading | — | 18 pt |
| p15 (13) | 27 + section heading | — | 6 pt |
| p16 (14) | 27 + heading | — | 18 pt |
| p17 (15) | 26 | — | **92 pt (0.14 pp)**. Section VI moved to p18. |
| p18 (16) | 13 + 2 headings (Conclusion 11 rows, Acknowledgments 2 rows) | — | **275 pt = 0.42 pp ≈ 12.7 rows ≈ 190 words** |

Totals: 322 body rows ≈ 10.8 pp; floats ≈ 3.2 pp; headings, equations and list spacing ≈ 1.3 pp; blank ≈ 0.7 pp.
Content ends at 15.58 counted pages.

### Ledger unit costs checked against the PDF

| Ledger unit (`placement_plan.md:130`) | Measured | Verdict |
|---|---|---|
| 345 words/page | Full-text pages p4 = 452, p14 = 432, p15 = 443 words (pdftotext tokens, folio excluded; each carries one heading). Mean 442; 15.3 words per body row; a heading-free page ≈ 457. For tex words: ablation l.369–379 = 446 words over ≈ 1.12 pp incl. heading ≈ 400/pp. | **Density is ~25% higher than 345.** The `sts_review.md:599` figure of 285 w/p at literal 1.5 is wrong: the compile is literal 1.5 and denser. |
| one sentence (~25 words) ≈ 0.07 pp | 1.7 rows ≈ 0.057 pp | Conservative by ~20% |
| one table row ≈ 0.03 pp | 13.5 pt ≈ 0.021 pp (Tables 1–2) | Conservative |
| small table (5–6 rows + caption + credit) ≈ 0.35 pp | Table 1 (4 rows, 3-line caption) ≈ 0.26; 6 rows ≈ 0.30 | Slightly conservative |
| figure at 0.6\textwidth + caption ≈ 0.45 pp | Fig. 4 (2.71 in image) 0.45; Fig. 2 (3.23 in) 0.52; Fig. 3 (4.09 in) 0.62. Overhead for a 4-line caption + credit + separation ≈ 106 pt. | Right only for landscape figures. **The new d-figs PNGs are portrait:** `sts_limit_sweep.png` 1015×1259 → 4.84 in at 0.6 tw → **≈ 0.70 pp** (E1c, ledger 0.6). `sts_crossnet_scatter.png` 977×1164 → 4.65 in → **≈ 0.68 pp** (E2a, ledger 0.45). `sts_tradeoff_bands.png` = same pixels as Fig. 2 → 0. `sts_critical_bus_map.png` 3.05 in at 0.55 tw vs 3.10 in now → 0. |
| E14 ablation −0.9 | The section is 1.12 pp for 446 words; cutting to 150–200 words saves ≈ 0.60–0.65 pp | Overstated by ~0.27 |
| Cut-3 reject digression −0.4 | The digression is 118 words ≈ 0.27 pp in total; cutting to one sentence saves ≈ 0.20 | Overstated by ~0.2 |
| Cut-5 case57/pegase −0.3 | 114 words ≈ 0.26 pp in total; cutting to one sentence saves ≈ 0.20 | Overstated by ~0.1 |
| Cut-7 merge l.361–363 −0.4 | Block is 204 words ≈ 0.47 pp in total; a merge saving half ≈ 0.23 | Likely overstated by ~0.17 |
| E15 S_mean −0.25 | 83 words + one display equation ≈ 0.28 | OK |
| Fig. 5 cut −0.5 | 0.51 | OK |

### Projected total

1. **Ledger §2 arithmetic, rows as listed:** Step 1 +0.15 → Step 2 1.87 → Step 3 2.04 → Step 4 (Cut-3 −0.4,
   Cut-5 −0.3, Cut-6 −0.3 + P-011 table +0.35, Cut-7 −0.4) = **0.99** with Fig. 5 kept, or 0.49 with it cut → Step 5
   +0.3 = **1.29 / 0.79**. The ledger's "≈0.9–1.4 after Step 4" does **not** follow from its own rows. It reproduces
   only as the post-Step-5 total with the next item added.
2. **Ledger rows with a page cost that §2 omits:** P-003 +0.1, P-007 +0.07, P-010 +0.05, P-013 +0.03, P-019 +0.03,
   P-020 +0.03, Top-5 #2(a) theory −0.2 → **+0.11**. Plan net = **1.40 (Fig. 5 kept) / 0.90 (Fig. 5 cut)**.
3. **Unit-cost correction from the PDF:** portrait figures +0.33; cuts save less, +0.71; prose adds cost less
   (about 2.45 pp of adds × 0.83), −0.42. Net **+0.62**. Corrected plan net = **≈ 2.0 / 1.5 pp**.
4. **Counted pages:** 15.58 + 2.0 = 17.6 → **18 counted pages** with Fig. 5 kept. 15.58 + 1.5 = 17.1 → **17–18**
   with Fig. 5 cut. Options outside the plan (C8 risk panel +0.45, E10 as a table +0.29 over sentences, E7 Mondrian
   +0.15) add ≈ 0.9 → **≈ 19**.

**Confidence without a compile: moderate. Central estimate 18, range 17–19.5.** The main uncertainty is float
placement. The current compile already loses 0.26 pp to headings pushed over page breaks (p3, p17), and p13 is a
float-only page. E1b, E1c and E2a all land in IV-C/IV-D next to Fig. 4 and Fig. 5, so a second float-only page (up to
~0.5 pp of white) is plausible. The cap is only at risk if every option is taken and floats place badly. An Overleaf
compile after Step 2 is the check that settles this.

---

## 5. Rules the report text must satisfy (current file)

| Rule | Verdict | Evidence |
|---|---|---|
| R05 page cap | **PASS** | 16 counted pages (§4); no appendix. |
| R06 font | **PASS** | `\documentclass[12pt]` with newtx Times. Body glyph box 10.8 pt, consistent with 12 pt. Captions `\small` (10.95 pt). Table bodies `\small` (10.95 pt, borderline against the 11 pt-TNR floor). Credit lines `\scriptsize` (8 pt), covered by "Captions may be smaller if legible". |
| R07 layout | **PASS** | Measured: one column; margins 72 pt on all four sides (text x 72–540, y 72–720); baseline pitch 21.67 pt = literal 1.5, which satisfies either reading of "1.5 spacing". The header comment l.8–12 (`\onehalfspacing`) is stale: the file uses `\setstretch{1.5}` at l.75 (§8-3). |
| R08 links | **PASS** | The only URL is in `\bibitem{case118}` (l.424), allowed by the 5e exception. hyperref's internal cross-refs are not external links. |
| R10 / R21 graphics citation | **PASS for 6 of 7; Fig. 5 NEEDS AUTHOR** | Every float carries student, program and year (§1, §2). Fig. 5 names Matplotlib only; its layout comes from igraph via pandapower. Its Overleaf image is also stale (P-004). The report names the student ("Rajan Saha") instead of saying "the student researcher": the rule's element is present, and the exact form is an author choice. Checker FAIL is P-006. |
| R13 contact details | **PASS** | Title page p1: name, title, school, program; no email or phone. |
| R18 published work | **NEEDS AUTHOR** | The URTC paper (`paper_current_URTC_20260808.tex:48–55`: Saha first author, Pinsky second) is not mentioned. The .tex header l.3 says "Body text is VERBATIM from the URTC conference version". R18 asks for acknowledgment "in your application" and "your own version … that highlights your actual contributions". R27 bounds co-author text (P-012). |
| R20 disclosure | **FAIL (as written)** | The Acknowledgments (l.393) names BU RISE and "teaching fellows and staff". It does not say the program was paid, names no instructors, omits the URTC co-author, and has no AI line. Where the disclosure goes (report or application) = author decision. |
| R22 / R04 generative AI | **FAIL (current file)** | No AI disclosure and no citation of AI-generated code portions anywhere in the .tex (ledger C7 grep; re-confirmed in this audit: the only "AI" hits are the l.101 foundation-model mention and a bib title). The prompt log exists (`notes/ai-prompt-log.md`). Placement = author/STS (P-002). |
| R23 no literature review beyond short intro | **NEEDS AUTHOR (borderline)** | The Introduction's prior-work paragraph (l.101) is short. But l.314 spends 118 words on Chow, Tsybakov and Mammen inside Results, including "he proved that the rejection threshold is …", and l.361–363 (204 words) positions the work against the literature in Discussion. The rule excludes "history of literature beyond the short introduction" and "detailed explanations of … procedures of other researchers". l.101 also describes Manoharan's procedure (randomized full solves). Cut-3 and Cut-7 bear on this. |
| R24 first person | **PASS** | 49 "I", 5 "my", and 0 "we", "our" or "the authors" in non-comment text. Some passive voice (l.119), which the rule allows. |
| R12 pagination (extra) | **PASS** | Measured (§1). |
| R14 size (extra) | **PASS** size; filename NEEDS AUTHOR | 1,236,133 bytes, under 4 MB. The ZIP code is not in the repo. |

---

## Notes for the lead

- Checker defects, not edited by me: the P-006 regex, the stale 10 pt floor at l.11, the stale R09-ask text at l.87,
  and R04 PASS testing only the hooks. The owner decides whether to change the gate.
- I did not append to `notes/ai-prompt-log.md`. Ledger §8-4 says the lead logged this run's prompt.
- Commit candidate for the owner: `notes/panels/compliance_round1.md` (new file only).
