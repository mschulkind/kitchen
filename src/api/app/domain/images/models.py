"""Image domain models (DTOs). 🖼️

Pydantic models for image generation data transfer.

Fun fact: The human brain processes images 60,000x faster than text! 👁️
"""

from pydantic import BaseModel, Field


class GenerateImageRequest(BaseModel):
    """Request to generate an image for a recipe. 📸"""

    title: str = Field(description="Recipe title for prompt")
    description: str | None = Field(default=None, description="Recipe description")
    ingredients: list[str] | None = Field(
        default=None, description="Key ingredients for visual cues"
    )
    style: str = Field(
        default="professional",
        description="Image style: professional, rustic, modern, minimal",
    )


class GenerateImageResponse(BaseModel):
    """Response from image generation. ✅"""

    success: bool
    image_url: str | None = None
    message: str | None = None
    error: str | None = None


class ImageGenerationConfig(BaseModel):
    """Configuration for image generation. ⚙️"""

    model: str = Field(default="gemini-2.0-flash-preview-image-generation")
    width: int = Field(default=1024, ge=256, le=2048)
    height: int = Field(default=768, ge=256, le=2048)
    style_prompt: str = Field(
        default="high-end professional food photography, overhead view, "
        "beautifully plated, natural lighting, bokeh background, "
        "4k resolution, appetizing colors, restaurant quality"
    )
