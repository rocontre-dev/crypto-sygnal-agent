"""API v1 router that includes all endpoint routers."""

from fastapi import APIRouter

from .health import router as health_router
from .markets import router as markets_router
from .indicators import router as indicators_router
from .signals import router as signals_router
from .ai_explanations import router as ai_explanations_router

# Create the main API v1 router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(health_router)
api_router.include_router(markets_router)
api_router.include_router(indicators_router)
api_router.include_router(signals_router)
api_router.include_router(ai_explanations_router)
