"""Dashboard service with caching."""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.core.logging_config import get_logger
from app.domain.enums.crypto_symbol import CryptoSymbol
from app.repositories.market_data_repository import MarketDataRepository
from app.schemas.dashboard import (
    DashboardAIExplanation,
    DashboardItem,
    DashboardMarketData,
    DashboardResponse,
    DashboardSignal,
)
from app.services.ai_explanation_service import AIExplanationService
from app.services.market_data_service import MarketDataService
from app.services.signal_engine_service import SignalEngineService

logger = get_logger(__name__)


class DashboardCache:
    """Simple in-memory cache for dashboard data."""

    def __init__(self, ttl_seconds: int = 60):
        self.ttl_seconds = ttl_seconds
        self._cache: Optional[Dict[str, Any]] = None
        self._cached_at: Optional[datetime] = None

    def get(self) -> Optional[Dict[str, Any]]:
        """Get cached data if valid."""
        if self._cache is None or self._cached_at is None:
            return None

        age = (datetime.now(timezone.utc) - self._cached_at).total_seconds()
        if age > self.ttl_seconds:
            self._cache = None
            self._cached_at = None
            return None

        return self._cache

    def set(self, data: Dict[str, Any]) -> None:
        """Store data in cache."""
        self._cache = data
        self._cached_at = datetime.now(timezone.utc)

    def is_valid(self) -> bool:
        """Check if cache has valid data."""
        return self.get() is not None


class DashboardService:
    """Service for generating dashboard data with caching."""

    SUPPORTED_SYMBOLS = ["BTC", "ETH", "SOL"]

    def __init__(
        self,
        repository: MarketDataRepository,
        cache_ttl: Optional[int] = None,
    ):
        """Initialize dashboard service.

        Args:
            repository: Market data repository
            cache_ttl: Cache TTL in seconds (default from settings)
        """
        self.repository = repository
        self.cache = DashboardCache(cache_ttl or settings.DASHBOARD_CACHE_TTL_SECONDS)

        # Create service instances
        self.market_service = MarketDataService(repository)
        self.signal_service = SignalEngineService()
        self.ai_service = AIExplanationService()

    async def get_dashboard(self) -> DashboardResponse:
        """Get dashboard data, using cache if available."""
        start_time = time.time()

        # Check cache first
        cached_data = self.cache.get()
        if cached_data is not None:
            generation_time = (time.time() - start_time) * 1000
            return DashboardResponse(
                **cached_data,
                cache_status="cached",
                generation_time_ms=round(generation_time, 2),
            )

        # Generate fresh data
        items = await self._generate_dashboard()
        generation_time = (time.time() - start_time) * 1000

        # Determine overall source
        overall_source = "coingecko"
        for item in items:
            if item.market_data.source == "mock":
                overall_source = "mock"
                break

        # Build cache data (without cache_status and generation_time_ms)
        cache_data = {
            "updated_at": datetime.now(timezone.utc),
            "source": overall_source,
            "items": [item.model_dump() for item in items],
        }
        self.cache.set(cache_data)

        return DashboardResponse(
            **cache_data,
            cache_status="fresh",
            generation_time_ms=round(generation_time, 2),
        )

    async def _generate_dashboard(self) -> List[DashboardItem]:
        """Generate fresh dashboard data for all symbols in parallel."""
        # Generate data for all symbols in parallel
        tasks = [self._generate_symbol_data(symbol) for symbol in self.SUPPORTED_SYMBOLS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results, handling any failures gracefully
        items: List[DashboardItem] = []

        for symbol, result in zip(self.SUPPORTED_SYMBOLS, results):
            if isinstance(result, Exception):
                logger.warning(f"Failed to generate data for {symbol}: {result}")
                # Use fallback data for failed symbols
                item = await self._generate_fallback_item(symbol)
            else:
                item = result
            items.append(item)

        return items

    async def _generate_symbol_data(self, symbol: str) -> DashboardItem:
        """Generate complete data for a single symbol."""
        # Get market data
        market_data = await self.market_service.get_market_data_by_symbol(symbol)
        if market_data is None:
            raise ValueError(f"No market data for {symbol}")

        # Get trading signal
        try:
            signal = await self.signal_service.generate_signal(symbol)
        except Exception as e:
            logger.warning(f"Failed to get signal for {symbol}: {e}")
            raise

        # Get AI explanation (skip if no OpenAI key)
        try:
            ai_explanation = await self.ai_service.generate_explanation(symbol)
            if ai_explanation is None:
                raise ValueError(f"No AI explanation for {symbol}")
        except Exception as e:
            logger.warning(f"Failed to get AI explanation for {symbol}: {e}")
            # Use deterministic fallback
            signal_for_fallback = await self.signal_service.generate_signal(symbol)
            if signal_for_fallback:
                ai_explanation = self.ai_service._generate_fallback_explanation(
                    signal_for_fallback
                )
            else:
                raise

        return DashboardItem(
            market_data=DashboardMarketData(
                symbol=market_data.symbol,
                price=market_data.price,
                market_cap=market_data.market_cap,
                volume_24h=market_data.volume_24h,
                change_24h=market_data.change_24h,
                timestamp=market_data.timestamp,
                source=market_data.source,
            ),
            signal=DashboardSignal(
                symbol=signal.symbol,
                signal=signal.signal,
                confidence_score=signal.confidence_score,
                risk_level=signal.risk_level,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                timestamp=signal.timestamp,
            ),
            ai_explanation=DashboardAIExplanation(
                symbol=ai_explanation.symbol,
                signal=ai_explanation.signal,
                confidence_score=ai_explanation.confidence_score,
                risk_level=ai_explanation.risk_level,
                technical_summary=ai_explanation.technical_summary,
                plain_spanish_explanation=ai_explanation.plain_spanish_explanation,
                risk_warning=ai_explanation.risk_warning,
                educational_disclaimer=ai_explanation.educational_disclaimer,
                timestamp=ai_explanation.timestamp,
            ),
        )

    async def _generate_fallback_item(self, symbol: str) -> DashboardItem:
        """Generate fallback item for a failed symbol."""
        now = datetime.now(timezone.utc)

        # Get mock market data
        market_data = await self.market_service.get_market_data_by_symbol(symbol)
        if market_data is None:
            # Create minimal fallback
            market_data_response = type(
                "obj",
                (object,),
                {
                    "symbol": symbol,
                    "price": 0.0,
                    "market_cap": 0.0,
                    "volume_24h": 0.0,
                    "change_24h": 0.0,
                    "timestamp": now,
                    "source": "mock",
                },
            )
        else:
            market_data_response = market_data

        # Get signal (use fallback)
        try:
            signal = await self.signal_service.generate_signal(symbol)
        except Exception:
            signal = type(
                "obj",
                (object,),
                {
                    "symbol": symbol,
                    "signal": "WAIT",
                    "confidence_score": 0.0,
                    "risk_level": "LOW",
                    "stop_loss": 0.0,
                    "take_profit": 0.0,
                    "timestamp": now,
                },
            )

        # Get AI explanation (use fallback)
        try:
            ai_explanation = self.ai_service._generate_fallback_explanation(signal)
        except Exception:
            ai_explanation = type(
                "obj",
                (object,),
                {
                    "symbol": symbol,
                    "signal": "WAIT",
                    "confidence_score": 0.0,
                    "risk_level": "LOW",
                    "technical_summary": "Análisis no disponible.",
                    "plain_spanish_explanation": "No hay explicación disponible.",
                    "risk_warning": "Las criptomonedas son volátiles.",
                    "educational_disclaimer": "Solo fines educativos.",
                    "timestamp": now,
                },
            )

        return DashboardItem(
            market_data=DashboardMarketData(
                symbol=market_data_response.symbol,
                price=market_data_response.price,
                market_cap=market_data_response.market_cap,
                volume_24h=market_data_response.volume_24h,
                change_24h=market_data_response.change_24h,
                timestamp=market_data_response.timestamp,
                source="mock",
            ),
            signal=DashboardSignal(
                symbol=signal.symbol,
                signal=signal.signal,
                confidence_score=signal.confidence_score,
                risk_level=signal.risk_level,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                timestamp=signal.timestamp,
            ),
            ai_explanation=DashboardAIExplanation(
                symbol=ai_explanation.symbol,
                signal=ai_explanation.signal,
                confidence_score=ai_explanation.confidence_score,
                risk_level=ai_explanation.risk_level,
                technical_summary=ai_explanation.technical_summary,
                plain_spanish_explanation=ai_explanation.plain_spanish_explanation,
                risk_warning=ai_explanation.risk_warning,
                educational_disclaimer=ai_explanation.educational_disclaimer,
                timestamp=ai_explanation.timestamp,
            ),
        )