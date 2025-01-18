import pandas as pd
from typing import Optional, List
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path

class HistoricalDataHandler:
    """Class to handle historical financial data operations"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(__file__).parent.parent.parent / "data"
        self.data: Optional[pd.DataFrame] = None
        self.valid_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
        
    def fetch_data(self, 
                   symbol: str,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   period: str = "1y") -> pd.DataFrame:
        """
        Fetch historical data for a given symbol
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date for historical data
            end_date: End date for historical data
            period: Time period for data if start/end dates not specified
            
        Returns:
            DataFrame with historical price data
        """
        try:
            ticker = yf.Ticker(symbol)
            if start_date and end_date:
                self.data = ticker.history(start=start_date, end=end_date)
            else:
                self.data = ticker.history(period=period)
            return self.data
        except Exception as e:
            raise Exception(f"Error fetching data for {symbol}: {str(e)}")

    def get_latest_price(self, symbol: str) -> float:
        """Get the most recent closing price for a symbol"""
        if self.data is None:
            self.fetch_data(symbol)
        return self.data['Close'].iloc[-1]

    def calculate_returns(self) -> pd.Series:
        """Calculate daily returns from closing prices"""
        if self.data is not None:
            return self.data['Close'].pct_change()
        return pd.Series()

    def load_data(self, symbol: str, start_date: Optional[str] = None) -> pd.DataFrame:
        """Load historical data for symbol"""
        file_path = self.data_dir / f"{symbol}_history.parquet"
        if file_path.exists():
            self.data = pd.read_parquet(file_path)
            if start_date:
                self.data = self.data[self.data.index >= start_date]
        return self.data

    def get_price_history(self, columns: List[str] = None) -> pd.DataFrame:
        """
        Get stored price history
        
        Args:
            columns: List of specific columns to return
            
        Returns:
            DataFrame with requested price history
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if columns:
            invalid_cols = [col for col in columns if col not in self.valid_columns]
            if invalid_cols:
                raise ValueError(f"Invalid columns: {invalid_cols}. Valid columns are {self.valid_columns}")
            return self.data[columns]
        
        return self.data

    def save_data(self, symbol: str) -> None:
        """Save current data to parquet file"""
        if self.data is not None:
            file_path = self.data_dir / f"{symbol}_history.parquet"
            self.data.to_parquet(file_path)