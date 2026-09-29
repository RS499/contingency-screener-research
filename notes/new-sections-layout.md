# new-sections-layout.md

Specification for the sections to be added or replaced in `report/paper_current_STS.tex`.

**This file contains no manuscript prose.** Each entry states what must be true, the numbers
that must appear with their `notes/writing-numbers.md` row and result set, the citations, the
figure/table dependency, and the insertion point. The sentences are the author's.

**Anchor:** `report/paper_current_STS.tex`, 344 lines, sha256
`754be12b5f025c8e271a130e2f8548163251732c7e94e05283799278ee421c22`. Line numbers are positions
in that file, not identities. **Re-anchor after any edit.**

**RE-ANCHOR CHECK, 2026-08-19, git HEAD `03e1136`.** The manuscript was re-hashed on the
instruction that it had changed. **It has not changed.** sha256 is byte-identical to the value
recorded above, the file is still 344 lines, and `git diff HEAD` against it is empty (last
touched at commit `6082204`). All nine insertion points were re-verified line-by-line against
their quoted preceding sentences — **9 of 9 match, 9 distinct lines, no collision.** See §1.

**Number source:** `notes/writing-numbers.md` only. `writing-background.md` and
`section-V-writing-context.md` were not read; both are absent from the repository.

---

## 0. SUPERSEDED VALUES — correction history, retained deliberately

The Stage 4 brief supplied numbers for amendments 1, 2 and the thermal chain. Each was checked
against the artifact and then, in paired adjudication S8 and S9, re-derived from raw by an
independent agent whose anchor was **exact (0.0)** on every dataset it touched.

**Every supplied value below is SUPERSEDED. They are retained, not deleted, so the correction
history survives.** Every entry in §2 is specified against the measured column.

### 0.1 Amendment 1 — the S ratios — SUPERSEDED

| | supplied in brief (SUPERSEDED) | **measured, anchored (S8)** |
|---|---|---|
| ridge, case118 → case30-thermal | ~~0.604 → 0.219~~ | **0.603785 → 0.721343** — **RISES**, diff **+0.117558**, larger std **0.075685**, exceeds |
| histgb, case118 → case30-thermal | ~~0.443 → 0.482~~ | **0.791930 → 0.343935** — **FALLS**, diff **−0.447995**, larger std **0.074329**, exceeds |

Ridge's starting value (0.604) is the only supplied figure that survives. **The direction is
inverted for both models in the supplied pair.** S8 agent B re-derived both from raw with
anchors exact at 0.0 on case118 and on the case30 protocol, and reported the per-seed values
now recorded in `notes/writing-numbers.md`.

### 0.2 Amendment 1 — "zero counterexamples in 4.6M cases" — SUPERSEDED AND WITHDRAWN

~~"zero counterexamples in 4.6M cases"~~ — **withdrawn entirely, not merely corrected.** See
§2-D and §7 Q3: the count is zero **by construction**, so it is a derivation, not a
verification, and must not appear as an empirical claim anywhere in the layout or the draft.

For the record, the two populations that were conflated into "4.6M": missed cases **19,625**;
total test cases **6,128,100**. Neither is 4.6M. **NO SOURCE for 4.6M.**

The identity gap `5.551115123125783e-17` IS a real measurement and survives — but it measures
floating-point round-off on an identity, not the truth of the identity.

### 0.3 Amendment 2 — the 2C stratum figures — SUPERSEDED, and the framing REFUTED

| | supplied in brief (SUPERSEDED) | **measured, anchored (S9)** |
|---|---|---|
| stratum violation rates | ~~24.3% vs 4.7%~~ | benign **0.15373696096354447**, marginal **0.19577686957768695** |
| in-distribution marginal coverage | ~~0.7970, "only 0.0017 away"~~ | **0.8844348119083406 ± 0.026846519782127615** |
| shifted coverage | — | **0.7952977736840497 ± 0.017998553298487808** |
| gap (in-distribution − shifted) | ~~0.0017~~ | **+0.089137038224291**, larger std 0.026847, **exceeds 3.3×** |

**The supplied framing is refuted, not merely unsupported.** The brief held ridge's drop to be
confounded by stratum difficulty. Cell (c) holds difficulty fixed — calibrate marginal, evaluate
marginal — and removes only the mismatch; it sits near nominal at 0.884. The supplied 0.7970 is
within 0.0017 of the **SHIFTED** value (0.795298), not the in-distribution one, consistent with
the two having been transposed. **2C is a drift finding.** See §8.

### 0.4 The thermal share-above-100 chain

| | supplied in brief | **measured** |
|---|---|---|
| void (C-4) | 1.0 | 1.0 — confirmed, 120-prefix, positional mapping |
| "S1, 120-base prefix" | 0.9989 | **S1 was the FULL 61,500 population**, value 0.9989105691056911 |
| "full corrected population" | 0.9927 | **0.9989105691056911** |
| 120-prefix, bus-mapped | not listed | 0.999797 (S7 agent B) |

**NO SOURCE for 0.9927.** The chain has three real values, not the three supplied: 1.0 (void
prefix), 0.999797 (corrected prefix), 0.9989105691 (corrected full population). S1 and the
re-emitted artifact agree exactly on the full-population figure.

**And no value from this chain appears anywhere in `report/paper_current_STS.tex`** — grep for
`0.9989`, `0.9927`, `99.89`, `99.27`, `100%` returns 0 hits each. There is nothing to correct
in the manuscript on this axis; there is only something to ADD.

---

## 1. INSERTION POINTS — collision check

Discussion paragraphs are single unwrapped source lines at **256, 258, 260, 262**. Results
subsections open at **213, 229, 233**. Every insertion point below is distinct.

| # | new content | insertion point | follows the sentence ending |
|---|---|---|---|
| A | §II Related Work (new section) | **after line 86**, before `\section{Background}` at 89 | "…we explain why there must be a certain floor for escalation." |
| B | §III Background, NERC/ANSI grounding paragraph | **after line 96**, before `\section{Method}` at 99 | "…while ensuring specific generator reactive power limits are enforced." |
| C | §III-A replacement paragraph (sampling correction) | **replaces line 104 in place** | n/a — replacement, not insertion |
| D | §V Theory (new section) | **after line 141**, before `\section{Results}` at 144 | n/a — follows the Fig. 1 float `\end{figure}` |
| E | Results: flag-branch subsection | **after line 227**, before `\subsection{The faster model…}` at 229 | n/a — follows the Fig. 3 float `\end{figure}` |
| F | Results: non-convergence paragraph | **after line 235**, inside IV-3, before the Fig. 4 float at 241 | "…followed by bus 107 with 9.31\%." |
| G | Discussion: break-even paragraph | **after line 256** | "…which is because most of the data is very close to the limit." |
| H | Discussion: drift paragraphs | **after line 258** | "…rather than guarantees on individual contingencies." |
| I | Discussion: case30-thermal replacement | **replaces line 260 in place** | n/a — replacement |

**Naming convention: entry C is named by its PRE-renumbering number, §III-A** — matching
`E-A4-1`/`E-A4-2`/`E-A4-3`, which cite the same paragraph. After A is inserted the same
paragraph becomes §IV-A; the pre-renumbering name is used throughout this file.

**No two insertion points collide.** G follows 256 and H follows 258 — distinct paragraphs, and
this is the pair that collided in the earlier attempt. C and I are in-place replacements, not
insertions, so they cannot collide with A/B/D/E/F/G/H.

**Renumbering consequence:** inserting A as §II shifts Background→III, Method→IV, Theory→V,
Results→VI, Discussion→VII, Conclusion→VIII. Every `\ref{sec:…}` resolves automatically. The
single live cross-reference is `\ref{sec:discussion}` at line 116. **Three stale comments must
be updated by hand: line 134 "Cited in III-D", line 220 "Cited in IV-B", line 239 "Cited in
IV-C"** — these are comments only, they do not typeset, and under `article` with `\thesection`
Romanized `\thesubsection` renders **`IV.1`, `IV.2`, `IV.3`**, never `IV-B`.

---

## 2. SECTION SPECIFICATIONS

### A — §II Related Work

- **Number/title after renumbering:** §II, Related Work
- **`\label` to add:** `\label{sec:related}`
- **Insertion:** after line 86
- **Claim, one sentence:** Four prior approaches screen contingencies with surrogates, and this
  work differs from each in a stated, checkable way.
- **Numbers:** none required. If the GNN recall figure is used, the source is
  `notes/lit/notes/Graph Neural Networks for Fast Contingency Analysis of Power Systems.md` §4 —
  **approximate, transcribed from Fig. 7 bar labels, not prose-stated**, and the paper carries
  **NO BIBKEY** in `report/paper_current_STS.tex`. Add the bibkey and state the approximation, or
  do not use the figure.
- **Citations:** `manoharan2026` RESOLVED (`notes/prior-art.md` §6); `alcantara2026` RESOLVED
  (`prior-art.md` §6, §7.1); `christianson2025` RESOLVED (`prior-art.md` §7.2); `ejebe1979`
  **RESOLVED** — pinned and VERIFIED at `prior-art.md` §3 (Ejebe & Wollenberg, *Automatic
  Contingency Selection*, IEEE Trans. PAS, PAS-98(1):97-109, 1979); the bibkey STRING
  `ejebe1979` is absent from `prior-art.md`, the citation is not; `bates2021` **TODO** — no
  entry of any kind in `prior-art.md`.
- **Figure/table:** a four-row comparison table. Artifact: none — it is a literature table, not
  a result. **APA line: does not exist and is required by R10.**
- **Words / pages:** ~550 / ~1.6 pp (table ~0.4 pp of that).

### B — §III Background, NERC/ANSI grounding

- **`\label`:** extend existing `\label{sec:background}`; no new label.
- **Insertion:** after line 96
- **Claim:** The 0.94 pu screening floor is a conservative choice relative to the ANSI C84.1
  Range B service limit and is not itself a NERC requirement.
- **Numbers:** 0.917 pu — **provenance defect, see §6 erratum E-A4-7**; 0.94 pu (structural).
- **Citations:** `nerc` **TODO — no entry of any kind in `notes/prior-art.md`**; `grep -ni
  'nerc\|TPL-001'` returns zero hits. `ansi2020` RESOLVED but **cited for a number sourced from
  a NEMA front-matter excerpt, not the paid standard** (`prior-art.md` §7.3).
- **Figure/table:** none.
- **Words / pages:** ~220 / ~0.6 pp.

### C — §III-A replacement (sampling correction) — REPLACES line 104

- **Claim:** Load real and reactive power are scaled per load; generator real power is never
  scaled; the per-load multiplier support is wider than the nominal window in regional mode;
  and a quarter of scenarios carry a generator outage.
- **Numbers, all case118:**

| value | writing-numbers row | note |
|---|---|---|
| `net.gen.p_mw` never assigned | §III-A corrections block | `generate_dataset.py:136-144` touches six fields; `p_mw` is not one. Only reads at `:57` and `:168` |
| per-load P, independent mode: [1.0000, 1.1200], **0.00%** outside | §III-A corrections | 750 bases |
| per-load P, regional mode: [0.9009, 1.2310], **43.91%** outside | §III-A corrections | 750 bases; 22.9% below 1.0 |
| per-load P, all modes: **21.95%** outside | §III-A corrections | denominator must be stated |
| per-load Q, all modes: [0.8156, 1.4083], **56.83%** outside | §III-A corrections | extra pf draw `U(0.9, 1.15)` |
| generator outage share | rows 10 | **0.249259** of converged N-1 rows; 374/1500 bases |
| non-converged decomposition | rows 4, 5 | 45 failures, not 1,545; 1,500 are N-0 base rows |
| total / base / N-1 / converged | rows 1–4 | 280,500 / 1,500 / 279,000 / 278,955 |

- **Citations:** none new.
- **Words / pages:** ~300 / ~0.8 pp (replaces ~180 words, net +0.35 pp).

### D — §V Theory: Why Escalation Has a Floor

- **Number/title:** §V, Theory: why escalation has a floor
- **`\label`:** `\label{sec:theory}`
- **Insertion:** after line 141
- **Claim:** Escalation is the predictive mass in a band of width `q_hat` above the limit, so
  its floor is set by boundary density, and which model is safer depends on how each model's
  overshoot sits relative to its own band width rather than on band width alone.
- **Sub-claim §5.4, per amendment 1, specified against MEASURED values:** The barrier inequality
  is exact within a model and carries no cross-model content.

**THE STATISTIC THIS SECTION USES: the conditional MEAN, `S_mean = E[o | Y < L] / q_hat`.**
This must be stated in the section's own text. The p99 statistic moves the OPPOSITE way for
ridge, so a sentence that does not name its statistic is contradicted by the other figure in the
same artifact. See §7 Q2.

| value | writing-numbers row | result set |
|---|---|---|
| ridge **S_mean** 0.603785 ± 0.075685 → **0.721343 ± 0.065644** — **RISES** | S-ratio rows | case118 → case30-thermal |
| histgb **S_mean** 0.791930 ± 0.074329 → **0.343935 ± 0.061752** — **FALLS** | S-ratio rows | case118 → case30-thermal |
| ridge diff **+0.117558**, larger std 0.075685, **exceeds** | S-ratio rows | — |
| histgb diff **−0.447995**, larger std 0.074329, **exceeds** | S-ratio rows | — |
| within-network std-rule margins on the S_mean ordering | S-ratio rows | case118 2.5×, case30-thermal 5.7× |
| mechanism: ridge barrier ×1.34 vs overshoot ×1.60; histgb barrier ×1.03 vs overshoot ×0.45 | barrier block | both |
| identity gap `\|P(o>q) − (1−cov)\|` = **5.551115123125783e-17** | barrier block | both — **round-off on an identity, not a test of it** |

- **DO NOT WRITE, in any form:** "zero counterexamples in N cases", or any sentence presenting
  the absence of counterexamples to `o ≥ q_hat + d` as an empirical result. **Certify implies
  `pred ≥ 0.94 + q_hat`; violation implies `y < 0.94`; therefore `o = pred − y ≥ q_hat + d`
  necessarily.** The set is empty by construction. **State it as a derivation** — two lines of
  algebra in the section — and do not attach a sample size to it. Presenting it as verification
  is a defect, not a strengthening.
- **Do NOT state** that the tail ratio explains the reversal: `S_p99/q_hat` **FALLS for both
  models** — ridge 6.548389 → 4.390677 (diff −2.157712, larger std 0.572435, exceeds) and histgb
  9.774697 → 5.213065 (diff −4.561632, larger std 0.649338, exceeds). Pre-registered prediction
  P-BH-6 was wrong and is recorded as such.
- **UNWRITABLE AS SHAPED:** any sentence of the form "the S ratio rises/falls across networks",
  "the S ratio moves in direction X", or any single-direction statement about "the S ratio".
  **The two models move in OPPOSITE directions and both moves exceed the std rule.** Respecify
  per model: ridge's S_mean rises, histgb's S_mean falls. See §7 Q1.
- **Citations:** `lei2018` RESOLVED, `vovk2005` RESOLVED, `romano2019` RESOLVED, `barber2021`
  RESOLVED, `tibshirani2019` RESOLVED — all per the `.tex` comment block at lines 289–300, none
  keyed in `prior-art.md`. **See erratum E-A4-8.**
- **Figure:** the escalation-identity figure. Artifact `data/fig_identity.png` +
  `fig_identity.manifest.json` (Schema B, carries `apa_citation`). **APA line: manifest has it,
  the `.tex` does not.**
- **Words / pages:** ~900 / ~2.4 pp including one figure.

### E — Results: the flag branch

- **Number/title:** §VI-2 (after renumbering), The flag branch is not covered by the guarantee
- **`\label`:** `\label{subsec:flag}`
- **Insertion:** after line 227
- **Claim:** The flag decision is invariant to the coverage target because it reads only the
  point prediction, so the conformal guarantee constrains certification only, and false flags
  are never corrected downstream.
- **Numbers, all case118:**

| value | writing-numbers row | note |
|---|---|---|
| deciding line `flag = pred < limit` | flag-branch block | `feasibility/gate_eval.py:20`, no `q_hat` term (`:19` is `certify`, `:18` is `lower`) |
| invariance: `nunique == 1` across all 30 targets, all 10 (model, seed) groups | flag-branch block | |
| flag precision ridge@0.94 | rows 12, 13 | **0.560620** count-pooled / **0.561265** seed-mean — state which |
| flag precision histgb@0.97 | rows 15, 16 | **0.856295** / **0.856372** |
| ceiling ridge | row 14 | **0.691482** count-pooled (**0.692415** seed-mean) |
| ceiling histgb | row 17 | **1.009272** — non-binding, flag rate below the violation base rate |
| false flags | flag-branch block | 6,155.8 (ridge@0.94) vs 76.8 missed; 1,379.4 (histgb@0.97) vs 80.8 |
| false-flag margin | flag-branch block | seed-mean p50 1.77 / 0.95 milli-pu; 89.7% / 97.3% within 5 milli-pu |

- **CANNOT BE COMPUTED, must not be written:** pooled percentiles of false-flag margins — raw
  margins are not stored.
- **Citations:** none new.
- **Words / pages:** ~450 / ~1.2 pp.

### F — Results: non-convergence paragraph

- **Insertion:** after line 235 (inside the boundary-layer subsection, before the Fig. 4 float)
- **Claim:** Forty-five N-1 solves failed to converge, the gate escalates or flags essentially
  all of them, and treating every one as a violation moves the missed rate by less than 0.0001.
- **Numbers, all case118:** 45 failures (row 5); 1,500 base rows excluded by design (row 2);
  0/45 certified ridge@0.94 and 1/225 seed-rows histgb@0.97; missed-rate delta **0.0000 at four
  decimals**, negative for ridge; all 45 are transformer outages on 3 elements (trafo 0/7/6 →
  IEEE 1/8/7), counts 37/7/1.
- **Citations:** none.
- **Words / pages:** ~200 / ~0.5 pp.

### G — Discussion: break-even

- **Insertion:** after line 256
- **Claim:** Equation 2 charges escalated solves but not the solves that built the dataset, and
  the amortisation threshold is stated here.
- **Numbers:** from `data/break_even.json` — **NOT YET IN `writing-numbers.md`. Add rows first.**
  Also `data/parallel_speedup.json` for the parallelism-invariance point. Dataset cost:
  280,500 solves at `ms_solver` 9.14, read from `data/solve_time.json` (`ms_solver`).
  **No `solve_time` row exists in `writing-numbers.md` either — the break-even rows AND the
  solver-timing row are both still missing and must be added before drafting.**
- **Citations:** `manoharan2026` RESOLVED (the criticism this paragraph answers is aimed at the
  GNN work, not Manoharan — check the target before drafting).
- **Words / pages:** ~250 / ~0.7 pp.

### H — Discussion: drift

- **Insertion:** after line 258
- **Claim, per amendment 2, specified against MEASURED values:** Calibrating on benign base
  cases and screening marginal ones costs ridge about ten coverage points while histgb is
  unaffected, so marginal coverage does not transfer conditionally for the linear model.
- **Numbers, all case118:**

**2C IS A DRIFT FINDING, NOT A CONFOUND.** Cell (c) holds stratum difficulty fixed and removes
only the calibration/test mismatch; ridge still drops, and the drop exceeds its std by 3.3×.

| value | writing-numbers row | note |
|---|---|---|
| ridge (a) SHIFTED coverage @0.90 | 2C rows | **0.7952977736840497 ± 0.017998553298487808** |
| ridge (b) BENIGN CONTROL @0.90 | 2C rows | **0.8963930839821412 ± 0.011400530217031263** |
| ridge (c) **IN-DISTRIBUTION MARGINAL** @0.90 | 2C rows | **0.8844348119083406 ± 0.026846519782127615** |
| gap (b) − (a) | derived | **+0.10109531029809142**, larger std 0.017999 → **EXCEEDS, 5.6×** |
| gap (c) − (a) | derived | **+0.089137038224291**, larger std 0.026847 → **EXCEEDS, 3.3×** |
| histgb coverage @0.90, both comparisons | 2C rows | gap 0.002868 vs std 0.015195 → **FAILS the std rule; state as indistinguishable from zero** |
| **histgb escalation, the model contrast to use** | 2C rows | **0.028 benign → 0.591 in-distribution marginal** |
| benign stratum violation rate | **`2C benign stratum violation rate`** | **0.15373696096354447** over 139,485 rows — **SINGLE-PATH**, cite `data/dataset.parquet` |
| marginal stratum violation rate | **`2C marginal stratum violation rate`** | **0.19577686957768695** over 139,470 rows — **SINGLE-PATH**, cite `data/dataset.parquet` |
| median split point | 2C rows | `n0_min_vm` = 0.9433575252264039 |

- **The model contrast is best stated on ESCALATION, not coverage.** histgb has no coverage gap
  in either comparison, so a coverage-based contrast has nothing to say about it. Its stratum
  sensitivity appears as escalation 0.028 → 0.591.
- **SINGLE-PATH resolved:** the two stratum violation rates now have rows in
  `notes/writing-numbers.md` citing `data/dataset.parquet` with the derivation and row counts.
  `data/drift_n0_stratum_long.parquet` has no violation-rate field. **This entry is USABLE AS
  STANDS** now that those rows exist.
| 2D | 2D rows | histgb line→trafo 0.022810 vs control −0.001425; ridge immune (0.003776 vs 0.005931) |
| 2E | 2E rows | ESS 0.79–0.82; realized shift +0.0046 to +0.0054; **under-powered by construction** — do NOT quote a window width; the "7.7 pp" figure is WITHDRAWN (it appears only in `notes/ai-prompt-log.md` prose; the artifact-derivable base `agg_loading` range is **10.96 pp**) |

- **Confounds that must be stated:** gen-outage prevalence differs **+4.8 pp** between strata
  (0.2253 vs 0.2733); argmin-bus composition shifts toward IEEE 76/53/107; `agg_loading` differs
  at p = 0.012 but by 0.13σ.
- **Do NOT claim** the strata differ in load level: `corr(n0_min_vm, agg_loading)` = **−0.0724**.
- **Citations:** `tibshirani2019` RESOLVED (weighted conformal, for 2E).
- **Words / pages:** ~500 / ~1.3 pp.

### I — Discussion: case30-thermal replacement — REPLACES line 260

- **Claim, per amendments 4 and 5:** On a thermally feasible regeneration of the 30-bus network
  the boundary mass is an order of magnitude below the 118-bus value and the escalation floor
  falls with it, at a coverage target whose location is not resolved at five seeds.
- **Numbers — EVERY ROW NAMES ITS RESULT SET (amendment 5):**

| value | result set | writing-numbers row |
|---|---|---|
| boundary mass **56.86%** | case118 | row 7 |
| boundary mass **7.0862%** | **case30-thermal** | row 21 |
| violation rate **17.4756%** | case118 | row 6 |
| violation rate **15.3967%** | **case30-thermal** | row 20 |
| histgb escalation **5.84% ± 1.25**, speedup **17.91× ± 3.71** at target **0.97** | **case30-thermal** | S6 block — **use the decidable target, not 0.96** |
| N-0 acceptance **18.63%**, range **[0.87, 0.99]** | **case30-thermal** | rows 47–49 |
| acceptance **exactly 0.000** at every `lo` from 1.00 down to 0.94 | **case30-thermal** | row 46 |
| N-1 loading above 100%: **0.214846** | **case30-thermal** | row 50 |
| N-1 loading above 100%: **0.9989105691** (full population) | **case30-published** | row 51 corrected |

- **Amendment 4, mandatory:** the crossing location is **INDETERMINATE**. histgb at 0.96 sits
  **0.41 std** from the 0.01 threshold with **2 of 5 seeds** below it; the decidable target is
  0.97 (**1.20 std**, 5/5 seeds). Ridge is equally indeterminate between 0.97 and 0.98 (its
  exclusion of 0.97 rests on **0.22 std**). **State the indeterminacy; do not quote 0.96 as
  resolved.**
- **The superseded figures at line 260** are all **case30-published**: 20.0%, 28.8%,
  8.96 ± 0.91%, 11.27 ± 1.02×. Line 72 (abstract) carries the same four. Both are labelled only
  "the IEEE 30-bus system" — **ambiguous under amendment 5 and must be relabelled**.
- **Also at line 260, unrelated to case30:** the ANSI 0.917 pu provenance defect; "Only 86 of
  the 1,500 base cases are above 0.95 pu, while all sit above 0.94 pu" is **circular** — the
  second clause is the acceptance criterion (`generate_dataset.py:256`), 46.18% of draws
  rejected, min `n0_min_vm` = 0.94000004.
- **Words / pages:** ~450 / ~1.2 pp (replaces ~190 words, net +0.7 pp).

---

## 3. AMENDMENT 3 — the 2F concentration claim is DROPPED

**No layout entry is specified for 2F concentration.** Six scalars are SINGLE-PATH with no
per-seed counterpart in `data/qlimit_class.json`: `deep_elements`, `n_distinct_elements`,
`top_element_share`, `deep_argmin_buses_ieee`, `n_distinct_argmin_buses`, `top_bus_share`.

**What may be kept, and only in Discussion as support for the existing line-262 caution:** the
negative result — deep misses are not homogeneous and no discriminating pre-outage signature was
found. Supporting value: the off-setpoint-generator indicator is present in **1.000000** of
deep-miss rows AND **1.000000** of all 278,955 converged N-1 rows (baseline mean 20.799 vs
21.328 ridge / 21.453 histgb).

**Differences, recomputed from `data/qlimit_class.json` alone** (pairing: pooled deep-miss mean
over the 5-seed union, minus the row-level baseline over all 278,955 converged N-1 rows):
ridge **0.528292**, histgb **0.653536**.

**The std comparison is NOT PRINTABLE from this artifact — `data/qlimit_class.json` stores no
std of any kind**, and the deep-miss pools are 5-split unions over the same 1,500 scenarios, so
they are not independent observations. The earlier figures 0.7285 / 0.973412 / 2.40071 are
WITHDRAWN: 0.7285 was a difference against a per-seed-mean deep figure (21.5278) that appears in
no data artifact, and it does not correspond to either mean quoted above.

**The verdict is unchanged and survives:** the comparison **fails the project's std rule** — it
is unevaluable, since no std exists in the artifact, and every candidate difference (0.528292,
0.653536, or the withdrawn 0.7285) is smaller than any std that has been quoted for it.
**Do not state any percentage-concentration figure.**

---

## 4. PAGE BUDGET

| item | pages |
|---|---|
| current body (Introduction → Conclusion, excluding front matter and bibliography) | ~11.0 |
| A Related Work | +1.6 |
| B Background grounding | +0.6 |
| C §III-A replacement (net) | +0.35 |
| D §V Theory | +2.4 |
| E flag branch | +1.2 |
| F non-convergence | +0.5 |
| G break-even | +0.7 |
| H drift | +1.3 |
| I case30-thermal (net) | +0.7 |
| existing figures 1–4 | (already counted) |
| new figures: identity (D) | +0.0 (counted in D) |
| **projected total** | **~20.45 pp** |

**RE-REPORTED 2026-08-19 after the S8/S9 amendments.** Net change **+0.10 pp**: §2-D gains the
explicit statistic declaration and the two-line derivation replacing the withdrawn
counterexample claim (+0.15 pp), §2-H gains the third coverage cell and the escalation contrast
(+0.10 pp), and the withdrawn "zero counterexamples in 4.6M cases" sentence is removed
(−0.15 pp).

**Against a hard 20-page cap with appendices counted and front matter excluded, this is over by
~0.45 pp.** Three levers, in order of least damage: consolidate Fig. 2 and Fig. 4 into one
two-panel float (−0.4 pp); cut the Related Work comparison table to prose-with-citations
(−0.4 pp); trim §VI Results, which currently carries the three original subsections plus two
new ones. **Decide before drafting D, not after.**

**Page estimates are planning figures, not measurements. NOTHING HERE HAS BEEN COMPILED** — no
TeX toolchain is installed on this machine (`pdflatex`, `xelatex` and `latexmk` are all absent
from PATH, re-verified 2026-08-19; `/usr/local/texlive` exists but is EMPTY and `/Library/TeX`
does not exist). The 20.45 figure is an estimate from word counts and float
sizes, not a page count from a rendered PDF, and the overrun could be larger or smaller once
compiled. **Do not treat the 0.45 pp overrun as measured.**

---

## 5. LAYOUT CLAIMS MARKED NO SOURCE

| claim | status |
|---|---|
| GNN recall figure for Related Work (A) | **SOURCE EXISTS, NO BIBKEY.** `notes/lit/notes/Graph Neural Networks for Fast Contingency Analysis of Power Systems.md` §4 carries under-/over-voltage recall values, flagged approximate (Fig. 7 bar-label transcription, not prose-stated). No data artifact carries it, and **the paper has no bibkey in `report/paper_current_STS.tex`** — one must be added before it is cited |
| "around 14%" bin share, manuscript line 235 | **NOT NO SOURCE — reproduces at 14.06%.** Max 0.001-pu-wide bin over converged N-1 rows, `data/dataset.parquet`. Add a `writing-numbers.md` row before use |
| S ratios 0.604→0.219 / 0.443→0.482 (brief) | **NO SOURCE** — measured values differ and invert |
| "4.6M cases" (brief) | **NO SOURCE** — populations are 19,625 and 6,128,100 |
| stratum violation rates 24.3% / 4.7% (brief) | **NO SOURCE** — measured 15.3737% / 19.5777% |
| in-distribution marginal coverage 0.7970 (brief) | **NO SOURCE** — measured 0.884435 |
| thermal full-population share 0.9927 (brief) | **NO SOURCE** — measured 0.9989105691 |
| break-even figures for G | **NOT YET IN `writing-numbers.md`** — add rows before drafting |
| stratum violation rates 0.15373696096354447 / 0.19577686957768695 | **SINGLE-PATH — RESOLVED.** Rows added to `writing-numbers.md` citing `data/dataset.parquet`; the drift artifact has no such field |
| home ZIP for the PDF filename (R14) | **NO SOURCE** — not in this repository |

---

## 6. ERRATA THE AUDIT IMPLIES

Each is a defect in the manuscript or its supporting record, with file:line evidence. **None is
applied.**

| id | defect | evidence |
|---|---|---|
| **E-A4-1** | III-A claims generator base values are scaled by the 1.0–1.12 multiplier. They are never scaled. | `report/paper_current_STS.tex:104` vs `feasibility/generate_dataset.py:136-144` (six fields, `p_mw` absent) and `:57`, `:168` (only reads). All 53 `genp_*` columns `nunique==1`, `std=0`. |
| **E-A4-2** | III-A states the multiplier range is 1.0–1.12. True only for load P in independent mode. | `:104` vs `data/dataset.parquet`: regional per-load P [0.9009, 1.2310], **43.91%** outside; all-mode Q [0.8156, 1.4083], **56.83%** outside. Cause `generate_dataset.py:110-112`, `REG_JITTER = 0.10`. |
| **E-A4-3** | III-A "the remainder failing to converge" implies 1,545 failures. | `:104` vs `data/dataset.parquet`: **45** failures; the other 1,500 are N-0 base rows, all converged. |
| **E-A4-4** | Line 262 "we did not test N-2 cases". | `:262` vs `data/sampling_audit.json`: **24.93%** of converged N-1 rows (69,532/278,955) carry a generator outage in addition to the branch outage. `P_GEN_OUT = 0.30` at `generate_dataset.py:28`, drawn at `:128`. |
| **E-A4-5** | IV-B title and its supporting sentence assert a general model-safety ordering. | `:229`, `:231` vs three result sets: holds on case118 (ridge lower at all 30 targets); **absent** on case30-published (1.49±0.53 vs 1.47±0.20 at 0.90, 0.03 pp inside one sigma); **inverted** on case30-thermal (ridge 6.087% vs histgb 2.226%). |
| **E-A4-6** | Both "sub-1%" crossings fail at one sigma. | `:72`, `:209`, `:215`, `:250` vs Table II `:186`, `:196`: ridge@0.94 0.79+0.21 = **1.00** exactly; histgb@0.97 0.83+0.24 = **1.07**. First robustly sub-1% targets are ridge 0.95 and histgb 0.98, which change the headline to 67.9%/1.48× and 72.0%/1.39×. |
| **E-A4-7** | ANSI 0.917 pu cited to the standard, sourced from a NEMA front-matter excerpt. | `:260` vs `notes/prior-art.md` §7.3. |
| **E-A4-8** | `nerc` has no entry of any kind in `notes/prior-art.md`. | `grep -ni 'nerc\|TPL-001' notes/prior-art.md` → 0 hits. The `.tex` comment at `:300` says so itself: "ADD THE VERIFICATION DATE HERE". |
| **E-A4-9** | Fig. 1 embeds the M1-sized schematic. | `:138` `data/gate_schematic_v2.png`, sized from M1 `q_hat = 0.002557109746803765` (`data/tradeoff_curve.json`), against the M2 value 0.002291 the results use. `data/gate_schematic_v3.png` is the M2-consistent version. `notes/erratum.md` E1 already records this. |
| **E-A4-10** | Line 92 "the only active constraint is the lower voltage limit". | vs `data/thermal_check.json`: **73.14%** of converged N-1 rows and **73.40%** of N-0 base rows exceed 1.05 pu on case118. |
| **E-A4-11** | Line 260's 0.94 pu justification is circular. | "all sit above 0.94 pu" is the acceptance criterion at `generate_dataset.py:256`; 46.18% of draws rejected; min `n0_min_vm` = 0.94000004. |
| **E-A4-12** | Acknowledgments assert all numbers came from committed tested code at the cited URL. | `:287` cites `github.com/rajsaha-blip/…` = `upstream`, whose HEAD is **990c3c5** (2026-08-03). Local and `origin` are at **03e1136**. `data/*.parquet` were untracked until recently and `notes/` is gitignored entirely. |
| **E-A4-13** | Zero subsections carry `\label{}`, and three source comments name IEEEtran-style subsection ids the document cannot print. | `:134` "III-D", `:220` "IV-B", `:239` "IV-C"; `\thesubsection` renders `IV.1`/`IV.2`/`IV.3` under `article` with `\thesection` Romanized. |
| **E-A4-14** | Abstract and line 260 pair a case118 **ridge** headline with a case30 **histgb** headline without naming either family. | `:72`, `:260` vs `data/case30_frozen.json`: 11.27× is histgb@0.93; ridge on case30-published crosses at 0.92 with 2.98×. |
| **E-A4-15** | Two voice families in one document. | `we`×17, `our`×5, `us`×1 across Abstract→Discussion; `the authors` at `:287`. **Zero instances of "I" or "my"** — the three grep hits are inside LaTeX comments. |
| **E-A4-16** | `notes/erratum.md` E1 cites `paper_current.tex`, a path that no longer exists. | The file is now `paper_current_URTC_20260808.tex`; E1's line number 112 is still correct. E1 also states no `urtc-submission` tag exists; it does, at `23bc760`. |

---

## 7. AMENDMENT TO §2-D (§V Theory), from paired adjudication S8

S8 confirmed every S_mean value and both directions from an independently anchored raw
re-derivation (case118 and case30-thermal anchors both exact at 0.0). It also raised two
qualifications not anticipated when §2-D was written. **§2-D's number table stands unchanged;
the following constrains how those numbers may be described.**

**Q1 — there is no single direction for "the S ratio".** The two models move in opposite
directions and both moves survive the std rule:

| model | case118 → case30-thermal | difference | larger std | direction |
|---|---|---|---|---|
| ridge | 0.603785 → 0.721343 | +0.117558 | 0.075685 | **RISES** |
| histgb | 0.791930 → 0.343935 | −0.447995 | 0.074329 | **FALLS** |

Any sentence of the form "the S ratio moves in direction X across networks" is unwritable. The
statement must be per model.

**Q2 — the direction is statistic-dependent, and for ridge the two statistics disagree.**

| statistic | ridge | histgb |
|---|---|---|
| S_mean = E[o \| viol] / q_hat | 0.603785 → 0.721343 (**RISES**) | 0.791930 → 0.343935 (FALLS) |
| S_p99 = p99(o \| viol) / q_hat | 6.548389 → 4.390677 (**FALLS**) | 9.774697 → 5.213065 (FALLS) |

Both S_p99 moves exceed their larger stds (0.572435 and 0.649338). So ridge's mean overshoot
rises relative to its barrier while its 99th percentile falls relative to its barrier.

**§5.4 must name the statistic it uses.** The mechanism specified in §2-D uses the conditional
MEAN. If that is not stated explicitly, the claim is contradicted by the tail statistic in the
same artifact.

**Q3 — the counterexample count is zero BY CONSTRUCTION, not empirically.** S8 agent B: certify
implies pred ≥ 0.94 + q_hat, and violation implies y < 0.94, so o = pred − y ≥ q_hat + d and the
set is empty by definition. **Do not present 0 counterexamples as an empirical finding.**

## 8. AMENDMENT TO §2-H (Discussion drift), from paired adjudication S9

S9 settled the deciding cell that §0.3 flagged. **The confound reading is refuted, not merely
unsupported.**

| cell | ridge coverage @0.90 | per-seed |
|---|---|---|
| (a) shifted: cal benign → test marginal | **0.7952977736840497 ± 0.017998553298487808** | .803610 / .822659 / .798313 / .780672 / .771236 |
| (b) benign control | 0.8963930839821412 ± 0.011400530217031263 | .884050 / .894713 / .900772 / .915861 / .886570 |
| (c) **in-distribution marginal**: cal marginal → test marginal | **0.8844348119083406 ± 0.026846519782127615** | .918392 / .871224 / .877883 / .844685 / .909990 |

| gap | mean | larger std | verdict |
|---|---|---|---|
| (b) − (a) | +0.10109531029809142 | 0.017999 | **EXCEEDS, 5.6×** |
| (c) − (a) | **+0.089137038224291** | 0.026847 | **EXCEEDS, 3.3×** |

Cell (c) holds the stratum difficulty fixed and removes only the mismatch. It sits near nominal.
**Ridge's drop is calibration/test stratum MISMATCH — drift — not stratum difficulty.** The
claim specified in §2-H is therefore supported as written.

**histgb has no coverage gap in either comparison** (both under one std). Its stratum
sensitivity appears in escalation: **0.028 benign vs 0.591 in-distribution marginal**. If the
paragraph contrasts the models, that is the axis to contrast on.

**Stratum violation rates — SINGLE-PATH, cite `data/dataset.parquet` not the drift artifact:**

| stratum | violation rate | rows |
|---|---|---|
| benign | **0.15373696096354447** | 21,444 / 139,485 |
| marginal | **0.19577686957768695** | 27,305 / 139,470 |

`drift_n0_stratum_long.parquet` contains no violation-rate field. **A `writing-numbers.md` row
must be added citing `data/dataset.parquet` before these enter the draft.**
