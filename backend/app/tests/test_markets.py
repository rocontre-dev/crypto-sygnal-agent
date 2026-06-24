"""Tests for market data endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_all_markets(client: AsyncClient):
    """Test getting all market data."""
    response = await client.get("/api/v1/markets")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data
    assert data["count"] == 3
    assert len(data["data"]) == 3

    # Check that all symbols are present
    symbols = [item["symbol"] for item in data["data"]]
    assert "BTC" in symbols
    assert "ETH" in symbols
    assert "SOL" in symbols


@pytest.mark.asyncio
async def test_get_market_by_symbol_btc(client: AsyncClient):
    """Test getting BTC market data."""
    response = await client.get("/api/v1/markets/BTC")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"
    assert "price" in data
    assert "market_cap" in data
    assert "volume_24h" in data
    assert "change_24h" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_get_market_by_symbol_eth(client: AsyncClient):
    """Test getting ETH market data."""
    response = await client.get("/api/v1/markets/ETH")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "ETH"
    assert "price" in data
    assert "market_cap" in data
    assert "volume_24h" in data
    assert "change_24h" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_get_market_by_symbol_sol(client: AsyncClient):
    """Test getting SOL market data."""
    response = await client.get("/api/v1/markets/SOL")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "SOL"
    assert "price" in data
    assert "market_cap" in data
    assert "volume_24h" in data
    assert "change_24h" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_get_market_by_symbol_invalid(client: AsyncClient):
    """Test getting market data for an invalid symbol."""
    response = await client.get("/api/v1/markets/INVALID")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "INVALID" in data["detail"] or "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_market_by_symbol_lowercase(client: AsyncClient):
    """Test getting market data with lowercase symbol (should work)."""
    response = await client.get("/api/v1/markets/btc")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"