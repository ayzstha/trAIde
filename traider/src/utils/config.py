import pytest
from pathlib import Path
import os
from dotenv import load_dotenv
from src.data.market_data import MarketDataFetcher

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "models"

# API Configuration
API_KEY = os.getenv("YAHOO_API_KEY", "")

# Trading Parameters
DEFAULT_TIMEFRAME = "1d"
DEFAULT_PERIOD = "1y"
SYMBOLS = ["SPY", "QQQ", "AAPL"]  # Default symbols to track

# Project configuration
class Config:
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    CACHE_DIR = DATA_DIR / "cache"
    MODEL_DIR = PROJECT_ROOT / "models"
    
    # Market Data
    DEFAULT_INTERVAL = "1d"
    DEFAULT_PERIOD = "1y"
    CACHE_EXPIRY_HOURS = 24
    
    # Trading Parameters
    DEFAULT_SYMBOLS = ["SPY", "QQQ", "AAPL"]
    
    # API Keys
    YAHOO_API_KEY = os.getenv("YAHOO_API_KEY", "")

config = Config()

def test_market_data_fetcher():
    fetcher = MarketDataFetcher()
    data = fetcher.fetch_data("AAPL", period="5d")
    assert not data.empty
    assert "Close" in data.columns
    assert "Volume" in data.columns