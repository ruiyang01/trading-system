import asyncio
import logging
import json

import redis.asyncio as redis

from config import config
from strategies import MomentumStrategy, RSIStrategy, MACDStrategy, BollingerStrategy, SignalType

logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StrategyEngine:
    def __init__(self):
        self.redis_client = None
        self.strategies = [
            MomentumStrategy(),
            RSIStrategy(),
            MACDStrategy(),
            BollingerStrategy()
        ]
        self.price_history: dict[str, list[float]] = {}
    
    async def connect_redis(self):
        self.redis_client = await redis.from_url(config.redis_url)
        logger.info("Connected to Redis")
    
    async def process_price(self, price_data: dict):
        symbol = price_data['symbol']
        price = price_data['price']
        
        # 更新价格历史
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append(price)
        self.price_history[symbol] = self.price_history[symbol][-config.price_history_length:]
        
        # 用所有策略生成信号
        for strategy in self.strategies:
            signal = strategy.generate_signal(
                prices=self.price_history[symbol],
                current_price=price,
                symbol=symbol
            )
            
            if signal.signal_type != SignalType.HOLD:
                await self.redis_client.publish("signals", signal.to_json())
                logger.info(f"🚨 [{strategy.name.upper()}] {signal.signal_type.value.upper()} {symbol} @ ${price:.2f} (conf: {signal.confidence:.2f})")
    
    async def run(self):
        await self.connect_redis()
        
        logger.info("=" * 50)
        logger.info("Strategy Engine Started")
        logger.info(f"Strategies: {[s.name for s in self.strategies]}")
        logger.info("=" * 50)
        
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe("prices")
        
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    price_data = json.loads(message["data"])
                    await self.process_price(price_data)
                except Exception as e:
                    logger.error(f"Error: {e}")


async def main():
    engine = StrategyEngine()
    await engine.run()


if __name__ == "__main__":
    asyncio.run(main())