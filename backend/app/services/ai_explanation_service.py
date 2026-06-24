"""AI explanation service."""

import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional

from app.domain.enums.signal_type import SignalType
from app.schemas.ai_explanation import AIExplanationResponse
from app.services.signal_engine_service import SignalEngineService


class AIExplanationService:
    """Service for generating AI-powered explanations of trading signals.

    This service uses OpenAI (when available) to generate clear Spanish
    explanations of trading signals. The AI NEVER modifies the signal
    decision - it only explains the existing rule-based signal in clearer terms.

    If OpenAI is not available or fails, a deterministic fallback explanation
    is returned.
    """

    def __init__(self):
        """Initialize the AI explanation service."""
        self.signal_service = SignalEngineService()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    async def generate_explanation(self, symbol: str) -> Optional[AIExplanationResponse]:
        """Generate an AI explanation for a trading signal.

        Args:
            symbol: Cryptocurrency symbol (BTC, ETH, SOL)

        Returns:
            AIExplanationResponse with the explanation,
            or None if symbol is not supported
        """
        # Get the trading signal from SignalEngineService
        signal = await self.signal_service.generate_signal(symbol)
        if signal is None:
            return None

        # Check if OpenAI is available
        if self.openai_api_key:
            try:
                return await self._generate_with_openai(signal)
            except Exception:
                # Fallback to deterministic explanation on any error
                return self._generate_fallback_explanation(signal)
        else:
            # No API key - use fallback
            return self._generate_fallback_explanation(signal)

    async def _generate_with_openai(self, signal) -> AIExplanationResponse:
        """Generate explanation using OpenAI.

        Args:
            signal: TradingSignalEntity from SignalEngineService

        Returns:
            AIExplanationResponse with AI-generated explanation
        """
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.openai_api_key, timeout=10.0)

            prompt = self._build_prompt(signal)

            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un analista financiero que explica señales de trading "
                            "de criptomonedas en español claro y educativo. "
                            "NUNCA digas 'compra seguro' o 'vende seguro'. "
                            "NUNCA prometas ganancias. "
                            "NUNCA inventes precios. "
                            "Siempre incluye advertencias de riesgo y descargos educativos."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.7,
            )

            await client.close()

            content = response.choices[0].message.content.strip()

            # Parse the AI response
            explanation_data = self._parse_ai_response(content, signal)

            return AIExplanationResponse(
                symbol=signal.symbol_str,
                signal=signal.signal.value,
                confidence_score=float(signal.confidence_score),
                risk_level=signal.risk_level.value,
                stop_loss=float(signal.stop_loss),
                take_profit=float(signal.take_profit),
                invalidation_condition=signal.invalidation_condition,
                technical_summary=explanation_data.get(
                    "technical_summary",
                    self._get_default_technical_summary(signal),
                ),
                plain_spanish_explanation=explanation_data.get(
                    "plain_spanish_explanation",
                    self._get_default_plain_explanation(signal),
                ),
                risk_warning=explanation_data.get(
                    "risk_warning",
                    self._get_default_risk_warning(),
                ),
                educational_disclaimer=explanation_data.get(
                    "educational_disclaimer",
                    self._get_default_educational_disclaimer(),
                ),
                timestamp=datetime.now(timezone.utc),
            )

        except Exception:
            # Fallback on any error
            return self._generate_fallback_explanation(signal)

    def _build_prompt(self, signal) -> str:
        """Build the prompt for OpenAI.

        Args:
            signal: TradingSignalEntity

        Returns:
            Prompt string
        """
        return (
            f"Explica la siguiente señal de trading de {signal.symbol_str}:\n\n"
            f"Señal: {signal.signal.value}\n"
            f"Confianza: {signal.confidence_score}/100\n"
            f"Nivel de riesgo: {signal.risk_level.value}\n"
            f"Stop Loss: {signal.stop_loss}\n"
            f"Take Profit: {signal.take_profit}\n"
            f"Condición de invalidación: {signal.invalidation_condition}\n"
            f"Razón original: {signal.reason}\n\n"
            "Por favor proporciona:\n"
            "1. Un resumen técnico (technical_summary)\n"
            "2. Una explicación en español simple (plain_spanish_explanation)\n"
            "3. Una advertencia de riesgo (risk_warning)\n"
            "4. Un descargo educativo (educational_disclaimer)\n\n"
            "Responde en formato JSON con las claves exactas mencionadas."
        )

    def _parse_ai_response(self, content: str, signal) -> Dict[str, str]:
        """Parse the AI response.

        Args:
            content: Raw AI response text
            signal: TradingSignalEntity

        Returns:
            Dictionary with parsed fields
        """
        import json

        try:
            # Try to parse as JSON
            data = json.loads(content)
            return {
                "technical_summary": data.get("technical_summary", ""),
                "plain_spanish_explanation": data.get("plain_spanish_explanation", ""),
                "risk_warning": data.get("risk_warning", ""),
                "educational_disclaimer": data.get("educational_disclaimer", ""),
            }
        except (json.JSONDecodeError, Exception):
            # If parsing fails, use the content as plain explanation
            return {
                "technical_summary": self._get_default_technical_summary(signal),
                "plain_spanish_explanation": content[:500] if content else "",
                "risk_warning": self._get_default_risk_warning(),
                "educational_disclaimer": self._get_default_educational_disclaimer(),
            }

    def _generate_fallback_explanation(self, signal) -> AIExplanationResponse:
        """Generate a deterministic fallback explanation.

        This is used when OpenAI is not available or fails.

        Args:
            signal: TradingSignalEntity

        Returns:
            AIExplanationResponse with fallback explanation
        """
        return AIExplanationResponse(
            symbol=signal.symbol_str,
            signal=signal.signal.value,
            confidence_score=float(signal.confidence_score),
            risk_level=signal.risk_level.value,
            stop_loss=float(signal.stop_loss),
            take_profit=float(signal.take_profit),
            invalidation_condition=signal.invalidation_condition,
            technical_summary=self._get_default_technical_summary(signal),
            plain_spanish_explanation=self._get_default_plain_explanation(signal),
            risk_warning=self._get_default_risk_warning(),
            educational_disclaimer=self._get_default_educational_disclaimer(),
            timestamp=datetime.now(timezone.utc),
        )

    def _get_default_technical_summary(self, signal) -> str:
        """Get default technical summary based on signal type."""
        summaries = {
            SignalType.ENTER: (
                f"Los indicadores técnicos para {signal.symbol_str} muestran condiciones favorables "
                f"para una posible entrada. El análisis técnico sugiere un momento propicio basado "
                f"en múltiples indicadores alineados."
            ),
            SignalType.EXIT: (
                f"Los indicadores técnicos para {signal.symbol_str} muestran condiciones desfavorables "
                f"que sugieren considerar una salida. Múltiples señales técnicas indican posible debilidad."
            ),
            SignalType.REDUCE: (
                f"Los indicadores técnicos para {signal.symbol_str} muestran señales mixtas que "
                f"sugieren reducir la exposición. Algunos indicadores muestran debilidad creciente."
            ),
            SignalType.WAIT: (
                f"Los indicadores técnicos para {signal.symbol_str} no muestran una dirección clara. "
                f"Las señales son mixtas y se recomienda esperar mayor confirmación antes de actuar."
            ),
        }
        return summaries.get(signal.signal, "Análisis técnico no disponible.")

    def _get_default_plain_explanation(self, signal) -> str:
        """Get default plain Spanish explanation based on signal type."""
        explanations = {
            SignalType.ENTER: (
                f"El análisis de {signal.symbol_str} sugiere que podría ser un buen momento para "
                f"considerar una posición. Los indicadores muestran condiciones que históricamente "
                f"han precedido movimientos alcistas. Sin embargo, siempre evalúa tu situación personal."
            ),
            SignalType.EXIT: (
                f"El análisis de {signal.symbol_str} indica que podría ser prudente considerar "
                f"reducir o cerrar posiciones. Los indicadores muestran señales de debilidad que "
                f"merecen atención. Evalúa si esto se alinea con tu estrategia."
            ),
            SignalType.REDUCE: (
                f"El análisis de {signal.symbol_str} sugiere precaución. Algunos indicadores muestran "
                f"señales de advertencia, por lo que podría ser apropiado reducir la exposición "
                f"para gestionar el riesgo."
            ),
            SignalType.WAIT: (
                f"El análisis de {signal.symbol_str} no muestra oportunidades claras en este momento. "
                f"Los indicadores están mixtos y no hay una ventaja evidente. La paciencia puede "
                f"ser la mejor estrategia hasta que el panorama se aclare."
            ),
        }
        return explanations.get(signal.signal, "Explicación no disponible.")

    def _get_default_risk_warning(self) -> str:
        """Get default risk warning."""
        return (
            "ADVERTENCIA DE RIESGO: Las criptomonedas son activos altamente volátiles. "
            "Puedes perder parte o la totalidad de tu inversión. Nunca inviertas dinero "
            "que no puedas permitirte perder. El rendimiento pasado no garantiza resultados futuros. "
            "Considera buscar asesoramiento financiero profesional antes de tomar decisiones de inversión."
        )

    def _get_default_educational_disclaimer(self) -> str:
        """Get default educational disclaimer."""
        return (
            "DESCARGO DE RESPONSABILIDAD: Esta explicación es únicamente para fines educativos "
            "e informativos. No constituye asesoramiento financiero, recomendación de inversión, "
            "ni oferta para comprar o vender ningún activo. Las decisiones de inversión son "
            "responsabilidad exclusiva del inversor. El autor no se hace responsable de ninguna "
            "pérdida o daño derivado del uso de esta información."
        )