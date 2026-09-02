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
# The third is the join 3d-models' D-049 §3 asked for: its one-file decisions
# log is indexed by heading, links only, and a `D-0xx` cited anywhere that is
# neither a heading there nor a file in bikar's docs/decisions/ blocks. Case 8
# is that witness — a citation committed on bikar's ref that resolves nowhere
# must refuse in both modes and leave the ledger untouched — and case 9 pins
# the half of the rule the pointer gates already know: a citation that exists
# only in a sibling's WORKING TREE is not a citation yet, because the ref is
# what is read. Cases 10 and 11 pin the two resolutions (a heading, a bikar
# file); cases 12 and 13 pin the missing-input shapes the fourth repo adds.
#
# Each case is run from a throwaway tree laid out the way the four repos are on
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

# Lay out <root>/{qiyas,bikar,3d-models,sacred-patterns} — docs/decisions/ for
# the three frontmatter repos, docs/decisions-log.md with two `## D-0xx — `
# headings for 3d-models — and put a copy of the script where the real one
# lives. `repos` names which siblings to create; the rest are simply absent.
# 3d-models also gets an origin URL (never fetched): the index links out to
# the browsable file, and the script derives that from the remote.
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
    if [ "$repo" = "3d-models" ]; then
      mkdir -p "$root/3d-models/docs"
      cat >"$root/3d-models/docs/decisions-log.md" <<EOF
# Decisions

## D-001 — First thing, with \`code\` in it

Body.

## D-002 — Second thing — with a dash of its own

Body.
EOF
      # The script under test cites 3d-models decisions in its own comments,
      # and it is a tracked file of the scaffolded sacred-patterns — so those
      # citations are held to the rule like any other, and the fixture log
      # carries a heading for each. Computed, not listed: a comment edit that
      # cites a new decision must not turn this suite red for a wrong reason.
      for cited in $(grep -o -E 'D-0[0-9]{2}' "$SCRIPT" | sort -u); do
        case "$cited" in D-001 | D-002) continue ;; esac
        printf '\n## %s — Cited by the generator'\''s own comments\n\nBody.\n' "$cited" \
          >>"$root/3d-models/docs/decisions-log.md"
      done
      git_init "$root/3d-models"
      git -C "$root/3d-models" remote add origin git@github.com:omars-lab/3d-models.git
      git -C "$root/3d-models" update-ref refs/remotes/origin/main HEAD
      git -C "$root/3d-models" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
      continue
    fi
    mkdir -p "$root/$repo/docs/decisions"
    cat >"$root/$repo/docs/decisions/2026-01-01-$repo-thing.md" <<EOF
---
tag: $repo-tag
status_token: ACCEPTED
picked_option: A
---

# $repo decision

Cites 3d-models D-001, which resolves.
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

# commit_to_ref <repo-dir> — commit the working tree and move origin/main onto
# it, so a fixture edit becomes what the script reads.
commit_to_ref() {
  git -C "$1" add -A
  git -C "$1" -c user.email=t@t -c user.name=t commit -q --no-verify -m edit
  git -C "$1" update-ref refs/remotes/origin/main HEAD
}

ALL="qiyas bikar 3d-models sacred-patterns"

echo "gen-decision-ledger-xrepo.test"

# 1 — the happy path: all four present, every repo contributes a row.
root=$(scaffold "$ALL")
if run "$root" && grep -q 'qiyas-tag' "$root/sacred-patterns/docs/decisions/LEDGER-XREPO.md" &&
  grep -q 'bikar-tag' "$root/sacred-patterns/docs/decisions/LEDGER-XREPO.md"; then
  ok "writes a row per repo when all four are present"
else
  fail "complete tree should render rows from every repo; stderr: $(cat "$root/err")"
fi
rm -rf "$root"

# 2 — THE WITNESS. bikar absent. The pre-existing ledger must survive untouched.
root=$(scaffold "qiyas 3d-models sacred-patterns")
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
root=$(scaffold "qiyas 3d-models sacred-patterns")
if run "$root" --check; then
  ok "--check exits 0 when it cannot see all four repos"
else
  fail "--check should skip, not fail, on an incomplete checkout"
fi
grep -q 'SKIPPED' "$root/err" || fail "--check should announce the skip on stderr"
rm -rf "$root"

# 4 — complete tree, stale ledger: --check still catches it. (Guards against
# "fixed the skip by making --check never fail".)
root=$(scaffold "$ALL")
printf 'stale\n' >"$root/sacred-patterns/docs/decisions/LEDGER-XREPO.md"
if run "$root" --check; then
  fail "--check should report a stale ledger on a complete tree"
else
  ok "--check still reports a stale ledger when all four are present"
fi
rm -rf "$root"

# 5 — THE LOAD-BEARING WITNESS. A sibling's working tree disagrees with its
# origin ref: `status_token: ACCEPTED` flipped to `DEAD`, uncommitted. This is
# the by-design failure, and it is by-design precisely because nothing is
# missing — every repo is present, every doc parses, and the generator that
# reads working trees produces a confident, wrong, committed file. The tag also
# loses its ★, so the roll-up stops naming an authoritative doc that is still
# authoritative on the branch everyone else sees.
root=$(scaffold "$ALL")
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
root=$(scaffold "$ALL")
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

# 7 — the 3d-models index: one row per heading, linking to the heading's
# GitHub fragment on the browsable file at the ref that was read. The two
# fixture headings are the two shapes the real log has — inline code, and a
# title carrying its own dash past the id's.
root=$(scaffold "$ALL")
ledger="$root/sacred-patterns/docs/decisions/LEDGER-XREPO.md"
if run "$root"; then
  grep -q '^| D-001 | \[First thing, with `code` in it\](https://github.com/omars-lab/3d-models/blob/main/docs/decisions-log.md#d-001--first-thing-with-code-in-it) |$' "$ledger" &&
    ok "a heading becomes one linked row, id and title, nothing copied" ||
    fail "D-001 row missing or mis-linked: $(grep 'D-001' "$ledger" || echo '<none>')"
  grep -q '#d-002--second-thing--with-a-dash-of-its-own) |$' "$ledger" &&
    ok "a title with its own dash keeps it, and the anchor drops it the way GitHub does" ||
    fail "D-002 anchor wrong: $(grep 'D-002' "$ledger" || echo '<none>')"
  grep -q '<!-- inputs: .*3d-models origin/main' "$ledger" ||
    fail "the ledger should record the ref 3d-models was read at"
else
  fail "write mode should succeed on a complete tree; stderr: $(cat "$root/err")"
fi
rm -rf "$root"

# 8 — THE D-049 WITNESS. bikar's ref cites D-077; no such heading, no such
# file. Both modes must refuse, name the repo and the number, and leave the
# committed ledger byte-identical — a broken reference is not staleness, and
# no regeneration repairs it.
root=$(scaffold "$ALL")
ledger="$root/sacred-patterns/docs/decisions/LEDGER-XREPO.md"
run "$root" || fail "test setup: the complete tree should generate first"
before=$(cat "$ledger")
printf '\nAlso D-077, which resolves nowhere.\n' >>"$root/bikar/docs/decisions/2026-01-01-bikar-thing.md"
commit_to_ref "$root/bikar"
if run "$root"; then
  fail "write mode should refuse a D-number that resolves in neither repo"
else
  ok "write mode refuses a dangling D-number"
fi
grep -q 'bikar (origin/main) cites D-077' "$root/err" ||
  fail "the refusal should name the citing repo, its ref and the number; stderr: $(cat "$root/err")"
[ "$(cat "$ledger")" = "$before" ] && ok "the refusal left the ledger byte-identical" ||
  fail "a dangling citation reached the committed ledger"
if run "$root" --check; then
  fail "--check should fail on a dangling D-number, not skip"
else
  ok "--check blocks on the same dangling D-number"
fi
rm -rf "$root"

# 9 — the ref discipline holds for citations too: the same D-077 written into
# bikar's WORKING TREE and not committed is somebody's in-flight work, not a
# reference this ledger can see.
root=$(scaffold "$ALL")
printf '\nAlso D-077, uncommitted.\n' >>"$root/bikar/docs/decisions/2026-01-01-bikar-thing.md"
if run "$root"; then
  ok "an uncommitted sibling citation does not block (read at the ref)"
else
  fail "working-tree-only citation should not block; stderr: $(cat "$root/err")"
fi
rm -rf "$root"

# 10 — a citation this repo makes is held to the same rule, from its working
# tree, because that is what this repo is read from.
root=$(scaffold "$ALL")
printf '\nCites D-088.\n' >>"$root/sacred-patterns/docs/decisions/2026-01-01-sacred-patterns-thing.md"
if run "$root"; then
  fail "a dangling citation in this worktree should refuse"
else
  grep -q 'sacred-patterns (this worktree) cites D-088' "$root/err" &&
    ok "a dangling citation in this worktree refuses and is named" ||
    fail "wrong refusal: $(cat "$root/err")"
fi
rm -rf "$root"

# 11 — the second home D-049 §3 allows: a D-number that names a file in
# bikar's docs/decisions/ resolves, heading or no heading.
root=$(scaffold "$ALL")
cat >"$root/bikar/docs/decisions/2026-01-02-D-077-in-bikar.md" <<EOF
---
tag: bikar-second
status_token: ACCEPTED
picked_option: A
---

# D-077 lives here as a file
EOF
commit_to_ref "$root/bikar"
if run "$root"; then
  ok "a D-number that names a bikar decision file resolves"
else
  fail "bikar-file resolution failed; stderr: $(cat "$root/err")"
fi
rm -rf "$root"

# 12 — 3d-models absent: the resolver is unknown, so the same asymmetry as
# case 2/3 — write refuses naming the repo, --check skips loudly.
root=$(scaffold "qiyas bikar sacred-patterns")
if run "$root"; then
  fail "write mode should refuse when 3d-models is missing"
else
  grep -q '3d-models (not cloned' "$root/err" && ok "write mode refuses when 3d-models is missing, and says which" ||
    fail "refusal should name 3d-models: $(cat "$root/err")"
fi
run "$root" --check && grep -q 'SKIPPED' "$root/err" && ok "--check skips when 3d-models is missing" ||
  fail "--check should skip on a missing 3d-models"
rm -rf "$root"

# 13 — a log with no headings is unreadable input, not a repo with no
# decisions (Tenet 29): the index must not quietly become empty.
root=$(scaffold "$ALL")
printf '# Decisions\n\nNo headings of the expected shape.\n' >"$root/3d-models/docs/decisions-log.md"
commit_to_ref "$root/3d-models"
if run "$root"; then
  fail "a headingless log should refuse, not render an empty index"
else
  grep -q 'has no `## D-0xx — ` headings' "$root/err" && ok "a headingless log refuses and says why" ||
    fail "wrong refusal for a headingless log: $(cat "$root/err")"
fi
rm -rf "$root"

# 14 — the citation scan excludes this suite's own file, for the same reason it
# excludes LEDGER-XREPO.md: the test scaffold plants deliberately-dangling
# D-numbers to prove the check fires (cases 8-10). Those are fixtures, not
# citations, and the scan must not read its own test data as a repo citing
# nowhere. Regression witness: against the pre-fix script this D-099 blocks.
root=$(scaffold "$ALL")
mkdir -p "$root/sacred-patterns/scripts"
printf '#!/bin/sh\n# fixture cites D-099, which resolves nowhere.\n' \
  >"$root/sacred-patterns/scripts/gen-decision-ledger-xrepo.test.sh"
commit_to_ref "$root/sacred-patterns"
if run "$root"; then
  ok "a dangling D-number in the test scaffold is excluded, not blocked"
else
  fail "test-scaffold fixtures must be excluded from the citation scan; stderr: $(cat "$root/err")"
fi
rm -rf "$root"

if [ "$fails" -ne 0 ]; then
  echo "$fails assertion(s) failed" >&2
  exit 1
fi
echo "all assertions passed"
