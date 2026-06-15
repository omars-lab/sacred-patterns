# Stage-1 structure audit — iter-39 (first structure gate)

Plain English first: this is the first run of the new stage-gated process —
the line skeleton of our best construction (iter-39), stripped of all color
and bands, side by side with the edge-extracted reference. The owner looks
at the pair and says whether the STRUCTURE is agreed; until it is, every
iteration is a `stage: structure` iteration and color/weave stay frozen.

## Expected vs observed (Tenet 24 — expectation stated before viewing)

**Pre-stated expectation:** "the skeleton will show a uniform fine girih
mesh; the reference lines will show ~10 bold rosette flowers with strong
radial arms — the densities will visibly disagree."

**Observed: confirmed.** The reference's edge map shows ~13 bold rosette
flowers with a scalloped (lobed) outer boundary; our skeleton is a much
finer, denser uniform mesh with a smooth round boundary. The two clearest
structural divergences, in the order the eye finds them:

1. **Boundary:** reference is scalloped (lobes following the rosettes);
   ours is round.
2. **Field density / boldness:** reference reads as discrete bold flowers
   with whitespace between them; ours reads as a continuous fine mesh.

## Numbers

- `structure_similarity` = **84.1** (pixel-diff on Canny edge maps;
  iter-38 = 83.6 — the pockets-star geometry registers +0.5 structurally,
  consistent with its +0.5 full-color move)
- `skeleton_sha256` = `71baccec863a09fe8546e5d26ebad6c91057af60bd27b34e61b6565ccf4496b3`
  (the freeze check for Stage 2/3 once the gate passes)

## Shape census (gt.json, 933 shapes)

| face_class | count | sides profile |
|---|---|---|
| .turquoise | 590 | triangles (sides=3: 580 total) |
| .royal | 210 | quads (sides=4: 170 total) |
| .navy | 90 | 6+ sided |
| .pocket | 22 | big in-lens star faces |
| .cobalt | 20 | pentagons |
| .deep_navy | 1 | the 240-vertex outer region |

The census tells the same story as the eye: 580 triangles + 170 quads =
a fine mesh, where the baseline expects bold discrete elements (stars,
rhombi, large polygons per `input/baseline.json` zones).

## Gate artifacts

- `structure-context-sbs.png` — reference | skeleton (the gate visual)
- `structure-sbs.png` — reference edge map | skeleton edge map
- `input/reference-analysis/swatch-sheet.png` — standardized palette
  (the parallel Stage-2 entry gate; see `reference-analysis.md`)

## Expected verdict and routing

Expected: structure **NOT agreed** → iter-40+ are `stage: structure`
iterations until the owner gates it. Candidates already routed (from
iter-39's visual-verdict.md, now re-scoped as structure work):

- **Scalloped boundary ring** (carried since iter-36; authorable today
  with `connect arc` chains on a separate layer) — attacks divergence #1.
- **Field scale/density** (`girih field decagonal 62` edge size / shells)
  — attacks divergence #2; needs its own hypothesis.

Color knowledge (iter-38/39 fills, the standardized palette) transfers
onto the agreed structure when Stage 2 opens.
