"""Tests for Recipes API Routes. 📖

Tests for recipe management endpoints.

Fun fact: The average cookbook has about 150 recipes! 📚
"""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.api.app.domain.recipes.service import RecipeService
from src.api.app.routes.recipes import get_recipe_service
from src.api.main import app


@pytest.fixture
def mock_recipe_service():
    """Create a mock RecipeService."""
    return AsyncMock(spec=RecipeService)


@pytest.fixture
def client(mock_recipe_service):
    """Create a test client with mocked dependencies."""

    async def override_get_recipe_service():
        yield mock_recipe_service

    app.dependency_overrides[get_recipe_service] = override_get_recipe_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestListRecipes:
    """Tests for GET /recipes endpoint."""

    def test_list_recipes_pagination_params(self, client):
        """Test pagination query params are validated."""
        # Invalid page (< 1)
        response = client.get("/api/v1/recipes?page=0")
        assert response.status_code == 422

    def test_list_recipes_per_page_limit(self, client):
        """Test per_page max limit is enforced."""
        # per_page > 50 should be rejected
        response = client.get("/api/v1/recipes?per_page=100")
        assert response.status_code == 422


class TestGetRecipe:
    """Tests for GET /recipes/{recipe_id} endpoint."""

    def test_get_recipe_invalid_id(self, client):
        """Test getting recipe with invalid UUID."""
        response = client.get("/api/v1/recipes/not-a-uuid")
        assert response.status_code == 422


class TestCreateRecipe:
    """Tests for POST /recipes endpoint."""

    def test_create_recipe_validation(self, client):
        """Test recipe creation validates input."""
        response = client.post(
            "/api/v1/recipes",
            json={},  # Missing required fields
        )
        assert response.status_code == 422

    def test_create_recipe_empty_title(self, client):
        """Test recipe with empty title is rejected."""
        response = client.post(
            "/api/v1/recipes",
            json={
                "title": "",
                "source_url": "https://example.com/recipe",
            },
        )
        assert response.status_code == 422


class TestUpdateRecipe:
    """Tests for PATCH /recipes/{recipe_id} endpoint."""

    def test_update_recipe_invalid_id(self, client):
        """Test updating recipe with invalid UUID."""
        response = client.patch(
            "/api/v1/recipes/not-a-uuid",
            json={"title": "New Title"},
        )
        assert response.status_code == 422


class TestDeleteRecipe:
    """Tests for DELETE /recipes/{recipe_id} endpoint."""

    def test_delete_recipe_invalid_id(self, client):
        """Test deleting recipe with invalid UUID."""
        response = client.delete("/api/v1/recipes/not-a-uuid")
        assert response.status_code == 422


class TestIngestRecipe:
    """Tests for POST /recipes/ingest endpoint."""

    def test_ingest_missing_url(self, client):
        """Test ingest without URL."""
        response = client.post(
            "/api/v1/recipes/ingest",
            json={},
        )
        assert response.status_code == 422


class TestParseIngredient:
    """Tests for POST /recipes/parse-ingredient endpoint."""

    def test_parse_single_validation(self, client):
        """Test parse endpoint validates input."""
        response = client.post(
            "/api/v1/recipes/parse-ingredient",
            json={},  # Missing required field
        )
        assert response.status_code == 422

    def test_parse_empty_text(self, client):
        """Test parse with empty text is rejected."""
        response = client.post(
            "/api/v1/recipes/parse-ingredient",
            json={"text": ""},
        )
        assert response.status_code == 422


class TestParseBatchIngredients:
    """Tests for POST /recipes/parse-ingredients endpoint."""

    def test_parse_batch_validation(self, client):
        """Test batch parse validates input."""
        response = client.post(
            "/api/v1/recipes/parse-ingredients",
            json={},  # Missing required field
        )
        assert response.status_code == 422

    def test_parse_batch_empty_list(self, client):
        """Test batch parse with empty list is rejected."""
        response = client.post(
            "/api/v1/recipes/parse-ingredients",
            json={"texts": []},
        )
        assert response.status_code == 422


class TestSearchRecipes:
    """Tests for GET /recipes/search endpoint."""

    def test_search_empty_query(self, client):
        """Test search with empty query."""
        response = client.get("/api/v1/recipes/search?q=")
        assert response.status_code == 422
