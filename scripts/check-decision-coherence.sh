#!/usr/bin/env sh
# Decision-doc coherence gate — make status-lies and unmarked reversals
# un-shippable. CI-blocking + pre-commit.
#
# Why this exists: the 2026-06-06 coherence audit found 6 docs whose frontmatter
# said ACCEPTED while their body said PENDING, 5 unmarked reversals, and a
# 3/61 supersede-marker rate against >=8 real reversals. The discipline lived
# only in skill prose agents skip under pressure. This gate enforces it.
#
# Every rule reads ONLY structured YAML frontmatter keys via
# `yq --front-matter=extract`. NO regex. NO markdown-body scan. The status
# <-> decision rule is `status_token==ACCEPTED ⟹ picked_option!=null` — two
# parsed fields compared, never a search for "PENDING" in the prose.
#
# Rules (each tied to an audit finding):
#   1. status_token in the enum                       (audit §2)
#   2. ACCEPTED ⟹ picked_option != null               (audit §2 — the 6 mismatches)
#   3. supersedes <-> superseded_by bidirectional      (audit §3 — unmarked reversals)
#   4. <=1 authoritative (ACCEPTED, unsuperseded) doc per tag  (audit §6.4)
#   5. tag in tags.yaml vocabulary                     (closed list)
#
# A .coherence-baseline.json allowlist grandfathers known violations so the
# gate ships green; it is APPEND-BLOCKED (a NEW {doc,rule} not in the baseline
# is always an error — you can only shrink the baseline, never grow it).
#
# Usage: scripts/check-decision-coherence.sh
# Prereqs: yq (mikefarah v4+) + jq. `brew install yq jq`. Exit 0 clean / 1 violation.

set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
DECISIONS_DIR="$ROOT/docs/decisions"
TAGS_FILE="$DECISIONS_DIR/tags.yaml"
BASELINE="$DECISIONS_DIR/.coherence-baseline.json"

for tool in yq jq; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "check-decision-coherence: $tool not found. Install: brew install yq jq" >&2
    exit 1
  fi
done

VALID_TOKENS="PROPOSED ACCEPTED REJECTED SUPERSEDED REOPENED PENDING"

fm() {
  result=$(yq --front-matter=extract "$2" "$1" 2>/dev/null || echo "null")
  [ "$result" = "null" ] && result=""
  printf '%s' "$result"
}

# in_baseline <relpath> <rule> — 0 if the {doc,rule} pair is grandfathered.
in_baseline() {
  [ -f "$BASELINE" ] || return 1
  match=$(jq -r --arg d "$1" --arg r "$2" \
    '.violations[] | select(.doc==$d and .rule==$r) | .doc' "$BASELINE" 2>/dev/null || true)
  [ -n "$match" ]
}

docs=$(find "$DECISIONS_DIR" -maxdepth 1 -name '*.md' \
  ! -name 'README.md' ! -name 'LEDGER.md' ! -name 'LEDGER-XREPO.md' | sort)

valid_tags=$(yq 'keys | .[]' "$TAGS_FILE" 2>/dev/null || true)

violations=""          # newline list of "relpath\trule\tmessage"
matched_baseline=""    # "relpath\trule" pairs that fired AND were grandfathered

record() {
  # $1 relpath, $2 rule, $3 message
  if in_baseline "$1" "$2"; then
    matched_baseline="${matched_baseline}$1	$2\n"
  else
    violations="${violations}$1	$2	$3\n"
  fi
}

# --- Per-doc rules 0, 1, 2, 5 -----------------------------------------------
for doc in $docs; do
  rel="docs/decisions/$(basename "$doc")"

  # Rule 0 — frontmatter MUST parse as YAML. A doc whose frontmatter yq can't
  # read would silently evade every other rule (the fm() helper swallows the
  # error and returns ''), so an unparseable doc is treated as ALL-GREEN — the
  # exact gap that let YAML-invalid docs (unquoted colons in status:/related:)
  # hide from the audit. Fail loudly instead.
  if ! yq --front-matter=extract '.' "$doc" >/dev/null 2>&1; then
    record "$rel" "rule-0" "frontmatter does not parse as YAML (quote values containing ':' — status:, related: entries)"
    continue
  fi

  status=$(fm "$doc" '.status_token')
  picked=$(fm "$doc" '.picked_option')
  tag=$(fm "$doc" '.tag')

  # Rule 1 — status_token enum membership. Empty (pre-backfill) is exempt:
  # the backfill (Part D) sets it; the baseline grandfathers the interim.
  if [ -n "$status" ]; then
    ok=0
    for t in $VALID_TOKENS; do [ "$status" = "$t" ] && ok=1; done
    if [ "$ok" -eq 0 ]; then
      record "$rel" "rule-1" "status_token '$status' not in enum ($VALID_TOKENS)"
    fi
  fi

  # Rule 2 — ACCEPTED ⟹ picked_option != null. Two parsed fields.
  if [ "$status" = "ACCEPTED" ] && [ -z "$picked" ]; then
    record "$rel" "rule-2" "status_token=ACCEPTED but picked_option is null"
  fi

  # Rule 5 — tag in vocabulary.
  if [ -n "$tag" ]; then
    found=0
    for vt in $valid_tags; do [ "$tag" = "$vt" ] && found=1; done
    if [ "$found" -eq 0 ]; then
      record "$rel" "rule-5" "tag '$tag' not in tags.yaml vocabulary"
    fi
  fi
done

# --- Rule 3 — supersede bidirectionality ------------------------------------
# If B.supersedes names A: A.status_token in {SUPERSEDED,REOPENED} AND
# A.superseded_by names B. Both directions parsed from list fields.
for doc in $docs; do
  rel="docs/decisions/$(basename "$doc")"
  n=$(yq --front-matter=extract '.supersedes | length' "$doc" 2>/dev/null || echo 0)
  [ -z "$n" ] && n=0
  [ "$n" = "null" ] && n=0
  i=0
  while [ "$i" -lt "$n" ]; do
    a_path=$(yq --front-matter=extract ".supersedes[$i]" "$doc" 2>/dev/null || echo "")
    i=$((i + 1))
    [ -z "$a_path" ] && continue
    a_file="$ROOT/$a_path"
    if [ ! -f "$a_file" ]; then
      record "$rel" "rule-3" "supersedes names '$a_path' which does not exist"
      continue
    fi
    a_status=$(fm "$a_file" '.status_token')
    if [ "$a_status" != "SUPERSEDED" ] && [ "$a_status" != "REOPENED" ]; then
      record "$a_path" "rule-3" "is superseded by $rel but status_token='$a_status' (need SUPERSEDED/REOPENED)"
    fi
    # back-pointer present?
    back=$(yq --front-matter=extract '.superseded_by[]' "$a_file" 2>/dev/null || echo "")
    case "$back" in
      *"$rel"*) : ;;
      *) record "$a_path" "rule-3" "missing superseded_by back-pointer to $rel" ;;
    esac
  done
done

# --- Rule 4 — at most one authoritative doc per tag -------------------------
# Authoritative = ACCEPTED with empty superseded_by. Group by tag; a 2nd such
# doc on the same tag is an unmarked reversal (must supersede the prior).
auth_pairs=""   # "tag\trel"
for doc in $docs; do
  rel="docs/decisions/$(basename "$doc")"
  status=$(fm "$doc" '.status_token')
  tag=$(fm "$doc" '.tag')
  superseded_by=$(fm "$doc" '.superseded_by[0]')
  if [ "$status" = "ACCEPTED" ] && [ -z "$superseded_by" ] && [ -n "$tag" ]; then
    auth_pairs="${auth_pairs}$tag	$rel\n"
  fi
done
dup_tags=$(printf '%b' "$auth_pairs" | awk -F'\t' 'NF==2{c[$1]++} END{for(t in c) if(c[t]>1) print t}')
for t in $dup_tags; do
  offenders=$(printf '%b' "$auth_pairs" | awk -F'\t' -v tag="$t" '$1==tag{print $2}')
  for rel in $offenders; do
    record "$rel" "rule-4" "tag '$t' has >1 authoritative (ACCEPTED, unsuperseded) doc — one must supersede the prior"
  done
done

# --- Append-block check: any stale baseline entries? ------------------------
# A baseline entry that NO LONGER fires means the doc was fixed — the entry
# must be removed (ratchet-down). We flag stale entries as errors so the
# baseline can only shrink.
stale=""
if [ -f "$BASELINE" ]; then
  count=$(jq '.violations | length' "$BASELINE" 2>/dev/null || echo 0)
  j=0
  while [ "$j" -lt "$count" ]; do
    bd=$(jq -r ".violations[$j].doc" "$BASELINE")
    br=$(jq -r ".violations[$j].rule" "$BASELINE")
    j=$((j + 1))
    case "$(printf '%b' "$matched_baseline")" in
      *"$bd	$br"*) : ;;
      *) stale="${stale}$bd	$br\n" ;;
    esac
  done
fi

# --- Report -----------------------------------------------------------------
rc=0
if [ -n "$violations" ]; then
  echo "Decision-coherence gate FAILED — new violations (not in baseline):" >&2
  printf '%b' "$violations" | while IFS="$(printf '\t')" read -r d r m; do
    [ -z "$d" ] && continue
    echo "  - [$r] $d: $m" >&2
  done
  rc=1
fi
if [ -n "$stale" ]; then
  echo "Decision-coherence gate FAILED — STALE baseline entries (doc fixed; remove from baseline to ratchet down):" >&2
  printf '%b' "$stale" | while IFS="$(printf '\t')" read -r d r; do
    [ -z "$d" ] && continue
    echo "  - [$r] $d" >&2
  done
  rc=1
fi

if [ "$rc" -eq 0 ]; then
  ng=$(printf '%b' "$matched_baseline" | grep -c '	' || true)
  [ -z "$ng" ] && ng=0
  echo "OK: decision coherence clean (${ng} known violation(s) still grandfathered in baseline)."
fi
exit "$rc"
