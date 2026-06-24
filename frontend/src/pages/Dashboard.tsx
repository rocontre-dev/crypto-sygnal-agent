/** Main dashboard page - optimized with single API call and improved loading. */

import { useState, useEffect, useCallback, useRef } from 'react';
import { getDashboard } from '../services/api';
import { CryptoCard } from '../components/CryptoCard';
import { ErrorState } from '../components/ErrorState';
import { UpdateStatusBar } from '../components/UpdateStatusBar';
import type { DashboardResponse, DashboardItem, MarketData } from '../types/market';
import './Dashboard.css';

const SUPPORTED_SYMBOLS = ['BTC', 'ETH', 'SOL'];
const SLOW_LOADING_THRESHOLD_MS = 8000;
const MAX_RETRY_ATTEMPTS = 15; // Retry for up to 30 seconds (15 * 2s)
const RETRY_DELAY_MS = 2000; // 2 seconds between retries
const AUTO_REFRESH_INTERVAL_MS = 30000; // Auto-refresh every 30 seconds

export function Dashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSlowMessage, setShowSlowMessage] = useState(false);
  const [dashboardReady, setDashboardReady] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const slowMessageTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const retryTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const autoRefreshTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Check if all required symbols are present in dashboard items
  const hasAllSymbols = useCallback((data: DashboardResponse | null): boolean => {
    if (!data || !data.items || data.items.length === 0) return false;
    const symbols = data.items.map((item) => item.market_data.symbol);
    return SUPPORTED_SYMBOLS.every((s) => symbols.includes(s));
  }, []);

  const loadData = useCallback(async () => {
    // If we already have data, show refreshing state instead of full loading
    if (dashboardData) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError(null);
    setShowSlowMessage(false);
    // Don't reset dashboardReady if we already have data (for smooth refresh)
    if (!dashboardData) {
      setDashboardReady(false);
    }
    setRetryCount(0);

    // Clear any existing timers
    if (slowMessageTimerRef.current) {
      clearTimeout(slowMessageTimerRef.current);
    }
    if (retryTimerRef.current) {
      clearTimeout(retryTimerRef.current);
    }

    // Set timer for slow loading message
    slowMessageTimerRef.current = setTimeout(() => {
      setShowSlowMessage(true);
    }, SLOW_LOADING_THRESHOLD_MS);

    // Internal function to attempt loading
    const attemptLoad = async (attempt: number): Promise<boolean> => {
      try {
        const response = await getDashboard();
        
        // Clear retry timer
        if (retryTimerRef.current) {
          clearTimeout(retryTimerRef.current);
          retryTimerRef.current = null;
        }

        setDashboardData(response);

        // Only show dashboard when all symbols are present
        if (hasAllSymbols(response)) {
          setDashboardReady(true);
        } else {
          setError('Datos incompletos recibidos del backend.');
        }
        
        // Clear loading state on success or non-retryable error
        setLoading(false);
        setRefreshing(false);
        if (slowMessageTimerRef.current) {
          clearTimeout(slowMessageTimerRef.current);
          slowMessageTimerRef.current = null;
        }
        return true; // Done
        
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
        
        // Check if it's a network error (backend unavailable)
        // Match various network error patterns
        const isNetworkError = 
          errorMessage.toLowerCase().includes('fetch') ||
          errorMessage.toLowerCase().includes('network') ||
          errorMessage.toLowerCase().includes('conn') || // connection, connect, etc.
          errorMessage.toLowerCase().includes('err_network') ||
          errorMessage === 'Error desconocido';
        
        if (isNetworkError && attempt < MAX_RETRY_ATTEMPTS) {
          // Schedule retry
          retryTimerRef.current = setTimeout(() => {
            attemptLoad(attempt + 1);
          }, RETRY_DELAY_MS);
          return false; // Still trying
        } else if (isNetworkError) {
          // Max retries reached, show error
          setError('No se pudo conectar con el backend. Verifica que FastAPI esté corriendo en http://localhost:8000.');
          setLoading(false);
          setRefreshing(false);
          if (slowMessageTimerRef.current) {
            clearTimeout(slowMessageTimerRef.current);
            slowMessageTimerRef.current = null;
          }
          return true; // Done
        } else {
          // Non-network error, show immediately
          setError(errorMessage);
          setLoading(false);
          setRefreshing(false);
          if (slowMessageTimerRef.current) {
            clearTimeout(slowMessageTimerRef.current);
            slowMessageTimerRef.current = null;
          }
          return true; // Done
        }
      }
    };

    // Start loading
    await attemptLoad(0);
  }, [hasAllSymbols]);

  // Effect to set up auto-refresh when dashboard is ready
  useEffect(() => {
    if (dashboardReady && !loading && !error) {
      // Clear any existing timer
      if (autoRefreshTimerRef.current) {
        clearInterval(autoRefreshTimerRef.current);
      }

      // Set up auto-refresh
      autoRefreshTimerRef.current = setInterval(() => {
        loadData();
      }, AUTO_REFRESH_INTERVAL_MS);
    }

    return () => {
      if (autoRefreshTimerRef.current) {
        clearInterval(autoRefreshTimerRef.current);
      }
    };
  }, [dashboardReady, loading, error, loadData]);

  // Effect to handle timer cleanup when loading state changes
  useEffect(() => {
    if (!loading) {
      if (slowMessageTimerRef.current) {
        clearTimeout(slowMessageTimerRef.current);
        slowMessageTimerRef.current = null;
      }
      if (retryTimerRef.current) {
        clearTimeout(retryTimerRef.current);
        retryTimerRef.current = null;
      }
      setShowSlowMessage(false);
    }
  }, [loading]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (slowMessageTimerRef.current) {
        clearTimeout(slowMessageTimerRef.current);
      }
      if (retryTimerRef.current) {
        clearTimeout(retryTimerRef.current);
      }
      if (autoRefreshTimerRef.current) {
        clearInterval(autoRefreshTimerRef.current);
      }
    };
  }, []);

  // Initial load
  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="dashboard-loading__overlay">
          <div className="dashboard-loading__spinner"></div>
          <h2 className="dashboard-loading__title">Preparando análisis de mercado...</h2>
          <p className="dashboard-loading__subtitle">Conectando con el backend y cargando datos actualizados.</p>
          {showSlowMessage && (
            <p className="dashboard-loading__slow-message">
              El análisis está tardando más de lo normal.
            </p>
          )}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <header className="dashboard-header">
          <div className="header-content">
            <h1>📈 CryptoSignalAgent</h1>
            <p className="subtitle">Dashboard de Señales de Trading</p>
          </div>
          <button className="refresh-button" onClick={loadData}>
            🔄 Reintentar
          </button>
        </header>
        <div className="dashboard__error-container">
          <ErrorState message={error} onRetry={loadData} />
        </div>
      </div>
    );
  }

  if (!dashboardData || !dashboardReady) {
    return (
      <div className="dashboard">
        <header className="dashboard-header">
          <div className="header-content">
            <h1>📈 CryptoSignalAgent</h1>
            <p className="subtitle">Dashboard de Señales de Trading</p>
          </div>
        </header>
        <div className="dashboard__error-container">
          <ErrorState message="No hay datos disponibles." onRetry={loadData} />
        </div>
      </div>
    );
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
    <div className={`dashboard ${dashboardReady ? 'dashboard--ready' : ''}`}>
      <header className="dashboard-header">
        <div className="header-content">
          <h1>📈 CryptoSignalAgent</h1>
          <p className="subtitle">
            Dashboard de Señales de Trading
            {refreshing && <span className="refreshing-indicator"> • Actualizando...</span>}
          </p>
        </div>
        <button className="refresh-button" onClick={loadData} disabled={refreshing}>
          {refreshing ? '⏳ Actualizando...' : '🔄 Actualizar análisis'}
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