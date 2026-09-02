"""Iter-57 wave-15 consensus + model fit + grid snap — AXIS-SYMMETRIC
PENTAGRAM on the dart axes.

Question this answers (Tenet 9): which exact (r, x) rows reproduce the
wave-15 deep_navy five-pointed STAR tile (~181 u^2, r 171-198, apex
pointing radially outward) so ONE rotated cycle per DART axis (18 mod
36) stamps all 10? Both zoom witnesses (ids 30/58) show a clean
pentagram — wave-4's shape class recurring at the outer ring — so the
model is the symmetric-rows parametrization with a NON-CONVEX walk:
on-axis inner valley + 4 ordered +side rows (point/valley/point/valley)
+ on-axis apex; expand() mirrors the pairs (poly_mask's even-odd ray
casting handles the star's concavity, contour_rows' start/apex picks
are r-based and axis-near, both star-safe).

Pipeline identical to fit-wave15.py (symmetrized consensus, closing
probe, eps sweep -> rows -> descent -> DOF pick, g=0.5-first snap with
0.01 escalation — SMALL tile, w11-scale, escalation likely).

Dart cpt rule (axis = 18 deg): + vertex at rel x -> cpt((18+x)/g mod
M); mirror cpt((18-x)/g mod M). On-axis verts (x=0) -> M=20 cpt1
(exact 18 deg), wave-12 precedent.

Outputs: wave15-fit.json, wave15-fit-overlay.png
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
OUT = SESS / "iterations/56/measure"
PXU = math.sqrt(1091 / 640.7)

spec = importlib.util.spec_from_file_location("analyze_reference", TOOLS / "analyze-reference.py")
ar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ar)

plan = json.loads((SESS / "input/reference-analysis/wave-plan/wave-plan.json").read_text())
w15 = next(w for w in plan["waves"] if w["wave"] == 15)
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

real = [s for s in w15["shapes"] if not s["fragment"]]

GRID = 0.25
X0, X1, Y0, Y1 = 163.0, 203.0, -16.0, 16.0
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
    th_axis = (s["theta_deg"] // 36) * 36 + 18  # dart axes (18 mod 36)
    stack.append(shape_grid(s["id"], th_axis, mirror=False))
    stack.append(shape_grid(s["id"], th_axis, mirror=True))

TARGET_AREA = 181.2
CELL = GRID * GRID
acc = np.sum(stack, axis=0).astype(float)
print(f"max stack: {int(acc.max())}/{len(stack)}")
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
print(f"consensus area: {cons.sum() * CELL:.1f} u^2 (target {TARGET_AREA})")

# closing probe: does morphological closing at band scale fill much?
for ru in (3, 4):
    rad = int(ru / GRID)
    yy, xx = np.ogrid[-rad:rad + 1, -rad:rad + 1]
    disk = (xx * xx + yy * yy) <= rad * rad
    closed = ndimage.binary_closing(cons, structure=disk)
    print(f"closing probe {ru}u: {closed.sum() * CELL:.1f} u^2 "
          f"(fill {100 * (closed.sum() - cons.sum()) / cons.sum():.1f}%)")

gxc = X0 + (np.arange(NX) + 0.5) * GRID
gyc = Y0 + (np.arange(NY) + 0.5) * GRID
GXC, GYC = np.meshgrid(gxc, gyc)

def expand(rows):
    """Symmetric rows -> full polygon. rows[0]/rows[-1] are on-axis
    (x forced 0); middle rows are (r, +x) pairs walked base->apex."""
    plus = [(r, x) for r, x in rows[1:-1]]
    return ([(rows[0][0], 0.0)] + plus + [(rows[-1][0], 0.0)]
            + [(r, -x) for r, x in reversed(plus)])

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

def contour_rows(eps):
    """+side walk from inner on-axis crossing to outer, contour order."""
    cnts, _ = cv2.findContours(cons.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=cv2.contourArea)
    approx = cv2.approxPolyDP(c, eps, True)[:, 0, :].astype(float)
    pts = []
    for gx, gy in approx:
        x = X0 + (gx + 0.5) * GRID
        y = Y0 + (gy + 0.5) * GRID
        pts.append((math.hypot(x, y), math.degrees(math.atan2(y, x))))
    # rotate the closed walk so it starts at the innermost near-axis vert
    k0 = min(range(len(pts)), key=lambda i: pts[i][0] + 100 * abs(pts[i][1]) * 0.05)
    pts = pts[k0:] + pts[:k0]
    # apex = outermost near-axis vert; take the side walked first
    ka = max(range(len(pts)), key=lambda i: pts[i][0] - 100 * abs(pts[i][1]) * 0.05)
    seg = pts[: ka + 1]
    if sum(1 for r, x in seg if x < -0.5) > len(seg) / 2:  # walked the -side; mirror it
        seg = [(r, -x) for r, x in seg]
    rows = [[seg[0][0], 0.0]] + [[r, max(x, 0.1)] for r, x in seg[1:-1]] + [[seg[-1][0], 0.0]]
    return rows

def descend(rows):
    best = iou(poly_mask(expand(rows)))
    rows = [list(v) for v in rows]
    for sweep in range(8):
        improved = False
        for i, j, step in itertools.product(range(len(rows)), range(2), (1.0, 0.5, 0.25, 0.1)):
            if j == 1 and (i == 0 or i == len(rows) - 1):
                continue  # on-axis verts keep x=0
            for sign in (1, -1):
                trial = [v.copy() for v in rows]
                trial[i][j] += sign * step
                if j == 1 and trial[i][1] < 0.1:
                    continue
                v = iou(poly_mask(expand(trial)))
                if v > best:
                    best, rows, improved = v, trial, True
        if not improved:
            break
    return best, rows

results = {}
for eps in (1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0):
    rows = contour_rows(eps)
    n = len(rows)
    if n in results:
        continue
    b, m = descend(rows)
    results[n] = (b, m)
    print(f"eps {eps}: {n}-row symmetric model ({2*n-2} verts) fitted IoU {b:.3f}")

# Geometric 6-row seed: the eye + wave-4 precedent say PENTAGRAM, but
# approxPolyDP's 6-row seed descends to a poor local optimum (0.916 vs
# the noisy 8-row 0.939 with a split point-vertex). Seed the 10-vert
# star from ideal pentagram geometry (star center r~184, outer ~12.5u,
# inner ~0.382 outer) refined against the measured extremes (bottom
# points r~172.5, apex ~196) and let descent refine; keep whichever
# 6-row is better.
geo = [[179.2, 0.0],   # on-axis inner valley (star bottom)
       [172.5, 2.4],   # bottom point pair
       [182.6, 1.4],   # lower valley pair
       [188.2, 3.6],   # side point pair
       [187.9, 0.9],   # upper valley pair
       [196.0, 0.0]]   # on-axis apex (outward point)
bg, mg = descend(geo)
print(f"geo seed: 6-row symmetric model (10 verts) fitted IoU {bg:.3f}")
if 6 not in results or bg > results[6][0]:
    results[6] = (bg, mg)

n_pick = max(results, key=lambda n: results[n][0] - 0.004 * (2 * n - 2))
best, rows = results[n_pick]
print(f"\npicked {n_pick}-row model ({2*n_pick-2} verts), IoU {best:.3f}:")
for r, x in rows:
    print(f"  r {r:7.2f}  x {x:5.2f}")

for g, M in ((0.5, 720), (0.25, 1440)):
    snapped = [[round(r, 1), round(x / g) * g] for r, x in rows]
    siou = iou(poly_mask(expand(snapped)))
    print(f"g={g} (M={M}): snapped IoU {siou:.3f}")
    if g == 0.5:
        siou05, snapped05 = siou, snapped
if best - siou05 <= 0.01:
    g, M, siou, snapped = 0.5, 720, siou05, snapped05
    print("keeping g=0.5 (loss within 0.01)")
else:
    g, M = 0.25, 1440
    snapped = [[round(r, 1), round(x / g) * g] for r, x in rows]
    siou = iou(poly_mask(expand(snapped)))
    print("g=0.5 loss > 0.01 — keeping g=0.25")

def shoelace(vrt):
    pts = [(r * math.cos(math.radians(rel)), r * math.sin(math.radians(rel)))
           for r, rel in vrt]
    s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2

# cpt on the DART axis: axis angle 18 deg; + vertex at rel x sits at
# absolute 18+x, mirror at 18-x (wave-12 precedent: C57.cpt41/cpt31).
# On-axis (x=0) rows get M=20 cpt1 (exact 18 deg) in the .bkr.
out_rows = []
for r, x in snapped:
    kp = round((18 + x) * M / 360) % M
    km = round((18 - x) * M / 360) % M
    assert abs(kp * 360 / M - (18 + x)) < 1e-9, x
    assert abs(km * 360 / M - (18 - x)) < 1e-9, x
    out_rows.append({"r": r, "x": x, "M": M, "cpt_plus": kp, "cpt_minus": km})
result = {
    "n_rows": n_pick, "n_verts": 2 * n_pick - 2,
    "fitted_iou": best, "snapped_iou": siou, "grid_deg": g,
    "area_u2": shoelace(expand(snapped)),
    "consensus_area_u2": float(cons.sum() * CELL),
    "rows": out_rows,
}
(OUT / "wave15-fit.json").write_text(json.dumps(result, indent=1))
print(json.dumps(result, indent=1))

pm = poly_mask(expand(snapped))
rgb = np.zeros((NY, NX, 3), dtype=np.uint8)
rgb[cons] = [150, 150, 150]
edge = pm & ~ndimage.binary_erosion(pm)
rgb[edge] = [255, 40, 40]
Image.fromarray(np.flipud(rgb)).resize((NX * 3, NY * 3), Image.NEAREST).save(
    OUT / "wave15-fit-overlay.png")
print("overlay written")
