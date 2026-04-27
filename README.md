# Liquidity Scanner - PHASE 1 MVP

Liquidity scanner using Binance data.

## Structure

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
