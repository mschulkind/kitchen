"""Tests for the RecipeScorer. 📊

Tests recipe scoring based on inventory match.
"""

from datetime import date, timedelta
from uuid import uuid4

from src.api.app.domain.pantry.models import PantryItem
from src.api.app.domain.planner.scorer import RecipeScorer
from src.api.app.domain.recipes.models import Recipe, RecipeIngredient


def make_pantry_item(
    name: str,
    quantity: float = 1.0,
    unit: str | None = None,
    expiry_days: int | None = None,
) -> PantryItem:
    """Create a test pantry item."""
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    expiry = date.today() + timedelta(days=expiry_days) if expiry_days else None

    return PantryItem(
        id=uuid4(),
        household_id=uuid4(),
        name=name,
        quantity=quantity,
        unit=unit,
        location="pantry",
        expiry_date=expiry,
        created_at=now,
        updated_at=now,
    )


def make_recipe(
    title: str,
    ingredients: list[tuple[str, float | None, str | None]],
    tags: list[str] | None = None,
    prep_time: int | None = None,
) -> Recipe:
    """Create a test recipe with ingredients."""
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    recipe_id = uuid4()

    recipe_ingredients = [
        RecipeIngredient(
            id=uuid4(),
            recipe_id=recipe_id,
            item_name=name,
            quantity=qty,
            unit=unit,
            raw_text=f"{qty} {unit} {name}" if qty else name,
            notes=None,
            section=None,
            sort_order=0,
            confidence=1.0,
            created_at=now,
        )
        for name, qty, unit in ingredients
    ]

    return Recipe(
        id=recipe_id,
        household_id=uuid4(),
        title=title,
        ingredients=recipe_ingredients,
        tags=tags or [],
        prep_time_minutes=prep_time or 30,
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


class TestRecipeScorer:
    """Tests for RecipeScorer class."""

    def test_score_recipe_with_full_match(self) -> None:
        """Recipe with all ingredients in pantry gets high score."""
        scorer = RecipeScorer()

        recipe = make_recipe(
            "Simple Salad",
            [
                ("lettuce", 1, "head"),
                ("tomato", 2, "count"),
            ],
        )

        pantry = [
            make_pantry_item("Lettuce", 2, "head"),
            make_pantry_item("Tomato", 5, "count"),
        ]

        scores = scorer.score_recipes([recipe], pantry)

        assert len(scores) == 1
        assert scores[0].inventory_match_percent == 100.0
        assert len(scores[0].missing_items) == 0

    def test_score_recipe_with_partial_match(self) -> None:
        """Recipe with some missing ingredients gets lower score."""
        scorer = RecipeScorer()

        recipe = make_recipe(
            "Pasta",
            [
                ("pasta", 1, "lb"),
                ("tomato sauce", 1, "jar"),
                ("parmesan", 0.5, "cup"),
            ],
        )

        pantry = [
            make_pantry_item("Pasta", 2, "lb"),
            # Missing tomato sauce and parmesan
        ]

        scores = scorer.score_recipes([recipe], pantry)

        assert len(scores) == 1
        # Only 1 of 3 ingredients available = ~33%
        assert scores[0].inventory_match_percent < 50
        assert len(scores[0].missing_items) >= 1

    def test_score_recipe_with_no_match(self) -> None:
        """Recipe with no matching ingredients gets zero match."""
        scorer = RecipeScorer()

        recipe = make_recipe(
            "Exotic Dish",
            [
                ("dragon fruit", 2, "count"),
                ("durian", 1, "whole"),
            ],
        )

        pantry = [
            make_pantry_item("Apple", 5),
            make_pantry_item("Banana", 3),
        ]

        scores = scorer.score_recipes([recipe], pantry)

        assert len(scores) == 1
        assert scores[0].inventory_match_percent == 0.0

    def test_scores_sorted_by_total_score(self) -> None:
        """Recipes are sorted by total score descending."""
        scorer = RecipeScorer()

        # Recipe with full match
        recipe1 = make_recipe("Simple", [("apple", 1, "count")])

        # Recipe with partial match
        recipe2 = make_recipe(
            "Complex",
            [
                ("apple", 1, "count"),
                ("rare_spice", 1, "tsp"),
            ],
        )

        pantry = [make_pantry_item("Apple", 10)]

        scores = scorer.score_recipes([recipe1, recipe2], pantry)

        assert len(scores) == 2
        # First result should have higher score
        assert scores[0].total_score >= scores[1].total_score

    def test_expiring_items_boost_score(self) -> None:
        """Recipes using expiring items get higher spoilage score."""
        scorer = RecipeScorer()

        recipe = make_recipe("Salad", [("lettuce", 1, "head")])

        # Item expiring in 3 days
        pantry_expiring = [make_pantry_item("Lettuce", 1, "head", expiry_days=3)]

        # Item expiring in 30 days
        pantry_fresh = [make_pantry_item("Lettuce", 1, "head", expiry_days=30)]

        score_expiring = scorer.score_recipes([recipe], pantry_expiring)[0]
        score_fresh = scorer.score_recipes([recipe], pantry_fresh)[0]

        # Expiring item should have higher spoilage score
        assert score_expiring.spoilage_score >= score_fresh.spoilage_score

    def test_filter_by_prep_time(self) -> None:
        """Filter recipes by maximum prep time."""
        scorer = RecipeScorer()

        quick_recipe = make_recipe("Quick", [], prep_time=15)
        slow_recipe = make_recipe("Slow", [], prep_time=60)

        recipes = [quick_recipe, slow_recipe]

        filtered = scorer.filter_by_prep_time(recipes, max_minutes=30)

        assert len(filtered) == 1
        assert filtered[0].title == "Quick"

    def test_filter_by_tags_required(self) -> None:
        """Filter recipes by required tags."""
        scorer = RecipeScorer()

        vegetarian = make_recipe("Veggie", [], tags=["vegetarian", "healthy"])
        meat = make_recipe("Meat", [], tags=["comfort", "hearty"])

        recipes = [vegetarian, meat]

        filtered = scorer.filter_by_tags(recipes, required_tags=["vegetarian"])

        assert len(filtered) == 1
        assert filtered[0].title == "Veggie"

    def test_filter_by_tags_excluded(self) -> None:
        """Filter recipes by excluded tags."""
        scorer = RecipeScorer()

        spicy = make_recipe("Spicy", [], tags=["spicy", "indian"])
        mild = make_recipe("Mild", [], tags=["comfort"])

        recipes = [spicy, mild]

        filtered = scorer.filter_by_tags(recipes, excluded_tags=["spicy"])

        assert len(filtered) == 1
        assert filtered[0].title == "Mild"
