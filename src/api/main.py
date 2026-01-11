"""Kitchen API - The Chef's Brain 🧠

FastAPI application for the Kitchen project.
Provides the intelligence layer for recipe management,
meal planning, and inventory tracking.

Fun fact: The first commercial kitchen robot was introduced in 2016! 🤖
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.app.core.config import get_settings
from src.api.app.core.logging import configure_logging, get_logger
from src.api.app.routes import health, pantry, planner, recipes, shopping


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan handler.

    Runs on startup and shutdown.
    """
    settings = get_settings()
    configure_logging(settings.debug)
    logger = get_logger(__name__)

    logger.info(
        "Starting Kitchen API",
        version=settings.app_version,
        debug=settings.debug,
    )

    yield

    logger.info("Shutting down Kitchen API")


def create_app() -> FastAPI:
    """Application factory.

    Creates and configures the FastAPI application.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="The Chef's Brain - AI-powered kitchen management 🍳",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware for frontend access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health.router)
    app.include_router(pantry.router, prefix="/api/v1")
    app.include_router(recipes.router, prefix="/api/v1")
    app.include_router(shopping.router, prefix="/api/v1")
    app.include_router(planner.router, prefix="/api/v1")

    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
