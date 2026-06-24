/** Risk level badge component with color coding. */

import type { RiskLevel } from '../types/signal';
import './RiskBadge.css';

interface RiskBadgeProps {
  risk: RiskLevel;
}

const riskLabels: Record<RiskLevel, string> = {
  LOW: 'BAJO',
  MEDIUM: 'MEDIO',
  HIGH: 'ALTO',
};

export function RiskBadge({ risk }: RiskBadgeProps) {
  return (
    <span className={`risk-badge risk-badge--${risk.toLowerCase()}`}>
      {riskLabels[risk]}
    </span>
  );
}