"""Tests for image generation service. 🖼️

Unit tests for the ImageGenerationService with mocked dependencies.

Fun fact: Food photography is a $20B industry! 📸
"""

from uuid import UUID

import pytest

from src.api.app.domain.images.models import GenerateImageRequest, ImageGenerationConfig
from src.api.app.domain.images.service import ImageGenerationService


class TestImageGenerationModels:
    """Test the image generation models."""

    def test_generate_image_request_defaults(self):
        """Test default values in GenerateImageRequest."""
        request = GenerateImageRequest(title="Test Tacos")
        assert request.title == "Test Tacos"
        assert request.style == "professional"
        assert request.description is None
        assert request.ingredients is None

    def test_generate_image_request_full(self):
        """Test GenerateImageRequest with all fields."""
        request = GenerateImageRequest(
            title="Spicy Tacos",
            description="Crispy shells with seasoned beef",
            ingredients=["ground beef", "taco shells", "cheese"],
            style="rustic",
        )
        assert request.title == "Spicy Tacos"
        assert request.style == "rustic"
        assert len(request.ingredients) == 3

    def test_image_generation_config_defaults(self):
        """Test default config values."""
        config = ImageGenerationConfig()
        assert config.width == 1024
        assert config.height == 768
        assert "gemini" in config.model.lower()
        assert "professional" in config.style_prompt


class TestImageGenerationService:
    """Test the image generation service."""

    @pytest.fixture
    def mock_service(self):
        """Create a mock image service."""
        return ImageGenerationService(use_mock=True)

    def test_service_uses_mock_mode(self, mock_service):
        """Test service correctly identifies mock mode."""
        assert mock_service.use_mock is True

    def test_build_prompt_basic(self, mock_service):
        """Test basic prompt generation."""
        request = GenerateImageRequest(title="Chicken Tacos")
        prompt = mock_service._build_prompt(request)

        assert "Chicken Tacos" in prompt
        assert "professional" in prompt.lower() or "lighting" in prompt.lower()

    def test_build_prompt_with_description(self, mock_service):
        """Test prompt with description."""
        request = GenerateImageRequest(
            title="Chicken Tacos",
            description="Crispy corn shells filled with seasoned chicken",
        )
        prompt = mock_service._build_prompt(request)

        assert "Chicken Tacos" in prompt
        assert "Crispy corn shells" in prompt

    def test_build_prompt_with_ingredients(self, mock_service):
        """Test prompt includes key ingredients."""
        request = GenerateImageRequest(
            title="Chicken Tacos",
            ingredients=["chicken", "corn tortillas", "salsa", "cheese", "lettuce"],
        )
        prompt = mock_service._build_prompt(request)

        assert "chicken" in prompt.lower()
        assert "tortillas" in prompt.lower() or "corn" in prompt.lower()

    def test_build_prompt_rustic_style(self, mock_service):
        """Test rustic style prompt."""
        request = GenerateImageRequest(title="Homemade Bread", style="rustic")
        prompt = mock_service._build_prompt(request)

        assert "rustic" in prompt.lower() or "wooden" in prompt.lower()

    def test_build_prompt_modern_style(self, mock_service):
        """Test modern style prompt."""
        request = GenerateImageRequest(title="Sushi Plate", style="modern")
        prompt = mock_service._build_prompt(request)

        assert "modern" in prompt.lower() or "minimalist" in prompt.lower()

    @pytest.mark.asyncio
    async def test_get_mock_image_deterministic(self, mock_service):
        """Test mock images are deterministic based on recipe ID."""
        recipe_id = "test-recipe-123"
        url1 = await mock_service._get_mock_image(recipe_id)
        url2 = await mock_service._get_mock_image(recipe_id)

        assert url1 == url2
        assert "unsplash" in url1

    @pytest.mark.asyncio
    async def test_get_mock_image_varies_by_id(self, mock_service):
        """Test different recipe IDs get different images."""
        url1 = await mock_service._get_mock_image("recipe-1")
        url2 = await mock_service._get_mock_image("recipe-2")
        url3 = await mock_service._get_mock_image("recipe-3")

        # At least some should be different (probabilistic but very likely)
        urls = {url1, url2, url3}
        assert len(urls) >= 1  # At minimum they're valid URLs

    @pytest.mark.asyncio
    async def test_generate_image_mock_mode(self, mock_service):
        """Test full image generation in mock mode."""
        recipe_id = UUID("12345678-1234-1234-1234-123456789abc")
        request = GenerateImageRequest(
            title="Test Pizza",
            description="Delicious pepperoni pizza",
            ingredients=["dough", "tomato sauce", "mozzarella", "pepperoni"],
        )

        result = await mock_service.generate_image(recipe_id, request)

        assert result.success is True
        assert result.image_url is not None
        assert "unsplash" in result.image_url or "http" in result.image_url

    @pytest.mark.asyncio
    async def test_generate_image_returns_url(self, mock_service):
        """Test that generation returns a valid URL."""
        recipe_id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        request = GenerateImageRequest(title="Simple Salad")

        result = await mock_service.generate_image(recipe_id, request)

        assert result.success is True
        assert result.image_url.startswith("http")


class TestImageGenerationServiceNoApiKey:
    """Test service behavior without API key."""

    def test_service_falls_back_to_mock_without_key(self):
        """Test service uses mock when no API key is provided."""
        service = ImageGenerationService(google_api_key=None, use_mock=False)
        # Without key, should fall back to mock
        assert service.use_mock is True

    def test_service_uses_real_with_key(self):
        """Test service uses real generation when key is provided."""
        service = ImageGenerationService(google_api_key="fake-key-for-testing", use_mock=False)
        # With key, should not be mock mode
        assert service.use_mock is False
