"""Health check API endpoints."""

from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> dict[str, str]:
    """Check the health status of the API.

    Returns:
        HealthResponse: Status of the API
    """
    return {"status": "ok"}