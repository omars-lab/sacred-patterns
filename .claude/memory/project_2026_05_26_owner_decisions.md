---
name: 2026-05-26-owner-decisions
description: Owner decisions on 2026-05-26 unblock list —
metadata: 
  node_type: memory
  type: project
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

Owner picks on 2026-05-26 unblock list (presented in layman terms at owner ask "present options i need to decide on to unblock"):

- **#603 GHA billing** — **WAIT**. Do not prompt for billing action; do not push held commits until owner moves. Loop stays idle on push-gated work until budget restored.
- **#597 bikar mirror-polygon body emission** — **Option B (derived-id naming)**, NOT Option A. Owner wants a proper naming-conventions plan first because `mirror` is one of a family (`rotate N`, future transforms) that produce derived shapes; an ad-hoc suffix for `mirror` alone would calcify into inconsistency. Plan must cover at least mirror + rotate, ideally generalize to "transform composition" (e.g. rotate-then-mirror).
- **#525 / #138** — **PRESENT** layman summaries (in-flight: owner asked for these next).
- **#525 cutover** — **SHIP NOW** (Option A: single cutover, delete legacy Shape, regen baselines, SCHEMA_VERSION 1.17→1.18). Owner confirmed 2026-05-27. Must file "audit downstream consumers across qiyas/bikar/sacred-patterns" as part of PR.
- **#138 iter-18** — **RENDER + VISUAL CONFIRM**. Owner confirmed 2026-05-27. Render iter-18, save image, surface to owner via SendUserFile for visual review (NOT just compare numerics).

**Why:** Owner is exercising long-term-shape judgment — Option A's "asymmetric naming" was the load-bearing con, and Option B becomes the right pick once a consistent convention exists across all derived-shape producers.

**How to apply:**
- Do NOT author Option B implementation until the naming-conventions plan is written and accepted.
- The plan lives at `bikar/docs/design/derived-shape-naming.md` (new) — present-options skill applies since this is a cross-cutting design decision.
- Plan scope: mirror, rotate N, and a forward-looking rule for future transforms (e.g. `triangle__mirror`, `triangle__rot1` … `triangle__rotN-1`, composed: `triangle__rot1__mirror`).
- #603 stays WAIT — do not surface again unless owner asks; loop heartbeat continues.
