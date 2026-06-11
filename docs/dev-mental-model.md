# sacred-patterns developer mental model

This doc captures the load-bearing principles that shape how sacred-patterns
works — the "why" behind decisions that aren't obvious from reading the code.
It's the first thing a new agent (human or otherwise) should read after
CLAUDE.md.

The structure is *index-of-principles*, not *retrospective-of-decisions*. Each
entry distills one rule and links to the full decision doc for the audit
trail. The principle is what generalizes; the decision doc is what records
the alternatives weighed at the time.

Maintenance contract: when a decision in `docs/decisions/` flips to
`ACCEPTED`, append a one-paragraph principle entry here per the
[decision-doc skill's Post-ACCEPT step](../../sacred-patterns/.claude/skills/decision-doc/SKILL.md).
The hook at `.claude/hooks/mental-model-decision-watch.sh` (when wired up)
will nudge if a fresh ACCEPTED doc has no entry. If a previously-ACCEPTED
decision is **superseded**, mark the entry `(SUPERSEDED by [...])` rather
than deleting it — the audit trail includes the superseded principle for
future readers wondering why something *isn't* the case anymore.

## How the three-repo iteration loop works

sacred-patterns is the **orchestrator** in a three-repo cascade with
bikar (the producer of geometry) and qiyas (the consumer / detector).
A new contributor needs the operational model:

```
sacred-patterns (this repo) — orchestrates everything
  ├── invokes bikar to render a .bkr → .svg + gt.json
  ├── invokes qiyas to encode the SVG → encoding.json
  ├── invokes qiyas diff to compare against a baseline / reference image
  ├── parses qiyas's verdict (GO / ITERATE / STOP)
  └── either accepts the iteration, asks for another, or stops the loop

bikar (producer)  — DSL → SVG with data-* attrs per the metadata contract.
                    Reusable beyond this loop; sacred-patterns does NOT
                    depend on its internals.

qiyas (consumer)  — SVG → encoding.json + diff verdict.
                    Reads data-* via SVG fast-path; reusable beyond
                    bikar (works on hand-authored SVGs and photos too).
```

**Entry points:**
- `iteration-validate.sh` (in `tools/`) — the wholesale gate that
  takes a pattern's current iteration, renders it, encodes it,
  scores it, and emits a single verdict.
- `iterate.sh` — the agent-facing loop driver that ingests a verdict
  and produces the next edit (or stops).
- Skills under `.claude/skills/` — `pattern-decomposition`,
  `iterate-detector-calibration`, `present-options`,
  `handle-falsification` — the codified workflows agents invoke.

**The DSL Metadata Contract (`docs/dsl-metadata-contract.md`)** is the
load-bearing cross-repo agreement: every fact bikar's DSL knows at
authoring time propagates through SVG `data-*` attributes as
authoritative ground truth that qiyas reads directly. This is tenet 21
(DSL-as-source-of-truth) in operational form. **When bikar gains a
new authoritative fact OR qiyas needs a new field, amend this doc
first**, then ship the bikar emit + qiyas read sides together.

**Auto-capture-on-GO (sacred-patterns#77)** closes the loop: when an
iteration converges to GO verdict, the artifacts auto-promote into
qiyas's fixture corpus so the next baseline is the converged result.
This is the mechanism that prevents iteration drift across sessions.

**Critical-path drift audit** (`qiyas/calibration/critical-path-drift-audit.py`)
classifies cross-repo tasks as ON_PATH (blocking the cascade) vs
OFF_PATH (parallel work), giving the routing protocol in
[`.claude/plans/post-i1-task-routing.md`](../../sacred-patterns/.claude/plans/post-i1-task-routing.md)
its data. Read both before any routing decision.

**Companion mental-model docs** (read these to understand the other
ends of the cascade):
- [bikar/docs/dev-mental-model.md](https://github.com/NaqshCoffee/bikar/blob/main/docs/dev-mental-model.md) — DSL → SVG, the 5 emission channels, gt-emitter hazards
- [qiyas/docs/dev-mental-model.md](https://github.com/NaqshCoffee/qiyas/blob/main/docs/dev-mental-model.md) — SVG → encoding, detector pipeline, fast-path, diff

When any of the three sides of the cascade changes its surface, update
all three mental-model docs in the same PR series.

## How do I know if a decision was already made / tried / falsified?

Consult **`docs/decisions/LEDGER.md`** (per-repo) and
**`docs/decisions/LEDGER-XREPO.md`** (the cross-repo roll-up that joins qiyas +
bikar + sacred-patterns by problem-tag) — the generated, can't-drift index of
what's decided / dead / authoritative-per-tag. Because tags surface across repos
(`face-class-identity` lives in both qiyas and bikar; the `svg-direct` spine
crosses qiyas + SP), the cross-repo ledger is the right first stop from the
orchestrator seat. Look up your problem-tag (vocabulary in
`docs/decisions/tags.yaml`); the dead-ends table marks falsified approaches
`DEAD` / `REFUTED` / `OPEN`. This is the first stop *before* re-deciding, per
tenet C1.

Why it can't lie: the ledgers are generated from each decision doc's structured
frontmatter keys (`scripts/gen-decision-ledger.sh` +
`gen-decision-ledger-xrepo.sh`, `npm run ledger`), and a gate
(`scripts/check-decision-coherence.sh`, `npm run check:decisions`, run from
`.husky/pre-commit`) keeps them honest. Schema + Mermaid state machine:
`docs/decision-schema.md` (this repo is the canonical home; mirrored into qiyas +
bikar). When you author a decision via `present-options`, its §0 Premise check
forces this lookup; when one is falsified via `handle-falsification`, its L0
branch + `dead_end:` step write the falsification back into the ledger.

→ [decision-schema.md](decision-schema.md) · [LEDGER-XREPO.md](decisions/LEDGER-XREPO.md)

## Decisions that shaped this codebase

### Construction must be able to express extended-then-clipped shapes

bikar's DSL must let a construction reach beyond its natural boundary and
then clip the result to a containing region — that's the canonical mechanism
behind Islamic-pattern partial shapes (Kaplan's "boundary segment removal"
and the same pattern Asymptote expresses with `clip(picture, path)`). When a
satellite star's edges should extend into its neighbor's territory and then
be clipped along their shared chord, the renderer is *not* drawing a
"half-star" literally — it's drawing the full construction and clipping. The
qiyas detector mirrors this on the read side: a partial polygon whose
endpoints land on a zone boundary and whose vertex count would close into N
if extended is `CLIPPED-MISSING`, distinct from `MISSING` (no construction
attempted). This makes the iteration loop's signal actionable: every
`CLIPPED-MISSING` warning maps to a one-line `extend ... clip-to <boundary>`
edit instead of a hand-derived fix. The principle generalizes beyond
medallion-10 to every pattern with internal boundaries — Phase 1.B's
multi-ring corpus and any future decagram-strapwork construction inherits
the primitives.
→ [2026-05-07 — partial-shape rendering via construction](decisions/2026-05-07-partial-shape-rendering-via-construction.md)
