"""Signal engine service."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from app.domain.entities.trading_signal import TradingSignalEntity
from app.domain.enums.crypto_symbol import CryptoSymbol
from app.domain.enums.signal_type import RiskLevel, SignalType
from app.services.technical_indicator_service import TechnicalIndicatorService


class SignalEngineService:
    """Service for generating trading signals based on technical indicators.

    Uses rule-based logic to analyze technical indicators and generate
    trading signals with confidence scores, risk levels, and protective
    levels.
    """

    def __init__(self):
        """Initialize the signal engine service."""
        self.indicator_service = TechnicalIndicatorService()

    async def generate_signal(self, symbol: str) -> Optional[TradingSignalEntity]:
        """Generate a trading signal for the given symbol.

        Args:
            symbol: Cryptocurrency symbol (BTC, ETH, SOL)

        Returns:
            TradingSignalEntity with the generated signal,
            or None if symbol is not supported
        """
        try:
            crypto_symbol = CryptoSymbol(symbol.upper())
        except ValueError:
            return None

        # Get technical indicators
        indicators = await self.indicator_service.calculate_indicators(symbol)
        if indicators is None:
            return None

        # Analyze conditions and generate signal
        return self._analyze_and_generate_signal(crypto_symbol, indicators)

    def _analyze_and_generate_signal(
        self, symbol: CryptoSymbol, indicators
    ) -> TradingSignalEntity:
        """Analyze indicators and generate trading signal.

        Args:
            symbol: Cryptocurrency symbol
            indicators: TechnicalIndicatorEntity with current indicators

        Returns:
            TradingSignalEntity with the generated signal
        """
        rsi = float(indicators.rsi)
        macd = float(indicators.macd)
        ema20 = float(indicators.ema20)
        ema50 = float(indicators.ema50)
        ema200 = float(indicators.ema200)
        percent_change = float(indicators.percent_change)

        # Calculate current price (use EMA20 as proxy for current price)
        current_price = ema20

        # Evaluate conditions
        rsi_oversold = rsi < 35
        rsi_overbought = rsi > 70
        rsi_elevated = rsi > 65
        price_above_ema20 = current_price > ema20
        price_below_ema20 = current_price < ema20
        ema20_above_ema50 = ema20 > ema50
        macd_positive = macd > 0
        macd_negative = macd < 0
        strong_negative_change = percent_change < -3

        # Determine signal based on rules
        signal, confidence, reasons = self._determine_signal(
            rsi_oversold, rsi_overbought, rsi_elevated,
            price_above_ema20, price_below_ema20,
            ema20_above_ema50, macd_positive, macd_negative,
            strong_negative_change, percent_change
        )

        # Determine risk level
        risk_level = self._determine_risk_level(signal, confidence, rsi, percent_change)

        # Calculate stop loss and take profit
        stop_loss, take_profit = self._calculate_levels(signal, current_price, ema50, ema200)

        # Generate reason in Spanish
        reason = self._generate_reason(signal, reasons, rsi, macd, percent_change)

        # Generate invalidation condition in Spanish
        invalidation = self._generate_invalidation(signal, ema50, ema200, current_price)

        return TradingSignalEntity(
            symbol=symbol,
            signal=signal,
            confidence_score=Decimal(str(round(confidence, 2))),
            risk_level=risk_level,
            reason=reason,
            stop_loss=Decimal(str(round(stop_loss, 2))),
            take_profit=Decimal(str(round(take_profit, 2))),
            invalidation_condition=invalidation,
            timestamp=datetime.now(timezone.utc),
        )

    def _determine_signal(
        self, rsi_oversold, rsi_overbought, rsi_elevated,
        price_above_ema20, price_below_ema20,
        ema20_above_ema50, macd_positive, macd_negative,
        strong_negative_change, percent_change
    ):
        """Determine signal type and confidence based on conditions."""
        reasons = []
        confidence = 50  # Base confidence

        # ENTER conditions
        enter_conditions = 0
        if rsi_oversold:
            enter_conditions += 1
            reasons.append("rsi_oversold")
        if price_above_ema20:
            enter_conditions += 1
            reasons.append("price_above_ema20")
        if ema20_above_ema50:
            enter_conditions += 1
            reasons.append("ema20_above_ema50")
        if macd_positive:
            enter_conditions += 1
            reasons.append("macd_positive")

        # EXIT conditions
        exit_conditions = 0
        if rsi_overbought:
            exit_conditions += 1
            reasons.append("rsi_overbought")
        if price_below_ema20:
            exit_conditions += 1
            reasons.append("price_below_ema20")
        if macd_negative:
            exit_conditions += 1
            reasons.append("macd_negative")

        # REDUCE conditions
        reduce_conditions = 0
        if rsi_elevated:
            reduce_conditions += 1
            reasons.append("rsi_elevated")
        if price_below_ema20 and not rsi_overbought:
            reduce_conditions += 1
            reasons.append("losing_ema20")
        if strong_negative_change:
            reduce_conditions += 1
            reasons.append("strong_negative_change")

        # Determine signal
        if enter_conditions >= 3 and exit_conditions <= 1:
            signal = SignalType.ENTER
            confidence = 50 + (enter_conditions * 15)
        elif exit_conditions >= 2 and enter_conditions <= 1:
            signal = SignalType.EXIT
            confidence = 50 + (exit_conditions * 15)
        elif reduce_conditions >= 2:
            signal = SignalType.REDUCE
            confidence = 50 + (reduce_conditions * 12)
        else:
            signal = SignalType.WAIT
            confidence = 40 + min(len(reasons) * 5, 20)

        # Ensure confidence is between 0 and 100
        confidence = max(0, min(100, confidence))

        return signal, confidence, reasons

    def _determine_risk_level(self, signal, confidence, rsi, percent_change):
        """Determine risk level based on signal and market conditions."""
        if signal == SignalType.WAIT:
            return RiskLevel.LOW

        if confidence >= 75 and abs(percent_change) < 3:
            return RiskLevel.LOW
        elif confidence >= 60 or abs(percent_change) < 5:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH

    def _calculate_levels(self, signal, current_price, ema50, ema200):
        """Calculate stop loss and take profit levels."""
        if signal == SignalType.ENTER:
            # Stop loss below entry, take profit above
            stop_loss = current_price * 0.97  # 3% below
            take_profit = current_price * 1.05  # 5% above
        elif signal == SignalType.EXIT:
            # Stop loss above exit, take profit below
            stop_loss = current_price * 1.02  # 2% above
            take_profit = current_price * 0.95  # 5% below
        elif signal == SignalType.REDUCE:
            stop_loss = current_price * 0.98  # 2% below
            take_profit = current_price * 1.03  # 3% above
        else:  # WAIT
            stop_loss = current_price * 0.95  # 5% below
            take_profit = current_price * 1.05  # 5% above

        return stop_loss, take_profit

    def _generate_reason(self, signal, reasons, rsi, macd, percent_change):
        """Generate reason text in Spanish."""
        parts = []

        if signal == SignalType.ENTER:
            parts.append("Señal de COMPRA detectada.")
            if "rsi_oversold" in reasons:
                parts.append(f"RSI en zona de sobreventa ({rsi:.1f}).")
            if "price_above_ema20" in reasons:
                parts.append("Precio por encima de EMA20.")
            if "ema20_above_ema50" in reasons:
                parts.append("EMA20 > EMA50 (tendencia alcista).")
            if "macd_positive" in reasons:
                parts.append(f"MACD positivo ({macd:.2f}).")

        elif signal == SignalType.EXIT:
            parts.append("Señal de SALIDA detectada.")
            if "rsi_overbought" in reasons:
                parts.append(f"RSI en zona de sobrecompra ({rsi:.1f}).")
            if "price_below_ema20" in reasons:
                parts.append("Precio por debajo de EMA20.")
            if "macd_negative" in reasons:
                parts.append(f"MACD negativo ({macd:.2f}).")

        elif signal == SignalType.REDUCE:
            parts.append("Señal de REDUCIR posición.")
            if "rsi_elevated" in reasons:
                parts.append(f"RSI elevado ({rsi:.1f}).")
            if "losing_ema20" in reasons:
                parts.append("Precio perdiendo EMA20.")
            if "strong_negative_change" in reasons:
                parts.append(f"Cambio porcentual negativo ({percent_change:.2f}%).")

        else:  # WAIT
            parts.append("Sin señal clara.")
            parts.append("Condiciones mixtas en el mercado.")
            parts.append(f"RSI: {rsi:.1f}, MACD: {macd:.2f}.")

        return " ".join(parts)

    def _generate_invalidation(self, signal, ema50, ema200, current_price):
        """Generate invalidation condition in Spanish."""
        if signal == SignalType.ENTER:
            return f"Si el precio cae por debajo de EMA50 ({ema50:.2f}) o RSI supera 50 sin romper resistencias clave."
        elif signal == SignalType.EXIT:
            return f"Si el precio recupera EMA20 ({current_price:.2f}) y MACD se vuelve positivo."
        elif signal == SignalType.REDUCE:
            return f"Si el precio recupera EMA20 con volumen o RSI baja de 50."
        else:
            return "Esperar confirmación de ruptura de rango o cambio en tendencia."