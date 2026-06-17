# Medallion-10 — higher-level grouping (#46)

**Plain English:** #45 told us the medallion is built from 26 distinct shapes. This
answers the next question — *how are those 26 shapes organized?* The answer is simple
and strong: the medallion is **one repeating wedge, rotated 10 times, stacked as 26
concentric bands.** Nothing is placed freely; every one of the 381 shapes sits at a
fixed radius and a fixed 10-fold angular slot.

View: `shape-grouping.png` (Dropbox) — polar band map (left) + the single repeating
wedge (right). Generator: `render_grouping.py` (git).

## The organizing structure

After recentering `clusters.json` `member_centers` on the pattern center
(centroid of all 381 members = **(512.2, 512.2)**), every cluster is **perfectly
concentric** — radial spread 0.0. So each of the 26 classes IS a concentric band at a
discrete radius (r = 0 → 463.7). The medallion decomposes into:

| role | count | what it is | bands |
|------|-------|-----------|-------|
| CENTER | 1 (×1) | the unique centerpiece star, r=0 | k25 |
| ON-AXIS | 6 (×10) | shapes centered ON a spoke arm (ang ≡ 0/36 mod 36) | k17 k15 k23 k16 k24 k20 |
| HALF-AXIS | 6 (×10) | shapes BETWEEN arms (ang ≡ 18 mod 36) | k14 k21 k18 k13 k19 k22 |
| PAIRED | 13 (×20) | mirror L/R halves of an arm motif (a mirror pair about a spoke) | k00 k01 k05 k06 k07 k12 k09 k03 k10 k11 k04 k02 k08 |

**One 36° wedge = 38 shapes** (1 center counted once + the per-wedge share of each
ring). Rotate that wedge 10× → the whole 381-shape medallion. This is the
higher-level grouping: not 26 loose vocabulary entries, but **1 motif × 10-fold ×
26 radial bands.**

## k24 / k25 star reconciliation (the open question from #45)

#45 flagged that k24 (×10, 20-gon) and k25 (×1, 20-gon) are both star silhouettes.
The radial structure resolves it cleanly:
- **k25** — ×1, **r=0**, role CENTER. The unique central star.
- **k24** — ×10, **r=381.4**, role ON-AXIS. The rim-star band, one star centered on
  each of the 10 arms.

Same silhouette, different radius, different role — no conflation. The congruence
clusterer correctly split them because the central star is unique (no 10-fold
companions at r=0) while the rim stars form a 10-fold ring.

## How this is derived (reproducible)

`render_grouping.py`:
1. center = centroid of all `member_centers` (raster px) = (512.2, 512.2)
2. per class: mean radius from center; angular positions mod 36°
3. role = f(count, angle-mod-36): ×1→CENTER, ×20→PAIRED, ×10 & ang∈{0,36}→ON-AXIS,
   ×10 & ang≈18→HALF-AXIS
4. draw the full medallion (polar map, role-colored) + the collapsed wedge stack

## Why it matters downstream

- **Simplification UX (#42):** the DSL author doesn't need 26 hand-placed rings — the
  structure says "one wedge under `rotate 10 around C0.mpt`, bands at these 26 radii."
  This is the grouping #42's umbrella can lean on to propose `rotate`/`mirror`
  collapses.
- **Motif vocabulary:** the three roles map to construction intent — on-axis = the
  petal/shield tips that crown each arm; half-axis = the interstitial fillers; paired =
  the arm-body halves. A future motif detector groups bands into named radial stacks
  (inner rosette / arm shaft / rim crown) along these role transitions.
