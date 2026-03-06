from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json


class SignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class Signal:
    symbol: str
    signal_type: SignalType
    confidence: float
    price: float
    target_price: float
    stop_loss: float
    strategy: str
    timestamp: datetime
    
    def to_json(self) -> str:
        data = asdict(self)
        data['signal_type'] = self.signal_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return json.dumps(data)


class BaseStrategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def generate_signal(self, prices: list[float], current_price: float, symbol: str) -> Signal:
        pass
