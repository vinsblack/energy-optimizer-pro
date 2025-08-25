// 🏢⚡ Energy Optimizer Pro - E2E Dashboard Tests
// ===============================================

import { test, expect } from '@playwright/test'

test.describe('🏢 Energy Optimizer Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the dashboard
    await page.goto('/')
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle')
  })

  test('should display dashboard title and navigation', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Energy Optimizer Pro/)
    
    // Check main heading
    await expect(page.locator('h1')).toContainText('Energy Dashboard')
    
    // Check navigation elements
    await expect(page.locator('[data-testid="nav-dashboard"]')).toBeVisible()
    await expect(page.locator('[data-testid="nav-buildings"]')).toBeVisible()
    await expect(page.locator('[data-testid="nav-analytics"]')).toBeVisible()
    await expect(page.locator('[data-testid="nav-optimization"]')).toBeVisible()
  })

  test('should display key metrics cards', async ({ page }) => {
    // Wait for metrics to load
    await page.waitForSelector('[data-testid="metrics-grid"]')
    
    // Check all metric cards are present
    const metricCards = [
      'total-buildings',
      'energy-consumption', 
      'cost-savings',
      'efficiency-score',
      'carbon-reduction',
    ]
    
    for (const metric of metricCards) {
      await expect(page.locator(`[data-testid="metric-${metric}"]`)).toBeVisible()
      
      // Check that values are displayed (not loading states)
      const valueElement = page.locator(`[data-testid="metric-${metric}"] [data-testid="metric-value"]`)
      await expect(valueElement).not.toContainText('--')
      await expect(valueElement).not.toContainText('Loading')
    }
  })

  test('should display energy consumption chart', async ({ page }) => {
    // Check chart container
    await expect(page.locator('[data-testid="energy-chart"]')).toBeVisible()
    
    // Check chart components
    await expect(page.locator('[data-testid="line-chart"]')).toBeVisible()
    await expect(page.locator('[data-testid="x-axis"]')).toBeVisible()
    await expect(page.locator('[data-testid="y-axis"]')).toBeVisible()
    
    // Check chart controls
    await expect(page.locator('[data-testid="chart-time-range"]')).toBeVisible()
    await expect(page.locator('[data-testid="chart-refresh"]')).toBeVisible()
  })

  test('should allow time range selection for charts', async ({ page }) => {
    // Open time range selector
    await page.click('[data-testid="chart-time-range"]')
    
    // Check available options
    const timeRanges = ['24h', '7d', '30d', '90d', '1y']
    
    for (const range of timeRanges) {
      await expect(page.locator(`[data-testid="time-range-${range}"]`)).toBeVisible()
    }
    
    // Select 7 days
    await page.click('[data-testid="time-range-7d"]')
    
    // Wait for chart to update
    await page.waitForTimeout(1000)
    
    // Verify selection is active
    await expect(page.locator('[data-testid="time-range-7d"]')).toHaveClass(/active|selected/)
  })

  test('should display buildings overview', async ({ page }) => {
    // Check buildings section
    await expect(page.locator('[data-testid="buildings-overview"]')).toBeVisible()
    
    // Check buildings grid/list
    await expect(page.locator('[data-testid="buildings-grid"]')).toBeVisible()
    
    // Check that at least one building is displayed
    const buildingCards = page.locator('[data-testid^="building-card-"]')
    await expect(buildingCards.first()).toBeVisible()
    
    // Check building card content
    const firstCard = buildingCards.first()
    await expect(firstCard.locator('[data-testid="building-name"]')).toBeVisible()
    await expect(firstCard.locator('[data-testid="building-type"]')).toBeVisible()
    await expect(firstCard.locator('[data-testid="building-efficiency"]')).toBeVisible()
  })

  test('should navigate to building details', async ({ page }) => {
    // Wait for buildings to load
    await page.waitForSelector('[data-testid^="building-card-"]')
    
    // Click on first building
    const firstBuilding = page.locator('[data-testid^="building-card-"]').first()
    await firstBuilding.click()
    
    // Should navigate to building details page
    await expect(page).toHaveURL(/\/buildings\/[^\/]+/)
    
    // Check building details page elements
    await expect(page.locator('[data-testid="building-details"]')).toBeVisible()
    await expect(page.locator('[data-testid="building-energy-chart"]')).toBeVisible()
    await expect(page.locator('[data-testid="building-metrics"]')).toBeVisible()
  })

  test('should handle responsive design', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    
    // Check mobile navigation
    await expect(page.locator('[data-testid="mobile-nav-toggle"]')).toBeVisible()
    
    // Open mobile menu
    await page.click('[data-testid="mobile-nav-toggle"]')
    await expect(page.locator('[data-testid="mobile-nav-menu"]')).toBeVisible()
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 })
    
    // Metrics should be in grid layout
    await expect(page.locator('[data-testid="metrics-grid"]')).toBeVisible()
    
    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 })
    
    // Full navigation should be visible
    await expect(page.locator('[data-testid="desktop-nav"]')).toBeVisible()
  })

  test('should display real-time data updates', async ({ page }) => {
    // Enable real-time updates if available
    const realtimeToggle = page.locator('[data-testid="realtime-toggle"]')
    if (await realtimeToggle.isVisible()) {
      await realtimeToggle.click()
      
      // Wait for real-time connection
      await page.waitForTimeout(2000)
      
      // Check for real-time indicator
      await expect(page.locator('[data-testid="realtime-indicator"]')).toBeVisible()
      await expect(page.locator('[data-testid="realtime-indicator"]')).toHaveClass(/connected|active/)
    }
  })

  test('should handle error states gracefully', async ({ page }) => {
    // Test with invalid API endpoint
    await page.route('**/api/**', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      })
    })
    
    // Reload page to trigger error
    await page.reload()
    
    // Should display error message
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible()
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible()
    
    // Test retry functionality
    await page.unroute('**/api/**')
    await page.click('[data-testid="retry-button"]')
    
    // Should recover and display data
    await page.waitForTimeout(2000)
    await expect(page.locator('[data-testid="metrics-grid"]')).toBeVisible()
  })

  test('should search and filter buildings', async ({ page }) => {
    // Navigate to buildings page
    await page.click('[data-testid="nav-buildings"]')
    await expect(page).toHaveURL('/buildings')
    
    // Test search functionality
    const searchInput = page.locator('[data-testid="buildings-search"]')
    await searchInput.fill('office')
    
    // Wait for search results
    await page.waitForTimeout(1000)
    
    // Check filtered results
    const visibleBuildings = page.locator('[data-testid^="building-card-"]:visible')
    await expect(visibleBuildings.first()).toBeVisible()
    
    // Test building type filter
    await page.click('[data-testid="filter-type"]')
    await page.click('[data-testid="filter-office"]')
    
    // Wait for filter to apply
    await page.waitForTimeout(1000)
    
    // Verify filtered results
    const filteredBuildings = page.locator('[data-testid^="building-card-"]:visible')
    const count = await filteredBuildings.count()
    expect(count).toBeGreaterThan(0)
  })

  test('should export data functionality', async ({ page }) => {
    // Click export button
    await page.click('[data-testid="export-data"]')
    
    // Choose export format
    await page.click('[data-testid="export-format-csv"]')
    
    // Wait for download
    const downloadPromise = page.waitForEvent('download')
    await page.click('[data-testid="export-confirm"]')
    const download = await downloadPromise
    
    // Verify download
    expect(download.suggestedFilename()).toMatch(/energy-data.*\.csv/)
    
    // Save the download for verification
    await download.saveAs('./test-results/downloaded-file.csv')
  })

  test('should handle authentication flow', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login')
    
    // Fill login form
    await page.fill('[data-testid="email-input"]', 'admin@energy-optimizer.com')
    await page.fill('[data-testid="password-input"]', 'admin123')
    
    // Submit form
    await page.click('[data-testid="login-submit"]')
    
    // Should redirect to dashboard after successful login
    await expect(page).toHaveURL('/')
    
    // Check authenticated user elements
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
    await expect(page.locator('[data-testid="logout-button"]')).toBeVisible()
  })

  test('should run optimization workflow', async ({ page }) => {
    // Navigate to optimization page
    await page.click('[data-testid="nav-optimization"]')
    await expect(page).toHaveURL('/optimization')
    
    // Select building for optimization
    await page.click('[data-testid="select-building"]')
    await page.click('[data-testid="building-option-0"]')
    
    // Select ML algorithm
    await page.click('[data-testid="select-algorithm"]')
    await page.click('[data-testid="algorithm-xgboost"]')
    
    // Start optimization
    await page.click('[data-testid="start-optimization"]')
    
    // Check progress indicator
    await expect(page.locator('[data-testid="optimization-progress"]')).toBeVisible()
    
    // Wait for completion (with timeout)
    await page.waitForSelector('[data-testid="optimization-results"]', { timeout: 60000 })
    
    // Verify results are displayed
    await expect(page.locator('[data-testid="energy-savings"]')).toBeVisible()
    await expect(page.locator('[data-testid="cost-savings"]')).toBeVisible()
    await expect(page.locator('[data-testid="recommendations"]')).toBeVisible()
  })
})

test.describe('🔔 Notifications and Alerts', () => {
  test('should display and manage notifications', async ({ page }) => {
    await page.goto('/')
    
    // Check notification center
    await page.click('[data-testid="notification-center"]')
    await expect(page.locator('[data-testid="notifications-panel"]')).toBeVisible()
    
    // Mark notification as read
    const notification = page.locator('[data-testid^="notification-"]:first')
    if (await notification.isVisible()) {
      await notification.click()
      await expect(notification).toHaveClass(/read/)
    }
  })

  test('should handle system alerts', async ({ page }) => {
    await page.goto('/')
    
    // Simulate system alert via WebSocket
    await page.evaluate(() => {
      // Mock WebSocket message
      window.dispatchEvent(new CustomEvent('mock-alert', {
        detail: {
          type: 'warning',
          message: 'Energy consumption above threshold',
          building_id: 'test-building'
        }
      }))
    })
    
    // Check alert display
    await expect(page.locator('[data-testid="system-alert"]')).toBeVisible()
    await expect(page.locator('[data-testid="system-alert"]')).toContainText('Energy consumption above threshold')
  })
})

test.describe('📊 Analytics and Reporting', () => {
  test('should generate and download reports', async ({ page }) => {
    await page.goto('/analytics')
    
    // Open report generator
    await page.click('[data-testid="generate-report"]')
    
    // Configure report settings
    await page.selectOption('[data-testid="report-type"]', 'energy-summary')
    await page.selectOption('[data-testid="report-format"]', 'pdf')
    
    // Set date range
    await page.fill('[data-testid="date-from"]', '2024-07-01')
    await page.fill('[data-testid="date-to"]', '2024-07-31')
    
    // Generate report
    const downloadPromise = page.waitForEvent('download')
    await page.click('[data-testid="generate-report-submit"]')
    
    // Wait for generation to complete
    await page.waitForSelector('[data-testid="report-ready"]', { timeout: 30000 })
    
    // Download report
    await page.click('[data-testid="download-report"]')
    const download = await downloadPromise
    
    // Verify download
    expect(download.suggestedFilename()).toMatch(/energy-summary.*\.pdf/)
  })

  test('should display interactive charts', async ({ page }) => {
    await page.goto('/analytics')
    
    // Check various chart types
    const chartTypes = ['energy-trend', 'efficiency-comparison', 'cost-breakdown']
    
    for (const chartType of chartTypes) {
      await expect(page.locator(`[data-testid="chart-${chartType}"]`)).toBeVisible()
      
      // Test chart interactions
      const chart = page.locator(`[data-testid="chart-${chartType}"]`)
      await chart.hover()
      
      // Check tooltip appears
      await expect(page.locator('[data-testid="tooltip"]')).toBeVisible()
    }
  })
})

test.describe('⚡ Performance and Accessibility', () => {
  test('should meet performance benchmarks', async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/')
    
    // Measure performance
    const performanceMetrics = await page.evaluate(() => {
      const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
      return {
        loadTime: perfData.loadEventEnd - perfData.loadEventStart,
        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
        timeToInteractive: perfData.loadEventEnd - perfData.fetchStart,
      }
    })
    
    // Assert performance targets
    expect(performanceMetrics.loadTime).toBeLessThan(3000) // 3 seconds
    expect(performanceMetrics.domContentLoaded).toBeLessThan(2000) // 2 seconds
    expect(performanceMetrics.timeToInteractive).toBeLessThan(5000) // 5 seconds
  })

  test('should be accessible', async ({ page }) => {
    await page.goto('/')
    
    // Check basic accessibility
    await expect(page.locator('main')).toBeVisible()
    await expect(page.locator('h1')).toBeVisible()
    
    // Test keyboard navigation
    await page.keyboard.press('Tab')
    await expect(page.locator(':focus')).toBeVisible()
    
    // Check for skip links
    await page.keyboard.press('Tab')
    const skipLink = page.locator('[data-testid="skip-to-main"]')
    if (await skipLink.isVisible()) {
      await expect(skipLink).toBeFocused()
    }
    
    // Test color contrast (basic check)
    const headingElement = page.locator('h1')
    const styles = await headingElement.evaluate(el => {
      const computed = window.getComputedStyle(el)
      return {
        color: computed.color,
        backgroundColor: computed.backgroundColor,
      }
    })
    
    // Basic contrast check (this would need a more sophisticated implementation)
    expect(styles.color).toBeTruthy()
    expect(styles.backgroundColor).toBeTruthy()
  })
})

test.describe('🔄 Real-time Features', () => {
  test('should connect to WebSocket and receive updates', async ({ page }) => {
    await page.goto('/')
    
    // Enable real-time mode if available
    const realtimeToggle = page.locator('[data-testid="realtime-toggle"]')
    if (await realtimeToggle.isVisible()) {
      await realtimeToggle.click()
      
      // Wait for WebSocket connection
      await page.waitForTimeout(2000)
      
      // Check connection status
      await expect(page.locator('[data-testid="realtime-status"]')).toContainText(/connected|online/i)
      
      // Mock WebSocket message
      await page.evaluate(() => {
        // Simulate real-time energy update
        window.dispatchEvent(new CustomEvent('mock-ws-message', {
          detail: {
            type: 'energy_update',
            building_id: 'test-building',
            data: {
              consumption: 245.7,
              timestamp: new Date().toISOString(),
            }
          }
        }))
      })
      
      // Check that UI updates with new data
      await page.waitForTimeout(1000)
      // This would check for actual data updates in a real implementation
    }
  })
})

test.describe('🔍 Search and Filtering', () => {
  test('should search across the application', async ({ page }) => {
    await page.goto('/')
    
    // Open global search
    await page.click('[data-testid="global-search"]')
    
    // Search for buildings
    await page.fill('[data-testid="search-input"]', 'office')
    await page.keyboard.press('Enter')
    
    // Check search results
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible()
    await expect(page.locator('[data-testid^="search-result-"]')).toHaveCount(1, { timeout: 5000 })
  })
})

test.describe('📱 Mobile Experience', () => {
  test.use({ viewport: { width: 375, height: 667 } })
  
  test('should work on mobile devices', async ({ page }) => {
    await page.goto('/')
    
    // Check mobile-specific elements
    await expect(page.locator('[data-testid="mobile-nav-toggle"]')).toBeVisible()
    
    // Test mobile navigation
    await page.click('[data-testid="mobile-nav-toggle"]')
    await expect(page.locator('[data-testid="mobile-nav-menu"]')).toBeVisible()
    
    // Test mobile charts (should be responsive)
    await expect(page.locator('[data-testid="energy-chart"]')).toBeVisible()
    
    // Test touch interactions
    const chart = page.locator('[data-testid="energy-chart"]')
    await chart.tap()
    
    // Check mobile-optimized tooltips
    await expect(page.locator('[data-testid="mobile-tooltip"]')).toBeVisible()
  })

  test('should handle mobile gestures', async ({ page }) => {
    await page.goto('/buildings')
    
    // Test swipe gestures for navigation (if implemented)
    const buildingsList = page.locator('[data-testid="buildings-list"]')
    
    // Simulate swipe
    await buildingsList.touchscreen.tap({ x: 200, y: 300 })
    await page.touchscreen.tap({ x: 100, y: 300 })
    
    // Check if swipe navigation worked
    // This would be implemented based on actual swipe functionality
  })
})
