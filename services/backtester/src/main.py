import asyncio
import logging
from datetime import datetime
from data_fetcher import fetch_binance_history, fetch_yahoo_history
from backtest_engine import BacktestEngine, BacktestResult
from optimized_strategies import (
    OptimizedMomentumStrategy, 
    OptimizedRSIStrategy, 
    MACDStrategy,
    CombinedStrategy
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 原始策略用于对比
class MomentumStrategy:
    def __init__(self):
        self.name = "momentum_v1"
    
    def generate_signal(self, prices: list[float]) -> tuple[str, float]:
        if len(prices) < 20:
            return "hold", 0.5
        short_ma = sum(prices[-5:]) / 5
        long_ma = sum(prices[-20:]) / 20
        diff_pct = (short_ma - long_ma) / long_ma * 100
        if diff_pct > 1:
            return "buy", min(diff_pct / 5, 1.0)
        elif diff_pct < -1:
            return "sell", min(abs(diff_pct) / 5, 1.0)
        return "hold", 0.5


class RSIStrategy:
    def __init__(self):
        self.name = "rsi_v1"
        self.period = 14
    
    def generate_signal(self, prices: list[float]) -> tuple[str, float]:
        if len(prices) < 15:
            return "hold", 0.5
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        recent = changes[-14:]
        gains = [c for c in recent if c > 0]
        losses = [-c for c in recent if c < 0]
        avg_gain = sum(gains) / 14 if gains else 0
        avg_loss = sum(losses) / 14 if losses else 0.0001
        rsi = 100 - (100 / (1 + avg_gain / avg_loss))
        if rsi < 30:
            return "buy", min((30 - rsi) / 30, 1.0)
        elif rsi > 70:
            return "sell", min((rsi - 70) / 30, 1.0)
        return "hold", 0.5


async def run_backtest(symbol: str, strategy, days: int = 30, is_crypto: bool = True):
    logger.info(f"Backtesting {strategy.name} on {symbol}...")
    
    if is_crypto:
        candles = await fetch_binance_history(symbol, days)
    else:
        candles = await fetch_yahoo_history(symbol, days)
    
    if len(candles) < 50:
        return None
    
    engine = BacktestEngine(initial_balance=10000.0, position_size_pct=0.1)
    price_history = []
    
    for candle in candles:
        price_history.append(candle.close)
        signal_type, confidence = strategy.generate_signal(price_history)
        
        if signal_type != "hold":
            engine.execute_signal(
                symbol=symbol,
                signal_type=signal_type,
                price=candle.close,
                confidence=confidence,
                timestamp=candle.timestamp,
                strategy=strategy.name
            )
    
    final_prices = {symbol: candles[-1].close}
    return engine.get_results(final_prices)


async def main():
    symbols = ["BTCUSDT", "ETHUSDT"]
    
    # 原始策略 vs 优化策略
    strategies = [
        MomentumStrategy(),
        OptimizedMomentumStrategy(),
        RSIStrategy(),
        OptimizedRSIStrategy(),
        MACDStrategy(),
        CombinedStrategy(),
    ]
    
    all_results = []
    
    for symbol in symbols:
        for strategy in strategies:
            result = await run_backtest(symbol, strategy, days=30, is_crypto=True)
            if result:
                all_results.append((symbol, strategy.name, result))
    
    # 打印结果
    print("\n" + "="*80)
    print("📊 BACKTEST COMPARISON: Original vs Optimized Strategies")
    print("="*80)
    print(f"{'Symbol':<10} {'Strategy':<18} {'Return':>10} {'Win Rate':>10} {'MaxDD':>10} {'Trades':>8}")
    print("-"*80)
    
    for symbol, name, result in all_results:
        print(f"{symbol:<10} {name:<18} {result.total_return_pct:>+9.2f}% {result.win_rate:>9.1f}% {result.max_drawdown_pct:>9.2f}% {result.total_trades:>8}")
    
    print("="*80)
    
    # 找出最佳策略
    best = max(all_results, key=lambda x: x[2].total_return_pct)
    print(f"\n🏆 Best Strategy: {best[1]} on {best[0]}")
    print(f"   Return: {best[2].total_return_pct:+.2f}%")
    print(f"   Win Rate: {best[2].win_rate:.1f}%")
    print(f"   Max Drawdown: {best[2].max_drawdown_pct:.2f}%")


if __name__ == "__main__":
    asyncio.run(main())