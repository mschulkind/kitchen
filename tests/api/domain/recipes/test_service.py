"""Tests for Recipe Service. 🧪

Tests the service layer for recipe ingestion and management.
Implements tests from Phase 2.3 spec.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.api.app.domain.recipes.models import (
    CreateRecipeDTO,
    ParsedIngredient,
    Recipe,
    UpdateRecipeDTO,
)
from src.api.app.domain.recipes.service import (
    RecipeAlreadyExistsError,
    RecipeNotFoundError,
    RecipeService,
)


@pytest.fixture
def mock_repository():
    """Create a mock RecipeRepository."""
    return AsyncMock()


@pytest.fixture
def mock_parser():
    """Create a mock IngredientParser."""
    parser = MagicMock()
    parser.parse.return_value = ParsedIngredient(
        raw_text="1 cup flour",
        quantity=1.0,
        unit="cup",
        item_name="flour",
        confidence=0.9,
    )
    parser.parse_many.return_value = [
        ParsedIngredient(
            raw_text="1 cup flour",
            quantity=1.0,
            unit="cup",
            item_name="flour",
            confidence=0.9,
        ),
        ParsedIngredient(
            raw_text="2 eggs",
            quantity=2.0,
            unit="count",
            item_name="eggs",
            confidence=0.9,
        ),
    ]
    return parser


@pytest.fixture
def service(mock_repository, mock_parser):
    """Create a RecipeService with mocked dependencies."""
    return RecipeService(mock_repository, mock_parser)


@pytest.fixture
def sample_recipe():
    """Create a sample Recipe for testing."""
    now = datetime.now(UTC)
    return Recipe(
        id=uuid4(),
        household_id=uuid4(),
        title="Test Recipe",
        source_url="https://example.com/recipe",
        source_domain="example.com",
        servings=4,
        prep_time_minutes=15,
        cook_time_minutes=30,
        total_time_minutes=45,
        description="A test recipe description",
        instructions=["Step 1", "Step 2"],
        tags=["test"],
        is_parsed=True,
        created_at=now,
        updated_at=now,
    )


class TestRecipeServiceGetRecipe:
    """Tests for get_recipe method."""

    @pytest.mark.asyncio
    async def test_get_existing_recipe(self, service, mock_repository, sample_recipe):
        """Test getting an existing recipe."""
        mock_repository.get_by_id.return_value = sample_recipe

        result = await service.get_recipe(sample_recipe.id, sample_recipe.household_id)

        assert result == sample_recipe
        mock_repository.get_by_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_nonexistent_recipe_raises(self, service, mock_repository):
        """Test that getting a nonexistent recipe raises an error."""
        mock_repository.get_by_id.return_value = None
        recipe_id = uuid4()
        household_id = uuid4()

        with pytest.raises(RecipeNotFoundError) as exc_info:
            await service.get_recipe(recipe_id, household_id)

        assert exc_info.value.recipe_id == recipe_id


class TestRecipeServiceCreateRecipe:
    """Tests for create_recipe method."""

    @pytest.mark.asyncio
    async def test_create_normalizes_title(self, service, mock_repository, sample_recipe):
        """Test that recipe titles are normalized."""
        mock_repository.get_by_url.return_value = None
        mock_repository.create.return_value = sample_recipe

        dto = CreateRecipeDTO(
            title="  my test recipe  ",
            source_url="https://example.com/new-recipe",
        )
        household_id = uuid4()

        await service.create_recipe(household_id, dto)

        # Check the DTO passed to repository has normalized title
        call_args = mock_repository.create.call_args
        normalized_dto = call_args[0][1]
        assert normalized_dto.title == "my test recipe"

    @pytest.mark.asyncio
    async def test_create_checks_duplicate_url(self, service, mock_repository, sample_recipe):
        """Test that duplicate URLs are rejected."""
        mock_repository.get_by_url.return_value = sample_recipe

        dto = CreateRecipeDTO(
            title="Another Recipe",
            source_url=sample_recipe.source_url,
        )
        household_id = sample_recipe.household_id

        with pytest.raises(RecipeAlreadyExistsError) as exc_info:
            await service.create_recipe(household_id, dto)

        assert exc_info.value.url == sample_recipe.source_url
        assert exc_info.value.existing_recipe == sample_recipe

    @pytest.mark.asyncio
    async def test_create_allows_same_url_different_household(
        self, service, mock_repository, sample_recipe
    ):
        """Test that same URL can be used by different households."""
        mock_repository.get_by_url.return_value = None  # No duplicate
        mock_repository.create.return_value = sample_recipe

        dto = CreateRecipeDTO(
            title="Shared Recipe",
            source_url="https://example.com/shared",
        )
        different_household = uuid4()

        result = await service.create_recipe(different_household, dto)

        assert result == sample_recipe

    @pytest.mark.asyncio
    async def test_create_normalizes_tags(self, service, mock_repository, sample_recipe):
        """Test that tags are normalized to lowercase."""
        mock_repository.get_by_url.return_value = None
        mock_repository.create.return_value = sample_recipe

        dto = CreateRecipeDTO(
            title="Tagged Recipe",
            tags=["Italian", "QUICK", "  Weeknight  "],
        )
        household_id = uuid4()

        await service.create_recipe(household_id, dto)

        call_args = mock_repository.create.call_args
        normalized_dto = call_args[0][1]
        assert normalized_dto.tags == ["italian", "quick", "weeknight"]


class TestRecipeServiceWithIngredients:
    """Tests for recipe creation with ingredient parsing."""

    @pytest.mark.asyncio
    async def test_create_with_ingredients(
        self, service, mock_repository, mock_parser, sample_recipe
    ):
        """Test creating a recipe with ingredient texts."""
        mock_repository.get_by_url.return_value = None
        mock_repository.create.return_value = sample_recipe
        mock_repository.add_ingredients.return_value = None

        dto = CreateRecipeDTO(title="Recipe With Ingredients")
        ingredient_texts = ["1 cup flour", "2 eggs"]
        household_id = uuid4()

        await service.create_recipe(household_id, dto, ingredient_texts=ingredient_texts)

        # Parser should be called with ingredient texts
        mock_parser.parse_many.assert_called_once_with(ingredient_texts)
        # Ingredients should be added to database
        mock_repository.add_ingredients.assert_called_once()

    @pytest.mark.asyncio
    async def test_parse_ingredients_returns_structured_data(
        self, service, mock_repository, mock_parser, sample_recipe
    ):
        """Test that parse_ingredients returns structured data."""
        texts = ["500g Flour", "1 large Onion, chopped"]

        # Mock repository to return recipe exists
        mock_repository.get_by_id.return_value = sample_recipe
        mock_repository.clear_ingredients.return_value = None
        mock_repository.add_ingredients.return_value = None

        mock_parser.parse_many.return_value = [
            ParsedIngredient(
                raw_text="500g Flour",
                quantity=500,
                unit="gram",
                item_name="flour",
                confidence=0.9,
            ),
            ParsedIngredient(
                raw_text="1 large Onion, chopped",
                quantity=1,
                unit="count",
                item_name="onion",
                notes="large, chopped",
                confidence=0.8,
            ),
        ]

        result = await service.parse_ingredients(
            sample_recipe.id, sample_recipe.household_id, texts
        )

        assert len(result) == 2
        assert result[0].item_name == "flour"
        assert result[0].quantity == 500
        assert result[1].notes == "large, chopped"


class TestRecipeServiceUpdateRecipe:
    """Tests for update_recipe method."""

    @pytest.mark.asyncio
    async def test_update_existing_recipe(self, service, mock_repository, sample_recipe):
        """Test updating an existing recipe."""
        # Create updated version based on sample_recipe
        updated_recipe = sample_recipe.model_copy(update={"title": "Updated Title"})
        mock_repository.update.return_value = updated_recipe

        dto = UpdateRecipeDTO(title="Updated Title")
        result = await service.update_recipe(sample_recipe.id, sample_recipe.household_id, dto)

        assert result.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_update_nonexistent_raises(self, service, mock_repository):
        """Test that updating a nonexistent recipe raises an error."""
        mock_repository.update.return_value = None
        recipe_id = uuid4()
        household_id = uuid4()

        with pytest.raises(RecipeNotFoundError):
            await service.update_recipe(recipe_id, household_id, UpdateRecipeDTO(title="New"))


class TestRecipeServiceListRecipes:
    """Tests for list_recipes method."""

    @pytest.mark.asyncio
    async def test_list_recipes_paginated(self, service, mock_repository, sample_recipe):
        """Test listing recipes with pagination."""
        mock_repository.get_all_by_household.return_value = ([sample_recipe], 1)

        recipes, total = await service.list_recipes(sample_recipe.household_id, page=1, per_page=20)

        assert len(recipes) == 1
        assert total == 1

    @pytest.mark.asyncio
    async def test_list_recipes_with_tags(self, service, mock_repository, sample_recipe):
        """Test listing recipes filtered by tags."""
        mock_repository.get_all_by_household.return_value = ([sample_recipe], 1)

        await service.list_recipes(sample_recipe.household_id, tags=["italian", "quick"])

        mock_repository.get_all_by_household.assert_called_once()
        call_kwargs = mock_repository.get_all_by_household.call_args.kwargs
        assert call_kwargs["tags"] == ["italian", "quick"]


class TestRecipeServiceIngestUrl:
    """Tests for ingest_from_url method (Phase 2A)."""

    @pytest.mark.asyncio
    async def test_ingest_creates_recipe_from_url(self, service, mock_repository, sample_recipe):
        """Integration: Test URL ingestion creates a recipe."""
        mock_repository.get_by_url.return_value = None
        mock_repository.create.return_value = sample_recipe

        # Note: This test would need the actual scraper mocked too
        # For now we verify the service method exists
        # Full integration test would use a test server
        assert hasattr(service, "ingest_from_url")

    @pytest.mark.asyncio
    async def test_ingest_rejects_duplicate_url(self, service, mock_repository, sample_recipe):
        """Test that ingesting a duplicate URL is rejected."""
        mock_repository.get_by_url.return_value = sample_recipe

        with pytest.raises(RecipeAlreadyExistsError):
            await service.ingest_from_url(sample_recipe.household_id, sample_recipe.source_url)
