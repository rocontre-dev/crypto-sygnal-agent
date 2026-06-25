"""Market data entity."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..enums.crypto_symbol import CryptoSymbol


@dataclass
class MarketDataEntity:
    """Market data entity representing cryptocurrency market information.

    This entity encapsulates the core market data for a cryptocurrency,
    including price, market cap, volume, and price changes.

    Attributes:
        id: Unique identifier for the market data record
        symbol: Cryptocurrency symbol (e.g., BTC, ETH, SOL)
        price: Current price in USD
        market_cap: Market capitalization in USD (None for Binance ticker)
        volume_24h: Trading volume in the last 24 hours in USD
        change_24h: Price change percentage in the last 24 hours
        timestamp: When this data was recorded
        source: Data source ("binance_ticker" or "mock")
    """

    symbol: CryptoSymbol
    price: Decimal
    volume_24h: Decimal
    change_24h: Decimal
    timestamp: datetime
    market_cap: Optional[Decimal] = None
    id: Optional[int] = None
    source: str = "binance_ticker"

    @property
    def symbol_str(self) -> str:
        """Get symbol as string."""
        return self.symbol.value if isinstance(self.symbol, CryptoSymbol) else self.symbol