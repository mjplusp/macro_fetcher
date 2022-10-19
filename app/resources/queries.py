macro_meta_table = """ CREATE TABLE IF NOT EXISTS macro_meta (
    name VARCHAR(255),
    name_kr VARCHAR(255),
    original_symbol VARCHAR(255),
    symbol VARCHAR(255),
    exchange VARCHAR(255),
    type VARCHAR(255)
    );"""

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

commodity_table = """ CREATE TABLE IF NOT EXISTS commodity (
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