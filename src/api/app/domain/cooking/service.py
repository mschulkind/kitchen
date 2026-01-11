"""Cooking Service - Chef's Companion logic. 👨‍🍳

Handles cooking sessions, context export, and inventory consumption.

Fun fact: Marking items as "cooked" and deducting inventory can
reduce food waste by up to 30%! 🌍
"""

from datetime import datetime
from uuid import uuid4

from src.api.app.domain.cooking.models import (
    ContextExportRequest,
    ContextExportResponse,
    CookingContext,
    CookingSession,
    MarkCookedRequest,
    MarkCookedResponse,
    MiseEnPlaceItem,
    RecipeStep,
)
from src.api.app.domain.cooking.prompt_builder import PromptBuilder
from src.api.app.domain.pantry.models import PantryItem
from src.api.app.domain.planning.delta_service import DeltaService
from src.api.app.domain.recipes.models import Recipe


class CookingService:
    """Service for cooking assistance. 👨‍🍳

    Provides context export, recipe views, and consumption tracking.

    Example:
        >>> service = CookingService()
        >>> context = await service.get_cooking_context(recipe_id)
        >>> print(service.export_for_clipboard(context))
    """

    def __init__(
        self,
        prompt_builder: PromptBuilder | None = None,
        delta_service: DeltaService | None = None,
    ) -> None:
        """Initialize the service.

        Args:
            prompt_builder: For context generation.
            delta_service: For inventory comparison.
        """
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.delta_service = delta_service or DeltaService()

    async def get_cooking_context(
        self,
        recipe: Recipe,
        pantry_items: list[PantryItem],
        *,
        user_preferences: list[str] | None = None,
    ) -> CookingContext:
        """Get cooking context for a recipe.

        Args:
            recipe: The recipe to cook.
            pantry_items: Current inventory.
            user_preferences: User's preferences.

        Returns:
            CookingContext with all info needed.
        """
        return self.prompt_builder.build_context(
            recipe,
            pantry_items,
            user_preferences=user_preferences,
        )

    async def export_context(
        self,
        recipe: Recipe,
        pantry_items: list[PantryItem],
        request: ContextExportRequest,
    ) -> ContextExportResponse:
        """Export cooking context for clipboard.

        Args:
            recipe: The recipe.
            pantry_items: Current inventory.
            request: Export configuration.

        Returns:
            ContextExportResponse with formatted content.
        """
        context = await self.get_cooking_context(recipe, pantry_items)
        return self.prompt_builder.format_for_clipboard(context, request.format)

    async def get_mise_en_place(
        self,
        recipe: Recipe,
    ) -> list[MiseEnPlaceItem]:
        """Generate mise en place checklist for a recipe.

        Breaks down ingredients into prep tasks.

        Args:
            recipe: The recipe.

        Returns:
            List of prep tasks.
        """
        items = []

        for order, ing in enumerate(recipe.ingredients or []):
            # Parse notes for prep instructions
            prep_task = ing.item_name
            if ing.notes:
                prep_task = f"{ing.notes.capitalize()} {ing.item_name}"

            # Add quantity
            if ing.quantity:
                qty_str = f"{ing.quantity}"
                if ing.unit and ing.unit != "count":
                    qty_str += f" {ing.unit}"
                prep_task = f"Prepare {qty_str} {prep_task}"
            else:
                prep_task = f"Prepare {prep_task}"

            items.append(MiseEnPlaceItem(
                task=prep_task,
                ingredient=ing.item_name,
                order=order,
            ))

        return items

    async def get_recipe_steps(
        self,
        recipe: Recipe,
    ) -> list[RecipeStep]:
        """Get recipe as step-by-step cards.

        Parses instructions into individual steps.

        Args:
            recipe: The recipe.

        Returns:
            List of cooking steps.
        """
        steps = []

        for i, instruction in enumerate(recipe.instructions or []):
            # Try to detect timer requirements
            timer_required = any(
                word in instruction.lower()
                for word in ["minute", "hour", "second", "timer", "wait", "rest"]
            )

            # Try to extract duration
            duration = None
            import re
            time_match = re.search(r"(\d+)\s*(minute|min|hour|hr)", instruction.lower())
            if time_match:
                amount = int(time_match.group(1))
                unit = time_match.group(2)
                duration = amount * 60 if "hour" in unit or "hr" in unit else amount

            steps.append(RecipeStep(
                number=i + 1,
                instruction=instruction,
                duration_minutes=duration,
                timer_required=timer_required,
            ))

        return steps

    async def mark_cooked(
        self,
        recipe: Recipe,
        pantry_items: list[PantryItem],
        request: MarkCookedRequest,
    ) -> MarkCookedResponse:
        """Mark a recipe as cooked and deduct inventory.

        Args:
            recipe: The cooked recipe.
            pantry_items: Current inventory.
            request: Cook request with servings.

        Returns:
            MarkCookedResponse with results.
        """
        items_decremented = []
        warnings = []

        if not request.deduct_inventory:
            return MarkCookedResponse(
                success=True,
                items_decremented=[],
            )

        # Calculate what was used
        for ing in recipe.ingredients or []:
            if not ing.quantity:
                continue

            # Scale by servings
            recipe_servings = recipe.servings or 2
            scale_factor = request.servings_made / recipe_servings
            used_quantity = ing.quantity * scale_factor

            # Find matching pantry item
            matched = False
            for pantry_item in pantry_items:
                if pantry_item.name.lower() == ing.item_name.lower():
                    matched = True
                    # In production: update database
                    items_decremented.append(
                        f"{ing.item_name}: -{used_quantity} {ing.unit or 'units'}"
                    )
                    break

            if not matched:
                warnings.append(f"Couldn't find {ing.item_name} in pantry")

        return MarkCookedResponse(
            success=True,
            items_decremented=items_decremented,
            warnings=warnings,
        )

    async def start_cooking_session(
        self,
        recipe: Recipe,
        servings: int = 2,
    ) -> CookingSession:
        """Start a new cooking session.

        Args:
            recipe: The recipe to cook.
            servings: Number of servings to make.

        Returns:
            New CookingSession.
        """
        total_steps = len(recipe.instructions or [])

        return CookingSession(
            id=uuid4(),
            recipe_id=recipe.id,
            recipe_title=recipe.title,
            started_at=datetime.now(),
            current_step=1,
            total_steps=total_steps,
            mise_en_place_completed=False,
            servings=servings,
        )
