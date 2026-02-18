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

## 🎰 The Slot Machine: Granular Meal Refinement

> These ideas come from the original "Planning Algorithm & UX" design and Phase 6 spec. They describe the **dream UX** for meal plan refinement — turning plan tweaking from a chore into something fun.

### The Concept

Once a user has selected an "Adventure Path" (theme), the plan is displayed as a grid where each day has **component slots** (Main dish, Side dish). The user can interact with these slots like a slot machine — locking what they like, spinning what they don't.

### Slot Machine UI

```
┌─────────────── Monday ───────────────┐
│ 🔒 Main: Honey Garlic Chicken  [🎰] │
│ 🔓 Side: Roasted Broccoli      [🎰] │
└──────────────────────────────────────┘
┌─────────────── Tuesday ──────────────┐
│ 🔓 Main: Chicken Tinga Tacos   [🎰] │
│ 🔓 Side: Mexican Rice          [🎰] │
└──────────────────────────────────────┘
```

### Interactions

- **🔒 Lock**: Tap the lock icon on any component (Main or Side) to preserve it during re-rolls
- **🎰 Spin (Single Slot)**: Tap the spin icon on just the Main or just the Side — keeps the other
- **🎰 Spin (Whole Day)**: Spin button at day level replaces all unlocked slots for that day
- **🌀 Global Re-roll**: "Shuffle all unlocked slots" across the entire plan, respecting the theme
- **💬 Micro-Direction**: When hitting Spin, optional text input appears: "Make it spicy", "Too heavy, something lighter", "Kids won't eat this"
- **Long-press Spin**: Shows the directive input for more targeted re-rolling

### Data Model for Slot Machine

```sql
-- Extends meal_plan_days or plan_slots
ALTER TABLE plan_slots ADD COLUMN is_main_locked BOOLEAN DEFAULT FALSE;
ALTER TABLE plan_slots ADD COLUMN is_side_locked BOOLEAN DEFAULT FALSE;
ALTER TABLE plan_slots ADD COLUMN side_recipe_id UUID REFERENCES recipes(id);
```

### Refinement API

```
POST /api/v1/plans/{plan_id}/reroll
Body: {
  "day_date": "2026-02-20",
  "slot": "main" | "side" | "both",
  "directive": "Make it spicy",  // optional
  "locked_slots": ["2026-02-19:main", "2026-02-20:main"]
}
Response: { "new_recipe": { ... }, "alternatives": [...] }
```

---

## 🃏 The Card Stack: Theme Selection UX

> From the original "Choose Your Own Adventure" design — the AI doesn't just generate a plan, it generates **strategy options** that feel meaningfully different.

### Strategy Pitch

The AI analyzes inventory + preferences and proposes 3 distinct **Adventure Paths**:

> **User**: "Plan for Mon-Thu. Use the chicken."
>
> **AI**: "Okay, here are 3 ways we can play this:"
>
> 1. 🏠 **The "Efficiency" Path**: Roast the whole chicken Monday. Tacos Tuesday. Soup Wednesday. (Low effort, high reuse).
> 2. 🌍 **The "Global Tour" Path**: Chicken Curry (Indian) on Mon. Chicken Schnitzel (German) on Tue. (High variety, more prep).
> 3. 🥗 **The "Healthy/Light" Path**: Poached chicken salads and grain bowls. (Low calorie, fresh).

### Card Stack UI

- **Visual**: Horizontal scroll of "Strategy Cards"
- **Content**: Large emoji + theme name + "Why this path?" narrative + "Inventory Used" progress bar + estimated shopping items count
- **Selection**: Tap card to select, green border + checkmark appears
- **Animation**: Cards fan out like a hand of cards, selected card slides to center

### The Algorithm (Under the Hood)

1. **Inventory & Constraint Retrieval**: Fetch pantry items (qty > 0), user preferences, filtered recipes
2. **Candidate Pool Generation**: Score every recipe by:
   - **Use-Up Score**: How many pantry items does it use? (Weighted by expiry — rotting spinach scores highest)
   - **Effort Score**: Prep time vs. user's "Low effort" request
   - **Preference Match**: Does it fit the "Vibe"?
3. **Strategy Clustering** (The Magic): LLM takes top 20 candidates and groups them:
   - Cluster 1: Common Ingredient (e.g., "All use Chicken")
   - Cluster 2: Common Vibe (e.g., "Quick & Easy")
   - Cluster 3: Novelty (e.g., "Recipes you haven't tried")
4. **Narrative Generation**: LLM writes the "Pitch" for each path

### Data Structures

```typescript
type PlanRequest = {
  dateRange: DateRange;
  attendees: number;
  constraints: string[];  // "No dairy"
  goals: string[];        // "Use spinach"
};

type PlanStrategy = {
  id: string;
  title: string;           // "The Comfort Route"
  description: string;     // "Hearty meals for a rainy week."
  primary_focus: "efficiency" | "variety" | "speed" | "health" | "adventure";
  preview_recipes: RecipeStub[];
  inventory_usage_pct: number;
  estimated_shopping_items: number;
};

type DraftPlan = {
  strategy_id: string;
  days: {
    date: Date;
    main: Recipe;
    side: Recipe | null;
    locked: boolean;
    alternatives: Recipe[];  // Pre-fetched for "Spinning"
  }[];
};
```

---

## 🎚️ The Tweak Bar: Algorithm Weight Controls

Instead of (or in addition to) typing constraints, give the user **sliders** for the algorithm weights:

| Slider | Left | Right |
|--------|------|-------|
| **Adventurousness** | 🏠 Safe | 🌍 Wild |
| **Effort** | 😴 Lazy | 👨‍🍳 Chef Mode |
| **Pantry Usage** | 🛒 Buy Fresh | 🧹 Empty Fridge |
| **Health** | 🍔 Comfort | 🥗 Clean Eating |

These sliders directly weight the scoring algorithm: a "Wild + Chef Mode + Empty Fridge" configuration surfaces complex recipes using obscure pantry items, while "Safe + Lazy + Buy Fresh" gives simple crowd-pleasers with a bigger shopping list.

---

## 🍗 Leftover Chain: Multi-Day Ingredient Reuse

> From the original brief: "The app will prioritize recipes that share ingredients, use up garden surpluses, and incorporate leftovers (e.g., roast chicken one night, chicken soup the next)."

### How It Works

1. **Detection**: When generating plans, AI identifies "leftover chain" opportunities
2. **Display**: Day 2 meals show "Uses leftovers from Day 1" badge
3. **Tracking**: After cooking, prompt "Did you have leftovers? How much?" — feeds into next day's plan
4. **Scoring**: Leftover chains get a scoring bonus (less food waste = better plan)

### Example Chain

```
Day 1: Whole Roast Chicken (4 servings) → 2 servings leftover
Day 2: Chicken Tinga Tacos (uses leftover chicken) → leftover tortillas
Day 3: Chicken Tortilla Soup (uses leftover chicken + tortillas)
```

**Fun fact:** 🐋 Whale sharks filter 6,000 liters of water per hour but still manage zero food waste. That's the energy we want. ♻️

---

## 🎮 Gamification Ideas (Future)

> Inspired by research into apps like Mealime, Kitmate, Recipe Roulette, and Duolingo-style habit building.

### Recipe Roulette / Tinder-Style Swiping
- **Swipe right** on recipes you'd eat this week, **swipe left** to skip
- AI learns your preferences from swipe patterns
- Great for "I don't know what I want" moments — faster than browsing

### Cooking Streaks
- Track consecutive days/weeks of cooking at home
- Milestone badges: "Week Warrior 🏅", "Month Master 🎖️", "Global Explorer 🌍" (tried 5 cuisines)
- Gentle streak notifications: "You've cooked 12 days in a row!"

### Family Voting
- Each household member votes on proposed meals (👍/👎 or ⭐ ratings)
- AI weighs votes by household role (e.g., the cook's vote counts more)
- Weekly "Most Popular Meal" highlight
- "Dad's Pick of the Week" leaderboard

### Ingredient Challenges
- "Pantry Challenge": Cook using only what's in your pantry this week
- "Use It or Lose It": Challenge to use 3 expiring items before they go bad
- "Global Tour": Cook one dish from a different country each week

### Achievement System
- Badges for milestones (first recipe imported, first plan generated, 10th meal cooked)
- Skill recognition: "Pasta Master" (cooked 10 pasta dishes), "Grill Sergeant" (5 grilled meals)
- Progress bars for long-term goals

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

### OQ-PLN-07: Gamification MVP
Which gamification feature should we try first? Cooking streaks are simplest. Tinder-swiping is flashiest. Family voting requires multi-user. What's the best ROI?

### OQ-PLN-08: Tweak Bar Implementation
Should the Tweak Bar (sliders) be part of the plan generation screen, or a separate "preferences" view that persists across sessions?

### OQ-PLN-09: Leftover Chain Automation
How much should leftover chains be automated vs. manual? Should the AI assume leftovers, or only suggest chains when user confirms leftovers?
