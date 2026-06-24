"""Timeframe enumeration for market history data."""

from enum import Enum


class Timeframe(str, Enum):
    """Supported timeframes for market history data.

    This enum defines the available timeframes for historical
    OHLC data retrieval.

    Note: Currently only 1d (daily) timeframe is supported.
    4h timeframe is planned for future implementation with
    a different data provider (e.g., Binance, Coinbase).
    """

    ONE_DAY = "1d"
    FOUR_HOURS = "4h"