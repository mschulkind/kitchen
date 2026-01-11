"""Recipe Scorer - Ranking recipes by inventory match. 📊

Scores recipes based on how well they match the current inventory,
prioritizing items that are expiring soon.

Fun fact: Using expiring ingredients first can reduce food waste by 40%! 🌍
"""

from datetime import date, timedelta
from typing import Sequence, cast

from src.api.app.domain.pantry.models import PantryItem
from src.api.app.domain.planner.models import RecipeScore, ScoringCriteria
from src.api.app.domain.planning.delta_service import DeltaService
from src.api.app.domain.recipes.models import ParsedIngredient, Recipe, RecipeIngredient


class RecipeScorer:
    """Scores recipes based on inventory match and freshness. 📊

    Used by the planner to rank candidate recipes.

    Example:
        >>> scorer = RecipeScorer(delta_service)
        >>> scores = scorer.score_recipes(recipes, pantry_items)
        >>> best = max(scores, key=lambda s: s.total_score)
    """

    def __init__(
        self,
        delta_service: DeltaService | None = None,
        criteria: ScoringCriteria | None = None,
    ) -> None:
        """Initialize the scorer.

        Args:
            delta_service: Service for comparing ingredients.
            criteria: Scoring configuration.
        """
        self.delta_service = delta_service or DeltaService()
        self.criteria = criteria or ScoringCriteria()

    def score_recipes(
        self,
        recipes: list[Recipe],
        pantry_items: list[PantryItem],
    ) -> list[RecipeScore]:
        """Score multiple recipes against the pantry.

        Args:
            recipes: List of candidate recipes.
            pantry_items: Current inventory.

        Returns:
            List of RecipeScore sorted by total_score (descending).
        """
        scores = [
            self._score_single_recipe(recipe, pantry_items)
            for recipe in recipes
            if recipe.ingredients  # Skip recipes without parsed ingredients
        ]

        # Sort by total score descending
        scores.sort(key=lambda s: s.total_score, reverse=True)
        return scores

    def _score_single_recipe(
        self,
        recipe: Recipe,
        pantry_items: list[PantryItem],
    ) -> RecipeScore:
        """Score a single recipe.

        Args:
            recipe: Recipe to score.
            pantry_items: Current inventory.

        Returns:
            RecipeScore for the recipe.
        """
        if not recipe.ingredients:
            return RecipeScore(
                recipe_id=recipe.id,
                recipe_title=recipe.title,
                inventory_match_percent=0.0,
                spoilage_score=0.0,
                freshness_score=0.0,
                total_score=0.0,
                missing_items=[],
            )

        # Use delta service to compare
        ingredients = cast(
            list[RecipeIngredient | ParsedIngredient],
            recipe.ingredients,
        )
        comparison = self.delta_service.calculate_missing(
            ingredients,
            pantry_items,
        )

        total_ingredients = len(recipe.ingredients)
        have_count = len(comparison.have_enough) + len(comparison.assumptions)
        inventory_match = (have_count / total_ingredients) if total_ingredients > 0 else 0

        # Calculate spoilage score (prioritize expiring items)
        spoilage_score = self._calculate_spoilage_score(
            comparison.have_enough,
            pantry_items,
        )

        # Calculate freshness score (prefer fresh produce)
        freshness_score = self._calculate_freshness_score(recipe)

        # Weighted total
        total_score = (
            self.criteria.inventory_weight * inventory_match
            + self.criteria.spoilage_weight * spoilage_score
            + self.criteria.freshness_weight * freshness_score
        )

        # Get missing item names
        missing = [item.item_name for item in comparison.missing]
        missing.extend([item.item_name for item in comparison.partial])

        return RecipeScore(
            recipe_id=recipe.id,
            recipe_title=recipe.title,
            inventory_match_percent=inventory_match * 100,
            spoilage_score=spoilage_score,
            freshness_score=freshness_score,
            total_score=total_score,
            missing_items=missing,
        )

    def _calculate_spoilage_score(
        self,
        matched_items: list,
        pantry_items: list[PantryItem],
    ) -> float:
        """Calculate score based on using items about to expire.

        Higher score = uses more items expiring soon.
        """
        if not matched_items:
            return 0.0

        today = date.today()
        week_later = today + timedelta(days=7)

        # Build lookup of pantry items by name
        pantry_by_name: dict[str, PantryItem] = {}
        for item in pantry_items:
            key = item.name.lower().strip()
            if key not in pantry_by_name:
                pantry_by_name[key] = item
            else:
                existing = pantry_by_name[key]
                # Keep the one expiring sooner
                if item.expiry_date and existing.expiry_date:
                    if item.expiry_date < existing.expiry_date:
                        pantry_by_name[key] = item
                elif item.expiry_date and not existing.expiry_date:
                    pantry_by_name[key] = item

        expiring_count = 0
        for delta_item in matched_items:
            key = delta_item.item_name.lower().strip()
            if key in pantry_by_name:
                pantry_item = pantry_by_name[key]
                if pantry_item.expiry_date and pantry_item.expiry_date <= week_later:
                    expiring_count += 1

        return expiring_count / len(matched_items) if matched_items else 0.0

    def _calculate_freshness_score(self, recipe: Recipe) -> float:
        """Calculate score based on use of fresh ingredients.

        Higher score = uses more fresh produce/herbs.
        """
        if not recipe.ingredients:
            return 0.0

        fresh_keywords = {
            "fresh",
            "herb",
            "basil",
            "cilantro",
            "parsley",
            "mint",
            "dill",
            "chive",
            "lettuce",
            "spinach",
            "arugula",
            "tomato",
            "cucumber",
            "bell pepper",
            "lemon",
            "lime",
            "orange",
            "avocado",
        }

        fresh_count = 0
        for ingredient in recipe.ingredients:
            name_lower = ingredient.item_name.lower()
            if any(keyword in name_lower for keyword in fresh_keywords):
                fresh_count += 1

        return fresh_count / len(recipe.ingredients)

    def filter_by_prep_time(
        self,
        recipes: list[Recipe],
        max_minutes: int,
    ) -> list[Recipe]:
        """Filter recipes by maximum prep time.

        Args:
            recipes: Recipes to filter.
            max_minutes: Maximum prep + cook time.

        Returns:
            Filtered list of recipes.
        """
        result = []
        for recipe in recipes:
            total_time = (recipe.prep_time_minutes or 0) + (recipe.cook_time_minutes or 0)
            if recipe.total_time_minutes:
                total_time = recipe.total_time_minutes

            # Include if no time info or within limit
            if total_time == 0 or total_time <= max_minutes:
                result.append(recipe)

        return result

    def filter_by_tags(
        self,
        recipes: list[Recipe],
        required_tags: list[str] | None = None,
        excluded_tags: list[str] | None = None,
    ) -> list[Recipe]:
        """Filter recipes by tags.

        Args:
            recipes: Recipes to filter.
            required_tags: Tags that must be present.
            excluded_tags: Tags that must NOT be present.

        Returns:
            Filtered list of recipes.
        """
        result = []
        required = {t.lower() for t in (required_tags or [])}
        excluded = {t.lower() for t in (excluded_tags or [])}

        for recipe in recipes:
            recipe_tags = {t.lower() for t in (recipe.tags or [])}

            # Check required tags
            if required and not required.issubset(recipe_tags):
                continue

            # Check excluded tags
            if excluded and excluded.intersection(recipe_tags):
                continue

            result.append(recipe)

        return result
