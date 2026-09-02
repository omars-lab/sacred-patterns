#!/usr/bin/env python3
"""Iter-51 wave-9 ENVELOPE fit — the raw consensus contour (43 verts,
fit-wave9.py) is scalloped by white band crossings, exactly like wave 8's
5-9-vert contours hid a 4-vert diamond. The underlying tile is the
envelope: morphologically CLOSE the consensus at band scale to fill the
band-carved notches, then extract + simplify that outline.

Question this answers (Tenet 9): what low-DOF symmetric polygon is the
wave-9 interstice tile BEFORE the strapwork carves it? The render gets
carved by our own bands, so the model must be the un-carved tile.

Snap rule for star-tip axes (0 mod 36): vertex at rel +-x needs only
x*M/360 integer (cpt at +-x around 0 deg); on-axis vertices are cpt0.

Outputs: wave9-envelope.json (closed-mask polygon, paired (r, rel) verts,
         snapped grid placements), wave9-envelope-overlay.png
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
    th_axis = round(s["theta_deg"] / 36) * 36  # star-tip axis -> canonical 18
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
print(f"consensus: {cons.sum() * CELL:.1f} u^2")

# --- envelope: close at band scale (strapwork width 8u), sweep radii ---------
def disk(rad_cells: int) -> np.ndarray:
    yy, xx = np.ogrid[-rad_cells:rad_cells + 1, -rad_cells:rad_cells + 1]
    return (xx * xx + yy * yy) <= rad_cells * rad_cells

for rad_u in (3.0, 4.0, 5.0):
    rad = int(rad_u / GRID)
    closed = ndimage.binary_closing(cons, structure=disk(rad))
    cnts, _ = cv2.findContours(closed.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=cv2.contourArea)
    for eps in (3.0, 4.0, 5.0):
        approx = cv2.approxPolyDP(c, eps, True)
        print(f"close r={rad_u}u eps={eps}: {len(approx)} verts, area {closed.sum() * CELL:.1f} u^2")

RAD_U = 4.0
closed = ndimage.binary_closing(cons, structure=disk(int(RAD_U / GRID)))
cnts, _ = cv2.findContours(closed.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
c = max(cnts, key=cv2.contourArea)
EPS = 4.0
approx = cv2.approxPolyDP(c, EPS, True)[:, 0, :].astype(float)

verts = []
for gx, gy in approx:
    x = X0 + (gx + 0.5) * GRID
    y = Y0 + (gy + 0.5) * GRID
    r = math.hypot(x, y)
    rel = math.degrees(math.atan2(y, x)) - 18.0
    verts.append((r, rel))
print(f"\nenvelope polygon ({len(verts)} verts):")
for r, rel in verts:
    print(f"  r {r:7.2f}  rel {rel:7.2f}")

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

pm = poly_mask(verts)
iou_closed = float((closed & pm).sum() / (closed | pm).sum())
cover_cons = float((cons & pm).sum() / cons.sum())
print(f"polygon vs closed-mask IoU {iou_closed:.3f}; covers {cover_cons:.3f} of raw consensus")

(OUT / "wave9-envelope.json").write_text(json.dumps({
    "closing_radius_u": RAD_U, "eps_px": EPS,
    "iou_vs_closed": iou_closed, "consensus_cover": cover_cons,
    "verts": [{"r": round(r, 2), "rel": round(rel, 2)} for r, rel in verts]}, indent=1))

rgb = np.zeros((NY, NX, 3), dtype=np.uint8)
rgb[closed] = [70, 70, 70]
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
    OUT / "wave9-envelope-overlay.png")
print("overlay written")
