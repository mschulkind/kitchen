"""Prompt Builder - Context for AI cooking assistance. 📝

Generates formatted context for external LLM chats.

Fun fact: Claude can process recipe context and suggest real-time
substitutions based on what you have in your kitchen! 🤖
"""

from typing import cast

from src.api.app.domain.cooking.models import ContextExportResponse, CookingContext
from src.api.app.domain.pantry.models import PantryItem
from src.api.app.domain.planning.delta_service import DeltaService
from src.api.app.domain.recipes.models import ParsedIngredient, Recipe, RecipeIngredient


class PromptBuilder:
    """Builds cooking context for AI assistants. 🤖

    Generates rich context that can be pasted into Claude, GPT, etc.

    Example:
        >>> builder = PromptBuilder()
        >>> context = builder.build_context(recipe, pantry_items)
        >>> print(builder.format_for_clipboard(context))
    """

    # Template for context export
    CONTEXT_TEMPLATE = """# Cooking: {title}

## Recipe Info
- **Source**: {source}
- **Servings**: {servings}

## Ingredients
{ingredients}

## Instructions
{instructions}

## What I Have
{available}

## What I Need
{missing}

{substitutions}

{preferences}

---
*Context exported from Kitchen App. Ask me for help with this recipe!*
"""

    def __init__(
        self,
        delta_service: DeltaService | None = None,
    ) -> None:
        """Initialize the builder.

        Args:
            delta_service: For comparing recipe to inventory.
        """
        self.delta_service = delta_service or DeltaService()

    def build_context(
        self,
        recipe: Recipe,
        pantry_items: list[PantryItem],
        *,
        user_preferences: list[str] | None = None,
    ) -> CookingContext:
        """Build cooking context from recipe and inventory.

        Args:
            recipe: The recipe to cook.
            pantry_items: Current pantry items.
            user_preferences: User's cooking preferences.

        Returns:
            CookingContext with all relevant info.
        """
        # Format ingredients as strings
        ingredients = []
        for ing in recipe.ingredients or []:
            parts = []
            if ing.quantity:
                parts.append(str(ing.quantity))
            if ing.unit and ing.unit != "count":
                parts.append(ing.unit)
            parts.append(ing.item_name)
            if ing.notes:
                parts.append(f"({ing.notes})")
            ingredients.append(" ".join(parts))

        # Compare to inventory
        recipe_ingredients = cast(
            list[RecipeIngredient | ParsedIngredient],
            recipe.ingredients or [],
        )
        result = self.delta_service.calculate_missing(
            recipe_ingredients,
            pantry_items,
        )

        available = [
            f"✓ {item.item_name}" for item in result.have_enough
        ]
        missing = [
            f"✗ {item.item_name} ({item.delta_quantity} {item.delta_unit})"
            for item in result.missing
        ]
        partial = [
            f"△ {item.item_name} (need more)"
            for item in result.partial
        ]

        # Generate substitution hints
        substitutions = self._generate_substitution_hints(
            [item.item_name for item in result.missing],
            pantry_items,
        )

        return CookingContext(
            recipe_title=recipe.title,
            recipe_source=recipe.source_url,
            servings=recipe.servings or 2,
            ingredients=ingredients,
            instructions=recipe.instructions or [],
            available_ingredients=available,
            missing_ingredients=missing + partial,
            substitution_hints=substitutions,
            user_preferences=user_preferences or [],
        )

    def format_for_clipboard(
        self,
        context: CookingContext,
        format: str = "markdown",
    ) -> ContextExportResponse:
        """Format context for copying to clipboard.

        Args:
            context: The cooking context.
            format: Output format ("markdown", "text", "json").

        Returns:
            ContextExportResponse with formatted content.
        """
        if format == "json":
            import json
            content = json.dumps(context.model_dump(), indent=2)
        elif format == "text":
            content = self._format_text(context)
        else:
            content = self._format_markdown(context)

        return ContextExportResponse(
            content=content,
            format=format,
            character_count=len(content),
        )

    def _format_markdown(self, context: CookingContext) -> str:
        """Format context as Markdown."""
        ingredients_str = "\n".join(f"- {ing}" for ing in context.ingredients)
        instructions_str = "\n".join(
            f"{i+1}. {step}" for i, step in enumerate(context.instructions)
        )
        available_str = "\n".join(context.available_ingredients) or "- (none)"
        missing_str = "\n".join(context.missing_ingredients) or "- (none)"

        substitutions = ""
        if context.substitution_hints:
            substitutions = "## Possible Substitutions\n"
            substitutions += "\n".join(f"- {s}" for s in context.substitution_hints)

        preferences = ""
        if context.user_preferences:
            preferences = "## My Preferences\n"
            preferences += "\n".join(f"- {p}" for p in context.user_preferences)

        return self.CONTEXT_TEMPLATE.format(
            title=context.recipe_title,
            source=context.recipe_source or "Unknown",
            servings=context.servings,
            ingredients=ingredients_str,
            instructions=instructions_str,
            available=available_str,
            missing=missing_str,
            substitutions=substitutions,
            preferences=preferences,
        )

    def _format_text(self, context: CookingContext) -> str:
        """Format context as plain text."""
        lines = [
            f"COOKING: {context.recipe_title}",
            "",
            "INGREDIENTS:",
        ]
        for ing in context.ingredients:
            lines.append(f"  - {ing}")

        lines.append("")
        lines.append("INSTRUCTIONS:")
        for i, step in enumerate(context.instructions):
            lines.append(f"  {i+1}. {step}")

        lines.append("")
        lines.append("WHAT I HAVE:")
        for item in context.available_ingredients:
            lines.append(f"  {item}")

        lines.append("")
        lines.append("WHAT I NEED:")
        for item in context.missing_ingredients:
            lines.append(f"  {item}")

        return "\n".join(lines)

    def _generate_substitution_hints(
        self,
        missing_items: list[str],
        pantry_items: list[PantryItem],
    ) -> list[str]:
        """Generate substitution suggestions.

        Args:
            missing_items: Items the user is missing.
            pantry_items: What they have.

        Returns:
            List of substitution suggestions.
        """
        hints = []

        # Common substitutions map
        substitutions = {
            "butter": ["coconut oil", "olive oil", "margarine"],
            "milk": ["oat milk", "almond milk", "coconut milk", "cream + water"],
            "egg": ["flax egg", "banana", "applesauce"],
            "sour cream": ["greek yogurt", "cottage cheese"],
            "buttermilk": ["milk + lemon juice", "milk + vinegar"],
            "cream": ["coconut cream", "evaporated milk"],
            "lemon juice": ["lime juice", "vinegar"],
            "brown sugar": ["white sugar + molasses", "honey"],
            "bread crumbs": ["crushed crackers", "oats", "panko"],
            "chicken broth": ["vegetable broth", "water + bouillon"],
        }

        pantry_names = {item.name.lower() for item in pantry_items}

        for missing in missing_items:
            missing_lower = missing.lower()
            for item, subs in substitutions.items():
                if item in missing_lower:
                    available_subs = [s for s in subs if any(p in s.lower() for p in pantry_names)]
                    if available_subs:
                        hints.append(f"{missing}: Try {available_subs[0]} instead")
                    else:
                        hints.append(f"{missing}: Could substitute with {subs[0]}")
                    break

        return hints
