#!/usr/bin/env sh
# Generate docs/decisions/LEDGER-XREPO.md — the cross-repo roll-up of decided /
# dead / authoritative-per-tag across qiyas + bikar + sacred-patterns.
#
# Why a cross-repo roll-up: problem-tags span repos (face-class-identity lives
# in both qiyas and bikar; svg-direct's spine crosses qiyas + SP). A future
# session asking "has this tag been decided anywhere?" needs one place that
# joins all three repos' frontmatter. The per-repo LEDGER.md answers
# within-repo; this answers across.
#
# Reads ONLY structured frontmatter keys via `yq --front-matter=extract`.
# Sibling repos are READ FROM A GIT REF, not from their working trees — see
# "Where each repo is read from" below. Refuses to write if any is unreadable.
#
# Usage: scripts/gen-decision-ledger-xrepo.sh [--check]
# Prereqs: yq (mikefarah v4+). `brew install yq`. Exit 0 ok / 1 stale-or-missing.

set -eu

SP_ROOT=$(cd "$(dirname "$0")/.." && pwd)
LEDGER="$SP_ROOT/docs/decisions/LEDGER-XREPO.md"

# Sibling discovery must not depend on WHICH worktree this ran from. The old
# `cd "$SP_ROOT/.."` made that a function of where the worktree was created,
# and the two placements measurably disagree: a worktree made beside the repos
# ran fine, while one under a scratch directory reported all three siblings
# missing — write mode refusing and check mode skipping, both correctly, and
# both for a reason that had nothing to do with the repos. Resolve the MAIN
# worktree via --git-common-dir and take ITS parent, so every worktree reads
# the same siblings the primary checkout does.
#
# The fallback is spelled out rather than folded into the `cd` chain because
# the tidy version is off by one level: `cd "$(… || echo .)" && cd ../..` lands
# on `$SP_ROOT/../..` when this is not a git tree, not on `$SP_ROOT/..`.
if _common_dir=$(cd "$SP_ROOT" && git rev-parse --git-common-dir 2>/dev/null); then
  GIT_ROOT=$(cd "$SP_ROOT" && cd "$_common_dir" && cd ../.. && pwd)
else
  GIT_ROOT=$(cd "$SP_ROOT/.." && pwd)
fi

CHECK_MODE=0
[ "${1:-}" = "--check" ] && CHECK_MODE=1

if ! command -v yq >/dev/null 2>&1; then
  echo "gen-decision-ledger-xrepo: yq not found. Install: brew install yq" >&2
  exit 1
fi

# Scratch files for yq's stderr, and for materializing a doc out of a git ref.
YQ_ERR=$(mktemp)
DOC_TMP=$(mktemp)
trap 'rm -f "$YQ_ERR" "$DOC_TMP"' EXIT INT TERM

# fm <file> <expr> <label> — extract a frontmatter expression, '' if null.
#
# <label> is the doc's logical path, which is not <file> when the content came
# out of a git ref into a temp file. Diagnostics name the doc a human can go
# fix, never the mktemp path.
#
# Fails closed. This used to read
#
#   result=$(yq --front-matter=extract "$2" "$1" 2>/dev/null || echo "null")
#
# which collapsed "the key is absent" and "yq could not read the file at all"
# into the same empty string. That is worse here than in the per-repo
# generator: the loop below does `[ -z "$tag" ] && continue`, so a doc whose
# frontmatter does not parse was not merely degraded to an `(untagged)` row —
# it dropped out of the cross-repo ledger entirely, from the one table whose
# whole job is to answer "has another repo already decided this tag?". A
# settled decision could be re-litigated because the doc recording it happened
# to be unreadable, and nothing anywhere would say so.
#
# Tenet 29: a reader that cannot interpret its input errors, never skips.
fm() {
  if ! result=$(yq --front-matter=extract "$2" "$1" 2>"$YQ_ERR"); then
    echo "gen-decision-ledger-xrepo: cannot read frontmatter of $3" >&2
    echo "  expression: $2" >&2
    sed 's/^/  yq: /' "$YQ_ERR" >&2
    echo "  Fix the doc's YAML (quote values containing ':') and re-run." >&2
    exit 1
  fi
  [ "$result" = "null" ] && result=""
  printf '%s' "$result"
}

# ---------------------------------------------------------------------------
# Where each repo is read from, and why the two cases differ
#
# SIBLINGS (qiyas, bikar) are read from a git ref — origin/HEAD's default
# branch. They used to be read from `$GIT_ROOT/<repo>/docs/decisions`, the
# sibling WORKING TREE, which made this generator's output a function of
# whichever branch somebody else's session happened to have checked out. That
# is not hypothetical: on 2026-08-16 the primary bikar checkout sat 6 commits
# behind origin/main while this ran, its docs/decisions tree really did differ
# (2487a54a vs 87affcb2), and the only thing between that and a wrong committed
# ledger was a human diffing `9e4b3f1..origin/main -- docs/decisions/` by hand
# before trusting the output. Replayed afterwards, that stale tree happens to
# produce identical rows — it was a near miss and is reported as one. What is
# not a near miss is that the check was manual: a generator that needs hand-
# verification to be trusted is not a generator.
#
# The failure the ref cannot have is the one that was measured. Flip a single
# `status_token: ACCEPTED` to `DEAD` in a sibling's WORKING TREE — an edit
# nobody committed, the shape of somebody else's in-flight work or an editor
# autosave — and the old reader wrote that row into the committed ledger,
# dropping the tag's ★ authoritative marker. Same tree, this reader: unchanged.
# Mid-rebase and mid-bisect siblings are the same defect wearing other clothes.
#
# SACRED-PATTERNS is read from this worktree, on purpose and not by omission.
# It is the repo being edited: a session that adds a decision doc runs the
# generator and commits the doc and the ledger together, so an uncommitted doc
# here is the input, not contamination. The siblings get the opposite treatment
# for the same reason — their uncommitted state is somebody else's in-flight
# work and none of this file's business.
#
# What is deliberately NOT recorded in the file: the tree sha each sibling was
# read at. It would make the ledger self-describing, and it would also make
# `--check` fail whenever a sibling edits a decision doc's PROSE — a change
# that moves the tree sha and cannot move a single row, because only four
# frontmatter keys are ever read. That is a gate crying wolf about its own
# provenance, and a gate that cries wolf gets switched off. The ref NAME goes
# in the file because it is the durable fact; the sha goes to stderr on every
# run because it is the volatile one.
# ---------------------------------------------------------------------------

# sibling_ref <dir> — echo the remote-tracking ref to read, or fail.
sibling_ref() {
  if _r=$(git -C "$1" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null); then
    printf '%s' "$_r"
    return 0
  fi
  for _c in origin/main origin/master; do
    if git -C "$1" rev-parse --verify --quiet "$_c^{commit}" >/dev/null 2>&1; then
      printf '%s' "$_c"
      return 0
    fi
  done
  return 1
}

# emit_row <repo> <basename> <file-to-read>
emit_row() {
  _repo="$1"
  _rel="$1/docs/decisions/$2"
  _file="$3"
  tag=$(fm "$_file" '.tag' "$_rel")
  [ -z "$tag" ] && return 0   # untagged docs don't roll up (pre-backfill)
  status=$(fm "$_file" '.status_token' "$_rel")
  [ -z "$status" ] && status="(none)"
  picked=$(fm "$_file" '.picked_option' "$_rel")
  [ -z "$picked" ] && picked="—"
  superseded_by=$(fm "$_file" '.superseded_by[0]' "$_rel")
  auth="—"
  if [ "$status" = "ACCEPTED" ] && [ -z "$superseded_by" ]; then
    auth="★"
  fi
  rows="${rows}${tag}\t${_repo}\t${_rel}\t${status}\t${picked}\t${auth}\n"
}

# A repo that cannot be read is a checkout this machine does not have — NOT
# input that legitimately contributed zero rows. The two are indistinguishable
# once the join is rendered, which is why `missing` is tracked rather than
# skipped: see the guard below the loop. "Cannot be read" now covers three
# shapes, all fail-closed and each naming which one it hit: no clone, no
# resolvable origin ref, or no docs/decisions/ in that ref.
missing=""
rows=""
sources=""

for repo in qiyas bikar sacred-patterns; do
  if [ "$repo" = "sacred-patterns" ]; then
    dir="$SP_ROOT/docs/decisions"
    if [ ! -d "$dir" ]; then
      missing="${missing}${missing:+, }$repo (no docs/decisions/ in this worktree)"
      continue
    fi
    sources="${sources}${sources:+ | }${repo} this worktree"
    for doc in $(find "$dir" -maxdepth 1 -name '*.md' \
      ! -name 'README.md' ! -name 'LEDGER.md' ! -name 'LEDGER-XREPO.md' | sort); do
      emit_row "$repo" "$(basename "$doc")" "$doc"
    done
    continue
  fi

  d="$GIT_ROOT/$repo"
  if [ ! -e "$d/.git" ]; then
    missing="${missing}${missing:+, }$repo (not cloned under $GIT_ROOT)"
    continue
  fi
  if ! ref=$(sibling_ref "$d"); then
    missing="${missing}${missing:+, }$repo (no origin/HEAD, origin/main or origin/master)"
    continue
  fi
  if ! tree=$(git -C "$d" rev-parse --verify --quiet "$ref:docs/decisions" 2>/dev/null); then
    missing="${missing}${missing:+, }$repo ($ref has no docs/decisions/)"
    continue
  fi
  echo "gen-decision-ledger-xrepo: $repo read at $ref (docs/decisions tree $(printf '%.12s' "$tree"))" >&2
  sources="${sources}${sources:+ | }${repo} ${ref}"
  for base in $(git -C "$d" ls-tree --name-only "$ref:docs/decisions" \
    | grep '\.md$' \
    | grep -v -x -e 'README.md' -e 'LEDGER.md' -e 'LEDGER-XREPO.md' \
    | sort); do
    git -C "$d" show "$ref:docs/decisions/$base" >"$DOC_TMP"
    emit_row "$repo" "$base" "$DOC_TMP"
  done
done

# The two modes part ways on an incomplete environment, and the asymmetry is
# the point.
#
# WRITE refuses. The ledger is a committed file: rendering the join with a repo
# missing drops every one of its rows under a banner that says GENERATED, and
# the next `--check` on a complete machine reports *that* file as the stale
# one. A generator that silently narrows its own inputs is Tenet 29's failure
# with a `--check` mode bolted on.
#
# CHECK skips, loudly. "Cannot verify" is not "verified"; it is the same shape
# as the yq/jq guard in .husky/pre-commit and the `../3d-models` guard in
# bikar's — an absent sibling is a missing tool, not input this reader dropped.
# It exits 0 because the alternative is refusing to commit in one repo until
# the other two are cloned, and because write mode now makes the harm it would
# be guarding against unreachable.
if [ -n "$missing" ]; then
  if [ "$CHECK_MODE" -eq 1 ]; then
    echo "gen-decision-ledger-xrepo: SKIPPED — unreadable under $GIT_ROOT: $missing" >&2
    echo "  The roll-up joins all three repos, so this machine cannot verify it." >&2
    exit 0
  fi
  echo "gen-decision-ledger-xrepo: REFUSING to write a partial ledger." >&2
  echo "  Unreadable under $GIT_ROOT: $missing" >&2
  echo "  Every row from those repos would vanish from a committed, generated file." >&2
  exit 1
fi

render() {
  printf '<!-- GENERATED by scripts/gen-decision-ledger-xrepo.sh — do not edit. -->\n'
  printf '<!-- inputs: %s -->\n' "$sources"
  printf '# Cross-repo Decision LEDGER\n\n'
  printf 'Decided / dead / authoritative-per-tag joined across qiyas + bikar +\n'
  printf 'sacred-patterns. Grouped by problem-tag (shared vocabulary in each\n'
  printf 'repo'\''s `docs/decisions/tags.yaml`). For within-repo detail see that\n'
  printf 'repo'\''s `LEDGER.md`. Schema: `docs/decision-schema.md`.\n\n'
  printf 'Sibling repos are read at the remote-tracking ref named in the comment\n'
  printf 'above, not from their working trees, so no row here can move because\n'
  printf 'somebody else switched a branch. sacred-patterns is read from the\n'
  printf 'working tree because it is the repo being edited.\n\n'
  printf '| tag | repo | doc | status | picked | authoritative |\n'
  printf '|-----|------|-----|--------|--------|---------------|\n'
  if [ -n "$rows" ]; then
    printf '%b' "$rows" | sort | while IFS="$(printf '\t')" read -r tag repo rel status picked auth; do
      [ -z "$tag" ] && continue
      printf '| `%s` | %s | %s | %s | %s | %s |\n' "$tag" "$repo" "$rel" "$status" "$picked" "$auth"
    done
  else
    printf '| _(no tagged docs yet — run after backfill)_ | | | | | |\n'
  fi
  printf '\n_★ = live authoritative doc for that tag in that repo._\n'
}

if [ "$CHECK_MODE" -eq 1 ]; then
  tmp=$(mktemp)
  render >"$tmp"
  if [ ! -f "$LEDGER" ] || ! diff -q "$LEDGER" "$tmp" >/dev/null 2>&1; then
    echo "gen-decision-ledger-xrepo: $LEDGER is STALE. Run the generator." >&2
    rm -f "$tmp"
    exit 1
  fi
  rm -f "$tmp"
  echo "OK: LEDGER-XREPO.md in sync."
  exit 0
fi

render >"$LEDGER"
echo "Wrote $LEDGER"
