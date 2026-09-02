#!/usr/bin/env python3
"""Render a CONTACT SHEET of the canonical shape-classes so we can SEE the pattern's
vocabulary instead of reading hex codes (Tenet 24 — render and look).

Each cell = one cluster's representative outline, normalized to fill the cell, filled
with its dominant color, captioned with the count + vertex count. Laid out in a grid,
biggest-count first. The eye can then spot over-splits — two cells that are visibly the
SAME silhouette in different colors are merge candidates for the propose-and-confirm UI.
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

CELL = 150
PAD = 14
COLS = 10
clusters = CL["clusters"]
rows = math.ceil(len(clusters) / COLS)
W, H = COLS * CELL, rows * CELL
img = Image.new("RGB", (W, H), "#FFFFFF")
d = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 13)
except Exception:
    font = ImageFont.load_default()


def fit(outline, x0, y0, size):
    """Scale an outline to fill a square cell with padding, centered."""
    xs = [p[0] for p in outline]
    ys = [p[1] for p in outline]
    w = max(xs) - min(xs) or 1
    h = max(ys) - min(ys) or 1
    s = (size - 2 * PAD) / max(w, h)
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    return [(x0 + size / 2 + (p[0] - cx) * s, y0 + size / 2 + (p[1] - cy) * s)
            for p in outline]


for i, c in enumerate(clusters):
    r, col = divmod(i, COLS)
    x0, y0 = col * CELL, r * CELL
    d.rectangle([x0, y0, x0 + CELL, y0 + CELL], outline="#E0E0E0")
    color = c["dominant_color"] or "#CCCCCC"
    if c["kind"] == "circle":
        d.ellipse([x0 + PAD, y0 + PAD, x0 + CELL - PAD, y0 + CELL - PAD],
                  fill=color if color != "None" else "#CCCCCC", outline="#888")
    else:
        poly = fit(c["representative_outline"], x0, y0, CELL)
        d.polygon(poly, fill=color, outline="#333")
    cap = f"{c['cluster_id']} x{c['count']} ({c['vertex_count']}gon)"
    d.text((x0 + 4, y0 + 2), cap, fill="#000", font=font)

out = WG / "cluster-atlas.png"
img.save(out)
print(f"{len(clusters)} classes -> {out}")
