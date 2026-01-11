"""Planner models - Meal plan generation DTOs. 📅

Pydantic models for the "Choose Your Own Adventure" planner.

Fun fact: Planning meals for the week can save up to 4 hours of cooking time! ⏰
"""

from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class PlanStatus(str, Enum):
    """Status of a meal plan. 📊"""

    DRAFT = "draft"  # Still being configured
    ACTIVE = "active"  # User's current plan
    COMPLETED = "completed"  # Week finished
    ARCHIVED = "archived"  # Old plan kept for reference


class MealType(str, Enum):
    """Type of meal in a day. 🍽️"""

    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class RecipeStub(BaseModel):
    """Minimal recipe info for plan previews. 📖

    Used in plan options before full selection.
    """

    id: UUID | None = None  # None if not yet in DB (LLM-generated)
    title: str
    prep_time_minutes: int | None = None
    inventory_match_percent: float | None = None  # How much user has
    tags: list[str] = Field(default_factory=list)


class MealSlot(BaseModel):
    """A single meal slot in a plan. 🍳

    Represents one meal on one day.
    """

    id: UUID
    plan_id: UUID
    date: date
    meal_type: MealType
    recipe_id: UUID | None = None
    recipe_title: str | None = None
    is_locked: bool = False  # User locked this slot (Phase 6)
    notes: str | None = None
    servings: int = 2


class PlanOption(BaseModel):
    """A proposed plan option for user selection. 🎲

    The "Choose Your Own Adventure" card.
    """

    id: str  # Temporary ID before selection
    title: str  # e.g., "Efficiency Week"
    theme: str  # e.g., "Maximize pantry usage"
    description: str  # Engaging pitch text
    preview_meals: list[RecipeStub]  # 3-4 preview recipes
    estimated_shopping_items: int | None = None
    inventory_usage_percent: float | None = None
    difficulty: str | None = None  # "Easy", "Moderate", "Adventurous"


class MealPlan(BaseModel):
    """A complete meal plan. 📋

    Contains all meal slots for a date range.
    """

    id: UUID
    household_id: UUID
    name: str
    start_date: date
    end_date: date
    status: PlanStatus = PlanStatus.DRAFT
    selected_option_id: str | None = None
    constraints: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    # Slots (populated by joins)
    slots: list[MealSlot] | None = None


class CreatePlanRequest(BaseModel):
    """Request to generate plan options. 🎲

    User provides date range and constraints.
    """

    start_date: date
    end_date: date
    constraints: list[str] = Field(
        default_factory=list,
        description="Dietary restrictions, preferences, etc.",
    )
    num_options: int = Field(default=3, ge=1, le=5)
    meal_types: list[MealType] = Field(
        default_factory=lambda: [MealType.DINNER],
        description="Which meals to plan",
    )


class PlanOptionsResponse(BaseModel):
    """Response with generated plan options. 🎲"""

    options: list[PlanOption]
    generation_time_ms: int | None = None


class SelectOptionRequest(BaseModel):
    """Request to select a plan option. ✅"""

    option_id: str


class PlanSummary(BaseModel):
    """Summary of a meal plan for list views. 📊"""

    id: UUID
    name: str
    start_date: date
    end_date: date
    status: PlanStatus
    total_meals: int
    completed_meals: int
    created_at: datetime


class RecipeScore(BaseModel):
    """Score for a recipe in the context of the current inventory. 📊

    Used by the scorer to rank recipes.
    """

    recipe_id: UUID
    recipe_title: str
    inventory_match_percent: float  # % of ingredients user has
    spoilage_score: float  # Higher = uses expiring items
    freshness_score: float  # Higher = uses fresh produce
    total_score: float
    missing_items: list[str]


class ScoringCriteria(BaseModel):
    """Configuration for recipe scoring. ⚙️"""

    inventory_weight: float = Field(default=0.5, ge=0, le=1)
    spoilage_weight: float = Field(default=0.3, ge=0, le=1)
    freshness_weight: float = Field(default=0.2, ge=0, le=1)
    prefer_quick_meals: bool = False
    max_prep_time_minutes: int | None = None
