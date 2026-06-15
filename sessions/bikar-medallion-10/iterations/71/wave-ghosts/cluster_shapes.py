#!/usr/bin/env python3
"""Cluster the finished pattern's faces into CANONICAL shape-classes — the data
layer for the simplification UX (task #43).

Plain English (owner, 2026-06-15): the finished render has 675 faces, but many are
the SAME shape drawn slightly differently — the small kites especially. "Do we see
the final composition: how many unique shapes there are, their placement?" This script
answers the first half: it groups faces by their actual shape (not just area) so the
40 near-identical kites collapse into ONE canonical "kite", and reports how many
genuinely-distinct shapes the pattern is built from.

How (congruence, not area-binning — area alone collides a fat hexagon with a star arm):
each face's outline is normalized — translate to centroid, scale by RMS radius to unit
size — then reduced to a rotation/mirror-invariant SIGNATURE: the sorted multiset of
(edge-length, turning-angle) around the polygon, made cyclic-and-mirror-canonical. Two
faces are "the same shape" when their signatures match within EPS. Vertex count is the
hard first split; congruence within a vertex-count bucket is the real test.

Output: clusters.json next to the renders — a list of canonical classes, each with a
representative outline, member ids, count, vertex_count, area, and the dominant
fill_color/face_class. The /simplify propose-and-confirm UI (task #44) reads this and
shows each cluster as "these N look like one shape — merge?".

Tenet 23: reads the engine-emitted pattern.gt.json (the producer-of-record truth), not
re-derived from raster. Tenet 18: self-checks the partition is total + disjoint.
"""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

B = Path("/Users/omareid/Library/CloudStorage/Dropbox/Data/sacred-patterns/bikar-medallion-10")
ITER = sys.argv[1] if len(sys.argv) > 1 else "71"
GT = B / "iterations" / ITER / "pattern.gt.json"
OUT = B / "iterations" / ITER / "wave-ghosts" / "clusters.json"

# Congruence tolerance on the unit-normalized signature. ~3% of unit scale — tight
# enough that distinct shapes stay split, loose enough that render jitter on
# "the same" kite doesn't spuriously fork it. Tunable; surfaced in the report.
EPS = 0.06


def centroid(pts):
    n = len(pts)
    return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)


def normalized_outline(pts):
    """Center on centroid, scale by RMS radius to unit size. Position/scale removed;
    rotation + mirror still present (the signature removes those)."""
    cx, cy = centroid(pts)
    c = [(p[0] - cx, p[1] - cy) for p in pts]
    rms = math.sqrt(sum(x * x + y * y for x, y in c) / len(c)) or 1.0
    return [(x / rms, y / rms) for x, y in c]


def edge_turn_signature(pts):
    """Rotation+mirror-invariant congruence descriptor (owner rule 2026-06-15: "same
    shape = congruent up to rotation OR mirror-flip").

    Per vertex we record (interior angle, sorted pair of the two adjacent edge lengths).
    Sorting the edge pair is what makes each vertex feature MIRROR-symmetric — flipping
    the polygon swaps a vertex's incoming/outgoing edges, and the sorted pair is
    unchanged. Then we canonicalize over all cyclic rotations of the vertex sequence AND
    its reversal, taking the lexicographically smallest — so a shape and its mirror,
    however rotated and wherever the vertex list starts, produce the IDENTICAL signature.

    Verified (synthetic): scalene-vs-its-mirror = 0.0, scalene-vs-rotated = 0.0,
    scalene-vs-a-different-(isosceles)-triangle = 0.205 (> EPS). This fixed the k03/k04
    mirror-pair miss that the earlier (incoming-edge, signed-turn) descriptor left split."""
    n = len(pts)
    feats = []
    for i in range(n):
        a, b, c = pts[(i - 1) % n], pts[i], pts[(i + 1) % n]
        e1 = math.hypot(b[0] - a[0], b[1] - a[1])  # incoming edge
        e2 = math.hypot(c[0] - b[0], c[1] - b[1])  # outgoing edge
        v1 = (a[0] - b[0], a[1] - b[1])
        v2 = (c[0] - b[0], c[1] - b[1])
        cosang = (v1[0] * v2[0] + v1[1] * v2[1]) / ((math.hypot(*v1) * math.hypot(*v2)) or 1)
        ang = math.acos(max(-1.0, min(1.0, cosang)))  # interior angle, mirror-symmetric
        lo, hi = sorted((e1, e2))
        feats.append((round(ang, 3), round(lo, 3), round(hi, 3)))

    def canon(seq):
        return min(tuple(seq[i:] + seq[:i]) for i in range(len(seq)))

    return min(canon(feats), canon(list(reversed(feats))))


def sig_distance(s1, s2):
    """L-inf distance between two canonical signatures of equal length. Each element is
    a per-vertex feature tuple (interior angle + sorted adjacent edge lengths); we take
    the max abs component difference across all vertices and tuple slots."""
    if len(s1) != len(s2):
        return float("inf")
    d = 0.0
    for t1, t2 in zip(s1, s2):
        for x, y in zip(t1, t2):
            d = max(d, abs(x - y))
    return d


def _selfcheck_invariance():
    """Tenet 18: freeze the witness that drove the descriptor rewrite — the signature
    MUST be identical under mirror and rotation, and MUST differ for a distinct shape.
    This is the k03/k04 mirror-pair bug encoded as an assertion, not shell history."""
    def rot(pts, th):
        return [(x * math.cos(th) - y * math.sin(th),
                 x * math.sin(th) + y * math.cos(th)) for x, y in pts]
    scal = [(0, 0), (3, 0), (1, 2)]
    mir = [(-x, y) for x, y in scal]
    iso = [(0, 0), (2, 0), (1, 3)]
    s = edge_turn_signature(normalized_outline(scal))
    assert s == edge_turn_signature(normalized_outline(mir)), "mirror not invariant"
    assert s == edge_turn_signature(normalized_outline(rot(scal, 0.65))), "rotation not invariant"
    assert s != edge_turn_signature(normalized_outline(iso)), "distinct shapes collapsed"


def main():
    _selfcheck_invariance()
    gt = json.loads(GT.read_text())
    shapes = gt["shapes"]

    # Build a normalized signature per shape. Circles (no angular outline / radius
    # param) form their own family keyed by 'circle' rather than a polygon signature.
    enriched = []
    for s in shapes:
        outline = s.get("evidence", {}).get("outline", [])
        p = s["params"]
        is_circle = s["type"] == "circle"
        if is_circle or len(outline) < 3:
            sig = None
            vc = 0
        else:
            sig = edge_turn_signature(normalized_outline(outline))
            vc = len(outline)
        enriched.append({
            "id": s["id"],
            "type": s["type"],
            "vertex_count": vc,
            "area": s["area"],
            "fill_color": p.get("fill_color"),
            "face_class": p.get("face_class"),
            "center": s.get("center"),
            "polar": s.get("polar"),
            "outline": outline,
            "is_circle": is_circle,
            "_sig": sig,
        })

    # Drop the construction frame from the vocabulary (#48). Why: the 142× "round"
    # class the owner saw on /simplify is NOT a shape they place — it is the blueprint
    # geometry. Every `type:circle` shape in this render is an UNFILLED concentric
    # construction circle (verified: all 142 share center (511.6,519.4), all have
    # fill_color=None AND face_class=None), so highlighting the class floods the whole
    # disc magenta (#47 symptom). A real placeable circle-dot would be a FILLED face;
    # none exist here. So a circle with no fill_color and no face_class is the frame,
    # not the picture — exclude it from the shape vocabulary. (Polygon faces are all
    # filled and stay.) If a future pattern has genuine filled circle-dots, they keep
    # their fill_color/face_class and survive this filter.
    def _is_construction_circle(e):
        return e["is_circle"] and not e["fill_color"] and not e["face_class"]

    excluded = [e for e in enriched if _is_construction_circle(e)]
    enriched = [e for e in enriched if not _is_construction_circle(e)]
    # Tenet 18: the witness that drove this fix — every circle in THIS render is
    # construction geometry, so the placeable vocabulary is exactly the filled faces.
    assert all(e["is_circle"] for e in excluded), "non-circle slipped into the frame filter"
    assert all(not e["is_circle"] for e in enriched) or any(e["fill_color"] for e in enriched if e["is_circle"]), \
        "an unfilled construction circle survived the vocabulary filter"

    # Greedy single-link clustering WITHIN each vertex-count bucket (circles separate).
    clusters = []  # each: {members:[...], rep_sig, vertex_count}
    # circles first — one class (could refine by radius later). After the #48 frame
    # filter, only FILLED circle-dots reach here (none in the current medallion).
    circ = [e for e in enriched if e["is_circle"]]
    if circ:
        clusters.append({"members": circ, "rep_sig": None, "vertex_count": 0,
                         "kind": "circle"})

    by_vc = defaultdict(list)
    for e in enriched:
        if not e["is_circle"] and e["_sig"] is not None:
            by_vc[e["vertex_count"]].append(e)

    for vc, group in sorted(by_vc.items()):
        buckets = []  # list of (rep_sig, [members])
        for e in group:
            placed = False
            for bk in buckets:
                if sig_distance(e["_sig"], bk[0]) <= EPS:
                    bk[1].append(e)
                    placed = True
                    break
            if not placed:
                buckets.append((e["_sig"], [e]))
        for rep_sig, members in buckets:
            clusters.append({"members": members, "rep_sig": list(rep_sig),
                             "vertex_count": vc, "kind": "polygon"})

    # Tenet 18: the vocabulary partition must be total + disjoint OVER THE PLACEABLE
    # shapes — i.e. every shape EXCEPT the excluded construction frame (#48) lands in
    # exactly one cluster, and nothing lands twice.
    seen = set()
    for c in clusters:
        for m in c["members"]:
            assert m["id"] not in seen, f"shape {m['id']} in two clusters"
            seen.add(m["id"])
    assert len(seen) + len(excluded) == len(shapes), \
        f"partition covers {len(seen)} placeable + {len(excluded)} frame of {len(shapes)}"

    # Emit a compact, UI-friendly summary. Sort biggest-count first.
    clusters.sort(key=lambda c: -len(c["members"]))
    out = []
    for i, c in enumerate(clusters):
        ms = c["members"]
        areas = [m["area"] for m in ms]
        colors = Counter(m["fill_color"] for m in ms)
        fclass = Counter(m["face_class"] for m in ms)
        rep = max(ms, key=lambda m: m["area"])  # representative = largest member
        # Edge-length evidence (normalized rep outline) — the merge UI shows this so
        # the owner sees WHY shapes group ("3 edges: 1.40, 2.26, 1.40 — isosceles").
        rep_norm = normalized_outline(rep["outline"])
        edges = [round(math.hypot(rep_norm[(k + 1) % len(rep_norm)][0] - rep_norm[k][0],
                                  rep_norm[(k + 1) % len(rep_norm)][1] - rep_norm[k][1]), 3)
                 for k in range(len(rep_norm))] if c["kind"] == "polygon" else []
        out.append({
            "cluster_id": f"k{i:02d}",
            "kind": c["kind"],
            "vertex_count": c["vertex_count"],
            "count": len(ms),
            "area_min": round(min(areas), 1),
            "area_max": round(max(areas), 1),
            "area_spread_pct": round(100 * (max(areas) - min(areas)) / max(max(areas), 1), 1),
            "edge_evidence": edges,        # normalized edge lengths of the representative
            "dominant_color": colors.most_common(1)[0][0],
            "color_variants": dict(colors),
            "dominant_class": fclass.most_common(1)[0][0],
            "representative_outline": rep["outline"],
            "member_ids": [m["id"] for m in ms],
            "member_centers": [m["center"] for m in ms],
        })

    # Merge PROPOSALS for the propose-and-confirm UI (#44): the borderline pairs the
    # owner should judge. For every pair of polygon classes with the SAME vertex count,
    # measure signature distance; the closest pairs (just above EPS) are the ones most
    # likely to actually be "the same shape" the auto-clusterer split on jitter. We rank
    # by distance and keep the closest N so the owner walks the strongest candidates
    # first. Same-vertex-count is required (a 6-gon and 7-gon are never "the same").
    poly_clusters = [c for c in clusters if c["kind"] == "polygon"]
    idx = {id(c): i for i, c in enumerate(clusters)}  # map back to emitted cluster_id order
    # Recompute the emitted index per cluster (out[] is sorted same as clusters).
    cid_of = {id(c): out[i]["cluster_id"] for i, c in enumerate(clusters)}
    proposals = []
    for a in range(len(poly_clusters)):
        for b in range(a + 1, len(poly_clusters)):
            ca, cb = poly_clusters[a], poly_clusters[b]
            if ca["vertex_count"] != cb["vertex_count"]:
                continue
            dist = sig_distance(ca["rep_sig"], cb["rep_sig"])
            proposals.append({
                "a": cid_of[id(ca)], "b": cid_of[id(cb)],
                "vertex_count": ca["vertex_count"],
                "distance": round(dist, 4),
                # color-only hint: distance ~0 means identical silhouette, different
                # bucket only because EPS just barely split them (or color differs).
                "same_silhouette": dist <= EPS * 1.5,
            })
    proposals.sort(key=lambda p: p["distance"])
    proposals = proposals[:40]  # closest 40 — strongest merge candidates first

    OUT.write_text(json.dumps({"eps": EPS, "n_shapes": len(shapes),
                               # #48: shapes that count toward the vocabulary, after
                               # the construction-frame circles are removed.
                               "n_placeable": len(seen),
                               "n_excluded_frame": len(excluded),
                               "n_clusters": len(out), "clusters": out,
                               "proposals": proposals}, indent=1))

    # Console report.
    print(f"{len(shapes)} faces ({len(excluded)} construction-frame circles excluded, #48) "
          f"-> {len(seen)} placeable shapes -> {len(out)} canonical shape-classes (EPS={EPS})")
    print(f"{'cluster':8} {'kind':8} {'v':>3} {'count':>5} {'area_spread':>11}  color")
    for c in out:
        print(f"{c['cluster_id']:8} {c['kind']:8} {c['vertex_count']:>3} "
              f"{c['count']:>5} {c['area_spread_pct']:>10.1f}%  {c['dominant_color']}")
    poly = [c for c in out if c["kind"] == "polygon"]
    big = [c for c in poly if c["count"] >= 10]
    print(f"\n{len(poly)} polygon classes; {len(big)} are repeated >=10x "
          f"(the pattern's core vocabulary).")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
