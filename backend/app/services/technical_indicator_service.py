"""Technical indicator service."""

import numpy as np
import pandas as pd
import ta
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional

from app.domain.entities.technical_indicator import TechnicalIndicatorEntity
from app.domain.enums.crypto_symbol import CryptoSymbol


class TechnicalIndicatorService:
    """Service for calculating technical indicators.

    Generates mock historical candle data and calculates
    technical indicators using the ta library.
    """

    # Fixed random seed for deterministic results
    RANDOM_SEED = 42

    # Base prices for each symbol (for deterministic mock data)
    BASE_PRICES = {
        CryptoSymbol.BTC: 65000.0,
        CryptoSymbol.ETH: 3400.0,
        CryptoSymbol.SOL: 145.0,
    }

    # Volatility multipliers for each symbol
    VOLATILITY = {
        CryptoSymbol.BTC: 0.02,
        CryptoSymbol.ETH: 0.03,
        CryptoSymbol.SOL: 0.04,
    }

    def __init__(self):
        """Initialize the technical indicator service."""
        pass

    async def calculate_indicators(self, symbol: str) -> Optional[TechnicalIndicatorEntity]:
        """Calculate technical indicators for a given symbol.

        Args:
            symbol: Cryptocurrency symbol (BTC, ETH, SOL)

        Returns:
            TechnicalIndicatorEntity with calculated indicators,
            or None if symbol is not supported
        """
        try:
            crypto_symbol = CryptoSymbol(symbol.upper())
        except ValueError:
            return None

        # Generate mock candle data
        candles = self._generate_mock_candles(crypto_symbol)

        # Calculate indicators
        return self._calculate_from_candles(crypto_symbol, candles)

    def _generate_mock_candles(self, symbol: CryptoSymbol) -> pd.DataFrame:
        """Generate mock historical candle data.

        Args:
            symbol: Cryptocurrency symbol

        Returns:
            DataFrame with OHLCV data
        """
        # Ensure seed is within valid range for numpy (0 to 2**32 - 1)
        # Use abs() and modulo to guarantee a positive integer in valid range
        seed = abs(hash(symbol.value)) % (2**32 - 1) + self.RANDOM_SEED
        seed = seed % (2**32 - 1)  # Final safety check
        np.random.seed(seed)

        base_price = self.BASE_PRICES[symbol]
        volatility = self.VOLATILITY[symbol]
        n_candles = 350  # Generate 350 candles (more than 300 required)

        # Generate timestamps (hourly data for the last ~14 days)
        now = datetime.now(timezone.utc)
        timestamps = [now - timedelta(hours=n_candles - i) for i in range(n_candles)]

        # Generate price data with trend and noise
        trend = np.linspace(0, base_price * 0.1, n_candles)
        noise = np.cumsum(np.random.randn(n_candles) * base_price * volatility * 0.3)
        prices = base_price + trend + noise

        # Ensure prices stay positive
        prices = np.maximum(prices, base_price * 0.5)

        # Generate OHLC from close prices
        opens = prices[:-1]
        closes = prices[1:]

        # For the first candle, use the first price
        opens = np.insert(opens, 0, prices[0])
        closes = np.insert(closes, 0, prices[0])

        # Generate highs and lows
        ranges = np.abs(closes - opens) + np.random.rand(n_candles) * base_price * volatility * 0.5
        highs = np.maximum(opens, closes) + ranges * np.random.rand(n_candles)
        lows = np.minimum(opens, closes) - ranges * np.random.rand(n_candles)

        # Generate volume
        base_volume = base_price * 100000  # Base volume proportional to price
        volumes = base_volume * (1 + np.random.randn(n_candles) * 0.3)
        volumes = np.maximum(volumes, base_volume * 0.3)

        return pd.DataFrame({
            'timestamp': timestamps,
            'open': opens,
            'high': highs,
            'low': lows,
            'close': closes,
            'volume': volumes,
        })

    def _calculate_from_candles(self, symbol: CryptoSymbol, df: pd.DataFrame) -> TechnicalIndicatorEntity:
        """Calculate technical indicators from candle data.

        Args:
            symbol: Cryptocurrency symbol
            df: DataFrame with OHLCV data

        Returns:
            TechnicalIndicatorEntity with calculated indicators
        """
        # Calculate RSI (14 periods)
        rsi_indicator = ta.momentum.RSIIndicator(df['close'], window=14)
        rsi = float(rsi_indicator.rsi().iloc[-1])

        # Calculate MACD (12, 26, 9)
        macd_indicator = ta.trend.MACD(df['close'], window_fast=12, window_slow=26, window_sign=9)
        macd = float(macd_indicator.macd().iloc[-1])

        # Calculate EMAs
        ema20_indicator = ta.trend.EMAIndicator(df['close'], window=20)
        ema20 = float(ema20_indicator.ema_indicator().iloc[-1])

        ema50_indicator = ta.trend.EMAIndicator(df['close'], window=50)
        ema50 = float(ema50_indicator.ema_indicator().iloc[-1])

        ema200_indicator = ta.trend.EMAIndicator(df['close'], window=200)
        ema200 = float(ema200_indicator.ema_indicator().iloc[-1])

        # Calculate SMA (20 periods)
        sma20_indicator = ta.trend.SMAIndicator(df['close'], window=20)
        sma20 = float(sma20_indicator.sma_indicator().iloc[-1])

        # Calculate average volume (20 periods)
        avg_volume_indicator = ta.volume.VolumeWeightedAveragePrice(df['high'], df['low'], df['close'], df['volume'], window=20)
        avg_volume = float(df['volume'].rolling(window=20).mean().iloc[-1])

        # Calculate percent change
        last_close = float(df['close'].iloc[-1])
        prev_close = float(df['close'].iloc[-2])
        percent_change = ((last_close - prev_close) / prev_close) * 100

        # Get current timestamp
        timestamp = datetime.now(timezone.utc)

        return TechnicalIndicatorEntity(
            symbol=symbol,
            rsi=Decimal(str(round(rsi, 2))),
            macd=Decimal(str(round(macd, 2))),
            ema20=Decimal(str(round(ema20, 2))),
            ema50=Decimal(str(round(ema50, 2))),
            ema200=Decimal(str(round(ema200, 2))),
            sma20=Decimal(str(round(sma20, 2))),
            avg_volume=Decimal(str(round(avg_volume, 2))),
            percent_change=Decimal(str(round(percent_change, 2))),
            timestamp=timestamp,
        )