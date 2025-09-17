# Planning Documents Index

This index serves as a central hub for all planning, outlines, specifications, and decisions in the Personalized Dinner & Shopping App project. It is maintained in the `plans/` directory, which is git-tracked for version control.
  
  - Updated [.kilocode/rules.md](.kilocode/rules.md) with a new "Git Workflow" section outlining commit and push practices aligned with TDD iterations.

## Overview
The planning phase focuses on establishing the foundational architecture, UX flows, and technical decisions to ensure the app is efficient, user-friendly, and aligned with the project brief. Key themes include intelligent meal planning, dynamic inventory tracking, intuitive verification, and optimized shopping lists, with a mobile-first approach.

## Documents

### [planning-mode.md](planning-mode.md) **Summary**: Configuration spec for the new 'planning' mode, detailing capabilities for conversational spec-building, file updates, git workflows, and integration with the app's architecture.

### [brief.md](brief.md)
**Summary**: The core project brief outlining the app's summary, key features (e.g., intelligent meal planning, inventory tracking, categorical checklist UI, optimized shopping lists), technical architecture (backend logic, LLM integration), and high-level goals for usability and efficiency.

### [design-system.md](design-system.md)
**Summary**: Skeleton for recording technical decisions, including frameworks (FastAPI, React/TS, Tailwind), libraries, architecture patterns, data models (e.g., PantryItem, ShoppingListItem), and LLM integration choices. Includes sections for pending decisions like DB selection, auth, and deployment tech.

### [ux-flow.md](ux-flow.md)
**Summary**: Outline of user experience flows, such as meal planning → inventory verification → shopping list generation. Emphasizes mobile-first considerations with text-based wireframe sketches, key screens, and interactions.

### [hosting.md](hosting.md)
**Summary**: Skeleton for hosting and deployment details, covering local development setup (e.g., Vite + Uvicorn), potential cloud options (e.g., Vercel for frontend, Heroku for backend), and PWA considerations for mobile deployment.

### [development-todo.md](development-todo.md)
**Summary**: Detailed checklist for fleshing out the planning phase, covering design decisions, UX refinements, hosting choices, and implementation preparation.

### [../docs/db-research.md](../docs/db-research.md)
**Summary**: Research and recommendations for database options tailored to the app's offline-first PWA needs, evaluating SQLite, IndexedDB, PouchDB, Supabase, and PostgreSQL; recommends SQLite for fast MVP development with optional Supabase for future sync.

## Navigation Notes
- Use relative links for easy navigation within the `plans/` directory.
- As new documents are added or updated, this index will be revised to include summaries and links.
- For temporary research or data dumps, refer to the [docs/index.md](../docs/index.md).

TODO: Add more documents as the planning phase progresses (e.g., API specs, testing strategy)...
