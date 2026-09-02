# iter-70 — Wave-1 center-star fit (apply proven hankin-54 diff)

**What was broken:** The central 10-pointed star used `connect every 4 on C0`
({10/4}), whose contact points are needle-thin. Between the thin star points and
the surrounding darts, gold/whitespace slivers opened up — the owner-flagged
wave-1 fit gap. The discrete Schläfli step offers no `{10/3.5}` between too-thin
`{10/4}` and too-fat `{10/3}`.

**The fix (one line, lane #58/#50, proven in handoff/wave1-star-fit/HANDOFF.md):**

```
- connect every 4 on C0      # {10/4} — needle-thin points, gold slivers
+ hankin angle 54 on C0      # continuous contact-angle star, full points
```

`C0` unchanged: `radius 22.6 / divide into 10`. The fix is point *fatness* via the
Hankin contact angle, not size or position. θ=54 is the proven baseline (36 too
blunt, 72 too thin, {10/3} overshoots).

## Gate — both passed

**1. Census-equality (PRIMARY):** iter-69 → iter-70, **675 shapes both, zero
bucket delta** across all (type,sides) buckets. No face-split; the central star
stays one face. (`70/pattern.gt.json` vs `69/pattern.gt.json`.)

**2. Eyeball (DECISIVE, Tenet 24/27):**
- *Expected before viewing:* central navy star points fatten, gold slivers
  between star and darts close, no other geometry changes.
- *Observed:* exactly that. `wave1-star-ab.png` (69 thin vs 70 fat): the internal
  sliver/cross-hatch lines of {10/4} disappear, the star reads as one solid fat
  face. `wave1-ref-vs-fix.png` (reference vs 70): hankin-54 sits in the
  reference's fatness family — a touch rounder than the reference's moderate
  point-depth, which is the documented sub-point-shape residual, not the fit gap.

**3. iou:** attribution-only, NOT tuned (Tenet 7). Wave 1 is saturated-coverage.

Artifacts: `wave1-star-ab.png`, `wave1-ref-vs-fix.png`, `wave1-fix-eyeball.png`,
`render.svg`, `render.png`, `pattern.gt.json`.

## Follow-up within iter-70 — ROTATION FIX (owner-flagged: "shape better but rotation off")

The hankin-54 star had the right *fatness* but was rotated **18° off** the
reference. Root cause (measured, /tmp star sweep): `hankin` shoots rays from
the inscribed decagon's edge MIDPOINTS — points at 18°,54°,90°… for N=10 —
while the reference star's points (and the old `connect every 4`) sit at the
division-VERTEX phase 0°,36°,72°…. The 18° gap is exactly half a division step.

**Fix:** pre-rotate C0's decagon by 18° via a NEW DSL primitive
`divide C0 into 10 offset 18`. The kernel's `divideCircle` already took a
`startAngle`; the DSL `divide` statement didn't expose it — a Tenet-26
invocation gap, not new kernel work. Wired AST + parser + evaluator
(`offsetDeg` → radians → `startAngle`). C0.cpt* is referenced nowhere else
(only C0.mpt, the phase-invariant rotation center), so the rotation is local.

**Re-gate after rotation:** census still EQUAL (675, zero delta). Wave-1
coverage **0.838 → 0.932**, iou **0.627 → 0.751** — now *above* the original
{10/4} record (0.897 / 0.707). Eyeball (`wave-diff/wave-01/sbs.png`): the navy
star's 10 points land on the gold reference outline, points-on-points; the 18°
mismatch is gone. Regression frozen: `packages/core/tests/dsl/divide-offset.test.ts`
(4 tests). Full bikar suite 964 passed + 3 expected-fail green.

**Witness codified as a reusable technique (Tenet 18, cross-wave propagation
question).** The owner asked whether the skill propagates a fix like this across
the remaining waves. Answer: *within* a wave the symmetry construct (`rotate 10`)
already replicates a single re-authored sector (skill row A2); *across* waves the
offset is local to its circle and is NOT inherited (each wave divides a different
Cn — only C0 carries `offset 18`; the wave-2 darts on C1 align at phase 0 already,
93% coverage). The genuine propagation mechanism is making the **technique**
discoverable for the next wave that hits the same "right shape, wrong rotation"
signal. Now codified:
- New diagnostic-table row (A2 "shape correct but rotated, census EQUAL → phase
  mismatch → `divide offset`").
- New Cookbook entry **#8b** (hankin edge-midpoint phase 180/N vs division-vertex
  phase; fix with `divide Cn into N offset <deg>`, diagnose magnitude from
  rendered tip-angle delta, census must stay EQUAL).
Both in `sacred-patterns/.claude/skills/iterate-construction-hypothesis/SKILL.md`.
So the next aligned-but-rotated wave is a lookup, not a rediscovery.

**Iteration status:** iter-70 remains the frozen best (this turn changed only the
skill, not the `.bkr` — no iter-71 spun; an empty-geometry duplicate would lie
about progress). The aligned wave-1 is the live baseline later waves re-raster.

**Stale-crop fix (owner: "I still see old center in portal for waves 2 and
beyond").** The wave-1 rotation fix changed the center star, but only wave-1's
wave-diff was regenerated at iter-70 — waves 2–15 still pointed at their original
iterations (44, 45, …), all cut BEFORE the rotation fix. Since every wave-diff
crop is cut from the same full render and the center star sits inside the waves
2/3 (middle-flower) crops, those crops showed the OLD pre-rotation center. The
portal's `latest_gate_sbs()` resolves each wave to its newest wave-diff, so wave
1 served iter-70 (new center) while waves 2+ served their old iters (old center) —
which read as "the middle shape changed between waves." Fix: re-ran `wave-diff.py`
for ALL 15 built waves against iter-70's render; all now resolve to iter-70 with a
consistent aligned center. Verified the portal serves the fresh wave-2 sbs
(byte-identical, aligned center on the render panel). `session.json` waves 2–15
re-stamped to iter-70 metrics with a re-baseline note; prior `{iter,coverage,iou}`
preserved under `prev`. Coverage shifted for re-cut waves (wave-2 −7.0, wave-3
−3.3, wave-10 −3.0) — confirmed by eyeball to be the cross-raster baseline shift
(Cookbook #13), NOT geometry regression: the dart rings and shapes sit unchanged
on their gold outlines (iter-69 vs iter-70 render crops compared directly).
Codified as Cookbook **2b-ALL** (shared-geometry change stales every built wave's
crop, not just the changed wave's).

**Blueprint-circle leak fix (owner: "we are showing the blueprint circles used —
many grey circles — should they be in?").** No — construction circles are
scaffolding and must not appear in any render. Root cause: the blueprint group
(`<g data-layer="-1">`) is hidden in the web UI by JS (`applyLayerVisibility` sets
`display:none`), but cairosvg — the wave-diff gate rasterizer — runs no JS, so it
drew the white hairline circles into every gate crop. Measured leak: **80,865 px
(~8% of the 1024² raster)**. Fix at the source (Tenet 28 — fix the system, not the
symptom): the SVG renderer now emits `style="display:none"` on the blueprint
group, which cairosvg honors, so the blueprint is hidden in EVERY rasterizer (gate
crops, CLI `--image`, future paths). The web toggle still works
(`applyLayerVisibility` overwrites `style.display` each render). bikar commit
`deef89f`; regression `packages/core/tests/render/blueprint-hidden-default.test.ts`
(Tenet 18); 5 canonical snapshots updated (diff is ONLY the display:none addition).
iter-70 re-rendered with the fixed engine and all 15 gate crops regenerated — the
leaked circles are gone (before/after: `/tmp` diff showed 80,865 px removed,
eyeballed clean). Full bikar suite 966 + 3 xfail green.
