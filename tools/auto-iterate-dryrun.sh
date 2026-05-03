#!/usr/bin/env bash
# auto-iterate-dryrun.sh — Phase 0 of the auto-iterate plan.
# Reads the latest validation.json under SESSION_DIR/iterations/ and prints
# overall.* + warnings[0]. No edits, no loop. Smoke test for data plumbing.
#
# Usage: tools/auto-iterate-dryrun.sh <session-dir>
#
# Exits 0 on success. Exits 1 if the session has no validated iteration.

set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <session-dir>" >&2
    exit 2
fi

SESSION_DIR="$1"

if [ ! -d "$SESSION_DIR/iterations" ]; then
    echo "no iterations/ in $SESSION_DIR" >&2
    exit 1
fi

# Find the highest-numbered iteration with validation/validation.json.
LATEST=$(find "$SESSION_DIR/iterations" -mindepth 2 -maxdepth 3 -type f \
    -path '*/validation/validation.json' 2>/dev/null \
    | awk -F/ '{n=$(NF-2); print n"\t"$0}' \
    | sort -k1,1 -n \
    | tail -1 \
    | cut -f2-)

if [ -z "$LATEST" ]; then
    echo "no validation.json under $SESSION_DIR/iterations/*/validation/" >&2
    exit 1
fi

ITER_DIR=$(dirname "$(dirname "$LATEST")")
ITER_N=$(basename "$ITER_DIR")

echo "session:    $SESSION_DIR"
echo "iteration:  $ITER_N"
echo "validation: $LATEST"
echo

python3 - "$LATEST" <<'PY'
import json, sys
with open(sys.argv[1]) as f:
    v = json.load(f)
o = v.get("overall", {})

def line(k, default="-"):
    val = o.get(k, default)
    print(f"  {k:22s} {val}")

print("=== overall ===")
for k in ("topology_complete", "structural_score", "pixel_similarity",
         "composite_score", "go_no_go"):
    line(k)
print()

blockers = o.get("blocking_issues") or []
print(f"=== blocking_issues ({len(blockers)}) ===")
for b in blockers:
    print(f"  - {b}")
print()

warnings = o.get("warnings") or []
print(f"=== warnings ({len(warnings)} total; showing top 1) ===")
if warnings:
    w = warnings[0]
    print(f"  id:       {w.get('id')}")
    print(f"  source:   {w.get('source')}")
    print(f"  severity: {w.get('severity')}")
    print(f"  delta:    {w.get('counterfactual_score_delta')}")
    msg = w.get('message') or '-'
    print(f"  message:  {msg}")
    cf = (w.get('context') or {}).get('counterfactual_rationale')
    if cf:
        print(f"  rationale: {cf}")
else:
    print("  (none — qiyas score may be unavailable; check blocking_issues)")
PY
