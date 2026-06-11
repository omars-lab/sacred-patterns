#!/usr/bin/env python3
"""Stage 2 — index the DURABLE record into one ground_truth.json per repo.

WHY this is the triangulation backbone: transcript-derived claims are hearsay
until corroborated. Decision docs (with status markers + supersede rationale),
memory files (codified lessons), the theme-filtered git log (mechanical evidence
of reverts/fixes), and living routing docs are the durable record the Stage 4
reduce step checks claims against. A `SUPERSEDED`/`REOPENED`/`REJECTED` chain on
one problem is the strongest possible evidence of a repeated mistake — stronger
than counting transcript grumbles.

No model involved; deterministic.

Usage:
    index_ground_truth.py --repo-root DIR --decisions-dir DIR \
        --repo-memory DIR --project-memory DIR --out OUT_DIR \
        [--living DOC ...] [--since 2026-04-01] [--theme REGEX]

Output: <out>/ground_truth.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from typing import Any

STATUS_WORDS = ("ACCEPTED", "SUPERSEDED", "REJECTED", "REOPENED", "PROPOSED", "PENDING", "OPEN")
STATUS_RE = re.compile(r"^status:\s*(.+)$", re.I | re.M)
DATE_IN_NAME_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
TITLE_RE = re.compile(r"^#\s+(.+)$", re.M)
RELATED_TASK_RE = re.compile(r"\b((?:qiyas|bikar|sacred-patterns)#\d+)\b")
RELATED_COMMIT_RE = re.compile(r"\bcommit:\s*([0-9a-f]{7,40})\b", re.I)


def _read(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _classify_status(status_line: str) -> str:
    up = status_line.upper()
    for w in STATUS_WORDS:
        if w in up:
            return w
    return "UNKNOWN"


def index_decisions(decisions_dir: str, theme_re: re.Pattern[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not os.path.isdir(decisions_dir):
        return out
    for fn in sorted(os.listdir(decisions_dir)):
        if not fn.endswith(".md") or fn.upper() == "README.MD":
            continue
        path = os.path.join(decisions_dir, fn)
        text = _read(path)
        m_status = STATUS_RE.search(text)
        status_line = m_status.group(1).strip() if m_status else ""
        m_title = TITLE_RE.search(text)
        date_m = DATE_IN_NAME_RE.search(fn)
        # supersede/falsification rationale: the inline "— ..." after the verdict
        rationale = ""
        if "—" in status_line:
            rationale = status_line.split("—", 1)[1].strip()
        out.append(
            {
                "path": path,
                "file": fn,
                "date": date_m.group(1) if date_m else None,
                "title": m_title.group(1).strip() if m_title else fn,
                "status": _classify_status(status_line),
                "status_line": status_line[:300],
                "rationale": rationale[:400],
                "related_tasks": sorted(set(RELATED_TASK_RE.findall(text)))[:12],
                "related_commits": sorted(set(RELATED_COMMIT_RE.findall(text)))[:12],
                "theme_relevant": bool(theme_re.search(text)),
            }
        )
    return out


def index_memory(*dirs: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for d in dirs:
        if not d or not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md"):
                continue
            path = os.path.join(d, fn)
            text = _read(path)
            # first non-frontmatter, non-heading paragraph
            body = re.sub(r"^---.*?---", "", text, count=1, flags=re.S)
            first_para = ""
            for para in re.split(r"\n\s*\n", body):
                p = para.strip()
                if p and not p.startswith("#"):
                    first_para = " ".join(p.split())[:300]
                    break
            out.append({"path": path, "file": fn, "first_para": first_para})
    return out


def index_git(repo_root: str, since: str, theme_re: re.Pattern[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not os.path.isdir(os.path.join(repo_root, ".git")):
        return out
    try:
        log = subprocess.run(
            ["git", "-C", repo_root, "log", f"--since={since}", "--pretty=%H%x01%cI%x01%s", "--no-merges"],
            capture_output=True, text=True, check=True, timeout=60,
        ).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return out
    for line in log.splitlines():
        parts = line.split("\x01")
        if len(parts) != 3:
            continue
        sha, cdate, subject = parts
        is_revert = bool(re.match(r"\s*(revert|fix|hotfix)\b", subject, re.I))
        if theme_re.search(subject) or is_revert:
            out.append({"sha": sha[:12], "date": cdate[:10], "subject": subject[:160], "revert_or_fix": is_revert})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--decisions-dir", required=True)
    ap.add_argument("--repo-memory", default="")
    ap.add_argument("--project-memory", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--living", nargs="*", default=[])
    ap.add_argument("--since", default="2026-04-01")
    ap.add_argument("--theme", default=r"girih|medallion|substitution|ARI|Hungarian|A6|anti-symmetry|falsif|oracle|geom_label|shape_id|F2|detector|DSL|primitive")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    theme_re = re.compile(args.theme, re.I)

    decisions = index_decisions(args.decisions_dir, theme_re)
    memory = index_memory(args.repo_memory, args.project_memory)
    git = index_git(args.repo_root, args.since, theme_re)

    living: dict[str, str] = {}
    for doc in args.living:
        if os.path.isfile(doc):
            living[doc] = _read(doc)

    status_hist: dict[str, int] = {}
    for d in decisions:
        status_hist[d["status"]] = status_hist.get(d["status"], 0) + 1

    gt = {
        "repo_root": args.repo_root,
        "decisions": decisions,
        "decision_status_histogram": status_hist,
        "memory": memory,
        "git": git,
        "living_docs": living,
        "counts": {
            "decisions": len(decisions),
            "decisions_theme_relevant": sum(1 for d in decisions if d["theme_relevant"]),
            "memory": len(memory),
            "git_theme_or_revert": len(git),
            "living_docs": len(living),
        },
    }
    with open(os.path.join(args.out, "ground_truth.json"), "w", encoding="utf-8") as fh:
        json.dump(gt, fh, indent=2, ensure_ascii=False)
    print(json.dumps({"repo": os.path.basename(args.repo_root), **gt["counts"], "status_hist": status_hist}, indent=2))


if __name__ == "__main__":
    main()
