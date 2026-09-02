# Iteration 47 — Hypothesis

```yaml
attempt: 47
date: 2026-06-11
stage: structure
target_wave: 5
gap_targeted: >
  Wave 5 — 10 cyan shapes at kind_r_frac 0.295 on the STAR-TIP axes
  (0 deg mod 36, the petal axes) — sits at 71.6% coverage / 39.7 iou on
  the iter-46 render: the girih field's own cobalt pentagon tiles
  partially fill the envelopes, but the reference shape is larger and
  reaches further out. Visual identification (mask zoom of id 214): a
  radially-elongated pentagon pointing OUTWARD with a notched base — a
  6-vertex shield, same topology as the wave-3 petal, pointing the
  other way. Measured model (mask + contours + width profile across 3
  shapes): base-mid (axis, 69.5u), base corners (+-9.3 deg, 75u),
  shoulders (+-9 deg, 86u), apex (axis, 104.3u). Shoelace area 594.8u^2
  vs measured ~585u^2 (bands eat edges — right direction, 1.5% over).
one_idea: >
  An arrowhead ring in layer 1, same standalone-closed-cycle technique
  that passed waves 2-4: four new blueprint rings — C14 r69.5/10
  (base-mid, axis = cpt0), C15 r75/1200 (0.3-deg grid, +-9.3 =
  cpt31/cpt1169), C16 r86/40 (9-deg grid, +-9 = cpt1/cpt39), C17
  r104.3/10 (apex) — and one rotated 6-cycle: connect cycle [C14.cpt0
  C15.cpt31 C16.cpt1 C17.cpt0 C16.cpt39 C15.cpt1169]. Zero quantization
  error (every offset divides into gcd(36, delta) grids). Clearance:
  4u radial white gap above the wave-3 petal tip (65.5 -> 69.5, same
  axis); nearest wave-4 pentagram ink is >= 3 deg / 4u away at every
  radius (wing-valley-prong edges at 7.8-14.1 deg in our frame vs our
  edge at 9-9.3 deg, radially separated). The whole shape lives in the
  field zone — layer-1 paint covers field tiles and bands underneath,
  same accepted regime as the petal tips and pentagrams.
prediction: >
  Wave-5 coverage >= 95% (from 71.6) and iou >= 60% (from 39.7; the
  shape is petal-sized — same band-mismatch regime as wave 3, which
  landed 73.9-75.3). Waves 1-4 hold in the eyeball; wave-4 iou may dip
  a few points (metric interlock: our arrowhead corner ink sits inside
  the dilated pentagram envelopes' neighborhoods).
falsifier: >
  If the arrowheads render on the dart axes (rotated 18 deg), the axis
  read is wrong — re-measure, don't nudge. If an arrowhead fails to
  close (gt layer-1 6-gon count does not rise by 10), the 6-cycle hit
  a snapping defect — Tier-0 witness (one arrowhead, no field) before
  touching the composite. If coverage lands high but iou < 50, check
  WHERE: extra ink at the apex means the apex radius is over-measured
  (the reference apex may stop at the white band around the teal
  field star at ~104); missing ink at the base notch means the base-mid
  vertex is really an inward arc — consider an arc edge as the NEXT
  iteration's single idea. If waves 1-4 visibly regress beyond metric
  interlock, diff the gt shape census first.
```

## Verdict (2026-06-11): WAVE 5 PASSES

Wave-diff: wave-5 coverage 98.7% (predicted >= 95, from 71.6 baseline),
iou 52.3% — under the predicted >= 60 but above the < 50 falsifier
line, so the eyeball governs. Pre-stated expectation: ten navy
arrowheads pointing outward on the star-tip axes, filling the gold
envelopes; iou loss as slight over-size at the edges (model ran 1.5%
over) plus band-edge mismatch — not misplacement or wrong orientation.
The sbs (and render-wave.png) match it: all ten envelopes contain an
outward-pointing 6-vertex shield on the correct axis, correct
orientation, correct radial extent. One observation needed debunking:
a fractional sub-crop of sbs.png appeared to show an unchanged teal
pentagon — sbs panels are wave-REGION crops, so fractional geography
differs from the full medallion; a pixel-diff of iter-46 vs iter-47
renders put every changed pixel (20,522) exactly in the arrowhead
radial band (r 112-188px), and a direct render crop at the east
arrowhead shows the navy shield correctly shaped and placed. The
cyan/teal in the sbs left panel is adjacent field tiles inside the
wave-region crop, not the arrowhead fill.

Waves hold: wave-1 89.7/70.7 (unchanged), wave-2 93.1/49.5 (unchanged),
wave-3 96.0/72.7 (iou 73.9 -> 72.7, metric interlock), wave-4 98.3/39.2
(iou 42.4 -> 39.2, predicted interlock: our arrowhead corner ink sits
inside the dilated pentagram envelopes; eyeball clean).

Census: gt shapes 197 -> 211. +10 layer-1 6-gons (the arrowheads,
theta 0 mod 36, equal areas — exact rotational replication, Tenet 8).
+4 are the new blueprint circles C14-C17 emitted as construction
`circle` entries, not faces — benign.

Stage-2 note: arrowhead fill is navy #132A61 via the layer==1 rule;
the wave plan calls these cyan #52A2C4. Joins the existing Stage-2
backlog (wave-3 periwinkle, wave-4 deep_navy).

Next: wave 6 — 10 navy shapes at r_frac 0.348 on the dart axes
(theta ~= 18.7 mod 36, mean area ~1091px^2 ~= 639u^2) — iter-48.
