# Color Palettes — Traditional Islamic Art

Reference document of historically and regionally common color palettes found in Islamic geometric art. Use this when analyzing reference images to identify which tradition a pattern belongs to, and when generating new patterns.

## Ottoman Blue

Characteristic of Ottoman mosque interiors (Iznik tiles, Sultan Ahmed / Blue Mosque).

| Role | Color | Hex | Notes |
|------|-------|-----|-------|
| Primary | Deep navy | `#1a2c4d` | Dominant background |
| Secondary | Cobalt blue | `#2d4a7c` | Mid-tone fills |
| Tertiary | Cerulean | `#4a6ba5` | Transitional rings |
| Accent | Turquoise | `#5fb5c4` | Highlights |
| Highlight | Bright cyan | `#7dd6e0` | Central motif |
| Neutral | White/cream | `#f5f5e8` | Strapwork bands |
| Metallic | Gold | `#d4a843` | Outlines, calligraphy |

**Distribution rule:** Radial gradient — brightest at center, darkest at perimeter. White/cream reserved for interlace bands that weave across the gradient.

**D3.js usage:**
```javascript
const ottomanBlue = d3.scaleLinear()
  .domain([0, 0.25, 0.5, 0.75, 1.0])
  .range(['#7dd6e0', '#5fb5c4', '#4a6ba5', '#2d4a7c', '#1a2c4d']);
```

## Moroccan / Zellige

Characteristic of Moroccan zellige tilework (Fez, Marrakech, Alhambra-influenced).

| Role | Color | Hex | Notes |
|------|-------|-----|-------|
| Primary | Emerald green | `#1a6b4a` | Islamic green, dominant |
| Secondary | Deep blue | `#1a3a6b` | Complementary fills |
| Tertiary | White | `#f0ece0` | Tile edges, grout lines |
| Accent | Saffron yellow | `#e6a817` | Sparse highlights |
| Warm | Terracotta | `#c45a3c` | Earth-tone contrast |
| Dark | Black/charcoal | `#2a2a2a` | Outlines |

**Distribution rule:** Per-tile-type coloring — each distinct geometric shape gets a single color. Colors alternate to maximize contrast between adjacent tiles. White grout lines (1-2px) separate all tiles.

## Persian / Safavid

Characteristic of Persian mosque domes, mihrab niches, and manuscript illumination.

| Role | Color | Hex | Notes |
|------|-------|-----|-------|
| Primary | Persian turquoise | `#00a99d` | Dominant tile color |
| Secondary | Lapis blue | `#1e3a5f` | Deep accents |
| Tertiary | Cream/ivory | `#f5ecd7` | Background, calligraphy ground |
| Accent | Gold leaf | `#c9a84c` | Gilded outlines, arabesques |
| Warm | Rose pink | `#c76b8a` | Floral elements |
| Dark | Deep burgundy | `#6b1d3a` | Borders, shadow |

**Distribution rule:** Zonal — large fields of turquoise with gold tracery. Warmer tones (rose, burgundy) appear in arabesque/floral zones. Gold dominates interlace bands.

## Alhambra / Nasrid

Characteristic of the Alhambra palace in Granada.

| Role | Color | Hex | Notes |
|------|-------|-----|-------|
| Primary | Terra cotta red | `#b44b2a` | Carved stucco, warm base |
| Secondary | Sage green | `#6b8c5a` | Tile accents |
| Tertiary | Cobalt blue | `#2d5da1` | Tile accents |
| Accent | Gold/ochre | `#c9a84c` | Gilded muqarnas, outlines |
| Neutral | Plaster white | `#e8dcc8` | Carved stucco ground |
| Dark | Walnut brown | `#4a3728` | Shadow, wood elements |

**Distribution rule:** Material-driven — color changes with physical medium. Carved plaster is white/cream with gold accents. Tile zones use green/blue/terracotta in strict per-shape assignment. Muqarnas tiers alternate gold and white.

## Mamluk / Egyptian

Characteristic of Mamluk-era Cairo (mosques, madrasas, Quran manuscripts).

| Role | Color | Hex | Notes |
|------|-------|-----|-------|
| Primary | Crimson red | `#a82028` | Dominant, powerful |
| Secondary | Gold | `#c9a84c` | Lavish gilding |
| Tertiary | Royal blue | `#1e3a7b` | Deep contrast |
| Accent | White | `#f0ece0` | Calligraphy, highlights |
| Dark | Black | `#1a1a1a` | Outlines, manuscript borders |

**Distribution rule:** Bold contrast — large fields of red and blue separated by gold bands. Manuscript illumination uses gold for all geometric outlines with colored fills.

## Mughal / Indo-Islamic

Characteristic of Mughal architecture (Taj Mahal, Humayun's Tomb).

| Role | Color | Hex | Notes |
|------|-------|-----|-------|
| Primary | White marble | `#f5f0e8` | Dominant surface |
| Secondary | Carnelian red | `#b83a2a` | Pietra dura inlay |
| Tertiary | Jade green | `#3a7a4a` | Pietra dura inlay |
| Accent | Lapis blue | `#2a4a8a` | Pietra dura inlay |
| Warm | Onyx amber | `#c4903a` | Inlay accent |
| Dark | Black slate | `#2a2a2a` | Calligraphy, fine lines |

**Distribution rule:** White ground with colored stone inlay forming the pattern. Colors are sparse — most of the visual field is white, with colored elements defining the geometry.

## Monochrome / Carved Plaster

Not a color palette per se, but a common rendering mode.

| Role | Color | Hex | Notes |
|------|-------|-----|-------|
| Background | Shadow | `#c8bfa8` | Recessed areas |
| Foreground | Raised plaster | `#f0e8d8` | Relief surface |
| Accent | Gold highlight | `#d4b868` | Optional gilding |

**Distribution rule:** Depth via shadow only. The pattern is monochromatic white plaster with depth created by varying relief levels. Shadows (darker cream/brown) fill the recessed areas.

## Dark / Digital

A modern palette suitable for screen rendering and the existing sacred-patterns library.

| Role | Color | Hex | Notes |
|------|-------|-----|-------|
| Background | Near-black | `#0a1929` | Deep dark blue-black |
| Primary | Electric cyan | `#7dd6e0` | Bright, central |
| Secondary | Medium blue | `#2d4a7c` | Mid-tone fills |
| Accent | Gold | `#d4a843` | Outlines, strapwork |
| Highlight | Soft white | `#f5f5e8` | Interlace bands |
| Error | Warm red | `#e85a4f` | Debug/construction lines |

**Distribution rule:** Matches the `session-abc` approach — radial gradient from bright center to dark perimeter, with gold outlines and white strapwork.

---

## Identifying a Palette from a Reference Image

1. **Sample 5-8 distinct colors** from the image (background, dominant fill, secondary fills, outlines, highlights)
2. **Check distribution** — is it radial gradient, per-tile, zonal, or material-driven?
3. **Match to tradition** — compare sampled colors against the palettes above
4. **Note deviations** — the reference may use a non-traditional palette; record it as-is with hex codes
5. **Record in analysis.md** — list all colors with hex codes and their roles

## D3.js Color Tips

- Use `d3.scaleLinear()` with `.range()` for radial gradients
- Use `d3.scaleOrdinal()` for per-tile-type coloring
- For opacity effects: `d3.rgb(hex).copy({opacity: 0.5})`
- Gold strokes work well at 1.5-2px width on dark backgrounds
- White strapwork on dark backgrounds: use `#f5f5e8` (warm white) rather than pure `#ffffff`
