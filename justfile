recipe_dir := "phase0_flow/plans/2025-12-18_stew-and-latkes/recipes"
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

