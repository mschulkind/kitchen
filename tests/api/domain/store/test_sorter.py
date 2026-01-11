"""Store sorter tests. 🏪"""

from datetime import datetime
from uuid import uuid4

import pytest

from src.api.app.domain.shopping.models import ShoppingItem, ShoppingItemStatus
from src.api.app.domain.store.sorter import StoreSorter


class TestStoreSorter:
    """Tests for StoreSorter."""

    @pytest.fixture
    def sorter(self) -> StoreSorter:
        """Create sorter instance."""
        return StoreSorter()

    @pytest.fixture
    def sample_items(self) -> list[ShoppingItem]:
        """Create sample shopping items."""
        list_id = uuid4()
        return [
            ShoppingItem(
                id=uuid4(),
                shopping_list_id=list_id,
                name="Milk",
                quantity=1,
                unit="gallon",
                status=ShoppingItemStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            ShoppingItem(
                id=uuid4(),
                shopping_list_id=list_id,
                name="Bread",
                quantity=1,
                unit="loaf",
                status=ShoppingItemStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            ShoppingItem(
                id=uuid4(),
                shopping_list_id=list_id,
                name="Apples",
                quantity=6,
                unit="count",
                status=ShoppingItemStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]

    def test_sort_list_groups_by_aisle(self, sorter: StoreSorter, sample_items):
        """Test items are grouped by aisle."""
        list_id = uuid4()
        result = sorter.sort_list(sample_items, list_id)

        assert len(result.items) == 3
        # Apples should be in Produce, Milk in Dairy, Bread in Bakery
        aisles = {item.aisle for item in result.items}
        assert "Produce" in aisles
        assert "Dairy" in aisles
        assert "Bakery" in aisles

    def test_sort_list_orders_correctly(self, sorter: StoreSorter, sample_items):
        """Test items are ordered by aisle traversal."""
        list_id = uuid4()
        result = sorter.sort_list(sample_items, list_id)

        # Produce should come before Bakery, which comes before Dairy
        aisle_order = [item.aisle for item in result.items]
        produce_idx = next(i for i, a in enumerate(aisle_order) if a == "Produce")
        bakery_idx = next(i for i, a in enumerate(aisle_order) if a == "Bakery")
        dairy_idx = next(i for i, a in enumerate(aisle_order) if a == "Dairy")

        assert produce_idx < bakery_idx < dairy_idx

    def test_unknown_items_separate(self, sorter: StoreSorter):
        """Test unknown items go to separate list."""
        list_id = uuid4()
        items = [
            ShoppingItem(
                id=uuid4(),
                shopping_list_id=list_id,
                name="Weird Exotic Fruit",
                quantity=1,
                unit="count",
                status=ShoppingItemStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]

        result = sorter.sort_list(items, list_id)

        assert len(result.unknown_items) == 1
        assert result.unknown_items[0].aisle == "Unknown"

    def test_aisle_summary(self, sorter: StoreSorter, sample_items):
        """Test aisle summary counts."""
        list_id = uuid4()
        result = sorter.sort_list(sample_items, list_id)
        summary = sorter.get_aisle_summary(result)

        assert summary["Produce"] == 1
        assert summary["Dairy"] == 1
        assert summary["Bakery"] == 1


class TestStoreSorterEdgeCases:
    """Edge case tests for StoreSorter."""

    @pytest.fixture
    def sorter(self) -> StoreSorter:
        return StoreSorter()

    def test_empty_list(self, sorter: StoreSorter):
        """Test sorting empty list."""
        list_id = uuid4()
        result = sorter.sort_list([], list_id)

        assert len(result.items) == 0
        assert len(result.unknown_items) == 0

    def test_preserves_checked_status(self, sorter: StoreSorter):
        """Test checked status is preserved."""
        list_id = uuid4()
        items = [
            ShoppingItem(
                id=uuid4(),
                shopping_list_id=list_id,
                name="Milk",
                quantity=1,
                unit="gallon",
                status=ShoppingItemStatus.CHECKED,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]

        result = sorter.sort_list(items, list_id)

        assert result.items[0].is_checked is True
