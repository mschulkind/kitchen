"""Shopping domain models (DTOs). 🛒

Pydantic models for the Shopping List feature.

Fun fact: The average American makes 1.6 trips to the grocery store per week! 🛍️
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ShoppingItemStatus(str, Enum):
    """Status of a shopping list item. ✅"""

    PENDING = "pending"  # Not yet purchased
    CHECKED = "checked"  # Marked as purchased
    SKIPPED = "skipped"  # User decided not to buy


class ShoppingItem(BaseModel):
    """A single item on the shopping list. 🥕

    Represents an item to purchase, with quantity and category.
    """

    id: UUID
    shopping_list_id: UUID
    name: str
    quantity: float | None = None
    unit: str | None = None
    category: str | None = None  # e.g., "Produce", "Dairy"
    aisle_hint: str | None = None  # e.g., "Aisle 4"
    status: ShoppingItemStatus = ShoppingItemStatus.PENDING
    notes: str | None = None
    recipe_source: str | None = None  # Which recipe needs this item
    created_at: datetime
    updated_at: datetime
    checked_at: datetime | None = None
    checked_by_user_id: UUID | None = None


class ShoppingList(BaseModel):
    """A shopping list with multiple items. 📋

    Supports realtime sync for multi-user shopping.
    """

    id: UUID
    household_id: UUID
    name: str = "Shopping List"
    status: str = "active"  # active, completed, archived
    plan_id: UUID | None = None  # If generated from a meal plan
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None

    # Items (populated by joins)
    items: list[ShoppingItem] | None = None


class CreateShoppingItemDTO(BaseModel):
    """Data for creating a new shopping item. ➕"""

    name: str = Field(min_length=1, max_length=255)
    quantity: float | None = Field(default=None, gt=0)
    unit: str | None = Field(default=None, max_length=50)
    category: str | None = Field(default=None, max_length=100)
    notes: str | None = None
    recipe_source: str | None = None


class UpdateShoppingItemDTO(BaseModel):
    """Data for updating a shopping item. ✏️"""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    quantity: float | None = None
    unit: str | None = None
    category: str | None = None
    status: ShoppingItemStatus | None = None
    notes: str | None = None


class CreateShoppingListDTO(BaseModel):
    """Data for creating a new shopping list. ➕"""

    name: str = Field(default="Shopping List", max_length=255)
    plan_id: UUID | None = None


class ShoppingListSummary(BaseModel):
    """Summary of a shopping list for list views. 📊"""

    id: UUID
    name: str
    status: str
    total_items: int
    checked_items: int
    created_at: datetime

    @property
    def progress_percent(self) -> float:
        """Calculate completion percentage."""
        if self.total_items == 0:
            return 100.0
        return (self.checked_items / self.total_items) * 100


class GenerateListRequest(BaseModel):
    """Request to generate a shopping list from a plan. 🔄"""

    plan_id: UUID
    include_suggestions: bool = True  # Include "buy bulk" suggestions


class GenerateListResponse(BaseModel):
    """Response after generating a shopping list. ✅"""

    shopping_list: ShoppingList
    items_from_delta: int
    suggestions: list[str] = Field(default_factory=list)


class AggregatedItem(BaseModel):
    """An item aggregated from multiple recipes. 📦

    Used during shopping list generation to combine quantities.
    """

    name: str
    total_quantity: float | None = None
    unit: str | None = None
    sources: list[str] = Field(default_factory=list)  # Recipe names
    category: str | None = None
