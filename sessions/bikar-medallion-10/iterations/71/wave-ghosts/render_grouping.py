#!/usr/bin/env python3
"""#46 — Higher-level grouping VIEW. Answer "what is the medallion's organizing
structure?" at a glance — not "26 shape classes" (that's #45's flat inventory) but
"one repeating wedge, rotated 10x, stacked in 26 concentric bands."

WHY a view (not just the cluster list): #45 told the owner the medallion is built
from 26 distinct shapes. That's the vocabulary. This view tells the owner how those
shapes are ORGANIZED: every class sits at a fixed radius (perfectly concentric — radial
spread 0.0 after recentering on the pattern center), and every class is one of three
10-fold roles:
  - ON-AXIS    (x10, centered on a spoke axis 0/36 deg mod 36) — the petals/shields
                that sit ON each of the 10 arms
  - HALF-AXIS  (x10, at 18 deg mod 36) — the shapes that sit BETWEEN arms
  - PAIRED     (x20, a mirror pair L/R about a spoke) — the left+right halves of an
                arm motif
plus one CENTER (x1, r=0) unique centerpiece.

So the whole 381-shape medallion collapses to ONE 36-degree wedge (38 shapes) rotated
10 times. This view draws that: a polar band map (left) showing all 26 concentric rings
color-coded by role, and the single repeating wedge (right) — the motif that tiles the
medallion. The eye gets "it's one wedge x10, in 26 bands" in ~2 seconds (Tenet 27).

Reads clusters.json (cluster_shapes.py output); member_centers are in RASTER pixel
coords, so we recenter on the pattern center = centroid of all member centers
(~512.2, 512.2) before computing radii/angles. Authored code -> git; PNG -> Dropbox.

Run: python3 render_grouping.py [iter]   (default iter 71)
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

B = Path("/Users/omareid/Library/CloudStorage/Dropbox/Data/sacred-patterns/bikar-medallion-10")
ITER = sys.argv[1] if len(sys.argv) > 1 else "71"
WG = B / "iterations" / ITER / "wave-ghosts"
CL = json.loads((WG / "clusters.json").read_text())
clusters = CL["clusters"]

# role colors — warm = on the arm, cool = between arms, neutral = center
ROLE_COLOR = {
    "ON-AXIS": "#D2691E",    # warm orange: shapes centered on a spoke
    "HALF-AXIS": "#2C7FB8",  # cool blue: shapes between spokes
    "PAIRED": "#7B5EA7",     # purple: mirror-paired (arm L/R halves)
    "CENTER": "#B22222",     # deep red: the unique centerpiece
}


def font(sz, bold=False):
    name = "Arial Bold.ttf" if bold else "Arial.ttf"
    try:
        return ImageFont.truetype(f"/System/Library/Fonts/Supplemental/{name}", sz)
    except Exception:
        return ImageFont.load_default()


F_HERO = font(58, bold=True)
F_SUB = font(20)
F_SECTION = font(22, bold=True)
F_CAP = font(13)
F_CAPB = font(14, bold=True)
F_LEG = font(16)

# --- recenter + classify each band's 10-fold role -------------------------------
allc = [p for c in clusters for p in c["member_centers"]]
CX = sum(p[0] for p in allc) / len(allc)
CY = sum(p[1] for p in allc) / len(allc)


def role(c):
    """A class's 10-fold role from its members' angular positions (mod 36 deg)."""
    angs = sorted({round(((math.degrees(math.atan2(p[1] - CY, p[0] - CX)) + 360) % 360) % 36, 1)
                   for p in c["member_centers"]})
    if c["count"] == 1:
        return "CENTER"
    if c["count"] == 20:
        return "PAIRED"
    if c["count"] == 10:
        if any(abs(a) < 2 or abs(a - 36) < 2 for a in angs):
            return "ON-AXIS"
        return "HALF-AXIS"
    return "OTHER"


bands = []  # (r, cluster, role, mean_angle_deg)
for c in clusters:
    rs = [math.hypot(p[0] - CX, p[1] - CY) for p in c["member_centers"]]
    r = sum(rs) / len(rs)
    # representative angle: the first member's angle (for placing it in the wedge)
    p0 = c["member_centers"][0]
    a = (math.degrees(math.atan2(p0[1] - CY, p0[0] - CX)) + 360) % 360
    bands.append((r, c, role(c), a))
bands.sort(key=lambda b: b[0])

R_MAX = max(b[0] for b in bands) or 1


def fit_outline(outline, ang_deg, cx, cy, r, span_px):
    """Place a class's representative outline at polar (r, ang) on the band map,
    scaled to a small glyph. Outline is in raster coords; recenter + scale + rotate
    to sit on its band at its true angle."""
    xs = [p[0] for p in outline]
    ys = [p[1] for p in outline]
    w = (max(xs) - min(xs)) or 1
    h = (max(ys) - min(ys)) or 1
    s = span_px / max(w, h)
    ocx, ocy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    # target position on the band map
    a = math.radians(ang_deg)
    px = cx + r * math.cos(a)
    py = cy + r * math.sin(a)
    return [(px + (p[0] - ocx) * s, py + (p[1] - ocy) * s) for p in outline]


# --- canvas ---------------------------------------------------------------------
MAP = 760          # polar band-map square (left)
WEDGE = 520        # repeating-wedge panel (right)
MARGIN = 40
HEADER = 150
GAP = 50
W = MARGIN + MAP + GAP + WEDGE + MARGIN
H = HEADER + MARGIN + max(MAP, WEDGE + 180) + MARGIN

img = Image.new("RGB", (W, H), "#FFFFFF")
d = ImageDraw.Draw(img)

# --- header ---------------------------------------------------------------------
n_paired = sum(1 for b in bands if b[2] == "PAIRED")
n_axis = sum(1 for b in bands if b[2] == "ON-AXIS")
n_half = sum(1 for b in bands if b[2] == "HALF-AXIS")
wedge_count = sum(b[1]["count"] for b in bands) // 10

y = MARGIN
d.text((MARGIN, y), "One wedge, rotated 10x, in 26 bands", fill="#111", font=F_HERO)
y += 70
d.text((MARGIN, y),
       f"{len(bands)} concentric shape-bands collapse to one {wedge_count}-shape wedge "
       f"that tiles the medallion 10-fold",
       fill="#333", font=F_SUB)
y += 28
d.text((MARGIN, y),
       f"{n_axis} on-arm rings   +   {n_half} between-arm rings   +   "
       f"{n_paired} mirror-paired rings   +   1 centerpiece",
       fill="#777", font=F_SUB)

# --- LEFT: polar band map -------------------------------------------------------
map_x0, map_y0 = MARGIN, HEADER + MARGIN
mcx, mcy = map_x0 + MAP / 2, map_y0 + MAP / 2
draw_R = MAP / 2 - 50

# 10 faint spoke axes
for k in range(10):
    a = math.radians(k * 36)
    d.line([mcx, mcy, mcx + draw_R * math.cos(a), mcy + draw_R * math.sin(a)],
           fill="#E8E8E8", width=1)

# each band as a concentric ring of its glyph, colored by role
for r, c, rl, a0 in bands:
    rr = (r / R_MAX) * draw_R
    color = ROLE_COLOR[rl]
    n = c["count"]
    # draw the class glyph at each of its true angular positions on the ring
    for p in c["member_centers"]:
        pa = (math.degrees(math.atan2(p[1] - CY, p[0] - CX)) + 360) % 360
        glyph = fit_outline(c["representative_outline"], pa, mcx, mcy, rr, 26)
        if c["kind"] == "circle" or len(glyph) < 3:
            gx = mcx + rr * math.cos(math.radians(pa))
            gy = mcy + rr * math.sin(math.radians(pa))
            d.ellipse([gx - 5, gy - 5, gx + 5, gy + 5], fill=color, outline="#333")
        else:
            d.polygon(glyph, fill=color, outline="#333")
# center marker
d.ellipse([mcx - 7, mcy - 7, mcx + 7, mcy + 7], fill=ROLE_COLOR["CENTER"], outline="#333")
d.text((map_x0, map_y0 + MAP - 6), "Full medallion — every class is one concentric band",
       fill="#555", font=F_CAP)

# --- RIGHT: the single repeating wedge (one 36deg slice, center -> rim) ----------
wx0 = MARGIN + MAP + GAP
d.text((wx0, HEADER), "The repeating wedge  (36 deg, rotate 10x = whole)",
       fill="#111", font=F_SECTION)
wy = HEADER + 50
# Draw the wedge as a vertical stack: center at top, rim at bottom; one glyph per
# band that participates in a single wedge (CENTER + one rep from each ring).
# A band contributes its on-wedge shape(s): on-axis/half-axis => 1 glyph; paired => 2.
row_h = 30
swatch = 26
col_axis = wx0 + 30          # on-axis column (spoke center)
col_left = wx0 + 30 - 60     # paired-left
col_right = wx0 + 30 + 60    # paired-right
# normalize: clamp columns within panel
for r, c, rl, a0 in bands:
    color = ROLE_COLOR[rl]
    label = f'{c["cluster_id"]} {c["vertex_count"]}gon'
    if rl == "CENTER":
        cols = [wx0 + 30]
    elif rl == "PAIRED":
        cols = [wx0 + 14, wx0 + 14 + 52]
    else:
        cols = [wx0 + 40]
    for cxp in cols:
        outline = c["representative_outline"]
        if c["kind"] == "circle" or len(outline) < 3:
            d.ellipse([cxp, wy, cxp + swatch, wy + swatch], fill=color, outline="#333")
        else:
            xs = [p[0] for p in outline]; ys = [p[1] for p in outline]
            w0 = (max(xs) - min(xs)) or 1; h0 = (max(ys) - min(ys)) or 1
            s = (swatch) / max(w0, h0)
            ocx, ocy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
            gly = [(cxp + swatch / 2 + (p[0] - ocx) * s, wy + swatch / 2 + (p[1] - ocy) * s)
                   for p in outline]
            d.polygon(gly, fill=color, outline="#333")
    d.text((wx0 + 130, wy + 4), f"r={r:4.0f}  {label}  {rl.lower()}", fill="#444", font=F_CAP)
    wy += row_h

# --- legend ---------------------------------------------------------------------
ly = wy + 16
d.text((wx0, ly), "Role legend", fill="#111", font=F_CAPB)
ly += 24
for rl, col in [("ON-AXIS", "on a spoke arm"), ("HALF-AXIS", "between arms"),
                ("PAIRED", "arm L/R halves (x20)"), ("CENTER", "unique centerpiece")]:
    d.rectangle([wx0, ly, wx0 + 18, ly + 18], fill=ROLE_COLOR[rl], outline="#333")
    d.text((wx0 + 26, ly + 1), f"{rl.lower()} — {col}", fill="#444", font=F_LEG)
    ly += 26

out = WG / "shape-grouping.png"
img.save(out)
print(f"grouping: {len(bands)} bands -> 1 wedge x10 "
      f"({n_axis} on-axis + {n_half} half-axis + {n_paired} paired + 1 center) -> {out}")
