import { test, expect, Page } from '@playwright/test';

/**
 * Phase 5C E2E Tests - Planner (Generate Plan) 🎲
 *
 * Tests the meal plan generation flow as specified in phase-05-planner-core.md
 *
 * STRICT MODE: No conditional checks. Elements MUST exist.
 */

async function waitForAppReady(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1000);
}

test.describe('Phase 5C - Generate Plan Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/planner');
    await waitForAppReady(page);
  });

  test('planner page loads with correct title', async ({ page }) => {
    await expect(page.getByText('Meal Planner')).toBeVisible();
  });

  test('can find New Plan button', async ({ page }) => {
    const newPlanButton = page.getByTestId('new-plan-button');
    await expect(newPlanButton).toBeVisible();
  });

  test('New Plan opens configuration form', async ({ page }) => {
    await page.getByTestId('new-plan-button').click();
    await expect(page.getByText('Create New Plan')).toBeVisible();
    await expect(page.getByText('Days')).toBeVisible();
  });

  test('can configure number of days', async ({ page }) => {
    await page.getByTestId('new-plan-button').click();
    
    const daysInput = page.getByPlaceholder('Days to plan (e.g. 3)');
    await expect(daysInput).toBeVisible();
    await daysInput.fill('3');
    await expect(daysInput).toHaveValue('3');
  });

  test('can set dietary constraints', async ({ page }) => {
    await page.getByTestId('new-plan-button').click();
    
    // Constraints section should be visible
    await expect(page.getByText('Constraints')).toBeVisible();
    
    // Toggle a constraint
    const vegetarianToggle = page.getByLabel('Vegetarian');
    await expect(vegetarianToggle).toBeVisible();
  });

  test('generate button triggers loading state', async ({ page }) => {
    await page.getByTestId('new-plan-button').click();
    await page.getByPlaceholder('Days to plan (e.g. 3)').fill('3');
    
    const generateBtn = page.getByText('Generate Plan');
    await generateBtn.click();
    
    await expect(page.getByText('Chewing on data...')).toBeVisible();
  });
});
