# RESUME — medallion-10 weave reconstruction (PARKED 2026-06-26)

> **This is the single front door to the parked medallion-10 weave work.** It indexes every
> decision doc, memory, frozen test, studio URL, and the one next action — it does not restate them.
> Backed by GitHub issue **NaqshCoffee/bikar#2** and plan
> `bikar/.claude/plans/park-medallion-weave-handoff.md`.

---

## 1. TL;DR — where we stopped and why

We **paused before the owner's whole-field gate (#23)**. All structural and presentation gates are
GREEN and frozen as tests (Phases 0–5). The construction converges on the reference; the only thing
left is the owner's by-eye verdict on the finished deliverable — and the owner chose to pause there
deliberately ("there is much for us to learn here") rather than rush the verdict. Nothing is broken;
this is a clean park, not a stuck state.

**The single next action to resume:** bring the studio back up (§5), surface the deliverable, and let
the owner judge gate #23 via the studio. If approved → land the params into the flat pattern. If
rejected → fix only the named gap on `feat/strapwork-outer-edge-closure` with a Tier-0 witness + a
vitest, restart :8765, re-surface. See §6.

---

## 2. The approach in one paragraph

The reference is a **grown girih field** of ten decagon rosettes packed edge-to-edge into one dense
disc, with a white strapwork interlace framing every tile and colored faces recessed inside the
woven cells. We build it with one engine primitive — `girih field decagonal 30 shells 1 star 4` —
plus a `strapwork` pass, then style + clip it. We replaced a failing **10-round eyeball loop** (nudge
a crop/zoom of the finished picture, ask "looks right?") with a **six-phase loop where every phase
gates on an objective number** (a face count, a crossing ratio, a coverage %, a lobe count) read from
`gt.json` / strapwork data / `qiyas pixel-diff`, and **each gate is frozen as a test the moment it
passes** — so re-deciding a settled knob turns a green test red. "Wave N" is a pure review aid (a
radial crop of the whole field), never structure.

---

## 3. The thinking — what we learned (so we don't relearn it)

- **The 10-round eyeball-loop trap.** For ten rounds we tuned a crop fraction / zoom of the
  already-finished field and judged by eye. Two things were broken and neither was the pattern's
  structure: (a) the **measuring ruler distorted** — our panel auto-fit to fill, the reference showed
  at native scale, so ours looked ~5.3× bigger ("not same size"); (b) **no objective gates** — "looks
  right/wrong" can never tell you *which layer* is off. Phase 0 fixed the ruler (shared floor +
  symmetric scale); Phases 1–5 added a measured gate per layer.
- **The §10 degree-2-graph dead-end.** An attempt to weave per-wave produced a degree-2 graph with
  **0 crossings** (no self-crossing network). Resolution (§11): the all-at-once weaver on the whole
  gap-free field is the robust path — decorations join across shared tile edges into ONE connected
  interlace with hundreds of crossings.
- **The §12.5→§12.7 re-decide trap.** The same shells/zoom/floor knobs were re-decided three times,
  each from a fresh screenshot. Frozen gates make that structurally impossible now.
- **Discrete vs. overlapping rosettes — settled.** The reference rosettes **OVERLAP** (edge-share,
  ~2.0·apothem) into one dense disc with no center void — they are NOT discrete units at 2φ. The
  "build 11 discrete edge-kissing rosettes" reopen (#66) was a misread and was **CANCELLED by the
  owner 2026-06-24** (decision §13). The grown field is the right primitive.
- **The reference is FLAT.** "Genuine over/under depth" is in our match-target text but NOT in this
  reference image — it's a flat interlace mosaic. Chasing 3-D ribbon shadow would diverge from the
  reference (Tenet 7). Thin navy casing is the correct, perceptually-subtle-by-design match.

**Dead-ends — do NOT re-open** (full detail in the park plan §"Harvested findings"):
1. Don't rebuild as hand-attached discrete rosettes — overlapping grown field is correct.
2. Don't add a `merge_eps` knob — the strapwork graph is already ONE connected network (650 nodes,
   zero orphans, 560 crossings, 90 strands; the ~1120 `data-strand` values are correct degree-2
   runs-between-crossings by design, bikar#16).
3. Don't chase a 3-D ribbon shadow — the reference is flat.
4. Don't try to make the engine build wave-by-wave — "wave N" is a 34% radial crop; #52 is won't-do.
5. The periwinkle-centre palette detail is DROPPED — `ring_band` is global-extent scale-coupled.

---

## 4. Frozen gates (Tenet 18 witnesses) — a refactor must not silently break these

| Phase | Gate (number) | Test file | Engine guarded |
|---|---|---|---|
| 2 — star sharpness | {10/4} tip/valley = **3.078** (k=2→1.176, k=3→1.618) | `bikar/packages/core/tests/kernel/girih-tiles.test.ts` | `decagonStarPairs(k)` — `girih-tiles.ts:140` |
| 3 — interlace | **560** crossings, **280/280** over/under, **94.6%** at r>0.2R | `bikar/packages/core/tests/dsl/medallion-girih-field-weave-connectivity.test.ts` (Phase-3) | `evaluator.ts` → strapwork |
| 4 — color | royal #3F77C4=**21**, navy #112658=**260**, teal #439EC4=**170**, dnavy #0F2050=**350**, #3C3F47=**0**, total ~**802** | same file (Phase-4) | `evaluator.ts` + fill recipe |
| 5 — boundary | lobe-count==**10** @ 36°, R_in/R_out=0.90, rot=18°, N=12 falsifiability | `bikar/packages/core/tests/render/flower-clip-lobe-count.test.ts` (7 tests) | `scallopedFlowerLobes()` — `svg-utils.ts:564` |
| #71 — page default | `flipped=true`, cells+clip checked, wave=22, white panels | `sacred-patterns/tests/test_weave_progress_opens_on_deliverable.py` (6 tests) | `tools/wave-plan-server.py` |

**Locked construction (do NOT re-litigate):** `girih field decagonal 30 shells 1 star 4` + `strapwork`
(`width 1.8`, `crossing alternating`, `color #FFFFFF`, `casing #000000`). shells=1, zoom=1.0.
Home `.bkr`: `girih-network/girih-weave.bkr` (this session). Authoritative full deliverable DSL is
inlined in the connectivity test.

---

## 5. How to bring the studio back

```bash
# from the sacred-patterns repo root
python3 tools/wave-plan-server.py \
  /Users/omareid/Dropbox/Data/sacred-patterns/bikar-medallion-10 \
  --center 386 361 --diameter 738 --port 8765
```

Env var overrides (defaults baked into the server header, only set if your checkout differs):
- `BIKAR_NODE_BIN` (default `/Users/omareid/.nvm/versions/node/v22.22.3/bin/node`)
- `BIKAR_CLI_JS` (the bikar CLI `dist/index.js`)
- `QIYAS_PY` (default `/Users/omareid/Workspace/git/qiyas/.venv/bin/python`)

**Canonical colored deliverable** (note: `/weave-progress.png` and `/weave.png` take DIFFERENT param
sets — don't mix them):

```
http://localhost:8765/weave-progress.png?wave=22&waves=22&cells=1&card=%23FFFFFF
```
(`shells=1`, `edge=30`, `star=4`, `width=4`, `color=#FFFFFF`, `clip=1` are the defaults.)

The interactive page opens ON the deliverable (shapes view, full disc, white backdrop) per #71:
```
http://localhost:8765/weave-progress?wave=22&waves=22&edge=30&star=4&width=4&color=%23FFFFFF&card=%23FFFFFF&cells=1&clip=1&flip=1&zoom=1.0
```

**Reference image:** `/Users/omareid/Dropbox/Data/sacred-patterns/bikar-medallion-10/input/reference.jpg`

**Gate #23 verdict mechanism:** written by `POST /api/weave-verdict` to this session's
`session.json` → `stage_gates.weave.{approved,approved_date,verdicts}`. Currently
`approved=false`, `verdicts=[]`. **NEVER self-approved — owner-only, via the studio.**

---

## 6. Where to resume — the single next action

1. Bring the studio up (§5), `curl` the canonical deliverable PNG, Read it, write the
   expectation first, compare to `reference.jpg` (Tenet 24/25b).
2. Surface an all-dial `open`ed studio link to the owner (every dial as an explicit URL param).
3. **Owner judges gate #23** via the studio (`POST /api/weave-verdict`).
   - **Approved** → land the accepted params into the flat pattern; freeze the accepted
     `coverage.shared_pct` + per-zone SSIM floor as a corpus pytest; close the cascade.
   - **Rejected** → read the note, fix the ONE named gap on `feat/strapwork-outer-edge-closure`
     with a Tier-0 witness + vitest (Tenet 18), restart :8765, re-surface.

Detail for the *what-to-do-next* lives in the six-phase plan and the LOOP/OPEN-ITEMS prompts (§7).

**Resume follow-ons (part of this deliverable, not orphaned tasks)** — `bikar/.claude/plans/park-medallion-weave-handoff.md` → "Resume follow-ons":
- **Follow-on A — build the weave-building skill (task #5, OPEN).** Codify the converged iterative weave/strapwork-reconstruction method (grown girih field + phased objective-gate loop) into a reusable skill. Needs neither the studio nor gate #23, so it can be done independently of the owner's #23 verdict — best done while the experience is fresh.
- **Follow-on B — general visual-verification rule → DONE.** Landed as `bikar/CLAUDE.md` **Tenet 29** (every visible artifact is rendered, looked at expectation-first, compared to its reference before surfacing; surface via an openable params-shown link; enforced by the tenet stop-rule, not a Stop hook). Closed task #8.

**Named residual the owner may weigh at #23:** at the `.png`'s 1024px scale the white straps read
heavier than the reference's delicate ribbons (over/under reads flat); at the page's native ~300px
scale they read proportionate. That's the owner's call, not a structural defect.

---

## 7. Index — every artifact by path

**Decision docs (the why)** — `bikar/docs/decisions/`:
- `2026-06-16-weave-stage.md` — weave is a first-class stage
- `2026-05-28-medallion10-girih-ceiling.md` — the `girih field` generator primitive
- `2026-06-19-weave-field-method.md` — Option A; §10 degree-2 dead-end; §11 resolution; §12.7 shells-1; §13 reopen cancelled
- `2026-06-22-weave-strap-shadow-style.md` — tune the casing emitter, not a new shadow filter

**Load-bearing memories** — `~/.claude/projects/-Users-omareid-Workspace-git-bikar/memory/`:
- `medallion10_structure_is_packing_not_concentric.md`
- `medallion10_girih_field_is_the_white_network_generator.md`
- `medallion10_field_scale_count_coupling.md`
- `medallion10_deliverable_endpoint_vs_preview_endpoint.md`
- `weave_interlace_break_at_crossings.md`
- (plus `medallion10_weave_parked.md` — the park pointer)

**Frozen tests** — see the §4 table for paths.

**Driving docs (the what-to-do-next, kept on disk, not restated here):**
- `bikar/.claude/plans/refactored-fluttering-pnueli.md` — the six-phase execution plan
- `bikar/.claude/prompts/medallion-10-LOOP.md` — the `/loop` engine prompt (now PARKED)
- `bikar/.claude/prompts/medallion-10-OPEN-ITEMS.md` — the open-items snapshot (now PARKED)

**Park artifacts:**
- GitHub issue `NaqshCoffee/bikar#2`
- `bikar/.claude/plans/park-medallion-weave-handoff.md`
- `bikar/docs/backlog.md` (index row)
