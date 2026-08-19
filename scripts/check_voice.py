import os
import re
import sys

# Voice guard.
#
# Master Plan section 1 records that "use I, not we" is PERMITTED, NOT REQUIRED - the
# 4th-place 2026 paper uses "we" throughout. So this gate does NOT enforce first-person
# singular. It enforces CONSISTENCY, and reports every instance so the author can choose.
#
# The live inconsistency it exists to catch: an abstract in "I", a body in "we"/"our",
# and an Acknowledgments section in "the authors" - three voices in one document, which
# reads as three writers.

TEX = "report/paper_current_STS.tex"

MARKERS = [
    ("we", r"\bwe\b"),
    ("our", r"\bour\b"),
    ("ours", r"\bours\b"),
    ("us", r"\bus\b"),
    ("I", r"\bI\b"),
    ("my", r"\bmy\b"),
    ("the authors", r"\bthe authors?\b"),
]

SECTION_RE = re.compile(r"\\section\*?\{([^}]*)\}")


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


def section_of(lines, lineno):
    name = "<preamble>"
    for i in range(lineno):
        m = SECTION_RE.search(lines[i])
        if m:
            name = m.group(1)
    return name


def main():
    if not os.path.exists(TEX):
        print(f"SKIPPED: {TEX} absent")
        return 0

    with open(TEX) as f:
        lines = strip_comments(f.read())

    hits = []
    for i, line in enumerate(lines):
        for label, rx in MARKERS:
            for m in re.finditer(rx, line):
                hits.append((i + 1, section_of(lines, i), label,
                             line[max(0, m.start() - 40):m.end() + 40].strip()))

    if not hits:
        print("PASS: no first-person or third-person-author markers found")
        return 0

    by_section = {}
    for lineno, sect, label, ctx in hits:
        by_section.setdefault(sect, {}).setdefault(label, []).append(lineno)

    print(f"voice markers in {TEX}: {len(hits)} instance(s)")
    print()
    for sect in by_section:
        parts = [f"{lab}x{len(nos)}" for lab, nos in sorted(by_section[sect].items())]
        print(f"  {sect:38s} {', '.join(parts)}")

    families = {
        "first-person plural": {"we", "our", "ours", "us"},
        "first-person singular": {"I", "my"},
        "third-person author": {"the authors"},
    }
    present = set()
    for sect in by_section:
        for lab in by_section[sect]:
            for fam, labs in families.items():
                if lab in labs:
                    present.add(fam)

    print()
    print("  voice families present: " + ", ".join(sorted(present)))
    print()
    for lineno, sect, label, ctx in hits:
        print(f"    L{lineno:<5d} [{sect[:26]:26s}] {label:12s} ...{ctx}...")

    print()
    if len(present) > 1:
        print(f"FAIL: {len(present)} voice families in one document. "
              "Consistency is the requirement; which voice is the author's choice.")
        return 1
    print("PASS: a single voice family throughout")
    return 0


if __name__ == "__main__":
    sys.exit(main())
