# Planning Documents Index

## Table of Contents
- [Overview](#overview)
- [Documents](#documents)
- [Decision Logs](#decision-logs)
- [Navigation Notes](#navigation-notes)

This index serves as a central hub for all planning, outlines, specifications, and decisions in the Personalized Dinner & Shopping App project. It is maintained in the `plans/` directory, which is git-tracked for version control.
  
  - Updated [.kilocode/rules.md](.kilocode/rules.md) with a new "Git Workflow" section outlining commit and push practices aligned with TDD iterations.

## Overview
The planning phase focuses on establishing the foundational architecture, UX flows, and technical decisions to ensure the app is efficient, user-friendly, and aligned with the project brief. Key themes include intelligent meal planning, dynamic inventory tracking, intuitive verification, and optimized shopping lists, with a mobile-first approach.

## Documents

### [planning-mode.md](planning-mode.md) **Summary**: Configuration spec for the new 'planning' mode, detailing capabilities for conversational spec-building, file updates, git workflows, and integration with the app's architecture.

### [brief.md](brief.md)
**Summary**: The core project brief outlining the app's summary, key features (e.g., intelligent meal planning, inventory tracking, categorical checklist UI, optimized shopping lists), technical architecture (backend logic, LLM integration), and high-level goals for usability and efficiency.

### [design-system.md](design-system.md)
**Summary**: Records key technical decisions. **Supabase** has been selected as the primary database and authentication provider. The document now includes architectural patterns, data models (e.g., PantryItem), and a strategy for local development and testing using the Supabase CLI.

### [ux-flow.md](ux-flow.md)
**Summary**: Outline of user experience flows, such as meal planning → inventory verification → shopping list generation. Emphasizes mobile-first considerations with text-based wireframe sketches, key screens, and interactions.

### [hosting.md](hosting.md)
**Summary**: Outlines the hosting strategy, with the primary approach being self-hosting on a Raspberry Pi using Docker and Docker Compose. This includes running the frontend, backend, and Supabase stack in containers. Cloud hosting options are now considered secondary.

### [development-todo.md](development-todo.md)
**Summary**: Detailed checklist for fleshing out the planning phase, covering design decisions, UX refinements, hosting choices, and implementation preparation.

### [../docs/db-research.md](../docs/db-research.md)
**Summary**: Research and recommendations for database options tailored to the app's offline-first PWA needs, evaluating SQLite, IndexedDB, PouchDB, Supabase, and PostgreSQL; recommends SQLite for fast MVP development with optional Supabase for future sync.

## Decision Logs

This section contains detailed documentation for key technical and architectural decisions.

*   [**Phase 1: Ingredient Optimization Algorithm**](decisions/phase-1/ingredient-optimization.md): Logic for recipe and ingredient suggestions.
*   [**Phase 1.5: Realtime Integration**](decisions/phase-1.5/realtime-integration.md): Strategy for using Supabase Realtime.
*   [**Phase 1.5: Auth and Presence**](decisions/phase-1.5/auth-and-presence.md): User authentication and online presence tracking.
*   [**Phase 1.5: Conflict Resolution and Offline**](decisions/phase-1.5/conflict-resolution-and-offline.md): Handling for data sync and offline usage.
*   [**Phase 1.5: Notifications**](decisions/phase-1.5/notifications.md): Push notification setup using Supabase Edge Functions.
*   [**Phase 1.5: Multiuser Testing**](decisions/phase-1.5/multiuser-testing.md): Testing strategy for real-time features.

## Navigation Notes
- Use relative links for easy navigation within the `plans/` directory.
- As new documents are added or updated, this index will be revised to include summaries and links.
- For temporary research or data dumps, refer to the [docs/index.md](../docs/index.md).

TODO: Add more documents as the planning phase progresses (e.g., API specs, testing strategy)...
