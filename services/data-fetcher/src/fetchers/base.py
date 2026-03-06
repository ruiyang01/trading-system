from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Optional
import json


class AssetType(Enum):
    CRYPTO = "crypto"
    STOCK = "stock"


@dataclass
class PriceData:
    symbol: str
    asset_type: AssetType
    price: float
    volume: float
    change_24h: Optional[float]
    timestamp: datetime
    source: str

    def to_json(self) -> str:
        data = asdict(self)
        data['asset_type'] = self.asset_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> 'PriceData':
        data = json.loads(json_str)
        data['asset_type'] = AssetType(data['asset_type'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class BaseFetcher(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def asset_type(self) -> AssetType:
        pass

    @abstractmethod
    async def get_price(self, symbol: str) -> PriceData:
        pass

    @abstractmethod
    async def get_prices(self, symbols: list[str]) -> list[PriceData]:
        pass
