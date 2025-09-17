# Database Research for Personalized Dinner & Shopping App

## Table of Contents
- [Overview of Needs](#overview-of-needs)
- [Comparison Table](#comparison-table)
- [Recommendations](#recommendations)

## Overview of Needs

The app requires a database solution that supports realtime multiuser collaboration for shared meal plans, inventories, and shopping lists across users/devices, while maintaining offline-first functionality for mobile PWA usage. Handling structured data like recipes, ingredients, pantry inventories (PantryItem model), shopping lists, and meal plans. Key needs include:
- **Realtime Multiuser Sync**: Live updates for shared checklists/inventories (e.g., concurrent editing with conflict resolution), user presence/notifications, and auth for collaborators (e.g., invites, row-level security).
- **Offline Support**: Local storage and editing of inventory/meal plans without internet (e.g., via IndexedDB or SQLite in browser), with optimistic updates and queued sync on reconnect.
- **Data Scale**: Small to medium (hundreds of items per user/group); structured relational data with relationships (e.g., recipes to ingredients, users to shared plans).
- **Dev Speed**: Fast setup with minimal boilerplate; easy integration with React/TS frontend (Vite) and Python/FastAPI backend (Pydantic/SQLAlchemy), leveraging Supabase Python/JS clients.
- **PWA Fit**: Leverage service workers for offline queuing and sync; focus on seamless realtime transitions with modern PWA best practices (e.g., background sync for queued actions).

Given the emphasis on realtime collaboration and dev speed, managed services like Supabase are preferred for MVP, with local fallbacks for offline resilience and easy scaling for multiuser features.

## Comparison Table

| Database Option | Pros | Cons | Dev Speed | Sync Features | Integration Effort (React/TS + Python/FastAPI) | Multiuser Fit |
|-----------------|------|------|-----------|---------------|-----------------------------------------------|---------------|
| **Supabase** (PostgreSQL with realtime/offline) | Full PostgreSQL relational DB; built-in realtime subscriptions (e.g., live inventory updates); easy auth/RLS for collaborators; client libs for offline optimistic updates via service workers; managed service reduces ops. | Cloud dependency (free tier limits for heavy use); potential costs for scaling groups. | High (managed, quick SDK setup with JS/Python clients). | Excellent: Realtime bidirectional sync, presence, notifications; built-in conflict resolution; offline queuing. | Low: Supabase JS client for React (realtime hooks); Python client for FastAPI; SQLAlchemy compatible; fits stack seamlessly. | High: Low effort for shared plans/invites; realtime for concurrent edits without custom WebSockets. |
| **SQLite** (via sql.js for frontend, sqlite3 for backend) | Lightweight, no server; full SQL support; zero setup for local dev/offline prototypes; excellent for structured data; PWA offline via sql.js + service workers. | Manual sync logic needed (e.g., via API); no built-in realtime or auth. | High (embedded, no auth/config). | Basic (custom API sync); offline-first with local persistence; secondary for realtime multiuser. | Low: sql.js npm for React; sqlite3/SQLAlchemy for FastAPI; Pydantic models map easily. | Low: Requires custom backend for collaboration; suitable as local fallback only. |
| **IndexedDB** (native browser, via Dexie.js wrapper) | Native PWA offline; fast for key-value/structured data; no backend DB needed for pure client-side. | Not relational (manual joins); limited querying; sync requires custom backend. | High for frontend-only; medium if backend involved. | Custom sync; good for simple caching/offline queuing. | Low for React (Dexie.js); backend via FastAPI API endpoints; fits small-scale inventory. | Low: No native multiuser/realtime; needs full custom sync layer. |
| **PouchDB/CouchDB** | Seamless offline sync (browser to CouchDB backend); replication handles conflicts; JSON docs fit app data. | NoSQL (less ideal for relational recipes/inventories); steeper learning for queries. | Medium (setup replication). | Excellent bidirectional sync; offline by design; supports multiuser replication. | Medium: PouchDB npm for React; CouchDB Python client for FastAPI; some schema mapping needed. | Medium: Good for sync but requires more setup than Supabase for auth/realtime. |
| **PostgreSQL** (backend-only, with frontend caching) | Robust relational SQL; scalable; great for structured data with ORMs. | No native offline/realtime (requires custom IndexedDB caching + WebSockets/service workers); server setup. | Medium (install/setup needed). | Custom sync via API/WebSockets; no built-in offline. | Medium: psycopg2/SQLAlchemy for FastAPI; React fetches via TanStack Query + local cache. | Medium: Scalable for multiuser but high effort for realtime/auth without add-ons. |
| **WatermelonDB** (React-optimized, SQLite underhood) | Optimized for React/mobile; lazy loading; sync adapters available; full offline. | Tied to React; requires schema definition; sync not built-in. | Medium-high for React apps. | Pluggable sync (e.g., to backend API); offline by design. | Low for frontend (npm install); backend sync via FastAPI; good for inventory models. | Low: Custom multiuser logic needed; best as local layer atop a realtime backend. |

*Notes*: Evaluated based on 2024-2025 best practices for realtime PWAs (e.g., Supabase for collaboration, service workers for offline queuing). Excluded Firebase (vendor lock-in, NoSQL) and Realm (less Python-friendly) for stack fit; prioritize Supabase for low-effort multiuser realtime.

## Recommendations

1. **Top Choice: Supabase** (for realtime multiuser MVP)
   - **Why**: Essential for instant multiuser updates (e.g., shared inventories/meal plans across devices/users) without building custom WebSockets; built-in realtime subscriptions, conflict resolution (optimistic updates), and auth/invites via RLS. Fits dev speed with managed service, JS/Python SDKs, and PostgreSQL relational power—enables fast iteration on collaboration features. Retains PWA offline via client-side queuing/service workers; low effort for presence/notifications.
   - **Implementation Sketch**: Frontend: Supabase JS client in React for realtime queries/subscriptions (e.g., live checklists); optimistic local edits with sync. Backend: Supabase Python client in FastAPI for LLM logic/server-side validation. Use row-level security for collaborators; service workers for offline queuing per modern PWA practices.
   - **Trade-offs**: Cloud dep but free tier suffices for MVP; scales easily for groups.

2. **Secondary: SQLite** (for offline-only prototypes/local fallback)
   - **Why**: Optimizes pure offline dev/testing with zero setup—use as local cache atop Supabase for resilient PWAs. sql.js for browser persistence, sqlite3/SQLAlchemy for backend mocks. Easy to layer under Supabase client for hybrid offline/realtime.
   - **Implementation Sketch**: Frontend: sql.js + Supabase hybrid (local first, sync to cloud). Backend: FastAPI endpoints proxying Supabase for local testing. Offline: Queue edits in SQLite for upload on reconnect.
   - **Trade-offs**: Manual sync for multiuser (avoid for core collab); use only for non-shared prototypes.

These choices prioritize realtime collaboration without slowing dev: Start with Supabase for shared features, add SQLite fallback for offline. Evaluate post-MVP for advanced conflicts if needed; avoids complex options like custom WebSockets.