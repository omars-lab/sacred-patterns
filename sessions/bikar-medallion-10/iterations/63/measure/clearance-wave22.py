#!/usr/bin/env python3
"""Iter-64 wave-22 clearance proof — rasterize all 30 snapped navy
stamps (TRIPLETS per STAR-TIP axis: one ON-AXIS axial 10-vert kite
r 246.1-279.1 + mirror flank pair 7-vert shields rel 3.75-10
r 240.1-272.5, from wave22-fit.json) in reference px space; count
overlap px against reference waves 1-21 (must adjudicate cleanly),
attribute off-target px (loud, Tenet 3), then compute model-vs-model
min distances vs the built neighbors. Prime suspects (zones overlap on
paper):
  - axial vs OUR w21 inner wedge (same axis: wedge rel 0.75-3.0
    r 236.6-251.6 vs axial rel<=2.75 r>=246.1 — BOTH ranges overlap;
    the white band between them is all that separates),
  - flank vs OUR w21 outer sail (same axis: sail r tops at 239.4,
    flank floor 240.1 — 0.7u radial proximity at overlapping rel),
  - flank vs w20 pentagon (dart-18 mirror member leans to absolute
    7.25+ deg at r up to 251.4 — inside flank's rel 3.75-10 zone),
  - axial vs w18 star tip (same axis, tip r 235 on-axis vs axial
    apex 246.1 on-axis — pure radial gap ~11u),
  - intra-wave: axial vs flank+ (rel 2.75 edge vs rel 3.75 vertex at
    r~260 — ~1 deg ~ 4.5u, closest intra-wave approach),
  - flank+ vs next axis flank- (across the dart line: rel 10 vs
    absolute 26 — wide, check only).
Expectation (Tenet 26, pre-stated): all model-vs-model gaps >= the
4.21u survival precedent, with the tightest being flank-vs-w21-sail
and axial-vs-flank; overlap px (if any) bright band-edge halo RGB
180-199 EDT-assigned to neighbor seeds, 0 px deep after 2-px erosion.
"""
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

fit = json.loads((SESS / "iterations/63/measure/wave22-fit.json").read_text())
# axial rows -> full symmetric polygon (r, rel): +side walk in row order,
# then -side back, on-axis endpoints once each.
rows = fit["axial"]["rows"]
mid = [(v["r"], v["x"]) for v in rows[1:-1]]
axial_verts = ([(rows[0]["r"], 0.0)] + mid + [(rows[-1]["r"], 0.0)]
               + [(r, -x) for r, x in reversed(mid)])
flank_verts = [(v["r"], v["rel"]) for v in fit["flank"]["vertices"]]

# 30 stamps: per star-tip axis, axial once + flank both signs
mask = Image.new("1", (a.shape[1], a.shape[0]), 0)
d = ImageDraw.Draw(mask)
stamps = {}
for k in range(10):
    axis = k * 36.0
    plans = [("axial", 1, axial_verts), ("flank", 1, flank_verts),
             ("flank", -1, flank_verts)]
    for fam, sign, verts in plans:
        pts = []
        for r, rel in verts:
            t = math.radians(axis + sign * rel)
            pts.append((cx + r * PXU * math.cos(t), cy - r * PXU * math.sin(t)))
        d.polygon(pts, fill=1)
        m = Image.new("1", (a.shape[1], a.shape[0]), 0)
        ImageDraw.Draw(m).polygon(pts, fill=1)
        stamps[(fam, sign, axis)] = np.asarray(m, dtype=bool)
stamp = np.asarray(mask, dtype=bool)
print(f"stamped px (30 stamps): {stamp.sum()}")

w22ids = []
for wnum in range(1, 23):
    w = next(w for w in plan["waves"] if w["wave"] == wnum)
    ids = [s["id"] for s in w["shapes"] if not s["fragment"]]
    if wnum == 22:
        w22ids = ids
    wmask = np.isin(labels, ids)
    ov = (stamp & wmask).sum()
    tag = "ON-TARGET" if wnum == 22 else ("OK" if ov == 0 else "OVERLAP!")
    print(f"wave {wnum:2d}: overlap {ov} px ({ov / stamp.sum() * 100:.1f}% of stamp) {tag}")

on = (stamp & np.isin(labels, w22ids)).sum()
off = stamp & ~np.isin(labels, w22ids)
w22all = next(w for w in plan["waves"] if w["wave"] == 22)
frag_ids = [s["id"] for s in w22all["shapes"] if s["fragment"]]
off_white = (off & near_white).sum()
off_frag = (off & np.isin(labels, frag_ids)).sum()
off_other = off.sum() - off_white - off_frag
print(f"\non-target: {on} px ({on / stamp.sum() * 100:.1f}%)")
print(f"off-target: {off.sum()} px = near-white {off_white} "
      f"({off_white / stamp.sum() * 100:.1f}%) + w22-fragments {off_frag} "
      f"({off_frag / stamp.sum() * 100:.1f}%) + OTHER {off_other} "
      f"({off_other / stamp.sum() * 100:.1f}%)")

# any non-zero neighbor overlap: localize + depth-after-erosion witness
for wnum in range(1, 22):
    w = next(w for w in plan["waves"] if w["wave"] == wnum)
    wmask = np.isin(labels, [s["id"] for s in w["shapes"] if not s["fragment"]])
    ov_all = stamp & wmask
    if ov_all.sum() == 0:
        continue
    eroded = ndimage.binary_erosion(stamp, structure=four, iterations=2)
    deep = (eroded & wmask).sum()
    ys, xs = np.nonzero(ov_all)
    print(f"\nwave {wnum} contact: {ov_all.sum()} px, {deep} px deep after "
          f"2-px stamp erosion, RGB mean {a[ys, xs].mean(axis=0).round(0)}")
    for key, st in stamps.items():
        n = (st & wmask).sum()
        if n == 0:
            continue
        oys, oxs = np.nonzero(st & wmask)
        mx, my = oxs.mean(), oys.mean()
        r = math.hypot(mx - cx, cy - my) / PXU
        th = math.degrees(math.atan2(cy - my, mx - cx)) % 360
        fam, sign, axis = key
        rel = (th - axis + 180) % 360 - 180
        print(f"  {fam}{'+' if sign > 0 else '-'} axis {axis:5.1f}: {n} px, "
              f"centroid r={r:.1f}u theta={th:.2f} (rel {rel:+.2f})")

# --- model-vs-model min distance ------------------------------------
def to_xy(polar):
    return [(r * math.cos(math.radians(t)), r * math.sin(math.radians(t)))
            for r, t in polar]

def seg_dist(p1, p2, q1, q2):
    def pt_seg(p, a_, b_):
        ax, ay = a_; bx, by = b_; px, py = p
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

axial_xy = to_xy(axial_verts)
flank_p = to_xy(flank_verts)
flank_m = to_xy([(r, -rel) for r, rel in flank_verts])
print(f"\nmin dist axial vs flank+ (same axis): "
      f"{poly_min_dist(axial_xy, flank_p):.2f} u")
print(f"min dist flank+ vs flank- (across the star-tip line): "
      f"{poly_min_dist(flank_p, flank_m):.2f} u")
# next-axis flank- in our axis frame: axis+36, -rel -> absolute 36-rel
flank_next_m = to_xy([(r, 36.0 - rel) for r, rel in flank_verts])
print(f"min dist flank+ vs next-axis flank- (across the dart line): "
      f"{poly_min_dist(flank_p, flank_next_m):.2f} u")

# w21 inner wedge + outer sail on OUR axis (+ members)
w21 = json.loads((SESS / "iterations/62/measure/wave21-fit.json").read_text())
inner_p = to_xy([(v["r"], v["rel"]) for v in w21["inner"]["vertices"]])
inner_m = to_xy([(v["r"], -v["rel"]) for v in w21["inner"]["vertices"]])
outer_p = to_xy([(v["r"], v["rel"]) for v in w21["outer"]["vertices"]])
print(f"min dist axial vs w21 inner wedge (+, same axis): "
      f"{poly_min_dist(axial_xy, inner_p):.2f} u")
print(f"min dist axial vs w21 inner wedge (-, same axis): "
      f"{poly_min_dist(axial_xy, inner_m):.2f} u")
print(f"min dist flank+ vs w21 inner wedge (+): "
      f"{poly_min_dist(flank_p, inner_p):.2f} u")
print(f"min dist flank+ vs w21 outer sail (+): "
      f"{poly_min_dist(flank_p, outer_p):.2f} u")
print(f"min dist axial vs w21 outer sail (+): "
      f"{poly_min_dist(axial_xy, outer_p):.2f} u")

# w18 star on OUR axis (tip r 235 on-axis vs axial apex 246.1)
w18 = json.loads((SESS / "iterations/59/measure/wave18-fit.json").read_text())
p18 = [(v["r"], v["x"]) for v in w18["rows"][1:-1]]
m18 = ([(w18["rows"][0]["r"], 0.0)] + p18 + [(w18["rows"][-1]["r"], 0.0)]
       + [(r, -x) for r, x in reversed(p18)])
star = to_xy(m18)
print(f"min dist axial vs w18 star (same star-tip axis): "
      f"{poly_min_dist(axial_xy, star):.2f} u")
print(f"min dist flank+ vs w18 star: {poly_min_dist(flank_p, star):.2f} u")

# w20 pentagon, dart-18 mirror member (leans toward our axis)
w20 = json.loads((SESS / "iterations/61/measure/wave20-fit.json").read_text())
pv = [(v["r"], v["rel"]) for v in w20["pent"]["vertices"]]
pent18m = to_xy([(r, 18.0 - rel) for r, rel in pv])
print(f"min dist flank+ vs w20 pentagon (dart-18 mirror member): "
      f"{poly_min_dist(flank_p, pent18m):.2f} u")
print(f"min dist axial vs w20 pentagon (dart-18 mirror member): "
      f"{poly_min_dist(axial_xy, pent18m):.2f} u")
