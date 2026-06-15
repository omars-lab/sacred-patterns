# iter-35 visual verdict — bold straps (width 6 → 8, portal gap q12-…-699-199)

First seed-driven iteration: hypothesis.md was authored from the machine seed
(`hypothesis-seed.md`, drafted by tools/seed-hypothesis.py from iter-34's
portal verdict), with every TODO(judgment) filled by hand.

## Expectation (written in hypothesis.md BEFORE viewing — Tenet 24)

Same rosette lattice as iter-34, bands roughly double in thickness, straps
fuse into bold white ribbons, blue/turquoise pockets shrink slightly but stay
clearly visible, weave gaps remain. Failure signature: pockets vanishing under
white, or merged white blobs near the center where decoration lines converge.

## Observation AFTER viewing

**The named failure mode fired at the initial width guess, and the probe
ladder resolved it:**

- **width 12** (the ratio-matching guess): outer-ring straps read bold, but
  the dense center merged into white mass — the central 10-point star barely
  legible, small pockets swallowed. Exactly the predicted over-widening cost.
- **width 10**: middle ring still washes out.
- **width 8 (shipped)**: the widest setting that keeps the center star and
  ring tiles legible. Straps clearly bolder than iter-34's width 6; pockets
  intact; weave gaps visible. Strand count unchanged at 2790 (width is pure
  render-style — the network is untouched).

Against the reference: the bold-strap *reading* is recovered at the lattice
level. The residual whiteness/fineness gap vs the reference is network
DENSITY, not width — our decagons-only field has no bowtie/hexagon
pocket-stars (deferred per iter-34's second finding), so the space the
reference fills with large colored tiles is here subdivided by extra
decoration lines. No width value fixes a density property; widening past 8
only erases tiles.

## Metrics (corroboration, not the decider)

- pixel-diff similarity **71.4%** (iter-34: 70.8%) — predicted +3–5, actual
  **+0.6**. Predicted-vs-actual error: the prediction over-credited strap
  weight; the heatmap is red across the whole interior, i.e. the composite is
  dominated by fine-texture density mismatch and the palette-family drift the
  machine already flagged (r=84.6 vs b=62.6, "wrong palette family"), neither
  of which width touches.
- gt.json: 2031 shapes (unchanged from iter-34) — classification stable.

## Verdict

Ships as iter-35: the reviewer's named gap ("white bands far too fine") is
addressed at the maximum width the construction tolerates, on a viewed render
compared against a pre-stated expectation, with the probe trail recorded.
**Still below the 80% portal floor — the loop continues.**

Next-gap routing (for iter-36's hypothesis, in priority order):
1. **Palette family** — the machine's channel-drift warning names it directly;
   our navy/royal/cobalt family is visibly darker/greener than the reference's
   blue family. A palette-only edit is now the top candidate since the
   structural lattice is aligned and strap weight is at its tolerable max.
2. **Pocket-star density** (deferred from iter-34) — bowtie/hexagon tiles in
   the field would replace subdivided white regions with the reference's
   colored pocket-stars; this is the remaining structural lever but is
   engine-side (field composition), much larger than a palette pass.
3. Scalloped-vs-rounded boundary ring (unchanged, smaller).
