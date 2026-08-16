#!/usr/bin/env sh
# Tests for gen-decision-ledger-xrepo.sh, and specifically for the two things it
# has been caught getting wrong.
#
# The first: `[ -d "$dir" ] || continue` treated an uncloned sibling repo as a
# repo with no decisions. Write mode then rendered a join missing every row from
# that repo, into a committed file headed `GENERATED ... do not edit`. Case 2 is
# that witness. Against the pre-fix script it exits 0 and truncates the ledger;
# against this one it exits 1 and leaves the file byte-identical. Cases 3 and 4
# pin the deliberate asymmetry: --check may skip when it cannot see all three
# repos, because "cannot verify" must not block a commit in one repo on the
# other two being present — and it is only safe to skip because write mode can
# no longer produce the file it would have caught.
#
# The second: siblings were read from their WORKING TREES, so this generator's
# output was a function of whichever branch somebody else's session happened to
# have checked out, and of any edit they had not committed yet. Case 5 is that
# witness, and it is the load-bearing one — it is a by-design failure rather
# than an absence, so nothing about it shows up as a missing input. Case 6 pins
# the discovery half: a linked worktree must resolve the same siblings the
# primary checkout does, wherever on disk it was created.
#
# Each case is run from a throwaway tree laid out the way the three repos are on
# disk. The siblings are real git repos with a local `refs/remotes/origin/*` —
# no network, no remote, but the same ref names the script resolves in anger.
#
# Usage: sh scripts/gen-decision-ledger-xrepo.test.sh
# Prereqs: yq (mikefarah v4+) and git, same as the script under test.

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
#
# Every scaffolded repo is a real git repo, and each sibling gets a local
# `refs/remotes/origin/main` plus an `origin/HEAD` pointing at it. That is the
# whole state the script resolves — no remote is configured and nothing touches
# the network. sacred-patterns is a git repo too, because the script derives the
# sibling root from `git rev-parse --git-common-dir`; scaffolding it as a plain
# directory would exercise the fallback instead of the path that runs in anger.
# --no-verify because a scaffold commit is test fixture, not authorship: without
# it the machine's own hooks (gitleaks, coherence gates) run once per scaffolded
# repo per case, which is both slow and a way for this suite's result to depend
# on the host's global git config — the same class of coupling case 5 exists to
# kill, one layer down.
git_init() {
  git -C "$1" init -q
  git -C "$1" add -A
  git -C "$1" -c user.email=t@t -c user.name=t commit -q --no-verify -m scaffold
}

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
    if [ "$repo" != "sacred-patterns" ]; then
      git_init "$root/$repo"
      git -C "$root/$repo" update-ref refs/remotes/origin/main HEAD
      git -C "$root/$repo" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
    fi
  done
  git_init "$root/sacred-patterns"
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

# 5 — THE LOAD-BEARING WITNESS. A sibling's working tree disagrees with its
# origin ref: `status_token: ACCEPTED` flipped to `DEAD`, uncommitted. This is
# the by-design failure, and it is by-design precisely because nothing is
# missing — every repo is present, every doc parses, and the generator that
# reads working trees produces a confident, wrong, committed file. The tag also
# loses its ★, so the roll-up stops naming an authoritative doc that is still
# authoritative on the branch everyone else sees.
root=$(scaffold "qiyas bikar sacred-patterns")
doc="$root/bikar/docs/decisions/2026-01-01-bikar-thing.md"
sed 's/^status_token: ACCEPTED$/status_token: DEAD/' "$doc" >"$doc.tmp" && mv "$doc.tmp" "$doc"
grep -q '^status_token: DEAD$' "$doc" || fail "test setup: the uncommitted flip did not apply"
ledger="$root/sacred-patterns/docs/decisions/LEDGER-XREPO.md"
if run "$root"; then
  bikar_row=$(grep 'bikar-tag' "$ledger" || true)
  case "$bikar_row" in
    *DEAD*) fail "an UNCOMMITTED sibling edit reached the generated ledger: $bikar_row" ;;
    *ACCEPTED*) ok "a sibling's uncommitted edit does not reach the ledger (read at the ref)" ;;
    *) fail "expected a bikar-tag row, got: ${bikar_row:-<none>}" ;;
  esac
  case "$bikar_row" in
    *'★'*) ok "the tag keeps its authoritative marker" ;;
    *) fail "the authoritative ★ was lost: $bikar_row" ;;
  esac
else
  fail "write mode should succeed on a complete tree (exit $?); stderr: $(cat "$root/err")"
fi
grep -q 'bikar read at origin/main' "$root/err" ||
  fail "the run should name the ref it read each sibling at, on stderr"
grep -q '<!-- inputs: .*bikar origin/main' "$ledger" ||
  fail "the ledger should record which ref each sibling was read at"
rm -rf "$root"

# 6 — discovery must not depend on where the worktree was made. A linked
# worktree created OUTSIDE the sibling root used to see no siblings at all,
# because the root was `$SP_ROOT/..`. Same repos, same rows, different cwd.
root=$(scaffold "qiyas bikar sacred-patterns")
outside=$(mktemp -d)
if git -C "$root/sacred-patterns" worktree add -q --detach "$outside/wt" HEAD 2>"$root/wt-err"; then
  if sh "$outside/wt/scripts/gen-decision-ledger-xrepo.sh" >"$root/out" 2>"$root/err"; then
    wt_ledger="$outside/wt/docs/decisions/LEDGER-XREPO.md"
    if grep -q 'qiyas-tag' "$wt_ledger" && grep -q 'bikar-tag' "$wt_ledger"; then
      ok "a worktree outside the sibling root resolves the same siblings"
    else
      fail "worktree run dropped sibling rows"
    fi
  else
    fail "worktree run should succeed; stderr: $(cat "$root/err")"
  fi
  git -C "$root/sacred-patterns" worktree remove --force "$outside/wt" >/dev/null 2>&1 || true
else
  fail "test setup: could not create a worktree: $(cat "$root/wt-err")"
fi
rm -rf "$root" "$outside"

if [ "$fails" -ne 0 ]; then
  echo "$fails assertion(s) failed" >&2
  exit 1
fi
echo "all assertions passed"
