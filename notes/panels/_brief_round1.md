# Round-1 blind panel brief (shared by all 5 panelists)

Repo: /Users/rajansaha/contingency-screener-research (cwd). Paper under review: a Regeneron STS 2027
research report, `report/paper_current_STS.tex`, by a high-school student (solo project, BU RISE
summer program, continued into the fall). Deadline 2026-11-05. STS scholar stage (Top 300) is judged
by panels from many disciplines; the Top 40 are then picked by a panel of doctoral scientists,
mathematicians and engineers. The Research Report is weighted most.

## What to read
- The compiled paper: `notes/panels/round1_paper_text.txt` (pdftotext of the author's Overleaf export,
  20 physical pages, compiled 2026-09-27 13:50 from the current .tex). The PDF itself, with figures, is
  `/Users/rajansaha/.claude/jobs/484f4ac7/tmp/paper_v39.pdf` (Read tool, `pages` parameter). The figure
  PNGs are in `data/` (see the `\includegraphics` lines in the .tex).
- The source: `report/paper_current_STS.tex`. Anchor findings to it.
- Project rules: `CLAUDE.md` (repo root). STS rules: `notes/sts-constraints.yaml`. Verified prior-work
  entries: `notes/prior-art.md`. The std rule: `notes/number_check.md` lines 81-107 (section 3) ONLY.
- Anything you need to check claims: `data/` (JSON, parquet, manifests), `scripts/`, `feasibility/`,
  `scratch/*.py`, `notes/lit/` (papers), `notes/cited papers/`.

## BLIND RULE — do NOT open any of these (earlier reviews; the point is independent judgment)
`notes/sts_review.md`, `notes/placement_plan.md`, `notes/claude_ai_draft_edits.tex`,
`notes/number_check.md` (except lines 81-107), `notes/writing-guide.md`, `notes/science-review.md`,
`notes/reviewer-issues.md`, `notes/sts-audit-*.md`, `notes/factcheck-*.md`, `notes/novelty-review.md`,
`notes/audit-new-sections-layout.md`, `notes/new-sections-layout.md`, `notes/RUN_REPORT.md`,
`notes/erratum.md`, `notes/frozen-gaps.md`, `notes/defend-every-line.md`, `notes/claims_map.md`,
`notes/handoff-*.md`, `notes/state-of-project.md`, `notes/ai-prompt-log.md`, `notes/retired/`,
`report/*.md`, and any other `notes/panels/round1_*.md` written by another panelist (until told).
If a grep result shows text from one of these, do not follow it up.

## Hard rules
- Read-only everywhere except your ONE output file `notes/panels/round1_<role>.md`. You may write
  throwaway scripts/outputs only under `/Users/rajansaha/.claude/jobs/484f4ac7/tmp/panel_<role>/`.
- Python: `.venv/bin/python` only (bare `python` is blocked by a hook and is the wrong interpreter).
- No git writes of any kind. Never write to `report/` (hook-blocked: STS report prose is author-only).
- STS 2027 forbids AI-written report text. Your "suggested fix" says WHAT must change (content,
  number, source, location) — never a ready-to-paste replacement sentence.
- Evidence convention: **VERIFIED** (you recomputed it from a file, give file → key or command),
  **Reported** (taken from a file/manifest without recomputation), **unverified**.
- Std rule: a difference ("above", "better", "gap") is real only if it exceeds the larger of the two
  seed stds. Seeds use population std (ddof=0) over 5 splits unless a file says otherwise.
- The M1/M2 rule: M2 (gate-aware) selection is the promoted result; v2 artifacts are canonical
  (`data/frozen_poster_numbers_v2.json`, `data/tradeoff_curve_v2.json`). Flag any M1/v1 number printed.
- Bus numbering: prose uses IEEE 1-based names; code/artifacts use 0-based (IEEE = index + 1).
- Never invent a number or a citation. If you cannot check something, say unverified.

## Output file format (`notes/panels/round1_<role>.md`)
1. **Rubric** — 1-10 for originality, rigor, significance, clarity, student potential; one sentence each.
2. **Findings** — numbered `<ROLE>-##`. Each: `.tex` anchor (quote the first ~8 words of the sentence;
   add the line number for navigation), severity FATAL / MAJOR / MINOR, evidence (file → key, or the
   exact command run and its output), suggested fix (content-level). Order by severity. FATAL = a judge
   would stop trusting the paper or it breaks an STS rule; MAJOR = materially lowers the score;
   MINOR = polish.
3. **Three strongest parts** of the paper that must be protected during revision, with anchors.
4. (Optional) **Open questions** you could not settle.
Aim for depth over count; keep the file under ~350 lines.
