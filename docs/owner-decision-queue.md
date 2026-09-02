# Owner decision queue — 2026-06-10 digest

One page, every open decision doc across the three repos (source:
`docs/decisions/LEDGER-XREPO.md`, 19 docs / 14 tags), ranked so you can
clear the genuine picks in one sitting. Format proven 2026-05-24 (7-task
gridlock cleared in one pass).

**The split:** 8 docs are *reconciliations* — reality or a prior owner pick
already decided them; they need status surgery, not judgment. 6 tags need
you. Each row names what your pick unblocks.

## Bucket A — reconciliations (no decision needed; loop ships these under existing authority)

| Tag / doc | Why it's already decided |
|---|---|
| `shape-vocab-typed-params` (3 docs) | Option C (Pydantic discriminated union) **shipped** — #525/#531, owner-approved 2026-05-24; schema now 1.20. Mark ACCEPTED citing the pick + commits; sequencing doc's #410 gate is moot post-cutover. |
| `serialization-d4` | Option B (schema bump + baseline regen) **happened** — schema went 1.17→1.20 across shipped cutovers. Mark ACCEPTED with evidence. |
| `anti-symmetry-floor` | **Overtaken 2026-06-10**: the Star-8/Hexagram breach witness XPASSed under the trust-plan filtering and is now a live passing assertion (qiyas `06e632b`). Mark RESOLVED-superseded. |
| `fill-void` | Option B (explicit `classify` companions) **effectively shipped** via the 2026-05-19 corpus sweep (~91% of the gap closed, routing doc §B6). Mark ACCEPTED-as-implemented. |
| `i1-ratchet` | The doc's own 2026-05-28 adjudication resolved the open question (7 un-indexed dirs all FALSIFIED ticks; Option A index-read). Reversible CLI behavior → documented default. |
| `scope-rescope` | Option A (close I1 at shipped state) — the cascade closed long ago; status-only. |
| `closeout-report-surface` | Option A (markdown report) was built (CLOSEOUT-REPORT.md exists). Mark done; Option C (CLI generator) stays a someday note. |
| `star7-red-detection` (routing doc of the pair) | Routing (extend I1) stands but the mechanism doc superseded its HSV approach with Tenet-23 metadata consumption, and Universal DSL Tagging shipped the plumbing. Reconcile the pair to one authoritative doc. |

## Bucket B — genuine owner picks (6, ranked by unblock value)

1. **`derived-shape-naming`** (bikar) — *What do mirrored/rotated copies of a
   named shape get called in the DSL?* Doc recommends Schoenflies suffixes
   (`__C5_2`, `__sigma`). **User-visible language design — your taste call.**
   Unblocks: `mirror-rotate` (which is gated on this), the line-primitive
   cascade's naming arm, and ultimately richer transform support in every
   future pattern. *This is the highest-leverage pick on the board.*
2. **`mirror-rotate`** (bikar) — falls out almost automatically once #1 is
   picked (Option A vs B is determined by the naming answer + whether you
   want mirror-only or symmetric mirror+rotate scope).
3. **`line-primitive`** (bikar) — *Should a `line` cut faces (CGAL model) or
   stay render-only?* Doc recommends Option E (face-cutting + a default
   class for unclassified sub-faces). Architectural commit to the
   face-walker; unblocks the whole D1–D3 line cascade. Recommend: accept
   Option E — it's the Tenet-30-shaped answer (the engine capability, not
   the per-pattern workaround).
4. **`arc-lens-partial`** (bikar + sacred-patterns pair, REOPENED) — the old
   Option A cascade is a recorded dead end; the falsification points at
   "Option I: qiyas detector + sliver cleanup." Pick needed: bless filing
   Option I as a fresh, narrow decision doc and retire the REOPENED pair to
   SUPERSEDED. (Mostly housekeeping; one nod from you.)
5. **`ci-coverage-telemetry`** (qiyas) — *Which canonical bikar pattern does
   the cross-repo DSL-contract CI gate render?* (Q2). One-line answer;
   unblocks wiring the validate-dsl-contract gate into bikar CI. Suggest:
   single-petal (Tier 0, the atomic witness).
6. **`closeout-feedback-surface`** + **`svg-direct`** (qiyas) — both look
   overtaken (the review portal *is* the feedback surface now; SVG-direct
   shipped and medallion-10 converged at iter-33) but each needs a 5-minute
   verification before closing. Pick: authorize the verify-and-close pass.

## Suggested sitting

Answer 1–3 (the bikar trio — they interlock), nod 4–6, and the loop ships
Bucket A plus the closures with evidence citations. Net effect: the open
queue drops from 19 docs to ~2 fresh, narrow ones (line-primitive
implementation decision trail + arc-lens Option I).

---
*Generated 2026-06-10 from the LEDGERs + a per-doc staleness audit. Statuses
verified against shipped code where claimed (C2); verify counts against
`docs/decisions/LEDGER-XREPO.md` if reading this later.*
