#!/usr/bin/env python3
"""Iter-54 wave-12 clearance proof — rasterize the 10 snapped bell tiles
(one per dart axis, axis-symmetric) in reference px space; count overlap
px against reference waves 1-11 (must be ~0) and wave-12 (on-target)."""
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

fit = json.loads((SESS / "iterations/53/measure/wave12-fit.json").read_text())
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

for wnum in range(1, 23):
    w = next(w for w in plan["waves"] if w["wave"] == wnum)
    ids = [s["id"] for s in w["shapes"] if not s["fragment"]]
    wmask = np.isin(labels, ids)
    ov = (stamp & wmask).sum()
    tag = "ON-TARGET" if wnum == 12 else ("OK" if ov == 0 else "OVERLAP!")
    print(f"wave {wnum:2d}: overlap {ov} px ({ov / stamp.sum() * 100:.1f}% of stamp) {tag}")
