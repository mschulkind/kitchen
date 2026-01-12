# Frontend Redesign & Implementation Plan 🎨

> 🧭 **Navigation**: [Central Plan](central-plan.md) | [Implementation Tasks](frontend-tasks.md) | [E2E Test Plan](e2e-test-plan.md) | [Planning Index](index.md)

## Executive Summary

This document outlines the comprehensive redesign of the Kitchen mobile application (`src/mobile`), moving away from the "dated" bottom-tab architecture to a modern, gesture-friendly **Hub & Spoke** model. It aligns with the **Mobile-First Principles** defined in `AGENTS.md`.

## 1. Navigation Architecture: "The Hub"

Instead of persistent bottom tabs, we will use a **Dashboard Hub** pattern. This is more immersive and scalable for the "Kitchen" context where distinct modes (Cooking vs. Planning vs. Shopping) are often exclusive focus areas.

### Structure

- **Root**: Native Stack Navigator (`src/mobile/app/_layout.tsx`)
  - **Auth**: Unauthenticated Landing Stack (`src/mobile/app/(auth)`)
  - **App**: Authenticated Hub Stack (`src/mobile/app/(app)`)

### Navigation Flow

- **Home (The Hub)**: A dashboard with dynamic widgets and big entry buttons to key modules.
- **Modules** (Pushed on Stack):
  - `Inventory`: The Pantry list.
  - `Recipes`: The cookbook.
  - `Planner`: Calendar and suggestions.
  - `Shopping`: Smart shopping list.
- **Return**: Standard edge-swipe back or top-left "Home" button.

## 2. Screens & UI Design

### 2.1. Unauthenticated Landing Page (`/landing`)

- **Goal**: Welcome users and prompt login.
- **UI Components**:
  - **Hero**: App Icon + "Kitchen" text.
  - **Value Props**: 3-item carousel (e.g., "Plan with AI", "Shop Smart", "Cook with Ease").
  - **Actions**:
    - Primary: "Sign In" (Opens Supabase Auth Sheet).
    - Secondary: "Create Account".
- **Tech**: `Link` to auth routes, check session on mount.

### 2.2. The Hub (`/index`)

- **Goal**: At-a-glance status and navigation.
- **Widgets (Realtime)**:
  - **"Tonight"**: What's for dinner? (Reads `meal_plans` for today).
  - **"Shopping"**: x items to buy (Count of unchecked items in `shopping_list`).
  - **"Pantry"**: x items expiring (Query `pantry_items` with filter).
- **Grid**: Large, touch-friendly cards for modules.

### 2.3. Recipe Engine (`/recipes/*`)

- **List (`/recipes/index`)**:
  - **Search**: Debounced input for title/ingredients.
  - **FAB**: "Add Recipe" Action Sheet with options:
    - **Paste URL**: Opens a Dialog to paste a recipe URL (Triggers Scraper).
    - **Manual Entry**: Navigates to `/recipes/new`.
    - **Scan**: (Future) Camera OCR.
  - **List Item**: Card with image, title, "cook time", and "last cooked" date.
- **Manual Entry (`/recipes/new`)**:
  - **Form**: Title, Servings, Prep/Cook time.
  - **Arrays**: Dynamic lists for Ingredients and Steps (add/remove/reorder).
  - **Validation**: Basic required fields.
- **Detail (`/recipes/[id]`)**:
  - **Header**: Parallax image.
  - **Actions**: "Start Cooking" (Sticky FAB), "Check Stock" (Secondary), Edit, Delete.
  - **Content**:
    - Ingredients list (toggle metric/imperial).
    - Step-by-step preview.
- **Stock Check (`/recipes/[id]/check-stock`)** (Phase 3):
  - **Goal**: Confirm ingredients before cooking.
  - **UI**: Three sections - "You Have (Enough)", "You Have (Not Enough)", "Missing".
  - **Interaction**: Tap "Missing" item -> Moves to "You Have" (Lazy Discovery).
- **Cooking Mode (`/recipes/[id]/cook`)**:
  - **Focus Mode**: Full screen, status bar hidden.
  - **Wake Lock**: `expo-keep-awake` active.
  - **UI**: Large text step-by-step carousel.
  - **Controls**: Huge "Next" / "Back" tap zones.

### 2.4. Planner Module (`/planner/*`)

- **Calendar (`/planner/index`)**:
  - **Grid**: 4-day view or Week view.
  - **Slot Card**: Main + Side dish slots.
  - **Actions**: Lock icon (prevent reroll), Spin icon (Phase 6 Reroll).
  - **FAB**: "New Plan".
- **Generator (`/planner/new`)** (Phase 5):
  - **Form**: Days to plan (slider), Constraints (Chip selections e.g. "Vegetarian").
  - **Output**: Navigate to preview/selection screen with 3 "Adventure" themes.

### 2.5. Inventory & Vision (`/inventory/*`)

- **List (`/inventory/index`)**:
  - **Filter/Sort**: By Expiry, by Name, by Category.
  - **FAB**: "Scan Item" or "Manually Add".
- **Vision Staging (`/inventory/scan-result`)** (Phase 4):
  - **Goal**: Verify AI detection before committing.
  - **UI**: List of "Candidates" (Name, Qty, Unit) with editable fields.
  - **Action**: "Confirm All" (Commits to DB).

### 2.6. Shopping (`/shopping`)

- **List**:
  - **Grouped**: By Aisle (Phase 8) or Category (default).
  - **Sort**: Smart sort based on store layout.
  - **Interaction**: Swipe to delete, Tap to check (moves to bottom).
  - **Voice**: Microphone icon to "Quick Add" (Phase 9).

## 3. Technical Architecture

### 3.1. Routing (Expo Router)

Moving from `(tabs)` to a clean stack layout.

```typescript
// src/mobile/app/_layout.tsx -> Root Provider (QueryClient, AuthProvider)
// src/mobile/app/(app)/_layout.tsx -> Stack Navigator (Protected)
// src/mobile/app/(auth)/_layout.tsx -> Stack Navigator (Public)
```

### 3.2. Data & Sync Strategy (TanStack Query + Supabase)

As per `AGENTS.md`, we prioritize **Realtime** and **Offline** capabilities.

- **Fetching**: Standard `useQuery` for fetching lists/details.
- **Realtime**: `useEffect` hooks subscribe to Supabase channels (e.g., `recipes`, `shopping_list`).
  - On event (`INSERT`, `UPDATE`, `DELETE`), invalidate relevant Query Keys.
- **Mutations**: Optimistic updates where possible.

### 3.3. Component Library (Tamagui)

We will expand `src/mobile/components` with tailored UI elements:

- **`Core/Button.tsx`**: Wrapper around Tamagui Button, enforcing `minHeight: 44` (Touch Target).
- **`Core/Input.tsx`**: Standardized text input.
- **`Layout/Screen.tsx`**: Wrapper with `SafeAreaView`.
- **`Modules/HubCard.tsx`**: Dashboard entry points.
- **`Modules/RecipeCard.tsx`**: List item display.
- **`Modules/CookingStep.tsx`**: Large text view.

## 4. E2E Test Strategy 🧪

We use **Playwright** for End-to-End testing. The goal is to verify the "User Journey" rather than individual implementation details.

### 4.1. "Strict Mode" Philosophy

We are moving away from "Permissive Tests" (which check `if (exists) click`) to **"Strict Tests"** (which assert `expect(exists).toBeVisible()`).

- **Permissive**: Good for prototyping. Checks if the app *crashes*.
- **Strict**: Good for production. Checks if the app *functions correctly*.

**Rules for Writing Tests:**

1. **No Conditionals**: Tests should not contain `if/else` logic based on UI state. If a button isn't where it should be, the test **MUST FAIL**.
2. **Explicit Assertions**: Use `await expect(locator).toBeVisible()` or `await expect(locator).toHaveText()` for every verified step.
3. **Data-TestIDs**: Do not select by class names or obscure layout hierarchies. Add `testID="my-element"` props to Tamagui components (renders as `data-testid` on web) and select via `page.getByTestId('my-element')`.
   - *Bad*: `page.locator('div > div > button')`
   - *Good*: `page.getByTestId('add-recipe-fab')`
4. **Mobile Viewport**: All tests should run with a mobile viewport configuration (e.g., iPhone 13 Pro) since we are Mobile-First.

### 4.2. Mocking vs. Real Backend

- **Happy Path (Critical Flows)**: Should run against a **Real Backend** (local Docker stack) whenever possible to verify the full integration (App -> API -> DB).
  - *Example*: Creating a recipe and seeing it appear in the list.
- **Edge Cases / flaky External APIs**: Use **Network Mocking** (`page.route()`) for:
  - LLM Responses (Vision, Planner Generator) to save cost and time.
  - Third-party Scraper failures.
  - Error states (e.g., "500 Server Error").

### 4.3. Test Coverage Matrix

| Test File | Critical Flows | Mocking Strategy | Status |
| :--- | :--- | :--- | :--- |
| `phase1-inventory.spec.ts` | List load, Add Item, Delete Item, Filter | Real DB | 🟡 Needs Strict |
| `phase2-recipes.spec.ts` | Import URL, Manual Entry, Search, Detail | Real DB + Mock LLM | ✅ Ready |
| `phase3-delta.spec.ts` | Stock Check UI, "Missing" -> "Have" move | Real DB | 🟡 Needs Strict |
| `phase4-vision.spec.ts` | Camera Open, Staging List Edit, Commit | **Mock Vision API Response** | 🟡 Needs Strict |
| `phase5-planner.spec.ts` | New Plan Form, Option Selection, Calendar Grid | **Mock Planner LLM Response** | ✅ Ready |
| `phase6-refiner.spec.ts` | Lock Slot, Spin Slot (Reroll) | Real DB + Mock Refiner | 🔴 Missing |
| `phase7-shopping.spec.ts` | Item Check, Clear Completed, Smart Sort | Real DB (Realtime Sync implied) | 🟡 Needs Strict |

### 4.4. Example: Strict Test Pattern

```typescript
test('can add a recipe manually', async ({ page }) => {
  // 1. Arrange: Go to screen
  await page.goto('/recipes');
  
  // 2. Act: Open form
  await page.getByTestId('add-recipe-fab').click();
  await page.getByTestId('manual-entry-option').click();
  
  // 3. Act: Fill form
  await page.getByTestId('recipe-title-input').fill('Test Tacos');
  await page.getByTestId('save-recipe-button').click();
  
  // 4. Assert: Redirected and item exists
  await expect(page).toHaveURL('/recipes');
  await expect(page.getByTestId('recipe-card-test-tacos')).toBeVisible(); 
});
```
