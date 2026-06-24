"""Tests for technical indicator endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_indicators_btc(client: AsyncClient):
    """Test getting technical indicators for BTC."""
    response = await client.get("/api/v1/indicators/BTC")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"
    assert "rsi" in data
    assert "macd" in data
    assert "ema20" in data
    assert "ema50" in data
    assert "ema200" in data
    assert "sma20" in data
    assert "avg_volume" in data
    assert "percent_change" in data
    assert "timestamp" in data

    # Verify RSI is within valid range
    rsi = float(data["rsi"])
    assert 0 <= rsi <= 100, f"RSI {rsi} is out of range [0, 100]"


@pytest.mark.asyncio
async def test_get_indicators_eth(client: AsyncClient):
    """Test getting technical indicators for ETH."""
    response = await client.get("/api/v1/indicators/ETH")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "ETH"
    assert "rsi" in data
    assert "macd" in data
    assert "ema20" in data
    assert "ema50" in data
    assert "ema200" in data
    assert "sma20" in data
    assert "avg_volume" in data
    assert "percent_change" in data
    assert "timestamp" in data

    # Verify RSI is within valid range
    rsi = float(data["rsi"])
    assert 0 <= rsi <= 100, f"RSI {rsi} is out of range [0, 100]"


@pytest.mark.asyncio
async def test_get_indicators_sol(client: AsyncClient):
    """Test getting technical indicators for SOL."""
    response = await client.get("/api/v1/indicators/SOL")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "SOL"
    assert "rsi" in data
    assert "macd" in data
    assert "ema20" in data
    assert "ema50" in data
    assert "ema200" in data
    assert "sma20" in data
    assert "avg_volume" in data
    assert "percent_change" in data
    assert "timestamp" in data

    # Verify RSI is within valid range
    rsi = float(data["rsi"])
    assert 0 <= rsi <= 100, f"RSI {rsi} is out of range [0, 100]"


@pytest.mark.asyncio
async def test_get_indicators_invalid_symbol(client: AsyncClient):
    """Test getting technical indicators for an invalid symbol."""
    response = await client.get("/api/v1/indicators/INVALID")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "INVALID" in data["detail"] or "not available" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_indicators_lowercase(client: AsyncClient):
    """Test getting indicators with lowercase symbol (should work)."""
    response = await client.get("/api/v1/indicators/btc")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"