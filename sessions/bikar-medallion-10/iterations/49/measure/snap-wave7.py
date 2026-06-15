#!/usr/bin/env python3
"""Iter-49 wave-7 grid snap — quantize the fitted vertex models onto bikar
division grids and verify the quantization costs <~0.01 IoU.

Question this answers (Tenet 9): which (M, cpt-index) grid placements
reproduce the fitted wave-7 polygons, so the .bkr cycles snap exactly
(zero quantization error) while staying within the consensus-mask fit?

Grid rule: a vertex at rel offset x from the dart axis (18 deg) needs a
circle divided into M=360/g where BOTH (18+x)/g and (18-x)/g are integers
(the rotated block authors +side and -side cycles from the same circle).

Outputs: wave7-snap.json (chosen snaps, per-group IoU/area, cpt indices)
         wave7-snap-overlay-{outer,inner}.png (consensus vs snapped poly)
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
OUT = SESS / "iterations/49/measure"
PXU = math.sqrt(1091 / 640.7)  # px per pattern unit (wave-6 area calibration)

spec = importlib.util.spec_from_file_location("analyze_reference", TOOLS / "analyze-reference.py")
ar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ar)

plan = json.loads((SESS / "input/reference-analysis/wave-plan/wave-plan.json").read_text())
w7 = next(w for w in plan["waves"] if w["wave"] == 7)
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

real = [s for s in w7["shapes"] if not s["fragment"]]

# --- consensus masks on a 0.25u grid (same procedure as the fit pass) -------
GRID = 0.25
X0, X1, Y0, Y1 = 85.0, 130.0, 15.0, 85.0  # canonical-frame window (units)
NX, NY = int((X1 - X0) / GRID), int((Y1 - Y0) / GRID)

def shape_grid(sid: int, th_axis: float, side: int) -> np.ndarray:
    """Boolean canonical-frame occupancy grid for one shape (4x4 subsampled)."""
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
    if side < 0:
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

groups: dict[str, list[np.ndarray]] = {"outer": [], "inner": []}
for s in real:
    th_axis = (s["theta_deg"] // 36) * 36 + 18.0
    rel = s["theta_deg"] - th_axis
    side = 1 if rel > 0 else -1
    grp = "outer" if s["r_frac"] > 0.40 else "inner"
    groups[grp].append(shape_grid(s["id"], th_axis, side))

TARGET_AREA = 142 / PXU**2  # measured mean area in u^2 (~83.4)
CELL = GRID * GRID

def consensus(stack: list[np.ndarray]) -> np.ndarray:
    acc = np.sum(stack, axis=0).astype(float)
    lo, hi = 0.0, float(acc.max())
    for _ in range(40):  # binary-search threshold to area-match the measured mean
        mid = (lo + hi) / 2
        if (acc >= mid).sum() * CELL > TARGET_AREA:
            lo = mid
        else:
            hi = mid
    return acc >= (lo + hi) / 2

cons = {k: consensus(v) for k, v in groups.items()}

# cell centers in canonical frame
gxc = X0 + (np.arange(NX) + 0.5) * GRID
gyc = Y0 + (np.arange(NY) + 0.5) * GRID
GXC, GYC = np.meshgrid(gxc, gyc)

def poly_mask(verts_rt: list[tuple[float, float]]) -> np.ndarray:
    """Rasterize an (r, theta_abs_deg) polygon onto the cell-center grid."""
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

def iou(mask: np.ndarray, poly: np.ndarray) -> float:
    return float((mask & poly).sum() / (mask | poly).sum())

def shoelace(verts_rt: list[tuple[float, float]]) -> float:
    pts = [(r * math.cos(math.radians(t)), r * math.sin(math.radians(t))) for r, t in verts_rt]
    s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2

fit = json.loads((OUT / "wave7-model-fit.json").read_text())
for grp in ("outer", "inner"):
    verts = [(r, t) for r, t in fit[grp]["verts"]]
    print(f"sanity {grp}: rebuilt-consensus IoU of fitted model = {iou(cons[grp], poly_mask(verts)):.3f} "
          f"(fit pass had {fit[grp]['iou']:.3f}); area {shoelace(verts):.1f}u^2")

# --- snap candidates ---------------------------------------------------------
# rel -> [(snapped_rel, M)]; M from the established grid set where possible.
CAND = {
    2.3:  [(2.25, 160), (2.5, 720)],
    9.4:  [(9.45, 800), (9.5, 720), (9.0, 40)],
    7.2:  [(7.2, 400)],
    6.4:  [(6.3, 400), (6.5, 720)],
    10.9: [(10.8, 400), (11.0, 720)],
    11.6: [(11.7, 400), (11.5, 720)],
    14.2: [(14.4, 100), (14.0, 720)],
    16.3: [(16.2, 200), (16.5, 720)],
}

def snap_group(grp: str) -> dict:
    verts = [(r, t) for r, t in fit[grp]["verts"]]
    rels = [round(t - 18.0, 1) for _, t in verts]
    options = [CAND[rel] for rel in rels]
    best = None
    for combo in itertools.product(*options):
        sv = [(round(r, 1), 18.0 + c[0]) for (r, _), c in zip(verts, combo)]
        score = iou(cons[grp], poly_mask(sv))
        n_grids = len({c[1] for c in combo})
        key = (round(score, 4), -n_grids)  # max IoU, prefer fewer distinct grids
        if best is None or key > best[0]:
            best = (key, combo, sv, score)
    _, combo, sv, score = best
    return {
        "iou_snapped": score,
        "area_snapped": shoelace(sv),
        "verts": [
            {"r": r, "rel": c[0], "M": c[1],
             "cpt_plus": round((18.0 + c[0]) / (360 / c[1])),
             "cpt_minus": round((18.0 - c[0]) / (360 / c[1]))}
            for (r, _), c in zip(verts, combo)
        ],
    }

result = {grp: snap_group(grp) for grp in ("outer", "inner")}
print(json.dumps(result, indent=1))
(OUT / "wave7-snap.json").write_text(json.dumps(result, indent=1))

# overlays: consensus gray, snapped poly outline red
for grp in ("outer", "inner"):
    sv = [(v["r"], 18.0 + v["rel"]) for v in result[grp]["verts"]]
    pm = poly_mask(sv)
    rgb = np.zeros((NY, NX, 3), dtype=np.uint8)
    rgb[cons[grp]] = [150, 150, 150]
    edge = pm & ~ndimage.binary_erosion(pm)
    rgb[edge] = [255, 40, 40]
    Image.fromarray(np.flipud(rgb)).resize((NX * 4, NY * 4), Image.NEAREST).save(
        OUT / f"wave7-snap-overlay-{grp}.png")
print("overlays written")
