# Database Research for Personalized Dinner & Shopping App

## Overview of Needs

The app requires a database solution that supports offline-first functionality for mobile PWA usage, handling structured data like recipes, ingredients, pantry inventories (PantryItem model), shopping lists, and meal plans. Key needs include:
- **Offline Support**: Local storage and editing of inventory/meal plans without internet (e.g., via IndexedDB or SQLite in browser).
- **Sync Capabilities**: Optional multi-device sync for backups/personal use, but prioritize simplicity to avoid overkill for a personal tool. No real-time collaboration needed.
- **Data Scale**: Small, personal use (hundreds of items max); structured relational data with relationships (e.g., recipes to ingredients).
- **Dev Speed**: Fast setup with minimal boilerplate; easy integration with React/TS frontend (Vite) and Python/FastAPI backend (Pydantic/SQLAlchemy).
- **PWA Fit**: Leverage service workers for caching/sync; focus on magical offline-to-online transitions without complex conflict resolution.

Given the emphasis on dev speed and offline usability, local/simple options are preferred for MVP, with easy migration paths for sync if multi-device becomes essential.

## Comparison Table

| Database Option | Pros | Cons | Dev Speed | Sync Features | Integration Effort (React/TS + Python/FastAPI) |
|-----------------|------|------|-----------|---------------|-----------------------------------------------|
| **SQLite** (via sql.js for frontend, sqlite3 for backend) | Lightweight, no server; full SQL support; zero setup for local dev; excellent for structured data; PWA offline via sql.js + service workers. | Manual sync logic needed (e.g., via API); no built-in real-time. | High (embedded, no auth/config). | Basic (custom API sync); offline-first with local persistence. | Low: sql.js npm for React; sqlite3/SQLAlchemy for FastAPI; Pydantic models map easily. |
| **IndexedDB** (native browser, via Dexie.js wrapper) | Native PWA offline; fast for key-value/structured data; no backend DB needed for pure client-side. | Not relational (manual joins); limited querying; sync requires custom backend. | High for frontend-only; medium if backend involved. | Custom sync; good for simple caching. | Low for React (Dexie.js); backend via FastAPI API endpoints; fits small-scale inventory. |
| **PouchDB/CouchDB** | Seamless offline sync (browser to CouchDB backend); replication handles conflicts; JSON docs fit app data. | NoSQL (less ideal for relational recipes/inventories); steeper learning for queries. | Medium (setup replication). | Excellent bidirectional sync; offline by design. | Medium: PouchDB npm for React; CouchDB Python client for FastAPI; some schema mapping needed. |
| **Supabase** (PostgreSQL with realtime/offline) | Full PostgreSQL relational DB; easy auth/sync; realtime subscriptions; client libs for offline (via service workers). | Cloud dependency (free tier limits); overkill for personal if no multi-device. | High (managed service, quick start). | Built-in realtime/offline sync; row-level subscriptions. | Low: Supabase JS client for React; Python client for FastAPI; SQLAlchemy compatible. |
| **PostgreSQL** (backend-only, with frontend caching) | Robust relational SQL; scalable; great for structured data with ORMs. | No native offline (requires custom IndexedDB caching + service workers); server setup. | Medium (install/setup needed). | Custom sync via API; no built-in offline. | Medium: psycopg2/SQLAlchemy for FastAPI; React fetches via TanStack Query + local cache. |
| **WatermelonDB** (React-optimized, SQLite underhood) | Optimized for React/mobile; lazy loading; sync adapters available; full offline. | Tied to React; requires schema definition; sync not built-in. | Medium-high for React apps. | Pluggable sync (e.g., to backend API). | Low for frontend (npm install); backend sync via FastAPI; good for inventory models. |

*Notes*: Evaluated based on 2023-2024 best practices for PWAs (e.g., IDB for transient data, SQLite for persistence). Excluded Firebase (vendor lock-in, NoSQL) and Realm (acquired by MongoDB, less Python-friendly) for stack fit.

## Recommendations

1. **Top Choice: SQLite** (for initial MVP)
   - **Why**: Optimizes dev speed with zero setup—no servers, auth, or external deps. Use sql.js for browser-side offline persistence (PantryItem inventory, meal plans) and sqlite3/SQLAlchemy for backend validation/sync. PWA service workers can handle caching/sync to backend API. Fits small-scale structured data perfectly; easy TDD with in-memory DB for tests. No overkill for personal use.
   - **Implementation Sketch**: Frontend: sql.js + Dexie.js hybrid for queries. Backend: FastAPI endpoints for sync (e.g., POST /inventory/sync). Offline: Local DB edits queue for upload on reconnect.
   - **Trade-offs**: Manual sync is simple for personal app (e.g., one-way upload); add if multi-device needed later.

2. **Secondary: Supabase** (for easy future sync)
   - **Why**: If multi-device backups become priority, Supabase adds PostgreSQL power with minimal effort—realtime subscriptions for inventory updates, built-in offline via JS client. Dev speed remains high (free tier, auto-generated clients). Migratable from SQLite (similar SQL). Avoids custom sync boilerplate while keeping PWA offline via local caching.
   - **Implementation Sketch**: Use Supabase client in React for direct DB access (with row-level security); FastAPI as proxy for LLM logic. Start with SQLite, migrate schemas later.
   - **Trade-offs**: Introduces cloud dep, but free for personal; skip if offline-only suffices.

These choices prioritize fast iteration: Start local with SQLite, evaluate sync needs post-MVP. Avoid complex options like PouchDB unless replication is core.