from datetime import datetime
import math
from .base import BaseStrategy, Signal, SignalType


class BollingerStrategy(BaseStrategy):
    """布林带策略: 价格触及下轨买入, 触及上轨卖出"""
    
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        self.period = period
        self.std_dev = std_dev
    
    @property
    def name(self) -> str:
        return "bollinger"
    
    def calculate_bands(self, prices: list[float]) -> tuple[float, float, float]:
        if len(prices) < self.period:
            return 0, 0, 0
        
        recent = prices[-self.period:]
        middle = sum(recent) / self.period
        
        variance = sum((p - middle) ** 2 for p in recent) / self.period
        std = math.sqrt(variance)
        
        upper = middle + (self.std_dev * std)
        lower = middle - (self.std_dev * std)
        
        return upper, middle, lower
    
    def generate_signal(self, prices: list[float], current_price: float, symbol: str) -> Signal:
        upper, middle, lower = self.calculate_bands(prices)
        
        if lower == 0:
            return Signal(
                symbol=symbol,
                signal_type=SignalType.HOLD,
                confidence=0.5,
                price=current_price,
                target_price=current_price,
                stop_loss=current_price * 0.95,
                strategy="bollinger",
                timestamp=datetime.now()
            )
        
        # 价格在下轨附近 - 买入
        if current_price <= lower * 1.01:
            confidence = min((lower - current_price) / lower + 0.5, 1.0)
            return Signal(
                symbol=symbol,
                signal_type=SignalType.BUY,
                confidence=confidence,
                price=current_price,
                target_price=middle,
                stop_loss=lower * 0.98,
                strategy=f"bollinger(lower:{lower:.2f})",
                timestamp=datetime.now()
            )
        
        # 价格在上轨附近 - 卖出
        elif current_price >= upper * 0.99:
            confidence = min((current_price - upper) / upper + 0.5, 1.0)
            return Signal(
                symbol=symbol,
                signal_type=SignalType.SELL,
                confidence=confidence,
                price=current_price,
                target_price=middle,
                stop_loss=upper * 1.02,
                strategy=f"bollinger(upper:{upper:.2f})",
                timestamp=datetime.now()
            )
        
        return Signal(
            symbol=symbol,
            signal_type=SignalType.HOLD,
            confidence=0.5,
            price=current_price,
            target_price=current_price,
            stop_loss=current_price * 0.95,
            strategy="bollinger",
            timestamp=datetime.now()
        )