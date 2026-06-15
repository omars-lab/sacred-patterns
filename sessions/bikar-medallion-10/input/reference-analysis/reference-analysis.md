# Reference analysis — standardized palette + line measurements

Plain English: these are the colors the reference photo actually uses,
extracted once so color iterations tune toward an agreed target instead
of re-guessing. Stage 2 `palette` blocks use these hex values verbatim;
iterations only change which faces map to which named color.

- **Lattice line:** `#FCFDFD`, width ≈ 5.1px (0.688% of medallion diameter 738px)
- **Fill clusters (k=7, area share of fill pixels):**

| name | hex | share |
|---|---|---|
| navy | `#132A61` | 47.5% |
| royal | `#2661BF` | 19.4% |
| cyan | `#3EAACC` | 10.4% |
| cyan_2 | `#02C5D4` | 7.9% |
| periwinkle | `#80A1E8` | 5.2% |
| navy_2 | `#22406C` | 4.9% |
| gray | `#B8B8B8` | 4.6% |

Note: the `gray` cluster is the medallion's rim outline plus lattice-blend pixels, not a tile color — Stage 2 palettes skip it.

## Zone dominance (radial bands, top-3 clusters per band)

| zone | dominant colors |
|---|---|
| center | periwinkle 71%, navy 27%, gray 1% |
| inner field | navy 37%, cyan 30%, periwinkle 14% |
| mid field | royal 32%, navy 31%, cyan_2 14% |
| outer / boundary | navy 74%, royal 16%, gray 10% |

Swatch sheet: `swatch-sheet.png` — the Stage-2 entry-gate visual.
