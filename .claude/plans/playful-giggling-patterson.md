# bikar ↔ qiyas: make the deconstruction separation explicit, and extract the shared contract

## Context

We do "deconstruction" (turning a pattern into its constituent shapes) in **two**
places, and the boundary between them has never been written down. That ambiguity
is the problem the owner wants solved:

- **qiyas must stay self-service** — someone can visualize/review a deconstruction
  *without* standing up the whole bikar studio. qiyas's job is **machine CV
  deconstruction + Claude-Code-skill-driven work + a review portal**.
- **bikar is the self-service *human* deconstruction surface** — where an author
  picks shape types, flags faces by eye, and drops point-observations.
- The two are **compatible, never merged** — they exchange JSON artifacts.

The intended outcome: (1) a documented, diagrammed **"which tool when"** division of
labor so the separation is intentional, and (2) if there's a reusable core hiding in
qiyas, **extract it as a shared contract** bikar can type-check against — without
forcing the Python CV algorithm across the Python/JS boundary.

**Key facts established by exploration (ground truth, read from code):**
- qiyas is **already fully standalone** — zero runtime bikar imports; `qiyas review
  --image --ref` on :8731; its FastAPI app already serves `/encoding`, `/diff`,
  `/annotations`. "Self-service" already holds; we are *documenting* it, not building it.
- bikar's `packages/web/src/sessions.ts` is the **manual, by-eye** deconstruction
  view: `FaceAnnotation{status: approved|flagged, issueType, comment}` +
  `PointSet{type: missing|expected-star|expected-rosette|note}` → `feedback.json`.
- qiyas `Encoding` (schema.py, `SCHEMA_VERSION="1.21"`) and bikar `GroundTruthEncoding`
  (gt-emitter.ts, `GT_SCHEMA_VERSION="1.23"`) are **sibling version-lines of ONE
  artifact family** — same shape vocabulary, same `evidence.{face_class, shape_id,
  authored_region, outline_arcs}` fields — differing only by producer (gt's
  `confidence` is always 1.0 = authored truth; Encoding's is detector confidence).
- The seam today is **file-based and write-only**: bikar emits `pattern.gt.json`,
  qiyas reads it for calibration. The `dsl-metadata-contract.md` gate covers the SVG
  `data-*` channel per-attribute, but **nothing type-checks the JSON envelopes**.

## The separation (Deliverable A)

One-sentence rule for the top of the doc:
> **Reach for bikar when you are the *author* asserting what the pattern *is*.
> Reach for qiyas when you are the *reviewer* judging what the machine *saw*.**

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

**bikar's two deconstruction skills are one journey, two stages — and need an honest
rename to say so.** Today `deconstruct` and `pattern-decomposition` have colliding
"invoke when…" triggers (both: "recreate this pattern"), a Tenet-11 smell. In fact
`deconstruct` is the **bootstrap on-ramp** (`make deconstruct` → session dir + first
render + Studio URL; the only place the concrete `compileDSL`/`pixel-diff` commands
live) and `pattern-decomposition` is the **deep iterative engine** (the wave-by-wave
Stage-1, the G8 structure→color→weave ladder, the ghost technique — the flow the
medallion-10 campaign actually runs). The fix (Phase 0):
- rename `bikar/.claude/skills/pattern-decomposition/` → **`iteratively-deconstruct-pattern`**
  (names the wave/stage-ladder engine; update the ~6 referrers: `bikar/CLAUDE.md`,
  `docs/roadmap.md`, three `.claude/plans/*`, `compact-prompt`,
  `iterate-pattern-from-qiyas-warnings`).
- rename `bikar/.claude/skills/deconstruct/` → **`start-deconstruction`** (the on-ramp;
  the `make deconstruct` target stays — it's how every session starts).
- make the handoff explicit in both "When to Invoke" sections: `start-deconstruction`
  ends by handing off to `iteratively-deconstruct-pattern`; the latter names the former
  as its prerequisite. They stop competing on the trigger.

**The wave cockpit (`sacred-patterns/tools/wave-plan-server.py`, :8765) is the
interactive UI for `iteratively-deconstruct-pattern`'s wave/ghost flow** — not a
separate fourth tool. The separation doc names it as bikar-lane deep-decon cockpit; an
open question (out of scope here, noted for follow-on) is whether its wave/ghost pages
should fold into the bikar studio `/sessions` so the deep lane has one home.

Three journey diagrams (authored as Mermaid `.mmd`): (1) bikar self-service decon
journey, (2) qiyas skill+portal review journey, (3) the shared-artifact seam
(`gt.json` one way as DSL truth; `encoding.json` optionally back as the machine read;
`annotations.json` as reviewer judgement).

**Lives at** `sacred-patterns/docs/bikar-qiyas-separation.md` (cross-repo home,
sibling to `dsl-metadata-contract.md`), diagrams under `docs/diagrams/`, one-line
mirror stubs in `bikar/docs/` and `qiyas/docs/`, one new row in
`cross-repo-dependencies.md`.

## The extractable library (Deliverable B)

**Recommendation: extract the artifact *contract* (schemas only — no algorithm
crosses the boundary). Reject WASM. The HTTP service is an optional later phase.**

| Option | Verdict |
|---|---|
| **1. Shared artifact contract** — Pydantic envelopes + generated JSON Schema + published TS mirror `@naqshcoffee/qiyas-schema`; both sides type-check ONE family contract | **RECOMMEND (Phase 1–3)** |
| **2. HTTP `POST /deconstruct`** on the existing review FastAPI app → `encoding.json`; lets bikar `/sessions` optionally show the machine's read beside the human's | **OPTIONAL (Phase 4)** — depends on 1; clearly deferrable |
| **3. WASM-compile the pipeline** | **REJECT** — `cairosvg`/`opencv` don't WASM cleanly; violates Tenets 1 & 25 |
| **4. Do nothing / file-based seam** | **Not correct here** — qiyas already reads the gt envelope; un-typed envelope breaks silently on any field rename |

**SCHEMA_VERSION coordination (the crux):** `GT_SCHEMA_VERSION` (bikar, producer) and
`SCHEMA_VERSION` (qiyas, consumer) are **two version-lines of one family**, bumping
independently because their producers evolve independently. The shared package
(`@naqshcoffee/qiyas-schema` semver) versions the **family contract**; each side
declares which family version it satisfies. A new shared `evidence.*` channel = one
family bump consumed by both. Per Tenet 24, a family-contract change is **break +
regen** (regenerate JSON Schema + TS mirror, bump both sides, re-run the round-trip
gate) — no compat window for the internal envelope. This lifts
`dsl-metadata-contract.md` from per-`data-*`-attribute to per-envelope.

## Phased implementation (each phase ships standalone — Tenets 1, 12)

- **Phase 0 — separation doc + bikar skill rename (Deliverable A).** (a) Write
  `bikar-qiyas-separation.md` + three `.mmd` diagrams + mirror stubs + cross-repo row —
  ships the "which tool when" decision immediately. (b) Rename bikar's two decon skills
  (`pattern-decomposition` → `iteratively-deconstruct-pattern`, `deconstruct` →
  `start-deconstruction`), update the ~6 referrers, and make the on-ramp→engine handoff
  explicit in both "When to Invoke" sections. Docs/skills only; no engine code.
- **Phase 1 — `qiyas/src/qiyas/contract/` package.** Move the envelope Pydantic models
  (`Encoding`/`Diff` + leaf `Symmetry`/`Statistics`/`Evidence`/`Contour` from
  `schema.py`; `AnnotationsFile`/`Annotation` from `review/state.py`; `ReviewVerdict`
  from `review/verdict.py`) behind a contract layer the rest of qiyas imports from;
  export `model_json_schema()` → `contract/schemas/*.json`; wire the existing
  import-linter layer. Internal to qiyas; ships standalone.
- **Phase 2 — publish `@naqshcoffee/qiyas-schema`.** Codegen TS types from the JSON
  Schema; publish to GitHub Packages mirroring bikar-core's release script. Ships a
  package nobody must consume yet.
- **Phase 3 — bikar consumes the contract.** Assert (compile-time) that
  `GroundTruthEncoding` structurally conforms to the shared `EncodingLike` envelope;
  extend `qiyas validate-dsl-contract --strict` to assert envelope-level round-trip.
  Compile-time only; ships standalone.
- **Phase 4 (optional) — HTTP deconstruct endpoint.** Add `POST /deconstruct` to the
  existing review app → contract-typed `encoding.json`; bikar `/sessions` gains an
  optional Tenet-29-simple "show the machine's read" toggle. Defers cleanly.

## Files to create / modify

**Create (A):** `sacred-patterns/docs/bikar-qiyas-separation.md`;
`sacred-patterns/docs/diagrams/{bikar-decon-journey,qiyas-review-journey,shared-artifact-seam}.mmd`;
mirror stubs `bikar/docs/bikar-qiyas-separation.md`, `qiyas/docs/bikar-qiyas-separation.md`.
**Rename + modify (A — bikar skills):** `bikar/.claude/skills/pattern-decomposition/`
→ `iteratively-deconstruct-pattern/`; `bikar/.claude/skills/deconstruct/` →
`start-deconstruction/`; update referrers `bikar/CLAUDE.md`, `bikar/docs/roadmap.md`,
`bikar/.claude/plans/{vectorized-squishing-pearl,park-medallion-weave-handoff,weave-only-compare}.md`,
`bikar/.claude/skills/{compact-prompt,iterate-pattern-from-qiyas-warnings}/SKILL.md`;
edit both renamed skills' "When to Invoke" to name the handoff.
**Modify (A):** `sacred-patterns/docs/cross-repo-dependencies.md` (one §Reference row).

**Create/modify (B):** new `qiyas/src/qiyas/contract/` (envelope models + `schemas/*.json`);
modify `qiyas/src/qiyas/schema.py`, `qiyas/src/qiyas/review/state.py`,
`qiyas/src/qiyas/review/verdict.py` (import from contract); new
`bikar/packages/contract/` publishing `@naqshcoffee/qiyas-schema`; modify
`bikar/packages/core/src/render/gt-emitter.ts` (conform to shared envelope); modify
`sacred-patterns/docs/dsl-metadata-contract.md` (add envelope-level section).

## Verification (no CI churn — Tenet 25)

1. **Docs:** render the three `.mmd` diagrams; check the "which tool when" rule against
   the persona table for Tenet-11 (exactly one tool path per question).
2. **Phase 1/2:** load each generated JSON Schema and validate real fixtures
   (`encoding.json`, `annotations.json`, a captured `pattern.gt.json`) against it;
   assert TS codegen compiles.
3. **Phase 3:** extend the **existing** `qiyas validate-dsl-contract --strict` gate to
   round-trip a bikar fixture through qiyas at the *envelope* level — reuses the gate,
   no new GHA job.
4. **Phase 4:** `qiyas review` up; `POST /deconstruct` a fixture; assert the response
   validates against the shared schema and renders in the bikar machine-read panel;
   Tenet-29 5-second check on the toggle.

## Tenets in play

#1 smallest chunk · #11 one tool path per question · #23 DSL-as-source-of-truth
(the gt→encoding channel becomes type-enforced) · #24 no backcompat shims (break +
regen the envelope) · #25 GHA budget (reuse the existing gate) · #29 grandma-bar for
the optional machine-read toggle.

## Scope notes

- **Not** "collapse three servers into one." qiyas stays independent on :8731; bikar
  stays on :5173; wave-plan-server (:8765) is the medallion build cockpit and is out
  of scope here.
- The medallion-10 iter-70 refit (#23) and the training-pipeline task (#22) are
  separate threads, unaffected by this plan.
