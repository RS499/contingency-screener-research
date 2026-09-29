# Prior-art verification

Verification pass (2026-07-19). Read-only. Every entry below was checked against a live source,
not asserted from memory (assistant training cutoff is Jan 2026, so all 2026 arXiv IDs rest on
live retrieval). Status legend:

- **VERIFIED [FETCHED]** - the arXiv/abstract page was fetched; title, authors, year, ID confirmed.
- **VERIFIED [SEARCH]** - confirmed via live search results + an external corroborator (github,
  known venue), but the full paper was not individually fetched.
- **SEARCH-LISTED** - appears as a real result in live search with a working arXiv ID/URL, but
  authors/venue were not individually confirmed by fetch. Treat as a lead, not a settled citation.
- **NOT FOUND** - no source located; search terms recorded in the search log.

This file gathers evidence only. It contains no novelty or differentiation claims; the "factual
delta" rows state plain, checkable differences, not contribution claims.

**Addendum 2026-07-21.** The full text of arXiv:2602.07995v2 was read. The 2026-07-19 pass had
confirmed the identifier and abstract and done a quick HTML skim; that skim mischaracterized the
paper's demonstrated scope. See section 6 for the corrections. Claims elsewhere that still rest only
on the 2026-07-19 pass are flagged in section 6.6, including the arXiv:2607.13221 record, which was
not re-read.

**Addendum 2026-07-23.** Two peer-reviewed primitives were verified and added to B6 to replace two
LLM-routing preprints (C3PO / arXiv:2511.07396 and RouteNLP / arXiv:2604.23577) in the
1_research_draft.txt bibliography: Cortes-DeSalvo-Mohri, "Learning with Rejection" (ALT 2016), for the
reject-option lineage, and DeSalvo-Mohri-Syed, "Learning with Deep Cascades" (ALT 2015), for the
model-cascade lineage. The C3PO / RouteNLP A2 rows below are kept as evidence that they were
considered and replaced, not deleted. Fields verified against Crossref and dblp; the Springer chapter
pages sit behind an auth redirect and were not fetched directly. See B6 and the search log.

## 1. Claims table (A - named precedents from the notes)

| Claim | Status | Source (title, authors, year, venue, ID) | What it actually does | Factual delta vs this project |
|---|---|---|---|---|
| A1. arXiv:2602.07995v2; conformal + power-system contingency screening | VERIFIED [FETCHED]: metadata 2026-07-19, FULL TEXT read 2026-07-21 | *Trustworthiness Layer for Foundation Models in Power Systems: Application to N-k Contingency Screening*; Antonio Alcantara, Spyros Chatzivasileiadis; arXiv:2602.07995v2 (2602 identifier = Feb 2026 submission; v2 stamped 21 Apr 2026; accessed 2026-07-21) | Conformal intervals (stratified SCP + kernel-weighted KCP) on a foundation model's predictions; flags conservatively when the interval upper bound crosses the limit. Scope CLAIMED for voltage magnitudes; DEMONSTRATED on line loading only (Table I: line-congestion screening, recall/precision by N-k level; conformal upper bound on derived line loading, flagged when it exceeds 1.0). Full text: NO escalation to an exact solver, NO net-cost accounting, decision is a BINARY flag. | Three-way certify/flag/ESCALATE gate to an exact AC solve, net-cost accounting, boundary-mass floor, and voltage screening actually DEMONSTRATED. Correction in section 6: an earlier note said "does cover voltage (correcting the notes)" - that read the paper's CLAIMED scope as demonstrated capability and was itself wrong. |
| A2. "UCCI" real or garbled | VERIFIED [FETCHED] | *UCCI: Calibrated Uncertainty for Cost-Optimal LLM Cascade Routing*; Varun Kotte; 2026; arXiv:2605.18796 | Maps token-level margin uncertainty to a per-query error probability via isotonic regression; selects the escalation threshold by constrained cost minimization. | LLM domain, text tasks; escalation target is a larger LLM, not an exact physics solver; no voltage/physical-unit band. |
| A2. "C3PO" real or garbled | VERIFIED [FETCHED] | *C3PO: Optimized LLM Cascades with Probabilistic Cost Constraints for Reasoning*; A. Valkanas, S. Pal, P. Rumiantsev, Y. Zhang, M. Coates; 2025; arXiv:2511.07396 | Self-supervised, label-free LLM cascade; uses conformal prediction to bound P(inference cost > budget); PAC-Bayes accuracy guarantee. | LLM domain; conformal bounds the COST-exceedance probability, not a physical safety margin; deferral target is a larger LLM. |
| A2. "RouteNLP" real or garbled | VERIFIED [FETCHED] | *RouteNLP: Closed-Loop LLM Routing with Conformal Cascading and Distillation Co-Optimization*; D. Guo, J. Wu, S.M. Yiu; 2026; arXiv:2604.23577 | Router + conformally-calibrated cascade escalation threshold + distillation feedback loop. | LLM domain; escalation target is a larger LLM; no physical-unit band, no exact-solver fallback. |
| A3. "conformal triage" a real three-way term | VERIFIED [SEARCH] | *Conformal Triage for Medical Imaging AI Deployment*; A.N. Angelopoulos et al.; medRxiv 2024; code github.com/aangelopoulos/conformal-triage | Three-way low-risk / high-risk / uncertain partition with PPV/NPV guarantees. | Medical imaging; the deferral target is a HUMAN reviewer, not an expensive computation; classification not regression against a physical limit. |

Headline on A: none of UCCI / C3PO / RouteNLP were invented or garbled. All three are real papers
that pair conformal prediction with a cost-based escalation threshold in an LLM cascade. The
mechanism "calibrated uncertainty routes uncertain cases to a costlier model" is well populated
in the 2024-2026 LLM literature.

## 2. Field maps (B)

### B4. Conformal prediction in power systems
Predominantly forecasting; one contingency-screening paper.
- VERIFIED [FETCHED]: *Trustworthiness Layer ...* (2602.07995) - the only conformal + contingency
  screening paper found (see A1).
- SEARCH-LISTED: *Hierarchical Probabilistic Conformal Prediction for DER Adoption* (arXiv:2411.12193);
  *Conformal Prediction for Electricity Price Forecasting* (arXiv:2502.04935); *Stochastic MPC of
  Charging Hubs with Conformal Prediction* (arXiv:2504.00685); microgrid net-load CP (ResearchGate,
  2026). These apply CP to forecasting / market / DER problems, not contingency screening.

### B5. ML surrogates for N-1 screening with uncertainty / exact-solver fallback
- VERIFIED [FETCHED], closest to this project: *Audited Selective Verification for Risk-Controlled
  N-1 Thermal Contingency Screening under Deployment Shift*; Jayakumar Manoharan; 2026; arXiv:2607.13221.
  Cheap surrogate (LODF-based danger score) proposes skips; a random audit runs EXACT AC on a subset;
  a fixed-sequence Learn-Then-Test / Clopper-Pearson threshold bounds the thermal-violation rate for
  skipped cases; net AC-solve count is reported (3 s -> 0.8 s). Target is THERMAL. No boundary-mass /
  margin-density floor argument (searched: "boundary", "margin", "near", "density", "concentrate" -
  none in that sense; only the statistical audit minimum n_min = ceil(ln delta / ln(1 - alpha))).
  Factual delta: this project targets VOLTAGE, escalates PER-INSTANCE via a one-sided conformal
  residual band (not a random population audit), uses split-conformal (not LTT/Clopper-Pearson), and
  reports a boundary-mass floor; shared: surrogate + exact-AC fallback + net cost + shift concern.
- SEARCH-LISTED: *Fast and Reliable N-k Contingency Screening with Input-Convex Neural Networks*
  (arXiv:2410.00796); *Graph Neural Networks for Fast Contingency Analysis* (arXiv:2310.04213);
  *Deep Learning for Power System Security Assessment* (arXiv:1904.09029).

### B6. Selective prediction / learning-to-defer (target = expensive computation)
- VERIFIED [SEARCH]: *SelectiveNet: A Deep Neural Network with an Integrated Reject Option*;
  Y. Geifman, R. El-Yaniv; ICML 2019; arXiv:1901.09192 (also proceedings.mlr.press/v97/geifman19a).
  End-to-end classification-with-reject.
- SEARCH-LISTED: *Predict Responsibly: Increasing Fairness by Learning to Defer* (Madras, Pitassi,
  Zemel, 2018); *Post-hoc Estimators for Learning to Defer to an Expert* (Narasimhan et al., NeurIPS
  2022); *Selective Classification via One-Sided Prediction* (arXiv:2010.07853, relevant to the
  one-sided band). In all classic L2D work the deferral target is a HUMAN expert. Deferring to an
  expensive COMPUTATION is populated mainly by the LLM cascade line (A2) and B5's 2607.13221.
- VERIFIED [FETCHED] (2026-07-23): *Learning with Rejection*; C. Cortes, G. DeSalvo, M. Mohri; ALT
  2016, Lecture Notes in Comput. Sci. vol. 9925, Springer, pp. 67-82; DOI 10.1007/978-3-319-46379-7_5.
  The reject-option primitive (a paired predictor + rejector trained with an explicit rejection cost)
  that the paper's flag/escalate branch descends from. Two independent sources: Crossref
  (api.crossref.org/works/10.1007/978-3-319-46379-7_5, confirmed authors/title/pages/year/DOI) and
  dblp (dblp.org/rec/conf/alt/CortesDM16.bib, confirmed LNCS series vol. 9925). The Springer
  link.springer.com page redirects to an auth wall and was not fetched directly.
- VERIFIED [FETCHED] (2026-07-23): *Learning with Deep Cascades*; G. DeSalvo, M. Mohri, U. Syed; ALT
  2015, Lecture Notes in Comput. Sci. vol. 9355, Springer, pp. 254-269; DOI
  10.1007/978-3-319-24486-0_17. The peer-reviewed deep-cascade primitive underlying the model-cascade
  lineage from which the LLM routing preprints descend. Two independent sources: Crossref
  (api.crossref.org/works/10.1007/978-3-319-24486-0_17, confirmed authors/title/pages/year/DOI; 429 on
  first attempt, confirmed on retry) and dblp (dblp.org/rec/conf/alt/DeSalvoMS15.bib, confirmed
  publisher Springer and LNCS series vol. 9355). Springer page behind the same auth wall.

## 3. C7 - does a cheaper-than-AC VOLTAGE contingency screen exist?

**Yes.** Cheaper-than-full-AC voltage contingency screening is a classical, well-established field.
- Canonical citation (pinned): **Ejebe, G.C. and Wollenberg, B.F., "Automatic Contingency
  Selection," IEEE Transactions on Power Apparatus and Systems, PAS-98(1):97-109, 1979.** The
  foundational performance-index contingency-selection method; voltage-oriented performance-index
  variants (PI_V, PI_VQ) derive from this line. VERIFIED [SEARCH] (volume/number/pages from live
  search; widely cited standard reference).
- Method families found (SEARCH-LISTED): voltage-reactive-power performance index (PI_VQ) and
  composite security indices for ranking; sensitivity / voltage-stability indices (FVSI, sensitivity
  factor index, tangent-vector index, VQI, VCPI); non-iterative reactive-support / voltage-security
  screens via Norton equivalent; and older neural voltage screens (e.g. cascade-NN voltage screening,
  Electric Power Systems Research, 1999).
- NOTE (added 2026-08-21): the "pandapower" mentions in this subsection are about the TOOL's
  feasibility for computing FVSI-type indices. They are NOT a provenance record for the bibitem
  `pandapower` (Thurner et al., IEEE Trans. Power Syst., 2018). That record is section 8.3, verified
  2026-08-21. The automated gate in `scripts/check_citations.py` matched the software name here and
  reported a record that did not exist.
- pandapower feasibility: PARTIAL. These screens typically need one base-case AC solve plus
  sensitivities (pandapower exposes Ybus and the Jacobian; FVSI-type line indices are computable from
  a single solved base case). So a PI_VQ- or sensitivity-based voltage screen COULD be built on
  pandapower, but it yields a RANKING / approximation, not exact min_vm, and usually still needs a
  base AC solve. It is a real alternative baseline to brute-force AC, distinct from DC/LODF (which
  cannot see voltage at all - separately verified: DC min_vm stays at the min generator setpoint
  0.9430 across load 1.0-1.6x while AC collapses to 0.87).

## 4. Search log (every query, for reproducibility)

WebFetch:
1. arxiv.org/abs/2602.07995  (exists? title/authors/abstract)
2. arxiv.org/abs/2605.18796  (UCCI details)
3. arxiv.org/abs/2511.07396  (C3PO details)
4. arxiv.org/abs/2604.23577  (RouteNLP details)
5. arxiv.org/abs/2607.13221  (ASV-N1 details)
6. arxiv.org/html/2607.13221v1  (full text: audit target, risk-control name, boundary/margin search, thermal scope)
7. arxiv.org/html/2602.07995v1  (full text: voltage/thermal, escalation, cost accounting, binary vs three-way)
8. api.crossref.org/works/10.1007/978-3-319-46379-7_5  (Learning with Rejection: authors/title/pages/year/DOI) [2026-07-23]
9. dblp.org/rec/conf/alt/CortesDM16.bib  (Learning with Rejection: LNCS series/volume 9925) [2026-07-23]
10. dblp.org/search/publ/api?q=Learning+with+Rejection+Cortes+DeSalvo+Mohri  (cross-check) [2026-07-23]
11. api.crossref.org/works/10.1007/978-3-319-24486-0_17  (Learning with Deep Cascades: authors/title/pages/year/DOI; 429 then confirmed on retry) [2026-07-23]
12. dblp.org/rec/conf/alt/DeSalvoMS15.bib  (Learning with Deep Cascades: publisher Springer + LNCS series/volume 9355) [2026-07-23]

WebSearch:
1. "LLM cascade routing cost-optimal threshold defer to larger model FrugalGPT RouteLLM"
2. "conformal prediction power system contingency analysis security assessment power flow"
3. "C3PO cascade routing LLM   RouteNLP model routing paper"
4. ""conformal triage" OR "conformal" three-way certify flag escalate selective classification"
5. "machine learning surrogate N-1 contingency screening security assessment neural network uncertainty fallback AC power flow"
6. "voltage contingency ranking selection performance index sensitivity-based screening reactive power fast"
7. "conformal prediction power systems load forecasting state estimation optimal power flow distribution-free intervals"
8. "selective prediction learning to defer reject option neural network Geifman El-Yaniv Madras defer expensive computation"
9. "Ejebe Wollenberg automatic contingency selection performance index 1979 IEEE Transactions power apparatus"

## 5. Still unverified after this pass

- Authors / venue for every SEARCH-LISTED paper in B4, B5, B6 (only the 5 table papers + 2607.13221
  were fetched to confirm authors).
- A single canonical citation for the VOLTAGE-specific PI_VQ (as opposed to the general Ejebe-
  Wollenberg 1979 selection method). Ejebe-Wollenberg is pinned as the foundational reference; the
  voltage-PI specialization is asserted from the field literature, not a single fetched paper.
- The §10 conformal foundations (Lei et al. 2018 JASA; Romano-Patterson-Candes 2019; Gibbs-Candes
  2021; Vovk-Gammerman-Shafer 2005) were NOT re-verified in this pass - they were out of scope for
  the A/B/C claim list but should be confirmed before they appear in any writeup.
- FrugalGPT and RouteLLM appear in search as real and are within the assistant's pre-cutoff
  knowledge, but were not fetched here; confirm IDs before citing.

## 6. Full-text read of arXiv:2602.07995v2 (2026-07-21)

Basis: on 2026-07-19 the prior-art pass confirmed the identifier, authors, and abstract, and did a
quick HTML skim. On 2026-07-21 the full text (v2) was read. The skim had recorded the paper's
demonstrated scope wrong. What follows rests on the full-text read; where a claim still rests only
on the 2026-07-19 pass it is marked (section 6.6).

### 6.1 Voltage vs thermal (this corrects a correction)
The framework is presented as applicable to voltage magnitudes, but the demonstration is line
loading. Table I is line-congestion screening, with recall and precision reported by N-k level; the
conformal upper bound is applied to derived line loading and flagged when it exceeds 1.0. So the
precise record is: voltage extension CLAIMED, thermal DEMONSTRATED. An earlier note recorded the
paper as "voltage-agnostic"; a later session overwrote that with "DOES cover voltage (correcting the
notes)". Both are wrong. The first missed the claimed voltage extension; the second read that claimed
scope as a demonstrated capability. Neither "covers voltage" nor "voltage-agnostic" is accurate.

### 6.2 Identifier and dates
Cite as arXiv:2602.07995v2. The 2602 identifier indicates a February 2026 submission; the v2 PDF is
stamped 21 April 2026. Record both. Access date 2026-07-21 (full text); metadata and abstract
verified 2026-07-19. The bare "February 2026, not April" phrasing used earlier is dropped: both
dates are real (Feb submission, April v2).

### 6.3 Anticipated objection: my gate uses the single global quantile they argue against
The paper's opening argument against standard split conformal is that a single global quantile is
valid but inefficient: it under-covers severe contingencies and is over-conservative on routine
ones. This project's gate uses exactly one global quantile. Their two remedies are both things this
project does not do:

- SCP stratifies calibration residuals by contingency level and grid element.
- KCP kernel-weights calibration residuals by similarity to the test scenario, giving locally
  adaptive bounds.

On IEEE-118 they report KCP roughly 64% tighter (mean q_hat 0.019 vs 0.054), with empirical coverage
90.0% (SCP) / 90.1% (KCP) against a 90% target.

Answer: the single global quantile is the baseline case, and the boundary-mass finding is that
escalation stays floored even as the band tightens, so a tighter locally adaptive band does not
remove the escalation floor on this network. Their q_hat values are on line loading and mine are in
pu voltage, so the numbers are not directly comparable. The argument is structural, not numeric.

### 6.4 Fall-planning fact
Locally adaptive conformal in this exact domain, on this exact network (KCP on IEEE-118), is already
published in this paper. Any future work applying locally adaptive conformal to this screener is an
application of a published method, not a novel contribution. Recorded here so it is not rediscovered
later as a new idea.

### 6.5 Baseline lesson (known limitation)
The paper benchmarks against DC power flow and a classical threshold-tuning baseline (uniformly
scaling the flagging threshold), reporting DCPF at roughly 0.59 ms vs ACPF 6.73 ms per scenario on
IEEE-118. That is a domain-appropriate baseline set. This project has only the trivial baselines
(persistence, train-mean); the DCPF and classical threshold baselines are not built. This is a known
limitation, and the gap the adversarial review flagged. It is recorded, not queued as work to start
now (freeze).

### 6.6 Flag: claims still resting only on the 2026-07-19 pass
Reading one full text overturned a recorded claim, so the same may be true elsewhere.
- arXiv:2607.13221 (section B5, the closest surrogate-plus-fallback paper): its whole record (LODF
  danger score, random audit running exact AC on a subset, Learn-Then-Test / Clopper-Pearson risk
  control, thermal scope, 3 s -> 0.8 s net solves, and "no boundary-mass argument") rests on the
  2026-07-19 HTML fetch and was not re-read on 2026-07-21. Re-read the full text before citing. The
  Task 6 finding that the boundary-mass floor is unclaimed by 2607.13221 depends on this record.
- novelty-review.md "IEEE 24/118", "N-k generalization", and "90% one-sided" for 2602.07995 are
  abstract-level framings, not re-confirmed against the full text.

## 7. Bibliography spot-checks (2026-07-28)

Four checks, requested against specific bibitems in `paper_current.tex`. Read-only; `.venv/bin/python`
used for all local PDF extraction; frozen files not touched. Every fetch below is dated 2026-07-28.

### 7.1 alcantara2026 title -- PDF header vs DBLP

Read directly from `notes/lit/Trustworthiness Layer for Foundation Models in Power Systems-
Application to N-k Contingency Screening.pdf`, page 1, via `pypdf` (local file, no fetch needed;
checked 2026-07-28):

> "Trustworthiness Layer for Foundation Models in
> Power Systems: Application to N-k Contingency
> Screening"
> Antonio Alcántara, Spyros Chatzivasileiadis, Senior Member, IEEE

This matches the bibitem's "Application to N-k contingency screening" exactly (modulo sentence-case
vs the PDF's title-case line wrap). The DBLP variant ("...Application for N-k Contingency Assessment"),
surfaced during the 2026-07-28 venue-resolution pass (see `notes/lit/_venues.md`), is DBLP's own
metadata mirror of the arXiv abs page and does not match the PDF header -- **the PDF header is the
primary source and is what the bibitem should follow; DBLP's variant is wrong (or reflects an abs-page
metadata field that itself diverges from the PDF, not verified further).**

### 7.2 ICNN paper (christianson25a) -- author list, title, pages

Fetched 2026-07-28: `https://proceedings.mlr.press/v283/christianson25a.html` (both the rendered
page and its BibTeX block).

Rendered page: "Nicolas Christianson, Wenqi Cui, Steven Low, Weiwei Yang, Baosen Zhang" -- "Fast and
Reliable $N-k$ Contingency Screening with Input-Convex Neural Networks" -- PMLR 283:527-539.

BibTeX block (verbatim):
```
@InProceedings{pmlr-v283-christianson25a,
  title = {Fast and Reliable $N - k$ Contingency Screening with Input-Convex Neural Networks},
  author = {Christianson, Nicolas and Cui, Wenqi and Low, Steven and Yang, Weiwei and Zhang, Baosen},
  booktitle = {Proceedings of the 7th Annual Learning for Dynamics \& Control Conference},
  pages = {527--539},
  year = {2025},
}
```
PMLR's own page gives full first names throughout, in both the display list and the BibTeX `author`
field -- there is no initials-only form on the source page to draw from.

### 7.3 ANSI C84.1 Range B lower bound

paper_current.tex line 177 claims: "ANSI C84.1 Range B extends to roughly 0.917 pu."

**Bibliographic identity -- primary-sourced, confirmed 2026-07-28.** Fetched
`https://www.nema.org/docs/default-source/standards-document-library/ansi-c84-1-2020-contents-and-scope...pdf`
(NEMA's own official free front-matter/TOC excerpt) and read it directly via `pypdf` after the
WebFetch tool's AI summary of it proved internally inconsistent (claimed "1995" title against a "2020"
URL) and was discarded in favor of reading the saved PDF bytes directly. The actual PDF header reads:

> "ANSI C84.1-2020, Revision of ANSI C84.1-2016, American National Standard for Electric Power
> Systems and Equipment -- Voltage Ratings (60 Hertz). Secretariat: National Electrical Manufacturers
> Association. Approved: March 10, 2020. American National Standards Institute, Inc."

So: **standard = ANSI C84.1-2020, publisher/secretariat = NEMA, approved by ANSI on 2020-03-10.**
This part is primary-source-verified.

**Numeric Range B value -- NOT verified against the approved 2020 text; the paid standard body was
not accessible.** The NEMA excerpt above is front matter/TOC only and does not include the numeric
Table 1. Two secondary sources were checked instead (fetched 2026-07-28):

- A Pacific Gas & Electric "Voltage Tolerance Boundary" document
  (`www.pge.com/assets/pge/docs/contact-us/report-an-issue/Voltage_Tolerance.pdf`), read via `pypdf`
  after WebFetch's summary reported the text as unreadable. States in prose: "The Range A service
  voltage range is plus or minus 5% of nominal. The Range B utilization voltage range is plus 6% to
  minus 13% of nominal" -- i.e. Range B **utilization** voltage lower bound = 0.87 pu (104V on a 120V
  base), not 0.917 pu.
- An unapproved, third-party-hosted 2016-revision **working draft** of the standard itself
  (`durastudio.com/.../ansi_c84-1-20xx_2016_revision_draft_2019-02-15.pdf` -- title page literally
  reads "ANSI C84.1-20XX" with "Approved: ________" left blank, i.e. not an approved/published text),
  read via `pypdf`. Its Table 1 for the 120 V nominal class contains the values 126, 114, 108, 127,
  110, 104. Note (b) to the table's illustrative figure states: "The difference between minimum
  service and minimum utilization voltages is intended to allow for voltage drop in the customer's
  wiring system" -- confirming Range B has two distinct minimums (service > utilization). Of the
  extracted values, 110/120 = 0.9167 pu and 104/120 = 0.8667 pu are the two candidates for these
  minimums; by the note's own logic (utilization is downstream of service, hence more drop) 110 is
  the **service** voltage minimum and 104 is the **utilization** voltage minimum. The value "108" in
  the extracted table could not be confidently assigned to a category from this text extraction alone
  and is left unresolved rather than guessed.

**Conclusion: do not guess further than this.** 0.917 pu (110/120) is a real number that appears
consistently across three independent sources (a general web search snippet naming "min of 110
volts" for Range B, the PG&E document's figure axis labels, and the unapproved draft's Table 1) and
most plausibly corresponds to Range B **service** voltage specifically. But the paper's unqualified
phrase "Range B extends to roughly 0.917 pu" is ambiguous: Range B's full/utilization-voltage extent
(the figure more directly comparable to "how far Range B reaches," per the PG&E prose and the same
draft's own Note b) is 0.867 pu, not 0.917 pu. Neither number has been confirmed against the actual
paid, approved ANSI C84.1-2020 standard body text -- only against NEMA's free front-matter (metadata
only, no numbers) plus one utility document and one unapproved draft (numbers, not an official
approved source). **This citation is not fully primary-source-verified; flag for reconciliation before
the number is defended as ANSI C84.1-2020's literal Range B figure, and consider whether "service" vs
"utilization" needs to be specified in the paper's own wording.**

### 7.4 angelopoulos2024 (medRxiv) -- does the load-bearing three-way passage exist?

No `notes/lit/notes/*angelopoulos*.md` note and no source PDF existed anywhere in the repo before this
check -- this citation had never been read past the search-level verification already on record in
section 1, row A3 ("VERIFIED [SEARCH]"). Fetched 2026-07-28:

- `https://api.semanticscholar.org/graph/v1/paper/DOI:10.1101/2024.02.09.24302543` -- confirms the
  paper is real: title "Conformal Triage for Medical Imaging AI Deployment," venue medRxiv, year 2024,
  DOI 10.1101/2024.02.09.24302543, 10 authors (Angelopoulos, Pomerantz, Do, Bates, Bridge, Elton, Lev,
  González, Jordan, Malik).
- `https://www.medrxiv.org/content/medrxiv/early/2024/02/11/2024.02.09.24302543.full.pdf` -- full text
  (11 pages), retrieved successfully via direct `curl` after both `WebFetch` and a plain `curl` to the
  `.../content/10.1101/....full.pdf` canonical URL were blocked with HTTP 403.

The paper's own Introduction states (verbatim, extracted via `pypdf`):

> "we split patients into a low-risk group with a high negative predictive value, a high-risk group
> with a high positive predictive value, and an uncertain group, building on a previous approach
> developed at the Massachusetts General Hospital wherein neuroradiologists decide these groupings
> manually [3, 18]. In our new approach, these groupings are decided by a black-box machine learning
> algorithm..."

and in the Formal Goal subsection:

> "Patients classified as high risk will be positive at the rate of the chosen PPV target, and
> similarly, those classified as low risk are guaranteed to be negative with high probability. In
> exchange for these guarantees, the algorithm is allowed to abstain on the most uncertain cases; the
> number of abstentions is determined by how stringent the PPV/NPV thresholds are."

**This confirms the citation is load-bearing as used.** The paper's own vocabulary is "low-risk /
high-risk / uncertain (abstain)," not literally "release / flag / defer" -- paper_current.tex line 173
paraphrases these into "release, flag, and defer," which is a fair paraphrase of the same three-way
structure (low-risk≈release, high-risk≈flag, uncertain/abstain≈defer), not a fabricated claim. Row A3
in section 1 should be upgraded from "VERIFIED [SEARCH]" to VERIFIED [FETCHED], full text read
2026-07-28, with the quotes above as the supporting passage.


---

## 8. Bibliography provenance entries (2026-08-21)

Six bibitems in `report/paper_current_STS.tex` resolved correctly against publishers but had **no
provenance record in this file**, or a record carrying no verification date. That is the only defect
they had: every printed field matches the resolved record and every claim they are cited for is one
the source makes. These entries close that gap. Nothing here changes a bibitem.

**Two independent sources per entry, per the standard set by the `cortes2016` entry in section 2.**
That standard earned its keep this session: Crossref's DOI record for `cortes2016` reports LNCS
**9355** (ALT 2015's volume) for an ALT **2016** chapter, contradicting its own ISBN in the same
record. A single-source Crossref confirmation would have "corrected" a correct bibitem into an
error. Every entry below therefore names both sources and flags where they disagree.

**Scope note.** Seven other bibitems fail for reasons this section does NOT fix, and they are
deliberately excluded: `nerc` and `case118` (primary source unfetchable — HTTP 403 and a TLS chain
failure), `barber2021` and `tibshirani2019` (claim-precision defects, section 8.7), `ansi2020`
(cited for a number its verified portion does not state, section 7.3), and `romano2019` and
`vovk2005` (section 8.8 — residual bibliographic gaps beyond provenance).

### 8.1 bates2021 -- Bates et al., J. ACM

Fetched 2026-08-21, two sources.

- Crossref (`api.crossref.org/works/10.1145/3478535`): title "Distribution-free, Risk-controlling
  Prediction Sets"; authors Stephen Bates, Anastasios Angelopoulos, Lihua Lei, Jitendra Malik,
  Michael Jordan; *Journal of the ACM*; vol. 68, issue 6; pages 1-34; 2021; DOI 10.1145/3478535.
  **Crossref carries no article-number field.**
- Semantic Scholar (`api.semanticscholar.org/graph/v1/paper/DOI:10.1145/3478535`): same title, same
  five authors in the same order, venue *Journal of the ACM*, year 2021, journal volume 68,
  **pages `43:1-43:34`**, DOI 10.1145/3478535, arXiv 2101.02703.

**The bibitem's "art. 43" is CONFIRMED** by the S2 pages field `43:1-43:34` -- article 43, 34 pages.
This was the one open question on this entry and it is now closed. Crossref's flat "1-34" is the
within-article pagination and is not in conflict.

Cited at `report/paper_current_STS.tex:84` and `:258`. At `:258` the fit is exact -- the paper IS
distribution-free risk control, which is what the sentence calls it. At `:84` the fit is LOOSE: the
sentence is about a surrogate emitting a point estimate with no attached uncertainty, and this paper
is about constructing risk-controlling sets, not about surrogate failure modes. The citation is not
wrong at `:84`, but it is doing weaker work there than at `:258`. Recorded, not repaired.

### 8.2 ejebe1979 -- Ejebe & Wollenberg, IEEE TPAS

Fetched 2026-08-21, two sources. Upgrades the section 3 line 99 record from VERIFIED [SEARCH]
(which carried no date) to VERIFIED [FETCHED].

- Crossref: title "Automatic Contingency Selection"; first author Ejebe, G.; *IEEE Transactions on
  Power Apparatus and Systems*; vol. PAS-98, issue 1; pages 97-109; 1979; DOI
  10.1109/tpas.1979.319518.
- Semantic Scholar (`DOI:10.1109/tpas.1979.319518`): same title; authors G. Ejebe, B. Wollenberg;
  venue *IEEE Transactions on Power Apparatus and Systems*; volume PAS-98; pages 97-109; year 1979.

Every printed field of the bibitem matches. S2 does not expose the issue number; Crossref gives
issue 1. Cited at `:94` for the claim that classical fast screens rank contingencies without a full
solver -- which is exactly the performance-index selection method this paper introduces.

### 8.3 pandapower -- Thurner et al., IEEE TPWRS

Fetched 2026-08-21, two sources. **This file previously had no record of the CITED WORK at all.**
The pre-existing "pandapower" hits at lines 109-110 concern the tool's feasibility for computing
FVSI-type indices; "Thurner" appeared nowhere. The automated gate matched the software name and
reported a record that did not exist.

- Crossref: title "Pandapower--An Open-Source Python Tool for Convenient Modeling, Analysis, and
  Optimization of Electric Power Systems"; first author Thurner, Leon; *IEEE Transactions on Power
  Systems*; vol. 33, issue 6; pages 6510-6521; **November 2018**; DOI 10.1109/tpwrs.2018.2829021.
- Semantic Scholar (`DOI:10.1109/tpwrs.2018.2829021`): same title; authors L. Thurner, A. Scheidler,
  F. Schäfer, J. Menke, Julian Dollichon, F. Meier, Steffen Meinecke, M. Braun; venue *IEEE
  Transactions on Power Systems*; volume 33; pages 6510-6521; **year 2017**; arXiv 1709.06743.

**Year discrepancy, resolved in the bibitem's favour.** S2's 2017 is the arXiv posting year
(1709.06743); Crossref's November 2018 is the IEEE issue. The bibitem says "Nov. 2018" and is
correct. Same preprint-year-versus-issue-year pattern as `barber2021` and `lei2018` -- a bare year
from a single index is not sufficient evidence to change a bibitem.

Cited at `:96` for the solver; `CLAUDE.md` §6 pins the version actually used (pandapower 3.5.4),
which is not the version this 2018 paper describes. The citation is for the tool's canonical
reference, not for the pinned build.

### 8.4 sklearn -- Pedregosa et al., JMLR

Fetched 2026-08-21, two sources, one of them the publisher.

- JMLR publisher page (`jmlr.org/papers/v12/pedregosa11a.html`): title "Scikit-learn: Machine
  Learning in Python"; 16 authors beginning Fabian Pedregosa, Gaël Varoquaux, Alexandre Gramfort,
  Vincent Michel, Bertrand Thirion; citation line printed as *Journal of Machine Learning Research*,
  volume 12, pages 2825-2830, 2011.
- OpenAlex (`doi:10.5555/1953048.2078195`): display_name "Scikit-learn: Machine Learning in Python";
  first author Pedregosa Fabian; publication_year 2011; source *Journal of Machine Learning
  Research*. **OpenAlex's biblio volume/first_page/last_page are null** -- the volume and page range
  rest on the JMLR page alone, which is the publisher of record and is authoritative for both.

Every printed field of the bibitem matches. Cited at `:108` for the two estimators (ridge,
histogram-based gradient boosting); the claim is trivially supported.

### 8.5 lei2018 -- Lei et al., JASA

Fetched 2026-08-21, two sources. **Partially discharges the section 5 warning** at lines 151-153,
which named this paper among conformal foundations that were NOT re-verified and "should be
confirmed before they appear in any writeup." It appears in the writeup at `:112`, twice.

- Crossref: title "Distribution-Free Predictive Inference for Regression"; first author Lei, Jing;
  *Journal of the American Statistical Association*; vol. 113, issue 523; pages 1094-1111; 2018;
  DOI 10.1080/01621459.2017.1307116.
- Semantic Scholar (`DOI:10.1080/01621459.2017.1307116`): same title; authors Jing Lei, M. G'Sell,
  A. Rinaldo, R. Tibshirani, L. Wasserman; venue *Journal of the American Statistical Association*;
  volume 113; pages 1094-1111; **year 2016**; arXiv 1604.04173.

**Year discrepancy, resolved in the bibitem's favour.** S2's 2016 is the arXiv posting year; the
JASA issue 113(523) is 2018. The bibitem's 2018 is correct.

**WHAT THIS ENTRY DOES NOT ESTABLISH.** Bibliographic identity is confirmed; the section 5 warning
asked for more than that. `:112` attributes a specific construction -- "the finite-sample rank
approach proposed by Lei et al." -- to this paper. **The paper body has not been re-read in this or
any recorded pass**, so that specific attribution rests on the author's memory of it, not on a
verified passage. Confirming a citation exists is not confirming it says what it is cited for. A
full-text read, in the manner of section 7.4, is still owed before `:112` is defended.

### 8.6 chow1970 -- Chow, IEEE TIT

Fetched 2026-08-21, two sources.

- Crossref: title "On optimum recognition error and reject tradeoff"; first author Chow, C.; *IEEE
  Transactions on Information Theory*; vol. 16, issue 1; pages 41-46; 1970; DOI
  10.1109/tit.1970.1054406.
- Semantic Scholar (`DOI:10.1109/tit.1970.1054406`): same title; author C. Chow; venue *IEEE
  Transactions on Information Theory*; volume 16; pages 41-46; year 1970; dblp
  `journals/tit/Chow70`.

Every printed field of the bibitem matches. Cited at `:256` as the origin of the reject-option
lineage, which is what this paper is.

### 8.7 Two bibitems NOT fixed here: claim-precision defects

Both resolve cleanly and both would pass a bibliographic check. Neither is a provenance problem, so
neither belongs in section 8; recorded here so they are not mistaken for closed.

- **barber2021**, cited at `:258`. Crossref confirms Foygel Barber / Candès / Ramdas / Tibshirani,
  *Information and Inference* 10(2):455-482, DOI 10.1093/imaiai/iaaa017, **published-print
  2021-06-15** (published-online 2020-08-25 -- the bibitem's 2021 is correct). The manuscript cites
  it for "if one demands perfect correctness with a limited amount of calibration data, then the
  prediction intervals become extremely wide." The theorem is about distribution-free **conditional**
  coverage forcing infinite expected length. "Perfect correctness" is not the quantity the
  impossibility result concerns. Right paper, wrong name for the thing it proves.
- **tibshirani2019**, cited at `:262` for "conformal prediction requires the data to be exchangeable
  with the calibration set." The paper's contribution is the **relaxation** -- weighted conformal
  prediction that stays valid under covariate shift. Citing the workaround as authority for the
  restriction is defensible on the paper's premise but inverted relative to its result.

### 8.8 Two bibitems NOT fixed here: residual bibliographic gaps

Excluded from section 8 because each has an unresolved bibliographic question, not merely a missing
record. Both are also named in the section 5 warning at lines 151-153.

- **romano2019.** The NeurIPS proceedings page (`papers.nips.cc/paper/8613-conformalized-quantile-
  regression`, fetched 2026-08-21) confirms title "Conformalized Quantile Regression" and authors
  Yaniv Romano, Evan Patterson, Emmanuel Candes, in *Advances in Neural Information Processing
  Systems 32 (NeurIPS 2019)*. **The page shows no page numbers.** The bibitem's "pp. 3538--3548" is
  unconfirmed by any primary source. Needs one source that prints the volume pagination.
- **vovk2005.** Crossref's top hit for this title is the **2022 second edition** (Springer
  International Publishing, DOI 10.1007/978-3-031-06649-8). OpenAlex confirms a distinct **2005
  first edition** exists (DOI 10.1007/b106715, Springer). The bibitem's "New York, NY, USA: Springer,
  2005" matches the first edition, but carries no DOI or edition marker, so a reader checking a
  reference against the 2022 edition will not find it. Needs an edition marker before it is closed.

## 9. Candidate citations -- verified, NOT inserted (2026-09-15)

Ten candidates proposed for `report/paper_current_STS.tex`. Research only: no bibitem added, no `\cite`
inserted. Fetched 2026-09-15 by a research subagent; metadata transcribed from the fetched source, not
from memory or another paper's reference list. DBLP, the ANSI webstore and the NEMA product page
refused automated access; where that left only one source, the entry says so (section 8 asks for two).

### 9.1 chow1970 (already a bibitem; relocation candidate only)
- Crossref `/works/10.1109/tit.1970.1054406`: C. Chow, "On optimum recognition error and reject
  tradeoff," *IEEE Trans. Inf. Theory* 16(1):41-46, Jan. 1970. Venue status: RESOLVED (journal).
- Proposal gave "C.K. Chow"; Crossref author field is "C. Chow" only. Bibitem already matches Crossref
  (section 8.6). Sources: 1 this pass (+2 in section 8.6).

### 9.2 tsybakov2004
- Crossref + Project Euclid (`aos/1079120131`): A. B. Tsybakov, "Optimal aggregation of classifiers in
  statistical learning," *Ann. Statist.* 32(1):135-166, Feb. 2004, DOI 10.1214/aos/1079120131.
  Venue status: RESOLVED. All proposed fields match. Sources: 2.

### 9.3 mammen1999
- Crossref + Project Euclid (`aos/1017939240`): E. Mammen and A. B. Tsybakov, "Smooth discrimination
  analysis," *Ann. Statist.* 27(6):1808-1829, Dec. 1999, DOI 10.1214/aos/1017939240. Venue status:
  RESOLVED. Proposal gave no title. Sources: 2.
- Distinct item, same title and authors: *Ann. Statist.* 32(5):2340-2341, Oct. 2004, DOI
  10.1214/009053604000000869 (2 pp.; item type not labeled on the fetched page). Do not confuse.

### 9.4 elyaniv2010
- jmlr.org `papers/v11/el-yaniv10a.html`: R. El-Yaniv and Y. Wiener, "On the Foundations of Noise-free
  Selective Classification," *JMLR* 11(53):1605-1641, 2010. No DOI. Venue status: RESOLVED. Proposal
  gave no title. Sources: 1 (DBLP blocked).

### 9.5 geifman2017
- papers.nips.cc abstract page + official BibTeX: Y. Geifman and R. El-Yaniv, "Selective Classification
  for Deep Neural Networks," *Advances in Neural Information Processing Systems* 30, 2017. Pages: NOT
  FOUND (BibTeX `pages` empty). No DOI. Venue status: RESOLVED (proceedings page reads "NIPS 2017").
  Sources: 2 (same host).

### 9.6 vovk2003mondrian
- Royal Holloway research portal (type "Working paper", March 2003) + report PDF `alrw.net/old/04.pdf`
  (title page: "Working Paper #4, March 28, 2003"): V. Vovk, D. Lindsay, I. Nouretdinov, A. Gammerman,
  "Mondrian Confidence Machine," On-line Compression Modelling Project, Working Paper #4. No DOI.
- **DISCREPANCY: proposal year 2005; source year 2003.** Venue status: RESOLVED AS UNREFEREED WORKING
  PAPER; no journal or conference version found (Crossref: none). Sources: 2.

### 9.7 angelopoulos2023gentle
- Crossref: A. N. Angelopoulos and S. Bates, "Conformal Prediction: A Gentle Introduction," *Found.
  Trends Mach. Learn.* 16(4):494-591, 2023, DOI 10.1561/2200000101. Venue status: RESOLVED. All
  proposed fields match. A monograph edition also exists (DOI 10.1561/9781638281597); cite the journal
  DOI. Sources: 1.

### 9.8 tibshirani2019
- papers.nips.cc abstract page + official BibTeX: R. J. Tibshirani, R. Foygel Barber, E. Candes, A.
  Ramdas, "Conformal Prediction Under Covariate Shift," *Advances in Neural Information Processing
  Systems* 32, 2019. Pages: NOT FOUND. No DOI. Venue status: RESOLVED. Sources: 2 (same host).
- Carried-over flag, section 8.7: its result is the covariate-shift **relaxation** (weighted conformal),
  not the restriction. Any use must cite it for the weighting method.

### 9.9 nakiganda2023
- arXiv abs v1, v2, v3 + export API, DOI 10.48550/arXiv.2310.04213.
  - v1 (2023-10-06), v2 (2023-11-10): "Topology-Aware Neural Networks for Fast Contingency Analysis of
    Power Systems"; authors A. M. Nakiganda, C. Cheylan, S. Chatzivasileiadis.
  - v3 (2025-03-04): "Graph Neural Networks for Fast Contingency Analysis of Power Systems"; authors
    A. M. Nakiganda, S. Chatzivasileiadis.
- **DISCREPANCY: proposed title + two-author list matches no single version.** Venue status: RESOLVED
  AS PREPRINT; no journal-ref on arXiv. An IEEE Xplore item "On Fast N-1 Contingency Analysis: A Graph
  Neural Network Approach" (document 10922618) surfaced in search; NOT opened, authorship NOT checked.
  Sources: 2.

### 9.10 nerc (already a bibitem) -- closes the section 8 "unfetchable" status
- nerc.com `globalassets/standards/reliability-standards/tpl/tpl-001-5.1.pdf` + standard page: NERC,
  "TPL-001-5.1 -- Transmission System Planning Performance Requirements." Board adopted 2018-11-07;
  filed 2020-04-23; FERC order 2020-06-10 (Docket RD20-8-000); effective 2023-07-01; status "Mandatory
  Subject to Enforcement". Bibitem "eff. Jul. 1, 2023" matches. Sources: 2.
- R5 (verbatim): "Each Transmission Planner and Planning Coordinator shall have criteria for acceptable
  System steady state voltage limits, post-Contingency voltage deviations, and the transient voltage
  response for its System."
- Table 1 note g (verbatim): "System steady state voltages and post-Contingency voltage deviations shall
  be within acceptable limits as established by the Planning Coordinator and the Transmission Planner."
- Text search for "0.94", "0.95", "per unit": no numeric voltage limit. **Does not state 0.94 pu.**

### 9.11 ansi2020 -- supersedes nothing in section 7.3; adds nothing numeric
- NEMA free "contents and scope" PDF: ANSI C84.1-2020 (Revision of ANSI C84.1-2016), "American National
  Standard for Electric Power Systems and Equipment -- Voltage Ratings (60 Hertz)," NEMA secretariat,
  approved 2020-03-10. Matches section 7.3. Sources: 1 (webstore blocked).
- Scope 1.1 (verbatim): "This Standard establishes nominal voltage ratings and operating tolerances for
  60 Hz electric power systems above 100 volts."
- TOC only: 5.1.1 Range A--Service Voltage; 5.1.2 Range A--Utilization Voltage; 5.1.3 Range B--Service
  and Utilization Voltages; 5.1.4 Outside Range B. Numeric table: NOT FOUND in the free excerpt.
- Unconfirmed: an "ANSI/NEMA C84.1-2020 (R2025)" reaffirmation listing (page not opened).
- **0.94 pu: NOT FOUND in any verified portion.** Section 7.3's secondary sources put Range A service at
  +/-5% and Range B service minimum at 110/120 = 0.917 pu -- neither is 0.94.

## 10. Six new bibitems: printed fields vs the verified record (2026-09-15)

The 23-entry bibliography adds six entries. Their bibliographic identity was verified in section 9
(fetched 2026-09-15); this section checks the printed bibitem fields against that record and flags
claim-precision issues found by reading the papers themselves. No claim_support record exists for any of
them yet, so `scripts/check_citations.py` still fails them (it fails all 23 for that reason).

### 10.1 angelopoulos2023 -- fields MATCH
Printed: Found. Trends Mach. Learn. 16(4):494-591, 2023. Section 9.7 record: identical. DOI
10.1561/2200000101 is not printed in the bibitem; the journal edition, not the monograph edition
(10.1561/9781638281597), is the one cited.

### 10.2 geifman2017 -- fields MATCH, pages correctly omitted
Printed: NeurIPS vol. 30, 2017, no page numbers. Section 9.5: the official NeurIPS BibTeX carries an empty
`pages` field, so omitting pages is correct, not an omission defect. The proceedings volume is styled
"NIPS 2017" on the publisher page; "NeurIPS" in the bibitem is the retrospective name.

### 10.3 tsybakov2004 -- fields MATCH
Printed: Ann. Statist. 32(1):135-166, 2004. Section 9.2: confirmed by Crossref and Project Euclid.
Local copy `notes/cited papers/Unconfirmed 946717.crdownload` is a complete PDF of the paper despite the
Chrome partial-download filename: `pdfinfo` reports 32 pages, journal pp. 135-166, ending with the
reference list. (An earlier note in this session called it partial; that was wrong.)

### 10.4 mammen1999 -- fields MATCH
Printed: Ann. Statist. 27(6):1808-1829, 1999. Section 9.3: confirmed by Crossref and Project Euclid.
Distinct 2004 item with the same title and authors (32(5):2340-2341) is NOT this entry.

### 10.5 elyaniv2010 -- fields MATCH
Printed: JMLR 11:1605-1641, 2010. Section 9.4: jmlr.org gives 11(53):1605-1641; the issue number is not
printed, which is normal for JMLR citations.

### 10.6 tibshirani2019 -- fields MATCH the proceedings, with two spelling notes
Printed: R. J. Tibshirani, R. Foygel Barber, E. J. Cand\`es, A. Ramdas; NeurIPS vol. 32, 2019; no pages.
Section 9.8: the NeurIPS page spells the third author "E. Candes" (no accent) and stores the second as
"Foygel Barber"; the accent in the bibitem is a typographic normalization, not a field error. Pages are
absent from the official BibTeX, so omitting them is correct.
**No local PDF.** `notes/cited papers/` has no copy of this paper; claims were checked against
arXiv:1904.06019 on 2026-09-15, which is a preprint of the same work, not the proceedings version.

### 10.7 Claim-precision finding on chow1970 (already a bibitem; author field unchanged as "C. Chow")
Read in full 2026-09-15: `notes/cited papers/On optimum recognition error and reject tradeoff.pdf`,
IEEE Trans. Inf. Theory 16(1):41-46.
- What the 1970 paper PROVES: the error-reject relation E(t) = -int t dR(t) (Eq. 13, p. 43) and
  dE/dR = -t (Eq. 20, p. 44; "The rejection threshold is the differential error-reject tradeoff").
- What it does NOT prove: the optimality of the reject rule. p. 41: "It is known [1] that the optimum
  rule is to reject the pattern if the maximum of the a posteriori probabilities is less than some
  threshold"; p. 42: "A detailed proof is given in [I]". Reference [1] is C. K. Chow, IRE Trans.
  Electronic Computers, EC-6:247-254, 1957.
- Reject rate is mass over a SUBLEVEL SET, not a band: V_R(t) = {v | m(v) < 1-t} (Eq. 12, p. 42) and
  R(t) = int_{V_R(t)} F(v) dv (Eq. 6', p. 42). The regions are nested, not shells (p. 42, III-A).
- The word "boundary" does not appear in the paper (full-text search, 0 hits).
- A thin shell appears only for the INCREMENT dR: Eqs. (15)-(16), p. 43; and the reject region is an
  interval around the Bayes boundary only in the binary equal-variance normal EXAMPLE, Eq. (26), p. 44.
- Regression, a scalar threshold on a predicted physical quantity, or a physical limit: NOT FOUND.
- Consequence: "Chow showed that an optimal classifier's reject rate is governed by the probability mass
  near the decision boundary" is OVERSTATED on both counts (attribution and geometry). Supported instead:
  a Bayes-optimal classifier rejects inputs whose maximum posterior falls below a threshold, so its reject
  rate is the mass of that low-confidence region, and the threshold equals the local slope of the
  error-reject curve.

### 10.8 angelopoulos2023 -- claim check (read 2026-09-15; local PDF is arXiv:2107.07511v6, 2022-12-08)
- Marginal coverage, Eq. (1) p. 4: "1 - alpha <= P(Y_test in C(X_test)) <= 1 - alpha + 1/(n+1)", called
  "marginal coverage ... averaged over the randomness in the calibration and test points". Theorem 1, p. 6.
  Split conformal named as "the most widely-used version ... our primary focus" (p. 6).
- "one-sided" / "two-sided": NOT FOUND anywhere in the document. Every worked regression interval is
  two-sided (Eqs. 4, 5; score s(x,y) = |y - f_hat(x)|/u(x)). The recipe admits any score, so a one-sided
  score is permitted but never instantiated. Do NOT cite this reference for the one-sided band.
- Supports the III.3 sentence about residuals -> coverage guarantee. Guarantee is MARGINAL, not conditional.

### 10.9 geifman2017 -- claim check (read 2026-09-15)
- Coverage (Sec. 2, p. 2): "phi(f,g) = E_P[g(x)], is the probability mass of the non-rejected region".
  Selective risk, Eq. (1): "R(f,g) = E_P[l(f(x),y) g(x)] / phi(f,g)" -- risk CONDITIONED on the accepted
  region. Risk-coverage curve defined p. 2 as "risk as a function of coverage [5]", credited to
  El-Yaniv & Wiener 2010; the term is NOT originated here.
- Contribution is selecting one threshold with a high-probability risk guarantee (Eq. 2, Thm 3.2,
  Algorithm 1 SGR), not sweeping a curve. Confidence scores: softmax response and MC-dropout (Sec. 4).
- Consequence: "sweeping abstention rate against error rate produces a risk-coverage curve" has the axes
  reflected (convention is selective risk vs coverage) and uses raw error rate where the convention is
  risk conditioned on the accepted region.
- Terminology collision to avoid in the manuscript: "coverage" here means accepted FRACTION; "coverage" in
  the conformal sections means the 1-alpha band target. They are different quantities.

### 10.10 elyaniv2010 -- claim check (read 2026-09-15)
- Abstract p. 1605: "We term this trade-off the risk-coverage (RC) trade-off" -- the term originates here.
- Realizable only: Sec. 1 p. 1606, "we focus in this work on noiseless settings whereby a perfect
  hypothesis for the problem at hand exists (the so called 'realizable case')"; Sec. 2 p. 1606 assumes
  "Pr_P(Y = f*(X)|X) = 1". The authors themselves warn against comparing their bounds with agnostic-setting
  bounds (Sec. 10).
- Fair as a foundations/lineage citation for abstention (Chow -> El-Yaniv & Wiener -> Cortes et al.).
  NOT a calibration method, and none of its bounds transfer to a noisy regression screener.

### 10.11 tibshirani2019 -- claim check (read 2026-09-15 from arXiv:1904.06019v3, 2020-07-06; no local PDF)
- Requires the likelihood ratio: abstract, "the likelihood ratio between these two distributions is
  known -- or, in practice, can be estimated accurately with access to a large set of unlabeled data".
  Weights Eq. (7) use w(X_i) = dPtilde_X(X_i)/dP_X(X_i); weighted split conformal is Eq. (10); Remark 3
  allows w known only up to proportionality.
- Covariate shift proper: model (6) states "the conditional distribution of Y|X is assumed to be the same
  for both the training and test data".
- Corollary 1 assumes "Ptilde_X is absolutely continuous with respect to P_X". The paper says nothing about
  test support outside supp(P_X): NOT FOUND. (That absolute-continuity hypothesis is the anchor for an
  argument that no ratio exists when the test event space is not contained in the training one; the
  power-systems half of such a sentence is the author's own argument, not the paper's.)

### 10.12 tsybakov2004 / mammen1999 -- claim check (both read in full 2026-09-15)
- Tsybakov 2004, Proposition 1, Eq. (5), p. 138: "P(|eta(X) - 1/2| <= t) <= C_eta t^alpha" for
  0 < t <= t*, with margin parameter kappa = (1+alpha)/alpha (Eq. 6); (A1) p. 138 is the set-geometry
  form d(G,G*) >= c_0 d_Delta^kappa(G,G*). "kappa is called the margin parameter" (p. 138). The band is on
  eta(x) = P(Y=1|X=x) around 1/2, measured by P_X -- genuine probability mass of X. Used for fast excess-
  risk rates: Thm 1 p. 140, O(n^{-kappa/(2kappa+rho-1)}); without (A1) only O(n^{-1/2}) (Prop. 2, p. 141).
- Mammen & Tsybakov 1999, Eq. (4), p. 1811: "Q{x in K : |f(x) - g(x)| <= eta} <= c_2 eta^alpha". The word
  "margin" appears ZERO times in the paper; Q is a sigma-finite dominating measure, not P_X; the band is on
  the density difference, with a stated x-space reading near the boundary (p. 1811). The |2eta-1| form is
  NOT in this paper.
- Primary citation for the P(|2eta-1| <= t) <= C t^alpha form: Tsybakov 2004, Prop. 1 Eq. (5). Mammen &
  Tsybakov 1999 is the correct citation for the idea (first fast rates from boundary behavior; Tsybakov
  credits it that way on p. 137), not for that formula.
- Reject/abstention: NOT FOUND in either. Regression with a threshold on a continuous outcome: NOT FOUND in
  either; Y is binary throughout.
