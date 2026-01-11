"""Planning domain models (DTOs). 🧮

Pydantic models for the Delta Engine - comparing recipes to inventory.

Fun fact: The average person throws away 25% of purchased groceries! 
The Delta Engine helps reduce waste by calculating exactly what's needed. 🌿
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DeltaStatus(str, Enum):
    """Status of an ingredient comparison. 📊"""

    HAS_ENOUGH = "has_enough"  # Inventory covers requirement
    PARTIAL = "partial"  # Have some, need more
    MISSING = "missing"  # Don't have any
    ASSUMED = "assumed"  # Assumed to have (staples like salt)
    UNIT_MISMATCH = "unit_mismatch"  # Can't compare (g vs cups, no density)


class DeltaItem(BaseModel):
    """Result of comparing one ingredient against inventory. 🔍

    Represents the "delta" between what a recipe needs and what's available.
    """

    item_name: str
    recipe_quantity: float | None
    recipe_unit: str | None
    inventory_quantity: float | None = None
    inventory_unit: str | None = None
    delta_quantity: float | None = None  # How much to buy (positive = need more)
    delta_unit: str | None = None
    status: DeltaStatus
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    notes: str | None = None
    matched_pantry_item_id: UUID | None = None  # ID of matched inventory item


class ComparisonResult(BaseModel):
    """Complete result of comparing a recipe (or plan) to inventory. 📋

    Contains categorized lists for easy UI rendering.
    """

    # Items user definitely has enough of
    have_enough: list[DeltaItem] = Field(default_factory=list)

    # Items user has partially (need to buy more)
    partial: list[DeltaItem] = Field(default_factory=list)

    # Items user doesn't have at all
    missing: list[DeltaItem] = Field(default_factory=list)

    # Items we assume user has (staples like salt, pepper)
    assumptions: list[DeltaItem] = Field(default_factory=list)

    # Items we couldn't compare (unit mismatch)
    unresolved: list[DeltaItem] = Field(default_factory=list)

    # Metadata
    recipe_id: UUID | None = None
    recipe_title: str | None = None
    comparison_time: datetime = Field(default_factory=datetime.utcnow)
    total_ingredients: int = 0

    @property
    def needs_shopping(self) -> bool:
        """Check if any shopping is needed."""
        return len(self.partial) > 0 or len(self.missing) > 0

    @property
    def shopping_list_items(self) -> list[DeltaItem]:
        """Get all items that need to be purchased."""
        return self.partial + self.missing

    @property
    def can_cook_now(self) -> bool:
        """Check if user can cook this recipe right now."""
        return not self.needs_shopping and len(self.unresolved) == 0


class VerificationRequest(BaseModel):
    """Request to verify ingredient assumptions. ✅

    User confirms which assumed items they actually have.
    """

    recipe_id: UUID
    confirmed_items: list[str] = Field(
        default_factory=list,
        description="Items user confirms they have",
    )
    missing_items: list[str] = Field(
        default_factory=list,
        description="Items user says they DON'T have",
    )


class VerificationResponse(BaseModel):
    """Response after verification with updated comparison. 📊"""

    # Updated comparison result
    result: ComparisonResult

    # Items added to pantry via Lazy Discovery (D13)
    items_added_to_pantry: list[str] = Field(default_factory=list)

    # Final shopping list after verification
    final_shopping_list: list[DeltaItem] = Field(default_factory=list)
