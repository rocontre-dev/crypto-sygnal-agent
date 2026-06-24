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