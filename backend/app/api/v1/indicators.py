"""Technical indicators API endpoints."""

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.technical_indicator import TechnicalIndicatorResponse
from app.services.technical_indicator_service import TechnicalIndicatorService

router = APIRouter(prefix="/indicators", tags=["Indicators"])


@router.get(
    "/{symbol}",
    response_model=TechnicalIndicatorResponse,
    summary="Get technical indicators by symbol",
    description=(
        "Returns calculated technical indicators for a specific cryptocurrency symbol. "
        "Indicators are calculated from real historical OHLCV data from Binance public klines.\n\n"
        "**Supported indicators:**\n"
        "- RSI (14 periods)\n"
        "- MACD (12, 26, 9) with signal line and histogram\n"
        "- EMA20, EMA50, EMA200\n"
        "- SMA20\n"
        "- ATR (14 periods)\n"
        "- ADX (14 periods)\n"
        "- Average Volume (20 periods)\n"
        "- Percent Change\n\n"
        "**Data source:** Binance public klines API"
    ),
    responses={
        200: {"description": "Successfully calculated indicators"},
        400: {"description": "Invalid or unsupported timeframe"},
        404: {"description": "Symbol not supported"},
        503: {"description": "Unable to fetch data from Binance"},
    },
)
async def get_indicators(
    symbol: str,
    timeframe: str = Query(
        default="1d",
        description="Candle timeframe. Currently only '1d' is supported. Use '4h' for 4-hour candles (not yet enabled).",
        examples=["1d"],
    ),
) -> TechnicalIndicatorResponse:
    """Get technical indicators for a specific cryptocurrency.

    Args:
        symbol: Cryptocurrency symbol (BTC, ETH, SOL)
        timeframe: Candle timeframe (default: "1d")

    Returns:
        TechnicalIndicatorResponse: Calculated indicators

    Raises:
        HTTPException: 404 if symbol not supported, 400 if timeframe not supported,
                       503 if data cannot be fetched
    """
    # Validate timeframe
    if timeframe not in ["1d"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Timeframe '{timeframe}' is not supported for indicators yet. "
                f"Currently only '1d' is available. '4h' indicators are not enabled yet."
            ),
        )

    service = TechnicalIndicatorService()
    
    try:
        indicator = await service.calculate_indicators(symbol, timeframe)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )

    if indicator is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technical indicators for symbol '{symbol}' not available. Supported symbols: BTC, ETH, SOL",
        )

    return TechnicalIndicatorResponse(
        symbol=indicator.symbol_str,
        timeframe=indicator.timeframe,
        rsi=float(indicator.rsi) if indicator.rsi is not None else None,
        macd=float(indicator.macd) if indicator.macd is not None else None,
        macd_signal=float(indicator.macd_signal) if indicator.macd_signal is not None else None,
        macd_histogram=float(indicator.macd_histogram) if indicator.macd_histogram is not None else None,
        ema20=float(indicator.ema20) if indicator.ema20 is not None else None,
        ema50=float(indicator.ema50) if indicator.ema50 is not None else None,
        ema200=float(indicator.ema200) if indicator.ema200 is not None else None,
        sma20=float(indicator.sma20) if indicator.sma20 is not None else None,
        atr=float(indicator.atr) if indicator.atr is not None else None,
        adx=float(indicator.adx) if indicator.adx is not None else None,
        avg_volume=float(indicator.avg_volume) if indicator.avg_volume is not None else None,
        percent_change=float(indicator.percent_change) if indicator.percent_change is not None else None,
        volume_available=indicator.volume_available,
        source=indicator.source,
        timestamp=indicator.timestamp,
    )