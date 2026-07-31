#!/usr/bin/env sh
# Tests for gen-decision-ledger-xrepo.sh, and specifically for the one thing it
# used to get wrong: `[ -d "$dir" ] || continue` treated an unclonedd sibling repo
# as a repo with no decisions. Write mode then rendered a join missing every row
# from that repo, into a committed file headed `GENERATED ... do not edit`.
#
# Case 2 below is the witness. Against the previous script it exits 0 and
# truncates the ledger; against this one it exits 1 and leaves the file byte-
# identical. Cases 3 and 4 pin the deliberate asymmetry: --check may skip when
# it cannot see all three repos, because "cannot verify" must not block a commit
# in one repo on the other two being present — and it is only safe to skip
# because write mode can no longer produce the file it would have caught.
#
# The script derives its sibling root as `dirname($0)/../..`, so each case is
# run from a throwaway tree laid out the way the three repos are on disk.
#
# Usage: sh scripts/gen-decision-ledger-xrepo.test.sh
# Prereqs: yq (mikefarah v4+), same as the script under test.

set -eu

SP_ROOT=$(cd "$(dirname "$0")/.." && pwd)
SCRIPT="$SP_ROOT/scripts/gen-decision-ledger-xrepo.sh"

if ! command -v yq >/dev/null 2>&1; then
  echo "gen-decision-ledger-xrepo.test: yq not found. Install: brew install yq" >&2
  exit 1
fi

fails=0
ok()   { echo "  ok   — $1"; }
fail() { echo "  FAIL — $1" >&2; fails=$((fails + 1)); }

# Lay out <root>/{qiyas,bikar,sacred-patterns}, each with docs/decisions/, and
# put a copy of the script where the real one lives. `repos` names which of the
# three siblings to create; the rest are simply absent.
scaffold() {
  root=$(mktemp -d)
  mkdir -p "$root/sacred-patterns/scripts" "$root/sacred-patterns/docs/decisions"
  cp "$SCRIPT" "$root/sacred-patterns/scripts/"
  for repo in $1; do
    mkdir -p "$root/$repo/docs/decisions"
    cat >"$root/$repo/docs/decisions/2026-01-01-$repo-thing.md" <<EOF
---
tag: $repo-tag
status_token: ACCEPTED
picked_option: A
---

# $repo decision
EOF
  done
  printf '%s' "$root"
}

run() { sh "$1/sacred-patterns/scripts/gen-decision-ledger-xrepo.sh" ${2:-} >"$1/out" 2>"$1/err"; }

echo "gen-decision-ledger-xrepo.test"

# 1 — the happy path: all three present, every repo contributes a row.
root=$(scaffold "qiyas bikar sacred-patterns")
if run "$root" && grep -q 'qiyas-tag' "$root/sacred-patterns/docs/decisions/LEDGER-XREPO.md" &&
  grep -q 'bikar-tag' "$root/sacred-patterns/docs/decisions/LEDGER-XREPO.md"; then
  ok "writes a row per repo when all three are present"
else
  fail "complete tree should render rows from every repo"
fi
rm -rf "$root"

# 2 — THE WITNESS. bikar absent. The pre-existing ledger must survive untouched.
root=$(scaffold "qiyas sacred-patterns")
ledger="$root/sacred-patterns/docs/decisions/LEDGER-XREPO.md"
printf 'PRE-EXISTING LEDGER WITH BIKAR ROWS\n' >"$ledger"
before=$(cat "$ledger")
if run "$root"; then
  fail "write mode should refuse when a sibling repo is missing (it exited 0)"
else
  ok "write mode refuses when a sibling repo is missing"
fi
if [ "$(cat "$ledger")" = "$before" ]; then
  ok "the refusal left the committed ledger byte-identical"
else
  fail "write mode overwrote the ledger with a partial join"
fi
grep -q 'REFUSING' "$root/err" || fail "the refusal should say so on stderr"
rm -rf "$root"

# 3 — same incomplete tree, --check: skips, exits 0, and says it skipped.
root=$(scaffold "qiyas sacred-patterns")
if run "$root" --check; then
  ok "--check exits 0 when it cannot see all three repos"
else
  fail "--check should skip, not fail, on an incomplete checkout"
fi
grep -q 'SKIPPED' "$root/err" || fail "--check should announce the skip on stderr"
rm -rf "$root"

# 4 — complete tree, stale ledger: --check still catches it. (Guards against
# "fixed the skip by making --check never fail".)
root=$(scaffold "qiyas bikar sacred-patterns")
printf 'stale\n' >"$root/sacred-patterns/docs/decisions/LEDGER-XREPO.md"
if run "$root" --check; then
  fail "--check should report a stale ledger on a complete tree"
else
  ok "--check still reports a stale ledger when all three are present"
fi
rm -rf "$root"

if [ "$fails" -ne 0 ]; then
  echo "$fails assertion(s) failed" >&2
  exit 1
fi
echo "all assertions passed"
