---
status: ACCEPTED 2026-05-20
discovered: 2026-05-20
decided: 2026-05-20
owner: omar (sacred-patterns owner)
related:
  - tenet: sacred-patterns/CLAUDE.md Tenet 23 — DSL-as-source-of-truth
  - contract: sacred-patterns/docs/dsl-metadata-contract.md
  - plan: bikar/.claude/plans/is-there-an-actionalble-logical-cascade.md
  - cross-repo: qiyas#490 (symptom), qiyas#400 (parallel cascade), qiyas#488 + #486 (blocked CI), bikar#333 (Slice 2 origin)
  - superseded-doc: qiyas/docs/decisions/2026-05-20-qiyas-anti-symmetry-floor-breach.md (Option A retained as bridge)
---

# Universal DSL-Authored Tagging — cross-repo cascade

## Layman summary

Today the pipeline is **bikar DSL → SVG → qiyas detector**. Three failure modes keep recurring because qiyas re-derives facts from raster/SVG geometry that bikar already *knew* at authoring time: squares get lumped into `unknown` (qiyas#400), the matcher pairs a Star-8 face against a Hexagram face as equals (qiyas#490), and the symmetry pillar mis-scores fold-8 vs fold-6 as related (qiyas#490). Each was patched individually. The cumulative pattern is the actual bug: **qiyas re-derives what bikar already declared**, and the patches make the heuristics noisier instead of removing the re-derivation.

The decision: ship the universal tagging cascade — bikar emits the facts it knows as `data-*` SVG attributes, qiyas reads them as authoritative, the matcher and scorer consult them first, geometric re-derivation becomes the fallback for the photo cascade only.

## Implications of getting this wrong

- **Wrong → the patches compound noise.** If we keep patching per-symptom (qiyas#490 Option A as the only fix), each new failure mode adds a heuristic with a threshold. Tenet 7 — every threshold is a future failure source the next iteration agent will tune-to-fit.
- **No-pick → the symptom recurs at every refactor.** The bikar SVG emitter and qiyas Contour schema have been refactored four times in two months. Each refactor silently drops the previous attempt at metadata carry-through (qiyas#400 Slice 2 had to re-add `data-sides` after a 2026-04-30 svg_primitives refactor dropped it). Without a contract, the next refactor drops it again.
- **Hard to undo.** SCHEMA bumps are commitment surface. Once `face_class` and `symmetry_fold` land on Contour, every qiyas fixture and the cross-repo CI gate inherit them. The contract shape needs to be right on first land — but the contract is *additive* (optional fields with documented fallbacks), so this risk is bounded by the fallback discipline.

## Main questions we need answered

1. **Does the SVG `data-*` carry-through pattern have prior art at this scale?** — answered via WebSearch: yes, every browser-rendered DSL (Vega, Mermaid, D3, React-Flow) treats `data-*` as the canonical metadata channel; W3C SVG 2 spec endorses the pattern (any element carries arbitrary author metadata).
2. **Does the matcher / scorer pattern (consume producer-provided labels before re-deriving) have prior art?** — answered: yes, DETR (Carion et al. 2020) is the canonical reference for Hungarian matching with class-confidence cost weighting; same citation as the qiyas#490 Option A decision doc.
3. **Will the SCHEMA bump (1.14 → 1.15) regress the byte-strict fixtures?** — open at decision time; mitigation is the 2026-05-20 byte-strict decision (Option D: pair byte-strict with meaning-level invariants) per the `_meaning_equal` pattern qiyas/tests/fixtures/ adopted.
4. **Will the bikar emitter additions break any existing test?** — answered by Explore: no, `face.sources` already carries the rotational source tags; emit is a non-semantic addition.
5. **Will qiyas#488 + #486 unblock soon enough that we don't need the bridge fix?** — open: if not, ship qiyas#490 Option A as the bridge in parallel with Slice 1–3 of this cascade; Option A gets deleted after Slice 3 lands.

## Options considered

### Option A — Ship the universal tagging cascade (RECOMMENDED)

**Layman:** make bikar emit every fact its DSL knows authoritatively as a SVG `data-*` attribute; make qiyas read them as authoritative; geometric re-derivation becomes the fallback for the photo cascade.

**What changes:** sacred-patterns adds Tenet 23 + DSL Metadata Contract v1. Bikar extends `svg-renderer.ts:219-236` to emit `data-face-class` + `data-symmetry-fold` (Phase 1) and later `data-construction-source` (Phase 2). Qiyas extends `Contour` with `face_class`, `symmetry_fold`, `construction_source` fields; SCHEMA 1.14 → 1.15. Matcher's Hungarian cost gets a class-mismatch penalty when both sides carry `face_class`. Scorer's `_check_dominant_fold` consults `symmetry_fold` first. Slice 5 wires a `qiyas validate-dsl-contract --strict` CI gate to lock the contract.

**Presentation — concrete shape:**

```html
<!-- bikar SVG output, post-Slice 1 (Star-8 face): -->
<path d="M…Z"
      class="petal" fill="#1B6CA8"
      data-face-index="3" data-sides="4" data-layer="0"
      data-face-class="petal" data-symmetry-fold="8" />
```

```python
# qiyas Contour, post-Slice 2 (SCHEMA 1.15):
class Contour(BaseModel):
    vertices: list[tuple[float, float]]
    # …existing fields…
    authoritative_sides: int | None = None
    face_index: int | None = None
    layer: int | None = None
    source_tag: SourceTag | None = None
    face_class: str | None = None       # NEW
    symmetry_fold: int | None = None    # NEW
    construction_source: list[str] | None = None  # NEW (Phase 2)
```

```python
# qiyas matcher (Slice 3), Hungarian cost with class-mismatch:
def _hungarian_cost(ref: Shape, recon: Shape) -> float:
    cost = _geometric_cost(ref, recon)
    if ref.face_class and recon.face_class and ref.face_class != recon.face_class:
        cost += CLASS_MISMATCH_COST  # ≈ 100, dominates pairing
    return cost
```

**Web research:**
- W3C SVG 2 specification — `data-*` author-metadata pattern, every element carries arbitrary key/value pairs preserved through DOM and serialization — [SVG 2 — Embedded Content](https://www.w3.org/TR/SVG2/embedded.html)
- DETR (Carion, Massa, Synnaeve, Usunier, Kirillov, Zagoruyko 2020) — bipartite matching with class-confidence cost weighting (the canonical pattern for "use producer-provided labels in the cost function") — [End-to-End Object Detection with Transformers (arXiv 2005.12872)](https://arxiv.org/abs/2005.12872)
- Vega-Lite — declarative DSL that emits SVG with extensive `data-*` annotations for downstream test/debug pipelines; canonical example of DSL-as-source-of-truth — [Vega-Lite documentation](https://vega.github.io/vega-lite/)

**Pros:**
- Dissolves qiyas#490 at the root (face_class mismatch is hard cost, not a soft heuristic).
- Closes the unrecovered slice of qiyas#400 (face_class makes the polygon classifier short-circuit even when geometric vertex-count would fail).
- Generalizes: every future "qiyas re-derives X" failure mode dissolves into "extend the contract with the corresponding `data-*` attribute."
- Contract is additive — every field is optional with a documented fallback; pre-#333 bikar, vtracer-traced SVG, and photos keep working unchanged.
- Slices are independently shippable; bikar can ship emit before qiyas ships consume.

**Cons:**
- Schema bump touches the byte-strict fixture surface (mitigated by the 2026-05-20 byte-strict decision Option D).
- 6 slices × ~1 day each = ~6 days, vs Option C's ~1 day (cost is real).
- Slice 3 of qiyas#400 (commit fa7e836) just landed; the new fields overlap conceptually with `authoritative_sides`. Risk: confusion about which field "wins." Mitigation: contract doc names the consumer for each.

**Cost:** 6 days (3 days for Phase 1 = Slices 0–3 unblocks #488 + #486; 3 days for Phases 2+3+CI gate).

**Closes which questions from §4:** 1 (yes, prior art is dense), 2 (yes, DETR is canonical).
**Leaves open which questions:** 3 (SCHEMA bump risk — mitigated by Option D), 4 (resolved: no breakage), 5 (CI deadline — mitigated by parallel bridge).

**Tenet alignment:**
- Tenet 1 (simplicity): re-derivation is the complex path; reading a label is the simple path. This option moves the complexity to one-time setup (the contract) instead of every read site.
- Tenet 2 (root cause): names the root cause (qiyas re-derives what bikar declared); the per-symptom patches treated symptoms.
- Tenet 7 (don't tune to fit): replaces the heuristic threshold path with a contract-based hard signal — no future threshold-tuning needed once the contract is wired.
- Tenet 11 (don't add new flag for old problem): this is the existing tag-based approach (qiyas#400 Slice 2) generalized, not a parallel mechanism.
- Tenet 23 (the new tenet): this option IS the application of Tenet 23.

### Option B — Status-quo: per-symptom patches (qiyas#490 Option A only)

**Layman:** keep the existing per-symptom patch path. Ship qiyas#490 Option A (Hungarian hint-vs-no-hint penalty) as a standalone fix. Leave qiyas#400 F3 unfixed for shapes the polygon classifier still misses. The next failure mode gets its own patch.

**What changes:** only qiyas#490 Option A — ~50 lines in `qiyas/src/qiyas/diff/matcher.py` adding `HINT_GEOMETRIC_MISMATCH_PENALTY` to the Hungarian cost when one side has `authoritative_sides` and the other does not.

**Presentation — concrete shape:**

```python
# qiyas matcher (Option A patch only):
def _hungarian_cost(ref: Shape, recon: Shape) -> float:
    cost = _geometric_cost(ref, recon)
    ref_hinted = ref.authoritative_sides is not None
    recon_hinted = recon.authoritative_sides is not None
    if ref_hinted != recon_hinted:
        cost += HINT_GEOMETRIC_MISMATCH_PENALTY  # ≈ 50
    return cost
```

**Web research:**
- DETR (Carion et al. 2020) — same citation; supports the matcher-cost-penalty approach as a building block, but the literature also notes that pure asymmetric penalties (hint vs no-hint) are a brittle slice of the full class-confidence cost (which Option A above takes the rest of) — [arXiv 2005.12872](https://arxiv.org/abs/2005.12872)
- "Hidden technical debt in machine learning systems" (Sculley et al., NeurIPS 2015) — coined "feedback loops" and "correction cascades" for exactly this pattern: each per-symptom fix is correct in isolation but accumulates noise that the next fix has to compensate for — [Sculley et al. 2015](https://papers.nips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html)

**Pros:**
- Cheap (~½ day implementation + tests).
- Unblocks qiyas#488 + #486 within hours.
- No SCHEMA bump.

**Cons:**
- Treats one symptom (asymmetric pairing); doesn't dissolve qiyas#490's other symptom (`_check_dominant_fold` mis-classifying 6-vs-8 as DIVISOR).
- Doesn't touch qiyas#400 F3.
- Adds a threshold (`HINT_GEOMETRIC_MISMATCH_PENALTY`) — Tenet 7 risk, to be tune-to-fit later.
- Sets a precedent for the next 3 "qiyas re-derives X" failure modes to each get their own threshold-bearing patch.

**Cost:** ½ day, ships within hours; technical-debt cost is the cumulative noise of the next 3 patches.

**Closes which questions from §4:** 5 (unblocks CI this week).
**Leaves open which questions:** 1, 2 (doesn't engage the structural problem), 3 (no SCHEMA change), 4 (no emit change).

**Tenet alignment:**
- Tenet 1 (simplicity): cheap *now*; expensive in cumulative threshold count later.
- Tenet 2 (root cause): does not address; treats symptom.
- Tenet 7 (don't tune to fit): violates — adds a tunable cost.
- Tenet 11 (don't add new flag for old problem): adds a new heuristic when an existing mechanism (tag-based hint) could be generalized.

### Option C — Qiyas-only universal hint inference (no bikar changes)

**Layman:** keep bikar as-is; have qiyas infer face_class and symmetry_fold from the existing tags + raster geometry alone. The detector becomes smarter; the producer stays the same.

**What changes:** qiyas adds a `Stage 1.6 — class inference` between `svg_primitives` and `shapes` that runs a classifier on the contour bag, using existing `authoritative_sides` as ground truth labels and propagating to untagged contours. No bikar changes; no SCHEMA bump.

**Presentation — concrete shape:**

```python
# qiyas Stage 1.6 (NEW), runs after svg_primitives:
def infer_face_class(contours: list[Contour]) -> list[Contour]:
    # Train a per-image classifier on contours with authoritative_sides
    # (the "labels"), then apply to contours without.
    labeled = [c for c in contours if c.authoritative_sides is not None]
    if not labeled: return contours  # no labels, no inference
    model = _fit_local_classifier(labeled)
    return [
        c.model_copy(update={"face_class": model.predict(c)}) if c.face_class is None else c
        for c in contours
    ]
```

**Web research:**
- Semi-supervised learning literature (Zhu 2005 survey) — propagating labels from labeled to unlabeled instances via geometric similarity; the canonical reference for "infer labels for unlabeled neighbors" — [Semi-Supervised Learning Literature Survey (Zhu, 2005)](https://pages.cs.wisc.edu/~jerryzhu/pub/ssl_survey.pdf)
- No prior art found for "infer at the consumer when the producer could simply emit." Every search returns either "extend the producer" or "use ML at the consumer because no producer exists" — the in-between case ("producer exists but we won't ask it for the label") is not a recognized pattern.

**Pros:**
- No cross-repo coordination required (bikar stays untouched).
- No SCHEMA bump.

**Cons:**
- Reinvents ML inference for a problem that has a deterministic source.
- Tenet 7 violation: every classifier has thresholds, every threshold drifts under iteration.
- Doesn't help the matcher case (symmetric class-mismatch needs the producer-provided label as ground truth; inferred labels can't disambiguate between two equally-likely guesses).
- Violates Tenet 23 by design (decline the producer's authority to keep the work on the consumer).
- Higher long-term cost than Option A: every new fact requires a new classifier instead of a new contract row.

**Cost:** 2-3 days for the inference stage + tuning + tests.

**Closes which questions from §4:** none cleanly.
**Leaves open which questions:** all of them.

**Tenet alignment:**
- Tenet 1 (simplicity): violates — adds a stage where none was needed.
- Tenet 2 (root cause): violates — declines to ask the layer that knows.
- Tenet 7 (don't tune to fit): violates — every classifier has tunable thresholds.
- Tenet 23 (the new tenet): violates by design.

### Option D — Ditch the bikar SVG-direct path entirely (always go through raster)

**Layman:** stop asking qiyas to read bikar SVG; rasterize bikar output and let qiyas's photo-cascade detector handle it. One pipeline (raster), not two (raster + SVG).

**What changes:** qiyas's `extract_primitives_svg` is deleted; the `svg_primitives` stage is replaced with a rasterize-then-vtrace stage. No bikar changes; no SCHEMA bump.

**Presentation — concrete shape:**

```python
# qiyas (Option D): one pipeline only.
def extract_primitives(svg_text: str) -> StageResult:
    png = rasterize_to_png(svg_text)
    contours = vtrace_to_contours(png)
    return StageResult(contours=contours)
    # No source_tag, no authoritative_sides, no face_class.
    # Geometric re-derivation is the only path.
```

**Web research:**
- 2026-05-17 sacred-patterns decision doc — `decisions/2026-05-17-eliminate-rasterize-trace-round-trip.md` — explicitly *rejected* the rasterize-trace path as the source of geometry: "render.svg is the geometry source, gt.json is the label oracle." This option would reverse that decision.
- No external prior art needed — the option is rejected by an existing accepted decision in this repo.

**Pros:**
- One pipeline.
- No contract surface to maintain.

**Cons:**
- Reverses the 2026-05-17 B1 decision (which had its own multi-option weighing).
- Loses every authoritative signal bikar already has — by design.
- Violates Tenet 23 by design.
- Re-introduces every problem 2026-05-17 was meant to dissolve.

**Cost:** ~3 days to delete + ~∞ days of re-introduced ambiguity.

**Closes which questions from §4:** none — by reverting a prior decision that closed several of these questions in the other direction.
**Leaves open which questions:** all of them, in a worse state.

**Tenet alignment:**
- Tenet 1 (simplicity): superficially simpler (one pipeline); not actually simpler (the rasterize-trace pipeline is lossy and the loss has to be paid by every consumer).
- Tenet 2 (root cause): violates — discards the layer that knows.
- Tenet 23 (the new tenet): violates by design.

## Recommendation

**Option A — Ship the universal tagging cascade.**

- Closes §4 question 1 (yes, prior art is dense) and §4 question 2 (yes, DETR pattern is canonical).
- Tenet 23 (the new tenet) is *defined* by this option; rejecting it would mean shipping the tenet without its anchoring instance.
- Tenet 2, 7, 11 alignment: addresses root cause, removes threshold accretion, generalizes the existing tag-based mechanism instead of adding a parallel one.
- Cost is real (~6 days) but slice-shippable: Slices 1–3 (~3 days) close qiyas#490 + a chunk of qiyas#400; Slices 4–5 are trigger-gated follow-ups.
- Bridge available: if §4 question 5 (CI deadline) forces immediacy, ship Option B in parallel as a 1-day bridge; delete it after Slice 3 lands.

## What would change this recommendation

- If the bikar `face.sources` data turns out to NOT cleanly carry `repeat:N` / `rotate:N` tags (Phase 1 emit assumption), Slice 1 cost rises and the cascade timeline extends; fall back to Option B as the long-term solution instead of the bridge.
- If the SCHEMA 1.14 → 1.15 bump breaks more than 2 byte-strict fixtures and the 2026-05-20 byte-strict Option D pattern doesn't generalize cleanly, defer Slice 2 and ship Option B for ~4–6 weeks while the byte-strict surface is refactored.
- If qiyas#488 + #486 owners need green CI today and Slice 1–3 of this cascade can't ship in <2 days, ship Option B as the bridge; cascade still proceeds.
- If a future failure mode reveals that bikar's DSL itself doesn't know a fact qiyas needs (e.g., a stylistic class that emerges from rendering, not authoring), revisit whether Option C's inference path becomes the right tool for that specific fact (per-fact decision; doesn't invalidate Option A for the facts the DSL does know).

## Final decision

**Decided:** 2026-05-20 by omar (auto-mode, per Tenet 19 bias for action)
**Picked:** Option A
**Rationale:** Tenet 23 names the principle; this option is the cascade that implements it. The cost (~6 days) is bounded; the alternatives all violate Tenet 23 by design. Bridge (Option B) is available if CI urgency forces it; cascade proceeds either way.
**Follow-ups (implementation):** tasks #491 (Slice 0), #492 (Slice 1), #493 (Slice 2), #494 (Slice 3), #495 (Slice 4 trigger-gated), #496 (Slice 5 CI gate). qiyas#490 marked SUPERSEDED with Option A retained as bridge if needed.
**Follow-ups (conditional / backlog — track triggers, not work):**
- **If §7 condition 3 (CI urgency) triggers:** ship qiyas#490 Option A as the bridge in parallel with Slice 1; delete it after Slice 3 lands.
- **If §7 condition 1 (face.sources doesn't carry repeat tags cleanly) triggers:** re-open this doc with the Slice 1 cost re-estimate; Option B becomes the long-term recommendation.

## Sources

- W3C SVG 2 specification — author-metadata pattern. https://www.w3.org/TR/SVG2/embedded.html
- Carion et al. 2020 — End-to-End Object Detection with Transformers. https://arxiv.org/abs/2005.12872
- Vega-Lite — declarative DSL emitting annotated SVG. https://vega.github.io/vega-lite/
- Sculley et al. 2015 — Hidden Technical Debt in Machine Learning Systems. https://papers.nips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html
- Zhu 2005 — Semi-Supervised Learning Literature Survey. https://pages.cs.wisc.edu/~jerryzhu/pub/ssl_survey.pdf
- sacred-patterns/docs/decisions/2026-05-17-eliminate-rasterize-trace-round-trip.md — B1 parent decision establishing "render.svg is geometry source."
- qiyas/docs/decisions/2026-05-20-qiyas-anti-symmetry-floor-breach.md — symptom decision doc, superseded by this cascade.
- sacred-patterns/docs/dsl-metadata-contract.md — companion contract spec (v1, ACCEPTED 2026-05-20).
- bikar/.claude/plans/is-there-an-actionalble-logical-cascade.md — implementation plan (6 slices).
