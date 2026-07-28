"""Mechanical consistency checker for paper_current.tex against the committed data artifacts.

Every numeric literal in the paper body must trace to a value in some data/*.json file. This
script extracts those literals, matches them against a value->(file, jsonpath) provenance map
built from the artifacts, and reports MATCHED / ORPHAN / AMBIGUOUS / HARD_FAIL. It also fails on
a hardcoded list of killed numbers, on banned phrases, and on broken cross-references.

Usage:
    .venv/bin/python scripts/check_paper.py paper_current.tex          human report, exit 0/1
    .venv/bin/python scripts/check_paper.py paper_current.tex --json   machine-readable failures
    .venv/bin/python scripts/check_paper.py paper_current.tex --update-provenance   rewrite the map

Read-only on every data/ file except data/paper_provenance.json, which is written ONLY with
--update-provenance. A plain run reports without writing; --json never writes.
"""

import os
import re
import sys
import glob
import json
import argparse
import datetime


# --- killed numbers -----------------------------------------------------------------------------
# No machine-readable killed-numbers file exists in notes/; these are hardcoded here and mirror
# notes/handoff-2026-08.md section 4 (the case57 "30.65" boundary mass and the "0.057 pu" depth,
# both unsourced) plus the four review-flagged context-gated kills. Maintain this list here.
KILLED_UNCONDITIONAL = [
    {"label": "30.65", "regex": r"(?<![\d.])30\.65(?![\d])",
     "why": "case57 boundary-mass figure, never computed from data (handoff s4)"},
    {"label": "0.057", "regex": r"(?<![\d.])0\.057(?![\d])",
     "why": "case57 depth over-prediction, unsourced (handoff s4)"},
]
KILLED_GATED = [
    {"label": "6.4", "regex": r"(?<![\d.])6\.4(?![\d])", "keywords": ["boundary", "mass"],
     "why": "6.4 as a boundary-mass figure"},
    {"label": "7.2", "regex": r"(?<![\d.])7\.2(?![\d])", "keywords": ["speedup", "faster", "throughput"],
     "why": "7.2 as a speedup"},
    {"label": "87", "regex": r"(?<![\d.])87(?![\d.])", "keywords": ["accept"],
     "why": "87 as an acceptance rate"},
    {"label": "0.75", "regex": r"(?<![\d.])0\.75(?![\d])", "keywords": ["violation"],
     "why": "0.75 as a violation rate"},
]

# --- banned phrases (case-insensitive) ----------------------------------------------------------
PHRASE_REGEXES = [
    r"\bany surrogate\b",
    r"\bprove[sn]?\b",
    r"\bfirst to\b",
    r"\bnovel\b",
    r"subtract.*savings",
    r"computation speed of the model",
    r"lands on the saturation",
    r"escalation floor",
    r"must be safe on every case",
]

# --- leftover authoring tags (case-sensitive) ---------------------------------------------------
LEFTOVER_TAGS = ["TODO", "GRAPHIC_TOOL", "SEVENTEEN", "AI_DISCLOSURE", "FIXME"]

# The single jsonpath field that carries the killed 30.65; any paper literal resolving here is a
# hard fail, not an ambiguity.
HARD_FAIL_FILE = "quintile_boundary_mass.json"
HARD_FAIL_PATH = "step3_top_quintile_vs_case57.case57_boundary_mass_pct"


def strip_line_comment(line):
    """Return the line up to the first unescaped LaTeX comment percent sign."""
    i = 0
    while i < len(line):
        if line[i] == "%" and (i == 0 or line[i - 1] != "\\"):
            return line[:i]
        i += 1
    return line


def strip_commands(text):
    """Remove the arguments of commands that carry no data numbers, so their contents (citation
    keys, label names, image paths, column specs, glue lengths) are not scanned as literals."""
    text = re.sub(r"\\includegraphics(\[[^\]]*\])?\{[^}]*\}", " ", text)
    text = re.sub(r"\\(cite|ref|label|eqref|autoref)\{[^}]*\}", " ", text)
    text = re.sub(r"\\setlength\{[^}]*\}\{[^}]*\}", " ", text)
    text = re.sub(r"\\begin\{tabular\}\{[^}]*\}", " ", text)
    text = re.sub(r"\\usepackage(\[[^\]]*\])?\{[^}]*\}", " ", text)
    return text


def get_body_lines(tex_text):
    """Split into (line_number, cleaned_text) pairs for the paper body, dropping comment lines,
    the whole thebibliography environment, and the \\begin{thebibliography}{N} boundary line."""
    out = []
    in_bib = False
    for n, raw in enumerate(tex_text.splitlines(), start=1):
        line = strip_line_comment(raw)
        if "\\begin{thebibliography}" in line:
            in_bib = True
            continue
        if "\\end{thebibliography}" in line:
            in_bib = False
            continue
        if in_bib:
            continue
        out.append((n, strip_commands(line)))
    return out


def normalize_thousands(text):
    """Turn LaTeX and plain thousands separators into bare digits: 1{,}500 and 1,500 -> 1500,
    and drop N-k contingency labels (N-0, N-1, N-2, N-k) so their digits are not read as data."""
    text = text.replace("{,}", "")
    text = re.sub(r"(?<=\d),(?=\d\d\d(?!\d))", "", text)
    text = re.sub(r"N-[0-9k]", " ", text)
    return text


def decimals_in(literal):
    """Number of digits the paper printed after the decimal point (0 for an integer literal)."""
    if "." in literal:
        return len(literal.split(".", 1)[1])
    return 0


def extract_literals(tex_text):
    """Return a dict: literal_string -> {'value': float, 'lines': [ints], 'decimals': int}.
    Aggregated across occurrences so a value that appears many times is reported once."""
    lits = {}
    for n, line in get_body_lines(tex_text):
        clean = normalize_thousands(line)
        for m in re.finditer(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w])", clean):
            s = m.group(1)
            if s not in lits:
                lits[s] = {"value": float(s), "lines": [], "decimals": decimals_in(s)}
            if n not in lits[s]["lines"]:
                lits[s]["lines"].append(n)
    return lits


def walk_json(obj, path, out):
    """Append (numeric_value, jsonpath) for every number leaf; bools are not treated as numbers."""
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        out.append((float(obj), path))
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk_json(v, f"{path}.{k}" if path else str(k), out)
        return
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            walk_json(v, f"{path}[{i}]", out)


def load_artifacts(data_dir):
    """Return a list of records {value, file, jsonpath, network}. Skips *.manifest.json and the
    provenance file itself; skips files that fail to parse (reported to stderr)."""
    records = []
    for fpath in sorted(glob.glob(os.path.join(data_dir, "*.json"))):
        fname = os.path.basename(fpath)
        if fname.endswith(".manifest.json") or fname == "paper_provenance.json":
            continue
        try:
            with open(fpath) as fh:
                obj = json.load(fh)
        except (ValueError, OSError) as e:
            sys.stderr.write(f"warning: could not parse {fname}: {e}\n")
            continue
        leaves = []
        walk_json(obj, "", leaves)
        for value, jsonpath in leaves:
            records.append({
                "value": value,
                "file": fname,
                "jsonpath": jsonpath,
                "network": classify_network(fname, jsonpath),
            })
    return records


def classify_network(fname, jsonpath):
    """Map a (file, jsonpath) source to its network. A jsonpath naming a network overrides the
    filename (so a case118_comparators block inside case30_frozen.json reads as case118, and a
    case57 field inside a case118 file reads as case57)."""
    p = jsonpath.lower()
    if "case57" in p:
        return "case57"
    if "case30" in p:
        return "case30"
    if "case118" in p:
        return "case118"
    f = fname.lower()
    if "case57" in f:
        return "case57"
    if "case30" in f:
        return "case30"
    return "case118"


def value_matches(literal_value, decimals, json_value):
    """True if the artifact value equals the printed literal at one of the two unit scales
    (same units, or fraction-stored-percent-printed). Integer literals require an exact value
    (a count), not a rounded float; decimal literals round the artifact to the paper's printed
    precision. Returns the scale that matched, or None. The 0.01 scale is deliberately omitted:
    the paper never prints a value one-hundredth of a stored one, and allowing it made killed
    percentages round onto innocent small paper numbers."""
    for scale in (1.0, 100.0):
        scaled = json_value * scale
        if decimals == 0:
            if abs(scaled - literal_value) < 1e-9:
                return scale
        elif round(scaled, decimals) == literal_value:
            return scale
    return None


def match_literals(literals, records):
    """For each literal, find every artifact record it matches and assign a status."""
    results = []
    for s in sorted(literals, key=lambda x: literals[x]["value"]):
        info = literals[s]
        sources = []
        for rec in records:
            scale = value_matches(info["value"], info["decimals"], rec["value"])
            if scale is not None:
                sources.append({
                    "file": rec["file"],
                    "jsonpath": rec["jsonpath"],
                    "network": rec["network"],
                    "artifact_value": rec["value"],
                    "scale": scale,
                })
        # Hard-fail only when the killed case57 field is the SOLE source. A paper number that also
        # traces to a legitimate field (e.g. 30.6 = histgb escalation, which merely rounds the same
        # as the killed 30.65 at one decimal) is not the killed number and must not be condemned.
        on_killed_field = [src for src in sources
                           if src["file"] == HARD_FAIL_FILE and src["jsonpath"] == HARD_FAIL_PATH]
        other_sources = [src for src in sources if src not in on_killed_field]
        hard = bool(on_killed_field) and not other_sources
        networks = sorted(set(src["network"] for src in sources))
        if hard:
            status = "HARD_FAIL"
        elif not sources:
            status = "ORPHAN"
        elif len(networks) > 1:
            status = "AMBIGUOUS"
        else:
            status = "MATCHED"
        results.append({
            "literal": s,
            "value": info["value"],
            "lines": info["lines"],
            "status": status,
            "networks": networks,
            "sources": sources,
        })
    return results


def find_sentences(tex_text):
    """Comment-stripped, command-stripped body as a list of sentences for same-sentence gating."""
    body = " ".join(line for _, line in get_body_lines(tex_text))
    body = re.sub(r"\s+", " ", body)
    return re.split(r"(?<=[.])\s+", body)


def check_killed(tex_text):
    """Return a list of killed-number hits: unconditional anywhere, gated on a same-sentence keyword."""
    hits = []
    body = " ".join(line for _, line in get_body_lines(tex_text))
    for k in KILLED_UNCONDITIONAL:
        if re.search(k["regex"], body):
            hits.append({"label": k["label"], "why": k["why"], "gated": False})
    sentences = find_sentences(tex_text)
    for k in KILLED_GATED:
        for sent in sentences:
            if re.search(k["regex"], sent) and any(w in sent.lower() for w in k["keywords"]):
                hits.append({"label": k["label"], "why": k["why"], "gated": True,
                             "sentence": sent.strip()[:160]})
                break
    return hits


def check_phrases(tex_text):
    """Return banned-phrase and leftover-tag hits with their line numbers."""
    hits = []
    lines = [(n, strip_line_comment(raw)) for n, raw in enumerate(tex_text.splitlines(), start=1)]
    for pat in PHRASE_REGEXES:
        rx = re.compile(pat, re.IGNORECASE)
        for n, line in lines:
            if rx.search(line):
                hits.append({"kind": "phrase", "pattern": pat, "line": n})
    for tag in LEFTOVER_TAGS:
        for n, line in lines:
            if tag in line:
                hits.append({"kind": "tag", "pattern": tag, "line": n})
    return hits


def check_structure(tex_text, root):
    """Cross-reference, bibliography-count, and figure-path checks."""
    problems = []
    cited = set()
    for m in re.finditer(r"\\cite\{([^}]*)\}", tex_text):
        for key in m.group(1).split(","):
            if key.strip():
                cited.add(key.strip())
    bibkeys = set(re.findall(r"\\bibitem\{([^}]*)\}", tex_text))
    for key in sorted(cited - bibkeys):
        problems.append({"kind": "unresolved_cite", "key": key})

    labels = set(re.findall(r"\\label\{([^}]*)\}", tex_text))
    refs = set()
    for m in re.finditer(r"\\(?:ref|eqref|autoref)\{([^}]*)\}", tex_text):
        refs.add(m.group(1).strip())
    for key in sorted(refs - labels):
        problems.append({"kind": "unresolved_ref", "key": key})

    decl = re.search(r"\\begin\{thebibliography\}\{(\d+)\}", tex_text)
    n_bibitem = len(re.findall(r"\\bibitem\{", tex_text))
    if decl:
        n_decl = int(decl.group(1))
        if n_decl != n_bibitem:
            problems.append({"kind": "bib_count", "declared": n_decl, "actual": n_bibitem})

    for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", tex_text):
        rel = m.group(1)
        if not os.path.exists(os.path.join(root, rel)):
            problems.append({"kind": "missing_graphic", "path": rel})
    return problems


def build_report(tex_path):
    """Run every check and return the full result dict."""
    root = os.path.dirname(os.path.abspath(tex_path))
    data_dir = os.path.join(root, "data")
    with open(tex_path) as fh:
        tex_text = fh.read()

    literals = extract_literals(tex_text)
    records = load_artifacts(data_dir)
    matched = match_literals(literals, records)

    orphans = [r for r in matched if r["status"] == "ORPHAN"]
    ambiguous = [r for r in matched if r["status"] == "AMBIGUOUS"]
    hard = [r for r in matched if r["status"] == "HARD_FAIL"]
    ok = [r for r in matched if r["status"] == "MATCHED"]

    killed = check_killed(tex_text)
    phrases = check_phrases(tex_text)
    structural = check_structure(tex_text, root)

    failing = bool(orphans) or bool(hard) or bool(killed) or bool(phrases) or bool(structural)
    return {
        "tex": tex_path,
        "data_dir": data_dir,
        "n_artifacts": len(set(rec["file"] for rec in records)),
        "n_records": len(records),
        "literals": matched,
        "matched": ok,
        "orphans": orphans,
        "ambiguous": ambiguous,
        "hard_fail": hard,
        "killed": killed,
        "phrases": phrases,
        "structural": structural,
        "exit": 1 if failing else 0,
    }


def write_provenance(report, data_dir):
    """Write the full literal->sources map and a manifest beside it. Called only for
    --update-provenance."""
    out_path = os.path.join(data_dir, "paper_provenance.json")
    payload = {
        "generated_from": os.path.basename(report["tex"]),
        "n_artifacts_scanned": report["n_artifacts"],
        "n_numeric_leaves": report["n_records"],
        "status_counts": {
            "matched": len(report["matched"]),
            "orphan": len(report["orphans"]),
            "ambiguous": len(report["ambiguous"]),
            "hard_fail": len(report["hard_fail"]),
        },
        "literals": report["literals"],
    }
    with open(out_path, "w") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")
    manifest = {
        "artifact": "data/paper_provenance.json",
        "generator": "scripts/check_paper.py",
        "source_tex": os.path.basename(report["tex"]),
        "written": datetime.datetime.now().isoformat(timespec="seconds"),
        "n_artifacts_scanned": report["n_artifacts"],
        "note": "Numeric provenance map for the paper; regenerate with --update-provenance. "
                "Derived artifact, not a frozen result.",
    }
    with open(os.path.join(data_dir, "paper_provenance.manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    return out_path


def print_report(report):
    """Human-readable report to stdout."""
    print(f"paper: {report['tex']}")
    print(f"artifacts scanned: {report['n_artifacts']} files, {report['n_records']} numeric leaves")
    print(f"literals: {len(report['literals'])} distinct "
          f"({len(report['matched'])} matched, {len(report['orphans'])} orphan, "
          f"{len(report['ambiguous'])} ambiguous, {len(report['hard_fail'])} hard-fail)")

    if report["hard_fail"]:
        print("\n== HARD FAIL (killed field) ==")
        for r in report["hard_fail"]:
            print(f"  {r['literal']}  lines {r['lines']}  -> {HARD_FAIL_FILE}:{HARD_FAIL_PATH}")

    if report["killed"]:
        print("\n== KILLED NUMBERS ==")
        for k in report["killed"]:
            tag = "gated" if k["gated"] else "unconditional"
            print(f"  {k['label']} ({tag}): {k['why']}")
            if k.get("sentence"):
                print(f"    in: {k['sentence']}")

    if report["phrases"]:
        print("\n== PHRASE / TAG REGRESSIONS ==")
        for h in report["phrases"]:
            print(f"  line {h['line']}  {h['kind']}: {h['pattern']}")

    if report["structural"]:
        print("\n== STRUCTURAL ==")
        for p in report["structural"]:
            print(f"  {p}")

    if report["ambiguous"]:
        print("\n== AMBIGUOUS (matches >1 network; warning, does not fail) ==")
        print("   (full per-source detail is in data/paper_provenance.json)")
        for r in report["ambiguous"]:
            nets = ",".join(r["networks"])
            print(f"  {r['literal']:>10s}  lines {r['lines']}  networks: {nets}  ({len(r['sources'])} sources)")

    if report["orphans"]:
        print("\n== ORPHANS (no artifact contains this value) ==")
        for r in report["orphans"]:
            print(f"  {r['literal']:>10s}  lines {r['lines']}")

    print(f"\nexit {report['exit']}")


def main():
    parser = argparse.ArgumentParser(description="Check paper_current.tex against data/*.json.")
    parser.add_argument("tex", help="path to the .tex file")
    parser.add_argument("--json", action="store_true", help="machine-readable failure list; never writes")
    parser.add_argument("--update-provenance", action="store_true",
                        help="rewrite data/paper_provenance.json and its manifest")
    args = parser.parse_args()

    if not os.path.exists(args.tex):
        sys.stderr.write(f"error: no such file: {args.tex}\n")
        return 2

    report = build_report(args.tex)

    if args.update_provenance and not args.json:
        path = write_provenance(report, report["data_dir"])
        print(f"wrote {path} (+ manifest)")

    if args.json:
        out = {
            "exit": report["exit"],
            "orphans": [{"literal": r["literal"], "lines": r["lines"]} for r in report["orphans"]],
            "ambiguous": [{"literal": r["literal"], "lines": r["lines"], "networks": r["networks"]}
                          for r in report["ambiguous"]],
            "hard_fail": [{"literal": r["literal"], "lines": r["lines"]} for r in report["hard_fail"]],
            "killed": report["killed"],
            "phrases": report["phrases"],
            "structural": report["structural"],
        }
        print(json.dumps(out, indent=2))
    else:
        print_report(report)

    return report["exit"]


if __name__ == "__main__":
    sys.exit(main())
