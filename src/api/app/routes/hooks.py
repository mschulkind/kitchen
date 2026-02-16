"""Webhook routes for voice assistants. 🎙️

REST endpoints for Google Assistant, Alexa, Home Assistant.

Fun fact: Over 4 billion devices now have voice assistants! 📱
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status

from src.api.app.core.config import get_settings
from src.api.app.domain.voice.models import (
    VoiceWebhookRequest,
    VoiceWebhookResponse,
)
from src.api.app.domain.voice.service import VoiceService

router = APIRouter(prefix="/hooks", tags=["Webhooks 🔊"])


async def get_voice_service() -> VoiceService:
    """Dependency injection for VoiceService."""
    return VoiceService()


async def verify_webhook_key(
    key: Annotated[str | None, Header(alias="X-Webhook-Key")] = None,
    api_key: str | None = None,
) -> bool:
    """Verify the webhook API key.

    Supports both header and query parameter for flexibility.
    """
    settings = get_settings()
    expected_key = settings.webhook_secret

    # Allow if no key configured (dev mode)
    if not expected_key:
        return True

    provided_key = key or api_key
    if not provided_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    if provided_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return True


# TODO: Replace with actual auth
async def get_household_from_key() -> UUID:
    """Get household ID from API key.

    In production, would map API keys to households.
    """
    return UUID("a0000000-0000-0000-0000-000000000001")


@router.post("/add-item", response_model=VoiceWebhookResponse)
async def webhook_add_item(
    request: VoiceWebhookRequest,
    service: Annotated[VoiceService, Depends(get_voice_service)],
    household_id: Annotated[UUID, Depends(get_household_from_key)],
    _verified: Annotated[bool, Depends(verify_webhook_key)],
) -> VoiceWebhookResponse:
    """Add items to shopping list via voice. 🎤

    Endpoint for Google Assistant, Alexa, or Home Assistant.

    Example:
        POST /hooks/add-item
        {"text": "bread and milk"}

    Returns spoken response for the voice assistant.
    """
    return await service.process_command(household_id, request)


@router.post("/voice", response_model=VoiceWebhookResponse)
async def webhook_voice_command(
    request: VoiceWebhookRequest,
    service: Annotated[VoiceService, Depends(get_voice_service)],
    household_id: Annotated[UUID, Depends(get_household_from_key)],
    _verified: Annotated[bool, Depends(verify_webhook_key)],
) -> VoiceWebhookResponse:
    """General voice command endpoint. 🎤

    Handles all voice command types:
    - "Add bread to my list"
    - "Check off milk"
    - "Do we have eggs?"

    The command is parsed to determine intent.
    """
    return await service.process_command(household_id, request)


@router.get("/health")
async def webhook_health() -> dict:
    """Health check for webhook endpoint. ❤️

    Useful for uptime monitoring.
    """
    return {"status": "ok", "service": "voice-webhook"}
