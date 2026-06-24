"""Market data service."""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from app.domain.entities.market_data import MarketDataEntity
from app.domain.enums.crypto_symbol import CryptoSymbol
from app.repositories.market_data_repository import MarketDataRepository
from app.schemas.market_data import MarketDataResponse
from app.services.coingecko_service import CoinGeckoService

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class MarketDataService:
    """Service for market data business logic.

    Provides methods for retrieving and processing market data.
    Uses real data from CoinGecko API with fallback to mock data.
    """

    def __init__(
        self,
        repository: MarketDataRepository,
        coingecko_service: Optional[CoinGeckoService] = None,
    ):
        """Initialize service with repository.

        Args:
            repository: Market data repository instance
            coingecko_service: Optional CoinGecko service instance for real data
        """
        self.repository = repository
        self.coingecko_service = coingecko_service or CoinGeckoService()

    async def get_all_market_data(self) -> List[MarketDataResponse]:
        """Get all market data.

        Fetches real data from CoinGecko API. Falls back to mock data
        for any symbols not returned by CoinGecko.

        Returns:
            List of market data responses for all supported symbols
        """
        # Try to fetch real data from CoinGecko
        coingecko_data = await self.coingecko_service.fetch_market_data()
        missing_symbols = self.coingecko_service.get_missing_symbols(
            coingecko_data
        )

        # Log warning if we need to use fallback for any symbols
        if missing_symbols:
            logger.warning(
                f"CoinGecko missing data for {missing_symbols}, "
                f"using mock data as fallback"
            )

        # Build result list from CoinGecko data
        result: List[MarketDataEntity] = []
        id_counter = 1

        for symbol_str, data in coingecko_data.items():
            try:
                symbol = CryptoSymbol(symbol_str)
            except ValueError:
                continue

            result.append(
                MarketDataEntity(
                    id=id_counter,
                    symbol=symbol,
                    price=Decimal(str(data["price"])),
                    market_cap=Decimal(str(data["market_cap"])),
                    volume_24h=Decimal(str(data["volume_24h"])),
                    change_24h=Decimal(str(data["change_24h"])),
                    timestamp=data["last_updated"],
                )
            )
            id_counter += 1

        # Add mock data for missing symbols
        if missing_symbols:
            mock_data = self._generate_mock_data_for_symbols(missing_symbols)
            for data in mock_data:
                data.id = id_counter
                result.append(data)
                id_counter += 1

        return [self._entity_to_response(data) for data in result]

    async def get_market_data_by_symbol(
        self, symbol: str
    ) -> Optional[MarketDataResponse]:
        """Get market data for a specific symbol.

        Fetches real data from CoinGecko API. Falls back to mock data
        if CoinGecko doesn't have data for the requested symbol.

        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH', 'SOL')

        Returns:
            Market data response or None if symbol is not supported
        """
        symbol_upper = symbol.upper()

        # Validate symbol is supported
        try:
            symbol_enum = CryptoSymbol(symbol_upper)
        except ValueError:
            return None

        # Try to fetch real data from CoinGecko
        coingecko_data = await self.coingecko_service.fetch_market_data()

        if symbol_upper in coingecko_data:
            data = coingecko_data[symbol_upper]
            entity = MarketDataEntity(
                id=1,
                symbol=symbol_enum,
                price=Decimal(str(data["price"])),
                market_cap=Decimal(str(data["market_cap"])),
                volume_24h=Decimal(str(data["volume_24h"])),
                change_24h=Decimal(str(data["change_24h"])),
                timestamp=data["last_updated"],
            )
            return self._entity_to_response(entity)

        # Fallback to mock data
        logger.warning(
            f"CoinGecko missing data for {symbol_upper}, "
            f"using mock data as fallback"
        )
        mock_data = self._generate_mock_data_for_symbols([symbol_upper])
        if mock_data:
            return self._entity_to_response(mock_data[0])

        return None

    def _generate_mock_data(self) -> List[MarketDataEntity]:
        """Generate mock market data with current timestamp.

        Returns:
            List of MarketDataEntity with mock values for all symbols
        """
        return self._generate_mock_data_for_symbols(
            ["BTC", "ETH", "SOL"]
        )

    def _generate_mock_data_for_symbols(
        self, symbols: List[str]
    ) -> List[MarketDataEntity]:
        """Generate mock market data for specific symbols.

        Args:
            symbols: List of symbol strings (e.g., ['BTC', 'ETH'])

        Returns:
            List of MarketDataEntity with mock values for the requested symbols
        """
        now = datetime.now(timezone.utc)

        mock_values = {
            "BTC": {
                "price": Decimal("67500.00"),
                "market_cap": Decimal("1300000000000.00"),
                "volume_24h": Decimal("25000000000.00"),
                "change_24h": Decimal("2.50"),
            },
            "ETH": {
                "price": Decimal("3500.00"),
                "market_cap": Decimal("420000000000.00"),
                "volume_24h": Decimal("12000000000.00"),
                "change_24h": Decimal("-1.20"),
            },
            "SOL": {
                "price": Decimal("150.00"),
                "market_cap": Decimal("65000000000.00"),
                "volume_24h": Decimal("3000000000.00"),
                "change_24h": Decimal("5.80"),
            },
        }

        result = []
        for i, sym in enumerate(symbols):
            if sym not in mock_values:
                continue
            try:
                symbol_enum = CryptoSymbol(sym)
            except ValueError:
                continue

            values = mock_values[sym]
            result.append(
                MarketDataEntity(
                    id=i + 1,
                    symbol=symbol_enum,
                    price=values["price"],
                    market_cap=values["market_cap"],
                    volume_24h=values["volume_24h"],
                    change_24h=values["change_24h"],
                    timestamp=now,
                )
            )

        return result

    @staticmethod
    def _entity_to_response(entity: MarketDataEntity) -> MarketDataResponse:
        """Convert domain entity to response schema.

        Args:
            entity: MarketDataEntity instance

        Returns:
            MarketDataResponse instance
        """
        return MarketDataResponse(
            id=entity.id,
            symbol=entity.symbol_str,
            price=entity.price,
            market_cap=entity.market_cap,
            volume_24h=entity.volume_24h,
            change_24h=entity.change_24h,
            timestamp=entity.timestamp,
        )