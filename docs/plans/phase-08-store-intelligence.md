# Phase 8: Store Intelligence 🏪

**Status**: 🚧 Not Started  
**Priority**: 🟢 Defer (Category-based sorting is sufficient for MVP)  
**Estimated Effort**: 1-2 weeks  
**Dependencies**: Phase 7 (Shopping list to sort)  
**Blocks**: None (enhancement)

> ⚠️ **Note**: Store scraping may have legal/ToS implications. See [Open Questions Q10](open-questions.md#q10-store-scraping-legalityfeasibility).

**Goal**: Optimized traversal of the local supermarket.

## 8.1 Technical Architecture

### Modules

- **`src/api/domain/store/shaws_scraper.py`**: Selenium/Playwright or API client.
- **`src/api/domain/store/sorter.py`**: Sorting logic.

### Data Model

- **`store_aisle_mappings`**:
  - `item_keyword`: "milk"
  - `aisle`: "Aisle 12"
  - `store_id`: UUID

## 8.2 Implementation Details (Granular Phases)

### Phase 8A: Scraper & Data

- **Goal**: Build the Map.
- **Tasks**:
    1. **Research**: Reverse-engineer Shaw's mobile API (look for `aisle` field in product search).
    2. **DB**: Populate `store_aisle_mappings` (e.g., "Cumin" -> "Aisle 4").
    3. **Job**: Background task to update mappings lazily (when a new item appears on a list).

### Phase 8B: Sorting Logic

- **Goal**: Apply the Map to the List.
- **Tasks**:
    1. **Service**: `StoreSorter.sort(list_items)`.
    2. **Config**: Allow user to reorder Aisle sequence (Produce -> Deli -> Aisle 1...).
    3. **UI**: Update Shopping List to show Section Headers ("Aisle 12").

## 8.3 Testing Plan

### Phase 8A Tests (Integration)

- [ ] **API Check**:
  - Input: Search for "Oreos".
  - Assert: Returns "Aisle 9" (or actual value).

### Phase 8B Tests (Unit)

- [ ] **Sorting**:
  - Input: `["Milk" (Aisle 15), "Apple" (Produce), "Bread" (Bakery)]`.
  - Config: Produce -> Bakery -> Aisle 1... -> Aisle 15.
  - Assert: `["Apple", "Bread", "Milk"]`.
- [ ] **Unknown Handling**:
  - Input: `["Weird Fruit" (Unknown)]`.
  - Assert: Appears at bottom or top (configurable).

### Phase 8C Tests (Frontend E2E)

1.  **Store Sort Flow**:
    - **Go to**: `/shopping`
    - **Verify**: List is in default category order.
    - **Action**: Select Store "Shaw's".
    - **Verify**: List reorders to match Shaw's layout (e.g., Produce first).
    - **Verify**: Headers change to "Aisle 1", "Aisle 2", etc.

2.  **Edit Mapping**:
    - **Action**: Long press "Cumin".
    - **Action**: Select "Edit Location".
    - **Fill**: "Aisle 4".
    - **Click**: Save.
    - **Verify**: "Cumin" moves to "Aisle 4" group.
