"""Voice Service - Voice command processing. 🎙️

Handles voice commands from Google Assistant, Alexa, etc.
Wires parsed commands to actual DB operations via Supabase.

Fun fact: Voice shopping is expected to reach $40 billion by 2027! 🛒
"""

from uuid import UUID, uuid4

from supabase import AsyncClient

from src.api.app.domain.voice.models import (
    ParsedVoiceCommand,
    VoiceCommandType,
    VoiceWebhookRequest,
    VoiceWebhookResponse,
)
from src.api.app.domain.voice.parser import VoiceParser


class VoiceService:
    """Service for processing voice commands. 🎤

    Orchestrates parsing and action execution against Supabase.

    Example:
        >>> service = VoiceService(supabase_client)
        >>> response = await service.process_command(household_id, request)
        >>> print(response.message)  # "Added milk to your shopping list"
    """

    def __init__(
        self,
        supabase: AsyncClient | None = None,
        parser: VoiceParser | None = None,
    ) -> None:
        self.supabase = supabase
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

        item_names = [item.name for item in parsed.items]

        if self.supabase:
            rows = [
                {
                    "id": str(uuid4()),
                    "household_id": str(household_id),
                    "name": item.name,
                    "quantity": str(int(item.quantity)) if item.quantity != 1.0 else "1",
                    "unit": item.unit,
                    "category": "Other",
                    "checked": False,
                }
                for item in parsed.items
            ]
            await self.supabase.table("shopping_list").insert(rows).execute()

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

        if self.supabase:
            for name in item_names:
                await (
                    self.supabase.table("shopping_list")
                    .delete()
                    .eq("household_id", str(household_id))
                    .ilike("name", name)
                    .execute()
                )

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

        if self.supabase:
            for name in item_names:
                await (
                    self.supabase.table("shopping_list")
                    .update({"checked": True})
                    .eq("household_id", str(household_id))
                    .ilike("name", name)
                    .execute()
                )

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

        if self.supabase:
            result = await (
                self.supabase.table("pantry_items")
                .select("name, quantity, unit, location")
                .eq("household_id", str(household_id))
                .ilike("name", f"%{item_name}%")
                .execute()
            )
            matches = result.data or []
            if matches:
                item = matches[0]
                loc = item.get("location", "pantry")
                qty = item.get("quantity", "some")
                unit = item.get("unit", "")
                message = f"Yes! You have {qty} {unit} of {item['name']} in the {loc}."
            else:
                message = f"No, I don't see any {item_name} in your pantry."
        else:
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
        location = parsed.raw_text.lower()
        if "fridge" in location:
            loc = "fridge"
        elif "freezer" in location:
            loc = "freezer"
        else:
            loc = "pantry"

        if self.supabase:
            rows = [
                {
                    "id": str(uuid4()),
                    "household_id": str(household_id),
                    "name": item.name,
                    "quantity": int(item.quantity),
                    "unit": item.unit or "count",
                    "location": loc,
                }
                for item in parsed.items
            ]
            await self.supabase.table("pantry_items").insert(rows).execute()

        message = f"Added {', '.join(item_names)} to your {loc}."

        return VoiceWebhookResponse(
            success=True,
            message=message,
            items_added=item_names,
            command_type=VoiceCommandType.ADD_PANTRY,
        )
