---
name: learn-new-pattern
description: Analyze a reference image of an Islamic geometric pattern, iteratively replicate it using the sacred-patterns library, and produce D3.js, GeoGebra, and declarative pattern outputs.
user_invocable: true
argument: image_path - Path to a reference image (jpg/png) of a geometric pattern
---

# learn-new-pattern

Analyze a reference image of an Islamic geometric pattern, iteratively replicate it, extend the library as needed, and generate multiple output formats — with user feedback at each step.

## Invocation

```
/learn-new-pattern /path/to/image.jpg
```

The user provides just an image path. The skill handles everything else.

## Workflow

### Step 1: Initialize Session

1. Read the reference image at the provided path
2. Auto-generate a session name from initial visual impression (e.g., `8-fold-rosette`, `12-fold-medallion`) — or ask the user if ambiguous
3. Create session folder at `/Users/omareid/Dropbox/Data/sacred-patterns/session-{name}/`
4. Create the full directory structure:
   ```
   session-{name}/
     input/
       reference.{ext}
     analysis.md
     construction.md
     pattern.json
     iterations/
     final/
     dashboard.html
     session.json
     learnings.md
   ```
5. Copy the reference image to `input/reference.{ext}`
6. Initialize `session.json` with status `in-progress`
7. Load general construction learnings from `.claude/skills/generate-drawing/learnings/`:
   - `rosette-construction.md` — Lee/Adams traditional construction method
   - `construction-antipatterns.md` — common mistakes to avoid
   - `rabbit-hole-checklist.md` — early warning signs for wasted iterations
   - `construction-techniques.md` — reusable algorithms
   - `color-palettes-learned.md` — palettes discovered from reference images
   - `patterns-catalog.md` — catalog of studied patterns
8. Load session-specific learnings from `/Users/omareid/Dropbox/Data/sacred-patterns/learnings/` (iteration-log.md, common-mistakes.md full file with session-specific entries)

### Step 1.5: Pattern Interpretation

Collaborative shape review step. Claude's visual analysis becomes editable; the user corrects it; the result becomes the ground truth for architectural audits.

1. After initializing the session, Claude visually analyzes the reference image and generates a shape inventory (JSON array of detected shapes with type, zone, vertex count, count, approximate vertices)
2. Claude generates `input/pattern-interpretation.html` using the template in `.claude/skills/interpret-pattern/interpretation-tool-template.md` — reference image as background, SVG shape overlays, sidebar property editors
3. Open in browser for user review. The user:
   - Corrects shape properties (type, vertex count, zone, count)
   - Drags vertices to correct shape boundaries
   - Adds missed shapes, deletes incorrect ones
   - Writes per-shape notes and global feedback
   - Clicks "Done" when satisfied
4. Claude extracts corrected data from the DOM via `evaluate_script`:
   ```javascript
   () => {
     const el = document.getElementById('interpretation-data');
     return el ? JSON.parse(el.textContent) : null;
   }
   ```
5. Claude generates `input/baseline.json` from the extracted data (see `.claude/skills/interpret-pattern/baseline-schema.md` for schema)

**Gate:** Step 2 cannot begin until `input/baseline.json` exists. This ensures the user has reviewed and corrected Claude's interpretation before iteration work starts.

The baseline is used by `qiyas svg-audit --baseline input/baseline.json` (A6 audit, run via `tools/iteration-validate.sh`) to validate SVG output against expected shapes every iteration.

See `.claude/skills/interpret-pattern/SKILL.md` for the full skill definition.

### Step 2: Analyze Pattern

Follow the instructions in `analysis-guide.md` to analyze the reference image.

1. Examine the image carefully for all geometric, chromatic, and structural features
2. Write `analysis.md` covering:
   - Symmetry type and group
   - Base polygon and star pattern ({n/k} notation)
   - Tiling method
   - Construction geometry with normalized radii
   - Tile shapes and angles
   - Interlace/strapwork details
   - Color palette with hex codes
   - Programmatic construction steps
3. Write `construction.md` with normalized, algorithmic construction steps
4. Present the analysis to the user for review before proceeding
5. Consult `learnings/common-mistakes.md` to avoid known pitfalls

### Step 3: Generate Pattern Definition

1. Read `declarative-language-guide.md` for the pattern.json format
2. Translate the analysis into a `pattern.json` declarative definition
3. The definition should capture all layers of the pattern using available primitives
4. Save to the session root as `pattern.json`

### Step 4: Iteration Loop

Follow `iteration-guide.md` for the detailed iteration workflow.

#### Two-Phase Iteration: Understand First, Then Refine

**PHASE 1: Architectural Understanding (priority)**

The goal of early iterations is NOT to maximize visual similarity — it is to **fully decompose and understand the geometric construction** of the pattern. A high similarity score is meaningless if we don't understand WHY the output looks right (or wrong). Conversely, a low score with deep geometric understanding is excellent progress.

Phase 1 iterations focus on:
- Identifying ALL construction lines and their geometric relationships
- Understanding which tile shapes exist and what bounds them
- Discovering which shapes are negative space vs explicit tiles
- Proving geometric facts (intersection locations, parallel lines, symmetry properties)
- Documenting the decomposition in `discoveries.md` and updating the Pattern Decomposition Strategies in SKILL.md
- Testing decomposition strategies from the catalog (face decomposition, sector-first, kite-fan, etc.)

**Phase 1 is complete when:**
- Every region of the pattern has been accounted for (we know what creates each tile shape)
- All construction lines have been identified (not just the primary star diagonals)
- Open questions in `discoveries.md` about the fundamental geometry are resolved
- We can explain the pattern's construction in pure geometric terms

**PHASE 2: Similarity Refinement (only after Phase 1)**

Once the geometric decomposition is understood, iterate on visual fidelity:
- Color distribution matching
- Exact proportions and radii
- Interlace/over-under weaving
- Fine details (line widths, edge treatments)
- Per-element comparison against reference

**Do NOT jump to Phase 2 prematurely.** Tweaking colors or proportions when the underlying geometry is wrong wastes iterations. A correct decomposition with rough colors is always better than a wrong decomposition with perfect colors.

#### One Iteration = One Output

**CRITICAL**: Each iteration MUST be a single numbered folder (`iterations/44/`, `iterations/45/`, etc.) with ONE `output.html`, ONE screenshot, and ONE retrospective. Do NOT create sub-versions within an iteration (no v1, v2, v3 inside the same folder).

If your first attempt at an iteration produces output that needs changes:
- That first attempt IS the iteration — write its retrospective
- The changes become the NEXT iteration (new folder, new number)
- Each distinct architectural approach or rendering attempt = its own iteration number

**Do NOT overwrite `output.html` to try a different approach.** Once you render and screenshot an iteration, that folder is FROZEN for approach changes. A new geometric approach, tile construction method, or rendering strategy = new iteration folder.

**Overwriting IS allowed ONLY** when the output has JavaScript/console errors that prevent rendering. If the page is blank or throws errors, fix the JS bug in place and re-render. Once the output renders successfully (no console errors, visible output), the file is frozen — any further changes are a new iteration.

**Enforcement checklist** (before writing `output.html`):
1. Does `iterations/{N}/output.html` already exist? If YES → is this a small bug fix (syntax, typo)? If NO → create `iterations/{N+1}/` instead
2. Did the geometric approach, tile construction, or rendering strategy change? If YES → new iteration folder
3. Did you already write a retrospective for this iteration? If YES → next iteration

**Why this matters**: The iteration numbering is the session's historical record. Sub-versions lose discoverability, make it harder to trace what changed, and break the "one retrospective per attempt" pattern. If iteration 50 tried crossing-band subdivision and iteration 51 tried circle-bounded tiles, that's clear. If both are buried as overwrites of iteration 50, the first approach is lost forever.

**Exception**: Minor typo/bug fixes that don't change the approach (e.g., fixing a syntax error that prevented rendering) can be fixed in-place without a new iteration number. But any change to the geometric approach, tile construction method, or rendering strategy = new iteration.

#### Iteration Steps

**a) Compile** — Translate `pattern.json` to a self-contained D3.js v7 HTML file following `compile-d3.md`

**b) Render & Capture** — Open HTML in browser, verify render (check console for errors), take screenshot. See iteration-guide.md for Chrome DevTools debugging workflow.

**c) Evaluate** — Compare screenshot to reference on structured criteria:
- **Decomposition completeness** (Phase 1): Are all regions accounted for? Any unexplained gaps or shapes?
- Scale calibration: verify the overall pattern fills the same proportion of the canvas as the reference (check this FIRST — wrong scale makes all other comparisons misleading)
- Symmetry order match
- Element count (stars, polygons, rosettes)
- Radial proportions
- Interlace/strapwork
- Color palette accuracy (Phase 2 priority)
- Each scored: MISSING / PARTIAL / PRESENT / ACCURATE

**d) Deep Retrospect** — The most critical step. For EVERY difference (not just MISSING/PARTIAL):
- Place the reference and screenshot side-by-side mentally
- Identify every structural, geometric, and chromatic difference
- For each difference, ask: "What fundamental pattern or construction principle am I missing?"
- Don't accept surface-level explanations — dig into the root geometric cause
- Challenge your own analysis: is the analysis.md actually correct, or did it miss something?
- Re-examine the reference image with fresh eyes — what do you see NOW that you didn't before?
- **Negative space analysis**: Some shapes in Islamic patterns aren't explicitly drawn — they emerge from the VOID between other shapes. Ask: "Could this shape be the background showing through gaps in overlapping layers?" If so, you don't draw it as a tile — you leave a gap and let the background color define the shape.
- **Decomposition strategy review**: Which strategy from the catalog applies to the unresolved regions? Should a new strategy be added?
- Update `analysis.md` and `construction.md` with corrections
- Record in `iterations/{nn}/retrospective.md`

**e) Update Discoveries** — Maintain `discoveries.md` at the session level (copied into each iteration folder). This is a running document tracking:
- **Confirmed facts** — Things we KNOW about the pattern (proven by analysis or confirmed by output matching)
- **Working assumptions** — Things we BELIEVE but haven't fully confirmed
- **Disproven assumptions** — Things we THOUGHT were true but discovered were wrong (with the iteration that disproved them)
- **Open questions** — Things we DON'T KNOW yet and need to investigate
- **Negative space shapes** — Shapes that appear to be formed by voids between other shapes rather than being explicitly drawn

Every iteration should update this document. New discoveries get added, confirmed assumptions move to "confirmed facts", wrong assumptions move to "disproven". This creates a growing understanding of the pattern that survives context resets and guides future iterations.

**f) Update Decomposition Strategies** — If this iteration discovered a new strategy, validated an existing one, or revealed limitations, update the Pattern Decomposition Strategies section in SKILL.md. This knowledge persists across sessions.

**g) Update** — Apply corrections to `pattern.json`

**h) Library Check** — If a primitive is missing, follow `library-extension-guide.md` to auto-create it, run `make compile`, and document in `iterations/{nn}/library-changes.md`

**i) Declarative Language Review** — Document what new constructs the declarative language would need to express this pattern. Write `iterations/{nn}/language-gaps.md`. This builds toward being able to replicate patterns purely from `pattern.json` in future sessions.

**j) Task Tracking** — When entering the iteration loop, create sub-tasks for each iteration and for skill enhancements discovered during the process. This gives the user clear progress visibility.

**k) Process Feedback Check** — Every 3rd iteration, scan for process inefficiencies (repeated approaches, root cause changes, coverage stalls, missing artifacts) and proactively suggest improvements to the user via `AskUserQuestion`. See `iteration-guide.md` Section N for the full trigger table and protocol.

**k) Decide**:
- **Phase 1**: Decomposition is incomplete → iterate with focus on understanding geometry
- **Phase 1 → Phase 2 transition**: Decomposition is complete, all regions accounted for → switch to similarity refinement
- **Phase 2**: Output is a near-identical derivative → **complete**
- **Phase 2**: Meaningful visual differences remain → iterate with corrections
- Convergence has stalled (3+ iterations with <0.03 improvement) → **ask user** for guidance on what to prioritize
- The confidence score tracks progress but is NOT used as a stop condition, especially in Phase 1

### Step 5: Finalize

1. Copy best iteration to `final/`:
   - `pattern.json` — final declarative definition
   - `output.html` — self-contained D3.js HTML
   - `output.svg` — extracted SVG
2. Generate GeoGebra outputs following `geogebra-guide.md`:
   - `pattern.ggb` — GeoGebra archive
   - `geogebra-script.txt` — paste-in script
3. Generate `dashboard.html` following `dashboard-guide.md`
4. Update `session.json` with final status, confidence, etc.
5. Update `learnings.md` with session-specific insights
6. Auto-generate marketing content:
   a) Assemble timelapse GIF from iteration screenshots (`magick convert`)
   b) Assemble timelapse MP4 for social media (`ffmpeg`)
   c) Generate social media post copy from session metadata
   d) Include timelapse and social copy in `dashboard.html`
   See `.claude/skills/creative-generation/` for details.

### Step 6: Deploy

1. Update general construction learnings in `.claude/skills/generate-drawing/learnings/` (git-tracked):
   - Add general anti-patterns to `construction-antipatterns.md`
   - Add reusable techniques to `construction-techniques.md`
   - Add discovered palettes to `color-palettes-learned.md`
   - Add to `patterns-catalog.md`
   - Update `rosette-construction.md` if new construction insights apply to all patterns
2. Update session-specific learnings in `/Users/omareid/Dropbox/Data/sacred-patterns/learnings/`:
   - Add session-specific mistakes to `common-mistakes.md`
   - Log any library extensions in `library-extensions-log.md`
2. If user approves, run gallery build and `make deploy`

### Step 7: Present Results

1. Show the final output alongside the reference image
2. Provide file paths to all outputs
3. Show iteration journey (how many iterations, what was corrected)
4. Collect user feedback
5. If feedback requires changes, return to Step 4

## Geometric Construction Principles

### Sector-First Construction

**The most reliable way to build a radially symmetric pattern:**

1. **Identify the fundamental sector** — For an n-fold pattern, one sector spans `360/n` degrees (e.g., 36 degrees for n=10). This sector contains ALL the geometric information needed.

2. **Build ONE sector completely** — Place every element in a single sector: star kite slice, interstitial tiles, strapwork lines, rosette fragments. Get the shapes, proportions, and colors exactly right for this one sector.

3. **Rotate and repeat** — Use `radial-repeat` (or a rotation transform) to duplicate the sector `n` times around the center. Every element in the final pattern is a rotated copy of something in the fundamental sector.

**Why this works better than drawing each element independently:**
- You only need to get ONE sector right — debugging is 10x easier
- No alignment issues between independently drawn elements
- Guarantees perfect symmetry (every sector is identical by construction)
- Partial shapes at sector boundaries (half-hexagons, truncated kites) are naturally handled by overlap between adjacent sectors

**When analyzing a reference**, always identify the fundamental sector first. Ask: "What is the minimal wedge that, when rotated n times, produces the full pattern?" Then list every element inside that wedge.

### Proportions from Trigonometry

All proportions must be derived from trigonometric relationships relative to a central circle -- never from arbitrary scaling factors like `R * 0.52`.

**Central origin construction:** Every coordinate is computed from the center point `(cx, cy)` using polar coordinates `(r, theta)` where `r` is derived from a geometric relationship and `theta` from `360/n` divisions.

**Deriving radii (instead of guessing them):**
- **Star outer radius** = circumscribed circle radius `R`
- **Star mid-ring radius** = computed from the intersection of adjacent {n/k} star polygon edges (use the line-line intersection formula with the known tip angles)
- **Star inner radius** = derived from the mid-ring intersection with the next edge pair
- **Satellite distance** = star tip radius + strapwork band width + satellite radius (each term derived from geometry, not eyeballed)
- **Satellite radius** = determined by the space between adjacent satellite centers (which are at `2*pi/n` angular intervals at the satellite distance)

**Deriving angles:**
- All angular positions from `i * 360/n` for n-fold symmetry
- Star point half-angle from `pi*k/n` for a {n/k} star polygon
- Kite and rhombus vertex angles from the star construction geometry

**Anti-pattern:** `starOuter = R * 0.52`, `satDist = R * 0.58`, `rMid = R * 0.625`. These magic numbers obscure the geometry and make debugging impossible. Instead, compute each value from the geometric relationship that produces it.

**Alternative derivation (Lee/Adams proportioning circle):** For rosette patterns, a single proportioning circle [Pa] centered at polygon vertex P can derive all key proportions. The relationship [a1-P] = [P-b] gives both the outer circle [oa] and inner circle [ob] from one construction. Three circles ([oa], [ob], [Pa]) completely define all rosette proportions. This is potentially simpler than deriving each ratio independently from star polygon edge intersections.

### Relative-to-Origin Scaling

**Core tenet:** Every coordinate, distance, and size MUST be defined as a ratio or function of the originating circle's midpoint `(cx, cy)` and radius `R`. When `R` changes, the entire diagram scales proportionally.

**How the landing page does it** (`drawHexagonWithSurroundingNonagons`):
- Central circle `(cx, cy, R)` defines everything
- Surrounding circles placed at distance `R` from center, each with radius `R`
- Nonagons sized at `0.75 * R` — a ratio, not an absolute
- Tiling outward: each new hexagon becomes a new origin, same ratios apply

**In iteration code, this means:**
- `satDist = R * cos(pi*k/n) + bandW + satR` — each term derived from `R`
- `bandW = R * someRatio` — not a standalone `0.025`
- Tile vertices: `(cx + r * cos(theta), cy + r * sin(theta))` — always relative to center
- When debugging, you can change `R` and everything should rescale correctly

### Curved Lines as Circles

**Rule:** Whenever a curved line appears in a reference pattern, it is almost certainly an arc of a circle. Determine which circle, and how that circle relates back to the primary construction circle.

**Protocol when you see a curve:**
1. **Identify the circle** — Every curve in Islamic geometric art is an arc of a circle. Find its center point and radius. The center is usually one of: the pattern center, a satellite center, a star tip, or an intersection point.
2. **Relate to the primary circle** — Express the curve's radius and center as functions of `R`, `n`, and `k`. Common relationships:
   - `r = R` (same circle, just a partial arc)
   - `r = R * cos(pi*k/n)` (mid-ring circle)
   - `r = satR` (satellite circle)
   - `r = satDist` (satellite orbit circle)
   - `r = satDist + satR` or `r = satDist - satR` (satellite tangent circles)
3. **Draw through the circle** — Don't approximate curves with Bezier paths or freehand arcs. Use `d3.arc()` or parametric `(cx + r*cos(t), cy + r*sin(t))` to draw exact circular arcs.
4. **Check tangency** — Curves in Islamic patterns often arise from circles tangent to construction lines or other circles. If the curve seems to "kiss" a straight line, it's tangent to that line. Find the tangent point.

**Why this matters:** Freehand curves or Bezier approximations create subtle asymmetries that compound across the pattern. Exact circular arcs maintain the pattern's mathematical precision. Every curve has a geometric origin — find it.

**Anti-pattern:** Drawing a curve with `path d="M... Q... T..."` (quadratic/cubic Bezier) when the shape is actually a circular arc. Bezier curves are not circles — they approximate them poorly, especially at larger arc angles.

### Reference Image Tracing (VTracer)

**Rule:** Every session must produce a proper `input/reference-traced.svg` by tracing the reference image — not a hand-drawn skeleton.

**Tool:** [VTracer](https://github.com/visioncortex/vtracer) via Python (`pip install vtracer`). It traces color bitmap images into multi-color SVGs with distinct tile regions.

**Standard procedure:**
```bash
# 1. Convert JPG to PNG (avoids JPEG compression artifacts)
magick input/reference.jpg -quality 100 /tmp/reference-clean.png

# 2. Trace with vtracer
python3 -c "
import vtracer
vtracer.convert_image_to_svg_py(
    '/tmp/reference-clean.png', 'input/reference-traced.svg',
    colormode='color', hierarchical='cutout',
    filter_speckle=4, color_precision=5,
    layer_difference=15, corner_threshold=60, mode='spline'
)"

# 3. Validate
./tools/validate-svg.sh input/reference-traced.svg
```

**Key parameters for geometric patterns:**
- `hierarchical='cutout'` — non-overlapping tile regions (essential for comparison)
- `color_precision=5` — fewer color bins, cleaner tile boundaries
- `layer_difference=15` — merge similar colors into distinct tiles
- `filter_speckle=4` — remove noise patches
- `mode='spline'` — smooth Bezier curves for geometric edges

**Anti-pattern:** Creating a hand-drawn placeholder SVG with `<text>` and `<circle>` markers instead of actually tracing the image. The reference SVG must faithfully reproduce the reference image's shapes, colors, and tile boundaries.

## Pattern Decomposition Strategies

A catalog of strategies for breaking down a reference pattern into renderable components. Each strategy has different strengths. During the iteration loop, evaluate which strategies apply and document what works in `discoveries.md`.

### Strategy 1: Planar Face Decomposition

**What**: Compute ALL polygonal faces created by the intersection of construction lines within a bounding region. Color each face based on position.

**How**: Build a planar graph from all line segments and their intersection points. Use half-edge traversal to trace each face. The number of faces follows Euler's formula: V - E + F = 2.

**When to use**: When the pattern is primarily defined by a set of intersecting straight lines (e.g., {n/k} star polygon diagonals), and you want to color every cell they create.

**Limitations**: Only finds faces INSIDE the line network. Unbounded outer faces require a clip boundary as additional edges. The number of faces is limited by the number of lines — 10 lines in general position create at most 56 regions, but with symmetry the count is lower. For a {10/4} pattern, 10 lines create only ~31 inner faces. This may be insufficient for patterns with dense tiling in zones where lines don't intersect.

**Key insight from session-1**: In a {10/4} star polygon, ALL diagonal intersections occur at exactly 4 concentric radii inside the star (none in the interstitial zone). Adjacent-sector diagonals extending into the same gap are PARALLEL — they never cross outside the star. Face decomposition works well for the central star but cannot help with interstitial tiles.

### Strategy 2: Sector-First Construction

**What**: Build one fundamental sector (360/n degrees for n-fold symmetry), then rotate it n times.

**How**: Identify every geometric element within a single sector wedge. Construct each element using polar coordinates from the center. Apply a rotation transform to replicate the sector.

**When to use**: Any pattern with rotational symmetry. Most reliable approach for radial medallions.

**Strengths**: Only need to get one sector right. Guarantees perfect symmetry. Partial shapes at sector boundaries are handled by overlap.

**Considerations**: The "fundamental sector" might be half a sector (using mirror symmetry too, reducing work further). Some elements span multiple sectors — decide whether to split them or draw complete and let overlap handle it.

### Strategy 3: Per-Tip Kite Fan

**What**: For each star tip, trace the fan of tile shapes extending outward along the two diagonals passing through that tip.

**How**: For a star tip at angle `s * 360/n`, identify the 2 diagonals through it. Find intersection points along each diagonal (sorted by distance from tip). Construct tiles between consecutive intersection points: the main kite (tip → int1_A → peak → int1_B), side triangles, outer triangles, and cross-peak quads.

**When to use**: For the interstitial zone of star-and-satellite patterns where face decomposition can't reach. Each tip generates a fan of tiles between its two diagonals.

**Limitation**: Only covers the region directly traceable from the tip's diagonals. The gap BETWEEN adjacent tip fans (the "inter-sector gap") needs separate treatment.

### Strategy 4: Inter-Sector Gap Fill

**What**: Fill the region between two adjacent kite fans with explicit tile shapes.

**How**: Identify the outermost intersection points from each adjacent tip's diagonal fan. Find where the "other lines" at those points intersect. Construct triangles, quads, and pentagons to fill the gap.

**When to use**: After per-tip kite fans leave gaps between sectors.

**Key geometric fact**: In a {10/4} pattern, the two diagonals extending from adjacent tips into the same sector gap are PARALLEL. The inter-sector gap is a parallelogram-shaped channel. Tiles within it must be bounded by lines from non-adjacent sectors or by explicit construction.

**Lee/Adams context**: Lee's minimal triangle approach provides theoretical foundation for this zone. For 10-fold patterns, TWO triangles are needed: [o-h-o'] contains the rosette proper, and [h-CR-o'] contains the tiling interaction zone (interstitial). The second triangle is governed by different geometric rules than the rosette triangle — this explains why interstitial tile construction is fundamentally harder.

### Strategy 5: Negative Space (Background Shows Through)

**What**: Some shapes in the pattern are NOT explicitly drawn tiles — they are the dark background visible through gaps between colored tiles and strapwork bands.

**How**: Set a dark background as the base layer. Draw colored tiles and white strapwork on top. Dark shapes appear automatically where no tile covers the background.

**When to use**: For dark navy dart/star shapes between white strapwork bands. Also for the dark central void of the star. If a shape is dark and has irregular boundaries matching the gaps between bands, it's likely negative space.

**Diagnostic test**: Temporarily change the background color (e.g., to red). If the shape changes color too, it's negative space. If it stays dark navy, it's an explicit tile.

### Strategy 6: Satellite-as-Overlay vs Satellite-as-Emergent

**What**: Two models for how satellite rosettes relate to the strapwork.

**Model A (Overlay)**: Satellites are opaque decagonal bodies drawn ON TOP of the strapwork, masking the diagonal bands where they pass through.

**Model B (Emergent)**: Satellites are NOT separate overlays. The diagonal bands pass THROUGH the satellite region. The satellite's dark body is just a region where many intersection-created faces are colored dark navy, creating the visual impression of a dark body. The "separation lines" are the incoming diagonal bands continuing through.

**How to determine which model**: Look carefully at the reference. If white strapwork bands appear to stop at the satellite edge and resume on the other side, it's Model A. If bands visibly pass through the satellite as continuous lines, it's Model B.

**Session-1 finding**: This pattern uses a HYBRID — the strapwork passes through (Model B), but the satellite also has its own internal radial separation lines that are NOT continuations of the diagonals. The internal structure is rendered separately from the strapwork network.

### Strategy 7: Additional Construction Lines

**What**: When the primary line network (e.g., 10 {10/4} diagonals) doesn't create enough intersections to define all tiles, add supplementary construction lines.

**Candidates**:
- Lines from satellite decagon vertices to star mid-ring points
- {n/k'} secondary star polygon diagonals (different skip value k')
- Lines along satellite decagon edges
- Radial lines from center through satellite centers
- Star kite boundary edges extended past the tips

**When to use**: When face decomposition or per-tip tile tracing leaves unfilled zones that the reference clearly fills with tiles. The additional lines create new intersection points in those zones.

**Status**: The traditional construction (per Brewer tutorial) DOES use additional lines (rectangle frame + 20-fold divisions). But computationally, Strategy 9 (Per-Sector Explicit Tile Construction) achieves the same result without additional lines.

### Strategy 8: Layered Rendering Order

**What**: Render the pattern in specific layer order to achieve correct visual stacking.

**Typical order (back to front)**:
1. Dark background (fills entire clip region)
2. Colored tile fills (interstitial kites, rhombi, pentagons)
3. Satellite interior tiles
4. Central star tiles (on top of interstitial)
5. White strapwork bands (on top of everything)
6. Satellite separation lines
7. Satellite outlines

**Why order matters**: The strapwork must be on top of all colored tiles. The central star tiles must cover the inner portions of interstitial tiles. Satellite details must be drawn after the satellite body.

### Strategy 9: Per-Sector Explicit Tile Construction

**What**: When line-based face decomposition fails (zero intersections in a zone), construct tiles explicitly by computing where band edges cross zone boundaries.

**How**: For each sector gap between adjacent star tips:
1. Identify the two diagonal bands that enter this gap from the adjacent tips
2. Compute each band's L/R edge lines (offset from center-line by half-band-width)
3. Find where each edge line crosses the inner boundary (star circle) and outer boundary (satellite circle)
4. Build quadrilateral tiles from these crossing points:
   - "Petal" tile: between the two edges of each band (inner edge to outer edge)
   - "Wing" tile: between the outer edge of one band and the outer edge of the adjacent sector's band
5. The dark dart between the two parallel bands' inner edges = negative space (no tile needed)

**When to use**: When face decomposition finds zero intersections in a zone because the construction lines there are parallel. This is the case for {10/4} patterns where adjacent-sector diagonals are offset by 5 (parallel).

**Strengths**: Bypasses the line-intersection requirement entirely. Uses line-circle intersections instead. Achieves ~90% interstitial coverage. Conceptually simple — each band is a "corridor" and tiles are the walls of that corridor.

**Validated**: Session-1 iter 44 v3. Produced ~40 interstitial tiles across 10 sectors, filling the zone that face decomposition couldn't reach.

**Lee/Adams validation**: This approach aligns with the Lee/Adams principle that interstitial shapes emerge from extending pattern lines to tiling boundaries. The corridor approach uses line-CIRCLE intersections (with satellite boundary circles), which IS the correct geometric mechanism. Lee confirms that interstitial tiles are "results of tiling interactions" — they emerge from line extensions, not independent construction. Potential refinement: hexagonal petals in the interstitial zone should be congruent to the rosette's own petals (a checkable criterion).

### Strategy 10: Band-Edge Face Decomposition

**What**: Instead of using single center-lines for face decomposition, use the L/R edge lines of each band (20 lines instead of 10 for a 10-fold pattern).

**How**: Offset each construction line perpendicular to its direction by ±halfBandWidth. This produces 2× the number of lines. Intersect all non-parallel pairs. Build the half-edge structure and traverse faces.

**When to use**: For the central star zone where lines DO intersect. The 20 edge lines create ~160 nodes and ~141 faces (vs 40 nodes and 31 faces with 10 center-lines). The face decomposition now captures the tile geometry INCLUDING the white band faces as explicit polygons.

**Limitation**: Still fails in zones where the underlying center-lines are parallel (the edge offsets are also parallel). Use Strategy 9 for those zones.

**Validated**: Session-1 iter 44 v1. Correctly found 81 tile faces and 60 band faces in the central star. All in the inner zone (r < R), none in the interstitial zone.

### Strategy 11: Computational Pre-Analysis

**What**: Before the first iteration, use the interactive analysis tools in `tools/analysis/` to compute the geometric framework, identify all intersection points, parallel pairs, and tile shapes.

**How**: Open each analysis tool as a `file:///` URL with the pattern's parameters. The tools compute and visualize:
- Star intersection map: all diagonal intersections and concentric radii
- Sector decomposition: which diags enter each gap, parallel status, separation distances
- Tile decomposition: exact tile vertices for one fundamental sector
- Construction overlay: all layers combined with toggleable visibility

**When to use**: At the START of every new session, before writing any iteration code. The pre-analysis reveals which decomposition strategies will work and provides ground-truth vertex coordinates.

**Strengths**: Prevents wasted iterations by revealing parallel pairs (which break face decomposition), computing exact radii (eliminating magic-number guessing), and identifying all tile shapes upfront.

**Reference**: See `tools/analysis/README.md` for parameters, workflow, and function reference. See `iteration-guide.md` "Geometric Pre-Analysis" section for the step-by-step protocol.

### Strategy 12: Compositional Placement

**What**: Instead of computing tile shapes from line intersections, PLACE known geometric shapes at positions derived from circle geometry. Each shape's position and size is a ratio of the originating circle's radius `R`.

**How**: Inspired by the landing page's `drawHexagonWithSurroundingNonagons`:
1. Start with the central shape (star polygon inscribed in circle `R`)
2. Compute surrounding positions using `surroundingCircles(n, distance_ratio)` — circles at angular intervals around center
3. Place known tile shapes (kites, rhombi, pentagons, hexagons) at each position, sized as ratios of `R`
4. Fill interstitial zones by placing shapes at positions computed from the gap geometry, not by intersecting lines

**When to use**: When intersection-based approaches fail — particularly when construction lines are PARALLEL in the interstitial zone (no intersections to derive tiles from). Also useful when you know what tile shapes should appear but need to compute their positions.

**Strengths**: Bypasses the parallel-lines problem. Every shape is placed explicitly, making debugging straightforward. Guarantees coverage (you decide where shapes go, rather than hoping intersections create them). Scales naturally with `R`.

**Weakness**: Requires knowing the tile shapes in advance (from reference analysis or pre-analysis tools). Less "automatic" than face decomposition.

## Session Isolation Rules

- Each session is fully self-contained — it NEVER reads from other session folders
- The only shared state is `learnings/` which is read at startup
- The skill does NOT compare against other sessions' outputs unless explicitly asked
- Combining patterns from multiple sessions requires explicit user request

## Session Folder Structure

```
session-{name}/
  input/                        # User-provided reference material
    reference.{jpg,png}         # Primary reference image
    notes.md                    # Optional user notes
  analysis.md                   # Pattern analysis (updated by retrospective loop)
  construction.md               # Normalized construction steps
  pattern.json                  # Declarative pattern definition (canonical)
  discoveries.md                # Running list of confirmed facts, assumptions, and open questions
  iterations/
    01/
      pattern.json              # Pattern definition for this iteration
      output.html               # Self-contained D3.js v7 HTML
      screenshot.png            # Browser screenshot of output
      evaluation.md             # Structured comparison vs reference
      retrospective.md          # WHY did analysis lead to wrong output?
      discoveries.md            # Updated snapshot of discoveries — what we know, assume, and question
      guidance.md               # What to change next
      library-changes.md        # Any TS library changes
    02/ ...
  final/
    pattern.json                # Final declarative definition
    output.html                 # Best iteration's HTML (self-contained)
    output.svg                  # Exported SVG
    pattern.ggb                 # GeoGebra archive
    geogebra-script.txt         # GeoGebra Classic paste-in script
  dashboard.html                # Self-contained session journey visualization
  session.json                  # Machine-readable session metadata
  learnings.md                  # Session-specific learnings
```

## session.json Schema

```json
{
  "name": "session-name",
  "status": "in-progress | completed | paused",
  "created": "ISO-8601 timestamp",
  "updated": "ISO-8601 timestamp",
  "pattern_type": "rosette | medallion | tessellation | ...",
  "symmetry_group": "D8 | D12 | ...",
  "symmetry_order": 8,
  "current_iteration": 1,
  "best_iteration": 1,
  "confidence_score": 0.0,
  "library_extensions": [],
  "color_palette": {
    "name": "palette name",
    "colors": {}
  },
  "tags": [],
  "reference_image": "input/reference.jpg"
}
```

## Guide Files

All guide files are in this skill directory:

| File | Purpose |
|------|---------|
| `analysis-guide.md` | How to analyze a reference image |
| `color-palettes.md` | Traditional Islamic art color palettes |
| `declarative-language-guide.md` | Pattern.json format and layer types |
| `compile-d3.md` | How to compile pattern.json to D3.js HTML |
| `compile-geogebra.md` | How to compile pattern.json to GeoGebra |
| `iteration-guide.md` | Core iteration workflow with retrospective loop |
| `library-extension-guide.md` | When/how to extend src/ts/ |
| `geogebra-guide.md` | GeoGebra script + .ggb generation |
| `dashboard-guide.md` | Per-session dashboard and gallery generation |
| `../../tools/analysis/README.md` | Geometric analysis tools — usage, parameters, workflow |
| `../../tools/analysis/svg-census.html` | Extract tile census (polygon counts, areas, colors) from iteration SVG |
| `../../tools/analysis/svg-diff.html` | Compare two SVGs at tile level with centroid matching |
| `../../tools/validate-svg.sh` | SVG structural validation (xmlns, XML, visual elements, wrapper detection) |
| `qiyas pixel-diff` (Docker) | Pixel-based image diff — visual overlay, heatmap, similarity score (called by orchestrator) |
| `qiyas zone-audit` (Docker) | Per-zone radial diff — concentric rings, named zones, strapwork gap analysis |

## Related Skills

- `/interpret-pattern` — Interactive pattern interpretation and baseline generation (Step 1.5)
- `/analyze-geometric-patterns` — Standalone image analysis (no iteration)
- `/generate-drawing` — Creative pattern composition from learned primitives
- `/creative-generation` — Auto-generate timelapse GIF, MP4, and social media copy
