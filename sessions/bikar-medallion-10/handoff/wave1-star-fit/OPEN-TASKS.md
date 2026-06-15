# Medallion-10 — Open Tasks Ledger (durable; survives /clear)

Plain-English purpose: the in-session task list (#23–#54) does NOT survive a session
clear. This file is the durable record of every OPEN task's full intent, so nothing is
lost when the session is cleaned. The CLOSEOUT-PROMPT.md is the *driver* (what to do
next); this file is the *source of truth* (what each task actually means). When a task
closes, move it to the "Closed" section with the commit/decision that closed it.

Snapshot date: 2026-06-15. Open: #23 #27 #31 #42 #45 #46 #48 #53 #54.

═══════════════════════════════════════════════════════════════
DEPENDENCY ORDER (read this before picking work)
═══════════════════════════════════════════════════════════════
The keystone is #53. Most "simplify" tasks chain behind its fuse landing:

  #53 (push 50897af → deploy → step 4 portal fuse)
    ├─ unblocks → #45 (unique-shape inventory becomes meaningful once petals
    │              fuse to one shape instead of 2–3 shards)
    ├─ unblocks → #46 (flower/rosette grouping reads fused shapes, not fragments)
    └─ #48 (rim-band exclusion) is INDEPENDENT — local clusterer fix, no push needed

  #42 (simplification UX umbrella) is blocked-by #45 + #46 + #48 — it closes LAST,
       after the three it umbrellas are done.

  #31 (confirm /waves+/inspect read wave-plan authority) — INDEPENDENT, local-only.
  #27 (shape inspector) — INDEPENDENT feature, no dependency, but no work started.
  #23 (re-enable strapwork) — INDEPENDENT, low-pri, deliberately parked.
  #54 ({10/3} re-author) — owner-gated build; does NOT block the color gate.

So the correct ordering is NOT "do #45/#46 locally before the push." It is:
  1. Independent-now: #31, #48 (and #27 if picked up).
  2. Push 50897af → deploy → #53 step 4.
  3. Then #45 → #46 (now meaningful) → #42 (umbrella closes).
  4. Owner-gated, separate: #54. Low-pri parked: #23.

═══════════════════════════════════════════════════════════════
FULL INTENT PER OPEN TASK
═══════════════════════════════════════════════════════════════

#23 — Re-enable strapwork option later  [pending, LOW-PRI, parked]
  What: the woven white-band lattice (strapwork) is currently DISABLED — owner chose
  flat colored-shapes-on-white for now (2026-06-14, ISSUES-OBSERVED.md defect #2).
  The `strapwork` block in iterations/71/pattern.bkr is COMMENTED OUT (not deleted),
  with the preserved `suppress_radial 55` threshold (the data-backed value that drops
  the 30–50° diagonal-slash bands if weave returns).
  Closure: re-enable only when the owner asks for the weave phase. Until then this is
  a deliberate park, not a gap. Nothing to lose — the block + threshold are preserved
  in-file with a re-enable note.

#27 — Interactive original↔final shape inspector  [pending, INDEPENDENT, NOT STARTED]
  What: click any sub-shape in the final render and see which WAVE introduced it
  (provenance lookup, the inverse of /waves). Distinct from /simplify (which groups
  shapes) — this is per-face "where did THIS come from."
  Status: no work started, no next-step defined. This is the one genuinely
  under-specified open task. Enabling data already exists: data-wave provenance ships
  in bikar 35c96d6 (each face carries its introducing wave). So the inspector is a
  portal-read feature on an attribute that already renders.
  Closure: portal page that reads data-wave on click → highlights + names the wave.
  Pick up after the #53 cluster, or anytime — it's independent.

#31 — Confirm /waves + /inspect read the wave-plan as authority  [CLOSED 2026-06-15]
  What: verify both portal pages source color + count + band from the AGREED
  wave-plan (session.json authority), not just from face position. A position-only
  read would silently drift from the owner-approved plan.
  CLOSED: traced both pages in tools/wave-plan-server.py.
    • waves_html() (L1316): plan = json.loads(wave-plan.json); passed = session()
      .waves_passed. Every card's colour/count/where (band) reads from the plan dict
      (w.get("color"), w.get("real_shape_count"...), w.get("where")) — NOT face position.
    • inspect_html() (L1685): plan = json.loads(wave-plan.json); each clickable hotspot
      carries data-wave=n + colour from the plan's wave entry. The click→wave readout
      reports data-wave (plan authority). Shape x/y/area_px is used ONLY to PLACE the
      hotspot on the photo; the WAVE it reports is the authoritative plan assignment.
      Right (render) pane is an honest "coming soon" placeholder (matcher task #26), not
      a position-derived guess.
  Verdict: neither page does a position-only read; no drift from the owner-approved plan.

#42 — Simplification UX umbrella  [pending, BLOCKED-BY #45 #46 #48]
  What: the dedicated post-waves phase to find the pattern's true shape vocabulary.
  This is the umbrella over #45 (inventory), #46 (groupings), #48 (rim-band filter).
  Closure: closes LAST, only when #45 + #46 + #48 are all done. Do not try to close
  it early — it's the rollup, not a standalone unit.

#45 — Unique-shape inventory view  [pending, SOFT-BLOCKED by #53 fuse]
  What: "this pattern is built from N shapes" — the headline count. Only meaningful
  AFTER #53's fuse lands: pre-fuse the count is inflated by construction-line shards
  (each petal = 2–3 fragments); post-fuse it's the real designed-shape count.
  Closure: after #53 step 4, the clusterer input is fused shapes; the inventory then
  reports designed shapes. Build the count view on the fused input.

#46 — Detect higher-level groupings (flowers/rosettes/bands)  [pending, BLOCKED by #53]
  What: read the pattern as flowers/rosettes/bands, not loose faces — the next level
  up from #45's flat inventory. Explicitly blocked-by #53's signal (needs fused shapes
  to group, not fragments).
  Closure: after #53 step 4 + #45, group the fused shapes into higher-order motifs.

#48 — Clusterer rim-band exclusion  [CLOSED 2026-06-15]
  What: the 142× "round" class is the outer-rim band (the frame), not a placeable
  shape. The clusterer must filter or split it so the rim doesn't dominate the
  vocabulary as a single bogus 142-count class.
  DIAGNOSIS (corrected #47's "rim band" framing by reading gt.json + render.svg):
    the 142× "round" class is NOT an outer-rim band of arc-slivers — it is the entire
    CONSTRUCTION-CIRCLE family. All 142 type:circle shapes share one concentric center
    (511.6,519.4), all have fill_color=None AND face_class=None, radius_px 40→489 (up
    to the full pattern radius). They are the blueprint geometry (the SVG's 142 <circle>
    elements = every circle in the render, all in the data-layer="-1" group). All 533
    POLYGON faces are filled = the real placeable shapes.
  FIX (producer-side, cluster_shapes.py so every consumer benefits): exclude unfilled
    construction circles (a type:circle with no fill_color AND no face_class) from the
    vocabulary BEFORE clustering. Result: 675 faces → 533 placeable → 35 canonical
    classes (was 36 with the bogus 142× k00). clusters.json gained n_placeable +
    n_excluded_frame. Inline Tenet-18 self-check + partition assert updated.
  VISUAL VERDICT (Tenet 24/25): GET /simplify → 35 shape cards, ZERO "round" cards,
    ZERO circle-svg silhouettes; card counts 40×/30×/20×/10× (10-fold). Expectation
    written before fetch, matched exactly.
  REGRESSION (Tenet 18): iterations/71/wave-ghosts/test_cluster_frame_exclusion.py —
    regens then asserts no circle class in vocab, n_excluded_frame==unfilled circles,
    n_placeable==filled faces, partition total. GREEN.
  Feeds #42.

#53 — Authored-shape id per face (THE KEYSTONE)  [in_progress]
  What: tag each fragmented face with the .bkr unit it belongs to, so /simplify fuses
  petals (one shape) instead of listing construction-line shards (2–3 fragments).
  Done: steps 1–3 — contract row, engine thread (data-authored-region +
  evidence.authored_region in girih-tiles.ts/evaluator.ts/gt-emitter.ts/
  svg-renderer.ts), Tier-0 witness (packages/core/tests/render/authored-region-id.test.ts,
  6 green). Committed bikar feat/divide-offset 50897af. Core builds clean, full suite
  980 pass + 3 xfail. Visually verified. Plan: bikar/.claude/plans/
  authored-region-id-fuse-fragments.md.
  REMAINING — step 4 (BLOCKED on push): /simplify consumer fuses faces by
  data-authored-region BEFORE clustering (sacred-patterns portal pre-pass). Blocked
  because the portal can't render the attr until 50897af is PUSHED + deployed
  (Cloudflare). Plus the canonical sacred-patterns contract amendment (currently
  mirrored only in bikar/docs/dsl-metadata-contract.md).
  Decision discipline: layers onto the existing face-extractor / region-identity
  decision doc (Tenet C5) — do NOT open a new tag.
  Closure: push 50897af → deploy → author the portal fuse pre-pass → verify the
  /simplify vocabulary count drops from fragment-count toward designed-shape-count,
  with "tap to find it" landing on a real shape (Tenet 25 recorded visual verdict).

#54 — Re-author wave-1 central star as {10/3}  [pending, OWNER-GATED, NOT a blocker]
  What: owner note from the structure re-gate (2026-06-15, "Its one shape, but its
  10/3"). The wave-1 build currently uses a hankin star (divide C0 into 10 offset 18,
  rays from decagon edge midpoints); the owner's note suggests a {10/3} star-polygon
  construction density instead. This is a construction-density REFINEMENT of an
  already-APPROVED structure gate — it does NOT reopen the gate and does NOT block the
  color gate.
  Closure: owner-gated build. Re-author wave-1 as a {10/3} star, render, surface for
  the owner to compare against the hankin version. Only when the owner picks the color
  phase or explicitly asks for #54.

═══════════════════════════════════════════════════════════════
CLOSED (move tasks here as they close, with the commit/decision)
═══════════════════════════════════════════════════════════════
#30 — Wave-1 = single central shape: CLOSED 2026-06-15. Owner PICK A via
  wave1-regate-picker ("one shape — the lone central star," note "Its one shape, but
  its 10/3"). session.json stage_gates.structure.approved=true, approved_at_iter=71.
  The 10/3 note spun off as #54.
