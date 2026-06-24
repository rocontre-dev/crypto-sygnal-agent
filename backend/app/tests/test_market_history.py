"""Tests for market history endpoints."""

import pytest
from httpx import AsyncClient

from app.services.market_history_service import MarketHistoryService


@pytest.mark.asyncio
async def test_get_history_btc(client: AsyncClient):
    """Test getting BTC historical data."""
    response = await client.get("/api/v1/history/BTC")
    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "symbol" in data
    assert "timeframe" in data
    assert "count" in data
    assert "volume_available" in data
    assert "source" in data
    assert "candles" in data

    # Check values
    assert data["symbol"] == "BTC"
    assert data["timeframe"] == "1d"
    assert data["volume_available"] is False
    assert data["source"] == "coingecko_ohlc"
    assert isinstance(data["candles"], list)
    assert data["count"] == len(data["candles"])

    # Check candle structure if we have candles
    if data["count"] > 0:
        candle = data["candles"][0]
        assert "timestamp" in candle
        assert "open" in candle
        assert "high" in candle
        assert "low" in candle
        assert "close" in candle
        assert "volume" in candle
        assert candle["volume"] is None  # Volume is always null


@pytest.mark.asyncio
async def test_get_history_eth(client: AsyncClient):
    """Test getting ETH historical data."""
    response = await client.get("/api/v1/history/ETH")
    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == "ETH"
    assert data["timeframe"] == "1d"
    assert data["volume_available"] is False
    assert data["source"] == "coingecko_ohlc"
    assert isinstance(data["candles"], list)


@pytest.mark.asyncio
async def test_get_history_sol(client: AsyncClient):
    """Test getting SOL historical data."""
    response = await client.get("/api/v1/history/SOL")
    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == "SOL"
    assert data["timeframe"] == "1d"
    assert data["volume_available"] is False
    assert data["source"] == "coingecko_ohlc"
    assert isinstance(data["candles"], list)


@pytest.mark.asyncio
async def test_get_history_with_explicit_timeframe(client: AsyncClient):
    """Test getting history with explicit 1d timeframe parameter."""
    response = await client.get("/api/v1/history/BTC?timeframe=1d")
    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == "BTC"
    assert data["timeframe"] == "1d"


@pytest.mark.asyncio
async def test_get_history_invalid_symbol(client: AsyncClient):
    """Test getting history for an invalid symbol returns 404."""
    response = await client.get("/api/v1/history/INVALID")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "INVALID" in data["detail"] or "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_history_invalid_timeframe_4h(client: AsyncClient):
    """Test getting history with 4h timeframe returns 400 with clear message."""
    response = await client.get("/api/v1/history/BTC?timeframe=4h")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    detail = data["detail"].lower()
    # Check for informative message about 4h not being available
    assert "4h" in detail or "not available" in detail or "coingecko" in detail


@pytest.mark.asyncio
async def test_get_history_invalid_timeframe_other(client: AsyncClient):
    """Test getting history with unsupported timeframe returns 400."""
    response = await client.get("/api/v1/history/BTC?timeframe=1h")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_get_history_lowercase_symbol(client: AsyncClient):
    """Test getting history with lowercase symbol works."""
    response = await client.get("/api/v1/history/btc")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"


@pytest.mark.asyncio
async def test_get_history_candle_ordering(client: AsyncClient):
    """Test that candles are ordered newest first."""
    response = await client.get("/api/v1/history/BTC")
    assert response.status_code == 200
    data = response.json()

    if data["count"] >= 2:
        # First candle should be newer than second candle
        first_timestamp = data["candles"][0]["timestamp"]
        second_timestamp = data["candles"][1]["timestamp"]
        assert first_timestamp >= second_timestamp


@pytest.mark.asyncio
async def test_get_history_volume_always_null(client: AsyncClient):
    """Test that volume is always null for all candles."""
    response = await client.get("/api/v1/history/BTC")
    assert response.status_code == 200
    data = response.json()

    for candle in data["candles"]:
        assert candle["volume"] is None, "Volume should always be null"


class TestMarketHistoryService:
    """Unit tests for MarketHistoryService."""

    def test_validate_symbol_valid(self):
        """Test symbol validation with valid symbols."""
        service = MarketHistoryService()
        assert service._validate_symbol("BTC") == "BTC"
        assert service._validate_symbol("btc") == "BTC"
        assert service._validate_symbol("ETH") == "ETH"
        assert service._validate_symbol("SOL") == "SOL"

    def test_validate_symbol_invalid(self):
        """Test symbol validation with invalid symbols."""
        service = MarketHistoryService()
        with pytest.raises(ValueError, match="Unsupported symbol"):
            service._validate_symbol("INVALID")
        with pytest.raises(ValueError, match="Unsupported symbol"):
            service._validate_symbol("DOGE")

    def test_validate_timeframe_valid(self):
        """Test timeframe validation with valid timeframe."""
        service = MarketHistoryService()
        assert service._validate_timeframe("1d") == "1d"

    def test_validate_timeframe_invalid(self):
        """Test timeframe validation with invalid timeframes."""
        service = MarketHistoryService()
        with pytest.raises(ValueError, match="not available"):
            service._validate_timeframe("4h")
        with pytest.raises(ValueError, match="not available"):
            service._validate_timeframe("1h")
        with pytest.raises(ValueError, match="not available"):
            service._validate_timeframe("1w")

    def test_cache_operations(self):
        """Test cache get, set, and expiry."""
        from datetime import datetime, timezone, timedelta
        from app.domain.entities.market_history import OHLCCandle
        from app.domain.enums.crypto_symbol import CryptoSymbol
        from app.domain.enums.timeframe import Timeframe

        service = MarketHistoryService(cache_ttl=1)
        now = datetime.now(timezone.utc)

        # Create test candle
        test_candle = OHLCCandle(
            timestamp=now,
            open=50000,
            high=51000,
            low=49000,
            close=50500,
            symbol=CryptoSymbol.BTC,
            timeframe=Timeframe.ONE_DAY,
        )

        # Cache miss initially
        assert service.cache.get("BTC", "1d") is None

        # Set cache
        service.cache.set("BTC", "1d", [test_candle])

        # Cache hit
        cached = service.cache.get("BTC", "1d")
        assert cached is not None
        assert len(cached) == 1
        assert cached[0].close == 50500

        # Check is_valid
        assert service.cache.is_valid("BTC", "1d") is True

    def test_build_response(self):
        """Test response building."""
        from datetime import datetime, timezone
        from app.domain.entities.market_history import OHLCCandle
        from app.domain.enums.crypto_symbol import CryptoSymbol
        from app.domain.enums.timeframe import Timeframe

        service = MarketHistoryService()
        now = datetime.now(timezone.utc)

        candles = [
            OHLCCandle(
                timestamp=now,
                open=50000,
                high=51000,
                low=49000,
                close=50500,
                symbol=CryptoSymbol.BTC,
                timeframe=Timeframe.ONE_DAY,
            )
        ]

        response = service._build_response("BTC", "1d", candles)

        assert response.symbol == "BTC"
        assert response.timeframe == "1d"
        assert response.count == 1
        assert response.volume_available is False
        assert response.source == "coingecko_ohlc"
        assert len(response.candles) == 1
        assert response.candles[0].volume is None