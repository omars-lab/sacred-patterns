#!/bin/bash
# iteration-validate.sh — Orchestrator for the validation signal stack.
#
# Runs every analytical signal in the iteration loop and emits a single
# validation.json that the iteration loop reads for go/no-go decisions.
#
# Signals invoked (in order):
#   1. validate-svg.sh on the recon SVG          — XML preflight
#   2. qiyas pixel-diff recon vs reference-traced — pixel similarity (SVG-vs-SVG)
#   3. qiyas pixel-diff recon vs reference image  — pixel similarity (SVG-vs-photo)
#   4. qiyas svg-audit [--baseline ...]          — A1/A2/A4/A5/A6 architectural audit
#   5. qiyas-diff.py recon vs reference image    — Hungarian shape matching
#   6. qiyas score (rollup of 2/3/5)             — composite + ranked warnings (best-effort)
#
# Usage:
#   ./tools/iteration-validate.sh \
#       --svg iterations/05/output.svg \
#       --reference input/reference.jpg \
#       [--reference-traced input/reference-traced.svg] \
#       [--baseline input/baseline.json] \
#       --out iterations/05/validation/
#
# Output: <out-dir>/validation.json plus per-tool subdirectories.
#
# This is the contract documented in docs/validation-json-schema.md.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

QIYAS_IMAGE="${QIYAS_IMAGE:-ghcr.io/naqshcoffee/qiyas:v0.1.1}"

SVG=""
REFERENCE=""
REFERENCE_TRACED=""
BASELINE=""
OUT=""
SKIP_QIYAS=0
AUTO_CAPTURE_ON_GO=0
AUTO_CAPTURE_ROOT=""
AUTO_CAPTURE_LABEL=""
# B1 Option A (qiyas#398): render.svg-direct path. Default-on; encode reads
# the bikar render.svg via qiyas's SVG fast-path instead of rasterize→trace.
# --no-svg-direct restores the legacy raster path (escape hatch for fast-path
# regressions on a specific input; remove once #399 count-fidelity calibration
# lands and the SVG fast-path is unconditionally superior).
SVG_DIRECT=1

# Run a qiyas subcommand inside Docker. Stages both inputs into the output
# dir under stable filenames (in_a.<ext>, in_b.<ext>), then mounts only the
# output dir. Staging avoids two issues: (a) Docker volume mounts on Dropbox-
# backed paths can fail with "Resource deadlock avoided" when ImageMagick
# tries to read large files; (b) we'd otherwise need separate mounts per
# input parent dir, which is brittle.
# Args: <subcommand> <input_a> <input_b> <out_dir> [extra args...]
qiyas_docker() {
    local subcmd="$1"; shift
    local input_a="$1"; shift
    local input_b="$1"; shift
    local out_dir="$1"; shift

    local out_abs
    out_abs="$(cd "$out_dir" && pwd)"

    local a_ext="${input_a##*.}"
    local b_ext="${input_b##*.}"
    local staged_a="$out_abs/in_a.$a_ext"
    local staged_b="$out_abs/in_b.$b_ext"

    cp "$input_a" "$staged_a"
    cp "$input_b" "$staged_b"

    docker run --rm \
        -v "$out_abs:/work" \
        "$QIYAS_IMAGE" \
        "$subcmd" "/work/in_a.$a_ext" "/work/in_b.$b_ext" --out /work "$@"

    local rc=$?
    rm -f "$staged_a" "$staged_b"
    return $rc
}

usage() {
    cat <<EOF
Usage: $0 --svg PATH --reference PATH --out DIR [options]

Required:
  --svg PATH                 Iteration output SVG
  --reference PATH           Reference image (JPG/PNG)
  --out DIR                  Output directory for validation.json

Optional:
  --reference-traced PATH    VTracer-traced reference SVG (enables 2nd pixel-diff)
  --baseline PATH            baseline.json from interpret-pattern (enables A6)
  --skip-qiyas               Skip qiyas validate (Docker not available)
  --svg-direct               (default) Use qiyas SVG fast-path for svg-audit
                             encode step (qiyas#398 — bypasses rasterize→trace
                             round-trip when the recon SVG is bikar's render.svg)
  --no-svg-direct            Force the legacy raster encode path (escape hatch
                             for fast-path regressions; remove once #399 lands)
  --auto-capture-on-go       After rollup, if validation.json overall.go_no_go
                             is GO, run 'qiyas fixtures capture' against the
                             recon SVG so converged sessions land in the qiyas
                             edge-case corpus automatically. Off by default.
                             V2.E (qiyas#77).
  --auto-capture-root DIR    Override the qiyas-checkout corpus root that
                             --auto-capture-on-go targets. Defaults to
                             \$QIYAS_CORPUS_ROOT or skips capture if neither
                             is set.
  --auto-capture-label SLUG  Override the fixture slug. Defaults to a slug
                             derived from the iteration directory name
                             (parent-of-validate-out plus -iterNN).
  -h, --help                 Show this help
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --svg) SVG="$2"; shift 2 ;;
        --reference) REFERENCE="$2"; shift 2 ;;
        --reference-traced) REFERENCE_TRACED="$2"; shift 2 ;;
        --baseline) BASELINE="$2"; shift 2 ;;
        --out) OUT="$2"; shift 2 ;;
        --skip-qiyas) SKIP_QIYAS=1; shift ;;
        --svg-direct) SVG_DIRECT=1; shift ;;
        --no-svg-direct) SVG_DIRECT=0; shift ;;
        --auto-capture-on-go) AUTO_CAPTURE_ON_GO=1; shift ;;
        --auto-capture-root) AUTO_CAPTURE_ROOT="$2"; shift 2 ;;
        --auto-capture-label) AUTO_CAPTURE_LABEL="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done

if [[ -z "$SVG" || -z "$REFERENCE" || -z "$OUT" ]]; then
    echo "Error: --svg, --reference, and --out are required" >&2
    usage
    exit 2
fi

[[ -f "$SVG" ]] || { echo "SVG not found: $SVG" >&2; exit 1; }
[[ -f "$REFERENCE" ]] || { echo "Reference not found: $REFERENCE" >&2; exit 1; }
[[ -z "$REFERENCE_TRACED" || -f "$REFERENCE_TRACED" ]] || \
    { echo "Reference-traced not found: $REFERENCE_TRACED" >&2; exit 1; }
[[ -z "$BASELINE" || -f "$BASELINE" ]] || \
    { echo "Baseline not found: $BASELINE" >&2; exit 1; }

mkdir -p "$OUT"

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${CYAN}iteration-validate${NC}"
echo "  SVG:        $SVG"
echo "  Reference:  $REFERENCE"
[[ -n "$REFERENCE_TRACED" ]] && echo "  Traced ref: $REFERENCE_TRACED"
[[ -n "$BASELINE" ]] && echo "  Baseline:   $BASELINE"
echo "  Output:     $OUT"
echo "  Encode:     primitives-source=$([[ "$SVG_DIRECT" -eq 1 ]] && echo "svg (B1 direct)" || echo "raster (legacy)")"
echo ""

# ============================================================
# 1. validate-svg.sh
# ============================================================
echo -e "${YELLOW}[1/6] validate-svg${NC}"
VALIDATE_LOG="$OUT/validate-svg.log"
VALIDATE_EXIT=0
"$SCRIPT_DIR/validate-svg.sh" "$SVG" >"$VALIDATE_LOG" 2>&1 || VALIDATE_EXIT=$?
echo "  exit $VALIDATE_EXIT (log: $VALIDATE_LOG)"

# ============================================================
# 2. qiyas pixel-diff vs reference-traced (optional)
# ============================================================
DIFF_TRACED_DIR=""
if [[ -n "$REFERENCE_TRACED" ]]; then
    echo -e "${YELLOW}[2/6] qiyas pixel-diff vs traced reference${NC}"
    DIFF_TRACED_DIR="$OUT/diff-vs-traced"
    mkdir -p "$DIFF_TRACED_DIR"
    qiyas_docker pixel-diff "$SVG" "$REFERENCE_TRACED" "$DIFF_TRACED_DIR" --rasterizer magick \
        >"$DIFF_TRACED_DIR.log" 2>&1 || echo "  (qiyas pixel-diff exited non-zero, continuing)"
else
    echo -e "${YELLOW}[2/6] qiyas pixel-diff vs traced reference — skipped (no --reference-traced)${NC}"
fi

# ============================================================
# 3. qiyas pixel-diff vs reference image
# ============================================================
echo -e "${YELLOW}[3/6] qiyas pixel-diff vs reference image${NC}"
DIFF_JPG_DIR="$OUT/diff-vs-jpg"
mkdir -p "$DIFF_JPG_DIR"
qiyas_docker pixel-diff "$SVG" "$REFERENCE" "$DIFF_JPG_DIR" --rasterizer magick \
    >"$DIFF_JPG_DIR.log" 2>&1 || echo "  (qiyas pixel-diff exited non-zero, continuing)"

# ============================================================
# 4. qiyas svg-audit (A1/A2/A4/A5/A6)
# ============================================================
# Two-step: (a) qiyas encode SVG → encoding.json; (b) qiyas svg-audit
# encoding.json → svg-audit.json. Baseline is passed through to enable A6 when
# present.
#
# B1 Option A (qiyas#398): when --svg-direct is set (the default), encode reads
# the bikar render.svg via qiyas's SVG fast-path (--primitives-source svg)
# instead of rasterize→trace. The legacy comment claimed "SVGs use clipPath
# which qiyas's SVG fast-path rejects" — empirically false as of 2026-05-21
# (verified against Petal-Full.svg with 24 clipPath elements: fast-path encodes
# 95 shapes cleanly, dominant_fold=6, conf=0.75). The round-trip cost was the
# fragmented-residue starvation root-caused in qiyas#371. --no-svg-direct keeps
# the legacy raster encode for regressions.
echo -e "${YELLOW}[4/6] qiyas svg-audit${NC}"
SVG_AUDIT_DIR="$OUT/svg-audit"
mkdir -p "$SVG_AUDIT_DIR"
svg_audit_abs="$(cd "$SVG_AUDIT_DIR" && pwd)"
svg_ext="${SVG##*.}"
cp "$SVG" "$svg_audit_abs/in.$svg_ext"
SVG_AUDIT_BASELINE_ARGS=()
if [[ -n "$BASELINE" ]]; then
    cp "$BASELINE" "$svg_audit_abs/baseline.json"
    SVG_AUDIT_BASELINE_ARGS=(--baseline /work/baseline.json)
fi
if [[ "$SVG_DIRECT" -eq 1 ]]; then
    ENCODE_PRIMITIVES_SOURCE="svg"
else
    ENCODE_PRIMITIVES_SOURCE="raster"
fi
{
    docker run --rm -v "$svg_audit_abs:/work" "$QIYAS_IMAGE" \
        encode "/work/in.$svg_ext" --primitives-source "$ENCODE_PRIMITIVES_SOURCE" -o /work/encoding.json &&
    docker run --rm -v "$svg_audit_abs:/work" "$QIYAS_IMAGE" \
        svg-audit /work/encoding.json --out /work ${SVG_AUDIT_BASELINE_ARGS[@]+"${SVG_AUDIT_BASELINE_ARGS[@]}"}
} >"$SVG_AUDIT_DIR/stdout.log" 2>&1 || \
    echo "  (qiyas svg-audit exited non-zero, continuing)"
rm -f "$svg_audit_abs/in.$svg_ext" "$svg_audit_abs/baseline.json"

# ============================================================
# 5. qiyas-diff
# ============================================================
QIYAS_DIR=""
QIYAS_RAN=0
if [[ "$SKIP_QIYAS" -eq 0 ]]; then
    echo -e "${YELLOW}[5/6] qiyas-diff${NC}"
    QIYAS_DIR="$OUT/qiyas"
    if "$SCRIPT_DIR/qiyas-diff.py" "$SVG" "$REFERENCE" "$QIYAS_DIR" \
            >"$QIYAS_DIR.log" 2>&1; then
        QIYAS_RAN=1
    else
        echo "  (qiyas-diff failed — see $QIYAS_DIR.log)"
    fi
else
    echo -e "${YELLOW}[5/6] qiyas-diff — skipped (--skip-qiyas)${NC}"
fi

# ============================================================
# 6. qiyas score (rollup of detector outputs into composite + ranked warnings)
# ============================================================
SCORE_DIR="$OUT/score"
SCORE_RAN=0
if [[ "$SKIP_QIYAS" -eq 0 ]]; then
    echo -e "${YELLOW}[6/6] qiyas score${NC}"
    mkdir -p "$SCORE_DIR"

    # Mount $OUT at /work and let qiyas score read each detector's output
    # by relative path. Best-effort: older qiyas images without `score`
    # exit non-zero, in which case the rollup proceeds without composite.
    SCORE_ARGS=(--output /work/score/score.json)
    [[ "$QIYAS_RAN" -eq 1 && -d "$QIYAS_DIR" ]] && \
        SCORE_ARGS+=(--validate-out "/work/$(basename "$QIYAS_DIR")")
    [[ -d "$DIFF_JPG_DIR" ]] && \
        SCORE_ARGS+=(--pixel-diff-out "/work/$(basename "$DIFF_JPG_DIR")")

    out_abs="$(cd "$OUT" && pwd)"
    if docker run --rm \
            -v "$out_abs:/work" \
            "$QIYAS_IMAGE" \
            score run "${SCORE_ARGS[@]}" \
            >"$SCORE_DIR.log" 2>&1; then
        SCORE_RAN=1
    else
        echo "  (qiyas score unavailable — older image or non-zero exit; see $SCORE_DIR.log)"
    fi
else
    echo -e "${YELLOW}[6/6] qiyas score — skipped (--skip-qiyas)${NC}"
fi

# ============================================================
# Roll up to validation.json
# ============================================================
echo ""
echo -e "${CYAN}Rolling up to validation.json...${NC}"

python3 "$SCRIPT_DIR/iteration-validate-rollup.py" \
    --svg "$SVG" \
    --reference "$REFERENCE" \
    ${REFERENCE_TRACED:+--reference-traced "$REFERENCE_TRACED"} \
    ${BASELINE:+--baseline "$BASELINE"} \
    --validate-svg-exit "$VALIDATE_EXIT" \
    --validate-svg-log "$VALIDATE_LOG" \
    ${DIFF_TRACED_DIR:+--diff-traced-dir "$DIFF_TRACED_DIR"} \
    --diff-jpg-dir "$DIFF_JPG_DIR" \
    --svg-audit-json "$SVG_AUDIT_DIR/svg-audit.json" \
    ${QIYAS_RAN:+--qiyas-ran $QIYAS_RAN} \
    ${QIYAS_DIR:+--qiyas-dir "$QIYAS_DIR"} \
    ${SCORE_RAN:+--qiyas-score-json "$SCORE_DIR/score.json"} \
    --out "$OUT/validation.json"

echo ""

# ============================================================
# Cross-iteration trajectory analysis (qiyas iter analyze)
# ============================================================
# After the per-iteration validation.json lands, walk every prior iteration's
# validation.json and emit iterations/iter.json — the trajectory+verdict
# rollup the iteration loop consumes for stagnation/regression detection
# (iteration-guide.md §"Stagnation Detection"). Best-effort: a missing CLI
# (older qiyas image) is logged, not fatal.
#
# Layout assumption: $OUT == iterations/{nn}/validation/, so the iterations
# root is two parents up. iter.json lands at iterations/iter.json.
ITER_ROOT="$(cd "$OUT/../.." && pwd)"
ITER_JSON="$ITER_ROOT/iter.json"

if [[ $SKIP_QIYAS -eq 0 ]]; then
    echo -e "${CYAN}Running qiyas iter analyze on $ITER_ROOT...${NC}"
    if docker run --rm \
        -v "$ITER_ROOT:/work" \
        "$QIYAS_IMAGE" \
        iter analyze /work --window 3 --out /work/iter.json \
        > "$ITER_ROOT/iter-analyze.log" 2>&1; then
        echo "  $ITER_JSON"
    else
        echo -e "${YELLOW}  iter analyze unavailable (older qiyas image?) — see $ITER_ROOT/iter-analyze.log${NC}"
    fi
else
    echo -e "${YELLOW}qiyas iter analyze — skipped (--skip-qiyas)${NC}"
fi

# ============================================================
# Auto-capture on GO (V2.E — qiyas#77)
# ============================================================
# When --auto-capture-on-go is set AND validation.json overall.go_no_go == GO,
# run `qiyas fixtures capture` against the recon SVG with --root pointing at
# an external qiyas checkout's edge-case corpus. The recon SVG (not the
# reference) is the fixture input so the corpus accumulates *what we actually
# converged on*, not what we were targeting.
if [[ $AUTO_CAPTURE_ON_GO -eq 1 && $SKIP_QIYAS -eq 0 ]]; then
    CAPTURE_ROOT="${AUTO_CAPTURE_ROOT:-${QIYAS_CORPUS_ROOT:-}}"
    if [[ -z "$CAPTURE_ROOT" ]]; then
        echo -e "${YELLOW}--auto-capture-on-go set but no --auto-capture-root or \$QIYAS_CORPUS_ROOT — skipping${NC}"
    elif [[ ! -d "$CAPTURE_ROOT" ]]; then
        echo -e "${YELLOW}--auto-capture-root $CAPTURE_ROOT does not exist — skipping${NC}"
    else
        GO_NO_GO="$(python3 -c "import json,sys; print(json.load(open('$OUT/validation.json'))['overall']['go_no_go'])" 2>/dev/null || echo "UNKNOWN")"
        if [[ "$GO_NO_GO" == "GO" ]]; then
            # Derive slug: <session-dir>-iter<NN> from iterations/<NN>/validation/.
            ITER_DIR="$(cd "$OUT/.." && pwd)"
            ITER_NUM="$(basename "$ITER_DIR")"
            SESSION_DIR="$(cd "$ITER_DIR/../.." && pwd)"
            SESSION_NAME="$(basename "$SESSION_DIR")"
            DEFAULT_SLUG="${SESSION_NAME}-iter${ITER_NUM}"
            SLUG="${AUTO_CAPTURE_LABEL:-$DEFAULT_SLUG}"
            # Normalize slug to fixtures-command grammar: lowercase alnum + hyphens.
            SLUG="$(echo "$SLUG" | tr '[:upper:]_' '[:lower:]-' | tr -cd '[:alnum:]-')"

            CAPTURE_ROOT_ABS="$(cd "$CAPTURE_ROOT" && pwd)"
            SVG_ABS="$(cd "$(dirname "$SVG")" && pwd)/$(basename "$SVG")"
            echo -e "${CYAN}Auto-capturing GO iteration to qiyas corpus...${NC}"
            echo "  slug: $SLUG"
            echo "  root: $CAPTURE_ROOT_ABS"
            CAPTURE_LOG="$OUT/auto-capture.log"
            if docker run --rm \
                    -v "$CAPTURE_ROOT_ABS:/corpus" \
                    -v "$(dirname "$SVG_ABS"):/recon" \
                    "$QIYAS_IMAGE" \
                    fixtures capture "/recon/$(basename "$SVG_ABS")" \
                        --label "$SLUG" \
                        --reason "auto-captured at GO (sacred-patterns iteration-validate.sh --auto-capture-on-go)" \
                        --root /corpus \
                    >"$CAPTURE_LOG" 2>&1; then
                echo -e "${GREEN}  captured: $CAPTURE_ROOT_ABS/$SLUG/${NC}"
            else
                echo -e "${YELLOW}  capture exited non-zero — see $CAPTURE_LOG${NC}"
            fi
        else
            echo "  --auto-capture-on-go: overall.go_no_go=$GO_NO_GO (not GO) — skipping capture"
        fi
    fi
fi

echo ""
echo -e "${GREEN}Validation complete${NC}"
echo "  $OUT/validation.json"
if [[ -f "$ITER_JSON" ]]; then
    echo "  $ITER_JSON"
fi
