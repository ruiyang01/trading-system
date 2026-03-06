from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    symbol: str
    side: str  # buy/sell
    price: float
    quantity: float
    timestamp: datetime
    strategy: str


@dataclass
class BacktestResult:
    initial_balance: float
    final_balance: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl: float
    total_return_pct: float
    max_drawdown_pct: float
    win_rate: float
    trades: list[Trade] = field(default_factory=list)


class BacktestEngine:
    def __init__(self, initial_balance: float = 10000.0, position_size_pct: float = 0.1):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position_size_pct = position_size_pct
        self.positions: dict[str, float] = {}  # symbol -> quantity
        self.entry_prices: dict[str, float] = {}  # symbol -> avg price
        self.trades: list[Trade] = []
        self.equity_curve: list[float] = [initial_balance]
        self.peak_equity = initial_balance
        self.max_drawdown = 0.0
    
    def execute_signal(self, symbol: str, signal_type: str, price: float, 
                       confidence: float, timestamp: datetime, strategy: str):
        position_value = self.balance * self.position_size_pct * confidence
        
        if signal_type == "buy" and self.balance >= position_value:
            quantity = position_value / price
            self.balance -= position_value
            
            # 更新持仓
            if symbol in self.positions:
                total_qty = self.positions[symbol] + quantity
                total_cost = self.entry_prices[symbol] * self.positions[symbol] + price * quantity
                self.entry_prices[symbol] = total_cost / total_qty
                self.positions[symbol] = total_qty
            else:
                self.positions[symbol] = quantity
                self.entry_prices[symbol] = price
            
            self.trades.append(Trade(symbol, "buy", price, quantity, timestamp, strategy))
            logger.debug(f"BUY {quantity:.6f} {symbol} @ ${price:.2f}")
        
        elif signal_type == "sell" and symbol in self.positions and self.positions[symbol] > 0:
            quantity = min(self.positions[symbol], position_value / price)
            sell_value = quantity * price
            self.balance += sell_value
            self.positions[symbol] -= quantity
            
            if self.positions[symbol] <= 0:
                del self.positions[symbol]
                del self.entry_prices[symbol]
            
            self.trades.append(Trade(symbol, "sell", price, quantity, timestamp, strategy))
            logger.debug(f"SELL {quantity:.6f} {symbol} @ ${price:.2f}")
        
        # 更新权益曲线
        self._update_equity(price if symbol in self.positions else 0)
    
    def _update_equity(self, current_price: float):
        # 计算总权益
        positions_value = sum(
            qty * current_price for sym, qty in self.positions.items()
        )
        total_equity = self.balance + positions_value
        self.equity_curve.append(total_equity)
        
        # 更新最大回撤
        if total_equity > self.peak_equity:
            self.peak_equity = total_equity
        
        drawdown = (self.peak_equity - total_equity) / self.peak_equity * 100
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
    
    def get_results(self, final_prices: dict[str, float]) -> BacktestResult:
        # 计算最终持仓价值
        positions_value = sum(
            qty * final_prices.get(sym, 0) for sym, qty in self.positions.items()
        )
        final_balance = self.balance + positions_value
        
        # 计算胜率
        winning = 0
        losing = 0
        
        buy_prices = {}
        for trade in self.trades:
            if trade.side == "buy":
                buy_prices[trade.symbol] = trade.price
            elif trade.side == "sell" and trade.symbol in buy_prices:
                if trade.price > buy_prices[trade.symbol]:
                    winning += 1
                else:
                    losing += 1
        
        total_closed = winning + losing
        win_rate = (winning / total_closed * 100) if total_closed > 0 else 0
        
        return BacktestResult(
            initial_balance=self.initial_balance,
            final_balance=final_balance,
            total_trades=len(self.trades),
            winning_trades=winning,
            losing_trades=losing,
            total_pnl=final_balance - self.initial_balance,
            total_return_pct=(final_balance - self.initial_balance) / self.initial_balance * 100,
            max_drawdown_pct=self.max_drawdown,
            win_rate=win_rate,
            trades=self.trades
        )
