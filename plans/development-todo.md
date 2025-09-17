# Development TODO: Fleshing Out Planning Phase

This document provides an ordered checklist for expanding the foundational planning documents into detailed specifications. Items are grouped into phases for logical progression: starting with core technical decisions to inform UX, then refining user flows, addressing hosting, and preparing for implementation. Each item specifies what to flesh out, the level of detail needed, and references to relevant files.

Focus on the app's mobile-first PWA nature, emphasizing offline capabilities, intuitive touch interfaces, and usability for busy users managing meals and shopping.

## Phase 1: Core Decisions (Design System Foundations)
These items finalize technical choices that underpin UX and implementation.

- [ ] Finalize database choice: Evaluate SQLite vs PostgreSQL for local/offline PWA use (considering sync needs for cloud), document pros/cons, migration paths, and decision in [`plans/design-system.md`](plans/design-system.md).  
  *Level of detail:* Add subsections with bullet-point comparisons, a simple text-based decision table, and reference to brief.md's offline requirements.

- [ ] Define authentication strategy: Assess options like JWT with local storage vs OAuth for PWA (prioritizing secure, offline-resilient login), include pros/cons and selected approach in [`plans/design-system.md`](plans/design-system.md).  
  *Level of detail:* Bullet points for each option, flow diagram in Mermaid (e.g., login → token storage → offline validation), cross-reference hosting.md for cloud integration.

- [ ] Specify ingredient optimization algorithm: Detail logic for suggesting substitutions (e.g., based on pantry similarity scores, nutritional matching via simple heuristics or embeddings), add to data models section in [`plans/design-system.md`](plans/design-system.md).  
  *Level of detail:* Pseudocode snippets, bullet-point steps, example inputs/outputs; reference brief.md's personalization goals.

## Phase 2: UX Refinements (User-Centric Details)
Build on core decisions to detail interactions, ensuring mobile usability.

- [ ] Refine categorical UI for shopping lists: Expand wireframes with specifics for categories (e.g., drag-to-reorder, swipe-to-checkoff), update mobile text wireframes in [`plans/ux-flow.md`](plans/ux-flow.md).  
  *Level of detail:* Add subsections with updated Mermaid flowcharts, accessibility notes (e.g., ARIA for screen readers), and usability best practices for touch interfaces.

- [ ] Develop LLM prompt examples for meal suggestions: Create 3-5 sample prompts for generating recipes (e.g., "Suggest low-carb meal using [pantry items], optimize for [diet prefs]"), integrate into LLM section of [`plans/design-system.md`](plans/design-system.md) and link from UX flow.  
  *Level of detail:* Bullet-point prompt templates with variables, expected outputs, error-handling (e.g., fallback if LLM unavailable offline); reference brief.md's AI personalization.

- [ ] Detail meal planning verification flow: Flesh out user confirmation steps (e.g., edit suggestions, approve shopping additions), including error states, in [`plans/ux-flow.md`](plans/ux-flow.md).  
  *Level of detail:* Sequence diagrams in Mermaid, mobile-specific interactions (e.g., modal popups), cross-reference data models like MealPlan.

## Phase 3: Infrastructure Setup (Hosting and Integration)
Address deployment to support PWA features.

- [ ] Select hosting providers: Compare Vercel/Netlify for frontend vs Render/Heroku for backend, evaluate PWA support (e.g., service workers, HTTPS), document choices and setup sketches in [`plans/hosting.md`](plans/hosting.md).  
  *Level of detail:* Bullet pros/cons, cost estimates, TODO resolutions from existing file; include text-based architecture diagram.

- [ ] Outline offline sync mechanisms: Define strategies for data sync (e.g., IndexedDB local + API polling on reconnect), add to hosting and design-system sections in respective files.  
  *Level of detail:* High-level flow in Mermaid, reference to database choice; ensure alignment with mobile-first brief.

## Phase 4: Implementation Prep (Finalizing for Coding)
Prepare artifacts for transition to development.

- [ ] Review and consolidate data models: Ensure models (e.g., PantryItem, ShoppingListItem, Recipe) include all fields, relationships, and validation rules; update [`plans/design-system.md`](plans/design-system.md) with ER diagram (text-based).  
  *Level of detail:* Add relational diagram in Mermaid, examples of JSON schemas; cover brief's optimization needs.

- [ ] Create API endpoint sketches: Based on UX flows, outline REST endpoints (e.g., POST /meal-plan, GET /shopping-list), including auth and error responses, in [`plans/design-system.md`](plans/design-system.md).  
  *Level of detail:* Bullet-list endpoints with methods, params, responses; reference FastAPI best practices for PWA.

- [ ] Compile testing strategy outline: Specify TDD approach for key features (e.g., unit tests for algorithm, E2E for flows), add new section to [`plans/design-system.md`](plans/design-system.md) linking to rules.md.  
  *Level of detail:* Phased checklist (unit/integration/E2E), tools (pytest/Vitest), coverage goals; align with brief's reliability focus.

After completing these items, review and update [`plans/index.md`](plans/index.md) to include a summary and link to this file for comprehensive planning navigation.