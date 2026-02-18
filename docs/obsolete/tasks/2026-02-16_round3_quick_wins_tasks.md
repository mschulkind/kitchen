# 🐋 Round 3: Quick Wins — Task List

> **Date**: 2026-02-16
> **Plan**: `docs/plans/2026-02-16_round3_quick_wins_plan.md`

## State Management

| Feature | Status |
|---------|--------|
| 1. Recipe Delete | ⬜ Not Started |
| 2. Recipe Edit | ⬜ Not Started |
| 3. Check-Stock Shopping Fix | ⬜ Not Started |
| 4. Cooking Mise-en-Place | ⬜ Not Started |
| 5. Store Sorter Integration | ⬜ Not Started |
| 6. Settings User Display | ⬜ Not Started |
| 7. Planner Meal Assignment | ⬜ Not Started |

---

## Tasks

### Feature 1: Recipe Delete (RCP-07)
- [ ] 1.1 Add delete button (Trash2 icon) to recipe detail page header
- [ ] 1.2 Add confirmation dialog (window.confirm on web)
- [ ] 1.3 Wire DELETE mutation to `API_URL/recipes/{id}`
- [ ] 1.4 Navigate back to recipe list on success + invalidate query cache

### Feature 2: Recipe Edit (RCP-06)
- [ ] 2.1 Create `src/mobile/app/(app)/recipes/[id]/edit.tsx` page
- [ ] 2.2 Pre-populate form with existing recipe data fetched from API
- [ ] 2.3 Wire PATCH mutation to `API_URL/recipes/{id}`
- [ ] 2.4 Add edit button (Edit3 icon) to recipe detail page header
- [ ] 2.5 Navigate to edit page on button press

### Feature 3: Check-Stock Shopping Fix (KNOWN-03 / DEL-04)
- [ ] 3.1 Add `household_id` to insert items in check-stock.tsx
- [ ] 3.2 Add null guard for householdId before insert

### Feature 4: Cooking Mise-en-Place (COOK-02)
- [ ] 4.1 Wire "Ingredients" button to show mise-en-place modal
- [ ] 4.2 Fetch from `/cooking/mise-en-place/{recipe_id}` API
- [ ] 4.3 Display checklist with checkable items in a Sheet/modal
- [ ] 4.4 Track checked state locally during cooking session

### Feature 5: Store Sorter Integration (SHOP-07 / P3B)
- [ ] 5.1 Add `GET /shopping/sorted/{list_id}` API endpoint
- [ ] 5.2 Wire `StoreSorter.sort_list()` into endpoint
- [ ] 5.3 Update shopping frontend to use sorted API response for grouping
- [ ] 5.4 Fall back to current hardcoded categories if API fails

### Feature 6: Settings User Display (KNOWN-06)
- [ ] 6.1 Import auth session in settings page
- [ ] 6.2 Replace "Guest User" with email/display name from session

### Feature 7: Planner Meal Assignment (PLN-03)
- [ ] 7.1 Add `POST /planner/plans/{plan_id}/slots/{slot_id}/assign` endpoint
- [ ] 7.2 Wire existing `update_slot()` service method
- [ ] 7.3 Update `add.tsx` to call API instead of direct Supabase

### Final
- [ ] 8.1 Run `just check` (lint + tests)
- [ ] 8.2 Commit all changes
- [ ] 8.3 Launch autonomous QA round 3
