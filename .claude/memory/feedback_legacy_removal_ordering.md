---
name: legacy-removal-ordering
description: "When migrating off a legacy compat shim, delete the producers BEFORE the consumers — never the reverse, because consumers still receive legacy inputs from un-migrated callers (including tests)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

When deleting a legacy compat function (`from_legacy`, coercion helper, adapter shim), do NOT start by removing it from internal consumers. Order the slices producer-side first:

1. Migrate every caller that *produces* legacy objects (tests, fixtures, external entry points, deserializers) to construct typed objects directly.
2. Only after step 1 leaves zero producers, remove the compat call from internal consumers (it is now a provable no-op).
3. Then delete the compat function itself.

**Why:** The summary claim "`from_legacy(s)` is idempotent on ShapeBase so removing it from detector elevators is safe" sounds true in isolation — and IS true when the input is already typed. The trap: tests and external entry points may still construct legacy `Shape` directly. With `from_legacy` removed from the consumer, those legacy inputs flow through unconverted; `isinstance(typed, RegularPolygonShape)` returns False; the elevator silently rejects them. Surfaced in qiyas #532 D4c slice-1 on 2026-05-24: `test_detectors_decagon.py::test_elevate_decagon_promotes_clean_decagon` flipped from green to red because `_make_polygon_shape()` returns `Shape(type="regular_polygon", ...)` not `RegularPolygonShape(...)`. Falsified across 12 detector files in one shot.

**How to apply:** Before any "remove the compat shim call from consumer X" slice, grep for who CONSTRUCTS the legacy type — tests, fixtures, parse boundaries, public API surfaces. If any construction site remains, that's the slice to ship FIRST. The shim's call site is the LAST thing to delete, not the first. Use the failing test as the safety net: it should stay green at every slice boundary, and only the slice that removes the shim's *definition* should require zero callers anywhere.

**Companion to:** [[feedback_consumer_audit_construction_contracts]] (consumer audits must check producers too, not just direct callers), and [[feedback_check_mechanism_already_implemented]] (read the target module before estimating rework — would have shown the Shape class is still defined and used by tests).
