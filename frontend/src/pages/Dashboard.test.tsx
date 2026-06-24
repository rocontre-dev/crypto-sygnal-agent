import { render, screen, waitFor } from '@testing-library/react';
import { Dashboard } from './Dashboard';
import * as api from '../services/api';

// Mock the API module
vi.mock('../services/api', () => ({
  getMarkets: vi.fn(),
  getSignal: vi.fn(),
  getAIExplanation: vi.fn(),
}));

const mockMarketsResponse = {
  data: [
    {
      id: 1,
      symbol: 'BTC',
      price: 67500,
      market_cap: 1300000000000,
      volume_24h: 25000000000,
      change_24h: 2.5,
      timestamp: '2024-01-15T10:30:00Z',
      source: 'coingecko' as const,
    },
    {
      id: 2,
      symbol: 'ETH',
      price: 3500,
      market_cap: 420000000000,
      volume_24h: 12000000000,
      change_24h: -1.2,
      timestamp: '2024-01-15T10:30:00Z',
      source: 'coingecko' as const,
    },
    {
      id: 3,
      symbol: 'SOL',
      price: 150,
      market_cap: 65000000000,
      volume_24h: 3000000000,
      change_24h: 5.8,
      timestamp: '2024-01-15T10:30:00Z',
      source: 'coingecko' as const,
    },
  ],
  count: 3,
};

const mockSignalResponse = {
  symbol: 'BTC',
  signal: 'ENTER',
  confidence_score: 75,
  risk_level: 'MEDIUM',
  reason: 'Test reason',
  stop_loss: 65000,
  take_profit: 70000,
  invalidation_condition: 'Test condition',
  timestamp: '2024-01-15T10:30:00Z',
};

const mockAIExplanationResponse = {
  symbol: 'BTC',
  signal: 'ENTER',
  confidence_score: 75,
  risk_level: 'MEDIUM',
  stop_loss: 65000,
  take_profit: 70000,
  invalidation_condition: 'Test condition',
  technical_summary: 'Test summary',
  plain_spanish_explanation: 'Test explanation',
  risk_warning: 'Test warning',
  educational_disclaimer: 'Test disclaimer',
  timestamp: '2024-01-15T10:30:00Z',
};

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders BTC, ETH, and SOL cards', async () => {
    // Mock API responses
    (api.getMarkets as vi.Mock).mockResolvedValue(mockMarketsResponse);
    (api.getSignal as vi.Mock).mockResolvedValue(mockSignalResponse);
    (api.getAIExplanation as vi.Mock).mockResolvedValue(mockAIExplanationResponse);

    render(<Dashboard />);

    // Wait for the dashboard to load
    await waitFor(() => {
      expect(screen.getByText('📈 CryptoSignalAgent')).toBeInTheDocument();
    });

    // Check that all three symbols are rendered
    expect(screen.getByText('BTC')).toBeInTheDocument();
    expect(screen.getByText('ETH')).toBeInTheDocument();
    expect(screen.getByText('SOL')).toBeInTheDocument();
  });

  it('renders the refresh button', async () => {
    (api.getMarkets as vi.Mock).mockResolvedValue(mockMarketsResponse);
    (api.getSignal as vi.Mock).mockResolvedValue(mockSignalResponse);
    (api.getAIExplanation as vi.Mock).mockResolvedValue(mockAIExplanationResponse);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('🔄 Actualizar análisis')).toBeInTheDocument();
    });
  });

  it('renders the UpdateStatusBar with market data', async () => {
    (api.getMarkets as vi.Mock).mockResolvedValue(mockMarketsResponse);
    (api.getSignal as vi.Mock).mockResolvedValue(mockSignalResponse);
    (api.getAIExplanation as vi.Mock).mockResolvedValue(mockAIExplanationResponse);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Última actualización real:')).toBeInTheDocument();
    });
  });

  it('shows error state when API fails', async () => {
    (api.getMarkets as vi.Mock).mockRejectedValue(new Error('API Error'));

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Error/i)).toBeInTheDocument();
    });
  });
});