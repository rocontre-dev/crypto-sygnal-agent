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
        id: Optional unique identifier
    """

    symbol: CryptoSymbol
    timeframe: str
    rsi: Decimal
    macd: Decimal
    ema20: Decimal
    ema50: Decimal
    ema200: Decimal
    sma20: Decimal
    avg_volume: Decimal
    percent_change: Decimal
    volume_available: bool
    source: str
    timestamp: datetime
    macd_signal: Optional[Decimal] = None
    macd_histogram: Optional[Decimal] = None
    atr: Optional[Decimal] = None
    adx: Optional[Decimal] = None
    id: Optional[int] = None

    @property
    def symbol_str(self) -> str:
        """Get symbol as string."""
        return self.symbol.value if isinstance(self.symbol, CryptoSymbol) else self.symbol