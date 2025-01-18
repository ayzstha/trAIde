from pathlib import Path
from data.market_data import MarketDataFetcher
from utils.config import config
from utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    # Initialize data fetcher
    fetcher = MarketDataFetcher()
    
    # Test fetch for default symbols
    for symbol in config.DEFAULT_SYMBOLS:
        try:
            data = fetcher.fetch_data(symbol)
            logger.info(f"Fetched {len(data)} records for {symbol}")
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")

if __name__ == "__main__":
    main()

import pytest
from src.data.market_data import MarketDataFetcher
from src.utils.config import config

def test_market_data_fetch():
    fetcher = MarketDataFetcher()
    symbol = "AAPL"
    data = fetcher.fetch_data(symbol, period="5d")
    assert not data.empty
    assert all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])