# Phase 7: Shopping List Core 🛒

**Status**: 🚧 Not Started  
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

## 7.2 Implementation Details

### The Aggregator

1. **Trigger**: User clicks "Finalize Plan".
2. **Input**: The `MealPlan`.
3. **Process**:
    - Extract all `RecipeIngredients`.
    - Call `DeltaService` (Phase 3) against `Pantry`.
    - Filter for `MISSING` or `BUY`.
    - Merge duplicates (e.g., 2 recipes need Onions -> Sum them).
4. **Output**: Insert rows into `shopping_list_items`.

### Realtime Sync

- Use **Supabase Realtime** on the client.
- `channel('shopping_list').on('postgres_changes', ...)`
- **Conflict Strategy**: Last-Write-Wins (LWW) for the boolean `is_checked` state is sufficient for V1.

## 7.3 Testing Plan

### Unit Tests

- `test_aggregation_summing`: Ensure 2 onions + 1 onion = 3 onions in the list.
- `test_aggregation_pantry_subtraction`: Ensure existing stock is subtracted.

### Integration Tests

- **Sync Test**:
  - Client A checks "Milk".
  - Client B (listening) should receive update within 500ms.
  - *Note*: Hard to test in CI, usually manual or with specialized realtime test harness.
