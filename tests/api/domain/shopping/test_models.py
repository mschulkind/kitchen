"""Tests for Shopping Domain Models. 🧪

Validates Pydantic DTOs and computed properties.
"""

import pytest
from pydantic import ValidationError

from src.api.app.domain.shopping.models import (
    CreateShoppingItemDTO,
    CreateShoppingListDTO,
    ShoppingItemStatus,
    ShoppingListSummary,
    UpdateShoppingItemDTO,
)


class TestShoppingItemStatus:
    """Tests for ShoppingItemStatus enum."""

    def test_all_statuses_exist(self):
        """All expected statuses are defined."""
        assert ShoppingItemStatus.PENDING == "pending"
        assert ShoppingItemStatus.CHECKED == "checked"
        assert ShoppingItemStatus.SKIPPED == "skipped"

    def test_status_count(self):
        """There should be exactly 3 statuses."""
        assert len(ShoppingItemStatus) == 3


class TestCreateShoppingItemDTO:
    """Tests for CreateShoppingItemDTO validation."""

    def test_valid_creation(self):
        """Test creating a valid shopping item DTO."""
        dto = CreateShoppingItemDTO(
            name="Milk",
            quantity=1.0,
            unit="gallon",
            category="Dairy",
        )
        assert dto.name == "Milk"
        assert dto.quantity == 1.0
        assert dto.category == "Dairy"

    def test_name_required(self):
        """Test that name is required."""
        with pytest.raises(ValidationError):
            CreateShoppingItemDTO(quantity=1.0, unit="cup")

    def test_empty_name_rejected(self):
        """Test that empty name is rejected."""
        with pytest.raises(ValidationError):
            CreateShoppingItemDTO(name="")

    def test_name_max_length(self):
        """Test name max length validation."""
        long_name = "a" * 256
        with pytest.raises(ValidationError):
            CreateShoppingItemDTO(name=long_name)

    def test_quantity_must_be_positive(self):
        """Test quantity must be positive."""
        with pytest.raises(ValidationError):
            CreateShoppingItemDTO(name="Test", quantity=-1.0)

        with pytest.raises(ValidationError):
            CreateShoppingItemDTO(name="Test", quantity=0)

    def test_optional_fields_default_none(self):
        """Test optional fields default to None."""
        dto = CreateShoppingItemDTO(name="Minimal Item")
        assert dto.quantity is None
        assert dto.unit is None
        assert dto.category is None
        assert dto.notes is None
        assert dto.recipe_source is None

    def test_recipe_source_captured(self):
        """Test recipe source is captured."""
        dto = CreateShoppingItemDTO(
            name="Flour",
            quantity=2.0,
            unit="cup",
            recipe_source="Chocolate Cake",
        )
        assert dto.recipe_source == "Chocolate Cake"


class TestUpdateShoppingItemDTO:
    """Tests for UpdateShoppingItemDTO validation."""

    def test_all_fields_optional(self):
        """Test that all update fields are optional."""
        dto = UpdateShoppingItemDTO()
        assert dto.name is None
        assert dto.quantity is None
        assert dto.status is None

    def test_partial_update(self):
        """Test partial update with status only."""
        dto = UpdateShoppingItemDTO(status=ShoppingItemStatus.CHECKED)
        assert dto.status == ShoppingItemStatus.CHECKED
        assert dto.name is None

    def test_name_validation_when_provided(self):
        """Test name is validated when provided."""
        with pytest.raises(ValidationError):
            UpdateShoppingItemDTO(name="")


class TestCreateShoppingListDTO:
    """Tests for CreateShoppingListDTO validation."""

    def test_default_name(self):
        """Test default list name."""
        dto = CreateShoppingListDTO()
        assert dto.name == "Shopping List"

    def test_custom_name(self):
        """Test custom list name."""
        dto = CreateShoppingListDTO(name="Weekly Groceries")
        assert dto.name == "Weekly Groceries"

    def test_name_max_length(self):
        """Test name max length."""
        long_name = "a" * 256
        with pytest.raises(ValidationError):
            CreateShoppingListDTO(name=long_name)


class TestShoppingListSummary:
    """Tests for ShoppingListSummary model."""

    def test_progress_percent_zero_items(self):
        """Test progress is 100% when no items."""
        from datetime import UTC, datetime
        from uuid import uuid4

        summary = ShoppingListSummary(
            id=uuid4(),
            name="Empty List",
            status="active",
            total_items=0,
            checked_items=0,
            created_at=datetime.now(UTC),
        )
        assert summary.progress_percent == 100.0

    def test_progress_percent_all_checked(self):
        """Test progress is 100% when all items checked."""
        from datetime import UTC, datetime
        from uuid import uuid4

        summary = ShoppingListSummary(
            id=uuid4(),
            name="Done List",
            status="active",
            total_items=5,
            checked_items=5,
            created_at=datetime.now(UTC),
        )
        assert summary.progress_percent == 100.0

    def test_progress_percent_half_checked(self):
        """Test progress calculation for partial completion."""
        from datetime import UTC, datetime
        from uuid import uuid4

        summary = ShoppingListSummary(
            id=uuid4(),
            name="Half Done",
            status="active",
            total_items=10,
            checked_items=5,
            created_at=datetime.now(UTC),
        )
        assert summary.progress_percent == 50.0

    def test_progress_percent_none_checked(self):
        """Test progress is 0% when no items checked."""
        from datetime import UTC, datetime
        from uuid import uuid4

        summary = ShoppingListSummary(
            id=uuid4(),
            name="New List",
            status="active",
            total_items=8,
            checked_items=0,
            created_at=datetime.now(UTC),
        )
        assert summary.progress_percent == 0.0
