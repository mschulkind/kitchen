"""Store Intelligence models. 🏪

DTOs for store aisle mapping and shopping optimization.

Fun fact: The average supermarket has about 40,000 products
arranged across 10-15 aisles! 🛒
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class StoreAisleMapping(BaseModel):
    """Mapping of an item keyword to a store aisle. 📍"""

    id: UUID
    store_id: UUID
    item_keyword: str = Field(
        ...,
        description="Keyword to match (e.g., 'milk', 'bread')",
    )
    aisle: str = Field(
        ...,
        description="Aisle location (e.g., 'Aisle 12', 'Produce')",
    )
    section: str | None = None  # "Left", "Right", "End Cap"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    last_verified: datetime | None = None


class Store(BaseModel):
    """A grocery store. 🏬"""

    id: UUID
    name: str
    address: str | None = None
    chain: str | None = None  # "Shaw's", "Whole Foods", etc.
    is_default: bool = False


class AisleConfig(BaseModel):
    """Store aisle ordering configuration. 📋

    Defines the optimal traversal order for a store.
    """

    store_id: UUID
    aisle_order: list[str] = Field(
        default_factory=list,
        description="Aisles in traversal order",
    )
    # Example: ["Produce", "Bakery", "Deli", "Aisle 1", "Aisle 2", ...]


class SortedShoppingItem(BaseModel):
    """A shopping item with aisle information. 🛒"""

    item_id: UUID
    name: str
    quantity: float | None = None
    unit: str | None = None
    aisle: str = "Unknown"
    aisle_order: int = 999  # For sorting
    section: str | None = None
    is_checked: bool = False


class SortedShoppingList(BaseModel):
    """Shopping list sorted by aisle order. 📋"""

    list_id: UUID
    store_id: UUID | None = None
    items: list[SortedShoppingItem]
    unknown_items: list[SortedShoppingItem] = Field(
        default_factory=list,
        description="Items with no known aisle",
    )
