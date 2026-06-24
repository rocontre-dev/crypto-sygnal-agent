"""Dashboard API endpoint."""

from fastapi import APIRouter, Depends

from app.repositories.market_data_repository import MarketDataRepository
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_repository(db=Depends) -> MarketDataRepository:
    """Dependency to get market data repository."""
    from app.database import get_db

    return MarketDataRepository(db)


@router.get(
    "",
    response_model=DashboardResponse,
    summary="Get dashboard data",
    description="Returns aggregated dashboard data for all supported cryptocurrencies (BTC, ETH, SOL) including market data, trading signals, and AI explanations. Uses caching for improved performance.",
    responses={
        200: {"description": "Successfully retrieved dashboard data"},
    },
)
async def get_dashboard(
    repository: MarketDataRepository = Depends(get_repository),
) -> DashboardResponse:
    """Get dashboard data for all supported cryptocurrencies.

    This endpoint aggregates market data, trading signals, and AI explanations
    for all supported symbols in a single request, with server-side caching
    for improved performance.

    Returns:
        DashboardResponse: Aggregated dashboard data with cache information
    """
    service = DashboardService(repository)
    return await service.get_dashboard()