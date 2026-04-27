"""Binance data client - PHASE 1 MVP"""

import requests
from binance.client import Client
import websockets
import asyncio

class BinanceDataIngestion:
    def __init__(self, api_key=None, api_secret=None):
        self.client = Client(api_key, api_secret)

    def get_klines(self, symbol="BTCUSDT", interval="5m", limit=100):
        """Get historical klines (candles)"""
        return self.client.get_klines(symbol=symbol, interval=interval, limit=limit)

    def get_recent_trades(self, symbol="BTCUSDT", limit=500):
        """Get recent trades"""
        return self.client.get_recent_trades(symbol=symbol, limit=limit)

    async def stream_klines(self, symbol="btcusdt", interval="5m", callback=None):
        """WebSocket stream for real-time candles"""
        uri = f"wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}"

        async with websockets.connect(uri) as websocket:
            while True:
                message = await websocket.recv()
                if callback:
                    callback(message)
                else:
                    print(message)
