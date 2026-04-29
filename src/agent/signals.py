"""
Technical analysis signal generator for Meteora DLMM pools.
Generates BUY/SELL/HOLD signals based on RSI, volatility, and trend.
"""

import statistics
from dataclasses import dataclass
from typing import Optional
from .meteora_client import PoolData


@dataclass
class TradingSignal:
    """Trading signal with confidence score."""
    pool_address: str
    signal: str  # BUY, SELL, HOLD
    confidence: float  # 0.0 to 1.0
    rsi: float
    volatility: float
    trend: float
    reasoning: str


class SignalGenerator:
    """Generates trading signals from pool data."""

    def __init__(
        self,
        lookback_periods: int = 14,
        rsi_oversold: float = 30.0,
        rsi_overbought: float = 70.0,
    ):
        self.lookback_periods = lookback_periods
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought

    def calculate_rsi(self, prices: list[float]) -> float:
        """
        Calculate Relative Strength Index.

        Args:
            prices: List of historical prices

        Returns:
            RSI value (0-100)
        """
        if len(prices) < 2:
            return 50.0  # Neutral

        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d for d in deltas if d > 0]
        losses = [-d for d in deltas if d < 0]

        avg_gain = statistics.mean(gains) if gains else 0.0
        avg_loss = statistics.mean(losses) if losses else 0.0

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_volatility(self, prices: list[float]) -> float:
        """
        Calculate price volatility (standard deviation).

        Args:
            prices: List of historical prices

        Returns:
            Volatility score (0.0 to 1.0)
        """
        if len(prices) < 2:
            return 0.0

        mean = statistics.mean(prices)
        variance = statistics.variance(prices, mean) if len(prices) > 1 else 0
        std_dev = variance ** 0.5

        # Normalize: higher std dev = higher volatility
        # Cap at 1.0
        volatility = std_dev / mean if mean > 0 else 0.0
        return min(volatility, 1.0)

    def calculate_trend(self, prices: list[float]) -> float:
        """
        Calculate trend direction using simple moving average.

        Args:
            prices: List of historical prices

        Returns:
            Trend score (-1.0 to 1.0)
            -1.0 = strong downtrend
             0.0 = neutral
            +1.0 = strong uptrend
        """
        if len(prices) < self.lookback_periods:
            return 0.0

        # Compare recent average to older average
        mid = len(prices) // 2
        recent_avg = statistics.mean(prices[mid:])
        older_avg = statistics.mean(prices[:mid])

        if older_avg == 0:
            return 0.0

        change = (recent_avg - older_avg) / older_avg
        # Normalize to -1 to 1 range
        return max(-1.0, min(1.0, change))

    def generate_signal(
        self,
        pool: PoolData,
        historical_prices: Optional[list[float]] = None,
    ) -> TradingSignal:
        """
        Generate a trading signal for a pool.

        Args:
            pool: Pool data from Meteora
            historical_prices: Optional price history for analysis

        Returns:
            TradingSignal with recommendation and confidence
        """
        if historical_prices is None:
            # Use pool price as single data point
            historical_prices = [pool.price]

        rsi = self.calculate_rsi(historical_prices)
        volatility = self.calculate_volatility(historical_prices)
        trend = self.calculate_trend(historical_prices)

        # Signal determination
        if rsi < self.rsi_oversold and trend > 0:
            signal = "BUY"
            reasoning = f"RSI oversold ({rsi:.1f}) with uptrend detected"
            confidence = 0.5 + (0.3 * (1 - rsi / 100)) + (0.2 * trend)
        elif rsi > self.rsi_overbought and trend < 0:
            signal = "SELL"
            reasoning = f"RSI overbought ({rsi:.1f}) with downtrend detected"
            confidence = 0.5 + (0.3 * (rsi / 100 - 0.7)) + (0.2 * abs(trend))
        else:
            signal = "HOLD"
            reasoning = f"RSI neutral ({rsi:.1f}), no clear trend"
            confidence = 0.5

        confidence = max(0.0, min(1.0, confidence))

        return TradingSignal(
            pool_address=pool.address,
            signal=signal,
            confidence=confidence,
            rsi=rsi,
            volatility=volatility,
            trend=trend,
            reasoning=reasoning,
        )
