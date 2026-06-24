"""Technical indicator service."""

import numpy as np
import pandas as pd
import ta
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from app.core.logging_config import get_logger
from app.domain.entities.technical_indicator import TechnicalIndicatorEntity
from app.domain.enums.crypto_symbol import CryptoSymbol
from app.services.market_history_service import MarketHistoryService

logger = get_logger(__name__)


class TechnicalIndicatorService:
    """Service for calculating technical indicators from real market data.

    Uses Binance historical OHLCV data from MarketHistoryService to calculate
    real technical indicators. No synthetic or mock data is used.
    """

    # Supported symbols
    SUPPORTED_SYMBOLS = {"BTC", "ETH", "SOL"}

    # Supported timeframes
    SUPPORTED_TIMEFRAMES = {"1d"}

    def __init__(self, market_history_service: Optional[MarketHistoryService] = None):
        """Initialize the technical indicator service.

        Args:
            market_history_service: Optional MarketHistoryService instance
        """
        self.market_history_service = market_history_service or MarketHistoryService()

    async def calculate_indicators(
        self, symbol: str, timeframe: str = "1d"
    ) -> Optional[TechnicalIndicatorEntity]:
        """Calculate technical indicators for a given symbol.

        Args:
            symbol: Cryptocurrency symbol (BTC, ETH, SOL)
            timeframe: Candle timeframe (default: "1d")

        Returns:
            TechnicalIndicatorEntity with calculated indicators,
            or None if symbol is not supported

        Raises:
            RuntimeError: If Binance history is unavailable
        """
        # Validate symbol
        symbol_upper = symbol.upper()
        if symbol_upper not in self.SUPPORTED_SYMBOLS:
            return None

        # Validate timeframe
        if timeframe not in self.SUPPORTED_TIMEFRAMES:
            return None

        crypto_symbol = CryptoSymbol(symbol_upper)

        logger.info(f"Calculating indicators for {symbol_upper}/{timeframe}")

        # Fetch real historical data from Binance via MarketHistoryService
        history_response = await self.market_history_service.fetch_ohlcv(
            symbol=symbol_upper,
            timeframe=timeframe,
            use_cache=True,
        )

        if not history_response or not history_response.candles:
            logger.error(f"No historical data available for {symbol_upper}")
            raise RuntimeError(
                f"Failed to fetch historical data for {symbol_upper}. "
                f"Binance API may be unavailable."
            )

        # Convert to DataFrame
        df = self._candles_to_dataframe(history_response.candles)

        # Calculate indicators from real data
        return self._calculate_from_candles(crypto_symbol, timeframe, df)

    def _candles_to_dataframe(self, candles) -> pd.DataFrame:
        """Convert candle responses to DataFrame.

        Args:
            candles: List of OHLCCandleResponse objects

        Returns:
            DataFrame with OHLCV data
        """
        data = {
            "timestamp": [c.timestamp for c in candles],
            "open": [c.open for c in candles],
            "high": [c.high for c in candles],
            "low": [c.low for c in candles],
            "close": [c.close for c in candles],
            "volume": [c.volume if c.volume is not None else 0.0 for c in candles],
        }
        df = pd.DataFrame(data)
        # Sort by timestamp ascending for indicator calculations
        df = df.sort_values("timestamp").reset_index(drop=True)
        return df

    def _calculate_from_candles(
        self, symbol: CryptoSymbol, timeframe: str, df: pd.DataFrame
    ) -> TechnicalIndicatorEntity:
        """Calculate technical indicators from candle data.

        Args:
            symbol: Cryptocurrency symbol
            timeframe: Candle timeframe
            df: DataFrame with OHLCV data

        Returns:
            TechnicalIndicatorEntity with calculated indicators
        """
        # Calculate RSI (14 periods)
        rsi = self._safe_float(
            ta.momentum.RSIIndicator(df["close"], window=14).rsi().iloc[-1]
        )

        # Calculate MACD (12, 26, 9)
        macd_indicator = ta.trend.MACD(
            df["close"], window_fast=12, window_slow=26, window_sign=9
        )
        macd = self._safe_float(macd_indicator.macd().iloc[-1])
        macd_signal = self._safe_float(macd_indicator.macd_signal().iloc[-1])
        macd_histogram = self._safe_float(macd_indicator.macd_diff().iloc[-1])

        # Calculate EMAs
        ema20 = self._safe_float(
            ta.trend.EMAIndicator(df["close"], window=20).ema_indicator().iloc[-1]
        )
        ema50 = self._safe_float(
            ta.trend.EMAIndicator(df["close"], window=50).ema_indicator().iloc[-1]
        )
        ema200 = self._safe_float(
            ta.trend.EMAIndicator(df["close"], window=200).ema_indicator().iloc[-1]
        )

        # Calculate SMA (20 periods)
        sma20 = self._safe_float(
            ta.trend.SMAIndicator(df["close"], window=20).sma_indicator().iloc[-1]
        )

        # Calculate ATR (14 periods)
        atr = self._safe_float(
            ta.volatility.AverageTrueRange(
                df["high"], df["low"], df["close"], window=14
            )
            .average_true_range()
            .iloc[-1]
        )

        # Calculate ADX (14 periods)
        adx = self._safe_float(
            ta.trend.ADXIndicator(
                df["high"], df["low"], df["close"], window=14
            )
            .adx()
            .iloc[-1]
        )

        # Calculate average volume (20 periods)
        avg_volume = self._safe_float(df["volume"].rolling(window=20).mean().iloc[-1])

        # Calculate percent change
        if len(df) >= 2:
            last_close = float(df["close"].iloc[-1])
            prev_close = float(df["close"].iloc[-2])
            percent_change = ((last_close - prev_close) / prev_close) * 100
        else:
            percent_change = 0.0

        timestamp = datetime.now(timezone.utc)

        return TechnicalIndicatorEntity(
            symbol=symbol,
            timeframe=timeframe,
            rsi=Decimal(str(round(rsi, 2))) if rsi is not None else Decimal("0"),
            macd=Decimal(str(round(macd, 2))) if macd is not None else Decimal("0"),
            ema20=Decimal(str(round(ema20, 2))) if ema20 is not None else Decimal("0"),
            ema50=Decimal(str(round(ema50, 2))) if ema50 is not None else Decimal("0"),
            ema200=Decimal(str(round(ema200, 2))) if ema200 is not None else Decimal("0"),
            sma20=Decimal(str(round(sma20, 2))) if sma20 is not None else Decimal("0"),
            avg_volume=Decimal(str(round(avg_volume, 2))) if avg_volume is not None else Decimal("0"),
            percent_change=Decimal(str(round(percent_change, 2))),
            macd_signal=Decimal(str(round(macd_signal, 2))) if macd_signal is not None else None,
            macd_histogram=Decimal(str(round(macd_histogram, 2))) if macd_histogram is not None else None,
            atr=Decimal(str(round(atr, 2))) if atr is not None else None,
            adx=Decimal(str(round(adx, 2))) if adx is not None else None,
            volume_available=True,
            source="binance_klines",
            timestamp=timestamp,
        )

    def _safe_float(self, value) -> Optional[float]:
        """Convert value to float, returning None for NaN.

        Args:
            value: Value to convert

        Returns:
            Float value or None if NaN
        """
        if value is None:
            return None
        try:
            f = float(value)
            if np.isnan(f):
                return None
            return f
        except (ValueError, TypeError):
            return None