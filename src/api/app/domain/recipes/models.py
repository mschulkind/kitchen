"""Recipe domain models (DTOs). 📖

Pydantic models for recipe data transfer.
Includes both recipe metadata and parsed ingredients.

Fun fact: The word "recipe" comes from Latin "recipere" meaning "to receive"! 📜
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ParsedIngredient(BaseModel):
    """A parsed ingredient extracted from raw text. 🧅

    Represents the structured data extracted from strings like
    "1 large onion, diced" -> {qty: 1, unit: "count", item: "onion", notes: "large, diced"}
    """

    raw_text: str
    quantity: float | None = None
    unit: str | None = None
    item_name: str
    notes: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class RecipeIngredient(BaseModel):
    """A stored recipe ingredient with full metadata. 🥕"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recipe_id: UUID
    raw_text: str
    quantity: float | None
    unit: str | None
    item_name: str
    notes: str | None
    section: str | None
    sort_order: int
    confidence: float | None
    created_at: datetime


class Recipe(BaseModel):
    """A stored recipe with all metadata. 📋"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    household_id: UUID
    title: str
    source_url: str | None
    source_domain: str | None
    servings: int | None
    prep_time_minutes: int | None
    cook_time_minutes: int | None
    total_time_minutes: int | None
    description: str | None
    instructions: list[str] | None
    tags: list[str] | None
    is_parsed: bool
    created_at: datetime
    updated_at: datetime

    # Related ingredients (populated by joins)
    ingredients: list[RecipeIngredient] | None = None


class CreateRecipeDTO(BaseModel):
    """Data for creating a new recipe. ➕"""

    title: str = Field(min_length=1, max_length=500)
    source_url: str | None = None
    servings: int | None = Field(default=None, ge=1, le=100)
    prep_time_minutes: int | None = Field(default=None, ge=0)
    cook_time_minutes: int | None = Field(default=None, ge=0)
    description: str | None = None
    instructions: list[str] | None = None
    tags: list[str] | None = None
    raw_markdown: str | None = None  # Optional per D12


class UpdateRecipeDTO(BaseModel):
    """Data for updating a recipe. ✏️"""

    title: str | None = Field(default=None, min_length=1, max_length=500)
    servings: int | None = Field(default=None, ge=1, le=100)
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    description: str | None = None
    instructions: list[str] | None = None
    tags: list[str] | None = None


class IngestRecipeRequest(BaseModel):
    """Request to ingest a recipe from URL. 🌐"""

    url: str = Field(description="URL of the recipe to scrape")
    parse_ingredients: bool = Field(
        default=True,
        description="Whether to parse ingredients after ingestion",
    )


class IngestRecipeResponse(BaseModel):
    """Response from recipe ingestion. ✅"""

    recipe: Recipe
    ingredients_parsed: int
    source: str  # "firecrawl" | "beautifulsoup" | "manual"
