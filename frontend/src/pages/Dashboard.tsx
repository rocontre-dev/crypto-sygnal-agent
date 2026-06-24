/** Main dashboard page - optimized with single API call. */

import { useState, useEffect, useCallback } from 'react';
import { getDashboard } from '../services/api';
import { CryptoCard } from '../components/CryptoCard';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { UpdateStatusBar } from '../components/UpdateStatusBar';
import type { DashboardResponse, DashboardItem, MarketData } from '../types/market';
import './Dashboard.css';

const SUPPORTED_SYMBOLS = ['BTC', 'ETH', 'SOL'];

export function Dashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await getDashboard();
      setDashboardData(response);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) {
    return <LoadingState message="Cargando análisis de mercado..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={loadData} />;
  }

  if (!dashboardData) {
    return <ErrorState message="No hay datos disponibles." onRetry={loadData} />;
  }

  // Convert dashboard items to the format expected by CryptoCard
  const getMarketDataForSymbol = (symbol: string, item: DashboardItem): MarketData => ({
    id: null,
    symbol: item.market_data.symbol,
    price: item.market_data.price,
    market_cap: item.market_data.market_cap,
    volume_24h: item.market_data.volume_24h,
    change_24h: item.market_data.change_24h,
    timestamp: item.market_data.timestamp,
    source: item.market_data.source,
  });

  // Create market data list for UpdateStatusBar
  const marketDataList: MarketData[] = dashboardData.items.map((item) => ({
    id: null,
    symbol: item.market_data.symbol,
    price: item.market_data.price,
    market_cap: item.market_data.market_cap,
    volume_24h: item.market_data.volume_24h,
    change_24h: item.market_data.change_24h,
    timestamp: item.market_data.timestamp,
    source: item.market_data.source,
  }));

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>📈 CryptoSignalAgent</h1>
          <p className="subtitle">Dashboard de Señales de Trading</p>
        </div>
        <button className="refresh-button" onClick={loadData}>
          🔄 Actualizar análisis
        </button>
      </header>

      <UpdateStatusBar
        marketData={marketDataList}
        dashboardMeta={{
          updated_at: dashboardData.updated_at,
          source: dashboardData.source,
          cache_status: dashboardData.cache_status,
          generation_time_ms: dashboardData.generation_time_ms,
        }}
      />

      <div className="cards-grid">
        {SUPPORTED_SYMBOLS.map((symbol) => {
          const item = dashboardData.items.find(
            (i) => i.market_data.symbol === symbol
          );
          if (!item) {
            return (
              <div key={symbol} className="crypto-card crypto-card--missing">
                <p>No hay datos disponibles para {symbol}</p>
              </div>
            );
          }

          // Get signal reasoning from AI explanation
          const getSignalReason = (signalType: string): string => {
            const reasons: Record<string, string> = {
              ENTER: 'Señal de COMPRA detectada basada en análisis técnico.',
              EXIT: 'Señal de VENTA detectada basada en análisis técnico.',
              REDUCE: 'Señal de REDUCIR posición detectada.',
              WAIT: 'Condiciones mixtas, se recomienda esperar.',
            };
            return reasons[signalType] || 'Análisis técnico en curso.';
          };

          return (
            <CryptoCard
              key={symbol}
              marketData={getMarketDataForSymbol(symbol, item)}
              signal={{
                symbol: item.signal.symbol,
                signal: item.signal.signal as 'ENTER' | 'WAIT' | 'REDUCE' | 'EXIT',
                confidence_score: item.signal.confidence_score,
                risk_level: item.signal.risk_level as 'LOW' | 'MEDIUM' | 'HIGH',
                stop_loss: item.signal.stop_loss,
                take_profit: item.signal.take_profit,
                reason: getSignalReason(item.signal.signal),
                invalidation_condition: 'Si el precio rompe soportes/resistencias clave.',
                timestamp: item.signal.timestamp,
              }}
              aiExplanation={{
                symbol: item.ai_explanation.symbol,
                signal: item.ai_explanation.signal as 'ENTER' | 'WAIT' | 'REDUCE' | 'EXIT',
                confidence_score: item.ai_explanation.confidence_score,
                risk_level: item.ai_explanation.risk_level as 'LOW' | 'MEDIUM' | 'HIGH',
                stop_loss: item.signal.stop_loss,
                take_profit: item.signal.take_profit,
                invalidation_condition: 'Si el precio rompe soportes/resistencias clave.',
                technical_summary: item.ai_explanation.technical_summary,
                plain_spanish_explanation: item.ai_explanation.plain_spanish_explanation,
                risk_warning: item.ai_explanation.risk_warning,
                educational_disclaimer: item.ai_explanation.educational_disclaimer,
                timestamp: item.ai_explanation.timestamp,
              }}
            />
          );
        })}
      </div>

      <footer className="dashboard-footer">
        <p>
          ⚠️ Las criptomonedas son activos volátiles. Esta información es solo para fines educativos.
        </p>
      </footer>
    </div>
  );
}