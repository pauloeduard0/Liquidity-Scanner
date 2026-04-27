"""Consumer - reads from Redis, processes data, and generates signals - PHASE 2"""

import json
import time
from datetime import datetime

from src.processing.volume_analyzer import analyze_klines
from src.processing.signal_engine import SignalEngine
import redis


class Consumer:
    def __init__(self, redis_host="localhost", redis_port=6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.signal_engine = SignalEngine()
        self.running = False

    def process_next(self):
        """Pop next item from Redis and process"""
        try:
            # Pop from left (oldest first)
            data_json = self.redis_client.lpop("liquidity:klines")

            if not data_json:
                return None

            data = json.loads(data_json)
            klines = data.get("klines", [])

            if not klines or len(klines) < 2:
                return None

            # Analyze volume
            analysis = analyze_klines(klines, multiplier=2)

            if not analysis:
                return None

            # Run through signal engine
            signal = self.signal_engine.evaluate(klines, analysis)

            # Store results in Redis
            self._store_signal(signal)
            self._update_status("consumer_alive", datetime.now().isoformat())

            return {"analysis": analysis, "signal": signal}

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Consumer error: {e}")
            return None

    def _store_signal(self, signal):
        """Store signal in Redis lists (capped)"""
        if signal:
            signal_data = {
                "timestamp": datetime.now().isoformat(),
                "signal": signal
            }
            # Store in signals list (keep last 100)
            self.redis_client.rpush("liquidity:signals", json.dumps(signal_data))
            self.redis_client.ltrim("liquidity:signals", -100, -1)

            # Also store in history (keep last 500)
            self.redis_client.rpush("liquidity:history", json.dumps(signal_data))
            self.redis_client.ltrim("liquidity:history", -500, -1)

    def _update_status(self, key, value):
        """Update system status in Redis hash"""
        self.redis_client.hset("liquidity:status", key, value)

    def run(self, poll_interval=5):
        """Run consumer loop"""
        self.running = True
        print("Consumer started...")

        while self.running:
            result = self.process_next()

            if result:
                analysis = result["analysis"]
                signal = result["signal"]

                if signal:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SIGNAL: {signal['type']} - {signal.get('reason', '')}")
                elif analysis:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No signal. Volume: {analysis['current_volume']:.2f} (avg: {analysis['avg_volume']:.2f})")

            time.sleep(poll_interval)

    def stop(self):
        """Stop consumer"""
        self.running = False
        print("Consumer stopped.")
