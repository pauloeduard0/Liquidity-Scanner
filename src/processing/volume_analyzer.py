"""Volume analysis and spike detection - PHASE 1 MVP"""

def calculate_average_volume(klines):
    """Calculate average volume based on candles"""
    if not klines:
        return 0
    total_volume = sum(float(kline[5]) for kline in klines)
    return total_volume / len(klines)

def detect_volume_spike(current_volume, avg_volume, multiplier=2):
    """Detect volume spike"""
    return current_volume > avg_volume * multiplier

def analyze_klines(klines, multiplier=2):
    """Analyze candles and return volume spike alerts"""
    if len(klines) < 2:
        return None

    avg_volume = calculate_average_volume(klines[:-1])
    current_volume = float(klines[-1][5])

    is_spike = detect_volume_spike(current_volume, avg_volume, multiplier)

    return {
        "current_volume": current_volume,
        "avg_volume": avg_volume,
        "is_spike": is_spike,
        "multiplier": multiplier
    }
