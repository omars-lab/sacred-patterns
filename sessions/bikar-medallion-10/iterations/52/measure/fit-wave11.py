#!/usr/bin/env python3
"""Iter-53 wave-11 consensus + closing probe + contour read.

Question this answers (Tenet 9): what polygon at STAR-TIP-axis rel ~ +8
deg reproduces the wave-11 deep-navy 4-pronged spiky tile (20 witnesses
in mirror pairs at +-7.9 deg, ~135u^2, r ~ 142-164)? All witnesses fold
to the + side (rel < 0 shapes mirror about the 0-deg star-tip axis), so
the consensus models ONE pair member; the .bkr stamps it plus its
mirror, wave-7/10 style. The zooms (ids 59/60) show a 4-spike star —
the concavities are obviously real boundary, but the closing probe
quantifies it anyway for the record.

Outputs: wave11-consensus-overlay.png, wave11-contour.json
"""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage

SESS = Path("/Users/omareid/Library/CloudStorage/Dropbox/Data/sacred-patterns/bikar-medallion-10")
TOOLS = Path("/Users/omareid/Workspace/git/sacred-patterns/tools")
OUT = SESS / "iterations/52/measure"
PXU = math.sqrt(1091 / 640.7)

spec = importlib.util.spec_from_file_location("analyze_reference", TOOLS / "analyze-reference.py")
ar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ar)

plan = json.loads((SESS / "input/reference-analysis/wave-plan/wave-plan.json").read_text())
w11 = next(w for w in plan["waves"] if w["wave"] == 11)
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

real = [s for s in w11["shapes"] if not s["fragment"]]

GRID = 0.25
X0, X1, Y0, Y1 = 130.0, 170.0, -5.0, 45.0
NX, NY = int((X1 - X0) / GRID), int((Y1 - Y0) / GRID)

def shape_grid(sid: int, th_axis: float, mirror: bool) -> np.ndarray:
    m = labels == sid
    ys, xs = np.nonzero(m)
    sub = np.linspace(-0.5 + 0.125, 0.5 - 0.125, 4)
    dxx, dyy = np.meshgrid(sub, sub)
    px = (xs[:, None] + dxx.ravel()[None, :] - cx) / PXU
    py = -((ys[:, None] + dyy.ravel()[None, :] - cy)) / PXU
    ang = math.radians(-th_axis)
    ca, sa = math.cos(ang), math.sin(ang)
    rx = px * ca - py * sa
    ry = px * sa + py * ca
    if mirror:
        ry = -ry
    g = np.zeros((NY, NX), dtype=bool)
    gx = ((rx - X0) / GRID).astype(int).ravel()
    gy = ((ry - Y0) / GRID).astype(int).ravel()
    ok = (gx >= 0) & (gx < NX) & (gy >= 0) & (gy < NY)
    g[gy[ok], gx[ok]] = True
    return g

stack = []
for s in real:
    th_axis = round(s["theta_deg"] / 36) * 36
    rel = s["theta_deg"] - th_axis
    # fold: rel<0 witnesses mirror to the + side (about the 0-deg axis)
    stack.append(shape_grid(s["id"], th_axis, mirror=(rel < 0)))
print(f"{len(stack)} folded witnesses")

TARGET_AREA = 229.7 / PXU**2  # ~134.9 u^2
CELL = GRID * GRID
acc = np.sum(stack, axis=0).astype(float)
lo, hi = 0.0, float(acc.max())
for _ in range(40):
    mid = (lo + hi) / 2
    if (acc >= mid).sum() * CELL > TARGET_AREA:
        lo = mid
    else:
        hi = mid
cons = acc >= (lo + hi) / 2
lab, nlab = ndimage.label(cons, structure=four)
if nlab > 1:
    sizes = ndimage.sum(cons, lab, range(1, nlab + 1))
    cons = lab == (1 + int(np.argmax(sizes)))
print(f"consensus: {cons.sum() * CELL:.1f} u^2 (target {TARGET_AREA:.1f}), max stack {int(acc.max())}/20")

def disk(rad_cells: int) -> np.ndarray:
    yy, xx = np.ogrid[-rad_cells:rad_cells + 1, -rad_cells:rad_cells + 1]
    return (xx * xx + yy * yy) <= rad_cells * rad_cells

def contour_verts(mask, eps):
    cnts, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=cv2.contourArea)
    return cv2.approxPolyDP(c, eps, True)[:, 0, :].astype(float)

for rad_u in (0.0, 3.0, 4.0):
    m = cons if rad_u == 0 else ndimage.binary_closing(cons, structure=disk(int(rad_u / GRID)))
    for eps in (2.0, 3.0):
        v = contour_verts(m, eps)
        print(f"close {rad_u}u eps {eps}: {len(v)} verts, area {m.sum() * CELL:.1f} u^2")

approx = contour_verts(cons, 2.0)
verts = []
for gx, gy in approx:
    x = X0 + (gx + 0.5) * GRID
    y = Y0 + (gy + 0.5) * GRID
    verts.append((math.hypot(x, y), math.degrees(math.atan2(y, x))))
print("\nraw consensus contour (eps 2.0), rel = angle from star-tip axis:")
for r, rel in verts:
    print(f"  r {r:7.2f}  rel {rel:7.2f}")
(OUT / "wave11-contour.json").write_text(json.dumps(
    {"verts": [{"r": round(r, 2), "rel": round(rel, 2)} for r, rel in verts]}, indent=1))

rgb = np.zeros((NY, NX, 3), dtype=np.uint8)
closed = ndimage.binary_closing(cons, structure=disk(int(4.0 / GRID)))
rgb[closed] = [70, 70, 70]
rgb[cons] = [150, 150, 150]
for rr in range(int(120 / 0.25)):
    r_ = 130 + rr * 0.25
    x, y = r_, 0.0  # the star-tip axis is the +x axis in this frame
    gx, gy = int((x - X0) / GRID), int((y - Y0) / GRID)
    if 0 <= gx < NX and 0 <= gy < NY:
        rgb[gy, gx] = [40, 120, 255]
Image.fromarray(np.flipud(rgb)).resize((NX * 4, NY * 4), Image.NEAREST).save(
    OUT / "wave11-consensus-overlay.png")
print("overlay written")
