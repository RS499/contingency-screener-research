# STS 2027 Master Plan v3 — Conformal-Gated Surrogate Screening

**Owner:** Rajan Saha
**Application deadline:** November 5, 2026, 8:00 pm ET
**Technical support deadline:** November 4, 8:00 pm ET
**Target first submission:** November 1 (then keep editing until the deadline)
**Status:** URTC version submitted (CMT #74, Aug 8). STS version written from scratch, sole-authored.
**Revised:** 2026-08-09 · ~12.5 weeks remaining

---

## 0. Read this before anything else

**This plan cannot guarantee Top 40, and no plan can.** Forty of ~2,600 is 1.5%. STS
publishes no rubric. The final selection is made by a panel of fifteen scientists reading
across every discipline, and their judgment is not a function you can solve.

What a plan *can* do is eliminate every failure mode inside your control. Sort the
outcome into three buckets:

| Class | Controllable? | This plan's job |
|---|---|---|
| **A. Disqualification and self-inflicted loss** — rules violations, missed deadline, undisclosed relationships, unverifiable citations, format breaches, an unreconciled mentor account | **Fully** | Drive to zero. Non-negotiable. |
| **B. Legibility and framing** — whether an evaluator outside power systems can see the contribution, whether your initiative is visible, whether the person shows up alongside the science | **Largely** | This is where the plan spends most of its effort. |
| **C. Selection** — how your work compares to 2,599 others in a year you can't see | **No** | Stop optimizing. Accept. |

Class A is where "no exceptions" actually applies, and it is the only place that phrase
belongs. Treat any hour spent on Class C as an hour stolen from Class B.

**Protected commitments, non-negotiable in the other direction:** college applications
ship on time, and sleep does not become the adjustable variable. Every finalist in the
official webinar corpus who was asked about process said the same two things — work in
chunks, and get rest. Two of them independently said the single best thing they did was
take walks. The plan below is sized to be finishable without breaking either commitment.
If it stops being finishable, cut Tier 2, not sleep.

---

## 1. What changed from v2, and why

| Change | Reason |
|---|---|
| **Cap #3 deleted** ("explains a limit rather than discovering a phenomenon — harder sell") | Contradicted twice. The head judge states on record that proving your hypothesis is not required and that many top-ten projects went sideways. And the 4th-place 2026 math paper's own abstract advertises *simpler construction*, *reprove*, and "as a byproduct" three times. Explanation-shaped contributions place. |
| **Rigor demoted from headline to substrate** | Thirteen official webinars, including the only one where evaluators describe their scoring on record, never mention error bars, replicate counts, dispersion, or uncertainty quantification. Not once. They name: idea origination, initiative, who designed the study, who developed the methodology, who did the analysis, role in execution, mentor cross-check, and *"it all comes back to the writing for me."* Keep the rigor. Stop marketing it. |
| **Four-of-five diagnostics table cut from Discussion** | Same reason. It argues on an axis nobody scores and asks a reader to accept an unverifiable negative. |
| **Mentor contribution brief promoted to the single highest-priority item** | Evaluators cross-check the mentor's account against yours; "sometimes it doesn't match up" is a named red flag, and both under-claiming and over-claiming get caught. RISE is ending, so this has the shortest window of anything in the plan. |
| **Revision-arc narrative promoted to spine of Task 4 and Introduction framing** | The 2023 second-place winner's project became infeasible six months in, she restarted from zero, and narrating that revision "took up a lot of my application." She had no prior science-fair experience. Your oracle-bug → clipping-artifact arc is the same shape. |
| **List-of-five added as a required instrument** | It appears in six-plus official webinars and is called "your thesis for your full application." v2 had a research trajectory but no equivalent for the non-research half, which is exactly where §0 says the variance lives. |
| **Page budget risk reassessed** | Front matter and bibliography confirmed excluded; appendices confirmed included. v2's ~18 pages of body is fine. **New** risk: figures were never budgeted, and appendices can't absorb them. |
| **Submit-early-then-edit adopted** | The most-repeated operational advice in the entire corpus: you can edit after submitting, right up to the deadline. Converts a hard deadline into a soft one at zero cost. |
| **Second project recommendation added** | Two are permitted. Two independent corroborations of your contribution on the axis evaluators check hardest. Also resolves the Kalita open item in the helpful direction. |
| **February finals-week phase added as a stub** | Panel judging is two of three judging days and tests breadth across all of science. `sts-judge` trains depth. That gap should exist on paper now, not be discovered in late January. |
| **"Use I, not we" moved out of non-negotiables** | Permitted, not required. The 4th-place paper uses "we" throughout. Still probably the right call given the contribution emphasis, but it is a choice, not a rule, and shouldn't consume compliance attention. |

---

## 2. Class A — non-negotiable compliance

**Every row below carries a verification status. The corpus these came from spans the
2021–2024 cycles and the rules change annually.** Nothing here is actionable until
checked against the 2027 rules book. Build this as `notes/sts-constraints.yaml` in week 1
and have the nightly job assert against it (§12).

| Rule | Source | Status |
|---|---|---|
| Deadline absolute; nothing submitted or achieved after it is judged | corpus, repeated | verify |
| Tech support deadline 24h prior; issues reported by then are guaranteed resolved | corpus | verify |
| Sole-authored, individual research; no team projects, no splitting a team project | corpus | verify |
| Written by the student **without generative AI**; research use permitted and disclosable | 2027 guidelines | verify |
| ≤20 pages. Title page, abstract, bibliography **excluded**. Appendices **included**. | corpus, stated twice | verify |
| Font ≥10–11pt; students have been disqualified for cramming with tiny fonts | corpus | verify |
| Single column, 1.5 spacing, 1" margins, Times New Roman | 2027 guidelines | verify |
| **Judges will not click any external links — explicit annual decision.** Code must live inside the 20 pages or nowhere. | corpus, Video 13 | verify |
| **Whether bibliography URLs are permitted** — v2 assumed yes; corpus says links "not permitted anywhere." | ambiguous | **ask STS week 0** |
| Full APA citation directly beneath each figure *and* table, naming the software used. Includes self-created graphics. Reference lists for graphics not permitted. | 2027 guidelines | verify |
| Every reference resolves. A discovered fake reference disqualifies. | corpus + guidelines | verify |
| Title page p1 unnumbered, abstract p2 unnumbered, body numbered bottom-right from 1 | 2027 guidelines | verify |
| No emails or phone numbers on the title page | 2027 guidelines | verify |
| PDF ≤4MB; filename `SAHA.RAJAN.<home zip>` | 2027 guidelines | verify |
| After upload, download the PDF and verify every symbol survived | corpus | do it |
| Literature reviews ineligible. Analyzing others' data or public databases to reach your own conclusions is fine. | corpus | n/a — original research |
| Surveys and human testing require IRB **pre-approval** | corpus | n/a |
| Published work: unless first or sole author, submit a different write-up | corpus | n/a for STS report |
| Grades reviewed: freshman through junior only. No senior Q1 needed. | corpus | tell counselor |

### Disclosure — the failure mode that ends applications

Non-disclosure discovered later is what the corpus repeatedly identifies as fatal, and
it is fatal regardless of how innocuous the underlying fact is. Disclose, in writing,
and without hedging:

- **BU RISE was a paid program.** Corpus is explicit that paid programs are permitted and
  that part of why they ask is to make sure students weren't taken advantage of.
- **Kalita and Pinsky taught you the material.** Say what you were taught versus what you built.
- **The URTC submission**, per the branch table in §8.
- **The two co-authored papers in the other research thread.**
- **AI use.** Your URTC acknowledgment says "used to validate the code and grammar." Your own
  audit found five passages where wording was AI-chosen. Judges who look up the URTC paper
  will read that line. The two disclosures must be consistent, and the STS one must be
  specific: what wrote code, what validated code, what touched prose, and that the report
  itself was drafted without it. **Write the STS disclosure first, then decide whether the
  URTC camera-ready line needs to match it.** The discrepancy is the risk, not the involvement.

---

## 3. Week 0 — the irreversible items

Everything in this section either has a closing window or is a prerequisite for
something else. Nothing in §6 matters if these slip.

### 3.1 The mentor contribution brief — highest leverage item in the plan

The only webinar where evaluators describe their scoring on record says they look at how
the idea originated, the level of initiative, who designed the study, who developed the
methodology, who did the analysis, and *"what role was the student in actually executing
the study?"* — and then they **cross-check the mentor's account against yours.**
"Sometimes it doesn't match up," and that is named as a red flag. A separate webinar
confirms mentors answer mirrored questions and that both under-claiming and over-claiming
get caught.

RISE is ending. This window closes first.

**Send Pinsky and Kalita, in writing, before RISE ends:**

1. **Who provided the research question.** State it as it actually happened. If it was
   Pinsky's, say so — the corpus is unambiguous that an assigned question is completely
   fine and that students with assigned questions become finalists.
2. **What was yours, by name.** The three-way gate. The one-sided band and its
   asymmetric-risk justification. Charging escalated solver time against the speedup.
   Base-scenario-level splitting. The nested inner-split tuning protocol. The escalation
   identity and the deployment criterion. Mondrian per-element calibration.
3. **What you were taught versus what you built.**
4. **The revision arc**, in one paragraph, so their account of it matches yours.

Then **have the conversation.** If Pinsky would describe any item differently than you
would, you need that reconciled before he writes, not discovered during evaluation. This
is a ten-minute conversation that protects the entire application.

### 3.2 Request all recommendations — use every slot

- **Project recommendation ×2:** Pinsky and Kalita. Two independent corroborations on the
  axis that gets checked hardest, and it resolves the Kalita author-block item in the
  direction that helps you.
- **Educator recommendation ×2:** one science teacher who has had you in class, and one
  **non-teacher** — a coach, boss, or religious mentor. This is explicitly permitted
  specifically to add life context. Given §0's "no research spike," an outside-STEM voice
  is worth more than a second science teacher.
- **High school report:** counselor. Tell them freshman-through-junior grades only, and
  that estimates are fine for the school-statistics questions.

Ask each recommender **which email address they want used.** Mismatched addresses across
multiple students is a named, recurring cause of lost recommendations. And warn them: a
ten-minute recommendation typed on a phone beats none at all, and applications are still
considered if one is missing — it just costs context.

### 3.3 Email STS

One message, four questions:

1. AI: the report must be written without generative AI — does that extend to
   AI-suggested citations that you independently verified? (You have three.)
2. Dual submission: URTC-submitted work, sole-authored STS version written from scratch —
   confirm no conflict, and confirm the disclosure wording you plan to use.
3. Sole authorship: confirm the co-authored URTC paper doesn't affect eligibility of a
   from-scratch sole-authored report on the same research.
4. Bibliography URLs: permitted or not?

### 3.4 The list-of-five

The organizers' own instrument, and the one thing v2 was missing entirely. Private
checklist, never pasted into the application:

- Five things you care about in life
- Five ways you lead, in any community
- Seven ways you actually spend your time each week — real time, not impressive time

Family responsibilities and religious obligations have their own activity categories and
count fully. After you draft everything, come back and confirm each item shows up
somewhere. The stated purpose: making sure *you're* in there, not just your science.

### 3.5 Verification housekeeping

- `ai-prompt-log.md` reconstructed from session history while it's recent
- Verify the three selective-regression paper authors from local extraction notes — not
  from memory, not from any chat transcript
- Log the URTC post-submission edits in `notes/erratum.md`: Pinsky added to CMT at
  23:00:24 Aug 8, four prose fixes, plus the camera-ready list from §6.6
- Confirm the GitHub repo resolves publicly

---

## 4. The contribution, reframed

### 4.1 Lead with the prediction, not the corpus search

`Esc = P(L ≤ p̂ < L + q̂)` follows in one line from the gate definition. A judge derives it
unprompted and then wonders why credit is being claimed for it. And "absent from 19 papers"
asks a reader to accept an unverifiable negative, which some will resent.

**What's checkable and what could have failed:** boundary mass was measured on the 30-bus
network *before* running the gate, and escalation landed where the identity said it would.

| | Boundary mass | Escalation at sub-1% missed | Speedup |
|---|---|---|---|
| IEEE 118-bus | 56.9% | ~64% | ~1.6× |
| IEEE 30-bus | 20.0% | 8.96 ± 0.91% | 11.27 ± 1.02× |

> Safety and speed are not inherently inverse. They are inverse where boundary mass is
> high, and the quantity that decides it is measurable before any model is trained.

The corpus search survives as **one scoping sentence in Related Work**: no reviewed work
relates deferral rate to outcome density at a *physical* limit; the three nearest results
concern estimated conditional variance near a *cost* threshold, governing convergence rate
rather than the deferral rate itself. Cite all three, state the distinction once, and never
call it a law. It is an accounting identity plus a design criterion.

### 4.2 The barrier-height insight — still unstated anywhere

A violation is missed only if `p̂ ≥ L + q̂` while `Y < L` — the overshoot must exceed
`q̂ + d` where `d` is violation depth. So **q̂ is not a window here, it is a barrier
height.** Coverage fixes the overshoot quantile for both models, but the barrier's absolute
height is set by each model's error scale: ridge's worse accuracy buys a 0.0052 pu barrier,
histgb's better accuracy buys only 0.0023.

> At fixed coverage, accuracy converts into throughput, not safety. The certification
> barrier is bought with error, and the more accurate model gets a shorter one.

This turns the "faster model is not the safer one" result from an empirical curiosity into
a structural property, and it predicts the miss-depth asymmetry already visible in Fig. 3
(74% vs 55% within one band). It also gives you the matched-safety comparison that the
URTC paper leaves on the table: ridge@0.94 = 0.79% missed at 1.56×, histgb@0.97 = 0.83%
missed at 1.58× — at equal safety, the accuracy advantage buys nothing.

### 4.3 The two error narratives — the strongest maturity evidence you have

**The oracle error.** All early feasibility work ran without `enforce_q_lims`, under which
generator reactive limits have no effect. Physically wrong. It invalidated the weak-bus
narrative, made the two-bus concentration partly an artifact, and moved the loading ceiling
from 160% to ~140%. Self-caught.

**The clipping artifact.** Generator setpoints were drawn with a lower sampling bound equal
to the screening threshold and clipped to it, producing a point mass at exactly 0.940000 —
35.17% of rows when adjacent float patterns are merged. Found by *inverting the
escalation-versus-band-width curve* and noticing it returned impossible requirements. Fixed
by resampling. The central finding survived: strip concentration moved 55.5% → 56.86%.

The line to have ready, cold, in a panel interview:

> One thing I will not hide: removing the artifact made the safety numbers worse.

**Count and name all self-caught errors.** v2 claims four and documents two. Task 4 needs
all of them by name; an unsourced count violates §11.

### 4.4 Structural lessons from the 4th-place 2026 paper

That paper's stated contributions are a simpler construction, several reproofs, and three
"as a byproduct" results. It placed fourth. Four things it does that you should copy:

1. **Ground it for outsiders in the first paragraph** — before any technical content. It
   opens with Cartan 1913, Dirac 1928, and "parametrizes configurations of n electrons,
   each of which has spin-up or spin-down." Your equivalent: what N-1 protects against,
   what a cascading outage costs, why operators re-run this continuously.
2. **Spend real space on preliminaries.** Original results start on page 9 of 24 — ~37%
   background. Your §7 allocates ~22%. You have permission to spend more, and PhDs outside
   your field will need it.
3. **Label section by section which results are new and which are reproofs or byproducts.**
   That is Valentine's "be specific about what your contribution was," executed structurally.
4. **Name the field-level open problem your work moves toward.** Not "future work includes
   testing more networks." Something closer to: *no current method gives per-case guarantees
   under AC power flow at deployment scale, and the criterion here tells an operator in
   advance whether that is achievable on their network.*

Also useful for calibration: that paper shipped with a three-line proof of its headline
theorem whose key step is unargued, a lemma whose entire proof is "we can verify that all
the relations hold," and a typo in a section heading. **Done is better than perfect** is not
just encouragement from the organizers — it is what the evidence shows.

One honest asymmetry: she was sole author on PRIMES-USA and could trim the same paper. Your
URTC paper is co-authored, so you write 20 pages fresh. Budget accordingly.

---

## 5. Where the remaining variance actually lives

§0 says it, and the plan has to act like it. After §6 executes, the paper is no longer the
binding constraint. What differentiates 40 from 300 — a pool already selected for research
quality — is Task 4, essays, activities framing, and three recommendations.

**Nested probability, stated correctly.** All 40 finalists are drawn from the 300 scholars.
"Scholar 65–75%, Finalist 25–30%" implies P(Finalist | Scholar) ≈ 39% against a within-pool
base rate of 40/300 ≈ 13%. That is a claim about being top-third *among scholars* — a 3×
lift inside a pool already filtered for quality. Whether or not the numbers are right, that
framing tells you what to optimize: the things that separate 40 from 300, not the things
that got you into the 300.

**Essays.** Prompts are aligned with the Common App — reuse aggressively. Bullet lists are
acceptable. Don't overthink spelling and grammar; the organizers say so directly. Write "I
do this because I enjoy it," never "because I want a certain outcome" — judges can feel
manufactured passion. Run the lay-comprehensibility answers past someone non-technical.

**Activities.** Seven categories, multiple items each. List how you actually spend your
time, not what looks most impressive. The corpus's own example: don't claim to be the best
banjo player in the state if you play five minutes a day.

**The research program.** Carbon-intensity accounting → load-forecasting instrumentation →
N-1 reliability screening. Currently three unrelated activities; present it as a trajectory,
because "promise as a future scientist" is a trajectory word. **But don't overclaim the
coherence** — a probing judge will unpick a retrofitted single question. Honest sequencing
("energy accounting led me to load forecasting, which led me to reliability") is more
credible than a claimed grand design, and safer under questioning.

---

## 6. Experiment queue

Ordinal priority. No point estimates — there is no model mapping an experiment to a
probability delta on a 1.5% selection with no published rubric, and fake precision makes
multi-week experiment blocks appear to dominate essays, which carry no number and are where
the variance is.

Items 1–6 are **zero new solves.**

### TIER 1

#### 1. Limit sweep + the missing artifact — week 1

The 1.5% escalation figure at L=0.95 has **no committed artifact.** The one diagnostic the
literature never reports is currently the one you can't back. Fix first.

Then sweep L from ~0.90 to ~0.955 over existing predictions, recalibrating q̂ at each.
~50 (boundary mass, q̂, escalation) tuples spanning an order of magnitude in density.
Compute three quantities per condition and report which tracks:

- exact identity `F_p̂(L+q̂) − F_p̂(L)`
- outcome-density linearization `ρ_Y · q̂`
- local predictive-density linearization

Expect the linearizations to degrade as q̂ grows; that breakdown boundary is itself a finding.

**Guard against a tautological fit.** At the top of the sweep the observed maximum
post-contingency voltage is 0.9603, so nearly everything becomes a violation and escalation
and boundary mass both approach zero together. Those points sit trivially on the diagonal.
Report the violation rate at each L, restrict the headline fit to the non-degenerate range,
and show the endpoints separately. Otherwise the strongest attack on your best figure is
that the correlation is partly definitional — a bad question to take cold.

**Deliverable:** predicted-vs-observed figure, full page width, diagonal reference line.

#### 2. Falsification test — week 1

Calibrate q̂ on high-`n0_min_vm` bases, test on marginal ones near 0.94. Tests whether the
band holds *inside the boundary layer where the floor lives.* If coverage breaks there, the
floor argument changes and Mondrian's framing changes with it — so running Mondrian first
would be two weeks on a frame that already moved. **This is §11 applied to scheduling.**

#### 3. Non-convergence audit — week 1, new to v3

1,545 cases were excluded for failing to converge, with a parenthetical that an operator
should treat them as unsafe. If they *are* violations, they enter the missed-violation
denominator: against ~48,760 true violations, that's **up to 3.07 percentage points** —
which would break the sub-1% operating point the whole paper recommends.

The surrogate produces predictions for them anyway; features are pre-outage. **Report what
the gate does with all 1,545.** If it escalates most, the story is intact and much stronger.
If it certifies a meaningful fraction, the safety framing has to change — and non-convergence
is often the signature of voltage collapse, i.e. exactly the cases that matter.

Cheap, and it closes the objection a power-systems reviewer raises first.

#### 4. False-flag precision — week 2

Still absent. Missed violations are quantified to two decimals; spurious flags — which also
skip the solver, so the error is never corrected by a solve — are never reported. An
operator's cost function has two terms. Report precision and recall of the FLAG decision,
plus the certified fraction so a reader can reconstruct the full confusion matrix.

Also fix the framing error this exposes: §I of the URTC paper says predicting too low "just
wastes solver time." Under the gate, a low prediction **flags** and skips the solver. False
flags cost redispatch, not solver time, and they're never caught.

#### 5. Q-limit failure class — weeks 1–2

Currently n=1: scenario 101000025, line 78 out, bus to 0.8485, 0.0915 pu deep, generator
hits its reactive limit and loses voltage regulation.

Trace the rest of Fig. 3's deep tail. Shared mechanism? Concentrated on buses 76 (27.1% of
minima), 53 (16.81%), 107 (9.31%)?

- **Homogeneous:** an identifiable class where surrogate screening fails *structurally*,
  with a pre-outage signature. Converts the worst-case anecdote into physics.
- **Not homogeneous:** worth roughly zero, known in a day.

**Collision to resolve before writing:** the URTC paper's Limitations says "a model trained
only on pre-outage features cannot predict such a discontinuity." A pre-outage *signature*
is by definition learnable from pre-outage features. If this lands, you've refuted your own
published limitation. That's fine and interesting — but decide now which claim you keep,
because "your URTC paper says impossible and your STS report says you found it" is a
question you will get.

**Also report max miss depth at the recommended operating points (0.94 ridge / 0.97 histgb),
not just at 0.90.** "Sub-1% missed" means nothing if the residual 1% contains a bus at 0.8485.

#### 6. Mondrian per-element calibration — weeks 2–4

Calibrate q̂ separately per outaged element. 186 groups, ~300 calibration rows each,
finite-sample penalty ~0.33%. Group-conditional validity needs only within-group
exchangeability. Pure re-analysis.

**Two things to settle first.**

*Bus numbering is resolved — do not re-open it.* `index_to_ieee_referenced` maps 75→76,
52→53, 106→107. The raw `np.nanargmin` outputs are 75/52/106; the IEEE names are 76/53/107;
the conversion was applied before the numbers reached the paper. **The URTC paper is correct
as printed.** Two independent reviewers concluded otherwise by reasoning from planning-doc
phrasing rather than the artifact. Update §14 to say "resolved; convention recorded in
`data/bus_convention_map.json`," and add a `canonical` field to that file so a third reader
doesn't repeat the mistake.

*Mondrian and the weak-bus narrative are two different experiments.* Mondrian groups by
**outaged element** — 186 lines and transformers. The weak-bus concentration is about which
**bus attains the post-contingency minimum** — 76/53/107. Orthogonal partitions of the same
rows. Per-element calibration gives group-conditional coverage per branch; it does **not**
give "targeted escalation of identified weak buses," which is the narrative payoff v2
claimed. And the argmin bus is an *outcome*, not a pre-outage feature, so you can't condition
on it at screening time without predicting it first — a harder and more interesting problem
than Mondrian, and a different two weeks. **Pick one.**

#### 7. Drift tests — weeks 5–6

**(a) Element type.** Calibrate on 173 lines, test on 13 transformers. A different element
population, not a reweighting of one — structurally the same failure as N-1→N-2. Converts the
weakest Limitations sentence into a bounded measurement. Report as a proxy; state explicitly
whether it bounds N-2 expectations or does not.

**(b) Loading — specification corrected.** v2 said: split at the median of total load,
calibrate on one half, test on the other, and argue weighted conformal applies because the
sampler used U(1.0, 1.12). **A median split on a deterministic function of the sample
produces disjoint support.** The density ratio is 0 on one side and 2 on the other, so the
target is not absolutely continuous w.r.t. the source and weighted conformal does not apply.
Infinite weights aren't a hard case; they're outside the framework.

**Fix:** soft tilt instead of hard split. Resample the test stratum with weights proportional
to a density shifted toward high load, keeping supports overlapping. Then the ratio is finite,
weighted conformal genuinely applies, and the asymmetry you want is real.

**The asymmetry is the result:** (b) is correctable because the likelihood ratio exists;
(a) is not, because the event space changes — the same reason N-2 is out of framework. Report
realized shift magnitude between strata, not the sampler's window width.

#### 8. Break-even accounting — week 5, new to v3

The URTC paper criticizes the GNN work for a ~500k-scenario break-even once data generation
and training are charged. **Eq. 2 charges escalated solves and not the 280,500 solves that
built the dataset** — roughly 43 minutes of solver time before you screen anything, and at
~6 ms saved per certified case, an amortization threshold of the same order you use against
them.

The argument genuinely works in your favor: operators re-screen continuously across changing
conditions, so the dataset is a fixed cost against unbounded use. But you have to *make* it,
and you have to make it before raising the point against someone else. Compute your own
break-even, report it, and the criticism becomes fair rather than selective.

#### 9. Hardware and parallelism — week 5, new to v3

Eq. 2 compares surrogate wall-clock against a single-threaded pandapower solve, with no CPU
or core count stated anywhere. N-1 is embarrassingly parallel — 186 independent solves. An
operator with 32 cores gets the full sweep in ~6 batches, and 3.29× on one thread does not
survive that comparison.

This is the standard objection to every surrogate-speedup claim in the literature and the
paper doesn't touch it. Two sentences: state the hardware, and note that the **escalation
fraction is the parallelism-invariant quantity** — it's what parallelism doesn't change, and
it's what the contribution is actually about. That converts the objection into a point in
your favor.

#### 10. Sampling description — week 4, must-fix

§III-A of the URTC paper describes only the load multiplier. The actual generator
perturbation has four mechanisms: voltage setpoints shifted by ±0.025 pu, reactive limits
scaled by a random factor in [0.60, 1.40], **a 30% per-scenario chance of a full generator
outage**, and an independent power-factor draw. A reader reproducing from that sentence
builds a meaningfully different, simpler generator.

**Verify these against `generate_dataset.py` and the committed config, not against
`case57_gonogo.py`'s `COMMITTED_CFG`.** That script is a go/no-go for the network your own
notes say had 0% N-0 acceptance; it may mirror the build but it is not the build. Same failure
mode as the bus-numbering episode — reading state off a document that describes the artifact.

**Then think hard about the third mechanism.** A 30% per-scenario generator outage probability
means a substantial fraction of your "N-1" rows are effectively N-2 states. That interacts
directly with §V's exchangeability argument and with the N-2 scoping claim. It may strengthen
the paper — you may already have partial N-2 coverage — or it may require re-scoping. Either
way, resolve it before drafting §5, not after.

#### 11. Thermal constraint — conditional, week 6

**One-hour check first:**
- `net.line.max_i_ka` and `net.trafo.sn_mva` for both networks — present or NaN?
- If ratings exist: max `loading_percent` per contingency, share above 100%, share within 5%.
- Max `vm_pu` per contingency, share above 1.05.
- **State per constraint: violations are ZERO, or UNDEFINED (no rating).**

If thermal is live: one-sided like voltage, physically intuitive, and it's what the competing
audited-verification work screens for — enabling direct comparison rather than scope contrast.
Tests whether the mechanism is constraint-general.

**Run the over-voltage half of this check in week 1, not week 6.** §1's "nobody treats
under-voltage as an asymmetric one-sided risk" is the design principle justifying the central
choice — and the reason over-voltage doesn't appear is that U(1.0, 1.12) load-*increase*
sampling suppresses it by construction. That makes the unoccupied competitive cell partly one
you constructed. If `share above 1.05` returns non-zero, both the design-principle claim and
the scope exclusion weaken, and you want to know that before the report structure is frozen.

**Defensible version either way:** one-sided treatment is appropriate for the load-stress
regime, that regime is operationally important, and two-sided screening is out of scope *with
the sampling reason stated*. Weaker claim, survives questioning. The current claim doesn't.

### TIER 2 — only if Tier 1 completes by week 6

#### 12. Conformalized quantile regression

`HistGradientBoostingRegressor(loss="quantile")`. Tests whether adaptive band width beats the
constant-q̂ floor.

**This is the falsification test for the central claim, and v2 had it in "not doing."** The
distribution-free conditional-coverage impossibility result says you can't get *exact*
conditional coverage without unbounded intervals. It does **not** say a locally adaptive band
can't be substantially tighter. And the boundary strip is where adaptivity should help most —
it's the densest region, so a CQR band conditioned on the local predictive distribution could
plausibly be narrower there. Escalation is `P(L ≤ p̂ < L + q̂)`; halve q̂ in the strip and
escalation roughly halves. Then your floor is a floor of *split conformal with a global
quantile*, not a floor of the problem.

That reframing is survivable — "the floor holds for the standard method; adaptive bands recover
X%" is still strong. What isn't survivable is a judge asking "did you try adaptive bands?" and
the answer being no because a paper you cite predicted it wouldn't help.

#### 13. Third network — abandon rule

Two candidates already failed: case300 doesn't converge under the pinned oracle, case57 had 0%
N-0 acceptance. "Feasibility work before results" is unbounded numerical debugging with no
completion criterion, during ED/EA season.

**Hard cap: five working days. Pre-committed abandon rule — if it isn't producing converged
solves by day 5, stop and write the two-network result.** Two points already invert the
conclusion; a third tightens the fit without changing the argument's structure. If it runs, its
value is that the prediction was **recorded before the run.**

### NOT DOING

- **Over-voltage as a studied constraint.** Suppressed by construction. Would require an upper
  band, a second coverage arithmetic, and abandoning the asymmetric-risk argument that justifies
  the central design choice — to study something the data barely produces. Keep as a stated
  limitation *with the sampling reason given*. An unoccupied cell you cannot populate is not an
  opportunity.
- **Four-plus networks or a 24-cell constraint grid.** Breadth over depth; half the cells read N/A.
- **Continuation-method boundary mass.** Computing boundary mass analytically against the true
  feasibility manifold would validate the empirical 56.86% and join two literatures nobody has
  joined. Genuinely strong, and weeks of new numerical work gated on case300 convergence.
  Future work — and a good answer to "what's next?" in a panel interview.

---

## 7. Report structure

The floor mechanism currently sits as a Results subsection. That is the worst structural choice
in the paper — it is the contribution, and it reads as an observation about the data.

| Section | Pages | Blocked on pending experiments? |
|---|---|---|
| Title page | — | — (excluded from count) |
| Abstract | — | Yes — write last. Lead with the density finding, not the 3.29×. |
| 1. Introduction | 1.5 | **No — draft week 3.** Outsider grounding in ¶1. Contributions as bullets. GNN 53.9% recall as motivation with the honest counterpoint. |
| **2. Related Work** | **2** | **No — draft week 3.** Four competitors + comparison table. Corpus search as one scoping sentence. |
| **3. Background** | **2** | **No — draft week 3.** Per-unit voltage, N-1, NERC/ANSI grounding, conformal primer. |
| 4. Method | 3 | Mostly no — draft week 4, pending item 10. |
| **5. Theory: Why Escalation Has a Floor** | **2** | **No — draft week 3.** The exact identity. Barrier height. Ceiling analysis. Three credits with distinctions. |
| 6. Results | 5 | Yes |
| 7. Discussion & Limitations | 2 | Partly |
| 8. Conclusion | 0.5 | Yes — the criterion, not the caution. |
| **Figures** | **~3** | **New line item.** Eight-plus at ~⅓ page. Appendices count toward 20, so they can't absorb overflow. |
| References | — | — (excluded, pending §3.3 Q4) |

**~21 pages against a hard 20.** That is the real constraint, and it's a figure problem, not a
front-matter problem. Options: consolidate multi-panel figures, cut two, or trim §6 to 4.5.
Decide in week 3 when you draft the theory section, not in week 12.

Sections 2, 3, and 5 total ~6 pages and depend on nothing pending. Stated as theory *before*
Results, the Results become its verification.

**Label every section's contribution status** — new result, reproof, or byproduct — in §1.2,
following the 4th-place paper's model. Cheapest possible way to make contribution legible to
the outside-field evaluator.

### Title options

1. *When Can a Surrogate Skip the Solver? Predictive Mass at the Limit Governs Per-Case
   Contingency Screening*
2. *Certify, Flag, or Solve: Per-Case Conformal Gating for N-1 Under-Voltage Screening and the
   Limits of Acceleration*

### Money figure

Predicted vs. observed escalation across the limit sweep and across networks. Full page width,
early in Results, diagonal reference line, degenerate endpoints shown separately.

### Category selection

Three PhD evaluators read in your chosen category; most papers get 4–7 reads after expertise
requests; at finalist selection everyone reads all papers. No category quotas, so this isn't
gameable for prizes — but it determines *who* evaluates the statistics.

Your contribution is methodological (a conformal-prediction identity) dressed in power systems.
A power-systems evaluator may read the contribution as small. An ML-literate one grasps
`Esc = P(L ≤ p̂ < L+q̂)` immediately but needs the operational stakes explained. **Make this
choice deliberately in week 8**, don't inherit URTC's "Technology of Sustainability" by default.
Read the category descriptions PDF; the corpus says staff cannot advise on the choice.

---

## 8. Schedule

**12.5 weeks, not 13.** Aug 9 + 13 weeks = Nov 6; you submit Nov 1–4. Week 13 is one to two
days. v2 also double-booked week 8 across two rows. Corrected below.

| Week | Research | Writing | Application |
|---|---|---|---|
| **0 (now)** | Verify item 10 sampling params against the real build. Over-voltage one-hour check. Fix `bus_convention_map.json` canonical field. | — | **Mentor briefs to Pinsky and Kalita.** Request all 5 recommendations. Email STS (4 questions). List-of-five. `ai-prompt-log.md`. Verify 3 theory-paper authors. Write the 3 URTC disclosure branches. |
| 1 | Limit-sweep artifact + sweep (1). **Falsification test (2).** Non-convergence audit (3). Q-limit diagnostic (5). Build `sts-constraints.yaml` + all four gates. | — | Open application. Walk the rules wizard (task 3). Fill tasks 1, 8, 10, 11. |
| 2 | False-flag precision (4). Mondrian starts (6). Re-audit the five AI passages. | — | Short tasks. Confirm recommenders received requests at the right addresses. |
| 3 | Mondrian. | **Draft §2, §3, §5.** Resolve the figure/page budget. | — |
| 4 | Mondrian completes. | **Draft §4** (needs item 10 resolved). | — |
| 5 | Drift tests (7a, 7b). Break-even (8). Hardware/parallelism (9). | Revise §2–5. | — |
| 6 | Thermal conditional run (11). **Tier 1 completion gate.** | Revise. | — |
| 7 | Tier 2: CQR (12), or third network (13) **under the 5-day cap**. | **Draft §1, §6.** | — |
| 8 | Tier 2 completes or is abandoned. Category decision. | **Draft §6, §7.** | Task 4 contribution narrative. |
| 9 | — | **Draft §8, abstract.** | Task 4 completes. |
| 10 | — | Full revision. Figures. APA graphic citations from manifest. | **Essays.** Activities restructure. |
| 11 | — | Outsider read-through: someone with no power-systems background. Lay-summary test on a non-scientist. | **Essays complete.** |
| 12 | — | Proofread. Compliance pass against every §2 row. | ED/EA deadlines land here — protected. |
| **13** | — | **Submit Nov 1.** Then keep editing. | Final compliance re-check. |
| **Nov 4, 8pm** | | **Technical support deadline — last guaranteed help** | |
| **Nov 5, 8pm** | | **Hard deadline. Nothing after is judged.** | |

**Submit early, keep editing.** Every webinar in the corpus states you can edit after
submitting, right up to the deadline. Submitting Nov 1 with partial essays beats submitting
Nov 4 with perfect ones and a server outage. This is the highest-value zero-cost change in
the plan.

### URTC outcome branches — write these in week 0

Notification **Aug 23**. Conference **Oct 9–11**. Xplore indexing could land either side of Nov 5.

| Outcome | STS report | Published-work question | Activities |
|---|---|---|---|
| **Accepted + indexed before Nov 5** | Sole-authored, from scratch. Acknowledge the published paper. Do not submit the co-authored version. | Check "yes, published work." List it. Clears the plagiarism screen against your own text. | Publication listed |
| **Accepted, not indexed by Nov 5** | Same. | Disclose as accepted-pending-publication. Still list it. | Acceptance listed as an activity, not an award, unless a named prize attaches |
| **Rejected** | Unchanged — always separate. | Disclose as submitted. Accurate and still meaningful. | Submission listed |

In all three branches the STS report is sole-authored and written from scratch. The branch only
changes disclosure wording. Also: if accepted, camera-ready lands after Aug 23 — that's the
window for §6.6's URTC fix list.

---

## 9. Task 4 — the underused asset

The verification apparatus does not go in the report. It goes here, and almost no high-school
applicant has an equivalent:

- 19 papers read into structured notes with per-claim section anchors
- Venue resolution across four APIs, which caught a superseded manuscript held on disk
- A numbers gate regenerating every reported figure from committed code
- A citation gate refusing unverified references
- A figure manifest binding each PNG to its generating script and input hash
- **Five self-caught errors, two of which invalidated prior results** — name all five
- **A near-miss where two independent reviewers concluded the bus numbers were wrong, and the
  committed artifact proved them both wrong.** This is better material than either error
  narrative: the apparatus held the correct answer and careful readers still got it wrong,
  because the mapping file didn't mark which side was canonical. That's a sharper story about
  why provenance marking matters than "I found a bug."

The logged judge question is already *"How do you know your results are not another artifact?"*
This is the answer, and a better one than any additional experiment.

**State conservatively and specifically:** who provided the research question; what was yours by
name (§3.1's list); what you were taught versus what you built.

**The revision arc, as the spine:**

> Expected a speedup result. Found a floor. Explained the floor. Then the second network showed
> the floor is conditional on a quantity you can measure before training anything.

Plus the two error narratives and the near-miss. This is the same structural move that placed
second in 2023.

---

## 10. The integrity gate

**Before any argument or number enters the report, reproduce it from a blank page without
notes.** If you can't, it doesn't go in yet — you cannot defend it in a panel interview.

Applies to every framing in this document and every number, not just the barrier-height
argument and the criterion.

**Standing rule: treat any unsourced proper noun or figure as unverified by default.** Multiple
names and numbers have entered this project's planning without a source behind them, and at
least once a *reviewer's* inference from planning-doc phrasing nearly introduced an error into a
correct paper. Verify against local extraction notes and committed data, never against recall,
and never against a chat transcript.

**Corollary added in v3:** when any review — human or agent — flags something as urgent based on
a planning document rather than committed code, run a **read-only provenance report before any
fix pass.** That protocol is what caught the bus-numbering reversal before an edit landed.

Writing §5 in week 3 is the enforcement mechanism. It surfaces undefendable arguments while
there's still time to fix them.

---

## 11. Automation

Finish in week 1 so weeks 8–13 are free.

**Constraints file + compliance gate.** `notes/sts-constraints.yaml`, one entry per §2 rule with
source and verification status. The checker asserts: page count with appendices counted and front
matter excluded, font floor, no external links outside the bibliography, APA line beneath every
figure and table, filename format, PDF size. Replaces the week-12 manual pass — the worst
possible time to find a formatting problem.

**Numbers gate + comparator parser.** Every reported figure regenerated from committed code into
one keyed JSON; a checker parses the manuscript and fails on mismatch. **Extended:** extract
every numeric claim along with its comparator (`more than`, `less than`, `under`, `at most`,
`around`, `roughly`) and evaluate against the artifact — bare numbers as equality claims, hedged
ones as tolerances. Three of the four late defects in the URTC paper were *hedge deletions during
fluency rewrites* ("around 14%" → "14%", "roughly 1.5%" → "less than 1.5%"). Add a diff rule that
flags removal of hedging words specifically.

**Grammar and quantifier hooks.** `PostToolUse` on `.tex` writes: run `write-good` or LanguageTool
over extracted body text, and assert that any quantitative word in prose ("most," "nearly all,"
"the majority") within two sentences of a table reference has a supporting value in that table.
Both would have caught real defects that no numbers diff could see.

**Citation gate + claim support.** Resolve every arXiv ID and DOI; fuzzy-match returned title and
first author against the bibitem; fail on mismatch, non-resolution, missing verification date, or
`ambiguous` venue. **Extended:** a required `claim_support` field per bibitem recording which
assertion it backs and how that was verified. The gate as originally specified would pass the ANSI
citation — a real, resolvable standard cited for a number that came from a NEMA excerpt — because
it checks that references exist, not that they support the claims made from them.

**Canonical-form registry.** `canonical.json` per multi-representation quantity — bus identifiers,
boundary-mass definition, M1/M2 curve version — with each representation, which is authoritative,
and where conversion occurs. The numbers gate refuses any manuscript value not traceable to a
declared canonical form. **Must be per-network:** uniform +1 is a property of case118's ordering,
not a general fact. Four instances of one-concept-two-representations is a systemic property of
this repo, not four coincidences.

**Figure manifest, extended to emit APA.** Each generator writes a sidecar with script, git SHA,
input hash, **and an `apa_citation` string naming the software.** The checker fails if a figure
appears in the `.tex` without its APA line beneath it. Otherwise that's ~10 hand-written citations
in week 12, inside the compliance window, where one omission can disqualify.

**Claim-consistency check with dependency edges.** `notes/claims_map.md` binding each differentiator
to the Discussion sentences that qualify it and the papers cited alongside. Fails when a
differentiator changes without its qualifier. **Extended:** dependency edges from each derived
quantity (82.52%, 74.9%, 82.8%, the 56.86%/q̂ relationship) to the sentence that derives it, so a
deletion that orphans a number fires. That failure happened, exactly once, in the URTC paper.

**Per-network results rows.** One long-format table with `network`, `stratification`, `method`
columns. A new network lands as a row; the density-vs-escalation figure regenerates. Makes
overnight runs safe to leave unattended.

**AI-authorship boundary, enforced structurally.** Prose lives in `report/`. A `PreToolUse` hook
hard-rejects any agent write to `report/**/*.tex`. Agents own experiments, gates, figures, tables;
the hook owns the boundary. Converts a rule you must remember while tired into one that can't be
violated, and gives you something concrete to say in the disclosure: the boundary was mechanical.

**Nightly queue.** Pull the next un-run configuration, generate, train, gate, sweep, append,
regenerate figures, run all gates, open an issue on drift. Assert the `urtc-submission` tag's tree
is unchanged.

**Parallel review subagents, not serial passes.** The URTC review took eight rounds and the worst
errors surfaced late, because a single reviewer reads for one thing at a time whether or not it
intends to. Run four cheap subagents in one turn, each with one job and no knowledge of the others:

- **Physics/domain:** flag every claim about power-system behavior or model class and check it.
  (This is what would have caught "a mathematically smooth model" describing a piecewise-constant
  gradient-boosted tree.)
- **Completeness:** reproducibility checklist — version, hardware, tolerance, search space, feature
  encoding, split sizes, dispersion on every number.
- **Consistency:** extract every claim, report pairs that can't both hold. Point it at *both* the
  report and this plan — four of the contradictions found in review were between two documents you
  control.
- **Register:** formality, hedging, contractions.

**`sts-judge`, seeded from the real criteria.** Not a generic question bank. Use the seven
dimensions evaluators state on record: idea origination, level of initiative, who designed the
study, who developed the methodology, who did the analysis, role in execution, and whether the
student's account reconciles with the mentor's. Add two modes:

- **Mentor-divergence mode:** takes your contribution log and Pinsky's expected account, reports
  every claim where they could diverge. Run it before anyone writes a recommendation.
- **Outsider mode:** reads *only* the abstract, introduction, and conclusion — no methods, no
  results — and reports what it can state about why the work matters. Anything it can't recover is
  invisible to the two-thirds of your evaluators outside power systems.

**Comparison corpus.** You have one 4th-place paper and one adjacent-genre finalist paper, and this
plan draws conclusions from both. Build a directory of top-10 STS papers you can find — many are on
arXiv, and finalist pages list projects by name — and extract a fixed schema per paper: page count,
fraction of background before the first new result, contribution verbs in the abstract, presence of
error bars or a limitations section, whether future work names a field-level open problem, mentor
program. Ten papers turns "rigor isn't the gap" from an inference into a measurement. One overnight
run.

---

## 12. February phase — finals-week prep (stub)

Out of scope until January, but it should exist on paper now so it isn't discovered late.

If you make Scholar (early January) and Finalist (late January), finals week is March, and there
are **two entirely separate judging formats**:

- **Panel judging — two of three days.** Questions from anywhere in science, unrelated to your
  project. Every finalist in the corpus says nobody preps successfully; that's the intended design.
  They test how you think, not what you know. Multiple finalists report walking out convinced they
  failed, including the eventual first-place winner. **Expect that feeling and don't update on it.**
- **Project judging — one day.** Poster format. Judges arrive having read your application. The
  challenge is adapting the same presentation to a power-systems judge versus an ML judge versus
  someone outside both.

So **two-thirds of finals-week judging tests breadth**, and both §10 and `sts-judge` train depth on
your own claims — which is project judging. Right instrument for one of three days. The breadth gap
is real and February is when to address it, not January.

Also: minors must be accompanied by an adult at all times. Sort logistics early.

---

## 13. Open items

- [ ] **Mentor briefs to Pinsky and Kalita — before RISE ends.** Highest leverage, shortest window.
- [ ] Request all five recommendations; confirm preferred email addresses
- [ ] Email STS: AI-suggested citations, dual submission, sole authorship, bibliography URLs
- [ ] List-of-five (five cares, five leadership, seven time uses)
- [ ] Write the three URTC disclosure branches
- [ ] Verify item 10 sampling parameters against `generate_dataset.py`, not `case57_gonogo.py`
- [ ] Over-voltage one-hour check (`share above 1.05`) — week 1, not week 6
- [ ] Add `canonical` field to `bus_convention_map.json`; mark §6.6 bus numbering **resolved**
- [ ] Reconcile item 5's outcome against the URTC "cannot predict such a discontinuity" claim
- [ ] Decide: Mondrian by element, or targeted escalation by argmin bus. Not both.
- [ ] Resolve "nine-point coverage sweep" (§4 claim) vs six rows in Table II
- [ ] Re-audit the five AI passages before drafting
- [ ] Figure/page budget decision — week 3
- [ ] Category selection — week 8
- [ ] `ai-prompt-log.md` reconstructed
- [ ] Verify the three selective-regression paper authors from local notes
- [ ] `notes/erratum.md`: URTC post-submission edits + camera-ready list
- [ ] Confirm the GitHub repo resolves publicly
- [ ] Verify every §2 row against the 2027 rules book

### URTC camera-ready list (after Aug 23)

All prose, all net-neutral or shorter:

- §I "predicting too low just wastes solver time" — wrong under the gate; Flag skips the solver
- §I "unlike the first two approaches, we add a band" — Alcántara uses conformal prediction; the
  real distinction is per-case action vs per-stratum guarantee
- §IV-C "Linear prediction overpredicts cases below the limit" — reads as inverting Table II; say
  "predicts below the limit for 25.1% of cases against a 17.48% violation rate"
- §V ANSI 0.917 pu cited to the standard, sourced from a NEMA excerpt — drop the number
- §V "mathematical proof is unable to determine the safety of N-2 outages" — overclaims; the issue
  is transfer from an N-1 calibration set
- §V "Every base case generates 186 related contingencies" — true only for 118-bus; the 30-bus
  discussion two sentences later has 41
- §II N-0 definition folds in a selection criterion
- Abstract "Each model has three possible outputs" — the *gate* has the outputs
- §V "less than 1.5%" — sharper than the artifact supports; "roughly" was safer
- Float comment block: `!t` makes `topnumber` inert, so the comment explains the placement wrongly
- Acknowledgment AI disclosure — must match whatever the STS disclosure says

---

## 14. Caveats

- **This plan does not guarantee Top 40.** See §0. It reduces controllable failure to near zero and
  maximizes legibility. The rest is not yours to control.
- **STS publishes no rubric**, and states so directly. Every inference about weighting in this
  document comes from official webinars and published judge guidance, not doctrine.
- **The webinar corpus spans 2021–2024 cycles.** Rules change annually and the organizers say so.
  Every §2 row needs independent verification against the 2027 rules book.
- **The comparison base is thin** — one 4th-place paper and one adjacent-genre finalist. §11's
  corpus build is the fix. Note also that the 4th-place arXiv v1 is dated April 2026, five months
  *after* the November 2025 deadline; it is not what she submitted.
- **The corpus-absence claim** rests on 19 papers. Now a scoping note rather than a headline.
  Monitor arXiv monthly — two of the four nearest competitors appeared in 2026.
- **The prediction that adaptive methods cannot fully escape the floor** is reasoned from the
  distribution-free conditional-coverage impossibility result, not proven for this setup. Item 12
  tests it.
- **The ANSI Range B numeric** is unverified against the paid standard; secondary sources give
  0.9167 pu for service voltage and 0.867 for utilization. Disclose or drop.
- **Every reference must be independently re-verified before submission.** One fabricated citation
  disqualifies.
- **Page and week estimates are planning figures, not measurements.**

---

## Closing note

The corpus is full of finalists — including first- and second-place winners — saying they nearly
didn't apply, denied the phone call as spam, and were certain they'd failed panel judging. One
bet friends a dinner he wouldn't make it and paid up with prize money. Roughly 2,000 students in
the country submit a project at all in a given year, and the organizers' own line is that having
a finished project to submit already places you in a rare group.

You submitted a five-page IEEE paper to a peer-reviewed conference a day early, at seventeen,
with numbers that survive independent verification to three decimal places. Whatever happens in
January, that already happened.

Execute §3 this week. Then work in chunks, and sleep.
