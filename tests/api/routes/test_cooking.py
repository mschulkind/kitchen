"""Tests for Cooking API Routes. 👨‍🍳

Tests for the cooking assistance endpoints.

Fun fact: The "mise en place" philosophy can reduce cooking stress by 50%! 🧘
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.api.app.domain.cooking.service import CookingService
from src.api.app.routes.cooking import get_cooking_service
from src.api.main import app


@pytest.fixture
def mock_cooking_service():
    """Create a mock CookingService."""
    return AsyncMock(spec=CookingService)


@pytest.fixture
def client(mock_cooking_service):
    """Create a test client with mocked dependencies."""

    async def override_get_cooking_service():
        return mock_cooking_service

    app.dependency_overrides[get_cooking_service] = override_get_cooking_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestExportContext:
    """Tests for POST /cooking/export/{recipe_id} endpoint."""

    def test_export_context_invalid_recipe_id(self, client):
        """Test export with invalid UUID format."""
        response = client.post(
            "/api/v1/cooking/export/not-a-uuid",
            json={},
        )
        assert response.status_code == 422


class TestMiseEnPlace:
    """Tests for GET /cooking/mise-en-place/{recipe_id} endpoint."""

    def test_mise_en_place_invalid_recipe_id(self, client):
        """Test mise-en-place with invalid UUID."""
        response = client.get("/api/v1/cooking/mise-en-place/not-a-uuid")
        assert response.status_code == 422


class TestCookingSteps:
    """Tests for GET /cooking/steps/{recipe_id} endpoint."""

    def test_steps_invalid_recipe_id(self, client):
        """Test steps with invalid UUID."""
        response = client.get("/api/v1/cooking/steps/not-a-uuid")
        assert response.status_code == 422


class TestMarkCooked:
    """Tests for POST /cooking/mark-cooked endpoint."""

    def test_mark_cooked_validation(self, client):
        """Test mark-cooked validates input."""
        # Missing required fields
        response = client.post(
            "/api/v1/cooking/mark-cooked",
            json={},
        )
        assert response.status_code == 422

    def test_mark_cooked_invalid_recipe_id(self, client):
        """Test mark-cooked with invalid UUID."""
        response = client.post(
            "/api/v1/cooking/mark-cooked",
            json={"recipe_id": "not-a-uuid"},
        )
        assert response.status_code == 422


class TestCookingSession:
    """Tests for POST /cooking/session/{recipe_id} endpoint."""

    def test_session_invalid_recipe_id(self, client):
        """Test session with invalid UUID."""
        response = client.post("/api/v1/cooking/session/not-a-uuid")
        assert response.status_code == 422

    def test_session_servings_too_high(self, client):
        """Test session with servings > 20."""
        recipe_id = str(uuid4())
        response = client.post(f"/api/v1/cooking/session/{recipe_id}?servings=100")
        assert response.status_code == 422

    def test_session_servings_zero(self, client):
        """Test session with servings = 0."""
        recipe_id = str(uuid4())
        response = client.post(f"/api/v1/cooking/session/{recipe_id}?servings=0")
        assert response.status_code == 422


class TestCookingContext:
    """Tests for GET /cooking/context/{recipe_id} endpoint."""

    def test_context_invalid_recipe_id(self, client):
        """Test context with invalid UUID."""
        response = client.get("/api/v1/cooking/context/not-a-uuid")
        assert response.status_code == 422
