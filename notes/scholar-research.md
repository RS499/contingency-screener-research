# scholar-research.md

What is publicly documented about how Regeneron STS Scholars (top 300) are selected, what is observable
about the 260 scholars who were not finalists, how your file compares, and a ranked plan from
2026-09-14 to the deadline, **Thursday 2026-11-05 at 8:00 pm ET**.

**Written 2026-09-14. Git HEAD `14bf5ec`.** Report only: no `.tex` edit, no application text, no git.
Prompt logged in `notes/ai-prompt-log.md` (entry dated 2026-09-14).

**No probability of any outcome appears here.** Where one would be tempting, §5 states what is unknown instead.

---

## 0. METHOD, LABELS, AND CORRECTIONS TO THE INPUTS

### 0.1 How this was produced

1. **Web fan-out.** The `deep-research` workflow ran five search angles, fetched 20 sources, extracted
   99 claims, checked 25 of them with three independent votes each (24 confirmed, 1 refuted) and merged
   the survivors into 13 findings. The workflow's claims are cited below as "(workflow, vote 3-0)".
2. **Primary PDFs, read directly** with `pdftotext -layout` and copied to the session scratchpad, not the repo:

   | document | URL | sha256 | read |
   |---|---|---|---|
   | STS 2027 Rules and Entry Instructions (50 pp) | `https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Official-Rules.pdf` | `f2ad0aaf7ae88c67f3bc4dfc5f4313450794401745d05cefb8a827795790f9d1` | printed pp. 1-14 and 29-50 in full (page numbers below follow the book's own table of contents, e.g. Appendix 5 = p.35; the workflow's findings used an offset of one); pp. 15-28 (human, animal, PHBA and hazard rules) grep only |
   | STS 2027 Application Questions (preview) | `https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Application-Questions.pdf` | `92e989bd146058565a900a9769e8dffd26a72a71f3509ad6def3d71582c2da9e` | complete |
   | 2026 Scholar Book | `https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2026/Program-Books/Scholar.pdf` | `2cfa8b497b77edb26ca7b33c9ed9988d3138c53a53d6d0049812985f7e7f1be3` | complete; parsed to 300 rows |
   | 2025 Scholar Book | `https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2025/Program-Books/Scholar.pdf` | `c3476a23b9bf455bf0c6a687f30077115e3d53c496db1895289e6fe2961ba0bc` | Pennsylvania section and a school search only |

3. **HTML pages** (evaluator page, FAQ, tips blog, 2026 finalists page) were fetched on 2026-09-14.
   **Verbatim fidelity differs by route.** The finalists page was downloaded with curl and its text read
   directly. The evaluator page, the FAQ and the tips blog came through a fetch tool that routes page text
   through a summarising model. Those quotes are as the tool returned them and were **not byte-checked**.
   The workflow's verifiers fetched the evaluator page independently and returned the same sentences.
   **One failure was observed:** the fetch tool said the 2026 scholars page lists 2 Pennsylvania
   scholars; the Scholar Book PDF lists 5. **Counts in this file come from the PDFs, not that tool.**

**Every URL in this file was fetched 2026-09-14** unless another date is given.

### 0.2 Evidence labels

| label | meaning |
|---|---|
| **RULE** | A binding instruction to entrants, in an official document. What the document says is demonstrated by the document itself. |
| **PROCESS** | The Society describing its own selection process. It is authoritative about the intended process, but an outsider cannot audit how it is applied. It **ASSERTS**. |
| **DATA** | Counts published by the Society or computed from its lists. It **DEMONSTRATES** what the counts are, and nothing about why. |
| **PROMO** | Announcement boilerplate. It **ASSERTS**. |
| **GROUNDED / INFERRED** | Used in §3-§4. GROUNDED: traceable to a fetched source named in the row. INFERRED: my reading, with no source behind the step. |
| **OWNER-ASSERTED** | A fact about you, taken from your prompt or your activities draft. I did not verify it. |

### 0.3 Corrections to the prompt and to `notes/finalist-paper-analysis.md`

| # | what was believed | what was found | source |
|---|---|---|---|
| C1 | "`report/activities.md`" | **Does not exist.** The activities list is `report/STS Activities Science Fair Projects.md` (untracked). That file was used. | `ls report/` |
| C2 | "Task 4's six contribution boxes" | The six 200-word boxes are **Task 6 ("Science Research Description"), Q12 "What Did You Do?"**. Task 4 is **Recommendation Requests** in both official documents. | Application Questions, Task 6 Q12; Rules p.8 |
| C3 | "Task 5's AI disclosure" | **Correct.** Task 5 is Disclosures, and the AI questions are Q8-Q9. | Application Questions, Task 5 |
| C4 | "the Task 7 essays" | **Wrong in both documents.** Task 7 is the **Rules Wizard**. Essays are **Task 10**: two essays, 200 words each. | Rules p.8; Application Questions, Task 10 |
| C5 | Task numbering is stable | **It is not.** The Rules list Tasks 1-12. The Application Questions preview says "Complete Tasks 1-13" and calls the High School Report both "Tasks 4a-c" and "task 2c". **Identify tasks by name, not number**, and check the numbering in the live portal. | both PDFs (workflow, vote 3-0) |
| C6 | "No rubric, weighting, or score breakdown" (finalist analysis §1.4) | **Partly corrected.** The 2027 Rules name **four evaluation areas**. A rubric **exists and is given to evaluators**, but its content and weights are **not published**. | §1.1, §1.3 below |
| C7 | The "outstanding research, leadership skills…" string was NOT LOCATED (finalist analysis §1.2) | **Located, verbatim**, on the 2025 and 2026 scholar press releases and scholar pages. It is PROMO text. | §1.6 (workflow, vote 3-0) |
| C8 | Whether evaluators are matched to discipline was unknown (finalist analysis §5 item 4) | **Answered for the process as stated:** evaluators are "in the appropriate scientific discipline", and the chosen category "will determine the expertise of the initial review only." | Rules p.12; Appendix 1, p.30 |
| C9 | "~2,600 entrants" | 2026: **2,612 entrants**, per the 2026 finalists page. 2025: 2,471. | §2.1 |
| C10 | Prior compliance item R1(a), float citation lines absent | **Now resolved.** `report/paper_current_STS.tex` has 7 floats and 7 "created by Rajan Saha" lines (`:138, :201, :239, :251, :269, :286, :301`). | grep, sha256 `f0204900…bb83` |

---

## 1. PART 1: WHAT THE SOCIETY ITSELF SAYS

### 1.1 The four evaluation areas (PROCESS)

Rules 2027, "Selection Process", printed p.12:

> "Regeneron STS utilizes a holistic selection process to identify future leaders in science,
> technology, engineering and mathematics. All components of the entrant's application are reviewed and
> considered; the research project, while important, is not the only factor for award decisions."

> "After reviewing entries for completeness, accuracy, eligibility and rules adherence, student age,
> citizenship and residence, all portions of every eligible submission are evaluated by three or more
> doctoral scientists, mathematicians, and/or engineers in the appropriate scientific discipline. The
> originality of each entry is checked using plagiarism monitoring software. A rules committee reviews
> each project for compliance with the eligibility, scientific and integrity rules. Regeneron is not
> involved in the selection process."

> "Entries are evaluated in four areas:
> • Research Report and Scientific Merit
> • Student Contribution to the Research
> • Academic Aptitude and Achievement
> • Overall Potential as a Future Leader of the Scientific Community"

> "Regeneron STS only considers the content shared in each entrant's application package; Regeneron STS
> does not consider updates or materials sent after the submission deadline. Demonstrated student
> interest, outside letters of recommendation and quotas of any sort (category, region) are not factors
> in the selection process. Evaluators consider student circumstances and access to labs, activities and
> other personal contexts in relation to student achievement."

**What this demonstrates and what it does not.** It shows the named areas and the stated exclusions. It
does **not** give weights, points, a score scale, or how the four areas combine. "Outside letters of
recommendation" means letters beyond the portal recommendations. The portal recommendations are
collected and are part of "all portions" (workflow, vote 3-0).

### 1.2 Weighting (PROCESS, qualitative only)

FAQ, `https://www.societyforscience.org/regeneron-sts/frequently-asked-questions/`:

> "with greatest weight given to the Research Report"
> "the research is very important, it is not the only factor when naming scholars and finalists"
> "Entries are reviewed by three or more PhD scientists, mathematicians, or engineers in the subject area
> of the entry. Scholars and finalists are selected by the judges, using all available entry evidence"
> "All components of the application package are considered in this review"
> "Entrants' recommendations, grades and stories they share highlight their abilities"

**This is the only relative weighting found anywhere, and it is qualitative.** No source reconciles
"greatest weight to the Research Report" with the four unweighted areas in §1.1. **NO SOURCE** for any
numeric weight.

### 1.3 What evaluators receive and how much time they have (PROCESS)

Evaluator recruitment page, `https://www.societyforscience.org/regeneron-sts/eval/`:

> "Each entry is read by at least three PhD-level Evaluators, sometimes more if additional scientific
> expertise is needed."
> "Evaluators are asked to consider each entrant's original research paper, personal essays, activities
> and transcripts."
> "Evaluators will receive a rubric, training video and materials and sample entries to help calibrate."
> "A training webinar is offered to share application insights and review strategies."
> "Evaluators are assigned approximately 40-60 entries."
> "Application packages can be quite long, up to 75 pages."
> "The time commitment is approximately 20-30 hours for a new Evaluator."
> "Evaluators must review applications without the use of AI."
> "Evaluators should consider all aspects of the application, student's activities how they spend their
> time, what resources are at their disposal, their academic achievements and more."

**Derived, not stated:** 20-30 hours across 40-60 entries is **20 to 45 minutes per entry** for a new
evaluator, for packages of up to 75 pages. This is my arithmetic. The page does not say time is spread
evenly, and it does not cover returning evaluators.

**The rubric exists and is not public.** Its content, and the training webinar's content: **NO SOURCE.**

### 1.4 What the application forms say they use each answer for (RULE / PROCESS)

Application Questions 2027 (preview; "some questions and word counts could vary slightly"):

- **Task 6 Q11:** "It is important to be honest about your contribution. **Context helps us understand and
  score your entry.** We understand that students often face limitations when it comes to freedom of
  selecting a research question, operating certain types of equipment, etc." It also asks:
  "Approximately what % of the Research Report you are submitting is work conducted and conceived of by
  you vs. others in the lab?"
- **Task 6 Q12, "What Did You Do?":** six boxes of 200 words each: purpose, designing procedures,
  implementing, gathering/recording data, analyzing data, formulating conclusions. "**NOTE: This is the
  bulk of the application** where you can tell us what you did, explain your thought process and more!
  Elaborate beyond your research paper."
- **Task 6 Q9:** "Was the project assigned to you? What % credit can you take for the idea?" (250 words)
- **Task 6 Q13:** "What didn't you do? Describe any important aspects of your project that you did not
  personally conduct." (150 words)
- **Task 6 Q4:** "Should an expert in Artificial Intelligence also review your entry?"
- **Task 6 Q16:** "We only recommend submitting published research papers if the entrant is the first or
  sole author of the paper, and if a mentor will attest that the bulk of this work can be attributed to
  you. Otherwise, submitting group work conducted with adults can confuse evaluators…"
- **Task 5 preamble:** "Your disclosure allows our evaluators and judges to assess your contributions to the
  research project, understand why your research might look similar to another entrant/parent/adult, and
  helps tell your story."
- **Task 5 Q5:** "**Entrants who have a paid relationship that is not disclosed will be disqualified.** All
  options below are permitted and very common." Q5a asks for "total cost, name of program, etc."
- **Task 5 Q7:** "Is there any reason your Research Report might get flagged in a plagiarism or AI detector?"
  (150 words)
- **Task 5 Q8-Q9:** "Select all of the ways AI tools were utilized in your STS research project **and/or
  application process**. Entrants are expected to draft their own Research Reports and application
  responses without AI." Q9 asks for the specific tools and how they were used (200 words).
- **Task 9 intro:** "for many successful entrants each year, the research they submit to Regeneron STS is
  their first project!" (ASSERTS; no count given.)
- **Task 9 Q3:** list "any conferences in which you have presented your work or plan to present your work in
  the next 3 months". **Q4:** list peer-reviewed publications, "List the name(s) of any coauthor(s)", and
  check the box if related to the STS research.
- **Task 10 Q2:** "we prefer that you think beyond your research project in this essay. **Our word count is
  shorter, as we care more about your story than the prose.**"
- **Task 12:** "If you choose not to share your test scores, this decision will not be held against you."

### 1.5 The recommendation forms (RULE; how they are scored is NO SOURCE)

Rules Appendices 5-7, printed pp. 35-40:

- **Types:** Educator Recommendation (up to 2); Project Recommendation (up to 2; "Each applicant must
  request one Project Recommendation, but may request two"); High School Report (counselor uploads the
  transcript). All are **due at the student deadline, November 5, 2026, 8:00 pm ET. "No exceptions can be
  made."**
- "**Recommenders should not use AI tools to draft recommendations.** … it is against STS Rules for any
  outside parties to provide edits." Entry-rules section 6h: "No persons should edit or draft a Regeneron
  STS recommendation besides the actual requested recommender."
- **Educator form Q8:** rank Independence, Creativity, Problem-Solving Abilities and Leadership Potential
  (Top 1% … Top 50%). "**Rankings are NOT used to cull applicants.**" **Q2:** "Have any of your former
  students entered and/or won awards in the Science Talent Search?" **Q7:** the teacher's knowledge of
  the project, and "Can you attest that the application and research project submitted in this
  application properly reflect the student's contribution?"
- **Project form Q2:** "Were you paid for your services as a mentor or coach to this student, and/or did you
  work with this student through a program that charges tuition or fees? … If yes, describe and explain
  the fees/tuition."
- **Project form Q7:** "How did the student get the idea for the project? … Was the project assigned; picked
  from a list of possible research topics; result from discussion with a scientist; arise from work in
  which the student was engaged; suggested by student?"
- **Project form Q11:** "For what aspects of the research can you give credit to the student as being their
  own unique contribution: Research Question, Procedural Design, Data Collection, Data Analysis, Drawing
  Conclusions (200 words each). **We want to know exactly what the student did.**"
- **Project form Q13:** "Were they creative in their science, or creative for a high school student?"
  **Q14:** "would you hire this student again … How do they rank against other students you have worked
  with in the past?"

Press releases say scholars' promise is "demonstrated through" research projects, essays and
recommendations (§1.6). **No source says how recommendations are weighted.**

### 1.6 Stated criteria in announcements (PROMO)

Verbatim on the 2025 and 2026 scholar press releases and scholar pages (workflow, vote 3-0):
`https://www.societyforscience.org/press-release/regeneron-sts-2026-scholars/`,
`https://www.societyforscience.org/regeneron-sts/2026-scholars/`,
`https://www.societyforscience.org/press-release/300-teen-scientists-selected-as-regeneron-sts-2025-scholars/`,
`https://www.societyforscience.org/regeneron-sts/2025-scholars/`:

> "Scholars were chosen based on their outstanding research, leadership skills, community involvement,
> commitment to academics, creativity in asking scientific questions and exceptional promise as STEM
> leaders demonstrated through the submission of their original, independent research projects, essays
> and recommendations."

2026 finalists page, `https://www.societyforscience.org/regeneron-sts/2026-finalists/`, for **finalists**:
"selected from 300 scholars and 2,612 entrants … based on the originality and creativity of their
scientific research, as well as their achievement and leadership both inside and outside of the classroom."

### 1.7 Advice the Society gives entrants (PROCESS / ASSERTS)

Rules p.11, "Top 10 ways", which the tips blog repeats (Kevin Easterly, 2024-11-04,
`https://www.societyforscience.org/blog/regeneron-sts-application-tips/`):

> "Don't overthink the essays! Feeling stuck? Remember that done is better than perfect!"
> "Pay attention to word counts. You don't need to max out every word count, but take note of sections
> where you're encouraged to explain your process in detail. Give us all the information we need to
> accurately assess what you did and how you did it."
> "Give us context. Regeneron STS is a holistic competition; it's not just about the research."
> "Request your recommendations ASAP. … all three recommendation types require adults to answer
> questions in our system and are NOT traditional form letters."
> "BONUS TIP: Context also means being honest about the support you've received. … it's fine to pay to
> attend a research program or have received guidance or connections from a relative, but it's important
> that those connections are credited and clear. Err on the side of sharing more information about who
> and what has helped you along the way, not less!"

### 1.8 What fails an entry before it is scored (RULE + DATA)

Rules Appendix 14, "Common reasons projects fail to qualify", describing **2026**:

> "Top 3 Reasons Projects Failed to Qualify in 2026: 1 Fake references and/or citations in Research
> Report; 2 Failure to disclose a conflict of interest; 3 Vertebrate animal research conducted in a home
> environment."

The "Other" items that could apply to this project, verbatim:

> "Student's research report fails plagiarism screening." / "Student and mentor discrepancy in paid program
> sum." / "Student fails to disclose personal relationships in the mentorship of their project, or other
> conflict of interest." / "Student or mentor fails to disclose payment for services." / "Research Report
> exceeds 20-page limit, or attempts to deceive the spirit of the page limit." / "Research Report contains
> false references, fraudulent data, etc." / "Any aspect of the application is refuted with evidence." /
> "Unrefuted AI use in application responses."

Entry Rule 8: "Students may not use generative Artificial Intelligence (AI) to write Regeneron STS
application questions, draft the Research Report or generate citations. Students are responsible for
personally drafting all responses to application questions."

Entry Rule 9: "Students are responsible for ensuring all information in the application and research
report is accurate, from personal facts and project data to research report references."

Entry Rule 12: "The Society understands that entrant papers often resemble their mentors' research papers.
This is one reason students are provided the opportunity to mention similar work and the level of their
participation in published work of the lab."

Appendix 4 (the AI usage chart; the full 13 rows are already in `notes/sts-constraints.yaml`). Rows that
bear on this project:

> "Use generative AI to initially write the research plan, abstract, paper or poster. — No — Never
> acceptable. This must be the independent work of the student. Guidance or refinement after the initial
> document has been completed can be done with explicit citation and a log."
> "Use AI to write initial code for your project — Yes — Acceptable, only with explicit citation stating
> which portions of the code were AI generated and with a log of the prompts."
> "You write an abstract. Ask AI to sharpen the language but not modify, add to, or replace the main
> points — Yes — Acceptable use without explicit citation only if changes suggested by AI are minor and
> limited to grammar and syntax. Must be credited."

### 1.9 NO SOURCE

- Rubric content, point values, or weights for the four areas. **NO SOURCE** (the rubric exists; §1.3).
- How recommendations, essays, activities or test scores are weighted. **NO SOURCE.**
- Any evaluator or judge statement on what distinguishes a scholar from a non-scholar. **NO SOURCE.**
- Webinar transcripts. **NO SOURCE.** The Rules (p.11) and the evaluator page refer to webinars; no
  transcript was found.
- Alumni interviews stating selection criteria. **NO SOURCE.** The only alumni text found is a
  testimonial in the Rules (p.29), which states no criteria.
- How disclosed AI use or paid support changes a score, as opposed to eligibility. **NO SOURCE.**

---

## 2. PART 2: WHAT IS OBSERVABLE ABOUT SCHOLARS, NOT FINALISTS

**Bottom line first:** no public data compares scholars with non-scholars on any attribute of the
application. The published scholar list has only a few fields. Nothing below separates scholars from
non-scholars, and nothing is extrapolated down from the finalists.

### 2.1 Society aggregates (DATA)

| cycle | entrants | entrant schools | scholars | scholar schools | derived |
|---|---|---|---|---|---|
| 2026 | "over 2,600" (release); **2,612** (finalists page) | 826 | 300 | 203, "in 34 states, Washington, D.C. and China" | 300/2,612 = 11.5% of entrants; 203/826 = 24.6% of entrant schools |
| 2025 | "nearly 2,500" (release); **2,471** (top-40 blog) | 795 | 300 | 200 | 300/2,471 = 12.1%; 200/795 = 25.2% |

Sources: 2026 scholars press release, 2026 Fast Facts blog
(`https://www.societyforscience.org/blog/regeneron-sts-2026-scholar-fast-facts/`), 2026 finalists page,
2025 scholars press release, 2025 top-40 blog
(`https://www.societyforscience.org/blog/regeneron-sts-top-40-finalists-2025/`) (workflow, vote 3-0; the
2,612 figure read directly). **The ratios are my arithmetic. The Society does not print them.**

### 2.2 What the Scholar Book contains (DATA, my tally)

**Fields per scholar:** city, school, surname and given name, age, project title. **Not present:**
category, mentor, lab or institution, publications, prior competitions, demographics. **That limits what
anyone can observe about the 260.**

Parsed from the 2026 Scholar Book (sha256 above) into 300 rows. Each of the 40 finalists on the 2026
finalists page was matched to a row by name (40 of 40 matched), leaving **260 non-finalist scholars**.

| quantity | all 300 | 260 non-finalists | 40 finalists |
|---|---|---|---|
| location groups (states + D.C. + China) | 36 (published figure: 34 + D.C. + China = 36, **matches**) | | |
| distinct schools (school+state key) | 202 (published: 203, **off by one**; my key would merge two same-name schools in one state, **unresolved**) | 180 | 35 (published: 35, **matches**) |
| schools with 2+ scholars | 55, holding 153 of 300 scholars | 132 of 260 come from such schools | |
| New York / California / New Jersey / Texas | 76 / 55 / 18 / 18 | | |
| Pennsylvania | 5 | 2 | 3 |
| largest single-school counts | Jericho SHS (NY) 10; Thomas Jefferson HSST (VA) 8; Harker, Bergen County Academies, Bronx Science, NCSSM 5 each | | |
| ages | 16: 4; 17: 148; 18: 144; 19: 4 | | |

**Title keywords** (case-insensitive regex over titles, not hand-coded, descriptive only):

| pattern | 260 non-finalists | 40 finalists |
|---|---|---|
| ML/AI terms (machine learning, deep learning, neural, AI, transformer, reinforcement learning, language model, convolutional) | 55 | 6 |
| the word "Novel" | 49 | 9 |
| "conformal" in the sense of conformal **prediction** | 1 (a Pennsylvania non-finalist scholar; sepsis diagnosis) | 0 |
| power grid / contingency / power system | 0 | 0 |

**Why none of this separates scholars from non-scholars.** There is no entrant-side base rate for any of
these features, so their frequency among scholars says nothing about selection. A title is not a project.
The finalist-versus-non-finalist differences rest on 40 titles and are not interpreted.

**School concentration is DEMONSTRATED; its cause is not.** It could reflect research programs, entrant
volume per school, teacher experience, or selection. No source separates those, so this file takes no
position.

**Your school.** Conestoga High School (Berwyn) does **not** appear in the 2026 book. It appears **once** in
the 2025 book (one 2025 scholar). This bears on Educator form Q2 ("Have any of your former students
entered and/or won awards…") and Q3 (school research culture). **No source links a school's track record
to selection.**

### 2.3 Coverage of non-finalist scholars (NO USABLE SOURCE)

The workflow found school and local announcements (Long Island Press, Stony Brook University news, Roslyn
School District), a PrepScholar post, and consultancy blogs (Polygence, Create & Learn). **No claim from
them survived three-vote verification** as evidence of what scholars share. The announcements list names
and titles; the blogs only **assert**, for example that the rubric is confidential. **NO SOURCE**
characterizes non-finalist scholars by mentorship, publications, ISEF history, or independence.

---

## 3. PART 3: YOUR FILE AGAINST WHAT WAS FOUND

**What the comparison can and cannot do.** The Society publishes criteria, not the scholar cut-line.
Every "above" or "below" below is **relative to what the Society says it looks for**, never relative to
scholars, because no scholar profile is public (§2). **Whether the file clears the cut is not knowable
from any source.**

### 3.0 Eligibility screen (binary; applies before any scoring)

This comes first because §1.1 puts the "completeness, accuracy, eligibility and rules adherence" review
ahead of evaluation, and Appendix 14 lists specific failures.

| # | item | evidence in repo / file | status | label |
|---|---|---|---|---|
| E-1 | **Paid program disclosed, with a sum matching the mentor's** | `CLAUDE.local.md` and `notes/sts-constraints.yaml:456` record that BU RISE was paid. **No fee total is recorded anywhere in the repo** (grep for "fee", "tuition", "paid"). Project form Q2 asks the mentor to "explain the fees/tuition"; Appendix 14 lists "Student and mentor discrepancy in paid program sum." | **OPEN**, and cheap to close | GROUNDED |
| E-2 | **AI disclosure covers the project and the application process** | `notes/ai-prompt-log.md` is 5,589 lines and meets the Appendix 4 logbook condition. **But:** (a) the STS report's Acknowledgments (`report/paper_current_STS.tex:353`) now contains **no AI statement and no paid-program statement**. Erratum E3's sentence was removed, not replaced. (b) `notes/contribution-log.md` (entry 2026-07-21) records an **agent-drafted five-page IEEE-style reference paper** (`notes/1_research_draft*.txt`) that predates your drafting. Whether that falls under the Appendix 4 row "Use generative AI to initially write the … paper … Never acceptable" is **not settled by any source I found**. (c) Task 5 Q8 covers the "application process", so **this research session is disclosable AI use in the application process**. | **OPEN**. Item (b) is the highest-consequence unresolved question in the file. | GROUNDED (the rules and the facts); INFERRED (that (b) is ambiguous) |
| E-3 | **Report text versus the co-authored URTC paper** | The STS report is sole-authored. The URTC version (`paper_current_URTC_20260808.tex:48-55`) lists Rajan Saha and Eugene Pinsky and shares text and figures. URTC 2026 runs **Oct 9-11, 2026** (`https://ieeeboston.org/events/2026-undergraduate-research-technology-conference-urtc/`), inside Task 9 Q3's "next 3 months" window. Entry Rule 12 plus Task 5 Q7 give a place to explain the overlap. Guidelines rule 6: "acknowledge the published paper in your application." | **OPEN** until declared in Task 5 Q7 and Task 9 Q3-Q4 | GROUNDED |
| E-4 | **Every factual claim in the activities list is true on Nov 5** | Activities #1 says the URTC paper was "accepted **and presented** to MIT faculty". The presentation is Oct 9-11, so this is **not true as of 2026-09-14**; it becomes true only if it happens. It also says the Anacodic paper was "**published** in Advances in Carbon Neutrality (MDPI)", while your prompt says only "two further papers" and gives no status; **verify the DOI**. It says "Selected for the BU RISE Data Science Practicum (**~5% acceptance**)"; **no source for 5% is in the repo**. "Two first-author papers" is consistent with the URTC author order and your prompt. | **VERIFY before submit** | GROUNDED (Entry Rule 9; Appendix 14 "refuted with evidence"); the specific mismatches are read from the files |
| E-5 | **Report format** | Floats cited (C10, resolved). Links appear only inside `thebibliography` (`:382`), which complies. **No `\pagestyle` or footer command** in the `.tex`, so `article` defaults to bottom-centre page numbers; Guidelines rule 5c requires "bottom right corner, starting after the abstract". **Check the rendered PDF.** Also required: ≤4 MB; filename "LASTNAME.FIRSTNAME.ZIPCODE"; a separate bibliography-only PDF with no name (Task 6 Q19). | **OPEN** (page numbers); unmeasured (size) | GROUNDED |
| E-6 | **Activities form options match the 2027 form** | The draft's science-competition checklist uses options not in the 2027 preview ("Regeneron ISEF Finalist", "Broadcom MASTERS / Thermo Fisher JIC"). The 2027 list includes "**Science training program or summer institute**", which describes BU RISE, but nothing is checked. | cosmetic, and accuracy | GROUNDED |

### 3.1 Research Report and Scientific Merit (the "greatest weight" area, FAQ)

| aspect | your evidence | vs. what the Society describes | label |
|---|---|---|---|
| Eligible report type | Completed research with results; ~15 pp against a 20-page limit | **Meets** Task 8 ("Papers that only outline a review … or detail a plan … are not eligible"). | GROUNDED |
| Authorship clarity | Sole-authored STS version; the group/co-authored version is kept separate | **Matches** the recommended practice exactly (Guidelines rule 6; Task 6 Q16: "Please consider drafting a version of the paper that highlights your own contributions"). | GROUNDED |
| Reviewer match | Category "Engineering"; the method is conformal ML. Task 6 Q4 offers an AI-expert review; Appendix 1 says the category "will determine the expertise of the initial review only". | **Decision not yet made.** Which choice helps: **NO SOURCE**. | GROUNDED (mechanism); INFERRED (that it matters) |
| Scientific content | Pre-registered predictions including failures; a sealed cross-network negative; ≥5 seeds with error bars; a limit, not a magnitude, as the headline; one network; the gate ties `static_severity` (finalist analysis §3.4-§3.6, R7) | The Society publishes no merit rubric. **I cannot place this relative to scholars.** The evaluator page asks for review "in the appropriate scientific discipline"; how a power-systems reviewer weighs a limit-type headline is **unknown**. | INFERRED |
| Reading time | A report plus up to 75 pages of application | **Derived:** 20-45 minutes per entry for a new evaluator (§1.3). INFERRED consequence: the abstract, the first figure and Task 6 Q5 (the 200-word layperson summary) carry disproportionate load. | GROUNDED (the hours); INFERRED (the consequence) |

### 3.2 Student Contribution to the Research (a scored area, collected four times)

**This is the area where published evidence is most specific.** Contribution is checked at eligibility
("independent and original work"), named as an evaluation area, asked in Task 6 Q9, Q11, Q12 and Q13,
and asked separately of the Project Recommender (Q7, Q11, Q12). (§1.1, §1.4, §1.5; workflow, vote 3-0.)

| aspect | your evidence | assessment | label |
|---|---|---|---|
| Report authorship | Sole author | **Above** what Task 6 Q16 describes as the problem case (group papers that "confuse evaluators"). | GROUNDED |
| Program context | Paid BU RISE practicum; instructors Kalita and Pinsky and TFs; URTC co-author Pinsky | Permitted ("All options below are permitted and very common", Task 5 Q5), but it **must be delineated** (Rules section 6g: "Entrant and mentor should take care to delineate the student contribution to the project vs. the work of the lab"). | GROUNDED |
| Origin of the idea | **Not recorded in the repo** in a form I can cite. Project form Q7 asks whether it was "assigned; picked from a list …; suggested by student". | **Unknown.** Your Task 6 Q9 "% credit for the idea" and the recommender's Q7 answer are read side by side, and you cannot see the recommendation. **A mismatch would be visible to evaluators.** No source says how a mismatch is treated, except the payment-sum rule (E-1). | GROUNDED (both questions exist); INFERRED (visibility) |
| AI toolchain in the implementation | Extensive agent-executed code, experiments and verification recorded in `notes/ai-prompt-log.md` | Task 6 Q12 "Implementing the procedure" and Q13 "What didn't you do?" must reflect this. Appendix 4 requires "explicit citation stating which portions of the code were AI generated". **This narrows what the Implementing box can claim; it does not remove the other five boxes.** | GROUNDED (the rules); INFERRED (the narrowing) |
| Where you are strong | Research question framing, pre-registration, the decision to report negative results, analysis design, the claim ceiling. These are what Q12 "Designing", "Analyzing" and "Formulating conclusions" ask for, and they are documented by date in `notes/preregistration.md` and the prompt log. | **Above** what the forms ask for, **if the answers make it visible.** The report alone cannot, because Task 6 Q12 says "Elaborate beyond your research paper". | GROUNDED (the forms); INFERRED (strength) |

### 3.3 Academic Aptitude and Achievement

| aspect | your evidence | assessment | label |
|---|---|---|---|
| Transcript | "Unblemished", five AP/honors in junior year, four AP 5s (OWNER-ASSERTED) | Transcript is **required** via the High School Report. **No academic threshold is published**, and no scholar academic profile is public. **Above or below: not determinable.** | GROUNDED (required); NO SOURCE (threshold) |
| SAT 1530, single sitting | OWNER-ASSERTED | Optional (Task 12). "will not be held against you" if omitted. Superscoring is permitted, so "single sitting" is not a distinction the form records. | GROUNDED |
| Coursework | Task 3 Q6: current classes (up to eight) | Required field; no weight published. | GROUNDED |

### 3.4 Overall Potential as a Future Leader of the Scientific Community

| aspect | your evidence (OWNER-ASSERTED, activities draft) | assessment | label |
|---|---|---|---|
| Leadership, general | Co-Editor-in-Chief (45 staff, 7 issues/yr); two service-club officer roles (50+ and 40 members; $1,000+ raised); DECA ICDC top-10 individual of 353; NovaPlan founder (50+ users) | "Leadership skills, community involvement" are named (PROMO, §1.6), and the four areas name "Future Leader". **Documented breadth is clearly present.** Relative standing: **NO SOURCE**. | GROUNDED (named criteria); INFERRED (breadth) |
| STEM-specific leadership or initiative | NovaPlan (self-built software); Anacodic research (a second research line, 170 h); no STEM club, outreach or teaching role listed | Task 10 Q1 asks for "scientific aptitude, leadership, curiosity, inventiveness and/or initiative" and "other STEM-related interests besides your project". **Your STEM initiative evidence is the two research lines and NovaPlan.** No STEM-community leadership role is listed. **Whether that matters: NO SOURCE.** I do not extrapolate from finalist bios. | GROUNDED (the question); INFERRED (gap) |
| Prior research and competitions | No science fair, ISEF, or prior STS-type competition | Task 9: "for many successful entrants each year, the research they submit to Regeneron STS is their first project!" (ASSERTS; no count). **No source says prior competitions are required or weighted.** | GROUNDED |
| Publications and dissemination | URTC accepted (conference Oct 9-11); Anacodic papers (status per E-4) | Collected in Task 9 Q3-Q4. **Publication as a scoring input: NO SOURCE.** The forms discuss publication only for its effect on judging contribution. | GROUNDED |
| Recommender rankings | Unknown (confidential) | Educator Q8 rankings are "NOT used to cull applicants" (PROCESS). Their other uses: NO SOURCE. | GROUNDED |
| Context and resources | Paid selective program; university-affiliated lab access | "Evaluators consider student circumstances and access to labs" (§1.1). **Direction of the adjustment: NO SOURCE.** Rules p.11: "it's fine to pay to attend a research program". | GROUNDED (the statement); NO SOURCE (direction) |

### 3.5 Summary of Part 3

- **Above what the Society describes:** sole authorship of the report (§3.2) and a separate report
  version that matches the recommended practice exactly (§3.1). Both are GROUNDED.
- **Plainly open, and each is a rule, not a preference:** paid-program sum (E-1), the AI disclosure
  scope including the agent-drafted reference draft (E-2), declaring the URTC overlap (E-3), activities
  claims that are not yet true or not yet sourced (E-4), page-number position (E-5). All GROUNDED.
- **Unwritten, and the Society names it "the bulk of the application":** Task 6 Q12. GROUNDED.
- **Not determinable from any source:** academic standing relative to scholars, leadership relative to
  scholars, and scientific merit relative to scholars.

---

## 4. PART 4: RANKED PLAN, 2026-09-14 TO 2026-11-05

**Window:** 52 days. **Hard dates** (Rules p.5): customer support closes **Wed Nov 4, 8:00 pm ET**;
application **and all recommendations** close **Thu Nov 5, 8:00 pm ET**. URTC is Oct 9-11 (lost time).

**How items are ranked (INFERRED).** Effect per hour cannot be measured. The ranking uses an ordering the
sources support. First come items whose failure is binary and total under a cited rule (disqualification
or incomplete application) and cost few hours. Next come items the Society's own text singles out as
heavily used ("bulk of the application", "greatest weight"). Then the remaining required tasks, then
optional ones. Hour estimates are mine (INFERRED).

**Every item marked "you write" must be written by you without AI (Entry Rule 8).** This file contains no
application text.

### Rank 1: Recommendations: confirm all four are live, and reconcile facts the recommender will report
- **What.** For each of the four open requests, confirm: the request was sent through the portal to the
  address the recommender prefers; the recommender has opened it; they know the deadline is **the same
  Nov 5, 8:00 pm ET** with "No exceptions". Set a personal target with each (for example Oct 22), and
  send a reminder schedule. **Confirm at least one is a Project Recommendation** from "the person closest to
  the student's research", often a TF rather than the program head. **Confirm the High School Report
  (transcript) request goes to the counselor**, if it is not already one of the four. **Give the Project
  Recommender the facts they will be asked for:** program fee total and who paid, dates (Q8), and your
  paper and URTC status. **Do not draft or edit their text.**
- **Hours.** 1.5-2 now; 15 minutes per week afterwards.
- **Evidence.** Rules p.5 (deadline includes recommendations); Appendix 5 ("Applicants must request the
  following recommendations"; "Each applicant must request one Project Recommendation"); Appendix 7 Q2 and
  Q8; section 6h (no outside edits); Appendix 14 ("Student and mentor discrepancy in paid program sum").
  GROUNDED.
- **If skipped.** A required recommendation missing at 8:00 pm Nov 5 cannot be accepted "for any reason".
  A fee mismatch is a listed fail-to-qualify reason. **This is the only item on the list whose outcome
  depends on other people's calendars, which is why it ranks above work that is entirely yours.**

### Rank 2: Resolve the AI-disclosure scope, and email STS about the one ambiguous case
- **What.**
  - **(a)** Build a factual inventory from `notes/ai-prompt-log.md` and `notes/contribution-log.md`, mapped
    to the Task 5 Q8 checkboxes: Writing Code; Data Analysis; Literature Search; Bibliography Support;
    Editing/Refining Research Report; Project Ideation; Other (application-process research, including this
    file). Record which code portions were AI-generated (Appendix 4 code row).
  - **(b)** Put the agent-drafted reference paper (`notes/contribution-log.md`, 2026-07-21) to STS as a
    **factual question** at `sts@societyforscience.org`: what it was, that it was never submitted, and how
    the submitted report was written. **Send it early**, so the answer arrives well before the Nov 4
    support deadline. **You write the email.**
  - **(c)** Then **you write** Task 5 Q6 (200 words), Q7 (150), Q9 (200), and the fee description Q5a.
- **Hours.** (a) 3-4; (b) 1; (c) 3-4. Total 7-9.
- **Evidence.** Task 5 Q5, Q7-Q9; Entry Rules 8 and 10; Appendix 4; Appendix 14 ("Unrefuted AI use in
  application responses", "Student or mentor fails to disclose payment for services"); Rules p.11 bonus
  tip ("Err on the side of sharing more information … not less!"). GROUNDED.
- **If skipped.** Undisclosed paid support: "will be disqualified" (Task 5 Q5). An AI question that
  surfaces later ("Any aspect of the application is refuted with evidence") is a listed failure. **The
  ambiguity in (b) does not resolve itself by silence**, and the Society invites the question (Rules
  Appendix 14 intro).

### Rank 3: Task 6 Q12, "What Did You Do?" (six boxes, 1,200 words), with Q9, Q11 and Q13
- **What. You write** the six 200-word boxes, plus Q9 (idea origin and % credit, 250), Q11 (independence
  and % of report, 150) and Q13 (what you did not do, 150). **Sequence:**
  - Do Q13 first. It forces the honest boundary: the AI-executed implementation, the course framework,
    anything the instructors or TFs supplied.
  - Then the six boxes, each attributing support ("Attribute the support you received in each area … and
    highlight what you claim as your own").
  - **Mapping to the recommender's form**, which you will never see: your Purpose ↔ their Research
    Question; Designing ↔ Procedural Design; Gathering/Recording ↔ Data Collection; Analyzing ↔ Data
    Analysis; Formulating conclusions ↔ Drawing Conclusions. **"Implementing" has no counterpart on their
    form**, so it is the one box only you describe.
  - Draw dated evidence from `notes/preregistration.md` and the prompt log. **Facts only; the words are yours.**
- **Hours.** 10-14.
- **Evidence.** Task 6 Q12 ("This is the bulk of the application … Elaborate beyond your research paper");
  Q11 ("Context helps us understand and score your entry"); evaluation area "Student Contribution to the
  Research" (Rules p.12); Project form Q11 ("We want to know exactly what the student did"). GROUNDED.
- **If skipped or thin.** The required task is incomplete, or contribution is judged from the report and
  a recommendation you cannot see. **This is the single largest text block that the Society explicitly
  says it uses, and it is the area (§3.2) where your sole authorship can actually be shown.**

### Rank 4: Report compliance pass (no new content)
- **What.**
  - Page numbers bottom-right, starting after the abstract (rule 5c); check the rendered PDF, since the
    `.tex` sets no footer.
  - PDF ≤4 MB. File named `LASTNAME.FIRSTNAME.ZIPCODE`. Not image-scanned.
  - A separate bibliography-only PDF with no name (Task 6 Q19).
  - Acknowledgments: **you write** the paid-program and AI disclosure. Currently absent at `:353`.
  - Re-run the existing citation gate (`scripts/check_citations.py`), because fake references are the #1
    2026 fail reason.
  - The finalist analysis's R2 (superseded case30 numbers in the abstract) was **not re-checked here**;
    confirm its status.
- **Hours.** 2-3, excluding the owner-written acknowledgment.
- **Evidence.** Research Report Guidelines rules 2, 4, 5 and "full disclosure of any research or person that
  has influenced the applicant's work is required"; Task 8; Appendix 14 top-3. GROUNDED.
- **If skipped.** Format breaches are rule violations; a fake reference is disqualification. The report
  carries "greatest weight" (FAQ).

### Rank 5: Declarations of related work (Task 9 Q3-Q4) and the plagiarism explanation (Task 5 Q7)
- **What.** List URTC (accepted; presentation Oct 9-11; co-author Eugene Pinsky; check "related to STS
  research"). List both Anacodic papers **with their exact status** (published, accepted or submitted),
  co-authors, and whether they are related (they are a different project). **You write** the Task 5 Q7
  explanation of text overlap with the URTC paper.
- **Hours.** 1-2.
- **Evidence.** Guidelines rule 6 ("acknowledge the published paper in your application"); Entry Rule 12;
  Task 9 Q3-Q4; Task 5 Q7. GROUNDED.
- **If skipped.** The report "fails plagiarism screening" against a co-authored paper that was never
  declared (Appendix 14), and contribution becomes ambiguous (Task 6 Q16).

### Rank 6: Activities fact-check and form alignment (Task 11)
- **What.**
  - Change nothing that is true, and fix what is not yet true or not sourced (E-4): the "presented" timing,
    the MDPI status and DOI, the "~5%" figure.
  - Re-check every hour figure against the stated weekly rates.
  - Select "Science training program or summer institute" for BU RISE (E-6).
  - Fill Task 11 Q6 Awards (optional, 250 words) and Q7 Interests (75 words).
  - **You make every edit.**
- **Hours.** 1.5-2.
- **Evidence.** Entry Rule 9; Appendix 14 ("Any aspect of the application is refuted with evidence"); the
  Application Questions Task 11 option list. GROUNDED.
- **If skipped.** A claim false on the submission date is exactly what that fail reason names.

### Rank 7: Task 10 essays (two × 200 words)
- **What. You write** Q1 (potential as a scientist or engineer: concrete examples, other STEM interests,
  plans, ten years out) and Q2 (one Common App prompt; the Society prefers you "think beyond your research
  project").
- **Hours.** 6-8.
- **Evidence.** Task 10 text; the press-release criteria name essays as where promise is "demonstrated"
  (PROMO); the evaluator page lists "personal essays" (PROCESS). **Weight: NO SOURCE.** Ranked **below**
  Task 6 Q12 on the Society's own signals: "Don't overthink the essays!" and "we care more about your
  story than the prose" (Rules p.11; Task 10 Q2) set against "This is the bulk of the application" (Task 6
  Q12). That ordering is GROUNDED in the wording and INFERRED as a priority.
- **If skipped.** A required task is incomplete. The "Future Leader" area loses its only first-person
  evidence.

### Rank 8: The rest of Task 6 (Q1, Q4, Q5, Q10, Q14, Q15, Q16)
- **What.**
  - Decide the category (Engineering vs. Computer Science) and Q4 (AI-expert review).
  - **You write** Q5, the layperson summary (200 words; "will aid readers, including evaluators"); Q10,
    duration (75); Q14, limitations (200); Q15, benefits (200).
  - Q16: answer "not published" for the STS report itself; URTC goes in Task 9.
  - Dates in Q10 must match the Rules Wizard Part I dates and Project form Q8.
- **Hours.** 4-5.
- **Evidence.** Task 6 text; Appendix 1. GROUNDED. The Q5 load under a 20-45 minute read is INFERRED (§3.1).
- **If skipped.** Required fields are incomplete. The category choice sets the "expertise of the initial
  review".

### Rank 9: Tasks 1-3, 7 (Rules Wizard) and 12 (test scores)
- **What.**
  - Eligibility, demographics, school information (Task 3 includes a newspaper contact).
  - Rules Wizard Part I dates (brainstorm start, data start/end, data source, RRI supervision). No human,
    animal or PHBA work, so few branches.
  - Task 12: upload SAT/AP evidence (optional).
- **Hours.** 2-3.
- **Evidence.** Rules p.11 ("Complete Tasks 1, 2, 3 and 4 first … 20% of your application is already
  done!"); Application Questions Tasks 1-3, 7, 12. GROUNDED.
- **If skipped.** Tasks 1-3 and 7 are required. Task 12 is optional, "not held against you".

### Rank 10: Submission buffer
- **What.** Full application submitted by **Tue Nov 3**. Download your full application before the deadline
  ("You will not be able to download your application once the deadline has passed"). Confirm all
  recommendations show as submitted by Nov 3.
- **Hours.** 1.
- **Evidence.** Rules p.5 (the support guarantee applies only to requests by Nov 4, 8:00 pm ET);
  Application Questions instruction 5. GROUNDED.
- **If skipped.** A portal problem after Nov 4, 8:00 pm has no guaranteed fix.

### 4.1 Totals and a week-by-week layout (INFERRED)

**Estimated total: ~37-50 hours** across 7.4 weeks, about 5-7 hours per week. URTC week is light.

| week | dates | items |
|---|---|---|
| 1 | Sep 14-20 | Rank 1 (all four recommenders + fee facts); Rank 2(a) inventory; Rank 2(b) email to STS; Rank 9 Tasks 1-3 |
| 2 | Sep 21-27 | Rank 3: Q13, then the six Q12 boxes (first full version) |
| 3 | Sep 28-Oct 4 | Rank 3: Q9, Q11, revise Q12; Rank 2(c) Task 5 text once the STS reply is in |
| 4 | Oct 5-11 | **URTC Oct 9-11**; Rank 5 declarations; Rank 6 activities fact-check (update "presented" only after it happens) |
| 5 | Oct 12-18 | Rank 7 essays |
| 6 | Oct 19-25 | Rank 8 remaining Task 6; Rank 4 compliance pass; recommender check-in at your Oct 22 target |
| 7 | Oct 26-Nov 1 | Full read-through for consistency across Task 5, Task 6, Task 9, Task 11 and the report; Rank 9 Rules Wizard dates and Task 12 |
| — | Nov 2-3 | Rank 10: submit; download a copy; confirm recommendations received |

### 4.2 What is deliberately NOT on the plan
- **New experiments or analyses:** excluded by instruction, and no source indicates the report is ineligible
  or incomplete as it stands.
- **Rewriting the report's science:** the finalist analysis's R3, R6, R7 and R9 are INFERRED and already
  specified there. Nothing found here raises their priority above Ranks 1-8.
- **Chasing a science-fair or competition record before Nov 5:** Task 9 says first projects are common,
  and nothing after the deadline is considered (Rules p.12).

---

## 5. WHAT IS UNKNOWN

1. **The rubric's content and weights.** It exists (§1.3) and is not public. How "greatest weight to the
   Research Report" maps onto the four areas: **unknown**.
2. **Who the 2,312 non-scholars of 2026 were.** No attribute of any non-scholar application is public, so
   **no feature of your file can be shown to separate scholars from non-scholars.** §2 is descriptive only.
3. **What your recommenders will write**, including idea origin, % credit, and fee amounts. The forms are
   confidential (Appendix 5). Whether a student/recommender mismatch other than the fee sum affects
   scoring: **NO SOURCE**.
4. **How STS will classify the agent-drafted reference paper** under Appendix 4 (E-2). Answerable only by
   the Society.
5. **Direction of the context adjustment** for a paid, university-affiliated program ("Evaluators consider
   student circumstances and access to labs"): **NO SOURCE**.
6. **Whether publication status, prior competitions or school track record matter:** **NO SOURCE** (§2.3).
7. **Portal task numbering and word limits.** The preview "could vary slightly", and the two PDFs already
   disagree (C5).
8. **The one-school discrepancy** in my 2026 tally (202 vs 203), unresolved (§2.2).
9. **Your academic and activity facts** are OWNER-ASSERTED. The transcript, AP and SAT PDFs in
   `notes/files_for_STS_portal/` were **not opened** for this report.

---

## 6. SOURCE REGISTER (all fetched 2026-09-14)

| source | type | route | used in |
|---|---|---|---|
| `https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Official-Rules.pdf` | RULE / PROCESS / DATA | direct PDF | §1.1, §1.5, §1.7, §1.8, §3, §4 |
| `https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Application-Questions.pdf` | RULE | direct PDF | §1.4, §3, §4 |
| `https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Project-Rec.pdf` | RULE | workflow (same questions read directly in Rules Appendix 7) | §1.5 |
| `https://www.societyforscience.org/regeneron-sts/eval/` | PROCESS | fetch tool + workflow verifier | §1.3 |
| `https://www.societyforscience.org/regeneron-sts/frequently-asked-questions/` | PROCESS | fetch tool | §1.2 |
| `https://www.societyforscience.org/regeneron-sts/judging-and-awards/` | PROCESS | workflow (vote 3-0) | §0.3, §1.1 |
| `https://www.societyforscience.org/regeneron-sts/application-requirements/` | PROCESS | workflow (vote 3-0) | §1.1 |
| `https://www.societyforscience.org/blog/regeneron-sts-application-tips/` | ASSERTS (advice) | fetch tool | §1.7 |
| `https://www.societyforscience.org/press-release/regeneron-sts-2026-scholars/` | PROMO / DATA | workflow (vote 3-0) | §1.6, §2.1 |
| `https://www.societyforscience.org/regeneron-sts/2026-scholars/` | PROMO / DATA | workflow + fetch tool (PA count from tool WRONG; see §0.1) | §1.6 |
| `https://www.societyforscience.org/blog/regeneron-sts-2026-scholar-fast-facts/` | DATA | workflow (vote 3-0) | §2.1 |
| `https://www.societyforscience.org/press-release/300-teen-scientists-selected-as-regeneron-sts-2025-scholars/` | PROMO / DATA | workflow (vote 3-0) | §1.6, §2.1 |
| `https://www.societyforscience.org/regeneron-sts/2025-scholars/` | PROMO / DATA | workflow (vote 2-1 on page variant) | §1.6 |
| `https://www.societyforscience.org/blog/regeneron-sts-top-40-finalists-2025/` | DATA | workflow (vote 3-0) | §2.1 |
| `https://www.societyforscience.org/regeneron-sts/2026-finalists/` | DATA / PROMO | curl, read directly | §1.6, §2.1, §2.2 |
| `https://www.societyforscience.org/press-release/regeneron-sts-2026-top-40-finalists/` | PROMO / DATA | curl, read directly | §2.1 |
| `https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2026/Program-Books/Scholar.pdf` | DATA | direct PDF, parsed | §2.2 |
| `https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2025/Program-Books/Scholar.pdf` | DATA | direct PDF, PA section | §2.2 |
| `https://ieeeboston.org/events/2026-undergraduate-research-technology-conference-urtc/` | DATA (event dates) | fetch tool | §3.0 E-3, §4 |
| Long Island Press, Stony Brook news, Roslyn SD, PrepScholar, Polygence, Create & Learn | secondary / blog | workflow; **no claim survived verification** | §2.3 only |

**Refuted during verification (0-3):** "a second Project Recommendation is allowed *only if* the student
worked with more than one mentor." The verified rule is that one is required and two are allowed.
