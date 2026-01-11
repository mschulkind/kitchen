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

## 8.2 Implementation Details

### The Scraper

- **Rate Limiting**: Be polite. Cache results aggressively.
- **Normalization**: Map "Lucerne Whole Milk Gallon" -> "Milk".

### The Sorter

- **Default Map**:
    1. Produce
    2. Bakery
    3. Deli
    4. ...
    5. Dairy (Back of store)
    6. Frozen (End)
- **Algorithm**:
  - For each list item, lookup `aisle`.
  - If found, assign index. If not, assign "Unknown" (bottom).
  - Sort list by index.

## 8.3 Testing Plan

### Unit Tests

- `test_sorter`: Input `["Milk" (Aisle 12), "Apple" (Produce)]`. Expected: `["Apple", "Milk"]` (assuming Produce is index 0).

### Integration Tests

- **Mock Scraper**: Ensure the system handles "Product Not Found" gracefully (defaults to "Uncategorized").
