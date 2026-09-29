# finalist-paper-analysis.md

Comparative analysis of six papers in `notes/reference/finalist-papers/` against
`report/paper_current_STS.tex` and `notes/writing-guide.md`. **Written 2026-08-27.**
**Git HEAD at analysis:** `ab970c19bd9210a2a2c00b1ff21fe9e8d8488051`.

**This file contains no manuscript prose.** The header prohibition in `notes/writing-guide.md`
applies here. Every entry is a fact, a citation, or a specification.

**No number in any existing file was changed by this analysis.** This file is the only one
written apart from the prompt log.

---

## 0. PROVENANCE, LIMITATIONS, AND WHAT THIS CANNOT TELL YOU

### 0.1 The finalist-paper provenance is OWNER-ASSERTED

**Stated once, and it governs every claim in Part 1.** The owner states that each PDF in
`notes/reference/finalist-papers/` is the work submitted by an STS 2026 finalist. **I did not
verify that.** I verified only what each PDF says about itself — title, authors, venue, dates,
content. I did not confirm that any author was an STS finalist, that any placed where the
filename claims, or that the PDF is the document submitted to Regeneron STS rather than a
related version. **Filenames assert placements (4th, 9th, 10th); nothing inside the PDFs
corroborates those placements.** Treat every "finalist" statement below as inheriting that
assertion.

**The directory README disagrees with the directory.** `README.md` describes **two** papers
(Xie, Nguyen); the directory holds **six**. The README's framing ("published papers by STS 2026
finalists") is also not accurate for all six: **three of the six are unrefereed preprints**
(Arni, Du, Chen — see 1.2). Recorded as a discrepancy, not repaired.

### 0.2 The limitation that bounds this entire analysis

**I have no access to rejected applications.** Everything in Part 1 describes six papers that
were selected. Nothing here can identify what separates a finalist from a non-finalist, because
the comparison set — the roughly 2,000 entrants who were not named finalists, and the 260
scholars who were not — is absent. **A feature shared by all six papers is not thereby a cause
of selection.** It may be a property of competent work in these fields generally, of the papers
their authors chose to submit, or of nothing at all. Where I state a shared feature I mark it
SHARED. Where a paper actively demonstrates something, I mark it DEMONSTRATED. **The inference
from SHARED to "this is why they won" is unavailable and I do not make it.**

Sample size six, non-random, self-selected by the owner. No statistical claim is drawn from it.

### 0.3 Read coverage, per paper

Reported because it bounds the figure and table counts below.

| paper | pages | pages I read | coverage |
|---|---|---|---|
| Nabat | 8 | 1-8 | COMPLETE |
| Nguyen | 8 | 1-8 | COMPLETE |
| Xie | 12 | 1-12 | COMPLETE |
| Arni | 18 | 1-18 | COMPLETE |
| Du | 21 | 1-11 | **PARTIAL (52%)** |
| Chen | 24 | 1-6, 22-24 | **PARTIAL (38%)** |

Page counts derived by counting `/Type /Page` objects in the raw PDF bytes with
`.venv/bin/python`; `pypdf` is **not installed** in `.venv`, so no library-based count was
available. The method agrees with the README's independently stated counts for the two papers
the README covers (Xie 12, Nguyen 8), which is the only cross-check available.

**Abstract word counts for the six are ESTIMATED** from the rendered page, not machine-counted —
the PDFs were read as images. They are labelled approximate throughout. My own abstract count
(161) IS machine-counted from `report/paper_current_STS.tex`.

---

## 1. THE OFFICIAL CRITERIA, AS FOUND

### 1.1 The Scholar screen — CONFIRMED VERBATIM

Fetched **2026-08-27**, `https://www.societyforscience.org/regeneron-sts/judging-and-awards/`:

> "Eligible Regeneron STS entrants are then evaluated and scored by three Ph.D. level scientists.
> Each qualified project is scored based upon the online application questions, the Research
> Report, and the overall scientific potential of the student."

> "The top 300 entries are named scholars and are then reviewed again by a panel of 15
> distinguished scientists from a variety of disciplines."

> "Each year in late January, from among the 300 scholars, 40 finalists are announced."

**Matches the prompt's quoted text.** No discrepancy on the Scholar screen.

### 1.2 The selection basis — DISCREPANCY, and it matters

The prompt quotes a selection basis beginning "outstanding research, leadership skills, community
involvement, commitment to academics, creativity in asking scientific questions and exceptional
promise as STEM leaders…". **I could not locate that string on societyforscience.org.** What I
found instead, fetched **2026-08-27**,
`https://www.societyforscience.org/regeneron-sts/frequently-asked-questions/`:

> "exceptional research skills, a commitment to academics and their extracurricular pursuits,
> innovative thinking, promise as a scientist, and evidence of leadership in their communities."

**Per the instruction, I use what I found and flag the difference.** The two lists overlap
substantially. The prompt's version is plausibly from a press release or an older cycle; I did
not find it, so I record it as **NOT LOCATED at the URLs I fetched** rather than as wrong.

**Two statements on the same page are load-bearing and are NOT in the prompt's version:**

> "with greatest weight given to the Research Report"

> "while the research is very important, it is not the only factor when naming scholars and
> finalists."

The first raises the stakes on the artifact this analysis is about. The second bounds how much
any paper-level change can buy.

### 1.3 The Research Report Guidelines — FOUND, and this is the most consequential section here

**`https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Research-Report-Guidelines.pdf`,
fetched 2026-08-27. Two pages. This is the STS 2027 cycle — the one the owner is entering.**

The prompt asked for formatting rules, page limits, and any released rubric. **There is no
rubric.** There are hard rules. Verbatim:

**Page limit and structure (rule 4):**
> "The paper should be 20 pages or less. There is no page minimum. Pages of content beyond page
> 20 (excluding the pages mentioned below) will not be read or considered."

> "Include a title page as the first page, abstract as the second page and a bibliography at the
> end of the Research Report. The title page, abstract and bibliography do not count toward the
> 20-page limit."

> "Appendices count toward the 20-page limit."

> "Within the 20-page limit, we recommend including a short introduction describing the background
> and purpose of the work, an experimental design section including methods and results, and
> concluding discussion of results and implications. We do not require a specific format/order,
> and you may format in the standards of your scientific discipline."

**Format (rule 5):**
> "The font size should appear on the page at least as large as Times New Roman 11pt font."
> "Use 1.5 line spacing and 1" margins on all sides. Do not use multiple columns."
> "Number the pages of your research report in the bottom right corner, starting after the abstract."
> "Students may not provide links within the Research Report or application of any sort, except
> within bibliographic references or where specifically requested in the application."
> "PDF files that are 4MB or smaller are the only format accepted in the online system."

**Figure citation (rule 2) — disqualification-level:**
> "Every single image, graph, table, chart, etc. that appears in the Research Report must be cited
> per the Citation Guide in Appendix 3 on page 33. This includes images created by the Student
> Researcher. Failure to cite an image could result in disqualification."

**Generative AI (rule 1):**
> "The Student Researcher is required to write the paper without the use of generative AI (ChatGPT
> or other programs)."

And on references, rule 4f:
> "Entrants should generate their reference lists without the use of AI, which is known to
> hallucinate and create fake or altered references. Discovery of a fake reference will result in
> disqualification."

**Published work and authorship (rule 6):**
> "It is not recommended that students submit published research papers if they are not the sole
> or first author, or if the formatting is different from Regeneron STS requirements. Publishing
> research of the lab makes it difficult to assess student contribution to the work. In the case
> of published group research, acknowledge the published paper in your application, and submit
> your own version of the research to Regeneron STS that highlights your actual contributions to
> the larger research project."

**Voice (rule 7):**
> "If it is widely accepted to write scientific journal articles in your specific subject area
> using first person plural "we" then it is acceptable for a student to use the first person "I"
> in place of "we" in their Regeneron STS research report. This will help to clarify what was done
> independently vs. with support."

**Literature review (rule 8):**
> "Do not include library research or a history of literature beyond the short introduction,
> detailed explanations of experiments and procedures of other researchers that preceded the
> project, lengthy autobiographical information or personal history."

**Individual contribution:**
> "the research report must accurately reflect the work of only the student researcher. While
> students may seek review of their content and presentation of the research report, both the
> content and writing should be the work of the applicant. Submitting a paper co-authored by many
> individuals confuses the evaluators regarding the contribution of the student. Adults reviewing
> research reports should suggest areas for improvement, but not provide the student with
> replacement text or rewrite any portion of the entry."

> "full disclosure of any research or person that has influenced the applicant's work is required."

**Eligibility:**
> "Research proposals, investigations not yet completed, literature reviews and essays are not
> eligible for this competition."

### 1.4 What I could not find — NO SOURCE

- **A rubric, scoring sheet, or weighted criteria list.** NO SOURCE. Searched
  societyforscience.org; the judging page states who scores and on what basis, not how. **I did
  not infer one**, per instruction.
- **The prompt's exact "outstanding research, leadership skills…" selection-basis string.**
  NOT LOCATED at the URLs fetched (see 1.2).
- **Any word limit** on the Research Report. NO SOURCE — the constraint is pages, not words.
- **Any guidance on how many figures or tables are expected.** NO SOURCE.

---

## 2. PART 1 — WHAT THE SIX PAPERS ACTUALLY DO

### 2.1 Per paper

Every claim cites the file and page.

#### A. Nabat — "Learning broken symmetries with approximate invariance"

| dimension | finding |
|---|---|
| Pages | 8 (paginated 072002-1 to 072002-8) |
| Authors / affiliations | **5.** Seth Nabat (Taft Charter High School STEAM Magnet, Woodland Hills CA) **first author**; Aishik Ghosh (UC Irvine + LBNL); Edmund Witkowski (Independent Researcher); Gregor Kasieczka (Universität Hamburg); Daniel Whiteson (UC Irvine) (p.1) |
| Venue, verified | **Phys. Rev. D 111, 072002 (2025). VERIFIED from the PDF's own header** — "Received 7 January 2025; accepted 13 March 2025; published 3 April 2025", DOI 10.1103/PhysRevD.111.072002 (p.1). Refereed, published |
| Abstract words | ~150 (ESTIMATED) |
| Contribution sentence | **Abstract, sentence 5** (p.1): "We propose a learning model which balances the generality and asymptotic performance of unconstrained networks with the rapid learning of constrained networks." |
| Section structure | I. Introduction; II. Dataset; III. Approach; IV. Network Training and Performance; V. Conclusions; Acknowledgments; Data Availability; Appendix A Hybrid Subnets; Appendix B Model Details; Appendix C Alternate Hybrid Architectures; References |
| Figures / tables | **8 figures, 0 tables** |
| Headline in abstract | **QUALITATIVE, not a magnitude** (p.1): "our model learns as rapidly as symmetry constrained networks but escapes its performance limitations" |
| Baseline | **Self-defined, internal**: a general PFN and an invariant network, matched to "a sum total of 1152 hidden layer neurons across all subnets" for fairness (p.4). No external SOTA comparison |
| Dispersion | **YES.** "Colored bands indicate the degree of statistical variation and correspond to one standard deviation across five ensembles" (Figs. 4, 6, 7, 8 captions, pp.5-7). Also "the difference in AUC between the general and enlarged hybrid models was 0.000 ± 0.002" (p.6) |
| Negative result / limitations | **YES, both, and in the body.** p.5: "Note also that the general network slightly outperforms the hybrid network for the full datasets and after long training times." Appendix A (p.6): "For a large dataset, the general PFN outperforms the hybrid model on final AUC." Also reports an outlier run: "in one out of the five trials, the learned weight MLP converged on a very different shaped function" (p.4). No dedicated Limitations section |
| Sample size | 20,000 events (20% subset) and the full sample; 100 epochs; **five ensembles per configuration** (pp.4-5) |
| Evaluation weakness | **Self-acknowledged and severe by design.** "a simplified toy example" (abstract, p.1). Simulated data only. Detector smearing set to 10% of true p_T, which the paper calls "somewhat larger than expected at current LHC experiments, but helpful to exaggerate the effect for demonstration purposes" (p.3) — the effect size is deliberately inflated. Single dataset, single task |

#### B. Nguyen — "Metallicity Regulates Planet Formation across All Masses"

| dimension | finding |
|---|---|
| Pages | 8 |
| Authors / affiliations | **2.** Max Nguyen (Leland High School, San Jose CA) **first author**; Vardan Adibekyan (Instituto de Astrofísica e Ciências do Espaço, Univ. Porto) (p.1) |
| Venue, verified | **The Astronomical Journal 170:334, 2025 December. VERIFIED from the PDF header** — "Received 2025 August 26; revised 2025 October 9; accepted 2025 October 11; published 2025 November 17", DOI 10.3847/1538-3881/ae1466 (p.1). Refereed, published |
| Abstract words | ~180 (ESTIMATED) |
| Contribution sentence | **Abstract** (p.1): "We show that even the most massive planets form preferentially in metal-rich environments." |
| Section structure | Abstract; 1 Introduction; 2 Sample Selection; 3 Summed Mass Fraction of Heavy Elements–Z (3.1-3.4); 4 Robustness Checks; 5 [Fe/H] as a Proxy for Metallicity; 6 Discussion and Conclusion; Acknowledgments; **Author Contributions**; ORCID iDs; References |
| Figures / tables | **5 figures, 4 tables** |
| Headline in abstract | **QUALITATIVE DIRECTION, not a magnitude.** No numeral appears in the abstract's result sentences |
| Baseline | **External and independent**: two separately-constructed control samples of non-host stars — 3,673 stars (Hypatia Catalog) and 394 stars (HARPS) — with the paper noting they "naturally differ in their selection functions and completeness" and using agreement across both as the robustness argument (§3.2, p.3) |
| Dispersion | **YES, throughout.** Tables 2, 3, 4 report mean ± standard error of the mean plus KS and AD p-values (pp.4-7). Figure 2 carries explicit error bars (p.3) |
| Negative result / limitations | **YES, extensively, and integrated rather than quarantined.** §3.3: multiplicity difference "is not statistically significant… both of which exceed the commonly adopted significance threshold of 0.05" (p.4). §3.4: "None of these subsample trends is statistically significant, as all p-values lie well above the 0.05 threshold" (p.5). §4 Robustness Checks is a whole section of sensitivity tests (p.6). §6: "they do not rule out the possibility that GI may operate under specific conditions" (p.7). No section is titled Limitations |
| Sample size | 5,806 confirmed exoplanets → filtered to **412 stars hosting 575 planets**; controls 3,673 (Hypatia) and 394 (HARPS) (§2, pp.2-3) |
| Evaluation weakness | Present-day stellar abundances used as a proxy for primordial disk composition — **the paper tests this itself** on 30 FGK stars and reports the difference is "about 0.57 times the uncertainty" (§2, p.3). RV-detected planets only (~97%), an acknowledged selection restriction. Catalog selection functions differ between the two controls (acknowledged, §3.2) |
| Notable | **An explicit "Author Contributions" section** (p.8): "M.N. conducted most of the research/calculations and drafted the manuscript. V.A. provided guidance at key stages of the project and revisions of the manuscript." This is the only paper of the six that states the division of labour in the paper itself |

#### C. Xie — "Distilling Empathy from Large Language Models"

| dimension | finding |
|---|---|
| Pages | 12 (paginated 343-354) |
| Authors / affiliations | **4.** Henry J. Xie (Westview High School, Portland OR) **first author**; Jinghan Zhang, Xinhao Zhang, Kunpeng Liu (Portland State University) (p.343) |
| Venue, verified | **SIGDIAL 2025. VERIFIED from the page footer** — "Proceedings of the 26th Annual Meeting of SIGDIAL, pages 343-354, Aug 25-27, 2025. ©2025 SIGDIAL" (p.343). Refereed, published |
| Abstract words | ~170 (ESTIMATED) |
| Contribution sentence | **Abstract** (p.343): "In this paper, we develop a comprehensive approach for effective empathy distillation from LLMs into SLMs." Elaborated as three bulleted components in §1 (p.344) |
| Section structure | Abstract; 1 Introduction; 2 Background (2.1-2.2); 3 Dataset Statistics and Analysis; 4 Two-Step Fine-Tuning for Distillation (4.1-4.3); 5 Empathy Distillation Methods (5.1-5.3); 6 Evaluation and Discussion; 7 Conclusions; **Limitations**; **Ethical Statement**; Acknowledgments; References; A Appendix |
| Figures / tables | **10 figures, 1 table** |
| Headline in abstract | **MAGNITUDE** (p.343): "significantly outperform the base SLM at generating empathetic responses with a win rate of 90+%" and "a 10+% improvement in win rate" |
| Baseline | **Self-defined, head-to-head**: win rate against the un-fine-tuned base SLM. One external comparator (GPT-4o) appears in Figs. 1 and 10 |
| Dispersion | **NO. None anywhere.** Table 1 (p.350) reports 84 point values with no ±, no CI, no seed count. Figures 6-10 are bar charts without error bars. No repeated runs are reported |
| Negative result / limitations | **YES — a dedicated `Limitations` section** (p.351), required by ACL-family venues: "our evaluations are subject to LLMs' biases and hallucinations… human evaluation is an essential step". Also a negative finding in the body (p.347): "SFT with the combined dataset even under-performs the datasets of some individual LLMs… including more examples into the SFT dataset does not necessarily guarantee improvement" |
| Sample size | 2,000 unique dialogue contexts (LLMs-vs-Humans dataset, Welivita & Pu 2024), five responders per context (§3, p.345) |
| Evaluation weakness | **Two, one self-acknowledged and one structural.** (i) LLM-as-judge throughout, acknowledged in Limitations (p.351). (ii) **In two of the four studies the teacher model and the judge model are both GPT-4o** — the paper states this itself (p.350: "in two combinations the teacher and judge are the same (GPT-4o)") and argues the trends match the cross-model studies. That is a circularity in the evaluation, disclosed but not removed. (iii) **No dispersion of any kind**, so no reported difference can be tested against run-to-run variation |

#### D. Arni — "Using Deep Learning for Robust Classification of Fast Radio Bursts"

| dimension | finding |
|---|---|
| Pages | 18 |
| Authors / affiliations | **3.** Rohan Arni (High Technology High School, Lincroft NJ) **first author**; Carlos Blanco (Penn State; Stockholm Univ. / Oskar Klein Centre); Anirudh Prabhu (Princeton; PCTS) (p.1) |
| Venue, verified | **NOT PUBLISHED.** The title block reads "Prepared for submission to JCAP" and the sidebar reads "arXiv:2511.02634v1 [astro-ph.HE] 4 Nov 2025" (p.1). **Unrefereed preprint, submission not confirmed** |
| Abstract words | ~150 (ESTIMATED) |
| Contribution sentence | **Abstract** (p.1): "We adopt a Supervised Variational Autoencoder (sVAE) architecture which combines the representational learning capabilities of Variational Autoencoders (VAEs) with a supervised classification task, thereby improving both classification performance and the interpretability of the latent space." |
| Section structure | Contents; 1 Introduction; 2 Methods (2.1-2.5); 3 Results (3.1-3.7); 4 Conclusions and Discussion; 5 Acknowledgements; References; 6 Appendix (6.1 Libraries and Reproducibility) |
| Figures / tables | **4 figures, 9 tables** |
| Headline in abstract | **QUALITATIVE plus two counts** (p.1): "achieves high classification accuracy for FRB repeaters" — no performance numeral — then "We also identify four non-repeating FRBs as repeater candidates, two of which have been independently flagged in previous studies." The hard number (F2 = 0.9807) appears only in §4 (p.13) |
| Baseline | **External**: prior ML classifications of the same CHIME catalog, refs [14] and [15]; §4 (p.13) claims the F2 of 0.9807 "is significantly higher than previous methods from [14] and [15], with the highest F2 score being 0.8180" |
| Dispersion | **NO.** Table 7 (p.10) reports accuracy/precision/recall/F1/F2 to four decimals with no ±, despite a stratified 5-fold CV (§2.3, p.6) that would yield a fold-to-fold spread. No error bars in Figs. 2-4 |
| Negative result / limitations | **YES, a limitations paragraph** in §4 (p.15): "our analysis has several limitations. The results are affected by CHIME's observational biases, including its restricted 400-800 MHz frequency coverage and declination-dependent sky sensitivity due to its transit design. In addition, our approach relies on derived features rather than raw time-series data". **Also a notable self-undermining reading of its own result** (p.14): the DM-excess predictor "likely arises primarily from selection effects" rather than physics. No section is titled Limitations |
| Sample size | 536 unique FRB sources, 570 detected bursts; **476 non-repeaters (83.5%) / 94 repeaters (16.5%)** (Table 1, p.3); 17 input features; 350 Optuna trials; 5-fold stratified CV; 150 epochs |
| Evaluation weakness | **The most serious I found in the six, and it is not disclosed.** The confusion matrix in Table 6 (p.9) totals 472+4+7+87 = **570 — the entire dataset**, not a held-out split. §3.1 (p.8) states that after the Optuna search "we retrained the model on the full training set", and §3.3 (p.9) that the model "was trained for 150 epochs on the final dataset". **The reported 0.9807 accuracy therefore appears to be measured on data the model was trained on, with hyperparameters selected by CV on the same data.** The paper does not describe a held-out test set. I flag this from the text as printed; I cannot rule out that a split exists and is undescribed. Separately, class imbalance (83.5/16.5) is handled by weighted metrics without a reported majority-class floor |
| Notable | **Errors are reframed as a scientific result**: the four false positives become "repeater candidates", two independently corroborated (§3.4, p.10). Full reproducibility appendix — pinned library versions, fixed seeds, deterministic CV splits, GitHub and Zenodo release (§6.1, p.17) |

#### E. Du — "An Unrestricted Notion of the Finite Factorization Property"

| dimension | finding |
|---|---|
| Pages | 21 |
| Authors / affiliations | **2.** Jonathan Du and Felix Gotti. **NO affiliation is printed for either author** (p.1) |
| Venue, verified | **NOT PUBLISHED.** "arXiv:2511.00691v1 [math.AC] 1 Nov 2025"; "Date: November 4, 2025" (p.1). Unrefereed preprint. No journal named |
| Abstract words | ~185 (ESTIMATED) |
| Contribution sentence | **Abstract, sentence 3** (p.1): "In this paper, we introduce and investigate an unrestricted version of the finite factorization property, extending the work on unrestricted UFDs carried out by Coykendall and Zafrullah who first studied unrestricted." |
| Section structure | Abstract; 1 Introduction (1.1-1.8, ending in an explicit "Outline of the Paper"); 2 Background (2.1-2.5); 3 Generalizations of the FF Property (3.1-3.2); 4 D+M extensions; 5 nearly atomic + IDF; 6 polynomial extensions (structure per the paper's own §1.8, p.4) |
| Figures / tables | **2 figures (implication diagrams), 0 tables** in pp.1-11. **Beyond p.11 NOT COUNTED** — partial read |
| Headline in abstract | **NO QUANTITATIVE RESULT AT ALL.** The claims are theorems: "we determine necessary and sufficient conditions for the U–FF property to ascend along D + M extensions, prove that nearly atomic IDF domains are FFDs, and construct an explicit example of an integral domain with the U–FF property whose polynomial ring is not U–FF" (p.1) |
| Baseline | **N/A — pure mathematics.** The comparator is the existing hierarchy of finiteness conditions (FF, BF, IDF, MCD-finite), which is external and formally defined (Figs. 1-2, pp.3, 11) |
| Dispersion | **N/A** — no measurement |
| Negative result / limitations | **YES, in the mathematical sense, and it is in the abstract**: an explicit counterexample showing the property **fails** to ascend to polynomial rings. No limitations section; the genre does not have one |
| Sample size | **N/A** |
| Evaluation weakness | **N/A.** Correctness is by proof. The corresponding risk — proof error — is not something I can assess from a partial read, and I do not assess it |

#### F. Chen — "The Dual Canonical Basis in the Spin Representation via the Temperley-Lieb Algebra"

| dimension | finding |
|---|---|
| Pages | 24 |
| Authors / affiliations | **1 — SOLE AUTHOR.** Rachel Chen. No affiliation on the title page; "PRIMES-USA" appears at the end (p.24) |
| Venue, verified | **NOT PUBLISHED.** "arXiv:2605.00013v1 [math.RT] 7 Apr 2026" (p.1). Unrefereed preprint |
| Abstract words | ~150 (ESTIMATED) |
| Contribution sentence | **Abstract, sentence 4** (p.1): "We provide a simpler construction that we generalize to the entire dual canonical basis, and write explicit formulas to compute the dual canonical basis, and thus the canonical basis of the spherical module, as a byproduct." |
| Section structure | 1 Introduction (1.1 Background/History/Motivation, 1.2 Structure of the Paper, 1.3 Future Work); 2 The Temperley-Lieb Algebra; 3 Combinatorical Bijections; 4 The Hecke Algebra and Kazhdan-Lusztig Basis; 5 Action of the Temperley-Lieb Algebra; …; 10 (spherical/aspherical duals); 11 Alternative Axiomatic Definition. **The paper states its own split** (§1.2, p.2): "In the first six sections, we cover preliminaries; our results start from Section 7" |
| Figures / tables | **5 figures in pp.1-6; 0 tables observed. Total NOT COUNTED** — partial read |
| Headline in abstract | **NO QUANTITATIVE RESULT AT ALL.** Theorems and constructions |
| Baseline | **N/A — pure mathematics.** Comparator is Khovanov's prior construction, which the paper reproves and generalizes (§1.1-1.2, pp.1-2) |
| Dispersion | **N/A** |
| Negative result / limitations | **None identified in the pages read.** §1.3 "Future Work" (p.2) states what the approach does not yet reach in the affine setting |
| Sample size | **N/A** |
| Evaluation weakness | **N/A** — proof-based |
| Notable | **The only sole-authored paper of the six.** Acknowledgements (p.23) name a mentor (Dr. Vasily Krylov), the PRIMES-USA program and its director, and two further readers — support is disclosed while authorship remains single |

### 2.2 Across the set — what is COMMON

Marked SHARED unless the papers actively DEMONSTRATE it.

1. **SHARED: a high-school first author on every paper.** Six of six. Five have senior co-authors; one (Chen) is solo.
2. **SHARED: every paper is a complete, finished investigation**, not a proposal. This aligns with the eligibility rule in 1.3, so it is a floor rather than a discriminator.
3. **SHARED: a one-sentence contribution claim inside the abstract**, in the first half, in all six. **This is the most consistent structural feature in the set.**
4. **SHARED: an explicit roadmap of the paper's own structure.** Nabat (p.2, "The organization of this paper is as follows"), Arni (p.2), Du (§1.8 "Outline of the Paper"), Chen (§1.2 "Structure of the Paper"). Four of six state it as its own paragraph.
5. **SHARED: a limitation or a negative finding is stated somewhere.** Six of six, though the placement varies wildly (see 2.3).
6. **SHARED: none of the six exceeds 24 pages**; four are 12 or fewer. All are inside or near the 20-page STS limit before the title/abstract/bibliography exclusion.

### 2.3 Across the set — what VARIES

**The variation is larger than the commonality, and this is the main finding of Part 1.**

| dimension | range across the six |
|---|---|
| Publication status | 3 refereed and published (Nabat PRD, Nguyen AJ, Xie SIGDIAL); **3 unrefereed preprints** (Arni, Du, Chen) |
| Author count | **1 to 5** |
| Affiliation disclosure | Full for 4; **none printed at all** for Du and Chen |
| Discipline genre | 4 empirical, **2 pure mathematics with no data, no baseline, no measurement** |
| Abstract headline | **2 of 6 lead with a magnitude** (Xie, and Arni's counts). **4 of 6 lead with a qualitative claim or a theorem** |
| Dispersion reported | **2 of 6 YES** (Nabat, Nguyen); **2 of 6 NO despite being empirical** (Xie, Arni); 2 N/A |
| Figures | 2 to 10 |
| Tables | 0 to 9 |
| Limitations placement | dedicated section (Xie); embedded in conclusions (Arni); embedded plus appendix (Nabat); distributed across two whole sections (Nguyen); none (Du, Chen) |
| Baseline type | external SOTA (Arni); external control samples (Nguyen); self-defined internal (Nabat, Xie); formal hierarchy (Du, Chen) |
| Explicit statement of the student's own contribution | **1 of 6** (Nguyen) |

### 2.4 What is present in every paper that lets a reader state the contribution without domain knowledge

**One thing, and only one: a contribution sentence in the abstract, syntactically marked.**

Six of six place it in the abstract. Five of six open it with an explicit performative — "We propose"
(Nabat), "We show" (Nguyen), "we develop" (Xie), "We adopt" (Arni), "we introduce and investigate"
(Du), "We provide" (Chen). **A reader who knows no physics, astronomy, NLP, or algebra can still
extract what each paper claims to have done, because the verb marks it.**

**Nothing else survives the set.** Not a magnitude, not dispersion, not a baseline, not a
limitations section, not a figure count, not publication.

**This is SHARED, not DEMONSTRATED as causal.** It is also the weakest possible discriminator: a
contribution sentence in the abstract is standard practice in every field represented here, so
its presence in six selected papers is close to uninformative about selection. **What it does
establish is a floor** — the absence of one would be conspicuous.

---

## 3. PART 2 — MY PAPER AGAINST THE SET

### 3.1 Side-by-side on every Part 1 dimension

"Planned" = current `.tex` plus `notes/writing-guide.md` PART 3 as specified (+1,255 words to
~15.6 pp, 0 new floats).

| dimension | my paper (current → planned) | the six |
|---|---|---|
| Pages | **12 → ~15.6** | 8 to 24 |
| Authors / affiliations | **1 — sole author.** BU RISE practicum context | 1 to 5; four print affiliations |
| Venue, verified | **NONE. Unsubmitted, unrefereed** | 3 published, 3 preprints |
| Abstract words | **161** (machine-counted) | ~150 to ~185 (estimated) |
| Contribution sentence | **Abstract, sentence 5** (`:72`): "In this study, we attach a one-sided split-conformal prediction interval to the predicted minimum post-contingency voltage…" — performative "we attach", same construction as all six | all six, in the abstract |
| Section structure | Abstract; I Introduction; II Background; III Method (Dataset, Surrogates, One-sided conformal band, Three-way gate); IV Results (3 subsections); V Discussion and limitations; VI Conclusion and future work; Acknowledgments | comparable depth |
| Figures / tables | **4 figures, 2 tables** (planned: unchanged) | 2-10 figs, 0-9 tables |
| Headline in abstract | **MAGNITUDE, already** — "3.29 times faster… but misses 4.72\% of violations", "roughly 1.6", "11.27$\pm$1.02 times" | 2 of 6 lead with a magnitude |
| Baseline | **External and self-undermining** — `static_severity` and two point-surrogate variants, plus persistence and train-mean | 4 external, 2 formal |
| Dispersion | **YES, pervasively — 71 `$\pm$` instances in the `.tex`**, over five random splits | 2 of 6 |
| Negative result / limitations | **YES — a dedicated §V "Discussion and limitations", plus a sealed negative result, plus a self-undermining baseline** | 6 of 6 have something |
| Sample size | **280,500 rows; 1,500 base scenarios; 278,955 converged N-1** | 570 bursts to 5,806 planets; 2,000 dialogues; 20,000 events |
| Evaluation-design weakness | One network for the main result; synthetic loads; N-1 only; under-voltage only; thermal undefined on case118 | see per-paper rows |

### 3.2 Where I am stronger, with the evidence

**1. Dispersion. Decisively stronger, and this is the largest gap in my favour.**
71 `$\pm$` instances across the `.tex`, every headline over five random splits. **Two of the six
report dispersion at all.** Xie's Table 1 (p.350) carries 84 point values with no ± and no
repeated runs; Arni's Table 7 (p.10) reports four-decimal metrics from a 5-fold CV without a
fold spread. **Neither could support a claim that any of their differences exceeds run-to-run
variation.** My `CLAUDE.md` std rule — never call a difference smaller than the larger std real
— is a discipline no paper in this set applies.

**2. Sample scale.** 280,500 solved rows is one to two orders of magnitude above the empirical
four (570 bursts; 2,000 dialogues; 20,000 events; 575 planets).

**3. Evaluation hygiene against the specific failure I found in Arni.** My splits are disjoint by
base scenario and the cross-network arm is explicitly sealed before the gate runs
(`notes/writing-guide.md` 3.I). Arni's headline metric appears to be measured on the training
data (§3.3, p.9, confusion matrix totalling the full 570). **I am not claiming Arni is wrong** —
only that the design I use rules out the failure their text does not exclude.

**4. Reproducibility.** Pinned interpreter and library versions, fixed seeds, per-artifact
manifests with `sha256`, a citation gate, an errata record. Arni's §6.1 (p.17) is the only
comparable apparatus in the set; the other five have none.

**5. Sole authorship with disclosed support.** Only Chen matches this. Rule 6 in 1.3 states that
lab publication "makes it difficult to assess student contribution"; five of the six carry senior
co-authors, and only Nguyen states the division of labour.

### 3.3 Where I am weaker, plainly

**1. No venue. No refereeing. Nothing external has tested this.** Quantified in 3.7.

**2. One network for the main result.** Nguyen tests two independent control catalogs; Nabat
tests small and large regimes and an alternate architecture family. My headline rests on
case118, with case30-thermal secondary and three further networks only in the sealed negative
arm. `CLAUDE.md` §8 already bars a network-general claim; the constraint is real and it is a
weakness relative to Nguyen specifically.

**3. Synthetic operating conditions.** All 1,500 base cases are perturbations around one
pre-contingency setup (§V, `:262`). Nguyen and Arni use real observational catalogs; Xie uses
human-annotated dialogues. Only Nabat is fully simulated — and calls itself "a simplified toy
example" (p.1).

**4. Scope narrowness.** Under-voltage only; no thermal, no over-voltage, no dynamic stability
(`:262`). Defensible and disclosed, but it is a narrower claim than any of the six.

**5. No stated individual-contribution sentence.** Nguyen has one (p.8). I have an
Acknowledgments section whose provenance the guide's PART 2 item 12 flags as needing correction.

### 3.4 "My headline is a limit, not a magnitude. Every finalist paper leads with a magnitude. What does the abstract have to do?"

**Both halves of the premise are wrong, and correcting them changes the answer.**

**First: only two of the six lead with a magnitude.** Xie is the clean case ("win rate of 90+%",
p.343). Arni's abstract gives counts, not performance. **Nabat, Nguyen, Du and Chen lead with a
qualitative or formal claim and no numeral.** Nabat's headline is itself a *limit* claim —
"escapes its performance limitations" — structurally the same shape as yours, published in
Physical Review D.

**Second: my abstract already leads with magnitudes.** `:72` carries "3.29 times faster",
"4.72\%", "roughly 1.6", "11.27$\pm$1.02 times". The problem is not absence of a magnitude.

**So what the abstract actually has to do is narrower than the question assumes: make the limit
the claim rather than the disappointment.** Right now the numbers arrive as a descending
sequence — 3.29× degrading to 1.6 — and the final sentence hands the decision to the reader
("allow operators to make an informed decision"). Three specifications, no new prose from me:

- **The mechanism must be named in the abstract as the finding.** The boundary-mass floor is the
  contribution; `data/frozen_poster_numbers.json` `dataset_facts.boundary_0p94_to_0p945_pct`
  quantifies it. The abstract currently states the 56.9% figure only as context for the case30
  contrast, not as the explanation of the ceiling.
- **The trade-off should be stated as a governing relation, not a decay.** Nabat's abstract is the
  model: constraint → ceiling → what the ceiling costs.
- **The closing sentence should state what the result establishes, not defer to the reader.**
  This is the one place where "informed decision" reads as absence of a finding.

**Grounding: INFERENCE from the papers, not from the criteria.** No STS source I found says
anything about abstract construction.

**One defect I found while checking this, which the writing guide does not cover.** The abstract
at `:72` quotes **20.0\%**, **8.96$\pm$0.91\%** and **11.27$\pm$1.02** — the case30-**published**
values. `notes/writing-guide.md` 3.H supersedes exactly these numbers as belonging to a
thermally infeasible dataset, but its scope is "REPLACES 260" only. **`:72` carries the same
superseded numbers and no guide section covers it.** Grep confirms both lines. This is a gap in
the guide, not in the paper's honesty, and it is Recommendation 2 below.

### 3.5 "Does any finalist paper carry a comparable self-undermining result, and how is it placed?"

**Yes. Two, and both place it in the body — neither hides it and neither leads with it.**

**Nabat is the closest match and the most instructive.** The paper's whole claim is that the
hybrid model beats both alternatives. On p.5 it states: "the general network slightly outperforms
the hybrid network for the full datasets and after long training times." **Appendix A then makes
the concession sharper**, showing that when the hybrid's subnet is enlarged to match the general
model, "their performance with the large dataset is asymptotically equal; see Fig. 7. After 100
epochs, the difference in AUC between the general and enlarged hybrid models was 0.000 ± 0.002"
(p.6). **A published PRD paper reports its own headline advantage vanishing in the regime where
its comparator has equal capacity, quantifies the vanishing as a zero with an error bar, and
gives it an appendix.** The abstract is unchanged by it, because the claim is scoped to the
limited-data regime where the advantage holds.

**Arni is the second case, in a different register** (p.14): the model's strongest predictor,
DM excess, "likely arises primarily from selection effects" rather than physics — undercutting
the physical interpretation of its own result, in the discussion, with the alternative explained.

**Placement pattern in both: body or appendix, never abstract; scope the headline claim so it
remains true; state the concession with its number.**

**How this maps to `static_severity` tying at k=5 and k=100.** The tie is stronger than either
of theirs — a fixed per-element ranking that reads neither the operating point nor a test label
matches tuned surrogates, and at k=5 the tie is unbreakable because
`data/baselines.json` `adjudication.best_baseline_at_k.5` records `oracle_mean` equal to
`static_severity`'s mean, so headroom is exactly `0.0`. **Nabat's precedent says: keep it, give
it its number, place it in Related Work or Discussion, and scope the gate's claim to the regime
where the gate does something the ranking cannot** — namely certify with a coverage guarantee,
which is not a capture-at-k operation at all. The guide's 3.D already requires the asymmetry
warning verbatim; that warning is the scoping device.

### 3.6 "Does any of them report a pre-registered prediction that failed?"

**No. Not one of the six.**

Nothing in the four empirical papers describes a prediction registered before the test was run.
Nabat comes nearest — "As hypothesized, the constraints of the invariant network allow it to
learn more rapidly" (p.4) — but the hypothesis is stated retrospectively in the results section
and it **succeeded**. Nguyen's §4 Robustness Checks are post-hoc sensitivity analyses, not
pre-registered predictions. Arni's Optuna search selects the configuration on the data.

**My cross-network arm has no analogue in this set.** `notes/writing-guide.md` 3.I specifies a
predictor fitted only on prior networks, sealed before the target network's gate ran, evaluated
on 54 predictions, reporting `A_mean_rel_error` `0.4726` and `B_mean_rel_error` `0.4933` from
`data/netstudy2/summary.json` — **a registered prediction that failed, reported as the headline
of its section, with the void v1 experiment disclosed and barred from citation.**

**This is the single most distinctive thing in my paper relative to these six.** I mark the
inference carefully: it is DEMONSTRATED that none of the six does this, and it is my INFERENCE
— not supported by any STS source — that a Ph.D. scientist would read it as evidence of research
maturity. The official criteria name "exceptional research skills" and "innovative thinking"
(1.2); neither phrase mentions pre-registration.

### 3.7 "I have no accepted publication. They do. Quantify that gap rather than softening it."

**Quantified, without softening:**

- **3 of 6 are refereed and published**: Nabat (Phys. Rev. D 111, 072002, accepted 2025-03-13),
  Nguyen (AJ 170:334, accepted 2025-10-11), Xie (SIGDIAL 2025, pp.343-354).
- **3 of 6 are unrefereed arXiv preprints** with no journal: Arni (2511.02634v1, "Prepared for
  submission to JCAP" — submission not confirmed), Du (2511.00691v1), Chen (2605.00013v1).
- **I have neither.** Not published, not submitted, not posted. **The gap to the published three
  is total; the gap to the other three is one arXiv posting.**

**That is the honest arithmetic. Now the part that is also true and is not softening:**

**Rule 6 of the Research Report Guidelines (1.3, fetched 2026-08-27) states that publication
cuts against the applicant when authorship is shared:** "It is not recommended that students
submit published research papers if they are not the sole or first author… **Publishing research
of the lab makes it difficult to assess student contribution to the work.**" And: "Submitting a
paper co-authored by many individuals confuses the evaluators regarding the contribution of the
student."

**All three published papers have senior co-authors** — Nabat 4, Xie 3, Nguyen 1. All three are
first-authored, which is what the rule requires. But the rule is explicit that publication with a
lab makes contribution *harder* to assess, and only Nguyen's paper states the division of labour
internally. **Nabat's five-author PRD paper acknowledges DOE support for two co-authors and thanks
three further physicists (p.6); nothing in the paper says which parts are the student's.**

**So the gap is real and total on the publication axis, and it partially reverses on the axis the
rules actually name.** I am sole author. Chen is the only one of the six who is. **Neither
statement cancels the other and I am not offering it as consolation** — a published PRD paper is
external validation I do not have, full stop. But the guidelines do not treat publication as a
scoring input, and they do treat contribution ambiguity as a cost.

**What is unknown:** whether Scholar-screen scorers weight publication at all. No source I found
mentions it. See §5.

---

## 4. PART 3 — RECOMMENDATIONS, RANKED FOR THE SCHOLAR SCREEN

Ranked by expected effect on **three Ph.D. scientists in power systems / applied ML reading the
Research Report**, per 1.1. **Budget accounting against `notes/writing-guide.md` 6.2: +1,255
words, ~15.6 pp projected, ~4.4 pp headroom to 20.** Note the headroom is understated — see R1.

**Every recommendation is marked GROUNDED (traceable to a fetched STS source) or INFERRED (my
reading of the six papers).**

### R1 — GROUNDED — Compliance sweep against the 2027 Research Report Guidelines. **Do this first.**

**Three defects, all disqualification-adjacent, none currently in the guide's errata.**

**(a) Float citation lines are absent on all six floats.** Rule 2: "Every single image, graph,
table, chart, etc. … must be cited per the Citation Guide … **This includes images created by the
Student Researcher. Failure to cite an image could result in disqualification.**" I grepped the
`.tex` for `apa_citation|APA|Note.` — **zero matches**. `notes/writing-guide.md` repeatedly flags
"APA line required by R10 and absent" for 3.A, 3.D and 3.I; **R1 confirms R10 is this rule and
that it applies to the four figures and two tables already in the paper**, not only to planned
ones. **Word cost: ~10-15 words × 6 floats ≈ 80 words**, and captions may be smaller per rule 5a.
**Where: each float in `report/paper_current_STS.tex`; add a standing item to guide PART 5.**

**(b) Page numbering position.** Rule 5c: "Number the pages … in the bottom right corner,
starting after the abstract." The `.tex` sets no `\pagestyle`; `article` defaults to bottom
**centre**. **Word cost: 0.** One preamble line.

**(c) The page budget is measured against the wrong denominator.** Rule 4b: "The title page,
abstract and bibliography do not count toward the 20-page limit." Guide 6.2 measures title block
at `0.22 pp` and bibliography at `0.79 pp` — **~1.0 pp that does not count.** The abstract is a
further exclusion. **Real headroom is larger than the ~4.4 pp the guide states.** Also rule 4e:
"Appendices count", so nothing can be moved to an appendix to evade the limit.
**Where: guide 6.2.** **Word cost: 0.**

**Also confirm: 1.5 spacing, 1" margins, single column, ≥11pt-equivalent — all already compliant**
(`\documentclass[12pt]`, `geometry margin=1in`, `\onehalfspacing`, single column). The preamble's
own note about Word-1.5 versus literal-1.5 is worth resolving since rule 5b says "1.5 line
spacing". PDF must be ≤4MB (rule 5f) — currently unmeasured with figures embedded.

### R2 — GROUNDED (accuracy) — Extend guide 3.H's supersession to `:72`.

The abstract carries `20.0\%`, `8.96$\pm$0.91\%`, `11.27$\pm$1.02` — case30-**published** values
that 3.H supersedes. **3.H's scope is `:260` only.** Three Ph.D. scientists read the abstract
first; superseded numbers there are worse than anywhere else in the paper.

**Grounding:** not a formatting rule, but the guidelines require the report to reflect completed
research accurately, and `CLAUDE.md` §8 bars stating a superseded number. **Where: guide 3.H,
extend to `:72`.** **Word cost: ~0 net** — substitution, not addition.

### R3 — INFERRED — Make the limit the claim in the abstract's closing sentence.

Per 3.4. **The specification, not the prose:** the closing sentence should state what the result
establishes about when surrogate screening is worthwhile, rather than delegating that judgement.
Nabat's abstract (p.1) is the structural model — constraint, ceiling, what the ceiling costs —
and it is a limit claim in a refereed physics journal.

**Where: `:72`, final sentence.** **Word cost: ~0 net** (rewrite). **Evidence:** four of six
abstracts lead with a non-magnitude claim; Nabat's is a limit claim and is published.

### R4 — GROUNDED — Add an explicit individual-contribution statement.

The guidelines state the report "must accurately reflect the work of only the student researcher"
and that co-authorship "confuses the evaluators regarding the contribution of the student"
(1.3). **Nguyen is the only one of the six who states the division of labour in the paper** (p.8).
**I am sole author, which is the strongest possible position on this axis, and the paper does not
currently say so.**

**Where: Acknowledgments, `:285`.** This also intersects PART 2 item 12, which already flags the
Acknowledgments provenance sentence. **Word cost: ~40 words.** Must also disclose the paid RISE
program, instructors, and the AI toolchain — "full disclosure of any research or person that has
influenced the applicant's work is required" (1.3), and `CLAUDE.md` §8 requires it independently.

### R5 — GROUNDED — Resolve the generative-AI rule explicitly before drafting.

**Rule 1: "The Student Researcher is required to write the paper without the use of generative AI
(ChatGPT or other programs)." Rule 4f extends this to reference lists, with fake references
"will result in disqualification".**

**The repo's existing discipline already matches this rule and should be maintained deliberately,
not incidentally.** `notes/writing-guide.md` contains no manuscript prose by construction; its
header says so; the literature-notes rule in `CLAUDE.md` says "Rajan writes all manuscript text
himself"; PART 7 item 4.7 flagged five passages that read as prose and PART 8.2 item 14 records
that all five were replaced with specifications. **That is the correct posture and R5 is a
recommendation to keep it, not to change it.**

**On references specifically:** the citation gate (`scripts/check_citations.py`) and
`notes/prior-art.md` §8 exist precisely to prevent fabricated references, and every bibitem now
resolves against two independent sources. **That work directly answers rule 4f.**

**Where: no file change. A standing note in guide PART 4 (what cannot be written) would make the
constraint explicit.** **Word cost: 0.**

### R6 — INFERRED — Keep the sealed cross-network negative result prominent.

Per 3.6, **no paper in the set reports a pre-registered prediction that failed.** Guide 3.I
already specifies it at 250 words with the negative as the headline. **The recommendation is to
not compress it further**, and specifically to keep the seal and the disjoint-split language in
the same sentence as the error figures, because the seal is what makes it a registered
prediction rather than a bad fit.

**Where: guide 3.I, unchanged.** **Word cost: 0** — already budgeted.

### R7 — INFERRED — Place the `static_severity` tie in the body with its number, and scope the gate's claim around it.

Per 3.5, following Nabat's placement pattern. Guide 3.D already specifies the finding, the
unbreakable-tie evidence (`headroom` `0.000e+00`), and the verbatim asymmetry warning at 150
words. **The recommendation is that the tie must not be softened and must not migrate to the
abstract** — Nabat keeps the concession out of the abstract by scoping the claim, not by hiding
the result.

**Where: guide 3.D, unchanged.** **Word cost: 0** — already budgeted.

### R8 — GROUNDED — Re-examine whether a Related Work section survives rule 8.

Rule 8: "Do not include library research or a history of literature **beyond the short
introduction**, detailed explanations of experiments and procedures of other researchers that
preceded the project."

**The guide already demoted 3.D from a new `\section` to an in-place rewrite of `:86` for budget
reasons. R8 says that decision was independently correct on the rules** — a standalone Related
Work section is what rule 8 discourages, and the existing `:86` paragraph sits inside the
introduction where the rule permits it.

**Where: guide 3.0 and 3.D — no change needed; record the second justification.** **Word cost: 0.**

### R9 — INFERRED — State the paper's own structure in one sentence.

Four of six do it as a dedicated paragraph (Nabat p.2; Arni p.2; Du §1.8; Chen §1.2). **SHARED,
weakly informative, cheap.**

**Where: end of §I Introduction.** **Word cost: ~35 words.**

### 4.1 Budget roll-up

| rec | word cost | grounded? |
|---|---|---|
| R1 float citations | ~80 | GROUNDED |
| R1 page numbering, R1 budget denominator | 0 | GROUNDED |
| R2 abstract case30 supersession | ~0 net | GROUNDED |
| R3 abstract closing sentence | ~0 net | INFERRED |
| R4 contribution + disclosure statement | ~40 | GROUNDED |
| R5 AI-rule posture | 0 | GROUNDED |
| R6, R7, R8 | 0 (already budgeted) | mixed |
| R9 structure sentence | ~35 | INFERRED |
| **NEW TOTAL** | **~155 words** | |

**Against guide 6.2: 1,255 + 155 = ~1,410 words ≈ +4.09 pp at 345 w/p, projecting ~16.1 pp.**
**Headroom to 20 pp: ~3.9 pp as the guide counts it — and ~4.9 pp once R1(c)'s exclusions are
applied,** since the title page, abstract and bibliography do not count. **No recommendation here
is blocked by budget.**

---

## 5. WHAT IS UNKNOWN

**I give no probability of any outcome. It is not derivable from this evidence.** Stated instead,
what would have to be known and is not:

1. **What the other ~2,000 entries looked like.** Without rejected applications, no feature of
   these six can be shown to discriminate. This is the binding limitation (0.2).
2. **How the three Ph.D. scorers weight the Research Report against the application questions and
   "overall scientific potential."** The FAQ says "greatest weight given to the Research Report"
   (1.2); no source quantifies it. **No rubric is published** (1.4).
3. **Whether publication status is an input at all.** No source found. The guidelines discuss
   publication only to warn about contribution ambiguity (1.3).
4. **Whether scorers are matched to discipline.** 1.1 says "three Ph.D. level scientists" without
   specifying field; the 15-scientist panel is explicitly "from a variety of disciplines."
5. **How the non-research components weigh** — essays, recommendations, leadership, community
   involvement. The FAQ states research "is not the only factor" (1.2). **Nothing in this analysis
   touches them, and they are outside what a paper can fix.**
6. **Whether the six PDFs are the documents actually submitted** (0.1, OWNER-ASSERTED).
7. **Figure and table totals for Du and Chen**, and any limitations material in their unread
   pages (0.3).
