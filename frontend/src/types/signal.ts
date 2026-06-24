/** Trading signal types. */

export type SignalType = 'ENTER' | 'WAIT' | 'REDUCE' | 'EXIT';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';

export interface TradingSignal {
  symbol: string;
  signal: SignalType;
  confidence_score: number;
  risk_level: RiskLevel;
  reason: string;
  stop_loss: number | null;
  take_profit: number | null;
  invalidation_condition: string;
  timestamp: string;
}
