#!/usr/bin/env sh
# Generate docs/decisions/LEDGER-XREPO.md — the cross-repo roll-up of decided /
# dead / authoritative-per-tag across qiyas + bikar + sacred-patterns, plus an
# index of 3d-models' decisions.
#
# Why a cross-repo roll-up: problem-tags span repos (face-class-identity lives
# in both qiyas and bikar; svg-direct's spine crosses qiyas + SP). A future
# session asking "has this tag been decided anywhere?" needs one place that
# joins all three repos' frontmatter. The per-repo LEDGER.md answers
# within-repo; this answers across.
#
# Why 3d-models is an index and not more rows: it keeps its decisions in ONE
# file, docs/decisions-log.md, one `## D-0xx — title` heading each — its D-004
# chose that over mirroring this tree, and its D-049 §3 chose "index only,
# generated" for the join. So this reads those headings at the repo's origin
# ref and emits one link per heading; nothing is transcribed, so nothing can
# drift between two copies. The same D-049 §3 names what the cross-repo check
# blocks on: a `D-0xx` cited in any of the four repos that is neither a heading
# in that file nor a file in bikar's docs/decisions/ is a broken reference —
# the rule the doc-pointer gates already apply to paths.
#
# Reads ONLY structured frontmatter keys via `yq --front-matter=extract`, and
# ONLY the `## D-0xx — ` heading lines of 3d-models' log.
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
# ran fine, while one under a scratch directory reported all the siblings
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

# ---------------------------------------------------------------------------
# 3d-models: one file, headings only, links out.
#
# heading_anchor <heading text> — the fragment GitHub renders for a heading:
# lowercase, drop everything but letters, digits, spaces and hyphens, then
# spaces to hyphens. "D-004 — Decisions live in this file" becomes
# "d-004--decisions-live-in-this-file" (the em dash goes, its two spaces stay).
# The log's headings are ASCII plus that em dash, so the byte-wise class is
# exact for them; a heading with an accented letter would lose it here where
# GitHub keeps it, and the link would land on the page, not the heading.
# ---------------------------------------------------------------------------
heading_anchor() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed -e 's/[^a-z0-9 -]//g' -e 's/ /-/g'
}

# origin_https <dir> — the browsable URL of a repo's origin, or fail. Links in
# the index must open from a rendered page, not only from a checkout that has
# the sibling beside it, so they are absolute; the URL is derived from the
# remote the ref was fetched from rather than typed here.
origin_https() {
  _u=$(git -C "$1" remote get-url origin 2>/dev/null) || return 1
  case "$_u" in
    git@github.com:*) _u="https://github.com/${_u#git@github.com:}" ;;
    ssh://git@github.com/*) _u="https://github.com/${_u#ssh://git@github.com/}" ;;
  esac
  printf '%s' "${_u%.git}"
}

DM_LOG="docs/decisions-log.md"
dm_rows=""        # "id\ttitle\tanchor" per heading
dm_ids=""         # newline-separated heading ids — the resolver for citations
dm_url=""
dm_ref=""
d="$GIT_ROOT/3d-models"
if [ ! -e "$d/.git" ]; then
  missing="${missing}${missing:+, }3d-models (not cloned under $GIT_ROOT)"
elif ! dm_ref=$(sibling_ref "$d"); then
  missing="${missing}${missing:+, }3d-models (no origin/HEAD, origin/main or origin/master)"
elif ! blob=$(git -C "$d" rev-parse --verify --quiet "$dm_ref:$DM_LOG" 2>/dev/null); then
  missing="${missing}${missing:+, }3d-models ($dm_ref has no $DM_LOG)"
elif ! dm_url=$(origin_https "$d"); then
  missing="${missing}${missing:+, }3d-models (no origin URL to link to)"
else
  echo "gen-decision-ledger-xrepo: 3d-models read at $dm_ref ($DM_LOG blob $(printf '%.12s' "$blob"))" >&2
  sources="${sources}${sources:+ | }3d-models ${dm_ref}"
  dm_url="$dm_url/blob/${dm_ref#origin/}/$DM_LOG"
  # `## D-0xx — title`: the id is the first word, the title is everything past
  # the FIRST " — " (titles carry their own dashes: D-024 has two more).
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    rest="${line#\#\# }"
    id="${rest%% *}"
    title="${rest#* — }"
    dm_ids="${dm_ids}${id}
"
    dm_rows="${dm_rows}${id}\t$(printf '%s' "$title" | sed 's/|/\\|/g')\t$(heading_anchor "$rest")\n"
  done <<EOF
$(git -C "$d" show "$dm_ref:$DM_LOG" | grep -E '^## D-0[0-9]{2} — ')
EOF
  # A log with no headings is a file this reader cannot interpret, not a repo
  # with no decisions (Tenet 29) — the 49 it has today cannot become 0 quietly.
  if [ -z "$dm_ids" ]; then
    missing="${missing}${missing:+, }3d-models ($dm_ref $DM_LOG has no \`## D-0xx — \` headings)"
  fi
fi

# ---------------------------------------------------------------------------
# The citation check. cited_ids <dir> [<ref>] prints the distinct `D-0xx`
# tokens in a repo's tracked text — at the ref for a sibling, in the working
# tree for this repo, since that is what each is read from above. A token is a
# citation only with a non-identifier on both sides, so `LD-012` or `D-0123`
# do not count; `D-0xx` itself never matches. This ledger is excluded from its
# own scan: its rows are the index, not citations, and a heading that vanished
# upstream shows up as staleness, which is the right name for it.
# The test scaffold is excluded for the mirror reason: it plants
# deliberately-dangling D-numbers as fixtures to prove this very check fires,
# and (like every string in a decision doc) they would otherwise be scanned as
# citations of nowhere. No literal id is written in this comment on purpose:
# the test harness harvests every `D-0xx` token from THIS script to build the
# fixture headings its cases resolve against, so an example id named here would
# quietly become resolvable and defeat the very cases it illustrates.
# ---------------------------------------------------------------------------
CITE_RE='(^|[^A-Za-z0-9-])D-0[0-9]{2}([^A-Za-z0-9-]|$)'
cited_ids() {
  { git -C "$1" grep -h -o -I -E "$CITE_RE" ${2:+"$2"} -- . ':(exclude)docs/decisions/LEDGER-XREPO.md' ':(exclude)scripts/gen-decision-ledger-xrepo.test.sh' 2>/dev/null || true; } \
    | grep -o -E 'D-0[0-9]{2}' | sort -u
}

# resolves <id> — 0 if the id is a heading in 3d-models' log or names a file
# in bikar's docs/decisions/ at its ref (D-049 §3's two homes).
resolves() {
  printf '%s' "$dm_ids" | grep -q -x -F "$1" && return 0
  [ -n "$bikar_files" ] && printf '%s\n' "$bikar_files" | grep -q -i -F "$1"
}

dangling=""
if [ -z "$missing" ]; then
  bikar_files=$(git -C "$GIT_ROOT/bikar" ls-tree --name-only "$(sibling_ref "$GIT_ROOT/bikar"):docs/decisions" 2>/dev/null || true)
  for repo in qiyas bikar 3d-models sacred-patterns; do
    if [ "$repo" = "sacred-patterns" ]; then
      ids=$(cited_ids "$SP_ROOT"); where="this worktree"
    else
      ref=$(sibling_ref "$GIT_ROOT/$repo"); ids=$(cited_ids "$GIT_ROOT/$repo" "$ref"); where="$ref"
    fi
    for id in $ids; do
      resolves "$id" || dangling="${dangling}  ${repo} (${where}) cites ${id}
"
    done
  done
fi

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
    echo "  The roll-up joins all four repos, so this machine cannot verify it." >&2
    exit 0
  fi
  echo "gen-decision-ledger-xrepo: REFUSING to write a partial ledger." >&2
  echo "  Unreadable under $GIT_ROOT: $missing" >&2
  echo "  Every row from those repos would vanish from a committed, generated file." >&2
  exit 1
fi

# A dangling D-number blocks in BOTH modes — it is a broken reference, not a
# stale file, and no regeneration repairs it. Write refuses because an index
# that other repos cite past is the drift the index exists to make impossible.
# The usual cause is ordering, not a typo: bikar merged a citation before this
# machine fetched the 3d-models PR that added the heading — so the first
# repair named is the fetch.
if [ -n "$dangling" ]; then
  echo "gen-decision-ledger-xrepo: D-numbers that resolve in neither repo:" >&2
  printf '%s' "$dangling" >&2
  echo "  A cited D-0xx must be a \`## D-0xx — \` heading in 3d-models $DM_LOG ($dm_ref)" >&2
  echo "  or a file in bikar docs/decisions/. Fetch both repos; if it is still dangling," >&2
  echo "  fix the citation in the repo that made it (3d-models D-049 §3)." >&2
  exit 1
fi

render() {
  printf '<!-- GENERATED by scripts/gen-decision-ledger-xrepo.sh — do not edit. -->\n'
  printf '<!-- inputs: %s -->\n' "$sources"
  printf '# Cross-repo Decision LEDGER\n\n'
  printf 'Decided / dead / authoritative-per-tag joined across qiyas + bikar +\n'
  printf 'sacred-patterns, then an index of 3d-models'\'' decisions. Grouped by\n'
  printf 'problem-tag (shared vocabulary in each repo'\''s `docs/decisions/tags.yaml`).\n'
  printf 'For within-repo detail see that repo'\''s `LEDGER.md`. Schema:\n'
  printf '`docs/decision-schema.md`.\n\n'
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
  printf '\n_★ = live authoritative doc for that tag in that repo._\n\n'

  printf '## 3d-models decisions — index\n\n'
  printf '3d-models keeps its decisions in one file, `%s`, one\n' "$DM_LOG"
  printf '`## D-0xx — title` heading each (its D-004). Each row links to that heading at\n'
  printf 'the ref named above; nothing is copied (its D-049 §3). Every `D-0xx` cited in\n'
  printf 'qiyas, bikar, sacred-patterns or 3d-models must resolve to a row here or to a\n'
  printf 'file in bikar'\''s `docs/decisions/`, or the generator refuses.\n\n'
  printf '| id | decision |\n'
  printf '|----|----------|\n'
  printf '%b' "$dm_rows" | sort | while IFS="$(printf '\t')" read -r id title anchor; do
    [ -z "$id" ] && continue
    printf '| %s | [%s](%s#%s) |\n' "$id" "$title" "$dm_url" "$anchor"
  done
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
