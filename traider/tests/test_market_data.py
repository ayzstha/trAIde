import pytest
from pathlib import Path
from ..src.data.market_data import MarketDataFetcher

def test_market_data_fetcher_initialization():
    fetcher = MarketDataFetcher()
    assert fetcher.cache_dir.exists()

def test_data_fetching(sample_market_data):
    fetcher = MarketDataFetcher()
    data = fetcher.fetch_data("AAPL", period="5d")
    assert not data.empty
    assert all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])

def test_cache_mechanism():
    fetcher = MarketDataFetcher()
    symbol = "AAPL"
    fetcher.fetch_data(symbol, period="1d")
    cache_files = list(fetcher.cache_dir.glob(f"{symbol}*.parquet"))
    assert len(cache_files) > 0