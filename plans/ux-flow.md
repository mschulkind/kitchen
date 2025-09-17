# UX Flows

This document outlines the primary user experience flows for the Personalized Dinner & Shopping App, emphasizing mobile-first design principles for on-the-go use. Flows are designed to be intuitive, with minimal navigation, large touch targets, and quick interactions. Reference [brief.md](brief.md) for feature context and [design-system.md](design-system.md) for technical alignment.

## Core Principles
- **Mobile-First**: All screens optimized for touch (e.g., 44px+ buttons), portrait orientation, thumb-friendly layouts.
- **Simplicity**: 3-4 taps max per flow; no deep menus. Use bottom navigation or gestures.
- **Offline-Capable**: Cache inventory and plans locally; sync when online.
- **Feedback**: Immediate visual cues (e.g., checkmarks for verification, loading spinners for LLM suggestions).
- **Accessibility**: High contrast, voice-over support, semantic labels.

## Primary Flow: Generate Meal Plan → Verify Inventory → Create Shopping List

### 1. Initiate Meal Planning
**Goal**: User requests a meal plan (e.g., 4 days), app suggests recipes based on inventory/garden.

**Key Screens**:
- **Home/Dashboard Screen**:
  - Large "Plan Meals" button (primary CTA, full-width, green).
  - Quick stats: Current inventory summary (e.g., "5 staples low"), garden highlights.
  - Text Wireframe:
    ```
    [Header: App Logo | Settings Icon]
    
    Welcome back! Ready to plan?
    
    [Large Button: Plan 4-Day Meals]
    
    Garden Surplus: Tomatoes (3), Basil (handful)
    Pantry Staples: Milk (full), Butter (low)
    
    [Bottom Nav: Home | Plans | Inventory | List]
    ```

**Interactions**:
- Tap "Plan Meals" → Modal for days (default 4, slider or buttons: 3/4/7 days).
- App fetches inventory → Calls backend/LLM for suggestions (e.g., "Recipes using tomatoes and leftovers").
- Loading: Spinner with "Finding efficient recipes...".

### 2. Review and Select Recipes
**Goal**: User views suggested plan, adjusts if needed.

**Key Screens**:
- **Meal Plan Review Screen**:
  - Vertical scroll of days, each with recipe card (name, prep time, key ingredients, overlap indicator e.g., "Shares 70% with Day 1").
  - Edit button per day for LLM re-suggest.
  - Text Wireframe:
    ```
    4-Day Plan (Efficient: 80% ingredient reuse)
    
    Day 1: Tomato Basil Chicken (30min)
    - Ingredients: Chicken (pantry), Tomatoes (garden), etc.
    [Edit | Approve]
    
    Day 2: Chicken Soup (20min, uses leftovers)
    - Ingredients: Leftovers from Day 1, Veggies...
    [Edit | Approve]
    
    [Button: Next - Verify Inventory]
    [Back to Home]
    ```

**Interactions**:
- Swipe to approve/edit; tap edit → LLM prompt for alternatives (e.g., "Vegetarian option using these ingredients").
- Confirm plan → Proceed to verification.

### 3. Inventory Verification
**Goal**: User confirms what's on hand via categorical checklist; app adjusts needs.

**Key Screens**:
- **Categorical Checklist Screen**:
  - Tabs or accordion for locations: Pantry | Fridge | Freezer | Garden.
  - Checkboxes for ingredients (grouped, with quantities editable).
  - Large toggles for quick yes/no; search bar for staples.
  - Text Wireframe:
    ```
    Verify Ingredients (Plan needs 15 items)
    
    [Tab: Pantry] [Fridge] [Freezer] [Garden]
    
    Pantry:
    - [ ] Butter (1 stick) - Needed for Days 1-3
    - [ ] Flour (2 cups) - Needed for Day 4
    - [x] Milk (1L) - In stock
    
    [Search: Find ingredient...]
    [Button: Confirm & Generate List] (Disabled until 80% verified)
    ```

**Interactions**:
- Tap checkbox → Adjust quantity slider if partial; auto-mark based on last sync.
- Garden tab: Photo upload or manual entry for fresh produce.
- Progress bar shows verification %; hints like "Using garden tomatoes saves $5".
- Submit → Backend calculates deficits.

### 4. Generate and Optimize Shopping List
**Goal**: User gets a sorted, actionable list for the store.

**Key Screens**:
- **Shopping List Screen**:
  - List sorted by store layout (Produce first, then Dairy, etc.).
  - Checkboxes to mark as bought; quantities editable.
  - Export/share options (e.g., PDF, email).
  - Text Wireframe:
    ```
    Shopping List (Total: 12 items, ~$25)
    
    Produce:
    - [ ] Tomatoes (2) - For Day 1
    - [ ] Onions (3)
    
    Dairy:
    - [ ] Butter (1 stick)
    
    Meat:
    - [ ] Chicken (1lb)
    
    [Sort: By Store | By Aisle]
    [Button: Mark All Bought | Share List]
    [Back to Plan]
    ```

**Interactions**:
- Drag to reorder; integrate with device maps if possible (future).
- Check item → Remove from list, update plan costs.
- "Done Shopping" → Archive list, suggest next plan.

## Secondary Flows
- **Inventory Management**: Standalone screen to add/update items (scan barcode or manual). Flow: Home → Inventory Tab → Add Item (dropdown for location, expiry picker).
- **Recipe Library**: Search/browse saved recipes; integrate LLM for "Similar to this with my inventory".
- **Settings**: Offline mode toggle, garden setup, store layout customization.

## Mobile Considerations
- **Gestures**: Swipe to delete/archive, pull-to-refresh inventory.
- **Performance**: Lazy-load recipe details; pre-fetch common staples.
- **Edge Cases**: Low battery mode (reduce LLM calls); no internet (use cached plan).
- **Testing**: Simulate on mobile devices; ensure flows work in 5-10 seconds.

## TODOs
- Wireframe tools: Consider Figma prototypes (link in [context/](context/)).
- User Testing: Validate checklist UX with sample users.
- Integration: Link to backend endpoints in [design-system.md](design-system.md).

References: Align with mobile-first rules in [.kilocode/rules.md](../.kilocode/rules.md).