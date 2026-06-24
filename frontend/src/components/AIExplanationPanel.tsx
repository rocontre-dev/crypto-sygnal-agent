/** AI explanation panel component. */

import type { AIExplanation } from '../types/aiExplanation';
import './AIExplanationPanel.css';

interface AIExplanationPanelProps {
  explanation: AIExplanation;
}

export function AIExplanationPanel({ explanation }: AIExplanationPanelProps) {
  return (
    <div className="ai-explanation-panel">
      <div className="ai-panel-header">
        <span className="ai-icon">🤖</span>
        <h4>Análisis de IA</h4>
      </div>

      <div className="ai-panel-section">
        <h5>Resumen Técnico</h5>
        <p>{explanation.technical_summary}</p>
      </div>

      <div className="ai-panel-section">
        <h5>Explicación</h5>
        <p>{explanation.plain_spanish_explanation}</p>
      </div>

      <div className="ai-panel-section ai-panel-section--warning">
        <h5>⚠️ Advertencia de Riesgo</h5>
        <p>{explanation.risk_warning}</p>
      </div>

      <div className="ai-panel-section ai-panel-section--disclaimer">
        <h5>Descargo de Responsabilidad</h5>
        <p>{explanation.educational_disclaimer}</p>
      </div>
    </div>
  );
}