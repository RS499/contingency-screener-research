# Round-1 challenges — STS Top-40 judge

I read `round1_{power,stats,nonspecialist,repro}.md`. New recomputation is labeled VERIFIED (source file named). Blind rule respected.

## A. Where I disagree (substance or severity)

**1. REPRO (checked list, Fig. 5 "labels ... match the text") is wrong about the submitted PDF.**
- The committed `data/critical_bus_map.png` does carry IEEE names (bus 76/53/107/1/21). REPRO checked that file.
- The compiled PDF the judges will see embeds a different, older image: `paper_v39.pdf` p.11 reads "bus 75 (27%)", "bus 52", "bus 106", "bus 0", "bus 20" (VERIFIED visually), and its title and colourbar differ.
- So NS-09 and my STS-12 describe what a judge sees. REPRO describes the repo.
- The actual defect is that the Overleaf project is out of sync with the repo. Fix: re-upload every figure and check each embedded image against its manifest `output_sha256`. Severity: MINOR as a label issue, but it proves that figures in the PDF can be stale. Fig. 2 (no error bars) needs the same check.

**2. REPRO-01 should be FATAL, not "could become FATAL". I agree with POWER-01's severity.**
- The confirmation REPRO asked for now exists: two panelists wrote independent back-off loops (POWER `pvpq.py`, REPRO `t7.py`), and both land on min_vm 0.94507 for the featured case.
- The repo's own `data/miss_mechanism.json` records gen 21 `at_min: true`, which is the absorbing limit. The paper prints that the generator "reaches the limit of reactive power and can no longer control the voltage" (:367). It does this three times, including a caption.
- The artifact contradicts the prose. That is an integrity problem, not just a physics nuance.
- Caveat I keep: PV/PQ equilibria need not be unique. The fix is to drop or rebuild the narrative, not to claim that the true value is 0.945.

**3. POWER-02: severity MAJOR is right, but its consequence is overstated.**
- POWER says the coverage results "do not survive as statements about physical under-voltage". REPRO's random sample (n=300) moves the violation rate only from 16.7 to 15.7% and the strip from 58.7 to 57.0%.
- The flips go both ways: POWER saw 0/150 safe→violation, REPRO saw 4/250.
- So the headline trade-off very likely survives. The deep tail, Fig. 3, S_mean and the 0.7179 minimum do not.
- I would not ask for a full 279k relabel before 5 Nov. It would change every printed number late in the cycle, and it is heavy compute that needs the owner's approval. Minimum fix: a seeded relabel sample drawn across all 5 splits, the disagreement rate reported by depth band beside the headline, and the one-way Q-limit convention named as the oracle. A full relabel is the owner's call.

**4. My own STS-05 was incomplete. I accept STATS-02 and REPRO-03.**
- I checked only the ~64% escalation match (a tie).
- Their interpolation shows histgb is *safer* below ~55% escalation, tied near the recommended point, and ridge safer at ~72%.
- The IV.2 heading is wrong on the axis an operator pays for. The reversal on case30 (my STS-05) still stands.

**5. NS severity inflation.**
- NS lists 15 MAJORs. NS-13 (jargon), NS-17/18-style cues and NS-22 (Table 2 skips rows) are MINOR for a Top-40 doctoral panel.
- They matter more at the Top-300 stage, where readers come from mixed disciplines, so keep NS-13 MAJOR there only.
- NS-06 (a grid property or a filter property) is the finding most likely to decide a Top-40 read, and it agrees with POWER-03 and my STS-03.

**6. A compliance item I missed and REPRO/NS only raised in passing: the URTC paper.**
- The .tex header (:3) says the body is "VERBATIM from the URTC conference version".
- `sts-constraints.yaml` R18 (GUIDE2027 rule 6) asks that published work be acknowledged in the application, and that group-published work be submitted as the student's own version.
- R03 notes that whether the URTC co-authors are students or adults is "NOT RECORDED IN THIS REPOSITORY".
- The report does not mention URTC. Severity: MAJOR. It becomes FATAL if the URTC paper has student co-authors (R03 bars splitting a team project). The owner must settle it.

## B. What the others add, combined (new synthesis, panel recomputation, provisional)

STATS-05 and POWER-05 together are worse than either alone.
- `data/baselines.json` counts flagged cases as captured for free: the gate's `k_equivalent` is escalations only.
- If flagged cases are also solved (POWER-05, flag shares 17.2% histgb / 25.1% ridge), the gate budget at 0.90 becomes ≈89 solves per base for histgb and ≈138 for ridge.
- A static ranking by training violation frequency (`comparators.static_severity.curve_mean`, VERIFIED) at those budgets captures:

| Model | Solves per base (k) | Static ranking | Gate |
|---|---|---|---|
| histgb | 89 | 96.64% | 95.28±0.98% |
| ridge | 138 | 99.41% | 97.04±0.44% |

- At histgb 0.97 (k≈150), the static ranking captures 99.71% against the gate's 99.17%.
- I did not compute the std at those k, so the std rule is not yet applied. Treat this as provisional.

Reading: under operator accounting, a list that ignores the operating point matches or beats the ML gate on case118. This is consistent with POWER-04: dispatch is fixed and the same elements violate in every base case. The student should report it as a finding. It is also the strongest evidence that the operating-point distribution is too narrow for the network-level claims.

## C. Effect on my scores and verdict

| Criterion | Round 1 | Revised | Reason |
|---|---|---|---|
| Originality | 5 | 4 | POWER-03(a): the setpoint floor equals the limit (`GEN_VM_LO = 0.94`), so most of "boundary mass" is a sampler setting, not a discovery about the network. |
| Rigor | 6 | 5 | Label validity (POWER-01/02), operating point picked on test (STATS-01), flags uncounted (STATS-06). |
| Significance | 4 | 3 | Section B, plus STATS-04: 11.1±2.6% of test base cases contain a silent miss at histgb 0.97. |
| Clarity | 4 | 4 | Unchanged. |
| Student potential | 7 | 7 | The repo shows the student already built most of the controls the panel is asking for. That speaks well of them; the paper doesn't show it. |

**Revised verdict**
- **Top 300: below a coin flip as submitted.** There are three blockers:
  - the AI and support disclosure;
  - the deepest-miss narrative that the repo contradicts;
  - the unacknowledged URTC paper.
- **With those fixed: about a coin flip.** It is honest, solo, with error bars and an explained negative result.
- **Top 40: very unlikely as submitted; a long shot after revision.** The route to Top 40 is not a better gate. It is a sharper negative result that the student owns: what actually sets the gate's value, shown by manipulation.

**Revised single most important change.** Make boundary mass the manipulated variable in a controlled experiment, and report everything that moves.
- Rebuild case118 at 5 seeds, varying two data-side factors:
  - the setpoint floor (POWER-03(d): 0.94 vs 0.95; one run already exists);
  - the N-0 gate, on or off (`unconditioned_base.json` exists).
- Add the existing limit sweep and N-0 strata as the threshold-side factors.
- For each cell, report escalation, missed rate, the share of base cases with any miss (STATS-04), and the margin over the static ranking with flags solved (Section B).
- Scope the title and conclusion to what this shows.
- The rebuilds are heavy compute and need the owner's approval.
- This one change answers POWER-03, NS-06, STATS-07 and my STS-03/04 together.

## D. AI disclosure: in the report, or can the application form carry it?

**It must be in the report. I keep it FATAL until STS confirms otherwise.**
- `sts-constraints.yaml` R04 and R22 quote RULES2027 App. 4 (p.34): AI-written code is acceptable "only with explicit citation stating which portions of the code were AI generated". AI language help "Must be credited". A citation of portions belongs with the work it cites, and the Research Report is the document the Top-300 and Top-40 panels actually read.
- R20 (GUIDE2027, closing paragraphs): "full disclosure of any research or person that has influenced the applicant's work is required". The wording is general and names no location.
- **Weakness of my position:** the YAML's own `meta.warning` says RULES2027 is only 18% read (pp. 3–6, 33–35). R19 names p.8 (APPLICATION REQUIREMENTS) as unread. So whether an application field satisfies App. 4 is unverified.
- **I partly concede NS-01's conditional.** If STS confirms that a form field suffices, the report-level omission drops to MAJOR.
- **Why it stays a blocker anyway:** the in-report fix costs three or four lines and carries no rules risk. Its absence is a regression from an earlier draft (R04 note). Under-crediting AI in the judged document is exactly what App. 4 penalises. It should be treated as a blocker regardless.
