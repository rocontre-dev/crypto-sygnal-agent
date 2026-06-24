"""Technical indicator Pydantic schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TechnicalIndicatorResponse(BaseModel):
    """Response schema for technical indicator data.

    Attributes:
        symbol: Cryptocurrency symbol
        rsi: Relative Strength Index (14 periods)
        macd: MACD value (12, 26, 9)
        ema20: 20-period Exponential Moving Average
        ema50: 50-period Exponential Moving Average
        ema200: 200-period Exponential Moving Average
        sma20: 20-period Simple Moving Average
        avg_volume: Average trading volume (20 periods)
        percent_change: Price change percentage
        timestamp: When this data was calculated
    """

    symbol: str = Field(..., description="Cryptocurrency symbol", examples=["BTC"])
    rsi: Decimal = Field(..., description="Relative Strength Index (14 periods)", examples=[48.3])
    macd: Decimal = Field(..., description="MACD value (12, 26, 9)", examples=[125.8])
    ema20: Decimal = Field(..., description="20-period EMA", examples=[67200])
    ema50: Decimal = Field(..., description="50-period EMA", examples=[66450])
    ema200: Decimal = Field(..., description="200-period EMA", examples=[61200])
    sma20: Decimal = Field(..., description="20-period SMA", examples=[67010])
    avg_volume: Decimal = Field(..., description="Average volume (20 periods)", examples=[21000000000])
    percent_change: Decimal = Field(..., description="Price change percentage", examples=[1.6])
    timestamp: datetime = Field(..., description="Calculation timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "BTC",
                "rsi": "48.3",
                "macd": "125.8",
                "ema20": "67200.0",
                "ema50": "66450.0",
                "ema200": "61200.0",
                "sma20": "67010.0",
                "avg_volume": "21000000000.0",
                "percent_change": "1.6",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    )