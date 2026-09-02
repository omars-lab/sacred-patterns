#!/usr/bin/env python3
"""analyze-reference.py — decompose a reference photo into the facts each stage steers by.

Plain English: before tuning a reconstruction's colors we should agree, once,
on WHAT the reference's colors actually are — instead of re-guessing them
every iteration (iter-36 and iter-38 both re-derived them ad hoc). This tool
separates the photo into its LINE population (the white lattice) and its FILL
population (the tile colors), extracts a standardized fill palette by
clustering, measures the line color and stroke width, and composes a swatch
sheet the owner can look at and say "those are the right colors" — the entry
gate to Stage 2 (color) of the stage-gated loop.

Outputs (under SESSION_DIR/input/reference-analysis/):
    reference-palette.json   line color/width + fill clusters (hex, area share)
    reference-analysis.md    zone→color table + the numbers, plain-English first
    swatch-sheet.png         reference beside its extracted swatches (the gate visual)

Usage (needs PIL + numpy — the qiyas venv has both):
    /Users/omareid/Workspace/git/qiyas/.venv/bin/python \\
        tools/analyze-reference.py /path/to/session-dir [--clusters 6]

Requires SESSION_DIR/input/reference.jpg and input/reference-structure.png
(the Stage-1 edge map produced by tools/structure-diff.sh — run that first).

Determinism (Tenet 8): k-means uses a fixed seed and fixed iteration count;
all thresholds are constants below. Same photo → identical palette JSON.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print(
        "error: needs numpy + PIL. Run with the qiyas venv python:\n"
        "  /Users/omareid/Workspace/git/qiyas/.venv/bin/python tools/analyze-reference.py ...",
        file=sys.stderr,
    )
    sys.exit(1)

# --- fixed constants (changing any of these invalidates cross-session
# --- comparability of palettes; tune only with a recorded reason) ----------
NEAR_WHITE_MIN = 200   # min(R,G,B) above this = lattice/background candidate
EDGE_DILATE_PX = 2     # fill pixels this close to an edge are excluded
                       # (they straddle the lattice boundary and are blends)
KMEANS_SEED = 0
KMEANS_ITERS = 40
# Radial zone bands (fraction of medallion radius). Zones are approximated
# radially because the medallion is centered; true per-region zones (rosette
# vs lens vs field) would need shape detection the frozen detector owns.
ZONE_BANDS = [(0.00, 0.18, "center"), (0.18, 0.45, "inner field"),
              (0.45, 0.75, "mid field"), (0.75, 1.10, "outer / boundary")]

# Human-friendly anchor names: each extracted cluster is labeled with the
# nearest anchor so the owner reads "navy", not "fill_3". Anchors are labels
# only — the palette VALUES are always the extracted cluster means.
COLOR_ANCHORS = {
    "deep_navy": (28, 36, 56),
    "navy": (19, 42, 97),
    "royal": (43, 97, 183),
    "periwinkle": (130, 158, 218),
    "cobalt": (50, 130, 200),
    "cyan": (50, 176, 202),
    "turquoise": (64, 200, 200),
    "steel": (90, 120, 160),
    "gray": (184, 184, 184),   # rim outline / lattice-blend population
    "white": (245, 245, 245),
}

# Closing radius (px) used to build the medallion mask from the colored
# content: must exceed the lattice half-width so the white strokes between
# tiles get bridged. Lattice measures ~7px on the 753px reference.
CLOSE_PX = 8


def dilate(mask: np.ndarray, iters: int) -> np.ndarray:
    """8-connected binary dilation via shifted ORs (no scipy dependency).

    dilate([[0,0,0],[0,1,0],[0,0,0]], 1) -> all-ones 3x3.
    """
    out = mask.copy()
    for _ in range(iters):
        m = out
        p = np.pad(m, 1)
        out = (
            p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
            | p[:-2, :-2] | p[:-2, 2:] | p[2:, :-2] | p[2:, 2:]
        )
    return out


def erode(mask: np.ndarray, iters: int = 1) -> np.ndarray:
    """8-connected binary erosion (dual of dilate) via shifted ANDs."""
    out = mask.copy()
    for _ in range(iters):
        p = np.pad(out, 1, constant_values=True)
        out = (
            p[1:-1, 1:-1] & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
            & p[:-2, :-2] & p[:-2, 2:] & p[2:, :-2] & p[2:, 2:]
        )
    return out


def medallion_mask(near_white: np.ndarray) -> np.ndarray:
    """Build the medallion region from the colored content by closing + flood.

    Why not flood the near-white from the border directly: the white lattice
    CONNECTS to the white background at the medallion's rim (same color,
    touching), so a border flood eats the lattice along with the background.
    Instead: take the colored content (~near_white), morphologically close it
    (dilate then erode by CLOSE_PX) so the lattice gaps between tiles are
    bridged, then flood the border-connected region of the complement — that
    is the true background, and the medallion is everything else.
    """
    closed = erode(dilate(~near_white, CLOSE_PX), CLOSE_PX)
    outside = ~closed
    grown = np.zeros_like(outside)
    grown[0, :] = outside[0, :]
    grown[-1, :] = outside[-1, :]
    grown[:, 0] = outside[:, 0]
    grown[:, -1] = outside[:, -1]
    while True:
        nxt = dilate(grown, 1) & outside
        if (nxt == grown).all():
            return ~grown
        grown = nxt


def estimate_stroke_width(line_mask: np.ndarray) -> float:
    """Estimate the lattice stroke width (px) by erosion-area regression.

    Why this works: for a stroke network of total length L and uniform width
    w, the area after k erosions is ~ L*(w - 2k) — linear in k. Fitting the
    early (still-linear) area decay and taking the x-intercept k* gives
    w = 2*k*. Junctions and corners only bend the tail, which we exclude.

    estimate_stroke_width(7px-wide synthetic grid) -> ~7.0
    """
    areas = [int(line_mask.sum())]
    if areas[0] == 0:
        return float("nan")
    m = line_mask
    while areas[-1] > 0 and len(areas) < 40:
        m = erode(m)
        areas.append(int(m.sum()))
    # Use the decay while area is still >30% of original (the linear regime).
    pts = [(k, a) for k, a in enumerate(areas) if a > 0.3 * areas[0]]
    if len(pts) < 2:
        # Mask died within one erosion: width is between 1 and 3 px.
        return 2.0
    ks = np.array([p[0] for p in pts], dtype=float)
    vs = np.array([p[1] for p in pts], dtype=float)
    slope, intercept = np.polyfit(ks, vs, 1)
    if slope >= 0:  # degenerate (blob, not strokes)
        return float("nan")
    return float(2.0 * (-intercept / slope))


def kmeans(pixels: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Plain numpy k-means with k-means++ init, fixed seed (deterministic).

    kmeans(Nx3 float array of RGB fills, 6) -> (6x3 centers, N labels).
    """
    rng = np.random.default_rng(KMEANS_SEED)
    # k-means++ seeding: spread initial centers by squared-distance sampling.
    centers = [pixels[rng.integers(len(pixels))]]
    for _ in range(k - 1):
        d2 = np.min(
            ((pixels[:, None, :] - np.array(centers)[None, :, :]) ** 2).sum(-1), axis=1
        )
        centers.append(pixels[rng.choice(len(pixels), p=d2 / d2.sum())])
    centers = np.array(centers, dtype=float)
    labels = np.zeros(len(pixels), dtype=int)
    for _ in range(KMEANS_ITERS):
        d2 = ((pixels[:, None, :] - centers[None, :, :]) ** 2).sum(-1)
        labels = d2.argmin(axis=1)
        for j in range(k):
            sel = pixels[labels == j]
            if len(sel):
                centers[j] = sel.mean(axis=0)
    return centers, labels


def nearest_anchor(rgb: tuple[float, float, float]) -> str:
    return min(
        COLOR_ANCHORS,
        key=lambda n: sum((a - b) ** 2 for a, b in zip(COLOR_ANCHORS[n], rgb)),
    )


def hexc(rgb) -> str:
    return "#{:02X}{:02X}{:02X}".format(*(int(round(c)) for c in rgb))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("session_dir", type=Path)
    ap.add_argument("--clusters", type=int, default=6,
                    help="fill clusters (chosen by eye from the photo; default 6)")
    args = ap.parse_args()

    ref_path = args.session_dir / "input" / "reference.jpg"
    edge_path = args.session_dir / "input" / "reference-structure.png"
    out_dir = args.session_dir / "input" / "reference-analysis"
    if not ref_path.is_file():
        sys.exit(f"error: {ref_path} not found")
    if not edge_path.is_file():
        sys.exit(f"error: {edge_path} not found — run tools/structure-diff.sh first")
    out_dir.mkdir(parents=True, exist_ok=True)

    img = np.asarray(Image.open(ref_path).convert("RGB"), dtype=float)
    edges_img = np.asarray(Image.open(edge_path).convert("L"))
    edge_mask = edges_img < 128  # edge map is dark-lines-on-white

    # --- line vs fill separation -------------------------------------------
    near_white = img.min(axis=2) > NEAR_WHITE_MIN
    medallion = medallion_mask(near_white)
    line_mask = near_white & medallion           # the lattice
    edge_zone = dilate(edge_mask, EDGE_DILATE_PX)
    fill_mask = medallion & ~near_white & ~edge_zone

    line_rgb = tuple(np.median(img[line_mask], axis=0)) if line_mask.any() else (255,) * 3
    width_px = estimate_stroke_width(line_mask)

    ys, xs = np.nonzero(medallion)
    cy, cx = ys.mean(), xs.mean()
    diameter = max(ys.max() - ys.min(), xs.max() - xs.min())

    # --- standardized fill palette -----------------------------------------
    fill_pixels = img[fill_mask]
    centers, labels = kmeans(fill_pixels, args.clusters)
    shares = np.bincount(labels, minlength=args.clusters) / len(labels)
    order = np.argsort(-shares)

    clusters = []
    used_names: dict[str, int] = {}
    for j in order:
        name = nearest_anchor(tuple(centers[j]))
        # Two clusters can land on the same anchor; suffix the later one.
        used_names[name] = used_names.get(name, 0) + 1
        if used_names[name] > 1:
            name = f"{name}_{used_names[name]}"
        clusters.append({
            "name": name,
            "hex": hexc(centers[j]),
            "area_share": round(float(shares[j]), 4),
            "_label": int(j),
        })

    # --- radial zone table --------------------------------------------------
    fy, fx = np.nonzero(fill_mask)
    r = np.hypot(fy - cy, fx - cx) / (diameter / 2.0)
    zone_rows = []
    for lo, hi, zname in ZONE_BANDS:
        sel = (r >= lo) & (r < hi)
        if not sel.any():
            continue
        band_labels = labels[sel]
        counts = np.bincount(band_labels, minlength=args.clusters) / len(band_labels)
        top = sorted(clusters, key=lambda c: -counts[c["_label"]])[:3]
        zone_rows.append((zname, [(c["name"], round(float(counts[c["_label"]]) * 100)) for c in top]))

    # --- reference-palette.json ---------------------------------------------
    palette = {
        "source": "input/reference.jpg",
        "tool": "tools/analyze-reference.py",
        "line": {
            "hex": hexc(line_rgb),
            "width_px": round(width_px, 1),
            "width_over_diameter": round(width_px / diameter, 5),
            "note": "the white lattice — feeds Stage 3 strapwork color/width",
        },
        "fills": [{k: v for k, v in c.items() if not k.startswith("_")} for c in clusters],
        "constants": {
            "near_white_min": NEAR_WHITE_MIN,
            "edge_dilate_px": EDGE_DILATE_PX,
            "kmeans_seed": KMEANS_SEED,
            "clusters": args.clusters,
        },
    }
    (out_dir / "reference-palette.json").write_text(json.dumps(palette, indent=2) + "\n")

    # --- reference-analysis.md ----------------------------------------------
    md = [
        "# Reference analysis — standardized palette + line measurements",
        "",
        "Plain English: these are the colors the reference photo actually uses,",
        "extracted once so color iterations tune toward an agreed target instead",
        "of re-guessing. Stage 2 `palette` blocks use these hex values verbatim;",
        "iterations only change which faces map to which named color.",
        "",
        f"- **Lattice line:** `{palette['line']['hex']}`, width ≈ {width_px:.1f}px"
        f" ({width_px / diameter:.3%} of medallion diameter {diameter}px)",
        f"- **Fill clusters (k={args.clusters}, area share of fill pixels):**",
        "",
        "| name | hex | share |",
        "|---|---|---|",
    ]
    md += [f"| {c['name']} | `{c['hex']}` | {c['area_share']:.1%} |" for c in clusters]
    if any(c["name"].startswith("gray") for c in clusters):
        md += ["", "Note: the `gray` cluster is the medallion's rim outline plus"
               " lattice-blend pixels, not a tile color — Stage 2 palettes skip it."]
    md += ["", "## Zone dominance (radial bands, top-3 clusters per band)", "",
           "| zone | dominant colors |", "|---|---|"]
    md += [f"| {z} | " + ", ".join(f"{n} {p}%" for n, p in tops) + " |" for z, tops in zone_rows]
    md += ["", "Swatch sheet: `swatch-sheet.png` — the Stage-2 entry-gate visual."]
    (out_dir / "reference-analysis.md").write_text("\n".join(md) + "\n")

    # --- swatch sheet (the owner-facing gate visual) -------------------------
    ref_thumb = Image.open(ref_path).convert("RGB")
    th = 520
    ref_thumb = ref_thumb.resize((int(ref_thumb.width * th / ref_thumb.height), th))
    row_h, sw_w, panel_w = 62, 120, 420
    rows = len(clusters) + 1
    sheet = Image.new("RGB", (ref_thumb.width + panel_w, max(th, rows * row_h + 20)), "white")
    sheet.paste(ref_thumb, (0, (sheet.height - th) // 2))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.load_default(size=16)
    except TypeError:  # older PIL: no size kwarg
        font = ImageFont.load_default()
    x0 = ref_thumb.width + 16
    entries = [("lattice line", palette["line"]["hex"],
                f"width {width_px:.1f}px")] + [
        (c["name"], c["hex"], f"{c['area_share']:.1%} of fills") for c in clusters
    ]
    for i, (name, hx, note) in enumerate(entries):
        y = 10 + i * row_h
        draw.rectangle([x0, y, x0 + sw_w, y + row_h - 14], fill=hx, outline="#888")
        draw.text((x0 + sw_w + 12, y + 2), f"{name}  {hx}", fill="black", font=font)
        draw.text((x0 + sw_w + 12, y + 24), note, fill="#555", font=font)
    sheet.save(out_dir / "swatch-sheet.png")

    print(f"analyze-reference: line={palette['line']['hex']} width={width_px:.1f}px "
          f"clusters={args.clusters} -> {out_dir}")
    for c in clusters:
        print(f"  {c['name']:<14} {c['hex']}  {c['area_share']:.1%}")


if __name__ == "__main__":
    main()
