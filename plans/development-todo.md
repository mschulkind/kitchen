# Development TODO: Fleshing Out Planning Phase

## Table of Contents
- [Phases](#phases)
- [Phase 0: Core Decisions](#phase-0-core-decisions)
- [Phase 1: Core Decisions (Design System Foundations)](#phase-1-core-decisions-design-system-foundations)
- [Phase 1.5: Realtime Collaboration Setup](#phase-15-realtime-collaboration-setup)
- [Phase 2: UX Refinements](#phase-2-ux-refinements)
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

- [x] [`Specify ingredient optimization algorithm`](decisions/phase-1/ingredient-optimization.md): Detail logic for suggesting substitutions (e.g., based on pantry similarity scores, nutritional matching via simple heuristics or embeddings), add to data models section in [`plans/design-system.md`](plans/design-system.md).
  *Level of detail:* Pseudocode snippets, bullet-point steps, example inputs/outputs; reference brief.md's personalization goals.
  *Progress (2025-09-18 00:45 EDT):* Decision finalized to use an LLM-powered approach. Details are in the decision log and integrated into the design system.

### Phase 1.5: Realtime Collaboration Setup
This phase builds on core setup to enable multiuser sync, focusing on quick integration via Supabase SDKs for dev speed.

- [x] [`Integrate Supabase Realtime`](decisions/phase-1.5/realtime-integration.md): Set up client subscriptions for key tables (e.g., meal_plans, inventory, shopping_lists); test live updates with multiple simulated users/devices.
  - API Sketch: Use `supabase.channel('shared-list').on('postgres_changes', { event: '*', schema: 'public', table: 'shopping_lists' }, callback)` for broadcasting changes.
  - Mobile: Ensure Expo compatibility; implement optimistic updates (e.g., local state mutation before DB write).
  - *Progress (2025-09-18):* Expanded channels to include inventory_items and meal_plans tables with filters; detailed optimistic updates using React Query for mutations, IndexedDB for offline queuing, and mobile-specific UX (e.g., toasts on sync). Pseudocode added for update hooks and reconnect sync.
  *Progress (2025-09-18 00:53 EDT):* Decision approved and finalized.
 
 
- [x] [`Implement User Auth &amp; Presence`](decisions/phase-1.5/auth-and-presence.md): Configure Supabase auth (email/password or social); add presence tracking for online indicators.
   - API Sketch: `supabase.auth.signInWithPassword({ email, password })`; track presence with `supabase.channel('presence').track({ user: userId, online: true })`.
   - UX Tie-in: Big avatar buttons for invites; simple alerts for conflicts.
    *Progress (2025-09-18 00:59 EDT):* Decision approved to use Google social login exclusively. Documented.
  
   - [x] [`Conflict Resolution &amp; Offline Handling`](decisions/phase-1.5/conflict-resolution-and-offline.md): Add last-write-wins logic for simple cases; optimistic UI with sync queues.
    - TDD: Write unit tests for sync handlers (e.g., mock WebSocket events, assert state updates); integration tests for multiuser scenarios (e.g., two clients editing simultaneously).
    - Mobile Focus: Use local storage for offline queuing; show user-friendly toasts on sync (e.g., "Changes synced with 2 collaborators").
    *Progress (2025-09-18 01:11 EDT):* Decision finalized for LWW (MVP) and CRDT (V2). Documented.
 
 - [x] [`Notifications Setup`](decisions/phase-1.5/notifications.md): Integrate Supabase Edge Functions for push alerts on changes; hook to Expo Notifications.
   *Progress (2025-09-18 01:19 EDT):* Decision finalized to defer push notifications until post-MVP. Documented.
   - API Sketch: Trigger function on DB insert/update: `supabase.functions.invoke('send-notification', { body: { userId, message } })`.
 
- [x] [`Testing Multiuser Sync`](decisions/phase-1.5/multiuser-testing.md): Manual tests for invites, live edits, conflicts; add e2e tests with tools like Detox for mobile realtime flows.
  *Progress (2025-09-18 01:59 EDT):* Multiuser testing strategy finalized and documented.

This phase ensures realtime multiuser without delaying core dev—Supabase's SDKs allow rapid prototyping of sync features.

### Phase 2: UX Refinements
These items refine user-facing flows and integrations for intuitive mobile experience.

- [x] [`Refine categorical UI for shopping lists`](decisions/phase-1/ui-categorical-shopping.md): Expand wireframes with specifics for categories (e.g., drag-to-reorder, swipe-to-checkoff), update mobile text wireframes in [`plans/ux-flow.md`](plans/ux-flow.md).  
  *Level of detail:* Add subsections with updated Mermaid flowcharts, accessibility notes (e.g., ARIA for screen readers), and usability best practices for touch interfaces.
  *Progress: Review initiated 2025-09-18 00:23 EDT*
  *Progress (2025-09-18 02:06 EDT):* Phased UI/UX strategy for categorical shopping lists has been finalized and documented.

- [ ] [`Develop LLM prompt examples for meal suggestions`](decisions/phase-1/llm-prompts.md): Create 3-5 sample prompts for generating recipes (e.g., "Suggest low-carb meal using [pantry items], optimize for [diet prefs]"), integrate into LLM section of [`plans/design-system.md`](plans/design-system.md) and link from UX flow.  
  *Level of detail:* Bullet-point prompt templates with variables, expected outputs, error-handling (e.g., fallback if LLM unavailable offline); reference brief.md's AI personalization.
  *Progress: Review initiated 2025-09-18 00:23 EDT*
  (Requires user decision)

- [ ] [`Detail meal planning verification flow`](decisions/phase-1/meal-planning-verification.md): Flesh out user confirmation steps (e.g., edit suggestions, approve shopping additions), including error states, in [`plans/ux-flow.md`](plans/ux-flow.md).  
  *Level of detail:* Sequence diagrams in Mermaid, mobile-specific interactions (e.g., modal popups), cross-reference data models like MealPlan.
  *Progress: Review initiated 2025-09-18 00:23 EDT*
  (Requires user decision)

## Phase 3: Infrastructure Setup (Hosting and Integration)
Address deployment to support PWA features.

- [x] Select hosting providers: **Self-hosted on Raspberry Pi using Docker** is the primary strategy. Cloud options are secondary. Decision documented in [`plans/hosting.md`](plans/hosting.md).
  *Level of detail:* Bullet pros/cons, cost estimates, TODO resolutions from existing file; include text-based architecture diagram.

- [-] [`Outline offline sync mechanisms`](decisions/phase-3/offline-sync-mechanisms.md): Define strategies for data sync (e.g., IndexedDB local + API polling on reconnect), add to hosting and design-system sections in respective files.  
  *Level of detail:* High-level flow in Mermaid, reference to database choice; ensure alignment with mobile-first brief.
  *Progress: Review initiated 2025-09-18 00:23 EDT*
  (Requires user decision)

## Phase 4: Implementation Prep (Finalizing for Coding)
Prepare artifacts for transition to development.

- [ ] [`Create `Procfile.dev` for Overmind`](decisions/phase-4/procfile-dev.md): Define the processes for the frontend, backend, and Supabase CLI to streamline local development, as specified in [`plans/hosting.md`](plans/hosting.md).
  *Progress: Review initiated 2025-09-18 00:23 EDT*
  (Requires user decision)

- [ ] [`Review and consolidate data models`](decisions/phase-4/data-models-consolidation.md): Ensure models (e.g., PantryItem, ShoppingListItem, Recipe) include all fields, relationships, and validation rules; update [`plans/design-system.md`](plans/design-system.md) with ER diagram (text-based).  
  *Level of detail:* Add relational diagram in Mermaid, examples of JSON schemas; cover brief's optimization needs.
  *Progress: Review initiated 2025-09-18 00:23 EDT*
  (Requires user decision)

- [ ] [`Create API endpoint sketches`](decisions/phase-4/api-endpoint-sketches.md): Based on UX flows, outline REST endpoints (e.g., POST /meal-plan, GET /shopping-list), including auth and error responses, in [`plans/design-system.md`](plans/design-system.md).  
  *Level of detail:* Bullet-list endpoints with methods, params, responses; reference FastAPI best practices for PWA.
  *Progress: Review initiated 2025-09-18 00:23 EDT*
  (Requires user decision)

- [ ] [`Compile testing strategy outline`](decisions/phase-4/testing-strategy-outline.md): Specify TDD approach for key features, add new section to [`plans/design-system.md`](plans/design-system.md) linking to rules.md.  
  *Level of detail:* Phased checklist (unit/integration/E2E), tools (pytest/Vitest), coverage goals; align with brief's reliability focus.
  *Progress: Review initiated 2025-09-18 00:23 EDT*
  (Requires user decision)

After completing these items, review and update [`plans/index.md`](plans/index.md) to include a summary and link to this file for comprehensive planning navigation.