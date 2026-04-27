"""Simple console output - PHASE 1 MVP"""

from datetime import datetime

def print_alert(analysis, symbol="BTCUSDT"):
    """Print volume spike alert to console with timestamp"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if analysis and analysis["is_spike"]:
        print(f"[{current_time}] 🚨 ALERT: Volume Spike detected on {symbol}!")
        print(f"   Current volume: {analysis['current_volume']:.2f}")
        print(f"   Average volume: {analysis['avg_volume']:.2f}")
        print(f"   Multiplier: {analysis['multiplier']}x")
    elif analysis:
        print(f"[{current_time}] ✓ {symbol} - Normal volume: {analysis['current_volume']:.2f} (avg: {analysis['avg_volume']:.2f})")

def print_kline(kline):
    """Print candle information"""
    print(f"Kline: Open={kline[1]}, High={kline[2]}, Low={kline[3]}, Close={kline[4]}, Volume={kline[5]}")
