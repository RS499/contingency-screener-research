# Contribution and support log

Records who or what produced each deliverable, so credit is traceable and honest. This exists
because the venues this project targets (Regeneron STS and similar) require individually credited,
reproducible work, and CLAUDE.md section 10 makes disclosure the default in every borderline case.

## 2026-07-21 Scoped exception to section 10: agent-drafted reference paper

**What was suspended.** Section 10 holds that the AI toolchain must not write the owner's report
prose. For one task, and only that task, this clause was suspended by explicit owner instruction.

**What was produced under the exception.** A LaTeX draft of a five-page IEEE-style conference paper,
written to `notes/1_research_draft.txt`. It is a `.txt` file, not a `.tex` file, so it cannot be
mistaken for a submission artifact. The file opens with a header stating that it is agent-drafted,
dated, and not submittable as written. It replaces a stock IEEEtran conference template that was
sitting at that path as a scaffold.

**Why.** The draft is a structural reference the owner reads to learn how an IEEE conference paper is
shaped: section ordering, figure and caption placement, citation density, how limitations are framed.
It is not submission text and will not be submitted. Any text that reaches a poster, report, or
submission is written by the owner, per section 10, which resumes in full after this task.

**Limits that stayed in force.** Every number in the draft comes from
`data/frozen_poster_numbers.json`; anything absent is marked as a gap rather than invented. Every
citation comes from `notes/prior-art.md`, with unverified fields flagged, not filled from memory. The
claim ceiling (no "first", no "novel method") holds. The freeze on pipeline code, datasets, and
experiments holds. No numbers were recomputed.

**Toolchain disclosure.** The draft was written by Claude (Claude Code, Opus 4.8), applying a scoped
subset of the academic-research-skills conventions (outline-before-draft, the knowledge-isolation
rule, the writing-quality checklist, IEEE formatting) under the owner's precedence order. The heavy
multi-agent pipeline modes were not run; where their mandatory conventions conflicted with the task
specification, the task specification governed. Details are in the task report.
