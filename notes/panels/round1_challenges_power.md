# Round-1 challenges — Power-systems panelist

Read: `round1_{stats,nonspecialist,sts_judge,repro}.md`.
New script: `/Users/rajansaha/.claude/jobs/484f4ac7/tmp/panel_power/c1.py`, output in `c1.log` and `c1.csv`. It runs repro's `t7.solve_pvpq` and my `pvpq.solve_pvpq` on repro's exact t8 sample (`default_rng(1)`, 300 rows).

## A. Tension (b): my label-flip rate vs repro's. The methods agree; the gap is sampling

- **Method differences.**
  - Repro (t7) uses 1e-6 tolerances for both Q and V and pre-creates one sgen per generator.
  - Mine (`pvpq.py`) uses Q 1e-3 and V 1e-4 and recreates the sgens on each iteration.
  - Both use the same rule: pin every violator at its limit, release a pinned unit when V is on the wrong side of Vset, and iterate until nothing changes.
- **Same 300 rows (VERIFIED, `c1.log`).**
  - The two implementations give identical min_vm on all 300 rows: 0 differences above 1e-4 and 0 label disagreements.
  - Both find 7 violations becoming safe and 4 safe rows becoming violations.
  - Deepest case: my 0.94507 and repro's 0.9451 are the same value. Two independently written loops now agree; an independent AC solver is still open.
- **Why 8.7% vs 14%.** It is sampling, not method. My 13/150 came from a stratified sample of violations; repro's 7/50 came from 300 random rows.
  - Pooled viol→safe: 20/200 = 10% (95% CI roughly 6–15%).
  - Pooled safe→viol: 4/400 = 1.0%. That is 0/150 in my boundary and safe strata plus 4/250 in repro's sample.
- **Correction to my POWER-02.** I wrote "no safe→violation flips". That held for my sample only.
  - Flips go both ways. One row recorded as safe (0.9417) is actually a deep violation (0.9132) under consistent PV/PQ (`c1.csv`, row 242).
  - So the one-way switching can hide violations as well as invent them. The net violation rate falls by about 1 point (repro: 16.7 → 15.7%).
  - The finding stays MAJOR. Its direction is now "noise in both directions, concentrated near L", not "misses overstated".

## B. Challenges (substance or severity)

1. **REPRO-01 (MAJOR, "could become FATAL") vs my POWER-01 (FATAL).**
   - For the specific deepest-miss claim I keep FATAL.
   - Two separately written implementations reproduce the same consistent solution.
   - The project's own artifact already shows the unit at Q_min (`data/qlims_off_check.json → gen21_reactive_state`).
   - The printed physical mechanism ("reaches the limit of reactive power and can no longer control the voltage") is contradicted three times (l.292, l.303, l.367).
   - I agree the label-noise finding in general (POWER-02 / REPRO-01) stays MAJOR until checked with an independent solver.

2. **REPRO strength #2 and NS strength #3 ("boundary-mass explanation", "Fig. 4 + 118-vs-30 contrast").**
   - The arithmetic is robust, and I agree: the strip share barely moves under relabeling (repro 58.7 → 57.0%).
   - The interpretation should not be protected as written. The strip is made by the sampler:
     - `GEN_VM_LO` (0.94) equals the limit.
     - Raising only that constant to 0.95 cut the strip from 67.3% to 37.0% (`a7.py`; provisional, 40 bases).
     - The N-0 gate halves it (`data/unconditioned_base.json`).
   - The case30 contrast is a voltage-schedule contrast. pandapower case30 schedules every unit at 1.00 pu, while case118 schedules 7 of 53 below 0.96 (VERIFIED, `a1.py` and an inline check).
   - Protect Fig. 4 and the numbers. Do not protect "network property" or the 118-vs-30 contrast as causal evidence.

3. **STS-04 (the judge's "single change": a within-network dose-response from the limit sweep and N-0 strata).**
   - I agree the paper should use within-network evidence. But those two artifacts do not test the physical cause.
   - **(i) The limit sweep is near-definitional.** Escalation is by definition P(L ≤ p̂ < L+q̂). For an accurate predictor it must track true-voltage mass near L as L moves, so r = 0.98–0.995 is expected by construction (STATS-07 and STATS-08 make the same point).
   - **(ii) The N-0 stratum split conditions on the base voltage.** It confirms inheritance (STS-03, which I support: my `a1.py` gives 82% of strip rows with the N-1 min within 1e-4 of the N-0 min, and 31.6% of strip rows are a PV bus holding its own sampled setpoint). It does not manipulate anything.
   - **(iii) Only sampler manipulations test the cause:** gate on/off, setpoint floor, voltage schedule.
   - **(iv) All three artifacts share the one-way Q-limit oracle.**
   - Suggested dose-response variable: the sampler (for example `GEN_VM_LO` or the schedule), not L. It needs a 5-seed, full-size rebuild before anything is printed.

4. **STS-05, suggested fix (use S_mean to explain the case30 reversal).**
   - On case118, S_mean averages overshoot over violations. That makes it sensitive to the violation tail, which is oracle-dependent.
   - Under consistent PV/PQ, the 40 deepest violations rise by a median 0.122 pu (`relabel2.csv`), and violations flip at 1.7% in [0.92, 0.935) and 20–26% within 0.005 pu of L.
   - S_mean should not be promoted as an explanatory statistic until the case118 labels are validated. Case30 has not been checked for the same artifact.

5. **STS-15 (MINOR, operating-point realism) should be MAJOR.**
   - It is more than the 73% over-voltage share. On average 20.95 of 53 units sit at a Q limit in N-0, against 6 of 53 in native case118 (`classical_screen_metrics.json → gens_at_qlim_base`; VERIFIED native).
   - 69.1% of bases are simultaneously below 0.95 and above 1.05 (VERIFIED).
   - Real-power dispatch is fixed and the slack absorbs everything (all `genp_*` columns constant, VERIFIED).
   - Independent setpoint jitter on adjacent units drives the reactive circulation behind POWER-01.
   - This goes to what the result means, not polish (POWER-04).

6. **STS strength #3 and NS honourable mention ("case57 dropped for physical reasons").**
   - The number is reproducible (REPRO row 82; my inline solve: 0.9012, 24 buses at load ×0.0).
   - But 0.90 pu at zero load, with every unit scheduled at 0.98–1.04 pu, is not a physical property. It signals broken model data: bus nominals range from 115 to 500 kV and trafo `vk_percent` goes up to 13,414.
   - Do not protect this as an example of good judgment. As printed it would cost credibility with a power-systems judge (POWER-07; NS-10(f) makes the same "realistic conditions" point).

## C. Accepted findings that change my review

- **STATS-04.**
  - 11.1 ± 2.6% of test base cases hold at least one certified violation at histgb 0.97. This answers my open question and strengthens POWER-05.
  - Caveat: under A, some of these misses may be label artifacts and some hidden misses may be missing from the count.
- **STATS-05.**
  - A static element-frequency ranking matches the ridge gate's capture at the same budget (`baselines.json`).
  - This is the operator-style baseline I asked for in POWER-06, and it strengthens that finding.
- **STATS-06 / NS-04.**
  - Ridge flag precision is 56%, and train-mean flags every case.
  - This complements POWER-05 (flagged cases are unsolved and uncosted).
- **STATS-01 and STATS-02 / REPRO-03 / NS-05 / STS-05.**
  - The operating point is chosen on test data.
  - The model comparison is made at matched targets instead of matched cost.
  - I accept both. Neither conflicts with my findings.
- **STS-11.**
  - The 1% target is unjustified, and miss depth is shown only at 0.90.
  - This matches POWER-05. Miss depth at any point also inherits POWER-02.
- **Tension (a): Theory as a strength.**
  - I concede. Eqs. 3–4 are identities (STATS-08, STS-10, NS-15), and I accept those findings as MINOR.
  - My strength #3 narrows to the ceiling and saturation reasoning and the physical persistence argument (l.347–349), which are correct and useful. It no longer covers a section labelled "Theory".
- **Tension (c): AI and paid-program disclosure.**
  - This is outside my discipline. On the rule text quoted (R22/R04, R20), I accept STS-01 as FATAL as a compliance exposure. It is fixable in hours and says nothing about the science.
  - STS-02 as MAJOR is reasonable.

## D. Revised scores

- Originality: 5 (unchanged).
- Rigor: 4 (unchanged).
- Significance: 3 (unchanged). STATS-04 and STATS-05 reinforce it.
- Clarity: 6 → 5 (NS-02 "coverage" has three meanings; NS-13 jargon; the Theory concession).
- Student potential: 8 (unchanged).
- Counts: FATAL 1, MAJOR 5, MINOR 8 are unchanged. POWER-02 now reads "flips in both directions".
