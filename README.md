# Liquidity Scanner

A liquidity scanner for cryptocurrencies using Binance data. Detects institutional patterns such as volume absorption and stop hunts (liquidity sweeps).

## Architecture

Producer-Consumer pattern with Redis as message broker:

```
Binance API → Producer (polls 5m) → [Redis Queue] → Consumer → SignalEngine → FastAPI
```

- **Producer**: Polls Binance klines (5m timeframe) every 5 minutes, publishes to Redis
- **Consumer**: Reads from Redis, processes via SignalEngine, stores signals
- **Redis**: Message queue (`liquidity:klines`) + storage (`liquidity:signals`, `liquidity:history`, `liquidity:status`)
- **FastAPI**: REST API to query signals and status

## Structure

```
Liquidity-Scanner/
├── src/
│   ├── ingestion/          # Data collection
│   │   ├── binance_client.py  # Binance API client (REST + WebSocket)
│   │   └── producer.py        # Polls Binance, publishes to Redis
│   ├── processing/        # Analysis and signal generation
│   │   ├── volume_analyzer.py # Volume spike detection
│   │   ├── signal_engine.py   # Trading rules engine
│   │   └── consumer.py        # Reads Redis, processes, generates signals
│   ├── api/               # FastAPI backend
│   │   └── main.py           # Endpoints: /signals, /history, /status
│   └── output/            # Output handlers
│       └── console_output.py
├── main.py                 # Entry point (orchestrator)
├── requirements.txt        # Dependencies
└── README.md
```

## Installation

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Redis

**Option A - Docker (recommended):**
```bash
docker run -d -p 6379:6379 redis
```

**Option B - Local (Ubuntu/Debian):**
```bash
sudo service redis-server start
```

**Option C - WSL:**
```bash
sudo service redis-server start
```

### 3. Run the application

```bash
python main.py
```

This starts:
- Producer thread (polls every 5 min)
- Consumer thread (checks every 30s)
- FastAPI server on `http://0.0.0.0:8000`

## API Endpoints

| Endpoint | Description | Query Params |
|----------|-------------|--------------|
| `GET /` | API info | - |
| `GET /signals` | Latest trading signals | `limit` (default 10, max 100) |
| `GET /history` | Historical events | `limit` (default 50, max 500) |
| `GET /status` | System health check | - |

### Status Response Example

```json
{
  "producer_alive": true,
  "consumer_alive": true,
  "last_producer_check": "2026-04-27T12:37:19",
  "last_consumer_check": "2026-04-27T12:37:19",
  "signals_count": 2,
  "history_count": 5,
  "klines_pending": 0
}
```

## Signal Types

| Signal | Condition |
|--------|-----------|
| **ABSORPTION** | High volume spike + small candle body relative to range (price doesn't move despite heavy volume) |
| **LIQUIDITY_SWEEP_LOW** | Price breaks recent low but closes back above it (stop hunt) |
| **LIQUIDITY_SWEEP_HIGH** | Price breaks recent high but closes back below it (stop hunt) |

## Technologies

| Technology | Purpose |
|------------|---------|
| **Python 3** | Main programming language |
| **python-binance** | Binance API client (REST) |
| **Redis** | Message broker + signal storage |
| **FastAPI** | REST API backend |
| **uvicorn** | ASGI server |
| **websockets** | Prepared for real-time streaming |
| **requests** | HTTP client |
