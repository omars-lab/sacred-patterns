# Weave approach — options research (2026-06-19, owner requested websearch + pros/cons)

**Plain English:** the owner said the field-Hankin contact-ray weave is "no better" twice (nodules,
then "weaves are no better"). Looking at the reference's weave in isolation, it's a CONTINUOUS network
of straight bands (star outlines at each tile linked edge-to-edge), not the localized rosette-blobs our
contact rays produce. The owner asked me to research how this is actually done and lay out the options
with pros/cons before pivoting. This note is that research.

## What the reference's weave actually IS (visual ground truth)
- `ref-weave-only.png`: a dense, continuous, uniform-width white band network — 10-pointed star
  outlines centered on every tile, connected by straight crossing bands running edge-to-edge across
  the WHOLE disc. No gaps, no detached blobs, genuine over/under at crossings.
- `flat-bare.png` (our structure, weave OFF): the thin white GAPS between colored tiles already trace
  essentially this same network. The reference dresses those boundaries as bold over/under straps.

## How Islamic strapwork is generated (literature — Hankin / Kaplan PIC + strapwork offset)
1. **Hankin "Polygons-In-Contact" (PIC), formalized Kaplan 2005** (cs.uwaterloo.ca kaplan_2005):
   lay a contact-polygon tiling; at each shared-edge midpoint spawn two rays into EACH adjacent polygon
   at contact angle θ; extend each ray until it meets a ray from a different edge of the SAME polygon;
   connect those pairs → star motif inside each polygon; the rays from adjacent polygons meet AT the
   shared midpoint, so motifs join across edges into ONE continuous network; erase the tiling. The
   network is continuous BECAUSE rays are TRIMMED at their meeting points (not left overshooting).
2. **Strapwork dressing (offset method — USPTO font-decoration patent describes the generic algo):**
   take the line network (the "director curves"); offset each line ±half-width to get band edges;
   subdivide all curves at intersection points; mark every 4th crossing-interval as hidden → that
   renders the alternating over/under. This is EXACTLY bikar's band-emitter (detectCrossings →
   assignStrands → emitStrandSegments), which already works.

**Key takeaway:** the weave is a LINE NETWORK dressed as bands. The reference's network = trimmed PIC
star lines (continuous), NOT untrimmed contact rays (blobs). bikar already has BOTH the trimmed
primitive (`hankinLines`) and the band-emitter; the field variant (`hankinContactRays`, untrimmed) is
the one producing blobs.

## The engine state (what bikar already has)
- `hankinLines(vertices, θ, δ)` — PROPER trimmed PIC: right-ray of edge i meets left-ray of edge i+1,
  TRIMMED at the meeting point → clean per-polygon star outline (connections.ts:90).
- `hankinContactRays(polygons, θ, rayLength)` — untrimmed overshooting rays meant to cross between
  tiles via the global graph (connections.ts:216). THIS is what the medallion field weave uses → blobs.
- Band-emitter (over/under at degree-4 nodes) — works, witnessed (`{8/3}`, basket-weave).

## OPTIONS (with pros/cons)

### Option A — Dress the existing TILE-BOUNDARY network as straps (my initial read)
Trace the tile edges (which already form the continuous field-spanning lattice visible in flat-bare)
and feed THAT graph to the band-emitter as wide white over/under straps.
- **Pros:** reuses the medallion's own geometry (zero new construction); the lattice provably spans the
  whole field already; deterministic; matches the reference's "boundaries-as-straps" look directly.
- **Cons:** tile boundaries meet at many degree-3/5/6 vertices (not clean degree-4 crossings), so
  over/under parity may not be well-defined everywhere — the band-emitter wants degree-4 crossings. May
  produce T-junctions the weaver can't cleanly interlace. Risk: straps that branch, not cross.

### Option B — Proper trimmed PIC star network (hankinLines across the field, not contact rays)
Use the EXISTING `hankinLines` (trimmed) on each wave's tiles instead of `hankinContactRays`
(untrimmed). Produces clean star outlines per tile that join across shared edges into the continuous
network the reference shows; dress with the band-emitter.
- **Pros:** this is the literature-canonical method (Kaplan PIC); the trimmed primitive ALREADY EXISTS
  and is tested; produces exactly the star-outline network the reference is; crossings are clean
  degree-4 (rays pair 2-at-a-time) so over/under is well-defined.
- **Cons:** need to recover per-tile polygons across the field (already solved for the field variant —
  reuse `recoverWavePolygons`); θ per wave may need tuning; gap polygons between tiles need the
  inference fill (Kaplan's hard part) or are left as background.

### Option C — Keep field-Hankin contact rays but TRIM at first crossing (the plan's flagged engine fix)
Add ray-trimming to `hankinContactRays` so rays stop at their first crossing instead of overshooting
into blobs.
- **Pros:** smallest delta from current code; keeps the field-wide cross-tile contact idea.
- **Cons:** trimming untrimmed field rays essentially re-derives PIC the hard way; still produces the
  contact-ray character (rosette-ish), not the clean star network; the owner has now rejected this
  family twice. Lowest confidence.

## RECOMMENDATION (for owner to decide)
**Option B** (proper trimmed PIC via the existing `hankinLines`) is the literature-canonical answer and
reuses an already-tested primitive — highest confidence of matching the reference's continuous star
network. Option A is a strong simpler alternative IF the tile-boundary graph weaves cleanly (degree-4
risk). Option C is the lowest-confidence continuation of the rejected direction.

Sources: Kaplan 2005 "Islamic Star Patterns from Polygons in Contact" (cs.uwaterloo.ca/~csk);
Bridges 2008 "Hankin's PIC Grid Method"; USPTO font-decoration patent (strapwork offset algo);
bikar docs/concepts.md "Hankin Method (Polygons in Contact) — Detailed".
