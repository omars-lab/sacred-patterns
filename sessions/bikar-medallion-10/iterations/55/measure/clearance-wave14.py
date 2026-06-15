#!/usr/bin/env python3
"""Iter-56 wave-14 clearance proof — rasterize the 20 snapped shield
stamps (mirror PAIR per star-tip axis: + member at fitted rel, mirror
member at -rel) in reference px space; count overlap px against
reference waves 1-13 + unbuilt 15-22 (must be 0), attribute off-target
px, then compute model-vs-model min distances against OUR built
neighbors on/near the same star-tip axes: wave-13 teardrop (on-axis,
r 151.4-185.1, flank rel +-4.25-4.5), wave-11 birds (same axes, rel
3.75-11.25, r 145.9-161 — radially overlapping our 162-192 band, the
close one), wave-14's own mirror partner across the axis, and the
next-axis neighbor pair."""
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

fit = json.loads((SESS / "iterations/55/measure/wave14-fit.json").read_text())
plus = [(v["r"], v["rel"]) for v in fit["vertices"]]
minus = [(r, -x) for r, x in plus]

mask = Image.new("1", (a.shape[1], a.shape[0]), 0)
d = ImageDraw.Draw(mask)
for k in range(10):
    axis = k * 36.0
    for member in (plus, minus):
        pts = []
        for r, rel in member:
            t = math.radians(axis + rel)
            pts.append((cx + r * PXU * math.cos(t), cy - r * PXU * math.sin(t)))
        d.polygon(pts, fill=1)
stamp = np.asarray(mask, dtype=bool)
print(f"stamped px: {stamp.sum()}")

w14ids = []
for wnum in range(1, 23):
    w = next(w for w in plan["waves"] if w["wave"] == wnum)
    ids = [s["id"] for s in w["shapes"] if not s["fragment"]]
    if wnum == 14:
        w14ids = ids
    wmask = np.isin(labels, ids)
    ov = (stamp & wmask).sum()
    tag = "ON-TARGET" if wnum == 14 else ("OK" if ov == 0 else "OVERLAP!")
    print(f"wave {wnum:2d}: overlap {ov} px ({ov / stamp.sum() * 100:.1f}% of stamp) {tag}")

# off-target attribution: every stamp px not on the wave-14 mask must be
# near-white band, a wave-14 fragment, or named "other" (loud, Tenet 3)
on = (stamp & np.isin(labels, w14ids)).sum()
off = stamp & ~np.isin(labels, w14ids)
w14all = next(w for w in plan["waves"] if w["wave"] == 14)
frag_ids = [s["id"] for s in w14all["shapes"] if s["fragment"]]
off_white = (off & near_white).sum()
off_frag = (off & np.isin(labels, frag_ids)).sum()
off_other = off.sum() - off_white - off_frag
print(f"\non-target: {on} px ({on / stamp.sum() * 100:.1f}%)")
print(f"off-target: {off.sum()} px = near-white {off_white} "
      f"({off_white / stamp.sum() * 100:.1f}%) + w14-fragments {off_frag} "
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

w14_plus = to_xy(plus)   # axis 0, + member
w14_minus = to_xy(minus)  # axis 0, mirror member
print(f"\nmin dist + member vs own mirror (across axis 0): "
      f"{poly_min_dist(w14_plus, w14_minus):.2f} u")

w13 = json.loads((SESS / "iterations/54/measure/wave13-fit.json").read_text())
rows13 = w13["rows"]
p13 = [(v["r"], v["x"]) for v in rows13[1:-1]]
m13 = ([(rows13[0]["r"], 0.0)] + p13 + [(rows13[-1]["r"], 0.0)]
       + [(r, -x) for r, x in reversed(p13)])
print(f"min dist + member vs w13 teardrop (same axis 0): "
      f"{poly_min_dist(w14_plus, to_xy(m13)):.2f} u")

w11 = json.loads((SESS / "iterations/52/measure/wave11-fit.json").read_text())
bird_plus = to_xy([(v["r"], v["cpt_plus"] * 360 / v["M"]) for v in w11["vertices"]])
bird_minus = to_xy([(v["r"], v["cpt_mirror"] * 360 / v["M"] - 360) for v in w11["vertices"]])
print(f"min dist + member vs w11 bird + member (axis 0): "
      f"{poly_min_dist(w14_plus, bird_plus):.2f} u")
print(f"min dist - member vs w11 bird - member (axis 0): "
      f"{poly_min_dist(w14_minus, bird_minus):.2f} u")

# next-axis neighbor: our + member (rel up to 14.5) vs the NEXT axis's
# mirror member (axis 36, rel down to 36-14.5 = 21.5)
next_minus = to_xy([(r, 36.0 - x) for r, x in plus])
print(f"min dist + member vs next-axis mirror member (axis 36): "
      f"{poly_min_dist(w14_plus, next_minus):.2f} u")

w9 = json.loads((SESS / "iterations/50/measure/wave9-fit.json").read_text())
p9 = [(v["r"], v["x"]) for v in w9["vertices"][1:-1]]
m9 = ([(w9["vertices"][0]["r"], 0.0)] + p9 + [(w9["vertices"][-1]["r"], 0.0)]
      + [(r, -x) for r, x in reversed(p9)])
print(f"min dist + member vs w9 16-gon (same axis 0): "
      f"{poly_min_dist(w14_plus, to_xy(m9)):.2f} u")
