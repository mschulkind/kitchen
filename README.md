# Kitchen 🍳

**The "Choose Your Own Adventure" Meal Planner**

A personal-use application that transforms meal planning from a chore into a creative workflow. It uses AI to "pitch" you meal ideas based on your actual inventory, helps you verify ingredients with a "Delta Engine" that does the math for you, and generates optimized shopping lists.

---

## 🏗️ Architecture

The project is a Monorepo using a **Hybrid Stack**:

- **Frontend**: [Expo](https://expo.dev) (React Native) targeting **Web First** (PWA) and Android.
- **Backend API**: [FastAPI](https://fastapi.tiangolo.com/) (Python) for core logic, AI orchestration, and scraping.
- **Database**: [Supabase](https://supabase.com) (PostgreSQL) for relational data, Auth, and Realtime sync.
- **Infrastructure**: Fully self-hostable via **Docker Compose**.

## 🚀 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose
- [Just](https://github.com/casey/just) (Command runner)
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Node.js & npm/yarn

### Quick Start

1.  **Clone & Setup**

    ```bash
    git clone https://github.com/yourusername/kitchen.git
    cd kitchen
    # Install dependencies
    just setup
    ```

2.  **Configure Environment (CRITICAL)**

    You **must** configure the `.env` file before starting the stack, or the database will fail to boot.

    ```bash
    cp .env.example .env
    ```

    Open `.env` and set the following values (at minimum):

    - `POSTGRES_PASSWORD`: Set this to a strong password (required).
    - `JWT_SECRET` / `ANON_KEY` / `SERVICE_ROLE_KEY`: Generate these automatically:

    ```bash
    # Install dependency
    uv pip install pyjwt

    # Generate keys and append to .env
    python3 scripts/generate_supabase_keys.py >> .env
    ```

    *Note: Open `.env` and clean up any duplicate keys if you ran this multiple times.*

3.  **Start Infrastructure (Supabase + API)**

    ```bash
    # Starts Postgres, Realtime, Auth, and the Python API
    just up
    ```

4.  **Start Frontend**

    ```bash
    # Runs Expo in web mode
    just web
    ```

Visit `http://localhost:8200` for the App and `http://localhost:5300/docs` for the API Swagger UI.

## ⚙️ Configuration & Ports

The application is fully configurable via the `.env` file (loaded automatically by `mise` or `docker-compose`).

| Service | Default Port | Env Var | Description |
| :--- | :--- | :--- | :--- |
| **Kitchen API** | `5300` | `API_PORT` | The main FastAPI backend. |
| **Web App** | `8200` | `WEB_PORT` | The Expo PWA (Frontend). |
| **Supabase (API)** | `8250` | `SUPABASE_PORT` | The Kong Gateway for Supabase (REST, Realtime, Auth). |
| **Supabase Studio** | `5303` | `STUDIO_PORT` | The Supabase Admin UI dashboard. |
| **Postgres** | `54322` | `DB_PORT` | Host mapping for direct DB access (avoiding system 5432). |

To change a port, update `.env`:
```bash
API_PORT=5301
WEB_PORT=8201
```

---

## 🧪 Testing

We follow a strict **TDD** process split into granular phases.

### Backend Tests (Python)

Run unit tests for the Delta Engine, Recipe Parser, and Core API:

```bash
just test-api
```

### Frontend Tests (JS/TS)

Run unit and component tests:

```bash
just test-web
```

### End-to-End Tests

*Currently manual or via Maestro scripts (see `docs/plans`)*

---

## 📂 Documentation

The source of truth for all planning and architecture is in `docs/`.

- **[Execution Roadmap](docs/plans/execution-roadmap.md)**: The master checklist of what is built vs. planned.
- **[Central Plan](docs/plans/central-plan.md)**: High-level architectural vision.
- **[Design System](docs/plans/design-system.md)**: UI/UX standards.
- **[Open Questions](docs/plans/open-questions.md)**: Decision log.

### Key Feature Specs

- [Phase 2: Recipe Engine](docs/plans/phase-02-recipe-engine.md) (Parsing "1 onion")
- [Phase 3: Delta Engine](docs/plans/phase-03-delta-engine.md) (The Math logic)
- [Phase 5: Planner Core](docs/plans/phase-05-planner-core.md) (The "Adventure" algorithm)

---

## 🛠️ Development Workflow

1. **Pick a Phase**: Check `docs/plans/execution-roadmap.md` for the active phase (e.g., `1C`).
2. **Read the Spec**: Open the corresponding `docs/plans/phase-XX.md` file.
3. **Write Tests**: Implement the tests defined in the "Testing Plan" section first.
4. **Implement**: Write code in `src/api` or `src/mobile` to pass the tests.
5. **Verify**: Run `just lint` and `just check` before committing.

### Common Commands

- `just lint`: Run formatters (Ruff, Prettier) and linters.
- `just check`: Run all tests and type checks.
- `just clean`: Remove artifacts and temp files.
