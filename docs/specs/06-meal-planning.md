# 06 — Meal Planning 📅

> Plan your week of meals. Choose recipes, generate AI-powered plans, lock favorites, and auto-generate shopping lists.

---

## Overview

The Meal Planner helps users answer "What's for dinner this week?" It's a calendar-style view showing meals organized by day. Users can manually assign recipes to days, or ask the AI to generate a plan based on constraints (dietary, time, pantry utilization). Planned meals can be locked to protect them during re-generation. The planner connects directly to the shopping list — one tap generates a list of everything needed for the week.

The UX philosophy is "Choose Your Own Adventure" — the AI proposes thematic plan options (efficiency, variety, healthy), and the user picks one and customizes from there.

**Fun fact:** 🐋 Baleen whales have the ultimate meal plan: migrate 10,000 miles to eat in the summer, then fast for months. Talk about intermittent fasting. 🗓️

---

## User Stories

### US-PLN-01: View Weekly Plan
**As a** user planning my week,
**I want to** see all meals laid out by day,
**So that** I have a clear picture of the week ahead.

### US-PLN-02: Add Meal to Day
**As a** user who wants to assign a recipe to a specific day,
**I want to** tap on a day and pick a recipe,
**So that** I can build my plan manually.

### US-PLN-03: Generate AI Meal Plan
**As a** user who wants automated planning,
**I want to** set constraints and have the AI suggest a full week,
**So that** planning is effortless.

### US-PLN-04: Choose Plan Theme
**As a** user reviewing AI options,
**I want to** pick from 2-3 thematic plans ("Efficiency Week", "Global Flavors", "Pantry Challenge"),
**So that** I have meaningful variety.

### US-PLN-05: Lock Meals
**As a** user who's committed to certain meals,
**I want to** lock them so they don't change during re-generation,
**So that** I keep what I like while refreshing the rest.

### US-PLN-06: Delete Meal
**As a** user changing my mind,
**I want to** remove a meal from a day,
**So that** I can replace it or leave the day open.

### US-PLN-07: Generate Shopping List from Plan
**As a** user with a complete meal plan,
**I want to** auto-generate a shopping list from all recipes in the plan,
**So that** I buy exactly what I need.

### US-PLN-08: Navigate Between Weeks
**As a** user planning ahead,
**I want to** see next week (and this week),
**So that** I can plan more than one week.

### US-PLN-09: See What's Already in Pantry
**As a** user viewing a generated plan,
**I want to** know which recipes use ingredients I already have,
**So that** I minimize shopping and waste.

---

## User Flows

### Flow: View Weekly Plan
1. User navigates to Planner
2. Current week displayed (Mon-Sun) in vertical day list
3. Each day shows its meals or empty state
4. "This Week" / "Next Week" labels for context
5. Bottom action bar: "Generate AI Meal Plan" + "Generate Shopping List"

### Flow: Add Meal Manually
1. User taps "Add a meal" card on an empty day (or "Add another" on a filled day)
2. Navigates to recipe picker screen
3. Search/browse recipes → tap to select
4. Meal inserted for that date + meal type
5. Returns to planner → new meal visible

### Flow: Generate AI Meal Plan
1. User taps "Generate AI Meal Plan" in bottom action bar
2. Configuration screen:
   - Days slider (1-7)
   - Constraint toggles: 🌱 Vegetarian, 🐟 Pescatarian, 🌾 Low Carb, ⏱️ Under 30 min, 🔥 Spicy
   - "Prioritize pantry items" toggle
3. User taps "Generate Plan" → loading spinner
4. Preview screen: "Choose Your Adventure" — 3 thematic options
   - Each option: emoji, theme name, description, estimated shopping items, difficulty
5. User picks an option → meals populated for selected days
6. Returns to planner → meals visible with lock icons

### Flow: Lock/Unlock Meal
1. User taps lock/unlock icon on a meal card
2. Lock: meal won't change during re-generation (icon filled, label "Locked")
3. Unlock: meal is eligible for change (icon outline, label "Unlocked")
4. Toggle is immediate, no confirmation needed

### Flow: Delete Meal
1. User taps delete (X) button on meal card (only visible on unlocked meals)
2. ConfirmDialog: "Remove meal?" / "Remove {recipe title} from {day}?"
3. Confirm → meal deleted → day shows empty state
4. Cancel → no change

### Flow: Generate Shopping List
1. User taps "Generate Shopping List" (only visible if meals exist)
2. For each meal in the week:
   - Fetch recipe details (ingredients)
   - Compare against existing shopping list (avoid duplicates)
3. Missing/new ingredients added to shopping list
4. Navigate to Shopping List screen
5. Show toast: "Added X items to shopping list"

### Flow: Navigate Weeks
1. User taps "Next ›" → advance to next week (weekOffset + 1)
2. User taps "‹ Prev" → go back one week (min: current week, weekOffset ≥ 0)
3. Label updates: "This Week", "Next Week", or date range (for 2+ weeks out)

---

## UI Behavior

### Planner Screen (Redesigned Round 7)
- **Week navigation bar:** Prev ‹ / Week Label / › Next
  - Prev disabled at current week
  - Label: "This Week", "Next Week", or date range
- **Day list:** Vertical scroll, one section per day:
  - **Day header:** "Monday, Feb 17" + "Today" badge (if today)
  - **Meal cards:** Recipe title (tappable → recipe detail), lock icon, delete button
  - **Empty day:** Dashed "Add a meal" card with Plus icon
  - **Filled day:** Meals listed + "Add another" button below
- **Bottom action bar:** Fixed at bottom:
  - "Generate Shopping List" (blue, shows meal count) — only if meals exist
  - "Generate AI Meal Plan" (green, sparkle icon) — always visible
- **Max-width:** 800px (desktop)
- **ConfirmDialog:** For delete actions

### Meal Card
```
┌─────────────────────────────────────┐
│ Honey Garlic Chicken          🔒  ✕ │
│ (tap title → recipe detail)        │
└─────────────────────────────────────┘
```
- Title is tappable → navigates to `/recipes/{id}`
- Lock icon: 🔒 (locked) or 🔓 (unlocked), tappable
- Delete (✕): Only on unlocked meals, triggers confirm

### Plan Configuration Screen
- **Days slider:** 1-7, with numeric display
- **Constraint chips:** Toggle buttons with icons
- **Pantry toggle:** Switch with description
- **Generate button:** Green, full-width, large

### Plan Preview Screen ("Choose Your Adventure")
- **3 option cards:** Emoji + theme + description + stats
- **Selection state:** Green border + checkmark when selected
- **Apply button:** Green, disabled until selection made

---

## Data Model

### `meal_plans` Table (Supabase — used by frontend directly)
```
meal_plans
├── id: uuid (PK)
├── household_id: uuid (FK → households)
├── date: date (which day)
├── meal_type: text ('main' | 'side' | 'breakfast' | 'lunch' | 'dinner' | 'snack')
├── recipe_id: uuid (FK → recipes)
├── locked: boolean (default: true)
├── notes: text (optional)
├── created_at: timestamp
└── updated_at: timestamp
```

### Backend `plans` Table (API — for plan-level metadata)
```
plans
├── id: uuid (PK)
├── household_id: uuid (FK)
├── name: text
├── start_date: date
├── end_date: date
├── status: enum (draft | active | completed | archived)
├── selected_option_id: text (which adventure option was chosen)
├── constraints: jsonb (dietary, time, preferences)
├── created_at: timestamp
└── updated_at: timestamp

plan_slots
├── id: uuid (PK)
├── plan_id: uuid (FK → plans)
├── date: date
├── meal_type: enum
├── recipe_id: uuid (FK → recipes)
├── is_locked: boolean
├── notes: text
├── servings: integer
├── created_at: timestamp
└── updated_at: timestamp
```

**Note:** There are currently two parallel data models — the frontend uses `meal_plans` directly via Supabase, while the backend has a more structured `plans` + `plan_slots` model. These need to be reconciled.

---

## Business Rules

1. **One plan active at a time** per household (backend constraint)
2. **Locked meals survive re-generation** — only unlocked slots get new recipes
3. **Past weeks are read-only** — can't add meals to past dates (weekOffset ≥ 0)
4. **Shopping list deduplication** — if an item is already on the list, don't add again
5. **Ingredient aggregation** — if 2 recipes need onions, combine into one shopping item
6. **Minimum 3 recipes required** for AI plan generation (to have enough variety)
7. **Plan themes are distinct** — each of the 3 options should feel meaningfully different
8. **Recipe scoring** — AI prioritizes recipes that match pantry (minimize shopping)

---

## Current State

| Feature | Status | Notes |
|---------|--------|-------|
| Weekly day list view | ✅ Built (Round 7) | Vertical layout, redesigned |
| Add meal manually | ✅ Built | Recipe picker → insert |
| Week navigation | ✅ Built | Prev/Next with labels |
| Lock/unlock meals | ✅ Built | Toggle with icons |
| Delete meal | ✅ Built | With ConfirmDialog |
| Generate shopping list | ✅ Built | Aggregates recipes → shopping |
| Plan generation config | ✅ Built | Days, constraints, pantry toggle |
| "Choose Your Adventure" | ✅ Built | 3 thematic options |
| Desktop layout | ✅ Built (Round 7) | maxWidth 800px |
| **AI plan generation** | ⚠️ Mock | Returns fake options, not real LLM |
| **Recipe scoring** | ✅ Built (backend) | Not wired to frontend |
| **Data model reconciliation** | ❌ Needed | Frontend/backend use different tables |

---

## Open Questions

### OQ-PLN-01: Data Model Reconciliation
The frontend writes to `meal_plans` directly via Supabase, but the backend has a richer `plans` + `plan_slots` model. Should we consolidate to one approach?

### OQ-PLN-02: Meal Types
Currently most meals are 'main'. Should we support breakfast/lunch/dinner/snack per day? How does the UI handle multiple meal types per day?

### OQ-PLN-03: Re-Generation Flow
When user taps "Generate" with existing meals, what happens to unlocked meals? Delete and replace? Prompt for confirmation?

### OQ-PLN-04: Plan History
Should users see past plans? ("What did we eat last week?") Or are completed plans archived silently?

### OQ-PLN-05: Side Dish Pairing
The phase 0 prototypes emphasize main + side pairing. How explicit should this be in the planner? Separate slots? Or AI bundles main+side together?

### OQ-PLN-06: Leftover Tracking
Phase 0 mentions "repurposing leftovers" (e.g., roast chicken → soup). Should the planner track leftovers and suggest follow-up meals?
