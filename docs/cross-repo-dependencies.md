# Cross-repo task dependencies

Tracks task-level dependencies between **sacred-patterns**, **qiyas**, and **bikar** so a blocker in one repo surfaces in the others. Mirror of `qiyas/docs/cross-repo-dependencies.md` (synced manually — keep both sides in step when adding/pruning a row).

## The convention (Option A — link in description)

When a task in this repo blocks or is blocked by work in another repo, mention it in the task description using this format:

```
<repo>#<task-id>
```

Examples:

- `blocked by qiyas#67`
- `unblocks bikar#42`
- `coordinated shipment with qiyas#27`

The format is grep-able. To find all sacred-patterns tasks waiting on cross-repo work:

```bash
# from this repo's working directory
grep -rn "qiyas#\|bikar#" .claude/  # plans only
# or against TaskList output
TaskList | grep -E "qiyas#|bikar#"
```

**Why Option A and not a shared table or hooks:** zero infrastructure cost; the convention works the moment you adopt it. If grep-driven discipline drifts (see the §"Active dependencies" table below stays empty for >1 month while cross-repo work clearly continues), revisit Option B (this doc becomes the manually-synced source of truth) or Option C (TaskCreate hook auto-syncs across repos).

## When to add an entry to the table below

The table is for *active* cross-repo dependencies — things blocking each other *right now*. Once both sides ship, prune the row (the changelog entries on each side are the durable history).

A task earns a row when:
- One side is blocked on the other (hard dependency)
- Both sides need to ship in the same window (coordinated shipment)
- One side's design decision constrains the other's implementation

Pure "future maybe" links (e.g. "if we add X here, Y might want it there") don't earn a row — they belong in the originating task's description as a forward reference.

## Active dependencies

| sacred-patterns | qiyas | bikar | direction | status | notes |
|-----------------|-------|-------|-----------|--------|-------|
| (calibration corpus) | qiyas#79 | — | sacred-patterns awaits | pending | `qiyas score backfill` — needed before `qiyas score replay` is usable against the calibration corpus (sessions today have no `validation/` subdirs). |
| bikar-medallion-10 (driver) | qiyas#59 + #60 | — | qiyas-side | active | A5 band-segment classifier + crossing topology — promoted 2026-05-02 from deferred. bikar-medallion-10 (10-fold medallion with full white interlaced strapwork) chosen as parity driver. Reference captured at qiyas fixture `bikar-medallion-10-strapwork`. Orchestrator's `A5_band_integrity` consumer is already in place. |
| iteration-guide + iteration-validate.sh consume iter.json | qiyas#74 (Slices 1-4 SHIPPED; Slice 5 in flight as sp#589) | — | sacred-patterns-side | active | V2.A iteration-aware analysis — `qiyas iter analyze` CLI lands a `verdict.kind` + `top_edit_candidate` + `iterations-to-converge` prediction over a trailing window. Slice 5 wires it into `tools/iteration-validate.sh` (auto-invoke after `validation.json` lands) and the iteration-guide D0 + Stagnation Detection sections (consume `iter.json` first; fall back to per-iteration drilldown only on PENDING). Closes the agent's manual JSON-diffing rule at iteration-guide.md:60-62. |
| iteration-guide consumes recommended_actions | qiyas#75 (Slices 1-6 SHIPPED 2026-05-26) | — | sacred-patterns-side | active | V2.B global warning optimizer — `qiyas score` writes `recommended_actions[]` (net-delta-ranked, accounts for cross-warning interaction matrix) and `qiyas iter analyze` surfaces `top_edit_candidate.recommended_action_rank` + `recommended_action_net_delta` + `recommended_action_predicted_collateral` when score.json is present. iteration-guide D0 now prefers these fields over the bare `warnings[0]` directive — see `.claude/skills/learn-new-pattern/iteration-guide.md` §D0. Backward-compat: when score.json is absent, falls back to the V2.A trajectory-only signal. |
| iteration-validate.sh `--auto-capture-on-go` | qiyas#77 | — | coordinated | pending | V2.E populates qiyas fixture corpus on every converged session without human intervention. Mechanical step: `qiyas fixtures capture` (already shipped in qiyas#65). See qiyas/docs/roadmap.md §V2.E. |
| escalate-qiyas-divergence skill | (qiyas/docs/issues destination) | — | sacred-patterns-side | pending | V2.F closes divergence-policy enforcement gap. Skill mechanical step uses qiyas#65 fixture-capture; lands issues at qiyas/docs/issues/. See qiyas/docs/roadmap.md §V2.F. |

## Partial-shapes via construction (#106 cascade)

The "construction-extended-then-clipped shape" pattern — needed to break medallion-10's ~74% ceiling where the central decagram chords physically must reach past the medallion boundary, then get clipped to it — landed across all three repos. The qiyas detector + bikar DSL primitives are now wired end-to-end:

| Repo | Capability | Where to look |
|------|-----------|---------------|
| qiyas | OpenPolyline shape + `partial_polygon` detector + `A6 CLIPPED-MISSING` verdict + `extend_and_clip` counterfactual | qiyas#256 (slices 1-7); reads `params.partial` + `params.clipped_at_boundary` from gt.json |
| bikar | `boundary X = union(...)` + `extend connect ... beyond F` + `extend edges from <poly> beyond F` + `clip pattern to X` + `params.extension_factor` + `params.clipped_at_boundary` + `params.partial` emission | bikar#258 PR1 (boundary), PR2 (extend), PR3 (clip) — schema 1.16 → 1.17 → 1.19 |
| sacred-patterns | Iteration-guide warning-translation row for `A6 ... CLIPPED-MISSING` → DSL idiom (`extend + clip pattern to medallion_outline`) | this doc + `.claude/skills/learn-new-pattern/iteration-guide.md` §E2 mechanical edit table |

**Validation gate** (#260): re-run iter-14 medallion-10 against the full cascade; confirm at least one `A6 ... CLIPPED-MISSING` warning materializes in `overall.warnings`, surfaces a non-zero `counterfactual_score_delta`, and the DSL idiom applies cleanly. Until that runs, treat the cascade as **shipped but unverified end-to-end**.

## Recently resolved (last 30 days, prune after)

| sacred-patterns | qiyas | bikar | direction | shipped | notes |
|-----------------|-------|-------|-----------|---------|-------|
| (interpret-pattern automation path) | qiyas#81 | — | qiyas-side | 2026-05-02 | `qiyas baseline emit IMAGE` ships the mechanical inverse of #32 — auto-generates baseline.json directly from an encoder pass. Collapses `learn-new-pattern` Step 1.5 human gate to one CLI call; round-trip A6 audit on bikar-medallion-10 = 18/18 PASS. |
| `tools/iteration-validate.sh:231` update | qiyas#27 | — | coordinated | 2026-05-01 | `qiyas score` became a click Group; orchestrator updated to `qiyas score run` in the same shipment. |
| (auto-consumes via overall.warnings) | qiyas#70 | — | qiyas-side | 2026-05-02 | svg-audit warnings flow through `qiyas score` into `overall.warnings[0]`. No sacred-patterns code change required. |
| (iteration-loop triage) | qiyas#67 | — | qiyas-side | 2026-05-02 | `qiyas trace --show-unknown` (text/JSON) + `--show-unknown-html` (visual overlay) shipped same day. Investigators can now triage why specific contours classified as `unknown` and what tolerance bump would admit them. |

## Reference: cross-repo contracts

- **bikar ↔ qiyas deconstruction separation** — `docs/bikar-qiyas-separation.md` (canonical here; mirror stubs in `bikar/docs/` and `qiyas/docs/`). Names which tool to reach for (bikar = by-eye author / producer-of-record; qiyas = machine-CV reviewer / portal), the shared-artifact seam (`pattern.gt.json` → `encoding.json` → `annotations.json`), and the roadmap to extract the shared envelope contract (`@naqshcoffee/qiyas-schema`, Phases 1–4). Companion to `dsl-metadata-contract.md` (per-`data-*` channel) at the envelope level.

## Reference: the three repos

- **sacred-patterns** (`/Users/omareid/Workspace/git/sacred-patterns/`) — pattern-construction (TypeScript/D3), iteration loop, interpret-pattern UX, validation orchestrator. Calls qiyas via Docker.
- **qiyas** (`/Users/omareid/Workspace/git/qiyas/`) — analytical signals (encoder, detectors, svg-audit, score, pixel-diff, zone-audit). Authoritative for *what's in the image* and *how good the reconstruction is*.
- **bikar** (`/Users/omareid/Workspace/git/bikar/`) — pattern-construction package; consumes qiyas analytical signals.
