# validation.json — sacred-patterns `overall.*` rollup

The shared envelope (top-level shape, `inputs`, `tools.*` conventions, versioning) is defined upstream in `qiyas/docs/validation-envelope.md`. This file documents only the **sacred-patterns-specific `overall.*` block** — the iteration loop's go/no-go rollup, convergence thresholds, and structural-score format.

The split mirrors the weights-file pattern used by `qiyas score`: shared schema in qiyas, per-consumer policy in the consumer.

---

## What's in this doc

- The `overall.*` schema sacred-patterns's orchestrator emits
- Convergence thresholds tied to our iteration philosophy (G1–G5 gates in `CLAUDE.md`)
- Decision rules for `go_no_go` enum values

## What's NOT in this doc

- Top-level shape (`version`, `inputs`, `tools`) — see `qiyas/docs/validation-envelope.md`
- Per-tool slot contents — see each tool's own JSON output schema (qiyas signals documented in qiyas, local signals documented in this repo)
- Cross-consumer envelope rules — see `qiyas/docs/validation-envelope.md`

## Top-level shape (excerpt)

For full envelope shape, see `qiyas/docs/validation-envelope.md`. Sacred-patterns's slice:

```json
{
  "version": "1",
  "envelope_version": "qiyas-1",
  "generated_at": "2026-04-30T14:33:12Z",
  "inputs": { "svg": "...", "reference": "...", "baseline": "..." },
  "tools": { ... },
  "overall": {
    "topology_complete": true,
    "structural_score": "6/7",
    "pixel_similarity": 81.4,
    "composite_score": 0.74,
    "go_no_go": "iterate",
    "blocking_issues": [
      "A6: 2 shapes MISSING (satellite-inner-stars, band-segments)"
    ],
    "warnings": [
      {
        "id": "missing-shapes",
        "source": "diff",
        "severity": "error",
        "message": "2 shape(s) in reference have no match in recon",
        "context": {"missing_count": 2, "counterfactual_score_delta": 0.18},
        "counterfactual_score_delta": 0.18,
        "rank": 1
      }
    ]
  }
}
```

## overall.* field reference

| Field | Type | Required | Description |
|---|---|---|---|
| `topology_complete` | boolean | yes | `validate_svg.exit_code == 0` AND all of `A2_symmetry`, `A4_coverage`, `A5_bands` pass. Mirrors the C1 structural audit's "topology" rollup. |
| `structural_score` | string | yes | `"N/M"` — A6 PASS count over total expected shapes from `baseline.json`. `"n/a"` when no baseline supplied. The G2 hard gate triggers when N < M. |
| `pixel_similarity` | number \| null | no | Median of `tools.svg_diff_vs_*.similarity_pct`. **Regression-detection signal only**, not a convergence target. Null when no svg-diff tools ran. |
| `composite_score` | number \| null | no | `qiyas score`'s composite (`pillars.*` aggregated per `weights/sacred-patterns.json`). Null when `qiyas score` did not run (older Docker image, --skip-qiyas, or non-zero exit). |
| `go_no_go` | string | yes | `"converged"` / `"iterate"` / `"broken"`. Decision rules below. |
| `blocking_issues` | string[] | yes | Human-readable list of what would block convergence. Empty when `go_no_go == "converged"`. The iteration loop's `guidance.md` is grounded in this list. |
| `warnings` | object[] | no | Top-N warnings from `qiyas score`, ranked globally by `counterfactual_score_delta`. Empty when `qiyas score` did not run. **`overall.warnings[0]` is the next-action directive for the iteration agent** — fixing it delivers the largest expected score lift. |

## go_no_go decision rules

These rules encode the convergence philosophy in `CLAUDE.md` (topology > geometry > proportions > coloring) and the G1–G5 hard gates:

- **`"broken"`** — `tools.validate_svg.exit_code != 0` OR any tool errored OR the orchestrator could not produce a valid SVG to analyze. The iteration loop must fix the render before evaluating further (G1: only fix-broken-render edits permitted on a non-rendering iteration).
- **`"converged"`** — ALL of:
  - `topology_complete == true`
  - `structural_score` numerator equals denominator (A6 fully passes; baseline match complete)
  - `pixel_similarity >= 80` (regression detection — not the convergence target, just a sanity floor)
  - When `composite_score` is populated: `composite_score >= 0.85` AND topology pillar `>= 0.95` (per `qiyas/.claude/plans/unified-similarity-score.md`)
- **`"iterate"`** — anything else. The G2 gate determines what the next iteration MUST target: structural improvement when `structural_score` numerator < denominator, otherwise pixel/proportion work.

When `qiyas score` is unavailable (older Docker image, `--skip-qiyas`, or non-zero exit), the rollup falls back to the four pre-score conditions above. `composite_score` and `warnings` stay null/empty in that case, but `go_no_go` still computes from the deterministic A2/A4/A5/A6 + pixel signals. The unavailability is also added to `blocking_issues` so the orchestrator's one-line summary surfaces it loudly.

## No synthesized warnings fallback (intentional)

A previous iteration of the rollup tried to synthesize `overall.warnings` from per-audit `tools.svg_audit.A2/A5/A6.warnings[]` when `qiyas score` was unavailable. That fallback was **removed deliberately**. Reasons:

- **It hides the real failure.** The whole reason we noticed the v0.1.0 image was stale is that empty `overall.warnings` was visible. With a fallback, the next time `qiyas score` regresses (a weight bug, a new pillar that throws), the orchestrator quietly serves synth warnings that look real and the agent acts on them. We lose the diagnostic signal.
- **The synthesized deltas are uncalibrated.** Using `cv` for A2, `1 - crossing_count/expected` for A5, and `(expected-found)/expected/N` for A6 produces a ranking dominated by whichever audit happens to have the largest raw severity number — not by which fix would actually move the composite score most. That's wrong apportionment dressed up as a ranked priority list.
- **Per-audit warnings are still accessible.** They live in `tools.svg_audit.A2/A5/A6.warnings[]`. Anyone debugging can read them directly. The orchestrator's `blocking_issues` already surfaces them in human form. The fallback wasn't surfacing new info; it was re-shaping existing info into a slot whose meaning should be specific (qiyas-score-ranked).
- **"Fail loud" is the right policy here.** When `qiyas score` is unavailable, the right move is to fix the score tool — not paper over it. Putting a fallback in front removes the pressure to keep the real path healthy.

If a future contributor is tempted to re-add this fallback: read `qiyas/docs/issues/2026-05-02-orchestrator-warnings-empty-when-score-unavailable.md` first, particularly the path from "Option D" (originally chosen) to the eventual revert.

## Why these thresholds

- **`pixel_similarity >= 80`** — regression floor, calibrated against ~90 iterations on bikar-medallion-10. Below 80 indicates a render regression worth investigating; above 80 says nothing about convergence quality.
- **`composite_score >= 0.85`** — sacred-patterns convergence target per `unified-similarity-score.md`. Calibrate against the converged-iteration corpus (task #26) once `qiyas score` is available.
- **Topology pillar `>= 0.95`** — encodes "topology before geometry" from the convergence hierarchy. A pattern with broken topology cannot earn convergence from good colors.

These thresholds are sacred-patterns-specific. BIKAR's `validation-overall.md` (when it exists) will define its own.

## Versioning

`version: "1"` on the consumer-side schema. Bumped when this doc's `overall.*` schema changes:

- **Patch** (`"1"` → `"1.1"`): adding optional fields. No orchestrator migration required.
- **Major** (`"1"` → `"2"`): renaming/removing keys, changing `go_no_go` enum values, changing types.

The envelope's `envelope_version` is independent and bumped by qiyas. A given `validation.json` is interpretable by the pair `(envelope_version, version)`.

## What this rollup deliberately does NOT include

- A single normalized "score" computed locally — that's `qiyas score`'s job (Phase 3). Until then, `pixel_similarity` is the only numeric rollup, and it's diagnostic-only.
- Per-shape geometric error vectors — those live inside each tool's own JSON.
- Recommendations for the next iteration — that's `iteration-guide.md`'s job; this doc is data only.
- Pattern-family-specific weighting — when `qiyas score` is wired in, `weights/sacred-patterns.json` carries the policy.
