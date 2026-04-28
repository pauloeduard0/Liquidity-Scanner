"""Liquidity Scanner - PHASE 2
Orchestrator: starts producer, consumer, and API server
"""

import threading
import time
from datetime import datetime

from src.ingestion.producer import Producer
from src.processing.consumer import Consumer


def run_producer():
    """Run producer in thread"""
    producer = Producer()
    producer.run()  # Default: poll every 5s to track volume accumulation


def run_consumer():
    """Run consumer in thread"""
    consumer = Consumer()
    consumer.run(poll_interval=30)  # Check every 30s, data comes every 5 min


def run_api():
    """Run FastAPI server"""
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=False)


def main():
    print("=" * 60)
    print("  Liquidity Scanner - PHASE 2")
    print("  Professional Architecture with Redis + FastAPI")
    print("=" * 60)
    print()

    # Start producer thread
    producer_thread = threading.Thread(target=run_producer, daemon=True)
    producer_thread.start()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Producer thread started.")

    # Start consumer thread
    consumer_thread = threading.Thread(target=run_consumer, daemon=True)
    consumer_thread.start()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Consumer thread started.")

    # Start API in main thread
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting API server on http://0.0.0.0:8000")
    print(f"   Endpoints: /signals, /history, /status")
    print()

    try:
        run_api()
    except KeyboardInterrupt:
        print("\nShutting down...")
        print("Bye!")


if __name__ == "__main__":
    main()
