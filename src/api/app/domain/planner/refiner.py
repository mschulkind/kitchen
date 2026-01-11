"""Refiner Service - Slot Machine Logic. 🎰

Handles meal slot locking, re-rolling, and refinement with directives.

Fun fact: The "slot machine" metaphor comes from the satisfying randomness
of pulling a lever and getting a new combination! 🎲
"""

import random
from uuid import UUID, uuid4

from src.api.app.domain.pantry.models import PantryItem
from src.api.app.domain.planner.models import MealSlot, MealType, RecipeStub
from src.api.app.domain.planner.scorer import RecipeScorer
from src.api.app.domain.recipes.models import Recipe


class RefinerService:
    """Service for refining meal plan slots. 🎰

    Handles the "spin" mechanics - locking meals and re-rolling
    with optional directives.

    Example:
        >>> refiner = RefinerService()
        >>> new_recipe = await refiner.reroll_slot(slot, recipes, pantry, "Make it spicy")
        >>> print(f"New recipe: {new_recipe.title}")
    """

    def __init__(
        self,
        scorer: RecipeScorer | None = None,
    ) -> None:
        """Initialize the refiner.

        Args:
            scorer: Recipe scorer for ranking alternatives.
        """
        self.scorer = scorer or RecipeScorer()

    async def reroll_slot(
        self,
        slot: MealSlot,
        available_recipes: list[Recipe],
        pantry_items: list[PantryItem],
        directive: str | None = None,
        *,
        exclude_recipe_ids: list[UUID] | None = None,
    ) -> RecipeStub:
        """Re-roll a single meal slot.

        Finds an alternative recipe for the slot, respecting:
        - Locked slots (won't change those)
        - User directives ("Make it spicy", "No chicken")
        - Inventory optimization

        Args:
            slot: The slot to re-roll.
            available_recipes: All available recipes.
            pantry_items: Current inventory.
            directive: Optional text directive (e.g., "Make it healthy").
            exclude_recipe_ids: Recipe IDs to exclude from selection.

        Returns:
            RecipeStub for the new recipe.

        Raises:
            ValueError: If slot is locked.
        """
        if slot.is_locked:
            raise ValueError(f"Cannot reroll locked slot {slot.id}")

        exclude_ids = set(exclude_recipe_ids or [])
        if slot.recipe_id:
            exclude_ids.add(slot.recipe_id)

        # Filter recipes
        candidates = [r for r in available_recipes if r.id not in exclude_ids]

        # Apply directive filter if provided
        if directive:
            candidates = self._apply_directive_filter(candidates, directive)

        if not candidates:
            raise ValueError("No suitable recipes found for reroll")

        # Score remaining candidates
        scores = self.scorer.score_recipes(candidates, pantry_items)

        # Add some randomness - pick from top 5
        top_candidates = scores[:5]
        if top_candidates:
            selected = random.choice(top_candidates)
            recipe = next(r for r in candidates if r.id == selected.recipe_id)
            return RecipeStub(
                id=recipe.id,
                title=recipe.title,
                prep_time_minutes=recipe.prep_time_minutes,
                inventory_match_percent=selected.inventory_match_percent,
                tags=recipe.tags or [],
            )

        # Fallback: random selection
        recipe = random.choice(candidates)
        return RecipeStub(
            id=recipe.id,
            title=recipe.title,
            prep_time_minutes=recipe.prep_time_minutes,
            tags=recipe.tags or [],
        )

    def _apply_directive_filter(
        self,
        recipes: list[Recipe],
        directive: str,
    ) -> list[Recipe]:
        """Apply user directive to filter recipes.

        Supports:
        - "no X" / "without X" - exclude recipes with ingredient/tag X
        - "X" / "with X" - prefer recipes with ingredient/tag X
        - "quick" / "fast" - prefer recipes under 30 min
        - "healthy" / "light" - prefer healthy-tagged recipes
        - "spicy" - prefer spicy-tagged recipes

        Args:
            recipes: Recipes to filter.
            directive: User's text directive.

        Returns:
            Filtered/sorted list of recipes.
        """
        directive_lower = directive.lower()
        result = recipes.copy()

        # Handle exclusions: "no chicken", "without mushrooms"
        exclusion_words = ["no ", "without ", "exclude "]
        for word in exclusion_words:
            if word in directive_lower:
                # Extract what to exclude
                exclude_term = directive_lower.split(word)[-1].strip().split()[0]
                result = [
                    r for r in result
                    if not self._recipe_contains(r, exclude_term)
                ]

        # Handle time preferences
        if any(w in directive_lower for w in ["quick", "fast", "easy", "simple"]):
            result = [
                r for r in result
                if r.prep_time_minutes is None or r.prep_time_minutes <= 30
            ]

        # Handle tag-based preferences
        preference_tags = {
            "healthy": ["healthy", "light", "low-fat", "vegetable"],
            "spicy": ["spicy", "hot", "cajun", "thai", "mexican"],
            "comfort": ["comfort", "hearty", "stew", "soup", "casserole"],
            "vegetarian": ["vegetarian", "vegan", "meatless"],
        }

        for keyword, tags in preference_tags.items():
            if keyword in directive_lower:
                # Boost recipes with these tags (sort to top)
                result = sorted(
                    result,
                    key=lambda r: sum(1 for t in (r.tags or []) if t.lower() in tags),
                    reverse=True,
                )

        return result

    def _recipe_contains(self, recipe: Recipe, term: str) -> bool:
        """Check if recipe contains a term in title, tags, or ingredients.

        Args:
            recipe: Recipe to check.
            term: Term to look for.

        Returns:
            True if recipe contains the term.
        """
        term_lower = term.lower()

        # Check title
        if term_lower in recipe.title.lower():
            return True

        # Check tags
        if recipe.tags and any(term_lower in tag.lower() for tag in recipe.tags):
            return True

        # Check ingredients
        if recipe.ingredients:
            for ing in recipe.ingredients:
                if term_lower in ing.item_name.lower():
                    return True

        return False

    async def toggle_lock(
        self,
        slot_id: UUID,
        locked: bool,
    ) -> MealSlot:
        """Toggle the lock state of a slot.

        Locked slots won't be changed during rerolls.

        Args:
            slot_id: The slot to lock/unlock.
            locked: New lock state.

        Returns:
            Updated MealSlot.
        """
        # In production, this would update the database
        # For now, return a mock updated slot
        from datetime import date
        return MealSlot(
            id=slot_id,
            plan_id=uuid4(),
            date=date.today(),
            meal_type=MealType.DINNER,
            is_locked=locked,
        )

    async def reroll_day(
        self,
        day_slots: list[MealSlot],
        available_recipes: list[Recipe],
        pantry_items: list[PantryItem],
        directive: str | None = None,
    ) -> list[tuple[MealSlot, RecipeStub]]:
        """Re-roll all unlocked slots for a day.

        Respects locked slots and tries to find diverse options.

        Args:
            day_slots: All slots for a single day.
            available_recipes: Available recipes.
            pantry_items: Current inventory.
            directive: Optional directive for all rerolls.

        Returns:
            List of (slot, new_recipe) tuples for unlocked slots.
        """
        results = []
        used_recipe_ids: list[UUID] = []

        # Include already-locked recipes in exclusion list
        for slot in day_slots:
            if slot.is_locked and slot.recipe_id:
                used_recipe_ids.append(slot.recipe_id)

        for slot in day_slots:
            if slot.is_locked:
                continue

            new_recipe = await self.reroll_slot(
                slot,
                available_recipes,
                pantry_items,
                directive,
                exclude_recipe_ids=used_recipe_ids,
            )

            if new_recipe.id:
                used_recipe_ids.append(new_recipe.id)

            results.append((slot, new_recipe))

        return results


class SlotMachineConfig:
    """Configuration for the slot machine behavior. ⚙️"""

    def __init__(
        self,
        *,
        randomness_factor: float = 0.3,
        prefer_variety: bool = True,
        max_rerolls_per_session: int = 10,
    ) -> None:
        """Initialize config.

        Args:
            randomness_factor: How much randomness vs optimization (0-1).
            prefer_variety: Whether to avoid recipe repetition.
            max_rerolls_per_session: Limit to prevent abuse.
        """
        self.randomness_factor = randomness_factor
        self.prefer_variety = prefer_variety
        self.max_rerolls_per_session = max_rerolls_per_session
