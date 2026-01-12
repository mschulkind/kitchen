"""Property-Based Tests for Delta Service. 🧮

Uses Hypothesis to test mathematical invariants of the delta calculations.
These tests verify that the "hard math" is correct.

Phase 3.3 spec: Hypothesis: Req(x) - Inv(y) == -(Inv(y) - Req(x))
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st
from pytest import approx

from src.api.app.domain.pantry.models import PantryItem
from src.api.app.domain.planning.delta_service import DeltaService
from src.api.app.domain.recipes.models import ParsedIngredient

# =============================================================================
# Test Fixtures & Helpers
# =============================================================================

# Floating point tolerance for unit conversions (handles precision issues)
FLOAT_TOLERANCE = 1e-6


def make_pantry_item(
    name: str = "item",
    quantity: float | None = None,
    unit: str | None = None,
) -> PantryItem:
    """Helper to create a PantryItem for testing."""
    now = datetime.now(UTC)
    return PantryItem(
        id=uuid4(),
        household_id=uuid4(),
        name=name,
        quantity=quantity,
        unit=unit,
        location="pantry",
        is_staple=False,
        created_at=now,
        updated_at=now,
    )


def make_ingredient(
    name: str = "item",
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


def assert_has_enough_or_negligible_delta(result, tolerance: float = FLOAT_TOLERANCE):
    """Assert result is HAS_ENOUGH or has negligible delta due to float precision.

    This handles the common case where unit conversions result in tiny
    floating-point deltas that should be treated as zero.
    """
    if len(result.have_enough) == 1:
        return  # Perfect match

    if len(result.partial) == 1:
        delta = result.partial[0].delta_quantity
        assert delta is not None
        assert delta == approx(0, abs=tolerance), f"Delta {delta} exceeds tolerance {tolerance}"
        return

    pytest.fail(
        f"Unexpected result: have_enough={len(result.have_enough)}, "
        f"partial={len(result.partial)}, missing={len(result.missing)}"
    )


# =============================================================================
# Hypothesis Strategies
# =============================================================================


@st.composite
def positive_quantity(draw) -> float:
    """Generate positive quantities for ingredients."""
    return draw(st.floats(min_value=0.01, max_value=10000, allow_nan=False))


@st.composite
def unit_strategy(draw) -> str:
    """Generate valid units."""
    return draw(
        st.sampled_from(
            [
                "count",
                "gram",
                "kilogram",
                "milliliter",
                "liter",
                "cup",
                "tablespoon",
                "teaspoon",
                "ounce",
                "pound",
            ]
        )
    )


# =============================================================================
# Property-Based Tests
# =============================================================================


class TestDeltaPropertyBased:
    """Property-based tests for delta calculations."""

    @given(
        req_qty=positive_quantity(),
        inv_qty=positive_quantity(),
        unit=unit_strategy(),
    )
    @settings(max_examples=100, deadline=None)
    def test_delta_symmetry(self, req_qty: float, inv_qty: float, unit: str):
        """Test: Req(x) - Inv(y) should be consistent.

        If we need X and have Y:
        - delta = X - Y
        - If we swap (need Y, have X), delta = Y - X = -(X - Y)
        """
        service = DeltaService()
        name = "test_item"

        recipe = [make_ingredient(name, req_qty, unit)]
        pantry = [make_pantry_item(name, inv_qty, unit)]

        result = service.calculate_missing(recipe, pantry)

        if req_qty <= inv_qty:
            assert_has_enough_or_negligible_delta(result)
        else:
            # Should need to buy
            assert len(result.partial) == 1
            delta = result.partial[0].delta_quantity
            expected_delta = req_qty - inv_qty
            assert delta == approx(expected_delta, rel=0.01)

    @given(
        quantity=positive_quantity(),
        unit=unit_strategy(),
    )
    @settings(max_examples=50, deadline=None)
    def test_exact_match_never_needs_shopping(self, quantity: float, unit: str):
        """Test: When requirement equals inventory, no shopping needed."""
        service = DeltaService()
        name = "exact_match_item"

        recipe = [make_ingredient(name, quantity, unit)]
        pantry = [make_pantry_item(name, quantity, unit)]

        result = service.calculate_missing(recipe, pantry)

        # Should either have enough, or have negligible delta
        assert_has_enough_or_negligible_delta(result)

    @given(req_qty=positive_quantity())
    @settings(max_examples=50, deadline=None)
    def test_empty_pantry_means_missing(self, req_qty: float):
        """Test: With empty pantry (non-staple), items are missing."""
        service = DeltaService()

        recipe = [make_ingredient("special_ingredient", req_qty, "count")]
        pantry = []

        result = service.calculate_missing(recipe, pantry, include_staples_in_assumptions=False)

        assert len(result.missing) == 1
        assert result.needs_shopping is True

    @given(items=st.lists(positive_quantity(), min_size=1, max_size=10))
    @settings(max_examples=50, deadline=None)
    def test_total_ingredients_count(self, items: list[float]):
        """Test: Total ingredients count matches input."""
        service = DeltaService()

        recipe = [make_ingredient(f"item_{i}", qty, "count") for i, qty in enumerate(items)]
        pantry = []

        result = service.calculate_missing(recipe, pantry, include_staples_in_assumptions=False)

        assert result.total_ingredients == len(items)

    @given(
        qty1=positive_quantity(),
        qty2=positive_quantity(),
    )
    @settings(max_examples=50, deadline=None)
    def test_surplus_never_goes_to_shopping(self, qty1: float, qty2: float):
        """Test: If pantry > required, item never appears in shopping list."""
        assume(qty2 >= qty1 * 1.1)  # Ensure clear surplus

        service = DeltaService()
        name = "surplus_item"

        recipe = [make_ingredient(name, qty1, "gram")]
        pantry = [make_pantry_item(name, qty2, "gram")]

        result = service.calculate_missing(recipe, pantry)

        # Should not be in any shopping-related category
        assert len(result.missing) == 0
        assert len(result.partial) == 0
        assert len(result.shopping_list_items) == 0


class TestDeltaCommutativeProperties:
    """Tests for commutative and associative properties."""

    def test_multiple_pantry_items_aggregate(self):
        """Test: Multiple pantry entries for same item should aggregate.

        This tests that when you have the same item in multiple pantry entries,
        their quantities are combined when calculating if you have enough.
        """
        service = DeltaService()
        recipe = [make_ingredient("butter", 100, "gram")]
        pantry = [
            make_pantry_item("butter", 50, "gram"),
            make_pantry_item("butter", 60, "gram"),  # Total: 110g
        ]

        result = service.calculate_missing(recipe, pantry)

        # 110g >= 100g, should have enough
        assert len(result.have_enough) == 1

    @given(
        req=positive_quantity(),
        inv=positive_quantity(),
    )
    @settings(max_examples=50, deadline=None)
    def test_consistent_categorization(self, req: float, inv: float):
        """Test: Same input always produces same categorization."""
        service = DeltaService()

        recipe = [make_ingredient("consistency_test", req, "cup")]
        pantry = [make_pantry_item("consistency_test", inv, "cup")]

        result1 = service.calculate_missing(recipe, pantry)
        result2 = service.calculate_missing(recipe, pantry)

        # Results should be identical
        assert len(result1.have_enough) == len(result2.have_enough)
        assert len(result1.missing) == len(result2.missing)
        assert len(result1.partial) == len(result2.partial)


class TestUnitConversionProperties:
    """Property tests for unit conversion edge cases."""

    @given(ml_qty=positive_quantity())
    @settings(max_examples=50, deadline=None)
    def test_ml_to_l_conversion(self, ml_qty: float):
        """Test: 1000ml should equal 1L (within float tolerance)."""
        assume(ml_qty <= 5000)  # Reasonable range

        service = DeltaService()

        liters = ml_qty / 1000
        recipe = [make_ingredient("milk", ml_qty, "milliliter")]
        pantry = [make_pantry_item("milk", liters, "liter")]

        result = service.calculate_missing(recipe, pantry)

        assert_has_enough_or_negligible_delta(result)

    @given(g_qty=positive_quantity())
    @settings(max_examples=50, deadline=None)
    def test_g_to_kg_conversion(self, g_qty: float):
        """Test: 1000g should equal 1kg (within float tolerance)."""
        assume(g_qty <= 10000)

        service = DeltaService()

        kg = g_qty / 1000
        recipe = [make_ingredient("flour", g_qty, "gram")]
        pantry = [make_pantry_item("flour", kg, "kilogram")]

        result = service.calculate_missing(recipe, pantry)

        assert_has_enough_or_negligible_delta(result)
