#!/usr/bin/env bash
# structure-diff.sh — Stage-1 structure comparison: skeleton render vs edge-extracted reference.
#
# Plain English: renders the line-skeleton of an iteration's pattern (no
# fills, no bands), turns both the skeleton and the reference photo into
# edge maps, and scores how well the line networks agree — a structure
# similarity number that ignores color entirely. Also composes the
# side-by-side images the owner looks at for the structure gate.
#
# Usage:
#   ./tools/structure-diff.sh SESSION_DIR ITER
#
# Reads   SESSION_DIR/iterations/ITER/pattern.bkr
#         SESSION_DIR/input/reference.jpg
# Writes  iterations/ITER/structure.bkr        (regenerated every run)
#         iterations/ITER/skeleton.svg/.png    (the Stage-1 visual; sha256 of
#                                               the PNG is the freeze check —
#                                               Stage 2/3 edits must keep it
#                                               byte-identical)
#         iterations/ITER/skeleton-edges.png   (Canny edge map)
#         input/reference-structure.png        (one-time edge map of the photo)
#         iterations/ITER/structure-diff/      (qiyas pixel-diff on edge maps)
#         iterations/ITER/structure-sbs.png    (reference-lines | skeleton-edges)
#         iterations/ITER/structure-context-sbs.png (reference | skeleton)
#
# Requires: node >= 20 on PATH (bikar CLI), ImageMagick 7 (magick), docker
# with the qiyas image. Canny thresholds are FIXED (tuned once at first
# execution); changing them invalidates cross-iteration comparability.

set -euo pipefail

SESSION_DIR=${1:?usage: structure-diff.sh SESSION_DIR ITER}
ITER=${2:?usage: structure-diff.sh SESSION_DIR ITER}
BIKAR_DIR=${BIKAR_DIR:-/Users/omareid/Workspace/git/bikar}
QIYAS_IMAGE=${QIYAS_IMAGE:-ghcr.io/naqshcoffee/qiyas:latest}
CANNY="0x1+10%+30%"   # fixed — see header
TOOLS_DIR=$(cd "$(dirname "$0")" && pwd)
ITDIR=$SESSION_DIR/iterations/$ITER

[ -f "$ITDIR/pattern.bkr" ] || { echo "error: $ITDIR/pattern.bkr not found" >&2; exit 1; }
[ -f "$SESSION_DIR/input/reference.jpg" ] || { echo "error: $SESSION_DIR/input/reference.jpg not found" >&2; exit 1; }

# 1. Skeleton .bkr (always regenerated — it is derived, never hand-edited).
python3 "$TOOLS_DIR/make-structure.py" "$ITDIR/pattern.bkr" > "$ITDIR/structure.bkr"

# 2. Render the skeleton (SVG), rasterize via rsvg-convert — NOT magick:
#    ImageMagick 7.1.2's internal MSVG renderer silently drops stroked paths
#    (fills raster fine, strokes vanish → an all-white skeleton), and it does
#    not invoke its rsvg delegate on read. Witnessed 2026-06-11; minimal repro
#    is any <path fill="none" stroke="#000"> through `magick foo.svg foo.png`.
node "$BIKAR_DIR/packages/cli/dist/index.js" render "$ITDIR/structure.bkr" -o "$ITDIR/skeleton.svg" >/dev/null
rsvg-convert --width 1024 --height 1024 --keep-aspect-ratio --background-color white \
  "$ITDIR/skeleton.svg" -o "$ITDIR/skeleton.png"

# 3. Edge maps: Canny produces white-on-black; negate to dark-lines-on-white
#    so qiyas pixel-diff's content/background split sees lines as content.
if [ ! -f "$SESSION_DIR/input/reference-structure.png" ]; then
  magick "$SESSION_DIR/input/reference.jpg" -colorspace Gray -canny "$CANNY" -negate \
    "$SESSION_DIR/input/reference-structure.png"
fi
magick "$ITDIR/skeleton.png" -colorspace Gray -canny "$CANNY" -negate "$ITDIR/skeleton-edges.png"

# 4. Structure similarity = pixel-diff on the two EDGE MAPS (color-blind by
#    construction; no qiyas code change — the structure-awareness lives in
#    the preprocessing above).
docker run --rm -v "$SESSION_DIR:/work" "$QIYAS_IMAGE" pixel-diff \
  /work/input/reference-structure.png \
  "/work/iterations/$ITER/skeleton-edges.png" \
  --out "/work/iterations/$ITER/structure-diff" --rasterizer magick

# 5. Owner-facing side-by-sides.
magick \( "$SESSION_DIR/input/reference-structure.png" -resize x720 \) \
       \( "$ITDIR/skeleton-edges.png" -resize x720 \) \
       +append -background white "$ITDIR/structure-sbs.png"
magick \( "$SESSION_DIR/input/reference.jpg" -resize x720 \) \
       \( "$ITDIR/skeleton.png" -resize x720 \) \
       +append -background white "$ITDIR/structure-context-sbs.png"

# 6. Summary: the similarity number + the freeze-check sha.
SIM=$(python3 -c "import json;print(json.load(open('$ITDIR/structure-diff/pixel-diff.json'))['similarity_pct'])")
SHA=$(shasum -a 256 "$ITDIR/skeleton.png" | cut -d' ' -f1)
echo "structure-diff: iter=$ITER structure_similarity=$SIM skeleton_sha256=$SHA"
echo "  gate visuals: $ITDIR/structure-sbs.png  $ITDIR/structure-context-sbs.png"
