#!/usr/bin/env python3
"""Iter-60 wave-18 clearance proof — rasterize all 10 snapped royal
TEN-POINTED-STAR stamps (ONE axis-symmetric 20-vert polygon per STAR-TIP
axis, 0 mod 36 — wave-13 on-axis topology, rows from wave18-fit.json) in
reference px space; count overlap px against reference waves 1-17 +
unbuilt 19-22 (must be 0), attribute off-target px (loud, Tenet 3), then
compute model-vs-model min distances vs the built neighbors:
  - vs OUR w16 sails/fins (SAME star-tip axes; inner r 179-195 rel +-2.7,
    outer r 195-209 rel +-5.25..8.75 — BOTH radially overlap our
    194.9-235.0 band: prime face-split suspects),
  - vs OUR w14 shields (same axes, r 162-192 — radially inside, check),
  - vs OUR w17 house-pentagons (DART axes 18 mod 36; nose rel 0.75 ->
    17.25 deg from our star-tip line, r-band 187-225 overlaps ours),
  - vs OUR w13 teardrop (same axis, ON-axis, apex r 185.1 vs our inner
    point 194.9 — direct radial neighbor along the axis itself)."""
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

fit = json.loads((SESS / "iterations/59/measure/wave18-fit.json").read_text())
mid = [(v["r"], v["x"]) for v in fit["rows"][1:-1]]
star18 = ([(fit["rows"][0]["r"], 0.0)] + mid
          + [(fit["rows"][-1]["r"], 0.0)] + [(r, -x) for r, x in reversed(mid)])

mask = Image.new("1", (a.shape[1], a.shape[0]), 0)
d = ImageDraw.Draw(mask)
for k in range(10):
    axis = k * 36.0  # STAR-TIP axes
    pts = []
    for r, t in star18:
        th = math.radians(axis + t)
        pts.append((cx + r * PXU * math.cos(th), cy - r * PXU * math.sin(th)))
    d.polygon(pts, fill=1)
stamp = np.asarray(mask, dtype=bool)
print(f"stamped px (10 stamps): {stamp.sum()}")

w18ids = []
for wnum in range(1, 23):
    w = next(w for w in plan["waves"] if w["wave"] == wnum)
    ids = [s["id"] for s in w["shapes"] if not s["fragment"]]
    if wnum == 18:
        w18ids = ids
    wmask = np.isin(labels, ids)
    ov = (stamp & wmask).sum()
    tag = "ON-TARGET" if wnum == 18 else ("OK" if ov == 0 else "OVERLAP!")
    print(f"wave {wnum:2d}: overlap {ov} px ({ov / stamp.sum() * 100:.1f}% of stamp) {tag}")

# off-target attribution: every stamp px not on the wave-18 mask must be
# near-white band, a wave-18 fragment, or named "other" (loud, Tenet 3)
on = (stamp & np.isin(labels, w18ids)).sum()
off = stamp & ~np.isin(labels, w18ids)
w18all = next(w for w in plan["waves"] if w["wave"] == 18)
frag_ids = [s["id"] for s in w18all["shapes"] if s["fragment"]]
off_white = (off & near_white).sum()
off_frag = (off & np.isin(labels, frag_ids)).sum()
off_other = off.sum() - off_white - off_frag
print(f"\non-target: {on} px ({on / stamp.sum() * 100:.1f}%)")
print(f"off-target: {off.sum()} px = near-white {off_white} "
      f"({off_white / stamp.sum() * 100:.1f}%) + w18-fragments {off_frag} "
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

# our stamp at star-tip axis 0 (absolute frame)
star_xy = to_xy([(r, 0.0 + t) for r, t in star18])

# w16 families: SAME star-tip axes, mirror pairs — check both members at
# axis 0 (their +- rel straddle our on-axis star).
w16 = json.loads((SESS / "iterations/57/measure/wave16-fit.json").read_text())
for fam in ("inner", "outer"):
    fv = [(v["r"], v["rel"]) for v in w16[fam]["vertices"]]
    for sign, nm in ((1, "+"), (-1, "-")):
        member = to_xy([(r, sign * rel) for r, rel in fv])
        print(f"min dist star vs w16 {fam}{nm} (same axis 0): "
              f"{poly_min_dist(star_xy, member):.2f} u")

# w14 shields: same axes, radially inside (r 162-192 vs our 194.9 inner).
w14 = json.loads((SESS / "iterations/55/measure/wave14-fit.json").read_text())
shv = [(v["r"], v["rel"]) for v in w14["vertices"]]
for sign, nm in ((1, "+"), (-1, "-")):
    member = to_xy([(r, sign * rel) for r, rel in shv])
    print(f"min dist star vs w14 shield{nm} (same axis 0): "
          f"{poly_min_dist(star_xy, member):.2f} u")

# w17 pentagons: DART axes; nearest dart lines to axis 0 are +-18. The
# member whose verts lean back toward us is the mirror at +18 (18-rel)
# and the + member at -18 (-18+rel) — check both.
w17 = json.loads((SESS / "iterations/58/measure/wave17-fit.json").read_text())
pv = [(v["r"], v["rel"]) for v in w17["pent"]["vertices"]]
pent18m = to_xy([(r, 18.0 - rel) for r, rel in pv])
pentm18p = to_xy([(r, -18.0 + rel) for r, rel in pv])
print(f"min dist star vs w17 pent (dart-18 mirror member): "
      f"{poly_min_dist(star_xy, pent18m):.2f} u")
print(f"min dist star vs w17 pent (dart--18 + member): "
      f"{poly_min_dist(star_xy, pentm18p):.2f} u")

# w13 teardrop: ON the same axis, apex r 185.1 vs our inner point 194.9.
w13 = json.loads((SESS / "iterations/54/measure/wave13-fit.json").read_text())
p13 = [(v["r"], v["x"]) for v in w13["rows"][1:-1]]
m13 = ([(w13["rows"][0]["r"], 0.0)] + p13 + [(w13["rows"][-1]["r"], 0.0)]
       + [(r, -x) for r, x in reversed(p13)])
tear = to_xy([(r, 0.0 + t) for r, t in m13])
print(f"min dist star vs w13 teardrop (same axis 0, on-axis): "
      f"{poly_min_dist(star_xy, tear):.2f} u")
