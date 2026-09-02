#!/usr/bin/env python3
"""Iter-58 wave-16 clearance proof — rasterize all 40 snapped sail/fin
stamps (4 per STAR-TIP axis: inner family + member at axis+rel, inner
mirror at axis-rel, outer + member, outer mirror — free polygons from
wave16-fit.json, wave-7/14 mirror-pair style) in reference px space;
count overlap px against reference waves 1-15 + unbuilt 17-22 (must be
0), attribute off-target px (loud, Tenet 3), then compute model-vs-model
min distances:
  - inner+ vs outer+ (same axis, same side — the new family gap),
  - inner+ vs inner- and outer+ vs outer- (across the star-tip line),
  - vs OUR w14 shields (SAME star-tip axes, r 162-192, rel up to 14.5 —
    prime face-split suspect: radially inside/overlapping our r-band),
  - vs OUR w13 teardrop (on-axis, apex r 185.1 — radial neighbor),
  - vs OUR w15 pentagrams (dart axes 18 mod 36 — outer family reaches
    rel 8.75, i.e. 9.25 deg from the dart line: far but check)."""
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

fit = json.loads((SESS / "iterations/57/measure/wave16-fit.json").read_text())
fams = {
    name: [(v["r"], v["rel"]) for v in fit[name]["vertices"]]
    for name in ("inner", "outer")
}

mask = Image.new("1", (a.shape[1], a.shape[0]), 0)
d = ImageDraw.Draw(mask)
for k in range(10):
    axis = k * 36.0
    for fam in fams.values():
        for sign in (1, -1):
            pts = []
            for r, rel in fam:
                t = math.radians(axis + sign * rel)
                pts.append((cx + r * PXU * math.cos(t), cy - r * PXU * math.sin(t)))
            d.polygon(pts, fill=1)
stamp = np.asarray(mask, dtype=bool)
print(f"stamped px (40 stamps): {stamp.sum()}")

w16ids = []
for wnum in range(1, 23):
    w = next(w for w in plan["waves"] if w["wave"] == wnum)
    ids = [s["id"] for s in w["shapes"] if not s["fragment"]]
    if wnum == 16:
        w16ids = ids
    wmask = np.isin(labels, ids)
    ov = (stamp & wmask).sum()
    tag = "ON-TARGET" if wnum == 16 else ("OK" if ov == 0 else "OVERLAP!")
    print(f"wave {wnum:2d}: overlap {ov} px ({ov / stamp.sum() * 100:.1f}% of stamp) {tag}")

# off-target attribution: every stamp px not on the wave-16 mask must be
# near-white band, a wave-16 fragment, or named "other" (loud, Tenet 3)
on = (stamp & np.isin(labels, w16ids)).sum()
off = stamp & ~np.isin(labels, w16ids)
w16all = next(w for w in plan["waves"] if w["wave"] == 16)
frag_ids = [s["id"] for s in w16all["shapes"] if s["fragment"]]
off_white = (off & near_white).sum()
off_frag = (off & np.isin(labels, frag_ids)).sum()
off_other = off.sum() - off_white - off_frag
print(f"\non-target: {on} px ({on / stamp.sum() * 100:.1f}%)")
print(f"off-target: {off.sum()} px = near-white {off_white} "
      f"({off_white / stamp.sum() * 100:.1f}%) + w16-fragments {off_frag} "
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

# our four stamps at star-tip axis 0
inner_p = to_xy([(r, rel) for r, rel in fams["inner"]])
inner_m = to_xy([(r, -rel) for r, rel in fams["inner"]])
outer_p = to_xy([(r, rel) for r, rel in fams["outer"]])
outer_m = to_xy([(r, -rel) for r, rel in fams["outer"]])

print(f"\nmin dist inner+ vs outer+ (same axis, same side): "
      f"{poly_min_dist(inner_p, outer_p):.2f} u")
print(f"min dist inner+ vs inner- (across star-tip line): "
      f"{poly_min_dist(inner_p, inner_m):.2f} u")
print(f"min dist outer+ vs outer- (across star-tip line): "
      f"{poly_min_dist(outer_p, outer_m):.2f} u")

w14 = json.loads((SESS / "iterations/55/measure/wave14-fit.json").read_text())
sh_plus = to_xy([(v["r"], v["rel"]) for v in w14["vertices"]])
sh_minus = to_xy([(v["r"], -v["rel"]) for v in w14["vertices"]])
for nm, ours in (("inner+", inner_p), ("inner-", inner_m),
                 ("outer+", outer_p), ("outer-", outer_m)):
    print(f"min dist {nm} vs w14 shield + member (axis 0): "
          f"{poly_min_dist(ours, sh_plus):.2f} u")
    print(f"min dist {nm} vs w14 shield - member (axis 0): "
          f"{poly_min_dist(ours, sh_minus):.2f} u")

w13 = json.loads((SESS / "iterations/54/measure/wave13-fit.json").read_text())
p13 = [(v["r"], v["x"]) for v in w13["rows"][1:-1]]
m13 = ([(w13["rows"][0]["r"], 0.0)] + p13 + [(w13["rows"][-1]["r"], 0.0)]
       + [(r, -x) for r, x in reversed(p13)])
td = to_xy([(r, t) for r, t in m13])  # axis 0 on-axis
for nm, ours in (("inner+", inner_p), ("outer+", outer_p)):
    print(f"min dist {nm} vs w13 teardrop (axis 0): "
          f"{poly_min_dist(ours, td):.2f} u")

w15 = json.loads((SESS / "iterations/56/measure/wave15-fit.json").read_text())
p15 = [(v["r"], v["x"]) for v in w15["rows"][1:-1]]
m15 = ([(w15["rows"][0]["r"], 0.0)] + p15 + [(w15["rows"][-1]["r"], 0.0)]
       + [(r, -x) for r, x in reversed(p15)])
star = to_xy([(r, 18.0 + t) for r, t in m15])  # dart axis +18
for nm, ours in (("outer+", outer_p), ("inner+", inner_p)):
    print(f"min dist {nm} vs w15 pentagram (dart axis 18): "
          f"{poly_min_dist(ours, star):.2f} u")
