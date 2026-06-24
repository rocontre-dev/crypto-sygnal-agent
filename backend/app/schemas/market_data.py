"""Market data Pydantic schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class MarketDataResponse(BaseModel):
    """Response schema for a single market data entry.

    Attributes:
        id: Unique identifier
        symbol: Cryptocurrency symbol
        price: Current price in USD
        market_cap: Market capitalization in USD
        volume_24h: 24-hour trading volume in USD
        change_24h: 24-hour price change percentage
        timestamp: Data timestamp
    """

    id: Optional[int] = None
    symbol: str = Field(..., description="Cryptocurrency symbol", examples=["BTC"])
    price: float = Field(..., description="Current price in USD", examples=[67500.00])
    market_cap: float = Field(..., description="Market capitalization in USD", examples=[1300000000000])
    volume_24h: float = Field(..., description="24-hour trading volume in USD", examples=[25000000000])
    change_24h: float = Field(..., description="24-hour price change percentage", examples=[2.5])
    timestamp: datetime = Field(..., description="Data timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "symbol": "BTC",
                "price": "67500.00",
                "market_cap": "1300000000000.00",
                "volume_24h": "25000000000.00",
                "change_24h": "2.50",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    )


class MarketDataListResponse(BaseModel):
    """Response schema for a list of market data entries.

    Attributes:
        data: List of market data entries
        count: Number of entries in the response
    """

    data: List[MarketDataResponse] = Field(..., description="List of market data entries")
    count: int = Field(..., description="Number of entries")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": 1,
                        "symbol": "BTC",
                        "price": "67500.00",
                        "market_cap": "1300000000000.00",
                        "volume_24h": "25000000000.00",
                        "change_24h": "2.50",
                        "timestamp": "2024-01-15T10:30:00Z"
                    },
                    {
                        "id": 2,
                        "symbol": "ETH",
                        "price": "3500.00",
                        "market_cap": "420000000000.00",
                        "volume_24h": "12000000000.00",
                        "change_24h": "-1.20",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                ],
                "count": 2
            }
        }
    )