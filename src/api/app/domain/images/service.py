"""Image generation service. 🖼️

Service for generating recipe images using Google Gemini or mock images.
Supports both real API calls and mock mode for testing.

Fun fact: Professional food photographers use over 50 different props! 📸
"""

import base64
import logging
import os
from io import BytesIO
from typing import Protocol
from uuid import UUID

import httpx
from PIL import Image as PILImage

from src.api.app.domain.images.models import (
    GenerateImageRequest,
    GenerateImageResponse,
    ImageGenerationConfig,
)

logger = logging.getLogger(__name__)


class StorageClient(Protocol):
    """Protocol for storage operations."""

    async def upload(self, bucket: str, path: str, data: bytes, content_type: str) -> str:
        """Upload file and return public URL."""
        ...


class ImageGenerationService:
    """Service for generating recipe images. 🍕

    Uses Google Gemini for real generation or placeholder images for testing.
    Uploads results to Supabase storage and returns public URLs.
    """

    # Placeholder images for mock mode (various food types)
    MOCK_IMAGES = [
        "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800",  # Salad
        "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800",  # Pizza
        "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800",  # Veggies
        "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800",  # Plate
        "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=800",  # Meal
        "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=800",  # Pancakes
        "https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=800",  # Cake
        "https://images.unsplash.com/photo-1484723091739-30a097e8f929?w=800",  # Toast
        "https://images.unsplash.com/photo-1551782450-a2132b4ba21d?w=800",  # Burger
        "https://images.unsplash.com/photo-1529042410759-befb1204b468?w=800",  # Ramen
    ]

    def __init__(
        self,
        storage_client: StorageClient | None = None,
        google_api_key: str | None = None,
        use_mock: bool = False,
    ):
        """Initialize the image generation service.

        Args:
            storage_client: Client for uploading images to storage
            google_api_key: Google API key for Gemini
            use_mock: If True, use placeholder images instead of real generation
        """
        self.storage_client = storage_client
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        self.use_mock = use_mock or not self.google_api_key
        self.config = ImageGenerationConfig()

    def _build_prompt(self, request: GenerateImageRequest) -> str:
        """Build the image generation prompt. 📝"""
        base_prompt = f"A {self.config.style_prompt} of {request.title}"

        if request.description:
            base_prompt += f". {request.description}"

        if request.ingredients:
            # Include top 3-5 key ingredients for visual cues
            key_ingredients = request.ingredients[:5]
            base_prompt += f". Key ingredients visible: {', '.join(key_ingredients)}"

        # Style modifiers
        style_modifiers = {
            "professional": "studio lighting, clean white background edges",
            "rustic": "wooden table, warm tones, farmhouse style",
            "modern": "minimalist plating, geometric arrangement, sleek",
            "minimal": "simple composition, negative space, elegant",
        }

        style = request.style if request.style in style_modifiers else "professional"
        base_prompt += f". {style_modifiers[style]}"

        return base_prompt

    async def _generate_with_gemini(self, prompt: str) -> bytes | None:
        """Generate image using Google Gemini API. 🤖"""
        try:
            # Import Google Generative AI library
            import google.generativeai as genai

            genai.configure(api_key=self.google_api_key)

            # Use the image generation model
            model = genai.GenerativeModel(self.config.model)

            # Generate with image output
            response = await model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="image/png",
                ),
            )

            # Extract image bytes from response
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "inline_data") and part.inline_data:
                        return base64.b64decode(part.inline_data.data)

            logger.warning("No image data in Gemini response")
            return None

        except ImportError:
            logger.warning("google-generativeai not installed, using mock")
            return None
        except Exception as e:
            logger.error(f"Gemini image generation failed: {e}")
            return None

    async def _get_mock_image(self, recipe_id: str) -> str:
        """Get a deterministic mock image URL based on recipe ID. 🎭"""
        # Use recipe ID hash to consistently select same image
        index = hash(recipe_id) % len(self.MOCK_IMAGES)
        return self.MOCK_IMAGES[index]

    async def _download_and_resize(self, url: str) -> bytes | None:
        """Download and resize an image. 📐"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, follow_redirects=True, timeout=30)
                response.raise_for_status()

                # Resize to target dimensions
                img_file = PILImage.open(BytesIO(response.content))
                img_rgb = img_file.convert("RGB")
                img_resized = img_rgb.resize(
                    (self.config.width, self.config.height), PILImage.Resampling.LANCZOS
                )

                # Convert back to bytes
                buffer = BytesIO()
                img_resized.save(buffer, format="JPEG", quality=85)
                return buffer.getvalue()

        except Exception as e:
            logger.error(f"Failed to download/resize image: {e}")
            return None

    async def generate_image(
        self, recipe_id: UUID, request: GenerateImageRequest
    ) -> GenerateImageResponse:
        """Generate and store a recipe image. 🎨

        Args:
            recipe_id: The recipe to generate an image for
            request: Generation parameters

        Returns:
            Response with image URL or error
        """
        recipe_id_str = str(recipe_id)
        prompt = self._build_prompt(request)
        logger.info(f"Generating image for recipe {recipe_id_str}: {prompt[:100]}...")

        image_data: bytes | None = None
        image_url: str | None = None

        if self.use_mock:
            # Use mock image for testing
            mock_url = await self._get_mock_image(recipe_id_str)
            image_data = await self._download_and_resize(mock_url)

            if not image_data:
                # Fallback: just return the mock URL directly
                return GenerateImageResponse(
                    success=True,
                    image_url=mock_url,
                    message="Mock image generated (placeholder)",
                )
        else:
            # Use real Gemini generation
            image_data = await self._generate_with_gemini(prompt)

        if image_data and self.storage_client:
            # Upload to storage
            try:
                path = f"recipes/{recipe_id_str}/cover.jpg"
                image_url = await self.storage_client.upload(
                    bucket="recipe-images",
                    path=path,
                    data=image_data,
                    content_type="image/jpeg",
                )
                logger.info(f"Image uploaded: {image_url}")
            except Exception as e:
                logger.error(f"Failed to upload image: {e}")
                return GenerateImageResponse(
                    success=False,
                    error=f"Failed to upload image: {e}",
                )
        elif image_data:
            # No storage client, return base64 data URL for testing
            b64 = base64.b64encode(image_data).decode()
            image_url = f"data:image/jpeg;base64,{b64[:100]}..."  # Truncated for logging

            # For actual use, we'd return the full data URL or temp file
            # In mock mode without storage, return the mock URL
            if self.use_mock:
                image_url = await self._get_mock_image(recipe_id_str)
        elif self.use_mock:
            # Fallback for mock mode
            image_url = await self._get_mock_image(recipe_id_str)

        if image_url:
            return GenerateImageResponse(
                success=True,
                image_url=image_url,
                message="Image generated successfully",
            )

        return GenerateImageResponse(
            success=False,
            error="Failed to generate image",
        )


# Singleton for mock mode in development
_mock_service: ImageGenerationService | None = None


def get_mock_image_service() -> ImageGenerationService:
    """Get a mock image service for development/testing."""
    global _mock_service
    if _mock_service is None:
        _mock_service = ImageGenerationService(use_mock=True)
    return _mock_service
