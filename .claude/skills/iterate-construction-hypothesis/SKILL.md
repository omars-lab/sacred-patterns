---
name: iterate-construction-hypothesis
description: Use this skill when a pattern reconstruction has plateaued and the next move is to try a DIFFERENT bikar DSL construction — not to tune the qiyas detector. Encodes the hypothesize-author-render-verify-measure-log loop for the CONSTRUCTION side: you change the .bkr (circles, divisions, connect/arc statements, repeat/rotate, classify rules), render it, verify it visually through the review portal, and measure composite_score against the prior iteration — while the detector stays frozen. The defining guard is the inverse of iterate-detector-calibration: tweak the construction, NEVER the thresholds. USE THIS SKILL ANY TIME you are about to change a .bkr to move a reconstruction score, especially when the plateau tempts you to instead loosen a detector tolerance.
user_invocable: true
argument: session-slug (e.g. bikar-medallion-10) — the Dropbox iteration session to advance
---

# iterate-construction-hypothesis

This skill drives **construction-side** pattern iteration as a self-aware
loop with persistent memory and explicit loop-detection. It is the mirror
image of qiyas's `iterate-detector-calibration`: that skill changes the
*detector* to better read a fixed construction; this skill changes the
*construction* to better express the intended geometry, with the detector
held fixed.

## The plain-English problem this solves

A reconstruction (medallion-10 is the canonical case) gets to a score and
*stops moving*. The reflex is to reach for a detector knob — "the matcher
won't pair these two faces, let me loosen the cost" / "the symmetry pillar
mis-scores, let me widen the fold tolerance." That reflex is a Tenet 7
violation in disguise (sacred-patterns Tenet 23 names it precisely:
re-deriving / re-tuning downstream what the construction should have
declared upstream). Every threshold you loosen to fit one pattern is noise
the next pattern's detector has to compensate for.

This skill says: **when the score plateaus, the hypothesis is about the
construction, not the detector.** Maybe the medallion needs a different
overlay star ({10/3} vs {10/4}), maybe the petals need to be built from
girih tile primitives instead of wedge-and-rotate arcs, maybe two faces
the detector "can't tell apart" are genuinely the wrong shape in the
`.bkr` and should be re-authored. The detector is the *oracle that tells
you the construction is wrong* — you fix the construction, never silence
the oracle.

## When to use

- A reconstruction's `composite_score` has plateaued across ≥2 iterations
  and the next idea you have involves a `.bkr` edit (new construction
  lines, different overlay, re-authored faces, a new `classify` rule, a
  symmetry-order change).
- You catch yourself about to edit a qiyas detector parameter, segmenter
  choice, matcher cost, or signature tolerance to make a *specific
  reconstruction* score better. **STOP — that's this skill's trigger, not
  iterate-detector-calibration's.** (That skill is for closing
  *corpus-wide* identity-fidelity gaps where the construction is ground
  truth and the detector is genuinely wrong. If you're tuning the detector
  to fit *one* reconstruction, you're in the wrong loop.)
- The medallion-10 ceiling (sacred-patterns #85) or any "this pattern
  won't converge under the current construction philosophy" situation.

## The hard line — construction vs detector

| You may change (construction side) | You may NOT change (detector side) |
|---|---|
| `.bkr` blueprint (circles, lines, divisions, named points) | qiyas matcher cost weights / `CLASS_MISMATCH_COST` |
| `connect` / `connect arc` / `cycle` statements | qiyas segmenter choice (watershed/CCL), confidence floors |
| `repeat N` / `rotate N` / `mirror` symmetry constructs | qiyas signature normalization tolerances, fold slack |
| overlay star order ({10/3} vs {10/4}), petal construction method | `_check_dominant_fold` thresholds, ARI merge gates |
| `classify .name where …` rules, per-edge class tags | qiyas `acceptance.yaml` gate values, visibility-filter knobs |
| new DSL primitives in **bikar** (girih tiles, chirality, etc.) | anything in `qiyas/src/qiyas/**` that reads a number to decide a verdict |

If the fix genuinely requires a *new bikar DSL capability* (a primitive
that doesn't exist yet — girih tile, chirality, conditional template
block), that is still construction-side: it's a bikar feature, file it and
build it. It is categorically different from loosening a qiyas number.

**If you believe the detector is genuinely wrong** (not just inconvenient
for this pattern) — i.e., it mis-reads a construction that is provably
correct — that is NOT this skill. Switch to `escalate-qiyas-divergence`:
capture the fixture, file the qiyas issue with a reproducer, and let the
detector fix happen in qiyas's own calibration loop with its own
corpus-wide regression guard. The split is: *construction wrong → fix here;
detector wrong → escalate there; never tune the detector from here.*

## Hard prerequisites — read these BEFORE acting

Blocking. Do not start an iteration until you have read all four:

1. **Memory index.** Read
   `~/.claude/projects/-Users-omareid-Workspace-git-sacred-patterns/memory/MEMORY.md`.
   Read the full bodies of any entry bearing on this reconstruction's
   construction philosophy — for medallion-10 that includes
   `feedback_a6_baseline_construction_philosophy_mismatch` (the 5
   falsifications proving parameter-tuning can't break the ceiling) and
   any `feedback_bikar_*` face-walker memory relevant to the shapes you're
   about to author. **If a memory cites a construction approach already
   falsified for this gap, do NOT re-attempt it without first reading WHY
   it failed.** If the reason no longer applies, note that in the iteration
   log; otherwise pick a different hypothesis.
2. **Session state.** Read the session's `session.json`, `discoveries.md`,
   and the last 2 `iterations/N/evaluation.md` at
   `~/Dropbox/Data/sacred-patterns/<session-slug>/`. These name what
   construction was tried, what it scored, and why it stalled.
3. **The plateau evidence.** Read the latest `iterations/N/validation/
   validation.json` — the `composite_score`, the ranked `warnings`, and
   the `svg-audit` A1/A2/A4/A5/A6 verdicts. The warnings name the discrete
   construction gaps to attack (a missing face, a wrong fold, a
   shape-count divergence). **`cf_delta` in a warning is upside-only —
   model the cost** (memory `feedback_cf_delta_cost_blind`): on a
   saturated mesh the edit's cost can dominate its predicted lift.
4. **The reference.** Open `input/reference.{jpg,png}` and the latest
   `iterations/N/render.svg` side by side in the review portal (Tenet 27).
   Write down, before iterating, the single most visually-wrong thing —
   that is your gap.

## The iteration recipe

For each iteration N:

### Step 1 — Pick the construction gap (write the log header FIRST)

Create `iterations/<N>/hypothesis.md` with this frontmatter BEFORE any
`.bkr` edit:

```markdown
---
attempt: N
date: YYYY-MM-DD
gap_targeted: "<one-sentence visually-confirmed gap from the portal look>"
construction_hypothesis: "<what about the CONSTRUCTION is wrong, and why>"
bkr_change: "<the smallest single .bkr edit — or named bikar primitive to add>"
predicted_lift: "<+0.NN composite, and which warning it should clear>"
predicted_cost: "<what the edit might BREAK — new false faces, fold change>"
prior_art_searched: "<web search query for the construction technique, or 'none'>"
related_memory: "<memory files read that bear on this construction>"
detector_untouched: "confirmed — no qiyas param/threshold/cost in this iteration"
---

## Plan
<why this gap, why this construction hypothesis, why this is the smallest edit>

## Guardrails check
- This is a CONSTRUCTION edit (.bkr / bikar primitive), not a detector edit: confirmed
- Construction-philosophy memory checked — this approach not already falsified: confirmed (or: falsified before because X, but X no longer applies because Y)
- predicted_cost names a concrete failure mode I will look for in the render: confirmed
```

If you cannot fill a field honestly, STOP and surface why instead of
fudging.

### Step 2 — Make the change: exactly one construction idea

One overlay change, one petal-construction method, one symmetry-order
edit, one re-authored face group, one new `classify` rule. Not two. The
point of single-change iteration is causal attribution against the score.
If a construction idea is "obviously" multi-part (new blueprint + new
overlay + new faces), it is a multi-iteration plan — split it, ship the
blueprint change first, measure, then the overlay.

If the idea needs a bikar primitive that doesn't exist, that primitive is
its own task (file it, build it in bikar with its own Tier-0 test per
bikar Tenet 17) — do not fake it with a hand-placed magic-number
approximation (bikar Tenet 9). A missing primitive is a real finding;
surface it.

### Step 3 — Render and VISUALLY VERIFY (Tenet 27 — the ship gate)

Render the new `.bkr` (bikar CLI per Tenet 26) and run the orchestrator:

```bash
./tools/iteration-validate.sh \
    --svg iterations/<N>/render.svg \
    --reference input/reference.jpg \
    --baseline input/baseline.json \
    --out iterations/<N>/validation/
```

Then — **before reading the score** — open the render in the review
portal and look at it against the reference and against the `predicted_cost`
you wrote in Step 1. State what you see. The order matters: if you read the
score first, the eye rationalizes the number. **No iteration is "shipped"
(committed, recorded as the new best, declared converged) without a
recorded review-portal verdict** — that is Tenet 27, and it is the whole
reason the detector can stay frozen: the human eye, not a loosened
threshold, is the acceptance authority.

### Step 4 — Measure against the prior iteration

Compare `composite_score` and the specific warning you predicted you'd
clear. Three outcomes:

- **Lift confirmed + visual confirms + no new defect** → record as the new
  best in `evaluation.md`, commit the `.bkr`, advance.
- **Score up but the portal shows a new defect** (a face the metric likes
  but the eye rejects) → NOT shipped. The metric is lying; Tenet 27 caught
  it. Log the divergence, revert or refine.
- **No lift / score down** → the construction hypothesis is falsified for
  this gap. Go to loop-detection.

### Step 5 — Log the outcome in `evaluation.md`

Record observed vs predicted lift, the portal verdict, and whether the
`predicted_cost` materialized. This is the witness the next iteration reads
in Step 1 prerequisite 2.

## Loop-detection — the stop rules (Tenet 7 + memory)

Stop and escalate when ANY fires:

1. **Same construction approach falsified twice.** If two iterations tried
   variants of the same construction idea (e.g. two different overlay-star
   orders) and both failed to lift the score, STOP iterating that idea —
   the gap is deeper than the parameter you're varying. This is the Tenet 7
   stop rule on the construction side; invoke `handle-falsification` on the
   governing decision doc.
2. **Construction-philosophy ceiling.** If the falsifications cluster into
   "the current construction *philosophy* cannot produce the baseline's
   expected vocabulary" (the medallion-10 finding —
   `feedback_a6_baseline_construction_philosophy_mismatch`), STOP. The next
   move is a *different philosophy* (e.g. girih tile primitives), which is
   a scoped bikar feature build, not a loop iteration. Surface it as a
   decision (`present-options`) — don't grind iterations against a ceiling.
3. **You reached for the detector.** If you find yourself wanting to loosen
   a qiyas threshold "just to get this one to match," that is the signal
   the construction hypothesis has run out — STOP and either (a) find the
   real construction defect the detector is correctly flagging, or (b)
   escalate via `escalate-qiyas-divergence` if the detector is genuinely
   wrong. Never tune the detector from this loop.

## Web-search escalation

When a construction hypothesis stalls (rule 1 fired once), web-search the
*construction technique* before the second variant — Islamic-geometry
construction literature (Bonner, Lee, Critchlow, the Topkapi Scroll
analyses) often names the canonical compass-and-straightedge or girih
method for exactly the motif you're failing to reconstruct. A construction
you're hand-deriving may have a documented method that produces the right
face vocabulary directly. Cite the source in the iteration log. This mirrors
`feedback_canonical_algo_web_search` on the construction side.

## Memory contract

- **On resume:** read the construction-philosophy and face-walker memories
  named in prerequisite 1.
- **On a falsification:** write a `feedback`-type memory per
  `handle-falsification` — but only when the lesson is about *construction
  reasoning* (an overlay that can't produce a motif, a face-walker hazard
  that constrains how you can author a shape). A per-pattern score isn't a
  memory; the *generalizable construction constraint* is.
- **On a confirmed lift that breaks a plateau:** note the construction
  move that worked in `discoveries.md` (session-local) AND, if it
  generalizes across patterns, a `feedback` memory.

## Companion skills & tenets

- **`iterate-detector-calibration`** (qiyas) — the mirror loop; that one
  changes the detector against a fixed corpus, this one changes the
  construction against a fixed detector. Know which side you're on.
- **`escalate-qiyas-divergence`** (sacred-patterns) — when the detector is
  genuinely wrong, not just inconvenient; the off-ramp from this loop.
- **`handle-falsification`** / **`present-options`** — when the loop hits a
  ceiling (stop rules 1/2), these capture the dead-end and re-frame the
  options.
- **`learn-new-pattern`** — the authoring skill this loop advances; the
  construction techniques and anti-patterns it loads
  (`generate-drawing/learnings/`) are the source vocabulary for hypotheses.
- **Tenets:** 7 (don't tune to fit — the whole reason this loop exists), 17
  (prove the primitive first — a new construction validates atomic before
  composite), 18 (codify the witness), 23 (DSL-as-source-of-truth — fix the
  construction channel, not the downstream tolerance), 26 (render and look
  while iterating), 27 (no ship without a portal verdict — the gate that
  lets the detector stay frozen).

## Verification — before considering an iteration done

- [ ] `hypothesis.md` frontmatter filled honestly, `detector_untouched: confirmed`.
- [ ] Exactly one construction idea changed; no qiyas param touched.
- [ ] Render viewed in the review portal BEFORE reading the score; verdict recorded (Tenet 27).
- [ ] `composite_score` compared to prior iteration; predicted warning checked.
- [ ] Outcome logged in `evaluation.md`; falsification (if any) routed to a stop rule.
- [ ] If a stop rule fired: escalation skill invoked (handle-falsification / present-options / escalate-qiyas-divergence), not a third blind variant.
