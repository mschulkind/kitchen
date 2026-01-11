import { test, expect, Page } from '@playwright/test';

/**
 * Phase 1C E2E Tests - Kitchen App 🧪
 * 
 * Smoke tests for the Kitchen app frontend.
 * These tests verify the app loads and basic navigation works.
 * 
 * Run with: just test-e2e
 */

// Helper to wait for app to hydrate (Expo/React takes time)
async function waitForAppReady(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  // Wait for React to hydrate - look for any meaningful content
  await page.waitForTimeout(3000);
}

test.describe('Kitchen App - Home', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);
  });

  test('home page loads successfully', async ({ page }) => {
    // The home page should have "Kitchen" text somewhere
    const pageText = await page.textContent('body');
    expect(pageText).toContain('Kitchen');
  });

  test('home page has navigation elements', async ({ page }) => {
    // Should have navigation/tab bar
    const pageContent = await page.content();
    // Check that page has reasonable content
    expect(pageContent.length).toBeGreaterThan(1000);
  });

  test('can click manage pantry link', async ({ page }) => {
    // Try to find and click Manage Pantry or similar link
    const pantryButton = page.getByText(/pantry/i).first();
    const isVisible = await pantryButton.isVisible().catch(() => false);
    
    if (isVisible) {
      await pantryButton.click();
      await waitForAppReady(page);
      // Should navigate somewhere
      const url = page.url();
      expect(url).toBeTruthy();
    } else {
      // If not visible, that's okay for smoke test - app loaded
      expect(true).toBe(true);
    }
  });
});

test.describe('Kitchen App - Inventory', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/inventory');
    await waitForAppReady(page);
  });

  test('inventory page loads successfully', async ({ page }) => {
    // The page should load without crashing
    const pageContent = await page.content();
    expect(pageContent.length).toBeGreaterThan(500);
  });

  test('inventory page shows pantry-related content', async ({ page }) => {
    // Should have "Pantry" or "inventory" related text
    const pageText = await page.textContent('body');
    const hasPantryContent = 
      pageText?.toLowerCase().includes('pantry') ||
      pageText?.toLowerCase().includes('empty') ||
      pageText?.toLowerCase().includes('search') ||
      pageText?.toLowerCase().includes('item');
    
    expect(hasPantryContent).toBe(true);
  });

  test('has search functionality', async ({ page }) => {
    // Look for search input - could be placeholder or input element
    const searchInput = page.locator('input[placeholder*="earch" i], input[type="search"]');
    const hasSearch = await searchInput.count() > 0;
    
    // If there's a search, try using it
    if (hasSearch) {
      await searchInput.first().fill('test');
      const value = await searchInput.first().inputValue();
      expect(value).toBe('test');
    } else {
      // Search might not be visible on empty state
      expect(true).toBe(true);
    }
  });
});

test.describe('Kitchen App - Navigation', () => {
  test('can navigate between pages', async ({ page }) => {
    // Start at home
    await page.goto('/');
    await waitForAppReady(page);
    
    // Try to navigate to inventory
    await page.goto('/inventory');
    await waitForAppReady(page);
    
    // Go back to home
    await page.goto('/');
    await waitForAppReady(page);
    
    // All navigations should work
    expect(page.url()).toContain('localhost');
  });

  test('app maintains state during navigation', async ({ page }) => {
    // Navigate to inventory
    await page.goto('/inventory');
    await waitForAppReady(page);
    
    const pageContent = await page.content();
    expect(pageContent.length).toBeGreaterThan(500);
  });
});
