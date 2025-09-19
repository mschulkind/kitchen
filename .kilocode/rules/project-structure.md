# Project Structure and Practices

## Table of Contents
- [Directory Usage](#directory-usage)
- [TDD Practices](#tdd-practices)

## Directory Usage

- **`plans/`**: Git-tracked for planning, outlines, specs, and decisions. Use `index.md` for navigation.
- **`context/`**: Gitignored for research, data, temporary notes, and references. Use `index.md` for organization.
- **`src/`**: Source code (Python backend, TS/React frontend). Tests should be separate but parallel.
- **General**: All paths are relative to the project root. Use clear naming and READMEs.

## TDD Practices

- **Test-First Workflow**: Write tests before implementation. Start with unit tests, followed by integration tests for application flows.
- **Fast Tests**: Keep test suites under 1 second. Mock external dependencies (e.g., LLM calls) and avoid slow I/O. Aim for 80%+ code coverage on critical paths.
- **Test Structure**: Place backend tests in `tests/`, mirroring the source structure. Co-locate frontend tests with components. Use E2E tests for key user flows.