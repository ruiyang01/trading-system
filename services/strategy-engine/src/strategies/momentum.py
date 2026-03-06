from datetime import datetime
from .base import BaseStrategy, Signal, SignalType


class MomentumStrategy(BaseStrategy):
    def __init__(self, short_window: int = 5, long_window: int = 20):
        self.short_window = short_window
        self.long_window = long_window
    
    @property
    def name(self) -> str:
        return "momentum"
    
    def generate_signal(self, prices: list[float], current_price: float, symbol: str) -> Signal:
        if len(prices) < self.long_window:
            return self._hold_signal(current_price, symbol)
        
        short_ma = sum(prices[-self.short_window:]) / self.short_window
        long_ma = sum(prices[-self.long_window:]) / self.long_window
        diff_pct = (short_ma - long_ma) / long_ma * 100
        
        if diff_pct > 2:
            return Signal(
                symbol=symbol,
                signal_type=SignalType.BUY,
                confidence=min(diff_pct / 10, 1.0),
                price=current_price,
                target_price=current_price * 1.05,
                stop_loss=current_price * 0.97,
                strategy=self.name,
                timestamp=datetime.now()
            )
        elif diff_pct < -2:
            return Signal(
                symbol=symbol,
                signal_type=SignalType.SELL,
                confidence=min(abs(diff_pct) / 10, 1.0),
                price=current_price,
                target_price=current_price * 0.95,
                stop_loss=current_price * 1.03,
                strategy=self.name,
                timestamp=datetime.now()
            )
        return self._hold_signal(current_price, symbol)
    
    def _hold_signal(self, price: float, symbol: str) -> Signal:
        return Signal(
            symbol=symbol,
            signal_type=SignalType.HOLD,
            confidence=0.5,
            price=price,
            target_price=price,
            stop_loss=price * 0.95,
            strategy=self.name,
            timestamp=datetime.now()
        )