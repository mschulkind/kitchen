# Phase 3: The Planner Agent

**Goal**: Port the high-value "Phase 0" planning logic (Request -> Options -> Verification -> Final) into the interactive application.

## 3.1 Architecture Refactoring

The current `main.py` script is a linear CLI process. We need to break it into granular, stateless API interactions.

### Domain Services
- **`PlanningService`**: Orchestrates the flow.
- **`RecipeService`**: Search and retrieval.
- **`InventoryService`**: (Already built in Phase 1).

## 3.2 Planning Workflow Steps (API Endpoints)

### Step 1: Request
- **POST `/v1/plans/request`**
    - Input: `{ days: 4, focus: "Use up garden tomatoes", dining_dates: [...] }`
    - Action:
        1. Fetch current `pantry_items`.
        2. Construct context for LLM.
        3. Call LLM to generate 3-4 high-level "Plan Options".
    - Output: `{ options: [ { id: "A", title: "Garden Focus", description: "..." }, ... ] }`

### Step 2: Selection
- **POST `/v1/plans/select`**
    - Input: `{ option_id: "A" }` (or the full selected option object)
    - Action:
        1. Generate the full detailed plan (recipes for each day).
        2. Verify ingredients against DB.
    - Output: `DraftPlan` object with `days`, `recipes`, and `missing_ingredients`.

### Step 3: Verification (The "Categorical Checklist" 2.0)
- **UI**: The specific UI described in `ux-flow.md`.
- **Logic**:
    - User checks off items they actually have (handling database inaccuracies).
    - User swaps recipes or ingredients.
- **POST `/v1/plans/finalize`**
    - Input: `FinalizedPlan` (User confirmed state).
    - Action:
        1. Create `shopping_list` rows.
        2. Store the `meal_plan` in the DB.

## 3.3 Recipe Management & Scraping

- **Scraping Service**:
    - Port `firecrawl` logic to a background worker (e.g., Celery or just async FastAPI background task for now).
    - Endpoint: `POST /v1/recipes/import` -> `{ url: "..." }`.
- **Parsing**:
    - When a recipe is imported, use LLM to extract structured `ingredients` list for better shopping list aggregation.

## Definition of Done (Phase 3)
- [ ] "Plan Wizard" UI in the app.
- [ ] Backend logic can read from DB inventory instead of Markdown.
- [ ] LLM Prompt Engineering migrated and versioned in Python code.
- [ ] Ability to go from "I need food" to "Shopping List" entirely within the app.
