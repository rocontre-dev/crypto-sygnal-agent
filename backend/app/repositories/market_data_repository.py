"""Market data repository."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market_data import MarketData


class MarketDataRepository:
    """Repository for market data access.

    Provides methods for querying market data from the database.
    """

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session.

        Args:
            db: Async database session
        """
        self.db = db

    async def get_all(self) -> List[MarketData]:
        """Get all market data entries.

        Returns:
            List of all market data records
        """
        result = await self.db.execute(select(MarketData).order_by(MarketData.symbol))
        return list(result.scalars().all())

    async def get_by_symbol(self, symbol: str) -> Optional[MarketData]:
        """Get market data by symbol.

        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH', 'SOL')

        Returns:
            Market data record or None if not found
        """
        result = await self.db.execute(
            select(MarketData).where(MarketData.symbol == symbol.upper())
        )
        return result.scalar_one_or_none()

    async def save(self, market_data: MarketData) -> MarketData:
        """Save or update market data.

        Args:
            market_data: Market data record to save

        Returns:
            Saved market data record
        """
        self.db.add(market_data)
        await self.db.flush()
        await self.db.refresh(market_data)
        return market_data