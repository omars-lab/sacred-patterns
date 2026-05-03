# Construction Anti-Patterns

General pitfalls applicable to ANY Islamic geometric pattern construction. Extracted from session-specific discoveries into reusable guidance.

Consult this at the start of every new session to avoid repeating known errors.

---

### Islamic patterns are TILINGS, not wireframes
- **Category:** structure
- **What happens:** Drawing geometric wireframes with overlaid lines instead of computing filled tile regions. Leaves large unfilled gaps.
- **Root cause:** Treating the pattern as "draw geometric shapes" rather than "compute a tile partition of the plane and color each tile."
- **Correction:** Islamic geometric patterns are fundamentally tilings. The colored regions are the primary visual content, and the white strapwork is just the borders between tiles.
- **How to avoid:** Always think "tiles first, strapwork second." Every pixel should belong to a colored tile.

### Don't use `var top` in browser global scope
- **Category:** code / JS
- **What happens:** Using `var top` in the browser global scope doesn't create a new variable because `window.top` is a read-only property. The assignment silently fails, producing `undefined` polygon coordinates.
- **Root cause:** Browser window properties like `top`, `left`, `right`, `parent`, `self`, `name`, `status`, `length` are read-only and cannot be overwritten with `var` in global scope.
- **Correction:** Use prefixed names: `rTop`, `pLeft`, `tRight`, etc.

### Polygon strokes double-count shared edges — use explicit band lines
- **Category:** architecture / strapwork
- **What happens:** Adjacent polygons with white stroke draw each shared edge TWICE. The apparent strapwork width is 2x the stroke-width value. Oscillating between "too thick" and "too thin" never converges.
- **Root cause:** ARCHITECTURAL problem — no parametric adjustment to stroke-width can fix double-counted edges.
- **Correction:** Draw ALL tiles with NO stroke. Draw ALL strapwork as explicit band lines on top. Each shared edge gets exactly ONE line.
- **Anti-pattern detection:** If you find yourself adjusting a parameter UP in one iteration and DOWN in the next, STOP. You are treating an architectural problem as a parametric one.

### Floating components — everything must connect to the network
- **Category:** architecture / connectivity
- **What happens:** Components built as independent geometric constructs (e.g., using `satPolarPt()`) appear visually near the main pattern but aren't connected to the edge network.
- **Root cause:** Constructing geometry independently rather than deriving it from the unified network.
- **Correction:** Every geometric element must be derived from or connected to the unified edge/strapwork network. For rosettes, the Lee/Adams proportioning circle [Pa] provides a principled derivation: satellites ARE the peripheral stars at polygon vertex [P], geometrically determined by the proportioning circle centered at P.
- **How to avoid:** After every blueprint render, check: "Can I trace a continuous path from the center to every satellite through the edge network?"
- **Note (Lee/Adams):** Satellite positions can come from the proportioning circle geometry (circle-based derivation), not only from line-line intersections. The key is that every element must be GEOMETRICALLY DETERMINED by the construction, not placed independently.

### Build networks in concentric layers, not as independent components
- **Category:** architecture / construction method
- **What happens:** Building the central star as one component and satellites as independent components, then trying to "connect" them. Produces inconsistent junction points.
- **Root cause:** Not thinking of the pattern as concentric layers radiating from a center point.
- **Correction:** Build outward from the center in layers: Layer 0 (center) -> Layer 1 (first radial ring) -> Layer 2 (interstitial connectors) -> Layer 3 (satellite centers) -> Layer 4 (satellite internals). Each layer's endpoints ARE the attachment points for the next layer.

### SVG extracted from D3 is not a valid standalone SVG file
- **Category:** artifact / SVG
- **What happens:** D3's `outerHTML` produces HTML-flavored SVG without the `xmlns` attribute. Browser renders it as text instead of an image.
- **Correction:** After extraction: (1) Add `xmlns="http://www.w3.org/2000/svg"` to the `<svg>` tag. (2) Validate the file starts with `<svg` and ends with `</svg>`. Always run `./tools/validate-svg.sh`.

### Reference SVG must be traced from the image, not hand-drawn
- **Category:** artifact / reference
- **What happens:** Creating a hand-drawn placeholder skeleton with `<text>` labels instead of a faithful trace.
- **Correction:** Use VTracer (`pip install vtracer`) to automatically trace the reference image into a colored SVG with `hierarchical='cutout'`, `color_precision=5`, `layer_difference=15`.

### Spatial coverage metrics don't measure structural fidelity
- **Category:** evaluation / metrics
- **What happens:** Pixel diff reports high "spatial coverage" but tile topology is fundamentally different. Two different tile topologies can have 95%+ overlap if they cover similar canvas regions.
- **Correction:** Always perform manual structural fidelity check alongside diff metrics. Never claim structural match based on diff numbers alone.

### Don't add construction line families without visual confirmation
- **Category:** structure / hypothesis testing
- **What happens:** Adding {10/3} diagonals to a {10/4} pattern produces 20 visible bands. Reference clearly shows only 10.
- **Correction:** ALWAYS count visible elements in the reference first. If the reference has N bands, any construction that produces 2N is wrong.

### Interstitial shapes are RESULTS, not designs (Lee/Adams principle)
- **Category:** architecture / interstitial
- **What happens:** Trying to independently design interstitial tile shapes by one of three wrong methods:
  1. **Eyeballed polar coordinates** — manually estimating vertex positions from the reference. Produces shapes that are approximately in the right zone but have wrong geometry.
  2. **Extended rosette scaling** — rendering the central rosette at a larger radius and clipping to the transition zone. Produces scaled copies of rosette tiles, not the correct interstitial shapes.
  3. **Line-LINE intersections** — computing intersections of band centerlines. In many patterns (e.g., {10/4}), adjacent-sector diagonals are PARALLEL in the interstitial zone, so no intersections exist there.
- **Root cause:** Treating interstitial tiles as shapes to be independently placed or derived from a single construction element (the central rosette). They actually EMERGE from the complete strapwork band network.
- **Correction:** Interstitial tiles are the **FACES of the planar graph** formed by strapwork band EDGES. Each band has two edges (centerline ± half-width perpendicular). Where edges from different bands cross, they create vertices. Connecting these vertices along the band edges creates face polygons — THESE are the tiles. Zoomed reference analysis confirms: every interstitial tile edge IS a strapwork band edge. Tile shapes are pentagons, rhombi, and star fragments — all bounded by band edges.
- **How to avoid:**
  1. Never eyeball tile vertices — derive them from the construction geometry
  2. Never assume interstitial tiles are scaled copies of rosette tiles — they have different geometry
  3. The correct construction: compute band edge-edge intersection points → connect into face polygons
- **Note (Lee/Adams):** This aligns with Lee's principle that interstitial tiles are "results of tiling interactions" — they emerge from the band network, not from independent placement.

### Color changes can't fix structural mismatch
- **Category:** evaluation / strategy
- **What happens:** Spending iterations on color corrections when the diff heatmap is uniformly red. Result: <0.5% improvement.
- **Correction:** A uniformly red heatmap means GLOBAL structural mismatch. Address structure first. Only do color corrections after structural improvements plateau.
- **Anti-pattern detection:** If "color match %" is low and the heatmap shows no localized hotspots, the issue is not color.

### VTracer reference SVG loses strapwork — always diff against original JPG too
- **Category:** evaluation / tooling
- **What happens:** VTracer traces tiles but NOT thick white strapwork bands. Wider bands penalized by VTracer metric even when they're closer to the original photo.
- **Correction:** Run dual-metric comparison: diff vs VTracer SVG (spatial structure) AND diff vs reference JPG (visual fidelity).
- **Anti-pattern detection:** If increasing band width makes VTracer diff worse but visual output looks closer to reference, the metric is wrong, not the change.

### Strapwork bands and interlace must be zone-clipped
- **Category:** architecture / clipping
- **What happens:** Strapwork diagonal lines extend infinitely along diagonals, painting over satellite interiors.
- **Correction:** Add a separate clip path at `satDist` radius. Satellites render their own internal strapwork independently.

### Breaking metric stagnation: test the OTHER direction
- **Category:** process / hypothesis
- **What happens:** 3+ parameter values tested in one direction, all regressing. Never tested the opposite direction.
- **Correction:** After testing 3 values in one direction with no improvement, MUST test the opposite direction. Trust the human eye over the metric.

### Color corrections must target large pixel areas to move metrics
- **Category:** evaluation / strategy
- **What happens:** Correcting a color that covers <2% of canvas pixels produces zero metric change.
- **Correction:** Before any color correction, estimate pixel area coverage. Rank by area: star kites (~15-20%) > background/void (~20%) > interstitial (~5-8%) > satellites (~5-8%) > individual small tiles (<2%).

### Star proportions matter more than tile topology
- **Category:** proportion
- **What happens:** Focusing on tile shapes while star is too small relative to satellites, creating an unfillable interstitial zone.
- **Correction:** Get proportions right FIRST (star radius, satellite distance, satellite size), then work on tile shapes.
