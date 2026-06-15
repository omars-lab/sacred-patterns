#!/usr/bin/env python3
"""Slice the iter-71 recipe to a CUMULATIVE wave-N recipe: blueprint + the
wave-1..N overlay blocks + the fill/classify tail, dropping waves N+1..22.

Plain English (owner, 2026-06-15): the 'Our build' tile should show the picture
built FROM SCRATCH up through wave N — wave 1 = just the central star, wave 22 =
the full medallion. The recipe builds in layers, not waves, so we slice the
pattern body at the `# Wave-N overlay:` comment markers.

WITNESS PROBE (Tenet 17/24): this script's first job is to test whether a
truncated recipe renders 'just waves 1..N' or whether the girih background field
over-colors the whole frame regardless (feedback_slice_truncation_doesnt_isolate).
Render wave 1 and LOOK before trusting the slice.

Usage: slice_recipe.py <N>  ->  prints the wave-1..N recipe to stdout.
"""
import re
import sys
from pathlib import Path

SRC = Path("/Users/omareid/Library/CloudStorage/Dropbox/Data/sacred-patterns/"
           "bikar-medallion-10/iterations/71/pattern.bkr")


def slice_to(n: int) -> str:
    lines = SRC.read_text().splitlines()
    # Find the pattern-body wave-overlay markers (NOT the blueprint '# Wave-N
    # rings' markers — those are construction circles, all kept). The overlay
    # markers say "# Wave-N overlay" and live after `pattern ... on center_star`.
    pat_start = next(i for i, l in enumerate(lines)
                     if l.startswith("pattern "))
    # marker line index -> wave number, only in the pattern body
    markers = []
    for i in range(pat_start, len(lines)):
        m = re.match(r"\s*#\s*Wave-(\d+)\s+overlay", lines[i])
        if m:
            markers.append((i, int(m.group(1))))
    # The fill/classify tail begins at the first `voids detect` after the body.
    tail_start = next(i for i in range(pat_start, len(lines))
                      if lines[i].strip().startswith("voids detect"))

    # Everything before the FIRST overlay marker is the wave-1 base (girih
    # field + hankin star) — always kept. Each marker i..next-marker is one
    # wave's block. Keep blocks for waves <= n; drop the rest (up to tail).
    keep = list(range(0, markers[0][0]))  # blueprint + pattern head + wave-1 base
    for idx, (line_i, wave) in enumerate(markers):
        end = markers[idx + 1][0] if idx + 1 < len(markers) else tail_start
        if wave <= n:
            keep.extend(range(line_i, end))
    keep.extend(range(tail_start, len(lines)))  # fill/classify tail
    return "\n".join(lines[i] for i in keep) + "\n"


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    sys.stdout.write(slice_to(n))
