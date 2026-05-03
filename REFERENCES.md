# Research References: Islamic Geometric Art & Computational Pattern Generation

## Key Concepts

- **Hankin / Polygons in Contact**: Construction method where rays sprout from tile edge midpoints at a contact angle and grow until intersection.
- **Strapwork / Bands**: The white interlacing lines. Two approaches: (A) lines drawn on top of tiles, (B) tiles inset from band edges so bands are genuine gaps. Approach B is correct for traditional appearance.
- **Contact Angle**: For 10-fold patterns, girih lines cross tile boundaries at 54 degrees (3pi/10 radians).
- **Band Width Ratio**: Traditional 10-fold patterns use band width of approximately 0.10-0.12 of pattern radius (1/6 to 1/5 of tile edge length).
- **Rendering Styles (Kaplan)**: Plain, Outline, Interlace, Checkerboard, Emboss, Combined.
- **DCEL (Doubly-Connected Edge List)**: Planar subdivision data structure for computing tile faces from line arrangements.

---

## Academic Papers

- **Kaplan, "Islamic Star Patterns from Polygons in Contact" (2005)**
  https://cs.uwaterloo.ca/~csk/publications/Papers/kaplan_2005.pdf
  Defines the Hankin "polygons in contact" method. Six rendering styles (plain, outline, interlace, checkerboard, emboss, combined).

- **Kaplan, PhD Thesis**
  https://cs.uwaterloo.ca/~csk/other/phd/kaplan_diss_starpatterns_print.pdf
  Chapter 3 covers star pattern construction in depth.

- **Kaplan & Salesin, "Islamic Star Patterns in Absolute Geometry" (2004)**
  https://grail.cs.washington.edu/wp-content/uploads/2015/08/kaplan-2004-isp.pdf
  Extends to non-Euclidean geometries, details offset curve thickening for strapwork.

- **Hankin's Polygons in Contact Grid Method (Bridges 2008)**
  https://archive.bridgesmathart.org/2008/bridges2008-21.pdf

- **Cline, "Interlace Patterns Emerging in a Penrose-Type Islamic Design" (Bridges 2024)**
  https://archive.bridgesmathart.org/2024/bridges2024-163.pdf
  Recent work on interlace in Penrose-type patterns.

- **Azizi Naserabad & Ghanbaran, "Computational approach in presentation a parametric method to construct hybrid girihs" (2025)**
  https://journals.sagepub.com/doi/10.1177/14780771241279347
  Latest parametric hybrid girih construction.

---

## Open Source Implementations

- **Taprats** (Java) -- Original Kaplan implementation, all 6 rendering styles.
  https://taprats.sourceforge.net/

- **CodingTrain/StarPatterns** (JavaScript/p5.js) -- Hankin method, line-based skeleton.
  https://github.com/CodingTrain/StarPatterns

- **miracle2k/islamic-patterns** (TypeScript) -- Two methods (Eric Broug + polygons in contact).
  https://github.com/miracle2k/islamic-patterns

- **pierrebai/Alhambra** (C++/Qt) -- Full interlace rendering, Kaplan+Baillargeon method. Configurable band width.
  https://github.com/pierrebai/Alhambra

- **ChortleMortal/TiledPatternMaker** (C++/Qt) -- Full interlace, derived from Taprats.
  https://github.com/ChortleMortal/TiledPatternMaker

- **Ehyaei/Kaashi** (R) -- Hankin method, sf geometry output.
  https://github.com/Ehyaei/Kaashi

- **harpninja/geometric** (JavaScript/D3.js) -- D3 SVG rendering, Paul Bourke geometry.
  https://github.com/harpninja/geometric

- **jaycody/saracenic-stars** (JavaScript) -- Polygons in contact, Hankin method.
  https://github.com/jaycody/saracenic-stars

---

## Tutorials & Guides

- **Envato Tuts+ "Geometric Design: Knots and Weaves"**
  https://design.tutsplus.com/tutorials/geometric-design-knots-and-weaves--cms-23968
  Explains strapwork band construction: widening outlines so space between shapes becomes itself a shape.

- **Drawing Islamic Geometric Designs: 10-fold Rosette (Anthony Lee's methods)**
  https://www.drawingislamicgeometricdesigns.com/basic-rosettes-anthony-lees-methods/Blog%20Post%20Title%20One-n5m4l

- **Rombo.tools Islamic Pattern Generator**
  https://www.rombo.tools/2026/01/05/islamic-pattern/
  Interactive generator with Line Width parameter.

---

## Reference / Encyclopedia

- **Wikipedia: Islamic Geometric Patterns**
  https://en.wikipedia.org/wiki/Islamic_geometric_patterns

- **Wikipedia: Girih**
  https://en.wikipedia.org/wiki/Girih

- **Wikipedia: Girih Tiles**
  https://en.wikipedia.org/wiki/Girih_tile
