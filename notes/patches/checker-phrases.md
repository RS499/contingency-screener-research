# checker-phrases — OS-6 "proven methods", OS-10 "escalation floor"

Fix specification only. No replacement wording.

## 1. Ledger IDs + severity
- **OS-6** "proven methods" (checker banned phrase) — MINOR.
- **OS-10** "escalation floor" (checker banned phrase) — MINOR on its own; entangled with **C12 / P-014**
  (MAJOR: the floor is never defined or given a number).

## 2. Anchors
- OS-6: "Calibrated uncertainty, as well as making the decision" — l.361 (phrase at end of the
  sentence: "…are proven methods.").
- OS-10: "This escalation floor is set by how the" — l.365.
- Related, not flagged: heading "The boundary layer sets a floor on escalation" — l.312; "the
  reasoning for the existence of such a floor" — l.388; "I explain why there must be a certain floor
  for escalation" — l.101.

## 3. Old text (verbatim)
- l.361: `Calibrated uncertainty, as well as making the decision of either outsourcing the problem or not to a more complex model \cite{desalvo2015} and providing the model with multiple choices \cite{angelopoulos2024,cortes2016,chow1970,elyaniv2010}, are proven methods.`
- l.365: `This escalation floor is set by how the distribution of the data occurs in relation to the 0.94 pu limit.`

## 4. What must change (content)

**Checker evidence (read-only run, 2026-09-27):** `.venv/bin/python scripts/check_paper.py
report/paper_current_STS.tex` → exit 1; section "PHRASE / TAG REGRESSIONS":
`line 361 phrase: \bprove[sn]?\b` and `line 365 phrase: escalation floor`. No other phrase hits.

**Which regex fires and what it covers** (`scripts/check_paper.py` l.48-58, `PHRASE_REGEXES`,
case-insensitive, applied per line after stripping `%` comments):

| Pattern | Fires on | Does NOT fire on (tested) |
|---|---|---|
| `\bprove[sn]?\b` | l.361 "proven"; would also catch "prove", "proves" | l.314 "proved" (Chow's theorem — a correct use about a cited proof); l.367 "proof"; "provides/providing" (l.99, 109, 231, 361); "provenance", "improve", "approved" |
| `escalation floor` | l.365 only | l.312 heading ("sets a floor on escalation" — word order differs); l.388 "such a floor"; l.101 "a certain floor for escalation" |

**Why each is banned — what the notes record.**
- Both patterns were added by the owner on 2026-08-03 as corrections to the checker spec:
  `notes/ai-prompt-log.md` l.1330-1334 ("phrase list uses `lands on the saturation`, split
  `\bfirst to\b` and `subtract.*savings`, add `escalation floor` and `must be safe on every case`").
  First committed in `d32f309` (2026-07-28 per `git log -S`). **No stated rationale for either
  pattern was found** in `notes/` (grep over handoff-2026-08.md, writing-guide.md, RUN_REPORT.md,
  ai-prompt-log.md, sts_review.md, number_check.md, placement_plan.md). Recorded context only, not
  a rationale:
  - `prove*` sits with `\bnovel\b` and `\bfirst to\b` — the CLAUDE.md §8 overclaiming guard. At
    l.361 the word also asserts something about cited work (that three-way / defer / cascade
    methods are "proven") that no cited source is checked to support (`notes/sts_review.md` l.294-295,
    l.498; `notes/placement_plan.md` l.439).
  - `escalation floor`: `notes/writing-guide.md` §2.8 (l.318-330) records "the floor exists on any
    network" as a barred network-general claim; l.866 bars "any network-general statement of the
    escalation floor". The panels add the definitional problem: the paper never gives the floor a
    number and the section titled "floor" reports ceilings and a saturation point (NS-14 / P-014),
    and the legacy key name `perfect_model_floor_saturation` names a ceiling-side quantity "floor".
    That the ban was *meant* to address these is an inference, not a recorded reason — the author
    should confirm what they intended when adding it.

**What must change — OS-6:** the sentence's content (these ideas already exist in prior work; two
things differ here) is sound and matches the claim ceiling; only the unsupported certainty word
must go. The replacement must not carry any `prove*` form.

**What must change — OS-10 (author decision required, content only):** the checker bans the
two-word term while C12/P-014 require the paper to *define* a floor with a number. The author must
pick one of:
- (a) **Keep "floor" as the paper's term**, define it once with a value ± std at a named operating
  point (C12/P-014), and then either never juxtapose "escalation" + "floor" as a bigram, or ask the
  owner-of-checker (the author) to retire the `escalation floor` pattern — a script edit the author
  decides and makes; this spec does not edit the gate.
- (b) **Drop "floor" as a term** everywhere (l.101, l.312 heading, l.365, l.388) and describe the
  quantity by what it is (the share of cases the gate must escalate at a stated missed-rate target,
  set by the boundary mass) — which also removes the collision with the "0.94 pu floor" (voltage
  limit) used at l.107 and l.303.
Either way: one term per concept, and the term the heading uses must be the term the conclusion uses.

## 5. Numbers
None printed in these two sentences. If option (a) defines the floor numerically, the numbers come
from C12/P-014's spec, not from here. re-read: n/a.

## 6. Must not claim
- That cited methods are "proven" or that the gate is a "proven" method.
- Any network-general floor ("on any network", "must be a floor") — CLAUDE.md §8; Top-5 #2(b) E7
  shows Mondrian lowers escalation (42.9 ± 1.9% vs 57.0%), so "must" is refuted on case118 itself.
- That the floor is "set by the network" — the cause is sampler × limit on case118 (Top-5 #1, P-007,
  D8); l.365's "set by how the distribution of the data occurs" is the scoped form, keep the scope.
- **Adjacent trap for 2b-5:** the same list bans `lands on the saturation`; the l.347 fix
  (numbers-2b §2b-5) must not introduce that phrase. An earlier fact-check approved "essentially
  lands on the saturation point" (`notes/factcheck-2026-08-27.md` l.357) — that wording would now
  fail the checker.

## 7. Consistency (must change in step)
- OS-10 ↔ C12/P-014 (floor definition), l.101 (C3/Top-5 #2(b) "must be a certain floor"), l.312
  heading, l.388 conclusion, OS-7 (l.388 future-work clause). Choose option (a) or (b) once and apply
  to all five places.
- OS-6 ↔ Cut-7 (merge l.361-363 with related work): if Cut-7 rewrites l.361, OS-6 is absorbed.
- After the rewrite, re-run `.venv/bin/python scripts/check_paper.py report/paper_current_STS.tex`;
  the PHRASE section must be empty.

## 8. Page cost + dependencies
0 pp. Depends on: C12/P-014 (option a vs b), Cut-7, 2b-5 (adjacent banned phrase).

## 9. Voice note
The l.361 sentence is the paper's honest concession of prior art; keep its function when removing
the certainty word.
