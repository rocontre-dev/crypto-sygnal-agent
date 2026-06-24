"""Market data service."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from app.domain.entities.market_data import MarketDataEntity
from app.domain.enums.crypto_symbol import CryptoSymbol
from app.repositories.market_data_repository import MarketDataRepository
from app.schemas.market_data import MarketDataResponse


class MarketDataService:
    """Service for market data business logic.

    Provides methods for retrieving and processing market data.
    Uses mock data for demonstration purposes.
    """

    def __init__(self, repository: MarketDataRepository):
        """Initialize service with repository.

        Args:
            repository: Market data repository instance
        """
        self.repository = repository

    async def get_all_market_data(self) -> List[MarketDataResponse]:
        """Get all market data.

        Returns:
            List of market data responses for all supported symbols
        """
        mock_data = self._generate_mock_data()
        return [self._entity_to_response(data) for data in mock_data]

    async def get_market_data_by_symbol(self, symbol: str) -> Optional[MarketDataResponse]:
        """Get market data for a specific symbol.

        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH', 'SOL')

        Returns:
            Market data response or None if symbol is not supported
        """
        mock_data = self._generate_mock_data()
        for data in mock_data:
            if data.symbol.value == symbol.upper():
                return self._entity_to_response(data)
        return None

    def _generate_mock_data(self) -> List[MarketDataEntity]:
        """Generate mock market data with current timestamp.

        Returns:
            List of MarketDataEntity with mock values
        """
        now = datetime.now(timezone.utc)

        return [
            MarketDataEntity(
                id=1,
                symbol=CryptoSymbol.BTC,
                price=Decimal("67500.00"),
                market_cap=Decimal("1300000000000.00"),
                volume_24h=Decimal("25000000000.00"),
                change_24h=Decimal("2.50"),
                timestamp=now,
            ),
            MarketDataEntity(
                id=2,
                symbol=CryptoSymbol.ETH,
                price=Decimal("3500.00"),
                market_cap=Decimal("420000000000.00"),
                volume_24h=Decimal("12000000000.00"),
                change_24h=Decimal("-1.20"),
                timestamp=now,
            ),
            MarketDataEntity(
                id=3,
                symbol=CryptoSymbol.SOL,
                price=Decimal("150.00"),
                market_cap=Decimal("65000000000.00"),
                volume_24h=Decimal("3000000000.00"),
                change_24h=Decimal("5.80"),
                timestamp=now,
            ),
        ]

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