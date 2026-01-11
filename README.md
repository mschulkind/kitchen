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

1. **Clone & Setup**

    ```bash
    git clone https://github.com/yourusername/kitchen.git
    cd kitchen
    # Install dependencies
    just setup
    ```

2. **Start Infrastructure (Supabase + API)**

    ```bash
    # Starts Postgres, Realtime, Auth, and the Python API
    just up
    ```

3. **Start Frontend**

    ```bash
    # Runs Expo in web mode
    just web
    ```

Visit `http://localhost:8081` for the App and `http://localhost:8000/docs` for the API Swagger UI.

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
