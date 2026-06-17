/**
 * Playwright config for the weave-studio URL-param round-trip (studio-url-params
 * .spec.ts). Unlike the gallery config (which serves a static site/), this boots
 * the live Python studio — wave-plan-server.py against the medallion-10 session —
 * because the URL-param behaviour under test is the studio's own client JS.
 *
 * Run: `npx playwright test --config tools/tests/studio-visual/studio.config.ts`
 * Prereqs: Node 22 on PATH (the studio shells to the bikar CLI to render), and
 * the medallion-10 session present at SESSION_DIR. Opt-in — NOT part of the fast
 * gate (it needs the bikar CLI + a real session, which CI doesn't have).
 *
 * STUDIO_PORT / SESSION_DIR are overridable via env so the same config runs in
 * other environments without editing the file.
 */
import { defineConfig, devices } from "@playwright/test";

const PORT = process.env.STUDIO_PORT ?? "8795";
const SESSION_DIR =
  process.env.SESSION_DIR ??
  "/Users/omareid/Dropbox/Data/sacred-patterns/bikar-medallion-10";

export default defineConfig({
  testDir: ".",
  fullyParallel: false, // one studio server; serialize to avoid render contention
  forbidOnly: !!process.env.CI,
  retries: 0,
  reporter: "list",
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"], viewport: { width: 1440, height: 900 } },
    },
  ],
  webServer: {
    // Playwright runs webServer.command from THIS config file's directory
    // (tools/tests/studio-visual), so the server is two levels up. SERVER_PY
    // lets CI/other envs override with an absolute path.
    command: `python3 ${process.env.SERVER_PY ?? "../../wave-plan-server.py"} ${SESSION_DIR} --center 386 361 --diameter 738 --port ${PORT}`,
    url: `http://127.0.0.1:${PORT}/weave-studio`,
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
  },
});
