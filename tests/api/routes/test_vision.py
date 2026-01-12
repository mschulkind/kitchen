"""Tests for Vision API Routes. 📸

Tests for visual inventory scanning endpoints.

Fun fact: GPT-4V can identify over 10,000 different food items! 🍕
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


class TestAnalyzeImage:
    """Tests for POST /vision/analyze endpoint."""

    def test_analyze_validation(self, client):
        """Test analyze validates input - missing required field."""
        response = client.post(
            "/api/v1/vision/analyze",
            json={},  # Missing required fields
        )
        assert response.status_code == 422


class TestConfirmItems:
    """Tests for POST /vision/confirm endpoint."""

    def test_confirm_validation(self, client):
        """Test confirm validates input - missing required fields."""
        response = client.post(
            "/api/v1/vision/confirm",
            json={},  # Missing required fields
        )
        assert response.status_code == 422

    def test_confirm_empty_items(self, client):
        """Test confirm with empty items list returns success with 0 created."""
        response = client.post(
            "/api/v1/vision/confirm",
            json={"scan_id": str(uuid4()), "items": []},
        )
        # Empty items is allowed - returns success with 0 created
        assert response.status_code == 200
        data = response.json()
        assert data["created_count"] == 0

    def test_confirm_missing_scan_id(self, client):
        """Test confirm without scan_id."""
        response = client.post(
            "/api/v1/vision/confirm",
            json={
                "items": [{"name": "Milk", "quantity": 1, "unit": "gallon"}],
            },
        )
        assert response.status_code == 422


class TestQuickScan:
    """Tests for POST /vision/quick-scan endpoint."""

    def test_quick_scan_validation(self, client):
        """Test quick-scan validates input - missing required field."""
        response = client.post(
            "/api/v1/vision/quick-scan",
            json={},  # Missing required fields
        )
        assert response.status_code == 422

    def test_quick_scan_invalid_location(self, client):
        """Test quick-scan with invalid location."""
        response = client.post(
            "/api/v1/vision/quick-scan",
            json={"image_url": "https://example.com/img.jpg", "location": "invalid"},
        )
        assert response.status_code == 422
