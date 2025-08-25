// 🏢⚡ Energy Optimizer Pro - Playwright E2E Testing Configuration
// =================================================================

import { defineConfig, devices } from '@playwright/test'

/**
 * See https://playwright.dev/docs/test-configuration.
 */
export default defineConfig({
  // Test directory
  testDir: './e2e',
  
  // Run tests in files in parallel
  fullyParallel: true,
  
  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,
  
  // Retry on CI only
  retries: process.env.CI ? 2 : 0,
  
  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter to use
  reporter: [
    ['html'],
    ['json', { outputFile: 'playwright-report/results.json' }],
    ['junit', { outputFile: 'playwright-report/results.xml' }],
    process.env.CI ? ['github'] : ['list'],
  ],
  
  // Shared settings for all the projects below
  use: {
    // Base URL for tests
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',
    
    // Browser context options
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,
    
    // Collect trace when retrying the failed test
    trace: 'on-first-retry',
    
    // Record video on failure
    video: 'retain-on-failure',
    
    // Take screenshot on failure
    screenshot: 'only-on-failure',
    
    // Action timeout
    actionTimeout: 10000,
    
    // Navigation timeout
    navigationTimeout: 30000,
    
    // Custom test timeout
    testIdAttribute: 'data-testid',
  },

  // Configure projects for major browsers
  projects: [
    // ================================
    // 🌐 Desktop Browsers
    // ================================
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Additional Chrome-specific settings
        launchOptions: {
          args: [
            '--disable-web-security',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--disable-background-timer-throttling',
          ],
        },
      },
    },
    
    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
        // Firefox-specific settings
        launchOptions: {
          firefoxUserPrefs: {
            'media.navigator.streams.fake': true,
            'media.navigator.permission.disabled': true,
          },
        },
      },
    },
    
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    // ================================
    // 📱 Mobile Browsers  
    // ================================
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },

    // ================================
    // 🖥️ High-DPI Displays
    // ================================
    {
      name: 'chromium-hidpi',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
        deviceScaleFactor: 2,
      },
    },

    // ================================
    // ♿ Accessibility Testing
    // ================================
    {
      name: 'accessibility',
      use: {
        ...devices['Desktop Chrome'],
        // Enable accessibility tree snapshots
        extraHTTPHeaders: {
          'Accept-Language': 'en-US,en;q=0.9',
        },
      },
      testMatch: '**/*.accessibility.spec.ts',
    },

    // ================================
    // 🚀 Performance Testing
    // ================================
    {
      name: 'performance',
      use: {
        ...devices['Desktop Chrome'],
        // Performance monitoring
        launchOptions: {
          args: [
            '--enable-precise-memory-info',
            '--enable-performance-manager-debugging',
          ],
        },
      },
      testMatch: '**/*.performance.spec.ts',
    },
  ],

  // ================================
  // 🌐 Development Server
  // ================================
  webServer: process.env.CI ? undefined : {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
    env: {
      NEXT_PUBLIC_ENVIRONMENT: 'test',
      NEXT_PUBLIC_API_URL: 'http://localhost:8000',
      NEXT_PUBLIC_WS_URL: 'ws://localhost:8000',
    },
  },

  // ================================
  // 📁 Test Organization
  // ================================
  
  // Test match patterns
  testMatch: [
    '**/*.spec.ts',
    '**/*.e2e.ts',
    '**/*.test.ts',
  ],
  
  // Test ignore patterns
  testIgnore: [
    '**/node_modules/**',
    '**/dist/**',
    '**/.next/**',
    '**/coverage/**',
  ],

  // ================================
  // ⚙️ Global Setup & Teardown
  // ================================
  
  // Global setup (run once before all tests)
  globalSetup: './e2e/global-setup.ts',
  
  // Global teardown (run once after all tests)
  globalTeardown: './e2e/global-teardown.ts',
  
  // Setup for each test file
  // testDir: './e2e',

  // ================================
  // 📊 Reporting & Artifacts
  // ================================
  
  // Output directory for test artifacts
  outputDir: 'test-results/',
  
  // Maximum time one test can run for
  timeout: 30000,
  
  // Maximum time for the whole test suite
  globalTimeout: 600000,
  
  // Expect assertions timeout
  expect: {
    timeout: 5000,
    toHaveScreenshot: {
      // Screenshot comparison options
      mode: 'strict',
      threshold: 0.2,
    },
  },

  // ================================
  // 🔧 Advanced Configuration
  // ================================
  
  // Maximum failures
  maxFailures: process.env.CI ? 10 : undefined,
  
  // Update snapshots
  updateSnapshots: process.env.UPDATE_SNAPSHOTS ? 'all' : 'missing',
  
  // Preserve output on failure
  preserveOutput: 'failures-only',

  // Custom metadata
  metadata: {
    'energy-optimizer-version': '1.0.0',
    'test-environment': process.env.PLAYWRIGHT_ENV || 'local',
  },
})
