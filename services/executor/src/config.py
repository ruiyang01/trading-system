import os
from dataclasses import dataclass, field


@dataclass
class Config:
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "postgresql://trader:trader123@postgres:5432/trading"))
    initial_balance: float = 10000.0
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))


config = Config()
