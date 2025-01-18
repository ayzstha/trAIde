import yfinance as yf
import pandas as pd
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))


class MarketDataFetcher:
    def __init__(self):
        self.cache_dir = Path(__file__).parent.parent.parent / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_data(self, symbol: str, period: str = '1y', interval: str = '1d'):
        print(f"Fetching data for {symbol}")
        ticker = yf.Ticker(symbol)
        return ticker.history(period=period, interval=interval)

def test_fetch_data():
    fetcher = MarketDataFetcher()
    data = fetcher.fetch_data('AAPL', period='5d')
    print(f"Fetched {len(data)} records for AAPL")
    return data

if __name__ == "__main__":
    test_fetch_data()