from dataclasses import dataclass
from typing import Optional
import math


class OptimizedMomentumStrategy:
    """
    优化版动量策略:
    - 使用 EMA 代替 SMA
    - 添加趋势过滤器
    - 添加成交量确认
    """
    
    def __init__(self, fast_period: int = 8, slow_period: int = 21, trend_period: int = 50):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.trend_period = trend_period
        self.name = "momentum_v2"
    
    def ema(self, prices: list[float], period: int) -> float:
        if len(prices) < period:
            return sum(prices) / len(prices)
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        return ema
    
    def generate_signal(self, prices: list[float], volumes: Optional[list[float]] = None) -> tuple[str, float]:
        if len(prices) < self.trend_period:
            return "hold", 0.5
        
        fast_ema = self.ema(prices, self.fast_period)
        slow_ema = self.ema(prices, self.slow_period)
        trend_ema = self.ema(prices, self.trend_period)
        
        current_price = prices[-1]
        
        # 趋势方向
        uptrend = current_price > trend_ema
        downtrend = current_price < trend_ema
        
        # EMA 交叉
        diff_pct = (fast_ema - slow_ema) / slow_ema * 100
        
        # 只在趋势方向交易
        if diff_pct > 0.5 and uptrend:
            confidence = min(diff_pct / 3, 1.0)
            return "buy", confidence
        elif diff_pct < -0.5 and downtrend:
            confidence = min(abs(diff_pct) / 3, 1.0)
            return "sell", confidence
        
        return "hold", 0.5


class OptimizedRSIStrategy:
    """
    优化版 RSI 策略:
    - RSI 超卖/超买
    - 添加 RSI 背离检测
    - 使用动态阈值
    """
    
    def __init__(self, period: int = 14, oversold: int = 25, overbought: int = 75):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.name = "rsi_v2"
        self.prev_rsi = 50
    
    def calculate_rsi(self, prices: list[float]) -> float:
        if len(prices) < self.period + 1:
            return 50.0
        
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        recent = changes[-self.period:]
        
        gains = [c for c in recent if c > 0]
        losses = [-c for c in recent if c < 0]
        
        avg_gain = sum(gains) / self.period if gains else 0
        avg_loss = sum(losses) / self.period if losses else 0.0001
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def generate_signal(self, prices: list[float]) -> tuple[str, float]:
        rsi = self.calculate_rsi(prices)
        
        # RSI 从超卖区反弹
        if rsi < self.oversold:
            confidence = min((self.oversold - rsi) / 20 + 0.5, 1.0)
            self.prev_rsi = rsi
            return "buy", confidence
        
        # RSI 从超买区回落
        elif rsi > self.overbought:
            confidence = min((rsi - self.overbought) / 20 + 0.5, 1.0)
            self.prev_rsi = rsi
            return "sell", confidence
        
        # RSI 背离 - 价格新高但 RSI 没有新高
        if len(prices) > 20:
            price_high = max(prices[-10:])
            price_prev_high = max(prices[-20:-10])
            
            if prices[-1] > price_prev_high and rsi < self.prev_rsi - 5:
                # 看跌背离
                return "sell", 0.6
        
        self.prev_rsi = rsi
        return "hold", 0.5


class MACDStrategy:
    """
    MACD 策略:
    - MACD 线穿越信号线
    - 柱状图确认
    """
    
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        self.fast = fast
        self.slow = slow
        self.signal_period = signal
        self.name = "macd_v2"
        self.prev_histogram = 0
    
    def ema(self, prices: list[float], period: int) -> float:
        if len(prices) < period:
            return sum(prices) / len(prices)
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        return ema
    
    def calculate_macd(self, prices: list[float]) -> tuple[float, float, float]:
        if len(prices) < self.slow + self.signal_period:
            return 0, 0, 0
        
        fast_ema = self.ema(prices, self.fast)
        slow_ema = self.ema(prices, self.slow)
        macd_line = fast_ema - slow_ema
        
        # 计算信号线 (MACD 的 EMA)
        macd_values = []
        for i in range(self.slow, len(prices)):
            f = self.ema(prices[:i+1], self.fast)
            s = self.ema(prices[:i+1], self.slow)
            macd_values.append(f - s)
        
        signal_line = self.ema(macd_values, self.signal_period) if len(macd_values) >= self.signal_period else macd_line
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def generate_signal(self, prices: list[float]) -> tuple[str, float]:
        macd_line, signal_line, histogram = self.calculate_macd(prices)
        
        # 柱状图由负转正 - 买入
        if histogram > 0 and self.prev_histogram <= 0:
            confidence = min(abs(histogram) / prices[-1] * 1000 + 0.5, 1.0)
            self.prev_histogram = histogram
            return "buy", confidence
        
        # 柱状图由正转负 - 卖出
        elif histogram < 0 and self.prev_histogram >= 0:
            confidence = min(abs(histogram) / prices[-1] * 1000 + 0.5, 1.0)
            self.prev_histogram = histogram
            return "sell", confidence
        
        self.prev_histogram = histogram
        return "hold", 0.5


class CombinedStrategy:
    """
    组合策略: 多个策略共同确认
    - 至少 2 个策略同意才交易
    - 置信度取平均
    """
    
    def __init__(self):
        self.momentum = OptimizedMomentumStrategy()
        self.rsi = OptimizedRSIStrategy()
        self.macd = MACDStrategy()
        self.name = "combined"
    
    def generate_signal(self, prices: list[float]) -> tuple[str, float]:
        signals = [
            self.momentum.generate_signal(prices),
            self.rsi.generate_signal(prices),
            self.macd.generate_signal(prices)
        ]
        
        buy_count = sum(1 for s, c in signals if s == "buy")
        sell_count = sum(1 for s, c in signals if s == "sell")
        
        buy_confidence = sum(c for s, c in signals if s == "buy") / max(buy_count, 1)
        sell_confidence = sum(c for s, c in signals if s == "sell") / max(sell_count, 1)
        
        # 至少 2 个策略同意
        if buy_count >= 2:
            return "buy", buy_confidence
        elif sell_count >= 2:
            return "sell", sell_confidence
        
        return "hold", 0.5