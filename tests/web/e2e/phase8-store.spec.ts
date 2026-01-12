import { test, expect, Page } from '@playwright/test';

/**
 * Phase 8C E2E Tests - Store Intelligence 🏪
 *
 * STRICT MODE: No conditional checks. Elements MUST exist.
 * Tests the store-based sorting flow as specified in phase-08-store-intelligence.md
 *
 * Fun fact: Following a sorted list can reduce shopping time by 30%! ⏱️
 */

async function waitForAppReady(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1000);
}

test.describe('Phase 8C - Store Selection', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/shopping');
    await waitForAppReady(page);
  });

  test('store selector is visible', async ({ page }) => {
    await expect(page.getByTestId('store-selector')).toBeVisible();
  });

  test('can open store dropdown', async ({ page }) => {
    await page.getByTestId('store-selector').click();
    await expect(page.getByTestId('store-options')).toBeVisible();
  });

  test('store options are listed', async ({ page }) => {
    await page.getByTestId('store-selector').click();
    await expect(page.getByTestId('store-option-0')).toBeVisible();
  });

  test('can select a store', async ({ page }) => {
    await page.getByTestId('store-selector').click();
    await page.getByTestId('store-option-0').click();
    
    // Selector should show selected store
    const selectorText = await page.getByTestId('store-selector').textContent();
    expect(selectorText?.length).toBeGreaterThan(0);
  });
});

test.describe('Phase 8C - Aisle Grouping', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/shopping');
    await waitForAppReady(page);
  });

  test('items are grouped by aisle when store selected', async ({ page }) => {
    // Select a store first
    await page.getByTestId('store-selector').click();
    await page.getByTestId('store-option-0').click();
    
    // Wait for re-sort
    await page.waitForTimeout(500);
    
    // Aisle headers should appear
    await expect(page.getByTestId('aisle-section-0')).toBeVisible();
  });

  test('aisle sections show aisle numbers', async ({ page }) => {
    await page.getByTestId('store-selector').click();
    await page.getByTestId('store-option-0').click();
    await page.waitForTimeout(500);
    
    // Should show aisle numbers
    await expect(page.getByText(/Aisle \d+/)).toBeVisible();
  });
});

test.describe('Phase 8C - Smart Sort Order', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/shopping');
    await waitForAppReady(page);
  });

  test('sort direction button is visible', async ({ page }) => {
    await expect(page.getByTestId('sort-direction-button')).toBeVisible();
  });

  test('can toggle sort direction', async ({ page }) => {
    const button = page.getByTestId('sort-direction-button');
    const initialText = await button.textContent();
    
    await button.click();
    
    const newText = await button.textContent();
    expect(newText).not.toBe(initialText);
  });
});

test.describe('Phase 8C - Store Settings', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/settings');
    await waitForAppReady(page);
  });

  test('store management section exists', async ({ page }) => {
    await expect(page.getByText('Stores')).toBeVisible();
  });

  test('add store button is visible', async ({ page }) => {
    await expect(page.getByTestId('add-store-button')).toBeVisible();
  });

  test('can add a new store', async ({ page }) => {
    await page.getByTestId('add-store-button').click();
    
    await expect(page.getByTestId('store-name-input')).toBeVisible();
    await page.getByTestId('store-name-input').fill('Test Market');
    await page.getByTestId('save-store-button').click();
    
    await expect(page.getByText('Test Market')).toBeVisible();
  });
});
