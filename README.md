# Liquidity Scanner

Liquidity scanner using Binance data.

## Architecture - PHASE 2

Producer-Consumer pattern with Redis as message broker:

```
Binance API → Producer (polls 5m) → [Redis Queue] → Consumer → SignalEngine → Signals API
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

```bash
pip install -r requirements.txt
```

Requirements: `requests`, `websockets`, `python-binance`, `redis`, `fastapi`, `uvicorn`

**Redis** must be running:
```bash
sudo service redis-server start
```

## Usage

```bash
python3 main.py
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

## PHASE 1 - Features (MVP)

- [x] Collect Binance klines (candles)
- [x] Collect recent trades
- [x] Calculate average volume
- [x] Detect volume spike (2x average)
- [x] Console output

## PHASE 2 - Features (Current)

- [x] Producer-Consumer architecture with Redis
- [x] FastAPI REST API
- [x] Signal Engine with trading rules
- [x] ABSORPTION signal detection
- [x] LIQUIDITY_SWEEP signal detection
- [x] Signal persistence in Redis
- [x] System status monitoring
- [x] CORS enabled for frontend integration

```
Liquidity-Scanner/
├── src/
│   ├── ingestion/      # Data collection (API + WebSocket)
│   │   └── binance_client.py
│   ├── processing/     # Volume analysis and spike detection
│   │   └── volume_analyzer.py
│   └── output/         # Output (console, API, etc.)
│       └── console_output.py
├── main.py             # Entry point
├── requirements.txt    # Dependencies
└── README.md
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## PHASE 1 - Features

- [x] Collect Binance klines (candles)
- [x] Collect recent trades
- [x] Calculate average volume
- [x] Detect volume spike (2x average)
- [x] Console output
