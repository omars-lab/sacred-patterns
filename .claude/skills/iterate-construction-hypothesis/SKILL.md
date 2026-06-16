---
name: iterate-construction-hypothesis
description: Use this skill when a pattern reconstruction has plateaued and the next move is to try a DIFFERENT bikar DSL construction — not to tune the qiyas detector. Encodes the hypothesize-author-render-verify-measure-log loop for the CONSTRUCTION side: you change the .bkr (circles, divisions, connect/arc statements, repeat/rotate, classify rules), render it, verify it visually through the review portal, and measure composite_score against the prior iteration — while the detector stays frozen. The defining guard is the inverse of iterate-detector-calibration: tweak the construction, NEVER the thresholds. USE THIS SKILL ANY TIME you are about to change a .bkr to move a reconstruction score, especially when the plateau tempts you to instead loosen a detector tolerance.
user_invocable: true
argument: session-slug (e.g. bikar-medallion-10) — the Dropbox iteration session to advance
---

# iterate-construction-hypothesis

This skill drives **construction-side** pattern iteration as a self-aware
loop with persistent memory and explicit loop-detection. It is the mirror
image of qiyas's `iterate-detector-calibration`: that skill changes the
*detector* to better read a fixed construction; this skill changes the
*construction* to better express the intended geometry, with the detector
held fixed.

## The plain-English problem this solves

A reconstruction (medallion-10 is the canonical case) gets to a score and
*stops moving*. The reflex is to reach for a detector knob — "the matcher
won't pair these two faces, let me loosen the cost" / "the symmetry pillar
mis-scores, let me widen the fold tolerance." That reflex is a Tenet 7
violation in disguise (sacred-patterns Tenet 23 names it precisely:
re-deriving / re-tuning downstream what the construction should have
declared upstream). Every threshold you loosen to fit one pattern is noise
the next pattern's detector has to compensate for.

This skill says: **when the score plateaus, the hypothesis is about the
construction, not the detector.** Maybe the medallion needs a different
overlay star ({10/3} vs {10/4}), maybe the petals need to be built from
girih tile primitives instead of wedge-and-rotate arcs, maybe two faces
the detector "can't tell apart" are genuinely the wrong shape in the
`.bkr` and should be re-authored. The detector is the *oracle that tells
you the construction is wrong* — you fix the construction, never silence
the oracle.

## When to use

- A reconstruction's `composite_score` has plateaued across ≥2 iterations
  and the next idea you have involves a `.bkr` edit (new construction
  lines, different overlay, re-authored faces, a new `classify` rule, a
  symmetry-order change).
- You catch yourself about to edit a qiyas detector parameter, segmenter
  choice, matcher cost, or signature tolerance to make a *specific
  reconstruction* score better. **STOP — that's this skill's trigger, not
  iterate-detector-calibration's.** (That skill is for closing
  *corpus-wide* identity-fidelity gaps where the construction is ground
  truth and the detector is genuinely wrong. If you're tuning the detector
  to fit *one* reconstruction, you're in the wrong loop.)
- The medallion-10 ceiling (sacred-patterns #85) or any "this pattern
  won't converge under the current construction philosophy" situation.

## Routing — which fix is this? (read FIRST)

Before you change anything, route the friction. There are **five**
destinations, and they are cheap-to-expensive top to bottom — check them
**in order** and take the first that fits. The expensive mistake is
skipping straight to "build a new primitive" or "different philosophy"
when the capability already exists and just isn't being invoked.

| # | The friction looks like… | Destination | Why this and not the next one down |
|---|---|---|---|
| **1** | The capability **already exists** but isn't wired in — a DSL statement that's authored but never invoked, a kernel function that's tested but never called from the renderer, a `data-*` attribute the evaluator computes but the renderer drops. | **Emit / invocation fix** — grep the renderer / evaluator / barrel for the symbol; the gap is one call site. Stay in this skill (it's a `.bkr` or wiring edit). | This is the **cheapest** fix and the **most common** one missed. iter-34's A5 0→100 was exactly this: `computeStrapwork` existed, the `strapwork` DSL statement existed, the decoration segments were emitted — the only missing piece was a `strapwork …` line invoking the weave. No new geometry, no new statement. See memory `feedback_check_emit_layer_before_option` + `feedback_girih_strapwork_is_render_style_not_geometry`. |
| **2** | Same construction **philosophy**, you just need different `.bkr` geometry — a different overlay star order, re-authored faces, a new `classify` rule, a symmetry-order change. | **This skill** (`iterate-construction-hypothesis`) — hypothesize → author → render → verify → measure. | The DSL/kernel can already express what you want; you're searching the *construction space*, not extending the *language*. |
| **3** | You need a **new DSL statement** — new syntax / keyword / AST node, because the construction can't be *spelled* in the current grammar (e.g. a `strapwork` statement before it existed). | **bikar `dsl-design`** then **`engine-extension`** (parser→AST→evaluator path). File it as a bikar feature task. | The missing piece is *surface syntax*, not a geometry algorithm. The kernel may already have the math; you're exposing it to the language. |
| **4** | You need a **new kernel algorithm** — a geometry primitive that doesn't exist at all (the substitution-rule field generator, a new intersection routine, `computeStrapwork` before it existed). | **bikar `engine-extension`** (kernel path) — build it in `packages/core/src/kernel/` with its own Tier-0 test per bikar Tenet 17. | The missing piece is *computation*, not syntax. Often paired with #3 (new algorithm + new statement to invoke it), but the algorithm is its own task with its own atomic witness. |
| **5** | The construction **philosophy itself is wrong** — falsifications cluster into "this whole approach can't produce the baseline's vocabulary" (the medallion-10 wedge-and-rotate → girih finding). | **`present-options`** — author a decision doc; this is a philosophy pivot, not an iteration. | A different philosophy is a *scoped feature build behind a decision*, not a loop iteration. Grinding iterations against a philosophy ceiling is the Tenet-7 trap loop-detection rule #2 catches. |

**Stop rule before extending anything (#3/#4):** confirm you ruled out #1.
Grep for the symbol you think is missing — `computeStrapwork`,
`girihField`, the `data-` attribute, the DSL keyword. The 2026-05-28
iter-34 lesson is that the cheapest fix (invocation) masquerades as the
expensive one (new geometry) until you check the emit layer. **Companion
to bikar Tenet 26** (extend the DSL when the construction fights the
language) — Tenet 26 governs the #2-vs-#3/#4 fork (don't hand-author
around a missing primitive); this table adds the #1 fork above it (don't
*build* a primitive that already exists, just invoke it) and the #5 fork
below it (don't iterate against a philosophy ceiling).

## Per-iteration triage — what is this qiyas-diff signal telling me? (read SECOND)

The routing table above answers *"where does the fix live"* (invocation /
construction-space / new statement / new algorithm / philosophy). This
checklist answers the prior question the loop kept re-asking: *"is this gap
even mine to fix in the .bkr at all?"* Run it on every `validation.json`
warning / `qiyas-diff` pairing **before** editing — classify the gap into
exactly one of three owners, because editing the `.bkr` for a detector bug
or a DSL gap is wasted motion (and a Tenet-7 trap when it tempts a detector
tweak).

**The three owners:**

| Owner | The signal looks like… | First action (NOT a `.bkr` geometry edit) |
|---|---|---|
| **Construction issue** (yours — fix here) | The render is *visually wrong* against the reference in the way the warning names: a face missing that the reference clearly has, wrong fold order, a shape with the wrong vertex count, an overlay star at the wrong `{n/k}`. The detector is correctly reporting a real construction defect. | Route through the 5-way table → usually #1 (invocation) or #2 (construction-space). Edit the `.bkr`. |
| **bikar DSL gap** (construction-side, but a feature not an iteration) | You know the correct geometry but **cannot spell it** in the current DSL, or the face-walker/gt-emitter *mangles* a correctly-authored construction (an absorbed polyclass face, a dropped same-class face, a sliver — see the `feedback_bikar_*` face-walker memories). The `.bkr` is right; bikar's engine can't render/emit it faithfully. | Route through the 5-way table → #3 (new statement) or #4 (new kernel algorithm). File a bikar feature task with a Tier-0 witness; do NOT hand-author a magic-number approximation (bikar Tenet 9). |
| **qiyas detector bug** (NOT yours — escalate, never tune) | The construction is **provably correct** (portal look confirms the render matches the reference) but the detector mis-reads it — pairs two geometrically-different faces, mis-scores a fold it should read from `data-symmetry-fold`, re-derives a fact the DSL already declares (Tenet 23). The metric disagrees with a correct render. | `escalate-qiyas-divergence` — capture the fixture, file the qiyas issue with a reproducer. **Never** loosen a qiyas number from this loop (stop rule 3). |

**The discriminating question** (forces the classification before any edit):
*open the render in the portal and compare to the reference.* If the render
is visually wrong → **construction issue** (or DSL gap if you can't author
the fix). If the render is visually right but the score is low → **detector
bug** (escalate) or you mis-read which warning is load-bearing. The portal
look (Tenet 27) IS the triage instrument; you cannot classify the owner
from the JSON alone (Tenet 26 — the serialization is lossy for topology).

### qiyas-diff signal → deterministic `.bkr` edit (construction-issue owner only)

When triage says **construction issue**, this maps the concrete
`validation.json` / `qiyas-diff` signal to the smallest `.bkr` edit. These
are starting points for the Step-1 hypothesis, not blind rewrites — each
still gets a `predicted_cost` and a portal verify.

| qiyas-diff / svg-audit signal | Most likely construction cause | Deterministic first `.bkr` edit |
|---|---|---|
| `unmatched_truth` face (reference has a shape the recon lacks) + A4 PARTIAL/SPARSE | A face the construction never builds, or builds then the face-walker absorbs | Grep emit layer first (5-way #1); if truly absent, add the `connect`/`cycle`/`classify` that authors that face (5-way #2) |
| `unmatched_detector` face (recon has a shape the reference lacks) | A spurious face from an over-division or a stray intersection | Remove the extra `divide`/`intersect`, or add the missing `classify .name` so a real face isn't read as unclassified |
| A6 MISSING/PARTIAL for a named baseline shape | The baseline shape's vocabulary isn't produced by this construction philosophy | If isolated: author the shape (5-way #2). If it clusters with other A6 misses → philosophy ceiling (5-way #5, stop rule 2) |
| A2 N-fold BROKEN/APPROXIMATE | Symmetry construct wrong order, or a per-sector edit broke rotational identity | Fix the `repeat N` / `rotate N` order; re-author the sector once and let the symmetry construct replicate it |
| A2 shape correct but ROTATED off-reference (census stays EQUAL, points miss the outline) | Construction **phase** mismatch — `hankin` rays start at edge-MIDPOINT phase (180/N), a half-step off the division-VERTEX phase | Phase-align the circle's ring with `divide Cn into N offset <deg>`; never hand-rotate a copy — see Cookbook #8b |
| A5 band-network GAPS/BROKEN | Strapwork decoration not woven (render-style gap, not geometry) | Invoke the `strapwork …` statement (5-way #1) — see `feedback_girih_strapwork_is_render_style_not_geometry`; do NOT add new tile geometry |
| Face emitted with `face_class=None` / unclassified in gt.json | Polygon authored but no matching `classify` rule, or the classify-by-predicate polyclass trap | Add the `classify .name where <pred>`; if two same-`sides` classes collide, that's a DSL gap not a construction edit (`feedback_per_edge_class_tags_same_trap_as_classify`) |
| Shape-count divergence but render looks right in the portal | Detector mis-read of a correct construction | **Escalate** (detector-bug owner) — do not edit the `.bkr` |

## The hard line — construction vs detector

| You may change (construction side) | You may NOT change (detector side) |
|---|---|
| `.bkr` blueprint (circles, lines, divisions, named points) | qiyas matcher cost weights / `CLASS_MISMATCH_COST` |
| `connect` / `connect arc` / `cycle` statements | qiyas segmenter choice (watershed/CCL), confidence floors |
| `repeat N` / `rotate N` / `mirror` symmetry constructs | qiyas signature normalization tolerances, fold slack |
| overlay star order ({10/3} vs {10/4}), petal construction method | `_check_dominant_fold` thresholds, ARI merge gates |
| `classify .name where …` rules, per-edge class tags | qiyas `acceptance.yaml` gate values, visibility-filter knobs |
| new DSL primitives in **bikar** (girih tiles, chirality, etc.) | anything in `qiyas/src/qiyas/**` that reads a number to decide a verdict |

If the fix genuinely requires a *new bikar DSL capability* (a primitive
that doesn't exist yet — girih tile, chirality, conditional template
block), that is still construction-side: it's a bikar feature, file it and
build it. It is categorically different from loosening a qiyas number.

**If you believe the detector is genuinely wrong** (not just inconvenient
for this pattern) — i.e., it mis-reads a construction that is provably
correct — that is NOT this skill. Switch to `escalate-qiyas-divergence`:
capture the fixture, file the qiyas issue with a reproducer, and let the
detector fix happen in qiyas's own calibration loop with its own
corpus-wide regression guard. The split is: *construction wrong → fix here;
detector wrong → escalate there; never tune the detector from here.*

## The stage ladder — structure → color → weave (read THIRD)

Plain English: an iteration that changes geometry, colors, AND band styling
at once cannot attribute its score move to any of them — and steering all
three by one full-color pixel number papers over structural divergence with
color tuning (the medallion-10 74% plateau was exactly this; iter-39's
"looked better, measured worse" color remap was the proof). So the loop is
staged: **get the structure agreed first, then color, then the weave** —
each stage with its own allowed edits, its own visual artifact, its own
metric, and an explicit owner-agreement gate before the next stage opens.

The `.bkr` statement vocabulary partitions natively by stage:

| Stage | Allowed `.bkr` edits | Visual artifact (the gate) | Steering metric |
|---|---|---|---|
| **1 STRUCTURE** | geometry statements only: `girih field`, `voids detect`, `connect`/`cycle`, `rotate`/`mirror`, `layer`, `face`, `tile`, blueprint | skeleton vs edge-extracted reference (`tools/structure-diff.sh`) | `structure_similarity` (pixel-diff on edge maps) + gt.json shape census. **Ignore** color_match. |
| **2 COLOR** | `palette` / `classify` / `fill` / `style` only — structure FROZEN | flat-color render vs reference + the standardized swatch sheet | `color_match_pct` toward `input/reference-analysis/reference-palette.json` values (values fixed once agreed; iterations only remap faces→named colors, **every remap ablation-gated**). Must not move structure_similarity. |
| **3 WEAVE** | `strapwork` block only — structure + fills FROZEN | full render vs reference + zoomed band crossings | full pixel `similarity_pct` + A5 band integrity; strapwork `color`/`width` seeded from the reference-analysis line measurements |

**Rules:**

- **An iteration belongs to exactly ONE stage** — the `stage:` frontmatter
  field in `hypothesis.md` (required). Step-2's "exactly one construction
  idea" means one idea *within the active stage*.
- **Scoping note:** strapwork *centerlines* (which decoration lines exist)
  are structure and appear in the skeleton; the bands' width/weave/color
  are Stage 3. Stage 1 settles "where do the lines go"; Stage 3 settles
  "how they're dressed".
- **Freeze check:** every Stage-2/3 iteration re-runs `structure-diff.sh`
  and confirms `skeleton_sha256` is byte-identical to the gated one. A
  changed sha means the iteration touched structure — revert or route back.
- **Route-back:** if a Stage-2/3 hypothesis genuinely needs a structure
  edit, the loop drops back to Stage 1 explicitly (new `stage: structure`
  iteration, re-gate — cheap: skeleton re-diff + owner nod). Never smuggle
  a geometry edit through a color iteration.
- **Gates are visual first, metric second:** the owner's eye on the
  side-by-side is the gate (Tenets 24/25/27); the machine numbers exist to
  catch regressions after agreement, not to substitute for it. The gate
  verdict is recorded in `session.json`:
  ```json
  "stage_gates": {
    "structure": {"approved_at_iter": null, "skeleton_sha256": null, "approved_date": null},
    "color":     {"approved_at_iter": null, "palette_agreed": false, "approved_date": null},
    "weave":     {"approved_at_iter": null, "approved_date": null}
  }
  ```
  Gate verdicts are recorded IN the review surfaces, never transcribed from
  chat: the studio's "The plan looks right" button (`POST /api/agree` →
  `wave_plan.agreed`) and the palette page's "These colours are right"
  (`POST /api/palette-agree` → `palette_agreed`). The portal-native upgrade
  path is qiyas annotation kinds Q12/Q9/Q11 with `verdict: "right"` (already
  supported in `qiyas/src/qiyas/review/state.py`) — wire later if wanted.
- **Per-wave owner verdicts are the decisive steering signal — consume them
  FIRST, every tick.** The `/iterate` portal gives the owner an approve /
  "Needs work" button + comment on every built wave; the verdict lands in
  `session.json` waves_passed[<n>].owner_verdict `{state, note, date}` (the
  studio's `POST /api/wave-verdict`, never chat). A `state: "denied"` is the
  highest-priority work in the loop — the owner's eye caught a defect the
  census/coverage metrics missed, which is the entire reason the portal
  exists (Tenets 24/25/27). **The note IS the fix instruction** (owner
  design: "Deny + comment = a fix request"). The loop reads denials at pickup
  with `tools/wave-feedback.py <session-dir>` (exit 2 = denied waves exist,
  with the wave + note printed; exit 0 = clean; `--json`/`--quiet` for
  tooling). Fix the lowest-numbered denied wave first (Tenet 20), re-render,
  re-run the gate, and let the owner re-judge in the portal — **never
  self-clear a denial**; only the owner flips it back to approved. When every
  built wave is owner-approved, `/api/wave-verdict` auto-rolls the structure
  stage to `approved` (the rollup is derived, not a separate button).
- **Stage entry gates:** Stage 2 opens only after BOTH the structure gate
  AND the owner's palette-swatch agreement (`tools/analyze-reference.py`
  swatch sheet); Stage 3 opens after the color gate. The weave gate is the
  80% expert-review gate — fleshed out in "Stage 3 is studio-iterated" below.
- **Tooling:** `tools/make-structure.py` (pattern.bkr → structure.bkr),
  `tools/structure-diff.sh` (skeleton render + edge maps + structure
  similarity + gate side-by-sides; skeleton SVGs must rasterize via
  rsvg-convert — ImageMagick's MSVG silently drops stroked paths),
  `tools/analyze-reference.py` (line/fill separation, standardized palette,
  swatch sheet — runs under the qiyas venv python),
  `tools/start-session.py` (the ONE-COMMAND front door for a NEW image:
  photo in → session folder + stage-gate session.json + edge map + swatch
  sheet + auto-detected wave plan + the studio server, all in one run —
  start here when recreating a new reference),
  `tools/plan-waves.py` (the wave plan below — runs under the qiyas venv),
  `tools/wave-plan-server.py` (the REVIEW HUB + wave-plan STUDIO: `/` reads
  session.json stage_gates and lists what needs the owner's eyes; `/plan` is
  the studio — owner clicks any shape, fixes its wave/flower with paired
  shape-level/wave-level buttons, Apply re-plans with the fixes persisted in
  wave-plan-overrides.json, the agree button records the gate; `/iterate` is
  the per-wave build review — each built wave shows its gate crop + history
  filmstrip beside an approve / "Needs work" + comment panel
  (`POST /api/wave-verdict`, auto-reconnects on a server restart); `/palette`
  is the colour gate; `/weave-studio` is the WEAVE gate — see "Stage 3 is
  studio-iterated" below),
  `tools/wave-feedback.py` (the loop's reader for the `/iterate` verdicts —
  prints denied waves + their fix-instruction notes, exit 2 when work is
  owed; run it at every loop pickup before advancing construction).

### Stage 1 is wave-based — plan the waves FIRST, never steer by one-shot whole-image diff

Plain English: before any structure iteration, the reference photo itself is
decomposed into an ordered reconstruction plan — concentric **waves** of
shapes working outward from a validated center — and the owner agrees to the
waves before construction starts. Reconstruction then attacks wave 1 until it
matches, then wave 2, etc. A whole-image structure diff mixes every wave's
divergence into one number and hides which ring is wrong; it is a tracking
metric only, never the steering signal (owner directive, 2026-06-11).

The protocol — for a NEW image the whole thing is ONE command (qiyas venv):
`tools/start-session.py <photo> --name <slug>` builds the session folder,
runs every step below with an auto-detected center/diameter, and starts the
studio. The pieces stay individually runnable: `tools/plan-waves.py
<session-dir>` (`--center X Y --diameter D` are optional overrides — when
omitted they are detected from the medallion mask and printed to confirm):

1. **Validate the center** — auto-detect the medallion center (mass center of
   the medallion mask); the owner confirms it with one look at the studio's
   marked-up picture (the legacy `review/structure-priorities.html` annotator
   is retired — `docs/review-experience-audit.md`). Every wave is measured
   from this point.
2. **Exhaust the shapes** — every lattice-separated colored tile becomes a
   labelled shape (erode to snap JPEG-soft lattice bridges, label the cores,
   grow labels back = 100% coverage). The JSON reports
   `coverage_of_tile_area` so "all shapes exhausted" is checkable, not vibes.
3. **A wave holds ONE KIND of shape** (owner criteria, 2026-06-11): midpoints
   equidistant from the validated center, same/rotated copies of one another
   (rotation-invariant moment match), similar area, similar color (raw RGB
   distance, NOT palette names — names flicker at cluster boundaries). Kinds
   are connected components of the pairwise all-four-criteria graph, ordered
   inside-out by radius. **Validation: kind counts must respect the fold** —
   medallion-10 gave 22 waves with counts 1/10/20/40; a count like 7 or 13
   means the grouping is wrong. (Witnessed dead ends: raw radius bands put
   93% of the pattern in one wave; palette-name color matching split one
   kind 4/6.) The big rosette-center stars (top area tier) group into radial
   rings used for plain-language "where" labels.
4. **Waves group into composite FLOWERS (motifs)** (owner, 2026-06-11: "a
   shape similar to our middle one revolves around the origin — a mix of
   several waves"). Each anchor ring seeds one flower family; a wave joins
   the family the majority of its members sit nearest to; within a family,
   fold-divisible waves chunk consecutive-by-angle into instances (per-member
   nearest-anchor coin-flips for kinds sitting exactly BETWEEN two flowers —
   witnessed [1,..,1,2,2] splits for the 18°-offset waves). **Validation,
   the composite analog of the fold check: every instance of a family must
   hold the same wave-multiset** (medallion-10: middle flower 21 shapes,
   inner ×10 @ 15, outer ×10 @ 21 — the owner's "similar to the middle"
   confirmed by count). A flower is the DSL-native unit: build it once,
   `rotate` fold times. Full algorithm, thresholds, and witnessed dead
   ends: `docs/wave-planning-design.md`.
5. **Owner gates the plan in the wave-plan STUDIO** — run
   `tools/wave-plan-server.py <dropbox-session-dir> --session-json <git-session-dir>/session.json`
   (qiyas venv; `--center`/`--diameter` optional overrides, auto-detected
   otherwise; `start-session.py` launches this for you on a new image) and
   send the owner the printed localhost URL. **Always pass `--session-json`
   pointed at the GIT `sessions/<slug>/session.json`** so the owner's gate
   verdicts (palette / per-wave / weave) write to source-of-record, not the
   Dropbox render copy — the `<session-dir>` positional stays the Dropbox
   path so reference.jpg + renders still resolve (the two args bridge the
   authored-in-git / rendered-in-Dropbox split). Omitting `--session-json`
   defaults verdicts to `<session-dir>/session.json` and silently drifts from
   git. The page has
   the flip-through (flowers row + waves row, one group bright per frame,
   colored maps) AND an inspector: click any shape → see its wave + flower
   in plain language → move it to a different wave/flower (or its whole
   wave; or take it out of its flower entirely). "Apply my fixes" POSTs to
   the server, which writes `wave-plan-overrides.json` next to the plan and
   re-runs plan-waves.py so every picture, count, and multiset validation
   regenerates with the fixes baked in (the planner auto-loads that file on
   every run, so fixes survive re-planning). Construction starts only after
   "waves agreed", recorded in `session.json` →
   `stage_gates.structure.wave_plan.agreed`.
6. **Iterate flower-by-flower, wave-by-wave** — each `stage: structure`
   iteration targets the lowest unmatched wave; its gate visual and diff are
   CROPPED/MASKED to that wave's region. Wave N must pass its visual check
   before wave N+1 opens — the whole-image structure_similarity is logged
   for trend, not steered by.

### Stage 3 is studio-iterated — dial the band knobs live, never one-shot the weave

Plain English: the weave (the woven white ribbons + the clean outline around
each outer petal) is a real stage with its own knobs — band width, band color,
over/under, outer-edge closure, radial-spoke suppression — and each knob needs
*render → look → adjust → look again*, exactly like structure had its 22 waves
and color had its palette gate. It is NOT a quick on/off toggle at the tail of
color. Two things make that explicit (medallion-10, bikar#23,
`bikar/docs/decisions/2026-06-16-weave-stage.md`):

1. **The weave can be invisible as authored.** When the bands are white and sit
   in the white gaps between colored shapes, weave-on and weave-off look almost
   identical — the eye reads "the gaps got wider", not "ribbons woven over the
   pattern". Don't gate weave by a whole-image pixel delta; gate it by the
   owner's eye on the band crossings and the outer-petal outline against the
   reference. (Red-recolor proof to confirm the band network exists is a debug
   trick, not the gate.)
2. **The outer edge must close.** The reference outlines each outer petal with
   one continuous mitred ribbon; the naive emit ends each ribbon in a ragged
   perpendicular stub at the degree-2 petal turns. The bikar engine now mitres
   degree-1/2 strapwork terminal nodes into a continuous turn
   (`strapwork.ts mitreBandCorners` + `svg-renderer.ts computeTerminalMitres`,
   with a `MITER_LIMIT = 2.0` clamp so shallow outer-ring turns fall back to a
   flat cap instead of shooting a runaway radial spike). Rendering-only, no DSL
   change. If a future weave shows open outer edges, that's the regression
   `bikar/tests/kernel/strapwork-outer-edge.test.ts` guards.

**The gate surface is `/weave-studio`** (`tools/wave-plan-server.py`): the photo
(left) vs our live render (right), grandma-plain dials — "Ribbon thickness",
"Ribbon colour", "Trim the spokes" (radial suppression), edge-fix — each change
debounced to a live `POST /api/preview` that writes a transient weave-variant
`.bkr` (the flat source-of-record `pattern.bkr` stays flat — the studio appends
the strapwork block to a TEMP copy, never the committed file), runs the bikar
CLI render, rasterizes, and swaps the image in ~1–2s. The owner dials the knobs
against the photo and clicks **"This looks right"** →
`POST /api/weave-verdict` writes `session.json stage_gates.weave`
(`{approved, approved_at_iter, approved_date, approved_authority, weave_params:
{width, color, suppress_*, edge_fix}, verdicts: [...]}`). `approved` is set
**only** on that owner click (`approved_authority: "owner (weave studio)"`) —
NEVER self-approved, same rule as every other gate. Only once the owner approves
the weave params is the strapwork block landed into `pattern.bkr` (uncommented
with the chosen width/color/suppression).

**Live render is a shared primitive.** `POST /api/preview`
(`{source_variant, params}` → transient `.bkr` → CLI render → rasterize → PNG
URL) is built once and designed reusable; it's wired for the weave studio first
(the loop's blocker), and the merge→code-diff `/simplify`, shape-inspect, and
gate-review A/B surfaces are follow-on consumers (bikar#13/#27/#45) — each
wired as its own task, not a four-surface refactor up front.

## Cookbook — proven tricks from the medallion-10 wave run (iters 41–55)

Plain English: fifteen techniques that each earned their place by either
passing a wave gate or catching a real defect during the run that took
medallion-10 from 0 to 13 passed waves. Each entry names the trick, when to
reach for it, and the witness iteration. This is a **living section** — add
a trick when it survives contact with a second wave; retire one when a
better tool supersedes it (note what replaced it).

### Measuring the reference (before any .bkr edit)

1. **Fold-and-cluster consensus measurement.** Never model a shape from one
   contour — at ~10px shape scale, single-shape contours are noise. Fold ALL
   N rotational/mirror copies into one canonical frame (rotate to the
   nearest fold axis, e.g. `axis = 18 + 36*round((theta-18)/36)` for
   10-fold; mirror-fold by the rel-angle sign), then greedy-cluster the
   folded vertices in (tangential, radial) space with a ~3 pattern-unit
   merge radius. n≈20–40 witnesses per vertex denoise what no single contour
   can. *Witness: iter-49's wave-7 models, IoU 0.93–0.95 vs consensus.*
2. **Area residual as a missing-vertex detector.** If the shoelace area of
   your vertex model runs >10% under the measured mask area, suspect a
   vertex hidden in a long shallow edge that `approximate_polygon` merges
   away. Discriminate weak clusters: exactly collinear with an existing
   edge → spurious; off-line AND including it closes the area gap → real.
   *Witness: the wave-7 kite's hidden 5th vertex, 70.4→83.9u² vs 83.3
   measured.*
3. **IoU coordinate-descent against consensus masks — report fitted AND
   snapped.** Optimize the vertex model by coordinate-descent on IoU against
   the rebuilt consensus mask, then grid-snap and re-score. Snapping should
   cost ~nothing (iter-49: 0.933→0.888 fitted-vs-snapped on the same
   rebuilt masks scored 0.880 — i.e. the snap is free); a big snap cost
   means the grid step is wrong, not the model.
4. **Exact-gcd grid trick.** A vertex at `axis ± δ` lands exactly on a /N
   division ring iff the ring's angular step divides gcd(18, δ). Pick ring
   division counts so every model vertex has an exact cpt — then **assert
   it programmatically** (a snap script that checks `cpt_index * step ==
   18 ± rel` exactly) instead of eyeballing near-misses. *Witness: iter-49's
   measure/snap-wave7.py, zero quantization error across 9 rings.*
5. **Pixel-scale erosion bias is ~10% at ~10px shapes — document, don't
   tune.** The segmentation's erode/regrow shaves small shapes; measured
   mask areas under-read truth by up to ~10% at the smallest scales. Note
   the bias in the measurement file and carry on — re-tuning ERODE_ITERS to
   fit one wave is the Tenet-7 trap.

### Proving the edit before rendering

6. **Data-proven clearance.** Before predicting "no collisions with prior
   waves," rasterize the snapped polygons in reference-pixel space and count
   overlap pixels against the prior waves' reference masks. Zero is the only
   acceptable number; "looks clear" is not a clearance check. *Witness:
   iter-49's 40 polygons, 0px overlap with ref waves 1–6, 84% of ink on
   ref wave-7 pixels.*
7. **Falsifier routes named in advance.** The hypothesis's `falsifier:`
   block pre-commits the diagnosis for each failure shape: displaced blob →
   registration/radius (re-measure); short face-count delta → unclosed
   cycle (Tier-0 witness); uniform boundary halo → band-edge erosion
   (accepted, Stage-2). When the gate misses, you execute a named route
   instead of improvising. *Witness: iter-49's iou miss fired the
   "check WHERE" branch and resolved in one attribution pass.*
8. **Tier-0 witness when a cycle fails to close.** If layer-1 face deltas
   come up short, do NOT debug inside the composite — author the one shape
   alone (no field, no repeats) and confirm the cycle closes there first
   (bikar Tenet 17).
8b. **Right-shape-wrong-rotation on a `hankin` wave → phase-align with
    `divide … offset <deg>`, never a hand-rotated copy.** When a wave's
    shape fatness/family is correct but it sits rotated off the reference
    (the A2 "shape better but rotation off" signal — census stays EQUAL, the
    points just don't land on the reference outline), suspect a **construction
    phase mismatch**, not a geometry error. `hankin angle θ on Cn` shoots rays
    from the inscribed N-gon's edge MIDPOINTS — phase `180/N` (18° for N=10) —
    while a `connect every k` star and most reference stars sit at the
    division-VERTEX phase (0°). The gap is exactly half a division step. **Fix:
    pre-rotate that circle's division ring** with `divide Cn into N offset
    <deg>` (the offset rotates the first division point CCW; negative = CW) so
    the hankin star's points fall back on the reference's points — do NOT
    author a second rotated star or nudge coordinates. The offset is **local to
    the one circle**; sibling waves on other circles keep their own phase (this
    is NOT a global rotation — only the misaligned circle carries the offset).
    **Diagnose the magnitude empirically:** measure the rendered star's tip
    angles from the navy-pixel mask vs the reference's, the delta IS the offset.
    Census must stay EQUAL through the change (the offset rotates a ring, it
    doesn't add/remove faces) — if it doesn't, the offset broke a downstream
    intersection and you have a different bug. *Witness: iter-70 wave-1 — the
    hankin-54 center star was 18° off; `divide C0 into 10 offset 18` put its 10
    points on the gold reference outline, coverage 0.838→0.932, census EQUAL
    675. The DSL `offset` keyword was a Tenet-26 invocation gap: kernel
    `divideCircle` already took a `startAngle`, the `divide` statement just
    didn't expose it (bikar commit 3ff260a, regression
    `packages/core/tests/dsl/divide-offset.test.ts`).*

### Gating the result

9. **Census is the PRIMARY machine gate.** Predict the exact gt.json face
   deltas by (sides, layer) bucket — e.g. "+20 layer-1 pentagons, +20
   layer-1 quads, +9 benign blueprint circles" — and verify exactly. Count
   bucket deltas, NOT raw side counts (the field already has pentagons).
   A census hit + eyeball pass outranks any iou number. *Adopted as primary
   from iter-53.*
10. **iou misses need attribution, not retuning.** When iou lands under
    prediction, decompose the penalty before touching anything: where does
    the penalty ink sit relative to the REFERENCE? *Witness: iter-49 — 91%
    of the penalty sat where the reference itself is white band/unbuilt
    waves; counterfactual iou 0.771. The miss was the unbuilt surroundings,
    not the wave's geometry.* An interstice wave's envelope is owned by
    later waves — calibrate the prediction, don't move the geometry.
11. **Saturated-baseline waves are weak-signal on iou.** When the field
    already paints most of a wave's crop, predict an iou *band* [lo, hi],
    not a floor — census + eyeball + clearance carry the gate.
12. **Metric-interlock allowance, pre-declared.** Passed waves' iou may dip
    ≤2 points when an adjacent wave lands ink inside their dilated crop
    envelopes. Declare the allowance in the hypothesis; beyond it, diff the
    shape census FIRST (face-split signal, not paint signal).
13. **One rasterizer path, no exceptions.** Wave-diff comparisons are only
    valid when both renders go through one rasterization call (canonical:
    cairosvg, output_height=1024). Baselines come from a re-raster of the
    frozen iteration's SVG, never from a stale PNG on disk. *Witness:
    iter-49's phantom drift (w1 coverage −7.5) that vanished when iter-48
    was re-rastered through the same path.*
14. **Wave N+1's baseline is free.** The previous iteration's wave-diff
    already computed ALL waves' metrics — read wave N+1's baseline from it
    instead of re-running anything.

### End-of-iteration bookkeeping (do this EVERY pass, pass or fail)

15. The gate verdict is not "done" until the surfaces that other sessions
    and the owner read are synced. In order:
    1. **Verdict appended** to `iterations/<N>/hypothesis.md` (pass/fail,
       metrics, attribution, next wave).
    2. **`session.json` → `stage_gates.structure.waves_passed[<wave>]`**
       gets `{iter, coverage, iou, date}` on a pass — this is the *status
       text* the studio's `/iterate` and `/slides` pages read live; skipping
       it makes the dashboard lie. (Re-passing an already-passed wave at a
       new iteration — e.g. a fit refinement on top of a later stage — counts:
       re-stamp its entry to the new `{iter, coverage}` so the attribution
       and the gate picture in 2b agree.)
    2b. **Wave-diff regenerated for the changed wave** — run
       `tools/wave-diff.py <session> <wave> --render iterations/<N>/render.cairo.png`
       so `iterations/<N>/wave-diff/wave-<NN>/sbs.png` exists. THIS is what
       drives the per-wave gate picture: `/iterate` (and `/slides`) serve
       `/gate/<wave>/sbs.png`, which resolves via `latest_gate_sbs()` to the
       *newest iteration that ran a wave-diff for that wave*. Step 2's
       `session.json` text alone does NOT move the picture — without 2b the
       card shows the OLD iteration's render even though the text says the new
       one passed (text and image disagree = the same "dashboard lies"
       failure as step 2, on the image surface). Needs `render.cairo.png`
       (cairosvg, 1024) per Cookbook #13's one-rasterizer rule. *Witness:
       iter-70's hankin-54 wave-1 re-pass — `session.json` was updated but
       `/iterate` kept serving iter-69's thin-star gate until wave-diff ran on
       iter-70.*
       **2b-ALL — a shared-geometry change stales EVERY built wave's crop, not
       just the changed wave's.** Every wave-diff crop is cut from the SAME full
       render, so when a fix touches geometry that other waves' crops include
       (the center star sits inside waves 2, 3, … crops; a ring shape sits inside
       its neighbours' crops), regenerating only the changed wave leaves all the
       OTHER waves' crops showing the OLD geometry — the portal serves a current
       center for wave 1 and a stale center for waves 2+. The owner sees "the
       middle shape is different between wave 1 and wave 2" — which reads as a
       geometry contradiction but is pure crop staleness. **Rule:** after a fix
       that changes any shape visible in more than its own wave's crop — or any
       whole-image re-raster (a renderer change, the blueprint display:none fix)
       — re-cut **ALL passed waves** against the new render with the one
       idempotent command:
       `/Users/omareid/Workspace/git/qiyas/.venv/bin/python tools/regate-all.py <session> <N>`.
       It loops `wave-diff.py` over every wave in `waves_passed`, re-stamps each
       entry to the fresh coverage/iou (preserving the genuine pre-change number
       under `prev`), and is safe to re-run (same iter → same numbers, `prev`
       untouched). A **Stop-hook** (`.claude/hooks/portal-regate-watch.py`) trips
       automatically when an iteration's `render.svg` is newer than its gate
       stamps and nudges you with the exact `regate-all.py` line — so you don't
       have to remember. `--dry-run` previews the wave list; `--no-stamp` re-cuts
       the crops without touching `session.json`. Coverage will shift a little
       for the re-cut waves — that is the
       cross-raster baseline shift (Cookbook #13), NOT a regression; confirm by
       eyeballing that the shapes still sit on their gold outlines before
       accepting the new numbers. *Witness: iter-70 — wave-1's `divide offset`
       rotation fix changed the center star; only wave-1's crop was regenerated,
       so waves 2–15 kept showing the pre-rotation center until all 15 were
       re-cut against iter-70's render. The dart rings (waves 2's own shapes)
       were verified unchanged by eyeball — the −7pt wave-2 coverage drop was the
       baseline shift, not lost ink.*
    3. **Progress sheet regenerated** (the progress-strip script pattern:
       reference + one tile per passed wave + current best, gold borders on
       reference/best; registration per-iteration — magick raster ≤48,
       cairosvg 49+) and copied to `<session>/progress.png`.
    4. **Frozen-best pointer**: if the wave passed, this iteration is the
       new frozen best — later baselines re-raster THIS SVG.
    A parallel studio/bookkeeping session may exist; whoever lands the
    verdict owns the sync (don't assume the other session will).

### End-of-build DSL reflection (after the LAST wave passes — one-time phase)

16. When the final wave passes, the build is geometrically done but the
    recipe is not: a wave-by-wave `.bkr` accretes per-wave overlays, stale
    comments, and repetition a from-scratch author would never write. Run a
    **reflection phase** before declaring the construction closed:
    1. **Freeze the witness** — the final iteration's render (canonical
       rasterizer) and its gt.json shape census are the equivalence oracle.
       Record both checksums/counts in the reflection's hypothesis.md.
    2. **Each optimization attempt is its own iteration** (`stage:
       structure`, idea = one simplification), gated by **census equality +
       pixel-identical raster** vs the frozen final — NOT by similarity
       thresholds; a simplification that changes any face is a fail, full
       stop. Run bikar `/simplify-pattern` for the candidate list: collapse
       per-wave `rotate 10` + `connect cycle` pairs into shared blueprints,
       merge circles that exist only to host one cpt, hoist duplicated
       layer/classify boilerplate, delete comments that narrate dead waves.
    3. **Capture every attempt durably, including the failures** — a
       simplification that breaks census equality is a finding about engine
       semantics (e.g. dedup order, layer extraction) and goes in the
       attempt's hypothesis.md verdict plus, if it names an engine
       behaviour, bikar `docs/lessons.md`. The point of the phase is the
       captured attempt log, not just a shorter file.
    4. **The deck tells this story too** — optimization iterations get
       recipe-diff slides like any wave (the /slides route diffs
       `pattern.bkr` between consecutive passed entries), so the owner sees
       the recipe getting shorter while the picture stays identical.
    Stop rule: two consecutive attempts that fail census equality for the
    same root cause → stop simplifying, file the engine finding, ship the
    last green recipe.

## Hard prerequisites — read these BEFORE acting

Blocking. Do not start an iteration until you have read all four:

1. **Memory index.** Read
   `~/.claude/projects/-Users-omareid-Workspace-git-sacred-patterns/memory/MEMORY.md`.
   Read the full bodies of any entry bearing on this reconstruction's
   construction philosophy — for medallion-10 that includes
   `feedback_a6_baseline_construction_philosophy_mismatch` (the 5
   falsifications proving parameter-tuning can't break the ceiling) and
   any `feedback_bikar_*` face-walker memory relevant to the shapes you're
   about to author. **If a memory cites a construction approach already
   falsified for this gap, do NOT re-attempt it without first reading WHY
   it failed.** If the reason no longer applies, note that in the iteration
   log; otherwise pick a different hypothesis.
2. **Session state.** Read the session's `session.json`, `discoveries.md`,
   and the last 2 `iterations/N/evaluation.md` at
   `~/Dropbox/Data/sacred-patterns/<session-slug>/`. These name what
   construction was tried, what it scored, and why it stalled.
3. **The plateau evidence.** Read the latest `iterations/N/validation/
   validation.json` — the `composite_score`, the ranked `warnings`, and
   the `svg-audit` A1/A2/A4/A5/A6 verdicts. The warnings name the discrete
   construction gaps to attack (a missing face, a wrong fold, a
   shape-count divergence). **`cf_delta` in a warning is upside-only —
   model the cost** (memory `feedback_cf_delta_cost_blind`): on a
   saturated mesh the edit's cost can dominate its predicted lift.
4. **The reference.** Open `input/reference.{jpg,png}` and the latest
   `iterations/N/render.svg` side by side in the review portal (Tenet 27).
   Write down, before iterating, the single most visually-wrong thing —
   that is your gap.

## The iteration recipe

For each iteration N:

### Step 1 — Pick the construction gap (write the log header FIRST)

Create `iterations/<N>/hypothesis.md` with this frontmatter BEFORE any
`.bkr` edit:

```markdown
---
attempt: N
date: YYYY-MM-DD
stage: structure | color | weave   # exactly one — see the stage ladder; edits outside the stage's vocabulary are invalid
gap_targeted: "<one-sentence visually-confirmed gap from the portal look>"
construction_hypothesis: "<what about the CONSTRUCTION is wrong, and why>"
bkr_change: "<the smallest single .bkr edit — or named bikar primitive to add>"
predicted_lift: "<+0.NN composite, and which warning it should clear>"
predicted_cost: "<what the edit might BREAK — new false faces, fold change>"
prior_art_searched: "<web search query for the construction technique, or 'none'>"
related_memory: "<memory files read that bear on this construction>"
detector_untouched: "confirmed — no qiyas param/threshold/cost in this iteration"
---

## Plan
<why this gap, why this construction hypothesis, why this is the smallest edit>

## Guardrails check
- This is a CONSTRUCTION edit (.bkr / bikar primitive), not a detector edit: confirmed
- Construction-philosophy memory checked — this approach not already falsified: confirmed (or: falsified before because X, but X no longer applies because Y)
- predicted_cost names a concrete failure mode I will look for in the render: confirmed
```

If you cannot fill a field honestly, STOP and surface why instead of
fudging.

**Start from the seed when one exists.** If the prior iteration carried a
portal review, `tools/seed-hypothesis.py` (run by hand or by auto-iterate)
has drafted `iterations/<N>/hypothesis-seed.md` with the machine-knowable
half pre-filled: attempt number, the top-ranked gap citing its
`annotation_id`, the evidence trail from `review-verdict.json`. Author
`hypothesis.md` from that seed. Two rules govern the split:

- `gap_targeted` is a machine draft — rewording is allowed, but either keep
  the `[annotation …]` citation or state in `## Plan` why you override the
  ranking (structure-before-pixels is the default order for a reason).
- Every `TODO(judgment)` field is YOURS: `construction_hypothesis`,
  `bkr_change`, `predicted_cost`, the Expected-visual prose. Never let
  machine text stand in for them — a templated Tenet-24 expectation is a
  fudged one. A hypothesis.md still containing `TODO(judgment)` is invalid.

### Step 2 — Make the change: exactly one construction idea

One overlay change, one petal-construction method, one symmetry-order
edit, one re-authored face group, one new `classify` rule. Not two. The
point of single-change iteration is causal attribution against the score.
If a construction idea is "obviously" multi-part (new blueprint + new
overlay + new faces), it is a multi-iteration plan — split it, ship the
blueprint change first, measure, then the overlay.

If the idea needs a bikar primitive that doesn't exist, that primitive is
its own task (file it, build it in bikar with its own Tier-0 test per
bikar Tenet 17) — do not fake it with a hand-placed magic-number
approximation (bikar Tenet 9). A missing primitive is a real finding;
surface it.

### Step 3 — Render and VISUALLY VERIFY (Tenet 27 — the ship gate)

Render the new `.bkr` (bikar CLI per Tenet 26) and run the orchestrator:

```bash
./tools/iteration-validate.sh \
    --svg iterations/<N>/render.svg \
    --reference input/reference.jpg \
    --baseline input/baseline.json \
    --out iterations/<N>/validation/
```

Then — **before reading the score** — open the render in the review
portal and look at it against the reference and against the `predicted_cost`
you wrote in Step 1. State what you see. The order matters: if you read the
score first, the eye rationalizes the number. **No iteration is "shipped"
(committed, recorded as the new best, declared converged) without a
recorded review-portal verdict** — that is Tenet 27, and it is the whole
reason the detector can stay frozen: the human eye, not a loosened
threshold, is the acceptance authority.

**After the portal look, land the machine verdict:**

```bash
./tools/portal-handoff.py <session-dir> <N>
```

This writes `iterations/<N>/review-verdict.json`, sha-bound to the render
you just reviewed. `visual-verdict.md` stays the narrative; the JSON is the
machine marker the loop's terminal check and `seed-hypothesis.py` read
(decision `docs/decisions/2026-06-07-loop-terminal-condition.md`, ACCEPTED
Option C — `portal_verdict_recorded` is a conjunct of "converged", so a
review that never runs the handoff doesn't count).

### Step 4 — Measure against the prior iteration

Compare `composite_score` and the specific warning you predicted you'd
clear. Three outcomes:

- **Lift confirmed + visual confirms + no new defect** → record as the new
  best in `evaluation.md`, commit the `.bkr`, advance.
- **Score up but the portal shows a new defect** (a face the metric likes
  but the eye rejects) → NOT shipped. The metric is lying; Tenet 27 caught
  it. Log the divergence, revert or refine.
- **No lift / score down** → the construction hypothesis is falsified for
  this gap. Go to loop-detection.

### Step 5 — Log the outcome in `evaluation.md`

Record observed vs predicted lift, the portal verdict, and whether the
`predicted_cost` materialized. This is the witness the next iteration reads
in Step 1 prerequisite 2.

## Loop-detection — the stop rules (Tenet 7 + memory)

Stop and escalate when ANY fires:

1. **Same construction approach falsified twice.** If two iterations tried
   variants of the same construction idea (e.g. two different overlay-star
   orders) and both failed to lift the score, STOP iterating that idea —
   the gap is deeper than the parameter you're varying. This is the Tenet 7
   stop rule on the construction side; invoke `handle-falsification` on the
   governing decision doc.
2. **Construction-philosophy ceiling.** If the falsifications cluster into
   "the current construction *philosophy* cannot produce the baseline's
   expected vocabulary" (the medallion-10 finding —
   `feedback_a6_baseline_construction_philosophy_mismatch`), STOP. The next
   move is a *different philosophy* (e.g. girih tile primitives), which is
   a scoped bikar feature build, not a loop iteration. Surface it as a
   decision (`present-options`) — don't grind iterations against a ceiling.
3. **You reached for the detector.** If you find yourself wanting to loosen
   a qiyas threshold "just to get this one to match," that is the signal
   the construction hypothesis has run out — STOP and either (a) find the
   real construction defect the detector is correctly flagging, or (b)
   escalate via `escalate-qiyas-divergence` if the detector is genuinely
   wrong. Never tune the detector from this loop.

## Web-search escalation

When a construction hypothesis stalls (rule 1 fired once), web-search the
*construction technique* before the second variant — Islamic-geometry
construction literature (Bonner, Lee, Critchlow, the Topkapi Scroll
analyses) often names the canonical compass-and-straightedge or girih
method for exactly the motif you're failing to reconstruct. A construction
you're hand-deriving may have a documented method that produces the right
face vocabulary directly. Cite the source in the iteration log. This mirrors
`feedback_canonical_algo_web_search` on the construction side.

## Memory contract

- **On resume:** read the construction-philosophy and face-walker memories
  named in prerequisite 1.
- **On a falsification:** write a `feedback`-type memory per
  `handle-falsification` — but only when the lesson is about *construction
  reasoning* (an overlay that can't produce a motif, a face-walker hazard
  that constrains how you can author a shape). A per-pattern score isn't a
  memory; the *generalizable construction constraint* is.
- **On a confirmed lift that breaks a plateau:** note the construction
  move that worked in `discoveries.md` (session-local) AND, if it
  generalizes across patterns, a `feedback` memory.

## Companion skills & tenets

- **`iterate-detector-calibration`** (qiyas) — the mirror loop; that one
  changes the detector against a fixed corpus, this one changes the
  construction against a fixed detector. Know which side you're on.
- **`escalate-qiyas-divergence`** (sacred-patterns) — when the detector is
  genuinely wrong, not just inconvenient; the off-ramp from this loop.
- **`handle-falsification`** / **`present-options`** — when the loop hits a
  ceiling (stop rules 1/2), these capture the dead-end and re-frame the
  options.
- **`learn-new-pattern`** — the authoring skill this loop advances; the
  construction techniques and anti-patterns it loads
  (`generate-drawing/learnings/`) are the source vocabulary for hypotheses.
- **Tenets:** 7 (don't tune to fit — the whole reason this loop exists), 17
  (prove the primitive first — a new construction validates atomic before
  composite), 18 (codify the witness), 23 (DSL-as-source-of-truth — fix the
  construction channel, not the downstream tolerance), 26 (render and look
  while iterating), 27 (no ship without a portal verdict — the gate that
  lets the detector stay frozen).

## Verification — before considering an iteration done

- [ ] `hypothesis.md` frontmatter filled honestly, `detector_untouched: confirmed`,
      `stage:` named and every `.bkr` edit within that stage's vocabulary.
- [ ] Stage 2/3 only: freeze check passed — `structure-diff.sh` re-run,
      `skeleton_sha256` byte-identical to the gated one.
- [ ] No `TODO(judgment)` remains in `hypothesis.md` — every judgment field
      authored by you, not the seed.
- [ ] Exactly one construction idea changed; no qiyas param touched.
- [ ] Render viewed in the review portal BEFORE reading the score; verdict recorded (Tenet 27).
- [ ] `tools/portal-handoff.py` run after the review — `iterations/<N>/review-verdict.json`
      exists and sha-matches the render.
- [ ] `composite_score` compared to prior iteration; predicted warning checked.
- [ ] Outcome logged in `evaluation.md`; falsification (if any) routed to a stop rule.
- [ ] If a stop rule fired: escalation skill invoked (handle-falsification / present-options / escalate-qiyas-divergence), not a third blind variant.
- [ ] Bookkeeping synced (Cookbook #15): verdict in hypothesis.md,
      `session.json` waves_passed updated on a pass, progress sheet
      regenerated + copied to `progress.png`.
