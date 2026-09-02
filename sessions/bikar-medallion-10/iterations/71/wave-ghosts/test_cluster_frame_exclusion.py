#!/usr/bin/env python3
"""Regression test for #48 (Tenet 18): the construction frame stays OUT of the
shape vocabulary.

Plain English: the owner saw a bogus "round (142×)" card on the /simplify page.
That class was the blueprint construction circles — the frame, not a shape anyone
places. This test freezes the witness that drove the fix: after clustering, NO
canonical class is an unfilled construction circle, and the placeable-shape count
equals the filled faces (not the inflated all-faces count).

Run: /Users/omareid/Workspace/git/qiyas/.venv/bin/python -m pytest \
       iterations/71/wave-ghosts/test_cluster_frame_exclusion.py -q
(or plain `python test_cluster_frame_exclusion.py` — it asserts on import-run.)
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent           # .../iterations/71/wave-ghosts
ITER = HERE.parent.name                            # "71"
SESSION = HERE.parents[2]                          # .../bikar-medallion-10
GT = SESSION / "iterations" / ITER / "pattern.gt.json"
CLUSTERS = HERE / "clusters.json"
SCRIPT = HERE / "cluster_shapes.py"


def _regen():
    """Re-run the clusterer so the test asserts on a FRESH partition, not a stale file."""
    subprocess.run([sys.executable, str(SCRIPT), ITER], check=True,
                   capture_output=True, text=True)


def test_no_construction_circle_class_in_vocabulary():
    """The witness: every gt circle here is an UNFILLED construction circle, so the
    vocabulary must contain ZERO circle classes and exactly the filled faces."""
    _regen()
    gt = json.loads(GT.read_text())
    shapes = gt["shapes"]
    circles = [s for s in shapes if s["type"] == "circle"]
    filled_circles = [s for s in circles
                      if s["params"].get("fill_color") or s["params"].get("face_class")]
    placeable = [s for s in shapes
                 if not (s["type"] == "circle"
                         and not s["params"].get("fill_color")
                         and not s["params"].get("face_class"))]

    data = json.loads(CLUSTERS.read_text())

    # 1. No vocabulary class is the construction frame (the 142× "round" bug).
    circle_classes = [c for c in data["clusters"] if c["kind"] == "circle"]
    assert circle_classes == [], \
        f"construction-circle class leaked back into the vocabulary: {circle_classes!r}"

    # 2. The excluded count equals the unfilled construction circles.
    n_frame = len(circles) - len(filled_circles)
    assert data["n_excluded_frame"] == n_frame, \
        f"excluded {data['n_excluded_frame']} frame circles, expected {n_frame}"

    # 3. The placeable count is the real (deflated) vocabulary base, not all faces.
    assert data["n_placeable"] == len(placeable), \
        f"placeable {data['n_placeable']} != filled-face count {len(placeable)}"
    assert data["n_placeable"] < data["n_shapes"], \
        "frame exclusion did not shrink the vocabulary base"

    # 4. Every emitted class covers >=1 member and sums to the placeable count
    #    (partition is total over placeable shapes).
    covered = sum(c["count"] for c in data["clusters"])
    assert covered == data["n_placeable"], \
        f"classes cover {covered} but {data['n_placeable']} placeable shapes exist"


if __name__ == "__main__":
    test_no_construction_circle_class_in_vocabulary()
    print("OK — #48 frame-exclusion witness holds")
