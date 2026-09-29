# Top5-5 — abstract and introduction structure (content order only)

Fix specification, not prose. Every sentence of the fixed passages is the author's (GUIDE2027 rule 1;
RULES2027 App. 4; `sts-constraints.yaml` R04/R22/R27). Nothing below is wording to paste.

## 1. Ledger ID(s) + severity
- **Top-5 #5** (MAJOR). Also carries: **OS-1** (abstract last sentence), **OS-2** ("three distinct ways" /
  scope listed as a contribution), **NS-03**, **NS-19**, **NS-20** (abstract vs intro prior-work
  categories), **STS-06** (no question/hypothesis), **STS-19** (abstract gives numbers, not mechanism),
  **C3/Top-5 #2(b)** ("must" floor) where it touches l.101.
- Claim ceiling: `notes/panel_ledger.md` §6 (content proposal) + `CLAUDE.local.md` "Honest claim ceiling".

## 2. Anchors (verbatim first ~8 words + line)
| Line | Anchor |
|---|---|
| 63 | `\title{\textbf{Conformal‑Gated Surrogate Screening for N‑1 Under‑Voltage` (title; retitle = author-decision §5) |
| 81 | "The power system grid should remain resilient following" (abstract, one paragraph, 282 words) |
| 97 | "Power grids must be able to stay operational" (intro ¶1) |
| 99 | "One method to improve performance is to replace" (intro ¶2) |
| 101 | "There have been several approaches when it comes" (intro ¶3, ends with the three-ways list) |

## 3. Old text (verbatim)
**l.81 (abstract, complete):**
> The power system grid should remain resilient following the loss of any individual component. The N-1 constraint uses an AC power flow solver for each loss event of the grid elements to determine the voltage of the remaining components. With operators running every combination and repeatedly testing under different conditions, it becomes computationally expensive. Past work has either replaced these solves with surrogate models that check a group of cases at once, return a binary risk classification, or claim no missed unsafe scenarios with only a simple direct current (DC) model. In this study, I attach a one-sided split-conformal prediction interval to the predicted minimum post-contingency voltage for a ridge regression and a gradient-boosted model. For each model, there are three potential outcomes: classify the scenario as safe if the band is above 0.94 per-unit, flag it if the prediction is below the limit, or escalate the situation to the solver if it is a borderline case. On the IEEE 118-bus AC network at 90\% coverage, the gradient-boosted model is 3.29 times faster than the solver but misses 4.72\% of violations. For the gradient-boosted model, first going just under a 1\% mean missed rate at a 0.97 coverage target results in a 63.7\% escalation and speedup dropping to roughly 1.58, with error bars going slightly above 1\%. In the IEEE 30-bus system, using a base case that is thermally feasible, where the regenerated 30-bus network has 7.09\% of its contingencies in the [0.94, 0.945) boundary band compared to 56.86\% for case118, the gradient-boosted model at 0.97 coverage results in a 5.84$\pm$1.25\% escalation. These results allow operators to make an informed decision about whether surrogate screening would be worthwhile on a specific network.

**l.99 (last sentence only):**
> I add the solver time for escalated cases to the screening gate's total time to reflect the true end-to-end cost.

**l.101 (from the contribution list to the end):**
> My work stands out from these papers in three distinct ways. First, unlike the first two approaches, I add a three-way gate to each contingency. Second, I specifically check for only under-voltage issues. Finally, I explain why there must be a certain floor for escalation.

(l.97 and the prior-work sentences of l.101 are structurally fine; they are anchors for order only.)

## 4. What must change (content, in this order)

### 4a. Abstract — five content slots, in order
The abstract currently runs context → prior work → method → three numbers → a generic closing. The
panels (NS page-1 test, STS-19) could not extract the question, the mechanism, or whether case30 was a
success. Required order:

1. **Question** (one slot). Content: under what conditions a calibrated gate on a fast surrogate saves
   AC solves while holding missed violations near 1%, and what quantity sets the saving. It must be a
   question or a testable expectation, not a list of differences (STS-06: judges score the question
   first). Context about N-1 cost may precede it but should shrink to what the question needs.
2. **Mechanism** (one idea, words not symbols). Content: a case is sent to the solver when its
   prediction lands within one band width above the limit, so the share sent to the solver tracks how
   much of the voltage distribution sits just above the limit (the boundary mass) times the band
   width. If the cross-network result (E2a) is cited here it carries its scope: few target networks
   and one named failure (case24, ridge). "Boundary mass" must be defined in plain words at this
   first use, or not named in the abstract at all (C12).
3. **Honest headline on case118** — the operating point the author chooses in the §5 headline
   decision, with ± and the split count above 1%, and the throughput it costs. The unfavorable part is
   the result and must not be softened (CLAUDE.md §3, §9; NS "three strongest parts" #2).
4. **Why case118 behaves this way, scoped** — the sampler places base cases at the limit (N-0
   acceptance at the same 0.94; generator set-point floor equal to the limit, P-007); removing the N-0
   acceptance filter halves the boundary mass. Scoped to "this sampler on this network" — not a network
   property (ledger §6; D8).
5. **When it pays** — the regenerated case30 contrast with **the same metrics as case118** (boundary
   mass, escalation, missed, speedup), so the reader can tell it is a success (NS page-1 test (c);
   NS-12). Then the operator-facing consequence (why it matters): the boundary mass can be measured
   from solved data before a surrogate is trained, so it signals in advance whether a gate will pay on a
   given network and operating-point distribution. The current last sentence (OS-1) is replaced by
   this content, not kept alongside it.

Content the abstract must NOT drop if space allows only one extra clause: that the missed rate is
measured against the solver's labels (P-003/N2) — the author decides whether this lives in the
abstract or only in §III/§V; it must at least be in the body before any missed rate is read as physical.

Prior-work sentence in the abstract: if kept, its three categories must map one-to-one onto the three
papers described in l.101 (NS-20). The current "check a group of cases at once" matches none of the
three intro descriptions. Dropping prior work from the abstract is acceptable and saves words.

Terms used in the abstract that the panels flagged as blocking (NS-13): surrogate, conformal,
coverage, escalation, per-unit, [0.94, 0.945) notation, case118. Each is either defined at first use,
replaced by plain content, or removed from the abstract (P-017 carries the full term table; C4 the
coverage word).

### 4b. Introduction — order of paragraphs
1. l.97 context (keep; NS-26: the criterion does not "use" a solver — that is l.81 only).
2. l.99 failure mode of point surrogates (keep). The last sentence (net-cost accounting) uses
   "escalated" before it is defined (NS-19) and is not a delta against Manoharan, who reports net AC
   solves (`notes/sts_review.md` l.506; lit note §3). Either move it after the gate is introduced or
   drop it from the delta list.
3. l.101 prior work (keep the three papers; the Manoharan sentence must say thermal-only — P-028).
4. **New slot: the research question(s)** with what outcome would count as each answer (STS-06).
   Candidate questions the data can answer (content, author picks and phrases):
   - Q1: at a ~1% missed-violation rate, what fraction of AC solves does the gate avoid on case118, and
     is that fraction stable across splits?
   - Q2: does the escalation rate follow the boundary mass × band width across networks, and what sets
     the boundary mass on case118 (network vs sampler)?
   - The project's RQ1 (N-1 → N-2 coverage transfer) is NOT answerable from the current paper (N7
     propose-only; only 2D line→trafo drift exists) and must not be posed as answered.
5. **Replace the three-ways list** with only the differences that are contributions, each tied to where
   it is shown (NS-19). Content that survives the claim ceiling:
   - three-way per-contingency gate with an exact AC solver as the escalation target (vs Alcántara's
     binary flag, Manoharan's population audit) — instantiation, not method novelty;
   - a measured, predictive account of when escalation is high (boundary mass × band width), with its
     case118 cause traced to the sampler.
   Remove: "I specifically check for only under-voltage issues" (a scope choice; belongs in Background
   l.107 where the scope is already stated) and "there must be a certain floor" (refuted by the
   paper's own case30 result and by the Mondrian run, Top-5 #2(b)/C3).
6. Optional last intro slot: a one-line roadmap of the answer (question → where answered). Only if
   pages allow.

## 5. Numbers (as they would be cited; source → key; status)
All re-read with `.venv/bin/python` on 2026-09-27 by the spec writer unless marked otherwise.

| Value | Source → key | Status |
|---|---|---|
| histgb @0.90: escalation 30.6 ± 2.5%, missed 4.72 ± 0.98%, speedup 3.29 ± 0.30× | `data/tradeoff_curve_v2.json` records (target 0.90); `frozen_poster_numbers_v2.json` → `four_metrics_at_90pct_coverage.histgb` (means 0.30625 / 0.04717 / 3.2871) | re-read OK |
| Test-picked histgb @0.97: missed 0.83 ± 0.24%, escalation 63.7 ± 5.1%, speedup 1.58 ± 0.12×; 2 of 5 splits > 1% (1.162, 1.032) | `frozen_poster_numbers_v2.json` → `safety_operating_points.histgb[4]`; ± and per-seed from `data/sts_e12_e13_conditional.json` → `summary.histgb.any_miss."0.97".missed_viol_rows` / `tuned_metrics.json` sweeps | re-read OK |
| Test-picked ridge @0.94: missed 0.79 ± 0.21%, escalation 64.3 ± 2.8%, speedup 1.56 ± 0.07× | `safety_operating_points.ridge[1]`; `data/sts_n1_class_conditional.json` → `summary.ridge.global_reference."0.94"` | re-read OK |
| **Held-out (E5)** histgb: inner targets [0.96, 0.97, 0.97, 0.96, 0.96]; missed 1.15 ± 0.27% (per split 1.61, 0.80, 1.03, 1.05, 1.23 → 4 of 5 > 1%); escalation 59.3 ± 4.0%; speedup 1.69 ± 0.12× | `data/tuning_search.json` → `selections[seed].histgb.m2` + `records[].inner_cov_at` × `data/tuned_metrics.json` → `records[metric=m2].sweep` | re-read OK (recomputed) |
| Held-out ridge: inner targets [0.97, 0.94, 0.96, 0.92, 0.94]; missed 0.77 ± 0.78% (1 of 5 > 1%: 2.24); escalation 65.4 ± 8.1%; speedup 1.55 ± 0.22× | same | re-read OK (recomputed) |
| Certify-only speedup (flagged cases also solved): histgb @0.97 1.24×, ridge @0.94 1.12× | `data/sts_n1_class_conditional.json` → `summary.{histgb,ridge}.global_reference.{"0.97","0.94"}.certify_only_speedup` | re-read OK |
| Boundary mass case118 56.86%; violations 17.48% | `data/unconditioned_base.json` → `committed_gated.boundary_0p94_to_0p945_pct`, `.violation_rate_pct` (= frozen v2) | re-read OK |
| Unconditioned build (no N-0 filter): boundary mass 28.83%; violations 56.04% | `data/unconditioned_base.json` → `unconditioned.boundary_0p94_to_0p945_pct`, `.violation_rate_pct` | re-read OK |
| case30 regenerated: boundary mass 7.09% (7.0862); violations 15.40% (15.3967) | `data/case30_thermal/case30_thermal_frozen.json` → `boundary_mass_pct`, `violation_rate_pct` | re-read OK |
| case30 regenerated histgb @0.97: escalation 5.84 ± 1.25%, missed 0.76 ± 0.20%, speedup 17.91 ± 3.71× | same file → `records[family=histgb, coverage_target=0.97]` (5 seeds, ddof 0) | re-read OK (recomputed) |
| ρ·q̂ vs escalation: r = 0.8105 (log-log 0.9176), 132 points; case24 ridge median ratio 0.3408, 9/9 below 0.5 | `data/sts_crossnet_scatter.json` → `all_points.pearson_r_linear`, `.pearson_r_loglog`, `per_network_family[2]` | re-read OK (untracked file) |
| Static training-frequency ranking at the gate's full solve budget: 99.41 ± 0.16% vs ridge gate 97.04 ± 0.44%; 96.64 ± 0.50% vs histgb gate 95.28 ± 0.98% | `data/baselines.json` → `comparators.static_severity.curve_mean/curve_std[k−1]`, k = 138 / 89 | static values re-read OK; gate values = lead-VERIFIED (ledger §Commands C5) |
| Label audit (N2): 4,615 of 48,749 stored violations (9.47%) flip to safe; 2,162 safe → violation; corrected boundary mass 56.22% | `data/sts_n2_label_audit.json` → `violation_rate.*` | Reported (read, not recomputed; untracked; ledger §4 still says "pending") |

Std-rule checks for comparisons the abstract/intro may make:
- histgb vs ridge at the ~1% points (0.83 ± 0.24 vs 0.79 ± 0.21; 63.7 ± 5.1 vs 64.3 ± 2.8): gaps below
  the larger std → **tie**; no ranking may be stated.
- Held-out vs test-picked histgb missed (1.15 ± 0.27 vs 0.83 ± 0.24): gap 0.32 > 0.27 → real, but only
  just; state both, do not call held-out "worse by X" as a finding.
- case118 vs case30 escalation (63.7 ± 5.1 vs 5.84 ± 1.25): gap far above both stds → real.
- Static ranking vs gate (full budget): 99.41 ± 0.16 vs 97.04 ± 0.44 (gap 2.37) and 96.64 ± 0.50 vs
  95.28 ± 0.98 (gap 1.36) → both real (lead-verified D14).

## 6. Must not claim
- No "first", "novel", "novel method"; no conformal-method novelty (the closest prior work already uses
  locally adaptive conformal on IEEE-118; `prior-art.md` §6.3-6.4).
- No network-general law: ρ·q̂ tracks escalation on the tested networks with a named failure; the
  effective number of independent target networks is small (STATS-07).
- Not "the network sets the boundary mass" / "inherent" (D8; P-007).
- Not "there must be a floor" (case30 5.84%; Mondrian 42.9 ± 1.9% at 1.45 ± 0.30% missed,
  `data/mondrian_element_summary.json`, re-read OK — see C12.md §5).
- Not "the faster model is not safer" at matched cost (C8/D-c).
- Speedup is 1/escalation restated — not independent evidence; do not present escalation and speedup
  as two findings.
- No physical missed rate: missed rates are measured against pandapower's labels; ~9.5% of stored
  violations flip under a consistent PV/PQ re-solve (N2). No sentence may imply the 1% is a physical
  grid-safety rate.
- The 1% target is the author's chosen tolerance, not an operating standard (P-013).
- Not "answers N-1 → N-2" (N7 not run).
- "ρ measurable before training" means from solved data; it does not avoid the solves that build the
  dataset — do not imply a zero-solve predictor.

## 7. Consistency (must change in step)
- Title l.63 (retitle = author-decision §5): must match the claim strength the abstract ends on (NS-07).
- Conclusion l.388: same question, same headline operating point, same scoping of the cause; drop
  "reasoning for the existence of such a floor" and "Future work … more networks" (C1/OS-7).
- IV-A l.231, IV-C l.349, Fig. 2 caption l.281: same headline operating point and split count (E5c).
- Discussion l.361 ("I also explain why the speedup is capped") and l.365 ("escalation floor", checker
  phrase OS-10): same scoping.
- The boundary mass 56.86% the abstract cites is printed at **l.121** (clip paragraph), **l.314**,
  **l.365**, and as 56.9 at **l.323** (Fig. 4 caption; → 56.86 per numbers-2b 2b-3). All must be the
  same value and the same defined quantity (C12). l.121 comes before the IV-C definition point, so its
  wording depends on where C12 places the definition.
- Every number the abstract cites must be in the body first: E1b (unconditioned build), E2a (ρ·q̂),
  E4 (case30 speedup), E5 (held-out), E8 (certify-only), P-009 (static ranking). The abstract cannot
  lead the body.
- C4 (coverage vocabulary), C12 (boundary-mass definition), P-017 (terms), P-018 (case30 is not the IEEE
  30-bus PF case — "IEEE 30-bus" at l.81 must change with it).

## 8. Page cost + dependencies
- Abstract: on its own unnumbered page (R05/R12) → 0 counted pages. Length: currently 282 words; the
  application's abstract-field word limit is **unverified** (STS open question, `round1_sts_judge.md`
  §4) — keep the reordered abstract ≤ current length.
- Intro: +1 question slot (~+0.07), −1 scope item and −"must" (~−0.03), l.99 last sentence moved/dropped
  (~−0.02). **Net ≈ +0.02 pp.**
- Blocking dependencies: §5 headline operating-point decision (test-picked vs held-out vs N1);
  title decision; P-001/P-003/N2 outcome; E1b/E2a/E4/E5/E8/P-009 placed in the body; C12 definition.
- Do this **last** in the prose pass (ledger §2 Step 5), after the body numbers are fixed.

## 9. Voice note
The NS reader's own three-line summary (question / answer / why it matters, `round1_nonspecialist.md`
§0) is the test: after the rewrite, a non-specialist should be able to write it without guessing.
