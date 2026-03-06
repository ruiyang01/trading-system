CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    quantity DECIMAL(18, 8) NOT NULL,
    price DECIMAL(18, 8) NOT NULL,
    total_value DECIMAL(18, 8) NOT NULL,
    strategy VARCHAR(50),
    confidence DECIMAL(5, 4),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(10) NOT NULL,
    price DECIMAL(18, 8) NOT NULL,
    confidence DECIMAL(5, 4),
    strategy VARCHAR(50),
    executed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    quantity DECIMAL(18, 8) NOT NULL,
    avg_price DECIMAL(18, 8) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);
