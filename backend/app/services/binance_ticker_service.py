"""Binance ticker service for current market data."""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

import httpx

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class BinanceTickerService:
    """Service for fetching current ticker data from Binance public API.

    Uses Binance public 24hr ticker endpoint to get current prices,
    volume, and price changes. No API key required.

    Note: Binance does not provide market capitalization data.
    """

    # Binance API base URL for 24hr ticker
    BASE_URL = "https://api.binance.com/api/v3/ticker/24hr"

    # Symbol mapping: our symbols -> Binance symbols
    BINANCE_SYMBOL_MAP: Dict[str, str] = {
        "BTC": "BTCUSDT",
        "ETH": "ETHUSDT",
        "SOL": "SOLUSDT",
    }

    # Supported symbols
    SUPPORTED_SYMBOLS = {"BTC", "ETH", "SOL"}

    def __init__(self, timeout: float = 10.0, base_url: Optional[str] = None):
        """Initialize Binance ticker service.

        Args:
            timeout: Request timeout in seconds
            base_url: Override base URL for testing
        """
        self.timeout = timeout
        self.base_url = base_url or self.BASE_URL

    async def fetch_ticker_data(
        self, symbols: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Fetch ticker data for specified symbols.

        Args:
            symbols: List of symbols to fetch. If None, fetches all supported.

        Returns:
            Dict mapping symbol to ticker data with keys:
            - price: float
            - volume_24h: float
            - change_24h: float
            - timestamp: datetime
            - source: "binance_ticker"
            - market_cap: None (not available from Binance)
        """
        symbols_to_fetch = symbols or list(self.SUPPORTED_SYMBOLS)
        binance_symbols = [
            self.BINANCE_SYMBOL_MAP.get(s.upper())
            for s in symbols_to_fetch
            if s.upper() in self.SUPPORTED_SYMBOLS
        ]

        if not binance_symbols:
            logger.warning("No valid symbols to fetch from Binance")
            return {}

        logger.info(f"Fetching Binance ticker data for {binance_symbols}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Fetch all symbols at once if possible, or individually
                results: Dict[str, Dict[str, Any]] = {}

                for our_symbol, binance_symbol in zip(
                    [s for s in symbols_to_fetch if s.upper() in self.SUPPORTED_SYMBOLS],
                    binance_symbols,
                ):
                    params = {"symbol": binance_symbol}
                    logger.debug(f"Fetching ticker for {binance_symbol}")

                    response = await client.get(self.base_url, params=params)

                    if response.status_code == 200:
                        data = response.json()
                        parsed = self._parse_ticker_data(data, our_symbol.upper())
                        if parsed:
                            results[our_symbol.upper()] = parsed
                    else:
                        logger.warning(
                            f"Binance ticker returned {response.status_code} "
                            f"for {binance_symbol}: {response.text[:100]}"
                        )

                return results

        except httpx.TimeoutException as e:
            logger.error(f"Binance ticker timeout after {self.timeout}s: {e}")
            return {}
        except httpx.RequestError as e:
            logger.error(f"Binance ticker request error: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error fetching Binance ticker: {e}")
            return {}

    def _parse_ticker_data(
        self, data: Dict[str, Any], symbol: str
    ) -> Optional[Dict[str, Any]]:
        """Parse Binance ticker response.

        Args:
            data: Raw ticker data from Binance
            symbol: Our symbol string (e.g., "BTC")

        Returns:
            Parsed data dict or None if parsing fails
        """
        try:
            last_price = float(data.get("lastPrice", 0))
            quote_volume = float(data.get("quoteVolume", 0))
            price_change_percent = float(data.get("priceChangePercent", 0))

            # Use closeTime if available, otherwise current time
            close_time = data.get("closeTime")
            if close_time:
                timestamp = datetime.fromtimestamp(close_time / 1000, tz=timezone.utc)
            else:
                timestamp = datetime.now(timezone.utc)

            return {
                "price": last_price,
                "volume_24h": quote_volume,
                "change_24h": price_change_percent,
                "timestamp": timestamp,
                "source": "binance_ticker",
                "market_cap": None,  # Not available from Binance
            }
        except (TypeError, ValueError, KeyError) as e:
            logger.warning(f"Error parsing Binance ticker data for {symbol}: {e}")
            return None

    def get_missing_symbols(
        self, fetched_data: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Get symbols that were not returned by Binance.

        Args:
            fetched_data: Data returned from fetch_ticker_data

        Returns:
            List of symbol strings missing from the response
        """
        fetched_symbols = set(fetched_data.keys())
        return [s for s in self.SUPPORTED_SYMBOLS if s not in fetched_symbols]