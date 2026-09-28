"""Read-only page estimate for report/paper_current_STS.tex (no TeX toolchain available).

Prose words: Introduction through Acknowledgments, excluding floats, equations, headings, the
abstract and the bibliography (same definition as notes/writing-guide.md section 6.2). Figure
heights: PNG pixel aspect x \\textwidth fraction x 6.5 in. Writes nothing.

Usage: .venv/bin/python scratch/page_estimate.py
"""

import re
import struct

TEX = "report/paper_current_STS.tex"
FIGS = [("data/gate_schematic_v4.png", 0.8), ("data/tradeoff_hero_col_v2.png", 0.6),
        ("data/miss_depth_v3.png", 0.6), ("data/boundary_mass_hist_v2.png", 0.6),
        ("data/critical_bus_map.png", 0.55)]
WPP_ONEHALF = 345                      # measured, notes/writing-guide.md section 6.2
WPP_LITERAL = 345 * 1.241 / 1.5        # same layout at \setstretch{1.5}
TABULAR_PP = 0.55


def prose_words(text):
    lines = [l for l in text.split("\n") if not l.lstrip().startswith("%")]
    s = "\n".join(lines)
    body = s[s.index("\\section{Introduction}"):s.index("\\begin{thebibliography}")]
    body = re.sub(r"\\begin\{(figure|table)\}.*?\\end\{(figure|table)\}", " ", body, flags=re.S)
    body = re.sub(r"\\begin\{equation\}.*?\\end\{equation\}", " ", body, flags=re.S)
    body = re.sub(r"\$[^$]*\$", " X ", body)
    body = re.sub(r"\\(label|ref|cite|includegraphics)\{[^}]*\}", " ", body)
    body = re.sub(r"\\(sub)*section\*?\{[^}]*\}", " ", body)
    body = re.sub(r"\\[A-Za-z]+", " ", body)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-.]*", body))


def fig_pages():
    total_in = 0.0
    for path, frac in FIGS:
        with open(path, "rb") as fh:
            head = fh.read(24)
        w, h = struct.unpack(">II", head[16:24])
        total_in = total_in + 6.5 * frac * h / w
    return total_in / 9.0


if __name__ == "__main__":
    with open(TEX) as fh:
        words = prose_words(fh.read())
    figs = fig_pages()
    print(f"prose words: {words}; figure graphics: {figs:.2f} pp; tabular: {TABULAR_PP} pp")
    for name, wpp in [("onehalfspacing", WPP_ONEHALF), ("setstretch 1.5", WPP_LITERAL)]:
        print(f"  {name:15s} {wpp:.0f} w/p -> {words / wpp + figs + TABULAR_PP:.1f} counted pages")
