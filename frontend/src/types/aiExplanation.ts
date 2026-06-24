/** AI explanation types. */

import type { SignalType, RiskLevel } from './signal';

export interface AIExplanation {
  symbol: string;
  signal: SignalType;
  confidence_score: number;
  risk_level: RiskLevel;
  stop_loss: number;
  take_profit: number;
  invalidation_condition: string;
  technical_summary: string;
  plain_spanish_explanation: string;
  risk_warning: string;
  educational_disclaimer: string;
  timestamp: string;
}