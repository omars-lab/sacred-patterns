# Medallion-10 — issues observed & how we overcame them (with code pointers)

Plain-English purpose: this is the memory the owner asked for on 2026-06-14 —
*"why do we not remember the issue?"* Every white-line / outer-band defect we hit,
one line each: what it looked like, the root cause, the fix, and where the fix lives.
The point is that the NEXT session reads this before re-investigating from scratch.

## White / radial-line defects (the recurring family)

| # | Symptom (what the eye sees) | Root cause | Fix | Code pointer |
|---|---|---|---|---|
| 1 | Faint grey/white **hairline circles** across the whole render in rasterized output (cairosvg / CLI `--image`), invisible in the web UI | Blueprint construction circles `data-layer="-1"` are hidden only by the web UI's runtime JS (`applyLayerVisibility` sets `display:none`); non-JS rasterizers never run that JS, so 80,865 px (~8% of a 1024² raster) of white `<circle stroke="#FFFFFF">` leaked in | Emit `style="display:none"` on `<g data-layer="-1">` at SVG-build time so EVERY rasterizer honors it | bikar commit `deef89f` — `packages/core/src/render/svg-renderer.ts` (blueprint group emit). **FIXED + verified present in iter-71 render.svg** (`data-layer="-1" style="display:none"`, the 142 blueprint circles sit inside it and do not leak). |
| 2 | Bold **radial white spokes / thin radial white strip lines** slashing outward through the outer band (waves 16+); reference has a fine *tangential* woven lattice instead | The white lines ARE strapwork bands (proven 2026-06-14: a background→magenta swap left them white = strapwork, not background gaps). They are NOT true radial spokes (<22°) — measuring by band **centerline** (not raw quad vertices, the earlier measurement bug) shows ZERO bands <22° in the outer band. The histogram is **bimodal**: ~60 "diagonal slash" bands at 30–50° from radial + 90 genuine tangential bands at 60–90°, with a clean empty gap at 50–60°. The eye reads the 30–50° diagonals as radial slashes. `suppress_radial 22` was too narrow to catch them. | **✅ RESOLVED 2026-06-14 (owner decision) — strapwork DISABLED.** Owner explored "straps for free" (white showing through inter-tile gaps); render proof showed the faces tile **edge-to-edge with no gaps**, so dropping strapwork yields a flat color field (no negative-space lattice). Owner chose the flat-color aesthetic for now: colored shapes on white, no painted lattice, no slashes. The `strapwork` block in `pattern.bkr` is **commented out (not deleted)** with a one-line re-enable note + the preserved `suppress_radial 55` guidance (the data-backed threshold that drops the 30–50° slashes if weave returns). Re-rendered iter-71 (render.svg/png/gt.json): `data-strand=0` (was 330), 652 faces / 675 shapes unchanged, eyeball confirms no white slashes. | overlays `iterations/71/pattern.bkr` (commented `strapwork` block + re-enable note); engine bikar `packages/core/src/dsl/evaluator.ts` `filterRadialEdges` (preserved for re-enable); design `bikar/docs/design/strapwork-radial-suppression.md`; eyeball `iterations/71/render.png`, `radial-options/COMPARE-strap-vs-nostrap.png`. |

### Why #2 kept coming back (the answer to "why don't we remember")

Bug #1 was recorded properly — a commit with a root cause, a measurement (80,865 px),
and a one-line subject a `grep` finds. Bug #2 was **never recorded as a bug**: every time
it surfaced it was filed as a *band-width tuning note* —

- iter-35: strapwork band *weight* too fine → bolder straps (a `width` knob, +0.03 pixel-sim)
- iter-69: owner `band_width` verdict → backlog
- iter-71 (current frozen best): `width 8 → 10` (a `width` knob again)

…so it lived as a recurring **symptom adjustment** (the Tenet-7 trap) with no entry in
`docs/lessons.md` or `docs/engine-issues.md`. No durable record → every session rediscovers
it. This file + the bikar `engine-issues.md` entry close that gap.

## Bookkeeping / portal defects (this session)

| # | Symptom | Root cause | Fix | Code pointer |
|---|---|---|---|---|
| 3 | `/iterate` build page returned empty body / connection reset | A wave stamped with `owner_verdict: null` (exactly what the re-gate stamp writes); page read `gate.get("owner_verdict", {}).get("state")` — the `{}` default only applies when the KEY is absent, so explicit `None` slipped through and `None.get("state")` raised | `gate.get("owner_verdict") or {}` at both read sites | `sacred-patterns/tools/wave-plan-server.py` ~L560, L1244; regression test `tools/tests/test_portal_none_verdict.py` (Tenet 18) |
| 4 | Progress filmstrip collapsed from a full catalog to 2 thumbnails | `rebuild_progress_strip()` dedups by iteration; all built waves share iter-71 → collapsed to 2 panels | By design after redesign: 2-panel strip = reference + latest render; per-wave progress moved to the green/white **squares bar** | `wave-plan-server.py` `iterate_html()` squares bar; `rebuild_progress_strip()` L369 |

## Premise errors corrected (the C1/C2 trap, repeatedly)

The "remaining work" label was wrong at every checkpoint; only reading the iter-71
`gt.json` tree directly gave truth (Tenet C1/C2):

- "converged" → wrong (22-wave plan had unbuilt waves)
- "15/22 unbuilt" → wrong (waves 16, 17 were already built, only un-stamped)
- "wave 18: 2/10 emit, 8 MISSING" → **wrong** (2026-06-14: all 10 `.royal_wave` 20-vertex
  faces emit at normalized r 0.821, census-equal to the 10 reference royal medallions at
  ref-norm 0.803-0.812; the survey misread the radial band by normalizing against a
  different radius). Wave 18 is an **invocation-gap (stamp-only)**, not a geometry gap.
  Proof: `iterations/71/wave18-check.png` (10 markers, evenly placed).

- "wave 19: 10/20, half navy missing" → **wrong** (2026-06-14: all 20 `.deep_navy_wave`
  faces emit at render renorm r 0.834, paired around the 10 medallions (alternating
  25.1°/10.9° gaps = 10 pairs), census-equal to the 20 reference `deep_navy` shapes at
  renorm r 0.81–0.82. The survey misread the band — TWO adjacent navy rings sit at renorm
  r 0.834 (wave 19) and 0.864 (wave 20); it counted only one. Wave 19 is an
  **invocation-gap (stamp-only)**. Proof: `iterations/71/wave19-check.png`,
  `wave19-zoom-top.png` (markers land on dark-slate #353941 navy star-faces, NOT royal
  #2661BF, NOT white lattice). Stamped `waves_passed["19"]` 2026-06-14.

**Lesson:** normalize BOTH frames by their own outermost wave before comparing radial
bands — the gt render (R≈369, content reaches r_frac 1.245) and the wave-plan photo
(diam 738, ref shapes cap at r_frac 0.943) do NOT share a normalization.

## Outer-edge waves 20-22 — ALL invocation-gaps (the "color gap" framing was ITSELF a premise error)

**RETRACTED (2026-06-14, second pass — Tenet C2):** the first pass this session concluded
waves 20-22 were "GENUINE color gaps" (geometry right, color wrong). **That was wrong — a
THIRD instance of the same radial-census misattribution trap** that already bit waves 18 and
19. Verifying by **layer attribute** (not by radial band) overturned it: all three waves emit
the correct color and were already correctly built. They were invocation-gaps (stamp-only),
exactly like 16/18/19.

| Ref wave | Reference (renorm r, hex) | Render emits (by LAYER, decisive) | Verdict |
|---|---|---|---|
| 20 | 20 navy `#283B6E` @ 0.879–0.889 (darts on dart axes) | 20 layer-1 navy `#132A61` @ renorm r 0.846–0.851, paired 10-fold | ✅ census-equal; ref maps to palette navy (RGB dist 30 vs royal 89.5) |
| 21 | 39 real deep_navy `#404249` @ 0.870–0.915 (slivers) | 40 layer-2 deep_navy `#3C3F47` @ renorm r 0.834–0.864 | ✅ census-equal (40 vs 39 = ref drops 4 fragments from 43; construction emits full 40); ref maps to deep_navy (dist 5.4) |
| 22 | 30 navy `#25396C` @ 0.961–1.000 (rim triplets) | 30 layer-1 navy `#132A61` @ renorm r 0.917–0.936, 10 triplets | ✅ census-equal; ref maps to navy (dist 25.9 vs royal 92.1) |

**Why the first pass misfired (the recurring lesson, now THIRD occurrence):** a radial-band
census at r≥0.90 returns a MIX of layers — the wave-22 navy OVERLAY tiles (layer 1) AND the
base-field royal `#2661BF` decagon faces (layer 0) that fill the GAPS *around* them. Counting
"30 royal at r≥0.95" attributed the base-field royal to wave 22, when wave 22's own tiles are
navy. **The fix to the analysis, not the pattern: census by `data-layer` (each wave overlay is
assigned a layer that encodes its color — layer 1=navy, 2=deep_navy, 3=cobalt, 4=royal,
5=periwinkle, 6=cyan_2; layer 0=base field, sides-colored). The trailing `layer 0` after a
wave's connects is the RESET, not that wave's layer.**

**Color-family proof (RGB Euclidean triage):** each reference outer hex maps cleanly to an
EXISTING palette family already assigned via the wave's layer — w20 #283B6E→navy (30),
w21 #404249→deep_navy (5.4), w22 #25396C→navy (25.9); royal is 89-125 away from all three.
No new palette color, no `classify where r_frac`, no engine change needed. (The earlier
"premise checked: `r_frac` predicate doesn't exist" finding stands and is still true — it just
turned out to be irrelevant, because no radius-gated coloring was needed.)

**Eyeball proof (Tenet 24/25, BEFORE stamping):** `iterations/71/wave22-check.png` (30 markers =
10 triplets on navy rim tips), `wave2021-check.png` (20 magenta on navy dart-lobes + 40 green on
deep-navy slivers). All land on correctly-colored faces matching `input/reference-analysis/wave-plan/wave-{20,21,22}.png`.

**Outcome:** waves 20/21/22 stamped `waves_passed["20"/"21"/"22"]` 2026-06-14 → **22/22
structure waves stamped.** owner_verdict null on all (owner portal eyeball + stage-gate approval
still pending — do NOT self-approve `stage_gates.structure.approved`).

**Meta-lesson (the trap bit THREE times — 18, 19, 20-22):** when censusing a multi-layer
medallion render, the FIRST query must be by `data-layer` / `data-face-class`, NOT by radial
band. Radial bands overlap across layers at the outer edge (overlay tiles + base-field gap-fill
share a radius), so a radial census systematically misattributes base-field faces to the overlay
wave. This is now the dominant failure mode of this reconstruction's verification step.

---

## 2026-06-15 — The girih background DIVERGES the image (reference is shapes-on-WHITE)

**Done:** Owner observed the generated blue background "seems to be diverging the image more than
helping" and asked for an image-diff at wave 22 without the background. Ran it — owner is RIGHT, with
three independent confirmations:
1. **Metric:** RMSE vs the aligned reference photo — wave-22 (NO backdrop) = **0.368**, wave-23 (WITH
   backdrop) = **0.404**. Lower = closer; the backdrop measurably moves us AWAY from the reference.
2. **Eye (Tenet 24):** clean 3-up (reference | shapes-only | +backdrop). The reference is a delicate
   10-lobe FLOWER with shapes on white; the +backdrop render paints a solid blue CONVEX DECAGON that
   (a) overshoots the scalloped flower edge and (b) buries the shapes under heavy deep_navy/cobalt
   field-fill. `/tmp/edge-compare.png`, `/tmp/diff-3up.png`.
3. **DEFINITIVE — color-sampled the actual photo:** aligned reference between-shape gaps at
   (300,300) and (700,700) = `srgb(251,251,252)` = **WHITE**; corners = white. The reference has
   WHITE between the shapes, NOT a blue field. The girih background fabricates a field that simply
   isn't in the photo.

**How the background is generated** (so the next session doesn't re-derive it): master
`iterations/71/pattern.bkr` line 731 `girih field decagonal 62 shells 1 pockets star` — an engine
primitive (`evaluateGirihField` → `growGirihField`, bikar `packages/core/src/dsl/evaluator.ts`
~2477) that grows a GAP-FREE convex decagonal girih tiling (5 tile types, shells 1, edge 62) — then
tail rules lines 786–793 `fill void where sides == N color …` paint those field faces by polygon
side-count. Net: a fully-painted convex decagon. That convex fill is the divergence — the reference
is open/scalloped/white-ground.

**Left:** the decision — drop the girih backdrop (wave 23) entirely? The reference is shapes-on-white,
which wave-22 ALREADY is, so wave-22 IS the better match. Surfaced to owner (do not change wave plan
w/o owner). If owner says drop it: revert the wave-23 block + the tail backdrop fills, set MAX_WAVE
back to 22, drop the wave-23 wave-plan.json entry + card, regenerate.

**Next:** await owner go/no-go on dropping the backdrop.

**Held:** bikar 0 / qiyas 0 / sacred-patterns 1 (tools/wave-plan-server.py, unchanged this sub-tick).

---

## 2026-06-15 — Cumulative wave-N.bkr family + portal "Our build"/"Just this wave" wiring

**Done:** (1) /waves portal code-diff tile switched from per-iteration pattern.bkr diffs to
CUMULATIVE wave-(n-1).bkr → wave-n.bkr diffs (each card now shows exactly the lines wave n
added); "Our build" tile serves cumulative wave-{n}-build.png (#34). (2) generate_wave_files.py
now keys the slicer off the `wave N` STATEMENT, not `# Wave-N overlay` comment markers — the
master folds wave-2's blurb into wave-1's comment block (no standalone `# Wave-2 overlay`), so
the comment-marker slicer silently DROPPED wave 2 (wave-1.bkr===wave-2.bkr, empty diff). (3)
"Just this wave's shapes" iso tiles were STALE legacy artifacts (a sliver for wave 1) — now
generated from the same cumulative render by ghosting every face whose `data-wave != n` to white
(data-wave-authoritative, Tenet 23). (4) Two invariants frozen as self-checks (Tenet 18):
all-22-waves-present + monotonic + wave-22-tail==master (pre-render); wave-1 build==iso
pixel-identical (post-render, magick compare AE=0).

**Left:** nothing on this thread — portal UX fully reflects the cumulative family, verified live.

**Next:** idle — unfired trigger = owner go-ahead on one of: (a) #30 wave-1 structure RE-GATE
(owner's lone-star choice changed wave-1's PRESENTATION only; geometry unchanged, wave-22===master,
all 22 still gated PASSED — re-gate may be a no-op confirmation, but I must NOT self-approve
`stage_gates.structure.approved`); (b) commit the HELD portal edit (tools/wave-plan-server.py).

**Held:** bikar 0 / qiyas 0 / sacred-patterns 1 — tools/wave-plan-server.py (code-diff →
cumulative wave-family switch). Held per GHA-budget tenet (push burns billable minutes); single
docs-adjacent code edit, batch with the next portal change or push on owner go-ahead. The
generator + 44 PNGs live in the Dropbox session dir (not git-tracked), already in place.

**Verified (Tenet 24/25):** wave-1 = lone navy star (build==iso, pixel-identical); wave-2 iso =
10 darts only (no star); wave-7 build = shapes-on-white no backdrop; wave-14 iso = 20-shape ring;
wave-22 build = full medallion + girih backdrop. Portal reloaded, all tiles correct.

## 2026-06-15 — Backdrop split into its own final wave 23 (owner decision)

**Done:** Owner reported wave 22 "jumps" — it dumped the ENTIRE blue girih backdrop at once
alongside its own 30 navy shapes (every earlier wave was shapes-on-white; wave 22 suddenly = the
whole blue field). Owner DECIDED (AskUserQuestion): "Backdrop as its own final wave 23." Moved the
`girih field decagonal 62 shells 1 pockets star` statement from under `wave 1` (line 440) to a new
`wave 23` block placed just before `voids detect` (master `iterations/71/pattern.bkr`). Bumped
`MAX_WAVE = 22 → 23` in `generate_wave_files.py` (the `_scope_tail_line` backdrop-deferral threshold
keys off MAX_WAVE, so the tail `fill void where sides==…` rules now auto-reveal at wave 23, stay
deferred for 1..22). Regenerated the family: 23 build + 23 iso PNGs. Field-statement move is
geometry-neutral — `_girih_hexagon_star` is referenced ONLY in the tail (classify .pocket / fill
void where source==), never by intermediate wave geometry, so circle-numbering (C129…C141 in wave
22) is unchanged.

**Left:** nothing on this thread. Owner DECIDED (AskUserQuestion, 2026-06-15): "Yes — add a wave-23
card." Added a wave-23 entry to `wave-plan.json` (`kind: "backdrop"`, plain-language `where`, n_waves
22→23) — a PRESENTATION step, not a detected shape-wave, flagged with `kind` + a `note` so it's never
mistaken for reference-detected geometry. `waves_html` special-cases `kind == "backdrop"`: the card
title reads "Wave 23 — the background that fills every gap behind the shapes" (no "271 shapes"), and
the three tiles get backdrop-honest blurbs (no "ringed in orange" / "shapes this wave adds").
Generated `wave-23-crop.png` = the full reference photo (the backdrop is the whole field, nothing to
zoom-crop). Server restarted; `/waves` now renders 23 cards.

**Next:** idle — unfired trigger = owner go-ahead on one of: (a) #30 wave-1 structure RE-GATE (never
self-approve); (b) commit the HELD portal edits (tools/wave-plan-server.py — now 2 edits batched:
prior cumulative-diff switch + this tick's wave-23 card).

**Held:** bikar 0 / qiyas 0 / sacred-patterns 1 — tools/wave-plan-server.py (prior cumulative-diff
switch + the wave-23-card special-casing, batched into one held unit). Held per GHA-budget tenet;
push on owner go-ahead. wave-plan.json (+wave-23 entry) and the master pattern.bkr / generator /
44→46 PNGs all live in the Dropbox session dir (NOT git-tracked) — already in place, no push needed.

**Verified (Tenet 24/25):** wave-22-build = decorative shapes on WHITE (no blue backdrop, gaps
white); wave-23-build = full medallion + backdrop, AE=0 vs master render; wave-23-iso = girih
backdrop field ALONE (decorative-shape positions ghosted white); self-check OK (23 waves, monotonic,
wave-23 tail==master); wave-1 build==iso pixel-identical. Master full render unchanged (4134 paths,
AE=0 vs pre-edit). PORTAL: /waves HTML renders the wave-23 card — title "Wave 23 — the background
that fills every gap behind the shapes", all 3 tiles (crop/build/iso) wired, "of 23 waves" count,
backdrop blurbs present; 3-up tile montage eyeballed (full photo | finished medallion | blue field
alone). Server health 200 after restart.

## 2026-06-15 — Girih backdrop DROPPED (owner decision: "doesn't seem useful for our current objective")

**Done:** Owner asked to understand how the girih backdrop was built and whether it's useful, then
decided to drop it ("it looks nice, but it doesnt seem useful for our current objective"). The
decision was evidence-backed: the reference is shapes-on-WHITE (color-sampled — between-shape gaps =
srgb(251,251,252), corners white; NO blue field in the photo), and the convex girih field overshot
the scalloped flower edge and DIVERGED the image (RMSE 0.404 with backdrop vs 0.368 without; lower =
closer to reference). Reverted the whole backdrop thread: (1) master `iterations/71/pattern.bkr` —
removed the `wave 23` block + `girih field decagonal 62 shells 1 pockets star` statement, removed the
backdrop `classify` rules (`.pocket where source==_girih_hexagon_star`, the sides-based
`.deep_navy/.royal/.turquoise/.cobalt/.navy` block) and the geometric backdrop `fill void where
ring/source/sides` rules, each replaced with an explanatory removal comment; the decorative `fill
void where layer == N` rules KEPT (they self-scope to the 22 waves). (2) `generate_wave_files.py` —
`MAX_WAVE = 23 → 22`; rewrote the now-stale backdrop-deferral comments (`_scope_tail_line` survives
as a harmless guard — no geometric rules remain to defer); dropped the `field_note` backdrop wording
from the wave-file header. (3) `wave-plan.json` — removed the wave-23 backdrop entry, `n_waves` 23→22.
(4) `tools/wave-plan-server.py` (git-tracked, HELD) — removed the dead `kind=="backdrop"` card
special-casing (title override + `backdrop_blurbs`). (5) Deleted stale wave-23 artifacts
(`wave-23.bkr`, `wave-23-{build,iso,crop}.{png,svg}`) and the `wave-22-nobackdrop.bkr` scratch.
Regenerated the 22-wave family (22 build + 22 iso PNGs).

**Left:** nothing on this thread. The girih-field primitive itself is UNTOUCHED in the engine
(`evalGirihField` / `growGirihField`) — it remains a reusable engine capability for FUTURE patterns
with a genuine dense girih ground; it's just not invoked by this medallion (recorded so it isn't
re-derived).

**Next:** idle — unfired trigger = owner go-ahead on one of: (a) #30 wave-1 structure RE-GATE (never
self-approve); (b) commit the HELD portal edit (tools/wave-plan-server.py — now batches the prior
cumulative-diff switch + this revert of the wave-23 card special-casing).

**Held:** bikar 0 / qiyas 0 / sacred-patterns 1 — tools/wave-plan-server.py (cumulative-diff switch +
backdrop-card-special-casing now REMOVED; net still one held unit). Held per GHA-budget tenet; push on
owner go-ahead. wave-plan.json, master pattern.bkr, generator, and 44 PNGs all live in the Dropbox
session dir (NOT git-tracked) — already in place.

**Verified (Tenet 24/25):** /tmp/master-nobg.png AND wave-22-build.png both = decorative shapes on
WHITE, gaps white, scalloped silhouette clear, no blue field — matches the shapes-on-white reference.
3081 paths (down from 4134 with backdrop). Generator self-check OK (22 waves, monotonic, wave-22
tail==master); wave-1 build==iso pixel-identical. wave-plan.json validates (n_waves=22, max wave=22,
no backdrop entry). Server + generator py_compile clean. PORTAL restarted (200): /waves renders
exactly 22 cards (max card=22, highest heading "Wave 22"), zero wave-23 card, zero backdrop-card
language ("blue background that fills" → 0 hits). The remaining "girih backdrop" mentions in the HTML
are inside the code-DIFF tiles — the honest recipe diff showing the removal-comment lines I added to
the master, which is correct.

---

## 2026-06-15 — Merge /iterate into /waves (one card per wave)

**Done:** Folded the old `/iterate` review workbench into `/waves` so each wave is ONE card with
everything (owner: "merge the experiences" → "Merge into one page"; "i like the shape highlighting in
iterate more than the inner circle highlights in wave" → "Gold-outlined sbs as hero"). Each per-wave
card now leads with the gold-OUTLINED side-by-side hero (`/gate/{n}/sbs.png` — our build left, photo
right, this wave's shapes ringed gold), then the three close-up tiles (crop / build / iso), a foldaway
"recipe change" diff, a foldaway "history" filmstrip, and the approve / needs-work verdict panel. The
page header gained a row of 22 green progress squares. `/iterate` → 301 redirect to `/waves`; the hub
collapsed its two redundant waves cards into one. `continue_prompt_text` build-view URL updated
`/iterate` → `/waves`. Single edited file: `tools/wave-plan-server.py` (git-tracked, still HELD).

**Left:** nothing on the merge. `iterate_html()` is now dead code (no caller) but left in place — it
shares helpers; removing it is a separate cleanup, not part of this owner ask.

**Next:** idle — unfired trigger = owner go-ahead on one of: (a) #30 wave-1 structure RE-GATE (never
self-approve); (b) commit the HELD portal edit.

**Held:** bikar 0 / qiyas 0 / sacred-patterns 1 — tools/wave-plan-server.py (cumulative-diff switch +
backdrop-card removal + this /iterate→/waves merge; net still one held unit). Held per GHA-budget
tenet; push on owner go-ahead.

**Verified (Tenet 24/25):** Expected one continuous page, each wave a single card with the gold sbs as
the big top image, then 3 smaller tiles, collapsed recipe/history disclosures, an approve/needs-work
box, and 22 green progress squares in the header. Browser-rendered `/waves` matches exactly: header
"The waves, one by one" + "22 of 22 waves are built" + 22 green squares; Wave-1 card shows the gold
8-point star outlined on both halves of the sbs hero, the 3 tiles (photo-crop orange-ringed, build,
iso — build==iso lone star), folded "Show the recipe change" + "Show history (33 steps)", and the
"This wave looks right / Needs work" verdict with plain-language prompt + textarea. Structural
verification via curl: 22 `data-wave-card` real cards (w1..w22; the 23rd hit is the JS selector
string, not a card), 22 heroes, 22 verdict panels, 22 history filmstrips, 22 codediff blocks, 1
progress-squares row, ITERATE_JS wired (1 `api/wave-verdict` POST). `/iterate` → 301 → `/waves`. Hub:
1 `/waves` link, 0 `/iterate` links, old "build, wave by wave" card gone. py_compile clean; portal
restarted (200).

---

## 2026-06-15 — Wave hero made additive (build + ghosted photo), both reveal 1..N

**Done:** Owner saw the merged hero's right (photo) side still showed the WHOLE pattern at
once with this wave gold-outlined — "the right image is also not additive" — and asked for
"an additive view just like we did for /waves". Chosen pairing (AskUserQuestion): **Build +
ghosted photo**. Built it:
- NEW generator `iterations/71/wave-ghosts/build_wave_photo_ghosts.py` — full reference photo
  with everything desaturated + lightened toward grey (#DBDBDB) EXCEPT the cumulative
  shape-disks of waves 1..N (from wave-plan `shapes[].{x,y,area_px}`, disk r = sqrt(area)/2
  ×1.9 so same-band shapes merge), soft mask edge (Gaussian blur 4), cropped to the pattern
  bounding circle (center 386,361 / diam 738) so framing matches `wave-N-build.png`. Output
  `wave-N-photo.png` (512px) ×22. Cumulative reveal is monotonic 0.9%→72.2% (asserted per
  Tenet 18 — mask never shrinks).
- Portal `waves_html()` hero rewired: built waves now show a `.heropair` two-up of
  `/wave-ghosts/wave-{n}-build.png` (left, our build through N) beside
  `/wave-ghosts/wave-{n}-photo.png` (right, photo revealed through N), replacing the
  gold-outline `/gate/{n}/sbs.png`. Added `.heropair` CSS (1fr 1fr grid). Next/unbuilt wave
  hero unchanged (`/wave-{n}.png` highlight). Updated page-header + hub-card copy from "this
  wave outlined in gold" → "both fill in one wave at a time" (now accurate).

**Left:** nothing on the additive hero. The old `/gate/{n}/sbs.png` route + `latest_gate_sbs`
still exist (history filmstrip still uses per-iteration sbs frames) — intentionally kept.

**Next:** idle — unfired trigger = owner go-ahead on #30 wave-1 RE-GATE (never self-approve)
or commit the HELD portal edit.

**Held:** bikar 0 / qiyas 0 / sacred-patterns 1 — `tools/wave-plan-server.py` (now also carries
the additive-hero rewire). The new `build_wave_photo_ghosts.py` + 22 `wave-N-photo.png` live in
the Dropbox session dir (NOT git-tracked) — in place. Held per GHA-budget tenet.

**Verified (Tenet 24/25):** Expected wave 1 = lone centre star colour on both halves (left our
star on white, right the photo grey-ghosted except the centre star); wave 9 = central medallion
1..9 in colour, outer petals still grey; wave 22 = whole flower in colour. Browser-rendered
`/waves` matches exactly on all three: wave-1 hero is two pictures side by side, left lone navy
star, right whole photo ghosted grey with ONLY the centre star in full navy; wave-9 hero shows
the central region (navy/blue/teal) coloured on both sides with outer petals ghosted; caption
"both fill in one wave at a time. Everything past this wave is greyed out". py_compile clean,
portal restarted (200), 22 heropairs, 22 `wave-N-photo.png` served (image/png), zero "outlined
in gold" text anywhere.

---
## #43 Shape clustering — data layer built, atlas reveals real structure (2026-06-15)

**Done:** Built `iterations/71/wave-ghosts/cluster_shapes.py` (clusters the 675 emitted
faces from `pattern.gt.json` into canonical shape-classes by rotation+mirror-invariant
edge/turn signature, Tenet 23 — reads engine truth not raster) + `render_cluster_atlas.py`
(contact sheet `cluster-atlas.png`). Result: 675 faces → 50 classes, every polygon class
0.0% area-spread (members geometrically identical to fractions of a %). 46 classes repeat
≥10× = the near-10-fold core vocabulary.

**Left (two fixes before #44 consumes clusters.json):**
1. Mirror-pair bug: k03/k04 are the same scalene triangle flipped (edges [1.25,1.72,2.12]
   vs [1.25,2.12,1.72]) but didn't merge — mirror canonicalization picks mismatched
   rotation starts; dist 0.63 > EPS 0.06. Fix the canon() mirror alignment.
2. Expose evidence in clusters.json (per-class edge-length signature) so the merge UI
   can show WHY two shapes are/aren't grouped, and flag mirror-pairs as their own category
   ("same shape, flipped").

**Witness (Tenet 18/24):** the atlas PNG is the witness — eyeballing it caught the
mirror-pair miss that reading hex codes hid, AND corrected my own snap judgment (k02 is
isosceles, genuinely distinct from the k03/k04 scalene pair — not an over-split). This is
the case for the propose-and-confirm loop showing edge evidence, not just silhouette.

**Next:** owner judges the vocabulary from cluster-atlas.png — what counts as "the same
shape" (rotation-only? mirror too? color-blind across rings?) sets the merge-loop default.

**Held:** bikar 0 / qiyas 0 / sacred-patterns 1 (tools/wave-plan-server.py, unchanged).

---

## #47 — /simplify: click a shape card → see where it sits in the whole picture (2026-06-15)

Plain English: on the /simplify page, the owner wanted to click any shape in the
"shapes we found" strip and immediately SEE every place that shape lives in the full
medallion — not just its silhouette in a box. Built a popup modal that draws the full
render with every copy of the clicked shape outlined in bright magenta.

**Done:** click-card→modal shipped. Each cluster card carries `data-cid`; clicking opens
a modal that draws `/simplify/pattern.png` (the exact `render.png` gt.json was emitted
against — 1024×1038 box, NOT render.cairo.png whose box differs) with an SVG overlay
(`viewBox 0 0 1024 1038`, `preserveAspectRatio=none`) tracing each member's TRUE gt
outline. Payload gained per-cluster `members` (gt outlines, int-rounded) + `centers`
(fallback) + top-level `image{w,h}`. Verified in Chrome: k01 (40 triangles) outlines
land exactly on real triangle faces in symmetric rings; console clean; structure gate
untouched (approved_at_iter still null). All in tools/wave-plan-server.py (HELD).

**Left:** the modal surfaced a CLUSTERING-QUALITY finding (not a modal bug): cluster
**k00 "round" (142×)** is the outer-rim boundary band — 142 thin arc-segment faces that
together tile the whole rim, so highlighting all 142 floods the disc magenta. The
clusterer (cluster_shapes.py) lumps these rim slivers into one circle/round class. Worth
revisiting whether rim-boundary slivers should be their own class or excluded from the
"shapes we found" vocabulary — they're not a shape the owner places, they're the frame.

**Next:** owner reviews the click-to-see modal; decide if k00 rim-band should be filtered
out of the vocabulary strip (a #43 clusterer tweak, separate from this feature).

**Held:** bikar 0 / qiyas 0 / sacred-patterns 1 (tools/wave-plan-server.py — now also the
click-to-see modal + /simplify/pattern.png route; commit owner-gated, GHA budget).

## #49 + #50 — /simplify: clickable merge silhouettes + "Decisions you've made" review (2026-06-15)

Plain English: two follow-ups to the #47 click-to-see modal, both about the
"Are these the same shape?" merge loop. (#49) The two candidate silhouettes in the
merge-question card weren't clickable — the owner wanted the SAME locate-in-picture
modal when tapping either. (#50) The 16 "same shape?" answers already given were saved
to disk but INVISIBLE on the page — the owner asked *"how do we see all the 'is same
shape' decisions we already made?"*

**Done (#49):** each merge candidate is now a `<button class="peek" data-cid>` carrying
its `swatch()` silhouette + a "tap to find it" hint; event delegation on `#pair` opens
`openModal(cid)`. Verified in Chrome: tapping either silhouette in the ask card opens the
locate modal with that shape outlined in magenta across the medallion.

**Done (#50):** added a "Decisions you've made (N)" gate below the ask card. Renders one
row per saved verdict: two mini silhouettes flanking "vs", a green "✓ One shape" /
"✗ Kept apart" verdict, and a "Change my mind" button. Mini swatches reuse the #47/#49
locate modal (clickable). "Change my mind" POSTs `state:"skip"` (the handler treats skip
as CLEARING the verdict — `v.pop(key)`), splices the pair back into the ask queue, and
scrolls up to it. A live client `verdicts` copy keeps the list in sync without a reload.

**Verified end-to-end in Chrome (Tenet 24/25, expectation written before viewing):**
expected 16 rows each with two minis + "vs" + green "✓ One shape" + "Change my mind" —
confirmed exactly. Clicked row-1 mini → locate modal opened (k07, "appears 20 times",
outlines land on real faces). Clicked "Change my mind" → disk verdicts dropped 16→15,
k07|k08 removed, pair re-queued into ask card (pair 16/40 shown), page scrolled up,
"Decisions you've made (15)". Re-answered "Yes — one shape" via the live UI → disk
restored to 16, k07|k08 = `{state:"same", date:"2026-06-15"}`. Console clean throughout.
**Isolation confirmed:** session.json `stage_gates.structure.approved` still `None`,
`approved_at_iter` still `None` (mtime Jun 14, predates all portal work) — the merge loop
writes ONLY to `iterations/71/wave-ghosts/merge-verdicts.json`, never the owner-gated gate.

**Next:** owner reviews #49/#50. The remaining /simplify backlog: #48 (k00 rim-band should
leave the vocabulary strip — a #43 clusterer tweak), #45 (unique-shape inventory),
#46 (higher-level groupings — flowers/rosettes/bands).

**Held:** bikar 0 / qiyas 0 / sacred-patterns 1 (tools/wave-plan-server.py — now also the
clickable merge silhouettes + decisions-made review; commit owner-gated, GHA budget).

## #51→#52→#53 — "there are not even triangles there": the vocabulary lists FRAGMENTS, not designed shapes (2026-06-15)

Plain English: the owner clicked "tap to find it" on a /simplify triangle merge-card and
found the highlighted spots in the original are **not triangles at all**. Chasing it down
the render-and-look ladder (Tenet 24) corrected the diagnosis TWICE — a good example of
why you look at the image instead of reading the metric.

**The false trails (each killed by a render):**
- *First guess — bad captions.* The cards say "two side-lengths" vs "3 different
  side-lengths" for shapes that look identical. Rendered the 3 triangle clusters at true
  proportion (`/tmp/triangle-compare.png`): k01 `[1.63,1.63,1.92]` tall isosceles,
  k02 `[1.25,1.72,2.12]` slanted scalene, k03 `[1.40,2.26,1.40]` wide isosceles — three
  **genuinely different** triangles, distance 0.32–0.63 ≫ EPS. Captions + clustering both
  CORRECT. Not the bug.
- *Second guess — pose, not shape.* The card silhouettes are drawn at whatever rotation
  the face sat at, so the eye can't separate "different shape" from "spun around." Real
  presentation flaw, but not what the owner meant.
- *Third guess — salience/slivers.* Highlighted all 110 `.turquoise` faces on the render
  (`/tmp/turquoise-located.png`): they tile the turquoise rosette PETALS, not noise.

**The actual root cause (confirmed):** each designed shape (a turquoise petal, a bow-tie)
is **fragmented into 2–3 triangular faces** by construction lines crossing through it.
`/tmp/petal-split.png` — one rosette's turquoise region = **12 loose triangles**, where a
red+purple+blue triangle together make ONE petal. gt.json confirms `has_arcs:false`, all
`outline_arcs type:line` — they ARE real straight triangles, just **sub-pieces** of the
shape the artist drew. So the vocabulary lists *construction fragments*; you look for a
triangle, your eye sees a petal-made-of-triangles, and "there are no triangles there" is
exactly right. Same family as #48 (rim band) — extracted geometry ≠ designed shape.

**Owner decision (2026-06-15):** fuse the fragments back into the authored shape by
reading the `.bkr`'s authored unit — NOT a geometric heuristic. (Picked "Read it from
the design" over "fuse by geometry".)

**Engine finding that scopes the fix (#53):** the existing `data-shape-id` attribute is
the WRONG fuse key — for girih faces it resolves to the `tileType` (`decagon`), UNIFORM
across all 110 petals, so it can't tell petal A from petal B. `source_primitives` on the
turquoise faces is likewise uniform (`_girih_decagon/_girih_decoration/_girih_outline/
layer:0`, only 2 variants over all 110). The wave shapes get a per-unit `C141:cycle:#N`
id; the girih decoration faces get **no analogous per-region id**. So the real work is a
NEW engine signal: emit a per-authored-decoration-region id on girih faces (which placed
tile + which decoration region), thread it girih-tiles.ts → segment tags → face
extraction → gt-emitter, contract-amend FIRST (Tenet 23/C5 — do not reuse data-shape-id),
prove on a Tier-0 single petal (Tenet 17), then /simplify fuses by it before clustering.
**OWNER-GATED** (bikar core build + commit + GHA budget) — investigation only this turn.

**Pre-staged plan (2026-06-15, idle loop tick — planning only, NOT started):**
`bikar/.claude/plans/authored-region-id-fuse-fragments.md`. 4 steps (contract-amend FIRST;
thread per-tile-instance id girih-tiles.ts:190 → evaluator emit sites → faceClasses-style
Map → gt-emitter; Tier-0 single-petal witness + vitest FIRST; /simplify fuses by id before
clustering). Key C5 finding: #53 is NOT a fresh decision tag — it extends the ACCEPTED
`face-extractor` doc (2026-05-18-region-identity-class-emission-4-layer-fix.md, Option D:
face-attribute Map consumed by gt-emitter, NOT edge-derived). Layer on that doc on approval.

**Tasks:** #51 (caption/rotation — closed, not the bug), #52 (artifact-vs-designed —
closed, refined into #46), #46 (fuse fragments → flowers, re-scoped with evidence),
#53 (emit authored-region id — the engine build, owner-gated; plan staged above).

**Held:** bikar 0 / qiyas 0 / sacred-patterns 1 (no new code this turn — investigation +
task records only).

---

## Loop entry — 2026-06-15 (structure gate APPROVED)

**Done:** Owner cleared three gated decisions this session via the visual picker / direct
go-ahead. (1) #53 bikar engine COMMITTED `50897af` (authored-region id; commit-not-push,
owner-authorized). (2) /simplify portal COMMITTED sacred-patterns `f1ae423` (#44–#52,
grandma-plain experience; commit-not-push). (3) **#30 wave-1 structure RE-GATE: owner
PICK A via wave1-regate-picker** — wave 1 = ONE central star (single authored shape; NOT
split into disk+frame). `stage_gates.structure.approved=true` @ iter 71, authority + owner
note recorded in session.json; verdicts[] appended iter-71 'agreed'; #30 closed.
**Left:** owner note 'Its one shape, but its 10/3' → the central star should be a {10/3}
star polygon, not the current hankin {10/4}-derived build. Filed as task #54 (within-approved-
grouping refinement, NOT a gate reopen). PUSH of `50897af` + `f1ae423` still owner-gated
(batch one GHA cycle).
**Next:** advance to the COLOR stage (`stage_gates.color.palette_agreed` false, owner-gated)
OR, on owner go-ahead, push the two batched commits / build #54. Idle-not-blocked: unfired
trigger = owner go-ahead on push-vs-color-vs-#54.
**Held:** bikar 1 (`50897af` committed, unpushed) / qiyas 0 / sacred-patterns 1
(`f1ae423` committed, unpushed) — both held for one batched push per the GHA-budget tenet.

---

## 2026-06-17 — WEAVE-gate monitor (PID 87867) watches the WRONG json path; the loop self-wake is the real signal

**Plain English:** the long-lived background monitor that's supposed to wake the loop when the owner
approves the weave reads the wrong key in `session.json`, so it will never fire — even after a real
approval. The loop's own periodic self-wake (which reads the correct key) is what actually catches the
verdict; don't trust the monitor as the primary wake.

**Detail:** monitor PID 87867 polls `d.get('weave',{})` — the **top-level** `weave` key, which does
not exist (always `{}` → prints `None 0` forever, never changes, never fires). The authoritative gate
is at `stage_gates.weave.approved` / `.verdicts`, written by `POST /api/weave-verdict`
(`tools/wave-plan-server.py:3437`, `s["stage_gates"].setdefault("weave",{})`) and read back at
:2739/:3134 as `gates.get("weave",{}).get("approved")` where `gates = stage_gates`. The loop prompt
forbids re-arming the monitor, so the fix is NOT to re-arm — it's to keep reading
`stage_gates.weave` directly each tick (already done) and rely on the ScheduleWakeup heartbeat, not
the monitor, to land the owner verdict. A future re-arm (if ever authorized) must watch
`d['stage_gates']['weave']`, not `d['weave']`.

**FIXED 2026-06-17 (same day):** owner authorized the fix. Killed the mis-pathed monitor (PID 87867 /
task bkxvggy7c) and re-armed a correct one — task **bt4dilwoq**, watching
`d['stage_gates']['weave']` (approved / verdicts / note), emitting on any change AND on read errors so
a crash can't masquerade as "no verdict." This monitor is now the dependable primary wake again; the
ScheduleWakeup heartbeat remains the backstop.

---

## 2026-06-17 — Weave studio "no over/under" is ILLEGIBILITY, not absence — bands too thin, casing reads as dashes, wrong crossing distribution

**Plain English (owner report + screenshot):** the weave studio shows no over/under weaving on the
bands, the shadow toggle seems to do nothing, and the perimeter / central star has an ugly thick grey
doubled halo. The owner is right that it looks wrong — but the surprise from the render-and-look
(Tenet 24) is that the over/under IS in the SVG; it's just visually illegible.

**What the render-and-look actually found (three layers, simplest first):**

1. **The engine over/under WORKS.** The canonical `patterns/Weave/Weave-8.bkr` witness renders a clean,
   genuine basket weave — counting paths *inside the groups* (not the class string): 8 `strapwork-over`
   / 8 `strapwork-under` / 8 `strapwork-casing` paths, with dark shadows carving each "this band dips
   under that one." So casing/over-under emission is not broken. (Earlier mis-measurement: grepping
   `strapwork-casing` as a substring returns 1 — it's a single `<g>` wrapper; the real count is the
   `<path>`s *inside* that group.)

2. **The studio's served weave DOES contain interlace** — 180 over / 180 under / 180 casing paths
   (POST `/api/preview-svg` `{style:crossing, casing:#0A2240}`). The crossings are geometrically present.
   So "no over/under" is **illegibility, not absence**: at a high-res arm crop the dark-navy casings
   read as ISOLATED dashes/diamonds sitting between tiles, and the white bands are too THIN relative to
   the tile gaps to read as continuous woven ribbons. In Weave-8 the bands are wide ribbons and the
   casing is an obvious gap; here width 10 against the medallion's tile spacing is too thin and the
   casing stubs don't connect into a ribbon-under-ribbon read.

3. **The central star grey halo** (the owner's "perimeter" complaint): at the center crop, a thick
   light-grey doubled outline traces the 10-point star, and the inner rosette's bands are so dense+thin
   they merge into a white blob with no legible weave. The halo is the casing/outline rendering light
   instead of the dark-navy it was asked for at the dense center where bands overdraw each other.

**SECONDARY (distribution) root cause — the studio never invokes field-Hankin.**
`build_weave_variant` (`tools/wave-plan-server.py:1316`) emits the OLD per-circle ring weave
(`weave .weave_overlay` + `ring every k on <circle>`), NEVER the field-Hankin primitive
(`weave … field angle θ on wave N` — built this session, present in `packages/core/dist` 3×, reachable
through the CLI which imports the symlinked local core). Per-circle {n/k} chords cross only at each
ring's CENTER, so crossings cluster centrally and the arms get a sparse, irregular scatter — which is
exactly why the weave looks busiest in the middle and thin on the arms.

**Verified field-Hankin RUNS but needs tuning:** a hand-authored proof
(`field angle 36 on wave 1-9 ray 60`) rendered through the CLI and produced 32 690 crossings — proof
the primitive fires end-to-end — but over-densified into tiny black tangles inside the rosettes because
θ=36 / ray=60 were wrong and waves 1-9 are the inner rosette tiles, not the arms. The fix is correct
per-wave θ (≈90−180/n for an n-gon edge) on the ARM/perimeter waves, with ray bounded to the local
inradius.

**NEXT (all owner-gated tuning in the studio — #23, NEVER self-approve):**
- (a) `build_weave_variant` should emit `field angle θ on wave N` on the arm/perimeter waves so
  crossings distribute across the field, not pile centrally.
- (b) widen the bands and/or tune casing so over/under reads as ribbons, not dashes (the legibility fix
  — likely a band-width vs tile-gap ratio knob, measured against Weave-8's clean ratio).
- (c) the central-star grey halo is a separate casing-overdraw/outline bug at the dense center.

**Visual witnesses (rendered, eyeballed; in /tmp this session, regenerable):** `weave8.png` (GOOD
reference interlace), `weave-studio-served.png` (flat-looking medallion), `studio-arm-crop.png`
(casing-as-dashes), `studio-center-crop.png` (grey halo + white blob), `field-hankin-proof.png`
(field primitive fires but untuned).
