# Cuts — Cut-3, Cut-5, Cut-6, Cut-7, Cut-8, and Cut-2 (Fig. 5, author-decision)

Fix specification, not prose. Each cut names the exact span (first words … last words, verbatim), the
estimated saving in counted pages (plan unit costs, **not a compile** — no TeX toolchain here; confirm on
the next Overleaf export), and what must survive elsewhere. Where a cut shrinks a passage "to one
sentence", the sentence is the author's; this file only says what content it must carry.

Ledger rows: §1h (Cut-1..8), E14/E15 (Cut-1, Cut-4 handled by s-specA), §2 Step 4.

---

## Cut-3 — reject-option digression (l.314) → one sentence + cites
- **Ledger:** Cut-3; NS ("interrupts the mechanism"); P-017 (reject-option/Bayes-optimal/posterior/
  margin-condition terms are blocking and disappear with it).
- **Span to delete (verbatim first … last words):** l.314 from
  "While the methodology of this research is similar to classical reject-option results, it is not a direct application of it."
  … to
  "Therefore, the methodology carries over, not the underlying theorem."
  (five sentences; the paragraph's first sentence "Most of the contingencies lie within 0.005 per unit…"
  and everything from "Fig.~\ref{fig:boundary} displays the distribution…" onward are NOT in the span).
- **Keep (one sentence, author's):** content = the escalation window resembles a reject option near a
  decision boundary, but it is a fixed-width window above a physical limit, so the analogy is to the
  idea, not the theorem. Citations to keep attached: `chow1970`, `tsybakov2004`, `mammen1999`.
- **Must be preserved elsewhere:** if the one sentence drops `tsybakov2004` or `mammen1999`, they are
  cited nowhere else (grep: both only at l.314) → remove both bibitems and change
  `\begin{thebibliography}{23}` to the new count (`scripts/check_paper.py` checks declared vs actual
  bibitems). `chow1970` is also cited at l.361 (safe unless Cut-7 removes it too).
- **Saving:** −0.4 pp.
- **Also removes:** the l.314 claim "he proved that the rejection threshold is the local slope of the
  error–reject curve" (a claim-precision item recorded in `prior-art.md` §10.7 — cutting it removes the
  risk rather than fixing it).

## Cut-5 — case57 / case89pegase detail (l.353) → one sentence each, corrected reason
- **Ledger:** Cut-5; P-021 (case57 reason is wrong physics: at zero load it is broken model data, D10);
  C1 (inventory).
- **Span to delete:** l.353 from
  "I also dropped two networks, case57 and case89pegase, early due to major issues."
  … to
  "…meaning that no load-multiplier window falls within a safe thermal loading threshold, so the case was left out."
  (four sentences; ends the paragraph).
- **Keep:** that both were excluded before any gate ran, and one reason each — case57: the pandapower
  model does not reproduce a sensible base solution (voltage below the limit even at zero load; P-021
  corrects the "realistic conditions" framing); case89pegase: transformers over rating at nominal load
  and no feasible load window. **Where:** in the C1 network inventory (Method or the P-011 table), not
  wedged between predictor results (STS-09).
- **Numbers that may survive (one each, if the author keeps a number):** case57 minimum pre-outage
  voltage 0.9012 pu at load multiplier 0 with 24 buses below 0.94; 0 of 3,000 draws accepted
  (`data/case57_feasibility.json`); case89pegase 392% transformer loading / 16 of 50 over 100%, 199.37%
  maximum at multiplier 0 (source per `minors_P-018_P-027.md` P-021 and the case89pegase diagnostic
  `data/netstudy2/case89pegase_nofeasible_diagnostic.json` — not re-read here).
- **Must be preserved:** the practice of stating exclusions with reasons (STS/NS "strongest parts" #3).
- **Saving:** −0.3 pp.

## Cut-6 — dataset wall of numbers (l.119) → P-011 reproducibility table
- **Ledger:** Cut-6; P-011 (table, D15: knobs in a table, not prose); 2c-1..4.
- **Spans to move (verbatim):**
  1. "For Independent mode (750 bases), I multiplied the load by multipliers ranging from 1.0 to 1.12."
     … to
     "…range from 0.8156 to 1.4083 (to account for stochastic variations in the random power factor)."
  2. "The total sample contained 1{,}500 base cases and 280{,}500 rows, including the base cases."
     … to
     "…resulting in 278{,}955 converged rows."
- **Keep in prose (content, author's words):** the load-scaling idea in one clause (two sampling modes,
  defined — P-017 "Independent/Regional" are undefined blocking terms); the N-0 acceptance rule; the
  generator-out rule and its share (C6 definition lives here); 186 contingencies per base; the
  violation share; the post-contingency voltage range (with the P-003 caveat once settled). Every
  number appears **once** — in the table or the prose, never both (`P-011.md` l.48, l.210).
- **Must be preserved elsewhere:** 750/750, 0.9009-1.2310 (43.91% outside), 0.8156-1.4083, 280,500 /
  1,500 / 279,000 / 45 / 278,955 → P-011 rows. The "power factor" wording is inaccurate (it is a
  reactive-load multiplier — `P-011.md` flag); fix it where it lands.
- **Saving:** −0.3 pp (the table's +0.35 pp is counted in P-011; net of the pair ≈ +0.05).

## Cut-7 — Discussion l.361-363 merged into the Introduction's related work
- **Ledger:** Cut-7; OS-6 ("proven methods" — checker phrase, `checker-phrases.md`); R23 (no
  literature review beyond the short introduction); NS-24/STS-20/P-010 (l.363's statistics).
- **Span A to delete from Discussion (l.361, whole paragraph):**
  "Calibrated uncertainty, as well as making the decision of either outsourcing the problem or not to a more complex model"
  … to
  "…which is because most of the data is very close to the limit."
- **Span B to delete from Discussion (l.363, first two sentences):**
  "My approach differs from Manoharan's audited population control \cite{manoharan2026},"
  … to
  "…while the gate uses a margin of error that is subtracted from each prediction."
- **Keep l.363's remaining sentences** — they are the statistical caveats and are re-specified in
  `P-010.md` (marginal vs conditional; base-case grouping). Do not cut them with this item.
- **Must be preserved elsewhere (Introduction l.101, as one clause/sentence, author's):**
  - the lineage citations that currently live only at l.361: `desalvo2015`, `angelopoulos2024`,
    `cortes2016` (grep: each cited only at l.361) — if dropped, remove their bibitems and update the
    count; `chow1970` and `elyaniv2010` are also cited elsewhere;
  - the honest positioning (`CLAUDE.local.md` claim ceiling): the certify/flag/escalate mechanism is
    pre-empted by cascade routing and conformal triage; what is specific here is the instantiation (an
    exact AC solver as the escalation target, net-cost accounting, physical-unit band);
  - the Manoharan contrast (population-rate bound vs per-case band), accurate per `P-028.md`;
    `bates2021` stays cited at l.99 regardless.
  - Drop, not move: "I also explain why the speedup is capped" (the "must"/cap claim — C3/Top-5 #2(b)).
- **Saving:** −0.4 pp (Discussion) partially offset by ≈ +0.05 in the intro → **net ≈ −0.35 pp**.

## Cut-8 — shrink Fig. 3 (only if short)
- **Ledger:** Cut-8.
- **Span:** l.302 `\includegraphics[width=0.6\textwidth]{data/miss_depth_v3.png}` — reduce the width
  (the float, not the text).
- **Coupling (blocking):** Fig. 3 must be rebuilt anyway — the PNG draws "deepest miss 0.0915 pu" inside
  the image (ridge panel arrow; histgb ▼ marker at the same depth), which is the P-001 artifact case
  (`minors_P-018_P-027.md` P-024/P-025; `C4.md` fork note). Shrinking the current PNG does not fix
  P-001. Do Cut-8 on the rebuilt figure (d-figs), after N2.
- **Must be preserved:** legibility at print size (NS-09 made the same complaint about Fig. 5's
  in-figure text); R06 font floor applies to figure text by spirit, not rule.
- **Saving:** −0.25 pp (only if the layout actually pulls a page; unconfirmed without a compile).

## Cut-2 — Fig. 5 critical-bus map (AUTHOR-DECISION)
- **Ledger:** Cut-2 (author-decision); P-004 (stale 0-based PNG in Overleaf); P-025 (PowerNorm, igraph
  undisclosed); NS-09 ("referenced once and not used").
- **Span if cut:** the whole float l.331-343, from the comment block
  `% FIGURE 5 (fig:critical) -- critical bus map, from`
  … to
  `\end{figure}` (l.343), plus the clause "as shown in Fig.~\ref{fig:busmap}" at the end of l.314.
- **If cut, preserve:** the bus-share sentence in l.314 may stay without the figure (IEEE 76 / 53 / 107
  at 27.10 / 16.81 / 9.31% — precision per `numbers-2b.md` 2b-4), or go with it; `\ref{fig:busmap}`
  must not be left dangling (`check_paper.py` flags unresolved refs).
- **If kept:** upload `data/sts_critical_bus_map.png` (IEEE labels 76/53/107/1/21) and point
  `\includegraphics` at it; the caption must disclose the igraph layout and the square-root colour
  scale, and either mention bus 1 (8.45%) or not (d-figs flag 4); the credit line names every program
  (R21). The figure then has to *do* something in the argument — the one supported use is P-007: 31.62%
  of strip rows sit at IEEE 76, a PV bus holding its own sampled setpoint, i.e. the bus concentration is
  part of the sampler-driven boundary mass (numbers in `data/sts_dataset_facts.json`, per ledger
  Top-5 #1 row; not re-read here).
- **Saving:** −0.5 pp if cut; 0 if kept.
- **Recommendation (for the author to accept or not):** cut unless the author uses it for P-007 — nobody
  on the panel protects it as is.

---

## Totals (plan unit costs; not compiled)
| Cut | Saving (pp) | Blocking dependency |
|---|---|---|
| Cut-3 | −0.40 | bibitem count if tsybakov/mammen drop |
| Cut-5 | −0.30 | P-021 reason; C1 inventory location |
| Cut-6 | −0.30 | P-011 table (+0.35 counted there) |
| Cut-7 | −0.35 net | P-010 (keeps l.363 tail); P-028 (Manoharan wording); bibitem count |
| Cut-8 | −0.25 | P-001 figure rebuild (d-figs, after N2) |
| Cut-2 | −0.50 or 0 | author-decision; P-004/P-025 if kept |
| **All** | **−2.10** (with Cut-2) / **−1.60** (Fig. 5 kept) | one Overleaf compile to confirm |
