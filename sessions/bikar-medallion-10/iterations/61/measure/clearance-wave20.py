#!/usr/bin/env python3
"""Iter-62 wave-20 clearance proof — rasterize all 20 snapped navy
outer-lobe pentagon stamps (2 per DART axis: + member at axis+rel,
mirror at axis-rel — free 6-vert polygon from wave20-fit.json,
wave-10/17 mirror-pair topology) in reference px space; count overlap
px against reference waves 1-19 + unbuilt 21-22 (must be 0), attribute
off-target px (loud, Tenet 3), then compute model-vs-model min
distances vs the built neighbors:
  - vs OUR w17 house-pentagons (SAME dart axes: their outer reach
    r ~224 vs our inner verts r 222.7-226.5 — prime RADIAL suspect),
  - vs OUR w19 kites (star-tip axes: their mirror member at axis 36
    leans back toward our + member — prime ANGULAR suspect),
  - vs OUR w18 stars (star-tip axes, outer band r 194.9-235 — check),
  - vs OUR w14 shields + w16 fins (star-tip families radially
    inside/adjacent — check)."""
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

fit = json.loads((SESS / "iterations/61/measure/wave20-fit.json").read_text())
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

w20ids = []
for wnum in range(1, 23):
    w = next(w for w in plan["waves"] if w["wave"] == wnum)
    ids = [s["id"] for s in w["shapes"] if not s["fragment"]]
    if wnum == 20:
        w20ids = ids
    wmask = np.isin(labels, ids)
    ov = (stamp & wmask).sum()
    tag = "ON-TARGET" if wnum == 20 else ("OK" if ov == 0 else "OVERLAP!")
    print(f"wave {wnum:2d}: overlap {ov} px ({ov / stamp.sum() * 100:.1f}% of stamp) {tag}")

# off-target attribution: every stamp px not on the wave-20 mask must be
# near-white band, a wave-20 fragment, or named "other" (loud, Tenet 3)
on = (stamp & np.isin(labels, w20ids)).sum()
off = stamp & ~np.isin(labels, w20ids)
w20all = next(w for w in plan["waves"] if w["wave"] == 20)
frag_ids = [s["id"] for s in w20all["shapes"] if s["fragment"]]
off_white = (off & near_white).sum()
off_frag = (off & np.isin(labels, frag_ids)).sum()
off_other = off.sum() - off_white - off_frag
print(f"\non-target: {on} px ({on / stamp.sum() * 100:.1f}%)")
print(f"off-target: {off.sum()} px = near-white {off_white} "
      f"({off_white / stamp.sum() * 100:.1f}%) + w20-fragments {off_frag} "
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

# our two stamps at dart axis 18 (absolute frame); the + member leans
# toward star-tip axis 36, the mirror toward axis 0.
pent_p = to_xy([(r, 18.0 + rel) for r, rel in pent])
pent_m = to_xy([(r, 18.0 - rel) for r, rel in pent])
print(f"\nmin dist pent+ vs pent- (across the dart line): "
      f"{poly_min_dist(pent_p, pent_m):.2f} u")

# w17 house-pentagons: SAME dart axis (prime radial suspect, both members)
w17 = json.loads((SESS / "iterations/58/measure/wave17-fit.json").read_text())
pv = [(v["r"], v["rel"]) for v in w17["pent"]["vertices"]]
for tag, sgn in (("+", 1), ("-", -1)):
    member = to_xy([(r, 18.0 + sgn * rel) for r, rel in pv])
    print(f"min dist pent+ vs w17 pent{tag} (same dart axis 18): "
          f"{poly_min_dist(pent_p, member):.2f} u")

# w19 kites: star-tip axis 36; its mirror member (36 - rel) leans back
# toward our + member (prime angular suspect). Check the + member too.
w19 = json.loads((SESS / "iterations/60/measure/wave19-fit.json").read_text())
kv = [(v["r"], v["rel"]) for v in w19["kite"]["vertices"]]
kite36m = to_xy([(r, 36.0 - rel) for r, rel in kv])
print(f"min dist pent+ vs w19 kite (axis-36 mirror member): "
      f"{poly_min_dist(pent_p, kite36m):.2f} u")

# w18 star: ON star-tip axis 36 (axis-symmetric expand of fit rows)
w18 = json.loads((SESS / "iterations/59/measure/wave18-fit.json").read_text())
p18 = [(v["r"], v["x"]) for v in w18["rows"][1:-1]]
m18 = ([(w18["rows"][0]["r"], 0.0)] + p18 + [(w18["rows"][-1]["r"], 0.0)]
       + [(r, -x) for r, x in reversed(p18)])
star = to_xy([(r, 36.0 + t) for r, t in m18])
print(f"min dist pent+ vs w18 star (star-tip axis 36): "
      f"{poly_min_dist(pent_p, star):.2f} u")

# w14 shields + w16 fins: star-tip families radially inside/adjacent —
# the axis-36 members leaning toward us.
w14 = json.loads((SESS / "iterations/55/measure/wave14-fit.json").read_text())
sv = [(v["r"], v["rel"]) for v in w14["vertices"]]  # flat JSON, no family wrapper
shield36m = to_xy([(r, 36.0 - rel) for r, rel in sv])
print(f"min dist pent+ vs w14 shield (axis-36 mirror member): "
      f"{poly_min_dist(pent_p, shield36m):.2f} u")
w16 = json.loads((SESS / "iterations/57/measure/wave16-fit.json").read_text())
for fam in ("inner", "outer"):
    fv = [(v["r"], v["rel"]) for v in w16[fam]["vertices"]]
    member = to_xy([(r, 36.0 - rel) for r, rel in fv])
    print(f"min dist pent+ vs w16 {fam} (axis-36 mirror member): "
          f"{poly_min_dist(pent_p, member):.2f} u")
