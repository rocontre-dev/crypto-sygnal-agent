"""Market history Pydantic schemas for OHLC data."""

from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field, ConfigDict


class OHLCCandleResponse(BaseModel):
    """Response schema for a single OHLCV candle.

    Attributes:
        timestamp: Candle open time
        open: Opening price in USD
        high: Highest price in USD during the period
        low: Lowest price in USD during the period
        close: Closing price in USD
        volume: Trading volume (available from Binance)
    """

    timestamp: datetime = Field(..., description="Candle open time")
    open: float = Field(..., description="Opening price in USD")
    high: float = Field(..., description="Highest price in USD")
    low: float = Field(..., description="Lowest price in USD")
    close: float = Field(..., description="Closing price in USD")
    volume: Optional[float] = Field(
        default=None,
        description="Trading volume (available from Binance)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "timestamp": "2024-01-15T00:00:00Z",
                "open": "42500.00",
                "high": "43200.00",
                "low": "42100.00",
                "close": "42800.00",
                "volume": "15234.56"
            }
        }
    )


class MarketHistoryResponse(BaseModel):
    """Response schema for market history data.

    Attributes:
        symbol: Cryptocurrency symbol (BTC, ETH, SOL)
        timeframe: Candle timeframe (1d, 4h)
        count: Number of candles in the response
        volume_available: Whether volume data is available (true for Binance)
        source: Data source identifier
        candles: List of OHLCV candles
    """

    symbol: str = Field(..., description="Cryptocurrency symbol")
    timeframe: str = Field(..., description="Candle timeframe")
    count: int = Field(..., description="Number of candles")
    volume_available: bool = Field(
        default=True,
        description="Whether volume data is available (true for Binance klines)"
    )
    source: str = Field(
        default="binance_klines",
        description="Data source identifier"
    )
    candles: List[OHLCCandleResponse] = Field(..., description="List of OHLCV candles")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "BTC",
                "timeframe": "1d",
                "count": 365,
                "volume_available": True,
                "source": "binance_klines",
                "candles": [
                    {
                        "timestamp": "2024-01-15T00:00:00Z",
                        "open": "42500.00",
                        "high": "43200.00",
                        "low": "42100.00",
                        "close": "42800.00",
                        "volume": "15234.56"
                    }
                ]
            }
        }
    )
