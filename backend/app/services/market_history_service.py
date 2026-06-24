"""Market history service for fetching and caching OHLC data."""

import logging
import time
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

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
        self._cache: Dict[str, Dict[str, Any]] = {}
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
    """Service for fetching and managing historical OHLC market data.

    This service fetches real historical OHLC data from CoinGecko API
    with caching support and graceful fallback to cached data.

    Note: CoinGecko's free OHLC endpoint provides open, high, low, close
    prices but does NOT provide volume data. Volume is always None.

    Supported timeframes:
    - 1d (daily): Last 365 days

    Pending timeframes:
    - 4h (4-hour): Requires alternative data provider (Binance, Coinbase, etc.)
    """

    # CoinGecko API base URL
    BASE_URL = "https://api.coingecko.com/api/v3"

    # Mapping from our symbols to CoinGecko coin IDs
    COIN_ID_MAP: Dict[str, str] = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
    }

    # Supported symbols
    SUPPORTED_SYMBOLS = {"BTC", "ETH", "SOL"}

    # Supported timeframes (only 1d for now)
    SUPPORTED_TIMEFRAMES = {"1d"}

    # Days to fetch for each timeframe
    DAYS_MAP: Dict[str, int] = {
        "1d": 365,
    }

    def __init__(
        self,
        timeout: float = 10.0,
        cache_ttl: Optional[int] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize market history service.

        Args:
            timeout: Request timeout in seconds
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
                f"Timeframe '{timeframe}' is not available from CoinGecko OHLC "
                f"free endpoint yet. Supported timeframes: {', '.join(sorted(self.SUPPORTED_TIMEFRAMES))}. "
                f"4h timeframe support is pending and may require Binance, Coinbase, "
                f"or another OHLCV provider."
            )
        return timeframe

    def _parse_ohlc_data(
        self, data: List[List[Any]], symbol: CryptoSymbol, timeframe: Timeframe
    ) -> List[OHLCCandle]:
        """Parse CoinGecko OHLC response into candle entities.

        Args:
            data: Raw OHLC data from CoinGecko API
            symbol: Cryptocurrency symbol
            timeframe: Candle timeframe

        Returns:
            List of OHLCCandle entities
        """
        candles = []
        for ohlc in data:
            if len(ohlc) < 5:
                continue

            try:
                # CoinGecko returns: [timestamp_ms, open, high, low, close]
                timestamp_ms = ohlc[0]
                timestamp = datetime.fromtimestamp(
                    timestamp_ms / 1000, tz=timezone.utc
                )

                candle = OHLCCandle(
                    timestamp=timestamp,
                    open=Decimal(str(ohlc[1])),
                    high=Decimal(str(ohlc[2])),
                    low=Decimal(str(ohlc[3])),
                    close=Decimal(str(ohlc[4])),
                    symbol=symbol,
                    timeframe=timeframe,
                    volume=None,  # CoinGecko OHLC does not provide volume
                )
                candles.append(candle)
            except (TypeError, ValueError, IndexError) as e:
                logger.warning(f"Error parsing OHLC data point: {e}")
                continue

        return candles

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        use_cache: bool = True,
    ) -> MarketHistoryResponse:
        """Fetch historical OHLC data for a cryptocurrency.

        This method fetches real historical data from CoinGecko API.
        It uses caching to reduce API calls and provides graceful
        fallback to cached data if the API is unavailable.

        Args:
            symbol: Cryptocurrency symbol (BTC, ETH, SOL)
            timeframe: Candle timeframe (currently only "1d" supported)
            use_cache: Whether to use cached data when available

        Returns:
            MarketHistoryResponse containing OHLC candles

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

        # Fetch from CoinGecko
        start_time = time.time()
        candles = await self._fetch_from_coingecko(symbol_upper, timeframe_enum)

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

    async def _fetch_from_coingecko(
        self, symbol: str, timeframe: Timeframe
    ) -> List[OHLCCandle]:
        """Fetch OHLC data from CoinGecko API.

        Args:
            symbol: Cryptocurrency symbol (already validated)
            timeframe: Candle timeframe

        Returns:
            List of OHLCCandle entities, or empty list on failure
        """
        coin_id = self.COIN_ID_MAP.get(symbol)
        if not coin_id:
            logger.error(f"No CoinGecko coin ID mapping for symbol: {symbol}")
            return []

        days = self.DAYS_MAP.get(timeframe.value, 365)
        
        # Build the full URL for debugging
        url = f"{self.base_url}/coins/{coin_id}/ohlc"
        params = {"vs_currency": "usd", "days": days}
        
        logger.debug(f"Fetching OHLC from CoinGecko: URL={url}, params={params}, timeout={self.timeout}s")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"Sending GET request to {url}")
                response = await client.get(url, params=params)
                
                logger.debug(f"CoinGecko response: status={response.status_code}, url={response.url}")
                
                if response.status_code != 200:
                    # Log detailed warning with special handling for rate limits
                    response_body = response.text[:200] if response.text else 'empty'
                    if response.status_code == 429:
                        logger.warning(
                            f"CoinGecko API RATE LIMIT EXCEEDED for {symbol}. "
                            f"Status: 429. URL: {response.url}. "
                            f"Message: {response_body}. "
                            f"Consider increasing cache TTL or upgrading to CoinGecko paid API."
                        )
                    else:
                        logger.warning(
                            f"CoinGecko API returned status {response.status_code} for {symbol}. "
                            f"URL: {response.url}. Response body: {response_body}"
                        )
                    return []

                # Log response size
                content_length = len(response.text) if response.text else 0
                logger.debug(f"Response body size: {content_length} bytes")
                
                try:
                    data = response.json()
                except ValueError as e:
                    logger.error(f"Failed to parse JSON response for {symbol}: {e}. Response: {response.text[:200]}")
                    return []
                
                if not isinstance(data, list):
                    logger.warning(
                        f"Unexpected response format for {symbol}: expected list, got {type(data).__name__}. "
                        f"Response: {str(data)[:200]}"
                    )
                    return []
                
                if len(data) == 0:
                    logger.warning(f"Empty OHLC data returned for {symbol}")
                    return []
                
                logger.debug(f"Received {len(data)} OHLC data points for {symbol}")

                symbol_enum = CryptoSymbol(symbol)
                return self._parse_ohlc_data(data, symbol_enum, timeframe)

        except httpx.TimeoutException as e:
            logger.error(f"CoinGecko API timeout for {symbol} after {self.timeout}s: {type(e).__name__}: {e}")
            return []
        except httpx.RequestError as e:
            logger.error(f"CoinGecko API request error for {symbol}: {type(e).__name__}: {e}. URL: {url}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching history for {symbol}: {type(e).__name__}: {e}")
            return []

    def log_debug_info(self):
        """Log debug information about the service configuration.
        
        This method can be called to output current configuration for debugging.
        """
        logger.debug(f"MarketHistoryService config: base_url={self.base_url}, timeout={self.timeout}s, cache_ttl={self.cache.ttl_seconds}s")
        logger.debug(f"Supported symbols: {self.SUPPORTED_SYMBOLS}")
        logger.debug(f"Supported timeframes: {self.SUPPORTED_TIMEFRAMES}")
        logger.debug(f"Coin ID mapping: {self.COIN_ID_MAP}")

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
                volume=None,  # Always null for CoinGecko OHLC
            )
            for c in candles
        ]

        # Sort by timestamp descending (newest first)
        candle_responses.reverse()

        return MarketHistoryResponse(
            symbol=symbol,
            timeframe=timeframe,
            count=len(candle_responses),
            volume_available=False,
            source="coingecko_ohlc",
            candles=candle_responses,
        )