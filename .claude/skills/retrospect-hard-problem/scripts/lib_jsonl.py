"""Shared helpers for streaming Claude Code session transcripts.

WHY this module exists: session transcripts reach ~900 MB for a month-long
session. The ONLY safe way to read them is line-by-line — `json.load(file)` or
`jq -s` would load the whole file into memory and OOM. Every consumer in this
skill imports `iter_events` so the no-slurp rule is enforced in one place.

Minimal example:
    >>> from lib_jsonl import iter_events
    >>> kept = [e for e in iter_events("session.jsonl") if e["type"] == "user"]
    # streams the file; never holds more than one parsed line at a time
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from typing import Any

# A single externalized-but-inlined tool_result can be multiple MB. Parsing it
# is pointless for our signals (we keep at most a few hundred chars downstream),
# so cap the raw line before json.loads to bound peak memory per line.
MAX_LINE_BYTES = 2_000_000

# Event types that carry no analytic signal for a retrospective. Dropping them
# before JSON parse is the cheap ~40%-of-lines win named in the plan.
DISCARD_TYPES = frozenset(
    {
        "permission-mode",
        "file-history-snapshot",
        "attachment",
        "queue-operation",
        "last-prompt",
        "ai-title",
        "system",
    }
)

CONTINUATION_MARKER = "This session is being continued from a previous conversation"


def iter_events(path: str, *, keep_discarded_counts: dict[str, int] | None = None) -> Iterator[dict[str, Any]]:
    """Stream one parsed JSON event per line, skipping known-noise types.

    Never holds more than one line in memory. Lines over MAX_LINE_BYTES are
    truncated-and-skipped (counted under '_oversized' if a counter is passed)
    rather than parsed. Malformed lines are skipped (counted under '_malformed').

    If `keep_discarded_counts` is provided, it is mutated in place with a
    histogram of every type encountered (including discarded + kept), so callers
    can report a noise budget.
    """
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            if len(raw) > MAX_LINE_BYTES:
                if keep_discarded_counts is not None:
                    keep_discarded_counts["_oversized"] = keep_discarded_counts.get("_oversized", 0) + 1
                continue
            # Cheap prefix sniff: skip parse for the highest-volume noise types.
            # (Full correctness still relies on the post-parse check below; this
            # is only an optimization for the common case.)
            try:
                obj = json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                if keep_discarded_counts is not None:
                    keep_discarded_counts["_malformed"] = keep_discarded_counts.get("_malformed", 0) + 1
                continue
            etype = obj.get("type", "_none")
            if keep_discarded_counts is not None:
                keep_discarded_counts[etype] = keep_discarded_counts.get(etype, 0) + 1
            if etype in DISCARD_TYPES:
                continue
            yield obj


def content_as_text(message: dict[str, Any] | None) -> str | None:
    """Return the message content IFF it is a plain string, else None.

    Human prompts and compaction summaries have string content. Tool-call /
    tool-result turns have *list* content (blocks). We deliberately treat only
    the string form as a human-authored signal.

    >>> content_as_text({"content": "continue with the plan"})
    'continue with the plan'
    >>> content_as_text({"content": [{"type": "tool_result", "content": "..."}]}) is None
    True
    """
    if not message:
        return None
    c = message.get("content")
    return c if isinstance(c, str) else None


def iter_content_blocks(message: dict[str, Any] | None) -> Iterator[dict[str, Any]]:
    """Yield each content block when message content is a list, else nothing."""
    if not message:
        return
    c = message.get("content")
    if isinstance(c, list):
        for block in c:
            if isinstance(block, dict):
                yield block


def is_compaction_summary(text: str) -> bool:
    return text.lstrip().startswith(CONTINUATION_MARKER)


def text_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]
