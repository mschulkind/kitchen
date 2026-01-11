# Phase 1: The Foundation & Data Layer

**Goal**: Establish the application shell, database schema, and core API services. Move the "Source of Truth" from Markdown files to a structured Postgres database.

## 1.1 Project Structure & Monorepo Setup

We will organize the repository to support both the Mobile/Web frontend and the Python backend.

### Directory Layout
```text
/
├── src/
│   ├── mobile/          # Expo (React Native) project
│   │   ├── app/         # Expo Router pages
│   │   ├── components/  # Shared UI components
│   │   ├── lib/         # Supabase client, utilities
│   │   └── ...
│   └── api/             # Python (FastAPI) project
│       ├── app/
│       │   ├── main.py  # Entry point
│       │   ├── api/     # Route handlers
│       │   ├── core/    # Config, logging
│       │   ├── services/# Business logic (SOLID)
│       │   └── models/  # Pydantic & DB models
│       ├── tests/
│       └── ...
├── infra/               # Docker, Supabase config, IaC
└── docs/                # Documentation
```

### Tasks
- [ ] Initialize `src/mobile` with `create-expo-app`.
- [ ] Initialize `src/api` with `poetry` or `uv`.
- [ ] Configure strict linting (Ruff for Python, ESLint/Prettier for JS).
- [ ] Set up a `justfile` or `Makefile` for common commands (e.g., `just dev`, `just test`).

## 1.2 Database Schema (Supabase)

We need to model the core domain entities.

### Core Tables

1.  **`users`** (Managed by Supabase Auth)
    - `id`: UUID (PK)
    - `email`: String
    - `full_name`: String

2.  **`households`**
    - `id`: UUID (PK)
    - `name`: String
    - `owner_id`: UUID (FK -> users.id)

3.  **`household_members`**
    - `household_id`: UUID
    - `user_id`: UUID
    - `role`: Enum (owner, editor, viewer)

4.  **`pantry_items`**
    - `id`: UUID (PK)
    - `household_id`: UUID (FK)
    - `name`: String (e.g., "Basmati Rice")
    - `category`: Enum (Produce, Dairy, Pantry, Frozen, Spices, Garden)
    - `quantity`: Float
    - `unit`: String (kg, lbs, units)
    - `expiry_date`: Date (Optional)
    - `location`: String (Free text or Enum: "Top Shelf", "Deep Freezer")

5.  **`recipes`**
    - `id`: UUID (PK)
    - `household_id`: UUID (FK) (Nullable, if null = global/system recipe)
    - `name`: String
    - `description`: Text
    - `source_url`: String
    - `source_markdown`: Text (The raw scraped content)
    - `parsed_ingredients`: JSONB (Structured for search)
    - `prep_time_minutes`: Integer

### Security (RLS)
- Enable RLS on all tables.
- Policies: Users can only select/insert/update rows where `household_id` matches a household they are a member of.

## 1.3 Python API - Core Architecture

We will follow **Clean Architecture** principles.

### Dependency Injection
Use a lightweight DI framework (or simple composition root pattern) to inject dependencies.

```python
# Example Service Interface
class InventoryService(Protocol):
    def add_item(self, item: CreateItemDTO) -> Item: ...
    def get_pantry(self, household_id: UUID) -> List[Item]: ...

# Implementation
class SupabaseInventoryService:
    def __init__(self, db_client):
        self.db = db_client
```

### Endpoints
- `GET /health`: Health check.
- `GET /v1/pantry`: List items.
- `POST /v1/pantry`: Add item.
- `PATCH /v1/pantry/{id}`: Update quantity/details.

## 1.4 Data Migration Strategy

The "Phase 0" data lives in `phase0_flow/stock_lists/` and `recipes/`.

### Migration Script (`scripts/migrate_phase0.py`)
1.  Read `phase0_flow/stock_lists/*.md`.
2.  Parse the Markdown lists (Regex or LLM).
3.  Connect to Supabase.
4.  Insert items into `pantry_items` for the default user/household.
5.  Read `phase0_flow/recipes/*.md`.
6.  Insert into `recipes`, keeping the `source_markdown`.

## Definition of Done (Phase 1)
- [ ] Repo structure created and CI (GitHub Actions) runs lint/test.
- [ ] Supabase project created locally (Docker) or cloud.
- [ ] Database schema applied.
- [ ] Python API running and serving JSON.
- [ ] Existing markdown data migrated to DB.
- [ ] Simple "Hello World" mobile app can fetch and display the pantry list.
