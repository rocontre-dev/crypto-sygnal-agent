"""Tests for AI explanation endpoints."""

import os

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_ai_explanation_btc(client: AsyncClient):
    """Test getting AI explanation for BTC."""
    response = await client.get("/api/v1/ai-explanations/BTC")
    assert response.status_code == 200
    data = response.json()

    # Verify signal fields are present and unchanged
    assert data["symbol"] == "BTC"
    assert data["signal"] in ["ENTER", "WAIT", "REDUCE", "EXIT"]
    assert isinstance(data["confidence_score"], (int, float))
    assert 0 <= data["confidence_score"] <= 100
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert isinstance(data["stop_loss"], (int, float))
    assert isinstance(data["take_profit"], (int, float))
    assert "invalidation_condition" in data

    # Verify AI-generated fields
    assert "technical_summary" in data
    assert "plain_spanish_explanation" in data
    assert "risk_warning" in data
    assert "educational_disclaimer" in data
    assert "timestamp" in data

    # Verify AI doesn't use forbidden phrases
    explanation_lower = data["plain_spanish_explanation"].lower()
    assert "compra seguro" not in explanation_lower
    assert "vende seguro" not in explanation_lower


@pytest.mark.asyncio
async def test_get_ai_explanation_eth(client: AsyncClient):
    """Test getting AI explanation for ETH."""
    response = await client.get("/api/v1/ai-explanations/ETH")
    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == "ETH"
    assert data["signal"] in ["ENTER", "WAIT", "REDUCE", "EXIT"]
    assert isinstance(data["confidence_score"], (int, float))
    assert 0 <= data["confidence_score"] <= 100
    assert "technical_summary" in data
    assert "plain_spanish_explanation" in data
    assert "risk_warning" in data
    assert "educational_disclaimer" in data


@pytest.mark.asyncio
async def test_get_ai_explanation_sol(client: AsyncClient):
    """Test getting AI explanation for SOL."""
    response = await client.get("/api/v1/ai-explanations/SOL")
    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == "SOL"
    assert data["signal"] in ["ENTER", "WAIT", "REDUCE", "EXIT"]
    assert isinstance(data["confidence_score"], (int, float))
    assert 0 <= data["confidence_score"] <= 100
    assert "technical_summary" in data
    assert "plain_spanish_explanation" in data
    assert "risk_warning" in data
    assert "educational_disclaimer" in data


@pytest.mark.asyncio
async def test_get_ai_explanation_invalid_symbol(client: AsyncClient):
    """Test getting AI explanation for an invalid symbol."""
    response = await client.get("/api/v1/ai-explanations/INVALID")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "INVALID" in data["detail"] or "not available" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_ai_explanation_lowercase(client: AsyncClient):
    """Test getting AI explanation with lowercase symbol (should work)."""
    response = await client.get("/api/v1/ai-explanations/btc")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"


@pytest.mark.asyncio
async def test_ai_explanation_fallback_without_api_key():
    """Test that fallback explanation works when OPENAI_API_KEY is missing."""
    # Save original value
    original_key = os.getenv("OPENAI_API_KEY")

    # Remove the key if it exists
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]

    try:
        from app.services.ai_explanation_service import AIExplanationService

        service = AIExplanationService()
        explanation = await service.generate_explanation("BTC")

        assert explanation is not None
        assert explanation.symbol == "BTC"
        assert explanation.signal in ["ENTER", "WAIT", "REDUCE", "EXIT"]
        assert 0 <= explanation.confidence_score <= 100
        assert explanation.risk_warning is not None
        assert explanation.educational_disclaimer is not None
        assert "riesgo" in explanation.risk_warning.lower()
        assert "educativo" in explanation.educational_disclaimer.lower() or "descargo" in explanation.educational_disclaimer.lower()
    finally:
        # Restore original value
        if original_key is not None:
            os.environ["OPENAI_API_KEY"] = original_key


@pytest.mark.asyncio
async def test_ai_explanation_preserves_signal_from_signal_engine(client: AsyncClient):
    """Test that AI explanation preserves the original signal from SignalEngineService."""
    # Get the signal directly
    signal_response = await client.get("/api/v1/signals/BTC")
    assert signal_response.status_code == 200
    signal_data = signal_response.json()

    # Get the AI explanation
    ai_response = await client.get("/api/v1/ai-explanations/BTC")
    assert ai_response.status_code == 200
    ai_data = ai_response.json()

    # Verify signal fields match exactly
    assert ai_data["symbol"] == signal_data["symbol"]
    assert ai_data["signal"] == signal_data["signal"]
    assert ai_data["confidence_score"] == signal_data["confidence_score"]
    assert ai_data["risk_level"] == signal_data["risk_level"]
    assert ai_data["stop_loss"] == signal_data["stop_loss"]
    assert ai_data["take_profit"] == signal_data["take_profit"]
    assert ai_data["invalidation_condition"] == signal_data["invalidation_condition"]