# Session record — STS panel review and follow-up analyses (2026-09-27 to 09-28)

What Claude Code did in this session, in order, and where every output lives. The prompts are logged
verbatim in `notes/ai-prompt-log.md`, entries 2026-09-27 (b), (c) and (d). The report
`report/paper_current_STS.tex` was **not edited** (sha256 `c86e47d6…` before and after). The frozen JSONs
were not touched, and no git command that writes was run.

---

## Part 1 — Panel review and revision plan (prompt entry b)

### Deviations from the prompt (project rules won, as the prompt said they should)

| Asked for | What happened | Why |
|---|---|---|
| New branch `sts-panel-revision`, one commit per ledger ID | No branch, no commits. Commands are given in `notes/panel_ledger.md` §8. | CLAUDE.md §8: Claude runs no git writes. |
| Edit the .tex with `\edit` / `\del` markup; drafter writes "new text in my voice" | No .tex edits. The "patches" are fix *specifications* with no replacement wording. | Hooks block writes to `report/`. STS GUIDE2027 rule 1 and RULES2027 App. 4 forbid AI-written report text (`sts-constraints.yaml` R04, R22, R27). |
| Compile with latexmk after each integration | No compile. Used the Overleaf export "Conformal Gated Surrogate Screening (39).pdf". | No TeX toolchain on the machine. |
| Phase 4 re-review rounds 2-3 | Not run. | They need a revised paper, and only the author can revise it. |

### What was done

1. **Compiled state.** The Overleaf export matches the .tex (saved 1 minute earlier). It has **16 counted pages**
   (body pp. 3-18).
2. **Phase 1, blind panels.** Five reviewers (power systems, statistics/ML, non-specialist, STS judge,
   reproducibility), none of whom saw the earlier reviews, followed by a challenge round.
   - Files: `notes/panels/round1_*.md`, `round1_challenges_*.md`, `round1_disagreements.md` (D1-D16).
   - Mean scores after the challenge round: originality 5.0, rigor 5.0, significance 3.6, clarity 4.8,
     potential 7.8.
   - STS judge: Top 300 below a coin flip as submitted, about a coin flip once the blockers are fixed. Top 40
     very unlikely now, a long shot after revision.
3. **Phase 2, ledger.** `notes/panel_ledger.md`: 110 rows, work plan, author decisions AD-1 to AD-14, what text
   cannot fix, and commit commands. Every item from the 09-23 review was still present in the .tex.
4. **Data and figures.** New files only, each with a manifest: E1a facts, the limit-sweep figure, the
   cross-network scatter, a prose-free Fig. 5, Fig. 2 with std bands, Fig. 3 without the artifact annotation,
   the matched-escalation JSON, and the conditional-share recount.
5. **Approved runs.**
   - N2: Q-limit label audit.
   - N1: class-conditional calibration.
   - N4: paired 5-seed F1 shuffle.
   - N6: warm-start timing, which I re-ran at low machine load.
   - E12/E13: conditional coverage.
6. **Phase 3, specs.** 38 fix specs in `notes/patches/`. Two independent verifiers recomputed every number:
   set A 21/21 and set B 17/17 signed off after one fix round, and no spec failed twice.
7. **Compliance.** `notes/panels/compliance_round1.md`: checker run; the real density is about 440 words per
   page; the projection after all changes is about 18 counted pages (17-19.5).

### Main findings (full detail in the ledger)

**Findings the earlier review missed:**
- **FATAL — the featured worst miss is a solver artifact.** The 0.8485 pu case re-solves to 0.945073.
  pandapower switches a generator from voltage control to fixed reactive output and never switches it back.
- **FATAL — no AI disclosure in the report.** The Acknowledgments also omit the paid program, the instructors
  and the URTC paper.
- **Labels (N2).** 4,615 violations flip to safe and 2,162 safe rows flip to violation. The violation rate
  goes from 17.48% to 16.60%. 66% of the histgb@0.97 misses are artifact labels. Under corrected labels
  (no retraining), histgb@0.97 misses 0.46% and ridge@0.94 misses 1.14%, so the model ordering at the
  operating points reverses.
- **Static baseline.** A static training-frequency ranking beats the gate once flagged cases are also solved.
- **Fig. 5 in Overleaf is a stale 0-based copy** (labels 75/52/106). The repo PNG is correct.
- **Fig. 2's caption and text cite error bars the figure does not draw.**
- **The pre-registration was misread.** The review, the panels and my first ledger all read "removing the N-0
  filter halves boundary mass" as causal. The author's pre-registered conditional test (68.90% → 65.59%)
  says the filter does not create the concentration (D16).
- **Disclosure facts.** On 09-13 an AI session edited the URTC camera-ready text. None of those sentences
  appears verbatim in the STS body; 4 are close matches (`notes/panels/urtc_overlap.md`). `notes/` is
  git-ignored, so the prompt log and the pre-registration have no commit history.

**Honest headline numbers:**
- Held-out histgb misses 1.15 ± 0.27% (4 of 5 splits above 1%).
- Certify-only speedup 1.24×.
- Break-even about 4,200 sweeps.
- 10 parallel workers give 5.4×.

**Corrections to my own ledger, caught by teammates and fixed:**
- the unconditioned-build reading (D16);
- the 31.6% → 13.09% claim about generators holding their setpoint (P-007);
- the E14 std reading;
- the page-cost density (345 → 440 words per page).

---

## Part 2 — Follow-up analyses (prompt entry d)

Constraint: write only new files under `scratch/` and `data/sts_*`, with manifests. Make no decisions.

### 1) Independent label cross-check

- **Script and outputs:** `scratch/label_crosscheck.py` → `data/sts_label_crosscheck.json`,
  `_rows.parquet`, manifest.
- **Method:** my own semismooth-Newton AC power flow. The reactive-limit rule is a complementarity condition,
  so a generator at its limit returns to voltage control when the voltage demands it. Only the network model
  is shared with pandapower.
- **Validation:** with limits off, it matches pandapower within 1.5e-9 pu on all 201 rows.
- **Sample:** 100 violation→safe rows and 100 safe→violation rows (seed 20260927), plus the named worst case.

| | Agrees with original labels | Agrees with N2 labels |
|---|---|---|
| Violation → safe (100) | 0/100 [0, 3.6%] | 100/100 [96.4, 100%] |
| Safe → violation (100) | 0/100 [0, 3.6%] | 100/100 [96.4, 100%] |
| Pooled (200) | 0/200 [0, 1.8%] | 200/200 [98.2, 100%] |

Intervals are exact 95% (Clopper-Pearson). Every re-solve converged to a generator state consistent with the
limit rule.
- **Worst case:** 0.945073, the same value as N2.
- **Voltage differences:** 5 rows differ from N2 by more than 1e-4 pu (largest 5.0e-4); the labels are the same.
- **Fragile row:** one row is 1e-6 below the limit.

### 2) Matched-budget comparison

- **Script and output:** `scratch/matched_budget.py` → `data/sts_matched_budget.json`, manifest.
- **Reproduction:** exact against `tuned_metrics.json` (90 cells) and the `baselines.json` static curve.
- **Labels:** the stored labels.
- **Two accountings are reported rather than one chosen:**
  - **A (paper's):** only escalated cases use the solver.
  - **B:** flagged cases are solved too.
- **Under A:** the gate's catch rate (escalated or flagged) ties the static ranking for ridge at 0.90-0.92 and
  is higher at every other target for both models. If the gate is credited only with escalated cases, it
  catches 10-19% of violations and the static ranking is higher everywhere.
- **Under B:** the static ranking is higher at every target, except ridge at 0.97-0.98, where both reach
  about 100%.

### 3) Generator-voltage-floor rebuild

- **Prediction:** `scratch/n3_floor_prediction.md`, sha256
  `9975a07ec1c1a3004b524636239194a1584a8eadc5b6e3748766c4714446ba0f`, recorded 2026-09-28T03:15:32Z. The
  builds started at 03:17:22Z, and the file re-hashed identically afterwards.
- **Hash not git-committed.** "Commit the hash" conflicted with CLAUDE.md §8. Instead the hash is recorded in
  `scratch/n3_floor_prediction.sha256`, the prompt log and the transcript.
- **Runs:** `scratch/n3_floor_rebuild.py` → `data/sts_n3_floor094.*` and `data/sts_n3_floor095.*`. The only
  change between them is `GEN_VM_LO`.
- **Build A (0.94) is byte-identical to `data/dataset.parquet`.** This also recovers the dataset seed: 100,
  run as 4 shards.

| | Predicted 0.95 [range] | Observed 0.95 | Observed 0.94 |
|---|---|---|---|
| Boundary mass | 33% [20-45] | 32.95% | 56.86% |
| Conditional share | 40% [28-55] | 39.23% | 68.90% |
| Violation rate | 15.5% [12-18] | 16.01% | 17.48% |
| Bases in the strip | 35% [20-50] | 36.87% | 67.73% |
| N-0 gate pass rate | 70% [55-85] | 72.43% | 53.82% |

- **Outcome:** all quantities fell inside the predicted ranges. The pre-stated reading rule says this is
  "consistent with the generator voltage floor being a major driver".
- **Bounds on the result:**
  - one build per floor (no repeat-build error bars);
  - the prediction was informed by the 40-base probe;
  - pandapower labels in both builds;
  - no retraining or gate run;
  - the strip is still 33%, against 7.09% for case30.
- **Wall time:** about 6.9 h each, because the Mac slept on battery (power log).
- **Full scoring:** `scratch/n3_floor_result.md`.

### Housekeeping in Part 2

- **Changelog rows moved.** Four rows I had appended to `notes/ai_usage_changelog.md` fell outside the
  allowed folders. I moved them to `scratch/ai_usage_changelog_entry_d.md`.
- **First launch stopped.** It was stopped after about 10 s, with no output, because a 10-minute shell timeout
  could have killed it. It was then relaunched detached.

---

## Open items (all author decisions; nothing was decided here)

- **Ledger §5 AD-1 to AD-14:**
  - AD-1: the headline operating point;
  - AD-2: whether to relabel with the switch-back values (N2b);
  - AD-3: retitling;
  - AD-4: the disclosure wording, plus questions for STS staff;
  - AD-5: now partly answered by the floor rebuild — whether to retrain and run the gate on the 0.95 build;
  - AD-9: whether to keep Fig. 5;
  - and the rest.
- **Commits.** Owner commands are in ledger §8. For the prediction's git timestamp, the command is in
  `scratch/n3_floor_result.md`.
- **Overleaf.** Re-upload Fig. 5 (and any swapped figures), then re-export to get a real page count.
