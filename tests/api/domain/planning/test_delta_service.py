"""Tests for Delta Service. 🧮

The "hard math" tests for the kitchen brain.
These tests follow the spec from Phase 3.3.
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.api.app.domain.pantry.models import PantryItem
from src.api.app.domain.planning.delta_service import DeltaService
from src.api.app.domain.planning.models import DeltaStatus
from src.api.app.domain.recipes.models import ParsedIngredient


@pytest.fixture
def service() -> DeltaService:
    """Create a delta service instance for testing."""
    return DeltaService()


def make_pantry_item(
    name: str,
    quantity: float | None = None,
    unit: str | None = None,
) -> PantryItem:
    """Helper to create a PantryItem for testing."""
    return PantryItem(
        id=uuid4(),
        household_id=uuid4(),
        name=name,
        quantity=quantity,
        unit=unit,
        location="pantry",
        is_staple=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def make_ingredient(
    name: str,
    quantity: float | None = None,
    unit: str | None = None,
) -> ParsedIngredient:
    """Helper to create a ParsedIngredient for testing."""
    return ParsedIngredient(
        raw_text=f"{quantity or ''} {unit or ''} {name}".strip(),
        quantity=quantity,
        unit=unit,
        item_name=name,
    )


class TestSimpleComparisons:
    """Tests for simple quantity comparisons (spec Phase 3A)."""

    def test_simple_surplus(self, service: DeltaService):
        """Test: Recipe needs 2 onions, pantry has 5 -> HAS_ENOUGH"""
        recipe = [make_ingredient("onion", 2, "count")]
        pantry = [make_pantry_item("onion", 5, "count")]

        result = service.calculate_missing(recipe, pantry)

        assert len(result.have_enough) == 1
        assert result.have_enough[0].status == DeltaStatus.HAS_ENOUGH
        assert result.have_enough[0].delta_quantity is None

    def test_simple_deficit(self, service: DeltaService):
        """Test: Recipe needs 5 onions, pantry has 2 -> BUY 3"""
        recipe = [make_ingredient("onion", 5, "count")]
        pantry = [make_pantry_item("onion", 2, "count")]

        result = service.calculate_missing(recipe, pantry)

        assert len(result.partial) == 1
        delta = result.partial[0]
        assert delta.status == DeltaStatus.PARTIAL
        assert delta.delta_quantity == 3

    def test_exact_match(self, service: DeltaService):
        """Test: Recipe needs exactly what pantry has."""
        recipe = [make_ingredient("eggs", 6, "count")]
        pantry = [make_pantry_item("eggs", 6, "count")]

        result = service.calculate_missing(recipe, pantry)

        assert len(result.have_enough) == 1
        assert result.have_enough[0].delta_quantity is None

    def test_missing_completely(self, service: DeltaService):
        """Test: Recipe needs item not in pantry -> MISSING"""
        recipe = [make_ingredient("cumin", 1, "teaspoon")]
        pantry = [make_pantry_item("salt", 100, "gram")]

        result = service.calculate_missing(recipe, pantry)

        assert len(result.missing) == 1
        assert result.missing[0].status == DeltaStatus.MISSING
        assert result.missing[0].delta_quantity == 1


class TestUnitConversions:
    """Tests for unit conversion during comparison."""

    def test_unit_conv_success(self, service: DeltaService):
        """Test: Recipe needs 500ml milk, pantry has 1L -> HAS_ENOUGH"""
        recipe = [make_ingredient("milk", 500, "milliliter")]
        pantry = [make_pantry_item("milk", 1, "liter")]

        result = service.calculate_missing(recipe, pantry)

        assert len(result.have_enough) == 1
        assert result.have_enough[0].status == DeltaStatus.HAS_ENOUGH

    def test_unit_conv_partial(self, service: DeltaService):
        """Test: Recipe needs 1L milk, pantry has 500ml -> PARTIAL"""
        recipe = [make_ingredient("milk", 1, "liter")]
        pantry = [make_pantry_item("milk", 500, "milliliter")]

        result = service.calculate_missing(recipe, pantry)

        assert len(result.partial) == 1
        delta = result.partial[0]
        # Should need 500ml more (0.5L)
        assert delta.delta_quantity is not None
        assert abs(delta.delta_quantity - 0.5) < 0.01

    def test_density_conversion_flour(self, service: DeltaService):
        """Test: Recipe needs 1 cup flour, pantry has 150g -> HAS_ENOUGH"""
        recipe = [make_ingredient("flour", 1, "cup")]
        pantry = [make_pantry_item("flour", 150, "gram")]

        result = service.calculate_missing(recipe, pantry)

        # 1 cup flour = ~120g, so 150g should be enough
        assert len(result.have_enough) == 1

    def test_density_failure(self, service: DeltaService):
        """Test: Recipe needs 1 cup spinach, pantry has 200g -> UNIT_MISMATCH"""
        # Spinach doesn't have a known density
        recipe = [make_ingredient("spinach", 1, "cup")]
        pantry = [make_pantry_item("spinach", 200, "gram")]

        result = service.calculate_missing(recipe, pantry)

        # Should be unresolved due to no density data
        assert len(result.unresolved) == 1
        assert result.unresolved[0].status == DeltaStatus.UNIT_MISMATCH


class TestFuzzyMatching:
    """Tests for fuzzy name matching."""

    def test_exact_match_priority(self, service: DeltaService):
        """Test: Exact match is preferred over fuzzy."""
        recipe = [make_ingredient("onion", 1, "count")]
        pantry = [
            make_pantry_item("onion", 5, "count"),  # Exact
            make_pantry_item("onions", 3, "count"),  # Similar
        ]

        result = service.calculate_missing(recipe, pantry)

        assert len(result.have_enough) == 1
        assert result.have_enough[0].confidence == 1.0

    def test_fuzzy_match_singular_plural(self, service: DeltaService):
        """Test: 'egg' matches 'eggs' (singular/plural)."""
        recipe = [make_ingredient("egg", 2, "count")]
        pantry = [make_pantry_item("eggs", 12, "count")]

        result = service.calculate_missing(recipe, pantry)

        # Should find a match with fuzzy matching
        assert len(result.have_enough) == 1 or len(result.missing) == 0

    def test_no_match_different_items(self, service: DeltaService):
        """Test: 'carrot' does not match 'potato'."""
        recipe = [make_ingredient("carrot", 2, "count")]
        pantry = [make_pantry_item("potato", 5, "count")]

        result = service.calculate_missing(recipe, pantry)

        assert len(result.missing) == 1


class TestAssumptions:
    """Tests for staple assumptions."""

    def test_salt_is_assumed(self, service: DeltaService):
        """Test: Salt is assumed to be available."""
        recipe = [make_ingredient("salt", 1, "teaspoon")]
        pantry = []  # Empty pantry

        result = service.calculate_missing(recipe, pantry)

        assert len(result.assumptions) == 1
        assert result.assumptions[0].status == DeltaStatus.ASSUMED
        assert "salt" in result.assumptions[0].item_name.lower()

    def test_pepper_is_assumed(self, service: DeltaService):
        """Test: Black pepper is assumed to be available."""
        recipe = [make_ingredient("black pepper", 0.5, "teaspoon")]
        pantry = []

        result = service.calculate_missing(recipe, pantry)

        assert len(result.assumptions) == 1
        assert result.assumptions[0].status == DeltaStatus.ASSUMED

    def test_water_is_assumed(self, service: DeltaService):
        """Test: Water is assumed to be available."""
        recipe = [make_ingredient("water", 2, "cup")]
        pantry = []

        result = service.calculate_missing(recipe, pantry)

        assert len(result.assumptions) == 1

    def test_can_disable_assumptions(self, service: DeltaService):
        """Test: Assumptions can be disabled."""
        recipe = [make_ingredient("salt", 1, "teaspoon")]
        pantry = []

        result = service.calculate_missing(
            recipe,
            pantry,
            include_staples_in_assumptions=False,
        )

        assert len(result.assumptions) == 0
        assert len(result.missing) == 1


class TestNoQuantities:
    """Tests for ingredients without quantities."""

    def test_recipe_no_quantity_has_item(self, service: DeltaService):
        """Test: Recipe has no quantity, pantry has item -> HAS_ENOUGH"""
        recipe = [make_ingredient("butter", None, None)]
        pantry = [make_pantry_item("butter", 200, "gram")]

        result = service.calculate_missing(recipe, pantry)

        assert len(result.have_enough) == 1

    def test_pantry_no_quantity_has_item(self, service: DeltaService):
        """Test: Pantry has no quantity but has item -> HAS_ENOUGH (low confidence)"""
        recipe = [make_ingredient("cheddar cheese", 2, "cup")]
        pantry = [make_pantry_item("cheddar cheese", None, None)]

        result = service.calculate_missing(recipe, pantry)

        assert len(result.have_enough) == 1
        # Confidence should be lower
        assert result.have_enough[0].confidence < 1.0


class TestComparisonResultProperties:
    """Tests for ComparisonResult computed properties."""

    def test_needs_shopping_true(self, service: DeltaService):
        """Test: needs_shopping is True when items are missing."""
        recipe = [make_ingredient("rare ingredient", 1, "cup")]
        pantry = []

        result = service.calculate_missing(recipe, pantry)

        assert result.needs_shopping is True

    def test_needs_shopping_false(self, service: DeltaService):
        """Test: needs_shopping is False when all items available."""
        recipe = [make_ingredient("salt", 1, "teaspoon")]  # Assumed
        pantry = []

        result = service.calculate_missing(recipe, pantry)

        assert result.needs_shopping is False

    def test_can_cook_now_true(self, service: DeltaService):
        """Test: can_cook_now is True when everything is available."""
        recipe = [make_ingredient("butter", 1, "tablespoon")]
        pantry = [make_pantry_item("butter", 200, "gram")]

        result = service.calculate_missing(recipe, pantry)

        assert result.can_cook_now is True

    def test_shopping_list_items(self, service: DeltaService):
        """Test: shopping_list_items returns partial + missing."""
        recipe = [
            make_ingredient("flour", 500, "gram"),  # Partial
            make_ingredient("yeast", 1, "packet"),  # Missing
        ]
        pantry = [make_pantry_item("flour", 200, "gram")]

        result = service.calculate_missing(recipe, pantry)

        shopping = result.shopping_list_items
        assert len(shopping) == 2


class TestMultipleIngredients:
    """Tests for recipes with multiple ingredients."""

    def test_mixed_results(self, service: DeltaService):
        """Test: Recipe with mix of available, missing, and assumed."""
        recipe = [
            make_ingredient("flour", 2, "cup"),
            make_ingredient("eggs", 3, "count"),
            make_ingredient("baking powder", 1, "teaspoon"),
            make_ingredient("salt", 0.5, "teaspoon"),
        ]
        pantry = [
            make_pantry_item("flour", 500, "gram"),  # Should be enough
            make_pantry_item("eggs", 12, "count"),  # Plenty
            # No baking powder
        ]

        result = service.calculate_missing(recipe, pantry)

        assert result.total_ingredients == 4
        assert len(result.have_enough) >= 2  # flour, eggs
        assert len(result.missing) == 1  # baking powder
        assert len(result.assumptions) == 1  # salt
