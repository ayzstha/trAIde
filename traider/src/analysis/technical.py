import pandas as pd
import numpy as np
from typing import Union, Tuple, Dict

class TechnicalAnalyzer:
    @staticmethod
    def calculate_ma(data: pd.DataFrame, window: int = 20, ma_type: str = 'sma') -> pd.Series:
        """
        Calculate Moving Average
        
        Args:
            data (pd.DataFrame): OHLCV price data
            window (int): Moving average period
            ma_type (str): 'sma' or 'ema'
            
        Returns:
            pd.Series: Moving average values
        """
        if len(data) < window:
            raise ValueError(f"Data length ({len(data)}) must be >= window ({window})")
        
        if ma_type.lower() == 'sma':
            return data['Close'].rolling(window=window).mean()
        elif ma_type.lower() == 'ema':
            return data['Close'].ewm(span=window, adjust=False).mean()
        else:
            raise ValueError("ma_type must be 'sma' or 'ema'")

    @staticmethod
    def calculate_rsi(data: pd.DataFrame, window: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index
        
        Args:
            data (pd.DataFrame): OHLCV price data
            window (int): RSI period
            
        Returns:
            pd.Series: RSI values
        """
        if len(data) < window:
            raise ValueError(f"Data length ({len(data)}) must be >= window ({window})")
            
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        # Handle division by zero
        rs = gain / np.where(loss == 0, 0.000001, loss)
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, window: int = 20, 
                                num_std: float = 2.0) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Args:
            data (pd.DataFrame): OHLCV price data
            window (int): Moving average period
            num_std (float): Number of standard deviations
            
        Returns:
            Dict[str, pd.Series]: middle, upper, and lower bands
        """
        if len(data) < window:
            raise ValueError(f"Data length ({len(data)}) must be >= window ({window})")
        
        middle_band = data['Close'].rolling(window=window).mean()
        std_dev = data['Close'].rolling(window=window).std()
        
        return {
            'middle': middle_band,
            'upper': middle_band + (std_dev * num_std),
            'lower': middle_band - (std_dev * num_std)
        }

    @staticmethod
    def calculate_atr(data: pd.DataFrame, window: int = 14) -> pd.Series:
        """
        Calculate Average True Range
        
        Args:
            data (pd.DataFrame): OHLCV price data
            window (int): ATR period
            
        Returns:
            pd.Series: ATR values
        """
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Close'].shift())
        low_close = abs(data['Low'] - data['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(window=window).mean()

    @staticmethod
    def calculate_macd(data: pd.DataFrame, 
                      fast_period: int = 12, 
                      slow_period: int = 26, 
                      signal_period: int = 9) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate MACD and Signal line
        
        Args:
            data (pd.DataFrame): OHLCV price data
            fast_period (int): Fast EMA period
            slow_period (int): Slow EMA period
            signal_period (int): Signal line period
            
        Returns:
            Tuple[pd.Series, pd.Series]: MACD line and Signal line
        """
        if len(data) < max(fast_period, slow_period, signal_period):
            raise ValueError("Insufficient data for MACD calculation")
            
        exp1 = data['Close'].ewm(span=fast_period, adjust=False).mean()
        exp2 = data['Close'].ewm(span=slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        return macd, signal
    
    @staticmethod
    def calculate_support_resistance(data: pd.DataFrame, window: int = 20) -> Tuple[float, float]:
        """Calculate Support and Resistance levels"""
        rolling_min = data['Low'].rolling(window=window).min()
        rolling_max = data['High'].rolling(window=window).max()
        return rolling_min.iloc[-1], rolling_max.iloc[-1]
    
    @staticmethod
    def calculate_volume_profile(data: pd.DataFrame, bins: int = 50) -> pd.Series:
        """Calculate Volume Profile"""
        price_bins = pd.cut(data['Close'], bins=bins)
        return data.groupby(price_bins)['Volume'].sum()