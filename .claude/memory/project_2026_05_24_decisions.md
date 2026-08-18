---
name: 2026-05-24-decisions
description: Owner picks delivered 2026-05-24 on the 7-task gridlock + medallion-10 ceiling + cutover scope
metadata: 
  node_type: memory
  type: project
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

Owner answered the exec summary of `sacred-patterns/docs/decisions/2026-05-23-unblock-critical-path-workstream.md` on 2026-05-24 with the following picks. Decision doc to be updated to status: ACCEPTED 2026-05-24.

**Picks:**
1. **Option B granted** — standing authorization for documented-default + reversible-mechanism shipments. Captured as [[feedback_decision_pick_authorization.md]].
2. **#80/#85/#123/#127/#129 — DO NOT close as ceiling.** Owner explicitly: "no, we must strive to get better." Medallion-10 must converge beyond iter-14. The cascade stays open; alternate attack vectors (partial-shape #106 residue-extractor refactor, Tier 1 corpus expansion, detector calibration loop) are the productive next moves; iter-17 REVERT-to-iter-14 guidance still in force for *naive* iter-18.
3. **#525 — SHIP cutover.** Pydantic discriminated-union migration final slice; bump SCHEMA 1.17→1.18; delete legacy `Shape`; regen sacred-patterns iteration-loop baselines as part of the PR.
4. **#138 — ship Option G** (fix baseline schema notes-as-discriminator, 2-3 days). Unblocks #516.
5. **#391 — ship Option A** (import-linter contract-based layering gate for qiyas + bikar).
6. **#434 — ship Option B** (merge policy as typed parameter on `buildIntersectionGraph`).

**Also granted:** Tenet 24 (sacred-patterns/bikar/qiyas CLAUDE.md) — "don't fear breaking things if it makes our code more robust." And the no-backcompat waiver captured as [[feedback_no_backwards_compatibility.md]].

**Why:** owner direction 2026-05-24, in response to exec summary one-liners. Per-pick rationale tied to whether the pick was reversible (B/C/D/E) or product-policy (#2 — keep striving).

**How to apply:**
- Drain queue order (smallest to largest): #434 → #391 → #138 → #525.
- For each: read decision doc, ship per-recommended option, commit with rationale, push (per [[feedback_push_authorization_general.md]]), close task.
- For #2 (medallion-10): pivot to alternate attack vectors instead of close-as-accepted. #106 residue-extractor refactor is the named next move; Tier 1 corpus expansion is the foundation work; iter-18 still gated on Tax-B-aware planning (do NOT generate iter-18 naively).
- Update decision doc `2026-05-23-unblock-critical-path-workstream.md` frontmatter: status: ACCEPTED 2026-05-24, decided: 2026-05-24, owner: omareid, picked: Option B (with #2 carve-out per owner direction).
- Update mental-model doc per Post-ACCEPT step of present-options skill.
