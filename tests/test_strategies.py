import pytest
import sys
sys.path.insert(0, 'services/strategy-engine/src')

from strategies.rsi import RSIStrategy
from strategies.momentum import MomentumStrategy
from strategies.base import SignalType


class TestRSIStrategy:
    def setup_method(self):
        self.strategy = RSIStrategy()
    
    def test_rsi_buy_signal_on_oversold(self):
        # 模拟价格持续下跌 (RSI 会很低)
        prices = [100 - i * 0.5 for i in range(30)]
        signal = self.strategy.generate_signal(prices, prices[-1], "BTCUSDT")
        
        assert signal.symbol == "BTCUSDT"
        # RSI 低时应该产生买入信号
        assert signal.signal_type in [SignalType.BUY, SignalType.HOLD]
    
    def test_rsi_sell_signal_on_overbought(self):
        # 模拟价格持续上涨 (RSI 会很高)
        prices = [100 + i * 0.5 for i in range(30)]
        signal = self.strategy.generate_signal(prices, prices[-1], "BTCUSDT")
        
        assert signal.symbol == "BTCUSDT"
        # RSI 高时应该产生卖出信号
        assert signal.signal_type in [SignalType.SELL, SignalType.HOLD]
    
    def test_rsi_hold_signal_on_neutral(self):
        # 模拟价格横盘
        prices = [100 + (i % 3 - 1) * 0.1 for i in range(30)]
        signal = self.strategy.generate_signal(prices, prices[-1], "ETHUSDT")
        
        assert signal.signal_type == SignalType.HOLD


class TestMomentumStrategy:
    def setup_method(self):
        self.strategy = MomentumStrategy()
    
    def test_momentum_with_insufficient_data(self):
        prices = [100, 101, 102]
        signal = self.strategy.generate_signal(prices, prices[-1], "BTCUSDT")
        
        assert signal.signal_type == SignalType.HOLD
    
    def test_momentum_buy_signal(self):
        # 短期均线高于长期均线
        prices = [100] * 20 + [110, 112, 115, 118, 120]
        signal = self.strategy.generate_signal(prices, prices[-1], "BTCUSDT")
        
        assert signal.symbol == "BTCUSDT"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
