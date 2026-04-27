"""Producer - polls Binance and publishes to Redis - PHASE 2"""

import json
import time
from datetime import datetime

from src.ingestion.binance_client import BinanceDataIngestion
import redis


class Producer:
    def __init__(self, redis_host="localhost", redis_port=6379):
        self.ingestion = BinanceDataIngestion()
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.running = False

    def poll_and_publish(self):
        """Poll Binance for klines and publish to Redis"""
        try:
            klines = self.ingestion.get_klines(symbol="BTCUSDT", interval="5m", limit=100)

            # Prepare data with timestamp
            data = {
                "timestamp": datetime.now().isoformat(),
                "symbol": "BTCUSDT",
                "interval": "5m",
                "klines": klines
            }

            # Push to Redis list
            self.redis_client.rpush("liquidity:klines", json.dumps(data))

            # Trim list to keep last 10 entries
            self.redis_client.ltrim("liquidity:klines", -10, -1)

            # Update status
            self._update_status("producer_alive", datetime.now().isoformat())

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Producer: Published {len(klines)} klines to Redis")

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Producer error: {e}")

    def _update_status(self, key, value):
        """Update status in Redis"""
        self.redis_client.hset("liquidity:status", key, value)

    def run(self, interval=60):
        """Run producer loop"""
        self.running = True
        print("Producer started...")

        while self.running:
            self.poll_and_publish()
            time.sleep(interval)

    def stop(self):
        """Stop producer"""
        self.running = False
        print("Producer stopped.")
