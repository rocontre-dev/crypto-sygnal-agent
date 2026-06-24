/** Market data types. */

export interface MarketData {
  id: number | null;
  symbol: string;
  price: number;
  market_cap: number;
  volume_24h: number;
  change_24h: number;
  timestamp: string;
  source: "coingecko" | "mock";
}

export interface MarketDataListResponse {
  data: MarketData[];
  count: number;
}

/** Dashboard types for the aggregated endpoint. */

export interface DashboardMarketData {
  symbol: string;
  price: number;
  market_cap: number;
  volume_24h: number;
  change_24h: number;
  timestamp: string;
  source: "coingecko" | "mock";
}

export interface DashboardSignal {
  symbol: string;
  signal: string;
  confidence_score: number;
  risk_level: string;
  stop_loss: number;
  take_profit: number;
  timestamp: string;
}

export interface DashboardAIExplanation {
  symbol: string;
  signal: string;
  confidence_score: number;
  risk_level: string;
  technical_summary: string;
  plain_spanish_explanation: string;
  risk_warning: string;
  educational_disclaimer: string;
  timestamp: string;
}

export interface DashboardItem {
  market_data: DashboardMarketData;
  signal: DashboardSignal;
  ai_explanation: DashboardAIExplanation;
}

export interface DashboardResponse {
  updated_at: string;
  source: "coingecko" | "mock";
  cache_status: "fresh" | "cached";
  generation_time_ms: number;
  items: DashboardItem[];
}
