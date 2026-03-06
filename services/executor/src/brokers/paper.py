import uuid
from datetime import datetime
import logging

from .base import BaseBroker, Order, OrderSide, OrderStatus

logger = logging.getLogger(__name__)


class PaperBroker(BaseBroker):
    """模拟交易 - 不用真钱"""
    
    def __init__(self, initial_balance: float = 10000.0):
        self.balance = initial_balance
        self.positions: dict[str, float] = {}  # symbol -> quantity
        self.orders: list[Order] = []
    
    @property
    def name(self) -> str:
        return "paper"
    
    async def execute_order(self, symbol: str, side: OrderSide, amount: float, price: float) -> Order:
        quantity = amount / price
        
        order = Order(
            id=str(uuid.uuid4())[:8],
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            status=OrderStatus.PENDING,
            timestamp=datetime.now()
        )
        
        if side == OrderSide.BUY:
            if self.balance >= amount:
                self.balance -= amount
                self.positions[symbol] = self.positions.get(symbol, 0) + quantity
                order.status = OrderStatus.FILLED
                logger.info(f"✅ BUY {quantity:.6f} {symbol} @ ${price:.2f} = ${amount:.2f}")
            else:
                order.status = OrderStatus.FAILED
                logger.warning(f"❌ Insufficient balance for {symbol}")
        
        elif side == OrderSide.SELL:
            current_qty = self.positions.get(symbol, 0)
            if current_qty >= quantity:
                self.balance += amount
                self.positions[symbol] -= quantity
                order.status = OrderStatus.FILLED
                logger.info(f"✅ SELL {quantity:.6f} {symbol} @ ${price:.2f} = ${amount:.2f}")
            else:
                order.status = OrderStatus.FAILED
                logger.warning(f"❌ Insufficient position for {symbol}")
        
        self.orders.append(order)
        return order
    
    async def get_balance(self) -> dict:
        return {"USD": self.balance}
    
    async def get_positions(self) -> dict:
        return self.positions.copy()