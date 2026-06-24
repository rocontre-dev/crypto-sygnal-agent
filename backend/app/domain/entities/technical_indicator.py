"""Technical indicator entity."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..enums.crypto_symbol import CryptoSymbol


@dataclass
class TechnicalIndicatorEntity:
    """Technical indicator entity representing calculated indicators for a cryptocurrency.

    This entity encapsulates all calculated technical indicators for a cryptocurrency,
    including trend indicators, momentum indicators, and volume indicators.

    Attributes:
        symbol: Cryptocurrency symbol (e.g., BTC, ETH, SOL)
        rsi: Relative Strength Index (14 periods)
        macd: MACD value (12, 26, 9)
        ema20: 20-period Exponential Moving Average
        ema50: 50-period Exponential Moving Average
        ema200: 200-period Exponential Moving Average
        sma20: 20-period Simple Moving Average
        avg_volume: Average trading volume (20 periods)
        percent_change: Price change percentage
        timestamp: When this data was calculated
        id: Optional unique identifier
    """

    symbol: CryptoSymbol
    rsi: Decimal
    macd: Decimal
    ema20: Decimal
    ema50: Decimal
    ema200: Decimal
    sma20: Decimal
    avg_volume: Decimal
    percent_change: Decimal
    timestamp: datetime
    id: Optional[int] = None

    @property
    def symbol_str(self) -> str:
        """Get symbol as string."""
        return self.symbol.value if isinstance(self.symbol, CryptoSymbol) else self.symbol