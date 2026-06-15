#!/usr/bin/env python3
"""Iter-49 wave-7 measurement — segment the reference exactly as plan-waves
does, pull the wave-7 shape masks, and extract canonical-frame vertex
clusters so the shield model can be grid-snapped in pattern units.

Question this answers (Tenet 9): what polygon, in pattern units relative to
the 36-deg repeat axis, reproduces the 40 small deep-navy wave-7 tiles?

Outputs under iterations/49/measure/:
    wave7-tinted.png   reference crop with wave-7 shapes tinted red (visual ID)
    wave7-zoom-<id>.png  mask + image zoom of two sample shapes (one per ring)
    wave7-vertices.json  canonical-frame vertex clusters + per-shape areas
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

SESS = Path("/Users/omareid/Library/CloudStorage/Dropbox/Data/sacred-patterns/bikar-medallion-10")
TOOLS = Path("/Users/omareid/Workspace/git/sacred-patterns/tools")
OUT = SESS / "iterations/49/measure"

spec = importlib.util.spec_from_file_location("analyze_reference", TOOLS / "analyze-reference.py")
ar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ar)

plan = json.loads((SESS / "input/reference-analysis/wave-plan/wave-plan.json").read_text())
w7 = next(w for w in plan["waves"] if w["wave"] == 7)
cx, cy = plan["center"]["x"], plan["center"]["y"]
radius_px = plan["diameter_px"] / 2.0

img = Image.open(SESS / "input/reference.jpg").convert("RGB")
a = np.asarray(img)
near_white = (a >= 200).all(axis=2)
medallion = ar.medallion_mask(near_white)
tiles = medallion & ~near_white
four = ndimage.generate_binary_structure(2, 1)
cores = ndimage.binary_erosion(tiles, structure=four, iterations=2)
seed_labels, n = ndimage.label(cores, structure=four)
_, (iy, ix) = ndimage.distance_transform_edt(seed_labels == 0, return_indices=True)
labels = np.where(tiles, seed_labels[iy, ix], 0)
print(f"{n} shapes segmented (plan had {plan['total_shapes']})")

real = [s for s in w7["shapes"] if not s["fragment"]]
ids = [s["id"] for s in real]

# Sanity: the plan's per-shape centroids must match this segmentation's labels.
for s in real[:3]:
    m = labels == s["id"]
    ys, xs = np.nonzero(m)
    print(f"id {s['id']}: plan ({s['x']:.0f},{s['y']:.0f}) seg ({xs.mean():.0f},{ys.mean():.0f}) area plan {s['area_px']} seg {m.sum()}")

# Tinted overview: wave-7 red on a dimmed reference.
dim = (a * 0.45).astype(np.uint8)
w7mask = np.isin(labels, ids)
tinted = dim.copy()
tinted[w7mask] = [255, 40, 40]
ys, xs = np.nonzero(medallion)
y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
Image.fromarray(tinted[y0:y1, x0:x1]).save(OUT / "wave7-tinted.png")

# Zooms: one sample per sub-ring (inner ~0.376, outer ~0.421).
for sid in (92, 107):  # 92: outer ring theta 83.3; 107: inner ring theta 76.8
    s = next(x for x in real if x["id"] == sid)
    m = labels == sid
    ys, xs = np.nonzero(m)
    pad = 14
    yy0, yy1, xx0, xx1 = ys.min()-pad, ys.max()+pad, xs.min()-pad, xs.max()+pad
    crop = a[yy0:yy1, xx0:xx1]
    mcrop = (m[yy0:yy1, xx0:xx1] * 255).astype(np.uint8)
    z = 8
    big = np.concatenate([
        np.asarray(Image.fromarray(crop).resize(((xx1-xx0)*z, (yy1-yy0)*z), Image.NEAREST)),
        np.stack([np.asarray(Image.fromarray(mcrop).resize(((xx1-xx0)*z, (yy1-yy0)*z), Image.NEAREST))]*3, axis=2),
    ], axis=1)
    Image.fromarray(big).save(OUT / f"wave7-zoom-{sid}.png")
    print(f"zoom id {sid}: theta {s['theta_deg']} r_frac {s['r_frac']} area {s['area_px']}")

# --- canonical-frame vertex extraction --------------------------------------
# Each shape is rotated so its cluster axis (theta mod 36 cluster center)
# maps to 0 deg; vertices then cluster across all 40 shapes. Mirror-fold the
# two reflected clusters (about the dart axis 18) onto their partners so all
# 40 shapes witness ONE model (the +side); the .bkr authors the -side by grid
# symmetry.
import math

def contour_polygon(mask: np.ndarray, eps: float) -> np.ndarray:
    """Douglas-Peucker simplified outer contour (marching squares via PIL-free)."""
    # boundary pixels -> ordered walk via cv2 if available, else convex-ish trace
    try:
        import cv2
        cnts, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        c = max(cnts, key=cv2.contourArea)
        approx = cv2.approxPolyDP(c, eps, True)
        return approx[:, 0, :].astype(float)
    except ImportError:
        sys.exit("cv2 required for contour extraction")

records = []
for s in real:
    m = labels == s["id"]
    th_axis_repeat = (s["theta_deg"] // 36) * 36 + 18.0  # the dart axis of this repeat
    rel = s["theta_deg"] - th_axis_repeat                # signed offset from dart axis
    poly = contour_polygon(m, eps=1.2)
    # to pattern frame: x right, y UP, theta CCW from +x; rotate so repeat axis -> 18 deg
    px = poly[:, 0] - cx
    py = -(poly[:, 1] - cy)
    ang = math.radians(-(th_axis_repeat - 18.0))
    ca, sa = math.cos(ang), math.sin(ang)
    rx = px * ca - py * sa
    ry = px * sa + py * ca
    # mirror-fold: shapes on the -side of the dart axis reflect about the 18-deg line
    side = 1 if rel > 0 else -1
    if side < 0:
        a18 = math.radians(18.0)
        # reflect across line at angle 18
        for i in range(len(rx)):
            r = math.hypot(rx[i], ry[i]); t = math.atan2(ry[i], rx[i])
            t2 = 2*a18 - t
            rx[i], ry[i] = r*math.cos(t2), r*math.sin(t2)
    verts = [
        {"r": float(math.hypot(x_, y_)), "theta": float((math.degrees(math.atan2(y_, x_))) % 360)}
        for x_, y_ in zip(rx, ry)
    ]
    records.append({
        "id": s["id"], "theta_deg": s["theta_deg"], "rel": rel, "side": side,
        "r_frac": s["r_frac"], "area_px": int((labels == s["id"]).sum()),
        "n_verts": len(verts), "verts": verts,
    })

(OUT / "wave7-vertices.json").write_text(json.dumps({
    "center": [cx, cy], "radius_px": radius_px, "records": records}, indent=1))
vc = sorted(set(r["n_verts"] for r in records))
print("vertex counts seen:", {v: sum(1 for r in records if r['n_verts']==v) for v in vc})
print("rel offsets:", sorted(round(r['rel'],1) for r in records)[:12], "...")
