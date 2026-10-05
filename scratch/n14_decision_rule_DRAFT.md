# N14 decision rule — C24 amendment, islanding outages, and the two N13 analyses that did not run

- **Written:** by Claude Code on 2026-10-05 at the owner's request; owner decisions settled 2026-10-05.
- **When it takes force:** when the N14 run (`scratch/run_prompt_n14.md`, Step 1) copies this file unchanged to
  `scratch/n14_decision_rule.md` and hashes it, after the owner has pushed it.
- **Facts it rests on:** `scratch/n14_prefacts.md` (read-only checks, 2026-10-05).
- **What was already seen.** All N13 results exist and were seen when this was written (`scratch/n13_result.md`).
  Every N14 verdict below is a re-analysis of the rebuilt N13 datasets, decided once already on them, and the
  paper reports it as such.
- **Two parts are post hoc and are flagged where they occur:** the §A tolerance and the §B exclusion criterion.
  Both were written AFTER seeing the N13 result they change.

## 0. Tolerances and cutoff

- **Tolerances.** Every equality check in this rule states a numeric tolerance or is a hash comparison:
  - voltages: 1e-9 pu;
  - files: sha256 equal to the value recorded in the named manifest.
  - The word "exactly" is never used without one of these.
- **Cutoff: 2026-10-12 23:59 America/New_York.**
  - The run checks the time before every step.
  - If N14 is not finished by then, the paper uses the N13 results, each stated as such: trafo 63 included,
    C24 excluded.
  - After the cutoff, the run finishes the step in progress, writes its result file and starts nothing new.
    Anything unfinished is reported as "not run", never estimated.

## A. C24 amendment

**What N13 required.** Check 3, pinned clause: "its pinned outage minima equal the old stored `min_vm`
exactly" (`scratch/n13_decision_rule.md` §2).

**Why it was mis-specified.**
- **The failure:** C24 failed only this clause. Its pinned minima differ from the old stored values by at most
  **1.95e-14 pu**, on 1,062 of 2,266 compared rows (`data/sts_n13_build_C24.json`).
- **Corrected labels reproduce:** C24's corrected labels match the old switch-back labels within 1e-9 pu (max
  difference 0), with 0 status mismatches. Checks 1, 2, 4, 5 and 6 passed.
- **The cause is part of the prescribed method:**
  - The N10/N11 corrected solve adds one out-of-service helper sgen per generator before the pinned solve.
  - On a network that already has sgens (C24 has 22), this changes pandapower's floating-point summation order.
  - The same effect was present in N11 (max 1.03e-13 pu).
- **Purpose of the clause:** to prove the code path is identical, and 1.95e-14 pu is floating-point noise.

**Amendment.**
- Check 3's pinned clause becomes: "its pinned outage minima equal the old stored `min_vm` within **1e-9 pu**",
  the same tolerance as the corrected clause.
- It applies to every dataset.
  - Every other N13 dataset passed with a maximum difference of 0, so for them the amendment changes nothing.
    The run re-states this from the N13 build files.
- **Post hoc:** the tolerance was chosen after seeing the 1.95e-14 pu failure.

**Procedure.**
1. Re-run check 3 for C24 under the amended clause, from the existing N13 files (`data/sts_n13_C24.parquet`,
   `data/sts_n13_audit_C24.parquet`). No rebuild.
2. **If it passes,** run C24's tier-A analyses as N13 rule §3 specifies (the tier-A rows that list C24):
   - gate with full M2 re-search (`scratch/n11_smallnets.py` procedure);
   - fixed-budget static at k_B, COND-HIST and GLOBAL-STATIC (N10 Part B; N12 Part A);
   - the cross-network table row (N12 Part C).
   - Then apply BEATS-STATIC and GATE-BEATS-CONDHIST to C24 under their N13 definitions.
3. **If it fails, C24 stays excluded.**
- **Old C24 results (N11) stay unused,** in every case.

**Arm F disclosure, in this rule and in the paper:** "Arm F had produced C24 safety numbers (missed, escalation,
speedup) on the original C24 bases with corrected inputs before this amendment; the gate-vs-baseline comparisons
had not been computed."

**Amendment disclosure sentence for the paper:** "case24 is included under a pre-registered amendment (N14) that
replaced N13's exact-equality check on pinned voltages with a 1e-9 pu tolerance; the original check failed by at
most 1.95e-14 pu, a floating-point difference."
- This sentence is used only if C24 passes the re-check. If it fails, the paper states that C24 stays excluded
  under the amended check.

## B. Islanding outages

**Definition.** An islanding outage is a single-branch outage after which at least one bus is no longer connected
to the reference (ext_grid) bus. Topology is scenario-independent in every dataset.

**How N13 labelled them** (`scratch/n14_prefacts.md` item 3):
- `min_vm` was the minimum over buses in the reference bus's island; cut-off buses had NaN voltages and were
  excluded.
- No islanding row was dropped.

| Dataset | Islanding outages | Rows | Share of converged outage rows |
|---|---|---|---|
| D94 | 9 | 13,500 | 4.84% |
| ILL | 72 | 108,000 | 29.98% |
| C30 | 3 | 4,500 | 7.32% |
| C24 | 1 (line 9) | — | — |

**Method assumption, stated:** any generation lost in a cut-off island is picked up by the single slack (ext_grid)
bus. There is no distributed slack, no load shedding and no frequency model.

### Primary (option 3): keep islanding outages

- **Label:** the lowest voltage on buses still connected to the island that contains the reference bus. This is
  the N13 label, unchanged.
- **Lost load** on cut-off buses is a separate event that the gate does not screen.

### Exclusion (applied in the primary analysis)

> Exclude any outage after which the island containing the reference bus holds fewer than half of the network's
> buses. This criterion was written after identifying trafo 63 on case_illinois200 as the only outage that meets
> it; its 1,500 rows are all labelled 1.04 pu, the slack setpoint, and describe one bus, not the grid.

- Excluded outages' rows are removed from train, cal and test. The splits are drawn by base case and do not change.
- **What it removes:** ILL trafo 63 only (1,500 rows of the rebuilt ILL).
  - No other outage on any network meets it: every other islanding outage leaves at least 95.8% of the buses
    connected.
  - No N2R pair meets it.
- **The paper states this criterion and its post-hoc origin in those words.**

### Primary results per network

- **D94 and C30: restated from N13, not recomputed.** Neither has an outage that meets the exclusion criterion,
  so their primary datasets equal N13's.
  - **Condition:** the sha256 of each N13 dataset file and of each N13 analysis output reused must equal the
    value recorded in its N13 manifest.
  - Files: `data/sts_n13_D94.parquet`, `data/sts_n13_C30.parquet` and the D94/C30 entries of
    `data/sts_n13_gate_{D94,C30}.json`, `condhist`, `budget`, `guarantee`, `crossnet`, `n2`, `mondrian`, `floor`,
    `verdicts`.
  - **If any hash differs,** that network is recomputed under this primary definition instead (the N13 §3 tier-A
    analyses on its N13 dataset, full M2 re-search).
- **ILL: recomputed without trafo 63.** These are the N13 §3 tier-A analyses that list ILL, run on the rebuilt ILL
  with trafo 63's rows removed:
  - gate with full M2 re-search (`scratch/n10_gate_illinois.py` procedure);
  - fixed-budget static at k_B, COND-HIST and GLOBAL-STATIC;
  - the price of a guarantee (N12 Part B);
  - the cross-network row.
- **C24:** per §A.

### Primary verdicts (N13 definitions, word for word)

- **BEATS-STATIC:** per network.
- **SAFER-IL.**
- **GATE-BEATS-CONDHIST:** per network.
  - **Primary: ILL.**
  - Reported: the count of networks (D94, ILL, C30, and C24 if re-admitted) on which the gate wins.

### Sensitivity (pre-specified, reported either way)

- **Networks:** D94, ILL, C30 and C24. C24 is included only if it passes the §A re-check.
- **Data:** every islanding outage is removed from train, cal and test, as if never in the dataset:
  - D94: 9 outages, 13,500 rows;
  - ILL: 72, 108,000;
  - C30: 3, 4,500;
  - C24: 1.
- **Procedure:** the full N13 arm-S procedure: M2 re-search, held-out target selection, outer splits seeds 0-4,
  rule-B accounting.
- **Analyses:**
  - the held-out gate (missed, escalation, speedup A and B);
  - BEATS-STATIC;
  - GATE-BEATS-CONDHIST.
- **Not in the sensitivity run:** N-2, the budget curve, the guarantee and Mondrian.

### ILL GATE-BEATS-CONDHIST: wording fixed in advance

| Outcome | Wording |
|---|---|
| (a) holds in primary and sensitivity | "the gate's advantage over COND-HIST on Illinois holds with and without islanding outages" |
| (b) holds in primary only | "the gate's advantage on Illinois depends on including islanding outages" |
| (c) fails in primary | "on Illinois the gate does not beat COND-HIST once trafo 63 is excluded" |

- In case (c), the cross-network count of networks where the gate wins drops by one.
- Case (c) applies whatever the sensitivity result; the sensitivity result is still reported.

### Descriptive (no verdict)

- Per network (D94, ILL, C30, and C24 if re-admitted), in primary: catch for gate, fixed-budget static and
  COND-HIST, on islanding rows and on non-islanding rows separately.
- The removed trafo-63 rows are not counted.
- Mean ± std over 5 splits.

## C. The two N13 analyses that did not run: dropped from N14

Classified from `scratch/n13_result.md` and the N13 logs.

**1. Classical screen on rebuilt D94. Classification (b): not a mis-specified check.**
- **What happened:** `scripts/run_classical.py` stopped on its own guard: "reconstructed vm0 differs from stored by
  1.58e-03 (tolerance 1e-05)" (`data/sts_n13_classical.json`).
- **Why it isn't (a):** the difference is a real 1.58e-3 pu gap between two operating points, not floating-point
  noise.
  - The classical screen linearizes around its own base solve, which is the pinned solver. The rebuilt inputs
    are the corrected N-0 states.
  - Running it on rebuilt data needs a method change (a corrected base solve), not a tolerance.
- **Decision:** dropped from N14. The classical row in the rebuilt Table 1 is reported as "not run", with no
  old-build row.

**2. D95c gate. Classification (b): failed computation.**
- **What happened:** it crashed in split 4's ridge M2 search inside scikit-learn Ridge (numpy `LinAlgError: SVD did
  not converge`) after splits 0-3 had finished (`scratch/n13_gate_D95c.log`). It was not retried, and no
  `data/sts_n13_gate_D95c.json` was written.
- **Decision:** dropped from N14. The D95c gate is reported from the old build, labelled "old build, uncorrected
  solver", per N13 rule §1 (`data/sts_n11_gate_095bc.json`).
- The rebuilt D95c dataset passed checks 1-6 and stays in the floor replication (`data/sts_n13_floorrep.json`).

## D. Common rules

- **Std:** population std (ddof=0) over 5 splits.
- **Std rule:** a difference counts only if it exceeds the larger of the two stds.
- **Two comparisons, both reported:** the unpaired std-rule verdict, and the paired mean ± std of the per-split
  differences. The pairs are the same outer splits; the splits are drawn by base case, so removing outages does
  not change them.
- **Fixed after hashing:** no new seeds, networks, limits, candidates, bins or tolerances. The §A tolerance and the
  §B exclusion criterion are fixed by this file.
- **Every verdict** is reported either way.
- **Deviations** are logged in `notes/overnight_status.md` and `scratch/n14_result.md`. Any affected verdict is
  marked "with deviation".
- **The N13 results stay reported as registered,** including C24's exclusion and the N13 ILL verdicts.

## E. Replacement

- The N14 primary results replace the N13 ILL and C24 numbers as the paper's numbers, whichever way they move.
  The N13 numbers are reported as "before N14".
- D94 and C30 keep their N13 numbers: they are restated, per §B, provided the hashes match.
- The sensitivity results are reported beside the primary ones and never replace them.
- This is fixed before the run, so which numbers lead cannot be chosen after seeing them.
