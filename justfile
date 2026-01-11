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
# Code Quality & Testing
# ============================================================================

# Run all checks (format, lint, test)
check: lint test

# Lint all code (Python, Markdown, Mermaid)
lint: lint-py lint-md lint-mmd

# Lint Python code
lint-py:
    uv run ruff check .

# Lint Markdown (GitHub format)
lint-md:
    npm run lint

# Lint Mermaid diagrams in Markdown
lint-mmd:
    python3 scripts/lint_mermaid.py

# Format Python code
format:
    uv run ruff check --fix .
    uv run ruff format .

# Run tests
test:
    uv run pytest

# Run tests with coverage
test-cov:
    uv run pytest --cov=src --cov-report=term-missing

# ============================================================================
# Docker & Infrastructure (Phase 1)
# ============================================================================

# Start the full stack (API + Supabase)
up:
    docker compose -f infra/docker/docker-compose.yml up -d

# Stop all containers
down:
    docker compose -f infra/docker/docker-compose.yml down

# View logs for all services
logs:
    docker compose -f infra/docker/docker-compose.yml logs -f

# View API logs only
logs-api:
    docker compose -f infra/docker/docker-compose.yml logs -f api

# Rebuild and restart API container
rebuild-api:
    docker compose -f infra/docker/docker-compose.yml up -d --build api

# Run API locally (without Docker)
dev-api:
    cd src/api && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# ============================================================================
# Mobile App (Phase 1C)
# ============================================================================

# Install mobile dependencies
mobile-install:
    cd src/mobile && npm install

# Start Expo dev server (Web first - D3)
mobile-web:
    cd src/mobile && npm run web

# Start Expo dev server (all platforms)
mobile-start:
    cd src/mobile && npm start

# ============================================================================
# Database
# ============================================================================

# Open Supabase Studio (DB admin UI)
studio:
    @echo "Opening Supabase Studio at http://localhost:3000"
    @xdg-open http://localhost:3000 2>/dev/null || open http://localhost:3000 2>/dev/null || echo "Visit http://localhost:3000"
