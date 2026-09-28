"""Read-only: run scripts/check_paper.py matching on the STS tex against data/ AND its subdirs.

check_paper.build_report() looks for data/ beside the tex (report/data, which does not exist) and
only globs data/*.json, so it misses data/netstudy2/ and data/case30_thermal/. This wrapper reuses
its functions with the real directories. Writes nothing.

Usage: .venv/bin/python scratch/provenance_sts.py
"""

import os
import sys
import glob

sys.path.insert(0, "scripts")
import check_paper

TEX = "report/paper_current_STS.tex"
DIRS = ["data", "data/netstudy2", "data/netstudy", "data/case30_thermal"]


def all_dirs():
    out = list(DIRS)
    for d in glob.glob("data/netstudy2/*/") + glob.glob("data/netstudy/*/"):
        out.append(d.rstrip("/"))
    return out


if __name__ == "__main__":
    with open(TEX) as fh:
        tex_text = fh.read()
    records = []
    for d in all_dirs():
        records = records + check_paper.load_artifacts(d)
    literals = check_paper.extract_literals(tex_text)
    matched = check_paper.match_literals(literals, records)
    print(f"artifact files: {len(set(r['file'] for r in records))}, leaves: {len(records)}")
    counts = {}
    for r in matched:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(counts)
    print("\n== ORPHANS ==")
    for r in matched:
        if r["status"] == "ORPHAN":
            print(f"  {r['literal']:>12s}  lines {r['lines']}")
    print("\n== AMBIGUOUS ==")
    for r in matched:
        if r["status"] == "AMBIGUOUS":
            print(f"  {r['literal']:>12s}  lines {r['lines']}  nets {r['networks']}")
    print("\n== SPECIFIC MATCHES (first source) ==")
    for r in matched:
        if r["status"] == "MATCHED" and r["specific"]:
            s = r["sources"][0]
            print(f"  {r['literal']:>12s}  lines {r['lines']}  -> {s}")
