#!/usr/bin/env python3
"""Iter-63 wave-21 clearance proof — rasterize all 40 snapped deep_navy
wedge stamps (TWO families x one mirror pair per STAR-TIP axis: inner
5-vert at rel ~+-2, outer 7-vert at rel ~+-5.7 — wave-16 two-family
topology, from wave21-fit.json) in reference px space; count overlap px
against reference waves 1-20 + unbuilt 22 (must be 0), attribute
off-target px (loud, Tenet 3), then compute model-vs-model min
distances vs the built neighbors:
  - inner vs OUR w18 star (same star-tip axis, its tip reaches r 235
    on-axis vs our inner verts r 236.6-251.6 at rel 0.75-3.0 — prime
    RADIAL suspect for inner),
  - outer vs OUR w20 pentagon (adjacent dart axis: its vertex at
    rel 10.75 from dart = 7.25 deg from OUR star-tip axis, exactly our
    outer family's angular zone — prime ANGULAR suspect),
  - outer vs OUR w19 kite (same star-tip axis, r 214-222.5 radially
    inside us at overlapping rel — prime suspect #2),
  - inner vs outer (same axis, same sign — intra-wave gap),
  - inner+ vs inner- (across the star-tip line),
  - outer vs w16 outer fin (same axis, radially inside — check)."""
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

fit = json.loads((SESS / "iterations/62/measure/wave21-fit.json").read_text())
fams = {name: [(v["r"], v["rel"]) for v in fit[name]["vertices"]]
        for name in ("inner", "outer")}

mask = Image.new("1", (a.shape[1], a.shape[0]), 0)
d = ImageDraw.Draw(mask)
for k in range(10):
    axis = k * 36.0  # STAR-TIP axes
    for verts in fams.values():
        for sign in (1, -1):
            pts = []
            for r, rel in verts:
                t = math.radians(axis + sign * rel)
                pts.append((cx + r * PXU * math.cos(t), cy - r * PXU * math.sin(t)))
            d.polygon(pts, fill=1)
stamp = np.asarray(mask, dtype=bool)
print(f"stamped px (40 stamps): {stamp.sum()}")

w21ids = []
for wnum in range(1, 23):
    w = next(w for w in plan["waves"] if w["wave"] == wnum)
    ids = [s["id"] for s in w["shapes"] if not s["fragment"]]
    if wnum == 21:
        w21ids = ids
    wmask = np.isin(labels, ids)
    ov = (stamp & wmask).sum()
    tag = "ON-TARGET" if wnum == 21 else ("OK" if ov == 0 else "OVERLAP!")
    print(f"wave {wnum:2d}: overlap {ov} px ({ov / stamp.sum() * 100:.1f}% of stamp) {tag}")

# off-target attribution: every stamp px not on the wave-21 mask must be
# near-white band, a wave-21 fragment, or named "other" (loud, Tenet 3).
# NOTE: one outer + member is fragmented in the plan (39 real + 4
# fragments) — its stamp area should attribute to fragments/near-white.
on = (stamp & np.isin(labels, w21ids)).sum()
off = stamp & ~np.isin(labels, w21ids)
w21all = next(w for w in plan["waves"] if w["wave"] == 21)
frag_ids = [s["id"] for s in w21all["shapes"] if s["fragment"]]
off_white = (off & near_white).sum()
off_frag = (off & np.isin(labels, frag_ids)).sum()
off_other = off.sum() - off_white - off_frag
print(f"\non-target: {on} px ({on / stamp.sum() * 100:.1f}%)")
print(f"off-target: {off.sum()} px = near-white {off_white} "
      f"({off_white / stamp.sum() * 100:.1f}%) + w21-fragments {off_frag} "
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

# our four stamps at star-tip axis 0 (absolute frame)
inner_p = to_xy([(r, rel) for r, rel in fams["inner"]])
inner_m = to_xy([(r, -rel) for r, rel in fams["inner"]])
outer_p = to_xy([(r, rel) for r, rel in fams["outer"]])
outer_m = to_xy([(r, -rel) for r, rel in fams["outer"]])
print(f"\nmin dist inner+ vs inner- (across the star-tip line): "
      f"{poly_min_dist(inner_p, inner_m):.2f} u")
print(f"min dist inner+ vs outer+ (same axis, same sign): "
      f"{poly_min_dist(inner_p, outer_p):.2f} u")
print(f"min dist outer+ vs outer- (across the star-tip line): "
      f"{poly_min_dist(outer_p, outer_m):.2f} u")

# w18 star ON our axis (axis-symmetric expand of fit rows) — its tip
# reaches r 235 at rel 0; our inner sits r 236.6+ at rel 0.75+.
w18 = json.loads((SESS / "iterations/59/measure/wave18-fit.json").read_text())
p18 = [(v["r"], v["x"]) for v in w18["rows"][1:-1]]
m18 = ([(w18["rows"][0]["r"], 0.0)] + p18 + [(w18["rows"][-1]["r"], 0.0)]
       + [(r, -x) for r, x in reversed(p18)])
star = to_xy(m18)
print(f"min dist inner+ vs w18 star (same star-tip axis): "
      f"{poly_min_dist(inner_p, star):.2f} u")
print(f"min dist outer+ vs w18 star (same star-tip axis): "
      f"{poly_min_dist(outer_p, star):.2f} u")

# w20 pentagon on the adjacent dart axis 18: its mirror member
# (18 - rel) leans back toward our star-tip axis 0 — verts down to
# 18 - 10.75 = 7.25 deg absolute, exactly our outer family's zone.
w20 = json.loads((SESS / "iterations/61/measure/wave20-fit.json").read_text())
pv = [(v["r"], v["rel"]) for v in w20["pent"]["vertices"]]
pent18m = to_xy([(r, 18.0 - rel) for r, rel in pv])
print(f"min dist outer+ vs w20 pentagon (dart-18 mirror member): "
      f"{poly_min_dist(outer_p, pent18m):.2f} u")
print(f"min dist inner+ vs w20 pentagon (dart-18 mirror member): "
      f"{poly_min_dist(inner_p, pent18m):.2f} u")

# w19 kite on OUR axis (+ member, rel 6.0-8.45, r 214-222.5 — radially
# inside our outer family at overlapping rel).
w19 = json.loads((SESS / "iterations/60/measure/wave19-fit.json").read_text())
kv = [(v["r"], v["rel"]) for v in w19["kite"]["vertices"]]
kite_p = to_xy(kv)
print(f"min dist outer+ vs w19 kite (same axis, + member): "
      f"{poly_min_dist(outer_p, kite_p):.2f} u")

# w16 outer fin on OUR axis (+ member) — radially inside, check only.
w16 = json.loads((SESS / "iterations/57/measure/wave16-fit.json").read_text())
fv = [(v["r"], v["rel"]) for v in w16["outer"]["vertices"]]
fin_p = to_xy(fv)
print(f"min dist outer+ vs w16 outer fin (same axis, + member): "
      f"{poly_min_dist(outer_p, fin_p):.2f} u")
