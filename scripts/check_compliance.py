import os
import re
import sys

import yaml

CONSTRAINTS = "notes/sts-constraints.yaml"
TEX = "report/paper_current_STS.tex"

PAGE_CAP = 20
FONT_FLOOR_PT = 10

PASS = "PASS"
FAIL = "FAIL"
SKIPPED = "SKIPPED"
MANUAL = "MANUAL"


def read_constraints(path):
    with open(path) as f:
        return yaml.safe_load(f)


def read_tex(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return f.read()


def strip_comments(text):
    out = []
    for line in text.splitlines():
        idx = 0
        cut = None
        while idx < len(line):
            if line[idx] == "%" and (idx == 0 or line[idx - 1] != "\\"):
                cut = idx
                break
            idx += 1
        out.append(line if cut is None else line[:cut])
    return "\n".join(out)


def check_font_floor(tex):
    m = re.search(r"\\documentclass\[([^\]]*)\]", tex)
    if not m:
        return FAIL, "no \\documentclass options found; point size undeclared"
    sizes = re.findall(r"(\d+)pt", m.group(1))
    if not sizes:
        return FAIL, f"\\documentclass[{m.group(1)}] declares no point size"
    pt = int(sizes[0])
    if pt < FONT_FLOOR_PT:
        return FAIL, f"body font {pt}pt is below the {FONT_FLOOR_PT}pt floor"
    return PASS, f"body font {pt}pt >= {FONT_FLOOR_PT}pt floor (floor itself is status: verify)"


def check_layout_packages(tex):
    wanted = {
        "geometry margin=1in": r"\\usepackage\[[^\]]*margin=1in[^\]]*\]\{geometry\}",
        "setspace": r"\\usepackage\{setspace\}",
        "onehalfspacing": r"\\onehalfspacing|\\setstretch",
        "Times (newtx)": r"\\usepackage\{newtxtext,newtxmath\}|\\usepackage\{times\}|\\usepackage\{mathptmx\}",
    }
    missing = [name for name, rx in wanted.items() if not re.search(rx, tex)]
    if missing:
        return FAIL, "missing layout declarations: " + ", ".join(missing)
    twocol = re.search(r"\\documentclass\[[^\]]*twocolumn|\\twocolumn", tex)
    if twocol:
        return FAIL, "document declares two-column layout"
    return PASS, "single column, 1in margins, setspace, Times family all declared"


def check_no_external_links(tex):
    body = strip_comments(tex)
    bib_start = body.find(r"\begin{thebibliography}")
    pre = body if bib_start < 0 else body[:bib_start]
    post = "" if bib_start < 0 else body[bib_start:]
    rx = r"\\url\{[^}]*\}|https?://[^\s{}]+"
    outside = re.findall(rx, pre)
    inside = re.findall(rx, post)
    if outside:
        return FAIL, (f"{len(outside)} external link(s) OUTSIDE the bibliography: "
                      + "; ".join(outside[:5]))
    if inside:
        return MANUAL, (f"{len(inside)} link(s) inside the bibliography only. "
                        "R09 is status: ask - whether bibliography URLs are permitted "
                        "is unresolved, so this cannot be scored")
    return PASS, "no external links anywhere"


def check_no_contact_details(tex):
    body = strip_comments(tex)
    m = re.search(r"\\maketitle", body)
    head = body[:m.start()] if m else body[:4000]
    emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", head)
    phones = re.findall(r"\+?\d[\d\s().-]{8,}\d", head)
    problems = []
    if emails:
        problems.append(f"email(s): {emails}")
    if phones:
        problems.append(f"phone-like string(s): {phones}")
    if problems:
        return FAIL, "; ".join(problems)
    return PASS, "no emails or phone numbers before \\maketitle"


def check_apa_beneath_floats(tex):
    body = strip_comments(tex)
    # finditer, not findall: findall with a capturing group returns the GROUP, so
    # `block` would be the bare word "figure"/"table" and every float would look
    # unlabelled. That bug reported 6 of 6 floats missing an APA line for the wrong
    # reason on the first run.
    floats = [(m.group(1), m.group(0))
              for m in re.finditer(r"\\begin\{(figure|table)\}.*?\\end\{\1\}", body, re.S)]
    if not floats:
        return SKIPPED, "no float environments found"
    missing = []
    for kind, block in floats:
        label = re.search(r"\\label\{([^}]*)\}", block)
        name = label.group(1) if label else "<unlabelled>"
        if not re.search(r"\\apacite|APA:|\(\d{4}\)\.", block):
            missing.append(f"{kind} {name}")
    if missing:
        return FAIL, (f"{len(missing)} of {len(floats)} floats carry no APA line: "
                      + ", ".join(missing))
    return PASS, f"all {len(floats)} floats carry an APA line"


def check_page_count(tex):
    return SKIPPED, ("page count needs a compiled PDF; no TeX toolchain on PATH "
                     "(pdflatex/xelatex/latexmk all absent). Appendices count toward "
                     f"the {PAGE_CAP}-page cap; title page, abstract and bibliography do not")


def check_pagination(tex):
    return SKIPPED, "pagination needs a compiled PDF; no TeX toolchain on PATH"


def check_pdf_size_and_name(tex):
    return SKIPPED, ("needs a built PDF and the home ZIP code. The ZIP is NOT recorded "
                     "in this repository and must not be guessed; filename must be "
                     "SAHA.RAJAN.<home zip>")


def check_citations_resolve(tex):
    return MANUAL, "delegated to scripts/check_citations.py"


def check_authorship_boundary(tex):
    hooks = [
        ".claude/hooks/guard_report_prose.sh",
        ".claude/hooks/guard_report_bash.sh",
    ]
    missing = [h for h in hooks if not os.path.exists(h)]
    if missing:
        return FAIL, "authorship-boundary hook(s) absent: " + ", ".join(missing)
    settings_path = ".claude/settings.json"
    if not os.path.exists(settings_path):
        return FAIL, "no .claude/settings.json; hooks exist but are not registered"
    with open(settings_path) as f:
        raw = f.read()
    unregistered = [h for h in hooks if os.path.basename(h) not in raw]
    if unregistered:
        return FAIL, "hook(s) present but not registered in settings.json: " + ", ".join(unregistered)
    return PASS, "both authorship-boundary hooks present and registered"


CHECKS = {
    "font_floor": check_font_floor,
    "layout_packages": check_layout_packages,
    "no_external_links": check_no_external_links,
    "no_contact_details": check_no_contact_details,
    "apa_beneath_floats": check_apa_beneath_floats,
    "page_count": check_page_count,
    "pagination": check_pagination,
    "pdf_size_and_name": check_pdf_size_and_name,
    "citations_resolve": check_citations_resolve,
    "authorship_boundary": check_authorship_boundary,
}


def status_defect(row):
    """A confirmed row with no date_checked is itself a defect."""
    if row.get("status") == "confirmed" and not row.get("date_checked"):
        return "status is 'confirmed' but date_checked is empty"
    if row.get("status") in ("contradicted", "n/a") and not row.get("note"):
        return f"status is '{row['status']}' but note is empty"
    return None


def main():
    if not os.path.exists(CONSTRAINTS):
        print(f"FAIL: {CONSTRAINTS} absent")
        return 1
    doc = read_constraints(CONSTRAINTS)
    tex = read_tex(TEX)

    print(f"compliance gate against {CONSTRAINTS}")
    print(f"manuscript: {TEX}" + ("" if tex else "  [ABSENT]"))
    print(f"2027 rules book present: {doc['meta'].get('rules_book_2027_present')}")
    print()

    counts = {PASS: 0, FAIL: 0, SKIPPED: 0, MANUAL: 0}
    hard_fail = 0

    for row in doc["rules"]:
        rid = row["id"]
        defect = status_defect(row)
        if defect:
            print(f"  {rid}  FAIL     [constraints file] {defect}")
            counts[FAIL] += 1
            hard_fail += 1
            continue

        name = row.get("check")
        if not name:
            print(f"  {rid}  MANUAL   status={row['status']:12s} {row['rule'][:64]}")
            counts[MANUAL] += 1
            continue
        if name not in CHECKS:
            print(f"  {rid}  FAIL     [constraints file] unknown check {name!r}")
            counts[FAIL] += 1
            hard_fail += 1
            continue
        if tex is None:
            print(f"  {rid}  SKIPPED  {name}: manuscript absent at {TEX}")
            counts[SKIPPED] += 1
            continue

        verdict, detail = CHECKS[name](tex)
        counts[verdict] += 1
        if verdict == FAIL:
            hard_fail += 1
        print(f"  {rid}  {verdict:8s} {name}: {detail}")

    print()
    print(f"PASS={counts[PASS]}  FAIL={counts[FAIL]}  "
          f"SKIPPED={counts[SKIPPED]}  MANUAL={counts[MANUAL]}")
    print()
    print("SKIPPED is never a pass. Every SKIPPED row names what is missing.")
    print("No row may be marked confirmed without the 2027 rules book.")
    return 1 if hard_fail else 0


if __name__ == "__main__":
    sys.exit(main())
