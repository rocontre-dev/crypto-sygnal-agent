"""Trading signal entity."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..enums.crypto_symbol import CryptoSymbol
from ..enums.signal_type import RiskLevel, SignalType


@dataclass
class TradingSignalEntity:
    """Trading signal entity representing a generated trading signal.

    This entity encapsulates a complete trading signal with entry/exit
    recommendations, confidence scores, risk assessment, and protective
    levels.

    Attributes:
        symbol: Cryptocurrency symbol (e.g., BTC, ETH, SOL)
        signal: Trading signal type (ENTER, WAIT, REDUCE, EXIT)
        confidence_score: Signal confidence (0-100)
        risk_level: Risk assessment (LOW, MEDIUM, HIGH)
        reason: Detailed explanation in Spanish
        stop_loss: Suggested stop-loss price
        take_profit: Suggested take-profit price
        invalidation_condition: Condition that invalidates the signal (Spanish)
        timestamp: When this signal was generated
        id: Optional unique identifier
    """

    symbol: CryptoSymbol
    signal: SignalType
    confidence_score: Decimal
    risk_level: RiskLevel
    reason: str
    invalidation_condition: str
    timestamp: datetime
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    id: Optional[int] = None

    @property
    def symbol_str(self) -> str:
        """Get symbol as string."""
        return self.symbol.value if isinstance(self.symbol, CryptoSymbol) else self.symbol