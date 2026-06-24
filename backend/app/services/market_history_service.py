"""Market history service for fetching and caching OHLCV data from Binance."""

import logging
import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.core.logging_config import get_logger
from app.domain.entities.market_history import OHLCCandle
from app.domain.enums.crypto_symbol import CryptoSymbol
from app.domain.enums.timeframe import Timeframe
from app.schemas.market_history import MarketHistoryResponse, OHLCCandleResponse

logger = get_logger(__name__)


class MarketHistoryCache:
    """In-memory cache for market history data with TTL support."""

    def __init__(self, ttl_seconds: int = 3600):
        """Initialize cache with TTL.

        Args:
            ttl_seconds: Time-to-live in seconds for cached data
        """
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, List[OHLCCandle]] = {}
        self._cached_at: Dict[str, datetime] = {}

    def _make_key(self, symbol: str, timeframe: str) -> str:
        """Create cache key from symbol and timeframe."""
        return f"{symbol}_{timeframe}"

    def get(self, symbol: str, timeframe: str) -> Optional[List[OHLCCandle]]:
        """Get cached data if valid.

        Args:
            symbol: Cryptocurrency symbol
            timeframe: Candle timeframe

        Returns:
            List of cached OHLC candles or None if expired/missing
        """
        key = self._make_key(symbol, timeframe)

        if key not in self._cache or key not in self._cached_at:
            logger.debug(f"Cache miss for {symbol}/{timeframe}")
            return None

        age = (datetime.now(timezone.utc) - self._cached_at[key]).total_seconds()
        if age > self.ttl_seconds:
            # Cache expired, remove it
            del self._cache[key]
            del self._cached_at[key]
            logger.debug(f"Cache expired for {symbol}/{timeframe}")
            return None

        logger.debug(f"Cache hit for {symbol}/{timeframe}")
        return self._cache[key]

    def set(
        self, symbol: str, timeframe: str, candles: List[OHLCCandle]
    ) -> None:
        """Store data in cache.

        Args:
            symbol: Cryptocurrency symbol
            timeframe: Candle timeframe
            candles: List of OHLC candles to cache
        """
        key = self._make_key(symbol, timeframe)
        self._cache[key] = candles
        self._cached_at[key] = datetime.now(timezone.utc)
        logger.debug(f"Cache set for {symbol}/{timeframe}: {len(candles)} candles")

    def is_valid(self, symbol: str, timeframe: str) -> bool:
        """Check if cache has valid data for the given key.

        Args:
            symbol: Cryptocurrency symbol
            timeframe: Candle timeframe

        Returns:
            True if valid cached data exists
        """
        return self.get(symbol, timeframe) is not None


class MarketHistoryService:
    """Service for fetching and managing historical OHLCV market data from Binance.

    This service fetches real historical OHLCV data from Binance public klines API
    with caching support and graceful fallback to cached data.

    Note: This service uses ONLY public market data from Binance.
    No API key is required. No trading execution or order placement.

    Supported timeframes:
    - 1d (daily): Last 365 candles
    - 4h (4-hour): Last 500 candles
    """

    # Binance API base URL for public klines
    BASE_URL = "https://api.binance.com/api/v3/klines"

    # Mapping from our symbols to Binance symbols
    BINANCE_SYMBOL_MAP: Dict[str, str] = {
        "BTC": "BTCUSDT",
        "ETH": "ETHUSDT",
        "SOL": "SOLUSDT",
    }

    # Supported symbols
    SUPPORTED_SYMBOLS = {"BTC", "ETH", "SOL"}

    # Supported timeframes (Binance intervals)
    SUPPORTED_TIMEFRAMES = {"1d", "4h"}

    # Binance interval mapping
    BINANCE_INTERVAL_MAP: Dict[str, str] = {
        "1d": "1d",
        "4h": "4h",
    }

    # Limit for each timeframe
    LIMIT_MAP: Dict[str, int] = {
        "1d": 365,
        "4h": 500,
    }

    def __init__(
        self,
        timeout: float = 10.0,
        cache_ttl: Optional[int] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize market history service.

        Args:
            timeout: Request timeout in seconds (default: 10.0)
            cache_ttl: Cache TTL in seconds (default from settings)
            base_url: Override base URL for testing purposes
        """
        self.timeout = timeout
        self.base_url = base_url or self.BASE_URL
        self.cache = MarketHistoryCache(
            cache_ttl or settings.MARKET_HISTORY_CACHE_TTL_SECONDS
        )

    def _validate_symbol(self, symbol: str) -> str:
        """Validate and normalize symbol.

        Args:
            symbol: Cryptocurrency symbol

        Returns:
            Normalized uppercase symbol

        Raises:
            ValueError: If symbol is not supported
        """
        symbol_upper = symbol.upper()
        if symbol_upper not in self.SUPPORTED_SYMBOLS:
            raise ValueError(
                f"Unsupported symbol: {symbol}. "
                f"Supported symbols: {', '.join(sorted(self.SUPPORTED_SYMBOLS))}"
            )
        return symbol_upper

    def _validate_timeframe(self, timeframe: str) -> str:
        """Validate timeframe.

        Args:
            timeframe: Timeframe string

        Returns:
            Validated timeframe

        Raises:
            ValueError: If timeframe is not supported
        """
        if timeframe not in self.SUPPORTED_TIMEFRAMES:
            raise ValueError(
                f"Timeframe '{timeframe}' is not supported. "
                f"Supported timeframes: {', '.join(sorted(self.SUPPORTED_TIMEFRAMES))}"
            )
        return timeframe

    def _parse_kline_data(
        self, data: List[List[Any]], symbol: CryptoSymbol, timeframe: Timeframe
    ) -> List[OHLCCandle]:
        """Parse Binance kline response into candle entities.

        Binance kline format:
        [
          [
            openTime,
            open,
            high,
            low,
            close,
            volume,
            closeTime,
            quoteAssetVolume,
            numberOfTrades,
            takerBuyBaseAssetVolume,
            takerBuyQuoteAssetVolume,
            ignore
          ]
        ]

        Args:
            data: Raw kline data from Binance API
            symbol: Cryptocurrency symbol
            timeframe: Candle timeframe

        Returns:
            List of OHLCCandle entities
        """
        candles = []
        for kline in data:
            if len(kline) < 6:
                continue

            try:
                # Binance returns openTime in milliseconds
                open_time_ms = kline[0]
                timestamp = datetime.fromtimestamp(
                    open_time_ms / 1000, tz=timezone.utc
                )

                candle = OHLCCandle(
                    timestamp=timestamp,
                    open=Decimal(str(kline[1])),
                    high=Decimal(str(kline[2])),
                    low=Decimal(str(kline[3])),
                    close=Decimal(str(kline[4])),
                    volume=Decimal(str(kline[5])),
                    symbol=symbol,
                    timeframe=timeframe,
                )
                candles.append(candle)
            except (TypeError, ValueError, IndexError) as e:
                logger.warning(f"Error parsing kline data point: {e}")
                continue

        return candles

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        use_cache: bool = True,
    ) -> MarketHistoryResponse:
        """Fetch historical OHLCV data for a cryptocurrency.

        This method fetches real historical data from Binance public klines API.
        It uses caching to reduce API calls and provides graceful
        fallback to cached data if the API is unavailable.

        Args:
            symbol: Cryptocurrency symbol (BTC, ETH, SOL)
            timeframe: Candle timeframe ("1d" or "4h")
            use_cache: Whether to use cached data when available

        Returns:
            MarketHistoryResponse containing OHLCV candles

        Raises:
            ValueError: If symbol or timeframe is not supported
            RuntimeError: If data cannot be fetched and no cache is available
        """
        # Validate inputs
        symbol_upper = self._validate_symbol(symbol)
        validated_timeframe = self._validate_timeframe(timeframe)

        timeframe_enum = Timeframe(validated_timeframe)
        symbol_enum = CryptoSymbol(symbol_upper)

        logger.info(f"History fetch started for {symbol_upper}/{validated_timeframe}")

        # Check cache first
        if use_cache:
            cached_candles = self.cache.get(symbol_upper, validated_timeframe)
            if cached_candles is not None:
                logger.info(f"Cache hit for {symbol_upper}/{validated_timeframe}")
                return self._build_response(symbol_upper, validated_timeframe, cached_candles)

        logger.info(f"Cache miss for {symbol_upper}/{validated_timeframe}")

        # Fetch from Binance
        start_time = time.time()
        candles = await self._fetch_from_binance(symbol_upper, timeframe_enum)

        if candles:
            fetch_time = time.time() - start_time
            logger.info(
                f"History fetch completed for {symbol_upper}: "
                f"{len(candles)} candles in {fetch_time:.2f}s"
            )

            # Cache the results
            self.cache.set(symbol_upper, validated_timeframe, candles)

            return self._build_response(symbol_upper, validated_timeframe, candles)

        # Fallback to cache if available
        if use_cache:
            fallback_candles = self.cache.get(symbol_upper, validated_timeframe)
            if fallback_candles is not None:
                logger.info(f"Fallback activated for {symbol_upper}/{validated_timeframe}")
                return self._build_response(symbol_upper, validated_timeframe, fallback_candles)

        # No data available
        logger.error(f"No data available for {symbol_upper}/{validated_timeframe}")
        raise RuntimeError(
            f"Failed to fetch history for {symbol_upper}. "
            f"No cached data available."
        )

    async def _fetch_from_binance(
        self, symbol: str, timeframe: Timeframe
    ) -> List[OHLCCandle]:
        """Fetch kline data from Binance public API.

        Args:
            symbol: Cryptocurrency symbol (already validated)
            timeframe: Candle timeframe

        Returns:
            List of OHLCCandle entities, or empty list on failure
        """
        binance_symbol = self.BINANCE_SYMBOL_MAP.get(symbol)
        if not binance_symbol:
            logger.error(f"No Binance symbol mapping for: {symbol}")
            return []

        interval = self.BINANCE_INTERVAL_MAP.get(timeframe.value)
        limit = self.LIMIT_MAP.get(timeframe.value, 500)

        url = self.base_url
        params = {
            "symbol": binance_symbol,
            "interval": interval,
            "limit": limit,
        }

        logger.debug(
            f"Fetching klines from Binance: URL={url}, "
            f"params={params}, timeout={self.timeout}s"
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"Sending GET request to {url}")
                response = await client.get(url, params=params)

                logger.debug(
                    f"Binance response: status={response.status_code}, "
                    f"url={response.url}"
                )

                # Handle error status codes
                if response.status_code != 200:
                    response_body = response.text[:200] if response.text else "empty"

                    # Specific handling for rate limit and access errors
                    if response.status_code in [429, 451, 403]:
                        status_messages = {
                            429: "Rate limit exceeded",
                            451: "Content unavailable in your region",
                            403: "Access forbidden",
                        }
                        msg = status_messages.get(response.status_code, "Unknown error")
                        logger.warning(
                            f"Binance API error ({response.status_code}): {msg}. "
                            f"Symbol: {symbol}, URL: {response.url}. "
                            f"Response: {response_body}"
                        )
                    else:
                        logger.warning(
                            f"Binance API returned status {response.status_code} "
                            f"for {symbol}. URL: {response.url}. Response: {response_body}"
                        )
                    return []

                # Log response size
                content_length = len(response.text) if response.text else 0
                logger.debug(f"Response body size: {content_length} bytes")

                try:
                    data = response.json()
                except ValueError as e:
                    logger.error(
                        f"Failed to parse JSON response for {symbol}: {e}. "
                        f"Response: {response.text[:200]}"
                    )
                    return []

                if not isinstance(data, list):
                    logger.warning(
                        f"Unexpected response format for {symbol}: "
                        f"expected list, got {type(data).__name__}. "
                        f"Response: {str(data)[:200]}"
                    )
                    return []

                if len(data) == 0:
                    logger.warning(f"Empty kline data returned for {symbol}")
                    return []

                logger.debug(f"Received {len(data)} kline data points for {symbol}")

                symbol_enum = CryptoSymbol(symbol)
                return self._parse_kline_data(data, symbol_enum, timeframe)

        except httpx.TimeoutException as e:
            logger.error(
                f"Binance API timeout for {symbol} after {self.timeout}s: "
                f"{type(e).__name__}: {e}"
            )
            return []
        except httpx.RequestError as e:
            logger.error(
                f"Binance API request error for {symbol}: "
                f"{type(e).__name__}: {e}. URL: {url}"
            )
            return []
        except Exception as e:
            logger.error(
                f"Unexpected error fetching history for {symbol}: "
                f"{type(e).__name__}: {e}"
            )
            return []

    def _build_response(
        self, symbol: str, timeframe: str, candles: List[OHLCCandle]
    ) -> MarketHistoryResponse:
        """Build MarketHistoryResponse from candles.

        Args:
            symbol: Cryptocurrency symbol
            timeframe: Candle timeframe
            candles: List of OHLCCandle entities

        Returns:
            MarketHistoryResponse
        """
        candle_responses = [
            OHLCCandleResponse(
                timestamp=c.timestamp,
                open=float(c.open),
                high=float(c.high),
                low=float(c.low),
                close=float(c.close),
                volume=float(c.volume) if c.volume is not None else None,
            )
            for c in candles
        ]

        # Sort by timestamp descending (newest first)
        candle_responses.reverse()

        return MarketHistoryResponse(
            symbol=symbol,
            timeframe=timeframe,
            count=len(candle_responses),
            volume_available=True,  # Binance provides real volume
            source="binance_klines",
            candles=candle_responses,
        )

    def log_debug_info(self):
        """Log debug information about the service configuration.

        This method can be called to output current configuration for debugging.
        """
        logger.debug(
            f"MarketHistoryService config: base_url={self.base_url}, "
            f"timeout={self.timeout}s, cache_ttl={self.cache.ttl_seconds}s"
        )
        logger.debug(f"Supported symbols: {self.SUPPORTED_SYMBOLS}")
        logger.debug(f"Supported timeframes: {self.SUPPORTED_TIMEFRAMES}")
        logger.debug(f"Binance symbol mapping: {self.BINANCE_SYMBOL_MAP}")