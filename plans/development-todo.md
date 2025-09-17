# Development TODO: Fleshing Out Planning Phase

## Table of Contents
- [Phases](#phases)
- [Phase 0: Core Decisions](#phase-0-core-decisions)
- [Phase 1: Core Decisions (Design System Foundations)](#phase-1-core-decisions-design-system-foundations)
- [Phase 1.5: Realtime Collaboration Setup](#phase-15-realtime-collaboration-setup)
- [Phase 3: Infrastructure Setup (Hosting and Integration)](#phase-3-infrastructure-setup-hosting-and-integration)
- [Phase 4: Implementation Prep (Finalizing for Coding)](#phase-4-implementation-prep-finalizing-for-coding)

This document provides an ordered checklist for expanding the foundational planning documents into detailed specifications. Items are grouped into phases for logical progression: starting with core technical decisions to inform UX, then refining user flows, addressing hosting, and preparing for implementation. Each item specifies what to flesh out, the level of detail needed, and references to relevant files.

Focus on the app's mobile-first PWA nature, emphasizing offline capabilities, intuitive touch interfaces, and usability for busy users managing meals and shopping.

## Phases

### Phase 0: Core Decisions
- [x] Finalize tech stack (React Native/Expo, Supabase for realtime DB/auth)
- [x] Define MVP features from brief.md (now extended to multiuser)

### Phase 1: Core Decisions (Design System Foundations)
These items finalize technical choices that underpin UX and implementation.

- [x] Finalize database choice: **Supabase (PostgreSQL)** has been selected. Decision is documented in [`plans/design-system.md`](plans/design-system.md) and [`docs/db-research.md`](../docs/db-research.md).
  *Level of detail:* Add subsections with bullet-point comparisons, a simple text-based decision table, and reference to brief.md's offline requirements.

- [x] Define authentication strategy: **Supabase Auth** will be used, as it integrates seamlessly with the chosen database. Decision documented in [`plans/design-system.md`](plans/design-system.md).
  *Level of detail:* Bullet points for each option, flow diagram in Mermaid (e.g., login → token storage → offline validation), cross-reference hosting.md for cloud integration.

- [-] Specify ingredient optimization algorithm: Detail logic for suggesting substitutions (e.g., based on pantry similarity scores, nutritional matching via simple heuristics or embeddings), add to data models section in [`plans/design-system.md`](plans/design-system.md). Decision documented in [`decisions/phase-1/ingredient-optimization.md`](decisions/phase-1/ingredient-optimization.md).
  *Level of detail:* Pseudocode snippets, bullet-point steps, example inputs/outputs; reference brief.md's personalization goals.

### Phase 1.5: Realtime Collaboration Setup
This phase builds on core setup to enable multiuser sync, focusing on quick integration via Supabase SDKs for dev speed.

- [ ] Integrate Supabase Realtime: Set up client subscriptions for key tables (e.g., meal_plans, inventory, shopping_lists); test live updates with multiple simulated users/devices. Decision documented in [`decisions/phase-1.5/realtime-integration.md`](decisions/phase-1.5/realtime-integration.md).
  - API Sketch: Use `supabase.channel('shared-list').on('postgres_changes', { event: '*', schema: 'public', table: 'shopping_lists' }, callback)` for broadcasting changes.
  - Mobile: Ensure Expo compatibility; implement optimistic updates (e.g., local state mutation before DB write).

- [ ] Implement User Auth & Presence: Configure Supabase auth (email/password or social); add presence tracking for online indicators. Decision documented in [`decisions/phase-1.5/auth-and-presence.md`](decisions/phase-1.5/auth-and-presence.md).
  - API Sketch: `supabase.auth.signInWithPassword({ email, password })`; track presence with `supabase.channel('presence').track({ user: userId, online: true })`.
  - UX Tie-in: Big avatar buttons for invites; simple alerts for conflicts.

- [ ] Conflict Resolution & Offline Handling: Add last-write-wins logic for simple cases; optimistic UI with sync queues. Decision documented in [`decisions/phase-1.5/conflict-resolution-and-offline.md`](decisions/phase-1.5/conflict-resolution-and-offline.md).
  - TDD: Write unit tests for sync handlers (e.g., mock WebSocket events, assert state updates); integration tests for multiuser scenarios (e.g., two clients editing simultaneously).
  - Mobile Focus: Use local storage for offline queuing; show user-friendly toasts on sync (e.g., "Changes synced with 2 collaborators").

- [ ] Notifications Setup: Integrate Supabase Edge Functions for push alerts on changes; hook to Expo Notifications. Decision documented in [`decisions/phase-1.5/notifications.md`](decisions/phase-1.5/notifications.md).
  - API Sketch: Trigger function on DB insert/update: `supabase.functions.invoke('send-notification', { body: { userId, message } })`.

- [ ] Testing Multiuser Sync: Manual tests for invites, live edits, conflicts; add e2e tests with tools like Detox for mobile realtime flows. Decision documented in [`decisions/phase-1.5/multiuser-testing.md`](decisions/phase-1.5/multiuser-testing.md).

This phase ensures realtime multiuser without delaying core dev—Supabase's SDKs allow rapid prototyping of sync features.

- [ ] Refine categorical UI for shopping lists: Expand wireframes with specifics for categories (e.g., drag-to-reorder, swipe-to-checkoff), update mobile text wireframes in [`plans/ux-flow.md`](plans/ux-flow.md).  
  *Level of detail:* Add subsections with updated Mermaid flowcharts, accessibility notes (e.g., ARIA for screen readers), and usability best practices for touch interfaces.

- [ ] Develop LLM prompt examples for meal suggestions: Create 3-5 sample prompts for generating recipes (e.g., "Suggest low-carb meal using [pantry items], optimize for [diet prefs]"), integrate into LLM section of [`plans/design-system.md`](plans/design-system.md) and link from UX flow.  
  *Level of detail:* Bullet-point prompt templates with variables, expected outputs, error-handling (e.g., fallback if LLM unavailable offline); reference brief.md's AI personalization.

- [ ] Detail meal planning verification flow: Flesh out user confirmation steps (e.g., edit suggestions, approve shopping additions), including error states, in [`plans/ux-flow.md`](plans/ux-flow.md).  
  *Level of detail:* Sequence diagrams in Mermaid, mobile-specific interactions (e.g., modal popups), cross-reference data models like MealPlan.

## Phase 3: Infrastructure Setup (Hosting and Integration)
Address deployment to support PWA features.

- [x] Select hosting providers: **Self-hosted on Raspberry Pi using Docker** is the primary strategy. Cloud options are secondary. Decision documented in [`plans/hosting.md`](plans/hosting.md).
  *Level of detail:* Bullet pros/cons, cost estimates, TODO resolutions from existing file; include text-based architecture diagram.

- [-] Outline offline sync mechanisms: Define strategies for data sync (e.g., IndexedDB local + API polling on reconnect), add to hosting and design-system sections in respective files.  
  *Level of detail:* High-level flow in Mermaid, reference to database choice; ensure alignment with mobile-first brief.

## Phase 4: Implementation Prep (Finalizing for Coding)
Prepare artifacts for transition to development.

- [ ] Create `Procfile.dev` for Overmind: Define the processes for the frontend, backend, and Supabase CLI to streamline local development, as specified in [`plans/hosting.md`](plans/hosting.md).

- [ ] Review and consolidate data models: Ensure models (e.g., PantryItem, ShoppingListItem, Recipe) include all fields, relationships, and validation rules; update [`plans/design-system.md`](plans/design-system.md) with ER diagram (text-based).  
  *Level of detail:* Add relational diagram in Mermaid, examples of JSON schemas; cover brief's optimization needs.

- [ ] Create API endpoint sketches: Based on UX flows, outline REST endpoints (e.g., POST /meal-plan, GET /shopping-list), including auth and error responses, in [`plans/design-system.md`](plans/design-system.md).  
  *Level of detail:* Bullet-list endpoints with methods, params, responses; reference FastAPI best practices for PWA.

- [ ] Compile testing strategy outline: Specify TDD approach for key features (e.g., unit tests for algorithm, E2E for flows), add new section to [`plans/design-system.md`](plans/design-system.md) linking to rules.md.  
  *Level of detail:* Phased checklist (unit/integration/E2E), tools (pytest/Vitest), coverage goals; align with brief's reliability focus.

After completing these items, review and update [`plans/index.md`](plans/index.md) to include a summary and link to this file for comprehensive planning navigation.