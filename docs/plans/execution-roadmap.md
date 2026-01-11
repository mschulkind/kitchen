# Execution Roadmap & Granular Phases

**Goal**: Split the 10 broad phases into atomic, testable execution chunks to ensure steady progress and avoid "big bang" integration issues.

## Phase 1: Foundation (The Skeleton)

*Est: 2-3 Weeks*

- [ ] **Phase 1A: Infra & Repo Setup**
  - [ ] Initialize Monorepo (`api`, `web`, `infra`).
  - [ ] Create `docker-compose.yml` (Supabase + App).
  - [ ] Configure Linting (Ruff, ESLint) & CI.
  - *Test*: `docker compose up` starts all services without error.

- [ ] **Phase 1B: Backend Core & DB**
  - [ ] Define `pantry_items` table in Supabase.
  - [ ] Implement `PantryService` (FastAPI) with CRUD.
  - [ ] Add `Pydantic` models for validation.
  - *Test*: `pytest` passes for all CRUD operations.

- [ ] **Phase 1C: Frontend Core & MVP UI**
  - [ ] Setup Expo + Tamagui + Router.
  - [ ] Create "Inventory List" Screen.
  - [ ] Connect to API (TanStack Query).
  - *Test*: Can add/delete an item in the Browser and see it persist.

## Phase 2: Recipe Engine (The Parser)

*Est: 2 Weeks*

- [ ] **Phase 2A: The Ingestor & DB**
  - [ ] Define `recipes` and `recipe_ingredients` tables.
  - [ ] Implement Firecrawl scraper wrapper.
  - *Test*: Can fetch a URL and save raw markdown.

- [ ] **Phase 2B: The Parser Logic**
  - [ ] Implement `IngredientParser` (Regex + LLM Adapter).
  - [ ] Implement `UnitRegistry` (Pint).
  - *Test*: "1 large onion" parses to `{qty: 1, unit: 'count', item: 'onion'}`.

## Phase 3: Delta Engine (The Brain)

*Est: 3 Weeks*

- [ ] **Phase 3A: The Comparator Logic**
  - [ ] Implement `calculate_missing(recipe, pantry)`.
  - [ ] Handle Unit Conversions (g vs ml).
  - *Test*: Unit tests for Surplus, Deficit, and Mismatch.

- [ ] **Phase 3B: The Verification UI**
  - [ ] Create "Assumption Engine" (User Audit object).
  - [ ] Create "Lazy Discovery" flow (Add item during verify).
  - *Test*: Backend returns correct "Assumptions" list.

## Phase 4: Visual Pantry (The Eyes)

*Est: 1 Week*

- [ ] **Phase 4A: Vision Pipeline**
  - [ ] Implement `VisionService` (Gemini Adapter).
  - [ ] Connect Mobile Camera -> Supabase Storage.
  - *Test*: Upload image -> Receive JSON inventory list.

- [ ] **Phase 4B: Staging UI**
  - [ ] Create "Review Scan" Screen.
  - [ ] Implement "Commit to Pantry" action.
  - *Test*: Full flow from Photo to DB Record.

## Phase 5: Planner Core (The Director)

*Est: 3 Weeks*

- [ ] **Phase 5A: Generator Logic**
  - [ ] Implement `PlanGenerator` (LLM-driven themes).
  - [ ] Ensure **Structured JSON** output for generated recipes.
  - *Test*: Generator returns 3 valid Options.

- [ ] **Phase 5B: Planner UI**
  - [ ] Create "Adventure Card" Selection Screen.
  - [ ] Create 4-Day Plan View.
  - *Test*: User can select a theme and see a Plan.

## Phase 6: Slot Machine (The Refiner)

*Est: 1-2 Weeks*

- [ ] **Phase 6A: Refinement Logic**
  - [ ] Update DB for granular slots (Main/Side).
  - [ ] Implement `RefinerService` (Re-roll with directive).
  - *Test*: "Make it spicy" returns a spicy alternative.

- [ ] **Phase 6B: Slot Machine UI**
  - [ ] Implement Locking & Spinning UI.
  - *Test*: Lock "Main", Spin "Side" -> Only Side changes.

## Phase 7: Shopping List (The Output)

*Est: 1 Week*

- [ ] **Phase 7A: Aggregation Engine**
  - [ ] Implement `Plan -> Shopping List` logic (using Delta Engine).
  - [ ] Merge duplicates.
  - *Test*: 2 Recipes needing Onions result in 1 List Item.

- [ ] **Phase 7B: Sync & UI**
  - [ ] Create Checklist UI.
  - [ ] Connect Supabase Realtime.
  - *Test*: Checkbox state syncs between two browser tabs.

## Phase 8: Store Intel (The Map)

*Est: 1 Week*

- [ ] **Phase 8A: Scraper & Data**
  - [ ] Reverse-engineer Shaws API.
  - [ ] Create `store_aisles` table.
  - *Test*: Can fetch aisle for "Milk".

- [ ] **Phase 8B: Sorting Logic**
  - [ ] Sort Shopping List by Aisle Index.
  - *Test*: Produce appears before Dairy.

## Phase 9: Voice (The Ear)

*Est: 1 Week*

- [ ] **Phase 9A: Webhook & NLP**
  - [ ] Implement `/hooks/add-item`.
  - [ ] Implement NLP Parser ("Add X and Y").
  - *Test*: `POST {text: "milk"}` adds Milk to list.

## Phase 10: Chef's Companion (The Hand)

*Est: 1 Week*

- [ ] **Phase 10A: Cooking Mode**
  - [ ] Implement "Copy for AI" Prompt Builder.
  - [ ] Implement "Mark as Cooked" logic.
  - *Test*: Copy button puts valid prompt in clipboard.

---
**Total Phases**: 20
**Total Estimated Time**: ~12-16 Weeks (at casual pace)
