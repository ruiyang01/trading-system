import asyncpg
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None
    
    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(self.database_url)
            logger.info("Connected to PostgreSQL")
        except Exception as e:
            logger.warning(f"DB connection failed: {e}")
            self.pool = None
    
    async def close(self):
        if self.pool:
            await self.pool.close()
    
    async def save_trade(self, symbol: str, side: str, quantity: float,
                        price: float, total_value: float, strategy: str,
                        confidence: float, status: str):
        if not self.pool:
            return
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO trades (symbol, side, quantity, price, total_value, strategy, confidence, status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ''', symbol, side, quantity, price, total_value, strategy, confidence, status)
        except Exception as e:
            logger.error(f"Failed to save trade: {e}")
