"""Voice domain models. 🎙️

DTOs for voice command processing.

Fun fact: The average person speaks 125-150 words per minute,
but can type only 40 words per minute! 🗣️
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class VoiceCommandType(str, Enum):
    """Type of voice command recognized. 🎤"""

    ADD_ITEM = "add_item"  # Add to shopping list
    REMOVE_ITEM = "remove_item"
    CHECK_ITEM = "check_item"  # Mark as checked
    ASK_INVENTORY = "ask_inventory"  # "Do we have milk?"
    ADD_PANTRY = "add_pantry"  # Add to pantry
    UNKNOWN = "unknown"


class ParsedVoiceItem(BaseModel):
    """An item parsed from voice input. 📝"""

    name: str
    quantity: float = 1.0
    unit: str | None = None


class ParsedVoiceCommand(BaseModel):
    """A parsed voice command. 🎤"""

    raw_text: str
    command_type: VoiceCommandType
    items: list[ParsedVoiceItem] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    error: str | None = None


class VoiceWebhookRequest(BaseModel):
    """Request from voice assistant webhook. 🔊

    Supports Google Assistant, Alexa, and Home Assistant.
    """

    text: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="The voice command text",
    )
    source: str = Field(
        default="unknown",
        description="Source platform (google, alexa, homeassistant)",
    )
    user_id: str | None = None  # For multi-user households


class VoiceWebhookResponse(BaseModel):
    """Response for voice assistant. 🎤"""

    success: bool
    message: str  # Spoken response
    items_added: list[str] = Field(default_factory=list)
    command_type: VoiceCommandType = VoiceCommandType.UNKNOWN


class VoiceLog(BaseModel):
    """Log entry for voice commands. 📋"""

    id: UUID
    household_id: UUID
    raw_text: str
    parsed_command: ParsedVoiceCommand
    success: bool
    response_message: str
    created_at: datetime
