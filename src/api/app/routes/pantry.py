"""Pantry API routes. 🥫

REST endpoints for pantry item management.
Follows RESTful conventions with proper HTTP status codes.

Fun fact: The first REST API was described by Roy Fielding in 2000! 📚
"""

from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.app.db.session import get_supabase
from src.api.app.domain.pantry.models import (
    CreatePantryItemDTO,
    PantryItem,
    PantryItemList,
    UpdatePantryItemDTO,
)
from src.api.app.domain.pantry.repository import PantryRepository
from src.api.app.domain.pantry.service import PantryItemNotFoundError, PantryService

router = APIRouter(prefix="/pantry", tags=["Pantry 🥫"])


async def get_pantry_service() -> AsyncGenerator[PantryService]:
    """Dependency injection for PantryService."""
    async with get_supabase() as supabase:
        repository = PantryRepository(supabase)
        yield PantryService(repository)


# TODO: Replace with actual auth - get from JWT token
async def get_current_household_id() -> UUID:
    """Get the current user's household ID.

    This is a placeholder until auth is implemented.
    In production, this would decode the JWT and fetch the household.
    """
    # Default household for development
    return UUID("a0000000-0000-0000-0000-000000000001")


@router.get("", response_model=PantryItemList)
async def list_pantry_items(
    service: Annotated[PantryService, Depends(get_pantry_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 50,
) -> PantryItemList:
    """List all pantry items for the current household.

    Supports pagination via `page` and `per_page` parameters.
    """
    return await service.list_items(household_id, page=page, per_page=per_page)


@router.get("/search")
async def search_pantry_items(
    service: Annotated[PantryService, Depends(get_pantry_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
    q: Annotated[str, Query(min_length=1, max_length=100)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[PantryItem]:
    """Search pantry items by name. 🔍

    Uses fuzzy matching to find items.
    """
    return await service.search_items(household_id, q, limit=limit)


@router.get("/{item_id}", response_model=PantryItem)
async def get_pantry_item(
    item_id: UUID,
    service: Annotated[PantryService, Depends(get_pantry_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> PantryItem:
    """Get a single pantry item by ID."""
    try:
        return await service.get_item(item_id, household_id)
    except PantryItemNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.post("", response_model=PantryItem, status_code=status.HTTP_201_CREATED)
async def create_pantry_item(
    dto: CreatePantryItemDTO,
    service: Annotated[PantryService, Depends(get_pantry_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> PantryItem:
    """Create a new pantry item. ➕"""
    return await service.create_item(household_id, dto)


@router.patch("/{item_id}", response_model=PantryItem)
async def update_pantry_item(
    item_id: UUID,
    dto: UpdatePantryItemDTO,
    service: Annotated[PantryService, Depends(get_pantry_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> PantryItem:
    """Update an existing pantry item. ✏️

    Only provided fields will be updated.
    """
    try:
        return await service.update_item(item_id, household_id, dto)
    except PantryItemNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pantry_item(
    item_id: UUID,
    service: Annotated[PantryService, Depends(get_pantry_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> None:
    """Delete a pantry item. 🗑️"""
    try:
        await service.delete_item(item_id, household_id)
    except PantryItemNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.post("/confirm", response_model=PantryItem, status_code=status.HTTP_201_CREATED)
async def confirm_possession(
    item_name: Annotated[str, Query(min_length=1, max_length=255)],
    service: Annotated[PantryService, Depends(get_pantry_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
    unit: str = "count",
    quantity: float = 1.0,
) -> PantryItem:
    """Confirm possession of an item (Lazy Discovery). 🔍

    Used during recipe verification to add items to the pantry
    when the user confirms they have something.

    See Decision D13: Lazy Discovery.
    """
    return await service.confirm_possession(
        household_id,
        item_name,
        unit=unit,
        quantity=quantity,
    )
