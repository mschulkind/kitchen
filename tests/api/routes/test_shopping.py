"""Tests for Shopping List API Routes. 🛒

Tests for shopping list management endpoints.

Fun fact: The average shopping trip takes 43 minutes! ⏱️
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.api.app.domain.shopping.service import ShoppingService
from src.api.app.routes.shopping import get_shopping_service
from src.api.main import app


@pytest.fixture
def mock_shopping_service():
    """Create a mock ShoppingService."""
    return AsyncMock(spec=ShoppingService)


@pytest.fixture
def client(mock_shopping_service):
    """Create a test client with mocked dependencies."""

    async def override_get_shopping_service():
        yield mock_shopping_service

    app.dependency_overrides[get_shopping_service] = override_get_shopping_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestListShoppingLists:
    """Tests for GET /shopping/lists endpoint."""

    def test_list_shopping_lists_endpoint_exists(self, client):
        """Test the list endpoint exists and responds."""
        response = client.get("/api/v1/shopping/lists")
        # Should not be 404 (not found)
        assert response.status_code != 404


class TestGetActiveList:
    """Tests for GET /shopping/lists/active endpoint."""

    def test_get_active_list_invalid_path(self, client):
        """Test typos in path get rejected."""
        response = client.get("/api/v1/shopping/lists/actve")  # Typo
        assert response.status_code == 422  # Invalid UUID


class TestCreateShoppingList:
    """Tests for POST /shopping/lists endpoint."""

    def test_create_list_invalid_name_type(self, client):
        """Test list creation with wrong type."""
        response = client.post(
            "/api/v1/shopping/lists",
            json={"name": 123},  # Wrong type
        )
        assert response.status_code == 422


class TestGetShoppingList:
    """Tests for GET /shopping/lists/{list_id} endpoint."""

    def test_get_list_invalid_id(self, client):
        """Test getting list with invalid UUID."""
        response = client.get("/api/v1/shopping/lists/not-a-uuid")
        assert response.status_code == 422


class TestCompleteList:
    """Tests for POST /shopping/lists/{list_id}/complete endpoint."""

    def test_complete_list_invalid_id(self, client):
        """Test completing list with invalid UUID."""
        response = client.post("/api/v1/shopping/lists/not-a-uuid/complete")
        assert response.status_code == 422


class TestDeleteList:
    """Tests for DELETE /shopping/lists/{list_id} endpoint."""

    def test_delete_list_invalid_id(self, client):
        """Test deleting list with invalid UUID."""
        response = client.delete("/api/v1/shopping/lists/not-a-uuid")
        assert response.status_code == 422


class TestAddItem:
    """Tests for POST /shopping/lists/{list_id}/items endpoint."""

    def test_add_item_validation(self, client):
        """Test add item validates input."""
        list_id = str(uuid4())
        response = client.post(
            f"/api/v1/shopping/lists/{list_id}/items",
            json={},  # Missing required fields
        )
        assert response.status_code == 422

    def test_add_item_empty_name(self, client):
        """Test adding item with empty name is rejected."""
        list_id = str(uuid4())
        response = client.post(
            f"/api/v1/shopping/lists/{list_id}/items",
            json={"name": "", "quantity": 1, "unit": "count"},
        )
        assert response.status_code == 422

    def test_add_item_negative_quantity(self, client):
        """Test adding item with negative quantity is rejected."""
        list_id = str(uuid4())
        response = client.post(
            f"/api/v1/shopping/lists/{list_id}/items",
            json={"name": "Milk", "quantity": -1, "unit": "gallon"},
        )
        assert response.status_code == 422


class TestUpdateItem:
    """Tests for PATCH /shopping/lists/{list_id}/items/{item_id} endpoint."""

    def test_update_item_invalid_list_id(self, client):
        """Test update with invalid list UUID."""
        item_id = str(uuid4())
        response = client.patch(
            f"/api/v1/shopping/lists/not-a-uuid/items/{item_id}",
            json={"quantity": 2},
        )
        assert response.status_code == 422

    def test_update_item_invalid_item_id(self, client):
        """Test update with invalid item UUID."""
        list_id = str(uuid4())
        response = client.patch(
            f"/api/v1/shopping/lists/{list_id}/items/not-a-uuid",
            json={"quantity": 2},
        )
        assert response.status_code == 422


class TestCheckItem:
    """Tests for POST /shopping/lists/{list_id}/items/{item_id}/check endpoint."""

    def test_check_item_invalid_list_id(self, client):
        """Test check with invalid list UUID."""
        item_id = str(uuid4())
        response = client.post(f"/api/v1/shopping/lists/not-a-uuid/items/{item_id}/check")
        assert response.status_code == 422

    def test_check_item_invalid_item_id(self, client):
        """Test check with invalid item UUID."""
        list_id = str(uuid4())
        response = client.post(f"/api/v1/shopping/lists/{list_id}/items/not-a-uuid/check")
        assert response.status_code == 422


class TestUncheckItem:
    """Tests for POST /shopping/lists/{list_id}/items/{item_id}/uncheck endpoint."""

    def test_uncheck_item_invalid_list_id(self, client):
        """Test uncheck with invalid list UUID."""
        item_id = str(uuid4())
        response = client.post(f"/api/v1/shopping/lists/not-a-uuid/items/{item_id}/uncheck")
        assert response.status_code == 422

    def test_uncheck_item_invalid_item_id(self, client):
        """Test uncheck with invalid item UUID."""
        list_id = str(uuid4())
        response = client.post(f"/api/v1/shopping/lists/{list_id}/items/not-a-uuid/uncheck")
        assert response.status_code == 422


class TestDeleteItem:
    """Tests for DELETE /shopping/lists/{list_id}/items/{item_id} endpoint."""

    def test_delete_item_invalid_list_id(self, client):
        """Test delete with invalid list UUID."""
        item_id = str(uuid4())
        response = client.delete(f"/api/v1/shopping/lists/not-a-uuid/items/{item_id}")
        assert response.status_code == 422

    def test_delete_item_invalid_item_id(self, client):
        """Test delete with invalid item UUID."""
        list_id = str(uuid4())
        response = client.delete(f"/api/v1/shopping/lists/{list_id}/items/not-a-uuid")
        assert response.status_code == 422


class TestClearChecked:
    """Tests for POST /shopping/lists/{list_id}/clear-checked endpoint."""

    def test_clear_checked_invalid_id(self, client):
        """Test clear checked with invalid UUID."""
        # Note: This tests the path with an invalid UUID format
        response = client.post("/api/v1/shopping/lists/not-a-uuid/clear-checked")
        assert response.status_code == 422
