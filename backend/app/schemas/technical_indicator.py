"""Technical indicator Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TechnicalIndicatorResponse(BaseModel):
    """Response schema for technical indicator data.

    Attributes:
        symbol: Cryptocurrency symbol
        timeframe: Candle timeframe (e.g., "1d")
        rsi: Relative Strength Index (14 periods)
        macd: MACD value (12, 26, 9)
        macd_signal: MACD signal line (9-period EMA of MACD)
        macd_histogram: MACD histogram (MACD - signal)
        ema20: 20-period Exponential Moving Average
        ema50: 50-period Exponential Moving Average
        ema200: 200-period Exponential Moving Average
        sma20: 20-period Simple Moving Average
        atr: Average True Range (14 periods)
        adx: Average Directional Index (14 periods)
        avg_volume: Average trading volume (20 periods)
        percent_change: Price change percentage
        volume_available: Whether volume data is available
        source: Data source identifier
        timestamp: When this data was calculated
    """

    symbol: str = Field(..., description="Cryptocurrency symbol", examples=["BTC"])
    timeframe: str = Field(..., description="Candle timeframe", examples=["1d"])
    rsi: Optional[float] = Field(default=None, description="Relative Strength Index (14 periods)", examples=[48.3])
    macd: Optional[float] = Field(default=None, description="MACD value (12, 26, 9)", examples=[125.8])
    macd_signal: Optional[float] = Field(default=None, description="MACD signal line", examples=[118.45])
    macd_histogram: Optional[float] = Field(default=None, description="MACD histogram", examples=[7.35])
    ema20: Optional[float] = Field(default=None, description="20-period EMA", examples=[67200])
    ema50: Optional[float] = Field(default=None, description="50-period EMA", examples=[66450])
    ema200: Optional[float] = Field(default=None, description="200-period EMA", examples=[61200])
    sma20: Optional[float] = Field(default=None, description="20-period SMA", examples=[67010])
    atr: Optional[float] = Field(default=None, description="Average True Range (14 periods)", examples=[1250.5])
    adx: Optional[float] = Field(default=None, description="Average Directional Index (14 periods)", examples=[28.45])
    avg_volume: Optional[float] = Field(default=None, description="Average volume (20 periods)", examples=[21000000000])
    percent_change: Optional[float] = Field(default=None, description="Price change percentage", examples=[1.6])
    volume_available: bool = Field(default=True, description="Whether volume data is available")
    source: str = Field(default="binance_klines", description="Data source identifier")
    timestamp: datetime = Field(..., description="Calculation timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "BTC",
                "timeframe": "1d",
                "rsi": 48.3,
                "macd": 125.8,
                "macd_signal": 118.45,
                "macd_histogram": 7.35,
                "ema20": 67200.0,
                "ema50": 66450.0,
                "ema200": 61200.0,
                "sma20": 67010.0,
                "atr": 1250.5,
                "adx": 28.45,
                "avg_volume": 21000000000.0,
                "percent_change": 1.6,
                "volume_available": True,
                "source": "binance_klines",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    )