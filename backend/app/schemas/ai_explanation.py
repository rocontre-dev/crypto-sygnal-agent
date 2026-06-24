"""AI explanation Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class AIExplanationResponse(BaseModel):
    """Response schema for AI-generated explanation of a trading signal.

    The signal-related fields (symbol, signal, confidence_score, risk_level,
    stop_loss, take_profit, invalidation_condition) come directly from
    SignalEngineService and are NOT modified by the AI.

    The AI only generates:
    - technical_summary
    - plain_spanish_explanation
    - risk_warning
    - educational_disclaimer

    Attributes:
        symbol: Cryptocurrency symbol
        signal: Trading signal type (ENTER, WAIT, REDUCE, EXIT) - from SignalEngineService
        confidence_score: Signal confidence (0-100) - from SignalEngineService
        risk_level: Risk assessment (LOW, MEDIUM, HIGH) - from SignalEngineService
        stop_loss: Suggested stop-loss price - from SignalEngineService
        take_profit: Suggested take-profit price - from SignalEngineService
        invalidation_condition: Condition that invalidates the signal - from SignalEngineService
        technical_summary: Technical analysis summary in Spanish
        plain_spanish_explanation: Clear explanation in simple Spanish
        risk_warning: Risk warning message
        educational_disclaimer: Educational disclaimer
        timestamp: When this explanation was generated
    """

    symbol: str = Field(..., description="Cryptocurrency symbol")
    signal: str = Field(..., description="Trading signal type")
    confidence_score: float = Field(..., description="Signal confidence (0-100)")
    risk_level: str = Field(..., description="Risk level")
    stop_loss: Optional[float] = Field(default=None, description="Suggested stop-loss price (null for WAIT/EXIT/REDUCE)")
    take_profit: Optional[float] = Field(default=None, description="Suggested take-profit price (null for WAIT/EXIT/REDUCE)")
    invalidation_condition: str = Field(..., description="Invalidation condition from SignalEngineService")
    technical_summary: str = Field(..., description="Technical analysis summary in Spanish")
    plain_spanish_explanation: str = Field(..., description="Clear explanation in simple Spanish")
    risk_warning: str = Field(..., description="Risk warning message")
    educational_disclaimer: str = Field(..., description="Educational disclaimer")
    timestamp: datetime = Field(..., description="Explanation generation timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "BTC",
                "signal": "ENTER",
                "confidence_score": 75.0,
                "risk_level": "MEDIUM",
                "stop_loss": 65000.0,
                "take_profit": 70000.0,
                "invalidation_condition": "Si el precio cae por debajo de EMA50.",
                "technical_summary": "El RSI muestra sobreventa con valor de 32.5, indicando posible reversión alcista.",
                "plain_spanish_explanation": "Los indicadores técnicos sugieren una oportunidad de compra.",
                "risk_warning": "Las criptomonedas son activos volátiles. Nunca inviertas dinero que no puedas permitirte perder.",
                "educational_disclaimer": "Esta explicación es solo para fines educativos. No constituye asesoramiento financiero.",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    )