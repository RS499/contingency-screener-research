import os
import sys
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import classical_manifest as cm
import figtools as ft

CURVE = "data/tradeoff_curve_v2.json"
OUT_TXT = "data/poster/table1.txt"
OUT_PNG = "data/poster/table1.png"
FIGSIZE = (14.05, 4.0)
ROWS = [("ridge", 0.90), ("ridge", 0.94), ("histgb", 0.90), ("histgb", 0.97)]
HEADERS = ["Model", "Target", "Esc. (%)", "Missed (%)", "Speedup"]


def pull_rows(curve_path):
    with open(curve_path) as f:
        records = json.load(f)["records"]
    rows = []
    for fam, cov in ROWS:
        r = next(x for x in records if x["model"] == fam and abs(x["coverage_target"] - cov) < 1e-9)
        rows.append([
            fam, f"{cov:.2f}",
            f"{r['escalation']*100:.1f}±{r['escalation_std']*100:.1f}",
            f"{r['missed_viol']*100:.2f}±{r['missed_viol_std']*100:.2f}",
            f"{r['net_speedup']:.2f}±{r['net_speedup_std']:.2f}"])
    return rows


def write_text(rows, path):
    widths = [max(len(HEADERS[c]), max(len(row[c]) for row in rows)) for c in range(len(HEADERS))]
    lines = []
    lines.append("  ".join(HEADERS[c].ljust(widths[c]) for c in range(len(HEADERS))))
    lines.append("  ".join("-" * widths[c] for c in range(len(HEADERS))))
    for row in rows:
        lines.append("  ".join(row[c].ljust(widths[c]) for c in range(len(HEADERS))))
    text = "\n".join(lines) + "\n"
    with open(path, "w") as f:
        f.write(text)
    return text


def make_png(rows, path):
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.axis("off")
    tbl = ax.table(cellText=rows, colLabels=HEADERS, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(ft.POSTER_FS_BASE)
    tbl.scale(1, 3.2)
    for (r, _c), cell in tbl.get_celld().items():
        cell.set_linewidth(1.0)
        if r == 0:
            cell.set_text_props(weight="bold")
            cell.set_facecolor("#eeeeee")
    ft.add_credit(fig)
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    ft.pad_to_exact(path, FIGSIZE)


def main():
    os.makedirs(os.path.dirname(OUT_TXT), exist_ok=True)
    rows = pull_rows(CURVE)

    text = write_text(rows, OUT_TXT)
    print(text)
    print(f"wrote {OUT_TXT}")

    make_png(rows, OUT_PNG)
    print(f"wrote {OUT_PNG}")

    manifest_path = "data/poster/table1.manifest.json"
    meta = dict(figure="poster Table I: 4-row safety/throughput reduction", source=CURVE,
                rows=[dict(model=f, target=c) for f, c in ROWS], figsize_in=list(FIGSIZE))
    settings = dict(task="poster Table I", source=CURVE)
    man = cm.build_manifest(OUT_PNG, meta, settings)
    man["content_sha256"] = dict(txt=cm.content_hash(OUT_TXT), png=cm.content_hash(OUT_PNG))
    with open(manifest_path, "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote {manifest_path} (sha256 txt={man['content_sha256']['txt'][:12]}..., "
          f"png={man['content_sha256']['png'][:12]}...)")


if __name__ == "__main__":
    main()
