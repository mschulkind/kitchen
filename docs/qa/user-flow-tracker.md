# 🐋 Kitchen App — User Flow Tracker & QA Central

> **Purpose**: Central document for spec agreement, QA tracking, and roadmap planning.
> **Last Updated**: 2026-02-15
> **Status**: 🔴 Full QA cycle in progress — all scenarios starting as untested.

---

## 📊 Summary Dashboard

| Metric | Count |
|--------|-------|
| Total Scenarios | 58 |
| ✅ Pass | 0 |
| ❌ Fail | 0 |
| 🐛 Bug Found | 0 |
| 🔧 Fixed | 0 |
| ⬜ Untested | 58 |
| 🚫 Blocked | 0 |

### Phase Readiness

| Phase | Scenarios | Passed | Readiness |
|-------|-----------|--------|-----------|
| P0 — Auth & Navigation | 6 | 0/6 | 0% |
| P1A — Pantry/Inventory | 8 | 0/8 | 0% |
| P1B — Recipes | 10 | 0/10 | 0% |
| P1C — Shopping Lists | 8 | 0/8 | 0% |
| P2A — Meal Planner | 8 | 0/8 | 0% |
| P2B — Delta Engine | 4 | 0/4 | 0% |
| P2C — Cooking Mode | 5 | 0/5 | 0% |
| P2D — Vision / Scanning | 4 | 0/4 | 0% |
| P3A — Voice | 2 | 0/2 | 0% |
| P3B — Store Intelligence | 2 | 0/2 | 0% |
| P3C — Recipe Images | 1 | 0/1 | 0% |

---

## 🔴 P0 — Auth & Navigation (Can you use the app at all?)

These must pass before anything else is testable.

### AUTH-01: Landing page loads
- **Priority**: P0
- **Preconditions**: Stack running (`just up` + frontend)
- **Steps**: Navigate to app root URL
- **Expected**: Landing page renders with "Get Started" button
- **Status**: ⬜ Untested
- **Notes**:

### AUTH-02: Dev login flow
- **Priority**: P0
- **Preconditions**: Dev user seeded (`admin@kitchen.local`)
- **Steps**: Navigate to `/devlogin`, click sign in
- **Expected**: User is authenticated, redirected to dashboard
- **Status**: ⬜ Untested
- **Notes**:

### AUTH-03: Dashboard hub loads after login
- **Priority**: P0
- **Preconditions**: Authenticated user
- **Steps**: After login, observe dashboard
- **Expected**: Hub page renders with widget cards (Tonight's Meal, Shopping Count, Expiring Items)
- **Status**: ⬜ Untested
- **Notes**:

### AUTH-04: Navigation between sections
- **Priority**: P0
- **Preconditions**: Authenticated user on dashboard
- **Steps**: Navigate to Pantry, Recipes, Planner, Shopping via nav
- **Expected**: Each section loads without errors
- **Status**: ⬜ Untested
- **Notes**:

### AUTH-05: Session persistence on refresh
- **Priority**: P0
- **Preconditions**: Authenticated user
- **Steps**: Refresh the browser page
- **Expected**: User remains logged in, current page state preserved
- **Status**: ⬜ Untested
- **Notes**:

### AUTH-06: API health check
- **Priority**: P0
- **Preconditions**: Backend running
- **Steps**: `curl http://localhost:5300/health`
- **Expected**: 200 OK response
- **Status**: ⬜ Untested
- **Notes**:

---

## 🟠 P1A — Pantry / Inventory

### INV-01: View empty pantry
- **Priority**: P1
- **Preconditions**: Authenticated, no pantry items
- **Steps**: Navigate to Pantry
- **Expected**: Empty state message displayed
- **Status**: ⬜ Untested
- **Notes**: Previous QA found RLS blocker here

### INV-02: Add pantry item manually
- **Priority**: P1
- **Preconditions**: On pantry screen
- **Steps**: Enter item name, select location (Fridge/Pantry/Freezer), set quantity, save
- **Expected**: Item appears in pantry list, persists on refresh
- **Status**: ⬜ Untested
- **Notes**: 🔴 Known blocker from Jan 19 QA — RLS policy issue

### INV-03: Edit pantry item
- **Priority**: P1
- **Preconditions**: At least one pantry item exists
- **Steps**: Click item, modify quantity or location, save
- **Expected**: Changes persist on refresh
- **Status**: ⬜ Untested
- **Notes**:

### INV-04: Delete pantry item
- **Priority**: P1
- **Preconditions**: At least one pantry item exists
- **Steps**: Click item, click delete
- **Expected**: Item removed from list, stays removed on refresh
- **Status**: ⬜ Untested
- **Notes**:

### INV-05: Search pantry items
- **Priority**: P1
- **Preconditions**: Multiple pantry items exist
- **Steps**: Type in search field
- **Expected**: List filters to matching items in real-time
- **Status**: ⬜ Untested
- **Notes**:

### INV-06: Pantry pagination
- **Priority**: P1
- **Preconditions**: More items than one page
- **Steps**: Scroll/paginate through items
- **Expected**: Additional items load correctly
- **Status**: ⬜ Untested
- **Notes**:

### INV-07: Pantry location filter
- **Priority**: P1
- **Preconditions**: Items in multiple locations
- **Steps**: Filter by Fridge, Pantry, Freezer, Garden
- **Expected**: Only items in selected location shown
- **Status**: ⬜ Untested
- **Notes**:

### INV-08: Realtime sync (multi-user)
- **Priority**: P1
- **Preconditions**: Two browser tabs/sessions as same household
- **Steps**: Add item in Tab A, observe Tab B
- **Expected**: Item appears in Tab B without refresh
- **Status**: ⬜ Untested
- **Notes**:

---

## 🟠 P1B — Recipes

### RCP-01: View recipe list
- **Priority**: P1
- **Preconditions**: Authenticated
- **Steps**: Navigate to Recipes
- **Expected**: Recipe list loads (or empty state if no recipes)
- **Status**: ⬜ Untested
- **Notes**:

### RCP-02: Add recipe manually
- **Priority**: P1
- **Preconditions**: On recipes screen
- **Steps**: Click "New Recipe", fill in title, ingredients, instructions, save
- **Expected**: Recipe appears in list, detail view shows correct data
- **Status**: ⬜ Untested
- **Notes**:

### RCP-03: Import recipe from URL
- **Priority**: P1
- **Preconditions**: On recipes screen, valid recipe URL available
- **Steps**: Click import, paste URL, submit
- **Expected**: Recipe is scraped, parsed, and added to list with ingredients
- **Status**: ⬜ Untested
- **Notes**:

### RCP-04: View recipe detail
- **Priority**: P1
- **Preconditions**: At least one recipe exists
- **Steps**: Click on recipe in list
- **Expected**: Detail page shows title, ingredients, instructions, tags
- **Status**: ⬜ Untested
- **Notes**:

### RCP-05: Edit recipe
- **Priority**: P1
- **Preconditions**: Viewing a recipe detail
- **Steps**: Click edit, modify title or ingredients, save
- **Expected**: Changes persist, visible on refresh
- **Status**: ⬜ Untested
- **Notes**:

### RCP-06: Delete recipe
- **Priority**: P1
- **Preconditions**: At least one recipe exists
- **Steps**: Click delete on recipe
- **Expected**: Recipe removed from list
- **Status**: ⬜ Untested
- **Notes**:

### RCP-07: Search recipes
- **Priority**: P1
- **Preconditions**: Multiple recipes exist
- **Steps**: Type in search field
- **Expected**: List filters to matching recipes
- **Status**: ⬜ Untested
- **Notes**:

### RCP-08: Filter recipes by tag
- **Priority**: P1
- **Preconditions**: Recipes with different tags
- **Steps**: Click a tag filter
- **Expected**: Only recipes with that tag shown
- **Status**: ⬜ Untested
- **Notes**:

### RCP-09: Parse ingredient text
- **Priority**: P1
- **Preconditions**: Adding/editing a recipe
- **Steps**: Type "2 cups all-purpose flour" in ingredient field
- **Expected**: Parsed into structured ingredient (qty: 2, unit: cup, item: all-purpose flour)
- **Status**: ⬜ Untested
- **Notes**:

### RCP-10: Recipe list pagination
- **Priority**: P1
- **Preconditions**: Many recipes
- **Steps**: Scroll/paginate
- **Expected**: Additional recipes load
- **Status**: ⬜ Untested
- **Notes**:

---

## 🟠 P1C — Shopping Lists

### SHOP-01: View shopping list
- **Priority**: P1
- **Preconditions**: Authenticated
- **Steps**: Navigate to Shopping
- **Expected**: Active shopping list displayed (or empty state)
- **Status**: ⬜ Untested
- **Notes**:

### SHOP-02: Add item to shopping list
- **Priority**: P1
- **Preconditions**: On shopping screen
- **Steps**: Type item name, submit
- **Expected**: Item appears in list
- **Status**: ⬜ Untested
- **Notes**:

### SHOP-03: Check off item
- **Priority**: P1
- **Preconditions**: Shopping list with items
- **Steps**: Tap checkbox on an item
- **Expected**: Item shows as checked, moves to "checked" section
- **Status**: ⬜ Untested
- **Notes**:

### SHOP-04: Uncheck item
- **Priority**: P1
- **Preconditions**: Shopping list with checked items
- **Steps**: Tap checkbox on checked item
- **Expected**: Item moves back to unchecked section
- **Status**: ⬜ Untested
- **Notes**:

### SHOP-05: Clear checked items
- **Priority**: P1
- **Preconditions**: Shopping list with checked items
- **Steps**: Click "Clear Checked"
- **Expected**: All checked items removed from list
- **Status**: ⬜ Untested
- **Notes**:

### SHOP-06: Delete item from list
- **Priority**: P1
- **Preconditions**: Shopping list with items
- **Steps**: Swipe or click delete on item
- **Expected**: Item removed
- **Status**: ⬜ Untested
- **Notes**:

### SHOP-07: Realtime sync (multi-user shopping)
- **Priority**: P1
- **Preconditions**: Two sessions, same household
- **Steps**: Check item in Tab A, observe Tab B
- **Expected**: Check state syncs instantly
- **Status**: ⬜ Untested
- **Notes**:

### SHOP-08: Create new shopping list
- **Priority**: P1
- **Preconditions**: Authenticated
- **Steps**: Create a new shopping list
- **Expected**: New list created and becomes active
- **Status**: ⬜ Untested
- **Notes**:

---

## 🟡 P2A — Meal Planner

### PLAN-01: View planner (week view)
- **Priority**: P2
- **Preconditions**: Authenticated
- **Steps**: Navigate to Planner
- **Expected**: Week calendar view with meal slots
- **Status**: ⬜ Untested
- **Notes**:

### PLAN-02: Generate AI meal plan
- **Priority**: P2
- **Preconditions**: On planner, recipes exist in system
- **Steps**: Click "New Plan", submit preferences
- **Expected**: 3 thematic plan options returned
- **Status**: ⬜ Untested
- **Notes**: Requires LLM API key

### PLAN-03: Select and activate a plan
- **Priority**: P2
- **Preconditions**: Plan options generated
- **Steps**: Choose one of 3 options, click activate
- **Expected**: Plan is activated, shows in week view
- **Status**: ⬜ Untested
- **Notes**:

### PLAN-04: Lock a meal slot
- **Priority**: P2
- **Preconditions**: Active plan with slots
- **Steps**: Click lock icon on a meal slot
- **Expected**: Slot marked as locked, preserved during regeneration
- **Status**: ⬜ Untested
- **Notes**:

### PLAN-05: Unlock a meal slot
- **Priority**: P2
- **Preconditions**: Active plan with locked slot
- **Steps**: Click unlock on locked slot
- **Expected**: Slot unlocked
- **Status**: ⬜ Untested
- **Notes**:

### PLAN-06: Manually add recipe to slot
- **Priority**: P2
- **Preconditions**: Active plan, recipes exist
- **Steps**: Click empty slot, search recipe, select it
- **Expected**: Recipe assigned to that slot
- **Status**: ⬜ Untested
- **Notes**:

### PLAN-07: Preview meal plan
- **Priority**: P2
- **Preconditions**: Plan options generated
- **Steps**: Click preview on a plan option
- **Expected**: Full plan preview with all meals shown
- **Status**: ⬜ Untested
- **Notes**:

### PLAN-08: Complete a meal plan
- **Priority**: P2
- **Preconditions**: Active plan
- **Steps**: Mark plan as complete
- **Expected**: Plan archived, planner ready for new plan
- **Status**: ⬜ Untested
- **Notes**:

---

## 🟡 P2B — Delta Engine (Stock Check)

### DELTA-01: Check stock for a recipe
- **Priority**: P2
- **Preconditions**: Recipe exists, pantry has some items
- **Steps**: Open recipe detail, click "Check Stock"
- **Expected**: Shows which ingredients you have vs. need
- **Status**: ⬜ Untested
- **Notes**:

### DELTA-02: Fuzzy matching of ingredients
- **Priority**: P2
- **Preconditions**: Pantry has "Salt", recipe needs "Kosher Salt"
- **Steps**: Run stock check
- **Expected**: "Kosher Salt" matched to "Salt" in pantry
- **Status**: ⬜ Untested
- **Notes**:

### DELTA-03: Unit conversion in comparison
- **Priority**: P2
- **Preconditions**: Pantry has "1 lb butter", recipe needs "200g butter"
- **Steps**: Run stock check
- **Expected**: Correct comparison across unit systems
- **Status**: ⬜ Untested
- **Notes**:

### DELTA-04: Add missing items to shopping list
- **Priority**: P2
- **Preconditions**: Stock check shows missing items
- **Steps**: Click "Add to shopping list" for missing items
- **Expected**: Missing items added to active shopping list
- **Status**: ⬜ Untested
- **Notes**:

---

## 🟡 P2C — Cooking Mode

### COOK-01: Enter cooking mode
- **Priority**: P2
- **Preconditions**: Recipe exists
- **Steps**: Open recipe, click "Cook"
- **Expected**: Cooking mode loads with large text, step-by-step view
- **Status**: ⬜ Untested
- **Notes**:

### COOK-02: Mise-en-place checklist
- **Priority**: P2
- **Preconditions**: In cooking mode
- **Steps**: View mise-en-place tab/section
- **Expected**: Checklist of prep items displayed
- **Status**: ⬜ Untested
- **Notes**:

### COOK-03: Step-by-step navigation
- **Priority**: P2
- **Preconditions**: In cooking mode
- **Steps**: Navigate between cooking steps
- **Expected**: Steps advance correctly, current step highlighted
- **Status**: ⬜ Untested
- **Notes**:

### COOK-04: Screen wake lock
- **Priority**: P2
- **Preconditions**: In cooking mode
- **Steps**: Leave device idle
- **Expected**: Screen stays on (wake lock active)
- **Status**: ⬜ Untested
- **Notes**:

### COOK-05: Mark recipe as cooked (inventory deduction)
- **Priority**: P2
- **Preconditions**: Finished cooking, pantry items exist
- **Steps**: Click "Done Cooking" or similar
- **Expected**: Pantry quantities decremented for used ingredients
- **Status**: ⬜ Untested
- **Notes**:

---

## 🟡 P2D — Vision / Scanning

### VIS-01: Analyze food image
- **Priority**: P2
- **Preconditions**: Authenticated, camera/image available
- **Steps**: Navigate to scan, take/upload photo of food items
- **Expected**: AI identifies food items, shows candidates
- **Status**: ⬜ Untested
- **Notes**: Requires Gemini API key

### VIS-02: Confirm scanned items to pantry
- **Priority**: P2
- **Preconditions**: Image analyzed, candidates shown
- **Steps**: Select items to confirm, submit
- **Expected**: Confirmed items added to pantry
- **Status**: ⬜ Untested
- **Notes**:

### VIS-03: Quick scan mode
- **Priority**: P2
- **Preconditions**: Authenticated
- **Steps**: Use quick scan endpoint
- **Expected**: Common items identified rapidly
- **Status**: ⬜ Untested
- **Notes**:

### VIS-04: Reject/dismiss scan candidates
- **Priority**: P2
- **Preconditions**: Scan candidates shown
- **Steps**: Dismiss incorrect items
- **Expected**: Dismissed items not added to pantry
- **Status**: ⬜ Untested
- **Notes**:

---

## 🟢 P3A — Voice

### VOICE-01: Add item via voice webhook
- **Priority**: P3
- **Preconditions**: Backend running, webhook configured
- **Steps**: POST to `/hooks/add-item` with "Add milk to shopping list"
- **Expected**: Milk added to active shopping list
- **Status**: ⬜ Untested
- **Notes**: Backend-only, no frontend UI

### VOICE-02: Voice command parsing
- **Priority**: P3
- **Preconditions**: Backend running
- **Steps**: POST to `/hooks/voice` with various intents
- **Expected**: Intent parsed and action executed
- **Status**: ⬜ Untested
- **Notes**:

---

## 🟢 P3B — Store Intelligence

### STORE-01: Aisle-based shopping list sorting
- **Priority**: P3
- **Preconditions**: Shopping list with items, store layout configured
- **Steps**: View shopping list with aisle sorting enabled
- **Expected**: Items sorted by store aisle
- **Status**: ⬜ Untested
- **Notes**: Frontend not built yet per status report

### STORE-02: Store layout configuration
- **Priority**: P3
- **Preconditions**: Settings accessible
- **Steps**: Configure preferred store
- **Expected**: Store layout saved, used for sorting
- **Status**: ⬜ Untested
- **Notes**: Frontend not built yet

---

## 🟢 P3C — Recipe Images

### IMG-01: Generate AI recipe image
- **Priority**: P3
- **Preconditions**: Recipe exists, Gemini API key set
- **Steps**: Click "Generate Image" on recipe
- **Expected**: AI-generated cover image created and displayed
- **Status**: ⬜ Untested
- **Notes**: Feature planned, may not be implemented

---

## 🔧 Bug Log

| Bug ID | Scenario | Description | Severity | Status | Fix Commit |
|--------|----------|-------------|----------|--------|------------|
| | | | | | |

---

## 🗺️ Roadmap (To be filled after QA)

### Production Ready Now
_TBD after QA_

### Needs Fixes Before Launch
_TBD after QA_

### Deferred / Future Work
_TBD after QA_

### Next Sprint Priorities
_TBD after QA_
