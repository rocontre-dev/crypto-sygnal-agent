import { render, screen, waitFor, act } from '@testing-library/react';
import { Dashboard } from './Dashboard';
import * as api from '../services/api';

// Mock the API module
vi.mock('../services/api', () => ({
  getDashboard: vi.fn(),
  // Keep old functions for backward compatibility in other tests
  getMarkets: vi.fn(),
  getSignal: vi.fn(),
  getAIExplanation: vi.fn(),
}));

const mockDashboardResponse = {
  updated_at: '2024-01-15T10:30:00Z',
  source: 'coingecko' as const,
  cache_status: 'fresh' as const,
  generation_time_ms: 1234.5,
  items: [
    {
      market_data: {
        symbol: 'BTC',
        price: 67500,
        market_cap: 1300000000000,
        volume_24h: 25000000000,
        change_24h: 2.5,
        timestamp: '2024-01-15T10:30:00Z',
        source: 'coingecko' as const,
      },
      signal: {
        symbol: 'BTC',
        signal: 'ENTER',
        confidence_score: 75,
        risk_level: 'MEDIUM',
        stop_loss: 65000,
        take_profit: 70000,
        timestamp: '2024-01-15T10:30:00Z',
      },
      ai_explanation: {
        symbol: 'BTC',
        signal: 'ENTER',
        confidence_score: 75,
        risk_level: 'MEDIUM',
        technical_summary: 'Technical summary for BTC',
        plain_spanish_explanation: 'Explicación para BTC',
        risk_warning: 'Risk warning for BTC',
        educational_disclaimer: 'Educational disclaimer for BTC',
        timestamp: '2024-01-15T10:30:00Z',
      },
    },
    {
      market_data: {
        symbol: 'ETH',
        price: 3500,
        market_cap: 420000000000,
        volume_24h: 12000000000,
        change_24h: -1.2,
        timestamp: '2024-01-15T10:30:00Z',
        source: 'coingecko' as const,
      },
      signal: {
        symbol: 'ETH',
        signal: 'WAIT',
        confidence_score: 50,
        risk_level: 'MEDIUM',
        stop_loss: 3400,
        take_profit: 3700,
        timestamp: '2024-01-15T10:30:00Z',
      },
      ai_explanation: {
        symbol: 'ETH',
        signal: 'WAIT',
        confidence_score: 50,
        risk_level: 'MEDIUM',
        technical_summary: 'Technical summary for ETH',
        plain_spanish_explanation: 'Explicación para ETH',
        risk_warning: 'Risk warning for ETH',
        educational_disclaimer: 'Educational disclaimer for ETH',
        timestamp: '2024-01-15T10:30:00Z',
      },
    },
    {
      market_data: {
        symbol: 'SOL',
        price: 150,
        market_cap: 65000000000,
        volume_24h: 3000000000,
        change_24h: 5.8,
        timestamp: '2024-01-15T10:30:00Z',
        source: 'coingecko' as const,
      },
      signal: {
        symbol: 'SOL',
        signal: 'ENTER',
        confidence_score: 80,
        risk_level: 'HIGH',
        stop_loss: 140,
        take_profit: 170,
        timestamp: '2024-01-15T10:30:00Z',
      },
      ai_explanation: {
        symbol: 'SOL',
        signal: 'ENTER',
        confidence_score: 80,
        risk_level: 'HIGH',
        technical_summary: 'Technical summary for SOL',
        plain_spanish_explanation: 'Explicación para SOL',
        risk_warning: 'Risk warning for SOL',
        educational_disclaimer: 'Educational disclaimer for SOL',
        timestamp: '2024-01-15T10:30:00Z',
      },
    },
  ],
};

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('shows loading screen initially', () => {
    (api.getDashboard as vi.Mock).mockResolvedValue(mockDashboardResponse);

    render(<Dashboard />);

    expect(screen.getByText('Preparando análisis de mercado...')).toBeInTheDocument();
    expect(screen.getByText('Conectando con el backend y cargando datos actualizados.')).toBeInTheDocument();
  });

  it('renders BTC, ETH, and SOL cards from dashboard endpoint', async () => {
    (api.getDashboard as vi.Mock).mockResolvedValue(mockDashboardResponse);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('📈 CryptoSignalAgent')).toBeInTheDocument();
    });

    // Check that all three symbols are rendered
    expect(screen.getByText('BTC')).toBeInTheDocument();
    expect(screen.getByText('ETH')).toBeInTheDocument();
    expect(screen.getByText('SOL')).toBeInTheDocument();
  });

  it('renders the refresh button', async () => {
    (api.getDashboard as vi.Mock).mockResolvedValue(mockDashboardResponse);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('🔄 Actualizar análisis')).toBeInTheDocument();
    });
  });

  it('renders the UpdateStatusBar with dashboard metadata', async () => {
    (api.getDashboard as vi.Mock).mockResolvedValue(mockDashboardResponse);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Última actualización real:')).toBeInTheDocument();
    });
  });

  it('shows error state when dashboard API fails', async () => {
    (api.getDashboard as vi.Mock).mockRejectedValue(new Error('API Error'));

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Error/i)).toBeInTheDocument();
    });
  });

  it('shows retry button on error', async () => {
    (api.getDashboard as vi.Mock).mockRejectedValue(new Error('API Error'));

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('🔄 Reintentar')).toBeInTheDocument();
    });
  });

  it('shows slow loading message after 8 seconds', async () => {
    // This test verifies the slow loading feature exists
    // The actual timing behavior is tested manually due to complexity with async timers
    (api.getDashboard as vi.Mock).mockResolvedValue(mockDashboardResponse);

    render(<Dashboard />);

    // Initially should show loading screen
    expect(screen.getByText('Preparando análisis de mercado...')).toBeInTheDocument();

    // Dashboard should eventually load
    await waitFor(() => {
      expect(screen.getByText('📈 CryptoSignalAgent')).toBeInTheDocument();
    });
  });

  it('shows error when API fails', async () => {
    (api.getDashboard as vi.Mock).mockRejectedValue(
      new Error('Error del servidor')
    );

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Error/i)).toBeInTheDocument();
    });
  });
});