"""Shopping List API routes. 🛒

REST endpoints for shopping list management.
Supports realtime sync for multi-user shopping.

Fun fact: The average shopping trip takes 43 minutes! ⏱️
"""

from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from src.api.app.db.session import get_supabase
from src.api.app.domain.shopping.models import (
    CreateShoppingItemDTO,
    CreateShoppingListDTO,
    ShoppingItem,
    ShoppingList,
    ShoppingListSummary,
    UpdateShoppingItemDTO,
)
from src.api.app.domain.shopping.repository import ShoppingRepository
from src.api.app.domain.shopping.service import (
    ShoppingItemNotFoundError,
    ShoppingListNotFoundError,
    ShoppingService,
)
from src.api.app.domain.store.sorter import StoreSorter

router = APIRouter(prefix="/shopping", tags=["Shopping 🛒"])


async def get_shopping_service() -> AsyncGenerator[ShoppingService]:
    """Dependency injection for ShoppingService."""
    async with get_supabase() as supabase:
        repository = ShoppingRepository(supabase)
        yield ShoppingService(repository)


# TODO: Replace with actual auth - get from JWT token
async def get_current_household_id() -> UUID:
    """Get the current user's household ID."""
    return UUID("a0000000-0000-0000-0000-000000000001")


async def get_current_user_id() -> UUID:
    """Get the current user's ID."""
    return UUID("00000000-0000-0000-0000-000000000002")


class ClearCheckedResponse(BaseModel):
    """Response after clearing checked items."""

    deleted_count: int


# =========================================================================
# Shopping Lists
# =========================================================================


@router.get("/lists", response_model=list[ShoppingListSummary])
async def list_shopping_lists(
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
    include_completed: Annotated[bool, Query()] = False,
) -> list[ShoppingListSummary]:
    """List all shopping lists for the household.

    Returns summaries with item counts for efficiency.
    """
    return await service.list_all(household_id, include_completed=include_completed)


@router.get("/lists/active", response_model=ShoppingList | None)
async def get_active_list(
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> ShoppingList | None:
    """Get the current active shopping list.

    Returns None if no active list exists.
    """
    return await service.get_active_list(household_id)


@router.get("/lists/{list_id}", response_model=ShoppingList)
async def get_shopping_list(
    list_id: UUID,
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> ShoppingList:
    """Get a shopping list by ID with all items."""
    try:
        return await service.get_list(list_id, household_id)
    except ShoppingListNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shopping list {list_id} not found",
        ) from None


@router.post("/lists", response_model=ShoppingList, status_code=status.HTTP_201_CREATED)
async def create_shopping_list(
    dto: CreateShoppingListDTO,
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> ShoppingList:
    """Create a new shopping list."""
    return await service.create_list(household_id, dto)


@router.post("/lists/{list_id}/complete", response_model=ShoppingList)
async def complete_shopping_list(
    list_id: UUID,
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> ShoppingList:
    """Mark a shopping list as completed. ✅

    Typically called after a shopping trip.
    """
    try:
        return await service.complete_list(list_id, household_id)
    except ShoppingListNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shopping list {list_id} not found",
        ) from None


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(
    list_id: UUID,
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> None:
    """Delete a shopping list and all its items. 🗑️"""
    try:
        await service.delete_list(list_id, household_id)
    except ShoppingListNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shopping list {list_id} not found",
        ) from None


# =========================================================================
# Shopping Items
# =========================================================================


@router.post(
    "/lists/{list_id}/items",
    response_model=ShoppingItem,
    status_code=status.HTTP_201_CREATED,
)
async def add_shopping_item(
    list_id: UUID,
    dto: CreateShoppingItemDTO,
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> ShoppingItem:
    """Add an item to a shopping list. ➕"""
    try:
        return await service.add_item(list_id, household_id, dto)
    except ShoppingListNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shopping list {list_id} not found",
        ) from None


@router.patch("/lists/{list_id}/items/{item_id}", response_model=ShoppingItem)
async def update_shopping_item(
    list_id: UUID,
    item_id: UUID,
    dto: UpdateShoppingItemDTO,
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> ShoppingItem:
    """Update a shopping item. ✏️"""
    try:
        return await service.update_item(item_id, list_id, household_id, dto)
    except ShoppingListNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shopping list {list_id} not found",
        ) from None
    except ShoppingItemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shopping item {item_id} not found",
        ) from None


@router.post("/lists/{list_id}/items/{item_id}/check", response_model=ShoppingItem)
async def check_shopping_item(
    list_id: UUID,
    item_id: UUID,
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> ShoppingItem:
    """Mark an item as checked (purchased). ✅

    Syncs in realtime to other users viewing the list.
    """
    try:
        return await service.check_item(item_id, list_id, household_id, user_id)
    except ShoppingListNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shopping list {list_id} not found",
        ) from None
    except ShoppingItemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shopping item {item_id} not found",
        ) from None


@router.post("/lists/{list_id}/items/{item_id}/uncheck", response_model=ShoppingItem)
async def uncheck_shopping_item(
    list_id: UUID,
    item_id: UUID,
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> ShoppingItem:
    """Unmark an item (back to pending).

    Useful if something was checked by mistake.
    """
    try:
        return await service.uncheck_item(item_id, list_id, household_id)
    except ShoppingListNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shopping list {list_id} not found",
        ) from None
    except ShoppingItemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shopping item {item_id} not found",
        ) from None


@router.delete(
    "/lists/{list_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_shopping_item(
    list_id: UUID,
    item_id: UUID,
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> None:
    """Delete a shopping item. 🗑️"""
    try:
        await service.delete_item(item_id, list_id, household_id)
    except ShoppingListNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shopping list {list_id} not found",
        ) from None
    except ShoppingItemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shopping item {item_id} not found",
        ) from None


@router.post("/lists/{list_id}/clear-checked", response_model=ClearCheckedResponse)
async def clear_checked_items(
    list_id: UUID,
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> ClearCheckedResponse:
    """Remove all checked items from a list. 🧹

    Useful after a shopping trip to clean up the list.
    """
    try:
        deleted = await service.clear_checked(list_id, household_id)
        return ClearCheckedResponse(deleted_count=deleted)
    except ShoppingListNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shopping list {list_id} not found",
        ) from None


# =========================================================================
# Store Sorting
# =========================================================================


@router.get("/lists/{list_id}/sorted")
async def get_sorted_shopping_list(
    list_id: UUID,
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> dict:
    """Get shopping list sorted by store aisle. 🏪

    Uses the StoreSorter to group items by aisle for efficient shopping.
    """
    try:
        shopping_list = await service.get_list(list_id, household_id)
    except ShoppingListNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shopping list {list_id} not found",
        ) from None

    sorter = StoreSorter()
    sorted_list = sorter.sort_list(shopping_list.items, list_id)
    summary = sorter.get_aisle_summary(sorted_list)

    return {
        "list_id": str(list_id),
        "aisles": [
            {
                "name": aisle,
                "items": [
                    {
                        "id": str(item.item_id),
                        "name": item.name,
                        "quantity": item.quantity,
                        "unit": item.unit,
                        "checked": item.is_checked,
                    }
                    for item in sorted_list.items
                    if item.aisle == aisle
                ],
            }
            for aisle in dict.fromkeys(i.aisle for i in sorted_list.items)
        ],
        "unknown": [
            {
                "id": str(item.item_id),
                "name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "checked": item.is_checked,
            }
            for item in sorted_list.unknown_items
        ],
        "summary": summary,
    }
