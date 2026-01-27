plan_dir := `ls -d phase0_flow/plans/*/ | sort | tail -n 1 | sed 's/\/$//'`
recipe_dir := plan_dir / "recipes"
output_dir := recipe_dir / "pdfs"
css_file := recipe_dir / "recipes.css"
plan_file := plan_dir / "04-final-plan.md"
plan_pdf := output_dir / "00-plan-overview.pdf"

# List all available commands
default:
    @just --list

# Convert all recipes to PDF and the plan overview
all: plan
    mkdir -p {{output_dir}}
    @for file in {{recipe_dir}}/*.md; do \
        filename=$(basename "$file" .md); \
        echo "Converting $file to {{output_dir}}/$filename.pdf"; \
        uv run pandoc "$file" -o "{{output_dir}}/$filename.pdf" --pdf-engine=weasyprint --css={{css_file}} --metadata title="Recipe" --section-divs; \
    done
    @for file in {{recipe_dir}}/*.html; do \
        if [ -f "$file" ]; then \
            filename=$(basename "$file" .html); \
            echo "Converting $file to {{output_dir}}/$filename.pdf"; \
            uv run weasyprint "$file" "{{output_dir}}/$filename.pdf"; \
        fi \
    done

# Convert the meal plan overview to PDF (excluding shopping list)
plan:
    @mkdir -p {{output_dir}}
    @if [ -f "{{plan_file}}" ]; then \
        echo "Converting {{plan_file}} to {{plan_pdf}} (stripping shopping list)"; \
        awk '/## 🛒 Consolidated Shopping List/{skip=1; next} skip && /^---/{skip=0; next} !skip' "{{plan_file}}" > "{{recipe_dir}}/.tmp-plan.md"; \
        uv run pandoc "{{recipe_dir}}/.tmp-plan.md" -o "{{plan_pdf}}" --pdf-engine=weasyprint --css={{css_file}} --metadata title="Meal Plan Overview" --section-divs; \
        rm "{{recipe_dir}}/.tmp-plan.md"; \
    else \
        echo "No plan file found at {{plan_file}}"; \
    fi

# Convert a specific recipe to PDF (supports .json, .html, or .md)
recipe name:
    mkdir -p {{output_dir}}
    @if [ -f "{{recipe_dir}}/{{name}}.json" ]; then \
        echo "Rendering JSON: {{recipe_dir}}/{{name}}.json"; \
        uv run python scripts/render_recipe.py "{{recipe_dir}}/{{name}}.json" "{{output_dir}}/{{name}}.pdf"; \
    elif [ -f "{{recipe_dir}}/{{name}}.html" ]; then \
        echo "Converting HTML: {{recipe_dir}}/{{name}}.html"; \
        uv run weasyprint "{{recipe_dir}}/{{name}}.html" "{{output_dir}}/{{name}}.pdf"; \
    elif [ -f "{{recipe_dir}}/{{name}}.md" ]; then \
        echo "Converting Markdown: {{recipe_dir}}/{{name}}.md"; \
        uv run pandoc "{{recipe_dir}}/{{name}}.md" -o "{{output_dir}}/{{name}}.pdf" --pdf-engine=weasyprint --css={{css_file}} --metadata title="Recipe" --section-divs; \
    else \
        echo "No recipe found: {{name}} (looked for .json, .html, and .md)"; \
        exit 1; \
    fi

# Render all JSON recipes to PDF
render-all:
    mkdir -p {{output_dir}}
    @for file in {{recipe_dir}}/*.json; do \
        if [ -f "$file" ]; then \
            filename=$(basename "$file" .json); \
            echo "Rendering $file to {{output_dir}}/$filename.pdf"; \
            uv run python scripts/render_recipe.py "$file" "{{output_dir}}/$filename.pdf"; \
        fi \
    done

# Convert all variant-* recipes to PDF for comparison
variants:
    mkdir -p {{output_dir}}
    @for file in {{recipe_dir}}/variant-*.html; do \
        if [ -f "$file" ]; then \
            filename=$(basename "$file" .html); \
            echo "Converting $file to {{output_dir}}/$filename.pdf"; \
            uv run weasyprint "$file" "{{output_dir}}/$filename.pdf"; \
        fi \
    done
    @echo ""
    @echo "✅ All variants generated in {{output_dir}}/"
    @ls -la {{output_dir}}/variant-*.pdf 2>/dev/null || echo "No variant PDFs found"
    @# Concatenate all variants into one PDF for easy viewing
    @if command -v pdfunite >/dev/null 2>&1; then \
        pdfunite {{output_dir}}/variant-*.pdf {{output_dir}}/all-variants.pdf 2>/dev/null && \
        echo "📄 Combined PDF: {{output_dir}}/all-variants.pdf"; \
    fi

# Remove generated PDFs
clean:
    rm -rf {{output_dir}}

# ============================================================================
# Setup & Installation
# ============================================================================

# Setup the entire project
setup: install dev-setup
    cd tests/web && npx playwright install chromium

# Development environment setup (Keys, Docker, Seeds)
dev-setup:
    ./scripts/setup_env.sh
    just up-infra
    @echo "Waiting for Auth service to start..."
    uv run scripts/seed_dev_data.py

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
check: lint test typecheck typecheck-js

# Lint all code (Python, Markdown, Mermaid)
lint: lint-py lint-md lint-mmd

# Lint Python code
lint-py:
    uv run ruff check .

# Lint frontend code (skip if no config)
lint-js:
    cd src/mobile && npm run lint || true

# Type check frontend code
typecheck-js:
    cd src/mobile && npm run typecheck

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

# Start infrastructure ONLY (DB, Auth, Realtime) - for local API dev
up-infra:
    cp .env infra/docker/.env
    @python3 -c "import os; from string import Template; print(Template(open('infra/docker/volumes/kong/kong.yml.template').read()).safe_substitute(os.environ))" > infra/docker/volumes/kong/kong.yml
    docker compose -f infra/docker/docker-compose.yml up -d db kong auth realtime rest meta storage studio

docker-up:
    cp .env infra/docker/.env
    @python3 -c "import os; from string import Template; print(Template(open('infra/docker/volumes/kong/kong.yml.template').read()).safe_substitute(os.environ))" > infra/docker/volumes/kong/kong.yml
    docker compose -f infra/docker/docker-compose.yml up -d

# Start both Frontend and Backend locally using Hivemind
dev-all: up-infra
    @mkdir -p logs
    @if ! command -v hivemind > /dev/null; then echo "Hivemind not found. Install with: go install github.com/DarthSim/hivemind/v2@latest (or brew/apt/pacman)"; exit 1; fi
    hivemind Procfile.dev

# Stop all containers
down: docker-down

# DANGER: Wipes the database and restarts everything from scratch
reset-stack:
    @printf "\033[31mDANGER: This will wipe the database and all stored data.\033[0m\n"
    @python3 -c "if input('Type \'delete\' to continue: ') != 'delete': print('Aborted.'); exit(1)"
    docker compose -f infra/docker/docker-compose.yml down -v
    rm -rf infra/docker/volumes/kong/kong.yml
    just up

docker-down:
    docker compose -f infra/docker/docker-compose.yml down

# View logs for all services
logs:
    docker compose -f infra/docker/docker-compose.yml logs -f

# Run API locally (without Docker)
dev-api:
    uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 5300

# ============================================================================
# Mobile & Frontend (Phase 1C)
# ============================================================================

# Start Expo dev server (Web first - D3)
dev-frontend:
    cd src/mobile && BROWSER=none npx expo start --web --port 8200

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
