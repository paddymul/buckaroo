import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './pw-tests',
  testMatch: 'integration.spec.ts',
  fullyParallel: false, // Integration tests should run serially
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1, // Only one worker for integration tests
  reporter: 'html',
  use: {
    trace: 'on-first-retry',
    // Timeouts for integration tests (30 seconds max)
    actionTimeout: 15000,
    navigationTimeout: 30000,
    timeout: 30000, // Test timeout
  },

  projects: [
    {
      name: 'chromium-integration',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // JupyterLab is started by the shell script, not by Playwright
});
