"""Tests for Pantry Domain Models. 🧪

Validates Pydantic DTOs and business logic constraints.
"""

from datetime import date

import pytest
from pydantic import ValidationError

from src.api.app.domain.pantry.models import (
    CreatePantryItemDTO,
    PantryLocation,
    UpdatePantryItemDTO,
)


class TestCreatePantryItemDTO:
    """Tests for CreatePantryItemDTO validation."""

    def test_valid_creation(self):
        """Test creating a valid pantry item."""
        dto = CreatePantryItemDTO(
            name="Rice",
            quantity=1.0,
            unit="kg",
            location=PantryLocation.PANTRY,
        )
        assert dto.name == "Rice"
        assert dto.quantity == 1.0
        assert dto.unit == "kg"
        assert dto.location == PantryLocation.PANTRY

    def test_negative_quantity_rejected(self):
        """Test that negative quantities are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreatePantryItemDTO(
                name="Rice",
                quantity=-5.0,
                unit="kg",
            )
        assert "greater than 0" in str(exc_info.value).lower()

    def test_zero_quantity_rejected(self):
        """Test that zero quantity is rejected."""
        with pytest.raises(ValidationError):
            CreatePantryItemDTO(
                name="Rice",
                quantity=0,
                unit="kg",
            )

    def test_empty_name_rejected(self):
        """Test that empty names are rejected."""
        with pytest.raises(ValidationError):
            CreatePantryItemDTO(
                name="",
                quantity=1.0,
                unit="kg",
            )

    def test_default_location_is_pantry(self):
        """Test that default location is 'pantry'."""
        dto = CreatePantryItemDTO(
            name="Flour",
            quantity=2.0,
            unit="kg",
        )
        assert dto.location == PantryLocation.PANTRY

    def test_all_locations_valid(self):
        """Test all storage locations are valid."""
        for location in PantryLocation:
            dto = CreatePantryItemDTO(
                name="Test",
                quantity=1.0,
                unit="count",
                location=location,
            )
            assert dto.location == location

    def test_expiry_date_optional(self):
        """Test that expiry date is optional."""
        dto = CreatePantryItemDTO(
            name="Salt",
            quantity=1.0,
            unit="kg",
        )
        assert dto.expiry_date is None

    def test_expiry_date_accepted(self):
        """Test that valid expiry dates are accepted."""
        dto = CreatePantryItemDTO(
            name="Milk",
            quantity=1.0,
            unit="gallon",
            expiry_date=date(2026, 1, 20),
        )
        assert dto.expiry_date == date(2026, 1, 20)


class TestUpdatePantryItemDTO:
    """Tests for UpdatePantryItemDTO validation."""

    def test_all_fields_optional(self):
        """Test that all update fields are optional."""
        dto = UpdatePantryItemDTO()
        assert dto.name is None
        assert dto.quantity is None
        assert dto.unit is None
        assert dto.location is None

    def test_partial_update(self):
        """Test partial update with only quantity."""
        dto = UpdatePantryItemDTO(quantity=2.0)
        assert dto.quantity == 2.0
        assert dto.name is None

    def test_negative_quantity_rejected(self):
        """Test that negative quantities are rejected in updates."""
        with pytest.raises(ValidationError):
            UpdatePantryItemDTO(quantity=-1.0)


class TestPantryLocation:
    """Tests for PantryLocation enum. 🏠"""

    def test_all_locations(self):
        """Test all expected locations exist."""
        locations = [loc.value for loc in PantryLocation]
        assert "pantry" in locations
        assert "fridge" in locations
        assert "freezer" in locations
        assert "counter" in locations
        assert "garden" in locations  # 🌱

    def test_location_count(self):
        """Test we have exactly 5 locations."""
        assert len(PantryLocation) == 5
