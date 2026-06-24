"""AI explanations API endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.schemas.ai_explanation import AIExplanationResponse
from app.services.ai_explanation_service import AIExplanationService

router = APIRouter(prefix="/ai-explanations", tags=["AI Explanations"])


@router.get(
    "/{symbol}",
    response_model=AIExplanationResponse,
    summary="Get AI explanation for trading signal",
    description="Returns an AI-generated explanation for a trading signal. The AI explains the existing rule-based signal in clearer Spanish without modifying the original signal decision.",
    responses={
        200: {"description": "Successfully generated AI explanation"},
        404: {"description": "Symbol not supported"},
    },
)
async def get_ai_explanation(symbol: str) -> AIExplanationResponse:
    """Get an AI explanation for a trading signal.

    This endpoint uses OpenAI (when available) to generate a clear Spanish
    explanation of the trading signal. The AI:
    - Never modifies the signal decision (ENTER, WAIT, REDUCE, EXIT)
    - Never changes confidence_score, risk_level, stop_loss, or take_profit
    - Only generates explanatory text (technical_summary, plain_spanish_explanation, risk_warning, educational_disclaimer)
    - Falls back to deterministic explanations when OpenAI is unavailable

    Args:
        symbol: Cryptocurrency symbol (BTC, ETH, SOL)

    Returns:
        AIExplanationResponse: AI-generated explanation with original signal data

    Raises:
        HTTPException: If symbol is not supported
    """
    service = AIExplanationService()
    explanation = await service.generate_explanation(symbol)

    if explanation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI explanation for symbol '{symbol}' not available. Supported symbols: BTC, ETH, SOL",
        )

    return explanation