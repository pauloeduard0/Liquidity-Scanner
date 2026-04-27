"""Signal Engine - trading rules - PHASE 2"""

from datetime import datetime


class SignalEngine:
    """Evaluates market data and generates trading signals"""

    def __init__(self):
        self.recent_highs = []  # Track recent highs for sweep detection
        self.recent_lows = []   # Track recent lows
        self.max_tracking = 10  # Number of candles to track

    def evaluate(self, klines, analysis):
        """
        Evaluate klines and analysis to generate signals
        Returns signal dict or None
        """
        if not klines or len(klines) < 2:
            return None

        # Update recent highs/lows
        self._update_price_levels(klines)

        # Check for absorption
        absorption_signal = self._check_absorption(klines, analysis)
        if absorption_signal:
            return absorption_signal

        # Check for liquidity sweep
        sweep_signal = self._check_liquidity_sweep(klines)
        if sweep_signal:
            return sweep_signal

        return None

    def _update_price_levels(self, klines):
        """Update recent highs and lows tracking"""
        latest = klines[-1]
        high = float(latest[2])
        low = float(latest[3])

        self.recent_highs.append(high)
        self.recent_lows.append(low)

        # Keep only last N candles
        if len(self.recent_highs) > self.max_tracking:
            self.recent_highs.pop(0)
            self.recent_lows.pop(0)

    def _check_absorption(self, klines, analysis):
        """
        Absorption: High volume but price doesn't move much
        Condition: volume spike AND small candle body relative to range
        """
        if not analysis.get("is_spike"):
            return None

        latest = klines[-1]
        open_price = float(latest[1])
        close_price = float(latest[4])
        high = float(latest[2])
        low = float(latest[3])

        candle_range = high - low
        if candle_range == 0:
            return None

        body_ratio = abs(close_price - open_price) / candle_range

        # If body is less than 30% of range, it's absorption
        if body_ratio < 0.3:
            return {
                "type": "ABSORPTION",
                "reason": f"High volume ({analysis['current_volume']:.2f}) but small price movement (body ratio: {body_ratio:.2f})",
                "volume": analysis['current_volume'],
                "avg_volume": analysis['avg_volume'],
                "body_ratio": round(body_ratio, 3),
                "timestamp": datetime.now().isoformat()
            }

        return None

    def _check_liquidity_sweep(self, klines):
        """
        Liquidity Sweep: Breaks recent high/low then quickly reverses
        Condition: New high/low broken, then candle closes back inside range
        """
        if len(klines) < 3 or len(self.recent_highs) < 3:
            return None

        latest = klines[-1]
        prev = klines[-2]

        current_high = float(latest[2])
        current_low = float(latest[3])
        current_close = float(latest[4])
        prev_close = float(prev[4])

        # Recent high/low (excluding current)
        recent_high = max(self.recent_highs[:-1])
        recent_low = min(self.recent_lows[:-1])

        signal = None

        # Check for sweep of recent high
        if current_high > recent_high and current_close < recent_high:
            signal = {
                "type": "LIQUIDITY_SWEEP_HIGH",
                "reason": f"Broke recent high ({recent_high:.2f}) but closed back at {current_close:.2f}",
                "broken_level": recent_high,
                "current_close": current_close,
                "timestamp": datetime.now().isoformat()
            }

        # Check for sweep of recent low
        elif current_low < recent_low and current_close > recent_low:
            signal = {
                "type": "LIQUIDITY_SWEEP_LOW",
                "reason": f"Broke recent low ({recent_low:.2f}) but closed back at {current_close:.2f}",
                "broken_level": recent_low,
                "current_close": current_close,
                "timestamp": datetime.now().isoformat()
            }

        return signal
