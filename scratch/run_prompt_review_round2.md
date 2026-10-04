# Round-2 pre-submission review + paper-fix-plan reconciliation

Adapted from the 2026-09-27 review prompt (`notes/ai-prompt-log.md` entry "2026-09-27 (b)"). The parts that
broke project rules last time are removed: AI edits to the .tex, `\edit` markup, a git branch, commits. This
version is review-only. It then cross-references `notes/paper_fix_plan.md` and updates it.

How to start it: open a new Claude Code session in the repo and type
"Read scratch/run_prompt_review_round2.md and do it."

---

## Prompt

You are the team lead for a round-2 pre-submission review of my Regeneron STS 2027 research report,
report/paper_current_STS.tex. The deadline is 2026-11-05. Find everything that would keep this report out of
the Top 40, then reconcile the findings with my existing revision plan, notes/paper_fix_plan.md, and update
that plan. Be honest about what text changes can and cannot do.

STS scholars are chosen by judges from many disciplines, with the Research Report weighted most. The Top 40
are then chosen from the 300 scholars by an additional panel of doctoral scientists, mathematicians and
engineers. Design the review to survive both stages.

### 0. Ground rules (every teammate, every phase)

**Read first.** CLAUDE.md, notes/sts-constraints.yaml and notes/prior-art.md. Project rules override
anything below; if they conflict, tell me.

**Report only.**
- No edits to anything under report/ (hook-enforced).
- No replacement sentences or "suggested wording": fixes are content-level specifications only.
- No git writes of any kind.
- You may write only these:
  - new files under notes/panels/round2/;
  - edits to notes/paper_fix_plan.md (Phase 2 only);
  - appends to notes/ai-prompt-log.md;
  - new files under data/sts_r2_* and scratch/r2_*, if a check needs a computation (each data file gets a
    manifest).

**Python.** .venv/bin/python only.

**Data integrity.**
- Do not modify existing data files.
- The current, canonical labels are the PV/PQ switch-back corrected labels:
  - case118: data/sts_n2_label_audit.parquet;
  - other networks: see scratch/n10_result.md, scratch/n11_result.md and scratch/n12_result.md.
- Old pandapower ("stored") labels are superseded. Any number in the paper computed on them must be flagged.
- v2/M2 artifacts only.

**Numbers.**
- Never invent a number.
- Evidence convention:
  - VERIFIED (you recomputed it; give the command or file → key);
  - Reported (taken from a file or teammate without recomputing);
  - unverified.
- Std rule: no "above", "better" or "gap" unless the difference exceeds the larger seed std.

**Citations.** Never fill a bibliography field from memory. Use only entries verified in notes/prior-art.md;
list any others for me. Check that the paper's descriptions of prior work match the source papers in
notes/cited papers/ and notes/lit/.

**Compile and page count.**
- There is no TeX on this machine. Use the newest Overleaf export in ~/Downloads ("Conformal Gated Surrogate
  Screening (N).pdf").
- Check that it was exported after report/paper_current_STS.tex was last modified, and that its text matches.
  If it doesn't match, ask me to export a fresh PDF before Phase 1.
- Report counted pages (title, abstract and bibliography excluded; appendices count; cap 20).
- Run scripts/check_compliance.py.

**Logging.** Append this prompt to notes/ai-prompt-log.md (CLAUDE.md §8).

### Phase 1 — Blind judge panels (read-only)

Create an agent team of 5 panelists.

**Blind rule.** No panelist may open any of these:
- notes/paper_fix_plan.md, notes/panel_ledger.md, notes/sts_review.md, notes/placement_plan.md;
- notes/number_check.md (except its §3 std-rule definition);
- notes/writing-guide.md, notes/patches/, notes/panels/ (round 1), notes/session_record_*.md;
- any other earlier review.

They judge the PDF and the .tex, plus whatever repo files (data/, scripts/, scratch/ code and result files)
they need to check claims.

**The panelists:**
1. **Power-systems PhD.** Physics correctness, realism of base cases and sampler, trustworthiness of the
   labels (including Q-limit handling and the switch-back correction), and operator relevance.
2. **Statistics / ML PhD.**
   - What is guaranteed vs measured.
   - Test-set leakage in operating-point choice.
   - Baselines, including the no-ML conditional-history baseline.
   - Paired vs unpaired comparisons.
   - Whether the pre-registration claims are supported by evidence held by a third party.
3. **Non-specialist doctoral scientist.** Can they state the question, the answer and why it matters after
   page 1? List every blocking term.
4. **STS Top-40 selection judge.**
   - Score originality, rigor, significance and evidence of the student's own thinking.
   - Say plainly whether this is Top 300 / Top 40 material now, and name the single change that would move
     it most.
5. **Reproducibility auditor.**
   - Trace every number, table and figure to its source file and script.
   - Flag every number still on old (stored) labels.
   - Flag mismatches and rounding inconsistencies, and figure/caption disagreements. That includes figures in
     the Overleaf PDF that differ from the repo PNGs: extract them with pdfimages and pixel-diff them.

**Each panelist writes notes/panels/round2/round2_<role>.md containing:**
- a rubric, 1-10 each, for originality, rigor, significance, clarity and student potential, each with one
  sentence of justification;
- findings, each with:
  - a .tex anchor (quote the first words; line numbers for navigation only);
  - severity: FATAL / MAJOR / MINOR;
  - evidence;
  - a content-level fix;
- the 3 strongest parts of the paper to protect.

**Challenge round.** After everyone writes, panelists challenge findings they disagree with. Record the
disagreements and resolutions in notes/panels/round2/round2_disagreements.md.

### Phase 2 — Reconcile with the plan and update it

As lead, now read:
- notes/paper_fix_plan.md (all sections, including the dated updates);
- notes/panel_ledger.md;
- notes/panels/round1_*.md (round-1 rubrics) and notes/panels/round1_disagreements.md;
- scratch/n9_result.md, scratch/n10_result.md, scratch/n11_result.md, scratch/n12_result.md.

**Write notes/panels/round2/round2_summary.md:**
- **Rubric table, round 1 vs round 2** (per panelist and mean), plus the STS judge's Top-300 / Top-40
  judgment for each round.
- **Status of every item in the plan:** done in the current .tex / partly / not done / no longer applies.
- **NEW findings** that the plan does not cover. Mark them clearly; they are the reason this run exists.
- **Plan items the panels disagree with,** with reasoning.
- **Contradictions inside the plan** (stale lines, superseded numbers, inconsistent claim ceilings).

**Then update notes/paper_fix_plan.md:**
1. Append a section "Update <date> — Round-2 review" with:
   - each new finding: what, where, severity, evidence, fix, page cost;
   - each status change;
   - a revised ordered work plan.
2. Fix stale or contradictory lines in place. Keep the history readable: annotate superseded lines rather
   than deleting them.
3. Every number you add to the plan must be VERIFIED by you or by a separate verifier agent, which recomputes
   it from the source file. No number enters the plan without a sign-off.
4. Keep one consistent claim ceiling (can say / cannot say) and one Results structure. If round 2 changes
   them, replace them and mark the old ones superseded.
5. List the author decisions that remain open, each with options and a recommendation.

### Deliverables (final message)

- The rubric table, round 1 vs round 2, with each round's STS-judge verdict.
- The FATAL and MAJOR findings, each marked new vs already in the plan.
- A summary of the plan changes, i.e. which sections were added and which lines were fixed.
- The open author decisions, with recommendations.
- What text edits cannot fix, and whether each is a threat to Top 40.
- The exact git commands for me to commit notes/panels/round2/, notes/paper_fix_plan.md,
  notes/ai-prompt-log.md and any data/scratch files written.

Do not claim anything is done without its evidence. If you are unsure whether something counts as an author
decision, treat it as one.
