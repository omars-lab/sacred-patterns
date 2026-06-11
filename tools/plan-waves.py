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
    wave-<k>.png     wave k in full color over a dimmed grayscale reference,
                     with the wave's ring dashed through its midpoints
    waves-map.png    every shape tinted by its wave (distinct colors, Tenet 24)
    flower-<f>.png   composite flower f: the repeated unit ringed in gold,
                     a dotted orbit through its rotated twins (half-bright),
                     everything else pale — build once, spin fold times
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
from PIL import Image, ImageDraw
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


def friendly(color: str) -> str:
    """Palette anchor names are engineer tokens; the page speaks plain words
    (Tenet 27). Map the known ones, humanize the rest — e.g.
    friendly("navy") -> "dark-blue", friendly("deep_navy") -> "deep navy"."""
    return FRIENDLY.get(color, color.replace("_", " "))


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
    ap.add_argument(
        "--overrides",
        type=Path,
        default=None,
        help="wave-plan-overrides.json saved from the wave-plan studio "
        "({shape_waves: {id: wave}, shape_flowers: {id: flower}, wave_flowers:"
        " {wave: flower}, wave_merges: {wave: wave}}, all 1-based, flower 0 = "
        "no flower). When omitted, <out>/wave-plan-overrides.json is "
        "auto-loaded if present, so the owner's saved fixes survive re-runs.",
    )
    args = ap.parse_args()

    tools_dir = Path(__file__).resolve().parent
    ar = load_analyze_reference(tools_dir)

    out_dir = args.session_dir / "input" / "reference-analysis" / "wave-plan"
    ov_path = args.overrides or (out_dir / "wave-plan-overrides.json")
    overrides: dict = {}
    if ov_path.exists():
        overrides = json.loads(ov_path.read_text())
        print(
            f"applying owner fixes from {ov_path}: "
            f"{len(overrides.get('shape_waves', {}))} shape move(s), "
            f"{len(overrides.get('wave_merges', {}))} wave merge(s), "
            f"{len(overrides.get('wave_flowers', {}))} wave re-seat(s)"
        )

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

    # Owner shape moves (from the page's "Fix the groups" mode) land HERE —
    # before flower seating, instance splitting, validation, and visuals — so
    # one saved overrides file flows through every downstream artifact.
    # Merges first, single-shape moves second: a shape-level move must win
    # over its wave's merge (the owner singled that shape out).
    for src, dst in overrides.get("wave_merges", {}).items():
        wave_of[wave_of == int(src) - 1] = int(dst) - 1
    for sid, wv in overrides.get("shape_waves", {}).items():
        wave_of[int(sid) - 1] = int(wv) - 1
    # Per-wave real membership recomputed AFTER the moves; every consumer
    # below (family vote, JSON stats) reads this, never kind_members again.
    wave_members = [np.nonzero((wave_of == w) & real)[0] for w in range(n_waves)]

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
        if not len(wave_members[w]):
            continue  # wave emptied by owner moves; its shapes live elsewhere
        vals, cnts = np.unique(fam_vote[wave_members[w]], return_counts=True)
        wave_fam[w] = int(vals[np.argmax(cnts)])
    for ov in args.seat:
        wv, fm = (int(t) for t in ov.split("="))
        wave_fam[wv - 1] = fm - 1
    for wv, fm in overrides.get("wave_flowers", {}).items():
        wave_fam[int(wv) - 1] = int(fm) - 1  # 0 -> -1 = taken out of any flower
    fam_of = wave_fam[wave_of]
    # Per-shape flower fixes ride on TOP of the wave's seat: the owner can pull
    # one shape out of a flower (0) or force it into one without moving its
    # wave (the "remove from flower" button on the inspector panel).
    for sid, fm in overrides.get("shape_flowers", {}).items():
        fam_of[int(sid) - 1] = int(fm) - 1
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
        members = wave_members[w]
        if not len(members):
            continue  # emptied by owner moves — nothing left to plan here
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

    out_dir.mkdir(parents=True, exist_ok=True)

    # --- visuals: dimmed grayscale base, full-color current wave -------------
    gray = np.asarray(img.convert("L"), dtype=float)
    dim = (255 - (255 - gray) * 0.18).astype(np.uint8)
    dim_rgb = np.stack([dim] * 3, axis=2)

    def dash_circle(draw, radius):
        # Gold dashes over a white halo, centered on the validated center —
        # the one visual vocabulary for "this is a ring around the middle"
        # (used by both the wave rings and the flower orbit). The halo keeps
        # the dashes readable on the pale background AND on navy tiles.
        box = [cx - radius, cy - radius, cx + radius, cy + radius]
        for adeg in range(0, 360, 8):
            draw.arc(box, adeg, adeg + 4, fill=(255, 255, 255), width=6)
        for adeg in range(0, 360, 8):
            draw.arc(box, adeg, adeg + 4, fill=(193, 128, 10), width=3)

    # A wave IS a ring — midpoints equidistant from the center is the
    # grouping rule, so draw that circle through the members' midpoints
    # (owner ask 2026-06-11: "when we see a wave, why don't we see a circle
    # going through the midpoint of all shapes in the wave"). The center
    # wave (single shape at radius ~0) gets no ring.
    wave_ringed = []
    for w in range(n_waves):
        frame = dim_rgb.copy()
        sel_mask = np.isin(labels, idx[wave_of == w])
        frame[sel_mask] = a[sel_mask]
        im = Image.fromarray(frame)
        mem = (wave_of == w) & real
        orad = float(np.hypot(cxs[mem] - cx, cys[mem] - cy).mean()) if mem.any() else 0.0
        if orad > 15:
            dash_circle(ImageDraw.Draw(im), orad)
        wave_ringed.append(orad > 15)
        im.save(out_dir / f"wave-{w + 1}.png")

    wave_map = dim_rgb.copy()
    for w in range(n_waves):
        tint = tuple(int(WAVE_COLORS[w % len(WAVE_COLORS)][j : j + 2], 16) for j in (1, 3, 5))
        sel_mask = np.isin(labels, idx[wave_of == w])
        wave_map[sel_mask] = tint
    Image.fromarray(wave_map).save(out_dir / "waves-map.png")

    # Flower frames: ONE instance full color, its rotated twins half-bright
    # (so the eye can confirm "same flower, turned"), everything else pale.
    # The repeated unit is CALLED OUT explicitly, not just brighter (owner
    # 2026-06-11: "per flower, are we highlighting the main repeated
    # pattern? ... that is repeated across origin?"): a gold ring circles
    # the one flower we build, and a dotted orbit through the twins' centers
    # shows the path it is turned along — build once, spin fold times.
    for f in range(len(rings)):
        frame = dim_rgb.copy()
        sib = np.isin(labels, idx[(fam_of == f) & (inst_of != 0)])
        frame[sib] = (0.55 * a[sib] + 0.45 * frame[sib]).astype(np.uint8)
        bright = np.isin(labels, idx[(fam_of == f) & (inst_of == 0)])
        frame[bright] = a[bright]
        im = Image.fromarray(frame)
        n_inst = motifs[f]["n_instances"] if f < len(motifs) else 1
        if n_inst > 1:
            d = ImageDraw.Draw(im)
            inst_cx, inst_cy = [], []
            for i in range(n_inst):
                m = (fam_of == f) & (inst_of == i)
                if not m.any():
                    continue
                wts = areas[m]
                inst_cx.append(float((cxs[m] * wts).sum() / wts.sum()))
                inst_cy.append(float((cys[m] * wts).sum() / wts.sum()))
            # Dotted orbit first (under the ring): circle through the
            # instance centers — the path the gold-ringed unit turns along.
            orad = float(np.mean(np.hypot(np.array(inst_cx) - cx, np.array(inst_cy) - cy)))
            dash_circle(d, orad)
            # Gold ring around the unit we build — big enough to cover its
            # farthest member shape (centroid distance + that shape's own
            # radius from its area) plus a little breathing room.
            m0 = (fam_of == f) & (inst_of == 0)
            rr = float(np.max(
                np.hypot(cxs[m0] - inst_cx[0], cys[m0] - inst_cy[0])
                + np.sqrt(areas[m0] / np.pi)
            )) + 6
            d.ellipse(
                [inst_cx[0] - rr, inst_cy[0] - rr, inst_cx[0] + rr, inst_cy[0] + rr],
                outline=(212, 146, 10), width=4,
            )
        im.save(out_dir / f"flower-{f + 1}.png")

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
        "owner_fixes_applied": overrides if overrides else None,
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
                f"{m['shapes_per_instance']} shapes (from {len(m['waves'])} waves). "
                f"The gold ring marks the one we build; the dotted circle is the "
                f"path it repeats along — the same flower, turned around the "
                f"center {m['n_instances']} times. Build once, spin {m['n_instances']} times."
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
                f"{friendly(w['color'])} "
                + (
                    "shapes, all the same kind, "
                    if w["real_shape_count"] != 1
                    else "shape "
                )
                + f"{w['where']} ({w['area_share']:.0%} of the pattern). "
                + (
                    "The dotted ring runs through all their midpoints — "
                    "that ring is the wave. "
                    if wave_ringed[w["wave"] - 1]
                    else ""
                )
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
    # The inspector ("click any shape") needs every shape's centroid + current
    # group client-side so a click can hit-test the nearest shape and show its
    # wave + flower with fix actions. Fixes accumulate as an overrides object
    # ({shape_waves, shape_flowers, wave_flowers}); served by
    # wave-plan-server.py they POST back and this tool re-runs with them, so
    # the owner's corrections survive every regeneration.
    img_w, img_h = img.size
    shapes_js = json.dumps(
        [
            {"id": s["id"], "x": s["x"], "y": s["y"], "a": s["area_px"],
             "w": wv["wave"], "c": friendly(s["color"])}
            for wv in waves
            for s in wv["shapes"]
        ]
    )
    wave_info_js = json.dumps(
        {
            str(wv["wave"]): {
                "flower": wv["flower"],
                "count": wv["real_shape_count"],
                "color": friendly(wv["color"]),
                "where": wv["where"],
                "view": n_flower_views + i,
            }
            for i, wv in enumerate(waves)
        }
    )
    flowers_js = json.dumps(
        [
            {"motif": m["motif"], "name": m["name"], "n": m["n_instances"],
             "view": m["motif"] - 1}
            for m in motifs
        ]
    )
    applied_js = json.dumps(overrides if overrides else {})
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>The plan: copy the pattern in waves</title>
<style>
 /* One design system, shared with the hub + palette pages (wave-plan-server.py
    HUB_CSS mirrors these tokens): warm-paper gallery look, serif display voice,
    ONE button system (uniform height, inline-flex centering) so rows align. */
 :root {{
   --paper: #F6F3EC; --card: #FFFFFF; --ink: #202A36; --muted: #7A746A;
   --line: #E4DFD3; --accent: #19599C; --accent-soft: #EAF1F8;
   --apply: #D4501E; --agree: #1F7A45;
   --shadow: 0 1px 2px rgba(32,42,54,.05), 0 10px 28px rgba(32,42,54,.08);
   --serif: Charter, 'Iowan Old Style', Georgia, serif;
 }}
 * {{ box-sizing: border-box; }}
 body {{ font-family: 'Avenir Next', Seravek, 'Helvetica Neue', -apple-system, sans-serif;
        margin: 0; background: var(--paper); color: var(--ink);
        -webkit-font-smoothing: antialiased; }}
 header {{ padding: 18px 24px 12px; background: var(--card);
          border-bottom: 1px solid var(--line); }}
 h1 {{ font-family: var(--serif); font-weight: 600; font-size: 24px;
      letter-spacing: .1px; margin: 0 0 6px; }}
 p {{ margin: 4px 0; }}
 #caption {{ font-size: 16px; }}
 .muted {{ color: var(--muted); font-size: 13.5px; line-height: 1.55; }}
 .controls {{ padding: 8px 24px 0; display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }}
 .rowlabel {{ font-size: 11.5px; letter-spacing: .08em; text-transform: uppercase;
             color: var(--muted); min-width: 64px; }}
 button {{ font: inherit; font-size: 14px; font-weight: 500; color: var(--ink);
          display: inline-flex; align-items: center; justify-content: center;
          height: 32px; padding: 0 14px; border-radius: 999px;
          border: 1px solid var(--line); background: var(--card); cursor: pointer;
          transition: transform .15s ease, box-shadow .15s ease,
                      background .15s ease, border-color .15s ease; }}
 button:hover {{ border-color: var(--accent); box-shadow: var(--shadow);
                transform: translateY(-1px); }}
 button:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
 button:disabled {{ opacity: .55; cursor: default; transform: none; box-shadow: none; }}
 button.on {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
 button.act {{ height: 30px; padding: 0 12px; border-radius: 8px; font-size: 13.5px; }}
 #applybtn {{ background: var(--apply); color: #fff; border-color: var(--apply); font-weight: 600; }}
 #agreebtn {{ background: var(--agree); color: #fff; border-color: var(--agree); font-weight: 600; }}
 #fixhint {{ font-size: 14px; color: #8a3c00; }}
 #fixlist {{ padding: 6px 24px 0; font-size: 13.5px; }}
 #fixlist .fix {{ display: inline-flex; align-items: center; gap: 6px;
                 background: var(--accent-soft); border: 1px solid var(--line);
                 border-radius: 999px; padding: 3px 11px; margin: 2px 6px 2px 0; }}
 #fixlist a {{ color: var(--accent); }}
 #main {{ display: flex; align-items: flex-start; gap: 18px; padding: 10px 24px 24px; }}
 /* The marks overlay (inset:0) and the image must share ONE box, or every
    selection ring lands offset from its shape: width 100% makes the image
    fill the wrapper so the absolute SVG maps 1:1 onto the pixels. The
    wrapper width is capped so the WHOLE picture fits the window height
    (owner, 2026-06-11: full-width image ate the screen) — the cap is the
    viewport height times the image's aspect ratio. */
 #imgwrap {{ position: relative; flex: 0 1 auto; min-width: 0; cursor: pointer;
            margin: 0 auto;
            width: min(100%, calc((100vh - 250px) * {img_w / img_h:.4f}));
            border-radius: 14px; overflow: hidden; box-shadow: var(--shadow); }}
 #imgwrap img {{ display: block; width: 100%; height: auto; }}
 #marks {{ position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }}
 #panel {{ flex: 0 0 340px; position: sticky; top: 12px; background: var(--card);
          border: 1px solid var(--line); border-radius: 14px; padding: 16px 18px;
          box-shadow: var(--shadow); font-size: 14.5px; }}
 #panel h3 {{ margin: 0 0 2px; font-family: var(--serif); font-size: 19px; }}
 #panel .sec {{ margin: 12px 0 0; padding-top: 12px; border-top: 1px solid var(--line); }}
 #panel .seclabel {{ font-size: 11.5px; letter-spacing: .08em; text-transform: uppercase;
                    color: var(--muted); margin: 0 0 4px; }}
 #panel .row {{ margin: 8px 0; }}
 #panel select {{ font: inherit; font-size: 13.5px; width: 100%; height: 32px;
                 padding: 0 8px; margin: 4px 0 8px; border: 1px solid var(--line);
                 border-radius: 8px; background: var(--card); color: var(--ink); }}
 #panel .btns {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 0 0 4px; }}
 #panel a {{ color: var(--accent); }}
</style></head><body>
<header>
 <h1>The plan: a few flowers, copied in waves, middle first</h1>
 <p id="caption"></p>
 <p class="muted">The whole pattern is a few FLOWERS — composite shapes that
   repeat around the center — and every flower is built from WAVES, where one
   wave is one kind of simple shape. {plan['real_shapes']} shapes,
   {coverage:.0%} of the colored area covered; every shape belongs to exactly
   one wave and one flower. <b>Click any shape on the picture</b> to see its
   groups and fix them — we don't start building until you agree.
   <a href="/" id="hublink" hidden>&larr; Back to your review list</a></p>
</header>
<div class="controls"><span class="rowlabel">Flowers:</span>{flower_buttons}</div>
<div class="controls"><span class="rowlabel">Waves:</span>{wave_buttons}<span class="muted">&larr; &rarr; keys flip through</span></div>
<div class="controls"><span class="rowlabel"></span>
 <button id="applybtn" style="display:none"></button>
 <button id="agreebtn" style="display:none">The plan looks right — start building</button>
 <span id="fixhint"></span></div>
<div id="fixlist" class="muted"></div>
<div id="main">
 <div id="imgwrap"><img id="view" src="{views[0]['src']}">
  <svg id="marks" viewBox="0 0 {img_w} {img_h}" preserveAspectRatio="none"></svg></div>
 <div id="panel" hidden>
  <h3 id="p-title"></h3>
  <p id="p-desc" class="muted"></p>
  <p class="row" id="p-wave"></p>
  <p class="row" id="p-flower"></p>
  <div class="sec"><p class="seclabel">Fix its wave</p>
   <select id="selwave"></select>
   <div class="btns">
    <button class="act" id="btn-wave-shape">Move shape</button>
    <button class="act" id="btn-wave-wave">Move wave</button></div>
   <p class="muted">Pick a wave — its shapes light up yellow on the picture. "Move wave" merges its whole wave — everything like it — into the one you picked.</p></div>
  <div class="sec"><p class="seclabel">Fix its flower</p>
   <select id="selflower"></select>
   <div class="btns">
    <button class="act" id="btn-flower-shape">Move shape</button>
    <button class="act" id="btn-flower-wave">Move wave</button></div>
   <div class="btns">
    <button class="act" id="btn-noflower">Take shape out</button>
    <button class="act" id="btn-noflower-wave">Take wave out</button></div>
   <p class="muted">Pick a flower — its shapes light up yellow. "Take out" leaves it on its own, outside any flower.</p></div>
  <div class="sec btns" style="border-top:none;padding-top:8px"><button class="act" id="btn-close">Close</button></div>
 </div>
</div>
<script>
 const views = {views_js};
 let currentView = 0;
 function show(i) {{
   currentView = i;
   document.querySelectorAll('[id^="v"].on').forEach(b => b.classList.remove('on'));
   const btn = document.getElementById('v' + i);
   if (btn) btn.classList.add('on');
   document.getElementById('view').src = views[i].src;
   document.getElementById('caption').textContent = views[i].cap;
 }}
 show(0);
 // Arrow keys flip to the next/previous view (owner ask 2026-06-11) —
 // wrap-around, and hands off when focus is in a dropdown/field so the
 // arrows keep their native meaning there. A just-clicked view button can
 // keep focus: keydown still bubbles to document, so flipping works.
 document.addEventListener('keydown', (e) => {{
   if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
   const t = document.activeElement ? document.activeElement.tagName : '';
   if (t === 'SELECT' || t === 'INPUT' || t === 'TEXTAREA') return;
   e.preventDefault();
   const n = views.length;
   show((currentView + (e.key === 'ArrowRight' ? 1 : n - 1)) % n);
 }});
</script>
<script>__EDIT_JS__</script></body></html>
"""
    edit_js = """
 const shapes = __SHAPES__;
 const waveInfo = __WAVE_INFO__;
 const flowers = __FLOWERS__;
 const IMG_W = __IMG_W__, IMG_H = __IMG_H__;
 // Served over http (wave-plan-server.py): fixes POST back and the plan
 // regenerates server-side. Opened as a file: fixes download as JSON instead.
 const SERVER = location.protocol.startsWith('http');
 const applied = __APPLIED__;
 const fixes = {
   shape_waves: Object.assign({}, applied.shape_waves || {}),
   shape_flowers: Object.assign({}, applied.shape_flowers || {}),
   wave_flowers: Object.assign({}, applied.wave_flowers || {}),
   wave_merges: Object.assign({}, applied.wave_merges || {}),
 };
 let sel = null;
 const $ = id => document.getElementById(id);
 const fl = n => String.fromCharCode(64 + n);
 // A shape's own move wins; otherwise its whole wave may have been merged.
 const waveOf = s => fixes.shape_waves[s.id] ?? fixes.wave_merges[s.w] ?? s.w;
 const flowerOfWave = w => fixes.wave_flowers[w] ?? (waveInfo[w] ? waveInfo[w].flower : 0);
 const flowerOfShape = s => fixes.shape_flowers[s.id] ?? flowerOfWave(waveOf(s));
 const flowerLabel = f => f ? 'Flower ' + fl(f) + ' — ' + flowers[f - 1].name : 'no flower (on its own)';
 const dirty = () => JSON.stringify(fixes) !== JSON.stringify({
   shape_waves: applied.shape_waves || {},
   shape_flowers: applied.shape_flowers || {},
   wave_flowers: applied.wave_flowers || {},
   wave_merges: applied.wave_merges || {},
 });
 function setHint(t) { $('fixhint').textContent = t; }
 // Which group is the dropdown pointing at, when it differs from the
 // selection's CURRENT group? That difference is what a Move/Merge would
 // change — so it's exactly what the yellow preview must show.
 function previewWave() {
   if (!sel) return null;
   const v = parseInt($('selwave').value, 10);
   return Number.isFinite(v) && v !== waveOf(sel) ? v : null;
 }
 function previewFlower() {
   if (!sel) return null;
   const v = parseInt($('selflower').value, 10);
   return Number.isFinite(v) && v !== flowerOfShape(sel) ? v : null;
 }
 function drawMarks() {
   let m = '';
   if (sel) {
     const w = waveOf(sel);
     // Yellow first (underneath): the destination group picked in a dropdown
     // — what pressing Move/Merge would combine the selection with.
     const pw = previewWave(), pf = previewFlower();
     const gold = s => '<circle cx="' + s.x + '" cy="' + s.y + '" r="9" fill="#F2B705" fill-opacity="0.9" stroke="#7A5C00" stroke-width="1.5"/>';
     if (pw !== null)
       for (const s of shapes)
         if (waveOf(s) === pw) m += gold(s);
     if (pf !== null && pf !== 0)
       for (const s of shapes)
         if (flowerOfShape(s) === pf && waveOf(s) !== pw) m += gold(s);
     for (const s of shapes)
       if (s.id !== sel.id && waveOf(s) === w)
         m += '<circle cx="' + s.x + '" cy="' + s.y + '" r="6" fill="#1b6ca8" fill-opacity="0.85"/>';
     m += '<circle cx="' + sel.x + '" cy="' + sel.y + '" r="15" fill="none" stroke="#E64A19" stroke-width="4"/>';
   }
   $('marks').innerHTML = m;
 }
 function options() {
   let ws = '';
   for (const w in waveInfo) {
     const i = waveInfo[w];
     ws += '<option value="' + w + '">Wave ' + w + ' — ' + i.count + ' ' + i.color + ' ' + (i.count === 1 ? 'shape ' : 'shapes ') + i.where + '</option>';
   }
   $('selwave').innerHTML = ws;
   let fs = '';
   for (const f of flowers)
     fs += '<option value="' + f.motif + '">Flower ' + fl(f.motif) + ' — ' + f.name + '</option>';
   fs += '<option value="0">No flower — keep it on its own</option>';
   $('selflower').innerHTML = fs;
 }
 function openPanel(s) {
   sel = s;
   const w = waveOf(s), f = flowerOfShape(s), wi = waveInfo[w];
   $('p-title').textContent = 'Shape #' + s.id;
   $('p-desc').textContent = 'A ' + s.c + ' shape. Blue dots = the other shapes in its wave. Pick a different group below and it lights up yellow.';
   $('p-wave').innerHTML = '<b>Its wave:</b> Wave ' + w + ' — ' + wi.count + ' ' + wi.color +
     (wi.count === 1 ? ' shape ' : ' shapes ') + wi.where + ' <a href="#" id="see-wave">see it</a>';
   $('p-flower').innerHTML = '<b>Its flower:</b> ' + flowerLabel(f) +
     (f && flowers[f - 1] ? ' <a href="#" id="see-flower">see it</a>' : '');
   $('see-wave').onclick = e => { e.preventDefault(); show(wi.view); };
   const sf = $('see-flower');
   if (sf) sf.onclick = e => { e.preventDefault(); show(flowers[f - 1].view); };
   $('selwave').value = String(w);
   $('selflower').value = String(f);
   $('panel').hidden = false;
   drawMarks();
 }
 function afterEdit(msg) {
   renderFixes();
   if (sel) openPanel(sel);
   setHint(msg);
 }
 function renderFixes() {
   const L = [];
   const chip = (txt, k, id) => L.push('<span class="fix">' + txt +
     ' <a href="#" data-k="' + k + '" data-id="' + id + '">undo</a></span>');
   for (const id in fixes.shape_waves)
     chip('shape #' + id + ' &rarr; wave ' + fixes.shape_waves[id], 'shape_waves', id);
   for (const id in fixes.shape_flowers)
     chip('shape #' + id + ' &rarr; ' + (fixes.shape_flowers[id] ? 'flower ' + fl(fixes.shape_flowers[id]) : 'no flower'),
       'shape_flowers', id);
   for (const w in fixes.wave_flowers)
     chip('wave ' + w + ' &rarr; ' + (fixes.wave_flowers[w] ? 'flower ' + fl(fixes.wave_flowers[w]) : 'no flower'),
       'wave_flowers', w);
   for (const w in fixes.wave_merges)
     chip('wave ' + w + ' merged into wave ' + fixes.wave_merges[w], 'wave_merges', w);
   $('fixlist').innerHTML = L.length ? '<span class="muted">Your fixes:</span> ' + L.join(' ') : '';
   const d = dirty();
   $('applybtn').style.display = d ? '' : 'none';
   $('applybtn').textContent = SERVER ? 'Apply my fixes and redraw the pictures' : 'Save my fixes';
 }
 $('fixlist').addEventListener('click', e => {
   const a = e.target.closest('a'); if (!a) return;
   e.preventDefault();
   delete fixes[a.dataset.k][a.dataset.id];
   afterEdit('Undone. (If it was already applied, press the apply button to redraw without it.)');
   drawMarks();
 });
 $('imgwrap').addEventListener('click', e => {
   const img = $('view'), r = img.getBoundingClientRect();
   const nx = (e.clientX - r.left) * IMG_W / r.width;
   const ny = (e.clientY - r.top) * IMG_H / r.height;
   let best = null, bd = Infinity;
   for (const s of shapes) {
     const d = Math.hypot(s.x - nx, s.y - ny);
     if (d < bd) { bd = d; best = s; }
   }
   if (!best || bd > Math.max(30, 2 * Math.sqrt(best.a / Math.PI))) return;
   openPanel(best);
 });
 $('btn-wave-shape').addEventListener('click', () => {
   if (!sel) return;
   const w = parseInt($('selwave').value, 10);
   if (w === sel.w) delete fixes.shape_waves[sel.id]; else fixes.shape_waves[sel.id] = w;
   afterEdit('Moved shape #' + sel.id + ' to wave ' + w + '.');
 });
 $('btn-wave-wave').addEventListener('click', () => {
   if (!sel) return;
   const src = waveOf(sel), dst = parseInt($('selwave').value, 10);
   if (src === dst) { setHint('That is already its wave — pick a different one to merge into.'); return; }
   fixes.wave_merges[src] = dst;
   afterEdit('Merged wave ' + src + ' (everything like it) into wave ' + dst + '.');
 });
 $('btn-flower-shape').addEventListener('click', () => {
   if (!sel) return;
   const f = parseInt($('selflower').value, 10);
   fixes.shape_flowers[sel.id] = f;
   afterEdit('Moved shape #' + sel.id + ' to ' + flowerLabel(f) + '.');
 });
 $('btn-flower-wave').addEventListener('click', () => {
   if (!sel) return;
   const f = parseInt($('selflower').value, 10);
   fixes.wave_flowers[waveOf(sel)] = f;
   afterEdit('Moved wave ' + waveOf(sel) + ' (everything like it) to ' + flowerLabel(f) + '.');
 });
 $('btn-noflower').addEventListener('click', () => {
   if (!sel) return;
   fixes.shape_flowers[sel.id] = 0;
   afterEdit('Took shape #' + sel.id + ' out of its flower.');
 });
 $('btn-noflower-wave').addEventListener('click', () => {
   if (!sel) return;
   const w = waveOf(sel);
   fixes.wave_flowers[w] = 0;
   afterEdit('Took wave ' + w + ' (everything like it) out of its flower.');
 });
 // Live preview: changing a dropdown lights the destination group yellow on
 // the picture BEFORE any button is pressed, so the owner sees what a
 // move/merge will combine (owner ask 2026-06-11: "when I switch wave, why
 // don't i see what it will be merged with?").
 $('selwave').addEventListener('change', () => {
   drawMarks();
   const pw = previewWave();
   setHint(pw !== null
     ? 'Yellow = wave ' + pw + ' — that is what "Move" will combine your pick with.'
     : 'That is already its wave.');
 });
 $('selflower').addEventListener('change', () => {
   drawMarks();
   const pf = previewFlower();
   if (pf === null) setHint('That is already its flower.');
   else if (pf === 0) setHint('No flower — "Move" / "Take out" sets it on its own.');
   else setHint('Yellow = ' + flowerLabel(pf) + ' — that is where "Move" will put your pick.');
 });
 $('btn-close').addEventListener('click', () => {
   sel = null; $('panel').hidden = true; drawMarks();
 });
 // Server mode: the gate verdict is recorded HERE (session.json via the
 // server), not transcribed from chat — the page that shows the plan is the
 // page that records the agreement.
 if (SERVER) {
   $('hublink').hidden = false;
   $('agreebtn').style.display = '';
   $('agreebtn').addEventListener('click', async () => {
     if (dirty()) { setHint('You have unapplied fixes — press the apply button first, then agree.'); return; }
     $('agreebtn').disabled = true;
     try {
       const r = await fetch('/api/agree', { method: 'POST' });
       if (!r.ok) throw new Error(await r.text());
       $('agreebtn').textContent = 'Recorded ✓ — we will start building';
     } catch (err) {
       $('agreebtn').disabled = false;
       setHint('Could not record the agreement — tell me and I will look: ' + err.message);
     }
   });
 }
 $('applybtn').addEventListener('click', async () => {
   if (SERVER) {
     setHint('Redrawing the pictures with your fixes\u2026 this takes a few seconds.');
     $('applybtn').disabled = true;
     try {
       const r = await fetch('/api/overrides', { method: 'POST', body: JSON.stringify(fixes) });
       if (!r.ok) throw new Error(await r.text());
       location.reload();
     } catch (err) {
       $('applybtn').disabled = false;
       setHint('Something went wrong applying the fixes \u2014 tell me and I will look: ' + err.message);
     }
   } else {
     const blob = new Blob([JSON.stringify(fixes, null, 2)], { type: 'application/json' });
     const a = document.createElement('a');
     a.href = URL.createObjectURL(blob);
     a.download = 'wave-plan-overrides.json';
     a.click();
     setHint('Saved to your Downloads. Tell me you saved it and I will redraw the pictures with your fixes.');
   }
 });
 options();
 renderFixes();
"""
    html = html.replace(
        "__EDIT_JS__",
        edit_js.replace("__SHAPES__", shapes_js)
        .replace("__WAVE_INFO__", wave_info_js)
        .replace("__FLOWERS__", flowers_js)
        .replace("__APPLIED__", applied_js)
        .replace("__IMG_W__", str(img_w))
        .replace("__IMG_H__", str(img_h)),
    )
    (out_dir / "wave-plan.html").write_text(html)
    print(
        f"wrote {out_dir}/wave-plan.html (+ {n_waves} wave PNGs, "
        f"{len(rings)} flower PNGs, waves-map.png, flowers-map.png, wave-plan.json)"
    )


if __name__ == "__main__":
    main()
