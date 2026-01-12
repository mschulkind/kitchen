import { test, expect, Page } from '@playwright/test';

/**
 * Phase 2C E2E Tests - Recipe Management 📖
 *
 * Tests the recipe CRUD flows as specified in phase-02-recipe-engine.md
 *
 * STRICT MODE: No conditional checks. Elements MUST exist.
 * 
 * Fun fact: The average cookbook contains about 150 recipes! 📚
 */

async function waitForAppReady(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1000);
}

test.describe('Phase 2C - Recipe List', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/recipes');
    await waitForAppReady(page);
  });

  test('recipes page loads with correct title', async ({ page }) => {
    await expect(page.getByText('Recipes')).toBeVisible();
  });

  test('search input is visible', async ({ page }) => {
    const searchInput = page.getByTestId('recipe-search-input');
    await expect(searchInput).toBeVisible();
  });

  test('can search for recipes', async ({ page }) => {
    const searchInput = page.getByTestId('recipe-search-input');
    await searchInput.fill('Chicken');
    await expect(searchInput).toHaveValue('Chicken');
  });

  test('add recipe FAB is visible', async ({ page }) => {
    const fab = page.getByTestId('add-recipe-fab');
    await expect(fab).toBeVisible();
  });

  test('FAB opens action sheet', async ({ page }) => {
    await page.getByTestId('add-recipe-fab').click();
    await expect(page.getByText('Add Recipe')).toBeVisible();
    await expect(page.getByTestId('paste-url-option')).toBeVisible();
    await expect(page.getByTestId('manual-entry-option')).toBeVisible();
  });
});

test.describe('Phase 2C - Import Recipe Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/recipes');
    await waitForAppReady(page);
  });

  test('import button opens URL dialog', async ({ page }) => {
    await page.getByTestId('import-recipe-fab').click();
    await expect(page.getByTestId('recipe-url-input')).toBeVisible();
  });

  test('can enter URL and submit', async ({ page }) => {
    await page.getByTestId('import-recipe-fab').click();
    
    const urlInput = page.getByTestId('recipe-url-input');
    await urlInput.fill('https://www.seriouseats.com/easy-roasted-chicken-recipe');
    
    await page.getByText('Import').click();
    
    await expect(page.getByText('Parsing recipe...')).toBeVisible();
  });
});

test.describe('Phase 2C - Manual Recipe Entry', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/recipes/new');
    await waitForAppReady(page);
  });

  test('new recipe form loads', async ({ page }) => {
    await expect(page.getByTestId('recipe-title-input')).toBeVisible();
  });

  test('form has all required sections', async ({ page }) => {
    await expect(page.getByTestId('recipe-title-input')).toBeVisible();
    await expect(page.getByTestId('servings-input')).toBeVisible();
    await expect(page.getByTestId('prep-time-input')).toBeVisible();
    await expect(page.getByTestId('cook-time-input')).toBeVisible();
    await expect(page.getByTestId('ingredients-header')).toBeVisible();
    await expect(page.getByTestId('instructions-header')).toBeVisible();
  });

  test('can add ingredient row', async ({ page }) => {
    await page.getByTestId('add-ingredient-button').click();
    await expect(page.getByTestId('ingredient-row-1')).toBeVisible();
  });

  test('can add step row', async ({ page }) => {
    await page.getByTestId('add-step-button').click();
    await expect(page.getByTestId('step-row-1')).toBeVisible();
  });

  test('can fill and save recipe', async ({ page }) => {
    await page.getByTestId('recipe-title-input').fill('Test Tacos');
    await page.getByTestId('servings-input').fill('4');
    await page.getByTestId('ingredient-name-0').fill('Ground Beef');
    await page.getByTestId('ingredient-qty-0').fill('1');
    await page.getByTestId('ingredient-unit-0').fill('lb');
    await page.getByTestId('step-instruction-0').fill('Brown the beef');
    
    await page.getByTestId('save-recipe-button').click();
  });
});

test.describe('Phase 2C - Recipe Detail', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to a specific recipe (assumes test data exists)
    await page.goto('/(app)/recipes/test-recipe-id');
    await waitForAppReady(page);
  });

  test('recipe detail shows title', async ({ page }) => {
    await expect(page.getByTestId('recipe-title')).toBeVisible();
  });

  test('ingredients section is visible', async ({ page }) => {
    await expect(page.getByTestId('ingredients-section')).toBeVisible();
  });

  test('instructions section is visible', async ({ page }) => {
    await expect(page.getByTestId('instructions-section')).toBeVisible();
  });

  test('check stock button is visible', async ({ page }) => {
    await expect(page.getByTestId('check-stock-button')).toBeVisible();
  });

  test('start cooking FAB is visible', async ({ page }) => {
    await expect(page.getByTestId('start-cooking-fab')).toBeVisible();
  });
});

test.describe('Phase 2C - Cooking Mode', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/recipes/test-recipe-id/cook');
    await waitForAppReady(page);
  });

  test('cooking mode shows step content', async ({ page }) => {
    await expect(page.getByTestId('cooking-step-0')).toBeVisible();
  });

  test('navigation controls are visible', async ({ page }) => {
    await expect(page.getByTestId('next-step-button')).toBeVisible();
    await expect(page.getByTestId('prev-step-button')).toBeVisible();
  });

  test('close button is visible', async ({ page }) => {
    await expect(page.getByTestId('close-cooking-button')).toBeVisible();
  });

  test('can navigate to next step', async ({ page }) => {
    await page.getByTestId('next-step-button').click();
    await expect(page.getByTestId('cooking-step-1')).toBeVisible();
  });
});
