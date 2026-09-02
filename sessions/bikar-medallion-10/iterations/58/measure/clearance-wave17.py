#!/usr/bin/env python3
"""Iter-59 wave-17 clearance proof — rasterize all 20 snapped navy
house-pentagon stamps (2 per DART axis: + member at axis+rel, mirror at
axis-rel — free 6-vert polygon from wave17-fit.json, wave-10 mirror-pair
topology) in reference px space; count overlap px against reference
waves 1-16 + unbuilt 18-22 (must be 0), attribute off-target px (loud,
Tenet 3), then compute model-vs-model min distances:
  - + member vs mirror member (across the dart line — our verts reach
    rel 0.75, i.e. 1.5 deg between the pair's nearest verts),
  - vs OUR w15 pentagrams (SAME dart axes, apex r 194.3 vs our r-band
    187-225 — prime radial-neighbor/face-split suspect),
  - vs OUR w16 sails/fins (star-tip axes; outer family reaches rel 8.75
    = 9.25 deg from the dart line, r 195-209 overlapping our band —
    prime ANGULAR suspect),
  - vs OUR w12 bell (same dart axes, apex r 170.7 — radially inside),
  - vs OUR w14 shields (star-tip axes, r 162-192, rel up to 14.5 —
    3.5 deg from the dart line at the far edge: check)."""
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

fit = json.loads((SESS / "iterations/58/measure/wave17-fit.json").read_text())
pent = [(v["r"], v["rel"]) for v in fit["pent"]["vertices"]]

mask = Image.new("1", (a.shape[1], a.shape[0]), 0)
d = ImageDraw.Draw(mask)
for k in range(10):
    axis = k * 36.0 + 18.0  # DART axes
    for sign in (1, -1):
        pts = []
        for r, rel in pent:
            t = math.radians(axis + sign * rel)
            pts.append((cx + r * PXU * math.cos(t), cy - r * PXU * math.sin(t)))
        d.polygon(pts, fill=1)
stamp = np.asarray(mask, dtype=bool)
print(f"stamped px (20 stamps): {stamp.sum()}")

w17ids = []
for wnum in range(1, 23):
    w = next(w for w in plan["waves"] if w["wave"] == wnum)
    ids = [s["id"] for s in w["shapes"] if not s["fragment"]]
    if wnum == 17:
        w17ids = ids
    wmask = np.isin(labels, ids)
    ov = (stamp & wmask).sum()
    tag = "ON-TARGET" if wnum == 17 else ("OK" if ov == 0 else "OVERLAP!")
    print(f"wave {wnum:2d}: overlap {ov} px ({ov / stamp.sum() * 100:.1f}% of stamp) {tag}")

# off-target attribution: every stamp px not on the wave-17 mask must be
# near-white band, a wave-17 fragment, or named "other" (loud, Tenet 3)
on = (stamp & np.isin(labels, w17ids)).sum()
off = stamp & ~np.isin(labels, w17ids)
w17all = next(w for w in plan["waves"] if w["wave"] == 17)
frag_ids = [s["id"] for s in w17all["shapes"] if s["fragment"]]
off_white = (off & near_white).sum()
off_frag = (off & np.isin(labels, frag_ids)).sum()
off_other = off.sum() - off_white - off_frag
print(f"\non-target: {on} px ({on / stamp.sum() * 100:.1f}%)")
print(f"off-target: {off.sum()} px = near-white {off_white} "
      f"({off_white / stamp.sum() * 100:.1f}%) + w17-fragments {off_frag} "
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

# our two stamps at dart axis 18 (absolute frame)
pent_p = to_xy([(r, 18.0 + rel) for r, rel in pent])
pent_m = to_xy([(r, 18.0 - rel) for r, rel in pent])
print(f"\nmin dist pent+ vs pent- (across dart line): "
      f"{poly_min_dist(pent_p, pent_m):.2f} u")

w15 = json.loads((SESS / "iterations/56/measure/wave15-fit.json").read_text())
p15 = [(v["r"], v["x"]) for v in w15["rows"][1:-1]]
m15 = ([(w15["rows"][0]["r"], 0.0)] + p15 + [(w15["rows"][-1]["r"], 0.0)]
       + [(r, -x) for r, x in reversed(p15)])
star = to_xy([(r, 18.0 + t) for r, t in m15])  # same dart axis 18
for nm, ours in (("pent+", pent_p), ("pent-", pent_m)):
    print(f"min dist {nm} vs w15 pentagram (same dart axis 18): "
          f"{poly_min_dist(ours, star):.2f} u")

w12 = json.loads((SESS / "iterations/53/measure/wave12-fit.json").read_text())
p12 = [(v["r"], v["x"]) for v in w12["rows"][1:-1]]
m12 = ([(w12["rows"][0]["r"], 0.0)] + p12 + [(w12["rows"][-1]["r"], 0.0)]
       + [(r, -x) for r, x in reversed(p12)])
bell = to_xy([(r, 18.0 + t) for r, t in m12])  # same dart axis 18
print(f"min dist pent+ vs w12 bell (same dart axis 18): "
      f"{poly_min_dist(pent_p, bell):.2f} u")

# w16 families live on star-tip axes; nearest star-tip lines to dart
# axis 18 are 0 and 36 — check our + member vs axis-36 mirror members
# (their -rel side faces us) and vs axis-0 + members.
w16 = json.loads((SESS / "iterations/57/measure/wave16-fit.json").read_text())
for fam in ("inner", "outer"):
    fv = [(v["r"], v["rel"]) for v in w16[fam]["vertices"]]
    fam36m = to_xy([(r, 36.0 - rel) for r, rel in fv])  # axis 36, mirror side
    fam0p = to_xy([(r, 0.0 + rel) for r, rel in fv])    # axis 0, + side
    print(f"min dist pent+ vs w16 {fam} (axis-36 mirror): "
          f"{poly_min_dist(pent_p, fam36m):.2f} u")
    print(f"min dist pent- vs w16 {fam} (axis-0 +): "
          f"{poly_min_dist(pent_m, fam0p):.2f} u")

w14 = json.loads((SESS / "iterations/55/measure/wave14-fit.json").read_text())
shv = [(v["r"], v["rel"]) for v in w14["vertices"]]
sh36m = to_xy([(r, 36.0 - rel) for r, rel in shv])
sh0p = to_xy([(r, 0.0 + rel) for r, rel in shv])
print(f"min dist pent+ vs w14 shield (axis-36 mirror): "
      f"{poly_min_dist(pent_p, sh36m):.2f} u")
print(f"min dist pent- vs w14 shield (axis-0 +): "
      f"{poly_min_dist(pent_m, sh0p):.2f} u")
