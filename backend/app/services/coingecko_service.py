"""CoinGecko market data service."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class CoinGeckoService:
    """Service for fetching market data from CoinGecko API.

    This service provides methods to retrieve real-time cryptocurrency
    market data from the CoinGecko API v3.
    """

    # CoinGecko API base URL
    BASE_URL = "https://api.coingecko.com/api/v3"

    # Mapping from CoinGecko coin IDs to our symbols
    COIN_ID_TO_SYMBOL: Dict[str, str] = {
        "bitcoin": "BTC",
        "ethereum": "ETH",
        "solana": "SOL",
    }

    # Our supported symbols
    SUPPORTED_SYMBOLS = {"BTC", "ETH", "SOL"}

    def __init__(self, timeout: float = 5.0, base_url: Optional[str] = None):
        """Initialize CoinGecko service.

        Args:
            timeout: Request timeout in seconds (default: 5.0)
            base_url: Override base URL for testing purposes
        """
        self.timeout = timeout
        self.base_url = base_url or self.BASE_URL

    async def fetch_market_data(self) -> Dict[str, Dict[str, Any]]:
        """Fetch market data for all supported cryptocurrencies.

        Returns:
            Dictionary mapping symbol (e.g., 'BTC') to market data dict containing:
                - price: Current price in USD (float)
                - market_cap: Market capitalization in USD (float)
                - volume_24h: 24-hour trading volume in USD (float)
                - change_24h: 24-hour price change percentage (float)
                - last_updated: Last update timestamp (datetime)

            If CoinGecko fails, returns an empty dictionary.
            Partial data may be returned if only some symbols are available.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/coins/markets",
                    params={
                        "vs_currency": "usd",
                        "ids": "bitcoin,ethereum,solana",
                        "order": "market_cap_desc",
                        "per_page": 3,
                        "page": 1,
                        "sparkline": "false",
                        "price_change_percentage": "24h",
                    },
                )

                if response.status_code != 200:
                    logger.warning(
                        f"CoinGecko API returned status {response.status_code}"
                    )
                    return {}

                data = response.json()
                return self._parse_response(data)

        except httpx.TimeoutException as e:
            logger.warning(f"CoinGecko API timeout: {e}")
            return {}
        except httpx.RequestError as e:
            logger.warning(f"CoinGecko API request error: {e}")
            return {}
        except Exception as e:
            logger.warning(f"Unexpected error fetching from CoinGecko: {e}")
            return {}

    def _parse_response(
        self, data: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Parse CoinGecko API response into our format.

        Args:
            data: List of coin data from CoinGecko API

        Returns:
            Dictionary mapping our symbols to parsed market data
        """
        result: Dict[str, Dict[str, Any]] = {}

        for coin in data:
            coin_id = coin.get("id", "").lower()
            symbol = self.COIN_ID_TO_SYMBOL.get(coin_id)

            if symbol is None:
                # Skip coins we don't support
                continue

            try:
                # Parse last_updated timestamp
                last_updated_str = coin.get("last_updated")
                last_updated = None
                if last_updated_str:
                    try:
                        last_updated = datetime.fromisoformat(
                            last_updated_str.replace("Z", "+00:00")
                        )
                    except (ValueError, AttributeError):
                        last_updated = datetime.now(timezone.utc)

                result[symbol] = {
                    "price": float(coin.get("current_price", 0) or 0),
                    "market_cap": float(coin.get("market_cap", 0) or 0),
                    "volume_24h": float(coin.get("total_volume", 0) or 0),
                    "change_24h": float(
                        coin.get("price_change_percentage_24h", 0) or 0
                    ),
                    "last_updated": last_updated or datetime.now(timezone.utc),
                }

            except (TypeError, ValueError) as e:
                logger.warning(
                    f"Error parsing CoinGecko data for {coin_id}: {e}"
                )
                continue

        return result

    def get_missing_symbols(
        self, fetched_data: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Get list of symbols not present in fetched data.

        Args:
            fetched_data: Data returned from fetch_market_data()

        Returns:
            List of symbols that need fallback mock data
        """
        return [
            symbol
            for symbol in self.SUPPORTED_SYMBOLS
            if symbol not in fetched_data
        ]