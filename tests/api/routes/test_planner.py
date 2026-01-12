"""Tests for Planner API Routes. 🎲

Tests for meal planning endpoints.

Fun fact: Meal planning can reduce food waste by up to 25%! ♻️
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.api.app.domain.planner.service import PlannerService
from src.api.app.routes.planner import get_planner_service
from src.api.main import app


@pytest.fixture
def mock_planner_service():
    """Create a mock PlannerService."""
    return AsyncMock(spec=PlannerService)


@pytest.fixture
def client(mock_planner_service):
    """Create a test client with mocked dependencies."""

    async def override_get_planner_service():
        yield mock_planner_service

    app.dependency_overrides[get_planner_service] = override_get_planner_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestListPlans:
    """Tests for GET /planner/plans endpoint."""

    def test_list_plans_endpoint_exists(self, client):
        """Test the list endpoint exists and responds."""
        response = client.get("/api/v1/planner/plans")
        # Should not be 404 (not found)
        assert response.status_code != 404


class TestGetPlan:
    """Tests for GET /planner/plans/{plan_id} endpoint."""

    def test_get_plan_invalid_id(self, client):
        """Test getting plan with invalid UUID."""
        response = client.get("/api/v1/planner/plans/not-a-uuid")
        assert response.status_code == 422


class TestGenerateOptions:
    """Tests for POST /planner/generate endpoint."""

    def test_generate_validation(self, client):
        """Test generate validates input."""
        response = client.post(
            "/api/v1/planner/generate",
            json={},  # Missing required fields
        )
        assert response.status_code == 422

    def test_generate_invalid_days(self, client):
        """Test generate with invalid days count."""
        response = client.post(
            "/api/v1/planner/generate",
            json={"days": 0},  # Must be >= 1
        )
        assert response.status_code == 422

    def test_generate_negative_days(self, client):
        """Test generate with negative days."""
        response = client.post(
            "/api/v1/planner/generate",
            json={"days": -3},
        )
        assert response.status_code == 422


class TestScoreRecipes:
    """Tests for POST /planner/score-recipes endpoint."""

    def test_score_recipes_limit_validation(self, client):
        """Test score-recipes validates limit."""
        response = client.post("/api/v1/planner/score-recipes?limit=0")
        assert response.status_code == 422

    def test_score_recipes_limit_max(self, client):
        """Test score-recipes enforces max limit."""
        response = client.post("/api/v1/planner/score-recipes?limit=100")
        assert response.status_code == 422


class TestGetActivePlan:
    """Tests for GET /planner/plans/active endpoint."""

    def test_get_active_plan_invalid_path(self, client):
        """Test typos in path get rejected."""
        response = client.get("/api/v1/planner/plans/actve")  # Typo
        assert response.status_code == 422  # Invalid UUID


class TestActivatePlan:
    """Tests for POST /planner/plans/{plan_id}/activate endpoint."""

    def test_activate_invalid_plan_id(self, client):
        """Test activate with invalid plan UUID."""
        response = client.post("/api/v1/planner/plans/not-a-uuid/activate")
        assert response.status_code == 422


class TestCompletePlan:
    """Tests for POST /planner/plans/{plan_id}/complete endpoint."""

    def test_complete_invalid_plan_id(self, client):
        """Test complete with invalid plan UUID."""
        response = client.post("/api/v1/planner/plans/not-a-uuid/complete")
        assert response.status_code == 422


class TestDeletePlan:
    """Tests for DELETE /planner/plans/{plan_id} endpoint."""

    def test_delete_plan_invalid_id(self, client):
        """Test deleting plan with invalid UUID."""
        response = client.delete("/api/v1/planner/plans/not-a-uuid")
        assert response.status_code == 422


class TestLockSlot:
    """Tests for POST /planner/plans/{plan_id}/slots/{slot_id}/lock endpoint."""

    def test_lock_invalid_plan_id(self, client):
        """Test lock with invalid plan UUID."""
        slot_id = str(uuid4())
        response = client.post(f"/api/v1/planner/plans/not-a-uuid/slots/{slot_id}/lock")
        assert response.status_code == 422

    def test_lock_invalid_slot_id(self, client):
        """Test lock with invalid slot UUID."""
        plan_id = str(uuid4())
        response = client.post(f"/api/v1/planner/plans/{plan_id}/slots/not-a-uuid/lock")
        assert response.status_code == 422


class TestUnlockSlot:
    """Tests for POST /planner/plans/{plan_id}/slots/{slot_id}/unlock endpoint."""

    def test_unlock_invalid_plan_id(self, client):
        """Test unlock with invalid plan UUID."""
        slot_id = str(uuid4())
        response = client.post(f"/api/v1/planner/plans/not-a-uuid/slots/{slot_id}/unlock")
        assert response.status_code == 422

    def test_unlock_invalid_slot_id(self, client):
        """Test unlock with invalid slot UUID."""
        plan_id = str(uuid4())
        response = client.post(f"/api/v1/planner/plans/{plan_id}/slots/not-a-uuid/unlock")
        assert response.status_code == 422
