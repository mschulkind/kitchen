"""Vision Service - Image analysis for inventory. 📸

Processes images using LLM vision capabilities to detect
food items and quantities.

Fun fact: GPT-4V can identify over 10,000 different food items! 🍕
"""

import time
from typing import Protocol
from uuid import UUID, uuid4

from src.api.app.domain.vision.models import (
    AnalyzeImageRequest,
    AnalyzeImageResponse,
    DetectedItem,
    ScanStatus,
)


class LLMVisionAdapter(Protocol):
    """Protocol for LLM vision providers.

    Supports multiple backends (GPT-4o, Gemini 1.5 Pro, Claude 3).
    """

    async def analyze_image(
        self,
        image_url: str,
        prompt: str,
    ) -> list[DetectedItem]:
        """Analyze an image and return detected items."""
        ...


class MockLLMVisionAdapter:
    """Mock adapter for testing without API calls. 🧪

    Returns realistic sample data for development.
    """

    async def analyze_image(
        self,
        image_url: str,
        prompt: str,
    ) -> list[DetectedItem]:
        """Return mock detected items.

        In production, this would call GPT-4o or Gemini Vision.
        """
        # Simulate some processing time
        await self._simulate_delay()

        # Return sample detections based on common fridge/pantry items
        return [
            DetectedItem(
                name="Milk",
                quantity=0.5,
                unit="gallon",
                confidence=0.92,
                location_hint="Fridge",
            ),
            DetectedItem(
                name="Eggs",
                quantity=12,
                unit="count",
                confidence=0.88,
                location_hint="Fridge",
            ),
            DetectedItem(
                name="Butter",
                quantity=1,
                unit="stick",
                confidence=0.85,
                location_hint="Fridge",
            ),
            DetectedItem(
                name="Cheddar Cheese",
                quantity=8,
                unit="oz",
                confidence=0.78,
                location_hint="Fridge",
            ),
        ]

    async def _simulate_delay(self) -> None:
        """Simulate API delay."""
        import asyncio

        await asyncio.sleep(0.1)  # 100ms simulated delay


# The vision prompt template
VISION_PROMPT = """Analyze this image of food items and identify each item.

For each item you can see, provide:
- name: The common name of the food item
- quantity: Estimated quantity (number)
- unit: The unit of measurement (e.g., "count", "lbs", "oz", "gallon")
- confidence: Your confidence level 0.0-1.0

Return as JSON array. Example:
[
  {{"name": "Milk", "quantity": 1, "unit": "gallon", "confidence": 0.9}},
  {{"name": "Eggs", "quantity": 12, "unit": "count", "confidence": 0.85}}
]

{context}

Image items:"""


class VisionService:
    """Service for visual inventory scanning. 📷

    Orchestrates image upload, analysis, and item confirmation.

    Example:
        >>> service = VisionService()
        >>> result = await service.analyze_image(request)
        >>> print(f"Found {len(result.detected_items)} items")
    """

    def __init__(
        self,
        adapter: LLMVisionAdapter | None = None,
    ) -> None:
        """Initialize the vision service.

        Args:
            adapter: The LLM vision adapter to use. Defaults to mock.
        """
        self.adapter = adapter or MockLLMVisionAdapter()

    async def analyze_image(
        self,
        household_id: UUID,
        request: AnalyzeImageRequest,
    ) -> AnalyzeImageResponse:
        """Analyze an image for food items.

        Args:
            household_id: The household making the request.
            request: The analysis request with image URL.

        Returns:
            AnalyzeImageResponse with detected items.
        """
        start_time = time.time()

        # Build prompt with context
        context = ""
        if request.context:
            context = f"Context: {request.context}"

        prompt = VISION_PROMPT.format(context=context)

        try:
            # Call the vision adapter
            detected_items = await self.adapter.analyze_image(
                request.image_url,
                prompt,
            )

            processing_time = int((time.time() - start_time) * 1000)

            return AnalyzeImageResponse(
                scan_id=uuid4(),
                status=ScanStatus.COMPLETED,
                detected_items=detected_items,
                processing_time_ms=processing_time,
                model_used="mock" if isinstance(self.adapter, MockLLMVisionAdapter) else "llm",
            )

        except Exception as e:
            return AnalyzeImageResponse(
                scan_id=uuid4(),
                status=ScanStatus.FAILED,
                detected_items=[],
                processing_time_ms=int((time.time() - start_time) * 1000),
                model_used=None,
                error_message=f"Error analyzing image: {e!s}",
            )

    async def confirm_and_create_items(
        self,
        household_id: UUID,
        items: list[DetectedItem],
        location: str = "pantry",
    ) -> list[UUID]:
        """Confirm detected items and add to pantry.

        This is called after user reviews and edits the detected items.

        Args:
            household_id: The household's ID.
            items: Confirmed/edited items to add.
            location: Storage location for all items.

        Returns:
            List of created item IDs.
        """
        # In a real implementation, this would call PantryService
        # For now, return mock IDs
        return [uuid4() for _ in items]


class OpenAIVisionAdapter:
    """OpenAI GPT-4o Vision adapter. 🤖

    Uses GPT-4o or GPT-4-turbo for image analysis.
    """

    def __init__(self, api_key: str) -> None:
        """Initialize with API key."""
        self.api_key = api_key

    async def analyze_image(
        self,
        image_url: str,
        prompt: str,
    ) -> list[DetectedItem]:
        """Analyze image using OpenAI Vision API."""
        import json

        try:
            import openai
        except ImportError as err:
            raise ImportError("openai package required: pip install openai") from err

        client = openai.AsyncOpenAI(api_key=self.api_key)

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            max_tokens=1000,
        )

        # Parse response
        content = response.choices[0].message.content or "[]"

        # Extract JSON from response
        try:
            # Try to find JSON array in response
            import re

            json_match = re.search(r"\[.*\]", content, re.DOTALL)
            if json_match:
                items_data = json.loads(json_match.group())
                return [DetectedItem(**item) for item in items_data]
        except (json.JSONDecodeError, ValueError):
            pass

        return []


class GeminiVisionAdapter:
    """Google Gemini Vision adapter. 🔮

    Uses Gemini 1.5 Pro for image analysis (recommended for vision).
    """

    def __init__(self, api_key: str) -> None:
        """Initialize with API key."""
        self.api_key = api_key

    async def analyze_image(
        self,
        image_url: str,
        prompt: str,
    ) -> list[DetectedItem]:
        """Analyze image using Gemini Vision API."""
        import json

        try:
            import google.generativeai as genai
        except ImportError as err:
            raise ImportError("google-generativeai package required") from err

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel("gemini-1.5-pro")

        # Gemini can accept URLs directly
        response = await model.generate_content_async(
            [
                prompt,
                {"type": "image", "source": {"url": image_url}},
            ]
        )

        content = response.text or "[]"

        try:
            import re

            json_match = re.search(r"\[.*\]", content, re.DOTALL)
            if json_match:
                items_data = json.loads(json_match.group())
                return [DetectedItem(**item) for item in items_data]
        except (json.JSONDecodeError, ValueError):
            pass

        return []
