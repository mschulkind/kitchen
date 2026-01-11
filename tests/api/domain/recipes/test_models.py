"""Tests for Recipe Domain Models. 🧪

Validates Pydantic DTOs and business logic constraints.
"""

import pytest
from pydantic import ValidationError

from src.api.app.domain.recipes.models import (
    CreateRecipeDTO,
    ParsedIngredient,
    UpdateRecipeDTO,
)


class TestParsedIngredient:
    """Tests for ParsedIngredient model."""

    def test_valid_creation(self):
        """Test creating a valid parsed ingredient."""
        ingredient = ParsedIngredient(
            raw_text="1 cup flour",
            quantity=1.0,
            unit="cup",
            item_name="flour",
        )
        assert ingredient.quantity == 1.0
        assert ingredient.unit == "cup"
        assert ingredient.item_name == "flour"
        assert ingredient.confidence == 1.0  # Default

    def test_optional_fields(self):
        """Test optional fields can be None."""
        ingredient = ParsedIngredient(
            raw_text="some ingredient",
            item_name="ingredient",
        )
        assert ingredient.quantity is None
        assert ingredient.unit is None
        assert ingredient.notes is None

    def test_notes_captured(self):
        """Test notes field captures extra info."""
        ingredient = ParsedIngredient(
            raw_text="1 large onion, diced",
            quantity=1.0,
            unit="count",
            item_name="onion",
            notes="large, diced",
        )
        assert ingredient.notes == "large, diced"

    def test_confidence_bounds(self):
        """Test confidence must be between 0 and 1."""
        # Valid bounds
        ParsedIngredient(raw_text="x", item_name="x", confidence=0.0)
        ParsedIngredient(raw_text="x", item_name="x", confidence=1.0)
        ParsedIngredient(raw_text="x", item_name="x", confidence=0.5)

        # Invalid bounds
        with pytest.raises(ValidationError):
            ParsedIngredient(raw_text="x", item_name="x", confidence=-0.1)

        with pytest.raises(ValidationError):
            ParsedIngredient(raw_text="x", item_name="x", confidence=1.1)


class TestCreateRecipeDTO:
    """Tests for CreateRecipeDTO validation."""

    def test_valid_creation(self):
        """Test creating a valid recipe DTO."""
        dto = CreateRecipeDTO(
            title="Test Recipe",
            source_url="https://example.com/recipe",
            servings=4,
            prep_time_minutes=15,
            cook_time_minutes=30,
        )
        assert dto.title == "Test Recipe"
        assert dto.servings == 4

    def test_title_required(self):
        """Test that title is required."""
        with pytest.raises(ValidationError):
            CreateRecipeDTO(source_url="https://example.com")

    def test_empty_title_rejected(self):
        """Test that empty title is rejected."""
        with pytest.raises(ValidationError):
            CreateRecipeDTO(title="")

    def test_title_max_length(self):
        """Test title max length validation."""
        long_title = "a" * 501
        with pytest.raises(ValidationError):
            CreateRecipeDTO(title=long_title)

    def test_servings_bounds(self):
        """Test servings must be 1-100."""
        CreateRecipeDTO(title="Test", servings=1)  # Min valid
        CreateRecipeDTO(title="Test", servings=100)  # Max valid

        with pytest.raises(ValidationError):
            CreateRecipeDTO(title="Test", servings=0)

        with pytest.raises(ValidationError):
            CreateRecipeDTO(title="Test", servings=101)

    def test_time_cannot_be_negative(self):
        """Test prep and cook times cannot be negative."""
        with pytest.raises(ValidationError):
            CreateRecipeDTO(title="Test", prep_time_minutes=-1)

        with pytest.raises(ValidationError):
            CreateRecipeDTO(title="Test", cook_time_minutes=-1)

    def test_optional_fields_default_none(self):
        """Test all optional fields default to None."""
        dto = CreateRecipeDTO(title="Minimal Recipe")
        assert dto.source_url is None
        assert dto.servings is None
        assert dto.prep_time_minutes is None
        assert dto.cook_time_minutes is None
        assert dto.description is None
        assert dto.instructions is None
        assert dto.tags is None

    def test_tags_as_list(self):
        """Test tags are stored as a list."""
        dto = CreateRecipeDTO(
            title="Tagged Recipe",
            tags=["italian", "quick", "weeknight"],
        )
        assert len(dto.tags) == 3
        assert "italian" in dto.tags


class TestUpdateRecipeDTO:
    """Tests for UpdateRecipeDTO validation."""

    def test_all_fields_optional(self):
        """Test that all update fields are optional."""
        dto = UpdateRecipeDTO()
        assert dto.title is None
        assert dto.servings is None

    def test_partial_update(self):
        """Test partial update with only some fields."""
        dto = UpdateRecipeDTO(title="New Title")
        assert dto.title == "New Title"
        assert dto.servings is None

    def test_title_validation_when_provided(self):
        """Test title is validated when provided."""
        with pytest.raises(ValidationError):
            UpdateRecipeDTO(title="")

    def test_servings_validation_when_provided(self):
        """Test servings validated when provided."""
        with pytest.raises(ValidationError):
            UpdateRecipeDTO(servings=0)
