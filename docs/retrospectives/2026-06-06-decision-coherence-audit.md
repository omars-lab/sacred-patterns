---
title: "Decision-coherence audit — all 61 decision docs, deep-read for contradictions / stale-status / duplicates"
date: 2026-06-06
repos: [qiyas, bikar, sacred-patterns]
derived_from: docs/retrospectives/2026-06-06-image-to-dsl-retrospective.md
scope: 61 decision docs (qiyas 40, bikar 18, sacred-patterns 3) — bodies read, not just frontmatter status
method: 10 topic-cluster deep-reads (coherence-across-cluster) + 3 per-repo status sweeps (frontmatter↔body + unmarked reversals)
status: REPORT — no edits applied; feeds Phase 3 plan
---

> **What the retrospective skipped.** The retro §4 (M2) status-*indexed* the 61
> docs and found "≥1" frontmatter/body mismatch. This audit *read the bodies* and
> found the problem is systemic, not a one-off: **6 genuine ACCEPTED-but-body-says-PENDING
> mismatches, 5 unmarked reversals, and only 3 of 61 docs carry a SUPERSEDED/REOPENED
> marker** despite at least 8 real reversals having occurred. The headline: the
> decision corpus is mostly coherent *within* a problem-tag's happy path, but the
> **status layer is unreliable** — you cannot trust a doc's frontmatter to tell you
> whether its decision is live, reversed, or still open.

# 0. Executive summary

**The good news:** of 10 topic clusters, **3 are cleanly coherent** (petal/ring,
scope/rescope, bikar-misc) — their SUPERSEDED docs are correctly marked, their
layering holds, and falsifications are recorded honestly in-body. The
methodology these clusters demonstrate (each doc authoritative for its own
sub-domain, falsifications logged in §9 with owner direction) is the target
state for the rest.

**The bad news, in priority order:**

1. **Status decay is the dominant failure.** 6 docs say `ACCEPTED` in frontmatter
   while their body's §8 says `PENDING — owner review required`. A cold reader
   trusting frontmatter would build on a decision the author themselves marked
   un-made. This is retro M2, and it is **6×, not 1×.**
2. **Reversals don't get marked.** At least 8 reversals occurred; only 3 docs
   carry SUPERSEDED/REOPENED. The 5 unmarked reversals leave earlier docs
   asserting `ACCEPTED` on premises a later doc silently falsified.
3. **One label-conflation contradiction is load-bearing and live.** The
   `2026-05-17` parent says "Option A"; its `2026-05-18` child picks "Option B"
   using *Option A's label* for *Option B's mechanism*. The two cannot both be
   true, and neither is marked superseded. (This is the SVG-direct spine of I1 —
   the contradiction is in the most load-bearing cluster.)
4. **No "one authoritative doc per tag" pointer exists.** Three READMEs list docs
   chronologically with prose status that *itself* drifts from frontmatter (the
   qiyas README lists `coverage-gate-scope` with **two** statuses on one line).

**A measurement caveat that matters for Phase 3.** The cluster agents flagged
every "PROPOSED frontmatter + a recommendation in the body" as a
frontmatter-body-mismatch. **It is not** — the `present-options` skill *defines*
PROPOSED as "has a recommendation, awaiting owner pick." Those ~5 cases
(`ci-arch-divergence`, `bikar-validate-dsl-contract`, `362-d4-cutover`,
`i1-ratchet`, `qiyas-anti-symmetry-floor`) are **correctly stated** and are
excluded from the "genuine mismatch" count below. The genuine mismatches are
only the **ACCEPTED-frontmatter / PENDING-body** cases — where the author marked
it done but the body says it isn't. This distinction is exactly the kind of
thing a hygiene checker must encode precisely (see Phase 3): the rule is *not*
"PROPOSED docs must have no recommendation," it's "ACCEPTED docs must have a
picked option in §8."

# 1. Cluster verdict table

| # | Topic cluster | Docs | Verdict | Authoritative doc (live) |
|---|---------------|------|---------|--------------------------|
| C1 | face-class / region-identity | 7 | **contradictory** | `qiyas/2026-05-29-f2-face-class-is-wrong-retrieval-label.md` (Option E, ACCEPTED 2026-06-01: gate on `geom_label`, *not* face_class identity) |
| C2 | petal-N / ring / rotate-block | 6 | coherent | `bikar/2026-05-15-bikar-petal-n-ring-class-assignment.md` (+ co-auth `qiyas/2026-05-07-petal-6-full-empty-provenance-collapse.md`) |
| C3 | scope / gate-scope / rescope | 6 | coherent | none single — each doc owns its own scope domain (methodology, not a tree) |
| C4 | shape-vocab / typed-params / discriminated-union | 3 | **mixed** | `qiyas/2026-05-18-shape-discriminated-union-migration-sequencing.md` (status unresolvable — see C4) |
| C5 | star7 red-shape detection | 2 | **contradictory** | none — both effectively PENDING; `2026-05-21` is de-facto guide via shipped commits |
| C6 | arc / lens / partial-shape (cross-repo) | 6 | **contradictory** | `bikar/2026-05-05-arc-lens-face-emission.md` + `2026-05-10` pair (live); SP `2026-05-07` is falsified/reopened |
| C7 | DSL-as-truth / SVG-direct / rasterize-trace | 7 | **contradictory** | `sacred-patterns/2026-05-20-universal-dsl-tagging.md` (clean) — but its substrate (`2026-05-17`/`2026-05-18`) is status-broken |
| C8 | closeout / dashboard / corpus-macro reporting | 6 | **contradictory** | `qiyas/2026-05-11-i1-next-corpus-and-macro-lift.md` |
| C9 | CI / coverage / telemetry / fixtures / contract | 9 | **contradictory** | `qiyas/2026-05-20-byte-strict-fixture-comparator-decay.md` (Option D, owner override) + `2026-05-19-qiyas-ci-silent` |
| C10 | bikar misc (clip/fill-void/merge/line/girih/…) | 9 | coherent | `bikar/2026-05-28-medallion10-girih-ceiling.md` (composite authority) |

# 2. Genuine ACCEPTED-frontmatter / PENDING-body mismatches (retro M2 — the real ones)

These are the load-bearing M2 cases: a cold reader trusting the frontmatter
would treat the decision as made when the author's own body marks it open.

| Doc | Frontmatter | Body §8 actually says | Why it matters |
|-----|-------------|----------------------|----------------|
| `qiyas/2026-05-29-f2-face-class-is-wrong-retrieval-label.md` | `ACCEPTED 2026-06-01 — Option E` | §Final decision picks **Option C**; §Falsification log then kills C; inline callout says owner re-decided to E | Frontmatter collapses a C→falsify→escalate→E journey into one state; the *picked-and-shipped-then-falsified* C is invisible to a status-only reader |
| `qiyas/2026-05-17-eliminate-rasterize-trace-round-trip.md` | `ACCEPTED 2026-05-18 — Option A (refined…)` | §8: `PENDING — owner review required` + "ships PROPOSED" | **Plus label conflation** (see §3 C7): frontmatter says "Option A" but the refined wording it cites is *Option B's* mechanism |
| `qiyas/2026-05-18-b1-mechanism-refinement-gt-vs-render-svg.md` | `ACCEPTED 2026-05-18` | §8: `PENDING — owner pick required` (3 paths open) | Child of the above; unblocks #398 — building on it assumes a pick that wasn't made |
| `qiyas/2026-05-18-star7-red-shape-detection-routing.md` | `ACCEPTED 2026-05-18` | §Final decision: `PENDING — owner review required` (conditioned on Q1/Q4) | `2026-05-21` builds a mechanism layer treating Option A as shipped (see C5) |
| `qiyas/2026-05-18-shape-discriminated-union-migration-sequencing.md` | `ACCEPTED 2026-05-18` (attributed to owner, Option B) | §8: `PENDING — owner review required`, re-presents all options | Makes it impossible to tell if Phase 1 is gated on #410 or unblocked |
| `bikar/2026-05-17-arc-region-class-precision.md` | `ACCEPTED 2026-05-18 AND REOPENED 2026-05-18` (both) | Body picks Option E+G but addendum says necessary-but-not-sufficient; source-tag fix open as #414 | Frontmatter carries two contradictory statuses simultaneously |

> Note `bikar/2026-05-19-face-extractor-origin-coincidence-fix.md` uses a
> non-standard status token `RESOLVED-FREEZE-ACCEPT` (the ground-truth indexer
> parsed it as `UNKNOWN`). Its body is internally consistent (8 options
> falsified, owner-endorsed Option E) — the issue is a vocabulary gap, not a
> mismatch. Phase 3's status enum must either bless or rename this token.
> Similarly `qiyas/2026-05-18-region-identity-class-emission-4-layer-fix.md` has
> a body that reads RESOLVED while its header reads PENDING — a genuine stale
> status.

# 3. Unmarked reversals (later doc overturns earlier; earlier not marked)

Only **3 of 61** docs carry a SUPERSEDED/REOPENED marker
(`qiyas/2026-05-07-petal-6-full-asymmetric-granularity` SUPERSEDED,
`bikar/2026-05-06-rotate-block-prev-next-index` SUPERSEDED,
`sacred-patterns/2026-05-07-partial-shape-rendering` REOPENED). Below are the
reversals that happened **without** the earlier doc being marked:

| Earlier doc (left ACCEPTED) | Later doc that reversed it | The reversal |
|-----------------------------|----------------------------|--------------|
| `bikar/2026-05-06-face-class-style-resolver-wiring.md` (Option F: "face_class is the **sole** class-selector path") | `bikar/2026-05-18-region-identity-class-emission` + `qiyas/2026-05-29-f2` | The "sole path" premise is falsified twice: `assignSourceTagClasses` runs in parallel (05-18), and face_class is proven a fill/role label not shape-identity (05-29). 05-06 stays ACCEPTED. |
| `qiyas/2026-05-19-ci-arch-divergence-encoder-baselines.md` (Option A: re-baseline to x86_64, keep byte-strict) | `qiyas/2026-05-20-byte-strict-fixture-comparator-decay.md` (Option D, owner override) | Owner directive "I don't need byte-level verification" directly rejects 05-19's recommendation. 05-19 stays PROPOSED, unmarked. |
| `qiyas/2026-05-18-star7-red-shape-detection-routing.md` | `qiyas/2026-05-21-star7-missed-red-shapes-mechanism.md` | 05-21 cites 05-18 as "picked Option A / the slice that shipped" — but 05-18's body says PENDING. The dependency is on a decision that was never finalized. |
| `qiyas/2026-05-17-eliminate-rasterize-trace-round-trip.md` (apparent Option A) | `qiyas/2026-05-18-b1-mechanism-refinement.md` (Option B) | 05-18 picks Option B's mechanism without marking 05-17 REOPENED; the label conflation (05-17 frontmatter calls Option B's mechanism "Option A") hides it. |
| `qiyas/2026-05-12-i1-closeout-report-surface.md` (defer the CLI / Option C) | `qiyas/2026-05-12-i1-closeout-report-feedback-surface.md` (assumes the CLI exists) | Same-day forward-dependency cycle: feedback-surface builds a server *into* the CLI that report-surface explicitly deferred. Neither cross-references the conflict. |

Plus the **assumption-shift** (softer than a reversal but worth noting): SP
`2026-05-07-partial-shape-rendering` was ACCEPTED 2026-05-07, then *falsified
2026-05-25* (composite **regressed** −0.13 vs the doc's predicted +0.05…+0.10).
`bikar/2026-05-10` and `qiyas/2026-05-11` were authored assuming that cascade
would land; when it was falsified 18 days later, no retroactive note was added
to the downstream docs. (The 05-07 doc *is* marked REOPENED — credit — but its
`decided:` frontmatter still reads `2026-05-07` and its follow-ups aren't marked
conditional.)

# 4. The one live contradiction to fix first (C7 — load-bearing)

The SVG-direct cluster is the spine of I1 (ARI=1.0). Inside it:

- `2026-05-17` frontmatter: `Option A (refined wording — render.svg direct,
  gt.json as label oracle)`.
- `2026-05-18` §6 explicitly recommends `Option B — render.svg as geometry
  source; gt.json as label oracle`.
- **"render.svg direct, gt.json as label oracle" is Option B's mechanism.** The
  05-17 frontmatter is wearing Option A's label over Option B's body. The B1
  fidelity audit it cites (`B1-gt-fidelity-audit-2026-05-17.md`, GREENLIGHT)
  *supports Option B*, confirming the label is wrong.

Net: the cluster's *behavior* is coherent (everyone implemented render.svg-as-
geometry-source, which is what shipped), but the *record* is contradictory — two
docs claim incompatible option letters for the same mechanism, neither marked
superseded. A future agent auditing "why did we pick render.svg" gets two
conflicting answers. **Reconcile:** correct 05-17's frontmatter to name Option B,
mark it REOPENED-then-resolved (mechanism sub-question, parent decision still
valid), and have 05-18 cite it as the resolving child.

# 5. Coherent clusters (the target state — keep doing this)

- **C2 petal/ring:** both SUPERSEDED docs carry explicit falsification closeouts
  naming *why* the premise died (rotate-block = capability already existed;
  petal-6-full = stale schema-1.13 fixture). Parent/child cross-refs present.
- **C3 scope:** each doc owns one scope domain; the 2026-05-22 falsification is
  logged in-body §9 with owner direction to Option G. No cross-doc conflict.
- **C10 bikar-misc:** PENDING docs (fill-void, line-primitive, mirror-rotate)
  are honestly PENDING; the girih-ceiling doc is complementary, not disruptive.

These three are the proof that the hygiene the rest needs is *achievable with the
existing skills* — the failure is enforcement, not authoring capability.

# 6. What to reconcile (ordered for Phase 3)

1. **C7 label-conflation** (load-bearing, live): fix 05-17 frontmatter to Option
   B + REOPENED-resolved; 05-18 cites it. *Highest value — it's the I1 spine.*
2. **6 ACCEPTED/PENDING mismatches** (§2): bring frontmatter into line with body.
   For the F2 doc, the journey (C→E) should be visible, not collapsed.
3. **5 unmarked reversals** (§3): mark each earlier doc SUPERSEDED/REOPENED with a
   one-line pointer to the doc that reversed it.
4. **C1 face-class chain**: mark `bikar/2026-05-06` SUPERSEDED-PARTIALLY (sole-path
   falsified), `bikar/2026-05-18` REOPENED-PENDING (task #414 is the re-opener),
   bless `qiyas/2026-05-29` Option E as authoritative for face_class semantics.
5. **Status-token vocabulary**: bless or rename `RESOLVED-FREEZE-ACCEPT`; define a
   `PROPOSED` (has recommendation) vs `PENDING` (no pick) vs `ACCEPTED` (pick in
   §8) state machine so the checker can be precise.
6. **README drift**: the three `docs/decisions/README.md` carry prose statuses
   that drift from frontmatter (qiyas's `coverage-gate-scope` line shows two
   statuses). Generate the README from frontmatter instead of hand-maintaining.

# 7. Answer to the audit's three questions

- **Do any ACCEPTED docs contradict each other?** Yes — C7 (label conflation,
  live, load-bearing) is the clearest; C1 (face-class sole-path) and C9
  (re-baseline vs meaning-level) are reversals dressed as coexisting ACCEPTEDs.
- **Are the multiple ACCEPTED docs coherently layered or contradictory?** Mixed:
  3/10 clusters coherent, 6/10 contradictory, 1/10 mixed. The contradictions are
  concentrated in **status**, not in **behavior** — the code mostly does the
  right (latest) thing; the *docs* mislead about which decision is live.
- **Is the supersede-marker count suspiciously low?** Yes — **3 of 61** (4.9%)
  against ≥8 actual reversals. Supersede-on-reversal is not happening. This is
  the single most actionable hygiene gap and the core of the Phase 3 mechanism.

---

## Appendix — method & confidence

- 10 cluster agents (Explore type) each read every full body in their cluster and
  judged coherence across it; 3 sweep agents independently re-checked every doc
  per repo for frontmatter↔body and unmarked reversals. Cross-checking the two
  passes is how the "PROPOSED-with-recommendation is benign" correction surfaced
  (the sweep over-flagged it; the cluster context disambiguated).
- **Confidence:** findings citing a specific line/section + a quoted phrase are
  high-confidence (most of §2–§4). The "assumption-shift" in §3 is lower-confidence
  (it's an inference about implicit dependency, not a direct contradiction) and is
  labeled as such.
- **Coverage:** all 61 decisions (40/18/3) read in body. The 3 READMEs were read
  for the status-drift finding (§6.6) but are not decision docs.
