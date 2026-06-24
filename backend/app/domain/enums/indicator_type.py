"""Technical indicator type enumeration."""

from enum import Enum


class IndicatorType(str, Enum):
    """Supported technical indicator types.

    This enum defines the list of supported technical indicators
    for cryptocurrency analysis.
    """

    RSI = "RSI"
    MACD = "MACD"
    EMA20 = "EMA20"
    EMA50 = "EMA50"
    EMA200 = "EMA200"
    SMA20 = "SMA20"
    AVG_VOLUME = "AVG_VOLUME"
    PERCENT_CHANGE = "PERCENT_CHANGE"