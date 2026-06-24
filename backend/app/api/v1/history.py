"""Market history API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.market_history import MarketHistoryResponse
from app.services.market_history_service import MarketHistoryService

router = APIRouter(prefix="/history", tags=["History"])


@router.get(
    "/{symbol}",
    response_model=MarketHistoryResponse,
    summary="Get historical OHLCV data",
    description=(
        "Returns historical OHLCV (Open, High, Low, Close, Volume) data for a specific cryptocurrency. "
        "Data is fetched from Binance public klines API and cached for improved performance.\n\n"
        "**Note:** This endpoint uses Binance public market data only. No API key is required.\n\n"
        "**Supported timeframes:**\n"
        "- `1d` (daily): Last 365 candles\n"
        "- `4h` (4-hour): Last 500 candles"
    ),
    responses={
        200: {"description": "Successfully retrieved historical data"},
        400: {"description": "Invalid or unsupported timeframe"},
        404: {"description": "Symbol not found"},
        503: {"description": "Service unavailable - unable to fetch data"},
    },
)
async def get_history(
    symbol: str,
    timeframe: str = Query(
        default="1d",
        description="Candle timeframe. Supported values: '1d' (daily), '4h' (4-hour).",
        examples=["1d"],
    ),
    service: MarketHistoryService = Depends(),
) -> MarketHistoryResponse:
    """Get historical OHLC data for a specific cryptocurrency.

    Args:
        symbol: Cryptocurrency symbol (BTC, ETH, SOL)
        timeframe: Candle timeframe (default: "1d"). Only "1d" is currently supported.
        service: Market history service (injected dependency)

    Returns:
        MarketHistoryResponse: Historical OHLC data with metadata

    Raises:
        HTTPException: 404 if symbol not found, 400 if timeframe not supported,
                       503 if data cannot be fetched
    """
    # Validate symbol
    if symbol.upper() not in service.SUPPORTED_SYMBOLS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Symbol '{symbol}' not found. "
                f"Supported symbols: {', '.join(sorted(service.SUPPORTED_SYMBOLS))}"
            ),
        )

    # Validate timeframe
    if timeframe not in service.SUPPORTED_TIMEFRAMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Timeframe '{timeframe}' is not supported. "
                f"Supported timeframes: {', '.join(sorted(service.SUPPORTED_TIMEFRAMES))}"
            ),
        )

    try:
        result = await service.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
        )
        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch historical data: {str(e)}",
        )


def get_market_history_service() -> MarketHistoryService:
    """Dependency to get market history service instance."""
    return MarketHistoryService()