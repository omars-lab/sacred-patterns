#!/bin/bash
# validate-svg.sh — Validate structural integrity of SVG files
#
# Usage:
#   ./tools/validate-svg.sh path/to/file.svg
#   ./tools/validate-svg.sh path/to/dir/    # validates all .svg files in dir
#
# Checks:
#   1. File starts with <svg (no wrapper text like # or {)
#   2. File ends with </svg>
#   3. Contains xmlns="http://www.w3.org/2000/svg" (required for browser rendering)
#   4. Valid XML structure (xmllint if available)
#   5. Contains at least one visual element (polygon, path, circle, rect, line, etc.)
#   6. No markdown/JSON wrapper artifacts
#
# Exit codes:
#   0 — all files valid
#   1 — one or more files invalid
#   2 — usage error

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

pass() { echo -e "  ${GREEN}PASS${NC} $1"; }
fail() { echo -e "  ${RED}FAIL${NC} $1"; ERRORS=$((ERRORS + 1)); }
warn() { echo -e "  ${YELLOW}WARN${NC} $1"; }

validate_svg() {
    local file="$1"
    local ERRORS=0

    echo ""
    echo "Validating: $file"
    echo "---"

    # Check file exists and is not empty
    if [[ ! -f "$file" ]]; then
        fail "File does not exist"
        return 1
    fi

    if [[ ! -s "$file" ]]; then
        fail "File is empty"
        return 1
    fi

    local size
    size=$(wc -c < "$file" | tr -d ' ')
    echo "  Size: $size bytes"

    # 1. Starts with <svg (allow optional XML declaration or whitespace)
    local first_chars
    first_chars=$(head -c 200 "$file" | tr -d '\n' | sed 's/^[[:space:]]*//')
    if [[ "$first_chars" == "<?xml"* ]] || [[ "$first_chars" == "<svg"* ]]; then
        pass "Starts with valid SVG/XML declaration"
    elif [[ "$first_chars" == "#"* ]]; then
        fail "Starts with '#' — likely markdown wrapper (not raw SVG)"
    elif [[ "$first_chars" == "{"* ]]; then
        fail "Starts with '{' — likely JSON wrapper (not raw SVG)"
    elif [[ "$first_chars" == "\""* ]]; then
        fail "Starts with '\"' — likely JSON-encoded string (not raw SVG)"
    else
        fail "Does not start with <svg or <?xml — first chars: ${first_chars:0:40}"
    fi

    # 2. Ends with </svg>
    local last_chars
    last_chars=$(tail -c 20 "$file" | tr -d '\n' | sed 's/[[:space:]]*$//')
    if [[ "$last_chars" == *"</svg>" ]]; then
        pass "Ends with </svg>"
    else
        fail "Does not end with </svg> — last chars: $last_chars"
    fi

    # 3. Contains xmlns
    if grep -q 'xmlns="http://www.w3.org/2000/svg"' "$file"; then
        pass "Contains xmlns attribute (browser-renderable)"
    else
        fail "Missing xmlns=\"http://www.w3.org/2000/svg\" — browsers will render as HTML text"
        echo -e "       Fix: sed -i '' 's/<svg /<svg xmlns=\"http:\\/\\/www.w3.org\\/2000\\/svg\" /' $file"
    fi

    # 4. XML validity (if xmllint available)
    if command -v xmllint &>/dev/null; then
        if xmllint --noout "$file" 2>/dev/null; then
            pass "Valid XML structure (xmllint)"
        else
            fail "Invalid XML structure — xmllint errors:"
            xmllint --noout "$file" 2>&1 | head -5 | sed 's/^/       /'
        fi
    else
        warn "xmllint not available — skipping XML validation"
    fi

    # 5. Contains visual elements (use -o to count occurrences, not lines)
    local visual_count
    visual_count=$(grep -oE '<(polygon|path|circle|rect|line|ellipse|polyline|text|g)[[:space:]>]' "$file" 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$visual_count" -gt 0 ]]; then
        pass "Contains $visual_count visual elements (polygon/path/circle/rect/line/g/etc.)"
    else
        fail "No visual elements found (polygon, path, circle, rect, line, etc.)"
    fi

    # 6. Check for common wrapper artifacts
    if grep -q '```' "$file"; then
        fail "Contains markdown code fence (\`\`\`) — likely wrapper artifact"
    else
        pass "No markdown artifacts detected"
    fi

    if grep -q '"evaluate_script response"' "$file" 2>/dev/null; then
        fail "Contains evaluate_script tool wrapper text"
    fi

    # Summary
    echo "---"
    if [[ "$ERRORS" -eq 0 ]]; then
        echo -e "  ${GREEN}VALID${NC} — SVG is structurally sound"
        return 0
    else
        echo -e "  ${RED}INVALID${NC} — $ERRORS issue(s) found"
        return 1
    fi
}

# --- Main ---

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <file.svg | directory>"
    echo ""
    echo "Validate SVG file structure for browser rendering compatibility."
    echo "When given a directory, validates all .svg files within it."
    exit 2
fi

TOTAL_ERRORS=0
TOTAL_FILES=0

for arg in "$@"; do
    if [[ -d "$arg" ]]; then
        # Validate all SVGs in directory
        while IFS= read -r -d '' svgfile; do
            TOTAL_FILES=$((TOTAL_FILES + 1))
            if ! validate_svg "$svgfile"; then
                TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
            fi
        done < <(find "$arg" -name "*.svg" -print0)
    elif [[ -f "$arg" ]]; then
        TOTAL_FILES=$((TOTAL_FILES + 1))
        if ! validate_svg "$arg"; then
            TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
        fi
    else
        echo -e "${RED}ERROR${NC}: $arg is not a file or directory"
        TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
    fi
done

echo ""
echo "================================"
if [[ "$TOTAL_FILES" -eq 0 ]]; then
    echo "No SVG files found."
    exit 2
elif [[ "$TOTAL_ERRORS" -eq 0 ]]; then
    echo -e "${GREEN}All $TOTAL_FILES SVG file(s) valid.${NC}"
    exit 0
else
    echo -e "${RED}$TOTAL_ERRORS of $TOTAL_FILES SVG file(s) invalid.${NC}"
    exit 1
fi
