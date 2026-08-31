---
name: no-backwards-compatibility
description: Backwards compatibility is not a gate — ship breaking changes when they make the code more robust; owner waived 2026-05-24
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

Backwards compatibility is **not a load-bearing concern** across qiyas, bikar, and sacred-patterns. When a refactor, schema bump, or API change makes the code more robust, ship it — even if it breaks downstream consumers. Coordinate the cutover (regen baselines, update consumer code) as part of the same PR or follow-on; do not author dual-emit shims, versioned schemas, strangler-fig layers, or compat helpers to soften the break.

**Why:** owner explicitly stated 2026-05-24 "we dont need backward compatibility" alongside granting Tenet 24 ("dont fear breaking things if it makes our code more rohbust"). The three repos are tightly coupled (qiyas detector ↔ bikar SVG ↔ sacred-patterns iteration loop), each consumer count is small (single-digit), and the owner pays the coordination cost themselves — strangler-fig overhead is justified only when consumers are many and migrations are years long. Here it's pure tax. The recurring pattern of "ship breaking → break consumer → fix consumer in same session" is cheaper than maintaining compat layers that calcify.

**How to apply:**
- Schema bumps: ship the bump, regen baselines, update consumer code, push. Don't author SCHEMA_VERSION dual-emit periods or deprecation warnings.
- API renames/refactors: rename in place, update all callers, push. Don't keep old names as aliases.
- JSON/serialization changes: cutover, regen fixtures, push. Don't version the JSON envelope.
- Pydantic discriminated-union migrations (#362 / #525): cutover directly; the old `Shape` class gets deleted, consumers update.
- **Still requires explicit owner OK:** breaking changes to **published external packages** (e.g., `@NaqshCoffee/bikar-core` on GitHub Packages used by `coffee-house-design-kit` or other external sites). External consumers haven't agreed to the no-backcompat contract; internal three-repo cascade has.

**Companion to:** Tenet 24 (don't fear breaking things — same incident, same day), [[feedback_decision_pick_authorization.md]] (the meta-authorization that operationalizes this for the queue of pending picks), [[feedback_push_authorization_general.md]] (push autonomy on tested-green).
