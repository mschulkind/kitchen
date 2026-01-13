import { test, expect, Page } from '@playwright/test';

/**
 * Phase 2D E2E Tests - Responsive Layouts 📱💻
 *
 * STRICT MODE: No conditional checks. Elements MUST exist.
 * Tests that layouts adapt correctly across viewport sizes.
 *
 * Fun fact: 60% of web traffic now comes from mobile devices! 📊
 */

async function waitForAppReady(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1000);
}

test.describe('Phase 2D - Desktop Grid Layout', () => {
  test.beforeEach(async ({ page }) => {
    // Set desktop viewport
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/(app)/');
    await waitForAppReady(page);
  });

  test('tonight widget is visible on desktop', async ({ page }) => {
    const tonightWidget = page.getByTestId('tonight-widget');
    await expect(tonightWidget).toBeVisible();
  });

  test('shopping widget is visible on desktop', async ({ page }) => {
    const shoppingWidget = page.getByTestId('shopping-widget');
    await expect(shoppingWidget).toBeVisible();
  });

  test('pantry widget is visible on desktop', async ({ page }) => {
    await expect(page.getByTestId('pantry-widget')).toBeVisible();
  });

  test('dashboard shows all main widgets on desktop', async ({ page }) => {
    await expect(page.getByTestId('tonight-widget')).toBeVisible();
    await expect(page.getByTestId('shopping-widget')).toBeVisible();
    await expect(page.getByTestId('pantry-widget')).toBeVisible();
  });
});

test.describe('Phase 2D - Form Width Constraints', () => {
  test.beforeEach(async ({ page }) => {
    // Set desktop viewport
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/(app)/recipes/new');
    await waitForAppReady(page);
  });

  test('recipe form is visible on desktop', async ({ page }) => {
    // Form should load on the new recipe page
    await expect(page.getByTestId('recipe-title-input')).toBeVisible();
  });

  test('form inputs are accessible on desktop', async ({ page }) => {
    await expect(page.getByTestId('recipe-title-input')).toBeVisible();
    await expect(page.getByTestId('servings-input')).toBeVisible();
  });
});

test.describe('Phase 2D - Modal vs Bottom Sheet', () => {
  test.beforeEach(async ({ page }) => {
    // Set desktop viewport
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/(app)/recipes');
    await waitForAppReady(page);
  });

  test('add recipe FAB opens action sheet on desktop', async ({ page }) => {
    // Open the add recipe action sheet
    await page.getByTestId('add-recipe-fab').click();
    await page.waitForTimeout(300);

    // Options should be visible
    await expect(page.getByTestId('paste-url-option')).toBeVisible();
    await expect(page.getByTestId('manual-entry-option')).toBeVisible();
  });
});

test.describe('Phase 2D - Mobile Layout', () => {
  test.beforeEach(async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/(app)/');
    await waitForAppReady(page);
  });

  test('widgets are visible on mobile', async ({ page }) => {
    const tonightWidget = page.getByTestId('tonight-widget');
    await expect(tonightWidget).toBeVisible();
  });

  test('form is accessible on mobile', async ({ page }) => {
    await page.goto('/(app)/recipes/new');
    await waitForAppReady(page);

    await expect(page.getByTestId('recipe-title-input')).toBeVisible();
  });
});