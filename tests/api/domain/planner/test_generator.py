"""Tests for the PlanGenerator. 🎲

Tests plan option generation with different themes.
"""

from datetime import date, timedelta
from uuid import uuid4

from src.api.app.domain.pantry.models import PantryItem
from src.api.app.domain.planner.generator import PlanGenerator
from src.api.app.domain.planner.models import CreatePlanRequest
from src.api.app.domain.recipes.models import Recipe, RecipeIngredient


def make_pantry_item(name: str, quantity: float = 1.0) -> PantryItem:
    """Create a test pantry item."""
    from datetime import UTC, datetime

    now = datetime.now(UTC)

    return PantryItem(
        id=uuid4(),
        household_id=uuid4(),
        name=name,
        quantity=quantity,
        unit="count",
        location="pantry",
        created_at=now,
        updated_at=now,
    )


def make_recipe(title: str, ingredients: list[str], tags: list[str] | None = None) -> Recipe:
    """Create a test recipe with ingredients."""
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    recipe_id = uuid4()

    recipe_ingredients = [
        RecipeIngredient(
            id=uuid4(),
            recipe_id=recipe_id,
            item_name=name,
            quantity=1,
            unit="count",
            raw_text=name,
            notes=None,
            section=None,
            sort_order=0,
            confidence=1.0,
            created_at=now,
        )
        for name in ingredients
    ]

    return Recipe(
        id=recipe_id,
        household_id=uuid4(),
        title=title,
        ingredients=recipe_ingredients,
        tags=tags or [],
        prep_time_minutes=30,
        source_url=None,
        source_domain=None,
        servings=4,
        cook_time_minutes=None,
        total_time_minutes=None,
        description=None,
        instructions=None,
        is_parsed=True,
        created_at=now,
        updated_at=now,
    )


class TestPlanGenerator:
    """Tests for PlanGenerator class."""

    def test_generate_options_returns_correct_count(self) -> None:
        """Generator returns requested number of options."""
        generator = PlanGenerator()

        request = CreatePlanRequest(
            start_date=date.today(),
            end_date=date.today() + timedelta(days=6),
            num_options=3,
        )

        recipes = [
            make_recipe(f"Recipe {i}", ["ingredient"]) for i in range(10)
        ]
        pantry = [make_pantry_item("Ingredient")]

        response = generator.generate_options(request, recipes, pantry)

        assert len(response.options) == 3

    def test_generate_options_includes_efficiency_theme(self) -> None:
        """Generator always includes efficiency theme."""
        generator = PlanGenerator()

        request = CreatePlanRequest(
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2),
            num_options=3,
        )

        recipes = [make_recipe(f"Recipe {i}", ["ingredient"]) for i in range(5)]
        pantry = [make_pantry_item("Ingredient")]

        response = generator.generate_options(request, recipes, pantry)

        themes = [opt.theme for opt in response.options]
        assert "efficiency" in themes

    def test_generate_options_has_preview_meals(self) -> None:
        """Each option has preview meals."""
        generator = PlanGenerator()

        request = CreatePlanRequest(
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2),
            num_options=2,
        )

        recipes = [make_recipe(f"Recipe {i}", ["ingredient"]) for i in range(5)]
        pantry = [make_pantry_item("Ingredient")]

        response = generator.generate_options(request, recipes, pantry)

        for option in response.options:
            assert len(option.preview_meals) > 0
            assert option.title  # Has a title
            assert option.description  # Has a description

    def test_apply_constraints_filters_vegetarian(self) -> None:
        """Constraints filter out inappropriate recipes."""
        generator = PlanGenerator()

        recipes = [
            make_recipe("Veggie Stir Fry", ["tofu", "vegetables"]),
            make_recipe("Chicken Dinner", ["chicken", "rice"]),
            make_recipe("Beef Tacos", ["beef", "tortillas"]),
        ]

        filtered = generator._apply_constraints(recipes, ["vegetarian"])

        # Should filter out chicken and beef
        assert len(filtered) == 1
        assert filtered[0].title == "Veggie Stir Fry"

    def test_apply_constraints_empty_returns_all(self) -> None:
        """No constraints returns all recipes."""
        generator = PlanGenerator()

        recipes = [make_recipe(f"Recipe {i}", ["ingredient"]) for i in range(5)]

        filtered = generator._apply_constraints(recipes, [])

        assert len(filtered) == 5

    def test_estimate_difficulty_quick_is_easy(self) -> None:
        """Quick recipes result in easy difficulty."""
        generator = PlanGenerator()

        recipes = [
            make_recipe("Quick 1", []),
            make_recipe("Quick 2", []),
        ]
        for r in recipes:
            r.prep_time_minutes = 15

        difficulty = generator._estimate_difficulty(recipes)

        assert difficulty == "Easy"

    def test_estimate_difficulty_long_is_adventurous(self) -> None:
        """Long recipes result in adventurous difficulty."""
        generator = PlanGenerator()

        recipes = [
            make_recipe("Slow 1", []),
            make_recipe("Slow 2", []),
        ]
        for r in recipes:
            r.prep_time_minutes = 90

        difficulty = generator._estimate_difficulty(recipes)

        assert difficulty == "Adventurous"

    def test_not_enough_recipes_returns_fewer_options(self) -> None:
        """When there aren't enough recipes, fewer options are returned."""
        generator = PlanGenerator()

        request = CreatePlanRequest(
            start_date=date.today(),
            end_date=date.today() + timedelta(days=6),  # 7 days
            num_options=3,
        )

        # Only 3 recipes for a 7-day plan
        recipes = [make_recipe(f"Recipe {i}", ["ingredient"]) for i in range(3)]
        pantry = [make_pantry_item("Ingredient")]

        response = generator.generate_options(request, recipes, pantry)

        # Should still return some options but might be fewer
        assert len(response.options) <= 3
