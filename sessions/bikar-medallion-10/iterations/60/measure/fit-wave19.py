#!/usr/bin/env python3
"""Iter-60 wave-19 consensus + model fit + grid snap — ONE free
(asymmetric) polygon family, mirror-pair wave (wave-16 topology at the
STAR-TIP axes, outer edge).

Question this answers (Tenet 9): which exact (r, rel) vertices reproduce
the wave-19 small deep_navy KITE tiles so TWO rotated cycles (one +
member, one mirror, wave-16 style) stamp all 20 tiles? Plan thetas
cluster at rel ~ +-7.6 about the STAR-TIP axes; the zoom witnesses
(ids 102/111) are small elongated kites (~84 u^2) pointing outward —
hairline strands in the masks are segmentation grow-back noise the
area-matched consensus threshold washes out. Fitted as a free polygon
via folded consensus (rel<0 members mirrored into the + frame).

Pipeline (consensus and fit share one grid):
  1. folded consensus, area-matched threshold at the family's mean area;
  2. closing probe at 3/4u — small fill = concavities are real boundary;
  3. approxPolyDP eps sweep -> IoU coordinate descent -> DOF-penalized
     pick (IoU - 0.004 * n_verts);
  4. snap probe g=0.5 (M=720) FIRST; escalate to g=0.25 (M=1440) only
     if the g=0.5 loss > 0.01 IoU. SMALL tile (~84 u^2, w15/w16 class)
     — the smallness driver alone predicts escalation, but probe both.

Outputs: wave19-fit.json, wave19-fit-overlay-kite.png
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
OUT = SESS / "iterations/60/measure"
PXU = math.sqrt(1091 / 640.7)

spec = importlib.util.spec_from_file_location("analyze_reference", TOOLS / "analyze-reference.py")
ar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ar)

plan = json.loads((SESS / "input/reference-analysis/wave-plan/wave-plan.json").read_text())
w19 = next(w for w in plan["waves"] if w["wave"] == 19)
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

real = [s for s in w19["shapes"] if not s["fragment"]]

# Window is Cartesian in units: X radial-ish, Y TANGENTIAL u (not deg).
# Measured folded extents (wave19-vertices.json): x 207.2-224.0,
# y 20.9-41.4.
GRID = 0.25
X0, X1, Y0, Y1 = 203.0, 228.0, 17.0, 45.0
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


def fit_family(name: str, members: list) -> dict:
    print(f"\n=== family {name}: {len(members)} members ===")
    stack = []
    areas = []
    for s in members:
        th_axis = round(s["theta_deg"] / 36) * 36
        rel = s["theta_deg"] - th_axis
        stack.append(shape_grid(s["id"], th_axis, mirror=(rel < 0)))
        areas.append(s["area_px"] / PXU**2)
    target = float(np.mean(areas))
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

    snaps = {}
    for g, M in ((0.5, 720), (0.25, 1440)):
        snapped = [[round(r, 1), round(x / g) * g] for r, x in model]
        snaps[g] = (iou(poly_mask(snapped)), snapped, M)
        print(f"g={g} (M={M}): snapped IoU {snaps[g][0]:.3f}")
    if best - snaps[0.5][0] <= 0.01:
        g = 0.5
        print("keeping g=0.5 (loss within 0.01)")
    else:
        g = 0.25
        print("g=0.5 loss > 0.01 — keeping g=0.25")
    siou, snapped, M = snaps[g]

    # STAR-TIP-axis convention: rel measured from the 0 mod 36 axis,
    # cpt = rel/g, mirror = M - cpt (wave-16 precedent: cpt x / M-x).
    rows = []
    for r, x in snapped:
        kp = round(x / g) % M
        km = (M - kp) % M
        rows.append({"r": r, "rel": x, "M": M, "cpt_plus": kp, "cpt_mirror": km})

    pm = poly_mask(snapped)
    rgb = np.zeros((NY, NX, 3), dtype=np.uint8)
    rgb[cons] = [150, 150, 150]
    edge = pm & ~ndimage.binary_erosion(pm)
    rgb[edge] = [255, 40, 40]
    Image.fromarray(np.flipud(rgb)).resize((NX * 3, NY * 3), Image.NEAREST).save(
        OUT / f"wave19-fit-overlay-{name}.png")

    return {
        "n_verts": n_pick, "fitted_iou": best, "snapped_iou": siou,
        "grid_deg": g,
        "area_u2": shoelace(snapped), "consensus_area_u2": float(cons.sum() * CELL),
        "vertices": rows,
    }


result = {"kite": fit_family("kite", real)}
(OUT / "wave19-fit.json").write_text(json.dumps(result, indent=1))
print("\nwave19-fit.json written")
