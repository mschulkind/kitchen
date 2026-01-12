# Phase 7: Shopping List Core 🛒

**Status**: 🚧 In Progress (Backend ✅, Frontend 🚧)
**Priority**: 🔴 Essential (Critical output of the whole system!)  
**Estimated Effort**: 1-2 weeks  
**Dependencies**: Phase 3 (Delta Engine), Phase 5 (Finalized plan)  
**Blocks**: Phase 8 (Store Intelligence sorts the list)

**Goal**: A functional, syncable list derived from the Plan.

## 7.1 Technical Architecture

### Modules

- **`src/api/domain/shopping/aggregator.py`**: Combines Plan needs with Delta Engine.
- **`src/api/domain/shopping/syncer.py`**: Helpers for Realtime/Conflict resolution.

### Data Model

- **`shopping_list_items`**:
  - `id`, `name`, `quantity`, `unit`, `is_checked`, `category`, `aisle_hint`.

## 7.2 Implementation Details (Granular Phases)

### Phase 7A: Aggregation Engine

- **Goal**: Plan + Pantry = Shopping List.

- **Tasks**:

    1. **Service**: `ShoppingService.generate_from_plan(plan_id)`.

        - Calls `DeltaService` to find deficits.

        - Merges duplicates (Sum quantities).

    2. **Stock Up Logic**:

        - Check item metadata (e.g., "Canned Beans", "Rice").

        - If `shelf_life > 30 days` AND `frequency == high`:

        - Add `suggestion="Buy bulk? (Long shelf life)"` to the list item.

    3. **DB**: Insert into `shopping_list_items`.

### Phase 7B: Sync & UI

- **Goal**: Collaborative Checklist.
- **Tasks**:
    1. **Frontend**: `app/shopping/index.tsx`.
    2. **Realtime**: Use `supabase.channel` to listen for `UPDATE` events on `is_checked`.
    3. **UI**: Checkbox list grouped by Category (Produce, Dairy).

## 7.3 Testing Plan

### Phase 7A Tests (Unit)

- [ ] **Summing**:
  - Input: Recipe A needs 1 Onion. Recipe B needs 2 Onions.
  - Assert: List contains 1 item "Onion" with qty 3.
- [ ] **Subtraction**:
  - Input: Need 3 Onions. Have 1.
  - Assert: List contains "Onion" qty 2.

### Phase 7B Tests (Realtime)

- [ ] **Sync Scenario**:
  1. Open Client A and Client B.
  2. Client A checks "Milk".
  3. **Verify**: Client B shows "Milk" checked within < 1s.
  4. Client B unchecks "Milk".
  5. **Verify**: Client A shows unchecked.

### Phase 7C Tests (Frontend E2E)

1.  **Shopping Execution Flow**:
    - **Go to**: `/shopping`
    - **Action**: Click checkbox for "Apples".
    - **Verify**: Item moves to "Completed" section (or strikes through).
    - **Action**: Click "Clear Completed".
    - **Verify**: "Apples" is removed from list.
    - **Verify**: "Apples" count in Pantry increases (if configured to auto-add).

2.  **Add Custom Item**:
    - **Action**: Type "Batteries" in "Add item" input.
    - **Click**: Add.
    - **Verify**: "Batteries" appears in "Other" category.
