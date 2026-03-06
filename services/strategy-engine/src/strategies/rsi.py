from datetime import datetime
from .base import BaseStrategy, Signal, SignalType


class RSIStrategy(BaseStrategy):
    """
    RSI 策略: RSI < 30 超卖买入, RSI > 70 超买卖出
    """
    
    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    @property
    def name(self) -> str:
        return "rsi"
    
    def calculate_rsi(self, prices: list[float]) -> float:
        if len(prices) < self.period + 1:
            return 50.0
        
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        recent_changes = changes[-self.period:]
        
        gains = [c for c in recent_changes if c > 0]
        losses = [-c for c in recent_changes if c < 0]
        
        avg_gain = sum(gains) / self.period if gains else 0
        avg_loss = sum(losses) / self.period if losses else 0
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signal(self, prices: list[float], current_price: float, symbol: str) -> Signal:
        rsi = self.calculate_rsi(prices)
        
        if rsi < self.oversold:  # 超卖，买入信号
            confidence = (self.oversold - rsi) / self.oversold
            return Signal(
                symbol=symbol,
                signal_type=SignalType.BUY,
                confidence=min(confidence, 1.0),
                price=current_price,
                target_price=current_price * 1.05,
                stop_loss=current_price * 0.97,
                strategy=f"{self.name}(rsi={rsi:.1f})",
                timestamp=datetime.now()
            )
        elif rsi > self.overbought:  # 超买，卖出信号
            confidence = (rsi - self.overbought) / (100 - self.overbought)
            return Signal(
                symbol=symbol,
                signal_type=SignalType.SELL,
                confidence=min(confidence, 1.0),
                price=current_price,
                target_price=current_price * 0.95,
                stop_loss=current_price * 1.03,
                strategy=f"{self.name}(rsi={rsi:.1f})",
                timestamp=datetime.now()
            )
        
        return Signal(
            symbol=symbol,
            signal_type=SignalType.HOLD,
            confidence=0.5,
            price=current_price,
            target_price=current_price,
            stop_loss=current_price * 0.95,
            strategy=f"{self.name}(rsi={rsi:.1f})",
            timestamp=datetime.now()
        )