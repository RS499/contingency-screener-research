# P-002 + P-012 (+ §8-1) — disclosure CHECKLIST

**This file is a checklist of facts and rules only.** It contains no disclosure text, no suggested
sentence, and no fragment to paste. How each fact is worded, and where it is placed, is the author's
decision (`CLAUDE.local.md` "Disclosure — how to present it"; ledger §5). Honesty is the default in every
borderline case.

## 1. Ledger ID(s) + severity
- **P-002** — FATAL (submission blocker until STS confirms a form field suffices; D11). No generative-AI
  disclosure anywhere in the report.
- **§8-1** — FATAL for the AI part (= P-002); MAJOR for program and people (STS-02, NS-01).
- **P-012** — MAJOR (D12: not FATAL — Saha is first author; the co-author is an adult, so R03's
  student-team ban is not triggered). URTC paper + co-author not acknowledged; .tex header says the body
  is verbatim from the URTC version.

## 2. Anchors
| Line | Anchor |
|---|---|
| 391-393 | `\section*{Acknowledgments}` / "This paper has been written as part of the Boston" |
| 3-4 (comment, not printed) | "% Body text is VERBATIM from the URTC conference version" |
| 65-67 | `\author{Rajan Saha\\` … "Boston University RISE Data Science Practicum}" (title page) |

## 3. Old text (verbatim)
l.393:
> This paper has been written as part of the Boston University RISE data science practicum. I would like to thank the program and the teaching fellows and staff.

For comparison only (not to be restored): the URTC Acknowledgments (`paper_current_URTC_20260808.tex`
l.242) carried an AI line ("was used to validate the code and grammar"), a repository URL, and the
plural "the authors". R04's note records that line as naming **no code portion** (erratum E3), i.e. it
did not satisfy App. 4 either. The STS version removed it without replacement (`notes/scholar-research.md`
E-2(a)).

## 4. What must change — the checklist

Columns: **Fact** (what the record shows) · **Repo evidence** · **Rule that requires it (verbatim, row
id)** · **Who supplies the fact** · **Open?**

### A. Generative-AI use
| # | Fact to disclose | Repo evidence | Rule (verbatim) | Supplier | Open? |
|---|---|---|---|---|---|
| A1 | The AI tool(s) used: Claude Code (Anthropic); model recorded as `claude-opus-5[1m]` in 33 log entries; the 2026-07-21 reference draft records "Claude (Claude Code, Opus 4.8)"; the 2026-08-17 retired draft's chat product is NOT DETERMINED | `notes/ai-prompt-log.md` header l.3 and `**Model:**` lines; `notes/contribution-log.md` (2026-07-21); prompt log l.2294-2318 | R22 (App. 4): "Use AI to write initial code for your project - Yes - Acceptable, only with explicit citation stating which portions of the code were AI generated and with a log of the prompts." | author confirms the tool list (any other chatbot used?) | yes — any tool not in the log |
| A2 | **Which portions of the code were AI-generated** | Partial record only: prompt-log entries from 2026-07-26 onward name the files each task produced (e.g. l.13-24 classical baseline scripts); `notes/ai_usage_changelog.md` marks every `scripts/sts_*.py` as "AI-written". **No record exists for code created before 2026-07-26** (first prompt-log entry is l.13, 2026-07-26), which includes the core pipeline (`feasibility/generate_dataset.py`, gate, surrogate, splits) that produced every headline number | same R22 row ("which portions of the code were AI generated"); R04 note: "The code-portion condition is NOT MET" | **author** — must establish, file by file, which code is own / AI-generated / AI-edited; the repo cannot answer this for pre-07-26 code | **yes — highest-effort item** |
| A3 | A log of the prompts exists and where it is kept | `notes/ai-prompt-log.md` (6,155 lines; entries 2026-07-26 → 2026-09-27); some entries are reconstructions ("Reconstructed from: session transcript"; the 2026-08-17 prompt text is "NO SOURCE"). **Not in git:** `notes/` is git-ignored (`.gitignore:23`), so the log has no commit history and no timestamps anyone else can verify (see §4 F) | R22: "…and with a log of the prompts"; "Maintain a logbook of your prompts as part of your research notebook." | author decides how the log is offered | whether STS wants it submitted or held (Q3 below) |
| A4 | AI used for data analysis / experiment execution / verification (agent-run experiments, fact-checks, the round-1 review panels and this spec set) | prompt-log categories: research ×18, experiment ×5, citation-audit ×3, manuscript-adjacent ×5 (tally of `**Category:**` fields); `notes/panels/round1_*.md`; `notes/ai_usage_changelog.md` | R22: "Use AI to help identify appropriate statistical tests or software tools. (Interpretation of data must be done by the student researcher) - Yes - Acceptable, requires a log of your prompts"; R20: "full disclosure of any research or person that has influenced the applicant's work is required." | author | whether AI review of the student's own draft needs citation (Q4) |
| A5 | AI touched the **report file** mechanically: 2026-09-04 paste of four author-written subsections (verbatim paste), Unicode-to-LaTeX math conversion, fix of four build-breaking lines | prompt log l.4860, l.4937, l.4982 (sha256 before/after recorded) | R22: "You write an abstract. Ask AI to sharpen the language but not modify, add to, or replace the main points - Yes - Acceptable use without explicit citation only if changes suggested by AI are minor and limited to grammar and syntax. Must be credited." | author | whether formatting-only edits need credit (Q6) |
| A6 | AI **text edits to the URTC manuscript** at camera-ready (2026-09-13, "make the edits to the text") — and the STS body is declared verbatim from the URTC version | prompt log l.5521-5528 (pre/post sha256, 278 → 276 lines); `.tex` header l.3; URTC camera-ready commit `8b88a99` (2026-09-22) | R04/R22: "Use generative AI to initially write the research plan, abstract, paper or poster - No - Never acceptable … Guidance or refinement after the initial document has been completed can be done with explicit citation and a log." | **author** — determine whether any AI-edited URTC sentence is in the STS body (read-only: `git diff 8cefaa7 8b88a99 -- paper_current_URTC_20260808.tex` shows all camera-ready changes; the AI's share of them is not separable from the author's in git) | **yes** |
| A7 | An **agent-drafted five-page reference paper** was produced on 2026-07-21 under an explicit scoped exception, never submitted, kept as a structural reference | `notes/contribution-log.md` (2026-07-21); `notes/1_research_draft_ORIGINAL.txt` and `notes/1_research_draft_ORIGINAL_rev2.txt`. These are **NOT tracked in git**: all of `notes/` is git-ignored (`.gitignore:23`, under "# Private — never commit to the public fork"). The files must never be written to (CLAUDE.md §8). | R22: "Use generative AI to initially write the research plan, abstract, paper or poster - No - Never acceptable. This must be the independent work of the student." | author — can state how the submitted text was written relative to it | **yes — `scholar-research.md` E-2(b) calls it "the highest-consequence unresolved question"; ask STS (Q7)** |
| A8 | AI-drafted candidate prose (2026-08-17) was produced, found to rest on unverified numbers, and retired without entering the manuscript | prompt log l.2294-2318; `notes/retired/2026-08-17_ai_draft_sections_RETIRED.md` | same R22 row | author | fold into Q7 |
| A9 | AI used to resolve bibliography entries from local notes, which the student then verified | prompt log l.2202-2222 (2026-08-15) | R22: "Ask generative AI to produce a starter bibliography - No - Never acceptable"; "Ask generative AI to fix the structure or formatting of your bibliography - Yes - Acceptable without explicit citation. You must review and verify all citations as valid." R04 note: "STILL AN ASK" | author | **yes (Q5)** |
| A10 | Mechanical enforcement since 2026-08-18: hooks block agent writes to `report/` | `.claude/hooks/guard_report_prose.sh`, `guard_report_bash.sh`; R04 note | (supporting fact, not a rule requirement) | — | no |
| A11 | AI use in the **application process** (e.g. `notes/scholar-research.md`, this revision's panels) | prompt log 2026-09-14 entries | Application Task 5 Q8-Q9 (per `notes/scholar-research.md` l.167-169, quoted there; not re-verified against the form here): "Select all of the ways AI tools were utilized in your STS research project and/or application process." | author | form field, not report |

### B. Program and people
| # | Fact | Repo evidence | Rule (verbatim) | Supplier | Open? |
|---|---|---|---|---|---|
| B1 | BU RISE Data Science Practicum is a **paid / fee-based** program; fee total | R20 note ("BU RISE was paid"); `CLAUDE.local.md`. **No fee total recorded anywhere in the repo** (`scholar-research.md` E-1) | R20 (GUIDE2027 closing): "full disclosure of any research or person that has influenced the applicant's work is required." Application Task 5 Q5 (per `scholar-research.md` l.163): "Entrants who have a paid relationship that is not disclosed will be disqualified." | author (fee total; must match the mentor's form — E-1) | fee total |
| B2 | Instructors: Kalita and Pinsky taught the material | R20 note; `CLAUDE.local.md` | R20 (as B1) | author confirms full names and roles | — |
| B3 | Teaching fellows by name | **Not recorded in the repo** | R20 (as B1) | author | yes |
| B4 | Mentor: Eugene Pinsky is URTC co-author **and** the STS project recommender | `paper_current_URTC_20260808.tex` l.54-57; prompt log l.5336-5341 ("He is writing the STS project recommendation") | R03 (RULES2027 p.6 §4): "Research conducted alongside adult researchers in a research institution is permitted, but clarity and adequate knowledge of an individual's role and independence vs. work being done by the collective laboratory throughout the application is vital." | author delineates own vs mentor contribution | — |
| B5 | Kalita was once listed as a co-author on a pre-URTC draft and later removed | prompt log l.1165-1171 (fact pattern recorded; "no prompt in this log authorizes or discusses that removal") | R20 (as B1); R03 (as B4) | author — be able to state Kalita's role consistently across report, form and recommendations | yes |
| B6 | Anyone (human) who read a draft, and what they did (suggestions only) | **Not recorded in the repo** | R20: "full disclosure of any research or person that has influenced…"; R27: "Adults reviewing research reports should suggest areas for improvement, but not provide the student with replacement text or rewrite any portion of the entry." | author | yes |
| B7 | Any coaching / tutoring on the project | not recorded | R20 corpus enumeration ("coaching" — corpus-sourced, the book's wording is general) | author | yes |

### C. The URTC paper and its co-author (P-012)
| # | Fact | Repo evidence | Rule (verbatim) | Supplier | Open? |
|---|---|---|---|---|---|
| C1 | A conference version was submitted to IEEE MIT URTC (submitted 2026-08-08, CMT #74), accepted; camera-ready committed 2026-09-22; conference 2026-10-09..11 | commit `8cefaa7` message; commit `8b88a99`; `notes/scholar-research.md` E-3 (dates); prompt log l.5543 ("accepted … not yet published") | R18 (GUIDE2027 rule 6): "In the case of published group research, acknowledge the published paper in your application, and submit your own version of the research to Regeneron STS that highlights your actual contributions to the larger research project." | author | publication status on submission day (accepted vs published) |
| C2 | Authors: Rajan Saha (first) + Eugene Pinsky (BU faculty, adult) | `paper_current_URTC_20260808.tex` l.48-58 (lead-verified D12) | R18 (as C1): "It is not recommended that students submit published research papers if they are not the sole or first author…" — first author, so permitted | — | no |
| C3 | The STS body is declared **verbatim** from the URTC version | `.tex` l.3-4 | R20: "both the content and writing should be the work of the applicant"; R27 (as B6) | **author must confirm that no sentence in the STS body was written or rewritten by the co-author** (and see A6 for AI edits) | **yes** |
| C4 | The report itself does not mention the URTC paper | `grep -n -i urtc report/paper_current_STS.tex` → only l.3, a LaTeX comment (not printed) | R18 requires acknowledgment "in your application"; whether the report should also cite it is the author's choice (Q8) | author | Q8 |

### D. Tools (non-AI) — credit completeness
| # | Fact | Evidence | Rule | Note |
|---|---|---|---|---|
| D1 | Fig. 5 layout computed with python-igraph (via pandapower), colour scale PowerNorm; credit line names Matplotlib only | `notes/patches/P-006.md`; `minors_P-018_P-027.md` (P-025); STS-12 | R21: "If you used third-party software … you need to mention the name of the program." | handled in P-006/P-025 |
| D2 | Repository link: permitted only in the bibliography or where the application requests it | R08/R09 (GUIDE2027 rule 5e): "Students may not provide links within the Research Report or application of any sort, except within bibliographic references or where specifically requested in the application." | if a repo link is given, it goes in a bibitem or the form — never the Acknowledgments (the URTC version had it in the body) |

### F. Evidence status of the disclosure records (git)
- `.gitignore:23` ignores the whole `notes/` directory, under the comment "# Private — never commit to
  the public fork". Checked with `git check-ignore -v` for `notes/ai-prompt-log.md`,
  `notes/contribution-log.md`, `notes/sts-constraints.yaml` and `notes/1_research_draft_ORIGINAL.txt`;
  `git ls-files notes` returns nothing.
- So **none of these disclosure records is in git**:
  - the prompt log (A3);
  - the contribution log (A7);
  - both agent-drafted reference drafts (A7);
  - the retired 2026-08-17 draft (A8);
  - `notes/ai_usage_changelog.md` (A2);
  - `notes/sts-constraints.yaml` (the rule rows quoted here).
- Their only record is the local file system: mtimes, plus sha256 values quoted inside the prompt log
  itself. There is no commit history for them.
- Consequence for evidencing the logbook: R22 asks for "a log of the prompts … as part of your research
  notebook". The log exists. What the repo cannot show a third party is when each entry was written.
  The author decides how to evidence it: private copy, timestamped export, or submission on request. The
  public-fork policy is the reason `notes/` is ignored, and changing it is the owner's call (CLAUDE.md
  §8: Claude runs no git writes).
- The pipeline code and data artifacts (`feasibility/`, `scripts/`, most of `data/`) are tracked, apart
  from the untracked `sts_*` files listed in `_index_B.md`. Code provenance (A2) therefore can be
  pointed at commits; the prompts that produced the code cannot.
- Must not claim that the prompt log or the reference drafts are "in the repository history".

### E. Questions to ask STS staff (the author writes the email; `sts@societyforscience.org` per `scholar-research.md` Rank 2(b))
1. **Placement:** are AI-use disclosures (tools, code portions, prompt log) expected inside the Research
   Report, in the application (Task 5 Q8-Q9), or both? (Decides FATAL vs MAJOR for P-002 — D11, NS-01.)
2. **Granularity of the code citation:** is a file-level list of AI-generated / AI-assisted code
   acceptable for the App. 4 code row, and must it appear in the report?
3. **Prompt log:** submit it, attach it, or keep it available on request as part of the research
   notebook? Does a log kept outside version control (no commit timestamps; see §F) satisfy the rule,
   or is a particular form of evidence expected?
4. **AI review of the student's own draft** (AI reviewer panels producing feedback and verification,
   no replacement text): which App. 4 row governs it, and does it need explicit citation?
5. **AI-resolved citations** that the student then verified against the source (R04 "STILL AN ASK"):
   acceptable, and does it need citation?
6. **Formatting-only AI edits to the report file** (math-markup conversion, build fixes, verbatim paste
   of student text): does the "Must be credited" row apply?
7. **The 2026-07-21 agent-drafted reference paper** (never submitted; used as a structural reference)
   and the retired 2026-08-17 AI draft: does their existence need disclosure, and how does the
   "initially write … paper … Never acceptable" row apply to a draft that was not used as text?
   (Factual question; `scholar-research.md` recommends sending early.)
8. **URTC overlap:** is acknowledging the accepted conference paper and its adult co-author in the
   application sufficient, or should the report also cite it? Does text shared with a co-authored
   paper need to be rewritten if the student wrote it? And do AI camera-ready edits to the conference
   version (A6) carry over as a report issue if any of that text is reused?
9. **Paid program:** is Task 5 Q5a the only place the fee total is needed?
10. **Page budget:** does an Acknowledgments/disclosure section count toward the 20 pages? (R05 lists
    title page, abstract and bibliography as excluded; Acknowledgments are not listed.)

## 5. Numbers
| Value | Source | Status |
|---|---|---|
| 6,155 lines in the prompt log; first entry 2026-07-26 (l.13) | `wc -l notes/ai-prompt-log.md`; `grep -n "^## "` | re-read OK |
| 33 entries with a `**Model:**` field: 21 "claude-opus-5[1m] (Claude Code)", 12 "claude-opus-5[1m]" | `grep -o` tally | re-read OK |
| URTC authors Saha + Pinsky | `paper_current_URTC_20260808.tex` l.48-58 | re-read OK |
| `grep -n -i -E "generative|claude|chatgpt|\bAI\b|artificial"` on the STS .tex → only l.101 (Alcántara) and a bib title | ledger §Commands C7 | lead-VERIFIED |
No comparison → no std-rule check.

## 6. Must not claim
- Not that no code was AI-generated, and not a partial list presented as complete (A2 is incomplete for
  pre-2026-07-26 code).
- Not "AI was used only to validate code and grammar" (the URTC-era line) — the log shows code writing,
  experiment execution, analysis, verification, citation resolution, review panels, and report-file edits.
- Not that the URTC paper is "published" or "presented" before it is (`scholar-research.md` E-4).
- No TF name, fee total, or draft-reader name that the author has not supplied — the repo has none.
- The spec writer does not decide whether any item is "minor"; the rule rows decide, and STS answers the
  open questions.

## 7. Consistency (must agree everywhere)
- Report Acknowledgments ↔ application Task 5 Q5 (fee), Q7 (AI-detector question), Q8-Q9 (AI use), Task 9
  Q3-Q4 (URTC, co-author) ↔ the mentor/recommender forms (fee total and contribution split must match —
  `scholar-research.md` E-1, Appendix 14 "discrepancy").
- Title page l.65-67 names the program; the Acknowledgments must not contradict it.
- The .tex header comment l.3-4 ("VERBATIM from the URTC conference version") is a claim the author
  should re-check after C3 (comments are not printed, but the file is the record).
- P-006 / P-025: every float's credit line names every program used (igraph for Fig. 5).

## 8. Page cost + dependencies
- If placed in the report: Acknowledgments grow by an estimated **+0.10 to +0.15 pp** (a disclosure
  paragraph; a code-portion list could be longer — keep a file-level list in the application or an
  appendix per STS's answer to Q2; an appendix **counts** toward 20 pages, R05).
- If STS answers Q1 "form field only": report cost ≈ +0.05 (program + people), AI details in the form.
- Dependencies: STS answers to E1-E10; A2 file-by-file provenance (author); C3/A6 check of the STS body
  against the URTC camera-ready. Blocks submission (ledger §2 Step 1.3).

## 9. Voice note
—
