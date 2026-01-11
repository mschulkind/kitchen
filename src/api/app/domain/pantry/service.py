"""Pantry service - Business logic layer. 🧠

Contains the business rules for pantry management.
This is where validation, authorization, and domain logic lives.

Fun fact: A well-organized pantry can reduce food waste by up to 25%! 🌍
"""

from uuid import UUID

from src.api.app.domain.pantry.models import (
    CreatePantryItemDTO,
    PantryItem,
    PantryItemList,
    UpdatePantryItemDTO,
)
from src.api.app.domain.pantry.repository import PantryRepository


class PantryItemNotFoundError(Exception):
    """Raised when a pantry item is not found. 🔍"""

    def __init__(self, item_id: UUID) -> None:
        self.item_id = item_id
        super().__init__(f"Pantry item {item_id} not found")


class PantryService:
    """Service for pantry item business logic. 🥫

    Coordinates between the API layer and repository,
    applying business rules and validation.
    """

    def __init__(self, repository: PantryRepository) -> None:
        """Initialize service with repository.

        Args:
            repository: The pantry repository instance.
        """
        self.repository = repository

    async def get_item(self, item_id: UUID, household_id: UUID) -> PantryItem:
        """Get a single pantry item.

        Args:
            item_id: The item's ID.
            household_id: The user's household ID.

        Returns:
            The PantryItem.

        Raises:
            PantryItemNotFoundError: If item doesn't exist.
        """
        item = await self.repository.get_by_id(item_id, household_id)
        if not item:
            raise PantryItemNotFoundError(item_id)
        return item

    async def list_items(
        self,
        household_id: UUID,
        *,
        page: int = 1,
        per_page: int = 50,
    ) -> PantryItemList:
        """List all pantry items for a household.

        Args:
            household_id: The household to list items for.
            page: Page number (1-indexed).
            per_page: Items per page.

        Returns:
            Paginated list of items.
        """
        items, total = await self.repository.get_all_by_household(
            household_id,
            page=page,
            per_page=per_page,
        )

        return PantryItemList(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
        )

    async def create_item(
        self,
        household_id: UUID,
        dto: CreatePantryItemDTO,
    ) -> PantryItem:
        """Create a new pantry item.

        Args:
            household_id: The household to add the item to.
            dto: The item data.

        Returns:
            The created PantryItem.
        """
        # Business rule: Normalize item names (capitalize first letter)
        normalized_dto = CreatePantryItemDTO(
            name=dto.name.strip().title(),
            quantity=dto.quantity,
            unit=dto.unit.lower().strip(),
            location=dto.location,
            expiry_date=dto.expiry_date,
            notes=dto.notes,
        )

        return await self.repository.create(household_id, normalized_dto)

    async def update_item(
        self,
        item_id: UUID,
        household_id: UUID,
        dto: UpdatePantryItemDTO,
    ) -> PantryItem:
        """Update an existing pantry item.

        Args:
            item_id: The item to update.
            household_id: The user's household ID.
            dto: The fields to update.

        Returns:
            The updated PantryItem.

        Raises:
            PantryItemNotFoundError: If item doesn't exist.
        """
        # Normalize name if provided
        if dto.name is not None:
            dto = UpdatePantryItemDTO(
                name=dto.name.strip().title(),
                quantity=dto.quantity,
                unit=dto.unit.lower().strip() if dto.unit else None,
                location=dto.location,
                expiry_date=dto.expiry_date,
                notes=dto.notes,
            )

        item = await self.repository.update(item_id, household_id, dto)
        if not item:
            raise PantryItemNotFoundError(item_id)
        return item

    async def delete_item(self, item_id: UUID, household_id: UUID) -> None:
        """Delete a pantry item.

        Args:
            item_id: The item to delete.
            household_id: The user's household ID.

        Raises:
            PantryItemNotFoundError: If item doesn't exist.
        """
        deleted = await self.repository.delete(item_id, household_id)
        if not deleted:
            raise PantryItemNotFoundError(item_id)

    async def search_items(
        self,
        household_id: UUID,
        query: str,
        *,
        limit: int = 10,
    ) -> list[PantryItem]:
        """Search pantry items by name.

        Args:
            household_id: The household to search in.
            query: The search query.
            limit: Max results.

        Returns:
            Matching items.
        """
        return await self.repository.search_by_name(household_id, query, limit=limit)

    async def confirm_possession(
        self,
        household_id: UUID,
        item_name: str,
        *,
        unit: str = "count",
        quantity: float = 1.0,
    ) -> PantryItem:
        """Confirm possession of an item (Lazy Discovery - D13). 🔍

        When a user confirms they have an item during recipe verification,
        this method creates a persistent pantry entry.

        Args:
            household_id: The household.
            item_name: The item name to add.
            unit: Default unit (defaults to "count").
            quantity: Default quantity (defaults to 1).

        Returns:
            The created or existing PantryItem.
        """
        # Check if item already exists
        existing = await self.repository.search_by_name(
            household_id,
            item_name,
            limit=1,
        )

        if existing:
            # Item exists, return it
            return existing[0]

        # Create new item via Lazy Discovery
        dto = CreatePantryItemDTO(
            name=item_name,
            quantity=quantity,
            unit=unit,
        )

        return await self.repository.create(household_id, dto)
