# API Documentation

This document provides detailed information about the CryptoSignalAgent API endpoints.

## Base URL

```
http://localhost:8000
```

## API Version

All endpoints are prefixed with `/api/v1`.

## Authentication

Currently, the API does not require authentication. This will be implemented in future versions.

## Endpoints

### Health Check (Root)

Check the health status of the API (root endpoint).

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200 OK` - API is healthy
- `500 Internal Server Error` - API is experiencing issues

### Health Check (V1)

Check the health status of the API (versioned endpoint).

**Endpoint:** `GET /api/v1/health`

**Response:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200 OK` - API is healthy
- `500 Internal Server Error` - API is experiencing issues

### Root

Get welcome message and API information.

**Endpoint:** `GET /`

**Response:**
```json
{
  "message": "Welcome to CryptoSignalAgent",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### Market Data

Market data is sourced from the [CoinGecko API](https://www.coingecko.com/en/api). When CoinGecko is unavailable or returns incomplete data, the system falls back to mock data and logs a warning.

#### Get All Markets

Get market data for all supported cryptocurrencies.

**Endpoint:** `GET /api/v1/markets`

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "symbol": "BTC",
      "price": "67500.00",
      "market_cap": "1300000000000.00",
      "volume_24h": "25000000000.00",
      "change_24h": "2.50",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "symbol": "ETH",
      "price": "3500.00",
      "market_cap": "420000000000.00",
      "volume_24h": "12000000000.00",
      "change_24h": "-1.20",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "id": 3,
      "symbol": "SOL",
      "price": "150.00",
      "market_cap": "65000000000.00",
      "volume_24h": "3000000000.00",
      "change_24h": "5.80",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 3
}
```

**Status Codes:**
- `200 OK` - Successfully retrieved market data

**Data Source:**
- Primary: CoinGecko API v3
- Fallback: Mock data (when CoinGecko is unavailable)

#### Get Market by Symbol

Get market data for a specific cryptocurrency.

**Endpoint:** `GET /api/v1/markets/{symbol}`

**Path Parameters:**
- `symbol` - Cryptocurrency symbol (BTC, ETH, SOL)

**Response:**
```json
{
  "id": 1,
  "symbol": "BTC",
  "price": "67500.00",
  "market_cap": "1300000000000.00",
  "volume_24h": "25000000000.00",
  "change_24h": "2.50",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Successfully retrieved market data
- `404 Not Found` - Symbol not found (e.g., invalid symbol like 'INVALID')

**Data Source:**
- Primary: CoinGecko API v3
- Fallback: Mock data (when CoinGecko is unavailable)

### Technical Indicators

#### Get Indicators by Symbol

Get calculated technical indicators for a specific cryptocurrency.

Indicators calculated:
- RSI (14 periods) - Relative Strength Index
- MACD (12, 26, 9) - Moving Average Convergence Divergence
- EMA20, EMA50, EMA200 - Exponential Moving Averages
- SMA20 - Simple Moving Average
- Average Volume (20 periods)
- Percent Change

**Endpoint:** `GET /api/v1/indicators/{symbol}`

**Path Parameters:**
- `symbol` - Cryptocurrency symbol (BTC, ETH, SOL)

**Response:**
```json
{
  "symbol": "BTC",
  "rsi": "48.30",
  "macd": "125.80",
  "ema20": "67200.00",
  "ema50": "66450.00",
  "ema200": "61200.00",
  "sma20": "67010.00",
  "avg_volume": "21000000000.00",
  "percent_change": "1.60",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Successfully calculated indicators
- `404 Not Found` - Symbol not supported (e.g., 'INVALID')

### Trading Signals

#### Get Trading Signal by Symbol

Get a trading signal for a specific cryptocurrency based on technical analysis.

The signal engine analyzes technical indicators and generates trading signals with:
- Signal type: ENTER (buy), WAIT (hold), REDUCE (partial sell), EXIT (sell)
- Confidence score: 0-100
- Risk level: LOW, MEDIUM, HIGH
- Stop loss and take profit suggestions
- Reasoning and invalidation conditions (in Spanish)

**Signal Logic:**
- **ENTER**: RSI < 35, price > EMA20, EMA20 > EMA50, MACD > 0
- **EXIT**: RSI > 70, price < EMA20, MACD < 0
- **REDUCE**: RSI > 65, price losing EMA20, or strong negative change
- **WAIT**: Mixed conditions, low confidence

**Endpoint:** `GET /api/v1/signals/{symbol}`

**Path Parameters:**
- `symbol` - Cryptocurrency symbol (BTC, ETH, SOL)

**Response:**
```json
{
  "symbol": "BTC",
  "signal": "ENTER",
  "confidence_score": "75",
  "risk_level": "MEDIUM",
  "reason": "Señal de COMPRA detectada. RSI en zona de sobreventa (32.5). Precio por encima de EMA20. EMA20 > EMA50 (tendencia alcista). MACD positivo (125.80).",
  "stop_loss": "65000.00",
  "take_profit": "70000.00",
  "invalidation_condition": "Si el precio cae por debajo de EMA50 o RSI supera 50 sin romper resistencias clave.",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Successfully generated trading signal
- `404 Not Found` - Symbol not supported (e.g., 'INVALID')

### AI Explanations

#### Get AI Explanation for Trading Signal

Get an AI-generated explanation for a trading signal. The AI explains the existing rule-based signal in clearer Spanish without modifying the original signal decision.

The AI:
- Never modifies the signal decision (ENTER, WAIT, REDUCE, EXIT)
- Never changes confidence_score, risk_level, stop_loss, or take_profit
- Only generates explanatory text (technical_summary, plain_spanish_explanation, risk_warning, educational_disclaimer)
- Falls back to deterministic explanations when OpenAI is unavailable

**Endpoint:** `GET /api/v1/ai-explanations/{symbol}`

**Path Parameters:**
- `symbol` - Cryptocurrency symbol (BTC, ETH, SOL)

**Response:**
```json
{
  "symbol": "BTC",
  "signal": "ENTER",
  "confidence_score": 75.0,
  "risk_level": "MEDIUM",
  "stop_loss": 65000.0,
  "take_profit": 70000.0,
  "invalidation_condition": "Si el precio cae por debajo de EMA50.",
  "technical_summary": "Los indicadores técnicos para BTC muestran condiciones favorables para una posible entrada.",
  "plain_spanish_explanation": "El análisis de BTC sugiere que podría ser un buen momento para considerar una posición.",
  "risk_warning": "ADVERTENCIA DE RIESGO: Las criptomonedas son activos altamente volátiles...",
  "educational_disclaimer": "DESCARGO DE RESPONSABILIDAD: Esta explicación es únicamente para fines educativos...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Successfully generated AI explanation
- `404 Not Found` - Symbol not supported (e.g., 'INVALID')

## Interactive Documentation

The API provides interactive documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Rate Limiting

Rate limiting is not currently implemented but will be added in future versions.

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

## Market History

Get historical OHLC (Open, High, Low, Close) data for cryptocurrencies.

**Endpoint:** `GET /api/v1/history/{symbol}`

**Query Parameters:**
- `timeframe` - Candle timeframe (default: `1d`). Currently only `1d` is supported.

**Response:**
```json
{
  "symbol": "BTC",
  "timeframe": "1d",
  "count": 365,
  "volume_available": false,
  "source": "coingecko_ohlc",
  "candles": [
    {
      "timestamp": "2024-01-15T00:00:00Z",
      "open": 42500.00,
      "high": 43200.00,
      "low": 42100.00,
      "close": 42800.00,
      "volume": null
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Successfully retrieved historical data
- `400 Bad Request` - Invalid or unsupported timeframe (e.g., `4h`, `1h`)
- `404 Not Found` - Symbol not found (e.g., `INVALID`)
- `503 Service Unavailable` - Unable to fetch data and no cache available

**Data Source:**
- Primary: CoinGecko OHLC API v3
- Fallback: Cached data when API is unavailable

**Known Limitations:**
- **No Volume Data**: CoinGecko's free OHLC endpoint provides open, high, low, close prices but does NOT provide trading volume. The `volume` field is always `null` and `volume_available` is always `false`.
- **1d Timeframe Only**: The 4h (4-hour) timeframe is not available from CoinGecko's free OHLC endpoint. Support for 4h may require integration with Binance, Coinbase, or another OHLCV provider in the future.
- **Rate Limits**: CoinGecko free API has strict rate limits (~10-50 calls/minute). When rate limit is exceeded (HTTP 429), the service returns cached data if available, or a 503 error if no cache exists. The service uses caching (default TTL: 3600 seconds) to minimize API calls.
  - **Recommendation**: For production use with higher traffic, consider upgrading to CoinGecko's paid API or implementing a longer cache TTL via `MARKET_HISTORY_CACHE_TTL_SECONDS` environment variable.
- **Historical Depth**: CoinGecko provides up to 365 days of daily OHLC data for supported cryptocurrencies.

## CORS

The API supports Cross-Origin Resource Sharing (CORS) for the following origins:
- http://localhost:5173
- http://localhost:3000
