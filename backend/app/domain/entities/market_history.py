"""Market history entity for OHLC candle data."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..enums.crypto_symbol import CryptoSymbol
from ..enums.timeframe import Timeframe


@dataclass
class OHLCCandle:
    """OHLC candle entity representing a single price candle.

    This entity encapsulates the open, high, low, and close prices
    for a specific timeframe. Volume is not included as CoinGecko's
    free OHLC endpoint does not provide volume data.

    Attributes:
        timestamp: Candle open time
        open: Opening price
        high: Highest price during the period
        low: Lowest price during the period
        close: Closing price
        volume: Trading volume (always None for CoinGecko OHLC)
        symbol: Cryptocurrency symbol
        timeframe: Candle timeframe
    """

    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    symbol: CryptoSymbol
    timeframe: Timeframe
    volume: Optional[Decimal] = None

    @property
    def symbol_str(self) -> str:
        """Get symbol as string."""
        return self.symbol.value if isinstance(self.symbol, CryptoSymbol) else self.symbol

    @property
    def timeframe_str(self) -> str:
        """Get timeframe as string."""
        return self.timeframe.value if isinstance(self.timeframe, Timeframe) else self.timeframe