#!/usr/bin/env python3
"""make-structure.py — strip a .bkr pattern down to its line skeleton (Stage 1 of the stage-gated loop).

Plain English: to judge whether a reconstruction's STRUCTURE matches the
reference, we need to look at the geometry alone — no fills, no woven bands,
just the line network. This tool filters a pattern.bkr down to its geometry
statements and appends a fixed black-ink style tail, producing a
structure.bkr whose render is a black-on-white line drawing.

The .bkr statement vocabulary partitions cleanly by stage (the property the
stage-gated process leans on):
  - STRUCTURE (kept):  blueprint, girih, voids, connect, rotate, mirror,
                       layer, face, tile, arc ops, comments — anything that
                       creates or places geometry.
  - COLOR (dropped):   palette, classify, fill, style, animate.
  - WEAVE (dropped):   strapwork (band dressing; its CENTERLINES are
                       decoration geometry and still render as edges).
  - edges (replaced):  the pattern's own edge styling is dropped and replaced
                       by the fixed skeleton tail, so skeletons from different
                       iterations are directly comparable.

Why the tail is fixed (same for every pattern): the skeleton render doubles
as the Stage-2/3 FREEZE CHECK — a color or weave iteration must leave the
skeleton byte-identical. Any styling that varied per pattern would break
that comparison.

Usage:
    ./tools/make-structure.py iterations/39/pattern.bkr > iterations/39/structure.bkr

Example: medallion-10 iter-39's pattern.bkr (girih field + palette + 6
classify + 7 fill + edges + strapwork) reduces to the `girih field ... pockets
star` + `voids detect` statements plus the skeleton tail.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Statements that belong to the COLOR or WEAVE stages. Each is dropped along
# with its indented block body (palette entries, strapwork properties, ...).
DROP_KEYWORDS = {
    "palette",
    "classify",
    "fill",
    "style",
    "animate",
    "strapwork",
    "edges",
}

# Fixed skeleton styling appended to every structure.bkr (2-space pattern-body
# indent). ink width 1.2 is thick enough to survive Canny edge extraction at
# the 1024px raster, thin enough not to merge adjacent field lines.
SKELETON_TAIL = """
  # --- skeleton tail (appended by make-structure.py; identical for every
  # --- pattern so skeleton renders are comparable across iterations) ---
  palette skeleton
      ink = #000000
  edges color ink width 1.2
"""


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def first_token(line: str) -> str:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return ""
    return stripped.split()[0]


def strip_to_structure(source: str) -> str:
    """Drop color/weave statements (with their block bodies) and append the skeleton tail.

    Input (condensed):  "pattern p\\n  girih field decagonal 62\\n  palette x\\n      a = #FF0000\\n  fill void where sides == 3 color a\\n"
    Output:             "pattern p\\n  girih field decagonal 62\\n" + SKELETON_TAIL
    """
    out_lines: list[str] = []
    drop_indent: int | None = None  # indent of the statement being dropped

    for line in source.splitlines():
        blank = not line.strip()
        if drop_indent is not None:
            # Inside a dropped block: blank lines and deeper-indented lines
            # belong to it; the first non-blank line at <= indent ends it.
            if blank or indent_of(line) > drop_indent:
                continue
            drop_indent = None
        if first_token(line) in DROP_KEYWORDS:
            drop_indent = indent_of(line)
            continue
        out_lines.append(line)

    # Trim trailing blank lines before appending the tail.
    while out_lines and not out_lines[-1].strip():
        out_lines.pop()
    return "\n".join(out_lines) + "\n" + SKELETON_TAIL.lstrip("\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pattern", type=Path, help="path to pattern.bkr")
    args = ap.parse_args()

    if not args.pattern.is_file():
        print(f"error: {args.pattern} not found", file=sys.stderr)
        sys.exit(1)

    sys.stdout.write(strip_to_structure(args.pattern.read_text()))


if __name__ == "__main__":
    main()
