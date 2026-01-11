"""Shopping repository - Database access layer. 🗄️

Handles all database operations for shopping lists and items.

Fun fact: Online grocery shopping grew 300% during 2020! 📱
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from src.api.app.domain.shopping.models import (
    CreateShoppingItemDTO,
    CreateShoppingListDTO,
    ShoppingItem,
    ShoppingItemStatus,
    ShoppingList,
    ShoppingListSummary,
    UpdateShoppingItemDTO,
)

if TYPE_CHECKING:
    from supabase import AsyncClient


class ShoppingRepository:
    """Repository for shopping list CRUD operations. 🛒"""

    LISTS_TABLE = "shopping_lists"
    ITEMS_TABLE = "shopping_list_items"

    def __init__(self, supabase: "AsyncClient") -> None:
        """Initialize repository with Supabase client."""
        self.supabase = supabase

    # =========================================================================
    # Shopping Lists
    # =========================================================================

    async def get_list_by_id(
        self,
        list_id: UUID,
        household_id: UUID,
        *,
        include_items: bool = True,
    ) -> ShoppingList | None:
        """Get a shopping list by ID.

        Args:
            list_id: The list's unique identifier.
            household_id: The household to scope the query to (RLS).
            include_items: Whether to fetch items.

        Returns:
            ShoppingList if found, None otherwise.
        """
        result = await (
            self.supabase.table(self.LISTS_TABLE)
            .select("*")
            .eq("id", str(list_id))
            .eq("household_id", str(household_id))
            .maybe_single()
            .execute()
        )

        if not result.data:
            return None

        shopping_list = ShoppingList.model_validate(result.data)

        if include_items:
            shopping_list.items = await self._get_items(list_id)

        return shopping_list

    async def get_active_list(
        self,
        household_id: UUID,
    ) -> ShoppingList | None:
        """Get the active shopping list for a household.

        Most households have one active list at a time.
        """
        result = await (
            self.supabase.table(self.LISTS_TABLE)
            .select("*")
            .eq("household_id", str(household_id))
            .eq("status", "active")
            .order("created_at", desc=True)
            .limit(1)
            .maybe_single()
            .execute()
        )

        if not result.data:
            return None

        shopping_list = ShoppingList.model_validate(result.data)
        shopping_list.items = await self._get_items(shopping_list.id)
        return shopping_list

    async def get_all_lists(
        self,
        household_id: UUID,
        *,
        include_completed: bool = False,
    ) -> list[ShoppingListSummary]:
        """Get all shopping lists for a household.

        Args:
            household_id: The household to list for.
            include_completed: Whether to include completed/archived lists.

        Returns:
            List of shopping list summaries.
        """
        query = (
            self.supabase.table(self.LISTS_TABLE)
            .select("*")
            .eq("household_id", str(household_id))
            .order("created_at", desc=True)
        )

        if not include_completed:
            query = query.eq("status", "active")

        result = await query.execute()

        summaries = []
        for row in result.data or []:
            # Get item counts for each list
            items_result = await (
                self.supabase.table(self.ITEMS_TABLE)
                .select("status")
                .eq("shopping_list_id", row["id"])
                .execute()
            )
            items = items_result.data or []
            total = len(items)
            checked = sum(1 for i in items if i["status"] == "checked")

            summaries.append(
                ShoppingListSummary(
                    id=row["id"],
                    name=row["name"],
                    status=row["status"],
                    total_items=total,
                    checked_items=checked,
                    created_at=row["created_at"],
                )
            )

        return summaries

    async def create_list(
        self,
        household_id: UUID,
        dto: CreateShoppingListDTO,
    ) -> ShoppingList:
        """Create a new shopping list.

        Args:
            household_id: The household to add the list to.
            dto: The list data.

        Returns:
            The created ShoppingList.
        """
        now = datetime.now(UTC)
        list_id = uuid4()

        data = {
            "id": str(list_id),
            "household_id": str(household_id),
            "name": dto.name,
            "status": "active",
            "plan_id": str(dto.plan_id) if dto.plan_id else None,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        result = await (
            self.supabase.table(self.LISTS_TABLE)
            .insert(data)
            .execute()
        )

        return ShoppingList.model_validate(result.data[0])

    async def update_list_status(
        self,
        list_id: UUID,
        household_id: UUID,
        status: str,
    ) -> ShoppingList | None:
        """Update a shopping list's status.

        Args:
            list_id: The list to update.
            household_id: The household (for RLS).
            status: New status (active, completed, archived).

        Returns:
            Updated list or None if not found.
        """
        now = datetime.now(UTC)
        data: dict = {
            "status": status,
            "updated_at": now.isoformat(),
        }

        if status == "completed":
            data["completed_at"] = now.isoformat()

        result = await (
            self.supabase.table(self.LISTS_TABLE)
            .update(data)
            .eq("id", str(list_id))
            .eq("household_id", str(household_id))
            .execute()
        )

        if result.data:
            return ShoppingList.model_validate(result.data[0])
        return None

    async def delete_list(
        self,
        list_id: UUID,
        household_id: UUID,
    ) -> bool:
        """Delete a shopping list and all its items.

        Args:
            list_id: The list to delete.
            household_id: The household (for RLS).

        Returns:
            True if deleted, False if not found.
        """
        # Delete items first (cascade)
        await (
            self.supabase.table(self.ITEMS_TABLE)
            .delete()
            .eq("shopping_list_id", str(list_id))
            .execute()
        )

        result = await (
            self.supabase.table(self.LISTS_TABLE)
            .delete()
            .eq("id", str(list_id))
            .eq("household_id", str(household_id))
            .execute()
        )

        return len(result.data or []) > 0

    # =========================================================================
    # Shopping Items
    # =========================================================================

    async def _get_items(self, list_id: UUID) -> list[ShoppingItem]:
        """Get all items for a shopping list."""
        result = await (
            self.supabase.table(self.ITEMS_TABLE)
            .select("*")
            .eq("shopping_list_id", str(list_id))
            .order("category", nullsfirst=False)
            .order("name")
            .execute()
        )

        return [ShoppingItem.model_validate(row) for row in result.data or []]

    async def add_item(
        self,
        list_id: UUID,
        dto: CreateShoppingItemDTO,
    ) -> ShoppingItem:
        """Add an item to a shopping list.

        Args:
            list_id: The list to add to.
            dto: The item data.

        Returns:
            The created ShoppingItem.
        """
        now = datetime.now(UTC)
        item_id = uuid4()

        data = {
            "id": str(item_id),
            "shopping_list_id": str(list_id),
            "name": dto.name.strip().title(),
            "quantity": dto.quantity,
            "unit": dto.unit.lower().strip() if dto.unit else None,
            "category": dto.category,
            "status": ShoppingItemStatus.PENDING.value,
            "notes": dto.notes,
            "recipe_source": dto.recipe_source,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        result = await (
            self.supabase.table(self.ITEMS_TABLE)
            .insert(data)
            .execute()
        )

        return ShoppingItem.model_validate(result.data[0])

    async def add_items_batch(
        self,
        list_id: UUID,
        items: list[CreateShoppingItemDTO],
    ) -> list[ShoppingItem]:
        """Add multiple items to a shopping list.

        More efficient than adding one at a time.
        """
        if not items:
            return []

        now = datetime.now(UTC)
        data = [
            {
                "id": str(uuid4()),
                "shopping_list_id": str(list_id),
                "name": item.name.strip().title(),
                "quantity": item.quantity,
                "unit": item.unit.lower().strip() if item.unit else None,
                "category": item.category,
                "status": ShoppingItemStatus.PENDING.value,
                "notes": item.notes,
                "recipe_source": item.recipe_source,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
            }
            for item in items
        ]

        result = await (
            self.supabase.table(self.ITEMS_TABLE)
            .insert(data)
            .execute()
        )

        return [ShoppingItem.model_validate(row) for row in result.data]

    async def update_item(
        self,
        item_id: UUID,
        list_id: UUID,
        dto: UpdateShoppingItemDTO,
    ) -> ShoppingItem | None:
        """Update a shopping item.

        Args:
            item_id: The item to update.
            list_id: The list it belongs to.
            dto: The fields to update.

        Returns:
            Updated item or None if not found.
        """
        now = datetime.now(UTC)
        data: dict = {"updated_at": now.isoformat()}

        if dto.name is not None:
            data["name"] = dto.name.strip().title()
        if dto.quantity is not None:
            data["quantity"] = dto.quantity
        if dto.unit is not None:
            data["unit"] = dto.unit.lower().strip()
        if dto.category is not None:
            data["category"] = dto.category
        if dto.status is not None:
            data["status"] = dto.status.value
            if dto.status == ShoppingItemStatus.CHECKED:
                data["checked_at"] = now.isoformat()
        if dto.notes is not None:
            data["notes"] = dto.notes

        result = await (
            self.supabase.table(self.ITEMS_TABLE)
            .update(data)
            .eq("id", str(item_id))
            .eq("shopping_list_id", str(list_id))
            .execute()
        )

        if result.data:
            return ShoppingItem.model_validate(result.data[0])
        return None

    async def check_item(
        self,
        item_id: UUID,
        list_id: UUID,
        user_id: UUID | None = None,
    ) -> ShoppingItem | None:
        """Mark an item as checked (purchased).

        Args:
            item_id: The item to check.
            list_id: The list it belongs to.
            user_id: The user who checked it.

        Returns:
            Updated item or None if not found.
        """
        now = datetime.now(UTC)
        data = {
            "status": ShoppingItemStatus.CHECKED.value,
            "checked_at": now.isoformat(),
            "checked_by_user_id": str(user_id) if user_id else None,
            "updated_at": now.isoformat(),
        }

        result = await (
            self.supabase.table(self.ITEMS_TABLE)
            .update(data)
            .eq("id", str(item_id))
            .eq("shopping_list_id", str(list_id))
            .execute()
        )

        if result.data:
            return ShoppingItem.model_validate(result.data[0])
        return None

    async def uncheck_item(
        self,
        item_id: UUID,
        list_id: UUID,
    ) -> ShoppingItem | None:
        """Unmark an item (back to pending).

        Args:
            item_id: The item to uncheck.
            list_id: The list it belongs to.

        Returns:
            Updated item or None if not found.
        """
        data = {
            "status": ShoppingItemStatus.PENDING.value,
            "checked_at": None,
            "checked_by_user_id": None,
            "updated_at": datetime.now(UTC).isoformat(),
        }

        result = await (
            self.supabase.table(self.ITEMS_TABLE)
            .update(data)
            .eq("id", str(item_id))
            .eq("shopping_list_id", str(list_id))
            .execute()
        )

        if result.data:
            return ShoppingItem.model_validate(result.data[0])
        return None

    async def delete_item(
        self,
        item_id: UUID,
        list_id: UUID,
    ) -> bool:
        """Delete a shopping item.

        Args:
            item_id: The item to delete.
            list_id: The list it belongs to.

        Returns:
            True if deleted, False if not found.
        """
        result = await (
            self.supabase.table(self.ITEMS_TABLE)
            .delete()
            .eq("id", str(item_id))
            .eq("shopping_list_id", str(list_id))
            .execute()
        )

        return len(result.data or []) > 0

    async def clear_checked_items(
        self,
        list_id: UUID,
    ) -> int:
        """Delete all checked items from a list.

        Useful after a shopping trip.

        Returns:
            Number of items deleted.
        """
        result = await (
            self.supabase.table(self.ITEMS_TABLE)
            .delete()
            .eq("shopping_list_id", str(list_id))
            .eq("status", ShoppingItemStatus.CHECKED.value)
            .execute()
        )

        return len(result.data or [])
