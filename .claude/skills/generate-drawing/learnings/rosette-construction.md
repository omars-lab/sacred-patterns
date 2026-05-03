# Rosette Construction Method (Lee/Adams)

Source: "Drawing the Rosette of Islamic Geometric Art. Part 1: The Basic Structure" by Alan Adams, based on Anthony J Lee's explorations (1960s-1987). Saved locally at `learning-material/Drawing the Rosette...mhtml`.

This documents the traditional compass-and-straightedge construction method for Islamic rosette patterns. These principles apply as general drawing guidance — not all will apply to every pattern, but they contain key techniques to consider.

---

## Core Principle: Three Circles Define Everything

Almost all historical rosettes share the same system of proportions. A single **critical proportioning circle** at point [P] determines the entire rosette structure through three concentric circles:

1. **Circle [oa]** — The master circle (circumcircle) of the rosette. Defines the outer boundary.
2. **Circle [ob]** — The inner star polygon circle. Defines where the central star tips reach.
3. **Circle [oc]** — The star polygon layout circle (used for tapered rosettes; coincides with [ob] for parallel).

These circles are derived from the proportioning circle [Pa] centered at point P (a vertex of the limiting polygon). The only free artistic choice is how the petals taper — everything else follows from the geometry.

## Nomenclature (Lee's Labels)

Understanding the naming system is essential for reading construction literature:

- **[o]** — Center of the rosette
- **[P]** — Vertex of the limiting polygon (decagon for 10-fold). Also the center of peripheral stars.
- **[a]** — Points on the outer circle [oa]. Defines the rosette boundary.
- **[b]** — Points on the inner circle [ob]. Defines the central star polygon.
- **[c]** — Points on the second star polygon circle (for tapered rosettes).
- **[d]** — Points on the incircle of the star polygon.
- **[g]** — Point on the bisector of the angle at P. Controls petal taper vs. parallel.
- **R** — A radius of the rosette (line from center to the 2n-division of the circle).
- **I-R** — An inter-radius (halfway between two radii).
- **[CR]** — Center of the rhombus tile (used in minimal triangle analysis).

### Circles
- **[oP]** — Radius of the limiting polygon (circumscribing decagon).
- **[Pa]** — The critical proportioning circle. Centered at P with radius P-to-a.
- **[oa]** — Circumcircle of the rosette.
- **[ob]** — Layout circle for the first central star polygon.
- **[oc]** — Layout circle for the center star polygon.
- **[od]** — Incircle of the center star polygon.

## Rosette Structure: Three Concentric Zones

A rosette (Lee's definition) has this layered structure:

1. **Central star polygon** — The innermost shape. A {n/k} star polygon (e.g., {10/3} or {10/4}).
2. **Kites/Almonds** — Surround the star. Called "almond" or "turanj" (bergamot) in Persian.
3. **Hexagonal petals** — The outermost ring of the rosette proper. Elongated hexagons.

The rosette has strict rotational symmetry equal to n (the number of arms).

## Parallel vs. Tapered Rosettes

The ONLY difference between parallel and tapered rosettes is a single construction choice:

### Parallel (our {10/4} case)
- Line [b1-b5] spans **8 divisions** (4 radii + 4 inter-radii)
- Creates a **{10/4}** star polygon in the center
- Petal sides [g-c1] and [g2-c2] are **parallel**
- The petal ends are defined by a decagon
- Requires only circle [ob] (no separate [oc])

### Tapered ({10/3} case)
- Line [b1-b4] spans **6 divisions** (3 radii + 3 inter-radii)
- Creates a **{10/3}** star polygon in the center
- Petal sides converge/narrow outward
- Requires BOTH circle [ob] and circle [od] to define the star polygon
- Point [g] controls the slope of the petal end line

### Key relationship
Point [g] on the bisector is the bridge between the petal definition and the star polygon. In the parallel case, line [a10-g-a1] is straight. In the tapered case, it bends at [g].

## The Critical Proportioning Circle

This is the most important single construction element:

1. Points [P1] and [P2] are adjacent vertices of the peripheral polygon (decagon)
2. Connecting P1-P2 intersection lines defines point [a] on the radius
3. Circle [P1, radius=P1a] is the **critical proportioning circle**
4. This circle defines point [b] where it crosses the radius [o-P1]
5. **[a1-P] = [P-b]** — a and b lie on the same circle centered at P
6. **[P-g] is a bisector** — Angle [a1-P-g] = Angle [g-P-b]
7. These THREE circles ([oa], [ob], [Pa]) completely define ALL proportions

## Ideal Proportions: Why They Are Ideal

The "ideal proportions" defined by this method produce a specific result that no other proportions can:

- In the 10-fold case: ten tangent peripheral circles [Pa] around the center circle [ob] create **perfect pentagram stars** at each P vertex
- The central star polygon is itself a pair of overlapping pentagrams
- No other set of proportions gives perfect peripheral stars
- This is the archetype for all rosettes above sixfold symmetry

**Implication for our work:** Our "satellites" ARE these peripheral stars. They should be perfect pentagrams (for 10-fold). If they don't look like perfect pentagrams, the proportions are wrong.

## Tiling and Interstitial Shapes

### The closest tiling
- Rosettes are arranged so they touch at petal tips (no overlap)
- For 10-fold: 4 quarter-rosettes surround a center rosette in a rectangular tile
- The space between rosettes forms "bowtie" shaped concave tiles

### Interstitial shapes are RESULTS, not designs
This is perhaps the most important single insight from the article:

> "Polygons are formed in the bowtie tile space around the rosette... These are not independently constructed. They are results of tiling interactions."

The interstitial tiles emerge when pattern lines are extended to the tiling boundary. They include:
- **Congruent hexagonal petals** — identical to the rosette's own petals
- **Peripheral pentagram stars** — formed at P vertices by the interaction of neighboring rosettes
- **"Swallow" figures** — 3-point bird-shaped polygons from circle packing imperfection
- **Resultant rhombuses** — in the bowtie tile space

**Implication for our work:** We should NOT be independently designing interstitial tiles. We should extend the pattern lines to the tiling boundary and let the shapes emerge. Our "corridor" approach was an attempt to fill the interstitial zone with designed shapes, which is fundamentally backwards.

## The Minimal Triangle

For any rosette pattern, there exists a "minimal triangle" that contains ALL structural information:

### 8-fold case
- Triangle [o-CR-o'] = 1/8 of the pattern
- This single triangle, reflected and rotated, creates the entire pattern
- The proportioning circle [Pa] is the **incircle** of the larger triangle [o-CR-o']

### 10-fold case (more complex)
- Requires TWO triangles: [o-h-o'] and [h-CR-o']
- Point [h] defines the boundary between the rosette zone and the interstitial zone
- Triangle [o-h-o'] contains the rosette proper
- Triangle [h-CR-o'] contains the tiling interaction zone
- Together with reflections, these three triangles create the entire pattern

**Implication for our work:** The interstitial zone is governed by the SECOND triangle [h-CR-o'], which has different geometric rules than the rosette triangle. This explains why interstitial tile construction has been our hardest problem — we've been trying to derive interstitial shapes from the rosette's geometry, but they come from a different geometric domain.

## Construction Sequence (10-fold Parallel)

Step-by-step for the pattern type we are building:

1. **Divide the master circle** into 20 equal parts (2n for 10-fold)
2. **Define the rectangular tile** from the divided circle
3. **Find points [P]** — the two inter-radii on each side of the diagonals
4. **Draw the proportioning circle** [Pa] at P1 with radius P1-a
5. **Circle [ob]** — defined by point [b] where [Pa] crosses radius [oP1]
6. **Circle [oa]** — defined by point [a] on the radius
7. **Construct the bisector** at P between the polygon side and the radius
8. **Draw line [b1-b5]** — this defines parallel petals (the {10/4} star polygon)
9. **Define circle [oc]** from line [b1-b5]
10. **Draw the center star polygon** using circle [ob]
11. **Extend star polygon lines** to meet the petal ends (defined by decagon for parallel case)
12. **Draw circle [oc] extended** to the master circle for corner layout
13. **Complete the rosette** by drawing petal boundaries
14. **Extend pattern lines** to the tiling boundary to define interstitial shapes
15. **Fill the bowtie tile** by extending lines to hexagon tile boundaries

## 2n Divisions Rule

Rosettes always use **2n** divisions of the circle, where n is the symmetry number.
- 8-fold rosette → 16 divisions
- 10-fold rosette → 20 divisions
- 12-fold rosette → 24 divisions

This creates both **radii** (R) and **inter-radii** (I-R), which are equally important. The inter-radii define points [P] and the proportioning circle.

## Key Quotes and Principles

- "Almost all rosettes are basically the same layout, applied to different divisions of the circle"
- "The proportioning circle [P1 a] defines point [b]... These three circles completely define the proportions of the rosette"
- Interstitial shapes: "These are not independently constructed. They are results of tiling interactions."
- Ideal proportions: "No other set of proportions for the peripheral stars and a center star polygon will give this result"
- The minimal triangle: "Everything in this pattern is completely defined within the yellow triangle; it is the minimal triangle"

## Applicability to Our Work

### What confirms our current approach
- Our {10/4} diagonal strapwork = the parallel rosette case (correct)
- Our satellite construction at P vertices = peripheral star locations (correct)
- Our sector-first construction = mirrors the minimal triangle approach (correct)
- Our concentric circle system (R, satDist, satR) = analogous to [oa], [ob] system (correct)

### What suggests improvements
1. **Interstitial tiles should emerge from line extension, not independent construction** — the article shows interstitial shapes come from extending pattern lines to tiling boundaries
2. **Peripheral stars should be perfect pentagrams** — if our satellites don't look like pentagrams, the proportions may be off
3. **The proportioning circle [Pa] may give us better proportions** — currently our ratios are empirically derived; the Lee method derives them from a single circle
4. **The second minimal triangle governs the interstitial zone** — this is a different geometric domain from the rosette itself
5. **Hexagonal petals in the interstitial zone should be congruent to rosette petals** — a checkable criterion we haven't verified
