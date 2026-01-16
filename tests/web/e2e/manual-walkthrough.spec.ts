import { test, expect, Page } from '@playwright/test';

/**
 * Manual Walkthrough E2E Test 🚶
 *
 * This test simulates a user journey through the newly redesigned frontend.
 * It covers:
 * 1. Landing Page (Unauthenticated)
 * 2. Authentication (Mocked)
 * 3. Hub Dashboard (Authenticated)
 * 4. Navigation to Modules
 */

async function waitForAppReady(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1000);
}

test.describe('Frontend Redesign Walkthrough', () => {

  test('User Journey: Landing -> Hub -> Modules', async ({ page }) => {
    
    // --- 1. LANDING PAGE ---
    console.log('Step 1: Verify Landing Page');
    await page.goto('/');
    await waitForAppReady(page);

    // Should redirect to landing
    await expect(page).toHaveURL(/.*\/landing/);
    
    // Verify Hero
    await expect(page.getByTestId('landing-screen')).toBeVisible();
    await expect(page.getByText('Kitchen')).toBeVisible();
    await expect(page.getByText('Your AI-powered sous chef')).toBeVisible();
    
    // Verify Value Props
    await expect(page.getByText('Smart Pantry')).toBeVisible();
    await expect(page.getByText('AI Recipes')).toBeVisible();

    // --- 2. AUTHENTICATION ---
    console.log('Step 2: Enter App');
    // Click Get Started
    await page.getByTestId('get-started-button').click();

    // Should navigate to Hub (/(app)/index)
    // Note: The URL in Expo Router on web might look like /(app) or just /
    // We'll check for the Hub Screen testID
    await expect(page.getByTestId('hub-screen')).toBeVisible();

    // --- 3. HUB DASHBOARD ---
    console.log('Step 3: Verify Hub Dashboard');
    
    // Greeting
    await expect(page.getByTestId('user-greeting')).toBeVisible();
    
    // Widgets
    await expect(page.getByTestId('tonight-widget')).toBeVisible();
    await expect(page.getByTestId('shopping-widget')).toBeVisible();
    await expect(page.getByTestId('pantry-widget')).toBeVisible();
    
    // Navigation Cards
    await expect(page.getByTestId('recipes-card')).toBeVisible();
    await expect(page.getByTestId('pantry-card')).toBeVisible();
    await expect(page.getByTestId('planner-card')).toBeVisible();
    await expect(page.getByTestId('shopping-card')).toBeVisible();

    // --- 4. NAVIGATION TO MODULES ---
    console.log('Step 4: Navigate to Recipes');
    
    // Click Recipes Card
    await page.getByTestId('recipes-card').click();
    
    // Verify Recipe List
    // Use getByRole to target the header specifically, avoiding the "Recipes" text on the Hub card
    await expect(page.getByRole('heading', { name: 'Recipes' })).toBeVisible();
    await expect(page.getByTestId('add-recipe-fab')).toBeVisible();
    
    // Go Back (Simulate Browser Back or Back Button if visible)
    // In Expo Web, we can use page.goBack() or click a back button
    // Let's assume browser back for now or check if there is a back button
    // The recipe list might not have a back button if it's a stack push
    
    // Check if we can navigate back to Hub
    // We'll just verify we are on the recipes page for now
    await expect(page).toHaveURL(/.*\/recipes/);
    
    // Navigate back to Hub
    await page.goto('/(app)');
    await expect(page.getByTestId('hub-screen')).toBeVisible();
    
    console.log('Step 5: Navigate to Pantry');
    await page.getByTestId('pantry-card').click();
    await expect(page).toHaveURL(/.*\/inventory/);
    // Basic verification of pantry - target the header
    await expect(page.getByRole('heading', { name: 'Pantry' })).toBeVisible();
  });
});
