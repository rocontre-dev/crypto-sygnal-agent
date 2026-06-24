/** Main dashboard page. */

import { useState, useEffect, useCallback } from 'react';
import { getMarkets, getSignal, getAIExplanation } from '../services/api';
import { CryptoCard } from '../components/CryptoCard';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import type { MarketData } from '../types/market';
import type { TradingSignal } from '../types/signal';
import type { AIExplanation } from '../types/aiExplanation';
import './Dashboard.css';

const SUPPORTED_SYMBOLS = ['BTC', 'ETH', 'SOL'];

interface SymbolData {
  marketData: MarketData;
  signal: TradingSignal;
  aiExplanation: AIExplanation;
}

interface DashboardData {
  [symbol: string]: SymbolData;
}

export function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch all market data
      const marketsResponse = await getMarkets();
      const marketDataMap: { [symbol: string]: MarketData } = {};
      for (const item of marketsResponse.data) {
        marketDataMap[item.symbol] = item;
      }

      // Fetch signals and AI explanations for each symbol
      const result: DashboardData = {};

      for (const symbol of SUPPORTED_SYMBOLS) {
        try {
          const [signal, aiExplanation] = await Promise.all([
            getSignal(symbol),
            getAIExplanation(symbol),
          ]);

          const marketData = marketDataMap[symbol];
          if (marketData) {
            result[symbol] = {
              marketData,
              signal,
              aiExplanation,
            };
          }
        } catch (err) {
          console.error(`Error loading data for ${symbol}:`, err);
        }
      }

      if (Object.keys(result).length === 0) {
        setError('No se pudieron cargar los datos. Verifica que el backend esté ejecutándose.');
      } else {
        setData(result);
      }
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

  if (!data) {
    return <ErrorState message="No hay datos disponibles." onRetry={loadData} />;
  }

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

      <div className="cards-grid">
        {SUPPORTED_SYMBOLS.map((symbol) => {
          const symbolData = data[symbol];
          if (!symbolData) {
            return (
              <div key={symbol} className="crypto-card crypto-card--missing">
                <p>No hay datos disponibles para {symbol}</p>
              </div>
            );
          }

          return (
            <CryptoCard
              key={symbol}
              marketData={symbolData.marketData}
              signal={symbolData.signal}
              aiExplanation={symbolData.aiExplanation}
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