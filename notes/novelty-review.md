# Prior-work check: conformal band as an escalation-to-solver gate

**Bottom line up front.** Your core differentiator — a calibrated (conformal) prediction band
used as an *escalation/abstention* signal that routes uncertain cases to a costlier oracle,
with honest end-to-end compute accounting, is **not novel as a mechanism**. It is well
developed in two literatures you may not have been looking at: LLM cascade/routing serving, and
conformal medical triage. What I could not find published anywhere is your specific
*instantiation*: the escalation target being an **exact numerical solver** (physics ground
truth); the band living in the **physical units of a safety limit** (0.94 pu voltage), a
**three-way** certify/flag/escalate gate, and a **net-speedup metric that charges the escalated
solver time back against the surrogate's savings**, all in power-systems contingency screening.
Verdict: **(b) a novel application of a known mechanism.** Details and ranking below.

## The mechanism is already published

The closest precedents are not in power systems. The **LLM cascade / model-routing** literature
has, in the last year, converged on exactly your control loop: calibrate an uncertainty score,
set a threshold by explicit cost minimization, and *escalate* the cases above threshold to a
more expensive model, then report end-to-end cost. [UCCI](https://arxiv.org/abs/2605.18796) is
the sharpest single match: it maps model uncertainty to a per-query error probability and picks
the escalation threshold by *constrained cost minimization*, proving the threshold policy is
cost-optimal. This is your "escalation rate vs. net speedup" trade-off, formalized.
[C3PO](https://arxiv.org/abs/2511.07396) does the same under *probabilistic cost constraints*
with test-time compute control, and [RouteNLP](https://arxiv.org/abs/2604.23577) adds
conformal-prediction thresholds specifically to the routing decision. The one difference that
matters: their escalation target is a bigger *learned* model, not a ground-truth exact solver,
and there is no physical safety threshold, so "correct" is defined by the large model rather than
a hard limit. So they pre-empt the *cost-accounted escalation* half of your contribution, but not
the *exact-solver / physical-limit* half.

The other precedent is structurally even closer to your **three-way** gate.
[Conformal triage under prevalence shift](https://arxiv.org/abs/2605.20956) converts predictive
scores into a three-way action, *release* a case, *flag* it for urgent attention, or *defer*
it to human review, which is your certify / flag / escalate gate, one-for-one, in a medical
deployment. The escalation target there is a human reviewer rather than a solver, and there is
no compute-budget or net-speedup accounting (the "cost" is human-review load, not solver time).
But if a reviewer asks "isn't a three-way certify/flag/escalate gate just conformal triage?",
you need an answer ready: the honest one is that the *structure* is the same, and only the *escalation
target and cost model* differ.

## The abstention primitive itself is decades old

Underneath both of those, the "conformal band as a reject/abstain decision" primitive is
standard. [Conformalized Selective Regression](https://arxiv.org/abs/2402.16300) uses a
conformal band to let a *regressor* abstain under high uncertainty, the same object you build
(a band on a continuous prediction, abstain when it straddles a decision point), minus the third
state and the solver. [Classification with Reject Option via Conformal Prediction](https://arxiv.org/abs/2506.21802)
gives the distribution-free error guarantee for accepting only confident (singleton) conformal
predictions. These establish that "wrap a conformal band around a prediction and abstain when it
is uncertain" carries no novelty on its own. The reject option itself dates to the 1950s, as the
selective-regression paper notes. Your one-sided band in the safety-critical direction is a
sensible engineering choice, not a new construct.

## In power systems: a near-empty intersection

Within power systems, conformal prediction for contingency work is essentially a single-paper
field right now, and that paper is the one you already have.
[Your known prior work](https://arxiv.org/abs/2602.07995) (cite as arXiv:2602.07995v2: the 2602
identifier is a February 2026 submission and the v2 PDF is stamped 21 April 2026, so both dates are
real; the earlier "February 2026, not April" note here was itself imprecise and is corrected. A
full-text read on 2026-07-21 further found the paper's scope is voltage CLAIMED but thermal
DEMONSTRATED, see prior-art.md section 6) is the only hit for "conformal + security assessment" on
arXiv. As you say, its gate is *binary* (flag if the bound exceeds the limit), it reports
precision/recall, and it has no escalation-to-solver and no compute-budget accounting. Your
three-way gate and net-speedup metric are genuinely beyond it.

The rest of the ML-for-contingency literature is surrogate-screening without the conformal
control layer. [Graph Neural Networks for Fast Contingency Analysis](https://arxiv.org/abs/2310.04213)
is a topology-aware surrogate for N-k screening: it is the "fast approximate screen" you are
accelerating, yet it has no uncertainty band, no escalation, and no coverage guarantee.
[Decision-calibrated prediction sets for robust power system operations](https://arxiv.org/abs/2606.02081)
is the newest conformal-in-power-systems work, but it embeds calibrated sets as *uncertainty
sets inside a robust-optimization problem*, a different use of the same statistical tool, not a
screening-and-escalation gate. Neither pre-empts you.

## Scientific-computing analogue: multifidelity, not conformal

Outside power systems, the "cheap model with expensive-solver fallback" idea exists as
**multifidelity / active-learning** surrogate modeling, where a model's predictive uncertainty
*triggers a high-fidelity simulation*. But across the arXiv and OpenAlex sweeps I found no work that:

- uses a *conformal* band with a coverage guarantee as the trigger,
- triggers against a *physical safety threshold* rather than a variance or acquisition score,
- reports honest *net* speedup counting the triggered high-fidelity time.

Multifidelity active learning is a training-time acquisition loop; yours is a test-time triage gate
with a statistical guarantee. The two are cousins, not the same thing.

## Ranked by closeness to your differentiator

1. **LLM cascade routing with calibrated-uncertainty escalation + cost optimization**: [UCCI](https://arxiv.org/abs/2605.18796), [C3PO](https://arxiv.org/abs/2511.07396), [RouteNLP](https://arxiv.org/abs/2604.23577), [Edge-Cloud Conformal Alignment](https://arxiv.org/abs/2510.17543). *Closest on the mechanism:* calibrated score, cost-optimal escalation threshold, escalate to costly model, report end-to-end cost. **Differs:** escalation target is a larger learned model, not an exact solver; no hard physical limit ("truth" = big model); binary accept/escalate, no distinct "flag" state.
2. **Conformal triage (release / flag / defer)**: [Deployment Audit of Conformal Triage](https://arxiv.org/abs/2605.20956). *Closest on the three-way gate structure:* release/flag/defer maps one-to-one onto certify/flag/escalate. **Differs:** escalation target is a human reviewer; medical domain; cost is review load, with no solver-time or net-speedup accounting.
3. **Your known power-systems prior**: [Trustworthiness Layer for FMs](https://arxiv.org/abs/2602.07995). *Closest in domain and coverage framing* (90%, one-sided, N-k generalization on IEEE 24/118). **Differs:** binary gate, precision/recall, no escalation, no compute accounting, exactly as you characterized it.
4. **Conformal abstention / reject-option primitives**: [Conformalized Selective Regression](https://arxiv.org/abs/2402.16300), [Reject Option via CP](https://arxiv.org/abs/2506.21802). *The underlying tool.* **Differs:** two-way (predict/abstain), no solver, no cost accounting, no domain.
5. **Surrogate contingency screening & multifidelity fallback**: [GNN Contingency Analysis](https://arxiv.org/abs/2310.04213), multifidelity active-learning surrogates. *The thing you are accelerating / the non-conformal analogue of your fallback.* **Differs:** no conformal band, no coverage guarantee, no physical-threshold trigger.

## Verdict

**(b) a novel application of a known mechanism.** Be clear-eyed about which parts are which:

- **Not novel:** using a calibrated/conformal band as an escalation-or-abstention signal, and
  choosing the escalation threshold by cost. This is the explicit subject of the LLM-cascade
  papers, and the three-way release/flag/defer structure is the explicit subject of conformal
  triage. Do not claim "first to use a conformal band to route uncertain cases to a more
  expensive oracle," and do not claim the three-way gate as a novel decision structure. Both
  claims are refutable with a single citation.
- **Defensible as novel application:** the *combination*, in power-systems contingency
  screening, of (i) a conformal band expressed in the physical units of the operating limit
  (voltage pu) rather than an abstract score, (ii) an **exact AC solver** as the escalation
  target with the surrogate certifying the easy cases, (iii) a **net-speedup metric that charges
  escalated solver time back** against the savings (the honest end-to-end accounting the cascade
  papers do for dollars and the triage paper does not do at all), and (iv) the N-1→N-2 coverage
  stress test. I found no paper combining these, and in particular none pairing conformal
  escalation with an exact numerical solver under a physical safety limit.

Frame the contribution as *the escalation-with-cost-accounting idea, instantiated for
solver-in-the-loop contingency screening with a physical-unit conformal band*, and cite the LLM
cascades and conformal triage explicitly as the mechanism precedents, so a reviewer sees you
know where the idea comes from. The risk is not being scooped on the instantiation; it is that a reviewer who knows the cascade literature will read an over-broad novelty claim and
discount the paper. Claiming (b) and citing (1)-(2) up front is both more honest and more
defensible than claiming (a).
