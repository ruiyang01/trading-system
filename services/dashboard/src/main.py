import asyncio
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import redis.asyncio as redis
import asyncpg

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

REDIS_URL = "redis://redis:6379"
DATABASE_URL = "postgresql://trader:trader123@postgres:5432/trading"


async def connect_db_with_retry(max_retries=10):
    for i in range(max_retries):
        try:
            pool = await asyncpg.create_pool(DATABASE_URL)
            logger.info("Connected to PostgreSQL")
            return pool
        except Exception as e:
            logger.warning(f"DB connection failed ({i+1}/{max_retries}): {e}")
            await asyncio.sleep(2)
    raise Exception("Could not connect to PostgreSQL")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = await redis.from_url(REDIS_URL, decode_responses=True)
    logger.info("Connected to Redis")
    app.state.db = await connect_db_with_retry()
    yield
    await app.state.redis.close()
    await app.state.db.close()


app = FastAPI(title="Trading Dashboard", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r") as f:
        return f.read()


@app.get("/api/prices")
async def get_prices():
    keys = await app.state.redis.keys("price:*")
    prices = {}
    for key in keys:
        data = await app.state.redis.get(key)
        if data:
            prices[key.replace("price:", "")] = json.loads(data)
    return prices


@app.get("/api/account")
async def get_account():
    data = await app.state.redis.get("account:status")
    if data:
        return json.loads(data)
    return {"balance": {"USD": 10000}, "positions": {}, "total_orders": 0}


@app.get("/api/trades")
async def get_trades(limit: int = 50):
    try:
        async with app.state.db.acquire() as conn:
            rows = await conn.fetch('''
                SELECT id, symbol, side, quantity, price, total_value, strategy, confidence, status, created_at
                FROM trades 
                ORDER BY created_at DESC 
                LIMIT $1
            ''', limit)
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching trades: {e}")
        return []


@app.get("/api/signals")
async def get_signals(limit: int = 50):
    try:
        async with app.state.db.acquire() as conn:
            rows = await conn.fetch('''
                SELECT id, symbol, signal_type, price, confidence, strategy, executed, created_at
                FROM signals 
                ORDER BY created_at DESC 
                LIMIT $1
            ''', limit)
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching signals: {e}")
        return []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    pubsub = app.state.redis.pubsub()
    await pubsub.subscribe("prices", "signals")
    
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                channel = message["channel"]
                data = json.loads(message["data"])
                await websocket.send_json({
                    "type": channel,
                    "data": data
                })
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    finally:
        await pubsub.unsubscribe()
