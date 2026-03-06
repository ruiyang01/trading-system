import asyncio
from datetime import datetime
import httpx
from .base import BaseFetcher, PriceData, AssetType


class YahooFetcher(BaseFetcher):
    BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=10.0,
            headers={"User-Agent": "Mozilla/5.0"}
        )
    
    @property
    def name(self) -> str:
        return "yahoo"
    
    @property
    def asset_type(self) -> AssetType:
        return AssetType.STOCK
    
    async def get_price(self, symbol: str) -> PriceData:
        url = f"{self.BASE_URL}/{symbol}"
        params = {"interval": "1d", "range": "1d"}
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        meta = data['chart']['result'][0]['meta']
        prev_close = meta.get('previousClose', meta['regularMarketPrice'])
        current_price = meta['regularMarketPrice']
        change_24h = ((current_price - prev_close) / prev_close) * 100
        
        return PriceData(
            symbol=symbol,
            asset_type=AssetType.STOCK,
            price=current_price,
            volume=float(meta.get('regularMarketVolume', 0)),
            change_24h=round(change_24h, 2),
            timestamp=datetime.now(),
            source=self.name
        )
    
    async def get_prices(self, symbols: list[str]) -> list[PriceData]:
        tasks = [self.get_price(symbol) for symbol in symbols]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def close(self):
        await self.client.aclose()