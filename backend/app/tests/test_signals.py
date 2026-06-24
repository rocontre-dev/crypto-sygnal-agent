"""Tests for trading signal endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_signal_btc(client: AsyncClient):
    """Test getting trading signal for BTC."""
    response = await client.get("/api/v1/signals/BTC")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"
    assert data["signal"] in ["ENTER", "WAIT", "REDUCE", "EXIT"]
    assert "confidence_score" in data
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert "reason" in data
    assert "stop_loss" in data
    assert "take_profit" in data
    assert "invalidation_condition" in data
    assert "timestamp" in data

    # Verify numeric types (not strings)
    assert isinstance(data["confidence_score"], (int, float)), "confidence_score must be a number"
    assert isinstance(data["stop_loss"], (int, float)), "stop_loss must be a number"
    assert isinstance(data["take_profit"], (int, float)), "take_profit must be a number"

    # Verify confidence score is between 0 and 100
    confidence = float(data["confidence_score"])
    assert 0 <= confidence <= 100, f"Confidence {confidence} is out of range [0, 100]"


@pytest.mark.asyncio
async def test_get_signal_eth(client: AsyncClient):
    """Test getting trading signal for ETH."""
    response = await client.get("/api/v1/signals/ETH")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "ETH"
    assert data["signal"] in ["ENTER", "WAIT", "REDUCE", "EXIT"]
    assert "confidence_score" in data
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert "reason" in data
    assert "stop_loss" in data
    assert "take_profit" in data
    assert "invalidation_condition" in data
    assert "timestamp" in data

    # Verify numeric types (not strings)
    assert isinstance(data["confidence_score"], (int, float)), "confidence_score must be a number"
    assert isinstance(data["stop_loss"], (int, float)), "stop_loss must be a number"
    assert isinstance(data["take_profit"], (int, float)), "take_profit must be a number"

    # Verify confidence score is between 0 and 100
    confidence = float(data["confidence_score"])
    assert 0 <= confidence <= 100, f"Confidence {confidence} is out of range [0, 100]"


@pytest.mark.asyncio
async def test_get_signal_sol(client: AsyncClient):
    """Test getting trading signal for SOL."""
    response = await client.get("/api/v1/signals/SOL")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "SOL"
    assert data["signal"] in ["ENTER", "WAIT", "REDUCE", "EXIT"]
    assert "confidence_score" in data
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert "reason" in data
    assert "stop_loss" in data
    assert "take_profit" in data
    assert "invalidation_condition" in data
    assert "timestamp" in data

    # Verify numeric types (not strings)
    assert isinstance(data["confidence_score"], (int, float)), "confidence_score must be a number"
    assert isinstance(data["stop_loss"], (int, float)), "stop_loss must be a number"
    assert isinstance(data["take_profit"], (int, float)), "take_profit must be a number"

    # Verify confidence score is between 0 and 100
    confidence = float(data["confidence_score"])
    assert 0 <= confidence <= 100, f"Confidence {confidence} is out of range [0, 100]"


@pytest.mark.asyncio
async def test_get_signal_invalid_symbol(client: AsyncClient):
    """Test getting trading signal for an invalid symbol."""
    response = await client.get("/api/v1/signals/INVALID")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "INVALID" in data["detail"] or "not available" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_signal_lowercase(client: AsyncClient):
    """Test getting signal with lowercase symbol (should work)."""
    response = await client.get("/api/v1/signals/btc")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"