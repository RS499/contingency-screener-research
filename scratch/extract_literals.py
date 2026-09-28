"""Read-only: list every numeric literal occurrence in the BODY of report/paper_current_STS.tex
(title block through Acknowledgments, including captions, table cells and figure attribution
lines). Excluded, and counted separately: comment lines, the preamble, the bibliography, and
tokens that are names rather than quantities (\\cite / \\label / \\ref keys, file paths, N-0 / N-1 /
N-2, F1-F4, R^2, case118-style network ids) and LaTeX layout arguments (0.8\\textwidth, 1ex, 0.15in).

Imported by scratch/number_check.py; run directly to print the occurrence list.
Usage: .venv/bin/python scratch/extract_literals.py
"""

import re

TEX = "report/paper_current_STS.tex"

NAME_PATTERNS = [
    r"\\setcounter\{[^}]*\}\{[^}]*\}",
    r"\\(cite|label|ref|includegraphics|addcontentsline|setcounter|section|subsection)\*?(\[[^\]]*\])?\{[^}]*\}",
    r"\\(vspace|hspace)\*?\{[^}]*\}",
    r"width=[0-9.]+\\textwidth",
    r"\\itemsep0em",
    r"N[-\u2011][0-9]",
    r"\\setstretch\{[^}]*\}",
    r"\\setcounter\{[^}]*\}\{[^}]*\}",
    r"\(\$10\^\{-3\}\$ pu\)",
    r"\bF[1-4]\b",
    r"R\^2",
    r"\bcase(?:\\?_illinois\d+|\d+(?:\\?_[A-Za-z]+|[A-Za-z0-9])*)",
    r"\\mathbf\{1\}",
    r"L_?\{?[0-9]\}?",
    r"--",
]

NUM = re.compile(r"(?<![A-Za-z_\\])((?:(?<=[\s$\{])-)?\d+(?:\{,\}\d{3}|,\d{3})*(?:\.\d+)?)(\s*\\times\s*10\^\{(-?\d+)\})?")


VERSION = re.compile(r"\d+\.\d+\.\d+")


def body_range(lines):
    start = next(i for i, l in enumerate(lines) if l.startswith("\\title{"))
    stop = next(i for i, l in enumerate(lines) if l.startswith("\\begin{thebibliography}"))
    return start, stop


def occurrences():
    with open(TEX) as fh:
        lines = fh.read().split("\n")
    start, stop = body_range(lines)
    out = []
    excluded = 0
    for i in range(start, stop):
        raw = lines[i]
        if raw.lstrip().startswith("%"):
            continue
        text = raw.split("%")[0] if "\\%" not in raw else re.sub(r"(?<!\\)%.*$", "", raw)
        norm = text.replace("\\pm", " \\pm ")
        clean = norm
        for v in VERSION.finditer(clean):
            ctx = " ".join(norm[max(0, v.start() - 60):v.end() + 40].split())
            out.append({"line": i + 1, "printed": v.group(0), "value": None, "dp": 0, "sci": False, "ctx": ctx})
        clean = VERSION.sub(lambda m: " " * len(m.group(0)), clean)
        for pat in NAME_PATTERNS:
            before = len(NUM.findall(clean))
            clean = re.sub(pat, lambda m: " " * len(m.group(0)), clean)
            excluded = excluded + before - len(NUM.findall(clean))
        for m in NUM.finditer(clean):
            printed = m.group(0).strip()
            base = m.group(1).replace("{,}", "").replace(",", "")
            value = float(base)
            if m.group(3) is not None:
                value = value * 10 ** int(m.group(3))
            dp = len(base.split(".")[1]) if "." in base else 0
            ctx = " ".join(norm[max(0, m.start() - 60):m.end() + 40].split())
            out.append({"line": i + 1, "printed": printed, "value": value, "dp": dp,
                        "sci": m.group(3) is not None, "ctx": ctx})
    return out, excluded


if __name__ == "__main__":
    occ, excluded = occurrences()
    print(f"{len(occ)} numeric literal occurrences; {excluded} name/layout tokens excluded")
    for o in occ:
        print(f"L{o['line']:<4} {o['printed']:<22} | {o['ctx'][:110]}")
