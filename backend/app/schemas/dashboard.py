"""Dashboard Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


class DashboardMarketData(BaseModel):
    """Market data for a single cryptocurrency."""

    symbol: str = Field(..., description="Cryptocurrency symbol")
    price: float = Field(..., description="Current price in USD")
    market_cap: Optional[float] = Field(default=None, description="Market capitalization in USD (null for Binance ticker)")
    volume_24h: float = Field(..., description="24-hour trading volume in USD")
    change_24h: float = Field(..., description="24-hour price change percentage")
    timestamp: datetime = Field(..., description="Data timestamp")
    source: str = Field(..., description="Data source (binance_ticker or mock)")


class DashboardSignal(BaseModel):
    """Trading signal for a cryptocurrency."""

    symbol: str = Field(..., description="Cryptocurrency symbol")
    signal: str = Field(..., description="Signal type (ENTER, WAIT, REDUCE, EXIT)")
    confidence_score: float = Field(..., description="Confidence score 0-100")
    risk_level: str = Field(..., description="Risk level (LOW, MEDIUM, HIGH)")
    stop_loss: Optional[float] = Field(default=None, description="Suggested stop loss price (null for WAIT/EXIT/REDUCE)")
    take_profit: Optional[float] = Field(default=None, description="Suggested take profit price (null for WAIT/EXIT/REDUCE)")
    timestamp: datetime = Field(..., description="Signal timestamp")


class DashboardAIExplanation(BaseModel):
    """AI explanation for a trading signal."""

    symbol: str = Field(..., description="Cryptocurrency symbol")
    signal: str = Field(..., description="Signal type")
    confidence_score: float = Field(..., description="Confidence score")
    risk_level: str = Field(..., description="Risk level")
    technical_summary: str = Field(..., description="Technical analysis summary")
    plain_spanish_explanation: str = Field(..., description="Plain Spanish explanation")
    risk_warning: str = Field(..., description="Risk warning")
    educational_disclaimer: str = Field(..., description="Educational disclaimer")
    timestamp: datetime = Field(..., description="Explanation timestamp")


class DashboardItem(BaseModel):
    """Complete dashboard item for a single cryptocurrency."""

    market_data: DashboardMarketData = Field(..., description="Market data")
    signal: DashboardSignal = Field(..., description="Trading signal")
    ai_explanation: DashboardAIExplanation = Field(..., description="AI explanation")


class DashboardResponse(BaseModel):
    """Response schema for the dashboard endpoint."""

    updated_at: datetime = Field(..., description="When the dashboard was last updated")
    source: str = Field(..., description="Overall data source (binance_ticker or mock)")
    cache_status: str = Field(..., description="Cache status (fresh or cached)")
    generation_time_ms: float = Field(..., description="Time to generate in milliseconds")
    items: List[DashboardItem] = Field(..., description="Dashboard items for each symbol")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "updated_at": "2024-01-15T10:30:00Z",
                "source": "binance_ticker",
                "cache_status": "fresh",
                "generation_time_ms": 1234.5,
                "items": [
                    {
                        "market_data": {
                            "symbol": "BTC",
                            "price": 67500.0,
                            "market_cap": None,
                            "volume_24h": 25000000000.0,
                            "change_24h": 2.5,
                            "timestamp": "2024-01-15T10:30:00Z",
                            "source": "binance_ticker",
                        },
                        "signal": {
                            "symbol": "BTC",
                            "signal": "ENTER",
                            "confidence_score": 75.0,
                            "risk_level": "MEDIUM",
                            "stop_loss": 65000.0,
                            "take_profit": 70000.0,
                            "timestamp": "2024-01-15T10:30:00Z",
                        },
                        "ai_explanation": {
                            "symbol": "BTC",
                            "signal": "ENTER",
                            "confidence_score": 75.0,
                            "risk_level": "MEDIUM",
                            "technical_summary": "Technical analysis summary...",
                            "plain_spanish_explanation": "Explicación en español...",
                            "risk_warning": "Advertencia de riesgo...",
                            "educational_disclaimer": "Descargo de responsabilidad...",
                            "timestamp": "2024-01-15T10:30:00Z",
                        },
                    }
                ],
            }
        }
    )