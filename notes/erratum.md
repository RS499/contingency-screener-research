# Erratum log

Corrections to published or submitted material. Each entry records the defect, the evidence,
the fix, and how the correction is to be disclosed. Nothing here is a silent fix.

---

## E1 (2026-08-12) — Gate schematic in the paper is sized from the M1 band, not M2

**Where.** `paper_current_URTC_20260808.tex:112` and `README.md:6` both embed
`data/gate_schematic_v2.png`. (Path corrected 2026-08-19: the file was renamed from
`paper_current.tex`; line 112 is unchanged and still correct.)
`data/poster/gate_schematic.png` is byte-identical to v2 (md5 `5b8e53a285a1c739edef92c23db760d8`)
and carries the same defect.

**Defect.** The escalation strip in that figure is sized from the **M1** band width,
`q_hat = 0.002557` pu, read from `data/tradeoff_curve.json`. Every reported number in the
paper derives from **M2**, whose band width is `q_hat = 0.002291` pu
(`data/tradeoff_curve_v2.json`, histgb, `coverage_target` 0.90). The rendered strip is
therefore about 11.6% wider than the band the results actually use. This violates the
standing M1/M2 rule (M2 is the promoted selection; an M1 quantity is never the result).

**Scope — what is and is not wrong.** No *printed numeral* differs between v2 and v3. The
only numerals rendered as text are the hardcoded `"0.94 pu"` limit label and the y-axis ticks,
identical in both; `feasibility/gate_schematic.py` prints `"annotation prints no number"` and
uses `q_hat` only as geometry. The defect is in the figure's quantitative geometry, not in any
caption or label. It is a real inconsistency because the strip is the visual statement of the
band width, but it does not falsify a quoted number.

**Correct figure.** `data/gate_schematic_v3.png` is the M2-consistent version and is
regenerable byte-exactly:

```
.venv/bin/python feasibility/gate_schematic.py \
    --font-bump 2 --curve data/tradeoff_curve_v2.json --out data/gate_schematic_v3.png
```

Verified: that command reproduces committed v3 with md5 `5ceefccf43d5441191e9e41835924af2`.
(The `--font-bump 2` flag is documented in the script's own help text as "v3 uses 2"; the
font bump is cosmetic, the `--curve` argument is the substantive difference.) Nothing in the
repository currently references v3.

**Disposition — camera-ready fix, disclosed, NOT a silent correction.** The URTC submission
contains the M1 figure. The correction is to be stated in the camera-ready rather than
swapped in quietly, since the submitted and published figures would otherwise differ with no
record of why.

**Caveat on pinning the submitted state — CORRECTED 2026-08-19.** This entry previously read
"There is no `urtc-submission` tag ... `git tag -l` is empty locally." **That is no longer
true.** An annotated `urtc-submission` tag now exists locally: tag object `23bc760`, pointing
at commit `8cefaa7`. The submitted state is therefore pinned by a ref, and the claim "the URTC
submission contains the M1 figure" can be checked against that commit rather than resting only
on `paper_current_URTC_20260808.tex:112` still pointing at v2. Whether the tag has been pushed
to `origin` or `upstream` is not asserted here.

**Not yet done.** No `\includegraphics` path has been changed. `paper_current.tex`,
`data/poster/`, and `data/gate_schematic_v3.png` all remain uncommitted as of this entry.

---

## E2 (2026-08-27) — A live URL sits in the body of both papers, which STS Rule 5e forbids

**Where.** `report/paper_current_STS.tex:287`, in `\section*{Acknowledgments}`:
`\url{https://github.com/rajsaha-blip/contingency-screener-research}`. The URTC version carries
the same acknowledgments block — **verify `paper_current_URTC_20260808.tex` before acting; this
entry asserts the STS line only, which was read directly.**

**Defect.** STS 2027 Research Report Guidelines, rule 5e, verbatim (fetched 2026-08-27,
`sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Research-Report-Guidelines.pdf`):

> "Students may not provide links within the Research Report or application of any sort, except
> within bibliographic references or where specifically requested in the application."

The repository URL is in the Acknowledgments, not in a bibliographic reference, so the exception
does not reach it. Scanned the whole file: **two URLs exist. `:317` is inside
`\bibitem{case118}` and is permitted. `:287` is not.**

**Scope.** **STS version: RULE VIOLATION.** **URTC version: NOT A DEFECT** — IEEE conference
papers routinely carry a code URL, and no URTC rule against it is known here. This is a
venue-specific defect, not an error of fact. Nothing in the paper becomes untrue.

**Disposition.** Not applied. The fix is a judgement call the owner must make, because the URL is
doing real work — it is the reproducibility pointer, and `CLAUDE.md` §9 aims the repo at being a
runnable artifact. Two options, neither drafted here: move the repository to a `\bibitem` and cite
it, which the exception permits; or drop the URL from the STS version and name the repository
without linking it. **The STS application has a separate field for project links; whether that is
"where specifically requested in the application" is NOT VERIFIED and would settle the question.**

---

## E3 (2026-08-27) — The AI disclosure names no portion of the code, which Appendix 4 requires

**Where.** `report/paper_current_STS.tex:287`, same sentence block as E2: "An AI assistant, Claude
from Anthropic, was used to validate the code and grammar."

**Defect.** STS 2027 Official Rules, **Appendix 4, p.34** (fetched 2026-08-27,
`sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Official-Rules.pdf`)
permits AI code assistance on a stated condition, verbatim:

> "Use AI to write initial code for your project — Yes — Acceptable, only with explicit citation
> stating **which portions of the code were AI generated** and with a log of the prompts."

The disclosure at `:287` states *that* AI was used and does not state *which portions*. **The log
half of the condition is already met** — `notes/ai-prompt-log.md` is the "logbook of your prompts
as part of your research notebook" that Appendix 4 requires, and it predates this finding. **The
portion-level attribution does not exist anywhere in the repository.**

**Scope.** **STS version only.** URTC has no equivalent rule on record here. **Not a factual
error** — the sentence is true as far as it goes; it is incomplete against a rule.

**Also corrected by this entry.** `notes/finalist-paper-analysis.md` §1.3 and its R5 read rule 1
of the Research Report Guidelines as a flat prohibition on generative AI. **Appendix 4 is a graded
13-row table, not a prohibition**, and §1.3 never saw it because that pass fetched only the
two-page Guidelines, not the 50-page Rules book. `notes/writing-guide.md` PART 10.6 carries the
corrected reading with the table. **§1.3 is superseded on this point and has not been edited.**

**Disposition.** Not applied. What is attributable is a question of fact only the author can
answer, and the answer determines whether the sentence needs one clause or a paragraph.

---

## E4 (2026-08-27) — No graphic in the paper carries the citation Appendix 3 requires

**Where.** All six floats in `report/paper_current_STS.tex`: `:136-141` (`fig:gate`), `:154-169`
(`tab:models`), `:176-200` (`tab:ops`), `:206-211` (`fig:tradeoff`), `:222-227` (`fig:missdepth`),
`:241-246` (`fig:boundary`).

**Defect.** Rule 2 of the Research Report Guidelines and Appendix 3 of the Official Rules (both
fetched 2026-08-27) require every graphic — **explicitly including tables, and explicitly including
graphics the student created** — to be cited "under or next to each individual graphic", with the
student attribution, the creating program, and the year. Appendix 3: "improper citation of graphics
is grounds for disqualification." **Detector over the whole `.tex` returned ZERO floats carrying
any such line.**

**A second, quieter defect inside the first.** `notes/writing-guide.md` §3.A asserts that the
figure manifest "carries `apa_citation`". **That is true only for `data/fig_identity.manifest.json`
and `data/fig_floor.manifest.json`, neither of which is in the paper.** Of the four figures that
are: `gate_schematic_v2`, `tradeoff_hero_col_v2` and `boundary_mass_hist` have **no manifest at
all**, and `miss_depth_v2` has a manifest with **no `apa_citation` key**. Furthermore both existing
`apa_citation` values are a full APA reference to Matplotlib and **carry neither the
student-researcher attribution nor the year of creation**, so copying them would still fail
Appendix 3.

**Scope.** **STS version: DISQUALIFICATION RISK.** **URTC version: NOT A DEFECT** — IEEE style has
no such requirement.

**Blocked item.** The generating script for `data/tradeoff_hero_col_v2.png` was **NOT LOCATED** in
`feasibility/` or `scripts/`. Its citation cannot name a creating program until the script is
found. That is a repository question, not a rules question.

**Interaction with E1 — do not resolve E4 on `fig:gate` first.** E1 records that the committed
`data/gate_schematic_v2.png` is sized from the **M1** band while every reported number is **M2**,
and that `v3` is the corrected figure. Writing a citation line under `v2` attributes a figure
already known to be defective. **E1 before E4 on that float.**

**Disposition.** Not applied. Specified per float in `notes/writing-guide.md` PART 10.3, with a
word cost of ~72 words against the budget in §6.2.

---

## E5 (2026-08-27) — Page numbers render bottom-centre; Rule 5c requires bottom-right

**Where.** `report/paper_current_STS.tex` preamble, `:25-50`. No `\pagestyle`, `fancyhdr` or
`\fancyfoot` command exists anywhere in the file — `grep -c` returns 0 — so
`\documentclass[12pt]{article}` applies its default `plain` style and sets the folio bottom-centre.

**Defect.** Rule 5c, verbatim: "Number the pages of your research report in the bottom right
corner, starting after the abstract." **Two requirements, both unmet:** position, and the start
point. The file has no abstract page break, so there is nothing for numbering to start after —
this is the same structural gap recorded against Rule 4b in PART 10.5.

**Scope.** **STS version only.** URTC/IEEE templates set their own folio and this is not a defect
there.

**Disposition.** Not applied — the prompt directed that it be specified, not applied. Specified in
`notes/writing-guide.md` PART 10.4. **Word cost: 0.**
