# Round-1 blind panel — Power-systems PhD (contingency analysis, voltage stability, operator practice)

Paper: `report/paper_current_STS.tex` (compiled text `notes/panels/round1_paper_text.txt`, 2026-09-27).
All throwaway scripts and outputs: `/Users/rajansaha/.claude/jobs/484f4ac7/tmp/panel_power/`
(`a1.py`..`a7.py`, `pvpq.py`, `relabel.csv`, `relabel2.csv`). All solves used `.venv/bin/python`,
pandapower 3.5.4, the pinned config (`enforce_q_lims=True`, `init="dc"`, numba, NR) unless stated.
Bus names in prose are IEEE 1-based; code indices are given as `index` where needed.

---

## 1. Rubric (power-systems point of view)

| Criterion | Score | One sentence |
|---|---|---|
| Originality | 5 | A conformal band with a three-way certify/flag/escalate gate on AC min-voltage is a sensible combination, but the headline mechanism ("boundary mass") is mostly a property of how the author sampled operating points, not a discovery about the network. |
| Rigor | 4 | The statistical protocol (5 splits, locked cross-network hashes, audits) is careful, but the physical data layer was not checked: violation labels come from solver states where generators are pinned on the wrong side of their reactive limits, and the sampler that creates the boundary mass is not fully disclosed. |
| Significance | 3 | For an operator, a 1.2–1.6x reduction in AC solves on a 118-bus case (N-1 in about 1.7 s serial) at about a 1% missed-violation rate is not operationally attractive; the settings where it would matter (large systems, many base cases) are not tested. |
| Clarity | 6 | The gate and the accounting are easy to follow; several physics statements are loose or wrong (why voltage drops after an outage, what "N-1" means when a generator is already out, why case57 fails). |
| Student potential | 8 | The clip-artifact catch, the honest thermal and over-voltage scoping, and the audit trail show real scientific instinct; the problems below are fixable and a strong student can defend the fixes in interview. |

---

## 2. Findings

### POWER-01 — FATAL — The featured "deepest miss" is a solver artifact, and the paper's physical explanation of it is wrong

**Anchors.**
- `.tex` l.292: "The worst miss was a case at 0.0915..."
- `.tex` l.303 (Fig. 3 caption): "The deepest miss falls 0.0915 pu below the..."
- `.tex` l.367: "In addition, the worst case, at 0.0915 per..." The paper says the generator at the weakest bus "reaches the limit of reactive power and can no longer control the voltage."

**Evidence.** VERIFIED: I rebuilt scenario 101000025 with line 78 out (IEEE 51–58), using `scripts/miss_mechanism.rebuild_scenario`. Scripts: `a3.py` and `a4.py`.
- pandapower (pinned config) reproduces min_vm 0.8485 at IEEE 54. At that solution, generator 21 at IEEE 54 is pinned at its **absorbing** limit (Q = −194.7 Mvar = its scenario `min_q_mvar`) while its terminal voltage is 0.8485 pu against a setpoint of 0.9549. The repo's own `data/qlims_off_check.json → gen21_reactive_state` also records Q going from −10.0 to −194.7 Mvar, pinned at `min_q_mvar`.
- An excitation system at 0.85 pu terminal voltage is at maximum output, producing vars, not absorbing 195 Mvar. The state therefore breaks the PV/PQ complementarity condition. A unit held at Qmin must have V ≥ Vset; a unit held at Qmax must have V ≤ Vset.
- pandapower's `enforce_q_lims` switches PV buses to PQ in one direction only and never releases them. At this solution, four generators are pinned on the wrong side (gens 16, 21, 22, 32).
- I re-solved the same contingency with standard PV/PQ switching plus back-off (release a pinned unit when its voltage moves to the wrong side of its setpoint; `pvpq.py`). It converges in 3 outer iterations to **min_vm = 0.94507 at IEEE 27**. That equals this scenario's N-0 minimum (0.94507, `data/deepest_miss_case.json → part2_case.n0_base_min_vm`), so the contingency does not violate at all.
- In PV mode (no limits), several nearby units circulate large reactive power against one another:
  - IEEE 56 (gen 23) produces +285 Mvar against a 14.4 Mvar cap.
  - IEEE 55 (gen 22) absorbs −56 Mvar against a −7.5 cap.
  - IEEE 54 absorbs −196 Mvar.
  - Setpoints: 0.9549 / 0.9583 / 0.9721 at IEEE 54/55/56.
  - This is the classic "fighting generators" pattern from independently perturbed setpoints on electrically close units (see POWER-04).

**Why FATAL.** A power-systems judge who asks "which reactive limit?" gets "the absorbing one, at 0.85 pu", and the collapse story fails on the spot. The number is printed three times, one of them in a figure caption.

**Suggested fix (content).**
- Recheck the deepest misses with a PV/PQ logic that enforces complementarity, or at least test every labelled row for complementarity after the solve.
- Drop the collapse narrative, or rebuild it on a validated case.
- If any deep-miss story survives, name the limit (absorbing or producing) and the unit.

---

### POWER-02 — MAJOR — Violation labels, and especially the deep tail, depend on the one-way PV→PQ switching artifact

**Anchors.**
- l.119: "Minimum post-contingency bus voltages ranged from 0.7179 to..."
- l.292: "...with 26.7% of ridge misses and 21.4%..."
- Fig. 3 (l.303).
- The S_mean values (l.189).

**Evidence.** VERIFIED: re-solved 500 stratified rows (`a5.py` → `relabel.csv`, `a6.py` → `relabel2.csv`), running pandapower and back-off PV/PQ on each row.

- **Labels reproduce.** pandapower matches the recorded min_vm on 499 of 500 rows (|Δ| < 1e-5).
- **The wrong-side-pin state is almost universal.** 291 of 300 rows in the random strata have at least one generator pinned on the wrong side of its setpoint. So do all 40 of the 40 deepest rows.
- **Random violations (n=150):** 13 (8.7%) become non-violations under back-off. No non-violation row (n=150, boundary plus safe) became a violation.
- **Shallow violations near the gate:**
  - In [0.935, 0.94), 20 of 100 flip to safe.
  - In the first sample, 11 of 43 violations within 0.005 pu of the limit flip to safe.
  - These are the misses Fig. 3 counts "within one band width".
- **Deep tail:**
  - The 40 deepest rows all stay violations, but 38 of 40 rise by more than 0.01 pu (median +0.122 pu).
  - The dataset minimum, 0.7179 (scenario 100000022, trafo index 0 = IEEE 8–5), becomes 0.9294.
  - Rows in 0.92–0.935: 1 of 60 flips; none moves by more than 0.01 pu.

**Consequences.** The printed range (0.7179–0.9603), the violation rate (17.48%), the miss-depth histogram and its "deep miss" shares, and S_mean all rest on the artifact. The conformal coverage algebra is oracle-agnostic, so the coverage results survive as statements about pandapower's output. They do not survive as statements about physical under-voltage.

**Caveat.** PV/PQ equilibria need not be unique, and `pvpq.py` is one reasonable back-off implementation. Still, the pandapower states it replaces violate complementarity, so they are not valid AVR steady states either way.

**Suggested fix (content).**
- Validate a sample of labels against an independent AC solver with standard var-limit back-off (for example MATPOWER or a PSS/E-style solver). Report the label-disagreement rate by depth band.
- Either relabel or state the caveat where the range, the tail and Fig. 3 appear.
- Present the deep-tail numbers as oracle-dependent.

---

### POWER-03 — MAJOR — The "boundary mass" behind the title is mostly made by the operating-point sampler, not by case118

**Anchors.**
- Title.
- l.121: "This implies that clustering is an inherent characteristic..."
- l.365: "This escalation floor is set by how the..."
- l.388: "The main reason is that most of the..."

**Evidence.**
- **(a) The setpoint floor equals the voltage limit.** VERIFIED: in `feasibility/generate_dataset.py`, `GEN_VM_LO = 0.94` equals `VMIN_LIMIT = 0.94`. `draw_gen_vm` redraws each setpoint uniformly in ±`dvm` (0.025) until it is at least 0.94. Published case118 schedules 7 of 53 units below 0.96 pu (IEEE 76 at 0.943; `a1.py`). Accepted IEEE-76 setpoints have quantiles 0.940 / 0.954 / 0.968 (0 / 50 / 100%). The clip fix (l.121) replaced a point mass at 0.94 with a uniform density that starts at 0.94. The floor stayed where it was, which explains why the strip "stayed about the same".
- **(b) The strip is mostly the pre-outage state, not the contingency response.** VERIFIED (`a1.py`):
  - 67.7% of N-0 bases already have min_vm in [0.94, 0.945).
  - In 67.3% of N-1 rows, the post-contingency min is within 1e-4 pu of the N-0 min; inside the strip the share is 82.0%.
  - 31.6% of strip rows have their minimum at an in-service generator bus holding its own sampled setpoint. That is a regulated voltage the model receives as an input, not a contingency outcome.
- **(c) The N-0 gate doubles the strip.** Reported (`data/unconditioned_base.json`, the author's own no-gate build, not in the paper):
  - Without the gate, the median N-0 min is 0.9404 and 47.49% of bases already violate before any outage.
  - The strip is 28.83% without the gate against 56.86% with it; the gate pass rate is 53.82%.
  - With the load window centred on the limit, the gate truncates the distribution at 0.94 and mass piles up just above it.
- **(d) One sampler constant cuts the strip by about 30 points.** VERIFIED but provisional (`a7.py`; 40 bases, one seed, committed knobs, only `GEN_VM_LO` changed):
  - GEN_VM_LO 0.94: strip 67.3%, violations 18.4%, N-0 pass rate 56%.
  - GEN_VM_LO 0.95: strip 37.0%, violations 15.8%, N-0 pass rate 71%.
- **(e) The case30 contrast is confounded by the voltage schedule.** VERIFIED: pandapower `case30` schedules all 5 units and the slack at 1.00 pu, so sampled setpoints lie in [0.975, 1.025]. No PV bus can sit at the limit. The 7.09% vs 56.86% comparison (abstract, l.365) therefore mostly compares voltage schedules, not topology.

**Suggested fix (content).**
- State plainly that the strip comes from three things together: the generator-voltage sampling floor at the limit, case118's legacy low schedules, and an N-0 gate at the same 0.94.
- Report the unconditioned result, and a sensitivity with an operator-like voltage schedule, showing how the escalation floor moves.
- Scope the headline to "base cases that already sit at the limit". The mechanism (escalation = mass in [L, L+q̂)) is still correct and worth keeping; what is overstated is the claim that the mass is a network property.

---

### POWER-04 — MAJOR — The operating points are not ones an operator would run, and key sampling knobs are undisclosed

**Anchor.** l.119: "I determined the load levels by scaling the..." (the Method paragraph).

**Evidence.**
- **Generators at reactive limits before any outage.**
  - Reported: on average 20.95 of 53 units sit at a reactive limit in N-0, range 12–30 (`data/classical_screen_metrics.json → gens_at_qlim_base`).
  - VERIFIED: native case118 has 6 of 53. VERIFIED: the deepest-miss scenario has 20 of 53.
  - The bases are therefore reactive-reserve-depleted before any outage.
- **Voltage profile.** VERIFIED:
  - Only 86 of 1,500 bases clear 0.95 pu.
  - 73.4% of bases have max_vm above 1.05.
  - 69.1% have both min below 0.95 and max above 1.05.
  - Under a ±5% normal band, an operator would see low- and high-voltage alarms at the same time in N-0.
- **No real-power dispatch.** VERIFIED: all 53 `genp_*` columns take a single value across the dataset, so dispatch never varies.
  - All load growth (aggregate 1.014–1.124×) and any unit taken out goes to the one slack at IEEE 69.
  - Estimated extra slack MW before losses: median about 255, maximum about 766. In the deepest-miss scenario the solved slack output was 795 MW, against 514 MW in native case118.
- **Undisclosed knobs.**
  - Setpoint perturbation of ±0.025 pu.
  - Reactive-capability scaling U(0.6, 1.4): `QLIM_LO/QLIM_HI` defaults, not overridden in the committed invocation in `data/dataset.manifest.json → run_settings.invocation`.
  - Slack-only balancing.
  - None of these appears in the Method. The independent setpoint perturbation of electrically adjacent units is what drives the reactive circulation in POWER-01.

**Suggested fix (content).**
- Disclose every sampling knob and the slack-only balancing.
- Report the N-0 reactive-reserve statistics.
- Either justify these as a deliberate stress design (and say they are not typical operating points), or add a variant with distributed slack or participation factors and coordinated voltage schedules.

---

### POWER-05 — MAJOR — Speedup accounting skips the solver on exactly the cases an operator must solve

**Anchors.**
- l.140: "**Flag** (skip the solver)".
- l.349: "An operator that requires a missed rate around..."
- The speedups in the abstract.

**Evidence.**
- **Flagged cases.** In operations, a contingency predicted to violate is the one needing an accurate AC solution: the depth, the buses affected and the corrective action all depend on it. It does not get skipped.
- **Speedup if flagged cases are also solved.** VERIFIED from `data/flag_confusion_long.parquet` (v2 values; escalation matches Table II), using the paper's t_surr and t_solve:

  | Model, target | Flagged share | Speedup, flagged solved | Paper's speedup |
  |---|---|---|---|
  | histgb 0.90 | 17.2% | 2.10±0.12 | 3.29 |
  | histgb 0.97 | 17.2% | 1.24±0.07 | 1.58 |
  | ridge 0.94 | 25.1% | 1.12±0.03 | 1.56 |
  | ridge 0.97 | 25.1% | 1.01±0.00 | — |

  The flagged fraction does not change with the target, because the flag uses the point prediction only.
- **Miss tolerance (unverified domain judgment).** Operational screening is judged on whether it captures essentially all critical contingencies, not on a 1% average miss. There are about 32 violations per base case (17.48% × 186), so at a 0.8% per-row miss rate a sizeable share of N-1 runs would certify at least one violating contingency. I did not compute the per-base figure; the row-level gate outputs are not saved.
- **Scale.** Serial N-1 on case118 is about 186 × 9.14 ms ≈ 1.7 s. The paper mentions the parallel scaling measured in `data/parallel_speedup.json` nowhere.

**Suggested fix (content).**
- Report a second speedup accounting in which flagged cases are also solved.
- Drop or ground the "operator requires about 1%" framing: cite an operational screening criterion, or state it as the author's assumption.
- Say where speedup would matter (large systems, many base cases, planning studies) and that it is not tested there.

---

### POWER-06 — MAJOR — The classical baseline was built but omitted, and the paper mischaracterises classical screening

**Anchors.**
- l.109: "While this indicates which equipment is subject to..." ("fails to provide a numerical minimum voltage").
- l.124: "I tested my models against two baselines: persistence,..."

**Evidence.** Reported: `data/classical_screen_metrics.json` contains a linearised classical screen that outputs numerical post-contingency voltages (MAE 0.00377, R² 0.117) and an Ejebe–Wollenberg PI_V ranking.
- With its own conformal band at 0.90 it escalates 92.0%, misses 1.07% and gives a 1.09× speedup.
- That is a real operational-style baseline, and the surrogates beat it on escalation.
- The paper reports only persistence and the training mean, which are both trivial.
- Classical 1P1Q / voltage-PI screens compute approximate post-outage voltages to form the index, so "fails to provide a numerical minimum voltage" is inaccurate. It also contradicts the repo's own classical screen.

**Suggested fix (content).**
- Add the classical screen (documented as in its JSON, including the PI definition and reference point) to Table I or its own row.
- Correct the l.109 characterisation.

---

### POWER-07 — MINOR — The case57 exclusion reason is physically implausible and points to a model-data problem

**Anchor.** l.353: "In case57, the voltage was too low across..."

**Evidence.** VERIFIED (inline solve):
- pandapower `case57` at nominal load gives min 0.7199 pu, with 39 of 57 buses below 0.94.
- At load ×0.0 it gives 0.9012, with 24 buses below 0.94 (Q limits on). All units are scheduled at 0.98–1.04 pu.
- A network with no load and generators near 1.0 pu cannot sag to 0.90. The model data are suspect: buses are split across 115–500 kV nominals, and transformer `vk_percent` runs up to 13,414.
- The published IEEE 57-bus solution is not a 0.72-pu case (unverified; check against the archive or MATPOWER's solved case).
- The paper attributes the failure to the network ("too low across the whole network ... under realistic conditions"). A power judge will read the zero-load figure as a broken model.

**Suggested fix (content).**
- Say the case was excluded because pandapower's case57 did not reproduce a sensible base solution.
- Do not present 0.90 pu at zero load as a network property.

---

### POWER-08 — MINOR — case30 is labelled "published IEEE 30-bus"; it is a different case

**Anchors.**
- l.119: "I also tested the published IEEE 30-bus system,..."
- The abstract ("IEEE 30-bus system").

**Evidence.** VERIFIED:
- The `pandapower.networks.case30` docstring says the data are PYPOWER, "derived from Washington 30 Bus Dynamic Test Case". All its units are scheduled at 1.00 pu.
- The IEEE 30-bus power-flow case is `case_ieee30` (setpoints 1.01–1.082, slack 1.06).
- The 111.83% base loading (`data/thermal_check.json`) belongs to that variant.

**Suggested fix (content).** Name the case correctly and give its source, since the schedule difference also feeds POWER-03(e).

---

### POWER-09 — MINOR — Islanding outages are handled silently

**Anchors.** l.111 ("186 total pieces of equipment") and l.119.

**Evidence.** VERIFIED (`a2.py`, `pandapower.topology.unsupplied_buses`): 9 of 186 branch outages island buses.
- Lines index 6 and 7 island the 450 MW unit at IEEE 10. That power goes to the slack, and both outages are violations in 100% of bases.
- Five outages shed radial load: 6, 21, 68, 20 and 184 MW at IEEE 73, 86–87, 112, 117 and 116.
- `generate_dataset.solve` takes `np.nanmin` over energized buses, so these rows are labelled by the rest of the network and mostly come out "safe" (0.1–4.5% violations). Load lost this way never counts as a failure.

**Suggested fix (content).**
- State how islanded buses are treated.
- Consider reporting load-shedding outages separately, since an operator would not call them "safe".

---

### POWER-10 — MINOR — Non-convergence is the severe tail of one real critical outage, but the paper does not say so

**Anchor.** l.119: "Out of those 279,000, 45 were removed due..."

**Evidence.**
- Reported (`data/nonconverged_gate.json`): 37 of the 45 non-converged cases are trafo index 0 (IEEE 8–5); the other 8 are trafo index 7 (7 cases) and index 6 (1).
- VERIFIED: the same transformer produces 10 of the 12 deepest violations in my relabel sample and 15.1% of rows below 0.85 pu.
- Non-convergence here most plausibly marks the most severe states of a critical contingency (possible voltage collapse), not solver noise.
- The repo shows the gate would flag 38–39 of the 45, and that the missed rate barely changes if they are counted as violations. The paper uses neither fact.

**Suggested fix (content).** Say what non-convergence means physically, and report how the gate would treat these cases (numbers already in the JSON).

---

### POWER-11 — MINOR — The "N-1" framing contradicts itself when a generator is already out

**Anchors.**
- l.107: "The N-0 condition represents the current state..." ("without any equipment outages").
- l.111: "Some base cases are also missing a generator..." ("two elements out").
- l.367: "These are still N-1 contingencies, since each..."

**Evidence.**
- Reported: 374 of 1,500 bases (69,532 rows) have a unit out (`data/sampling_audit.json`).
- A generator out followed by a branch out, with no redispatch (the slack picks it up), is closer to a G-1 + L-1 sequence than to a clean N-1.
- The paper calls it three different things in three places.

**Suggested fix (content).** Choose one definition (for example, "unit on maintenance is part of the base case"), use it consistently, and note that there is no redispatch between the two outages.

---

### POWER-12 — MINOR — Loose physics and limit semantics in the Background

**Anchors.**
- l.107: "However, if a single piece of equipment fails,..." ("the rest of the network must absorb the extra load").
- l.365: "I use 0.94 pu as a conservative choice."

**Evidence.**
- A branch outage adds no load. It redistributes flow, raises series reactive losses (I²X), and removes a voltage-support path. That is why voltage drops.
- One 0.94 value serves as both the N-0 acceptance limit and the post-contingency limit.
- Practice normally distinguishes normal (pre-contingency) and emergency (post-contingency) ranges, and TPL-001 leaves the values to the planner (domain knowledge, unverified here).
- 0.94 is conservative as a post-contingency limit but lax as an N-0 acceptance limit: 94% of bases fail 0.95 (VERIFIED, 86 of 1,500 clear it).

**Suggested fix (content).** Correct the mechanism sentence and state which limit type 0.94 represents at each stage.

---

### POWER-13 — MINOR — Costs left out of the speedup, and planning vs operations context

**Anchors.**
- Eq. 2 at l.145, and l.147: "Here $n$ is the total number of..."
- l.97: "The N-1 criterion, for all the elements that..." (cites NERC TPL-001).

**Evidence.**
- Feature cost: the features include the N-0 AC voltages (`vm0_*`, `generate_dataset.scenario_features`), which take one base solve per scenario. That solve is not charged in Eq. 2. Amortised over 186 contingencies it is about 0.5%, which is negligible, but it should be stated. In real time the base state would come from state estimation.
- Solver cost: t_solve is a from-scratch pandapower solve (DC init, Ybus build, Q-limit outer loop, Python overhead). Production contingency analysis warm-starts and reuses factorisations. Because speedup ≈ 1/escalation, this barely changes the ratio; it matters only for the absolute cost claim.
- Context: TPL-001 is a planning standard. The motivation ("operators running every combination and repeatedly testing") describes real-time operations. The sampled-base-case design actually looks like a planning or operations-planning study.

**Suggested fix (content).**
- State that the base solve is excluded, and why.
- Match the motivation and the citation to the context the experiment actually represents.

---

### POWER-14 — MINOR — The case30 speedup inputs borrow case118's solve time

**Anchor.** No printed case30 speedup in the paper (only escalation and missed rate at l.365), so there is no paper-level error today.

**Evidence.**
- Reported: `data/case30_thermal/case30_thermal_frozen.json → ms_solver` is 9.14 (the case118 value).
- `data/case57_feasibility.json → step4_network_transfer_scan` records a case30 minimum solve time of 4.848 ms.

**Suggested fix (content).** If any case30 speedup reaches the poster or report, use case30's own solve time.

---

## 3. Three strongest parts to protect

1. **The clip-artifact catch and disclosure** (l.121: "The previous implementation of the dataset generator used..."). Finding a solver/sampler artifact by inverting the escalation–band-width relation, fixing it, and reporting before-and-after numbers (`data/clip_artifact.json`, VERIFIED 35.17 / 55.51 / 56.86) is exactly the instinct judges want. Keep it. Only its interpretive last sentence needs revisiting (POWER-03).
2. **Honest constraint scoping** (l.107: "I cannot check for thermal loading because case118...", plus the over-voltage disclosure and the case30 thermal regeneration with residual overloads disclosed at l.367).
   - The 9,900 MVA placeholder ratings are real: VERIFIED in `data/thermal_check.json`, where every line and transformer implies 9,900 MVA.
   - The 73.1% over-1.05 share is VERIFIED: `thermal_check.json → n1.share_above_1p05` = 0.7314.
   - Most published ML-screening papers hide these limits.
3. **The gate algebra and ceiling analysis** (l.167–181 Theory, l.347 "A case is escalated when the prediction lies...", and the persistence argument at l.349).
   - The identities are exact: escalation = mass of predictions in [L, L+q̂); certification of a violation requires o ≥ q̂ + (L − y).
   - The saturation/ceiling reasoning is right, and so is the physical point that persistence can never flag, because every accepted base is at or above 0.94.
   - This algebra is correct whatever the oracle, so it survives POWER-01/02.

---

## 4. Open questions I could not settle

- **Uniqueness of the back-off solutions.** PV/PQ switching with back-off can have more than one equilibrium. An independent solver (MATPOWER or PowerModels with var-limit back-off, or a commercial tool) on the 500 rows in `relabel*.csv` would settle whether 8.7% (random violations) and 20% (shallow violations) are the right disagreement rates.
- **Effect on the headline metrics.** A full relabel of 279k rows would take about 3 solves each, roughly 2–3 h on 10 cores. I did not run it, so I cannot say how escalation, missed rate or S_mean move.
- **Stability of POWER-03(d).** The 40-base setpoint-floor experiment is one seed; the size of the strip reduction needs a full-size rebuild to be quoted.
- **case57.** Whether pandapower's case57 differs from the published IEEE 57-bus solution (unverified), or whether some transformer/tap conversion is at fault.
- **Per-base-case miss probability.** The chance that an N-1 run certifies at least one violation at the 0.97 operating point cannot be computed: the row-level gate outputs are not saved.
