import { test, expect, Page } from '@playwright/test';

/**
 * Phase 7C E2E Tests - Shopping List 🛒
 *
 * STRICT MODE: No conditional checks. Elements MUST exist.
 * Tests the shopping list functionality.
 *
 * Fun fact: The average grocery trip takes 41 minutes! ⏱️
 */

async function waitForAppReady(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1000);
}

test.describe('Phase 7C - Shopping List View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/shopping');
    await waitForAppReady(page);
  });

  test('shopping page loads with title', async ({ page }) => {
    await expect(page.getByText('Shopping List')).toBeVisible();
  });

  test('quick add input is visible', async ({ page }) => {
    const input = page.getByTestId('quick-add-input');
    await expect(input).toBeVisible();
  });

  test('add button is visible', async ({ page }) => {
    await expect(page.getByTestId('add-item-button')).toBeVisible();
  });

  test('category sections are visible or empty state', async ({ page }) => {
    // Either we have grouped items or empty state
    const produceSection = page.getByTestId('category-produce');
    const emptyState = page.getByText('Your list is empty');
    
    const hasContent = await produceSection.count() > 0 || await emptyState.count() > 0;
    expect(hasContent).toBe(true);
  });

  test('summary footer shows counts', async ({ page }) => {
    await expect(page.getByTestId('shopping-summary')).toBeVisible();
  });
});

test.describe('Phase 7C - Add Items', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/shopping');
    await waitForAppReady(page);
  });

  test('can type in quick add input', async ({ page }) => {
    const input = page.getByTestId('quick-add-input');
    await input.fill('Milk');
    await expect(input).toHaveValue('Milk');
  });

  test('can add item with button', async ({ page }) => {
    const input = page.getByTestId('quick-add-input');
    await input.fill('Test Bread');
    await page.getByTestId('add-item-button').click();
    
    await expect(page.getByText('Test Bread')).toBeVisible();
  });

  test('input clears after adding', async ({ page }) => {
    const input = page.getByTestId('quick-add-input');
    await input.fill('Test Eggs');
    await page.getByTestId('add-item-button').click();
    
    await expect(input).toHaveValue('');
  });
});

test.describe('Phase 7C - Check/Uncheck Items', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/shopping');
    await waitForAppReady(page);
    
    // Add an item first
    const input = page.getByTestId('quick-add-input');
    await input.fill('Test Butter');
    await page.getByTestId('add-item-button').click();
  });

  test('unchecked item has checkbox', async ({ page }) => {
    const checkbox = page.getByTestId('check-Test Butter');
    await expect(checkbox).toBeVisible();
  });

  test('can check item', async ({ page }) => {
    await page.getByTestId('check-Test Butter').click();
    
    // Item should move to completed section
    await expect(page.getByTestId('completed-section')).toContainText('Test Butter');
  });

  test('can uncheck item', async ({ page }) => {
    // First check it
    await page.getByTestId('check-Test Butter').click();
    // Then uncheck
    await page.getByTestId('uncheck-Test Butter').click();
    
    // Item should be back in unchecked
    const checkbox = page.getByTestId('check-Test Butter');
    await expect(checkbox).toBeVisible();
  });
});

test.describe('Phase 7C - Clear Completed', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/shopping');
    await waitForAppReady(page);
    
    // Add and check an item
    await page.getByTestId('quick-add-input').fill('Test Cheese');
    await page.getByTestId('add-item-button').click();
    await page.getByTestId('check-Test Cheese').click();
  });

  test('clear completed button is visible when items checked', async ({ page }) => {
    await expect(page.getByTestId('clear-completed-button')).toBeVisible();
  });

  test('can clear completed items', async ({ page }) => {
    await page.getByTestId('clear-completed-button').click();
    
    // Item should be gone
    await expect(page.getByText('Test Cheese')).not.toBeVisible();
  });
});

test.describe('Phase 7C - Category Grouping', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/shopping');
    await waitForAppReady(page);
  });

  test('items are grouped by category', async ({ page }) => {
    // Add items from different categories
    await page.getByTestId('quick-add-input').fill('Apples');
    await page.getByTestId('add-item-button').click();
    
    await page.getByTestId('quick-add-input').fill('Chicken');
    await page.getByTestId('add-item-button').click();
    
    // Should see category headers
    await expect(page.getByTestId('category-produce')).toBeVisible();
    await expect(page.getByTestId('category-meat')).toBeVisible();
  });
});
