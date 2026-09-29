# Fix specifications — minors P-018 … P-027

Written 2026-09-27 by a spec writer (Claude Code), for the author. **Specifications only.** No replacement
text, no suggested wording. The author writes every word (GUIDE2027 rule 1; RULES2027 App. 4; R04/R22/R27).
Line numbers are from `report/paper_current_STS.tex` (460 lines, working tree 2026-09-27). All numbers were
re-read in this session with `.venv/bin/python`. Scratch script: `$CLAUDE_JOB_DIR/tmp/isl.py`
(islanding check); all other checks were one-line reads of the JSON keys named below.

Status legend: **re-read OK** = recomputed here and matches the printed value · **MISMATCH** = recomputed
and differs · **NOT FOUND** = no source key.

**Group net page cost: ≈ −0.04 pp** (itemised in the table at the end). If Cut-5 is taken, P-021's
−0.1 is already counted inside Cut-5, and the group net becomes ≈ +0.06 pp.

---

## P-018 — IEEE 30-bus is the wrong name for the network used

1. **Ledger ID / severity:** P-018 (POWER-08). MINOR.
2. **Anchors:**
   - l.81 "In the IEEE 30-bus system, using a base case"
   - l.119 "I also tested the published IEEE 30-bus system,"
   - l.365 "in a regeneration of the IEEE 30-bus network"
   - Bare "30-bus" also appears at l.119 ("regenerated the 30-bus network"), l.365 ("The original 30-bus system"), l.367 ("On the regenerated 30-bus network") and l.388 ("though the 30-bus result shows"). There is no bibitem for this network.
3. **Old text (affected phrases):** "In the IEEE 30-bus system" (l.81); "the published IEEE 30-bus system" (l.119); "a regeneration of the IEEE 30-bus network" (l.365).
4. **What must change:**
   - The code builds `pandapower.networks.case30` (`scripts/case30_thermal_build.py:29` NETWORK = "case30"; `scripts/thermal_check.py:39` builder=pn.case30). The pandapower 3.5.4 docstring (`.venv/.../pandapower/networks/power_system_test_cases.py:205-217`) says case30's data come from PYPOWER and are derived from the **"Washington 30 Bus Dynamic Test Case"**. The IEEE 30-bus power-flow case is a separate function, `case_ieee30` (l.224-238; MATPOWER, "Washington IEEE 30 bus Case"). So the paper names a network it did not use.
   - The name at every use must identify the network that was actually run. That network is the PYPOWER/pandapower case30, derived from the UW 30-bus dynamic test case.
   - The source should be cited the same way case118 is. A verified bibitem does not yet exist (see §6).
   - The property "published base case at 111.83% line loading" (l.119, l.365) belongs to case30 as built. Re-attribute it to the renamed network. Do not move it to case_ieee30.
5. **Numbers:** none are changed. The pandapower version is 3.5.4 (re-read OK, `pandapower.__version__`).
6. **Must not claim:** that the results hold for the IEEE 30-bus power-flow case (`case_ieee30` was never run through the gate; `scripts/triage_networks.py:40` only lists it as a candidate). Do not fill a bibitem from memory. Per the literature rules, the UW dynamic-case page and PYPOWER must be fetched and verified first.
7. **Consistency:** the abstract (l.81), Method (l.119), Discussion (l.365, l.367), Conclusion (l.388), and any figure or caption that is added later (E2a scatter, E4 row) must all use one name. C1's network inventory (the other patch set) must use the same name.
8. **Page cost:** 0 (+1 bibitem line, outside the page count). Dependency: C1 inventory; bibitem verification (author).

## P-019 — Islanding outages are labelled silently

1. **Ledger ID / severity:** P-019 (POWER-09). MINOR.
2. **Anchors:** l.111 "Since the contingencies include only lines and transformers,"; l.119 "Each accepted base case was put through a simulation"
3. **Old text:** "Since the contingencies include only lines and transformers, there are 186 total pieces of equipment that are subject to failure." (l.111)
4. **What must change:** Method must say, once, how outages that cut buses off from the rest of the network are handled. The facts:
   - 9 of the 186 outages leave buses unsupplied (checked with `pandapower.topology.unsupplied_buses` on the nominal case118 build). **re-read OK** (ledger: 9/186).
   - `feasibility/generate_dataset.py:197` takes `np.nanmin(vm)`. Buses that are cut off come back as NaN and are skipped, so the row is labelled by the voltage of the still-connected network.
   - Two of the nine (line idx 6 and 7) cut off IEEE buses 9–10 and 10. Those rows are violations in 100% of the 1,500 bases.
   - The other seven outages disconnect load (MW lost at the nominal build): line 103 → IEEE 73 (6 MW); line 121 → IEEE 86–87 (21 MW); line 163 → IEEE 111 (0 MW); line 164 → IEEE 112 (68 MW); line 170 → IEEE 117 (20 MW); trafo 11 → IEEE 87 (0 MW); trafo 12 → IEEE 116 (184 MW). Their violation rates over 1,500 bases each are 3.87, 0.13, 3.00, 0.60, 0.40, 2.20 and 4.53%.
   - A row where load is disconnected is therefore usually labelled "safe". An operator would not call lost load safe.
   - Content choice for the author: disclose the rule only, or also report the load-losing outages separately. Either is acceptable. The fix is disclosure.
5. **Numbers:** 9/186 re-read OK. Violation shares 0.13–4.53% re-read OK (ledger/POWER-09 said 0.1–4.5%). 100% for line 6 and line 7 re-read OK. Source: recomputed from `data/dataset.parquet` (columns outaged_type, outaged_idx, converged, violation) plus a pandapower topology call. No committed JSON key exists, so a printed count needs a new artifact with a manifest (d-figs/d-runs) before it goes in the report (CLAUDE.md §9).
6. **Must not claim:** that islanded rows are "safe", or that lost load counts as a violation (it does not in this labelling).
7. **Consistency:** P-011 reproducibility table (label rule row); P-020 (non-convergence is the other labelling edge case; handle both in one place).
8. **Page cost:** +0.03. Dependency: a new sourced artifact if any count is printed.

## P-020 — The 45 non-converged cases are a critical transformer's tail, not noise

1. **Ledger ID / severity:** P-020 (POWER-10; review PS minor). MINOR.
2. **Anchor:** l.119 "Out of those 279{,}000, 45 were removed due"
3. **Old text:** "Out of those 279{,}000, 45 were removed due to failing to converge, resulting in 278{,}955 converged rows."
4. **What must change:**
   - Say what the 45 are. 37 are trafo idx 0 (IEEE 8–5), 7 are trafo idx 7 (IEEE 65–68), and 1 is trafo idx 6 (IEEE 65–66). Each comes from a different base case, at most one per scenario.
   - Say how the gate would have treated them. Across all 45 (not only the test split), in every seed and at every operating point in the file, 37–39 are flagged, 0–2 certified and 4–8 escalated.
   - Say that counting them as violations barely moves the missed rate. Largest shift in the seed-mean: 1.3e-5 (0.0013 percentage points).
   - One caveat content point: a few non-converged cases are **certified** (skipped as safe) at three operating points, so "the gate never certifies them" must not be claimed:
     - histgb @0.90: 2 of the 45 in every seed; within the test split, 1 in seeds 0, 1 and 3, 0 in seeds 2 and 4;
     - ridge @0.90, seed 1: 1 of the 45, and it is in that seed's test split (1 of 8);
     - histgb @0.97, seed 3: 1 of the 45, in that seed's test split (1 of 9).
     At ridge @0.94 and in every other seed/target in the file, 0 are certified. The claim that follows from this data is "rarely certified, and only at these points". The test-split counts are the ones that enter the published missed rates.
5. **Numbers (source `data/nonconverged_gate.json`):**
   - n_nonconverged 45, n_converged 278,955: re-read OK.
   - `q3_top_elements` trafo_0 37 / trafo_7 7 / trafo_6 1: re-read OK. IEEE names from `net.trafo` hv/lv + 1: 8–5, 65–68, 65–66 (re-read OK).
   - `summary.*.flagged_all45_by_seed`: ridge 38–39, histgb 37–39. **MISMATCH vs ledger wording "38–39"**: histgb seed 4 flags 37. Print the range as 37–39, or quote per model.
   - `summary.histgb.target_0.9.certified_all45_by_seed` [2,2,2,2,2]: re-read OK.
   - `q1_q2_per_seed.<family>[seed].target_<t>.{all45,test_split_only}.certified`, re-read over all 20 seed×target cells:
     - histgb 0.90: all45 2 in every seed; test split 1/1/0/1/0.
     - ridge 0.90 seed 1: all45 1; test split 1 of 8.
     - histgb 0.97 seed 3: all45 1; test split 1 of 9.
     - Every other cell: 0.
     All re-read OK. This corrects the earlier version of this file, which said histgb @0.90 was the only place a non-converged case is certified.
   - `delta_missed`: ridge 0.90 −1.0e-5; ridge 0.94 −8.4e-6; histgb 0.90 +1.3e-5; histgb 0.97 +1.2e-5. re-read OK.
   - The file's `published_missed_mean` values (0.02963, 0.04717, 0.00794, 0.00832) equal the v2 Table 2 values (2.96, 4.72, 0.79, 0.83), so this artifact uses the promoted M2 models (M1/M2 rule satisfied). re-read OK.
6. **Must not claim:** that non-convergence proves voltage collapse. It is only consistent with a severe state. The same transformer dominates the deep tail in the panel's relabel sample, but that is teammate-verified and not a committed key.
7. **Consistency:** l.119 count sentence; P-011 table (dataset counts); P-019 (one labelling paragraph); P-003/N2 label audit (if N2 changes labels, re-check these tallies).
8. **Page cost:** +0.03. Dependency: none. `data/nonconverged_gate.json` and its manifest are tracked (`git ls-files`, 2026-09-27).

## P-021 — case57 exclusion: wrong physical reason

1. **Ledger ID / severity:** P-021 (POWER-07; review PS-M7; D10). MINOR.
2. **Anchor:** l.353 "In case57, the voltage was too low across"
3. **Old text:** "In case57, the voltage was too low across the whole network, meaning it was not possible to bring every bus above the 0.94 pu threshold under realistic conditions, as at load multiplier 0.0 the minimum pre-outage voltage remained 0.9012 pu with 24 buses below the 0.94 pu threshold."
4. **What must change (D10: keep the exclusion, correct the reason):**
   - A network with every load at zero should not sit at 0.90 pu. The zero-load result shows the pandapower case57 data do not reproduce a sensible base solution. That is a model-data problem, not a load-level or stress problem, and "under realistic conditions" is the wrong frame, because zero load is not a realistic condition.
   - "Across the whole network" overstates the zero-load result: 24 of 57 buses are below 0.94 there. At nominal load it is 39 of 57, minimum 0.7199 pu.
   - The acceptance-rule context: under the pinned case118 sampler, 0 of 3,000 draws pass the N-0 gate (`data/case57_feasibility.json` verdict). The rule, applied to broken data, is what decides.
   - Shorten to one sentence under Cut-5 (other patch set). Keep the fact that an exclusion was made and why.
5. **Numbers:**
   - 0.9012 → `data/netstudy/case57/nofeasible_diagnostic.json` → `scaling[multiplier=0.0].min_vm_pu` = 0.901210: re-read OK.
   - 24 → same record `n_bus_below_094` = 24: re-read OK.
   - Nominal 0.7199 pu, 39/57 → `scaling[multiplier=1.0]`, `nominal_n_bus_below_094`: re-read OK.
   - 0/3,000 accepted → `data/case57_feasibility.json` → `step1_n0.accepted` 0, `attempts` 3000: re-read OK.
6. **Must not claim:** that case57 is "structurally" unable to meet 0.94 as a property of the real IEEE 57-bus system (the file's `verdict` string says STRUCTURAL; that is a statement about this data build only). Do not claim realism for the zero-load probe.
7. **Consistency:** Cut-5 (case57/pegase detail); C1 network inventory; the "30.65" case57 boundary mass is a killed number (`scripts/check_paper.py` KILLED_UNCONDITIONAL) and must not reappear.
8. **Page cost:** −0.1 standalone. It is **inside** Cut-5 if that cut is taken (do not double-count).

## P-022 — "absorb the extra load" is wrong physics

1. **Ledger ID / severity:** P-022 (POWER-12). MINOR.
2. **Anchor:** l.107 "However, if a single piece of equipment fails,"
3. **Old text:** "However, if a single piece of equipment fails, the rest of the network must absorb the extra load, which could cause the voltage at one or more buses to go under the safe 0.94 pu floor."
4. **What must change:** A branch outage adds no load. The causal chain the passage must carry has three parts:
   - Power that used the lost branch is rerouted over the remaining paths.
   - The heavier flows raise series reactive losses (the I²X term).
   - A path that supported voltage is gone.
   Together these lower voltages at weak buses. The passage must stay at lay level (D15). The mechanism can be named without the formula.
5. **Numbers:** none.
6. **Must not claim:** that load increases after an outage. Islanding outages (P-019) *remove* load, which is the opposite case.
7. **Consistency:** l.99/l.97 introduction framing, if either restates the cause.
8. **Page cost:** 0.

## P-023 — What "±" means, and the abstract numbers without ±

1. **Ledger ID / severity:** P-023 (STATS-09). MINOR.
2. **Anchors:**
   - l.81 "On the IEEE 118-bus AC network at 90\% coverage"
   - l.208 Table 1 caption "Means $\pm$ standard deviation over five random splits."
   - l.241 Table 2 caption "Means $\pm$ standard deviation over five random splits."
3. **Old text:** "…the gradient-boosted model is 3.29 times faster than the solver but misses 4.72\% of violations. For the gradient-boosted model, first going just under a 1\% mean missed rate at a 0.97 coverage target results in a 63.7\% escalation and speedup dropping to roughly 1.58, with error bars going slightly above 1\%." (l.81)
4. **What must change:**
   - State once, in each table caption (or once in Method with captions pointing to it), what the ± is. It is a population standard deviation (ddof = 0) across five re-splits of one generated dataset. It measures split-to-split variability. It is not a standard error or a confidence interval, and it does not include data-generation variability.
   - Every case118 number in the abstract carries its ±, as the case30 number already does (5.84±1.25).
   - Report per-seed exceedances for case118 the same way the case30 sentence does ("k of 5"; C13, other patch set).
5. **Numbers (source `data/tradeoff_curve_v2.json` records; `std_convention` = "population std (ddof=0) over five held-out splits"; code `scripts/build_v2_frozen.py:34-38` uses `np.std` with ddof=0; `scripts/emit_v2_tables.py:22,32-34` also ddof=0 on numpy arrays):**
   - histgb 0.90: speedup 3.287±0.302 → 3.29±0.30; missed 4.717±0.977 → 4.72±0.98. re-read OK.
   - histgb 0.97: escalation 63.679±5.119 → 63.7±5.1; speedup 1.579±0.117 → 1.58±0.12; missed 0.832±0.245 → 0.83±0.24 (0.2447 rounds to 0.24). re-read OK.
   - ridge 0.94: missed 0.794±0.209 → 0.79±0.21. re-read OK.
   - case30 histgb 0.97: 5.836±1.250 → 5.84±1.25 (`data/case30_thermal/case30_thermal_frozen.json` records, ddof 0). re-read OK.
   - For reference only (not for printing unless the author switches convention): with ddof = 1 the upper bars are 0.79+0.23 = 1.03 (ridge 0.94) and 0.83+0.27 = 1.11 (histgb 0.97). re-read OK (STATS-09 values).
   - Per-seed missed (`data/tuned_metrics.json` m2 sweeps): ridge 0.94 [0.601, 0.624, 1.146, 0.918, 0.678], 1/5 > 1%. histgb 0.97 [1.162, 0.798, 1.032, 0.699, 0.470], 2/5 > 1%. re-read OK.
   - Std-rule: mean 0.83 vs threshold 1.00 differs by 0.17 < 0.24, so "under 1%" is not resolved. The same holds for ridge (0.21 gap vs 0.21 std). The text must not present either mean as reliably below 1%.
6. **Must not claim:** that ± is an uncertainty on the deployed rate, or that the mean being below 1% means the model meets a 1% target.
7. **Consistency:** abstract l.81; l.231 ("error bars … 1.0–1.07%" → numbers-2b 2b-1); Fig. 2 caption l.281 (P-005 bands); l.349; l.365 (case30 "all five splits"); conclusion l.388; C13.
8. **Page cost:** 0 (≈ +0.02 of caption words, absorbed). Dependency: headline operating-point decision (Top-5 #2(d)/E5) may change which abstract numbers need ±.

## P-024 — Miss-depth shares: pooled, and against two different thresholds

1. **Ledger ID / severity:** P-024 (REPRO-09). MINOR.
2. **Anchors:**
   - l.292 "At 0.90 coverage, 74\% of misses fall"
   - l.303 "74\% of ridge misses and 55\% of histgb"
3. **Old text:** "At 0.90 coverage, 74\% of misses fall within one band width of the limit for the linear model and 55\% for the gradient-boosted model (Fig.~\ref{fig:missdepth}), with 26.7\% of ridge misses and 21.4\% of histgb misses falling more than 0.005 pu below the limit." (l.292). Caption: "74\% of ridge misses and 55\% of histgb misses fall within one band width each." (l.303)
4. **What must change:**
   - Say these shares are **pooled**: misses from all five splits are put together before the share is taken. That is not a mean over splits.
   - Say the two pairs use **different yardsticks**. 74/55% is measured against each model's own band width q̂ at 0.90 (ridge ≈ 0.0052, histgb ≈ 0.0023 pu). 26.7/21.4% is measured against a fixed 0.005 pu. These are not complements of each other. For ridge the two thresholds almost coincide (q̂ ≈ 0.005). For histgb they do not: 55% are within its own band width, but 78.6% are within 0.005 pu.
   - Readers compare the models, so one fixed yardstick for both models is the clearer content choice. The author decides which.
   - Optional: per-seed mean ± std instead of pooled.
5. **Numbers (source `data/missed_depth.json` → `families.<model>.pooled` [0.90 entry] and `.per_seed.<s>.0.90`; cross-check `data/miss_depth_pool.json` depths):**
   - ridge pooled `share_below_qhat` 0.7368 → 74%: re-read OK. Per-seed mean 73.73±3.93%.
   - histgb pooled `share_below_qhat` 0.5490 → 55%: re-read OK. Per-seed mean 55.21±2.65%.
   - ridge pooled 1 − `share_below_strip` = 0.2674 → 26.7%: re-read OK (depth > 0.005 in pool: 0.26741). Per-seed mean 26.82%.
   - histgb pooled 1 − `share_below_strip` = 0.2141 → 21.4%: re-read OK (pool: 0.21410). Per-seed mean 21.21%.
   - histgb pooled `share_below_strip` 0.7859 (78.6% within 0.005 pu): re-read OK.
   - Pooled counts: ridge 1,436 misses, histgb 2,284.
   - Std-rule: pooled vs per-seed-mean differences are all below the per-seed std, so either presentation is defensible.
   - Pooled `max` = 0.091457 for **both** models: re-read OK. Ridge and histgb miss the same deepest case. That case is the P-001 artifact (scenario 101000025, `scripts/miss_depth_fig.py:119,192`).
6. **Must not claim:** that 74% and 26.7% are complementary shares, or that the shares are split means. Do not give any depth-tail number a physical reading before N2 (P-003).
7. **Consistency:** l.292, l.303 caption, E9 (miss depth at recommended points, after N2), and P-001 (the 0.0915 sentence in the same paragraph and caption). The Fig. 3 PNG itself prints "deepest miss 0.0915 pu" with an arrow in the ridge panel (`data/miss_depth_v3.png`; `scripts/miss_depth_fig.py:117-120`). The ledger's P-001 question "check whether it marks the 0.0915 case" is answered: **yes, in-image**. Removing it needs a new PNG (d-figs).
8. **Page cost:** 0. Dependency: P-001 / N2.

## P-025 — Figure and bookkeeping hygiene

1. **Ledger ID / severity:** P-025 (REPRO-11). MINOR.
2. **Anchors:**
   - Fig. 5 caption l.339 "The buses that most frequently hold the"
   - comment l.296 "% FIGURE 3 (fig:missdepth) -- miss-depth histogram, from"
   - comment l.317 "% FIGURE 4 (fig:boundary) -- boundary-mass histogram, from"
   - Fig. 3 caption l.303 "The histogram above measures how far missed"
3. **Old text:**
   - l.296-298: "% FIGURE 3 (fig:missdepth) -- miss-depth histogram, from / % data/miss_depth_v2.png (log-y; generated by scripts/miss_depth_fig.py / % from data/missed_depth.json). Cited in IV-B."
   - l.317-318: "% FIGURE 4 (fig:boundary) -- boundary-mass histogram, from / % data/boundary_mass_hist.png. Cited in IV-C."
4. **What must change:**
   - **Fig. 5 colour scale.** Both `feasibility/domain_figure.py:86` and `scripts/sts_critical_bus_map.py:99` use `PowerNorm(gamma=0.5)` (NORM_GAMMA = 0.5, domain_figure.py:20). The colour bar is square-root scaled, so small shares look bigger than they are. The caption must disclose this, or the figure must be rebuilt with a linear scale (d-figs, new file).
   - **Fig. 5 layout program.** The layout comes from pandapower's igraph generic coordinates (`domain_figure.py:30`, `data/bus_layout.json` library "igraph"). The credit line at l.342 names Matplotlib only. R21 requires the creating program(s) (STS-12). This overlaps P-004/P-006. Decide it there, and do it once.
   - **Stale .tex comments.** l.297 names `miss_depth_v2.png`, but the float includes `miss_depth_v3.png` (l.302). l.318 names `boundary_mass_hist.png`, but the float includes `boundary_mass_hist_v2.png` (l.322). Comments do not print, but they mislead a reproducer. Author edit, 0 pp.
   - **Stale manifest.** `data/critical_bus_map.manifest.json` → `manuscript_role` = "Not referenced by report/paper_current_STS.tex as of sha256 42d5ee14." That is false, because l.338 includes it. Fix = a **new** manifest file beside the replacement figure (`data/sts_critical_bus_map.manifest.json` already exists and has no `manuscript_role` key) or a superseding note. **Never edit the existing manifest** (d-figs).
   - **Fig. 3 shaded strip.** `scripts/miss_depth_fig.py:91` shades depth [0, 0.005) pu (STRIP = 0.005, l.22). The caption never says what the grey strip is. The caption must name it (the 0.005 pu strip width), or the strip should be dropped in a rebuilt PNG.
   - **Null hyperparameters.** `data/barrier_height.manifest.json` → `model_hyperparameters` = None. That violates the "manifest beside every artifact, including the model hyperparameters" rule (CLAUDE.md §8). S_mean (l.189) comes from this artifact. If E15 cuts S_mean, the paper no longer depends on it. If S_mean stays, d-figs/d-runs write a new superseding manifest with the M2 configs per seed. The same null appears in `data/nonconverged_gate.manifest.json` (used by P-020): same remedy if P-020 prints numbers.
5. **Numbers:** NORM_GAMMA 0.5 re-read OK; STRIP 0.005 re-read OK. None are printed in the report.
6. **Must not claim:** that Fig. 5 colours are proportional to share (they are not, under PowerNorm).
7. **Consistency:** P-004 (Fig. 5 re-upload), P-006 (credit-line form), Cut-2 (if Fig. 5 is cut, the Fig. 5 items lapse), E15 (S_mean cut removes the barrier-height dependency), P-001 (Fig. 3 rebuild — combine with the strip decision so d-figs builds one new PNG).
8. **Page cost:** 0. Owners: author (captions, comments) and d-figs (new PNGs and manifests only).

## P-026 — Table 1 mixes two pipelines without saying so

1. **Ledger ID / severity:** P-026 (REPRO-12). MINOR.
2. **Anchor:** l.208 "Four-model comparison at 90\% target coverage."
3. **Old text:** "Four-model comparison at 90\% target coverage. Means $\pm$ standard deviation over five random splits. Escalation and missed-violation rate (share of true violations) in percent; histgb is the gradient-boosted model. $^{\dagger}$The train-mean model never calls the solver, so this does not represent a proper screening speedup."
4. **What must change:**
   - The caption must say that the persistence and train-mean rows come from the committed first pipeline (`data/screener_metrics.json`), while the ridge and histgb rows come from the promoted M2 models (`data/tuned_metrics.json` + `data/tradeoff_curve_v2.json`).
   - It must also say that the baseline rows have no fitted parameters and use the identical five test splits, so the pipeline difference does not affect them.
   - Train-mean flag content (NS-04, handled with E8 in the other set): the constant prediction 0.93983 is below 0.94, so every case is flagged. The dagger note must carry that fact, not only "never calls the solver".
   - Bookkeeping: both baseline R² cells are **hard-coded strings** in `scripts/emit_v2_tables.py` ("$-0.06\pm0.00$" and "$-0.00\pm0.00$"), not computed. The printed values agree with the data (below), but the emitter should compute them. That is a code note for d-figs, not a report change.
5. **Numbers (`data/screener_metrics.json` records, ddof 0; ×1000 for MAE, ×100 for rates):**
   - persistence: MAE 4.2457±0.0706 → 4.2±0.1; R² −0.0611±0.0032 → −0.06±0.00; esc 99.534±0.164 → 99.5±0.2; missed 0.311±0.080 → 0.31±0.08; speedup 1.0047±0.0017 → 1.00±0.00. All re-read OK.
   - train mean: MAE 6.7316±0.1726 → 6.7±0.2; R² −0.0002±0.0002 → −0.00±0.00; esc 0.0±0.0; missed 0.00±0.00. re-read OK.
   - Same splits: test-row counts per seed are identical in both files (55,789 / 55,792 / 55,787 / 55,791 / 55,791), and `n_true_viol` per seed is identical to the v2 artifacts (e.g. 9,809 and 9,772 for seeds 0 and 1). re-read OK.
   - Mean converged N-1 min_vm 0.93983 (from `data/dataset.parquet`, n = 278,955): re-read OK.
6. **Must not claim:** that the baseline rows were re-run under M2 (they were not, and they do not need to be). Never quote the v1 ridge/histgb rows that sit in the same file (ridge 3.23% missed, histgb 6.91% missed at 0.90 are **M1-era numbers**; M1/M2 rule).
7. **Consistency:** Table 1 caption; the .tex comment l.202-204 (accurate: "copied verbatim … byte-identical"); NS-04/E8 (false-flag column); NS-17 (R² sign, below).
8. **Page cost:** 0 (caption clause).

## P-027 — Clarity minors (NS-17, NS-18, NS-20, NS-21, NS-22, NS-23, NS-24, STS-14)

### P-027a — NS-17: no direction cues on the metrics
1. P-027 / NS-17. MINOR.
2. Anchors: l.213 Table 1 header "Model & MAE ($10^{-3}$ pu) & $R^2$"; l.246 Table 2 header "Model & Target & Esc. & Cov."
3. Old text: the two header rows as printed (l.213, l.246).
4. Content: one cue per metric, in the header or a caption clause. MAE: lower is better. R²: higher is better; ≤ 0 means no better than predicting the mean. Esc.: lower is faster. Missed: lower is safer. Speedup: higher is better. Cov.: should match Target. Explain why a baseline R² prints as "−0.00" (a tiny negative value, −0.0002, rounded), or print it at a precision where the sign is meaningful.
5. Numbers: train-mean R² −0.0002±0.0002 re-read OK (`data/screener_metrics.json`).
6. Must not claim: that R² near 0 means the train-mean model is "unbiased" or useful.
7. Consistency: C4 (the "Cov." vs "Target" vocabulary is set in C4; use the same words).
8. Page cost: 0.

### P-027b — NS-18: "accurately", "very fast"
1. P-027 / NS-18. MINOR.
2. Anchors: l.199 "Both surrogate models accurately predict the minimum"; l.388 "My models can predict N-1 under-voltage"; l.388 "both methods perform very fast, yet they".
3. Old text: "Both surrogate models accurately predict the minimum post-contingency bus voltage used by the gate to make its decision." (l.199); "At 90\% coverage, both methods perform very fast, yet they miss too many violations to be considered safe." (l.388)
4. Content: tie each adjective to a comparison, or drop it. Ridge MAE is about 12% below persistence, the do-nothing baseline. Histgb is about 63% below. "Very fast" at 0.90 means 2.04× (ridge) and 3.29× (histgb).
5. Numbers: ridge M2 MAE 3.7543±0.1328 ×10⁻³ (`data/tuned_metrics.json` m2 records) vs persistence 4.2457±0.0706 → gap 11.6% (per seed 8.95–17.09%). **MISMATCH vs ledger "~10%"**: the gap is 11.6%. Std-rule: gap 0.49 > 0.13, so it is real. histgb 1.5627±0.0758 → 63.2% below persistence. Speedups 2.04±0.11 and 3.29±0.30 (`tradeoff_curve_v2.json`), re-read OK.
6. Must not claim: "accurate" without the reference point; that ridge is much better than persistence.
7. Consistency: Results l.199; Conclusion l.388; abstract, if it adds a qualifier.
8. Page cost: 0.

### P-027c — NS-20: abstract and intro describe prior work differently
1. P-027 / NS-20. MINOR.
2. Anchors: l.81 "Past work has either replaced these solves with"; l.101 "Manoharan \cite{manoharan2026} utilized a fast computer model".
3. Old text: "Past work has either replaced these solves with surrogate models that check a group of cases at once, return a binary risk classification, or claim no missed unsafe scenarios with only a simple direct current (DC) model." (l.81)
4. Content: the three abstract categories must map one-to-one, in the same order, onto the three intro papers, and each must name the same distinguishing property.
   - manoharan2026: a population-level (per-window) bound on the violation rate among skipped cases, obtained with a random audit. Thermal only.
   - alcantara2026: a binary conformal flag. Voltage claimed, thermal demonstrated (`notes/prior-art.md` §6.1).
   - christianson2025: a zero-false-negative guarantee for DC power flow only.
   "Check a group of cases at once" does not match the intro's "checks if any single piece of equipment".
5. Numbers: none.
6. Must not claim: any characterisation of manoharan2026 beyond the verified record until the full-text re-read (P-028, `prior-art.md` §6.6). The lit note (`notes/lit/notes/Audited Selective Verification…md` §3) records a per-window rate guarantee that is "not a per-action worst-case one".
7. Consistency: P-028; OS-2 / NS-19 ("three distinct ways", other set); Top5-5 (abstract restructure; sequence after it).
8. Page cost: 0.

### P-027d — NS-21: figure glyphs and symbols
1. P-027 / NS-21. MINOR.
2. Anchors: l.155 "The three-way gate mechanism is shown above."; l.303 "The histogram above measures how far missed"; l.323 "Minimum bus voltage after a contingency across"; l.281 "Escalation (solid, left axis) and missed violations".
3. Old text: the captions at l.155, l.303, l.323, l.281 as printed.
4. Content:
   - Fig. 1 (`gate_schematic_v4.png`, viewed): each case is drawn as a dot (the point prediction) on a stem ending in a bar (the lower band edge). Neither glyph is named in the figure or caption. The figure's own labels are "escalation strip, one band width" and "under-voltage limit (0.94 pu)", and the caption should use the same terms.
   - Fig. 3 (`miss_depth_v3.png`, viewed): the axis says "d = 0.94 − Y". "Y" is never defined, and the text uses lower-case y (l.175), itself undefined (P-017). The panel labels "q̂@0.90 = 0.0052 / 0.0023" are undefined notation. "One certified bus" (l.303) should refer to a certified contingency. The grey strip is unexplained (P-025).
   - Fig. 4: state what the tallest-bin figure (14.1%) is there to rule out, which is a single-value pile-up of the kind the clip bug caused. The number itself is numbers-2b / P-008.
   - Fig. 2: the x-axis spans 0.70–0.99 while the text and Table 2 use 0.90–0.98. Say so, or crop in a rebuilt PNG (P-005 is rebuilding Fig. 2 anyway).
5. Numbers: q̂ 0.0052 / 0.0023 as printed in l.132 and in the PNG. Not re-derived here (numbers set).
6. Must not claim: anything in the Fig. 3 caption about the 0.0915 case (P-001).
7. Consistency: P-017 (y/Y, q̂ notation); P-001 and P-025 (one Fig. 3 rebuild); P-005 (one Fig. 2 rebuild); C4 (axis word).
8. Page cost: 0 (caption words ≈ +0.03, offset by the P-001 caption deletion).

### P-027e — NS-22: Table 2 skips 0.91–0.93
1. P-027 / NS-22. MINOR.
2. Anchor: l.248 "ridge  & 0.90 & 49.1$\pm$2.7" → l.249 "ridge  & 0.94".
3. Old text: the Table 2 rows at l.248-260 (0.90, then 0.94–0.98, for each model).
4. Content: either include 0.91–0.93, or give a caption reason for the gap. The emitter picks `OPS_TARGETS = [0.90, 0.94, 0.95, 0.96, 0.97, 0.98]` (`scripts/emit_v2_tables.py:8`). The curve file holds 0.70–0.99 (30 levels), and IV.4 / `data/missed_depth.json` use 9 targets, 0.90–0.98. The "9 coverage targets" at l.353 therefore refers to a grid the reader never sees in full.
5. Numbers: `tradeoff_curve_v2.json` → `coverage_levels` 0.70…0.99 (30), re-read OK; `missed_depth.json` → `coverage_targets` 9 values 0.90–0.98, re-read OK.
6. Must not claim: that the omitted rows were not computed.
7. Consistency: C1/numbers (l.353 "9 coverage targets"); C4.
8. Page cost: 0 with a caption reason; +0.1 if six rows are added.

### P-027f — NS-23: cryptic forward reference at l.199
1. P-027 / NS-23 (also STS-14, 5th anchor). MINOR.
2. Anchor: l.199 "The question of safety is not in the"
3. Old text: "The question of safety is not in the number of errors made but in the location of those errors."
4. Content: say at this point what "location" means (how far below the 0.94 limit a missed violation falls, i.e. miss depth, shown in Fig. 3), or move the idea to where Fig. 3 is discussed.
5. Numbers: none.
6. Must not claim: any depth-based safety reading that depends on the tail before N2 (P-003).
7. Consistency: P-024, P-001, E9.
8. Page cost: 0.

### P-027g — NS-24 + STS-14: sentences whose meaning is lost
All MINOR. Each needs one checkable statement. Content only.

- **l.107** "In this study, I do not check for overvoltage, although 73.1\% of converged N-1 rows the highest bus voltage is over 1.05 pu, or the upper bound of the acceptable voltage band." The sentence is grammatically broken (a missing preposition before "73.1%"). Content: 73.1% of converged N-1 rows have their highest bus voltage above 1.05 pu. Number: 73.136% (`data/dataset.parquet`, max_vm > 1.05 over 278,955 converged N-1 rows): **re-read OK**, no committed key (add to a facts JSON, d-figs). Do not claim that 1.05 is a verified regulatory bound unless it is cited (ANSI range in `prior-art.md` §7.3/§9.11).
- **l.167** "Escalation happens when the model predicts in the same interval where the band crosses the threshold." Content: a case is escalated exactly when L ≤ p̂ < L + q̂, i.e. the prediction lies within one band width above the limit. This overlaps Top-5 #2(a) (Theory shortening) and may disappear with it.
- **l.363** "This establishes the lower bound because, in split conformal prediction, I can be correct on average but not necessarily inside the band." "This" and "the lower bound" have no clear referent. Content: (i) the coverage guarantee is an average over cases, not a per-case promise; (ii) the 186 contingencies from one base case are related, so the unit of independence is the base case. Owned jointly with **P-010** (grouping / marginal vs conditional, other set) and E12/E13. Do not duplicate: one passage.
- **l.377** "Since the input data varies across different scenarios, I can conclude that any change in values from the audit was not due to constant features and was from dynamic data." Content: the audit has two checks. Check 2: rebuilding the four F1 columns from a fresh network, with every branch in service, reproduces them exactly (25 scenarios, max error 0.0), so F1 holds only pre-outage information. Check 3: for every outaged element, F1 varies across base cases (0 elements with zero variance), so F1 is not a disguised element label. Source: `data/f1_leakage_audit.json` → `check_2_base_solve_integrity` (n 25, all max_abs errors 0.0) and `check_3_variation.variance_across_scenarios_for_fixed_element.*.n_elements_with_zero_variance` = 0: **re-read OK**. Folds into E14 (ablation rewrite, other set).

Page cost for P-027g: 0.

---

## Summary table

| ID | Sev. | Net pp | Depends on | Numbers (status) |
|---|---|---|---|---|
| P-018 | MINOR | 0 | C1; bibitem verification | pandapower 3.5.4 (OK) |
| P-019 | MINOR | +0.03 | new facts artifact if counts printed | 9/186 (OK); 100% ×2 (OK); 0.13–4.53% (OK) |
| P-020 | MINOR | +0.03 | N2 | 45, 37/7/1 (OK); flagged 37–39 (**MISMATCH vs ledger 38–39**); certified: histgb@0.90 2/45 every seed; ridge@0.90 seed 1 1/45 (1 of 8 test); histgb@0.97 seed 3 1/45 (1 of 9 test) (OK); Δmissed ≤ 1.3e-5 (OK) |
| P-021 | MINOR | −0.1 (inside Cut-5) | Cut-5 | 0.9012, 24 (OK); 0.7199, 39 (OK); 0/3000 (OK) |
| P-022 | MINOR | 0 | — | — |
| P-023 | MINOR | 0 | E5 headline; C13 | 3.29±0.30, 4.72±0.98, 63.7±5.1, 1.58±0.12, 0.83±0.24, 0.79±0.21, 5.84±1.25 (all OK); ddof=0 (OK) |
| P-024 | MINOR | 0 | P-001, N2 | 74/55/26.7/21.4% pooled (OK); 78.6% (OK); max 0.0915 both models (OK) |
| P-025 | MINOR | 0 | P-001, P-004, P-006, Cut-2, E15 | gamma 0.5 (OK); strip 0.005 (OK) |
| P-026 | MINOR | 0 | NS-04/E8 | baseline rows (all OK); same splits (OK); 0.93983 (OK) |
| P-027a-g | MINOR | 0 (+0.1 if Table 2 rows added) | C4, P-017, P-010, E14, P-028, Top5-5 | ridge vs persistence 11.6% (**MISMATCH vs ledger ~10%**); 73.136% (OK, no key); audit 25 / 0.0 / 0 (OK) |
| **Group** | | **≈ −0.04** (≈ +0.06 if Cut-5 carries P-021) | | |
