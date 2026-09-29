# Round-1 panel — Non-specialist doctoral scientist (STS scholar-stage juror)

Reviewer stance: an experimental scientist outside the field, reading at a judging table with limited
time, with working statistics but no power systems and no conformal prediction. I did not audit code.
Sources: `notes/panels/round1_paper_text.txt`, the PDF (`paper_v39.pdf`, all figure pages viewed),
`report/paper_current_STS.tex` (line numbers below), and a few `data/` JSONs to check how things read.

## 0. Page-1 test (title + abstract + first page of Introduction), in my own words

- **Question:** can a cheap machine-learning predictor, given a statistically calibrated safety margin,
  stand in for most of the slow grid simulations that check whether losing one power line or
  transformer pushes some voltage too low?
- **Answer:** only partly, on the 118-node test grid. To miss fewer than about 1% of the dangerous cases
  you still have to run the slow simulation on about two-thirds of cases, which gives roughly a 1.6x
  speed-up. On a smaller 30-node grid only about 6% of cases went to the simulation. The title
  suggests the difference comes from how many cases sit just above the voltage limit.
- **Why it matters:** an operator could know in advance whether this kind of screening is worth
  deploying on a given grid.
- **Could I do this?** PARTLY. I could pull the numbers out, but:
  (a) the abstract never says in words WHY the 118-bus speed-up collapses. The mechanism ("boundary
  mass") is only in the title, and the phrase is never defined anywhere in the paper;
  (b) "coverage", "conformal", "surrogate", "escalation" and "per-unit" block the abstract for an
  outsider ("per-unit" is defined on p.2);
  (c) the 30-bus sentence gives an escalation rate but no missed rate and no speed-up, so I could not
  tell whether 30-bus was a success;
  (d) no sentence anywhere states the research question or hypothesis. I had to reconstruct it.

## 1. Rubric (from the point of view of an intelligent scientist outside the field)

| Criterion | Score | One sentence |
|---|---|---|
| Originality | 6 | The trade-off result and the "near-limit pile-up" explanation read as the student's own, but the intro's list of how this work differs is weak (one of the three items is a scope restriction), so an outsider cannot see what is new. |
| Rigor | 7 | Five splits with ± everywhere, a self-found data bug, hash-locked predictions and stated exclusions are convincing; weaker are a figure caption that cites error bars the figure does not draw, a baseline row that looks perfect, and a data-filter confound the paper does not address. |
| Significance | 5 | The operator-facing message (about 1.6x speed-up at about 1% missed) is clear and useful, but the general claim rests on two networks and a cross-network predictor with ~47% mean relative error, and the paper never states the 30-bus speed-up, its most striking contrast. |
| Clarity | 4 | Heavy undefined jargon (about 60 blocking terms, table in NS-13), "coverage" used in three senses, no stated question, and whole subsections (Theory, cross-network, ablation) that a non-specialist cannot follow or connect to the conclusion. |
| Student potential | 8 | Finding the generator bug by noticing an impossible inverted requirement, reporting an unfavorable headline plainly, and locking predictions before testing are what a judge hopes to see. |

## 2. Findings

Counts: **FATAL 1, MAJOR 15, MINOR 10.**

### NS-01 — FATAL (STS rule, conditional) — Acknowledgments omit required disclosures
- Anchor: "This paper has been written as part of" (l.393).
- Evidence (Reported): `notes/sts-constraints.yaml` R20 quotes GUIDE2027: "full disclosure of any research
  or person that has influenced the applicant's work is required". The same row notes that BU RISE was
  PAID, that Kalita and Pinsky taught the material, and that AI use is logged. R04 quotes RULES2027 App. 4:
  AI-generated code is acceptable "only with explicit citation stating which portions", and grammar-level
  AI help "Must be credited". The current Acknowledgments names no instructor, does not say the program is
  fee-based, and says nothing about AI tools. R04's own note says an earlier Acknowledgments carried
  an AI line. That line is gone now.
- Why a judge cares: if the rules require disclosure and it turns up later, the paper loses the judge's
  trust. This finding is FATAL only if these disclosures appear nowhere else in the application. If the
  application form covers them, it drops to MAJOR (the report still under-credits).
- Fix (content): state the fee-based program, name the instructors/TFs and anyone who read a draft, and
  say which portions of code used AI and how, per R04/R20. Confirm where STS expects each disclosure to go.

### NS-02 — MAJOR — "Coverage" carries three meanings, and its link to "missed" is never explained
- Anchors: "converts the residuals from the calibration dataset into a coverage guarantee" (l.128);
  "(where coverage is the acceptance rate)" (l.231); "at a coverage of 0.96, the linear model" (l.292);
  Fig. 2 axis "target coverage" vs its caption's "safety target" (l.281); Table 2 "Target" vs "Cov." (l.246).
- Problem: sense 1 (l.128) = probability the true voltage is at or above the band's lower edge. Sense 2
  (l.231) = selective-prediction coverage = share of cases decided without the solver, which is about
  1 − escalation. Sense 3 = the knob ("target"), also called "safety target" (Fig. 2 caption) and
  "coverage" (l.292). An outsider reading "90% coverage" in the abstract then naturally expects about 10%
  of violations to be missed, and gets 4.72%. No sentence explains why per-case coverage and the
  missed-violation rate differ (a miss counts only when a case is certified). This is the paper's
  central number, and the lay reader cannot reconcile it.
- Fix: use one word per concept throughout, including in figure axes and captions. Add one explanation
  of how the target, empirical coverage, and missed-violation rate relate.

### NS-03 — MAJOR — The first page never states the question, the answer's mechanism, or what "boundary mass" is
- Anchors: title "Throughput Limits Set by Boundary Mass" (l.63); abstract "These results allow operators to
  make an informed decision" (l.81); intro "My work stands out from these papers" (l.101).
- Evidence: `grep -n -i "boundary mass\|throughput\|hypothes"` on the .tex finds "boundary mass" only in
  the title and once in IV.4 (l.353, as a predictor input). "Throughput" appears only in the title and the
  Table 2 caption. "Hypothesis" appears nowhere. The abstract juxtaposes 7.09% vs 56.86% but never says
  "because". The 30-bus sentence gives escalation only.
- Fix: the abstract and intro need an explicit question, the answer, and the causal claim in plain
  words. Define the boundary-mass quantity once, where it first appears. Give the 30-bus missed rate and
  speed-up next to the 118-bus pair so the contrast can be read at a glance (see NS-12).

### NS-04 — MAJOR — The train-mean row looks like the best model in Table 1; flagged false alarms are never counted
- Anchor: Table 1 row "train mean & 6.7±0.2 & −0.00±0.00 & 0.0±0.0 & 0.00±0.00" (l.216).
- Evidence (VERIFIED): `data/screener_metrics.json` train_mean records: escalation 0.0, missed_viol 0.0,
  n_escalated 0 on every seed. The mean converged N-1 min voltage is 0.93983 pu, below L = 0.94
  (`.venv/bin/python` over `data/dataset.parquet`, filter outaged_type != 'none' & converged: mean
  0.9398258, violation share 0.17476). So the constant prediction is below the limit and the gate FLAGS
  every case: about 82.5% of all contingencies are false alarms. The dagger footnote only says it "never
  calls the solver".
- Why it matters to a lay judge: the only row with 0% escalation and 0% misses looks perfect. More
  broadly, no table reports how many safe cases get flagged, and Eq. 2 treats flagged cases as free, so a
  model could buy speed-up by flagging more. The paper never says what happens to a flagged case
  operationally.
- Fix: say in the caption that train-mean flags everything. Report a false-flag (false-alarm) rate for
  every model, and state what flagging costs the operator.

### NS-05 — MAJOR — "The faster model is not the safer one" compares at equal knob setting, not at equal speed
- Anchor: "the more accurate model is not safer at any point in the coverage axis" (l.292); heading (l.290).
- Evidence (VERIFIED, `data/tradeoff_curve_v2.json`): ridge @0.94 esc 64.3±2.8, missed 0.79±0.21;
  histgb @0.97 esc 63.7±5.1, missed 0.83±0.24. At matched escalation (matched speed) the two models are
  indistinguishable under the std rule. The 0.96 comparison (0.14% vs 1.36%) pits ridge at 71.4%
  escalation against histgb at 57.0%, so ridge is slower there. The heading says "faster" but the
  sentence says "more accurate", which are two different properties.
- How a judge could read it: as choosing the comparison point that favours the story. The paper's own
  conclusion ("almost two-thirds ... 1.6") already implies the tie.
- Fix: state the comparison at equal escalation or equal missed rate, and scope the heading to match.

### NS-06 — MAJOR — Is the pile-up at 0.94 a property of the grid or of the data filter? Not addressed
- Anchors: "This implies that clustering is an inherent characteristic of the network and the sampling
  process" (l.121); "This escalation floor is set by how the distribution" (l.365).
- Evidence: the paper says base cases were KEPT only if pre-outage min voltage > 0.94 (l.119), and only 86
  of 1,500 bases exceed 0.95 (l.365). The first question an outsider asks is "if every starting state
  sits between 0.94 and 0.96, isn't a pile-up just above 0.94 after an outage expected by
  construction?" (Reported) `data/unconditioned_base.json`: without the N-0 filter, boundary mass is
  28.83% vs 56.86% with it. The base-case median minimum voltage is 0.9434 and the minimum is 0.94.
  The paper does not report or discuss this. "Network and sampling process" folds together the two
  causes the reader needs separated.
- Fix: say how much of the boundary mass comes from the acceptance filter and how much from the network,
  and scope "inherent" to match.

### NS-07 — MAJOR — The conclusion claims more than the evidence, and the title and conclusion disagree
- Anchors: title "Limits Set by Boundary Mass" (l.63); "though the 30-bus result shows that this depends on
  data distribution" (l.388); "Future work involves ... to determine whether speedup depends on the amount
  of data that lies near the threshold" (l.388); "the mean relative error was 0.4726 for predictor A" (l.353).
- Problem: the title asserts the cause. The conclusion lists that same cause as an open question. The
  only multi-network test (IV.4) predicts escalation with ~47% mean relative error, and the paper never
  says whether that is good or bad. "Shows" rests on one 118-vs-30 comparison, where the networks differ
  in size, topology and load window (0.87–0.99 vs 1.0–1.12), not only in boundary mass.
- Fix: make the title, results and conclusion state the same strength of claim. Say what a 0.47
  relative error means for the "set by boundary mass" claim. Name the other differences between the two
  networks.

### NS-08 — MAJOR — Fig. 2 caption and text cite error bars that the figure does not draw
- Anchors: "although the error bars still reach up to about 1.0–1.07%, as Fig. 2 shows" (l.231); Fig. 2
  caption "the error bars still reaching slightly above 1%" (l.281).
- Evidence (VERIFIED, visual): `data/tradeoff_hero_col_v2.png` shows four mean curves, a 1% guide line
  and two vertical markers. There are no error bars or shaded bands.
- Fix: draw the ±1 std spread, or stop pointing to the figure for it.

### NS-09 — MAJOR — Fig. 5 labels contradict its caption and the text (bus 75 vs 76, etc.)
- Anchor: caption "The three dominant buses are 76, 53, and 107" (l.339); text (l.314).
- Evidence (VERIFIED, visual PDF p.11; `data/unconditioned_base.json` critical_bus_top5 = 75, 52, 106, 0,
  20): the in-figure labels read "bus 75 (27%)", "bus 52 (17%)", "bus 106 (9%)", "bus 0 (8%)",
  "bus 20 (4%)". A judge reads "76" in the caption and "75" in the figure and concludes one is wrong. (This
  is the 0-/1-based naming split, but the reader is never told.) The internal title, footnote and
  colour-bar text are too small to read at print size. Buses 0 and 20 are labelled but never mentioned.
- Fix: use one numbering convention inside the figure and the caption. Make the internal text legible,
  and say why the figure matters to the escalation argument (at present it is referenced once and not
  used).

### NS-10 — MAJOR — Section IV.4 (cross-network) is not introduced, is miscounted, and reads as hiding results
- Anchors: "I used non-overlapping calibration and testing data" (l.353); "I tested five networks in
  total" (l.355); "I only report the average errors" (l.355); "under this locked tes" (l.353, typo).
- Problems: (a) The section starts with no statement of what is predicted, why, or on which networks;
  the three networks are named only at the end. (b) "Five networks in total" conflicts with the paper
  also using case118 and case30, which makes seven. (c) "9 coverage targets" conflicts with Table 2's
  six. (d) ρ is described only as "how crowded the voltages are just above the limit", with no
  definition or units. Predictor B's "trend line" is undefined. (e) "I only report the average errors"
  invites the reading "the per-network results were bad". (f) Reasons for dropping case57 use "load
  multiplier 0.0" (zero load) while claiming "realistic conditions".
- Fix: open with the purpose and the networks. Reconcile the network count and the target count.
  Define ρ and predictor B. Give per-network errors, or explain why only averages were pre-registered.

### NS-11 — MAJOR — The 0.95 pu paragraph's logic runs backwards for a reader
- Anchor: "I use 0.94 pu as a conservative choice. Only 86 of the 1,500" (l.365).
- Problem: to an outsider a HIGHER limit (0.95) is the more conservative one. The next sentence reports an
  escalation of 1.38% (low) and says "it finds everything hazardous". That only makes sense if nearly all
  cases are FLAGGED, which the text never says. The coverage target (0.90 per `data/escalation_at_095.json`,
  Reported) is not stated, and only ridge is quoted although histgb is also in the file.
- Fix: say what "conservative" means here. Say that at 0.95 most cases are flagged, give the operating
  target, and quote both models.

### NS-12 — MAJOR — The strongest contrast is buried, and part of it is missing
- Anchors: "which is discussed in Section V" (l.119); "The gradient-boosted model with a coverage target of
  0.97 gives 5.84" (l.365).
- Evidence (VERIFIED, `data/case30_thermal/case30_thermal_frozen.json`, histgb @0.97 over 5 seeds): esc
  5.84±1.25%, missed 0.76±0.20%, net speed-up 17.9±3.7. The speed-up is never stated in the paper,
  although it is the single most persuasive number against 1.58x on case118. The abstract's 30-bus
  result appears only in Discussion/limitations, not in Results. Section III.1 promises that the
  published 30-bus system "is discussed in Section V", but Section V gives no published-30-bus numbers.
  (Reported) `data/case30_frozen.json` holds them (boundary mass 20.01%, histgb esc ~7% at 0.90). A
  reader may think a result was dropped.
- Fix: move the 30-bus result into Results, with the same four metrics as 118. Either report the
  published-30 run or remove the promise.

### NS-13 — MAJOR — Blocking terms (jargon, symbols, acronyms)
Column "Def?" = defined before (or at) first use; "Usable?" = could an outsider work with the definition.

| Term / symbol | First appears | Def? | Usable? |
|---|---|---|---|
| N-1 | title l.63, abstract l.81 | no (l.97) | yes, once reached |
| contingency / post-contingency | title, l.81 | no (implied l.111) | partly |
| conformal, split-conformal, conformal-gated | title, l.81 | partly l.128 | no, "conformal" itself never explained |
| surrogate | title, l.81 | never explicitly | inferable from "fast approximation" l.99 |
| boundary mass | title | never | no |
| throughput | title | never | no |
| AC power flow / solver | l.81 | l.97 "physics calculation"; AC never expanded | partly |
| DC model | l.81 | expanded, but not how it differs | no |
| per-unit (pu) | l.81 | l.107 | yes, good |
| ridge regression; standardized inputs | l.81, l.124 | name only | no |
| gradient-boosted / histogram-based ... ensemble | l.81, l.124 | name only | no |
| histgb | l.147 (text) | only in Table 1 caption l.208 | late |
| coverage (3 senses) | l.81 | l.128, l.231 | no (NS-02) |
| escalate / flag / certify | l.81 | l.139-141 | yes |
| case118 | l.81 | never tied to "IEEE 118-bus" | inferable |
| [0.94, 0.945) notation | l.81 | no | scientists yes |
| thermally feasible / thermal loading / line loading % | l.81, l.107 | partly l.119 | partly |
| bus | l.107 | l.111 (after use) | yes |
| N-0, base case | l.107 | yes | yes |
| MVA | l.107 | no | no |
| reactive power (limits), power factor | l.111, l.119 | no | no |
| slack | l.119 | no | no |
| Independent mode / Regional mode | l.119 | never | no |
| "target range" 1.0–1.12 | l.119 | no | no |
| voltage set point, generator bus | l.121 | no | no |
| "inverting the escalation versus band width relation" | l.121 | no | no |
| "variables" (= hyperparameters) | l.124 | inconsistent with l.373 | confusing |
| calibration / test split | l.124 | yes | yes |
| persistence, training mean | l.124 | briefly | yes |
| q̂ | l.124 | before formal definition at l.128 | partly |
| residuals, quantile, finite-sample rank approach | l.128 | no | scientists partly |
| overshoot | l.128 | yes | yes |
| p̂, L | l.130, l.136 | yes | yes |
| y | l.175 | NEVER defined (true min voltage) | guess |
| Y in Fig. 3 axis "d = 0.94 − Y" | Fig. 3 | no; differs from y | no |
| q̂@0.90 (Fig. 3) | Fig. 3 | no | guess |
| 1{·} indicator | l.170 | no | no |
| E[· \| ·] | l.186 | no | scientists yes |
| S_mean | l.186 | yes, but no direction or use | no (NS-15) |
| n, t_solve, t_surr, n_esc | l.145 | yes | yes |
| "calibrated" | l.199 | no | partly |
| R², MAE | l.199, Table 1 | MAE expanded only at l.373 | yes |
| risk–coverage curve, selective prediction | l.231 | partly | partly |
| reject option, Bayes-optimal, posterior, error–reject curve, margin conditions | l.314 | no | no |
| escalation floor / ceiling / saturation point | l.312, l.347 | floor never; others in passing | no (NS-14) |
| ρ, predictor A/B, relative error, "locked and hashed" | l.353-355 | partly | no |
| case39, case24_ieee_rts, case_illinois200, case57, case89pegase, load multiplier 0.0 | l.353-355 | no | no |
| audited population control, distribution-free risk control | l.363 | no | no |
| exchangeable, weighted conformal, covariate, likelihood ratio, absolutely continuous | l.367 | no | no |
| dynamic stability | l.367 | yes | yes |
| agg_loading, vm0_*, F1–F4, LODF, electrical distance, one-hot, "re-searched", three-arm permutation control, pre_p_mw etc. | l.371-379 | LODF never; code names raw | no |
| foundation model, input-convex network, false negatives | l.101 | no | partly |

- Fix: define each term at first use in plain words. Drop code identifiers from prose, or map them once.
  Any term the argument does not need can go.

### NS-14 — MAJOR — The paper's key concept, the escalation "floor", is never given a number
- Anchors: heading "The boundary layer sets a floor on escalation" (l.312); "the reasoning for the existence
  of such a floor" (l.388); "lower escalation ceiling of 74.89% versus 82.79%" (l.347).
- Problem: the section titled "floor" gives CEILINGS and a "saturation point" (82.64%), but no floor
  value, and it never defines the floor operationally. An outsider reads floor = minimum and ceiling =
  maximum and cannot tell which number is the finding. The conclusion's "such a floor" (l.388) therefore
  has no numeric anchor.
- Fix: define the floor once (what quantity, at what operating point), give its value with ±, and
  distinguish it explicitly from the ceiling and the saturation point.

### NS-15 — MAJOR — The "Theory" subsection restates definitions and never pays off
- Anchors: "which lines up with the definitions of the gate's" (l.173); "it is a structural property of
  this gate" (l.181); "For the IEEE 118-bus system, using the statistic above" (l.189).
- Problem: Eq. 3 is the escalate rule of III.4 rewritten; Eq. 4 is algebra on the certify rule. S_mean is
  computed (0.60 vs 0.79) but the paper never says whether bigger is worse, and never uses it again
  (grep: no later use). y and the indicator are undefined (NS-13). An outsider sees a section labelled
  "Theory" that proves nothing. A skeptical judge may read it as dressing up.
- Fix: either connect Eq. 4 and S_mean to a later result (what they explain) and give their direction,
  or relabel and shorten the section.

### NS-16 — MAJOR — Is it N-1 or two elements out? The paper says both
- Anchors: "so those rows have two elements out after it" (l.111) vs "These are still N-1 contingencies,
  since each one only removes one branch" (l.367).
- Problem: 24.93% of the data (374 bases, 69,532 rows) has a generator out and then a branch out. The
  Background calls these two-element outages. The Discussion calls them N-1. N-2 is defined as "two
  branches fail together". An outsider cannot tell whether the headline claim ("N-1") covers a quarter
  of the data honestly.
- Fix: use one consistent definition. Say in Method, not only in Discussion, how these rows are
  classified and why.

### NS-17 — MINOR — No "bigger/smaller is better" cue on any metric
- Anchors: Table 1 header (l.213), Table 2 header (l.246), S_mean (l.189).
- Problem: Esc. (lower better), Missed (lower better), Speedup (higher better), Cov. (should match
  Target), R² "−0.00±0.00" (a negative zero). None is marked.
- Fix: direction markers or one caption clause. Explain the R² sign/zero.

### NS-18 — MINOR — "Accurately" and "very fast" are unqualified
- Anchors: "Both surrogate models accurately predict" (l.199); "My models can predict N-1 under-voltage
  contingencies" (l.388); "both methods perform very fast" (l.388).
- Evidence (Reported, Table 1): ridge MAE 3.8±0.1 vs persistence (do-nothing) 4.2±0.1, about 10% better
  (real under the std rule, but small). "Very fast" = 2.0–3.3x. A judge who notices the MAE gap will
  distrust "accurately".
- Fix: tie the adjective to a comparison, or drop it.

### NS-19 — MINOR — The intro's "three distinct ways" include a scope limit
- Anchor: "Second, I specifically check for only under-voltage issues." (l.101).
- Problem: restricting scope is not a contribution. An outsider counts two real deltas and reads the
  third as padding. The item "I add the solver time for escalated cases" (l.99) also appears before
  "escalated" is defined.
- Fix: list only the actual differences, each tied to where it is shown.

### NS-20 — MINOR — Prior work is described differently in the abstract and the intro
- Anchors: abstract "surrogate models that check a group of cases at once" (l.81) vs intro "checks if any
  single piece of equipment ... randomized full solves" (l.101).
- Problem: a reader cannot map the abstract's three categories onto the intro's three papers. (Accuracy of
  the characterisations is for the specialist panelists. I flag only the inconsistency.)
- Fix: make the abstract's categories match the intro's descriptions.

### NS-21 — MINOR — Figure captions: small gaps against the "caption alone" test
- Fig. 1 (l.155): the dot (prediction) and the bar (band) are not labelled in the figure or caption.
  Otherwise the best figure in the paper.
- Fig. 3 (l.303): "q̂@0.90", "Y" undefined; "one certified bus" (it is a contingency that is certified,
  not a bus). Referenced before it appears: yes. Supports the sentence: yes.
- Fig. 4 (l.323): clear. The purpose of "yet the tallest 0.001 pu bin ... holds only 14.1%" (ruling out
  a single-value artifact) is not stated, so "yet" puzzles.
- Fig. 2 (l.281): x-axis runs 0.70–0.99 while the text and Table 2 discuss 0.90–0.98; see also NS-08.
- All five figures and both tables are referenced in the text before they appear (checked on the PDF,
  pp.5–11).
- Fix: label the glyphs; define figure symbols in the caption; state what each caption's key number is
  there to show.

### NS-22 — MINOR — Table 2 skips 0.91–0.93
- Anchor: Table 2 rows (l.248-260). Fig. 2 and IV.4 (nine targets) use a finer grid, so the reader wonders
  what was left out.
- Fix: say why those rows are omitted, or include them.

### NS-23 — MINOR — Cryptic forward-reference sentence
- Anchor: "The question of safety is not in the number of errors made but in the location of those
  errors." (l.199). It is not explained until Fig. 3, one page later.
- Fix: say what "location" means where the claim is made.

### NS-24 — MINOR — Discussion paragraph 2 is not followable
- Anchor: "This establishes the lower bound because, in split conformal prediction, I can be correct on
  average" (l.363). "This" and "the lower bound" have no clear referent. The point about 186 correlated
  contingencies per base (a real and important caveat) is lost.
- Fix: state the caveat on its own: coverage is an average, not a per-case promise, and rows within a
  base are related.

### NS-25 — MINOR — The physics-feature ablation is in the wrong section and is hard to read
- Anchors: "In the specific ablations, I intentionally left out" (l.371); "Since the input data varies across
  different scenarios, I can conclude that any change" (l.377).
- Problems: it sits under "Discussion and limitations" but reports new results. Whether the MAIN models
  use agg_loading is not said. "Line loading" and "total demand" are used as if they were the same
  thing. The leakage-audit sentence does not describe leakage in a way an outsider recognises. The
  single-seed permutation check is compared against a multi-seed std.
- Fix: move it to Results or an appendix-like subsection. State the main model's feature set once. Say
  plainly what leakage would look like and what the audit rules out.

### NS-26 — MINOR — Typos and small mechanics
- "locked tes" (l.353); "although 73.1% of converged N-1 rows the highest bus voltage is over" (l.107, a
  missing "in"); "the N-1 constraint uses an AC power flow solver" (l.81: the criterion does not "use" a
  solver).

## 3. Three strongest parts (protect these during revision)

1. **The self-found data bug** — "The previous implementation of the dataset generator used a lower bound"
   (l.121). The student noticed an impossible requirement, traced it to a clipping artifact, fixed it,
   and reported that the headline quantity barely moved (55.5% to 56.86%). To a judge this is the most
   convincing evidence of real individual scientific work. Keep it, and make the discovery step readable
   (NS-13).
2. **The plain operator trade-off with error bars** — Table 2 (l.239-268) and "An operator that requires a
   missed rate around 1%" (l.349). An unfavorable headline stated plainly, with ± over five splits and
   the error-bar overshoot of 1% admitted. This is the "honest negative result" STS rewards.
3. **Fig. 4 plus the 118-vs-30 contrast** — Fig. 4 (l.320-329) is the one figure an outsider understands
   instantly, and the 56.86% vs 7.09% boundary share next to 63.7% vs 5.84% escalation (l.81, l.365) is the
   paper's most intuitive evidence. Honorable mention: the hash-locked cross-network predictions and the
   stated reasons for dropping case57/case89pegase (l.353-355), which show a pre-registration mindset.
   Keep those, but explain them (NS-10).

## 4. Open questions I could not settle

- Whether STS expects the AI/program/mentor disclosures (NS-01) in the report body or in the application
  form. That decides FATAL vs MAJOR.
- The .tex header says the body text is "VERBATIM from the URTC conference version". `sts-constraints.yaml`
  R18 asks that a published paper be acknowledged in the application, and that a group paper get the
  student's own version. The report does not mention the URTC paper. Whether the URTC paper had
  co-authors is not in the files I was allowed to read.
- Whether the operational cost of a flagged case (NS-04) is small enough that ignoring false alarms in
  the speed-up is reasonable. That is a specialist call. An outsider only sees that it is never discussed.
