"""Technical indicators API endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.schemas.technical_indicator import TechnicalIndicatorResponse
from app.services.technical_indicator_service import TechnicalIndicatorService

router = APIRouter(prefix="/indicators", tags=["Indicators"])


@router.get(
    "/{symbol}",
    response_model=TechnicalIndicatorResponse,
    summary="Get technical indicators by symbol",
    description="Returns calculated technical indicators for a specific cryptocurrency symbol.",
    responses={
        200: {"description": "Successfully calculated indicators"},
        404: {"description": "Symbol not supported"},
    },
)
async def get_indicators(symbol: str) -> TechnicalIndicatorResponse:
    """Get technical indicators for a specific cryptocurrency.

    Calculates the following indicators:
    - RSI (14 periods)
    - MACD (12, 26, 9)
    - EMA20, EMA50, EMA200
    - SMA20
    - Average Volume (20 periods)
    - Percent Change

    Args:
        symbol: Cryptocurrency symbol (BTC, ETH, SOL)

    Returns:
        TechnicalIndicatorResponse: Calculated indicators

    Raises:
        HTTPException: If symbol is not supported
    """
    service = TechnicalIndicatorService()
    indicator = await service.calculate_indicators(symbol)

    if indicator is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technical indicators for symbol '{symbol}' not available. Supported symbols: BTC, ETH, SOL",
        )

    return TechnicalIndicatorResponse(
        symbol=indicator.symbol_str,
        rsi=indicator.rsi,
        macd=indicator.macd,
        ema20=indicator.ema20,
        ema50=indicator.ema50,
        ema200=indicator.ema200,
        sma20=indicator.sma20,
        avg_volume=indicator.avg_volume,
        percent_change=indicator.percent_change,
        timestamp=indicator.timestamp,
    )