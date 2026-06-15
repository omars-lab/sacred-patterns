# Self-contained loop prompt — medallion-10 (save survives /clear)

Paste everything in the fenced block below into a clean session. It carries the full live
task graph (the in-session task list does NOT survive /clear) plus the proven wave-1 fix.

Snapshot date: 2026-06-14. Latest iteration: iter-71 (strapwork band_width 8→10 SHIPPED).
Structure stage: 17/22 waves passed — NEXT is wave 18 (NOT converged; see correction below).
Waves 16 & 17 were already BUILT (overlays present, emitting); they only needed stamping +
a color caveat on 17. Wave 18 is the first GENUINE structural gap: reference wants 10 royal
star-medallion faces @ r_frac 0.757-0.766, only 2 emit (8 MISSING) — real construction.

STATE CORRECTION (2026-06-14, verified against iter-71 committed tree — Tenet C1/C2):
the medallion-10 construction is NOT converged. Real autonomous construction work remains.
- The wave plan has **22 structure waves**; **16 are passed** (wave 16 stamped 2026-06-14).
- WAVE 16 was already BUILT (overlay pattern.bkr L612–619, emitting since iter-57). The
  iter-71 gt.json carries 40 deep_navy faces @ r_frac 0.64–0.71, census-equal to the 40
  reference non-fragment deep_navy shapes (r_frac 0.638–0.712). It only needed STAMPING
  (invocation-gap, SKILL routing #1) — no .bkr edit (authoring again would duplicate the
  overlay and double the faces). Now stamped in session.json waves_passed["16"].
- NEXT ACTION: **BUILD wave 17** (20 navy faces @ r_frac 0.72–0.73), then 18–22.
- IMPORTANT — waves 17–22 are NOT cleanly pre-built as distinct color groups (verified):
  the render populates the full outer radius, but the overlay classes do NOT decompose
  into the reference per-wave census — reference waves 17/20/22 want 70 `navy` faces yet
  the render emits NO `.navy_wave` class; `.deep_navy_wave=210` is one merged bucket. So
  each of 17–22 needs real construction + per-wave verification, NOT a batch-stamp like 16.
  Build one wave per iteration per the SKILL and the GATE block. When wave 22 passes, the
  structure stage reaches the owner approval gate.
- What IS real and done: color iter-69; wave-1 star fit iter-70; strapwork band_width
  iter-71 (frozen best render). These are genuine — they just are not the *end* of the
  structure stage.
- The top-level session.json `status="converged-interim"` / `remainingVisualGap` fields
  are from the 2026-05-28 interim girih-ceiling bar (iter-33 era) and are STALE w.r.t.
  the wave build. The **22-wave plan is the authoritative remaining-work ledger**.
- OWNER-GATED items (cannot be advanced by the loop) remain: structure/color stage
  approvals (stage_gates.*.approved null — never self-approve); owner re-judges any wave
  in the portal (never self-clear a denial); two bikar commits HELD on feat/divide-offset
  (3ff260a, deef89f — Tenet 22 batch + CI sim).
A loop tick is IDLE only when wave-feedback.py is exit 0 AND every wave 1–22 is passed.
Until wave 22 passes there IS an unfired construction trigger — build the next wave (now 17).
See session.json `liveFront` for the authoritative current state.

---

```
/loop Continue the medallion-10 stage-gated reconstruction loop. Apply the proven wave-1 star fix first, then advance construction.

READ FIRST (the task list does NOT survive /clear — these on-disk anchors are the memory):
- Loop memory: /Users/omareid/.claude/projects/-Users-omareid-Workspace-git-sacred-patterns/memory/MEMORY.md
- Master iteration skill (staged protocol; census = PRIMARY gate, eyeball = DECISIVE, do NOT tune toward iou):
  sacred-patterns/.claude/skills/iterate-construction-hypothesis/SKILL.md
- Session state (waves_passed, stage_gates): /Users/omareid/Dropbox/Data/sacred-patterns/bikar-medallion-10/session.json
- Wave plan (next unbuilt wave): http://127.0.0.1:8765/plan (or tools/wave-plan-server.py source)
- Proven wave-1 fix + evidence: /Users/omareid/Dropbox/Data/sacred-patterns/bikar-medallion-10/handoff/wave1-star-fit/HANDOFF.md

OWNER FEEDBACK FIRST (the decisive gate — check before anything else each tick):
  /Users/omareid/Workspace/git/qiyas/.venv/bin/python sacred-patterns/tools/wave-feedback.py \
    /Users/omareid/Dropbox/Data/sacred-patterns/bikar-medallion-10
  The owner reviews each built wave in the portal (http://127.0.0.1:8765/iterate) and presses
  "This wave looks right" / "Needs work" + a comment. A "Needs work" verdict (exit code 2) is the
  HIGHEST-priority steering signal in the loop — the owner's eye caught a defect the census/coverage
  metrics missed, which is the whole reason the portal exists (Tenets 24/25/27). The comment IS the
  fix instruction. Fix every denied wave (lowest wave number first, Tenet 20) BEFORE the proven-fix /
  construction-advance work below. Re-render, re-run the gate, and the owner re-judges in the portal —
  do NOT self-clear a denial; only the owner flips it back to approved.

LIVE TASK GRAPH (recreate as needed — all that existed at snapshot):
- #58 (NEXT, blocks #50) — Wave-1 center-star fit: apply the PROVEN one-line diff to live pattern.bkr.
    In the latest iteration's pattern.bkr, wave-1 overlay reads `connect every 4 on C0` ({10/4},
    points too thin → gold-sliver whitespace). Change to `hankin angle 54 on C0` (continuous
    contact-angle star, matches reference fatness). C0 stays radius 22.6 / divide into 10 — DO NOT
    resize/reposition (fix is point fatness, not size). Proven in scratch: census-equal (675 shapes,
    zero bucket delta, no face-split), eyeball-matched vs reference; central-star area {10/4}=2551 →
    hankin-54=3189. {10/3}=`connect every 3` overshoots (too fat); 36 too blunt, 72 too thin.
- #50 (in_progress) — wave 7 onward, inner flowers. The active construction front: build the next
    unbuilt wave per wave-plan, one wave per iteration, gated by census + clearance + eyeball.
- #27 (in_progress, umbrella) — Resume medallion-10 loop toward the 80% review gate. The overarching
    front #50/#58 advance under; close when the structure stage reaches the owner gate.
- #39 (pending, engine feature) — Generalized composite-repeat detection: grow composite shapes
    radially outward, test where they repeat. Not blocking the wave loop; pick up when a wave needs it.
- #57 (pending, blocked until the LAST wave passes) — End-of-build DSL reflection: simplify the final
    medallion-10 recipe, capture every attempt (per SKILL item 16). Do NOT start before wave 22 passes.

ORDER OF WORK:
0. OWNER FEEDBACK (above). Run wave-feedback.py. If any wave is denied (exit 2), fix the lowest-
   numbered denied wave FIRST — its comment is the fix instruction — before #58/#50. The owner's
   "Needs work" outranks the proven fix and the construction front; it's the decisive gate.
1. #58 (proven, cheap). Apply the diff, re-render, run the gate (below), mark complete.
2. Then #50 — next unbuilt wave per wave-plan. Continue the loop one wave per iteration.
3. #39 only if a wave needs it; #57 only after the last wave (22) passes.

GATE (every geometry change — staged protocol):
1. Census-equality (PRIMARY): re-render with --emit-truth; diff gt.json (type,sides) buckets vs the
   pre-change render. Only the intended face's shape may change; zero new buckets / no face-split.
2. Eyeball (DECISIVE, Tenet 24/27): STATE the expected visual BEFORE viewing, then build the wave sbs
   crop at matched scale vs input/reference.jpg; confirm the expected change (e.g. gold slivers close).
3. iou is attribution-only — do NOT tune toward it (Tenet 7). Outer waves are saturated-coverage.

AFTER each pass: sync bookkeeping (session.json waves_passed + the progress strip if a wave boundary
moved), update /slides if a wave passed, mark the task complete.

CONSTRAINTS:
- Node 22 for bikar render/commit: export PATH="/Users/omareid/.nvm/versions/node/v22.22.3/bin:$PATH"
- GITHUB_PACKAGES_TOKEN in bikar/.env (git-ignored), source before npm installs: set -a; . ./.env; set +a
- bikar CLI: /Users/omareid/Workspace/git/bikar/packages/cli/dist/index.js
    render <bkr> -o <svg> --emit-truth <gt.json> --image <png> --width 1024 --height 1024
- qiyas venv python (PIL/numpy/scipy/skimage/cairosvg): /Users/omareid/Workspace/git/qiyas/.venv/bin/python
- qiyas detector is FROZEN — never tune a qiyas number from this loop.
- sacred-patterns has NO active CI (pushes cheap); bikar/qiyas pushes follow Tenet 22 (batch, name CI sim).
- LANE NOTE: wave 1 / pattern.bkr is the construction worker's file (#50). If a separate worker session
  is running, run #58 AS that worker or while it's paused — two sessions editing pattern.bkr collide.
```

---

## Maintenance

When a wave passes or a task closes, update the LIVE TASK GRAPH block above so the next
clean session inherits the current state. This file is the durable mirror of the in-session
task list for the medallion-10 loop.
