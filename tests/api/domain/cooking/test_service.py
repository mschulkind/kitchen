"""Cooking service tests. 👨‍🍳"""

from datetime import datetime
from uuid import uuid4

import pytest

from src.api.app.domain.cooking.models import MarkCookedRequest
from src.api.app.domain.cooking.prompt_builder import PromptBuilder
from src.api.app.domain.cooking.service import CookingService
from src.api.app.domain.pantry.models import PantryItem, PantryLocation
from src.api.app.domain.recipes.models import Recipe, RecipeIngredient


@pytest.fixture
def sample_recipe() -> Recipe:
    """Create a sample recipe."""
    recipe_id = uuid4()
    return Recipe(
        id=recipe_id,
        household_id=uuid4(),
        title="Simple Pasta",
        source_url="https://example.com/pasta",
        source_domain="example.com",
        servings=2,
        prep_time_minutes=10,
        cook_time_minutes=15,
        total_time_minutes=25,
        description="A simple pasta dish",
        is_parsed=True,
        ingredients=[
            RecipeIngredient(
                id=uuid4(),
                recipe_id=recipe_id,
                raw_text="1 lb pasta",
                quantity=1.0,
                unit="lb",
                item_name="pasta",
                notes=None,
                section=None,
                sort_order=0,
                confidence=1.0,
                created_at=datetime.now(),
            ),
            RecipeIngredient(
                id=uuid4(),
                recipe_id=recipe_id,
                raw_text="2 cups marinara sauce",
                quantity=2.0,
                unit="cup",
                item_name="marinara sauce",
                notes=None,
                section=None,
                sort_order=1,
                confidence=1.0,
                created_at=datetime.now(),
            ),
            RecipeIngredient(
                id=uuid4(),
                recipe_id=recipe_id,
                raw_text="1/2 cup parmesan cheese",
                quantity=0.5,
                unit="cup",
                item_name="parmesan cheese",
                notes=None,
                section=None,
                sort_order=2,
                confidence=1.0,
                created_at=datetime.now(),
            ),
        ],
        instructions=[
            "Boil water in a large pot.",
            "Cook pasta for 10 minutes.",
            "Drain and return to pot.",
            "Add sauce and heat through.",
            "Serve with parmesan.",
        ],
        tags=["pasta", "quick"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_pantry_items() -> list[PantryItem]:
    """Create sample pantry items."""
    return [
        PantryItem(
            id=uuid4(),
            household_id=uuid4(),
            name="pasta",
            quantity=2.0,
            unit="lb",
            location=PantryLocation.PANTRY,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        PantryItem(
            id=uuid4(),
            household_id=uuid4(),
            name="olive oil",
            quantity=1.0,
            unit="bottle",
            location=PantryLocation.PANTRY,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]


class TestPromptBuilder:
    """Tests for PromptBuilder."""

    @pytest.fixture
    def builder(self) -> PromptBuilder:
        return PromptBuilder()

    def test_build_context(self, builder: PromptBuilder, sample_recipe, sample_pantry_items):
        """Test building cooking context."""
        context = builder.build_context(sample_recipe, sample_pantry_items)

        assert context.recipe_title == "Simple Pasta"
        assert len(context.ingredients) == 3
        assert len(context.instructions) == 5

    def test_identifies_available_ingredients(
        self, builder: PromptBuilder, sample_recipe, sample_pantry_items
    ):
        """Test context shows available ingredients."""
        context = builder.build_context(sample_recipe, sample_pantry_items)

        # Pasta is available
        available_names = " ".join(context.available_ingredients).lower()
        assert "pasta" in available_names

    def test_format_markdown(self, builder: PromptBuilder, sample_recipe, sample_pantry_items):
        """Test markdown formatting."""
        context = builder.build_context(sample_recipe, sample_pantry_items)
        response = builder.format_for_clipboard(context, "markdown")

        assert response.format == "markdown"
        assert "# Cooking: Simple Pasta" in response.content
        assert response.character_count > 0

    def test_format_text(self, builder: PromptBuilder, sample_recipe, sample_pantry_items):
        """Test plain text formatting."""
        context = builder.build_context(sample_recipe, sample_pantry_items)
        response = builder.format_for_clipboard(context, "text")

        assert response.format == "text"
        assert "COOKING: Simple Pasta" in response.content


class TestCookingService:
    """Tests for CookingService."""

    @pytest.fixture
    def service(self) -> CookingService:
        return CookingService()

    @pytest.mark.asyncio
    async def test_get_cooking_context(
        self, service: CookingService, sample_recipe, sample_pantry_items
    ):
        """Test getting cooking context."""
        context = await service.get_cooking_context(sample_recipe, sample_pantry_items)

        assert context.recipe_title == "Simple Pasta"
        assert len(context.ingredients) > 0

    @pytest.mark.asyncio
    async def test_get_mise_en_place(self, service: CookingService, sample_recipe):
        """Test getting mise en place checklist."""
        items = await service.get_mise_en_place(sample_recipe)

        assert len(items) == 3  # 3 ingredients
        assert all(not item.is_completed for item in items)

    @pytest.mark.asyncio
    async def test_get_recipe_steps(self, service: CookingService, sample_recipe):
        """Test getting recipe steps."""
        steps = await service.get_recipe_steps(sample_recipe)

        assert len(steps) == 5
        assert steps[0].number == 1
        # Step 2 has "10 minutes" so should have timer
        assert steps[1].timer_required is True
        assert steps[1].duration_minutes == 10

    @pytest.mark.asyncio
    async def test_mark_cooked_deducts_inventory(
        self, service: CookingService, sample_recipe, sample_pantry_items
    ):
        """Test marking cooked decrements inventory."""
        request = MarkCookedRequest(
            recipe_id=sample_recipe.id,
            servings_made=2,
            deduct_inventory=True,
        )

        response = await service.mark_cooked(sample_recipe, sample_pantry_items, request)

        assert response.success is True
        assert len(response.items_decremented) > 0

    @pytest.mark.asyncio
    async def test_start_cooking_session(self, service: CookingService, sample_recipe):
        """Test starting a cooking session."""
        session = await service.start_cooking_session(sample_recipe, servings=4)

        assert session.recipe_id == sample_recipe.id
        assert session.recipe_title == "Simple Pasta"
        assert session.total_steps == 5
        assert session.current_step == 1
        assert session.servings == 4
