#!/usr/bin/env python3
"""#45 — Unique-shape inventory VIEW. Answer "this pattern is built from N shapes"
at a glance, instead of reading clusters.json by hand.

WHY a view (not just the existing atlas): render_cluster_atlas.py is a flat contact
sheet — every class as one cell, no headline, no reconciliation of the raw->placeable->
class funnel, no separation of the repeating vocabulary from one-off centerpieces. The
owner's question is "how many DISTINCT designed shapes is this medallion made of, and
which ones dominate?" This view leads with that number, shows the 523-raw -> 142-frame
-> 381-placeable -> 26-class funnel that justifies it, and groups the classes into the
repeating vocabulary (>=10x, the 10-fold rotational families) vs unique centerpieces
(<10x). The eye gets the answer in ~2 seconds (Tenet 27 — art-savvy-grandma legible).

Reads the congruence-signature clusterer output (cluster_shapes.py -> clusters.json);
emits a single inventory card PNG. Rendered artifact -> Dropbox (storage rule); this
script is authored code -> git.

Run: python3 render_shape_inventory.py [iter]   (default iter 71)
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

B = Path("/Users/omareid/Library/CloudStorage/Dropbox/Data/sacred-patterns/bikar-medallion-10")
ITER = sys.argv[1] if len(sys.argv) > 1 else "71"
WG = B / "iterations" / ITER / "wave-ghosts"
CL = json.loads((WG / "clusters.json").read_text())

# --- layout constants ----------------------------------------------------------
MARGIN = 40
SWATCH = 130          # per-class tile
SW_PAD = 16
COLS = 9
HEADER_H = 170
SECTION_H = 46


def font(sz, bold=False):
    name = "Arial Bold.ttf" if bold else "Arial.ttf"
    try:
        return ImageFont.truetype(f"/System/Library/Fonts/Supplemental/{name}", sz)
    except Exception:
        return ImageFont.load_default()


F_HERO = font(64, bold=True)
F_SUB = font(20)
F_FUNNEL = font(17)
F_SECTION = font(22, bold=True)
F_CAP = font(13)
F_CAPB = font(13, bold=True)


def fit(outline, x0, y0, size):
    """Scale a class's representative outline to fill a swatch tile, centered."""
    xs = [p[0] for p in outline]
    ys = [p[1] for p in outline]
    w = max(xs) - min(xs) or 1
    h = max(ys) - min(ys) or 1
    s = (size - 2 * SW_PAD) / max(w, h)
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    return [(x0 + size / 2 + (p[0] - cx) * s, y0 + size / 2 + (p[1] - cy) * s)
            for p in outline]


def draw_class(d, c, x0, y0):
    color = c["dominant_color"] or "#CCCCCC"
    if color == "None":
        color = "#CCCCCC"
    if c["kind"] == "circle":
        d.ellipse([x0 + SW_PAD, y0 + SW_PAD, x0 + SWATCH - SW_PAD, y0 + SWATCH - SW_PAD],
                  fill=color, outline="#888")
    else:
        d.polygon(fit(c["representative_outline"], x0, y0, SWATCH), fill=color, outline="#333")
    # count badge (bold) + class id / vertex count (plain)
    d.text((x0 + 6, y0 + 4), f"x{c['count']}", fill="#000", font=F_CAPB)
    d.text((x0 + 6, y0 + SWATCH - 18), f"{c['cluster_id']} - {c['vertex_count']}gon",
           fill="#444", font=F_CAP)


# --- partition classes: repeating vocabulary (>=10x) vs unique (<10x) -----------
clusters = sorted(CL["clusters"], key=lambda c: (-c["count"], c["vertex_count"]))
vocab = [c for c in clusters if c["count"] >= 10]
unique = [c for c in clusters if c["count"] < 10]


def grid_rows(n):
    return math.ceil(n / COLS) if n else 0


vocab_rows = grid_rows(len(vocab))
uniq_rows = grid_rows(len(unique))
grid_w = COLS * SWATCH

H = (HEADER_H
     + (SECTION_H + vocab_rows * SWATCH if vocab else 0)
     + (SECTION_H + uniq_rows * SWATCH if unique else 0)
     + 2 * MARGIN)
W = grid_w + 2 * MARGIN

img = Image.new("RGB", (W, H), "#FFFFFF")
d = ImageDraw.Draw(img)

# --- header: the headline number + the funnel that justifies it -----------------
y = MARGIN
d.text((MARGIN, y), f"Built from {CL['n_clusters']} shapes", fill="#111", font=F_HERO)
y += 78
d.text((MARGIN, y),
       f"{len(vocab)} repeating shape families  +  {len(unique)} unique centerpiece"
       + ("s" if len(unique) != 1 else ""),
       fill="#333", font=F_SUB)
y += 30
funnel = (f"{CL['n_shapes']} faces detected   ->   "
          f"{CL['n_excluded_frame']} frame/background excluded   ->   "
          f"{CL['n_placeable']} placeable   ->   "
          f"{CL['n_clusters']} distinct classes (congruence eps {CL['eps']})")
d.text((MARGIN, y), funnel, fill="#777", font=F_FUNNEL)

# --- sections -------------------------------------------------------------------
y = HEADER_H + MARGIN


def section(title, items, y):
    d.text((MARGIN, y), title, fill="#111", font=F_SECTION)
    y += SECTION_H
    for i, c in enumerate(items):
        r, col = divmod(i, COLS)
        draw_class(d, c, MARGIN + col * SWATCH, y + r * SWATCH)
    return y + grid_rows(len(items)) * SWATCH


if vocab:
    total_v = sum(c["count"] for c in vocab)
    y = section(f"Repeating vocabulary  -  {len(vocab)} families, {total_v} shapes "
                f"(the 10-fold motifs)", vocab, y)
if unique:
    total_u = sum(c["count"] for c in unique)
    y = section(f"Unique  -  {len(unique)} class, {total_u} shape "
                f"(one-off centerpiece)", unique, y)

out = WG / "shape-inventory.png"
img.save(out)
print(f"inventory: {CL['n_clusters']} classes "
      f"({len(vocab)} repeating + {len(unique)} unique) -> {out}")
