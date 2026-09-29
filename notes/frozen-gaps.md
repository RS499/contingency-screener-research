# Frozen-poster-numbers gaps

data/frozen_poster_numbers.json is frozen and byte-stable. Do not regenerate it. This file lists
values a poster or writeup may need that are not in the frozen file, so a future session extends the
frozen file rather than reaching around it. Each entry says where the value lives now and why it
matters.

- R2 for ridge and histgb. Lives in data/screener_metrics.json and CLAUDE.md 3 (histgb 0.913, ridge
  0.777). Needed for the "more accurate model is the less safe one" point (defend-every-line entry
  10); the frozen file carries only escalation, coverage, missed, and speedup, not fit quality.
- Clip-era comparison values, meaning the clip violation rate and clip missed rates. Live in
  CLAUDE.md 5.5 (28.6% violation; ridge 3.84%, histgb 3.01% missed). Needed for every before-and-after
  framing of the artifact fix (defend-every-line entries 9 and 14), which contrast clip against v2.
- The zero-variance column count and the non-converged row count. Both are build-dependent and come
  from make_splits.py console output, not a committed file. The non-converged count is derivable
  (1,500 x 186 minus frozen converged_n1_rows 278,955 = 45 on v2); the column count is not, and
  neither is committed. They drifted between builds unnoticed, which is why defend-every-line now
  avoids pinning them.
- The 0.95 gate-pass rate on the resampled build. Session-derived from a one-off N-0 probe, never
  committed; low single digits, above the clip-era 2.93% in the artifact-clip threshold table. Needed
  for the "why 0.94 not 0.95" answer (defend-every-line entry 15), which quotes direction, not a v2
  number.
- The gradient-boosted conformal band width q_hat at the 90% coverage target. Not in the frozen file
  (which carries escalation, coverage, missed, and speedup, not band width). It lives in
  data/tradeoff_curve.json (record model histgb, coverage_target 0.90, field q_hat = 0.002557) and
  matches the mean over five seeds in data/screener_metrics.json. The gate schematic figure
  (feasibility/gate_schematic.py) reads it from the tradeoff curve to size its band.

## Repo-state reminders for the poster and any STS submission

These are not missing numbers; they are switches and deferred work a future poster or STS session
must know about, recorded here because that session will be reading this file.

- Per-figure credit line is OFF. figtools.py sets CREDIT_ENABLED = False for the IEEE paper, where
  the author byline establishes authorship. The poster and any STS submission require per-figure
  attribution, so set CREDIT_ENABLED = True and re-render every figure before submitting to those.
- Poster-to-paper size presets are not built. The tradeoff figures (hero, record, q_hat) are drawn at
  poster-panel dimensions with large FS_* fonts in tradeoff.py; the paper figures (gate schematic,
  boundary-mass histogram) are drawn at IEEE column widths with smaller paper fonts. For an IEEE
  submission the tradeoff figures would need re-rendering at column width with the smaller fonts.
  Deferred: a POSTER/PAPER preset that switches dimensions and font sizes together, roughly one to two
  hours of mechanical refactor plus per-figure legibility tuning. The critical-bus map is a poster and
  repository figure and is not planned for the paper, so it is out of scope for that preset.
- Fig. 3 of the reference draft (notes/1_research_draft.txt) now uses data/tradeoff_hero_col.png, a
  single-column (3.5 inch) re-render produced by feasibility/paper_hero.py from the committed tradeoff
  curve, with paper fonts and no in-figure title. The poster hero data/tradeoff_hero.png is unchanged.
  The broader POSTER/PAPER preset above (re-rendering the other poster figures at column width) is
  still open; paper_hero.py is a one-off column version of the hero only.
- Deferred legibility fixes for data/tradeoff_hero_col.png, versus the poster tradeoff_hero.png (note
  only, not re-rendered): (1) the column version dropped the shaded "missed-violation > 1% (unusable)"
  region that the poster shades; (2) the crossing annotations are now bare numbers (0.95, 0.96)
  crowded against the 1% reference line near the x-axis; (3) the upper-left legend occludes the histgb
  missed-violation curve where it is highest, roughly coverage 0.71 to 0.80 (confirmed by eye). A
  future column render should restore the shaded region, label the crossings more clearly, and move or
  shrink the legend so it does not sit over the histgb curve.
