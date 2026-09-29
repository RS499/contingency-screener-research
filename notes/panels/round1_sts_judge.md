# Round 1 — STS Top-40 selection judge (blind panelist)

Paper: `report/paper_current_STS.tex` (compiled 2026-09-27 13:50, 20 physical pages, body folios 1–16).
Read in full: the compiled text, the PDF figure pages 5–11, the .tex source, `CLAUDE.md`,
`notes/sts-constraints.yaml`, `notes/prior-art.md` §1–6, two finalist papers (openings only), and the
data artifacts cited below. Blind list respected. All recomputation used `.venv/bin/python`; std is
population std (ddof=0) over 5 seeds unless noted.

---

## 1. Rubric (1–10)

| Criterion | Score | One sentence |
|---|---|---|
| Originality | 5 | The mechanism (a calibrated band routes uncertain cases to an expensive oracle) is already in the literature, and the paper correctly doesn't claim it. The original part is the observation that escalation has a floor set by boundary mass. The paper states this but never shows the physical cause. |
| Rigor | 6 | Rigor is visible in the hashed pre-registered predictions, 5-seed stds throughout, the leakage audit, and the clip-artifact bug that was found, fixed and re-run. But the central mechanism rests on a confounded two-network comparison, and the model comparison is made at matched coverage targets rather than matched cost. |
| Significance | 4 | It covers one network under one synthetic stress distribution with only trivial baselines in print. The practical claim ("operators can decide per network") is backed in print only by a cross-network predictor with ~47% relative error. |
| Clarity | 4 | No research question or hypothesis is ever stated, and §IV.4 cannot be followed on a cold read. The "Theory" section restates the gate definitions, and several sentences lose their meaning (STS-14). |
| Student potential | 7 | The repo shows far more real scientific thinking than the paper does: chased surprises, controls and self-corrections. A Top-40 panel only sees the paper. |

### Plain verdict
- **Top 300 now: roughly a coin flip, and only once STS-01 is fixed.** As submitted, the missing AI
  disclosure is a rules exposure that can end the entry regardless of merit. With it fixed, this is a
  competent, honest, solo computational project with error bars and an explained negative result. That
  is the profile that makes Scholar, but ML-surrogate-on-a-test-grid projects are common, and the
  writing hides the best evidence.
- **Top 40 now: unlikely.** A doctoral panel will ask "isn't your boundary mass just your base-case
  filter?" (STS-03). The paper doesn't answer that, and the mechanism evidence in print is thin and
  confounded (STS-04). With the changes below it moves to a long shot that is credible, because the
  controlled evidence already exists in the repo.

### The single change that would move it most
**Replace the confounded case118-vs-case30 comparison and the A-vs-B predictor paragraph with a
within-network, controlled dose-response test of the mechanism.** The repo already has such tests,
tracked in git, over 5 seeds: the limit sweep (`data/sweep_results_long.parquet`), the N-0 stratum
split (`data/drift_n0_stratum_long.parquet`) and the quintile analysis
(`data/quintile_boundary_mass.json`). Pair it with a plain statement of the physical cause
(STS-03): most single outages don't move the weakest bus, so post-outage voltage inherits the
base-case voltage, and the sampler plus the N-0 filter put the base cases just above 0.94. This turns
the headline from a correlation seen in two networks into a mechanism with a controlled manipulation.
A Top-40 panel looks for exactly that. (Details in STS-03 and STS-04.)

### Next two
1. **Compare models at matched cost, and report the case30 ordering reversal together with the statistic
   that explains it** (STS-05). The paper's own S_mean predicts which model misses more on each network.
   That is currently an unused finding.
2. **State the research question(s) and hypothesis in the Introduction, and put the conformalized
   classical baseline in Table 1** (STS-06, STS-08). This makes the paper read as an investigation
   rather than a pipeline report, and it answers "is ML even needed here?"

### Where the student's own scientific thinking shows, and where it reads like a pipeline
- **Own thinking, visible:** (a) the clip-artifact discovery (:121). An inverted escalation-vs-band
  relation "returned unattainable accuracy requirements", which led to a generator bug. The student
  fixed it, regenerated the data, and reported the before/after (55.5% → 56.86%). This is the best
  paragraph in the paper for demonstrating a scientist at work, and it is compressed to three
  sentences. (b) Pre-registered, hashed cross-network predictions, with a result reported even though
  it was unflattering (:353–355). (c) Networks dropped for stated physical reasons, with numbers
  (case57, case89pegase). (d) Moving the limit to 0.95 pu to probe the design choice (:365).
  (e) The permutation control and leakage audit (:377).
- **Reads like a pipeline:** §III.5 "Theory" rewrites the gate's own inequalities and then defines
  S_mean without saying what it predicts. §IV.4 uses protocol vocabulary ("predictor A/B", "locked",
  "hashes intact") with no question attached. §V.1 lists five feature configurations with MAE to five
  significant figures and no hypothesis. The Table 2 walkthrough (:231) reads numbers aloud. The repo
  contains the missing "why" for most of these (barrier_height.json, sweep_results_long.parquet,
  qlimit_class.json). The paper does not carry it.

### Is the negative / mixed result a finding with a mechanism, or buried?
**Half and half.** The negative result is named in the title and argued in §IV.3 and the Conclusion,
which is to the student's credit. But the abstract never says what boundary mass is or why it caps
speedup. The only mechanism evidence offered is (i) a histogram of one network, (ii) one second network
generated with a different load window, and (iii) a cross-network predictor. For (iii) the paper
reports only that B is "not clearly more accurate" than A, not that both miss by about half. The
physical cause (inheritance from the N-0 voltage, STS-03) is never stated. So the result is presented
as a finding, but its mechanism is asserted rather than demonstrated.

### STS-rule compliance summary
- Page limit: **PASS.** Body folios 1–16. Title, abstract and bibliography are unnumbered, and there is
  no appendix (`pdfinfo` → 20 pages; folios in `notes/panels/round1_paper_text.txt`).
- Graphic citation line under every float: **PASS** for all 5 figures and 2 tables. Each carries
  student, program and year (:158, :223, :265, :284, :306, :327, :342). Fig. 5 omits the layout tool
  (STS-12).
- No links in the body: **PASS.** The only `\url` is inside `\bibitem{case118}`, which is permitted.
- Page numbers bottom-right, 1.5 spacing, 12 pt, 1" margins: **PASS** (:48, :75, :25–27).
- **AI disclosure: FAIL** (STS-01).
- **Paid-program and people disclosure: incomplete** (STS-02).

---

## 2. Findings

### STS-01 — FATAL — No disclosure of generative-AI use anywhere in the report
- **Anchor:** :393 "This paper has been written as part of the Boston University RISE data science practicum."
- **Evidence (VERIFIED):** `grep -n -i -E "generative|claude|chatgpt|\bAI\b|artificial" report/paper_current_STS.tex`
  returns only the Alcántara intro sentence (:101) and a bibliography title (:452). There is no
  disclosure. RULES2027 Appendix 4 (verbatim in `notes/sts-constraints.yaml` R22) says AI-written
  code is acceptable "only with explicit citation stating which portions of the code were AI
  generated and with a log of the prompts". GUIDE2027 requires "full disclosure of any research or
  person that has influenced" the work (R20). `sts-constraints.yaml` R04 records that an earlier
  Acknowledgments carried a partial AI statement. The current one carries none, so this has
  **regressed**. The repo's own `CLAUDE.md` names an AI toolchain and a prompt log as standing
  practice. AI review panels (including this one) are also influence to disclose.
- **Suggested fix:** Add a disclosure in the report. It should name the AI tools used, which portions
  of the code were AI-generated or AI-assisted, what AI was used for beyond code (review, citation
  checking, and so on), and the existence of the prompt log. Check with STS whether the application
  also has a separate field for this. Treat it as a submission blocker.

### STS-02 — MAJOR — Support disclosure is incomplete: the paid program isn't stated as paid, and instructors aren't named
- **Anchor:** :393 "I would like to thank the program and the teaching fellows and staff."
- **Evidence (Reported):** `sts-constraints.yaml` R20 notes that BU RISE was paid and that named
  instructors taught the material. The report names no person and does not say that the program
  charges fees.
- **Suggested fix:** State the program's fee-based nature, name the instructors and TFs and what each
  contributed, and name anyone who read a draft. The exact framing is the owner's call. The content must
  let a judge separate the student's contribution from the program's.

### STS-03 — MAJOR — The paper never states the physical cause of boundary mass: post-outage voltage inherits the base-case voltage, and the sampler puts base cases at the limit
- **Anchor:** :121 "This implies that clustering is an inherent characteristic of the network and the sampling process."
  Also :365 "The key findings obtained during the experiments relate to a network with a realistic topology".
- **Evidence (VERIFIED):** From `data/dataset.parquet`, over converged line/trafo rows (n = 278,955):
  - 77.6% of rows have |min_vm − n0_min_vm| < 0.001 pu.
  - 93.4% of the rows in the [0.94, 0.945) strip are within 0.001 pu of their own base-case minimum.
  - 67.7% of the 1,500 accepted bases have n0_min_vm in [0.94, 0.945).

  (Command: an inline pandas script over the columns `min_vm, n0_min_vm, outaged_type, converged`.)
  Also:
  - Reported, `data/quintile_boundary_mass.json`: boundary mass is 78.4 / 81.3 / 82.4 / 37.3 / 5.0%
    across the base-voltage quintiles of case118 itself. The top quintile (4.98%) already looks like
    case30 (7.09%).
  - Reported, `data/unconditioned_base.json`: removing the N-0 gate halves the boundary mass
    (56.86 → 28.83%).

  So the floor is a property of network × operating-point distribution × limit. On case118 it is
  driven mainly by how the student sampled and filtered base cases. A doctoral judge will reach this
  question first.
- **Suggested fix:** State the inheritance mechanism explicitly, with the three verified numbers above,
  and say plainly that the escalation floor is a statement about this stress distribution. Move the
  realism caveat (synthetic load window, N-0 filter at exactly the screening limit) next to the
  headline rather than leaving it in the limitations paragraph. This strengthens the paper: it turns
  "most data is near the limit" into a physical explanation.

### STS-04 — MAJOR — The mechanism evidence in print is confounded and weak, while stronger controlled evidence sits unused in the repo
- **Anchor:** :353 "I used non-overlapping calibration and testing data to ensure minimal bias."
  Also :353 "Since predictor B was not clearly more accurate than predictor A".
  Also :365 "For instance, in a regeneration of the IEEE 30-bus network".
- **Evidence:**
  - **Printed evidence is confounded.** The case30 contrast changes network, load window (0.87–0.99
    vs 1.0–1.12) and thermal filter all at once (:119).
  - **The cross-network predictors both miss by about half.** Reported, `data/netstudy2/summary.json`
    → `cross_network`: A_mean_rel_error 0.4726, B_mean_rel_error 0.4933 (these match the paper).
    For case24, predictor A gives 0.451 against a measured 0.217 (ridge, 0.90). The paper frames this
    as "B not better than A" instead of "the parameter-free law is off by a factor of ~2 across
    networks".
  - **Unused controlled evidence 1: limit sweep (VERIFIED).** In `data/sweep_results_long.parquet`
    (tracked in git), L runs from 0.900 to 0.955 on case118, 5 seeds, target 0.90. The Pearson
    correlation between boundary_mass and esc_observed is 0.977 for ridge and 0.995 for histgb. The
    calibration-CDF predictor has MAE 0.0018 (ridge) and 0.0014 (histgb).
  - **Unused controlled evidence 2: N-0 stratum split (VERIFIED).** In
    `data/drift_n0_stratum_long.parquet`, target 0.90, 5 seeds, the histgb escalation is
    2.8±0.8% on benign→benign vs 59.1±2.5% on marginal→marginal. That is the same network and model,
    with a ~20× difference. The trade-off is **not** removed: the benign-stratum histgb missed rate
    is 8.2±1.3%.
  - **Unused within-network predictor.** The within-network calibration predictor has a mean absolute
    error of 0.61 pp over 54 cases (Reported, `netstudy2/summary.json` → `within_network`). That is
    what actually supports the abstract's closing claim that operators can decide per network.
- **Suggested fix:** Make one figure and one short paragraph showing escalation against boundary mass
  under a controlled manipulation inside case118 (limit sweep or N-0 strata). Overlay the case30 and
  netstudy networks as out-of-sample points. Report the cross-network relative error honestly as the
  limit of the simple law. Also report what the controlled test shows about misses, not only
  escalation (boundary mass controls cost, not safety). All the data exists. It needs to go through
  the ≥5-seed, committed-code bar in `CLAUDE.md` §9 before entering the report.

### STS-05 — MAJOR — "The faster model is not the safer one" compares models at equal coverage targets, not equal cost, and omits the case30 reversal that the student's own statistic explains
- **Anchor:** :292 "On the IEEE 118-bus system, the more accurate model is not safer at any point in the coverage axis".
- **Evidence (VERIFIED from Table 2 = `data/frozen_poster_numbers_v2.json` → `safety_operating_points`):**
  - At matched escalation the two models are indistinguishable: ridge@0.94 has 64.3% escalation and
    0.79±0.21% missed; histgb@0.97 has 63.7% escalation and 0.83±0.24% missed. The gap of 0.04 is
    smaller than the std, so it is noise under the std rule. The paper prints both rows (:231) but
    draws the conclusion from same-target rows.
  - **case30 reverses the ordering** (VERIFIED, `data/case30_thermal/case30_thermal_frozen.json`
    records, ddof=0): at 0.90, histgb misses 2.23±0.35% at 2.7% escalation, while ridge misses
    6.09±0.42% at 11.9% escalation. Ridge needs 0.98 to go below 1% (37.8% escalation, 2.65×).
  - The case30 speedup of histgb@0.97, 17.9±3.7×, is never printed. Only its escalation is.
  - **S_mean explains the reversal** (Reported, `data/barrier_height.json` → `summary_at_090`).
    On case118, histgb 0.79±0.07 > ridge 0.60±0.08, and histgb misses more. On case30, histgb
    0.34±0.06 < ridge 0.72±0.07, and histgb misses less. Both gaps exceed the larger std.
  - The paper defines S_mean (:189) but never uses it for this purpose.
- **Suggested fix:** Recast the model comparison on the risk–coverage axis, meaning missed rate at
  matched escalation (the paper already cites risk–coverage, :231). Report case30 for both models,
  with speedup. Use S_mean, and the p99 tail version in the same JSON, as the explanation of which
  model is safer on which network. This turns a heading that is currently overstated into a real
  result.

### STS-06 — MAJOR — No research question or hypothesis, and one claim of necessity that the paper's own data contradicts
- **Anchor:** :101 "My work stands out from these papers in three distinct ways." and :101 "Finally, I explain why there must be a certain floor for escalation."
- **Evidence:**
  - The Introduction ends with a list of differences from prior work. No question or hypothesis is
    stated anywhere in the paper.
  - STS judges score the question first. The finalist exemplars (`notes/reference/finalist-papers/`)
    state the question or contribution in the abstract.
  - "Must be" a floor is contradicted by the paper's own case30 result (5.84% escalation, :365) and
    by the benign stratum (STS-04).
  - The second "distinct way" (under-voltage only) is a scope choice, not a contribution.
- **Suggested fix:** State one or two testable questions and what outcome would count as each answer.
  Scope the floor claim to the conditions under which it holds. Reserve the "differs from" list for
  differences that are contributions.

### STS-08 — MAJOR — Only trivial baselines in print, although a domain baseline exists; the global-quantile choice isn't defended against the closest prior work
- **Anchor:** :109 "Classical fast screens rank power system contingencies without running a full solver". Also :132 "A single quantile coverage is the easiest way to choose the band".
- **Evidence:**
  - Reported, `data/classical_screen_metrics.json` (5 seeds, tracked): an Ejebe–Wollenberg-style
    linearized screen, conformalized at 0.90, gives escalation 92.0±0.5%, speedup 1.085, missed
    1.07±0.22%.
  - That result shows the ML surrogate's value over a classical method (30.6% and 49.1% escalation).
    The paper instead dismisses classical screens as giving no numerical voltage (:109).
  - `notes/prior-art.md` §6.3–6.5: the closest prior work [4] already uses locally adaptive conformal
    (KCP) on IEEE-118 and a DCPF baseline.
  - The repo has a Mondrian (per-element) run (`data/mondrian_element_summary.json`). At histgb 0.97,
    seed 0, Mondrian gives 43.7% escalation and 1.66% missed vs global 63.8% and 1.16%: lower cost, more
    misses. The paper doesn't mention it.
- **Suggested fix:** Add the conformalized classical screen as a row in Table 1, with its timing basis
  stated. Add one or two sentences on locally adaptive bands, citing the closest prior work's use of
  them on the same network and what the repo's Mondrian run shows. The Mondrian run is single-seed in
  the summary, so verify 5 seeds before printing it.

### STS-09 — MAJOR — §IV.4 "Cross-network prediction" can't be followed on a cold read
- **Anchor:** :353 "Across the resulting 54 predictions of the escalation rate". Also :355 "I tested five networks in total, with three of them completing".
- **Evidence:**
  - The section never says what is being predicted, from which data, or before what event.
  - There is no per-network result table and no scale for whether 0.47 relative error is good.
  - It contains a typo ("locked tes").
  - "Five networks in total" conflicts with the seven networks the paper names (118, 30, 39, 24,
    Illinois200, 57, 89pegase).
  - The dropped-network paragraph (useful) is wedged between predictor results.
- **Suggested fix:** Restructure the section around one question and one figure (see STS-04). Give the
  network inventory once, in Method. Define each predictor's inputs and target in a sentence.

### STS-11 — MAJOR — The safety claim rests on a 1% miss target that is never justified, and miss depth is shown only at the unsafe operating point
- **Anchor:** :349 "An operator that requires a missed rate around 1\%". Also :303 Fig. 3 caption "The histogram above measures how far missed violations fall below the 0.94 pu floor at 90\% coverage".
- **Evidence:**
  - N-1 planning (the paper's own [1]) is a check of every contingency. The 1% tolerance is the
    student's choice and is never argued.
  - Fig. 3 shows depths at 0.90, which the paper itself calls unsafe. At the recommended points
    (ridge 0.94 / histgb 0.97), Reported `data/qlimit_class.json` gives a ridge deepest miss of
    0.032 pu (seed 4) and 58 "deep" misses (beyond one band width) across seeds.
  - Only the 0.90 deepest miss (0.0915 pu) is printed.
- **Suggested fix:** Justify the 1% target, or present it as an operator-chosen parameter. Report miss
  depth (tail and maximum) at the recommended operating points, not only at 0.90.

### STS-07 — MINOR — Fig. 2 caption and text refer to error bars that the figure doesn't have
- **Anchor:** :281 "with high escalation at both and the error bars still reaching slightly above 1\%." Also :231 "as Fig.~\ref{fig:tradeoff} shows."
- **Evidence (VERIFIED visually):** `data/tradeoff_hero_col_v2.png` draws mean curves only. There are
  no bars or bands.
- **Suggested fix:** Either add seed bands or bars for the missed-rate curves, or remove the claim from
  the caption and text. The 1.0–1.07% upper edge is the paper's key uncertainty statement and should
  be visible.

### STS-10 — MINOR — "Theory" is a restatement of definitions
- **Anchor:** :167 "Escalation happens when the model predicts in the same interval where the band crosses the threshold." Also :181 "Since this inequality comes from the gate's mechanisms, it is a structural property of this gate."
- **Evidence:** Eq. 3 and Eq. 4 follow directly from the gate definitions in :139–141. Nothing is
  derived from them in this section. The quantitative relation actually tested later (escalation ≈
  ρ·q̂, :353) is not derived here.
- **Suggested fix:** Either retitle the section and keep it short, or derive the escalation–density
  relation here and state when it should fail (non-uniform density within one band width, which is
  what the ~2× cross-network errors suggest).

### STS-12 — MINOR — Fig. 5 mixes the bus-numbering conventions; its credit line omits the layout tool
- **Anchor:** :339 "The three dominant buses are 76, 53, and 107".
- **Evidence (VERIFIED visually, PDF p.11):**
  - The figure's node labels read "bus 75 (27%)", "bus 52 (17%)", "bus 106 (9%)", "bus 0", "bus 20".
    These are 0-based. Caption and text use 1-based 76 / 53 / 107.
  - The figure's footer says "Topological layout (pandapower igraph)". The credit line names only
    Matplotlib.
- **Suggested fix:** Relabel the figure in IEEE 1-based names. Name every program used to make the
  graphic in its citation line (RULES2027 Appendix 3).

### STS-13 — MINOR — §V.1 ablation: a null result given 1.5 pages inside Discussion, with its one positive observation unexplained
- **Anchor:** :375 "The one negative outcome obtained here is that including F2". Also :377 "In a quick single-seed histgb check".
- **Evidence:**
  - The ridge +10.82% degradation has no proposed cause.
  - The permutation control is single-seed.
  - :377 "Since the input data varies across different scenarios, I can conclude that any change in
    values from the audit was not due to constant features" doesn't say what was concluded.
- **Suggested fix:** Shorten the section. State the hypothesis the ablation tested and the one-line
  answer. Offer a cause for the F2 effect or call it unexplained. Say explicitly what the leakage audit
  rules out.

### STS-14 — MINOR — Sentences whose meaning is lost (flagged only where comprehension fails)
- **Anchors:**
  - :107 "In this study, I do not check for overvoltage, although 73.1\% of converged N-1 rows the highest bus voltage…"
  - :167, quoted in STS-10.
  - :363 "This establishes the lower bound because, in split conformal prediction, I can be correct on average but not necessarily inside the band."
  - :377, quoted in STS-13.
  - :199 "The question of safety is not in the number of errors made but in the location of those errors." This is a strong idea that nothing after it develops.
- **Suggested fix:** The author should rewrite each of these so that it makes one checkable statement.

### STS-15 — MINOR — Realism of the operating points
- **Anchor:** :107 (the 73.1% overvoltage sentence) and :365 "a network with a realistic topology and synthetic loads".
- **Evidence (VERIFIED):** `max_vm > 1.05` in 73.14% of converged N-1 rows (`data/dataset.parquet`).
  A power-systems judge will read this as states that no operator would run.
- **Suggested fix:** Say what share of base cases are already outside the upper band, and why the
  under-voltage-only conclusion still holds. Alternatively, add a sentence on how this bounds the
  realism claim.

### STS-16 — MINOR — The closest-prior-work characterization of [3] rests on a record the repo says to re-read before citing
- **Anchor:** :101 "Manoharan \cite{manoharan2026} utilized a fast computer model that checks if any single piece of equipment".
- **Evidence (Reported):** `notes/prior-art.md` §6.6 says the arXiv:2607.13221 record rests on a
  2026-07-19 HTML skim and should be re-read in full before citing. No later re-read is recorded. The
  intro also doesn't say [3] is thermal-only, which is the actual scope difference.
- **Suggested fix:** Re-read [3] in full. Correct or confirm the description, and state its target
  (thermal) in the intro.

### STS-17 — MINOR — The cost accounting leaves out the base-case solve that the features require
- **Anchor:** :147 "Here $n$ is the total number of contingencies, $t_{\text{solve}}$ is the solver time per case".
- **Evidence:** The features include pre-outage voltages (vm0_*), which need one AC solve per
  scenario. `data/classical_screen_metrics.json` → `ms_classical_accountings` charges this for the
  classical screen. It is about 0.05 ms per case, which is negligible, but it isn't stated for the
  surrogate.
- **Suggested fix:** State the omission and its size in one clause.

### STS-19 — MINOR — The abstract gives numbers but not the mechanism
- **Anchor:** :81 "In the IEEE 30-bus system, using a base case that is thermally feasible, where the regenerated 30-bus network has 7.09\%".
- **Evidence:** 282 words (`sed -n 81p … | wc -w`). Boundary mass appears only as a percentage. The
  reader is never told what it is or why it caps speedup. The case30 sentence gives escalation but not
  speedup.
- **Suggested fix:** The abstract should carry the question, the mechanism in one idea, the controlled
  evidence, and the limit of the claim.

### STS-20 — MINOR — Grouped data vs conditional coverage are conflated
- **Anchor:** :363 "Every base case generates 186 related contingencies, and therefore, the coverage rates are measured averages".
- **Evidence:** "Measured averages, not per-contingency assurance" is the marginal-vs-conditional
  coverage point [18]. The 186-rows-per-base grouping is a separate issue: exchangeability holds across
  bases, not rows. The paper merges the two into one causal clause.
- **Suggested fix:** Separate the two points. Say which unit is exchangeable under the base-level split.

---

## 3. Three strongest parts to protect in revision

1. **The clip-artifact discovery and correction** (:121 "The previous implementation of the dataset
   generator used a lower bound"). An unexpected result from a model inversion exposed a generator bug.
   The student fixed it, regenerated, reported the before/after, and checked whether the headline
   survived. This is the most convincing evidence of independent scientific judgment in the paper.
   Expand the reasoning (what "unattainable" meant) rather than cutting it.
2. **The honest negative headline carried by error bars** (:231 and Table 2, :248–260). The paper
   reports that safety costs most of the speedup and keeps the ±std that shows the 1% line is touched.
   Keep the negative framing. Don't tune toward a nicer number.
3. **Pre-registration and explained exclusions** (:353–355, locked and hashed predictions reported
   even though they were unflattering; case57 and case89pegase dropped with physical reasons and
   numbers). Keep both. Make the pre-registered result readable (STS-09) rather than removing it.

---

## 4. Open questions I could not settle

- Whether STS 2027 wants the AI disclosure inside the report, in an application field, or both. RULES2027
  Appendix 4 wording implies a citation for code portions. `sts-constraints.yaml` records 41 of the
  book's 50 pages as unread.
- Whether the application's abstract field has a word limit that the 282-word report abstract exceeds
  (unverified).
- Whether the limit-sweep and N-0-stratum artifacts were produced by committed, tested code under the
  pinned solver config, which is the `CLAUDE.md` §9 bar for entering the report. Their manifests show
  the pinned solver and 5 seeds. I did not audit the generating scripts.
- Whether "five networks in total" (:355) is meant to exclude case118 and case30. If so, the sentence
  needs the qualifier.

### Finding count
FATAL 1 (STS-01) · MAJOR 8 (STS-02, 03, 04, 05, 06, 08, 09, 11) · MINOR 10 (STS-07, 10, 12, 13, 14, 15, 16, 17, 19, 20).
