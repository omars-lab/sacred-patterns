---
iteration: 31
date: 2026-05-28
skill: iterate-construction-hypothesis
detector_untouched: confirmed
gap_targeted: >
  iterations/30/visual-verdict.md confirmed the chord-overlay philosophy
  produces ZERO girih strapwork bands, ZERO explicit star tiles, and ZERO
  decagon rosette frames — so A6_pass_ratio = 0.0 (0 of 18 expected shapes
  matched). The baseline (input/baseline.json) expects a girih-tile
  vocabulary: a central star-v20 at dist 0.00-0.07 (qiyas type
  hankin_star), girih_rhombus shapes at 0.25-0.39, and v6/v8/v10/v14/v20
  star_polygon tiles across the rosette + transition zones.
construction_hypothesis: >
  A girih-tile decagonal medallion — built from bikar's native `girih`
  primitive (packages/core/src/kernel/girih-tiles.ts, all 5 Lu &
  Steinhardt tiles with DECORATION_PAIRS strapwork) — produces the
  explicit star + rhombus + decagon vocabulary the baseline expects, which
  the chord-overlay construction categorically cannot. This is NOT a
  parameter tweak of the existing construction; it is a different
  construction philosophy that already exists as a shipped DSL primitive.
bkr_change: >
  iter-31 is the Tier-0-first smallest single idea (Tenet 17): place ONLY
  the central decagon girih tile (`girih decagon <edgeLength>`) at origin,
  with `voids detect` + classify rules, and measure against baseline. The
  central decagon's internal {10/3} decoration produces a star-v20-like
  center (maps to inner-star--star-v20, dist 0.00-0.07) and girih_rhombus
  decoration faces. Do NOT add the attachment ring yet — prove the central
  tile renders + audits before composing the full medallion (iter-32+).
predicted_lift: >
  A6_pass_ratio 0.0 -> >0 (expect to newly match inner-star--star-v20 and
  at least one girih_rhombus / polygon-v0 inner-star shape). Composite
  score may DROP transiently because the single central tile covers far
  less area than the full chord-overlay (A4 coverage falls, A2 fold may
  weaken) — that is expected for a Tier-0 single-tile probe and is NOT a
  falsification. The signal to watch is A6: does ANY girih shape match a
  baseline expected_shape that the chord-overlay never could?
predicted_cost: >
  Low. Single `girih decagon` statement + classify rules. The primitive is
  shipped (Girih-Decagon.bkr starter demos it). Render via bikar CLI,
  rasterize with magick, svg-audit via QIYAS_IMAGE=...:dev (v0.1.1 not
  local). One render, one audit.
prior_art_searched: >
  Lu & Steinhardt 2007 (girih tiles, decagonal quasicrystal medallions) —
  the construction philosophy the medallion-10 reference uses, confirmed
  visually in iterations/30/visual-verdict.md. bikar girih-tiles.ts
  implements the exact 5-tile set with strapwork DECORATION_PAIRS.
related_memory: >
  feedback_a6_baseline_construction_philosophy_mismatch (UPDATE 2026-05-28:
  girih is NOT owner-gated, the primitive is shipped — the ceiling is an
  actionable construction iteration, not a present-options decision).
  feedback_check_mechanism_already_implemented (grep the module before
  declaring a philosophy unreachable). Tenet 17 (prove the primitive
  before composing), Tenet 27 (visual-verify before reading the score).
---

## iter-31 — central girih decagon tile (Tier-0 probe)

The single smallest construction idea: replace nothing yet, just stand up
ONE central `girih decagon` tile and confirm bikar renders it and qiyas
sees girih vocabulary in it. This is the foundation the full medallion
(iter-32+ ring attachment via `attach <name> edge <N>`) will compose onto.

**Expected visual (write BEFORE looking — Tenet 27/24):** a single decagon
outline centered at origin, with internal {10/3} strapwork decoration lines
forming a 10-pointed star at the center and a ring of rhombus/kite
decoration faces between the star and the decagon edge. White-band
interlace is NOT expected at this stage (no strapwork weave authored yet) —
just the tile + its decoration faces.
