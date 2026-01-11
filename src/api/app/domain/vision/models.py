"""Vision domain models. 📸

DTOs for visual pantry scanning and image analysis.

Fun fact: The human eye can distinguish about 10 million different colors,
but AI vision models typically use only 3 color channels! 🎨
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ScanStatus(str, Enum):
    """Status of a vision scan. 📊"""

    PENDING = "pending"  # Image uploaded, not yet analyzed
    PROCESSING = "processing"  # Analysis in progress
    COMPLETED = "completed"  # Analysis done
    FAILED = "failed"  # Analysis failed


class DetectedItem(BaseModel):
    """A single item detected in an image. 🔍

    This is a candidate that needs user confirmation before
    being added to the pantry.
    """

    name: str = Field(..., min_length=1, max_length=255)
    quantity: float | None = None
    unit: str | None = None
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How confident the model is in this detection",
    )
    location_hint: str | None = None  # "Fridge", "Pantry", etc.
    notes: str | None = None


class VisionScan(BaseModel):
    """A complete vision scan record. 📷"""

    id: UUID
    household_id: UUID
    image_url: str
    status: ScanStatus
    detected_items: list[DetectedItem] = Field(default_factory=list)
    error_message: str | None = None
    created_at: datetime
    processed_at: datetime | None = None


class AnalyzeImageRequest(BaseModel):
    """Request to analyze an image. 📸"""

    image_url: str = Field(
        ...,
        description="URL to the image in Supabase Storage",
    )
    context: str | None = Field(
        default=None,
        description="Additional context (e.g., 'This is my fridge')",
    )


class AnalyzeImageResponse(BaseModel):
    """Response from image analysis. 🔍"""

    scan_id: UUID
    status: ScanStatus
    detected_items: list[DetectedItem]
    processing_time_ms: int | None = None
    model_used: str | None = None


class ConfirmItemsRequest(BaseModel):
    """Request to confirm detected items into pantry. ✅"""

    scan_id: UUID
    items: list[DetectedItem] = Field(
        ...,
        description="Items to add (may be modified from original detection)",
    )
    location: str = "pantry"  # Default storage location


class BatchCreateResult(BaseModel):
    """Result of batch creating pantry items. 📦"""

    created_count: int
    items_created: list[UUID]
    errors: list[str] = Field(default_factory=list)
