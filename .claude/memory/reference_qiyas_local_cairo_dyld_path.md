---
name: qiyas-local-cairo-dyld-path
description: qiyas local pytest needs DYLD_FALLBACK_LIBRARY_PATH to Homebrew cairo or 6 cairosvg-dependent test files fail to collect; fixed via conda activation hook
metadata: 
  node_type: memory
  type: reference
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

The qiyas full pytest suite (2369 tests) includes 6 files that import `cairosvg` (canonical-validation, cli-trace, tolerance-sensitivity, + 3 more). `cairosvg` is a pure-Python wrapper that `dlopen`s the native `libcairo.2.dylib` at runtime. The conda `workspace` env does NOT search Homebrew's lib path by default, so on the Apple-Silicon dev box those 6 files fail collection with `OSError: no library called "cairo-2"` — leaving only 1235 of 2369 tests collectable locally.

**This is a local-env gap, not a broken foundation:** CI runs in Docker where `Dockerfile:44` installs `libcairo2`, so the full suite collects and passes in CI. But under the GHA-budget freeze, local mirroring is the ONLY verification path (`feedback_never_block_on_gha`), so the local hole mattered.

**Fix (applied 2026-05-28, owner-approved):** brew cairo 1.18.4 was already installed at `/opt/homebrew/opt/cairo/lib/libcairo.2.dylib` (arm64). Wrote a conda activation hook at `/usr/local/bin/miniconda3/envs/workspace/etc/conda/activate.d/cairo_dyld.sh` that exports `DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/opt/cairo/lib:$DYLD_FALLBACK_LIBRARY_PATH"`. After this, full collection succeeds (2369 tests, 0 errors) and the 6 files pass (693 passed + 2 xfailed in ~6.7min).

**How to apply:** if a fresh shell/session can't collect those 6 files, either activate the conda env (the hook fires) or prefix the pytest command with `DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/opt/cairo/lib"`. If brew cairo is missing entirely, `brew install cairo` (system-level — owner-confirm first per the autonomy contract). The hook lives only in the local conda prefix, not in any repo, so it does not travel with a git clone — a new machine needs it re-created.

**Companion to:** [[feedback_never_block_on_gha]] (local mirroring is load-bearing under the freeze), [[feedback_mirror_ci_locally]] (mirror CI exactly — the cairo files are part of CI's suite, so local parity requires them runnable).
