import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Optional, Dict
import time

class MarketDataFetcher:
    VALID_INTERVALS = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
    VALID_PERIODS = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    
    def __init__(self, max_retries: int = 3):
        self.logger = logging.getLogger(__name__)
        self.cache_dir = Path(__file__).parent.parent.parent / "data" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.data_cache: Dict[str, pd.DataFrame] = {}
        self.max_retries = max_retries

    def fetch_data(self, symbol: str, period: str = '1y', interval: str = '1d') -> pd.DataFrame:
        """
        Fetch market data for a given symbol
        
        Args:
            symbol: Stock ticker symbol
            period: Time period to fetch
            interval: Data interval
            
        Returns:
            DataFrame with OHLCV data
        """
        # Validate inputs
        if not symbol:
            raise ValueError("Symbol cannot be empty")
        if period not in self.VALID_PERIODS:
            raise ValueError(f"Invalid period. Must be one of {self.VALID_PERIODS}")
        if interval not in self.VALID_INTERVALS:
            raise ValueError(f"Invalid interval. Must be one of {self.VALID_INTERVALS}")
            
        cache_file = self.cache_dir / f"{symbol}_{interval}_{period}.parquet"
        
        if cache_file.exists() and self._is_cache_fresh(cache_file):
            self.logger.info(f"Loading cached data for {symbol}")
            return pd.read_parquet(cache_file)
        
        for attempt in range(self.max_retries):
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period, interval=interval)
                
                if data.empty:
                    raise ValueError(f"No data returned for {symbol}")
                
                # Preprocess data
                data = self._preprocess_data(data)
                
                # Cache the data
                data.to_parquet(cache_file)
                self.data_cache[symbol] = data
                self.logger.info(f"Successfully fetched data for {symbol}")
                return data
                
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)  # Wait before retry
                else:
                    raise RuntimeError(f"Failed to fetch data for {symbol} after {self.max_retries} attempts")

    def _preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the data"""
        # Remove any duplicates
        data = data.drop_duplicates()
        
        # Forward fill missing values
        data = data.ffill()
        
        # Ensure all required columns exist
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
            
        return data

    def _is_cache_fresh(self, cache_file: Path, max_age_hours: int = 24) -> bool:
        """Check if cached data is still valid"""
        if not cache_file.exists():
            return False
        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        return file_age.total_seconds() < max_age_hours * 3600

    def get_latest_price(self, symbol: str) -> float:
        """Get the most recent price for a symbol"""
        if symbol not in self.data_cache:
            self.fetch_data(symbol, period='1d', interval='1m')
        return self.data_cache[symbol]['Close'].iloc[-1]