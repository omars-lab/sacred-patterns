# Qiyas: hierarchical pixel-diff with per-region localization

## Problem

`qiyas pixel-diff` today produces a single global similarity score (e.g. 75.1% on iter-16 of bikar-medallion-10). That number tells you *whether* the recon diverges, not *where*. Three concrete failure modes this hides:

1. **Sector-localized regressions invisible.** Iter-16's A2 cv 0.2671 (BROKEN) means 10-fold symmetry is broken — i.e. divergence is concentrated in some sectors and not others. The global score averages across sectors and reports a smooth degradation. The iteration loop has no signal to say "wedge 3 looks fine, wedge 7 is the problem."
2. **Counterfactuals are global.** Plan #109's fragmentation tax targets the global extras count (247). It can't say "the extras are clustered in the strapwork band radius 60–80, not in the central rosette." That information would change the next iteration's edit.
3. **Diagnostic artifact has low information density.** The heatmap PNG (`qiyas/diff/heatmap.png`) shows per-pixel difference. Humans glance at it; the iteration loop ignores it (no machine-readable structure).

User-proposed approach: recursively break each image into quadrants, compare quadrant-pairs, recurse into the divergent ones until a minimum cell size. The output is a tree of per-region scores — both human-readable (overlay heatmap) and machine-readable (JSON tree).

## Three approaches considered

| Approach | What it does | Pros | Cons |
|---|---|---|---|
| **A: Recursive quadtree** (user's idea) | Split into 4 quadrants, score each, recurse into divergent ones | Cheap; localization is the output by construction; each leaf is a bounded region with one number | Quadtree axes are rectangular, our patterns are rotationally symmetric — a divergent sector can straddle quadrant boundaries |
| **B: MS-SSIM Gaussian pyramid** (Wang 2003) | Build pyramid by repeated blur+downsample, compute SSIM at each scale, weighted-combine | Well-validated perceptual metric; one number; matches human vision | Loses spatial localization (collapses to one composite score); no per-region tree |
| **C: Per-pixel SSIM map + region pooling** (skimage) | Sliding-window SSIM at full resolution → per-pixel quality map → pool by region | Highest localization granularity; off-the-shelf in skimage | Output is a dense map, not a tree; pooling regions still need to be defined |

**Recommended hybrid: A with B's metric inside each cell.** The quadtree gives the localization tree the user wants. At each leaf, the cell-pair gets a multi-scale SSIM (or just SSIM at the cell's resolution) to score it. This combines the strengths and matches the existing pixel-diff metric vocabulary.

## Sector-aware variant (deferred to PR2)

For our specific use case (10-fold rotationally symmetric medallions), a quadtree wastes effort: divergent regions are always concentrated in some subset of the 10 sectors, and the rotational orbit structure is *known* (qiyas already detects N-fold). A sector tree — 10 wedges → recurse radially within each wedge — would be more informative for medallion patterns.

But it's a special case; the quadtree works for ANY image and has zero domain assumptions. **Ship the quadtree first (PR1), add sector-aware as an opt-in mode in PR2.**

## Design

### Algorithm (PR1)

```
score(ref_img, recon_img) -> Tree:
  bbox = full image
  return subdivide(ref_img, recon_img, bbox, depth=0)

subdivide(ref, recon, bbox, depth):
  cell_score = similarity(ref[bbox], recon[bbox])
  node = { bbox, score: cell_score, depth, children: [] }

  if depth >= max_depth or
     bbox.width <= min_cell or
     cell_score >= prune_threshold:
    return node  # leaf

  for q in [TL, TR, BL, BR]:
    child_bbox = bbox.quadrant(q)
    node.children.append(subdivide(ref, recon, child_bbox, depth+1))

  return node
```

**Three knobs:**
- `max_depth`: hard cap on recursion (e.g. 6 → up to 4096 leaves)
- `min_cell`: minimum cell size in pixels (e.g. 32px) — below which SSIM becomes unreliable
- `prune_threshold`: stop subdividing if the cell already matches well (e.g. ≥0.95) — saves work on the easy parts of the image

### Per-cell similarity metric

PR1: **single-scale SSIM at the cell's native resolution.** Cell size ≥ 32px; SSIM Gaussian window 11×11; reuses the existing `scikit-image.metrics.structural_similarity` already in qiyas's deps (verify in `qiyas/pyproject.toml`).

Alternative considered: mean-MSE. Cheaper but ignores structure — would score a rotated copy as different even if it's "the same shape, different sector," which is exactly the wrong signal for our use case.

PR2 might upgrade to MS-SSIM (build a pyramid inside each cell), but adds cost without clear benefit at the cell sizes we'll have.

### Output schema

```json
{
  "schema_version": 1,
  "qiyas_version": "0.1.2",
  "max_depth_used": 4,
  "leaf_count": 47,
  "global_score": 0.751,
  "tree": {
    "bbox": [0, 0, 1024, 1024],
    "score": 0.751,
    "depth": 0,
    "children": [
      { "bbox": [0, 0, 512, 512], "score": 0.92, "depth": 1, "children": [] },
      { "bbox": [512, 0, 1024, 512], "score": 0.41, "depth": 1, "children": [
        { "bbox": [512, 0, 768, 256], "score": 0.32, "depth": 2, "children": [...] },
        ...
      ]},
      ...
    ]
  },
  "warnings": [
    {
      "id": "divergent-region",
      "severity": "warn",
      "message": "Cell at (640, 384, 256, 256) scored 0.18 (vs global 0.751) — 12.4% of total area, lowest-scoring leaf",
      "context": {
        "bbox": [640, 384, 896, 640],
        "cell_score": 0.18,
        "area_fraction": 0.124,
        "rank_among_leaves": 1
      }
    }
  ]
}
```

Two artifacts written:
- `hier-diff.json` (the tree above)
- `hier-diff.heatmap.png` — overlay where each leaf cell is filled with a color encoding its score (red=divergent, green=match), partition lines drawn

### CLI surface

```
qiyas hier-diff REF.png RECON.png \
  --max-depth 6 \
  --min-cell 32 \
  --prune-threshold 0.95 \
  --out DIR
```

Defaults chosen so a 1024×1024 image gives a tree with ~50–200 leaves of avg size 64–128px. Tune later from real corpus data.

### Integration with existing pixel-diff

Two integration paths considered:

**Option 1: separate sub-command.** `qiyas hier-diff` is its own thing. `pixel-diff` keeps emitting one global score. The orchestrator calls both; `validation.json` gets a new `tools.hier_diff` block.
- Pros: clean separation; doesn't risk regressing pixel-diff; opt-in cost
- Cons: two commands doing related work; potential to drift apart

**Option 2: pixel-diff gains a `--hierarchical` flag.** The same command emits the tree as part of its existing output schema. Warnings list grows.
- Pros: one command, one cost; the divergent-region warning composes naturally with the existing extra-shapes/missing-shapes warnings
- Cons: schema migration; harder to A/B test

**Recommended: Option 1 for PR1**, with a future migration to Option 2 once the metric is validated against the corpus. The orchestrator (`tools/iteration-validate.sh`) gets one more `qiyas` invocation; the pattern matches how `svg-audit` was added.

### How this composes with existing warnings

The hierarchy adds a new dimension to the warnings array: **where**. Currently warnings answer "what is wrong" (extras, missing, drift). Hier-diff warnings answer "where in the image." Concretely, the iteration loop's `warnings[0]` selection becomes:

> "247 extras (cf_delta=+0.225) — concentrated in cells {(640,384,256,256), (128,640,256,256)} (61% of extras by area)"

That's a much more actionable warning than the current "247 extras (cf_delta=+0.225)" alone. The fix is now scoped to a region, not the whole pattern.

## Three PRs

| PR | Scope | Cost | Unblocks |
|---|---|---|---|
| **PR1** | Quadtree + per-cell SSIM + JSON tree + heatmap PNG + `qiyas hier-diff` CLI + 3-corpus parity smoke test | 1.5–2 days | per-region localization in `validation.json` |
| **PR2** | Sector-aware variant (`--mode sector --n 10`) for rotationally symmetric patterns; cross-reference with svg-audit's detected n-fold | 1 day | medallion-specific localization without manual sector setup |
| **PR3** | Wire hier-diff warnings into qiyas score's warnings array; orchestrator integration in sacred-patterns; iteration-guide updates explaining how to read the tree | 0.5 day | iteration loop driven by region-localized warnings |

## Validation

PR1 passes when:
1. `qiyas hier-diff` runs on iter-14, iter-15, iter-16 of bikar-medallion-10 in <30s each.
2. The leaf-with-lowest-score for iter-15 visibly corresponds to a strapwork sector with broken symmetry (eyeball check against the heatmap).
3. The tree's depth-0 score matches `pixel-diff`'s global score within ±0.01 (sanity: same metric, same image).
4. JSON schema is stable (versioned, documented in `qiyas/docs/validation-envelope.md`).

PR2 passes when sector mode on iter-15 surfaces the BROKEN sectors as the worst-scoring wedges (matching the A2 cv signal).

PR3 passes when an iter-17+ run uses the new region warning to scope its edit and the resulting iteration improves the targeted region's score (closing the loop).

## Cross-tenet check

- **Tenet 1 (simplify while amplifying):** PR1 is the smallest shippable thing that adds region localization. It does not refactor pixel-diff. It does not add sector awareness yet (PR2). One chunk, ships value.
- **Tenet 5 (read existing shape):** Reuses skimage SSIM (already in deps), reuses pixel-diff's image-loading code, reuses validation.json's tools.* schema pattern. No parallel structures.
- **Tenet 3 (surface, don't hide):** A divergent leaf cell becomes a `warnings[]` entry, not a silent number in a tree. The loud signal goes through the existing warning channel.

## Open questions

- **Cell-shape vs window-shape mismatch.** SSIM uses an 11×11 sliding window. A 32×32 cell has only ~100 valid SSIM samples. Is that enough for stable scoring? Probably yes, but verify on the corpus.
- **Asymmetric trees.** If iter-16 prunes 12 cells early (high score) and recurses 35 deep cells, the JSON tree is unbalanced. Is the heatmap renderer OK with that? (Likely yes — each leaf is colored regardless of depth.)
- **Comparison against MS-SSIM baseline.** PR1 should include a one-shot comparison: how does the global hier-diff score correlate with MS-SSIM on the same image-pair? If correlation is high, hier-diff's global score can replace pixel-diff's global score outright (saving an invocation in the orchestrator).

## References

- MS-SSIM: Wang, Simoncelli, Bovik (2003), "Multi-scale Structural Similarity for Image Quality Assessment" — https://www.cns.nyu.edu/pub/eero/wang03b.pdf
- Per-pixel SSIM map (skimage): https://scikit-image.org/docs/0.25.x/auto_examples/transform/plot_ssim.html
- DSSIM (kornelski/dssim, multiscale SSIM in Rust): https://github.com/kornelski/dssim
- Quadtree-based image similarity (Springer 2024): https://link.springer.com/chapter/10.1007/978-981-96-8912-5_15
