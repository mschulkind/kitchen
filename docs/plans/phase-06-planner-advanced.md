# Phase 6: The "Slot Machine" (Refinement) 🎰

**Status**: 🚧 Not Started  
**Priority**: 🟡 Nice-to-Have (Can simplify for MVP with basic "replace meal" button)  
**Estimated Effort**: 1-2 weeks  
**Dependencies**: Phase 5 (Planner Core)  
**Blocks**: None (enhancement to Phase 5)

**Goal**: Granular control over the plan (Locking, Re-rolling, Components).

## 6.1 Technical Architecture

### Data Model Updates

- **`MealPlanDay`** table needs:
  - `main_recipe_id`: UUID
  - `side_recipe_id`: UUID (Nullable)
  - `is_main_locked`: Boolean
  - `is_side_locked`: Boolean

### Modules

- **`src/api/domain/planning/refiner.py`**: Handles the logic for "Get me a different recipe for this slot".

## 6.2 Implementation Details (Granular Phases)

### Phase 6A: Refinement Logic

- **Goal**: "Get me something else".
- **Tasks**:
    1. **DB**: Add `main_locked`, `side_locked` booleans to `meal_plan_days`.
    2. **Service**: `RefinerService.reroll(day_id, slot, directive)`.
        - Logic: Search DB/LLM for alternative matching constraints.

### Phase 6B: Slot Machine UI

- **Goal**: Interactive Locking and Spinning.
- **Tasks**:
    1. **UI**: Update `PlanDayCard` to show Main/Side slots independently.
    2. **Interaction**:
        - Tap Lock -> Toggle state.
        - Tap Spin -> Call API -> Animate change.
        - Long-press Spin -> Show "Directive" input (e.g., "Make it spicy").

## 6.3 Testing Plan

### Phase 6A Tests (Unit)

- [ ] **Locking**:
  - Input: Reroll Day 1. Main is Locked.
  - Assert: Only Side dish changes.
- [ ] **Directive**:
  - Input: Reroll with "No Chicken".
  - Assert: Returned recipe does not contain chicken ingredient/tag.

### Phase 6B Tests (E2E)
- [ ] **The "Spin" Flow**:
    1. Open Plan.
    2. Tap **Lock** icon on "Roast Chicken" (Main).
    3. Tap **Spin** button for the Day.
    4. **Verify**: Main remains "Roast Chicken". Side dish updates (e.g., from "Fries" to "Salad").
