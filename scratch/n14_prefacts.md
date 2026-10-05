# N14 pre-facts — read-only checks before drafting the N14 rule

Written by Claude Code on 2026-10-05.
- Read-only: no analysis was run and no model was fit.
- Topology checks used `pandapower.topology` on the base networks. Three single pandapower solves on base
  networks were run only to confirm how disconnected buses are labelled (item 3).
- Every number below comes from the named file or the stated computation; nothing is estimated.

**C24 amendment: NOT blocked** (item 1).

## 1. C24 status: does any rebuilt-C24 analysis result exist?

**No rebuilt-C24 model result exists.**

### Files that mention C24, and what they hold

| File | Content |
|---|---|
| `data/sts_n13_C24.parquet` (+ manifest) | rebuilt C24 dataset (rows only, no model) |
| `data/sts_n13_audit_C24.parquet` (+ manifest) | audit columns of the rebuild |
| `data/sts_n13_build_C24.json` (+ manifest) | build and checks 2-5 (check 3 failed) |
| `data/sts_n13_indep_C24.json` (+ manifest) | check 6 (passed) |
| `data/sts_n13_replaycheck.json` | check 1 (replay exact) |
| `data/sts_n13_old_rejects.json` | §5 count on the ORIGINAL C24 draws: 1,084 / 6,848 would pass |
| `data/sts_n13_verdicts.json` | BEATS-STATIC C24 = "not run"; GATE-BEATS-CONDHIST C24 = "not run" |
| `data/sts_n13_compare.json` | 20 C24 rows, all "rebuilt: not run" (gate vs static, COND-HIST, cross-network) |
| `data/sts_n13_armF.json`, `data/sts_n13_armF_C24.parquet`, `scratch/n13_armF_C24_build.json` | arm F on the ORIGINAL C24 bases with corrected inputs only (see below) |
| `scratch/n13_*.py`, `scratch/n13_decision_rule*.md`, `scratch/n13_result.md` | code and text that name C24 |

### Analysis files with no C24 content

- **Gate:** there is no `data/sts_n13_gate_C24.json`; the gate files that exist are D94, ILL, C30, D95a, D95b.
- **Other analyses:** `data/sts_n13_condhist.json`, `data/sts_n13_crossnet.json` and `data/sts_n13_guarantee.json`
  contain no C24 entry.

### One model result does involve C24: arm F

- `data/sts_n13_armF.json` → `networks.C24` has refits of the existing N11 M2 configs on the **original** C24
  base set (data/netstudy/case24_ieee_rts/dataset.parquet) with corrected N-0 inputs.
- It is a diagnostic on the old bases, not on the rebuilt C24 dataset, so it is not a rebuilt-C24 result.
- **OWNER:** confirm this reading. If arm F counts as a rebuilt-C24 result, the amendment is blocked.

## 2. C24 check 3

### N13 check 3, exact wording (`scratch/n13_decision_rule.md` §2)

> 3. **Label reproduction.** For every base case common to the old and rebuilt builds (same parameters):
>    - its pinned outage minima equal the old stored `min_vm` exactly;
>    - its corrected outage minima equal the old switch-back labels within 1e-9 pu.

### C24 result (`data/sts_n13_build_C24.json` → `checks.check3_label_reproduction`)

- **Scope:** 62 common bases; 2,356 outage rows compared; 2,266 with a converged pinned solve in both builds.
- **Pinned minima vs old stored min_vm:**
  - max |diff| = **1.9539925233402755e-14 pu**;
  - nonzero on 1,062 of 2,266 rows;
  - 0 pinned-status mismatches.
- **Corrected minima vs old N11 switch-back labels:**
  - max |diff| = **0.0** (within 1e-9 pu: **confirmed**);
  - 0 corrected-status mismatches.
- **Cause, verified in N13:**
  - The prescribed N10/N11 corrected solve adds one out-of-service helper sgen per generator before the pinned
    solve.
  - C24 already has 22 sgens, and the extra entries change pandapower's floating-point summation order.
  - Scenario 100000001, line 0: without helpers 0.9302299793844059 (= stored); with helpers 0.9302299793844045.
- **N11 had the same effect:** its C24 relabel recorded `resolve_min_vm_exact = False`, max 1.03e-13
  (`data/sts_n11_relabel_case24_ieee_rts.json`).

## 3. Islanding in N13: how islanding outages were labelled

- **Mechanism.** N13 labels come from `generate_dataset.make_row`: `min_vm = np.nanmin(res_bus.vm_pu)` after the
  corrected solve.
  - pandapower `runpp` runs with `check_connectivity=True` (its default).
  - Buses not connected to the ext_grid (reference) bus are left out of the power flow and get NaN voltages,
    even if their island contains generators: a `gen` is not a slack.
- **Which buses enter min_vm:** only the buses in the island that contains the reference bus.
- **Disconnected buses:** NaN, excluded from the minimum. Their lost load and generation are not counted
  anywhere; the slack absorbs the imbalance.
- **Dropped rows:** none. Every islanding outage row is `converged = True` in every rebuilt dataset, so it stays
  in every loader.
- **Confirmed by one solve each** (base networks, pinned solver):

| Network, outage | Buses with a result | NaN buses | min_vm |
|---|---|---|---|
| ILL trafo 63 | 1 | 199 | 1.04 |
| ILL line 0 | 199 | 1 | 0.8626 |
| case118 line 6 | 116 | 2 | 0.9357 |

### Counts per rebuilt dataset

Topology is scenario-independent: every branch is in service in every base, and the scenario generator outage
does not change connectivity.

| Dataset | Islanding outages (of all branches) | Islanding rows | Share of converged outage rows | Violation rate among islanding rows |
|---|---|---|---|---|
| D94 (case118) | 9 of 186 | 13,500 of 279,000, all converged | 4.84% | 23.00% |
| ILL (case_illinois200) | 72 of 245 | 108,000 of 367,500, all converged | **29.98%** | 12.71% |
| C30 (case30) | 3 of 41 | 4,500 of 61,500, all converged | 7.32% | 2.38% |

### Outages per network

- **case118:**
  - line 6 and line 121 cut off 2 buses each;
  - lines 7, 103, 163, 164, 170 and trafos 11, 12 cut off 1 bus each;
  - 8 of the 9 cut off a generator bus.
- **case_illinois200:**
  - 71 outages cut off exactly 1 bus each: lines 0, 4, 7, 10, 14, 19, 20, 26-30, 33, 34, 37, 40, 43, 46, 47, 50, 53,
    54, 57 and trafos 2-6, 8-19, 22-25, 28, 29, 31, 32, 36-38, 41-43, 45-49, 51-58, 60, 61, 64, 65;
  - trafo 63 cuts off 199 buses (item 4).
- **case30:** lines 12, 15, 33 cut off 1 bus each.
- **case24_ieee_rts** (C24, excluded; for completeness): line 9 cuts off 1 bus.
- **N2R (case118 N-2 pairs):** 1,687 of 16,990 unique pairs island at least one bus. None leaves the reference
  island with fewer than half the buses.

## 4. trafo 63 on ILL

| Fact | Value |
|---|---|
| Reference (ext_grid) bus | bus 188 (0-based; IEEE-style name 189 if 1-based naming is used) |
| Island sizes after the outage | the reference bus's island has **1 bus** (bus 188 alone); the other island has **199 buses** with all **37 generators** |
| Where the reference bus ends up | isolated, connected only to the ext_grid |
| Label | min_vm = 1.04 pu (the slack setpoint) in every row, "safe" |
| Rows | 1,500 in the rebuilt ILL (all converged); 1,500 in the old ILL |
| Effect of the label | the 199-bus island, i.e. the whole network, is outside the label |

## 5. Which outages meet the candidate exclusion criterion (Part 2 §B)

- **Criterion used for the check:** the outage leaves the reference bus's island with fewer than half of the
  network's buses.
- **Result: trafo 63 on ILL only.**
  - It leaves 1 / 200 buses.
  - Every other islanding outage on case118, case_illinois200, case30 and case24_ieee_rts leaves at least
    116 / 118, 199 / 200, 29 / 30 and 23 / 24.
  - No N2R pair meets it.
- **The gap between the two groups is wide.** trafo 63 leaves 1 bus. Every other outage leaves at least 95.8% of
  the buses (the smallest is case24 line 9, 23 / 24; case30's are 29 / 30 = 96.7%). So any threshold from 2 buses
  up to 95.8% of the network gives the same result.
- The draft states "fewer than half". **OWNER** to confirm the wording.
