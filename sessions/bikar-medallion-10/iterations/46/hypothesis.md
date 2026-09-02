# Iteration 46 — Hypothesis

```yaml
attempt: 46
date: 2026-06-11
stage: structure
target_wave: 4
gap_targeted: >
  Wave 4 — 10 deep-navy shapes on the DART axes (18 deg mod 36) at
  kind_r_frac 0.247 — has nothing of ours. Visual identification
  (wave4-tinted crop, Tenet 24: pre-stated "arrowhead forking into two
  prongs" was falsified — the divergence located the real shape): each is
  a small 5-pointed star (pentagram), one point aimed at the medallion
  center. Contour extraction gives a consistent 10-vertex outline in
  medallion-polar units: tip_in (axis, 58u), valleys axis+-2.7 deg
  (66.4u), wings axis+-10.2 deg (67.8u), valleys axis+-3.9 deg (72.3u),
  prongs axis+-5.6 deg (81.3u), valley_axis (axis, 75.5u). Model fit:
  star center r_c ~= 71u, point radius R ~= 13u — law-of-cosines check
  puts the inward tip at 58u and the prongs at 81.9u (both match);
  pentagram area ~1.12 R^2 ~= 190u^2 vs measured ~173u^2 (white bands
  eat the edges, same regime as every passed wave).
one_idea: >
  A pentagram ring in layer 1, same standalone-closed-cycle technique
  that passed waves 2 and 3. Tenet 26 routing: the DSL's star primitive
  (connect every K) only draws stars centered on a divided circle, but
  no extension is needed — every measured vertex angle is EXACTLY
  representable on a division grid whose step divides gcd(18, delta):
  six new blueprint rings C8 r58/20, C9 r66.4/400 (0.9 grid, +-2.7 =
  cpt17/cpt23), C10 r67.8/600 (0.6 grid, +-10.2 = cpt13/cpt47), C11
  r72.3/1200 (0.3 grid, +-3.9 = cpt47/cpt73), C12 r81.3/900 (0.4 grid,
  +-5.6 = cpt31/cpt59), C13 r75.5/20 — and one rotated 10-cycle:
  connect cycle [C8.cpt1 C9.cpt23 C10.cpt47 C11.cpt73 C12.cpt59
  C13.cpt1 C12.cpt31 C11.cpt47 C10.cpt13 C9.cpt17]. Zero quantization
  error. Analytic clearance: stars sit on the dart axes with a 17u
  radial white gap above the dart tips (r41 -> r58); nearest petal ink
  is on the OTHER axes — the star wing edge passes r ~67 where the
  petal tip region ends at 65.5, no crossing. tip_in pokes 1u inside
  the white canvas decagon (r59): layer-1 paint covers, accepted noise.
prediction: >
  Wave-4 coverage >= 85% and iou >= 45% (stars are the smallest shapes
  gated so far — band-edge mismatch weighs proportionally MORE, the
  inverse of the wave-3 regime; the dart wave landed 49.5-60 iou at a
  similar scale). Waves 1-3 hold in the eyeball (metric interlock dips
  allowed): nothing new touches the star (r <= 22.6), the darts (same
  axis but radially separated by 17u of white), or the petals
  (different axes, no edge crossing per the clearance check).
falsifier: >
  If the stars render on the star-tip axes (rotated 18 deg), the axis
  assumption is wrong — re-measure the wave-plan shape centers, don't
  nudge. If a star is mis-shaped (self-crossing outline, wrong prong
  spread), a cpt index or the cycle ordering is wrong — Tier-0 witness
  (one pentagram, no field, no rotate) before touching the composite.
  If coverage is high but iou < 40, check WHERE the extra ink is: tips
  past r81 into the field means the prong radius is over-measured. If
  waves 1-3 visibly regress (not just metric interlock), the new rings
  collided with existing geometry — diff the gt shape census first.
```

## Verdict (2026-06-11): WAVE 4 PASSES

Wave-diff: wave-4 coverage 98.3% (predicted >= 85), iou 42.4% —
slightly under the predicted >= 45 but above the < 40 falsifier line.
Pre-stated expectation: ten navy pentagrams on the dart axes, one point
aimed at the medallion center, iou shortfall showing as fat edges, not
misplacement. The sbs + per-star zoom match it exactly: orientation,
axis, position, and the 10-vertex outline all read as the reference;
our star limbs are slightly fatter than the reference's band-eaten
ones (the predicted mechanism — at this size the band-edge mismatch
weighs proportionally more than any wave so far).

Waves hold: wave-1 89.7/70.7 (unchanged), wave-2 93.1/49.5 (unchanged),
wave-3 96.0/73.9 (iou 75.3 -> 73.9, metric interlock from the adjacent
star ink inside the dilated petal envelope; eyeball clean).

Census: gt shapes 181 -> 197. +10 layer-1 10-gons (the pentagrams,
theta 18.2 mod 36, equal areas — exact rotational replication, Tenet
8). +6 are the new blueprint circles C8-C13 emitted as construction
`circle` entries, not faces — benign.

Two notes for later stages: (a) star color is navy #132A61 via the
layer==1 fill; the wave plan calls these deep_navy #262E3D — Stage 2.
(b) Limb fatness: if a future structure pass wants tighter iou here,
the lever is the valley radii (C9/C11 inward by ~1u), but the eyeball
gate does not ask for it.

Next: wave 5 — 10 cyan shapes at r_frac 0.295, the first inner-flower
(flower 2) wave — iter-47.
