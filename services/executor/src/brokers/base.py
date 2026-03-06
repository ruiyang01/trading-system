from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class Order:
    id: str
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    status: OrderStatus
    timestamp: datetime


class BaseBroker(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    async def execute_order(self, symbol: str, side: OrderSide, amount: float) -> Order:
        pass
    
    @abstractmethod
    async def get_balance(self) -> dict:
        pass
    
    @abstractmethod
    async def get_positions(self) -> dict:
        pass
