# Handoff — 2026-08

Current state document. Replaces `notes/sts-handoff.md`. **That file does not exist anywhere in
this repo** — confirmed by search (working tree, no hits) and by `notes/ai-prompt-log.md` itself,
which records twice (line 25, line 195, 2026-07-26) that it was referenced but never committed. It
cannot be marked superseded because there is nothing to mark; noting that gap here instead.

Built entirely from committed artifacts and `notes/ai-prompt-log.md`. Every number below cites the
file it came from. Where a number could not be sourced, it is omitted and the gap is stated.

---

## 1. Paper state

**Current version:** `paper_current.tex` (221 lines, IEEEtran `conference` class), sections
I Introduction, II Background, III Method, IV Results, V Discussion and limitations,
VI Conclusion and future work; 2 tables (`tab:ops`, `tab:models`), 4 figures, 18 bibliography
entries. As of this writing it is git-staged but **not committed** (`git status --short
paper_current.tex` → `AM`).

The document just went through the M1 → M2 (gate-aware tuned) promotion: every headline number,
both tables, and three of four figures were replaced with v2 values, source-checked in this
session's diff audit (`git diff -- paper_current.tex` against the staged index blob). See §2a.

**Venue:** not stated in any committed file. `paper_current.tex` uses the generic IEEEtran
conference class with no venue name. `notes/ai-prompt-log.md` references "Regeneron STS AI-usage
disclosure table" repeatedly (e.g. line 4, line 129) as the reason prompts are logged — that is a
disclosure requirement, not a stated venue commitment for this paper.

**What is submitted:** nothing. No submission action appears anywhere in `notes/ai-prompt-log.md`
or git history.

**Version number:** no version marker (e.g. "v10") for the paper exists anywhere in the repo —
searched `paper_current.tex`, every `notes/*.md`, and every `data/*.json` for a version string and
found none. If the paper is being tracked as "v10" externally (Overleaf revision history, a mentor
conversation), that number isn't recorded here; state it explicitly wherever it's cited so it can be
sourced next time rather than retyped from memory.

**What is still open:**
- Fig. 1's PNG (`data/gate_schematic_v2.png`) changed size this session (129,325 → 139,196 bytes,
  `git diff --stat`) from the "crosses" → "straddles" wording fix applied to
  `feasibility/gate_schematic.py` earlier this week (git-staged vs. working-tree diff). Fig. 4
  already carries an explicit repo comment about this class of problem (`paper_current.tex` line
  166: "Upload the PNG to the Overleaf data/ folder or this will not resolve"). Nothing in this repo
  can confirm whether the regenerated Fig. 1 PNG has been re-uploaded to Overleaf — flagging so it
  isn't missed, not claiming it's done or not done.
- The Acknowledgment section's disclosure sentence changed. The version at the staged git index
  read *"The authors used an AI for revising the document text; all reported numbers were produced
  by the authors' committed, tested code under a pinned solver configuration."* The current working
  tree drops the AI-revision clause entirely, reading only *"All the reported numbers were generated
  from the committed and tested code by the authors."* (`git diff -- paper_current.tex`). Given the
  volume of AI-assisted revision recorded in `notes/ai-prompt-log.md` across this project, this
  looks like a disclosure regression worth owner review, not a verified intentional change — I found
  no prompt authorizing the removal.
- `notes/contribution-log.md` (2026-07-21) documents one scoped exception where an AI drafted
  `notes/1_research_draft.txt` as a structural reference only, explicitly not submittable and not
  `paper_current.tex`. That exception is closed and does not cover the current paper text.
- Second-network testing (Discussion §V, unchanged claim) is still correctly framed as future work
  — consistent with the actual repo state (§2e, §5).

---

## 2. Results, each with artifact and date

### a. v2 gate-aware (M2) promotion
Source: `data/frozen_poster_numbers_v2.json` (`four_metrics_at_90pct_coverage`,
`safety_operating_points`, `crossings_first_below_1pct_missed`), file dated 2026-07-26. Selection
metric fixed a priori per `notes/ai-prompt-log.md` line ~391 ("M2 optimizes the deployment
objective... do not choose per-model").

At 90% target coverage:
- ridge: escalation 49.07%, empirical coverage 89.34%, missed 2.96%, net speedup 2.04x
- histgb: escalation 30.63%, empirical coverage 89.82%, missed 4.72%, net speedup 3.29x

Sub-1%-missed crossing (`crossings_first_below_1pct_missed`): ridge first at target coverage 0.94
(missed 0.79%), histgb first at target coverage 0.97 (missed 0.83%).

### b. Miss-depth distribution and the 0.849 reactive-limit mechanism
Sources: `data/missed_depth.json` (2026-07-29) for the distribution; `data/miss_mechanism.json`
(2026-07-29) for the causal mechanism.

Deepest certified miss, both families: depth = 0.0914569251411822 pu (0.0915 to 4 decimals, 0.091
to 3), y_true = 0.8485430748588177 pu (≈0.849), scenario_id 101000025, line 78 out. Independently
re-verified from scratch (not just re-reading the JSON) earlier this session: both families'
pooled-maximum certified miss at coverage 0.90 traces back to this exact row.

Mechanism (`data/miss_mechanism.json`): the weak bus is pandapower index 53 / IEEE name 54
(`weak_bus_index`/`weak_bus_ieee_name`), a PV bus with local generator (gen 21). Post-outage, that
generator saturates at its reactive minimum (`q_n1 = -194.71 MVAr = qmin`, `at_min: true`), versus
`q_n0 = -10.00 MVAr` pre-outage — a discrete PV→PQ transition, not a linear voltage drop. Bus
voltage at that location falls from `vm_n0 = 0.9549` to `vm_n1 = 0.8485` pu. The reconstruction was
independently re-solved and matched the recorded value (`solved_n1_min_vm =
0.8485430618229496` vs `recorded_min_vm = 0.8485430748588177`).

### c. Base-voltage quintile control
Source: `data/quintile_boundary_mass.json` (2026-07-31). Purpose per the file: isolate the filter
effect (base tightness against 0.94) from the network effect, within case118 alone.

Boundary mass by quintile (base_vm_mean → boundary_mass_pct), low to high base voltage:
0.94063→78.39%, 0.94183→81.28%, 0.94337→82.36%, 0.94528→37.31%, 0.94905→4.98%. This is
**non-monotonic** (rises through the third quintile, then drops sharply), Spearman rank correlation
-0.6 — not the flat/no-relationship read and not a clean monotonic one either. Violation rate by the
same quintiles IS monotonic: 21.54%→18.55%→17.19%→15.88%→14.21%, Spearman -1.0.

**Caveat, load-bearing:** this same file's `step3_top_quintile_vs_case57` field embeds
`case57_boundary_mass_pct: 30.65` — this is the KILLED number from §4. Do not cite that field. The
quintile-vs-quintile numbers above are independently computed from case118 data and are not
affected by it.

### d. case57 NO-GO
Source: `data/case57_feasibility.json` (2026-07-31), config = `COMMITTED_CFG` in
`feasibility/case57_gonogo.py`. Accept rate 0.0% (0/3000 candidate bases), nominal (unperturbed)
base min_vm 0.7199 pu, maximum achievable `n0_min_vm` over all converged draws = 0.7747 pu — case57
never reaches the 0.94 pu floor under the pinned config. Boundary mass: null (no accepted bases to
compute it over).

### e. case30 comparison
**Not sourceable — omitted.** No case30 dataset or gate result exists in this repo. What does exist:
`data/probe_alt_networks.json` (2026-07-31), a cheap 50-base feasibility probe only — case30 nominal
N-0 min_vm 0.9606 pu (clears 0.94), 50-base draw acceptance 40/50 (80%), base range [0.9417,
0.9674]. `notes/ai-prompt-log.md` (2026-07-31, "STAGE 1: generalize generator...") records that the
generator was generalized to arbitrary bus counts and proven byte-identical on case118, then states
plainly: *"STAGE 2 (build case30) not started."* Nothing since has run it.

---

## 3. FALSIFIED

**Not applicable — this result does not exist.** The task text describes a pre-registered
`rho_cal * q_hat` escalation prediction on case30, off by -53% and -68%. I searched
`notes/ai-prompt-log.md` and every `data/*.json` file for this and found nothing: the case30 STAGE 3
protocol (predicted_esc written before touching test, then compared against measured escalation)
was specified in detail in the 2026-07-31 log entry but, per §2e, STAGE 2 (building the case30
dataset it depends on) was never started. There is no `data/case30_prediction.json`, no case30 test
sweep, and no measured-vs-predicted comparison anywhere in the repo.

If this section is meant to record a real falsification, it has not happened yet in this repo and
should not be written as if it had. Leaving this as an explicit gap rather than a fabricated entry,
per the standing "never invent a metric value" rule (`CLAUDE.md` §8) and this project's own repeated
pattern of halting on unsourced numbers (§4).

---

## 4. KILLED NUMBERS

**case57 "87% acceptance, 30.65% boundary mass, base range [0.94000, 0.99464]" — unsourced. Must
never enter the paper, poster, or any frozen artifact.**

Source of this finding: `notes/state-of-project.md`'s DO-NOT-USE banner (dated 2026-07-31, at the
top of that file) and the matching `notes/ai-prompt-log.md` entry (2026-07-31, "provenance +
alt-network probe"). A full provenance search — repo files, git history, session transcripts — found
these numbers in exactly two places: the text of two prompts in `notes/ai-prompt-log.md`, and
artifacts derived from those prompts (`feasibility/quintile_boundary_mass.py`'s hardcoded
`CASE57_BOUNDARY_PCT = 30.65`, carried into `data/quintile_boundary_mass.json`). No tool run
anywhere in project history ever computed them from data. The only COMPUTED case57 result is
`data/case57_feasibility.json` (§2d), which shows the opposite: 0.0% acceptance, not 87%.

**"0.057 pu" sensitivity-screen depth over-prediction — also unsourced, killed the same way.**
Source: this session's `notes/ai-prompt-log.md` entry (poster figure regeneration STEP 5). Searched
`notes/`, `paper_current.tex`, and all scripts for `0.057`: no match anywhere. The real committed
value, from `data/classical_screen_metrics.json`'s `fit_quality` block, is `mean_signed_err =
0.00357354565325938` pu (0.0036 to 4 decimals; MAE 0.0038 pu; 63.44% of predictions over-predict).
Do not use 0.057 in any document.

---

## 5. Open experiments not run

**Reactive-headroom features.** Fully specified in `notes/ai-prompt-log.md`, "Prompt 16" (2026-07-31,
"reactive-headroom features; metric/diagnostic pinned before any run") but never executed — no
outcome is recorded after that prompt, and no matching artifact exists. The design: compute
per-generator `q_headroom_up`/`q_headroom_down` from each base's N-0 solve, test in three feature
arms (baseline; baseline + hop-limited/system-total headroom scalars; baseline + full per-generator
vector), with the primary metric pinned in advance (count of misses deeper than 0.02 pu + expected
shortfall of depth given a miss, not max depth). It would test whether the miss-mechanism found in
§2b (a generator hitting its reactive limit) is something the surrogate could see coming from
pre-outage features, or whether it is a genuinely undetectable discrete event given only N-0
information — directly separating "no signal" from "unpredictable."

**The exact identity from calibration predictions.** Not previously specified in the log — this is
inferred, not sourced, and stated as such. In this session's per-seed reconstruction of the deepest
miss case (scenario 101000025, line 78 out), that row landed in the TEST split for both families in
seeds 1–3 and in TRAIN for seeds 0 and 4; it was never observed in a CALIBRATION split for either
family across the 5 seeds checked. The open question this leaves: when this same case (or one like
it, a generator-Q-limit-bound scenario) does land in calibration for some seed, does its residual
look like an outlier relative to the rest of the calibration set, or does the one-sided conformal
quantile treat it as unremarkable? If it is identifiable in calibration, that would be evidence the
boundary-mass floor is partly addressable with a locally-adaptive band (`romano2019`,`barber2021`,
already cited in the paper as an alternative not pursued); if it is not identifiable, that supports
the current claim that no feasible calibration-time signal separates these cases.

**A third network.** case89pegase and case300 were probed at the same cheap level as case30
(`data/probe_alt_networks.json`, 2026-07-31): case89pegase clears N-0 with the best margin of the
three (nominal 0.9684 pu, 50-base draw 19/50 = 38% accepted) but carries an explicit PEGASE
per-unit-convention caveat noted in that same file — the 0.94 pu floor may not be physically
applicable there without checking PEGASE's voltage-limit convention first. case300 does not
converge under the pinned oracle at nominal loading (NO-GO, same file). This would test whether the
boundary-mass floor and its Q-limit mechanism (§2b) are a property of case118 specifically or
recur on a differently-shaped network, addressing the "no network-general claim" limitation stated
in Discussion §V of `paper_current.tex`.

---

## 6. Conventions currently enforced

**Mechanical** (`.claude/hooks/`, wired in `.claude/settings.json`, fire on every tool call
including inside subagents):
- `guard_paths.sh` blocks any Write/Edit to `data/frozen_poster_numbers.json` or
  `data/screener_metrics.json` (exit 2, the read-only freeze) and to `notes/1_research_draft*.txt`
  (the AI-disclosure-evidence file).
- `guard_python.sh` blocks any Bash command invoking bare `python`/`python3` (exit 2); only
  `.venv/bin/python` is allowed.

**`check_paper.py` does not exist anywhere in this repo.** There is no mechanical paper-consistency
checker. Any claim-vs-data check on `paper_current.tex` (like the diff audit in §1, or the KILLED
NUMBERS in §4) is currently manual, done per session, not automated.

**Convention only** (`CLAUDE.md`, `CLAUDE.local.md` — prompt-level, not hook-enforced, and can drift
across sessions):
- **Std rule** (`CLAUDE.md` §8): never state a difference smaller than the larger of the two
  reported stds as real.
- **M1/M2 rule and variant labeling** (`CLAUDE.md` §8): M2 (gate-aware) is the promoted surrogate
  selection; never quote an M1 (MAE-selected) number as the result. The file-naming half of this
  convention — `_v2` suffix for promoted-model artifacts (`frozen_poster_numbers_v2.json`,
  `tradeoff_curve_v2.json`, `gate_schematic_v2.png`, ...), unsuffixed for the original committed
  build — is followed consistently across every artifact cited in §2, but is convention, not
  hook-enforced; nothing blocks writing a new artifact without the suffix.
- **IEEE bus numbering** (`CLAUDE.md` §5): prose and the paper use IEEE 1-based bus names; code and
  artifacts use pandapower 0-based indices; IEEE name = index + 1 on case118; never mix the two
  conventions in one document. This convention was actively violated and fixed this session —
  `feasibility/domain_figure.py` was labeling critical-bus hotspots with the raw 0-based index
  (e.g. "bus 75") until corrected to IEEE names ("bus 76") mid-session, confirmed against the live
  dataset. Nothing mechanical would have caught that drift; a hook only exists for the two frozen
  files and the AI-disclosure file (above), not for numbering-convention consistency.
- **Read numbers from artifacts, never retype** (`CLAUDE.md` header: "No result number appears in
  this file. Read every metric from the JSON"; restated in `CLAUDE.md` §8 "Verify before writing").
  This is the rule the entire KILLED NUMBERS section (§4) exists to enforce after a violation: the
  case57 87%/30.65% figures entered a prompt's CONTEXT block by hand and were then carried into
  `feasibility/quintile_boundary_mass.py` as a hardcoded constant instead of being computed.
- Manifest beside every new artifact.
- No-overclaiming: no "first"/"novel method"; no network-general claim from one network; speedup
  restates the escalation axis, not independent evidence.
- Append every prompt to `notes/ai-prompt-log.md`.
- Disclosure default for support, mentors, AI toolchain (see §1's open item on the Acknowledgment
  regression — an example of exactly this kind of drift).
- Report before editing, show diffs; Claude stages, the owner commits/pushes.

---

## 7. Known-stale text elsewhere in the repo

- **`README.md`** is badly stale. It states "No surrogate or conformal wrapper exists yet," frames
  the project as still at the feasibility stage, and cites pre-screener dataset figures (17.5%
  violations / 78.1% straddle, framed as "metrics to be measured" that "[n]one of these are measured
  yet"). All of that predates the surrogate, the conformal gate, the tables, and every figure now in
  `paper_current.tex`.
- **`notes/frozen-gaps.md`**'s "Repo-state reminders" section (undated within the file, predates this
  session's poster work) says "Poster-to-paper size presets are not built" — a `--poster` CLI mode
  was in fact added to six figure scripts this session (`notes/ai-prompt-log.md`, poster figure
  entries). The reminder to set `CREDIT_ENABLED = True` and re-render before any poster/STS
  submission is, however, still open and unaddressed: `feasibility/figtools.py` currently has
  `CREDIT_ENABLED = False`, and the poster figures produced this session were rendered without
  per-figure credit.
- **`notes/state-of-project.md`** already carries its own stale banner ("Stale, 2026-07-21... for
  current state see CLAUDE.md section 0") — not a new finding, but noting it here since the file is
  long and the banner is easy to scroll past; its DO-NOT-USE case57 banner (§4) is the one part of
  it that is still load-bearing.
- The Acknowledgment disclosure regression in `paper_current.tex` — see §1.
