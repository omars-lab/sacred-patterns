"""Iter-61 wave-20 measurement — segment the reference exactly as plan-waves
does, pull the wave-20 shape masks, and extract canonical-frame vertex
clusters so the tile model can be grid-snapped in pattern units.

Question this answers (Tenet 9): what polygon, in pattern units relative
to the DART axis (18 mod 36), reproduces the 20 medium navy wave-20
tiles (~614 u^2, r_frac 0.829-0.838)? Plan thetas sit at rel +-5.4..6.6
about the dart axes (e.g. 12.0/24.6 about axis 18) — ONE MIRROR PAIR
per dart axis (wave-7/10/17 off-axis dart topology at the outer edge).
Medium tile: probe both grids per protocol — area alone does NOT
predict the grid (the discriminator is angular feature scale; w13/w17
escalated on near-axis vertex precision despite size).

Outputs under iterations/61/measure/:
    wave20-tinted.png    reference crop with wave-20 shapes tinted red
    wave20-zoom-<id>.png mask + image zoom of four sample shapes
    wave20-vertices.json canonical-frame vertex clusters + per-shape areas
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

SESS = Path("/Users/omareid/Library/CloudStorage/Dropbox/Data/sacred-patterns/bikar-medallion-10")
TOOLS = Path("/Users/omareid/Workspace/git/sacred-patterns/tools")
OUT = SESS / "iterations/61/measure"
PXU = math.sqrt(1091 / 640.7)

spec = importlib.util.spec_from_file_location("analyze_reference", TOOLS / "analyze-reference.py")
ar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ar)

plan = json.loads((SESS / "input/reference-analysis/wave-plan/wave-plan.json").read_text())
w18 = next(w for w in plan["waves"] if w["wave"] == 20)
cx, cy = plan["center"]["x"], plan["center"]["y"]

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

real = [s for s in w18["shapes"] if not s["fragment"]]
ids = [s["id"] for s in real]

for s in real[:3]:
    m = labels == s["id"]
    ys, xs = np.nonzero(m)
    print(f"id {s['id']}: plan ({s['x']:.0f},{s['y']:.0f}) seg ({xs.mean():.0f},{ys.mean():.0f}) "
          f"area plan {s['area_px']} seg {m.sum()}")

dim = (a * 0.45).astype(np.uint8)
wmask = np.isin(labels, ids)
tinted = dim.copy()
tinted[wmask] = [255, 40, 40]
ys, xs = np.nonzero(medallion)
y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
Image.fromarray(tinted[y0:y1, x0:x1]).save(OUT / "wave20-tinted.png")

for s in sorted(real, key=lambda s: abs(s['theta_deg'] % 36 - 18))[:4]:
    sid = s["id"]
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
    Image.fromarray(big).save(OUT / f"wave20-zoom-{sid}.png")
    print(f"zoom id {sid}: theta {s['theta_deg']} r_frac {s['r_frac']} area {s['area_px']}")

# --- canonical-frame vertex extraction: rotate each repeat's STAR-TIP axis to 0.
def contour_polygon(mask: np.ndarray, eps: float) -> np.ndarray:
    try:
        import cv2
        cnts, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        c = max(cnts, key=cv2.contourArea)
        approx = cv2.approxPolyDP(c, eps, True)
        return approx[:, 0, :].astype(float)
    except ImportError:
        sys.exit("cv2 required for contour extraction")

records = []
rmins, rmaxs = [], []
for s in real:
    m = labels == s["id"]
    # DART axes: 18 mod 36 (wave-7/10/17 convention)
    th_axis = (s["theta_deg"] // 36) * 36 + 18
    rel = s["theta_deg"] - th_axis
    poly = contour_polygon(m, eps=1.2)
    px = poly[:, 0] - cx
    py = -(poly[:, 1] - cy)
    ang = math.radians(-th_axis)
    ca, sa = math.cos(ang), math.sin(ang)
    rx = px * ca - py * sa
    ry = px * sa + py * ca
    verts = [
        {"r": float(math.hypot(x_, y_) / PXU), "theta": float(math.degrees(math.atan2(y_, x_)) % 360)}
        for x_, y_ in zip(rx, ry)
    ]
    rs = [v["r"] for v in verts]
    rmins.append(min(rs)); rmaxs.append(max(rs))
    records.append({
        "id": s["id"], "theta_deg": s["theta_deg"], "rel": rel,
        "r_frac": s["r_frac"], "area_px": int(m.sum()),
        "n_verts": len(verts), "verts": verts,
    })

(OUT / "wave20-vertices.json").write_text(json.dumps({
    "center": [cx, cy], "px_per_u": PXU, "records": records}, indent=1))
vc = sorted(set(r["n_verts"] for r in records))
print("vertex counts seen:", {v: sum(1 for r in records if r['n_verts'] == v) for v in vc})
print(f"radial extent (u): r_min {min(rmins):.1f}-{max(rmins):.1f}, r_max {min(rmaxs):.1f}-{max(rmaxs):.1f}")
print("rel offsets:", sorted(round(r['rel'], 1) for r in records))
print("mean area u^2:", round(sum(r['area_px'] for r in records) / len(records) / PXU**2, 1))
