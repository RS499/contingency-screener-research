# RUN_REPORT — STS 2027 Autonomous Runbook

Append-only. Never rewrite an earlier section. Corrections are appended as `CORRECTION`
blocks quoting the original.

Run started: 2026-08-19T01:39:23Z
Interpreter: `.venv/bin/python` → Python 3.13.9

---

## STAGE 0 — Preflight

**Started:** 2026-08-19T01:39:23Z
**Ended:** 2026-08-19T01:52:10Z
**Git HEAD at start:** `9cba13e723ad3c034f54b5cf34b1fc97c3b5cc60`
**Tree dirty:** **YES** — 36 entries

### What ran

Read-only git and filesystem inspection plus one test run. No writes outside this file.

```
git rev-parse HEAD
git status --porcelain
git tag -l
git remote -v
git ls-remote --tags origin ; git ls-remote --tags upstream
git ls-remote --heads origin ; git ls-remote --heads upstream
git ls-files ; git ls-files notes/
git ls-files --error-unmatch CLAUDE.md
git check-ignore -v data/*.parquet paper_current_STS.tex
git log --all --oneline -- paper_current.tex
git log --all --name-only --pretty=format: -- '*.tex'
git ls-tree -r HEAD --name-only
git log --format='%h  %ci  %s'
.venv/bin/python --version
.venv/bin/python -m pytest feasibility/ -q --no-header
.venv/bin/python -m pytest "feasibility/test_tradeoff_v2.py::test_v2_curve_guard[T3_quantile_index_valid]" -q
```

No seeds. No experiment executed.

### Pre-registration

Not applicable. Stage 0 executes no experiment and produces no measured quantity.
Per §2a, pre-registration begins at Stage 2. Recorded here so its absence is not read
as an omission.

### Results

Stage 0 records repository state, not artifact values, so the §2d provenance fields
(`jsonpath`, `aggregation`, `content_sha256`) do not apply. Every row below is a direct
command output, reproducible from the command list above at HEAD `9cba13e`.

| # | Check | Result | Verdict |
|---|---|---|---|
| 1 | `git status --porcelain` clean? | 36 entries: 2 modified (`.gitignore`, `README.md`), 34 untracked | **DIRTY** |
| 2 | `urtc-submission` tag, local | `git tag -l` returns empty | **MISSING** |
| 3 | `urtc-submission` tag, remotes | `origin`: no tags. `upstream`: no tags. | **MISSING** |
| 4 | `report/` exists? | No such directory | **ABSENT** |
| 5 | `paper_current_STS.tex` tracked? | `pathspec did not match any file(s) known to git`; not gitignored | **UNTRACKED** |
| 6 | `notes/` backed up outside repo ≤7d? | `~/Desktop/notes-backup` absent; no `*notes*backup*` under `~/Desktop` or `~/Documents` | **NO BACKUP FOUND** |
| 7 | Interpreter version | `Python 3.13.9` | **PASS** — matches pinned env |
| 8 | Test suite | **1 failed, 27 passed, 21 warnings** in 34.52s | **RED** |

#### 8 detail — the failure

```
FAILED feasibility/test_tradeoff_v2.py::test_v2_curve_guard[T3_quantile_index_valid]
feasibility/test_tradeoff.py:34: KeyError: 'n_cal'
    def test_T3_quantile_index_valid(d):
>       n = int(d["n_cal"])
```

`d_v2` keys observed at failure: `seeds`, `coverage_levels`, `limit`, `ms_solver`, … — no
`n_cal`. Runbook §1c's diagnosis (a v1 guard reused against a v2 artifact with a different
schema) is **CONFIRMED** by the traceback, not assumed.

#### 8 detail — the return-instead-of-assert guards

Runbook §1c states 21. Measured count is **21**, exact match. Distribution:

| File | Count |
|---|---|
| `feasibility/test_dataset.py` | 9 |
| `feasibility/test_pipeline.py` | 6 |
| `feasibility/test_manifest.py` | 3 |
| `feasibility/test_tradeoff.py` | 3 |
| **Total** | **21** |

Each raises `PytestReturnNotNoneWarning`; each returns `str`. They pass regardless of the
returned value and enforce nothing.

#### Repository tracking inventory

`git ls-files` → **152** tracked files.

| Top-level path | Tracked files |
|---|---|
| `data/` | 84 |
| `feasibility/` | 42 |
| `scripts/` | 23 |
| `README.md` | 1 |
| `.gitignore` | 1 |
| `requirements.txt` | 1 |
| `notes/` | **0** |

#### Commit timeline (all 21 commits)

| SHA | Date | Subject |
|---|---|---|
| `9cba13e` | 2026-08-12 13:59 | Add pytest fixtures for the feasibility guards and extend them to the M2 curve |
| `884a077` | 2026-08-12 00:21 | Add feasibility write-ups with oracle-correction headers |
| `41d8161` | 2026-08-12 00:21 | Add bases-clearing-0.95 artifact with terminal-provenance manifest |
| `990c3c5` | 2026-08-03 20:42 | Rewrite README to match the committed repository ← **both remotes point here** |
| `ad048b0` | 2026-08-03 09:37 | Add miss-depth analysis, second-network probes, and case30 gate run |
| `9a76b6d` | 2026-07-30 12:53 | Add gate-aware (M2) hyperparameter tuning and v2 promotion |
| `d32f309` | 2026-07-28 10:43 | Add classical sensitivity-screen baselines and comparison |
| `d000fa7` | 2026-07-24 20:57 | Add coverage-sweep tradeoff curves and safety operating points |
| `91450f1` | 2026-07-23 12:45 | Add figure infrastructure and the six standalone figures |
| `71b37cf` | 2026-07-21 10:34 | Freeze the committed headline numbers and audit bus numbering |
| `49a527b` | 2026-07-19 15:01 | Add setpoint-clip artifact detection |
| `25d7a58` | 2026-07-18 18:34 | Add one-sided conformal calibration and the three-way gate |
| `619f467` | 2026-07-17 19:05 | Add trivial baselines, surrogate models, and scenario splitting |
| `d1c3d4a` | 2026-07-16 22:25 | Add solver timing measurement and the manifest infrastructure |
| `ea3bd21` | 2026-07-16 11:19 | Add dataset, manifest, pipeline, and tradeoff guard tests |
| `72f65ec` | 2026-07-14 19:03 | Add the diversified N-1 dataset generator and its validation |
| `bcbd863` | 2026-07-12 15:22 | Add IEEE 118-bus network model and N-0/N-1 feasibility studies |
| `c64b8b7` | 2026-07-11 12:21 | Add project scaffolding: gitignore and pinned dependencies |
| `a4df350` | 2026-07-09 21:59 | Update README.md |
| `3788ef1` | 2026-07-09 16:50 | Initial commit |

**There is no commit dated between 2026-08-03 20:42 and 2026-08-12 00:21.**

### Verification

Per §2c a `verifier` subagent must recompute independently after every stage. The roster is
built in Stage 1 (§3) and does not exist yet — `.claude/agents/` is **ABSENT**. Stage 0
therefore has **no verifier block**, and this is a known gap, not an omission.

Two-key applied where a second independent path existed:

| Claim | Key 1 | Key 2 (different path) | Agreement |
|---|---|---|---|
| Tag `urtc-submission` absent | `git tag -l` → empty | `git ls-remote --tags` on both remotes → empty | MATCH |
| `paper_current_STS.tex` untracked | `git ls-files --error-unmatch` → error | `git ls-tree -r HEAD --name-only \| grep tex` → none | MATCH |
| `notes/` untracked | `git ls-files notes/` → 0 | `git check-ignore` → `.gitignore` `notes/` rule | MATCH |
| 21 return-style guards | pytest warning count = 21 | per-file tally 9+6+3+3 = 21 | MATCH |
| Test failure cause | summary line | isolated re-run traceback showing `KeyError: 'n_cal'` at `test_tradeoff.py:34` | MATCH |

### Contradictions found

**C0-1 — The submitted manuscript has no git record at all.**
`git log --all -- paper_current.tex` returns empty. `git log --all --name-only -- '*.tex'`
returns empty. `git ls-tree -r HEAD | grep tex` returns nothing. `.tex` is not gitignored.
**No `.tex` file has ever been committed to this repository.** The URTC submission is dated
Aug 8 (CMT #74); the nearest preceding commit is `990c3c5`, Aug 3, five days earlier, and
`paper_current.tex` no longer exists in the working tree (confirmed absent; `notes/erratum.md`
E1 still cites it by that path).

**C0-2 — Both remotes are 4 commits behind local HEAD.**
`origin` and `upstream` both point at `990c3c5` (2026-08-03). Local HEAD is `9cba13e`
(2026-08-12). Unpushed: `ad048b0`, `41d8161`, `884a077`, `9cba13e`.

**C0-3 — Two remotes, and the manuscript cites the one that is not `origin`.**
`origin` = `https://github.com/RS499/contingency-screener-research.git`
`upstream` = `https://github.com/rajsaha-blip/contingency-screener-research.git`
`paper_current_STS.tex:287` prints `https://github.com/rajsaha-blip/contingency-screener-research`,
i.e. `upstream`. Which repository judges would reach, and whether it resolves publicly, is
not determined by this stage.

**C0-4 — Every `data/*.parquet` is gitignored.**
`.gitignore:5` = `data/*.parquet`. Confirmed ignored: `dataset.parquet`,
`sweep_results_long.parquet`, `flag_confusion_long.parquet`, `mondrian_element_long.parquet`.
Their `.manifest.json` sidecars are untracked-but-committable; the parquets themselves are
not committable under the current rule.

**C0-5 — `notes/` is gitignored in full.**
`.gitignore` block "`# Private — never commit to the public fork`" lists `notes/` and
`CLAUDE.md`. `git ls-files notes/` → 0. `CLAUDE.md` is untracked. This directory holds
`ai-prompt-log.md`, `prior-art.md`, `erratum.md`, `contribution-log.md`, and this report —
the evidentiary basis named for STS Task 5. Runbook §1d item 8 anticipates this
("the only irrecoverable directory here"); Stage 0 confirms it and adds that check 6 found
no backup.

**C0-6 — `CLAUDE.md` §7 states it is tracked; it is not.**
`CLAUDE.md` §7: "Root `CLAUDE.md` (this file): SHARED conventions, TRACKED in git."
`git ls-files --error-unmatch CLAUDE.md` → `did not match any file(s) known to git`.

**C0-7 — `CLAUDE.md` §6 names a `tests/` directory that does not exist.**
`CLAUDE.md` §6 layout lists `tests/`. `pytest feasibility/ tests/` → `ERROR: file or
directory not found: tests/`. All 28 tests live under `feasibility/`.

**C0-8 — `guard_python.sh` false-positive.**
The regex `(^|[;&|]|[[:space:]])python3?([[:space:]]|$)` matches the word `python` inside a
quoted `echo` string. `echo "=== python version ==="` was blocked with exit 2 even though the
command invoked `.venv/bin/python`. The hook is over-broad on shell-literal text, not on
interpreter selection. It correctly blocked a genuine `python3 --version` in the same run, so
the guard's intended behaviour is intact; only its precision is not.

### NO SOURCE / CANNOT BE COMPUTED

- **The SHA of the Aug 8 URTC submitted state — NO SOURCE.** The runbook's HALT block asks
  for `git tag urtc-submission <sha you identify as the Aug 8 submitted state>`. No commit
  exists in the Aug 6–10 window (§Results, commit timeline), and no `.tex` has ever been
  tracked (C0-1). No SHA in this repository corresponds to the submitted manuscript. I will
  not nominate a plausible substitute; per §0.6 and §8 that is a failure, not a fallback.
- **Whether `notes/` was ever backed up outside the repo — NOT FOUND.** I searched
  `~/Desktop/notes-backup` and `*notes*backup*` to depth 2 under `~/Desktop` and
  `~/Documents`. Absence at those paths is not proof of absence everywhere; I did not search
  the whole filesystem, external volumes, or cloud sync targets.
- **Whether either GitHub remote resolves publicly — NOT CHECKED.** `git ls-remote` succeeded
  against both, which proves reachability with the local credential, not anonymous public
  visibility. Determining that requires an unauthenticated fetch, which I did not perform.
- **Whether `.claude/session data` can reconstruct 2026-08-13→18 for the prompt log — NOT
  YET CHECKED.** That is Stage 1b's job and was not attempted in Stage 0.

### What I did not do, and why

- **No git write.** §0.1 and §8. The tree is untouched; `git status` is identical to entry.
- **No fix to the red test.** Runbook §1c assigns it to Stage 1; §2f halts before Stage 1.
- **No `report/` directory, no boundary hook, no file move.** Stage 1a, and the HALT precedes it.
- **No verifier subagent.** The roster is a Stage 1 deliverable; `.claude/agents/` is absent.
- **No prose.** §0.2. This file is a run log and a specification, not manuscript text.
- **Did not read** `notes/writing-background.md` or `notes/section-V-writing-context.md`
  (§3/§5 prohibition). Both are **ABSENT** from the repo regardless.
- **Did not read** `.claude/` session data or reconstruct the prompt log — Stage 1b.

### Next stage preconditions

| Precondition for Stage 1 | Status |
|---|---|
| Tree clean | **NOT MET** — 36 dirty entries |
| `urtc-submission` tag exists locally and on remotes | **NOT MET** — absent everywhere, and unconstructible (NO SOURCE above) |
| `notes/` backed up outside the repo within 7 days | **NOT MET** — none found |
| Interpreter 3.13.9 | MET |
| Test suite green | NOT MET — but this is Stage 1c's assignment, not a Stage 0 blocker |
| `report/` absent so Stage 1a can create it | MET |

**HALT fired** under §2f: "Any action would require a git write" and the explicit Stage 0
condition "HALT if the tree is dirty or the tag is missing." Both fired. Stage 1 not entered.

---

## CORRECTION C-1 — scope of the first Stage 0 block

**Raised:** 2026-08-19T02:46:51Z
**Trigger:** instruction stating "A previous Stage 0 run executed in `~/rise-project-research`,
a different clone; discard anything in `notes/RUN_REPORT.md` from that run."

**The premise does not hold, and I did not discard the block.** Evidence:

| Check | Result |
|---|---|
| `~/rise-project-research/notes/RUN_REPORT.md` | **ABSENT** — no Stage 0 output exists there |
| `~/contingency-screener-research/notes/RUN_REPORT.md` | EXISTS, 243 lines, mtime 2026-08-18 21:43:28 |
| Working directory of the Stage 0 session | `/Users/rajansaha/contingency-screener-research` (`pwd -P`) |
| Every Stage 0 command | prefixed `cd /Users/rajansaha/contingency-screener-research` |
| `git rev-parse --show-toplevel` | `/Users/rajansaha/contingency-screener-research` |

The first Stage 0 block was measured in **this** clone. Discarding it would delete valid
measurements, and §1 makes this file append-only with corrections quoting the original.
It stands. What follows supersedes it only where the repository has since changed.

**The instruction was nonetheless pointing at something real.** `~/rise-project-research`
exists, and it holds `paper_current.tex` (33,241 bytes, mtime **2026-08-08 23:05**) — the
URTC submission night. That file is the object my first block reported as unrecoverable.

**Superseded finding — C0-1.** Original text:

> **C0-1 — The submitted manuscript has no git record at all.** [...] **No `.tex` file has
> ever been committed to this repository.**

That was true at 2026-08-19T01:52:10Z and is **no longer true.** Between the two runs, commit
`8cefaa7` was created carrying `paper_current_URTC_20260808.tex`, and annotated tag
`urtc-submission` was placed on it. C0-1 is **RESOLVED by action taken outside this run**, not
withdrawn as an error.

**Superseded finding — the NO SOURCE on the tag SHA.** Original text:

> **The SHA of the Aug 8 URTC submitted state — NO SOURCE.** [...] No SHA in this repository
> corresponds to the submitted manuscript. I will not nominate a plausible substitute.

Declining to nominate a SHA was correct: none existed. One now does, created by committing
the recovered file rather than by identifying an existing commit. The tag annotation records
this distinction accurately and is quoted in the re-run block below.

**Not superseded.** Every other Stage 0 finding — C0-2 through C0-8, the test results, the
tracking inventory — was re-measured in the re-run block and is either unchanged or updated
there explicitly.

---

## STAGE 0 (RE-RUN) — Preflight, second execution

**Started:** 2026-08-19T02:46:51Z
**Ended:** 2026-08-19T03:04:40Z
**Git HEAD at start:** `9cba13e723ad3c034f54b5cf34b1fc97c3b5cc60` (unchanged)
**Tree dirty:** **YES** — 36 entries
**Reason for re-run:** instructed. Premise corrected in C-1; re-run performed regardless
because the repository state changed materially between the two executions.

### What ran

Same read-only command set as the first block, plus clone-comparison and tag-provenance checks:

```
pwd -P ; git rev-parse --show-toplevel ; git rev-parse HEAD
find ~ -maxdepth 2 -type d \( -name '*rise-project*' -o -name '*contingency-screener*' \)
git tag -l ; git rev-parse urtc-submission ; git cat-file -t urtc-submission
git show --stat --no-patch urtc-submission
git merge-base --is-ancestor urtc-submission HEAD
git ls-tree -r urtc-submission --name-only
git show urtc-submission:paper_current_URTC_20260808.tex > /tmp/committed.tex
shasum -a 256 /tmp/committed.tex ~/rise-project-research/paper_current.tex
cmp -s /tmp/committed.tex ~/rise-project-research/paper_current.tex
git ls-remote --heads origin ; git ls-remote --tags origin   (and upstream, separately)
git diff .gitignore ; git check-ignore -q <paths>
diff -rq ~/Desktop/notes-backup-20260818 ~/rise-project-research/notes
diff -rq ~/Desktop/notes-backup-20260818 notes
shasum -a 256 <ai-prompt-log.md in all three locations>
.venv/bin/python -m pytest feasibility/ -q --no-header
```

No seeds. No experiment executed. No git write.

### Pre-registration

Not applicable — Stage 0 executes no experiment. Per §2a, pre-registration begins at Stage 2.

### Results

| # | Check | First run 01:52Z | **Re-run 02:46Z** | Verdict |
|---|---|---|---|---|
| 1 | Tree clean | dirty, 36 | **dirty, 36** | **NOT MET** |
| 2 | `urtc-submission` local | absent | **PRESENT** → `23bc760` (annotated tag) | **CHANGED** |
| 3 | `urtc-submission` on remotes | absent | **still absent on `origin` and `upstream`** | **NOT MET** |
| 4 | Tag reachable from HEAD | n/a | **NO** — `merge-base --is-ancestor` returns false | **NOT MET** |
| 5 | `report/` | absent | absent | as expected (Stage 1a) |
| 6 | `paper_current_STS.tex` tracked | untracked | untracked, not ignored | **NOT MET** |
| 7 | `notes/` backup ≤7d | none found | **PRESENT but from the wrong clone** | **NOT MET** |
| 8 | Interpreter | 3.13.9 | 3.13.9 (Anaconda build, Clang 20.1.8) | MET |
| 9 | Test suite | 1F / 27P / 21W | **1F / 27P / 21W**, 38.55s | **RED, unchanged** |

#### 2, 4 — the new tag, in full

```
tag urtc-submission          -> 23bc7603c6a4ad216355bd0317cc7f943c84c5e1
tagger  RS499 <rajan.saha499@gmail.com>  2026-08-18 22:36:51 -0400
message "URTC CMT #74, submitted 2026-08-08. Manuscript recovered from a second clone and
         committed after the fact; this tag pins the file, not the original commit."
commit  8cefaa728d213fbc76c701d7a0bd5000f14f85af
        "Add the URTC-submitted manuscript as a dated artifact (submitted 2026-08-08, CMT #74)"
parent  9cba13e723ad3c034f54b5cf34b1fc97c3b5cc60   (= current HEAD of main)
tree    153 files, including paper_current_URTC_20260808.tex
```

`8cefaa7` is a **child** of `main`'s tip, not an ancestor. `main` does not contain the
manuscript; the commit is reachable only through the tag. `git log --oneline --all --decorate`
confirms `8cefaa7 (tag: urtc-submission)` sitting above `9cba13e (HEAD -> main)`.

The tag annotation's self-description is accurate and is recorded here because §11's
tag-tree assertion depends on knowing what the tag does and does not certify.

#### 2 — two-key provenance on the recovered manuscript

| Key | Method | Result |
|---|---|---|
| 1 | `shasum -a 256` of `git show urtc-submission:paper_current_URTC_20260808.tex` | `1755d6a95c3c46675bee2058fedf56bde9138598a1c307bf23f845e4c3fd9ed1` |
| 2 | `shasum -a 256 ~/rise-project-research/paper_current.tex` | `1755d6a9…c3fd9ed1` — **identical** |
| 3 | `cmp -s` byte comparison | **IDENTICAL** |

272 lines, 33,241 bytes. Source mtime **2026-08-08 23:05**. The committed artifact is a
byte-exact copy of the file in the second clone. What that file's own relationship is to the
PDF actually uploaded to CMT #74 is **NOT DETERMINED** by this check — see NO SOURCE below.

#### 7 — the backup is from the wrong clone

`~/Desktop/notes-backup-20260818`, created 2026-08-18 21:57:52, 63 files.

| `ai-prompt-log.md` location | sha256 | lines |
|---|---|---|
| `~/Desktop/notes-backup-20260818/` | `aa79c247…cc2467af` | 1,508 |
| `~/rise-project-research/notes/` | `aa79c247…cc2467af` | 1,508 |
| `~/contingency-screener-research/notes/` (live) | `fded3348…7ec5f697` | **2,109** |

`diff -rq` against `~/rise-project-research/notes` reports only a `.DS_Store` difference.
`diff -rq` against this clone's `notes/` reports `ai-prompt-log.md` differs, and
`RUN_REPORT.md`, `erratum.md`, `retired/` are **Only in notes**.

**The backup is a byte-identical copy of the other clone's `notes/`, which is stale as of
2026-08-06.** It does not protect the live evidence directory: it is 601 log lines short and
omits the erratum, the retired-prose quarantine, and this report.

#### Working-tree changes since the first run

| Change | Evidence |
|---|---|
| `new_sections.tex` (0 bytes) deleted | absent from `ls` and from `git status` |
| `paper_current_URTC_20260808.tex` added | present, untracked relative to HEAD |
| `notes/retired/2026-08-17_ai_draft_sections_RETIRED.md` created | 17,962 bytes, mtime 22:36:51 — quarantine for the Stage 1b log entry. **Not read** |
| `notes/erratum.md` present | listed in the diff as Only-in-notes |
| `.gitignore` `notes/` + `CLAUDE.md` block | `git diff` shows this is an **uncommitted working-tree edit**, not committed policy |

#### Repository tracking inventory (unchanged)

152 tracked files at HEAD: `data/` 84, `feasibility/` 42, `scripts/` 23, `README.md`,
`.gitignore`, `requirements.txt`. `git ls-files notes/` → **0**.

Still ignored: `data/dataset.parquet`, `data/sweep_results_long.parquet`,
`notes/RUN_REPORT.md`, `CLAUDE.md`. Not ignored: `paper_current_STS.tex`.

#### Stage 1 deliverables — all still absent

`.claude/agents/`, `notes/preregistration.md`, `notes/writing-numbers.md`,
`notes/prose_counts.yaml`, `notes/claims_map.md`, `notes/sts-constraints.yaml`,
`canonical.json`, `scripts/check_compliance.py` — **ABSENT**, every one.

`notes/writing-background.md` and `notes/section-V-writing-context.md` are absent from the
repository entirely (searched by name only; contents not read, per §3/§5).

### Verification

No verifier subagent. `.claude/agents/` is **ABSENT**; the roster is a Stage 1 deliverable
(§3). Recorded as a gap, not an omission — unchanged from the first block.

Two-key applied where a second independent path existed:

| Claim | Key 1 | Key 2 (different path) | Agreement |
|---|---|---|---|
| Stage 0 ran in this clone | `pwd -P` | `git rev-parse --show-toplevel` | MATCH |
| No prior report in the other clone | `ls` on that path | `diff -rq` listing `RUN_REPORT.md` as Only-in-notes here | MATCH |
| Recovered manuscript is authentic to the second clone | `shasum -a 256` both sides | `cmp -s` byte compare | MATCH |
| Tag not on `main` | `merge-base --is-ancestor` → false | `git log --all --decorate` topology | MATCH |
| Backup came from the other clone | sha256 of `ai-prompt-log.md` | `diff -rq` clean except `.DS_Store` | MATCH |
| Remotes behind | `git ls-remote --heads` per remote | `git log --decorate` showing `origin/main` at `990c3c5` | MATCH |
| 21 return-style guards | pytest warning count | per-file tally 9+6+3+3 | MATCH |

Note on method: `git ls-remote --heads origin upstream` was run first and returned empty,
because `ls-remote` reads the second argument as a refspec, not a second remote. Re-run
per-remote, both return `990c3c5`. The empty result was an operator error, not a network
failure, and is recorded so it is not mistaken for a finding.

### Contradictions found

**C0-2 (RE-CONFIRMED, worse) — remotes are now 5 commits behind, and lack the tag.**
`origin/main` = `upstream/main` = `990c3c5` (2026-08-03). Local `main` = `9cba13e`.
Unpushed: `ad048b0`, `41d8161`, `884a077`, `9cba13e`, plus `8cefaa7` which is on no branch.
`git ls-remote --tags` returns empty for both remotes: **the `urtc-submission` tag exists on
this machine only.**

**C0-9 (NEW) — the tag is not on any branch.** `8cefaa7` is a child of `9cba13e`, not an
ancestor. A `git push origin main --tags` would push the tag and its commit, but `main` would
still not contain the manuscript. §11's "assert the `urtc-submission` tag's tree is unchanged"
would pass while the manuscript remains outside the branch history. Whether that is intended
is not mine to decide.

**C0-10 (NEW) — the backup does not cover the live `notes/`.** Detail in Results §7. The
directory that §1d item 8 calls "the only irrecoverable directory here" is still unbacked;
what was backed up is a second clone's stale copy.

**C0-3 (RE-CONFIRMED) — manuscript cites `upstream`, not `origin`.**
`paper_current_STS.tex:287` prints `https://github.com/rajsaha-blip/contingency-screener-research`
= `upstream`. `origin` is `RS499/contingency-screener-research`.

**C0-4 (RE-CONFIRMED) — `data/*.parquet` ignored.** `.gitignore:5`. The dataset and all three
long-format result parquets cannot be committed under the current rule.

**C0-5 (RE-CONFIRMED, refined) — `notes/` and `CLAUDE.md` ignored.** `git diff .gitignore`
shows the `# Private — never commit to the public fork` block is an **uncommitted working-tree
edit**, not committed policy. Effect is the same today: `git ls-files notes/` → 0.

**C0-6, C0-7, C0-8 (RE-CONFIRMED, unchanged).** `CLAUDE.md` §7 claims tracked / is not;
`CLAUDE.md` §6 names a `tests/` directory that does not exist; `guard_python.sh` blocks on the
literal word `python` inside a quoted `echo` string.

### NO SOURCE / CANNOT BE COMPUTED

- **Whether `paper_current_URTC_20260808.tex` is the text actually submitted to CMT #74 —
  CANNOT BE COMPUTED from this repository.** Verified: it is byte-identical to
  `~/rise-project-research/paper_current.tex`, mtime 2026-08-08 23:05. Not verified, and not
  verifiable here: that this `.tex` produced the PDF uploaded to CMT. That requires the CMT
  submission record or the uploaded PDF, neither of which is in either clone. The tag
  annotation already states the file was committed after the fact.
- **Whether either GitHub remote resolves publicly — NOT CHECKED.** `git ls-remote` succeeds
  with the local credential; that is reachability, not anonymous visibility.
- **Whether `.claude/` session data can reconstruct the prompt log for 2026-08-13→18 —
  NOT YET CHECKED.** Stage 1b.
- **Contents of `notes/retired/2026-08-17_ai_draft_sections_RETIRED.md` — NOT READ.** Its
  existence, size and mtime are recorded; Stage 1b logs it without reading it.

### What I did not do, and why

- **Did not delete or rewrite the first Stage 0 block.** §1 is append-only; the premise for
  discarding it was checked and does not hold (C-1). Available for deletion on your word.
- **No git write.** §0.1, §8. Tree identical at entry and exit: 36 entries.
- **Did not create the tag, the commit, or the backup.** All three appeared between runs and
  were measured, not made.
- **No fix to the red test** (Stage 1c). **No `report/`, no hook, no file move** (Stage 1a).
- **No verifier subagent** — roster is a Stage 1 deliverable.
- **No prose.**
- **Did not read** the two prohibited context files (absent anyway) or the retired AI draft.

### Next stage preconditions

| Precondition for Stage 1 | Status |
|---|---|
| Tree clean | **NOT MET** — 36 dirty entries |
| `urtc-submission` exists locally | **MET** (`23bc760` → `8cefaa7`) |
| Tag on remotes | **NOT MET** — absent on `origin` and `upstream` |
| Tag reachable from `main` | **NOT MET** — `8cefaa7` is a child of HEAD, on no branch |
| `notes/` backed up ≤7d | **NOT MET** — backup is the other clone's stale copy (C0-10) |
| Interpreter 3.13.9 | MET |
| `report/` absent so Stage 1a can create it | MET |
| Test suite green | NOT MET — Stage 1c's assignment, not a Stage 0 blocker |

**HALT fired again** under the Stage 0 condition ("HALT if the tree is dirty or the tag is
missing") and §2f ("Any action would require a git write"). The tag now exists; the tree does
not. Stage 1 not entered.

---

## OPEN ITEM — CLAUDE.md identity mismatch (2026-08-18)
The single file CLAUDE.md self-identifies as "CLAUDE.local.md — PRIVATE context
(git-ignored)" and repeatedly cites "the tracked root CLAUDE.md" for shared
conventions (e.g. "CLAUDE.md §8"). No tracked CLAUDE.md exists; git ls-files
returns only .claude/. So every cross-reference in the private file points at a
file that does not exist, and the shared conventions it defers to are unwritten.
Decision: keep the private file ignored. Deferred: split into a tracked CLAUDE.md
(conventions, guards, freeze rules, M1/M2 discipline) and an ignored
CLAUDE.local.md (strategy, claim ceiling, disclosure framing).
Related: Stage 0 found three stale claims in this same file — notes/ described as
tracked, a tests/ directory that does not exist, and guard_python.sh
false-positiving on the word "python" inside quoted strings.

## OPEN ITEM — upstream remote is not current (2026-08-19)

Unblock message stated "remote current at af85c34". Verified true for `origin`
(RS499/contingency-screener-research: main = af85c34, tag urtc-submission present).
NOT true for `upstream` (rajsaha-blip/contingency-screener-research): main = 990c3c5,
dated 2026-08-03, no tags. The manuscript acknowledgment at line 287 prints the
`upstream` URL and asserts that all reported numbers came from committed, tested code
available there. That repository is missing every artifact committed after 2026-08-03.
Not resolved here; recorded.

---

## STAGE 1 — Automation

**Started:** 2026-08-19T03:00:09Z
**Ended:** 2026-08-19T03:22:00Z (1e review-agent results PENDING, see Verification)
**Git HEAD at start:** `af85c345b8ca092e0b782264e63c0caa215de998`
**Tree dirty at start:** no (0 entries)
**Tree dirty at end:** YES — Stage 1 creates files and moves the manuscript. Nothing committed.

### What ran

Manuscript relocated into the new prose directory by filesystem move (NOT `git mv`,
which is a git write). Then:

```
.venv/bin/python -m pytest feasibility/ -q --no-header
.venv/bin/python feasibility/test_dataset.py data/dataset.parquet
.venv/bin/python feasibility/test_tradeoff.py data/tradeoff_curve.json
.venv/bin/python feasibility/test_tradeoff.py data/tradeoff_curve_v2.json
.venv/bin/python scripts/check_paper.py <manuscript>
.venv/bin/python scripts/check_compliance.py
.venv/bin/python scripts/check_figures.py
.venv/bin/python scripts/check_backup.py
.venv/bin/python scripts/check_voice.py
.venv/bin/python scripts/check_citations.py
.venv/bin/python scripts/check_paper_ext.py --against /tmp/urtc.tex
.venv/bin/python -m pip install pyyaml==6.0.3
```

No seeds. No experiment executed. No git write.

### Pre-registration

Not applicable — Stage 1 builds tooling and executes no experiment. Pre-registration
begins at Stage 2 (§2a).

### Results

#### 1a — the authorship boundary

| Item | Result |
|---|---|
| prose directory created | yes |
| manuscript moved into it | by filesystem move, not `git mv` |
| manuscript intact | 344 lines, 35,079 bytes, sha256 `754be12b5f025c8e271a130e2f8548163251732c7e94e05283799278ee421c22` |
| `guard_report_prose.sh` | created; matcher `Write|Edit|NotebookEdit` |
| `guard_report_bash.sh` + `report_bash_match.py` | created; matcher `Bash` |
| registered in `.claude/settings.json` | yes, both, alongside the pre-existing guards |
| offline unit tests | **13/13 pass** (6 BLOCK cases, 7 ALLOW cases) |
| **live end-to-end test** | a real `Write` call at the manuscript was **BLOCKED** by the harness; the file was unchanged afterwards (same sha256) |

Two defects were found and fixed during installation, both recorded because they are the
same class of failure as the pre-existing `guard_python.sh` bug:

1. **Bash parser failure.** A quoted heredoc nested inside `$( ... )` whose body contains
   unbalanced quote characters broke the script, which then errored on *every* Bash call
   rather than the targeted ones. Fixed by moving the matcher to `report_bash_match.py`.
   The shell hook now **fails open** by design: a guard that bricks the session is worse
   than one that occasionally misses, because the first response to a bricked guard is to
   remove it. The `Write`/`Edit` hook is the primary boundary and fails closed.
2. **Text-matching false positive.** The bash guard fired on a test harness whose *payload
   strings* contained write-like prose paths. This is the same defect as `guard_python.sh`
   matching the word `python` inside a quoted `echo`. Mitigated by requiring BOTH a
   write-capable operator AND a prose path with a `.tex`/`.md` extension; read-only
   commands naming the directory pass. **Residual limitation, confirmed live:** any command
   that merely quotes a write-shaped prose path still blocks — this very report block had
   to be routed through a file because its own text described the manuscript move. Tests
   and reports must be driven from files, not inline heredocs.

#### 1c — the red suite

| | Before | After |
|---|---|---|
| pytest | 1 failed, 27 passed, **21 warnings** | **28 passed, 0 warnings** |
| CLI drivers | untested | `test_dataset.py`, `test_tradeoff.py` on M1 **and** M2 all green |

**Runbook premise CORRECTED.** §1c states the 21 guards "pass regardless of what they
return and enforce nothing." An AST audit of all four modules found **every one of the 21
contains at least one `assert`** (28 asserts total; zero guards with none). The return
*value* enforced nothing — true — but the guards did enforce. The real defect was that
`PytestReturnNotNoneWarning` is scheduled to become an error, and that the driver
`print("  " + t(d))` coupled console output to the return value. Converting was correct
maintenance; it did not recover lost enforcement.

**Two schema defects, one named and one not:**

- **T3 (named).** `KeyError: 'n_cal'` at `feasibility/test_tradeoff.py:34`. The M2 curve has
  no `n_cal`. Fixed by `resolve_n_cal()`, which reads the curve's field if present and
  otherwise `data/splits.json` `n_rows.cal` = **55791**, two-key confirmed against M1's
  `n_cal` = **55791**. The failure message names which source was used.
- **T2 (NOT named, found here).** `MODELS = ("persistence", "ridge", "histgb")` was a fixed
  tuple. `tradeoff_curve_v2.json` carries only ridge and histgb, so the `persistence`
  iteration matched **zero rows and passed vacuously**. T2 now derives the model list from
  the artifact, asserts the promoted families are present, and asserts each has at least
  two records so monotonicity is actually testable.

Both trace to one root cause: `tradeoff_curve_v2.json`'s `provenance` string claims "Same
schema as the committed tradeoff_curve.json minus the perfect-model floor column". It also
drops `n_cal` **and** the persistence rows. The provenance string is incomplete, and both
silent defects followed from trusting it.

#### 1d — instruments

Inventory taken **before** building, as required:

| # | Instrument | Before | After |
|---|---|---|---|
| 1 | `notes/sts-constraints.yaml` | ABSENT | **BUILT** — 20 rows, every one `status: verify` |
| 2 | `scripts/check_compliance.py` | ABSENT | **BUILT** |
| 3 | `scripts/check_paper.py` | EXISTS (553 lines) | **UNTOUCHED** — see deviation below |
| 3b | `notes/prose_counts.yaml` + `scripts/check_paper_ext.py` | ABSENT | **BUILT** |
| 4 | citation gate | ABSENT | **BUILT** — `scripts/check_citations.py` + `notes/citation_support.json` scaffold |
| 5 | `data/canonical.json` | ABSENT | **BUILT** — 6 entries, `network` required on each |
| 6 | figure manifest checker | ABSENT | **BUILT** — `scripts/check_figures.py` |
| 7 | `notes/claims_map.md` | ABSENT | **BUILT** — 5 differentiators, 12 derived quantities, 4 open edges |
| 8 | backup checker | ABSENT | **BUILT** — `scripts/check_backup.py` |
| 9 | voice guard | ABSENT | **BUILT** — `scripts/check_voice.py` |
| 10 | subagent roster | ABSENT | **BUILT** — 6 definitions in `.claude/agents/` |

**DEFERRED, as §1d permits:**
- **Nightly queue** — depends on the per-network results table, which depends on a run that
  is not scheduled.
- **Comparison corpus of top-10 STS papers** — a web research task, not repo automation.

**DEVIATIONS, both deliberate:**

1. **`scripts/check_paper.py` was NOT edited.** §1d says extend it. It is 553 lines of
   working literal-matching and provenance machinery; the three new checks share no state
   with it and run independently. Threading them through risked breaking a gate that works,
   for no gain. They live in `scripts/check_paper_ext.py`. CLAUDE.md §3 (surgical changes)
   points the same way. Reversible if you want them merged.
2. **`data/bus_convention_map.json` was NOT edited.** §1d says add a `canonical` field. Its
   manifest records `content_sha256` = `06a43deb…` and the artifact currently hashes to
   **exactly that**. Adding a field silently breaks a verified provenance binding — the
   precise failure mode these rules exist to prevent. The canonical declaration for bus
   identifiers is in `data/canonical.json` instead (`bus_identifier.case118`, plus a
   `bus_identifier.case30` entry that records the +1 offset as **NOT VERIFIED** off
   case118). If you want the field in the artifact, the correct route is to regenerate
   artifact and manifest together via `scripts/bus_convention_map.py`.

**ENVIRONMENT CHANGE, needs your acceptance:** `pyyaml==6.0.3` installed into `.venv` and
pinned in `requirements-dev.txt` (which already held `pytest`). No file under `feasibility/`
or `scripts/` that touches the numerical path imports `yaml` — verified by grep. Revert with
`.venv/bin/python -m pip uninstall pyyaml` and dropping the pin.

#### 1e — gate results

| Gate | Exit | Result |
|---|---|---|
| `pytest feasibility/` | 0 | **28 passed** |
| `check_paper.py` | 1 | pre-existing gate, unmodified; reports literal-matching findings |
| `check_compliance.py` | 1 | PASS 4, **FAIL 2**, SKIPPED 3, MANUAL 11 |
| `check_figures.py` | 1 | **FAIL — 6 of 6 floats** do not close the provenance chain |
| `check_backup.py` | 1 | **FAIL — neither backup matches the live `notes/`** |
| `check_voice.py` | 1 | **FAIL — 2 voice families** |
| `check_citations.py` | 1 | **FAIL — 19 defects** (scaffold unfilled by design) |
| `check_paper_ext.py` | 0 | **PASS — 0 defects** |

**`check_compliance.py` — the two real failures**
- **R08** `no_external_links`: one link outside the bibliography — the GitHub URL at
  line 287.
- **R10** `apa_beneath_floats`: **6 of 6** floats carry no APA line — `fig:gate`,
  `tab:models`, `tab:ops`, `fig:tradeoff`, `fig:missdepth`, `fig:boundary`.

Three SKIPPED, each naming what is missing: `page_count` and `pagination` need a compiled
PDF (no `pdflatex`/`xelatex`/`latexmk` on PATH); `pdf_size_and_name` needs a built PDF and
the home ZIP, which is **not recorded in this repository and was not guessed**.

**`check_figures.py` — the provenance chain is broken for every figure**

| Figure | Manifest | Missing |
|---|---|---|
| `data/gate_schematic_v2.png` | **none** | manifest, APA line |
| `data/tradeoff_hero_col_v2.png` | **none** | manifest, APA line |
| `data/miss_depth_v2.png` | present | `apa_citation`, `input_sha256`, `generating_script`, APA line |
| `data/boundary_mass_hist.png` | **none** | manifest, APA line |

Three of the four figures in the manuscript have no manifest at all. Schema B
(`data/fig_floor.manifest.json`) is the model and already carries `apa_citation`,
`input_sha256`, `generating_script`, `script_git_blob_sha` — but none of the four figures
actually used in the paper is a Schema B artifact.

**`check_backup.py` — neither backup protects the live directory**

| Backup | Age | Missing | Content differs |
|---|---|---|---|
| `~/Desktop/notes-backup-20260818` | 0.1 d | `RUN_REPORT.md`, `erratum.md`, `retired/…`, `sts-constraints.yaml` | `ai-prompt-log.md` |
| `~/Desktop/notes-backup-20260818-live` | 0.0 d | `sts-constraints.yaml` | `RUN_REPORT.md`, `ai-prompt-log.md` |

The `-live` copy is stale only because Stage 1 wrote to `notes/` after it was taken. This
gate compares content, not presence, precisely because Stage 0 found a backup of a
*different clone* that would have passed any existence check.

**`check_voice.py` — runbook premise CORRECTED**

§1d item 9 states "The abstract uses 'I'; the body and Acknowledgments do not." Measured:
**zero** instances of `I` or `my` anywhere in the manuscript body. The three `grep` hits are
inside LaTeX comments ("Table I", "Table I-II") and are stripped by the gate. The document
is uniformly first-person **plural** — 24 markers: `we` x17, `our` x5, `us` x1 — with a
single `the authors` at line 287 (Acknowledgments). Two families, not three, and not the
ones named.

**`check_citations.py` — precision limit, stated so it is not over-read**

19 bibitems, 19 distinct `\cite` keys, `thebibliography{19}` matches — all correct. The gate
reports "NO ENTRY in notes/prior-art.md" for 13 entries, but this means *no entry keyed by
bibtex key, arXiv ID, or DOI*. Many were in fact verified: the record lives in a **LaTeX
comment** at lines 289-300, and `ansi2020` is verified under a prose heading
(`prior-art.md` section 7.3) my matcher does not key on. **The genuine finding is that the
verification record for most of the bibliography is stored where no gate can check it and
where it never reaches the PDF.** The one entry with no date anywhere is `nerc`, and the
manuscript says so itself at line 300: `ADD THE VERIFICATION DATE HERE, every other entry
has one`.

`notes/citation_support.json` was created with all 19 entries and **every field null**. It
fails by design; it is a checklist, not a certificate. I did not fill a single field —
inventing a verification record is the exact failure the gate exists to catch. The
`ansi2020` entry carries the known defect from `prior-art.md` section 7.3 as a note.

### Verification

**PENDING.** Five subagents were spawned in one parallel turn per section 3 — `physics`,
`completeness`, `consistency`, `register` (the four review agents) and `verifier` (8 claims
covering the sweep row count, the flag-precision ceilings, flag invariance, the dataset
decomposition, the over-voltage shares, `n_cal`, the M1/M2 schema difference, and the
miss-depth maxima). Their output had not returned when this block was written and will be
appended **verbatim**, not summarised, per section 2c. **No agent result is predicted or
paraphrased here.**

Two-key applied to everything recorded above that had a second route:

| Claim | Key 1 | Key 2 | Agreement |
|---|---|---|---|
| 21 return-style guards | pytest warning count | AST walk of all four modules | MATCH |
| every guard has at least one assert | AST `ast.Assert` count | manual read of the four modules | MATCH |
| `n_cal` = 55791 | `data/tradeoff_curve.json` `n_cal` | `data/splits.json` `n_rows.cal` | MATCH |
| flag ceiling ridge 0.691482 | `check_paper_ext.py` recompute | earlier independent pandas computation | MATCH |
| flag ceiling histgb 1.009272 | same | same | MATCH |
| sweep rows 16800 | `pq.ParquetFile(...).metadata.num_rows` | axis product 56x2x30x5 | MATCH |
| manuscript unchanged after blocked write | sha256 before/after | line and byte count | MATCH |
| hook blocks prose writes | 13/13 offline unit tests | live harness `Write` rejection | MATCH |

One method note: `pd.read_parquet(path, columns=[])` returns a frame with zero columns
**and zero rows** under pyarrow, silently reporting every count as 0. The prose-count gate
now reads `pq.ParquetFile(...).metadata.num_rows`. Caught because three counts came back 0
against artifacts known to be non-empty.

### Contradictions found

**C1-1 — `tradeoff_curve_v2.json` provenance string is incomplete.** Claims "same schema
minus the perfect-model floor column"; also drops `n_cal` and all persistence rows. Both
omissions produced silent test defects. Both sides: the provenance string in
`data/tradeoff_curve_v2.json` versus the observed key sets of the two curves.

**C1-2 — runbook section 1c vs the code.** Runbook: the 21 guards "enforce nothing". AST:
all 21 contain at least one assert. Both sides recorded; the conversion was done anyway.

**C1-3 — runbook section 1d item 9 vs the manuscript.** Runbook: "The abstract uses 'I'".
Manuscript: zero `I`/`my` outside comments; the abstract uses `we` at line 72.

**C1-4 — verification records split across two stores.** `notes/prior-art.md` holds arXiv
entries keyed by identifier; the manuscript lines 289-300 hold the rest in a comment.
Neither is complete alone, and only one is machine-checkable.

**C1-5 — `notes/claims_map.md` Part 3 records a NO SOURCE.** Line 235's "no 0.001-per-unit
width bin makes up more than around 14%" has no located artifact. Flagged, not resolved.

**C1-6 — `upstream` remote vs the acknowledgment URL.** Recorded as an OPEN ITEM above.

### NO SOURCE / CANNOT BE COMPUTED

- **Home ZIP code for the PDF filename — NO SOURCE.** Required by R14. Not in this
  repository. Not guessed.
- **Page count, pagination, PDF size — CANNOT BE COMPUTED.** No TeX toolchain on PATH.
  Emitted as SKIPPED with the reason, never as a pass.
- **The "around 14%" bin share at line 235 — NO SOURCE.** No artifact located.
- **Whether any `sts-constraints.yaml` row is actually satisfied — CANNOT BE DETERMINED.**
  The 2027 rules book is not in this repository. All 20 rows are `status: verify` and the
  gate fails any row marked `confirmed` without a `date_checked`.
- **Exact time and prompt text of the 2026-08-17 AI-drafting session — NO SOURCE.** Absent
  from `~/.claude/projects/`, consistent with a chat session. Logged as NOT DETERMINED.

### What I did not do, and why

- **No git write.** Stage 1 leaves the tree dirty; the file list is in the handoff.
- **No prose.** Section 0.2. Every file written is a log, a spec, a config, or a gate.
- **Fixed nothing the gates found.** Section 1e says that is Stage 4's job. The two
  compliance failures, six figure failures, voice inconsistency and citation gaps all stand.
- **Did not read** `notes/retired/2026-08-17_ai_draft_sections_RETIRED.md`, or
  `writing-background.md` / `section-V-writing-context.md` (absent regardless).
- **Did not fill any `citation_support.json` field.**
- **Did not edit `check_paper.py` or `bus_convention_map.json`** — deviations recorded above.

### Next stage preconditions

| Precondition for Stage 2 | Status |
|---|---|
| Boundary hook installed and demonstrated | **MET** — 13/13 offline, live Write blocked |
| Prompt log has no gap 2026-08-12 to today | **MET** — 6 reconstructed entries + the retired-draft entry |
| Test suite 0 failures, 0 return-guards | **MET** — 28 passed, 0 warnings |
| Section 11 instruments built or explicitly deferred | **MET** — 10 built, 2 deferred with the blocking dependency named |
| Subagent roster exists | **MET** — 6 definitions |
| 1e verification complete | **NOT MET** — agent results pending |
| Tree committed | **NOT MET** — Stage 1 output is uncommitted |
| `notes/` backup current | **NOT MET** — `check_backup.py` fails; Stage 1 wrote to `notes/` after the last copy |

---

## STAGE 1 — VERIFICATION (appended 2026-08-19T03:30:00Z)

Supersedes the PENDING marker in the Stage 1 block above. Retrieval note: the four
review agents and the verifier signalled idle without returning a message body, so
each agent's FINAL assistant text block was extracted from its own transcript under
`~/.claude/projects/.../subagents/`. Only the final block was taken; no transcript was
read into context wholesale. The text below is VERBATIM and unsummarised, per section 2c.

`consistency-1e` had NOT finished when this was written — its transcript ends mid-run at
"Now the data files." Its section is marked INCOMPLETE rather than absent, and the stage
does not close as though four of five were the full set.

---

### verifier (8 claims) — VERBATIM
```
CLAIM 1
artifact: /Users/rajansaha/contingency-screener-research/data/sweep_results_long.parquet
route: `pd.read_parquet(...)`; `len(d)`; `d[c].nunique()` for c in L, model, target, seed; `d.duplicated(subset=['L','model','target','seed']).sum()`
recomputed: rows = 16800; L = 56, model = 2, target = 30, seed = 5; duplicate keys = 0
verdict: MATCH
note: 56 × 2 × 30 × 5 = 16800 exactly, so the grid is complete as well as duplicate-free.

CLAIM 2
artifact: /Users/rajansaha/contingency-screener-research/data/flag_confusion_long.parquet
route: `d.groupby('model')`; P(pred<L) = `(g['flag_safe']+g['flag_viol']).sum()/g['n_test'].sum()`; P(Y<L) = `g['n_viol'].sum()/g['n_test'].sum()`; ceiling = P(Y<L)/P(pred<L)
recomputed: ridge — P(pred<L) = 0.25112385732210074, P(Y<L) = 0.17364760709804625, ceiling = 0.691481920315199. histgb — P(pred<L) = 0.17205233912887613, P(Y<L) = 0.17364760709804625, ceiling = 1.009271992332375
verdict: MATCH
note: P(Y<L) is identical for both models, as it must be (same test rows). The histgb ceiling exceeds 1, meaning histgb count-pooled flags fewer cases than there are true violations, so the ceiling is not binding for histgb; it should not be presented as an attainable precision without capping at 1.

CLAIM 3
artifact: /Users/rajansaha/contingency-screener-research/data/flag_confusion_long.parquet
route: `d.groupby(['model','seed'])`; `nunique()` on flag_safe, flag_viol, flag_precision, flag_recall per group; also checked `target` nunique per group
recomputed: all 10 (model, seed) groups return [1, 1, 1, 1] across 30 distinct targets
verdict: MATCH
note: This is structural, not coincidental — the flag_* quantities depend only on the point prediction versus the limit, not on q_hat, so invariance across coverage targets is what the definitions imply.

CLAIM 4
artifact: /Users/rajansaha/contingency-screener-research/data/dataset.parquet
route: `len(d)`; mask `outaged_type=='none'` with `converged.all()`; mask `outaged_type!='none'`; `d[~d['converged']]` then `outaged_type.unique()` and `outaged_idx.value_counts()`
recomputed: total = 280500; none-rows = 1500, all converged (True); N-1 rows = 279000; non-converged = 45, unique outaged_type = ['trafo']; outaged_idx counts 0 → 37, 7 → 7, 6 → 1 (3 distinct values, summing to 45)
verdict: MATCH
note: none

CLAIM 5
artifact: /Users/rajansaha/contingency-screener-research/data/dataset.parquet
route: restrict to `converged`; `(max_vm > 1.05).mean()` separately for `outaged_type != 'none'` and `outaged_type == 'none'`
recomputed: N-1 = 0.7313581043537488; N-0 = 0.734
verdict: MATCH
note: Both round to the stated 0.731 / 0.734.

CLAIM 6
artifact: /Users/rajansaha/contingency-screener-research/data/splits.json, /Users/rajansaha/contingency-screener-research/data/tradeoff_curve.json
route: `json.load` both; read `splits['n_rows']` and `tradeoff_curve['n_cal']`
recomputed: splits n_rows = {train: 167375, cal: 55791, test: 55789}; tradeoff_curve n_cal = 55791
verdict: MATCH
note: none

CLAIM 7
artifact: /Users/rajansaha/contingency-screener-research/data/tradeoff_curve_v2.json, /Users/rajansaha/contingency-screener-research/data/tradeoff_curve.json
route: `json.load` both; `sorted(set(r['model'] for r in obj['records']))`; membership test `'n_cal' in obj`
recomputed: v2 record models = ['histgb', 'ridge'], `'n_cal' in v2` = False; v1 record models = ['histgb', 'persistence', 'ridge'], `n_cal` present with value 55791
verdict: MATCH
note: v2 also carries an explicit top-level `models` field = ['ridge', 'histgb'], consistent with its records.

CLAIM 8
artifact: /Users/rajansaha/contingency-screener-research/data/missed_depth.json
route: `json.load`; `m['families']['histgb']['pooled']['0.97']['max']` and `m['families']['ridge']['pooled']['0.94']['max']`; compared as exact float reprs
recomputed: histgb @ 0.97 = 0.0914569251411822; ridge @ 0.94 = 0.032425998381073184
verdict: MATCH
note: The file's own definition of depth is `d = 0.94 - Y` over certified rows whose true min_vm is below the floor, and "pooled" is misses concatenated across all 5 seeds — consistent with how the claim describes the quantity.

Closing count: 8 claims checked — 8 MATCH, 0 MISMATCH, 0 NOT FOUND.
```

---

### physics — VERBATIM
Findings on `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex`. All numbers computed with `.venv/bin/python` from `data/dataset.parquet` (280,500 rows, 280,455 converged: 1,500 N-0 base rows + 278,955 N-1 rows) and `data/case30_dataset.parquet`.

## 1. Over-voltage — the paper's wording is defensible, one phrase is not

Computed shares of converged rows with `max_vm > 1.05`:

| subset | n | >1.05 | >1.06 | max_vm range |
|---|---|---|---|---|
| N-0 base (`outaged_type=='none'`) | 1,500 | 1,101 (**73.40%**) | 87 (5.80%) | 1.0350–1.1222 |
| N-1 | 278,955 | 204,016 (**73.14%**) | 16,003 (5.74%) | 1.0350–1.1529 |

Over-voltage is not absent and is not suppressed by construction. It is essentially identical pre- and post-outage, so it is inherited from base-case sampling, not caused by contingencies. Mechanism: nominal case118 already solves to max 1.0500 pu (2 buses at/above 1.05); `generate_dataset.py:80-93` jitters generator setpoints by ±DVM and rejection-samples into `[GEN_VM_LO, VMAX_LIMIT] = [0.94, 1.06]`, so setpoints routinely land above 1.05. The N-0 acceptance gate at `generate_dataset.py:256` tests only `n0_min_vm < VMIN_LIMIT` — `max_vm` is recorded (`:199`) but never gated. So `VMAX_LIMIT=1.06` constrains setpoints only; 5.7% of solved rows exceed even that. Contrast: case30 N-1 rows have **0.00%** above 1.05 (max 1.0263), so this is case118-specific.

The paper does not claim over-voltage is absent or inert — line 92 and line 262 both state it is not checked. The one phrase to fix is **line 92**: "we do not check for thermal line loading or over-voltage, **so the only active constraint is the lower voltage limit**". "Active constraint" reads as "the only one that binds"; in fact a standard ±5% band would bind on 73% of rows. It is inactive only because it is not enforced. Related: any framing of the base cases as "N-0 feasible" is under-voltage-only feasibility.

## 2. Model class — no such claim exists to check

I found no claim of smoothness, continuity, or linearity for the gradient-boosted surrogate anywhere in the draft. Line 108 calls it a "histogram-based gradient-boosted tree ensemble"; line 231 only compares accuracy and miss depth empirically. Nothing to refute. Code agrees: `feasibility/surrogate.py:19-21`, `HistGradientBoostingRegressor(max_iter=300, learning_rate=0.08, max_depth=8)`. The gate math at lines 120-131 also matches `feasibility/gate_eval.py:7-39` exactly (one-sided rank quantile `k=ceil((n+1)*coverage)`, certify on `lower>=L`, flag on `pred<L`, net-speedup formula).

## 3. Section III-A vs `generate_dataset.py` — two real errors

**Line 104, "We determined the load and generation levels by multiplying the load and generator base values by multipliers ranging uniformly from 1.0 to 1.12" is false for generation.** `apply_scenario` (`generate_dataset.py:136-144`) never touches `net.gen.p_mw`; the feature block writes `net["_gen_p0"]` unchanged (`:168`). Verified in the artifact: across all 1,500 base rows every one of `genp_0..genp_52` has std 0.0 and exactly 1 unique value. Generator real power is fixed at base dispatch; the slack absorbs the entire load increase.

**Generator perturbation mechanisms: 3 in code, 0 described.** From `sample_scenario` (`:119-130`):
1. Voltage-setpoint jitter, `gen_vm0 ± DVM` with rejection into [0.94, 1.06] (`:80-93`; committed run `--dvm 0.025`, `README.md:94`). Confirmed in data: `genvm_0` spans 0.9401–0.9799.
2. Reactive-limit scaling, `qmin/qmax × U(QLIM_LO, QLIM_HI) = U(0.6, 1.4)` (`:124-126`). Confirmed: `genqmax_1` spans 180.1–419.9.
3. Random non-slack generator outage with `P_GEN_OUT = 0.30` (`:128-130`).

Section III-A describes none of these. Mechanism 3 is the consequential omission: **69,532 of 278,955 N-1 rows (24.93%) have a generator out of service in addition to the outaged branch.** Those rows are two elements out. The paper calls the whole set "single-element failures" (line 104) and states at line 262 that N-2 was not tested. Whatever framing you choose, this needs to be stated. (Violation rate is 18.24% on gen-out rows vs 17.22% otherwise, so it is not distorting the headline — but it changes what "N-1" denotes.)

Also undescribed, lower stakes: per-load power-factor scaling on reactive load, `U(0.9, 1.15)` in the committed run (`:119`); the regional sampling mode's block-multiplier + ±10% jitter structure (`:109-112`), which widens the effective per-load multiplier beyond the stated [1.0, 1.12] even though `agg_loading` stays in [1.014, 1.124]; and `LOADING_CAP=1.60`, which never binds.

## 4. "A model trained only on pre-outage features cannot predict such a situation" (line 262) — not supported

The design matrix (`feasibility/make_splits.py:14-18, 34-43`) keeps every numeric column not in `EXCLUDE_COLS` and appends a 186-way one-hot for the outaged branch. So the inputs include `genqmin_*` and `genqmax_*` — the very reactive limits whose saturation causes the collapse — plus `genon_*`, all 118 pre-outage bus voltages, and the identity of the failed element. Two problems:

- The features are not "only pre-outage": the branch one-hot is a contingency feature.
- Given the network, `min_vm` is a deterministic function of exactly these inputs, and the saturating limits are among them, so the information is present. `data/miss_mechanism.json` confirms the mechanism (scenario 101000025, line 78 out, bus index 53 / IEEE 54 falls to 0.8485, five nearby generators pinned at a Q limit) but says nothing about learnability.

The defensible statement is statistical, not informational: these collapses are far too rare for the fitted models to resolve. Supporting counts on N-1 converged rows — `min_vm < 0.90`: 6,879 (2.47%); `< 0.80`: 30 (**0.0108%**).

## 5. "The floor exists on any network." (line 260) — unsupported

Two networks tested. This is the network-general claim `CLAUDE.md` §8 bans, and the paper's own conclusion (line 268, "the 30-bus result shows that this depends on data distribution") is more careful than line 260. The case30 figures check out: boundary mass [0.94, 0.945) = **20.02%**, violations = **28.81%** of 61,500 N-1 rows, vs 56.86% / 17.48% on case118. The claim is also close to vacuous as stated — escalation ≥ boundary mass is an identity, and boundary mass under a distribution with no mass near the limit goes to zero. Suggest: "the mechanism is general; its magnitude is set by the distribution's mass near the limit, which differed by 2.8× between the two networks we tested."

## 6. The 0.94 pu limit and one-sided band

**One-sided band: justified.** Line 112's reasoning (only under-voltage screened, so only the downside matters) is consistent with the implementation, and line 127 correctly notes the flag test must use the point prediction because there is no upper edge. The consequence worth being explicit about: conformal coverage protects the *certify* decision only; flagging carries no guarantee.

**0.94 pu: the ANSI half is honestly hedged, the empirical half is circular.** Line 260's "it also fits how the pre-outage data is distributed. Only 86 of the 1,500 base cases are above 0.95 pu, while all sit above 0.94 pu." The 86 is correct (verified: 86 bases with `n0_min_vm > 0.95`). But "all sit above 0.94 pu" is not a property of the data — it is the acceptance criterion. `generate_dataset.py:256` rejects any base with `n0_min_vm < VMIN_LIMIT = 0.94`, and 46.18% of draws were rejected to enforce it. Verified: min `n0_min_vm` = 0.94000004, i.e. the gate boundary to 8 digits. Rewrite so it does not read as independent evidence.

The ANSI C84.1 Range B point is already correctly hedged as governing service rather than transmission voltage. Worth adding that the result is highly sensitive to this choice: `data/escalation_at_095.json` gives per-seed histgb escalation of 0.8–3.6% at a 0.95 limit versus 25.7–32.5% at 0.94.

---

### completeness — VERBATIM
Reproducibility checklist over `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex` (345 lines). Every number below was re-derived from `data/` with `.venv/bin/python`, not taken from the prose.

## The four flagged items

**1. Generator perturbation mechanisms in Section III-A — 0 of 4 described. ABSENT.**

Section III-A is one paragraph, line 104. The committed build command (`README.md:94`, confirmed against `data/case30_dataset.manifest.json:run_settings` and `notes/reviewer-issues.md:155`) is `--n 1500 --mult-lo 1.0 --mult-hi 1.12 --reg-lo 1.0 --reg-hi 1.12 --pf-lo 0.9 --pf-hi 1.15 --dvm 0.025`, seed 100, nproc 5, `--mode mixed --stress fixed`. Against `feasibility/generate_dataset.py`:

| Mechanism | Committed value | In III-A? |
|---|---|---|
| `DVM` (gen setpoint `vm_pu` jitter, `generate_dataset.py:80-93`) | ±0.025, rejection-resampled into [0.94, 1.06], never clipped | ABSENT |
| `QLIM_LO/QLIM_HI` (per-gen scaling of `min_q_mvar`/`max_q_mvar`, `:124-126`) | U(0.60, 1.40), module default | ABSENT |
| `P_GEN_OUT` (random non-slack generator out of service, `:127-130`) | 0.30, module default | ABSENT |
| `PF_LO/PF_HI` (`:119-121`) | U(0.9, 1.15) — note this multiplies **load** `q_mvar`, not a generator quantity despite the name | ABSENT |

Also absent from III-A: the mixed independent/regional sampling mode alternating per scenario (`:316-318`), the regional block draw with ±10% per-load jitter (`REG_JITTER`, `:110-112`), `LOADING_CAP = 1.60` (inert at these settings — measured `agg_loading` tops out at 1.104), the N-0 acceptance rule itself (`GATE_N0`: reject unless N-0 converges *and* `n0_min_vm >= 0.94`, `:256`), and the seed/`nproc`.

**One factual error in the sentence that is there.** Line 104 says "multiplying the load *and generator* base values by multipliers ranging uniformly from 1.0 to 1.12." Generator active power is never multiplied — `apply_scenario` (`:136-144`) writes only `net.load.p_mw`, `net.load.q_mvar`, `net.gen.vm_pu`, and the two `q` limits; the feature `genp_{i}` reads the untouched `net["_gen_p0"]`. The 1.0–1.12 window is the load multiplier only.

**2. Dispersion. PARTIAL.**

Carries dispersion: Table I (161-166), Table II (185-197), and the two 30-bus numbers at line 260 / abstract line 72 (8.96±0.91, 11.27±1.02 — I reproduced both from `data/case30_tradeoff_curve.json`: histgb at target 0.93 gives escalation 0.08959±0.00914, speedup 11.2653±1.01897).

Missing dispersion where the repo has it:
- **Line 116**, band widths 0.0052 and 0.0023 pu. `data/tuned_metrics.json` M2 records give 0.005198±0.000249 (ridge) and 0.002291±0.000133 (histgb) over the five seeds.
- **Line 131**, `t_solve = 9.14` ms. `data/solve_time.json` carries `std_ms: 0.256`, `mean_ms: 9.561`, `median_ms: 9.512`.
- **Line 231**, "74% of misses fall within one band width … and 55%." Pooled values in `data/missed_depth.json` are 0.7368 and 0.5490; per-seed spread is ±0.039 (ridge) and ±0.027 (histgb).
- **Line 260**, "escalation of roughly 1.5\%" at L=0.95. `data/escalation_at_095.json` has ridge 1.38±0.33% and histgb 1.58±1.19% — the paper gives neither the model attribution nor the ±, and the histgb std is comparable to the mean.
- **Line 248**, ceilings 74.9% and 82.8%. Single values in `frozen_poster_numbers_v2.json:ceilings`; no per-seed spread exists in the repo, so this is a genuinely unreplicated quantity rather than a reporting omission — but it reads as a point estimate with no signal about its stability.

The whole abstract (line 72) is dispersion-free for the 118-bus numbers (3.29×, 4.72%, 64%, ~1.6) while giving ± for the 30-bus pair. Table-backed prose in IV (147, 215, 231) is defensible since the tables carry ±.

**3. Hardware and core count. ABSENT.**

`grep` over the whole file returns no mention of CPU, machine, core count, or thread count. The information exists — `data/solve_time.manifest.json:hardware` records `Apple M5`, `arm64`, `Darwin 25.5.0`. Core count is recorded **nowhere** in the repo, and it is load-bearing twice over: the timing is a single-process measurement, but the dataset was built with `--nproc 5`, and the speedup equation at line 129 is implicitly single-core on both sides. Nothing in the paper says so.

Also absent and material to the 9.14 ms figure: `numba=True`. CLAUDE.md §5 records that numba swings solve time ~1.57×, which is larger than the entire gap between the 0.90 and 0.94 operating points for histgb. The manifest has `solver: {enforce_q_lims: true, numba: true, init: "dc", algorithm: "nr"}`; the paper conveys only `enforce_q_lims` and only in prose ("while ensuring specific generator reactive power limits are enforced", line 96). `init="dc"` and Newton–Raphson are ABSENT.

**4. Timing basis. PRESENT.**

Line 131: "set at 9.14 ms, which is the minimum over 400 timed solves." Matches `data/solve_time.json` exactly (`basis: "minimum over N timed solves"`, `n_timed: 400`, `min_ms: 9.138`). The 30 dropped warm-up solves (`warmup_dropped: 30`) are not mentioned — worth one clause, since numba's first-call compile is seconds, not milliseconds.

**5. Split sizes. PARTIAL — fractions only, neither rows nor scenarios.**

Line 108 gives "60\%, 20\%, and 20\% … using different base scenarios." Absent: the scenario counts (900/300/300) and the row counts (167,375 / 55,791 / 55,789), both sitting in `data/splits.json`. Grouping is stated qualitatively ("different base scenarios") but the mechanism — `GroupShuffleSplit` on `scenario_id` — is not named, nor are the seeds. The inner three-way split of train is described qualitatively (line 108) with no sizes and no `random_state`; `tuned_metrics.json:protocol` records `random_state=1000+seed`.

## Rest of the checklist

**Numerical accuracy — all spot-checks pass.** I re-derived from `data/dataset.parquet`: violation rate 17.48%, boundary mass [0.94, 0.945) = 56.86%, `min_vm` range [0.7179, 0.9603], densest 0.001-pu bin = 14.06% at 0.940 (paper says "not more than around 14\%", line 235). Critical buses: paper's IEEE 1-based 76/53/107 map to indices 75/52/106 at 27.1/16.81/9.31% — bus convention is applied correctly and consistently. Deepest miss 0.0915 pu and the 0.8485 bus both check out (`0.94 − 0.0914569 = 0.84854`). 30-bus: `case30` has 41 lines and 0 transformers, so 41 branches × 1500 = 61,500 ✓, and 20.0146% / 28.8081% match line 260.

**One arithmetic misstatement, line 104. PRESENT but wrong.** "1{,}500 base cases and 280{,}500 rows, including the base cases. 278{,}955 of these solved successfully, with the remainder failing to converge." From the parquet: 280,500 total rows, of which **280,455 converged** — 45 non-converged, not 1,545. The figure 278,955 is the count of converged **N-1** rows (279,000 N-1 rows minus the same 45), which is what `frozen_poster_numbers_v2.json` labels `converged_n1_rows`. As written the sentence implies a 0.55% non-convergence rate when the true rate is 0.016%.

**Model hyperparameters. ABSENT.** No `alpha`, `learning_rate`, `max_iter`, `max_leaf_nodes`, `min_samples_leaf`, or `l2_regularization` anywhere in the file. This is more than an omission of constants: the M2 protocol selects a *different* config per seed, so there is no single hyperparameter set to quote. From `tuned_metrics.json`, ridge M2 picks alpha ∈ {1.0, 0.001, 0.001, 0.001, 0.01} and histgb M2 picks five distinct random-search configs (learning rates 0.08–0.2, `max_iter` 300–1000, `max_leaf_nodes` 31–255). The reported means are therefore averages over five *different models*, which the paper does not say. `data/case30_dataset.manifest.json:model_hyperparameters` is `null`.

**Feature specification. PARTIAL.** Line 108 lists the feature families qualitatively (per-bus loads, generator setup, baseline voltages, failed equipment). The count is absent — the parquet has 634 columns; the block is 2 per bus (`pload_i`, `qload_i`) + 5 per generator + 118 `vm0_i`. How the outaged element is encoded to the model is not stated at all.

**Software versions. ABSENT.** No Python, pandapower, numpy, pandas, scikit-learn, pyarrow, or numba version appears in the file. All seven are in every manifest (Python 3.13.9, pandapower 3.5.4, numpy 2.3.5, pandas 2.3.3, scikit-learn 1.7.2, pyarrow 21.0.0, numba 0.66.0). CLAUDE.md §6 notes that a bare `python` on this machine is 3.12 / sklearn 1.8 and changes the numerical path, so the pin is not cosmetic.

**Seeds. PARTIAL.** "five different random splits" (line 108) and "over five random splits" (table captions, 156/178) — the count is stated, the values are not. Dataset seed 100, `nproc` 5, and the M2 inner seed 1000+i are all unstated.

**`t_surr`. ABSENT.** Equation (2) at line 129 introduces `t_surr` and line 131 defines it as "the surrogate time" but never gives a value. From `tuned_metrics.json`: 0.00116±0.00012 ms (ridge), 0.00241±0.00062 ms (histgb). Without it the reader cannot evaluate the "close to the inverse of the escalation rate" claim.

**Definitions. PRESENT.** Escalation, coverage, and missed-violation denominators are all pinned — table captions say "share of true violations" and "empirical coverage", and line 248 says "30.6\% of all contingencies". The gate rules at 123-125 are exact and match `feasibility/gate_eval.py` semantics.

**Data and code availability. PARTIAL.** GitHub URL at line 287. `data/*.parquet` is not committed (README:88), so the repo alone does not reproduce the artifact — the build command must be run first, and the paper does not give it. The in-file comment at 279-283 already flags that STS judges do not follow links.

**Same-configuration claim for 30-bus. PRESENT and correct.** Line 260's "simulated using the same configuration" holds: the `case30` manifest invocation differs from the `case118` command only in `--network` and `--out`.

## Two build-level problems

- **Figure paths are broken from the file's own directory.** All four `\includegraphics` calls (138, 208, 224, 243) use `data/…`, but the tex now lives in `report/` and there is no `report/data/`. It compiles only if run from the repo root with an explicit output directory, which nothing in the file states.
- **Line 138 points at `data/gate_schematic_v2.png`** while `data/gate_schematic_v3.png` (Aug 4, newer than v2's Aug 1) sits untracked in the working tree. Confirm which is intended.

Bibliography count is right: 19 `\bibitem`s against `\begin{thebibliography}{19}`.

## The four I would fix first

1. Rewrite III-A to state all four perturbation mechanisms with their committed values, drop the "and generator" from the 1.0–1.12 multiplier claim, and add the N-0 gate rule. As written, III-A describes a materially simpler dataset than the one that produced every number in the paper.
2. Correct the 278,955 sentence at line 104 — as written it overstates non-convergence by two orders of magnitude.
3. Add a one-sentence environment statement: CPU, core count, `numba=True`, `init="dc"`, Newton–Raphson, and the seven package versions. The 1.57× numba sensitivity makes this a precondition for the speedup numbers meaning anything.
4. Add ± to the two band widths (116) and to `t_solve` (131), state `t_surr`, and give split sizes in both scenarios and rows (108).

The per-seed-hyperparameter issue is separate and worth a decision rather than a patch: the paper currently presents ridge and histgb as two fixed models, but each headline row averages five differently-configured models selected by M2. That is a defensible protocol, and it is documented in `tuned_metrics.json:protocol`, but it is invisible in the paper.

---

### register — VERBATIM
Register review of `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex`. No sentences rewritten; line numbers and quoted text only.

**Prior-version comparison (hedging deletions): none found.** A paragraph-level diff of `git show urtc-submission:paper_current_URTC_20260808.tex` against the STS file shows every prose paragraph is byte-identical. The only body-text change is L116, `Section~V` → `Section~\ref{sec:discussion}`. All non-prose differences are preamble/float/table-rule formatting and the author block. So every register issue below is inherited from URTC, not introduced by the STS reformat — except the acknowledgments mismatch in §3.

**Per-category counts:** contractions 2; hedging 9 under-hedged + 8 over-hedged (17); voice consistency 6 structural + 1 pronoun-accuracy issue, spanning 7 sections/subsections; overclaiming vocabulary 6 live instances (1 further instance defensible as reported speech); quantitative words near table/figure references 7.

## 1. Contractions (2)

- **L86**: "to determine whether **there's** a present risk or not"
- **L94**: "which equipment is subject to the most danger when **there's** an equipment failure"

Both are in otherwise fully expanded-form paragraphs; no other contraction appears in the file.

## 2. Hedging (17)

**Under-hedged — claim stronger than the evidence line supports (9):**

- **L92**: "N-1 screening simulates these failures and **catches any violations** of the under-voltage floor"
- **L147**: "Both models **ensure that the band is calibrated**, as the coverage is close to 90\%" — measured coverage is 89.3±1.3 and 89.8±1.0; "ensure" asserts a guarantee the empirical numbers only approximate.
- **L147**: "Both surrogates **accurately predict** the minimum post-contingency voltage for the gate to work"
- **L86**: "we explain why there **must be** a certain floor for escalation"
- **L260**: "The floor exists on **any network**, but its height depends on the data distribution" — a network-general existence claim from two networks; the trailing clause hedges only the magnitude, not the existence.
- **L262**: "**mathematical proof is unable to** determine the safety of N-2 outages"
- **L258**: "the prediction intervals become **extremely wide, to the point where it becomes useless**"
- **L260**: "the method flags almost all instances as unsafe, **offering nothing to operators**"
- **L72** (abstract): "These results **allow operators to make an informed decision** about whether surrogate screening would be worthwhile on a particular network."

**Over-hedged — vague qualifier attached to a quantity that is exactly known (8):**

- **L94**: "it takes **up to several milliseconds** for one scenario" — the pinned solve time (9.14 ms, stated at L131) is exact.
- **L235**: "no 0.001-per-unit width bin makes up more than **around** 14\%"
- **L248**: "the gradient-boosted model flags violations **about as often as** they occur, so its ceiling **essentially** lands on the saturation point"
- **L250**: "accept **about a 1.6 times** speedup instead of the **2 to 3 times** available at 0.90"
- **L260**: "Increasing the threshold to 0.95 pu leads to an escalation of **roughly 1.5\%**"; "**almost all** instances"
- **L268**: "requires escalating **around two-thirds** of cases"; "the bands **often** straddle this limit"; "most of the cases fall **very close** to the limit"
- **L72** (abstract): "speedup dropping to **roughly 1.6**" and "results in a **64\%** escalation" — Table II gives 1.56±0.07 / 1.58±0.12 and 64.3±2.8; the abstract drops the error bars that the tables carry.
- **L262**: "we are **unsure of the frequency or timing** at which operators should recalibrate"

## 3. Voice consistency by section (6 structural + 1 pronoun accuracy)

- **Acknowledgments, L287**: "**The authors** would like to thank the program..." and "generated using **the authors'** committed and tested code" — third-person plural, carried over verbatim from the two-author URTC version. The STS byline (L57–59) is Rajan Saha alone, and the rest of the paper is first-person "we". This is the one place where the verbatim carry-over creates a factual register error, not just a stylistic one.
- **Prior-work tense, L86**: four verbs, three tenses in one paragraph — "Manoharan **utilized**", "the system also **runs**", "Alcántara and Chatzivasileiadis **use**", "Christianson et al. **designed**".
- **Method tense split**: III-A (L104) is past — "We **determined** the load and generation levels", "The base cases **were kept**" — while III-B (L108) is present — "The surrogate **predicts**", "The data **is split**", "we **split**", "We never **look**". Adjacent subsections, opposite conventions.
- **Results tense split**: L215 "we **adjusted** the target from 0.90 to 0.98 and **recorded**" (past) vs L231 "The gradient-boosted model **is** far more accurate" and L235 "Fig. 4 **provides** a histogram" (present).
- **Background voice, L92–96**: impersonal ("A per-unit voltage normalizes...", passive "An AC power flow solver **is used** to get...") interleaved with first person ("**We refer to** each pre-outage state", "**we do not check** for thermal line loading").
- **Register drop into colloquial diction**, against the formal register elsewhere: L72 "The **so-called** N-1 constraint"; L86 "To **double-check** reliability", "a binary **yes/no switch**", "Our work **stands out** from these papers"; L92 "cause the voltage to **plunge**"; L248 "**so much of** the distribution **sits just above** 0.94"; L250 "is **barely faster** than the solver"; L262 "or whether or not the grid **crashed in the first place**"; L268 "a **note of caution to anyone expecting** large speedups".
- **L258**: "Manoharan's audited population control ... **His** method uses a bound" — the cited author's pronouns are not stated anywhere in the source or the bibliography entry (L309, "J. Manoharan"). A gendered pronoun inferred from a name is a factual risk, not only a register one.

## 4. Overclaiming vocabulary (6 live, 1 defensible)

Grep over the full overclaim lexicon returns no "novel", "significant", "state-of-the-art", "outperform", "unprecedented", "robust", or "key contribution". "first" appears only in ordinal/temporal senses (L86 "First, unlike the first two approaches"; L209, L215 "first falls below 1\%"; L262 "in the first place"). Remaining hits:

- **L86**: "Our work **stands out** from these papers in three **distinct** ways"
- **L86**: "an input-convex network that **completely removes** false negatives" — attributed to Christianson et al. and immediately qualified ("although that claim is only relevant to DC power flow models"), so this one is defensible as reported speech.
- **L147**: "**ensure**" (see §2)
- **L231**: "The gradient-boosted model is **far more accurate**"; "The linear model also **demonstrates** the lower missed rate across all targets"
- **L260**: "**any network**" (see §2)
- **L268**: "**Our contribution is explaining why that floor exists**" — stated without network scoping, one sentence after the paper's own limitation that only two networks were tested.

Note on **L231**, "demonstrates the lower missed rate across all targets in the sweep": at the 0.90 row the gap is 2.96±0.44 vs 4.72±0.98 (clears the std rule), but at 0.97 it is 0.03±0.03 vs 0.83±0.24 and at 0.98 it is 0.00±0.00 vs 0.30±0.13 — the claim holds, but "across all targets" rests on rows whose stds are of the same order as the differences at the low end.

## 5. Quantitative words near table references (7)

- **L147**, one clause before `(Table~\ref{tab:models})`: "Both surrogates **accurately predict** the minimum post-contingency voltage" — qualitative verdict fronting a table of exact MAE/R² values.
- **L215**, opening on `Table~\ref{tab:ops}`: "The ridge model **behaves similarly**, with a missed rate below 1\% occurring first at 0.94 for the ridge model (0.79\% missed...) and 0.97 for the gradient-boosted model" — "similarly" spans two models that reach the same threshold three coverage steps apart; the sentence also names "the ridge model" twice while the second half is about histgb.
- **L231**, on `Table~\ref{tab:models}`: "**far more accurate**" for 1.6±0.1 vs 3.8±0.1 (10⁻³ pu), and "at 0.90 coverage it is also faster, with it being 3.29 times faster versus 2.04 times". Separately, the comparison this paragraph rests on — "at a coverage of 0.96, the linear model misses 0.14\% ... while the gradient-boosted model misses 1.36\%" — is read out of Table II (`tab:ops`), but the paragraph cites only `tab:models`, which has no 0.96 row.
- **L235**, one sentence before `Fig.~\ref{fig:boundary}`: "The **majority** of contingencies are within 0.005 per unit of the boundary, which results in a **large amount of** escalations" — followed immediately by the exact 56.86\%; "amount" is also a mass-noun form on a count noun.
- **L231**: "**Only a few** misses were serious" — cited to `Fig.~\ref{fig:missdepth}`, which plots counts.
- **L248**: "**so much of** the distribution sits just above 0.94 that this narrow window still captures 30.6\% of all contingencies".
- **L250**, on `Table~\ref{tab:models}`: "the model escalates 99.5\% of cases and is **barely faster** than the solver" — the table's persistence speedup row reads 1.00±0.00, i.e. not faster; "barely faster" states a direction the cited cell does not support.

---

### consistency — INCOMPLETE

The agent had not finished when this block was written. Its transcript's final assistant
text block reads, in full:

```
Now the data files.
```

No findings are recorded from it. **Nothing is inferred, predicted, or written on its
behalf.** Stage 1 verification is therefore 4 of 5 agents complete, and the
`consistency` dimension — cross-document contradictions between the manuscript and the
planning documents — remains UNCHECKED by an independent reviewer.

---

## CORRECTION C-2 — sampling parameters read from module defaults, not the committed run

**Raised:** 2026-08-19T03:34:00Z
**Trigger:** the `physics` agent's report, independently re-verified before acceptance.

**What I got wrong.** In an earlier status audit I reported two sampling parameters as
corrections to the Master Plan, and both were wrong. I read the module-level constants in
`feasibility/generate_dataset.py` and treated them as the values the committed dataset was
built with. They are defaults; the committed run overrides them on the command line.

| Parameter | What I reported | Committed run (`README.md:94-95`) | Module default |
|---|---|---|---|
| generator setpoint jitter | "Plan says ±0.025 pu. Code says `DVM = 0.03` → ±0.03 pu." | **`--dvm 0.025`** | `DVM = 0.03` |
| load reactive scaling | "Code is `PF_LO, PF_HI = 0.80, 1.50`" | **`--pf-lo 0.9 --pf-hi 1.15`** | `0.80, 1.50` |

The Master Plan's ±0.025 was **correct**; my correction of it was not. Verified here by
reading `README.md:94-95` directly.

This is the same failure mode this project has hit repeatedly and that section 0.7 exists to
prevent — reading state off one artifact and asserting it of another. A module default is
not a run configuration.

**Also corrected:** I described four "generator perturbation mechanisms". There are
**three** generator-side mechanisms (setpoint jitter, reactive-limit scaling, generator
outage). The fourth item, the `PF_LO`/`PF_HI` draw, scales **load** reactive power
(`q_new = q0 * mp * pf`, `generate_dataset.py:119`), not a generator quantity.

**Not affected:** the generator-outage finding stands unchanged and was independently
reproduced — `P_GEN_OUT = 0.30`; 374 of 1,500 base scenarios (24.93%) carry a generator
outage; the `physics` agent puts it at **69,532 of 278,955 N-1 rows (24.93%)**.

---

## NEW FINDING C1-7 — generator real power is never varied (manuscript line 104 is false)

Raised by the `physics` agent, independently re-verified here before acceptance.

Line 104 states the load and generation levels were set "by multiplying the load **and
generator** base values by multipliers ranging uniformly from 1.0 to 1.12."

`apply_scenario` sets `net.load["p_mw"]` (`generate_dataset.py:137`) and never assigns
`net.gen["p_mw"]`. Re-verified independently against the artifact: across the 1,500 base
rows, `genp_0` through `genp_4` each have `nunique = 1` and `std = 0.000000`. Generator real
power is fixed at base dispatch and the slack bus absorbs the entire load increase.

The sentence is false as written for generation. **HALT condition (section 2f): a result
contradicts a claim already printed in the manuscript.**

---

## NEW FINDING C1-8 — "all sit above 0.94 pu" is the acceptance criterion, not a property of the data

Raised by the `physics` agent. Line 260 offers as evidence for the 0.94 pu limit that
"Only 86 of the 1,500 base cases are above 0.95 pu, while all sit above 0.94 pu."

The 86 is correct. The second half is circular: `generate_dataset.py:256` REJECTS any base
case with `n0_min_vm < VMIN_LIMIT = 0.94`. Agent reports 46.18% of draws rejected to enforce
it, and min `n0_min_vm` = 0.94000004 — the gate boundary to eight digits. It cannot be
independent evidence for the threshold that produced it.

---

## NEW FINDING C1-9 — the STS file is byte-identical prose to the URTC submission

Raised by the `register` agent. A paragraph-level diff of
`git show urtc-submission:paper_current_URTC_20260808.tex` against the STS manuscript finds
**every prose paragraph byte-identical**. The only body-text change is line 116,
`Section~V` → `Section~\ref{sec:discussion}`. All other differences are preamble, float and
table-rule formatting, and the author block.

Consequence: every register and content defect in the STS file is inherited from URTC, not
introduced by the reformat. It also means the "written from scratch, sole-authored" STS
report described in the Master Plan does not yet exist as prose — what exists is the URTC
body in STS layout.

---

## CORRECTION C-3 — consistency agent completed; its INCOMPLETE marker is lifted

**Raised:** 2026-08-19T03:40:00Z

The Stage 1 verification block recorded `consistency-1e` as INCOMPLETE, quoting its
then-final transcript block in full:

> ```
> Now the data files.
> ```

That was accurate at 03:30Z. The agent went idle at 2026-08-19T03:24:06Z and its transcript
now carries a third assistant block of 23,225 characters. Re-extracted the same way (final
block only). **Stage 1 verification is now 5 of 5 agents complete**, and the `consistency`
dimension is no longer unchecked.

Superseded text: "Stage 1 verification is therefore 4 of 5 agents complete, and the
`consistency` dimension ... remains UNCHECKED by an independent reviewer."

---

### consistency — VERBATIM

Consistency review complete. All paths absolute; both sides of every pair quoted; no winner picked.

---

## The three items you asked about specifically

### A. M1 vs M2 — where the missed rate first falls below 1% — **CONFIRMED contradiction**

- **Side 1 (M1):** `/Users/rajansaha/contingency-screener-research/data/frozen_poster_numbers.json` → `crossings_first_below_1pct_missed`: **ridge 0.95** (0.586% missed), **histgb 0.96** (0.836% missed). Source field says `data/tradeoff_curve.json`.
- **Side 2 (M2):** `/Users/rajansaha/contingency-screener-research/data/frozen_poster_numbers_v2.json` → same key: **ridge 0.94** (0.794%), **histgb 0.97** (0.832%). Recomputed independently from `/Users/rajansaha/contingency-screener-research/data/tradeoff_curve_v2.json` with `.venv/bin/python`: ridge first <1% at 0.94, histgb at 0.97. Matches.
- **Manuscript side:** `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:215` and the Fig. 2 caption at `:209` both state 0.94 / 0.97.
- Both curves are live and both are cited as authoritative elsewhere. The reconciling rule exists (`/Users/rajansaha/contingency-screener-research/data/canonical.json`, entry `tradeoff_curve_version`, `"authoritative": "M2"`), and `/Users/rajansaha/contingency-screener-research/notes/ai-prompt-log.md:1735` already records the split. But two *instructional* documents still push the M1 numbers:
  - `/Users/rajansaha/contingency-screener-research/notes/reviewer-issues.md:9-11` — "**Canonical now:** … ridge 48.2% esc / 89.0% cov / 3.23% missed / 2.08x; histgb 33.0% / 89.9% / 6.91% / 3.04x. **Quote THOSE.**" Those are the M1 values from `frozen_poster_numbers.json`.
  - `/Users/rajansaha/contingency-screener-research/notes/defend-every-line.md:228,245,251` — "For the gradient-boosted model at the 90% coverage target it is 6.91%… you move to a higher coverage target, **around 0.96**, where the missed rate drops under one percent."
  - Against `/Users/rajansaha/contingency-screener-research/CLAUDE.md:174-175` (M1/M2 rule: never quote an M1 number as the result) and the manuscript's 4.72% / 0.97.

### B. "Every base case generates 186 related contingencies" vs the 30-bus — **CONFIRMED contradiction**

- `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:258` (Discussion, exchangeability argument): "**Every base case generates 186 related contingencies**, and therefore, the coverage rates are measured averages rather than guarantees on individual contingencies."
- `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:260` (next paragraph): "on the IEEE 30-bus network simulated using the same configuration…" — and `:104` states "since there are **41** rather than 186 branches, the 1,500 bases produce 61,500 contingency scenarios."
- The unqualified quantifier is contradicted by the 30-bus results the manuscript itself reports two sentences later. Independently flagged in `/Users/rajansaha/contingency-screener-research/STS 2027 Master Plan v3.md:875-876` as a camera-ready item — so the plan and the manuscript disagree about whether this sentence stands.

### C. `notes/erratum.md` E1 file references — **one broken, one correct, one incomplete**

- `/Users/rajansaha/contingency-screener-research/notes/erratum.md:10`: "`paper_current.tex:112` and `README.md:6` both embed `data/gate_schematic_v2.png`."
  - **`paper_current.tex` does not exist** anywhere in the working tree. The file carrying that `\includegraphics` is `/Users/rajansaha/contingency-screener-research/paper_current_URTC_20260808.tex:112` — the line number is exactly right, the filename is stale (renamed on commit `8cefaa7`).
  - `README.md:6` — **correct**, verified.
  - **Incomplete:** `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:138` also embeds `data/gate_schematic_v2.png` and is not listed in E1's "Where".
- `/Users/rajansaha/contingency-screener-research/notes/erratum.md:11` md5 `5b8e53a2…` for `data/poster/gate_schematic.png` ≡ `data/gate_schematic_v2.png` — **verified byte-identical**. `:29-35` md5 `5ceefccf…` for `data/gate_schematic_v3.png` — **verified**.
- `/Users/rajansaha/contingency-screener-research/notes/erratum.md:44-49`: "There is no `urtc-submission` tag. … `git tag -l` is empty locally, so no ref pins exactly what was submitted." **Contradicted:** `git tag -l` → `urtc-submission`; `git rev-parse urtc-submission` → `23bc7603…` (annotated tag on commit `8cefaa7`). Recorded in `/Users/rajansaha/contingency-screener-research/notes/RUN_REPORT.md:352-360`.
- `/Users/rajansaha/contingency-screener-research/notes/erratum.md:54`: "`paper_current.tex`, `data/poster/`, and `data/gate_schematic_v3.png` all remain uncommitted." All three are now committed (`git ls-files` = 208 files, `data/poster/*` and `data/gate_schematic_v3.png` tracked).

---

## Other contradictory pairs found

### 1. How many rows failed to converge — 1,545 vs 45 (highest-consequence pair)

- **1,545 side:** `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:104` — "The total sample contained 1,500 base cases and 280,500 rows, including the base cases. 278,955 of these solved successfully, **with the remainder failing to converge** and, as a result, removed." (remainder = 1,545). Identical text at `/Users/rajansaha/contingency-screener-research/paper_current_URTC_20260808.tex:81`. Read the same way at `/Users/rajansaha/contingency-screener-research/STS 2027 Master Plan v3.md:358-366` — "**1,545 cases were excluded for failing to converge** … against ~48,760 true violations, that's **up to 3.07 percentage points** — which would break the sub-1% operating point the whole paper recommends."
- **45 side:** `/Users/rajansaha/contingency-screener-research/data/nonconverged_gate.json` — `"n_nonconverged": 45`, with `note_1545`: "1545 = 280500 total − 278955 converged N-1 = 1500 N-0 base rows (all converged, excluded because they are base cases not contingencies) + 45 genuine non-convergences. **Only the 45 are solver failures.**" Corroborated by `/Users/rajansaha/contingency-screener-research/notes/frozen-gaps.md:14-16` ("1,500 × 186 minus frozen converged_n1_rows 278,955 = **45** on v2") and `/Users/rajansaha/contingency-screener-research/data/break_even.json` (`"n1_solves": 279000`).
- **Downstream conflict:** `/Users/rajansaha/contingency-screener-research/notes/retired/2026-08-17_ai_draft_sections_RETIRED.md:29` — "the linear model at the 0.94 target rises from 0.79% to **3.87%** and the gradient-boosted model at 0.97 from 0.83% to **3.90%**. **No coverage target in our sweep recovers a sub-1% missed rate** under that treatment." Recomputed from `data/nonconverged_gate.json` (5-seed means): ridge@0.94 published 0.79% → 0.79% if non-converged count as violations; histgb@0.97 0.83% → 0.83%. The gate certifies 1 of 45 (ridge, one seed) and 10 of 225 seed-rows (histgb@0.90).

### 2. Saturation point — 82.52% vs 82.64%

- `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:248`: "escalation moves closer to every case predicted at or above the limit, **the remaining 82.52%** of cases, or the saturation point" (= 100 − 17.48).
- `/Users/rajansaha/contingency-screener-research/data/frozen_poster_numbers_v2.json` → `ceilings.perfect_model_floor_saturation = 0.826352…` (**82.64%**), sitting in the same object as `true_violation_rate: 0.1748`. Same value in `/Users/rajansaha/contingency-screener-research/data/frozen_poster_numbers.json`.
- `/Users/rajansaha/contingency-screener-research/data/case30_frozen.json` → `case118_comparators.saturation_point_pct: 82.52`, with `"source": "data/frozen_poster_numbers_v2.json"` — citing a file that carries 82.64.
- (The 74.9% / 82.8% escalation ceilings at `:248` **do** match `frozen_poster_numbers_v2.json` → 0.74888 / 0.82795. It is only the saturation figure that splits.)

### 3. Generator sampling — the manuscript describes one mechanism, the plan four

- `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:104`: "We determined the load and generation levels by **multiplying the load and generator base values by multipliers ranging uniformly from 1.0 to 1.12.**"
- `/Users/rajansaha/contingency-screener-research/STS 2027 Master Plan v3.md:478-483`: "The actual generator perturbation has **four mechanisms**: voltage setpoints shifted by ±0.025 pu, reactive limits scaled by a random factor in [0.60, 1.40], **a 30% per-scenario chance of a full generator outage**, and an independent power-factor draw."
- Code side: `/Users/rajansaha/contingency-screener-research/feasibility/generate_dataset.py:26` (`QLIM_LO, QLIM_HI = 0.60, 1.40`), `:28` (`P_GEN_OUT = 0.30`), `:23` (`PF_LO, PF_HI = 0.80, 1.50`), `:25` (`DVM = 0.03`), `:84` (`gen_vm0[i] + rng.uniform(-DVM, DVM)`).
- A *third* value for two of these: the committed invocation at `/Users/rajansaha/contingency-screener-research/feasibility/broadened-diversity.md:62` uses `--pf-lo 0.9 --pf-hi 1.15 --dvm 0.025`, i.e. the script's in-file defaults (0.80/1.50, 0.03) are not what produced the artifact. Same split recorded independently at `/Users/rajansaha/contingency-screener-research/notes/reviewer-issues.md:180-190` (Issue 3).
- Related: `/Users/rajansaha/contingency-screener-research/STS 2027 Master Plan v3.md:484-487` says to verify sampling params "against `generate_dataset.py` and the committed config, **not** against `case57_gonogo.py`'s `COMMITTED_CFG`" — but `/Users/rajansaha/contingency-screener-research/data/case30_dataset.manifest.json:55` records `"config_source": "feasibility/case57_gonogo.py:COMMITTED_CFG"` for the case30 build the manuscript reports at `:104` and `:260`.
- Also unresolved between the two: a 30% per-scenario generator outage means a share of "N-1" rows are effectively N-2 states, against `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:262` — "Our claims of safety are only true for N-1 contingency cases, since **we did not test N-2 cases**."

### 4. Can a pre-outage model predict the deep collapse?

- `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:262`: "A model trained only on pre-outage features **cannot predict such a situation.**"
- `/Users/rajansaha/contingency-screener-research/STS 2027 Master Plan v3.md:392-397`: "**Collision to resolve before writing:** … A pre-outage *signature* is by definition learnable from pre-outage features. If this lands, you've **refuted your own published limitation**." Still open at `:851`.

### 5. The 1.5%-at-L=0.95 artifact

- `/Users/rajansaha/contingency-screener-research/STS 2027 Master Plan v3.md:327`: "The 1.5% escalation figure at L=0.95 has **no committed artifact.**" Echoed in the manuscript's own comment block, `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:282-283`.
- `/Users/rajansaha/contingency-screener-research/data/escalation_at_095.json` is committed and gives ridge 1.385% ± 0.326, histgb 1.578% ± 1.190 at L=0.95 — supporting "roughly 1.5%" at `:260`. `/Users/rajansaha/contingency-screener-research/data/bases_clearing_0p95.json` is committed and gives `ge_0p95: 86` of 1,500, `min_base: 0.94000004` — supporting the "86 … while all sit above 0.94 pu" at the same line.

### 6. What the URTC text actually says vs the camera-ready list

- `/Users/rajansaha/contingency-screener-research/STS 2027 Master Plan v3.md:879`: "§V **'less than 1.5%'** — sharper than the artifact supports; 'roughly' was safer." Same defect narrative at `:737` ("'roughly 1.5%' → 'less than 1.5%'" as one of three hedge deletions).
- `/Users/rajansaha/contingency-screener-research/paper_current_URTC_20260808.tex:230` and `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:260` both read "**roughly** 1.5\%". The hedge is present in both `.tex` files, including the one pinned by the `urtc-submission` tag.
- (The companion hedge, "around 14%", is intact at `report/paper_current_STS.tex:235`.)

### 7. STS manuscript provenance — verbatim vs from scratch

- `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:3-4` (header): "Body text is **VERBATIM from the URTC conference version** (paper_current.tex, IEEEtran). Only the format changed."
- `/Users/rajansaha/contingency-screener-research/STS 2027 Master Plan v3.md:7`: "STS version **written from scratch**, sole-authored." Repeated at `:162` and `:660` ("In all three branches the STS report is sole-authored and written from scratch").
- Related: the header cites `paper_current.tex`, which does not exist.
- Related: `:287` says "**The authors** would like to thank…" (plural) against the sole-authored framing.

### 8. AI disclosure — three incompatible accounts

- `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:287`: "An AI assistant, Claude from Anthropic, was used to **validate the code and grammar.**" Identical at `/Users/rajansaha/contingency-screener-research/paper_current_URTC_20260808.tex:238`.
- `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:274-278` (its own comment): "`notes/ai-prompt-log.md` records **AI-WRITTEN scaffolding for the dataset generator, screener and eval harness, plus text revision.** Audit the log and widen this to match."
- `/Users/rajansaha/contingency-screener-research/STS 2027 Master Plan v3.md:130-136`: "Your own audit found **five passages where wording was AI-chosen** … the STS one must be specific."
- `/Users/rajansaha/contingency-screener-research/notes/handoff-2026-08.md:46-53` records a *fourth* wording — a staged-index version reading "The authors used an AI for revising the document text…" and a then-current working-tree version that "**drops the AI-revision clause entirely**." Neither matches what is in either `.tex` today.
- Related scope conflict: `/Users/rajansaha/contingency-screener-research/notes/contribution-log.md:8-11` records the AI-prose exception as one task only, "which resumes in full after this task"; `/Users/rajansaha/contingency-screener-research/notes/retired/2026-08-17_ai_draft_sections_RETIRED.md:1` is a second instance — "Same content, **same voice as the current paper**" — dated 2026-08-17, quarantined but not covered by the logged exception.

### 9. External links — plan forbids, manuscript prints one

- `/Users/rajansaha/contingency-screener-research/STS 2027 Master Plan v3.md:75`: "**Judges will not click any external links** — explicit annual decision. Code must live inside the 20 pages or nowhere." Compliance gate at `:719` asserts "no external links outside the bibliography."
- `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:287` prints `\url{https://github.com/rajsaha-blip/contingency-screener-research}` in Acknowledgments. The manuscript's own comment at `:279-283` flags it. `/Users/rajansaha/contingency-screener-research/notes/RUN_REPORT.md:246-251` (C0-3) adds that this URL is `upstream`, not `origin` (`RS499/contingency-screener-research`), and that both remotes sit 5 commits behind local.
- Also unmet: `:81` requires "Full APA citation directly beneath each figure *and* table"; the manuscript has none, and uses IEEE numeric references throughout.

### 10. ANSI C84.1 Range B — 0.917 pu

- `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:260`: "The ANSI C84.1 Range B specification [ansi2020] allows service voltages down to **0.917 pu**."
- `/Users/rajansaha/contingency-screener-research/STS 2027 Master Plan v3.md:911-912`: "The ANSI Range B numeric is **unverified against the paid standard**; secondary sources give **0.9167 pu** for service voltage and 0.867 for utilization. Disclose or drop." Also `:877` ("sourced from a NEMA excerpt — drop the number") and `:729-733`.
- Third account: `/Users/rajansaha/contingency-screener-research/notes/defend-every-line.md:408` — "the service-voltage standard (ANSI C84.1 **Range A**, NERC guidance) is **0.95 pu**."

### 11. Which build the 0.95-threshold answer rests on

- `/Users/rajansaha/contingency-screener-research/notes/defend-every-line.md:413,419`: "Only **44** of the 1,500 accepted bases (**2.93%**) also clear 0.95… The resampled v2 build raises base voltages somewhat, so the true share is higher than 2.93%."
- `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:260`: "Only **86** of the 1,500 base cases are above 0.95 pu." `/Users/rajansaha/contingency-screener-research/data/bases_clearing_0p95.json` carries both under explicit labels (`canonical_v2.ge_0p95: 86` / `clip_era.ge_0p95: 44`), so the artifact is the one place they are reconciled.

### 12. Converged-row count — 278,955 vs 278,960

- `/Users/rajansaha/contingency-screener-research/notes/reviewer-issues.md:21`: "the **278,960** converged N-1 cases in `data/dataset.parquet`."
- `/Users/rajansaha/contingency-screener-research/data/frozen_poster_numbers.json` → `converged_n1_rows: 278955`; same in `_v2`; `report/paper_current_STS.tex:104` states 278,955.
- `/Users/rajansaha/contingency-screener-research/notes/defend-every-line.md:234-236` attributes 278,960 to the *clip-era* build (`notes/artifact-clip-0.94.md`) and 278,955 to v2, so the reviewer-issues line applies a clip-era count to the v2 parquet by name.

### 13. Speedup vs parallelism — plan raises it, manuscript does not

- `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex:129-131` (Eq. 2) states no core count or hardware; `:147` reports "3.29 times faster than the solver."
- `/Users/rajansaha/contingency-screener-research/STS 2027 Master Plan v3.md:439-447`: "N-1 is embarrassingly parallel — 186 independent solves… **3.29× on one thread does not survive that comparison.**"
- `/Users/rajansaha/contingency-screener-research/data/parallel_speedup.json` now exists and measures 10 cores, effective 2.37 ms/case at 8 workers (vs 10.08 ms serial), and its own `benchmark_basis` field notes the P=1 mean is "not directly comparable" to the committed `ms_solver=9.14` minimum. Nothing in either `.tex` cites it.

### 14. `CLAUDE.md` self-description vs repository state

All four were flagged in `/Users/rajansaha/contingency-screener-research/notes/RUN_REPORT.md:264-273` (C0-6, C0-7) and `:522-534`; all four still hold at HEAD `af85c34`:

- `/Users/rajansaha/contingency-screener-research/CLAUDE.md:161` — "Root `CLAUDE.md` (this file): SHARED conventions, **TRACKED in git**." vs `git ls-files` → CLAUDE.md absent (208 tracked files, none of them CLAUDE.md).
- `/Users/rajansaha/contingency-screener-research/CLAUDE.md:163-165` — "As of this writing **only `README.md` is committed** (HEAD `a4df350`)" vs 23 commits, HEAD `af85c34`, 208 tracked files; `a4df350` is the 4th commit from the root.
- `/Users/rajansaha/contingency-screener-research/CLAUDE.md:128` and `:154-156` name a `tests/` directory and `paper_current.tex`; neither exists. All 28 tests are under `feasibility/`.
- `/Users/rajansaha/contingency-screener-research/CLAUDE.md:170` — "**The live draft is `paper_current.tex`** (repo root) — **the only one**." vs three drafts, none at that path: `paper_current_URTC_20260808.tex`, `report/paper_current_STS.tex`, and a deleted-from-index root `paper_current_STS.tex` (`git status` shows ` D paper_current_STS.tex`).
- The file also carries two headers: `:1` "# CLAUDE.local.md — PRIVATE context (git-ignored)" and `:36` "# CLAUDE.md — … (SHARED, tracked)", with the private half repeatedly citing "`CLAUDE.md` §8" as a separate document. Recorded as an open item at `/Users/rajansaha/contingency-screener-research/notes/RUN_REPORT.md:522-534`.

### 15. Dangling cross-references in the notes (each is one side of a pair with a file that does not exist)

- `notes/frozen-gaps.md:8` — "CLAUDE.md **3** (histgb 0.913, ridge 0.777)"; `:11-12` — "CLAUDE.md **5.5** (28.6% violation; ridge 3.84%, histgb 3.01% missed)"; `notes/reviewer-issues.md:12` — "one-sided floor is ~40-55% (**CLAUDE.md 3, 5.5**)"; `notes/contribution-log.md:5` — "**CLAUDE.md section 10** makes disclosure the default". Against `/Users/rajansaha/contingency-screener-research/CLAUDE.md:6-9`, which has 9 sections, no §5.5 or §10, and states "**No result number appears in this file.**" (Separately, the 0.913 there is the M1 R²; the manuscript's Table I at `report/paper_current_STS.tex:166` gives histgb R² 0.92, the M2 value.)
- `notes/reviewer-issues.md:212`, `notes/contribution-log.md:13`, `notes/handoff-2026-08.md:56`, `notes/frozen-gaps.md:44` all cite `notes/1_research_draft.txt`. Only `notes/1_research_draft_ORIGINAL.txt` and `notes/1_research_draft_ORIGINAL_rev2.txt` exist.
- `notes/frozen-gaps.md:22-28` states the histgb band width as "`q_hat = 0.002557`" from `data/tradeoff_curve.json` and that "the gate schematic figure … reads it from the tradeoff curve to size its band" — which is precisely the defect `notes/erratum.md:16-20` calls a violation of the M1/M2 rule (M2 value 0.002291, matching `report/paper_current_STS.tex:116`'s "0.0023 per unit").

### 16. `notes/RUN_REPORT.md` Stage 0 inventory vs current state

Time-evolution rather than authored disagreement, but the report is written as current and is append-only:

- `:100,376` — "152 tracked files … `notes/` 0" vs 208 now (`notes/` still 0).
- `:58` — "`report/` exists? **No such directory**" vs `/Users/rajansaha/contingency-screener-research/report/` present.
- `:59,341` — "`paper_current_STS.tex` **untracked**" vs it having since been tracked at the repo root and then deleted from the index (` D`), with the live copy untracked under `report/`.
- `:389-393` (C0-9) — "the tag is not on any branch … `8cefaa7` is a child of `9cba13e`, not an ancestor" vs `git merge-base --is-ancestor urtc-submission HEAD` → **true** now (HEAD advanced to `af85c34` through `8cefaa7`).

### 17. Minor / lower-confidence

- **Cross-model headline in the abstract.** `report/paper_current_STS.tex:72` pairs "a 64% escalation and speedup dropping to roughly 1.6" (that is **ridge**@0.94, per Table II `:186`) with "8.96±0.91% escalation at 11.27±1.02 times" for the 30-bus (that is **histgb**@0.93, per `data/case30_frozen.json` → `crossings_first_below_1pct_missed.histgb`; ridge on case30 crosses at 0.92 with 34.5% escalation and 2.98×). Same pairing at `STS 2027 Master Plan v3.md:216-219`. Neither states which family each column is.
- **Fig. 3 caption vs body.** `report/paper_current_STS.tex:225` — "**Most** misses stay within one band"; `:231` — "74% … for the linear model and **55%** for the gradient-boosted model."
- **Missing manifest.** `CLAUDE.md:180` requires "Manifest beside every new artifact"; `data/dataset.parquet` has no `.manifest.json` (`data/case30_dataset.manifest.json` exists for the second network).
- **`notes/science-review.md:266-271`** closes with "the feasibility GO verdict (convergence, speed, straddle abundance) … **has not yet been re-established** under the physically correct `enforce_q_lims=True` oracle," against `notes/state-of-project.md:20-24`, which reports the corrected ceiling (~140%) and the built dataset under that oracle. `science-review.md:3-6` carries a "Historical, 2026-07-21" banner; the closing sentence does not.

---

## STAGE 1 — VERIFICATION CLOSED (2026-08-19T03:44:00Z)

All five agents returned. `consistency` output is appended verbatim above under CORRECTION
C-3. Agent findings are **reports, not findings of fact** until re-derived; the items below
were independently re-computed in the main session before being recorded as confirmed.

### Independently re-verified from the consistency report

**C1-10 — two instructional notes still direct a future session to quote M1 numbers.**
Verified by reading the file directly:

- `notes/reviewer-issues.md:9-11` — "**Canonical now:** the v2 committed pipeline
  (`data/screener_metrics.json`, 5 seeds, pinned solver) at 90% coverage — ridge 48.2% esc /
  89.0% cov / 3.23% missed / 2.08x; histgb 33.0% / 89.9% / 6.91% / 3.04x. **Quote THOSE.**"

Those are M1 values. `CLAUDE.md` §8 states M2 is the promoted selection and an M1 number is
never the result. The manuscript quotes the M2 values (4.72% histgb missed at 0.90).

Crossing points differ between the curves, verified directly from both artifacts:

| Artifact | ridge first <1% missed | histgb first <1% missed |
|---|---|---|
| `data/frozen_poster_numbers.json` (M1) | **0.95** (0.586%) | **0.96** (0.836%) |
| `data/frozen_poster_numbers_v2.json` (M2) | **0.94** (0.794%) | **0.97** (0.832%) |
| manuscript lines 209, 215 | 0.94 | 0.97 |

The manuscript is on the M2 side and correct. The hazard is that a note in `notes/` instructs
otherwise, and notes are what a future session reads first.

**C1-11 — the abstract compares two different model families without saying so.** Verified
against `data/case30_frozen.json`:

- 118-bus: "a 64\% escalation and speedup dropping to roughly 1.6" = **ridge** @ 0.94
  (Table II, line 186: 64.3±2.8, 1.56±0.07).
- 30-bus: "8.96$\pm$0.91\% escalation at 11.27$\pm$1.02 times" = **histgb** @ 0.93
  (`case30_frozen.json` → `crossings_first_below_1pct_missed.histgb`: escalation
  0.08959349593495934, net_speedup 11.265301491886408).
- Ridge on case30 crosses at 0.92 with 34.5% escalation and 2.98x — a fifth of the headline
  speedup.

Neither column is labelled with its family. The 2.8x boundary-mass difference between
networks is the paper's argument; a cross-family pairing inflates the contrast beyond what
the mechanism explains.

**C1-12 — `data/dataset.parquet` has no manifest.** Verified: `data/dataset.manifest.json`
is ABSENT, while `data/case30_dataset.manifest.json` exists. `CLAUDE.md` §8 requires a
manifest beside every new artifact. The primary dataset — the input to every result in the
paper — is the one artifact without one.

### Not re-verified in the main session

The consistency report's items 14, 15, 16 and 17 (CLAUDE.md self-description drift, dangling
`notes/` cross-references, Stage 0 inventory time-evolution, Fig. 3 caption vs body) are
recorded verbatim above but were **not** independently re-derived here. They are the agent's
account, not confirmed fact. Items 14 and 16 largely restate findings already logged as C0-6,
C0-7 and C0-9.

### Stage 1 close

| Precondition for Stage 2 | Status |
|---|---|
| Boundary hook installed and demonstrated | MET |
| Prompt log gap closed | MET |
| Test suite green, no return-guards | MET — 28 passed, 0 warnings |
| Instruments built or explicitly deferred | MET — 10 built, 2 deferred |
| Subagent roster | MET — 6 definitions |
| **1e verification complete** | **MET — 5 of 5 agents returned** |
| Tree committed | **NOT MET** |
| `notes/` backup current | **NOT MET** |

**HALT stands** under section 2f: a result contradicts a claim already printed in the
manuscript (C1-7, generator real power is never varied). Stage 2 not entered.

---

## STAGE 2 — Remaining Tier-1 experiments (2A, 2B)

**Started:** 2026-08-19T03:48:00Z
**Ended:** 2026-08-19T03:47:00Z (2A sweep completed 04:43 wall)
**Git HEAD at start:** `6082204` (Stage 1 committed by the author between stages)
**Tree dirty at end:** YES — three new artifacts plus three new scripts. Nothing committed.

### What ran

```
.venv/bin/python scripts/dataset_manifest.py
.venv/bin/python scripts/thermal_check.py --max-scenarios 3      # smoke
.venv/bin/python scripts/thermal_check.py --max-scenarios 120    # headless, 416.6 s
.venv/bin/python scripts/sampling_audit.py
```

Solver pinned throughout: `enforce_q_lims=True, numba=True, init="dc", algorithm="nr"`.
No seeds are consumed — 2A re-solves committed scenarios, 2B reads only.

### Pre-registration

Written to `notes/preregistration.md` at 2026-08-19T03:52:00Z, **before** either script ran,
at HEAD `af85c34`. Quantities already observed earlier in the session are marked
`ALREADY OBSERVED` there and are NOT counted as predictions.

---

### 2A — Thermal and over-voltage → `data/thermal_check.json`

#### Rating audit — the answer is a third category the plan did not list

The plan asks for "violations are ZERO, or UNDEFINED (no rating)". Neither fits case118. A
third case occurs and is the dangerous one: **ratings populated but placeholder**. A naive
loading check against a placeholder returns a comforting zero, which would be the most
misleading possible answer. The script therefore reports the rating audit separately and
**refuses to run a loading sweep on a placeholder rating**.

| | case118 | case30 |
|---|---|---|
| lines | 173 | 41 |
| `max_i_ka` NaN | 0 | 0 |
| `max_i_ka` distinct values | **2** | 6 |
| `max_i_ka` range | 16.5674 – 41.4186 kA | 0.0684 – 0.5560 kA |
| **implied MVA rating** | **9900 – 9900** | 16 – 130 |
| transformers | 13 | 0 |
| `sn_mva` | **9900.0, single value** | n/a |
| N-0 max line loading | **4.475%** | **111.831%** |
| N-0 median line loading | 0.348% | 26.924% |
| N-0 max trafo loading | 3.589% | n/a |
| **LINE VERDICT** | **UNDEFINED (populated but PLACEHOLDER)** | **RATED** |
| **TRAFO VERDICT** | **UNDEFINED (populated but PLACEHOLDER)** | **N/A (no transformers)** |

The case118 evidence is unambiguous: every line rating implies exactly **9900 MVA**, and
every transformer `sn_mva` is exactly **9900**. One placeholder magnitude, applied uniformly,
in two different units. The base case loads it to 4.5%.

**So thermal on case118 is UNDEFINED, and the manuscript's scope exclusion is forced by the
data rather than chosen.** That is the strongest available form of that limitation.

#### case30 thermal sweep — SAMPLE, not a full sweep

| | value |
|---|---|
| coverage | **SAMPLE — first 120 of 1500 base scenarios, in dataset order, not random** |
| contingencies solved | 4,920 |
| solver failures | 0 |
| elapsed | 416.6 s |
| **share above 100% loading** | **1.000000** |
| share above 95% | 1.000000 |
| median max-line loading | **154.72%** |
| p90 | 192.48% |
| max | 490.45% |

**Every one of 4,920 case30 N-1 contingencies exceeds 100% line loading.** The base case
already sits at 111.83%. A 3-scenario smoke run beforehand gave share = 1.0 over 123
contingencies, so the result is stable across two disjoint sample sizes.

The full 1,500-scenario sweep was NOT run: at 416.6 s per 120 scenarios it projects to ~87
minutes, which exceeds the "ask before heavy compute" threshold. The prefix sample is
labelled as such inside the artifact (`coverage`, `sample_note`). It is a prefix, not a
random sample, so it is an estimate over dataset order — but with an observed share of
exactly 1.0 over 4,920 draws the qualitative conclusion does not depend on the sampling
scheme.

#### Over-voltage — recomputed from scratch, not copied

| population | n | > 1.05 | > 1.06 | max `max_vm` | median `max_vm` |
|---|---|---|---|---|---|
| case118 N-0 base | 1,500 | **0.734000** | 0.058000 | 1.12220 | 1.05435 |
| case118 N-1 converged | 278,955 | **0.731358** | 0.057368 | 1.15291 | 1.05425 |
| case30 N-0 base | 1,500 | **0.000000** | 0.000000 | 1.02498 | 1.01651 |
| case30 N-1 converged | 61,500 | **0.000000** | 0.000000 | 1.02635 | 1.01652 |

Two-key: recomputed through a second, independent route (pyarrow table read plus numpy masks
rather than the pandas path used inside the script) — N-1 `0.731358104`, N-0 `0.734000000`.
Identical.

The case30 column is new and matters: it is **0.00%**, so the over-voltage finding is
**case118-specific**, not a property of the sampler in general.

#### Pre-registration outcome — 2A

| Prediction | Outcome |
|---|---|
| **P2A-1** `max_i_ka` populated on case118 | **CORRECT literally** — 0 NaN. But the literal answer is not the useful one; see P2A-2's note. |
| **P2A-2** `sn_mva` populated | **CORRECT**, and the recorded caveat ("populated does NOT imply meaningful") is exactly what occurred: a single 9900 MVA value across all 13 transformers. |
| **P2A-3** thermal violations non-zero but **under 5%** | **WRONG.** Unfalsifiable on case118 (UNDEFINED); on case30 the share is **100%**, not under 5%. Recorded at LOW confidence as "the prediction most likely to be wrong", and it was. |
| **P2A-4** thermal/voltage violation sets overlap with Jaccard < 0.5 | **CANNOT BE COMPUTED.** On case118 thermal is UNDEFINED. On case30 the thermal violation set is the entire population, so every voltage violation is trivially also a thermal violation and Jaccard reduces to the voltage share — a degenerate test, not a measurement. |

---

### 2B — Generator outage and multiplier audit → `data/sampling_audit.json`

#### Outage probability and prevalence

| | value |
|---|---|
| `P_GEN_OUT` as coded | **0.30** (`feasibility/generate_dataset.py:28`) |
| RNG draw site | `feasibility/generate_dataset.py:128` — `if rng.random() < P_GEN_OUT` |
| candidate pool | non-slack generators only |
| base scenarios carrying an outage | **374 / 1,500 = 0.249333** |
| N-1 converged rows whose base carries one | **69,532 / 278,955 = 0.249259** |

The `physics` agent's 69,532 / 278,955 is now independently re-derived in the main session.

**A quarter of the rows the manuscript calls "single-element failures" are two-element
states** — a generator out of service in addition to the outaged branch.

#### Acceptance-gate effect — P2B-1

| | value |
|---|---|
| coded probability | 0.300000 |
| observed share among accepted bases | 0.249333 |
| relative acceptance odds (gen-out vs not) | **0.7750** |
| mean `n0_min_vm` with outage | 0.943813 |
| mean `n0_min_vm` without | 0.944104 |
| median with / without | 0.943045 / 0.943486 |

**P2B-1 CONFIRMED in direction.** Gen-out scenarios are accepted at 0.775 the odds of
healthy ones, and accepted gen-out bases sit closer to the 0.94 rejection boundary — mean
lower by 0.000291 pu, median by 0.000441 pu.

**Stated limitation:** rejected draws are not recorded in the dataset, so the rejection rate
by outage status **CANNOT BE COMPUTED** from this artifact. The odds ratio is inferred from
the accepted population against the coded probability, which assumes the coded 0.30 is the
draw rate — true by construction, but it is an inference, not a direct measurement.

#### Distribution by outage status — P2B-2, P2B-3

| | n | violation rate | boundary strip | mean `min_vm` | p01 | min |
|---|---|---|---|---|---|---|
| with generator outage | 69,532 | **0.182362** | **0.580956** | 0.939471 | 0.87971 | 0.72240 |
| without | 209,423 | **0.172230** | **0.564537** | 0.939944 | 0.88209 | 0.71794 |
| **delta** | | **+1.0132 pp** | **+1.6419 pp** | −0.000473 | | |

**P2B-2 CONFIRMED** — higher violation rate, gap +1.01 pp, inside the predicted "under 3 pp".
**P2B-3 CONFIRMED** — higher boundary-strip share, +1.64 pp.

Both differences are real but small. The mechanism predicted at pre-registration holds: the
base case already cleared 0.94 *with* the generator out, so these scenarios are pre-screened
for feasibility and the residual effect is reduced reactive headroom under contingency.

#### Multiplier audit — three independent routes, all agreeing (P2B-4)

**Route 1, static.** Every `net.*` assignment inside `apply_scenario`, by AST walk:

| line | target |
|---|---|
| 137 | `net.load['p_mw'] = params['p_new']` |
| 138 | `net.load['q_mvar'] = params['q_new']` |
| 139 | `net.gen['vm_pu'] = params['gen_vm']` |
| 140 | `net.gen['min_q_mvar'] = params['gen_qmin']` |
| 141 | `net.gen['max_q_mvar'] = params['gen_qmax']` |
| 142 | `net.gen['in_service'] = True` |
| 144 | `net.gen.iat[gen_out, 'in_service'] = False` |

`net.gen['p_mw']` appears **nowhere**. That is a parse result, not a reading.

**Route 2, empirical.** Per-family variance across the 1,500 base scenarios:

| family | verdict |
|---|---|
| `pload_` | VARIES |
| `qload_` | VARIES |
| **`genp_`** | **CONSTANT — not varied by any sampling mechanism** |
| `genvm_` | VARIES |
| `genqmin_` / `genqmax_` | VARIES |
| `genon_` | VARIES |
| `vm0_` | VARIES |

**Route 3, documented.** `README.md:94-95` committed invocation.

**The answer, for the corrected Section III-A sentence:**

**TOUCHED by the 1.0–1.12 multiplier:**
- `net.load.p_mw` — directly, `p_new = _p0 * mp`.
- `net.load.q_mvar` — `q_new = _q0 * mp * pf`, i.e. scaled by the multiplier **and** by an
  independent power-factor draw `pf ~ U(0.9, 1.15)` as invoked.

**NOT touched by the multiplier:**
- `net.gen.p_mw` — **never assigned at all.** Generator real power stays at base dispatch;
  the slack bus absorbs the entire load increase.
- `net.gen.vm_pu` — varied, by an independent `±dvm` jitter (`--dvm 0.025` as invoked).
- `net.gen.min_q_mvar` / `max_q_mvar` — varied, by an independent `U(0.60, 1.40)` draw.
- `net.gen.in_service` — set by the independent `P_GEN_OUT = 0.30` draw.

Realised `agg_loading`: **1.014225 – 1.123857**. The max exceeds 1.12 because the regional
mode applies a block multiplier plus per-load jitter.

**P2B-4 CONFIRMED** by all three routes.

---

### Verification

Two-key applied to every recorded quantity that had a second route:

| Claim | Key 1 | Key 2 (different path) | Agreement |
|---|---|---|---|
| case118 N-1 share `max_vm` > 1.05 | pandas in `thermal_check.py` → 0.731358104 | pyarrow table + numpy masks → 0.731358104 | MATCH |
| case118 N-0 share > 1.05 | 0.734000 | 0.734000000 | MATCH |
| case30 thermal share > 100% | 3-scenario smoke, n=123 → 1.0 | 120-scenario sample, n=4,920 → 1.0 | MATCH |
| `genp_*` never varied | AST: no `net.gen['p_mw']` assignment | empirical: nunique=1, std=0 | MATCH |
| gen-outage share of N-1 rows | `physics` agent → 24.93% | main-session recompute → 0.249259 | MATCH |
| `--dvm 0.025` | `README.md:95` | artifact max deviation 0.024995 | MATCH |
| `data/dataset.parquet` sha256 | `hashlib` in `dataset_manifest.py` | `shasum -a 256` | MATCH |

No verifier subagent was run for Stage 2. The roster exists; this is a gap, recorded as one.

### Contradictions found

**C2-1 — case30 is thermally infeasible in the base case.** N-0 max line loading is
**111.83%** before any contingency. The manuscript uses case30 as the counter-example
network whose low boundary mass yields 8.96% escalation and 11.27× speedup (line 260, and
the abstract). Those are voltage-only figures on a network where the base case already
violates its own line ratings and 100% of sampled N-1 contingencies do. This does not
contradict a printed sentence — line 262 discloses that thermal was not checked — but it
materially qualifies what the 30-bus operating point demonstrates. Recorded, not resolved.

**C2-2 — case118 thermal ratings are placeholders, so "we do not check thermal" is not a
choice on that network.** Both sides: `net.line.max_i_ka` implying a uniform 9900 MVA and
`net.trafo.sn_mva` = 9900 (pandapower's `case118`), versus the manuscript's framing at line
92 and line 262 which presents the exclusion as a scoping decision.

**C2-3 — over-voltage is case118-specific.** case118 73.1% of N-1 rows above 1.05; case30
**0.00%**. Any general statement about the sampler suppressing or not suppressing
over-voltage is network-specific.

### NO SOURCE / CANNOT BE COMPUTED

- **Full case30 thermal sweep — NOT RUN.** ~87 minutes projected. The artifact records a
  120-scenario prefix sample and says so. Authorisation needed for the full sweep.
- **Rejection rate by outage status — CANNOT BE COMPUTED.** Rejected draws are not recorded
  in `data/dataset.parquet`.
- **Thermal/voltage violation-set overlap (P2A-4) — CANNOT BE COMPUTED.** UNDEFINED on
  case118; degenerate on case30.
- **Whether case118's 9900 MVA is a pandapower conversion artifact or an upstream MATPOWER
  value — NOT DETERMINED.** Not traced beyond `pandapower.networks.case118`.
- **Environment at dataset generation time — UNKNOWN**, recorded as such in the new
  `data/dataset.manifest.json` under `provenance_class.unknown` (5 items).

### What I did not do, and why

- **No git write.** Three new artifacts, three new scripts, all uncommitted.
- **No prose, and no edits to the manuscript or to notes to resolve C1-7, C1-10 or C1-11** —
  logged as author decisions per instruction.
- **Did not run the full case30 thermal sweep** — exceeds the compute threshold.
- **Did not run a loading sweep on case118** — a sweep against a placeholder rating measures
  nothing and would report a misleading zero.
- **Did not edit `data/bus_convention_map.json`** (Stage 1 deviation still standing).

### Next stage preconditions

| Precondition for 2C–2F | Status |
|---|---|
| 2A artifact + manifest | **MET** — `data/thermal_check.json` |
| 2B artifact + manifest | **MET** — `data/sampling_audit.json` |
| `data/dataset.parquet` manifest | **MET** — emitted, retroactive and labelled as such |
| Pre-registration recorded before the run | **MET** — `notes/preregistration.md`, 03:52Z |
| Verifier subagent on Stage 2 | **NOT MET** |
| Tree committed | **NOT MET** |

---

## STAGE 2H — case30 thermal-feasible regeneration

**Started:** 2026-08-19T03:53:36Z   **Ended:** 2026-08-19T05:12:00Z
**Wall-clock work:** ~1.3 hours against a 5-working-day cap. **Cap not approached.**
**Git HEAD:** `60822046633e729db4bdcce0bb539163fe7fb4a4`
**Tree dirty at end:** YES — new scripts and `data/case30_thermal/`. Nothing committed.

### H0 — pre-registration

Written to `notes/preregistration.md` at **2026-08-19T03:53:36Z**, before any H1-H5 code ran,
with the decision rule copied verbatim. Eight predictions P2H-1..P2H-8, each with a
confidence label. Already-known case30 figures are marked ALREADY OBSERVED and excluded from
scoring. The pre-registration records, in advance, that I expected the **DEGENERATE** branch
to fire.

### H1 — the N-0 criterion

**Committed predicate, `feasibility/generate_dataset.py:256`:**

```python
if GATE_N0 and (not n0_conv or n0_min_vm < VMIN_LIMIT):
    n_reject += 1
    continue
```

i.e. **accept iff `n0_conv` AND `n0_min_vm >= 0.94`**. `VMIN_LIMIT = 0.94` at line 8.
Voltage only. The verifier independently confirmed that no `loading_percent`, `max_i_ka` or
`sn_mva` quantity is read anywhere in the acceptance path, and that `LOADING_CAP = 1.60`
(line 12) is an aggregate demand-multiplier cap applied during sampling, not a branch rating.

**Extended predicate:** accept iff `n0_conv` AND `n0_min_vm >= 0.94` AND
`max(line, trafo) loading_percent <= 100`.

**Placeholder guard.** `assert_ratings_usable()` RAISES rather than silently passing. Live
behaviour:

- `case118` → **RAISED**: "line ratings look like PLACEHOLDERS (2 distinct values, base-case
  max loading 4.475%). A thermal N-0 predicate against a placeholder accepts everything and
  reports a misleading zero. Refusing to run."
- `case30` → **USABLE**: 41 lines, 6 distinct ratings, base-case max loading 111.83%.

The extended predicate is applied to case30 only. case118 is refused by code, not by
convention.

**Implementation note.** `generate_dataset.py` was NOT edited. Sampling and row construction
are imported from it unchanged; only the accept/reject predicate lives in the new script. The
mirrored contingency loop (needed to capture per-contingency loading) is checked against the
committed `run_scenario` on 5 scenarios — **all match, empty diffs** — and that check is
stored in the artifact.

### H2 — the surviving loading range

Sweep of `lo` from 1.00 downward in 0.01 steps, window 0.12, 200 draws per candidate,
6 bases per candidate for the N-1 probe. Full table in
`data/case30_thermal/h2_range_sweep.json`.

| lo | hi | acceptance | max base load % | min base vm | probe violation rate |
|---|---|---|---|---|---|
| 1.00 | 1.12 | **0.000** | — | — | — |
| 0.99 | 1.11 | **0.000** | — | — | — |
| 0.98 | 1.10 | **0.000** | — | — | — |
| 0.97 | 1.09 | **0.000** | — | — | — |
| 0.96 | 1.08 | **0.000** | — | — | — |
| 0.95 | 1.07 | **0.000** | — | — | — |
| 0.94 | 1.06 | **0.000** | — | — | — |
| 0.93 | 1.05 | 0.010 | 99.66 | 0.95560 | 0.1585 |
| 0.92 | 1.04 | 0.020 | 99.40 | 0.94530 | 0.2256 |
| 0.91 | 1.03 | 0.030 | 99.50 | 0.94590 | 0.2033 |
| 0.90 | 1.02 | 0.060 | 99.77 | 0.94626 | 0.1341 |
| 0.89 | 1.01 | 0.115 | 99.89 | 0.94394 | 0.1423 |
| 0.88 | 1.00 | 0.165 | 99.92 | 0.94607 | 0.1463 |
| **0.87** | **0.99** | **0.205** | **99.79** | **0.94541** | **0.1423** |
| 0.86 | 0.98 | 0.230 | 99.72 | 0.94265 | 0.1301 |
| 0.85 | 0.97 | 0.320 | 99.94 | 0.94072 | 0.1260 |
| 0.84 | 0.96 | 0.370 | 100.00 | 0.94311 | 0.1260 |
| 0.83 | 0.95 | 0.400 | 99.98 | 0.94015 | 0.1545 |
| 0.82 | 0.94 | 0.435 | 99.84 | 0.94708 | 0.0854 |
| 0.81 | 0.93 | 0.570 | 99.99 | 0.94183 | 0.1260 |
| 0.80 | 0.92 | 0.555 | 99.72 | 0.94279 | 0.1220 |
| 0.79 | 0.91 | 0.600 | 99.71 | 0.94623 | 0.1220 |
| 0.78 | 0.90 | 0.615 | 99.93 | 0.94374 | 0.1179 |
| 0.77 | 0.89 | 0.700 | 99.74 | 0.94244 | 0.0691 |
| 0.76 | 0.88 | 0.715 | 99.93 | 0.94533 | 0.0650 |
| 0.75 | 0.87 | 0.815 | 99.96 | 0.94039 | 0.0650 |
| 0.74 | 0.86 | 0.820 | 99.96 | 0.94031 | 0.1098 |
| 0.73 | 0.85 | 0.885 | 99.59 | 0.94049 | 0.1057 |
| 0.72 | 0.84 | 0.885 | 99.30 | 0.94088 | 0.0935 |
| 0.71 | 0.83 | 0.845 | 99.73 | 0.94070 | 0.2195 |
| 0.70 | 0.82 | 0.855 | 99.17 | 0.94072 | 0.1992 |

**No thermally feasible base case exists anywhere at or above `lo` = 0.94.** The published
dataset's range, [1.00, 1.12], has acceptance **exactly zero** under the corrected criterion:
every base case in `data/case30_dataset.parquet` is thermally infeasible.

**Selected range: [0.87, 0.99]** — the highest `lo` with acceptance >= 0.20 and max base
loading <= 100. Selected by the rule stated before the sweep ran, not by hand.

**A bug found and fixed mid-H2, recorded because it changed reported numbers.** The first
sweep produced impossible violation rates of exactly 1.0 at three `lo` values next to
neighbours at 0.12. Cause: `run_scenario` toggles `in_service` and re-solves the CURRENT net
state (`generate_dataset.py:210-216`); it does not re-apply params. The committed `worker()`
calls it immediately after `solve_n0` so the net is correct there, but the probe deferred it
until after the draw loop, when the net held the LAST DRAWN — usually rejected — scenario.
Fixed by re-applying before each probe. The acceptance, loading and voltage columns were
computed inside the loop and were never affected; only the violation column was. The table
above is post-fix.

### H3 — regenerate, retrain, recalibrate, re-gate

Protocol constants are asserted equal to `scripts/case30_gate.py` at runtime and the run
aborts on drift: 5 seeds, limit 0.94, strip [0.94, 0.945), coverage grid 0.90..0.98, same
ridge/histgb candidate sets, same inner-split M2 selection, same population-std convention.
Only the input dataset and output paths differ.

| | value |
|---|---|
| accepted / drawn | **1500 / 8050** = 0.186335 |
| rejections | thermal 5710, voltage 840, non-convergence 0 |
| dataset rows | 63,000 (1500 x 42; 61,500 N-1, all converged) |
| equivalence vs committed `run_scenario` | **all 5 match, empty diffs** |
| max base loading | 100.00% |
| build time | 1269 s |
| gate time | 2224 s |

**Leakage guard:** per-contingency loading is written to a SEPARATE
`data/case30_thermal/n1_loading.parquet`. `make_splits.load_dataset` treats every numeric
column outside `EXCLUDE_COLS` as a feature, so loading in the same parquet would have fed a
post-outage outcome to the surrogate. The gate additionally asserts no `max_*load*` column
reached the feature list.

### H4 — three-way comparison

| quantity | case30 as published | case30 thermal-feasible | case118 |
|---|---|---|---|
| violation rate % | 28.8081 | **15.3967** | 17.4800 |
| boundary mass % | 20.0146 | **7.0862** | 56.8600 |
| **ridge @ 0.90** | | | |
| escalation % | 27.87 | **11.92** | 49.07 |
| empirical coverage % | 89.87 | 90.34 | 89.34 |
| missed violations % | 1.493 | **6.087** | 2.963 |
| net speedup x | 3.66 | **8.45** | 2.04 |
| **histgb @ 0.90** | | | |
| escalation % | 6.98 | **2.65** | 30.63 |
| empirical coverage % | 90.17 | 90.22 | 89.82 |
| missed violations % | 1.466 | **2.226** | 4.717 |
| net speedup x | 14.52 | **38.63** | 3.29 |
| **first target with mean missed < 1%** | | | |
| ridge | 0.92: 34.48% esc, 2.98x | **0.98: 37.83% esc, 2.65x** | 0.94: 64.3% esc, 1.56x |
| histgb | 0.93: 8.96% esc, 11.27x | **0.96: 4.86% esc, 21.46x** | 0.97: 63.7% esc, 1.58x |
| **max N-1 loading_percent** | share>100% = **1.000000**, median 154.72, max 490.45 (SAMPLE 120/1500) | share>100% = **0.214846**, median 97.66, max 145.80 (FULL 61,500) | **UNDEFINED** (uniform 9,900 MVA placeholders) |

### Which branch of the decision rule fired

Quoting the rule as committed at H0:

> - If the corrected network produces a converged, calibrated gate with a non-degenerate
>   violation rate (0.5% <= violation rate <= 40%), it REPLACES the current case30
>   figures in the manuscript.

**The NON-DEGENERATE branch fires.** All three conditions are met:

| condition | threshold | measured | verdict |
|---|---|---|---|
| violation rate in [0.5%, 40%] | — | **15.3967%** | PASS |
| N-0 acceptance rate >= 5% | 5% | **18.63%** | PASS |
| a thermal-feasible loading range exists | — | **[0.87, 0.99]** | PASS |
| gate converged and calibrated | coverage tracks target | max per-record deviation **0.016992** (guard tolerance 0.03) | PASS |

**So the corrected case30 result REPLACES the current case30 figures in the manuscript.**

This is the opposite of what H0 recorded that I expected. The pre-registration says, verbatim:
"Given P2H-3, I expect the **DEGENERATE** branch to fire, on violation rate below 0.5%."
It did not.

### Pre-registration comparison — every prediction, including the wrong ones

| # | Prediction | Outcome | Verdict |
|---|---|---|---|
| **P2H-1** | feasible `lo` in 0.86-0.90 | **0.87** | **CORRECT** |
| **P2H-2** | escalation FALLS below 8.96% (high confidence) | histgb crossing 8.96% -> **4.86%**; histgb @0.90 6.98% -> **2.65%** | **CORRECT** |
| **P2H-3** | violation rate under 5%, and further under 0.5% (moderate / low-to-moderate) | **15.3967%** | **WRONG, and wrong in the direction that decided the branch.** Flagged at H0 as "the prediction most likely to be wrong and the one that decides which branch fires". |
| **P2H-4** | boundary mass under 8% | 20.01% -> **7.0862%** | **CORRECT** |
| **P2H-5** | speedup rises above 11.27x | histgb crossing **21.46x**; @0.90 **38.63x** | **CORRECT** |
| **P2H-6** | coverage tracks target within 0.03 (high confidence) | max per-record deviation **0.016992**; seed-averaged **0.004260** | **CORRECT** |
| **P2H-7** | max N-1 loading still exceeds 100% on some contingencies | **21.48%** of 61,500 exceed 100%, max 145.80% | **CORRECT** |
| **P2H-8** | histgb keeps lower escalation and higher speedup; ridge keeps the lower missed rate | histgb esc 2.65% < ridge 11.92% and speedup 38.63x > 8.45x — correct. But **missed: histgb 2.226% < ridge 6.087%** | **HALF WRONG.** The model ordering on safety **reverses** relative to case118, where ridge has the lower missed rate at every target. |

**Why P2H-3 was wrong, stated because the mechanism matters more than the score.** I reasoned
that cutting load ~11% would lift the whole `min_vm` distribution away from 0.94 and collapse
the violation rate. It fell — 28.81% to 15.40% — but nowhere near to zero. The thermal gate
does not select *lightly loaded* base cases; it selects cases sitting just under 100% loading
(median base loading is at the cap, max 100.00%), which are also close to their voltage
limit. The corrected criterion trades one binding constraint for a state that is marginal on
both. That is why the network stays interesting rather than becoming degenerate.

### H5 — verification

**Two-key, every headline number.** Key 1 is the producing script's own pandas path; key 2 is
a raw `pyarrow` + `numpy` recompute that never touches pandas or the stored aggregates.

| quantity | key 1 | key 2 | verdict |
|---|---|---|---|
| violation rate | 15.3967% (stored, `round(x,4)`) | 15.396748% -> 15.3967 | MATCH at stored precision |
| boundary mass | 7.0862% (stored, `round(x,4)`) | 7.086179% -> 7.0862 | MATCH at stored precision |
| N-1 loading > 100% | 0.214845528 | 0.214845528 | MATCH |
| N-0 acceptance rate | 0.186335404 | 1500/8050 = 0.186335404 | MATCH |
| ridge crossing | target 0.98, 37.8341%, 2.6489x | re-derived from raw records: identical | MATCH |
| histgb crossing | target 0.96, 4.8618%, 21.4571x | re-derived from raw records: identical | MATCH |
| n1 rows | 61,500 | 61,500 | MATCH |

Method note: the first two initially read as MISMATCH because the artifact stores
`round(100*x, 4)` and the comparison used a 1e-9 tolerance against a rounded value. Recorded
so the correction is visible rather than silently tightened.


#### Verifier subagent — VERBATIM

Spawned with only artifact paths and claims; it had not seen H1-H4.

All ten claims recomputed independently. **10 MATCH, 0 MISMATCH, 0 NOT FOUND.**

**CLAIM 1 — MATCH.** Route: `pandas.read_parquet` on `/Users/rajansaha/contingency-screener-research/data/case30_thermal/dataset.parquet`, value_counts on `outaged_type`, `.all()` on `converged`, `nunique()` on `scenario_id`. Total 63000; `outaged_type` is `{'line': 61500, 'none': 1500}`; all 61500 N-1 rows converged (`converged` column is uniformly `True` across the whole file); 1500 distinct `scenario_id` overall and within N-1. (63000 = 1500 × 42 = 41 lines + 1 base row per scenario.)

**CLAIM 2 — MATCH.** Route: boolean masks over the 61500 N-1 converged rows. violation rate `15.3967%`, boundary mass `[0.94, 0.945)` `7.0862%`. Both agree at 4 dp with the values stored in `case30_thermal_frozen.json` (`violation_rate_pct: 15.3967`, `boundary_mass_pct: 7.0862`).

**CLAIM 3 — MATCH.** Route: `read_parquet` on `data/case30_thermal/n1_loading.parquet` (61500 rows, all converged). Share `max_loading_pct > 100` = `0.21484552845528454` (claimed 0.214845528, agrees to all stated digits); median `97.66` (97.65510699); max `145.80` (145.79724799).

**CLAIM 4 — MATCH.** Route: `cat data/case30_thermal/h3_build_stats.json`. `n_accepted: 1500`, `n_draws: 8050`, `acceptance_rate: 0.18633540372670807` (= 1500/8050, verified), `equivalence_all_match: true` with 5 blocks of 42 rows each, all `match: true`, empty `diffs`. Rejections split `voltage: 840`, `thermal: 5710`, `nonconvergence: 0` (840 + 5710 + 1500 = 8050, consistent).

**CLAIM 5 — MATCH.** Route: re-aggregated the 90 raw per-seed `records` (2 families × 9 coverage levels × 5 seeds) rather than reading the stored summary, then cross-checked against the stored block. At target 0.90 — ridge escalation mean 0.1191869919 → `11.92%`, net speedup mean `8.4493` → `8.45`; histgb escalation mean 0.0265365854 → `2.65%`, net speedup `38.6263` → `38.63`. My re-aggregation reproduces the stored `four_metrics_at_90pct_coverage` exactly.

**CLAIM 6 — MATCH.** Route: same re-aggregation, walking coverage targets in ascending order for the first mean `missed_viol < 0.01`. Ridge: 0.90–0.97 stay at or above 1% (0.97 is 1.0475%), first crossing at **0.98** — missed 0.5145%, escalation `37.8341%` → 37.83%, speedup `2.6489` → 2.65×. Histgb: 0.95 is 1.1874%, first crossing at **0.96** — missed 0.9094%, escalation `4.8618%` → 4.86%, speedup `21.4571` → 21.46×. Matches the stored `crossings_first_below_1pct_missed`.

**CLAIM 7 — MATCH.** Route: max deviation computed both ways. Per-record (all 90 records): max `|coverage_emp - coverage_target| = 0.016991869918699165`, which is ≤ 0.0170. At the seed-averaged level the max deviation is much tighter, `0.004260`. The claim holds on the stricter per-record reading.

**CLAIM 8 — MATCH.** Route: `json.load` on `data/case30_frozen.json`, plus recomputation of the crossing from its own records where present. `violation_rate_pct: 28.8081`, `boundary_mass_pct: 20.0146`. Histgb crossing: `coverage_target 0.93`, escalation `0.08959349593495934` → 8.959%, speedup `11.265301491886408` → 11.265×. (Note: this file stores summary blocks only — no `records` array — so the crossing was read from `crossings_first_below_1pct_missed` rather than re-derived.) For context, ridge's crossing there is 0.92.

**CLAIM 9 — MATCH.** File `/Users/rajansaha/contingency-screener-research/feasibility/generate_dataset.py`, **line 256**, exact predicate:

```python
if GATE_N0 and (not n0_conv or n0_min_vm < VMIN_LIMIT):
```

`VMIN_LIMIT = 0.94` (line 8). `n0_min_vm` comes from `solve_n0` as `float(np.nanmin(vm0))` (line 184) — a bus-voltage minimum only. The predicate consults exactly two things: N-0 convergence and N-0 minimum voltage. A grep for `loading|thermal|max_i_ka|sn_mva|rate` in this file turns up only `LOADING_CAP = 1.60` (line 12), which is an **aggregate demand-multiplier cap** applied inside `sample_scenario` (lines 117–118: `agg = (net["_p0"] * mp).sum() / net["_base_p_total"]`, rescaled if `agg > LOADING_CAP`). That is a total-load scaling ratio, not a branch loading or thermal rating, and it acts during sampling before the acceptance test. No branch `loading_percent`, `max_i_ka`, or `sn_mva` quantity is read anywhere in the acceptance path.

**CLAIM 10 — MATCH.** Route: instantiated the networks with `.venv/bin/python` and pandapower directly. `case30` line `max_i_ka` has **6** distinct values: `[0.0684267, 0.1368534, 0.27798346, 0.29936681, 0.38490018, 0.55596693]`. `case118` line `max_i_ka` has **2** distinct values: `[16.56744251, 41.41860627]`. All 13 `case118` trafo `sn_mva` equal `9900.0`. (Incidental: `case30` has no transformers at all, so its branch set is lines only.)

Verification scripts are in `/private/tmp/claude-501/-Users-rajansaha-contingency-screener-research/a20165b8-6ffa-4031-84e5-ca5fd47a15f6/scratchpad/` (`v1.py`, `v3.py`, `v5b.py`); nothing in the repo was written or modified.

One observation worth passing on, not a mismatch: Claim 7 is only true on the per-record reading with essentially no margin (0.016992 against a stated bound of 0.0170). If that number gets reported, the seed-averaged figure (0.0043) is the more stable one to quote, and whichever is used should say explicitly whether it is per-record or per-seed-mean.
### Contradictions found

**C2H-1 — every base case in the published case30 dataset is thermally infeasible.** At the
published range [1.00, 1.12] the corrected criterion accepts **0 of 200** draws at each of
seven consecutive `lo` values from 1.00 down to 0.94. This is stronger than the Stage 2A
finding (which showed the N-0 *nominal* case at 111.83%): it shows no draw in the published
sampling window can satisfy the thermal criterion at all.

**C2H-2 — the model-safety ordering reverses between networks.** On case118 ridge has the
lower missed rate at every coverage target. On the thermal-feasible case30, histgb has the
lower missed rate at 0.90 (2.226% vs 6.087%) AND crosses 1% earlier (0.96 vs 0.98). Any
statement that the linear model is the safer one is case118-specific.

**C2H-3 — the corrected result strengthens rather than weakens the two-network argument.**
Boundary mass 56.86% (case118) vs **7.09%** (corrected case30) is a **8.0x** spread, wider
than the 2.8x against the published 20.01%. The escalation contrast at the sub-1% operating
point widens correspondingly: 63.7% vs **4.86%**.

### NO SOURCE / CANNOT BE COMPUTED

- **Whether [0.87, 0.99] is operationally meaningful for a real 30-bus system — NOT
  DETERMINED.** It is the range the stated selection rule picks; whether a utility would
  operate a network at 87-99% of its test-case nominal load is outside this repository.
- **case118 thermal — remains UNDEFINED.** Unchanged from Stage 2A; the guard refuses it.
- **Whether the published case30 figures were ever intended as thermally feasible — NO
  SOURCE.** Nothing in the repo states an intent either way.

### What I did not do, and why

- **No git write.** New scripts and `data/case30_thermal/` are uncommitted.
- **No prose, no `.tex` edit, no edit to notes to resolve C1-7/C1-10/C1-11.**
- **Did not edit `feasibility/generate_dataset.py`** — the committed generator that produced
  the frozen case118 artifacts is untouched.
- **Did not apply the thermal predicate to case118** — refused by the guard, by design.
- **Did not re-run the published case30 pipeline** — its figures are read from the committed
  `data/case30_frozen.json`.

### Hard cap

~1.3 hours of wall-clock work against a 5-working-day cap. **The cap was not approached and
no abandon decision was needed.** A converged, calibrated gate was produced.

---

## STAGE 2C-2G — drift tests, Q-limit class, and the deferred verifier pass

**Started:** 2026-08-19T05:15:00Z   **Ended:** 2026-08-19T06:05:00Z
**Git HEAD:** `60822046633e729db4bdcce0bb539163fe7fb4a4`   **Tree dirty:** YES, uncommitted.
**Scope:** case118 only for 2C/2D/2E, per the standing amendment.

### Shared design

The surrogate is fit once per (seed, family) on the STANDARD train split using the stored M2
config from `data/tuned_metrics.json` — no re-search, so the model is identical to the one
behind every published number. Only the CALIBRATION and TEST populations change, which
isolates distribution shift from model difference.

**Every shifted cell is paired with a same-stratum control.** Calibrating on A and evaluating
on B says nothing alone — B may simply be harder. The control separates "the shift broke the
guarantee" from "this stratum is harder". Without it the experiment is uninterpretable.

---

### 2C — n0_min_vm stratum drift → `data/drift_n0_stratum_long.parquet`

Median split of the 1,500 base scenarios at `n0_min_vm` = **0.943358**. 1,200 rows
(2 models x 4 cells x 30 targets x 5 seeds).

**Mean coverage shortfall (target − empirical), averaged over all 30 targets:**

| model | calibrate | evaluate | shortfall | |
|---|---|---|---|---|
| ridge | benign | benign | **0.008282** | control |
| ridge | benign | **marginal** | **0.164335** | **shifted — 20x the control** |
| ridge | marginal | benign | −0.068568 | shifted (over-covers) |
| ridge | marginal | marginal | 0.010189 | control |
| histgb | benign | benign | 0.008910 | control |
| histgb | benign | marginal | 0.017613 | shifted |
| histgb | marginal | benign | −0.011827 | shifted |
| histgb | marginal | marginal | −0.007760 | control |

**At the 0.90 target specifically:**

| model | cal → test | empirical coverage | escalation | missed |
|---|---|---|---|---|
| ridge | benign → benign (control) | 0.8964 | 0.3318 | 0.0528 |
| ridge | **benign → marginal** | **0.7953** | 0.4340 | 0.0501 |
| histgb | benign → benign (control) | 0.8931 | 0.0285 | 0.0825 |
| histgb | benign → marginal | 0.8960 | 0.5371 | 0.0246 |

**The finding.** Calibrating on benign base cases and screening marginal ones costs **ridge**
about **10.5 coverage points** at the 0.90 target (0.8964 → 0.7953), and 16.4 points averaged
over the sweep against a control of 0.8 points. **histgb is essentially unaffected** (0.0176
vs a 0.0089 control). The conformal guarantee fails inside the boundary layer for the linear
model and holds for the gradient-boosted one.

This lands directly on the floor argument: the floor lives in the boundary layer, and that is
exactly where ridge's calibration stops transferring.

**Realized shift:** the difference in mean `n0_min_vm` between strata is only
**0.004844–0.004865 pu**. A shift that small breaking coverage by 10 points is the result.

**Circulating values NOT reproduced.** Values of 87.7 / 87.1 / 92.4 / 92.1 and a 0.0159 pu
strata gap have circulated in planning documents for this experiment. Measured here: ridge
coverages **79.53 / 88.44 / 90.22 / 89.64** and a realized gap of **0.00486 pu**. Neither the
coverages nor the gap match. The circulating figures remain **unverified and are not
reproduced by this run**; no artifact for them was ever located.

---

### 2D — element-type drift → `data/drift_element_type_long.parquet`

Calibrate on the 173 line outages, evaluate on the 13 transformer outages, and the reverse.
1,200 rows. Transformer rows are 3,890 of 55,790 test rows (~7%).

| model | calibrate | evaluate | shortfall (all targets) | |
|---|---|---|---|---|
| histgb | line | line | −0.001425 | control |
| histgb | **line** | **trafo** | **0.022810** | shifted |
| histgb | trafo | line | −0.022445 | shifted |
| histgb | trafo | trafo | 0.001512 | control |
| ridge | line | line | 0.005931 | control |
| ridge | line | trafo | 0.003776 | shifted |
| ridge | trafo | line | 0.007160 | shifted |
| ridge | trafo | trafo | 0.005035 | control |

**The finding, and it is the mirror image of 2C.** Element-type shift moves **histgb** by
~2.3 coverage points against a control of ~0.1, while **ridge is immune** (0.0038 shifted vs
0.0059 control — the shifted cell is *better* than its own control).

**So the two models fail under different shifts.** ridge breaks on the voltage-stratum shift
and holds on element type; histgb breaks on element type and holds on the voltage stratum.
Neither is uniformly robust.

**Does this bound N-2 expectations? NO, and the artifact says so.** Calibrating on lines and
testing on transformers changes the EVENT SPACE, not the weighting of one space. No
likelihood ratio exists between the two populations, so weighted conformal cannot correct it
— structurally the same failure as N-1 → N-2. It is a proxy for the *kind* of failure, not a
bound on its *size*.

**Non-convergence interaction:** all 45 solver non-convergences are transformer outages
(Stage 0/2B). They are dropped by `load_dataset`, so the transformer-side evaluation is
conditioned on convergence in a way the line side is not. With 45 rows against 3,890 the
effect is small, but the conditioning is asymmetric and is recorded rather than assumed away.

---

### 2E — loading soft tilt → `data/drift_loading_tilt_long.parquet`

**No median split.** An exponential tilt `w(a) ∝ exp(λ·normalised agg_loading)`, λ = 3.0,
which keeps the supports identical and the density ratio finite everywhere.

**Ratio finiteness and ESS confirmed BEFORE any coverage number was computed:**

| seed | ratio finite | ESS fraction | w_cal range | agg_loading range |
|---|---|---|---|---|
| 0 | True | 0.8220 | 0.2763 – 5.5492 | 1.0194 – 1.0959 |
| 1 | True | 0.8011 | 0.2215 – 4.4494 | 1.0189 – 1.0962 |
| 2 | True | 0.7903 | 0.1606 – 3.2251 | 1.0232 – 1.0951 |
| 3 | True | 0.7894 | 0.1995 – 4.0067 | 1.0289 – 1.0951 |
| 4 | True | 0.8104 | 0.2296 – 4.6126 | 1.0218 – 1.0927 |

ESS never falls below 0.79 against a 0.10 floor, so the tilt is **not degenerate** and the
run proceeded.

| model | cell | shortfall (all targets) |
|---|---|---|
| ridge | untilted test, unweighted cal (control) | 0.005857 |
| ridge | tilted test, unweighted cal | 0.004624 |
| ridge | tilted test, **weighted** cal | 0.003816 |
| histgb | untilted test, unweighted cal (control) | −0.001210 |
| histgb | tilted test, unweighted cal | 0.000624 |
| histgb | tilted test, **weighted** cal | −0.002061 |

**The finding is a null, and the reason is the sampler, not the method.** The realized shift
in mean `agg_loading` is only **+0.0046 to +0.0054** (untilted ~1.0590 → tilted ~1.0641),
because the sampler's own loading window spans just **1.019 to 1.096** — 7.7 points wide.
A λ = 3 tilt on a window that narrow cannot move the distribution far enough to break
coverage. Weighted conformal gives a small consistent improvement (ridge 0.00462 → 0.00382;
histgb's weighted cell over-covers) but there is almost no degradation to correct.

**This experiment is under-powered by construction and should be reported as such.** It does
NOT show weighted conformal is unnecessary; it shows this dataset cannot generate a loading
shift large enough to test it.

**Reporting defect, recorded.** `realized_mean_agg_test` was written as the tilted mean for
all three cells including the untilted control, so that column mislabels the control row. The
coverage, escalation and missed values are unaffected. Correct per-seed values are in the
Contradictions section below.

---

### 2F — Q-limit failure class → `data/qlimit_class.json`

"Deep" = a missed violation whose depth (0.94 − y) exceeds one band width `q_hat`, at the
recommended operating points.

**The pre-outage signature test.** A generator that has hit its reactive limit is no longer
holding its setpoint, so its bus voltage departs from `genvm`. Both quantities are already in
the committed feature block: `genvm_g` is the commanded setpoint, `vm0_[bus(g)]` the solved
pre-outage voltage. So "generator g is at a reactive limit pre-outage" is computable as
`|vm0_[bus(g)] − genvm_g| > 1e-4` **from features the surrogate already sees**.

| | ridge @ 0.94 | histgb @ 0.97 |
|---|---|---|
| total missed (5 seeds) | 384 | 404 |
| deep misses | **58** (15.1%) | **106** (26.2%) |
| distinct outaged elements | **32** | **54** |
| top element share | 0.0862 | 0.0472 |
| distinct argmin buses | **25** | **31** |
| top bus share | 0.1034 (IEEE 106) | 0.1509 (IEEE 104) |
| max depth | **0.032426** | **0.091457** |

**Off-setpoint generators — the discriminator that isn't:**

| population | mean off-setpoint gens | share with any |
|---|---|---|
| all 278,955 converged N-1 rows (baseline) | **20.799** | **1.000000** |
| ridge deep misses | 21.328 | 1.000000 |
| histgb deep misses | 21.453 | 1.000000 |

**VERDICT: NOT HOMOGENEOUS.** Deep misses spread across 32 and 54 distinct outaged elements
with no element above 9% and no argmin bus above 16%. And the reactive-limit signature does
not discriminate at all: **every** N-1 row in the dataset already has at least one
off-setpoint generator, with a mean of 20.8 of 54, against 21.3–21.5 in the deep-miss rows.
Being near a Q-limited generator is the normal state of this network, not a marker for
collapse.

Per the plan's own rule, "not homogeneous" is a valid, cheap and complete answer. It is worth
roughly zero as a predictive lead and it was obtained in one run.

**The collision, reported and NOT resolved.** The manuscript states at line 262 that "a model
trained only on pre-outage features cannot predict such a situation." The `physics` agent
argued this is unsupported because the reactive limits are in the design matrix. **2F does not
refute the manuscript's claim.** No pre-outage signature that discriminates deep misses was
found: the candidate signature is present in ~100% of all rows. So the information-theoretic
objection is not established by this evidence, and the manuscript's sentence survives this
test — though for a different reason than it gives. Which claim to keep is the author's
decision; both readings are recorded.

**Max miss depth at the operating points** — two-key against `data/missed_depth.json`:
ridge @ 0.94 **0.032426** and histgb @ 0.97 **0.091457**, identical to the values that file
already stores. The 0.0915 pu collapse survives into histgb's recommended sub-1% point.

---

### 2G — stage close and the deferred verifier pass

The Stage 2 block recorded "No verifier subagent was run for Stage 2" as a gap. That gap is
now closed. A `verifier` subagent, given only artifact paths and 11 claims and having seen
none of the producing work, recomputed 2A and 2B independently.

#### verifier-2ab — VERBATIM

All 11 claims recomputed independently. **Every claim: MATCH.**

**CLAIM 1 — MATCH.** Route: fresh `pn.case118()`, computed `sqrt(3)*vn_kv[from_bus]*max_i_ka` per line, then `pp.runpp(enforce_q_lims=True, init="dc", numba=True, algorithm="nr")`. 173 lines, only 2 distinct `max_i_ka` values, all implying 9900 MVA (to float noise: max 9900.000000000002). All 13 `trafo.sn_mva` = 9900. Base-case max line loading 4.475, max trafo loading 3.589.

**CLAIM 2 — MATCH.** Same route on `case30`: 41 lines, 6 distinct `max_i_ka`, implied MVA {16, 32, 65, 70, 90, 130} (min 16, max 130), `len(net.trafo)==0`, base-case max line loading 111.831.

**CLAIM 3 — MATCH.** Route: pandas on `data/dataset.parquet`, filtered `converged==True`, split `outaged_type=='none'` vs not (the other values are `line`/`trafo`). Shares >1.05: 0.734000 / 0.731358; max: 1.12220 / 1.15291; median: 1.05435 / 1.05425.

**CLAIM 4 — MATCH.** Same route on `data/case30_dataset.parquet` (1500 N-0, 61500 converged N-1): shares 0.000000 / 0.000000; max 1.02498 / 1.02635.

**CLAIM 5 — MATCH.** Route: `grep -n` + `awk` on exact line numbers. Line 25 `DVM = 0.03`, line 28 `P_GEN_OUT = 0.30`, line 128 `if rng.random() < P_GEN_OUT:`, line 129 `candidates = [i for i in range(ngen) if not net.gen.iloc[i]["slack"]]` — pool is non-slack generators.

**CLAIM 6 — MATCH.** 1500 base rows, 374 with `gen_out>=0` (0.249333); 278955 converged N-1 rows, 69532 with `gen_out>=0` (0.249259).

**CLAIM 7 — MATCH.** Converged N-1, split on `gen_out>=0`: violation 0.182362 vs 0.172230 (+1.0132 pp); strip `(min_vm>=0.94)&(min_vm<0.945)` 0.580956 vs 0.564537 (+1.6419 pp); mean `min_vm` 0.939471 vs 0.939944.

**CLAIM 8 — MATCH.** Base rows, mean `n0_min_vm`: 0.943813 (with gen outage) vs 0.944104 (without).

**CLAIM 9 — MATCH.** Route: `ast.parse`, walked the `apply_scenario` FunctionDef, collected every Assign/AugAssign/AnnAssign whose target's root Name is `net`. Exactly 7 hits, at lines 137-144: `net.load['p_mw']`, `net.load['q_mvar']`, `net.gen['vm_pu']`, `net.gen['min_q_mvar']`, `net.gen['max_q_mvar']`, `net.gen['in_service']` (=True), and `net.gen.iat[params['gen_out'], ...get_loc('in_service')]` (=False). No assignment matching gen + `p_mw`. Also scanned for method calls on `net` inside the function — the only one is the read-only `net.gen.columns.get_loc('in_service')` inside the `.iat` target, so no hidden mutation route.

**CLAIM 10 — MATCH.** 53 `genp_*` columns; over base rows, max `nunique()` across them is 1 and max `std()` is 0.0.

**CLAIM 11 — MATCH.** `agg_loading` over base rows: min 1.014225, max 1.123857. Max |genvm_i − case118 base `gen.vm_pu`[i]| for i in {0,1,2}: 0.024946, 0.024954, 0.024995 → overall 0.024995 ≤ 0.024995. Consistent with `--dvm 0.025` (README.md line 95), not `DVM = 0.03`. Supporting detail beyond the claim: across all 53 generators the max deviation is exactly 0.025000, which pins the bound tighter than the 3-generator subset does.

Files used (all read-only; scratch scripts written only under the session scratchpad): `/Users/rajansaha/contingency-screener-research/data/dataset.parquet`, `/Users/rajansaha/contingency-screener-research/data/case30_dataset.parquet`, `/Users/rajansaha/contingency-screener-research/feasibility/generate_dataset.py`, `/Users/rajansaha/contingency-screener-research/README.md`.
### Contradictions found

**C2C-1 — circulating 2C values are not reproduced.** Planning documents carry 87.7 / 87.1 /
92.4 / 92.1 and a 0.0159 pu strata gap. Measured: ridge coverages 79.53 / 88.44 / 90.22 /
89.64, realized gap 0.00486 pu. Both sides recorded; no artifact for the circulating figures
exists. Not resolved.

**C2D-1 — model robustness ordering is shift-dependent.** ridge breaks under the voltage-stratum
shift (2C: 0.1643 vs 0.0083 control) and is immune to element-type shift (2D: 0.0038 vs
0.0059). histgb is the reverse (2C: 0.0176 vs 0.0089; 2D: 0.0228 vs −0.0014). Any statement
that one model is "more robust" needs the shift named.

**C2E-1 — the 2E control row carries a mislabelled `realized_mean_agg_test`.** All three cells
were written with the tilted mean. Correct per-seed untilted means: 1.059097, 1.058946,
1.058411, 1.059368, 1.059807; tilted: 1.063707, 1.064138, 1.063808, 1.064081, 1.064363.
Coverage and escalation values are unaffected.

**C2F-1 — 2F does not support the `physics` agent's objection.** The agent argued the
manuscript's "cannot predict" claim is unsupported because reactive limits are in the feature
set. 2F finds the candidate signature present in 100% of rows and therefore non-discriminating.
Both positions recorded; not resolved.

### NO SOURCE / CANNOT BE COMPUTED

- **Circulating 2C values (87.7/87.1/92.4/92.1, 0.0159 pu) — NO SOURCE.** Searched; no
  artifact produces them. Not reproduced by this run.
- **A loading shift large enough to stress weighted conformal — CANNOT BE PRODUCED from this
  dataset.** The sampler's `agg_loading` window is 7.7 points wide.
- **Whether 2D bounds N-2 expectations — CANNOT BE COMPUTED.** The event space changes, so no
  likelihood ratio exists. 2D is a proxy for the kind of failure, not its size.
- **Rejection rate by outage status — CANNOT BE COMPUTED** (unchanged from 2B).

### What I did not do, and why

- **No git write, no prose, no `.tex` edit.**
- **No edit to resolve C1-7, C1-10, C1-11** — author decisions, per instruction.
- **Did not re-search hyperparameters** — stored M2 configs reused so the models match the
  published ones exactly.
- **Did not run 2C/2D/2E on case30 or case30-thermal** — case118 only, per the amendment.

---

## STAGE 3 — notes/writing-numbers.md

**Started:** 2026-08-19T06:05:00Z   **Ended:** 2026-08-19T06:20:00Z
**Git HEAD at verification:** `69eeb80a34c9815194d6ead556ab26e86bfc249d`

### What ran

A single generator reading every artifact in this session and emitting one row per quantity
with source file, jsonpath/column, aggregation, and a 16-char content sha256. **80 rows.**

### Results

`notes/writing-numbers.md`, 250 lines. Structure:

- **Three result sets declared up front** — case118, case30-published, case30-thermal — with
  their N-0 criterion and thermal status. The file states that a row saying only "case30" is
  ambiguous and must not be used.
- 80-row provenance table covering: case118 dataset counts and rates; the sweep row count
  (16,800, recorded as a **row count, not a prose product**); flag precision and ceilings in
  both aggregations; both case30 sets side by side including crossings and @0.90 metrics; the
  H2 acceptance sweep and chosen range; 2C/2D/2E shortfalls; 2F counts and depths.
- **Amendment items, all included:** the full case30-thermal result set; the H2 acceptance
  sweep; the zero-acceptance finding (**lo 0.94 through 1.00, 7 consecutive values, acceptance
  exactly 0.000**); the `run_scenario` state-carryover bug with file:line; and the
  barrier-height question.
- CANNOT BE COMPUTED: 7 entries. NO SOURCE: 4 entries.
- Cross-artifact disagreements listed, with the M1/M2 pair resolved by `data/canonical.json`
  and the two case30 pairs marked **not a contradiction but two result sets**.

### The barrier-height question — REPORTED, NOT RESOLVED

On case118 the inequality holds: ridge (MAE 3.8e-3, `q_hat` 0.0052) misses less than histgb
(MAE 1.6e-3, `q_hat` 0.0023) at every target. On case30-thermal the ordering **reverses** —
histgb misses 2.226% vs ridge 6.087% at 0.90, and crosses 1% at 0.96 vs ridge's 0.98, while
ridge's `q_hat` is still ~3x taller (~0.0065–0.0077 vs ~0.0020–0.0027, from the H3b
calibration log).

Two readings are recorded, both consistent with the artifacts: (1) the inequality does not
predict the reversal and is contradicted on its face; (2) the inequality is not violated —
it bounds misses relative to a model's OWN overshoot distribution, and reading it as a
cross-model ordering may be the error, with ridge's overshoot tail growing faster than its
barrier on this set (its 2C behaviour already shows its calibration failing in the boundary
layer). **Deciding between them requires comparing each model's overshoot tail against its own
`q_hat` on case30-thermal — an experiment that was not run.** Author's decision.

### Verification

Every row carries source file, jsonpath/column, aggregation and content sha256, per §2d.
Rows were generated by reading artifacts directly, not by copying from earlier report blocks.
A verifier pass over Stage 3 has NOT been run — recorded as a gap.

### NO SOURCE / CANNOT BE COMPUTED

Enumerated inside `notes/writing-numbers.md` (7 and 4 entries respectively) rather than
duplicated here.

### What I did not do, and why

- **No git write, no prose, no `.tex` edit, no edit to resolve C1-7/C1-10/C1-11.**
- **Did not read** `notes/writing-background.md` or `notes/section-V-writing-context.md` —
  both absent from the repository.
- **Did not run a Stage 3 verifier pass** — recorded as a gap.
- **Did not resolve the barrier-height question** — reported both readings, per instruction.

---

## VERIFIER PASS — 2C, 2D, 2E and Stage 3

**Run:** 2026-08-19T14:00:00Z. Two `verifier` subagents, spawned in parallel, neither having
seen the producing work. Each was given artifact paths and claims only. Output below is
**VERBATIM and unsummarised**, per §2c.

Retrieval: each agent's final assistant text block was extracted from its own transcript
under `~/.claude/projects/.../subagents/`; no transcript was read into context wholesale.

---

### verifier-drift — 2C / 2D / 2E (13 claims) — VERBATIM

All claims recomputed from the artifacts with `.venv/bin/python` + pandas. Nothing was written to the repo.

**A1 — MATCH.** `pd.read_parquet` shape is `(1200, 20)`; all eleven named columns are present (full set: coverage_target, q_hat, escalation, coverage_emp, missed_viol, net_speedup, n_test, n_true_viol, n_escalated, n_certified, n_flagged, test, seed, model, cal_stratum, test_stratum, is_control, median_n0_min_vm, realized_shift_mean_n0_min_vm, n_cal). 1200 = 2 models × 4 cells × 30 targets (0.70–0.99) × 5 seeds.

**A2 — MATCH.** `.unique()` on `median_n0_min_vm` returns exactly one value, 0.943357525 → 0.943358 at 6 dp.

**A3 — MATCH.** Computed `short = coverage_target - coverage_emp`, then `groupby(["model","cal_stratum","test_stratum"])["short"].mean()`. All eight values reproduce to 6 dp exactly as stated (ridge b→m 0.164335, ridge m→b -0.068568, histgb m→m -0.007760, etc.).

**A4 — MATCH.** Filtered `coverage_target == 0.90`, group-mean of coverage_emp: ridge b→b 0.896393, ridge b→m 0.795298, histgb b→b 0.893121, histgb b→m 0.895989. Same filter/group on escalation and missed_viol for ridge benign→marginal: 0.433996 and 0.050105.

**A5 — MATCH.** Group-mean of `realized_shift_mean_n0_min_vm`: benign→marginal -0.004844, marginal→benign +0.004865 (magnitudes as claimed); controls benign→benign -0.000056 and marginal→marginal +0.000077, both |·| < 1e-4. `is_control` is True exactly on the two diagonal cells.

**B1 — MATCH.** Shape `(1200, 18)`.

**B2 — MATCH.** Same shortfall route as A3. All eight values reproduce to 6 dp, including histgb line→trafo 0.022810 and histgb trafo→line -0.022445.

**B3 — MATCH.** At `coverage_target == 0.90`, mean n_test = 51900.0 for both line test strata and 3890.0 for both trafo test strata; mean n_cal = 51900.0 for line calibration and 3893.4 for trafo calibration.

**C1 — MATCH.** Shape `(900, 20)`; `cell` has exactly the three values untilted_test_unweighted_cal, tilted_test_unweighted_cal, tilted_test_weighted_cal. 900 = 2 × 3 × 30 × 5.

**C2 — MATCH.** JSON top level: `tilt_lambda` 3.0, `ess_floor` 0.1. Per-seed `ess_fraction` = 0.8220457778, 0.8010768885, 0.7902919042, 0.7893723143, 0.8103907736 → 0.8220 / 0.8011 / 0.7903 / 0.7894 / 0.8104 at 4 dp. `ratio_finite` true for all five.

**C3 — MATCH.** `groupby(["model","cell"])["short"].mean()` reproduces all six values to 6 dp.

**C4 — MATCH.** agg_min values: 1.019406, 1.018908, 1.023224, 1.028886, 1.021798 (all ≥ 1.018). agg_max: 1.095880, 1.096228, 1.095060, 1.095060, 1.092663 (all ≤ 1.097). Widest seed-wise window 1.096228 − 1.018908 = 0.0773, under 8 pp.

**C5 — MATCH; the defect is real.** `groupby(["seed","cell"])["realized_mean_agg_test"].nunique()` is 1 for every seed/cell, and the value is identical across all three cells within a seed (1.063707, 1.064138, 1.063808, 1.064081, 1.064363 for seeds 0–4). Source confirms the cause at `/Users/rajansaha/contingency-screener-research/scripts/drift_tests.py:237`: `realized_mean_agg_test=float(agg[ti][pick].mean())` — it always applies the tilted bootstrap index `pick`, including on the untilted control row, whose actual test set is `agg[ti]` unindexed. The untilted control therefore reports the tilted test mean, so the column cannot serve as evidence that the tilt moved the loading distribution.

A companion defect in the same statement, not covered by your claims: `realized_mean_agg_cal=float(agg[ci].mean())` is likewise unweighted for all three cells, so the `tilted_test_weighted_cal` row reports the *unweighted* calibration mean and hides the effect of `w_cal` (verified: identical across cells within each seed — 1.058861, 1.059059, 1.059392, 1.059325, 1.058282).
---

### verifier-s3 — all 80 rows of notes/writing-numbers.md — VERBATIM

All 80 rows verified. Results:

```
ROW 1  | case118 total rows                          | value: MATCH | sha: MATCH
ROW 2  | case118 base scenarios                      | value: MATCH | sha: MATCH
ROW 3  | case118 N-1 attempted                       | value: MATCH | sha: MATCH
ROW 4  | case118 N-1 converged                       | value: MATCH | sha: MATCH
ROW 5  | case118 non-converged                       | value: MATCH | sha: MATCH
ROW 6  | case118 violation rate                      | value: MATCH | sha: MATCH
ROW 7  | case118 boundary mass                       | value: MATCH | sha: MATCH
ROW 8  | case118 N-1 share max_vm>1.05               | value: MATCH | sha: MATCH
ROW 9  | case118 N-0 share max_vm>1.05               | value: MATCH | sha: MATCH
ROW 10 | case118 gen-outage share of N-1             | value: MATCH | sha: MATCH
ROW 11 | sweep total evaluations                     | value: MATCH | sha: MATCH
ROW 12 | flag precision ridge@0.94 count-pooled      | value: MATCH | sha: MATCH
ROW 13 | flag precision ridge@0.94 seed-mean         | value: MATCH | sha: MATCH
ROW 14 | flag ceiling ridge                          | value: MATCH | sha: MATCH
ROW 15 | flag precision histgb@0.97 count-pooled     | value: MATCH | sha: MATCH
ROW 16 | flag precision histgb@0.97 seed-mean        | value: MATCH | sha: MATCH
ROW 17 | flag ceiling histgb                         | value: MATCH | sha: MATCH
ROW 18 | case30-published violation rate             | value: MATCH | sha: MATCH
ROW 19 | case30-published boundary mass              | value: MATCH | sha: MATCH
ROW 20 | case30-thermal violation rate               | value: MATCH | sha: MATCH
ROW 21 | case30-thermal boundary mass                | value: MATCH | sha: MATCH
ROW 22 | case30-published ridge crossing target      | value: MATCH | sha: MATCH
ROW 23 | case30-published ridge crossing escalation  | value: MATCH | sha: MATCH
ROW 24 | case30-published ridge crossing speedup     | value: MATCH | sha: MATCH
ROW 25 | case30-published ridge esc@0.90             | value: MATCH | sha: MATCH
ROW 26 | case30-published ridge speedup@0.90         | value: MATCH | sha: MATCH
ROW 27 | case30-published ridge missed@0.90          | value: MATCH | sha: MATCH
ROW 28 | case30-thermal ridge crossing target        | value: MATCH | sha: MATCH
ROW 29 | case30-thermal ridge crossing escalation    | value: MATCH | sha: MATCH
ROW 30 | case30-thermal ridge crossing speedup       | value: MATCH | sha: MATCH
ROW 31 | case30-thermal ridge esc@0.90               | value: MATCH | sha: MATCH
ROW 32 | case30-thermal ridge speedup@0.90           | value: MATCH | sha: MATCH
ROW 33 | case30-thermal ridge missed@0.90            | value: MATCH | sha: MATCH
ROW 34 | case30-published histgb crossing target     | value: MATCH | sha: MATCH
ROW 35 | case30-published histgb crossing escalation | value: MATCH | sha: MATCH
ROW 36 | case30-published histgb crossing speedup    | value: MATCH | sha: MATCH
ROW 37 | case30-published histgb esc@0.90            | value: MATCH | sha: MATCH
ROW 38 | case30-published histgb speedup@0.90        | value: MATCH | sha: MATCH
ROW 39 | case30-published histgb missed@0.90         | value: MATCH | sha: MATCH
ROW 40 | case30-thermal histgb crossing target       | value: MATCH | sha: MATCH
ROW 41 | case30-thermal histgb crossing escalation   | value: MATCH | sha: MATCH
ROW 42 | case30-thermal histgb crossing speedup      | value: MATCH | sha: MATCH
ROW 43 | case30-thermal histgb esc@0.90              | value: MATCH | sha: MATCH
ROW 44 | case30-thermal histgb speedup@0.90          | value: MATCH | sha: MATCH
ROW 45 | case30-thermal histgb missed@0.90           | value: MATCH | sha: MATCH
ROW 46 | H2 lo values with ZERO acceptance           | value: MATCH | sha: MATCH
ROW 47 | H2 chosen range                             | value: MATCH | sha: MATCH
ROW 48 | H2 chosen acceptance                        | value: MATCH | sha: MATCH
ROW 49 | H3 build acceptance                         | value: MATCH | sha: MATCH
ROW 50 | case30-thermal N-1 loading >100%            | value: MATCH | sha: MATCH
ROW 51 | case30-published N-1 loading >100%          | value: MATCH | sha: MATCH
ROW 52 | 2C shortfall histgb benign->benign          | value: MATCH | sha: MATCH
ROW 53 | 2C shortfall histgb benign->marginal        | value: MATCH | sha: MATCH
ROW 54 | 2C shortfall histgb marginal->benign        | value: MATCH | sha: MATCH
ROW 55 | 2C shortfall histgb marginal->marginal      | value: MATCH | sha: MATCH
ROW 56 | 2C shortfall ridge benign->benign           | value: MATCH | sha: MATCH
ROW 57 | 2C shortfall ridge benign->marginal         | value: MATCH | sha: MATCH
ROW 58 | 2C shortfall ridge marginal->benign         | value: MATCH | sha: MATCH
ROW 59 | 2C shortfall ridge marginal->marginal       | value: MATCH | sha: MATCH
ROW 60 | 2D shortfall histgb line->line              | value: MATCH | sha: MATCH
ROW 61 | 2D shortfall histgb line->trafo             | value: MATCH | sha: MATCH
ROW 62 | 2D shortfall histgb trafo->line             | value: MATCH | sha: MATCH
ROW 63 | 2D shortfall histgb trafo->trafo            | value: MATCH | sha: MATCH
ROW 64 | 2D shortfall ridge line->line               | value: MATCH | sha: MATCH
ROW 65 | 2D shortfall ridge line->trafo              | value: MATCH | sha: MATCH
ROW 66 | 2D shortfall ridge trafo->line              | value: MATCH | sha: MATCH
ROW 67 | 2D shortfall ridge trafo->trafo             | value: MATCH | sha: MATCH
ROW 68 | 2E shortfall histgb tilted_test_unweighted_cal   | value: MATCH | sha: MATCH
ROW 69 | 2E shortfall histgb tilted_test_weighted_cal     | value: MATCH | sha: MATCH
ROW 70 | 2E shortfall histgb untilted_test_unweighted_cal | value: MATCH | sha: MATCH
ROW 71 | 2E shortfall ridge tilted_test_unweighted_cal    | value: MATCH | sha: MATCH
ROW 72 | 2E shortfall ridge tilted_test_weighted_cal      | value: MATCH | sha: MATCH
ROW 73 | 2E shortfall ridge untilted_test_unweighted_cal  | value: MATCH | sha: MATCH
ROW 74 | 2F baseline off-setpoint gens mean          | value: MATCH | sha: MATCH
ROW 75 | 2F ridge deep misses                        | value: MATCH | sha: MATCH
ROW 76 | 2F ridge distinct elements                  | value: MATCH | sha: MATCH
ROW 77 | 2F ridge max miss depth                     | value: MATCH | sha: MATCH
ROW 78 | 2F histgb deep misses                       | value: MATCH | sha: MATCH
ROW 79 | 2F histgb distinct elements                 | value: MATCH | sha: MATCH
ROW 80 | 2F histgb max miss depth                    | value: MATCH | sha: MATCH

COUNTS: value MATCH 80, value MISMATCH 0, value NOT FOUND 0 | sha MATCH 80, sha MISMATCH 0, sha NOT FOUND 0
```

Interpretive points that did not change any verdict but are worth recording:

- **Percent-to-fraction conversion (rows 18-21).** The jsonpath names `violation_rate_pct` / `boundary_mass_pct`, and the artifact stores `28.8081`, `20.0146`, `15.3967`, `7.0862`. The table states these as fractions (`0.288081` etc.). The conversion is correct and applied consistently, but the jsonpath as written does not literally yield the stated value.
- **Abbreviated jsonpaths.** `crossings.*` is really `crossings_first_below_1pct_missed.*`; `four_metrics.*` is `four_metrics_at_90pct_coverage.*`; `baseline.offsetpoint_gens_mean` is `baseline_all_n1_rows.offsetpoint_gens_mean`. Unambiguous, all resolve to the stated values.
- **Aggregation labels that describe stored scalars.** Rows 22-45 are labelled "seed-mean" but the `crossings.*` fields are stored scalars, not per-seed arrays I could re-average; the `four_metrics.*_mean` fields are pre-computed means. I verified the stored value; the seed-level re-derivation is only possible for case30-thermal (which carries a `records` array) and I did not need it since the stored values matched.
- **Rows 12-17 (flag branch).** The `@0.94` / `@0.97` qualifiers are cosmetic — flag membership is target-invariant in this artifact, so the pooled and seed-mean figures are identical at every one of the 30 targets. I confirmed this: filtering to the named target gives exactly the same numbers as pooling all targets.
- **Rows 6-10 subsetting.** Row 8 (`0.731358`) and row 10 (`0.249259`) match the converged N-1 subset specifically. Over all attempted N-1 rows including the 45 failures the values would be `0.731240` and `0.249333`. The row conditions read as bare (`max_vm>1.05`, `gen_out>=0`), so the converged restriction is implicit but is the one that reproduces the stated value.
- **Rows 76 and 79** (`n_distinct_elements` 32 / 54) are stored scalars; the `deep_elements` list in the artifact is truncated to the top 10 entries (31 and 43 counted occurrences), so those two cannot be recomputed from the artifact alone. I verified the stored field. Rows 75/77/78/80 I did re-derive from `per_seed_depth` (n_deep sums to 58 and 106; max over seeds is 0.032425998 and 0.091456925).
---

### Outcome

| pass | claims | MATCH | MISMATCH | NOT FOUND |
|---|---|---|---|---|
| verifier-drift (2C/2D/2E) | 13 | **13** | 0 | 0 |
| verifier-s3, value check | 80 | **80** | 0 | 0 |
| verifier-s3, sha256 check | 80 | **80** | 0 | 0 |

No §2f condition fired: no MISMATCH on any headline number.

### New defect found BY the verifier, not self-reported

**C2E-2 — `realized_mean_agg_cal` is also unweighted across all three cells.**
`scripts/drift_tests.py:237` sets `realized_mean_agg_cal=float(agg[ci].mean())` for every
cell, so the `tilted_test_weighted_cal` row reports the **unweighted** calibration mean and
hides the effect of `w_cal`. Verified identical across cells within each seed: 1.058861,
1.059059, 1.059392, 1.059325, 1.058282.

This is a companion to the already-recorded C2E-1 (`realized_mean_agg_test` carrying the
tilted mean on the untilted control). Both are **reporting-column defects only** — coverage,
escalation, missed and speedup are unaffected in every cell, which the verifier confirmed by
reproducing all six 2E shortfalls to 6 dp.

### Documentation defects in `notes/writing-numbers.md`, found by the verifier

None changed a verdict. All five are recorded in the file itself under "Verifier findings
against this table" so a later reader cannot be misled by the jsonpath column:

1. **Rows 18-21** name `violation_rate_pct` but state the value as a fraction. The conversion
   is correct and consistent, but the jsonpath as written does not literally yield the stated
   value.
2. **Abbreviated jsonpaths.** `crossings.*` is `crossings_first_below_1pct_missed.*`;
   `four_metrics.*` is `four_metrics_at_90pct_coverage.*`;
   `baseline.offsetpoint_gens_mean` is `baseline_all_n1_rows.offsetpoint_gens_mean`.
3. **Rows 22-45 labelled "seed-mean" are stored scalars**, not per-seed arrays. The label
   describes how the stored value was originally produced, not an aggregation the reader can
   redo from that file. Only case30-thermal carries a `records` array permitting re-derivation.
4. **Rows 6-10 carry an implicit converged restriction.** Over all attempted N-1 rows
   including the 45 failures the values would be 0.731240 and 0.249333 rather than 0.731358
   and 0.249259.
5. **Rows 76 and 79** (`n_distinct_elements` 32 / 54) cannot be recomputed from
   `data/qlimit_class.json` alone: its `deep_elements` list is truncated to the top 10
   (31 and 43 occurrences counted). The stored scalar was verified; the underlying list is not
   complete in the artifact.

### What I did not do, and why

- **No git write, no prose, no `.tex` edit, no edit to resolve C1-7/C1-10/C1-11.**
- **Did not change any value in `notes/writing-numbers.md`** — every one verified correct.
  Only an append-only "Verifier findings" section was added, recording the five documentation
  defects above.
- **Did not fix C2E-1 or C2E-2 in the artifact** — they are reporting columns, the affected
  results are unaffected, and regenerating would cost a rerun for no change to any conclusion.

---

## FOUR-AGENT AUDIT OF STAGES 0-3

**Run:** 2026-08-19T15:00:00Z. Four subagents spawned in ONE turn, in parallel. Each was
restricted to Read/Grep/Bash, forbidden from Write/Edit, and **explicitly forbidden from
reading `notes/RUN_REPORT.md`** so that none of them could inherit a conclusion recorded here.

The four reports are appended **verbatim and separately**, not merged, per instruction.

---

### AGENT 1 of 4 — physics-stages — VERBATIM

Audit complete. Findings below; all numbers computed by me from the artifacts, not read from any report.

## Direct answer to (1) — 2C is a voltage-margin split, not an operating-point shift, and it is confounded

`scripts/drift_tests.py:113-118` splits the 1500 base scenarios at the median `n0_min_vm` (= 0.9433575). `n0_min_vm` is a **solved outcome**, not a sampled control. Here is what actually differs between the two strata (750 base scenarios each, 139,485 / 139,470 converged N-1 rows):

| quantity | benign | marginal | verdict |
|---|---|---|---|
| base `n0_min_vm` mean | 0.94649 | 0.94158 | split variable, by construction |
| **`agg_loading` mean** | **1.05837** | **1.05984** | Δ = 0.0015 = **0.13σ** (within-stratum σ = 0.0113). t = −2.52, p = 0.012 — detectable, physically nil |
| gen-outage share of bases | 0.2253 | 0.2733 | **Δ = +4.8 pp, z = 2.15 (p ≈ 0.03) — a real confound** |
| post-contingency `min_vm` mean | 0.94205 | 0.93761 | Δ = −0.00444 |
| violation rate | 0.1537 | 0.1958 | Δ = +4.2 pp |
| boundary strip [0.94, 0.945) share | 0.3346 | 0.8027 | **Δ = +46.8 pp — the dominant difference** |
| transformer share of outages | 0.0698 | 0.0697 | identical |
| non-convergence share | 0.00011 | 0.00022 | negligible |
| top argmin buses (0-based) | 75: 24.2%, 52: 13.8%, 106: 7.7% | 75: 30.0%, 52: 19.9%, 106: 10.9% | **mild structural confound — marginal stratum concentrates on the weak buses** |

**It is a margin shift, not an operating-point shift.** Three independent computations say so:

1. Load level is the same. `corr(n0_min_vm, agg_loading)` over base cases = **−0.0724**. The median split on `n0_min_vm` is almost orthogonal to load. Nor is it a shift in any other sampled control: `corr(n0_min_vm, mean genvm)` = 0.199, `corr(n0_min_vm, mean genqmax)` = −0.007. No sampled input explains the split — it splits on the solved base voltage itself.
2. The shift is a **rigid offset**, not a change in contingency response. Post-outage gap = 0.00444; base `n0_min_vm` gap = 0.00491. **90% of the post-contingency shift is inherited from the base offset.** The contingency-induced drop (`n0_min_vm − min_vm`) is statistically the same in both strata: mean 0.004439 vs 0.003972, median 0.0 in both, share with zero drop 0.5522 vs 0.5753, p99 0.0636 vs 0.0616. The two strata respond to outages identically; they just start 0.005 pu apart.
3. What actually moves is the boundary density. ρ = strip share / 0.005 = **66.9/pu (benign) vs 160.5/pu (marginal)**. The control escalations track it: benign/benign 0.180 vs marginal/marginal 0.577 at 90% coverage.

**Divergence from the stated question.** The stated question is whether the band holds *inside the boundary layer where the floor lives*. The median split does not isolate the boundary layer — **33.5% of benign N-1 rows are already inside [0.94, 0.945)**. So the design is "more boundary vs less boundary", not "boundary vs not". What it delivers is a **shift in the boundary-mass density ρ**, which is exactly the quantity the escalation floor is made of — so the cell that matters (calibrate benign → test marginal) is a test of whether a band calibrated at low ρ holds at high ρ, not a test of the guarantee inside the layer.

The 2×2 from `data/drift_n0_stratum_long.parquet` (5 seeds × 2 families):

| cal → test | cov@0.90 (sd) | cov@0.95 (sd) | esc@0.90 |
|---|---|---|---|
| benign → benign (control) | 0.8948 (0.0143) | 0.9487 (0.0061) | 0.180 |
| **benign → marginal** | **0.8456 (0.0549)** | **0.9356 (0.0123)** | 0.486 |
| marginal → benign | 0.9167 (0.0199) | 0.9548 (0.0091) | 0.266 |
| marginal → marginal (control) | 0.8939 (0.0235) | 0.9469 (0.0068) | 0.577 |

The shifted cell under-covers by 4.8 pp against its own-stratum control at 0.90 — but its seed sd is **0.0549**, larger than the gap at 0.95 and comparable to it at 0.90. **By the project's own std rule the 0.95 result (0.9356 vs 0.9469, gap 0.011, sd 0.012) is not a finding.**

**Confounds to state explicitly if this is written up:** (a) generator-outage prevalence differs by 4.8 pp, so the marginal stratum contains more two-element states — an uncontrolled second shift; (b) argmin-bus composition shifts toward buses 75/52/106; (c) `agg_loading` differs at p = 0.012 and should be reported as controlled-but-nonzero rather than ignored. Load level and contingency response are **not** confounds and can be affirmatively cleared with the numbers above.

---

## Direct answer to (2) — the 2H thermal N-0 criterion selects NEAR-LIMIT bases, at a de-stressed load level

I replayed the exact draw loop (`scripts/case30_thermal_build.py:104-140`, seed 100, range [0.87, 0.99]) and reproduced `h3_build_stats.json` exactly: **8050 draws, 1500 accepted, rejected 5710 thermal / 840 voltage.**

Base max `loading_percent` (max over 41 lines):

| population | n | min | p10 | p25 | median | p75 | p90 | max |
|---|---|---|---|---|---|---|---|---|
| all draws | 8050 | 81.0 | 97.1 | 101.4 | **106.2** | 111.6 | 116.7 | 149.7 |
| voltage-accepted only | 7210 | 81.0 | 96.8 | 101.0 | 105.6 | 110.6 | 115.0 | 144.0 |
| **thermal-accepted** | **1500** | **81.0** | **92.0** | **94.5** | **96.9** | **98.6** | **99.4** | **99.999** |

**It selects near-limit networks.** 95.6% of accepted bases are above 90% loading, 71.0% above 95%, 17.5% above 99%. The criterion is a right-truncation at 100 of a distribution whose median is 106.2 — the accepted set piles against the ceiling. It does not select low-load networks in the thermal sense.

**But it does de-stress the load level, twice over:**
- **Range choice (dominant).** H2 moved the window from the committed [1.00, 1.12] to [0.87, 0.99]. Published case30 `agg_loading` runs 0.9895–1.1272 (mean 1.0595); thermal case30 runs 0.8502–0.9856 (mean 0.9188). **The two datasets have disjoint `agg_loading` support** (0.9856 < 0.9895).
- **Acceptance selection inside the window.** Mean `agg_loading` 0.9300 (all draws) → **0.9188** (accepted), and acceptance falls monotonically with load: 0.82 at agg ≈ 0.86, 0.36 at 0.90, 0.21 at 0.925, 0.077 at 0.945, 0.010 above 0.978. `corr(agg_loading, base max loading)` = 0.413.

**What case30-thermal actually demonstrates, versus the published case30:**

| | published case30 | case30-thermal |
|---|---|---|
| `agg_loading` | 0.9895–1.1272 (mean 1.0595) | 0.8502–0.9856 (mean 0.9188) — disjoint |
| N-1 violation rate | 28.81% | 15.40% |
| boundary mass [0.94, 0.945) | 20.01% | 7.09% |
| esc @ 0.90, histgb | 6.98% ± 0.87 | 2.65% ± 0.41 |
| net speedup, histgb | 14.5 | 38.6 |
| ρ·q̂ identity check | reported (−0.18% / −11.1% error) | **computed and discarded** |

They are **not the same demonstration**. Published case30 was a second network at a comparable stress level to case118, showing boundary mass 20.0% vs 56.9% and therefore a much lower floor — the network-dependence of ρ. case30-thermal is a **third operating point on the same ρ curve**, at a materially milder regime, showing the floor drops further when ρ drops further. It is a consistency check on the mechanism, not a thermally-repaired replacement for the published case30 result, and it cannot be swapped in for it without also reporting the load-window change.

Three further divergences in 2H:
- **"Thermal-feasible" holds at N-0 only.** `h3_build_stats.json` → `n1_loading.share_above_100 = 0.2148`: **21.5% of the 61,500 N-1 states in the "thermal-feasible" dataset exceed 100% line loading** (median 97.7, p90 106.7, max 145.8). The screener screens N-1 and screens voltage only, so within the regime the gate operates in, the dataset is thermally infeasible in one contingency out of five.
- **The gate is unchanged.** `scripts/case30_thermal_gate.py` screens `min_vm` against 0.94 exactly as before. Nothing thermal enters the gate. The experiment changes the *sampler*, not the *screener*.
- **The mechanism number is dropped.** `case30_thermal_gate.py:98-102` computes `rho_cal` and `predicted_esc = rho_cal * q90` per (family, seed), but `summary[family]` (lines 128-140) and `out` (lines 160-175) never emit them. `data/case30_frozen.json` carries `predicted_esc_mean` and `predicted_vs_measured_pct_error`; `data/case30_thermal/case30_thermal_frozen.json` does not. The one quantity that would tie case30-thermal to the ρ·q̂ claim is computed and thrown away.

---

## Per-experiment audit

### 2A — thermal / over-voltage (`scripts/thermal_check.py` → `data/thermal_check.json`)

**STATED QUESTION:** are thermal ratings present and meaningful, and what is the over-voltage picture?
**ACTUALLY MEASURED:** (i) a rating-plausibility audit on the *nominal* network; (ii) `max_vm` exceedance shares against a hardcoded 1.05 pu; (iii) for case30 only, a prefix sweep of post-contingency line loading.
**DIVERGENCE — three:**

1. **The over-voltage threshold does not match the network's own limit.** `thermal_check.py:34` sets `OVER_V = 1.05` and the artifact's top-level field is `"over_voltage_threshold": 1.05`. But `pn.case118().bus.max_vm_pu` is **1.06 on all 118 buses** (and `min_vm_pu` is 0.94 — the project's floor comes from the network, so the upper limit should come from the same place). Against 1.05 the artifact reports 73.4% of base cases and 73.1% of N-1 rows over limit; **against the network's declared 1.06 it is 5.80% and 5.74%.** The 1.06 numbers are in the JSON as `share_above_1p06`, but the headline field is the wrong threshold, and the ~13× difference is the whole interpretation.
2. **The result is an N-0 acceptance-gate gap, not a contingency effect, and is not framed that way.** base 5.80% → N-1 5.74% at 1.06: contingencies do not create over-voltage. What the number shows is that **5.8% of *accepted base cases* already violate the network's upper voltage limit before any outage**, because `generate_dataset.py:256` gates on `n0_min_vm >= 0.94` only. That is structurally the identical defect 2H fixes for thermal on case30 — and 2A does not connect them. It also directly qualifies `report/paper_current_STS.tex:92` ("we do not check for thermal line loading or over-voltage, so the only active constraint is the lower voltage limit"): over-voltage is not inert on case118's own limit, it is unchecked.
3. **The case30 thermal sweep measures base infeasibility, not contingency overload.** `share_above_100 = 1.0` exactly, median 154.7%, max 490.4% — but `rating_audit` in the same file reports the **nominal case30 base is already at 111.8%**, and the published case30 dataset sits at `agg_loading` 0.99–1.13 on top of that. Every contingency exceeding 100% is the arithmetic consequence of a base that already does. The artifact labels the prefix honestly (`"first 120 of 1500 base scenarios in dataset order, not a random sample"`) but does not report the base-case loading of the swept scenarios, which is what would make the 1.0 interpretable.

Minor, non-blocking: `rating_audit` (`thermal_check.py:51`) solves the *builder-default* network, so `base_case_loading_pct` describes nominal loads, not the study's sampled bases. The placeholder verdicts are correct and well-evidenced independently (case118 implied MVA = 9900.0 uniform on all 173 lines and all 13 transformers, 2 distinct `max_i_ka` values, base max loading 4.48%). The refusal to sweep a placeholder-rated network is sound.

### 2B — generator outage + multiplier audit (`scripts/sampling_audit.py` → `data/sampling_audit.json`)

**STATED QUESTION:** generator-outage prevalence and its distributional effect, plus which quantities the 1.0–1.12 multiplier touches.
**ACTUALLY MEASURED:** prevalence and the min_vm distribution split by outage status; a 3-way (AST / empirical / documented) audit of the multiplier.
**DIVERGENCE — one substantive, one framing:**

1. **`acceptance_effect` states a causal hypothesis the artifact declines to test, and the test is 13 seconds of work.** `sampling_audit.py:148-151`: *"If the gate is the cause, accepted gen-out scenarios should sit closer to the 0.94 rejection boundary. Rejected draws are NOT recorded in the dataset, so the rejection rate by outage status CANNOT BE COMPUTED from this artifact."* True of the artifact, false of the experiment — the generator is deterministic given the seed. I replayed the committed configuration (`README.md:94-95`) with `np.random.default_rng(0)`, 1169 draws to 600 accepted, 12.8 s:

   - P(gen_out) among **draws**: 0.2789 (consistent with the coded 0.30; n = 1169, se = 0.013)
   - P(gen_out) among **accepted**: 0.2300 (artifact reports 0.2493 for the full run)
   - **acceptance rate: 0.4233 with a generator out vs 0.5480 without**
   - non-convergence: 0.0031 vs 0.0047 — not the mechanism

   **The N-0 voltage gate is confirmed as the cause.** The artifact's own weak proxy — mean `n0_min_vm` with outage 0.94381 vs without 0.94410, Δ = 0.00029 — is far too small to support the inference, and the artifact correctly does not draw it. The gap is real, not noise: 0.2493 vs 0.30 on n = 1500 is z = −4.29.
2. **Framing.** `distribution_by_outage_status` reports Δ violation rate +1.01 pp and Δ boundary strip +1.64 pp on n = 69,532 vs 209,423 — statistically certain, physically small. The artifact reports the deltas without a variability estimate, so "materially different in distribution" (the header's word, `sampling_audit.py:17`) is not adjudicated by anything in the file. Under the project's own std rule these should be reported as detectable-but-small.

The multiplier audit itself is clean and I found no divergence: AST targets, empirical per-family variance, and the README invocation agree; `net.gen['p_mw']` is genuinely never assigned; the `agg_loading` max of 1.1239 > 1.12 is explained by the regional block multiplier plus jitter and is consistent with `generate_dataset.py:115-118` (`LOADING_CAP` clipping).

### 2C — `n0_min_vm` stratum drift

Covered in full above. Summary: **DIVERGENCE.** Labelled an operating-point shift; is a base-voltage-margin shift (load identical at 0.13σ, contingency response identical, 90% of the effect a rigid offset). Does not isolate the boundary layer (benign is 33.5% boundary). Confounded by generator-outage prevalence (+4.8 pp, z = 2.15) and argmin-bus composition. The 0.95 cell fails the project's own std rule.

### 2D — element-type drift

**STATED QUESTION:** *"the event space changes, so no likelihood ratio exists; this is the N-1 → N-2 failure mode"* (`drift_tests.py:31-32`).
**ACTUALLY MEASURED:** calibrate on the 173-line population, test on the 13-transformer population (and reverse), with same-stratum controls. Results (5 seeds × 2 families):

| cal → test | cov@0.90 | cov@0.95 | esc@0.90 | n_cal |
|---|---|---|---|---|
| line → line | 0.8962 | 0.9483 | 0.398 | 51,900 |
| **line → trafo** | **0.8845** | **0.9289** | 0.386 | 51,900 |
| trafo → line | 0.9097 | 0.9680 | 0.449 | 3,890 |
| trafo → trafo | 0.8959 | 0.9473 | 0.434 | 3,890 |

**DIVERGENCE — two:**

1. **The N-2 analogy is overstated.** The branch identity is a one-hot feature block (`make_splits.build_design_matrix`, 186 columns) and the surrogate is trained on the *standard* train split, which contains **both** element types. Transformer outages are inside the training distribution. Genuine N-2 states are outside it in the physics, not just in a one-hot block. This is a covariate shift with disjoint support in a categorical feature, and the shift-vs-control gaps (1.2 pp at 0.90, 1.9 pp at 0.95) are much smaller than the N-1→N-2 failure the analogy invokes. The manuscript already makes the N-2 claim carefully at `report/paper_current_STS.tex:116` — 2D should not be cited as evidence for it.
2. **The design changes calibration sample size (13×) simultaneously with the distribution, and does not control it.** I ran the missing control (3 seeds × 2 families): calibrate on line rows **subsampled to n = 3890**, test on line.

   | calibration set | cov@0.90 | cov@0.95 | esc@0.95 | q̂@0.95 |
   |---|---|---|---|---|
   | line, full (51,900) | 0.8972 | 0.9482 | 0.591 | 0.006004 |
   | line, subsampled to 3,890 | 0.8941 | 0.9463 | 0.585 | 0.005814 |
   | trafo (3,890) | 0.9121 | 0.9677 | 0.694 | 0.007698 |

   **The confound is real but not material** — matching n moves coverage by 0.2 pp, while the trafo calibration moves it by 2.0 pp. So the trafo-calibration over-coverage is a genuine distribution effect. This clears the design, but the clearing computation is mine, not the experiment's; as written the artifact cannot distinguish the two.

### 2E — loading soft tilt

**STATED QUESTION:** does a soft exponential tilt toward high load break the guarantee, with weighted conformal as the repair?
**ACTUALLY MEASURED:** an exp(3·normalised `agg_loading`) tilt, applied by bootstrap-resampling the test set with replacement, against unweighted and weighted calibration.

| cell | cov@0.90 | sd | cov@0.95 | sd | esc@0.90 |
|---|---|---|---|---|---|
| untilted / unweighted cal (control) | 0.8958 | 0.0126 | 0.9483 | 0.0060 | 0.398 |
| tilted / unweighted cal | 0.8948 | 0.0115 | 0.9465 | 0.0053 | 0.406 |
| tilted / weighted cal | 0.8969 | 0.0127 | 0.9489 | 0.0054 | 0.410 |

**DIVERGENCE — the experiment is underpowered by construction and cannot answer its question:**

1. **The tilt axis is nearly orthogonal to the target.** `corr(agg_loading, min_vm)` over all 278,955 converged N-1 rows = **−0.0304**. By comparison `corr(n0_min_vm, min_vm)` = **0.2242**. Tilting hard on `agg_loading` barely moves the outcome distribution no matter how large λ is. "Loading drift" is a natural-sounding shift axis that this dataset does not support as a driver.
2. **The realized shift is tiny.** `realized_mean_agg` moves 1.0590 (cal) → 1.0640 (tilted test): Δ = 0.005 on a within-population sd of 0.0113 (≈0.44σ) and a full range of 1.019–1.096. ESS fraction is 0.822 — the tilt is barely a tilt.
3. **All three cells are within noise of each other.** Max spread across cells is 0.0021 at 0.90 and 0.0024 at 0.95, against seed sds of 0.0126 and 0.0060. **Under the project's std rule, no difference here is real** — including the apparent benefit of weighted calibration. This is a null with no power behind it, and reporting it as "the guarantee survived the tilt" would be the divergence.
4. **Implementation note.** The tilted test set is `rng.choice(len(ti), size=len(ti), replace=True, p=w/Σw)` (`drift_tests.py:216-218`) — a bootstrap of the *observed* test rows. It can reweight but never extrapolate beyond observed support, and the duplicated rows make the seed sd an underestimate of true variance. That is a correct implementation of a within-support tilt, but it bounds what the experiment could ever detect.

The framing at `drift_tests.py:32-35` (why a median split on loading is *not* used) is technically sound and I found no error in it.

### 2F — Q-limit class

**STATED QUESTION:** do deep misses at the recommended operating points form an identifiable class with a **pre-outage signature**?
**ACTUALLY MEASURED:** for each deep miss, the count of "off-setpoint" generators and the graph distance from the argmin bus to the nearest one.
**DIVERGENCE — the indicator has no discriminative power, and the artifact lacks the baseline that would reveal it:**

1. **The off-setpoint indicator fires everywhere.** `baseline_all_n1_rows.offsetpoint_gens_share_with_any = 1.0`, mean 20.80 of 53 generators (52.75 in service on average). Deep misses: 21.33 (ridge) and 21.45 (histgb). **A statistic with the same value in the event class and the background cannot identify a class.** The artifact does report this contrast honestly, which is to its credit — but the conclusion it forces is that the indicator is inert, not that a signature was sought and weakly found.
2. **The tolerance is not the issue.** `SETPOINT_TOL = 1e-4` (`qlimit_class.py:42`). I swept it: 1e-4 → 20.80 gens/row, share-with-any 1.0000; 1e-3 → 19.55, 1.0000; 5e-3 → 14.84, 1.0000; 1e-2 → 9.99, 1.0000; 2e-2 → 3.62, 0.9760. There is no tolerance at which "some generator is off setpoint" becomes a rare event. The `|vm0 − genvm|` distribution over in-service generators has median 3.3e-8 but p75 = 6.6e-3 and p99 = 3.7e-2 — bimodal, and roughly 40% of generators genuinely bind under `enforce_q_lims=True` with `qscale ~ U(0.60, 1.40)`. The physics reading is right; the event is just ubiquitous.
3. **`min_hops` — the only statistic that could discriminate — has no baseline in the artifact.** `baseline_all_n1_rows` (`qlimit_class.py:190-195`) reports only the off-setpoint count and violation rate. I computed the missing baseline over 4,000 randomly sampled N-1 rows: **mean 1.342, median 1.0, share ≤ 2 = 0.8958, share = 0 = 0.2472.** Against that:

   | | mean min_hops | share ≤ 2 |
   |---|---|---|
   | **baseline (all N-1 rows)** | **1.342** | **0.8958** |
   | ridge deep misses (n = 58) | 1.552 | 0.8103 |
   | histgb deep misses (n = 106) | 0.981 | 0.8962 |

   **The two operating points bracket the baseline** — ridge worse, histgb identical to three decimals (0.8962 vs 0.8958). There is no proximity signal. This is unavoidable: with 20.8 off-setpoint generators scattered over 118 buses, *every* bus is ~1 hop from one.
4. **The deep-miss class is diffuse on every other axis too**, which the artifact does report: 58 deep misses over 32 distinct elements (top share 8.6%) and 25 argmin buses (top 10.3%) for ridge; 106 over 54 elements (top 4.7%) and 31 buses (top 15.1%) for histgb.

**Consequence for the manuscript.** `report/paper_current_STS.tex:262` says *"A model trained only on pre-outage features cannot predict such a situation."* 2F was built to adjudicate information-absence vs statistical-rarity (`qlimit_class.py:29-33`) and **it does not adjudicate it** — a feature present in 100% of rows is evidence for neither branch. The 0.0915 pu worst miss appears in the histgb per-seed maxima for seeds 2 and 3, so the anchor is reproduced; the mechanism attribution is not tested by this artifact.

### 2H — case30 thermal regeneration

Covered in full above. Summary of divergences: (a) the criterion selects near-limit bases (median 96.9%, p90 99.4%, max 99.999%) while simultaneously de-stressing load into a window **disjoint** from the published case30; (b) "thermal-feasible" holds at N-0 only — **21.5% of the N-1 states in the dataset exceed 100% loading**; (c) the gate remains voltage-only, so the experiment changes the sampler, not the screener; (d) `predicted_esc = ρ·q̂` is computed at `case30_thermal_gate.py:98-102` and never written to the output, so the mechanism identity check that `data/case30_frozen.json` carries is absent for the counter-example. The H1 refusal logic (`assert_ratings_usable`, `case30_thermal.py:49-72`) and the leakage guard (loading routed to `n1_loading.parquet`, asserted at `case30_thermal_gate.py:62-65`) are both correct and I found no problem with either. The 5/5 equivalence checks against `run_scenario` pass with zero diffs.

---

## No divergence found

- 2A placeholder verdicts and the refusal to sweep placeholder-rated networks.
- 2B multiplier audit (all three methods agree; `net.gen['p_mw']` genuinely never assigned).
- 2C/2D/2E shared design: model fit once per (seed, family) on the standard train split with the stored M2 config, only cal/test populations varying — this does isolate the shift from model differences, as claimed, and every shifted cell does carry a same-stratum control.
- 2E's stated reason for rejecting a hard median split on loading (disjoint support ⇒ infinite density ratio ⇒ outside the weighted-conformal framework).
- 2H protocol-drift assertion against `scripts/case30_gate.py` and the equivalence check against `run_scenario`.

## Scratch files (mine, not repo artifacts)

`/private/tmp/claude-501/-Users-rajansaha-contingency-screener-research/a20165b8-6ffa-4031-84e5-ca5fd47a15f6/scratchpad/replay.py`, `replay.parquet` (case30-thermal draw replay), `rep118.py` (case118 acceptance-by-outage-status replay), `nctl.py` (2D sample-size control + 2E correlations). I wrote no file inside the repository.
---

### AGENT 2 of 4 — code-audit — VERBATIM

Read all ten files end to end and ran verification computations against the committed artifacts. Findings below.

---

## HIGH

**`scripts/thermal_check.py:159-160` | HIGH | bus-indexed load features assigned positionally to the load table**

```python
net.load["p_mw"] = row[load_p].to_numpy(dtype=float)[:len(net.load)]
net.load["q_mvar"] = row[load_q].to_numpy(dtype=float)[:len(net.load)]
```

`pload_i` / `qload_i` are written by `feasibility/generate_dataset.py:160-165` as **per-bus** aggregates (`pbus[i]`, loop over `range(n_bus)`). This line assigns the first `len(net.load)` of them to load-table **rows**, whose `bus` column is not `0..n_load-1`. For case30: 30 bus columns, 20 loads, `net.load.bus = [1,2,3,6,7,9,11,13,14,15,...]`. Every load gets another bus's demand, and the demand at buses 20-29 is dropped entirely.

The correct idiom already exists elsewhere in the repo — `scripts/classical_screen.py:18-29` deletes the load table and creates one load per bus so index == bus. `thermal_check.py` is the only site that does not.

Consequence: the entire `networks.case30.thermal_sweep` block in `data/thermal_check.json` is computed against a fabricated operating point. It is the only network whose sweep runs (case118 is skipped as PLACEHOLDER), so the whole sweep artifact is affected.

Confirmed by computation, scenario 0 of `data/case30_dataset.parquet`: assigned total load 154.48 MW vs correct 203.95 MW (24% low); all 20 of 20 loads differ; max element-wise error 33.5 MW. Re-running the sweep on a 15-scenario prefix both ways:

| | share > 100% | median | p90 | max |
|---|---|---|---|---|
| as coded | 1.0000 | 162.14 | 184.02 | 474.11 |
| bus-mapped (`[net.load.bus.to_numpy()]`) | 1.0000 | 124.08 | 136.57 | 195.38 |

Published values (120 scenarios): median 154.72, p90 192.48, max 490.45. The as-coded replay tracks the published numbers; the corrected numbers are lower by ~30 pp at the median and 2.5× at the max. The qualitative verdict (share > 100% is 1.0) survives; every quantile does not.

---

## MEDIUM

**`scripts/case30_thermal_build.py:30` + `scripts/case30_thermal.py:222` | MEDIUM | the H2 range-selection sample is a bit-identical prefix of the H3 dataset it selected**

Both stages use seed 100, the same `apply_config` cfg, and the same `sample_scenario`/`solve_n0`/`n0_feasible` path, so `np.random.default_rng(100)` produces the same stream. The 41 scenarios that produced H2's acceptance estimate are the first 41 scenarios of `data/case30_thermal/dataset.parquet`.

Confirmed by replay: replaying `probe_range(0.87, 0.99, n_draws=200, seed=100)` gives 41/200 = 0.205, matching `h2_range_sweep.json.h2.chosen.acceptance_rate` exactly, and the first five `agg_loading` values (0.935331, 0.936387, 0.903755, 0.887072, 0.922299) are identical to the dataset's first five base scenarios (`np.allclose` over all 41: True).

Consequence: the selection rule is `acceptance_rate >= 0.20`, and the chosen range passes at 0.205 only on that 200-draw prefix. `h3_build_stats.json` reports the true rate for the same range at scale as **0.1863** (1500/8050) — the chosen range fails its own selection criterion. A recompute from either artifact reproduces both numbers and the discrepancy stays invisible. Fix is to use a different seed for the sweep than for the build.

**`scripts/drift_tests.py:181-187`, used at `:197-198` | MEDIUM | the weighted-conformal weights are not the likelihood ratio of the tilt actually applied**

`tilt_weights` normalises with `lo, hi = a.min(), a.max()` of whichever array it is handed. `w_cal` uses the calibration split's extremes; `w_te` — the tilt actually resampled onto the test set at `:216-218` — uses the test split's. Since the two ranges differ, `exp(lam·(a-lo_cal)/(hi_cal-lo_cal))` is not proportional to `exp(lam·(a-lo_te)/(hi_te-lo_te))`; the scale factor differs, not just a constant. `weighted_qhat` therefore receives a mis-specified `dP_test/dP_cal`. The weight function is also defined by data-dependent extremes of a random subsample, so it is not a fixed tilt at all — it varies by seed.

Confirmed by computation. Ratio of used to correct calibration weights, `used/correct`, spread across the cal set: seed 0 → 3.67× (cal `agg_loading` range 0.1096 vs test 0.0765), seeds 1-3 → 1.32-1.39×, seed 4 → 1.006×.

Effect on the published `tilted_test_weighted_cal` cell of `data/drift_loading_tilt_long.parquet`, seed 0 (my as-coded recomputation reproduces the stored `q_hat=0.005592`, `escalation=0.542634` exactly, confirming the artifact carries the defect):

| model | cov | q_hat as coded | q_hat corrected | escalation | coverage_emp |
|---|---|---|---|---|---|
| ridge | 0.90 | 0.005592 | 0.005640 | 54.26% → 54.65% | 0.9163 → 0.9176 |
| histgb | 0.90 | 0.002533 | 0.002693 | 37.00% → 38.96% | 0.9091 → 0.9129 |
| histgb | 0.95 | 0.004387 | 0.004505 | 55.44% → 56.15% | 0.9472 → 0.9487 |

Up to ~2 pp on escalation and ~0.4 pp on empirical coverage, worst on the seed with the largest range mismatch. The direction is anti-conservative (band too narrow), which is the direction that matters for a safety claim.

---

## LOW

**`scripts/case30_thermal.py:215` | LOW | dead condition; the artifact's stated selection rule overstates what was enforced**

`choose_range` requires `r["max_base_loading_pct"] <= THERMAL_MAX_PCT`, but `probe_range` is called with `thermal=True`, so `n0_feasible` already rejected every draw with `load_pct > 100` before it reached `base_loads`. The max over accepted draws cannot exceed 100 by construction. Confirmed: 0 of 31 sweep rows exceed 100 (global max 99.998), and the first row with `acceptance_rate >= 0.20` is the chosen row. The chosen range is unchanged, but `h2.selection_rule` in the artifact advertises a two-part criterion of which only one part can bind.

**`scripts/sampling_audit.py:74-91`, called at `:186-195` | LOW | family verdicts computed on a fixed 8-column prefix**

`family_variance(base, prefix, 8)` truncates to the first 8 columns and reports `min_nunique` / `max_std` as if they were family statistics. Checked against the full families: verdicts are unchanged (`genp_` 53/53 constant; `genon_` 51/53 varying). But `pload_` has 19 genuinely constant columns (buses with no load) that the prefix never sees, so `min_nunique` in the artifact is a prefix statistic, not the family's.

**`scripts/case30_thermal_gate.py:59` and `:61-63` | LOW | two guards that cannot fire**

Line 59 asserts `outaged_type != "none"` and `converged`, both of which `ms.load_dataset` already enforced at `feasibility/make_splits.py:23-24`. Lines 61-63 look for leaked loading columns matching `"load" in c.lower() and c.startswith("max_")` — no column can satisfy both (`pload_`/`qload_` fail the prefix; nothing is named `max_load*`). The real leakage guard is that loading was written to a separate parquet; the assertion adds no coverage.

**`feasibility/gate_eval.py:12` and `scripts/drift_tests.py:67-68` | LOW | silent clamp instead of the +∞ atom**

Both quantile routines clamp to the largest finite calibration score when the requested rank exceeds `n`, rather than returning +∞ (certify nothing). Anti-conservative in principle. It cannot trigger at the coverage levels and calibration sizes used here (n ≈ 55,800 cal rows, max coverage 0.98), so no published number is affected — worth a comment rather than a change.

---

## Categories with nothing found

- **Off-by-one in split boundaries / index arithmetic.** Verified all 5 seeds: exactly 900/300/300 scenarios, row counts sum to 278,955 = `len(df)`. `cal_share = cal_frac/(1-train_frac)` gives the intended 60/20/20. The `generate_dataset.py:256` line citation in `case30_thermal.py:20,250` is correct.
- **Leakage between calibration and test, scenario-level included.** Zero scenario overlap train/cal, train/test, cal/test on all 5 seeds; zero overlap between any inner-search partition and the outer cal or test sets. Every mask in `drift_tests.py` (`row_benign[ci]`, `is_line[ti]`, `agg[ci]`) is a global-row boolean array indexed by the split's positional indices into the same `reset_index(drop=True)` frame, and `y[ci][cm_]` matches. `X = pd.concat([scen, branch_oh], axis=1)` preserves the 0..n-1 index, so `.iloc` stays aligned. (One design note, not a defect: the 2C stratum median at `drift_tests.py:115-116` is computed over all 1500 scenarios including test — transductive, but it defines the stratum, not the model.)
- **Wrong axis in groupby / aggregation / reduction.** `select_features` uses `axis=0` correctly; `groupby("scenario_id")["n0_min_vm"].first()` is safe — verified `nunique()` per scenario is 1 for every scenario.
- **Silent dtype coercion.** `min_vm`, `max_vm`, `n0_min_vm` are kept float64 by `_FLOAT64_COLS`, so all limit comparisons are exact. `converged`/`violation` are real bools. The only float32 in a numeric path is `agg_loading`, cast up at `drift_tests.py:192`, which affects only tilt weights and cannot change a gate decision.
- **Filters applied in the wrong order.** Checked `sampling_audit` (converged filter before every block), `thermal_check.overvoltage_from_dataset` (converged before the type split), `case30_thermal_build` (converged before the loading percentiles).
- **Mask built against one dataframe, applied to another.** `sampling_audit.py:126` builds `n1_has_outage` on `n1c`'s own index and applies it to `n1c` — pandas-aligned, correct.
- **Mutable object reused across iterations without reset.** `apply_scenario` resets `net.gen["in_service"] = True` on every call before re-applying the outage; `run_scenario` and `contingency_rows` restore branch `in_service` immediately after each solve, including on the non-convergence path (`solve` swallows the exception). `thermal_check.thermal_sweep` rebuilds the net per contingency. `case30_thermal.probe_range:166` re-applies via `solve_n0` before each deferred N-1 probe — the one place where this was a real bug, already found and fixed with a comment recording it.
---

### AGENT 3 of 4 — consistency-stages — VERBATIM

I did not read `notes/RUN_REPORT.md`. Everything below is computed from the artifacts.

---

## Numbers I computed (basis for all verdicts)

**case118, `data/tradeoff_curve_v2.json`** (5 seeds, M2-tuned, pop. std):

| target | ridge missed % | histgb missed % | ridge q̂ | histgb q̂ | ridge sp | histgb sp |
|---|---|---|---|---|---|---|
| 0.70 | 11.51±1.00 | 12.64±1.34 | .00193 | .00040 | 6.99 | 32.19 |
| 0.90 | 2.96±0.44 | 4.72±0.98 | .00520 | .00229 | 2.04 | 3.29 |
| 0.94 | 0.79±0.21 | 2.48±0.38 | .00708 | .00361 | 1.56 | 2.15 |
| 0.96 | 0.14±0.07 | 1.36±0.20 | .00900 | .00482 | 1.40 | 1.76 |
| 0.97 | 0.03±0.03 | 0.83±0.25 | .01070 | .00574 | 1.35 | 1.58 |

Ridge is lower at every one of the 30 targets 0.70–0.99. Sub-1% crossings: ridge 0.94, histgb 0.97.

**case30-thermal, `data/case30_thermal/case30_thermal_frozen.json`** (recomputed seed-means from `records`):

| target | ridge missed % | histgb missed % | ridge q̂ | histgb q̂ | ridge sp | histgb sp |
|---|---|---|---|---|---|---|
| 0.90 | 6.09±0.42 | 2.23±0.35 | .00697 | .00236 | 8.45 | 38.63 |
| 0.94 | 3.15±0.38 | 1.48±0.34 | .00941 | .00311 | 5.54 | 27.65 |
| 0.98 | 0.52±0.21 | 0.48±0.18 | .01551 | .00521 | 2.65 | 14.08 |

histgb is lower at **all nine** targets. Crossings: ridge 0.98 (37.8% esc, 2.65×), histgb 0.96 (4.86% esc, 21.46×).

**case30-published, `data/case30_tradeoff_curve.json`**: at 0.90 ridge 1.49±0.53 vs histgb 1.47±0.20 (0.03 pp apart, smaller than either std → not a real difference under the std rule). Ridge lower at 0.92–0.98. Crossings: ridge 0.92 (34.5% esc, 2.98×), histgb 0.93 (8.96% esc, 11.27×).

**2C, `data/drift_n0_stratum_long.parquet`, target 0.90:**

| cal → test | ridge cov | ridge missed | ridge q̂ | histgb cov | histgb missed | histgb q̂ |
|---|---|---|---|---|---|---|
| benign→benign (control) | 0.8964 | 5.28% | .0041 | 0.8931 | 8.25% | .0022 |
| benign→marginal | **0.7953** | **5.01%** | .0041 | 0.8960 | **2.46%** | .0022 |
| marginal→benign | 0.9312 | 2.63% | .0057 | 0.9022 | 7.83% | .0024 |
| marginal→marginal | 0.8844 | 2.02% | .0057 | 0.9034 | 1.89% | .0024 |

---

## PAIR 1
**A:** "The linear model also demonstrates the lower missed rate across all targets in the sweep." [`report/paper_current_STS.tex:231`]
**B:** Under 2C stratum mismatch (calibrate on benign, test on marginal) ridge misses **5.01%** of violations vs histgb **2.46%** at target 0.90 — histgb lower at every target from 0.70 to 0.94; and ridge empirical coverage collapses to **0.7953** against a 0.90 target while histgb holds at 0.8960. [`data/drift_n0_stratum_long.parquet`, cells `cal_stratum=benign, test_stratum=marginal`]
**why they cannot both hold:** A is stated without a scope qualifier inside a subsection whose title is a general model-safety claim; B exhibits case118 targets where the linear model is the higher-missed-rate model by 2×.
**verdict:** CONTRADICTION — but conditional on scope. Read strictly as "the sweep" = the pooled case118 curve in Fig. 2, A is **verified true at all 30 targets**. Read as the general statement its subsection title asserts, B refutes it.
**evidence:** Also note the 2C **control** cell (benign→benign, no shift at all) has ridge *higher* than histgb at targets 0.70–0.79 (0.70: 15.58% vs 13.32%); the reversal is therefore not purely a shift artifact. The ridge coverage failure is the larger finding: the 10-point undercoverage occurs *within* N-1, from a pre-outage `n0_min_vm` stratum shift only, with the model and q̂ unchanged.

## PAIR 2
**A:** "The faster model is not the safer one" [`report/paper_current_STS.tex:229`]
**B:** On case30-thermal the gradient-boosted model is simultaneously the faster **and** the safer model at every target: 38.63× vs 8.45× speedup and 2.23±0.35% vs 6.09±0.42% missed at 0.90; sub-1% crossing at 0.96 with 21.46× vs ridge at 0.98 with 2.65×. [`data/case30_thermal/case30_thermal_frozen.json`]
**why they cannot both hold:** A asserts the fast/safe ordering is anti-correlated; on the third result set they are aligned, and the gap (3.86 pp) is ~9× the larger std.
**verdict:** CONTRADICTION.
**evidence:** Across all three result sets the title holds on **one**. case118: holds (ridge safer at all 30 targets, histgb faster). case30-published: does **not** hold cleanly — the 0.90 missed rates are 1.49±0.53 vs 1.47±0.20, a 0.03 pp gap far inside one sigma, so no safety ordering exists at the paper's own operating point, and the sub-1% crossings are one target apart (0.92 vs 0.93) with histgb delivering 11.27× against ridge's 2.98×. case30-thermal: inverted. This is also a failed preregistered prediction — P2H-8 at `notes/preregistration.md:209-210` predicted "ridge the lower missed rate, as on both existing networks," moderate confidence.

## PAIR 3
**A:** "the worst case … is an example of a sudden collapse where a generator at that case's weakest bus hits its reactive limit and can no longer regulate voltage. A model trained only on pre-outage features cannot predict such a situation." [`report/paper_current_STS.tex:262`]
**B:** The position to test: A is unsupported because `feasibility/make_splits.py` admits `genqmin_*`/`genqmax_*` into the design matrix, so the reactive limits are present.
**why they would conflict:** B claims the information is in X; A claims it is absent.
**verdict:** NOT A CONFLICT — B is refuted on two counts.
**evidence:** (i) B's premise is factually correct: `make_splits.py:21-31` keeps every numeric column not in `EXCLUDE_COLS` (`scenario_id, sampling_mode, outaged_type, outaged_idx, gen_out, agg_loading, n0_converged, n0_min_vm, converged, min_vm, max_vm, argmin_bus, violation, straddle, deep_collapse`), and I confirmed 106 `genqmin_*`/`genqmax_*` columns in `data/dataset.parquet`, all with non-zero train variance, so none is dropped by `select_features`. Also present: 118 `vm0_*`, 53 each of `genvm_*`, `genon_*`, `genp_*`. (ii) But the inference does not follow: those columns are the *limit values assigned to the scenario*, not the post-outage event of binding against them. Saturation is an outcome of the contingency solve. (iii) `data/qlimit_class.json` tested exactly B's hypothesis and returned negative: the off-setpoint-generator signature has `share_with_any = 1.0` in the deep-miss sets **and** `share_with_any = 1.0` in the all-N-1 baseline (mean 21.33 vs 21.45 off-setpoint gens vs baseline 20.80). A feature present in 100% of both classes separates nothing. Deep misses are also unconcentrated: 32 distinct outaged elements / 25 argmin buses for ridge (top shares 8.6% / 10.3%), 54 / 31 for histgb (4.7% / 15.1%). The artifact supports A, not B.
**separate caveat (not part of this pair):** A's word "cannot" is stronger than the artifact licenses — `qlimit_class.json` shows one candidate signature fails to separate, which is not a proof of unpredictability.

## PAIR 4
**A:** Barrier-height inequality: a miss requires overshoot `p̂ − Y > q̂ + d`; at fixed coverage q̂ is set by the model's error scale, so the less accurate model buys a taller barrier and should miss less.
**B:** The observed orderings.
**why they would conflict:** A predicts the model with the larger q̂ misses fewer, uniformly.
**verdict:** RECONCILABLE as an identity, CONTRADICTION as a predictor of ordering — it gets case118 right and case30-thermal exactly backwards.
**evidence:** The inequality itself is a tautology and always holds. Its *ordering prediction* requires the overshoot distribution to be held fixed across models, which it is not.
- case118 @0.90: ridge q̂ .00520 vs histgb .00229 (2.27× taller); ridge misses 2.96% vs 4.72%. **Predicted correctly.**
- case30-thermal @0.90: ridge q̂ .00697 vs histgb .00236 (2.95× taller — a *larger* ratio than case118); ridge misses 6.09% vs 2.23%, i.e. 2.7× **more**. **Predicted backwards.**
- 2C benign→marginal @0.90: ridge q̂ .0041 vs histgb .0022 (1.86× taller); ridge misses 5.01% vs 2.46%. **Predicted backwards.**
- 2C benign→benign @0.70: ridge q̂ .0004 vs histgb .0002 (2× taller); ridge misses 15.58% vs 13.32%. **Predicted backwards.**

Same sign of the q̂ ratio, opposite sign of the miss ordering, on the same 5-seed protocol. The suppressed term is the overshoot tail, and the artifacts quantify it directly: at 0.90 on case118, `share_below_qhat` is 0.737 (ridge) vs 0.552 (histgb) [`data/missed_depth.json`], and the paper's own escalation-ceiling argument at line 235 says ridge predicts below the limit more often (ceiling 74.9% vs 82.8%). So on case118 ridge wins by *bias* (it under-predicts more, flagging more), not by band height; the q̂ story is a coincidence of that network. On case30-thermal the bias runs the other way and the taller band cannot recover it.

---

## Additional contradictory pairs found

**PAIR 5 — the N-1 framing vs. the sampler.**
A: "As long as the test cases and calibration cases come from the same type of condition (a single-element outage) …" [`report/paper_current_STS.tex:116`]; "Our claims of safety are only true for N-1 contingency cases, since we did not test N-2 cases." [line 262]; the dataset description at line 104 mentions only load/generation multipliers and "186 contingencies representing single-element failures."
B: 374 of 1,500 base scenarios (24.93%) and 69,532 of 278,955 N-1 rows (24.93%) carry a generator out of service **in addition to** the outaged branch — an explicitly two-element state, drawn at `P_GEN_OUT = 0.3` in `feasibility/generate_dataset.py:28,128`. [`data/sampling_audit.json`]
Why they cannot both hold: a quarter of every calibration and test set is two-element, so "we did not test N-2" is false and the exchangeability argument is stated over a population the paper does not describe. Verdict: **CONTRADICTION.** The gen-out subpopulation is also not distributionally inert: violation rate 18.24% vs 17.22% (+1.01 pp), boundary-strip share 58.10% vs 56.45% (+1.64 pp).

**PAIR 6 — the manuscript's case30 paragraph vs. the preregistered decision rule.**
A: "on the IEEE 30-bus network simulated using the same configuration, 20.0% of contingencies approach the threshold, whereas another 28.8% fall below it, so the same missed rate gives 8.96±0.91% escalations and an 11.27±1.02 times speedup." [`report/paper_current_STS.tex:260`] — these are case30-**published** (`data/case30_frozen.json`: 20.0146, 28.8081, 0.089593, 11.2653).
B: The preregistered, non-revisable decision rule [`notes/preregistration.md:214-222`]: if the corrected network yields a converged calibrated gate with violation rate in [0.5%, 40%], it **REPLACES** the current case30 figures. case30-thermal gives violation rate 15.397%, boundary mass 7.086%, saturation 84.603% — inside the band. Meanwhile case30-published is thermally infeasible: base-case max line loading 111.83%, and **100.0%** of 4,920 sampled N-1 contingencies exceed 100% loading, median 154.7%, max 490.4% [`data/thermal_check.json`, case30; corroborated at `notes/writing-numbers.md:26`].
Why they cannot both hold: the rule fires, so line 260 should carry 7.09% / 15.40% and the case30-thermal crossing (0.96, 4.86% esc, 21.46×), not the superseded set. Verdict: **CONTRADICTION.** Note the replacement also flips the two-network narrative: boundary mass drops from 20.0% to 7.1%, strengthening the distribution-dependence argument while destroying the model-ordering claim (Pair 2).

**PAIR 7 — coverage validity claimed within N-1 vs. 2C.**
A: "As long as the test cases and calibration cases come from the same type of condition (a single-element outage), the true voltage remains at or above the lower bound with the desired probability." [`report/paper_current_STS.tex:116`], with shift risk deferred entirely to the N-1→N-2 case.
B: With calibration and test both entirely N-1 and differing only in pre-outage `n0_min_vm` stratum, ridge empirical coverage is 0.7953 against a 0.90 target (benign cal → marginal test) and 0.9312 (marginal cal → benign test). [`data/drift_n0_stratum_long.parquet`]
Why they cannot both hold: A makes "single-element outage" the sufficient condition for coverage; B breaks coverage by 10 points without leaving it. Verdict: **CONTRADICTION.** Scope note: histgb holds (0.8960 / 0.9022) in the same cells, so the failure is model-specific, and the 2D element-type and 2E loading-tilt tests do **not** reproduce it (2D ridge coverage 0.893–0.895 across all four cells; 2E ridge 0.893–0.895 across all three cells) — the vulnerable axis is the pre-outage voltage stratum specifically.

**PAIR 8 — "over-voltage is inert" vs. the case118 audit.**
A: `CLAUDE.md` §5, "Voltage binds, not thermal: … over-voltage is inert → the band is ONE-SIDED"; the manuscript lists over-voltage as merely an unchecked scope item [`report/paper_current_STS.tex:262`].
B: On case118, 73.4% of N-0 base states and 73.1% of N-1 rows exceed 1.05 pu, max 1.1529; 5.7% exceed 1.06. [`data/thermal_check.json`, case118.overvoltage]
Why they cannot both hold: "inert" means the constraint never binds; it binds in ~3 of every 4 rows. Verdict: **CONTRADICTION** with the convention as written in `CLAUDE.md`. It does not by itself invalidate the one-sided band (the *target* is min voltage, and the one-sidedness follows from that), but it does mean the accepted base cases are not feasible states, and `notes/preregistration.md:68-70` records the same observation as already-known.

**Non-conflicts I checked and cleared:** the 0.96 comparison at line 231 (0.14% vs 1.36%) matches `tradeoff_curve_v2.json` exactly; the 74%/55% within-one-band shares match `missed_depth.json` seed-means (0.737 / 0.552); 0.0915 pu and the 0.8485 bus both appear at target 0.90 in `missed_depth.json` (ridge seed 2, histgb seeds 1–3), so the Fig. 3 caption is correctly scoped; the 3.29×/2.04× speedups at line 231 match. One presentational asymmetry worth noting, though not a contradiction: line 260's "11.27 times" is the histgb crossing while case118's headline sub-1% number is the ridge crossing — the cross-network comparison silently switches model family, and case30-published's ridge crossing gives only 2.98×.
---

### AGENT 4 of 4 — completeness-stages — VERBATIM

## Verification method

Every claim below is from the artifact/manifest bytes. I verified all 12 `content_sha256` fields against a fresh SHA-256 of the file — **all 12 match**, so no artifact has drifted from its manifest.

---

# Checklist by stage

Legend: P = present, A = absent, PAR = partial.

| | 2A thermal | 2B sampling | 2C n0 | 2D elem | 2E tilt | 2F qlimit | 2H case30_thermal | dataset.manifest |
|---|---|---|---|---|---|---|---|---|
| split rows | n/a | n/a | **P** | **P** | **PAR** | A | **P** | n/a |
| split scenarios | n/a | n/a | **A** | **A** | **A** | **A** | **A** | P (1500) |
| seeds | n/a | n/a | PAR | PAR | PAR | PAR | PAR | **A** |
| solver tolerance | **A** | **A** | **A** | **A** | **A** | **A** | **A** | **A** |
| HP space + selection metric | n/a | n/a | **A** | **A** | **A** | **A** | **A** | n/a |
| feature encoding / count | n/a | n/a | **A** | **A** | **A** | **A** | **A** | A |
| dispersion on every number | **A** | **A** | **P** | **P** | **P** | PAR | PAR | n/a |
| hardware | P | P | P | P | P | P | P | P |
| software versions | P | P | P | P | P | P | P | P |

### Evidence

**Split sizes.** Rows only, never scenarios. `data/drift_n0_stratum_long.parquet` and `data/drift_element_type_long.parquet` carry `n_cal` and `n_test` per row (2C: 26409/29382 cal, 26037/29752 test; 2D: 51900/3891 cal, 51900/3889 test — these sum to 55791 = the full cal split, a good internal check). **`data/drift_loading_tilt_long.parquet` has no `n_cal` column at all** — 2E's calibration size is not in the artifact. `data/qlimit_class.json` has no split sizes of any kind. `data/case30_thermal/case30_thermal_frozen.json` has `n_test_per_seed = [12300]×5` and per-record `n_test`, but no cal or train size. Scenario counts appear in exactly one place in the repo, `data/splits.json` (`n_scenarios: {train:900, cal:300, test:300}`), which is **seed 0 only** and is not referenced by any Stage-2 manifest.

**Seeds.** PARTIAL everywhere: the *value* is recorded (a `seed` column in each drift parquet, `per_seed_depth[].seed` in 2F, `records[].seed` in 2H, `run_settings.seed: 100` for the 2H build). *How they are set* is only in source, never in an artifact: `scripts/drift_tests.py` uses `for seed in range(SEEDS)` feeding both `ms.make_splits(groups, seed)` and `T.fit_one(..., seed)`, plus a separate `np.random.default_rng(1000 + seed)` for the 2E tilt resample; `case30_thermal_gate.py` additionally uses `T.INNER_SEED_OFFSET + seed` for the inner split. None of the three RNG streams is named in any manifest. `data/dataset.manifest.json` is honest that the case118 seed is unrecoverable — it lists it under `provenance_class.unknown`.

**Solver tolerance — ABSENT project-wide.** `feasibility/manifest.py:4` is `SOLVER = dict(enforce_q_lims=True, numba=True, init="dc", algorithm="nr")`, replicated verbatim at `scripts/thermal_check.py:35`. `tolerance_mva` and `max_iteration` are never passed to `pp.runpp` in `feasibility/` or `scripts/`, so pandapower's defaults are in force and are recorded nowhere. Every manifest's `solver` block is complete as written and still under-specifies the numerics.

**Hyperparameters — ABSENT in all seven Stage-2 artifacts.** `scripts/classical_manifest.py:build_manifest` accepts a `model_config` argument defaulting to `None`; **every Stage-2 caller omits it**, so all seven manifests read `"model_hyperparameters": null`. This is a direct miss against the CLAUDE.md guard "manifest beside every new artifact, *including the model hyperparameters that produced it*." The worst case is 2H: `scripts/case30_thermal_gate.py` runs a live M2 search (`T.search_one_family` → `T.select_best` → `T.find_config`) and stores the winner in `phase_a[(family,seed)]["tag"]`/`["config"]` — then **never writes either into `out`**. The selected configuration for the thermal case30 headline is discarded at process exit. 2C/2D/2E/2F instead read a stored config via `m2_config(tuned, family, seed)` from `data/tuned_metrics.json`, but neither the config nor the path to it appears in their manifests (`run_settings.source` names only `data/dataset.parquet`). Search space (`RIDGE_ALPHAS = logspace(-3,4,15)`, 26 histgb candidates, `N_RANDOM_HISTGB=24`, `SEARCH_SEED=0`) and selection metric (M2 = maximise avoided-solve fraction subject to `INNER_MISSED_CEIL=0.01`, ties broken on inner MAE) exist only in `feasibility/tune_surrogates.py`.

**Feature encoding/count — ABSENT in every artifact.** `make_splits.load_dataset` + `build_design_matrix` + `select_features` all `print(...)` their shapes to stdout and return; nothing is persisted. Grepping all of `data/*.json` and `data/*/*.json` for `n_features`, `feature_count`, `kept_cols`, `scenario_features` returns zero hits. So the one-hot branch encoding, the zero-variance drop, and the final column count behind every Stage-2 number are unrecorded.

**Missing manifest.** `data/drift_loading_tilt_diagnostics.json` **has no manifest** — `scripts/drift_tests.py` writes it with a bare `json.dump` while its sibling parquet gets `cm.build_manifest`. Violates the standing "manifest beside every new artifact" guard.

**Missing invocation.** `scripts/thermal_check.py` reads `--max-scenarios` from `sys.argv`, and `data/thermal_check.manifest.json` records no invocation string — only `run_settings.sources`. The sample size survives only because `thermal_sweep()` writes it into the artifact body. Contrast `data/dataset.manifest.json`, which does record `run_settings.invocation`.

---

# (1) Single-seed / dispersion-free numbers presented as pooled

**Nothing is a single seed masquerading as pooled in 2C/2D/2E/2H-frozen** — those are genuinely per-seed. The real defect is a different one: several conclusion-bearing scalars have **no dispersion and no per-seed breakdown anywhere in the file**, because the experiment was never run more than once.

**`data/qlimit_class.json` — the worst case.** `per_seed_depth` exists (5 entries per model, with `q_hat`, `n_missed`, `n_deep`, `max_depth`, `median_depth`). But the fields that carry the stage's actual claim are pooled scalars with **no per-seed counterpart in the file**:
- `per_operating_point.{ridge,histgb}.offsetpoint_gens.{mean,median,min,max,share_with_any}`
- `.min_hops.{mean,median,share_within_2}`
- `.n_deep_total`, `.n_distinct_elements`, `.top_element_share`, `.deep_elements[].share`, `.deep_argmin_buses_ieee[].share`

The comparison that answers Stage 2F's question is `baseline_all_n1_rows.offsetpoint_gens_mean = 20.799` versus `ridge.offsetpoint_gens.mean = 21.328` — a gap of ~0.53 generators, reported with **no std on either side**. Per the project's own std rule, that difference is unevaluable as stated. Worse, these pools are unions over 5 seeds' deep misses (n=58 ridge, n=106 histgb), and the 5 test splits are independent 300-scenario draws from the same 1500 scenarios, so they overlap heavily — the pool is not 58 independent observations, and treating element/bus concentration shares (`top_bus_share = 0.1034` on 6 of 58) as if it were will overstate concentration.

**`data/case30_thermal/case30_thermal_frozen.json` — `crossings_first_below_1pct_missed`.** `scripts/case30_thermal_gate.py` computes these as `np.mean` over the 5 seeds and stores only the mean: `ridge {coverage_target:0.98, missed_viol:0.005145, escalation:0.3783, net_speedup:2.649}`, `histgb {0.96, 0.009094, 0.04862, 21.457}`. No std stored. This is genuinely pooled, not single-seed, and **per-seed values are fully recoverable from `records[]` in the same file** — so it's a presentation gap, not a provenance one. Note `histgb`'s crossing sits at `missed_viol = 0.00909`, within a whisker of the 0.01 threshold that defines it; without a std, whether the crossing is at 0.96 or 0.97 is not decidable from the artifact. The four headline metrics beside it *do* carry `_std` and `n_*_per_seed` — that block is the model the rest should follow.

**`data/thermal_check.json` — entirely dispersion-free, no seed concept.** `thermal_sweep.line_loading.{share_above_100, share_above_95, median, p90, max}` are point estimates over one non-random 120-scenario prefix, with no CI, no bootstrap, no repetition. `share_above_100 = 1.0` is saturated so a CI would be one-sided, but `median = 154.7` and `p90 = 192.5` are ordinary estimates quoted bare.

**`data/sampling_audit.json` — dispersion-free by construction.** All quantities are full-population reads of a fixed 280,500-row parquet, so per-seed variation genuinely does not apply. But `distribution_by_outage_status.delta.violation_rate_pp = 1.013` and `.boundary_strip_pp = 1.642` are differences between two subgroups (n=69,532 vs n=209,423) reported with **no standard error**, and the file draws no conclusion from them — which is the right call. The file is also commendably explicit about what it cannot do: `acceptance_effect.interpretation_note` states the rejection rate by outage status "CANNOT BE COMPUTED from this artifact."

**`data/case30_thermal/h2_range_sweep.json`.** Every acceptance rate rests on `n_draws_per_candidate: 200` at a single `seed: 100`, no repetition. The window that was selected (`lo:0.87`) came from a rule (`acceptance rate >= 0.20 AND max base loading <= 100`) evaluated on those single-seed 200-draw estimates. The `n1_probe` sub-objects are worse: at `lo:0.93` the probe reports `violation_rate: 0.1585` and `boundary_mass: 0.0732` from **2 accepted bases / 82 contingencies**. Those are scalars from n=2 with no dispersion. They did not drive the selection rule, but they sit in the artifact looking like measurements.

**`data/case30_thermal/h3_build_stats.json`** is a single build at seed 100 — scalars throughout (`acceptance_rate: 0.1863`, `n1_loading.share_above_100: 0.2148`). The `n1_loading` block is a full-population number over all 61,500 rows, so it needs no dispersion; the acceptance rate is single-seed and reads as exact.

---

# (2) Conclusion from a sample where the population was available

**Yes — one case, and the artifact discloses it.**

`data/thermal_check.json` → `networks.case30.thermal_sweep`:
- `n_scenarios_swept: 120` of `n_base_scenarios_in_dataset: 1500` = **8.0% of base scenarios**
- `n_contingencies_solved: 4920` of the 61,500 N-1 rows I counted in `data/case30_dataset.parquet` = **8.0% of contingencies**
- `elapsed_s: 416.6`, so the full population would have cost roughly 87 minutes — expensive, but entirely available. The parquet was on disk, complete, at run time.

**Is it stated inside the artifact? Yes, unambiguously.** The file leads the block with `"coverage": "SAMPLE - NOT a full sweep"`, gives the denominator in `n_base_scenarios_in_dataset`, and adds `"sample_note": "first 120 of 1500 base scenarios in dataset order, not a random sample; shares below are estimates over that prefix"`. `scripts/thermal_check.py:188-195` derives that label from `is_sample`, so it cannot silently degrade to "FULL SWEEP". This is the strongest disclosure practice in the whole set.

Two things temper how much it matters, and one sharpens it:
- The reported statistic is saturated — `share_above_100 = 1.0` on 4920/4920. A conclusion of "the published case30 dataset is thermally infeasible essentially everywhere" is robust to the missing 92%.
- I checked the prefix for representativeness: base `scenario_id` is strictly monotone (`100000000, 100000001, ...`), and the prefix-120 vs full-1500 means are `n0_min_vm` 0.95158 vs 0.95153 and `agg_loading` 1.06110 vs 1.05950. Dataset order tracks generation order from an i.i.d. sampler, so the prefix is behaviourally random — but the artifact correctly refuses to claim that, and no formal guarantee is available.
- Sharpening it: `median = 154.7` and `p90 = 192.5` are **not** saturated, and those are ordinary estimates on 8% of an available population with no CI. If any of the three tail numbers is quoted in prose, that is the one to run in full or drop.

**No other instance found.** The 2A case118 thermal sweep was *skipped*, not sampled, and the artifact gives the reason inline (`"line_verdict='UNDEFINED (rating populated but PLACEHOLDER)'; a loading sweep against a placeholder or absent rating measures nothing and would report a misleading zero"`) — the correct refusal, backed by `line_max_i_ka.n_distinct: 2` and `implied_mva_min/max: 9900.0`. 2B, 2C, 2D, 2E, 2F and the 2H gate all run on their full available populations. The 2H `h2_range_sweep` samples 200 draws per window, but there the population is the infinite draw distribution, not a stored file — that is estimation, not undersampling.

---

# (3) Manifest schema partition

**Schema B (all four of `apa_citation`, `input_sha256`, `generating_script`, `content_sha256`) — 2 files, both from Stage 1:**
- `data/fig_floor.manifest.json`
- `data/fig_identity.manifest.json`

Both are emitted by `scripts/sweep_figures.py` and are the only manifests in the repo that name their producer (`generating_script`), hash their *input* (`input_sha256` of `data/sweep_results_long.parquet`), pin the script blob (`script_git_blob_sha`, plus an honest `script_tracked_in_git: false`), timestamp the run (`generated_utc`), and cite a dependency (`apa_citation` for Matplotlib). `fig_floor` also embeds `rendered_numbers` so the figure's contents are auditable without re-running — including `requested_6p6pct_floor: {found: false, note: "..."}`, a recorded refusal to draw a number that did not exist.

**Schema A (environment-only) — every other manifest in the repo, 64 files.** I scanned all `data/*.manifest.json` and `data/*/*.manifest.json`: zero hits for `apa_citation`, `input_sha256`, or `generating_script` outside those two. This is structural, not accidental: `scripts/classical_manifest.py:build_manifest` composes `mf.build_manifest()` + `git_commit` + `artifact` + `content_sha256` + `run_settings` + `model_hyperparameters` and has no parameter for any Schema-B field.

Schema A splits in two:

*A-with-content-hash* (has `content_sha256`, so the artifact is tamper-evident) — includes **all eight artifacts in your scope**: `thermal_check`, `sampling_audit`, `drift_n0_stratum_long`, `drift_element_type_long`, `drift_loading_tilt_long`, `qlimit_class`, all five `case30_thermal/*`, and `dataset.manifest.json` (which carries two — one in the standard slot, one inside `provenance_class.field_provenance`). Plus `bases_clearing_0p95`, `break_even`, `bus_convention_map`, `case30_dataset`, `case30_frozen`, `case30_prediction`, `case30_tradeoff_curve`, `classical_predictions_meta`, `classical_screen_metrics`, `comparison_curve`, `comparison_curve_v2`, `deepest_miss_case`, `element_conditional_escalation`, `escalation_at_095`, `flag_confusion_long`, `frozen_poster_numbers_v2`, `miss_depth_v2`, `miss_depth_v2_cdf`, `miss_mechanism`, `miss_tail_counts`, `missed_depth`, `mondrian_element_long`, `nonconverged_gate`, `parallel_speedup`, all 7 under `data/poster/`, `qlims_off_check`, `sweep_results_long`, `tail_metric_config`, `tradeoff_curve_v2`, `tuned_frontier`, `tuned_metrics`, `tuning_search`.

*A-without-content-hash* (env block only — no integrity check on the artifact at all): `archive_clip/screener_metrics`, `archive_clip/tradeoff_curve`, `bus_layout`, `case57_feasibility`, **`frozen_poster_numbers`**, `paper_provenance`, `probe_alt_networks`, `quintile_boundary_mass`, `safety_operating_points`, **`screener_metrics`**, `solve_time`, `splits`, `tradeoff_curve`. Flagging two of these specifically: `data/frozen_poster_numbers.manifest.json` and `data/screener_metrics.manifest.json` are the manifests for the two **read-only frozen** headline files, and they are the thinnest in the repo — no `content_sha256`, no `git_commit`, no `run_settings`. The freeze is enforced by a hook, not by a hash; nothing in the artifact pair would detect an out-of-band edit.

---

# What I'd fix, ranked

1. **Persist the M2 config in 2H.** `scripts/case30_thermal_gate.py` selects hyperparameters at runtime and throws them away. The headline `escalation_mean`/`net_speedup_mean` for thermal case30 are currently not reproducible from the artifact alone. Add `phase_a[(f,s)]["tag"]`/`["config"]` to `out`, or pass `model_config=` to `cm.write_with_manifest` — the parameter already exists and is unused.
2. **Give 2F a per-seed breakdown of the class signature.** `offsetpoint_gens`, `min_hops`, and the element/bus concentration shares are the stage's answer and carry no dispersion. Emit them per seed alongside `per_seed_depth`, and state that the 5 test splits overlap so the pooled n is not an independent n.
3. **Write the missing manifest** for `data/drift_loading_tilt_diagnostics.json`.
4. **Either run the case30 thermal sweep in full (~87 min) or quote only `share_above_100`.** The saturated share survives 8% coverage; `median` and `p90` do not.
5. **Record feature count and split scenario counts** in `run_settings`. Both are already computed and printed; capturing them is a two-line change in `classical_manifest.build_manifest` callers.
6. **Add `tolerance_mva` and `max_iteration` explicitly to `SOLVER`** in `feasibility/manifest.py:4` so the pinned numerics are pinned in fact, not by pandapower's default.
7. **Add `content_sha256` to the two frozen headline manifests.** They are the most load-bearing files and the least protected.
---

## CORRECTION C-4 — the case30 thermal sweep in 2A was computed against a fabricated operating point

**Raised:** 2026-08-19T15:40:00Z, by the `code-audit` subagent (HIGH), independently
re-verified in the main session before acceptance.

**The defect.** `scripts/thermal_check.py:159-160`:

```python
net.load["p_mw"] = row[load_p].to_numpy(dtype=float)[:len(net.load)]
net.load["q_mvar"] = row[load_q].to_numpy(dtype=float)[:len(net.load)]
```

`pload_i` / `qload_i` are written by `feasibility/generate_dataset.py:160-165` as **per-BUS**
aggregates, indexed `0..n_bus-1`. `net.load` rows are **not** indexed by bus. On case30 there
are 30 bus columns and 20 loads, and `net.load.bus` is
`[1,2,3,6,7,9,11,13,14,15,16,17,18,19,20,22,23,25,28,29]`. Taking the first 20 bus columns
positionally gives every load a different bus's demand and silently discards the demand at
buses 20-29.

**Independently re-verified in the main session**, scenario 0 of `data/case30_dataset.parquet`:

| | value |
|---|---|
| total load in the features | 203.9502 MW |
| as-coded (first 20 bus columns) | **154.4838 MW** |
| bus-mapped (correct: `vals[net.load.bus]`) | 203.9502 MW |
| loads receiving the wrong bus's demand | **20 of 20** |

The correct idiom exists elsewhere in this repo — `scripts/classical_screen.py:18-29` rebuilds
one load per bus so that index == bus. `thermal_check.py` is the only site that does not.

**Superseded numbers.** The Stage 2A block reports, for case30-published:

> share>100% = 1.000000, median 154.72, p90 192.48, max 490.45 (SAMPLE 120/1500)

The agent's paired replay on a 15-scenario prefix, as-coded vs bus-mapped:

| | share > 100% | median | p90 | max |
|---|---|---|---|---|
| as coded | 1.0000 | 162.14 | 184.02 | 474.11 |
| bus-mapped (correct) | 1.0000 | **124.08** | **136.57** | **195.38** |

**The qualitative verdict survives; every quantile does not.** `share_above_100 = 1.000000`
holds under both. The median, p90 and max in `data/thermal_check.json`
`networks.case30.thermal_sweep` are **WRONG and must not be quoted**.

**Blast radius — what is and is not affected.** Traced in the main session:

| quantity | path | status |
|---|---|---|
| case30 N-0 base max loading **111.83%** | `rating_audit`, `pp.runpp` on the nominal network — no feature assignment | **UNAFFECTED** |
| case118 / case30 rating audits and PLACEHOLDER verdicts | same clean path | **UNAFFECTED** |
| over-voltage shares (73.40% / 73.14% / 0.00%) | read directly from the parquet | **UNAFFECTED** |
| case30-published sweep median / p90 / max | the buggy path | **WRONG** |
| case30-published sweep `share_above_100` = 1.0 | the buggy path, but robust to it | survives, still to be re-derived |
| H2 acceptance sweep, zero-acceptance finding | `case30_thermal.py` via `G.solve_n0` -> `apply_scenario` | **UNAFFECTED** |
| case30-thermal N-1 loading 0.214846 / median 97.66 / max 145.80 | `case30_thermal_build.py` via `G.solve_n0` | **UNAFFECTED** |
| everything in 2B, 2C, 2D, 2E, 2F, and the gate results | never touch this code path | **UNAFFECTED** |

`apply_scenario` (`generate_dataset.py:136-137`) assigns `params["p_new"]`, which is per-LOAD
and correct. Every path that goes through `G.solve_n0` is clean. Only `thermal_check.py`'s
sweep reconstructs the operating point from per-bus features, and only it is wrong.

**Why the verifier passes did not catch this.** Both prior verifier passes recomputed values
*from the artifact*. The artifact inherits the defect, so recomputation reproduces the wrong
number faithfully. This is exactly the class the `code-audit` agent was commissioned to find,
and it is the argument for auditing code as well as artifacts.

**`notes/writing-numbers.md` row 51** quotes only `share_above_100` = 1.000000, which
survives. A caveat has been appended there. No other row is affected.

**NOT FIXED.** The script is not corrected and the sweep is not re-run in this turn. Doing so
is a code change plus a compute job; flagging it is the reporting obligation, fixing it is a
decision.

---

## C-5 — H2's chosen range fails its own selection criterion at scale (MEDIUM)

Raised by `code-audit`. `scripts/case30_thermal.py` (H2 sweep) and
`scripts/case30_thermal_build.py` (H3 build) both use **seed 100** with the same config and
the same `sample_scenario` path, so `np.random.default_rng(100)` produces the same stream. The
41 accepted scenarios behind H2's acceptance estimate are **bit-identical to the first 41
scenarios of `data/case30_thermal/dataset.parquet`** (agent verified `np.allclose` over all 41
`agg_loading` values).

Consequence: the selection rule is `acceptance_rate >= 0.20`; the chosen range [0.87, 0.99]
passes at **0.205** on that 200-draw prefix, but `h3_build_stats.json` reports the true rate
for the same range at scale as **0.186335** (1500/8050). **The chosen range fails its own
selection criterion once measured at scale.** Both numbers are correctly stored and a
recompute from either artifact reproduces both — the discrepancy is invisible to
artifact-level verification.

The stated fix is to use a different seed for the sweep than for the build. Not applied.

Note this does not invalidate the H0 decision rule outcome: that rule requires **acceptance
rate >= 5%**, and 18.63% clears it comfortably. It is H2's own >= 20% range-selection
threshold that is not met at scale.

---

## C-6 — the 2E tilt weights are not the likelihood ratio of the tilt actually applied (MEDIUM)

Raised by `code-audit`. `scripts/drift_tests.py:181-187` normalises by `a.min(), a.max()` of
whichever array it receives, so `w_cal` uses the calibration split's extremes while `w_te` —
the tilt actually resampled onto the test set — uses the test split's. The two ranges differ,
so the weight handed to `weighted_qhat` is not proportional to `dP_test/dP_cal`. The weight
function is also defined by data-dependent extremes of a random subsample, so it is not a
fixed tilt and varies by seed.

Agent-computed `used/correct` weight ratio across the calibration set: seed 0 **3.67x**
(cal range 0.1096 vs test 0.0765), seeds 1-3 1.32-1.39x, seed 4 1.006x.

Effect on the published `tilted_test_weighted_cal` cell, seed 0 (the agent reproduced the
stored `q_hat` and `escalation` exactly, confirming the artifact carries the defect):

| model | target | q_hat as coded | q_hat corrected | escalation | coverage_emp |
|---|---|---|---|---|---|
| ridge | 0.90 | 0.005592 | 0.005640 | 54.26% -> 54.65% | 0.9163 -> 0.9176 |
| histgb | 0.90 | 0.002533 | 0.002693 | 37.00% -> 38.96% | 0.9091 -> 0.9129 |
| histgb | 0.95 | 0.004387 | 0.004505 | 55.44% -> 56.15% | 0.9472 -> 0.9487 |

Up to ~2 pp on escalation, ~0.4 pp on empirical coverage. **The direction is anti-conservative
— the band is too narrow — which is the direction that matters for a safety claim.**

This does not change 2E's headline finding (the tilt is too weak to break coverage, because
the sampler's loading window is 7.7 points wide), but the weighted cell is not a clean test of
weighted conformal and should not be presented as one. Not fixed.

---

## C-7 — the std-rule objection to 2C does NOT apply to the per-model claim; it applies to the agent's pooled statistic

The `physics-stages` agent reports the 2C cell as cov@0.90 = **0.8456 (sd 0.0549)** and
concludes that at 0.95 "by the project's own std rule the result is not a finding". That
statistic **pools ridge and histgb into one number.** Pooling a model that breaks with one
that does not inflates the sd and destroys the signal — the 0.0549 is the *between-model*
spread, not seed noise.

Recomputed per model in the main session, `data/drift_n0_stratum_long.parquet`, population std
(ddof=0) over 5 seeds:

| model | target | control mean (sd) | shifted mean (sd) | gap | larger sd | std rule |
|---|---|---|---|---|---|---|
| **ridge** | 0.90 | 0.8964 (0.0114) | **0.7953 (0.0180)** | **0.1011** | 0.0180 | **SURVIVES (5.6x)** |
| **ridge** | 0.95 | 0.9505 (0.0034) | **0.9291 (0.0112)** | **0.0214** | 0.0112 | **SURVIVES (1.9x)** |
| histgb | 0.90 | — | — | −0.0029 | 0.0152 | **FAILS** |

Ridge per-seed coverage at 0.90, shifted: 0.8036, 0.8227, 0.7983, 0.7807, 0.7712 — every seed
below 0.83, none overlapping the control's range (0.8840–0.9159).

The headlined shortfall statistic likewise survives: ridge benign→marginal **0.164335**
(sd 0.013285) against control **0.008282** (sd 0.017306) — gap 0.156 against a larger sd of
0.017.

**So the ridge collapse stands.** What the agent's objection correctly establishes is a
different and still-important point:

**histgb's 2C shift FAILS the std rule** (gap −0.0029 against sd 0.0152) and must be stated as
**indistinguishable from zero**, not as "a small effect of 0.0176". My earlier phrasing
("histgb is essentially unaffected") was directionally right but should be tightened to
"no effect distinguishable from seed noise".

**The agent's substantive findings on 2C, which I accept and which stand:**

1. **2C is a voltage-MARGIN split, not an operating-point shift.**
   `corr(n0_min_vm, agg_loading)` = **−0.0724** over base cases — the split is nearly
   orthogonal to load. What moves is boundary-mass density ρ: **66.9/pu (benign) vs 160.5/pu
   (marginal)**.
2. **90% of the post-contingency shift is inherited from the base offset.** Contingency
   response is statistically identical in both strata (mean drop 0.004439 vs 0.003972; median
   0.0 in both). The strata do not respond differently to outages — they start 0.005 pu apart.
3. **The design is "more boundary vs less boundary", not "boundary vs not":** 33.5% of benign
   N-1 rows are already inside [0.94, 0.945).
4. **Two real confounds to state if written up:** generator-outage prevalence differs by
   **+4.8 pp** (0.2253 vs 0.2733, z = 2.15), so the marginal stratum carries more two-element
   states; and argmin-bus composition shifts toward buses 75/52/106. `agg_loading` differs at
   p = 0.012 but by 0.13σ — report as controlled-but-nonzero.

Load level and contingency response are affirmatively **cleared** as confounds by (1) and (2).

## C-8 — what case30-thermal actually demonstrates is not what case30-published demonstrated

From `physics-stages`, replaying the H3 draw loop exactly (seed 100, 8050 draws, 1500
accepted, 5710 thermal / 840 voltage rejections — reproduces `h3_build_stats.json`):

Base max `loading_percent` among **thermal-accepted** bases: min 81.0, p10 92.0, p25 94.5,
median **96.9**, p75 98.6, p90 **99.4**, max **99.999**. Against all 8050 draws: median 106.2.

**The thermal criterion selects NEAR-LIMIT bases, not low-load ones** — it concentrates the
accepted population just under the 100% rating. Simultaneously it de-stresses the load level
into a window **disjoint** from the published case30's [1.00, 1.12].

Consequence, and it is the one that matters for the two-network argument: **case30-published
and case30-thermal are not the same counter-example.** The published set is a
voltage-marginal, thermally-infeasible network; the thermal set is a thermally-marginal,
load-de-stressed one. Both have low boundary mass relative to case118, but they get there by
different routes.

Also recorded from the same agent, unaffected by C-4: **"thermal-feasible" holds at N-0 only**
— 21.5% of the N-1 states in the regenerated dataset still exceed 100% loading — and the gate
remains voltage-only, so 2H changes the sampler, not the screener.

## C-9 — 2F does not adjudicate what it was built to adjudicate

`physics-stages` swept `SETPOINT_TOL` from 1e-4 to 2e-2: share-with-any-off-setpoint stays at
1.0000 until 2e-2, where it is still 0.9760. There is no tolerance at which "some generator is
off setpoint" becomes rare. Roughly 40% of generators genuinely bind under
`enforce_q_lims=True` with `qscale ~ U(0.60, 1.40)`.

It also computed the baseline my artifact omits — `min_hops` over 4,000 random N-1 rows:
**mean 1.342, share ≤ 2 = 0.8958**. Against ridge deep misses (1.552, 0.8103) and histgb
(0.981, **0.8962**). **The two operating points bracket the baseline and histgb matches it to
three decimals.** No proximity signal, as expected when 20.8 off-setpoint generators are
scattered over 118 buses.

So 2F was built to separate information-absence from statistical-rarity
(`qlimit_class.py:29-33`) and **does not separate them**: a feature present in 100% of rows is
evidence for neither branch. My Stage 2F write-up said 2F "does not refute" the manuscript
claim, which is correct but understates it — 2F does not bear on the question at all.
`data/qlimit_class.json` lacks a `min_hops` baseline field, which is why the artifact could
not show this on its own.

---

## C-10 — 2F's deep-miss pool is not 58 independent observations (completeness-stages)

The 5 test splits are independent 300-scenario draws from the same 1,500 scenarios, so they
**overlap heavily**. `data/qlimit_class.json` pools deep misses across seeds (n=58 ridge,
n=106 histgb) and reports concentration shares off that pool — `top_bus_share = 0.1034` is
6 of 58. Treating an overlapping union as independent observations **overstates
concentration**, which cuts against my own 2F conclusion in the conservative direction (the
class is *even less* concentrated than reported), but the statistic as published is not sound.

Compounding it: every conclusion-bearing scalar in 2F has **no dispersion and no per-seed
counterpart in the file** — `offsetpoint_gens.*`, `min_hops.*`, `n_deep_total`,
`n_distinct_elements`, `top_element_share`, the `deep_elements[].share` list. The comparison
that answers the stage's question is baseline **20.799** vs ridge **21.328** — a gap of ~0.53
generators **with no std on either side**. Under the project's own std rule that difference is
**unevaluable as stated**. `per_seed_depth` exists and carries `q_hat`/`n_missed`/`n_deep`/
`max_depth`, so the fix is available; it was not done.

## C-11 — the case30-thermal histgb crossing is not decidable from its artifact

`data/case30_thermal/case30_thermal_frozen.json` stores
`crossings_first_below_1pct_missed.histgb.missed_viol = 0.009094` — **within a whisker of the
0.01 threshold that defines the crossing** — and stores **no std** beside it. Whether the
crossing is at 0.96 or 0.97 is therefore not decidable from the artifact as written.

I reported "histgb crossing 0.96, 4.86% escalation, 21.46x" as a Stage 2H headline and in
`notes/writing-numbers.md` rows 40-42. **That number should carry this caveat.** Per-seed
values ARE recoverable from `records[]` in the same file, so this is a presentation gap rather
than a provenance one — the adjacent `four_metrics_at_90pct_coverage` block does carry `_std`
and `n_*_per_seed` and is the model the crossings block should follow.

## C-12 — H2's `n1_probe` sub-objects are n=2 scalars that look like measurements

`data/case30_thermal/h2_range_sweep.json`: at `lo = 0.93` the probe reports
`violation_rate = 0.1585` and `boundary_mass = 0.0732` from **2 accepted bases / 82
contingencies**. They did not drive the selection rule (which uses acceptance rate and max
base loading only) but they sit in the artifact looking like measurements. Every acceptance
rate in the sweep also rests on a single `seed: 100` with `n_draws_per_candidate: 200`, no
repetition — compounding C-5.

## C-13 — additional contradictions raised by consistency-stages

Recorded; not resolved. Both sides in the verbatim report above.

- **PAIR 5 — "we did not test N-2" is false.** `report/paper_current_STS.tex:262` states it
  plainly; 24.93% of every calibration and test set is a two-element state. The exchangeability
  argument at line 116 is therefore stated over a population the paper does not describe.
  **CONTRADICTION.**
- **PAIR 6 — the preregistered rule fires against line 260.** The manuscript's case30 paragraph
  carries the published figures (20.0% / 28.8% / 8.96% / 11.27x); the non-revisable rule at
  `notes/preregistration.md:214-222` says the thermal set REPLACES them. **CONTRADICTION.**
  *Caveat added by me:* the agent corroborated with the thermal sweep's median 154.7 / max
  490.4, which **C-4 shows are wrong**. Its point survives on `share_above_100 = 1.0` and the
  111.83% base figure, both unaffected by C-4.
- **PAIR 7 — coverage validity is claimed within N-1 and breaks within N-1.** Line 116 makes
  "same type of condition (a single-element outage)" sufficient for coverage; 2C breaks ridge
  coverage by 10 points **without leaving N-1**. **CONTRADICTION.** Scope: histgb holds, and
  2D and 2E do **not** reproduce it (ridge coverage 0.893-0.895 across all their cells) — the
  vulnerable axis is the pre-outage voltage stratum specifically.
- **PAIR 8 — `CLAUDE.md` §5 "over-voltage is inert" vs 73% of rows above 1.05 pu.**
  **CONTRADICTION with the convention as written.** Does not by itself invalidate the
  one-sided band, since the target is minimum voltage.
- **PAIR 2 detail I had not computed — case30-published has NO safety ordering at 0.90.**
  Ridge 1.49±0.53% vs histgb 1.47±0.20%, a 0.03 pp gap far inside one sigma. So the IV-B title
  "The faster model is not the safer one" holds on **one of three result sets**: case118 yes,
  case30-published no ordering, case30-thermal inverted.
- **PAIR 3 — NOT A CONFLICT.** The agent refutes the earlier physics position on two counts
  and finds the artifact **supports the manuscript's line 262**, not the objection to it. This
  is stronger than my C-9, which said only that 2F does not adjudicate. Both readings are now
  on record.
- **Presentational asymmetry, independently confirming C1-11:** line 260's 11.27x is the
  **histgb** crossing while case118's headline sub-1% number is the **ridge** crossing — the
  cross-network comparison silently switches model family, and case30-published's ridge
  crossing gives only 2.98x.

---

# PAIRED ADJUDICATION

Protocol: two agents per scenario, spawned in ONE turn, blind in round 1. Agent A reads the
derived artifact; Agent B re-derives from raw inputs without seeing A's artifact. Neither may
read `notes/RUN_REPORT.md`, `notes/writing-numbers.md` or `notes/preregistration.md`. Round 2
sends both agents ONLY the two values and the two derivation paths — never the other's
reasoning. Round 3 is a capped single exchange with both full reports. Anything unresolved
after round 3 is recorded UNRESOLVED with both positions in full.

Every round is appended verbatim. No disagreement is summarised into a conclusion.

---

## S1 — 2A thermal + over-voltage (including the C-4 void figures)

### S1 ROUND 1 — Agent A (derived artifact) — VERBATIM

All values below are read verbatim from `data/thermal_check.json` (sha256 first 16: `23d42c7146e0f580`; manifest `content_sha256` matches).

| quantity | value | file | jsonpath | aggregation | sha256(16) |
|---|---|---|---|---|---|
| case118 line max_i_ka n_nan | 0 | data/thermal_check.json | $.networks.case118.rating_audit.line_max_i_ka.n_nan | count of NaN over 173 lines | 23d42c7146e0f580 |
| case118 line max_i_ka n_distinct | 2 | data/thermal_check.json | $.networks.case118.rating_audit.line_max_i_ka.n_distinct | distinct-count over 173 lines | 23d42c7146e0f580 |
| case118 line max_i_ka min | 16.56744250718057 | data/thermal_check.json | $.networks.case118.rating_audit.line_max_i_ka.min | min over 173 lines | 23d42c7146e0f580 |
| case118 line max_i_ka max | 41.41860626795142 | data/thermal_check.json | $.networks.case118.rating_audit.line_max_i_ka.max | max over 173 lines | 23d42c7146e0f580 |
| case118 line implied MVA min | 9900.0 | data/thermal_check.json | $.networks.case118.rating_audit.line_max_i_ka.implied_mva_min | min over 173 lines | 23d42c7146e0f580 |
| case118 line implied MVA max | 9900.000000000002 | data/thermal_check.json | $.networks.case118.rating_audit.line_max_i_ka.implied_mva_max | max over 173 lines | 23d42c7146e0f580 |
| case118 trafo sn_mva n_distinct | 1 | data/thermal_check.json | $.networks.case118.rating_audit.trafo_sn_mva.n_distinct | distinct-count over 13 trafos | 23d42c7146e0f580 |
| case118 trafo sn_mva min | 9900.0 | data/thermal_check.json | $.networks.case118.rating_audit.trafo_sn_mva.min | min over 13 trafos | 23d42c7146e0f580 |
| case118 trafo sn_mva max | 9900.0 | data/thermal_check.json | $.networks.case118.rating_audit.trafo_sn_mva.max | max over 13 trafos | 23d42c7146e0f580 |
| case118 N-0 base loading_percent line_max | 4.475087324056162 | data/thermal_check.json | $.networks.case118.rating_audit.base_case_loading_pct.line_max | max over lines, single N-0 base solve | 23d42c7146e0f580 |
| case118 N-0 base loading_percent line_median | 0.34796764260032675 | data/thermal_check.json | $.networks.case118.rating_audit.base_case_loading_pct.line_median | median over lines, single N-0 base solve | 23d42c7146e0f580 |
| case118 N-0 base loading_percent trafo_max | 3.5892305584092106 | data/thermal_check.json | $.networks.case118.rating_audit.base_case_loading_pct.trafo_max | max over trafos, single N-0 base solve | 23d42c7146e0f580 |
| case118 line_verdict | UNDEFINED (rating populated but PLACEHOLDER) | data/thermal_check.json | $.networks.case118.rating_audit.line_verdict | verbatim string | 23d42c7146e0f580 |
| case118 trafo_verdict | UNDEFINED (rating populated but PLACEHOLDER) | data/thermal_check.json | $.networks.case118.rating_audit.trafo_verdict | verbatim string | 23d42c7146e0f580 |
| case30 line max_i_ka n_nan | 0 | data/thermal_check.json | $.networks.case30.rating_audit.line_max_i_ka.n_nan | count of NaN over 41 lines | 23d42c7146e0f580 |
| case30 line max_i_ka n_distinct | 6 | data/thermal_check.json | $.networks.case30.rating_audit.line_max_i_ka.n_distinct | distinct-count over 41 lines | 23d42c7146e0f580 |
| case30 line max_i_ka min | 0.06842669857062 | data/thermal_check.json | $.networks.case30.rating_audit.line_max_i_ka.min | min over 41 lines | 23d42c7146e0f580 |
| case30 line max_i_ka max | 0.55596692588631 | data/thermal_check.json | $.networks.case30.rating_audit.line_max_i_ka.max | max over 41 lines | 23d42c7146e0f580 |
| case30 line implied MVA min | 15.999999999999458 | data/thermal_check.json | $.networks.case30.rating_audit.line_max_i_ka.implied_mva_min | min over 41 lines | 23d42c7146e0f580 |
| case30 line implied MVA max | 130.00000000000085 | data/thermal_check.json | $.networks.case30.rating_audit.line_max_i_ka.implied_mva_max | max over 41 lines | 23d42c7146e0f580 |
| case30 n_trafos | 0 | data/thermal_check.json | $.networks.case30.rating_audit.n_trafos | count | 23d42c7146e0f580 |
| case30 N-0 base loading_percent line_max | 111.83140586617333 | data/thermal_check.json | $.networks.case30.rating_audit.base_case_loading_pct.line_max | max over lines, single N-0 base solve | 23d42c7146e0f580 |
| case30 N-0 base loading_percent line_median | 26.92413803795224 | data/thermal_check.json | $.networks.case30.rating_audit.base_case_loading_pct.line_median | median over lines, single N-0 base solve | 23d42c7146e0f580 |
| case30 N-0 base loading_percent trafo_max | null | data/thermal_check.json | $.networks.case30.rating_audit.base_case_loading_pct.trafo_max | ABSENT (stored null; no trafos) | 23d42c7146e0f580 |
| case30 line_verdict | RATED (rating appears meaningful) | data/thermal_check.json | $.networks.case30.rating_audit.line_verdict | verbatim string | 23d42c7146e0f580 |
| case30 trafo_verdict | N/A (network has no transformers) | data/thermal_check.json | $.networks.case30.rating_audit.trafo_verdict | verbatim string | 23d42c7146e0f580 |
| case30 thermal_sweep coverage | SAMPLE - NOT a full sweep | data/thermal_check.json | $.networks.case30.thermal_sweep.coverage | verbatim string | 23d42c7146e0f580 |
| case30 thermal_sweep n_scenarios_swept | 120 | data/thermal_check.json | $.networks.case30.thermal_sweep.n_scenarios_swept | count; first 120 of 1500 in dataset order (sample_note) | 23d42c7146e0f580 |
| case30 thermal_sweep n_base_scenarios_in_dataset | 1500 | data/thermal_check.json | $.networks.case30.thermal_sweep.n_base_scenarios_in_dataset | count | 23d42c7146e0f580 |
| case30 thermal_sweep n_contingencies_solved | 4920 | data/thermal_check.json | $.networks.case30.thermal_sweep.n_contingencies_solved | count (120 x 41) | 23d42c7146e0f580 |
| case30 thermal_sweep n_solver_failures | 0 | data/thermal_check.json | $.networks.case30.thermal_sweep.n_solver_failures | count | 23d42c7146e0f580 |
| case30 sweep line_loading n | 4920 | data/thermal_check.json | $.networks.case30.thermal_sweep.line_loading.n | count of contingency records (per-record max loading) | 23d42c7146e0f580 |
| case30 sweep line_loading share_above_100 | 1.0 | data/thermal_check.json | $.networks.case30.thermal_sweep.line_loading.share_above_100 | share over n=4920, prefix sample estimate | 23d42c7146e0f580 |
| case30 sweep line_loading share_above_95 | 1.0 | data/thermal_check.json | $.networks.case30.thermal_sweep.line_loading.share_above_95 | share over n=4920, prefix sample estimate | 23d42c7146e0f580 |
| case30 sweep line_loading median | 154.72382022635077 | data/thermal_check.json | $.networks.case30.thermal_sweep.line_loading.median | median over n=4920 | 23d42c7146e0f580 |
| case30 sweep line_loading p90 | 192.48176405289811 | data/thermal_check.json | $.networks.case30.thermal_sweep.line_loading.p90 | 90th pct over n=4920 | 23d42c7146e0f580 |
| case30 sweep line_loading max | 490.44656024383517 | data/thermal_check.json | $.networks.case30.thermal_sweep.line_loading.max | max over n=4920 | 23d42c7146e0f580 |
| case118 thermal_sweep ran? | skipped: true (did NOT run) | data/thermal_check.json | $.networks.case118.thermal_sweep.skipped | boolean flag | 23d42c7146e0f580 |
| case118 thermal_sweep skip reason | line_verdict='UNDEFINED (rating populated but PLACEHOLDER)'; a loading sweep against a placeholder or absent rating measures nothing and would report a misleading zero | data/thermal_check.json | $.networks.case118.thermal_sweep.reason | verbatim string | 23d42c7146e0f580 |
| case118 OV n0_base n | 1500 | data/thermal_check.json | $.networks.case118.overvoltage.n0_base.n | count of base scenarios | 23d42c7146e0f580 |
| case118 OV n0_base share_above_1p05 | 0.734 | data/thermal_check.json | $.networks.case118.overvoltage.n0_base.share_above_1p05 | share over n=1500 | 23d42c7146e0f580 |
| case118 OV n0_base share_above_1p06 | 0.058 | data/thermal_check.json | $.networks.case118.overvoltage.n0_base.share_above_1p06 | share over n=1500 | 23d42c7146e0f580 |
| case118 OV n0_base share_above_1p10 | 0.0013333333333333333 | data/thermal_check.json | $.networks.case118.overvoltage.n0_base.share_above_1p10 | share over n=1500 | 23d42c7146e0f580 |
| case118 OV n0_base max_vm_max | 1.1222032642156976 | data/thermal_check.json | $.networks.case118.overvoltage.n0_base.max_vm_max | max of per-scenario max vm over n=1500 | 23d42c7146e0f580 |
| case118 OV n0_base max_vm_median | 1.0543519864279756 | data/thermal_check.json | $.networks.case118.overvoltage.n0_base.max_vm_median | median of per-scenario max vm over n=1500 | 23d42c7146e0f580 |
| case118 OV n1 n | 278955 | data/thermal_check.json | $.networks.case118.overvoltage.n1.n | count of N-1 records | 23d42c7146e0f580 |
| case118 OV n1 share_above_1p05 | 0.7313581043537488 | data/thermal_check.json | $.networks.case118.overvoltage.n1.share_above_1p05 | share over n=278955 | 23d42c7146e0f580 |
| case118 OV n1 share_above_1p06 | 0.057367675790001973 | data/thermal_check.json | $.networks.case118.overvoltage.n1.share_above_1p06 | share over n=278955 | 23d42c7146e0f580 |
| case118 OV n1 share_above_1p10 | 0.0015737305300138015 | data/thermal_check.json | $.networks.case118.overvoltage.n1.share_above_1p10 | share over n=278955 | 23d42c7146e0f580 |
| case118 OV n1 max_vm_max | 1.1529085250441442 | data/thermal_check.json | $.networks.case118.overvoltage.n1.max_vm_max | max of per-record max vm over n=278955 | 23d42c7146e0f580 |
| case118 OV n1 max_vm_median | 1.0542520783507079 | data/thermal_check.json | $.networks.case118.overvoltage.n1.max_vm_median | median of per-record max vm over n=278955 | 23d42c7146e0f580 |
| case30 OV n0_base n | 1500 | data/thermal_check.json | $.networks.case30.overvoltage.n0_base.n | count of base scenarios | 23d42c7146e0f580 |
| case30 OV n0_base share_above_1p05 | 0.0 | data/thermal_check.json | $.networks.case30.overvoltage.n0_base.share_above_1p05 | share over n=1500 | 23d42c7146e0f580 |
| case30 OV n0_base share_above_1p06 | 0.0 | data/thermal_check.json | $.networks.case30.overvoltage.n0_base.share_above_1p06 | share over n=1500 | 23d42c7146e0f580 |
| case30 OV n0_base share_above_1p10 | 0.0 | data/thermal_check.json | $.networks.case30.overvoltage.n0_base.share_above_1p10 | share over n=1500 | 23d42c7146e0f580 |
| case30 OV n0_base max_vm_max | 1.0249843220727344 | data/thermal_check.json | $.networks.case30.overvoltage.n0_base.max_vm_max | max of per-scenario max vm over n=1500 | 23d42c7146e0f580 |
| case30 OV n0_base max_vm_median | 1.0165071567189714 | data/thermal_check.json | $.networks.case30.overvoltage.n0_base.max_vm_median | median of per-scenario max vm over n=1500 | 23d42c7146e0f580 |
| case30 OV n1 n | 61500 | data/thermal_check.json | $.networks.case30.overvoltage.n1.n | count of N-1 records | 23d42c7146e0f580 |
| case30 OV n1 share_above_1p05 | 0.0 | data/thermal_check.json | $.networks.case30.overvoltage.n1.share_above_1p05 | share over n=61500 | 23d42c7146e0f580 |
| case30 OV n1 share_above_1p06 | 0.0 | data/thermal_check.json | $.networks.case30.overvoltage.n1.share_above_1p06 | share over n=61500 | 23d42c7146e0f580 |
| case30 OV n1 share_above_1p10 | 0.0 | data/thermal_check.json | $.networks.case30.overvoltage.n1.share_above_1p10 | share over n=61500 | 23d42c7146e0f580 |
| case30 OV n1 max_vm_max | 1.0263452079242976 | data/thermal_check.json | $.networks.case30.overvoltage.n1.max_vm_max | max of per-record max vm over n=61500 | 23d42c7146e0f580 |
| case30 OV n1 max_vm_median | 1.0165154060357846 | data/thermal_check.json | $.networks.case30.overvoltage.n1.max_vm_median | median of per-record max vm over n=61500 | 23d42c7146e0f580 |
| placeholder_rule | a rating is judged PLACEHOLDER if base-case max loading is below 25.0% AND the rating takes at most 3 distinct values (lines), or is a single value at or above 1000 MVA (transformers) | data/thermal_check.json | $.placeholder_rule | verbatim string | 23d42c7146e0f580 |

Source files: `/Users/rajansaha/contingency-screener-research/data/thermal_check.json`, `/Users/rajansaha/contingency-screener-research/data/thermal_check.manifest.json` (sha256 16: `8c8b2835ef71805d`).
### S1 ROUND 1 — Agent B (re-derived from raw inputs) — VERBATIM

Solver config used everywhere below: `pp.runpp(net, enforce_q_lims=True, init="dc", numba=True)`, Newton–Raphson (default) — from `feasibility/generate_dataset.py:149` and `SOLVER` in `feasibility/manifest.py:5`. Interpreter `.venv/bin/python` (pandapower 3.5.4).

| quantity | value | file or source | derivation | aggregation | sha256(16) |
|---|---|---|---|---|---|
| 1. case118 line max_i_ka | n_nan=0; n_distinct=2 (16.56744250718057, 41.41860626795142); min=16.56744250718057; max=41.41860626795142 | `pandapower.networks.case118()` fresh | `net.line.max_i_ka.values`; `np.isnan().sum()`, `np.unique`, min, max | over all 173 lines | n/a |
| 2. case118 implied MVA = sqrt(3)*vn_kv(from_bus)*max_i_ka | min=9900.0; max=9900.000000000002 | same | `vn = net.bus.vn_kv.values[net.line.from_bus.values]`; `sqrt(3)*vn*max_i_ka`. vn_kv ∈ {138, 161, 345}; the two current values pair with the voltage levels to give one constant MVA | over 173 lines | n/a |
| 3. case118 trafo sn_mva | n_distinct=1; min=9900.0; max=9900.0 | same | `net.trafo.sn_mva` (13 trafos), `nunique`/min/max | over 13 trafos | n/a |
| 4. case118 N-0 base-case loading_percent | line max=4.4750873241; line median=0.3479676426; trafo max=3.5892305584 | same, solved | fresh `case118()`, no scenario applied, `runpp(enforce_q_lims=True, init="dc", numba=True)`; `np.nanmax/np.nanmedian` of `res_line.loading_percent`, `np.nanmax` of `res_trafo.loading_percent`. Base total load 4242.0 MW | single deterministic solve | n/a |
| 5. case30 line max_i_ka | n_nan=0; n_distinct=6 (0.06842669857062, 0.13685339714124, 0.27798346294315, 0.29936680624647, 0.38490017945975, 0.55596692588631); min=0.06842669857062; max=0.55596692588631 | `pandapower.networks.case30()` fresh | as in row 1 | over all 41 lines | n/a |
| 6. case30 implied MVA | min=15.999999999999458; max=130.00000000000085 | same | as in row 2; all buses vn_kv=135.0 | over 41 lines | n/a |
| 7. case30 n_trafos | 0 (`len(net.trafo)==0`); 41 lines, 30 buses, 5 gens + 1 ext_grid, 20 loads | same | `len(net.trafo)` | n/a | n/a |
| 8. case30 N-0 base-case loading_percent | line max=111.8314058662; line median=26.9241380380 | same, solved | fresh `case30()`, committed solver; `np.nanmax`/`np.nanmedian` of `res_line.loading_percent`. Base total load 189.2 MW. No trafo table, so no trafo value exists | single deterministic solve | n/a |
| 9. case30 N-1 max branch loading_percent | n=61500 (61500 of 61500 existing N-1 rows; 1500 of 1500 scenarios × 41 of 41 line outages; 0 non-converged); share>100 = 0.9989105691; share>95 = 0.9999837398; median=122.5609815225; p90=136.4415986919; max=217.5482267376 (min=94.6674635614) | `data/case30_dataset.parquet` + fresh `case30()` re-solve | see mapping note below | max over lines within each contingency, then share/median/p90/max over the 61500 contingencies | 4d73f8cdfe8131d2 |
| 10. case118 over-voltage, outaged_type=='none', converged | n=1500; >1.05: 0.7340000000; >1.06: 0.0580000000; >1.10: 0.0013333333; max(max_vm)=1.1222032642; median(max_vm)=1.0543519864 | `data/dataset.parquet` | filter `converged`, `outaged_type=='none'`; `np.mean(max_vm>t)`, max, median of `max_vm` (float64 column) | over rows | 8f0fd1081c8603e8 |
| 10b. case118 over-voltage, outaged_type!='none', converged | n=278955; >1.05: 0.7313581044; >1.06: 0.0573676758; >1.10: 0.0015737305; max=1.1529085250; median=1.0542520784 | `data/dataset.parquet` | same | over rows | 8f0fd1081c8603e8 |
| 11. case30 over-voltage, 'none', converged | n=1500; >1.05: 0.0; >1.06: 0.0; >1.10: 0.0; max=1.0249843221; median=1.0165071567 | `data/case30_dataset.parquet` | same | over rows | 4d73f8cdfe8131d2 |
| 11b. case30 over-voltage, !='none', converged | n=61500; >1.05: 0.0; >1.06: 0.0; >1.10: 0.0; max=1.0263452079; median=1.0165154060 | `data/case30_dataset.parquet` | same | over rows | 4d73f8cdfe8131d2 |
| 12. case118 thermal loading meaningfully evaluable? | NO — ratings are a uniform placeholder | `pandapower.networks.case118()` | Every line's implied rating is 9900 MVA and every trafo `sn_mva` is 9900 MVA (rows 2–3): a single constant, not per-branch engineering data. Consequence, measured: base-case line loading max 4.475%, median 0.348%, trafo max 3.589% (row 4) — the whole network sits two orders of magnitude below rating at N-0, so no N-1 outage on a bounded-stress scenario set can approach 100% except by numerical accident. Any case118 thermal screening result is a statement about the 9900 MVA placeholder, not about thermal security. Contrast case30, which carries 6 distinct genuine ratings and is already at 111.8% at N-0 | n/a | n/a |

Mapping for row 9 (how stored features map onto the network tables, and its justification):

- `feasibility/generate_dataset.py:157-178` (`scenario_features`) writes `pload_i`/`qload_i` as the **per-bus sum** of `params["p_new"]`/`q_new` over loads at bus `i`, `genvm_gi`/`genqmin_gi`/`genqmax_gi` positionally from `params`, and `genon_gi = 0 if gi == gen_out else 1`. `genp_gi` is `net["_gen_p0"][gi]`, i.e. the untouched base gen dispatch.
- `apply_scenario` (`:136-145`) sets exactly `net.load.p_mw`, `net.load.q_mvar`, `net.gen.vm_pu`, `net.gen.min_q_mvar`, `net.gen.max_q_mvar`, `net.gen.in_service`. Nothing else (ext_grid, gen.p_mw, line/trafo parameters) is modified.
- Inversion is exact for case30 because `net.load.bus` has no duplicates (20 loads on 20 distinct buses), so the per-bus sum is one-to-one: `net.load.p_mw = [pload_{bus} for bus in net.load.bus]`, likewise q; gens set positionally; `in_service = bool(genon_gi)`; gen `p_mw` left at base.
- Outages replayed as in `run_scenario` (`:210-216`): set `net.line.in_service=False` for one line, solve, restore.
- Precision caveat: these feature columns are stored float32 (`rows_to_frame`, `:227-233`), so the reconstruction is float32-accurate.
- Check, scenario_id 100000000: assigned total load = 203.950196 MW (base case30 is 189.2 MW).
- Independent validation of the mapping: recomputed N-0 min bus voltage matches stored `n0_min_vm` to max abs diff 4.815e-08 over all 1500 scenarios; recomputed N-1 `min_vm` matches the stored value to max abs diff 6.819e-08 over all 61500 contingencies, with convergence flags agreeing on 61500/61500. So row 9's loading numbers ride on a verified operating point, not an assumed one.

Nothing in the assigned list came out NOT INDEPENDENTLY DERIVABLE.
### S1 ROUND 2 — the diff I computed

AGREE (exact) — 40 quantities: all case118 and case30 rating-audit fields (max_i_ka n_nan /
n_distinct / min / max, implied MVA min and max, trafo sn_mva, N-0 base loading_percent line
max / line median / trafo max), and all over-voltage fields for both networks and both
subsets (n, share > 1.05 / 1.06 / 1.10, max_vm max, max_vm median).

Notable exact agreements across independent routes: case118 implied MVA min 9900.0 and max
9900.000000000002 on both sides; case118 N-0 line max 4.475087324056162 / median
0.34796764260032675 / trafo max 3.5892305584092106 on both; case30 N-0 line max
111.8314058662 on both; case118 N-1 share above 1.05 = 0.7313581043537488 on both;
case30 over-voltage 0.0 on both subsets on both.

DISAGREE — 6 quantities, all inside `networks.case30.thermal_sweep.line_loading`:

| quantity | A (artifact) | B (re-derived) |
|---|---|---|
| n | 4920 | 61500 |
| share above 100 | 1.0 | 0.9989105691 |
| share above 95 | 1.0 | 0.9999837398 |
| median | 154.72382022635077 | 122.5609815225 |
| p90 | 192.48176405289811 | 136.4415986919 |
| max | 490.44656024383517 | 217.5482267376 |

Both agents were sent only these values and the two derivation paths.

### S1 ROUND 2 — Agent A response — VERBATIM

**Root cause found — the artifact is wrong.** `/Users/rajansaha/contingency-screener-research/scripts/thermal_check.py`, in `thermal_sweep()`:

```python
net.load["p_mw"] = row[load_p].to_numpy(dtype=float)[:len(net.load)]
net.load["q_mvar"] = row[load_q].to_numpy(dtype=float)[:len(net.load)]
```

`pload_*` / `qload_*` are **per-bus** (30 columns for case30), but `net.load` has 20 rows at buses `[1,2,3,6,7,9,11,13,14,15,16,17,18,19,20,22,23,25,28,29]`. Truncating to the first 20 bus entries assigns the wrong bus's load to every load row and drops buses 20+. All 20 entries mismatch; scenario 100000000 total load becomes 154.48 MW instead of 203.95 MW. The correct mapping is `P[net.load.bus.to_numpy()]` (the OTHER route).

**Decisive check — reproduce the dataset's stored `min_vm`:**

| scenario / outage | stored min_vm | positional (artifact) | bus-mapped |
|---|---|---|---|
| 100000000 / line 0 | 0.960406 | 0.880874 | 0.960406 |
| 100000000 / line 1 | 0.946880 | 0.879625 | 0.946880 |
| 100000001 / line 0 | 0.953178 | 0.888835 | 0.953178 |
| 100000002 / line 0 | 0.959140 | 0.872712 | 0.959140 |

Bus mapping reproduces the committed dataset exactly; positional truncation does not. The artifact's 4920 solves were run at an operating point that is not the dataset's.

**Independent replication** (my own 40-scenario prefix, bus-mapped, same pinned solver): n=1640, share>100 = 1.0, share>95 = 1.0, median 123.8134562484445, p90 135.62956546070964, max 195.37529624106529 — matches the OTHER route's shape, not mine.

| quantity | verdict | support |
|---|---|---|
| n (4920 vs 61500) | the artifact is wrong | 4920 = 120x41 is an arithmetically correct count of what the artifact solved, but those 4920 solves are at invalid operating points; 61500 = 1500x41 is the full valid N-1 population |
| share above 100 (1.0 vs 0.9989105691) | the artifact is wrong | artifact sweep invalid. Note the 1.0 vs 0.9989 gap alone is prefix sampling, not the bug: my corrected 40-scenario prefix also gives 1.0 |
| share above 95 (1.0 vs 0.9999837398) | the artifact is wrong | same; corrected prefix also gives 1.0 |
| median (154.72 vs 122.56) | the artifact is wrong | corrected 40-scenario prefix: 123.81, consistent with 122.56, not 154.72 |
| p90 (192.48 vs 136.44) | the artifact is wrong | corrected prefix: 135.63, consistent with 136.44, not 192.48 |
| max (490.45 vs 217.55) | the artifact is wrong | corrected prefix: 195.38; the artifact's 490.45 is an artifact of mis-assigned loads. 217.55 > 195.38 is expected from 1500 vs 40 scenarios |

Scope notes:
- Only `thermal_sweep()` is affected. `rating_audit()` uses a fresh unmodified net, and `overvoltage_from_dataset()` reads stored columns — the case118/case30 rating, verdict, and over-voltage numbers I reported in round 1 are unaffected.
- The `gen*` assignments in the same loop are correct by coincidence: `genvm_`/`genqmin_`/`genqmax_` have 5 columns for case30's 5 gens (53 and 53 for case118), so the `[:len(net.gen)]` truncation is a no-op.
- The same bug would recur for case118 if its sweep were ever enabled: 118 `pload_` columns vs 99 `net.load` rows.
- No files were written; the artifact and script are unmodified.
### S1 ROUND 2 — Agent B response — VERBATIM

Reproduced the artifact path exactly (`scripts/thermal_check.py:thermal_sweep`, `max_scenarios=120`, case30): n=4920, share>100=1.0, share>95=1.0, max=490.44656024383517, median=154.72382022635077, p90=192.48176405289811 — bit-identical to the values you quoted, so the disagreement is in the code, not in the JSON transcription.

Root cause (single line), `scripts/thermal_check.py`:

```python
net.load["p_mw"] = row[load_p].to_numpy(dtype=float)[:len(net.load)]
net.load["q_mvar"] = row[load_q].to_numpy(dtype=float)[:len(net.load)]
```

`load_p` is `pload_0 … pload_29`, indexed **by bus**. Taking the first `len(net.load)=20` entries and assigning them positionally to load rows puts bus *i*'s demand on load row *i*, whose actual bus is `net.load.bus[i]` = [1,2,3,6,7,9,11,13,14,15,16,17,18,19,20,22,23,25,28,29]. Every load is therefore placed on the wrong bus and buses 20–29's demand is dropped entirely. `generate_dataset.py:161-165` writes `pbus[int(b)] += p` over `net["_load_bus"]`, so the inverse is `pload_{net.load.bus[i]}`, not `pload_{i}`. Check on scenario 100000000: correct total load 203.95019626617432 MW; the artifact's mapping assigns 154.48380851745605 MW to a shifted bus pattern. (The gen columns `[:len(net.gen)]` are positional in the source too, so those are correct; the defect is loads only. It would equally corrupt case118, where 99 loads meet 118 `pload_` columns — masked only because that sweep is skipped as PLACEHOLDER.)

My mapping is validated against the dataset independently: recomputed N-0 min voltage matches stored `n0_min_vm` to 4.8e-08 over 1500/1500 scenarios, and recomputed N-1 `min_vm` matches stored to 6.8e-08 over 61500/61500, convergence flags agreeing 61500/61500.

Two separate causes, quantified. Cause A = coverage (first 120 of 1500 base scenarios, dataset order); Cause B = the load-bus mis-mapping. Middle column is correct mapping restricted to the same 120-scenario prefix.

| quantity | mine (1500 scen, correct map) | 120 scen, correct map | artifact (120 scen, bad map) | Δ from A (sampling) | Δ from B (mis-mapping) |
|---|---|---|---|---|---|
| n | 61500 | 4920 | 4920 | -56580 | 0 |
| share>100 | 0.9989105691 | 0.9997967480 | 1.0 | +0.0008861789 | +0.0002032520 |
| share>95 | 0.9999837398 | 1.0 | 1.0 | +0.0000162602 | 0 |
| median | 122.5609815225 | 122.6595831089 | 154.7238202264 | +0.0986015864 | +32.0642371174 |
| p90 | 136.4415986919 | 135.6958884327 | 192.4817640529 | -0.7457102592 | +56.7858756202 |
| max | 217.5482267376 | 195.6071546649 | 490.4465602438 | -21.9410720727 | +294.8394055790 |

Verdicts:

- **n = 61500: my value stands.** 1500/1500 scenarios × 41/41 line outages, 0 solver failures. The artifact's 4920 is not wrong as a count of what it swept — it is self-labelled `"SAMPLE - NOT a full sweep"` — so on this row: **underdetermined by disagreement alone**; the two numbers answer different questions. Mine is the full population.
- **share above 100: my value stands / the artifact is wrong.** Artifact's 1.0 is dominated by cause B (+0.000203 over the correct 120-prefix value); the true full-sweep figure is 0.9989105691 (67 of 61500 contingencies at or below 100%).
- **share above 95: my value stands.** The artifact's 1.0 differs from mine only by cause A (+1.6e-05, i.e. the single contingency below 95% at 94.6674635614 falls outside the 120-prefix). Cause B contributes 0 here — this row is a sampling artifact, not the bug.
- **median: my value stands / the artifact is wrong.** 99.7% of the 32.16 gap is cause B.
- **p90: my value stands / the artifact is wrong.** Cause B contributes +56.79; cause A contributes -0.75 in the opposite direction.
- **max: my value stands / the artifact is wrong.** Cause B contributes +294.84. Note cause A alone would understate the max by 21.94 (the 120-prefix misses the tail), so the artifact's max is wrong in magnitude even relative to its own sample.
### S1 OUTCOME

Round 3 not required: both agents independently converged on "the artifact is wrong" and
independently identified the same single line as the root cause, from opposite directions —
A by reproducing the dataset's stored `min_vm` under both mappings, B by decomposing the two
causes quantitatively.

**The surviving 2A numbers** (both routes, exact agreement): every rating-audit field, both
PLACEHOLDER verdicts, the case118 skip, the case30 N-0 base max loading 111.8314058662, and
every over-voltage figure for both networks.

**The void 2A numbers**, superseded by B's full-population re-derivation:

| quantity | VOID (artifact) | CORRECTED (full 61,500, mapping validated to 6.8e-08 against stored `min_vm`) |
|---|---|---|
| share above 100 | 1.0 | **0.9989105691** |
| share above 95 | 1.0 | **0.9999837398** |
| median | 154.72382022635077 | **122.5609815225** |
| p90 | 192.48176405289811 | **136.4415986919** |
| max | 490.44656024383517 | **217.5482267376** |

**This corrects C-4 in one respect.** C-4 recorded that "share_above_100 = 1.000000 survives".
It does not: the full-population value is **0.9989105691**, i.e. **67 of 61,500 contingencies
are at or below 100%**. B shows the 1.0 arises from two causes at once — prefix sampling
(+0.00089) and the mis-mapping (+0.00020). The qualitative statement "essentially all case30
N-1 contingencies overload" survives; the exact 1.0 does not.

**New scope finding from both agents:** the same defect would corrupt case118 if its sweep
were ever enabled — 118 `pload_` columns against 99 `net.load` rows. It is masked only
because case118 is skipped as PLACEHOLDER. The `gen*` assignments in the same loop are correct
by coincidence, since those column counts equal `len(net.gen)`.

**One row recorded as answering different questions, not as a disagreement:** n = 4920 vs
61500. B: "the artifact's 4920 is not wrong as a count of what it swept — it is self-labelled
`SAMPLE - NOT a full sweep`". A: the 4920 solves are at invalid operating points.

**S1 TALLY:  AGREE 40  |  DISAGREE-resolved 5  |  UNRESOLVED 0  |  SINGLE-PATH 0**
(plus 1 row where the two values answer different questions by construction)

Nothing was changed. The script and artifact are unmodified.

---

## S2 — 2B generator outage + multiplier audit

### S2 ROUND 1 — Agent A (derived artifact) — VERBATIM

All values below are read verbatim from the artifact; none recomputed. `sha256(16)` = first 16 hex chars of the file's SHA-256 (`data/sampling_audit.json` = `f077ceb0678a4cb3`; manifest `content_sha256` matches the file digest exactly).

| quantity | value | file | jsonpath | aggregation | sha256(16) |
|---|---|---|---|---|---|
| outage_probability.as_coded | 0.3 | data/sampling_audit.json | $.outage_probability.as_coded | stored scalar | f077ceb0678a4cb3 |
| outage_probability.constant_defined_at | feasibility/generate_dataset.py:28 | data/sampling_audit.json | $.outage_probability.constant_defined_at | stored string | f077ceb0678a4cb3 |
| outage_probability.rng_draw_site | feasibility/generate_dataset.py:128 | data/sampling_audit.json | $.outage_probability.rng_draw_site | stored string | f077ceb0678a4cb3 |
| outage_probability.draw_expression | `if rng.random() < P_GEN_OUT` | data/sampling_audit.json | $.outage_probability.draw_expression | stored string | f077ceb0678a4cb3 |
| outage_probability.candidate_pool | non-slack generators only | data/sampling_audit.json | $.outage_probability.candidate_pool | stored string | f077ceb0678a4cb3 |
| prevalence.n_base_scenarios | 1500 | data/sampling_audit.json | $.prevalence.n_base_scenarios | count | f077ceb0678a4cb3 |
| prevalence.n_base_with_generator_outage | 374 | data/sampling_audit.json | $.prevalence.n_base_with_generator_outage | count | f077ceb0678a4cb3 |
| prevalence.share_of_base_scenarios | 0.24933333333333332 | data/sampling_audit.json | $.prevalence.share_of_base_scenarios | share (374/1500) | f077ceb0678a4cb3 |
| prevalence.n_n1_converged_rows | 278955 | data/sampling_audit.json | $.prevalence.n_n1_converged_rows | count | f077ceb0678a4cb3 |
| prevalence.n_n1_rows_with_generator_outage | 69532 | data/sampling_audit.json | $.prevalence.n_n1_rows_with_generator_outage | count | f077ceb0678a4cb3 |
| prevalence.share_of_n1_converged_rows | 0.24925884103170762 | data/sampling_audit.json | $.prevalence.share_of_n1_converged_rows | share (row-level) | f077ceb0678a4cb3 |
| acceptance_effect.coded_probability | 0.3 | data/sampling_audit.json | $.acceptance_effect.coded_probability | stored scalar | f077ceb0678a4cb3 |
| acceptance_effect.observed_share_of_accepted_bases | 0.24933333333333332 | data/sampling_audit.json | $.acceptance_effect.observed_share_of_accepted_bases | share over accepted bases | f077ceb0678a4cb3 |
| acceptance_effect.implied_relative_acceptance | 0.7750148016577856 | data/sampling_audit.json | $.acceptance_effect.implied_relative_acceptance | ratio | f077ceb0678a4cb3 |
| acceptance_effect.mean_n0_min_vm_with_outage | 0.9438126236403998 | data/sampling_audit.json | $.acceptance_effect.mean_n0_min_vm_with_outage | mean over N-0 bases | f077ceb0678a4cb3 |
| acceptance_effect.mean_n0_min_vm_without | 0.9441040473904923 | data/sampling_audit.json | $.acceptance_effect.mean_n0_min_vm_without | mean over N-0 bases | f077ceb0678a4cb3 |
| acceptance_effect.median_n0_min_vm_with_outage | 0.943045317945747 | data/sampling_audit.json | $.acceptance_effect.median_n0_min_vm_with_outage | median over N-0 bases | f077ceb0678a4cb3 |
| acceptance_effect.median_n0_min_vm_without | 0.9434863016228217 | data/sampling_audit.json | $.acceptance_effect.median_n0_min_vm_without | median over N-0 bases | f077ceb0678a4cb3 |
| rejection rate by outage status | ABSENT (artifact states it CANNOT BE COMPUTED: rejected draws not recorded) | data/sampling_audit.json | $.acceptance_effect.interpretation_note | — | f077ceb0678a4cb3 |
| with_generator_outage.n | 69532 | data/sampling_audit.json | $.distribution_by_outage_status.with_generator_outage.n | count of N-1 converged rows | f077ceb0678a4cb3 |
| with_generator_outage.mean_min_vm | 0.9394709975172333 | data/sampling_audit.json | $…with_generator_outage.mean_min_vm | mean | f077ceb0678a4cb3 |
| with_generator_outage.median_min_vm | 0.9420958412986705 | data/sampling_audit.json | $…with_generator_outage.median_min_vm | median | f077ceb0678a4cb3 |
| with_generator_outage.violation_rate | 0.18236207789219352 | data/sampling_audit.json | $…with_generator_outage.violation_rate | rate | f077ceb0678a4cb3 |
| with_generator_outage.boundary_strip_share | 0.5809555312661796 | data/sampling_audit.json | $…with_generator_outage.boundary_strip_share | share | f077ceb0678a4cb3 |
| with_generator_outage.p01_min_vm | 0.8797069626051496 | data/sampling_audit.json | $…with_generator_outage.p01_min_vm | 1st percentile | f077ceb0678a4cb3 |
| with_generator_outage.min_min_vm | 0.7224004261523653 | data/sampling_audit.json | $…with_generator_outage.min_min_vm | minimum | f077ceb0678a4cb3 |
| without_generator_outage.n | 209423 | data/sampling_audit.json | $…without_generator_outage.n | count of N-1 converged rows | f077ceb0678a4cb3 |
| without_generator_outage.mean_min_vm | 0.9399436558811946 | data/sampling_audit.json | $…without_generator_outage.mean_min_vm | mean | f077ceb0678a4cb3 |
| without_generator_outage.median_min_vm | 0.9425793539898427 | data/sampling_audit.json | $…without_generator_outage.median_min_vm | median | f077ceb0678a4cb3 |
| without_generator_outage.violation_rate | 0.17223036629214555 | data/sampling_audit.json | $…without_generator_outage.violation_rate | rate | f077ceb0678a4cb3 |
| without_generator_outage.boundary_strip_share | 0.5645368464781805 | data/sampling_audit.json | $…without_generator_outage.boundary_strip_share | share | f077ceb0678a4cb3 |
| without_generator_outage.p01_min_vm | 0.8820949243948777 | data/sampling_audit.json | $…without_generator_outage.p01_min_vm | 1st percentile | f077ceb0678a4cb3 |
| without_generator_outage.min_min_vm | 0.7179413407605296 | data/sampling_audit.json | $…without_generator_outage.min_min_vm | minimum | f077ceb0678a4cb3 |
| delta.violation_rate_pp | 1.0131711600047972 | data/sampling_audit.json | $.distribution_by_outage_status.delta.violation_rate_pp | percentage-point difference (with − without) | f077ceb0678a4cb3 |
| delta.boundary_strip_pp | 1.6418684787999127 | data/sampling_audit.json | $.distribution_by_outage_status.delta.boundary_strip_pp | percentage-point difference | f077ceb0678a4cb3 |
| delta.mean_min_vm | -0.0004726583639612647 | data/sampling_audit.json | $.distribution_by_outage_status.delta.mean_min_vm | difference of means | f077ceb0678a4cb3 |
| multiplier_range_as_invoked | U(1.0, 1.12) per load, committed run README.md:94-95 | data/sampling_audit.json | $.multiplier_audit.multiplier_range_as_invoked | stored string | f077ceb0678a4cb3 |
| static_assignment_targets [1] | lineno 137 → `net.load['p_mw']` (= `params['p_new']`) | data/sampling_audit.json | $.multiplier_audit.static_assignment_targets_in_apply_scenario[0] | list element | f077ceb0678a4cb3 |
| static_assignment_targets [2] | lineno 138 → `net.load['q_mvar']` (= `params['q_new']`) | data/sampling_audit.json | …[1] | list element | f077ceb0678a4cb3 |
| static_assignment_targets [3] | lineno 139 → `net.gen['vm_pu']` (= `params['gen_vm']`) | data/sampling_audit.json | …[2] | list element | f077ceb0678a4cb3 |
| static_assignment_targets [4] | lineno 140 → `net.gen['min_q_mvar']` (= `params['gen_qmin']`) | data/sampling_audit.json | …[3] | list element | f077ceb0678a4cb3 |
| static_assignment_targets [5] | lineno 141 → `net.gen['max_q_mvar']` (= `params['gen_qmax']`) | data/sampling_audit.json | …[4] | list element | f077ceb0678a4cb3 |
| static_assignment_targets [6] | lineno 142 → `net.gen['in_service']` (= `True`) | data/sampling_audit.json | …[5] | list element | f077ceb0678a4cb3 |
| static_assignment_targets [7] | lineno 144 → `net.gen.iat[params['gen_out'], net.gen.columns.get_loc('in_service')]` (= `False`) | data/sampling_audit.json | …[6] | list element | f077ceb0678a4cb3 |
| net_attributes_ever_assigned | `net.gen.iat[params['gen_out'], net.gen.columns.get_loc('in_service')]`; `net.gen['in_service']`; `net.gen['max_q_mvar']`; `net.gen['min_q_mvar']`; `net.gen['vm_pu']`; `net.load['p_mw']`; `net.load['q_mvar']` (7 entries) | data/sampling_audit.json | $.multiplier_audit.net_attributes_ever_assigned | full list | f077ceb0678a4cb3 |
| count of rng_draw_sites | 10 (draw_gen_vm:84, :91 uniform; sample_scenario:103, 110, 111, 114, 119, 124 uniform; :128 random; :130 choice) | data/sampling_audit.json | $.multiplier_audit.rng_draw_sites | length of list | f077ceb0678a4cb3 |
| empirical_family_variance.pload_ | n_columns_checked 8; all_constant false; min_nunique 1; max_nunique 1500; max_std 2.9073903560638428; verdict "VARIES across scenarios" | data/sampling_audit.json | $.multiplier_audit.empirical_family_variance.pload_ | per-prefix column scan | f077ceb0678a4cb3 |
| empirical_family_variance.qload_ | 8; false; 1; 1500; 2.4555294513702393; "VARIES across scenarios" | data/sampling_audit.json | …qload_ | per-prefix column scan | f077ceb0678a4cb3 |
| empirical_family_variance.genp_ | 8; true; 1; 1; 0.0; "CONSTANT across scenarios - NOT varied by any sampling mechanism" | data/sampling_audit.json | …genp_ | per-prefix column scan | f077ceb0678a4cb3 |
| empirical_family_variance.genvm_ | 8; false; 1495; 1500; 0.01453086081892252; "VARIES across scenarios" | data/sampling_audit.json | …genvm_ | per-prefix column scan | f077ceb0678a4cb3 |
| empirical_family_variance.genqmin_ | 8; false; 1500; 1500; 70.99347686767578; "VARIES across scenarios" | data/sampling_audit.json | …genqmin_ | per-prefix column scan | f077ceb0678a4cb3 |
| empirical_family_variance.genqmax_ | 8; false; 1500; 1500; 70.99347686767578; "VARIES across scenarios" | data/sampling_audit.json | …genqmax_ | per-prefix column scan | f077ceb0678a4cb3 |
| empirical_family_variance.genon_ | 8; false; 1; 2; 0.08911393940417375; "VARIES across scenarios" | data/sampling_audit.json | …genon_ | per-prefix column scan | f077ceb0678a4cb3 |
| empirical_family_variance.vm0_ | 8; false; 1500; 1500; 0.014501075829069893; "VARIES across scenarios" | data/sampling_audit.json | …vm0_ | per-prefix column scan | f077ceb0678a4cb3 |
| TOUCHED.load_p_mw | how: "net.load['p_mw'] = params['p_new'], where p_new = _p0 * mp"; empirical: "VARIES across scenarios" | data/sampling_audit.json | $.multiplier_audit.TOUCHED_BY_MULTIPLIER.load_p_mw | stored strings | f077ceb0678a4cb3 |
| TOUCHED.load_q_mvar | how: "net.load['q_mvar'] = params['q_new'], where q_new = _q0 * mp * pf; scaled by the multiplier AND by an INDEPENDENT power-factor draw pf ~ U(0.9, 1.15) as invoked"; empirical: "VARIES across scenarios" | data/sampling_audit.json | $.multiplier_audit.TOUCHED_BY_MULTIPLIER.load_q_mvar | stored strings | f077ceb0678a4cb3 |
| NOT_TOUCHED.gen_p_mw | how: "net.gen['p_mw'] is NEVER assigned in apply_scenario"; empirical: "CONSTANT across scenarios - NOT varied by any sampling mechanism"; consequence: "generator real power stays at base dispatch; the slack bus absorbs the entire load increase" | data/sampling_audit.json | $.multiplier_audit.NOT_TOUCHED_BY_MULTIPLIER.gen_p_mw | stored strings | f077ceb0678a4cb3 |
| NOT_TOUCHED.gen_vm_pu | how: "net.gen['vm_pu'] = params['gen_vm'], drawn as base +/- dvm"; empirical: "VARIES across scenarios"; consequence: "varied, but by an independent jitter, not by the multiplier" | data/sampling_audit.json | $…NOT_TOUCHED_BY_MULTIPLIER.gen_vm_pu | stored strings | f077ceb0678a4cb3 |
| NOT_TOUCHED.gen_q_limits | how: "net.gen['min_q_mvar'] / ['max_q_mvar'] = base * qscale, qscale ~ U(0.60, 1.40)"; empirical: "VARIES across scenarios / VARIES across scenarios"; consequence: "varied, but by an independent draw" | data/sampling_audit.json | $…NOT_TOUCHED_BY_MULTIPLIER.gen_q_limits | stored strings | f077ceb0678a4cb3 |
| NOT_TOUCHED.gen_in_service | how: "net.gen.iat[gen_out, 'in_service'] = False when the outage draw fires"; empirical: "VARIES across scenarios"; consequence: "set by the independent P_GEN_OUT draw" | data/sampling_audit.json | $…NOT_TOUCHED_BY_MULTIPLIER.gen_in_service | stored strings | f077ceb0678a4cb3 |
| aggregate_loading.min | 1.0142253637313843 | data/sampling_audit.json | $.multiplier_audit.aggregate_loading.min | minimum over scenarios | f077ceb0678a4cb3 |
| aggregate_loading.max | 1.1238573789596558 | data/sampling_audit.json | $.multiplier_audit.aggregate_loading.max | maximum over scenarios | f077ceb0678a4cb3 |

Artifact path: `/Users/rajansaha/contingency-screener-research/data/sampling_audit.json`; manifest: `/Users/rajansaha/contingency-screener-research/data/sampling_audit.manifest.json` (sha256(16) `4c5287b4654d1573`, git_commit `6082204`).
### S2 ROUND 1 — Agent B (re-derived, ANCHORED) — VERBATIM

ANCHOR: PASSED.

| quantity | value | file or source | derivation | aggregation | sha256(16) |
|---|---|---|---|---|---|
| **ANCHOR — recomputed N-0 min bus voltage vs stored `n0_min_vm`** | **60/60 scenarios matched at <1e-4; max abs diff 2.97e-08, median 1.29e-08; 0 non-convergences** | data/dataset.parquet + pandapower.networks.case118 | 60 base rows (`outaged_type=='none'`) drawn at random (np seed 0) from 1500; `net.load.p_mw = pload_{bus}[net.load.bus]`, `net.load.q_mvar = qload_{bus}[...]` (99 loads on 99 distinct buses, so the per-bus feature block is invertible), `net.gen.vm_pu/min_q_mvar/max_q_mvar = genvm_/genqmin_/genqmax_`, `net.gen.in_service = genon_.astype(bool)`; `pp.runpp(enforce_q_lims=True, init="dc", numba=True, algorithm="nr")` = feasibility/manifest.py SOLVER; compared `min(res_bus.vm_pu)` to stored `n0_min_vm` | max, median over 60 | 8f0fd1081c8603e8 |
| Anchor residual floor | consistent with float32 storage of the feature columns (`rows_to_frame` casts all non-keep float64 cols to float32); no systematic bias | data/dataset.parquet | rounding of the reconstructed inputs, not solver disagreement | — | 8f0fd1081c8603e8 |
| rows / base scenarios / converged N-1 rows | 280500 / 1500 / 278955 | data/dataset.parquet | row counts; N-1 = `outaged_type!='none' & converged` | count | 8f0fd1081c8603e8 |
| **1. base scenarios with `gen_out>=0`** | 374 of 1500 = 0.249333 (24.9333%) | data/dataset.parquet | `(base.gen_out>=0)` | count, mean | 8f0fd1081c8603e8 |
| **2. converged N-1 rows whose scenario has `gen_out>=0`** | 69532 of 278955 = 0.2492588 (24.9259%) | data/dataset.parquet | same mask on converged N-1 rows | count, mean | 8f0fd1081c8603e8 |
| **3. `n0_min_vm`, base WITH gen outage** | mean 0.94381262, median 0.94304532 (n=374) | data/dataset.parquet | mean/median of `n0_min_vm` | mean, median | 8f0fd1081c8603e8 |
| **3. `n0_min_vm`, base WITHOUT gen outage** | mean 0.94410405, median 0.94348630 (n=1126) | data/dataset.parquet | same | mean, median | 8f0fd1081c8603e8 |
| **3. difference (with − without)** | mean −0.00029142, median −0.00044098 | data/dataset.parquet | subtraction | — | 8f0fd1081c8603e8 |
| **4. converged N-1, gen-outage scenarios** | n=69532; mean min_vm 0.93947100; median 0.94209584; violation rate (min_vm<0.94) 0.18236208; boundary strip [0.94,0.945) 0.58095553; 1st pctile 0.87970696; min 0.72240043 | data/dataset.parquet | masks on `min_vm`; `np.percentile(...,1)` (linear interp) | n, mean, median, rate, pctile, min | 8f0fd1081c8603e8 |
| **4. converged N-1, no gen outage** | n=209423; mean min_vm 0.93994366; median 0.94257935; violation rate 0.17223037; boundary strip 0.56453685; 1st pctile 0.88209492; min 0.71794134 | data/dataset.parquet | same | same | 8f0fd1081c8603e8 |
| **4. differences (gen − no-gen)** | Δmean −0.00047266; Δviolation +0.01013171; Δboundary-strip +0.01641868 | data/dataset.parquet | subtraction | — | 8f0fd1081c8603e8 |
| **5. `agg_loading` over base scenarios** | min 1.0142254, max 1.1238574 (1496 distinct of 1500) | data/dataset.parquet | min/max | min, max | 8f0fd1081c8603e8 |
| 5b. `agg_loading` by mode | independent [1.0453284, 1.0732505] (n=750); regional [1.0142254, 1.1238574] (n=750) | data/dataset.parquet | grouped min/max on `sampling_mode` | min, max | 8f0fd1081c8603e8 |
| 5c. LOADING_CAP binding? | never — max agg_loading 1.1239 « cap 1.60 | data/dataset.parquet | max vs constant | max | 8f0fd1081c8603e8 |
| **6. `net.load p_mw` (pload_)** | **TOUCHED — independent per-load draw** | data/dataset.parquet + case118 | 118 cols, 19 constant (=19 buses with no load; 99 loaded buses all vary), max col std 15.4463; row-sum vs agg_loading r = **0.99999999999540**; but per-column r ranges [0.0188, 0.4042], mean 0.1577 | corr over 1500 base rows | 8f0fd1081c8603e8 |
| 6a. why the pload row-sum correlation is NOT evidence of a scalar multiplier | `max|rowsum(pload)/sum(case118 p_mw) − agg_loading| = 6.7e-08` — `agg_loading` IS the row-sum, by definition; per-load multipliers `pload_i/p0_i` span 0.9009–1.2310 with mean within-row std 0.0515, so loads move independently, not together | data/dataset.parquet + case118 | element-wise ratio to base `net.load.p_mw` | max, min, mean-of-std | 8f0fd1081c8603e8 |
| 6b. per-load multiplier range by mode | independent [1.0000, 1.1200] (within-row std 0.0344 ≈ uniform[1.00,1.12] std 0.0346); regional [0.9009, 1.2310] (within-row std 0.0685) | data/dataset.parquet + case118 | ratio to base, grouped by `sampling_mode` | min, max, mean-of-std | 8f0fd1081c8603e8 |
| **6. `net.load q_mvar` (qload_)** | **TOUCHED — load multiplier × independent power-factor draw** | data/dataset.parquet + case118 | 118 cols, 28 constant, max col std 10.977; row-sum vs agg_loading r = **0.69062267** (partial, not 1.0); implied pf = (q-ratio)/(p-ratio) spans 0.9000–1.1500 | corr, min, max | 8f0fd1081c8603e8 |
| **6. `net.gen p_mw` (genp_)** | **NOT TOUCHED — constant** | data/dataset.parquet + case118 | all 53 cols `nunique==1`, max std 0.0; max abs deviation from `case118 net.gen.p_mw` = 0.0 (18 gens have p0>0) | max std, max abs dev | 8f0fd1081c8603e8 |
| **6. `net.gen vm_pu` (genvm_)** | **TOUCHED — independent draw, uncorrelated with loading** | data/dataset.parquet + case118 | 53 cols, 0 constant, max col std 0.0147551; row-sum vs agg_loading r = **0.04324632**; deviation from base vm spans [−0.0250, +0.0250] i.e. a ±0.025 jitter | corr, min, max | 8f0fd1081c8603e8 |
| **6. `net.gen min_q_mvar / max_q_mvar` (genqmin_/genqmax_)** | **TOUCHED — independent draw, uncorrelated with loading; one shared scale per gen** | data/dataset.parquet + case118 | 53 cols each, 0 constant, max col std 236.351 (both); row-sum vs agg_loading r = **−0.03198674** (qmin), **+0.04202680** (qmax); implied scale = value/base spans 0.6000–1.4000 for both; max abs difference between the qmin-implied and qmax-implied scale = 1.41e-07 → same draw applied to both limits | corr, min, max | 8f0fd1081c8603e8 |
| **6. `net.gen in_service` (genon_)** | **TOUCHED — independent Bernoulli draw, uncorrelated with loading** | data/dataset.parquet | 53 cols, 2 constant-at-1 (gens 4 and 38 never drawn), max col std 0.102727; row-sum vs agg_loading r = **0.00997278**; row-sum = 53 or 52 | corr, count | 8f0fd1081c8603e8 |
| **7. non-slack generator fraction (outage candidate pool)** | **53 / 53 = 100%** — `net.gen.slack.sum() == 0` on case118; the slack is a separate `ext_grid` element (1 row, bus index 68 / IEEE bus 69), which is not in `net.gen` and therefore cannot be selected | pandapower.networks.case118 | direct read of `net.gen.slack`, `net.ext_grid` | count | (network object, not a file) |
| **7. is the slack ever taken out?** | **No — structurally impossible.** The slack is an `ext_grid`, and `gen_out` indexes `net.gen` only. Observed `gen_out` values: −1 plus 51 distinct gen indices in 0..52; only 4 and 38 are absent, consistent with 374 draws over 53 candidates (expected ~0.9 gens unseen), not with exclusion | data/dataset.parquet + case118 | `sorted(base.gen_out.unique())` | distinct values | 8f0fd1081c8603e8 |

Notes on two items that are not independently derivable from the parquet alone:

| quantity | value | reason |
|---|---|---|
| whether gens 4 and 38 were *excluded* vs merely *not drawn* | NOT INDEPENDENTLY DERIVABLE | 374 Bernoulli draws over 53 candidates leave ~0.9 gens unseen in expectation; absence from `gen_out` is indistinguishable from chance at this sample size using the data alone |
| the *nominal* sampling hyperparameters | derivable only as observed support, not as declared values | the data's empirical ranges are: per-load multiplier [1.00,1.12] (independent mode), regional jitter ±10%, pf [0.90,1.15], gen vm jitter ±0.025, q-limit scale [0.60,1.40], P(gen outage) ≈ 0.2493. These are the observed supports of 1500 draws, which bound but do not prove the declared parameters |

Two things worth flagging to whoever consumes this:

- The `pload_` row-sum correlation with `agg_loading` is **1.0 by identity, not by physics** — `agg_loading` is literally `sum(pload)/sum(base p_mw)` (verified to 6.7e-08). Reading that r=1.0 as "loads are scaled by a single multiplier" would be wrong: the per-load multipliers are independent draws spanning 0.90–1.23, and the per-column correlations against `agg_loading` are all below 0.41. The correct discriminator here is the per-column correlation and the within-row spread of the implied multipliers, not the row-sum.
- The observed generator-outage share is 0.2493, and it is essentially identical in the base rows (0.249333) and the converged N-1 rows (0.249259) — the N-0 feasibility gate and the N-1 non-convergence filter do not measurably deplete gen-outage scenarios. The gen-outage effect on outcomes is small but consistent in sign across all four measures: lower `n0_min_vm` (−0.00029 mean), lower N-1 `min_vm` (−0.00047 mean), higher violation rate (+0.0101), higher boundary-strip mass (+0.0164).
### S2 ROUND 2 — the diff I computed

B's anchor PASSED before it reported anything: 60/60 base scenarios reconstructed from stored
features and re-solved, recomputed N-0 minimum bus voltage matching stored `n0_min_vm` to
**max abs diff 2.97e-08**, median 1.29e-08, 0 non-convergences. Residual attributed to float32
storage of the feature columns, no systematic bias.

AGREE (exact) — 20 quantities: 374 / 1500 / 0.24933333333333332; 69532 / 278955 /
0.24925884103170762; mean `n0_min_vm` 0.9438126236403998 with and 0.9441040473904923 without;
violation rates 0.18236207789219352 / 0.17223036629214555; boundary-strip shares
0.5809555312661796 / 0.5645368464781805; delta 1.0131711600047972 pp; `agg_loading`
1.0142253637313843 / 1.1238573789596558; and `net.gen p_mw` NOT TOUCHED — B confirms all 53
columns `nunique==1`, max std 0.0, and max absolute deviation from `case118 net.gen.p_mw`
of exactly **0.0**.

DISAGREE — 2 items, both characterisations rather than numbers:

| item | A (artifact) | B (re-derived) |
|---|---|---|
| outage candidate pool | "non-slack generators only" | "53 of 53 are non-slack; the slack is an `ext_grid` element, not a `net.gen` row; the filter excludes nothing" |
| how the multiplier acts on `net.load p_mw` | "p_new = _p0 * mp" | "independent per-load draw; the row-sum correlation is an identity, not evidence of a scalar multiplier; per-load multipliers span 0.9009–1.2310" |

### S2 ROUND 2 — Agent A response — VERBATIM

Both re-derivations check out. Verdicts below, with the computations I ran.

**DISAGREEMENT 1 — candidate pool: THE ARTIFACT IS INCOMPLETE (other value stands; my value is a faithful but vacuous transcription).**

- My route was a verbatim read of `$.outage_probability.candidate_pool`. The string matches the code exactly — `feasibility/generate_dataset.py:129`: `candidates = [i for i in range(ngen) if not net.gen.iloc[i]["slack"]]`. So the artifact is not wrong about what the code says.
- But on case118 the filter is a no-op. Fresh `pandapower.networks.case118()`: `len(net.gen) == 53`, `net.gen["slack"].sum() == 0`, `net.gen["slack_weight"].sum() == 0.0`; the slack is `net.ext_grid` with a single row at bus index 68, and `set(net.ext_grid.bus) & set(net.gen.bus) == set()` — the slack bus carries no `gen` row at all, so it was never selectable.
- Dataset side: over the 1500 base scenarios, `gen_out` takes 52 distinct values (−1 plus 51 distinct generator indices), spanning index 0 to 52 — i.e. draws land across the full 0..52 gen range; the two unseen indices are ordinary sampling gaps in 374 draws, not an exclusion.
- Conclusion: the pool is all 53 generators. "non-slack generators only" implies a restriction that excludes nothing here, which is the misleading part. The other route's phrasing is the correct one to carry forward.

**DISAGREEMENT 2 — multiplier action on `net.load['p_mw']`: MY "how"/"empirical" STAND, but THE ARTIFACT IS WRONG one field over, at `multiplier_range_as_invoked`.**

- My two fields are correct and not in conflict with the other route: `apply_scenario` line 137 is `net.load["p_mw"] = params["p_new"]`, and `p_new = net["_p0"] * mp` (line 121) where `mp` is a length-`nloads` **vector** — an element-wise per-load draw, not a scalar. "TOUCHED / VARIES across scenarios" is right, and the other route says TOUCHED too.
- The real error is `$.multiplier_audit.multiplier_range_as_invoked = "U(1.0, 1.12) per load"`. That holds only in `independent` mode (`mp = rng.uniform(lo_i, hi_i, size=nloads)`). In `regional` mode `mp = block[load_region] * jit` with `block ~ U(reg_lo, reg_hi)` and `jit ~ U(0.9, 1.1)` (`REG_JITTER = 0.10`), and the committed run passes `--reg-lo 1.0 --reg-hi 1.12` (README.md:94-95), giving a per-load support of [0.90, 1.232] — below 1.0 and above 1.12. The run is `--mode mixed` (default), so both modes are present.
- Reproduced from `data/dataset.parquet` (per-bus `pload_*` divided by base per-bus load from a fresh case118, deduped to 1500 base scenarios): implied per-load multiplier overall **0.9008575439453125 – 1.2309630393981934**; independent **1.0000040054321289 – 1.1199995796635467**; regional **0.9008575439453125 – 1.2309630393981934**. Matches the other route exactly.
- Also reproduced: row-sum of `pload_*` over base total vs `agg_loading` — max abs difference 5.29e-07, r = 0.9999999999085685 (identity, not evidence of a scalar multiplier); per-column correlations against `agg_loading` min 0.018828782384534174, mean 0.15766134759675093, max 0.40418337284840183. My 5.3e-07 vs their 6.7e-08 is float32 storage/normalization, same conclusion.
- The artifact contradicts itself: `aggregate_loading.note` already says "the regional mode applies a block multiplier plus per-load jitter", which is incompatible with a flat "U(1.0, 1.12) per load".

Two further defects I found in the same block while checking, not part of either disagreement:

1. `TOUCHED_BY_MULTIPLIER.load_p_mw.how` omits two post-draw transforms of `mp`: `mp = np.clip(mp, 0.5, None)` (line 116) and the renormalization `mp *= LOADING_CAP / agg` when `agg > LOADING_CAP` (lines 117-118, `LOADING_CAP = 1.60`). Neither binds in this run — observed `agg_loading` max is 1.1238573789596558, and the observed multiplier floor 0.9009 is well above 0.5 — so the numbers are unaffected, but the "how" string is not a complete description of the map.
2. `load_q_mvar.how`'s "pf ~ U(0.9, 1.15) as invoked" is correct: code defaults are `PF_LO, PF_HI = 0.80, 1.50` (line 23), overridden by `--pf-lo 0.9 --pf-hi 1.15` in the committed invocation.

Files: `/Users/rajansaha/contingency-screener-research/feasibility/generate_dataset.py` (lines 19-23, 28, 96-133, 136-145), `/Users/rajansaha/contingency-screener-research/README.md` lines 94-95, `/Users/rajansaha/contingency-screener-research/data/sampling_audit.json`, `/Users/rajansaha/contingency-screener-research/data/dataset.parquet`.
### S2 ROUND 2 — Agent B response — VERBATIM

Both items re-checked from my own route, then against the other path's derivation.

## DISAGREEMENT 1 — outage candidate pool

**Verdict: my value stands. The artifact is not wrong about the code, but its string is vacuous on this network and must not be carried into the manuscript as a stated restriction.**

The two routes are describing different things and neither number is in error:

`feasibility/generate_dataset.py:129` reads

```python
candidates = [i for i in range(ngen) if not net.gen.iloc[i]["slack"]]
```

so `"non-slack generators only"` is a faithful transcription of the *code*. What it does on *case118* is nothing:

| check | result |
|---|---|
| `net.gen.slack.dtype` / `.unique()` / `.sum()` | `bool` / `[False]` / `0` |
| `len(net.gen)` | 53 |
| candidates after the filter | 53 of 53 (100%) |
| `len(net.ext_grid)`, its bus | 1, bus index 68 (IEEE bus 69) |
| generators at bus 68 | 0 |
| `net.gen.slack_weight` unique | `[0.]` |

The slack on case118 is an `ext_grid` element. `gen_out` indexes `net.gen`, which does not contain it, so the slack is unselectable *structurally* — the `slack` filter is not what protects it, and the filter removes zero candidates. Observed `gen_out` values confirm the pool is unrestricted: 51 distinct indices in 0..52 over 374 draws, with only gens 4 and 38 unseen (expected ~0.9 unseen by chance).

The risk here is a manuscript sentence like "generator outages were sampled from the non-slack generators," which reads as a deliberate design restriction on the candidate set. On this network it excludes nothing. The defensible phrasing is that the candidate pool is all 53 `net.gen` units, and the slack bus is out of scope because it is modeled as an external grid.

## DISAGREEMENT 2 — how the load multiplier acts on `net.load p_mw`

**Verdict: not a real disagreement. My value stands and the artifact is also correct; the word "multiplier" in the audit string is a vector, and reading it as a scalar is the only way to get a contradiction.**

`params["p_new"] = net["_p0"] * mp` where `mp` is length-`nloads` (99), drawn per load:

```
independent:  mp = rng.uniform(lo_i, hi_i, size=nloads)
regional:     mp = block[load_region] * jit,  jit = rng.uniform(0.9, 1.1, size=nloads)
```

So `_p0 * mp` is element-wise, exactly as the artifact says, and "VARIES across scenarios" is right. My claim was narrower and survives: the *row-sum* correlation of r = 0.99999999999540 against `agg_loading` is an identity, not evidence — `max|rowsum(pload)/sum(base p_mw) − agg_loading| = 6.7e-08`, i.e. `agg_loading` **is** that row-sum. Per-column correlations against `agg_loading` run 0.0188–0.4042 (mean 0.1577), and per-load implied multipliers span 0.9009–1.2310 with mean within-row std 0.0515. Loads do not move together.

Both statements are true; if the audit string is consumed as "one scalar multiplier scales all loads," that reading is wrong, and the row-sum correlation is the trap that would appear to confirm it.

## Manuscript statement: "load and generator base values multiplied by multipliers ranging uniformly from 1.0 to 1.12"

Measured element-wise as `feature / case118 base value`, over 1500 base scenarios (750 per mode, 99 loads each = 74,250 per-load multipliers per mode):

| target | mode | measured multiplier range | uniform on [1.0,1.12]? | fraction outside [1.0,1.12] | verdict |
|---|---|---|---|---|---|
| `net.load p_mw` | independent | [1.000004, 1.120000], mean 1.059979, std 0.034665 | yes — decile counts 7451/7436/7540/7316/7331/7447/7517/7413/7351/7448, flat; std 0.03466 vs U(1.00,1.12) theoretical 0.03464 | 0.0000 | **CONSISTENT** |
| `net.load p_mw` | regional | [0.900858, 1.230963], mean 1.058413, std 0.070012 | no | **0.4391** (22.94% below 1.0, 20.97% above 1.12) | **INCONSISTENT** |
| `net.load q_mvar` | both | [0.815637, 1.408329] | no | 0.5683 | **INCONSISTENT** |
| `net.gen p_mw` | both | exactly 1.0 — all 53 columns `nunique==1`, `max|genp_ − net.gen.p_mw| = 0.0` | not multiplied at all | n/a | **FALSE** |

Separately, per your request:

- **Independent mode, load P: consistent.** This is the one case the sentence describes correctly.
- **Regional mode, load P: not consistent.** The effective per-load multiplier is `block × jitter` with `block ~ U(1.00,1.12)` over 8 modularity communities and `jitter ~ U(0.90,1.10)`; the product's support is [0.900, 1.232], which reproduces the observed [0.900858, 1.230963] to three decimals. 43.9% of per-load multipliers fall outside the stated interval, and the distribution is not uniform (triangular-ish from the product). Regional mode is half the dataset (750 of 1500 base scenarios).
- **Load Q: not consistent in either mode.** Q carries an additional independent power-factor draw, `q_new = _q0 * mp * pf` with observed `pf ∈ [0.900, 1.150]`, giving an effective Q multiplier of [0.816, 1.408].
- **Generator base values: the claim is false in both modes.** Generator real power is byte-identical to case118 in every scenario. What actually varies on the generators is `vm_pu` (±0.025 additive jitter, not multiplicative), the reactive limits (`min_q_mvar`/`max_q_mvar` scaled by a shared per-generator draw on [0.600, 1.400]), and `in_service`. None of those is a 1.0–1.12 multiplier, and the q-limit scale runs in the opposite direction (it can shrink limits by 40%).

The sentence as written is defensible only for load real power in independent mode. To cover the dataset it would need to state the per-load (not aggregate) multiplier, the regional block-times-jitter construction and its wider support, the separate power-factor draw on Q, and drop the generator clause entirely.

Supporting scripts, if you want to re-run any of this: `/private/tmp/claude-501/-Users-rajansaha-contingency-screener-research/a20165b8-6ffa-4031-84e5-ca5fd47a15f6/scratchpad/an4.py` and `/private/tmp/claude-501/-Users-rajansaha-contingency-screener-research/a20165b8-6ffa-4031-84e5-ca5fd47a15f6/scratchpad/an5.py` (anchor at `.../anchor2.py`). `data/dataset.parquet` sha256(16) `8f0fd1081c8603e8`; `feasibility/generate_dataset.py` sha256(16) `30923b161f71f6a2`.
### S2 OUTCOME

Round 3 not required — both agents converged on both items.

**Item 1 — candidate pool. Both agents agree the artifact string is a faithful transcription
of the code and VACUOUS on this network.** `generate_dataset.py:129` filters
`if not net.gen.iloc[i]["slack"]`; on case118 `net.gen.slack.sum() == 0`, so 53 of 53 survive
the filter. The slack is `net.ext_grid` at bus index 68 with no `net.gen` row at that bus, so
it is unselectable structurally, not by the filter. Both agents independently warn that a
manuscript sentence reading "generator outages were sampled from the non-slack generators"
would assert a design restriction that excludes nothing.

**Item 2 — NOT A REAL DISAGREEMENT, but it exposed a third defect.** Both agents agree
`_p0 * mp` is element-wise with `mp` a length-99 vector, so both statements are true; the trap
is reading "multiplier" as a scalar, which the r = 0.99999999999540 row-sum correlation
appears to confirm. It does not: `agg_loading` **is** that row-sum (verified 6.7e-08 by B,
5.29e-07 by A), per-column correlations run 0.0188–0.4042.

**NEW DEFECT, found by A while checking — `multiplier_range_as_invoked` in the artifact is
WRONG.** It stores `"U(1.0, 1.12) per load"`. That holds only in `independent` mode. In
`regional` mode `mp = block[load_region] * jit` with `block ~ U(1.00, 1.12)` and
`jit ~ U(0.90, 1.10)`, support **[0.90, 1.232]**. The committed run is `--mode mixed`, so both
modes are present, 750 base scenarios each. A also notes the artifact contradicts itself — its
own `aggregate_loading.note` already describes the regional construction.

**The III-A correction, now quantified per mode by B** (element-wise `feature / case118 base`,
74,250 per-load multipliers per mode):

| target | mode | measured range | fraction outside [1.0, 1.12] | verdict |
|---|---|---|---|---|
| `net.load p_mw` | independent | [1.000004, 1.120000], std 0.034665 vs U theoretical 0.03464, flat deciles | 0.0000 | **CONSISTENT** |
| `net.load p_mw` | regional | [0.900858, 1.230963] | **0.4391** (22.94% below 1.0, 20.97% above 1.12) | **INCONSISTENT** |
| `net.load q_mvar` | both | [0.815637, 1.408329] | 0.5683 | **INCONSISTENT** |
| `net.gen p_mw` | both | exactly 1.0, `max\|genp_ − net.gen.p_mw\| = 0.0` | n/a | **FALSE — never multiplied** |

Two further incompletenesses A found in the same block, neither changing a number: the `how`
string omits `mp = np.clip(mp, 0.5, None)` and the `LOADING_CAP = 1.60` renormalisation
(neither binds — observed floor 0.9009, observed max `agg_loading` 1.1239); and
`load_q_mvar.how`'s "pf ~ U(0.9, 1.15) as invoked" is confirmed correct against the committed
override of the `0.80, 1.50` defaults.

**S2 TALLY:  AGREE 20  |  DISAGREE-resolved 2  |  UNRESOLVED 0  |  SINGLE-PATH 0**

Nothing changed.

---

## S3 — 2C n0-stratum drift (the ridge 10.5-point collapse)

### S3 ROUND 1 — Agent A (derived artifact) — VERBATIM

sha256(16) for `data/drift_n0_stratum_long.parquet` = `97c8ef7aa40c4e97` (full: 97c8ef7aa40c4e9728a472c286cc81069fce42ea498983d7c86e50e97e5cc3d3). Every row below is from that file only.

| quantity | value | file | column/filter | aggregation | sha256(16) |
|---|---|---|---|---|---|
| row count | 1200 | data/drift_n0_stratum_long.parquet | all rows | len | 97c8ef7aa40c4e97 |
| distinct model | histgb, ridge (2) | " | model | unique | 97c8ef7aa40c4e97 |
| distinct cal_stratum | benign, marginal (2) | " | cal_stratum | unique | 97c8ef7aa40c4e97 |
| distinct test_stratum | benign, marginal (2) | " | test_stratum | unique | 97c8ef7aa40c4e97 |
| distinct seed | 0,1,2,3,4 (5) | " | seed | unique | 97c8ef7aa40c4e97 |
| distinct coverage_target | 0.70..0.99 step 0.01 (30) | " | coverage_target | unique | 97c8ef7aa40c4e97 |
| distinct test | 2C_n0_stratum (1) | " | test | unique | 97c8ef7aa40c4e97 |
| distinct is_control | False, True (2) | " | is_control | unique | 97c8ef7aa40c4e97 |
| median_n0_min_vm distinct | 1 value: 0.9433575252264039 | " | median_n0_min_vm | unique | 97c8ef7aa40c4e97 |
| realized_shift_mean_n0_min_vm, benign→benign | -5.6419461091850034e-05 (5 distinct, min -0.0004931558153089544, max 0.00044589722316035196) | " | cal=benign,test=benign | mean over 300 rows | 97c8ef7aa40c4e97 |
| realized_shift, benign→marginal | -0.004844344018952729 (min -0.005084679348747789, max -0.004692811882023973) | " | cal=benign,test=marginal | mean | 97c8ef7aa40c4e97 |
| realized_shift, marginal→benign | 0.0048648452988956595 (min 0.004629860673348141, max 0.005231307528557938) | " | cal=marginal,test=benign | mean | 97c8ef7aa40c4e97 |
| realized_shift, marginal→marginal | 7.692074103478052e-05 (min -2.898106393722788e-05, max 0.00018898326943728172) | " | cal=marginal,test=marginal | mean | 97c8ef7aa40c4e97 |
| n_cal, benign→benign | 27488.4 (5 distinct, 26409–29758) | " | cal=benign,test=benign | mean | 97c8ef7aa40c4e97 |
| n_cal, benign→marginal | 27488.4 (26409–29758) | " | cal=benign,test=marginal | mean | 97c8ef7aa40c4e97 |
| n_cal, marginal→benign | 28305.0 (26038–29382) | " | cal=marginal,test=benign | mean | 97c8ef7aa40c4e97 |
| n_cal, marginal→marginal | 28305.0 (26038–29382) | " | cal=marginal,test=marginal | mean | 97c8ef7aa40c4e97 |

Item 5 — coverage_target == 0.90, 8 cells (per-seed coverage_emp seeds 0..4; std is ddof=0):

| cell (model, cal→test) | coverage_emp per seed | mean | std(ddof=0) | mean escalation | mean missed_viol | mean net_speedup | mean n_test | mean n_true_viol |
|---|---|---|---|---|---|---|---|---|
| histgb benign→benign | 0.8905787917194762, 0.9008798977212905, 0.8658217241018121, 0.9111868695743859, 0.8971362431393047 | 0.8931207052512539 | 0.015194812284911343 | 0.028453664038776548 | 0.08245783789748802 | 37.386508024779815 | 27301.6 | 4205.8 |
| histgb benign→marginal | 0.891402258671686, 0.9055072265223646, 0.8964488322404774, 0.89417660399444, 0.8924089906232764 | 0.8959887824104488 | 0.00505860700222826 | 0.5370570578461142 | 0.02458876466358913 | 1.8844276908145186 | 28488.4 | 5482.0 |
| histgb marginal→benign | 0.9116257633367899, 0.9093780552004211, 0.8827205753989037, 0.9200435806417601, 0.8873165814135833 | 0.9022169111982915 | 0.014558334813608409 | 0.03271266730695665 | 0.0783137429479348 | 31.577566460839343 | 27301.6 | 4205.8 |
| histgb marginal→marginal | 0.9110311911804249, 0.9089321186382628, 0.903816400206292, 0.9084790401638745, 0.8848248758963044 | 0.9034167252170316 | 0.00959002909673717 | 0.5914081281701327 | 0.018850618838870816 | 1.6940825379736197 | 28488.4 | 5482.0 |
| ridge benign→benign | 0.8840496216922072, 0.8947130931789126, 0.9007716211026151, 0.9158612448599445, 0.8865698390770265 | 0.8963930839821412 | 0.011400530217031263 | 0.3318449880802842 | 0.052824024109992915 | 3.0354631230187 | 27301.6 | 4205.8 |
| ridge benign→marginal | 0.803609841355203, 0.8226590862387835, 0.7983128269358285, 0.7806715926549126, 0.7712355212355212 | 0.7952977736840497 | 0.017998553298487808 | 0.43399563412808817 | 0.050105163885756435 | 2.314158855221238 | 28488.4 | 5482.0 |
| ridge marginal→benign | 0.9430425932327073, 0.9196435286154772, 0.9219301002059984, 0.9331529188486276, 0.9380950602994437 | 0.9311728402404509 | 0.009067327586748887 | 0.49924734074593397 | 0.02628340714530142 | 2.015147743955697 | 27301.6 | 4205.8 |
| ridge marginal→marginal | 0.918392040871202, 0.8712240564422221, 0.8778825609666249, 0.8446850537713073, 0.9099903474903475 | 0.8844348119083406 | 0.026846519782127615 | 0.561742812419088 | 0.020159097085074913 | 1.7907197339758025 | 28488.4 | 5482.0 |

Item 6 — coverage_target == 0.95, coverage_emp:

| cell | per-seed | mean | std(ddof=0) |
|---|---|---|---|
| histgb benign→benign | 0.9515305142681568, 0.9506655636609762, 0.9343249188226668, 0.9445752644712333, 0.9532165926147182 | 0.9468625707675502 | 0.00691448525185792 |
| histgb benign→marginal | 0.9454154342565205, 0.9393794095485992, 0.9319973476755323, 0.9389494476552783, 0.955184776613348 | 0.9421852831498556 | 0.007766058121369403 |
| histgb marginal→benign | 0.9499558320851097, 0.9595021433406031, 0.9450438183024336, 0.9604259656275261, 0.9368255983272972 | 0.9503506715365939 | 0.008905135394327843 |
| histgb marginal→marginal | 0.9443398763108363, 0.9520857592985821, 0.9448905916157077, 0.9483868607798669, 0.9381549917264203 | 0.9455716159462826 | 0.004633507495933159 |
| ridge benign→benign | 0.9535660790413643, 0.9552530646010379, 0.947557697007786, 0.949565950866341, 0.9464212373520516 | 0.9504728057737161 | 0.0034104153876088395 |
| ridge benign→marginal | 0.9387268082817962, 0.9370847318309473, 0.9340602667059603, 0.908113248957495, 0.9274682846111417 | 0.9290906680774681 | 0.01117265774028089 |
| ridge marginal→benign | 0.9635518684948343, 0.964465668947883, 0.949512936000838, 0.956981689101325, 0.9613934212000149 | 0.9591811167489789 | 0.00548152268456314 |
| ridge marginal→marginal | 0.9539190642645873, 0.9536269607507364, 0.9378177263685258, 0.9400468212744165, 0.9557018753447325 | 0.9482224896005997 | 0.007651158512537223 |

Item 7 — mean(coverage_target - coverage_emp) over all 30 targets × 5 seeds; per-seed means and their population std across the 5 seeds:

| cell | mean gap (all 150 rows) | per-seed mean gap (0..4) | std(ddof=0) across seeds |
|---|---|---|---|
| histgb benign→benign | 0.008909850197815778 | 0.044464864103647375, -0.0034545386177333272, 0.03614788822550423, -0.01705438208038989, -0.015554580641949497 | 0.02619770056449242 |
| histgb benign→marginal | 0.01761268876976547 | 0.0625674464461773, -0.0028160604607621598, 0.01856025442668043, 0.001583022410807907, 0.008168781025923869 | 0.02360211647542035 |
| histgb marginal→benign | -0.01182723765659447 | -0.014026257505344959, -0.010496227219172238, 0.016304540111495174, -0.026848311250131797, -0.024069932419818543 | 0.01532005498972407 |
| histgb marginal→marginal | -0.007760277474585696 | -0.0045877027874876904, -0.010576865995387808, -0.0036087575824553723, -0.008229936352330103, -0.011798124655267505 | 0.0032173998126271836 |
| ridge benign→benign | 0.00828229053020575 | 0.025448336341872456, -0.002216164047028161, 0.010059413661068632, -0.018894844128914345, 0.02701471082403017 | 0.01730635179513674 |
| ridge benign→marginal | 0.16433507565429079 | 0.18580061844581877, 0.14957223097472427, 0.1564516564748643, 0.15653339673714242, 0.1733174756389042 | 0.013284646112985727 |
| ridge marginal→benign | -0.068567556369252 | -0.07979548335061644, -0.05747298889473817, -0.05762327898234466, -0.07846794128328588, -0.06947808933527486 | 0.009672431659052518 |
| ridge marginal→marginal | 0.01018850912596195 | -0.034788473604015414, 0.017905678471128155, 0.028559272084284975, 0.03831943326749091, 0.0009466354109211188 | 0.02567773250381259 |

Item 8 — ridge benign→marginal minus ridge benign→benign, mean coverage_emp:

| target | gap (b→m minus b→b) | larger of the two cells' std(ddof=0) | gap / larger std |
|---|---|---|---|
| 0.90 | -0.1010953102980915 | 0.017998553298487808 | -5.62 |
| 0.95 | -0.0213821376962480 | 0.011172657740280890 | -1.91 |
### S3 ROUND 1 — Agent B (re-derived, ANCHORED) — VERBATIM

**ANCHOR: PASSED — max absolute difference 0 (exact) across all 10 (family, seed) cells at coverage target 0.90 vs `data/tuned_metrics.json` M2 records, and exact match to the 5-seed aggregates in `data/tradeoff_curve_v2.json`. All numbers below are ANCHORED.**

Script: `/private/tmp/claude-501/-Users-rajansaha-contingency-screener-research/a20165b8-6ffa-4031-84e5-ca5fd47a15f6/scratchpad/agentB.py`; raw output `/private/tmp/claude-501/-Users-rajansaha-contingency-screener-research/a20165b8-6ffa-4031-84e5-ca5fd47a15f6/scratchpad/agentB_out.json`

| quantity | value | source | derivation | aggregation | sha256(16) |
|---|---|---|---|---|---|
| ANCHOR max abs diff (esc, cov_emp, missed_viol, q_hat) repro vs stored @0.90 | 0.0 | data/tuned_metrics.json M2 records | refit M2 cfg on full train (seed), q_hat on full cal, gate on full test | max over 10 (family,seed)×4 metrics | 360a9ec768152afe |
| ANCHOR ridge esc / cov / mv @0.90 (repro) | 0.490697 ±0.026608 / 0.893390 ±0.013272 / 0.029632 ±0.004394 | dataset.parquet + tune_surrogates.py | as above | mean, std ddof=0 over 5 seeds | 8f0fd1081c8603e8 |
| ANCHOR ridge esc / cov / mv @0.90 (stored) | 0.490697 ±0.026608 / 0.893390 ±0.013272 / 0.029632 ±0.004394 | data/tradeoff_curve_v2.json | stored | stored 5-seed | a40a079733ecdfcd |
| ANCHOR histgb esc / cov / mv @0.90 (repro) | 0.306251 ±0.025100 / 0.898175 ±0.009842 / 0.047167 ±0.009772 | dataset.parquet + tune_surrogates.py | as above | mean, std ddof=0 over 5 seeds | 8f0fd1081c8603e8 |
| ANCHOR histgb esc / cov / mv @0.90 (stored) | 0.306251 ±0.025100 / 0.898175 ±0.009842 / 0.047167 ±0.009772 | data/tradeoff_curve_v2.json | stored | stored 5-seed | a40a079733ecdfcd |
| **1. median n0_min_vm (1500 base scenarios)** | 0.9433575252264039 | dataset.parquet, `outaged_type=="none"` | np.median | none | 8f0fd1081c8603e8 |
| 1. base scenarios per stratum (benign ≥ med / marginal < med) | 750 / 750 | dataset.parquet | count | none | 8f0fd1081c8603e8 |
| 1. N-1 rows per stratum (post load_dataset filter, total 278955) | benign 139485 / marginal 139470 | dataset.parquet + make_splits.load_dataset | count | none | 8f0fd1081c8603e8 |
| **2. mean n0_min_vm, scenario level** | benign 0.9464851373023853 / marginal 0.9415776341685533 | dataset.parquet | mean over 750 base rows each | none | 8f0fd1081c8603e8 |
| 2. realized shift, scenario level | 0.004907503133831925 | derived | benign − marginal | none | 8f0fd1081c8603e8 |
| 2. mean n0_min_vm, N-1 row level | benign 0.9464850995814914 / marginal 0.9415776326216536 | dataset.parquet | mean over N-1 rows each | none | 8f0fd1081c8603e8 |
| 2. realized shift, N-1 row level | 0.004907466959837792 | derived | benign − marginal | none | 8f0fd1081c8603e8 |
| n_cal (benign rows in cal split), per seed 0..4 | 26409; 26780; 29758; 26597; 27898 | make_splits.make_splits(seed) | cal ∩ benign | mean 27488.4, std 1247.428170 | 00c0168639765bd7 |
| n_test SHIFT cell (marginal test rows), per seed | 29752; 29198; 27146; 27338; 29008 | make_splits | test ∩ marginal | mean 28488.4, std 1048.394887 | 00c0168639765bd7 |
| n_test CONTROL cell (benign test rows), per seed | 26037; 26594; 28641; 28453; 26783 | make_splits | test ∩ benign | mean 27301.6, std 1047.718588 | 00c0168639765bd7 |
| n_true_viol SHIFT / CONTROL, per seed | 5820,5715,5275,5205,5395 / 3989,4057,4413,4381,4189 | gate_eval.score | y<0.94 count | none | 5f854d397f86962b |
| **3. ridge @0.90 SHIFT coverage** | 0.803610; 0.822659; 0.798313; 0.780672; 0.771236 | agentB.py | q_hat on cal∩benign, eval test∩marginal | mean 0.795298, std 0.017999 | 77e838b2269b030b |
| 3. ridge @0.90 SHIFT escalation | 0.425484; 0.479348; 0.454174; 0.402809; 0.408163 | agentB.py | gate_eval.run_gate/score | mean 0.433996, std 0.028901 | 77e838b2269b030b |
| 3. ridge @0.90 SHIFT missed_viol | 0.053608; 0.053718; 0.039810; 0.051489; 0.051900 | agentB.py | gate_eval.score | mean 0.050105, std 0.005224 | 77e838b2269b030b |
| 3. ridge @0.90 CONTROL coverage | 0.884050; 0.894713; 0.900772; 0.915861; 0.886570 | agentB.py | q_hat on cal∩benign, eval test∩benign | mean 0.896393, std 0.011401 | 77e838b2269b030b |
| 3. ridge @0.90 CONTROL escalation | 0.305796; 0.365759; 0.343319; 0.351703; 0.292648 | agentB.py | gate_eval | mean 0.331845, std 0.027897 | 77e838b2269b030b |
| 3. ridge @0.90 CONTROL missed_viol | 0.059664; 0.047079; 0.060503; 0.042684; 0.054190 | agentB.py | gate_eval | mean 0.052824, std 0.006978 | 77e838b2269b030b |
| 3. histgb @0.90 SHIFT coverage | 0.891402; 0.905507; 0.896449; 0.894177; 0.892409 | agentB.py | as above | mean 0.895989, std 0.005059 | 77e838b2269b030b |
| 3. histgb @0.90 SHIFT escalation | 0.468069; 0.582026; 0.469903; 0.556661; 0.608625 | agentB.py | gate_eval | mean 0.537057, std 0.057961 | 77e838b2269b030b |
| 3. histgb @0.90 SHIFT missed_viol | 0.031787; 0.018373; 0.027299; 0.017867; 0.027618 | agentB.py | gate_eval | mean 0.024589, std 0.005516 | 77e838b2269b030b |
| 3. histgb @0.90 CONTROL coverage | 0.890579; 0.900880; 0.865822; 0.911187; 0.897136 | agentB.py | as above | mean 0.893121, std 0.015195 | 77e838b2269b030b |
| 3. histgb @0.90 CONTROL escalation | 0.025617; 0.024742; 0.020321; 0.028538; 0.043050 | agentB.py | gate_eval | mean 0.028454, std 0.007759 | 77e838b2269b030b |
| 3. histgb @0.90 CONTROL missed_viol | 0.086488; 0.079123; 0.085429; 0.060032; 0.101217 | agentB.py | gate_eval | mean 0.082458, std 0.013349 | 77e838b2269b030b |
| **4. ridge @0.95 SHIFT coverage** | 0.938727; 0.937085; 0.934060; 0.908113; 0.927468 | agentB.py | as above, target 0.95 | mean 0.929091, std 0.011173 | 77e838b2269b030b |
| 4. ridge @0.95 SHIFT escalation | 0.676761; 0.671724; 0.649451; 0.603080; 0.615761 | agentB.py | gate_eval | mean 0.643356, std 0.029467 | 77e838b2269b030b |
| 4. ridge @0.95 SHIFT missed_viol | 0.003436; 0.004374; 0.003981; 0.011335; 0.005190 | agentB.py | gate_eval | mean 0.005663, std 0.002893 | 77e838b2269b030b |
| 4. ridge @0.95 CONTROL coverage | 0.953566; 0.955253; 0.947558; 0.949566; 0.946421 | agentB.py | as above | mean 0.950473, std 0.003410 | 77e838b2269b030b |
| 4. ridge @0.95 CONTROL escalation | 0.668472; 0.692149; 0.617018; 0.672688; 0.605496 | agentB.py | gate_eval | mean 0.651164, std 0.033747 | 77e838b2269b030b |
| 4. ridge @0.95 CONTROL missed_viol | 0.010278; 0.007395; 0.010197; 0.005022; 0.014562 | agentB.py | gate_eval | mean 0.009491, std 0.003200 | 77e838b2269b030b |
| 4. histgb @0.95 SHIFT coverage | 0.945415; 0.939379; 0.931997; 0.938949; 0.955185 | agentB.py | as above | mean 0.942185, std 0.007766 | 77e838b2269b030b |
| 4. histgb @0.95 SHIFT escalation | 0.781460; 0.779437; 0.780041; 0.750018; 0.783508 | agentB.py | gate_eval | mean 0.774893, std 0.012516 | 77e838b2269b030b |
| 4. histgb @0.95 SHIFT missed_viol | 0.008247; 0.007349; 0.002085; 0.002498; 0.011677 | agentB.py | gate_eval | mean 0.006371, std 0.003633 | 77e838b2269b030b |
| 4. histgb @0.95 CONTROL coverage | 0.951531; 0.950666; 0.934325; 0.944575; 0.953217 | agentB.py | as above | mean 0.946863, std 0.006914 | 77e838b2269b030b |
| 4. histgb @0.95 CONTROL escalation | 0.250951; 0.166128; 0.159003; 0.137595; 0.453795 | agentB.py | gate_eval | mean 0.233494, std 0.116723 | 77e838b2269b030b |
| 4. histgb @0.95 CONTROL missed_viol | 0.037353; 0.044121; 0.043055; 0.038119; 0.023872 | agentB.py | gate_eval | mean 0.037304, std 0.007220 | 77e838b2269b030b |
| **5. ridge @0.90 coverage gap (control−shift) vs larger std** | 0.101095 vs 0.017999 → EXCEEDS | derived | mean diff vs max(std) | 5 seeds | 77e838b2269b030b |
| 5. histgb @0.90 coverage gap vs larger std | −0.002868 (\|gap\| 0.002868) vs 0.015195 → DOES NOT EXCEED | derived | mean diff vs max(std) | 5 seeds | 77e838b2269b030b |
| 5. ridge @0.95 coverage gap vs larger std | 0.021382 vs 0.011173 → EXCEEDS | derived | mean diff vs max(std) | 5 seeds | 77e838b2269b030b |
| 5. histgb @0.95 coverage gap vs larger std | 0.004678 vs 0.007766 → DOES NOT EXCEED | derived | mean diff vs max(std) | 5 seeds | 77e838b2269b030b |

Notes bound to the table (not prose findings): q_hat is identical between SHIFT and CONTROL within each (family, seed, target) by construction — both calibrate on cal∩benign; only the evaluation stratum differs. `load_dataset` drops the 1500 `outaged_type=="none"` base rows and 45 non-converged N-1 rows (280500 → 278955), so the row-level stratum counts are post-filter. Nothing was NOT INDEPENDENTLY DERIVABLE; the forbidden files were not opened.
### S3 ROUND 2 — the diff I computed

**B's anchor is the strongest in this whole exercise: max absolute difference 0.0 — EXACT —
across all 10 (family, seed) cells on escalation, empirical coverage, missed_viol and q_hat,
against both `data/tuned_metrics.json` and `data/tradeoff_curve_v2.json`.**

AGREE — the headline reproduces PER SEED to full stored precision:

| | A (artifact) | B (re-derived from raw) |
|---|---|---|
| ridge @0.90 SHIFT per-seed coverage | 0.803609841355203, 0.8226590862387835, 0.7983128269358285, 0.7806715926549126, 0.7712355212355212 | 0.803610, 0.822659, 0.798313, 0.780672, 0.771236 |
| ridge @0.90 SHIFT mean / std | 0.7952977736840497 / 0.017998553298487808 | 0.795298 / 0.017999 |
| ridge @0.90 CONTROL mean / std | 0.8963930839821412 / 0.011400530217031263 | 0.896393 / 0.011401 |
| ridge @0.95 SHIFT mean / std | 0.9290906680774681 / 0.01117265774028089 | 0.929091 / 0.011173 |
| ridge @0.95 CONTROL mean / std | 0.9504728057737161 / 0.0034104153876088395 | 0.950473 / 0.003410 |
| ridge shortfall over 30 targets | 0.16433507565429079 | (matches) |
| median n0_min_vm | 0.9433575252264039 | 0.9433575252264039 |

**B's independent std-rule verdicts, computed without seeing any prior analysis:**

| cell | gap | larger std | verdict |
|---|---|---|---|
| ridge @0.90 | 0.101095 | 0.017999 | **EXCEEDS** |
| ridge @0.95 | 0.021382 | 0.011173 | **EXCEEDS** |
| histgb @0.90 | 0.002868 | 0.015195 | **DOES NOT EXCEED** |
| histgb @0.95 | 0.004678 | 0.007766 | **DOES NOT EXCEED** |

DISAGREE — 1 quantity: the realized stratum shift. A: benign->marginal −0.004844344018952729.
B: 0.004907503133831925. Both agents were sent only the two values and the two paths.

### S3 ROUND 2 — Agent A response — VERBATIM

**Verdict: my value stands. These are two different quantities, not one quantity computed two ways.**

`scripts/drift_tests.py:139-140` defines the column exactly:

```python
shift = (float(df.n0_min_vm.to_numpy()[ti][tm_].mean())
         - float(df.n0_min_vm.to_numpy()[ci][cm_].mean()))
```

where `ci = splits["cal"]`, `ti = splits["test"]`, `cm_` = cal-split rows in the cal stratum, `tm_` = test-split rows in the test stratum.

Populations, precisely:

- **My number** (`realized_shift_mean_n0_min_vm`, averaged per cell over 5 seeds × 30 targets): mean `n0_min_vm` over the **test-split** rows of the **test** stratum, minus mean `n0_min_vm` over the **cal-split** rows of the **cal** stratum. It is a *test-minus-cal* difference across two disjoint, seed-dependent, scenario-grouped subsamples. Sign convention is test − cal, which is why benign→marginal is negative.
- **The other number** (0.004907503133831925): mean `n0_min_vm` of the **entire benign stratum** minus the **entire marginal stratum**, pooled across train+cal+test, one fixed value. Sign convention benign − marginal.

They cannot coincide by construction. The off-diagonal cells carry the cal/test split offset in addition to the stratum contrast, and the diagonal control cells are exactly that offset (they are nonzero: −5.64e-05 and +7.69e-05, and the artifact would be wrong if they were forced to 0).

Internal consistency check on the artifact (all four cell means):
- (b→m + m→b) − (b→b + m→m) = 3.52e-19, i.e. the four cells satisfy the additive identity exactly.
- Implied benign−marginal within the cal split = 0.004921264759987509; within the test split = 0.004921264759987509 (identical to full precision by that identity). Compare the whole-dataset value 0.004907503133831925 — a 1.4e-05 subsample difference, the expected split-sampling gap.

Independent re-derivation of the other path from `data/dataset.parquet` (median split at 0.9433575252264039, identical to the artifact's `median_n0_min_vm`): 1500 scenarios, 750 benign; scenario-level benign 0.9464851373023853, marginal 0.9415776341685533, diff **0.004907503133831925** — reproduces their scenario-level number to full precision.

One discrepancy in *their* numbers, not mine: at N-1 row level I get 140250 benign / 140250 marginal rows and diff 0.004907503133831703 (equal to the scenario-level value, since every scenario contributes the same 187 rows). Their 139485 / 139470 rows and 0.004907466959837792 imply a filter (likely converged-only) that they did not state. That filter is defensible but it is a third population, not the artifact's.

Nothing in `data/drift_n0_stratum_long.parquet` is wrong; the column is correctly named "realized" — it is the shift actually realized between the two evaluated samples, which is the quantity the coverage numbers in the same row respond to. The whole-stratum contrast is the *design* shift and is a different, also-correct number. Do not substitute one for the other in text.
### S3 OUTCOME

Round 3 not required. A's response resolves the single disagreement: **these are two different
quantities, not one computed two ways.** The artifact's column is `mean(n0_min_vm over
test-split rows of the test stratum) − mean(over cal-split rows of the cal stratum)`, a
test-minus-cal difference across disjoint seed-dependent subsamples. B's is the whole-stratum
benign-minus-marginal contrast, one fixed value pooled over train+cal+test.

A verified the artifact's internal consistency: the four cell means satisfy the additive
identity `(b→m + m→b) − (b→b + m→m) = 3.52e-19`, and the control cells are correctly nonzero
(−5.64e-05, +7.69e-05) — they carry the cal/test split offset, and the artifact would be wrong
if they were forced to zero. A then re-derived B's number independently and reproduced
0.004907503133831925 to full precision.

**Neither number is wrong; they must not be substituted for each other in text.** The artifact
value is the shift actually realized between the two evaluated samples — the quantity the
coverage numbers in the same row respond to. B's is the design shift.

A also flagged that B's N-1 row-level counts (139485 / 139470) imply a converged-only filter B
did not state; A's own row-level computation gives 140250 / 140250. A third population,
defensible but undeclared.

**The ridge 10.5-point collapse no longer rests on one code path.** It is reproduced per seed,
from raw inputs, by a pipeline anchored at exactly 0.0 against two committed artifacts.

**S3 TALLY:  AGREE 28  |  DISAGREE-resolved 1  |  UNRESOLVED 0  |  SINGLE-PATH 0**

---

## S4 — 2D element-type drift + 2E loading tilt

### S4 ROUND 1 — Agent A (derived artifacts) — VERBATIM

| quantity | value | file | column/filter | aggregation | sha256(16) |
|---|---|---|---|---|---|
| **2D row count** | 1200 | data/drift_element_type_long.parquet | all rows | count | 58bd35de57f96c58 |
| 2D distinct model | 2: histgb, ridge | same | model | unique | 58bd35de57f96c58 |
| 2D distinct cal_stratum | 2: line, trafo | same | cal_stratum | unique | 58bd35de57f96c58 |
| 2D distinct test_stratum | 2: line, trafo | same | test_stratum | unique | 58bd35de57f96c58 |
| 2D distinct seed | 5: 0,1,2,3,4 | same | seed | unique | 58bd35de57f96c58 |
| 2D distinct coverage_target | 30: 0.70…0.99 step 0.01 | same | coverage_target | unique | 58bd35de57f96c58 |
| 2D distinct test | 1: 2D_element_type | same | test | unique | 58bd35de57f96c58 |
| 2D cell sizes | 150 rows each × 8 cells (30 targets × 5 seeds) | same | model×cal_stratum×test_stratum | count | 58bd35de57f96c58 |
| 2D is_control=True cells | (line,line), (trafo,trafo) for both models | same | is_control | unique | 58bd35de57f96c58 |
| **Q2 histgb/line/trafo(shift)** coverage_emp per seed 0–4 | 0.8822319362303934, 0.8769270298047277, 0.8587599691278621, 0.8887175533281932, 0.8732973528655873 | same | coverage_target==0.90 | per-seed | 58bd35de57f96c58 |
| Q2 histgb/line/trafo mean, std(ddof=0) | 0.8759867682713527, 0.010059370424695416 | same | same | mean, pop std | 58bd35de57f96c58 |
| Q2 histgb/line/trafo mean escalation / missed_viol | 0.2920740458427171 / 0.03613742543818853 | same | same | mean over 5 seeds | 58bd35de57f96c58 |
| Q2 histgb/line/trafo n_cal / n_test / n_true_viol | 51900 (all seeds) / mean 3890.0 (values 3889,3892,3887,3891,3891) / mean 869.4 (887,889,863,860,848) | same | same | per-seed + mean | 58bd35de57f96c58 |
| **Q2 histgb/line/line(control)** coverage_emp per seed | 0.9057996146435453, 0.9050867052023122, 0.8857225433526011, 0.9101541425818882, 0.8879768786127168 | same | coverage_target==0.90 | per-seed | 58bd35de57f96c58 |
| Q2 histgb/line/line mean, std0 | 0.8989479768786127, 0.010054692082547367 | same | same | mean, pop std | 58bd35de57f96c58 |
| Q2 histgb/line/line mean escal / missed | 0.304373795761079 / 0.04863496047556137 | same | same | mean | 58bd35de57f96c58 |
| Q2 histgb/line/line n_cal / n_test / n_true_viol | 51900 / 51900 / mean 8818.4 (8922,8883,8825,8726,8736) | same | same | per-seed + mean | 58bd35de57f96c58 |
| **Q2 histgb/trafo/line(shift)** coverage_emp per seed | 0.9382466281310212, 0.9340269749518304, 0.9078034682080924, 0.9315414258188824, 0.9123506743737958 | same | coverage_target==0.90 | per-seed | 58bd35de57f96c58 |
| Q2 histgb/trafo/line mean, std0 | 0.9247938342967246, 0.012290348313601828 | same | same | mean, pop std | 58bd35de57f96c58 |
| Q2 histgb/trafo/line mean escal / missed | 0.4027552986512524 / 0.03411400036615746 | same | same | mean | 58bd35de57f96c58 |
| Q2 histgb/trafo/line n_cal / n_test / n_true_viol | mean 3893.4 (3891,3890,3896,3895,3895) / 51900 / mean 8818.4 | same | same | per-seed + mean | 58bd35de57f96c58 |
| **Q2 histgb/trafo/trafo(control)** coverage_emp per seed | 0.9084597582926202, 0.9023638232271326, 0.8790841265757654, 0.9043947571318427, 0.8933436134669751 | same | coverage_target==0.90 | per-seed | 58bd35de57f96c58 |
| Q2 histgb/trafo/trafo mean, std0 | 0.897529215738867, 0.010466388386801816 | same | same | mean, pop std | 58bd35de57f96c58 |
| Q2 histgb/trafo/trafo mean escal / missed | 0.38256223103827847 / 0.024679028205950897 | same | same | mean | 58bd35de57f96c58 |
| Q2 histgb/trafo/trafo n_cal / n_test / n_true_viol | mean 3893.4 / mean 3890.0 / mean 869.4 | same | same | mean | 58bd35de57f96c58 |
| **Q2 ridge/line/line(control)** coverage_emp per seed | 0.915587668593449, 0.8830828516377649, 0.8880346820809248, 0.8799614643545279, 0.9007899807321773 | same | coverage_target==0.90 | per-seed | 58bd35de57f96c58 |
| Q2 ridge/line/line mean, std0 | 0.8934913294797688, 0.013135350581244815 | same | same | mean, pop std | 58bd35de57f96c58 |
| Q2 ridge/line/line mean escal / missed | 0.4915722543352602 / 0.03042375467409104 | same | same | mean | 58bd35de57f96c58 |
| Q2 ridge/line/line n_cal / n_test / n_true_viol | 51900 / 51900 / mean 8818.4 | same | same | mean | 58bd35de57f96c58 |
| **Q2 ridge/line/trafo(shift)** coverage_emp per seed | 0.9138596040113139, 0.8812949640287769, 0.8857730897864677, 0.878437419686456, 0.9059367771781033 | same | coverage_target==0.90 | per-seed | 58bd35de57f96c58 |
| Q2 ridge/line/trafo mean, std0 | 0.8930603709382237, 0.014168767792043967 | same | same | mean, pop std | 58bd35de57f96c58 |
| Q2 ridge/line/trafo mean escal / missed | 0.48015509390044364 / 0.02156696650830225 | same | same | mean | 58bd35de57f96c58 |
| Q2 ridge/line/trafo n_cal / n_test / n_true_viol | 51900 / mean 3890.0 / mean 869.4 | same | same | mean | 58bd35de57f96c58 |
| **Q2 ridge/trafo/line(shift)** coverage_emp per seed | 0.9251252408477842, 0.8869749518304432, 0.8801734104046243, 0.8795953757225433, 0.9015606936416185 | same | coverage_target==0.90 | per-seed | 58bd35de57f96c58 |
| Q2 ridge/trafo/line mean, std0 | 0.8946859344894028, 0.017155822671935425 | same | same | mean, pop std | 58bd35de57f96c58 |
| Q2 ridge/trafo/line mean escal / missed | 0.4953487475915222 / 0.02989147500297399 | same | same | mean | 58bd35de57f96c58 |
| Q2 ridge/trafo/line n_cal / n_test / n_true_viol | mean 3893.4 / 51900 / mean 8818.4 | same | same | mean | 58bd35de57f96c58 |
| **Q2 ridge/trafo/trafo(control)** coverage_emp per seed | 0.9220879403445615, 0.8856628982528263, 0.8790841265757654, 0.8776664096633257, 0.9069647905422771 | same | coverage_target==0.90 | per-seed | 58bd35de57f96c58 |
| Q2 ridge/trafo/trafo mean, std0 | 0.8942932330757511, 0.017408991798826313 | same | same | mean, pop std | 58bd35de57f96c58 |
| Q2 ridge/trafo/trafo mean escal / missed | 0.48606638130368535 / 0.021118987872008457 | same | same | mean | 58bd35de57f96c58 |
| Q2 ridge/trafo/trafo n_cal / n_test / n_true_viol | mean 3893.4 / mean 3890.0 / mean 869.4 | same | same | mean | 58bd35de57f96c58 |
| **Q3 histgb/line/line** mean(target−emp); std0 of per-seed means | -0.0014254335260115703; 0.012636515059457511 | same | all 30 targets × 5 seeds | mean of 150; pop std of 5 per-seed means | 58bd35de57f96c58 |
| Q3 histgb/line/trafo | 0.02281042403482064; 0.014910511949970336 | same | same | same | 58bd35de57f96c58 |
| Q3 histgb/trafo/line | -0.022445343609505463; 0.012874326021653185 | same | same | same | 58bd35de57f96c58 |
| Q3 histgb/trafo/trafo | 0.0015116975024007542; 0.015222686391703946 | same | same | same | 58bd35de57f96c58 |
| Q3 ridge/line/line | 0.00593114964675658; 0.010648106333140556 | same | same | same | 58bd35de57f96c58 |
| Q3 ridge/line/trafo | 0.0037759335639549986; 0.01104209940910968 | same | same | same | 58bd35de57f96c58 |
| Q3 ridge/trafo/line | 0.007160308285163769; 0.013458201650010397 | same | same | same | 58bd35de57f96c58 |
| Q3 ridge/trafo/trafo | 0.005034914421218128; 0.01314554108250376 | same | same | same | 58bd35de57f96c58 |
| Q3 per-seed means histgb/line/line (s0..s4) | 0.0113359023763648, -0.007428387925497774, 0.016056518946692352, -0.013774566473988444, -0.013316634553628784 | same | same | per-seed mean over 30 targets | 58bd35de57f96c58 |
| Q3 per-seed means histgb/line/trafo | 0.03301748521470815, 0.02108770126755738, 0.045463082068433226, 0.009053799366058416, 0.005430052257346004 | same | same | same | 58bd35de57f96c58 |
| Q3 per-seed means histgb/trafo/line | -0.020389852280025704, -0.029477199743095702, 0.0016750160565189483, -0.03425690430314708, -0.029777777777777785 | same | same | same | 58bd35de57f96c58 |
| Q3 per-seed means histgb/trafo/trafo | 0.00207551212822491, -0.0021051730044535683, 0.030121344653117225, -0.01155786858562496, -0.010975327679259834 | same | same | same | 58bd35de57f96c58 |
| Q3 per-seed means ridge/line/line | -0.01392100192678228, 0.012077713551701988, 0.016944123314065505, 0.005028901734104048, 0.00952601156069364 | same | same | same | 58bd35de57f96c58 |
| Q3 per-seed means ridge/line/trafo | -0.016121110825404992, 0.013961973278520034, 0.014247920418488968, 0.0032540906365115937, 0.003536794311659386 | same | same | same | 58bd35de57f96c58 |
| Q3 per-seed means ridge/trafo/line | -0.016744380218368663, 0.00906486833654463, 0.024192035966602434, 0.005894026974951823, 0.013394990366088622 | same | same | same | 58bd35de57f96c58 |
| Q3 per-seed means ridge/trafo/trafo | -0.018555326990657418, 0.010930113052415206, 0.021408541291484427, 0.004316371112824454, 0.007074873640023971 | same | same | same | 58bd35de57f96c58 |
| **Q4 histgb (line→trafo) − control matched on TEST stratum (trafo,trafo)** | -0.0215424474675143; larger std 0.010466388386801816 | same | coverage_target==0.90 | diff of 5-seed means; max of two pop stds | 58bd35de57f96c58 |
| Q4 histgb (trafo→line) − control (line,line) [test-matched] | +0.0258458574181119; larger std 0.012290348313601828 | same | same | same | 58bd35de57f96c58 |
| Q4 ridge (line→trafo) − control (trafo,trafo) [test-matched] | -0.0012328621375274; larger std 0.017408991798826313 | same | same | same | 58bd35de57f96c58 |
| Q4 ridge (trafo→line) − control (line,line) [test-matched] | +0.0011946050096340; larger std 0.017155822671935425 | same | same | same | 58bd35de57f96c58 |
| Q4-alt histgb (line→trafo) − control matched on CAL stratum (line,line) | -0.0229612086072600; larger std 0.010059370424695416 | same | same | same | 58bd35de57f96c58 |
| Q4-alt histgb (trafo→line) − control (trafo,trafo) | +0.0272646185578576; larger std 0.012290348313601828 | same | same | same | 58bd35de57f96c58 |
| Q4-alt ridge (line→trafo) − control (line,line) | -0.0004309585415451; larger std 0.014168767792043967 | same | same | same | 58bd35de57f96c58 |
| Q4-alt ridge (trafo→line) − control (trafo,trafo) | +0.0003927014136517; larger std 0.017408991798826313 | same | same | same | 58bd35de57f96c58 |
| **2E row count** | 900 | data/drift_loading_tilt_long.parquet | all rows | count | 3c744f658e5a3973 |
| 2E distinct cell | 3: tilted_test_unweighted_cal (is_control False), tilted_test_weighted_cal (False), untilted_test_unweighted_cal (True) | same | cell, is_control | unique | 3c744f658e5a3973 |
| 2E distinct model / seed / coverage_target / lam / test | 2 (histgb, ridge) / 5 (0–4) / 30 (0.70–0.99) / 1 (3.0) / 1 (2E_loading_tilt) | same | — | unique | 3c744f658e5a3973 |
| 2E cell sizes | 150 rows each × 6 (model,cell) groups | same | model×cell | count | 3c744f658e5a3973 |
| 2E n_cal column | NOT PRESENT in file | same | — | — | 3c744f658e5a3973 |
| **Q6 tilt_lambda / ess_floor** | 3.0 / 0.1 | data/drift_loading_tilt_diagnostics.json | top-level | — | 2ad3edeee5d6b581 |
| Q6 seed 0 | ratio_finite true; ess_fraction 0.8220457778183725; w_cal_min 0.27627676288964; w_cal_max 5.549167122038629; w_test_min 0.1926252065462984; w_test_max 3.868980698422327; agg_min 1.0194063186645508; agg_max 1.0958797931671143 | same | diagnostics[0] | — | 2ad3edeee5d6b581 |
| Q6 seed 1 | true; 0.8010768885427668; 0.22152321529090388; 4.449412720068701; 0.19181086457691993; 3.8526242027282747; 1.0189082622528076; 1.096228003501892 | same | diagnostics[1] | — | 2ad3edeee5d6b581 |
| Q6 seed 2 | true; 0.7902919041919305; 0.1605668251536922; 3.225070895263503; 0.2058175888987683; 4.133956781267671; 1.023223876953125; 1.0950603485107422 | same | diagnostics[2] | — | 2ad3edeee5d6b581 |
| Q6 seed 3 | true; 0.7893723143295119; 0.19948150014174817; 4.006693036589949; 0.22641605696476572; 4.547688072168365; 1.028885841369629; 1.0950603485107422 | same | diagnostics[3] | — | 2ad3edeee5d6b581 |
| Q6 seed 4 | true; 0.8103907736063903; 0.22964815225593574; 4.6126064414784205; 0.18201510009022726, 3.6558710134399584; 1.0217981338500977; 1.092663049697876 | same | diagnostics[4] | — | 2ad3edeee5d6b581 |
| **Q7 histgb/untilted_test_unweighted_cal (control)** coverage_emp s0..s4 | 0.9047123985014968, 0.9041439632922282, 0.8850269776112715, 0.9092864440501156, 0.8877059023856895 | data/drift_loading_tilt_long.parquet | coverage_target==0.90 | per-seed | 3c744f658e5a3973 |
| Q7 histgb/untilted mean, std0 | 0.8981751371681603, 0.009841776143853134 | same | same | mean, pop std | 3c744f658e5a3973 |
| Q7 histgb/untilted mean escal / missed / q_hat | 0.3062513593744674 / 0.04716684182384393 / 0.002290702766310826 | same | same | mean over 5 seeds | 3c744f658e5a3973 |
| Q7 histgb/tilted_test_unweighted_cal coverage_emp s0..s4 | 0.9025255874814031, 0.8916511327788931, 0.8847401724416083, 0.909788317112079, 0.8856984101378359 | same | same | per-seed | 3c744f658e5a3973 |
| Q7 histgb/tilted_unweighted mean, std0 | 0.8948807239903639, 0.009780145226649115 | same | same | mean, pop std | 3c744f658e5a3973 |
| Q7 histgb/tilted_unweighted mean escal / missed / q_hat | 0.3216485573113859 / 0.047797563398532326 / 0.002290702766310826 | same | same | mean | 3c744f658e5a3973 |
| Q7 histgb/tilted_test_weighted_cal coverage_emp s0..s4 | 0.9090860205416839, 0.8971178663607686, 0.8860845716744045, 0.9150221361868401, 0.8857163341757631 | same | same | per-seed | 3c744f658e5a3973 |
| Q7 histgb/tilted_weighted mean, std0 | 0.898605385787892, 0.011869831928670716 | same | same | mean, pop std | 3c744f658e5a3973 |
| Q7 histgb/tilted_weighted mean escal / missed / q_hat | 0.3301877432476122 / 0.04611684269370284 / 0.0023766851066798324 | same | same | mean | 3c744f658e5a3973 |
| Q7 ridge/untilted (control) coverage_emp s0..s4 | 0.9155926795604868, 0.8832807570977917, 0.8870166884758097, 0.8798372497356204, 0.9012206269828467 | same | same | per-seed | 3c744f658e5a3973 |
| Q7 ridge/untilted mean, std0 | 0.8933896003705112, 0.013272306727773393 | same | same | mean, pop std | 3c744f658e5a3973 |
| Q7 ridge/untilted mean escal / missed / q_hat | 0.4906972404572077 / 0.029631523339489742 / 0.005198231037165079 | same | same | mean | 3c744f658e5a3973 |
| Q7 ridge/tilted_unweighted coverage_emp s0..s4 | 0.9146068221333955, 0.8815421565815887, 0.8855826626274939, 0.8910756215160152, 0.9010055385277195 | same | same | per-seed | 3c744f658e5a3973 |
| Q7 ridge/tilted_unweighted mean, std0 | 0.8947625602772427, 0.01187781645098504 | same | same | mean, pop std | 3c744f658e5a3973 |
| Q7 ridge/tilted_unweighted mean escal / missed / q_hat | 0.49018436024292483 / 0.029305737024923645 / 0.005198231037165079 | same | same | mean | 3c744f658e5a3973 |
| Q7 ridge/tilted_weighted coverage_emp s0..s4 | 0.9163096667801897, 0.886435331230284, 0.8830551920698371, 0.8903586599989246, 0.8997867039486656 | same | same | per-seed | 3c744f658e5a3973 |
| Q7 ridge/tilted_weighted mean, std0 | 0.8951891108055801, 0.011953322911391362 | same | same | mean, pop std | 3c744f658e5a3973 |
| Q7 ridge/tilted_weighted mean escal / missed / q_hat | 0.4901377092305076 / 0.02926178603002922 / 0.005197752594625826 | same | same | mean | 3c744f658e5a3973 |
| Q7 q_hat identity: untilted vs tilted_unweighted | IDENTICAL per seed, both models (histgb s0..s4: 0.002335618678972362, 0.002353357097683695, 0.0020534393537054996, 0.002262051382869279, 0.002449047318323294; ridge: 0.00552461357270162, 0.0051332624013122885, 0.004943555243710485, 0.0049365181872691455, 0.00545320578083186) | same | coverage_target==0.90 | per-seed compare | 3c744f658e5a3973 |
| Q7 q_hat weighted-cal per seed | histgb: 0.002532530884947426, 0.0024736132296192537, 0.0020621894841291732, 0.002364726406086204, 0.0024503655286171044; ridge: 0.0055923248319244, 0.005231657767936215, 0.0048767865756425, 0.004884506998184324, 0.005403486799441692 | same | same | per-seed | 3c744f658e5a3973 |
| Q7 n_test (all cells) | 55789, 55792, 55787, 55791, 55791 (seeds 0–4) | same | same | per-seed | 3c744f658e5a3973 |
| Q7 n_true_viol tilted cells | 10000, 10012, 9993, 9579, 9884 | same | tilted_* cells | per-seed | 3c744f658e5a3973 |
| Q7 n_true_viol untilted control | 9809, 9772, 9688, 9586, 9584 | same | untilted cell | per-seed | 3c744f658e5a3973 |
| **Q8 histgb/untilted** mean(target−emp); std0 of per-seed means | -0.001210062187779429; 0.012726949646936454 | same | all 30 targets × 5 seeds | mean of 150; pop std of 5 per-seed means | 3c744f658e5a3973 |
| Q8 histgb/tilted_unweighted | 0.0006243005235913087; 0.013417838442768731 | same | same | same | 3c744f658e5a3973 |
| Q8 histgb/tilted_weighted | -0.002060867015001681; 0.01388033099830058 | same | same | same | 3c744f658e5a3973 |
| Q8 ridge/untilted | 0.005856662478539314; 0.010820969460643317 | same | same | same | 3c744f658e5a3973 |
| Q8 ridge/tilted_unweighted | 0.004624193051439177; 0.011180965773958629 | same | same | same | 3c744f658e5a3973 |
| Q8 ridge/tilted_weighted | 0.003815958682152921; 0.012865821476068656 | same | same | same | 3c744f658e5a3973 |
| **Q9 realized_mean_agg_cal / _test seed 0** | 1.0588607681058042 / 1.063706984571498 | same | seed==0, all 3 cells | nunique across cells = 1 | 3c744f658e5a3973 |
| Q9 seed 1 | 1.0590586759535978 / 1.0641375236471744 | same | seed==1 | nunique = 1 | 3c744f658e5a3973 |
| Q9 seed 2 | 1.0593918037804253 / 1.0638078221657312 | same | seed==2 | nunique = 1 | 3c744f658e5a3973 |
| Q9 seed 3 | 1.0593249775023965 / 1.06408076989636 | same | seed==3 | nunique = 1 | 3c744f658e5a3973 |
| Q9 seed 4 | 1.0582818039152206 / 1.0643631359839882 | same | seed==4 | nunique = 1 | 3c744f658e5a3973 |
| Q9 variation across cell within seed | NO — constant across all 3 cells (and both models) within each seed; ess_fraction and lam likewise constant | same | groupby(seed, cell) | nunique==1 | 3c744f658e5a3973 |

Full file paths: `/Users/rajansaha/contingency-screener-research/data/drift_element_type_long.parquet`, `/Users/rajansaha/contingency-screener-research/data/drift_loading_tilt_long.parquet`, `/Users/rajansaha/contingency-screener-research/data/drift_loading_tilt_diagnostics.json`.
### S4 ROUND 1 — Agent B (re-derived, ANCHORED) — VERBATIM

ANCHORED.

```
ANCHOR | quantity | my re-derivation | data/tradeoff_curve_v2.json | max abs diff
-------|----------|------------------|-----------------------------|-------------
ridge  M2 cov=0.90 escalation      | 0.4906972405 | 0.4906972405 | 0.0
ridge  M2 cov=0.90 coverage_emp    | 0.8933896004 | 0.8933896004 | 0.0
ridge  M2 cov=0.90 missed_viol     | 0.0296315233 | 0.0296315233 | 0.0
ridge  M2 cov=0.90 q_hat           | 0.0051982310 | 0.0051982310 | 0.0
histgb M2 cov=0.90 escalation      | 0.3062513594 | 0.3062513594 | 0.0
histgb M2 cov=0.90 coverage_emp    | 0.8981751372 | 0.8981751372 | 0.0
histgb M2 cov=0.90 missed_viol     | 0.0471668418 | 0.0471668418 | 0.0
histgb M2 cov=0.90 q_hat           | 0.0022907028 | 0.0022907028 | 0.0
MAX ABS DIFF over 2 families x 30 coverage targets x {esc, cov_emp, missed, q_hat, and all three stds} = 0.000e+00 (bit-exact)
```

Derivation of the anchor: `data/dataset.parquet` -> `make_splits.load_dataset` (278955 rows, 1500 scenarios) -> `build_design_matrix` (805 cols) -> `make_splits(groups, seed)` -> `select_features` on train -> refit the stored M2 config from `data/tuned_metrics.json["selections"][seed][family]["m2"]` (ridge: alpha1/alpha0.001 x3/alpha0.01; histgb: rand00/rand13/rand20/rand01/rand16) on the full train split -> `gate_eval.calibrate_qhat` on full cal -> `gate_eval.run_gate`/`score` on full test -> mean/popstd over 5 seeds. All numbers below are ANCHORED.

sha256(16) convention: for repo files, the file hash; for derived cells, `sha256(json.dumps(per-seed record list, sort_keys, compact))[:16]`.

```
quantity | value | source | derivation | aggregation | sha256(16)
=== INPUTS ===
dataset | 280500x634 rows, 278955 after (type!=none & converged) | data/dataset.parquet | read_parquet | - | 8f0fd1081c8603e8
M2 configs | ridge {0:alpha1, 1..3:alpha0.001, 4:alpha0.01}; histgb {0:rand00,1:rand13,2:rand20,3:rand01,4:rand16} | data/tuned_metrics.json .selections | key lookup | - | 360a9ec768152afe
anchor target | 30 targets x 2 models | data/tradeoff_curve_v2.json | - | - | a40a079733ecdfcd
gate code | calibrate_qhat/run_gate/score, LIMIT=0.94 | feasibility/gate_eval.py | - | - | 5f854d397f86962b
split code | GroupShuffleSplit 0.6/0.2/0.2 on scenario_id | feasibility/make_splits.py | - | - | 00c0168639765bd7
fit code | fit_ridge/fit_histgb/find_config reused verbatim | scripts/tune_surrogates.py | - | - | 9395044201a93337
element type counts (all rows) | line 259500, trafo 19500, none 1500 | data/dataset.parquet | value_counts(outaged_type) | - | 8f0fd1081c8603e8

=== 2D ELEMENT-TYPE DRIFT (cal_type -> test_type), cov target 0.90 ===
(format: mean +- population std ddof=0 over seeds 0-4; n_cal/n_test are seed means)
ridge  line->line   | n_cal 51900 n_test 51900 | cov_emp 0.893491+-0.013135 | esc 0.491572+-0.026227 | missed 0.030424+-0.004231 | q_hat 0.005199+-0.000243 | dataset.parquet | mask etype, calibrate on cal-subset, gate on test-subset | 5 seeds | 577c0ac3ebd9450c
ridge  line->trafo  | n_cal 51900 n_test 3890  | cov_emp 0.893060+-0.014169 | esc 0.480155+-0.024940 | missed 0.021567+-0.006579 | q_hat 0.005199+-0.000243 | same | same | 5 seeds | 0783e0c5483b2f28
ridge  trafo->line  | n_cal  3893 n_test 51900 | cov_emp 0.894686+-0.017156 | esc 0.495349+-0.039036 | missed 0.029891+-0.005335 | q_hat 0.005247+-0.000384 | same | same | 5 seeds | 3db32b193d5cc68b
ridge  trafo->trafo | n_cal  3893 n_test 3890  | cov_emp 0.894293+-0.017409 | esc 0.486066+-0.038685 | missed 0.021119+-0.007394 | q_hat 0.005247+-0.000384 | same | same | 5 seeds | cca1f86e950f6d41
histgb line->line   | n_cal 51900 n_test 51900 | cov_emp 0.898948+-0.010055 | esc 0.304374+-0.026352 | missed 0.048635+-0.010227 | q_hat 0.002265+-0.000133 | same | same | 5 seeds | 0f8bf237f4c2777c
histgb line->trafo  | n_cal 51900 n_test 3890  | cov_emp 0.875987+-0.010059 | esc 0.292074+-0.023088 | missed 0.036137+-0.005456 | q_hat 0.002265+-0.000133 | same | same | 5 seeds | 1c367cd5c1166bbe
histgb trafo->line  | n_cal  3893 n_test 51900 | cov_emp 0.924794+-0.012290 | esc 0.402755+-0.049190 | missed 0.034114+-0.009201 | q_hat 0.003041+-0.000318 | same | same | 5 seeds | ba92484fb0a534c7
histgb trafo->trafo | n_cal  3893 n_test 3890  | cov_emp 0.897529+-0.010466 | esc 0.382562+-0.045965 | missed 0.024679+-0.007334 | q_hat 0.003041+-0.000318 | same | same | 5 seeds | 838931a7a7fb74ce

=== 2D mean over the 30 targets of (target - coverage_emp) ===
ridge  line->line   |  0.005931+-0.010648 | as above | mean over 30 coverage_levels, then mean/std over seeds | 5 seeds | 577c0ac3ebd9450c
ridge  line->trafo  |  0.003776+-0.011042 | | | | 0783e0c5483b2f28
ridge  trafo->line  |  0.007160+-0.013458 | | | | 3db32b193d5cc68b
ridge  trafo->trafo |  0.005035+-0.013146 | | | | cca1f86e950f6d41
histgb line->line   | -0.001425+-0.012637 | | | | 0f8bf237f4c2777c
histgb line->trafo  |  0.022810+-0.014911 | | | | 1c367cd5c1166bbe
histgb trafo->line  | -0.022445+-0.012874 | | | | ba92484fb0a534c7
histgb trafo->trafo |  0.001512+-0.015223 | | | | 838931a7a7fb74ce

=== 2D PER SEED (cov_emp / esc / missed / n_cal / n_test), seeds 0..4 ===
ridge line->line   | cov .915588 .883083 .888035 .879961 .900790 | esc .539884 .488632 .466532 .469942 .492871 | miss .027460 .034560 .035921 .029452 .024725 | n_cal 51900 all | n_test 51900 all | 577c0ac3ebd9450c
ridge line->trafo  | cov .913860 .881295 .885773 .878437 .905937 | esc .527385 .471223 .458451 .462092 .481624 | miss .015784 .033746 .023175 .017442 .017689 | n_cal 51900 all | n_test 3889 3892 3887 3891 3891 | 0783e0c5483b2f28
ridge trafo->line  | cov .925125 .886975 .880173 .879595 .901561 | esc .566146 .495626 .452967 .466879 .495125 | miss .024210 .031971 .038640 .030140 .024496 | n_cal 3891 3890 3896 3895 3895 | n_test 51900 all | 3db32b193d5cc68b
ridge trafo->trafo | cov .922088 .885663 .879084 .877666 .906965 | esc .558241 .480473 .446360 .460293 .484965 | miss .012401 .033746 .024334 .018605 .016509 | n_cal 3891 3890 3896 3895 3895 | n_test 3889 3892 3887 3891 3891 | cca1f86e950f6d41
histgb line->line  | cov .905800 .905087 .885723 .910154 .887977 | esc .317919 .316994 .252909 .308054 .325992 | miss .046850 .044354 .053144 .033922 .064904 | n_cal 51900 all | n_test 51900 all | 0f8bf237f4c2777c
histgb line->trafo | cov .882232 .876927 .858760 .888718 .873297 | esc .309591 .304471 .246463 .299152 .300694 | miss .036077 .035996 .038239 .026744 .043632 | n_cal 51900 all | n_test 3889 3892 3887 3891 3891 | 1c367cd5c1166bbe
histgb trafo->line | cov .938247 .934027 .907803 .931541 .912351 | esc .474335 .435626 .330809 .376763 .396243 | miss .028133 .029832 .039547 .023722 .049336 | n_cal 3891 3890 3896 3895 3895 | n_test 51900 all | ba92484fb0a534c7
histgb trafo->trafo| cov .908460 .902364 .879084 .904395 .893344 | esc .449987 .414440 .315668 .365459 .367258 | miss .015784 .024747 .034762 .017442 .030660 | n_cal 3891 3890 3896 3895 3895 | n_test 3889 3892 3887 3891 3891 | 838931a7a7fb74ce

=== 2E WEIGHT DIAGNOSTICS. w(a)=exp(3.0*(a-a_min)/(a_max-a_min)) on agg_loading ===
SCHEME (i) = each array normalised by its OWN min/max. SCHEME (ii) = BOTH arrays normalised by the TEST split's min/max.
WHY (ii) IS THE CORRECT LIKELIHOOD RATIO: the tilt defines the target law Q on the TEST set, so w is one fixed function of a with the test split's (a_min,a_max) fixed in its definition; dQ/dP(a) = w(a)/E_P[w] and the conformal quantile is invariant to the constant. Under (i) w_cal and w_test are DIFFERENT functions of a (different exponent scaling), so w_cal is not dQ/dP evaluated at the calibration points; the tell is that under (i) both arrays span exactly [1, e^3=20.085537] by construction regardless of their actual loading spread. Note range normalisation is NOT constant-invariant: changing the range changes the effective lambda, so only the test-defined range is right.
scheme(i)  seed0 | w_cal [1.000000, 20.085537] w_test [1.000000, 20.085537] ESS_test 0.822046 ESS_cal 0.845030 finite&positive TRUE | cal rng [1.014225,1.123857] test rng [1.019406,1.095880] | | | af6502d34c6d216f
scheme(i)  seed1 | w_cal [1.000000, 20.085537] w_test [1.000000, 20.085537] ESS_test 0.801077 ESS_cal 0.793522 TRUE | cal rng [1.026955,1.095880] test rng [1.018908,1.096228] | | | 33d0a8776d9553c7
scheme(i)  seed2 | w_cal [1.000000, 20.085537] w_test [1.000000, 20.085537] ESS_test 0.790292 ESS_cal 0.809850 TRUE | cal rng [1.014225,1.092663] test rng [1.023224,1.095060] | | | 0a81531eb1f4dfe4
scheme(i)  seed3 | w_cal [1.000000, 20.085537] w_test [1.000000, 20.085537] ESS_test 0.789372 ESS_cal 0.772269 TRUE | cal rng [1.023224,1.095880] test rng [1.028886,1.095060] | | | abefcf19f22cd9d4
scheme(i)  seed4 | w_cal [1.000000, 20.085537] w_test [1.000000, 20.085537] ESS_test 0.810391 ESS_cal 0.797740 TRUE | cal rng [1.025844,1.096853] test rng [1.021798,1.092663] | | | 36c396fca9b6d319
scheme(ii) seed0 | w_cal [0.816078, 60.192080] w_test [1.000000, 20.085537] ESS_test 0.822046 ESS_cal 0.627898 TRUE | common rng [1.019406,1.095880] | | | 6f8056b002085715
scheme(ii) seed1 | w_cal [1.366465, 19.815996] w_test [1.000000, 20.085537] ESS_test 0.801077 ESS_cal 0.834377 TRUE | common rng [1.018908,1.096228] | | | 57421dd85623110f
scheme(ii) seed2 | w_cal [0.686745, 18.172058] w_test [1.000000, 20.085537] ESS_test 0.790292 ESS_cal 0.775995 TRUE | common rng [1.023224,1.095060] | | | c76f79cb2f7788ad
scheme(ii) seed3 | w_cal [0.773613, 20.845733] w_test [1.000000, 20.085537] ESS_test 0.789372 ESS_cal 0.729783 TRUE | common rng [1.028886,1.095060] | | | 421f255715847161
scheme(ii) seed4 | w_cal [1.186825, 23.984158] w_test [1.000000, 20.085537] ESS_test 0.810391 ESS_cal 0.796901 TRUE | common rng [1.021798,1.092663] | | | 22880863d41db994
ESS definition | (sum w)^2/(n*sum w^2) on the TEST weights | identical under (i) and (ii) because w_test uses the test range in both | | | (as above)
n_cal / n_test per seed | 55791/55789, 55790/55792, 55796/55787, 55795/55791, 55795/55791 | make_splits | | | (as above)

=== 2E REALIZED MEAN agg_loading OF TEST SET ===
seed0 | untilted 1.05909750 -> tilted 1.06373910 | data/dataset.parquet | resample len(test) with p ∝ w_test, RandomState(1000+seed) | per seed | af6502d34c6d216f
seed1 | untilted 1.05894590 -> tilted 1.06421141 | | | | 33d0a8776d9553c7
seed2 | untilted 1.05841135 -> tilted 1.06380070 | | | | 0a81531eb1f4dfe4
seed3 | untilted 1.05936834 -> tilted 1.06411459 | | | | abefcf19f22cd9d4
seed4 | untilted 1.05980732 -> tilted 1.06434153 | | | | 36c396fca9b6d319
(identical for (i) and (ii): the resampling probabilities depend only on w_test, which is the same array in both schemes. All five pairs differ; shift +0.0046 to +0.0054 pu, ~0.4x the agg_loading std 0.011371.)

=== 2E GATE CELLS at cov target 0.90 (mean +- popstd over 5 seeds) ===
weighted q_hat = weighted split-conformal quantile: p_i = w_cal_i/(sum w_cal + mean(w_test)); smallest calibration score with cumsum(p) >= target (the mean-test-weight denominator is the finite-sample (n+1)-analogue; it reduces to calibrate_qhat when all weights are equal).
(i)  ridge  untilted/unweighted | cov 0.893390+-0.013272 esc 0.490697+-0.026608 miss 0.029632+-0.004394 q 0.005198+-0.000249 gap30 +0.005857+-0.010821 | 33cfda1e3d57b509
(i)  ridge  tilted/unweighted   | cov 0.895031+-0.011627 esc 0.494042+-0.029642 miss 0.028015+-0.006512 q 0.005198+-0.000249 gap30 +0.003800+-0.011203 | d43fd68bbe59296f
(i)  ridge  tilted/WEIGHTED     | cov 0.895325+-0.011825 esc 0.494020+-0.032291 miss 0.028108+-0.005519 q 0.005196+-0.000282 gap30 +0.003046+-0.013059 | 2ca26fbc54642e1a
(i)  histgb untilted/unweighted | cov 0.898175+-0.009842 esc 0.306251+-0.025100 miss 0.047167+-0.009772 q 0.002291+-0.000133 gap30 -0.001210+-0.012727 | dd4c06cbf1d40981
(i)  histgb tilted/unweighted   | cov 0.894730+-0.008878 esc 0.320301+-0.024940 miss 0.048174+-0.009230 q 0.002291+-0.000133 gap30 +0.001148+-0.013198 | 6318a49f968b890a
(i)  histgb tilted/WEIGHTED     | cov 0.898484+-0.010891 esc 0.329467+-0.030671 miss 0.046471+-0.010038 q 0.002376+-0.000167 gap30 -0.001456+-0.013725 | d9549b69df23fa25
(ii) ridge  untilted/unweighted | cov 0.893390+-0.013272 esc 0.490697+-0.026608 miss 0.029632+-0.004394 q 0.005198+-0.000249 gap30 +0.005857+-0.010821 | 33cfda1e3d57b509
(ii) ridge  tilted/unweighted   | cov 0.895031+-0.011627 esc 0.494042+-0.029642 miss 0.028015+-0.006512 q 0.005198+-0.000249 gap30 +0.003800+-0.011203 | d43fd68bbe59296f
(ii) ridge  tilted/WEIGHTED     | cov 0.895390+-0.012412 esc 0.494250+-0.033620 miss 0.028131+-0.005605 q 0.005199+-0.000300 gap30 +0.003156+-0.013997 | 8956b9783d0fb2c7
(ii) histgb untilted/unweighted | cov 0.898175+-0.009842 esc 0.306251+-0.025100 miss 0.047167+-0.009772 q 0.002291+-0.000133 gap30 -0.001210+-0.012727 | dd4c06cbf1d40981
(ii) histgb tilted/unweighted   | cov 0.894730+-0.008878 esc 0.320301+-0.024940 miss 0.048174+-0.009230 q 0.002291+-0.000133 gap30 +0.001148+-0.013198 | 6318a49f968b890a
(ii) histgb tilted/WEIGHTED     | cov 0.899211+-0.011622 esc 0.332730+-0.035820 miss 0.045935+-0.010209 q 0.002409+-0.000201 gap30 -0.002001+-0.013807 | 908740ee37bfecf8
(the two untilted and two tilted/unweighted rows are byte-identical across schemes by construction; only the WEIGHTED rows differ)

=== 2E WEIGHTED-CELL PER-SEED q_hat, seeds 0..4 ===
(i)  ridge  | .00558903 .00522840 .00487655 .00488370 .00540034 | 2ca26fbc54642e1a
(ii) ridge  | .00563734 .00521994 .00486668 .00487203 .00540017 | 8956b9783d0fb2c7
(i)  histgb | .00253204 .00247318 .00206054 .00236243 .00245033 | d9549b69df23fa25
(ii) histgb | .00268591 .00246716 .00206430 .00237777 .00245032 | 908740ee37bfecf8

=== SCRIPTS (scratch, absolute paths) ===
fit_preds.py | /private/tmp/claude-501/-Users-rajansaha-contingency-screener-research/a20165b8-6ffa-4031-84e5-ca5fd47a15f6/scratchpad/fit_preds.py | 48ba040879c2f185
anchor.py    | .../scratchpad/anchor.py   | b85a7db0aab9b781
drift2d.py   | .../scratchpad/drift2d.py  | 99c59cc45f3a8eb0
tilt.py      | .../scratchpad/tilt.py     | 0098e8c413ab813d
drift2d.json | .../scratchpad/drift2d.json| aac357c68b4287c3
tilt.json    | .../scratchpad/tilt.json   | ee128bf7cc2c4635

=== NOT INDEPENDENTLY DERIVABLE ===
(none)
```

Three things worth flagging to the lead, since they are the substance rather than the arithmetic:

1. The (i)-vs-(ii) question resolves against (i). Under scheme (i) both weight arrays span exactly [1, e^3] no matter what the two splits' loading distributions are, so `w_cal` is not the density ratio at the calibration points; it is a *different* function of `agg_loading`. Under (ii) `w_cal` correctly spans seed-dependent ranges ([0.686745, 60.192080] across seeds), including values below 1 and above e^3 where calibration loading falls outside the test range. The ratio is finite and strictly positive everywhere under both schemes, so nothing blows up — which is why the two schemes give differences that are small relative to the seed std, and why the error is invisible in the aggregate.

2. The 2D drift result is entirely a `histgb` story. All four ridge cells sit at coverage 0.893-0.895 with a mean 30-target gap of +0.004 to +0.007. For `histgb`, `line->trafo` under-covers (0.875987, gap +0.022810) and `trafo->line` over-covers (0.924794, gap -0.022445) while both matched cells land at ~0.898. The two cross cells are separated by 0.049 in coverage against stds of ~0.010-0.012, so this clears the std rule; the two ridge cross cells are separated by 0.002 against stds of 0.014-0.017 and do not.

3. The escalation cost of correcting the tilt is real but one-sigma-marginal. For `histgb`, tilting raises escalation 0.306251 -> 0.320301 unweighted, and weighting it raises it further to 0.332730 under (ii), against an escalation std of 0.025-0.036. By the project's own std rule none of those three escalation numbers is separable from the others.
### S4 OUTCOME

B anchored at **max abs diff 0.0** against `data/tradeoff_curve_v2.json` before reporting.

**2D — AGREE, per cell, to full precision.** B reproduces every stored value: ridge line→line
0.893491, histgb line→trafo 0.875987, histgb trafo→line 0.924794, and the four ridge
shortfalls 0.005931 / 0.003776 / 0.007160 / 0.005035.

**B supplies the standard deviations the artifact omits, and they matter.** Ridge's four
shortfall cells are 0.005931±0.010648, 0.003776±0.011042, 0.007160±0.013458,
0.005035±0.013146 — every std is larger than every gap between the cells. **Ridge's 2D cells
are mutually indistinguishable under the project's std rule.** The histgb line→trafo effect
(0.022810 against a −0.001425 control) is the only 2D contrast with a gap of the same order as
its spread.

**2E — the C-6 question is answered, and the answer is smaller than C-6 implied.**

B computed both weighting schemes. Its reasoning for which is correct, verbatim above: under
scheme (i) both weight arrays span exactly [1, e³ = 20.085537] regardless of the actual
loading spread, which is the tell that `w_cal` is not the density ratio at the calibration
points; under (ii), normalising both by the test split's range, `w_cal` correctly spans
seed-dependent ranges including values below 1 and above e³.

| | scheme (i) — as coded | scheme (ii) — corrected |
|---|---|---|
| ESS_test, seeds 0–4 | 0.822046, 0.801077, 0.790292, 0.789372, 0.810391 | **identical** |
| ridge weighted, gap over 30 targets | +0.003046 ± 0.013059 | +0.003156 ± 0.013997 |
| histgb weighted, gap over 30 targets | −0.001456 ± 0.013725 | −0.002001 ± 0.013807 |
| ratio finite and positive | TRUE | TRUE |

**The ESS is completely unaffected** — B: "identical under (i) and (ii) because w_test uses the
test range in both". **The shortfall moves by 0.00011 (ridge) and 0.00055 (histgb) against
seed stds of ~0.013–0.014 — 20 to 100 times below the noise.**

So C-6's mis-specification is real and B confirms the diagnosis, but C-6's impact figure
(up to ~2 pp on escalation) was a **single-seed, single-target** worst case. Across 5 seeds and
30 targets the aggregate effect is ~0.0005. B's own summary: the ratio is finite and positive
under both schemes, "so nothing blows up — which is why the two schemes give differences that
are small relative to the seed std, and why the error is invisible in the aggregate."

B also confirms the realized tilt: mean `agg_loading` shifts +0.0046 to +0.0054 pu between
untilted and tilted test sets, about 0.4x the `agg_loading` std of 0.011371 — independently
confirming that the tilt is real but weak.

**S4 TALLY:  AGREE 22  |  DISAGREE-resolved 0  |  UNRESOLVED 0  |  SINGLE-PATH 0**

---

## S5 — 2F Q-limit class

### S5 ROUND 1 — Agent A (derived artifact) — VERBATIM

Artifact: `/Users/rajansaha/contingency-screener-research/data/qlimit_class.json` — sha256(16) `3c0149754f0eefdb` (full: `3c0149754f0eefdbd55095cce5fbe71aa1d7f1b1cb0db1a998e72beb8b36f610`), 9491 bytes, mtime 2026-08-19 10:06. Every row below comes from that one file, so the file/sha columns are constant and stated once here rather than repeated 100 times.

## 1–2. Per-seed depth fields and their moments

Path prefix: `$.per_operating_point.<model>.per_seed_depth[*].<field>`; seeds are `[0,1,2,3,4]` in both blocks.

### ridge (target 0.94)

| quantity | value | jsonpath | aggregation |
|---|---|---|---|
| q_hat per seed | 0.0074367979219531755, 0.007442509647866191, 0.006657457124686683, 0.006473333863994513, 0.007389140097740388 | `…ridge.per_seed_depth[0..4].q_hat` | stored per seed |
| q_hat mean | 0.00707984773124819 | derived | mean over 5 seeds |
| q_hat std (ddof=0) | 0.0004244694966807675 | derived | population std, 5 seeds |
| n_missed per seed | 59, 61, 111, 88, 65 | `…ridge.per_seed_depth[*].n_missed` | stored per seed |
| n_missed mean | 76.8 | derived | mean, 5 seeds |
| n_missed std (ddof=0) | 20.00399960007998 | derived | population std |
| n_deep per seed | 6, 12, 23, 8, 9 | `…ridge.per_seed_depth[*].n_deep` | stored per seed |
| n_deep mean | 11.6 | derived | mean, 5 seeds |
| n_deep std (ddof=0) | 6.019966777316965 | derived | population std |
| max_depth per seed | 0.024135209910541633, 0.015862163372903915, 0.012919168044457696, 0.022712215880924647, 0.032425998381073184 | `…ridge.per_seed_depth[*].max_depth` | stored per seed |
| max_depth mean | 0.021610951117980216 | derived | mean, 5 seeds |
| max_depth std (ddof=0) | 0.006828551345167926 | derived | population std |
| median_depth per seed | 0.0023336351505914843, 0.0028378321868701706, 0.003496901201088698, 0.0021644802483588577, 0.002333217059319548 | `…ridge.per_seed_depth[*].median_depth` | stored per seed |
| median_depth mean | 0.0026332131692457517 | derived | mean, 5 seeds |
| median_depth std (ddof=0) | 0.00048729481119280454 | derived | population std |

### histgb (target 0.97)

| quantity | value | jsonpath | aggregation |
|---|---|---|---|
| q_hat per seed | 0.005720216760455421, 0.005728406974601752, 0.005352561828672053, 0.005327379026154766, 0.006594729621320128 | `…histgb.per_seed_depth[*].q_hat` | stored per seed |
| q_hat mean | 0.005744658842240824 | derived | mean, 5 seeds |
| q_hat std (ddof=0) | 0.00045855084363036994 | derived | population std |
| n_missed per seed | 114, 78, 100, 67, 45 | `…histgb.per_seed_depth[*].n_missed` | stored per seed |
| n_missed mean | 80.8 | derived | mean, 5 seeds |
| n_missed std (ddof=0) | 24.2932089275995 | derived | population std |
| n_deep per seed | 32, 26, 17, 18, 13 | `…histgb.per_seed_depth[*].n_deep` | stored per seed |
| n_deep mean | 21.2 | derived | mean, 5 seeds |
| n_deep std (ddof=0) | 6.8527366796047255 | derived | population std |
| max_depth per seed | 0.035869194466890186, 0.045982601089145314, 0.0914569251411822, 0.0914569251411822, 0.06701563873171257 | `…histgb.per_seed_depth[*].max_depth` | stored per seed |
| max_depth mean | 0.0663562569140225 | derived | mean, 5 seeds |
| max_depth std (ddof=0) | 0.022825725415010524 | derived | population std |
| median_depth per seed | 0.0027602523326612505, 0.0025796435964495767, 0.0019163286144640024, 0.003305310902243397, 0.0027139182816193763 | `…histgb.per_seed_depth[*].median_depth` | stored per seed |
| median_depth mean | 0.0026550907454875204 | derived | mean, 5 seeds |
| median_depth std (ddof=0) | 0.00044469487274045394 | derived | population std |

## 3. n_deep_total vs sum of per-seed n_deep

| quantity | value | jsonpath | aggregation |
|---|---|---|---|
| ridge n_deep_total | 58 | `…ridge.n_deep_total` | stored |
| ridge sum(per-seed n_deep) | 58 (6+12+23+8+9) | derived | sum, 5 seeds |
| ridge — equal? | YES | — | — |
| histgb n_deep_total | 106 | `…histgb.n_deep_total` | stored |
| histgb sum(per-seed n_deep) | 106 (32+26+17+18+13) | derived | sum, 5 seeds |
| histgb — equal? | YES | — | — |

## 4. Concentration and max_depth (pooled)

| quantity | ridge | histgb | jsonpath | aggregation |
|---|---|---|---|---|
| n_distinct_elements | 32 | 54 | `…<model>.n_distinct_elements` | pooled over all deep rows, seeds merged |
| top_element_share | 0.08620689655172414 | 0.04716981132075472 | `…top_element_share` | pooled; = top count / n_deep_total |
| n_distinct_argmin_buses | 25 | 31 | `…n_distinct_argmin_buses` | pooled |
| top_bus_share | 0.10344827586206896 | 0.1509433962264151 | `…top_bus_share` | pooled |
| max_depth (op level) | 0.032425998381073184 | 0.0914569251411822 | `…<model>.max_depth` | max over pooled deep rows |

Cross-check: op-level `max_depth` equals the max of the five per-seed `max_depth` values in both blocks.

## 5. offsetpoint_gens (pooled over deep rows)

| quantity | ridge | histgb | jsonpath | aggregation |
|---|---|---|---|---|
| mean | 21.32758620689655 | 21.452830188679247 | `…<model>.offsetpoint_gens.mean` | pooled mean over deep rows (denominator 58 / 106 — verified: mean×n = 1237.0 and 2274.0, exact integers) |
| median | 21.0 | 22.0 | `.median` | pooled |
| min | 17 | 17 | `.min` | pooled |
| max | 27 | 27 | `.max` | pooled |
| share_with_any | 1.0 | 1.0 | `.share_with_any` | pooled |

## 6. min_hops (pooled over deep rows)

| quantity | ridge | histgb | jsonpath | aggregation |
|---|---|---|---|---|
| mean | 1.5517241379310345 | 0.9811320754716981 | `…<model>.min_hops.mean` | pooled; ×n = 90.0 / 104.0 exactly |
| median | 1.0 | 1.0 | `.median` | pooled |
| share_within_2 | 0.8103448275862069 | 0.8962264150943396 | `.share_within_2` | pooled; ×n = 47 / 95 rows exactly |

## 7. baseline_all_n1_rows (every field)

| quantity | value | jsonpath | aggregation |
|---|---|---|---|
| n_rows | 278955 | `$.baseline_all_n1_rows.n_rows` | full N-1 corpus, no seed split |
| offsetpoint_gens_mean | 20.799293792905665 | `.offsetpoint_gens_mean` | mean over 278955 rows (×n = 5802067.0 exactly) |
| offsetpoint_gens_share_with_any | 1.0 | `.offsetpoint_gens_share_with_any` | share over 278955 rows |
| violation_rate | 0.174755784983241 | `.violation_rate` | over 278955 rows (×n = 48749.0 exactly → 48749 violating rows) |

That is the complete set of four fields in this object.

## 8. deep_elements list length, count sum, truncation

| model | list len | sum of listed counts | n_deep_total | unlisted mass | unlisted elements |
|---|---|---|---|---|---|
| ridge | 10 | 31 | 58 | 27 deep misses (46.6%) unaccounted | 32 − 10 = 22 |
| histgb | 10 | 43 | 106 | 63 deep misses (59.4%) unaccounted | 54 − 10 = 44 |

Both lists are truncated to the top 10. Ridge is truncated by 22 element entries carrying 27 of 58 deep misses; histgb by 44 entries carrying 63 of 106. The same truncation applies to `deep_argmin_buses_ieee`: ridge lists 10 of 25 buses summing to 38 of 58; histgb lists 10 of 31 buses summing to 72 of 106.

## 9. Is "no single outaged element accounts for more than 9% of deep misses" recomputable?

**RECOMPUTABLE FROM ARTIFACT**, for the pooled-across-seeds reading, with one stated assumption.

Why: the maximum share is carried by the head of a list that is sorted by descending count, so truncation removes only smaller entries and cannot hide the maximum. Ridge head is `line_51` (tied with `line_147`) at count 5; 5/58 = 0.08620689655172414 < 0.09. Histgb head is count 5; 5/106 = 0.04716981132075472 < 0.09. Both match the stored `top_element_share` to full precision, which is what confirms the sort order — the file never declares it. The last listed counts (ridge 2, histgb 3) also bound every unlisted element at ≤2 and ≤3, i.e. ≤0.0345 and ≤0.0283, so no omitted element can reach 9% either. Both `count` and the `n_deep_total` denominator are stored, so the arithmetic is closed inside the file.

Two qualifiers on that "yes":
- It is recomputable only as a **pooled** statement over all five seeds merged. There is no per-seed element breakdown anywhere in the file, so the same statement at seed level — and any error bar on it — is **not** recomputable. Given ridge pools only 58 deep misses with a top count of 5, the leading share rests on five rows.
- The sorted-descending property is inferred from agreement with `top_element_share`, not asserted by the artifact. If a future run emitted an unsorted list, the recomputation would silently break.

## 10. Conclusion-bearing scalars with NO per-seed counterpart anywhere in the file

Per-seed data exists only inside `per_seed_depth`, whose five fields are `q_hat`, `n_missed`, `n_deep`, `max_depth`, `median_depth`. Everything below is pooled-only:

Per operating point (both ridge and histgb):
- `deep_elements[*].count` and `.share` (the whole list)
- `n_distinct_elements`
- `top_element_share`
- `deep_argmin_buses_ieee[*].count` and `.share` (the whole list)
- `n_distinct_argmin_buses`
- `top_bus_share`
- `offsetpoint_gens.mean`, `.median`, `.min`, `.max`, `.share_with_any`
- `min_hops.mean`, `.median`, `.share_within_2`

Top level:
- `baseline_all_n1_rows.n_rows`, `.offsetpoint_gens_mean`, `.offsetpoint_gens_share_with_any`, `.violation_rate` — all over the undivided 278955-row corpus.

Not on this list: `n_deep_total` (exactly the sum of per-seed `n_deep`) and op-level `max_depth` (exactly the max of per-seed `max_depth`) both reduce from per-seed values. `deepest` is a single labeled row, not an aggregate, and carries `seed`.

The practical consequence: the Stage-2F "identifiable class" claim rests on `min_hops`, `offsetpoint_gens`, and the concentration shares — and every one of those is in the no-per-seed-counterpart list, so none of them can be given an across-seed error bar from this artifact. Under the project std rule, they currently cannot be stated with a spread at all.

## Two things worth flagging

1. **Duplicate max_depth across histgb seeds 2 and 3**: both store `0.0914569251411822`, identical to full float precision. `deepest` attributes it to seed 2, row 74468, scenario_id 101000025. Two seeds independently producing a bit-identical maximum depth points to the same underlying scenario row appearing in both seeds' evaluation sets, which would mean the per-seed max_depth values are not independent draws.
2. **n_missed and n_deep are extremely dispersed across seeds** relative to their means: ridge n_deep spans 6–23 with mean 11.6 and population std 6.02 (std/mean = 0.52); histgb n_deep spans 13–32, std 6.85. The pooled counts (58, 106) that all the Section 4–6 conclusions are computed over are therefore dominated by whichever seed happened to miss most — ridge seed 2 alone contributes 23 of 58 deep misses (39.7%).
### S5 ROUND 1 — Agent B (re-derived, ANCHORED exact) — VERBATIM

**ANCHOR: PASSED — exact (max abs diff = 0.0, all 8 comparisons).** Refit from raw reproduces `data/tradeoff_curve_v2.json` at coverage target 0.90 bit-for-bit for both families (escalation, coverage_emp, missed_viol, and q_hat). Split reproduction independently confirmed: test-split row counts 55789/55792/55787/55791/55791 match `n_test` in `tuned_metrics.json`.

Route: `data/dataset.parquet` → `feasibility/make_splits.py` (load_dataset → build_design_matrix → make_splits → select_features) → refit of the M2 config read from `data/tuned_metrics.json` (ridge = StandardScaler+Ridge; histgb = HistGradientBoostingRegressor, `random_state=seed`) → `feasibility/gate_eval.py` calibrate_qhat/run_gate/score. Driver: `/private/tmp/claude-501/-Users-rajansaha-contingency-screener-research/a20165b8-6ffa-4031-84e5-ca5fd47a15f6/scratchpad/rederive.py`; raw output `/private/tmp/claude-501/-Users-rajansaha-contingency-screener-research/a20165b8-6ffa-4031-84e5-ca5fd47a15f6/scratchpad/rederived.json`.

| quantity | value | source | derivation | aggregation | sha256(16) |
|---|---|---|---|---|---|
| ANCHOR ridge@0.90 escalation | 0.4906972404572077 (stored 0.4906972404572077) | dataset.parquet + make_splits + gate_eval; cmp tradeoff_curve_v2.json | refit M2 ridge per seed, q_hat on cal, gate on test | mean of 5 seeds | 8f0fd1081c8603e8 |
| ANCHOR ridge@0.90 coverage_emp | 0.8933896003705112 (stored identical) | same | same | mean of 5 | 8f0fd1081c8603e8 |
| ANCHOR ridge@0.90 missed_viol | 0.029631523339489742 (stored identical) | same | same | mean of 5 | 8f0fd1081c8603e8 |
| ANCHOR histgb@0.90 escalation | 0.3062513593744674 (stored identical) | same | refit M2 histgb per seed | mean of 5 | 8f0fd1081c8603e8 |
| ANCHOR histgb@0.90 coverage_emp | 0.8981751371681603 (stored identical) | same | same | mean of 5 | 8f0fd1081c8603e8 |
| ANCHOR histgb@0.90 missed_viol | 0.04716684182384393 (stored identical) | same | same | mean of 5 | 8f0fd1081c8603e8 |
| ANCHOR max abs difference | 0.0 (also 0.0 for q_hat, both families) | — | max over 8 comparisons | — | a40a079733ecdfcd |
| **RIDGE @ coverage target 0.94** | | | | | |
| q_hat per seed | 0.0074368, 0.00744251, 0.00665746, 0.00647333, 0.00738914 | cal split | `calibrate_qhat(pred_cal, y_cal, 0.94)` | per seed | 4d6b7fad556c2c64 |
| q_hat | mean 0.00707985, std 0.000424469 | same | — | mean/std ddof=0 over 5 | 493351b8d7d6cff4 |
| escalation | mean 0.643412, std 0.0278282 | test split | matches stored 0.643412 / 0.0278282 exactly | mean/std ddof=0 | a40a079733ecdfcd |
| coverage_emp | mean 0.939516, std 0.00740206 | test split | matches stored exactly | mean/std ddof=0 | a40a079733ecdfcd |
| missed_viol rate | mean 0.00793537, std 0.00208993 | test split | matches stored exactly | mean/std ddof=0 | a40a079733ecdfcd |
| n_missed (certified AND y<0.94) per seed | 59, 61, 111, 88, 65 | test split | `certify & (y<0.94)` | per seed | 4d6b7fad556c2c64 |
| n_missed | mean 76.8, std 20.004 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| n_deep (depth > q_hat) per seed | 6, 12, 23, 8, 9 | test split | `(0.94-y)[missed] > q_hat` | per seed | 4d6b7fad556c2c64 |
| n_deep | mean 11.6, std 6.01997 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| max depth over missed set per seed | 0.0241352, 0.0158622, 0.0129192, 0.0227122, 0.032426 | test split | max(0.94-y) over missed | per seed | 4d6b7fad556c2c64 |
| max depth | mean 0.021611, std 0.00682855 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| median depth over missed set per seed | 0.00233364, 0.00283783, 0.0034969, 0.00216448, 0.00233322 | test split | median(0.94-y) over missed | per seed | 4d6b7fad556c2c64 |
| median depth | mean 0.00263321, std 0.000487295 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| deep: n distinct outaged elements per seed | 5, 12, 17, 7, 8 | `outaged_type`+`outaged_idx` | nunique over that seed's deep set only | per seed | 4d6b7fad556c2c64 |
| deep: n distinct elements | mean 9.8, std 4.26146 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| deep: largest single-element share per seed | 0.333333, 0.0833333, 0.173913, 0.25, 0.222222 | same | max count / n_deep | per seed | 4d6b7fad556c2c64 |
| deep: largest element share | mean 0.21256, std 0.0827942 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| deep: modal element per seed | line_155, line_10, line_147, line_30, line_51 | same | mode (0-based pandapower line idx) | per seed | 4d6b7fad556c2c64 |
| deep: n distinct argmin buses per seed | 5, 11, 13, 7, 7 | `argmin_bus` | nunique over that seed's deep set | per seed | 4d6b7fad556c2c64 |
| deep: n distinct buses | mean 8.6, std 2.93939 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| deep: largest single-bus share per seed | 0.333333, 0.166667, 0.173913, 0.25, 0.222222 | same | max count / n_deep | per seed | 4d6b7fad556c2c64 |
| deep: largest bus share | mean 0.229227, std 0.0604849 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| deep: modal argmin bus per seed (0-based) | 103, 105, 100, 26, 40 | same | mode | per seed | 4d6b7fad556c2c64 |
| deep: off-setpoint gen count, mean per seed | 22.5, 20.75, 21.0, 20.5, 22.8889 | `vm0_{bus(g)}`, `genvm_g`, `genon_g`; bus(g)=`case118().gen.bus` positional | `(|vm0-genvm|>1e-4)&(genon==1)` summed over 53 gens, mean over that seed's deep set | per seed | 4d6b7fad556c2c64 |
| deep: off-setpoint mean | mean 21.5278, std 0.973412 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| deep: share of rows with ≥1 off-setpoint | 1.0 all five seeds; mean 1.0, std 0.0 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| **HISTGB @ coverage target 0.97** | | | | | |
| q_hat per seed | 0.00572022, 0.00572841, 0.00535256, 0.00532738, 0.00659473 | cal split | `calibrate_qhat(...,0.97)` | per seed | 4d6b7fad556c2c64 |
| q_hat | mean 0.00574466, std 0.000458551 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| escalation | mean 0.636795, std 0.0511921 | test split | matches stored 0.636795 / 0.0511921 exactly | mean/std ddof=0 | a40a079733ecdfcd |
| coverage_emp | mean 0.969564, std 0.002463 | test split | matches stored exactly | mean/std ddof=0 | a40a079733ecdfcd |
| missed_viol rate | mean 0.00832214, std 0.00244681 | test split | matches stored exactly | mean/std ddof=0 | a40a079733ecdfcd |
| n_missed per seed | 114, 78, 100, 67, 45 | test split | `certify & (y<0.94)` | per seed | 4d6b7fad556c2c64 |
| n_missed | mean 80.8, std 24.2932 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| n_deep per seed | 32, 26, 17, 18, 13 | test split | depth > q_hat | per seed | 4d6b7fad556c2c64 |
| n_deep | mean 21.2, std 6.85274 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| max depth over missed set per seed | 0.0358692, 0.0459826, 0.0914569, 0.0914569, 0.0670156 | test split | max(0.94-y) over missed | per seed | 4d6b7fad556c2c64 |
| max depth | mean 0.0663563, std 0.0228257 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| median depth over missed set per seed | 0.00276025, 0.00257964, 0.00191633, 0.00330531, 0.00271392 | test split | median(0.94-y) over missed | per seed | 4d6b7fad556c2c64 |
| median depth | mean 0.00265509, std 0.000444695 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| deep: n distinct elements per seed | 24, 22, 17, 17, 11 | element key | per-seed deep set only | per seed | 4d6b7fad556c2c64 |
| deep: n distinct elements | mean 18.2, std 4.53431 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| deep: largest element share per seed | 0.09375, 0.115385, 0.0588235, 0.111111, 0.153846 | same | max count / n_deep | per seed | 4d6b7fad556c2c64 |
| deep: largest element share | mean 0.106583, std 0.0309109 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| deep: modal element per seed | line_162, line_4, line_10, line_10, line_156 | same | mode | per seed | 4d6b7fad556c2c64 |
| deep: n distinct argmin buses per seed | 15, 16, 11, 12, 6 | `argmin_bus` | per-seed deep set | per seed | 4d6b7fad556c2c64 |
| deep: n distinct buses | mean 12.0, std 3.52136 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| deep: largest bus share per seed | 0.28125, 0.115385, 0.176471, 0.333333, 0.538462 | same | max count / n_deep | per seed | 4d6b7fad556c2c64 |
| deep: largest bus share | mean 0.28898, std 0.14633 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| deep: modal argmin bus per seed (0-based) | 103, 62, 103, 53, 106 | same | mode | per seed | 4d6b7fad556c2c64 |
| deep: off-setpoint mean per seed | 20.25, 21.9231, 21.4118, 20.8889, 24.3077 | as above | mean over that seed's deep set | per seed | 4d6b7fad556c2c64 |
| deep: off-setpoint mean | mean 21.7563, std 1.39122 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| deep: share with ≥1 off-setpoint | 1.0 all five seeds; mean 1.0, std 0.0 | same | — | mean/std ddof=0 | 493351b8d7d6cff4 |
| **BASELINES (item 4)** | | | | | |
| all converged N-1 rows, n | 278955 | dataset.parquet, `outaged_type!='none' & converged` | load_dataset filter | full population | 8f0fd1081c8603e8 |
| all rows: off-setpoint mean | 20.7993 (row-level population std 2.40071) | same | same rule over 53 gens | full population | 8f0fd1081c8603e8 |
| all rows: share with ≥1 off-setpoint | 1.0 (minimum count over all rows = 12) | same | — | full population | 8f0fd1081c8603e8 |
| per-seed TEST-split baseline off-setpoint mean | 20.75, 20.8365, 20.9266, 20.73, 20.6901 → mean 20.7867, std 0.0848069 | same, restricted to each seed's test rows | like-for-like baseline at the same aggregation | mean/std ddof=0 | 4d6b7fad556c2c64 |
| per-seed TEST-split baseline share ≥1 | 1.0 all five seeds | same | — | mean/std ddof=0 | 4d6b7fad556c2c64 |
| **SPLIT OVERLAP (item 5)** | | | | | |
| test scenarios per seed | 300 each (of 1500) | make_splits(groups, seed) | GroupShuffleSplit on `scenario_id` | per seed | 00c0168639765bd7 |
| pairwise test-set overlaps (scenario_ids) | 0-1: 55, 0-2: 50, 0-3: 48, 0-4: 68, 1-2: 52, 1-3: 66, 1-4: 65, 2-3: 61, 2-4: 63, 3-4: 49 | same | set intersection of test scenario_ids | 10 pairs | 00c0168639765bd7 |
| union / intersection over 5 test splits | union 1018 scenario_ids; intersection 0 | same | — | — | 00c0168639765bd7 |
| **ITEM 6 VERDICT** | | | | | |
| ridge@0.94 deep-miss off-setpoint mean minus all-rows baseline | 21.5278 − 20.7993 = 0.7285; relevant stds: deep across-seed 0.973412, all-rows row-level 2.40071 → **DOES NOT EXCEED** the larger (nor the smaller) | derived above | std rule (CLAUDE.md §8) | per-seed values only | 493351b8d7d6cff4 |
| histgb@0.97 deep-miss off-setpoint mean minus all-rows baseline | 21.7563 − 20.7993 = 0.957; relevant stds: deep across-seed 1.39122, all-rows row-level 2.40071 → **DOES NOT EXCEED** the larger (nor the smaller) | derived above | std rule | per-seed values only | 493351b8d7d6cff4 |
| share-with-≥1-off-setpoint discriminates? | NO — degenerate. 1.0 on deep misses, 1.0 on all 278955 converged rows (min count 12). Carries zero signal on case118. | derived above | — | — | 8f0fd1081c8603e8 |

Notes on limits of what is derivable:
- **Test splits are NOT disjoint.** Every pair of seeds shares 48–68 of 300 test scenarios (union 1018 < 1500). Pooling the five seeds' deep misses would double-count scenarios; the five per-seed deep-miss sets are therefore **not independent observations**, and only the per-seed-then-aggregate convention used above is defensible. No quantity here was pooled.
- Deep-miss counts are small (ridge@0.94: 6–23 per seed; histgb@0.97: 13–32). Every "distinct elements / largest share" statistic is computed over ≤32 rows, so the shares are dominated by small-sample granularity (e.g. 0.333 = 2 of 6). Do not read the modal element or bus as a stable finding.
- `max depth over the missed set` equals `max depth over the deep set` in all 10 seed-family cells, i.e. the deepest miss is always a deep miss — expected, not an extra finding.
- The M2 hyperparameter *selection* was not re-derived (the inner 26-candidate-per-family search was not re-run); the selected configs were read from `data/tuned_metrics.json` and refit from raw. That step is **NOT INDEPENDENTLY DERIVABLE** within this budget — re-running it costs ~26 fits × 2 families × 5 seeds.
### S5 ROUND 2 — the diff I computed

B anchored at **max abs diff 0.0, all 8 comparisons**, and independently confirmed the split
reproduction (test-split row counts 55789/55792/55787/55791/55791 matching `tuned_metrics.json`).

AGREE: per-seed `n_deep` ridge 6, 12, 23, 8, 9 and histgb 32, 26, 17, 18, 13 on both routes;
means 11.6 / 21.2; population stds 6.019966777316965 / 6.8527366796047255; `n_deep_total`
58 / 106 equal to the per-seed sums on both routes.

DISAGREE — 2 items sent to both agents as values and paths only:
1. deep-miss off-setpoint mean: A 21.32758620689655 / 21.452830188679247 vs B 21.5278 / 21.7563
2. largest single-element share: A pooled 0.08620689655172414 / 0.04716981132075472 vs B per
   seed ridge 0.333333, 0.0833333, 0.173913, 0.25, 0.222222 and histgb 0.09375, 0.115385,
   0.0588235, 0.111111, 0.153846

### S5 ROUND 2 — Agent A response — VERBATIM

Both items check out arithmetically on their own terms. Here is the resolution.

## ITEM 1 — off-setpoint generator mean

**Same quantity, two weightings. My value stands as a description of the stored field.**

The stored field is the **row-weighted pooled mean over all deep-miss rows, seeds merged**, denominator `n_deep_total`. That is not an inference — it is forced by the stored precision:

| model | stored mean | × n_deep_total | result |
|---|---|---|---|
| ridge | 21.32758620689655 | × 58 | 1237.0 exactly |
| histgb | 21.452830188679247 | × 106 | 2274.0 exactly |

`n_offsetpoint_gens` is integer-valued, so a sum of 1237 over exactly 58 rows pins the denominator. An unweighted mean of five per-seed means would land on a rational with denominator 5·lcm(6,12,23,8,9) and would essentially never reduce to an exact 58ths. So the stored field is pooled, and my Round 1 aggregation label was correct.

The other value is the **unweighted mean of the five per-seed means** — a different estimator of the same underlying quantity. It is *not recoverable from the artifact*: there is no per-seed `offsetpoint_gens` block anywhere in the file (this was item 10 in Round 1). The two diverge because seed n_deep is wildly unequal — ridge is 6, 12, 23, 8, 9, so seed 2 alone carries 40% of the pooled weight and almost none of the mean-of-means weight.

Which is right depends on the estimand, and neither is wrong:
- If the question is "what does a typical deep miss look like," the pooled row mean is correct.
- If the question is "what is the seed-to-seed variability of this statistic," you need per-seed means, and only the other path can produce an error bar.

The disagreement is 0.200 gens (ridge) and 0.303 gens (histgb) on a base of ~21. Both aggregations sit within ~0.7 of the full-corpus baseline `offsetpoint_gens_mean` = 20.799293792905665, and `share_with_any` is **1.0 in the deep-miss set and 1.0 in the 278955-row baseline**. The off-setpoint-generator feature separates deep misses from everything else by roughly half a generator out of twenty-one, with zero separation on the binary version. Whichever aggregation you pick, this is a null result for the Stage-2F "pre-outage signature" question, and the choice between 21.33 and 21.53 does not change that. I would report it as null rather than adjudicate the weighting.

## ITEM 2 — largest single-element share

**Different quantities, not one quantity computed two ways.** Pooled top share asks "across all seeds merged, what fraction of deep misses does the single most frequent element carry." Per-seed max share asks "within one seed, what fraction does that seed's most frequent element carry," then reports five of them. Merging destroys the per-seed maxima whenever different seeds have different top elements — which is exactly what happens here.

First, a cross-check that the other agent's numbers are sound: dividing each per-seed share back by my per-seed `n_deep` gives exact integers.

| | seed 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| ridge n_deep | 6 | 12 | 23 | 8 | 9 |
| ridge top **element** count | 2 | 1 | 4 | 2 | 2 |
| ridge top **bus** count | 2 | 2 | 4 | 2 | 2 |
| histgb n_deep | 32 | 26 | 17 | 18 | 13 |
| histgb top **element** count | 3 | 3 | 1 | 2 | 2 |
| histgb top **bus** count | 9 | 3 | 3 | 6 | 7 |

All twenty back out to integers against my independently-sourced `n_deep`. The other agent's per-seed computation is correct.

### Does pooled overstate or understate? UNDERSTATE, by roughly a factor of 2.2–2.5.

| statistic | pooled (stored) | mean of per-seed | per-seed max | ratio | absolute gap |
|---|---|---|---|---|---|
| ridge, element | 0.086207 | 0.212560 | 0.333333 | 2.47× | +0.1264 |
| histgb, element | 0.047170 | 0.106583 | 0.153846 | 2.26× | +0.0594 |
| ridge, bus | 0.103448 | 0.229227 | 0.333333 | 2.22× | +0.1258 |
| histgb, bus | 0.150943 | 0.288980 | 0.538462 | 1.91× | +0.1380 |

Pooling understates per-seed concentration in all four cases, by 5.9 to 13.8 percentage points.

### But the per-seed number is not the honest correction either

The per-seed maxima are mostly the small-sample ceiling, not evidence of a physical hot spot. Ridge seed 0's headline 0.3333 is the count **2 out of 6**. Seed 1's 0.0833 is a count of **1 out of 12** — meaning in that seed no element repeated at all, and the "top element share" is just 1/n. A statistic whose floor is 1/n and whose observed values are counts of 1–4 cannot carry a concentration claim.

I checked both aggregations against a uniform null (deep misses thrown at random over 186 branches / 118 buses, 20k reps, expected max share):

| n | ridge element observed | uniform null |
|---|---|---|
| 6 | 0.3333 | 0.1798 |
| 12 | 0.0833 | 0.1091 |
| 23 | 0.1739 | 0.0784 |
| 8 | 0.2500 | 0.1428 |
| 9 | 0.2222 | 0.1314 |

Per seed the observed values straddle the null — seed 1 is *below* chance. The pooled figures separate more cleanly: element 0.0862 vs null 0.0445 (ridge), 0.0472 vs 0.0325 (histgb); bus 0.1034 vs 0.0519 and 0.1509 vs 0.0386. So pooled is the aggregation with enough sample to detect concentration at all, and it does detect roughly 2× chance — while simultaneously being the aggregation that makes the raw share look smallest.

The one place with concentration visible at both levels is **histgb argmin buses**: per-seed top counts 9/32, 7/13, 6/18 against a null max share of 0.071–0.117, and pooled 0.1509 against null 0.0386. That is a real bus-level hot spot (IEEE bus 104 leads pooled at 16 of 106). Element-level concentration is much weaker.

## Verdicts

- **Item 1 — my value stands.** The stored field is the pooled row mean, verified by exact-integer reconstruction; my aggregation label was right. The other value is a legitimate different weighting that the artifact does not contain. The gap is immaterial to the conclusion, which is null either way.
- **Item 2 — my value stands as a field reading; the claim built on it is underdetermined.** Nothing in the artifact is wrong: `top_element_share` correctly reports the pooled quantity and I labeled it pooled. But the sentence *"no single outaged element accounts for more than 9% of deep misses"* is true only pooled and false at seed level (ridge reaches 33.3%), so as a statement about whether deep misses are concentrated it is aggregation-dependent and should not go into the paper in that form.

The honest fix is not to swap one number for the other. Both are dominated by sample size — ridge pools 58 deep misses over 186 possible elements, so ~2.2 per element even under perfect uniformity, and per-seed it is 6 to 23 over 186. Neither aggregation can support a concentration claim about elements at this n. What I would state instead: report `n_distinct_elements` (32 of 186 for ridge, 54 of 186 for histgb) with the pooled top share and its uniform-null comparison, say explicitly that the sample is too small to resolve element-level structure, and carry the histgb **bus** concentration separately, since that is the one signal that survives both aggregations and the null.

Also worth flagging for whoever writes this up: the disagreement itself is a symptom of the Round 1 finding that these pooled scalars have no per-seed counterpart in `data/qlimit_class.json`. If the generating script (`/Users/rajansaha/contingency-screener-research/scripts/` — I did not read it, only the artifact) emitted per-seed `offsetpoint_gens`, `min_hops`, and element/bus tables, both items would be settled by the file rather than by re-derivation, and these statistics could carry the error bars the project's std rule requires.
### S5 OUTCOME

Round 3 not required.

**Item 1 — same quantity, two weightings; both correct.** A proved the stored field is the
row-weighted pooled mean, not an inference: 21.32758620689655 × 58 = **1237.0 exactly** and
21.452830188679247 × 106 = **2274.0 exactly**, and `n_offsetpoint_gens` is integer-valued, so
the denominator is pinned. B's is the unweighted mean of five per-seed means. They diverge
because per-seed `n_deep` is wildly unequal — ridge seed 2 alone carries 40% of the pooled
weight. **Neither is recoverable from the other**: the artifact has no per-seed
`offsetpoint_gens` block, so only B's route can produce an error bar.

**Item 2 — C-10's DIRECTION WAS WRONG. Pooling UNDERSTATES per-seed concentration.**

A cross-checked B's per-seed shares by dividing each back through its own `n_deep`; all twenty
recover exact integers, confirming B's computation.

| statistic | pooled (stored) | mean of per-seed | per-seed max | ratio | gap |
|---|---|---|---|---|---|
| ridge, element | 0.086207 | 0.212560 | 0.333333 | **2.47x** | +0.1264 |
| histgb, element | 0.047170 | 0.106583 | 0.153846 | 2.26x | +0.0594 |
| ridge, bus | 0.103448 | 0.229227 | 0.333333 | 2.22x | +0.1258 |
| histgb, bus | 0.150943 | 0.288980 | 0.538462 | 1.91x | +0.1380 |

C-10 recorded that pooling overlapping seeds "OVERSTATES concentration". **It understates it,
in all four cases, by 5.9 to 13.8 percentage points.** C-10 is corrected on this point.

**But A then establishes that neither number supports a concentration claim.** The per-seed
maxima are the small-sample ceiling: ridge seed 0's 0.3333 is a count of **2 out of 6**; seed
1's 0.0833 is **1 out of 12**, i.e. in that seed no element repeated at all and the statistic
is simply 1/n. A's conclusion, verbatim above: "A statistic whose floor is 1/n and whose
observed values are counts of 1-4 cannot carry a concentration claim."

**So the 2F claim "no single outaged element accounts for more than 9% of deep misses" is not
supportable as stated.** A ruled it RECOMPUTABLE from the artifact for the pooled reading —
the head of a descending-sorted list bounds the maximum, and the last listed counts bound every
unlisted element at <=2 and <=3 — but with two qualifiers: the sort order is inferred from
agreement with `top_element_share` rather than asserted by the file, and there is no per-seed
breakdown, so the statement has no error bar at all. The `deep_elements` list is truncated to
10 entries covering 31 of 58 ridge deep misses (46.6% unaccounted) and 43 of 106 for histgb.

**B independently confirmed the split-overlap premise:** the five test splits share 48-68
scenarios per pair, union 1018 of 1500, intersection 0. Pooling is not independent sampling.

**B's std-rule verdict on the stage's own question:** ridge deep-miss off-setpoint mean minus
all-rows baseline = 21.5278 - 20.7993 = **0.7285** against stds 0.973412 (across-seed) and
2.40071 (row-level) — **DOES NOT EXCEED**. histgb 0.957 against 1.39122 / 2.40071 —
**DOES NOT EXCEED**. And `share_with_any` is **1.0 in the deep-miss set and 1.0 across all
278,955 converged rows** (minimum count 12), carrying zero signal.

**2F's null result survives both routes and is strengthened.** What does not survive is the
9%-concentration evidence for it.

**S5 TALLY:  AGREE 18  |  DISAGREE-resolved 2  |  UNRESOLVED 0  |  SINGLE-PATH 6**

SINGLE-PATH (A has it, no per-seed counterpart exists anywhere in the artifact, so B cannot
re-derive an error bar for it): `deep_elements` list, `n_distinct_elements`,
`top_element_share`, `deep_argmin_buses_ieee` list, `n_distinct_argmin_buses`, `top_bus_share`
— for both operating points.

---

## S6 — 2H case30-thermal — PARTIAL

### S6 ROUND 1 — Agent A (derived artifact) — VERBATIM

All numbers below are read from the stored JSON at full precision. No file was written or modified.

## sha256 (first 16) of every source file

| file | sha256(16) |
|---|---|
| `/Users/rajansaha/contingency-screener-research/data/case30_thermal/case30_thermal_frozen.json` | `b340af22662fdd29` |
| `/Users/rajansaha/contingency-screener-research/data/case30_thermal/h3_build_stats.json` | `f2d3717c163ff964` |
| `/Users/rajansaha/contingency-screener-research/data/case30_thermal/h2_range_sweep.json` | `dd98d69da1be1937` |

Shorthand below: `FROZEN` = `case30_thermal_frozen.json` (sha `b340af22662fdd29`), `H3` = `h3_build_stats.json` (`f2d3717c163ff964`), `H2` = `h2_range_sweep.json` (`dd98d69da1be1937`). All under `/Users/rajansaha/contingency-screener-research/data/case30_thermal/`. `records[]` has 90 rows = 2 families x 9 coverage targets x 5 seeds; `n_test` = 12300 for every row; `n_true_viol` per seed = `[1881, 1816, 1914, 1895, 1856]` identically across every family and target (the seed indexes the split, not the label set).

## 1. Stored scalars

| quantity | value | file | jsonpath | aggregation |
|---|---|---|---|---|
| violation_rate_pct | 15.3967 | FROZEN | `$.violation_rate_pct` | as stored |
| saturation_point_pct | 84.6033 | FROZEN | `$.saturation_point_pct` | as stored |
| boundary_mass_pct | 7.0862 | FROZEN | `$.boundary_mass_pct` | as stored |
| seeds | 5 | FROZEN | `$.seeds` | as stored |
| limit | 0.94 | FROZEN | `$.limit` | as stored |
| ms_solver | 9.14 | FROZEN | `$.ms_solver` | as stored |
| coverage_levels | [0.9, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98] | FROZEN | `$.coverage_levels` | as stored |
| std_convention | "population std (ddof=0) over the five held-out splits" | FROZEN | `$.std_convention` | as stored |

`violation_rate_pct + saturation_point_pct = 100.0000` exactly — saturation is the arithmetic complement, not an independent measurement. Boundary mass (7.0862) is a distinct quantity from both.

## 2. Per-seed `missed_viol`, all 9 targets, both families

Recomputed from `$.records[?(@.family==F && @.coverage_target==C)].missed_viol`, seeds ordered 0..4; mean and population std (ddof=0).

**ridge**

| target | seed0 | seed1 | seed2 | seed3 | seed4 | mean | std(ddof=0) | #seeds < 0.01 |
|---|---|---|---|---|---|---|---|---|
| 0.90 | 0.05741626794258373 | 0.05671806167400881 | 0.062173458725182866 | 0.05963060686015831 | 0.06842672413793104 | 0.060873023867972956 | 0.004230980760261226 | 0 |
| 0.91 | 0.050505050505050504 | 0.04955947136563876 | 0.056948798328108674 | 0.05118733509234828 | 0.057112068965517244 | 0.053062544851332695 | 0.0032811682204587785 | 0 |
| 0.92 | 0.043593833067517275 | 0.04405286343612335 | 0.04597701149425287 | 0.04907651715039578 | 0.05064655172413793 | 0.04666935537448544 | 0.0027711631562129637 | 0 |
| 0.93 | 0.037745879851143006 | 0.03634361233480176 | 0.03605015673981191 | 0.04221635883905013 | 0.0447198275862069 | 0.03941516707020274 | 0.003450517681503146 | 0 |
| 0.94 | 0.02711323763955343 | 0.028083700440528634 | 0.030303030303030304 | 0.035883905013192614 | 0.03609913793103448 | 0.031496602265467896 | 0.003813611367009346 | 0 |
| 0.95 | 0.019670388091440724 | 0.023127753303964757 | 0.02246603970741902 | 0.025329815303430078 | 0.028017241379310345 | 0.023722247557112986 | 0.002806431638217094 | 0 |
| 0.96 | 0.013290802764486975 | 0.01762114537444934 | 0.017241379310344827 | 0.020052770448548814 | 0.023706896551724137 | 0.01838259888991082 | 0.0034335462715608983 | 0 |
| 0.97 | 0.007442849548112706 | 0.009911894273127754 | 0.009404388714733543 | 0.011609498680738786 | 0.014008620689655173 | 0.010475450381273592 | 0.0022104657593999153 | 3 |
| 0.98 | 0.001594896331738437 | 0.007158590308370044 | 0.005747126436781609 | 0.004221635883905013 | 0.007004310344827586 | 0.005145311861124538 | 0.002065428478269109 | 5 |

**histgb**

| target | seed0 | seed1 | seed2 | seed3 | seed4 | mean | std(ddof=0) | #seeds < 0.01 |
|---|---|---|---|---|---|---|---|---|
| 0.90 | 0.019138755980861243 | 0.026982378854625552 | 0.024033437826541274 | 0.017414248021108178 | 0.023706896551724137 | 0.022255143446972075 | 0.0034860525509527274 | 0 |
| 0.91 | 0.01701222753854333 | 0.0236784140969163 | 0.022988505747126436 | 0.014775725593667546 | 0.020474137931034482 | 0.019785802181457618 | 0.0034257007304609537 | 0 |
| 0.92 | 0.01701222753854333 | 0.022026431718061675 | 0.021421107628004178 | 0.012137203166226913 | 0.018318965517241378 | 0.018183187113615495 | 0.003555226078339563 | 0 |
| 0.93 | 0.01541733120680489 | 0.021475770925110133 | 0.02037617554858934 | 0.00949868073878628 | 0.017780172413793104 | 0.016909626166616752 | 0.0042608344188199854 | 1 |
| 0.94 | 0.01541733120680489 | 0.018722466960352423 | 0.01619644723092999 | 0.008443271767810026 | 0.015086206896551725 | 0.01477314481248981 | 0.0034118385642582035 | 1 |
| 0.95 | 0.013822434875066455 | 0.014317180616740088 | 0.013584117032392894 | 0.0063324538258575196 | 0.011314655172413793 | 0.01187416830449415 | 0.0029567424895495576 | 1 |
| 0.96 | 0.009569377990430622 | 0.010462555066079295 | 0.01044932079414838 | 0.00474934036939314 | 0.010237068965517241 | 0.009093532637113735 | 0.0021962920812743196 | 2 |
| 0.97 | 0.008506113769271665 | 0.007709251101321586 | 0.008881922675026124 | 0.0036939313984168864 | 0.009159482758620689 | 0.00759014034053139 | 0.0020082418201518605 | 5 |
| 0.98 | 0.004784688995215311 | 0.005506607929515419 | 0.00522466039707419 | 0.0015831134564643799 | 0.007004310344827586 | 0.004820676224619377 | 0.0017824180903893846 | 5 |

Every recomputed mean/std reproduces the corresponding stored value exactly where one exists (0.90 row vs `four_metrics_at_90pct_coverage`, crossing rows vs `crossings_first_below_1pct_missed`). No mismatch found anywhere in the file.

## 3. THE CRUX — the crossing and its two neighbors

Stored (`$.crossings_first_below_1pct_missed`):

| family | coverage_target | missed_viol | escalation | net_speedup |
|---|---|---|---|---|
| ridge | 0.98 | 0.005145311861124538 | 0.37834146341463415 | 2.648920064539311 |
| histgb | 0.96 | 0.009093532637113735 | 0.048617886178861786 | 21.45706393938002 |

Per-seed at the crossing and one step either side (aggregation: mean / population std over the 5 seeds; "#< 0.01" counts seeds individually below the 1% threshold):

**histgb** (step below = 0.95, crossing = 0.96, step above = 0.97)

| target | per-seed missed_viol (seeds 0-4) | mean | std | #< 0.01 |
|---|---|---|---|---|
| 0.95 | 0.013822434875066455, 0.014317180616740088, 0.013584117032392894, 0.0063324538258575196, 0.011314655172413793 | 0.01187416830449415 | 0.0029567424895495576 | 1 (seed 3) |
| **0.96** | 0.009569377990430622, 0.010462555066079295, 0.01044932079414838, 0.00474934036939314, 0.010237068965517241 | 0.009093532637113735 | 0.0021962920812743196 | **2 (seeds 0, 3)** |
| 0.97 | 0.008506113769271665, 0.007709251101321586, 0.008881922675026124, 0.0036939313984168864, 0.009159482758620689 | 0.00759014034053139 | 0.0020082418201518605 | 5 |

Raw counts at 0.96: `n_missed` = [18, 19, 20, 9, 19] out of `n_true_viol` = [1881, 1816, 1914, 1895, 1856]. The sub-1% mean is carried by seed 3 alone (9 misses against a ~19-miss cohort); three of the five seeds sit *above* 0.01 at the declared crossing.

**ridge** (step below = 0.97, crossing = 0.98; 0.98 is the top of the grid, so there is no step above)

| target | per-seed missed_viol (seeds 0-4) | mean | std | #< 0.01 |
|---|---|---|---|---|
| 0.97 | 0.007442849548112706, 0.009911894273127754, 0.009404388714733543, 0.011609498680738786, 0.014008620689655173 | 0.010475450381273592 | 0.0022104657593999153 | 3 (seeds 0, 1, 2) |
| **0.98** | 0.001594896331738437, 0.007158590308370044, 0.005747126436781609, 0.004221635883905013, 0.007004310344827586 | 0.005145311861124538 | 0.002065428478269109 | **5** |
| (0.99) | not in `coverage_levels` — grid ends at 0.98 | — | — | — |

## 4. Decidability of the crossing target

Test as specified: is `|mean − 0.01|` greater than the family's own population std at that target?

| family | crossing | mean | std | \|mean − 0.01\| | gap/std | verdict |
|---|---|---|---|---|---|---|
| histgb | 0.96 | 0.009093532637113735 | 0.0021962920812743196 | 0.000906467362886265 | 0.413 | **INDETERMINATE** |
| ridge | 0.98 | 0.005145311861124538 | 0.002065428478269109 | 0.004854688138875462 | 2.351 | **DECIDABLE at 0.98** — but see below |

**histgb: INDETERMINATE.** The mean sits 0.41 sigma below the 1% threshold. Under the project's own std rule (never call a difference smaller than the reported std real), 0.96 is not distinguishable from the threshold, and 3 of 5 seeds individually fail it. Nor is 0.96 separable from 0.95 above it: the 0.95 mean (0.011874) differs from the 0.96 mean by 0.002781, smaller than either std (0.002957, 0.002196). The first target that is genuinely separated from 0.01 for histgb is 0.97 (mean 0.007590, gap 0.002410 ≈ 1.20 sigma, 5/5 seeds below).

**ridge: the endpoint is decidable, the crossing identity is not.** 0.98 clears the threshold by 2.35 sigma with 5/5 seeds below, so "ridge is below 1% at 0.98" holds. But calling 0.98 the *first* such target requires 0.97 to be genuinely above 0.01, and it is not: mean 0.010475, gap to threshold 0.000475 = 0.215 sigma, with 3 of 5 seeds already below 0.01. The exclusion of 0.97 is noise-level. **The crossing target for ridge is INDETERMINATE between 0.97 and 0.98**, even though the sub-1% claim at 0.98 stands.

Net: `crossings_first_below_1pct_missed` records a threshold-crossing on a 0.01-wide grid using a statistic whose seed-to-seed scatter (std ~0.002-0.0035) is comparable to the change induced by one grid step (~0.0028 for histgb 0.95→0.96, ~0.0053 for ridge 0.97→0.98). Neither family's crossing index survives its own error bar.

## 5. Counterfactual — histgb crossing at 0.97 instead of 0.96

| target | metric | per-seed (0-4) | mean | std(ddof=0) |
|---|---|---|---|---|
| 0.96 | escalation | 0.034308943089430895, 0.0632520325203252, 0.05471544715447155, 0.0448780487804878, 0.0459349593495935 | 0.048617886178861786 | 0.009770044231923439 |
| 0.97 | escalation | 0.042195121951219515, 0.07894308943089431, 0.06463414634146342, 0.05333333333333334, 0.05268292682926829 | 0.05835772357723577 | 0.012504625358797069 |
| 0.96 | net_speedup | 29.146826483773797, 15.809741290885302, 18.276337897367327, 22.28255437251871, 21.769859652354963 | 21.45706393938002 | 4.514886374051058 |
| 0.97 | net_speedup | 23.699360514426765, 12.667335688102796, 15.471671923597338, 18.749961535910415, 18.98144206179975 | 17.91395434476741 | 3.709477412003147 |

Moving the crossing one step up costs 0.97 percentage points of escalation (0.0486 → 0.0584) and 3.54x of net speedup (21.46 → 17.91). Both shifts are smaller than the larger of the two stds in each pair (escalation delta 0.00974 vs std 0.01250; speedup delta 3.543 vs std 4.515), so the headline penalty for the safer operating point is itself inside the noise. Supporting counts at 0.97: `n_escalated` = [519, 971, 795, 656, 648], `n_missed` = [16, 14, 17, 7, 17]; at 0.96: `n_escalated` = [422, 778, 673, 552, 565], `n_missed` = [18, 19, 20, 9, 19]. Empirical coverage: 0.96 → 0.9636422764227642 ± 0.004500100982261615; 0.97 → 0.974260162601626 ± 0.0033857079089630164 (both over-cover their nominal target).

## 6. `four_metrics_at_90pct_coverage`, all fields

`$.four_metrics_at_90pct_coverage.<family>.*`, FROZEN. Aggregation: mean / population std over 5 seeds (already stored as such).

| field | ridge | histgb |
|---|---|---|
| escalation_mean | 0.1191869918699187 | 0.02653658536585366 |
| escalation_std | 0.009868056775128144 | 0.004071409644763381 |
| coverage_emp_mean | 0.9034146341463416 | 0.9021951219512196 |
| coverage_emp_std | 0.0041940504083067135 | 0.009797608166533104 |
| missed_viol_mean | 0.060873023867972956 | 0.022255143446972075 |
| missed_viol_std | 0.004230980760261226 | 0.0034860525509527274 |
| net_speedup_mean | 8.449258452147355 | 38.62634570430097 |
| net_speedup_std | 0.7145854052631637 | 6.2064483518404305 |
| n_test_per_seed | [12300, 12300, 12300, 12300, 12300] | [12300, 12300, 12300, 12300, 12300] |
| n_true_viol_per_seed | [1881, 1816, 1914, 1895, 1856] | [1881, 1816, 1914, 1895, 1856] |

Empirical coverage brackets the 0.90 nominal for both families within one std. `n_true_viol_per_seed` is identical across families, as expected — it is a property of the split, not the model.

## 7. `h3_build_stats.json`

| quantity | value | jsonpath |
|---|---|---|
| acceptance_rate | 0.18633540372670807 | `$.acceptance_rate` |
| n_accepted | 1500 | `$.n_accepted` |
| n_draws | 8050 | `$.n_draws` |
| rejected_by.nonconvergence | 0 | `$.rejected_by.nonconvergence` |
| rejected_by.voltage | 840 | `$.rejected_by.voltage` |
| rejected_by.thermal | 5710 | `$.rejected_by.thermal` |
| n1_loading.n | 61500 | `$.n1_loading.n` |
| n1_loading.share_above_100 | 0.21484552845528454 | `$.n1_loading.share_above_100` |
| n1_loading.median | 97.65510698522175 | `$.n1_loading.median` |
| n1_loading.p90 | 106.68668745699547 | `$.n1_loading.p90` |
| n1_loading.max | 145.79724799181238 | `$.n1_loading.max` |
| max_base_loading_pct | 99.99929123481061 | `$.max_base_loading_pct` |
| equivalence_all_match | true | `$.equivalence_all_match` |

Consistency notes: 840 + 5710 + 1500 = 8050 = `n_draws`, and 1500/8050 = 0.186335403726708 — the acceptance rate reconciles exactly. `max_base_loading_pct` = 99.99929 sits 0.0007 pp under the 100% acceptance ceiling, i.e. the thermal predicate binds essentially exactly. Thermal rejection dominates voltage rejection 6.8:1. `equivalence_checks` is 5 entries, each `match: true`, `n_rows: 42`, `diffs: []` — supporting `equivalence_all_match`. Also present: `median_base_loading_pct` 96.93849162006879, `elapsed_s` 1269.8, `range` {lo 0.87, hi 0.99}, `dataset_rows` 63000.

## 8. `h2_range_sweep.json` — chosen range and zero-acceptance lo values

Chosen (`$.h2.chosen`), selection rule `$.h2.selection_rule` = "highest lo whose acceptance rate >= 0.20 AND whose max base loading_percent <= 100":

| field | value |
|---|---|
| lo / hi | 0.87 / 0.99 |
| acceptance_rate | 0.205 |
| n_accepted / n_draws | 41 / 200 |
| rejected_by | nonconvergence 0, voltage 24, thermal 135 |
| max_base_loading_pct | 99.78849507593934 |
| median_base_loading_pct | 96.98108472272476 |
| min_base_vm_pu | 0.9454142466074986 |
| n1_probe | n_bases 6, n_contingencies 246, violation_rate 0.14227642276422764, boundary_mass 0.044715447154471545, min_vm_min 0.8739311515227777, min_vm_median 0.9573575614453106 |
| verdict | "FEASIBLE RANGE FOUND" |

Sweep params: window_width 0.12, step 0.01, n_draws_per_candidate 200, seed 100; 31 candidates from lo=1.00 down to lo=0.70.

**Every lo with `acceptance_rate` exactly 0.0** (`$.h2.sweep[?(@.acceptance_rate==0.0)].lo`), 7 of 31 candidates:

`1.0, 0.99, 0.98, 0.97, 0.96, 0.95, 0.94`

All seven have `nonconvergence: 0` and `max_base_loading_pct: null` (no accepted draw to measure), with thermal rejections 158-174 of 200 and voltage rejections 26-42.

Two observations on the selection. The chosen candidate clears its own 0.20 threshold by 0.005 — a single accepted draw out of 200 (41 vs the 40 needed). At n=200 the binomial standard error on p=0.205 is 0.0285, so the rule's cut sits ~0.18 SE above the threshold: which lo "wins" is not resolved by this sweep. The next candidate down, lo=0.86, gives 0.23 and also satisfies both constraints. Separately, the h2 chosen acceptance rate (0.205, n=200, seed 100) and the h3 realized acceptance rate on the same 0.87/0.99 range (0.186335, n=8050) differ by 0.0187, about 0.66 SE of the h2 estimate — consistent, with h3 the far better-resolved number.
### S6 STATUS — INCOMPLETE AT TIME OF WRITING

Agent B is still executing. Its route requires re-running the full M2 inner-split selection
twice — once on `data/case30_dataset.parquet` for the anchor and once on
`data/case30_thermal/dataset.parquet` — which is roughly a 75-minute job on this hardware. At
the time this block was written B had produced no value table; two `.venv/bin/python` processes
were confirmed live at 30+ minutes elapsed and ~210 MB resident each.

**No S6 diff has been computed and no S6 verdict is recorded.** Agent A's table above stands
alone and is explicitly NOT adjudicated. Recording it as a completed comparison would be
false.

**S6 TALLY: NOT YET COMPUTED**

---

## S7 — writing-numbers.md, all 80 rows — NOT STARTED

---

## CORRECTION C-14 — S6 agent B did NOT die; my earlier status note was wrong

The S6 block above records agent B as having produced no value table with its compute gone.
That reading was wrong. B had completed both model runs and was in its analysis phase; it
subsequently returned a full anchored table. The "S6 INCOMPLETE" note above is superseded by
the S6 outcome below. Recorded rather than edited, per the append-only rule.

## S6 — 2H case30-thermal — COMPLETE

### S6 ROUND 1 — Agent B (re-derived, ANCHORED bit-exact) — VERBATIM

**ANCHOR: PASSED (bit-exact).** Independent re-implementation of the protocol run against `data/case30_dataset.parquet` reproduces `data/case30_frozen.json` `four_metrics_at_90pct_coverage` with **max absolute difference = 0.0** across all 16 mean/std entries (both families × esc/cov/missed/speedup) and exact agreement on `n_missed_per_seed`, `n_true_viol_per_seed`, `violation_rate_pct`, `boundary_mass_pct`. All thermal numbers below are ANCHORED.

Re-derivation script: `/private/tmp/claude-501/-Users-rajansaha-contingency-screener-research/a20165b8-6ffa-4031-84e5-ca5fd47a15f6/scratchpad/rederive.py`; outputs `anchor_case30.json`, `thermal.json` in the same directory. `data/case30_thermal/case30_thermal_frozen.json` was never opened.

| quantity | value | source | derivation | aggregation | sha256(16) |
|---|---|---|---|---|---|
| ANCHOR max abs diff, 16 metric entries | 0.0 | data/case30_frozen.json vs re-run | rederive.py on case30_dataset.parquet, protocol of case30_gate.py | max abs over means+stds | d501f99671b40a78 / 4d73f8cdfe8131d2 |
| ANCHOR n_missed ridge (5 seeds) | 34,29,59,71,75 — identical | same | same | per-seed | d501f99671b40a78 |
| ANCHOR n_missed histgb (5 seeds) | 64,51,47,54,47 — identical | same | same | per-seed | d501f99671b40a78 |
| thermal rows / scenarios (converged N-1) | 61500 / 1500 (63000 raw; 1500 non-N-1 rows dropped, 0 non-converged) | data/case30_thermal/dataset.parquet | make_splits.load_dataset filter | count | cb1a38e9a39ef233 |
| violation rate (min_vm < 0.94) | 0.15396747967479674 (9469/61500) | dataset.parquet | boolean mean over converged N-1 | population share | cb1a38e9a39ef233 |
| boundary mass [0.94, 0.945) | 0.07086178861788618 (4358/61500) | dataset.parquet | boolean mean over converged N-1 | population share | cb1a38e9a39ef233 |
| ms_solver used | 9.14 | data/solve_time.json | mf.load_solve_time() (case118 basis, as in the script) | min over timed solves | 94d8e8059d2b3526 |
| test set per seed | n_test 12300; n_true_viol 1881,1816,1914,1895,1856 | rederive.py | outer GroupShuffleSplit | per-seed | cb1a38e9a39ef233 |
| M2 tags ridge (seeds 0-4) | alpha0.01, alpha3.162, alpha0.1, alpha0.001, alpha0.003162 | rederive.py | inner-split M2 selection | per-seed | 9395044201a93337 |
| M2 tags histgb (seeds 0-4) | rand15, rand14, rand11, rand00, rand00 | rederive.py | inner-split M2 selection | per-seed | 9395044201a93337 |
| **ridge missed_viol** 0.90 | 0.05741627, 0.05671806, 0.06217346, 0.05963061, 0.06842672 → mean 0.06087302, std 0.00423098 | rederive.py | gate_eval.score | mean, std ddof=0 | cb1a38e9a39ef233 |
| ridge missed_viol 0.91 | 0.05050505, 0.04955947, 0.05694880, 0.05118734, 0.05711207 → mean 0.05306254, std 0.00328117 | " | " | " | " |
| ridge missed_viol 0.92 | 0.04359383, 0.04405286, 0.04597701, 0.04907652, 0.05064655 → mean 0.04666936, std 0.00277116 | " | " | " | " |
| ridge missed_viol 0.93 | 0.03774588, 0.03634361, 0.03605016, 0.04221636, 0.04471983 → mean 0.03941517, std 0.00345052 | " | " | " | " |
| ridge missed_viol 0.94 | 0.02711324, 0.02808370, 0.03030303, 0.03588391, 0.03609914 → mean 0.03149660, std 0.00381361 | " | " | " | " |
| ridge missed_viol 0.95 | 0.01967039, 0.02312775, 0.02246604, 0.02532982, 0.02801724 → mean 0.02372225, std 0.00280643 | " | " | " | " |
| ridge missed_viol 0.96 | 0.01329080, 0.01762115, 0.01724138, 0.02005277, 0.02370690 → mean 0.01838260, std 0.00343355 | " | " | " | " |
| ridge missed_viol 0.97 | 0.00744285, 0.00991189, 0.00940439, 0.01160950, 0.01400862 → mean 0.01047545, std 0.00221047 (3/5 seeds < 0.01) | " | " | " | " |
| ridge missed_viol 0.98 | 0.00159490, 0.00715859, 0.00574713, 0.00422164, 0.00700431 → mean 0.00514531, std 0.00206543 (5/5 seeds < 0.01) | " | " | " | " |
| **histgb missed_viol** 0.90 | 0.01913876, 0.02698238, 0.02403344, 0.01741425, 0.02370690 → mean 0.02225514, std 0.00348605 | " | " | " | " |
| histgb missed_viol 0.91 | 0.01701223, 0.02367841, 0.02298851, 0.01477573, 0.02047414 → mean 0.01978580, std 0.00342570 | " | " | " | " |
| histgb missed_viol 0.92 | 0.01701223, 0.02202643, 0.02142111, 0.01213720, 0.01831897 → mean 0.01818319, std 0.00355523 | " | " | " | " |
| histgb missed_viol 0.93 | 0.01541733, 0.02147577, 0.02037618, 0.00949868, 0.01778017 → mean 0.01690963, std 0.00426083 (1/5 < 0.01) | " | " | " | " |
| histgb missed_viol 0.94 | 0.01541733, 0.01872247, 0.01619645, 0.00844327, 0.01508621 → mean 0.01477314, std 0.00341184 (1/5) | " | " | " | " |
| histgb missed_viol 0.95 | 0.01382243, 0.01431718, 0.01358412, 0.00633245, 0.01131466 → mean 0.01187417, std 0.00295674 (1/5) | " | " | " | " |
| histgb missed_viol 0.96 | 0.00956938, 0.01046256, 0.01044932, 0.00474934, 0.01023707 → mean 0.00909353, std 0.00219629 (2/5 < 0.01) | " | " | " | " |
| histgb missed_viol 0.97 | 0.00850611, 0.00770925, 0.00888192, 0.00369393, 0.00915948 → mean 0.00759014, std 0.00200824 (5/5 < 0.01) | " | " | " | " |
| histgb missed_viol 0.98 | 0.00478469, 0.00550661, 0.00522466, 0.00158311, 0.00700431 → mean 0.00482068, std 0.00178242 (5/5) | " | " | " | " |
| **CRUX — ridge first mean < 0.01** | coverage 0.98 (0.97 mean = 0.01047545, still above) | rederive.py | first grid point with mean missed_viol < 0.01 | mean over 5 seeds | cb1a38e9a39ef233 |
| ridge @ crossing 0.98 | per-seed above; mean 0.00514531, std 0.00206543, 5/5 seeds below 0.01 | " | " | " | " |
| ridge one step above 0.98 | DOES NOT EXIST — 0.98 is the last grid point (grid 0.90..0.98) | scripts/case30_thermal_gate.py COVERAGE_LEVELS | — | — | eb58994d58618ae9 |
| ridge decidability | **DECIDABLE**: gap 0.01 − 0.00514531 = 0.00485469 = 2.35 std (std 0.00206543) | " | gap/std | — | cb1a38e9a39ef233 |
| ridge @ 0.97 (the step below crossing) | mean 0.01047545 exceeds 0.01 by only 0.00047545 = 0.22 std → the *exclusion* of 0.97 is itself INDETERMINATE | " | gap/std | — | " |
| **CRUX — histgb first mean < 0.01** | coverage 0.96 (0.95 mean = 0.01187417) | " | " | " | " |
| histgb @ crossing 0.96 | per-seed above; mean 0.00909353, std 0.00219629, 2/5 seeds below 0.01 | " | " | " | " |
| histgb @ 0.97 (one step above) | per-seed above; mean 0.00759014, std 0.00200824, 5/5 seeds below 0.01 | " | " | " | " |
| histgb decidability @ 0.96 | **INDETERMINATE**: gap 0.01 − 0.00909353 = 0.00090647 = 0.41 std (std 0.00219629) | " | gap/std | — | " |
| histgb decidability @ 0.97 | **DECIDABLE**: gap 0.00240986 = 1.20 std (std 0.00200824) | " | gap/std | — | " |
| histgb escalation @ 0.96 | 0.03430894, 0.06325203, 0.05471545, 0.04487805, 0.04593496 → mean 0.04861789, std 0.00977004 (n_esc 422,778,673,552,565 of 12300) | " | gate_eval.score | mean, std ddof=0 | " |
| histgb net_speedup @ 0.96 | 29.14682648, 15.80974129, 18.27633790, 22.28255437, 21.76985965 → mean 21.45706394, std 4.51488637 | " | " | " | " |
| histgb escalation @ 0.97 | 0.04219512, 0.07894309, 0.06463415, 0.05333333, 0.05268293 → mean 0.05835772, std 0.01250463 (n_esc 519,971,795,656,648) | " | " | " | " |
| histgb net_speedup @ 0.97 | 23.69936051, 12.66733569, 15.47167192, 18.74996154, 18.98144206 → mean 17.91395434, std 3.70947741 | " | " | " | " |
| n1_loading converged rows | 61500 (0 non-converged) | data/case30_thermal/n1_loading.parquet | count | — | 5dd818561c7533aa |
| n1_loading share max_loading_pct > 100 | 0.21484552845528454 (13213/61500) | " | boolean mean | population share | " |
| n1_loading median max_loading_pct | 97.65510698522175 | " | np.median | — | " |
| n1_loading p90 max_loading_pct | 106.68668745699547 | " | np.percentile(90), linear interp | — | " |
| n1_loading max max_loading_pct | 145.79724799181238 | " | max | — | " |

Notes on the crux, since two things sit right on the line:
- histgb's stated crossing at 0.96 is not separated from the 0.01 threshold (0.41 std), and only 2 of 5 seeds are individually below 0.01 there. The first target that is both mean-below and separated by more than one std, with all 5 seeds below, is 0.97.
- ridge's crossing at 0.98 is well separated, but its exclusion of 0.97 rests on a 0.22-std excess — i.e. the *location* of the ridge crossing (0.97 vs 0.98) is not resolvable at 5 seeds even though the value at 0.98 is.
- Nothing in the task was undeliverable; the only structural gap is that ridge has no grid point above its crossing (item 3's "one step above" is undefined for ridge).
### S6 OUTCOME

**B's anchor is bit-exact.** An independent re-implementation of the protocol, run against
`data/case30_dataset.parquet`, reproduces `data/case30_frozen.json`'s
`four_metrics_at_90pct_coverage` with **max absolute difference 0.0 across all 16 mean/std
entries**, plus exact agreement on `n_missed_per_seed` (ridge 34,29,59,71,75; histgb
64,51,47,54,47), `n_true_viol_per_seed`, `violation_rate_pct` and `boundary_mass_pct`.
`case30_thermal_frozen.json` was never opened.

**AGREE on the dataset-level quantities, to full precision:**

| quantity | A (artifact) | B (re-derived) |
|---|---|---|
| violation rate | 15.3967% | **0.15396747967479674** (9469/61500) |
| boundary mass | 7.0862% | **0.07086178861788618** (4358/61500) |
| rows / scenarios | 63000 / 61500 N-1 / 1500 | 63000 raw, 61500 converged N-1, 1500 scenarios, 0 non-converged |
| test set | — | n_test 12300; n_true_viol 1881, 1816, 1914, 1895, 1856 |

B also independently reproduced the per-seed M2 selections: ridge `alpha0.01, alpha3.162,
alpha0.1, alpha0.001, alpha0.003162`; histgb `rand15, rand14, rand11, rand00, rand00`.

**THE CRUX — the histgb crossing at 0.96 is NOT DECIDABLE.**

| target | per-seed missed_viol | mean | std | seeds individually < 0.01 |
|---|---|---|---|---|
| **0.96** | 0.00956938, 0.01046256, 0.01044932, 0.00474934, 0.01023707 | **0.00909353** | 0.00219629 | **2 of 5** |
| **0.97** | 0.00850611, 0.00770925, 0.00888192, 0.00369393, 0.00915948 | **0.00759014** | 0.00200824 | **5 of 5** |

- **histgb @ 0.96: INDETERMINATE.** The mean is separated from the 0.01 threshold by
  0.00090647 = **0.41 std**, and only 2 of 5 seeds fall below 0.01 individually.
- **histgb @ 0.97: DECIDABLE.** Gap 0.00240986 = **1.20 std**, all 5 seeds below.

**What the headline becomes under each reading:**

| | escalation | net speedup |
|---|---|---|
| crossing at **0.96** (as published) | **4.86% ± 0.98** (n_esc 422, 778, 673, 552, 565 of 12300) | **21.46x ± 4.51** |
| crossing at **0.97** (the decidable one) | **5.84% ± 1.25** (n_esc 519, 971, 795, 656, 648) | **17.91x ± 3.71** |

**And a finding neither C-11 nor I anticipated: ridge's crossing location is also not
resolvable.** B: ridge @ 0.98 is DECIDABLE as a value (gap 2.35 std, 5/5 seeds below), but the
*exclusion* of 0.97 rests on a mean of 0.01047545 exceeding 0.01 by **0.22 std**. So the ridge
crossing could equally be 0.97. B notes ridge has no grid point above 0.98, so "one step above"
is undefined there.

**Both crossings in `data/case30_thermal/case30_thermal_frozen.json` are therefore
INDETERMINATE as to location at 5 seeds** — histgb between 0.96 and 0.97, ridge between 0.97
and 0.98. The stored scalars are correct as computed; what is not supported is treating either
crossing target as resolved.

**S6 TALLY:  AGREE 12  |  DISAGREE-resolved 0  |  UNRESOLVED 0  |  SINGLE-PATH 0  |  INDETERMINATE 2 (both crossing locations)**

---

## S7 — notes/writing-numbers.md, all 80 rows

### S7 ROUND 1 — Agent A (stated jsonpath) — VERBATIM

All 80 rows read from their stated sources.

```
ROW 1  | case118 total rows                      | stated: 280500     | found: 280500                | value: MATCH | sha: MATCH
ROW 2  | case118 base scenarios                  | stated: 1500       | found: 1500                  | value: MATCH | sha: MATCH
ROW 3  | case118 N-1 attempted                   | stated: 279000     | found: 279000                | value: MATCH | sha: MATCH
ROW 4  | case118 N-1 converged                   | stated: 278955     | found: 278955                | value: MATCH | sha: MATCH
ROW 5  | case118 non-converged                   | stated: 45         | found: 45                    | value: MATCH | sha: MATCH
ROW 6  | case118 violation rate                  | stated: 0.174756   | found: 0.174755784983241     | value: MATCH | sha: MATCH
ROW 7  | case118 boundary mass                   | stated: 0.568629   | found: 0.5686293488197021    | value: MATCH | sha: MATCH
ROW 8  | case118 N-1 share max_vm>1.05           | stated: 0.731358   | found: 0.7313581043537488    | value: MATCH | sha: MATCH
ROW 9  | case118 N-0 share max_vm>1.05           | stated: 0.734      | found: 0.734                 | value: MATCH | sha: MATCH
ROW 10 | case118 gen-outage share of N-1         | stated: 0.249259   | found: 0.24925884103170762   | value: MATCH | sha: MATCH
ROW 11 | sweep total evaluations                 | stated: 16800      | found: 16800                 | value: MATCH | sha: MATCH
ROW 12 | flag precision ridge@0.94 count-pooled  | stated: 0.56062    | found: 0.5606201196271288    | value: MATCH | sha: MATCH
ROW 13 | flag precision ridge@0.94 seed-mean     | stated: 0.561265   | found: 0.561264511296313     | value: MATCH | sha: MATCH
ROW 14 | flag ceiling ridge                      | stated: 0.691482   | found: 0.691481920315199     | value: MATCH | sha: MATCH
ROW 15 | flag precision histgb@0.97 count-pooled | stated: 0.856295   | found: 0.8562945368171021    | value: MATCH | sha: MATCH
ROW 16 | flag precision histgb@0.97 seed-mean    | stated: 0.856372   | found: 0.856371929696882     | value: MATCH | sha: MATCH
ROW 17 | flag ceiling histgb                     | stated: 1.009272   | found: 1.009271992332375     | value: MATCH | sha: MATCH
ROW 18 | case30-published violation rate         | stated: 0.288081   | found at violation_rate_pct: 28.8081 | value: MATCH (raw stored 28.8081; /100 exact) | sha: MATCH
ROW 19 | case30-published boundary mass          | stated: 0.20014600000000002 | found at boundary_mass_pct: 20.0146 | value: MATCH (raw 20.0146; /100 exact, stated value is the float repr of 20.0146/100) | sha: MATCH
ROW 20 | case30-thermal violation rate           | stated: 0.153967   | found at violation_rate_pct: 15.3967 | value: MATCH (raw 15.3967; /100 exact) | sha: MATCH
ROW 21 | case30-thermal boundary mass            | stated: 0.070862   | found at boundary_mass_pct: 7.0862 | value: MATCH (raw 7.0862; /100 exact) | sha: MATCH
ROW 22 | case30-published ridge crossing target  | stated: 0.92       | found: 0.92                  | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 23 | case30-published ridge crossing escal.  | stated: 0.344829   | found: 0.3448292682926829    | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 24 | case30-published ridge crossing speedup | stated: 2.985      | found: 2.9849746109526554    | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 25 | case30-published ridge esc@0.90         | stated: 0.278748   | found: 0.2787479674796748    | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 26 | case30-published ridge speedup@0.90     | stated: 3.6562     | found: 3.656172918726378     | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 27 | case30-published ridge missed@0.90      | stated: 0.014931   | found: 0.014931446336352586  | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 28 | case30-thermal ridge crossing target    | stated: 0.98       | found: 0.98                  | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 29 | case30-thermal ridge crossing escal.    | stated: 0.378341   | found: 0.37834146341463415   | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 30 | case30-thermal ridge crossing speedup   | stated: 2.6489     | found: 2.648920064539311     | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 31 | case30-thermal ridge esc@0.90           | stated: 0.119187   | found: 0.1191869918699187    | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 32 | case30-thermal ridge speedup@0.90       | stated: 8.4493     | found: 8.449258452147355     | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 33 | case30-thermal ridge missed@0.90        | stated: 0.060873   | found: 0.060873023867972956  | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 34 | case30-published histgb crossing target | stated: 0.93       | found: 0.93                  | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 35 | case30-published histgb crossing escal. | stated: 0.089593   | found: 0.08959349593495934   | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 36 | case30-published histgb crossing speedup| stated: 11.2653    | found: 11.265301491886408    | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 37 | case30-published histgb esc@0.90        | stated: 0.069821   | found: 0.06982113821138211   | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 38 | case30-published histgb speedup@0.90    | stated: 14.5218    | found: 14.521830759934906    | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 39 | case30-published histgb missed@0.90     | stated: 0.014664   | found: 0.014664013437545673  | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 40 | case30-thermal histgb crossing target   | stated: 0.96       | found: 0.96                  | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 41 | case30-thermal histgb crossing escal.   | stated: 0.048618   | found: 0.048617886178861786  | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 42 | case30-thermal histgb crossing speedup  | stated: 21.4571    | found: 21.45706393938002     | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 43 | case30-thermal histgb esc@0.90          | stated: 0.026537   | found: 0.02653658536585366   | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 44 | case30-thermal histgb speedup@0.90      | stated: 38.6263    | found: 38.62634570430097     | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 45 | case30-thermal histgb missed@0.90       | stated: 0.022255   | found: 0.022255143446972075  | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 46 | H2 lo values with ZERO acceptance       | stated: 0.94..1.0 (7 values) | found: [1.0, 0.99, 0.98, 0.97, 0.96, 0.95, 0.94] = 7 values | value: MATCH | sha: MATCH
ROW 47 | H2 chosen range                         | stated: [0.87, 0.99] | found: lo=0.87, hi=0.99    | value: MATCH | sha: MATCH
ROW 48 | H2 chosen acceptance                    | stated: 0.205      | found: 0.205                 | value: MATCH | sha: MATCH
ROW 49 | H3 build acceptance                     | stated: 0.186335   | found: 0.18633540372670807   | value: MATCH | sha: MATCH
ROW 50 | case30-thermal N-1 loading >100%        | stated: 0.214846   | found: 0.21484552845528454   | value: MATCH | sha: MATCH
ROW 51 | case30-published N-1 loading >100%      | stated: 1.0        | found: 1.0 (line_loading.share_above_100, 120/1500 prefix sample) | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 52 | 2C shortfall histgb benign->benign      | stated: 0.00891    | found: 0.008910              | value: MATCH | sha: MATCH
ROW 53 | 2C shortfall histgb benign->marginal    | stated: 0.017613   | found: 0.017613              | value: MATCH | sha: MATCH
ROW 54 | 2C shortfall histgb marginal->benign    | stated: -0.011827  | found: -0.011827             | value: MATCH | sha: MATCH
ROW 55 | 2C shortfall histgb marginal->marginal  | stated: -0.00776   | found: -0.007760             | value: MATCH | sha: MATCH
ROW 56 | 2C shortfall ridge benign->benign       | stated: 0.008282   | found: 0.008282              | value: MATCH | sha: MATCH
ROW 57 | 2C shortfall ridge benign->marginal     | stated: 0.164335   | found: 0.164335              | value: MATCH | sha: MATCH
ROW 58 | 2C shortfall ridge marginal->benign     | stated: -0.068568  | found: -0.068568             | value: MATCH | sha: MATCH
ROW 59 | 2C shortfall ridge marginal->marginal   | stated: 0.010189   | found: 0.010189              | value: MATCH | sha: MATCH
ROW 60 | 2D shortfall histgb line->line          | stated: -0.001425  | found: -0.001425             | value: MATCH | sha: MATCH
ROW 61 | 2D shortfall histgb line->trafo         | stated: 0.02281    | found: 0.022810              | value: MATCH | sha: MATCH
ROW 62 | 2D shortfall histgb trafo->line         | stated: -0.022445  | found: -0.022445             | value: MATCH | sha: MATCH
ROW 63 | 2D shortfall histgb trafo->trafo        | stated: 0.001512   | found: 0.001512              | value: MATCH | sha: MATCH
ROW 64 | 2D shortfall ridge line->line           | stated: 0.005931   | found: 0.005931              | value: MATCH | sha: MATCH
ROW 65 | 2D shortfall ridge line->trafo          | stated: 0.003776   | found: 0.003776              | value: MATCH | sha: MATCH
ROW 66 | 2D shortfall ridge trafo->line          | stated: 0.00716    | found: 0.007160              | value: MATCH | sha: MATCH
ROW 67 | 2D shortfall ridge trafo->trafo         | stated: 0.005035   | found: 0.005035              | value: MATCH | sha: MATCH
ROW 68 | 2E shortfall histgb tilted/unweighted   | stated: 0.000624   | found: 0.000624              | value: MATCH | sha: MATCH
ROW 69 | 2E shortfall histgb tilted/weighted     | stated: -0.002061  | found: -0.002061             | value: MATCH | sha: MATCH
ROW 70 | 2E shortfall histgb untilted/unweighted | stated: -0.00121   | found: -0.001210             | value: MATCH | sha: MATCH
ROW 71 | 2E shortfall ridge tilted/unweighted    | stated: 0.004624   | found: 0.004624              | value: MATCH | sha: MATCH
ROW 72 | 2E shortfall ridge tilted/weighted      | stated: 0.003816   | found: 0.003816              | value: MATCH | sha: MATCH
ROW 73 | 2E shortfall ridge untilted/unweighted  | stated: 0.005857   | found: 0.005857              | value: MATCH | sha: MATCH
ROW 74 | 2F baseline off-setpoint gens mean      | stated: 20.7993    | found: 20.799293792905665    | value: MATCH | sha: MATCH
ROW 75 | 2F ridge deep misses                    | stated: 58         | found: 58                    | value: MATCH | sha: MATCH
ROW 76 | 2F ridge distinct elements              | stated: 32         | found: 32                    | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 77 | 2F ridge max miss depth                 | stated: 0.032426   | found: 0.032425998381073184  | value: MATCH | sha: MATCH
ROW 78 | 2F histgb deep misses                   | stated: 106        | found: 106                   | value: MATCH | sha: MATCH
ROW 79 | 2F histgb distinct elements             | stated: 54         | found: 54                    | value: MATCH | sha: MATCH | agg STORED-SCALAR
ROW 80 | 2F histgb max miss depth                | stated: 0.091457   | found: 0.0914569251411822    | value: MATCH | sha: MATCH
```

Counts: value MATCH 80 / MISMATCH 0 / NOT FOUND 0. sha MATCH 80 / MISMATCH 0.

Resolutions applied, as the table's own notes direct:
- `crossings.*` resolved to `crossings_first_below_1pct_missed.*` (rows 22-24, 28-30, 34-36, 40-42).
- `four_metrics.*` resolved to `four_metrics_at_90pct_coverage.*` (rows 25-27, 31-33, 37-39, 43-45).
- `baseline.offsetpoint_gens_mean` resolved to `baseline_all_n1_rows.offsetpoint_gens_mean` (row 74).
- Rows 18-21 state fractions under `_pct` jsonpaths; raw stored values are 28.8081, 20.0146, 15.3967, 7.0862 and the /100 conversion is exact in each case (row 19's `0.20014600000000002` is the exact IEEE-754 result of 20.0146/100).
- Rows 22-45 are labelled seed-mean but the artifacts store scalars at those paths — marked STORED-SCALAR. Rows 76 and 79 likewise (`deep_elements` is truncated to 10 entries, so `n_distinct_elements` was read as stored, not re-derived). Row 51's aggregation column names a 120/1500 prefix sample; the file records the same, and `share_above_100` is a stored scalar.
- Rows 6-10 were computed over converged N-1 rows (base rows excluded, `converged` true), which is the restriction the stated values correspond to; the condition column does not spell it out.

File paths: `/Users/rajansaha/contingency-screener-research/notes/writing-numbers.md`, and sources under `/Users/rajansaha/contingency-screener-research/data/`.
### S7 ROUND 1 — Agent B (re-derived from raw) — VERBATIM

All 80 rows re-derived. Full results:

**ROW 1** | case118 total rows | stated: 280500 | mine: 280500 | route: `len(pd.read_parquet('data/dataset.parquet'))` | verdict: AGREE
**ROW 2** | case118 base scenarios | stated: 1500 | mine: 1500 | route: `(outaged_type=='none').sum()` | verdict: AGREE
**ROW 3** | case118 N-1 attempted | stated: 279000 | mine: 279000 | route: `(outaged_type!='none').sum()` | verdict: AGREE
**ROW 4** | case118 N-1 converged | stated: 278955 | mine: 278955 | route: `(outaged_type!='none') & converged` | verdict: AGREE
**ROW 5** | case118 non-converged | stated: 45 | mine: 45 | route: `(~converged).sum()`; all 45 are N-1 rows, so the bare `~converged` path and the N-1-restricted path agree here | verdict: AGREE
**ROW 6** | case118 violation rate | stated: 0.174756 | mine: 0.1747557849832 | route: `(min_vm<0.94).mean()` over converged N-1 | verdict: AGREE
**ROW 7** | case118 boundary mass | stated: 0.568629 | mine: 0.5686293488197 | route: `((min_vm>=0.94)&(min_vm<0.945)).mean()` over converged N-1. Note this is a share of *all* converged N-1 rows; the share of *non-violating* rows is 0.689044, a different quantity | verdict: AGREE
**ROW 8** | case118 N-1 share max_vm>1.05 | stated: 0.731358 | mine: 0.7313581044 | route: `(max_vm>1.05).mean()` over converged N-1. Over all 279,000 attempted N-1 it is 0.7312401 — the `converged` restriction is implicit in the table's condition column | verdict: AGREE
**ROW 9** | case118 N-0 share max_vm>1.05 | stated: 0.734 | mine: 0.734 | route: `(max_vm>1.05).mean()` over the 1500 `outaged_type=='none'` rows | verdict: AGREE
**ROW 10** | case118 gen-outage share of N-1 | stated: 0.249259 | mine: 0.2492588410 | route: `(gen_out>=0).mean()` over converged N-1; over all attempted N-1 it is 0.2493333 | verdict: AGREE
**ROW 11** | sweep total evaluations | stated: 16800 | mine: 16800 | route: `len(pd.read_parquet('data/sweep_results_long.parquet'))` = 56 L values × 2 models × 30 targets × 5 seeds | verdict: AGREE
**ROW 12** | flag precision ridge@0.94 count-pooled | stated: 0.56062 | mine: 0.5606201196 | route: `sum(flag_viol)/sum(flag_viol+flag_safe)` over the 5 (ridge, target=0.94) rows | verdict: AGREE
**ROW 13** | flag precision ridge@0.94 seed-mean | stated: 0.561265 | mine: 0.5612645113 | route: `mean(flag_precision)` over the same 5 rows. **Both given**: count-pooled 0.560620, seed-mean 0.561265 | verdict: AGREE
**ROW 14** | flag ceiling ridge | stated: 0.691482 | mine: 0.6914819203 | route: deduped to one row per seed (flag columns verified `nunique==1` across all 30 targets per seed), then `sum(n_viol)/sum(flag_viol+flag_safe)`. **Both**: count-pooled 0.691482, seed-mean 0.692415 | verdict: AGREE
**ROW 15** | flag precision histgb@0.97 count-pooled | stated: 0.856295 | mine: 0.8562945368 | route: as row 12 | verdict: AGREE
**ROW 16** | flag precision histgb@0.97 seed-mean | stated: 0.856372 | mine: 0.8563719297 | route: as row 13. **Both**: count-pooled 0.856295, seed-mean 0.856372 | verdict: AGREE
**ROW 17** | flag ceiling histgb | stated: 1.009272 | mine: 1.0092719923 | route: as row 14. **Both**: count-pooled 1.009272, seed-mean 1.009765 | verdict: AGREE
**ROW 18** | case30-published violation rate | stated: 0.288081 | mine: 28.8081% | route: re-derived from `data/case30_dataset.parquet`, **restricted to `outaged_type!='none' & converged`** (the filter `make_splits.load_dataset` applies). Over the raw file including the 1500 base rows it is 28.1222% — the table's condition column omits this restriction | verdict: AGREE
**ROW 19** | case30-published boundary mass | stated: 0.200146 | mine: 20.0146% | route: same filter; unfiltered gives 20.0603% | verdict: AGREE
**ROW 20** | case30-thermal violation rate | stated: 0.153967 | mine: 15.3967% | route: same, on `data/case30_thermal/dataset.parquet`; unfiltered 15.0302% | verdict: AGREE
**ROW 21** | case30-thermal boundary mass | stated: 0.070862 | mine: 7.0862% | route: same; unfiltered 6.9841% | verdict: AGREE

For rows 22–45 I did **not** stop at "not independently derivable". I first bounded the cost of the M2 inner-split search and found it tractable (~10 min per dataset), so I re-ran the full protocol from raw parquet in scratch — dataset load, group splits, inner-split M2 search over the 15 ridge / 26 histgb candidate sets, refit, conformal calibration, gate, seed-mean aggregation — writing nothing to `data/`. All 10 selected M2 tags per dataset match those recorded in `data/case30_prediction.json`.

**ROW 22** | c30-pub ridge crossing target | stated: 0.92 | mine: 0.92 | route: full re-run; first coverage in 0.90..0.98 with seed-mean missed < 0.01 | verdict: AGREE
**ROW 23** | c30-pub ridge crossing escalation | stated: 0.344829 | mine: 0.344829 | route: full re-run | verdict: AGREE
**ROW 24** | c30-pub ridge crossing speedup | stated: 2.985 | mine: 2.9850 | route: full re-run | verdict: AGREE
**ROW 25** | c30-pub ridge esc@0.90 | stated: 0.278748 | mine: 0.278748 | route: full re-run, seed-mean over 5 splits | verdict: AGREE
**ROW 26** | c30-pub ridge speedup@0.90 | stated: 3.6562 | mine: 3.6562 | route: full re-run | verdict: AGREE
**ROW 27** | c30-pub ridge missed@0.90 | stated: 0.014931 | mine: 0.014931 | route: full re-run | verdict: AGREE
**ROW 28** | c30-thermal ridge crossing target | stated: 0.98 | mine: 0.98 | route: full re-run on the thermal dataset | verdict: AGREE
**ROW 29** | c30-thermal ridge crossing escalation | stated: 0.378341 | mine: 0.378341 | route: full re-run | verdict: AGREE
**ROW 30** | c30-thermal ridge crossing speedup | stated: 2.6489 | mine: 2.6489 | route: full re-run | verdict: AGREE
**ROW 31** | c30-thermal ridge esc@0.90 | stated: 0.119187 | mine: 0.119187 | route: full re-run | verdict: AGREE
**ROW 32** | c30-thermal ridge speedup@0.90 | stated: 8.4493 | mine: 8.4493 | route: full re-run | verdict: AGREE
**ROW 33** | c30-thermal ridge missed@0.90 | stated: 0.060873 | mine: 0.060873 | route: full re-run | verdict: AGREE
**ROW 34** | c30-pub histgb crossing target | stated: 0.93 | mine: 0.93 | route: full re-run | verdict: AGREE
**ROW 35** | c30-pub histgb crossing escalation | stated: 0.089593 | mine: 0.089593 | route: full re-run | verdict: AGREE
**ROW 36** | c30-pub histgb crossing speedup | stated: 11.2653 | mine: 11.2653 | route: full re-run | verdict: AGREE
**ROW 37** | c30-pub histgb esc@0.90 | stated: 0.069821 | mine: 0.069821 | route: full re-run | verdict: AGREE
**ROW 38** | c30-pub histgb speedup@0.90 | stated: 14.5218 | mine: 14.5218 | route: full re-run | verdict: AGREE
**ROW 39** | c30-pub histgb missed@0.90 | stated: 0.014664 | mine: 0.014664 | route: full re-run | verdict: AGREE
**ROW 40** | c30-thermal histgb crossing target | stated: 0.96 | mine: 0.96 | route: full re-run. Confirms the caveat: seed-mean missed at 0.96 is 0.009094, and the five per-seed values are 0.00957 / 0.01046 / 0.01045 / 0.00475 / 0.01024 — three of five are *above* 0.01, so the crossing sits at 0.96 only on the seed-mean and is not robust | verdict: AGREE
**ROW 41** | c30-thermal histgb crossing escalation | stated: 0.048618 | mine: 0.048618 | route: full re-run | verdict: AGREE
**ROW 42** | c30-thermal histgb crossing speedup | stated: 21.4571 | mine: 21.4571 | route: full re-run | verdict: AGREE
**ROW 43** | c30-thermal histgb esc@0.90 | stated: 0.026537 | mine: 0.026537 | route: full re-run | verdict: AGREE
**ROW 44** | c30-thermal histgb speedup@0.90 | stated: 38.6263 | mine: 38.6263 | route: full re-run | verdict: AGREE
**ROW 45** | c30-thermal histgb missed@0.90 | stated: 22255e-6 (0.022255) | mine: 0.022255 | route: full re-run | verdict: AGREE

**ROW 46** | H2 lo values with zero acceptance | stated: 0.94..1.0 (7 values) | mine: [1.0, 0.99, 0.98, 0.97, 0.96, 0.95, 0.94], 7 | route: filtered the stored 31-point sweep for `acceptance_rate==0`. The 200-draw AC sampling behind each point was not re-executed (stochastic build, no stored seed state per point) | verdict: AGREE
**ROW 47** | H2 chosen range | stated: [0.87, 0.99] | mine: [0.87, 0.99] | route: applied the stated selection rule ("highest lo with acceptance ≥ 0.20 and max base loading ≤ 100") to the stored sweep: lo=0.88 gives 0.165, lo=0.87 gives 0.205 → 0.87 is the highest qualifying | verdict: AGREE
**ROW 48** | H2 chosen acceptance | stated: 0.205 | mine: 0.205 | route: 41 accepted / 200 draws at the chosen point | verdict: AGREE
**ROW 49** | H3 build acceptance | stated: 0.186335 | mine: 0.1863354037 | route: 1500 / 8050; `1500 + 840 voltage + 5710 thermal + 0 nonconv = 8050` reconciles exactly | verdict: AGREE
**ROW 50** | case30-thermal N-1 loading >100% | stated: 0.214846 | mine: 0.2148455285 | route: `(max_loading_pct > 100).mean()` over all 61,500 rows of `data/case30_thermal/n1_loading.parquet` | verdict: AGREE

**ROW 51** | case30-published N-1 loading >100% | stated: 1.0 | my re-derivation: **0.999797** (4919/4920) | route: full replay from raw. Mapping used: `pload_i`/`qload_i` are **per-bus** aggregates (`generate_dataset.py:158-166` sums `p_new` into `pbus[load_bus]`), so the correct assignment is `net.load['p_mw'] = pbus[net.load.bus.to_numpy()]`, not positional. **Mapping validated before any loading number was read**: the bus-mapped replay reproduces the stored `min_vm` to max abs error 6.8e-8 across all 4920 contingencies, while the as-coded positional path gives N-0 min_vm 0.8813 vs stored 0.9544 (and assigns 154.48 MW against the correct 203.95 MW). Same 120-scenario prefix, bus-mapped: share>100 = 0.999797, median 122.66, p90 135.70, max 195.61, min 99.61. As-coded on the same prefix: share>100 = 1.000000, median 154.7238, p90 192.4818, max 490.4466 — reproducing the stored `thermal_check.json` values exactly and confirming those three are artifacts of the bug. An independent random 120-scenario sample, bus-mapped, gives exactly 1.000000. | verdict: **DISAGREE** (at the stated precision)

**ROWS 52-59** | 2C shortfalls (histgb b→b 0.00891, b→m 0.017613, m→b −0.011827, m→m −0.00776; ridge b→b 0.008282, b→m 0.164335, m→b −0.068568, m→m 0.010189) | mine: 0.008910 / 0.017613 / −0.011827 / −0.007760 / 0.008282 / 0.164335 / −0.068568 / 0.010189 | route: `mean(coverage_target − coverage_emp)` grouped by (model, cal_stratum, test_stratum) on `drift_n0_stratum_long.parquet`; **mean is over seeds AND all 30 coverage targets** (150 rows per cell = 5 seeds × 30 targets). At target 0.90 alone the same cells give 0.006879 / 0.004011 / −0.002217 / −0.003417 / 0.003607 / **0.104702** / −0.031173 / 0.015565 — the headline ridge benign→marginal figure drops from 0.164 to 0.105, so the aggregation choice materially changes it | verdict: AGREE (all 8)
**ROWS 60-67** | 2D shortfalls | mine: histgb l→l −0.001425, l→t 0.022810, t→l −0.022445, t→t 0.001512; ridge l→l 0.005931, l→t 0.003776, t→l 0.007160, t→t 0.005035 | route: same statistic on `drift_element_type_long.parquet`; mean over seeds and all 30 targets | verdict: AGREE (all 8)
**ROWS 68-73** | 2E shortfalls | mine: histgb tilted/unw 0.000624, tilted/wtd −0.002061, untilted/unw −0.001210; ridge 0.004624, 0.003816, 0.005857 | route: same statistic on `drift_loading_tilt_long.parquet` grouped by (model, cell); mean over 5 seeds and all 30 targets | verdict: AGREE (all 6)

For rows 74–80 I refit the models. `qlimit_class.py` reads the M2 configs from `data/tuned_metrics.json` rather than searching, so a refit from raw is deterministic and cost ~7 s/seed ridge, ~20 s/seed histgb.

**ROW 74** | 2F baseline off-setpoint gens mean | stated: 20.7993 | mine: 20.799293792905665 | route: from `dataset.parquet` restricted to converged N-1 (278,955 rows), `(|vm0_[bus(g)] − genvm_g| > 1e-4) & (genon_g > 0.5)` summed per row and averaged, with `bus(g)` from `pn.case30`→ actually `pn.case118().gen.bus` | verdict: AGREE
**ROW 75** | 2F ridge deep misses | stated: 58 | mine: 58 | route: full refit, 5 seeds, target 0.94; deep = `certify & (y<0.94) & (0.94−y > q_hat)`. Per-seed n_deep 6/12/23/8/9 | verdict: AGREE
**ROW 76** | 2F ridge distinct elements | stated: 32 | mine: 32 | route: `value_counts` over `outaged_type_outaged_idx` of the 58 deep rows. Contrary to the verifier note, this **is** re-derivable — just not from the truncated top-10 list in the JSON | verdict: AGREE
**ROW 77** | 2F ridge max miss depth | stated: 0.032426 | mine: 0.032425998 (seed 4) | route: full refit; per-seed max depths 0.024135/0.015862/0.012919/0.022712/0.032426 | verdict: AGREE
**ROW 78** | 2F histgb deep misses | stated: 106 | mine: 106 | route: full refit, target 0.97; per-seed n_deep 32/26/17/18/13 | verdict: AGREE
**ROW 79** | 2F histgb distinct elements | stated: 54 | mine: 54 | route: as row 76; also re-derivable | verdict: AGREE
**ROW 80** | 2F histgb max miss depth | stated: 0.091457 | mine: 0.091456925 | route: full refit; attained on both seed 2 and seed 3 | verdict: AGREE

## Counts

**AGREE: 79 | DISAGREE: 1 | NOT INDEPENDENTLY DERIVABLE: 0**

## What matters beyond the counts

1. **Row 51 is the only disagreement, and it is small but real.** The corrected bus-mapped replay of the same 120-scenario prefix gives 4919/4920 = 0.999797, not 1.000000 — one contingency lands at 99.61% loading. `writing-numbers.md`'s claim that "a paired as-coded vs bus-mapped replay gives 1.0000 both ways" is wrong at four decimals (0.999797 rounds to 0.9998). The substantive statement — essentially every sampled N-1 on case30-published exceeds 100% — survives, and a random 120-scenario sample does give exactly 1.0. But the manuscript should not write "100%" without the qualifier. The file's caveat about the median/p90/max being wrong is confirmed exactly: the as-coded replay reproduces 154.7238 / 192.4818 / 490.4466, the corrected values are 122.66 / 135.70 / 195.61.

2. **Nothing was blocked.** The brief anticipated that the case30 M2 inner-split selection would be a wall. It is not: the whole search reproduces in about 10 minutes per dataset, and all 20 selected M2 tags match `case30_prediction.json`. Rows 22–45 are therefore fully re-derived from raw parquet, not merely read back. The same holds for rows 75–80, where `qlimit_class.py` reads stored configs rather than searching. Verifier finding 5 ("rows 76 and 79 cannot be recomputed from their artifact alone") is true of the JSON but should not be read as a limit on derivability — both re-derive exactly from the dataset.

3. **Two condition-column defects, same class as verifier finding 4.** Rows 18–21 read as unconditional shares but carry an implicit `outaged_type != 'none' & converged` restriction inherited from `make_splits.load_dataset`. Dropping it moves case30-published violation rate from 28.8081% to 28.1222% and case30-thermal from 15.3967% to 15.0302%. Anyone recomputing from the parquet by the literal condition will get the wrong number.

4. **Row 7's label invites a specific misreading.** `boundary mass 0.568629` is the share of *all* converged N-1 rows in [0.94, 0.945). The share of *non-violating* rows in that strip is 0.689044. Given CLAUDE.md §5's warning that the escalation ceiling and the boundary mass are distinct quantities, the denominator deserves to be stated.

5. **Aggregation sensitivity where it was asked about.** Flag precision: count-pooled and seed-mean differ in the fourth decimal only (0.560620 vs 0.561265; 0.856295 vs 0.856372) — safe either way, but they are different estimators. Flag ceiling: 0.691482 vs 0.692415 count-pooled vs seed-mean. 2C/2D/2E: the means are over seeds *and* all 30 coverage targets, and this is not cosmetic — ridge benign→marginal is 0.164335 pooled but 0.104702 at the 0.90 target alone.

6. **Row 40's caveat is understated, not overstated.** Three of the five per-seed missed rates at coverage 0.96 exceed 0.01 (0.00957, 0.01046, 0.01045, 0.00475, 0.01024). The 0.96 crossing is an artifact of averaging before thresholding.

Scratch scripts (not in the repo tree): `/private/tmp/claude-501/-Users-rajansaha-contingency-screener-research/a20165b8-6ffa-4031-84e5-ca5fd47a15f6/scratchpad/r51.py` (row 51 replay), `r2f.py` (rows 75-80), `r30.py` (rows 22-45), with logs `r51.log`, `r2f.log`, `r30_pub.log`, `r30_th.log`.
### S7 OUTCOME

**A: value MATCH 80 / 80, sha MATCH 80 / 80.** Every row reads back exactly from its stated
jsonpath, with the abbreviations resolved and the `_pct`-to-fraction conversions exact.

**B: AGREE 79 | DISAGREE 1 | NOT INDEPENDENTLY DERIVABLE 0.** B declined the easy exit — it
bounded the M2 inner-split search at ~10 min per dataset, judged it tractable, and re-ran the
full protocol from raw for rows 22-45 rather than marking them underivable. All 10 selected M2
tags per dataset match `data/case30_prediction.json`.

**The single DISAGREE — ROW 51, and it corrects a claim I wrote.**

| route | share above 100% |
|---|---|
| stated in `writing-numbers.md` (from the artifact) | 1.000000 |
| B, bus-mapped, SAME 120-scenario prefix | **0.999797** (4919/4920) |
| B, bus-mapped, a DIFFERENT random 120 sample | exactly 1.000000 |
| S1 agent B, bus-mapped, FULL 61,500 | 0.9989105691 |

All four are mutually consistent: the full population has 67 contingencies at or below 100%, so
one prefix catches one of them and another catches none.

B validated its mapping before reading any loading number — bus-mapped replay reproduces stored
`min_vm` to **6.8e-08** across all 4,920 contingencies, while the positional path gives N-0
`min_vm` 0.8813 against a stored 0.9544. And it reproduced the as-coded values exactly
(154.7238 / 192.4818 / 490.4466), confirming those three are artifacts of the defect, against
corrected 122.66 / 135.70 / 195.61.

**So my CAVEAT in `writing-numbers.md` — "a paired as-coded vs bus-mapped replay gives 1.0000
both ways" — is wrong at four decimals.** The substantive statement survives; the exact 1.0
does not, on the prefix.

**Four further findings B raised that no round-2 exchange was needed for:**

1. **The `converged` filter is load-bearing and unstated.** Recomputing the literal condition
   without it moves case30-published violation rate 28.8081% -> **28.1222%** and case30-thermal
   15.3967% -> **15.0302%**.
2. **Row 7's boundary mass denominator needs stating.** 0.568629 is the share of ALL converged
   N-1 rows in [0.94, 0.945); the share of NON-VIOLATING rows in that strip is **0.689044**.
   CLAUDE.md section 5 already warns these are distinct quantities.
3. **Aggregation sensitivity, quantified.** Flag ceiling count-pooled 0.691482 vs seed-mean
   **0.692415**. And the 2C shortfall is 0.164335 pooled over 30 targets but **0.104702 at the
   0.90 target alone** — not cosmetic.
4. **Row 40's caveat is UNDERSTATED, not overstated.** Three of the five per-seed missed rates
   at coverage 0.96 exceed 0.01 (0.00957, 0.01046, 0.01045, 0.00475, 0.01024). B: "the 0.96
   crossing is an artifact of averaging before thresholding." This independently corroborates
   S6 from a different route.

**S7 TALLY:  AGREE 79  |  DISAGREE-resolved 1  |  UNRESOLVED 0  |  SINGLE-PATH 0  |  STALE 5**

STALE (rows whose stated values were corrected in S1-S6 and which carry caveats):
row 51 (share above 100%), rows 40-42 (histgb crossing location), row 74 + rows 75-80 (2F
pooled statistics).

---

# PAIRED ADJUDICATION — CLOSING TABLE

| scenario | AGREE | DISAGREE-resolved | UNRESOLVED | SINGLE-PATH | STALE |
|---|---|---|---|---|---|
| S1 2A thermal + over-voltage | 40 | 5 | 0 | 0 | 5 |
| S2 2B outage + multiplier | 20 | 2 | 0 | 0 | 1 |
| S3 2C n0-stratum drift | 28 | 1 | 0 | 0 | 0 |
| S4 2D element type + 2E tilt | 22 | 0 | 0 | 0 | 0 |
| S5 2F Q-limit class | 18 | 2 | 0 | 6 | 1 |
| S6 2H case30-thermal | 12 | 0 | 0 | 0 | 2 |
| S7 writing-numbers, 80 rows | 79 | 1 | 0 | 0 | 5 |
| **TOTAL** | **219** | **11** | **0** | **6** | **14** |

**Round 3 was never invoked. Every disagreement closed in round 2.**

## Every SINGLE-PATH or UNRESOLVED quantity — these cannot go in the paper as they stand

**UNRESOLVED: none.**

**SINGLE-PATH — 6 quantities, all in `data/qlimit_class.json`.** Each is a pooled scalar with
no per-seed counterpart anywhere in the file, so no independent route can produce an error bar
for it:

1. `per_operating_point.<model>.deep_elements` — the list itself, truncated to 10 entries
   covering 31 of 58 (ridge) and 43 of 106 (histgb) deep misses
2. `n_distinct_elements` — 32 / 54
3. `top_element_share` — 0.086207 / 0.047170
4. `deep_argmin_buses_ieee` — the list, likewise truncated
5. `n_distinct_argmin_buses` — 25 / 31
6. `top_bus_share` — 0.103448 / 0.150943

S5 established these understate per-seed concentration by 1.91-2.47x, AND that the per-seed
alternative is the small-sample ceiling (counts of 1-4 on n as low as 6). **Neither aggregation
supports a concentration claim.**

**INDETERMINATE — 2 quantities, both in `data/case30_thermal/case30_thermal_frozen.json`:**
the histgb crossing location (0.96 vs 0.97) and the ridge crossing location (0.97 vs 0.98).
Both stored scalars are correctly computed; neither location is resolved at 5 seeds.

---

# CODE FINDING — the column-mapping defect, reported once, outside the pairs

**`scripts/thermal_check.py:159-160`**

```python
net.load["p_mw"] = row[load_p].to_numpy(dtype=float)[:len(net.load)]
net.load["q_mvar"] = row[load_q].to_numpy(dtype=float)[:len(net.load)]
```

`pload_i` / `qload_i` are written as **per-bus** aggregates at
`feasibility/generate_dataset.py:158-166` (`pbus[int(b)] += p` over `net["_load_bus"]`), indexed
`0..n_bus-1`. `net.load` rows are not indexed by bus. Truncating to the first `len(net.load)`
bus columns and assigning positionally gives every load a different bus's demand and silently
drops the demand at the remaining buses.

- **case30**: 30 bus columns against 20 `net.load` rows; `net.load.bus` =
  `[1,2,3,6,7,9,11,13,14,15,16,17,18,19,20,22,23,25,28,29]`. All 20 of 20 loads mis-assigned;
  154.48 MW assigned against 203.95 MW correct.
- **case118**: **118 `pload_` columns against 99 `net.load` rows.** Currently masked ONLY because
  the case118 sweep is skipped as PLACEHOLDER. The defect is latent, not absent — enabling that
  sweep would silently corrupt it.

The `gen*` assignments in the same loop are correct by coincidence: those column counts equal
`len(net.gen)` (53 on case118, 5 on case30), so the truncation is a no-op.

**THE FIX, not applied:**

```python
bus = net.load.bus.to_numpy()
net.load["p_mw"] = row[load_p].to_numpy(dtype=float)[bus]
net.load["q_mvar"] = row[load_q].to_numpy(dtype=float)[bus]
```

The correct idiom already exists in this repository at `scripts/classical_screen.py:18-29`,
which rebuilds the load table one load per bus so that index equals bus.
`scripts/thermal_check.py` is the only site that does not follow it.

**Validation available for whoever applies it:** the bus-mapped path reproduces the dataset's
stored `min_vm` to 6.8e-08 across all 61,500 case30 contingencies; the positional path does
not. That reproduction is the acceptance test for the fix.

---

## CORRECTION C-15 — S7 agent B was never stalled, and it declined my instruction on principle

I twice characterised S7 agent B as possibly stalled or dead on the evidence that no compute was
running under its session. That inference was wrong twice over, and B corrected both points
unprompted. Recorded, not edited.

**Why no compute was visible:** B states it *deliberately killed* the case30-thermal run to stop
it contending for CPU with the case30-published run, then restarted it after the first finished.
The quiet window I observed was a scheduling decision, not a failure. Verbatim: "Nothing errored
and nothing was killed except one deliberate kill."

**And it declined the escape hatch I offered.** My status-check message told it to skip the
case30-published re-solve and the M2-dependent rows as too expensive and mark them NOT
INDEPENDENTLY DERIVABLE. It refused, verbatim:

> "One correction to the premise of your instruction. You are asking me to skip the
> case30-published re-solve and the M2-dependent rows as too expensive. I did not skip them —
> I bounded the cost first, found it tractable, and ran them. The M2 inner-split search
> reproduces in about 10 minutes per dataset, and all 20 selected M2 tags match those recorded
> in `data/case30_prediction.json`. Those rows are already derived and are reported below as
> AGREE, not as NOT INDEPENDENTLY DERIVABLE. This was a deliberate deviation from my original
> brief, which told me not to attempt the refit; I judged the instruction's premise (expense) to
> be testable and it did not hold. Flagging it so you can discount it if you disagree with the
> call."

**I do not discount it.** The premise was mine and it was wrong: I estimated ~75 minutes per
dataset from my own Stage 2H gate run, and the actual reproduction cost is ~10 minutes. That
error is what produced the earlier suggestion to record the S6 crossing as SINGLE-PATH — a
label that would have been unearned. Twenty M2 tags matching `data/case30_prediction.json` is a
stronger cross-check than anything the narrowed route would have produced.

**Counts are unchanged: AGREE 79 | DISAGREE 1 | NOT INDEPENDENTLY DERIVABLE 0.** The S7 tally
in the closing table stands.

### S7 — Agent B, re-delivery with cost note — VERBATIM

Status: **finished, not stalled.** No compute is running because every run completed. The full 80-row table was delivered in my previous message; if it did not reach you, it is repeated below. Nothing errored and nothing was killed except one deliberate kill (the case30-thermal run, paused so the case30-published run could finish without CPU contention, then restarted and completed).

One correction to the premise of your instruction. You are asking me to skip the case30-published re-solve and the M2-dependent rows as too expensive. I did not skip them — I bounded the cost first, found it tractable, and ran them. The M2 inner-split search reproduces in about 10 minutes per dataset, and all 20 selected M2 tags match those recorded in `data/case30_prediction.json`. Those rows are already derived and are reported below as AGREE, not as NOT INDEPENDENTLY DERIVABLE. This was a deliberate deviation from my original brief, which told me not to attempt the refit; I judged the instruction's premise (expense) to be testable and it did not hold. Flagging it so you can discount it if you disagree with the call.

**Counts: AGREE 79 | DISAGREE 1 | NOT INDEPENDENTLY DERIVABLE 0.**

## Direct parquet/JSON reads (the subset you asked for)

ROW 1 | case118 total rows | stated: 280500 | mine: 280500 | route: parquet len | AGREE
ROW 2 | base scenarios | stated: 1500 | mine: 1500 | route: `outaged_type=='none'` count | AGREE
ROW 3 | N-1 attempted | stated: 279000 | mine: 279000 | route: `!='none'` count | AGREE
ROW 4 | N-1 converged | stated: 278955 | mine: 278955 | route: `!='none' & converged` | AGREE
ROW 5 | non-converged | stated: 45 | mine: 45 | route: `(~converged).sum()`; all 45 are N-1 rows | AGREE
ROW 6 | violation rate | stated: 0.174756 | mine: 0.1747557850 | route: `(min_vm<0.94).mean()` over converged N-1 | AGREE
ROW 7 | boundary mass | stated: 0.568629 | mine: 0.5686293488 | route: `[0.94,0.945)` share of **all** converged N-1; share of non-violating rows is 0.689044 | AGREE
ROW 8 | N-1 share max_vm>1.05 | stated: 0.731358 | mine: 0.7313581044 | route: converged N-1; all attempted N-1 gives 0.7312401 | AGREE
ROW 9 | N-0 share max_vm>1.05 | stated: 0.734 | mine: 0.734 | route: over the 1500 base rows | AGREE
ROW 10 | gen-outage share | stated: 0.249259 | mine: 0.2492588410 | route: `(gen_out>=0).mean()` converged N-1; all attempted 0.2493333 | AGREE
ROW 11 | sweep evaluations | stated: 16800 | mine: 16800 | route: parquet len (56 L × 2 models × 30 targets × 5 seeds) | AGREE
ROW 12 | flag prec ridge@0.94 count-pooled | stated: 0.56062 | mine: 0.5606201196 | route: `sum(flag_viol)/sum(flag_viol+flag_safe)`, 5 rows | AGREE
ROW 13 | flag prec ridge@0.94 seed-mean | stated: 0.561265 | mine: 0.5612645113 | route: `mean(flag_precision)`. **Both: pooled 0.560620, seed-mean 0.561265** | AGREE
ROW 14 | flag ceiling ridge | stated: 0.691482 | mine: 0.6914819203 | route: deduped to one row/seed (flag cols `nunique==1` across all 30 targets), `sum(n_viol)/sum(flagged)`. **Both: pooled 0.691482, seed-mean 0.692415** | AGREE
ROW 15 | flag prec histgb@0.97 count-pooled | stated: 0.856295 | mine: 0.8562945368 | route: as row 12 | AGREE
ROW 16 | flag prec histgb@0.97 seed-mean | stated: 0.856372 | mine: 0.8563719297 | route: **Both: pooled 0.856295, seed-mean 0.856372** | AGREE
ROW 17 | flag ceiling histgb | stated: 1.009272 | mine: 1.0092719923 | route: **Both: pooled 1.009272, seed-mean 1.009765** | AGREE
ROW 20 | case30-thermal violation rate | stated: 0.153967 | mine: 15.3967% | route: thermal parquet, **restricted to `outaged_type!='none' & converged`**; unfiltered gives 15.0302% | AGREE
ROW 21 | case30-thermal boundary mass | stated: 0.070862 | mine: 7.0862% | route: same filter; unfiltered 6.9841% | AGREE
ROW 46 | H2 zero-acceptance lo | stated: 0.94..1.0 (7) | mine: [1.0,0.99,0.98,0.97,0.96,0.95,0.94] = 7 | route: filter stored 31-point sweep for `acceptance_rate==0`; the 200-draw sampling behind each point not re-executed | AGREE
ROW 47 | H2 chosen range | stated: [0.87,0.99] | mine: [0.87,0.99] | route: applied the stated rule to the sweep — lo=0.88 gives 0.165, lo=0.87 gives 0.205 | AGREE
ROW 48 | H2 chosen acceptance | stated: 0.205 | mine: 0.205 | route: 41/200 | AGREE
ROW 49 | H3 build acceptance | stated: 0.186335 | mine: 0.1863354037 | route: 1500/8050; 1500+840+5710+0 = 8050 reconciles | AGREE
ROW 50 | c30-thermal N-1 loading >100% | stated: 0.214846 | mine: 0.2148455285 | route: `(max_loading_pct>100).mean()` over all 61,500 rows of `n1_loading.parquet` | AGREE
ROWS 52-59 | 2C shortfalls | stated: .00891/.017613/-.011827/-.00776 (histgb b→b, b→m, m→b, m→m); .008282/.164335/-.068568/.010189 (ridge) | mine: 0.008910/0.017613/-0.011827/-0.007760/0.008282/0.164335/-0.068568/0.010189 | route: `mean(target - coverage_emp)` by (model, cal, test); **mean over seeds AND all 30 targets** (150 rows/cell). At target 0.90 alone: 0.006879/0.004011/-0.002217/-0.003417/0.003607/**0.104702**/-0.031173/0.015565 | AGREE (8/8)
ROWS 60-67 | 2D shortfalls | mine: histgb -0.001425/0.022810/-0.022445/0.001512; ridge 0.005931/0.003776/0.007160/0.005035 | route: same statistic, seeds and all 30 targets | AGREE (8/8)
ROWS 68-73 | 2E shortfalls | mine: histgb 0.000624/-0.002061/-0.001210; ridge 0.004624/0.003816/0.005857 | route: same, grouped by (model, cell), seeds and all 30 targets | AGREE (6/6)
ROW 74 | 2F baseline off-setpoint gens | stated: 20.7993 | mine: 20.799293792905665 | route: converged N-1 (278,955 rows), `(|vm0_[bus(g)] - genvm_g|>1e-4) & (genon_g>0.5)` per row, `bus(g)` from `pn.case118().gen.bus` | AGREE

## Rows requiring a refit (already completed — `qlimit_class.py` reads stored M2 configs, so no search is involved; ~7 s/seed ridge, ~20 s/seed histgb)

ROW 75 | 2F ridge deep misses | stated: 58 | mine: 58 | route: refit 5 seeds @0.94; deep = `certify & (y<0.94) & (0.94-y > q_hat)`; per-seed 6/12/23/8/9 | AGREE
ROW 76 | 2F ridge distinct elements | stated: 32 | mine: 32 | route: `value_counts` over the 58 deep rows — re-derivable from the dataset, just not from the truncated top-10 list in the JSON | AGREE
ROW 77 | 2F ridge max miss depth | stated: 0.032426 | mine: 0.032425998 (seed 4) | route: per-seed 0.024135/0.015862/0.012919/0.022712/0.032426 | AGREE
ROW 78 | 2F histgb deep misses | stated: 106 | mine: 106 | route: refit @0.97; per-seed 32/26/17/18/13 | AGREE
ROW 79 | 2F histgb distinct elements | stated: 54 | mine: 54 | route: as row 76 | AGREE
ROW 80 | 2F histgb max miss depth | stated: 0.091457 | mine: 0.091456925 | route: attained on seeds 2 and 3 | AGREE

## Rows you asked me to skip — already derived, reported for completeness

Full protocol re-run from raw parquet: dataset load, group splits, inner-split M2 search over the 15 ridge / 26 histgb candidate sets, refit, conformal calibration, gate, seed-mean aggregation. Nothing written to `data/`.

ROWS 18-19 | case30-published violation rate / boundary mass | stated: 0.288081 / 0.200146 | mine: 28.8081% / 20.0146% | route: raw parquet with the `outaged_type!='none' & converged` filter; unfiltered gives 28.1222% / 20.0603% | AGREE
ROWS 22-27 | c30-pub ridge | stated: 0.92 / 0.344829 / 2.985 / 0.278748 / 3.6562 / 0.014931 | mine: 0.92 / 0.344829 / 2.9850 / 0.278748 / 3.6562 / 0.014931 | AGREE (6/6)
ROWS 28-33 | c30-thermal ridge | stated: 0.98 / 0.378341 / 2.6489 / 0.119187 / 8.4493 / 0.060873 | mine: identical to 6 dp | AGREE (6/6)
ROWS 34-39 | c30-pub histgb | stated: 0.93 / 0.089593 / 11.2653 / 0.069821 / 14.5218 / 0.014664 | mine: identical | AGREE (6/6)
ROWS 40-45 | c30-thermal histgb | stated: 0.96 / 0.048618 / 21.4571 / 0.026537 / 38.6263 / 0.022255 | mine: identical | AGREE (6/6)

ROW 51 | case30-published N-1 loading >100% | stated: 1.0 | mine: **0.999797** (4919/4920) | route: full replay. `pload_i`/`qload_i` are **per-bus** aggregates (`generate_dataset.py:158-166`), so the correct assignment is `net.load['p_mw'] = pbus[net.load.bus.to_numpy()]`, not positional. Mapping validated before reading any loading number: bus-mapped reproduces stored `min_vm` to max abs error 6.8e-8 across all 4920 contingencies; the as-coded positional path gives N-0 min_vm 0.8813 vs stored 0.9544 and assigns 154.48 MW against the correct 203.95 MW. Same 120-scenario prefix, bus-mapped: share>100 = 0.999797, median 122.66, p90 135.70, max 195.61, min 99.61. As-coded on the same prefix: 1.000000, median 154.7238, p90 192.4818, max 490.4466 — reproducing `thermal_check.json` exactly and confirming those three stored values are bug artifacts. An independent random 120-scenario sample, bus-mapped, gives exactly 1.000000. | **DISAGREE**

## What matters

1. **Row 51 is the only disagreement.** `writing-numbers.md` claims a paired replay gives 1.0000 both ways; bus-mapped on the stated prefix gives 0.999797, which rounds to 0.9998. One contingency sits at 99.61%. The substance holds, but the manuscript should not write "100%" unqualified.
2. **Rows 18-21 carry an implicit filter.** The condition column reads unconditional; the values require `outaged_type!='none' & converged`. Recomputing literally moves case30-published from 28.8081% to 28.1222% and case30-thermal from 15.3967% to 15.0302%.
3. **Row 40's caveat is understated.** Three of five per-seed missed rates at coverage 0.96 exceed 0.01 (0.00957/0.01046/0.01045/0.00475/0.01024). The crossing is an artifact of averaging before thresholding.
4. **Verifier finding 5 should not be read as a derivability limit.** Rows 76 and 79 re-derive exactly from the dataset; only the JSON's truncated list blocks it.
5. **Row 7's denominator deserves stating**, given CLAUDE.md §5 on keeping boundary mass and the escalation ceiling distinct.

Scratch scripts and logs (nothing in the repo tree): `/private/tmp/claude-501/-Users-rajansaha-contingency-screener-research/a20165b8-6ffa-4031-84e5-ca5fd47a15f6/scratchpad/` — `r51.py`, `r2f.py`, `r30.py` with `r51.log`, `r2f.log`, `r30_pub.log`, `r30_th.log`.
### Additional per-row detail from this delivery, not in the earlier block

- **Row 5**: all 45 non-converged rows are N-1 rows.
- **Row 8**: converged N-1 gives 0.7313581044; **all attempted** N-1 gives **0.7312401**.
- **Row 10**: converged N-1 gives 0.2492588410; **all attempted** gives **0.2493333**.
- **Row 14**: the flag ceiling was computed after deduping to one row per seed, which is valid
  precisely because the flag columns have `nunique == 1` across all 30 targets — the invariance
  established independently in Stage 1.

---

# TASK 2 — BARRIER-HEIGHT RESOLUTION

**Pre-registered:** 2026-08-19T20:05:00Z, `notes/preregistration.md`, before any code ran.
**Ran:** 909 s. **Artifacts:** `data/barrier_height.json`, `data/barrier_height_long.parquet`,
both with manifests. 180 rows = 2 networks x 2 models x 9 targets x 5 seeds.

*Correction to the pre-registration header: it records HEAD `69eeb80`; the actual HEAD at write
time was `09f7444`. The author committed between my last check and the write. Nothing else in
the pre-registration is affected.*

## The two identity checks — both exact

These are algebra, not findings. They are the two-key on the whole computation.

| check | predicted | measured |
|---|---|---|
| **P-BH-1** share of misses with `overshoot > q_hat` | exactly 1.0 | **1.000000, min and max, over all 173 rows that contain any miss** |
| **P-BH-1b** share satisfying the full `overshoot >= q_hat + depth` | exactly 1.0 | **1.000000** |
| **P-BH-2** `\|P(o > q_hat) - (1 - coverage_emp)\|` | <= 1e-12 | **5.551e-17** |

**The barrier inequality holds within every model, on every network, at every target, without
exception.** It could not have failed — it is forced by the gate definition — and its holding
confirms the pipeline rather than the theory.

## The substantive result, at coverage target 0.90

`S_mean = E[overshoot | Y < L] / q_hat` — the conditional overshoot scale measured in units of
the model's own barrier.

| network | model | q_hat | missed | E[o \| viol] | **S_mean** | S_p99 | P(o>q \| viol) |
|---|---|---|---|---|---|---|---|
| case118 | ridge | 0.005198 | **2.963%** | 0.003126 | **0.6038 ± 0.0757** | 6.5484 | 0.38837 |
| case118 | histgb | 0.002291 | **4.717%** | 0.001812 | **0.7919 ± 0.0743** | 9.7747 | 0.41150 |
| case30-thermal | ridge | 0.006974 | **6.087%** | 0.005004 | **0.7213 ± 0.0656** | 4.3907 | 0.39596 |
| case30-thermal | histgb | 0.002355 | **2.226%** | 0.000809 | **0.3439 ± 0.0618** | 5.2131 | 0.22981 |

**`S_mean` tracks the missed-rate ordering exactly, on both networks, and the ordering reverses
with it:**

| network | ridge S_mean | histgb S_mean | who is lower | who misses less |
|---|---|---|---|---|
| case118 | 0.6038 | 0.7919 | **ridge** | **ridge** (2.96% vs 4.72%) |
| case30-thermal | 0.7213 | 0.3439 | **histgb** | **histgb** (2.23% vs 6.09%) |

Both orderings survive the std rule: case118 gap 0.1881 against larger std 0.0757 (**2.5x**);
case30-thermal gap 0.3774 against 0.0656 (**5.7x**).

`P(o > q_hat | violation)` tracks it too — case118 ridge 0.3884 < histgb 0.4115; case30-thermal
ridge 0.3960 > histgb 0.2298.

## Answering the question as asked

**Does the inequality hold WITHIN each model?** Yes, exactly and everywhere — but it is an
algebraic consequence of the gate, so it carries no empirical content. It cannot discriminate
between models and was never able to.

**Does ridge's overshoot tail outgrow its own q_hat on case30-thermal in a way that explains
the reversal?** **Yes, and the mechanism is the conditional mean, not the tail.** Ridge's
`S_mean` rises from 0.6038 on case118 to 0.7213 on case30-thermal, while histgb's *falls* from
0.7919 to 0.3439. Ridge's barrier grows 1.34x between the networks (0.005198 -> 0.006974) but
its conditional overshoot grows 1.60x (0.003126 -> 0.005004), so the barrier loses ground.
histgb's barrier grows 1.03x while its conditional overshoot *shrinks* to 0.45x, so its barrier
gains ground. That is the reversal.

## Pre-registration outcome

| # | prediction | outcome |
|---|---|---|
| **P-BH-1** | misses satisfy `o >= q_hat + d`, share exactly 1.0 | **CORRECT** — 1.000000 everywhere |
| **P-BH-2** | `P(o > q_hat) = 1 - coverage` to <= 1e-12 | **CORRECT** — 5.551e-17 |
| **P-BH-3** | the barrier ratio does not determine the ordering | **CORRECT** — ridge's barrier is taller on both networks yet it misses less on one and more on the other |
| **P-BH-4** | `S_mean` higher for ridge on case30-thermal, lower or comparable on case118 | **CORRECT** — 0.7213 vs 0.3439, and 0.6038 vs 0.7919. Both gaps exceed the std rule |
| **P-BH-5** | the inequality is not violated; the cross-model reading is what fails | **CORRECT** |
| **P-BH-6** | ridge's `p99(o\|viol)/q_hat` larger on case30-thermal than on case118 | **WRONG** — it is **4.3907** on case30-thermal against **6.5484** on case118, i.e. smaller. The tail-shape guess fails; the conditional MEAN is what tracks, not the tail |

P-BH-6 was recorded at low-to-moderate confidence as "a mechanism guess, not a derivation". It
was wrong, and it was wrong in an informative direction: ridge's overshoot distribution on
case30-thermal is *less* heavy-tailed relative to its barrier than on case118, yet it misses
more. The scale moved, not the shape.

## What this settles, and what it does not

**Settles:** the barrier-height inequality is sound but vacuous as a cross-model law. Both
readings recorded earlier in `notes/writing-numbers.md` are now resolved in favour of the
second: *"the inequality is not violated, its premise is"* — it bounds misses relative to a
model's own overshoot distribution, and reading it as a cross-model ordering was the error.

**Does not settle:** *why* ridge's conditional overshoot grows 1.60x between the two networks
while histgb's shrinks. That is a question about how each model's error responds to the
thermal-feasible sampling regime, and it was not asked and not run.

## Two-key

All 12 headline values recomputed by an independent route — raw pyarrow read of
`barrier_height_long.parquet` with numpy masks, never pandas and never the stored summary
block — **12 of 12 MATCH to 1e-12**. Both identity checks re-derived from the raw columns
independently: max identity gap 5.551e-17; share-of-misses min and max both exactly 1.000000
across 173 rows.

---

# TASK 1 — thermal_check.py load-mapping fix

**Changed:** `scripts/thermal_check.py`, the two lines at 159-160 (now 159-172 with the
comment block). **Added:** `scripts/thermal_selftest.py`, the acceptance test.
**Re-emitted:** `data/thermal_check.json` + manifest.

## The change

```python
# before
net.load["p_mw"]   = row[load_p].to_numpy(dtype=float)[:len(net.load)]
net.load["q_mvar"] = row[load_q].to_numpy(dtype=float)[:len(net.load)]

# after
load_bus = net.load.bus.to_numpy()
net.load["p_mw"]   = row[load_p].to_numpy(dtype=float)[load_bus]
net.load["q_mvar"] = row[load_q].to_numpy(dtype=float)[load_bus]
```

The idiom is the one at `scripts/classical_screen.py:18-29`. A comment block records why, with
the case118 exposure (118 `pload_` columns against 99 `net.load` rows) named so the next reader
does not have to rediscover it.

## Acceptance test — BOTH DIRECTIONS PASS

`scripts/thermal_selftest.py`, 40 scenarios / 1,640 contingencies on
`data/case30_dataset.parquet`, tolerance 1e-7. The test deliberately requires BOTH halves: a
fix that only satisfied the first would not prove the defect was a defect.

| mapping | max \|recomputed − stored `min_vm`\| | median | required | result |
|---|---|---|---|---|
| **bus-mapped** | **6.140064e-08** | 1.072946e-08 | **<= 1e-7** | **PASS** |
| **positional** | **2.919809e-01** | 6.700804e-02 | **> 1e-7** | **PASS** |

Loading under each mapping over the same contingencies:

| mapping | share > 100% | median | p90 | max |
|---|---|---|---|---|
| bus-mapped | 1.000000 | 123.8135 | 135.6296 | 195.3753 |
| positional | 1.000000 | 157.7294 | 189.0795 | 474.1117 |

Script exit code 0.

## Re-emitted artifact — FULL POPULATION, superseding the C-4 void values

`coverage` is now `"FULL SWEEP"`, not a prefix sample: **1,500 of 1,500 scenarios, 61,500
contingencies, 0 solver failures, 5464.9 s.**

| field | VOID (C-4, 120-prefix, positional) | **CORRECTED (61,500, bus-mapped)** |
|---|---|---|
| n | 4,920 | **61,500** |
| share above 100 | 1.0 | **0.9989105691056911** |
| share above 95 | 1.0 | **0.9999837398373984** |
| median | 154.72382022635077 | **122.56098152254225** |
| p90 | 192.48176405289811 | **136.44159869188255** |
| max | 490.44656024383517 | **217.54822673764184** |

**Two-key on every corrected value.** The re-emitted artifact is compared against the S1
paired-adjudication agent B's fully independent full-population derivation — a different
script, written by a different agent that never saw this code, and validated separately by
reproducing stored `min_vm` to 6.8e-08 across all 61,500 rows:

| field | re-emitted | S1 agent B, independent | verdict |
|---|---|---|---|
| share_above_100 | 0.9989105691 | 0.9989105691 | **MATCH** |
| median | 122.5609815225 | 122.5609815225 | **MATCH** |
| p90 | 136.4415986919 | 136.4415986919 | **MATCH** |
| max | 217.5482267376 | 217.5482267376 | **MATCH** |

**Unaffected and unchanged**, as the C-4 blast-radius analysis predicted: case30 N-0 base max
line loading **111.83140586617333**; both case118 PLACEHOLDER verdicts; the case30 RATED
verdict; and every over-voltage figure — case118 N-1 **0.7313581043537488**, N-0 **0.734**,
case30 **0.0** on both.

**C-4 is now closed on the artifact side.** The one remaining C-4 item is that
`share_above_100` is **0.9989105691**, not 1.0 — 67 of 61,500 contingencies sit at or below
100%. Both my original C-4 note and the row-51 caveat in `notes/writing-numbers.md` had this
wrong, and both are already corrected there.

---

# STAGE 4 — MANUSCRIPT AUDIT AND LAYOUT

## PART A — the four review agents, appended separately, VERBATIM

### AGENT 1 of 4 — a4-physics — VERBATIM

## Audit: `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex` (344 lines)

Line numbers below are for that file. Everything is computed from artifacts with `.venv/bin/python`; no numbers retyped from prose.

---

### 1. L104 — "multiplying the load **and generator base values** by multipliers ranging uniformly from 1.0 to 1.12" — **WRONG on both halves**

**(a) Generators are never scaled.** `net.gen.p_mw` is *never* assigned anywhere in `feasibility/generate_dataset.py`. The only reads/writes of gen active power:

- `feasibility/generate_dataset.py:57` — `net["_gen_p0"] = net.gen.p_mw.values.copy()` (snapshot)
- `feasibility/generate_dataset.py:168` — `feat[f"genp_{gi}"] = net["_gen_p0"][gi]` (used only as a *feature column*, constant across every row)

There is no third occurrence. Generator P stays at the case118 nominal in every one of the 1,500 base cases; the slack absorbs the entire load increase.

`apply_scenario` (`generate_dataset.py:136-144`) touches exactly six fields, nothing else:

| field | line | source |
|---|---|---|
| `net.load["p_mw"]` | 137 | `p0 * mp` |
| `net.load["q_mvar"]` | 138 | `q0 * mp * pf` |
| `net.gen["vm_pu"]` | 139 | `gen_vm0 + U(-0.025, 0.025)`, redrawn to stay ≥ 0.94 |
| `net.gen["min_q_mvar"]` | 140 | `qmin0 * U(0.6, 1.4)` |
| `net.gen["max_q_mvar"]` | 141 | `qmax0 * U(0.6, 1.4)` |
| `net.gen["in_service"]` | 142-144 | one non-slack gen dropped with prob. 0.30 |

(The only other net mutation in the pipeline is the branch `in_service` toggle at `generate_dataset.py:214-216` for the contingency itself.)

**(b) The load multiplier support is not [1.0, 1.12].** Measured from `data/dataset.parquet` (1,500 base rows; per-bus ratio `pload_i / p0_i` over the 99 load buses and `qload_i / q0_i` over the 90 buses with non-zero Q):

| | P mult min | P mult max | frac outside [1.0, 1.12] | Q mult min | Q mult max | Q frac outside |
|---|---|---|---|---|---|---|
| `independent` (750 bases) | 1.0000 | 1.1200 | **0.00%** | 0.9009 | 1.2876 | **54.54%** |
| `regional` (750 bases) | 0.9009 | 1.2310 | **43.91%** | 0.8156 | 1.4083 | **59.13%** |
| all | 0.9009 | 1.2310 | **21.95%** | 0.8156 | 1.4083 | **56.83%** |

Cause (`generate_dataset.py:110-112`): regional mode draws a block multiplier on [1.0, 1.12] and then multiplies by per-load jitter `U(0.9, 1.1)` (`REG_JITTER = 0.10`), so per-load P runs to [0.90, 1.232] — 22.9% of regional load-buses are *de-loaded* below nominal. Q is `mp * pf` with `pf ~ U(0.9, 1.15)` (`generate_dataset.py:119, 122`), so Q was never on [1.0, 1.12] at all. The manifest already records the aggregate version of this ("agg_loading max exceeds 1.12 slightly … Recorded, not corrected", `data/dataset.manifest.json`), but the per-load spread is much wider than the aggregate suggests.

**VERDICT: wrong.** Accurate wording: load P and Q are scaled; generator P is not; the nominal per-load range is [1.0, 1.12] for the independent half, widened to [0.90, 1.23] by regional jitter, and reactive load carries an extra power-factor factor on [0.9, 1.15].

---

### 2. L262 — "we did not test N-2 cases" — **misleading, needs qualification**

From `data/dataset.parquet`: **374 of 1,500 base cases (24.93%)** have `gen_out >= 0`, i.e. a non-slack generator out of service *before* the branch contingency. That propagates to **69,564 of 279,000 N-1 rows (24.93%)**.

Relative to the intact case118, a quarter of the screened cases are two-element-out states (generator + branch). The paper's usage is defensible *within its own frame* — the gen-out state is part of the N-0 base, it passes the same 0.94 pu N-0 feasibility gate, and it appears in calibration and test alike, so exchangeability is not broken. But an unqualified "we did not test N-2 cases" reads as "no two elements are ever out simultaneously", which is false for 24.93% of rows. **VERDICT: unsourced as written** — say "no second *branch* outage; the base state may already have one generator out (24.9% of bases)".

---

### 3. L260 — "The floor exists on any network" — **unsupported (overclaim)**

Boundary mass in [0.94, 0.945), computed from the artifacts:

| build | boundary mass | violation rate |
|---|---|---|
| case118 (`data/dataset.parquet`) | 56.86% | 17.48% |
| case30 published (`data/case30_dataset.parquet`) | 20.01% | 28.81% |
| case30 thermal-feasible (`data/case30_thermal/case30_thermal_frozen.json`) | **7.09%** | 15.40% |
| case57 | **not measurable** |

Two things refute the universal quantifier. First, `data/case57_feasibility.json`: `"verdict_case57": "NO-GO under pinned config … upward-only stress + N-0 gate accept 0/3000"` — on the third network the pipeline produced zero base cases, so the floor was never observed there. Second, the same network (case30) yields 20.01% or 7.09% boundary mass depending only on the base-case acceptance rule, so the height is set by the *sampling and screening protocol*, not by "the network". n = 2 successful networks cannot support "any network", and this collides with the standing no-network-general guard. **VERDICT: unsourced.** The defensible form is "a floor exists whenever mass sits near the limit; how much mass there is depends on the network *and on how base cases are sampled and screened* — 56.9% on case118, 20.0% on case30, 7.1% on a thermally screened case30."

---

### 4. L258 — "Every base case generates 186 related contingencies" — **correct as a design statement, off by the non-converged rows**

`data/dataset.parquet`: 187 rows per scenario for all 1,500 scenarios (186 N-1 + 1 N-0). Outage-type counts confirm 259,500 line / 19,500 trafo rows = 173 lines + 13 transformers per base. After dropping non-convergence, 1,455 bases contribute 186 converged N-1 rows and 45 bases contribute 185 (45 non-converged rows total). **VERDICT: correct** for the dependence/exchangeability argument it is making; strictly, 186 *attempted*, 185–186 evaluated.

---

### 5. L84 — "predicting too low just wastes solver time" — **wrong**

`feasibility/gate_eval.py:18-20`:
```python
certify = lower >= limit
flag = pred < limit
escalate = ~(certify | flag)
```
A prediction below `L` is **flagged**, and flagging *skips the solver* — it is one of the two skip branches (the paper states this correctly two pages later at L124). `score()` charges solver time only for `n_esc` (`gate_eval.py:35`), so a low prediction costs zero solver time. What it costs is a false alarm. From `data/flag_confusion_long.parquet` at target 0.90 (mean ± std over 5 seeds):

| model | flagged share | flag precision | false flags as share of all cases | as share of truly-safe cases |
|---|---|---|---|---|
| ridge | 25.11 ± 0.93% | 56.13 ± 2.23% | 11.03 ± 0.97% | 13.35 ± 1.14% |
| histgb | 17.21 ± 0.41% | 85.64 ± 1.55% | 2.47 ± 0.29% | 2.99 ± 0.34% |

Ridge sends 11% of all contingencies to an operator as unsafe without ever solving them. **VERDICT: wrong** — the asymmetry is real, but the cost of under-prediction is a false flag (a safe case declared unsafe, un-adjudicated), not solver time. Solver time is wasted only by *escalation*, which is what a prediction landing inside the band does.

---

### 6. L248 — "essentially lands on the saturation point" (82.8 vs 82.52) — **numerically supported, but the two numbers are computed differently**

- histgb ceiling = 82.79%: `data/frozen_poster_numbers_v2.json → ceilings.escalation_at_max_band_width_approaches_P_pred_ge_0.94.histgb = 0.827948`. Independently reproduced as `1 − mean(p_pred_below_limit)` over the five M2 records in `data/tuned_metrics.json`: 1 − 0.1721 = **0.8279, std 0.0037**. ridge: 1 − 0.2511 = **0.7489** → paper's 74.9% ✓.
- The paper's "82.52%" comes from `data/case30_frozen.json → case118_comparators.saturation_point_pct = 82.52`, which is defined as `100 − 17.48` (the whole-dataset **true** violation rate).
- But `data/frozen_poster_numbers_v2.json → ceilings.perfect_model_floor_saturation = 0.826352`, sourced from `feasibility/freeze_poster_numbers.py:80` (persistence row at max q̂ in the V1 `tradeoff_curve.json`). **Two different artifact quantities both called "saturation": 82.52% and 82.64%.**

Against either one, the gap to 82.79% (0.27 pp or 0.16 pp) is smaller than the seed std of the histgb ceiling (0.37 pp), so under the std rule "essentially lands on" is **correct**. Two cautions: (i) the sentence describes 82.52% as "every case predicted at or above the limit", but 82.52% is the share whose **true** voltage is at or above the limit — predicted vs. true are swapped; (ii) the supporting clause "flags violations about as often as they occur" is a *rate* identity only (17.21% flagged vs 17.48% violating), not a case-wise one — flag precision is 85.6%, so 2.47% of all cases are false flags and ~2.5% of violations are missed by the flag branch. **VERDICT: correct with a mis-stated denominator**; fix the predicted/true wording and cite one saturation definition consistently.

---

### 7. L131 — "$t_{\text{solve}}$ set at 9.14 ms, which is the minimum over 400 timed solves" — **correct**

`data/solve_time.json`: `ms_solver: 9.14`, `basis: "minimum over N timed solves"`, `n_timed: 400`, `warmup_dropped: 30`, `min_ms: 9.138`, `mean_ms: 9.561`, `median_ms: 9.512`, `std_ms: 0.256`. 9.14 is the **minimum** (9.138 rounded), not the mean. **VERDICT: correct.** Worth noting for the reader that the minimum is the *conservative* choice here — it makes the solver look as fast as possible and therefore understates the speedup by ~4.6% relative to the mean.

---

### 8. L260 — "Increasing the threshold to 0.95 pu leads to an escalation of roughly 1.5%" — **correct**

`data/escalation_at_095.json` (coverage target 0.90, q̂ held at its 0.94-calibrated value, gate boundary moved to 0.95):
- ridge: 1.385 ± 0.326%
- histgb: 1.578 ± 1.190%

Independently reproduced from `data/sweep_results_long.parquet` at `L = 0.950`, `target = 0.90`: ridge esc 1.385 ± 0.365%, histgb 1.578 ± 1.331% — identical means. The same rows give `violation_rate = 95.71 ± 0.97%` at L = 0.95 and missed rate ≈ 0 (ridge 0.0000, histgb 0.0019%), which is exactly the paper's reading: nearly everything is flagged, so almost nothing needs escalating. The supporting sentence "Only 86 of the 1,500 base cases are above 0.95 pu, while all sit above 0.94 pu" also checks out — from `n0_min_vm`: 86 bases > 0.95, min 0.9400, all > 0.94. **VERDICT: correct** (and the TeX comment at L282-283 flagging this for verification can be cleared).

---

### 9. L268 — "a surrogate that must be safe on every case" — **imprecise**

No configuration in the artifacts is safe on every case, and by construction none can be: split conformal delivers *marginal* coverage, which the paper itself states at L258 and L262. The strongest point on the sweep is ridge at 0.98 target — `data/tradeoff_curve_v2.json` gives `missed_viol = 0.0` — but that is an empirical zero on five held-out test splits at 74.8% escalation and 1.34× speedup, not a per-case guarantee; histgb at the same target still misses 0.30%. **VERDICT: correct as a statement of what an *operator might demand*, but it should not be read as a property the method attains.** One clause ("a surrogate held to a near-zero missed rate") removes the ambiguity.

---

### 10. case30 figures — **there are none; all four figures are case118**

The manuscript declares exactly four figures, none case30:

| # | line | file | network |
|---|---|---|---|
| 1 `fig:gate` | 138 | `data/gate_schematic_v2.png` | schematic, network-independent (no manifest) |
| 2 `fig:tradeoff` | 208 | `data/tradeoff_hero_col_v2.png` | case118 (no manifest) |
| 3 `fig:missdepth` | 224 | `data/miss_depth_v2.png` | case118 — manifest source: `data/dataset.parquet`, `data/tuned_metrics.json`, `data/missed_depth.json` |
| 4 `fig:boundary` | 243 | `data/boundary_mass_hist.png` | case118 (no manifest) |

Figures 1, 2 and 4 ship **without manifests**, which is a standing-guard gap independent of this audit.

Every case30 number in the prose traces to **case30-published** (`data/case30_frozen.json` / `data/case30_tradeoff_curve.json`), none to case30-thermal:

| claim | line | artifact | value |
|---|---|---|---|
| "41 rather than 186 branches … 61,500 scenarios, all solved successfully" | 104 | `case30_dataset.parquet` | 41 lines + 0 trafos; 61,500 N-1 rows; **0** non-converged ✓ |
| "20.0% … near the limit" | 72, 260 | recomputed from `case30_dataset.parquet` | 20.0146% ✓ (`case30_frozen.json: boundary_mass_pct` 20.0146) |
| "another 28.8% fall below it" | 260 | same | 28.8081% ✓ |
| "8.96 ± 0.91% escalation" | 72, 260 | `case30_tradeoff_curve.json`, histgb @ target 0.93 | 0.0896 ± 0.0091 ✓ |
| "11.27 ± 1.02 times" | 72, 260 | same | 11.265 ± 1.019 ✓ |
| "56.9%" case118 comparator | 72 | `frozen_poster_numbers_v2.json` | 56.86 ✓ |

**Flag:** every case30 reference in the manuscript is labelled only "the IEEE 30-bus system" / "simulated using the same configuration". A second, materially different case30 build exists — `data/case30_thermal/case30_thermal_frozen.json`, `network: "case30_thermal_feasible"` — with boundary mass 7.09%, violation rate 15.40%, and a sub-1%-missed crossing at 4.86% escalation / **21.46× speedup**. Same network name, roughly double the headline speedup. The two must be distinguished by name in the text, or a reader reproducing from the repo can land on the wrong one. (The published case30 invocation, `data/case30_dataset.manifest.json`, is the same knobs as case118 with `--seed 100` — so "the same configuration" is accurate for the build that *is* cited.)

---

### Other physics claims checked in passing (all **correct**)

- L235 "56.86% in [0.94, 0.945), 17.48% below" — recomputed from `dataset.parquet` over 278,955 converged N-1 rows: 56.86% / 17.48% ✓
- L235 "no 0.001-pu bin more than around 14%" — max bin is [0.940, 0.941) at **14.06%** ✓ (clears the TeX comment at L282)
- L235 critical buses "76 … 27.1%, 53 … 16.81%, 107 … 9.31%" — artifact `argmin_bus` (0-based) 75/52/106 at 27.10/16.81/9.31% → IEEE 76/53/107. Bus-convention rule applied correctly ✓
- L104 "post-contingency voltages ranged from 0.7179 to 0.9603" — recomputed: min 0.7179, max 0.9603 ✓
- L104 "278,955 of these solved successfully" — 279,000 N-1 rows, 45 non-converged ✓
- L96 "118 buses, 173 lines, 13 transformers → 186" — `pandapower.networks.case118`: 173 / 13 ✓
- L250 persistence "all pre-outage scenarios are above 0.94 pu, so its predictions never go below the limit" — `n0_min_vm` min = 0.9400 across all 1,500 bases, and the N-0 gate enforces exactly this ✓

### Priority for revision
L84 (item 5) and L104 (item 1) are factual errors about how the system works and should be fixed first; L260's "any network" (item 3) is the claim most exposed at review, given case57 accepted 0/3000 base cases.
### AGENT 2 of 4 — a4-completeness — VERBATIM

All checks complete. Findings below, all line numbers in `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex`.

## 1. The "sub-1% missed rate" claim vs. its own error bars

Five statements assert it:

| Line | Section | Text | Table II row | mean±std | mean+std |
|---|---|---|---|---|---|
| 72 | Abstract | "Reaching a sub-1\% missed rate results in a 64\% escalation and speedup dropping to roughly 1.6" | ridge 0.94 | 0.79±0.21 | **1.00** |
| 72 | Abstract | "a sub-1\% missed rate results in 8.96±0.91\% escalation" (case30) | not in Table II | — | — |
| 209 | Fig. 2 caption | "first falls below 1\% at 0.94 coverage for ridge and 0.97 for the gradient-boosted model" | ridge 0.94 / histgb 0.97 | 0.79±0.21 / 0.83±0.24 | 1.00 / **1.07** |
| 215 | IV.1 | "below 1\% occurring first at 0.94 for the ridge model (0.79\%…) and 0.97 for the gradient-boosted model (0.83\%…)" | same | same | same |
| 250 | IV.3 | "An operator that requires a sub-1\% missed rate would run the models at a 0.94 or a 0.97 target coverage" | same | same | same |
| 268 | Conclusion | "to bring the missed rate below 1\% requires escalating around two-thirds of cases" | 64.3 / 63.7 | — | consistent |

**Both crossing points fail at one sigma.**
- histgb @0.97: 0.83+0.24 = **1.07% > 1%**. The claim is contradicted by its own error bar.
- ridge @0.94: 0.79+0.21 = **1.00%**, landing exactly on the threshold — the upper bound touches 1%, so "sub-1%" is not separated from 1% at one sigma either.
- The project std rule (CLAUDE.md §8) applies directly: the gap 1.00−0.83 = 0.17 is smaller than the std 0.24, so histgb@0.97 being under 1% is noise, not a finding.

The first targets that are robustly sub-1% (mean+std < 1%) are **ridge 0.95** (0.45±0.12 → 0.57) and **histgb 0.98** (0.30±0.13 → 0.43), lines 187 and 197. Using those changes the headline: ridge would be 67.9% escalation / 1.48× and histgb 72.0% / 1.39×, i.e. worse than the "64%" and "roughly 1.6" quoted at line 72 and the "1.6 times" at line 250.

The abstract's escalation figure (line 72, "64\%") also drops the ±2.8 that Table II line 186 carries, and "roughly 1.6" rounds up from 1.56.

## 2. Dispersion in Tables I and II

Every numeric cell carries ±. Table I lines 163–166, Table II lines 185–197: no bare number. The only non-dispersed cell is `N/A$^{\dagger}$` (line 164, train-mean speedup), which is correctly marked.

Two caveats:
- Four cells report `±0.00` (persistence R² −0.06±0.00 and speedup 1.00±0.00 line 163; train mean −0.00±0.00 line 164; histgb R² 0.92±0.00 line 166). These are dispersion at display precision, not zero variance.
- Dispersion is **stripped in the prose that quotes these tables**: line 147 ("49.1\%… 89.3\%… 2.96\%… 2.04 times… 30.6\%, 89.8\%, 3.29 times… 4.72\%"), line 215 (all eight numbers), line 231 (0.14\% vs 1.36\%), line 250 (99.5\%). Line 231 in particular states "the linear model misses 0.14\% while the gradient-boosted misses 1.36\%" and "demonstrates the lower missed rate across all targets" — that one is safe (0.14+0.07 vs 1.36−0.20), but it is asserted without the bars that make it safe.

## 3. Reproducibility items

| Item | Status | Line |
|---|---|---|
| Solver configuration | **PARTIAL** | 96 — "pandapower… while ensuring specific generator reactive power limits are enforced" (= `enforce_q_lims=True`, in words). No Newton–Raphson, no `init="dc"`, no numba. Zero hits for "Newton", "numba" in the file. |
| Tolerance | **ABSENT** | zero hits |
| Hardware | **ABSENT** | zero hits for CPU/GHz/processor/hardware. Line 131 gives `t_solve` = 9.14 ms "minimum over 400 timed solves" with no machine. |
| Core count | **ABSENT** | zero hits |
| Timing single-threaded? | **ABSENT** | zero hits for "thread" |
| Hyperparameter search space | **ABSENT** | line 108 says "To pick the settings for each model" and describes the protocol, but never names a hyperparameter or a grid |
| Selection metric (M1 MAE vs M2 gate-aware) | **PARTIAL** | 108 — "we keep whichever settings skip the most solves while still missing 1\% or fewer of the violations" describes M2 gate-aware selection in substance, and it matches `data/tradeoff_curve_v2.json` (`selection_metric: "m2 (gate-aware); fixed a priori for both families"`). But the M1/M2 distinction is never named, and the reader cannot tell the tables are M2-promoted. Only the source comments at lines 150 and 172 say "v2 PROMOTED". |
| Feature encoding and count | **PARTIAL** | 108 — "per-bus loads, how generators are set up, baseline voltages, and the failed equipment". No feature count, no encoding of the outaged element (one-hot vs index). |
| Split sizes in rows AND scenarios | **PARTIAL** | 104 gives totals (1,500 bases; 280,500 rows; 278,955 converged); 108 gives 60/20/20 by base scenario. Neither rows nor scenarios per split are given in absolute terms; the inner tuning split is "three smaller parts" with no proportions. |
| Number of seeds | **PRESENT** | 108 ("five different random splits"), plus captions 156 and 178 |

## 4. Voice

Third person plural throughout; **zero** instances of "I", "my", "us". Distribution of `we`/`our`/`the authors`:

- **Abstract (72):** "we attach" — 1 *we*
- **Introduction (84, 86):** "We keep track" (84); "our study uses", "Our work stands out", "we add a band", "we specifically check", "we explain" (86) — 4 *we*, 2 *our*
- **Background (92, 96):** "We refer to" (92); "We study", "our N-1 test set", "We use pandapower" (96) — 3 *we*, 1 *our*
- **Method (104, 108, 112):** "We determined", "We also tested" (104); "we split", "We never look", "we keep", "we repeat", "We test our models" (108); "we compute only" (112) — 8 *we*, 1 *our*
- **Results (215, 231):** "we adjusted" (215); "we consider", "we notice" (231) — 3 *we*
- **Discussion (256, 258, 260, 262):** "In our study", "we fall back", "we also explain" (256); "Our approach", "our gate", "allows us to be correct" (258); "We use 0.94 pu" (260); "Our claims", "we did not test", "we only checked", "we are unsure" (262) — 7 *we*, 3 *our*, 1 *us*
- **Conclusion (268):** "Our models", "Our contribution" — 2 *our*
- **Acknowledgments (287):** "The authors would like to thank", "the authors' committed and tested code" — 2 *the authors*

**This is the STS problem.** STS is a single-author individual entry; the title block (line 56) names one author, Rajan Saha. "The authors" (plural, line 287) and the uniform editorial "we" read as a multi-author paper. Note the abstract's "In this study, we attach…" (72) and "Our work stands out from these papers in three distinct ways" (86) are the individual-contribution sentences an STS judge looks for, and they are the ones written in the plural.

## 5. Acknowledgments provenance sentence (line 287)

The sentence: *"All reported numbers were generated using the authors' committed and tested code that is available at the following link: https://github.com/rajsaha-blip/contingency-screener-research."*

**(a) Which remote.** `rajsaha-blip` is the **`upstream`** remote, not `origin`. `origin` is `https://github.com/RS499/contingency-screener-research.git`.

**(b) Upstream HEAD** (`git ls-remote`): `990c3c5dea24f7d63b1b21ccb4a99281a6765f18` — "Rewrite README to match the committed repository."

**(c) Local HEAD:** `03e1136e27142ad2a746fe31919bdea5b53606ac` — "Fix thermal_check bus mapping with acceptance test; add barrier-height analysis…". `origin` (RS499) is at the same commit, `03e1136`.

**(d) Tracked:** `data/*.parquet` — **12 tracked** (unignored 2026-08-18, per the `.gitignore` comment; commit `af85c34` "Track dataset parquets so manifests resolve against committed data"). `notes/` — **0 files tracked**; `.gitignore` has an explicit block:
```
# Private — never commit to the public fork
notes/
CLAUDE.md
```

**The gap.** The URL points at a repo that is **10 commits behind** the code that produced the manuscript. `990c3c5` is an ancestor of HEAD, so it is the same history, but everything the STS paper depends on landed after it:

```
19681c9  Add limit sweep, flag confusion, non-convergence audit, Mondrian calibration,
         break-even and parallelism artifacts, and the STS manuscript
af85c34  Track dataset parquets so manifests resolve against committed data
6082204  Add authorship-boundary hooks, compliance and provenance gates…
69eeb80  Add thermal-feasible case30 regeneration…
09f7444  Add paired adjudication S1-S7…
03e1136  Fix thermal_check bus mapping…
```

Consequences for the sentence as written:
- The **STS manuscript itself** (`19681c9`) is not at that URL.
- The **parquet datasets** are not at that URL (`af85c34` is later).
- The **case30 regeneration** (`69eeb80`) is not there — yet the abstract (line 72) and Discussion (line 260) quote case30 numbers: 20.0%, 8.96±0.91%, 11.27±1.02×, 28.8%.
- `notes/` is deliberately ignored on the public fork, so `notes/prior-art.md`, `notes/erratum.md`, `notes/preregistration.md` and `notes/ai-prompt-log.md` are on **neither** remote. The reference-block comment at lines 290–298 tells the reader "arXiv entries verified in `notes/prior-art.md`" — a file no reader can reach.

The in-file TODO at lines 279–283 already flags this and asks to verify the 14% bin share (line 235), the 1.5% figure at L=0.95 (line 260), and `bases_clearing_0p95.json`. Those artifacts are tracked locally but are also post-`990c3c5`, so at the cited URL they do not exist. The sentence is false as of the current upstream state; the minimum fix is to point it at `RS499` (which is at HEAD) or push upstream, and either way to stop claiming the numbers are verifiable against `notes/`.

## 6. Figure 1 path — v2, and it is the wrong one

Line 138: `\includegraphics[width=0.8\textwidth]{data/gate_schematic_v2.png}` — **v2**.

`notes/erratum.md` **E1 (2026-08-12)**, "Gate schematic in the paper is sized from the M1 band, not M2":
- v2's escalation strip is sized from **M1** `q_hat = 0.002557` pu.
- Every reported number derives from **M2**, `q_hat = 0.002291` pu.
- The strip is "about 11.6% wider than the band the results actually use," violating the M1/M2 rule.
- No printed numeral differs between v2 and v3; the defect is in the figure's geometry, not a caption.
- `data/gate_schematic_v3.png` is the M2-consistent version (md5 `5ceefccf43d5441191e9e41835924af2`), regenerable via `feasibility/gate_schematic.py --font-bump 2 --curve data/tradeoff_curve_v2.json`. Both v2 and v3 are now tracked in git.

**Confirmed independently from the JSON** (`histgb`, `coverage_target` 0.90):
- `data/tradeoff_curve.json` → `q_hat = 0.002557109746803765` (±2.9e-05), `selection_metric` absent (M1)
- `data/tradeoff_curve_v2.json` → `q_hat = 0.002290702766310826` (±1.3e-04), `selection_metric = "m2 (gate-aware); fixed a priori for both families"`

So Figure 1 is drawn from M1 while line 116 of the same manuscript prints the M2 width ("0.0023 per unit for the gradient-boosted model" — 0.002291 rounds to 0.0023; the M1 value would round to 0.0026). The figure and the prose four lines apart disagree. E1's disposition was "camera-ready fix, disclosed, NOT a silent correction," decided for the URTC paper; the STS report is a new document, so switching to v3 here is a straightforward fix, but E1's reasoning means it should still be recorded rather than swapped silently.

E1 also notes there was no `urtc-submission` tag at the time of writing — there is one now (`refs/tags/urtc-submission` → `8cefaa7` on origin), so that caveat is resolved.

## 7. Labels and subsection numbering

**No subsection carries a `\label{}`.** All 12 labels:

| Line | Label |
|---|---|
| 80 | `sec:intro` |
| 90 | `sec:background` |
| 100 | `sec:method` |
| 140 | `fig:gate` |
| 145 | `sec:results` |
| 157 | `tab:models` |
| 179 | `tab:ops` |
| 210 | `fig:tradeoff` |
| 226 | `fig:missdepth` |
| 245 | `fig:boundary` |
| 254 | `sec:discussion` |
| 266 | `sec:conclusion` |

Seven unlabelled subsections: lines 102, 106, 110, 118, 213, 229, 233.

**What `\thesubsection` renders.** Only `\thesection` is renamed (line 50); `\thesubsection` is untouched. `article`'s default is `\thesection.\arabic{subsection}`, which inherits the redefinition, so it renders **`III.1`, `III.2`, `III.3`, `III.4`** for the Method subsections and **`IV.1`, `IV.2`, `IV.3`** for Results — dot-arabic, not IEEEtran's `III-A` / `IV-B` letters.

Nothing breaks, because no `\ref` targets a subsection. But the source comments still use the old style: line 134 "Cited in III-D", line 220 "Cited in IV-B", line 239 "Cited in IV-C". Those pointers no longer match what the document prints. If the intent stated at lines 14–17 — "every cross-reference resolves to the same string it did in the IEEEtran version" — is meant to cover subsections too, it needs `\renewcommand{\thesubsection}{\thesection-\Alph{subsection}}`, which would restore III-A…III-D and IV-A…IV-C.

## 8. Bibliography

`\begin{thebibliography}{19}` (line 303) vs **19** `\bibitem`s (lines 305–341). **Match.** The `{19}` argument only sets label width and 2 digits is correct for 19 entries.

**`nerc` in `notes/prior-art.md`: no entry.** `grep -ni 'nerc\|TPL-001'` returns zero hits across the file. It also has no field map or claims-table row.

`notes/citation_support.json` contains all 19 keys, and **every one of them is UNFILLED** — each entry is `{"cited_work": null, "claim": null, "verified_how": null, "venue_status": null, "source_of_number": null}` with the note "UNFILLED. Every field must be completed by the author from local extraction notes." Zero filled entries.

Cross-checking the 19 bibkeys against `prior-art.md` by name: only `alcantara2026` (1 hit), `angelopoulos2024` (1), and `pandapower` (3) appear. `prior-art.md` §7 does carry verified spot-checks for `alcantara2026`, `christianson25a`, ANSI C84.1 Range B, and `angelopoulos2024` under descriptive headings rather than bibkeys, so the verification exists for those four even where the key string does not. Nothing covers `nerc`, and the source comment at lines 299–300 admits it: *"NERC (nerc) confirmed against nerc.com as TPL-001-5.1, effective 2023-07-01 — ADD THE VERIFICATION DATE HERE, every other entry has one."* `nerc` is the first citation in the Introduction (line 82), supporting the paper's framing claim about the N-1 criterion.

---

### The three that matter most

1. **The headline is not supported at one sigma.** histgb @0.97 is 0.83±0.24; the "sub-1%" claim at lines 72, 209, 215, 250 crosses 1% on its own error bar, and ridge @0.94 lands exactly on it. Moving to the robust targets (ridge 0.95, histgb 0.98) costs the "64%" and "roughly 1.6" in the abstract.
2. **The provenance sentence at line 287 is false as written.** The cited URL is `upstream`, 10 commits behind; the STS manuscript, the parquets, and the entire case30 result postdate it, and `notes/` is `.gitignore`d off both remotes.
3. **Figure 1 is the M1 figure in an M2 paper**, contradicting line 116 four lines below it. E1 documents this and the fix is a one-word path change to `v3`, with the correction disclosed rather than made silently.
### AGENT 3 of 4 — a4-consistency — VERBATIM

All checks complete. Findings below.

---

## PAIR 1 — IV-B title vs. the three result sets

**A:** "The faster model is not the safer one" [`report/paper_current_STS.tex:229`] + "the linear model misses 0.14% ... the gradient-boosted 1.36% ... The linear model also demonstrates the lower missed rate across all targets in the sweep." [`:231`]

**B (case118):** ridge missed < histgb missed at every target 0.90–0.98, gap ≫ larger σ. At 0.90: ridge 2.963±0.439%, histgb 4.717±0.977%, gap +1.754 vs σ 0.977. At 0.96: 0.142±0.072 vs 1.357±0.198. [`data/tradeoff_curve_v2.json`]
→ **NOT A CONFLICT.** Claim A is *confirmed* on case118. (Only 0.70–0.72 and 0.99 fall inside one σ, all outside the manuscript's 0.90–0.98 sweep.)

**B (case30-published):** at 0.90 ridge 1.493±0.527%, histgb 1.466±0.195% — gap **−0.027** against larger σ 0.527. Ordering is *absent within one sigma*, and the nominal sign is reversed. histgb is simultaneously faster (14.52× vs 3.66×). Ridge only becomes safer beyond one σ at targets ≥0.94. [`data/case30_tradeoff_curve.json`, aggregated over the 5 seed records]
→ **CONTRADICTION** with "the faster model is not the safer one" as an unqualified title, at the operating point the abstract features. At 0.90 on case30-published the faster model is, if anything, the safer one, and the manuscript states no network restriction on IV-B.

**B (case30-thermal):** ordering fully **inverts** and is significant at every target 0.90–0.97. At 0.90: ridge 6.087±0.423%, histgb 2.226±0.349%, gap −3.862 vs σ 0.423; histgb also 38.63× vs 8.45×. Sub-1% crossing: histgb 0.96, ridge 0.98. Only at 0.98 does it collapse into one σ (0.515±0.207 vs 0.482±0.178). [`data/case30_thermal/case30_thermal_frozen.json`]
→ **CONTRADICTION.** On this set the faster model is the safer one at every target the paper sweeps, by a margin up to 9σ.

`notes/writing-numbers.md` already records this reversal as "Reported, not resolved" and states the barrier-height reading that resolves it is not settled by artifacts in this repo.

---

## PAIR 2 — every case30 number in the manuscript

Every case30 figure currently in the manuscript corresponds to **case30-published** (`data/case30_dataset.parquet`). Values under the other set:

| manuscript text | line | current value | set it belongs to | value under case30-thermal |
|---|---|---|---|---|
| "20.0% of contingencies are near the limit" | :72, :260 | 20.0% | published (`boundary_mass_pct` 20.0146) | **7.09%** (`boundary_mass_pct` 7.0862) |
| "another 28.8% fall below it" | :260 | 28.8% | published (`violation_rate_pct` 28.8081) | **15.40%** |
| "8.96±0.91% escalation" | :72, :260 | histgb @ target 0.93 | published | **4.86±0.98%** (histgb @ 0.96) |
| "11.27±1.02 times the solver's speed" | :72, :260 | histgb @ 0.93 | published | **21.46±4.51×** (histgb @ 0.96) |
| "41 rather than 186 branches ... 61,500 contingency scenarios, all solved successfully" | :104 | 41 / 61,500 / 0 failures | true of **both** sets | unchanged (61,500 rows, 0 failures) |
| "simulated using the same configuration" | :260 | true (mult 1.0–1.12, seed 100) | published | **false** — thermal build uses range [0.87, 0.99] (`data/case30_thermal/h3_build_stats.json` `range`) |

I verified the ±σ myself from the per-seed records: published histgb@0.93 = esc 8.96±0.91, speedup 11.27±1.02, missed 0.981±0.143; thermal histgb@0.96 = esc 4.86±0.98, speedup 21.46±4.51, missed 0.909±0.220.

**Verdict: RECONCILABLE but undeclared.** The manuscript never names which case30 dataset it uses, and `notes/writing-numbers.md` states explicitly that "a row that says only 'case30' is ambiguous and must not be used." Nothing in the manuscript distinguishes them.

---

## PAIR 3 — exchangeability / N-2 scoping vs. generator-outage prevalence

**A:** "As long as the test cases and calibration cases come from the same type of condition (a single-element outage), the true voltage remains at or above the lower bound..." [`:116`]; "Each accepted base case was put through a simulation of 186 contingencies representing single-element failures" [`:104`]; "Our claims of safety are only true for N-1 contingency cases, since we did not test N-2 cases" [`:262`].

**B:** The generator is dropped with probability 0.30 per scenario before the branch outage. **374 / 1,500 base cases (24.93%)** and **69,532 / 278,955 converged N-1 rows (24.93%)** have a non-slack generator out of service *in addition* to the outaged branch. `data/sampling_audit.json` states verbatim: *"A row with gen_out >= 0 has a generator out of service IN ADDITION to the outaged branch, so it is a two-element state."* I reproduced 0.24926 directly from `data/dataset.parquet`.

**Why they cannot both hold:** a quarter of the tested rows are two-element states, so "we did not test N-2 cases" is false as written, and "the same type of condition (a single-element outage)" does not describe the pool. The two strata are also not identically distributed — violation rate 18.24% with a generator out vs 17.22% without, boundary strip 58.10% vs 56.45%.

**Verdict: CONTRADICTION** for :104 and :262 as literal statements. **RECONCILABLE** for :116 specifically: exchangeability is not broken, because calibration and test rows are drawn from the same mixed pool — the defect is the description of what that pool contains, not the guarantee.

**Related, same paragraph:** ":92 'The N-0 condition represents the current state of the grid without any equipment outages'" is contradicted by the same 24.93% — the N-0 base state itself has a generator out in 374 of 1,500 cases.

**Also at :104 (arithmetic):** "280,500 rows ... 278,955 of these solved successfully, with the remainder failing to converge." The remainder is 1,545, but only **45** rows failed to converge; the other 1,500 are the N-0 base rows, which all converged. Confirmed from the parquet (279,000 N-1 attempted, 45 failed, 1,500 base) and by `notes/writing-numbers.md` §Non-convergence. **CONTRADICTION** (34× overstatement of solver failures).

---

## PAIR 4 — "the only active constraint is the lower voltage limit"

**A:** "In this study, we do not check for thermal line loading or over-voltage, so the only active constraint is the lower voltage limit." [`:92`]; restated at `:262`.

**B (over-voltage, case118):** `data/thermal_check.json` → `networks.case118.overvoltage`: **73.4%** of N-0 base cases and **73.1%** of N-1 rows have max bus voltage above 1.05 pu; 5.7% above 1.06; max 1.153 pu.

**B (thermal, case30-published):** `networks.case30.rating_audit.line_verdict` = **"RATED (rating appears meaningful)"**, base-case max loading **111.83%**, and the full 61,500-contingency sweep gives `share_above_100` = **0.9989** with max **217.5%**.

**Why they cannot both hold:** not checking a constraint does not make it inactive. On case118, over-voltage is violated in three quarters of the states the paper calls N-0-feasible — and `:92` separately asserts N-0 states have "all voltages within safe limits," which the same artifact refutes. On case30, the network has real ratings and 99.9% of the contingencies the case30 headline is computed over are thermally infeasible.

**Verdict: CONTRADICTION.** The scoping half ("we do not check X") is honest; the inference half ("so X is not active") is refuted by the artifact for both constraints and both networks. Note case118 thermal specifically is **not** a contradiction — ratings there are uniform 9,900 MVA placeholders, so the quantity is UNDEFINED, not zero (`placeholder_rule`, `thermal_sweep.skipped`), and `notes/writing-numbers.md` lists "case118 thermal violation rate" under CANNOT BE COMPUTED.

---

## PAIR 5 — Acknowledgments URL

**A:** "All reported numbers were generated using the authors' committed and tested code that is available at the following link: `https://github.com/rajsaha-blip/contingency-screener-research`" [`:287`]

**B:** That URL is remote `upstream`. It is public (GitHub API `"private": false`, HTTP 200) and reachable, but its HEAD is **990c3c5**, ten commits behind local HEAD 03e1136. Absent from that tree:

- `data/dataset.parquet` and `data/case30_dataset.parquet` — **both datasets every reported number is computed from**
- `data/bases_clearing_0p95.json` (the "86 of 1,500 bases" number at `:260`)
- `data/thermal_check.json`, `data/sampling_audit.json`
- the entire `notes/` directory
- `data/case30_thermal/` (whole set)
- **every manuscript file** — no `paper_current.tex`, no `report/paper_current_STS.tex`
- `CLAUDE.md`

The current work is on remote `origin` = `github.com/RS499/...`, which is at 03e1136 — a **different URL from the one printed in the paper**.

**Verdict: CONTRADICTION.** A reader following the cited link cannot regenerate a single reported number: the input data are not there. Present-tense "is available at" is false for the artifacts the sentence claims.

Two adjacent items flagged in the file's own TODO at `:283`, checked:
- **"roughly 1.5%" escalation at L=0.95** — supported: `data/escalation_at_095.json` gives ridge 1.385±0.326%, histgb 1.578±1.190%. Artifact absent from the cited remote.
- **"around 14%" bin share** (`:235`) — `notes/writing-numbers.md` lists this as **NO SOURCE**, no artifact anywhere in `data/`. I recomputed it from `data/dataset.parquet`: the max 0.001-pu bin is [0.940, 0.941) at **14.063%**. The number is correct and reproducible, but was not produced by any committed script or stored artifact, so the sentence "all reported numbers were generated using the authors' committed and tested code" does not hold for it. **CONTRADICTION**, narrow.

---

## PAIR 6 — `notes/erratum.md` vs. current repository state

Entry E1, claim by claim:

| erratum claim | line | status |
|---|---|---|
| "`paper_current.tex:112` ... embeds `data/gate_schematic_v2.png`" | :10 | **STALE PATH.** `paper_current.tex` does not exist; the file is now `paper_current_URTC_20260808.tex`, whose line 112 does embed v2. Substance holds, path does not resolve. |
| "`README.md:6` ... embeds v2" | :10 | **HOLDS** (`README.md:6`) |
| "`data/poster/gate_schematic.png` byte-identical to v2, md5 `5b8e53a2...`" | :11 | **HOLDS** — both md5 `5b8e53a285a1c739edef92c23db760d8` |
| M1 `q_hat = 0.002557` from `tradeoff_curve.json` | :15 | **HOLDS** (0.002557109746803765, histgb@0.90) |
| M2 `q_hat = 0.002291` from `tradeoff_curve_v2.json` | :16 | **HOLDS** (0.002290702766310826) |
| v3 md5 `5ceefccf43d5441191e9e41835924af2` | :36 | **HOLDS** |
| "Nothing in the repository currently references v3" | :39 | **HOLDS** — grep over `*.tex/*.md/*.py/*.json` returns zero hits |
| "There is no `urtc-submission` tag ... `git tag -l` is empty locally" | :46–48 | **REFUTED.** `git tag -l` → `urtc-submission`, created 2026-08-18 22:36, pointing at 8cefaa7 "Add the URTC-submitted manuscript as a dated artifact (submitted 2026-08-08, CMT #74)". |
| "`git ls-remote --tags origin` ... returns zero tags" | :46 | **REFUTED** — origin now carries `refs/tags/urtc-submission` |
| "`git ls-remote --tags upstream` returns zero tags" | :46 | **STILL HOLDS** — upstream has no tags |
| "The claim rests on `paper_current.tex:112`, not on a tagged commit" | :48–50 | **SUPERSEDED** by the tag above |
| "`paper_current.tex`, `data/poster/`, `data/gate_schematic_v3.png` all remain uncommitted" | :53–54 | **REFUTED** — all three are tracked (`git ls-files` resolves `data/gate_schematic_v3.png`, `data/poster/gate_schematic.png`, `paper_current_URTC_20260808.tex`) |

**Not covered by the erratum at all:** `report/paper_current_STS.tex:138` embeds `data/gate_schematic_v2.png` — the STS manuscript carries the same M1-band defect. E1's disposition ("state the correction in the camera-ready") is scoped to the URTC submission and says nothing about a second manuscript reproducing the defect.

**Verdict: CONTRADICTION** for the four tag/uncommitted claims (the repository moved past them); **RECONCILABLE** for the `paper_current.tex` path (rename); the technical core of E1 holds.

---

## PAIR 7 — case118 headline vs. case30 headline model family

**A (case118):** abstract `:72` — "the gradient-boosted model is 3.29 times faster ... misses 4.72%. Reaching a sub-1% missed rate results in a 64% escalation and speedup dropping to roughly 1.6."
**B (case30):** same paragraph — "a sub-1% missed rate results in 8.96±0.91% escalation at 11.27±1.02 times the solver's speed."

The case30 figure is unambiguously **histgb @ 0.93**. The case118 "64% / roughly 1.6" is **ambiguous between families** and the abstract never says which:

- histgb @ 0.97: esc 63.7±5.1, speedup 1.58, missed 0.83
- ridge @ 0.94: esc 64.3±2.8, speedup 1.56, missed 0.79

Both round to "64%" and "roughly 1.6". The two readings differ materially for the cross-network comparison the sentence is making: if histgb throughout, the comparison is 63.7% → 8.96% within one family; if ridge on case118, the paper compares ridge's case118 crossing against histgb's case30 crossing, and the matching ridge case30 number is **34.48% escalation at 2.98×**, not 8.96%/11.27×.

The same ambiguity recurs at `:260` ("the same missed rate gives 8.96±0.91% escalations") and `:268` ("escalating around two-thirds of cases"). `:215` and `:250` do name both families and both targets, so the body is explicit where the abstract and Discussion are not.

**Verdict: RECONCILABLE, but the family is never stated at the point of comparison.** No two claims are strictly incompatible; the defect is that the headline cross-network comparison is only valid under one of two readings the text does not disambiguate.

---

Files: `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex`, `/Users/rajansaha/contingency-screener-research/notes/erratum.md`, `/Users/rajansaha/contingency-screener-research/data/tradeoff_curve_v2.json`, `/Users/rajansaha/contingency-screener-research/data/case30_tradeoff_curve.json`, `/Users/rajansaha/contingency-screener-research/data/case30_frozen.json`, `/Users/rajansaha/contingency-screener-research/data/case30_thermal/case30_thermal_frozen.json`, `/Users/rajansaha/contingency-screener-research/data/thermal_check.json`, `/Users/rajansaha/contingency-screener-research/data/sampling_audit.json`, `/Users/rajansaha/contingency-screener-research/data/escalation_at_095.json`, `/Users/rajansaha/contingency-screener-research/data/bases_clearing_0p95.json`.
### AGENT 4 of 4 — a4-register — VERBATIM

## Part A — Register review: `/Users/rajansaha/contingency-screener-research/report/paper_current_STS.tex` (344 lines)

Reference artifacts read: `notes/writing-numbers.md`, `data/frozen_poster_numbers_v2.json`, `data/miss_depth_pool.json`, `data/solve_time.json`, `data/bases_clearing_0p95.json`, `data/barrier_height.json`. URTC baseline extracted read-only via `git show urtc-submission:paper_current_URTC_20260808.tex`. No writes, no git writes. The three forbidden files were not opened (and `notes/writing-numbers.md` itself records both as absent from the repo).

---

### 1. Contractions — 2, both in body prose

| Line | Section | Quote |
|---|---|---|
| 86 | I Introduction | "to determine whether **there's** a present risk or not" |
| 94 | II Background | "which equipment is subject to the most danger when **there's** an equipment failure" |

Nothing else. No `don't/isn't/can't/it's` anywhere in the file, including captions and the abstract.

---

### 2. Hedged numeric claims

**2a. Under-hedged — claim stronger than the artifact supports**

| Line | Quote | Artifact value | Problem |
|---|---|---|---|
| 72 (Abstract) | "the gradient-boosted model is **3.29 times faster** than the solver but misses **4.72\%** of violations" | Table I / `tradeoff_curve_v2`: 3.29±0.30, 4.72±0.98 | Both stds dropped. 4.72±0.98 spans 3.7–5.7%; the abstract reports a point value |
| 72 | "Reaching a sub-1\% missed rate results in a **64\%** escalation and speedup dropping to roughly 1.6" | ridge@0.94: 64.3±2.8, 1.56±0.07 | std dropped; the sentence also silently picks ridge without saying so, while the preceding sentence is about histgb (whose sub-1% point is 0.97 / 63.7±5.1 / 1.58±0.12) |
| 72 | "a sub-1\% missed rate results in **8.96±0.91\%** escalation at **11.27±1.02** times" | `case30_frozen.json` `crossings.histgb`: 0.089593, 11.2653 — values MATCH | The *crossing location* (0.93) is a stored scalar with no std. `writing-numbers.md` warns crossings sit within a whisker of the 1% threshold and "Do not quote a crossing target as resolved" |
| 112 | "converts the residuals … into **a coverage guarantee (the number of cases the band is guaranteed to contain)**" | — | Marginal coverage is not a per-case guarantee. Line 258 of the same file says the opposite ("measured averages rather than guarantees on individual contingencies") |
| 147 | "Both models **ensure** that the band is calibrated, as the coverage is close to 90\%" | 89.3±1.3, 89.8±1.0 | "ensure" asserts a guarantee for an empirical mean; ridge's 89.3 is 0.7 pt below target |
| 231 | "**74\%** of misses fall within one band width of the limit for the linear model and **55\%** for the gradient-boosted model" | `miss_depth_pool.json`: ridge `share_below_qhat` 0.7368, `share_left_of_mean_line` 0.7451; histgb `share_below_qhat` 0.5490, `share_left_of_mean_line` 0.5442 | **The two numbers come from different estimators.** 74 matches ridge's `share_left_of_mean_line` (74.5), 55 matches histgb's `share_below_qhat` (54.9). Under one estimator the pair is 73.7/54.9; under the other 74.5/54.4. Neither yields "74 and 55" |
| 235 | "no 0.001-per-unit width bin makes up more than **around 14\%** of the entire dataset" | **NO SOURCE.** `writing-numbers.md` names this exact line: "no artifact located anywhere in `data/`" | No artifact at all. The file's own comment at line 282 flags it for verification |
| 235 | "bus 76 … holding the minimum voltage in **27.1\%** of contingencies, whereas bus 53 is second with **16.81\%**, followed by bus 107 with **9.31\%**" | No row in `writing-numbers.md` | Unsourced; also mixes 1-dp and 2-dp precision across a single list |
| 248 | "the remaining **82.52\%** of cases, or the saturation point" | `frozen_poster_numbers_v2.json` `perfect_model_floor_saturation` = 0.826352 (82.64%) | 82.52 is `100 − 17.48`; the artifact's own saturation scalar is 82.64. Two different numbers presented as one |
| 250 | "the model escalates 99.5\% of cases and is **barely faster** than the solver" | Table I speedup 1.00±0.00 | 1.00±0.00 is *not faster*. "barely faster" claims more than the artifact |
| 260 | "**The floor exists on any network**, but its height depends on the data distribution" | — | Network-general claim from two networks. Directly against `CLAUDE.md` §8 |
| 260 | "on the IEEE 30-bus network … **20.0\%** … whereas another **28.8\%** fall below" | `case30_frozen.json` 0.200146 / 0.288081 — MATCH | But this is the **case30-published** set, which `writing-numbers.md` records as **not thermally feasible** (99.89% of N-1 above 100% loading, full 61,500 sweep). The manuscript says only "IEEE 30-bus system" — the file's own rule is "a row that says only case30 is ambiguous and must not be used" |
| 260 | "Only **86** of the 1,500 base cases are above 0.95 pu" | `bases_clearing_0p95.json`: `gt_0p95` = 86 under `canonical_v2`; the `clip_era` block gives **44** | Value is right for the canonical era, but the artifact holds two, and the manuscript names neither |
| 262 | "**mathematical proof is unable to determine** the safety of N-2 outages" | — | Overstates: exchangeability fails so *this* guarantee doesn't transfer; that is not "proof is unable" |
| 262 | "the worst case, at 0.0915 per unit, **is an example of a sudden collapse where a generator … hits its reactive limit**" | 2F caveat in `writing-numbers.md`: deep-miss pools overlap across seeds and the baseline-vs-deep-miss comparison (20.799 vs 21.328 off-setpoint gens) is "**unevaluable under the project's std rule**" | Mechanism asserted from an n=1 case whose supporting comparison the artifacts declare unevaluable |
| 268 | "the speedup on this network **decreases enough to be comparable to the speed of the solver itself**" | 1.56±0.07 (ridge@0.94), 1.58±0.12 (histgb@0.97) | 1.56–1.58× is not "comparable to the solver"; persistence at 1.00±0.00 is |

Also unsourced against `writing-numbers.md`, though plausibly in other artifacts: line 104 "**53.82\%** of the cases passing", "voltages ranged from **0.7179 to 0.9603**"; line 260 "escalation of roughly **1.5\%**" at L=0.95. The manuscript's own comment block (lines 279–283) already flags the 14% bin share, the 1.5% figure and `bases_clearing_0p95.json` as unverified. Line 248's ceilings **74.9\% versus 82.8\%** do check out (`frozen_poster_numbers_v2.json`: 0.7488763, 0.8279477).

**2b. Over-hedged — vague qualifier on an exactly-known quantity**

| Line | Quote | Exact artifact value |
|---|---|---|
| 72 | "speedup dropping to **roughly 1.6**" | 1.56±0.07 |
| 92 | "voltage within a band **around** nominal" | (definitional, acceptable) |
| 94 | "it takes **up to several milliseconds** for one scenario" | `solve_time.json`: min 9.14 ms, mean 9.561, median 9.512, std 0.256 over 400 solves — the paper states 9.14 exactly at line 131 |
| 231 | "**Only a few** misses were serious" | Pool counts: 1,436 ridge / 2,284 histgb misses; p99 depth 0.0350 / 0.0460; `qlimit_class.json` 58 and 106 deep misses |
| 235 | "results in **a large amount of** escalations" | 30.6±2.5% (histgb), 49.1±2.7% (ridge) |
| 235 | "no bin makes up more than **around 14\%**" | (no artifact — over-hedge *and* unsourced) |
| 248 | "flags violations **about as often** as they occur, so its ceiling **essentially** lands on the saturation point" | flag ceiling histgb = **1.009272** count-pooled / 1.009 seed-mean. This is known to four decimals |
| 248 | "A model that **rarely** predicts below the limit" | ridge flag ceiling 0.691482 |
| 250 | "accept **about a 1.6 times** speedup instead of the **2 to 3 times** available at 0.90" | 1.56±0.07 / 1.58±0.12; 2.04±0.11 and 3.29±0.30 |
| 260 | "escalation of **roughly 1.5\%**" | unverified scalar, presented with a hedge |
| 260 | "the method flags **almost all** instances as unsafe" | An escalation of 1.5% does not by itself give a flag share; no artifact for the flag share at L=0.95 |
| 268 | "escalating **around two-thirds** of cases" | 64.3±2.8 (ridge@0.94) / 63.7±5.1 (histgb@0.97) |

---

### 3. Voice

No `I`, `my`, `me` in prose (the three grep hits at lines 19, 23, 150 are "Table I" inside LaTeX comments).

**Family A — first-person plural (`we` / `our` / `us`), 38 occurrences across every body section:**

- Abstract: L72 (`we attach`)
- I Introduction: L84 (`We keep track`), L86 (`our study uses`, `Our work stands out`, `we add`, `we specifically check`, `we explain`)
- II Background: L92 (`We refer`, `we do not check`), L96 (`We study`, `our N-1 test set`, `We use`)
- III Method: L104 (`We determined`, `We also tested`), L108 (`we split`, `We never look`, `we keep`, `we repeat`, `We test`, `our models`), L112 (`we compute`)
- IV Results: L215 (`we adjusted`), L231 (`we consider`, `we notice`)
- V Discussion: L256 (`our study`, `we fall back`, `we also explain`), L258 (`Our approach`, `our gate`, `allows us`), L260 (`We use 0.94 pu`), L262 (`Our claims`, `we did not test`, `we only checked`, `we are unsure`)
- VI Conclusion: L268 (`Our models`, `Our contribution`)

**Family B — third person (`the authors`), 2 occurrences, Acknowledgments only:**

- L287: "**The authors** would like to thank the program…" and "generated using the **authors'** committed and tested code"

**Two distinct voice families**, cleanly split: first-person plural in Abstract through Conclusion, third person confined to Acknowledgments. The split is a convention break rather than a drift, but see §6 — the plural is now factually wrong.

---

### 4. Overclaiming vocabulary

| Line | Word | Quote |
|---|---|---|
| 86 | *completely* | "an input-convex network that **completely** removes false negatives" — attributed to Christianson et al. and immediately qualified ("only relevant to DC power flow models"); acceptable as reported speech |
| 86 | *ensure* | "runs randomized full solves … to **ensure** the model is accurate" — describing Manoharan's method |
| 86 | *must* | "we explain why there **must be** a certain floor for escalation" — asserts necessity; the evidence is distributional on two networks |
| 96 | *ensuring* | "while **ensuring** specific generator reactive power limits are enforced" — factual (`enforce_q_lims=True`), not an overclaim |
| 112 | *guarantee / guaranteed* | "converts the residuals … into a coverage **guarantee** (the number of cases the band is **guaranteed** to contain)" — **the strongest overclaim in the file**; contradicted by L258 |
| 116 | *guarantee* | "there is no **guarantee** for what the band truly encompasses" — negation, fine |
| **147** | *ensure* | "Both models **ensure** that the band is calibrated" — asserts a guarantee for an empirical 89.3/89.8 |
| 156 | *never* | "The train-mean model **never** calls the solver" — true by construction |
| 231 | *cannot* | "accuracy **cannot** settle this decision by itself" — argumentative, defensible |
| **248** | *every case* | "escalation moves closer to **every case** predicted at or above the limit" |
| 250 | *never / cannot / never* | "its predictions **never** go below the limit … since it **cannot** predict under the limit, it can **never** mark a case as a violation" — true by construction for persistence |
| 256 | *First* | enumerative, not a novelty claim |
| 258 | *guarantees* | "measured averages rather than **guarantees** on individual contingencies" — the correct statement; note it directly contradicts L112 |
| **260** | *any network* | "The floor exists on **any network**, but its height depends on the data distribution" — network-general claim from n=2 networks |
| 262 | *proof / unable / cannot* | "mathematical **proof is unable** to determine the safety of N-2 outages"; "A model trained only on pre-outage features **cannot** predict such a situation" |
| **268** | *every case* | "a note of caution to anyone expecting large speedups from a surrogate that must be safe on **every case**" |

**"first" is never used as a novelty claim.** All five instances (L86, 209, 215, 256, 262) are enumerative ("First, unlike…") or temporal ("first falls below 1\%", "in the first place"). **"novel" does not appear anywhere in the file.** Neither does "always".

---

### 5. Quantitative words near a table or figure reference

| Line | Word(s) | Reference within two sentences | Does the referenced float carry the value? |
|---|---|---|---|
| 147 | "how **much** error" | Table~\ref{tab:models} | Rhetorical, no number claimed — no issue |
| 225 (Fig. 3 caption) | "**Most** misses stay within one band" | Fig. 3 itself | **NO.** The figure is a log-count histogram; the shares (74%/55%) live only in L231 prose. "Most" is true for ridge (74) and only marginally for histgb (55) — one word covering both is the weakest claim in the caption set |
| 231 | "**far more** accurate" | Table~\ref{tab:models} | **YES.** MAE 1.6±0.1 vs 3.8±0.1, R² 0.92 vs 0.77 — gaps exceed both stds |
| 231 | "**Only a few** misses were serious" | Fig.~\ref{fig:missdepth} | **NO.** Fig. 3 shows the tail but no count; artifact counts (1,436/2,284 misses; 58/106 deep) are not in any float |
| 235 | "**The majority** of contingencies are within 0.005 pu" | Fig.~\ref{fig:boundary} | **YES**, via the 56.86% stated in the same paragraph (`boundary mass` 0.568629) |
| 235 | "results in a **large amount** of escalations" | Fig.~\ref{fig:boundary} | **NO.** Escalation appears in Tables I and II, not Fig. 4 |
| 235 | "**slightly** higher than the threshold" | Fig.~\ref{fig:boundary} | **YES** — the [0.94, 0.945) strip is stated |
| 235 | "**Notably**, no bin … more than **around 14\%**" | Fig.~\ref{fig:boundary} | **NO.** No artifact anywhere; `writing-numbers.md` names this line as NO SOURCE |
| 235 | "**around** 14\%" / bus shares 27.1 / 16.81 / 9.31 | Fig.~\ref{fig:boundary} | **NO.** Fig. 4 is a voltage histogram; per-bus shares appear in no float |
| 244 (Fig. 4 caption) | "**Over half** are within 0.005 pu above the limit" | Fig. 4 | **YES** — 56.86% |
| 244 | "the tail below the limit drops **much lower**" | Fig. 4 | Visually yes; the numeric anchor (min 0.7179) is at L104, not in the float |
| 248 | "so **much** of the distribution sits just above 0.94" | Fig. 4 (prior paragraph) | **YES** — 56.86% |
| 248 | "flags violations **about as often** as they occur … ceiling **essentially** lands on the saturation point" | Tables I/II (prior page) | **NO.** Flag ceiling 1.009272 appears in no table; the reader cannot check "essentially" |
| 248 | "A model that **rarely** predicts below the limit" | — | **NO** artifact in any float |
| 250 | "**barely** faster than the solver" | Table~\ref{tab:models} | Table gives 1.00±0.00 — which contradicts "faster" rather than supporting "barely faster" |
| 250 | "accept **about** a 1.6 times speedup instead of the 2 to 3 times" | Table~\ref{tab:models} | 2.04 and 3.29 are in Table I; **1.56/1.58 are in Table II, not Table I** — the sentence cites only Table I |

---

### 6. Comparison against `urtc-submission:paper_current_URTC_20260808.tex`

Method: stripped full-line comments from both, compared paragraph-level prose line by line, then compared full token-frequency tables of all non-comment content.

**No hedging word was removed.** Not one. Every hedge listed in §2b and every overclaim listed in §4 is present verbatim in the URTC submission.

**Exactly one prose paragraph differs, and only in a cross-reference macro** (line 116):

- URTC: "…which raises the issue of distribution shift described in **Section~V**."
- STS: "…which raises the issue of distribution shift described in **Section~\ref{sec:discussion}**."

Every other body paragraph — abstract, all six sections, all four captions, the acknowledgments — is byte-identical apart from one trailing space stripped at the end of the acknowledgments (L287). The remaining diffs are formatting only: `IEEEtran`→`article`, `\captionof{figure}`→`\caption`, `\centerline{\includegraphics[width=\columnwidth]}`→`\includegraphics[width=0.5–0.8\textwidth]`, `\hline`→booktabs, the combined float split into three, and `\label{sec:*}` anchors added.

**One substantive non-prose change the register review should surface:** the author block. URTC carries **two** authors —

```
\IEEEauthorblockN{Rajan Saha} … \IEEEauthorblockN{Eugene Pinsky}
\textit{Boston University} … epinsky@bu.edu
```

The STS version is single-author (`\author{Rajan Saha\\ Conestoga High School…}`), with Eugene Pinsky and the BU Department of Computer Science affiliation removed. The acknowledgments text at L287 was **not** updated to match and still reads "**The authors** would like to thank…" and "the **authors'** committed and tested code." Under a single-author STS byline that plural is now factually wrong, and it is the entire basis of voice family B in §3.

---

### Highest-priority items

1. **L112 "guarantee … guaranteed to contain"** — flatly contradicted by L258 within the same manuscript.
2. **L235 "around 14\%"** — `writing-numbers.md` names this line as having no artifact anywhere in `data/`.
3. **L260 "The floor exists on any network"** — network-general claim from two networks.
4. **L231's 74/55 pair** — drawn from two different estimators in `miss_depth_pool.json`.
5. **L287 "The authors" (plural)** against a single-author byline, unchanged from the two-author URTC version.
6. **L260's "IEEE 30-bus"** does not say which case30 set; the values are from the thermally infeasible published set.

No sentence was rewritten.
## S9 — 2C stratum quantities

### S9 ROUND 1 — Agent A (derived artifact) — VERBATIM

All from `/Users/rajansaha/contingency-screener-research/data/drift_n0_stratum_long.parquet`, sha256(16) = `97c8ef7aa40c4e97` (manifest `content_sha256` matches file). Aggregation "per-seed then mean/std(ddof=0)" throughout; no recompute from `dataset.parquet`.

| quantity | value | file | column/filter | aggregation | sha256(16) |
|---|---|---|---|---|---|
| row count | 1200 | drift_n0_stratum_long.parquet | all | count | 97c8ef7aa40c4e97 |
| distinct model | ridge, histgb (2) | " | model | unique | 97c8ef7aa40c4e97 |
| distinct cal_stratum | benign, marginal (2) | " | cal_stratum | unique | 97c8ef7aa40c4e97 |
| distinct test_stratum | benign, marginal (2) | " | test_stratum | unique | 97c8ef7aa40c4e97 |
| distinct seed | 0,1,2,3,4 (5) | " | seed | unique | 97c8ef7aa40c4e97 |
| distinct coverage_target | 30 (0.70…0.99 step 0.01) | " | coverage_target | unique | 97c8ef7aa40c4e97 |
| grid check | 2×2×2×5×30 = 1200 | " | — | product | 97c8ef7aa40c4e97 |
| test tag | 2C_n0_stratum (1 value) | " | test | unique | 97c8ef7aa40c4e97 |
| median_n0_min_vm distinct count | 1 | " | median_n0_min_vm | unique | 97c8ef7aa40c4e97 |
| median_n0_min_vm value | 0.9433575252264039 | " | median_n0_min_vm | constant | 97c8ef7aa40c4e97 |
| realized_shift benign→benign per seed | 0:-0.0004931558153089544; 1:0.00044589722316035196; 2:-4.175646759363438e-05; 3:3.1783273622298935e-05; 4:-0.00022486551933931231 | " | realized_shift_mean_n0_min_vm, cal=benign,test=benign | 1 value/seed | 97c8ef7aa40c4e97 |
| realized_shift benign→benign mean | -5.6419461091850034e-05 | " | " | mean over 5 seeds | 97c8ef7aa40c4e97 |
| realized_shift benign→marginal per seed | 0:-0.005084679348747789; 1:-0.004692811882023973; 2:-0.0048278421961810425; 3:-0.004813948001075152; 4:-0.004802438666735687 | " | cal=benign,test=marginal | 1 value/seed | 97c8ef7aa40c4e97 |
| realized_shift benign→marginal mean | -0.004844344018952729 | " | " | mean | 97c8ef7aa40c4e97 |
| realized_shift marginal→benign per seed | 0:0.004671239083787304; 1:0.005231307528557938; 2:0.00497506899802469; 3:0.004816750210760223; 4:0.004629860673348141 | " | cal=marginal,test=benign | 1 value/seed | 97c8ef7aa40c4e97 |
| realized_shift marginal→benign mean | 0.0048648452988956595 | " | " | mean | 97c8ef7aa40c4e97 |
| realized_shift marginal→marginal per seed | 0:7.971555034846922e-05; 1:9.259842337361324e-05; 2:0.00018898326943728172; 3:-2.898106393722788e-05; 4:5.2287525951766334e-05 | " | cal=marginal,test=marginal | 1 value/seed | 97c8ef7aa40c4e97 |
| realized_shift marginal→marginal mean | 7.692074103478052e-05 | " | " | mean | 97c8ef7aa40c4e97 |
| n_cal cal=benign (both test cells) per seed | 0:26409; 1:26780; 2:29758; 3:26597; 4:27898 | " | n_cal, cal_stratum=benign | 1 value/seed | 97c8ef7aa40c4e97 |
| n_cal cal=benign mean | 27488.4 | " | " | mean | 97c8ef7aa40c4e97 |
| n_cal cal=marginal (both test cells) per seed | 0:29382; 1:29010; 2:26038; 3:29198; 4:27897 | " | n_cal, cal_stratum=marginal | 1 value/seed | 97c8ef7aa40c4e97 |
| n_cal cal=marginal mean | 28305.0 | " | " | mean | 97c8ef7aa40c4e97 |
| n_test, test=benign (seeds 0–4) | 26037, 26594, 28641, 28453, 26783 | " | n_test, test_stratum=benign | per seed | 97c8ef7aa40c4e97 |
| n_true_viol, test=benign (seeds 0–4) | 3989, 4057, 4413, 4381, 4189 | " | n_true_viol, test_stratum=benign | per seed | 97c8ef7aa40c4e97 |
| n_test, test=marginal (seeds 0–4) | 29752, 29198, 27146, 27338, 29008 | " | n_test, test_stratum=marginal | per seed | 97c8ef7aa40c4e97 |
| n_true_viol, test=marginal (seeds 0–4) | 5820, 5715, 5275, 5205, 5395 | " | n_true_viol, test_stratum=marginal | per seed | 97c8ef7aa40c4e97 |
| ridge b→b coverage_emp (seeds 0–4) | 0.8840496216922072, 0.8947130931789126, 0.9007716211026151, 0.9158612448599445, 0.8865698390770265 | " | coverage_target==0.90 | per seed | 97c8ef7aa40c4e97 |
| ridge b→b coverage_emp mean / std0 | 0.8963930839821412 / 0.011400530217031263 | " | " | mean, std ddof=0 | 97c8ef7aa40c4e97 |
| ridge b→b escalation (seeds 0–4) | 0.305795598571264, 0.3657591938031135, 0.34331901819070565, 0.3517028081397392, 0.2926483216965986 | " | " | per seed | 97c8ef7aa40c4e97 |
| ridge b→b escalation mean / std0 | 0.3318449880802842 / 0.02789662733624099 | " | " | mean, std | 97c8ef7aa40c4e97 |
| ridge b→b missed_viol (seeds 0–4) | 0.05966407620957633, 0.04707912250431353, 0.060503059143439834, 0.04268431864871034, 0.054189544043924565 | " | " | per seed | 97c8ef7aa40c4e97 |
| ridge b→b missed_viol mean / std0 | 0.052824024109992915 / 0.006977622199007145 | " | " | mean, std | 97c8ef7aa40c4e97 |
| ridge b→m coverage_emp (seeds 0–4) | 0.803609841355203, 0.8226590862387835, 0.7983128269358285, 0.7806715926549126, 0.7712355212355212 | " | " | per seed | 97c8ef7aa40c4e97 |
| ridge b→m coverage_emp mean / std0 | 0.7952977736840497 / 0.017998553298487808 | " | " | mean, std | 97c8ef7aa40c4e97 |
| ridge b→m escalation (seeds 0–4) | 0.42548400107555795, 0.47934790054113297, 0.4541737272526339, 0.40280927646499376, 0.40816326530612246 | " | " | per seed | 97c8ef7aa40c4e97 |
| ridge b→m escalation mean / std0 | 0.43399563412808817 / 0.028900974348308982 | " | " | mean, std | 97c8ef7aa40c4e97 |
| ridge b→m missed_viol (seeds 0–4) | 0.05360824742268041, 0.0537182852143482, 0.03981042654028436, 0.05148895292987512, 0.051899907321594066 | " | " | per seed | 97c8ef7aa40c4e97 |
| ridge b→m missed_viol mean / std0 | 0.050105163885756435 / 0.0052238651041763146 | " | " | mean, std | 97c8ef7aa40c4e97 |
| ridge m→b coverage_emp (seeds 0–4) | 0.9430425932327073, 0.9196435286154772, 0.9219301002059984, 0.9331529188486276, 0.9380950602994437 | " | " | per seed | 97c8ef7aa40c4e97 |
| ridge m→b coverage_emp mean / std0 | 0.9311728402404509 / 0.009067327586748887 | " | " | mean, std | 97c8ef7aa40c4e97 |
| ridge m→b escalation (seeds 0–4) | 0.5429965049736913, 0.4616454839437467, 0.4525330819454628, 0.49509717780198925, 0.5439644550647799 | " | " | per seed | 97c8ef7aa40c4e97 |
| ridge m→b escalation mean / std0 | 0.49924734074593397 / 0.038799368928741355 | " | " | mean, std | 97c8ef7aa40c4e97 |
| ridge m→b missed_viol (seeds 0–4) | 0.02531962897969416, 0.02982499383781119, 0.037389530931339225, 0.02145628851860306, 0.01742659345905944 | " | " | per seed | 97c8ef7aa40c4e97 |
| ridge m→b missed_viol mean / std0 | 0.02628340714530142 / 0.006907415046352431 | " | " | mean, std | 97c8ef7aa40c4e97 |
| ridge m→m coverage_emp (seeds 0–4) | 0.918392040871202, 0.8712240564422221, 0.8778825609666249, 0.8446850537713073, 0.9099903474903475 | " | " | per seed | 97c8ef7aa40c4e97 |
| ridge m→m coverage_emp mean / std0 | 0.8844348119083406 / 0.026846519782127615 | " | " | mean, std | 97c8ef7aa40c4e97 |
| ridge m→m escalation (seeds 0–4) | 0.6286300080666846, 0.5555859990410302, 0.5393428129374493, 0.5001097373619138, 0.5850455046883618 | " | " | per seed | 97c8ef7aa40c4e97 |
| ridge m→m escalation mean / std0 | 0.561742812419088 / 0.04325555381069406 | " | " | mean, std | 97c8ef7aa40c4e97 |
| ridge m→m missed_viol (seeds 0–4) | 0.014948453608247423, 0.02957130358705162, 0.02293838862559242, 0.025552353506243995, 0.00778498609823911 | " | " | per seed | 97c8ef7aa40c4e97 |
| ridge m→m missed_viol mean / std0 | 0.020159097085074913 / 0.00781883285004433 | " | " | mean, std | 97c8ef7aa40c4e97 |
| histgb b→b coverage_emp (seeds 0–4) | 0.8905787917194762, 0.9008798977212905, 0.8658217241018121, 0.9111868695743859, 0.8971362431393047 | " | " | per seed | 97c8ef7aa40c4e97 |
| histgb b→b coverage_emp mean / std0 | 0.8931207052512539 / 0.015194812284911343 | " | " | mean, std | 97c8ef7aa40c4e97 |
| histgb b→b escalation (seeds 0–4) | 0.025617390636402042, 0.024742423102955553, 0.02032051953493244, 0.02853829121709486, 0.04304969570249785 | " | " | per seed | 97c8ef7aa40c4e97 |
| histgb b→b escalation mean / std0 | 0.028453664038776548 / 0.0077590862568321164 | " | " | mean, std | 97c8ef7aa40c4e97 |
| histgb b→b missed_viol (seeds 0–4) | 0.08648784156430182, 0.07912250431353217, 0.08542941309766598, 0.06003195617438941, 0.10121747433755073 | " | " | per seed | 97c8ef7aa40c4e97 |
| histgb b→b missed_viol mean / std0 | 0.08245783789748802 / 0.013349455189353954 | " | " | mean, std | 97c8ef7aa40c4e97 |
| histgb b→m coverage_emp (seeds 0–4) | 0.891402258671686, 0.9055072265223646, 0.8964488322404774, 0.89417660399444, 0.8924089906232764 | " | " | per seed | 97c8ef7aa40c4e97 |
| histgb b→m coverage_emp mean / std0 | 0.8959887824104488 / 0.00505860700222826 | " | " | mean, std | 97c8ef7aa40c4e97 |
| histgb b→m escalation (seeds 0–4) | 0.46806937348749666, 0.5820261661757654, 0.46990348485964784, 0.5566610578681689, 0.6086252068394925 | " | " | per seed | 97c8ef7aa40c4e97 |
| histgb b→m escalation mean / std0 | 0.5370570578461142 / 0.05796109113738272 | " | " | mean, std | 97c8ef7aa40c4e97 |
| histgb b→m missed_viol (seeds 0–4) | 0.03178694158075601, 0.01837270341207349, 0.027298578199052133, 0.017867435158501442, 0.02761816496756256 | " | " | per seed | 97c8ef7aa40c4e97 |
| histgb b→m missed_viol mean / std0 | 0.02458876466358913 / 0.005516335637505814 | " | " | mean, std | 97c8ef7aa40c4e97 |
| histgb m→b coverage_emp (seeds 0–4) | 0.9116257633367899, 0.9093780552004211, 0.8827205753989037, 0.9200435806417601, 0.8873165814135833 | " | " | per seed | 97c8ef7aa40c4e97 |
| histgb m→b coverage_emp mean / std0 | 0.9022169111982915 / 0.014558334813608409 | " | " | mean, std | 97c8ef7aa40c4e97 |
| histgb m→b escalation (seeds 0–4) | 0.03863732380842647, 0.027562608107091824, 0.024719807269299256, 0.03855480968614909, 0.0340887876638166 | " | " | per seed | 97c8ef7aa40c4e97 |
| histgb m→b escalation mean / std0 | 0.03271266730695665 / 0.005683921372070908 | " | " | mean, std | 97c8ef7aa40c4e97 |
| histgb m→b missed_viol (seeds 0–4) | 0.07370268237653547, 0.0754251910278531, 0.0793111262179923, 0.05546678840447387, 0.10766292671281928 | " | " | per seed | 97c8ef7aa40c4e97 |
| histgb m→b missed_viol mean / std0 | 0.0783137429479348 / 0.016816410465681674 | " | " | mean, std | 97c8ef7aa40c4e97 |
| histgb m→m coverage_emp (seeds 0–4) | 0.9110311911804249, 0.9089321186382628, 0.903816400206292, 0.9084790401638745, 0.8848248758963044 | " | " | per seed | 97c8ef7aa40c4e97 |
| histgb m→m coverage_emp mean / std0 | 0.9034167252170316 / 0.00959002909673717 | " | " | mean, std | 97c8ef7aa40c4e97 |
| histgb m→m escalation (seeds 0–4) | 0.6162947028771175, 0.6115144872936502, 0.5456789213880499, 0.59730046089692, 0.5862520683949255 | " | " | per seed | 97c8ef7aa40c4e97 |
| histgb m→m escalation mean / std0 | 0.5914081281701327 / 0.025203460747037748 | " | " | mean, std | 97c8ef7aa40c4e97 |
| histgb m→m missed_viol (seeds 0–4) | 0.01993127147766323, 0.01627296587926509, 0.017440758293838864, 0.01095100864553314, 0.029657089898053754 | " | " | per seed | 97c8ef7aa40c4e97 |
| histgb m→m missed_viol mean / std0 | 0.018850618838870816 / 0.0061479015870778845 | " | " | mean, std | 97c8ef7aa40c4e97 |
| ridge 0.90 gap (a)-(b) | -0.10109531029809149; larger std 0.017998553298487808; ratio -5.617 → EXCEEDS | " | coverage_emp | mean diff vs max std | 97c8ef7aa40c4e97 |
| ridge 0.90 gap (a)-(c) | -0.08913703822429087; larger std 0.026846519782127615; ratio -3.320 → EXCEEDS | " | coverage_emp | mean diff vs max std | 97c8ef7aa40c4e97 |
| histgb 0.90 gap (a)-(b) | 0.002868077159194904; larger std 0.015194812284911343; ratio 0.189 → WITHIN NOISE | " | coverage_emp | mean diff vs max std | 97c8ef7aa40c4e97 |
| histgb 0.90 gap (a)-(c) | -0.007427942806582877; larger std 0.00959002909673717; ratio -0.775 → WITHIN NOISE | " | coverage_emp | mean diff vs max std | 97c8ef7aa40c4e97 |
| stratum violation-rate field | ABSENT (only missed_viol, n_true_viol, n_test; no stored rate) | " | column scan | — | 97c8ef7aa40c4e97 |
| manifest artifact.n_records / n_fields | null / null (actual 1200 / 20) | drift_n0_stratum_long.manifest.json | artifact | — | 97c8ef7aa40c4e97 |
| manifest model_hyperparameters | null | drift_n0_stratum_long.manifest.json | model_hyperparameters | — | 97c8ef7aa40c4e97 |

Files: `/Users/rajansaha/contingency-screener-research/data/drift_n0_stratum_long.parquet`, `/Users/rajansaha/contingency-screener-research/data/drift_n0_stratum_long.manifest.json`.
### S9 ROUND 1 — Agent B (re-derived, ANCHORED exact) — VERBATIM

**ANCHORED.** Max absolute difference between my refit and `data/tuned_metrics.json` M2 per-seed sweep at coverage 0.90 (q_hat, escalation, coverage_emp, missed_viol, 10 model-seed records): **0.0** (exact). Seed-mean also reproduces `data/tradeoff_curve_v2.json` at 0.90 exactly (diff 0.0 on all four fields, both families, and the ddof=0 stds match to full precision).

Derivation script: `/private/tmp/claude-501/-Users-rajansaha-contingency-screener-research/a20165b8-6ffa-4031-84e5-ca5fd47a15f6/scratchpad/b.py` (sha256 3e00400166e2eb54), raw output `.../scratchpad/out.json` (sha256 05a64949f65b247f).

quantity | value | source | derivation | aggregation | sha256(16)
---|---|---|---|---|---
ANCHOR ridge escalation@0.90 (5-seed mean) | 0.4906972404572077 | dataset.parquet + tuned_metrics M2 cfg | refit M2 on full train, q̂ on full cal, gate on full test | mean over 5 seeds | 8f0fd1081c8603e8
ANCHOR ridge coverage_emp@0.90 | 0.8933896003705112 | same | same | mean | 8f0fd1081c8603e8
ANCHOR ridge missed_viol@0.90 | 0.029631523339489742 | same | same | mean | 8f0fd1081c8603e8
ANCHOR histgb escalation@0.90 | 0.3062513593744674 | same | same | mean | 8f0fd1081c8603e8
ANCHOR histgb coverage_emp@0.90 | 0.8981751371681603 | same | same | mean | 8f0fd1081c8603e8
ANCHOR histgb missed_viol@0.90 | 0.04716684182384393 | same | same | mean | 8f0fd1081c8603e8
ANCHOR max abs diff vs tradeoff_curve_v2 / tuned_metrics | 0.0 | data/tradeoff_curve_v2.json, data/tuned_metrics.json | elementwise abs diff, 4 fields × 2 families (+ per-seed) | max | a40a079733ecdfcd / 360a9ec768152afe
**1. Stratum definition** | | | | |
n base scenarios | 1500 | dataset.parquet, outaged_type=="none" | row count | count | 8f0fd1081c8603e8
median n0_min_vm (base) | 0.9433575252264039 | same | np.median over 1500 base rows | median | 8f0fd1081c8603e8
n base scenarios benign (n0_min_vm >= median) | 750 | same | mask | count | 8f0fd1081c8603e8
n base scenarios marginal (< median) | 750 | same | mask | count | 8f0fd1081c8603e8
converged N-1 rows, benign | 139485 | dataset.parquet, outaged_type!="none" & converged | scenario_id join to stratum | count | 8f0fd1081c8603e8
converged N-1 rows, marginal | 139470 | same | same | count | 8f0fd1081c8603e8
converged N-1 rows, total | 278955 | same | same | count | 8f0fd1081c8603e8
**2. Violation / boundary rates** | | | | |
violation rate benign (min_vm < 0.94) | 0.15373696096354447 (21444 / 139485) | dataset.parquet | mean(min_vm<0.94) over benign converged N-1 rows | pooled rows | 8f0fd1081c8603e8
violation rate marginal | 0.19577686957768695 (27305 / 139470) | same | same, marginal rows | pooled rows | 8f0fd1081c8603e8
boundary-strip share benign [0.94,0.945) | 0.3346381331325949 (46677 / 139485) | same | mean of mask | pooled rows | 8f0fd1081c8603e8
boundary-strip share marginal [0.94,0.945) | 0.802645730264573 (111945 / 139470) | same | mean of mask | pooled rows | 8f0fd1081c8603e8
**3. Realized shift (n0_min_vm)** | | | | |
scenario-level mean, benign | 0.9464851373023853 | 750 base rows | mean | mean | 8f0fd1081c8603e8
scenario-level mean, marginal | 0.9415776341685533 | 750 base rows | mean | mean | 8f0fd1081c8603e8
scenario-level benign − marginal | 0.004907503133831925 | same | difference | — | 8f0fd1081c8603e8
N-1-row-level mean, benign | 0.9464850995814914 | 139485 rows | mean | mean | 8f0fd1081c8603e8
N-1-row-level mean, marginal | 0.9415776326216536 | 139470 rows | mean | mean | 8f0fd1081c8603e8
N-1-row-level benign − marginal | 0.004907466959837792 | same | difference | — | 8f0fd1081c8603e8
**4a. RIDGE SHIFTED (cal=benign, test=marginal)** | | | | |
coverage_emp per seed | [0.803609841355203, 0.8226590862387835, 0.7983128269358285, 0.7806715926549126, 0.7712355212355212] | b.py | q̂ on benign cal rows, gate on marginal test rows | per seed | 3e00400166e2eb54
coverage_emp mean ± std(ddof=0) | 0.7952977736840497 ± 0.017998553298487808 | b.py | — | 5 seeds | 3e00400166e2eb54
escalation per seed | [0.42548400107555795, 0.47934790054113297, 0.4541737272526339, 0.40280927646499376, 0.40816326530612246] | b.py | — | per seed | 3e00400166e2eb54
escalation mean ± std | 0.43399563412808817 ± 0.028900974348308982 | b.py | — | 5 seeds | 3e00400166e2eb54
missed_viol per seed | [0.05360824742268041, 0.0537182852143482, 0.03981042654028436, 0.05148895292987512, 0.051899907321594066] | b.py | — | per seed | 3e00400166e2eb54
missed_viol mean ± std | 0.050105163885756435 ± 0.0052238651041763146 | b.py | — | 5 seeds | 3e00400166e2eb54
q_hat per seed | [0.0038719337820996014, 0.004358059826088723, 0.004226576685081751, 0.004100426172779059, 0.00397889449840938] | b.py | conformal quantile, benign cal | per seed | 3e00400166e2eb54
q_hat mean ± std | 0.004107178192891703 ± 0.00017264983212700758 | b.py | — | 5 seeds | 3e00400166e2eb54
n_cal per seed | [26409, 26780, 29758, 26597, 27898] | b.py | benign ∩ cal split | per seed | 3e00400166e2eb54
n_test per seed | [29752, 29198, 27146, 27338, 29008] | b.py | marginal ∩ test split | per seed | 3e00400166e2eb54
**4b. RIDGE BENIGN CONTROL (cal=benign, test=benign)** | | | | |
coverage_emp per seed | [0.8840496216922072, 0.8947130931789126, 0.9007716211026151, 0.9158612448599445, 0.8865698390770265] | b.py | — | per seed | 3e00400166e2eb54
coverage_emp mean ± std | 0.8963930839821412 ± 0.011400530217031263 | b.py | — | 5 seeds | 3e00400166e2eb54
escalation mean ± std | 0.3318449880802842 ± 0.02789662733624099 | b.py | per seed [0.305795598571264, 0.3657591938031135, 0.34331901819070565, 0.3517028081397392, 0.2926483216965986] | 5 seeds | 3e00400166e2eb54
missed_viol mean ± std | 0.052824024109992915 ± 0.006977622199007145 | b.py | per seed [0.05966407620957633, 0.04707912250431353, 0.060503059143439834, 0.04268431864871034, 0.054189544043924565] | 5 seeds | 3e00400166e2eb54
q_hat mean ± std | 0.004107178192891703 ± 0.00017264983212700758 (identical to 4a; same cal set) | b.py | — | 5 seeds | 3e00400166e2eb54
n_cal / n_test per seed | [26409, 26780, 29758, 26597, 27898] / [26037, 26594, 28641, 28453, 26783] | b.py | — | per seed | 3e00400166e2eb54
**4c. RIDGE IN-DISTRIBUTION MARGINAL (cal=marginal, test=marginal)** | | | | |
coverage_emp per seed | [0.918392040871202, 0.8712240564422221, 0.8778825609666249, 0.8446850537713073, 0.9099903474903475] | b.py | q̂ on marginal cal rows | per seed | 3e00400166e2eb54
coverage_emp mean ± std | 0.8844348119083406 ± 0.026846519782127615 | b.py | — | 5 seeds | 3e00400166e2eb54
escalation mean ± std | 0.561742812419088 ± 0.04325555381069406 | b.py | per seed [0.6286300080666846, 0.5555859990410302, 0.5393428129374493, 0.5001097373619138, 0.5850455046883618] | 5 seeds | 3e00400166e2eb54
missed_viol mean ± std | 0.020159097085074913 ± 0.00781883285004433 | b.py | per seed [0.014948453608247423, 0.02957130358705162, 0.02293838862559242, 0.025552353506243995, 0.00778498609823911] | 5 seeds | 3e00400166e2eb54
q_hat per seed | [0.0060863498953687145, 0.0053823798672983925, 0.005305324828547731, 0.005244097106357759, 0.006235816576919406] | b.py | — | per seed | 3e00400166e2eb54
q_hat mean ± std | 0.005650793654898401 ± 0.0004216059325605824 | b.py | — | 5 seeds | 3e00400166e2eb54
n_cal / n_test per seed | [29382, 29010, 26038, 29198, 27897] / [29752, 29198, 27146, 27338, 29008] | b.py | — | per seed | 3e00400166e2eb54
**4a. HISTGB SHIFTED** | | | | |
coverage_emp per seed | [0.891402258671686, 0.9055072265223646, 0.8964488322404774, 0.89417660399444, 0.8924089906232764] | b.py | — | per seed | 3e00400166e2eb54
coverage_emp mean ± std | 0.8959887824104488 ± 0.00505860700222826 | b.py | — | 5 seeds | 3e00400166e2eb54
escalation mean ± std | 0.5370570578461142 ± 0.05796109113738272 | b.py | per seed [0.46806937348749666, 0.5820261661757654, 0.46990348485964784, 0.5566610578681689, 0.6086252068394925] | 5 seeds | 3e00400166e2eb54
missed_viol mean ± std | 0.02458876466358913 ± 0.005516335637505814 | b.py | per seed [0.03178694158075601, 0.01837270341207349, 0.027298578199052133, 0.017867435158501442, 0.02761816496756256] | 5 seeds | 3e00400166e2eb54
q_hat mean ± std | 0.0021927423879113837 ± 0.00023814407456335525 | b.py | per seed [0.0020206550300618797, 0.0023252226949092014, 0.001922932398855992, 0.002106898389391487, 0.002588003426338359] | 5 seeds | 3e00400166e2eb54
n_cal / n_test per seed | [26409, 26780, 29758, 26597, 27898] / [29752, 29198, 27146, 27338, 29008] | b.py | — | per seed | 3e00400166e2eb54
**4b. HISTGB BENIGN CONTROL** | | | | |
coverage_emp per seed | [0.8905787917194762, 0.9008798977212905, 0.8658217241018121, 0.9111868695743859, 0.8971362431393047] | b.py | — | per seed | 3e00400166e2eb54
coverage_emp mean ± std | 0.8931207052512539 ± 0.015194812284911343 | b.py | — | 5 seeds | 3e00400166e2eb54
escalation mean ± std | 0.028453664038776548 ± 0.0077590862568321164 | b.py | per seed [0.025617390636402042, 0.024742423102955553, 0.02032051953493244, 0.02853829121709486, 0.04304969570249785] | 5 seeds | 3e00400166e2eb54
missed_viol mean ± std | 0.08245783789748802 ± 0.013349455189353954 | b.py | per seed [0.08648784156430182, 0.07912250431353217, 0.08542941309766598, 0.06003195617438941, 0.10121747433755073] | 5 seeds | 3e00400166e2eb54
q_hat mean ± std | 0.0021927423879113837 ± 0.00023814407456335525 (same cal as 4a) | b.py | — | 5 seeds | 3e00400166e2eb54
n_cal / n_test per seed | [26409, 26780, 29758, 26597, 27898] / [26037, 26594, 28641, 28453, 26783] | b.py | — | per seed | 3e00400166e2eb54
**4c. HISTGB IN-DISTRIBUTION MARGINAL** | | | | |
coverage_emp per seed | [0.9110311911804249, 0.9089321186382628, 0.903816400206292, 0.9084790401638745, 0.8848248758963044] | b.py | — | per seed | 3e00400166e2eb54
coverage_emp mean ± std | 0.9034167252170316 ± 0.00959002909673717 | b.py | — | 5 seeds | 3e00400166e2eb54
escalation mean ± std | 0.5914081281701327 ± 0.025203460747037748 | b.py | per seed [0.6162947028771175, 0.6115144872936502, 0.5456789213880499, 0.59730046089692, 0.5862520683949255] | 5 seeds | 3e00400166e2eb54
missed_viol mean ± std | 0.018850618838870816 ± 0.0061479015870778845 | b.py | per seed [0.01993127147766323, 0.01627296587926509, 0.017440758293838864, 0.01095100864553314, 0.029657089898053754] | 5 seeds | 3e00400166e2eb54
q_hat mean ± std | 0.00239242522916987 ± 0.0001000850364723261 | b.py | per seed [0.002524150911685674, 0.0024567416339507098, 0.0022244923239046477, 0.0023787537452482077, 0.0023779875310601106] | 5 seeds | 3e00400166e2eb54
n_cal / n_test per seed | [29382, 29010, 26038, 29198, 27897] / [29752, 29198, 27146, 27338, 29008] | b.py | — | per seed | 3e00400166e2eb54
**5. DECIDING QUESTION (coverage gaps)** | | | | |
RIDGE (b)−(a) mean | +0.10109531029809142; per seed [0.08043978, 0.07205401, 0.10245879, 0.13518965, 0.11533432] | b.py | benign_control − shifted | mean of per-seed diffs | 3e00400166e2eb54
RIDGE (b)−(a) larger std / exceeds? | 0.017998553298487808 (shifted std) — **EXCEEDS** (5.6×) | b.py | max(std_a, std_b) | — | 3e00400166e2eb54
RIDGE (c)−(a) mean | +0.089137038224291; per seed [0.11478220, 0.04856497, 0.07956973, 0.06401346, 0.13875483] | b.py | indist_marginal − shifted | mean of per-seed diffs | 3e00400166e2eb54
RIDGE (c)−(a) larger std / exceeds? | 0.026846519782127615 (cell-c std) — **EXCEEDS** (3.3×) | b.py | max(std_a, std_c) | — | 3e00400166e2eb54
HISTGB (b)−(a) mean | −0.002868077159194993; per seed [−0.00082347, −0.00462733, −0.03062711, 0.01701027, 0.00472725] | b.py | — | mean of per-seed diffs | 3e00400166e2eb54
HISTGB (b)−(a) larger std / exceeds? | 0.015194812284911343 (cell-b std) — **DOES NOT EXCEED** | b.py | — | — | 3e00400166e2eb54
HISTGB (c)−(a) mean | +0.0074279428065828325; per seed [0.01962893, 0.00342489, 0.00736757, 0.01430244, −0.00758411] | b.py | — | mean of per-seed diffs | 3e00400166e2eb54
HISTGB (c)−(a) larger std / exceeds? | 0.00959002909673717 (cell-c std) — **DOES NOT EXCEED** | b.py | — | — | 3e00400166e2eb54

Verdict on the deciding question (ridge): cell (c) coverage 0.884 ± 0.027 sits at nominal 0.90 within one std, while the shifted cell (a) is 0.795 ± 0.018. Both (b)−(a) and (c)−(a) exceed the larger relevant std, so ridge's drop is attributable to the calibration/test stratum MISMATCH, not to the marginal stratum being intrinsically harder to cover. HistGB shows no coverage gap in either comparison (both under one std); its stratum sensitivity appears in escalation instead (0.028 benign vs 0.591 in-distribution marginal).

Nothing was blocked; every quantity is independently derivable from `data/dataset.parquet`, `feasibility/make_splits.py`, `feasibility/gate_eval.py`, `scripts/tune_surrogates.py`, and the M2 configs in `data/tuned_metrics.json`.

Source hashes (sha256, first 16): `data/dataset.parquet` 8f0fd1081c8603e8 · `data/tuned_metrics.json` 360a9ec768152afe · `data/tradeoff_curve_v2.json` a40a079733ecdfcd · `feasibility/make_splits.py` 00c0168639765bd7 · `feasibility/gate_eval.py` 5f854d397f86962b · `scripts/tune_surrogates.py` 9395044201a93337
### S9 OUTCOME

B anchored at **max absolute difference 0.0 (exact)** against `data/tuned_metrics.json` per-seed
M2 records across q_hat / escalation / coverage_emp / missed_viol for all 10 model-seed cells,
and its seed-means reproduce `data/tradeoff_curve_v2.json` exactly including the ddof=0 stds.

**AGREE — per seed, to full stored precision:**

| quantity | A (artifact) | B (re-derived) |
|---|---|---|
| median `n0_min_vm` | 0.9433575252264039 | 0.9433575252264039 |
| ridge SHIFTED per-seed coverage | 0.803609841355203, 0.8226590862387835, 0.7983128269358285, 0.7806715926549126, 0.7712355212355212 | identical |
| ridge SHIFTED mean ± std | 0.7952977736840497 ± 0.017998553298487808 | identical |
| ridge BENIGN CONTROL per-seed | 0.8840496216922072, 0.8947130931789126, 0.9007716211026151, 0.9158612448599445, 0.8865698390770265 | identical |
| ridge BENIGN CONTROL mean ± std | 0.8963930839821412 ± 0.011400530217031263 | identical |
| ridge IN-DISTRIBUTION MARGINAL mean ± std | 0.884435 ± 0.026847 | **0.8844348119083406 ± 0.026846519782127615** |
| histgb benign→benign mean ± std | 0.8931207052512539 ± 0.015194812284911343 | identical |

**THE DECIDING RESULT — the ridge drop is DRIFT, not stratum difficulty.**

Cell (c), in-distribution marginal, is the cell that settles it: calibrate on marginal, evaluate
on marginal, so the stratum is equally hard but there is no mismatch.

| comparison | mean gap | per-seed | larger std | verdict |
|---|---|---|---|---|
| (b) benign control − (a) shifted | **+0.10109531029809142** | 0.08043978, 0.07205401, 0.10245879, 0.13518965, 0.11533432 | 0.017999 | **EXCEEDS, 5.6×** |
| (c) in-distribution marginal − (a) shifted | **+0.089137038224291** | 0.11478220, 0.04856497, 0.07956973, 0.06401346, 0.13875483 | 0.026847 | **EXCEEDS, 3.3×** |

B's verdict, verbatim above: cell (c) coverage 0.884 ± 0.027 "sits at nominal 0.90 within one
std, while the shifted cell (a) is 0.795 ± 0.018. Both (b)−(a) and (c)−(a) exceed the larger
relevant std, so ridge's drop is attributable to the calibration/test stratum MISMATCH, not to
the marginal stratum being intrinsically harder to cover."

**This REFUTES the amendment-2 framing supplied in the Stage 4 brief.** That framing held the
10.5-point drop to be "confounded by stratum difficulty", with in-distribution marginal coverage
at 0.7970, "only 0.0017 away" from the shifted value. Measured: in-distribution marginal is
**0.8844348119083406**, and the gap is **0.089137**, which exceeds its own std by 3.3×. The
supplied 0.7970 sits within 0.0017 of the SHIFTED value (0.7952977736840497), not the
in-distribution one — consistent with the two having been transposed.

**The layout's §0.3 flag is therefore confirmed by an independent anchored route.** The
supported claim for Discussion entry H is the one already specified there: ridge's residuals are
stratum-dependent, so marginal coverage does not hold conditionally. The confound reading is not
supported.

**histgb shows no coverage gap in either comparison** (both under one std). B notes its stratum
sensitivity surfaces in escalation instead: **0.028 benign vs 0.591 in-distribution marginal**.

**SINGLE-PATH — the stratum violation rates.** `data/drift_n0_stratum_long.parquet` contains no
violation-rate field (A: **ABSENT**), so only B's raw route produces them:

| stratum | violation rate | rows |
|---|---|---|
| benign | **0.15373696096354447** | 21,444 / 139,485 |
| marginal | **0.19577686957768695** | 27,305 / 139,470 |

Neither is the 24.3% / 4.7% pair supplied in the brief. **NO SOURCE for those two values**, now
established from both a raw re-derivation and the artifact's own absence of the field.

**S9 TALLY:  AGREE 24  |  DISAGREE-resolved 0  |  UNRESOLVED 0  |  SINGLE-PATH 2**

SINGLE-PATH: benign stratum violation rate; marginal stratum violation rate. Both are derivable
only from `data/dataset.parquet`, not from the drift artifact.

---

## S8 — barrier height

### S8 ROUND 1 — Agent A (derived artifacts) — VERBATIM

| quantity | value | file | jsonpath or column/filter | aggregation | sha256(16) |
|---|---|---|---|---|---|
| file digest — long parquet | b9e9b4040c8c56e7b281f1b072e2a6c43b7def0adee07451311f8fe7d71eb47e | data/barrier_height_long.parquet | whole file | — | b9e9b4040c8c56e7 |
| file digest — json | 468e30b2c9d7614bf72f878c648306d892ee0685c4de4618418430414107daa0 | data/barrier_height.json | whole file | — | 468e30b2c9d7614b |
| file digest — json manifest | c13ee8d59e229f39bd9318a5ad73d9700f78ba5ee1e21fdfa1e49e091927ce1a | data/barrier_height.manifest.json | whole file | — | c13ee8d59e229f39 |
| file digest — parquet manifest | ee52279f562e3945716f192e98445f43b34ea7801f257a87eb79130a54126a0e | data/barrier_height_long.manifest.json | whole file | — | ee52279f562e3945 |
| manifest content_sha256 (json) | 468e30b2c9d7614bf72f878c648306d892ee0685c4de4618418430414107daa0 | data/barrier_height.manifest.json | $.content_sha256 | — | matches json file ✓ |
| manifest content_sha256 (parquet) | b9e9b4040c8c56e7b281f1b072e2a6c43b7def0adee07451311f8fe7d71eb47e | data/barrier_height_long.manifest.json | $.content_sha256 | — | matches parquet ✓ |
| manifest git_commit | 09f74446c4ecf6c5f3524189f3986f67ae280693 | both manifests | $.git_commit.full | — | — |
| manifest model_hyperparameters | null | both manifests | $.model_hyperparameters | — | — |
| manifest artifact.n_records / n_fields | null / null | both manifests | $.artifact.* | — | — |
| **1. long parquet shape** | | | | | |
| row count | 180 | barrier_height_long.parquet | all rows | count | b9e9b4040c8c56e7 |
| column count | 21 | barrier_height_long.parquet | all columns | count | b9e9b4040c8c56e7 |
| distinct network | case118, case30_thermal (2) | barrier_height_long.parquet | network | unique | b9e9b4040c8c56e7 |
| distinct model | histgb, ridge (2) | barrier_height_long.parquet | model | unique | b9e9b4040c8c56e7 |
| distinct seed | 0,1,2,3,4 (5) | barrier_height_long.parquet | seed | unique | b9e9b4040c8c56e7 |
| distinct coverage_target | 0.9,0.91,0.92,0.93,0.94,0.95,0.96,0.97,0.98 (9) | barrier_height_long.parquet | coverage_target | unique | b9e9b4040c8c56e7 |
| cell count check | 2×2×5×9 = 180 = row count (complete grid) | barrier_height_long.parquet | — | product | b9e9b4040c8c56e7 |
| **2. identity_checks block** | | | | | |
| max_identity_gap | 5.551115123125783e-17 | barrier_height.json | $.identity_checks.max_identity_gap | — | 468e30b2c9d7614b |
| min_share_missed_overshoot_gt_qhat | 1.0 | barrier_height.json | $.identity_checks.min_share_missed_overshoot_gt_qhat | — | 468e30b2c9d7614b |
| min_share_missed_overshoot_ge_qhat_plus_depth | 1.0 | barrier_height.json | $.identity_checks.min_share_missed_overshoot_ge_qhat_plus_depth | — | 468e30b2c9d7614b |
| n_rows_with_any_miss | 173 | barrier_height.json | $.identity_checks.n_rows_with_any_miss | — | 468e30b2c9d7614b |
| n_rows | 180 | barrier_height.json | $.identity_checks.n_rows | — | 468e30b2c9d7614b |
| identity_checks cross-check (parquet) | max abs identity_gap = 5.551115123125783e-17; rows with n_missed>0 = 173; rows = 180 — all agree | barrier_height_long.parquet | identity_gap, n_missed | max / count | b9e9b4040c8c56e7 |
| other json header fields | question/definitions present; coverage_targets = [0.9…0.98]; seeds = 5; limit = 0.94 | barrier_height.json | $.coverage_targets, $.seeds, $.limit | — | 468e30b2c9d7614b |
| **3. per-seed values at coverage_target = 0.90** (seed order 0,1,2,3,4; std = ddof=0) | | | | | |
| case118 / ridge · q_hat | 0.00552461357270162 ; 0.0051332624013122885 ; 0.004943555243710485 ; 0.0049365181872691455 ; 0.00545320578083186 | barrier_height_long.parquet | q_hat @ network=case118, model=ridge, coverage_target=0.9 | mean 0.005198231037165079 · std0 0.00024864109822318324 | b9e9b4040c8c56e7 |
| case118 / ridge · missed_viol | 0.02620042817820369 ; 0.034281620957838724 ; 0.0351981833195706 ; 0.02837471312330482 ; 0.024102671118530886 | same | missed_viol | mean 0.029631523339489742 · std0 0.004393889029106623 | b9e9b4040c8c56e7 |
| case118 / ridge · mean_overshoot_given_viol | 0.003421674375822684 ; 0.003255016420962104 ; 0.003301614037913879 ; 0.0031686727817745665 ; 0.0024851497469978454 | same | mean_overshoot_given_viol | mean 0.0031264254726942158 · std0 0.0003308830523464929 | b9e9b4040c8c56e7 |
| case118 / ridge · S_mean_over_qhat | 0.6193508977225051 ; 0.6341028699662768 ; 0.6678622722208696 ; 0.6418841502389884 ; 0.45572271556910654 | same | S_mean_over_qhat | mean 0.6037845811435492 · std0 0.07568533879876284 | b9e9b4040c8c56e7 |
| case118 / ridge · S_p99_over_qhat | 5.999243363166272 ; 6.914424921213873 ; 6.988541875573607 ; 7.118471599968324 ; 5.721262536236863 | same | S_p99_over_qhat | mean 6.548388859231787 · std0 0.5724351732365826 | b9e9b4040c8c56e7 |
| case118 / ridge · p_overshoot_gt_qhat_given_viol | 0.3784279743093078 ; 0.4081047891936144 ; 0.4080305532617671 ; 0.39787189651575217 ; 0.3494365609348915 | same | p_overshoot_gt_qhat_given_viol | mean 0.3883743548430666 · std0 0.022275285649880475 | b9e9b4040c8c56e7 |
| case118 / ridge · p_overshoot_gt_qhat | 0.08440732043951317 ; 0.1167192429022082 ; 0.11298331152419022 ; 0.12016275026437956 ; 0.09877937301715331 | same | p_overshoot_gt_qhat | mean 0.10661039962948889 · std0 0.013272306727773363 | b9e9b4040c8c56e7 |
| case118 / ridge · coverage_emp | 0.9155926795604868 ; 0.8832807570977917 ; 0.8870166884758097 ; 0.8798372497356204 ; 0.9012206269828467 | same | coverage_emp | mean 0.8933896003705112 · std0 0.013272306727773393 | b9e9b4040c8c56e7 |
| case118 / ridge · identity_gap | 1.3877787807814457e-17 ; 5.551115123125783e-17 ; 5.551115123125783e-17 ; 5.551115123125783e-17 ; 2.7755575615628914e-17 | same | identity_gap | mean 4.163336342344337e-17 · std0 1.7554167342883506e-17 | b9e9b4040c8c56e7 |
| case118 / histgb · q_hat | 0.002335618678972362 ; 0.002353357097683695 ; 0.0020534393537054996 ; 0.002262051382869279 ; 0.002449047318323294 | barrier_height_long.parquet | q_hat @ case118, histgb, 0.9 | mean 0.002290702766310826 · std0 0.0001327635720642294 | b9e9b4040c8c56e7 |
| case118 / histgb · missed_viol | 0.04557039453563054 ; 0.04308227589029881 ; 0.0514037985136251 ; 0.03306905904443981 ; 0.06270868113522537 | same | missed_viol | mean 0.04716684182384393 · std0 0.009772209302677339 | b9e9b4040c8c56e7 |
| case118 / histgb · mean_overshoot_given_viol | 0.0018242843371307287 ; 0.0020035244052224364 ; 0.0017829020608238653 ; 0.0014873937382153977 ; 0.0019627611827035944 | same | mean_overshoot_given_viol | mean 0.0018121731448192044 · std0 0.00018208635440535663 | b9e9b4040c8c56e7 |
| case118 / histgb · S_mean_over_qhat | 0.7810711369774569 ; 0.8513473825091894 ; 0.8682516274983039 ; 0.6575419769327814 ; 0.8014386524991159 | same | S_mean_over_qhat | mean 0.7919301552833694 · std0 0.07432884539735458 | b9e9b4040c8c56e7 |
| case118 / histgb · S_p99_over_qhat | 9.156508345887303 ; 10.050495511549022 ; 10.70742076378319 ; 9.74912150545601 ; 9.209939494280208 | same | S_p99_over_qhat | mean 9.774697124191146 · std0 0.5740733048592552 | b9e9b4040c8c56e7 |
| case118 / histgb · p_overshoot_gt_qhat_given_viol | 0.4117647058823529 ; 0.4110724519033975 ; 0.42557803468208094 ; 0.37168787815564364 ; 0.4373956594323873 | same | p_overshoot_gt_qhat_given_viol | mean 0.41149974601117245 · std0 0.022154160557125376 | b9e9b4040c8c56e7 |
| case118 / histgb · p_overshoot_gt_qhat | 0.0952876014985033 ; 0.09585603670777172 ; 0.11497302238872856 ; 0.0907135559498844 ; 0.11229409761431056 | same | p_overshoot_gt_qhat | mean 0.1018248628318397 · std0 0.009841776143853145 | b9e9b4040c8c56e7 |
| case118 / histgb · coverage_emp | 0.9047123985014968 ; 0.9041439632922282 ; 0.8850269776112715 ; 0.9092864440501156 ; 0.8877059023856895 | same | coverage_emp | mean 0.8981751371681603 · std0 0.009841776143853134 | b9e9b4040c8c56e7 |
| case118 / histgb · identity_gap | 5.551115123125783e-17 ; 4.163336342344337e-17 ; 2.7755575615628914e-17 ; 0.0 ; 2.7755575615628914e-17 | same | identity_gap | mean 3.053113317719181e-17 · std0 1.841096603147574e-17 | b9e9b4040c8c56e7 |
| case30_thermal / ridge · q_hat | 0.007069312705351605 ; 0.007661893421298416 ; 0.0070427253779346 ; 0.006556230440814881 ; 0.006539367450236533 | barrier_height_long.parquet | q_hat @ case30_thermal, ridge, 0.9 | mean 0.006973905879127207 · std0 0.00041241771592434367 | b9e9b4040c8c56e7 |
| case30_thermal / ridge · missed_viol | 0.05741626794258373 ; 0.05671806167400881 ; 0.062173458725182866 ; 0.05963060686015831 ; 0.06842672413793104 | same | missed_viol | mean 0.060873023867972956 · std0 0.004230980760261226 | b9e9b4040c8c56e7 |
| case30_thermal / ridge · mean_overshoot_given_viol | 0.004960951740946013 ; 0.004715014759830381 ; 0.004993396642308323 ; 0.005103797560327324 ; 0.005245157822937022 | same | mean_overshoot_given_viol | mean 0.0050036637052698115 · std0 0.00017526787268526498 | b9e9b4040c8c56e7 |
| case30_thermal / ridge · S_mean_over_qhat | 0.7017587066406721 ; 0.6153850622254355 ; 0.7090148166153146 ; 0.7784652486517798 ; 0.8020894777441052 | same | S_mean_over_qhat | mean 0.7213426623754614 · std0 0.0656438240627924 | b9e9b4040c8c56e7 |
| case30_thermal / ridge · S_p99_over_qhat | 3.9856628583193507 ; 4.029388560481003 ; 4.56734854922222 ; 4.877051042392468 ; 4.493934578895959 | same | S_p99_over_qhat | mean 4.390677117862201 · std0 0.33852635481112553 | b9e9b4040c8c56e7 |
| case30_thermal / ridge · p_overshoot_gt_qhat_given_viol | 0.3875598086124402 ; 0.3595814977973568 ; 0.37565308254963425 ; 0.4216358839050132 ; 0.4353448275862069 | same | p_overshoot_gt_qhat_given_viol | mean 0.3959550200901302 · std0 0.02834341217458747 | b9e9b4040c8c56e7 |
| case30_thermal / ridge · p_overshoot_gt_qhat | 0.09 ; 0.09723577235772357 ; 0.09447154471544715 ; 0.09869918699186991 ; 0.10252032520325204 | same | p_overshoot_gt_qhat | mean 0.09658536585365854 · std0 0.004194050408306695 | b9e9b4040c8c56e7 |
| case30_thermal / ridge · coverage_emp | 0.91 ; 0.9027642276422764 ; 0.9055284552845528 ; 0.90130081300813 ; 0.897479674796748 | same | coverage_emp | mean 0.9034146341463416 · std0 0.0041940504083067135 | b9e9b4040c8c56e7 |
| case30_thermal / ridge · identity_gap | 2.7755575615628914e-17 ; 5.551115123125783e-17 ; 1.3877787807814457e-17 ; 5.551115123125783e-17 ; 1.3877787807814457e-17 | same | identity_gap | mean 3.3306690738754695e-17 · std0 1.8824747269678058e-17 | b9e9b4040c8c56e7 |
| case30_thermal / histgb · q_hat | 0.0019888518317571213 ; 0.0026916894619768428 ; 0.002758134823135583 ; 0.0021480028654903283 ; 0.002188979088448284 | barrier_height_long.parquet | q_hat @ case30_thermal, histgb, 0.9 | mean 0.002355131614161632 · std0 0.000309952457868838 | b9e9b4040c8c56e7 |
| case30_thermal / histgb · missed_viol | 0.019138755980861243 ; 0.026982378854625552 ; 0.024033437826541274 ; 0.017414248021108178 ; 0.023706896551724137 | same | missed_viol | mean 0.022255143446972075 · std0 0.0034860525509527274 | b9e9b4040c8c56e7 |
| case30_thermal / histgb · mean_overshoot_given_viol | 0.0008119370518968176 ; 0.0011117819051856684 ; 0.0008028059618872284 ; 0.000554815791985001 ; 0.000764007748914108 | same | mean_overshoot_given_viol | mean 0.0008090696919737645 · std0 0.00017796503278283765 | b9e9b4040c8c56e7 |
| case30_thermal / histgb · S_mean_over_qhat | 0.4082441129762206 ; 0.4130424110547836 ; 0.2910684260802593 ; 0.2582937857759106 ; 0.34902469052625584 | same | S_mean_over_qhat | mean 0.343934685282686 · std0 0.06175223629218416 | b9e9b4040c8c56e7 |
| case30_thermal / histgb · S_p99_over_qhat | 5.859320122686069 ; 5.6387637522939364 ; 4.612412341158058 ; 4.257176259320144 ; 5.697651964304223 | same | S_p99_over_qhat | mean 5.213064887952486 · std0 0.6493375914589473 | b9e9b4040c8c56e7 |
| case30_thermal / histgb · p_overshoot_gt_qhat_given_viol | 0.21584263689526847 ; 0.2406387665198238 ; 0.2304075235109718 ; 0.21108179419525067 ; 0.2510775862068966 | same | p_overshoot_gt_qhat_given_viol | mean 0.22980966146564227 · std0 0.014938288830694315 | b9e9b4040c8c56e7 |
| case30_thermal / histgb · p_overshoot_gt_qhat | 0.09024390243902439 ; 0.09154471544715446 ; 0.09439024390243902 ; 0.09585365853658537 ; 0.11699186991869918 | same | p_overshoot_gt_qhat | mean 0.09780487804878048 · std0 0.009797608166533115 | b9e9b4040c8c56e7 |
| case30_thermal / histgb · coverage_emp | 0.9097560975609756 ; 0.9084552845528455 ; 0.905609756097561 ; 0.9041463414634147 ; 0.8830081300813009 | same | coverage_emp | mean 0.9021951219512196 · std0 0.009797608166533104 | b9e9b4040c8c56e7 |
| case30_thermal / histgb · identity_gap | 2.7755575615628914e-17 ; 1.3877787807814457e-17 ; 2.7755575615628914e-17 ; 2.7755575615628914e-17 ; 4.163336342344337e-17 | same | identity_gap | mean 2.7755575615628914e-17 · std0 8.777083671441753e-18 | b9e9b4040c8c56e7 |
| **4. S_mean_over_qhat direction, case118 → case30_thermal @ 0.90** | | | | | |
| ridge | case118 0.6037845811435492 (std0 0.07568533879876284) → case30_thermal 0.7213426623754614 (std0 0.0656438240627924); diff = **+0.11755808123191225**; sign **POSITIVE (rises)**; |diff| > max std (0.07568533879876284) → **YES** | barrier_height_long.parquet | S_mean_over_qhat @ model=ridge, coverage_target=0.9 | seed mean, std0 | b9e9b4040c8c56e7 |
| histgb | case118 0.7919301552833694 (std0 0.07432884539735458) → case30_thermal 0.343934685282686 (std0 0.06175223629218416); diff = **−0.4479954700006834**; sign **NEGATIVE (falls)**; |diff| > max std (0.07432884539735458) → **YES** | same | S_mean_over_qhat @ model=histgb, 0.9 | seed mean, std0 | b9e9b4040c8c56e7 |
| **5. S_p99_over_qhat direction, case118 → case30_thermal @ 0.90** | | | | | |
| ridge | case118 6.548388859231787 (std0 0.5724351732365826) → case30_thermal 4.390677117862201 (std0 0.33852635481112553); diff = **−2.157711741369586**; sign **NEGATIVE (falls)**; |diff| > max std (0.5724351732365826) → **YES** | barrier_height_long.parquet | S_p99_over_qhat @ ridge, 0.9 | seed mean, std0 | b9e9b4040c8c56e7 |
| histgb | case118 9.774697124191146 (std0 0.5740733048592552) → case30_thermal 5.213064887952486 (std0 0.6493375914589473); diff = **−4.56163223623866**; sign **NEGATIVE (falls)**; |diff| > max std (0.6493375914589473) → **YES** | same | S_p99_over_qhat @ histgb, 0.9 | seed mean, std0 | b9e9b4040c8c56e7 |
| **6. share columns (all 180 rows)** | | | | | |
| share_missed_overshoot_gt_qhat | min 1.0, max 1.0, non-null 173 (null 7) | barrier_height_long.parquet | share_missed_overshoot_gt_qhat | min / max / count | b9e9b4040c8c56e7 |
| share_missed_overshoot_ge_qhat_plus_depth | min 1.0, max 1.0, non-null 173 (null 7) | barrier_height_long.parquet | share_missed_overshoot_ge_qhat_plus_depth | min / max / count | b9e9b4040c8c56e7 |
| null rows explained | the 7 nulls are exactly the 7 rows with n_missed == 0 | barrier_height_long.parquet | n_missed == 0 | count | b9e9b4040c8c56e7 |
| **7. counterexample population** | | | | | |
| sum n_missed (all 180 rows) | 19625 | barrier_height_long.parquet | n_missed | sum | b9e9b4040c8c56e7 |
| sum n_test (all 180 rows) | 6128100 | barrier_height_long.parquet | n_test | sum | b9e9b4040c8c56e7 |
| **8. summary_at_090 — every stored field** | | | | | |
| case118/ridge | q_hat mean 0.005198231037165079, std 0.00024864109822318324; missed mean 0.029631523339489742, std 0.004393889029106623; mean_overshoot_given_viol 0.0031264254726942158; S_mean mean 0.6037845811435492, std 0.07568533879876284; S_p99 mean 6.548388859231787, std 0.5724351732365826; p_overshoot_gt_qhat_given_viol mean 0.3883743548430666 | barrier_height.json | $.summary_at_090.case118.ridge.* | — | 468e30b2c9d7614b |
| case118/histgb | q_hat mean 0.002290702766310826, std 0.0001327635720642294; missed mean 0.04716684182384393, std 0.009772209302677339; mean_overshoot_given_viol 0.0018121731448192044; S_mean mean 0.7919301552833694, std 0.07432884539735458; S_p99 mean 9.774697124191146, std 0.5740733048592552; p_overshoot_gt_qhat_given_viol mean 0.41149974601117245 | barrier_height.json | $.summary_at_090.case118.histgb.* | — | 468e30b2c9d7614b |
| case30_thermal/ridge | q_hat mean 0.006973905879127207, std 0.00041241771592434367; missed mean 0.060873023867972956, std 0.004230980760261226; mean_overshoot_given_viol 0.0050036637052698115; S_mean mean 0.7213426623754614, std 0.0656438240627924; S_p99 mean 4.390677117862201, std 0.33852635481112553; p_overshoot_gt_qhat_given_viol mean 0.3959550200901302 | barrier_height.json | $.summary_at_090.case30_thermal.ridge.* | — | 468e30b2c9d7614b |
| case30_thermal/histgb | q_hat mean 0.002355131614161632, std 0.000309952457868838; missed mean 0.022255143446972075, std 0.0034860525509527274; mean_overshoot_given_viol 0.0008090696919737645; S_mean mean 0.343934685282686, std 0.06175223629218416; S_p99 mean 5.213064887952486, std 0.6493375914589473; p_overshoot_gt_qhat_given_viol mean 0.22980966146564227 | barrier_height.json | $.summary_at_090.case30_thermal.histgb.* | — | 468e30b2c9d7614b |
| **cross-check** | every summary_at_090 field reproduces the parquet seed-level mean / std(ddof=0) to full stored precision — 0 mismatches; the summary block stores no p_overshoot_gt_qhat, no coverage_emp, no identity_gap, and no std for mean_overshoot_given_viol or for p_overshoot_gt_qhat_given_viol | both | — | — | — |

Files: `/Users/rajansaha/contingency-screener-research/data/barrier_height.json`, `/Users/rajansaha/contingency-screener-research/data/barrier_height_long.parquet`, `/Users/rajansaha/contingency-screener-research/data/barrier_height.manifest.json`, `/Users/rajansaha/contingency-screener-research/data/barrier_height_long.manifest.json`
### S8 ROUND 1 — Agent B (re-derived, ANCHORED exact on BOTH datasets) — VERBATIM

**ANCHOR: PASSED (both). case118 max |Δ| = 0.0 (exact); case30 protocol max |Δ| = 0.0 (exact).** All numbers below are ANCHORED.

Derivation common to all rows: `.venv/bin/python`, `feasibility/make_splits.py` (GroupShuffleSplit on `scenario_id`, 0.6/0.2/0.2), M2 config refit on full train, `ge.calibrate_qhat` on full cal at 0.90, gate on full test. `o = pred_test - y_test`, `d = 0.94 - y_test`, violation `y_test < 0.94`. Aggregation "5 seeds" = mean ± population std (ddof=0), seeds 0–4. Scratch driver: `/private/tmp/claude-501/-Users-rajansaha-contingency-screener-research/a20165b8-6ffa-4031-84e5-ca5fd47a15f6/scratchpad/agentB.py`; per-cell output `res_case118.json`, `res_case30.json`, `res_case30t.json` in that directory.

| quantity | value | source | derivation | aggregation | sha256(16) |
|---|---|---|---|---|---|
| ANCHOR case118 max abs diff vs tradeoff_curve_v2 @0.90 (escalation, coverage_emp, missed_viol, q_hat; means and stds) | 0.0 (exact bit-match, all 8 pairs) | data/dataset.parquet; data/tuned_metrics.json (stored M2 tags); data/tradeoff_curve_v2.json | refit stored M2 per (family,seed), calibrate on cal, gate test @0.90 | 5 seeds | 8f0fd1081c8603e8 / 360a9ec768152afe / a40a079733ecdfcd |
| ANCHOR case30 max abs diff vs case30_frozen four_metrics_at_90pct_coverage | 0.0 (exact; incl. n_missed_per_seed and n_true_viol_per_seed identical) | data/case30_dataset.parquet; data/case30_frozen.json | inner-split M2 selection per scripts/case30_thermal_gate.py protocol | 5 seeds | 4d73f8cdfe8131d2 / d501f99671b40a78 |
| CROSSCHECK case30-thermal max abs diff vs data/case30_thermal/case30_thermal_frozen.json | 0.0 (exact, 8 pairs) | data/case30_thermal/dataset.parquet | same protocol, thermal dataset | 5 seeds | cb1a38e9a39ef233 / b340af22662fdd29 |
| M2 tags selected, case118 ridge / histgb | alpha1, alpha0.001, alpha0.001, alpha0.001, alpha0.01 / rand00, rand13, rand20, rand01, rand16 | data/tuned_metrics.json selections | stored | per seed | 360a9ec768152afe |
| M2 tags selected, case30-thermal ridge / histgb | alpha0.01, alpha3.162, alpha0.1, alpha0.001, alpha0.003162 / rand15, rand14, rand11, rand00, rand00 | re-derived | inner-split search (not stored anywhere) | per seed | cb1a38e9a39ef233 |
| **1. q_hat** case118 ridge | 0.00519823 ± 0.00024864 (seeds: .005525/.005133/.004944/.004937/.005453) | dataset.parquet | calibrate_qhat(cal, 0.90) | 5 seeds | 8f0fd1081c8603e8 |
| **1.** q_hat case118 histgb | 0.00229070 ± 0.00013276 | dataset.parquet | same | 5 seeds | 8f0fd1081c8603e8 |
| **1.** q_hat case30-thermal ridge | 0.00697391 ± 0.00041242 | case30_thermal/dataset.parquet | same | 5 seeds | cb1a38e9a39ef233 |
| **1.** q_hat case30-thermal histgb | 0.00235513 ± 0.00030995 | case30_thermal/dataset.parquet | same | 5 seeds | cb1a38e9a39ef233 |
| **2. mean(o \| viol)** case118 ridge | 0.00312643 ± 0.00033088 | dataset.parquet | mean of o over y_test<0.94 | 5 seeds | 8f0fd1081c8603e8 |
| **2.** mean(o \| viol) case118 histgb | 0.00181217 ± 0.00018209 | dataset.parquet | same | 5 seeds | 8f0fd1081c8603e8 |
| **2.** mean(o \| viol) case30-thermal ridge | 0.00500366 ± 0.00017527 | case30_thermal/dataset.parquet | same | 5 seeds | cb1a38e9a39ef233 |
| **2.** mean(o \| viol) case30-thermal histgb | 0.00080907 ± 0.00017797 | case30_thermal/dataset.parquet | same | 5 seeds | cb1a38e9a39ef233 |
| **2. S_mean** case118 ridge | 0.603785 ± 0.075685 (seeds: .619351/.634103/.667862/.641884/.455723) | dataset.parquet | mean(o\|viol)/q_hat per seed | 5 seeds | 8f0fd1081c8603e8 |
| **2.** S_mean case118 histgb | 0.791930 ± 0.074329 (seeds: .781071/.851347/.868252/.657542/.801439) | dataset.parquet | same | 5 seeds | 8f0fd1081c8603e8 |
| **2.** S_mean case30-thermal ridge | 0.721343 ± 0.065644 (seeds: .701759/.615385/.709015/.778465/.802089) | case30_thermal/dataset.parquet | same | 5 seeds | cb1a38e9a39ef233 |
| **2.** S_mean case30-thermal histgb | 0.343935 ± 0.061752 (seeds: .408244/.413042/.291068/.258294/.349025) | case30_thermal/dataset.parquet | same | 5 seeds | cb1a38e9a39ef233 |
| **3. S_p99** case118 ridge | 6.548389 ± 0.572435 (seeds: 5.999243/6.914425/6.988542/7.118472/5.721263) | dataset.parquet | np.percentile(o[viol],99)/q_hat | 5 seeds | 8f0fd1081c8603e8 |
| **3.** S_p99 case118 histgb | 9.774697 ± 0.574073 (seeds: 9.156508/10.050496/10.707421/9.749122/9.209939) | dataset.parquet | same | 5 seeds | 8f0fd1081c8603e8 |
| **3.** S_p99 case30-thermal ridge | 4.390677 ± 0.338526 (seeds: 3.985663/4.029389/4.567349/4.877051/4.493935) | case30_thermal/dataset.parquet | same | 5 seeds | cb1a38e9a39ef233 |
| **3.** S_p99 case30-thermal histgb | 5.213065 ± 0.649338 (seeds: 5.859320/5.638764/4.612412/4.257176/5.697652) | case30_thermal/dataset.parquet | same | 5 seeds | cb1a38e9a39ef233 |
| **4. missed_viol** case118 ridge | 0.0296315 ± 0.0043939 (seeds: .026200/.034282/.035198/.028375/.024103; n_missed 257/335/341/272/231) | dataset.parquet | ge.score missed_viol @0.90 | 5 seeds | 8f0fd1081c8603e8 |
| **4.** missed_viol case118 histgb | 0.0471668 ± 0.0097722 (n_missed 447/421/498/317/601) | dataset.parquet | same | 5 seeds | 8f0fd1081c8603e8 |
| **4.** missed_viol case30-thermal ridge | 0.0608730 ± 0.0042310 (n_missed 108/103/119/113/127) | case30_thermal/dataset.parquet | same | 5 seeds | cb1a38e9a39ef233 |
| **4.** missed_viol case30-thermal histgb | 0.0222551 ± 0.0034861 (n_missed 36/49/46/33/44) | case30_thermal/dataset.parquet | same | 5 seeds | cb1a38e9a39ef233 |
| **5. identity check** P(o>q_hat) vs 1−coverage_emp: expected exactly 0 (coverage = mean(y ≥ pred−q_hat) = mean(o ≤ q_hat), complementary by construction) | measured max abs = 5.55e-17 over all 20 (network, model, seed) cells — float round-off only | both datasets | per cell, all test rows | max over 20 cells | 8f0fd1081c8603e8 + cb1a38e9a39ef233 |
| **5.** P(o>q_hat) means (= 1 − coverage_emp) | case118 ridge 0.106610 ± 0.013272; case118 histgb 0.101825 ± 0.009842; case30t ridge 0.096585 ± 0.004194; case30t histgb 0.097805 ± 0.009798 | both | all test rows | 5 seeds | — |
| **6. COUNTEREXAMPLE COUNT** rows certified AND violating with o < q_hat + d | **0** | both | certify ⇒ pred ≥ 0.94 + q_hat; viol ⇒ y < 0.94 ⇒ o = pred − y ≥ q_hat + d, so the set is empty by construction | union of 20 cells | — |
| **6.** total missed cases examined | 4498 | both | Σ n_missed over 20 cells (case118 ridge 1436 + histgb 2284; case30t ridge 570 + histgb 208) | union of 20 cells | — |
| **6.** total test cases examined | 680900 | both | Σ n_test over 20 cells (case118 55789/55792/55787/55791/55791 ×2 models; case30t 12300 ×5 ×2) | union of 20 cells | — |
| **7. DIRECTION, ridge** | case118 S_mean 0.603785 ± 0.075685 → case30-thermal 0.721343 ± 0.065644; diff **+0.117558** (positive); larger std 0.075685; **exceeds = YES**; ridge **RISES** | both | S_mean means | 5 seeds each | — |
| **7. DIRECTION, histgb** | case118 S_mean 0.791930 ± 0.074329 → case30-thermal 0.343935 ± 0.061752; diff **−0.447995** (negative); larger std 0.074329; **exceeds = YES**; histgb **FALLS** | both | S_mean means | 5 seeds each | — |
| **7. (supplementary) S_p99 direction** | ridge 6.548389 → 4.390677, diff −2.157712, larger std 0.572435, exceeds YES, **FALLS**; histgb 9.774697 → 5.213065, diff −4.561632, larger std 0.649338, exceeds YES, **FALLS** | both | S_p99 means | 5 seeds each | — |

Two notes on item 7: the two models disagree in sign for S_mean (ridge rises, histgb falls), so there is no single direction for "the S ratio" across networks; and the S_mean direction and the S_p99 direction disagree for ridge (mean rises, 99th percentile falls), so the answer depends on which statistic of the overshoot distribution is used. Both gaps exceed the larger of the two stds under the project's std rule.
### S8 OUTCOME

B anchored **exactly on both datasets**: case118 max |Δ| = **0.0** against
`data/tradeoff_curve_v2.json`, and the case30 protocol max |Δ| = **0.0** against
`data/case30_frozen.json`. It never opened `data/barrier_height.json`,
`barrier_height_long.parquet`, or `scripts/barrier_height.py`.

**AGREE — every S_mean to six decimals, with per-seed values B supplies that the summary block
does not expose:**

| network | model | A (artifact) | B (re-derived) | B per-seed |
|---|---|---|---|---|
| case118 | ridge | 0.603785 ± 0.075685 | **0.603785 ± 0.075685** | .619351 / .634103 / .667862 / .641884 / .455723 |
| case118 | histgb | 0.791930 ± 0.074329 | **0.791930 ± 0.074329** | .781071 / .851347 / .868252 / .657542 / .801439 |
| case30-thermal | ridge | 0.721343 ± 0.065644 | **0.721343 ± 0.065644** | .701759 / .615385 / .709015 / .778465 / .802089 |
| case30-thermal | histgb | 0.343935 ± 0.061752 | **0.343935 ± 0.061752** | .408244 / .413042 / .291068 / .258294 / .349025 |

**THE DIRECTION QUESTION — the claim §5.4 rests on is NOT single-path.**

| model | case118 → case30-thermal | difference | larger std | exceeds? | direction |
|---|---|---|---|---|---|
| ridge | 0.603785 → 0.721343 | **+0.117558** | 0.075685 | **YES** | **RISES** |
| histgb | 0.791930 → 0.343935 | **−0.447995** | 0.074329 | **YES** | **FALLS** |

Both directions are independently reproduced from raw and both survive the std rule. **This
confirms the layout's §0.1 flag from a second route: the Stage 4 brief had the direction
inverted for both models.**

**Identity and counterexamples, both re-derived independently:**

| check | A (artifact) | B (re-derived) |
|---|---|---|
| max \|P(o>q_hat) − (1−coverage)\| | 5.551115123125783e-17 | **5.55e-17 over all 20 cells** |
| certified-and-violating rows with `o < q_hat + d` | implied 0 | **0** |

B adds the reason the counterexample count is 0, which the artifact does not state: "certify ⇒
pred ≥ 0.94 + q_hat; viol ⇒ y < 0.94 ⇒ o = pred − y ≥ q_hat + d, so the set is empty by
construction." It is not an empirical zero.

**TWO QUALIFICATIONS B RAISED THAT MATERIALLY AFFECT §5.4, neither previously recorded:**

1. **There is no single direction for "the S ratio".** The two models disagree in sign — ridge
   rises, histgb falls. Any §5.4 sentence of the form "the S ratio moves in direction X across
   networks" is unwritable; the statement must be per model.

2. **The direction is statistic-dependent, and for ridge the two statistics disagree.**
   S_p99/q_hat **FALLS for both models**: ridge 6.548389 → 4.390677 (diff −2.157712, larger std
   0.572435, exceeds) and histgb 9.774697 → 5.213065 (diff −4.561632, larger std 0.649338,
   exceeds). So ridge's mean overshoot rises relative to its barrier while its 99th percentile
   falls relative to its barrier. **§5.4 must name which statistic it is using.** The mechanism
   sentence specified in the layout uses the conditional MEAN and must say so explicitly, or it
   will be contradicted by the tail statistic in the same artifact.

This is the same finding that falsified pre-registered prediction P-BH-6, now confirmed from an
independent anchored route and extended: it is not only that the tail ratio fails to explain the
reversal, it is that the tail ratio moves the *opposite way* from the mean ratio for ridge.

**S8 TALLY:  AGREE 34  |  DISAGREE-resolved 0  |  UNRESOLVED 0  |  SINGLE-PATH 0**

---

# PAIRED ADJUDICATION S8-S9 — CLOSING TABLE

| scenario | AGREE | DISAGREE-resolved | UNRESOLVED | SINGLE-PATH |
|---|---|---|---|---|
| S8 barrier height | 34 | 0 | 0 | 0 |
| S9 2C stratum quantities | 24 | 0 | 0 | 2 |
| **TOTAL** | **58** | **0** | **0** | **2** |

Round 2 was not required in either scenario — both A/B pairs agreed on every shared quantity at
first pass. Both B routes anchored exactly (0.0).

## SINGLE-PATH

| quantity | value | why single-path |
|---|---|---|
| benign stratum violation rate | 0.15373696096354447 (21,444 / 139,485) | `drift_n0_stratum_long.parquet` has no violation-rate field; A reports ABSENT |
| marginal stratum violation rate | 0.19577686957768695 (27,305 / 139,470) | same |

Both are derivable from `data/dataset.parquet` alone, so the remedy is a `writing-numbers.md`
row citing that source rather than the drift artifact.

## UNRESOLVED

None.

## What S8 and S9 settle about the Stage 4 amendments

Both supplied amendment values that the layout flagged in its §0 are now **independently
refuted from anchored raw re-derivations**, not merely disagreed with:

- **Amendment 1 direction.** Ridge RISES (+0.117558), histgb FALLS (−0.447995), both exceeding
  the std rule. The supplied "ridge 0.604 → 0.219, histgb 0.443 → 0.482" inverts both.
- **Amendment 2 confound.** In-distribution marginal coverage is **0.8844348119083406 ±
  0.026846519782127615**, not 0.7970; the gap to the shifted cell is **0.089137**, exceeding its
  own std by 3.3×. Ridge's drop is stratum MISMATCH, not stratum difficulty.
- **The stratum violation rates** are 15.37% / 19.58%, not 24.3% / 4.7%.

And one qualification the layout did NOT anticipate: **§5.4's claim is statistic-dependent**,
because S_p99 falls for ridge while S_mean rises. The layout's §2-D entry must be amended to
name the conditional mean explicitly.

---

---

## netstudy — case39 — COMPLETE

| field | value |
|---|---|
| phases completed | 1a, 1b, 1c, 1d, 1e |
| elapsed_s | 1578.0 |
| elapsed vs 1-day cap | 0.0548 |
| abandon rule fired | False |
| abandon reason | None |
| seal sha at 1c | 08a53393d147afff254ddefde2d46e50db7e43df018890b54806c0e1708f786a |
| seal sha at 1e | 08a53393d147afff254ddefde2d46e50db7e43df018890b54806c0e1708f786a |
| seal verdict | SEAL INTACT |
| hits | 18/18 |
| mean abs error | 8.866364432770347e-18 |
| max abs error | 5.551115123125783e-17 |
| artifacts | data/netstudy/case39/ |

---

## netstudy — case24_ieee_rts — COMPLETE

| field | value |
|---|---|
| phases completed | 1a, 1b, 1c, 1d, 1e |
| elapsed_s | 1375.0 |
| elapsed vs 1-day cap | 0.0477 |
| abandon rule fired | False |
| abandon reason | None |
| seal sha at 1c | c8e4d70e7e4241b48b407c1e092f5d5a5af8be63aacd433660e6123d393e23a5 |
| seal sha at 1e | c8e4d70e7e4241b48b407c1e092f5d5a5af8be63aacd433660e6123d393e23a5 |
| seal verdict | SEAL INTACT |
| hits | 18/18 |
| mean abs error | 1.5419764230904953e-17 |
| max abs error | 5.551115123125783e-17 |
| artifacts | data/netstudy/case24_ieee_rts/ |

---

## netstudy — case57 — ABANDONED (no feasible range)

| field | value |
|---|---|
| phases completed | 1a |
| elapsed_s | 130.7 |
| elapsed vs 1-day cap | 0.0045 |
| abandon rule fired | True |
| abandon reason | NO FEASIBLE RANGE |
| seal sha at 1c | None |
| seal sha at 1e | None |
| seal verdict | None |
| hits | None |
| mean abs error | None |
| max abs error | None |
| artifacts | data/netstudy/case57/range_sweep.json |

---

## netstudy — Phase 2 + verifier pass

| field | value |
|---|---|
| networks attempted | case39, case24_ieee_rts, case57 |
| networks 4 and 5 | NOT RUN — never named; the prompt's candidate list is truncated at item 3 |
| completed | case39, case24_ieee_rts |
| abandoned | case57 (NO FEASIBLE RANGE, 0.0 acceptance at all 71 sweep candidates) |
| predictions | 36 |
| hits | 36 |
| max abs error | 5.551115123125783e-17 |
| seals | both INTACT; case39 prefix 348 lines, case24 prefix 384 lines |
| floor claim | HOLDS across the attempted set |
| verifier defects fixed in phase2_summary.json | missing exactness note; bogus error_correlations; undocumented ms_solver provenance; seal-region irreproducibility |
| verifier defects NOT fixed | notes/ is git-ignored so no independent timestamp authority exists |


---

## netstudy v1 — VOID AS VALIDATION. Retained, not deleted.

The three blocks above (`netstudy — case39`, `netstudy — case24_ieee_rts`,
`netstudy — case57`) and `data/netstudy/` are **VOID as validation of the escalation
identity**. The arithmetic in them is correct and the seals are intact; what is void is the
claim that 36/36 hits validated anything.

**Why void.** The 1b "prediction" and the 1d "measurement" were computed from the SAME
prediction array over the SAME test rows, so agreement was fixed before either network ran.

| evidence | file:line |
|---|---|
| test rows selected once per seed | `scripts/netstudy.py:309` — `Xte = Xk.iloc[splits["test"]]` |
| that array stored as `pred_test` | `scripts/netstudy.py:319` |
| 1b reads it | `scripts/netstudy.py:334` — `pte = np.asarray(e["pred_test"])` |
| 1b prediction mask | `scripts/netstudy.py:345` — `((pte >= LIMIT) & (pte < LIMIT + q_hat)).mean()` |
| 1d reads the same array | `scripts/netstudy.py:476` — `pred_te, yte = e["pred_test"], e["yte"]` |
| 1d gate mask, after De Morgan on `~(certify \| flag)` | `feasibility/gate_eval.py:19-21` — `(pred >= L) & (pred < L + q_hat)` |
| 1d escalation | `feasibility/gate_eval.py:36` — `float(escalate.mean())` |

`netstudy.py:345` and `gate_eval.py:21` are the same boolean mask. The two quantities are one
expression evaluated twice.

**Measured proof of definitionality, per (family, seed, target), 90 cells per network:**

| comparison | case39 | case24_ieee_rts |
|---|---|---|
| `boundary_mass_pred` vs measured `escalation`, bitwise identical | 90/90 | 90/90 |
| `n_escalated / n_test` vs `boundary_mass_pred`, bitwise identical | 90/90 | 90/90 |
| `identity_escalation` (`F_Lq - F_L`) vs measured, bitwise identical | 32/90 | 35/90 |
| `q_hat` 1b vs 1d, max abs diff | 0.000e+00 | 0.000e+00 |
| test index sets 1b vs 1d | IDENTICAL all 5 seeds | IDENTICAL all 5 seeds |

The reported `max_abs_error` 5.551115123125783e-17 is 2^-54 — the gap between computing
`mean(A & B)` directly and computing `mean(B) - mean(A)`. It is float rounding, not agreement.

**What survives from v1:** the case57 NO FEASIBLE RANGE abandon and its structural-under-voltage
diagnostic (independent of the identity), the four range sweeps and dataset builds, and the
per-network gate artifacts as measurements. **What does not survive:** every hit/miss verdict,
`comparison.json` in each network directory, and `phase2_summary.json`'s headline.

Superseded by netstudy v2 (`data/netstudy2/`), which computes the prediction on the
CALIBRATION split and scores the gate on the disjoint TEST split.


---

## netstudy v2 — case39 — COMPLETE

| field | value |
|---|---|
| phases completed | 1a, 1b, 1c, 2b-seal, 1d, 1e, 2b-compare |
| elapsed_s | 1190.9 |
| elapsed vs 1-day cap (86400s) | 0.0138 |
| abandon fired | False |
| abandon reason | None |
| cal/test disjoint all seeds | True |
| seal sha at 1c | 70d5e0a73572501aaf8d2741984e0cdf1ea255fc9e724004e0406e437d701593 |
| seal verdict at 1e | SEAL INTACT |
| within-network hits (1e) | 17/18 |
| within-network mean abs err | 0.004755417491194148 |
| within-network max abs err | 0.012930423724816287 |
| epsilon alarm | False |
| cross-network prior set (2b) | case118,case30_thermal |
| 2b A mean abs err | 0.047996344909855077 |
| 2b B mean abs err | 0.08186537982347714 |
| 2b B hits | 13/18 |

---

## netstudy v2 — case24_ieee_rts — COMPLETE

| field | value |
|---|---|
| phases completed | 1a, 1b, 1c, 2b-seal, 1d, 1e, 2b-compare |
| elapsed_s | 1469.3 |
| elapsed vs 1-day cap (86400s) | 0.0170 |
| abandon fired | False |
| abandon reason | None |
| cal/test disjoint all seeds | True |
| seal sha at 1c | bd7876c954d6792d0d5959cb51d54c455c3fae94d90906d24a9446d7e3dbaafc |
| seal verdict at 1e | SEAL INTACT |
| within-network hits (1e) | 9/18 |
| within-network mean abs err | 0.010505098220086629 |
| within-network max abs err | 0.01975568464187824 |
| epsilon alarm | False |
| cross-network prior set (2b) | case118,case30_thermal,case39 |
| 2b A mean abs err | 0.28941053971826936 |
| 2b B mean abs err | 0.1659392107297836 |
| 2b B hits | 10/18 |

---

## netstudy v2 — case89pegase — ABANDONED (no feasible range)

| field | value |
|---|---|
| phases completed | none |
| elapsed_s | 167.7 |
| elapsed vs 1-day cap (86400s) | 0.0019 |
| abandon fired | True |
| abandon reason | NO FEASIBLE RANGE in 1a |
| cal/test disjoint all seeds | None |
| seal sha at 1c | None |
| seal verdict at 1e | None |
| within-network hits (1e) | None |
| within-network mean abs err | None |
| within-network max abs err | None |
| epsilon alarm | None |
| cross-network prior set (2b) | None |
| 2b A mean abs err | None |
| 2b B mean abs err | None |
| 2b B hits | None |

---

## netstudy v2 — case_illinois200 — COMPLETE

| field | value |
|---|---|
| phases completed | 1a, 1b, 1c, 2b-seal, 1d, 1e, 2b-compare |
| elapsed_s | 17312.0 |
| elapsed vs 1-day cap (86400s) | 0.2004 |
| abandon fired | False |
| abandon reason | None |
| cal/test disjoint all seeds | True |
| seal sha at 1c | bc88ed393644a33b70248c9bc511329855de725636e53b75e5f068c44bbde427 |
| seal verdict at 1e | SEAL INTACT |
| within-network hits (1e) | 17/18 |
| within-network mean abs err | 0.003108051639171215 |
| within-network max abs err | 0.015609070269174075 |
| epsilon alarm | False |
| cross-network prior set (2b) | case118,case24_ieee_rts,case30_thermal,case39 |
| 2b A mean abs err | 0.011511804577285388 |
| 2b B mean abs err | 0.06903164785111085 |
| 2b B hits | 18/18 |
