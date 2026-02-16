"""Vision API routes. 📸

REST endpoints for visual inventory scanning.
Handles image analysis and item confirmation.

Fun fact: Computer vision has improved 100x in the last decade! 🚀
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.api.app.domain.pantry.models import PantryLocation
from src.api.app.domain.vision.models import (
    AnalyzeImageRequest,
    AnalyzeImageResponse,
    BatchCreateResult,
    ConfirmItemsRequest,
    ScanStatus,
)
from src.api.app.domain.vision.service import VisionService

router = APIRouter(prefix="/vision", tags=["Vision 📸"])


async def get_vision_service() -> VisionService:
    """Dependency injection for VisionService."""
    # In production, would configure with real adapter based on settings
    return VisionService()


# TODO: Replace with actual auth
async def get_current_household_id() -> UUID:
    """Get the current user's household ID."""
    return UUID("a0000000-0000-0000-0000-000000000001")


@router.post("/analyze", response_model=AnalyzeImageResponse)
async def analyze_image(
    request: AnalyzeImageRequest,
    service: Annotated[VisionService, Depends(get_vision_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> AnalyzeImageResponse:
    """Analyze an image for food items. 🔍

    Uploads an image URL and returns detected items.
    Items are candidates that need confirmation before adding to pantry.

    The image should be uploaded to Supabase Storage first.
    """
    result = await service.analyze_image(household_id, request)

    if result.status == ScanStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze image",
        )

    return result


@router.post("/confirm", response_model=BatchCreateResult)
async def confirm_items(
    request: ConfirmItemsRequest,
    service: Annotated[VisionService, Depends(get_vision_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> BatchCreateResult:
    """Confirm detected items and add to pantry. ✅

    Called after user reviews and potentially edits the detected items.
    Creates pantry items for each confirmed detection.
    """
    try:
        created_ids = await service.confirm_and_create_items(
            household_id,
            request.items,
            request.location,
        )

        return BatchCreateResult(
            created_count=len(created_ids),
            items_created=created_ids,
        )

    except Exception as e:
        return BatchCreateResult(
            created_count=0,
            items_created=[],
            errors=[str(e)],
        )


class QuickScanRequest(BaseModel):
    """Quick scan with context hint. 📷"""

    image_url: str
    location: PantryLocation = PantryLocation.FRIDGE


@router.post("/quick-scan", response_model=AnalyzeImageResponse)
async def quick_scan(
    request: QuickScanRequest,
    service: Annotated[VisionService, Depends(get_vision_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> AnalyzeImageResponse:
    """Quick scan with automatic location detection. ⚡

    Convenience endpoint that includes location context in the scan.
    """
    analyze_request = AnalyzeImageRequest(
        image_url=request.image_url,
        context=f"This is a photo of my {request.location.value}",
    )

    return await service.analyze_image(household_id, analyze_request)
