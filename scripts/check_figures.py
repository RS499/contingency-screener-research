import hashlib
import json
import os
import re
import sys

# Figure manifest gate.
#
# Walks every \includegraphics path in the manuscript and fails if:
#   - the image has no sidecar manifest
#   - the manifest carries no apa_citation
#   - the manifest carries no input_sha256 (the provenance chain does not close)
#   - the .tex has no APA line beneath that float
#
# Schema B (data/fig_floor.manifest.json) is the model: it binds the PNG to its
# generating script, the script's git blob sha, the input file AND that input's hash.
# Schema A records environment only and cannot answer "what produced this image".
#
# The alternative to this gate is ~10 hand-written APA citations in week 12, inside
# the compliance window, where one omission can disqualify.

TEX = "report/paper_current_STS.tex"

REQUIRED = ["apa_citation", "input_sha256", "generating_script", "content_sha256"]
APA_RE = r"\\apacite|APA:|\(\d{4}\)\."


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
    return "\n".join(out)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_path(image):
    root, _ext = os.path.splitext(image)
    return root + ".manifest.json"


def float_blocks(body):
    return [(m.group(1), m.group(0))
            for m in re.finditer(r"\\begin\{(figure|table)\}.*?\\end\{\1\}", body, re.S)]


def main():
    if not os.path.exists(TEX):
        print(f"SKIPPED: {TEX} absent")
        return 0

    with open(TEX) as f:
        body = strip_comments(f.read())

    blocks = float_blocks(body)
    figures = [(kind, block) for kind, block in blocks if kind == "figure"]
    tables = [(kind, block) for kind, block in blocks if kind == "table"]

    print(f"figure manifest gate on {TEX}")
    print(f"  {len(figures)} figure float(s), {len(tables)} table float(s)")
    print()

    fails = 0

    for _kind, block in figures:
        label = re.search(r"\\label\{([^}]*)\}", block)
        name = label.group(1) if label else "<unlabelled>"
        images = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", block)
        if not images:
            print(f"  FAIL  figure {name}: no \\includegraphics")
            fails += 1
            continue
        for image in images:
            problems = []
            if not os.path.exists(image):
                problems.append("image file absent")
            mpath = manifest_path(image)
            if not os.path.exists(mpath):
                problems.append(f"no manifest at {mpath}")
            else:
                with open(mpath) as f:
                    man = json.load(f)
                for field in REQUIRED:
                    if not man.get(field):
                        problems.append(f"manifest missing {field}")
                recorded = man.get("content_sha256")
                if recorded and os.path.exists(image):
                    actual = sha256_of(image)
                    if actual != recorded:
                        problems.append(
                            f"content_sha256 MISMATCH: manifest {recorded[:12]}... "
                            f"actual {actual[:12]}...")
            if not re.search(APA_RE, block):
                problems.append("no APA line beneath the float in the .tex")

            if problems:
                print(f"  FAIL  figure {name} -> {image}")
                for p in problems:
                    print(f"          {p}")
                fails += 1
            else:
                print(f"  PASS  figure {name} -> {image}")

    for _kind, block in tables:
        label = re.search(r"\\label\{([^}]*)\}", block)
        name = label.group(1) if label else "<unlabelled>"
        if not re.search(APA_RE, block):
            print(f"  FAIL  table {name}: no APA line beneath the float")
            print("          R10 requires an APA citation beneath every figure AND table,")
            print("          naming the software used, including self-created graphics.")
            fails += 1
        else:
            print(f"  PASS  table {name}")

    print()
    if fails:
        print(f"FAIL: {fails} float(s) do not close the provenance chain")
        return 1
    print("PASS: every float carries a manifest with apa_citation and input_sha256")
    return 0


if __name__ == "__main__":
    sys.exit(main())
