#!/usr/bin/env bash
# score-backfill.sh — re-run iteration-validate.sh against historical
# iterations missing a validation/ subdir. Builds the calibration
# corpus needed for V2.B (#75 — global warning optimizer).
#
# Walks SESSION_DIR/iterations/<N>/, finds the iteration's SVG
# (output.svg or render.svg), and runs the orchestrator if no
# validation/validation.json exists yet.
#
# Usage:
#   tools/score-backfill.sh <session-dir> [--dry-run] [--limit N]
#
# Exits 0 on success (even if some iters fail individually — they're
# logged and skipped). Exits 1 only on argument or precondition errors.

set -euo pipefail

DRY_RUN=0
LIMIT=0
SESSION_DIR=""

while [ "$#" -gt 0 ]; do
    case "$1" in
        --dry-run) DRY_RUN=1; shift ;;
        --limit) LIMIT="$2"; shift 2 ;;
        -*) echo "unknown flag: $1" >&2; exit 1 ;;
        *)
            if [ -z "$SESSION_DIR" ]; then
                SESSION_DIR="$1"
                shift
            else
                echo "extra positional: $1" >&2; exit 1
            fi
            ;;
    esac
done

if [ -z "$SESSION_DIR" ]; then
    echo "usage: $0 <session-dir> [--dry-run] [--limit N]" >&2
    exit 1
fi

if [ ! -d "$SESSION_DIR/iterations" ]; then
    echo "[error] no iterations/ in $SESSION_DIR" >&2
    exit 1
fi

REFERENCE="$SESSION_DIR/input/reference.jpg"
BASELINE="$SESSION_DIR/input/baseline.json"
if [ ! -f "$REFERENCE" ]; then
    echo "[error] missing $REFERENCE" >&2; exit 1
fi
if [ ! -f "$BASELINE" ]; then
    echo "[error] missing $BASELINE" >&2; exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ORCH="$REPO_ROOT/tools/iteration-validate.sh"

echo "[start] session=$(basename "$SESSION_DIR")"
echo "        reference=$REFERENCE"
echo "        baseline=$BASELINE"
[ "$DRY_RUN" = "1" ] && echo "        DRY RUN — no orchestrator calls"

count=0
processed=0
failed=0
skipped=0
for d in $(ls -d "$SESSION_DIR/iterations"/[0-9]* 2>/dev/null \
           | awk -F/ '{print $NF"\t"$0}' | sort -k1,1n | cut -f2-); do
    n=$(basename "$d")
    if [ -f "$d/validation/validation.json" ]; then
        skipped=$((skipped + 1))
        continue
    fi

    # Find the SVG: prefer render.svg (BIKAR), fall back to output.svg (D3).
    svg=""
    if [ -f "$d/render.svg" ]; then
        svg="$d/render.svg"
    elif [ -f "$d/output.svg" ]; then
        svg="$d/output.svg"
    fi

    if [ -z "$svg" ]; then
        echo "[skip $n] no svg (render.svg or output.svg)"
        skipped=$((skipped + 1))
        continue
    fi

    count=$((count + 1))
    if [ "$LIMIT" -gt 0 ] && [ "$count" -gt "$LIMIT" ]; then
        echo "[stop] hit --limit $LIMIT"
        break
    fi

    echo "[backfill $n] svg=$(basename "$svg")"
    if [ "$DRY_RUN" = "1" ]; then
        continue
    fi

    if "$ORCH" --svg "$svg" \
               --reference "$REFERENCE" \
               --baseline "$BASELINE" \
               --out "$d/validation" >> "$d/backfill.log" 2>&1; then
        processed=$((processed + 1))
    else
        failed=$((failed + 1))
        echo "[fail $n] orchestrator returned non-zero; see $d/backfill.log"
    fi
done

echo "[done] processed=$processed failed=$failed skipped=$skipped"
