"""Application configuration via environment variables. 🔧

Uses Pydantic Settings for type-safe configuration management.
All secrets should be passed via environment variables, never hardcoded!
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Kitchen API"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database (Supabase)
    supabase_url: str = "http://localhost:8000"
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    database_url: str = "postgresql://postgres:postgres@localhost:5432/postgres"

    # API Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # LLM Providers (Multi-Adapter Strategy per D6)
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""

    # Default LLM provider for different tasks
    llm_provider_vision: str = "gemini"  # D2: Gemini for vision
    llm_provider_planning: str = "claude"  # D2: Claude for planning

    # Voice/Webhook Integration (Phase 9)
    webhook_secret: str = ""  # Secret key for voice assistant webhooks


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
