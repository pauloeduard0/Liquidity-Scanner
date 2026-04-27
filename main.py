"""Liquidity Scanner - PHASE 1 MVP
Liquidity scanner using Binance data
Runs continuously, checking volume every minute
"""

import time
from src.ingestion.binance_client import BinanceDataIngestion
from src.processing.volume_analyzer import analyze_klines
from src.output.console_output import print_alert

def main():
    print("Liquidity Scanner - PHASE 1 MVP")
    print("Running continuously, checking volume every minute...")
    print("=" * 50)

    # Initialize client
    ingestion = BinanceDataIngestion()

    # Initialize with first data collection
    print("\nInitializing with historical data...")
    klines = ingestion.get_klines(symbol="BTCUSDT", interval="5m", limit=100)
    print(f"Loaded {len(klines)} candles for baseline.\n")

    try:
        while True:
            # Get fresh candles
            klines = ingestion.get_klines(symbol="BTCUSDT", interval="5m", limit=100)

            # Analyze volume
            analysis = analyze_klines(klines, multiplier=2)

            # Output
            print_alert(analysis, symbol="BTCUSDT")

            # Wait 1 minute before next check
            print(f"Next check in 60 seconds...\n")
            time.sleep(60)

    except KeyboardInterrupt:
        print("\nScanner stopped by user.")

if __name__ == "__main__":
    main()
