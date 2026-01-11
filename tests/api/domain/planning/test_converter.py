"""Tests for Unit Converter. ⚖️

Validates unit conversions including density-based transformations.
"""

import pytest

from src.api.app.domain.planning.converter import UnitConverter


@pytest.fixture
def converter() -> UnitConverter:
    """Create a converter instance for testing."""
    return UnitConverter()


class TestDirectConversion:
    """Tests for direct unit conversions (same dimension)."""

    def test_same_unit_no_conversion(self, converter: UnitConverter):
        """Test: same unit returns original value."""
        result = converter.convert(100, "gram", "gram")
        assert result.success
        assert result.value == 100
        assert result.method == "direct"

    def test_grams_to_kg(self, converter: UnitConverter):
        """Test: 500g -> 0.5kg"""
        result = converter.convert(500, "gram", "kilogram")
        assert result.success
        assert result.value is not None
        assert abs(result.value - 0.5) < 0.001
        assert result.method == "direct"

    def test_ml_to_liters(self, converter: UnitConverter):
        """Test: 1000ml -> 1L"""
        result = converter.convert(1000, "milliliter", "liter")
        assert result.success
        assert result.value is not None
        assert abs(result.value - 1.0) < 0.001

    def test_cups_to_tablespoons(self, converter: UnitConverter):
        """Test: 1 cup -> 16 tablespoons"""
        result = converter.convert(1, "cup", "tablespoon")
        assert result.success
        assert result.value is not None
        assert abs(result.value - 16.0) < 0.1

    def test_teaspoons_to_tablespoons(self, converter: UnitConverter):
        """Test: 3 tsp -> 1 tbsp"""
        result = converter.convert(3, "teaspoon", "tablespoon")
        assert result.success
        assert result.value is not None
        assert abs(result.value - 1.0) < 0.01


class TestDensityConversion:
    """Tests for density-based volume <-> weight conversions."""

    def test_flour_cups_to_grams(self, converter: UnitConverter):
        """Test: 1 cup flour -> ~120g"""
        result = converter.convert(1, "cup", "gram", ingredient="flour")
        assert result.success
        assert result.value is not None
        assert 115 < result.value < 125  # ~120g
        assert result.method == "density"

    def test_flour_grams_to_cups(self, converter: UnitConverter):
        """Test: 240g flour -> ~2 cups"""
        result = converter.convert(240, "gram", "cup", ingredient="flour")
        assert result.success
        assert result.value is not None
        assert 1.9 < result.value < 2.1

    def test_sugar_cups_to_grams(self, converter: UnitConverter):
        """Test: 1 cup sugar -> ~200g"""
        result = converter.convert(1, "cup", "gram", ingredient="sugar")
        assert result.success
        assert result.value is not None
        assert 195 < result.value < 205

    def test_milk_ml_to_cups(self, converter: UnitConverter):
        """Test: 245ml milk -> ~1 cup (direct volume, not density)"""
        # This should be a direct conversion, not density
        result = converter.convert(245, "milliliter", "cup", ingredient="milk")
        assert result.success
        assert result.value is not None
        # 245ml is about 1 cup
        assert 0.9 < result.value < 1.1

    def test_butter_tablespoons_to_grams(self, converter: UnitConverter):
        """Test: 2 tbsp butter -> ~28g (1/8 cup)"""
        result = converter.convert(2, "tablespoon", "gram", ingredient="butter")
        assert result.success
        assert result.value is not None
        # 2 tbsp = 1/8 cup, and 1 cup butter = 227g, so 1/8 = ~28g
        assert 25 < result.value < 32

    def test_ingredient_alias_works(self, converter: UnitConverter):
        """Test: 'ap flour' alias works for 'all-purpose flour'"""
        result = converter.convert(1, "cup", "gram", ingredient="ap flour")
        assert result.success
        assert result.value is not None
        assert 115 < result.value < 130


class TestConversionFailures:
    """Tests for conversion failures."""

    def test_incompatible_units_no_ingredient(self, converter: UnitConverter):
        """Test: gram to cup without ingredient fails."""
        result = converter.convert(100, "gram", "cup")
        assert not result.success
        assert result.method == "failed"

    def test_unknown_ingredient_density(self, converter: UnitConverter):
        """Test: unknown ingredient can't do density conversion."""
        result = converter.convert(100, "gram", "cup", ingredient="unicorn tears")
        assert not result.success
        assert "density" in (result.error or "").lower() or "cannot" in (result.error or "").lower()

    def test_incompatible_count_to_weight(self, converter: UnitConverter):
        """Test: count to gram fails (no density for 'eggs')."""
        result = converter.convert(3, "count", "gram", ingredient="eggs")
        assert not result.success


class TestKnownIngredients:
    """Tests for ingredient database."""

    def test_get_known_ingredients(self, converter: UnitConverter):
        """Test: known ingredients list includes common items."""
        known = converter.get_known_ingredients()
        assert "flour" in known
        assert "sugar" in known
        assert "butter" in known
        assert len(known) > 20  # Should have many ingredients
