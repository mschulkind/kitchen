# Kitchen Project: Central Development Plan

## Overview

This is the central planning document for moving the Kitchen project from its current "Phase 0" (Markdown & Script-based workflow) to a fully functional, AI-integrated web and mobile application.

The core goal is to preserve the high-quality "Agent-driven" planning experience while reducing the friction of data entry (inventory management) and plan execution (shopping/cooking).

## Architecture & Tech Stack

To support the "Heavy AI" requirements (planning, vision) alongside "Realtime App" requirements (sync, lists), we will use a hybrid stack:

### 1. Frontend: Expo (React Native)
- **Why**: Targets Web, iOS, and Android from a single codebase.
- **Role**: The UI layer. Handles user interactions, camera access (for pantry scan), and offline sync.
- **Key Libs**: `expo-router` (navigation), `tanstack-query` (data fetching), `gluestack-ui` or `tamagui` (UI components).

### 2. Backend: Supabase + Python (FastAPI/Modal)
- **Supabase**: The "State" layer.
    - **PostgreSQL**: Stores Pantry, Recipes, Plans, Users.
    - **Auth**: User management.
    - **Realtime**: Instant updates for shared shopping lists.
- **Python Service (The "Chef's Brain")**:
    - **Why**: Python is the native language of AI. Complex planning logic and Vision API handling are best done here, not in Edge Functions or JS.
    - **Role**:
        - Runs the "Phase 0" planning logic (Request -> Options -> Verification -> Final).
        - Handles Image Processing (Pantry Vision).
        - Scrapes recipes (Firecrawl/BeautifulSoup).
    - **Deployment**: Can be hosted on Render/Railway (as a web service) or Modal (serverless GPU/AI functions).

---

## Development Phases

### Phase 1: The Foundation (Repo & Data Layer)
**Goal**: Establish the app shell and move "Stock Lists" from Markdown to Database.

*   [ ] **1.1: Project Skeleton**: Initialize Expo `src/mobile` and Python `src/api` in the monorepo.
*   [ ] **1.2: Supabase Setup**:
    *   Define DB Schema for `pantry_items`, `users`, `households`.
    *   Setup Row Level Security (RLS).
*   [ ] **1.3: Data Migration Script**: Write a script to parse existing `phase0_flow/stock_lists/*.md` files and seed the Supabase DB for the dev user.
*   [ ] **1.4: Basic Inventory UI**: A simple list view in the app to Add/Remove/Edit items, synced with Supabase.

### Phase 2: Visual Pantry (The "Magic" Feature)
**Goal**: Removing the friction of inventory management using LLM Vision.

*   [ ] **2.1: Image Upload Pipeline**: App takes a photo -> Uploads to Supabase Storage -> Triggers Python Service.
*   [ ] **2.2: Vision Agent**:
    *   Integrate GPT-4o / Claude 3.5 Sonnet / Gemini 1.5 Pro.
    *   Prompt engineering: "Identify all food items, brands, and approximate fill levels. Return JSON."
*   [ ] **2.3: Verification UI**:
    *   Show the user the photo alongside the "Detected Items" list.
    *   Allow quick "Confirm", "Edit", or "Reject" actions.
*   [ ] **2.4: Categorization Logic**: Auto-tag items (Produce, Dairy, Pantry) using the LLM logic to sort them into the correct virtual storage locations.

### Phase 3: The Planner Agent (Porting Phase 0)
**Goal**: Move the "Markdown Agent" logic into a proper API workflow.

*   [ ] **3.1: Plan Request API**: Endpoint `POST /plans` accepting preferences (days, focus).
*   [ ] **3.2: Option Generator**: Port the logic that reads `stock_lists` (now from DB) and generates 4 summary options.
*   [ ] **3.3: Selection UI**: A "Chat-like" or "Card" interface where users pick Option A, B, C, or D.
*   [ ] **3.4: Verification & Generation**:
    *   Backend generates the full shopping list and recipes.
    *   Frontend renders the result (not as a markdown file, but as interactive native views).

### Phase 4: Execution & Realtime
**Goal**: Making the plan usable in the store and kitchen.

*   [ ] **4.1: Interactive Shopping List**: Checkboxes, sorting by aisle (LLM enriched category).
*   [ ] **4.2: Cooking View**: "Step-by-step" mode for recipes.
*   [ ] **4.3: Consumption**: When a recipe is marked "Cooked", auto-decrement ingredients from the Pantry DB.

---

## Open Questions & Decisions

### 1. Vision API Cost & Latency
*   **Question**: Sending 5 high-res photos of a pantry to GPT-4o is expensive (~$0.01-$0.03 per call) and slow (5-10s).
*   **Mitigation**:
    *   Compress images before upload.
    *   Use "Flash" or "Haiku" models for initial rough passes?
    *   Is the user willing to wait 30s for a "Pantry Scan"? (Likely yes, if it saves typing 50 items).

### 2. Python Hosting
*   **Decision**: Where does the FastAPI service live?
    *   *Option A*: **Render/Railway**. Keeps it simple, always on.
    *   *Option B*: **Supabase Edge Functions (Python)**. Recently released, but might be limited for heavy agentic logic or scraping.
    *   *Recommendation*: Start with a simple Container execution (Docker) that can be deployed anywhere (Render is easy).

### 3. Recipe Storage Format
*   **Current**: Markdown files.
*   **Future**:
    *   Keep Markdown strings in a JSON column?
    *   Parse into structured SQL (Instructions table, Ingredients table)?
    *   *Recommendation*: Hybrid. Store the "Source Markdown" for LLM context, but parse "Ingredients" into a structured JSONB column for the shopping list generator to query against.

### 4. Scraping Strategy
*   **Current**: Local Firecrawl.
*   **Future**:
    *   Need a reliable remote scraper.
    *   Self-host Firecrawl or use a service API?
    *   Impacts the "Add Recipe from URL" feature in the app.

## Next Steps

1.  **Refine this Plan**: Review dependencies and agree on the "Hybrid Stack" approach.
2.  **Repo Structure**: reorganizing to support `src/web` and `src/api` side-by-side.
3.  **Prototype Vision**: Write a quick Python script to test "Photo -> Ingredients JSON" quality with current LLMs.
