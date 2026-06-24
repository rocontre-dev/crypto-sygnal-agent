"""Market data SQLAlchemy model."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime, Index, Integer, Numeric, String

from .base import Base


class MarketData(Base):
    """Market data database model.

    Stores cryptocurrency market data including price, market cap,
    volume, and price changes.

    Attributes:
        id: Primary key
        symbol: Cryptocurrency symbol (BTC, ETH, SOL)
        price: Current price in USD
        market_cap: Market capitalization in USD
        volume_24h: Trading volume in the last 24 hours
        change_24h: Price change percentage in the last 24 hours
        timestamp: When this data was recorded
        created_at: Record creation timestamp
        updated_at: Record last update timestamp
    """

    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, index=True)
    price = Column(Numeric(18, 8), nullable=False)
    market_cap = Column(Numeric(18, 2), nullable=False)
    volume_24h = Column(Numeric(18, 2), nullable=False)
    change_24h = Column(Numeric(8, 4), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_market_data_symbol_timestamp", "symbol", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<MarketData(symbol={self.symbol}, price={self.price})>"