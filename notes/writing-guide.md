# writing-guide.md

Specification for writing `report/paper_current_STS.tex`. **This file contains no manuscript
prose.** Every entry states what must be true, the numbers that must appear with their
provenance, the citations, the figure or table dependency, and the insertion point. The
sentences are the author's.

**Git HEAD at read time (every number below): `ab970c19bd9210a2a2c00b1ff21fe9e8d8488051`.** HEAD moved during the session that
built this file: earlier entries in `notes/ai-prompt-log.md` record `03e1136`, and the owner
has since committed `bca6f88` and `ab970c1`. Every number here was read at `ab970c1`.

**Number rule applied.** Every number was re-read from its artifact in this session and
carries source file, jsonpath or column, aggregation, and the artifact's `sha256`.
`notes/writing-numbers.md` was used as an index, not as a source: each row used was
re-derived from the artifact it names. Section 0.2 reports the one row that no longer
reconciles.

**Prompt truncation.** The instruction that produced this file was cut at the PART 2, PART 3,
PART 5 and PART 7 headers. The bullet lists under each survived and the intent was
recoverable; the reconstruction used is: PART 2 = claim-by-claim audit of the named list,
PART 3 = new-section specifications A-J, PART 5 = errata with file:line and affected version,
PART 7 = an independent verifier pass reproduced verbatim. Nothing was invented to fill a gap.

**REVISION 2026-08-23 — REBUILT TO A ~1,000-WORD BUDGET.** PART 3 now carries four sections, not
ten. Six moved to **PART 9, CUT FOR BUDGET**, with their specifications and provenance tables
intact. PART 6.1 and 6.2 are rebuilt: **6.2's page figures now derive from a measured
345 words/page**, replacing the ~378 w/p the old budget implied. PARTS 0, 1, 2, 4, 5, 7 and 8 are
UNCHANGED from the 2026-08-20 revision. The header's prohibition below still stands: this file
contains no manuscript prose.

**Page counts in this file are UNVERIFIABLE.** No TeX toolchain exists in the environment that
produced them. The 12-page anchor is the owner's count; every derived page figure inherits that
limitation and is a planning number, not a compile result.

**Retired inputs.** `notes/writing-background.md` and `notes/section-V-writing-context.md` were
NOT read. Both are absent from the repository.

---

## 0. PROVENANCE

### 0.1 Artifacts read, with content_sha256

| artifact | sha256 |
|---|---|
| `data/barrier_height.json` | `468e30b2c9d7614bf72f878c648306d892ee0685c4de4618418430414107daa0` |
| `data/barrier_height_long.parquet` | `b9e9b4040c8c56e7b281f1b072e2a6c43b7def0adee07451311f8fe7d71eb47e` |
| `data/baselines.json` | `2a6f005cec8914fe0f7c847ce0e53fcc7eebb858aa0eb7579d18087c418e22b6` |
| `data/break_even.json` | `0d4266967a611d2adc7547fab1edf0eefceb91ef2633c6336fc12362c9a6ce3f` |
| `data/case30_frozen.json` | `d501f99671b40a78603ccf21a1a26226f2cac351c7146076e1b510ad17aecf3f` |
| `data/case30_thermal/case30_thermal_frozen.json` | `b340af22662fdd29dce66e4b74841ad4f7ae41155a1b5addef975198ced48897` |
| `data/case30_thermal/h2_range_sweep.json` | `dd98d69da1be19374a88a169047135a60556fd6d9344d9b8595b6434d1e86e56` |
| `data/case30_thermal/h3_build_stats.json` | `f2d3717c163ff9641fe1fcb6afd3ecc1b7cdcf93c9af07013eb1104bbd37f256` |
| `data/dataset.parquet` | `8f0fd1081c8603e805e07a776e9f8e70392795203751fbd915d46ea4e49c1b8e` |
| `data/drift_element_type_long.parquet` | `58bd35de57f96c58df0fdcf8edae28daf4da20a73c60a502d90dcbe83335f75d` |
| `data/drift_loading_tilt_long.parquet` | `3c744f658e5a3973d8b073aeacf15381edb75f8735be96f07458625861f5404b` |
| `data/drift_n0_stratum_long.parquet` | `97c8ef7aa40c4e9728a472c286cc81069fce42ea498983d7c86e50e97e5cc3d3` |
| `data/escalation_at_095.json` | `64ed35d02657c1bb55fd37d13599d16a0019fe72f8058070a04d3c3bc5e6f10a` |
| `data/f1_leakage_audit.json` | `86698fa6ddb16164b70440ab0878c47da20a05afab8ae78d9d270e02b91cc7bf` |
| `data/flag_confusion_long.parquet` | `2ef84483e67518dab73e5ea5864e7c1e944f929b7b07d996358c65f5b0c9687f` |
| `data/frozen_poster_numbers.json` | `a4205c3eaf7096e27d652e4502eb2906483b797dfdc1a905fb4568709c641eb7` |
| `data/netstudy/case57/nofeasible_diagnostic.json` | `930f4ff81668afaafc5e3311a47f19f21be224dfe896618474c5aeb99348ab1b` |
| `data/netstudy2/case24_ieee_rts/comparison.json` | `116483aadbea62781857e46c2375f40c10057053e24efa957de925dced670b93` |
| `data/netstudy2/case24_ieee_rts/cross_2b_comparison.json` | `cae985d53f3d0278ed0f6fabafe5174d3369bc17e111ffeafa1a0d183e4ae64e` |
| `data/netstudy2/case39/comparison.json` | `e40fc3aa577fbf174ac3277e65b29bd535d58c5b164ef0f06a49d35cdc7e7f61` |
| `data/netstudy2/case39/cross_2b_comparison.json` | `06382885d8e913af92c51f71cb2930baaf3eb718d36684e54cb71da0f4264f4d` |
| `data/netstudy2/case89pegase_nofeasible_diagnostic.json` | `aa91609d83686501a3fec912f6ed62d3d753dcb4b5d64a15dde1b5e66f559c9d` |
| `data/netstudy2/case_illinois200/comparison.json` | `1f17800d52863f792bdfdbafb053e2f412f448867b383c7ff02089d7a730f1b5` |
| `data/netstudy2/case_illinois200/cross_2b_comparison.json` | `e3d7179aa0c974da97a7a8725ff307200dc2a2c826a6dac69827ddad618bbaf7` |
| `data/netstudy2/run_status.json` | `756bf0fa45e02476b28afa06899b463d820e377d658f5cc5b1f7e6653afe698e` |
| `data/netstudy2/summary.json` | `19766d5040cec8db72a2e80626a50549c2f03d853e1a723d1488f7f6316c6038` |
| `data/network_triage.json` | `61b34d19b1909b4c5b13884685b0b9d52eff47073e3de750f4ec5dbda398cfbc` |
| `data/nonconverged_gate.json` | `17b42095584c94a0fbbc3e4c3c267eacacf8798e93eccd0491664c8baf2f3f1a` |
| `data/parallel_speedup.json` | `fd2ecbdb8f16a7af809be4e74eeec2c26d61450075532c1910cbaeb1d27162e1` |
| `data/physics_ablation.json` | `ebe57a48ecbfd74b96dbcd029c5a9199fb0eee7361b8e48845a82ce204f4aae6` |
| `data/physics_conclusion.json` | `d6e21ce26bedf4b03e981c44ce2e04557ccede59ef8567fe0f75e17286bc5268` |
| `data/physics_features.json` | `0a1ec40697d6b1d1b45dffe910d97c2d81bee6d7f1a3236a93466656ac142d3b` |
| `data/qlimit_class.json` | `3c0149754f0eefdbd55095cce5fbe71aa1d7f1b1cb0db1a998e72beb8b36f610` |
| `data/sampling_audit.json` | `f077ceb0678a4cb3586c8a694756878048d319c5f31e5ff1ed085ea4e6b922e7` |
| `data/solve_time.json` | `94d8e8059d2b35260da090e33e3ce058c0437ef7b578556a134bbdc258a0d4ec` |
| `data/thermal_check.json` | `cbeadaa2d61d90549523a2cde27b7ee468598e719031dd892f80df76dcb4c000` |
| `data/tradeoff_curve.json` | `36274416190296fdac862c97550ffc0ad34c15baaf0abdf11859faa80c99b062` |
| `data/tradeoff_curve_v2.json` | `a40a079733ecdfcd70191b749571d73cb1a7c870595da635c848b2c68fad8dbd` |
| `data/tuned_metrics.json` | `360a9ec768152afe634ef1f92dd44c72b64a185f89e4f480a09dcd777e4cbf83` |

### 0.2 `notes/writing-numbers.md` reconciliation

83 provenance rows name a `data/` source. All 83 sources exist. **82 of 83 carry a stored
`sha256(16)` that still matches the artifact.**

**ONE ROW DOES NOT RECONCILE, and it is the row that file already flags as superseded:**

| row | stored sha16 | current sha16 | status |
|---|---|---|---|
| `case30-published N-1 loading >100%` (row 51), source `data/thermal_check.json` | `23d42c7146e0f580` | `cbeadaa2d61d9054` | **SUPERSEDED** |

The stored value `1.0` was a 120-scenario prefix under a positional bus mapping. The artifact
was re-emitted as a full 61,500-contingency sweep after `scripts/thermal_check.py:159-160` was
fixed. Use the corrected value in section 0.3, never the stored row.

### 0.3 The corrected replacement for row 51

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| case30-published share of N-1 above 100% loading | `0.9989105691056911` | `data/thermal_check.json` | `networks.case30.thermal_sweep.line_loading.share_above_100` | raw full sweep 61500 | `cbeadaa2d61d9054` |
---

## PART 1 — STATE OF THE MANUSCRIPT

### 1.1 Anchor

| field | value |
|---|---|
| file | `report/paper_current_STS.tex` |
| sha256 | `754be12b5f025c8e271a130e2f8548163251732c7e94e05283799278ee421c22` |
| line count | 344 |
| git HEAD at read time | `ab970c19bd9210a2a2c00b1ff21fe9e8d8488051` |
| last commit touching this file | `6082204` |
| working tree | clean for this file; `git diff HEAD` empty |

**Re-anchor after any edit. Every line number below is a position in this sha, not an identity.**

### 1.2 Section tree with line numbers and labels

| lines | element | `\label{}` |
|---|---|---|
| 79-87 | `\section{Introduction}` | `sec:intro` (80) |
| 89-97 | `\section{Background}` | `sec:background` (90) |
| 99-141 | `\section{Method}` | `sec:method` (100) |
| 102-104 | `\subsection{Dataset}` | **none** |
| 106-108 | `\subsection{Surrogates}` | **none** |
| 110-116 | `\subsection{One-sided conformal band}` | **none** |
| 118-141 | `\subsection{Three-way gate}` | **none** |
| 136-141 | `Fig. 1 float `data/gate_schematic_v2.png`` | `fig:gate` (140) |
| 144-250 | `\section{Results}` | `sec:results` (145) |
| 154-169 | `Table I float` | `tab:models` (157) |
| 176-200 | `Table II float` | `tab:ops` (179) |
| 206-211 | `Fig. 2 float `data/tradeoff_hero_col_v2.png`` | `fig:tradeoff` (210) |
| 213-215 | `\subsection{Safety comes at high escalation}` | **none** |
| 222-227 | `Fig. 3 float `data/miss_depth_v2.png`` | `fig:missdepth` (226) |
| 229-231 | `\subsection{The faster model is not the safer one}` | **none** |
| 233-250 | `\subsection{The boundary layer sets a floor on escalation}` | **none** |
| 241-246 | `Fig. 4 float `data/boundary_mass_hist.png`` | `fig:boundary` (245) |
| 253-262 | `\section{Discussion and limitations}` | `sec:discussion` (254) |
| 265-268 | `\section{Conclusion and future work}` | `sec:conclusion` (266) |
| 285-287 | `\section*{Acknowledgments}` | **none** |
| 303-343 | ``thebibliography{19}`, 19 `\bibitem`s` | n/a |

**Twelve `\label{}`s exist. ZERO are on a subsection.** Consequence in PART 2, item 15.

### 1.3 Classification of every existing section

| section | verdict | reason | evidence line |
|---|---|---|---|
| I Introduction, 82-84 | **REVISE** | asymmetry framing is sound and the escalation-cost sentence is correct; the section inherits the abstract's sub-1% claim, which fails at one sigma | `:72` vs Table II `:186`, `:196` |
| I, paragraph at 86 | **REPLACE** | this is a compressed related-work paragraph carrying four precedents inside the Introduction; it becomes its own section (PART 3-D) and must be removed from here | `:86` |
| II Background, 92 | **REVISE** | asserts the lower voltage limit is the only active constraint; over-voltage is not inert on this dataset | `:92` vs `data/thermal_check.json` |
| II Background, 94-96 | **KEEP AS IS** | solver description, network counts and the 186 branch count all reconcile | `:96` vs `data/dataset.parquet` |
| III-A Dataset, 104 | **REPLACE** | three independent defects in one sentence: generator scaling, multiplier range, and the non-convergence count | `:104`, errata E-1/E-2/E-3 |
| III-B Surrogates, 106-108 | **KEEP AS IS** | feature description matches the committed design matrix | `:108` vs `make_splits.EXCLUDE_COLS` |
| III-C One-sided conformal band, 110-116 | **KEEP AS IS** | band construction and the single live cross-reference are correct | `:116` |
| III-D Three-way gate, 118-135 | **KEEP AS IS** | gate definition and `t_solve` reconcile | `:131` vs `data/solve_time.json` |
| Fig. 1 float, 136-141 | **REVISE** | embeds the M1-sized schematic; an M2-consistent file exists and is unreferenced | `:138`, erratum E-9 |
| IV preamble + Table I, 147-169 | **KEEP AS IS** | all four model rows reconcile against the promoted M2 artifacts | `:163-166` vs `data/tuned_metrics.json` |
| Table II, 176-200 | **KEEP AS IS** | all twelve rows reconcile | `:185-197` vs `data/tradeoff_curve_v2.json` |
| IV-1 Safety comes at high escalation, 213-215 | **REVISE** | states a sub-1% missed rate first occurs at 0.94; the error bar crosses 1% | `:215` vs `:186` |
| IV-2 The faster model is not the safer one, 229-231 | **REVISE** | the title and its supporting sentence assert a model-safety ordering that does not hold on all three result sets | `:229`, `:231`, erratum E-5 |
| IV-3 The boundary layer sets a floor, 233-250 | **REVISE** | numbers reconcile including the 14% bin share, but the subsection is the natural host for the flag-branch and non-convergence material | `:235` |
| V Discussion, 256 | **REVISE** | cascade and reject-option framing is sound; break-even is asserted without the amortisation threshold | `:256` |
| V Discussion, 258 | **REVISE** | the 186-per-scenario coverage caveat is correct and should be kept; drift evidence is absent | `:258` |
| V Discussion, 260 | **REPLACE** | carries four case30-PUBLISHED figures that are superseded by the thermally feasible regeneration, plus a network-general floor claim and the ANSI provenance defect | `:260`, errata E-7, E-11, E-14 |
| V Discussion, 262 | **REVISE** | asserts no N-2 cases were tested; a quarter of converged N-1 rows carry a simultaneous generator outage | `:262`, erratum E-4 |
| VI Conclusion, 268 | **REVISE** | 'safe on every case' overstates what a 90%-coverage band supports | `:268` |
| Acknowledgments, 287 | **REVISE** | provenance sentence and the repository URL do not match the remote's state | `:287`, erratum E-12 |
| Bibliography, 303-343 | **REVISE** | 19 entries resolve; `nerc` has no entry in `notes/prior-art.md` and the `.tex` comment says so itself | `:299-300`, erratum E-8 |

**Nothing is classified DELETE.** Every existing section carries at least one claim that
survives; the weakest, `:260`, is REPLACE rather than DELETE because its ANSI and
distribution-dependence points must be restated, not dropped.
---

## PART 2 — CLAIM-BY-CLAIM AUDIT

Each item: the claim as it stands, the artifact verdict, and what the guide requires.

### 2.1 III-A sampling: generator scaling, multiplier range, `--mode mixed`, non-convergence

**Claim at `:104`:** load AND generator base values are multiplied by 1.0-1.12; the remainder failed to converge.

**Verdict: FALSE on three counts.**

1. `net.gen.p_mw` is never assigned. `feasibility/generate_dataset.py:136-144` assigns six
   fields; `gen.p_mw` is not among them. It is read only at `:57` and `:168`. All 53
   `genp_*` columns have `nunique == 1` and `std == 0`.
2. The 1.0-1.12 window holds only for per-bus load P in independent mode. Measured support:

| mode | P range | P share outside [1.0,1.12] | Q range | Q share outside |
|---|---|---|---|---|
| independent (750 bases) | [1.0000, 1.1200] | 0.00% | [0.9009, 1.2876] | 54.54% |
| regional (750 bases) | [0.9009, 1.2310] | 43.91% | [0.8156, 1.4083] | 59.13% |
| all (1,500 bases) | [0.9009, 1.2310] | 21.95% | [0.8156, 1.4083] | 56.83% |

Re-derived this session from `data/dataset.parquet` by dividing `pload_i`/`qload_i` by the
per-bus case118 base load. **These columns are PER BUS, not per load** (`generate_dataset.py:160-162` accumulates
`pbus`/`qbus` per bus; `:164-165` writes them as `pload_i`/`qload_i`); case118 has at most one load per bus so the map is unique. Cause:
`REG_JITTER = 0.10` at `:21`, applied at `:111`.

3. The non-convergence count is not the remainder.

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| total rows | `280500` | `data/dataset.parquet` | `num_rows` | count | `8f0fd1081c8603e8` |
| N-0 base rows | `1500` | `data/dataset.parquet` | `outaged_type=='none'` | count | `8f0fd1081c8603e8` |
| N-1 attempted | `279000` | `data/dataset.parquet` | `outaged_type!='none'` | count | `8f0fd1081c8603e8` |
| N-1 converged | `278955` | `data/dataset.parquet` | `outaged_type!='none' & converged` | count | `8f0fd1081c8603e8` |
| genuine solver failures | `45` | `data/dataset.parquet` | `~converged` | count | `8f0fd1081c8603e8` |

1,545 = 1,500 base rows (all converged, excluded because they are base cases) + 45 failures.

**REQUIRED:** state per-load P and Q support separately by mode, name the denominator for
every share, state that generator real power is never scaled, and give 45 as the failure count.

### 2.2 Line 262's N-2 claim

**Claim at `:262`:** safety claims hold for N-1 only, because N-2 cases were not tested.

**Verdict: FALSE.** A quarter of converged N-1 rows are two-element states.

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| share of converged N-1 rows with a simultaneous generator outage | `0.24925884103170762` | `data/sampling_audit.json` | `prevalence.share_of_n1_converged_rows` | raw | `f077ceb0678a4cb3` |
| count of such rows | `69532` | `data/sampling_audit.json` | `prevalence.n_n1_rows_with_generator_outage` | count | `f077ceb0678a4cb3` |
| same share, re-derived from the parquet | `0.24925884103170762` | `data/dataset.parquet` | `gen_out>=0 ; converged N-1` | raw | `8f0fd1081c8603e8` |

`P_GEN_OUT = 0.30` at `generate_dataset.py:28`, drawn at `:128`, non-slack generators only.
**REQUIRED:** the limitation must be restated as untested N-2 BRANCH pairs, not untested N-2.

### 2.3 IV-B's title and supporting claim across all three result sets

**Claim at `:229`, `:231`:** the faster model is not the safer one; the linear model has the
lower missed rate across all targets.

**Verdict: HOLDS on case118 ONLY. Absent on case30-published, INVERTED on case30-thermal.**

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| case30-published ridge missed @0.90 | `0.014931446336352586` | `data/case30_frozen.json` | `...missed_viol_mean` | seed-mean | `d501f99671b40a78` |
| case30-published histgb missed @0.90 | `0.014664013437545673` | `data/case30_frozen.json` | `...missed_viol_mean` | seed-mean | `d501f99671b40a78` |
| case30-thermal ridge missed @0.90 | `0.060873023867972956` | `data/case30_thermal/case30_thermal_frozen.json` | `...missed_viol_mean` | seed-mean | `b340af22662fdd29` |
| case30-thermal histgb missed @0.90 | `0.022255143446972075` | `data/case30_thermal/case30_thermal_frozen.json` | `...missed_viol_mean` | seed-mean | `b340af22662fdd29` |

On case30-published the two are 0.03 pp apart, inside one sigma. On case30-thermal the
ordering reverses: histgb is the safer model. **REQUIRED:** the title must be scoped to
case118 or restated as a coverage-axis claim; the general ordering cannot be written.

### 2.4 Every 'sub-1%' instance and its error bar

**Instances at `:72` (abstract), `:209` (Fig. 2 caption), `:215`, `:250`.**

**Verdict: BOTH quoted crossings fail at one sigma.**

| target | missed % | + std | upper edge | sub-1%? |
|---|---|---|---|---|
| ridge @0.94 (`:186`) | 0.79 | 0.21 | **1.00** | NO |
| histgb @0.97 (`:196`) | 0.83 | 0.24 | **1.07** | NO |
| ridge @0.95 (`:187`) | 0.45 | 0.12 | 0.57 | yes |
| histgb @0.98 (`:197`) | 0.30 | 0.13 | 0.43 | yes |

Read from Table II in the manuscript itself, which reconciles against
`data/tradeoff_curve_v2.json`. The first robustly sub-1% targets change the headline to
67.9%/1.48x (ridge 0.95) and 72.0%/1.39x (histgb 0.98). **REQUIRED:** every sub-1% sentence
must move to 0.95/0.98 or state the crossing as not resolved at five seeds.

### 2.5 III-D `t_solve`

**Claim at `:131`:** 9.14 ms, the minimum over 400 timed solves.

**Verdict: RECONCILES.**

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| ms_solver | `9.14` | `data/solve_time.json` | `ms_solver` | min over 400 timed solves | `94d8e8059d2b3526` |

**REQUIRED:** keep. Note for PART 5 that every `net_speedup` in the case30 and netstudy
artifacts reuses this case118 value without re-timing.

### 2.6 Section I's 'wastes solver time'

**Claim at `:84`:** predicting too high certifies an unsafe condition as safe; predicting too
low just wastes solver time.

**Verdict: CORRECT AND LOAD-BEARING.** It is the asymmetry that justifies a one-sided band.
The following sentence, that escalated solver time is added to the gate's total, also holds:
`feasibility/gate_eval.py:39` computes `net_speedup` with `n_esc * ms_solver` in the denominator.
**REQUIRED:** keep. PART 3-F must state what this accounting does NOT charge.

### 2.7 IV-C's saturation-point claim

**Claim at `:235`:** most contingencies are within 0.005 pu of the boundary; 56.86% in
[0.94, 0.945); 17.48% below; no 0.001-pu bin exceeds around 14%.

**Verdict: ALL THREE RECONCILE, including the 14% figure.**

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| boundary mass [0.94,0.945) | `0.5686293488197021` | `data/dataset.parquet` | `0.94<=min_vm<0.945` | raw | `8f0fd1081c8603e8` |
| violation rate | `0.174755784983241` | `data/dataset.parquet` | `min_vm<0.94 ; converged N-1` | raw | `8f0fd1081c8603e8` |
| largest 0.001-pu-wide bin share | `0.1406284167697299` | `data/dataset.parquet` | `0.001-pu histogram of min_vm ; converged N-1` | raw | `8f0fd1081c8603e8` |
| weakest bus | `{'bus0': 75, 'bus_ieee': 76, 'share': 0.2709612661540392}` | `data/dataset.parquet` | `argmin_bus` | raw | `8f0fd1081c8603e8` |
| second | `{'bus0': 52, 'bus_ieee': 53, 'share': 0.16808445806671327}` | `data/dataset.parquet` | `argmin_bus` | raw | `8f0fd1081c8603e8` |
| third | `{'bus0': 106, 'bus_ieee': 107, 'share': 0.09307952895628327}` | `data/dataset.parquet` | `argmin_bus` | raw | `8f0fd1081c8603e8` |

The 14% share was previously labelled NO SOURCE. **That label was wrong** and is withdrawn:
it re-derives exactly from `data/dataset.parquet`. Bus indices are 0-based in the artifact;
the manuscript's 76/53/107 are the IEEE names. **REQUIRED:** add a `writing-numbers.md` row
for the bin share before it is defended.

### 2.8 Conclusion's 'must be safe on every case' and V's 'floor exists on any network'

**Claims at `:268` and `:260`.**

**Verdict: BOTH OVERCLAIM, for different reasons.**

`safe on every case` — the gate provides a MARGINAL coverage guarantee at a target rate, not
a per-contingency one. The manuscript states this correctly at `:258` and then contradicts it
at `:268`. `data/baselines.json` `gate_definition` records the same asymmetry.

`the floor exists on any network` — a network-general claim from, now, five networks, two of
which could not be built at all. It is barred by CLAUDE.md section 8.

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| case30-thermal boundary mass % | `7.0862` | `data/case30_thermal/case30_thermal_frozen.json` | `boundary_mass_pct` | raw | `b340af22662fdd29` |
| case118 boundary mass % | `56.86` | `data/frozen_poster_numbers.json` | `dataset_facts.boundary_0p94_to_0p945_pct` | raw | `a4205c3eaf7096e2` |

**REQUIRED:** restate as a mechanism that is measurable per network, with its measured range
across the networks actually built, and drop 'any network' and 'every case'.

### 2.9 The ANSI 0.917 provenance

**Claim at `:260`:** ANSI C84.1 Range B allows service voltages down to 0.917 pu.

**Verdict: NOT PRIMARY-SOURCE VERIFIED.** `notes/prior-art.md` section 7.3 states the
bibliographic identity is confirmed from NEMA's free front matter, which contains no numeric
table, and that 0.917 comes from a utility document and an UNAPPROVED 2016 working draft. The
same section records that Range B's utilization-voltage extent is 0.867 pu, not 0.917.
**REQUIRED:** either specify 'service' explicitly and cite what was actually read, or drop the
number. Do not cite the approved standard for a figure not read from it.

### 2.10 The '186 related contingencies' claim

**Claim at `:258`:** every base case generates 186 related contingencies, so coverage is a
measured average rather than a per-contingency guarantee.

**Verdict: THE COUNT IS RIGHT AND THE INFERENCE IS RIGHT.** 173 lines + 13 transformers
= 186, confirmed at `:96`. Per-scenario RAW N-1 row counts are 186 for all 1,500 scenarios; it is the CONVERGED-only
counts that run 185-186, on exactly 45 scenarios. `data/baselines.json` `dataset_facts`
records 185/186 and states its filter explicitly. **The filter must be stated whenever the
185 appears.**

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| N-1 attempted = 1,500 x 186 | `279000` | `data/dataset.parquet` | `outaged_type!='none'` | count | `8f0fd1081c8603e8` |

**REQUIRED:** keep. It is one of the few places the manuscript scopes its own guarantee
correctly, and PART 3-A depends on it.
### 2.11 Voice: the abstract's first person against the body and Acknowledgments

**Verdict: TWO VOICE FAMILIES IN ONE DOCUMENT.** Counted this session over lines 60-290,
comment lines excluded, case-sensitive:

| token | count |
|---|---|
| `we` | 17 |
| `our` | 5 |
| `us` | 1 |
| `the authors` | 1, at `:287` |
| `I` / `my` | **0** outside LaTeX comments (3 comment lines at `:19`, `:23`, `:150`) |

The body is first-person plural throughout; the Acknowledgments switch to third person.
**REQUIRED:** pick one and apply it to `:287`. This interacts with the STS individual-work
rule and is the author's call, not a mechanical fix.

### 2.12 The Acknowledgments provenance sentence against the remote's actual state

**Claim at `:287`:** every number came from committed, tested code at
`github.com/rajsaha-blip/contingency-screener-research`.

**Verdict: THE URL POINTS AT THE STALE REMOTE.** Measured this session:

| ref | commit |
|---|---|
| local HEAD | `ab970c19bd9210a2a2c00b1ff21fe9e8d8488051` |
| `origin` (`RS499/...`) | `ab970c19bd9210a2a2c00b1ff21fe9e8d8488051` |
| `upstream` (`rajsaha-blip/...`, the cited URL) | `990c3c5dea24f7d63b1b21ccb4a99281a6765f18` |

`origin` has caught up to local during this session; the CITED remote has not. Separately,
`notes/` is git-ignored (`.gitignore:23`), so no note, log or prereg named in the guide is
reachable from that URL at all. **REQUIRED:** correct the URL or the claim. The `.tex`
comment at `:279-283` already flags that STS judges do not follow links.

### 2.13 Fig. 1's schematic version

**Claim at `:138`:** `\includegraphics{data/gate_schematic_v2.png}`.

**Verdict: M1-SIZED FIGURE IN AN M2 PAPER.**

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| M1 histgb q_hat at 0.90 (the width v2 was drawn from) | `0.002557109746803765` | `data/tradeoff_curve.json` | `records[model=histgb,target=0.90].q_hat` | seed-mean | `36274416190296fd` |
| M2 histgb q_hat at 0.90 (the width the results use) | `0.002290702766310826` | `data/tradeoff_curve_v2.json` | `records[model=histgb,target=0.90].q_hat` | seed-mean | `a40a079733ecdfcd` |

The strip is about 11.6% wider than the band the results use. `data/gate_schematic_v3.png` is
the M2-consistent file and nothing references it. `notes/erratum.md` E1 already records this.
**REQUIRED:** repoint the figure or state the discrepancy in the caption.

### 2.14 `nerc`'s absence from `notes/prior-art.md`

**Verdict: CONFIRMED ABSENT.** `grep -ni 'nerc\|TPL-001' notes/prior-art.md` returns zero
hits. The bibitem exists at `:305`; the `.tex` comment at `:299-300` says so itself and ends
`ADD THE VERIFICATION DATE HERE, every other entry has one`.
**REQUIRED:** resolve `nerc` into `notes/prior-art.md` with a fetch date, or cite NERC only
for what a reader can check without it.

### 2.15 Absent subsection labels and what `\thesubsection` actually renders

**Verdict: ZERO subsections carry a label, and three source comments name a scheme the
document cannot print.**

`\documentclass[12pt]{article}` at `:25`; `\renewcommand{\thesection}{\Roman{section}}` at
`:50`; **`\thesubsection` is never redefined**, so it renders `\thesection.\arabic{subsection}`
- `IV.1`, `IV.2`, `IV.3` - never `IV-B`. Comments at `:134` (`Cited in III-D`), `:220`
(`Cited in IV-B`) and `:239` (`Cited in IV-C`) name IEEEtran-style ids.

**REQUIRED:** add `\label{}` to every subsection before any new section cross-references one,
and fix the three comments. They do not typeset, so this is hygiene, not a printed defect.
---
## PART 3 — NEW SECTIONS (ACTIVE SET)

**Five sections are active. Five are cut to PART 9.** 3.J was restored 2026-08-24. Every length below is
stated in WORDS first and converted at the measured **345 words/page** derived in 6.2. No
section here adds a float.

### 3.0 Insertion points, collision-checked

Five of the original ten. The five cut insertion points are released; **no collision remains and
the renumbering consequence disappears** — 3.D was the only section that would have inserted a
new numbered section ahead of Background, and at 150 words prose-only it is now specified as a
subsection of the existing Introduction rather than a new `\section`.

| sec | content | insertion | follows the line ending |
|---|---|---|---|
| H | Discussion: case30-thermal (REPLACES 260) | replaces 260 in place | n/a - in-place replacement |
| A | Theory: escalation identity and barrier inequality | after 141 | `\end{figure}` (Fig. 1 float) |
| I | Results: cross-network out-of-sample test | after 250 | ...instead of the 2 to 3 times available at 0.90. |
| J | Discussion: physics-features ablation | after 262 | ...as seasons and demand change throughout the year. |
| D | Related Work paragraph, IN PLACE at 86 | rewrites 86 | n/a - in-place replacement |

**RENUMBERING: NONE.** With 3.D demoted to an in-place rewrite of `:86` and 3.E cut, no new
`\section` is added anywhere. Background stays III, Method IV, Results VI, Discussion VII.
`\ref{sec:discussion}` at `:116` is unaffected. **PART 2 item 15's three stale comments still
need fixing by hand** — that is a comment defect, not a numbering one, and it survives the cut.

**3.A adds `\label{sec:theory}` as a SUBSECTION of the existing Method section, not a new
top-level section.** At 300 words it does not carry a `\section`.

### 3.H Discussion — case30-thermal replacing case30-published (REPLACES 260 **AND 72**) — **~200 words**

**Insertion:** replaces `:260` in place. **No new float.**

**SCOPE EXTENDED 2026-08-27 TO `:72`, THE ABSTRACT. This was a gap, not a choice.** Confirmed by
grep: `20.0\%`, `8.96` and `11.27` occur at **exactly two lines, `:72` and `:260`**. 3.H
previously covered `:260` only, so the abstract would have kept the superseded case30-**published**
figures after the discussion sentence was corrected — **the first thing three Ph.D. scorers read,
left quoting a dataset this project has itself retired as thermally infeasible.**

**Replacement specification, per result set. No number is written here; each is named by the row
that already carries it.**

| what `:72` currently asserts | result set it came from | replace with | source row |
|---|---|---|---|
| share of contingencies "near the limit" on the 30-bus network | **case30-PUBLISHED**, superseded | the case30-**THERMAL** boundary mass | `data/case30_thermal/case30_thermal_frozen.json` `boundary_mass_pct`, already tabulated in this section |
| the 118-bus comparison share | case118, **correct as is** | unchanged | `data/frozen_poster_numbers.json` `dataset_facts.boundary_0p94_to_0p945_pct` |
| the escalation figure at a sub-1% missed rate | **case30-PUBLISHED**, superseded | the `esc_mean`/`esc_std` pair at the **DECIDABLE** target 0.97 | `records[family=histgb,coverage_target=0.97]`, the row already in this section's table |
| the speedup figure | **case30-PUBLISHED**, superseded | the `sp_mean`/`sp_std` pair from the same row | same row |

**THE TARGET MUST BE NAMED IN THE ABSTRACT.** `:72` currently attaches its case30 pair to "a
sub-1\% missed rate" with no coverage target. 3.H's standing bar applies verbatim to the abstract:
the crossing is **indeterminate** at five seeds, 0.97 is the first decidable target, and **0.96
must not be quoted as resolved.** An abstract that names the metric without naming the target
reintroduces the defect the body corrects.

**Word cost: ~0 net at `:72`** — substitution, not addition. **This correction is MANDATORY
regardless of budget:** a superseded number in the abstract is a defect, not a length choice.

**"Replaces figures currently WRONG in the .tex" means NUMBERS, not floats.** `:260` currently
quotes the case30-PUBLISHED values `20.0%` boundary and `28.8%` below the limit. Both are
superseded: that dataset is not thermally feasible. No `\begin{figure}` or `\begin{table}` is
added or removed by this section.

**Claim (one sentence):** On a thermally feasible regeneration of the 30-bus network the
boundary mass is an order of magnitude below the 118-bus value and the escalation floor falls
with it, at a coverage target whose location is not resolved at five seeds.

**WHAT SURVIVES AT 200 WORDS — three sentences, in this order:**
1. the two boundary masses, case118 against case30-THERMAL, each naming its result set;
2. the escalation and speedup at the DECIDABLE target 0.97 for histgb, with error bars;
3. one sentence that the crossing location is indeterminate at five seeds.

**WHAT IS DROPPED AT THIS LENGTH, and may not be claimed without it:** the zero-acceptance
sweep, the N-0 acceptance rate, the load-multiplier range, and the case30-published corrected
share above 100% loading. **Consequence: the sentence "the published case30 dataset had to be
regenerated because it is not thermally feasible" LOSES ITS EVIDENCE and must not appear.**
Write the replacement as a statement about case30-thermal only, with no comparative claim about
why the published set was abandoned. The rows stay in the table below so the claim can be
restored if a reviewer asks for it.

**EVERY ROW MUST NAME ITS RESULT SET. The two case30 sets are not interchangeable.**
| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| boundary mass %, case118 | `56.86` | `data/frozen_poster_numbers.json` | `dataset_facts.boundary_0p94_to_0p945_pct` | raw | `a4205c3eaf7096e2` |
| boundary mass %, case30-THERMAL | `7.0862` | `data/case30_thermal/case30_thermal_frozen.json` | `boundary_mass_pct` | raw | `b340af22662fdd29` |
| boundary mass %, case30-PUBLISHED (superseded) | `20.0146` | `data/case30_frozen.json` | `boundary_mass_pct` | raw | `d501f99671b40a78` |
| violation rate %, case118 | `17.48` | `data/frozen_poster_numbers.json` | `dataset_facts.violation_rate_pct` | raw | `a4205c3eaf7096e2` |
| violation rate %, case30-THERMAL | `15.3967` | `data/case30_thermal/case30_thermal_frozen.json` | `violation_rate_pct` | raw | `b340af22662fdd29` |
| violation rate %, case30-PUBLISHED (superseded) | `28.8081` | `data/case30_frozen.json` | `violation_rate_pct` | raw | `d501f99671b40a78` |
| case30-thermal histgb at the DECIDABLE target 0.97 | `{'missed_mean': 0.00759014034053139, 'missed_std': 0.0020082418201518605, 'n_below': 5, 'gap_over_std': 1.1999848002798688, 'esc_mean': 0.05835772357723577, 'esc_std': 0.012504625358797069, 'sp_mean': 17.91395434476741, 'sp_std': 3.709477412003147}` | `data/case30_thermal/case30_thermal_frozen.json` | `records[family=histgb,coverage_target=0.97]` | seed-mean/std ddof=0 | `b340af22662fdd29` |
| case30-thermal histgb at 0.96 — INDETERMINATE | `{'missed_mean': 0.009093532637113735, 'missed_std': 0.0021962920812743196, 'n_below': 2, 'gap_over_std': 0.4127262355562109, 'esc_mean': 0.048617886178861786, 'esc_std': 0.009770044231923439, 'sp_mean': 21.45706393938002, 'sp_std': 4.514886374051058}` | `data/case30_thermal/case30_thermal_frozen.json` | `records[family=histgb,coverage_target=0.96]` | seed-mean/std ddof=0 | `b340af22662fdd29` |
| case30-thermal ridge at 0.97 — INDETERMINATE | `{'missed_mean': 0.010475450381273592, 'missed_std': 0.0022104657593999153, 'n_below': 3, 'gap_over_std': -0.21509058860186275, 'esc_mean': 0.29704065040650407, 'esc_std': 0.017025065795993916, 'sp_mean': 3.377433434234618, 'sp_std': 0.19017596315076635}` | `data/case30_thermal/case30_thermal_frozen.json` | `records[family=ridge,coverage_target=0.97]` | seed-mean/std ddof=0 | `b340af22662fdd29` |
| case30-thermal N-0 acceptance rate | `0.18633540372670807` | `data/case30_thermal/h3_build_stats.json` | `acceptance_rate` | raw | `f2d3717c163ff964` |
| chosen load-multiplier range | `{'lo': 0.87, 'hi': 0.99, 'acc': 0.205}` | `data/case30_thermal/h2_range_sweep.json` | `h2.chosen` | raw | `dd98d69da1be1937` |
| lo values with EXACTLY zero acceptance | `[1.0, 0.99, 0.98, 0.97, 0.96, 0.95, 0.94]` | `data/case30_thermal/h2_range_sweep.json` | `h2.sweep acceptance_rate==0` | raw | `dd98d69da1be1937` |
| case30-thermal share of N-1 above 100% loading | `0.21484552845528454` | `data/case30_thermal/h3_build_stats.json` | `n1_loading.share_above_100` | raw | `f2d3717c163ff964` |
| case30-published share above 100%, corrected full sweep | `0.9989105691056911` | `data/thermal_check.json` | `networks.case30.thermal_sweep.line_loading.share_above_100` | raw full sweep 61500 | `cbeadaa2d61d9054` |
**THE CROSSING LOCATION IS INDETERMINATE AND MUST BE STATED AS SUCH.** histgb at 0.96 sits
0.41 std from the 0.01 threshold with 2 of 5 seeds below it; the first decidable target is
0.97 at 1.20 std with 5 of 5. Ridge is equally indeterminate between 0.97 and 0.98. **Quote
the pair or quote the metric at a fixed coverage target; do not quote 0.96 as resolved.**

**Also at 260 and unrelated to case30:** the ANSI provenance defect (PART 2 item 9) and a
circular justification of the 0.94 floor — 'all sit above 0.94 pu' IS the acceptance criterion
at `feasibility/generate_dataset.py:256`. **Both are line-level corrections and are MANDATORY
regardless of budget.** The ANSI correction is word-neutral: strike the attribution of 0.917 pu
to the approved standard. The circularity correction is word-neutral: strike 'and it also fits
how the pre-outage data is distributed'.

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| base cases above 0.95 pu | `86` | `data/dataset.parquet` | `n0_min_vm>0.95 \| base` | count | `8f0fd1081c8603e8` |
| minimum n0_min_vm over base cases | `0.940000035663552` | `data/dataset.parquet` | `n0_min_vm` | min | `8f0fd1081c8603e8` |
| escalation at a 0.95 pu limit, ridge | `{'mean': 0.01384836867553085, 'std': 0.0032631713264372076}` | `data/escalation_at_095.json` | `per_seed.ridge.0.95` | seed-mean/std ddof=0 | `64ed35d02657c1bb` |
| escalation at a 0.95 pu limit, histgb | `{'mean': 0.01578085711179363, 'std': 0.011903766459957115}` | `data/escalation_at_095.json` | `per_seed.histgb.0.95` | seed-mean/std ddof=0 | `64ed35d02657c1bb` |
**Citations:** none new. `ansi2020` stays cited at `:260` for the standard's identity only, never
for the 0.917 figure — `prior-art.md` 7.3 and 8's scope note.

**Estimate: ~200 words replacing ~190 words. NET +10 words = +0.03 pp at 345 w/p.**

### 3.A Theory — the escalation identity and the barrier inequality — **~300 words, NO FIGURE**

**Insertion:** after 141. **`\label` to add:** `\label{sec:theory}` on a SUBSECTION.
**Cut from ~900 words and one figure. `data/fig_identity.png` is NOT used.**

**Claim (one sentence):** Escalation equals the predictive mass in a band of width `q_hat`
above the limit, so its floor is set by boundary density, and which model is safer depends on
how each model's conditional overshoot sits relative to its own band width.

**THE THREE THINGS THAT MUST SURVIVE, and nothing else:**
1. **The identity.** Escalation = P(L <= pred < L + q_hat). State it as a definition unrolled
   from `feasibility/gate_eval.py:18-20`, in two lines, with no figure.
2. **The barrier inequality.** Certify implies `pred >= L + q_hat`; violation implies `y < L`;
   therefore `overshoot >= q_hat + depth`. Two lines of derivation.
3. **The named statistic.** `S_mean = E[overshoot | Y < L] / q_hat`, named explicitly, with the
   case118 pair and error bars.

**THE SECTION MUST NAME ITS STATISTIC.** The p99 statistic moves the OPPOSITE way for ridge; a
sentence that does not name which statistic it means is contradicted by the other figure in
the same artifact.

**WHAT THE FIGURE CUT COSTS.** `data/fig_identity.png` was to show the identity holding across
the coverage sweep. Without it the identity rests on the derivation plus the measured gap of
`5.55e-17` quoted in one clause. **That is sufficient and the figure was never load-bearing** —
but the manifest's `apa_citation` requirement (R10) disappears with it, closing one open item.

**DROPPED AT THIS LENGTH:** the cross-network S comparison in full. At 300 words state the
case118 pair only. **The per-model direction warning below still binds** — it is the reason the
cross-network comparison is dropped rather than compressed.
| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| ridge S_mean case118 | `0.6037845811435492` | `data/barrier_height.json` | `summary_at_090.case118.ridge.S_mean_over_qhat_at_090_mean` | seed-mean/std ddof=0 | `468e30b2c9d7614b` |
| ridge S_mean std case118 | `0.07568533879876284` | `data/barrier_height.json` | `summary_at_090.case118.ridge.S_mean_over_qhat_at_090_std` | seed-mean/std ddof=0 | `468e30b2c9d7614b` |
| ridge S_mean case30-thermal | `0.7213426623754614` | `data/barrier_height.json` | `summary_at_090.case30_thermal.ridge.S_mean_over_qhat_at_090_mean` | seed-mean/std ddof=0 | `468e30b2c9d7614b` |
| ridge S_mean std case30-thermal | `0.0656438240627924` | `data/barrier_height.json` | `summary_at_090.case30_thermal.ridge.S_mean_over_qhat_at_090_std` | seed-mean/std ddof=0 | `468e30b2c9d7614b` |
| histgb S_mean case118 | `0.7919301552833694` | `data/barrier_height.json` | `summary_at_090.case118.histgb.S_mean_over_qhat_at_090_mean` | seed-mean/std ddof=0 | `468e30b2c9d7614b` |
| histgb S_mean std case118 | `0.07432884539735458` | `data/barrier_height.json` | `summary_at_090.case118.histgb.S_mean_over_qhat_at_090_std` | seed-mean/std ddof=0 | `468e30b2c9d7614b` |
| histgb S_mean case30-thermal | `0.343934685282686` | `data/barrier_height.json` | `summary_at_090.case30_thermal.histgb.S_mean_over_qhat_at_090_mean` | seed-mean/std ddof=0 | `468e30b2c9d7614b` |
| histgb S_mean std case30-thermal | `0.06175223629218416` | `data/barrier_height.json` | `summary_at_090.case30_thermal.histgb.S_mean_over_qhat_at_090_std` | seed-mean/std ddof=0 | `468e30b2c9d7614b` |
| ridge S_p99 case118 | `6.548388859231787` | `data/barrier_height.json` | `summary_at_090.case118.ridge.S_p99_over_qhat_at_090_mean` | seed-mean/std ddof=0 | `468e30b2c9d7614b` |
| ridge S_p99 case30-thermal | `4.390677117862201` | `data/barrier_height.json` | `summary_at_090.case30_thermal.ridge.S_p99_over_qhat_at_090_mean` | seed-mean/std ddof=0 | `468e30b2c9d7614b` |
| histgb S_p99 case118 | `9.774697124191146` | `data/barrier_height.json` | `summary_at_090.case118.histgb.S_p99_over_qhat_at_090_mean` | seed-mean/std ddof=0 | `468e30b2c9d7614b` |
| histgb S_p99 case30-thermal | `5.213064887952486` | `data/barrier_height.json` | `summary_at_090.case30_thermal.histgb.S_p99_over_qhat_at_090_mean` | seed-mean/std ddof=0 | `468e30b2c9d7614b` |
| identity gap \|P(o>q) - (1-cov)\| | `5.551115123125783e-17` | `data/barrier_height.json` | `identity_checks.max_identity_gap` | max | `468e30b2c9d7614b` |
| share of misses satisfying overshoot >= q_hat + depth | `1.0` | `data/barrier_height.json` | `identity_checks.min_share_missed_overshoot_ge_qhat_plus_depth` | min | `468e30b2c9d7614b` |
| rows containing a miss | `173` | `data/barrier_height.json` | `identity_checks.n_rows_with_any_miss` | count | `468e30b2c9d7614b` |
**DIRECTION IS PER MODEL AND UNWRITABLE AS A SINGLE STATEMENT.** ridge S_mean RISES, histgb
S_mean FALLS, both moves exceed the larger of the two stds. S_p99 FALLS for BOTH. Any sentence
of the form 'the S ratio moves in direction X across networks' is barred. **The S_p99 and
case30-thermal rows are retained above solely so this bar stays checkable at the artifact.**

**WITHDRAWN AND MUST NOT APPEAR:** any 'zero counterexamples in N cases' claim. The set is empty
BY CONSTRUCTION, per the barrier inequality above. State it as a two-line derivation and attach
no sample size. The measured share of 1.000000 and the gap of 5.55e-17 confirm the COMPUTATION,
not the theory.

**Citations:** `lei2018` **RESOLVED for bibliographic identity** — `prior-art.md` 8.5, two
sources, 2026-08-21; **8.5 also records that the paper BODY was never read**, so the specific
'finite-sample rank approach' attribution at `:112` is still unverified and this section must
not add a second such attribution. `vovk2005` and `romano2019` — `prior-art.md` 8.8; romano2019's
pagination is CONFIRMED (dblp + OpenAlex), vovk2005 still needs the first-edition marker.
`barber2021` is NOT cited here; its home is `:258` and its placement defect is in 8.7.

**Estimate: ~300 words, +0.87 pp at 345 w/p. No figure.**

### 3.I Results — the cross-network out-of-sample test — **~250 words, NO TABLE**

**Insertion:** after 250, before `\section{Discussion...}` at 253. **`\label`:**
`\label{subsec:crossnet}`. **The per-network table is CUT.** All per-network rows stay below as
provenance; none is printed in the manuscript.

**Claim (one sentence):** Predicting a network's escalation from its boundary mass and
calibration band width, sealed before its gate ran and fitted only on prior networks, fails
with a mean relative error near one half over 54 sealed predictions.

**WHAT SURVIVES AT 250 WORDS:**
1. **The sealed negative result, as the headline.** 54 predictions, mean relative error
   `0.4726` for predictor A and `0.4933` for B. State the seal and the disjoint split in the
   same sentence. **Predictor A beats B, which is the evidence that there is no stable
   cross-network slope to learn from four networks** — one clause.
2. **The two structural abandons, ONE SPECIFICATION EACH** (below).
3. One clause recording the network-count convention.

**NETWORK-COUNT CONVENTION, fixed here and to be used everywhere:** **five networks attempted**,
**three completed** (case39, case24_ieee_rts, case_illinois200, all v2), **two abandoned**
(case57 voltage clause, case89pegase thermal clause). The v2 `run_status.json` alone lists only
four; it does not carry case57, which was attempted under v1. Any count must cite BOTH status
files or state that it covers v2 only.

**ABANDON SPECIFICATION 1 — case57, voltage clause.** One sentence: at load multiplier 0.0 the
network still sits at `min_vm = 0.9012` pu with 24 buses below 0.94, so no load-multiplier
window satisfies the voltage clause. Cite the zero-load row. Do not assert load-independence
without it.

**ABANDON SPECIFICATION 2 — case89pegase, thermal clause.** One sentence: at load multiplier 0.0
max loading is still `199.37%`, so no window satisfies the thermal clause. Cite the zero-load
row. Same rule.

**DROPPED AT THIS LENGTH:** the within-network arm entirely, the per-network breakdown, and the
`data/network_triage.json` roster. **Consequence: the sentence "two further networks failed
triage under the pinned `enforce_q_lims=True`" LOSES ITS EVIDENCE and must not appear.** The
triage row is retained below for restoration.
| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| per-network status, netstudy v2 (4 networks) | `{'case39': 'COMPLETE', 'case24_ieee_rts': 'COMPLETE', 'case89pegase': 'ABANDONED (no feasible range)', 'case_illinois200': 'COMPLETE'}` | `data/netstudy2/run_status.json` | `results.*.status` | raw | `756bf0fa45e02476` |
| within-network (1e) totals: cal-split CDF vs disjoint test-split gate | `{'n': 54, 'hits': 43, 'n_bitwise_identical': 0, 'mean_abs_error': 0.006122855783483999, 'max_abs_error': 0.01975568464187824, 'by_family': {'ridge': {'n': 27, 'hits': 17, 'mean_signed_error': 0.004664175801652297, 'mean_abs_error': 0.009457749390165525, 'max_abs_error': 0.01975568464187824, 'all_same_sign': False}, 'histgb': {'n': 27, 'hits': 26, 'mean_signed_error': 0.0002017153210343269, 'mean_abs_error': 0.0027879621768024704, 'max_abs_error': 0.015609070269174075, 'all_same_sign': False}}, 'epsilon_alarm_any': False}` | `data/netstudy2/summary.json` | `within_network` | seed-mean | `19766d5040cec8db` |
| cross-network (2b) totals: the genuine out-of-sample test | `{'n': 54, 'A_mean_abs_error': 0.11630622973513659, 'A_mean_rel_error': 0.47255463711418216, 'B_mean_abs_error': 0.10561207946812383, 'B_mean_rel_error': 0.49325198702123735, 'B_hits': 41, 'verdict': 'the cross-network prediction from boundary mass alone is the genuine out-of-sample test; read its relative error, not the within-network one'}` | `data/netstudy2/summary.json` | `cross_network` | seed-mean | `19766d5040cec8db` |
| case39 within-network | `{'hits': 17, 'n': 18, 'mean': 0.004755417491194148, 'mx': 0.012930423724816287, 'bitwise': 0, 'alarm': False, 'seal': 'SEAL INTACT', 'disjoint': True}` | `data/netstudy2/case39/comparison.json` | `top-level` | seed-mean | `e40fc3aa577fbf17` |
| case39 cross-network | `{'A_abs': 0.047996344909855077, 'A_rel': 0.21138176992382546, 'B_abs': 0.08186537982347714, 'B_rel': 0.43989217952424436, 'B_hits': 13, 'prior': ['case118', 'case30_thermal'], 'slope': 0.6796629042800791}` | `data/netstudy2/case39/cross_2b_comparison.json` | `top-level` | seed-mean | `06382885d8e913af` |
| case24_ieee_rts within-network | `{'hits': 9, 'n': 18, 'mean': 0.010505098220086629, 'mx': 0.01975568464187824, 'bitwise': 0, 'alarm': False, 'seal': 'SEAL INTACT', 'disjoint': True}` | `data/netstudy2/case24_ieee_rts/comparison.json` | `top-level` | seed-mean | `116483aadbea6278` |
| case24_ieee_rts cross-network | `{'A_abs': 0.28941053971826936, 'A_rel': 1.1526343043423664, 'B_abs': 0.1659392107297836, 'B_rel': 0.6788513264435896, 'B_hits': 10, 'prior': ['case118', 'case30_thermal', 'case39'], 'slope': 0.6921544026482949}` | `data/netstudy2/case24_ieee_rts/cross_2b_comparison.json` | `top-level` | seed-mean | `cae985d53f3d0278` |
| case_illinois200 within-network | `{'hits': 17, 'n': 18, 'mean': 0.003108051639171215, 'mx': 0.015609070269174075, 'bitwise': 0, 'alarm': False, 'seal': 'SEAL INTACT', 'disjoint': True}` | `data/netstudy2/case_illinois200/comparison.json` | `top-level` | seed-mean | `1f17800d52863f79` |
| case_illinois200 cross-network | `{'A_abs': 0.011511804577285388, 'A_rel': 0.053647837076354926, 'B_abs': 0.06903164785111085, 'B_rel': 0.3610124550958781, 'B_hits': 18, 'prior': ['case118', 'case24_ieee_rts', 'case30_thermal', 'case39'], 'slope': 0.6064526708251727}` | `data/netstudy2/case_illinois200/cross_2b_comparison.json` | `top-level` | seed-mean | `e3d7179aa0c974da` |
**THE HEADLINE IS THE CROSS-NETWORK NUMBER, NOT THE WITHIN-NETWORK ONE.** The within-network
arm measures whether an empirical CDF transfers between two disjoint splits of the SAME
dataset; sampling error is the expected answer and getting it validates nothing. **With the
within-network arm cut from the prose, do not let a summary sentence imply the 54 predictions
were accurate** — the 54 that matter are the cross-network ones.

**A PRIOR VERSION OF THIS EXPERIMENT IS VOID AND MUST NOT BE CITED.** `data/netstudy/` v1
computed the predictive CDF and the gate on the SAME rows, so agreement was definitional;
`scripts/netstudy.py:345` and `feasibility/gate_eval.py:19-21` are the same boolean mask. Its
36/36 hit rate validates nothing. **Only `data/netstudy2/` may be cited.**

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| case57: voltage clause, structural | `{'verdict': 'STRUCTURAL: min_vm stays below the 0.94 floor even at zero load, so no load-multiplier window can satisfy the voltage clause', 'zero_load': [{'multiplier': 0.0, 'converged': True, 'min_vm_pu': 0.901210232938954, 'argmin_bus_0based': 45, 'argmin_bus_ieee': 46, 'n_bus_below_094': 24, 'max_vm_pu': 1.04}]}` | `data/netstudy/case57/nofeasible_diagnostic.json` | `verdict + scaling[multiplier=0]` | raw | `930f4ff81668afaa` |
| case89pegase: thermal clause, structural | `{'verdict': 'STRUCTURAL, THERMAL CLAUSE: max loading stays above 100% even at zero load, so no load-multiplier window can satisfy the thermal clause', 'zero_load': [{'multiplier': 0.0, 'converged': True, 'min_vm_pu': 0.996808668657954, 'max_line_loading_pct': 199.3691033077705, 'max_trafo_loading_pct': 190.12418911487404, 'max_loading_pct': 199.3691033077705, 'meets_voltage': True, 'meets_thermal': False}]}` | `data/netstudy2/case89pegase_nofeasible_diagnostic.json` | `verdict + scaling[multiplier=0]` | raw | `aa91609d83686501` |
| triage verdicts for every network attempted | `[{'net': 'case14', 'status': 'GO', 'ratings': 'PLACEHOLDER (thermal predicate UNDEFINED)', 'minvm': 1.0100000000000002, 'maxload': 1.5075683604572943}, {'net': 'case24_ieee_rts', 'status': 'GO', 'ratings': 'USABLE', 'minvm': 0.9190262634314021, 'maxload': 92.09744578265602}, {'net': 'case30', 'status': 'GO', 'ratings': 'USABLE', 'minvm': 0.9606237083025229, 'maxload': 111.83140586617333}, {'net': 'case_ieee30', 'status': 'GO', 'ratings': 'PLACEHOLDER (thermal predicate UNDEFINED)', 'minvm': 0.9314526970368632, 'maxload': 50.34234434994488}, {'net': 'case39', 'status': 'GO', 'ratings': 'USABLE', 'minvm': 0.982, 'maxload': 77.01593961042626}, {'net': 'case57', 'status': 'GO', 'ratings': 'PLACEHOLDER (thermal predicate UNDEFINED)', 'minvm': 0.7199136792083631, 'maxload': 1.783828050433146}, {'net': 'case89pegase', 'status': 'GO', 'ratings': 'USABLE', 'minvm': 0.9683821878621461, 'maxload': 392.21369912529985}, {'net': 'case118', 'status': 'GO', 'ratings': 'PLACEHOLDER (thermal predicate UNDEFINED)', 'minvm': 0.943, 'maxload': 4.475087324056162}, {'net': 'case145', 'status': 'NO-GO (cost)', 'ratings': 'USABLE', 'minvm': 0.9150000000000004, 'maxload': 1055.5355870993728}, {'net': 'case_illinois200', 'status': 'GO', 'ratings': 'USABLE', 'minvm': 0.8508916163301868, 'maxload': 105.52486650363153}, {'net': 'case300', 'status': 'NO-GO', 'ratings': None, 'minvm': None, 'maxload': None}, {'net': 'GBreducednetwork', 'status': 'GO', 'ratings': 'USABLE', 'minvm': 0.8995590616126872, 'maxload': 191.50855657535084}, {'net': 'iceland', 'status': 'NO-GO', 'ratings': None, 'minvm': None, 'maxload': None}, {'net': 'case1354pegase', 'status': 'NO-GO (cost)', 'ratings': 'USABLE', 'minvm': 0.9810240257365945, 'maxload': 303.45746550740284}]` | `data/network_triage.json` | `networks[]` | raw | `61b34d19b1909b4c` |
**Citations:** none new. **Figure/table: NONE.** The R10 APA-line obligation disappears with the
table.

**Estimate: ~250 words, +0.72 pp at 345 w/p. No table.**

### 3.J Discussion — the physics-features ablation — **~400 words, no new float**

**Insertion:** after 262, before `\section{Conclusion...}` at 265. **RESTORED to the active set
2026-08-24** from PART 9, where it was 9.6. **No float.** Every number below is unchanged from
the specification that was cut; only the length and the print/retain split are new.

**Claim (one sentence):** Adding pre-outage branch flows, the full pre-outage loading vector,
LODF rows and electrical distance to the design matrix improves neither surrogate beyond
seed-to-seed noise, and the full loading vector significantly degrades the linear model.

**THE RUN IS COMPLETE. The outcome is negative and must be reported as negative.**
`CLAUDE.md` section 8 requires it.

**WHAT SURVIVES AT 400 WORDS — four things, in this order. The order is load-bearing: the
premise correction must come FIRST, because the ablation cannot be characterised before the
design matrix it ablates is stated correctly.**

**1. THE DESIGN-MATRIX PREMISE CORRECTION (~80 words), stated before any result.** The brief's
premise — 'the only loading feature is the scenario scalar `agg_loading`' — is wrong.
`agg_loading` is in `make_splits.EXCLUDE_COLS`, so **it is not a feature and the committed design
matrix carries NO loading information of any kind**; `branch_flow_columns_present` is `False`.
The matrix **does** carry `vm0_*`, the **118 pre-outage bus voltages**, so part of the base AC
solution is already exposed — the voltages, not the flows. State the excluded-column set, the
resulting feature count, and the pre-outage bus-voltage family.

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| column audit of data/dataset.parquet | `{'n_columns_total': 634, 'n_feature_columns': 619, 'feature_families': {'pload_': 118, 'qload_': 118, 'genvm_': 53, 'genp_': 53, 'genqmin_': 53, 'genqmax_': 53, 'genon_': 53, 'vm0_': 118}, 'loading_like_names_anywhere': ['agg_loading'], 'loading_like_among_features': [], 'agg_loading_in_EXCLUDE_COLS': True, 'agg_loading_is_a_feature': False, 'branch_flow_columns_present': False, 'correction_to_the_premise': "The brief says 'the only loading feature is the scenario scalar agg_loading'. That is not right: agg_loading is listed in make_splits.EXCLUDE_COLS and is therefore NOT a feature. The committed design matrix carries NO loading information of any kind. It does carry vm0_* (118 pre-outage bus voltages), so part of the base AC solution is already exposed - the voltages, not the flows."}` | `data/physics_features.json` | `column_audit` | raw | `0a1ec40697d6b1d1` |
| the re-solve: 1,500 N-0 base cases, acceptance test against stored vm0_* | `{'n_base_cases': 1500, 'n_contingency_solves': 0, 'elapsed_s': 15.2, 'solver': {'enforce_q_lims': True, 'numba': True, 'init': 'dc', 'algorithm': 'nr'}, 'builder': 'feasibility/generate_dataset.build_net + reconstruct()', 'acceptance': {'n_base': 1500, 'n_nonconverged': 0, 'max_abs_vm_error': 7.422861947325998e-08, 'median_abs_vm_error': 5.6322178143553003e-08, 'max_abs_n0_min_vm_error': 5.238082512182274e-08, 'tolerance_note': 'reconstruction is accepted only if max\|vm error\| < 1e-6', 'passed': True}}` | `data/physics_features.json` | `resolve` | raw | `0a1ec40697d6b1d1` |
**Only the `column_audit` row is printed. The `resolve` acceptance test is RETAINED, NOT PRINTED
— see the drop list.**

**2. THE NEGATIVE RESULT ACROSS ALL FIVE CONFIGURATIONS (~130 words).** Name all five —
`baseline`, `+F1`, `+F1+F2`, `+F1+F3`, `+F1+F2+F3+F4` — for both families, and give MAE with its
seed std. **The best configuration per family does NOT exceed its seed std in either case**
(`exceeds_seed_std` is `False` for ridge `+F1+F3` and for histgb `+F1+F2+F3+F4`). That flag, not
the ranking, is the result. **Apply the std rule explicitly; do not print a ranking without it.**

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| ridge baseline (m2_searched) | `{'mae': 0.003754331383041597, 'mae_std': 0.0001327709477972888, 'r2': 0.7718344962233189, 'q': 0.005198231037165079, 'esc': 0.4906972404572077}` | `data/physics_ablation.json` | `by_target["0.9"] within records[config=baseline,mode=m2_searched,family=ridge]` | seed-mean/std ddof=0 | `ebe57a48ecbfd74b` |
| ridge +F1 (m2_searched) | `{'mae': 0.003757561472638325, 'mae_std': 0.00013064413526126274, 'r2': 0.7740816055900643, 'q': 0.0052265163382688275, 'esc': 0.49006995027785044}` | `data/physics_ablation.json` | `by_target["0.9"] within records[config=+F1,mode=m2_searched,family=ridge]` | seed-mean/std ddof=0 | `ebe57a48ecbfd74b` |
| ridge +F1+F2 (m2_searched) | `{'mae': 0.004160567068914968, 'mae_std': 0.0002469750927689239, 'r2': 0.7436187441155141, 'q': 0.0059267020262995015, 'esc': 0.4790570536938226}` | `data/physics_ablation.json` | `by_target["0.9"] within records[config=+F1+F2,mode=m2_searched,family=ridge]` | seed-mean/std ddof=0 | `ebe57a48ecbfd74b` |
| ridge +F1+F3 (m2_searched) | `{'mae': 0.003707247952052467, 'mae_std': 9.605446564111182e-05, 'r2': 0.778894659214655, 'q': 0.005086370761358228, 'esc': 0.48278147888336403}` | `data/physics_ablation.json` | `by_target["0.9"] within records[config=+F1+F3,mode=m2_searched,family=ridge]` | seed-mean/std ddof=0 | `ebe57a48ecbfd74b` |
| ridge +F1+F2+F3+F4 (m2_searched) | `{'mae': 0.0041605736478983356, 'mae_std': 0.00024697184335338156, 'r2': 0.7436186756728211, 'q': 0.005926983885764669, 'esc': 0.4790857325400939}` | `data/physics_ablation.json` | `by_target["0.9"] within records[config=+F1+F2+F3+F4,mode=m2_searched,family=ridge]` | seed-mean/std ddof=0 | `ebe57a48ecbfd74b` |
| histgb baseline (m2_searched) | `{'mae': 0.0015627340080947231, 'mae_std': 7.57534137085136e-05, 'r2': 0.9227177815491915, 'q': 0.002290702766310826, 'esc': 0.3062513593744674}` | `data/physics_ablation.json` | `by_target["0.9"] within records[config=baseline,mode=m2_searched,family=histgb]` | seed-mean/std ddof=0 | `ebe57a48ecbfd74b` |
| histgb +F1 (m2_searched) | `{'mae': 0.0015923820700770972, 'mae_std': 0.00013318478341733196, 'r2': 0.9199263376405377, 'q': 0.00227093569757173, 'esc': 0.29320976711680763}` | `data/physics_ablation.json` | `by_target["0.9"] within records[config=+F1,mode=m2_searched,family=histgb]` | seed-mean/std ddof=0 | `ebe57a48ecbfd74b` |
| histgb +F1+F2 (m2_searched) | `{'mae': 0.0016253256828618365, 'mae_std': 0.00016538014717106518, 'r2': 0.9189831095020116, 'q': 0.0024039444455195903, 'esc': 0.30894431094520347}` | `data/physics_ablation.json` | `by_target["0.9"] within records[config=+F1+F2,mode=m2_searched,family=histgb]` | seed-mean/std ddof=0 | `ebe57a48ecbfd74b` |
| histgb +F1+F3 (m2_searched) | `{'mae': 0.0015777997761304348, 'mae_std': 9.781834960839108e-05, 'r2': 0.9212936650192578, 'q': 0.002232001521909477, 'esc': 0.2789559951185392}` | `data/physics_ablation.json` | `by_target["0.9"] within records[config=+F1+F3,mode=m2_searched,family=histgb]` | seed-mean/std ddof=0 | `ebe57a48ecbfd74b` |
| histgb +F1+F2+F3+F4 (m2_searched) | `{'mae': 0.001526431521937137, 'mae_std': 0.00011087102283403783, 'r2': 0.9255456494658165, 'q': 0.002207085499369321, 'esc': 0.2794617204268418}` | `data/physics_ablation.json` | `by_target["0.9"] within records[config=+F1+F2+F3+F4,mode=m2_searched,family=histgb]` | seed-mean/std ddof=0 | `ebe57a48ecbfd74b` |
**3. THE ONLY EFFECT EXCEEDING ITS SEED STD IS HARM: F2 ON RIDGE (~80 words).** Every other delta
is inside noise. **One clause must record that the ridge harm holds under BOTH tag modes** —
`m2_searched` and `m2_fixed` agree for ridge — because that agreement is what makes the harm
credible rather than an artefact of the re-run search. **The four `m2_fixed` values below are
RETAINED, NOT PRINTED**; the clause asserts the agreement, the table backs it.

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| ridge +F1+F2 (m2_fixed) | `{'mae': 0.004181458626422725, 'mae_std': 0.00025374360587192377, 'r2': 0.7417276870212449, 'q': 0.0059959748766333035, 'esc': 0.481537740542956}` | `data/physics_ablation.json` | `by_target["0.9"] within records[config=+F1+F2,mode=m2_fixed,family=ridge]` | seed-mean/std ddof=0 | `ebe57a48ecbfd74b` |
| ridge +F1+F2+F3+F4 (m2_fixed) | `{'mae': 0.00418146274229267, 'mae_std': 0.00025373997728867523, 'r2': 0.7417277815189343, 'q': 0.005996244815169516, 'esc': 0.4815700041968126}` | `data/physics_ablation.json` | `by_target["0.9"] within records[config=+F1+F2+F3+F4,mode=m2_fixed,family=ridge]` | seed-mean/std ddof=0 | `ebe57a48ecbfd74b` |
| histgb +F1+F2 (m2_fixed) | `{'mae': 0.001554613935082648, 'mae_std': 7.746789577967615e-05, 'r2': 0.9226448716849719, 'q': 0.0023148622230970027, 'esc': 0.30339798104248006}` | `data/physics_ablation.json` | `by_target["0.9"] within records[config=+F1+F2,mode=m2_fixed,family=histgb]` | seed-mean/std ddof=0 | `ebe57a48ecbfd74b` |
| histgb +F1+F2+F3+F4 (m2_fixed) | `{'mae': 0.0015435561459530886, 'mae_std': 0.00010878654202252338, 'r2': 0.9244145500363139, 'q': 0.002259294136701784, 'esc': 0.2921845963082056}` | `data/physics_ablation.json` | `by_target["0.9"] within records[config=+F1+F2+F3+F4,mode=m2_fixed,family=histgb]` | seed-mean/std ddof=0 | `ebe57a48ecbfd74b` |
| best configuration by MAE, per family, with significance | `{'ridge': {'best_config': '+F1+F3', 'best_mae': 0.003707247952052467, 'baseline_mae': 0.003754331383041597, 'delta_pct': -1.2541096186076446, 'exceeds_seed_std': False}, 'histgb': {'best_config': '+F1+F2+F3+F4', 'best_mae': 0.001526431521937137, 'baseline_mae': 0.0015627340080947231, 'delta_pct': -2.3230112078923773, 'exceeds_seed_std': False}}` | `data/physics_conclusion.json` | `best_config_by_mae` | seed-mean | `d6e21ce26bedf4b0` |
| wall time per configuration (s) | `{'baseline': 2605.0, '+F1': 2651.0, '+F1+F2': 3414.7, '+F1+F3': 3344.5, '+F1+F2+F3+F4': 4578.9}` | `data/physics_ablation.json` | `elapsed_s` | raw | `ebe57a48ecbfd74b` |
**The histgb divergence between `m2_searched` and `m2_fixed` is DROPPED at this length.**
Consequence: no sentence may characterise how the search responds to added features for histgb.

**4. THE PERMUTATION CONTROL (~90 words).** Report all three arms — `baseline`, `F1_real`,
`F1_shuffled` — with their MAE values **stated against the seed-to-seed std**, so the reader
applies the std rule instead of reading a ranking. **Do not claim F1's physical content
contributes**: the shuffled arm is not worse than the real one. Report the fresh-net
reproduction error and the in-service branch count at solve time in the same sentence, so the
audit is visibly a leakage test and not a performance claim.

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| F1 leakage audit: fresh-net reproduction and the within-element permutation | `{'c2': {'n_scenarios_checked': 25, 'all_186_branches_in_service_before_and_after_solve': True, 'fresh_net_per_scenario': True, 'max_abs_reproduction_error': {'pre_p_mw': 0.0, 'pre_q_mvar': 0.0, 'pre_loading_percent': 0.0, 'pre_i_ka': 0.0}, 'verdict': "F1 reproduces from a FRESH net with every branch in service; the stored values cannot depend on any prior row's outage"}, 'perm': {'baseline': {'mae': 0.0015637634048802542, 'r2': 0.9263341003707094, 'n_features': 701, 'fit_s': 19.6}, 'F1_real': {'mae': 0.0015538985417833714, 'r2': 0.9265841387307037, 'n_features': 705, 'fit_s': 19.9}, 'F1_shuffled': {'mae': 0.0015300136559860003, 'r2': 0.9261287434252089, 'n_features': 705, 'fit_s': 21.8}}}` | `data/f1_leakage_audit.json` | `check_2 + check_4` | seed 0 | `86698fa6ddb16164` |
**WHAT WAS DROPPED AT 400 WORDS, and the consequence of each:**

| dropped | consequence |
|---|---|
| **F3's LODF zero-fill policy** — the undefined-row count, the denominator criterion, the `lodf_valid` indicator (table below, retained) | **LODF may be NAMED as one of the added families and nothing more.** The 'REQUIRED wherever the LODF fill is described' rule does not trigger, because the fill is no longer described. If any sentence describes the fill, the full rule comes back with it. |
| **The re-solve acceptance test** — 1,500 N-0 base cases reproduced against stored `vm0_*` | The premise correction is asserted from the column audit alone. **No sentence may claim the stored `vm0_*` were independently verified**, because the evidence is no longer in the paper. |
| **Wall time per configuration** | No cost claim may be made about the added features. The ablation reports accuracy only. |
| **The four `m2_fixed` printed values, and the histgb mode divergence** | Only the ridge-agreement clause survives (item 3). |
| **The collinearity explanation** — LODF and electrical distance being topology-only and collinear with the 186-way branch one-hot | **This removes the section's only causal explanation, and that is the safer outcome.** The standing rule — any causal explanation of the null must be labelled a hypothesis and must name what would test it — no longer has anything to bind, because no cause is offered. **The ablation measures the null; it does not identify its cause. Say that, and stop.** |

**RETAINED BUT NOT PRINTED**, so any of the above can be restored without re-deriving:

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| LODF zero-fill policy and the validity indicator | `{'rule': 'row zero-filled when \|1 - h[k]\| < 1e-9 OR any cell non-finite', 'den_tolerance': 1e-09, 'indicator_column': 'lodf_valid', 'indicator_semantics': '1 = LODF row defined; 0 = outage islands the network and every entry was filled', 'n_valid': 177, 'n_invalid': 9}` | `data/physics_features.json` | `F3.CORRECTED.fill_policy` | raw | `0a1ec40697d6b1d1` |
**Citations:** none new. **Estimate: ~400 words, +1.16 pp at 345 w/p. No float.**

### 3.D Related Work — IN-PLACE rewrite of `:86` — **~150 words, PROSE ONLY, NO TABLE**

**Insertion:** rewrites `:86` in place. **NOT a new `\section`.** The four-axis comparison table
is CUT. The compressed related-work paragraph already at `:86` is REWRITTEN, not removed.

**Claim (one sentence):** On a common budget axis two non-ML comparators match or beat the
gate's capture at the budgets it actually operates at, and the like-for-like capture metric must
be named whenever that comparison is made.

**WHAT SURVIVES AT 150 WORDS — two things only:**
1. **The baseline finding, stated against the gate.** `static_severity` — a fixed per-element
   ranking that never reads the current operating point and never reads a test label — is the
   best comparator at k=5 and at k=100, tied with both point-surrogate variants. At k=5 the tie
   **cannot be broken**: the oracle equals `static_severity`'s mean exactly, headroom
   `0.000e+00`. The gate's own budget lands at k-equivalent `91.3` (ridge) and `57.0` (histgb),
   inside the range where the comparators are competitive.
2. **The asymmetry warning**, verbatim below, in one clause.

**WHAT IS DROPPED:** the four-axis comparison of prior surrogate and classical screens
(Manoharan, Alcántara, Christianson, Ejebe). **Consequence: the existing `:86` sentences that
describe those three papers STAY AS THEY ARE** — this rewrite appends the baseline finding to
them rather than replacing them, so no citation is orphaned. **Verify after editing that
`manoharan2026`, `alcantara2026` and `christianson2025` are still cited at `:86`.**

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| new power-flow solves used to produce the comparison | `0` | `data/baselines.json` | `n_new_power_flow_solves` | count | `2a6f005cec8914fe` |
| budgets k reported | `[5, 10, 20, 50, 100]` | `data/baselines.json` | `k_reported` | raw | `2a6f005cec8914fe` |
| best baseline at k=5, with the tie set and the oracle | `{'best': 'static_severity', 'mean': 0.154848069914131, 'std': 0.001480183946999836, 'oracle': 0.154848069914131, 'tied': ['static_severity', 'surrogate_point_ridge', 'surrogate_point_histgb'], 'headroom': 0.0}` | `data/baselines.json` | `adjudication.best_baseline_at_k.5` | seed-mean/std | `2a6f005cec8914fe` |
| best at k=10 | `{'best': 'surrogate_point_histgb', 'mean': 0.30924096609974394, 'std': 0.0028593487178835892, 'oracle': 0.309696139828262, 'tied': ['surrogate_point_histgb'], 'headroom': 0.0004551737285180546}` | `data/baselines.json` | `adjudication.best_baseline_at_k.10` | seed-mean/std | `2a6f005cec8914fe` |
| best at k=20 | `{'best': 'surrogate_point_histgb', 'mean': 0.6078855770271991, 'std': 0.005429131193755249, 'oracle': 0.6184622190871562, 'tied': ['surrogate_point_histgb'], 'headroom': 0.010576642059957009}` | `data/baselines.json` | `adjudication.best_baseline_at_k.20` | seed-mean/std | `2a6f005cec8914fe` |
| best at k=50 | `{'best': 'surrogate_point_histgb', 'mean': 0.9287228804811146, 'std': 0.014425396909695186, 'oracle': 0.9909877554252949, 'tied': ['surrogate_point_histgb'], 'headroom': 0.062264874944180315}` | `data/baselines.json` | `adjudication.best_baseline_at_k.50` | seed-mean/std | `2a6f005cec8914fe` |
| best at k=100, with the tie set and the oracle | `{'best': 'static_severity', 'mean': 0.9756860617286156, 'std': 0.0045148894581456, 'oracle': 1.0, 'tied': ['static_severity', 'surrogate_point_ridge', 'surrogate_point_histgb'], 'headroom': 0.024313938271384394}` | `data/baselines.json` | `adjudication.best_baseline_at_k.100` | seed-mean/std | `2a6f005cec8914fe` |
| gate ridge k-equivalent budget | `91.25333333333333` | `data/baselines.json` | `adjudication.gate_vs_baselines.ridge.k_equivalent_mean` | seed-mean | `2a6f005cec8914fe` |
| gate histgb k-equivalent budget | `56.952666666666666` | `data/baselines.json` | `adjudication.gate_vs_baselines.histgb.k_equivalent_mean` | seed-mean | `2a6f005cec8914fe` |
**THE ASYMMETRY MUST BE STATED WHEREVER THE GATE IS COMPARED.** From
`data/baselines.json` `gate_definition.asymmetry_warning`, verbatim:

> capture_escalate_only and the baselines are the like-for-like comparison. capture_escalate_or_flag credits the gate with a mechanism the baselines do not have. Do not quote the second against the first without saying so.

The gate's budget is not free: `k_equivalent = escalation * rows_per_scenario`, so the gate
cannot be swept along the k axis without changing its coverage target. Report
`capture_escalate_only` as the like-for-like number. **This warning is NOT optional at 150 words
— if it will not fit, cut the k=100 row instead.**

**Two comparator caveats that must travel with any citation of them:**
- PI_VQ exponent and per-bus weights: `NO SOURCE` in the notes; the
  artifact implements the most common form and says so.
- `base_proximity_n0` as specified is DEGENERATE (`True`); a
  steelman variant was added and is labelled an addition, not the requested comparator.

**Citations:** none new, and **none added**. The GNN comparator is NOT cited — it has no bibkey
in the `.tex` and at 150 words there is no room to introduce one. `bates2021` is unaffected here;
its `prior-art.md` record is 8.1, verified 2026-08-21.

**Estimate: ~150 words appended to `:86`. NET +150 words = +0.43 pp at 345 w/p. No table.**

---
## PART 4 — WHAT CANNOT BE WRITTEN

| claim | label | what would be required |
|---|---|---|
| `4.6M cases` as a counterexample population | **NO SOURCE** | nothing. Zero hits in any `data/` artifact; it appears only in `notes/ai-prompt-log.md`, `notes/new-sections-layout.md` and `notes/audit-new-sections-layout.md`. The two real populations are 6,128,100 test rows and 19,625 missed. The claim is also WITHDRAWN as definitional. |
| 2E window width `7.7 pp` | **NO SOURCE** | nothing. Zero hits in any `data/` artifact; notes-only. Do not substitute the base `agg_loading` range. |
| histgb MAE near `0.00076` under any feature configuration | **NO SOURCE** | nothing. The only `0.00076` in `data/` is `q_for_esc_10` in `data/tradeoff_curve.json`, a band width, not an MAE. The measured `+F1` histgb MAE is in section 3.J. |
| S ratios `0.604 -> 0.219` / `0.443 -> 0.482` | **NO SOURCE / SUPERSEDED** | nothing. The measured values are in section 3.A and they invert the supplied direction. |
| stratum violation rates `24.3%` / `4.7%` | **NO SOURCE** | nothing. Grep hits are substrings inside `break_even_cases`. Measured values in section 3.G. |
| in-distribution marginal coverage `0.7970` | **NO SOURCE as that quantity** | nothing. The hits in `data/tuned_metrics.json` are `coverage_emp` fields of a different experiment. Measured 2C value in section 3.G. |
| thermal full-population share `0.9927` | **NO SOURCE** | nothing. The corrected value is in section 0.3. |
| 2F concentration: `deep_elements`, `n_distinct_elements`, `top_element_share`, `deep_argmin_buses_ieee`, `n_distinct_argmin_buses`, `top_bus_share` | **SINGLE-PATH** | a per-seed re-derivation. `data/qlimit_class.json` stores these as pooled scalars with no per-seed counterpart, and the deep-miss pools are unions over five splits of the same 1,500 scenarios, so they overlap and overstate concentration. Do not state any percentage-concentration figure. |
| 2F deep-miss vs baseline off-setpoint comparison | **CANNOT BE EVALUATED under the std rule** | a per-seed breakdown. The artifact carries no std of any kind. The difference between the pooled means is smaller than any std that has been quoted for it, under every pairing. |
| case30-thermal sub-1% crossing at 0.96 | **INDETERMINATE** | more seeds. 0.41 std from the threshold with 2 of 5 seeds below. Quote 0.97, or quote the pair. |
| case30-published headline figures at `:260` | **SUPERSEDED** | nothing — they are correct for a dataset that is not thermally feasible. Replace per section 3.H and label the result set. |
| pooled percentiles of false-flag margins | **CANNOT BE COMPUTED** | re-running the flag-confusion pass with raw margins retained. Only per-seed p50/p90/max/mean are stored. |
| the 46.18% draw-rejection share | **CANNOT BE COMPUTED from a committed artifact** | re-running the generator with rejection logging. Rejected draws are never written to `data/dataset.parquet`. |
| the rejected-scenario count in `data/break_even.json` | **UNVERIFIABLE BY CONSTRUCTION** | the artifact says so itself: it is a hardcoded constant whose source run log is not a committed file. |
| home ZIP for the PDF filename (R14) | **NO SOURCE** | the owner. `notes/sts-constraints.yaml` R14 states it is not recorded in this repository and must not be guessed. |
| any GNN recall figure | **SOURCE EXISTS, NO BIBKEY** | a bibitem. The figures are in `notes/lit/notes/Graph Neural Networks for Fast Contingency Analysis of Power Systems.md` section 4, flagged as approximate bar-label transcription. That paper has no key in the `.tex`. |
| `net_speedup` on any network other than case118 | **PROVENANCE DEFECT** | re-timing the solver per network. Every `net_speedup` in the case30 and netstudy artifacts divides by the case118 `ms_solver`; per-network measured solve times exist in `data/network_triage.json` and were NOT substituted. |
| the `baselines.py` comparison against a physics configuration | **RUN NOT DONE** | a feature-injection hook. `scripts/baselines.py:330-331` builds its design matrix from `data/dataset.parquet` with no such hook; editing it means editing a committed analysis script. |
| any network-general statement of the escalation floor | **BARRED** | more networks, and it would still be barred by CLAUDE.md section 8. Five networks were attempted; two could not be built. |
| `data/netstudy/` v1 hit rates | **VOID** | nothing. Definitional, not empirical. Cite `data/netstudy2/` only. |

**No section in PART 3 is blocked on an unfinished run.** The physics ablation completed; its
outcome is negative and section 3.J is specified against the completed artifact.

---
## PART 5 — ERRATA THE AUDIT IMPLIES

`URTC` = `paper_current_URTC_20260808.tex` (the submitted version). `STS` =
`report/paper_current_STS.tex`. **None of these is applied.**

| id | defect | evidence | affects |
|---|---|---|---|
| **E-1** | III-A claims generator base values are scaled by the 1.0-1.12 multiplier. They are never scaled. | `STS:104` vs `feasibility/generate_dataset.py:136-144`; all 53 `genp_*` columns `nunique==1`, `std=0` | BOTH |
| **E-2** | III-A states the multiplier range is 1.0-1.12. True only for per-bus load P in independent mode. | `STS:104` vs `data/dataset.parquet`; measured support in PART 2 item 1; cause `generate_dataset.py:21`, `:111` | BOTH |
| **E-3** | III-A's 'the remainder failing to converge' implies 1,545 failures. | `STS:104` vs `data/dataset.parquet`: 45 failures; 1,500 are N-0 base rows | BOTH |
| **E-4** | Line 262 states no N-2 cases were tested. | `STS:262` vs `data/sampling_audit.json`; `P_GEN_OUT = 0.30` at `generate_dataset.py:28`, drawn `:128` | BOTH |
| **E-5** | IV-B's title and supporting sentence assert a general model-safety ordering. | `STS:229`, `:231` vs three result sets; PART 2 item 3 | BOTH |
| **E-6** | Both 'sub-1%' crossings fail at one sigma. | `STS:72`, `:209`, `:215`, `:250` vs Table II `:186`, `:196` | BOTH |
| **E-7** | ANSI 0.917 pu cited to the standard, sourced from a NEMA front-matter excerpt. | `STS:260` vs `notes/prior-art.md` section 7.3 | BOTH |
| **E-8** | `nerc` has no entry of any kind in `notes/prior-art.md`. | `grep -ni 'nerc\|TPL-001' notes/prior-art.md` returns 0; the `.tex` comment at `:299-300` says so | BOTH |
| **E-9** | Fig. 1 embeds the M1-sized schematic. | `STS:138` `data/gate_schematic_v2.png`; M1 vs M2 `q_hat` in PART 2 item 13; `data/gate_schematic_v3.png` is the M2 version and is unreferenced. `notes/erratum.md` E1 records it | BOTH; E1 cites `paper_current_URTC_20260808.tex:112` |
| **E-10** | Line 92's 'the only active constraint is the lower voltage limit'. | `STS:92` vs `data/thermal_check.json` at `networks.case118.overvoltage.n1.share_above_1p05` = 0.7313581043537488 and `...n0_base.share_above_1p05` = 0.734. That artifact names its own input at `networks.case118.overvoltage.dataset` = `data/dataset.parquet`, where the same two shares re-derive from `max_vm>1.05`. **Either artifact may be cited; the jsonpath was the missing part, not the artifact.** | BOTH |
| **E-11** | Line 260's 0.94 pu justification is circular. | 'all sit above 0.94 pu' IS the acceptance criterion at `feasibility/generate_dataset.py:256` | BOTH |
| **E-12** | Acknowledgments assert all numbers came from committed tested code at the cited URL. | `STS:287` cites `rajsaha-blip` = `upstream`, HEAD `990c3c5`; local and `origin` are at `ab970c19`; `notes/` is gitignored at `.gitignore:23` | BOTH |
| **E-13** | Zero subsections carry `\label{}`, and three comments name subsection ids the document cannot print. | `STS:134`, `:220`, `:239`; `\thesubsection` renders `IV.1` | BOTH |
| **E-14** | Abstract and line 260 pair a case118 **ridge** headline with a case30 **histgb** headline without naming either family. | `STS:72`, `:260` vs `data/case30_frozen.json` | BOTH |
| **E-15** | Two voice families in one document. | `we`x17, `our`x5, `us`x1 across the body; `the authors` at `STS:287` | BOTH |
| **E-16** | ~~`notes/erratum.md` E1's caveat that no `urtc-submission` tag exists.~~ **WITHDRAWN — already corrected upstream.** `notes/erratum.md:48-54` was amended on 2026-08-19 and now reads "**That is no longer true.**", naming tag object `23bc760` -> commit `8cefaa7`. No erratum is owed. | `notes/erratum.md:48-54`, verified from source; the previous pointer `:46` landed two lines above the caveat block | **none — no defect remains** |
| **E-17** | `data/netstudy/` v1 reported a 36/36 hit rate as validation. | `scripts/netstudy.py:345` vs `feasibility/gate_eval.py:19-21` are the same boolean mask; void notice in `notes/RUN_REPORT.md` | record only; not yet in either .tex |
| **E-18** | `notes/writing-numbers.md` row 51 no longer reconciles. | stored sha16 `23d42c7146e0f580` vs current `cbeadaa2d61d9054` for `data/thermal_check.json`; the file's own 'ROW 51 SUPERSEDED' section gives the corrected value | record only |
---

---

## PART 6 — ORDER AND BUDGET

### 6.1 Writing order, with dependencies

Ten items for the active set. Two are new: the `:92` correction orphaned by cutting 3.E,
and the bibliography repair forced by cutting 3.G.

| # | item | why here | depends on |
|---|---|---|---|
| 1 | PART 2 fixes to III-A (`:104`) | three false statements in one sentence; everything downstream describes this dataset. **Now also the only home for the 45 non-convergence failures** (see 9.2) | nothing |
| 2 | PART 2 fix to `:92`, over-voltage scope | **orphaned by cutting 3.E**; a scope statement other sections inherit (see 9.3) | III-A fixed |
| 3 | PART 2 fixes to `:262` and `:268` | scope statements. **`:262` now also drops `tibshirani2019` and re-sources to `vovk2005`** (see 9.5) | nothing |
| 4 | Bibliography repair | `tibshirani2019` becomes uncited once step 3 lands; remove the bibitem and set `\begin{thebibliography}{18}` | step 3 |
| 5 | 3.A Theory | the identity and the barrier inequality are the mechanism the results refer back to | `lei2018` resolved (`prior-art.md` 8.5); `vovk2005` edition marker; `romano2019` pagination CONFIRMED |
| 6 | IV-B retitle (PART 2 item 3) | must be scoped before 3.H introduces the second result set | 3.H numbers to hand |
| 7 | 3.H case30-thermal replacing `:260` | supplies the second result set and kills the superseded case30-published NUMBERS | IV-B retitled |
| 8 | 3.I cross-network test | the sealed negative result; cites the v1 void | 3.H, so the result-set naming convention exists |
| 9 | 3.J physics-features ablation | a negative result about the SURROGATE, not the gate; independent of every other item. **Placed after item 3 because it inserts after `:262`, the line that item 3 rewrites** | `:262` corrected; run already complete |
| 10 | 3.D Related Work appended at `:86` | written last because the baseline finding must be framed against the final claim set | 3.A, 3.H, 3.I, 3.J settled |

**Conclusion rewrite is NOT a separate item at this budget.** With six sections cut there is no
new claim set to summarise; the existing Conclusion needs only the PART 2 corrections already
listed. **Nothing here is blocked on an unfinished run.** One item is blocked on a decision
rather than compute: the `vovk2005` edition marker. **Nothing is blocked on
`notes/writing-numbers.md`** — the break-even and `ms_solver` rows that blocked the old item 11
were added 2026-08-21, and 3.F, the only section that needed them, is cut.

### 6.2 Page budget

**THE OLD BUDGET AND WHY IT WAS WRONG.** The previous 6.2 projected +4,670 words at +12.35 pp,
implying **378 words/page**. It also opened from a "~11.0 pp" current body that was an estimate,
not a count. Both are replaced below by a measurement.

**DERIVATION OF WORDS/PAGE. Stated assumption, one:** new sections add running text, headings and
captions, but no graphics, no bibliography and no title block; so the density that governs them
is the density of pages carrying running text, not the all-in density of the current document.

| step | value | basis |
|---|---|---|
| body words, prose only | `3,164` | owner's count; independently re-derived below |
| total pages | `12` | owner's count. **UNVERIFIABLE HERE — no TeX toolchain exists in this environment.** Every page figure below inherits that limitation |
| figure graphics | `-1.39 pp` | **MEASURED.** 4 PNGs: pixel aspect ratio x `\textwidth` fraction / 9 in text height |
| bibliography | `-0.79 pp` | modelled. 485 words at `\singlespacing` + 19 item skips + heading |
| tabular bodies | `-0.48 pp` | modelled. 20 `\\` row breaks at body line height |
| title / author block | `-0.22 pp` | modelled. `\title` with `\vspace{-0.5in}`, `\author`, `\maketitle` |
| **pages carrying running text** | **`9.12 pp`** | `12 - 2.88` |
| **PROSE-ONLY DENSITY** | **`345 words/page`** | `3,164 / 9.12 = 347`, rounded down to 345 |

**Captions and headings are deliberately LEFT IN the numerator's pages** — they consume text
lines the way prose does, and new sections will add their own.

**INDEPENDENT WORD-COUNT CHECK.** Comments stripped; body taken between `\begin{document}` and
`\end{document}`; `thebibliography` removed; math, `tabular`, `equation`/`align` removed;
`\label`/`\ref`/`\cite`/`\includegraphics` removed with their arguments; remaining command names
dropped but their brace contents kept; tokens counted on `[A-Za-z0-9][A-Za-z0-9'\-.]*`.

| definition | words | vs 3,164 |
|---|---|---|
| body incl. float captions, excl. bibliography | `3,471` | `+9.7%` |
| body excl. `figure`/`table` environments | `3,214` | `+1.6%` |
| the same, minus section/subsection headings | `3,173` | **`+0.3%`** |

**The owner's 3,164 is CONFIRMED**, matching the third definition to nine words. Float count
independently confirmed at **4 figures and 2 tables**. No material difference; 3,164 is used.

**A CORRECTION TO THE PREMISE OF THIS REBUILD.** The old guide's implied 378 w/p was compared
against the all-in `3,164 / 12 = 264` w/p and called "roughly 43% denser than the document
actually achieves." **That comparison is not like-for-like.** The all-in 264 includes page area
consumed by four figures and two tables; prose-only sections do not incur it. Against the
correct figure the old guide was **378 vs 345, about 10% optimistic**, not 43%. The old budget
was still wrong — 4,670 words is **13.5 pp of prose alone** at 345 w/p, against the +12.35 pp it
claimed, and that is before floats — but it was wrong by roughly 1 to 3 pp, not by a third.
**The decision to cut to ~1,000 words stands on its own; the stated reason should be accurate.**

**THE NEW BUDGET.**

| item | words | pp at 345 w/p |
|---|---|---|
| PART 2 III-A replacement (`:104`), net | `+120` | `+0.35` |
| PART 2 `:92` over-voltage correction, net (from cut 3.E) | `+25` | `+0.07` |
| PART 2 remaining corrections incl. `:262`, `:260` ANSI, `:260` circularity | `0` | `0.00` |
| 3.A Theory, no figure | `+300` | `+0.87` |
| 3.H case30-thermal, 200 replacing 190 | `+10` | `+0.03` |
| 3.I cross-network, no table | `+250` | `+0.72` |
| 3.J physics-features ablation, no float **(RESTORED 2026-08-24)** | `+400` | `+1.16` |
| 3.D Related Work appended at `:86`, no table | `+150` | `+0.43` |
| **TOTAL NEW PROSE** | **`+1,255`** | **`+3.64`** |
| new floats | `0 of 2 allowed` | `0.00` |
| **PROJECTED TOTAL** | | **`~15.6 pp`** |

**Against a hard 20-page cap this is UNDER by ~4.4 pp. No levers are needed.**

**DENOMINATOR CORRECTED 2026-08-27 — the projected total above is NOT the number the 20-page cap
applies to.** STS 2027 Rule 4b excludes the title page, the abstract and the bibliography; Rule 4e
includes appendices. Both verbatim in PART 10.7, fetched 2026-08-27.

| excluded by Rule 4b | pp | basis |
|---|---|---|
| title block | `0.22` | §6.2 accounting above |
| abstract | `0.47` | 161 words (machine-counted from `:69-77`) at 345 w/p |
| bibliography | `0.79` | §6.2 accounting above |
| **total excluded** | **`1.48`** | |

| quantity | as §6.2 states it | Rule-4b corrected |
|---|---|---|
| current paper | `12.00 pp` | **`10.52 pp` countable** |
| projected with +1,255 words | `15.64 pp` | **`14.16 pp` countable** |
| **headroom to 20 pp** | `4.36 pp` | **`5.84 pp`** |

**The exclusions buy `1.48 pp` of headroom that §6.2 was not counting.** With PART 10.3's float
citations added (~72 words) the projection becomes `15.85 pp` gross, **`14.37 pp` countable, and
headroom `5.63 pp`**.

**RULE 4e: APPENDICES COUNT TOWARD THE 20 PAGES.** Nothing may be moved into an appendix to evade
the limit. Rule 4e states both placements are acceptable and both are charged the same.

**PRECONDITION.** The exclusion is only computable if the title page and abstract are *pages*.
They currently are not — `\maketitle` at `:64` and a `\section*{Abstract}` at `:69` run inline.
PART 10.5 records this as a FAIL on structure. Excluded pages are excluded however much space they
take, so fixing the layout costs no budget.

**THE TOTAL IS NOW ~255 WORDS OVER THE ~1,000-WORD FIGURE THIS BUDGET WAS BUILT TO**, because
restoring 3.J was a deliberate decision taken after that figure was set. **It is recorded as an
overrun, not silently absorbed.** At `+3.64 pp` against a 20-page cap the overrun costs nothing;
the ~1,000 figure was a budget, not a constraint, and the constraint is the page cap.

**REMAINING HEADROOM AGAINST 20 pp: `~4.4 pp`**, of which about `0.80 pp` is the two unused
floats at the measured mean of `0.40 pp` per existing figure, leaving roughly **`3.5 pp`, or
~1,240 words at 345 w/p, of prose headroom.** The first claim to restore with it is named in
9.1; the second is 3.J's own drop list, whose largest item is F3's LODF fill policy.

**9.1 QUOTES THE SUPERSEDED HEADROOM.** Its closing sentence offers the flag-branch scope claim as
"the first claim to restore from 6.2's unspent 145-word headroom." That 145 was correct when 3.J
was cut; **the figure is now `~3.5 pp` / ~1,240 words, per the table above.** 9.1 is left
unchanged because PART 9's entries are held fixed; **this table is the authority on headroom, not
9.1.** The ~40-word discharge 9.1 proposes is unaffected and still the cheapest item to buy.

**ONE FIGURE COUNT CHANGES.** No float is added, and none is removed. The manuscript stays at 4
figures and 2 tables. `data/fig_identity.png` is built but unused; it is not deleted.

**PART 7 AND PART 8 AUDIT THE RETIRED 6.2, NOT THIS ONE.** PART 7 item 4.6 and PART 8.2 item 5
both find a lever-arithmetic error in the old budget (levers summing to 2.9 pp landing at
20.45 pp, not 20.05 pp). **That finding is correct about the file it audited and no longer
describes this one** — the levers, the 23.35 pp total and the 20-page overrun are all gone.
Both are preserved unchanged as instructed; read them as history, not as open items.

**EVERY PAGE FIGURE IN THIS FILE DERIVES FROM THE 345 w/p ROW ABOVE.** No other density appears
anywhere in this guide. Page figures inherit the unverifiable 12-page anchor and are planning
numbers, not compile results.

---
## PART 7 — INDEPENDENT VERIFICATION

The following is the verifier's report **reproduced verbatim**. It was produced by an agent that
did not write this file, working read-only from the artifacts. **Its findings are NOT resolved
here.** Where it disagrees with a section above, both statements stand and the disagreement is
listed in section 8.

---

# VERIFICATION (independent pass)

**Verifier did not author this file.** Every number, sha, citation and line pointer below was re-derived from the artifacts with `.venv/bin/python`; no value was copied from the guide. Read-only throughout; no file written, no git write.

**Summary — 153 provenance rows checked · 153/153 source files exist · 153/153 stored `sha256(16)` still match · 153/153 values reproduce exactly at full float precision · 0 reproduced only after rounding · 0 failed to reproduce · 20 rows carry an INCOMPLETE jsonpath/aggregation cell (value right, stated path underdetermines it) · 12/12 citation keys have a `\bibitem` · 3 citation status notes are wrong · 10/10 insertion points confirmed, 0 collisions · 7 adversarial claims: 5 confirmed exactly, 1 count off by one (load-bearing part still correct), 1 confirmed with caveat · 6 further defects found.**

Note on scope: the guide contains **153** provenance-format rows, not ~135. Total non-separator table rows: **374**.

## 1. PER NUMBER

### 1.1 Existence and sha

All 153 rows name a file that exists. All 153 stored `sha256(16)` prefixes equal the file's current sha256 prefix, recomputed this pass. Separately, all **39** full sha256 values in §0.1 match their files exactly. **Zero sha defects.**

### 1.2 Value re-derivation

All 153 rows reproduce exactly at full float precision across 21 named artifacts plus 15 single-row artifacts. **No row failed to reproduce. No row needed rounding to reproduce.** Notable confirmations: `escalation_at_095` is exact under ddof=0 (ddof=1 would give 0.003648/0.013309, so the stated convention is the right one); the three case30-thermal record dicts re-aggregated from `records` (n=5, ddof=0) are exact across all 24 sub-fields; `baselines` `headroom` is derived, not stored, and all five derive exactly.

### 1.3 Six rows in §3.G whose stated column omits a required filter

The six stratum rows print correct numbers, but the jsonpath/column cell states only `n0_min_vm>=median` / `n0_min_vm<median`. Taken literally (all 280,500 rows) they do **not** reproduce. They reproduce exactly once the population is restricted to converged N-1 rows.

| row | printed | literal reading (all rows) | with `converged N-1` filter |
|---|---|---|---|
| benign stratum rows | `139485` | 140250 | **139485** ok |
| benign violation rate | `0.15373696096354447` | 0.15289839572192512 | **exact** ok |
| benign gen-outage prevalence | `0.22528587303294262` | 0.2253333333333333 | **exact** ok |
| marginal stratum rows | `139470` | 140250 | **139470** ok |
| marginal violation rate | `0.19577686957768695` | 0.19468805704099823 | **exact** ok |
| marginal gen-outage prevalence | `0.27323438732343874` | 0.2733333333333333 | **exact** ok |

139485 + 139470 = 278955 = the converged-N-1 count. **Fix: add the `converged N-1` filter to these six cells.**

### 1.4 Fourteen rows in §3.J whose stated path omits the coverage target

`mae`, `mae_std`, `r2` reproduce under the stated path. `q` and `esc` do **not** — they are `by_target[...]` fields and reproduce only at **coverage target 0.90**, which no cell states. The artifact's own `operating_targets` are `{"ridge": 0.94, "histgb": 0.97}`; a reader following those gets different numbers (ridge baseline: 0.00707984773124819 / 0.6434123029630445 at 0.94; histgb baseline: 0.005744658842240824 / 0.6367945178499592 at 0.97). **Fix: add `by_target["0.9"]` to the jsonpath cell of all 14 rows.** Values as printed are correct.

### 1.5 Rows whose printed value is a re-presentation, not the literal stored object

Values all correct; key names differ from the artifact (`oracle` vs `oracle_mean`, `tied` vs `statistically_tied_with_best`, `acc` vs `acceptance_rate`, `c2` vs `check_2_base_solve_integrity`, the six netstudy2 rows, and `q1_q2_per_seed.ridge` which is a **list**, not a dict).

### 1.6 Numbers stated with NO provenance row

- §2.1 mode/range table: 9 P/Q ranges and shares carry **no sha row**, but the derivation is fully specified in adjacent prose and **all 9 reproduce exactly**.
- §4 row 1: `6,128,100` and `19,625` carry **no source, column, aggregation or sha**. Both confirmed as column sums over `data/barrier_height_long.parquet` (180 rows, sha `b9e9b404…`). **Needs a provenance row.**
- §2.4, §2.11, §2.12, §3.J `:924` figures all independently reconciled and exact.
- Three artifacts listed in §0.1 as read carry **zero** provenance rows: `data/barrier_height_long.parquet`, `data/qlimit_class.json`, `data/tuned_metrics.json`.

### 1.7 Derived claims in prose, re-checked

All confirmed except one: **"the fixed-tag ridge delta for `+F1+F3` against `+F1` is at the ninth significant figure" is WRONG — it is the seventh.** (`+F1` m2_fixed = 0.003757561472638325; `+F1+F3` m2_fixed = 0.0037575673017984693.) Also: "pooled and seed-mean differ in the fourth decimal" is true for ridge (0.56062 / 0.56126) but **histgb differs in the fifth** (0.856295 / 0.856372).

## 2. PER CITATION

All 12 keys have a `\bibitem`. The `prior-art.md:151-153` quote is exact:

> `- The §10 conformal foundations (Lei et al. 2018 JASA; Romano-Patterson-Candes 2019; Gibbs-Candes`
> `  2021; Vovk-Gammerman-Shafer 2005) were NOT re-verified in this pass - they were out of scope for`
> `  the A/B/C claim list but should be confirmed before they appear in any writeup.`

That list covers `lei2018`, `romano2019`, `vovk2005` and Gibbs–Candès 2021 — it does **not** cover `barber2021` or `tibshirani2019`, and the guide is right to separate them.

**Citation status errors found:**

1. **`barber2021` is not in the `.tex` comment at `:294-295`.** `grep -i barber` returns only `:258` (live `\cite`) and `:329` (bibitem). The guide's "the only record is the `.tex` comment at `:294-295`" is false for this key.
2. **All three "TODO" keys are already live-cited in the manuscript body** — `bates2021` at `:84`, `:258`; `barber2021` at `:258`; `tibshirani2019` at `:262`. "The only record is a comment" understates the exposure.
3. `bates2021` "no prior-art entry" is correct, but the single `grep -i bates` hit is "Bates" as a *co-author of `angelopoulos2024`* at `prior-art.md:326`.
4. `barber2021`, `tibshirani2019` zero mentions — CONFIRMED.
5. GNN comparator claims — CONFIRMED, including that the paper has **no** bibkey in the `.tex`.

**No key marked RESOLVED lacks its named support. No key marked TODO turned out to be resolved.**

## 3. PER INSERTION POINT

**Anchor confirmed:** sha256 `754be12b…21c22`, 344 lines, last touched `6082204`, `git diff HEAD` empty, HEAD `ab970c19…`. (Precise note: the file has no terminating newline, so it holds 345 newline-separated lines; this affects nothing, every insertion point is ≤ 262.)

All ten line numbers exist, all ten quoted tails are the actual tail of that line, and **no two collide** (86, 96, 141, 227, 235, 250, 256, 258, 260, 262).

**Caveat the guide should state explicitly:** F/G/H/J are four consecutive paragraph lines of one Discussion section and B/C/I are close together in Results. All ten are positions in *one* sha; applying any single one invalidates every later line number. §3.0's "Ten distinct lines, no collision" reads as if they can be applied independently. **They cannot be applied in ascending order without re-anchoring.**

Section tree (§1.2) re-derived and correct in every row. Renumbering claim correct; the single live `\ref{sec:…}` is `\ref{sec:discussion}` at `:116`.

## 4. ADVERSARIAL CHECKS

**4.1 `agg_loading` excluded — CONFIRMED.** 634 columns, 15 excluded, 619 features.

**4.2 `writing-numbers.md` — the load-bearing claim is correct, the surrounding counts are wrong:**

| quantity | guide says | verifier measures |
|---|---|---|
| rows naming a `data/` source | 83 | **87** |
| of those, carrying a stored sha16 | (implied 83) | **82** |
| stored shas that still match | 82 | **81** |
| **stored shas that no longer match** | **1** | **1** ok |

The single mismatch is `data/thermal_check.json`, stored `23d42c7146e0f580` vs current `cbeadaa2d61d9054`, and it is the **51st** sha-bearing row, confirming the "row 51" label. **Fix §0.2's arithmetic to 82 / 81 / 1.**

**4.3 k=5 headroom exactly 0.000e+00 — CONFIRMED bitwise.** Other headrooms: k=10 `0.0004551737285180546`, k=20 `0.010576642059957009`, k=50 `0.062264874944180315`, k=100 `0.024313938271384394`.

**4.4 Zero subsection labels, `\thesubsection` never redefined — CONFIRMED.** 12 labels; 7 subsections at 102, 106, 110, 118, 213, 229, 233, none labelled.

**4.5 No TeX toolchain — CONFIRMED.** All five binaries absent; `/usr/local/texlive` empty; `/Library/TeX` absent.

**4.6 Page-budget arithmetic — ONE ERROR.** Items sum to 23.35 and 23.35 − 20 = 3.35 pp over, both correct. But levers 1–6 total 0.4+0.4+0.3+0.7+0.5+0.6 = **2.9 pp**, so applying all six lands at **20.45 pp, not the stated 20.05 pp.**

**4.7 Manuscript prose in the guide — PRESENT.** The ten "Claim (one sentence)" entries are finished result sentences; defensible as claims-to-be-supported. Five others are not: §3.I's "Both abandons are load-INDEPENDENT…", §3.J's "Reproduction from a fresh net…", §3.J's "`agg_loading` is in `make_splits.EXCLUDE_COLS` and is NOT a feature…", §3.E's "Over-voltage is not inert; it is UNSCREENED.", and a full paragraph at `:924` copied verbatim from a `verdict` string. **Flagged for the author's decision; no fix applied.**

**4.8 Six further defects:**

1. §3.0 table header is `| sec | content | insertion | follows the line ending |` but column 2 holds the **line number** and column 3 the content. **Columns 2 and 3 are mislabelled in all ten rows.**
2. **E-16 is stale.** `notes/erratum.md:48-54` was already corrected on 2026-08-19 and already names tag object `23bc760` → commit `8cefaa7`. E-16 describes a defect that no longer exists, and its pointer `:46` lands two lines before the caveat block.
3. **E-10 names the wrong artifact.** The 73.14% / 73.40% over-voltage shares come from `data/dataset.parquet` (`max_vm>1.05`), not `data/thermal_check.json` — which is what §3.E's own provenance rows correctly say.
4. **Network-count inconsistency.** `run_status.json` returns **4** entries (3 COMPLETE + 1 ABANDONED) but the row is labelled "five networks attempted"; §2.8 says "five networks, two of which could not be built"; lever 6 says "the **two** completed networks" when three completed.
5. §2.11 states the count window is lines 60-290 then names comment lines `:19`, `:23`, `:150`, two of which are outside that window. (Counts themselves exact.)
6. The reconstruction note promises "PART 7 = an independent verifier pass reproduced verbatim", but the file contained only PART 1 through PART 6.

**4.9 Code, note and file pointers — all spot-checked, all correct.** Including `gate_eval.py:18/19/20/21/39`, `generate_dataset.py:136-144`/`:57`/`:168`/`:21`/`:111`/`:28`/`:128`/`:160-162`/`:164-165`/`:256`, all 53 `genp_*` columns constant, `make_splits.EXCLUDE_COLS`, `thermal_check.py:159-160`, `drift_tests.py:237`, `baselines.py:330-331`, `netstudy.py:345` ≡ `gate_eval.py:19-21`, `RUN_REPORT.md:7033-7037` void notice, `.gitignore:23`, `sts-constraints.yaml` R10 `:118-121` and R14 `:162`, `fig_identity.manifest.json` carries `apa_citation`, the `.tex` contains **zero** APA lines, `GEN_REJECTED = 1287` hardcoded at `freeze_poster_numbers.py:11`.

## 5. COULD NOT VERIFY, AND WHY

| item | reason |
|---|---|
| That every number was **read at** `ab970c1` | Reading history is not recoverable; only content agreement is checkable, and it holds. |
| §0.1's framing "artifacts **read**" | Only the shas are checkable. All 39 match. |
| The prompt-truncation account | No artifact records the originating instruction; unfalsifiable from the repo. |
| The two retired notes | Out of scope by instruction; confirmed absent only by non-appearance, not opened. |
| All word-count estimates and page figures | No TeX toolchain. Only the internal arithmetic was checkable — see 4.6. |
| Whether the `urtc-submission` tag has been **pushed** | `git ls-remote` was run for `HEAD` only; `erratum.md:53-54` itself declines to assert this. |
| Whether the ten "Claim (one sentence)" lines constitute manuscript prose | A judgment call reserved to the author; instances enumerated in 4.7. |
| The substantive correctness of ANSI 0.917 pu | `prior-art.md` §7.3 states the approved standard body text was never accessed. The guide's characterisation is exact; the number remains unverified upstream. |
| Whether `k_equivalent_mean` equals `escalation × rows_per_scenario` numerically | Not a guide claim; 91.253/186 = 0.49061 against ridge escalation 0.49070 — close, not identity. |

**Nothing else in any category was found wanting.** Specifically: **zero** provenance rows have a missing file, **zero** have a stale sha, **zero** fail to reproduce, **zero** citation keys lack a `\bibitem`, **zero** insertion points are wrong or collide, and **zero** RESOLVED keys lack their named support.

---

## 8. TALLY AND UNRESOLVED DISAGREEMENTS

### 8.1 Tally

| quantity | count |
|---|---|
| provenance-format rows in this guide (verifier's count) | **153** |
| distinct artifacts carrying a full sha256 in §0.1 | **39** |
| total table rows | **374** |
| rows two-key verified (value re-derived by an independent route) | **153 of 153** |
| rows the verifier confirmed reproduce exactly | **153 of 153** |
| rows requiring rounding to reproduce | **0** |
| rows that failed to reproduce | **0** |
| citation keys checked | **12**, all with a `\bibitem` |
| insertion points checked | **10**, all confirmed, **0** collisions |
| numbers stated WITHOUT a provenance row | **11** (9 in §2.1, 2 in §4) |
| artifacts listed as read but carrying no provenance row | **3** |

### 8.2 Disagreements, stated in full and NOT resolved

1. **Row count.** This guide's assembly counted ~135 provenance rows; the verifier counts **153**. Not reconciled.
2. **`writing-numbers.md` arithmetic.** §0.2 states 83 rows naming a `data/` source and 82 matching. The verifier measures **87** naming a source, **82** carrying a sha, **81** matching, **1** not. Both agree the mismatch count is **1** and that it is row 51. The surrounding counts in §0.2 are wrong and are left as written.
3. **Significant figures.** §3.J states the fixed-tag ridge delta for `+F1+F3` against `+F1` is at the **ninth** significant figure; the verifier measures the **seventh**. Left as written.
4. **Decimal place.** §3.B states pooled and seed-mean flag precision "differ in the fourth decimal"; true for ridge, but histgb differs in the **fifth**. Left as written.
5. **Page-budget levers.** §6.2 states applying levers 1-6 lands near **20.05 pp**; the levers sum to 2.9 pp, which lands at **20.45 pp**. Left as written.
6. **`barber2021` provenance.** §3.A states its only record is the `.tex` comment at `:294-295`; the verifier finds `barber2021` is not named in that comment block at all. Left as written.
7. **Live citation exposure.** The verifier notes all three TODO conformal keys are already live-cited in the body (`:84`, `:258`, `:262`), which the guide does not say. Not incorporated.
8. ~~Six §3.G rows omit the `converged N-1` filter; fourteen §3.J rows omit `by_target["0.9"]`.~~ **FIXED.** All six §3.G cells now read `converged N-1 whose base has n0_min_vm >=/< median` (and the two gen-outage cells name the stratum); all fourteen §3.J cells now read `by_target["0.9"] within records[...]`. **Additionally, 20 rows carried an unescaped `|` inside a cell, which broke the markdown table — the verifier parsed by content and did not see this. All are now escaped or replaced with `;`. Zero broken rows remain.**
9. ~~§3.0 column headers are mislabelled against their contents in all ten rows.~~ **FIXED.** Columns 2 and 3 were transposed by a tuple-unpacking error in the generator. All ten rows now read `sec | content | after <line> | tail`; the H row reads `replaces 260 in place`.
10. ~~E-16 is stale; E-10 names the wrong artifact.~~ **FIXED, and the verifier is half wrong.** E-16: confirmed stale from source — `notes/erratum.md:48-54` already reads "**That is no longer true.**" and names `23bc760` -> `8cefaa7`; E-16 is now struck through and marked WITHDRAWN, no erratum owed. E-10: **the verifier's finding does not hold.** `data/thermal_check.json` DOES carry both shares, at `networks.case118.overvoltage.n1.share_above_1p05` = 0.7313581043537488 and `...n0_base.share_above_1p05` = 0.734, and names `data/dataset.parquet` as its own input at `networks.case118.overvoltage.dataset`. The artifact was right; the missing jsonpath was the defect, and it has been supplied. **This disagreement with the verifier is recorded, not resolved in the verifier's favour.**
11. ~~Network counts are inconsistent across §3.I, §2.8 and §6.2 lever 6.~~ **FIXED.** A convention is now fixed in §3.I and derived from source: **five attempted** = the union of `data/netstudy/run_status.json` and `data/netstudy2/run_status.json`; **three completed** (case39, case24_ieee_rts, case_illinois200); **two abandoned** (case57 under v1, case89pegase under v2). The §3.I provenance row is relabelled "netstudy v2 (4 networks)" because that file alone does not carry case57. §6.2 lever 6 corrected from two to three completed networks.
12. **§2.11** names three comment lines, two of which fall outside its own stated 60-290 window. Counts exact. Not fixed.
13. **Insertion-point independence.** The verifier requires an explicit statement that the ten points cannot be applied in ascending order without re-anchoring. §3.0 does not say this. Not added.
14. ~~Manuscript prose: five passages beyond the ten "Claim" lines.~~ **FIXED.** All five were deleted and replaced with specifications of what must be true — in §3.E (over-voltage/thermal scope), §3.I (the two abandons), §3.J (design-matrix contents), §3.J (the F1 leakage audit) and §3.J (the LODF fill, now pointing at the artifact's jsonpath instead of quoting its verdict string). **The ten "Claim (one sentence)" entries are kept, as instructed.**

### 8.2b Fix pass, 2026-08-20

Four defects and the prose finding were fixed on instruction; the diff is summarised at the end
of this section. **Items 1-7, 12 and 13 above remain UNRESOLVED and are left as written**, namely:
the 135-vs-153 row count, the §0.2 arithmetic (82/81/1), the seventh-not-ninth significant
figure, the fourth-vs-fifth decimal, the `barber2021` comment provenance, the live-citation
exposure of the three TODO conformal keys, the §2.11 window mismatch, and the missing statement
that insertion points cannot be applied in ascending order without re-anchoring. **Ten findings
stand open.**

### 8.3 What this means for use

Every number in this guide reproduces from its named artifact. **No number is wrong**, and the
fix pass changed no value — it changed provenance cells, column order, two errata, a counting
convention, the page-budget arithmetic, and five passages of prose. The ten open findings in
§8.2 are all statements ABOUT the guide rather than errors in its numbers; none of them

---

## PART 9 — CUT FOR BUDGET

Five sections are cut. **No specification is deleted.** A sixth, 3.J, was cut on
2026-08-23 and RESTORED to PART 3 on 2026-08-24; it no longer appears here. Each is
reproduced verbatim below with its provenance table intact — value, source, jsonpath,
aggregation and sha unchanged — preceded by three statements: what claim is lost, whether a
surviving section depends on it, and where its content must be relocated.

**These are cuts, not retractions.** Every artifact still exists and every row is still true.
A claim listed as LOST is one the manuscript may no longer make, not one that has been
disproved. **Restoring any section requires restoring its words to 6.2's budget table.**

**Total cut: ~2,770 words, 2 tables and 1 figure** — five sections (3.B 450, 3.C 200, 3.E 220,
3.F 250, 3.G 500 = 1,620 words) plus 3.A's 600-word reduction and its figure, 3.I's table, and
3.D's 550-word reduction and its table. At 345 w/p that is about **8.0 pp**.

**BOOKKEEPING CORRECTED 2026-08-24 along with 3.J's restoration.** The previous tally read
"~2,900 words and 1 table" and counted 3.J's 400 words among the cuts. 3.J is now active, and
the table count was understated — 3.D's comparison table and 3.I's per-network table are two,
not one. **No provenance value changed; this is a count of what is cut, not a measurement.**

### 9.1 CUT — 3.B, the flag branch

**CLAIM LOST:** that the flag decision reads only the point prediction and is therefore
invariant to the coverage target; that the conformal guarantee constrains certification only;
and that false flags are never corrected downstream. **Also lost: every flag-precision and
false-flag-margin number.**

**DEPENDENCY: NONE of the four surviving sections depends on it.** 3.A states the gate
definition it would have drawn on, and states it independently from
`feasibility/gate_eval.py:18-20`.

**RELOCATION: none, and this is the most expensive cut.** The claim that the conformal
guarantee constrains certification ONLY is a scope limit on the whole method, and with 3.B gone
nothing states it. **Guard: no surviving text may describe the band as governing the flag
branch.** 3.A's identity covers certification and escalation only — verify that its wording does
not imply otherwise. **This is the first claim to restore from 6.2's unspent 145-word headroom**;
one sentence naming `flag = pred < limit` and its target-invariance would discharge it at about
40 words.

### 3.B Results — the flag branch

**Insertion:** after 227. **`\label`:** `\label{subsec:flag}`.

**Claim (one sentence):** The flag decision reads only the point prediction, so it is invariant
to the coverage target, the conformal guarantee constrains certification only, and false flags
are never corrected downstream.

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| max nunique of flag columns per (model,seed) group | `1` | `data/flag_confusion_long.parquet` | `groupby(model,seed).nunique()` | max over 10 groups | `2ef84483e67518da` |
| coverage targets swept | `30` | `data/flag_confusion_long.parquet` | `target` | nunique | `2ef84483e67518da` |
| flag precision ridge@0.94 count-pooled | `0.5606201196271288` | `data/flag_confusion_long.parquet` | `sum(flag_viol)/sum(flag_viol+flag_safe)` | count-pooled | `2ef84483e67518da` |
| flag precision ridge@0.94 seed-mean | `0.561264511296313` | `data/flag_confusion_long.parquet` | `flag_precision` | seed-mean | `2ef84483e67518da` |
| flag precision histgb@0.97 count-pooled | `0.8562945368171021` | `data/flag_confusion_long.parquet` | `sum(flag_viol)/sum(flag_viol+flag_safe)` | count-pooled | `2ef84483e67518da` |
| flag precision histgb@0.97 seed-mean | `0.856371929696882` | `data/flag_confusion_long.parquet` | `flag_precision` | seed-mean | `2ef84483e67518da` |
| flag ceiling ridge | `0.691481920315199` | `data/flag_confusion_long.parquet` | `sum(n_viol)/sum(flag_viol+flag_safe)` | count-pooled | `2ef84483e67518da` |
| flag ceiling histgb | `1.009271992332375` | `data/flag_confusion_long.parquet` | `sum(n_viol)/sum(flag_viol+flag_safe)` | count-pooled | `2ef84483e67518da` |
| false flags ridge@0.94 | `6155.8` | `data/flag_confusion_long.parquet` | `flag_safe` | seed-mean | `2ef84483e67518da` |
| missed violations ridge@0.94 | `76.8` | `data/flag_confusion_long.parquet` | `missed_viol_rate*n_viol` | seed-mean | `2ef84483e67518da` |
| false flags histgb@0.97 | `1379.4` | `data/flag_confusion_long.parquet` | `flag_safe` | seed-mean | `2ef84483e67518da` |
| missed violations histgb@0.97 | `80.8` | `data/flag_confusion_long.parquet` | `missed_viol_rate*n_viol` | seed-mean | `2ef84483e67518da` |
| false-flag margin p50 ridge@0.94 (pu) | `0.0017661206200870639` | `data/flag_confusion_long.parquet` | `ff_margin_p50` | seed-mean | `2ef84483e67518da` |
| false-flag margin p50 histgb@0.97 (pu) | `0.0009450433600094899` | `data/flag_confusion_long.parquet` | `ff_margin_p50` | seed-mean | `2ef84483e67518da` |
| share within 5 milli-pu, ridge@0.94 | `0.8966875951906849` | `data/flag_confusion_long.parquet` | `ff_share_within_0p005` | seed-mean | `2ef84483e67518da` |
| share within 5 milli-pu, histgb@0.97 | `0.9726282660280823` | `data/flag_confusion_long.parquet` | `ff_share_within_0p005` | seed-mean | `2ef84483e67518da` |

The deciding line is `feasibility/gate_eval.py:20`, `flag = pred < limit`, with no `q_hat`
term; `:18` is `lower`, `:19` is `certify`. **State which aggregation is quoted** — pooled and
seed-mean differ in the fourth decimal. The histgb ceiling exceeds 1, meaning the flag rate
sits below the violation base rate and the ceiling is non-binding.

**CANNOT BE COMPUTED:** pooled percentiles of false-flag margins. The artifact stores only
p50/p90/max/mean per seed; raw margins are not retained.

**Citations:** none new. **Figure/table:** none required. **Estimate: ~450 words, ~1.2 pp.**

### 9.2 CUT — 3.C, non-convergence

**CLAIM LOST:** that the gate escalates or flags essentially all 45 non-converged solves, and
that treating every one as a violation moves the missed rate by less than 0.0001. **The
disposition of the 45 is lost. The count itself is not.**

**DEPENDENCY: YES — PART 2 item 1 depends on the count**, which is why the count survives and
the disposition does not.

**RELOCATION — MANDATORY, and specified here.** III-A's corrected sentence at `:104` carries the
45. PART 2 item 1 already requires: "state per-load P and Q support separately by mode, name the
denominator for every share, state that generator real power is never scaled, **and give 45 as
the failure count**." That requirement is unchanged and now does double duty.

**HOW III-A CARRIES THEM — the corrected sentence must state all three parts:**
1. the arithmetic, `1,545 = 1,500 + 45`, naming the 1,500 as N-0 base rows excluded **by design**
   and the 45 as **genuine solver failures**;
2. that the 45 are excluded from every gate metric reported in the paper;
3. **nothing about their disposition.**

**GUARD, and it is the point of this entry: with 3.C cut, the manuscript MAY NOT claim the 45 are
immaterial.** The sentence "treating them as violations changes nothing" is exactly what 3.C
existed to support, and its evidence — the per-seed missed-rate deltas and the certified counts
— is no longer in the paper. State the count and the exclusion; make no claim about the effect.
The rows below are retained so the claim can be restored if a reviewer asks whether 45 excluded
failures could flip a sub-1% missed rate. **They cannot, but the paper will no longer show it.**

### 3.C Results — non-convergence

**Insertion:** after 235, inside the boundary-layer subsection, before the Fig. 4 float at 241.

**Claim (one sentence):** Forty-five N-1 solves failed to converge, the gate escalates or flags
essentially all of them, and treating every one as a violation moves the missed rate by less
than 0.0001.

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| genuine solver failures | `45` | `data/nonconverged_gate.json` | `n_nonconverged` | count | `17b42095584c94a0` |
| N-0 base rows excluded by design | `1500` | `data/nonconverged_gate.json` | `n_base_rows_excluded_by_design` | count | `17b42095584c94a0` |
| failing elements and counts (0-based trafo idx) | `[['trafo_0', 37], ['trafo_7', 7], ['trafo_6', 1]]` | `data/nonconverged_gate.json` | `q3_top_elements` | count | `17b42095584c94a0` |
| certified of 45x5 seed-rows, ridge@0.94 | `0` | `data/nonconverged_gate.json` | `q1_q2_per_seed.ridge.target_0.94.all45.certified` | sum over 5 seeds | `17b42095584c94a0` |
| certified of 45x5 seed-rows, histgb@0.97 | `1` | `data/nonconverged_gate.json` | `q1_q2_per_seed.histgb.target_0.97.all45.certified` | sum over 5 seeds | `17b42095584c94a0` |
| missed-rate delta, ridge@0.94 | `-8.434263776042894e-06` | `data/nonconverged_gate.json` | `target_0.94 missed_rate_if_nc_are_violations - published` | seed-mean | `17b42095584c94a0` |
| missed-rate delta, histgb@0.97 | `1.1975987507569474e-05` | `data/nonconverged_gate.json` | `target_0.97 missed_rate_if_nc_are_violations - published` | seed-mean | `17b42095584c94a0` |
| largest per-seed \|delta\|, histgb@0.97 | `9.766500934411601e-05` | `data/nonconverged_gate.json` | `same` | max abs per-seed | `17b42095584c94a0` |

**The four-decimal claim is aggregation-dependent.** The seed-MEAN delta rounds to 0.0000 for
both families, but one histgb seed reaches 9.8e-05, which rounds to 0.0001 at four decimals.
Write the bound as 'below 0.0001' on the per-seed maximum, or state the seed-mean explicitly.

Trafo indices are 0-based in the artifact; IEEE names are 1/8/7. **Citations:** none.
**Estimate: ~200 words, ~0.5 pp.**
### 9.3 CUT — 3.E, Background NERC/ANSI grounding

**CLAIM LOST:** that the 0.94 pu floor is conservative relative to the ANSI C84.1 Range B
service limit and is not itself a NERC requirement. **With 3.E gone the 0.94 pu floor is stated
without external grounding.** That is acceptable — 0.94 is structural, set at
`feasibility/generate_dataset.py:256` — but no sentence may imply a standards basis for it.

**DEPENDENCY: YES, one, and it is the reason for the mandatory relocation below.** 3.E was the
home of the `:92` over-voltage correction. Nothing else depends on 3.E.

**RELOCATION 1 — MANDATORY. The `:92` over-voltage correction becomes a line-level correction,
executed with the PART 2 set as item 2 of 6.1.** It needs no host section: `:92` claims the lower
voltage limit is the only active constraint, and the claim is false on this dataset. The
correction is an in-place rewrite of that sentence carrying three things:
1. **`73.14%`** of converged N-1 rows sit above 1.05 pu, and **`73.4%`** of N-0 base rows do —
   both from `data/dataset.parquet`, sha `8f0fd1081c8603e8`;
2. over-voltage is therefore a **SCOPE decision**, not an absent phenomenon;
3. thermal is **UNDEFINED on case118** — ratings are placeholders, transformer `sn_mva` uniform
   at `9,900` — so its omission is **not a property of the network**.

**Net cost: ~25 words**, budgeted in 6.2. **This correction is mandatory regardless of budget:
`:92` is currently false, and a false scope statement is a defect, not a length choice.**

**RELOCATION 2 — the ANSI provenance defect moves to 3.H**, which already owns `:260` where
`ansi2020` is cited. See 3.H. Word-neutral.

**What is NOT relocated:** the NERC grounding. `nerc` still has **zero entries of any kind in
`notes/prior-art.md`** — `prior-art.md` section 8's scope note excludes it, and the primary PDF
returned HTTP 403 on both paths. **Cutting 3.E removes the only section that would have required
that record, so the `nerc` citation at `:82` is now the sole exposure.** It stays cited for the
N-1 criterion, a claim the standard certainly makes but which nobody here has read the body to
confirm. **Flag it in PART 8, not here.**

### 3.E Background — NERC/ANSI grounding

**Insertion:** after 96, before `\section{Method}` at 99. Extend `\label{sec:background}`; no
new label.

**Claim (one sentence):** The 0.94 pu screening floor is a conservative choice relative to the
ANSI C84.1 Range B service limit and is not itself a NERC requirement.

**Numbers:** 0.94 pu is structural. **0.917 pu carries the provenance defect in PART 2 item 9
and must not be cited to the approved standard.**

**This section must also correct `:92`.** The claim that the lower voltage limit is the only
active constraint does not hold on this dataset:

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| share of converged N-1 rows above 1.05 pu | `0.7313581043537488` | `data/dataset.parquet` | `max_vm>1.05 ; converged N-1` | raw | `8f0fd1081c8603e8` |
| share of N-0 base rows above 1.05 pu | `0.734` | `data/dataset.parquet` | `max_vm>1.05 ; base rows` | raw | `8f0fd1081c8603e8` |
| case118 line rating verdict | `UNDEFINED (rating populated but PLACEHOLDER)` | `data/thermal_check.json` | `networks.case118.rating_audit.line_verdict` | raw | `cbeadaa2d61d9054` |
| case118 transformer sn_mva (uniform) | `9900.0` | `data/thermal_check.json` | `...trafo_sn_mva.max` | raw | `cbeadaa2d61d9054` |

**REQUIRED of this section:** state which constraint families this study screens and which it
does not, and classify each omission as a SCOPE decision or a physics finding. The two
over-voltage shares above are the measured basis for that classification. For thermal, state
that no thermal predicate is defined on case118, citing the rating verdict and the uniform
`sn_mva` rows above, and do not describe the omission as a property of the network.

**Citations:** `nerc` **TODO — zero entries of any kind in `notes/prior-art.md`**, and the
`.tex` comment at `:299-300` admits it. `ansi2020` **RESOLVED for bibliographic identity only**
— `prior-art.md` section 7.3 confirms the title block from NEMA's free front matter and states
the numeric Range B value was NOT verified against the approved standard.

**Figure/table:** none. **Estimate: ~220 words, ~0.6 pp.**

### 9.4 CUT — 3.F, break-even and parallelism

**CLAIM LOST:** the amortisation threshold — that the gate must screen roughly `786,904`
contingencies (`gen_only` basis) before it repays the cost of generating its own training set —
and the parallelism-invariance point. **Equation 2's cost model is therefore stated at `:84` and
never closed out.**

**DEPENDENCY: NONE.** No surviving section quotes a break-even number.

**RELOCATION: none, and no compressed form is offered.** A one-clause version would have to pick
one of four cost bases, and `notes/writing-numbers.md` F.3 records that the search-inclusive
basis nearly doubles the answer (`8,037` scenarios against `4,231`). **A single unqualified
break-even number is worse than none.** If the headroom in 6.2 is ever spent here, it must name
its basis.

**GUARD: with 3.F cut, no surviving text may claim the gate "pays for itself."** The speedup
numbers in the existing Results measure per-case screening cost only and do not amortise dataset
generation. That distinction was 3.F's job. **Verify that `:84` and the Conclusion do not imply
end-to-end net saving.**

**Housekeeping: the `notes/writing-numbers.md` rows this section was blocked on were added
2026-08-21** (section F.1-F.4: `ms_solver`, `solves_recorded_in_dataset`,
`t_generation_s_recorded`, the full `ridge.gen_only` block, and the disclosure rows). **They are
now unused by any surviving section. Do not delete them** — they are correct, two-keyed, and the
cheapest thing to restore.

### 3.F Discussion — break-even and parallelism

**Insertion:** after 256.

**Claim (one sentence):** Equation 2 charges escalated solves but not the solves that built the
dataset, the amortisation threshold is stated here, and the speedup claim is invariant to
parallelism only under a stated assumption.

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| solver time per case | `9.14` | `data/solve_time.json` | `ms_solver` | min over 400 timed solves | `94d8e8059d2b3526` |
| solves recorded in the dataset | `280500` | `data/break_even.json` | `generation.solves_recorded_in_dataset` | count | `0d4266967a611d2a` |
| recorded generation time (s) | `2563.77` | `data/break_even.json` | `generation.t_generation_s_recorded` | raw | `0d4266967a611d2a` |
| ridge break-even at its operating point, generation cost only | `{'target': 0.94, 'escalation': 0.6434123029630445, 'saving_ms_per_case': 3.2580487700032297, 'one_time_cost_s': 2563.77, 'break_even_cases': 786903.5060507883, 'break_even_scenarios': 4230.664011025744}` | `data/break_even.json` | `break_even_at_operating_points.ridge.gen_only` | raw | `0d4266967a611d2a` |
| best measured parallel configuration | `{'n_workers': 10, 'effective_ms_per_case': 1.8675689245524105, 'speedup': 5.3984555430992, 'efficiency': 0.53984555430992}` | `data/parallel_speedup.json` | `best_parallel` | mean over 930 solves/config | `fd2ecbdb8f16a7af` |

**TWO PROVENANCE DEFECTS THAT MUST BE DISCLOSED IF THESE NUMBERS ARE USED:**

- Rejected-scenario count: `GEN_REJECTED is a hardcoded constant in feasibility/freeze_poster_numbers.py whose stated source is a generate_dataset.py run log that is NOT a committed file. The rejected-scenario count is therefore unverifiable from the repo.`
- Parallel hardware: `the manifest hardware block records machine/processor/system/release/cpu but NOT core count, thread count, or whether the solve was single-threaded. Core count below is measured on the machine running this benchmark and is NOT evidence about the machine that produced ms_solver=9.14.`

**NOT YET IN `notes/writing-numbers.md`:** every `data/break_even.json` row AND the
`ms_solver` row. Both must be added before drafting. The comparator in the same artifact is a
GNN break-even read from a lit note in SCENARIOS while this project's is in screened
CONTINGENCIES; the artifact states the unit mismatch and it must not be elided.

**Citations:** `manoharan2026` RESOLVED. **Estimate: ~250 words, ~0.7 pp.**
### 9.5 CUT — 3.G, drift

**CLAIM LOST:** that calibrating on benign base cases and screening marginal ones costs the
linear model about ten coverage points while the boosted model is unaffected, and that the
deciding cell shows this is calibration/test MISMATCH rather than stratum difficulty. **Also
lost: the element-type shift (2D) and the loading-tilt weighted-conformal experiment (2E).**

**DEPENDENCY: YES, and it is a citation dependency, not a claim dependency.** 3.A's guarantee is
stated without a drift caveat; 3.G was to supply the limitation. **Guard: 3.A must not overstate
the guarantee's reach.** One clause noting that coverage is measured under the calibration
distribution is sufficient and is already inside 3.A's 300 words.

**RELOCATION: none for the drift results.** 2C, 2D and 2E all go. The three-cell design is the
whole argument and does not compress to a clause without becoming an unsupported assertion.

**`tibshirani2019` — THE CITATION NOW HAS NO HOME. IT MUST BE DROPPED FROM `:262` WITH NO
REPLACEMENT HOME.** The chain: `prior-art.md` 8.7 found `tibshirani2019` cited at `:262` as
authority that conformal prediction REQUIRES exchangeability, whereas the paper's contribution is
the RELAXATION — weighted conformal valid under covariate shift. Its correct home was this
section's 2E block, the only place in the project where weighted calibration is actually used.
**With 3.G cut, that home no longer exists.** Therefore:

1. **Drop `\cite{tibshirani2019}` from `:262`.** It is the sole cite site — verified by parsing
   the `.tex`.
2. **Re-source the exchangeability requirement at `:262` to `vovk2005`**, already in the
   bibliography and already cited at `:112`. Conformal validity under exchangeability is that
   book's central premise. `lei2018` is the second candidate but is carrying `:112` twice
   already, and `prior-art.md` 8.5 records that its body was never read.
3. **`tibshirani2019` then becomes an uncited `\bibitem`.** Remove it and set
   `\begin{thebibliography}{18}`. This is step 4 of 6.1. **The citation gate WARNs on uncited
   bibitems and FAILs on a width mismatch — both would fire if step 3 is skipped.**

**This is a genuine loss and should be recorded as one.** The project ran a weighted-conformal
experiment, and at this budget the manuscript neither reports it nor cites the method.

### 3.G Discussion — drift

**Insertion:** after 258.

**Claim (one sentence):** Calibrating on benign base cases and screening marginal ones costs
the linear model about ten coverage points while the boosted model is unaffected, and the
deciding cell shows this is calibration/test MISMATCH, not stratum difficulty.

**2C IS A DRIFT FINDING, NOT A CONFOUND.** Cell (c) holds stratum difficulty fixed and removes
only the mismatch; ridge still drops.

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| (a) ridge SHIFTED: cal benign -> test marginal @0.90 | `{'cov': 0.7952977736840497, 'std': 0.017998553298487808, 'esc': 0.43399563412808817}` | `data/drift_n0_stratum_long.parquet` | `coverage_emp ; model=ridge,cal=benign,test=marginal,target=0.90` | seed-mean/std ddof=0 | `97c8ef7aa40c4e97` |
| (b) ridge BENIGN CONTROL @0.90 | `{'cov': 0.8963930839821412, 'std': 0.011400530217031263, 'esc': 0.3318449880802842}` | `data/drift_n0_stratum_long.parquet` | `coverage_emp ; model=ridge,cal=benign,test=benign,target=0.90` | seed-mean/std ddof=0 | `97c8ef7aa40c4e97` |
| (c) ridge IN-DISTRIBUTION MARGINAL @0.90 | `{'cov': 0.8844348119083406, 'std': 0.026846519782127615, 'esc': 0.561742812419088}` | `data/drift_n0_stratum_long.parquet` | `coverage_emp ; model=ridge,cal=marginal,test=marginal,target=0.90` | seed-mean/std ddof=0 | `97c8ef7aa40c4e97` |
| histgb shifted @0.90 | `{'cov': 0.8959887824104488, 'std': 0.00505860700222826, 'esc': 0.5370570578461142}` | `data/drift_n0_stratum_long.parquet` | `coverage_emp ; model=histgb,cal=benign,test=marginal,target=0.90` | seed-mean/std ddof=0 | `97c8ef7aa40c4e97` |
| histgb benign control @0.90 | `{'cov': 0.8931207052512539, 'std': 0.015194812284911343, 'esc': 0.028453664038776548}` | `data/drift_n0_stratum_long.parquet` | `coverage_emp ; model=histgb,cal=benign,test=benign,target=0.90` | seed-mean/std ddof=0 | `97c8ef7aa40c4e97` |
| histgb in-distribution marginal @0.90 | `{'cov': 0.9034167252170316, 'std': 0.00959002909673717, 'esc': 0.5914081281701327}` | `data/drift_n0_stratum_long.parquet` | `coverage_emp ; model=histgb,cal=marginal,test=marginal,target=0.90` | seed-mean/std ddof=0 | `97c8ef7aa40c4e97` |
| median split point on n0_min_vm | `0.9433575252264039` | `data/dataset.parquet` | `n0_min_vm` | median over all rows | `8f0fd1081c8603e8` |
| benign stratum violation rate | `0.15373696096354447` | `data/dataset.parquet` | `min_vm<0.94 ; converged N-1 whose base has n0_min_vm>=median` | raw | `8f0fd1081c8603e8` |
| benign stratum rows | `139485` | `data/dataset.parquet` | `converged N-1 whose base has n0_min_vm>=median` | count | `8f0fd1081c8603e8` |
| marginal stratum violation rate | `0.19577686957768695` | `data/dataset.parquet` | `min_vm<0.94 ; converged N-1 whose base has n0_min_vm<median` | raw | `8f0fd1081c8603e8` |
| marginal stratum rows | `139470` | `data/dataset.parquet` | `converged N-1 whose base has n0_min_vm<median` | count | `8f0fd1081c8603e8` |
| gen-outage prevalence, benign stratum | `0.22528587303294262` | `data/dataset.parquet` | `gen_out>=0 ; converged N-1, benign stratum` | raw | `8f0fd1081c8603e8` |
| gen-outage prevalence, marginal stratum | `0.27323438732343874` | `data/dataset.parquet` | `gen_out>=0 ; converged N-1, marginal stratum` | raw | `8f0fd1081c8603e8` |
| corr(n0_min_vm, agg_loading) over base rows | `-0.0723904338296946` | `data/dataset.parquet` | `corr over base rows` | raw | `8f0fd1081c8603e8` |

**THE MODEL CONTRAST MUST BE ON ESCALATION, NOT COVERAGE.** histgb has no coverage gap in
either comparison; its stratum sensitivity appears as escalation, from the benign control to
the in-distribution marginal cell. Both escalation figures are in the `esc` field of the rows
above.

**SINGLE-PATH:** the two stratum violation rates are derivable ONLY from
`data/dataset.parquet`. `data/drift_n0_stratum_long.parquet` carries no violation-rate field.
Cite the dataset, not the drift artifact.

**Do NOT claim the strata differ in load level** — the correlation above is effectively zero.

**2D, element-type shift:**

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| histgb line->trafo shortfall | `0.02281042403482064` | `data/drift_element_type_long.parquet` | `mean(target-coverage_emp)` | seed+target mean | `58bd35de57f96c58` |
| histgb line->line control | `-0.0014254335260115703` | `data/drift_element_type_long.parquet` | `mean(target-coverage_emp)` | seed+target mean | `58bd35de57f96c58` |
| ridge line->trafo | `0.0037759335639549986` | `data/drift_element_type_long.parquet` | `mean(target-coverage_emp)` | seed+target mean | `58bd35de57f96c58` |
| ridge line->line control | `0.00593114964675658` | `data/drift_element_type_long.parquet` | `mean(target-coverage_emp)` | seed+target mean | `58bd35de57f96c58` |

**2E, loading tilt — UNDER-POWERED BY CONSTRUCTION:**

| quantity | value | source file | jsonpath / column | aggregation | sha256(16) |
|---|---|---|---|---|---|
| effective sample size fraction, range over all cells | `[0.7893723143295119, 0.8220457778183725]` | `data/drift_loading_tilt_long.parquet` | `ess_fraction` | min/max | `3c744f658e5a3973` |
| ridge tilted test, weighted cal | `0.003815958682152921` | `data/drift_loading_tilt_long.parquet` | `mean(target-coverage_emp)` | seed+target mean | `3c744f658e5a3973` |
| ridge tilted test, unweighted cal | `0.004624193051439177` | `data/drift_loading_tilt_long.parquet` | `mean(target-coverage_emp)` | seed+target mean | `3c744f658e5a3973` |
| histgb tilted test, weighted cal | `-0.002060867015001681` | `data/drift_loading_tilt_long.parquet` | `mean(target-coverage_emp)` | seed+target mean | `3c744f658e5a3973` |
| histgb tilted test, unweighted cal | `0.0006243005235913087` | `data/drift_loading_tilt_long.parquet` | `mean(target-coverage_emp)` | seed+target mean | `3c744f658e5a3973` |

**DO NOT QUOTE A WINDOW WIDTH FOR 2E.** A '7.7 pp' figure circulated in session notes; it
appears in no artifact and is WITHDRAWN. **Do not quote `realized_mean_agg_test` or
`realized_mean_agg_cal`** — `notes/writing-numbers.md` records both as defective reporting
columns (`scripts/drift_tests.py:237` applies the tilted index to all three cells). Coverage,
escalation, missed and speedup are unaffected.

**Citations:** `tibshirani2019` for weighted conformal — **TODO**, zero mentions in
`notes/prior-art.md`, no lit note. **Estimate: ~500 words, ~1.3 pp.**

---

---

## PART 10 — COMPLIANCE (STS 2027)

**GROUNDED.** Every rule below was re-fetched and re-verified **2026-08-27** from primary sources.
Nothing here is inferred from the finalist papers; nothing here is inferred from a rubric, because
**no rubric is published** — see 10.7.

**Sources, with fetch dates:**

| doc | URL | fetched | pages |
|---|---|---|---|
| Research Report Guidelines, STS 2027 | `sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Research-Report-Guidelines.pdf` | 2026-08-27 | 2 |
| Official Rules & Entry Instructions, STS 2027 | `sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Official-Rules.pdf` | 2026-08-27 | 50 |

**RE-VERIFICATION RESULT: NO DISCREPANCY.** Rules 2, 4b, 4e, 5b, 5c, 5e and 5f read **verbatim
identical** to what `notes/finalist-paper-analysis.md` §1.3 records. That section stands unamended.

**ONE THING §1.3 GOT WRONG BY OMISSION, corrected here — see 10.6.** §1.3 read rule 1 as a flat
prohibition on generative AI. **Appendix 4 of the Official Rules (p.34) is a graded table, not a
prohibition**, and several permitted uses *require* a prompt log. §1.3 never saw Appendix 4
because it only fetched the two-page Guidelines. **10.6 supersedes §1.3's R5 reading.**

### 10.1 The float-citation rule — GROUNDED, Rule 2 + Appendix 3

**Rule 2, Research Report Guidelines, verbatim:**
> "Every single image, graph, table, chart, etc. that appears in the Research Report must be cited
> per the Citation Guide in Appendix 3 on page 33. This includes images created by the Student
> Researcher. Failure to cite an image could result in disqualification."

**Appendix 3, Official Rules p.33, "APPENDIX 3: CITATION GUIDE", verbatim, the parts that bind:**
> "Regeneron STS entrants are required to properly cite ALL graphics that appear within their
> Research Reports. This includes all graphics created by the finalist or their lab and all
> graphics borrowed from any other source… Please be aware that improper citation of graphics is
> grounds for disqualification."

> "ALL Graphics that appear within the Research Report must be cited, in full, **under or next to
> each individual graphic. Reference lists are not permitted for graphics.**"

> "'Graphics' includes any figure, table, graph, chart, photography, logo, etc. that is referenced
> within the paper."

> "All graphics created by the finalist need to be cited."

> "APA style citations are preferred."

**"How To Cite Graphics Created by the Student Researcher", verbatim — this is the governing
sub-rule for all six floats:**
> "Be sure to include mention that you, the student researcher, created the image."

> "If you used third-party software (including but not limited to BioRender, Canva, Microsoft
> Powerpoint, R, etc.) to create your image, you need to mention the name of the program."

> "Always mention the year the graphic was created."

> "EXAMPLE: Graph created by the student researcher using BioRender, 2024."

**The required format is therefore three obligatory elements plus placement. Not inferred — each
is a separate bullet in Appendix 3:** (i) attribution to the student researcher, (ii) the name of
the creating program, (iii) the year of creation; placed **under or next to the graphic**, never
in a reference list.

### 10.2 Every float, its artifact, and its manifest state

Line ranges from `report/paper_current_STS.tex`, re-derived this session by parsing the `.tex`.

| # | env | lines | label | graphic / source | generating script | manifest | `apa_citation` |
|---|---|---|---|---|---|---|---|
| 1 | figure | 136-141 | `fig:gate` | `data/gate_schematic_v2.png` | `feasibility/gate_schematic.py` (per erratum E1) | **NONE** | **ABSENT** |
| 2 | table | 154-169 | `tab:models` | `tabular`, no image file | typeset from result JSON | n/a | **ABSENT** |
| 3 | table | 176-200 | `tab:ops` | `tabular`, no image file | typeset from result JSON | n/a | **ABSENT** |
| 4 | figure | 206-211 | `fig:tradeoff` | `data/tradeoff_hero_col_v2.png` | **NOT LOCATED** in `feasibility/` or `scripts/` | **NONE** | **ABSENT** |
| 5 | figure | 222-227 | `fig:missdepth` | `data/miss_depth_v2.png` | `scripts/miss_depth_fig.py` | **YES** | **ABSENT — no such key** |
| 6 | figure | 241-246 | `fig:boundary` | `data/boundary_mass_hist.png` | `feasibility/boundary_mass_hist.py` | **NONE** | **ABSENT** |

**FLOATS CURRENTLY CARRYING A CITATION LINE: ZERO of six.** Detector: `created by | Graph created |
Figure created | student researcher | Note. | Adapted from`, case-insensitive, over the whole
`.tex`. Zero matches.

**THE GUIDE HAS BEEN ASSUMING A FIELD THAT DOES NOT EXIST ON THESE FIGURES.** §3.A states "the
manifest carries `apa_citation`". That is true for `data/fig_identity.manifest.json` and
`data/fig_floor.manifest.json` — **neither of which is in the paper.** Of the four figures that
ARE in the paper, three have **no manifest at all** and the fourth has a manifest without the key.

**AND THE EXISTING `apa_citation` VALUES WOULD NOT SATISFY APPENDIX 3 ANYWAY.** Both read a full
APA reference to Matplotlib (Hunter, 2007). That names the program — Appendix 3 bullet (ii) — but
carries **neither the student-researcher attribution (i) nor the year of creation (iii)**. A
figure citation copied from those manifests would still be non-compliant.

### 10.3 Per-float specification — what the citation line must contain, and where

**Specification only. No text is written here; the sentences are the author's.**

**Placement, all six:** immediately **after** the `\caption{...}` content, inside the same float,
before `\label`. Appendix 3 requires "under or next to each individual graphic"; putting it inside
the caption satisfies "under" and survives float repositioning. **It may not go in the
bibliography** — "Reference lists are not permitted for graphics."

**Floats 1, 4, 5, 6 (the four PNGs) — each line must contain:**
1. an explicit statement that the **student researcher** created the graphic;
2. the **name of the program** that produced it — for floats 5 and 6 that is the plotting library
   named in the generating script's own imports, read from the script, not assumed;
3. the **year the graphic was created** — take it from the manifest's `git_commit` date or the
   artifact mtime, not from the current year;
4. for float 1 only: the figure is a **schematic**, not a data plot, and erratum **E1** records
   that the committed `v2` is sized from the M1 band while the paper's numbers are M2. **The
   citation line does not fix E1 and must not be written as though it does.** Resolve E1 first, or
   the citation will attribute a known-defective figure.

**Floats 2 and 3 (the two tables) — Appendix 3's "Graphics" explicitly includes tables.** Each
line must contain items 1-3 above, and in place of a plotting program must **name the artifact the
values were read from**, so the table is traceable to a `sha256`-carrying file the way every
`writing-numbers.md` row is.

**WHAT MUST NOT APPEAR:** a bare software reference with no student attribution (see 10.2); a
shared citation covering more than one float — Appendix 3 says "each individual graphic"; any
`\url` inside the line, which would violate rule 5e (10.5).

**WORD COST.** Appendix 3's own example is **9 words**. Allowing for the artifact name on tables
and a longer program name: **~12 words per float × 6 floats = ~72 words.** If instead the full APA
software reference is repeated under each float, the cost is **~120 words**. **The short form is
specified**; Appendix 3's example is itself the short form, and rule 5a permits smaller caption
type ("Captions may be smaller if legible"), so the cost lands inside the caption budget.

### 10.3b RESOLVED ELEMENTS PER GRAPHIC — regeneration pass 2026-08-27

**All three Appendix 3 elements are now sourced for every graphic in the paper. NOTHING IS
NO SOURCE.** Two figures were regenerated and verified byte-identical; two Schema-B manifests
now exist that did not before.

**Element (i), student attribution — one source, all six floats.**
`report/paper_current_STS.tex:56` is a sole-author block, and every generating script named
below is repository code. No float is borrowed, third-party, or AI-generated.

**Element (iii), year — 2026 for every float**, taken from git blob dates.

| float | (ii) creating program | evidence for (ii) | (iii) year | evidence for (iii) | manifest |
|---|---|---|---|---|---|
| `fig:gate` **(v3)** | `matplotlib 3.11.1` | `feasibility/gate_schematic.py:3-5`; version read from the live interpreter; pinned `requirements.txt:7` | **2026** | git blob date `2026-08-18` | **`data/gate_schematic_v3.manifest.json` — NEW** |
| `tab:models` | emitter `scripts/emit_v2_tables.py`, typeset as a LaTeX `tabular` | `scripts/emit_v2_tables.py:7` writes `notes/paper_tables_v2.tex` | **2026** | git date `2026-07-30` on the emitter | none — not an image file |
| `tab:ops` | same emitter, same route | same | **2026** | same | none |
| `fig:tradeoff` | `matplotlib 3.11.1` | `feasibility/paper_hero.py:4-7`; live interpreter; `requirements.txt:7` | **2026** | git blob date `2026-07-30` | **`data/tradeoff_hero_col_v2.manifest.json` — NEW** |
| `fig:missdepth` | `matplotlib 3.11.1` | `scripts/miss_depth_fig.py:14,16` | **2026** | git blob date `2026-08-03` | exists, **no `apa_citation`** |
| `fig:boundary` | `matplotlib 3.11.1` | `feasibility/boundary_mass_hist.py:4,6` | **2026** | git blob date `2026-07-23` | **none** |

**WHAT EACH LINE MUST CONTAIN — specification only. No caption text is written in this guide.**

- **Four PNG floats:** the three elements above, in the author's own sentence, placed after the
  caption content inside the float. The program element must read `matplotlib 3.11.1` — the
  version is an environment fact, re-read this session, not a remembered one.
- **Two tabular floats:** elements (i) and (iii) as above; for (ii), **name the emitter that
  produced the values and state the table is typeset from it.** Appendix 3's software bullet is
  written for image-creation programs and a LaTeX `tabular` has none. **Naming a plotting library
  for a table would be false**, and a false citation is worse than a differently-shaped one.
- **Forbidden in every line:** a shared citation spanning more than one float (Appendix 3 says
  "each individual graphic"); any `\url{}` (rule 5e); a bare software reference with no student
  attribution and no year — which is what both pre-existing `apa_citation` values are.

**MANIFEST NOTE.** The two new manifests carry an `appendix3_elements` block holding the three
elements as discrete, sourced fields, and a `caption_line_status` field recording that the
sentence is the author's to write. `apa_citation` remains the APA software reference, consistent
with the existing Schema-B files. **The manifests supply the elements; they do not compose the
line.**

### 10.3c THE `fig:gate` DECISION IS NOW EVIDENCE-BACKED

**v3 is drawn at the M2 band width — CONFIRMED, not inferred.** The regeneration printed it:

> `strip sized from q_hat=0.002290702766310826 pu read from data/tradeoff_curve_v2.json (histgb, coverage_target 0.90); annotation prints no number`

That value matches `data/tradeoff_curve_v2.json` `records[histgb, coverage_target 0.90].q_hat`
exactly, and the run reproduced the committed `v3` **byte-identically** (md5
`5ceefccf43d5441191e9e41835924af2`, 157,375 B).

**v2 is drawn at the M1 width — CONFIRMED at the curve level.** Running the same script against
the default `data/tradeoff_curve.json` prints `q_hat=0.002557109746803765`, matching that file's
`histgb @ 0.90`. This is the width erratum **E1** attributes to v2.

**BUT v2 IS NOT BYTE-REPRODUCIBLE FROM TODAY'S SCRIPT — a new finding.** Neither
`--font-bump 0` (md5 `29d71ec7895b82c2c4cd99ea8c005bd1`) nor `--font-bump 2` (md5
`5ae2eb993cf50a4522e2a379377a343f`) reproduces the committed `5b8e53a285a1c739edef92c23db760d8`.
The committed v2 was produced by an earlier state of the script or different settings that are
not recorded.

**CONSEQUENCE FOR 10.11's OPTION 2.** Keeping v2 and disclosing its M1 sizing means shipping a
figure that **cannot be regenerated from the repository**, in a paper whose reproducibility is a
stated contribution. **Option 1 — repoint to v3 — is now the better-evidenced choice on
reproducibility grounds as well as on E1 grounds.** v3 regenerates byte-exactly and its band
width is confirmed by the script's own output.

### 10.4 Page numbering — GROUNDED, Rule 5c

**Rule 5c, verbatim:**
> "Number the pages of your research report in the bottom right corner, starting after the
> abstract."

**What the `.tex` currently produces: bottom CENTRE.** `grep -c "pagestyle|fancyhdr|fancyfoot"`
returns **0** — no page-style command anywhere. `\documentclass[12pt]{article}` therefore applies
its default `plain` style, which sets the folio bottom-centre. **FAIL.**

**The single preamble change required** — specified, **NOT APPLIED** per instruction: load
`fancyhdr`, select it as the page style, clear all header/footer fields, place `\thepage` in the
**right** foot slot, and suppress the header rule. **Second, separate requirement in the same
rule:** numbering must **start after the abstract**, so arabic numbering has to be reset once the
abstract ends — the current file has no abstract page break at all (10.5, structure row).

**Word cost: 0.**

### 10.5 Remaining format rules — verified PASS / FAIL / UNMEASURED

| rule | requirement (verbatim fragment) | state of `report/paper_current_STS.tex` | verdict |
|---|---|---|---|
| 5b | "Use 1.5 line spacing" | `\onehalfspacing` at `:66` | **PASS**, with a caveat: the preamble's own note at `:8-12` says this is Word-style 1.5 (`baselinestretch` ~1.24), not a literal 1.5, and offers `\setstretch{1.5}` as the alternative. The rule says "1.5 line spacing" without defining it. **Unresolved by the rule text; flagged, not decided.** |
| 5b | "1″ margins on all sides" | `\usepackage[letterpaper,margin=1in]{geometry}` at `:27` | **PASS** |
| 5b | "Do not use multiple columns" | single column; no `twocolumn`, no `multicol` | **PASS** |
| 5a | "at least as large as Times New Roman 11pt font" | `\documentclass[12pt]` + `newtxtext` (Times) at `:25`, `:30` | **PASS** — 12pt Times exceeds the 11pt floor |
| 5c | page numbers bottom right, after abstract | no page-style command; `article` default is bottom-centre | **FAIL** — see 10.4 |
| 5e | "may not provide links within the Research Report… except within bibliographic references" | **one `\url{}` in the BODY at `:287`**, in Acknowledgments. The only other URL is at `:317` inside `\bibitem{case118}`, which the rule permits | **FAIL** — see erratum E2 |
| 5f | "PDF files that are 4MB or smaller" | four embedded PNGs total **443,554 bytes ≈ 0.43 MB**; the compiled PDF adds fonts and text | **UNMEASURED** — no TeX toolchain exists in this environment. The figure payload is ~11% of the cap, so the margin is wide, but the compiled size is not a fact I can assert |
| 4b | title page first, abstract second, bibliography last | `\maketitle` at `:64` with `\vspace{-0.5in}`; abstract is a `\section*{Abstract}` at `:69`, **inline, not a separate page**; bibliography last | **FAIL on structure** — the rule requires the title page and abstract to be *pages*, which is also what makes the 4b exclusion computable. See 10.7 |
| 2 | every graphic cited | zero of six | **FAIL** — see 10.1-10.3 |

### 10.6 Generative AI — GROUNDED, Appendix 4, and it CORRECTS §1.3

**Appendix 4, Official Rules p.34, "USE OF GENERATIVE AI TO SUPPORT A RESEARCH PROJECT."** A
13-row table of task / acceptable? / conditions, adapted from an AHA Ad Hoc Committee document
approved 2025-07-29. **It is not a prohibition.** Rows that bind this project, verbatim:

| task | acceptable? | conditions (verbatim) |
|---|---|---|
| "Use generative AI to initially write the research plan, abstract, paper or poster" | **No** | "Never acceptable. This must be the independent work of the student. Guidance or refinement after the initial document has been completed can be done with explicit citation and a log." |
| "Ask generative AI to write an abstract or section of your research paper. Submit as your own work" | **No** | "Never acceptable" |
| "You write an abstract. Ask AI to sharpen the language but not modify, add to, or replace the main points" | **Yes** | "Acceptable use without explicit citation only if changes suggested by AI are minor and limited to grammar and syntax. Must be credited." |
| "Use AI to write initial code for your project" | **Yes** | "Acceptable, only with explicit citation stating which portions of the code were AI generated and with a log of the prompts." |
| "Use an AI chatbot as a writing tool to help generate and develop ideas" | **Yes** | "Acceptable, may require explicit citation depending on circumstances. Maintain a logbook of your prompts as part of your research notebook." |
| "Use AI to help identify appropriate statistical tests or software tools. (Interpretation of data must be done by the student researcher)" | **Yes** | "Acceptable, requires a log of your prompts as part of your research notebook." |
| "Use AI to produce your conclusions, future steps, etc." | **No** | "Never acceptable." |
| "Ask generative AI to produce a starter bibliography" | **No** | "Never acceptable." |

**WHAT THIS CHANGES.** `notes/finalist-paper-analysis.md` §1.3 and R5 read rule 1 as "no
generative AI, full stop." **That reading is too strong.** Rule 1 governs *writing the paper*;
Appendix 4 governs the project and permits code assistance, idea development and tool selection —
**each conditioned on a prompt log.**

**WHAT THE PROJECT ALREADY SATISFIES.** `notes/ai-prompt-log.md` is exactly the "logbook of your
prompts as part of your research notebook" that three of the permitted rows require. The standing
rule that this guide contains **no manuscript prose**, and that the author writes every sentence,
is what keeps the two "Never acceptable" writing rows clear. **Both were adopted before Appendix 4
was read here, and both hold.**

**WHAT IS NOT YET SATISFIED — one open item.** The code row requires "**explicit citation stating
which portions of the code were AI generated**". The Acknowledgments at `:287` states that an AI
assistant "was used to validate the code and grammar" but **identifies no portion**. **A
per-portion attribution does not exist in the repository.** Recorded as erratum **E3**; not
drafted here, because what is attributable is a matter of fact only the author can settle.

### 10.7 The 20-page denominator — GROUNDED, Rules 4b and 4e

**Rule 4b, verbatim:**
> "Include a title page as the first page, abstract as the second page and a bibliography at the
> end of the Research Report. **The title page, abstract and bibliography do not count toward the
> 20-page limit.**"

**Rule 4e, verbatim — state this so nothing is moved into an appendix to evade the limit:**
> "**Appendices count toward the 20-page limit.** Some students choose to include all images,
> charts, data, etc. within the paper, while others place them in appendices. Both options are
> acceptable."

**Rule 4a, verbatim:**
> "The paper should be 20 pages or less. There is no page minimum. Pages of content beyond page 20
> (excluding the pages mentioned below) will not be read or considered."

**Consequence: §6.2 has been measuring against the wrong denominator.** Its total counts the title
block and the bibliography inside the 20. Both are excluded, and so is the abstract. The corrected
arithmetic is in §6.2 as amended. **`notes/finalist-paper-analysis.md` R1(c) flagged this; 10.7 is
where it is discharged.**

**Structural precondition, and it is not free.** The exclusion is computable only if the title page
and abstract are *pages*. They currently are not (10.5, row 4b). Making them pages costs layout,
not budget — excluded pages are excluded however much space they occupy.

### 10.10 BLOCKER (a) RESOLVED — the `fig:tradeoff` generator

**FOUND: `feasibility/paper_hero.py`.** Library: **matplotlib**, pinned `matplotlib==3.11.1` at
`requirements.txt:7`, and the installed interpreter reports the same version. The script also
imports the local helper `feasibility/figtools.py`.

**Why the earlier search missed it.** `paper_hero.py:10` declares `OUT = "data/tradeoff_hero_col.png"`
— the **v1** name — and `:29-30` expose `--curve` and `--out`. The v2 file was produced by passing
`--out`, so **the literal string `tradeoff_hero_col_v2` never appears in any script.** A
filename-substring grep cannot find it. Same construction as `gate_schematic.py` in erratum E1.
**The v2 invocation is not recorded anywhere in the repository**; the script and library are
established, the exact command is not.

### 10.11 BLOCKER (b) — `fig:gate` options, in order

E1 records that `data/gate_schematic_v2.png` is sized from the **M1** band while every reported
number is **M2**, and that `data/gate_schematic_v3.png` is the corrected figure, regenerable
byte-exactly by the command in E1.

**OPTION 1 — repoint `:138` to `v3` and cite v3.** Closes **E1** and clears **E4** for this float
in one edit. All three Appendix 3 elements are sourceable for v3. **Cost: one
`\includegraphics` path plus the citation line.** E1's own disposition language — that the
correction be *stated* rather than swapped in quietly — applies to the **URTC** paper, which is
already submitted. **The STS report is not yet submitted, so for STS this is not a silent
correction; it is simply using the correct figure.**

**OPTION 2 — keep `v2` and disclose the M1 sizing in the caption.** Satisfies **E4** only.
**Leaves E1 OPEN**, and spends caption words disclosing a defect that Option 1 removes. It also
puts a known-defective figure in front of the Scholar screen with an explanation attached.

**RECOMMENDED ORDER: Option 1.** Option 2 exists only if v3 turns out not to regenerate, which E1
says it does (md5 `5ceefccf43d5441191e9e41835924af2`, verified there).

**Do not write the citation line for `v2`.** Under either option the cited artefact must be the
one actually embedded.

### 10.12 The three Appendix 3 elements, per float, with sourcing

**Element (i) student attribution — SOURCEABLE for all six.** Evidence: `\author{Rajan Saha}` at
`report/paper_current_STS.tex:56` is a sole-author block, and every generating script named below
is repository code. **No float is borrowed or third-party.**

**Element (iii) year — SOURCEABLE for all six as 2026.** Taken from git blob dates, not mtimes,
because mtimes drift on checkout.

| # | float | (ii) creating program | evidence | (iii) year | evidence |
|---|---|---|---|---|---|
| 1 | `fig:gate` | matplotlib (+ local `figtools`) | `feasibility/gate_schematic.py:3-5,8` | **2026** | git blob date `2026-07-23` for `gate_schematic_v2.png` |
| 2 | `tab:models` | values emitted by `scripts/emit_v2_tables.py`; typeset as a LaTeX `tabular` | `scripts/emit_v2_tables.py:7` writes `notes/paper_tables_v2.tex` | **2026** | git date `2026-07-30` on the emitter (`9a76b6d`) |
| 3 | `tab:ops` | same emitter, same route | same | **2026** | same |
| 4 | `fig:tradeoff` | matplotlib 3.11.1 (+ `figtools`) | `feasibility/paper_hero.py:4-7`; `requirements.txt:7` | **2026** | git blob date `2026-07-30` |
| 5 | `fig:missdepth` | matplotlib | `scripts/miss_depth_fig.py:14-16` | **2026** | git blob date `2026-08-03` |
| 6 | `fig:boundary` | matplotlib (+ `figtools`) | `feasibility/boundary_mass_hist.py:4-6` | **2026** | git blob date `2026-07-23` |

**NOTHING IS NO SOURCE.** All three elements are sourceable for all six floats. **What remains
unsourced is narrower and does not block the citation:** the exact `--out`/`--curve` invocation
that produced `tradeoff_hero_col_v2.png` (10.10), and a git date for the two tables' *rendered*
output, because `notes/` is git-ignored at `.gitignore:23` — hence the emitter's date is used
instead, which is the honest anchor.

**One caveat that must travel with elements (ii) for the tables.** Appendix 3's software bullet is
written for image-creation programs. A LaTeX `tabular` has no such program in the same sense.
**Specification: name the emitter that produced the values and the fact that the table is typeset
from it** — that is the closest true statement, and it is stronger than naming a plotting library
that was not used.

### 10.13 The `:287` Acknowledgments sentence — every finding, and the options

**Verbatim, `report/paper_current_STS.tex:287`:**

> "This paper has been written as part of the Boston University RISE data science practicum. The
> authors would like to thank the program and the teaching fellows and staff. An AI assistant,
> Claude from Anthropic, was used to validate the code and grammar. All reported numbers were
> generated using the authors' committed and tested code that is available at the following link:
> `\url{https://github.com/rajsaha-blip/contingency-screener-research}`."

**Five findings touch this one sentence block:**

| finding | what it says |
|---|---|
| **E2** | the `\url{}` is a body link outside the bibliography — GUIDE2027 rule 5e violation |
| **E3** | "validate the code and grammar" names no code portion — RULES2027 Appendix 4 p.34 requires it |
| **PART 2 item 12** | **the provenance claim is FALSE as written.** The cited remote `rajsaha-blip` is at `990c3c5`; local and `origin` (`RS499/...`) are at `ab970c1`. Separately `notes/` is git-ignored at `.gitignore:23`, so no note, log or prereg named in this guide is reachable from that URL |
| **R08** (`sts-constraints.yaml`) | `check_compliance.py` reports **FAIL**: "1 external link(s) OUTSIDE the bibliography" |
| **R24** | GUIDE2027 rule 7 permits "I"; "the authors" is plural in a sole-authored report |

**Because item 12 shows the claim is false as written, no option that leaves the sentence
unchanged is available.** That is a correctness constraint, not a stylistic one.

| option | satisfies | closes | leaves open | cost |
|---|---|---|---|---|
| **1. Move the URL into a `\bibitem` and cite it** | rule 5e via its explicit bibliographic exception — **R09 is now `confirmed`, so this route is verified, not assumed** | **E2**, **R08** | **PART 2 item 12 unless the URL is also corrected** to the remote that actually carries `ab970c1`, and unless the claim is narrowed to what is reachable — `notes/` is ignored | +1 bibitem; interacts with 6.1 step 4, which already removes `tibshirani2019`, so the net width stays 19 |
| **2. Drop the URL, keep the prose naming the repository** | rule 5e | **E2**, **R08** | **PART 2 item 12** — naming a repository whose contents do not match the claim is the same defect without the hyperlink | ~0 words |
| **3. Drop both the URL and the provenance claim** | rule 5e | **E2**, **R08**, **PART 2 item 12** | nothing on this axis; **E3 is untouched by all three options** | negative — removes words |

**E3 is orthogonal and must be fixed under every option.** It is about naming which code portions
were AI-generated, which no choice above addresses.

**Option 1 is the only one that preserves the reproducibility pointer**, which `CLAUDE.md` §9 aims
the repo at. **Option 3 is the only one that closes all three findings by itself.** The choice is
the owner's; the trade is a verified-compliant pointer versus fewer open findings.

### 10.14 Status of PART 10 — specified end-to-end, or blocked

| item | state |
|---|---|
| 10.1-10.3 float citations, floats 2-6 | **SPECIFIED END-TO-END.** All three Appendix 3 elements sourced (10.12); placement and word cost fixed (10.3) |
| 10.3 float 1 (`fig:gate`) | **DECISION PENDING, not blocked.** Elements all sourced; awaits Option 1 vs 2 (10.11) |
| 10.4 page numbering | **SPECIFIED.** Position change stated; **the "starts after the abstract" half depends on the title/abstract page split**, which is 10.5's structural FAIL |
| 10.5 format rules | **VERIFIED** except PDF size, permanently **UNMEASURED** here — no TeX toolchain |
| 10.6 generative AI | **SPECIFIED**, and now carried as `R22` in `notes/sts-constraints.yaml`. One open item: E3 |
| 10.7 page denominator | **CLOSED.** Corrected in §6.2; `R05` confirmed |
| 10.10 tradeoff generator | **RESOLVED** |
| 10.11 `fig:gate` | **OPTIONS STATED**, decision pending |
| 10.13 `:287` | **OPTIONS STATED**, decision pending; blocked on nothing but a choice |

**STILL BLOCKED, AND ON WHAT:**

1. **The compiled-PDF checks** — `R05` page count, `R12` pagination, `R14` size. Blocker: **no TeX
   toolchain in this environment.** Permanent here; needs a build elsewhere.
2. **`R14` filename** — blocker: **the home ZIP is NO SOURCE** and is not guessed. Owner-supplied.
3. **`R19` grades** — blocker: **RULES2027 pp.8 and 41 were not read.** 41 of the book's 50 pages
   remain unread.
4. **`nerc` bibitem** (`R11`) — blocker: primary PDF returns HTTP 403.
5. **`scripts/check_compliance.py:11` carries `FONT_FLOOR_PT = 10`** and its PASS message still
   reads "floor itself is status: verify". **`R06` is now `corrected` and the floor is 11pt.** The
   script is stale and out of scope this turn — it is neither of the two files this pass may write.
   **The manuscript passes either way at 12pt**, so this is a gate defect, not a paper defect.

### 10.8 What I could not find — NO SOURCE

- **A rubric, scoring sheet or weighted criteria.** NO SOURCE, re-confirmed 2026-08-27. Not inferred.
- **Any word limit.** NO SOURCE. The constraint is pages.
- **Any stated expectation on figure or table count.** NO SOURCE.
- **The generating script for `data/tradeoff_hero_col_v2.png`.** NOT LOCATED in `feasibility/` or
  `scripts/`. Its citation line cannot name a creating program until the script is found, so
  **float 4 is blocked on a repository question, not a rules question.**

### 10.9 Out of scope this pass

`notes/sts-constraints.yaml` records `rules_book_2027_present: false` and carries rows at
`status: verify` pending exactly the document fetched above. **Several of those rows are now
answerable.** This turn was restricted to `notes/writing-guide.md` and `notes/erratum.md`, so that
file is **unchanged and still says the 2027 rules book is absent.** That statement is now stale.
Reconciling it is a separate, named task.
