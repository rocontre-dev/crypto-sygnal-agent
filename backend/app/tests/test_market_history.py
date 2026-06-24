"""Tests for market history endpoints."""

import pytest
from httpx import AsyncClient

from app.services.market_history_service import MarketHistoryService


@pytest.mark.asyncio
async def test_get_history_btc_1d(client: AsyncClient):
    """Test getting BTC historical data with 1d timeframe."""
    response = await client.get("/api/v1/history/BTC?timeframe=1d")
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
    assert data["volume_available"] is True
    assert data["source"] == "binance_klines"
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
        assert candle["volume"] is not None  # Volume should NOT be null
        assert isinstance(candle["volume"], (int, float))


@pytest.mark.asyncio
async def test_get_history_btc_4h(client: AsyncClient):
    """Test getting BTC historical data with 4h timeframe."""
    response = await client.get("/api/v1/history/BTC?timeframe=4h")
    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == "BTC"
    assert data["timeframe"] == "4h"
    assert data["volume_available"] is True
    assert data["source"] == "binance_klines"
    assert isinstance(data["candles"], list)

    # Check that volume is not null
    if data["count"] > 0:
        candle = data["candles"][0]
        assert candle["volume"] is not None


@pytest.mark.asyncio
async def test_get_history_eth_1d(client: AsyncClient):
    """Test getting ETH historical data."""
    response = await client.get("/api/v1/history/ETH?timeframe=1d")
    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == "ETH"
    assert data["timeframe"] == "1d"
    assert data["volume_available"] is True
    assert data["source"] == "binance_klines"
    assert isinstance(data["candles"], list)


@pytest.mark.asyncio
async def test_get_history_sol_4h(client: AsyncClient):
    """Test getting SOL historical data with 4h timeframe."""
    response = await client.get("/api/v1/history/SOL?timeframe=4h")
    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == "SOL"
    assert data["timeframe"] == "4h"
    assert data["volume_available"] is True
    assert data["source"] == "binance_klines"
    assert isinstance(data["candles"], list)


@pytest.mark.asyncio
async def test_get_history_invalid_symbol(client: AsyncClient):
    """Test getting history for an invalid symbol returns 404."""
    response = await client.get("/api/v1/history/INVALID")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "INVALID" in data["detail"] or "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_history_invalid_timeframe(client: AsyncClient):
    """Test getting history with unsupported timeframe returns 400."""
    response = await client.get("/api/v1/history/BTC?timeframe=1h")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "1h" in data["detail"] or "not supported" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_history_lowercase_symbol(client: AsyncClient):
    """Test getting history with lowercase symbol works."""
    response = await client.get("/api/v1/history/btc?timeframe=1d")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"


@pytest.mark.asyncio
async def test_get_history_candle_ordering(client: AsyncClient):
    """Test that candles are ordered newest first."""
    response = await client.get("/api/v1/history/BTC?timeframe=1d")
    assert response.status_code == 200
    data = response.json()

    if data["count"] >= 2:
        # First candle should be newer than second candle
        first_timestamp = data["candles"][0]["timestamp"]
        second_timestamp = data["candles"][1]["timestamp"]
        assert first_timestamp >= second_timestamp


@pytest.mark.asyncio
async def test_get_history_volume_not_null(client: AsyncClient):
    """Test that volume is not null for all candles."""
    response = await client.get("/api/v1/history/BTC?timeframe=1d")
    assert response.status_code == 200
    data = response.json()

    for candle in data["candles"]:
        assert candle["volume"] is not None, "Volume should not be null"
        assert isinstance(candle["volume"], (int, float))


@pytest.mark.asyncio
async def test_get_history_default_timeframe(client: AsyncClient):
    """Test that default timeframe is 1d."""
    response = await client.get("/api/v1/history/BTC")
    assert response.status_code == 200
    data = response.json()
    assert data["timeframe"] == "1d"


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
        """Test timeframe validation with valid timeframes."""
        service = MarketHistoryService()
        assert service._validate_timeframe("1d") == "1d"
        assert service._validate_timeframe("4h") == "4h"

    def test_validate_timeframe_invalid(self):
        """Test timeframe validation with invalid timeframes."""
        service = MarketHistoryService()
        with pytest.raises(ValueError, match="not supported"):
            service._validate_timeframe("1h")
        with pytest.raises(ValueError, match="not supported"):
            service._validate_timeframe("1w")

    def test_binance_symbol_mapping(self):
        """Test Binance symbol mapping."""
        service = MarketHistoryService()
        assert service.BINANCE_SYMBOL_MAP["BTC"] == "BTCUSDT"
        assert service.BINANCE_SYMBOL_MAP["ETH"] == "ETHUSDT"
        assert service.BINANCE_SYMBOL_MAP["SOL"] == "SOLUSDT"

    def test_supported_timeframes(self):
        """Test supported timeframes include 1d and 4h."""
        service = MarketHistoryService()
        assert "1d" in service.SUPPORTED_TIMEFRAMES
        assert "4h" in service.SUPPORTED_TIMEFRAMES

    def test_limit_map(self):
        """Test limit map for timeframes."""
        service = MarketHistoryService()
        assert service.LIMIT_MAP["1d"] == 365
        assert service.LIMIT_MAP["4h"] == 500

    def test_cache_operations(self):
        """Test cache get, set, and expiry."""
        from datetime import datetime, timezone
        from app.domain.entities.market_history import OHLCCandle
        from app.domain.enums.crypto_symbol import CryptoSymbol
        from app.domain.enums.timeframe import Timeframe

        service = MarketHistoryService(cache_ttl=1)
        now = datetime.now(timezone.utc)

        # Create test candle with volume
        test_candle = OHLCCandle(
            timestamp=now,
            open=50000,
            high=51000,
            low=49000,
            close=50500,
            volume=1234.56,
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
        assert cached[0].volume == 1234.56

        # Check is_valid
        assert service.cache.is_valid("BTC", "1d") is True

    def test_build_response_has_volume(self):
        """Test response building includes volume."""
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
                volume=1234.56,
                symbol=CryptoSymbol.BTC,
                timeframe=Timeframe.ONE_DAY,
            )
        ]

        response = service._build_response("BTC", "1d", candles)

        assert response.symbol == "BTC"
        assert response.timeframe == "1d"
        assert response.count == 1
        assert response.volume_available is True
        assert response.source == "binance_klines"
        assert len(response.candles) == 1
        assert response.candles[0].volume is not None
        assert response.candles[0].volume == 1234.56

    def test_base_url_is_binance(self):
        """Test that base URL points to Binance."""
        service = MarketHistoryService()
        assert service.base_url == "https://api.binance.com/api/v3/klines"