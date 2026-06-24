"""Cryptocurrency symbol enumeration."""

from enum import Enum


class CryptoSymbol(str, Enum):
    """Supported cryptocurrency symbols.

    This enum defines the list of supported cryptocurrency symbols
    for market data tracking.
    """

    BTC = "BTC"
    ETH = "ETH"
    SOL = "SOL"