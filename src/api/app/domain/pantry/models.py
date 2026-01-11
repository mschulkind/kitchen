"""Pantry domain models (DTOs). 🥫

Pydantic models for data transfer between layers.
These are NOT database models - they are API contracts.
"""

from datetime import date, datetime
from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PantryLocation(str, Enum):
    """Storage location for pantry items. 📍

    Fun fact: The average American kitchen has 300+ items stored across
    these locations! 🏠
    """

    PANTRY = "pantry"
    FRIDGE = "fridge"
    FREEZER = "freezer"
    COUNTER = "counter"
    GARDEN = "garden"  # For fresh herbs and produce! 🌱


class PantryItem(BaseModel):
    """A single item in the household pantry. 🍎

    Represents stored food with quantity, location, and optional expiry tracking.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    household_id: UUID
    name: str
    quantity: float
    unit: str
    location: PantryLocation
    expiry_date: date | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class CreatePantryItemDTO(BaseModel):
    """Data for creating a new pantry item. ➕"""

    name: Annotated[str, Field(min_length=1, max_length=255)]
    quantity: Annotated[float, Field(gt=0, description="Must be positive")]
    unit: Annotated[str, Field(min_length=1, max_length=50)]
    location: PantryLocation = PantryLocation.PANTRY
    expiry_date: date | None = None
    notes: str | None = None


class UpdatePantryItemDTO(BaseModel):
    """Data for updating an existing pantry item. ✏️

    All fields are optional - only provided fields will be updated.
    """

    name: Annotated[str, Field(min_length=1, max_length=255)] | None = None
    quantity: Annotated[float, Field(gt=0)] | None = None
    unit: Annotated[str, Field(min_length=1, max_length=50)] | None = None
    location: PantryLocation | None = None
    expiry_date: date | None = None
    notes: str | None = None


class PantryItemList(BaseModel):
    """Paginated list of pantry items. 📋"""

    items: list[PantryItem]
    total: int
    page: int
    per_page: int
