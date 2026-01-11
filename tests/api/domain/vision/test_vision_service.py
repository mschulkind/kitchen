"""Vision service tests. 📸"""

from uuid import uuid4

import pytest

from src.api.app.domain.vision.models import (
    AnalyzeImageRequest,
    DetectedItem,
    ScanStatus,
)
from src.api.app.domain.vision.service import (
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
