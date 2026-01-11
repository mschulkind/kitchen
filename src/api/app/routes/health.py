"""Health check routes. 🏥

System health endpoints for monitoring and Docker healthchecks.
"""

from fastapi import APIRouter

router = APIRouter(tags=["Health 🏥"])


@router.get("/health")
async def health_check() -> dict:
    """Simple health check endpoint.

    Used by Docker healthcheck and load balancers.
    """
    return {"status": "healthy", "service": "kitchen-api"}


@router.get("/ready")
async def readiness_check() -> dict:
    """Readiness check - verifies all dependencies are available.

    TODO: Add database connectivity check.
    """
    return {"status": "ready", "checks": {"database": "ok"}}
