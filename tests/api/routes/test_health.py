"""Tests for Health Route. ❤️

Tests the application health check endpoint.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


class TestHealthEndpoint:
    """Tests for GET /health endpoint."""

    def test_health_check(self, client):
        """Test basic health check returns ok."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "kitchen-api"

    def test_readiness_check(self, client):
        """Test readiness check endpoint."""
        response = client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data
