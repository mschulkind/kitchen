"""Voice Service - Voice command processing. 🎙️

Handles voice commands from Google Assistant, Alexa, etc.

Fun fact: Voice shopping is expected to reach $40 billion by 2027! 🛒
"""

from uuid import UUID

from src.api.app.domain.voice.models import (
    ParsedVoiceCommand,
    VoiceCommandType,
    VoiceWebhookRequest,
    VoiceWebhookResponse,
)
from src.api.app.domain.voice.parser import VoiceParser


class VoiceService:
    """Service for processing voice commands. 🎤

    Orchestrates parsing and action execution.

    Example:
        >>> service = VoiceService()
        >>> response = await service.process_command(request)
        >>> print(response.message)  # "Added milk to your shopping list"
    """

    def __init__(
        self,
        parser: VoiceParser | None = None,
    ) -> None:
        """Initialize the service.

        Args:
            parser: Voice command parser.
        """
        self.parser = parser or VoiceParser()

    async def process_command(
        self,
        household_id: UUID,
        request: VoiceWebhookRequest,
    ) -> VoiceWebhookResponse:
        """Process a voice command.

        Args:
            household_id: The household making the request.
            request: The voice command request.

        Returns:
            VoiceWebhookResponse with result.
        """
        # Parse the command
        parsed = self.parser.parse(request.text)

        # Execute based on command type
        match parsed.command_type:
            case VoiceCommandType.ADD_ITEM:
                return await self._handle_add_item(household_id, parsed)
            case VoiceCommandType.REMOVE_ITEM:
                return await self._handle_remove_item(household_id, parsed)
            case VoiceCommandType.CHECK_ITEM:
                return await self._handle_check_item(household_id, parsed)
            case VoiceCommandType.ASK_INVENTORY:
                return await self._handle_ask_inventory(household_id, parsed)
            case VoiceCommandType.ADD_PANTRY:
                return await self._handle_add_pantry(household_id, parsed)
            case _:
                return VoiceWebhookResponse(
                    success=False,
                    message="Sorry, I didn't understand that command.",
                    command_type=VoiceCommandType.UNKNOWN,
                )

    async def _handle_add_item(
        self,
        household_id: UUID,
        parsed: ParsedVoiceCommand,
    ) -> VoiceWebhookResponse:
        """Handle adding items to shopping list."""
        if not parsed.items:
            return VoiceWebhookResponse(
                success=False,
                message="What would you like to add?",
                command_type=VoiceCommandType.ADD_ITEM,
            )

        # In production: call ShoppingService to add items
        item_names = [item.name for item in parsed.items]

        # Format response
        if len(item_names) == 1:
            message = f"Added {item_names[0]} to your shopping list."
        elif len(item_names) == 2:
            message = f"Added {item_names[0]} and {item_names[1]} to your shopping list."
        else:
            message = f"Added {len(item_names)} items to your shopping list."

        return VoiceWebhookResponse(
            success=True,
            message=message,
            items_added=item_names,
            command_type=VoiceCommandType.ADD_ITEM,
        )

    async def _handle_remove_item(
        self,
        household_id: UUID,
        parsed: ParsedVoiceCommand,
    ) -> VoiceWebhookResponse:
        """Handle removing items from shopping list."""
        if not parsed.items:
            return VoiceWebhookResponse(
                success=False,
                message="What would you like to remove?",
                command_type=VoiceCommandType.REMOVE_ITEM,
            )

        item_names = [item.name for item in parsed.items]

        # In production: call ShoppingService to remove items
        message = f"Removed {', '.join(item_names)} from your list."

        return VoiceWebhookResponse(
            success=True,
            message=message,
            command_type=VoiceCommandType.REMOVE_ITEM,
        )

    async def _handle_check_item(
        self,
        household_id: UUID,
        parsed: ParsedVoiceCommand,
    ) -> VoiceWebhookResponse:
        """Handle checking off items."""
        if not parsed.items:
            return VoiceWebhookResponse(
                success=False,
                message="What did you get?",
                command_type=VoiceCommandType.CHECK_ITEM,
            )

        item_names = [item.name for item in parsed.items]

        # In production: call ShoppingService to check items
        message = f"Checked off {', '.join(item_names)}."

        return VoiceWebhookResponse(
            success=True,
            message=message,
            command_type=VoiceCommandType.CHECK_ITEM,
        )

    async def _handle_ask_inventory(
        self,
        household_id: UUID,
        parsed: ParsedVoiceCommand,
    ) -> VoiceWebhookResponse:
        """Handle inventory questions."""
        if not parsed.items:
            return VoiceWebhookResponse(
                success=False,
                message="What are you looking for?",
                command_type=VoiceCommandType.ASK_INVENTORY,
            )

        item_name = parsed.items[0].name

        # In production: call PantryService to check inventory
        # For now, return placeholder
        message = f"Let me check... You have some {item_name} in the fridge."

        return VoiceWebhookResponse(
            success=True,
            message=message,
            command_type=VoiceCommandType.ASK_INVENTORY,
        )

    async def _handle_add_pantry(
        self,
        household_id: UUID,
        parsed: ParsedVoiceCommand,
    ) -> VoiceWebhookResponse:
        """Handle adding items to pantry."""
        if not parsed.items:
            return VoiceWebhookResponse(
                success=False,
                message="What did you add to the pantry?",
                command_type=VoiceCommandType.ADD_PANTRY,
            )

        item_names = [item.name for item in parsed.items]

        # In production: call PantryService to add items
        message = f"Added {', '.join(item_names)} to your pantry."

        return VoiceWebhookResponse(
            success=True,
            message=message,
            items_added=item_names,
            command_type=VoiceCommandType.ADD_PANTRY,
        )
