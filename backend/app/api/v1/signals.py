"""Trading signals API endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.schemas.trading_signal import TradingSignalResponse
from app.services.signal_engine_service import SignalEngineService

router = APIRouter(prefix="/signals", tags=["Signals"])


@router.get(
    "/{symbol}",
    response_model=TradingSignalResponse,
    summary="Get trading signal by symbol",
    description="Returns a trading signal for a specific cryptocurrency based on technical analysis.",
    responses={
        200: {"description": "Successfully generated trading signal"},
        404: {"description": "Symbol not supported"},
    },
)
async def get_trading_signal(symbol: str) -> TradingSignalResponse:
    """Get a trading signal for a specific cryptocurrency.

    Analyzes technical indicators and generates a trading signal with:
    - Signal type (ENTER, WAIT, REDUCE, EXIT)
    - Confidence score (0-100)
    - Risk level (LOW, MEDIUM, HIGH)
    - Stop loss and take profit suggestions
    - Reasoning and invalidation conditions (in Spanish)

    Args:
        symbol: Cryptocurrency symbol (BTC, ETH, SOL)

    Returns:
        TradingSignalResponse: Generated trading signal

    Raises:
        HTTPException: If symbol is not supported
    """
    service = SignalEngineService()
    signal = await service.generate_signal(symbol)

    if signal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trading signal for symbol '{symbol}' not available. Supported symbols: BTC, ETH, SOL",
        )

    return TradingSignalResponse(
        symbol=signal.symbol_str,
        signal=signal.signal.value,
        confidence_score=signal.confidence_score,
        risk_level=signal.risk_level.value,
        reason=signal.reason,
        stop_loss=signal.stop_loss,
        take_profit=signal.take_profit,
        invalidation_condition=signal.invalidation_condition,
        timestamp=signal.timestamp,
    )