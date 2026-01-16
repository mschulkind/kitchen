---
name: project-setup
description: Standards for project structure, tooling, and configuration (justfile, uv, ruff, etc).
---

# Project Setup & Configuration Skill

This skill outlines the standard procedure for setting up a new project or refining an existing one with robust tooling for testing, linting, and documentation management, based on the `kitchen` and `songtv` project standards.

## 1. Directory Structure

- **`docs/`**: Documentation root.
    - **`docs/plans/`**: All planning documents, specifications, and decision records.
- **`src/`**: Source code.
- **`tests/`**: Test suite (mirroring `src` structure).
- **`scripts/`**: Utility scripts.

## 2. Tooling Stack

- **Task Runner**: [`just`](https://github.com/casey/just)
- **Python Management**: [`uv`](https://github.com/astral-sh/uv)
- **Node/JS Management**: `npm` (primarily for linting/frontend).

## 3. Configuration Files

### `pyproject.toml` (Python)
Configure `ruff` (linting/formatting) and `pytest` (testing).

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py313" # Adjust for python version

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM"]
ignore = ["E501", "B008"]
```

### `package.json` (Docs & scripts)
Use `markdownlint-cli` for markdown validation.

```json
{
  "scripts": {
    "lint": "markdownlint '**/*.md' --ignore node_modules"
  },
  "devDependencies": {
    "markdownlint-cli": "^0.x.x"
  }
}
```

### `.markdownlint.json`
Configure for GitHub Flavored Markdown and Mermaid diagram support.

```json
{
  "default": true,
  "MD003": { "style": "atx" },
  "MD004": { "style": "dash" },
  "MD007": { "indent": 2 },
  "MD013": false,
  "MD024": { "siblings_only": true },
  "MD033": false,
  "MD040": true,
  "MD041": true,
  "MD046": { "style": "fenced" },
  "MD010": true
}
```

### `justfile`
Standardize developer commands.

```makefile
# Run all checks
check: lint test

# Linting (Python, Markdown, and Mermaid diagrams)
lint: lint-py lint-md lint-mmd
lint-py:
    uv run ruff check .
lint-md:
    npm run lint
lint-mmd:
    python3 scripts/lint_mermaid.py

# Testing
test:
    uv run pytest
```

## 4. Best Practices

- **Consolidate Plans**: Keep all planning docs in `docs/plans` to maintain a clean root directory.
- **Unified Check**: Always provide a `just check` command that runs all verification steps (formatting, linting, testing) locally before pushing.
- **Markdown & Mermaid Linting**: Ensure documentation is consistent and renders correctly on GitHub. Mermaid diagrams are validated for syntax correctness using a dedicated script and `mermaid-cli`.