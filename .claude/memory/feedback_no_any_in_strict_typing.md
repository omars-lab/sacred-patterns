---
name: No `Any` AND no `object`/`dict[str, object]` as strict-mode silencers
description: When fixing strict mypy/TS errors, never use Any *or* object-as-bag to silence the gate; both are anti-patterns. Model variant data with discriminated unions / TypedDict / Pydantic / Protocol — derive the real type or refactor the code that resists typing
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
When closing strict-mode type-check errors (mypy strict, tsc --strict), NEVER reach for `Any` / `dict[str, Any]` / `unknown` cast — AND never reach for `dict[str, object]` / `object` as a fig-leaf substitute. The point of the gate is to surface the *real* type, including for variant payloads.

**Why:** the user reviewed a triangle.py edit (2026-05-16) where I closed a `dict` `[type-arg]` error by annotating `dict[str, Any]`. That defeats the purpose — the gate is asking "what's actually in this dict?" and `Any` says "I don't know." Later that day (2026-05-16) the user reviewed my follow-up across `schema.py` + the detector cascade where I had swapped `dict[str, Any]` → `dict[str, object]` and added `_param_int`/`_param_float` helper functions. The user's feedback: **"object should be similar to any ... if we need to make classes for data /better types, we should"** and **"we should be properly applying types and polymorphism"**. From the consumer's perspective `dict[str, object]` is bag-typed too — it forces narrowing at every read site instead of declaring the variant. The decision doc at `qiyas/docs/decisions/2026-05-16-typed-shape-params-vs-object-bag.md` recommends a discriminated-union / per-subclass model (Pydantic discriminated union on the `Literal` `type` field) over the `dict[str, object]` + helper approach.

**How to apply:**
- For variant dicts keyed by an existing `Literal` discriminator (e.g., `Shape.params` keyed off `ShapeType`): use a discriminated union — Pydantic `Annotated[Union[...], Field(discriminator='type')]` for runtime+static, or `Union` of `TypedDict`s for mypy-only. Each variant gets its own typed shape; consumers narrow by checking the discriminator.
- For variant payloads that aren't yet polymorphic: prefer polymorphism (per-variant subclass with its own typed fields) over a single class with a bag-typed `params` field, especially when the data already carries an `is-a` relationship to a base type.
- For untyped third-party returns: write a `Protocol` describing the slice you use, or a thin wrapper that returns a typed view.
- For `no-any-return` errors from arithmetic on untyped params: fix the param's type, don't `# type: ignore` the return.
- For genuinely runtime-shaped surfaces (parsed JSON before validation, plugin interfaces): `dict[str, object]` is acceptable AT THE BOUNDARY with immediate narrowing into a typed model; never propagate it through the codebase.
- If a function resists clean typing, that's a *signal the function does too much* — split it before adding a type.

**Anti-pattern catalog (all forbidden):**
- `Any` / `dict[str, Any]` / `list[Any]` — what we started with.
- `object` / `dict[str, object]` as the *destination* type of a refactor when the data has a known variant shape — same bag-typed semantics as `Any` from the consumer's view, just with more verbose narrowing code.
- `# type: ignore[no-any-return]` / `# type: ignore[arg-type]` / `cast(X, untyped_value)` to silence a single error without fixing the upstream type.
- Helper functions like `_param_int(params, key, default)` that *exist only to launder* `dict[str, object]` into a typed value — these are calcification of the anti-pattern, not a solution to it.

**Cross-repo scope:** lift to a tenet across qiyas (Python), bikar/sacred-patterns (TS) — same rule. `unknown` is acceptable at parse boundaries with immediate narrowing; `any` is never acceptable. TS equivalent of "object as Any-substitute": `Record<string, unknown>` for variant payloads when a discriminated union already exists.

**Stop rule:** if your only way to make mypy/tsc green for a function is `Any`/`any`/`# type: ignore` OR `dict[str, object]`/`Record<string, unknown>` *for data that has a known discriminator*, stop. Either model the variant (TypedDict per case + Literal discriminator, OR Pydantic submodel per case + discriminated union, OR class hierarchy), or the code needs a refactor. Don't ship the silencer; don't ship the fig-leaf.
