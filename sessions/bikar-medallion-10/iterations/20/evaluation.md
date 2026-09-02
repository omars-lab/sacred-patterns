# Iter 20 — STOP CONDITION TRIGGERED: composite dropped 0.8236 → 0.697 (-0.13)

## Bottom line

Layering `boundary outline = union(C0)` + `clip pattern to outline` on top of iter-19's `extend` regressed three axes simultaneously:

| Signal | Iter 19 | Iter 20 | Predicted | Verdict |
|---|---|---|---|---|
| composite | 0.8236 | **0.697** (-0.13) | +0.02 to +0.04 | **STOP** (-0.13 vs -0.02 limit) |
| structural | 0/18 | 0/18 | 3-7/18 | **MISS** (still 0) |
| missing-shapes | 32 (sev=warn) | **39 (sev=error)** | ≤20 | **REGRESSED** to iter-18 levels |
| extra-shapes | 30 | 34 | 15-25 | **REGRESSED** (+4) |
| A2 cv | 0.0962 | 0.1026 | similar | flat |
| pixel | 71.3 | 72.9 | +1 to +5 | **PASS** small (the only positive) |
| top warning | extra-shapes | **symmetry-mismatch (cf=0.0958)** | — | **NEW WARNING SURFACE** |

## Root reason

The `clip pattern to outline` primitive isn't working as the cascade plan modeled it. Three things happened together:

1. **Symmetry-mismatch resurged at cf=0.0958.** Clipping the satellite extension arcs at C0 creates boundary-incident edges whose distribution breaks the rotational-orders distribution the symmetry pillar uses to detect the dominant fold. The pillar can no longer see 10-fold cleanly through the clipped fragments.

2. **Missing-shapes went BACK to 39 (sev=error).** Clipping dropped some of the *unclipped* extension shapes that were registering as partial matches in iter-19; the closed-clipped versions don't match expected vertex counts either.

3. **`asymmetric-channel-drift`** new warning surfaced (cf=0.043). Likely the clipped boundary region's color distribution is non-radially-uniform because the clip drops some fills but keeps adjacent ones.

This is not a tuning failure (different factor) — it's a *primitive interaction* failure: `extend + clip(union(C0))` doesn't produce the geometry the reference shows.

## Why the cascade plan's prediction was wrong here

The cascade plan said "clip pattern to medallion_outline converts open arcs into closed partial shapes." On the medallion-10 case, that's incomplete: the medallion silhouette in the reference is NOT a simple `union(C0)` — the satellite circles extend slightly past C0's radius (they're at distance 1.0·R from origin with radius 0.3·R, so their outer reach is 1.3·R). The reference's silhouette is the **union of C0 AND the satellite circles**, not C0 alone.

The plan does mention `union(C0_satellite_circles)` as the boundary in §What needs to change, but the concrete iter-19→20 sequencing assumed a simpler `union(C0)` would suffice. It doesn't.

## Falsification triggered — invoking handle-falsification protocol

Per Tenet 7 stop rule + sacred-patterns `handle-falsification` skill: this is variant 1 of `clip pattern to union(C0)`. Before authoring variant 2 (`union(C0, @0.0..9)`), the protocol says:

1. Reopen the cascade decision doc (`docs/decisions/2026-05-07-partial-shape-rendering-via-construction.md`) with falsification log.
2. Codify the witness (iter-20 composite drop) as a test or tracked task.
3. Introspect: is this L1 (impl bug), L2 (the clip primitive's mechanism), L3 (option set missing), or L4 (framing wrong)?
4. Web-search canonical `clip-and-extend` patterns.
5. Author new option(s).
6. Capture cross-repo memory.

Initial introspection: this looks like **L2** (option-letter level) — the clip primitive's mechanism is right but the cascade plan's `union(C0)` boundary specification was wrong for this pattern; the corrected boundary `union(C0, @0.0...9)` (or simply not-on-medallion-10) would be the right L2-corrected option.

But before rushing to L2-corrected iter-21, the loop priority should be: **rolling back iter-20** (iter-19 is the new floor), **documenting falsification**, **moving to a different on-path task** (per §F mechanical critical-path check) while the cascade decision doc gets its handle-falsification treatment.

## Rollback action

Iter-20 is documented but NOT promoted to baseline. Iter-19 (composite=0.8236) remains the medallion-10 ceiling. Next loop pickup is on a different critical-path task; the cascade #106 falsification protocol runs as a sub-task.

## Stop conditions evaluated

- composite drop > 0.02: **TRIGGERED** (-0.13)
- missing-shapes did not improve / regressed: **TRIGGERED** (32 → 39 sev=error)
- structural stays 0/18: **TRIGGERED**
- Render did succeed: not triggered

## Next directive (NOT iter-21 yet)

1. Switch to a different critical-path task (per autonomy/loop protocol — don't keep adding variants of a falsified option).
2. Schedule the cascade #106 falsification protocol as the next decision-doc work item.
3. Iter-21 waits for the corrected L2 option (probably `boundary outline = union(C0, @0.0, @0.1, ..., @0.9)`) to be authored via the falsification protocol.
