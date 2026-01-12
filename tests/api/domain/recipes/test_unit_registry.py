"""Tests for Unit Registry. 🧪

Validates unit normalization and conversion logic.
"""

import pytest

from src.api.app.domain.recipes.unit_registry import UnitRegistry


@pytest.fixture
def registry() -> UnitRegistry:
    """Create a unit registry instance for testing."""
    return UnitRegistry()


class TestFractionParsing:
    """Tests for fraction parsing."""

    def test_parse_simple_integer(self, registry: UnitRegistry):
        """Test: '2' -> 2.0"""
        assert registry.parse_fraction("2") == 2.0

    def test_parse_decimal(self, registry: UnitRegistry):
        """Test: '1.5' -> 1.5"""
        assert registry.parse_fraction("1.5") == 1.5

    def test_parse_simple_fraction(self, registry: UnitRegistry):
        """Test: '1/2' -> 0.5"""
        assert registry.parse_fraction("1/2") == 0.5

    def test_parse_mixed_number(self, registry: UnitRegistry):
        """Test: '1 1/2' -> 1.5"""
        assert registry.parse_fraction("1 1/2") == 1.5

    def test_parse_unicode_half(self, registry: UnitRegistry):
        """Test: '½' -> 0.5"""
        assert registry.parse_fraction("½") == 0.5

    def test_parse_unicode_quarter(self, registry: UnitRegistry):
        """Test: '¼' -> 0.25"""
        assert registry.parse_fraction("¼") == 0.25

    def test_parse_unicode_three_quarters(self, registry: UnitRegistry):
        """Test: '¾' -> 0.75"""
        assert registry.parse_fraction("¾") == 0.75

    def test_parse_unicode_third(self, registry: UnitRegistry):
        """Test: '⅓' -> ~0.333"""
        result = registry.parse_fraction("⅓")
        assert result is not None
        assert abs(result - (1 / 3)) < 0.001

    def test_parse_mixed_unicode(self, registry: UnitRegistry):
        """Test: '1½' -> 1.5"""
        assert registry.parse_fraction("1½") == 1.5

    def test_parse_empty_string(self, registry: UnitRegistry):
        """Test: '' -> None"""
        assert registry.parse_fraction("") is None

    def test_parse_invalid(self, registry: UnitRegistry):
        """Test: invalid strings return None"""
        assert registry.parse_fraction("abc") is None


class TestUnitNormalization:
    """Tests for unit normalization."""

    def test_normalize_tbsp(self, registry: UnitRegistry):
        """Test: 'tbsp' -> 'tablespoon'"""
        assert registry.normalize_unit("tbsp") == "tablespoon"

    def test_normalize_tsp(self, registry: UnitRegistry):
        """Test: 'tsp' -> 'teaspoon'"""
        assert registry.normalize_unit("tsp") == "teaspoon"

    def test_normalize_cup(self, registry: UnitRegistry):
        """Test: 'c' -> 'cup'"""
        assert registry.normalize_unit("c") == "cup"

    def test_normalize_gram(self, registry: UnitRegistry):
        """Test: 'g' -> 'gram'"""
        assert registry.normalize_unit("g") == "gram"

    def test_normalize_kilogram(self, registry: UnitRegistry):
        """Test: 'kg' -> 'kilogram'"""
        assert registry.normalize_unit("kg") == "kilogram"

    def test_normalize_ounce(self, registry: UnitRegistry):
        """Test: 'oz' -> 'ounce'"""
        assert registry.normalize_unit("oz") == "ounce"

    def test_normalize_pound(self, registry: UnitRegistry):
        """Test: 'lb' -> 'pound'"""
        assert registry.normalize_unit("lb") == "pound"
        assert registry.normalize_unit("lbs") == "pound"

    def test_normalize_count_variants(self, registry: UnitRegistry):
        """Test: count variants normalize to 'count'"""
        for unit in ["pc", "pcs", "piece", "pieces", "each"]:
            assert registry.normalize_unit(unit) == "count", f"Failed for: {unit}"

    def test_normalize_preserves_unknown(self, registry: UnitRegistry):
        """Test: unknown units are returned as-is (lowercase)"""
        assert registry.normalize_unit("some_unknown_unit") == "some_unknown_unit"


class TestUnitConversion:
    """Tests for unit conversion."""

    def test_convert_grams_to_kg(self, registry: UnitRegistry):
        """Test: 500g -> 0.5kg"""
        result = registry.convert(500, "gram", "kilogram")
        assert result is not None
        assert abs(result - 0.5) < 0.001

    def test_convert_ml_to_liters(self, registry: UnitRegistry):
        """Test: 1000ml -> 1L"""
        result = registry.convert(1000, "milliliter", "liter")
        assert result is not None
        assert abs(result - 1.0) < 0.001

    def test_convert_tsp_to_tbsp(self, registry: UnitRegistry):
        """Test: 3 tsp -> 1 tbsp"""
        result = registry.convert(3, "teaspoon", "tablespoon")
        assert result is not None
        assert abs(result - 1.0) < 0.001

    def test_convert_cups_to_ml(self, registry: UnitRegistry):
        """Test: 1 cup -> ~237ml (US)"""
        result = registry.convert(1, "cup", "milliliter")
        assert result is not None
        # US cup is approximately 237ml
        assert 230 < result < 250

    def test_convert_incompatible_returns_none(self, registry: UnitRegistry):
        """Test: gram to cup (no density) returns None"""
        result = registry.convert(100, "gram", "cup")
        assert result is None


class TestUnitCompatibility:
    """Tests for unit compatibility checking."""

    def test_volume_units_compatible(self, registry: UnitRegistry):
        """Test: volume units are compatible."""
        assert registry.are_compatible("cup", "milliliter")
        assert registry.are_compatible("tablespoon", "teaspoon")
        assert registry.are_compatible("liter", "fluid_ounce")

    def test_mass_units_compatible(self, registry: UnitRegistry):
        """Test: mass units are compatible."""
        assert registry.are_compatible("gram", "kilogram")
        assert registry.are_compatible("ounce", "pound")

    def test_mass_volume_incompatible(self, registry: UnitRegistry):
        """Test: mass and volume are not directly compatible."""
        assert not registry.are_compatible("gram", "cup")
        assert not registry.are_compatible("kilogram", "liter")

    def test_count_self_compatible(self, registry: UnitRegistry):
        """Test: count units are self-compatible."""
        assert registry.are_compatible("count", "count")


class TestVagueUnits:
    """Tests for vague/unmeasurable units."""

    def test_pinch_is_vague(self, registry: UnitRegistry):
        """Test: 'pinch' is a vague unit."""
        assert registry.is_vague_unit("pinch")

    def test_dash_is_vague(self, registry: UnitRegistry):
        """Test: 'dash' is a vague unit."""
        assert registry.is_vague_unit("dash")

    def test_to_taste_is_vague(self, registry: UnitRegistry):
        """Test: 'to taste' is a vague unit."""
        assert registry.is_vague_unit("to taste")

    def test_cup_is_not_vague(self, registry: UnitRegistry):
        """Test: 'cup' is not a vague unit."""
        assert not registry.is_vague_unit("cup")

    def test_gram_is_not_vague(self, registry: UnitRegistry):
        """Test: 'gram' is not a vague unit."""
        assert not registry.is_vague_unit("gram")
