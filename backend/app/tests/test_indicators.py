"""Tests for technical indicators endpoints."""

import pytest
from httpx import AsyncClient

from app.services.technical_indicator_service import TechnicalIndicatorService


@pytest.mark.asyncio
async def test_get_indicators_btc_1d(client: AsyncClient):
    """Test getting BTC technical indicators with 1d timeframe."""
    response = await client.get("/api/v1/indicators/BTC?timeframe=1d")
    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "symbol" in data
    assert "timeframe" in data
    assert "rsi" in data
    assert "macd" in data
    assert "ema20" in data
    assert "ema50" in data
    assert "ema200" in data
    assert "sma20" in data
    assert "atr" in data
    assert "adx" in data
    assert "avg_volume" in data
    assert "percent_change" in data
    assert "volume_available" in data
    assert "source" in data

    # Check values
    assert data["symbol"] == "BTC"
    assert data["timeframe"] == "1d"
    assert data["volume_available"] is True
    assert data["source"] == "binance_klines"

    # Check that indicators are real numbers (not null)
    assert data["rsi"] is not None
    assert data["macd"] is not None
    assert data["ema20"] is not None
    assert data["ema50"] is not None
    assert data["ema200"] is not None

    # Check that MACD signal and histogram are present
    assert "macd_signal" in data
    assert "macd_histogram" in data


@pytest.mark.asyncio
async def test_get_indicators_eth_1d(client: AsyncClient):
    """Test getting ETH technical indicators."""
    response = await client.get("/api/v1/indicators/ETH?timeframe=1d")
    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == "ETH"
    assert data["timeframe"] == "1d"
    assert data["volume_available"] is True
    assert data["source"] == "binance_klines"
    assert data["rsi"] is not None
    assert data["ema200"] is not None


@pytest.mark.asyncio
async def test_get_indicators_sol_1d(client: AsyncClient):
    """Test getting SOL technical indicators."""
    response = await client.get("/api/v1/indicators/SOL?timeframe=1d")
    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == "SOL"
    assert data["timeframe"] == "1d"
    assert data["volume_available"] is True
    assert data["source"] == "binance_klines"
    assert data["rsi"] is not None
    assert data["adx"] is not None


@pytest.mark.asyncio
async def test_get_indicators_invalid_symbol(client: AsyncClient):
    """Test getting indicators for an invalid symbol returns 404."""
    response = await client.get("/api/v1/indicators/INVALID")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "INVALID" in data["detail"] or "not available" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_indicators_4h_timeframe_returns_400(client: AsyncClient):
    """Test that 4h timeframe returns 400 (not yet enabled)."""
    response = await client.get("/api/v1/indicators/BTC?timeframe=4h")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "4h" in data["detail"] or "not enabled" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_indicators_lowercase_symbol(client: AsyncClient):
    """Test getting indicators with lowercase symbol works."""
    response = await client.get("/api/v1/indicators/btc?timeframe=1d")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"


@pytest.mark.asyncio
async def test_get_indicators_default_timeframe(client: AsyncClient):
    """Test that default timeframe is 1d."""
    response = await client.get("/api/v1/indicators/BTC")
    assert response.status_code == 200
    data = response.json()
    assert data["timeframe"] == "1d"


@pytest.mark.asyncio
async def test_get_indicators_includes_all_fields(client: AsyncClient):
    """Test that response includes all required fields."""
    response = await client.get("/api/v1/indicators/BTC?timeframe=1d")
    assert response.status_code == 200
    data = response.json()

    required_fields = [
        "symbol", "timeframe", "rsi", "macd", "macd_signal", "macd_histogram",
        "ema20", "ema50", "ema200", "sma20", "atr", "adx",
        "avg_volume", "percent_change", "volume_available", "source", "timestamp"
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"


class TestTechnicalIndicatorService:
    """Unit tests for TechnicalIndicatorService."""

    def test_supported_symbols(self):
        """Test supported symbols."""
        service = TechnicalIndicatorService()
        assert "BTC" in service.SUPPORTED_SYMBOLS
        assert "ETH" in service.SUPPORTED_SYMBOLS
        assert "SOL" in service.SUPPORTED_SYMBOLS

    def test_supported_timeframes(self):
        """Test supported timeframes."""
        service = TechnicalIndicatorService()
        assert "1d" in service.SUPPORTED_TIMEFRAMES
        assert "4h" not in service.SUPPORTED_TIMEFRAMES

    def test_validate_symbol_valid(self):
        """Test symbol validation with valid symbols."""
        service = TechnicalIndicatorService()
        # Just check that the service has the expected symbols
        assert "BTC" in service.SUPPORTED_SYMBOLS
        assert "ETH" in service.SUPPORTED_SYMBOLS
        assert "SOL" in service.SUPPORTED_SYMBOLS

    def test_validate_symbol_invalid(self):
        """Test symbol validation with invalid symbols."""
        service = TechnicalIndicatorService()
        assert "INVALID" not in service.SUPPORTED_SYMBOLS
        assert "DOGE" not in service.SUPPORTED_SYMBOLS

    def test_safe_float_with_valid_number(self):
        """Test _safe_float with valid numbers."""
        service = TechnicalIndicatorService()
        assert service._safe_float(123.45) == 123.45
        assert service._safe_float("123.45") == 123.45
        assert service._safe_float(0) == 0.0

    def test_safe_float_with_nan(self):
        """Test _safe_float with NaN returns None."""
        import numpy as np
        service = TechnicalIndicatorService()
        assert service._safe_float(float('nan')) is None
        assert service._safe_float(np.nan) is None

    def test_safe_float_with_none(self):
        """Test _safe_float with None returns None."""
        service = TechnicalIndicatorService()
        assert service._safe_float(None) is None

    def test_market_history_service_dependency(self):
        """Test that MarketHistoryService is used."""
        from app.services.market_history_service import MarketHistoryService
        service = TechnicalIndicatorService()
        assert isinstance(service.market_history_service, MarketHistoryService)