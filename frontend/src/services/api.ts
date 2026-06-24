/** API service for communicating with the backend. */

import type { MarketDataListResponse, DashboardResponse } from '../types/market';
import type { TradingSignal } from '../types/signal';
import type { AIExplanation } from '../types/aiExplanation';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Fetches market data for all supported cryptocurrencies.
 * @throws {ApiError} If the request fails
 */
export async function getMarkets(): Promise<MarketDataListResponse> {
  const response = await fetch(`${API_URL}/api/v1/markets`);

  if (!response.ok) {
    if (response.status === 0) {
      throw new ApiError('No se pudo conectar con el servidor. Verifica que el backend esté ejecutándose.');
    }
    throw new ApiError(`Error al obtener datos del mercado: ${response.statusText}`, response.status);
  }

  return response.json();
}

/**
 * Fetches aggregated dashboard data for all supported cryptocurrencies.
 * This is a single endpoint that returns market data, signals, and AI explanations.
 * @throws {ApiError} If the request fails
 */
export async function getDashboard(): Promise<DashboardResponse> {
  const response = await fetch(`${API_URL}/api/v1/dashboard`);

  if (!response.ok) {
    if (response.status === 0) {
      throw new ApiError('No se pudo conectar con el servidor. Verifica que el backend esté ejecutándose.');
    }
    throw new ApiError(`Error al obtener datos del dashboard: ${response.statusText}`, response.status);
  }

  return response.json();
}

/**
 * Fetches trading signal for a specific symbol.
 * @param symbol - Cryptocurrency symbol (e.g., 'BTC', 'ETH', 'SOL')
 * @throws {ApiError} If the request fails
 */
export async function getSignal(symbol: string): Promise<TradingSignal> {
  const response = await fetch(`${API_URL}/api/v1/signals/${symbol}`);

  if (!response.ok) {
    if (response.status === 0) {
      throw new ApiError('No se pudo conectar con el servidor. Verifica que el backend esté ejecutándose.');
    }
    if (response.status === 404) {
      throw new ApiError(`No hay señal disponible para ${symbol}`);
    }
    throw new ApiError(`Error al obtener señal para ${symbol}: ${response.statusText}`, response.status);
  }

  return response.json();
}

/**
 * Fetches AI explanation for a specific symbol.
 * @param symbol - Cryptocurrency symbol (e.g., 'BTC', 'ETH', 'SOL')
 * @throws {ApiError} If the request fails
 */
export async function getAIExplanation(symbol: string): Promise<AIExplanation> {
  const response = await fetch(`${API_URL}/api/v1/ai-explanations/${symbol}`);

  if (!response.ok) {
    if (response.status === 0) {
      throw new ApiError('No se pudo conectar con el servidor. Verifica que el backend esté ejecutándose.');
    }
    if (response.status === 404) {
      throw new ApiError(`No hay explicación disponible para ${symbol}`);
    }
    throw new ApiError(`Error al obtener explicación para ${symbol}: ${response.statusText}`, response.status);
  }

  return response.json();
}