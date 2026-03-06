# Trading System

A complete quantitative trading system MVP with real-time data, multiple strategies, paper trading, and dashboard.

## Architecture
```
Data Fetcher → Strategy Engine → Executor → Dashboard
(Binance/Yahoo)  (4 Strategies)   (Paper)    (Real-time UI)
      │               │              │
      └───────────────┼──────────────┘
                      ▼
                    Redis
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      Dashboard   PostgreSQL   WebSocket
```

## Features

- **Data Fetcher**: Real-time prices from Binance (Crypto) and Yahoo Finance (Stocks)
- **Strategies**: Momentum, RSI, MACD, Bollinger Bands
- **Executor**: Paper trading with risk management
- **Dashboard**: Real-time prices, positions, P&L, order history
- **Backtester**: Historical strategy testing

## Quick Start
```bash
docker-compose up --build
```

Open http://localhost:3001

## Services

| Service | Port | Description |
|---------|------|-------------|
| Dashboard | 3001 | Web UI |
| Redis | 6379 | Real-time data |
| PostgreSQL | 5432 | Trade history |

## Tech Stack

- Python 3.11
- FastAPI
- Redis
- PostgreSQL
- Docker & Docker Compose

## License

MIT

MIT
