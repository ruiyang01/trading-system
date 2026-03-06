import asyncio
import logging
import json

import redis.asyncio as redis

from config import config
from database import Database
from risk_manager import RiskManager, RiskConfig
from brokers import PaperBroker, OrderSide

logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Executor:
    def __init__(self):
        self.redis_client = None
        self.db = Database(config.database_url)
        self.broker = PaperBroker(initial_balance=config.initial_balance)
        self.risk_manager = RiskManager(
            config=RiskConfig(),
            total_capital=config.initial_balance
        )
    
    async def connect(self):
        self.redis_client = await redis.from_url(config.redis_url)
        logger.info("Connected to Redis")
        try:
            await self.db.connect()
        except Exception as e:
            logger.warning(f"DB connection failed: {e}, continuing without DB")
    
    async def process_signal(self, signal_data: dict):
        symbol = signal_data['symbol']
        signal_type = signal_data['signal_type']
        confidence = signal_data['confidence']
        price = signal_data['price']
        strategy = signal_data.get('strategy', 'unknown')
        
        logger.info(f"📥 Received: {signal_type.upper()} {symbol} @ ${price:.2f} [{strategy}]")
        
        # 风控检查
        can_trade, reason = self.risk_manager.can_trade(symbol, confidence)
        
        if not can_trade:
            logger.warning(f"⚠️ Blocked: {reason}")
            return
        
        # 计算仓位
        position_size = self.risk_manager.calculate_position_size(confidence)
        
        # 执行交易
        if signal_type == "buy":
            order = await self.broker.execute_order(symbol, OrderSide.BUY, position_size, price)
        elif signal_type == "sell":
            order = await self.broker.execute_order(symbol, OrderSide.SELL, position_size, price)
        else:
            return
        
        # 保存到数据库
        try:
            if self.db.pool:
                await self.db.save_trade(
                    symbol=symbol,
                    side=signal_type,
                    quantity=order.quantity,
                    price=price,
                    total_value=position_size,
                    strategy=strategy,
                    confidence=confidence,
                    status=order.status.value
                )
        except Exception as e:
            logger.error(f"DB save error: {e}")
        
        # 更新风控
        if order.status.value == "filled":
            value = position_size if signal_type == "buy" else -position_size
            self.risk_manager.update_position(symbol, value)
        
        await self.publish_status()
    
    async def publish_status(self):
        balance = await self.broker.get_balance()
        positions = await self.broker.get_positions()
        
        # 获取所有订单
        orders_list = []
        for order in self.broker.orders[-50:]:  # 最近50个
            orders_list.append({
                "id": order.id,
                "symbol": order.symbol,
                "side": order.side.value,
                "quantity": order.quantity,
                "price": order.price,
                "status": order.status.value,
                "timestamp": order.timestamp.isoformat()
            })
        
        status = {
            "balance": balance,
            "positions": positions,
            "total_orders": len(self.broker.orders),
            "orders": orders_list
        }
        
        await self.redis_client.set("account:status", json.dumps(status))
        logger.info(f"💰 Balance: ${balance['USD']:.2f} | Positions: {len(positions)} | Orders: {len(self.broker.orders)}")
    
    async def run(self):
        await self.connect()
        
        logger.info("=" * 50)
        logger.info("Executor Started (Paper Trading)")
        logger.info(f"Initial Balance: ${config.initial_balance:.2f}")
        logger.info("=" * 50)
        
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe("signals")
        
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    signal_data = json.loads(message["data"])
                    await self.process_signal(signal_data)
                except Exception as e:
                    logger.error(f"Error: {e}")


async def main():
    executor = Executor()
    await executor.run()


if __name__ == "__main__":
    asyncio.run(main())