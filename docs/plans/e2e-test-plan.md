# End-to-End (E2E) Test Plan & Status 🧪

> 🧭 **Navigation**: [Redesign Plan](frontend-redesign.md) | [Implementation Tasks](frontend-tasks.md) | [Central Plan](central-plan.md) | [Planning Index](index.md)

**Goal**: Achieve 100% "Strict Mode" coverage for all core user flows.
**Strict Mode Definition**: Tests must use explicit assertions (`expect().toBeVisible()`) and specific Data-TestIDs (`getByTestId()`). No permissive logical checks (`if (exists)`) allowed.

## 1. Test Suite Status Overview

| Suite | Phase | Status | Strict? | Mocks Needed | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `phase1-inventory.spec.ts` | 1. Foundation | ✅ Ready | Yes | DB | High |
| `phase2-recipes.spec.ts` | 2. Recipes | ✅ Ready | Yes | DB, LLM (Import) | High |
| `phase2d-responsive.spec.ts` | 2D. Responsive | 🔴 Missing | Yes | - | Medium |
| `phase3-delta.spec.ts` | 3. Delta | 🚧 Skipped | Yes | DB (Seed Data) | High |
| `phase4-vision.spec.ts` | 4. Vision | ✅ Ready | Yes | Vision API | Medium |
| `phase5-planner.spec.ts` | 5. Planner | ✅ Ready | Yes | LLM (Generate) | High |
| `phase6-refiner.spec.ts` | 6. Refiner | 🔴 Missing | Yes | Refiner API | Medium |
| `phase7-shopping.spec.ts` | 7. Shopping | 🚧 Skipped | Yes | Realtime Sync | High |
| `phase8-store.spec.ts` | 8. Store | ⚪ Pending | - | Scraper API | Low |
| `phase9-voice.spec.ts` | 9. Voice | ⚪ Pending | - | Webhook | Low |
| `phase10-cooking.spec.ts` | 10. Cooking | ⚪ Pending | - | - | Low |

---

## 2. Detailed Work Plan

### `phase1-inventory.spec.ts` (Inventory CRUD)

**Status**: Mostly Complete. One skipped test.

**Tasks**:
- [ ] **Unskip Save Test**: Enable the `can fill and save item form` test.
  - *Requirement*: Ensure `testID="save-item-button"` works and database mutation succeeds in CI environment.
- [ ] **Verify Filter Logic**: Add specific assertion that filtering by 'Fridge' hides 'Pantry' items.

### `phase2d-responsive.spec.ts` (Responsive Layouts)

**Status**: Missing.

**Tasks**:
- [ ] **Create File**: `tests/web/e2e/phase2d-responsive.spec.ts`.
- [ ] **Implement Desktop Grid Test**:
  - Set viewport to `1280x720`.
  - Assert `tonight-widget` and `shopping-widget` are displayed horizontally (check bounding boxes).
- [ ] **Implement Form Constraint Test**:
  - Navigate to `/recipes/new` on Desktop.
  - Assert form container width is `< 800px`.
- [ ] **Implement Modal Test**:
  - Trigger "Add Recipe".
  - Assert it renders as a centered Dialog (not a bottom sheet) on Desktop.

### `phase2-recipes.spec.ts` (Recipe Engine)

**Status**: Complete.

**Tasks**:
- [ ] **Mock Import Scraper**: Currently hits real URL. Add `page.route('**/api/v1/recipes/scrape', ...)` to return mock data (Title: "Mock Chicken", Ingredients: ["Chicken"]).

### `phase3-delta.spec.ts` (Delta / Stock Check)

**Status**: All tests skipped due to missing data.

**Tasks**:
- [ ] **Create Seed Recipe**: In `test.beforeAll`, programmatically insert a recipe with ID `test-recipe-id` and known ingredients (Mock Ingredient A, Mock Ingredient B).
- [ ] **Unskip All Tests**: Remove `.skip` from `test.describe`.
- [ ] **Verify "Missing" to "Have"**: Tap "I have this" on Mock Ingredient A and assert it moves to the "Have" section.

### `phase4-vision.spec.ts` (Visual Pantry)

**Status**: Complete.

**Tasks**:
- [ ] **Verify Integration**: Ensure that clicking "Confirm All" actually adds items to the Inventory list (navigate to `/inventory` and check for item existence).

### `phase5-planner.spec.ts` (Planner Core)

**Status**: Complete.

**Tasks**:
- [ ] **No pending tasks**. Suite is green.

### `phase6-refiner.spec.ts` (Slot Machine)

**Status**: Missing.

**Tasks**:
- [ ] **Create File**: `tests/web/e2e/phase6-refiner.spec.ts`.
- [ ] **Implement Lock Test**:
  - Click lock icon on a slot.
  - Assert lock icon changes state/color.
- [ ] **Implement Spin Test**:
  - Click refresh/spin icon.
  - Assert slot content changes (requires mocking the Refiner API response).

### `phase7-shopping.spec.ts` (Shopping List)

**Status**: Most tests skipped.

**Tasks**:
- [ ] **Database Cleanup**: Add `test.afterEach` to clear shopping list items to ensure clean state.
- [ ] **Unskip "Add Items"**: Enable text input and button press tests.
- [ ] **Unskip "Check/Uncheck"**: Enable toggle tests.
- [ ] **Unskip "Clear Completed"**: Enable clear button tests.
- [ ] **Verify Grouping**: Assert "Apples" appears under "Produce" header (requires Mock API or correct category logic).

## 3. Implementation Guide for "Strict Mode"

1.  **Identify the Element**: Look at the Figma/Design spec.
2.  **Tag the Component**: Go to the source code (`src/mobile/app/...`) and add `testID="my-element-name"`.
3.  **Write the Test**:
    ```typescript
    await page.getByTestId('save-button').click();
    await expect(page.getByTestId('success-message')).toBeVisible();
    ```
4.  **Run & Refine**: `npx playwright test phaseX-name`.
