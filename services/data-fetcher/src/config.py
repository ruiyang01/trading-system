import os
from dataclasses import dataclass, field


@dataclass
class Config:
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))
    
    crypto_symbols: list[str] = field(default_factory=lambda: [
        "BTCUSDT", "ETHUSDT", "SOLUSDT"
    ])
    
    stock_symbols: list[str] = field(default_factory=lambda: [
        "NVDA", "AAPL", "TSLA"
    ])
    
    crypto_interval: int = 5
    stock_interval: int = 60
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))


config = Config()
