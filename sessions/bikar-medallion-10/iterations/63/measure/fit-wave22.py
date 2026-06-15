"""Iter-63 wave-22 consensus + model fit + grid snap — HYBRID: one
AXIS-SYMMETRIC family (w18-row machinery) + one free-polygon mirror
family (w20/w21 machinery), triplet wave at the STAR-TIP axes.

Question this answers (Tenet 9): which exact vertices reproduce the 30
navy wave-22 rim tiles (~615 u^2, the OUTERMOST wave) so THREE rotated
cycles stamp all 30 — one axis-symmetric AXIAL tile per star-tip axis
(10 members at rel ~ +-0.3, modeled as symmetric rows: on-axis inner +
(r, +-x) pairs + on-axis outer, the w12/13/18 parametrization) plus a
FLANK mirror pair (20 members at |rel| ~ 6.3-6.9, free polygon via
folded consensus)? The zoom witnesses (ids 1/424 axial, 175 flank) are
medium convex kite/shield silhouettes matching the pre-stated
"medium 4-6-vert convex rim tile" expectation (Tenet 26); thin mask
spurs are grow-back noise the area-matched consensus washes out.

Pipeline per family (consensus and fit share one grid):
  1. consensus — axial: all 10 stacked as-is + mirrored (symmetric);
     flank: rel<0 members mirrored into the + frame (folded);
     area-matched threshold at the family's mean area;
  2. closing probe at 3/4u — small fill = concavities are real boundary;
  3. approxPolyDP eps sweep -> IoU coordinate descent -> DOF-penalized
     pick (IoU - 0.004 * n_verts);
  4. snap probe g=0.5 (M=720) FIRST; escalate to g=0.25 (M=1440) only
     if the g=0.5 loss > 0.01 IoU. Medium tiles (w20 class) but the
     axial family has on-axis + near-axis verts — expect escalation
     per the near-axis-precision driver (w13/w17/w18/w20 family);
     probe both before accepting.

Outputs: wave22-fit.json (axial rows + flank vertices),
         wave22-fit-overlay-{axial,flank}.png
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
OUT = SESS / "iterations/63/measure"
PXU = math.sqrt(1091 / 640.7)

spec = importlib.util.spec_from_file_location("analyze_reference", TOOLS / "analyze-reference.py")
ar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ar)

plan = json.loads((SESS / "input/reference-analysis/wave-plan/wave-plan.json").read_text())
w22 = next(w for w in plan["waves"] if w["wave"] == 22)
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

real = [s for s in w22["shapes"] if not s["fragment"]]

# Window is Cartesian in units: X radial-ish, Y TANGENTIAL u (not deg).
# Measured extents (wave22-vertices.json, canonical frame): axial
# x 242.3-285.7 y -15.1..19.6; flank folded x 234.5-278.6 y 12.3-52.6.
GRID = 0.25
X0, X1, Y0, Y1 = 230.0, 290.0, -18.0, 56.0
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


gxc = X0 + (np.arange(NX) + 0.5) * GRID
gyc = Y0 + (np.arange(NY) + 0.5) * GRID
GXC, GYC = np.meshgrid(gxc, gyc)
CELL = GRID * GRID


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


def shoelace(vrt):
    pts = [(r * math.cos(math.radians(rel)), r * math.sin(math.radians(rel)))
           for r, rel in vrt]
    s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def consensus_of(stack, target):
    acc = np.sum(stack, axis=0).astype(float)
    print(f"max stack: {int(acc.max())}/{len(stack)}; target area {target:.1f} u^2")
    lo, hi = 0.0, float(acc.max())
    for _ in range(40):
        mid = (lo + hi) / 2
        if (acc >= mid).sum() * CELL > target:
            lo = mid
        else:
            hi = mid
    cons = acc >= (lo + hi) / 2
    lab, nlab = ndimage.label(cons, structure=four)
    if nlab > 1:
        sizes = ndimage.sum(cons, lab, range(1, nlab + 1))
        cons = lab == (1 + int(np.argmax(sizes)))
    print(f"consensus area: {cons.sum() * CELL:.1f} u^2")
    for ru in (3, 4):
        rad = int(ru / GRID)
        yy, xx = np.ogrid[-rad:rad + 1, -rad:rad + 1]
        disk = (xx * xx + yy * yy) <= rad * rad
        closed = ndimage.binary_closing(cons, structure=disk)
        print(f"closing probe {ru}u: fill "
              f"{100 * (closed.sum() - cons.sum()) / cons.sum():.1f}%")
    return cons


def save_overlay(cons, pm, name):
    rgb = np.zeros((NY, NX, 3), dtype=np.uint8)
    rgb[cons] = [150, 150, 150]
    edge = pm & ~ndimage.binary_erosion(pm)
    rgb[edge] = [255, 40, 40]
    Image.fromarray(np.flipud(rgb)).resize((NX * 2, NY * 2), Image.NEAREST).save(
        OUT / f"wave22-fit-overlay-{name}.png")


def snap_probe(model, iou_fn, fitted):
    """Probe g=0.5 first, escalate per the 0.01-IoU rule (campaign protocol)."""
    snaps = {}
    for g, M in ((0.5, 720), (0.25, 1440)):
        snapped = [[round(r, 1), round(x / g) * g] for r, x in model]
        snaps[g] = (iou_fn(snapped), snapped, M)
        print(f"g={g} (M={M}): snapped IoU {snaps[g][0]:.3f}")
    if fitted - snaps[0.5][0] <= 0.01:
        g = 0.5
        print("keeping g=0.5 (loss within 0.01)")
    else:
        g = 0.25
        print("g=0.5 loss > 0.01 — keeping g=0.25")
    return g, snaps[g]


# --- AXIAL family: symmetric rows (w18 machinery) ---------------------
def fit_axial(members):
    print(f"\n=== family axial: {len(members)} members (symmetric rows) ===")
    stack = []
    areas = []
    for s in members:
        th_axis = round(s["theta_deg"] / 36) * 36
        stack.append(shape_grid(s["id"], th_axis, mirror=False))
        stack.append(shape_grid(s["id"], th_axis, mirror=True))
        areas.append(s["area_px"] / PXU**2)
    cons = consensus_of(stack, float(np.mean(areas)))

    def iou(snapped_or_model):
        pm = poly_mask(expand(snapped_or_model))
        return float((cons & pm).sum() / (cons | pm).sum())

    def expand(rows):
        plus = [(r, x) for r, x in rows[1:-1]]
        return ([(rows[0][0], 0.0)] + plus + [(rows[-1][0], 0.0)]
                + [(r, -x) for r, x in reversed(plus)])

    def contour_rows(eps):
        cnts, _ = cv2.findContours(cons.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        c = max(cnts, key=cv2.contourArea)
        approx = cv2.approxPolyDP(c, eps, True)[:, 0, :].astype(float)
        pts = []
        for gx, gy in approx:
            x = X0 + (gx + 0.5) * GRID
            y = Y0 + (gy + 0.5) * GRID
            pts.append((math.hypot(x, y), math.degrees(math.atan2(y, x))))
        k0 = min(range(len(pts)), key=lambda i: pts[i][0] + 100 * abs(pts[i][1]) * 0.05)
        pts = pts[k0:] + pts[:k0]
        ka = max(range(len(pts)), key=lambda i: pts[i][0] - 100 * abs(pts[i][1]) * 0.05)
        seg = pts[: ka + 1]
        if sum(1 for r, x in seg if x < -0.5) > len(seg) / 2:
            seg = [(r, -x) for r, x in seg]
        return [[seg[0][0], 0.0]] + [[r, max(x, 0.1)] for r, x in seg[1:-1]] + [[seg[-1][0], 0.0]]

    def descend(rows):
        best = iou(rows)
        rows = [list(v) for v in rows]
        for _ in range(8):
            improved = False
            for i, j, step in itertools.product(range(len(rows)), range(2), (1.0, 0.5, 0.25, 0.1)):
                if j == 1 and (i == 0 or i == len(rows) - 1):
                    continue  # on-axis verts keep x=0
                for sign in (1, -1):
                    trial = [v.copy() for v in rows]
                    trial[i][j] += sign * step
                    if j == 1 and trial[i][1] < 0.1:
                        continue
                    v = iou(trial)
                    if v > best:
                        best, rows, improved = v, trial, True
            if not improved:
                break
        return best, rows

    results = {}
    for eps in (1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0):
        rows = contour_rows(eps)
        n = len(rows)
        if n in results:
            continue
        b, m = descend(rows)
        results[n] = (b, m)
        print(f"eps {eps}: {n}-row symmetric model ({2*n-2} verts) fitted IoU {b:.3f}")

    n_pick = max(results, key=lambda n: results[n][0] - 0.004 * (2 * n - 2))
    best, rows = results[n_pick]
    print(f"picked {n_pick}-row model ({2*n_pick-2} verts), IoU {best:.3f}:")
    for r, x in rows:
        print(f"  r {r:7.2f}  x {x:5.2f}")

    g, (siou, snapped, M) = snap_probe(rows, iou, best)
    out_rows = []
    for r, x in snapped:
        kp = round(x * M / 360 * (360 / M) / (360 / M))  # rel deg -> cpt: x / (360/M)
        kp = round(x / (360 / M)) % M
        km = (M - kp) % M
        out_rows.append({"r": r, "x": x, "M": M, "cpt_plus": kp, "cpt_minus": km})
    save_overlay(cons, poly_mask(expand(snapped)), "axial")
    return {
        "n_rows": n_pick, "n_verts": 2 * n_pick - 2,
        "fitted_iou": best, "snapped_iou": siou, "grid_deg": g,
        "area_u2": shoelace(expand(snapped)),
        "consensus_area_u2": float(cons.sum() * CELL),
        "rows": out_rows,
    }


# --- FLANK family: free polygon, folded consensus (w20/21 machinery) --
def fit_flank(members):
    print(f"\n=== family flank: {len(members)} members (free polygon) ===")
    stack = []
    areas = []
    for s in members:
        th_axis = round(s["theta_deg"] / 36) * 36
        rel = s["theta_deg"] - th_axis
        stack.append(shape_grid(s["id"], th_axis, mirror=(rel < 0)))
        areas.append(s["area_px"] / PXU**2)
    cons = consensus_of(stack, float(np.mean(areas)))

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
        for _ in range(8):
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
    for eps in (1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0):
        seed = contour_seed(eps)
        n = len(seed)
        if n in results:
            continue
        b, m = descend(seed)
        results[n] = (b, m)
        print(f"eps {eps}: {n}-vert fitted IoU {b:.3f}")

    n_pick = max(results, key=lambda n: results[n][0] - 0.004 * n)
    best, model = results[n_pick]
    print(f"picked {n_pick}-vert model, IoU {best:.3f}:")
    for r, x in model:
        print(f"  r {r:7.2f}  rel {x:5.2f}")

    g, (siou, snapped, M) = snap_probe(
        model, lambda s: iou(poly_mask(s)), best)
    rows = []
    for r, x in snapped:
        kp = round(x / g) % M
        km = round(-x / g) % M
        rows.append({"r": r, "rel": x, "M": M, "cpt_plus": kp, "cpt_mirror": km})
    save_overlay(cons, poly_mask(snapped), "flank")
    return {
        "n_verts": n_pick, "fitted_iou": best, "snapped_iou": siou,
        "grid_deg": g,
        "area_u2": shoelace(snapped), "consensus_area_u2": float(cons.sum() * CELL),
        "vertices": rows,
    }


def fam_of(s):
    th_axis = round(s["theta_deg"] / 36) * 36
    return "axial" if abs(s["theta_deg"] - th_axis) < 3.0 else "flank"


result = {
    "axial": fit_axial([s for s in real if fam_of(s) == "axial"]),
    "flank": fit_flank([s for s in real if fam_of(s) == "flank"]),
}
(OUT / "wave22-fit.json").write_text(json.dumps(result, indent=1))
print("\nwave22-fit.json written")
