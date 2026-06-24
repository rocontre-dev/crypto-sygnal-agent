/** Cryptocurrency card component displaying market data, signal, and AI explanation. */

import type { MarketData } from '../types/market';
import type { TradingSignal } from '../types/signal';
import type { AIExplanation } from '../types/aiExplanation';
import { SignalBadge } from './SignalBadge';
import { RiskBadge } from './RiskBadge';
import { AIExplanationPanel } from './AIExplanationPanel';
import './CryptoCard.css';

interface CryptoCardProps {
  marketData: MarketData;
  signal: TradingSignal;
  aiExplanation: AIExplanation;
}

function formatPrice(price: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(price);
}

function formatVolume(volume: number): string {
  if (volume >= 1e9) {
    return `$${(volume / 1e9).toFixed(1)}B`;
  }
  if (volume >= 1e6) {
    return `$${(volume / 1e6).toFixed(1)}M`;
  }
  return formatPrice(volume);
}

function formatPercent(value: number): string {
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
}

export function CryptoCard({ marketData, signal, aiExplanation }: CryptoCardProps) {
  const changePositive = marketData.change_24h >= 0;

  return (
    <div className="crypto-card">
      <div className="crypto-card-header">
        <div className="crypto-symbol">
          <span className="symbol-icon">{marketData.symbol}</span>
          <h3>{marketData.symbol}/USD</h3>
        </div>
        <SignalBadge signal={signal.signal} />
      </div>

      <div className="crypto-card-price">
        <span className="price">{formatPrice(marketData.price)}</span>
        <span className={`change ${changePositive ? 'positive' : 'negative'}`}>
          {formatPercent(marketData.change_24h)}
        </span>
      </div>

      <div className="crypto-card-stats">
        <div className="stat">
          <span className="stat-label">Volumen 24h</span>
          <span className="stat-value">{formatVolume(marketData.volume_24h)}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Confianza</span>
          <span className="stat-value">
            <div className="confidence-bar">
              <div
                className="confidence-fill"
                style={{ width: `${signal.confidence_score}%` }}
              />
            </div>
            {signal.confidence_score.toFixed(0)}%
          </span>
        </div>
        <div className="stat">
          <span className="stat-label">Riesgo</span>
          <RiskBadge risk={signal.risk_level} />
        </div>
      </div>

      <div className="crypto-card-levels">
        {signal.stop_loss !== null && signal.take_profit !== null ? (
          <>
            <div className="level">
              <span className="level-label">Stop Loss</span>
              <span className="level-value stop-loss">{formatPrice(signal.stop_loss)}</span>
            </div>
            <div className="level">
              <span className="level-label">Take Profit</span>
              <span className="level-value take-profit">{formatPrice(signal.take_profit)}</span>
            </div>
          </>
        ) : (
          <div className="level no-levels">
            <span className="level-value">—</span>
            <span className="level-note">No hay operación activa en este momento.</span>
          </div>
        )}
      </div>

      <div className="crypto-card-reason">
        <h5>Señal</h5>
        <p>{signal.reason}</p>
      </div>

      {aiExplanation && <AIExplanationPanel explanation={aiExplanation} />}
    </div>
  );
}