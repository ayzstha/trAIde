import yfinance as yf
import pandas as pd
import numpy as np
from ta.trend import MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from .config import TradingConfig as cfg

def fetch_data(ticker, period, interval):    # Added interval parameter
    """Fetch stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)    # Passed interval
        if df.empty:
            raise ValueError(f"No data found for ticker '{ticker}' with period '{period}' and interval '{interval}'.")
        return df
    except Exception as e:
        print(f"Error fetching data for ticker '{ticker}' with period '{period}' and interval '{interval}': {str(e)}")
        raise

def calculate_indicators(df):
    """Calculate technical indicators"""
    try:
        df = df.copy()
        
        # RSI
        rsi = RSIIndicator(df['Close'])
        df['RSI'] = rsi.rsi()
        
        # MACD
        macd = MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        
        # Bollinger Bands
        bb = BollingerBands(df['Close'])
        df['BB_high'] = bb.bollinger_hband()
        df['BB_low'] = bb.bollinger_lband()
        
        return df
    except Exception as e:
        print(f"Error calculating indicators: {str(e)}")
        raise