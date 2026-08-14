import fs from "node:fs";
import path from "node:path";
import { defineConfig, devices } from "@playwright/test";

const repoRoot = path.join(__dirname, "../..");
const winPython = path.join(repoRoot, ".venv", "Scripts", "python.exe");
const nixPython = path.join(repoRoot, ".venv", "bin", "python");
const python = fs.existsSync(winPython)
  ? winPython
  : fs.existsSync(nixPython)
    ? nixPython
    : "python";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  timeout: 45000,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
  },
  webServer: [
    {
      command: `"${python}" -m uvicorn pixel_api.main:app --host 127.0.0.1 --port 8000`,
      cwd: repoRoot,
      url: "http://127.0.0.1:8000/health",
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
    },
    {
      command: "npm run dev",
      url: "http://localhost:3000",
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
    },
  ],
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        launchOptions: {
          args: ["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream"],
        },
      },
    },
  ],
});
