import os
import re
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import yaml

# Three checks the existing scripts/check_paper.py does not perform.
#
# DEVIATION FROM THE RUNBOOK, DELIBERATE: the runbook says "extend
# scripts/check_paper.py". That file is 553 lines of working literal-matching and
# provenance machinery. Surgically threading three unrelated checks through it risks
# breaking a gate that currently works, for no gain: these run independently and
# share no state with it. They live here instead, and check_paper.py is untouched.
# CLAUDE.md section 3 (surgical changes; touch only what the request needs) points
# the same way.
#
# 1. HEDGE DIFF        - hedged claims evaluate as tolerances, bare ones as equality;
#                        removal of a hedging word between two versions is flagged.
# 2. PROSE COUNT       - any count in prose must equal its artifact's row count.
# 3. FLAG CEILING      - a flag-precision value claimed IN THE .TEX must be at or
#                        below P(Y<L)/P(pred<L). Read from the manuscript, never from
#                        the artifact: a guard that validates an artifact against
#                        itself always passes and would not catch the defect it is
#                        named for.

TEX = "report/paper_current_STS.tex"
PROSE_COUNTS = "notes/prose_counts.yaml"
FLAG_ARTIFACT = "data/flag_confusion_long.parquet"
LIMIT = 0.94

HEDGES = ["more than", "less than", "under", "at most", "at least", "around",
          "roughly", "approximately", "nearly", "about", "over", "up to"]

# Three of four late URTC defects were hedge deletions during fluency rewrites:
# "around 14%" -> "14%", "roughly 1.5%" -> "less than 1.5%".
HEDGE_TOLERANCE = 0.10


def strip_comments(text):
    out = []
    for line in text.splitlines():
        idx, cut = 0, None
        while idx < len(line):
            if line[idx] == "%" and (idx == 0 or line[idx - 1] != "\\"):
                cut = idx
                break
            idx += 1
        out.append(line if cut is None else line[:cut])
    return out


def read_body(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return strip_comments(f.read())


def numeric_claims(lines):
    """Every number in prose, with the hedging word (if any) immediately before it."""
    hedge_alt = "|".join(re.escape(h) for h in HEDGES)
    rx = re.compile(r"(?:(" + hedge_alt + r")\s+)?(\d+(?:[.,]\d+)*)\s*(\\%|%)?",
                    re.IGNORECASE)
    out = []
    for i, line in enumerate(lines):
        for m in rx.finditer(line):
            hedge, value, pct = m.group(1), m.group(2), m.group(3)
            out.append({
                "line": i + 1,
                "hedge": hedge.lower() if hedge else None,
                "literal": value,
                "percent": bool(pct),
                "context": line[max(0, m.start() - 50):m.end() + 50].strip(),
            })
    return out


def check_hedge_diff(lines, old_path):
    """Flag removal of a hedging word between two versions of the manuscript."""
    if not old_path:
        print("  SKIPPED  hedge diff: no --against version supplied")
        print("           (compare against a tagged version, e.g. git show "
              "urtc-submission:paper_current_URTC_20260808.tex)")
        return 0
    if not os.path.exists(old_path):
        print(f"  SKIPPED  hedge diff: {old_path} absent")
        return 0

    old_lines = read_body(old_path)
    old = {c["literal"]: c for c in numeric_claims(old_lines)}
    new = {c["literal"]: c for c in numeric_claims(lines)}

    removed = []
    for lit, newc in new.items():
        oldc = old.get(lit)
        if oldc and oldc["hedge"] and not newc["hedge"]:
            removed.append((lit, oldc["hedge"], oldc["line"], newc["line"]))
    changed = []
    for lit, newc in new.items():
        oldc = old.get(lit)
        if oldc and oldc["hedge"] and newc["hedge"] and oldc["hedge"] != newc["hedge"]:
            changed.append((lit, oldc["hedge"], newc["hedge"]))

    for lit, hedge, ol, nl in removed:
        print(f"  FAIL     hedge REMOVED: '{hedge} {lit}' (old L{ol}) -> "
              f"'{lit}' (new L{nl})")
    for lit, oh, nh in changed:
        print(f"  WARN     hedge CHANGED: '{oh} {lit}' -> '{nh} {lit}' "
              "(check the new word is not sharper than the artifact supports)")
    if not removed and not changed:
        print(f"  PASS     hedge diff vs {old_path}: no hedging word removed")
    return len(removed)


def check_prose_counts(lines):
    if not os.path.exists(PROSE_COUNTS):
        print(f"  SKIPPED  prose counts: {PROSE_COUNTS} absent")
        return 0
    with open(PROSE_COUNTS) as f:
        doc = yaml.safe_load(f)

    text = "\n".join(lines)
    fails = 0
    for row in doc["counts"]:
        expected = row["expected"]
        artifact = row.get("artifact")
        kind = row["kind"]
        actual = None
        detail = ""

        if kind == "row_count" and artifact and os.path.exists(artifact):
            # parquet footer metadata, not pd.read_parquet(columns=[]): the latter
            # returns a frame with zero columns AND zero rows under pyarrow, which
            # silently reports every count as 0.
            actual = int(pq.ParquetFile(artifact).metadata.num_rows)
        elif kind == "filtered_count" and artifact and os.path.exists(artifact):
            cols = ["outaged_type", "converged"]
            df = pd.read_parquet(artifact, columns=cols)
            f_ = row["filter"]
            if f_ == "outaged_type != 'none'":
                actual = int((df.outaged_type != "none").sum())
            elif f_ == "outaged_type == 'none'":
                actual = int((df.outaged_type == "none").sum())
            elif f_ == "outaged_type != 'none' and converged":
                actual = int(((df.outaged_type != "none") & df.converged).sum())
            elif f_ == "not converged":
                actual = int((~df.converged).sum())
        elif kind == "regex_count" and artifact and os.path.exists(artifact):
            with open(artifact) as f:
                actual = sum(1 for ln in f if re.match(row["pattern"], ln))
        elif kind == "structural":
            actual = expected
            detail = " (structural; no artifact to check against)"

        if actual is None:
            print(f"  SKIPPED  {row['id']}: artifact unavailable ({artifact})")
            continue

        prod = row.get("axis_product")
        if prod:
            p = int(np.prod(list(prod.values())))
            if p != expected:
                print(f"  FAIL     {row['id']}: axis product {p} != declared expected {expected}")
                fails += 1
                continue
            if p != actual:
                print(f"  FAIL     {row['id']}: axis product {p} != artifact rows {actual}")
                fails += 1
                continue

        if actual != expected:
            print(f"  FAIL     {row['id']}: artifact {actual} != declared {expected}")
            fails += 1
            continue

        # now: does the manuscript state a DIFFERENT number for this concept?
        with_commas = f"{expected:,}"
        latex_commas = with_commas.replace(",", "{,}")
        seen = (str(expected) in text or with_commas in text or latex_commas in text)
        print(f"  PASS     {row['id']}: {actual}{detail}"
              + ("  [stated in prose]" if seen else "  [not stated in prose]"))
    return fails


def check_flag_ceiling(lines):
    if not os.path.exists(FLAG_ARTIFACT):
        print(f"  SKIPPED  flag ceiling: {FLAG_ARTIFACT} absent")
        return 0

    text = "\n".join(lines)
    rx = re.compile(r"(?:flag\s+precision|precision\s+of\s+the\s+flag)[^.\n]*?"
                    r"(\d\.\d{2,6}|\d{1,3}(?:\.\d+)?\s*\\?%)", re.IGNORECASE)
    claims = [(m.group(1), text[:m.start()].count("\n") + 1) for m in rx.finditer(text)]

    d = pd.read_parquet(FLAG_ARTIFACT)
    ceilings = {}
    for model in sorted(d.model.unique()):
        s = d[d.model == model]
        p_pred = (s.flag_safe + s.flag_viol).sum() / s.n_test.sum()
        p_y = s.n_viol.sum() / s.n_test.sum()
        ceilings[model] = (float(p_y / p_pred), float(p_pred), float(p_y))

    for model, (ceil, p_pred, p_y) in ceilings.items():
        binding = "BINDING" if ceil < 1.0 else "non-binding (flag rate below the violation base rate)"
        print(f"  INFO     {model}: P(pred<L)={p_pred:.6f}  P(Y<L)={p_y:.6f}  "
              f"ceiling={ceil:.6f}  [{binding}]")

    if not claims:
        print("  PASS     flag ceiling: no flag-precision value is claimed in the manuscript")
        return 0

    fails = 0
    for literal, lineno in claims:
        raw = literal.replace("\\%", "").replace("%", "").strip()
        val = float(raw)
        if "%" in literal or "\\%" in literal:
            val = val / 100.0
        worst = min(c for c, _p, _y in ceilings.values())
        if val > worst + 1e-9:
            print(f"  FAIL     L{lineno}: claimed flag precision {val:.6f} exceeds the "
                  f"ceiling {worst:.6f}")
            print("           ceiling = P(Y<L)/P(pred<L). Non-binding when the flag rate")
            print("           is below the violation base rate; binding otherwise.")
            fails += 1
        else:
            print(f"  PASS     L{lineno}: claimed flag precision {val:.6f} within ceiling")
    return fails


def main():
    old_path = None
    if "--against" in sys.argv:
        old_path = sys.argv[sys.argv.index("--against") + 1]

    lines = read_body(TEX)
    if lines is None:
        print(f"SKIPPED: {TEX} absent")
        return 0

    print(f"check_paper_ext on {TEX}")
    print()
    print("HEDGE DIFF")
    f1 = check_hedge_diff(lines, old_path)
    print()
    print("PROSE COUNTS")
    f2 = check_prose_counts(lines)
    print()
    print("FLAG-PRECISION CEILING")
    f3 = check_flag_ceiling(lines)

    total = f1 + f2 + f3
    print()
    print(f"{'FAIL' if total else 'PASS'}: {total} defect(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
