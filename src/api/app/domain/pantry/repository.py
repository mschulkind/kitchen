"""Pantry repository - Database access layer. 🗄️

Handles all database operations for pantry items.
Uses Supabase client for PostgreSQL access.

Fun fact: The word "repository" comes from Latin "repositorium",
meaning "a place where things are stored" - perfect for a pantry! 📚
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from src.api.app.domain.pantry.models import (
    CreatePantryItemDTO,
    PantryItem,
    UpdatePantryItemDTO,
)

if TYPE_CHECKING:
    from supabase import AsyncClient


class PantryRepository:
    """Repository for pantry item CRUD operations. 🥫"""

    TABLE_NAME = "pantry_items"

    def __init__(self, supabase: "AsyncClient") -> None:
        """Initialize repository with Supabase client."""
        self.supabase = supabase

    async def get_by_id(self, item_id: UUID, household_id: UUID) -> PantryItem | None:
        """Get a single pantry item by ID.

        Args:
            item_id: The item's unique identifier.
            household_id: The household to scope the query to (RLS).

        Returns:
            PantryItem if found, None otherwise.
        """
        result = await (
            self.supabase.table(self.TABLE_NAME)
            .select("*")
            .eq("id", str(item_id))
            .eq("household_id", str(household_id))
            .maybe_single()
            .execute()
        )

        if result.data:
            return PantryItem.model_validate(result.data)
        return None

    async def get_all_by_household(
        self,
        household_id: UUID,
        *,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[PantryItem], int]:
        """Get all pantry items for a household.

        Args:
            household_id: The household to fetch items for.
            page: Page number (1-indexed).
            per_page: Items per page.

        Returns:
            Tuple of (items list, total count).
        """
        offset = (page - 1) * per_page

        # Get paginated items
        result = await (
            self.supabase.table(self.TABLE_NAME)
            .select("*", count="exact")
            .eq("household_id", str(household_id))
            .order("name")
            .range(offset, offset + per_page - 1)
            .execute()
        )

        items = [PantryItem.model_validate(row) for row in result.data]
        total = result.count or 0

        return items, total

    async def create(self, household_id: UUID, dto: CreatePantryItemDTO) -> PantryItem:
        """Create a new pantry item.

        Args:
            household_id: The household this item belongs to.
            dto: The item data.

        Returns:
            The created PantryItem.
        """
        now = datetime.utcnow()
        data = {
            "id": str(uuid4()),
            "household_id": str(household_id),
            "name": dto.name,
            "quantity": dto.quantity,
            "unit": dto.unit,
            "location": dto.location.value,
            "expiry_date": dto.expiry_date.isoformat() if dto.expiry_date else None,
            "notes": dto.notes,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        result = await (
            self.supabase.table(self.TABLE_NAME).insert(data).execute()
        )

        return PantryItem.model_validate(result.data[0])

    async def update(
        self,
        item_id: UUID,
        household_id: UUID,
        dto: UpdatePantryItemDTO,
    ) -> PantryItem | None:
        """Update an existing pantry item.

        Args:
            item_id: The item to update.
            household_id: The household (for RLS).
            dto: The fields to update.

        Returns:
            Updated PantryItem if found, None otherwise.
        """
        # Build update data from non-None fields
        update_data: dict = {"updated_at": datetime.utcnow().isoformat()}

        if dto.name is not None:
            update_data["name"] = dto.name
        if dto.quantity is not None:
            update_data["quantity"] = dto.quantity
        if dto.unit is not None:
            update_data["unit"] = dto.unit
        if dto.location is not None:
            update_data["location"] = dto.location.value
        if dto.expiry_date is not None:
            update_data["expiry_date"] = dto.expiry_date.isoformat()
        if dto.notes is not None:
            update_data["notes"] = dto.notes

        result = await (
            self.supabase.table(self.TABLE_NAME)
            .update(update_data)
            .eq("id", str(item_id))
            .eq("household_id", str(household_id))
            .execute()
        )

        if result.data:
            return PantryItem.model_validate(result.data[0])
        return None

    async def delete(self, item_id: UUID, household_id: UUID) -> bool:
        """Delete a pantry item.

        Args:
            item_id: The item to delete.
            household_id: The household (for RLS).

        Returns:
            True if deleted, False if not found.
        """
        result = await (
            self.supabase.table(self.TABLE_NAME)
            .delete()
            .eq("id", str(item_id))
            .eq("household_id", str(household_id))
            .execute()
        )

        return len(result.data) > 0

    async def search_by_name(
        self,
        household_id: UUID,
        query: str,
        *,
        limit: int = 10,
    ) -> list[PantryItem]:
        """Search pantry items by name (fuzzy match).

        Args:
            household_id: The household to search in.
            query: The search query.
            limit: Max results to return.

        Returns:
            Matching PantryItems.
        """
        # Using ilike for case-insensitive partial matching
        # TODO: Upgrade to pg_trgm for better fuzzy matching
        result = await (
            self.supabase.table(self.TABLE_NAME)
            .select("*")
            .eq("household_id", str(household_id))
            .ilike("name", f"%{query}%")
            .limit(limit)
            .execute()
        )

        return [PantryItem.model_validate(row) for row in result.data]
