"""Cooking domain models. 👨‍🍳

DTOs for cooking execution and context export.

Fun fact: Professional chefs spend up to 80% of their time on
"mise en place" (preparation) before actual cooking! 🔪
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class RecipeViewType(str, Enum):
    """Different ways to view a recipe. 📖"""

    STANDARD = "standard"  # Classic recipe format
    MISE_EN_PLACE = "mise_en_place"  # Checklist of prep tasks
    STEP_BY_STEP = "step_by_step"  # Large text, one step at a time
    INGREDIENT_FOCUS = "ingredient_focus"  # Grouped by ingredient
    TIMELINE = "timeline"  # For complex recipes with parallel tasks


class MiseEnPlaceItem(BaseModel):
    """A single prep task for mise en place view. ✅"""

    task: str  # e.g., "Dice 2 onions"
    ingredient: str
    is_completed: bool = False
    order: int = 0


class RecipeStep(BaseModel):
    """A cooking step for step-by-step view. 👨‍🍳"""

    number: int
    instruction: str
    duration_minutes: int | None = None
    timer_required: bool = False
    tips: list[str] = Field(default_factory=list)


class CookingContext(BaseModel):
    """Full context for AI cooking assistance. 🤖

    Contains all relevant info for a cooking session.
    """

    recipe_title: str
    recipe_source: str | None = None
    servings: int = 2
    ingredients: list[str]  # Formatted ingredient strings
    instructions: list[str]  # Step-by-step instructions
    available_ingredients: list[str]  # What user has
    missing_ingredients: list[str]  # What user needs
    substitution_hints: list[str] = Field(default_factory=list)
    user_preferences: list[str] = Field(default_factory=list)
    equipment_needed: list[str] = Field(default_factory=list)


class ContextExportRequest(BaseModel):
    """Request to export cooking context. 📤"""

    recipe_id: UUID
    include_inventory: bool = True
    include_substitutions: bool = True
    format: str = "markdown"  # "markdown", "text", "json"


class ContextExportResponse(BaseModel):
    """Exported context for copying. 📋"""

    content: str
    format: str
    character_count: int


class MarkCookedRequest(BaseModel):
    """Request to mark a recipe as cooked. ✅"""

    recipe_id: UUID
    servings_made: int = 2
    deduct_inventory: bool = True


class MarkCookedResponse(BaseModel):
    """Response after marking recipe cooked. 📊"""

    success: bool
    items_decremented: list[str]
    warnings: list[str] = Field(default_factory=list)


class CookingSession(BaseModel):
    """An active cooking session. 🍳"""

    id: UUID
    recipe_id: UUID
    recipe_title: str
    started_at: datetime
    current_step: int = 1
    total_steps: int
    mise_en_place_completed: bool = False
    servings: int = 2
