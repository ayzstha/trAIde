import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

class PatternRecognition:
    @staticmethod
    def identify_trend(data: pd.DataFrame, window: int = 20) -> str:
        """
        Identify current trend direction using moving average
        
        Args:
            data (pd.DataFrame): Price data with OHLCV columns
            window (int): Moving average period
            
        Returns:
            str: "UPTREND" or "DOWNTREND"
        """
        ma = data['Close'].rolling(window=window).mean()
        current_price = data['Close'].iloc[-1]
        if current_price > ma.iloc[-1]:
            return "UPTREND"
        return "DOWNTREND"
    
    @staticmethod
    def detect_breakout(data: pd.DataFrame, window: int = 20) -> Optional[str]:
        """
        Detect price breakouts from recent high/low ranges
        
        Args:
            data (pd.DataFrame): Price data with OHLCV columns
            window (int): Lookback period for range
            
        Returns:
            Optional[str]: "BREAKOUT_UP", "BREAKOUT_DOWN", or None if no breakout
        """
        rolling_high = data['High'].rolling(window=window).max()
        rolling_low = data['Low'].rolling(window=window).min()
        
        if data['Close'].iloc[-1] > rolling_high.iloc[-2]:
            return "BREAKOUT_UP"
        elif data['Close'].iloc[-1] < rolling_low.iloc[-2]:
            return "BREAKOUT_DOWN"
        return None
    
    @staticmethod
    def detect_consolidation(data: pd.DataFrame, window: int = 20, threshold: float = 0.02) -> bool:
        """Detect price consolidation periods"""
        recent_data = data['Close'].tail(window)
        price_range = (recent_data.max() - recent_data.min()) / recent_data.mean()
        return price_range < threshold

    @staticmethod
    def detect_double_top(data: pd.DataFrame, window: int = 20, threshold: float = 0.02) -> Optional[bool]:
        """
        Detect double top pattern
        Args:
            data: OHLCV price data
            window: Lookback period
            threshold: Price difference threshold
        Returns:
            bool or None: True if double top detected
        """
        peaks = data['High'].rolling(window=5, center=True).apply(
            lambda x: (x[2] > x[0:2]).all() and (x[2] > x[3:]).all()
        )
        peak_prices = data.loc[peaks == 1, 'High']
        
        if len(peak_prices) >= 2:
            last_two_peaks = peak_prices.tail(2)
            price_diff = abs(last_two_peaks.iloc[1] - last_two_peaks.iloc[0])
            avg_price = last_two_peaks.mean()
            if price_diff / avg_price < threshold:
                return True
        return None

    @staticmethod 
    def detect_head_shoulders(data: pd.DataFrame, window: int = 20) -> Optional[str]:
        """
        Detect head and shoulders pattern
        Args:
            data: OHLCV price data
            window: Lookback period
        Returns:
            str or None: "HEAD_SHOULDERS_TOP" or "HEAD_SHOULDERS_BOTTOM"
        """
        peaks = data['High'].rolling(window=5, center=True).apply(
            lambda x: (x[2] > x[0:2]).all() and (x[2] > x[3:]).all()
        )
        troughs = data['Low'].rolling(window=5, center=True).apply(
            lambda x: (x[2] < x[0:2]).all() and (x[2] < x[3:]).all()
        )
        
        peak_prices = data.loc[peaks == 1, 'High'].tail(3)
        trough_prices = data.loc[troughs == 1, 'Low'].tail(2)
        
        if len(peak_prices) == 3 and len(trough_prices) == 2:
            if peak_prices.iloc[1] > peak_prices.iloc[0] and peak_prices.iloc[1] > peak_prices.iloc[2]:
                if abs(peak_prices.iloc[0] - peak_prices.iloc[2]) / peak_prices.mean() < 0.02:
                    return "HEAD_SHOULDERS_TOP"
        return None

    @staticmethod
    def detect_triangle(data: pd.DataFrame, window: int = 20) -> Optional[str]:
        """
        Detect triangle patterns
        Args:
            data: OHLCV price data
            window: Lookback period
        Returns:
            str or None: "ASCENDING_TRIANGLE", "DESCENDING_TRIANGLE", "SYMMETRIC_TRIANGLE"
        """
        highs = data['High'].tail(window)
        lows = data['Low'].tail(window)
        
        high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
        low_slope = np.polyfit(range(len(lows)), lows, 1)[0]
        
        if abs(high_slope) < 0.001 and low_slope > 0.001:
            return "ASCENDING_TRIANGLE"
        elif high_slope < -0.001 and abs(low_slope) < 0.001:
            return "DESCENDING_TRIANGLE"
        elif abs(high_slope + low_slope) < 0.001:
            return "SYMMETRIC_TRIANGLE"
        return None

    @staticmethod
    def find_support_resistance(data: pd.DataFrame, window: int = 20, 
                              threshold: float = 0.02) -> Tuple[float, float]:
        """
        Find support and resistance levels
        Args:
            data: OHLCV price data
            window: Lookback period
            threshold: Price cluster threshold
        Returns:
            Tuple[float, float]: Support and resistance prices
        """
        prices = pd.concat([data['High'], data['Low']])
        hist, bins = np.histogram(prices, bins=50)
        
        support = bins[np.argmax(hist[:len(hist)//2])]
        resistance = bins[len(hist)//2 + np.argmax(hist[len(hist)//2:])]
        
        return support, resistance

    @staticmethod
    def detect_ma_crossover(data: pd.DataFrame, fast_period: int = 20, 
                          slow_period: int = 50) -> Optional[str]:
        """
        Detect moving average crossovers
        Args:
            data: OHLCV price data
            fast_period: Fast MA period
            slow_period: Slow MA period
        Returns:
            str or None: "GOLDEN_CROSS" or "DEATH_CROSS"
        """
        fast_ma = data['Close'].rolling(window=fast_period).mean()
        slow_ma = data['Close'].rolling(window=slow_period).mean()
        
        if fast_ma.iloc[-2] < slow_ma.iloc[-2] and fast_ma.iloc[-1] > slow_ma.iloc[-1]:
            return "GOLDEN_CROSS"
        elif fast_ma.iloc[-2] > slow_ma.iloc[-2] and fast_ma.iloc[-1] < slow_ma.iloc[-1]:
            return "DEATH_CROSS"
        return None