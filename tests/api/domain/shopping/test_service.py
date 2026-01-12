"""Tests for Shopping Service. 🛒

Tests shopping list business logic.
"""

from src.api.app.domain.planning.models import DeltaItem
from src.api.app.domain.shopping.service import ShoppingService


class TestCategoryGuessing:
    """Tests for category guessing logic."""

    def test_guess_produce_category(self) -> None:
        """Produce items are categorized correctly."""
        service = ShoppingService(repository=None)  # type: ignore

        assert service._guess_category("Fresh Onion") == "Produce"
        assert service._guess_category("Garlic Cloves") == "Produce"
        assert service._guess_category("Baby Spinach") == "Produce"
        assert service._guess_category("Roma Tomatoes") == "Produce"

    def test_guess_dairy_category(self) -> None:
        """Dairy items are categorized correctly."""
        service = ShoppingService(repository=None)  # type: ignore

        assert service._guess_category("Whole Milk") == "Dairy"
        assert service._guess_category("Unsalted Butter") == "Dairy"
        assert service._guess_category("Sharp Cheddar Cheese") == "Dairy"
        assert service._guess_category("Eggs") == "Dairy"

    def test_guess_meat_category(self) -> None:
        """Meat items are categorized correctly."""
        service = ShoppingService(repository=None)  # type: ignore

        assert service._guess_category("Chicken Breast") == "Meat"
        assert service._guess_category("Ground Beef") == "Meat"
        assert service._guess_category("Pork Chops") == "Meat"
        assert service._guess_category("Bacon Strips") == "Meat"

    def test_guess_pantry_category(self) -> None:
        """Pantry items are categorized correctly."""
        service = ShoppingService(repository=None)  # type: ignore

        assert service._guess_category("Long Grain Rice") == "Pantry"
        assert service._guess_category("Spaghetti Pasta") == "Pantry"
        assert service._guess_category("All-Purpose Flour") == "Pantry"
        assert service._guess_category("Olive Oil") == "Pantry"

    def test_guess_unknown_returns_none(self) -> None:
        """Unknown items return None category."""
        service = ShoppingService(repository=None)  # type: ignore

        assert service._guess_category("Exotic Mystery Item") is None
        assert service._guess_category("Special Widget") is None


class TestDeltaConversion:
    """Tests for converting delta items to shopping items."""

    def test_delta_items_to_shopping_items(self) -> None:
        """Delta items are converted to shopping DTOs."""
        service = ShoppingService(repository=None)  # type: ignore

        delta_items = [
            DeltaItem(
                item_name="Onion",
                recipe_quantity=2,
                recipe_unit="count",
                inventory_quantity=0,
                inventory_unit=None,
                delta_quantity=2,
                delta_unit="count",
                status="missing",
            ),
            DeltaItem(
                item_name="Butter",
                recipe_quantity=1,
                recipe_unit="stick",
                inventory_quantity=0,
                inventory_unit=None,
                delta_quantity=1,
                delta_unit="stick",
                status="missing",
            ),
        ]

        shopping_items = service.delta_items_to_shopping_items(
            delta_items, recipe_source="Test Recipe"
        )

        assert len(shopping_items) == 2
        assert shopping_items[0].name == "Onion"
        assert shopping_items[0].quantity == 2
        assert shopping_items[0].unit == "count"
        assert shopping_items[0].category == "Produce"
        assert shopping_items[0].recipe_source == "Test Recipe"

        assert shopping_items[1].name == "Butter"
        assert shopping_items[1].category == "Dairy"

    def test_empty_delta_items(self) -> None:
        """Empty delta list returns empty shopping list."""
        service = ShoppingService(repository=None)  # type: ignore

        shopping_items = service.delta_items_to_shopping_items([])

        assert shopping_items == []


class TestItemAggregation:
    """Tests for aggregating delta items."""

    def test_aggregate_same_items(self) -> None:
        """Same items from different sources are combined."""
        service = ShoppingService(repository=None)  # type: ignore

        delta_items = [
            DeltaItem(
                item_name="Onion",
                recipe_quantity=1,
                recipe_unit="count",
                inventory_quantity=0,
                inventory_unit=None,
                delta_quantity=1,
                delta_unit="count",
                status="missing",
            ),
            DeltaItem(
                item_name="Onion",
                recipe_quantity=2,
                recipe_unit="count",
                inventory_quantity=0,
                inventory_unit=None,
                delta_quantity=2,
                delta_unit="count",
                status="missing",
            ),
        ]

        aggregated = service.aggregate_delta_items(delta_items)

        assert len(aggregated) == 1
        assert aggregated[0].name == "Onion"
        assert aggregated[0].total_quantity == 3  # 1 + 2

    def test_aggregate_different_items(self) -> None:
        """Different items remain separate."""
        service = ShoppingService(repository=None)  # type: ignore

        delta_items = [
            DeltaItem(
                item_name="Onion",
                recipe_quantity=1,
                recipe_unit="count",
                inventory_quantity=0,
                inventory_unit=None,
                delta_quantity=1,
                delta_unit="count",
                status="missing",
            ),
            DeltaItem(
                item_name="Garlic",
                recipe_quantity=3,
                recipe_unit="cloves",
                inventory_quantity=0,
                inventory_unit=None,
                delta_quantity=3,
                delta_unit="cloves",
                status="missing",
            ),
        ]

        aggregated = service.aggregate_delta_items(delta_items)

        assert len(aggregated) == 2
        names = {item.name for item in aggregated}
        assert "Onion" in names
        assert "Garlic" in names

    def test_aggregate_assigns_categories(self) -> None:
        """Aggregated items get category assignments."""
        service = ShoppingService(repository=None)  # type: ignore

        delta_items = [
            DeltaItem(
                item_name="Milk",
                recipe_quantity=1,
                recipe_unit="gallon",
                inventory_quantity=0,
                inventory_unit=None,
                delta_quantity=1,
                delta_unit="gallon",
                status="missing",
            ),
        ]

        aggregated = service.aggregate_delta_items(delta_items)

        assert len(aggregated) == 1
        assert aggregated[0].category == "Dairy"
