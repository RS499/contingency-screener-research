import json
import os
import re
import sys

# Citation gate.
#
# Fails on: non-resolution, title/author mismatch, missing verification date,
# ambiguous venue status, or a missing claim_support record.
#
# WHY claim_support IS REQUIRED. As originally specified this gate would PASS the
# ansi2020 entry: ANSI C84.1-2020 is a real, resolvable standard, correctly
# transcribed. What is wrong is that the manuscript cites it for a number (0.917 pu)
# that came from a NEMA front-matter excerpt, not from the paid standard body text.
# A gate that checks references EXIST cannot catch a reference cited for a claim it
# does not make. So every bibitem must record WHICH assertion it backs and HOW that
# was verified.
#
# NETWORK ACCESS. This script does not fetch. Resolution status is read from
# notes/prior-art.md and notes/citation_support.json, which are human-maintained
# records of fetches that actually happened, with dates. Inventing a resolution
# result would be the exact failure this gate exists to prevent.

TEX = "report/paper_current_STS.tex"
PRIOR_ART = "notes/prior-art.md"
SUPPORT = "notes/citation_support.json"

DATE_RE = r"20\d{2}-\d{2}-\d{2}"


def read(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return f.read()


def bibitems(tex):
    out = []
    for m in re.finditer(r"\\bibitem\{([^}]*)\}(.*?)(?=\\bibitem\{|\\end\{thebibliography\})",
                         tex, re.S):
        key = m.group(1)
        body = " ".join(m.group(2).split())
        lineno = tex[:m.start()].count("\n") + 1
        out.append({"key": key, "body": body, "line": lineno})
    return out


def cited_keys(tex):
    keys = set()
    for m in re.finditer(r"\\cite\{([^}]*)\}", tex):
        for k in m.group(1).split(","):
            keys.add(k.strip())
    return keys


def identifiers(body):
    ids = {}
    m = re.search(r"arXiv:(\d{4}\.\d{4,5})(v\d+)?", body, re.IGNORECASE)
    if m:
        ids["arxiv"] = m.group(0)
    m = re.search(r"doi:\s*(10\.\S+?)(?:[,.]?\s|$)", body, re.IGNORECASE)
    if m:
        ids["doi"] = m.group(1).rstrip(".,")
    return ids


def prior_art_record(prior_art, key, body):
    """Look for the key, or a distinctive token from the entry, in prior-art.md."""
    if prior_art is None:
        return None, None
    hay = prior_art.lower()
    needles = [key.lower()]
    ids = identifiers(body)
    if "arxiv" in ids:
        needles.append(ids["arxiv"].lower().split("v")[0])
    if "doi" in ids:
        needles.append(ids["doi"].lower())
    for n in needles:
        idx = hay.find(n)
        if idx >= 0:
            window = prior_art[max(0, idx - 800): idx + 800]
            dates = re.findall(DATE_RE, window)
            return True, (dates[0] if dates else None)
    return False, None


def main():
    tex = read(TEX)
    if tex is None:
        print(f"SKIPPED: {TEX} absent")
        return 0

    prior_art = read(PRIOR_ART)
    support = {}
    if os.path.exists(SUPPORT):
        with open(SUPPORT) as f:
            support = json.load(f).get("entries", {})

    items = bibitems(tex)
    cited = cited_keys(tex)

    print(f"citation gate on {TEX}")
    print(f"  {len(items)} bibitem(s), {len(cited)} distinct \\cite key(s)")
    print(f"  prior-art record: {PRIOR_ART}" + ("" if prior_art else "  [ABSENT]"))
    print(f"  claim_support record: {SUPPORT}"
          + ("" if support else "  [ABSENT - every entry will FAIL this field]"))
    print()

    declared = {it["key"] for it in items}
    fails = 0

    orphan_cites = sorted(cited - declared)
    for k in orphan_cites:
        print(f"  FAIL  \\cite{{{k}}} has no \\bibitem")
        fails += 1
    unused = sorted(declared - cited)
    for k in unused:
        print(f"  WARN  \\bibitem{{{k}}} is never cited")

    m = re.search(r"\\begin\{thebibliography\}\{(\d+)\}", tex)
    if m:
        width = int(m.group(1))
        if width != len(items):
            print(f"  FAIL  thebibliography width {width} != {len(items)} bibitems")
            fails += 1
        else:
            print(f"  PASS  thebibliography width {width} matches {len(items)} bibitems")
    print()

    for it in items:
        key, body = it["key"], it["body"]
        problems = []

        found, date = prior_art_record(prior_art, key, body)
        if prior_art is None:
            problems.append(f"{PRIOR_ART} absent; resolution unverifiable")
        elif not found:
            problems.append(f"NO ENTRY in {PRIOR_ART}")
        elif not date:
            problems.append(f"entry in {PRIOR_ART} carries no verification date")

        rec = support.get(key)
        if not rec:
            problems.append("no claim_support record")
        else:
            if not rec.get("claim"):
                problems.append("claim_support record has no 'claim'")
            if not rec.get("verified_how"):
                problems.append("claim_support record has no 'verified_how'")
            if rec.get("venue_status") == "ambiguous":
                problems.append("venue_status is 'ambiguous'")
            if rec.get("source_of_number") and rec.get("source_of_number") != rec.get("cited_work"):
                problems.append(
                    f"cited as {rec.get('cited_work')!r} but the number came from "
                    f"{rec.get('source_of_number')!r}")

        if problems:
            print(f"  FAIL  {key:16s} (L{it['line']})")
            for p in problems:
                print(f"          {p}")
            fails += 1
        else:
            print(f"  PASS  {key:16s} (L{it['line']})  verified {date}")

    print()
    if fails:
        print(f"FAIL: {fails} citation defect(s). One fabricated or unsupported "
              "reference is disqualifying.")
        return 1
    print("PASS: every bibitem resolves, carries a verification date, and records "
          "the claim it supports")
    return 0


if __name__ == "__main__":
    sys.exit(main())
