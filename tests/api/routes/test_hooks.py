"""Tests for Webhook Routes. 🎙️

Tests the voice webhook endpoints including authentication.
Phase 9 security tests.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.app.domain.voice.models import VoiceCommandType, VoiceWebhookResponse
from src.api.app.domain.voice.service import VoiceService
from src.api.app.routes.hooks import get_voice_service, verify_webhook_key
from src.api.main import app


@pytest.fixture
def mock_voice_service():
    """Create a mock VoiceService."""
    mock = AsyncMock(spec=VoiceService)
    mock.process_command.return_value = VoiceWebhookResponse(
        success=True,
        command_type=VoiceCommandType.ADD_ITEM,
        message="Added bread to your list",
        items_added=["bread"],
    )
    return mock


@pytest.fixture
def client(mock_voice_service):
    """Create a test client with mocked dependencies."""

    async def override_get_voice_service():
        return mock_voice_service

    async def override_verify_webhook_key():
        # Allow all requests in default test mode
        return True

    app.dependency_overrides[get_voice_service] = override_get_voice_service
    app.dependency_overrides[verify_webhook_key] = override_verify_webhook_key
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def secured_client(mock_voice_service):
    """Create a test client that enforces webhook key validation."""

    async def override_get_voice_service():
        return mock_voice_service

    app.dependency_overrides[get_voice_service] = override_get_voice_service
    # Don't override verify_webhook_key - use real validation
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestWebhookAddItem:
    """Tests for POST /hooks/add-item endpoint."""

    def test_add_item_success(self, client, mock_voice_service):
        """Test adding item via webhook."""
        response = client.post(
            "/api/v1/hooks/add-item",
            json={"text": "Add bread"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "bread" in data["items_added"]

    def test_add_item_with_quantity(self, client, mock_voice_service):
        """Test adding item with quantity."""
        response = client.post(
            "/api/v1/hooks/add-item",
            json={"text": "Add 2 gallons of milk"},
        )

        assert response.status_code == 200
        mock_voice_service.process_command.assert_called_once()


class TestWebhookVoiceCommand:
    """Tests for POST /hooks/voice endpoint."""

    def test_voice_command_success(self, client, mock_voice_service):
        """Test general voice command."""
        response = client.post(
            "/api/v1/hooks/voice",
            json={"text": "Check off the milk"},
        )

        assert response.status_code == 200
        mock_voice_service.process_command.assert_called()

    def test_voice_command_with_source(self, client, mock_voice_service):
        """Test voice command with source platform."""
        response = client.post(
            "/api/v1/hooks/voice",
            json={"text": "Add eggs", "source": "google_assistant"},
        )

        assert response.status_code == 200


class TestWebhookSecurity:
    """Tests for webhook authentication. 🔒

    Phase 9 security tests.
    """

    def test_webhook_without_key_rejected_when_required(self, secured_client):
        """Test request without API key is rejected when key is configured.

        Phase 9 test: Security - Request without key returns 401.
        """
        with patch("src.api.app.routes.hooks.get_settings") as mock_settings:
            mock_settings.return_value.webhook_secret = "test-secret-key"

            response = secured_client.post(
                "/api/v1/hooks/add-item",
                json={"text": "Add bread"},
            )

            assert response.status_code == 401
            assert "Missing API key" in response.json()["detail"]

    def test_webhook_with_invalid_key_rejected(self, secured_client):
        """Test request with invalid API key is rejected.

        Phase 9 test: Security - Invalid key returns 401.
        """
        with patch("src.api.app.routes.hooks.get_settings") as mock_settings:
            mock_settings.return_value.webhook_secret = "correct-key"

            response = secured_client.post(
                "/api/v1/hooks/add-item",
                json={"text": "Add bread"},
                headers={"X-Webhook-Key": "wrong-key"},
            )

            assert response.status_code == 401
            assert "Invalid API key" in response.json()["detail"]

    def test_webhook_with_valid_key_accepted(self, secured_client, mock_voice_service):
        """Test request with valid API key is accepted.

        Phase 9 test: Security - Valid key allows access.
        """
        with patch("src.api.app.routes.hooks.get_settings") as mock_settings:
            mock_settings.return_value.webhook_secret = "valid-secret"

            response = secured_client.post(
                "/api/v1/hooks/add-item",
                json={"text": "Add bread"},
                headers={"X-Webhook-Key": "valid-secret"},
            )

            assert response.status_code == 200

    def test_webhook_dev_mode_no_key_required(self, secured_client, mock_voice_service):
        """Test dev mode (no key configured) allows all requests.

        In development, if no webhook_secret is set, all requests pass.
        """
        with patch("src.api.app.routes.hooks.get_settings") as mock_settings:
            mock_settings.return_value.webhook_secret = ""  # No key configured

            response = secured_client.post(
                "/api/v1/hooks/add-item",
                json={"text": "Add bread"},
            )

            assert response.status_code == 200


class TestWebhookHealth:
    """Tests for GET /hooks/health endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/hooks/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "voice-webhook"
