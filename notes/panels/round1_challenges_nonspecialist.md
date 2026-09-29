# Round-1 challenges — Non-specialist juror (reads the four specialist reviews)

Seat: an intelligent scientist outside the field, judging at the table. My test for every proposed
fix is whether a lay judge will understand the paper better or worse after it.

## A. Factual conflict that must be settled first: Fig. 5 labels (NS-09, STS-12 vs REPRO)
- REPRO (Checked) says the labels in `critical_bus_map.png` read 76/53/107/1/21, matching the text.
  NS-09 and STS-12 say they read 75/52/106/0/20. **Both are right about what they looked at.**
  VERIFIED: the repo PNG (`data/critical_bus_map.png`, mtime Sep 4) shows 1-based labels. The compiled
  Overleaf PDF (`paper_v39.pdf` p.11) shows 0-based labels. **Overleaf is holding a stale copy of the image.**
- Consequence: NS-09 and STS-12 drop to MINOR as figure errors. The real issue is process: the repo
  and the Overleaf figure assets are out of sync. Every figure in the export should be re-checked
  against the repo PNG before submission. REPRO's byte-reproducibility check covers the repo, not
  Overleaf.

## B. Fixes I challenge: they would make the paper harder for a lay judge

- **STATS-03 (joint bound α/P(y<L) ≈ 57% / 17%; exchangeability at the base-case level).** I agree with
  the substance. I oppose putting the bound in the main text. A lay judge who reads "guaranteed below
  57%" next to a measured 4.72% will conclude the guarantee is useless and stop reading. The judge
  needs one plain split in Method: which number is promised (average coverage), which numbers are only
  measured (missed rate, escalation, speed-up), and the one condition the promise needs. The numeric
  bound belongs in an appendix or the interview.
- **STATS-05 (add a violation-conditional / RCPS-CRC calibration as the principled alternative).** That
  brings in a second band construction and a third meaning of "guarantee" in a paper whose single
  band a lay reader can barely follow now (NS-02). I oppose it as main-text content before the
  existing terms are fixed. I ACCEPT STATS-05 part 1: the static "historically worst lines" ranking,
  which ties ridge at matched budget (Reported, `baselines.json`). That is the most lay-friendly
  baseline in the whole repo. Any judge understands "just check the lines that usually fail", and
  it answers "is ML even needed?"
- **POWER-02, POWER-04, REPRO-05 (label-disagreement tables by depth band, N-0 reactive-reserve
  statistics, every sampling knob, versions, search spaces, per-seed configurations).** Each is fair
  on its own. Together they would add a page of parameters to a Method section that already loses
  outsiders at "Independent/Regional mode" (NS-13). Put the reproducibility material in one compact
  table (and the repo). In prose, give only the knobs that CHANGE THE STORY: the setpoint floor at
  0.94, the N-0 gate at 0.94, and slack-only balancing. The STS page limit (STS-judge: body folios
  1–16 now) should decide whether an appendix fits. I did not check the limit.
- **STS-04 (replace the case118-vs-case30 contrast with a within-network dose-response figure).** I
  ACCEPT the direction, with one condition: ONE manipulation, ONE figure. The N-0 stratum split (same
  grid, same model; benign bases about 2.8% escalation vs marginal bases about 59.1%) is the most
  intuitive evidence anyone has proposed, because a lay judge sees a controlled comparison. Adding
  the limit sweep, the quintiles and the netstudy overlay all together would recreate the §IV.4
  problem. Keep case30 as a second example, not as proof.
- **POWER-05 (second speed-up accounting with flagged cases solved).** I accept it: it is my NS-04
  from the operator side. But two speed-up columns with no rule for which one is the headline will
  confuse. The paper should pick one accounting as the headline and say in a sentence why.
- **POWER rubric, Significance 3.** I challenge the reasoning, not the domain facts. Scoring
  significance by "not operationally attractive" penalises an honest negative result, and STS says it
  rewards those when the mechanism is explained. My own significance drops (see D), but for reasons of
  evidence strength, not because the speed-up is small.

## C. Severity challenges

- **STATS-12 (coverage has two meanings): MINOR → MAJOR for this jury.** The abstract's headline
  ("90% coverage … misses 4.72%") cannot be decoded without the distinction (NS-02). For specialists it
  is a wording slip. For a multidisciplinary panel it blocks the central result.
- **STS-07 (Fig. 2 error bars): MINOR → MAJOR.** REPRO-02 and my NS-08 rate it MAJOR. The one
  uncertainty statement the abstract leans on ("error bars slightly above 1%") points to a figure that
  does not show it. A judge who checks will doubt the other captions.
- **POWER-01 FATAL: I agree, for a different reason.** A lay judge cannot detect the solver artifact.
  But the claim is printed three times, including an arrow in Fig. 3, and an interviewing engineer
  can break it with one question. The fix (remove or re-ground the story) is cheap and the downside is
  unbounded. Keep FATAL until the paper changes.
- **NS-15 (my "Theory" finding) MAJOR → MINOR.** I accept STATS-08 and STS-10 (both MINOR), and
  especially STS-05's use of S_mean to explain the case30 ordering reversal. That gives the section a
  payoff a lay judge can follow ("this number predicts which model misses more on which grid").
- **STS-01 / STS-02 vs my NS-01:** I accept the split (AI = FATAL, people/fees = MAJOR). It is
  cleaner than my conditional FATAL.

## D. Findings I now accept that change my own scores
- **POWER-01, POWER-02, REPRO-01** (labels depend on one-way generator-limit switching; the deepest
  miss is not a violation under a consistent re-solve, pending independent confirmation): Rigor 7 → 6.
- **STATS-01** (the 0.94/0.97 operating points were chosen on test; held-out selection gives histgb
  1.15±0.27%, with 4/5 seeds above 1%) and **STATS-04** (about 1 in 9 test base cases contains a silent
  miss at histgb 0.97; panel recomputation, not yet committed code): Significance 5 → 4. STATS-04's
  per-study number is also the most lay-readable safety statistic proposed, so it strengthens NS-03.
- **POWER-03 / STS-03** (the strip is mostly inherited base-case voltage plus the sampler floor): this
  confirms NS-06 and moves Originality 6 → 5. STS-03's plain mechanism ("most outages don't move the
  weakest bus, so the post-outage voltage inherits the starting voltage") is the best lay explanation
  in any review. Protect it.
- **Revised:** Originality 5, Rigor 6, Significance 4, Clarity 4, Student potential 8.
  NS-09 → MINOR (stale Overleaf asset), NS-15 → MINOR. New counts: FATAL 1, MAJOR 13, MINOR 12.

## E. POWER-01: what a lay judge needs to see about the worst miss
1. **No featured claim that fails.** The "sudden collapse … reaches the limit of reactive power"
   sentence (l.367) and the Fig. 3 arrow labelled "deepest miss 0.0915 pu" must not survive in their
   current form. A lay judge takes an annotated extreme as the paper's most vivid evidence.
2. **One plain sentence on what went wrong.** The simulator can leave a generator stuck at a limit in
   a state real equipment cannot be in. A re-check found this case is not a violation. No
   "PV/PQ complementarity" in the main text.
3. **A number, and only a confirmed one.** State how many labels change and whether the headline
   missed rates move. Do this only after an independent solver or second implementation confirms it
   (POWER and REPRO both used their own loops; 8.7–14% flips among violations is still provisional).
   An unconfirmed rate in print is worse than none.
4. **Frame it like the clip bug (l.121).** It is a second self-found artifact, and presented that way
   it adds to the paper's best feature, individual scientific judgment. Hidden or minimised, it
   becomes the interview question that ends the conversation.
5. **Say what survives.** The gate algebra and the boundary-mass share are oracle-agnostic or robust in
   the re-solve samples (POWER strengths §3; REPRO-01: strip 58.7% → 57.0%). A lay judge needs to be
   told that the core finding stands even though the showcase example does not.
