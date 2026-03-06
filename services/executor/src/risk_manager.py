from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RiskConfig:
    max_position_pct: float = 0.1      # 单个持仓最大 10%
    max_daily_loss_pct: float = 0.05   # 单日最大亏损 5%
    stop_loss_pct: float = 0.03        # 止损 3%
    min_confidence: float = 0.6        # 最小信号置信度


class RiskManager:
    def __init__(self, config: RiskConfig, total_capital: float):
        self.config = config
        self.total_capital = total_capital
        self.daily_pnl = 0.0
        self.positions: dict[str, float] = {}  # symbol -> value
    
    def can_trade(self, symbol: str, signal_confidence: float) -> tuple[bool, str]:
        # 检查置信度
        if signal_confidence < self.config.min_confidence:
            return False, f"Confidence {signal_confidence:.2f} < {self.config.min_confidence}"
        
        # 检查每日亏损
        if self.daily_pnl < -self.total_capital * self.config.max_daily_loss_pct:
            return False, f"Daily loss limit reached: {self.daily_pnl:.2f}"
        
        # 检查持仓集中度
        position_value = self.positions.get(symbol, 0)
        if position_value > self.total_capital * self.config.max_position_pct:
            return False, f"Position limit reached for {symbol}"
        
        return True, "OK"
    
    def calculate_position_size(self, signal_confidence: float) -> float:
        max_position = self.total_capital * self.config.max_position_pct
        return max_position * signal_confidence
    
    def update_position(self, symbol: str, value: float):
        self.positions[symbol] = self.positions.get(symbol, 0) + value
        logger.info(f"Position updated: {symbol} = ${self.positions[symbol]:.2f}")
    
    def update_pnl(self, pnl: float):
        self.daily_pnl += pnl
        logger.info(f"Daily PnL: ${self.daily_pnl:.2f}")