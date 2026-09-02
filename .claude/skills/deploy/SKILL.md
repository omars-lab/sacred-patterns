---
name: deploy
description: Pre-flight checks, build, gallery generation, and deploy to GitHub Pages (gh-pages branch). Verifies the live site responds after push.
user_invocable: true
argument: none
---

# deploy

Build the site, generate the gallery, push to the `gh-pages` branch, and verify the live site.

## Invocation

```
/deploy
```

Also triggered by: "update the site", "deploy to gh-pages", "push to pages", "update docs".

## How the Site Works

- **Live URL:** https://art.bytesofpurpose.com/
- **Hosting:** GitHub Pages served from the `gh-pages` branch
- **Content:**
  - `index.html` + `bundle.js` — the pattern viewer (built by webpack from `src/ts/`)
  - `gallery/` — learning session dashboards, timelapse assets, and gallery index
- **Build pipeline:** TypeScript → webpack → `site/` directory → copy to gh-pages worktree → push

## Workflow

### Step 1: Pre-Flight Checks

Run these checks before building. If any fail, stop and report.

1. **Clean working tree for source files:**
   ```bash
   # Check for uncommitted changes in src/ and templates/
   git diff --quiet -- src/ templates/ webpack.config.js package.json
   ```
   If there are uncommitted source changes, warn the user — the deploy will use the current working tree state, which may include unintended changes. Ask whether to proceed or commit first.

2. **TypeScript compiles cleanly:**
   ```bash
   make compile
   ```
   Must exit 0. If ESLint or tsc fails, stop and report errors.

3. **gh-pages branch exists:**
   ```bash
   git rev-parse --verify gh-pages 2>/dev/null
   ```
   If it doesn't exist, the Makefile `deploy` target will fail. Advise the user to create the branch:
   ```bash
   git checkout --orphan gh-pages && git rm -rf . && git commit --allow-empty -m "Init gh-pages" && git push origin gh-pages && git checkout master
   ```

4. **No stale git worktrees:**
   ```bash
   git worktree list
   ```
   If there's already a worktree for gh-pages (from a failed prior deploy), clean it up:
   ```bash
   git worktree remove <path> --force
   ```

5. **Remote is reachable:**
   ```bash
   git ls-remote --exit-code origin gh-pages
   ```
   If this fails, the push step will fail. Check network/auth.

6. **Sessions directory exists** (for gallery):
   ```bash
   ls /Users/omareid/Dropbox/Data/sacred-patterns/session-* 2>/dev/null
   ```
   Not fatal if empty — gallery will just have no sessions.

### Step 2: Build

```bash
make build
```

This runs `npm run build` which:
- Compiles TypeScript via ts-loader
- Bundles with webpack to `site/bundle.js`
- Generates `site/index.html` from `templates/index.tpl`

Verify outputs exist:
```bash
ls -la site/bundle.js site/index.html
```

### Step 3: Generate Gallery

```bash
make gallery
```

This:
- Copies `dashboard.html` from each session to `site/gallery/{session}/index.html`
- Copies `timelapse.gif` and `timelapse.mp4` if they exist
- Copies creative drawings
- Runs `build-gallery-index.sh` to generate `site/gallery/index.html`

Verify gallery was generated:
```bash
ls site/gallery/index.html
```

### Step 4: Deploy

```bash
make deploy
```

This is the full target (`build` + `gallery` + gh-pages push). If Steps 2-3 already ran successfully, `make deploy` will skip the redundant work (make dependency resolution).

Alternatively, run just the deploy portion if build and gallery are already done:
```bash
# The deploy target in the Makefile handles the full flow,
# so just run make deploy — it depends on build and gallery.
make deploy
```

The deploy target:
1. Creates a temporary directory
2. Checks out `gh-pages` as a git worktree there
3. Copies `site/bundle.js`, `site/index.html`, and `site/gallery/` into the worktree
4. Commits and pushes to `origin gh-pages`
5. Cleans up the worktree

### Step 5: Verify

After deploy completes:

1. **Check the commit landed:**
   ```bash
   git log --oneline -1 origin/gh-pages
   ```

2. **Verify the live site responds** (may take 1-2 minutes for GitHub Pages to update):
   ```bash
   curl -s -o /dev/null -w "%{http_code}" https://art.bytesofpurpose.com/
   ```
   Should return `200`.

3. **Verify the gallery page responds:**
   ```bash
   curl -s -o /dev/null -w "%{http_code}" https://art.bytesofpurpose.com/gallery/
   ```

4. **Verify analysis tools respond:**
   ```bash
   curl -s -o /dev/null -w "%{http_code}" https://art.bytesofpurpose.com/tools/analysis/showcase.html
   curl -s -o /dev/null -w "%{http_code}" https://art.bytesofpurpose.com/tools/analysis/star-intersection-map.html
   curl -s -o /dev/null -w "%{http_code}" https://art.bytesofpurpose.com/tools/analysis/construction-overlay.html
   ```

5. **Verify components page responds (if exists):**
   ```bash
   curl -s -o /dev/null -w "%{http_code}" https://art.bytesofpurpose.com/components/
   ```

6. Report results to the user with all live URLs that returned 200.

**If any endpoint returns 404 after waiting 2 minutes**, check that the file exists in the gh-pages branch:
```bash
git log --oneline -1 origin/gh-pages
git show origin/gh-pages:<path/to/file> | head -1
```

### Updating Deployed Pages

When new functionality is added to the project, update the corresponding deployed pages:

1. **New analysis tool added** → Update `tools/analysis/showcase.html` with screenshots and description. Update `tools/analysis/README.md`. Re-deploy.
2. **New session completed** → Gallery is auto-built from session data by `make gallery`. Re-deploy.
3. **New component added** → Update `templates/components/index.html`. Re-deploy.
4. **Site bundle changed** → `make build` rebuilds `site/bundle.js`. Re-deploy.

After each deploy, run the full verification checklist (all curl checks above).

## Error Recovery

| Error | Fix |
|-------|-----|
| `make compile` fails | Fix TypeScript or ESLint errors first |
| `fatal: 'gh-pages' is already checked out` | Run `git worktree remove <path> --force`, then retry |
| `npm run build` fails | Check `webpack.config.js`, run `npm install` |
| `git push` fails | Check remote auth, try `git push origin gh-pages` manually |
| Gallery empty | Check sessions directory path, verify `session.json` files exist |
| Site returns 404 after deploy | Wait 2 minutes (GitHub Pages cache), check that `index.html` is in the gh-pages root |

## Related

- `Makefile` — `build`, `gallery`, `deploy` targets
- `CLAUDE.md` — build commands reference
- `/creative-generation` — generates timelapse assets included in gallery
- `/learn-new-pattern` — generates session dashboards included in gallery
