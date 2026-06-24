"""Market data API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.repositories.market_data_repository import MarketDataRepository
from app.schemas.market_data import MarketDataListResponse, MarketDataResponse
from app.services.market_data_service import MarketDataService

router = APIRouter(prefix="/markets", tags=["Markets"])


def get_repository(db=Depends) -> MarketDataRepository:
    """Dependency to get market data repository."""
    from app.database import get_db
    # This is a simplified dependency - in production use proper DI
    return MarketDataRepository(db)


@router.get(
    "",
    response_model=MarketDataListResponse,
    summary="Get all market data",
    description="Returns market data for all supported cryptocurrencies (BTC, ETH, SOL).",
    responses={
        200: {"description": "Successfully retrieved market data"},
    },
)
async def get_all_markets(
    repository: MarketDataRepository = Depends(get_repository),
) -> MarketDataListResponse:
    """Get market data for all supported cryptocurrencies.

    Returns:
        MarketDataListResponse: List of market data for all symbols
    """
    service = MarketDataService(repository)
    data = await service.get_all_market_data()
    return MarketDataListResponse(data=data, count=len(data))


@router.get(
    "/{symbol}",
    response_model=MarketDataResponse,
    summary="Get market data by symbol",
    description="Returns market data for a specific cryptocurrency symbol.",
    responses={
        200: {"description": "Successfully retrieved market data"},
        404: {"description": "Symbol not found"},
        422: {"description": "Invalid symbol"},
    },
)
async def get_market_by_symbol(
    symbol: str,
    repository: MarketDataRepository = Depends(get_repository),
) -> MarketDataResponse:
    """Get market data for a specific cryptocurrency.

    Args:
        symbol: Cryptocurrency symbol (BTC, ETH, SOL)

    Returns:
        MarketDataResponse: Market data for the requested symbol

    Raises:
        HTTPException: If symbol is not found or invalid
    """
    service = MarketDataService(repository)
    data = await service.get_market_data_by_symbol(symbol)

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Market data for symbol '{symbol}' not found. Supported symbols: BTC, ETH, SOL",
        )

    return data