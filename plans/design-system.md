# Design System

This document outlines the technical design decisions for the Personalized Dinner & Shopping App, including frameworks, libraries, architecture patterns, data models, and integration choices. It serves as a living reference for the tech stack and unresolved decisions. Reference [.kilocode/rules.md](../.kilocode/rules.md) for high-level guidelines.

## Frameworks and Libraries

### Backend
- **Framework**: FastAPI (chosen for async support, auto-generated docs, and performance; fallback to Flask if simplicity is prioritized).
  - Decision: Confirmed based on brief's emphasis on efficiency.
- **Database**: SQLite for local/personal use (lightweight, no server needed); PostgreSQL for potential cloud scaling.
  - TODO: Evaluate if ORM like SQLAlchemy or Tortoise-ORM is needed for data models.
- **Other**: Pydantic for data validation (integrated with FastAPI).

### Frontend
- **Framework**: React with TypeScript for type safety and component reusability.
  - Build Tool: Vite for fast HMR and bundling.
- **Styling**: Tailwind CSS for mobile-first, utility-based design.
- **State Management**: TanStack Query (formerly React Query) for data fetching/caching (e.g., inventory sync); Zustand for simple global state if needed.
- **Other**: React Router for navigation (if multi-page feel is required, though single-page preferred for mobile).

### Testing
- Backend: pytest with pytest-asyncio for async tests.
- Frontend: Vitest for fast unit tests; integrate with Vite.
- TODO: Decide on E2E testing tool (e.g., Playwright for mobile simulation).

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

## Pending Decisions
- **Database Choice**: SQLite vs. PostgreSQL – weigh local vs. scalable needs.
- **Authentication**: None for personal use, but if multi-user, consider JWT or none (local-only).
- **Deployment Tech**: See [hosting.md](hosting.md) for details.
- **Offline Capabilities**: Implement IndexedDB for inventory; sync on reconnect.
- **Performance**: Caching strategies (Redis if scaling); optimize LLM calls.
- **Security**: Sanitize LLM inputs/outputs; no external data ingestion yet.

## References
- Project [brief.md](brief.md) for feature alignment.
- [.kilocode/rules.md](../.kilocode/rules.md) for TDD and directory rules.

TODO: Update as decisions are finalized; track changes with git commits.