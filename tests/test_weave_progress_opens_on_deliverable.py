"""Iteration-process fix (2026-06-25): the /weave-progress PAGE opens ON the
deliverable, not a degenerate wave-1 weave-only crop.

Plain English: the owner opened the progress page to judge progress and got a
wave-1 compare crop — "your photo" was a blank white disc and "ours" was a lone
central rosette — and called it: "what visual validation did we do? seems like
none? … our iteration process is broken … fix it." The root cause was that the
page DEFAULTED to the weave-only strap-compare view (flipped=false) with the
wave slider at a low wave, so opening the link landed on the crop-trick the
phased plan diagnosed as the root failure, instead of the finished converged
candidate.

The owner-authorized fix makes the page open ON the deliverable: shapes view
(flipped=true), coloured cells + scalloped edge checked, full disc (wave 22),
and BOTH panels on a WHITE backdrop (matching the reference photo's white page
and the /weave-progress.png deliverable's white card). The weave-only
strap-compare view is still ONE flip away (a debug aid), but it is no longer
the surface the owner lands on.

This test FREEZES that decision (Tenet 18 — the witness that justified the fix
outlives the session) so a future "default back to the weave-only compare"
refactor goes red instead of silently reintroducing the crop-trick landing.
Static string assertions on the server source — no Docker, no running server.
"""
import re
from pathlib import Path

SERVER = Path(__file__).resolve().parent.parent / "tools" / "wave-plan-server.py"


def _src() -> str:
    return SERVER.read_text()


def test_page_defaults_to_shapes_deliverable_view():
    # The page opens in the SHAPES (deliverable) view, not weave-only. The default
    # is a live `let flipped = true;` declaration.
    text = _src()
    assert re.search(r"\blet flipped\s*=\s*true\s*;", text), (
        "the page must default `flipped = true` (shapes/deliverable view) — "
        "`flipped = false` reintroduces the weave-only crop-trick landing"
    )
    assert not re.search(r"\blet flipped\s*=\s*false\s*;", text), (
        "no surviving `let flipped = false;` — that is the broken default"
    )


def test_cells_and_clip_checkboxes_default_checked():
    # Colour-the-cells AND scalloped-edge are ON by default so the first paint is
    # the coloured, clipped deliverable — not the bare weave skeleton.
    text = _src()
    assert re.search(r'<input type="checkbox" id="cells"\s+checked>', text), (
        "the `cells` checkbox must default `checked` (colour the cells)"
    )
    assert re.search(r'<input type="checkbox" id="clip"\s+checked>', text), (
        "the `clip` checkbox must default `checked` (scalloped edge)"
    )


def test_wave_slider_opens_at_full_disc():
    # The wave slider opens at 22 (full disc), so the page shows the WHOLE
    # converged medallion, not a wave-1 crop.
    text = _src()
    m = re.search(r'<input type="range" id="wave"[^>]*value="(\d+)"', text)
    assert m, "the wave slider must exist with a value"
    assert int(m.group(1)) == 22, (
        f"the wave slider must open at 22 (full disc), not {m.group(1)} — a low "
        "wave value lands the owner on a partial-reveal crop"
    )


def test_both_panels_go_white_in_shapes_view():
    # applyPanelBg() swaps both panels to #FFFFFF in the shapes (deliverable) view
    # and #000 in the weave-only view. The deliverable is coloured-tiles-on-WHITE
    # (matching the reference photo's white page + the .png card), so a colour disc
    # floating on black would read as a panel mismatch.
    text = _src()
    assert re.search(r"function applyPanelBg\(\)", text), (
        "applyPanelBg() must exist to track the panel backdrop to the view"
    )
    # The shapes-branch background is white; the weave-branch is black.
    assert re.search(
        r"const bg\s*=\s*flipped\s*\?\s*'#FFFFFF'\s*:\s*'#000'", text
    ), "panel bg must be #FFFFFF when flipped (shapes), #000 otherwise (weave)"
    # And applyRefSrc wires it (fires on flip + init).
    assert re.search(r"function applyRefSrc\(\)[\s\S]{0,400}applyPanelBg\(\)", text), (
        "applyRefSrc() must call applyPanelBg() so the backdrop tracks the flip"
    )


def test_refwrap_initial_paint_is_shapes_on_white():
    # The #refwrap initial inline style + img src must be the shapes-on-white
    # state so there is NO black flash before the JS runs (the page opens ON the
    # deliverable from the very first paint).
    text = _src()
    m = re.search(r'<div id="refwrap"[^>]*style="([^"]*)"[^>]*>\s*<img id="refimg"[^>]*src="([^"]*)"', text)
    assert m, "could not find the #refwrap container + #refimg"
    style, src = m.group(1), m.group(2)
    assert "#FFFFFF" in style or "#ffffff" in style, (
        f"#refwrap must initialise on a WHITE backdrop (got style {style!r})"
    )
    assert "mode=shapes" in src, (
        f"#refimg must initialise to the shapes reference (got src {src!r})"
    )


def test_shapes_reference_renders_tiles_on_white_not_black():
    # The ?mode=shapes reference image fills the non-shape pixels with WHITE
    # (np.full_like(arr, 255)), not black (np.zeros_like), so the reference panel
    # matches the deliverable's white-card polarity.
    text = _src()
    # Find the want_shapes branch and confirm it builds a WHITE-filled array.
    assert re.search(
        r"if want_shapes:[\s\S]{0,1300}np\.full_like\(arr,\s*255", text
    ), (
        "the ?mode=shapes branch must fill non-shape pixels with WHITE "
        "(np.full_like(arr, 255)) — np.zeros_like reintroduces the black backdrop "
        "that mismatches the deliverable's white card"
    )
    # And it must NOT zero-fill (black) the backdrop inside that branch — the old
    # `rgb = np.zeros_like(arr, dtype="uint8")` black-fill line must be gone.
    shapes_branch = re.search(
        r"if want_shapes:([\s\S]{0,1300}?)\n\s+else:", text
    )
    assert shapes_branch, "could not isolate the want_shapes branch"
    assert 'np.zeros_like(arr, dtype="uint8")' not in shapes_branch.group(1), (
        "the ?mode=shapes branch must not zero-fill (black) the backdrop — "
        "`rgb = np.zeros_like(arr, ...)` reintroduces the black reference panel"
    )
