import { render, screen } from '@testing-library/react';
import { UpdateStatusBar } from './UpdateStatusBar';
import type { MarketData } from '../types/market';

describe('UpdateStatusBar', () => {
  const mockMarketData: MarketData[] = [
    {
      id: 1,
      symbol: 'BTC',
      price: 67500,
      market_cap: 1300000000000,
      volume_24h: 25000000000,
      change_24h: 2.5,
      timestamp: '2024-01-15T10:30:00Z',
      source: 'coingecko',
    },
    {
      id: 2,
      symbol: 'ETH',
      price: 3500,
      market_cap: 420000000000,
      volume_24h: 12000000000,
      change_24h: -1.2,
      timestamp: '2024-01-15T10:30:00Z',
      source: 'coingecko',
    },
    {
      id: 3,
      symbol: 'SOL',
      price: 150,
      market_cap: 65000000000,
      volume_24h: 3000000000,
      change_24h: 5.8,
      timestamp: '2024-01-15T10:30:00Z',
      source: 'coingecko',
    },
  ];

  const mockFallbackData: MarketData[] = [
    {
      id: 1,
      symbol: 'BTC',
      price: 67500,
      market_cap: 1300000000000,
      volume_24h: 25000000000,
      change_24h: 2.5,
      timestamp: '2024-01-15T10:30:00Z',
      source: 'mock',
    },
    {
      id: 2,
      symbol: 'ETH',
      price: 3500,
      market_cap: 420000000000,
      volume_24h: 12000000000,
      change_24h: -1.2,
      timestamp: '2024-01-15T10:30:00Z',
      source: 'mock',
    },
    {
      id: 3,
      symbol: 'SOL',
      price: 150,
      market_cap: 65000000000,
      volume_24h: 3000000000,
      change_24h: 5.8,
      timestamp: '2024-01-15T10:30:00Z',
      source: 'mock',
    },
  ];

  it('shows CoinGecko when all data source is coingecko', () => {
    render(<UpdateStatusBar marketData={mockMarketData} />);

    expect(screen.getByText('Última actualización real:')).toBeInTheDocument();
    expect(screen.getByText(/Fuente: CoinGecko/)).toBeInTheDocument();
    expect(screen.getByText('Estado: Datos reales')).toBeInTheDocument();
  });

  it('shows fallback when any data source is mock', () => {
    render(<UpdateStatusBar marketData={mockFallbackData} />);

    expect(screen.getByText('Última actualización real:')).toBeInTheDocument();
    expect(screen.getByText('Fuente: Datos simulados')).toBeInTheDocument();
    expect(screen.getByText('Estado: Fallback activo')).toBeInTheDocument();
  });

  it('shows "no disponible" when market data is empty', () => {
    render(<UpdateStatusBar marketData={[]} />);

    expect(screen.getByText('Última actualización:')).toBeInTheDocument();
    expect(screen.getByText('no disponible')).toBeInTheDocument();
  });

  it('shows "no disponible" when market data is null', () => {
    render(<UpdateStatusBar marketData={[] as unknown as undefined} />);

    expect(screen.getByText('Última actualización:')).toBeInTheDocument();
    expect(screen.getByText('no disponible')).toBeInTheDocument();
  });
});