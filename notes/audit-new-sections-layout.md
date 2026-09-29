# Audit — `notes/new-sections-layout.md`

Verification pass run 2026-08-19 at git HEAD `03e1136`, clean tree. Every number was located in
its artifact and re-read; every citation key was resolved against `report/paper_current_STS.tex`
and `notes/prior-art.md` / `notes/lit/notes/`; every insertion point was checked line-by-line.
`notes/RUN_REPORT.md`, `writing-background.md` and `section-V-writing-context.md` were not read.

Nothing in the layout or the manuscript was modified.

---

## A. Anchor and file identity

| claim | artifact value | file | path | verdict |
|---|---|---|---|---|
| sha256 `754be12b…21c22` | `754be12b5f025c8e271a130e2f8548163251732c7e94e05283799278ee421c22` | `report/paper_current_STS.tex` | `shasum -a 256` | MATCH |
| 344 lines | 344 | same | `wc -l` | MATCH |
| `git diff HEAD` empty | empty | same | `git diff HEAD` | MATCH |
| last touched at `6082204` | `6082204` | same | `git log -1 --` | MATCH |
| git HEAD `03e1136` | `03e1136` | repo | `git log -1` | MATCH |

## B. Insertion points (§1) — line number + quoted preceding sentence

| # | claimed line | quoted sentence ends | verdict |
|---|---|---|---|
| A | after 86, before `\section{Background}` at 89 | "…why there must be a certain floor for escalation." | MATCH (89 = `\section{Background}`) |
| B | after 96, before `\section{Method}` at 99 | "…specific generator reactive power limits are enforced." | MATCH |
| C | replaces 104 | n/a | MATCH (104 = the 1.0–1.12 sampling sentence) |
| D | after 141, before `\section{Results}` at 144 | follows `\end{figure}` | MATCH (141 = `\end{figure}`) |
| E | after 227, before `\subsection{The faster model…}` at 229 | follows Fig. 3 float | MATCH |
| F | after 235, before Fig. 4 float at 241 | "…followed by bus 107 with 9.31\%." | MATCH (241 = `\begin{figure}`) |
| G | after 256 | "…most of the data is very close to the limit." | MATCH |
| H | after 258 | "…rather than guarantees on individual contingencies." | MATCH |
| I | replaces 260 | n/a | MATCH |
| Discussion paras at 256/258/260/262; Results subsecs at 213/229/233 | confirmed | — | MATCH |
| "no two collide", 9 distinct lines | 86, 96, 104, 141, 227, 235, 256, 258, 260 — 9 distinct | — | MATCH |
| single live `\ref{sec:…}` = `\ref{sec:discussion}` at 116 | only sec-ref in file is line 116 | `grep \ref{` | MATCH |
| stale comments at 134 "III-D", 220 "IV-B", 239 "IV-C" | all three present verbatim | — | MATCH |
| `\thesubsection` renders `IV.1` not `IV-B` | `\thesection` Romanized (line 50), `\thesubsection` not redefined, `article` | — | MATCH |

## C. §2-C — sampling correction

| claim | artifact value | file | path | verdict |
|---|---|---|---|---|
| `net.gen.p_mw` never assigned; six fields touched | `apply_scenario` def at :136, assigns p_mw/q_mvar (load), vm_pu/min_q/max_q/in_service (gen); no `gen.p_mw` | `feasibility/generate_dataset.py` | :136–144 | MATCH |
| gen `p_mw` read only at :57, :168 | :57 `_gen_p0` copy; :168 `feat["genp_"]` | same | grep | MATCH |
| 53 `genp_*` cols, nunique 1, std 0 (E-A4-1) | 53 / 1 / 0.0 | `data/dataset.parquet` | `genp_*` | MATCH |
| independent P `[1.0000, 1.1200]`, 0.00% outside, 750 bases | `[1.0000,1.1200]`, 0.00%, n=750 | `data/dataset.parquet` | `pload_i` ÷ case118 base | MATCH |
| regional P `[0.9009, 1.2310]`, 43.91% outside, 22.9% below 1.0 | `[0.9009,1.2310]`, 43.91%, 22.94% | same | same | MATCH |
| all-mode P 21.95% outside | 21.95% | same | same | MATCH |
| all-mode Q `[0.8156, 1.4083]`, 56.83% outside | `[0.8156,1.4083]`, 56.83% | same | `qload_i` | MATCH |
| pf draw `U(0.9, 1.15)`; `REG_JITTER = 0.10` at :110-112 | `REG_JITTER = 0.10` (:21), used :111 | `generate_dataset.py` | — | MATCH |
| the above cited to "writing-numbers §III-A corrections block" | that block states only touched/not-touched; carries **no** percentages or ranges | `notes/writing-numbers.md` | §III-A section | **MISMATCH (citation)** — values correct, row does not exist |
| "per-load" P/Q multipliers | `pload_i`/`qload_i` are **per-bus** (118 cols), not per-load (99 loads) | `data/dataset.parquet` | — | **MISMATCH (label)** |
| gen-outage share 0.249259, 374/1500 | 0.24925884, 374/1500 | `data/sampling_audit.json` + parquet | `prevalence` | MATCH |
| 45 failures, 1,500 N-0 base rows | 45 / 1500 | `data/dataset.parquet` | `~converged` | MATCH |
| 280,500 / 1,500 / 279,000 / 278,955 | identical | same | counts | MATCH |
| rows 1–4, 4–5, 10 pointers | rows 1–4 ok, 4–5 ok, 10 ok | `writing-numbers.md` | table order | MATCH |

## D. §2-D — Theory / barrier height

| claim | artifact value | file | path | verdict |
|---|---|---|---|---|
| ridge S_mean 0.603785 ± 0.075685 → 0.721343 ± 0.065644, RISES | 0.6037845811 ± 0.0756853388 → 0.7213426624 ± 0.0656438241 | `data/barrier_height.json` | `summary_at_090.*.ridge.S_mean_over_qhat_at_090_*` | MATCH |
| histgb S_mean 0.791930 ± 0.074329 → 0.343935 ± 0.061752, FALLS | 0.7919301553 ± 0.0743288454 → 0.3439349 ± 0.0617518 | same | histgb | MATCH |
| ridge diff +0.117558, larger std 0.075685, exceeds | +0.1175580813 / 0.075685 → 1.55× | derived | — | MATCH |
| histgb diff −0.447995, larger std 0.074329, exceeds | −0.4479952 / 0.074329 → 6.03× | derived | — | MATCH |
| within-network margins case118 2.5×, case30-thermal 5.7× | 2.486× / 5.749× | derived | — | MATCH |
| ridge barrier ×1.34 vs overshoot ×1.60 | 1.3416 / 1.6004 | `barrier_height.json` | `q_hat_…`, `mean_overshoot_given_viol…` | MATCH |
| histgb barrier ×1.03 vs overshoot ×0.45 | 1.0281 / 0.4465 | same | same | MATCH |
| identity gap `5.551115123125783e-17` | `5.551115123125783e-17` | same | `identity_checks.max_identity_gap` | MATCH |
| S_p99 ridge 6.548389 → 4.390677, diff −2.157712, larger std 0.572435 | 6.548388859 → 4.390677118, −2.157712, stds 0.572435 / 0.338526 | same | `S_p99_over_qhat_at_090_*` | MATCH |
| S_p99 histgb 9.774697 → 5.213065, diff −4.561632, larger std 0.649338 | identical; stds 0.574073 / 0.649338 | same | same | MATCH |
| S_p99 FALLS for both; P-BH-6 wrong | both negative, both exceed | same | — | MATCH |
| counterexample set empty by construction; 19,625 missed / 6,128,100 test (§0.2) | `n_missed` 19,625; `n_test` 6,128,100 over 180 rows | `data/barrier_height_long.parquet` | column sums | MATCH |
| "4.6M" NO SOURCE | neither population is 4.6M | — | — | MATCH |
| `data/fig_identity.png` + manifest carries `apa_citation`; `.tex` does not | manifest has `apa_citation` (Matplotlib/Hunter 2007); 0 hits in `.tex` | `data/fig_identity.manifest.json` | `apa_citation` | MATCH |

## E. §2-E — flag branch

| claim | artifact value | file | path | verdict |
|---|---|---|---|---|
| `gate_eval.py:19  flag = pred < limit` | :19 is `certify = lower >= limit`; **flag is :20**; `lower` is :18 | `feasibility/gate_eval.py` | :18–20 | **MISMATCH (off by one)** |
| invariance `nunique == 1`, 30 targets, 10 (model,seed) groups | max nunique 1 over `flag_safe/flag_viol/flag_precision/flag_recall`; 30 targets; 10 groups | `data/flag_confusion_long.parquet` | groupby | MATCH |
| flag precision ridge@0.94 0.560620 / 0.561265 | 0.5606201196 / 0.5612645113 | same | pooled / `flag_precision` mean | MATCH |
| flag precision histgb@0.97 0.856295 / 0.856372 | 0.8562945368 / 0.8563719297 | same | same | MATCH |
| ceiling ridge 0.691482 (seed-mean 0.692415) | 0.6914819203 / 0.6924150174 | same | `n_viol`/(`flag_viol`+`flag_safe`) | MATCH |
| ceiling histgb 1.009272 | 1.0092719923 | same | same | MATCH |
| false flags 6,155.8 vs 76.8 missed (ridge@0.94) | 6155.8 / 76.8 | same | `flag_safe` mean; `missed_viol_rate`×`n_viol` | MATCH |
| false flags 1,379.4 vs 80.8 (histgb@0.97) | 1379.4 / 80.8 | same | same | MATCH |
| margin p50 1.77 / 0.95 milli-pu | 0.0017661206 / 0.0009450434 | same | `ff_margin_p50` seed-mean | MATCH |
| 89.7% / 97.3% within 5 milli-pu | 0.8966875952 / 0.9726282660 | same | `ff_share_within_0p005` | MATCH |
| pooled percentiles CANNOT BE COMPUTED | only p50/p90/max/mean stored per seed; no raw margins | same | schema | MATCH |
| rows 12,13 / 15,16 / 14 / 17 pointers | correct in table order | `writing-numbers.md` | — | MATCH |

## F. §2-F — non-convergence

| claim | artifact value | file | path | verdict |
|---|---|---|---|---|
| 45 failures | 45 | `data/nonconverged_gate.json` | `n_nonconverged` | MATCH |
| 1,500 base rows excluded by design | 1500 | same | `n_base_rows_excluded_by_design` | MATCH |
| row pointers "(row 6)" for 45 and "(row 7)" for 1,500 | row 6 = violation rate; row 7 = boundary mass. 45 is **row 5**, 1,500 is **row 2** | `writing-numbers.md` | table order | **MISMATCH** |
| 0/45 certified ridge@0.94 | 0 across all 5 seeds | `nonconverged_gate.json` | `q1_q2_per_seed.ridge.target_0.94.all45.certified` | MATCH |
| 1/225 seed-rows histgb@0.97 | 1 certified over 45×5 | same | histgb `target_0.97` | MATCH |
| missed-rate delta 0.0000 at four decimals, negative for ridge | seed-mean +1.2e-05 (histgb) / −8e-06 (ridge); one histgb seed = **9.8e-05 → rounds to 0.0001** | same | `missed_rate_if_nc_are_violations` − `published_missed_rate` | PARTIAL — true on seed-mean, false on one per-seed value; the prose claim "< 0.0001" holds |
| all 45 are trafo 0/7/6 (IEEE 1/8/7), counts 37/7/1 | trafo_0 37, trafo_7 7, trafo_6 1 | same | `q3_top_elements` | MATCH |

## G. §2-G — break-even

| claim | artifact value | file | path | verdict |
|---|---|---|---|---|
| break-even figures NOT YET in `writing-numbers.md` | 0 hits for `break_even` | `notes/writing-numbers.md` | grep | MATCH |
| "(row: solve_time)" | no `solve_time` row exists in the provenance table | same | grep | **MISMATCH** — value itself is correct |
| `ms_solver` 9.14 | 9.14 (min over 400 timed solves) | `data/solve_time.json` | `ms_solver` | MATCH |
| dataset cost 280,500 solves | 280500 | `data/break_even.json` | `generation.solves_recorded_in_dataset` | MATCH |
| `data/parallel_speedup.json` exists for parallelism-invariance | present, 1–10 workers | `data/parallel_speedup.json` | `scaling` | MATCH |

## H. §2-H / §8 — drift (2C, 2D, 2E)

| claim | artifact value | file | path | verdict |
|---|---|---|---|---|
| (a) shifted 0.7952977736840497 ± 0.017998553298487808 | identical; per-seed .803610/.822659/.798313/.780672/.771236 | `data/drift_n0_stratum_long.parquet` | ridge, cal=benign→test=marginal, target 0.90 | MATCH |
| (b) benign control 0.8963930839821412 ± 0.011400530217031263 | identical; per-seed match §8 exactly | same | benign→benign | MATCH |
| (c) in-dist marginal 0.8844348119083406 ± 0.026846519782127615 | identical; per-seed match §8 exactly | same | marginal→marginal | MATCH |
| gap (b)−(a) +0.10109531029809142, 5.6× | +0.1010953103, 5.62× | derived | — | MATCH |
| gap (c)−(a) +0.089137038224291, 3.3× | +0.0891370382, 3.32× | derived | — | MATCH |
| histgb gap 0.002868 vs std 0.015195 → FAILS std rule | −0.0028680772, larger std 0.0151948 | same | histgb | MATCH |
| histgb escalation 0.028 benign → 0.591 in-dist marginal | 0.028454 / 0.591408 | same | `escalation` | MATCH |
| median split `n0_min_vm` = 0.9433575252264039 | 0.9433575252264039 | `dataset.parquet` / drift parquet | `median_n0_min_vm` | MATCH |
| benign violation rate 0.15373696096354447 over 139,485 rows | 0.15373696096354447, 21,444/139,485 | `data/dataset.parquet` | `min_vm<0.94` given `n0_min_vm >= split` | MATCH |
| marginal 0.19577686957768695 over 139,470 rows | 0.19577686957768695, 27,305/139,470 | same | — | MATCH |
| SINGLE-PATH label; drift parquet has no violation-rate field | schema has no such column | `drift_n0_stratum_long.parquet` | columns | MATCH — label correct |
| 2D histgb line→trafo 0.022810 vs control −0.001425; ridge 0.003776 / 0.005931 | 0.022810 / −0.001425 / 0.003776 / 0.005931 | `data/drift_element_type_long.parquet` | mean(target−coverage_emp) | MATCH |
| 2E ESS 0.79–0.82 | 0.7894–0.8220 | `data/drift_loading_tilt_long.parquet` | `ess_fraction` | MATCH |
| 2E realized shift +0.0046 to +0.0054 | 0.004556–0.005397 (tilted − untilted test mean, corrected per-seed route); the artifact's own `realized_*` columns are defective and give 0.004416–0.006081 | `writing-numbers.md` corrected values | — | MATCH via corrected route only |
| 2E "window 7.7 pp wide" | no artifact carries it; base `agg_loading` full range is **10.96 pp**; 1.019–1.096 appears only in `notes/ai-prompt-log.md` | — | — | **NOT FOUND in any artifact** |
| gen-outage prevalence +4.8 pp (0.2253 vs 0.2733) | 0.22528587 vs 0.27323439, delta = 4.79 pp | `dataset.parquet` | `gen_out>=0` by stratum | MATCH |
| argmin-bus composition shifts toward IEEE 76/53/107 | top argmin buses 75/52/106 (0-based) = IEEE 76/53/107 | same | `argmin_bus` | MATCH |
| `agg_loading` p = 0.012, 0.13 sigma | p = 0.01196, 0.1297 sigma | same | two-sample t on base rows | MATCH |
| `corr(n0_min_vm, agg_loading)` = −0.0724 | −0.0723904 | same | — | MATCH |

## I. §2-I / §0.4 — case30-thermal and the thermal chain

| claim | artifact value | file | path | verdict |
|---|---|---|---|---|
| case118 boundary mass 56.86% | 0.5686293488 | `data/dataset.parquet` | `0.94<=min_vm<0.945` | MATCH |
| case30-thermal boundary mass 7.0862% | 7.0862 | `case30_thermal_frozen.json` | `boundary_mass_pct` | MATCH |
| case118 violation rate 17.4756% | 0.1747557850 | `dataset.parquet` | `min_vm<0.94` | MATCH |
| case30-thermal violation rate 15.3967% | 15.3967 | `case30_thermal_frozen.json` | `violation_rate_pct` | MATCH |
| histgb esc 5.84% ± 1.25, speedup 17.91× ± 3.71 at 0.97 | 5.84 ± 1.25, 17.91 ± 3.71 (5 seeds, ddof=0) | same | `records[]` | MATCH |
| N-0 acceptance 18.63%, range [0.87, 0.99] | 0.186335; chosen `lo` 0.87 / `hi` 0.99 | `h3_build_stats.json`, `h2_range_sweep.json` | — | MATCH |
| acceptance exactly 0.000 at every `lo` 1.00→0.94 | 7 values, all 0.0 | `h2_range_sweep.json` | `h2.sweep` | MATCH |
| N-1 loading >100%: 0.214846 (case30-thermal) | 0.2148455285 | `h3_build_stats.json` | `n1_loading.share_above_100` | MATCH |
| N-1 loading >100%: 0.9989105691 (case30-published, full) | 0.9989105691056911 over 61,500, 0 failures | `data/thermal_check.json` | `networks.case30.thermal_sweep.line_loading.share_above_100` | MATCH |
| rows 20/21/46/47–49/50/51 pointers | all correct in table order | `writing-numbers.md` | — | MATCH |
| crossing INDETERMINATE: histgb@0.96 = 0.41 std, 2/5 seeds | 0.41 std, 2 of 5 below 0.01 | `case30_thermal_frozen.json` | `records[]` | MATCH |
| decidable target 0.97 = 1.20 std, 5/5 | 1.20 std, 5/5 | same | — | MATCH |
| ridge exclusion of 0.97 rests on 0.22 std | −0.22 std | same | — | MATCH |
| line-260 superseded four are case30-published: 20.0%, 28.8%, 8.96±0.91%, 11.27±1.02× | 20.0146, 28.8081; esc@0.93 8.96±0.91%, speedup 11.27±1.02× | `case30_frozen.json`, `case30_tradeoff_curve.json` | `boundary_mass_pct`, `violation_rate_pct`, records at 0.93 | MATCH |
| line 72 (abstract) carries the same four | all four present at :72 | `.tex` | :72 | MATCH |
| "Only 86 of the 1,500 base cases above 0.95 pu" circular; 46.18% rejected; min `n0_min_vm` = 0.94000004 | 86 bases; min 0.940000036; acceptance predicate at `generate_dataset.py:256` | `dataset.parquet`, source | — | MATCH (rejection share not re-derived — see closing) |
| no thermal-chain value appears in the `.tex` (grep 0.9989/0.9927/99.89/99.27/100%) | 0 hits each | `report/paper_current_STS.tex` | grep | MATCH |
| §0.4 "NO SOURCE for 0.9927" | no occurrence anywhere in `data/` | — | grep | MATCH |

## J. §3 — 2F concentration dropped

| claim | artifact value | file | path | verdict |
|---|---|---|---|---|
| six named scalars are SINGLE-PATH (no per-seed counterpart) | `per_seed_depth` carries only `q_hat/n_missed/n_deep/max_depth/median_depth`; all six exist only as pooled scalars | `data/qlimit_class.json` | — | MATCH |
| off-setpoint indicator present in 1.000000 of deep-miss rows and of all 278,955 converged N-1 rows | 1.0 and 1.0; `n_rows` 278,955 | same | `share_with_any` | MATCH |
| baseline mean 20.799 vs 21.328 / 21.453 | 20.799294 / 21.327586 / 21.452830 | same | `offsetpoint_gens*` | MATCH |
| "difference **0.7285** against stds 0.973412 and 2.40071" | 0.7285 = 21.5278 − 20.7993, a **different (per-seed-mean) deep figure**; the quoted means give 0.5283 and 0.6535. Neither 21.5278 nor either std exists in `qlimit_class.json` | `data/qlimit_class.json` | — | **MISMATCH — internally inconsistent, and not in any data artifact** |
| verdict "fails the std rule" | holds under every pairing (0.5283 / 0.6535 / 0.7285 all < 0.973412) | derived | — | MATCH (conclusion survives) |

## K. Citations

| key | resolves? | local support for the attached claim | verdict |
|---|---|---|---|
| `manoharan2026` | bibitem :309; `notes/lit/notes/Audited Selective Verification….md` full extraction (audit/skip, LODF score, per-window risk control, thermal-only) | supports §2-A and §2-G's "audited population control" / "distribution-free risk control" | **PASS on resolution; MISMATCH on anchor** — layout cites `prior-art.md §6`, which is alcantara2026's full-text read; Manoharan is at §2/B5 |
| `alcantara2026` | bibitem :311; `prior-art.md` §1 A1, §6, §7.1 | §6 = full text of arXiv:2602.07995v2; §7.1 = title check | MATCH |
| `christianson2025` | bibitem :313; `prior-art.md` §7.2 (PMLR page + BibTeX, pp. 527–539) | supports the ICNN comparison | MATCH |
| `ejebe1979` | bibitem :315; `prior-art.md` §3 pins it as the canonical Automatic Contingency Selection reference, VERIFIED [SEARCH], vol/no/pages given | layout labels it "TODO — currently no keyed entry" | **MISMATCH (label)** — the bibkey string is absent but the citation is resolved and pinned at §3 |
| `bates2021` | bibitem :307; `.tex` comment :294 ("publisher PDF"); 0 substantive hits in `prior-art.md` | layout's "TODO" is correct | MATCH |
| `nerc` | bibitem :305; zero `nerc`/`TPL-001` hits in `prior-art.md`; `.tex` :299-300 self-flags the missing verification date | — | MATCH |
| `ansi2020` | bibitem :341; `prior-art.md` §7.3 | §7.3 confirms bibliographic identity from a NEMA front-matter excerpt and explicitly says the 0.917 numeric is **not** verified against the paid standard | MATCH — layout's characterisation is exact |
| `lei2018`, `vovk2005`, `romano2019`, `barber2021`, `tibshirani2019` | all have bibitems; 0 hits each in `prior-art.md`; verification recorded only in the `.tex` comment block | layout says "per the `.tex` comment block at lines 289–300" — block runs 289–301, statements at 290–300 | MATCH (line range off by one at the closing rule) |
| `tibshirani2019` cited for weighted conformal (2E) | resolves; **no `notes/lit/` extraction note exists** for it | — | PASS on resolution; NO LOCAL NOTE |
| GNN recall figure (§2-A) marked NO SOURCE | `notes/lit/notes/Graph Neural Networks….md` §4 carries under/over-voltage recall values (Fig. 7 bar-label transcription, flagged approximate, e.g. 118-bus N-1 under 53.9/53.8) | no *data* artifact; a local extraction note does carry figures; also **no bibkey exists** for this paper in the `.tex` | **MISMATCH (over-strict)** |

## L. §5 — NO SOURCE / SINGLE-PATH / INDETERMINATE / SUPERSEDED labels

| label | verdict |
|---|---|
| GNN recall figure = NO SOURCE | **MISMATCH** — see K |
| "around 14%" bin share (line 235) = NO SOURCE, "no artifact located" | **MISMATCH** — reproduces exactly: max 0.001-pu-wide bin = **14.06%** of converged N-1 rows, `data/dataset.parquet` |
| S ratios 0.604→0.219 / 0.443→0.482 = NO SOURCE | MATCH (measured values differ and invert) |
| "4.6M cases" = NO SOURCE | MATCH (19,625 and 6,128,100) |
| stratum rates 24.3% / 4.7% = NO SOURCE | MATCH (measured 15.3737% / 19.5777%) |
| in-dist marginal 0.7970 = NO SOURCE | MATCH (measured 0.884435; 0.7970 is within 0.0017 of the shifted 0.795298) |
| thermal 0.9927 = NO SOURCE | MATCH |
| break-even rows not yet in `writing-numbers.md` | MATCH |
| stratum violation rates SINGLE-PATH — RESOLVED | MATCH (rows exist; drift parquet has no such field) |
| home ZIP (R14) = NO SOURCE | MATCH — `notes/sts-constraints.yaml` R14 states it explicitly |
| crossing location INDETERMINATE (§2-I / Amendment 4) | MATCH — and no other layout entry quotes 0.96 as settled |
| "zero counterexamples" WITHDRAWN | MATCH — 8 mentions, all prohibitive; no entry uses it as a result |
| S-ratio direction UNWRITABLE as single-direction | MATCH — every use in the layout is per-model |
| 2F concentration DROPPED | MATCH — no layout entry uses `top_bus_share` etc. |
| 0.917 pu provenance defect | MATCH as a defect; **internal cross-reference error** — §2-B points to "§5 erratum E-A4-7"; E-A4-7 is in **§6**, not §5 |
| §2-C SUPERSEDED framing (§0.1, §0.3, §0.4) | MATCH on every measured column |

## M. §6 — Errata

| id | verdict |
|---|---|
| E-A4-1 gen values never scaled | MATCH (:104 vs :136-144; 53 `genp_*` nunique 1, std 0) |
| E-A4-2 multiplier range true only for independent-mode load P | MATCH (43.91% / 56.83% reproduced) |
| E-A4-3 "the remainder failing to converge" implies 1,545 | MATCH (45 real failures; 1,500 are N-0 base rows) |
| E-A4-4 line 262 "we did not test N-2" | MATCH (24.93%, 69,532/278,955; `P_GEN_OUT = 0.30` at :28, drawn at :128) |
| E-A4-5 model-safety ordering not general | MATCH — case118 ridge lower at all targets; case30-published 1.49±0.53 vs 1.47±0.20 (0.03 pp, inside one sigma); case30-thermal ridge 6.087% vs histgb 2.226% (inverted) |
| E-A4-6 both "sub-1%" crossings fail at one sigma | MATCH — :186 0.79+0.21 = 1.00; :196 0.83+0.24 = 1.07; ridge 0.95 → 67.9%/1.48×; histgb 0.98 → 72.0%/1.39× |
| E-A4-7 ANSI 0.917 from NEMA front matter | MATCH (`prior-art.md` §7.3) |
| E-A4-8 `nerc` has no `prior-art.md` entry | MATCH (0 grep hits; `.tex` :300 self-flags) |
| E-A4-9 Fig. 1 embeds M1-sized schematic | MATCH — :138 `gate_schematic_v2.png`; M1 `q_hat` 0.002557109746803765 (`tradeoff_curve.json`), M2 0.002290702766310826 (`tradeoff_curve_v2.json`); v3 exists; `erratum.md` E1 records it |
| E-A4-10 line 92 "only active constraint" | MATCH — 73.14% of N-1 and 73.40% of N-0 exceed 1.05 pu |
| E-A4-11 line 260 circular | MATCH — predicate at `generate_dataset.py:256`; min `n0_min_vm` = 0.94000004 |
| E-A4-12 acknowledgments URL | MATCH — :287 = `rajsaha-blip` = `upstream`, HEAD **990c3c5**; local and `origin` at **03e1136**; `notes/` gitignored (`.gitignore:23`) |
| E-A4-13 zero subsection labels; three IEEEtran-style comments | MATCH — 12 labels, none on a subsection |
| E-A4-14 abstract pairs case118 ridge with case30 histgb | MATCH — 11.27× is histgb@0.93; ridge crosses at 0.92 with 2.98× |
| E-A4-15 two voice families | MATCH exactly — `we`×17, `our`×5, `us`×1, `the authors`×1 at :287, zero `I`/`my` outside comments (3 comment lines) |
| E-A4-16 `erratum.md` E1 cites a dead path | MATCH — E1 says `paper_current.tex:112`; file is now `paper_current_URTC_20260808.tex` and :112 still embeds `gate_schematic_v2.png`; E1:46 says "There is no `urtc-submission` tag" — the tag exists, object **23bc760** → commit 8cefaa7 |

## N. §4 — Page budget

| claim | verdict |
|---|---|
| no TeX toolchain (`pdflatex`/`xelatex`/`latexmk` absent; `/usr/local/texlive` empty; `/Library/TeX` absent) | MATCH — all three absent from PATH; neither path exists |
| ~11.0 pp body, +8 section increments, ~20.45 pp total, 0.45 pp over | UNVERIFIABLE — planning estimates, self-labelled as such |
| §2-A "APA line required by R10" | MATCH — `notes/sts-constraints.yaml` R10 requires an APA line beneath every figure and table; `.tex` has 0 |

## O. Internal consistency of the layout

| finding | verdict |
|---|---|
| §1 row C calls it "§III-A replacement"; §2-C heading calls it "§IV-A replacement" | INCONSISTENT (pre- vs post-renumbering naming, both defensible in isolation) |
| §2-B points to "§5 erratum E-A4-7"; the errata table is §6 | INCONSISTENT |
| §2-G cites "(row: solve_time)" while §5 correctly records break-even rows as missing | INCONSISTENT |

---

## Could not verify

- **Page counts (§4).** No TeX toolchain on this machine; every page figure is an unmeasured
  estimate. The layout says so itself; the toolchain absence was confirmed, the numbers were not.
- **Word counts** (~550 / ~220 / ~300 / ~900 / ~450 / ~200 / ~250 / ~500 / ~450). These describe
  text that does not exist yet.
- **The 46.18% rejection share** in §2-I / E-A4-11. Rejected draws are not written to
  `data/dataset.parquet` (`sampling_audit.json` states this explicitly) and the generator was not
  re-run; the figure could not be re-derived from a committed artifact.
- **`GEN_REJECTED` = 1,287 underlying `break_even.json`.** The artifact's own
  `rejected_provenance` field says it is a hardcoded constant whose source run log is not
  committed — unverifiable by construction.
- **2F stds 0.973412 / 2.40071 and the 21.5278 deep-miss mean.** Present only in
  `notes/RUN_REPORT.md`, which was excluded by instruction; these lines were seen only as
  incidental grep output while locating the numbers, and the file was not opened. They are absent
  from `data/qlimit_class.json`.
- **The 2E "7.7 pp window."** The 1.019–1.096 span it derives from appears only in
  `notes/ai-prompt-log.md` prose; no artifact carries it, and the artifact-derivable base
  `agg_loading` range is 10.96 pp.
- **Second-order citation support for `lei2018`, `vovk2005`, `romano2019`, `barber2021`,
  `tibshirani2019`.** No `notes/lit/` extraction notes exist for any of the five, so only the
  existence of the bibitems and the `.tex` comment block's fetch dates were verified — not that
  they support the specific claims §2-D and §2-H will attach to them.
- **`notes/RUN_REPORT.md`, `writing-background.md`, `section-V-writing-context.md`.** Not read,
  per instruction. The latter two are in fact absent from the repository, consistent with the
  layout's own header.
