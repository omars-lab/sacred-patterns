#!/usr/bin/env python3
"""Iter-55 wave-13 clearance proof — rasterize the 10 snapped teardrop
tiles (one per star-tip axis, axis-symmetric) in reference px space;
count overlap px against reference waves 1-12 + unbuilt 14-22 (must be
0), attribute off-target px, then compute model-vs-model min distances
against OUR built neighbors that share or flank the star-tip axes:
wave-9 16-gon (apex on-axis r 146.1 vs our base r 151.4 — the close
one), wave-11 birds (same axes, rel 3.75-11.25, r 145.9-161), wave-12
bells (dart axes +-18)."""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

SESS = Path("/Users/omareid/Library/CloudStorage/Dropbox/Data/sacred-patterns/bikar-medallion-10")
TOOLS = Path("/Users/omareid/Workspace/git/sacred-patterns/tools")
PXU = math.sqrt(1091 / 640.7)

spec = importlib.util.spec_from_file_location("analyze_reference", TOOLS / "analyze-reference.py")
ar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ar)

plan = json.loads((SESS / "input/reference-analysis/wave-plan/wave-plan.json").read_text())
cx, cy = plan["center"]["x"], plan["center"]["y"]

img = Image.open(SESS / "input/reference.jpg").convert("RGB")
a = np.asarray(img)
near_white = (a >= 200).all(axis=2)
medallion = ar.medallion_mask(near_white)
tiles = medallion & ~near_white
four = ndimage.generate_binary_structure(2, 1)
cores = ndimage.binary_erosion(tiles, structure=four, iterations=2)
seed_labels, _ = ndimage.label(cores, structure=four)
_, (iy, ix) = ndimage.distance_transform_edt(seed_labels == 0, return_indices=True)
labels = np.where(tiles, seed_labels[iy, ix], 0)

fit = json.loads((SESS / "iterations/54/measure/wave13-fit.json").read_text())
rows = fit["rows"]
plus = [(v["r"], v["x"]) for v in rows[1:-1]]
model = ([(rows[0]["r"], 0.0)] + plus + [(rows[-1]["r"], 0.0)]
         + [(r, -x) for r, x in reversed(plus)])

mask = Image.new("1", (a.shape[1], a.shape[0]), 0)
d = ImageDraw.Draw(mask)
for k in range(10):
    axis = k * 36.0
    pts = []
    for r, rel in model:
        t = math.radians(axis + rel)
        pts.append((cx + r * PXU * math.cos(t), cy - r * PXU * math.sin(t)))
    d.polygon(pts, fill=1)
stamp = np.asarray(mask, dtype=bool)
print(f"stamped px: {stamp.sum()}")

w13ids = []
for wnum in range(1, 23):
    w = next(w for w in plan["waves"] if w["wave"] == wnum)
    ids = [s["id"] for s in w["shapes"] if not s["fragment"]]
    if wnum == 13:
        w13ids = ids
    wmask = np.isin(labels, ids)
    ov = (stamp & wmask).sum()
    tag = "ON-TARGET" if wnum == 13 else ("OK" if ov == 0 else "OVERLAP!")
    print(f"wave {wnum:2d}: overlap {ov} px ({ov / stamp.sum() * 100:.1f}% of stamp) {tag}")

# off-target attribution: every stamp px not on the wave-13 mask must be
# near-white band, a wave-13 fragment, or named "other" (loud, Tenet 3)
on = (stamp & np.isin(labels, w13ids)).sum()
off = stamp & ~np.isin(labels, w13ids)
w13all = next(w for w in plan["waves"] if w["wave"] == 13)
frag_ids = [s["id"] for s in w13all["shapes"] if s["fragment"]]
off_white = (off & near_white).sum()
off_frag = (off & np.isin(labels, frag_ids)).sum()
off_other = off.sum() - off_white - off_frag
print(f"\non-target: {on} px ({on / stamp.sum() * 100:.1f}%)")
print(f"off-target: {off.sum()} px = near-white {off_white} "
      f"({off_white / stamp.sum() * 100:.1f}%) + w13-fragments {off_frag} "
      f"({off_frag / stamp.sum() * 100:.1f}%) + OTHER {off_other} "
      f"({off_other / stamp.sum() * 100:.1f}%)")

# --- model-vs-model min distance (face-split guard) -------------------
def to_xy(polar):
    return [(r * math.cos(math.radians(t)), r * math.sin(math.radians(t)))
            for r, t in polar]

def seg_dist(p1, p2, q1, q2):
    def pt_seg(p, a, b):
        ax, ay = a; bx, by = b; px, py = p
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
        return math.hypot(px - (ax + t * dx), py - (ay + t * dy))
    return min(pt_seg(p1, q1, q2), pt_seg(p2, q1, q2),
               pt_seg(q1, p1, p2), pt_seg(q2, p1, p2))

def poly_min_dist(A, B):
    best = float("inf")
    for i in range(len(A)):
        for j in range(len(B)):
            best = min(best, seg_dist(A[i], A[(i + 1) % len(A)],
                                      B[j], B[(j + 1) % len(B)]))
    return best

w13_xy = to_xy([(r, t) for r, t in model])  # axis 0

w9 = json.loads((SESS / "iterations/50/measure/wave9-fit.json").read_text())
p9 = [(v["r"], v["x"]) for v in w9["vertices"][1:-1]]
m9 = ([(w9["vertices"][0]["r"], 0.0)] + p9 + [(w9["vertices"][-1]["r"], 0.0)]
      + [(r, -x) for r, x in reversed(p9)])
print(f"\nmin dist to w9 16-gon (same axis 0): "
      f"{poly_min_dist(w13_xy, to_xy(m9)):.2f} u")

w11 = json.loads((SESS / "iterations/52/measure/wave11-fit.json").read_text())
bird_plus = to_xy([(v["r"], v["cpt_plus"] * 360 / v["M"]) for v in w11["vertices"]])
bird_minus = to_xy([(v["r"], v["cpt_mirror"] * 360 / v["M"] - 360) for v in w11["vertices"]])
print(f"min dist to w11 bird + member (axis 0): {poly_min_dist(w13_xy, bird_plus):.2f} u")
print(f"min dist to w11 bird - member (axis 0): {poly_min_dist(w13_xy, bird_minus):.2f} u")

w12 = json.loads((SESS / "iterations/53/measure/wave12-fit.json").read_text())
p12 = [(v["r"], v["x"]) for v in w12["rows"][1:-1]]
m12 = ([(w12["rows"][0]["r"], 0.0)] + p12 + [(w12["rows"][-1]["r"], 0.0)]
       + [(r, -x) for r, x in reversed(p12)])
for ax in (18.0, -18.0):
    bell = to_xy([(r, ax + t) for r, t in m12])
    print(f"min dist to w12 bell (axis {ax:+.0f}): {poly_min_dist(w13_xy, bell):.2f} u")
