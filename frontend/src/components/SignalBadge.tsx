/** Signal badge component with color coding. */

import type { SignalType } from '../types/signal';
import './SignalBadge.css';

interface SignalBadgeProps {
  signal: SignalType;
}

const signalLabels: Record<SignalType, string> = {
  ENTER: 'COMPRA',
  WAIT: 'ESPERA',
  REDUCE: 'REDUCIR',
  EXIT: 'SALIDA',
};

export function SignalBadge({ signal }: SignalBadgeProps) {
  return (
    <span className={`signal-badge signal-badge--${signal.toLowerCase()}`}>
      {signalLabels[signal]}
    </span>
  );
}