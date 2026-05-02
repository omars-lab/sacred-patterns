#!/usr/bin/env python3
"""Roll up per-tool outputs into a single validation.json.

Called by iteration-validate.sh. Reads each tool's output from disk and
emits the schema documented in docs/validation-overall.md (sacred-patterns
overall.* rollup) and qiyas/docs/validation-envelope.md (shared envelope).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path
from statistics import median


SCHEMA_VERSION = "1"


def parse_validate_log(log_path: Path) -> dict:
    """validate-svg.sh emits PASS/FAIL lines per check. Parse them."""
    if not log_path.exists():
        return {"checks": {}, "stdout": ""}

    text = log_path.read_text(encoding="utf-8", errors="replace")
    checks: dict[str, str] = {}
    # Lines look like "  ✓ Has xmlns" / "  ✗ Missing xmlns" or "  PASS: ..."
    for line in text.splitlines():
        stripped = line.strip()
        # Match common patterns from validate-svg.sh
        m = re.match(r"^[✓✗xX*✓✗].*?([A-Za-z][A-Za-z0-9 _-]+)$", stripped)
        if m:
            label = m.group(1).strip()
            status = "PASS" if stripped[0] in "✓✓" else "FAIL"
            checks[label] = status
    return {"checks": checks, "stdout": text}


def parse_diff_stats(diff_dir: Path) -> dict:
    """qiyas pixel-diff emits pixel-diff.json with the structured schema."""
    json_path = diff_dir / "pixel-diff.json"
    if not json_path.exists():
        return {"available": False, "output_dir": str(diff_dir)}

    try:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"available": False, "output_dir": str(diff_dir), "error": f"JSON decode error: {e}"}

    out: dict = {"available": True, "output_dir": str(diff_dir)}
    if "similarity_pct" in payload:
        out["similarity_pct"] = float(payload["similarity_pct"])
    if "color_match_pct" in payload:
        out["color_match_pct"] = float(payload["color_match_pct"])
    coverage = payload.get("coverage", {})
    if "shared_pct" in coverage:
        out["coverage_shared_pct"] = float(coverage["shared_pct"])
    if "only_a_pct" in coverage:
        out["coverage_only_a_pct"] = float(coverage["only_a_pct"])
    if "only_b_pct" in coverage:
        out["coverage_only_b_pct"] = float(coverage["only_b_pct"])
    if "background_pct" in coverage:
        out["coverage_background_pct"] = float(coverage["background_pct"])
    if "channel_diffs" in payload:
        out["channel_diffs"] = payload["channel_diffs"]
    return out


def load_svg_audit(json_path: Path) -> dict:
    """qiyas svg-audit emits {audits: {A1, A2, A4, A5, A6?}, ...}.

    Translate to the flat A2_symmetry/A4_coverage/A5_bands/A6_baseline shape
    that compute_overall() consumes. The translation is deliberate and not
    a passthrough: svg-audit's per-audit envelope (status/score/etc.) is
    surfaced under stable keys so the rollup logic stays stable across the
    arch-audit → svg-audit swap.
    """
    if not json_path.exists():
        return {"available": False}
    try:
        raw = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"available": False, "error": f"JSON decode error: {e}"}

    audits = raw.get("audits", {})
    out: dict = {
        "available": True,
        "schema_version": raw.get("schema_version"),
        "qiyas_version": raw.get("qiyas_version"),
        "n_fold": raw.get("n_fold"),
        "audits_run": raw.get("audits_run", []),
        "audits_skipped": raw.get("audits_skipped", []),
        "score": raw.get("score"),
        "warnings": raw.get("warnings", []),
    }

    if "A1" in audits:
        out["A1_census"] = audits["A1"]
    if "A2" in audits:
        out["A2_symmetry"] = audits["A2"]
    if "A4" in audits:
        a4 = dict(audits["A4"])
        # Mirror arch-audit's "medallion_pct" alias for back-compat readers.
        if "coverage_pct" in a4 and "medallion_pct" not in a4:
            a4["medallion_pct"] = a4["coverage_pct"]
        out["A4_coverage"] = a4
    if "A5" in audits:
        out["A5_bands"] = audits["A5"]
    if "A6" in audits:
        out["A6_baseline"] = audits["A6"]
    return out


def load_qiyas(qiyas_dir: Path | None, ran: bool) -> dict:
    """qiyas validate emits diff.json with shape pairs and per-shape errors."""
    if not ran or qiyas_dir is None:
        return {"available": False}
    diff_path = qiyas_dir / "diff.json"
    if not diff_path.exists():
        return {"available": False}
    try:
        d = json.loads(diff_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"available": False, "error": f"JSON decode error: {e}"}

    # Pull out the headline metrics. Schema specifics are best-effort —
    # the full diff.json is preserved at qiyas_dir/diff.json for drill-down.
    ref_enc_path = qiyas_dir / "ref.encoding.json"
    recon_enc_path = qiyas_dir / "recon.encoding.json"

    def _dominant_fold(p: Path) -> int | None:
        if not p.exists():
            return None
        try:
            enc = json.loads(p.read_text(encoding="utf-8"))
            return enc.get("symmetry", {}).get("dominant_fold")
        except (json.JSONDecodeError, KeyError):
            return None

    matched = d.get("matched", [])
    missing_in_recon = d.get("missing_in_recon", [])
    extra_in_recon = d.get("extra_in_recon", [])
    ambiguous = d.get("ambiguous", [])
    scores = d.get("scores", {})

    total_ref = len(matched) + len(missing_in_recon)
    shape_match_pct = (len(matched) / total_ref * 100) if total_ref > 0 else None

    return {
        "available": True,
        "dominant_fold_ref": _dominant_fold(ref_enc_path),
        "dominant_fold_recon": _dominant_fold(recon_enc_path),
        "shape_match_pct": round(shape_match_pct, 1) if shape_match_pct is not None else None,
        "matched_count": len(matched),
        "missing_in_recon_count": len(missing_in_recon),
        "extra_in_recon_count": len(extra_in_recon),
        "ambiguous_count": len(ambiguous),
        "scores": scores,
        "report_html": str(qiyas_dir / "report.html"),
        "output_dir": str(qiyas_dir),
    }


def load_qiyas_score(json_path: Path | None) -> dict:
    """qiyas score emits the §D5b composite + ranked warnings JSON."""
    if json_path is None or not json_path.exists():
        return {"available": False}
    try:
        return {"available": True, **json.loads(json_path.read_text(encoding="utf-8"))}
    except json.JSONDecodeError as e:
        return {"available": False, "error": f"JSON decode error: {e}"}


def compute_overall(
    *,
    validate_exit: int,
    svg_audit: dict,
    diff_traced: dict,
    diff_jpg: dict,
    qiyas: dict,
    qiyas_score: dict,
    has_baseline: bool,
) -> dict:
    """Apply the decision rules from docs/validation-overall.md."""
    blocking: list[str] = []

    if validate_exit != 0:
        blocking.append(f"validate-svg failed (exit {validate_exit})")

    a2 = svg_audit.get("A2_symmetry", {}) if svg_audit.get("available") else {}
    a4 = svg_audit.get("A4_coverage", {}) if svg_audit.get("available") else {}
    a5 = svg_audit.get("A5_bands", {}) if svg_audit.get("available") else {}
    a6 = svg_audit.get("A6_baseline") if svg_audit.get("available") else None

    a2_status = a2.get("status")
    a4_status = a4.get("status")
    a5_status = a5.get("status")

    if a2_status and a2_status not in ("EXACT", "APPROXIMATE"):
        blocking.append(f"A2 symmetry: {a2_status}")
    if a4_status and a4_status != "FULL":
        blocking.append(f"A4 coverage: {a4_status} ({a4.get('medallion_pct')}%)")
    if a5_status and a5_status != "COMPLETE":
        blocking.append(f"A5 bands: {a5_status}")

    structural_score = "n/a"
    if a6 is not None:
        structural_score = a6.get("score", "n/a")
        missing = [s for s in a6.get("shapes", []) if s.get("status") in ("MISSING", "PARTIAL")]
        if missing:
            ids = ", ".join(s["id"] for s in missing[:5])
            blocking.append(f"A6: {len(missing)} shape(s) MISSING/PARTIAL ({ids})")

    pixel_scores = [
        s.get("similarity_pct")
        for s in (diff_traced, diff_jpg)
        if s.get("available") and s.get("similarity_pct") is not None
    ]
    pixel_similarity = round(median(pixel_scores), 1) if pixel_scores else None

    topology_complete = (
        validate_exit == 0
        and a2_status in ("EXACT", "APPROXIMATE")
        and a4_status == "FULL"
        and a5_status == "COMPLETE"
    )

    # qiyas score outputs (slice 7 of #39): composite + top-N ranked
    # warnings. `available=False` when the older Docker image without
    # `qiyas score` was used or the command exited non-zero.
    composite_score = qiyas_score.get("score") if qiyas_score.get("available") else None
    score_warnings = (qiyas_score.get("warnings") or []) if qiyas_score.get("available") else []
    topology_pillar = None
    if qiyas_score.get("available"):
        pillars = qiyas_score.get("pillars") or {}
        topology_pillar = pillars.get("topology")

    # go/no/go decision
    if validate_exit != 0 or svg_audit.get("error"):
        go_no_go = "broken"
    elif (
        topology_complete
        and a6 is not None
        and a6.get("pass_count") == a6.get("total_count")
        and pixel_similarity is not None
        and pixel_similarity >= 80
        and (
            # When composite is available, additionally require the
            # convergence thresholds from validation-overall.md.
            composite_score is None
            or (
                composite_score >= 0.85
                and (topology_pillar is None or topology_pillar >= 0.95)
            )
        )
    ):
        go_no_go = "converged"
    else:
        go_no_go = "iterate"

    return {
        "topology_complete": topology_complete,
        "structural_score": structural_score,
        "pixel_similarity": pixel_similarity,
        "composite_score": composite_score,
        "go_no_go": go_no_go,
        "blocking_issues": blocking,
        "warnings": score_warnings,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--svg", required=True)
    p.add_argument("--reference", required=True)
    p.add_argument("--reference-traced")
    p.add_argument("--baseline")
    p.add_argument("--validate-svg-exit", type=int, required=True)
    p.add_argument("--validate-svg-log", required=True)
    p.add_argument("--diff-traced-dir")
    p.add_argument("--diff-jpg-dir", required=True)
    p.add_argument("--svg-audit-json", required=True)
    p.add_argument("--qiyas-ran", type=int, default=0)
    p.add_argument("--qiyas-dir")
    p.add_argument("--qiyas-score-json", help="Path to qiyas score output JSON.")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    validate_svg = {
        "exit_code": args.validate_svg_exit,
        **parse_validate_log(Path(args.validate_svg_log)),
    }

    diff_traced = (
        parse_diff_stats(Path(args.diff_traced_dir))
        if args.diff_traced_dir
        else {"available": False}
    )
    diff_jpg = parse_diff_stats(Path(args.diff_jpg_dir))
    svg_audit = load_svg_audit(Path(args.svg_audit_json))
    qiyas = load_qiyas(
        Path(args.qiyas_dir) if args.qiyas_dir else None,
        bool(args.qiyas_ran),
    )
    qiyas_score = load_qiyas_score(
        Path(args.qiyas_score_json) if args.qiyas_score_json else None
    )

    overall = compute_overall(
        validate_exit=args.validate_svg_exit,
        svg_audit=svg_audit,
        diff_traced=diff_traced,
        diff_jpg=diff_jpg,
        qiyas=qiyas,
        qiyas_score=qiyas_score,
        has_baseline=bool(args.baseline),
    )

    payload = {
        "version": SCHEMA_VERSION,
        "generated_at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "inputs": {
            "svg": args.svg,
            "reference": args.reference,
            **({"reference_traced": args.reference_traced} if args.reference_traced else {}),
            **({"baseline": args.baseline} if args.baseline else {}),
        },
        "overall": overall,
        "tools": {
            "validate_svg": validate_svg,
            **({"svg_diff_vs_traced": diff_traced} if args.diff_traced_dir else {}),
            "svg_diff_vs_jpg": diff_jpg,
            "svg_audit": svg_audit,
            **({"qiyas": qiyas} if qiyas.get("available") or args.qiyas_ran else {}),
            **({"qiyas_score": qiyas_score} if qiyas_score.get("available") else {}),
        },
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    # Print one-line summary
    o = overall
    bi = f" — {len(o['blocking_issues'])} blocker(s)" if o["blocking_issues"] else ""
    composite = f"  composite={o['composite_score']}" if o.get("composite_score") is not None else ""
    top_warning = ""
    if o.get("warnings"):
        first = o["warnings"][0]
        top_warning = f"  top_warning={first.get('id')}"
    print(
        f"  go_no_go={o['go_no_go']}  topology={'OK' if o['topology_complete'] else 'incomplete'}  "
        f"structural={o['structural_score']}  pixel={o['pixel_similarity']}%"
        f"{composite}{top_warning}{bi}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
