#!/usr/bin/env python3
"""Generate the per-wave CUMULATIVE recipe family wave-1.bkr … wave-22.bkr.

Plain English (owner reframe, 2026-06-15): instead of one monolithic recipe
with `wave N` markers, the owner wants to SEE THE CODE GROW — wave-1.bkr is the
blueprint + just wave 1, wave-2.bkr adds wave 2's lines, …, wave-22.bkr is the
complete master. The /waves "Our build" tile renders wave-N.bkr; the code-diff
tile diffs wave-(N-1).bkr → wave-N.bkr to show exactly what wave N added.

Why this is only NOW possible (Tenet 23/26): a naive recipe slice over-colors —
the `girih field` paints the whole backdrop via `fill void where sides==N`
regardless of which wave's connects are present (witness:
PROBE-wave1-slice-overcolors.png, feedback_slice_truncation_doesnt_isolate).
The bikar wave-provenance engine (data-wave per face) lets us scope every fill
rule by `and wave <= N`, so wave-N.bkr genuinely shows only waves 1..N in color
and the rest blank — the owner's "Only waves 1..N, rest blank" choice.

Two structural regions of the master (iterations/71/pattern.bkr):
  HEADER  : blueprint block + `pattern … on center_star` + wave-1 base
            (girih field + hankin star), up to the first `# Wave-N overlay`.
  BODY    : the `# Wave-N overlay` blocks, each prefixed `wave N`.
  TAIL    : from `voids detect` onward — palette, classify, fill void, edges.

A wave-N file = HEADER + BODY[wave 1..N] + TAIL(scoped to `wave <= N`).

Usage:
  generate_wave_files.py            # writes wave-1.bkr … wave-22.bkr here
  generate_wave_files.py --stdout N # prints wave-N recipe to stdout (no write)
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "pattern.bkr"
MAX_WAVE = 22

# The bikar CLI (renders .bkr -> .svg) and the wave-ghosts dir the portal serves
# the "Our build" tile from. Each wave-N.bkr renders to wave-{n}-build.png there.
BIKAR_CLI = Path("/Users/omareid/Workspace/git/bikar/packages/cli/dist/index.js")
GHOSTS_DIR = HERE.parent / "wave-ghosts"
BUILD_PX = 1024

# Every tail fill/classify rule in this recipe colours a DECORATIVE SHAPE,
# selected by `layer == K` (the star at layer 1, the wave families at layers
# 2..6). These rules self-scope: a `layer == 2` fill only colours faces that
# exist, and an un-built wave emits no layer-2 faces — so each rule fires
# correctly whenever its wave is present and is a no-op otherwise. We therefore
# keep every tail rule verbatim in every wave file.
#
# Historical note (owner 2026-06-15): an earlier recipe also carried a GIRIH
# BACKDROP — a girih field whose faces were coloured GEOMETRICALLY (by
# `sides`/`ring`/`source`, with no layer pin). The owner dropped it: the
# reference is shapes-on-WHITE, and the convex girih field overshot the
# scalloped flower edge and diverged the image (RMSE 0.404 with vs 0.368
# without). `_scope_tail_line` below survives as a harmless guard: should a
# non-layer-pinned (geometric) rule ever reappear, it would be deferred to the
# final wave rather than silently painting every intermediate snapshot.
_RULE_RE = re.compile(r"^\s*(?:fill void|classify \.\w+)\s+where\s+(?P<cond>.*)$")
# A rule is "decorative" iff its condition pins a layer (the star/family channels).
_LAYER_PIN_RE = re.compile(r"\blayer\s*(==|<=|<|>=|>)\s*\d")


def _scope_tail_line(line: str, n: int) -> str:
    """Keep decorative-shape (layer-pinned) rules verbatim. This recipe has no
    geometric (non-layer-pinned) rules anymore, so this is a no-op on the current
    master; it survives only as a guard — any future geometric rule would be
    deferred to the final wave instead of painting every snapshot. Idempotent."""
    m = _RULE_RE.match(line)
    if not m:
        return line
    if _LAYER_PIN_RE.search(m.group("cond")):
        return line  # decorative-shape rule — self-scopes, keep as-is
    if n >= MAX_WAVE:
        return line  # final wave — would reveal a geometric rule, if any existed
    # Geometric rule, not the final wave: comment out so the snapshot stays clean.
    return f"  # [geometric rule deferred to wave {MAX_WAVE}] {line.strip()}"


# A wave block is delimited by the `wave N` STATEMENT itself (not the
# `# Wave-N overlay` comment) — the statement is what the engine reads and the
# only marker guaranteed present and contiguous (the comment markers skip
# wave 2, whose blurb is folded into wave 1's comment block). Matches an
# indented `wave <int>` line inside the pattern body.
_WAVE_STMT_RE = re.compile(r"^\s+wave\s+(\d+)\s*$")


def slice_to(n: int, scope_field: bool = True) -> str:
    lines = SRC.read_text().splitlines()
    pat_start = next(i for i, l in enumerate(lines) if l.startswith("pattern "))

    # Pattern-body `wave N` statements: (line index, wave number), in order.
    markers = []
    for i in range(pat_start, len(lines)):
        m = _WAVE_STMT_RE.match(lines[i])
        if m:
            markers.append((i, int(m.group(1))))

    tail_start = next(i for i in range(pat_start, len(lines))
                      if lines[i].strip().startswith("voids detect"))

    def _block_start(stmt_i: int, floor: int) -> int:
        """A wave's `# Wave-N overlay` comment sits just ABOVE its `wave N`
        statement. Back the block start up over that leading comment/blank run
        so the intro comment travels WITH the wave it introduces (the diff for
        wave N then reads as "comment explaining wave N, then wave N's lines").
        `floor` stops the walk from eating the previous wave's own statement."""
        s = stmt_i
        while s - 1 > floor and (not lines[s - 1].strip()
                                 or lines[s - 1].lstrip().startswith("#")):
            s -= 1
        return s

    # Everything before wave 1's comment block (blueprint + pattern head) is
    # always kept; each wave block runs from its leading comment to the next
    # wave's leading comment. Keep blocks with wave <= n.
    first_start = _block_start(markers[0][0], pat_start)
    keep = list(range(0, first_start))  # blueprint + pattern head
    for idx, (line_i, wave) in enumerate(markers):
        start = _block_start(line_i, markers[idx - 1][0] if idx > 0 else pat_start)
        if idx + 1 < len(markers):
            end = _block_start(markers[idx + 1][0], line_i)
        else:
            end = tail_start
        if wave <= n:
            keep.extend(range(start, end))

    out = [lines[i] for i in keep]
    # Tail: optionally scope each field fill/classify rule to `wave <= n`.
    for i in range(tail_start, len(lines)):
        out.append(_scope_tail_line(lines[i], n) if scope_field else lines[i])

    header = (f"# AUTO-GENERATED by waves/generate_wave_files.py — wave-{n} of "
              f"{MAX_WAVE} cumulative snapshots. Do not edit by hand; edit the\n"
              f"# master iterations/71/pattern.bkr and re-run the generator.\n"
              f"# This file = blueprint + waves 1..{n}; decorative shapes on "
              f"white (no background field — the reference is shapes-on-white).\n"
              f"# (owner 2026-06-15: wave-1 = lone star; girih backdrop dropped.)\n")
    return header + "\n".join(out) + "\n"


def _svg_to_png(svg: Path, png: Path) -> None:
    subprocess.run(["magick", str(svg), "-resize", f"{BUILD_PX}x{BUILD_PX}",
                    "-background", "white", "-flatten", str(png)],
                   check=True, capture_output=True)


def _render_build_png(n: int) -> None:
    """Render wave-{n}.bkr -> wave-ghosts/wave-{n}-build.png (the portal's 'Our
    build' tile). node bikar render -> svg, then magick svg -> flattened png."""
    bkr = HERE / f"wave-{n}.bkr"
    svg = GHOSTS_DIR / f"wave-{n}-build.svg"
    subprocess.run(["node", str(BIKAR_CLI), "render", str(bkr), "-o", str(svg)],
                   check=True, capture_output=True)
    _svg_to_png(svg, GHOSTS_DIR / f"wave-{n}-build.png")


# A face <path> in the cumulative render carries its construction-pass tag
# data-wave="K". To show "just wave n's shapes" we ghost every face whose K != n
# to white (so only wave n's faces keep their colour on a clean page). This is
# the data-wave-authoritative isolation (Tenet 23): no geometry re-derivation,
# the renderer already told us which wave each face belongs to.
_PATH_RE = re.compile(r"<path\b[^>]*\bdata-wave=\"(\d+)\"[^>]*/>")
_FILL_RE = re.compile(r'\bfill="[^"]*"')
_STROKE_RE = re.compile(r'\bstroke="[^"]*"')


def _ghost_other_waves(svg_text: str, n: int) -> str:
    """Rewrite every face NOT tagged data-wave==n to fill white / no stroke,
    leaving wave n's faces untouched. Faces already `fill="none"` (the unfilled
    girih field) stay invisible. Idempotent for a given n."""
    def repl(m: "re.Match[str]") -> str:
        tag = m.group(0)
        if int(m.group(1)) == n:
            return tag  # keep wave n's faces as-is
        tag = _FILL_RE.sub('fill="#FFFFFF"', tag)
        tag = _STROKE_RE.sub('stroke="none"', tag)
        return tag
    return _PATH_RE.sub(repl, svg_text)


def _render_iso_png(n: int) -> None:
    """Render wave-{n}-iso.png = ONLY wave n's shapes on white (the portal's
    'Just this wave's shapes' tile). Built from the SAME cumulative wave-n.bkr
    render as the 'Our build' tile, then ghosting every face whose data-wave!=n.
    For n==1 this keeps all wave-1 faces, so wave-1-iso == wave-1-build exactly
    (the owner's invariant: the first wave's 'our build' and 'just this wave'
    must match — nothing was built before it)."""
    src_svg = GHOSTS_DIR / f"wave-{n}-build.svg"  # produced by _render_build_png
    iso_svg = GHOSTS_DIR / f"wave-{n}-iso.svg"
    iso_svg.write_text(_ghost_other_waves(src_svg.read_text(), n))
    _svg_to_png(iso_svg, GHOSTS_DIR / f"wave-{n}-iso.png")


def _self_check() -> None:
    """Freeze the two invariants the 2026-06-15 slicing bug exposed (Tenet 18).

    The bug: the slicer keyed off `# Wave-N overlay` COMMENT markers, but the
    master folds wave 2's blurb into wave 1's comment block (no standalone
    `# Wave-2 overlay` line), so wave 2's geometry silently vanished and
    wave-1.bkr === wave-2.bkr (identical line counts, empty diff). Switching to
    the `wave N` STATEMENT as the delimiter fixed it. These asserts catch any
    return of that class of bug on every regen:

      (1) every wave 1..MAX appears as a `wave N` statement (none dropped);
      (2) line counts grow strictly monotonically (each wave adds ≥1 line);
      (3) wave-MAX is the WHOLE master — its body (minus the auto-header) is a
          suffix-preserving superset that ends at the same tail. We assert the
          last non-blank line matches the master's, a cheap proxy for "the
          final snapshot is the complete recipe."
    """
    lines = SRC.read_text().splitlines()
    found = {int(m.group(1))
             for l in lines if (m := _WAVE_STMT_RE.match(l))}
    missing = set(range(1, MAX_WAVE + 1)) - found
    assert not missing, f"master is missing `wave N` statements: {sorted(missing)}"

    counts = [len(slice_to(n).splitlines()) for n in range(1, MAX_WAVE + 1)]
    bad = [(n, counts[n - 1]) for n in range(2, MAX_WAVE + 1)
           if counts[n - 1] <= counts[n - 2]]
    assert not bad, f"wave files not strictly growing (wave, lines): {bad}"

    master_last = next(l for l in reversed(lines) if l.strip())
    wave_max_last = next(l for l in reversed(slice_to(MAX_WAVE).splitlines())
                         if l.strip())
    assert wave_max_last == master_last, (
        f"wave-{MAX_WAVE} tail diverges from master: "
        f"{wave_max_last!r} != {master_last!r}")
    print(f"self-check OK: {MAX_WAVE} waves present, monotonic, "
          f"wave-{MAX_WAVE} tail == master")


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "--stdout":
        sys.stdout.write(slice_to(int(sys.argv[2])))
        return
    _self_check()
    render = "--no-render" not in sys.argv
    for n in range(1, MAX_WAVE + 1):
        (HERE / f"wave-{n}.bkr").write_text(slice_to(n))
    print(f"wrote wave-1.bkr … wave-{MAX_WAVE}.bkr to {HERE}")
    if render:
        GHOSTS_DIR.mkdir(exist_ok=True)
        for n in range(1, MAX_WAVE + 1):
            _render_build_png(n)        # 'Our build' tile (cumulative 1..n)
            _render_iso_png(n)          # 'Just this wave's shapes' tile (only n)
        print(f"rendered wave-{{1..{MAX_WAVE}}}-build.png + -iso.png to {GHOSTS_DIR}")
        _check_wave1_iso_equals_build()  # owner's invariant (Tenet 18 witness)


def _check_wave1_iso_equals_build() -> None:
    """Owner invariant (2026-06-15) frozen as a post-render check (Tenet 18):
    wave 1 is the FIRST wave, so 'Our build' (cumulative through 1) and 'Just
    this wave's shapes' (only wave 1) must be the SAME image — nothing was built
    before it. `magick compare -metric AE` returns the count of differing pixels
    (0 == identical). The legacy iso artifact failed this (a sliver, not the
    star); this catches any regression of that decoupling."""
    build = GHOSTS_DIR / "wave-1-build.png"
    iso = GHOSTS_DIR / "wave-1-iso.png"
    r = subprocess.run(["magick", "compare", "-metric", "AE",
                        str(build), str(iso), "null:"],
                       capture_output=True, text=True)
    # compare writes the AE count to stderr and exits non-zero when > 0.
    ae = (r.stderr or r.stdout).strip().split()[0]
    assert ae in ("0", "0.0"), (
        f"wave-1 'Our build' != 'Just this wave's shapes' (AE={ae} px). "
        "The first wave's cumulative and isolated tiles must match.")
    print("post-render check OK: wave-1 build == iso (pixel-identical)")


if __name__ == "__main__":
    main()
