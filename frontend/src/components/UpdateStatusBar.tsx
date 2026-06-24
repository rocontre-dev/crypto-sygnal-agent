/** Status bar component showing the last update time and data source. */

import type { MarketData } from '../types/market';
import './UpdateStatusBar.css';

interface DashboardMeta {
  updated_at: string;
  source: "coingecko" | "mock";
  cache_status: "fresh" | "cached";
  generation_time_ms: number;
}

interface UpdateStatusBarProps {
  marketData: MarketData[];
  dashboardMeta?: DashboardMeta;
}

export function UpdateStatusBar({ marketData, dashboardMeta }: UpdateStatusBarProps) {
  // If we have dashboard meta, use it for more accurate info
  if (dashboardMeta && marketData.length > 0) {
    const formattedDate = new Date(dashboardMeta.updated_at).toLocaleString('es-ES', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });

    const isFallback = dashboardMeta.source === "mock";

    return (
      <div className="update-status-bar">
        <span className="update-status-bar__label">Última actualización real:</span>
        <span className="update-status-bar__value">{formattedDate}</span>
        <span className="update-status-bar__separator">|</span>
        <span className="update-status-bar__source">
          Fuente: {isFallback ? 'Datos simulados' : 'CoinGecko'}
        </span>
        <span className="update-status-bar__separator">|</span>
        <span className={`update-status-bar__status ${isFallback ? 'update-status-bar__status--warning' : 'update-status-bar__status--ok'}`}>
          Estado: {isFallback ? 'Fallback activo' : 'Datos reales'}
        </span>
        <span className="update-status-bar__separator">|</span>
        <span className="update-status-bar__cache">
          Caché: {dashboardMeta.cache_status === 'cached' ? '✅ cached' : '🔄 fresh'} ({dashboardMeta.generation_time_ms}ms)
        </span>
      </div>
    );
  }

  // Fallback when no dashboard meta available
  if (!marketData || marketData.length === 0) {
    return (
      <div className="update-status-bar">
        <span className="update-status-bar__label">Última actualización:</span>
        <span className="update-status-bar__value">no disponible</span>
      </div>
    );
  }

  // Find the most recent timestamp among all market data
  const latestTimestamp = marketData.reduce((latest, item) => {
    const itemDate = new Date(item.timestamp);
    return itemDate > latest ? itemDate : latest;
  }, new Date(0));

  // Format the date/time in Spanish using browser locale
  const formattedDate = latestTimestamp.toLocaleString('es-ES', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });

  // Determine source from market data
  // If any item has source="mock", we consider it fallback mode
  const hasMockData = marketData.some((item) => item.source === "mock");
  const isFallback = hasMockData;

  return (
    <div className="update-status-bar">
      <span className="update-status-bar__label">Última actualización real:</span>
      <span className="update-status-bar__value">{formattedDate}</span>
      <span className="update-status-bar__separator">|</span>
      <span className="update-status-bar__source">
        Fuente: {isFallback ? 'Datos simulados' : 'CoinGecko'}
      </span>
      <span className="update-status-bar__separator">|</span>
      <span className={`update-status-bar__status ${isFallback ? 'update-status-bar__status--warning' : 'update-status-bar__status--ok'}`}>
        Estado: {isFallback ? 'Fallback activo' : 'Datos reales'}
      </span>
    </div>
  );
}
