# Testing Strategy 🧪

We follow a strict **TDD** (Test Driven Development) approach. This ensures our complex logic (Delta Engine, Parser) is robust before we build UI on top of it.

## 1. Backend Testing (Python/FastAPI)

### Unit Tests

*Fast, isolated, no DB required.*

- **Location**: `src/api/tests/unit/`
- **What to test**:
  - **Business Logic**: `calculate_missing()`, `parse_ingredient()`.
  - **Data Transformations**: DTOs, Unit Conversions.
- **Mocking**: Use `unittest.mock` to stub out:
  - **LLM Calls**: Never call OpenAI in a unit test. Mock the response JSON.
  - **Database**: Mock the Repository layer.

**Example (Mocking LLM)**:

```python
@patch("app.domain.recipes.parser.call_llm")
def test_parse_complex_line(mock_llm):
    mock_llm.return_value = {"item": "onion", "qty": 1, "unit": "count"}
    result = parser.parse("1 large onion")
    assert result.item == "onion"
```

### Integration Tests

*Slower, uses real DB container.*

- **Location**: `src/api/tests/integration/`
- **What to test**:
  - **API Endpoints**: `POST /pantry`, `GET /recipes`.
  - **DB Constraints**: Unique keys, Foreign keys.
- **Fixture**: Use `pytest-asyncio` and a clean DB fixture that rolls back after each test.

## 2. Frontend Testing (React Native)

### Unit/Component Tests (`vitest`)

- **Location**: `src/mobile/components/__tests__/`
- **What to test**:
  - **Rendering**: Does the card show the title?
  - **Interaction**: Does clicking "Delete" call the `onDelete` prop?

### End-to-End (E2E) Tests

*We use **Playwright** to test the Web PWA.*



- **Location**: `tests/web/e2e/`

- **Tool**: Playwright (Typescript)

- **Key Flows**:

    1.  Add Item -> Verify in List.

    2.  Take Photo -> Verify Staging (Mocked Camera).

    3.  Generate Plan -> Verify Options.



## 3. The "Delta Engine" Test Suite

This is the most critical suite. It lives in `src/api/tests/domain/planning/test_delta.py`.

**Must Pass**:

- `test_surplus`: Have 5, Need 2 -> OK.
- `test_deficit`: Have 2, Need 5 -> Buy 3.
- `test_unit_mismatch`: Have 1 cup, Need 100g -> Try convert -> Result.

## 4. Running Tests

```bash
# Run all
just test

# Run only Unit tests (Fast)
uv run pytest src/api/tests/unit

# Run with Coverage
uv run pytest --cov=app src/api
```

## 5. Network Isolation 🛡️

**Constraint**: Tests (Unit AND E2E) **MUST NOT** hit external APIs (OpenAI, Supabase Cloud, Shaws).

### Backend Enforcement

We use `pytest-socket` to disable socket calls during tests.

```python
# conftest.py
def pytest_runtest_setup():
    socket.socket = disabled_socket
```

- **Mocks**: Use `respx` or `vcr.py` to record/replay "Golden Data" for HTTP clients.
- **Exceptions**: Any test attempting a real network call will raise a `SocketBlockedError`.

### Frontend Enforcement

- Configure `MSW` (Mock Service Worker) to `error` on unhandled requests.
