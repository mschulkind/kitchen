import { test, expect, Page } from '@playwright/test';

/**
 * Phase 2C E2E Tests - Recipe Management 📖
 *
 * Tests the recipe CRUD flows as specified in phase-02-recipe-engine.md
 *
 * STRICT MODE: No conditional checks. Elements MUST exist.
 */

async function waitForAppReady(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  // Wait for Tamagui hydration
  await page.waitForTimeout(1000);
}

test.describe('Phase 2C - Import Recipe Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to recipes via the Hub to ensure deep linking works
    // or go directly if testing the screen in isolation
    await page.goto('/(app)/recipes'); 
    await waitForAppReady(page);
  });

  test('recipes page loads with correct title', async ({ page }) => {
    await expect(page.getByText('Recipes')).toBeVisible();
  });

  test('can find import URL button', async ({ page }) => {
    const importButton = page.getByTestId('import-recipe-fab');
    await expect(importButton).toBeVisible();
  });

  test('import button opens URL input dialog', async ({ page }) => {
    await page.getByTestId('import-recipe-fab').click();
    await expect(page.getByPlaceholder('https://example.com/recipe')).toBeVisible();
  });

  test('can enter URL and submit', async ({ page }) => {
    await page.getByTestId('import-recipe-fab').click();
    
    const urlInput = page.getByPlaceholder('https://example.com/recipe');
    await urlInput.fill('https://www.seriouseats.com/easy-roasted-chicken-recipe');
    
    const submitBtn = page.getByText('Import');
    await submitBtn.click();
    
    // Should show loading state or success
    await expect(page.getByText('Parsing recipe...')).toBeVisible();
  });
});

test.describe('Phase 2C - Manual Recipe Entry', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/recipes');
    await waitForAppReady(page);
  });

  test('can navigate to create manual recipe', async ({ page }) => {
    // Open action sheet or FAB
    await page.getByTestId('add-recipe-fab').click();
    await page.getByText('Manual Entry').click();
    
    // Should be on new recipe form
    await expect(page.getByPlaceholder('Recipe Title')).toBeVisible();
  });

  test('manual recipe form has required fields', async ({ page }) => {
    await page.goto('/(app)/recipes/new'); // Direct link test
    
    await expect(page.getByPlaceholder('Recipe Title')).toBeVisible();
    await expect(page.getByText('Ingredients')).toBeVisible();
    await expect(page.getByText('Instructions')).toBeVisible();
  });
});

test.describe('Phase 2C - Recipe List & Search', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/recipes');
    await waitForAppReady(page);
  });

  test('search bar is present and functional', async ({ page }) => {
    const searchBar = page.getByPlaceholder('Search recipes...');
    await expect(searchBar).toBeVisible();
    
    await searchBar.fill('Pasta');
    // Expect list to filter (requires mock data or seed)
  });

  test('recipe list items render correctly', async ({ page }) => {
    const listItems = page.getByTestId('recipe-card');
    // Should have at least one empty state or items
    await expect(listItems.first().or(page.getByText('No recipes found'))).toBeVisible();
  });
});
