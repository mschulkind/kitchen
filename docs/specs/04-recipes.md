# 04 — Recipes 📖

> Browse, view, import, and manage your recipe collection. No manual creation — recipes come from AI or URL import.

---

## Overview

Recipes are the building blocks of the Kitchen app. Users don't manually type recipes — they either import them from URLs or create them through conversation with an AI (see spec #05). Recipes include structured ingredients (parsed into name, quantity, unit) and step-by-step instructions. They connect to the pantry (stock checking), planner (meal assignment), and shopping list (missing items).

**Fun fact:** 🐋 Whales don't need recipes. Their meal plan has been "open mouth, swim forward" for 50 million years. Efficiency goals. 🏊

---

## User Stories

### US-RCP-01: Browse Recipes
**As a** home cook,
**I want to** browse my recipe collection with search,
**So that** I can find what I want to make.

### US-RCP-02: Import Recipe from URL
**As a** user who found a recipe online,
**I want to** paste a URL and have the app extract the recipe,
**So that** I don't have to type it out.

### US-RCP-03: View Recipe Detail
**As a** user deciding what to cook,
**I want to** see the full recipe with ingredients, instructions, and metadata,
**So that** I can evaluate it and gather what I need.

### US-RCP-04: Check Stock Against Recipe
**As a** user about to cook a recipe,
**I want to** see which ingredients I have, which are low, and which are missing,
**So that** I know what to buy or substitute.

### US-RCP-05: Add Missing Ingredients to Shopping List
**As a** user who checked stock and found missing items,
**I want to** add them to my shopping list with one tap,
**So that** I remember to buy them.

### US-RCP-06: "I Have This" (Lazy Discovery)
**As a** user checking stock who actually has an item not in inventory,
**I want to** tap "I have this" to add it to my pantry,
**So that** my inventory catches up to reality.

### US-RCP-07: Edit Recipe
**As a** user who wants to tweak a recipe,
**I want to** edit the title, servings, times, ingredients, and instructions,
**So that** the recipe matches how I actually make it.

### US-RCP-08: Delete Recipe
**As a** user who doesn't want a recipe anymore,
**I want to** delete it with confirmation,
**So that** it doesn't clutter my collection.

### US-RCP-09: View Source Attribution
**As a** user viewing an imported recipe,
**I want to** see where it came from (original URL),
**So that** I can credit the source or revisit the original.

---

## User Flows

### Flow: Browse & Search
1. User navigates to Recipes screen
2. Sees list of recipe cards (image, title, cook time, last cooked)
3. Types in search bar → list filters by title
4. Taps a recipe card → navigates to recipe detail

### Flow: Import from URL
1. User taps "+" FAB → action sheet opens
2. Selects "Import from URL"
3. URL input dialog appears
4. User pastes URL → taps "Import"
5. Spinner shows "Parsing recipe..."
6. Backend: `POST /api/v1/recipes/ingest` → scrapes page → parses ingredients → saves
7. Success → recipe appears in list → user can view it
8. Error → error message shown (e.g., "Couldn't parse this page")

### Flow: View Recipe Detail
1. User taps recipe card → detail screen
2. Sees: hero image (or placeholder), title, metadata row (servings, prep time, cook time)
3. Scrolls to ingredients list (name + qty/unit)
4. Scrolls to instructions (numbered steps)
5. Source attribution at bottom (if imported)

### Flow: Check Stock
1. From recipe detail, user taps "Check Stock" button
2. Stock-check screen loads recipe ingredients + pantry items
3. Ingredients categorized into 3 groups:
   - ✅ **You Have (Enough)** — green, item name + qty
   - ⚠️ **Low Stock** — yellow, item name + "Need: X more"
   - ❌ **Missing** — red, item name + qty needed + "I Have This" button
4. User can tap "I Have This" → adds item to pantry (Lazy Discovery)
5. User can tap "Add to Shopping List" → adds missing + low items to shopping list
6. Navigates to shopping list after adding

### Flow: Delete Recipe
1. User taps trash icon on recipe detail
2. ConfirmDialog: "Delete Recipe?" / "This will permanently remove it"
3. Confirm → recipe deleted → redirect to recipes list
4. Cancel → dialog closes

---

## UI Behavior

### Recipes List Screen
- **Search bar:** Filter by title (client-side)
- **Recipe cards:** Image (100×100), title (2 lines max), cook time, last cooked date
- **FAB:** Orange "+" button → action sheet
- **Action sheet options:**
  - "Import from URL" → URL dialog
  - "Chat with AI (Coming Soon)" → disabled ← See spec #05
- **Empty state:** Book emoji + "No recipes yet" + prompt to import or chat
- **Max-width:** 800px (desktop)

### Recipe Detail Screen
- **Hero image:** Full-width, or placeholder with "Generate with AI" button (parked)
- **Metadata row:** Servings (users icon), Prep time (clock), Cook time (chef hat)
  - Only shown if value > 0 (fixed Round 7)
- **Check Stock button:** Blue, prominent
- **Ingredients:** Card with list, each row has name (left) + qty/unit (right)
- **Instructions:** Numbered steps with orange badges
- **Source:** Gray card with URL hostname (if imported)
- **Actions:** Edit (pencil), Delete (trash) in header
- **Max-width:** 800px (desktop)

### Stock Check Screen
- **Three sections:** Have / Low / Missing (with counts)
- **"I Have This" button:** Green plus icon on missing items
- **"Add to Shopping List" button:** Orange, bottom of screen
- **"🎉 You have everything!" message:** When all items available

---

## Data Model

### `recipes` Table
```
recipes
├── id: uuid (PK)
├── household_id: uuid (FK → households)
├── title: text (required)
├── source_url: text (optional)
├── source_domain: text (optional, extracted from URL)
├── servings: integer (optional)
├── prep_time_minutes: integer (optional)
├── cook_time_minutes: integer (optional)
├── total_time_minutes: integer (optional)
├── description: text (optional)
├── instructions: jsonb[] (array of step objects)
├── tags: text[] (optional)
├── image_url: text (optional)
├── is_parsed: boolean (default: false)
├── raw_markdown: text (optional, original scraped content)
├── last_cooked_at: timestamp (optional)
├── created_at: timestamp
└── updated_at: timestamp
```

### `recipe_ingredients` Table
```
recipe_ingredients
├── id: uuid (PK)
├── recipe_id: uuid (FK → recipes)
├── raw_text: text (original ingredient line)
├── quantity: numeric (parsed)
├── unit: text (parsed)
├── item_name: text (parsed, normalized)
├── notes: text (e.g., "diced", "large")
├── section: text (optional, e.g., "For the sauce")
├── sort_order: integer
├── confidence: float (parser confidence 0.0-1.0)
├── created_at: timestamp
└── updated_at: timestamp
```

---

## Business Rules

1. **No manual recipe creation** — recipes only come from URL import or AI chat (spec #05)
2. **Ingredient parsing:** Raw text → structured (qty, unit, item_name, notes) with confidence score
3. **Deduplication:** Same source URL won't create duplicate recipes
4. **Stock matching:** Case-insensitive comparison between recipe ingredients and pantry item names
5. **Source attribution:** Always show where imported recipes came from
6. **Recipe editing:** Users can modify any field after import/creation
7. **Deletion is permanent:** With confirmation dialog, not recoverable
8. **Tags are optional:** For future categorization (e.g., "vegetarian", "quick", "kid-friendly")

---

## Current State

| Feature | Status | Notes |
|---------|--------|-------|
| Browse recipes | ✅ Built | Search + card list |
| Import from URL | ✅ Built | Backend ingestion pipeline |
| View recipe detail | ✅ Built | Full layout with metadata |
| Check stock | ✅ Built | 3-tier comparison |
| Add to shopping list | ✅ Built | From stock check |
| Lazy Discovery | ✅ Built | "I have this" button |
| Edit recipe | ✅ Built | Full form |
| Delete recipe | ✅ Built | With ConfirmDialog (Round 7) |
| Source attribution | ✅ Built | Shows URL hostname |
| Desktop layout | ✅ Built (Round 7) | maxWidth 800px |
| Manual creation | ❌ Removed (Round 7) | Per user decision |
| AI image generation | ⏸️ Parked | Button exists, API needs keys |
| AI chat creation | 🔴 Not started | See spec #05 |

---

## 📄 Recipe PDF Export

> From the original recipe-format-design.md — generate beautiful, printable recipe cards.

### Concept

A "Print / Export" button on any recipe generates a formatted PDF with:
- **Header**: Recipe title, source attribution, servings, times
- **Mise en Place**: Organized ingredient checklist by section
- **Timeline**: Interleaved steps for main dish + side dish that finish at the same time
- **Shopping List**: Only missing items (after stock check)

### Format Ideas
- Color-coded sections (orange for active cooking, blue for prep, green for resting)
- Countdown timers embedded as text cues ("Set timer: 25 min")
- QR code linking back to the in-app recipe for digital access while shopping
- Jinja2 template rendering on the backend → PDF via WeasyPrint or similar

### API
```
GET /api/v1/recipes/{id}/pdf
GET /api/v1/recipes/{id}/pdf?include_shopping=true&side_recipe_id={uuid}
```

---

## ⭐ Favorites & Recipe Organization

> From todo.txt and the original phase specs — ways to curate and prioritize your recipe collection.

### Favorites
- **Star/Heart icon** on recipe cards and detail view
- `is_favorite BOOLEAN` field on recipes table
- Favorites filter on the recipe list ("Show favorites only")
- Favorites get **priority weighting** in meal plan generation — the AI should prefer your favorites
- "Save as Favorite" prompt after cooking a meal from the planner

### Tags & Categories
- User-assignable tags: "weeknight", "kid-friendly", "date night", "meal prep", "comfort food", "quick", "vegetarian"
- AI auto-suggests tags based on recipe content during import/creation
- Tag-based filtering on recipe list (multi-select chip bar)
- Tags influence meal plan diversity — AI avoids planning 5 "comfort food" meals in a row

### Recipe Collections (Future)
- Curated lists: "Summer Grilling", "Slow Cooker Favorites", "Holiday Meals"
- Share collections with other households
- Import community-curated collections

---

## 📏 Recipe Scaling

> From todo.txt — handle different serving sizes intelligently.

### How It Works
- Recipe detail shows a **servings adjuster** (stepper: -/+)
- Changing servings recalculates all ingredient quantities proportionally
- Stock check uses the **adjusted quantities**, not the original
- Shopping list items reflect the scaled amounts
- Some ingredients don't scale linearly (e.g., salt, spices) — flag these

### Smart Scaling Rules
- Round to practical measurements (don't say "0.67 cups" — say "⅔ cup")
- Handle unit conversions during scaling (e.g., 0.25 cups → 4 tablespoons)
- Flag when scaling down below practical minimums ("Can't halve 1 egg easily")

---

## 🏷️ Ingredient Specification Improvements

> From todo.txt — "when specifying '1 can', also specify the size of the can"

### Can/Package Sizes
- Ingredient parser should extract container sizes: "1 can (14.5 oz) diced tomatoes"
- Display both container count AND volume/weight
- Stock check matches against actual pantry container sizes
- Common can sizes stored as reference data: 14.5oz, 15oz, 28oz, etc.

### Weight vs. Volume Support
- Support both weight (grams, oz, lbs) and volume (cups, tbsp, ml) measurements
- Smart conversion between weight and volume for common ingredients
- User preference for metric vs. imperial (stored in settings)

---

## ⏱️ Time-Based Filtering

> From todo.txt — "keep recipes under one hour including prep, or make this configurable"

- **Default filter**: Show total time (prep + cook) on recipe cards
- **Time filter** on recipe list: "Under 30 min", "Under 1 hour", "Any time"
- **Configurable max time** in settings (household preference)
- AI plan generation respects time constraints: "Only weeknight-friendly meals (under 45 min)"
- Time-based tags auto-applied: "Quick" (< 30 min), "Medium" (30-60 min), "Project" (> 60 min)

---

## Open Questions

### OQ-RCP-01: Recipe Categories/Tags
Should we show tags on recipe cards? Should there be a tag filter? What tags are useful?

### OQ-RCP-02: Favorites
Should users be able to "star" favorite recipes? Should favorites be promoted in meal planning?

### OQ-RCP-03: Recipe Scaling
When checking stock, should the comparison account for the servings needed vs. recipe default servings?

### OQ-RCP-04: Ingredient Parsing Accuracy
Current parser has confidence scores. Should we show low-confidence parses to users for correction?

### OQ-RCP-05: Recipe Source Variety
Beyond URL import and AI chat, should we support other sources? (e.g., shared recipes from other households, curated collections)

### OQ-RCP-06: PDF Layout
Should PDFs include interleaved main+side timelines by default? Or only when a side dish is specified?

### OQ-RCP-07: Favorite Weighting
How much should favorites influence meal plan generation? Always include at least 1 favorite per week? Or just boost their score?

### OQ-RCP-08: Scaling Edge Cases
How to handle non-linear scaling (salt, yeast, baking powder)? Manual override table? AI suggestion?
