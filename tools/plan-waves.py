#!/usr/bin/env python3
"""Radial wave plan for source-image reconstruction (Stage-1 planning artifact).

Plain English: before reconstructing a pattern we plan WHICH shapes to copy in
WHAT order — concentric waves working outward from the validated center. This
tool finds every colored tile in the reference photo (the white lattice
separates them), assigns each to a radial wave, and emits a flip-through
planning experience the owner gates BEFORE any construction iteration. The
loop then attacks wave 1 until it matches, then wave 2, etc. — per-wave diffs,
never a one-shot whole-image diff.

Why exhaustive: the owner's gate condition is "all shapes from the original
image exhausted" — every tile pixel must belong to some wave, and the JSON
reports the coverage number so the claim is checkable, not vibes.

Usage:
    /Users/omareid/Workspace/git/qiyas/.venv/bin/python tools/plan-waves.py \
        /Users/omareid/Dropbox/Data/sacred-patterns/bikar-medallion-10 \
        --center 386 361 --diameter 738

Outputs (under <session>/input/reference-analysis/wave-plan/):
    wave-plan.json   waves -> shapes (centroid, r_frac, theta, area, color)
    wave-<k>.png     wave k in full color over a dimmed grayscale reference
    waves-map.png    every shape tinted by its wave (distinct colors, Tenet 24)
    flower-<f>.png   composite flower f: one instance bright, its rotated
                     twins half-bright, everything else pale
    flowers-map.png  every shape tinted by its composite flower
    wave-plan.html   the flip-through planning experience (plain language)

Two grouping levels (owner, 2026-06-11): a WAVE is one kind of simple shape
(equidistant midpoints, rotated copies, similar area+color); a FLOWER (motif)
is the composite the owner sees — "a shape similar to our middle one that
revolves around the origin" — several waves dressing one anchor star,
repeated fold times. Build once, spin fold times: the DSL-native unit.

Example: medallion-10 reference (753x722, center (386,361), diameter 738) ->
22 same-kind waves over 426 shapes (380 real + 46 fragments), counts all
10-fold (1, 10s, 20s, 40s); 3 composite flowers (middle x1, inner x10 @
r~0.46, outer x10 @ r~0.76); 100.0% of colored-tile area assigned.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

# Same near-white threshold as analyze-reference.py so "tile" means the same
# thing in both tools (lattice + background are near-white; tiles are not).
NEAR_WHITE_MIN = 200
# Components smaller than this are jpg-noise slivers along lattice edges; they
# still get a wave (exhaustiveness) but are reported separately as fragments.
FRAGMENT_AREA = 25
# Why erode before labeling: JPEG softening leaves 1-3px sub-threshold gaps in
# the ~5px white lattice, so adjacent tiles touch and the whole medallion fuses
# into ONE component (witnessed first run: 41 shapes, all-red waves-map).
# Eroding snaps those thin bridges; labels are then grown back over the full
# tile mask via nearest-seed so coverage stays 100%.
ERODE_ITERS = 2
# Anchor detection: rosette-center stars are the LARGEST tiles in the photo
# (witnessed on medallion-10: center 1687px, rim ring ~1690px, middle ring
# ~1485px vs interstitial stars ~1100px). Shapes within this fraction of the
# max area are anchors; anchors whose radii differ by more than RING_GAP form
# separate rings. Rings provide the plain-language "where" labels for wave
# captions only — the waves themselves come from same-kind grouping.
ANCHOR_AREA_FRAC = 0.8
RING_GAP = 0.1

# Distinct per-wave tints (Tenet 24: never debug/plan in monochrome).
WAVE_COLORS = ["#E64A19", "#F9A825", "#43A047", "#1E88E5", "#8E24AA", "#00ACC1"]
# Plain-language color words for captions (Tenet 27 — no palette jargon).
FRIENDLY = {
    "navy": "dark-blue",
    "navy_2": "dark-blue",
    "royal": "blue",
    "cyan": "light-blue",
    "cyan_2": "turquoise",
    "periwinkle": "lilac",
    "gray": "gray",
}


def load_analyze_reference(tools_dir: Path):
    """Reuse medallion_mask + palette anchors from analyze-reference.py
    (single source of truth for what counts as medallion / which blues exist)."""
    spec = importlib.util.spec_from_file_location(
        "ar", tools_dir / "analyze-reference.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("session_dir", type=Path)
    ap.add_argument("--center", nargs=2, type=float, required=True)
    ap.add_argument("--diameter", type=float, required=True)
    ap.add_argument("--reference", default="input/reference.jpg")
    ap.add_argument(
        "--seat",
        action="append",
        default=[],
        metavar="WAVE=FLOWER",
        help="Owner re-seat from the gate, e.g. --seat 13=3 moves wave 13 "
        "into flower family 3 (both 1-based) without a code change.",
    )
    args = ap.parse_args()

    tools_dir = Path(__file__).resolve().parent
    ar = load_analyze_reference(tools_dir)

    img = Image.open(args.session_dir / args.reference).convert("RGB")
    a = np.asarray(img)
    near_white = (a >= NEAR_WHITE_MIN).all(axis=2)
    medallion = ar.medallion_mask(near_white)
    tiles = medallion & ~near_white

    # Every lattice-separated colored region becomes one labelled shape.
    # 4-connectivity + erosion so tiles can't bleed through soft lattice gaps;
    # labels are grown back over the full tile mask (nearest seed) afterwards.
    four = ndimage.generate_binary_structure(2, 1)
    cores = ndimage.binary_erosion(tiles, structure=four, iterations=ERODE_ITERS)
    seed_labels, n = ndimage.label(cores, structure=four)
    _, (iy, ix) = ndimage.distance_transform_edt(seed_labels == 0, return_indices=True)
    labels = np.where(tiles, seed_labels[iy, ix], 0)
    print(f"{n} connected shapes in the tile mask (after {ERODE_ITERS}px bridge-snap)")

    cx, cy = args.center
    radius = args.diameter / 2.0
    idx = np.arange(1, n + 1)
    areas = ndimage.sum_labels(tiles, labels, idx)
    cys, cxs = zip(*ndimage.center_of_mass(tiles, labels, idx))
    cxs, cys = np.array(cxs), np.array(cys)
    r_frac = np.hypot(cxs - cx, cys - cy) / radius
    theta = (np.degrees(np.arctan2(-(cys - cy), cxs - cx)) + 360) % 360
    mean_rgb = np.stack(
        [ndimage.mean(a[..., ch], labels, idx) for ch in range(3)], axis=1
    )

    real = areas >= FRAGMENT_AREA

    # Waves = rings of flowers. Anchors (the big rosette-center stars) group
    # into radial rings; every shape joins the wave of its NEAREST anchor, so
    # a wave is a set of whole flowers — the unit the owner judges — rather
    # than a raw radius band that would cut flowers in half (witnessed second
    # run: radius-histogram waves put 93% of the pattern in one wave because
    # the outer field has no radial density valleys).
    anchor_ids = np.nonzero(areas >= ANCHOR_AREA_FRAC * areas.max())[0]
    by_r = anchor_ids[np.argsort(r_frac[anchor_ids])]
    rings: list[list[int]] = [[int(by_r[0])]]
    for i in by_r[1:]:
        if r_frac[i] - r_frac[rings[-1][-1]] > RING_GAP:
            rings.append([int(i)])
        else:
            rings[-1].append(int(i))
    ring_r = [float(r_frac[ring].mean()) for ring in rings]
    print(
        f"{len(anchor_ids)} flower anchors in {len(rings)} rings @ r ~ "
        + ", ".join(f"{r:.2f}" for r in ring_r)
    )

    # --- group into same-KIND waves ----------------------------------------
    # Owner's wave criteria (2026-06-11): one wave = ONE kind of shape —
    # midpoints equidistant from the validated center, same/rotated copies of
    # one another, similar area, same palette color. Rotation-invariance via
    # normalized central-moment invariants (phi1 + an eccentricity proxy), so
    # a petal and its 36°-rotated sibling group together while an equal-area
    # star does not. Kinds are connected components of the pairwise
    # "similar on all four criteria" graph over real shapes.
    Y, X = np.indices(tiles.shape)
    sx = ndimage.sum_labels(X, labels, idx)
    sy = ndimage.sum_labels(Y, labels, idx)
    sxx = ndimage.sum_labels(X * X, labels, idx)
    syy = ndimage.sum_labels(Y * Y, labels, idx)
    sxy = ndimage.sum_labels(X * Y, labels, idx)
    mu20 = sxx - sx**2 / areas
    mu02 = syy - sy**2 / areas
    mu11 = sxy - sx * sy / areas
    phi1 = (mu20 + mu02) / areas**2  # rotation-invariant "spread"
    ecc = np.sqrt((mu20 - mu02) ** 2 + 4 * mu11**2) / (mu20 + mu02)  # 0=round
    color_names = [ar.nearest_anchor(tuple(c)) for c in mean_rgb]

    # COLOR_TOL compares mean RGB directly — palette NAMES flicker for shapes
    # near a cluster boundary (witnessed: one kind of 10 split 4 "turquoise" /
    # 6 "cyan" by jpg jitter), while raw RGB distance stays small within a
    # kind (~40) and large across families (navy-royal ~110).
    R_TOL, AREA_RATIO, PHI1_REL, ECC_ABS, COLOR_TOL = 0.04, 1.3, 0.25, 0.2, 60.0
    rid = np.nonzero(real)[0]
    rgb_d = np.linalg.norm(mean_rgb[rid][:, None] - mean_rgb[rid][None, :], axis=2)
    same = (
        (rgb_d < COLOR_TOL)
        & (np.abs(r_frac[rid][:, None] - r_frac[rid][None, :]) < R_TOL)
        & (
            np.maximum(areas[rid][:, None], areas[rid][None, :])
            < AREA_RATIO * np.minimum(areas[rid][:, None], areas[rid][None, :])
        )
        & (
            np.abs(phi1[rid][:, None] - phi1[rid][None, :])
            < PHI1_REL * np.maximum(phi1[rid][:, None], phi1[rid][None, :])
        )
        & (np.abs(ecc[rid][:, None] - ecc[rid][None, :]) < ECC_ABS)
    )
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import connected_components

    n_kinds, kind_lbl = connected_components(csr_matrix(same), directed=False)
    kind_members = [rid[kind_lbl == k] for k in range(n_kinds)]
    # Order: inside-out by mean radius, biggest shapes first on ties.
    order = sorted(
        range(n_kinds),
        key=lambda k: (
            round(float(r_frac[kind_members[k]].mean()), 2),
            -float(areas[kind_members[k]].mean()),
        ),
    )
    wave_of = np.full(n, -1)
    for w, k in enumerate(order):
        wave_of[kind_members[k]] = w
    # Fragments inherit the nearest real shape's wave (exhaustiveness: every
    # tile pixel stays in some wave; fragments are jpg slivers, not shapes).
    frag = np.nonzero(~real)[0]
    if len(frag):
        d2f = (cxs[frag][:, None] - cxs[rid][None, :]) ** 2 + (
            cys[frag][:, None] - cys[rid][None, :]
        ) ** 2
        wave_of[frag] = wave_of[rid[np.argmin(d2f, axis=1)]]
    n_waves = n_kinds
    print(f"{n_waves} same-kind waves; counts: "
          + ", ".join(str(len(kind_members[k])) for k in order))

    # --- group kinds into composite flowers (motifs) -------------------------
    # Owner (2026-06-11): "there is a shape similar to our middle one that
    # revolves around the origin — a mix of several waves." A MOTIF is that
    # composite: one flower (an anchor star plus the kinds dressing it),
    # repeated fold times around the center — the DSL-native unit (build the
    # flower once, rotate fold). Each anchor ring seeds one family; a wave
    # joins the family the majority of its members sit nearest to (euclidean
    # to anchor centroids). Within a family a shape belongs to the INSTANCE
    # whose anchor is nearest BY ANGLE — euclidean instance assignment
    # mis-seats shapes at angular boundaries (witnessed: 10-member waves
    # splitting [1,..,1,2,2] over 9 instances). Validation, the composite
    # analog of the fold-count check: every instance of a family must hold
    # the same wave-multiset.
    a_idx = np.array([i for ring in rings for i in ring])
    a_fam = np.array([f for f, ring in enumerate(rings) for _ in ring])
    d2a = (cxs[:, None] - cxs[a_idx][None, :]) ** 2 + (
        cys[:, None] - cys[a_idx][None, :]
    ) ** 2
    fam_vote = a_fam[np.argmin(d2a, axis=1)]
    wave_fam = np.zeros(n_waves, dtype=int)
    for w in range(n_waves):
        vals, cnts = np.unique(fam_vote[kind_members[order[w]]], return_counts=True)
        wave_fam[w] = int(vals[np.argmax(cnts)])
    for ov in args.seat:
        wv, fm = (int(t) for t in ov.split("="))
        wave_fam[wv - 1] = fm - 1
    fam_of = wave_fam[wave_of]
    inst_of = np.zeros(n, dtype=int)
    for f, ring in enumerate(rings):
        if len(ring) < 2:
            continue
        ang = theta[np.array(sorted(ring, key=lambda i: theta[i]))]
        n_inst = len(ring)
        sel = np.nonzero(fam_of == f)[0]
        for w in np.unique(wave_of[sel]):
            mem = sel[(wave_of[sel] == w)]
            mem_real = mem[real[mem]]
            mem_frag = mem[~real[mem]]
            mem_real = mem_real[np.argsort(theta[mem_real])]
            k, rem = divmod(len(mem_real), n_inst)
            if k == 0 or rem:
                # Not fold-divisible (lost slivers): honest per-member
                # nearest-anchor; the multiset check reports the deviation.
                if len(mem_real):
                    dd = np.abs(theta[mem_real][:, None] - ang[None, :])
                    inst_of[mem_real] = np.minimum(dd, 360 - dd).argmin(axis=1)
            else:
                # Fold-divisible kinds: consecutive-by-angle chunks of k ARE
                # the instances; pick the circular split + anchor alignment
                # with least total angular distance. Per-member nearest-anchor
                # coin-flips for kinds sitting exactly BETWEEN two flowers
                # (witnessed: 18deg-offset waves splitting [1,..,1,2,2] over
                # 9 instances); chunking is deterministic and even.
                ts = theta[mem_real]
                best_s, best_j0, best_cost = 0, 0, np.inf
                for s in range(k):
                    rolled = np.roll(ts, -s).copy()
                    wrap = np.nonzero(np.diff(rolled) < 0)[0]
                    if len(wrap):
                        rolled[wrap[0] + 1 :] += 360
                    gm = rolled.reshape(n_inst, k).mean(axis=1) % 360
                    dd = np.abs(gm[:, None] - ang[None, :])
                    dd = np.minimum(dd, 360 - dd)
                    j0 = int(dd[0].argmin())
                    cost = sum(dd[g, (j0 + g) % n_inst] for g in range(n_inst))
                    if cost < best_cost:
                        best_s, best_j0, best_cost = s, j0, cost
                for g in range(n_inst):
                    for t in range(k):
                        mi = mem_real[(best_s + g * k + t) % len(mem_real)]
                        inst_of[mi] = (best_j0 + g) % n_inst
            if len(mem_frag):
                dd = np.abs(theta[mem_frag][:, None] - ang[None, :])
                inst_of[mem_frag] = np.minimum(dd, 360 - dd).argmin(axis=1)

    multi = [f for f, ring in enumerate(rings) if len(ring) > 1]
    motif_names = []
    for f, ring in enumerate(rings):
        if len(ring) == 1:
            motif_names.append("the middle flower")
        elif len(multi) == 2:
            motif_names.append(
                "the inner flowers" if f == multi[0] else "the outer flowers"
            )
        else:
            motif_names.append(f"the flowers at ring {f + 1}")

    motifs = []
    for f, ring in enumerate(rings):
        n_inst = len(ring)
        M = np.zeros((n_inst, n_waves), dtype=int)
        sel = np.nonzero((fam_of == f) & real)[0]
        np.add.at(M, (inst_of[sel], wave_of[sel]), 1)
        # Reference composition = per-wave mode across instances, so a single
        # lost sliver (wave of 39, not 40) reads as a deviation, not the norm.
        ref = np.array(
            [np.bincount(M[:, w]).argmax() for w in range(n_waves)], dtype=int
        )
        deviations = int(np.abs(M - ref).sum())
        motifs.append(
            {
                "motif": f + 1,
                "name": motif_names[f],
                "n_instances": n_inst,
                "anchor_r_frac": round(ring_r[f], 3),
                "waves": {str(w + 1): int(ref[w]) for w in range(n_waves) if ref[w]},
                "shapes_per_instance": int(ref.sum()),
                "instances_identical": deviations == 0,
                "deviations": deviations,
            }
        )
        parts = " + ".join(f"{ref[w]}x w{w + 1}" for w in range(n_waves) if ref[w])
        flag = (
            "all instances identical"
            if deviations == 0
            else f"{deviations} shape(s) deviate (lost slivers / seat noise)"
        )
        print(
            f"flower {f + 1} ({motif_names[f]}, x{n_inst}): "
            f"{int(ref.sum())} shapes per flower = {parts} — {flag}"
        )

    def where_label(r: float) -> str:
        k = int(np.argmin([abs(r - rr) for rr in ring_r]))
        if k == 0 and len(rings[0]) == 1:
            return "in the middle flower"
        if k == len(rings) - 1:
            return "at the outer edge"
        return "in the middle ring"

    total_area = float(areas.sum())
    waves = []
    for w in range(n_waves):
        sel = wave_of == w
        members = kind_members[order[w]]
        shapes = [
            {
                "id": int(i + 1),
                "x": round(float(cxs[i]), 1),
                "y": round(float(cys[i]), 1),
                "r_frac": round(float(r_frac[i]), 3),
                "theta_deg": round(float(theta[i]), 1),
                "area_px": int(areas[i]),
                "fragment": bool(areas[i] < FRAGMENT_AREA),
                "color": color_names[i],
                "hex": ar.hexc(mean_rgb[i]),
            }
            for i in np.nonzero(sel)[0]
        ]
        kr = float(r_frac[members].mean())
        waves.append(
            {
                "wave": w + 1,
                "color": color_names[members[0]],
                "where": where_label(kr),
                "flower": int(wave_fam[w] + 1),
                "kind_r_frac": round(kr, 3),
                "mean_area_px": int(areas[members].mean()),
                "r_frac_range": [
                    round(float(r_frac[sel].min()), 3),
                    round(float(r_frac[sel].max()), 3),
                ],
                "shape_count": int(sel.sum()),
                "real_shape_count": int(len(members)),
                "area_share": round(float(areas[sel].sum()) / total_area, 4),
                "shapes": shapes,
            }
        )

    out_dir = args.session_dir / "input" / "reference-analysis" / "wave-plan"
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- visuals: dimmed grayscale base, full-color current wave -------------
    gray = np.asarray(img.convert("L"), dtype=float)
    dim = (255 - (255 - gray) * 0.18).astype(np.uint8)
    dim_rgb = np.stack([dim] * 3, axis=2)

    for w in range(n_waves):
        frame = dim_rgb.copy()
        sel_mask = np.isin(labels, idx[wave_of == w])
        frame[sel_mask] = a[sel_mask]
        Image.fromarray(frame).save(out_dir / f"wave-{w + 1}.png")

    wave_map = dim_rgb.copy()
    for w in range(n_waves):
        tint = tuple(int(WAVE_COLORS[w % len(WAVE_COLORS)][j : j + 2], 16) for j in (1, 3, 5))
        sel_mask = np.isin(labels, idx[wave_of == w])
        wave_map[sel_mask] = tint
    Image.fromarray(wave_map).save(out_dir / "waves-map.png")

    # Flower frames: ONE instance full color, its rotated twins half-bright
    # (so the eye can confirm "same flower, turned"), everything else pale.
    for f in range(len(rings)):
        frame = dim_rgb.copy()
        sib = np.isin(labels, idx[(fam_of == f) & (inst_of != 0)])
        frame[sib] = (0.55 * a[sib] + 0.45 * frame[sib]).astype(np.uint8)
        bright = np.isin(labels, idx[(fam_of == f) & (inst_of == 0)])
        frame[bright] = a[bright]
        Image.fromarray(frame).save(out_dir / f"flower-{f + 1}.png")

    flower_map = dim_rgb.copy()
    for f in range(len(rings)):
        tint = tuple(int(WAVE_COLORS[f % len(WAVE_COLORS)][j : j + 2], 16) for j in (1, 3, 5))
        sel_mask = np.isin(labels, idx[fam_of == f])
        flower_map[sel_mask] = tint
    Image.fromarray(flower_map).save(out_dir / "flowers-map.png")

    coverage = float(areas.sum()) / float(tiles.sum())
    plan = {
        "source": str(args.reference),
        "tool": "tools/plan-waves.py",
        "center": {"x": cx, "y": cy},
        "diameter_px": args.diameter,
        "n_waves": n_waves,
        "total_shapes": int(n),
        "real_shapes": int(real.sum()),
        "fragment_shapes": int((~real).sum()),
        "coverage_of_tile_area": round(coverage, 4),
        "agreed": False,
        "seat_overrides": list(args.seat),
        "motifs": motifs,
        "waves": [{k: v for k, v in w.items() if k != "shapes"} for w in waves],
    }
    (out_dir / "wave-plan.json").write_text(
        json.dumps({**plan, "waves": waves}, indent=2)
    )
    print(
        f"coverage: {coverage:.1%} of colored-tile pixels assigned; "
        f"{plan['real_shapes']} shapes + {plan['fragment_shapes']} fragments"
    )

    # --- the flip-through planning experience (plain language, Tenet 27) -----
    # Two levels: composite flowers first (the big picture), then the waves
    # (one kind at a time). All buttons drive one unified view list.
    views = []
    for m in motifs:
        nm = m["name"]
        if m["n_instances"] > 1:
            cap = (
                f"{nm.capitalize()} — one whole flower made of "
                f"{m['shapes_per_instance']} shapes (from {len(m['waves'])} waves), "
                f"repeated {m['n_instances']} times around the center. The bright "
                f"one is a single flower; its paler twins are the same flower, "
                f"turned. We build it once and spin it."
            )
        else:
            cap = (
                f"{nm.capitalize()} — {m['shapes_per_instance']} shapes "
                f"(from {len(m['waves'])} waves) around the very center. "
                f"This is where we start."
            )
        views.append(
            {
                "label": f"Flower {chr(64 + m['motif'])}"
                + (f" (x{m['n_instances']})" if m["n_instances"] > 1 else ""),
                "src": f"flower-{m['motif']}.png",
                "cap": cap,
            }
        )
    views.append(
        {
            "label": "All flowers (map)",
            "src": "flowers-map.png",
            "cap": "Every shape tinted by its flower group — "
            + ", ".join(
                f"{['red', 'yellow', 'green', 'blue', 'purple', 'teal'][(m['motif'] - 1) % 6]} is {m['name']}"
                for m in motifs
            )
            + ".",
        }
    )
    n_flower_views = len(views)
    for w in waves:
        views.append(
            {
                "label": f"Wave {w['wave']}",
                "src": f"wave-{w['wave']}.png",
                "cap": f"Wave {w['wave']} — {w['real_shape_count']} "
                f"{FRIENDLY.get(w['color'], w['color'])} shapes, all the same kind, "
                f"{w['where']} ({w['area_share']:.0%} of the pattern). "
                + (
                    "We copy these first."
                    if w["wave"] == 1
                    else ("We copy these last." if w["wave"] == n_waves else "")
                ),
            }
        )
    views.append(
        {
            "label": "All waves (map)",
            "src": "waves-map.png",
            "cap": "Every wave at once — each color is one wave, "
            "middle (red) first, edge last.",
        }
    )
    flower_buttons = "".join(
        f'<button onclick="show({i})" id="v{i}">{v["label"]}</button>'
        for i, v in enumerate(views[:n_flower_views])
    )
    wave_buttons = "".join(
        f'<button onclick="show({i})" id="v{i}">{v["label"]}</button>'
        for i, v in enumerate(views[n_flower_views:], start=n_flower_views)
    )
    views_js = json.dumps([{"src": v["src"], "cap": v["cap"]} for v in views])
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>The plan: copy the pattern in waves</title>
<style>
 body {{ font-family: -apple-system, sans-serif; margin: 0; background: #f5f3ee; color: #222; }}
 header {{ padding: 14px 20px; background: #fff; border-bottom: 1px solid #ddd; }}
 h1 {{ font-size: 20px; margin: 0 0 6px; }} p {{ margin: 4px 0; }}
 #caption {{ font-size: 17px; }} .muted {{ color: #666; font-size: 14px; }}
 .controls {{ padding: 6px 20px; display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }}
 .rowlabel {{ font-size: 14px; color: #666; min-width: 60px; }}
 button {{ font-size: 16px; padding: 8px 16px; border-radius: 8px; border: 1px solid #999;
          background: #fff; cursor: pointer; }}
 button.on {{ background: #1b6ca8; color: #fff; border-color: #1b6ca8; }}
 img {{ display: block; margin: 0 20px 20px; max-width: calc(100% - 40px); }}
</style></head><body>
<header>
 <h1>The plan: a few flowers, copied in waves, middle first</h1>
 <p id="caption"></p>
 <p class="muted">The whole pattern is a few FLOWERS — composite shapes that
   repeat around the center — and every flower is built from WAVES, where one
   wave is one kind of simple shape. {plan['real_shapes']} shapes,
   {coverage:.0%} of the colored area covered; every shape belongs to exactly
   one wave and one flower. Bright shapes are what's being shown; pale ones
   come later. If anything looks wrong (a shape in the wrong group, a flower
   missing a petal), say so — we don't start building until you agree.</p>
</header>
<div class="controls"><span class="rowlabel">Flowers:</span>{flower_buttons}</div>
<div class="controls"><span class="rowlabel">Waves:</span>{wave_buttons}</div>
<img id="view" src="{views[0]['src']}">
<script>
 const views = {views_js};
 function show(i) {{
   document.querySelectorAll('button').forEach(b => b.classList.remove('on'));
   document.getElementById('v' + i).classList.add('on');
   document.getElementById('view').src = views[i].src;
   document.getElementById('caption').textContent = views[i].cap;
 }}
 show(0);
</script></body></html>
"""
    (out_dir / "wave-plan.html").write_text(html)
    print(
        f"wrote {out_dir}/wave-plan.html (+ {n_waves} wave PNGs, "
        f"{len(rings)} flower PNGs, waves-map.png, flowers-map.png, wave-plan.json)"
    )


if __name__ == "__main__":
    main()
