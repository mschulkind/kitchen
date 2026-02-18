# Design System

This document outlines the technical design decisions for the Personalized Dinner & Shopping App, including frameworks, libraries, architecture patterns, data models, and integration choices. It serves as a living reference for the tech stack and unresolved decisions. Reference [.kilocode/rules.md](../.kilocode/rules.md) for high-level guidelines.

## Core Technologies & Architectural Decisions

- **Database**: **Supabase (PostgreSQL)**
  - **Reasoning**: Chosen for its robust realtime sync, built-in authentication, row-level security, and excellent client libraries for both our React/TS frontend and Python/FastAPI backend. This aligns with our need for rapid development of collaborative features like shared shopping lists and inventories.
  - **Reference**: See [`../docs/db-research.md`](../docs/db-research.md) for a detailed comparison.
  
- **Authentication**: **Supabase Auth (Google Social Login)**
  - **Reasoning**: Exclusively using Google Social Login simplifies the user experience for our mobile-first audience, reduces development overhead, and allows for easy profile data pre-filling (name, avatar), which benefits collaborative features. This decision aligns with the principle of minimizing friction for users. For full details, see the decision log at [`decisions/phase-1.5/auth-and-presence.md`](decisions/phase-1.5/auth-and-presence.md).
  
- **Deployment**:
  - **Frontend**: *Pending (Vercel recommended)*
  - **Backend**: *Pending (Heroku or similar recommended)*

## Local Development & Testing Strategy

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
    - Notes: Poll or realtime subscribe. Push notifications are deferred until post-MVP as per the decision in [`decisions/phase-1.5/notifications.md`](decisions/phase-1.5/notifications.md).

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
- **Prompt Templates**: A standardized set of prompt examples has been finalized. For full details, see the decision log at [`decisions/phase-1/llm-prompts.md`](decisions/phase-1/llm-prompts.md).
  - **1. Basic Meal Plan Generation**:

    ```
    "You are a meal planning assistant. Generate a {days}-day meal plan for {servings} people, using as many of these pantry items as possible: {pantry_list} and garden items: {garden_list}. Prioritize ingredient reuse and simple recipes (under 45min prep). Exclude {diet_restrictions}. Output a valid JSON object with the structure: {days: [{day: 'Day 1', recipe_name: string, ingredients_used: string[], new_shopping_list_items: string[], instructions: string}]}"
    ```

  - **2. Recipe Substitution & Customization**:

    ```
    "You are a recipe customization assistant. The user wants to make '{recipe_name}' which requires {full_ingredients_list}. They only have these items from their pantry: {available_pantry}. Suggest logical substitutions for the missing ingredients. Consider dietary preferences: {prefs}. Output a valid JSON object with the structure: {original_recipe: string, substitutions: [{original: string, substitute: string, rationale: string}], adjusted_instructions: string, nutritional_notes: string}"
    ```

  - **3. Low-Waste Plan with Leftovers**:

    ```
    "You are a waste-reduction assistant. Create a 3-day meal plan that minimizes food waste. Use leftovers from these previous meals: {previous_meals} and items from the current pantry: {pantry_list}. Focus on {cuisine_pref} recipes and adhere to {diet_prefs}. Output a valid JSON object with the structure: {days: [{day: string, recipe_name: string, uses_leftovers_from: string[], shopping_list_additions: string[]}]}"
    ```

  - **4. Garden Surplus Optimization**:

    ```
    "You are a garden-to-table assistant. Suggest 2-3 simple recipes that make the most of a garden surplus. The user has: {garden_items_with_quantities}. Supplement with common pantry staples: {pantry_staples}. Respect these dietary restrictions: {diet_restrictions}. Output a valid JSON object with the structure: {recipes: [{recipe_name: string, key_garden_ingredients: string[], full_ingredient_list: string[], instructions: string, prep_time_minutes: int}]}"
    ```

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

**Offline Handling**: The application will employ an optimistic UI strategy with a client-side sync queue to ensure offline functionality. For the MVP, conflicts will be managed using a **Last-Write-Wins (LWW)** approach. A future migration to **Conflict-Free Replicated Data Types (CRDTs)** is planned for V2 to support more advanced collaboration. This two-phased approach is detailed in the [`conflict-resolution-and-offline.md` decision log](decisions/phase-1.5/conflict-resolution-and-offline.md).

- **Queue & Sync Flow**: Mutations are queued in **IndexedDB** during offline periods. A background task processes the queue upon reconnection, replaying actions and invalidating the local cache on success.
- **Mobile Optimization**: Use Expo's AsyncStorage for preferences and tokens; display a non-intrusive offline indicator in the UI.
- **Error Resolution**: If sync conflicts occur under the LWW model, the latest server state will prevail. For critical conflicts, a user notification system may be considered in later iterations.
- **Reference**: See [hosting.md](hosting.md) for full sync mechanisms and diagrams, and the decision log for the complete rationale.

**Migration Path**: The initial implementation will rely on Supabase's default behaviors, which align with LWW. The data models and API will be designed to facilitate a future transition to an operation-based CRDT model.

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
- **Concurrent Editing & Conflict Resolution**: For the MVP, the system will use a **Last-Write-Wins (LWW)** strategy. The last update to reach the server will be considered the canonical version. For V2, a migration to **CRDTs** is planned to handle concurrent edits more gracefully. This decision is fully documented in [`decisions/phase-1.5/conflict-resolution-and-offline.md`](decisions/phase-1.5/conflict-resolution-and-offline.md). On mobile, simple conflict alerts (e.g., "List changed by another user—reload?") with big confirm buttons will be used.
- **Invites & Access**: Auth-based invites via Google account integration, leveraging the simplicity of a single sign-on provider. Role-based permissions (owner, editor, viewer) will be stored in Supabase tables.
- **Notifications**: *Post-MVP feature.* Push notifications for changes (e.g., "Item added to shared inventory") will use Supabase Edge Functions, optimized for mobile with Expo Notifications. The decision to defer this feature is documented in [`decisions/phase-1.5/notifications.md`](decisions/phase-1.5/notifications.md).
- **Reference**: For a detailed breakdown of the realtime architecture, channel design, and implementation pseudocode, see the full decision log at [`decisions/phase-1.5/realtime-integration.md`](decisions/phase-1.5/realtime-integration.md).

This architecture extends core features from brief.md (e.g., shared inventory verification checklists) to multiuser without overcomplicating the UX.

## Testing Strategy

Align with TDD practices from [.kilocode/rules/tdd-practices.md](../.kilocode/rules/tdd-practices.md): Test-first, fast suites (&lt;1s), and aim for 80%+ coverage on critical paths. All tests will run against a local Supabase stack to ensure a production-parity environment.

The testing strategy is phased to align with the development roadmap, prioritizing rapid feedback during web development and comprehensive native testing for the mobile release. For full details, see the complete strategy at [`decisions/phase-1.5/multiuser-testing.md`](decisions/phase-1.5/multiuser-testing.md).

### Phase 1: PWA / Web App Development

- **Focus**: Manual testing and automated component/integration tests (Vitest/RTL).
- **Environment**: Desktop web browsers.
- **Manual Tests**: All multiuser scenarios (invites, live edits, offline sync) will be executed on the web PWA for quick iteration.
- **Automated Tests**: Unit and integration tests will cover shared logic. E2E tests are deferred to the native phase.

### Phase 2: Native Android App Development

- **Focus**: Automated End-to-End (E2E) testing and manual regression.
- **Environment**: Android Emulator and physical devices.
- **Automated E2E Tests**: A full **Detox test suite** will be implemented to run against the Android app, automating critical multiuser and offline flows to ensure native stability.

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
  - **Mobile Focus**: Detox for React Native/Expo (simulate two devices for sync, offline toggle). E2E tests will be implemented during the native Android development phase.
  - **Tools**: Detox (E2E mobile); Playwright if web PWA testing needed.
  - **Goals**: Cover top 5 flows from brief.md (planning, verification, shopping); run on CI with device matrix (Android); &lt;30s suite.

**Overall**: CI via GitHub Actions (lint → unit → integration → E2E on PR); coverage report with threshold gates. Mock LLM with fixed responses for determinism; test offline with network throttling. The full multiuser testing plan is detailed in [`decisions/phase-1.5/multiuser-testing.md`](decisions/phase-1.5/multiuser-testing.md).

TODO: Add test setup to Procfile.dev (e.g., `test: pytest + vitest`); integrate with hosting CI/CD.

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
