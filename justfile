recipe_dir := `ls -d phase0_flow/plans/*/ | sort | tail -n 1 | sed 's/$/recipes/'`
output_dir := recipe_dir / "pdfs"
css_file := recipe_dir / "recipes.css"

# List all available commands
default:
    @just --list

# Convert all recipes to PDF
all:
    mkdir -p {{output_dir}}
    @for file in {{recipe_dir}}/*.md; do \
        filename=$(basename "$file" .md); \
        echo "Converting $file to {{output_dir}}/$filename.pdf"; \
        uv run pandoc "$file" -o "{{output_dir}}/$filename.pdf" --pdf-engine=weasyprint --css={{css_file}} --metadata title="Recipe" --section-divs; \
    done

# Convert a specific recipe to PDF (e.g. just recipe green-maghrebi-stew)
recipe name:
    mkdir -p {{output_dir}}
    uv run pandoc "{{recipe_dir}}/{{name}}.md" -o "{{output_dir}}/{{name}}.pdf" --pdf-engine=weasyprint --css={{css_file}} --metadata title="Recipe" --section-divs

# Remove generated PDFs
clean:
    rm -rf {{output_dir}}

# ============================================================================
# Setup & Installation
# ============================================================================

# Setup the entire project
setup: install
    cd tests/web && npx playwright install --with-deps chromium

# Install all dependencies
install: install-py install-js

# Install Python dependencies
install-py:
    uv sync

# Install frontend and tool dependencies
install-js:
    npm install
    cd src/mobile && npm install
    cd tests/web && npm install

# ============================================================================
# Code Quality & Testing
# ============================================================================

# Run all checks (format, lint, typecheck, test)
check: lint test typecheck

# Lint all code (Python, Markdown, Mermaid)
lint: lint-py lint-md lint-mmd

# Lint Python code
lint-py:
    uv run ruff check .

# Lint frontend code
lint-js:
    cd src/mobile && npm run lint

# Lint Markdown (GitHub format)
lint-md:
    npm run lint

# Lint Mermaid diagrams in Markdown
lint-mmd:
    python3 scripts/lint_mermaid.py

# Format all code
format: format-py

# Format Python code
format-py:
    uv run ruff check --fix .
    uv run ruff format .

# Type check Python code
typecheck:
    uv run mypy src/api

# Run all tests
test: test-py

# Run Python tests
test-py:
    uv run pytest

# Run frontend tests
test-js:
    cd src/mobile && npm run test

# Run E2E tests (Playwright)
test-e2e:
    cd tests/web && npx playwright test

# Run tests with coverage
test-cov:
    @echo "=== Backend Coverage ==="
    uv run pytest --cov=src/api --cov-report=term-missing tests/api
    @echo "\n=== Frontend Coverage ==="
    cd src/mobile && npm run test -- --coverage

# Aliases
coverage: test-cov

# ============================================================================
# Docker & Infrastructure (Phase 1)
# ============================================================================

# Start the full stack (API + Supabase)
up: docker-up

docker-up:
    docker compose -f infra/docker/docker-compose.yml up -d

# Stop all containers
down: docker-down

docker-down:
    docker compose -f infra/docker/docker-compose.yml down

# View logs for all services
logs:
    docker compose -f infra/docker/docker-compose.yml logs -f

# Run API locally (without Docker)
dev-api:
    cd src/api && uv run uvicorn main:app --reload --host 0.0.0.0 --port 5300

# ============================================================================
# Mobile & Frontend (Phase 1C)
# ============================================================================

# Start Expo dev server (Web first - D3)
dev-frontend:
    cd src/mobile && npx expo start --web --port 8200

web: dev-frontend

# Start Expo dev server (all platforms)
mobile-start:
    cd src/mobile && npx expo start --port 8200

# ============================================================================
# Database
# ============================================================================

# Open Supabase Studio (DB admin UI)
studio:
    @echo "Opening Supabase Studio at http://localhost:5303"
    @xdg-open http://localhost:5303 2>/dev/null || open http://localhost:5303 2>/dev/null || echo "Visit http://localhost:5303"

# ============================================================================
# PDF Generation (Legacy)
# ============================================================================
