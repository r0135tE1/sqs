import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: 'list',
  use: {
    baseURL: 'http://localhost',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: {
    // Assumes docker compose is running. If not, this command starts it.
    // Use `reuseExistingServer` to skip startup if it's already up.
    command: 'docker compose up',
    cwd: '../..',
    url: 'http://localhost',
    reuseExistingServer: true,
    timeout: 120_000,
  },
})
