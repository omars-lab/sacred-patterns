#!/usr/bin/env python3
"""Iter-51 wave-9 clearance proof — rasterize the 10 snapped 16-gons in
reference px space and count overlap px against reference waves 1-8
(must be ~0: standalone-cycle requirement) and the wave-9 mask
(on-target fraction). Same data-proof pattern as wave 8 (iter-50).
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

fit = json.loads((SESS / "iterations/50/measure/wave9-fit.json").read_text())
vm = fit["vertices"]
half = [(v["r"], v["x"]) for v in vm]
model = ([(half[0][0], 0.0)] + [(r, +x) for r, x in half[1:-1]]
         + [(half[-1][0], 0.0)] + [(r, -x) for r, x in reversed(half[1:-1])])

mask = Image.new("1", (a.shape[1], a.shape[0]), 0)
d = ImageDraw.Draw(mask)
for k in range(10):
    th0 = k * 36.0  # star-tip axes at 0 mod 36
    pts = []
    for r, rel in model:
        t = math.radians(th0 + rel)
        x = cx + r * PXU * math.cos(t)
        y = cy - r * PXU * math.sin(t)
        pts.append((x, y))
    d.polygon(pts, fill=1)
stamp = np.asarray(mask, dtype=bool)
print(f"stamped px: {stamp.sum()}")

for wnum in range(1, 10):
    w = next(w for w in plan["waves"] if w["wave"] == wnum)
    ids = [s["id"] for s in w["shapes"] if not s["fragment"]]
    wmask = np.isin(labels, ids)
    ov = (stamp & wmask).sum()
    tag = "ON-TARGET" if wnum == 9 else ("OK" if ov == 0 else "OVERLAP!")
    print(f"wave {wnum}: overlap {ov} px ({ov / stamp.sum() * 100:.1f}% of stamp) {tag}")
