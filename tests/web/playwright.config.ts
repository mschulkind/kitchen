import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html', { open: 'never' }]],
  // Increase timeout for Expo's slow initial bundle
  timeout: 60000,
  expect: {
    timeout: 30000,
  },
  use: {
    baseURL: `http://localhost:${process.env.WEB_PORT || 8201}`,
    trace: 'on-first-retry',
    headless: true,
    // Wait longer for navigation
    navigationTimeout: 60000,
  },
  webServer: {
    command: 'cd ../../src/mobile && npx expo start --web --port 8201',
    port: 8201,
    reuseExistingServer: !process.env.CI,
    // Give Expo more time to bundle
    timeout: 180 * 1000,
    stdout: 'pipe',
    stderr: 'pipe',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
