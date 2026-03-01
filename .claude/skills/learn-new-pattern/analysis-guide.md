# Analysis Guide

Instructions for analyzing a reference image of an Islamic geometric pattern. The analysis must produce a complete, machine-actionable description covering all visual dimensions of the art form.

## Before You Start

1. Read `learnings/common-mistakes.md` for known pitfalls
2. Read `learnings/patterns-catalog.md` for previously studied patterns that may share structural elements
3. Set aside assumptions — analyze what you actually see, not what you expect

## Analysis Template

Write the analysis as `analysis.md` in the session folder, covering every section below. Use precise numeric values where possible.

---

### 1. Symmetry Type

Identify the fundamental symmetry:

- **Rotational Order** — How many times does the pattern repeat around the center? (Common: 4, 6, 8, 10, 12, 16)
- **Dihedral Group** — State as D{n} (e.g., D8 for 8-fold symmetry with 8 mirror axes)
- **Mirror Axes** — How many, and at what angular intervals? (360/2n degrees apart for D{n})
- **Wallpaper Group** — If the pattern tiles periodically, identify the wallpaper group (p4m, p6m, cmm, etc.)
- **Fundamental Domain** — Describe the smallest region that generates the full pattern through symmetry operations

**Common mistakes:**
- Confusing 8-fold with 16-fold: count the distinct rotational positions, not total vertices
- Missing mirror symmetry: check both diagonal and axis-aligned mirrors
- Assuming rotational symmetry when only bilateral exists

### 2. Base Polygon & Star Pattern

Identify the primary geometric motifs:

- **Central Star** — State using {n/k} notation where n is the number of points and k is the step (connecting every k-th vertex). Example: {8/3} means 8 points, connecting every 3rd vertex
- **Secondary Stars** — List any satellite or surrounding stars with their {n/k} notation
- **Underlying Polygons** — What regular polygons form the construction grid? (octagon, hexagon, etc.)
- **Polygon Relationships** — How do the polygons relate? (inscribed, circumscribed, edge-sharing, vertex-sharing)

**How to determine {n/k}:**
1. Count the number of points (n)
2. For each point, trace the line to see which other point it connects to
3. Count how many vertices you skip (that number + 1 = k)
4. {8/2} produces an octagram (8-pointed with short points), {8/3} produces a deeper star

### 3. Tiling Method

Classify the overall composition:

- **Radial Rosette** — Single central motif radiating outward with concentric rings
- **Periodic Tiling** — Repeating unit cell across the plane (identify the repeat vectors)
- **Girih Tiling** — Uses the 5 girih tile shapes (decagon, pentagon, bowtie, rhombus, hexagon)
- **Hybrid** — Rosette center with periodic border, or multiple rosette centers in a grid

### 4. Construction Geometry

Define the radial structure using normalized radii (r0 = 1.0 for the pattern's primary circle):

```
r0 = 1.0    — primary construction circle
r1 = ???    — [describe what sits at this radius]
r2 = ???    — [describe what sits at this radius]
...
```

For each radius, note:
- What geometric element sits there (star vertices, polygon edges, rosette centers, band guides)
- The ratio to r0
- Whether it's a construction guide or a rendered element

**Angular divisions:**
- Primary angles (e.g., every 45 degrees for 8-fold)
- Secondary angles (e.g., every 22.5 degrees for bisected 8-fold)
- Any non-regular angular subdivisions

### 5. Tile Shapes & Angles

List every distinct tile shape in the pattern:

For each tile:
- Name/description (e.g., "elongated kite", "rhombus", "irregular pentagon")
- Number of sides
- Vertex angles (list all)
- Edge lengths (relative to r0)
- How many instances in one fundamental domain
- Symmetry of the tile itself

### 6. Interlace & Strapwork

This is a critical visual feature of Islamic geometric art. Analyze carefully:

- **Band Paths** — Where do the bands run? (concentric rings, radial spokes, spiral, following star edges)
- **Over-Under Pattern** — At each crossing, which band goes over? Describe the alternation rule
- **Band Width** — Uniform or varying? What fraction of the tile edge?
- **Crossing Density** — How many crossings in one fundamental domain?
- **Shadow/Depth Treatment** — How is depth conveyed at crossings? (shadow, color shift, gap, clip)
- **Band Color** — Same as background, contrasting, or gradient?

**If no interlace is visible**, explicitly state "No interlace/strapwork detected" — do not invent it.

### 7. Arabesque & Biomorphic Elements

Look for non-geometric organic forms:

- **Vegetal Scrollwork** — Vine paths, leaf shapes, palmette motifs, floral fills
- **Curvilinear Elements** — Bezier-like curves filling geometric voids
- **Integration** — How do organic forms relate to the geometric grid? (contained within tiles, overlaid, border-only)

**If none present**, state "No arabesque elements detected."

### 8. Calligraphic Zones

Identify areas reserved for or containing calligraphy:

- **Cartouche Locations** — Border panels, central medallion, corner pieces
- **Text-Geometry Boundary** — How does the geometric field meet the text zone?

**If none present**, state "No calligraphic zones detected."

### 9. Muqarnas Projections

If the pattern represents a 2D projection of 3D muqarnas (honeycomb vaulting):

- **Tier Structure** — How many tiers visible?
- **Nesting Pattern** — How do tiers relate geometrically?
- **Projection Method** — Top-down (plan view) or side view?

**If not applicable**, state "Not a muqarnas projection."

### 10. Color & Material

Extract the complete color language:

- **Color Palette** — List every distinct color with hex codes. Use a color picker approach: describe what you see, then assign the closest hex value
- **Color Distribution** — How are colors assigned? (radial gradient, zonal, per-tile-type, alternating)
- **Background Color** — The base/empty color
- **Stroke Color** — Line/outline color
- **Fill Rules** — What determines which tiles get which fills?
- **Material Cues** — Does the coloring suggest a physical material? (ceramic tile, carved plaster, painted wood, metalwork, stone inlay)
- **Opacity/Transparency** — Any translucent elements?

**Color palette format:**
```
Primary:    #hex — description (e.g., bright cyan, used for central star)
Secondary:  #hex — description
Accent:     #hex — description
Background: #hex — description
Stroke:     #hex — description
```

### 11. Programmatic Construction Steps

Write algorithmic pseudocode for constructing the entire pattern. This should be detailed enough to directly translate into code.

```
Step 1: Set up canvas (width, height, background color)
Step 2: Define center point and scale
Step 3: Compute construction radii (r0 through rN)
Step 4: [specific construction step]
...
Step N: Apply colors and styling
```

Each step should reference specific geometry primitives (Point, Circle, Polygon, Star, Line) and state exact parameters.

---

## Writing construction.md

After completing the analysis, write a normalized `construction.md` that distills the analysis into pure algorithmic steps. This file should:

1. Use only geometric operations (no subjective descriptions)
2. Reference normalized coordinates (center at origin, r0 = 1.0)
3. Be ordered for bottom-to-top rendering (background first, foreground last)
4. Specify exact parameters for every element
5. Note any elements that require library extensions not yet available

This file is the bridge between human-readable analysis and machine-executable pattern.json.
