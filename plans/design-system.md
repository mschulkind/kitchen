# Design System

This document outlines the technical design decisions for the Personalized Dinner & Shopping App, including frameworks, libraries, architecture patterns, data models, and integration choices. It serves as a living reference for the tech stack and unresolved decisions. Reference [.kilocode/rules.md](../.kilocode/rules.md) for high-level guidelines.

### Core Technologies & Architectural Decisions

- **Database**: **Supabase (PostgreSQL)**
  - **Reasoning**: Chosen for its robust realtime sync, built-in authentication, row-level security, and excellent client libraries for both our React/TS frontend and Python/FastAPI backend. This aligns with our need for rapid development of collaborative features like shared shopping lists and inventories.
  - **Reference**: See [`../docs/db-research.md`](../docs/db-research.md) for a detailed comparison.
  
- **Authentication**: **Supabase Auth (Google Social Login)**
  - **Reasoning**: Exclusively using Google Social Login simplifies the user experience for our mobile-first audience, reduces development overhead, and allows for easy profile data pre-filling (name, avatar), which benefits collaborative features. This decision aligns with the principle of minimizing friction for users. For full details, see the decision log at [`decisions/phase-1.5/auth-and-presence.md`](decisions/phase-1.5/auth-and-presence.md).
  
- **Deployment**:
  - **Frontend**: *Pending (Vercel recommended)*
  - **Backend**: *Pending (Heroku or similar recommended)*

### Local Development & Testing Strategy
- **Environment**: Utilize the Supabase CLI to run a full local stack (PostgreSQL, Auth, Storage) via Docker.
- **Data Seeding**: Implement scripts to seed the local database for consistent test states.
- **Workflow**: Automated tests will reset the database (`supabase db reset`) before runs to ensure isolation and prevent test contamination.
- **Goal**: Achieve production parity in the local environment, enabling thorough testing of all features, including realtime sync, offline capabilities, and security policies.

## Architecture Patterns
- **Overall**: Client-server architecture with backend API for core logic (meal planning, inventory). Frontend consumes API; consider offline-first with local storage/Service Workers for PWA.
- **Modular Design**: Separate concerns – e.g., recipe module, inventory module, LLM agent module.
- **API Design**: RESTful endpoints (e.g., /meals/plan, /inventory/verify) with JSON payloads. Use OpenAPI for docs. FastAPI for backend: auto-docs at /docs, Pydantic validation, async for realtime ties. Auth via Supabase JWT in Authorization header; RLS for data access. Error responses: JSON { "error": str, "details": dict } with HTTP codes (400 Bad Request, 401 Unauthorized, 500 Internal).

  - **POST /api/meal-plan**: Generate/verify meal plan.
    - Params: Body JSON { "days": int (default 4), "diet_prefs": list[str], "pantry_ids": list[int], "garden_items": list[str] }.
    - Response: 200 { "plan": MealPlan schema, "suggested_recipes": list[Recipe], "optimization_score": float }.
    - Auth: Required (token); scopes: user or shared plan owner.
    - Errors: 400 { "error": "Invalid diet prefs" }; 500 { "error": "LLM unavailable - fallback used" }.
    - Notes: Calls LLM prompts (from LLM Integration); applies ingredient-optimization for subs.

  - **GET /api/inventory**: Fetch user/shared inventory for verification.
    - Params: Query ?location=pantry&shared_id=uuid (optional for multiuser).
    - Response: 200 { "items": list[PantryItem], "categories": dict[location: list] }.
    - Auth: Required; RLS filters by user/memberships.
    - Errors: 401 { "error": "Unauthorized access to shared inventory" }.
    - Notes: Cached for offline; realtime subscription for live updates.

  - **PUT /api/inventory/verify**: Update verification for plan.
    - Params: Body JSON { "item_id": int, "available": bool, "quantity": float, "sub_used": str (optional) }.
    - Response: 200 { "updated_item": PantryItem, "plan_adjustments": dict (e.g., "added_to_shopping": list) }.
    - Auth: Required; optimistic update with queue (offline sync).
    - Errors: 409 { "error": "Conflict - another user updated" } (LWW resolution).
    - Notes: Triggers realtime broadcast; ties to verification flow in ux-flow.md.

  - **POST /api/shopping-list**: Generate/optimize list from verified plan.
    - Params: Body JSON { "plan_id": int, "store_layout": str (default "standard") }.
    - Response: 200 { "list": list[ShoppingListItem], "total_cost": float, "categories": dict }.
    - Auth: Required.
    - Errors: 400 { "error": "No verified plan" }.
    - Notes: Sorted by category (ux-flow.md); realtime for shared lists.

  - **PUT /api/shopping-list/{list_id}**: Update shared list (add/check/reorder).
    - Params: Path list_id, Body JSON { "action": "add|check|reorder", "items": list[dict] }.
    - Response: 200 { "updated_list": list[ShoppingListItem] }.
    - Auth: Required; role check for editor.
    - Errors: 403 { "error": "Viewer cannot edit" }; 409 conflict on reorder.
    - Notes: Broadcast via realtime channel; optimistic for offline.

  - **GET /api/notifications**: Fetch user notifications (for in-app).
    - Params: Query ?type=push|inapp&limit=20.
    - Response: 200 { "notifications": list[dict {message, resource_id, timestamp}] }.
    - Auth: Required.
    - Errors: 401 unauthorized.
    - Notes: Poll or realtime subscribe; tie to notifications.md Edge Functions.

  - **General Best Practices**: All endpoints async (FastAPI); rate limit (5/min free); CORS for frontend; OpenAPI tags for grouping (e.g., "meal-planning", "inventory"). PWA: Cache GETs with service worker; queue PUT/POST offline.

TODO: Implement in backend; test with Postman/Supabase mocks.

- **Data Flow**: User input → Backend logic (with LLM for suggestions) → UI updates. Favor reactive updates in React.
- TODO: Microservices vs. monolith? Likely monolith for personal app simplicity.

## Data Models
- **PantryItem**:
  - Fields: id, name, location (enum: Pantry, Fridge, Freezer, Garden), quantity, unit, expiry_date, notes.
  - Usage: Tracks user inventory; queried for recipe matching.
- **ShoppingListItem**:
  - Fields: id, name, quantity, unit, category (enum: Produce, Dairy, Meat, etc.), priority (based on recipe needs).
  - Usage: Generated post-verification, sorted by store layout.
- **Recipe**:
  - Fields: id, name, ingredients (list of {name, quantity, unit, category}), instructions, cuisine, prep_time, servings.
  - Usage: Stored locally or fetched via LLM; optimized for ingredient overlap.
- **MealPlan**:
  - Fields: days (array of {date, recipe_id, notes for leftovers}).
  - Usage: Generated plan favoring efficiency.
- **Substitutions**:
  - Fields: id, original_ingredient, substitute_options (array of {sub_name, category (e.g., protein, fat), nutritional_notes}), user_custom (bool).
  - Usage: Pre-defined or user-added map for algorithm substitutions; queried to suggest pantry-available swaps.
- TODO: Define schemas in Pydantic; consider relationships (e.g., Recipe to Ingredients). Reference [decisions/phase-1/ingredient-optimization.md](decisions/phase-1/ingredient-optimization.md) for algorithm integration.

## LLM Integration
- **Provider**: OpenAI GPT (e.g., GPT-4o-mini for cost-efficiency) or local Ollama for privacy/offline.
  - Prompts: Structured for recipe generation (e.g., "Suggest 4-day plan using [ingredients], prioritizing [garden items] and leftovers").
- **Usage Patterns**: 
  - Dynamic suggestions: Input current inventory → Output recipe ideas.
  - Customization: Modify recipes on-the-fly (e.g., substitute ingredients).
- **Error Handling**: Fallback to rule-based logic if LLM fails or unavailable offline (e.g., use ingredient-optimization algorithm for pantry matching/substitutions); cache responses in IndexedDB for retry; log failures without user disruption (e.g., show "Using cached recipes").
- **Prompt Templates**: 3-5 structured templates for key use cases, using JSON output for easy parsing. Prompts include variables from inventory (PantryItem/Recipe models), user prefs (diet, servings), and brief.md goals (efficiency, waste reduction). Offline: Fallback to pre-defined recipe DB or heuristics.

  - **Template 1: Basic Meal Plan Generation** (4-day plan from pantry/garden)
    Prompt: "Generate a 4-day meal plan for {servings} people, using as many of these pantry items as possible: {pantry_list} and garden items: {garden_list}. Prioritize ingredient reuse and simple recipes (under 45min prep). Exclude {diet_restrictions}. Output JSON: {days: [{day: 'Day 1', recipe_name: str, ingredients_used: list, new_needed: list, instructions: str}]}"
    Expected Output: JSON array of days with recipes optimized for overlap (e.g., Day 1 uses tomatoes from garden, Day 2 leftovers); if offline, fallback to scored recipes from ingredient-optimization.
    Error Handling: If no valid plan, return rule-based top-4 from pantry match score.

  - **Template 2: Recipe Substitution & Customization**
    Prompt: "Suggest substitutions for missing ingredients in this recipe: {recipe_name} requiring {full_ingredients}. User has {available_pantry}. Dietary: {prefs}. Use categories (protein/fat/veg) for matches. Output JSON: {original_recipe: str, substituted_ingredients: dict (original: sub), adjusted_instructions: str, nutritional_notes: str}"
    Expected Output: Adjusted recipe with swaps (e.g., butter -> olive oil, same fat category); tie to Substitutions model for validation.
    Error Handling: Offline fallback to pre-defined substitutions table query.

  - **Template 3: Low-Waste Plan with Leftovers**
    Prompt: "Create a 3-day meal plan minimizing waste: Use leftovers from {previous_meals} and current {pantry_list}. Focus on {cuisine_pref} recipes. Optimize for {diet_prefs}. Output JSON: {days: [{day: str, recipe: str, uses_leftovers: list, reduces_waste_by: str, shopping_adds: list}]}"
    Expected Output: Plan chaining leftovers (e.g., Day 1 chicken → Day 2 soup); quantify savings (e.g., "Uses 80% pantry").
    Error Handling: If LLM timeout, use heuristic chaining from ingredient-optimization (score recipes by leftover match).

  - **Template 4: Garden Surplus Optimization**
    Prompt: "Suggest 2-3 recipes using garden surplus: {garden_items} (quantities: {garden_quantities}), supplemented by {pantry_staples}. {diet_restrictions}. Keep simple for busy users. Output JSON: {recipes: [{name: str, ingredients: list (garden_used, pantry_used), instructions: str, prep_time: int}]}"
    Expected Output: Recipes highlighting garden (e.g., "Tomato Salad" using 3 tomatoes); prioritize fresh/seasonal.
    Error Handling: Offline: Local recipe filter by garden tags.

  - **Template 5: Dietary Personalization**
    Prompt: "Adapt a {base_recipe} for {diet_type} (e.g., low-carb, vegan), using {user_pantry}. Suggest alternatives if needed. Output JSON: {adapted_recipe: str, substitutions: dict, nutritional_summary: str (calories, macros)}"
    Expected Output: Customized version (e.g., low-carb swap rice for cauliflower); include macros for health focus.
    Error Handling: Fallback to category-based subs from ingredient-optimization if no LLM.

TODO: Implement prompts in backend (FastAPI endpoint); test with mock responses; add rate limiting (e.g., 10 calls/day free tier).

## Ingredient Optimization
This section details the LLM-powered algorithm for matching recipes to the user's pantry, suggesting substitutions, and dynamically generating meal ideas. This approach prioritizes creating an intelligent and flexible user experience, aligning with the core vision of the app. For a full breakdown of the logic, prompt engineering, and rationale, see the detailed decision log.

### Key Logic
- **Dynamic Generation**: Instead of a fixed heuristic system, the app will use a large language model (LLM) to generate recipe and substitution suggestions based on the user's real-time context (pantry, preferences, query).
- **Prompt Engineering**: The core of the logic resides in carefully constructed prompts that guide the LLM to return structured, reliable JSON data.
- **Integration**: The LLM is called via a backend API endpoint, which processes the user's context and formats the response for the UI. The system includes fallbacks for offline use or API failures.
- **Reference**: The complete algorithm flow, prompt structure, and rationale are documented in [`decisions/phase-1/ingredient-optimization.md`](decisions/phase-1/ingredient-optimization.md).

This algorithm ensures efficient, offline-capable optimization using local data models, with realtime sync via Supabase for shared inventories.

## Database

With the requirement for realtime multiuser collaboration (e.g., shared meal plans, inventory, and shopping lists across devices), **Supabase (PostgreSQL-based with built-in realtime subscriptions via WebSockets)** is the selected database.

**Pros**: Instant sync across users/devices using client SDKs (JS/Python); integrated auth for user management; supports offline mode with optimistic updates and automatic conflict resolution on reconnect; scalable for multiuser without heavy setup.
**Cons**: Cloud dependency, but offers free tier for dev/testing; potential latency for very remote users, mitigated by edge functions.

**Offline Handling** (Expanded): Use Supabase's client-side caching for queries (e.g., from()...select() caches recent data); implement optimistic UI updates (local state mutation before DB write, rollback on error). For mutations, queue in IndexedDB (Dexie.js for structured store) or Expo AsyncStorage (mobile key-value); on reconnect (navigator.onLine or Expo NetInfo), replay queue with retries, applying LWW for conflicts (conflict-resolution-and-offline). Cache critical models (PantryItem, MealPlan) for offline view/edit; sync notifications queued if offline.

- **Queue & Sync Flow**: Mutations added to queue on fail/offline; background task (Expo TaskManager) replays on online, invalidates cache on success, broadcasts via realtime channels.
- **Mobile Optimization**: AsyncStorage for prefs/tokens; limit queue to 50 items to avoid bloat; UX: Offline indicator in header, sync progress bar.
- **Error Resolution**: If sync conflicts, alert with diff (e.g., "Server has newer inventory—merge?"); fallback to local-only mode if persistent.
- **Reference**: See [hosting.md](hosting.md) for full sync mechanisms and diagrams.

**Migration Path**: Start with Supabase from scratch for simplicity; hybrid with local IndexedDB for pure offline fallback if needed.

This enables realtime features without sacrificing dev speed, leveraging Supabase's JS SDK for quick integration in our React Native/Expo frontend.

## Collaboration Architecture

To support multiuser realtime collaboration while keeping the app mobile-friendly and usable:

- **Realtime Features**: Use Supabase Realtime (WebSockets) for live updates. Subscriptions are managed through dedicated channels for key resources to ensure efficient data sync.
  - **Channels**:
    - `shared-list:{id}` for `shopping_list_items`
    - `meal-plan:{id}` for `meal_plan_recipes` and `meal_plans`
    - `inventory:{id}` for `inventory_items`
- **Optimistic Updates & Offline Handling**: The frontend will use React Query (TanStack Query) for optimistic UI updates, providing a seamless experience even with poor connectivity. Actions taken offline are queued in IndexedDB and synced upon reconnection.
- **User Presence**: Track online status via Supabase presence channels (e.g., show "User X is editing" indicators with large, touch-friendly avatars).
- **Concurrent Editing & Conflict Resolution**: Implement last-write-wins for simple cases (e.g., timestamped updates). On mobile, show simple conflict alerts (e.g., "List changed by another user—reload?") with big confirm buttons.
- **Invites & Access**: Auth-based invites via Google account integration, leveraging the simplicity of a single sign-on provider. Role-based permissions (owner, editor, viewer) will be stored in Supabase tables.
- **Notifications**: Push notifications for changes (e.g., "Item added to shared inventory") using Supabase Edge Functions, optimized for mobile with Expo Notifications.
- **Reference**: For a detailed breakdown of the realtime architecture, channel design, and implementation pseudocode, see the full decision log at [`decisions/phase-1.5/realtime-integration.md`](decisions/phase-1.5/realtime-integration.md).

This architecture extends core features from brief.md (e.g., shared inventory verification checklists) to multiuser without overcomplicating the UX.

## Testing Strategy
Align with [.kilocode/rules.md](../.kilocode/rules.md) TDD practices: Test-first, fast suites (<1s), 80%+ coverage on critical paths (e.g., LLM prompts, ingredient-optimization, realtime sync, offline). Structure tests in tests/ mirroring src/; colocate frontend tests. Use mocking for externalities (LLM, Supabase) to ensure speed. Reference [decisions/phase-1.5/multiuser-testing.md](decisions/phase-1.5/multiuser-testing.md) for realtime/multiuser specifics; align with brief.md reliability for core flows (meal planning, verification, shopping).

### Phased Checklist
- **Unit Tests** (Broad base, 70% total coverage):
  - **Backend (pytest)**: Test individual functions (e.g., ingredient-optimization scoring, LLM prompt formatting). Mock dependencies (OpenAI, Supabase client). Example: assert pantry_match_score(pantry, recipe) == expected.
  - **Frontend (Vitest)**: Test components/logic in isolation (e.g., verification checkbox updates state, drag-reorder in shopping list). Use RTL for user interactions.
  - **Tools**: pytest (backend, fixtures for DB mocks); Vitest + jsdom (frontend).
  - **Goals**: 90% coverage on algorithm/LLM; run in <0.5s with parallel.

- **Integration Tests** (Middle layer, 20% coverage):
  - **Scope**: API endpoints + component interactions (e.g., POST /meal-plan calls LLM and returns optimized plan; realtime channel subscription updates UI on mock event).
  - **Multiuser**: Mock Supabase for concurrent edits (e.g., two clients add item, assert LWW resolution).
  - **Offline**: Test queue add/sync with mocked navigator.onLine.
  - **Tools**: pytest with TestClient for FastAPI; RTL + MSW for frontend API mocks.
  - **Goals**: 80% on endpoints (ux-flow.md flows); verify auth/RLS (e.g., unauthorized 401).

- **E2E Tests** (Top, 10% coverage, critical flows only):
  - **Scope**: Full user journeys (e.g., initiate plan → verify inventory → generate list; multiuser invite → live edit → conflict alert).
  - **Mobile Focus**: Detox for React Native/Expo (simulate two devices for sync, offline toggle).
  - **Tools**: Detox (E2E mobile); Playwright if web PWA testing needed.
  - **Goals**: Cover top 5 flows from brief.md (planning, verification, shopping); run on CI with device matrix (iOS/Android); <30s suite.

**Overall**: CI via GitHub Actions (lint → unit → integration → E2E on PR); coverage report with threshold gates. Mock LLM with fixed responses for determinism; test offline with network throttling. Link to multiuser-testing.md for realtime details.

TODO: Add test setup to Procfile.dev (e.g., test: pytest + vitest); integrate with hosting CI/CD.

## Pending Decisions
- **Authentication**: Decision finalized to use **Google Social Login exclusively** via Supabase Auth. See the [`auth-and-presence.md` decision log](decisions/phase-1.5/auth-and-presence.md) for details.
- **Deployment Tech**: See [hosting.md](hosting.md) for details.
- **Offline Capabilities**: Implement IndexedDB for inventory; sync on reconnect via Supabase.
- **Performance**: Caching strategies (Supabase built-in); optimize LLM calls.
- **Security**: Sanitize LLM inputs/outputs; row-level security in Supabase.

## References
- Project [brief.md](brief.md) for feature alignment.
- [.kilocode/rules.md](../.kilocode/rules.md) for TDD and directory rules.

TODO: Update as decisions are finalized; track changes with git commits.
