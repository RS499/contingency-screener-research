# Reproducibility fixes

> **Stale, 2026-07-21.** This record says numba is not installed; numba is now pinned and installed
> (numba 0.66.0), and the environment list here omits dependencies added since (numba, matplotlib,
> python-igraph). The pinned, complete list is requirements.txt.

Record of two repairs to the feasibility setup: rebuilding the virtual environment, and reconstructing the missing sweep script behind gonogo.md.

## 1. Virtual environment rebuilt on Python 3.13

The checked-in `.venv` was broken. Its `pyvenv.cfg` claimed version 3.13.9, but the interpreter resolved to Python 3.12.4, and no packages were installed. It could not run the feasibility scripts.

Fix: removed the old `.venv` and recreated it with `/opt/anaconda3/bin/python3.13`, then installed from `requirements.txt`. Python 3.13 was chosen to match the interpreter that produced the original numbers.

Resulting environment:

- Python 3.13.9
- pandapower 3.5.4
- numpy 2.3.5
- pandas 2.3.3

These match the pinned versions exactly. `straddle.py` runs inside the venv and produces the expected output. numba is not installed, so pandapower runs without it, which matches the "numba off" method note in gonogo.md.

Setup used:

```
rm -rf .venv
/opt/anaconda3/bin/python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## 2. gonogo.py reconstructed

The sweep script behind gonogo.md was not in the repository, so its table could not be re-run. I rebuilt it as `feasibility/gonogo.py` from the `straddle.py` template. The one structural change: `straddle.py` draws per-bus non-uniform multipliers, while `gonogo.py` scales the whole load uniformly to each loading level. Both run full N-1 (1 base case plus 186 branch outages = 187 cases per level).

To follow the documented method, the reconstruction uses Newton-Raphson with a flat start (`init="flat"`), numba off, and the same violation and near-limit definitions gonogo.md lists, including the over-voltage and thermal bands (both inert on case118, since thermal ratings never bind).

### Comparison against the original table

Every structural column reproduces exactly at all five loading levels.

| Loading | Column | gonogo.md | Reconstructed | Match |
|--------:|--------|----------:|--------------:|:-----:|
| 100% | Cases / Near / Viol / NonConv / MinV | 187 / 175 / 12 / 0 / 0.902 | 187 / 175 / 12 / 0 / 0.902 | yes |
| 120% | Cases / Near / Viol / NonConv / MinV | 187 / 155 / 32 / 0 / 0.884 | 187 / 155 / 32 / 0 / 0.884 | yes |
| 140% | Cases / Near / Viol / NonConv / MinV | 187 / 0 / 185 / 2 / 0.750 | 187 / 0 / 185 / 2 / 0.750 | yes |
| 160% | Cases / Near / Viol / NonConv / MinV | 187 / 0 / 182 / 5 / 0.804 | 187 / 0 / 182 / 5 / 0.804 | yes |
| 180% | Cases / Near / Viol / NonConv / MinV | 187 / 0 / 154 / 33 / 0.735 | 187 / 0 / 154 / 33 / 0.735 | yes |

Non-convergence rate follows from the counts and also matches: 0.0% / 0.0% / 1.1% / 2.7% / 17.6%.

### Numbers that differ: solve times

The solve-time columns differ, as expected for wall-clock timing measured on a different machine and run. They are the only numbers that do not reproduce.

| Loading | mean_ms (orig / repro) | median_ms (orig / repro) | p95_ms (orig / repro) |
|--------:|-----------------------:|-------------------------:|----------------------:|
| 100% | 11.55 / 7.91 | 9.01 / 7.86 | 19.19 / 8.08 |
| 120% | 9.17 / 8.17 | 8.36 / 8.03 | 15.58 / 8.56 |
| 140% | 8.66 / 8.08 | 8.09 / 7.94 | 9.80 / 8.82 |
| 160% | 8.94 / 8.53 | 8.54 / 8.47 | 9.47 / 8.73 |
| 180% | 9.77 / 9.85 | 9.72 / 9.75 | 10.21 / 10.37 |

The reconstructed means sit in the same 8 to 10 ms band as the original. The visible gap is in the p95 at 100 and 120% (original 19.19 and 15.58 versus reconstructed 8.08 and 8.56). The original run had a slow tail on the early cases, most likely first-call warmup or system noise, that the reconstructed run does not show once the solver is warm. This does not affect any decision: the GO gate requires p95 under 100 ms, and every value on both runs clears it with wide margin.

### Verdict

The GO decision and all convergence and voltage findings in gonogo.md reproduce exactly. Only the solve-time tail differs, and it stays well within the performance gate, so the verdict is unchanged. gonogo.md's table can now be regenerated from the repository with:

```
.venv/bin/python feasibility/gonogo.py
```

---

## 3. Interpreter hazard: bare `python` is NOT the committed environment (recorded 2026-07-26)

**All reproduction must use `.venv/bin/python`.** Bare `python` on `$PATH` resolves to **3.12.4 /
scikit-learn 1.8.0**; every committed manifest records **3.13.9 / scikit-learn 1.7.2**, which is
`.venv/bin/python`. This is the same failure mode as section 1 above (a `.venv` whose `pyvenv.cfg`
claimed 3.13.9 while the interpreter resolved to 3.12.4) — it has now recurred from the opposite
direction, so it is a standing hazard, not a one-off.

It is not silent. Under scikit-learn 1.8.0 the committed ridge path
(`StandardScaler` → `Ridge(alpha=10.0)` on the float32 design matrix, `surrogate.py:23-27`) emits
`divide by zero`, `overflow`, and `invalid value` RuntimeWarnings from `_ridge.py:305` and `:309`,
where the solver falls back to SVD. Under 1.7.2 the same call is clean. So the interpreter choice
changes the numerical path of a committed model, not just the version string.

Recorded because this is the same class of latent environment inconsistency that produced the
oracle error — `enforce_q_lims` missing from all the feasibility work — and that one was found late.

```
.venv/bin/python feasibility/run_all.py --seeds 5      # correct
python feasibility/run_all.py --seeds 5                # WRONG interpreter
```
