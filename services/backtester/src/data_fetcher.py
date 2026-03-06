import httpx
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class OHLCV:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


async def fetch_binance_history(symbol: str, days: int = 30) -> list[OHLCV]:
    """获取 Binance 历史 K 线数据"""
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol.replace("/", ""),
        "interval": "1h",  # 1小时K线
        "limit": min(days * 24, 1000)
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    
    result = []
    for candle in data:
        result.append(OHLCV(
            timestamp=datetime.fromtimestamp(candle[0] / 1000),
            open=float(candle[1]),
            high=float(candle[2]),
            low=float(candle[3]),
            close=float(candle[4]),
            volume=float(candle[5])
        ))
    
    logger.info(f"Fetched {len(result)} candles for {symbol}")
    return result


async def fetch_yahoo_history(symbol: str, days: int = 30) -> list[OHLCV]:
    """获取 Yahoo Finance 历史数据"""
    end = datetime.now()
    start = end - timedelta(days=days)
    
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {
        "period1": int(start.timestamp()),
        "period2": int(end.timestamp()),
        "interval": "1h"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        data = response.json()
    
    result = []
    chart = data["chart"]["result"][0]
    timestamps = chart["timestamp"]
    quotes = chart["indicators"]["quote"][0]
    
    for i, ts in enumerate(timestamps):
        if quotes["close"][i] is not None:
            result.append(OHLCV(
                timestamp=datetime.fromtimestamp(ts),
                open=float(quotes["open"][i] or 0),
                high=float(quotes["high"][i] or 0),
                low=float(quotes["low"][i] or 0),
                close=float(quotes["close"][i]),
                volume=float(quotes["volume"][i] or 0)
            ))
    
    logger.info(f"Fetched {len(result)} candles for {symbol}")
    return result
