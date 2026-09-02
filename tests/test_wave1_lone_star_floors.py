"""Phase 0 (2026-06-23): the wave compare uses ONE shared reveal floor — the fixed
ruler — so both panels show the same fraction of their content disc at the same
on-screen size.

Plain English: the "your photo" (reference) panel and the "ours" panel each show a
growing central disc as you step through the 22 waves. For ten rounds the studio
faked "wave N" by cropping the finished picture to a shrinking circle, and the two
panels used DIFFERENT crop floors (OURS_FLOOR 0.34 vs REF_FLOOR 0.19) — tuned by eye
to land the same MOTIF at wave 1, at the cost of showing the two discs at different
on-screen SIZES (owner 2026-06-23: "not same size"). You cannot iterate structure to
correctness while looking through a lens that makes a correct result look wrong.

Phase 0 collapses the two floors into ONE shared floor (SHARED_FLOOR), so a single
`sharedFrac(pf)` reveals the same fraction of each field's inscribed content disc on
both panels. This makes the compare apples-to-apples and lets a NUMBER (qiyas
pixel-diff via /api/pixel-diff) replace the eyeball. The motif difference that the
decoupled floors used to hide at wave 1 is a REAL structural signal (the skeleton
topology question Phase 1 adjudicates), not a crop artifact to tune away.

This test FREEZES the shared-floor decision so a future "just decouple the floors
again to make wave 1 look matched" refactor goes red instead of silently
reintroducing the distorting (size-asymmetric) ruler. It REPLACES the prior
test_floors_are_decoupled_* invariant, which froze the asymmetry we deliberately
undid.
"""
import re
from pathlib import Path

SERVER = Path(__file__).resolve().parent.parent / "tools" / "wave-plan-server.py"


def _read_floats(pattern: str) -> list[float]:
    text = SERVER.read_text()
    return [float(m) for m in re.findall(pattern, text)]


def _read_float(pattern: str) -> float:
    vals = _read_floats(pattern)
    assert vals, f"could not find {pattern!r} in {SERVER}"
    return vals[0]


def test_one_shared_floor_no_decoupled_floors():
    # The fixed ruler: a single SHARED_FLOOR constant, and NO surviving decoupled
    # OURS_FLOOR/REF_FLOOR *constant declarations*. (The comment block may still
    # mention the old names as history; we only forbid live `const`/assignment
    # declarations of them.)
    shared = _read_float(r"const SHARED_FLOOR\s*=\s*([0-9.]+)")
    assert 0.0 < shared < 1.0, f"SHARED_FLOOR ({shared}) must be a fraction in (0,1)"
    text = SERVER.read_text()
    assert not re.search(r"const OURS_FLOOR\s*=", text), \
        "decoupled `const OURS_FLOOR` must be gone — Phase 0 uses one shared floor"
    assert not re.search(r"const REF_FLOOR\s*=", text), \
        "decoupled `const REF_FLOOR` must be gone — Phase 0 uses one shared floor"


def test_both_panels_route_through_shared_frac():
    # oursFrac and refFrac must both delegate to sharedFrac — same fraction on both
    # panels at every wave (the size-symmetry guarantee).
    text = SERVER.read_text()
    assert re.search(r"function sharedFrac\(pf\)", text), "sharedFrac() must exist"
    assert re.search(r"function oursFrac\(pf\)\s*\{\s*return sharedFrac\(pf\)", text), \
        "oursFrac must return sharedFrac(pf)"
    assert re.search(r"function refFrac\(pf\)\s*\{\s*return sharedFrac\(pf\)", text), \
        "refFrac must return sharedFrac(pf)"


def test_png_twin_uses_shared_floor():
    # The shareable /weave-progress.png twin renders OUR field; its python-side
    # SHARED_FLOOR literal must equal the page's const so the surfaced render is the
    # render the owner judges (Tenet 25b).
    page = _read_float(r"const SHARED_FLOOR\s*=\s*([0-9.]+)")
    # The python-side literal: `SHARED_FLOOR = 0.25` (no `const`, indented in a
    # method). Match a `SHARED_FLOOR =` that is NOT preceded by `const `.
    py = _read_float(r"(?<!const )\bSHARED_FLOOR\s*=\s*([0-9.]+)")
    assert abs(page - py) < 1e-9, \
        "PNG-twin SHARED_FLOOR must match the live page's SHARED_FLOOR (Tenet 25b)"


def test_shared_floor_grows_to_full_disc_at_wave_22():
    # frac(pf) = SHARED_FLOOR + pf*(1-SHARED_FLOOR); pf = (w-1)/(waves-1). At wave 22
    # pf=1 so frac=1.0 (the inscribed full disc) regardless of the floor.
    floor = _read_float(r"const SHARED_FLOOR\s*=\s*([0-9.]+)")

    def frac(w: int, waves: int = 22) -> float:
        pf = (w - 1) / (waves - 1)
        return floor + pf * (1 - floor)

    assert abs(frac(22) - 1.0) < 1e-9
    # And at wave 1, frac == the floor (both panels, same value — the whole point).
    assert abs(frac(1) - floor) < 1e-9


def test_pixel_diff_endpoint_wired():
    # Phase 0's numeric verdict: an /api/pixel-diff endpoint exists and shells to the
    # qiyas venv pixel-diff, returning the coverage keys. This is the "match is a
    # number, not an eyeball" guarantee.
    text = SERVER.read_text()
    assert '/api/pixel-diff' in text, "the numeric-verdict endpoint must exist"
    assert 'pixel-diff' in text and 'QIYAS_PY' in text, \
        "the endpoint must shell to the qiyas venv pixel-diff"
    assert 'coverage' in text, "the endpoint must surface coverage.* keys"
