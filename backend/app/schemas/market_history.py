"""Market history Pydantic schemas for OHLC data."""

from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field, ConfigDict


class OHLCCandleResponse(BaseModel):
    """Response schema for a single OHLC candle.

    Attributes:
        timestamp: Candle open time
        open: Opening price in USD
        high: Highest price in USD during the period
        low: Lowest price in USD during the period
        close: Closing price in USD
        volume: Trading volume (always null for CoinGecko OHLC)
    """

    timestamp: datetime = Field(..., description="Candle open time")
    open: float = Field(..., description="Opening price in USD")
    high: float = Field(..., description="Highest price in USD")
    low: float = Field(..., description="Lowest price in USD")
    close: float = Field(..., description="Closing price in USD")
    volume: Optional[float] = Field(
        default=None,
        description="Trading volume (null - not available from CoinGecko OHLC)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "timestamp": "2024-01-15T00:00:00Z",
                "open": "42500.00",
                "high": "43200.00",
                "low": "42100.00",
                "close": "42800.00",
                "volume": None
            }
        }
    )


class MarketHistoryResponse(BaseModel):
    """Response schema for market history data.

    Attributes:
        symbol: Cryptocurrency symbol (BTC, ETH, SOL)
        timeframe: Candle timeframe (1d)
        count: Number of candles in the response
        volume_available: Whether volume data is available (always false)
        source: Data source identifier
        candles: List of OHLC candles
    """

    symbol: str = Field(..., description="Cryptocurrency symbol")
    timeframe: str = Field(..., description="Candle timeframe")
    count: int = Field(..., description="Number of candles")
    volume_available: bool = Field(
        default=False,
        description="Whether volume data is available (CoinGecko OHLC does not provide volume)"
    )
    source: str = Field(
        default="coingecko_ohlc",
        description="Data source identifier"
    )
    candles: List[OHLCCandleResponse] = Field(..., description="List of OHLC candles")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "BTC",
                "timeframe": "1d",
                "count": 365,
                "volume_available": False,
                "source": "coingecko_ohlc",
                "candles": [
                    {
                        "timestamp": "2024-01-15T00:00:00Z",
                        "open": "42500.00",
                        "high": "43200.00",
                        "low": "42100.00",
                        "close": "42800.00",
                        "volume": None
                    }
                ]
            }
        }
    )