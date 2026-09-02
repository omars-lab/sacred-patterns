#!/usr/bin/env python3
"""Localize the 14-px w18 overlap blob from clearance-wave21.py — which
stamp member (family x sign x axis) and which w18 star region does it
touch? Question being answered: is the contact a band-edge anti-aliasing
halo (px RGB 180-199 EDT-assigned to the w18 seed) or real tile
contact?  Expectation (Tenet 26, pre-stated): centroid near r~235-237 on
ONE star-tip axis at |rel| < 2 deg — the inner family's lowest-r vertex
zone facing the w18 star tip (model gap 5.21u ~ 6.8 px, wide enough
that only halo px between the two tiles can be claimed by both)."""
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

# per-member stamps so the overlap attributes to ONE (family, sign, axis)
members = {}
for k in range(10):
    axis = k * 36.0
    for fam, verts in fams.items():
        for sign in (1, -1):
            m = Image.new("1", (a.shape[1], a.shape[0]), 0)
            d = ImageDraw.Draw(m)
            pts = []
            for r, rel in verts:
                t = math.radians(axis + sign * rel)
                pts.append((cx + r * PXU * math.cos(t), cy - r * PXU * math.sin(t)))
            d.polygon(pts, fill=1)
            members[(fam, sign, axis)] = np.asarray(m, dtype=bool)

w18 = next(w for w in plan["waves"] if w["wave"] == 18)
w18mask = np.isin(labels, [s["id"] for s in w18["shapes"] if not s["fragment"]])

for key, stamp in members.items():
    ov = stamp & w18mask
    n = ov.sum()
    if n == 0:
        continue
    ys, xs = np.nonzero(ov)
    mx, my = xs.mean(), ys.mean()
    r = math.hypot(mx - cx, cy - my) / PXU
    th = math.degrees(math.atan2(cy - my, mx - cx)) % 360
    fam, sign, axis = key
    rel = (th - axis + 180) % 360 - 180
    print(f"{fam}{'+' if sign > 0 else '-'} axis {axis:5.1f}: {n} px, "
          f"centroid r={r:.1f}u theta={th:.2f} (rel {rel:+.2f}), "
          f"px=({mx:.0f},{my:.0f}), RGB mean {a[ys, xs].mean(axis=0).round(0)}")

# which w18 seed shape claims those px, and how far is the contact from
# the actual dark ink of that shape's eroded core?
ov_all = np.zeros_like(w18mask)
for stamp in members.values():
    ov_all |= stamp & w18mask
ids = sorted(set(labels[ov_all].tolist()))
print(f"\nw18 shape ids claiming overlap px: {ids}")
for sid in ids:
    core = seed_labels == sid
    cys, cxs = np.nonzero(core)
    oys, oxs = np.nonzero(ov_all & (labels == sid))
    dmin = min(math.hypot(ox - kx, oy - ky)
               for ox, oy in zip(oxs, oys) for kx, ky in zip(cxs, cys))
    print(f"  shape {sid}: min px-distance from overlap blob to its "
          f"eroded core (real dark ink): {dmin:.1f} px ({dmin / PXU:.2f} u)")
