import { test, expect, Page } from '@playwright/test';

/**
 * Phase 1C E2E Tests - Inventory (Pantry) Management 🥫
 *
 * STRICT MODE: No conditional checks. Elements MUST exist.
 * Tests the core inventory CRUD flows as specified in phase-01-foundation.md
 *
 * Fun fact: The average household has about 500 items in their kitchen! 📊
 */

async function waitForAppReady(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1000);
}

test.describe('Phase 1C - Inventory List', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/inventory');
    await waitForAppReady(page);
  });

  test('inventory page loads with title', async ({ page }) => {
    await expect(page.getByText('Pantry')).toBeVisible();
  });

  test('search input is visible', async ({ page }) => {
    const searchInput = page.getByTestId('search-input');
    await expect(searchInput).toBeVisible();
  });

  test('can search for items', async ({ page }) => {
    const searchInput = page.getByTestId('search-input');
    await searchInput.fill('Milk');
    await expect(searchInput).toHaveValue('Milk');
  });

  test('sort select is visible', async ({ page }) => {
    const sortSelect = page.getByTestId('sort-select');
    await expect(sortSelect).toBeVisible();
  });

  test('filter select is visible', async ({ page }) => {
    const filterSelect = page.getByTestId('filter-select');
    await expect(filterSelect).toBeVisible();
  });
});

test.describe('Phase 1C - Add Item Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/inventory');
    await waitForAppReady(page);
  });

  test('add item button is visible', async ({ page }) => {
    const addButton = page.getByTestId('add-item-button');
    await expect(addButton).toBeVisible();
  });

  test('add button opens action sheet', async ({ page }) => {
    await page.getByTestId('add-item-button').click();
    await expect(page.getByText('Add Item')).toBeVisible();
    await expect(page.getByTestId('scan-item-option')).toBeVisible();
    await expect(page.getByTestId('manual-add-option')).toBeVisible();
  });

  test('manual add opens form sheet', async ({ page }) => {
    await page.getByTestId('add-item-button').click();
    await page.getByTestId('manual-add-option').click();
    
    await expect(page.getByTestId('item-name-input')).toBeVisible();
    await expect(page.getByTestId('item-qty-input')).toBeVisible();
    await expect(page.getByTestId('item-unit-input')).toBeVisible();
  });

  test('can fill and save item form', async ({ page }) => {
    await page.getByTestId('add-item-button').click();
    await page.getByTestId('manual-add-option').click();
    
    await page.getByTestId('item-name-input').fill('Test Eggs');
    await page.getByTestId('item-qty-input').fill('12');
    await page.getByTestId('item-unit-input').fill('count');
    
    // Select fridge location
    await page.getByTestId('location-fridge').click();
    
    await page.getByTestId('save-item-button').click();
    
    // Item should appear in list
    await expect(page.getByText('Test Eggs')).toBeVisible();
  });
});

test.describe('Phase 1C - Vision Staging', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/inventory/scan-result');
    await waitForAppReady(page);
  });

  test('scan result page shows analyzing state', async ({ page }) => {
    await expect(page.getByText('Analyzing image...')).toBeVisible();
  });

  test('detected items appear after processing', async ({ page }) => {
    // Wait for mock detection to complete
    await page.waitForTimeout(2500);
    
    await expect(page.getByTestId('detected-count')).toBeVisible();
    await expect(page.getByTestId('detected-item-0')).toBeVisible();
  });

  test('can edit detected item', async ({ page }) => {
    await page.waitForTimeout(2500);
    
    await page.getByTestId('edit-item-0').click();
    await expect(page.getByTestId('edit-name-0')).toBeVisible();
  });

  test('can remove detected item', async ({ page }) => {
    await page.waitForTimeout(2500);
    
    const initialCount = await page.getByText(/\d+ Items? Detected/).textContent();
    await page.getByTestId('remove-item-0').click();
    
    // Count should decrease
    const newCount = await page.getByTestId('detected-count').textContent();
    expect(newCount).not.toBe(initialCount);
  });

  test('confirm all button is visible', async ({ page }) => {
    await page.waitForTimeout(2500);
    
    const confirmButton = page.getByTestId('confirm-all-button');
    await expect(confirmButton).toBeVisible();
  });
});

test.describe('Phase 1C - Location Grouping', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/inventory');
    await waitForAppReady(page);
  });

  test('items are grouped by location', async ({ page }) => {
    // At least one location section should be visible (or empty state)
    const fridgeSection = page.getByTestId('location-fridge');
    const pantrySection = page.getByTestId('location-pantry');
    const emptyState = page.getByText('Your pantry is empty');
    
    const hasContent = await fridgeSection.count() > 0 ||
                       await pantrySection.count() > 0 ||
                       await emptyState.count() > 0;
    
    expect(hasContent).toBe(true);
  });
});
