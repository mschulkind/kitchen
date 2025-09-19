# Project Structure and Practices

## Table of Contents
- [Directory Usage](#directory-usage)
- [TDD Practices](#tdd-practices)

## Directory Usage

- **plans/**: Git-tracked directory for all planning, outlines, specs, and decisions (e.g., brief.md, design-system.md). Maintain an index.md for navigation.
- **context/**: Gitignored; for dumping research, data, temporary notes, and references (e.g., API docs, recipe datasets). Use index.md to organize and link content.
- **src/** or similar: For source code (backend in Python, frontend in TS/React). Keep tests separate but parallel.
- **General**: All paths relative to project root (/home/matt/code/kitchen). Use clear naming and READMEs in subdirs for clarity.

## TDD Practices

- **Test-First Workflow**: Write tests before implementation code. Start with unit tests for core functions (e.g., recipe matching algorithm), then integration tests for flows like meal planning to shopping list.
- **Fast Test Guidelines**: Ensure test suites run in under 1 second. Use mocking for external dependencies (e.g., LLM calls), parallel execution where possible, and avoid slow I/O in tests. Aim for 80%+ code coverage on critical paths like inventory verification.
- **Test Structure**: Backend tests in `tests/` mirroring source structure; frontend tests colocated with components. Include end-to-end tests for key UX flows using tools like Playwright if needed.