"""Shopping service - Business logic layer. 🧠

Orchestrates shopping list management and generation from meal plans.

Fun fact: Shoppers who use lists spend 23% less than those who don't! 💰
"""

from uuid import UUID

from src.api.app.domain.planning.delta_service import DeltaService
from src.api.app.domain.planning.models import DeltaItem
from src.api.app.domain.shopping.models import (
    AggregatedItem,
    CreateShoppingItemDTO,
    CreateShoppingListDTO,
    ShoppingItem,
    ShoppingList,
    ShoppingListSummary,
    UpdateShoppingItemDTO,
)
from src.api.app.domain.shopping.repository import ShoppingRepository


class ShoppingListNotFoundError(Exception):
    """Raised when a shopping list is not found. 🔍"""

    def __init__(self, list_id: UUID) -> None:
        self.list_id = list_id
        super().__init__(f"Shopping list {list_id} not found")


class ShoppingItemNotFoundError(Exception):
    """Raised when a shopping item is not found. 🔍"""

    def __init__(self, item_id: UUID) -> None:
        self.item_id = item_id
        super().__init__(f"Shopping item {item_id} not found")


# Category mapping for common items
CATEGORY_MAP: dict[str, str] = {
    # Produce
    "onion": "Produce",
    "garlic": "Produce",
    "tomato": "Produce",
    "potato": "Produce",
    "carrot": "Produce",
    "celery": "Produce",
    "lettuce": "Produce",
    "spinach": "Produce",
    "broccoli": "Produce",
    "pepper": "Produce",
    "lemon": "Produce",
    "lime": "Produce",
    "apple": "Produce",
    "banana": "Produce",
    "avocado": "Produce",
    "ginger": "Produce",
    "herbs": "Produce",
    "cilantro": "Produce",
    "parsley": "Produce",
    "basil": "Produce",
    # Dairy
    "milk": "Dairy",
    "butter": "Dairy",
    "cheese": "Dairy",
    "cream": "Dairy",
    "yogurt": "Dairy",
    "eggs": "Dairy",
    "sour cream": "Dairy",
    # Meat
    "chicken": "Meat",
    "beef": "Meat",
    "pork": "Meat",
    "ground": "Meat",
    "bacon": "Meat",
    "sausage": "Meat",
    "turkey": "Meat",
    # Bakery
    "bread": "Bakery",
    "tortilla": "Bakery",
    "bun": "Bakery",
    "roll": "Bakery",
    # Pantry
    "rice": "Pantry",
    "pasta": "Pantry",
    "flour": "Pantry",
    "sugar": "Pantry",
    "oil": "Pantry",
    "vinegar": "Pantry",
    "sauce": "Pantry",
    "broth": "Pantry",
    "stock": "Pantry",
    "beans": "Pantry",
    "lentils": "Pantry",
    "canned": "Pantry",
    # Frozen
    "frozen": "Frozen",
    "ice cream": "Frozen",
    # Spices
    "cumin": "Spices",
    "paprika": "Spices",
    "oregano": "Spices",
    "thyme": "Spices",
    "cinnamon": "Spices",
}


class ShoppingService:
    """Service for shopping list business logic. 🛒

    Handles list management, item operations, and generation from plans.
    """

    def __init__(
        self,
        repository: ShoppingRepository,
        delta_service: DeltaService | None = None,
    ) -> None:
        """Initialize service.

        Args:
            repository: The shopping repository instance.
            delta_service: Optional delta service for list generation.
        """
        self.repository = repository
        self.delta_service = delta_service or DeltaService()

    # =========================================================================
    # Shopping Lists
    # =========================================================================

    async def get_list(
        self,
        list_id: UUID,
        household_id: UUID,
    ) -> ShoppingList:
        """Get a shopping list by ID.

        Args:
            list_id: The list's ID.
            household_id: The user's household ID.

        Returns:
            The ShoppingList with items.

        Raises:
            ShoppingListNotFoundError: If list doesn't exist.
        """
        shopping_list = await self.repository.get_list_by_id(
            list_id,
            household_id,
            include_items=True,
        )
        if not shopping_list:
            raise ShoppingListNotFoundError(list_id)
        return shopping_list

    async def get_active_list(
        self,
        household_id: UUID,
    ) -> ShoppingList | None:
        """Get the current active shopping list.

        Args:
            household_id: The household to get list for.

        Returns:
            Active ShoppingList or None if no active list.
        """
        return await self.repository.get_active_list(household_id)

    async def get_or_create_active_list(
        self,
        household_id: UUID,
    ) -> ShoppingList:
        """Get active list or create one if none exists.

        Args:
            household_id: The household.

        Returns:
            The active ShoppingList.
        """
        active = await self.repository.get_active_list(household_id)
        if active:
            return active

        # Create a new list
        dto = CreateShoppingListDTO(name="Shopping List")
        return await self.repository.create_list(household_id, dto)

    async def list_all(
        self,
        household_id: UUID,
        *,
        include_completed: bool = False,
    ) -> list[ShoppingListSummary]:
        """Get all shopping lists for a household.

        Args:
            household_id: The household.
            include_completed: Whether to include completed lists.

        Returns:
            List of shopping list summaries.
        """
        return await self.repository.get_all_lists(
            household_id,
            include_completed=include_completed,
        )

    async def create_list(
        self,
        household_id: UUID,
        dto: CreateShoppingListDTO,
    ) -> ShoppingList:
        """Create a new shopping list.

        Args:
            household_id: The household.
            dto: The list data.

        Returns:
            The created ShoppingList.
        """
        return await self.repository.create_list(household_id, dto)

    async def complete_list(
        self,
        list_id: UUID,
        household_id: UUID,
    ) -> ShoppingList:
        """Mark a shopping list as completed.

        Args:
            list_id: The list to complete.
            household_id: The household.

        Returns:
            The updated ShoppingList.

        Raises:
            ShoppingListNotFoundError: If list doesn't exist.
        """
        result = await self.repository.update_list_status(
            list_id,
            household_id,
            "completed",
        )
        if not result:
            raise ShoppingListNotFoundError(list_id)
        return result

    async def delete_list(
        self,
        list_id: UUID,
        household_id: UUID,
    ) -> None:
        """Delete a shopping list.

        Args:
            list_id: The list to delete.
            household_id: The household.

        Raises:
            ShoppingListNotFoundError: If list doesn't exist.
        """
        deleted = await self.repository.delete_list(list_id, household_id)
        if not deleted:
            raise ShoppingListNotFoundError(list_id)

    # =========================================================================
    # Shopping Items
    # =========================================================================

    async def add_item(
        self,
        list_id: UUID,
        household_id: UUID,
        dto: CreateShoppingItemDTO,
    ) -> ShoppingItem:
        """Add an item to a shopping list.

        Args:
            list_id: The list to add to.
            household_id: The household (for validation).
            dto: The item data.

        Returns:
            The created ShoppingItem.

        Raises:
            ShoppingListNotFoundError: If list doesn't exist.
        """
        # Verify list exists and belongs to household
        shopping_list = await self.repository.get_list_by_id(
            list_id,
            household_id,
            include_items=False,
        )
        if not shopping_list:
            raise ShoppingListNotFoundError(list_id)

        # Auto-assign category if not provided
        if not dto.category:
            dto = CreateShoppingItemDTO(
                name=dto.name,
                quantity=dto.quantity,
                unit=dto.unit,
                category=self._guess_category(dto.name),
                notes=dto.notes,
                recipe_source=dto.recipe_source,
            )

        return await self.repository.add_item(list_id, dto)

    async def update_item(
        self,
        item_id: UUID,
        list_id: UUID,
        household_id: UUID,
        dto: UpdateShoppingItemDTO,
    ) -> ShoppingItem:
        """Update a shopping item.

        Args:
            item_id: The item to update.
            list_id: The list it belongs to.
            household_id: The household.
            dto: The fields to update.

        Returns:
            The updated ShoppingItem.

        Raises:
            ShoppingItemNotFoundError: If item doesn't exist.
        """
        # Verify list belongs to household
        shopping_list = await self.repository.get_list_by_id(
            list_id,
            household_id,
            include_items=False,
        )
        if not shopping_list:
            raise ShoppingListNotFoundError(list_id)

        result = await self.repository.update_item(item_id, list_id, dto)
        if not result:
            raise ShoppingItemNotFoundError(item_id)
        return result

    async def check_item(
        self,
        item_id: UUID,
        list_id: UUID,
        household_id: UUID,
        user_id: UUID | None = None,
    ) -> ShoppingItem:
        """Mark an item as checked (purchased). ✅

        Args:
            item_id: The item to check.
            list_id: The list it belongs to.
            household_id: The household.
            user_id: The user who checked it.

        Returns:
            The updated ShoppingItem.

        Raises:
            ShoppingItemNotFoundError: If item doesn't exist.
        """
        # Verify list belongs to household
        shopping_list = await self.repository.get_list_by_id(
            list_id,
            household_id,
            include_items=False,
        )
        if not shopping_list:
            raise ShoppingListNotFoundError(list_id)

        result = await self.repository.check_item(item_id, list_id, user_id)
        if not result:
            raise ShoppingItemNotFoundError(item_id)
        return result

    async def uncheck_item(
        self,
        item_id: UUID,
        list_id: UUID,
        household_id: UUID,
    ) -> ShoppingItem:
        """Unmark an item (back to pending).

        Args:
            item_id: The item to uncheck.
            list_id: The list it belongs to.
            household_id: The household.

        Returns:
            The updated ShoppingItem.

        Raises:
            ShoppingItemNotFoundError: If item doesn't exist.
        """
        # Verify list belongs to household
        shopping_list = await self.repository.get_list_by_id(
            list_id,
            household_id,
            include_items=False,
        )
        if not shopping_list:
            raise ShoppingListNotFoundError(list_id)

        result = await self.repository.uncheck_item(item_id, list_id)
        if not result:
            raise ShoppingItemNotFoundError(item_id)
        return result

    async def delete_item(
        self,
        item_id: UUID,
        list_id: UUID,
        household_id: UUID,
    ) -> None:
        """Delete a shopping item.

        Args:
            item_id: The item to delete.
            list_id: The list it belongs to.
            household_id: The household.

        Raises:
            ShoppingItemNotFoundError: If item doesn't exist.
        """
        # Verify list belongs to household
        shopping_list = await self.repository.get_list_by_id(
            list_id,
            household_id,
            include_items=False,
        )
        if not shopping_list:
            raise ShoppingListNotFoundError(list_id)

        deleted = await self.repository.delete_item(item_id, list_id)
        if not deleted:
            raise ShoppingItemNotFoundError(item_id)

    async def clear_checked(
        self,
        list_id: UUID,
        household_id: UUID,
    ) -> int:
        """Clear all checked items from a list.

        Args:
            list_id: The list to clear.
            household_id: The household.

        Returns:
            Number of items deleted.

        Raises:
            ShoppingListNotFoundError: If list doesn't exist.
        """
        # Verify list belongs to household
        shopping_list = await self.repository.get_list_by_id(
            list_id,
            household_id,
            include_items=False,
        )
        if not shopping_list:
            raise ShoppingListNotFoundError(list_id)

        return await self.repository.clear_checked_items(list_id)

    # =========================================================================
    # List Generation (Phase 7A)
    # =========================================================================

    def aggregate_delta_items(
        self,
        delta_items: list[DeltaItem],
    ) -> list[AggregatedItem]:
        """Aggregate delta items by combining quantities.

        When multiple recipes need the same ingredient, combine them.

        Args:
            delta_items: List of delta items from comparisons.

        Returns:
            Aggregated items ready for shopping list.
        """
        aggregated: dict[str, AggregatedItem] = {}

        for item in delta_items:
            key = item.item_name.lower().strip()

            if key not in aggregated:
                aggregated[key] = AggregatedItem(
                    name=item.item_name,
                    total_quantity=item.delta_quantity,
                    unit=item.delta_unit,
                    sources=[],
                    category=self._guess_category(item.item_name),
                )
            else:
                existing = aggregated[key]
                # Try to add quantities if units match
                if (
                    existing.total_quantity is not None
                    and item.delta_quantity is not None
                    and existing.unit == item.delta_unit
                ):
                    existing.total_quantity += item.delta_quantity
                elif item.delta_quantity is not None:
                    # Different units - just note it
                    existing.sources.append(f"+{item.delta_quantity} {item.delta_unit or 'units'}")

            # Track source if available
            if item.notes:
                aggregated[key].sources.append(item.notes)

        return list(aggregated.values())

    def delta_items_to_shopping_items(
        self,
        delta_items: list[DeltaItem],
        recipe_source: str | None = None,
    ) -> list[CreateShoppingItemDTO]:
        """Convert delta items to shopping item DTOs.

        Args:
            delta_items: Items that need to be purchased.
            recipe_source: Optional recipe name for attribution.

        Returns:
            List of CreateShoppingItemDTO ready for insertion.
        """
        return [
            CreateShoppingItemDTO(
                name=item.item_name,
                quantity=item.delta_quantity,
                unit=item.delta_unit,
                category=self._guess_category(item.item_name),
                recipe_source=recipe_source,
                notes=item.notes,
            )
            for item in delta_items
        ]

    def _guess_category(self, item_name: str) -> str | None:
        """Guess the category for an item based on name.

        Args:
            item_name: The item name.

        Returns:
            Category string or None if unknown.
        """
        name_lower = item_name.lower()

        # Check exact matches first
        for keyword, category in CATEGORY_MAP.items():
            if keyword in name_lower:
                return category

        return None
