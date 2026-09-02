---
name: bikar-polygon-corner-leakage-deg4-non-monotonic
description: "REFUTED 2026-05-27 by Tick 91: D_8 octagon at deg-4 + 1 lens + safe tangents emitted CLEAN ESCAPE despite being predicted LEAK as 3rd even-D witness. Parity rule (even-D leak / odd-D clean) is FALSE at D_8 — D_8 edges (67.5°/112.5°) are symmetric about polygon-interior axis (the predicted leak mechanism) yet produce no leakage. New pattern at N=6 witnesses: only D_4 LEAK×1 and D_6 LEAK×2 leak; D_3, D_5, D_7, D_8 all CLEAN. The actual variable is NOT D parity. Candidate replacement hypotheses: (a) leak-window restricted to low-even-D (D_4, D_6) only, mechanism uncharacterized; (b) leak correlates with a specific edge-tangent value (e.g., 45° or 60° appearing in canonical polygon angle sets); (c) leak depends on edge-vs-CL_a tangent interaction not edge-vs-CL_shared. PRIOR strengthened-claim (Tick 90, FALSIFIED): even-D-leak / odd-D-clean parity at N=5 witnesses, predicted D_8 LEAK."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

## Falsification log

### 2026-05-27 — Parity rule falsified at D_8 (Tick 91)

**What was tried:** Authored `octagon-with-lens-at-vertex-separated-tangents.bkr.tmpl` as Tick 91 probe to test parity rule's prediction that D_8 (3rd even-D witness) should LEAK. Construction mirrored Ticks 87-90: CL_shared at (89.5811, 59.0885) r=60 tangent 10°; CL_a tangent 151.25° (unique safe-tangent window center, min-sep 38.75°). Octagon inscribed in C0, P=cpt0=(100,0).

**How it failed:** Render emitted 5 shapes with BOTH faces pure: shape[0] `.octagon×8` (zero `.lens_a` leak), shape[1] `.lens_a×2` (zero `.octagon` leak). Predicted LEAK; got CLEAN ESCAPE. Fingerprint identical to D_3/D_5/D_7 — D_8 joins the clean witnesses, not the leak witnesses.

**Root reason (current best understanding):** The parity rule's *mechanism* — "even-D polygon edges symmetric about polygon-interior axis → tangent-sort tie-break fires → leak" — is wrong as stated. All inscribed regular even-N polygons have edges symmetric about their vertex's polygon-interior axis (it's a property of regular even-N polygons by construction). If symmetry alone caused the leak, D_8 would leak too. The actual load-bearing variable is something else that *correlates* with even-D at N=4 and N=6 but breaks down by N=8. Looking at the data: D_4 edges land at 45°/135°, D_6 at 60°/120°, D_8 at 67.5°/112.5°. The "leak" witnesses (D_4, D_6) have edge tangents at canonical 45°/60° values; D_8's 67.5° isn't in any canonical set. This is a single thread of evidence — not a proven mechanism.

**What this falsifies in the doc:**
- [x] The picked option's mechanism (parity rule's "even-D symmetric → leak" claim)
- [x] The option enumeration (the rule should have been authored with explicit alternatives like "low-even-D only" or "specific-tangent-value-dependent")
- [ ] The doc's framing question — "what predicts polygon-corner leak at deg-4 + 1 lens" is still the right question
- [x] The audit / impact analysis — the symmetric-about-interior-axis check wasn't actually computed for D_8 before predicting LEAK; if it had been, the prediction would have noted D_8 ALSO has the symmetric property (since all regular even-N polygons do)

**Falsification artifacts:** qiyas template `calibration/i1-corpus/templates/octagon-with-lens-at-vertex-separated-tangents.bkr.tmpl` and render `calibration/i1-corpus/renders/octagon-with-lens-at-vertex-separated-tangents/pattern.gt.json` (5 shapes, both faces pure); this conversation's geometric-pattern computation script (D_3..D_8 edge tangents + verdict table).

### 2026-05-27 — H3 refuted at D_4 (Tick 92)

**What was tried:** Authored `square-with-shifted-lens-at-vertex-separated-tangents.bkr.tmpl` as Phase-2 first probe to discriminate H3 (edge-vs-CL_a interaction) from H1 (canonical tangent values) and H2 (low-even-D-only). Construction kept the Tick 82 baseline IDENTICAL — same C0, same square, same P=cpt0, same CL_shared at (42.0445, 15.5291) r=60 tangent 75° — and shifted ONLY CL_a from tangent 105° (Tick 82) to tangent 0° (CL_a center=(100,-40) r=40). Tangent 0° picked as maximally distant safe-window-center from Tick 82's 105° (safe windows from 0.5° sweep: 105° single point, (0°,15°), (165°,180°)).

**How it failed:** Render emitted 5 shapes with LEAK fingerprint IDENTICAL to Tick 82: shape[0] square-emergent face polyclass-contaminated with `.lens_a×1` leak tag (src=['.lens_a', '.square'×4, 'C0:arc:#1', 'layer:0'×5, 'square_poly'×4]); shape[1] PURE lens_a×4; 3 circles. Same shape count, same leak count, same directional asymmetry as Tick 82.

**Root reason (current best understanding):** CL_a placement within the safe-tangent envelope is NOT the load-bearing variable for the D_4 leak. The leak survives intact under a 105° rotation of CL_a's tangent. H3 (edge-vs-CL_a interaction) is REFUTED as the discriminating variable — whatever mechanism causes D_4 and D_6 to leak while D_3/D_5/D_7/D_8 stay clean does NOT depend on which specific safe-tangent angle CL_a takes.

**What this falsifies in Phase 2 search:**
- [x] H3 (edge-vs-CL_a interaction) — REFUTED. CL_a's tangent value within safe envelope is not the load-bearing variable.
- [ ] H1 (canonical tangent values 45°/60°) — still alive but STRUCTURALLY UNTESTABLE with regular polygons inscribed in C0 (square edges fixed at 45°/135°; hexagon edges fixed at 60°/120°). To test H1, must construct a NON-REGULAR polygon with edges at non-canonical tangents (e.g., scalene quadrilateral with edges at 50°/130° instead of 45°/135°).
- [ ] H2 (low-even-D only, mechanism uncharacterized) — still alive; becomes the default framing if H1 also refuted; direct path is bikar source-level audit.

**Falsification artifacts:** qiyas template `calibration/i1-corpus/templates/square-with-shifted-lens-at-vertex-separated-tangents.bkr.tmpl` and render `calibration/i1-corpus/renders/square-with-shifted-lens-at-vertex-separated-tangents/pattern.gt.json` (5 shapes, square face polyclass with `.lens_a×1`, lens face pure).

**Next probe (Tick 93 candidate):** scalene quadrilateral at P with one edge at 50° (non-canonical), CL_shared 75°, CL_a 105° (Tick 82 values). Tests H1 directly. If non-regular CLEAN-ESCAPES → H1 confirmed (canonical tangent values are the trigger). If still LEAKS → H1 refuted, accept H2 + open bikar source-audit task.

### 2026-05-27 — H1 CONFIRMED at D_4 via non-canonical tangents (Tick 93)

**What was tried:** Authored `scalene-quad-with-lens-at-vertex-non-canonical-tangents.bkr.tmpl` to discriminate H1 (canonical tangent values 45°/60° as trigger) from H2 (low-even-D-only, mechanism uncharacterized). Construction kept the Tick 82 baseline lens IDENTICAL — same CL_shared at (42.0445, 15.5291) r=60 tangent 75°, same CL_a at (61.363, -10.3528) r=40 tangent 105° — and replaced the regular square (edges pinned at 45°/135° by C0 inscription) with a SCALENE quadrilateral [P A B D] whose edges at P land at NON-CANONICAL 35° (P→D) and 145° (P→A) tangents (≥30° from both CL_shared and CL_a). Vertices A=(165.53,45.89), B=(83.75,117.93), D=(1.70,68.83) realized via auxiliary radius-1 anchor circles (bikar blueprint forbids `point` statement; off-C0 cartesian vertices must be cpt of named circles). Edge lengths PA=80, AB=109, BD=95.6, DP=120 (4 distinct values, scalene per Tenet 8 asymmetric-witness requirement).

**How it succeeded:** Render emitted 8 shapes with BOTH faces PURE. shape[0] scalene_quad face src=`['.scalene_quad'×4, 'layer:0'×4, 'scalene_quad_poly'×4]` — ZERO `.lens_a` leak. shape[1] lens face src=`['.lens_a'×2, 'C_D:arc:#0'×2, 'C_D:arc:#1'×2, 'layer:0'×4]` — `C_D:arc` traces are auxiliary anchor-circle DCEL fragments, not class leak; ZERO `.scalene_quad` leak. Render.svg confirms via `data-face-class="scalene_quad" data-sides="4"` and `data-face-class="lens_a" data-sides="2"`. CLEAN ESCAPE fingerprint identical to D_3/D_5/D_7/D_8.

**Root reason (current best understanding):** Polygon-edge tangent value at P IS the load-bearing variable for the D_4 leak. Tick 82's LEAK reproduced for ~6 ticks under varying CL_a placement (Tick 92 confirmed CL_a-within-safe-envelope is not load-bearing); changing ONLY the polygon edges from canonical 45°/135° to non-canonical 35°/145° at otherwise-identical lens topology eliminates the leak entirely. The mechanism: bikar's tangent-sort tie-break at degree-4 polygon-corner DCEL vertices has special-case behavior when polygon-edge tangents equal canonical values (45° = atan2(1,1), 60° = atan2(√3,1)) that classical regular-polygon constructions concentrate at — likely an epsilon-sensitive comparator or a hash-collision in the sort key, not a designed special case.

**What this confirms in Phase 2 search:**
- [x] H1 (canonical tangent values 45°/60° are the leak trigger) — CONFIRMED at D_4 via non-canonical edges.
- [x] H2 (low-even-D-only, mechanism uncharacterized) — REFRAMED. The "low-even-D" correlation at N=6 witnesses was a coincidence: D_4 and D_6 are the regular polygons whose edges land at canonical 45° and 60°; D_8's 67.5° isn't canonical (hence CLEAN at Tick 91). H2 is not a mechanism, it's a side effect of which regular polygons happen to have canonical-tangent edges.
- [x] H3 (edge-vs-CL_a interaction) — already REFUTED by Tick 92.

**Confirmation artifacts:** qiyas template `calibration/i1-corpus/templates/scalene-quad-with-lens-at-vertex-non-canonical-tangents.bkr.tmpl` and render `calibration/i1-corpus/renders/scalene-quad-with-lens-at-vertex-non-canonical-tangents/{pattern.gt.json, render.svg}` (8 shapes; scalene_quad face PURE, lens face PURE).

**Cascade transition:** Phase 2 of qiyas#132 polygon-corner-leakage matrix CLOSES with H1 confirmed. Phase 3 OPENS as a bikar source-level audit — grep `packages/core/src/dsl/evaluator.ts` and face-extractor files for the tangent-sort comparator at degree-4 polygon-corner vertices; identify whether 45°/135° and 60°/120° are special-cased (atan2(1,1)=45°, atan2(√3,1)=60°) or fall out of a generic comparator with epsilon-sensitive behavior. Corpus Ticks 82 (D_4 LEAK), 88 (D_6 LEAK), 87/89/90/91/92 (CLEAN regular polygons), 93 (CLEAN scalene at non-canonical tangents) become the regression suite for the fix.

**Optional cross-confirmation (Tick 94 candidate, deferrable):** scalene hexagon (D_6) with one vertex at P and edges shifted from canonical 60°/120° to non-canonical 50°/130° at otherwise-identical-to-Tick-88 lens topology. Predicted CLEAN. If CLEAN: H1 cross-confirmed at the other LEAK fingerprint witness, closes matrix. If LEAKS: H1 narrowed to D_4-specific, reopen mechanism question. NOT required to start Phase 3 source audit; the audit can proceed in parallel.

**Post-ship disambiguation check (2026-05-27):** The Tick 93 template includes two `classify ... where sides == N` rules that Tick 82 lacks; this could have explained the CLEAN ESCAPE via the `faceClasses` Map path in gt-emitter (resolveFaceClassFromMap line 1062) instead of via tangent-value mechanism. Confounding-variable check ran: stripped both classify rules from `/tmp/tick93-disambig/pattern.bkr`, re-rendered with bikar CLI. Result: 8 shapes (same), shape[0] PURE `.scalene_quad`×4 (zero `.lens_a` leak), shape[1] PURE `.lens_a`×2 (zero `.scalene_quad` leak). H1 stands — classify rules only affect `face_class` field; the leak fingerprint is in `source_primitives` multiset which is upstream of classify resolution. Source-primitives accumulation happens via edge-tag propagation in face-walker traversal, independent of classify rules. The cascade-transition to Phase 3 source audit is genuinely sound.

### 2026-05-27 — Phase 3 source audit narrows mechanism to tangent-INTERLEAVING (not tangent-VALUE)

**Refined mechanism (2026-05-27):** Re-examining Tick 82 vs Tick 93 outgoing-tangent ordering at P reveals the true load-bearing variable is **tangent interleaving**, not canonical-value membership:

- **Tick 82 (LEAK, square inscribed in C0):** P=(100,0); polygon edges P→cpt1 tangent 135°, P→cpt3 tangent 225°; lens arcs CL_shared 75°, CL_a 105°. CCW outgoing order from 0°: **[75° lens, 105° lens, 135° poly, 225° poly]** — lens tangents on one half-plane, polygon tangents on the other. ZERO interleaving.

- **Tick 93 (CLEAN, scalene):** P=(100,0); polygon edges P→A 35°, P→D 145°; lens arcs CL_shared 75°, CL_a 105°. CCW order: **[35° poly, 75° lens, 105° lens, 145° poly]** — polygon edges bracket the lens tangents. FULL interleaving.

- **Tick 92 (LEAK, square + shifted CL_a):** square edges 135°/225°; CL_shared 75°, CL_a 0°. CCW order: **[0° lens, 75° lens, 135° poly, 225° poly]** — same separation pattern as Tick 82 (lenses then polys). LEAK fingerprint preserved (Tick 92's "H3 refuted" finding now makes sense: CL_a movement within {0°, 105°} both stay on the same side of polygon-edge sector).

- **Tick 91 (CLEAN, octagon D_8):** polygon edges 67.5°/112.5° at P; lens CL_shared 10°, CL_a 151.25°. CCW order: **[10° lens, 67.5° poly, 112.5° poly, 151.25° lens]** — lens arcs bracket the polygon edges. FULL interleaving (inverted bracketing direction).

**The mechanism (refined):** At a degree-4 polygon-corner DCEL vertex, when polygon-edge tangents at P are **angularly separated from lens-arc tangents into two contiguous sectors** (no interleaving), bikar's face-walker correctly walks each face but the per-edge-tag-set inheritance during cycle traversal incorrectly attributes shared-vertex outgoing-edge tags to the polygon face. When polygon and lens tangents **interleave** (alternate around P), the face-walker's CCW `next`-pointer chain naturally separates the cycles cleanly.

**This is a face-extractor / cycle-walker tag-attribution bug, not a tangent-sort comparator bug.** `compareOutgoing` in planar-graph-builder.ts works correctly — the bug is downstream, in how `collectCycleProvenance` (face-extractor.ts:17) accumulates tags from half-edges along the cycle. When the cycle's `next` pointer momentarily walks through a half-edge that has lens-arc tags (the half-edge at the shared vertex P pointing toward the lens), those tags get added to the cycle's `edgeSources` even if that half-edge's "twin" is the actual polygon edge.

**H1 is REFINED, not abandoned:** Canonical tangent values (45°/60°) happen to produce non-interleaved configurations for regular inscribed polygons (square edges land at 135°/225° from vertex on C0, hexagon at 60°/300°, etc.) which DON'T interleave with lens arcs at the typical 75°/105° construction angles. Non-canonical values like D_5 pentagon (54°/126° edges from vertex) DO interleave with 75°/105° lens arcs (54° → 75° → 105° → 126°), explaining CLEAN ESCAPE without any tangent-value-specific mechanism. The "canonical tangent value" framing was a *correlation* with the actual *interleaving* causation.

**Predictive verification (must compute before next probe):** For each prior Tick (82/87/88/89/90/91/92/93), compute outgoing-tangent CCW order at P and check interleaving. Prediction: ALL LEAK ticks (82, 88, 92) have non-interleaved (polygon-tangents-contiguous OR lens-tangents-contiguous) ordering; ALL CLEAN ticks (87, 89, 90, 91, 93) have interleaved (alternating polygon-lens-polygon-lens or lens-polygon-lens-polygon) ordering.

**Phase 3 source-fix target (next):** The bug lives in face-extractor.ts:23-46 (`collectCycleProvenance`) — the cycle walks `halfEdges[heIdx].tags` but doesn't verify the half-edge actually belongs to the polygon-side of a shared vertex. Need to add a discriminator that distinguishes "edge tags from this face's own boundary" from "edge tags from a sibling face that shares this vertex." Open question: is the `face` field on half-edges (line 24) reliable enough as a discriminator, or does the cycle walker traverse half-edges that are still face=-1 when their tags get collected?

### Post-falsification N=6 matrix at deg-4 + 1 lens + safe tangents

| D | Interior | Edges at P (mod 180°) | min sep from CL_shared(10°) | Verdict |
|---|---|---|---|---|
| 3 | 60° | 30°/150° | 20° | CLEAN |
| 4 | 90° | 45°/135° | 35° | **LEAK ×1** |
| 5 | 108° | 54°/126° | 44° | CLEAN |
| 6 | 120° | 60°/120° | 50° | **LEAK ×2** |
| 7 | 128.57° | 64.29°/115.71° | 54.29° | CLEAN |
| 8 | 135° | 67.50°/112.50° | 57.50° | CLEAN |

**Observation:** No clean separation function over min-sep or interior angle. D_4 and D_6 are the only leakers across the 6-witness range. Candidate replacement hypotheses (uncharacterized):
- **(H1) Specific-tangent-value:** leak fires when polygon-edge tangent at P equals 45° or 60° (canonical angles appearing in classical polygon constructions). D_4 has 45°, D_6 has 60°; D_3 (30°/150° — neither 45° nor 60°), D_5 (54°/126°), D_7, D_8 don't. *Predicts D_12 LEAK at 60°/120° too — but D_12 has the same edge tangents as D_6 (60° = 60° mod 180°, edges differ in cpt-2 direction); needs deeper geometric check.*
- **(H2) Low-even-D-only:** leak restricted to D_4 and D_6; D_8+ all clean. Mechanism uncharacterized but predictively narrow.
- **(H3) Edge-vs-CL_a interaction:** since CL_a tangent varies per polygon (90° at D_3/D_5; 150° at D_6; 153° at D_7; 151.25° at D_8), maybe edge-vs-CL_a matters and we've been looking at the wrong pair. Re-tabulate: D_4 edge_45 vs CL_a(?)... need to check what CL_a was for D_4 in Tick 82.

The mechanism is now genuinely unknown; the parity rule was a coincidence pattern at N=5 that broke at N=6.



When a polygon vertex P doubles as the corner of a single lens at safe-separation tangents (≥30° pairwise) at minimum-degree DCEL (degree-4 = 2 polygon edges + 2 lens arcs), the polygon-corner tag-leakage follows an EVEN-D-LEAK / ODD-D-CLEAN parity rule (4 witnesses, zero counter-examples as of Tick 89). The matrix at deg-4 + 1 lens + safe tangents:

- **Square (90° interior, D_4, Tick 82):** PARTIAL LEAK. Polygon face polyclass-mixed with `.lens_a` (1 tag); lens face stays pure. **EVEN.**
- **Pentagon (108° interior, D_5, Tick 87):** CLEAN ESCAPE. Both polygon face AND lens face pure; zero leakage. **ODD.**
- **Hexagon (120° interior, D_6, Tick 88):** PARTIAL LEAK. Polygon face polyclass-mixed with `.lens_a×2` (2 tags); lens face stays pure. **EVEN.**
- **Heptagon (128.57° interior, D_7, Tick 89):** CLEAN ESCAPE. Both polygon face AND lens face pure; zero leakage. Fingerprint identical to D_5 pentagon. **ODD.**

**Why:** qiyas#132 Tick 88 (2026-05-27) authored `hexagon-with-lens-at-vertex-separated-tangents.bkr.tmpl` to discriminate "square-only leakage anomaly" (Tick 87's reading after pentagon PASS) from "low-D_N graded" pattern at deg-4 + 1 lens. Geometry mirrors Tick 87 lens topology (CL_shared + CL_a both through P, NOT C0+CL): C0=(0,0) r=100 ÷6 → hexagon inscribed; P=C0.cpt0=(100,0). CL_shared=(89.5811, 59.0885) r=60 (tangent 10° at P, identical to Tick 87 CL_shared); CL_a=(120, 34.6410) r=40 (tangent 150° at P, center perpendicular to tangent in +x/+y away from hexagon interior). Hexagon edges at P: P→cpt1 tangent 120°, P→cpt5 tangent 60°. Pairwise tangent differences (mod 180°): edge_60 vs edge_120 = 60° (exterior wedge), edge_60 vs CL_shared(10°) = 50°, edge_60 vs CL_a(150°) = 90°, edge_120 vs CL_shared(10°) = 70°, edge_120 vs CL_a(150°) = 30°, CL_shared vs CL_a = 40°. Minimum separation 30° (at hazard threshold, NOT below, no co-tangent — same hazard level as Ticks 82/83/87).

**Render verdict (PARTIAL LEAK, Risk (i) D_6 LEAK CONFIRMED):**
- shape[0]: type=unknown (lens-cycle), src=[`.lens_a`×4, `C0:arc:#0`×2, `C0:arc:#1`×2, `layer:0`×4] — PURE lens-cycle, NO `.hexagon` leak
- shape[1]: type=unknown (hexagon-dominant polyclass), src=[`.hexagon`×6, `.lens_a`×2, `C0:arc:#0`, `C0:arc:#1`, `hexagon_poly`×6, `layer:0`×8] — TWO `.lens_a` leak tags on hexagon face
- shapes[2-4]: 3 circles

Total 5 shapes. PARTIAL fingerprint mirrors Tick 82's square+lens_a contamination shape. Hexagon leaks **2** lens tags vs square's **1** — leak count appears to scale with polygon edge count, but with only 2 even-D witnesses the trend is tentative.

**The refuted reading:** Tick 87's "leakage is square-specific at deg-4 + 1 lens + safe tangents" claim is FALSE. **Tick 89 STRENGTHENS the parity reading from tentative to predictive:**
- **Even-D polygons (D_4, D_6) LEAK** at deg-4 minimum (D_4: 1 lens tag, D_6: 2 lens tags); both with lens face staying pure.
- **Odd-D polygons (D_5, D_7) CLEAN** at the same matrix cell; both faces pure (2-witness odd-D class).

Pentagon is no longer the single-witness anomaly. D_5 and D_7 form a 2-witness odd-D-clean class; D_4 and D_6 form a 2-witness even-D-leak class. The parity rule is now load-bearing with 4 supporting witnesses and zero counter-examples. The square's anomaly is specifically at deg-6 (escapes when triangle/hexagon absorb, Ticks 83/85); the deg-4 matrix is no longer about per-polygon anomalies but about the parity of D_N itself.

**Cross-matrix observation:** the deg-4 + 1 lens matrix mirrors the deg-6 + safe tangents matrix's non-monotonic zigzag pattern:
- Deg-6 matrix (interior angle order): 60° absorb → 90° escape → 120° absorb → 135° partial-escape. Zigzag.
- Deg-4 matrix (interior angle order): 90° leak → 108° clean → 120° leak. Zigzag at the same parity (odd-D escapes, even-D leaks/absorbs).

**Refined mechanism (parity-rule, N=4 witnesses):** bikar's tangent-sort tie-break at degree-N DCEL vertices is sensitive to polygon-edge tangent symmetry relative to the polygon-interior axis at P. Even-D polygons (D_4, D_6, D_8) have polygon-edge tangents symmetric about the polygon-interior axis (square at ±45°; hexagon at ±60°; octagon at ±67.5°) → LEAK. Odd-D polygons (D_3, D_5, D_7, D_9) have polygon-edge tangents asymmetric about the polygon-interior axis (pentagon at 54°/126°; heptagon at 64.29°/115.71°) → CLEAN. The asymmetry in odd-D is what allows clean escape at deg-4 (Tick 89 confirmed this for D_7). Closed-form rule still requires source-level audit, but the parity prediction is now falsifiable: D_8 → LEAK (3rd even-D), D_9 → CLEAN (3rd odd-D), D_3 → CLEAN (small-D limit).

**How to apply:** (a) **Parity-rule leakage prediction** (replaces all prior anomaly-framings): polygon-corner-shared lens vertex at deg-4 minimum + safe tangents leaks tags iff D_N is EVEN; D_3/D_8/D_9 are now falsifiable predictions (D_3/D_9 → CLEAN, D_8 → LEAK); (b) **For cascade authoring:** the polygon-anchored escape hatch's safety claim at deg-4 + 1 lens + safe tangents is empirically NEGATIVE for even-D polygons and POSITIVE for odd-D polygons (2 witnesses each); treat even-D polygon faces as "expect N lens tag leakage proportional to polygon edge count" and odd-D polygon faces as "expect clean escape"; (c) **For downstream consumers:** dominant-tag voting remains universally safe (in both Tick 82 D_4 and Tick 88 D_6 the dominant tag was `.polygon`; lens tag count was 1-2 of N polygon tags); treating "pure polygon face with zero lens leakage" as a polygon-face witness at HIGH confidence is appropriate for odd-D (D_5, D_7); (d) **Open follow-up witness candidates** (in Tenet 17 simplest-first order): triangle (D_3, 60° interior) — small-D limit, predicted CLEAN; octagon (D_8, 135° interior) — 3rd even-D witness, predicted LEAK; nonagon (D_9, 140° interior) — 3rd odd-D witness, predicted CLEAN; (e) **The witness IS the prediction:** bikar's face-walker behavior at deg-4 + 1 lens + safe tangents is now documented across 4 ticks (82 D_4 leak +1tag, 87 D_5 clean, 88 D_6 leak +2tag, 89 D_7 clean); the parity rule is load-bearing enough to make pre-render predictions — the next 1-2 ticks should be designed to falsify rather than confirm.

**Companion to:** [[feedback_bikar_polygon_corner_leakage_is_square_specific]] (Tick 87 — "square-specific" claim NOW REFINED by this entry to "even-D leak, odd-D clean" tentative rule; pentagon was misframed as proving square multi-anomaly), [[feedback_bikar_polygon_anchored_escape_is_graded_non_monotonic]] (Tick 86 — deg-6 matrix non-monotonic; this entry shows deg-4 matrix has the same non-monotonic structure), [[feedback_bikar_polygon_anchored_escape_is_square_specific]] (Tick 85 — original deg-6 square-only claim, refined by Tick 86), [[feedback_bikar_polygon_corner_sharing_universal_tag_leakage]] (Tick 82 — "universal-leakage" claim refuted by Tick 87 was correct *direction*; this entry shows leakage is universal *across even-D* but not odd-D), [[feedback_bikar_polygon_corner_degree_orthogonal_to_tangent]] (Tick 83 — square-deg-6 escape claim still narrows to single witness in its matrix), [[feedback_bikar_homogeneous_radius_degree_4_tangent_contamination]] (Ticks 77/79 — underlying tangent-sort tie-break defect that likely powers all polygon-class anomalies in both deg-4 and deg-6 matrices).
