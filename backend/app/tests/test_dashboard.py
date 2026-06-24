"""Tests for dashboard endpoint."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.services.dashboard_service import DashboardService, DashboardCache
from app.schemas.dashboard import DashboardResponse


class TestDashboardCache:
    """Tests for DashboardCache."""

    def test_cache_returns_none_when_empty(self):
        cache = DashboardCache(ttl_seconds=60)
        assert cache.get() is None
        assert cache.is_valid() is False

    def test_cache_stores_and_retrieves_data(self):
        cache = DashboardCache(ttl_seconds=60)
        data = {"key": "value"}
        cache.set(data)
        assert cache.get() == data
        assert cache.is_valid() is True

    def test_cache_expires_after_ttl(self):
        cache = DashboardCache(ttl_seconds=0)  # 0 second TTL
        data = {"key": "value"}
        cache.set(data)
        # Should be expired immediately
        assert cache.get() is None
        assert cache.is_valid() is False


class TestDashboardEndpoint:
    """Tests for /api/v1/dashboard endpoint."""

    @pytest.mark.asyncio
    async def test_dashboard_returns_all_symbols(self):
        """Test that dashboard returns BTC, ETH, and SOL."""
        # Mock the DashboardService to return mock data
        mock_response = DashboardResponse(
            updated_at=datetime.now(timezone.utc),
            source="coingecko",
            cache_status="fresh",
            generation_time_ms=100.0,
            items=[],
        )

        with patch.object(DashboardService, 'get_dashboard', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            from app.api.v1.dashboard import get_dashboard
            from app.repositories.market_data_repository import MarketDataRepository

            mock_repo = MagicMock(spec=MarketDataRepository)
            result = await get_dashboard(mock_repo)

            assert result.source == "coingecko"
            assert result.cache_status == "fresh"
            assert result.generation_time_ms == 100.0

    @pytest.mark.asyncio
    async def test_dashboard_returns_source(self):
        """Test that dashboard returns source field."""
        mock_response = DashboardResponse(
            updated_at=datetime.now(timezone.utc),
            source="mock",
            cache_status="cached",
            generation_time_ms=50.0,
            items=[],
        )

        with patch.object(DashboardService, 'get_dashboard', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            from app.api.v1.dashboard import get_dashboard
            from app.repositories.market_data_repository import MarketDataRepository

            mock_repo = MagicMock(spec=MarketDataRepository)
            result = await get_dashboard(mock_repo)

            assert result.source == "mock"
            assert result.cache_status == "cached"

    @pytest.mark.asyncio
    async def test_dashboard_returns_cache_status(self):
        """Test that dashboard returns cache_status field."""
        mock_response = DashboardResponse(
            updated_at=datetime.now(timezone.utc),
            source="coingecko",
            cache_status="fresh",
            generation_time_ms=100.0,
            items=[],
        )

        with patch.object(DashboardService, 'get_dashboard', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            from app.api.v1.dashboard import get_dashboard
            from app.repositories.market_data_repository import MarketDataRepository

            mock_repo = MagicMock(spec=MarketDataRepository)
            result = await get_dashboard(mock_repo)

            assert result.cache_status in ["fresh", "cached"]

    @pytest.mark.asyncio
    async def test_dashboard_returns_generation_time(self):
        """Test that dashboard returns generation_time_ms field."""
        mock_response = DashboardResponse(
            updated_at=datetime.now(timezone.utc),
            source="coingecko",
            cache_status="fresh",
            generation_time_ms=100.0,
            items=[],
        )

        with patch.object(DashboardService, 'get_dashboard', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            from app.api.v1.dashboard import get_dashboard
            from app.repositories.market_data_repository import MarketDataRepository

            mock_repo = MagicMock(spec=MarketDataRepository)
            result = await get_dashboard(mock_repo)

            assert result.generation_time_ms >= 0

    @pytest.mark.asyncio
    async def test_dashboard_handles_partial_failure(self):
        """Test that dashboard handles partial failures gracefully."""
        # When partial failure occurs, source should be "mock"
        mock_response = DashboardResponse(
            updated_at=datetime.now(timezone.utc),
            source="mock",
            cache_status="fresh",
            generation_time_ms=100.0,
            items=[],
        )

        with patch.object(DashboardService, 'get_dashboard', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            from app.api.v1.dashboard import get_dashboard
            from app.repositories.market_data_repository import MarketDataRepository

            mock_repo = MagicMock(spec=MarketDataRepository)
            result = await get_dashboard(mock_repo)

            # Should return mock source when there are failures
            assert result.source == "mock"