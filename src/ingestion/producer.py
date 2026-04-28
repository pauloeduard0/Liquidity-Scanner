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
        self.last_closed_close_time = None

    def poll_and_publish(self):
        """Poll Binance for klines and publish to Redis"""
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Producer: Polling Binance...")

            # Get 101 klines: 100 closed + 1 current (open)
            klines = self.ingestion.get_klines(symbol="BTCUSDT", interval="5m", limit=101)

            if not klines or len(klines) < 2:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Producer: No klines received")
                return

            # Last item is CURRENT (open) candle
            current_open = klines[-1]
            closed_klines = klines[:-1]

            # Current candle info
            current_open_time = int(current_open[0])
            current_vol = float(current_open[5])
            current_high = float(current_open[2])
            current_low = float(current_open[3])

            # Always update current candle tracking in Redis
            self.redis_client.hset("liquidity:current_candle", mapping={
                "open_time": current_open_time,
                "volume": current_vol,
                "high": current_high,
                "low": current_low,
                "close": float(current_open[4]),
                "timestamp": datetime.now().isoformat()
            })
            self.redis_client.expire("liquidity:current_candle", 600)

            # Log current candle status
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Producer: Current candle (open={datetime.fromtimestamp(current_open_time/1000).strftime('%H:%M:%S')}) vol={current_vol:.2f}")

            # Check for NEW closed candle
            most_recent_closed = closed_klines[-1] if closed_klines else None
            if most_recent_closed:
                closed_close_time = int(most_recent_closed[6])

                if self.last_closed_close_time != closed_close_time:
                    self.last_closed_close_time = closed_close_time
                    closed_klines = closed_klines[-100:]  # Keep last 100

                    data = {
                        "timestamp": datetime.now().isoformat(),
                        "symbol": "BTCUSDT",
                        "interval": "5m",
                        "klines": closed_klines,
                        "current_candle": {
                            "open_time": current_open_time,
                            "volume": current_vol,
                            "high": current_high,
                            "low": current_low
                        }
                    }

                    self.redis_client.rpush("liquidity:klines", json.dumps(data))
                    self.redis_client.ltrim("liquidity:klines", -10, -1)

                    closed_time_str = datetime.fromtimestamp(closed_close_time/1000).strftime('%H:%M:%S')
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Producer: >>> New closed candle at {closed_time_str}, vol={float(most_recent_closed[5]):.2f}")

            # Update status
            self._update_status("producer_alive", datetime.now().isoformat())

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Producer error: {e}")

    def _update_status(self, key, value):
        """Update status in Redis"""
        self.redis_client.hset("liquidity:status", key, value)

    def run(self, interval=5):
        """Run producer loop - poll every 5s"""
        self.running = True
        print(f"Producer started... (polling every {interval}s)")

        while self.running:
            self.poll_and_publish()
            time.sleep(interval)

    def stop(self):
        """Stop producer"""
        self.running = False
        print("Producer stopped.")
