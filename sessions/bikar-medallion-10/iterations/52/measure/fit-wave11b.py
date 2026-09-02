#!/usr/bin/env python3
"""Iter-53 wave-11 model fit + grid snap — free (asymmetric) polygon.

Question this answers (Tenet 9): which exact (r, rel) vertices reproduce
the wave-11 4-pronged spiky tile at star-tip-axis rel ~ +8 so TWO rotated
cycles (one + its mirror, wave-7/10 style) stamp all 20 tiles? The tile
is a pair member, NOT self-symmetric, so the fit is unconstrained; the
mirror partner reuses the same circles with mirrored cpt indices.

Seeds come from approxPolyDP simplifications of the consensus contour at
several eps values (the tile is too spiky to hand-seed reliably); each
seed is refined by IoU coordinate descent and the winner is picked with
the DOF penalty IoU - 0.004*n_verts (wave-10 precedent).

Snap rule (star-tip axes, 0 mod 36, M=1440 g=0.25): vertex at rel x ->
cpt(4x mod 1440); mirror partner -> cpt(-4x mod 1440). Both exact when
x is a multiple of 0.25; asserted 1e-9. M=1440 (not the usual 720)
because the g=0.5 snap cost 0.045 IoU on this small spiky tile
(0.928 -> 0.883) while g=0.25 keeps 0.921 — probed before accepting.

Outputs: wave11-fit.json, wave11-fit-overlay.png
"""
from __future__ import annotations

import importlib.util
import itertools
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
    stack.append(shape_grid(s["id"], th_axis, mirror=(rel < 0)))

TARGET_AREA = 229.7 / PXU**2
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
    pts = [(r * math.cos(math.radians(rel)), r * math.sin(math.radians(rel)))
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

def iou(pm):
    return float((cons & pm).sum() / (cons | pm).sum())

def contour_seed(eps):
    cnts, _ = cv2.findContours(cons.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=cv2.contourArea)
    approx = cv2.approxPolyDP(c, eps, True)[:, 0, :].astype(float)
    seed = []
    for gx, gy in approx:
        x = X0 + (gx + 0.5) * GRID
        y = Y0 + (gy + 0.5) * GRID
        seed.append([math.hypot(x, y), math.degrees(math.atan2(y, x))])
    return seed

def descend(model):
    best = iou(poly_mask(model))
    model = [list(v) for v in model]
    for sweep in range(8):
        improved = False
        for i, j, step in itertools.product(range(len(model)), range(2), (1.0, 0.5, 0.25, 0.1)):
            for sign in (1, -1):
                trial = [v.copy() for v in model]
                trial[i][j] += sign * step
                v = iou(poly_mask(trial))
                if v > best:
                    best, model, improved = v, trial, True
        if not improved:
            break
    return best, model

results = {}
for eps in (2.5, 3.0, 3.5, 4.0, 5.0):
    seed = contour_seed(eps)
    n = len(seed)
    if n in results:
        continue
    b, m = descend(seed)
    results[n] = (b, m)
    print(f"eps {eps}: {n}-vert fitted IoU {b:.3f}")

n_pick = max(results, key=lambda n: results[n][0] - 0.004 * n)  # mild DOF penalty
best, model = results[n_pick]
print(f"\npicked {n_pick}-vert model, IoU {best:.3f}:")
for r, x in model:
    print(f"  r {r:7.2f}  rel {x:5.2f}")

snapped = [[round(r, 1), round(x * 4) / 4] for r, x in model]
siou = iou(poly_mask(snapped))
print(f"snapped IoU {siou:.3f}")

def shoelace(vrt):
    pts = [(r * math.cos(math.radians(rel)), r * math.sin(math.radians(rel)))
           for r, rel in vrt]
    s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2

g = 0.25
rows = []
for r, x in snapped:
    kp = round(x / g) % 1440
    km = round(-x / g) % 1440
    assert abs((kp * g) % 360 - x % 360) < 1e-9 and abs((km * g) % 360 - (-x) % 360) < 1e-9, x
    rows.append({"r": r, "rel": x, "M": 1440, "cpt_plus": kp, "cpt_mirror": km})
result = {
    "n_verts": n_pick, "fitted_iou": best, "snapped_iou": siou,
    "area_u2": shoelace(snapped), "consensus_area_u2": float(cons.sum() * CELL),
    "vertices": rows,
}
(OUT / "wave11-fit.json").write_text(json.dumps(result, indent=1))
print(json.dumps(result, indent=1))

pm = poly_mask(snapped)
rgb = np.zeros((NY, NX, 3), dtype=np.uint8)
rgb[cons] = [150, 150, 150]
edge = pm & ~ndimage.binary_erosion(pm)
rgb[edge] = [255, 40, 40]
Image.fromarray(np.flipud(rgb)).resize((NX * 4, NY * 4), Image.NEAREST).save(
    OUT / "wave11-fit-overlay.png")
print("overlay written")
