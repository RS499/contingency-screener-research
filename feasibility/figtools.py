
CREDIT = "Figure created by student researcher using Matplotlib, 2026."

CREDIT_ENABLED = False

POSTER_FS_BASE = 18
POSTER_FS_LABEL = 20
POSTER_FS_TICK = 16
POSTER_FS_ANNOT = 16
POSTER_LW = 2.5
POSTER_DPI = 300


def add_credit(fig, text=CREDIT):
    if not CREDIT_ENABLED:
        return
    fig.text(0.99, 0.005, text, ha="right", va="bottom", fontsize=7, color="gray")


def pad_to_exact(path, figsize_in, dpi=POSTER_DPI):
    from PIL import Image
    img = Image.open(path)
    tw, th = int(round(figsize_in[0] * dpi)), int(round(figsize_in[1] * dpi))
    w, h = img.size
    if (w, h) == (tw, th):
        return
    scale = min(tw / w, th / h, 1.0)
    if scale < 1.0:
        img = img.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
        w, h = img.size
    canvas = Image.new("RGB", (tw, th), "white")
    canvas.paste(img.convert("RGB"), ((tw - w) // 2, (th - h) // 2))
    canvas.save(path, dpi=(dpi, dpi))
