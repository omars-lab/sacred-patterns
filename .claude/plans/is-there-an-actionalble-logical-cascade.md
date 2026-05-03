# Actionable cascade — consolidating analytical tools into qiyas

## Context

Two design docs are settled but unscheduled work:

- `.claude/plans/qiyas-integration.md` — *should* we adopt qiyas as a third signal in the iteration loop. Decision: yes.
- `docs/image-validation-design.md` — *what's the target architecture* once we adopt. Decision: qiyas owns analysis, sacred-patterns owns construction + iteration UX, `validation.json` is the contract, fix-qiyas-on-divergence is policy.

Neither doc specifies *how to actually start*. This plan turns the design into a sequenced, shippable cascade. It begins with the smallest concrete deliverable (a real wrapper + a real orchestrator producing a real `validation.json`) and ends with arch-audit deleted, `qiyas svg-audit` carrying A1–A6 in qiyas, and the qiyas-owned design docs living in qiyas. Each phase is independently mergeable and the loop keeps working at every step.

**Three user-confirmed parameters** that shape the plan:

1. **Integration surface = Docker CLI.** The orchestrator shells out to `docker run ghcr.io/naqshcoffee/qiyas`. No Python-API dependency on qiyas; no local-uv coupling.
2. **A5 (band-network integrity) ends up upstream in qiyas, full path.** No permanent local A5 fallback.
3. **First shipment = Phase 0 + Phase 1 together.** qiyas wrapper and orchestrator land as one coherent change with one iteration-guide update.

**Two policies that bind every phase:**

- **Move, don't copy.** When a piece of functionality migrates to qiyas, the local script is **deleted in the same shipment** that wires up the qiyas replacement. No "keep both alive while we validate" window — that pattern is exactly the parallel-tooling failure mode the divergence policy in `docs/image-validation-design.md` §5 was designed to prevent. Parity validation happens *before* the swap PR opens, not after.
- **Design docs follow the code.** When functionality moves to qiyas, the design docs that describe *that functionality* move to qiyas. Sacred-patterns keeps only the docs that describe our iteration loop, our construction, and our orchestration. Cross-references replace the moved sections.

## Grounding facts from exploration

These are load-bearing for the plan; they came from reading actual call sites and qiyas source.

- **Real call sites in the iteration loop** (from `.claude/skills/learn-new-pattern/iteration-guide.md`):
  - Step 7: `validate-svg.sh iterations/{nn}/output.svg` (line 272)
  - Step 9: `validate-svg.sh input/reference-traced.svg` (line 301)
  - Step 10: `svg-diff.sh` × 2 — vs reference-traced.svg (line 314), vs reference.jpg (line 316)
  - Step 11: `svg-diff.sh` × 2 — tiles-only variants (lines 338–339)
  - Step 12: `arch-audit.py` × 1 or 2 — without baseline (line 357), with baseline (line 360)
- **arch-audit.py emits clean JSON** with stable keys (`A2_symmetry`, `A3_shapes`, `A4_coverage`, `A5_bands`, `A6_baseline`). The orchestrator can parse it directly.
- **zone-audit.py is documented in CLAUDE.md but is NOT actually called from iteration-guide.** Migrating it is purely a forward-looking move — no backward compat to break.
- **Makefile is uninvolved.** The iteration loop is entirely skill-driven; no `make` targets to update.
- **qiyas SVG fast-path handles D3-rendered SVGs for geometry**, but **discards `fill` colors and rejects `clipPath` elements** (raises `SvgParseError`, falls back to raster). Our outputs use clipPath heavily — `qiyas svg-audit` must rasterize or pre-process before encoding.
- **arch-audit A6 matches by `vertex_count` + `zone` only, not by `type`.** Type is advisory. The eventual `qiyas svg-audit` A6 wrapper does NOT need to solve the kite/petal/band-segment vocabulary problem to reach parity.
- **qiyas has no public Python API today** (`pyproject.toml` declares only `qiyas = "qiyas.cli:main"`), which confirms the Docker CLI choice.
- **qiyas has parallel doc structures** to sacred-patterns: `docs/` (architecture, backlog, dev-mental-model, etc.) and `.claude/plans/` (per-feature plans). Doc relocation is natural — destination directories already exist.

## Doc relocations summary

Established up front so each phase can reference it cleanly:

| Doc | From | To | When |
|---|---|---|---|
| `docs/image-validation-design.md` | sacred-patterns | **split:** qiyas keeps §3 architecture + §5 divergence policy; sacred-patterns keeps §4 (`validation.json` schema) + §9 (out-of-scope for us) | Phase 0+1 |
| `.claude/plans/qiyas-integration.md` | sacred-patterns | **split:** qiyas-side concerns (gap analysis §4, shape-vocab table) move to `qiyas/docs/decisions-pending.md` or a new `qiyas/.claude/plans/sacred-patterns-integration.md`; sacred-patterns keeps the iteration-loop wiring decisions | Phase 0+1 |
| Any new pixel-diff / zone-audit / svg-audit design notes | n/a — written net-new | qiyas only (`qiyas/.claude/plans/`) | Phase 2 / Phase 3 |
| `validation.json` schema doc | sacred-patterns (new in Phase 0+1) | sacred-patterns permanently | n/a — it's the orchestrator's contract |
| Iteration-guide tool sections | sacred-patterns | sacred-patterns permanently — but content collapses to "call the orchestrator; see `validation.json`" | Phase 0+1 |

## The cascade

Three phases. Each ends with the iteration loop working end-to-end. After every phase, future-us can stop without leaving the system in a half-migrated state. The "move, don't copy" policy means each phase is *one* PR (sacred-patterns side) plus possibly one matching qiyas-side PR for the same shipment — never a long-running parallel state.

### Phase 0+1 — wrapper + orchestrator + unified rollup + initial doc relocation

**Sacred-patterns deliverables:**
- `tools/qiyas-diff.sh` — thin Docker wrapper around `qiyas validate` and `qiyas encode`. Inputs: reference image + our SVG/PNG. Outputs: `qiyas/ref.encoding.json`, `qiyas/recon.encoding.json`, `qiyas/diff.json`, `qiyas/report.html`.
- `tools/iteration-validate.sh` — orchestrator. Inputs: `--svg`, `--reference`, `--baseline` (optional), `--out`. Calls `validate-svg.sh`, `svg-diff.sh` × 2 (vs reference-traced and vs JPG), `arch-audit.py` (with `--baseline` if provided), `qiyas-diff.sh`. Reads each tool's output and emits a single `validation.json` to `--out/validation.json`.
- `docs/validation-json-schema.md` — pin the schema (top-level `tools.*` keys, `overall.*` derivation rules, version field). This stays in sacred-patterns permanently because it's the orchestrator's contract.
- Iteration-guide updates — Steps 7, 9, 10, 11, 12 collapse into a single Step that calls the orchestrator and reads `validation.json`. Convergence philosophy and G1–G5 gates intact; only the *invocation* changes.
- CLAUDE.md tool-list updates — `iteration-validate.sh` becomes the headline tool; underlying signals listed beneath.

**Doc relocations in this phase:**
- `docs/image-validation-design.md` — extract the architecture (§3) and divergence policy (§5) into a new `qiyas/docs/sacred-patterns-integration.md` (or appended to `qiyas/docs/architecture.md` §"Consumers"). Replace those sections in the sacred-patterns doc with a one-paragraph cross-reference. Keep the `validation.json` schema and out-of-scope section local.
- `.claude/plans/qiyas-integration.md` — qiyas-relevant gap analysis and shape-vocab table move to `qiyas/docs/decisions-pending.md` (qiyas already has this file). Sacred-patterns retains only the iteration-loop wiring sections.

**This phase does NOT:**
- Move any *runtime* logic to qiyas. Local tools still implement everything; qiyas is the new third signal. Doc moves are decoupled from code moves — docs lead, code follows.
- Delete any local script (svg-diff, arch-audit, validate-svg, zone-audit). Those go in Phases 2–3.
- Touch zone-audit. Since iteration-guide doesn't call it today, it stays out of the orchestrator until Phase 2.
- Require qiyas-side *code* work. Doc PRs only on the qiyas side.

**Validation (must pass before merging):**
- Run `tools/iteration-validate.sh` against an existing completed session. Confirm `validation.json` is well-formed, all `tools.*` entries populate, and `overall.topology_complete` matches the session's known state.
- Re-run an iteration on the next learn-new-pattern session and confirm Steps 7+9+10+11+12 collapse cleanly to a single orchestrator call.

**Critical files:**
- (sacred-patterns, new) `tools/qiyas-diff.sh`, `tools/iteration-validate.sh`, `docs/validation-json-schema.md`
- (sacred-patterns, edit) `.claude/skills/learn-new-pattern/iteration-guide.md`, `CLAUDE.md`, `docs/image-validation-design.md`, `.claude/plans/qiyas-integration.md`
- (qiyas, new) `qiyas/docs/sacred-patterns-integration.md` (or section in existing doc), `qiyas/docs/decisions-pending.md` updates

### Phase 2 — migrate pixel-diff and zone-audit to qiyas (one shipment, no parallel state)

**Order of operations** (this is the move-not-copy discipline):
1. **Land qiyas-side first.** `qiyas pixel-diff` and `qiyas zone-audit` ship in qiyas, including their design docs at `qiyas/.claude/plans/pixel-diff.md` and `qiyas/.claude/plans/zone-audit.md`.
2. **Run parity validation locally** before opening the sacred-patterns PR. Three completed sessions; diff `qiyas pixel-diff` output against `tools/svg-diff.sh` output. Any divergence beyond rounding noise gets filed and fixed in qiyas before the swap.
3. **Open one sacred-patterns PR** that simultaneously: (a) swaps `iteration-validate.sh` to call qiyas, (b) **deletes** `tools/svg-diff.sh` and `tools/zone-audit.py`, (c) updates CLAUDE.md and iteration-guide. No "kept around for parity" period.

**Qiyas-side deliverables:**
- `qiyas pixel-diff IMG_A IMG_B [--out DIR]` — port `tools/svg-diff.sh` semantics (rasterize, auto-trim, ImageMagick compare, similarity score + heatmap + overlay PNGs). Schema-versioned output.
- `qiyas zone-audit DIFF_A DIFF_B [--out DIR]` — port `tools/zone-audit.py` semantics (concentric ring match, broad zone summaries, strapwork gap analysis).
- Design docs at `qiyas/.claude/plans/pixel-diff.md` and `qiyas/.claude/plans/zone-audit.md` (qiyas already uses this convention per its `.claude/plans/` directory).

**Sacred-patterns deliverables (single PR, single shipment):**
- `tools/iteration-validate.sh` calls `qiyas pixel-diff` and `qiyas zone-audit` instead of local scripts.
- **Deletes** `tools/svg-diff.sh` and `tools/zone-audit.py`.
- Updates CLAUDE.md tool-list (remove svg-diff and zone-audit entries; iteration-validate now calls qiyas for these).
- Updates `docs/validation-json-schema.md` if any keys change.

**Divergence handling (already-validated by Phase 2 step 2):** the sacred-patterns swap PR doesn't open until parity is confirmed locally. Any in-flight divergence is a qiyas bug, fixed in qiyas, never an excuse to keep local copies.

**Critical files:**
- (qiyas, new) `src/qiyas/cli.py` additions, `src/qiyas/pixel/`, `src/qiyas/zone/` modules, `qiyas/.claude/plans/pixel-diff.md`, `qiyas/.claude/plans/zone-audit.md`
- (sacred-patterns, edit) `tools/iteration-validate.sh`, `CLAUDE.md`, iteration-guide
- (sacred-patterns, **delete**) `tools/svg-diff.sh`, `tools/zone-audit.py`

### Phase 3 — `qiyas svg-audit` absorbs A1/A2/A4/A5/A6, arch-audit deletes (one shipment)

**Order of operations** (move-not-copy):
1. **Land qiyas-side first.** `qiyas svg-audit` ships in qiyas with A1/A2/A4/A5/A6, including the band-network detector and the baseline-vocab adapter. Design docs at `qiyas/.claude/plans/svg-audit.md` and `qiyas/.claude/plans/band-network-detector.md`.
2. **Parity validation locally** — three sessions, diff `qiyas svg-audit` JSON against `arch-audit.py` JSON within explicit per-key tolerances. Counts: exact. Coverage: ±0.5%. Symmetry status: equal. A6 PASS/PARTIAL/MISSING/EXCESS verdicts: equal per shape.
3. **Single sacred-patterns PR:** swap `iteration-validate.sh` to call `qiyas svg-audit`, **delete** `tools/arch-audit.py`, update docs.

**Qiyas-side deliverables:**
- `qiyas svg-audit OUR.svg [--baseline BASELINE.json] [--reference REF] [--out DIR]` emitting an A1–A6 rollup that matches arch-audit's existing JSON keys (so the orchestrator translation is one-line).
  - **A1 (semantic census):** surface from `qiyas encode` shapes_by_type. Replaces arch-audit's `A3_shapes`.
  - **A2 (sector symmetry):** surface from Stage 4 dominant_fold + per-sector check.
  - **A4 (coverage):** face-walking from Stage 2.5 → union vs clip-circle area.
  - **A5 (band-network integrity):** new detector. Walks band-segment primitives as connected components, verifies count and crossing topology. Largest piece of new work in the cascade.
  - **A6 (baseline match):** baseline.json → synthetic encoding (vertex_count + zone-derived position; type vocab advisory). Run `qiyas diff` against the actual encoding, translate into PASS/PARTIAL/MISSING/EXCESS.
- Pre-processing for our SVGs: flatten `clipPath` to a bounding mask or rasterize-and-encode when clipPath is present (since SVG fast-path raises today).
- Design docs in qiyas: `qiyas/.claude/plans/svg-audit.md`, `qiyas/.claude/plans/band-network-detector.md`, `qiyas/.claude/plans/baseline-adapter.md`.

**Sacred-patterns deliverables (single PR):**
- `tools/iteration-validate.sh` calls `qiyas svg-audit` instead of `arch-audit.py`.
- **Deletes** `tools/arch-audit.py`.
- Updates CLAUDE.md, iteration-guide, and `docs/validation-json-schema.md` if keys change.
- baseline.json schema unchanged — qiyas's adapter consumes the existing format.

**Doc moves in this phase:** any sacred-patterns-side doc that describes A1–A6 audit semantics (currently mostly comments and CLAUDE.md prose) gets cross-referenced to `qiyas/.claude/plans/svg-audit.md`. The convergence philosophy stays in CLAUDE.md (it's *our* methodology, not qiyas's).

**A5 contingency:** No permanent local fallback. If A5 stalls long enough that an iteration session needs it, the `docs/image-validation-design.md` §5 exception applies — temporary local workaround with a deletion ticket against the qiyas A5 milestone. But that workaround does not enter Phase 3's normal scope; Phase 3 ships only when A5 ships.

**Critical files:**
- (qiyas, new) `src/qiyas/cli.py` additions, `src/qiyas/svg_audit/` module incl. `band_network.py` and `baseline_adapter.py`, three plan docs
- (sacred-patterns, edit) `tools/iteration-validate.sh`, `CLAUDE.md`, iteration-guide
- (sacred-patterns, **delete**) `tools/arch-audit.py`

## End state

```
Iteration loop calls:
   ./tools/iteration-validate.sh --svg X --reference Y --baseline B --out OUT

iteration-validate.sh shells out to (Docker CLI):
   qiyas validate ...           → reference-grounded shape pairing
   qiyas pixel-diff ...         → similarity %, heatmap                (Phase 2)
   qiyas zone-audit ...         → per-ring scores                      (Phase 2)
   qiyas svg-audit ...          → A1/A2/A4/A5/A6                       (Phase 3)
   ./tools/validate-svg.sh ...  → 5-line XML preflight (stays local)

Writes single validation.json. Iteration loop reads overall.* for go/no-go,
humans drill into tools.* for diagnosis.

Doc state:
  sacred-patterns/docs/validation-json-schema.md      → orchestrator contract (local)
  sacred-patterns/CLAUDE.md                           → iteration philosophy (local)
  sacred-patterns/docs/image-validation-design.md     → trimmed: cross-refs qiyas docs
  qiyas/docs/sacred-patterns-integration.md           → architecture + divergence policy
  qiyas/.claude/plans/{pixel-diff,zone-audit,svg-audit,band-network-detector,baseline-adapter}.md
  arch-audit.py, svg-diff.sh, zone-audit.py           → DELETED
```

Sacred-patterns owns: iteration loop, interpret-pattern UX (baseline.json authoring), orchestrator, validate-svg preflight, pattern construction code (`src/ts/`), the `validation.json` schema, our iteration philosophy.

qiyas owns: every analytical signal (regardless of input format), the design docs that describe those signals.

## Verification — end-to-end

After each phase, run this loop to confirm the cascade is healthy:

1. **Pick a completed session** (e.g. the most recent one in `/Users/omareid/Dropbox/Data/sacred-patterns/`).
2. **Run `./tools/iteration-validate.sh`** with that session's final SVG, reference image, and baseline.json. Confirm exit 0 and well-formed `validation.json`.
3. **Cross-check** at least one `tools.*` field per signal — for Phases 2 and 3 this is the parity check that gates the swap PR; for Phase 0+1 it's a sanity check against the wrapped tools' standalone output.
4. **Re-run** the orchestrator with `--baseline` removed — confirm A6 falls through cleanly and `overall.*` updates accordingly.
5. **Drive an actual iteration** on the next learn-new-pattern session using only the orchestrator.

Phase 2 and Phase 3 add the explicit **pre-swap parity gate**: three completed sessions, divergence beyond defined tolerance blocks the swap PR until qiyas-side fix lands. No exceptions.

## Open items (do not block Phase 0+1)

- **qiyas-side conversation before Phase 2 starts:** confirm qiyas owners accept the upstream consolidation scope (pixel-diff + zone-audit + svg-audit, including A5).
- **BIKAR coordination before Phase 2:** BIKAR has its own `scripts/svg-diff.sh` per `qiyas/docs/dev-mental-model.md` §13. Phase 2 should coordinate so BIKAR migrates simultaneously and we delete two copies, not one.
- **Long-running qiyas process for high-iteration loops:** Docker startup overhead (~1–3s per call, multiple calls per iteration) compounds at scale. Revisit after Phase 0+1 lands and we have real wall-clock data.
