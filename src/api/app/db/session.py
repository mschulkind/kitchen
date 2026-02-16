"""Database session management using Supabase. 🗄️

Provides async database connections via Supabase Python client.
For direct PostgreSQL access, we use asyncpg.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from supabase import AsyncClient, acreate_client

from src.api.app.core.config import get_settings


async def get_supabase_client() -> AsyncClient:
    """Create an async Supabase client instance.
    
    Uses service_role key to bypass RLS — the API is the trusted backend.
    Falls back to anon key if service_role key is not configured.
    """
    settings = get_settings()
    key = settings.supabase_service_role_key or settings.supabase_anon_key
    return await acreate_client(
        settings.supabase_url,
        key,
    )


@asynccontextmanager
async def get_supabase() -> AsyncGenerator[AsyncClient]:
    """Async context manager for Supabase client.

    Usage:
        async with get_supabase() as supabase:
            result = await supabase.table("pantry_items").select("*").execute()
    """
    client = await get_supabase_client()
    yield client
    # AsyncClient has no close method; no cleanup needed
