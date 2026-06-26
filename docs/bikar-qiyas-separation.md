# bikar ↔ qiyas: the deconstruction separation

**Version:** 1.0
**Status:** ACCEPTED (2026-06-26)
**Owner:** sacred-patterns (canonical) · mirror stubs in `bikar/docs/` and `qiyas/docs/`
**Tenets:** #11 (one tool path per question) · #23 (DSL-as-source-of-truth) · #29 (grandma-bar UI)

## What this doc is

We do **deconstruction** — turning a pattern into its constituent shapes — in two
places. This doc names which tool to reach for, why they stay separate (never
merged), and the JSON artifacts they exchange. It is the companion to
[`dsl-metadata-contract.md`](dsl-metadata-contract.md): that one governs the
per-`data-*`-attribute SVG channel; this one governs the *workflow* split and the
*envelope-level* artifact seam.

## The one-sentence rule

> **Reach for bikar when you are the *author* asserting what the pattern *is*.
> Reach for qiyas when you are the *reviewer* judging what the machine *saw*.**

bikar is the human, by-eye, producer-of-record surface. qiyas is the machine-CV +
skill-driven + review-portal surface. They are **compatible (they exchange JSON
artifacts), never merged.**

## Which tool when

| Axis | **bikar lane** | **qiyas lane** |
|---|---|---|
| Persona | Pattern author (DSL-literate maker) | Tenet-29 art-savvy SME (non-technical, trained eye) |
| Question | "I'm building this — what is each face?" | "The machine read an image — is its read right?" |
| Mode | By-eye, author-driven; choose shape types, flag faces | Machine CV (`encode_image`) + skills + structured replay |
| Entry | bikar studio `/sessions` (:5173) | `qiyas review --image --ref` (:8731) |
| Input | `.bkr` under construction | Any raster / SVG / photo (no producer needed) |
| Output | `feedback.json` + authoritative `pattern.gt.json` | `annotations.json` (v3, Q1–Q12) + `ReviewVerdict` (v1) |
| Truth role | **Producer of record** (Tenet 23) | Detector-of-record only for producerless inputs |
| Guiding skill(s) | `start-deconstruction` (on-ramp) → `iteratively-deconstruct-pattern` (wave/stage-ladder engine) | `review-portal` (Q1–Q8 SOP), `review-smoke`/`review-validate`; `iterate-detector-calibration` for the detector |

**qiyas is self-service today.** It has zero runtime bikar imports; `qiyas review
--image --ref` stands up the portal on :8731 and its FastAPI app already serves
`/encoding`, `/diff`, `/annotations`. You can visualize and review a deconstruction
*without* standing up the bikar studio. This doc *documents* that property — it does
not build it.

**bikar is the by-eye human surface.** `packages/web/src/sessions.ts` is the manual
deconstruction view: `FaceAnnotation{status: approved|flagged, issueType, comment}`
plus `PointSet{type: missing|expected-star|expected-rosette|note}` → `feedback.json`.
The author picks shape types, flags faces, and drops point-observations.

## bikar's two skills are one journey, two stages

bikar guides deconstruction with **two** skills that are a single on-ramp→engine
journey, not competing entry points:

- **`start-deconstruction`** — the **bootstrap on-ramp.** `make deconstruct IMG=… NAME=…`
  scaffolds the session dir, drops the reference image, writes `session.json`, renders
  the first `.bkr`, and opens the Studio. The only place the concrete
  `compileDSL`/`pixel-diff` commands live. It ends by handing off to the engine.
- **`iteratively-deconstruct-pattern`** — the **deep iterative engine.** The
  wave-by-wave Stage-1 decomposition, the G8 structure→color→weave stage ladder, and
  the ghost technique (per-wave 3-view picker). This is the flow the medallion-10
  campaign actually runs. It names `start-deconstruction` as its prerequisite.

They stop competing on the "recreate this pattern" trigger: you *start* with the
on-ramp, then *iterate* with the engine.

**The wave cockpit** (`sacred-patterns/tools/wave-plan-server.py`, :8765) is the
interactive UI for `iteratively-deconstruct-pattern`'s wave/ghost flow — **not a
separate fourth tool.** It is the bikar-lane deep-decon cockpit. (Open follow-on, out
of scope here: whether its wave/ghost pages should fold into the bikar studio
`/sessions` so the deep lane has one home.)

## The shared-artifact seam

Three artifacts cross the boundary; each has one direction and one meaning:

- **`pattern.gt.json`** (bikar → qiyas) — the DSL ground truth. bikar emits it from
  `emitGroundTruth()` (`GT_SCHEMA_VERSION="1.23"`, `confidence` always 1.0 = authored
  truth). qiyas reads it for calibration.
- **`encoding.json`** (qiyas → optionally back) — the machine's read. qiyas's
  `encode_image()` emits it (`SCHEMA_VERSION="1.21"`, `confidence` = detector
  confidence). Optionally surfaced beside the human's read.
- **`annotations.json`** (qiyas, reviewer-authored) — the reviewer's judgement
  (v3, Q1–Q12 discriminated union; `ReviewVerdict` v1).

`Encoding` (qiyas) and `GroundTruthEncoding` (bikar) are **sibling version-lines of
ONE artifact family** — same shape vocabulary, same `evidence.{face_class, shape_id,
authored_region, outline_arcs}` fields — differing only by producer. This is why a
shared *contract* (Deliverable B, phases 1–3) is extractable: the envelope is one
family, even though no algorithm crosses the Python/JS boundary.

Diagrams: [`diagrams/bikar-decon-journey.mmd`](diagrams/bikar-decon-journey.mmd),
[`diagrams/qiyas-review-journey.mmd`](diagrams/qiyas-review-journey.mmd),
[`diagrams/shared-artifact-seam.mmd`](diagrams/shared-artifact-seam.mmd).

## What this doc is NOT

- **Not** "collapse the servers into one." qiyas stays independent on :8731; bikar
  stays on :5173; wave-plan-server (:8765) is the bikar-lane deep-decon cockpit.
- **Not** a merge. The two surfaces stay separate by design — they exchange JSON, they
  do not share a process or a runtime.

## Roadmap (the shared contract — Deliverable B)

The extractable library is the **artifact contract** (schemas only — no algorithm
crosses the boundary). Phased:

- **Phase 1** — `qiyas/src/qiyas/contract/` package: envelope Pydantic models +
  generated JSON Schema.
- **Phase 2** — publish `@naqshcoffee/qiyas-schema` (TS mirror of the JSON Schema).
- **Phase 3** — bikar's `GroundTruthEncoding` conforms to the shared envelope;
  `qiyas validate-dsl-contract --strict` extends to envelope-level round-trip.
- **Phase 4 (optional)** — `POST /deconstruct` on the review app → contract-typed
  `encoding.json`; bikar `/sessions` gains an optional "show the machine's read" toggle.

Per Tenet 24, a family-contract change is **break + regen** (regenerate JSON Schema +
TS mirror, bump both sides, re-run the round-trip gate) — no compat window for the
internal envelope.
