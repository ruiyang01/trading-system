import asyncio
import logging
from datetime import datetime

import redis.asyncio as redis

from config import config
from fetchers import BinanceFetcher, YahooFetcher, PriceData

logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class DataFetcherService:
    def __init__(self):
        self.redis_client = None
        self.binance = BinanceFetcher()
        self.yahoo = YahooFetcher()
        self.running = True
    
    async def connect_redis(self):
        self.redis_client = await redis.from_url(config.redis_url)
        logger.info(f"Connected to Redis")
    
    async def publish_price(self, price: PriceData):
        key = f"price:{price.symbol}"
        await self.redis_client.set(key, price.to_json())
        await self.redis_client.publish("prices", price.to_json())
        logger.info(f"{price.symbol}: ${price.price:.2f} ({price.change_24h:+.2f}%)")
    
    async def fetch_crypto_loop(self):
        while self.running:
            try:
                prices = await self.binance.get_prices(config.crypto_symbols)
                for price in prices:
                    await self.publish_price(price)
            except Exception as e:
                logger.error(f"Crypto error: {e}")
            await asyncio.sleep(config.crypto_interval)
    
    async def fetch_stock_loop(self):
        while self.running:
            try:
                prices = await self.yahoo.get_prices(config.stock_symbols)
                for price in prices:
                    if isinstance(price, PriceData):
                        await self.publish_price(price)
            except Exception as e:
                logger.error(f"Stock error: {e}")
            await asyncio.sleep(config.stock_interval)
    
    async def run(self):
        await self.connect_redis()
        logger.info("=" * 50)
        logger.info("Trading Data Fetcher Started")
        logger.info("=" * 50)
        await asyncio.gather(
            self.fetch_crypto_loop(),
            self.fetch_stock_loop()
        )


async def main():
    service = DataFetcherService()
    await service.run()


if __name__ == "__main__":
    asyncio.run(main())
  