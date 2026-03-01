#!/bin/bash
# build-gallery-index.sh — Generate gallery/index.html from session.json files
#
# Usage: ./build-gallery-index.sh <sessions_dir> <template_path> <output_path> <gallery_dir>
#
# Reads session-*/session.json files, builds a JSON array, and injects it
# into the gallery template to produce a static gallery index page.

set -euo pipefail

SESSIONS_DIR="${1:?Usage: build-gallery-index.sh <sessions_dir> <template_path> <output_path> <gallery_dir>}"
TEMPLATE="${2:?Missing template path}"
OUTPUT="${3:?Missing output path}"
GALLERY_DIR="${4:?Missing gallery dir}"

# Check if jq is available
HAS_JQ=false
if command -v jq &>/dev/null; then
    HAS_JQ=true
fi

SESSIONS_JSON="["
FIRST=true

for session_dir in "$SESSIONS_DIR"/session-*/; do
    [ -d "$session_dir" ] || continue
    sj="$session_dir/session.json"
    [ -f "$sj" ] || continue

    session_name=$(basename "$session_dir")

    if $HAS_JQ; then
        name=$(jq -r '.name // ""' "$sj")
        pattern_type=$(jq -r '.pattern_type // ""' "$sj")
        symmetry_group=$(jq -r '.symmetry_group // ""' "$sj")
        confidence_score=$(jq -r '.confidence_score // 0' "$sj")
        status=$(jq -r '.status // ""' "$sj")
    else
        # Fallback: basic grep/sed extraction
        name=$(grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "$sj" | head -1 | sed 's/.*: *"//;s/"//')
        pattern_type=$(grep -o '"pattern_type"[[:space:]]*:[[:space:]]*"[^"]*"' "$sj" | head -1 | sed 's/.*: *"//;s/"//')
        symmetry_group=$(grep -o '"symmetry_group"[[:space:]]*:[[:space:]]*"[^"]*"' "$sj" | head -1 | sed 's/.*: *"//;s/"//')
        confidence_score=$(grep -o '"confidence_score"[[:space:]]*:[[:space:]]*[0-9.]*' "$sj" | head -1 | sed 's/.*: *//')
        status=$(grep -o '"status"[[:space:]]*:[[:space:]]*"[^"]*"' "$sj" | head -1 | sed 's/.*: *"//;s/"//')
    fi

    # Use session_name as display name if name is empty
    [ -z "$name" ] && name="$session_name"

    # Determine thumbnail: use best iteration screenshot or reference image
    thumbnail=""
    # Check for final output screenshot first
    if [ -f "$session_dir/final/output.svg" ]; then
        thumbnail="$session_name/output.svg"
    fi
    # Fall back to last iteration screenshot
    if [ -z "$thumbnail" ]; then
        last_screenshot=$(ls -1 "$session_dir"/iterations/*/screenshot.png 2>/dev/null | tail -1)
        if [ -n "$last_screenshot" ]; then
            iter_num=$(basename "$(dirname "$last_screenshot")")
            thumbnail="$session_name/iterations/$iter_num/screenshot.png"
        fi
    fi

    # Check for timelapse GIF
    timelapse_gif=""
    if [ -f "$GALLERY_DIR/$session_name/timelapse.gif" ]; then
        timelapse_gif="$session_name/timelapse.gif"
    elif [ -f "$session_dir/final/timelapse.gif" ]; then
        timelapse_gif="$session_name/timelapse.gif"
    fi

    # Build JSON entry
    if ! $FIRST; then
        SESSIONS_JSON+=","
    fi
    FIRST=false

    SESSIONS_JSON+=$(cat <<ENTRY
{"name":"$name","url":"$session_name/index.html","pattern_type":"$pattern_type","symmetry_group":"$symmetry_group","confidence_score":$confidence_score,"status":"$status","thumbnail":"$thumbnail","timelapse_gif":"$timelapse_gif"}
ENTRY
)
done

SESSIONS_JSON+="]"

# Read template and substitute placeholders
mkdir -p "$(dirname "$OUTPUT")"
sed "s|{{SESSIONS_JSON}}|$SESSIONS_JSON|; s|{{DRAWINGS_JSON}}|[]|" "$TEMPLATE" > "$OUTPUT"

echo "Gallery index generated at $OUTPUT with $(echo "$SESSIONS_JSON" | grep -o '"name"' | wc -l | tr -d ' ') sessions"
