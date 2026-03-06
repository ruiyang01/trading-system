import asyncio
from datetime import datetime
import httpx
from .base import BaseFetcher, PriceData, AssetType


class BinanceFetcher(BaseFetcher):
    BASE_URL = "https://api.binance.com/api/v3"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
    
    @property
    def name(self) -> str:
        return "binance"
    
    @property
    def asset_type(self) -> AssetType:
        return AssetType.CRYPTO
    
    async def get_price(self, symbol: str) -> PriceData:
        url = f"{self.BASE_URL}/ticker/24hr"
        params = {"symbol": symbol.replace("/", "")}
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return PriceData(
            symbol=symbol,
            asset_type=AssetType.CRYPTO,
            price=float(data['lastPrice']),
            volume=float(data['quoteVolume']),
            change_24h=float(data['priceChangePercent']),
            timestamp=datetime.now(),
            source=self.name
        )
    
    async def get_prices(self, symbols: list[str]) -> list[PriceData]:
        tasks = [self.get_price(symbol) for symbol in symbols]
        return await asyncio.gather(*tasks)
    
    async def close(self):
        await self.client.aclose()