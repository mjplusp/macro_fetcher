market_index_table = """ CREATE TABLE IF NOT EXISTS market_index (
    date VARCHAR(8),
    time VARCHAR(6),
    symbol VARCHAR(10),
    last FLOAT(4),
    open FLOAT(4),
    high FLOAT(4),
    low FLOAT(4),
    daily_change FLOAT(4),
    daily_pct_change FLOAT(4),
    volume VARCHAR(10),
    created_at VARCHAR(6)
    );"""

fx_rate_table = """ CREATE TABLE IF NOT EXISTS fx_rate (
    date VARCHAR(8),
    time VARCHAR(6),
    symbol VARCHAR(10),
    last FLOAT(4),
    open FLOAT(4),
    high FLOAT(4),
    low FLOAT(4),
    daily_change FLOAT(4),
    daily_pct_change FLOAT(4),
    volume VARCHAR(10),
    created_at VARCHAR(6)
    );"""

bond_yield_table = """ CREATE TABLE IF NOT EXISTS bond_yield (
    date VARCHAR(8),
    time VARCHAR(6),
    symbol VARCHAR(10),
    last FLOAT(4),
    open FLOAT(4),
    high FLOAT(4),
    low FLOAT(4),
    daily_change FLOAT(4),
    daily_pct_change FLOAT(4),
    volume VARCHAR(10),
    created_at VARCHAR(6)
    );"""
