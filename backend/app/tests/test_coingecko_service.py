"""Tests for CoinGecko service."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from app.services.coingecko_service import CoinGeckoService


@pytest.fixture
def coingecko_service():
    """Create a CoinGeckoService instance for testing."""
    return CoinGeckoService(timeout=1.0)


@pytest.fixture
def mock_coingecko_response():
    """Mock CoinGecko API response data."""
    return [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": 67500.00,
            "market_cap": 1300000000000.00,
            "market_cap_rank": 1,
            "total_volume": 25000000000.00,
            "price_change_percentage_24h": 2.50,
            "last_updated": "2024-01-15T10:30:00.000Z",
        },
        {
            "id": "ethereum",
            "symbol": "eth",
            "name": "Ethereum",
            "current_price": 3500.00,
            "market_cap": 420000000000.00,
            "market_cap_rank": 2,
            "total_volume": 12000000000.00,
            "price_change_percentage_24h": -1.20,
            "last_updated": "2024-01-15T10:30:00.000Z",
        },
        {
            "id": "solana",
            "symbol": "sol",
            "name": "Solana",
            "current_price": 150.00,
            "market_cap": 65000000000.00,
            "market_cap_rank": 3,
            "total_volume": 3000000000.00,
            "price_change_percentage_24h": 5.80,
            "last_updated": "2024-01-15T10:30:00.000Z",
        },
    ]


@pytest.fixture
def partial_coingecko_response():
    """Mock partial CoinGecko API response (only BTC and ETH)."""
    return [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": 67500.00,
            "market_cap": 1300000000000.00,
            "market_cap_rank": 1,
            "total_volume": 25000000000.00,
            "price_change_percentage_24h": 2.50,
            "last_updated": "2024-01-15T10:30:00.000Z",
        },
        {
            "id": "ethereum",
            "symbol": "eth",
            "name": "Ethereum",
            "current_price": 3500.00,
            "market_cap": 420000000000.00,
            "market_cap_rank": 2,
            "total_volume": 12000000000.00,
            "price_change_percentage_24h": -1.20,
            "last_updated": "2024-01-15T10:30:00.000Z",
        },
    ]


class TestCoinGeckoServiceParseResponse:
    """Tests for _parse_response method."""

    def test_parse_full_response(self, coingecko_service, mock_coingecko_response):
        """Test parsing a complete response with all symbols."""
        result = coingecko_service._parse_response(mock_coingecko_response)

        assert len(result) == 3
        assert "BTC" in result
        assert "ETH" in result
        assert "SOL" in result

        # Check BTC data
        btc = result["BTC"]
        assert btc["price"] == 67500.00
        assert btc["market_cap"] == 1300000000000.00
        assert btc["volume_24h"] == 25000000000.00
        assert btc["change_24h"] == 2.50
        assert isinstance(btc["last_updated"], datetime)

        # Check ETH data
        eth = result["ETH"]
        assert eth["price"] == 3500.00
        assert eth["market_cap"] == 420000000000.00
        assert eth["volume_24h"] == 12000000000.00
        assert eth["change_24h"] == -1.20

        # Check SOL data
        sol = result["SOL"]
        assert sol["price"] == 150.00
        assert sol["market_cap"] == 65000000000.00
        assert sol["volume_24h"] == 3000000000.00
        assert sol["change_24h"] == 5.80

    def test_parse_partial_response(self, coingecko_service, partial_coingecko_response):
        """Test parsing a partial response with only some symbols."""
        result = coingecko_service._parse_response(partial_coingecko_response)

        assert len(result) == 2
        assert "BTC" in result
        assert "ETH" in result
        assert "SOL" not in result

    def test_parse_empty_response(self, coingecko_service):
        """Test parsing an empty response."""
        result = coingecko_service._parse_response([])
        assert len(result) == 0

    def test_parse_response_skips_unknown_coins(self, coingecko_service):
        """Test that unknown coin IDs are skipped."""
        data = [
            {
                "id": "dogecoin",
                "current_price": 0.10,
                "market_cap": 1000000000.00,
                "total_volume": 100000000.00,
                "price_change_percentage_24h": 1.0,
                "last_updated": "2024-01-15T10:30:00.000Z",
            }
        ]
        result = coingecko_service._parse_response(data)
        assert len(result) == 0

    def test_parse_response_handles_none_values(self, coingecko_service):
        """Test parsing response with None values."""
        data = [
            {
                "id": "bitcoin",
                "current_price": None,
                "market_cap": None,
                "total_volume": None,
                "price_change_percentage_24h": None,
                "last_updated": None,
            }
        ]
        result = coingecko_service._parse_response(data)

        assert "BTC" in result
        assert result["BTC"]["price"] == 0.0
        assert result["BTC"]["market_cap"] == 0.0
        assert result["BTC"]["volume_24h"] == 0.0
        assert result["BTC"]["change_24h"] == 0.0

    def test_parse_response_handles_invalid_timestamp(self, coingecko_service):
        """Test parsing response with invalid timestamp."""
        data = [
            {
                "id": "bitcoin",
                "current_price": 67500.00,
                "market_cap": 1300000000000.00,
                "total_volume": 25000000000.00,
                "price_change_percentage_24h": 2.50,
                "last_updated": "invalid-date",
            }
        ]
        result = coingecko_service._parse_response(data)

        assert "BTC" in result
        # Should use current time as fallback
        assert isinstance(result["BTC"]["last_updated"], datetime)


class TestCoinGeckoServiceGetMissingSymbols:
    """Tests for get_missing_symbols method."""

    def test_no_missing_symbols(self, coingecko_service, mock_coingecko_response):
        """Test when all symbols are present."""
        parsed = coingecko_service._parse_response(mock_coingecko_response)
        missing = coingecko_service.get_missing_symbols(parsed)
        assert len(missing) == 0

    def test_partial_missing_symbols(self, coingecko_service, partial_coingecko_response):
        """Test when some symbols are missing."""
        parsed = coingecko_service._parse_response(partial_coingecko_response)
        missing = coingecko_service.get_missing_symbols(parsed)
        assert len(missing) == 1
        assert "SOL" in missing

    def test_all_symbols_missing(self, coingecko_service):
        """Test when all symbols are missing (empty response)."""
        missing = coingecko_service.get_missing_symbols({})
        assert len(missing) == 3
        assert set(missing) == {"BTC", "ETH", "SOL"}


class TestCoinGeckoServiceFetchMarketData:
    """Tests for fetch_market_data method with mocked HTTP calls."""

    @pytest.mark.asyncio
    async def test_fetch_success(self, coingecko_service, mock_coingecko_response):
        """Test successful fetch from CoinGecko."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_coingecko_response

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            result = await coingecko_service.fetch_market_data()

            assert len(result) == 3
            assert "BTC" in result
            assert "ETH" in result
            assert "SOL" in result

    @pytest.mark.asyncio
    async def test_fetch_api_error(self, coingecko_service):
        """Test fetch when API returns error status."""
        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            result = await coingecko_service.fetch_market_data()

            assert result == {}

    @pytest.mark.asyncio
    async def test_fetch_timeout(self, coingecko_service):
        """Test fetch when request times out."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=Exception("Timeout"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            result = await coingecko_service.fetch_market_data()

            assert result == {}

    @pytest.mark.asyncio
    async def test_fetch_network_error(self, coingecko_service):
        """Test fetch when network error occurs."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=Exception("Network error"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            result = await coingecko_service.fetch_market_data()

            assert result == {}


class TestMarketDataServiceWithCoinGecko:
    """Integration tests for MarketDataService with CoinGecko."""

    @pytest.mark.asyncio
    async def test_get_all_with_full_coingecko_data(self):
        """Test get_all_market_data when CoinGecko returns all symbols."""
        from app.services.market_data_service import MarketDataService
        from app.repositories.market_data_repository import MarketDataRepository

        # Create a mock repository (not used when CoinGecko works)
        mock_repo = MagicMock(spec=MarketDataRepository)

        # Create mock CoinGecko service with full data
        mock_coingecko = MagicMock(spec=CoinGeckoService)
        mock_coingecko.fetch_market_data = AsyncMock(
            return_value={
                "BTC": {
                    "price": 68000.0,
                    "market_cap": 1350000000000.0,
                    "volume_24h": 26000000000.0,
                    "change_24h": 3.0,
                    "last_updated": datetime.now(timezone.utc),
                },
                "ETH": {
                    "price": 3600.0,
                    "market_cap": 430000000000.0,
                    "volume_24h": 13000000000.0,
                    "change_24h": -0.5,
                    "last_updated": datetime.now(timezone.utc),
                },
                "SOL": {
                    "price": 155.0,
                    "market_cap": 67000000000.0,
                    "volume_24h": 3200000000.0,
                    "change_24h": 6.0,
                    "last_updated": datetime.now(timezone.utc),
                },
            }
        )
        mock_coingecko.get_missing_symbols = MagicMock(return_value=[])

        service = MarketDataService(mock_repo, mock_coingecko)
        result = await service.get_all_market_data()

        assert len(result) == 3
        symbols = [r.symbol for r in result]
        assert "BTC" in symbols
        assert "ETH" in symbols
        assert "SOL" in symbols

        # Verify prices are from CoinGecko (not mock)
        btc = next(r for r in result if r.symbol == "BTC")
        assert btc.price == 68000.0

    @pytest.mark.asyncio
    async def test_get_all_with_partial_coingecko_data(self):
        """Test get_all_market_data when CoinGecko returns only some symbols."""
        from app.services.market_data_service import MarketDataService
        from app.repositories.market_data_repository import MarketDataRepository

        mock_repo = MagicMock(spec=MarketDataRepository)

        mock_coingecko = MagicMock(spec=CoinGeckoService)
        mock_coingecko.fetch_market_data = AsyncMock(
            return_value={
                "BTC": {
                    "price": 68000.0,
                    "market_cap": 1350000000000.0,
                    "volume_24h": 26000000000.0,
                    "change_24h": 3.0,
                    "last_updated": datetime.now(timezone.utc),
                },
                "ETH": {
                    "price": 3600.0,
                    "market_cap": 430000000000.0,
                    "volume_24h": 13000000000.0,
                    "change_24h": -0.5,
                    "last_updated": datetime.now(timezone.utc),
                },
            }
        )
        mock_coingecko.get_missing_symbols = MagicMock(return_value=["SOL"])

        service = MarketDataService(mock_repo, mock_coingecko)
        result = await service.get_all_market_data()

        assert len(result) == 3

        # BTC and ETH should have real data
        btc = next(r for r in result if r.symbol == "BTC")
        assert btc.price == 68000.0

        eth = next(r for r in result if r.symbol == "ETH")
        assert eth.price == 3600.0

        # SOL should have mock data
        sol = next(r for r in result if r.symbol == "SOL")
        assert sol.price == 150.00  # Mock price

    @pytest.mark.asyncio
    async def test_get_all_with_coingecko_failure(self):
        """Test get_all_market_data when CoinGecko fails completely."""
        from app.services.market_data_service import MarketDataService
        from app.repositories.market_data_repository import MarketDataRepository

        mock_repo = MagicMock(spec=MarketDataRepository)

        mock_coingecko = MagicMock(spec=CoinGeckoService)
        mock_coingecko.fetch_market_data = AsyncMock(return_value={})
        mock_coingecko.get_missing_symbols = MagicMock(
            return_value=["BTC", "ETH", "SOL"]
        )

        service = MarketDataService(mock_repo, mock_coingecko)
        result = await service.get_all_market_data()

        assert len(result) == 3
        # All should be mock data
        assert all(r.price in [67500.0, 3500.0, 150.0] for r in result)

    @pytest.mark.asyncio
    async def test_get_by_symbol_with_coingecko_data(self):
        """Test get_market_data_by_symbol when CoinGecko has data."""
        from app.services.market_data_service import MarketDataService
        from app.repositories.market_data_repository import MarketDataRepository

        mock_repo = MagicMock(spec=MarketDataRepository)

        mock_coingecko = MagicMock(spec=CoinGeckoService)
        mock_coingecko.fetch_market_data = AsyncMock(
            return_value={
                "BTC": {
                    "price": 68000.0,
                    "market_cap": 1350000000000.0,
                    "volume_24h": 26000000000.0,
                    "change_24h": 3.0,
                    "last_updated": datetime.now(timezone.utc),
                }
            }
        )

        service = MarketDataService(mock_repo, mock_coingecko)
        result = await service.get_market_data_by_symbol("BTC")

        assert result is not None
        assert result.symbol == "BTC"
        assert result.price == 68000.0

    @pytest.mark.asyncio
    async def test_get_by_symbol_with_fallback(self):
        """Test get_market_data_by_symbol when CoinGecko doesn't have the symbol."""
        from app.services.market_data_service import MarketDataService
        from app.repositories.market_data_repository import MarketDataRepository

        mock_repo = MagicMock(spec=MarketDataRepository)

        mock_coingecko = MagicMock(spec=CoinGeckoService)
        mock_coingecko.fetch_market_data = AsyncMock(return_value={})

        service = MarketDataService(mock_repo, mock_coingecko)
        result = await service.get_market_data_by_symbol("BTC")

        assert result is not None
        assert result.symbol == "BTC"
        assert result.price == 67500.0  # Mock price

    @pytest.mark.asyncio
    async def test_get_by_symbol_invalid(self):
        """Test get_market_data_by_symbol with invalid symbol."""
        from app.services.market_data_service import MarketDataService
        from app.repositories.market_data_repository import MarketDataRepository

        mock_repo = MagicMock(spec=MarketDataRepository)
        mock_coingecko = MagicMock(spec=CoinGeckoService)

        service = MarketDataService(mock_repo, mock_coingecko)
        result = await service.get_market_data_by_symbol("INVALID")

        assert result is None