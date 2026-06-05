/**
 * Playwright config for the gallery visual regression (Path B of the
 * review-site-visually skill). Serves the BUILT site/ and pins a single
 * chromium project + viewport so structural assertions are deterministic.
 * Run `npm run build` first, then `npm run test:visual`.
 *
 * This is intentionally separate from the gating `npm test` (JSDOM geometry
 * check) — visual tests are opt-in and not part of the fast pre-commit gate.
 */
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: ".claude/skills/review-site-visually/playwright",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0,
  reporter: "list",
  use: {
    baseURL: "http://localhost:4178",
    trace: "on-first-retry",
  },
  // Pin viewport + browser: screenshot determinism depends on it (snapshots
  // still diverge across CPU arch — see the skill's snapshot caveat).
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"], viewport: { width: 1440, height: 900 } },
    },
  ],
  webServer: {
    command: "npx serve site -l 4178",
    url: "http://localhost:4178",
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
  },
});
