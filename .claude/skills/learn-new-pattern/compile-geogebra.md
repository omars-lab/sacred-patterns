# Compile pattern.json to GeoGebra

Guide for translating a `pattern.json` declarative definition into GeoGebra outputs: a paste-in script (`.txt`) and a `.ggb` archive file.

## Output 1: GeoGebra Script (`.txt`)

A text file containing GeoGebra Classic commands that can be pasted into the GeoGebra input bar to construct the pattern.

### Script Structure

```
# Pattern Name — GeoGebra Construction Script
# Generated from pattern.json

# === Construction Circles ===
# Define radii relative to base unit r0
r0 = 4
r1 = r0 * 0.15
r2 = r0 * 0.35
...

# === Center Point ===
O = (0, 0)

# === Construction Circles ===
c0 = Circle(O, r0)
c1 = Circle(O, r1)
...

# === Angular Divisions ===
# Primary angles (e.g., every 45° for D8)
L0 = Ray(O, (r0 * cos(0°), r0 * sin(0°)))
L1 = Ray(O, (r0 * cos(45°), r0 * sin(45°)))
...

# === Geometric Elements ===
# [Layer-by-layer construction]

# === Styling ===
SetColor(element, R, G, B)
SetLineThickness(element, thickness)
ShowLabel(element, false)
```

### Mapping Layer Types to GeoGebra Commands

#### `star-polygon` → Polygon + Point definitions

```
# {8/3} star polygon at center O with radius r3
P_0 = (O_x + r3 * cos(0° + rotation), O_y + r3 * sin(0° + rotation))
P_1 = (O_x + r3 * cos(45° + rotation), O_y + r3 * sin(45° + rotation))
...P_7
StarPoly = Polygon(P_0, P_3, P_6, P_1, P_4, P_7, P_2, P_5)
# (vertices listed in connection order: 0→3→6→1→4→7→2→5→0)
```

For {n/k}: list vertices in order 0, k, 2k, 3k, ... (mod n).

#### `polygon` → Polygon command

```
# Regular octagon
Oct_0 = (O_x + r * cos(rotation), O_y + r * sin(rotation))
...Oct_7
OctPoly = Polygon(Oct_0, Oct_1, ..., Oct_7)
```

#### `circle` / `circle-ring` → Circle command

```
c_ring = Circle(O, r_ring)
SetColor(c_ring, R, G, B)
SetLineThickness(c_ring, 2)
```

#### `radial-repeat` → Rotate command

```
# Create base element at angle 0
BaseElem = [construct the element]

# Repeat by rotation
Elem_1 = Rotate(BaseElem, 45°, O)
Elem_2 = Rotate(BaseElem, 90°, O)
...
Elem_7 = Rotate(BaseElem, 315°, O)
```

GeoGebra's `Rotate(object, angle, center)` creates a rotated copy.

#### `rosette` → Polygon with alternating radii

```
# 12-petal rosette
Ros_outer_0 = (cx + outerR * cos(0°), cy + outerR * sin(0°))
Ros_inner_0 = (cx + innerR * cos(15°), cy + innerR * sin(15°))
Ros_outer_1 = (cx + outerR * cos(30°), cy + outerR * sin(30°))
...
RosPoly = Polygon(Ros_outer_0, Ros_inner_0, Ros_outer_1, Ros_inner_1, ...)
```

#### `line` → Segment command

```
LineSeg = Segment((x1, y1), (x2, y2))
```

#### `flower-of-life` → Recursive Circle construction

```
c_center = Circle(O, r_flower)
# Surrounding circles at 60° intervals
c_surr_0 = Circle((r * cos(0°), r * sin(0°)), r_flower)
c_surr_1 = Circle((r * cos(60°), r * sin(60°)), r_flower)
...
# Repeat for next level
```

### Color Mapping

GeoGebra uses RGB integers (0-255). Convert hex colors:

| Hex | R | G | B | GeoGebra |
|-----|---|---|---|----------|
| `#7dd6e0` | 125 | 214 | 224 | `SetColor(elem, 125, 214, 224)` |
| `#2d4a7c` | 45 | 74 | 124 | `SetColor(elem, 45, 74, 124)` |
| `#d4a843` | 212 | 168 | 67 | `SetColor(elem, 212, 168, 67)` |
| `#f5f5e8` | 245 | 245 | 232 | `SetColor(elem, 245, 245, 232)` |
| `#0a1929` | 10 | 25 | 41 | `SetColor(elem, 10, 25, 41)` |

### Script Conventions

- Use descriptive variable names (`CentralStar`, `SatPoly1`, `Ring7`)
- Hide labels: `ShowLabel(element, false)` for all construction elements
- Set line thickness: `SetLineThickness(element, N)` where N is 1-5
- Fill polygons: `SetFilling(element, opacity)` where opacity is 0.0-1.0
- Make construction elements auxiliary: `SetAuxiliary(element, true)`
- Scale factor: Use `r0 = 4` (or similar) as the base unit, matching session-abc convention

---

## Output 2: GeoGebra Archive (`.ggb`)

A `.ggb` file is a ZIP archive containing:

```
pattern.ggb (ZIP):
  ├── geogebra.xml               # The construction
  ├── geogebra_defaults2d.xml    # 2D view defaults
  ├── geogebra_defaults3d.xml    # 3D view defaults
  ├── geogebra_javascript.js     # JavaScript hooks (minimal)
  └── geogebra_thumbnail.png     # Preview image
```

### Building the .ggb Archive

1. **Generate `geogebra.xml`** from the construction steps
2. **Copy template files** from `templates/` directory:
   - `geogebra_defaults2d.xml`
   - `geogebra_defaults3d.xml`
   - `geogebra_javascript.js`
3. **Use iteration screenshot** as `geogebra_thumbnail.png`
4. **Create the ZIP archive:**

```bash
mkdir -p /tmp/ggb-build
cp templates/geogebra_defaults2d.xml /tmp/ggb-build/
cp templates/geogebra_defaults3d.xml /tmp/ggb-build/
cp templates/geogebra_javascript.js /tmp/ggb-build/
cp iterations/{nn}/screenshot.png /tmp/ggb-build/geogebra_thumbnail.png
# geogebra.xml is generated and written to /tmp/ggb-build/
cd /tmp/ggb-build && zip -j /path/to/final/pattern.ggb \
    geogebra.xml geogebra_defaults2d.xml geogebra_defaults3d.xml \
    geogebra_javascript.js geogebra_thumbnail.png
```

### geogebra.xml Structure

The XML follows GeoGebra's format (as seen in the session-8-fold reference):

```xml
<?xml version="1.0" encoding="utf-8"?>
<geogebra format="5.0" version="5.0.0"
    xmin="-8" xmax="8" ymin="-6" ymax="6"
    width="1024" height="768">
<construction>
    <!-- Points -->
    <element type="point" label="O">
        <show object="true" label="false"/>
        <coords x="0" y="0" z="1"/>
        <pointSize val="3"/>
    </element>

    <!-- Free numbers (radii) -->
    <element type="numeric" label="r0">
        <value val="4"/>
    </element>

    <!-- Dependent points -->
    <command name="Point">
        <input a0="(r0 * cos(0), r0 * sin(0))"/>
        <output a0="P_0"/>
    </command>

    <!-- Circles -->
    <command name="Circle">
        <input a0="O" a1="r0"/>
        <output a0="c0"/>
    </command>

    <!-- Polygons -->
    <command name="Polygon">
        <input a0="P_0" a1="P_3" a2="P_6" a3="P_1" a4="P_4" a5="P_7" a6="P_2" a7="P_5"/>
        <output a0="StarPoly"/>
    </command>

    <!-- Styling -->
    <element type="polygon" label="StarPoly">
        <show object="true" label="false"/>
        <objColor r="125" g="214" b="224" alpha="0.5"/>
        <lineStyle thickness="2"/>
    </element>
</construction>
</geogebra>
```

### XML Generation Notes

- Points use `<coords x="val" y="val" z="1"/>` (z=1 for homogeneous coordinates)
- Commands reference labels of previously defined elements
- Colors use integer RGB (0-255) with optional alpha (0.0-1.0)
- Labels default to hidden: `<show object="true" label="false"/>`
- Line thickness uses `<lineStyle thickness="N"/>` (1-13)
- Fill opacity uses `alpha` attribute in `objColor`
- View window: set `xmin`, `xmax`, `ymin`, `ymax` to frame the pattern with padding

### Template Files

The template files are stored in the skill's `templates/` directory, copied from the `session-8-fold/8-Fold Rosette/` extraction. They contain default GUI settings, view configurations, and a minimal JavaScript stub.
