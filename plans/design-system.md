# Design System

This document outlines the technical design decisions for the Personalized Dinner & Shopping App, including frameworks, libraries, architecture patterns, data models, and integration choices. It serves as a living reference for the tech stack and unresolved decisions. Reference [.kilocode/rules.md](../.kilocode/rules.md) for high-level guidelines.

### Core Technologies & Architectural Decisions

- **Database**: **Supabase (PostgreSQL)**
  - **Reasoning**: Chosen for its robust realtime sync, built-in authentication, row-level security, and excellent client libraries for both our React/TS frontend and Python/FastAPI backend. This aligns with our need for rapid development of collaborative features like shared shopping lists and inventories.
  - **Reference**: See [`../docs/db-research.md`](../docs/db-research.md) for a detailed comparison.
  
- **Authentication**: **Supabase Auth**
  - **Reasoning**: Tightly integrated with the database, providing a seamless solution for user management and security.

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
- **API Design**: RESTful endpoints (e.g., /meals/plan, /inventory/verify) with JSON payloads. Use OpenAPI for docs.
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
  - Fields: id, name, ingredients (list of {name, quantity, unit}), instructions, cuisine, prep_time, servings.
  - Usage: Stored locally or fetched via LLM; optimized for ingredient overlap.
- **MealPlan**:
  - Fields: days (array of {date, recipe_id, notes for leftovers}).
  - Usage: Generated plan favoring efficiency.
- TODO: Define schemas in Pydantic; consider relationships (e.g., Recipe to Ingredients).

## LLM Integration
- **Provider**: OpenAI GPT (e.g., GPT-4o-mini for cost-efficiency) or local Ollama for privacy/offline.
  - Prompts: Structured for recipe generation (e.g., "Suggest 4-day plan using [ingredients], prioritizing [garden items] and leftovers").
- **Usage Patterns**: 
  - Dynamic suggestions: Input current inventory → Output recipe ideas.
  - Customization: Modify recipes on-the-fly (e.g., substitute ingredients).
- **Error Handling**: Fallback to rule-based logic if LLM fails; cache responses.
- TODO: API key management (environment vars); rate limiting; prompt templates in code.

## Database

Previously, we decided on SQLite for local/offline storage in this personal-use app. However, with the new requirement for realtime multiuser collaboration (e.g., shared meal plans, inventory, and shopping lists across devices), we shift to Supabase (PostgreSQL-based with built-in realtime subscriptions via WebSockets). 

**Recommendation: Supabase**
- **Pros**: Instant sync across users/devices using client SDKs (JS/Python); integrated auth for user management; supports offline mode with optimistic updates and automatic conflict resolution on reconnect; scalable for multiuser without heavy setup.
- **Cons**: Cloud dependency (no fully local option like SQLite), but offers free tier for dev/testing; potential latency for very remote users, mitigated by edge functions.
- **Offline Handling**: Use Supabase's client-side caching for mobile-first app; implement optimistic UI updates (e.g., add item to shared list immediately, sync in background).
- **Migration Path**: Start with Supabase from scratch for simplicity; later, if needed, hybrid with local SQLite for pure offline fallback.

This enables realtime features without sacrificing dev speed, leveraging Supabase's JS SDK for quick integration in our React Native/Expo frontend.

## Collaboration Architecture

To support multiuser realtime collaboration while keeping the app mobile-friendly and usable:

- **Realtime Features**: Use Supabase Realtime (WebSockets) for live updates, e.g., inventory changes propagate instantly to all collaborators; shared shopping lists update checkmarks in real-time; meal plans sync additions/edits across devices.
- **User Presence**: Track online status via Supabase auth and presence channels (e.g., show "User X is editing the list" indicators in the UI, with large, touch-friendly avatars for mobile).
- **Concurrent Editing & Conflict Resolution**: Implement last-write-wins for simple cases (e.g., timestamped updates); for complex edits like meal plans, use operational transforms or Supabase's row-level locking. On mobile, show simple conflict alerts (e.g., "List changed by another user—reload?") with big confirm buttons.
- **Invites & Access**: Auth-based invites via email/share links; role-based permissions (owner, editor, viewer) stored in Supabase tables.
- **Notifications**: Push notifications for changes (e.g., "Item added to shared inventory") using Supabase Edge Functions, optimized for mobile with Expo Notifications.

This architecture extends core features from brief.md (e.g., shared inventory verification checklists) to multiuser without overcomplicating the UX.

## Pending Decisions
- **Database Choice**: Decided – SQLite for MVP (see [docs/db-research.md](../docs/db-research.md)); evaluate Supabase migration post-MVP if sync needed.
- **Authentication**: None for personal use, but if multi-user, consider JWT or none (local-only).
- **Deployment Tech**: See [hosting.md](hosting.md) for details.
- **Offline Capabilities**: Implement IndexedDB for inventory; sync on reconnect.
- **Performance**: Caching strategies (Redis if scaling); optimize LLM calls.
- **Security**: Sanitize LLM inputs/outputs; no external data ingestion yet.

## References
- Project [brief.md](brief.md) for feature alignment.
- [.kilocode/rules.md](../.kilocode/rules.md) for TDD and directory rules.

TODO: Update as decisions are finalized; track changes with git commits.