"""Refiner service tests. 🎰"""

from datetime import date, datetime
from uuid import uuid4

import pytest

from src.api.app.domain.pantry.models import PantryItem, PantryLocation
from src.api.app.domain.planner.models import MealSlot, MealType
from src.api.app.domain.planner.refiner import RefinerService
from src.api.app.domain.recipes.models import Recipe, RecipeIngredient


@pytest.fixture
def sample_recipes() -> list[Recipe]:
    """Create sample recipes for testing."""
    recipe1_id = uuid4()
    recipe2_id = uuid4()
    recipe3_id = uuid4()
    recipe4_id = uuid4()
    return [
        Recipe(
            id=recipe1_id,
            household_id=uuid4(),
            title="Chicken Tacos",
            source_url=None,
            source_domain=None,
            servings=4,
            tags=["mexican", "quick", "spicy"],
            prep_time_minutes=25,
            cook_time_minutes=None,
            total_time_minutes=None,
            description=None,
            is_parsed=True,
            ingredients=[
                RecipeIngredient(
                    id=uuid4(),
                    recipe_id=recipe1_id,
                    raw_text="1 lb chicken",
                    quantity=1.0,
                    unit="lb",
                    item_name="chicken",
                    notes=None,
                    section=None,
                    sort_order=0,
                    confidence=1.0,
                    created_at=datetime.now(),
                ),
            ],
            instructions=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        Recipe(
            id=recipe2_id,
            household_id=uuid4(),
            title="Vegetable Stir Fry",
            source_url=None,
            source_domain=None,
            servings=4,
            tags=["vegetarian", "healthy", "quick"],
            prep_time_minutes=20,
            cook_time_minutes=None,
            total_time_minutes=None,
            description=None,
            is_parsed=True,
            ingredients=[],
            instructions=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        Recipe(
            id=recipe3_id,
            household_id=uuid4(),
            title="Beef Stew",
            source_url=None,
            source_domain=None,
            servings=6,
            tags=["comfort", "hearty"],
            prep_time_minutes=90,
            cook_time_minutes=None,
            total_time_minutes=None,
            description=None,
            is_parsed=True,
            ingredients=[],
            instructions=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        Recipe(
            id=recipe4_id,
            household_id=uuid4(),
            title="Mushroom Risotto",
            source_url=None,
            source_domain=None,
            servings=4,
            tags=["vegetarian", "comfort"],
            prep_time_minutes=45,
            cook_time_minutes=None,
            total_time_minutes=None,
            description=None,
            is_parsed=True,
            ingredients=[
                RecipeIngredient(
                    id=uuid4(),
                    recipe_id=recipe4_id,
                    raw_text="2 cups mushrooms",
                    quantity=2.0,
                    unit="cup",
                    item_name="mushrooms",
                    notes=None,
                    section=None,
                    sort_order=0,
                    confidence=1.0,
                    created_at=datetime.now(),
                ),
            ],
            instructions=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]


@pytest.fixture
def sample_pantry_items() -> list[PantryItem]:
    """Create sample pantry items."""
    return [
        PantryItem(
            id=uuid4(),
            household_id=uuid4(),
            name="chicken",
            quantity=2.0,
            unit="lb",
            location=PantryLocation.FREEZER,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]


@pytest.fixture
def sample_slot() -> MealSlot:
    """Create a sample meal slot."""
    return MealSlot(
        id=uuid4(),
        plan_id=uuid4(),
        date=date.today(),
        meal_type=MealType.DINNER,
        recipe_id=uuid4(),
        is_locked=False,
    )


class TestRefinerService:
    """Tests for RefinerService."""

    @pytest.fixture
    def refiner(self) -> RefinerService:
        return RefinerService()

    @pytest.mark.asyncio
    async def test_reroll_slot_returns_new_recipe(
        self,
        refiner: RefinerService,
        sample_slot,
        sample_recipes,
        sample_pantry_items,
    ):
        """Test rerolling returns a different recipe."""
        result = await refiner.reroll_slot(
            sample_slot,
            sample_recipes,
            sample_pantry_items,
        )

        assert result is not None
        assert result.title is not None
        assert result.id != sample_slot.recipe_id

    @pytest.mark.asyncio
    async def test_reroll_locked_slot_raises_error(
        self,
        refiner: RefinerService,
        sample_recipes,
        sample_pantry_items,
    ):
        """Test rerolling locked slot raises ValueError."""
        locked_slot = MealSlot(
            id=uuid4(),
            plan_id=uuid4(),
            date=date.today(),
            meal_type=MealType.DINNER,
            is_locked=True,
        )

        with pytest.raises(ValueError, match="locked"):
            await refiner.reroll_slot(locked_slot, sample_recipes, sample_pantry_items)

    @pytest.mark.asyncio
    async def test_reroll_with_exclusion_directive(
        self,
        refiner: RefinerService,
        sample_slot,
        sample_recipes,
        sample_pantry_items,
    ):
        """Test reroll with 'no chicken' directive."""
        result = await refiner.reroll_slot(
            sample_slot,
            sample_recipes,
            sample_pantry_items,
            directive="no chicken",
        )

        # Should not return chicken tacos
        assert "chicken" not in result.title.lower()

    @pytest.mark.asyncio
    async def test_reroll_with_quick_directive(
        self,
        refiner: RefinerService,
        sample_slot,
        sample_recipes,
        sample_pantry_items,
    ):
        """Test reroll with 'quick' directive."""
        result = await refiner.reroll_slot(
            sample_slot,
            sample_recipes,
            sample_pantry_items,
            directive="quick",
        )

        assert result.prep_time_minutes is None or result.prep_time_minutes <= 30

    @pytest.mark.asyncio
    async def test_toggle_lock(self, refiner: RefinerService):
        """Test toggling slot lock."""
        slot_id = uuid4()
        result = await refiner.toggle_lock(slot_id, locked=True)

        assert result.is_locked is True

    @pytest.mark.asyncio
    async def test_reroll_day_respects_locks(
        self,
        refiner: RefinerService,
        sample_recipes,
        sample_pantry_items,
    ):
        """Test rerolling a day respects locked slots."""
        slots = [
            MealSlot(
                id=uuid4(),
                plan_id=uuid4(),
                date=date.today(),
                meal_type=MealType.LUNCH,
                recipe_id=sample_recipes[0].id,
                is_locked=True,  # This one is locked
            ),
            MealSlot(
                id=uuid4(),
                plan_id=uuid4(),
                date=date.today(),
                meal_type=MealType.DINNER,
                recipe_id=sample_recipes[1].id,
                is_locked=False,  # This one is not locked
            ),
        ]

        results = await refiner.reroll_day(
            slots,
            sample_recipes,
            sample_pantry_items,
        )

        # Only unlocked slot should be in results
        assert len(results) == 1
        assert results[0][0].meal_type == MealType.DINNER
