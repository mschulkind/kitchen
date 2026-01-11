"""Tests for Planning Domain Models. 🧪

Validates Pydantic DTOs and computed properties for the Delta Engine.
"""

import pytest
from pydantic import ValidationError

from src.api.app.domain.planning.models import (
    ComparisonResult,
    DeltaItem,
    DeltaStatus,
)


class TestDeltaStatus:
    """Tests for DeltaStatus enum."""

    def test_all_statuses_exist(self):
        """All expected statuses are defined."""
        assert DeltaStatus.HAS_ENOUGH == "has_enough"
        assert DeltaStatus.PARTIAL == "partial"
        assert DeltaStatus.MISSING == "missing"
        assert DeltaStatus.ASSUMED == "assumed"
        assert DeltaStatus.UNIT_MISMATCH == "unit_mismatch"

    def test_status_count(self):
        """There should be exactly 5 statuses."""
        assert len(DeltaStatus) == 5


class TestDeltaItem:
    """Tests for DeltaItem model."""

    def test_valid_creation(self):
        """Test creating a valid delta item."""
        item = DeltaItem(
            item_name="Flour",
            recipe_quantity=500,
            recipe_unit="gram",
            status=DeltaStatus.HAS_ENOUGH,
        )
        assert item.item_name == "Flour"
        assert item.status == DeltaStatus.HAS_ENOUGH

    def test_with_inventory_data(self):
        """Test delta item with inventory comparison."""
        item = DeltaItem(
            item_name="Eggs",
            recipe_quantity=3,
            recipe_unit="count",
            inventory_quantity=12,
            inventory_unit="count",
            delta_quantity=None,  # No delta, have enough
            status=DeltaStatus.HAS_ENOUGH,
        )
        assert item.inventory_quantity == 12

    def test_partial_with_delta(self):
        """Test delta item showing partial availability."""
        item = DeltaItem(
            item_name="Butter",
            recipe_quantity=200,
            recipe_unit="gram",
            inventory_quantity=100,
            inventory_unit="gram",
            delta_quantity=100,  # Need 100g more
            delta_unit="gram",
            status=DeltaStatus.PARTIAL,
        )
        assert item.delta_quantity == 100
        assert item.status == DeltaStatus.PARTIAL

    def test_confidence_bounds(self):
        """Test confidence must be between 0 and 1."""
        DeltaItem(
            item_name="x",
            recipe_quantity=1,
            recipe_unit="count",
            status=DeltaStatus.MISSING,
            confidence=0.0,
        )
        DeltaItem(
            item_name="x",
            recipe_quantity=1,
            recipe_unit="count",
            status=DeltaStatus.MISSING,
            confidence=1.0,
        )

        with pytest.raises(ValidationError):
            DeltaItem(
                item_name="x",
                recipe_quantity=1,
                recipe_unit="count",
                status=DeltaStatus.MISSING,
                confidence=-0.1,
            )

    def test_optional_fields(self):
        """Test optional fields default to None."""
        item = DeltaItem(
            item_name="Salt",
            recipe_quantity=1,
            recipe_unit="teaspoon",
            status=DeltaStatus.ASSUMED,
        )
        assert item.inventory_quantity is None
        assert item.inventory_unit is None
        assert item.delta_quantity is None
        assert item.notes is None
        assert item.matched_pantry_item_id is None


class TestComparisonResult:
    """Tests for ComparisonResult model."""

    def test_empty_result(self):
        """Test empty comparison result defaults."""
        result = ComparisonResult(total_ingredients=0)
        assert result.have_enough == []
        assert result.partial == []
        assert result.missing == []
        assert result.assumptions == []
        assert result.unresolved == []

    def test_needs_shopping_true_with_partial(self):
        """Test needs_shopping is True when partial items exist."""
        result = ComparisonResult(
            total_ingredients=1,
            partial=[
                DeltaItem(
                    item_name="Flour",
                    recipe_quantity=500,
                    recipe_unit="gram",
                    status=DeltaStatus.PARTIAL,
                    delta_quantity=200,
                )
            ],
        )
        assert result.needs_shopping is True

    def test_needs_shopping_true_with_missing(self):
        """Test needs_shopping is True when missing items exist."""
        result = ComparisonResult(
            total_ingredients=1,
            missing=[
                DeltaItem(
                    item_name="Yeast",
                    recipe_quantity=1,
                    recipe_unit="packet",
                    status=DeltaStatus.MISSING,
                )
            ],
        )
        assert result.needs_shopping is True

    def test_needs_shopping_false_when_all_available(self):
        """Test needs_shopping is False when all items available."""
        result = ComparisonResult(
            total_ingredients=2,
            have_enough=[
                DeltaItem(item_name="Salt", recipe_quantity=1, recipe_unit="tsp", status=DeltaStatus.HAS_ENOUGH),
                DeltaItem(item_name="Sugar", recipe_quantity=2, recipe_unit="cup", status=DeltaStatus.HAS_ENOUGH),
            ],
        )
        assert result.needs_shopping is False

    def test_shopping_list_items_combines_partial_and_missing(self):
        """Test shopping_list_items combines partial + missing."""
        result = ComparisonResult(
            total_ingredients=3,
            partial=[
                DeltaItem(item_name="Butter", recipe_quantity=1, recipe_unit="cup", status=DeltaStatus.PARTIAL),
            ],
            missing=[
                DeltaItem(item_name="Milk", recipe_quantity=2, recipe_unit="cup", status=DeltaStatus.MISSING),
                DeltaItem(item_name="Cream", recipe_quantity=1, recipe_unit="cup", status=DeltaStatus.MISSING),
            ],
        )
        shopping = result.shopping_list_items
        assert len(shopping) == 3
        names = [item.item_name for item in shopping]
        assert "Butter" in names
        assert "Milk" in names
        assert "Cream" in names

    def test_can_cook_now_true_when_everything_available(self):
        """Test can_cook_now is True when nothing is missing."""
        result = ComparisonResult(
            total_ingredients=2,
            have_enough=[
                DeltaItem(item_name="Rice", recipe_quantity=1, recipe_unit="cup", status=DeltaStatus.HAS_ENOUGH),
            ],
            assumptions=[
                DeltaItem(item_name="Salt", recipe_quantity=1, recipe_unit="tsp", status=DeltaStatus.ASSUMED),
            ],
        )
        assert result.can_cook_now is True

    def test_can_cook_now_false_with_unresolved(self):
        """Test can_cook_now is False when there are unresolved items."""
        result = ComparisonResult(
            total_ingredients=1,
            unresolved=[
                DeltaItem(item_name="Spinach", recipe_quantity=1, recipe_unit="cup", status=DeltaStatus.UNIT_MISMATCH),
            ],
        )
        assert result.can_cook_now is False

    def test_can_cook_now_false_with_missing(self):
        """Test can_cook_now is False when items are missing."""
        result = ComparisonResult(
            total_ingredients=1,
            missing=[
                DeltaItem(item_name="Cumin", recipe_quantity=1, recipe_unit="tsp", status=DeltaStatus.MISSING),
            ],
        )
        assert result.can_cook_now is False

    def test_total_ingredients_metadata(self):
        """Test total_ingredients is tracked correctly."""
        result = ComparisonResult(
            total_ingredients=5,
            have_enough=[
                DeltaItem(item_name="A", recipe_quantity=1, recipe_unit="x", status=DeltaStatus.HAS_ENOUGH),
                DeltaItem(item_name="B", recipe_quantity=1, recipe_unit="x", status=DeltaStatus.HAS_ENOUGH),
            ],
            missing=[
                DeltaItem(item_name="C", recipe_quantity=1, recipe_unit="x", status=DeltaStatus.MISSING),
            ],
            assumptions=[
                DeltaItem(item_name="D", recipe_quantity=1, recipe_unit="x", status=DeltaStatus.ASSUMED),
                DeltaItem(item_name="E", recipe_quantity=1, recipe_unit="x", status=DeltaStatus.ASSUMED),
            ],
        )
        assert result.total_ingredients == 5
        # Total of all lists
        total_in_lists = (
            len(result.have_enough)
            + len(result.missing)
            + len(result.assumptions)
        )
        assert total_in_lists == 5
