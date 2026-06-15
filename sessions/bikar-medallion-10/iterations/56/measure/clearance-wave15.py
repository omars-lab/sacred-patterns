#!/usr/bin/env python3
"""Iter-57 wave-15 clearance proof — rasterize the 10 snapped pentagram
stamps (one axis-symmetric star per DART axis, apex outward) in
reference px space; count overlap px against reference waves 1-14 +
unbuilt 16-22 (must be 0), attribute off-target px, then compute
model-vs-model min distances against OUR built neighbors: wave-12 bell
(SAME dart axes, apex C60 r 170.7 on-axis vs our inner verts r 175-178
— the radial neighbor), wave-14 shields (star-tip pairs reaching rel
14.5, i.e. 3.5 deg from the dart axis at r 162-192 — the angular
neighbor), wave-13 teardrop (star-tip on-axis, far)."""
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

fit = json.loads((SESS / "iterations/56/measure/wave15-fit.json").read_text())
rows = fit["rows"]
plus = [(v["r"], v["x"]) for v in rows[1:-1]]
model = ([(rows[0]["r"], 0.0)] + plus + [(rows[-1]["r"], 0.0)]
         + [(r, -x) for r, x in reversed(plus)])

mask = Image.new("1", (a.shape[1], a.shape[0]), 0)
d = ImageDraw.Draw(mask)
for k in range(10):
    axis = k * 36.0 + 18.0
    pts = []
    for r, rel in model:
        t = math.radians(axis + rel)
        pts.append((cx + r * PXU * math.cos(t), cy - r * PXU * math.sin(t)))
    d.polygon(pts, fill=1)
stamp = np.asarray(mask, dtype=bool)
print(f"stamped px: {stamp.sum()}")

w15ids = []
for wnum in range(1, 23):
    w = next(w for w in plan["waves"] if w["wave"] == wnum)
    ids = [s["id"] for s in w["shapes"] if not s["fragment"]]
    if wnum == 15:
        w15ids = ids
    wmask = np.isin(labels, ids)
    ov = (stamp & wmask).sum()
    tag = "ON-TARGET" if wnum == 15 else ("OK" if ov == 0 else "OVERLAP!")
    print(f"wave {wnum:2d}: overlap {ov} px ({ov / stamp.sum() * 100:.1f}% of stamp) {tag}")

# off-target attribution: every stamp px not on the wave-15 mask must be
# near-white band, a wave-15 fragment, or named "other" (loud, Tenet 3)
on = (stamp & np.isin(labels, w15ids)).sum()
off = stamp & ~np.isin(labels, w15ids)
w15all = next(w for w in plan["waves"] if w["wave"] == 15)
frag_ids = [s["id"] for s in w15all["shapes"] if s["fragment"]]
off_white = (off & near_white).sum()
off_frag = (off & np.isin(labels, frag_ids)).sum()
off_other = off.sum() - off_white - off_frag
print(f"\non-target: {on} px ({on / stamp.sum() * 100:.1f}%)")
print(f"off-target: {off.sum()} px = near-white {off_white} "
      f"({off_white / stamp.sum() * 100:.1f}%) + w15-fragments {off_frag} "
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

# our star at dart axis +18
w15_xy = to_xy([(r, 18.0 + t) for r, t in model])

w12 = json.loads((SESS / "iterations/53/measure/wave12-fit.json").read_text())
p12 = [(v["r"], v["x"]) for v in w12["rows"][1:-1]]
m12 = ([(w12["rows"][0]["r"], 0.0)] + p12 + [(w12["rows"][-1]["r"], 0.0)]
       + [(r, -x) for r, x in reversed(p12)])
bell = to_xy([(r, 18.0 + t) for r, t in m12])
print(f"\nmin dist vs w12 bell (same dart axis 18): "
      f"{poly_min_dist(w15_xy, bell):.2f} u")

w14 = json.loads((SESS / "iterations/55/measure/wave14-fit.json").read_text())
sh_plus = to_xy([(v["r"], v["rel"]) for v in w14["vertices"]])          # axis 0, + member (rel up to 14.5)
sh_minus_36 = to_xy([(v["r"], 36.0 - v["rel"]) for v in w14["vertices"]])  # axis 36, mirror member
print(f"min dist vs w14 shield + member (axis 0, below): "
      f"{poly_min_dist(w15_xy, sh_plus):.2f} u")
print(f"min dist vs w14 shield - member (axis 36, above): "
      f"{poly_min_dist(w15_xy, sh_minus_36):.2f} u")

w13 = json.loads((SESS / "iterations/54/measure/wave13-fit.json").read_text())
p13 = [(v["r"], v["x"]) for v in w13["rows"][1:-1]]
m13 = ([(w13["rows"][0]["r"], 0.0)] + p13 + [(w13["rows"][-1]["r"], 0.0)]
       + [(r, -x) for r, x in reversed(p13)])
for ax in (0.0, 36.0):
    td = to_xy([(r, ax + t) for r, t in m13])
    print(f"min dist vs w13 teardrop (axis {ax:.0f}): "
          f"{poly_min_dist(w15_xy, td):.2f} u")
