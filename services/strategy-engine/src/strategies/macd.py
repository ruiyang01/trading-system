from datetime import datetime
from .base import BaseStrategy, Signal, SignalType


class MACDStrategy(BaseStrategy):
    """MACD 策略: MACD 上穿信号线买入, 下穿卖出"""
    
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        self.fast = fast
        self.slow = slow
        self.signal_period = signal
    
    @property
    def name(self) -> str:
        return "macd"
    
    def ema(self, prices: list[float], period: int) -> float:
        if len(prices) < period:
            return sum(prices) / len(prices)
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        return ema
    
    def calculate_macd(self, prices: list[float]) -> tuple[float, float, float]:
        if len(prices) < self.slow:
            return 0, 0, 0
        
        fast_ema = self.ema(prices, self.fast)
        slow_ema = self.ema(prices, self.slow)
        macd_line = fast_ema - slow_ema
        
        # 简化：用当前 MACD 作为信号线近似
        signal_line = macd_line * 0.9
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def generate_signal(self, prices: list[float], current_price: float, symbol: str) -> Signal:
        macd_line, signal_line, histogram = self.calculate_macd(prices)
        
        if histogram > 0 and macd_line > 0:
            return Signal(
                symbol=symbol,
                signal_type=SignalType.BUY,
                confidence=min(abs(histogram) / current_price * 100, 1.0),
                price=current_price,
                target_price=current_price * 1.05,
                stop_loss=current_price * 0.97,
                strategy=f"macd({histogram:.2f})",
                timestamp=datetime.now()
            )
        elif histogram < 0 and macd_line < 0:
            return Signal(
                symbol=symbol,
                signal_type=SignalType.SELL,
                confidence=min(abs(histogram) / current_price * 100, 1.0),
                price=current_price,
                target_price=current_price * 0.95,
                stop_loss=current_price * 1.03,
                strategy=f"macd({histogram:.2f})",
                timestamp=datetime.now()
            )
        
        return Signal(
            symbol=symbol,
            signal_type=SignalType.HOLD,
            confidence=0.5,
            price=current_price,
            target_price=current_price,
            stop_loss=current_price * 0.95,
            strategy="macd",
            timestamp=datetime.now()
        )