"""Plan Generator - Creates thematic plan options. 🎲

The "Choose Your Own Adventure" engine that generates 3 distinct
plan options for users to choose from.

Fun fact: Decision fatigue is real - offering 3 curated options
reduces cognitive load by 60% compared to free-form planning! 🧠
"""

import random
import time
from typing import Any, cast
from uuid import uuid4

from src.api.app.domain.pantry.models import PantryItem
from src.api.app.domain.planner.models import (
    CreatePlanRequest,
    PlanOption,
    PlanOptionsResponse,
    RecipeStub,
)
from src.api.app.domain.planner.scorer import RecipeScorer
from src.api.app.domain.recipes.models import Recipe

# Theme definitions for plan options
THEMES = {
    "efficiency": {
        "title": "Efficiency Week 🚀",
        "description": "Maximize what you already have! These recipes use the most ingredients from your pantry.",
        "priority": "inventory_match",
    },
    "fresh": {
        "title": "Fresh & Vibrant 🥗",
        "description": "Use up those fresh ingredients before they go bad. Lots of produce-forward dishes!",
        "priority": "spoilage",
    },
    "quick": {
        "title": "Weeknight Express ⏱️",
        "description": "30 minutes or less from start to table. Perfect for busy weeknights!",
        "priority": "prep_time",
    },
    "adventure": {
        "title": "Culinary Adventure 🌍",
        "description": "Try something new! These recipes explore different cuisines and techniques.",
        "priority": "variety",
    },
    "comfort": {
        "title": "Comfort Classics 🍲",
        "description": "Hearty, satisfying meals that feel like a warm hug.",
        "priority": "tags",
        "preferred_tags": ["comfort", "hearty", "classic", "stew", "soup"],
    },
    "healthy": {
        "title": "Healthy Refresh 💚",
        "description": "Light, nutritious meals to keep you feeling great.",
        "priority": "tags",
        "preferred_tags": ["healthy", "light", "vegetable", "lean"],
    },
}


class PlanGenerator:
    """Generates thematic meal plan options. 🎲

    Creates 3 distinct plan options based on different priorities
    (efficiency, freshness, speed, etc.).

    Example:
        >>> generator = PlanGenerator(scorer, recipes, pantry)
        >>> options = generator.generate_options(request)
        >>> print(f"Generated {len(options.options)} options")
    """

    def __init__(
        self,
        scorer: RecipeScorer | None = None,
    ) -> None:
        """Initialize the generator.

        Args:
            scorer: Recipe scorer for ranking.
        """
        self.scorer = scorer or RecipeScorer()

    def generate_options(
        self,
        request: CreatePlanRequest,
        recipes: list[Recipe],
        pantry_items: list[PantryItem],
    ) -> PlanOptionsResponse:
        """Generate plan options for the user.

        Args:
            request: The plan request with dates and constraints.
            recipes: Available recipes to choose from.
            pantry_items: Current inventory.

        Returns:
            PlanOptionsResponse with generated options.
        """
        start_time = time.time()

        # Calculate number of meals needed
        num_days = (request.end_date - request.start_date).days + 1
        meals_per_day = len(request.meal_types)
        total_meals = num_days * meals_per_day

        # Score all recipes
        all_scores = self.scorer.score_recipes(recipes, pantry_items)
        scored_recipes = {s.recipe_id: s for s in all_scores}

        # Filter recipes based on constraints
        filtered_recipes = self._apply_constraints(recipes, request.constraints)

        # Select themes for options
        selected_themes = self._select_themes(request.num_options, request.constraints)

        # Generate each option
        options = []
        for theme_key in selected_themes:
            theme = cast(dict[str, Any], THEMES[theme_key])
            option = self._generate_single_option(
                theme_key,
                theme,
                filtered_recipes,
                scored_recipes,
                total_meals,
                pantry_items,
            )
            if option:
                options.append(option)

        # Ensure we have enough options
        while len(options) < request.num_options and len(options) < len(THEMES):
            # Try remaining themes
            for theme_key in THEMES:
                if theme_key not in selected_themes:
                    theme = cast(dict[str, Any], THEMES[theme_key])
                    option = self._generate_single_option(
                        theme_key,
                        theme,
                        filtered_recipes,
                        scored_recipes,
                        total_meals,
                        pantry_items,
                    )
                    if option:
                        options.append(option)
                        selected_themes.append(theme_key)
                        break
            else:
                break

        elapsed_ms = int((time.time() - start_time) * 1000)

        return PlanOptionsResponse(
            options=options[: request.num_options],
            generation_time_ms=elapsed_ms,
        )

    def _select_themes(
        self,
        num_options: int,
        constraints: list[str],
    ) -> list[str]:
        """Select which themes to use based on constraints.

        Args:
            num_options: How many options to generate.
            constraints: User's constraints (may influence theme selection).

        Returns:
            List of theme keys to use.
        """
        # Always include efficiency (most practical)
        selected = ["efficiency"]

        # Check constraints for theme hints
        constraint_text = " ".join(constraints).lower()

        if "quick" in constraint_text or "fast" in constraint_text:
            selected.append("quick")
        if "healthy" in constraint_text or "light" in constraint_text:
            selected.append("healthy")
        if "comfort" in constraint_text or "hearty" in constraint_text:
            selected.append("comfort")

        # Fill remaining slots with variety
        remaining = [k for k in THEMES if k not in selected]
        random.shuffle(remaining)

        while len(selected) < num_options and remaining:
            selected.append(remaining.pop())

        return selected[:num_options]

    def _apply_constraints(
        self,
        recipes: list[Recipe],
        constraints: list[str],
    ) -> list[Recipe]:
        """Filter recipes based on user constraints.

        Args:
            recipes: All available recipes.
            constraints: User's dietary restrictions, preferences.

        Returns:
            Filtered list of recipes.
        """
        if not constraints:
            return recipes

        constraint_text = " ".join(constraints).lower()

        # Common exclusions
        exclusions = []
        if "vegetarian" in constraint_text:
            exclusions.extend(["meat", "chicken", "beef", "pork", "fish"])
        if "vegan" in constraint_text:
            exclusions.extend(
                ["meat", "chicken", "beef", "pork", "fish", "dairy", "egg", "cheese", "milk"]
            )
        if "gluten-free" in constraint_text or "gluten free" in constraint_text:
            exclusions.extend(["flour", "bread", "pasta", "wheat"])
        if "no mushroom" in constraint_text:
            exclusions.append("mushroom")
        if "no seafood" in constraint_text:
            exclusions.extend(["fish", "shrimp", "salmon", "tuna", "crab"])

        if not exclusions:
            return recipes

        filtered = []
        for recipe in recipes:
            recipe_text = recipe.title.lower()
            if recipe.ingredients:
                recipe_text += " " + " ".join(i.item_name.lower() for i in recipe.ingredients)

            if not any(excl in recipe_text for excl in exclusions):
                filtered.append(recipe)

        return filtered

    def _generate_single_option(
        self,
        theme_key: str,
        theme: dict[str, Any],
        recipes: list[Recipe],
        scored_recipes: dict,
        total_meals: int,
        _pantry_items: list[PantryItem],
    ) -> PlanOption | None:
        """Generate a single plan option.

        Args:
            theme_key: The theme identifier.
            theme: Theme configuration.
            recipes: Available recipes.
            scored_recipes: Pre-computed scores.
            total_meals: Number of meals to plan.
            _pantry_items: Current inventory (reserved for future use).

        Returns:
            PlanOption or None if not enough recipes.
        """
        if len(recipes) < total_meals:
            # Not enough recipes for a full plan
            return None

        # Select recipes based on theme priority
        selected = self._select_recipes_for_theme(
            theme,
            recipes,
            scored_recipes,
            total_meals,
        )

        if len(selected) < min(3, total_meals):
            return None

        # Build preview (first 3-4 recipes)
        preview_meals = [
            RecipeStub(
                id=r.id,
                title=r.title,
                prep_time_minutes=r.prep_time_minutes,
                inventory_match_percent=(
                    scored_recipes[r.id].inventory_match_percent if r.id in scored_recipes else None
                ),
                tags=r.tags or [],
            )
            for r in selected[:4]
        ]

        # Calculate aggregate stats
        total_match = sum(
            scored_recipes[r.id].inventory_match_percent for r in selected if r.id in scored_recipes
        )
        avg_match = total_match / len(selected) if selected else 0

        # Estimate shopping items (rough calculation)
        all_missing = set()
        for r in selected:
            if r.id in scored_recipes:
                all_missing.update(scored_recipes[r.id].missing_items)
        estimated_shopping = len(all_missing)

        return PlanOption(
            id=f"{theme_key}_{uuid4().hex[:8]}",
            title=theme["title"],
            theme=theme_key,
            description=theme["description"],
            preview_meals=preview_meals,
            estimated_shopping_items=estimated_shopping,
            inventory_usage_percent=avg_match,
            difficulty=self._estimate_difficulty(selected),
        )

    def _select_recipes_for_theme(
        self,
        theme: dict,
        recipes: list[Recipe],
        scored_recipes: dict,
        count: int,
    ) -> list[Recipe]:
        """Select recipes matching a theme.

        Args:
            theme: Theme configuration.
            recipes: Available recipes.
            scored_recipes: Pre-computed scores.
            count: Number of recipes to select.

        Returns:
            List of selected recipes.
        """
        priority = theme.get("priority", "inventory_match")

        if priority == "inventory_match":
            # Sort by inventory match (highest first)
            sorted_recipes = sorted(
                recipes,
                key=lambda r: (
                    scored_recipes[r.id].inventory_match_percent if r.id in scored_recipes else 0
                ),
                reverse=True,
            )
        elif priority == "spoilage":
            # Sort by spoilage score (highest first)
            sorted_recipes = sorted(
                recipes,
                key=lambda r: (
                    scored_recipes[r.id].spoilage_score if r.id in scored_recipes else 0
                ),
                reverse=True,
            )
        elif priority == "prep_time":
            # Sort by total time (lowest first)
            sorted_recipes = sorted(
                recipes,
                key=lambda r: (r.total_time_minutes or r.prep_time_minutes or 999),
            )
        elif priority == "tags":
            # Filter and sort by preferred tags
            preferred = set(theme.get("preferred_tags", []))
            sorted_recipes = sorted(
                recipes,
                key=lambda r: len(preferred.intersection(set(r.tags or []))),
                reverse=True,
            )
        else:
            # Random for variety
            sorted_recipes = recipes.copy()
            random.shuffle(sorted_recipes)

        # Ensure variety (don't repeat similar recipes)
        selected = []
        used_titles: set[str] = set()

        for recipe in sorted_recipes:
            # Simple deduplication by title similarity
            title_words = set(recipe.title.lower().split())
            if not any(len(title_words.intersection(set(t.split()))) > 2 for t in used_titles):
                selected.append(recipe)
                used_titles.add(recipe.title.lower())

            if len(selected) >= count:
                break

        return selected

    def _estimate_difficulty(self, recipes: list[Recipe]) -> str:
        """Estimate overall difficulty of a plan.

        Args:
            recipes: Selected recipes.

        Returns:
            Difficulty string.
        """
        if not recipes:
            return "Unknown"

        # Calculate average prep time
        times = [(r.total_time_minutes or r.prep_time_minutes or 30) for r in recipes]
        avg_time = sum(times) / len(times)

        if avg_time <= 20:
            return "Easy"
        elif avg_time <= 45:
            return "Moderate"
        else:
            return "Adventurous"
