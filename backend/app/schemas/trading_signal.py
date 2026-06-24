"""Trading signal Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TradingSignalResponse(BaseModel):
    """Response schema for trading signal data.

    Attributes:
        symbol: Cryptocurrency symbol
        signal: Trading signal type (ENTER, WAIT, REDUCE, EXIT)
        confidence_score: Signal confidence (0-100) as a number
        risk_level: Risk assessment (LOW, MEDIUM, HIGH)
        reason: Detailed explanation in Spanish
        stop_loss: Suggested stop-loss price as a number
        take_profit: Suggested take-profit price as a number
        invalidation_condition: Condition that invalidates the signal (Spanish)
        timestamp: When this signal was generated
    """

    symbol: str = Field(..., description="Cryptocurrency symbol", examples=["BTC"])
    signal: str = Field(..., description="Trading signal type", examples=["ENTER"])
    confidence_score: float = Field(..., description="Signal confidence (0-100)", examples=[75.0])
    risk_level: str = Field(..., description="Risk level", examples=["MEDIUM"])
    reason: str = Field(..., description="Detailed explanation in Spanish")
    stop_loss: float = Field(..., description="Suggested stop-loss price")
    take_profit: float = Field(..., description="Suggested take-profit price")
    invalidation_condition: str = Field(..., description="Invalidation condition in Spanish")
    timestamp: datetime = Field(..., description="Signal generation timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "BTC",
                "signal": "ENTER",
                "confidence_score": 75.0,
                "risk_level": "MEDIUM",
                "reason": "Señal de COMPRA detectada. RSI en zona de sobreventa (32.5), precio por encima de EMA20, EMA20 > EMA50, MACD positivo.",
                "stop_loss": 65000.0,
                "take_profit": 70000.0,
                "invalidation_condition": "Si el precio cae por debajo de EMA50 o RSI supera 50.",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    )