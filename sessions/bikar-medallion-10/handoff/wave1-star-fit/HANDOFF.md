# Wave-1 center-star fit — PROVEN diff for the construction worker (lane #50)

**Status:** APPLIED to live pattern.bkr at **iter-70** (2026-06-12). Gate passed:
census-equal (675 shapes, zero bucket delta) + eyeball (slivers closed, full star,
fatness in reference family — see iter-70/hypothesis.md). Lane #58 closed.

**ROTATION FOLLOW-UP (owner-flagged "shape better but rotation off"):** the hankin-54
star had the right fatness but was **18° off** the reference. Root cause: `hankin`
shoots rays from the inscribed decagon's edge MIDPOINTS (phase 18°,54°,90°… for N=10),
while the reference star's points sit at the division-VERTEX phase (0°,36°,72°…) — a
half-division-step gap. **Fix:** pre-rotate C0's decagon 18° via a NEW DSL primitive
`divide C0 into 10 offset 18` (kernel `divideCircle` already took a `startAngle`; the
`divide` statement didn't expose it — a Tenet-26 invocation gap, not new kernel work).
Re-gate: census still EQUAL (675), wave-1 coverage **0.838 → 0.932**, iou 0.627 → 0.751
(above the original {10/4} record). Eyeball: navy star's 10 points land on the gold
reference outline, points-on-points. Regression frozen at
`packages/core/tests/dsl/divide-offset.test.ts` (4 tests); full bikar suite green.

## The fix (one line)

In `pattern.bkr`, the wave-1 star overlay:

```
  layer 1
- connect every 4 on C0      # {10/4} — points too thin (the gold-sliver whitespace)
+ hankin angle 54 on C0      # continuous contact-angle star — points match reference fullness
```

`C0` stays `radius 22.6 / divide into 10` — **do not resize or reposition.** The fix is
point *fatness*, via the Hankin contact angle, not size or position.

## Why this and not the cheaper option

Two candidate levers were rendered and eyeballed at matched star scale against the
reference (`wave1-bracket.png`):

| variant | result | verdict |
|---|---|---|
| `connect every 4` ({10/4}, current) | needle-thin points | too thin — the original gap |
| `connect every 3` ({10/3}) | blunt fat points, shallow valleys | **overshoots** — too fat |
| `hankin angle 36` | near-solid decagon | too blunt |
| **`hankin angle 54`** | full 10-pointed star, moderate depth | **matches reference** ✓ |
| `hankin angle 72` | thin sharp points | too thin |

The discrete Schläfli step has no `{10/3.5}` between too-thin `{10/4}` and too-fat
`{10/3}` — exactly the case iter-41's falsifier note named ("route to Hankin-angle star
rather than scale tuning"). `hankin angle` is the continuous knob; θ=54 lands in the
reference's fatness range.

## Gate evidence (already cleared)

- **Census-equality (PRIMARY):** hankin-54 vs {10/4} → **zero bucket changes**, no
  face-split. The central star stays one 20-vertex face (`{10/n}` stars emit 20-vertex
  outlines), same id, same totals (675 shapes both).
- **Central star area:** {10/4}=2551 → hankin-54=3189 (+25%) → {10/3}=3526. hankin-54 sits
  between the extremes; the +25% closes the documented ~13% thin-point gap.
- **Eyeball (DECISIVE, Tenet 24/27):** `wave1-fix-ab.png` — reference vs hankin-54 at
  matched scale. Full 10-pointed navy star, moderate point depth, gold slivers closed.
  Recorded divergence: reference points are slightly more rounded/organic and the white
  lattice is a touch wider — a sub-point-shape + Stage-3 lattice matter, not the fit gap.

## After applying

1. Re-render the live pattern.bkr; confirm census still equal except the star face's shape.
2. Re-run the wave-1 gate sbs; confirm the gold slivers are closed.
3. iou should rise as slivers close, but **do not tune toward an iou number** (Tenet 7) —
   census + eyeball carry acceptance. Wave 1 is saturated-coverage.
4. Optional next refinement (not the owner's flagged gap): nudge θ between 50–58 if a
   tighter point-roundness match is wanted; θ=54 is the proven baseline.

Scratch artifacts: `/tmp/wave1-hankin-54.{bkr,svg}`; images in this dir.
Images: `wave1-bracket.png` (full lever sweep), `wave1-fix-ab.png` (ref vs fix),
`wave1-matched-sbs.png` ({10/4} vs {10/3}).
