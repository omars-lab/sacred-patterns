#!/usr/bin/env bash
# Stage 0 — resolve the input manifest for a retrospective run.
#
# WHY: the mapping from a repo working dir to its Claude transcript project dir
# is a path-encoding ("/" -> "-") plus some repos keep their real work in a
# worktree project dir (bikar). This script resolves every input path once so
# the downstream Python stages don't re-implement the encoding.
#
# Usage:
#   discover_sources.sh --out artifacts [--repos bikar,qiyas,sacred-patterns] \
#     [--workspace ~/Workspace/git] [--projects ~/.claude/projects]
#
# Output: <out>/manifest.json  (one entry per repo: repo_root, project dirs,
# main jsonl(s), subagent dir, decisions dir, memory dirs, living docs)

set -euo pipefail

WORKSPACE="${HOME}/Workspace/git"
PROJECTS="${HOME}/.claude/projects"
REPOS="bikar,qiyas,sacred-patterns"
OUT="artifacts"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repos) REPOS="$2"; shift 2;;
    --workspace) WORKSPACE="$2"; shift 2;;
    --projects) PROJECTS="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done

mkdir -p "$OUT"
MANIFEST="$OUT/manifest.json"

# encode a working-dir path the way Claude Code names its project dir:
# leading slash dropped-then-prefixed-with-dash, every "/" -> "-"
encode_path() { echo "$1" | sed 's#/#-#g'; }

echo "{" > "$MANIFEST"
echo '  "generated_for_repos": "'"$REPOS"'",' >> "$MANIFEST"
echo '  "repos": [' >> "$MANIFEST"

IFS=',' read -ra REPO_ARR <<< "$REPOS"
first=1
for repo in "${REPO_ARR[@]}"; do
  repo_root="$WORKSPACE/$repo"
  enc="$(encode_path "$repo_root")"          # e.g. -Users-omareid-Workspace-git-bikar

  # collect every project dir whose name starts with the encoded root
  # (catches the bikar worktree dir: <enc>--claude-worktrees-...)
  project_dirs=()
  for d in "$PROJECTS/$enc" "$PROJECTS/$enc"--*; do
    [[ -d "$d" ]] && project_dirs+=("$d")
  done

  # main jsonl files = top-level *.jsonl across those project dirs (sorted by size desc)
  main_jsonls=()
  subagent_dirs=()
  for d in "${project_dirs[@]:-}"; do
    [[ -z "${d:-}" ]] && continue
    while IFS= read -r f; do main_jsonls+=("$f"); done < <(find "$d" -maxdepth 1 -name '*.jsonl' 2>/dev/null)
    while IFS= read -r s; do subagent_dirs+=("$s"); done < <(find "$d" -maxdepth 2 -type d -name subagents 2>/dev/null)
  done

  decisions_dir="$repo_root/docs/decisions"
  repo_memory="$repo_root/memory"
  proj_memory="$PROJECTS/$enc/memory"

  # living docs (best-effort; only emit ones that exist)
  living=()
  for cand in \
    "$repo_root/docs/iteration-status.md" \
    "$repo_root/.claude/plans/post-i1-task-routing.md"; do
    [[ -f "$cand" ]] && living+=("$cand")
  done

  json_arr() { # print a JSON array of the passed args, skipping empties
    printf '['
    local sep=""
    for x in "$@"; do
      [[ -z "$x" ]] && continue
      printf '%s"%s"' "$sep" "$x"; sep=", "
    done
    printf ']'
  }

  [[ $first -eq 0 ]] && echo "," >> "$MANIFEST"
  first=0
  {
    echo "    {"
    echo '      "name": "'"$repo"'",'
    echo '      "repo_root": "'"$repo_root"'",'
    echo '      "project_dirs": '"$(json_arr "${project_dirs[@]:-}")"','
    echo '      "main_jsonls": '"$(json_arr "${main_jsonls[@]:-}")"','
    echo '      "subagent_dirs": '"$(json_arr "${subagent_dirs[@]:-}")"','
    echo '      "decisions_dir": "'"$decisions_dir"'",'
    echo '      "repo_memory_dir": "'"$repo_memory"'",'
    echo '      "project_memory_dir": "'"$proj_memory"'",'
    echo '      "living_docs": '"$(json_arr "${living[@]:-}")"
    echo -n "    }"
  } >> "$MANIFEST"

  # fail loud if a repo resolved to zero transcripts AND zero ground truth
  if [[ ${#main_jsonls[@]} -eq 0 && ! -d "$decisions_dir" ]]; then
    echo "WARNING: repo '$repo' resolved no transcripts and no decisions dir" >&2
  fi
done

echo "" >> "$MANIFEST"
echo "  ]" >> "$MANIFEST"
echo "}" >> "$MANIFEST"

echo "wrote $MANIFEST" >&2
cat "$MANIFEST"
