import { test, expect, Page } from '@playwright/test';
const fs = require('fs');

async function waitForAppReady(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000); 
}

test('Take snapshot of inventory page', async ({ page }) => {
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    console.log('Logging in...');
    await page.goto('/devlogin');
    await page.getByLabel('Service Account Email').fill('admin@kitchen.local');
    await page.getByLabel('Password').fill('admin123');
    await page.getByTestId('dev-login-button').click();
    
    await waitForAppReady(page);
    console.log('Navigating to inventory...');
    await page.goto('/(app)/inventory');
    await waitForAppReady(page);
    
    const content = await page.content();
    fs.writeFileSync('inventory_debug.html', content);
    console.log('Snapshot saved to inventory_debug.html');
    
    // Also take a text-based snapshot of the accessibility tree
    // (This is what take_snapshot tool does, but I'll do it manually here to see output in logs)
    const body = await page.evaluate(() => document.body.innerText);
    console.log('BODY TEXT:', body);
});
