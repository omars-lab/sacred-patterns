---
name: bikar-github-packages-token-in-env
description: "bikar npm ci/install needs GITHUB_PACKAGES_TOKEN sourced from git-ignored bikar/.env (private @naqshcoffee/* deps); make test needs Docker, npx vitest run is the daemon-free fallback"
metadata: 
  node_type: memory
  type: reference
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

bikar's `npm ci` / `npm install` authenticate to GitHub Packages (`https://npm.pkg.github.com/`) for the private `@naqshcoffee/*` deps (e.g. `@naqshcoffee/ui`) via `${GITHUB_PACKAGES_TOKEN}` in the repo `.npmrc`. The token lives in **`bikar/.env`** (git-ignored, alongside Supabase/Cloudflare vars; `.env.example` lists the names). Source it before installing:

```bash
cd /Users/omareid/Workspace/git/bikar
set -a; . ./.env; set +a   # exports GITHUB_PACKAGES_TOKEN
npm ci
```

**Gotcha:** unset token → `npm error code E401 ... unauthenticated`, AND `npm ci` deletes `node_modules` before fetching, so a token-less run leaves a broken tree. Always source `.env` first.

**Build (CI mirror):** `npm run build -w packages/core` (tsup) + `npm run build -w packages/web` (Vite 8).

**Test:** `make test` routes through Docker (`docker compose run --rm bikar-studio npx vitest run`) and needs the Docker daemon. When Docker is down, `npx vitest run` runs the same suite daemon-free (900/900 as of 2026-06-01).

**How to apply:** when working bikar locally and an install fails E401, or `make test` fails on `docker.sock`, this is the fix — not a dependency or vite8 problem. Documented in bikar/CLAUDE.md "Local Development" section (commit c73b327). Token PAT must be **classic** (fine-grained tokens don't support GitHub Packages).
