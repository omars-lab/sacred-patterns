# Clean-session prompt — reclaim `art.bytesofpurpose.com` (and decide `3d-models`) for GitHub Pages

Copy everything in the fenced block below into a fresh Claude Code session started in
`/Users/omareid/Workspace/git/private-site`.

---

```
Context — read before acting:

I have two GitHub-Pages-hosted galleries on the `sacred-patterns` repo (org: omars-lab),
served from its `gh-pages` branch:
  - Sacred Patterns gallery — reachable today at https://blog.bytesofpurpose.com/sacred-patterns/
  - 3D Models gallery ("Islamic Cookie Cutters") — reachable today at https://blog.bytesofpurpose.com/3d-models/

`blog.bytesofpurpose.com` is a PRE-EXISTING DNS record that already points at GitHub Pages
and is explicitly NOT managed by the private-site Cloudflare stack (see
private-site/docs/domains.md "Pre-existing records").

The problem I want to fix:
`art.bytesofpurpose.com` used to point at GitHub Pages (the sacred-patterns gh-pages branch
served via a CNAME file at the gh-pages root). It currently does NOT — it is owned by the
Cloudflare Tunnel + Kong stack in THIS repo (private-site). From private-site/docs/domains.md
and private-site/kong/kong.prod.yml:
  - `art.bytesofpurpose.com` is a CNAME → Cloudflare Tunnel
    `587e13aa-b2cb-4d42-9ad2-b4578af4e383.cfargotunnel.com`
  - Tunnel ingress routes all subdomains to http://kong:8000
  - Kong route `art` (service `art-server`, hosts: [art.bytesofpurpose.com]) serves
    "Art HTMLs synced from Dropbox" (private-site/art/index.html, art_path in hosts.yml)
  - There is a Cloudflare Access BYPASS app "Public Art Gallery"
    (App ID 40c93395-aee8-44b7-86a2-a44886e28779, domain art.bytesofpurpose.com)
Because the Cloudflare DNS record for `art` is proxied to the tunnel, GitHub Pages can't
own the hostname, and on 2026-06-05 I deleted the CNAME file from the sacred-patterns
gh-pages branch (so GitHub Pages would stop fighting over it). As a result
https://art.bytesofpurpose.com/ now returns 530 (tunnel-side error) and the GitHub-Pages
gallery is only reachable via the blog. path.

What I want you to do:

1. INVESTIGATE FIRST, do not change anything yet. Read, in private-site:
   - docs/domains.md (domain table, DNS Records, Tunnel Ingress sections)
   - docs/cloudflare-setup-log.md
   - .claude/skills/cloudflare-setup/SKILL.md and .claude/skills/configure-access/SKILL.md
   - kong/kong.prod.yml (the `art` service + routes)
   - docker-compose.yml (the art-server service block)
   - how DNS records and CF Access apps are actually managed here (Terraform? a Makefile
     target? the cloudflare-setup skill calling the CF API? check the Makefile and .env for
     CLOUDFLARE_* tokens / account+zone IDs — do NOT print secret values).
   Then tell me the exact mechanism by which `art.bytesofpurpose.com`'s DNS record and its
   CF Access bypass app are created, so I know what has to be reversed.

2. DESIGN the cutover to hand `art.bytesofpurpose.com` back to GitHub Pages. The end state I
   want: `art.bytesofpurpose.com` resolves to GitHub Pages (omars-lab.github.io) and serves
   the sacred-patterns gh-pages site, the same way `blog.` does. That almost certainly means,
   in Cloudflare for the `art` record:
     - remove the proxied CNAME → cfargotunnel.com tunnel record
     - replace it with the GitHub Pages target — EITHER a CNAME `art` → `omars-lab.github.io`
       (DNS-only / grey-cloud, NOT proxied, so GitHub's TLS + Pages custom-domain works),
       OR whatever pattern `blog.` already uses (inspect blog.'s record and mirror it —
       blog. is the proven-working reference for "this subdomain is GitHub Pages, not tunnel").
     - remove or repoint the Kong `art` route + art-server service (and the now-orphaned
       "Public Art Gallery" CF Access bypass app) so nothing in private-site still claims the
       hostname.
   And on the GitHub side: restore a CNAME file containing `art.bytesofpurpose.com` at the
   root of the sacred-patterns gh-pages branch, and set the custom domain in the repo's Pages
   settings. (Coordinate with me — the sacred-patterns repo is at
   /Users/omareid/Workspace/git/sacred-patterns; its deploy skill copies a CNAME from site/
   into gh-pages if present. Decide where the CNAME source-of-truth should live so a future
   `make deploy` doesn't re-delete it.)

   Spell out every step, name the exact files/commands/CF resources, and call out anything
   destructive (DNS edits, deleting a tunnel route, deleting an Access app) so I can approve
   before you run it. Note the GitHub Pages "custom domain" verification + TLS-issuance lag
   (can take minutes to an hour) in the rollout plan.

3. ALSO handle `3d-models`. NOTE THE ASYMMETRY first: unlike `art`, there is currently NO
   `3d-models` / `models` subdomain anywhere in private-site (I grepped — zero references),
   and the 3D gallery is today only a PATH under the github-pages `blog.` domain
   (https://blog.bytesofpurpose.com/3d-models/). So there is nothing to "reclaim" from
   Cloudflare for it. Before designing anything, ASK ME which outcome I want:
     (a) leave 3d-models as a path under blog. (no work), or
     (b) give it its own GitHub-Pages custom subdomain — e.g. `3d-models.bytesofpurpose.com`
         or `models.bytesofpurpose.com` — pointed at GitHub Pages exactly like the restored
         `art` record (new DNS-only CNAME → omars-lab.github.io, custom domain on the repo
         that hosts it, CNAME file on its gh-pages branch).
   If (b), find out which repo/branch currently publishes the /3d-models/ content (it may be
   a different repo than sacred-patterns — check what serves blog.bytesofpurpose.com/3d-models/)
   and design the same DNS-only-CNAME + Pages-custom-domain cutover for it.

Constraints:
   - Do not edit anything until I approve the plan. Investigate + design, then present.
   - Never print secret values from .env (CF API tokens, etc.) — reference them by name only.
   - DNS / CF Access / tunnel-route changes are externally-visible and destructive: list them
     explicitly and get my go-ahead per change.
   - Prefer mirroring the already-working `blog.` record pattern over inventing a new one.
   - Use private-site's own skills (cloudflare-setup, configure-access) and Makefile targets
     where they exist rather than hand-rolling CF API calls.
```

---

## Why this prompt is shaped this way (notes for me, not for the clean session)

- `blog.bytesofpurpose.com` already works as GitHub Pages and is documented as a pre-existing,
  non-tunnel record — it's the proven reference pattern to mirror for `art`.
- The blocker for `art` is specifically the **proxied CNAME → cfargotunnel.com** plus the Kong
  `art` route + the "Public Art Gallery" CF Access bypass app — all three live in private-site
  and all three must be reversed, not just the DNS record.
- The CNAME file was deleted from gh-pages on 2026-06-05 (this session). Restoring it is the
  GitHub-side half; the sacred-patterns `deploy` skill copies `site/CNAME` → gh-pages if it
  exists, so the CNAME source-of-truth should live in the sacred-patterns repo (e.g. committed
  so `make deploy` re-emits it) — otherwise a future deploy silently drops it again.
- `3d-models` is deliberately left as an open question (a) vs (b) because there is no existing
  subdomain to reclaim — guessing a subdomain name or assuming intent would be wrong.
```
