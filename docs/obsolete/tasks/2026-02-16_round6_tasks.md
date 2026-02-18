# Round 6 Tasks

## State: In Progress

### VIS-04: Test Scan Item Rejection
- [ ] Navigate to scan-result page in browser
- [ ] Verify remove button exists per item
- [ ] Click remove on an item
- [ ] Verify item disappears from list
- [ ] Verify "Confirm All" count updates
- [ ] Update tracker

### VOICE-02: Wire Voice Handlers
- [ ] Read voice service.py and understand handler structure
- [ ] Read hooks route to understand API endpoint
- [ ] Implement _handle_add_item → insert to shopping_list via Supabase
- [ ] Implement _handle_remove_item → delete from shopping_list
- [ ] Implement _handle_check_item → update checked in shopping_list
- [ ] Implement _handle_ask_inventory → query pantry_items
- [ ] Implement _handle_add_pantry → insert to pantry_items
- [ ] Write/update tests
- [ ] Test via curl

### PLN-06: Move Meal Between Days
- [ ] Add "Move" button (CalendarDays icon) to meal card
- [ ] Create day-picker UI (sheet or inline buttons)
- [ ] Implement updateMealDate mutation
- [ ] Test in browser

### STORE-02: Store Preference in Settings
- [ ] Add "Preferred Store" section to settings.tsx
- [ ] Add text input for store name
- [ ] Store locally via AsyncStorage or Supabase user metadata
- [ ] Test in browser

### INV-06: Reclassify
- [ ] Update tracker to mark as "N/A — working as designed"

### Final
- [ ] Run all tests
- [ ] Full QA pass on new features
- [ ] Update tracker with final results
- [ ] Commit
