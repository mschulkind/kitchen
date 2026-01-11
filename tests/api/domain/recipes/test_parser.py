"""Tests for Ingredient Parser. 🧪

Validates the core parsing logic for converting ingredient strings
to structured data.

These tests follow the test cases from Phase 2.2 spec.
"""

import pytest

from src.api.app.domain.recipes.parser import IngredientParser, ParserConfig


@pytest.fixture
def parser() -> IngredientParser:
    """Create a parser instance for testing."""
    return IngredientParser()


class TestBasicParsing:
    """Tests for basic ingredient parsing."""

    def test_parse_simple_mass(self, parser: IngredientParser):
        """Test: '500g Flour' -> {qty: 500, unit: 'gram', item: 'flour'}"""
        result = parser.parse("500g Flour")

        assert result.quantity == 500.0
        assert result.unit == "gram"
        assert result.item_name == "flour"
        assert result.confidence >= 0.7

    def test_parse_simple_mass_with_space(self, parser: IngredientParser):
        """Test: '500 g Flour' -> {qty: 500, unit: 'gram', item: 'flour'}"""
        result = parser.parse("500 g Flour")

        assert result.quantity == 500.0
        assert result.unit == "gram"
        assert result.item_name == "flour"

    def test_parse_fraction_volume(self, parser: IngredientParser):
        """Test: '1/2 cup Milk' -> {qty: 0.5, unit: 'cup', item: 'milk'}"""
        result = parser.parse("1/2 cup Milk")

        assert result.quantity == 0.5
        assert result.unit == "cup"
        assert result.item_name == "milk"

    def test_parse_mixed_fraction(self, parser: IngredientParser):
        """Test: '1 1/2 cups flour' -> {qty: 1.5, unit: 'cup', item: 'flour'}"""
        result = parser.parse("1 1/2 cups flour")

        assert result.quantity == 1.5
        assert result.unit == "cup"
        assert result.item_name == "flour"

    def test_parse_unicode_fraction(self, parser: IngredientParser):
        """Test: '½ cup sugar' -> {qty: 0.5, unit: 'cup', item: 'sugar'}"""
        result = parser.parse("½ cup sugar")

        assert result.quantity == 0.5
        assert result.unit == "cup"
        assert result.item_name == "sugar"

    def test_parse_unicode_mixed_fraction(self, parser: IngredientParser):
        """Test: '1½ cups flour' -> {qty: 1.5, unit: 'cup', item: 'flour'}"""
        result = parser.parse("1½ cups flour")

        assert result.quantity == 1.5
        assert result.unit == "cup"
        assert result.item_name == "flour"


class TestCountableItems:
    """Tests for items that are counted (not measured)."""

    def test_parse_implicit_count(self, parser: IngredientParser):
        """Test: '3 Eggs' -> {qty: 3, unit: 'count', item: 'eggs'}"""
        result = parser.parse("3 Eggs")

        assert result.quantity == 3.0
        assert result.unit == "count"
        assert result.item_name == "eggs"

    def test_parse_single_item(self, parser: IngredientParser):
        """Test: '1 onion' -> {qty: 1, unit: 'count', item: 'onion'}"""
        result = parser.parse("1 onion")

        assert result.quantity == 1.0
        assert result.unit == "count"
        assert result.item_name == "onion"

    def test_parse_garlic_cloves(self, parser: IngredientParser):
        """Test: '3 cloves garlic' -> {qty: 3, unit: 'count', item: 'garlic'}"""
        result = parser.parse("3 cloves garlic")

        assert result.quantity == 3.0
        assert result.unit == "count"  # clove normalizes to count
        assert "garlic" in result.item_name.lower()


class TestDescriptorsAndNotes:
    """Tests for parsing descriptors and notes."""

    def test_parse_complex_count(self, parser: IngredientParser):
        """Test: '1 large Onion, chopped' -> includes notes for 'large, chopped'"""
        result = parser.parse("1 large Onion, chopped")

        assert result.quantity == 1.0
        assert result.item_name == "onion"
        assert result.notes is not None
        assert "large" in result.notes.lower() or "chopped" in result.notes.lower()

    def test_parse_with_parenthetical(self, parser: IngredientParser):
        """Test: '2 cups flour (sifted)' -> extracts parenthetical as note"""
        result = parser.parse("2 cups flour (sifted)")

        assert result.quantity == 2.0
        assert result.unit == "cup"
        assert result.item_name == "flour"
        assert result.notes is not None
        assert "sifted" in result.notes.lower()

    def test_parse_prep_instruction(self, parser: IngredientParser):
        """Test: '1 cup onion, finely diced' -> extracts prep as note"""
        result = parser.parse("1 cup onion, finely diced")

        assert result.quantity == 1.0
        assert result.unit == "cup"
        assert "onion" in result.item_name.lower()
        assert result.notes is not None


class TestVagueQuantities:
    """Tests for vague/unmeasurable quantities."""

    def test_parse_to_taste(self, parser: IngredientParser):
        """Test: 'Salt and Pepper to taste' -> handles vague quantity"""
        result = parser.parse("Salt and Pepper to taste")

        assert result.quantity == 0
        assert result.unit == "to taste"
        assert "salt" in result.item_name.lower()

    def test_parse_pinch(self, parser: IngredientParser):
        """Test: 'Pinch of salt' -> handles pinch unit"""
        result = parser.parse("Pinch of salt")

        assert result.unit == "pinch"
        assert "salt" in result.item_name.lower()

    def test_parse_optional(self, parser: IngredientParser):
        """Test: 'Fresh herbs (optional)' -> handles optional ingredient"""
        result = parser.parse("Fresh herbs (optional)")

        assert "herbs" in result.item_name.lower()
        assert result.notes is not None
        assert "optional" in result.notes.lower()


class TestUnitNormalization:
    """Tests for unit normalization."""

    def test_tablespoon_variants(self, parser: IngredientParser):
        """Test that various tablespoon abbreviations normalize."""
        variants = ["1 tbsp butter", "1 Tbsp butter", "1 tbs butter", "1 tablespoon butter"]

        for text in variants:
            result = parser.parse(text)
            assert result.unit == "tablespoon", f"Failed for: {text}"

    def test_teaspoon_variants(self, parser: IngredientParser):
        """Test that various teaspoon abbreviations normalize."""
        variants = ["1 tsp salt", "1 teaspoon salt"]

        for text in variants:
            result = parser.parse(text)
            assert result.unit == "teaspoon", f"Failed for: {text}"

    def test_ounce_variants(self, parser: IngredientParser):
        """Test that ounce abbreviations normalize."""
        result = parser.parse("4 oz cheese")
        assert result.unit == "ounce"
        assert result.quantity == 4.0


class TestEdgeCases:
    """Tests for edge cases and tricky inputs."""

    def test_parse_with_bullet(self, parser: IngredientParser):
        """Test: '• 1 cup flour' -> strips bullet"""
        result = parser.parse("• 1 cup flour")

        assert result.quantity == 1.0
        assert result.unit == "cup"
        assert result.item_name == "flour"

    def test_parse_with_number_prefix(self, parser: IngredientParser):
        """Test: '1. 1 cup flour' -> strips list number"""
        result = parser.parse("1. 1 cup flour")

        assert result.quantity == 1.0
        assert result.unit == "cup"

    def test_parse_with_of(self, parser: IngredientParser):
        """Test: '1 cup of flour' -> handles 'of' correctly"""
        result = parser.parse("1 cup of flour")

        assert result.quantity == 1.0
        assert result.unit == "cup"
        assert result.item_name == "flour"

    def test_empty_string(self, parser: IngredientParser):
        """Test: empty string returns original as item"""
        result = parser.parse("")
        assert result.item_name == ""
        assert result.confidence < 0.5

    def test_just_item_name(self, parser: IngredientParser):
        """Test: 'butter' with no quantity"""
        result = parser.parse("butter")

        assert result.quantity is None
        assert result.unit is None
        assert result.item_name == "butter"


class TestConfidenceScores:
    """Tests for confidence score calculation."""

    def test_high_confidence_complete_parse(self, parser: IngredientParser):
        """Test: complete parse has high confidence"""
        result = parser.parse("2 cups all-purpose flour")

        assert result.confidence >= 0.8

    def test_lower_confidence_no_quantity(self, parser: IngredientParser):
        """Test: missing quantity has lower confidence"""
        result = parser.parse("flour")

        assert result.confidence < 0.7

    def test_confidence_with_unit_only(self, parser: IngredientParser):
        """Test: having unit but no item has lower confidence"""
        result = parser.parse("cup")

        assert result.confidence < 0.6


class TestParseMany:
    """Tests for batch parsing."""

    def test_parse_many(self, parser: IngredientParser):
        """Test parsing multiple ingredients at once."""
        texts = [
            "2 cups flour",
            "1 tsp salt",
            "3 eggs",
        ]

        results = parser.parse_many(texts)

        assert len(results) == 3
        assert results[0].item_name == "flour"
        assert results[1].item_name == "salt"
        assert results[2].item_name == "eggs"
