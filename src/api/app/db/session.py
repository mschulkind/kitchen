"""Database session management using Supabase. 🗄️

Provides async database connections via Supabase Python client.
For direct PostgreSQL access, we use asyncpg.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from supabase import AsyncClient, acreate_client

from src.api.app.core.config import get_settings


async def get_supabase_client() -> AsyncClient:
    """Create an async Supabase client instance."""
    settings = get_settings()
    return await acreate_client(
        settings.supabase_url,
        settings.supabase_anon_key,
    )


@asynccontextmanager
async def get_supabase() -> AsyncGenerator[AsyncClient]:
    """Async context manager for Supabase client.

    Usage:
        async with get_supabase() as supabase:
            result = await supabase.table("pantry_items").select("*").execute()
    """
    client = await get_supabase_client()
    try:
        yield client
    finally:
        await client.aclose()
