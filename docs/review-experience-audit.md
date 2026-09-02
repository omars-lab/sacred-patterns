# Review-experience UX audit — four good rooms, no house

Plain English: the owner asked (2026-06-11) to "look at the review experiences
as a whole and evaluate its ease of use, intuitiveness, etc". This doc is that
evaluation. The yardstick is the art-savvy-grandma bar (bikar/qiyas Tenet 27):
a non-technical person with a trained eye must know what to click within 5
seconds, see no engineering jargon, and a few clicks must still capture
structured, replayable feedback.

Status: IMPLEMENTED (2026-06-11, same day). Recommendations 1–5 all shipped
in `tools/wave-plan-server.py` + `tools/plan-waves.py`: the hub front door
at `/` (reads stage_gates, plain-language cards), the in-studio agreement
button (`POST /api/agree` → session.json), the palette-gate page at
`/palette` (swatch sheet + agree + auto-saved note box), and one shared
save model (auto-save / Apply with visible confirmation). The
structure-priorities annotator is retired — its docs pointers now route to
the studio; the file remains on disk only as history. A same-day owner pass
added: wave-merge ("Move wave" merges everything like it), wave-level
take-out, paired shape/wave buttons everywhere, viewport-capped image, and
a design-system polish (shared tokens, one button system, serif display
voice) answering "button alignment is off, experience not modern".

## The headline finding

Each review surface individually is decent-to-good. The problem is the whole:
**four disconnected islands with four different launch mechanisms**, and
nothing tells the owner what needs their eyes today.

| Surface | How you get there | How feedback is saved |
|---|---|---|
| Wave-plan studio | run `tools/wave-plan-server.py`, open port 8765 | orange "Apply my fixes" → server persists + re-plans |
| qiyas review portal | run `qiyas review …` with the right flags, port 8000 | auto-saves on every Confirm |
| structure-priorities annotator | open an HTML *file* (file://), no server | downloads a JSON the owner must move into place |
| Palette swatch gate | someone sends a PNG | say so in chat; we transcribe it into session.json |

The owner cannot sit down and ask "what's waiting for my review?" — they must
know which tool to launch for which gate, on which port, with which flags. The
session already *knows* the answer (`session.json` → `stage_gates` records
exactly which gates are open) but no surface reads it back to them.

## Surface-by-surface

### Wave-plan studio (sacred-patterns `tools/wave-plan-server.py`, 2026-06-11)

The strongest surface, with one telling gap. Plain-language header; click any
shape → its groups in words ("Wave 1 — 1 dark-blue shape in the middle
flower"); fixes are explicit buttons; Apply round-trips through the server so
corrections re-flow into every picture, count, and validation.

Gaps:
- **No "the plan looks right — start building" button.** The agreement — the
  actual gate the page exists for — still travels through chat and gets
  hand-transcribed into `session.json`.
- **The open adjudications aren't asked on the page.** Wave 13 (turquoise
  ring r≈0.59: inner or outer flower?) and wave 15 (small navy stars r≈0.65)
  live in a JSON field; the surface lets the owner fix things but never asks
  the questions we actually have.
- Apply takes ~10–15 s (full re-plan) — covered by a hint, acceptable, but
  the reload drops scroll/selection state.

### structure-priorities annotator (`review/structure-priorities.html`)

**Fails the standard the owner set, and the evidence is on disk.** It is a
static file with a "Save my picks" button that *downloads* a JSON — exactly
the download-dance the owner rejected for the wave plan. Witness that the
pattern fails in practice: `structure-priorities.json` does not exist on disk
— the picks never made it back. Its Step 2 (click shapes in priority order)
is also superseded: the wave plan *is* the build order, with far better
structure. Recommendation: **retire it**; fold its one surviving job
(confirm the red cross is the center) into the studio's first load as a
single click.

### qiyas review portal (`qiyas review`)

The guided mode ("SimpleReview" / spot-the-difference) is genuinely
grandma-grade: synced magnifier lens, flip mode, click-mark-note-confirm,
numbered dots for what's done, opt-in machine hints, auto-save with resume.
It is the best interaction pattern we have; the other surfaces should imitate
it.

Blemishes:
- **Which experience you land in depends on CLI flags** (`--against`,
  `--advanced`) rather than anything the reviewer chooses on screen.
- The compare URL is a five-parameter monster no human could reconstruct.
- Developer-mode labels (Q5/Q9/Q11, "fold=6 (94%)", "scoreable shapes") are
  fine for engineers but leak into the guided wizard's step titles.
- The sessions landing page is good (two plain sections, one click to enter)
  but only covers qiyas-side artifacts — it knows nothing about the wave
  plan or palette gates.

### Palette swatch gate

**No surface at all.** It's a PNG (`input/reference-analysis/swatch-sheet.png`)
and a chat message. By our own bar, agreeing on colours should be: swatches
beside the photo, "these are right" or click the wrong swatch and pick what
it should be. This is the least-built gate and it is next in the pipeline
once structure passes.

### Cross-cutting: inconsistent "did it take?" semantics

Three different saving models (auto-save / batch-Apply-and-wait /
download-a-file). Each is learnable alone; together they mean the owner can
never be sure whether the last click stuck without remembering which room
they're in.

## Recommendations (in order of value)

1. **One front door.** A single command serving a hub page that reads
   `session.json` → `stage_gates` and says, in words: "Two things need your
   eyes: ① the wave plan — agree or fix it, ② the colour swatches." Each
   links to its surface. Everything else hangs off this.
2. **Put the gate in the studio.** An "I agree — start building" button that
   records `wave_plan.agreed` server-side, plus the two adjudication
   questions asked explicitly on the page with two-button answers.
3. **Retire structure-priorities.html** (center-confirm moves into the
   studio's first load).
4. **A palette-gate page** in the same style: swatches + photo, agree or
   correct, POST to the server.
5. **Unify save semantics** — pick one model (the portal's
   auto-save-with-confirmation is the best of the three) and a visible
   "saved ✓" everywhere.

## Provenance

- Owner directives this audit answers: "look at the review experiences as a
  whole and evaluate its ease of use, intuitiveness, etc" (2026-06-11);
  earlier the same day: "this should not be static html, but rather cli
  commands that runs localhost" (the standard the annotator now fails).
- Companion docs: `docs/wave-planning-design.md` (the studio),
  qiyas review portal (`qiyas/src/qiyas/review/`), bikar/qiyas Tenet 27
  (the grandma bar).
