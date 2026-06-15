# iter-36 visual verdict — palette-family pass (measured rank-matched clusters)

Palette-only iteration: the five hex literals in the palette block were
replaced with the reference's measured 8-cluster histogram values,
rank-matched by lightness (deep_navy #262E3D, navy #132A61, royal #2B61B7,
cobalt #32B0CA, turquoise #BBC5D5). No classify, fill, field, or strapwork
change. gt.json: 2031 shapes (unchanged) — geometry identical to iter-35.

## Expectation (written in hypothesis.md BEFORE viewing — Tenet 24)

Identical geometry/lattice to iter-35; dominant field shifts from near-black
navy to lighter royal-navy; green-teal turns pale blue-grey; steel kites turn
saturated royal; pentagons turn cyan — the render reads as the reference's
airier blue family. Failure signature: pale triangles washing out against the
white straps, or the dominant dark reading purple/grey.

## Observation AFTER viewing

**Expectation confirmed at the family level.** The render now reads as the
reference's blue family: saturated royal blues, cyan pentagons, pale
blue-grey patches, dominant dark a true royal-navy. Neither failure signature
fired — the dark is navy (not purple/grey), and the pale #BBC5D5 tiles sit
close to the white straps but keep legible boundaries.

## Metrics (corroboration, not the decider)

- pixel-diff similarity **72.9%** (iter-35: 71.4%) — predicted +4–8, actual
  **+1.5**. Second consecutive over-prediction.
- **The channel-drift warning did NOT clear** — spread *widened* (22.0 →
  30.3; r=83.3 vs b=53.0). With the palette now literally the reference's
  measured clusters, the persisting drift cannot be a flat-fill family error.
- Heatmap: red across the whole interior, same signature as iter-35.

## Why the drift persists (diagnosis)

The per-pixel comparison pairs each reference pixel against whatever sits at
that location in our render. The reference fills large regions with colored
pocket-star tiles; our decagons-only field subdivides those same regions with
extra decoration lines, so a colored reference pixel routinely pairs against
a white strap pixel (and vice versa). That misregistration produces channel
drift no palette value can fix — the warning is now a *structural-density*
symptom wearing a color costume. The counterfactual in pixel-diff.json caps
the whole drift fix at ~+5.7; the structural lever is bigger than that.

## Verdict

Ships as iter-36: the palette family is measured-correct and visually
confirmed; the residual metric gap is structural. **Still below the 80%
portal floor — the loop continues.**

Next-gap routing (for iter-37's hypothesis, in priority order):
1. **Pocket-star density** — now unambiguously the top lever (deferred since
   iter-34): bowtie/hexagon tiles in the girih field would replace the
   white-subdivided regions with the reference's large colored pocket-stars.
   Engine-side field-composition work, the only remaining large lever.
2. Per-role color correction (which class wears which family) — cheap, but
   should be driven by portal Q7 annotations, not guessed; defer until a
   portal pass.
3. Scalloped-vs-rounded boundary ring (unchanged, smaller).
