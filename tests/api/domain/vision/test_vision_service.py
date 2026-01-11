"""Vision service tests. 📸"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.api.app.domain.vision.models import (
    AnalyzeImageRequest,
    DetectedItem,
    ScanStatus,
)
from src.api.app.domain.vision.service import (
    VISION_PROMPT,
    MockLLMVisionAdapter,
    VisionService,
)


class TestDetectedItem:
    """Tests for DetectedItem model."""

    def test_create_basic_item(self):
        """Test creating a detected item."""
        item = DetectedItem(name="Milk", quantity=1, unit="gallon")
        assert item.name == "Milk"
        assert item.quantity == 1
        assert item.unit == "gallon"
        assert item.confidence == 0.5  # Default

    def test_confidence_bounds(self):
        """Test confidence is bounded 0-1."""
        item = DetectedItem(name="Test", confidence=0.95)
        assert item.confidence == 0.95

    def test_optional_fields(self):
        """Test optional fields work."""
        item = DetectedItem(
            name="Apple",
            quantity=3,
            unit="count",
            confidence=0.9,
            location_hint="Counter",
            notes="Red apples",
        )
        assert item.location_hint == "Counter"
        assert item.notes == "Red apples"


class TestMockVisionAdapter:
    """Tests for mock vision adapter."""

    @pytest.mark.asyncio
    async def test_returns_items(self):
        """Test mock returns sample items."""
        adapter = MockLLMVisionAdapter()
        items = await adapter.analyze_image(
            "https://example.com/image.jpg",
            "Analyze this image",
        )
        assert len(items) > 0
        assert all(isinstance(item, DetectedItem) for item in items)

    @pytest.mark.asyncio
    async def test_items_have_required_fields(self):
        """Test all returned items have names."""
        adapter = MockLLMVisionAdapter()
        items = await adapter.analyze_image("https://example.com/image.jpg", "")
        for item in items:
            assert item.name
            assert item.confidence > 0


class TestVisionService:
    """Tests for VisionService."""

    @pytest.fixture
    def service(self) -> VisionService:
        """Create service with mock adapter."""
        return VisionService(adapter=MockLLMVisionAdapter())

    @pytest.fixture
    def household_id(self):
        """Sample household ID."""
        return uuid4()

    @pytest.mark.asyncio
    async def test_analyze_image_success(self, service: VisionService, household_id):
        """Test successful image analysis."""
        request = AnalyzeImageRequest(
            image_url="https://example.com/fridge.jpg"
        )

        result = await service.analyze_image(household_id, request)

        assert result.status == ScanStatus.COMPLETED
        assert len(result.detected_items) > 0
        assert result.processing_time_ms is not None
        assert result.scan_id is not None

    @pytest.mark.asyncio
    async def test_analyze_with_context(self, service: VisionService, household_id):
        """Test analysis with context."""
        request = AnalyzeImageRequest(
            image_url="https://example.com/pantry.jpg",
            context="This is my pantry shelf",
        )

        result = await service.analyze_image(household_id, request)

        assert result.status == ScanStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_confirm_items_returns_ids(self, service: VisionService, household_id):
        """Test confirming items creates entries."""
        items = [
            DetectedItem(name="Milk", quantity=1, unit="gallon"),
            DetectedItem(name="Eggs", quantity=12, unit="count"),
        ]

        created_ids = await service.confirm_and_create_items(
            household_id,
            items,
            location="fridge",
        )

        assert len(created_ids) == 2

    @pytest.mark.asyncio
    async def test_analyze_returns_model_info(self, service: VisionService, household_id):
        """Test model info is included in response."""
        request = AnalyzeImageRequest(image_url="https://example.com/img.jpg")
        result = await service.analyze_image(household_id, request)

        assert result.model_used == "mock"

class TestVisionPromptValidation:
    """Phase 4A Tests - Prompt Validation. 📋

    Tests that the prompt construction is correct.
    """

    def test_prompt_contains_json_instruction(self):
        """Phase 4 test: Prompt instructs LLM to return JSON.

        Input: VisionService.analyze(image_url)
        Assert: Prompt contains "Return a JSON array"
        """
        assert "JSON" in VISION_PROMPT
        assert "Return as JSON array" in VISION_PROMPT

    def test_prompt_specifies_item_fields(self):
        """Prompt specifies required item fields."""
        assert "name" in VISION_PROMPT.lower()
        assert "quantity" in VISION_PROMPT.lower()
        assert "unit" in VISION_PROMPT.lower()
        assert "confidence" in VISION_PROMPT.lower()

    def test_prompt_has_example(self):
        """Prompt includes example JSON for LLM to follow."""
        assert "example" in VISION_PROMPT.lower()
        assert '"name":' in VISION_PROMPT


class TestVisionResponseParsing:
    """Phase 4A Tests - Response Parsing. 🔍

    Tests that LLM responses are parsed correctly.
    """

    @pytest.mark.asyncio
    async def test_parse_valid_items(self):
        """Phase 4 test: Mock LLM returns valid items.

        Input: Mock LLM returns [{"name": "Apple", "qty": 3}]
        Assert: Service parses into valid PantryCandidate objects.
        """
        mock_adapter = AsyncMock()
        mock_adapter.analyze_image.return_value = [
            DetectedItem(name="Apple", quantity=3, unit="count", confidence=0.9),
            DetectedItem(name="Orange", quantity=2, unit="count", confidence=0.85),
        ]

        service = VisionService(adapter=mock_adapter)
        result = await service.analyze_image(
            uuid4(),
            AnalyzeImageRequest(image_url="https://example.com/fruit.jpg"),
        )

        assert result.status == ScanStatus.COMPLETED
        assert len(result.detected_items) == 2
        assert result.detected_items[0].name == "Apple"
        assert result.detected_items[0].quantity == 3

    @pytest.mark.asyncio
    async def test_parse_empty_response(self):
        """Empty list from LLM is handled gracefully."""
        mock_adapter = AsyncMock()
        mock_adapter.analyze_image.return_value = []

        service = VisionService(adapter=mock_adapter)
        result = await service.analyze_image(
            uuid4(),
            AnalyzeImageRequest(image_url="https://example.com/empty.jpg"),
        )

        assert result.status == ScanStatus.COMPLETED
        assert len(result.detected_items) == 0


class TestVisionErrorHandling:
    """Phase 4A Tests - Error Handling. ⚠️

    Tests graceful failure modes.
    """

    @pytest.mark.asyncio
    async def test_adapter_exception_handled(self):
        """Phase 4 test: LLM errors are handled gracefully.

        Input: Mock LLM raises exception
        Assert: Service returns error status (not crash)
        """
        mock_adapter = AsyncMock()
        mock_adapter.analyze_image.side_effect = Exception("LLM API Error")

        service = VisionService(adapter=mock_adapter)
        result = await service.analyze_image(
            uuid4(),
            AnalyzeImageRequest(image_url="https://example.com/image.jpg"),
        )

        # Should return error status, not crash
        assert result.status == ScanStatus.FAILED
        assert result.error_message is not None
        assert "error" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_processing_time_recorded(self):
        """Processing time is always recorded."""
        mock_adapter = AsyncMock()
        mock_adapter.analyze_image.return_value = [
            DetectedItem(name="Test", quantity=1)
        ]

        service = VisionService(adapter=mock_adapter)
        result = await service.analyze_image(
            uuid4(),
            AnalyzeImageRequest(image_url="https://example.com/image.jpg"),
        )

        assert result.processing_time_ms is not None
        assert result.processing_time_ms >= 0
