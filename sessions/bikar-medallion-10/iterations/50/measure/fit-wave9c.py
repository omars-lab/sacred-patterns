#!/usr/bin/env python3
"""Iter-51 wave-9 symmetric model fit + grid snap.

Question this answers (Tenet 9): which exact (r, +-x) vertex placements
reproduce the wave-9 interstice so ONE rotated 16-point cycle stamps all
10 tiles? Envelope analysis (fit-wave9b) proved the concavities are real
boundary (closing filled <2% area), so the model is the symmetrized
consensus outline itself: 2 on-axis tips + 7 mirrored (r, +-x) pairs,
refined by IoU coordinate descent against the RAW consensus.

Snap rule (star-tip axes, 0 mod 36): x*M/360 integer; on-axis = cpt0.
We snap x to the 0.5-deg grid (M=720, cpt k=2x) and r to 0.1u, then
re-score; exactness asserted at 1e-9.

Outputs: wave9-fit.json, wave9-fit-overlay.png
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

SESS = Path("/Users/omareid/Library/CloudStorage/Dropbox/Data/sacred-patterns/bikar-medallion-10")
TOOLS = Path("/Users/omareid/Workspace/git/sacred-patterns/tools")
OUT = SESS / "iterations/50/measure"
PXU = math.sqrt(1091 / 640.7)

spec = importlib.util.spec_from_file_location("analyze_reference", TOOLS / "analyze-reference.py")
ar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ar)

plan = json.loads((SESS / "input/reference-analysis/wave-plan/wave-plan.json").read_text())
w9 = next(w for w in plan["waves"] if w["wave"] == 9)
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

real = [s for s in w9["shapes"] if not s["fragment"]]

GRID = 0.25
X0, X1, Y0, Y1 = 90.0, 160.0, 5.0, 80.0
NX, NY = int((X1 - X0) / GRID), int((Y1 - Y0) / GRID)

def shape_grid(sid: int, th_axis: float, mirror: bool) -> np.ndarray:
    m = labels == sid
    ys, xs = np.nonzero(m)
    sub = np.linspace(-0.5 + 0.125, 0.5 - 0.125, 4)
    dxx, dyy = np.meshgrid(sub, sub)
    px = (xs[:, None] + dxx.ravel()[None, :] - cx) / PXU
    py = -((ys[:, None] + dyy.ravel()[None, :] - cy)) / PXU
    ang = math.radians(-(th_axis - 18.0))
    ca, sa = math.cos(ang), math.sin(ang)
    rx = px * ca - py * sa
    ry = px * sa + py * ca
    if mirror:
        a18 = math.radians(18.0)
        r = np.hypot(rx, ry)
        t = 2 * a18 - np.arctan2(ry, rx)
        rx, ry = r * np.cos(t), r * np.sin(t)
    g = np.zeros((NY, NX), dtype=bool)
    gx = ((rx - X0) / GRID).astype(int).ravel()
    gy = ((ry - Y0) / GRID).astype(int).ravel()
    ok = (gx >= 0) & (gx < NX) & (gy >= 0) & (gy < NY)
    g[gy[ok], gx[ok]] = True
    return g

stack = []
for s in real:
    th_axis = round(s["theta_deg"] / 36) * 36
    stack.append(shape_grid(s["id"], th_axis, mirror=False))
    stack.append(shape_grid(s["id"], th_axis, mirror=True))

TARGET_AREA = 1485.8 / PXU**2
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

gxc = X0 + (np.arange(NX) + 0.5) * GRID
gyc = Y0 + (np.arange(NY) + 0.5) * GRID
GXC, GYC = np.meshgrid(gxc, gyc)

def poly_mask(vrt):
    pts = [(r * math.cos(math.radians(18.0 + rel)), r * math.sin(math.radians(18.0 + rel)))
           for r, rel in vrt]
    inside = np.zeros((NY, NX), dtype=bool)
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        cond = (GYC > min(y1, y2)) & (GYC <= max(y1, y2))
        with np.errstate(divide="ignore", invalid="ignore"):
            xint = x1 + (GYC - y1) * (x2 - x1) / (y2 - y1) if y2 != y1 else np.full_like(GXC, np.nan)
        inside ^= cond & (GXC < xint)
    return inside

def iou(pm: np.ndarray) -> float:
    return float((cons & pm).sum() / (cons | pm).sum())

# model: [(r, x)] — index 0 and 8 are on-axis (x pinned to 0), 1..7 mirrored
SEED = [(113.4, 0.0), (117.75, 2.5), (116.8, 5.4), (124.3, 6.05),
        (128.3, 8.55), (134.0, 6.9), (139.5, 8.0), (141.7, 7.5), (146.0, 0.0)]

def build(model):
    up = [(r, +x) for r, x in model[1:-1]]
    dn = [(r, -x) for r, x in reversed(model[1:-1])]
    return [(model[0][0], 0.0)] + up + [(model[-1][0], 0.0)] + dn

model = [list(v) for v in SEED]
best = iou(poly_mask(build(model)))
print(f"seed IoU {best:.3f}")
for sweep in range(8):
    improved = False
    for i, j, step in itertools.product(range(9), range(2), (1.0, 0.5, 0.25, 0.1)):
        if j == 1 and (i == 0 or i == 8):
            continue
        for sign in (1, -1):
            trial = [v.copy() for v in model]
            trial[i][j] += sign * step
            v = iou(poly_mask(build(trial)))
            if v > best:
                best, model, improved = v, trial, True
    if not improved:
        break
print(f"fitted IoU {best:.3f}")
for r, x in model:
    print(f"  r {r:7.2f}  x {x:5.2f}")

# snap: r -> 0.1u, x -> 0.5 deg (M=720, cpt k = 2x); axis tips on M=20 cpt0
snapped = [[round(r, 1), round(x * 2) / 2] for r, x in model]
siou = iou(poly_mask(build(snapped)))
print(f"snapped IoU {siou:.3f}")

def shoelace(vrt):
    pts = [(r * math.cos(math.radians(18.0 + rel)), r * math.sin(math.radians(18.0 + rel)))
           for r, rel in vrt]
    s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2

g720 = 360 / 720
rows = []
for i, (r, x) in enumerate(snapped):
    if i in (0, 8):
        rows.append({"r": r, "x": 0.0, "M": 20, "cpt_plus": 0, "cpt_minus": 0})
    else:
        k = round(x / g720)
        assert abs(k * g720 - x) < 1e-9, (i, x)
        rows.append({"r": r, "x": x, "M": 720, "cpt_plus": k, "cpt_minus": (720 - k) % 720})
result = {
    "fitted_iou": best, "snapped_iou": siou,
    "area_u2": shoelace(build(snapped)),
    "consensus_area_u2": float(cons.sum() * CELL),
    "vertices": rows,
}
(OUT / "wave9-fit.json").write_text(json.dumps(result, indent=1))
print(json.dumps(result, indent=1))

pm = poly_mask(build(snapped))
rgb = np.zeros((NY, NX, 3), dtype=np.uint8)
rgb[cons] = [150, 150, 150]
edge = pm & ~ndimage.binary_erosion(pm)
rgb[edge] = [255, 40, 40]
for rr in range(int(100 / 0.25)):
    r_ = 95 + rr * 0.25
    x = r_ * math.cos(math.radians(18)); y = r_ * math.sin(math.radians(18))
    gx, gy = int((x - X0) / GRID), int((y - Y0) / GRID)
    if 0 <= gx < NX and 0 <= gy < NY:
        rgb[gy, gx] = [40, 120, 255]
Image.fromarray(np.flipud(rgb)).resize((NX * 3, NY * 3), Image.NEAREST).save(
    OUT / "wave9-fit-overlay.png")
print("overlay written")
