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
# Assumes the three repos are siblings (../qiyas, ../bikar, . for SP). Skips
# any repo whose docs/decisions/ is absent.
#
# Usage: scripts/gen-decision-ledger-xrepo.sh [--check]
# Prereqs: yq (mikefarah v4+). `brew install yq`. Exit 0 ok / 1 stale-or-missing.

set -eu

SP_ROOT=$(cd "$(dirname "$0")/.." && pwd)
GIT_ROOT=$(cd "$SP_ROOT/.." && pwd)
LEDGER="$SP_ROOT/docs/decisions/LEDGER-XREPO.md"

CHECK_MODE=0
[ "${1:-}" = "--check" ] && CHECK_MODE=1

if ! command -v yq >/dev/null 2>&1; then
  echo "gen-decision-ledger-xrepo: yq not found. Install: brew install yq" >&2
  exit 1
fi

# Scratch file for yq's stderr, so fm() can tell "key absent" from "yq could
# not read this file" without merging yq's diagnostics into the value.
YQ_ERR=$(mktemp)
trap 'rm -f "$YQ_ERR"' EXIT INT TERM

# fm <doc> <expr> — extract a frontmatter expression, '' if null/absent.
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
    echo "gen-decision-ledger-xrepo: cannot read frontmatter of $1" >&2
    echo "  expression: $2" >&2
    sed 's/^/  yq: /' "$YQ_ERR" >&2
    echo "  Fix the doc's YAML (quote values containing ':') and re-run." >&2
    exit 1
  fi
  [ "$result" = "null" ] && result=""
  printf '%s' "$result"
}

# A repo whose docs/decisions/ is absent is a checkout this machine does not
# have — NOT input that legitimately contributed zero rows. The two are
# indistinguishable once the join is rendered, which is why `missing` is
# tracked rather than skipped: see the guard below the loop.
missing=""
rows=""
for repo in qiyas bikar sacred-patterns; do
  dir="$GIT_ROOT/$repo/docs/decisions"
  if [ ! -d "$dir" ]; then
    missing="${missing}${missing:+, }$repo"
    continue
  fi
  for doc in $(find "$dir" -maxdepth 1 -name '*.md' \
    ! -name 'README.md' ! -name 'LEDGER.md' ! -name 'LEDGER-XREPO.md' | sort); do
    tag=$(fm "$doc" '.tag')
    [ -z "$tag" ] && continue   # untagged docs don't roll up (pre-backfill)
    status=$(fm "$doc" '.status_token')
    [ -z "$status" ] && status="(none)"
    picked=$(fm "$doc" '.picked_option')
    [ -z "$picked" ] && picked="—"
    superseded_by=$(fm "$doc" '.superseded_by[0]')
    auth="—"
    if [ "$status" = "ACCEPTED" ] && [ -z "$superseded_by" ]; then
      auth="★"
    fi
    rel="$repo/docs/decisions/$(basename "$doc")"
    rows="${rows}${tag}\t${repo}\t${rel}\t${status}\t${picked}\t${auth}\n"
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
    echo "gen-decision-ledger-xrepo: SKIPPED — not checked out under $GIT_ROOT: $missing" >&2
    echo "  The roll-up joins all three repos, so this machine cannot verify it." >&2
    exit 0
  fi
  echo "gen-decision-ledger-xrepo: REFUSING to write a partial ledger." >&2
  echo "  Not checked out under $GIT_ROOT: $missing" >&2
  echo "  Every row from those repos would vanish from a committed, generated file." >&2
  exit 1
fi

render() {
  printf '<!-- GENERATED by scripts/gen-decision-ledger-xrepo.sh — do not edit. -->\n'
  printf '# Cross-repo Decision LEDGER\n\n'
  printf 'Decided / dead / authoritative-per-tag joined across qiyas + bikar +\n'
  printf 'sacred-patterns. Grouped by problem-tag (shared vocabulary in each\n'
  printf 'repo'\''s `docs/decisions/tags.yaml`). For within-repo detail see that\n'
  printf 'repo'\''s `LEDGER.md`. Schema: `docs/decision-schema.md`.\n\n'
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
