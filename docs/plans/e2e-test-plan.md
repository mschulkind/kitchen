# End-to-End (E2E) Test Plan & Status 🧪

> 🧭 **Navigation**: [Redesign Plan](frontend-redesign.md) | [Implementation Tasks](frontend-tasks.md) | [Central Plan](central-plan.md) | [Planning Index](index.md)

**Goal**: Achieve 100% "Strict Mode" coverage for all core user flows.
**Strict Mode Definition**: Tests must use explicit assertions (`expect().toBeVisible()`) and specific Data-TestIDs (`getByTestId()`). No permissive logical checks (`if (exists)`) allowed.

## 1. Test Suite Status Overview

All core suites are now implemented in Strict Mode.

| Suite | Phase | Status | Strict? | Mocks Implemented | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `phase1-inventory.spec.ts` | 1. Foundation | ✅ Ready | Yes | DB | High |
| `phase2-recipes.spec.ts` | 2. Recipes | ✅ Ready | Yes | DB, Scraper | High |
| `phase2d-responsive.spec.ts` | 2D. Responsive | ✅ Ready | Yes | - | Medium |
| `phase3-delta.spec.ts` | 3. Delta | ✅ Ready | Yes | DB, Seed Recipe | High |
| `phase4-vision.spec.ts` | 4. Vision | ✅ Ready | Yes | Vision API | Medium |
| `phase5-planner.spec.ts` | 5. Planner | ✅ Ready | Yes | Generator | High |
| `phase6-refiner.spec.ts` | 6. Refiner | ✅ Ready | Yes | Refiner API | Medium |
| `phase7-shopping.spec.ts` | 7. Shopping | ✅ Ready | Yes | Realtime Sync | High |
| `phase8-store.spec.ts` | 8. Store | 🚧 Skipped | Yes | Scraper API | Low |
| `phase9-voice.spec.ts` | 9. Voice | ✅ Ready | No | Webhook | Low |
| `phase10-cooking.spec.ts` | 10. Cooking | ✅ Ready | Yes | Recipe Mocks | Low |
| `phase11-images.spec.ts` | 11. Imagery | ⚪ Pending | - | - | Low |

---

## 2. Detailed Work Plan

### `phase1-inventory.spec.ts` (Inventory CRUD)

**Status**: Implemented.
**Coverage**: List load, Add Item (Manual/Scan), Edit, Delete, Filter by Location.

### `phase2d-responsive.spec.ts` (Responsive Layouts)

**Status**: Implemented.
**Coverage**: Desktop Grid (Widgets side-by-side), Form Max-Width constraints, Desktop Centered Modals vs Mobile Sheets.

### `phase2-recipes.spec.ts` (Recipe Engine)

**Status**: Implemented.
**Coverage**: Recipe List, Search, Manual Entry, Import URL (Mocked).

### `phase3-delta.spec.ts` (Delta / Stock Check)

**Status**: Implemented.
**Coverage**: Stock Check UI, "Missing" to "Have" transition (Lazy Discovery), Recipe Navigation. Uses `createSeedRecipe` helper.

### `phase4-vision.spec.ts` (Visual Pantry)

**Status**: Implemented.
**Coverage**: Scan Entry, Staging List (Mock Analysis), Edit Candidate, Confirm All (Integration).

### `phase5-planner.spec.ts` (Planner Core)

**Status**: Implemented.
**Coverage**: Calendar Grid, New Plan Generator Form (Days/Constraints), Mock Generation Response.

### `phase6-refiner.spec.ts` (Slot Machine)

**Status**: Implemented.
**Coverage**: Lock/Unlock Slots, Spin/Reroll (Mock API), Bulk Actions.

### `phase7-shopping.spec.ts` (Shopping List)

**Status**: Implemented.
**Coverage**: Quick Add, Check/Uncheck, Clear Completed, Category Grouping. Uses `setupShoppingMocks`.

### `phase8-store.spec.ts` (Store Intelligence)

**Status**: Skipped (Awaiting UI).
**Coverage**: Store selection, Aisle Grouping, Sorting.
**Blocker**: Store selection UI not yet implemented.

### `phase9-voice.spec.ts` (Voice Webhook)

**Status**: Ready (API Tests).
**Coverage**: Webhook parsing (item splitting, quantities), authentication.
**Note**: UI tests for microphone button are obsolete and skipped/removed.

### `phase10-cooking.spec.ts` (Cooking Companion)

**Status**: Implemented.
**Coverage**: Cooking Mode Entry, Step Navigation, Features (Timer, Ingredients), Exit Flow. Uses `setupCookingMocks`.

### `phase11-images.spec.ts` (Recipe Imagery)

**Status**: Pending.
**Coverage**: Generate Image Button, Loading State, Image Display.
**Blocker**: API implementation.

## 3. Implementation Guide for "Strict Mode"

1.  **Identify the Element**: Look at the Figma/Design spec.
2.  **Tag the Component**: Go to the source code (`src/mobile/app/...`) and add `testID="my-element-name"`.
3.  **Write the Test**:
    ```typescript
    await page.getByTestId('save-button').click();
    await expect(page.getByTestId('success-message')).toBeVisible();
    ```
4.  **Run & Refine**: `npx playwright test phaseX-name`.
