#!/usr/bin/env python3
"""Stage 1 — cheap, deterministic signal extraction from a session transcript.

WHY this is a script and not an agent: the transcript is far too large to read
into a model context. This pass distills a ~900 MB jsonl into a handful of small
JSONL artifacts (corrections, compaction summaries, a segment timeline, tool
errors, theme hits) that ARE small enough to reason over. No model is involved;
output is fully deterministic.

The timeline "segment" is the chunking spine for Stage 3: a new segment begins
at each human prompt (a non-sidechain user turn with plain-string content that
is NOT a compaction summary). Everything until the next human prompt — the
assistant turns and tool calls that prompt triggered — belongs to that segment.

Usage:
    extract_signals.py --jsonl SESSION.jsonl --out artifacts/<repo> \
        [--theme REGEX] [--subagent-dir DIR]

Example (validated on the small qiyas session — 27 lines):
    extract_signals.py --jsonl 7905a985-...jsonl --out /tmp/q
    # → /tmp/q/{corrections,compaction_summaries,timeline,tool_errors,
    #           theme_hits,extract_stats}.jsonl|.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
from typing import Any

from lib_jsonl import (
    content_as_text,
    is_compaction_summary,
    iter_content_blocks,
    iter_events,
    text_hash,
)

DEFAULT_THEME = (
    r"girih|medallion|substitution|\bARI\b|Hungarian|\bA6\b|anti-symmetry|"
    r"falsif|oracle|tune.{0,12}constant|geom_label|shape_id|\bF2\b|primitive|"
    r"DSL|detector|turning.?function|provenance"
)


def _truncate(s: str, n: int) -> str:
    s = " ".join(s.split())  # collapse whitespace so previews stay one line
    return s if len(s) <= n else s[:n] + "…"


def _block_is_error(block: dict[str, Any]) -> bool:
    if block.get("type") != "tool_result":
        return False
    if block.get("is_error"):
        return True
    c = block.get("content")
    text = c if isinstance(c, str) else json.dumps(c) if c else ""
    return bool(re.search(r"\b(error|traceback|exception|failed|stderr)\b", text, re.I))


def _block_text(block: dict[str, Any]) -> str:
    c = block.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        parts = [b.get("text", "") for b in c if isinstance(b, dict)]
        return " ".join(p for p in parts if p)
    return json.dumps(c) if c is not None else ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--theme", default=DEFAULT_THEME)
    ap.add_argument("--subagent-dir", default=None, help="dir of subagents/*.jsonl for the header index")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    theme_re = re.compile(args.theme, re.I)

    corrections: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    timeline: list[dict[str, Any]] = []
    tool_errors: list[dict[str, Any]] = []
    theme_hits: list[dict[str, Any]] = []
    seen_summary_hashes: set[str] = set()
    type_counts: dict[str, int] = {}

    seg: dict[str, Any] | None = None
    last_assistant_text = ""
    last_agent_name = ""

    def close_segment() -> None:
        if seg is not None:
            timeline.append(seg)

    for ev in iter_events(args.jsonl, keep_discarded_counts=type_counts):
        etype = ev.get("type")
        ts = ev.get("timestamp")
        branch = ev.get("gitBranch")
        msg = ev.get("message")

        if etype == "agent-name":
            last_agent_name = ev.get("name") or last_agent_name or ""
            continue

        if etype == "user" and not ev.get("isSidechain"):
            text = content_as_text(msg)
            if text is not None:
                if is_compaction_summary(text):
                    h = text_hash(text)
                    if h not in seen_summary_hashes:
                        seen_summary_hashes.add(h)
                        summaries.append({"ts": ts, "gitBranch": branch, "hash": h, "text": text})
                    # a compaction summary is a system-injected resume, not a
                    # human prompt — do not start a new segment on it
                else:
                    # genuine human prompt → boundary: close prior segment, open new
                    close_segment()
                    seg = {
                        "segment_id": len(timeline),
                        "ts_start": ts,
                        "ts_end": ts,
                        "gitBranch": branch,
                        "agent_name": last_agent_name,
                        "first_user_text": _truncate(text, 240),
                        "n_user": 1,
                        "n_assistant": 0,
                        "n_tool_use": 0,
                        "tool_histogram": {},
                        "had_correction": True,  # every human prompt is steering signal
                    }
                    corrections.append(
                        {
                            "ts": ts,
                            "gitBranch": branch,
                            "agent_name": last_agent_name,
                            "segment_id": seg["segment_id"],
                            "text": _truncate(text, 1200),
                            "prev_assistant": _truncate(last_assistant_text, 200),
                        }
                    )
                    if theme_re.search(text):
                        theme_hits.append({"ts": ts, "src": "human", "text": _truncate(text, 400)})
            else:
                # tool_result-bearing user turn — scan blocks for errors
                if seg is not None:
                    seg["ts_end"] = ts or seg["ts_end"]
                for block in iter_content_blocks(msg):
                    if _block_is_error(block):
                        tool_errors.append({"ts": ts, "text": _truncate(_block_text(block), 300)})
            continue

        if etype == "assistant":
            if seg is not None:
                seg["n_assistant"] += 1
                seg["ts_end"] = ts or seg["ts_end"]
            # capture assistant text (for correction context) + tool_use histogram
            atext_parts: list[str] = []
            for block in iter_content_blocks(msg):
                btype = block.get("type")
                if btype == "text":
                    atext_parts.append(block.get("text", ""))
                elif btype == "tool_use":
                    name = block.get("name", "?")
                    if seg is not None:
                        seg["n_tool_use"] += 1
                        seg["tool_histogram"][name] = seg["tool_histogram"].get(name, 0) + 1
            if atext_parts:
                last_assistant_text = " ".join(atext_parts)
                if theme_re.search(last_assistant_text):
                    theme_hits.append({"ts": ts, "src": "assistant", "text": _truncate(last_assistant_text, 400)})
            continue

    close_segment()

    # --- subagent header index (always cheap; bodies only under --include-subagents elsewhere)
    subagent_index: list[dict[str, Any]] = []
    if args.subagent_dir and os.path.isdir(args.subagent_dir):
        for fn in sorted(os.listdir(args.subagent_dir)):
            if not fn.endswith(".jsonl"):
                continue
            fp = os.path.join(args.subagent_dir, fn)
            first_prompt = ""
            terminal = ""
            n_turns = 0
            for ev in iter_events(fp):
                if ev.get("type") in ("user", "assistant"):
                    n_turns += 1
                    t = content_as_text(ev.get("message"))
                    if t is None:
                        t = " ".join(b.get("text", "") for b in iter_content_blocks(ev.get("message")))
                    if ev.get("type") == "user" and not first_prompt and t:
                        first_prompt = _truncate(t, 300)
                    if ev.get("type") == "assistant" and t:
                        terminal = _truncate(t, 400)
            subagent_index.append(
                {"agent_file": fn, "n_turns": n_turns, "task_prompt": first_prompt, "terminal": terminal}
            )

    def dump(name: str, rows: list[dict[str, Any]]) -> None:
        with open(os.path.join(args.out, name), "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    dump("corrections.jsonl", corrections)
    dump("compaction_summaries.jsonl", summaries)
    dump("timeline.jsonl", timeline)
    dump("tool_errors.jsonl", tool_errors)
    dump("theme_hits.jsonl", theme_hits)
    dump("subagent_index.jsonl", subagent_index)

    kept = sum(v for k, v in type_counts.items() if k not in ("_oversized", "_malformed"))
    stats = {
        "jsonl": args.jsonl,
        "type_counts": type_counts,
        "lines_parsed": kept,
        "n_corrections": len(corrections),
        "n_unique_summaries": len(summaries),
        "n_segments": len(timeline),
        "n_tool_errors": len(tool_errors),
        "n_theme_hits": len(theme_hits),
        "n_subagents": len(subagent_index),
    }
    with open(os.path.join(args.out, "extract_stats.json"), "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
