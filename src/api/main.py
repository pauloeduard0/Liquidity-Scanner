"""FastAPI Backend - PHASE 2"""

import json
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis

app = FastAPI(title="Liquidity Scanner API", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


@app.get("/")
async def root():
    """API root"""
    return {
        "name": "Liquidity Scanner API",
        "version": "2.0",
        "endpoints": ["/signals", "/history", "/status"]
    }


@app.get("/signals")
async def get_signals(limit: int = 10):
    """
    Get current/latest signals
    Query param: limit (default 10, max 100)
    """
    limit = min(limit, 100)

    try:
        signals_raw = redis_client.lrange("liquidity:signals", -limit, -1)
        signals = [json.loads(s) for s in signals_raw]
        return {
            "count": len(signals),
            "signals": list(reversed(signals))  # Most recent first
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_history(limit: int = 50):
    """
    Get historical events and signals
    Query param: limit (default 50, max 500)
    """
    limit = min(limit, 500)

    try:
        history_raw = redis_client.lrange("liquidity:history", -limit, -1)
        history = [json.loads(h) for h in history_raw]
        return {
            "count": len(history),
            "history": list(reversed(history))  # Most recent first
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """
    Get system health status
    """
    try:
        status = redis_client.hgetall("liquidity:status")

        # Check if producer/consumer are alive (last update within 2 minutes)
        now = datetime.now()

        producer_alive = False
        consumer_alive = False

        if "producer_alive" in status:
            from datetime import datetime as dt
            last_check = dt.fromisoformat(status["producer_alive"])
            diff = (now - last_check).total_seconds()
            producer_alive = diff < 120  # 2 minutes

        if "consumer_alive" in status:
            from datetime import datetime as dt
            last_check = dt.fromisoformat(status["consumer_alive"])
            diff = (now - last_check).total_seconds()
            consumer_alive = diff < 120  # 2 minutes

        return {
            "producer_alive": producer_alive,
            "consumer_alive": consumer_alive,
            "last_producer_check": status.get("producer_alive"),
            "last_consumer_check": status.get("consumer_alive"),
            "signals_count": redis_client.llen("liquidity:signals"),
            "history_count": redis_client.llen("liquidity:history"),
            "klines_pending": redis_client.llen("liquidity:klines")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
