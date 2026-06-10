#!/usr/bin/env python3
"""Stage 3 prep — pack the per-repo extracts into token-budgeted chunk packets.

WHY chunk by the segment spine, not by bytes: a byte/line split cuts mid-thread
and a single multi-MB tool_result would blow a chunk. Each packet is a
contiguous DATE RANGE of human-prompt segments plus the curated signal that
falls in that range. Each packet is what one Stage-3 map subagent reads — it is
ALWAYS distilled extract, never raw jsonl.

WHY summaries are special-cased: the compaction summaries total ~2M tokens of
near-duplicate text (each compaction extends the prior). Packing them naively
blows every budget. So a packet carries only the SINGLE most-recent summary at
or before its window end, head-truncated — that one summary already subsumes the
earlier ones in the window.

Usage:
    build_chunk_packets.py --in artifacts/<repo> --out artifacts/<repo>/packets \
        [--budget-chars 360000] [--max-windows 15]

Budget note: ~360k chars ≈ ~90k tokens of packet body, leaving headroom for the
map prompt. --max-windows caps a huge repo so it can't drown small ones.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any


def _load(path: str) -> list[dict[str, Any]]:
    if not os.path.isfile(path):
        return []
    return [json.loads(line) for line in open(path, encoding="utf-8")]


def _ts(row: dict[str, Any]) -> str:
    return row.get("ts") or row.get("ts_start") or ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="indir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget-chars", type=int, default=320_000)
    ap.add_argument("--max-windows", type=int, default=30)
    ap.add_argument("--summary-head-chars", type=int, default=12_000)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    segments = sorted(_load(os.path.join(args.indir, "timeline.jsonl")), key=lambda s: s.get("ts_start") or "")
    corrections = _load(os.path.join(args.indir, "corrections.jsonl"))
    summaries = sorted(_load(os.path.join(args.indir, "compaction_summaries.jsonl")), key=_ts)
    theme_hits = _load(os.path.join(args.indir, "theme_hits.jsonl"))
    tool_errors = _load(os.path.join(args.indir, "tool_errors.jsonl"))

    if not segments:
        print(json.dumps({"windows": 0, "note": "no segments"}))
        return

    # group corrections / theme_hits / tool_errors by ts for fast in-window pull
    def in_range(rows: list[dict[str, Any]], lo: str, hi: str) -> list[dict[str, Any]]:
        return [r for r in rows if lo <= _ts(r) <= hi]

    # Greedily pack segments until the estimated packet char-size hits budget.
    # Packet size is dominated by corrections + the one summary; segment headers
    # are tiny. We size on corrections-in-range as we extend the window.
    windows: list[dict[str, Any]] = []
    i = 0
    n = len(segments)
    # If max-windows would be exceeded at the natural budget, widen the budget so
    # every segment still lands in some window (coverage > granularity).
    while i < n:
        start_seg = segments[i]
        lo = start_seg.get("ts_start") or ""
        j = i
        cur_chars = 0
        while j < n:
            hi = segments[j].get("ts_end") or segments[j].get("ts_start") or lo
            corr = in_range(corrections, lo, hi)
            # Budget on the dominant packet costs: correction bodies AND the
            # per-segment headers (1 month ≈ 1000+ segments, so headers are not
            # negligible). +1.7x fudge approximates JSON quoting/structure.
            chars = int(
                1.7
                * (
                    sum(len(c.get("text", "")) + len(c.get("prev_assistant", "")) for c in corr)
                    + sum(len(json.dumps(s, ensure_ascii=False)) for s in segments[i : j + 1])
                )
            )
            if chars > args.budget_chars and j > i:
                break
            cur_chars = chars
            j += 1
        hi = segments[j - 1].get("ts_end") or segments[j - 1].get("ts_start") or lo

        latest_summary = None
        for s in summaries:
            if _ts(s) <= hi:
                latest_summary = s
            else:
                break

        windows.append(
            {
                "lo": lo,
                "hi": hi,
                "seg_from": start_seg["segment_id"],
                "seg_to": segments[j - 1]["segment_id"],
                "corrections": in_range(corrections, lo, hi),
                "theme_hits": in_range(theme_hits, lo, hi)[:120],
                "tool_errors": in_range(tool_errors, lo, hi)[:60],
                "segment_headers": [
                    {
                        "id": s["segment_id"],
                        "ts": s.get("ts_start"),
                        "branch": s.get("gitBranch"),
                        "first_user_text": s.get("first_user_text"),
                        "tools": s.get("tool_histogram"),
                    }
                    for s in segments[i:j]
                ],
                "latest_compaction_summary_head": (latest_summary["text"][: args.summary_head_chars] if latest_summary else None),
                "est_chars": cur_chars,
            }
        )
        i = j

    # If we blew past max-windows, merge adjacent windows pairwise until under cap.
    while len(windows) > args.max_windows:
        merged: list[dict[str, Any]] = []
        for k in range(0, len(windows), 2):
            if k + 1 < len(windows):
                a, b = windows[k], windows[k + 1]
                merged.append(
                    {
                        "lo": a["lo"], "hi": b["hi"],
                        "seg_from": a["seg_from"], "seg_to": b["seg_to"],
                        "corrections": a["corrections"] + b["corrections"],
                        "theme_hits": (a["theme_hits"] + b["theme_hits"])[:120],
                        "tool_errors": (a["tool_errors"] + b["tool_errors"])[:60],
                        "segment_headers": a["segment_headers"] + b["segment_headers"],
                        "latest_compaction_summary_head": b["latest_compaction_summary_head"] or a["latest_compaction_summary_head"],
                        "est_chars": a["est_chars"] + b["est_chars"],
                    }
                )
            else:
                merged.append(windows[k])
        windows = merged

    manifest = []
    for idx, w in enumerate(windows):
        path = os.path.join(args.out, f"window_{idx:02d}.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(w, fh, indent=2, ensure_ascii=False)
        body = len(json.dumps(w, ensure_ascii=False))
        manifest.append(
            {"window": idx, "path": path, "range": f"{w['lo'][:10]}..{w['hi'][:10]}",
             "n_corrections": len(w["corrections"]), "n_theme_hits": len(w["theme_hits"]),
             "packet_chars": body, "approx_tokens": body // 4}
        )
    with open(os.path.join(args.out, "packets_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    print(json.dumps({"windows": len(windows), "max_packet_tokens": max((m["approx_tokens"] for m in manifest), default=0), "manifest": manifest}, indent=2))


if __name__ == "__main__":
    main()
