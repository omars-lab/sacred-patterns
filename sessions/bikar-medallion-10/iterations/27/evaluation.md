# iter-27 — Direct `face` declaration for central 20-vertex shape (Resolution Path #1)

**Pattern:** iter-26 with central `face` statement declaring 20 outward arcs on Cstar20.
**Bikar HEAD:** 8c17615.
**Qiyas:** master.

## Why this run exists

iter-26 falsified Resolution Path #2 (layer isolation) — strapwork
crossings still subdivided the {20/3} chord polygon. iter-26's
evaluation.md recommended Resolution Path #1: declare the v20 face
directly via the `face` statement, which decouples from
chord-intersection-driven face extraction entirely.

iter-27 ships exactly that:
```
face
  arc Cstar20.cpt0 -> Cstar20.cpt1 on Cstar20
  arc Cstar20.cpt1 -> Cstar20.cpt2 on Cstar20
  ... (20 arcs total) ...
  arc Cstar20.cpt19 -> Cstar20.cpt0 on Cstar20
```

The face statement asserts a face at evaluation time, not derived
from intersections.

## Validation outcome — variant 3 also falsified

| Metric          | iter-25                | iter-26                | iter-27                |
|-----------------|-----------------------:|-----------------------:|-----------------------:|
| A1              | PASS                   | PASS                   | PASS                   |
| A2 status       | APPROXIMATE            | APPROXIMATE            | APPROXIMATE            |
| A2 cv           | **0.0365 (cascade best)** | 0.0415              | 0.0406                 |
| A4              | FULL                   | FULL                   | FULL                   |
| A5 status       | COMPLETE               | COMPLETE               | COMPLETE               |
| A6 score        | 0/18                   | 0/18                   | **0/18 (unchanged)**   |
| inner-star v20  | MISSING (0)            | MISSING (0)            | **MISSING (0)**        |
| v20 in SVG      | -                      | -                      | **1 (bikar emit OK!)** |
| v20 in qiyas encode | 0                  | 0                      | **0 (encoder drop)**   |
| total shapes    | 2578                   | 2218                   | 2154                   |

## Hypothesis falsified — root cause shifts to qiyas encoder

This run reveals something the prior two iters didn't: **bikar DID
emit the v20 face** (`grep data-sides="20" render.svg` finds exactly
1 face), but **qiyas's encoder didn't pick it up as a 20-vertex
shape** — `shapes_by_vertex_count` has no "20" key.

Inspecting the emitted face's SVG:
```
<path d="M20.0000,0.0000 A20,20 ... A20,20 ... Z"
      data-face-index="723" data-sides="20" data-layer="3"
      clip-path="url(#fc-723)" fill="none" stroke="none" />
```

The 20 successive outward arcs on a circle = a full closed circle.
The face IS visually a circle — qiyas's encoder correctly identifies
it as `type=circle` (the `data-sides="80"` count in the SVG is
likely qiyas's stroke-trace artifact). The 20-vertex polygon
identity exists only in bikar's planar-graph data and the SVG
`data-*` attributes, NOT in the rendered geometry.

## Three falsifications of the same construction goal (Tenet 7 stop)

| iter | Variant of "make a v20 shape appear in qiyas" | Falsified by |
|------|------------------------------------------------|--------------|
| 25   | {20/3} chord polygon in layer 0 (shared chords) | C1 chord intersections subdivide |
| 26   | {20/3} chord polygon in isolated layer 4       | Strapwork bands subdivide          |
| 27   | `face` statement with 20 arcs on Cstar20       | Renders as circle (no v20 shape in encoder) |

The pattern: each variant tried a different bikar-side production
mechanism. All three fail because **at the rendered-geometry level,
a v20 shape must have 20 VISIBLY DISTINCT vertices**. The {20/3}
chord polygon has them but gets subdivided; the
20-arcs-on-Cstar20 face has zero visible corners. The only
construction that would emit a vertex-distinct v20 shape inside the
strapwork medallion would be a chord polygon whose chords don't
cross any other chords — which requires removing OR isolating most
of the medallion's other content (Resolution Paths #3 and #4 from
iter-25).

## Recommendation — pivot per iter-26's Resolution Path #4

Per the `handle-falsification` skill's introspection layers:

- **L1 (implementation bug):** Ruled out. Bikar `face` statement
  works correctly — it emits the face with `data-sides="20"`.
- **L2 (option mechanism wrong):** YES — every "add a v20 shape"
  variant requires either chord-distinctness (broken by strapwork)
  or vertex-distinctness (broken by arc-collinearity-to-circle).
- **L3 (option enumeration wrong):** YES — the doc enumerated 4
  resolution paths but didn't note that Paths #1 and #2 share the
  failure mode (strapwork subdivision/blending).
- **L4 (framing wrong):** PARTIALLY — the framing was "close the
  inner-star v20 MISSING verdict." A deeper framing: "does this
  cascade's construction philosophy (chord-overlay + strapwork)
  support the baseline's expected shape vocabulary?" Answer:
  partially. A2/A4/A5 yes; A6 rich-inner-shapes no.

**The cascade should pivot per Resolution Path #4: accept the
A2/A4/A5 wins this cascade has achieved and declare iter-24/25 the
local-optimum frame for the medallion-10 deliverable.**

Cascade closeout metrics:
- A2 cv 0.0365 (iter-25, cascade best, well below iter-14's 0.067)
- A4 FULL coverage
- A5 COMPLETE band-network integrity
- Dominant fold 10, confidence 0.74
- A6 ceiling 0/18 — the baseline's 18 inner-shape expectations
  require a fundamentally different construction philosophy
  (handcrafted inner-zone star/rosette compositions, not the
  chord-overlay+strapwork approach this cascade has used).

A6 0/18 is NOT a regression from the cascade's starting state — it
just reflects that this cascade's construction philosophy and the
baseline's design philosophy don't compose. A6 will need a separate
cascade with a different construction approach (e.g., handcrafted
`face` statements for every expected inner shape, OR a new
construction philosophy starting from rosette-stamping primitives).

## Owner pickup options

1. **Close cascade at iter-25** as the local-optimum and file
   follow-on cascade for "rich inner-zone construction" as a
   separate workstream.
2. **Try Resolution Path #3** (replace C1 chord patterns with
   Cstar20 patterns) — requires re-inspecting reference.jpg to
   decide whether the v20 expectation is the visual
   {10/3}+{10/4}+{10/2} envelope or genuinely a separate 20-star.
3. **Continue iterating** with handcrafted `face` statements for
   each expected inner shape (v8 x6, v6 x2, v4 rhombi x10, etc.) —
   high effort, may close A6 incrementally but loses the cascade's
   philosophical coherence.

Recommendation: option 1 (close cascade) per the bias-for-action
tenet and Resolution Path #4 logic.
