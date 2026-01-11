"""Voice service tests. 🎙️"""

from uuid import uuid4

import pytest

from src.api.app.domain.voice.models import (
    VoiceCommandType,
    VoiceWebhookRequest,
)
from src.api.app.domain.voice.service import VoiceService


class TestVoiceService:
    """Tests for VoiceService."""

    @pytest.fixture
    def service(self) -> VoiceService:
        """Create service instance."""
        return VoiceService()

    @pytest.fixture
    def household_id(self):
        return uuid4()

    @pytest.mark.asyncio
    async def test_add_item_success(self, service: VoiceService, household_id):
        """Test adding item via voice."""
        request = VoiceWebhookRequest(text="Add bread to my list")
        response = await service.process_command(household_id, request)

        assert response.success is True
        assert response.command_type == VoiceCommandType.ADD_ITEM
        assert "bread" in response.items_added
        assert "bread" in response.message.lower()

    @pytest.mark.asyncio
    async def test_add_multiple_items(self, service: VoiceService, household_id):
        """Test adding multiple items."""
        request = VoiceWebhookRequest(text="Add bread and milk")
        response = await service.process_command(household_id, request)

        assert response.success is True
        assert len(response.items_added) == 2

    @pytest.mark.asyncio
    async def test_check_item(self, service: VoiceService, household_id):
        """Test checking off an item."""
        request = VoiceWebhookRequest(text="Check off the milk")
        response = await service.process_command(household_id, request)

        assert response.success is True
        assert response.command_type == VoiceCommandType.CHECK_ITEM

    @pytest.mark.asyncio
    async def test_inventory_question(self, service: VoiceService, household_id):
        """Test asking about inventory."""
        request = VoiceWebhookRequest(text="Do we have eggs?")
        response = await service.process_command(household_id, request)

        assert response.command_type == VoiceCommandType.ASK_INVENTORY

    @pytest.mark.asyncio
    async def test_unknown_command(self, service: VoiceService, household_id):
        """Test handling unknown command."""
        request = VoiceWebhookRequest(
            text="This is a very long and confusing sentence that doesn't make sense"
        )
        response = await service.process_command(household_id, request)

        # Should still parse to some extent
        assert response is not None

    @pytest.mark.asyncio
    async def test_source_preserved(self, service: VoiceService, household_id):
        """Test source platform is accepted."""
        request = VoiceWebhookRequest(
            text="Add milk",
            source="google_assistant",
        )
        response = await service.process_command(household_id, request)

        assert response.success is True
