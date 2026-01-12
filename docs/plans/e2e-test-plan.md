# End-to-End (E2E) Test Plan & Status 🧪

> 🧭 **Navigation**: [Redesign Plan](frontend-redesign.md) | [Implementation Tasks](frontend-tasks.md) | [Central Plan](central-plan.md) | [Planning Index](index.md)

**Goal**: Achieve 100% "Strict Mode" coverage for all core user flows.
**Strict Mode Definition**: Tests must use explicit assertions (`expect().toBeVisible()`) and specific Data-TestIDs (`getByTestId()`). No permissive logical checks (`if (exists)`) allowed.

## 1. Test Suite Status Overview

| Suite | Phase | Status | Strict? | Mocks Needed | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `phase1-inventory.spec.ts` | 1. Foundation | 🟡 Refactor | No | DB | High |
| `phase2-recipes.spec.ts` | 2. Recipes | ✅ Ready | Yes | DB, LLM (Import) | High |
| `phase2d-responsive.spec.ts` | 2D. Responsive | 🔴 Missing | Yes | - | Medium |
| `phase3-delta.spec.ts` | 3. Delta | 🟡 Refactor | No | DB | High |
| `phase4-vision.spec.ts` | 4. Vision | 🟡 Refactor | No | Vision API | Medium |
| `phase5-planner.spec.ts` | 5. Planner | ✅ Ready | Yes | LLM (Generate) | High |
| `phase6-refiner.spec.ts` | 6. Refiner | 🔴 Missing | N/A | Refiner API | Medium |
| `phase7-shopping.spec.ts` | 7. Shopping | 🟡 Expand | Yes | Realtime Sync | High |
| `phase8-store.spec.ts` | 8. Store | ⚪ Pending | - | Scraper API | Low |
| `phase9-voice.spec.ts` | 9. Voice | ⚪ Pending | - | Webhook | Low |
| `phase10-cooking.spec.ts` | 10. Cooking | ⚪ Pending | - | - | Low |

---

## 2. Detailed Work Plan

### `phase1-inventory.spec.ts` (Inventory CRUD)

**Current Issue**: Uses permissive helpers (`if (element.count() > 0)`). Fails to explicitly assert specific field names.

**Required Actions**:

- [ ] Remove all `if` checks.
- [ ] Replace text locators with `getByTestId()`.
- [ ] **TestID Mapping**:
  - Add Item Button -> `add-item-fab`
  - Name Input -> `item-name-input`
  - Quantity Input -> `item-qty-input`
  - Unit Picker -> `item-unit-picker`
  - Save Button -> `save-item-button`
- [ ] **Flows to Verify**:
  - Add item manually.
  - Edit existing item (change qty).
  - Delete item (swipe or long press).
  - Filter list by category.

### `phase2d-responsive.spec.ts` (Responsive Layouts)

**Goal**: Verify app adapts correctly to Mobile (375x667) and Desktop (1280x720) viewports.

**Required Actions**:

- [ ] **Desktop Hub Grid**:
  - Set viewport to 1280x720.
  - Assert `tonight-widget` and `shopping-widget` are side-by-side (or grid flow) rather than stacked vertically.
  - Assert `module-grid` uses 3-4 columns instead of 2.
- [ ] **Navigation Adaptation**:
  - **Mobile**: Assert Hamburger/Back gestures work.
  - **Desktop**: Assert Sidebar/TopNav is visible (if implemented) or layout is centered.
- [ ] **Form Constraints**:
  - Navigate to `/recipes/new`.
  - Assert `recipe-form-container` width is <= 800px even on 1280px screen (check computed style or bounding box).
- [ ] **Modals vs Dialogs**:
  - Trigger "Add Recipe" action.
  - **Mobile**: Assert Sheet covers bottom/full width.
  - **Desktop**: Assert Dialog is centered with overlay.

### `phase2-recipes.spec.ts` (Recipe Engine)

**Status**: Good.

**Required Actions**:

- [ ] Ensure `Import URL` test mocks the backend response to avoid hitting external sites (flaky).
- [ ] Verify `Cooking Mode` wake lock behavior (mock `expo-keep-awake`).

### `phase3-delta.spec.ts` (Delta / Stock Check)

**Current Issue**: Permissive logic for "Stock Check" button.

**Required Actions**:

- [ ] **Standardize UI**: Enforce that the "Check Stock" button always exists on Recipe Detail (TestID: `check-stock-button`).
- [ ] **Strict Flows**:
  - Open Stock Check Modal.
  - Assert "Missing" section contains elements `missing-item-{id}`.
  - Assert "Have" section contains elements `have-item-{id}`.
  - Click "Missing" item -> Assert it moves to "Have".

### `phase4-vision.spec.ts` (Visual Pantry)

**Current Issue**: Checks for *any* camera UI (video, file input).

**Required Actions**:

- [ ] **Mock Vision API**: Use `page.route` to intercept `/api/vision/analyze` and return a fixed JSON: `[{"name": "Banana", "qty": 5}]`.
- [ ] **Strict Flows**:
  - Click `scan-fab`.
  - Upload/Snap image (mock input).
  - Assert `staging-list` appears.
  - Edit candidate quantity.
  - Click `confirm-vision-items`.
  - Assert redirection to Inventory list.

### `phase5-planner.spec.ts` (Planner Core)

**Status**: Good.

**Required Actions**:

- [ ] **Mock Generator**: Intercept `/api/planner/generate` to return 3 fixed themes.
- [ ] Ensure "Constraints" chip selection is tested thoroughly.

### `phase6-refiner.spec.ts` (Slot Machine)

**Status**: Missing / Stub.

**Required Actions**:

- [ ] Create file.
- [ ] **Mock Refiner**: Intercept `/api/planner/refine` to return a swapped recipe.
- [ ] **Flows**:
  - Navigate to Planner.
  - Click `lock-button` on Main Dish (Day 1).
  - Click `spin-button` on Side Dish (Day 1).
  - Assert Side Dish changes, Main Dish stays.

### `phase7-shopping.spec.ts` (Shopping List)

**Status**: Strict but minimal.

**Required Actions**:

- [ ] **Expand Coverage**:
  - **Aisle Headers**: Assert existence of `header-produce` or `header-aisle-1`.
  - **Sync Mocking**: Simulate a second user by programmatically injecting a Supabase event (if possible) or just verify client-side optimistic UI updates.
  - **Clear Completed**: Add items, check them, click `clear-completed-button`, assert list is empty.

## 3. Implementation Guide for "Strict Mode"

1.  **Identify the Element**: Look at the Figma/Design spec.
2.  **Tag the Component**: Go to the source code (`src/mobile/app/...`) and add `testID="my-element-name"`.
3.  **Write the Test**:
    ```typescript
    // BAD
    const btn = page.getByText('Save');
    if (await btn.isVisible()) await btn.click();

    // GOOD
    await page.getByTestId('save-button').click();
    ```
4.  **Run & Refine**: `npx playwright test phaseX-name.spec.ts`.
