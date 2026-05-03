# Image validation — design doc

Status: agreed
Owners: sacred-patterns + qiyas
Companions:
- `qiyas/docs/sacred-patterns-integration.md` — architecture, divergence policy, A5 contingency (qiyas-side authoritative copy)
- `.claude/plans/qiyas-integration.md` — the *whether* and *how* of bringing qiyas in at all
- `.claude/plans/is-there-an-actionalble-logical-cascade.md` — sequenced migration plan
- `qiyas/docs/validation-envelope.md` — shared envelope (top-level shape, `inputs`, `tools.*` slots)
- `docs/validation-overall.md` — sacred-patterns `overall.*` rollup (go/no-go, thresholds)

This document keeps the parts of the design that are sacred-patterns-side: what `validation.json` carries, what stays in sacred-patterns, what the iteration-loop costs are. The architecture and divergence policy live in qiyas because they govern qiyas's surface; we cross-reference rather than duplicate.

---

## 1. Decisions

The five decisions this document encodes. Everything below elaborates; nothing below contradicts.

1. **qiyas is the canonical pattern-analysis library.** Anything that asks "what's in this pattern, and how does it compare to another?" is a qiyas question, regardless of input format (image or SVG).
2. **sacred-patterns is the pattern-construction-and-iteration product.** It owns pattern construction code, the iteration loop, the interpret-pattern UX, and the orchestrator that produces `validation.json`.
3. **The boundary is role, not input format.** See `qiyas/docs/sacred-patterns-integration.md` §Architecture for the responsibility split.
4. **`validation.json` is the contract between the two.** A single rollup file produced by `tools/iteration-validate.sh`, consumed by every downstream view (evaluation.md, retrospectives, dashboards). This is the user-facing centralization. Schema split: shared envelope upstream at `qiyas/docs/validation-envelope.md`, sacred-patterns `overall.*` rollup at `docs/validation-overall.md`. Mirrors the weights-file pattern: shared schema in qiyas, per-consumer policy in the consumer.
5. **When qiyas and any local tool disagree, we fix qiyas.** Divergences are qiyas-iteration fuel, not justifications for parallel tools. Full policy at `qiyas/docs/sacred-patterns-integration.md` §Divergence policy.

---

## 2. The signals in the iteration loop

Every signal the iteration loop consumes, where it lives in the target architecture, and what unique question it answers.

| Signal | Owner | What it answers |
|---|---|---|
| `qiyas encode` | qiyas | Structural fingerprint of an image or SVG: every detected shape, position, params, dominant fold |
| `qiyas diff` / `qiyas validate` | qiyas | Reference-grounded shape pairing, rotation-aware structural diff, composite score |
| `qiyas pixel-diff` | qiyas (Phase 2) | Pixel similarity %, visual overlay, heatmap |
| `qiyas zone-audit` | qiyas (Phase 2) | Per-ring match quality, strapwork gap analysis |
| `qiyas svg-audit` | qiyas (Phase 3) | A1 semantic census, A2 sector symmetry, A4 coverage, A5 band-network integrity, A6 baseline match |
| `qiyas review` | qiyas | Browser portal for verdicting individual shapes |
| `validate-svg.sh` | sacred-patterns | XML well-formedness preflight (xmlns, no wrapper artifacts) |
| Visual screenshot | Claude/user | Gestalt judgment ("does this look broken?") |
| `interpret-pattern` skill | sacred-patterns | Interactive UX for authoring `baseline.json` (user-verified shape expectations) |
| `iteration-validate.sh` | sacred-patterns | Orchestrator: runs qiyas signals + validate-svg, writes `validation.json` |

The unifying observation: every analytical question — image-vs-image, SVG-vs-SVG, image-vs-SVG, SVG-vs-baseline — is the same family of question (*what shapes does this pattern contain, and how does it compare?*). One library answers them. Sacred-patterns supplies inputs (the SVG it just rendered, the user-authored baseline) and consumes the rollup.

---

## 3. Architecture

See `qiyas/docs/sacred-patterns-integration.md` §Architecture for the full diagram and responsibility table. Short version: qiyas owns analysis (regardless of input format); sacred-patterns owns construction, the iteration UX, the interpret-pattern baseline-authoring tool, and the `iteration-validate.sh` orchestrator.

---

## 4. The unified rollup — `validation.json`

The orchestrator (`tools/iteration-validate.sh`) is the piece that makes the federation feel like one tool from the iteration loop's perspective. It runs every signal qiyas produces, plus the local validate-svg preflight, and writes a single rollup file. The schema is split: the shared envelope (top-level shape, `tools.*` conventions, versioning) is documented upstream at `qiyas/docs/validation-envelope.md`; the sacred-patterns-specific `overall.*` rollup (go/no-go rules, convergence thresholds) is documented at `docs/validation-overall.md`.

The iteration loop reads `overall.*` for go/no-go decisions; humans drill into `tools.*` for diagnosis. evaluation.md, retrospective.md, and the dashboard all consume this file instead of re-running tools or parsing their text output.

This is the actual user-facing centralization: one consolidated view, one canonical analytical backend, one orchestrator gluing them together.

---

## 5. Divergence policy

See `qiyas/docs/sacred-patterns-integration.md` §Divergence policy. Summary: when qiyas and any local checker disagree, we file the divergence upstream and fix qiyas. Local tools never become permanent parallel implementations. The one exception — a tracked, time-boxed local workaround — applies only when an upstream fix is days out and an iteration session is genuinely blocked.

---

## 6. Migration plan

Three phases. Each is independently shippable; cost-benefit can be reassessed after any phase. Sequenced in `.claude/plans/is-there-an-actionalble-logical-cascade.md`.

- **Phase 0+1** — Adopt qiyas as a third signal AND build the orchestrator + `validation.json` schema in one shipment. Result: iteration loop reads one file instead of four; qiyas runs alongside the existing local tools.
- **Phase 2** — Migrate `qiyas pixel-diff` and `qiyas zone-audit` upstream. Sacred-patterns deletes `tools/svg-diff.sh` and `tools/zone-audit.py` after a pre-swap parity gate. BIKAR coordinates simultaneously.
- **Phase 3** — `qiyas svg-audit` absorbs A1/A2/A4/A5/A6. Sacred-patterns deletes `tools/arch-audit.py`. Largest qiyas-side work is the band-network detector (A5) and the baseline-vocab adapter (A6).

A5 contingency lives at `qiyas/docs/sacred-patterns-integration.md` §A5 contingency.

---

## 7. Costs

Honest accounting, sacred-patterns-side:

- **One more IPC boundary in the iteration loop.** Most analytical tools become `docker run … qiyas` calls. Adds Docker-startup overhead per iteration. Mitigate with a long-running qiyas container or a Python API once qiyas exposes one.
- **Cross-repo coordination cost.** Tweaking a metric means a PR in qiyas instead of editing a Python file locally. Slower for ad-hoc experimentation, faster for permanent improvements (because they accumulate in a tool other consumers use).
- **Schema-bump fan-out.** qiyas bumps its schema regularly (currently 1.12, pre-v1). Mitigate by pinning the qiyas Docker tag and bumping intentionally.
- **Loss of inspectability.** A 50-line bash script reads in 30 seconds; a Python module in another repo doesn't. Mitigate by keeping the orchestrator thin and well-commented at the seam.
- **Upfront migration cost.** Phase 3 is 1–3 weeks of qiyas work, dominated by A5. Phases 0–2 are cheap.

None blocking, all real.

---

## 8. Out of scope for this consolidation

For the record:

- **`validate-svg.sh`** stays in sacred-patterns. 5-line XML preflight with no analytical content; not worth moving.
- **The interpret-pattern browser UX** stays. Interactive shape-correction tool that produces baseline.json is a sacred-patterns product. Its *output* feeds qiyas; the authoring tool stays here.
- **The iteration loop** (learn-new-pattern, Makefile, dashboards) stays. Sacred-patterns's product.
- **Pattern construction library (`src/ts/`)** stays. Has nothing to do with analysis.

---

## 9. Open questions

Sacred-patterns-side only. Qiyas-side open questions live at `qiyas/docs/decisions-pending.md` §Sacred-patterns integration.

1. **Unified similarity score + warnings.** How do all signals (qiyas validate, pixel-diff, zone-audit, svg-audit) compose into a single similarity score plus a prioritized list of actionable warnings? Designed in qiyas (per SP-5 in `qiyas/docs/decisions-pending.md`); sacred-patterns consumes via `validation.json.overall.*`.
2. **What's the right invocation surface for high-iteration loops?** Today: Docker CLI. Better long-term: a long-running qiyas process (HTTP or stdin-driven JSON-RPC) or a native Python library import. Phase 2 should validate which is the expected long-term integration mode. Tracked qiyas-side as SP-2.
