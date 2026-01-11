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

## 6.2 Implementation Details

### The Re-roll Logic

- **Input**: `current_plan_day`, `slot_to_reroll` (Main/Side), `text_directive` (Optional).
- **Process**:
    1. Identify the constraints of the *original* plan option (e.g., "Vegetarian").
    2. Add `text_directive` as a filter (e.g., "Spicy").
    3. Search DB for candidates excluding the current recipe.
    4. Return top match.

### UI Components (`SlotMachine.tsx`)

- **Visuals**:
  - Animate the "Spin" (simple vertical slide or opacity fade).
  - Lock Icon (Toggle).
  - Text Input (Popover on long-press of Spin button?).

## 6.3 Testing Plan

### Unit Tests

- `test_lock_respect`: Request re-roll of Day 1. Ensure Main does *not* change if locked.
- `test_directive_filtering`: Request re-roll with "No Chicken". Ensure result is not chicken.
- `test_side_compatibility`: Ensure the new side matches the main (e.g., don't suggest Rice as a side for Risotto). *Advanced: might need LLM check.*

### End-to-End Tests

- **The "Spin" Flow**:
    1. Open Plan.
    2. Tap Lock on "Roast Chicken".
    3. Tap Spin on "Day 1".
    4. Verify Chicken remains, but Side Dish changes.
