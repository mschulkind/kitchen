# Round 6: Autonomous Feature Implementation 🐋

## Problem
5 scenarios remain untested/unimplemented that can be resolved without user input.

## Approach

### 1. VIS-04: Scan Item Rejection — **Just Test** (0 effort)
Scan-result page already has remove buttons per item. Just navigate there and test dismissal flow in browser.

### 2. VOICE-02: Wire Voice Handlers — **Medium Effort**
Parser is solid (5 command types). Handlers are stubs returning hardcoded messages.
Wire handlers to actual Supabase operations:
- ADD_ITEM → insert into shopping_list
- REMOVE_ITEM → delete from shopping_list  
- CHECK_ITEM → update checked=true in shopping_list
- ASK_INVENTORY → query pantry_items
- ADD_PANTRY → insert into pantry_items

### 3. PLN-06: Move Meal Between Days — **Medium Effort**
Instead of complex drag-drop gesture handling (risky on web), implement a simpler
"Move" button that updates the meal's date. This is functionally equivalent and
much more reliable on web.

### 4. STORE-02: Store Preference in Settings — **Low Effort**
Add a simple "Preferred Store" text input in Settings. Backend Store model exists
but no CRUD endpoints yet — store this as a local preference for now.

### 5. INV-06: Reclassify — **No Action**
No pagination exists by design. FlatList loads all items. Working correctly for
household-scale inventory (typically <100 items). Not a bug.

## Open Questions
None — all decisions made autonomously.
