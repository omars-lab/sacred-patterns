#!/usr/bin/env python3
"""Iter-50 wave-8 model fit + grid snap — consensus-mask the 10 on-axis
diamonds, fit a 4-vertex axis-symmetric model, snap to bikar grids.

Question this answers (Tenet 9): which (r, M, cpt) placements reproduce the
wave-8 diamond so one rotated 4-point cycle stamps all 10 tiles exactly?

Model: diamond symmetric about the dart axis (18 deg) — vertices
inner (r_in, 18), side+ (r_side, 18+w), outer (r_out, 18), side- (r_side,
18-w). 4 DOF: r_in, r_out, r_side, w. Each of the 10 shapes contributes
its rotated mask AND its 18-deg mirror (20 effective witnesses), which
forces the consensus itself to be axis-symmetric.

Outputs: wave8-fit.json (fitted + snapped model, IoU, areas, cpt indices)
         wave8-fit-overlay.png (consensus gray, snapped poly outline red)
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
w8 = next(w for w in plan["waves"] if w["wave"] == 8)
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

real = [s for s in w8["shapes"] if not s["fragment"]]

GRID = 0.25
X0, X1, Y0, Y1 = 100.0, 145.0, 15.0, 65.0
NX, NY = int((X1 - X0) / GRID), int((Y1 - Y0) / GRID)

def shape_grid(sid: int, th_axis: float, mirror: bool) -> np.ndarray:
    """Canonical-frame occupancy grid for one shape (4x4 subsampled)."""
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
    th_axis = (s["theta_deg"] // 36) * 36 + 18.0
    stack.append(shape_grid(s["id"], th_axis, mirror=False))
    stack.append(shape_grid(s["id"], th_axis, mirror=True))

TARGET_AREA = 316.5 / PXU**2  # measured mean area (~185.9 u^2)
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
print(f"consensus: {cons.sum() * CELL:.1f} u^2 (target {TARGET_AREA:.1f}), max stack {int(acc.max())}/20")

gxc = X0 + (np.arange(NX) + 0.5) * GRID
gyc = Y0 + (np.arange(NY) + 0.5) * GRID
GXC, GYC = np.meshgrid(gxc, gyc)

def poly_mask(verts_rt: list[tuple[float, float]]) -> np.ndarray:
    pts = [(r * math.cos(math.radians(t)), r * math.sin(math.radians(t))) for r, t in verts_rt]
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

def iou(poly: np.ndarray) -> float:
    return float((cons & poly).sum() / (cons | poly).sum())

def diamond(r_in: float, r_out: float, r_side: float, w: float):
    return [(r_in, 18.0), (r_side, 18.0 + w), (r_out, 18.0), (r_side, 18.0 - w)]

def shoelace(verts_rt) -> float:
    pts = [(r * math.cos(math.radians(t)), r * math.sin(math.radians(t))) for r, t in verts_rt]
    s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2

# coordinate descent from mask-derived seeds
params = [116.5, 135.5, 126.0, 4.0]  # r_in, r_out, r_side, w
best = iou(poly_mask(diamond(*params)))
for sweep in range(6):
    improved = False
    for i, step in itertools.product(range(4), (1.0, 0.5, 0.25, 0.1, 0.05)):
        for sign in (1, -1):
            trial = params.copy()
            trial[i] += sign * step
            v = iou(poly_mask(diamond(*trial)))
            if v > best:
                best, params, improved = v, trial, True
    if not improved:
        break
fit_verts = diamond(*params)
print(f"fitted: r_in {params[0]:.2f} r_out {params[1]:.2f} r_side {params[2]:.2f} w {params[3]:.2f} "
      f"-> IoU {best:.3f}, area {shoelace(fit_verts):.1f} u^2")

# --- grid snap ---------------------------------------------------------------
# On-axis vertices (rel 0) need any M with 18/(360/M) integer: M=20 -> cpt1.
# Side vertices at rel +-w need M with (18+-w)/(360/M) both integer (wave-7 rule).
W_CAND = [(round(w, 3), M) for w, M in
          [(3.6, 100), (3.6, 200), (4.5, 80), (4.05, 800), (3.825, 1600),
           (4.2, 600), (3.9, 1200), (4.0, 90), (3.75, 240), (4.1, 3600),
           (3.95, 7200), (4.15, 7200), (4.05, 400),
           (4.75, 1440), (4.8, 300), (4.95, 800), (4.875, 960),
           (4.6, 1800), (4.65, 2400), (4.7, 3600), (5.0, 1800)]
          if abs(w - params[3]) <= 0.5]

def snap_r(x: float) -> float:
    return round(x, 1)

snapped_best = None
for w, M in W_CAND:
    g = 360 / M
    if abs((18 + w) / g - round((18 + w) / g)) > 1e-9: continue
    if abs((18 - w) / g - round((18 - w) / g)) > 1e-9: continue
    sv = diamond(snap_r(params[0]), snap_r(params[1]), snap_r(params[2]), w)
    v = iou(poly_mask(sv))
    if snapped_best is None or v > snapped_best[0]:
        snapped_best = (v, w, M, sv)
v, w, M, sv = snapped_best
print(f"snapped: w {w} on M={M} -> IoU {v:.3f}, area {shoelace(sv):.1f} u^2")

g = 360 / M
result = {
    "fitted": {"r_in": params[0], "r_out": params[1], "r_side": params[2], "w": params[3],
               "iou": best, "area_u2": shoelace(fit_verts)},
    "snapped": {
        "iou": v, "area_u2": shoelace(sv),
        "r_in": snap_r(params[0]), "r_out": snap_r(params[1]), "r_side": snap_r(params[2]),
        "w": w, "M_side": M,
        "cpt_side_plus": round((18 + w) / g), "cpt_side_minus": round((18 - w) / g),
        "M_axis": 20, "cpt_axis": 1,
    },
}
assert abs(result["snapped"]["cpt_side_plus"] * g - (18 + w)) < 1e-9
assert abs(result["snapped"]["cpt_side_minus"] * g - (18 - w)) < 1e-9
assert abs(result["snapped"]["cpt_axis"] * (360 / 20) - 18) < 1e-9
(OUT / "wave8-fit.json").write_text(json.dumps(result, indent=1))
print(json.dumps(result, indent=1))

pm = poly_mask(sv)
rgb = np.zeros((NY, NX, 3), dtype=np.uint8)
rgb[cons] = [150, 150, 150]
edge = pm & ~ndimage.binary_erosion(pm)
rgb[edge] = [255, 40, 40]
Image.fromarray(np.flipud(rgb)).resize((NX * 4, NY * 4), Image.NEAREST).save(
    OUT / "wave8-fit-overlay.png")
print("overlay written")
