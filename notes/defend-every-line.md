# Lines you must be able to defend

The screener code (make_splits.py, surrogate.py, gate_eval.py, run_all.py, test_pipeline.py) is
written at the course's Python level on purpose: every line is plain enough to type and read
back. But a handful of those plain lines encode a decision that is not obvious and is not in the
syllabus (conformal prediction and evaluation hygiene are self-taught). Those are the lines a
judge or reviewer will push on. This sheet lists each one, what it does, why it is there, and the
follow-up question you should expect with a crisp answer.

Rule of thumb: the code is simple so you own it; the sophistication lives in these decisions.
Being able to explain these is the difference between "a high schooler could type this" and "this
high schooler can defend every line."

---

## 1. Split by scenario, never by row

Where: `make_splits.py`, `make_splits()` (two-stage `GroupShuffleSplit` on `scenario_id`).

```python
gss1 = GroupShuffleSplit(n_splits=1, train_size=train_frac, random_state=seed)
train_idx, rest_idx = next(gss1.split(placeholder, groups=groups))
```

What it does: puts all 187 rows of any one scenario entirely in train, or entirely in
calibration, or entirely in test - never split across them.

Why it is there: every row of one scenario shares the same pre-contingency grid state (the same
loads, the same generator setpoints). If two rows from the same scenario landed in both train and
test, the model would have effectively seen the test state during training. Coverage and accuracy
would look great and be a lie.

Expected question: "Why not a normal random 80/20 split?"
Answer: because rows are not independent. They are grouped by scenario. A row-level split leaks
the shared pre-contingency state and voids the conformal coverage guarantee, which assumes the
calibration and test cases are exchangeable. Guard T1 and T5 in test_pipeline.py fail loudly if
any scenario or row appears in more than one split.

---

## 2. The band is one-sided (no absolute value)

Where: `gate_eval.py`, `calibrate_qhat()`.

```python
over = pred_cal - y_cal          # NOT abs(pred_cal - y_cal)
q_hat = over_sorted[k - 1]
```

What it does: measures only how far the prediction sits ABOVE the true voltage, and builds a band
that extends only downward: `lower = pred - q_hat`, with no upper limit.

Why it is there: the only dangerous mistake a screener can make is calling a case safe when the
true voltage is actually below the 0.94 floor. That is a downward error. Over-voltage does not
happen on this network (generators pin the ceiling), so guarding the upper side would waste band
width and needlessly escalate cases to the slow solver.

Expected question: "Why one-sided instead of a normal symmetric interval?"
Answer: the risk is asymmetric. We only care about the true value falling below the prediction.
Using `pred - y` instead of `|pred - y|` gives a tighter band in the direction that matters, so
fewer cases straddle the limit and fewer escalate, with coverage still holding at the 90% target.
An earlier two-sided version escalated more, which is what you would expect from a band twice as
wide, but that comparison was measured on the clip-era build and I have not re-run it on the current
data, so I quote the direction of the effect, not a multiplier. Guard T4 checks the band is
one-sided (a prediction far above the limit must still certify).

---

## 3. The finite-sample rank correction (why n+1, not n)

Where: `gate_eval.py`, `calibrate_qhat()`.

```python
k = int(np.ceil((n + 1) * coverage))
k = min(k, n)
return float(over_sorted[k - 1])
```

What it does: picks the calibration residual at rank `ceil((n+1) * 0.90)` rather than a plain
90th percentile.

Why it is there: this is the split-conformal quantile from Lei, G'Sell, Rinaldo, Tibshirani,
Wasserman (2018). The `n+1` accounts for the one extra (unseen) test point being ranked among the
`n` calibration points. It is what makes the 90% coverage guarantee exact in finite samples
rather than only approximate.

Expected question: "Why the plus one? Isn't that just the 90th percentile?"
Answer: not quite. Standard conformal prediction ranks the new test point against the `n`
calibration points, so there are `n+1` possible positions. Taking `ceil((n+1) * coverage)`
guarantees at least 90% coverage for any sample size, not just asymptotically. With our
calibration set of ~55,000 rows the difference is tiny, but it is the theoretically correct form
and costs nothing to write.

---

## 4. Zero-variance features dropped on the train split only

Where: `make_splits.py`, `select_features()`.

```python
std = X.iloc[train_idx].std(axis=0, ddof=0)
kept = [c for c in X.columns if std[c] > 0.0]
```

What it does: removes the constant columns (all 53 fixed-dispatch `genp_` columns, plus a few loads
that never varied), using variance computed only on the training rows. (The exact count shifted
between the clip-era and v2 builds, because resampling the generator setpoints changed which load
columns stayed constant, so I describe the families rather than pin a number.)

Why it is there: a constant column carries no signal and breaks standardization (dividing by a
zero standard deviation). Computing "which columns are constant" from the training split only
keeps the choice honest: nothing about the calibration or test data is allowed to influence which
features the model uses.

Expected question: "Why compute variance on train instead of the whole dataset?"
Answer: to avoid even a small leak. Any decision that shapes the model, including which features
exist, must be made without looking at calibration or test data. Using train-only variance keeps
the train/calibration/test wall complete.

---

## 5. Renormalizing the second split

Where: `make_splits.py`, `make_splits()`.

```python
cal_share = cal_frac / (1.0 - train_frac)
```

What it does: after 60% of scenarios go to train, the remaining 40% is split into calibration and
test. To get 20% of the WHOLE into calibration, we take 20/40 = 50% of that remainder.

Why it is there: `GroupShuffleSplit` works on whatever set you hand it. The second split only sees
the leftover 40%, so asking it for 20% would give 20% of 40% (8% of the whole), not 20%. The
division rescales the fraction.

Expected question: "Walk me through how you got a 60/20/20 split."
Answer: first split takes 60% of scenarios for train. The rest (40%) goes to a second split, where
calibration's share of that remainder is 0.20 / (1 - 0.60) = 0.50, so calibration and test each
get half of the 40%, which is 20% of the whole each. The written split.json confirms 900/300/300
scenarios.

---

## 6. Branch identity is type plus index, not the raw index

Where: `make_splits.py`, `build_design_matrix()`.

```python
branch = df["outaged_type"].astype(str) + "_" + df["outaged_idx"].astype(str)
branch_oh = pd.get_dummies(branch, prefix="br", dtype=np.float32)
```

What it does: encodes which branch is out of service as a one-hot of 186 categories, built from
the type ("line" or "trafo") combined with the index.

Why it is there: the raw index overlaps between the two branch types. Line index 5 and transformer
index 5 are completely different physical branches, but both store `outaged_idx = 5`. Feeding the
raw integer would merge them and also wrongly imply the indices are ordered (branch 10 is not
"twice" branch 5). Combining type with index and one-hot encoding fixes both problems.

Expected question: "Why one-hot? Why not just use the index number?"
Answer: two reasons. First, the index alone is ambiguous because lines and transformers reuse the
same numbers, so I join the type first. Second, branch identity is categorical, not numerical -
there is no sense in which branch 20 is larger than branch 10 - so one-hot is the correct
encoding. That gives 173 line columns plus 13 transformer columns, 186 in total.

---

## 7. Only converged N-1 rows are modeled

Where: `make_splits.py`, `load_dataset()`.

```python
keep = (df[BRANCH_TYPE_COL] != "none") & (df["converged"])
df = df[keep].reset_index(drop=True)
```

What it does: drops the 1,500 N-0 base rows (nothing is out of service in them) and the handful of
N-1 rows where the AC solve did not converge (their target voltage is missing), leaving the 278,955
converged N-1 rows the model is trained and tested on. (How many solves failed shifted slightly
between the clip-era and v2 builds, since resampling changed which scenarios diverged, so I count
what remains rather than what dropped.)

Why it is there: the screening question is specifically "after one branch trips, is the grid
safe?" The base cases are not contingencies. The non-converged cases have no `min_vm` to
predict; in deployment a non-converged solve is itself an alarm, handled outside the regression.

Expected question: "What happens to the cases your model can't score?"
Answer: the base cases are not part of the screening question and are excluded. The non-converged
contingencies carry no voltage to predict; a solver that fails to converge is already a flag in
practice, so they are not something the surrogate should guess at.

---

## 8. The speedup number is pinned to a recorded solver time

Where: `run_all.py`, `print_table()` and the `*` footnote; the solver time is read from
`data/solve_time.json`.

What it does: prints net speedup using a per-case solver time read from a committed file, not a
number hardcoded in the script. The basis is the minimum over the timed solves (9.14 ms), with the
standard deviation (0.26 ms) and the hardware recorded in the manifest beside the file.

Why it is there: net speedup is the only one of the four metrics that depends on a timing
measurement, and per-solve time depends on the numba setting, the solver options, and the machine.
Pinning it to a single recorded value, measured under a fixed configuration, keeps the number
reproducible and stops it drifting run to run. The minimum is used on purpose: contention and
scheduling only ever add time to a solve, so the fastest timed solve is the closest estimate of the
true per-case cost. Escalation, coverage, and missed-violation rate carry no timing and are final
regardless.

Expected question: "Is your speedup number real?"
Answer: yes, and it is pinned. The solver time in the denominator is read from a committed file, not
typed into the code: 9.14 milliseconds per case, taken as the minimum over the timed solves, with
the spread and the machine recorded alongside it. I use the minimum because a busy machine can only
make a solve slower, never faster, so the fastest one is the honest floor. The escalation rate the
speedup is built on carries no timing at all, so it was already final.

---

## 9. Why the gradient-boosted model misses almost 7% of true violations

Where: the missed-violation metric in `gate_eval.py` / `run_all.py`; the value is in
`data/frozen_poster_numbers.json` and `data/screener_metrics.json`.

What it does: reports the share of true violations the gate certified as safe. For the
gradient-boosted model at the 90% coverage target it is 6.91%.

Why it is there: this is a measured outcome, not a design choice, and it is the safety cost of the
gate at that operating point. The clip-era build reported 3.01% (CLAUDE.md 5.5); the clean v2 build
reports 6.91%. Two things moved between them, and they contribute about equally. The counts below are
derived from the committed rates, and they assume the same converged-row count for both builds
(278,955 for v2 from frozen, against 278,960 for the clip build in notes/artifact-clip-0.94.md, a
difference too small to matter):

- Absolute misses rose. Derivation: clip 278,955 x 28.6% x 3.01% = about 2,401 missed; v2 278,955 x
  17.48% x 6.91% = about 3,367 missed. That is about 966 more real violations slipping through.
- The violation pool shrank. Derivation: clip 278,955 x 28.6% = about 79,781 violations; v2 278,955
  x 17.48% = about 48,761. The clean build has fewer true violations.
- The rate move splits about evenly. Derivation: holding the misses at the clip count but dividing
  by the v2 pool gives 2,401 / 48,761 = about 4.92%. So 3.01% to 4.92% is the shrinking denominator
  (about 49% of the move), and 4.92% to 6.91% is the genuine rise in missed cases (about 51%).

Expected question: "Is 6.91% missed violations good enough?"
Answer: no, and I would not deploy at that point. Ninety percent coverage looks fast, but for a
safety screener, missing almost seven percent of real violations is too many. Some of the jump from
the old three percent is arithmetic, because the clean build has fewer true violations, so the same
misses are a bigger share. But not all of it. In absolute terms the model misses about 966 more real
violations on the clean data, so it genuinely got less safe, not just differently scaled. The honest
reading is that you move to a higher coverage target, around 0.96, where the missed rate drops under
one percent, and you accept the slower speedup that comes with it.

---

## 10. Why the more accurate model is the less safe one

Where: the model choice between ridge and gradient-boosted trees; fit quality in
`data/screener_metrics.json`, operating points in `data/frozen_poster_numbers.json`.

What it does: compares the two surrogates across coverage targets. The gradient-boosted model fits
better (R2 0.913 against 0.777 for ridge), yet it is not the safer choice.

Why it is there: fit quality and deployment safety are not the same axis. The ordering of the two
models flips as you tighten the safety requirement:

- At 0.90 coverage the gradient-boosted model is faster (3.04x against 2.08x) but misses more
  violations (6.91% against 3.23%).
- At 0.96 coverage the two tie on speedup (both 1.40x) while ridge is far safer (0.22% missed against
  0.84%).
- At 0.97 coverage ridge is both safer and faster (0.03% missed at 1.34x against 0.45% at 1.32x).

Which model you would actually deploy depends on the safe operating point, and there the ordering
lands on ridge.

Expected question: "Your gradient-boosted model has the higher R2. Why isn't it the obvious choice?"
Answer: because R2 does not tell you which model to deploy. The gradient-boosted model fits the
voltages more closely, but a tighter fit gives a tighter band, and a tighter band certifies more
cases, including some that should have escalated. Watch what happens as you tighten the safety
requirement. At ninety percent coverage the boosted model wins on speed but misses almost seven
percent of violations against ridge's three. By ninety-six percent they are tied on speed and ridge
is about four times safer. By ninety-seven percent ridge is both safer and faster. The model with the
better fit is the one you would not ship.

---

## 11. What boundary mass is, and why it floors escalation

Where: a property of the dataset, not a line of code; the figure is in
`data/frozen_poster_numbers.json`, the mechanism in CLAUDE.md section 3.

What it does: measures how many converged N-1 cases sit in the thin voltage strip just above the
limit. On the v2 build, 56.86% of them fall in [0.94, 0.945), a window half a voltage-hundredth wide
above the 0.94 floor.

Why it is there: the gate escalates a case when its band straddles the limit, which happens when the
prediction sits between the limit and the limit plus q_hat. So escalation is governed by how many
cases live in that strip, not by how accurate the model is. When most cases already sit right at the
limit, a large fraction land in the strip for any usable band width, and escalation stays high even
for a perfect model. That floor is the finding: on this network the gate cannot escalate much less
than the boundary mass, no matter how good the surrogate gets.

Expected question: "Explain boundary mass to me like I don't know conformal prediction."
Answer: the model predicts the lowest voltage after a line trips, and I put a small margin around
that prediction. If the whole margin is above the safe line, I certify. If it is all below, I flag.
If it crosses the line, I cannot tell, so I send that case to the exact solver. Here is the catch on
this grid. Almost fifty-seven percent of cases already sit in a razor-thin band right above the safe
line. So for any sensible margin, most of them cross the line and get sent to the solver. It is not the
model being weak. It is that the answers pile up exactly where the decision is hardest, and no amount
of model accuracy moves that pile.

---

## 12. Why one global quantile, when the closest prior work argues against it

Where: `gate_eval.py`, `calibrate_qhat()`, which computes a single q_hat over the whole calibration
set; the objection and answer are recorded in notes/prior-art.md section 6.3.

What it does: uses one conformal quantile for every case, rather than a quantile that adapts to the
contingency or to the local neighborhood of the test scenario.

Why it is there: the closest prior work (arXiv:2602.07995v2) opens by arguing that a single global
quantile is valid but inefficient, under-covering severe contingencies and over-conservative on
routine ones. They fix it two ways: stratifying the calibration residuals by contingency level and
grid element, and kernel-weighting them by similarity to the test scenario. On IEEE-118 their
kernel-weighted version is about 64% tighter (mean q_hat 0.019 against 0.054). The global quantile
here is deliberately the baseline case, because the finding does not depend on band width.

Expected question: "They show a locally adaptive band is much tighter. Why did you not use one?"
Answer: because it would not change the result. Their point is right. A locally adaptive band is
tighter, and if the story were about squeezing the band, I would use theirs. But my finding runs the
other way. Escalation stays floored by how many cases sit near the limit, and that floor does not
move when the band gets tighter, so the global quantile is the honest baseline for showing it. One
caveat I say up front: their tighter numbers are on line loading and mine are in per-unit voltage, so
the figures are not directly comparable. The argument is structural, not a number-to-number contest.

---

## 13. Why no neural network

Where: model choice in `surrogate.py` (ridge and gradient-boosted trees); dependencies in
`requirements.txt`, the code-style constraint in CLAUDE.md section 4.

What it does: trains a linear model and a gradient-boosted tree model. There is no deep-learning
framework in the dependencies (scikit-learn only, no torch or tensorflow).

Why it is there: several practical reasons, and one that matters more than the rest. The practical
ones:

- The data is tabular and this size, where gradient-boosted trees are competitive with neural
  networks.
- Training runs on a laptop.
- Every line has to be explainable at the poster.

The stronger reason is that the bottleneck here is the density of outcomes near the threshold, not
model capacity, so a larger model would not lift the escalation floor. Showing that with a simple,
readable model is cleaner than showing it with a big one.

Expected question: "Would a neural network do better?"
Answer: it would fit a little better, and it would not help. The thing holding the gate back is not
the model. It is that most cases sit right at the decision boundary, so they escalate no matter how
good the prediction is. A bigger model gives a tighter band, but the floor is set by the data, not
the band. So a neural network would add training cost and take away my ability to explain every line,
and it would run into the same floor. A simple model makes the point without the baggage.

---

## 14. How the clipping artifact was found

Where: the dataset generator, `generate_dataset.py`; the diagnosis is in notes/artifact-clip-0.94.md.

What it does: nothing in the current build. This entry records a bug that was in an earlier build,
and how it was caught and fixed.

Why it is there: while inverting the sensitivity of escalation to band width, the inversion returned
nonsense, demanding impossible accuracy to reach a target escalation. That is the signature of a
spike sitting exactly on the threshold rather than a smooth spread of values. The spike traced to one
line where the generator setpoint clip reused the 0.94 screening constant, so perturbed setpoints
piled up at exactly 0.94. The fix was to resample the setpoints instead of clipping them, and a guard
(test T9) now fails if any single voltage value takes more than one percent of the rows, so the same
spike cannot return unnoticed. The dataset was regenerated, the spike went to 0.00%, and the boundary
mass held at 56.86%.

Expected question: "How do you know your results are not another artifact?"
Answer: because I found the last one by noticing the math stopped making sense. When I inverted the
escalation curve, it asked for accuracy no model could reach, which only happens when the values are
piled on a single point instead of spread out. I traced that to one line where the setpoint clip had
borrowed the screening limit, so draws that should have spread out all landed on 0.94. I switched
clipping to resampling, and I added a test that fails if any voltage value ever takes more than one
percent of the rows. After regenerating, the spike was gone and the boundary-mass finding was still
there. One thing I will not hide: removing the artifact made the safety numbers worse, and I can say
exactly why. A case pinned at exactly 0.94 was pinned there by a clipped generator setpoint, and that
setpoint is one of the model's own inputs, so the model could read the answer straight off its
features. Those cases were trivially predictable, so the clip had been gating them for free (CLAUDE.md
5.5 records the atom sitting at a model-input value). Once resampled, those boundary cases became
genuinely hard, which is the real half of the increase: about 966 more true violations missed. The
gradient-boosted missed rate went from 3.01% to the honest 6.91%. That is the number I stand behind.

---

## 15. Why screen at 0.94 when the standard is 0.95

Where: the screening constant in the gate, the 0.94 limit the band is compared against.

What it does: sets the under-voltage floor. A band is certified safe only if it sits entirely above
this value, flagged if entirely below, and escalated if it crosses.

Why it is there: the service-voltage standard (ANSI C84.1 Range A, NERC guidance) is 0.95 pu, so 0.95
would be the natural screening limit. On this network it does not leave a workable population. The
evidence is the N-0 base voltages, which by construction all clear 0.94 (from the threshold table in
notes/artifact-clip-0.94.md, clip-era build):

- Only 44 of the 1,500 accepted bases (2.93%) also clear 0.95.
- The base voltages span roughly [0.940, 0.960], a band about two voltage-hundredths wide sitting
  right on the floor.

Screening at 0.95 would leave almost nothing certifiable before any contingency even runs. The
resampled v2 build raises base voltages somewhat, so the true share clearing 0.95 is higher than
2.93%, but the direction holds: this network is marginal at 0.95 under this sampling.

Expected question: "The standard is 0.95. Why is yours 0.94?"
Answer: you are right that the standard is 0.95, and I use 0.94 for a measured reason, not
convenience. On this grid, under the feasibility gate that keeps only cases with a workable starting
point, almost none of the accepted bases clear 0.95. On the build behind the poster it was 44 out of
1,500, and even after the cleaner rebuild raised voltages a little, it stays low. The base voltages
sit in a thin band right on the floor, so at 0.95 there would be nothing left to certify before a line
even trips. The honest caveat is that this is a property of this network under this sampling. On a grid
with more voltage headroom you would screen at 0.95, and I would want to recheck it there.

---

## 16. One network

Where: the whole study runs on IEEE 118-bus (case118); the scope limit is stated in CLAUDE.md 6.

What it does: nothing in the code. This entry states the generalization limit before a judge raises it.

Why it is there: the claim is deliberately narrow.

- What is supported: calibrated under-voltage screening on case118 under diversified, N-0-feasible
  N-1 stress, not contingency screening in general (CLAUDE.md 6).
- What would transfer: the mechanism, not the number. Escalation is governed by how many cases sit
  near the threshold, and any marginal network should show the same density-driven floor.
- What it needs to be shown: a second network, which is fall work. The intended comparison, case300,
  does not converge under the enforced-reactive-limit oracle at any load scale tested, which is itself
  a recorded finding (CLAUDE.md 7.3).

Expected question: "You have one network. Why should I believe this generalizes?"
Answer: I would not claim it generalizes yet, and I say so on the poster. What I have is one network,
case118, and the honest scope is under-voltage screening on that grid under this stress. What I think
transfers is the mechanism, not the exact numbers: escalation is floored by how many cases sit right
at the limit, and any marginal grid should have that same pile-up. Testing that needs a second
network, which is fall work. I tried case300 as the comparison and it would not converge under the
correct reactive-limit oracle at any load I tested, so that itself is a finding, and I am still
looking for a network that both converges and is stressed enough to be interesting.

---

## 17. No classical baseline

Where: the comparison in the speedup accounting is against brute-force AC power flow.

What it does: the net-speedup metric charges escalated cases the full AC solve time and compares the
total against solving every case with AC.

Why it is there: brute-force AC is the correct upper bound on cost, but it is not what an operator
runs, and there are cheaper classical voltage screens this project does not compare against.

- DC power flow is not one of them. DC cannot see an under-voltage at all: it holds bus voltage
  magnitudes at their setpoints, so the minimum does not move with load. Verified directly in
  notes/prior-art.md section 3, where DC keeps min_vm at 0.9430 across load 1.0 to 1.6x while AC
  collapses to 0.87.
- Classical voltage screens do exist. Performance-index and sensitivity methods trace back to Ejebe
  and Wollenberg, 1979 (prior-art.md section 3), and the closest prior work benchmarks against DC
  power flow and a threshold-tuning baseline (prior-art.md 6.5). Neither is implemented here.

Expected question: "You compare against brute-force AC. Operators do not run that. Where is your real
baseline?"
Answer: fair, and I will concede it cleanly. Brute-force AC is the honest ceiling on cost, but it is
not the operational baseline. The one people reach for first, DC power flow, does not apply here at
all, because DC holds voltages at their setpoints and cannot see an under-voltage, and I checked that
directly. What does exist is the classical voltage-screening literature, performance-index and
sensitivity methods going back to Ejebe and Wollenberg in 1979, and I have not implemented one. So the
correct thing to say is that a classical baseline is a known gap, not that no baseline exists.

---

## The one-line version for each

- Split by scenario, or the coverage guarantee is a lie (exchangeability).
- One-sided band, because only downward voltage errors are dangerous.
- Rank ceil((n+1) x 0.90), the exact finite-sample conformal quantile.
- Drop constant features using train only, so nothing leaks.
- cal_share = 0.20 / 0.40 = 0.50 to hit a true 60/20/20.
- Branch = type + index, one-hot, because indices overlap and are categorical.
- Model only converged contingencies; base cases and non-converged solves are handled separately.
- Speedup is pinned to a recorded minimum solver time (9.14 ms); the other three metrics carry no timing.
- Almost 7% missed at 90% coverage is the safety cost there; you move to higher coverage to get under 1%.
- Better fit (R2) does not mean safer to deploy; the model ordering flips at the safe operating point.
- Boundary mass is the pile of cases right at the limit; it floors escalation regardless of model accuracy.
- One global quantile on purpose; the escalation floor does not move when the band tightens.
- No neural network; the floor is set by outcome density near the threshold, not model capacity.
- Found the clip artifact when the sensitivity inversion demanded impossible accuracy; fixed by resampling, guarded by test T9.
- Screen at 0.94 not 0.95 because almost nothing clears 0.95 on this grid (44 of 1,500 bases); network-specific, would be rechecked elsewhere.
- One network, case118; the mechanism is what would transfer, and a second network is fall work (case300 does not converge under the correct oracle).
- The baseline is brute-force AC; DC cannot see voltage and classical voltage screens exist but are not implemented, a known gap.
