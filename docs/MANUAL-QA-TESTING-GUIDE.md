# 🧑‍🍳 Kitchen App — Complete Manual QA Testing Guide

> **Last Updated**: 2026-02-17
> **Coverage**: All 52/58 passing scenarios (90% of app)
> **Time to Complete**: ~30 minutes for full walkthrough

This guide walks you through **every feature** of the Kitchen meal planning app. Click-by-click instructions to see exactly what works.

---

## Table of Contents

1. [Setup & Getting Started](#setup--getting-started)
2. [Login & Authentication](#login--authentication)
3. [Dashboard Hub](#dashboard-hub)
4. [Pantry / Inventory](#pantry--inventory)
5. [Recipes](#recipes)
6. [Shopping Lists](#shopping-lists)
7. [Meal Planner](#meal-planner)
8. [Cooking Mode](#cooking-mode)
9. [Settings](#settings)
10. [Advanced Features](#advanced-features)

---

## Setup & Getting Started

### Prerequisites
- Backend API running: `http://localhost:5300`
- Frontend running: `http://localhost:8200`
- Both services should be active

### Starting the Services

**Terminal 1 — Start the API:**
```bash
cd /workspace
SUPABASE_URL=http://192.168.1.2:8250 \
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIiwiaXNzIjoic3VwYWJhc2UiLCJpYXQiOjE3NjgxOTk0MjUsImV4cCI6MjA4MzU1OTQyNX0.wiPYoEVwcFKQOTXEZ8UfZsFWoFCQvoqATXcSJeZJVK8 \
PYTHONDONTWRITEBYTECODE=1 python3 -B -m uvicorn src.api.main:app --host 0.0.0.0 --port 5300
```

**Terminal 2 — Start the Frontend:**
```bash
cd /workspace/src/mobile
BROWSER=none npx expo start --web --port 8200
```

Wait for both to show "ready" messages. 🟢

---

## Login & Authentication

### Option 1: Dev Login (Fastest) ⚡

1. **Navigate to**: `http://localhost:8200/devlogin`
2. **Email**: `admin@kitchen.local`
3. **Password**: `admin123`
4. **Click**: "Sign In" button
5. **Expected**: Redirected to Dashboard Hub

You're now logged in as "Chef" with the "Dev Kitchen" household.

### Option 2: Regular Login (Via Auth)

1. **Navigate to**: `http://localhost:8200`
2. **Click**: "Sign In" button on landing page
3. **Enter email**: any email address
4. **Enter password**: any password
5. **Click**: "Sign Up" to create account OR "Sign In" if returning
6. **Expected**: Redirected to Dashboard Hub

---

## Dashboard Hub

> The home screen showing your kitchen at a glance.

### View the Hub
1. **Navigate to**: `http://localhost:8200` (if not already here)
2. **See**: "Good Evening, Chef 👋" greeting (personalized to time of day)

### Widgets
The hub displays three status cards:

**Tonight's Dinner**
- Shows tonight's assigned meal (or "No meal planned for tonight")
- Updates from meal planner

**Shopping Count**
- "X to buy" — number of unchecked items on shopping list
- From the Shopping module

**Expiring Items**
- "X expiring" — pantry items past expiration
- Estimated from purchase date

### Module Cards
Below the widgets, six main sections:

| Card | Navigates To | Purpose |
|------|--------------|---------|
| 🍽️ Recipes | `/recipes` | Browse & cook recipes |
| 🥫 Pantry | `/inventory` | Manage pantry stock |
| 📅 Planner | `/planner` | Weekly meal planning |
| 🛒 Shopping | `/shopping` | Grocery list |
| ⚙️ Settings | `/settings` | App preferences |
| 🚪 Sign Out | — | Logout |

**Try it**: Click each card to navigate. Use browser back button to return to hub. ✅

---

## Pantry / Inventory

> Manage your household's food stock by location (Fridge, Freezer, Pantry, etc.).

### View Pantry

1. **From hub**: Click "Pantry: Manage Stock" card
   - OR navigate directly to: `http://localhost:8200/inventory`

2. **See**: Items grouped by location
   - 🧊 **Fridge**: Butter (2 count), Peas (5 count)
   - 🥫 **Pantry**: cheeseburger (1 burger)

### Add an Item

1. **Click**: "+" button (floating action button)
2. **Fill in**:
   - **Name**: "Milk"
   - **Location**: Select "Fridge" from dropdown
   - **Quantity**: 1
   - **Unit**: count
3. **Click**: "Save"
4. **Expected**: Item appears in Fridge section immediately

### Edit an Item

1. **Click**: Any item (e.g., "Peas")
2. **Navigate to**: `/inventory/[item-id]` (auto-navigated)
3. **Change**: Quantity to "10"
4. **Click**: "Save"
5. **Expected**: Return to list, "Peas" now shows "10 count"

### Delete an Item

1. **On pantry list**: Click trash icon on any item
2. **Confirm**: Browser dialog appears ("Are you sure?")
3. **Click**: "OK"
4. **Expected**: Item removed from list

### Search & Filter

1. **Search Box**: Type "Peas" in search field
   - List filters in real-time to show only "Peas"
2. **Location Filter**: Click "All Locations" dropdown
   - Select "Fridge" to show only fridge items
   - Select "Pantry" to show only pantry items

---

## Recipes

> Create, browse, edit, and cook recipes.

### View Recipe List

1. **From hub**: Click "Recipes: Browse & Cook"
   - OR: `http://localhost:8200/recipes`

2. **See**: Three demo recipes
   - Quick Salad (0 min prep)
   - Fluffy Pancakes (15 min prep)
   - Test Waffles (20 min prep)

### View Recipe Detail

1. **Click**: "Quick Salad" recipe card
2. **See**: Recipe detail page with:
   - **Title**: Quick Salad
   - **Servings**: 2
   - **Prep/Cook times**: 10m prep, 0m cook
   - **Ingredients**: lettuce (1 head), tomatoes (2 count), cucumber (1), olive oil
   - **Instructions**: 
     1. Wash lettuce
     2. Chop vegetables
     3. Toss with dressing

### Create a New Recipe (Manual Entry)

1. **Click**: "+" floating action button
2. **Click**: "Manual Entry" option
3. **Fill in**:
   - **Title**: "My Omelette"
   - **Servings**: 2
   - **Prep Time**: 5
   - **Cook Time**: 10
4. **Add Ingredients**: Click "+" to add rows
   - Row 1: eggs (3), count
   - Row 2: butter (1), tbsp
5. **Add Instructions**:
   - "Beat eggs in a bowl"
   - "Heat butter in pan"
   - "Pour eggs and cook until golden"
6. **Click**: "Save Recipe"
7. **Expected**: New recipe appears in list

### Edit a Recipe

1. **On recipe detail**: Click pencil ✏️ icon (top right)
2. **Navigate to**: `/recipes/[id]/edit`
3. **Change**: Title to "My Famous Omelette"
4. **Change**: Add ingredient "cheese (1 cup)"
5. **Click**: "Save"
6. **Expected**: Return to detail, title updated

### Delete a Recipe

1. **On recipe detail**: Click trash 🗑️ icon (top right)
2. **Confirm**: "Are you sure?" dialog
3. **Click**: "OK"
4. **Expected**: Redirected back to recipe list, recipe removed

### Check Stock (Pantry vs. Recipe)

1. **On recipe detail**: Click "Check Stock" button
2. **See**: Two sections:
   - **You Have**: Items that match your pantry (usually none or partial)
   - **Missing**: Items you need to buy
3. **For Quick Salad**:
   - Missing (4): lettuce, tomatoes, cucumber, olive oil
4. **Try**: Click "I have this" on any ingredient
   - Item moves from Missing to You Have
5. **Try**: Click "Add 4 items to Shopping List"
   - Items added to shopping list (deduped, auto-categorized)
   - Navigates to Shopping page

---

## Shopping Lists

> Manage your grocery shopping with automatic categorization by store aisle.

### View Shopping List

1. **From hub**: Click "Shopping: Grocery List"
   - OR: `http://localhost:8200/shopping`

2. **See**: Items grouped by category
   - 🥬 **Produce**: bananas, lettuce, tomatoes, cucumber
   - 🥩 **Meat & Seafood**: chicken breast
   - 🛢️ **Other**: flour, olive oil

### Add an Item

1. **Text field**: Type "Bread"
2. **Click**: "+" button (or press Enter)
3. **Expected**: "Bread" appears under "Other" category
4. **Note**: Auto-categorization by keyword (smart!)

### Check Off an Item

1. **Click**: Checkbox next to "Bread"
2. **Expected**:
   - Item moves to "Completed" section
   - "Clear Completed" button appears
   - Counter shows "✓ 1 completed"

### Uncheck an Item

1. **In Completed section**: Click checkbox next to completed item
2. **Expected**: Item moves back to active list

### Delete an Item

1. **Next to any item**: Click trash 🗑️ icon
2. **Expected**: Item removed immediately

### Clear All Completed Items

1. **Click**: "Clear Completed" button (appears when items are checked)
2. **Expected**: All checked items removed

---

## Meal Planner

> Plan your week's meals day-by-day and generate shopping lists.

### View Weekly Planner

1. **From hub**: Click "Planner: Week Layout"
   - OR: `http://localhost:8200/planner`

2. **See**: 7-day calendar view
   - Days Mon-Sun with dates
   - "Add Meal" buttons for each day
   - Date range at top: "Feb 16 - Feb 22" (or current week)

### Navigate Between Weeks

1. **Click**: Left arrow (previous week)
   - Date range shifts back
2. **Click**: Right arrow (next week)
   - Date range shifts forward

### Assign a Meal to a Day

1. **Click**: "Add Meal" on Monday (Feb 16)
2. **Navigates to**: Recipe picker
3. **Search** (optional): Type "salad"
4. **Click**: "Quick Salad" recipe
5. **Expected**:
   - Redirected to planner
   - Monday now shows "Quick Salad" in meal slot
   - Dashboard hub updates "Tonight's Dinner" widget!

### Remove a Meal

1. **On planner**: Click trash 🗑️ icon on meal card
2. **Expected**: Meal removed, day shows "Add Meal" again

### Move a Meal to Different Day

1. **On planner**: With a meal assigned, click the ↔️ swap icon (blue)
2. **Expected**: Day-picker row appears with buttons for other days
3. **Click**: "Wed" button
4. **Expected**:
   - Meal moves from Mon to Wed
   - Mon shows "Add Meal" again
   - Wed now displays the meal

### Lock/Unlock a Meal

1. **On meal card**: Click lock 🔒 icon (top-left of buttons)
2. **First click**: Lock turns green (locked)
   - Reroll & Move buttons disappear
   - Meal is "locked" (won't change unless unlocked)
3. **Click again**: Lock turns gray (unlocked)
   - Reroll & Move buttons reappear

### Reroll a Meal (AI Suggestion)

1. **On unlocked meal**: Click refresh ↻ icon (orange)
2. **Note**: Currently shows "Loading..." but full AI requires Gemini API key
3. **Expected**: Would suggest similar recipes if API key configured

### Generate Shopping List from Plan

1. **With meals assigned**: Click "Shopping List (1 meals)" button (bottom)
2. **Expected**:
   - Fetches all ingredients from assigned recipes
   - Deduplicates against existing items
   - Auto-categorizes (Produce, Dairy, Meat, etc.)
   - Navigates to Shopping page
   - Shows "✅ Added 4 items"

---

## Cooking Mode

> Large-text, step-by-step cooking instructions. Designed for use while cooking!

### Enter Cooking Mode

1. **On recipe detail** (e.g., Quick Salad): Click green "Cook 👨‍🍳" FAB
2. **Navigate to**: `/recipes/[id]/cook`
3. **See**:
   - Step counter: "Step 1 of 3"
   - Large instruction text: "Wash lettuce"
   - Back/Next buttons
   - Progress bar

### Navigate Steps

1. **Click**: "Next" button
   - Moves to Step 2: "Chop vegetables"
   - "Back" button now enabled
2. **Click**: "Next" again
   - Moves to Step 3: "Toss with dressing"
   - "Finish" button appears instead of "Next"
3. **Click**: "Back" button
   - Returns to previous step
   - Back disabled on Step 1

### Mise-en-Place (Ingredient Prep List)

1. **While cooking**: Click "Ingredients" button (top of screen)
2. **See**: Checklist of all ingredients
   - lettuce (checkbox)
   - tomatoes (checkbox)
   - cucumber (checkbox)
   - olive oil (checkbox)
3. **Check off**: Items as you prep them
   - Counter shows "3/4 ready" → "4/4 ready"
4. **Close**: Click elsewhere or button disappears

### Complete Cooking

1. **On final step**: Click "Finish" button
2. **See**: Confirmation "Cooking Complete!"
3. **Click**: "Done Cooking" button
4. **Expected**: Redirected to recipe detail, `last_cooked_at` updated

---

## Settings

> App preferences and household info.

### View Settings

1. **From hub**: Click "Settings" card
   - OR: `http://localhost:8200/settings`

2. **See**: Four sections

### Account Section
- **Email**: admin@kitchen.local
- **Status**: "Signed in"

### Household Section
- **Name**: My Kitchen
- **Members**: 1 member
- **Button**: "Manage" (for inviting collaborators — not yet implemented)

### Preferences
- **Expiry Notifications**: Toggle (currently ON)
- **Dark Mode**: Toggle (currently OFF)

### Preferred Store 🏪
- **Text field**: Enter your favorite grocery store
- **Example**: "Trader Joe's"
- **Button**: "Save Store"
- **Expected**: Changes to "✅ Saved!" confirmation
- **Storage**: Saved to device storage (persists across sessions)

### About
- Version: Kitchen App v0.1.0
- Phase: Phase 1: Foundation & Inventory

---

## Advanced Features

### Voice Commands (API Testing)

Voice commands are fully functional but require API calls. Test via curl:

**Add item to shopping list:**
```bash
curl -X POST http://localhost:5300/api/v1/hooks/voice \
  -H "Content-Type: application/json" \
  -d '{"text": "Add milk and eggs to my shopping list"}'
```
**Expected response:**
```json
{
  "success": true,
  "message": "Added milk and eggs to your shopping list.",
  "items_added": ["milk", "eggs"],
  "command_type": "add_item"
}
```

**Check off an item:**
```bash
curl -X POST http://localhost:5300/api/v1/hooks/voice \
  -H "Content-Type: application/json" \
  -d '{"text": "Check off the milk"}'
```

**Remove an item:**
```bash
curl -X POST http://localhost:5300/api/v1/hooks/voice \
  -H "Content-Type: application/json" \
  -d '{"text": "Remove eggs from my list"}'
```

**Ask about inventory:**
```bash
curl -X POST http://localhost:5300/api/v1/hooks/voice \
  -H "Content-Type: application/json" \
  -d '{"text": "Do we have any chicken?"}'
```

**Add to pantry:**
```bash
curl -X POST http://localhost:5300/api/v1/hooks/voice \
  -H "Content-Type: application/json" \
  -d '{"text": "I bought chicken and rice, put them in the fridge"}'
```

### Scanning & Vision (Requires API Key)

**Status**: Blocked on Gemini API key

To test when API key is available:
1. Navigate to `/inventory/scan`
2. Upload an image of food items
3. AI identifies items
4. Confirm/reject suggestions
5. Add to pantry

### Recipe Images (Requires API Key)

**Status**: Blocked on Gemini API key

To test when API key is available:
1. On recipe detail: Click "Generate with AI"
2. AI generates cover image for recipe
3. Image displays in recipe header

### Realtime Multi-User Sync (Requires Infrastructure)

**Status**: Blocked on Supabase Realtime WebSocket

To test when realtime is enabled:
1. Open app in two browser tabs (same household)
2. Add item to pantry in Tab A
3. Tab B should update instantly without refresh
4. Same for shopping list, meal plan, etc.

---

## Keyboard Shortcuts

| Action | Key |
|--------|-----|
| Go back | Browser back button or "Back" button on page |
| Close dialog | ESC or click outside |
| Add item | Enter (in text fields) |
| Search | Start typing in search box |

---

## Troubleshooting

### "Page won't load"
- Check that API is running (`http://localhost:5300/docs`)
- Check that Frontend is running (`http://localhost:8200`)
- Clear browser cache: Cmd+Shift+Delete → Clear all

### "Can't login"
- Make sure you use `/devlogin` for instant dev access
- If regular login, check email is valid
- Try creating new account

### "Item doesn't appear"
- Refresh browser (Cmd+R)
- Check browser console for errors (F12 → Console)
- Make sure you're logged in

### "Realtime sync not working"
- This requires Supabase Realtime to be enabled
- Currently blocked (WebSocket 404 error)
- Workaround: Refresh browser to see updates

---

## Feature Checklist

Use this checklist to verify features as you test:

### Core Features
- [ ] Login / Dev Login
- [ ] Dashboard Hub
- [ ] View Pantry items by location
- [ ] Add/Edit/Delete pantry item
- [ ] Search & filter pantry

### Recipes
- [ ] View recipe list
- [ ] View recipe detail with ingredients
- [ ] Create recipe (manual entry)
- [ ] Edit recipe
- [ ] Delete recipe
- [ ] Check stock vs. pantry

### Shopping
- [ ] View shopping list with categories
- [ ] Add item to shopping list
- [ ] Check off item
- [ ] Delete item
- [ ] Clear completed items

### Meal Planning
- [ ] View weekly planner
- [ ] Navigate weeks (prev/next)
- [ ] Add meal to day
- [ ] Remove meal
- [ ] Move meal to different day
- [ ] Lock/unlock meal
- [ ] Generate shopping list from plan

### Cooking
- [ ] Enter cooking mode
- [ ] Navigate steps (back/next)
- [ ] View mise-en-place checklist
- [ ] Complete cooking

### Settings
- [ ] View account info
- [ ] View household info
- [ ] Toggle preferences
- [ ] Save preferred store

---

## Time-Saving Tips ⚡

1. **Dev login first** — Use `/devlogin` to bypass email confirmation
2. **Pre-made data** — Dev account has sample recipes & pantry items ready
3. **Test different paths** — Try adding recipes manually AND from the planner
4. **Check categories** — Add "bananas", "chicken breast", "flour" to test auto-categorization
5. **Use browser back** — All pages support browser back button navigation

---

## Questions or Issues?

If you find bugs or unexpected behavior:
1. Note the exact steps to reproduce
2. Screenshot or note the error message
3. Check browser console (F12) for JavaScript errors
4. Report in the Kitchen GitHub issue tracker

Happy testing! 🧑‍🍳✨
