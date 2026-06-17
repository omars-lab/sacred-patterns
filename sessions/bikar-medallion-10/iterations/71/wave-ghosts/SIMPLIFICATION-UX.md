# Simplification UX — the post-waves shape-vocabulary phase (#42 umbrella)

**Plain English:** After the wave-plan is built, the medallion is 523 raw detected faces
— too many to reason about. This phase answers the human question *"what is this pattern
really made of, and how is it organized?"* in three steps, each a small visual the owner
can read in seconds (Tenet 27). #42 is the umbrella; it closes once its three parts ship.

This is the simplification UX: a funnel from raw faces → true shape vocabulary →
organizing structure, that a future DSL-author (human or agent) uses to write the
medallion compactly (`rotate 10` + 26 banded radii) instead of hand-placing 381 shapes.

## The three parts (all shipped, all eyeballed)

| # | step | deliverable | the question it answers |
|---|------|-------------|-------------------------|
| #48 | **rim-band exclusion** | clusterer filter (`n_excluded_frame: 142`) | "which faces are frame/background, not pattern?" — drop them before counting |
| #45 | **shape inventory** | `shape-inventory.png` / `render_shape_inventory.py` | "how many DISTINCT designed shapes?" → **26** (25 repeating families + 1 centerpiece) |
| #46 | **higher-level grouping** | `shape-grouping.png` / `render_grouping.py` / `GROUPING.md` | "how are those shapes ORGANIZED?" → **one 38-shape wedge × 10-fold, 26 concentric bands** |

## The funnel (one coherent story)

```
523 faces detected
  → 142 frame/background excluded        (#48 rim-band filter)
  → 381 placeable
  → 26 distinct shape classes            (#45 congruence clustering, eps 0.06)
  → 1 repeating 38-shape wedge × 10-fold (#46 radial-band + role decomposition)
     in 26 concentric bands
       1 center + 6 on-axis + 6 half-axis + 13 mirror-paired
```

Each arrow is a simplification the eye can verify against its own render. The end state
is the compact mental model: *the medallion is one wedge, rotated ten times, stacked in
26 rings.*

## Why this is the UX foundation (not just analysis)

The grouping (#46) is directly actionable for compact authoring:
- **`rotate 10 around C0.mpt`** captures the 10-fold immediately — the wedge is authored
  once.
- **26 banded radii** are the construction circles; every shape sits on one.
- **Role transitions** (center → inner rosette → arm shafts → rim crown) name the motif
  groups a simplifier can collapse into reusable sub-blocks.

This is what a "simplify this pattern" UX surfaces to the owner: not 381 faces, but the
three-screen funnel above, ending in the wedge they can edit.

## Status

All three parts shipped and visually verified (Tenet 24/25 — expectation written before
viewing, render eyeballed). #42 umbrella closed. The renders live in Dropbox
(`iterations/71/wave-ghosts/`); the generators + notes are authored code in git.
