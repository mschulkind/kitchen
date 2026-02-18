# Development Guide 🛠️

This document details the workflows for developing, testing, and deploying the Kitchen Monorepo.

## 1. Environment Setup

### Prerequisites

- **Docker Engine**: 24+
- **Node.js**: 20+ (LTS)
- **Python**: 3.12+
- **Just**: Command runner (optional but recommended)

### Initial Setup

Run this once after cloning:

```bash
# 1. Install Python dependencies
uv sync

# 2. Install Node dependencies
npm install

# 3. Setup pre-commit hooks (if configured)
# pre-commit install
```

## 2. Infrastructure (Docker)

We use Docker Compose to run the Database (Supabase) and the Python API locally.

```bash
# Start everything in detached mode
docker compose -f infra/docker/docker-compose.yml up -d

# View logs
docker compose -f infra/docker/docker-compose.yml logs -f

# Stop everything
docker compose -f infra/docker/docker-compose.yml down
```

**Services:**

- `db`: Postgres (Port 5432)
- `api`: FastAPI Backend (Port 8000)
- `realtime`: Supabase Realtime (Port 4000)
- `studio`: Supabase Studio (Port 3000) - *If enabled*

## 3. Backend Development (FastAPI)

Located in `src/api`.

### Running Locally (No Docker)

If you want to debug with breakpoints:

```bash
cd src/api
# Ensure DB is running in Docker first!
uv run uvicorn app.main:app --reload --port 8000
```

### Testing

We use `pytest`.

```bash
# Run all API tests
uv run pytest src/api

# Run specific domain tests
uv run pytest src/api/domain/pantry
```

## 4. Frontend Development (Expo/Tamagui)

Located in `src/mobile`.

### Running Locally

```bash
cd src/mobile
npx expo start
```

- Press `w` for Web.
- Press `a` for Android Emulator.

### Tamagui

We use Tamagui for UI. If you change `tamagui.config.ts`, you may need to restart the bundler.

## 5. Database Migrations

Currently, we use SQL scripts in `infra/docker/volumes/db/init`.
*Future*: We will move to `alembic` (Python) or `supabase migration` tool.

## 6. Code Style

We enforce strict linting.

- **Python**: `ruff`
- **JS/TS**: `eslint` + `prettier`
- **Markdown**: `markdownlint`

Run everything:

```bash
just lint
```
